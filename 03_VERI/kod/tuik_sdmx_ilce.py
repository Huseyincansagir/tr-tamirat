"""
TÜİK Dağıtım Yönetim Sistemi (databrowser2.tuik.gov.tr) SDMX arka ucundan ilçe verisi
======================================================================================
- İlçe kod listesi (CL_IBBS 1.2; 4 haneli ilçe kodları, üst kodu İBBS-3 = il)
- İl ve ilçeye göre doğumlar (DF_DOGUM_IL_ILCE_C), 2014-2025
- İl ve ilçelere göre il/ilçe merkezi, belde/köy nüfusu (DF_ADNKS_T22), 2014-2025

Çıktı: 03_VERI/ham/tuik/sdmx/*.json (ham yanıtlar) ve 03_VERI/islenmis/ilce_dogum_nufus.csv
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "tuik" / "sdmx"
HAM.mkdir(parents=True, exist_ok=True)
B = "https://databrowser2.tuik.gov.tr/api/core/nodes/1/datasets/"
H = {"Accept": "application/json", "User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}


def istek(url, govde=None):
    for deneme in range(4):
        try:
            r = urllib.request.Request(url, data=None if govde is None else json.dumps(govde).encode(),
                                       headers=H, method="GET" if govde is None else "POST")
            return json.load(urllib.request.urlopen(r, timeout=900))
        except Exception as e:  # ağ hatasında bekleyip yeniden dene
            print("  yeniden deneniyor:", e)
            time.sleep(10 * (deneme + 1))
    raise RuntimeError(url)


def jsonstat_df(d):
    """JSON-stat 2.0 -> uzun tablo"""
    ids, boy = d["id"], d["size"]
    kat = {k: d["dimension"][k]["category"]["index"] for k in ids}
    satir = []
    for flat, deger in d["value"].items():
        i, kalan = int(flat), []
        for s in reversed(boy):
            kalan.append(i % s)
            i //= s
        kalan = list(reversed(kalan))
        satir.append({k: kat[k][j] for k, j in zip(ids, kalan)} | {"deger": float(deger)})
    return pd.DataFrame(satir)


C = lambda i, v: {"id": i, "filterValues": v, "type": "CodeValues", "period": 0}
T = lambda a, b: {"id": "TIME_PERIOD", "filterValues": [], "type": "TimeRange", "period": 0,
                  "from": f"{a}-01-01T00:00:00", "to": f"{b}-12-31T00:00:00"}

# 1) ilçe kodları
kod_dosya = HAM / "CL_IBBS_ilce_kodlari.json"
if not kod_dosya.exists():
    v = istek(B + "TR,DF_DOGUM_IL_ILCE_C,1.0/column/REF_AREA/full/values")
    json.dump(v, open(kod_dosya, "w", encoding="utf-8"), ensure_ascii=False)
vals = json.load(open(kod_dosya, encoding="utf-8"))["criteria"][0]["values"]
ad = {x["id"]: x["name"] for x in vals}
ilce = pd.DataFrame([{"ilce_kod": x["id"], "ilce_ad_tuik": x["name"], "ibbs3_kod": x["parentId"], "il": ad[x["parentId"]]}
                     for x in vals if x["id"].isdigit() and x.get("parentId", "").startswith("TR") and len(x["parentId"]) == 5])
print("ilçe sayısı:", len(ilce))
kodlar = ilce.ilce_kod.tolist()

# 2) doğumlar (parçalar halinde)
parcalar = []
for i in range(0, len(kodlar), 250):
    d = istek(B + "TR,DF_DOGUM_IL_ILCE_C,1.0/data", [C("REF_AREA", kodlar[i:i + 250]), T(2014, 2025)])
    json.dump(d, open(HAM / f"DF_DOGUM_IL_ILCE_C_{i:04d}.json", "w", encoding="utf-8"), ensure_ascii=False)
    parcalar.append(jsonstat_df(d))
    time.sleep(2)
dg = pd.concat(parcalar)
print("doğum boyutları:", dg.columns.tolist(), dg.CINSIYET_BEBEK.unique() if "CINSIYET_BEBEK" in dg else "")
dg = dg[dg.CINSIYET_BEBEK.isin(["_T", "T", "TOPLAM"])] if "CINSIYET_BEBEK" in dg else dg
dog = dg.pivot_table(index="REF_AREA", columns="TIME_PERIOD", values="deger", aggfunc="sum")
dog.columns = [f"dogum_{c}" for c in dog.columns]

# 3) nüfus (T22: ikamet yeri = ilçe)
parcalar = []
for i in range(0, len(kodlar), 250):
    d = istek(B + "TR,DF_ADNKS_T22,1.1/data",
              [C("REF_AREA", ["TR"]), C("FREQ", ["A"]), C("INDICATOR", ["NG_ADNKS"]), C("IKAMET_YERI", kodlar[i:i + 250]), T(2014, 2025)])
    json.dump(d, open(HAM / f"DF_ADNKS_T22_{i:04d}.json", "w", encoding="utf-8"), ensure_ascii=False)
    parcalar.append(jsonstat_df(d))
    time.sleep(2)
nf = pd.concat(parcalar)
print("nüfus yerleşim türleri:", nf.YERLESIM_YERI_TUR.unique())
nf_top = nf[nf.YERLESIM_YERI_TUR == "_T"].pivot_table(index="IKAMET_YERI", columns="TIME_PERIOD", values="deger", aggfunc="sum")
nf_top.columns = [f"nufus_{c}" for c in nf_top.columns]
nf_mrk = nf[nf.YERLESIM_YERI_TUR == "1"].pivot_table(index="IKAMET_YERI", columns="TIME_PERIOD", values="deger", aggfunc="sum")
nf_mrk.columns = [f"merkez_nufus_{c}" for c in nf_mrk.columns]

out = ilce.set_index("ilce_kod").join(dog).join(nf_top).join(nf_mrk).reset_index()
out.to_csv(KOK / "03_VERI" / "islenmis" / "ilce_dogum_nufus.csv", index=False, encoding="utf-8")
print(out.shape)
print(out[[c for c in out.columns if c.endswith("2025")]].sum().to_dict())
print("eksik doğum 2025:", out.dogum_2025.isna().sum(), "| eksik nüfus 2025:", out.nufus_2025.isna().sum())
