"""
Kentsel stres etkenleri — Türkiye verisi (Faz 4 · Rapor 1)
=========================================================
1. Eurostat EU-SILC (anahtarsız API): Türkiye ve AB-27 için konut sıkışıklığı, konut maliyet yükü, gürültü,
   kirlilik, suç-şiddet, karanlık konut, yaşam memnuniyeti, başkalarına güven.
2. TÜİK SDMX (databrowser2): il düzeyinde trafik kazası ölü-yaralı (2015–2025) ve motorlu taşıt sayısı (aylık).
3. İkincil il tabloları (03_VERI/ham/stres/*.csv; eski TÜİK sitesinin Wayback arşivinden, bkz. kaynaklar.md):
   intihar 2000–2018, Yaşam Memnuniyeti 2013 (il), İllerde Yaşam Endeksi 2015.

Çıktı : 03_VERI/ham/stres/eurostat/*.json, 03_VERI/ham/stres/sdmx/*.json (ham yanıtlar, önbellek)
        05_ANALIZ/sonuclar/stres_turkiye_ab.csv   Türkiye–AB karşılaştırması (SILC)
        05_ANALIZ/sonuclar/stres_il_dis_veri.csv  81 il: intihar, mutluluk, İLYE algı göstergeleri, trafik, otomobil
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/stres_veri.py
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 200)
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "stres"
SON = KOK / "05_ANALIZ" / "sonuclar"
(HAM / "eurostat").mkdir(parents=True, exist_ok=True)
(HAM / "sdmx").mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def al(url, govde=None, deneme=4):
    for i in range(deneme):
        try:
            r = urllib.request.Request(url, data=None if govde is None else json.dumps(govde).encode(),
                                       headers=UA | ({"Content-Type": "application/json"} if govde is not None else {}),
                                       method="GET" if govde is None else "POST")
            with urllib.request.urlopen(r, timeout=600) as f:
                return json.load(f)
        except Exception as e:  # ağ hatasında bekleyip yeniden dene
            print("  yeniden deneniyor:", e)
            time.sleep(8 * (i + 1))
    raise RuntimeError(url)


def onbellek(yol, f):
    if not yol.exists():
        json.dump(f(), open(yol, "w", encoding="utf-8"), ensure_ascii=False)
    return json.load(open(yol, encoding="utf-8"))


def jsonstat(d):
    """JSON-stat 2.0 (Eurostat ve TÜİK SDMX) -> uzun tablo (kodlar)"""
    ids, boy = d["id"], d["size"]
    kat = {}
    for k in ids:
        ix = d["dimension"][k]["category"]["index"]
        kat[k] = sorted(ix, key=ix.get) if isinstance(ix, dict) else ix
    satir = []
    for flat, deger in d["value"].items():
        i, kalan = int(flat), []
        for s in reversed(boy):
            kalan.append(i % s)
            i //= s
        satir.append({k: kat[k][j] for k, j in zip(ids, reversed(kalan))} | {"deger": float(deger)})
    return pd.DataFrame(satir)


# --- 1. Eurostat EU-SILC: Türkiye ve AB-27 -------------------------------------------------------------------------
ES = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{}?format=JSON&lang=EN&geo=TR&geo=EU27_2020"
SILC = [  # (veri seti, Türkçe ad, süzgeç)
    ("ilc_lvho05a", "Aşırı kalabalık konutta yaşayan nüfus (%)", {"age": "TOTAL", "sex": "T", "rskpovth": "TOTAL"}),
    ("ilc_lvho05a", "Aşırı kalabalık konutta yaşayan 18 yaş altı (%)", {"age": "Y_LT18", "sex": "T", "rskpovth": "TOTAL"}),
    ("ilc_lvho07a", "Konut maliyeti hane gelirinin %40'ını aşan nüfus (%)", {"age": "TOTAL", "sex": "T", "rskpovth": "TOTAL"}),
    ("ilc_lvho07a", "Konut maliyet yükü, yoksulluk riski altındakiler (%)", {"age": "TOTAL", "sex": "T", "rskpovth": "B_60"}),
    ("ilc_mddw01", "Komşudan ya da sokaktan gürültü sorunu (%)", {"hhcomp": "TOTAL", "rskpovth": "TOTAL"}),
    ("ilc_mddw02", "Kirlilik, kir ya da başka çevre sorunu (%)", {"hhcomp": "TOTAL", "rskpovth": "TOTAL"}),
    ("ilc_mddw03", "Çevrede suç, şiddet ya da vandalizm (%)", {"hhcomp": "TOTAL", "rskpovth": "TOTAL"}),
    ("ilc_mdho04", "Konutunu fazla karanlık bulan nüfus (%)", {"hhcomp": "TOTAL", "rskpovth": "TOTAL", "sex": "T", "age": "TOTAL"}),
    ("ilc_pw01", "Genel yaşam memnuniyeti (0–10)", {"isced11": "TOTAL", "sex": "T", "age": "Y_GE16"}),
    ("ilc_pw03", "Başkalarına güven (0–10)", {"isced11": "TOTAL", "sex": "T", "age": "Y_GE16"}),
]
ab = []
for ds, ad, sz in SILC:
    d = jsonstat(onbellek(HAM / "eurostat" / f"{ds}.json", lambda: al(ES.format(ds))))
    for k, v in sz.items():
        if k in d:
            d = d[d[k] == v]
    p = d.pivot_table(index="time", columns="geo", values="deger")
    p.index = p.index.astype(int)
    tr = p["TR"].dropna()
    son = tr.index.max()
    ilk = tr.index.min()
    ab.append({"gosterge": ad, "veri_seti": ds, "tr_ilk_yil": ilk, "tr_ilk": tr[ilk], "tr_son_yil": son, "tr_son": tr[son],
               "ab27_ayni_yil": p.loc[son, "EU27_2020"] if "EU27_2020" in p and son in p.index else np.nan,
               "tr_2019": tr.get(2019, np.nan), "isaret": "[D] Eurostat EU-SILC"})
AB = pd.DataFrame(ab)
AB.to_csv(SON / "stres_turkiye_ab.csv", index=False, encoding="utf-8")
print("Türkiye – AB-27 (EU-SILC):\n", AB.drop(columns=["veri_seti", "isaret"]).round(2).to_string(index=False))

# --- 2. TÜİK SDMX: il düzeyi trafik kazası ve otomobil ----------------------------------------------------------------
SD = "https://databrowser2.tuik.gov.tr/api/core/nodes/1/datasets/TR,{},1.0/data"
ZAMAN = lambda a, b: [{"id": "TIME_PERIOD", "filterValues": [], "type": "TimeRange", "period": 0,
                       "from": f"{a}-01-01T00:00:00", "to": f"{b}-12-31T00:00:00"}]
tk = jsonstat(onbellek(HAM / "sdmx" / "DF_TRAFIK_KAZA_OLU_YARALI_V2.json",
                       lambda: al(SD.format("DF_TRAFIK_KAZA_OLU_YARALI_V2"), ZAMAN(2015, 2026))))
tk["TIME_PERIOD"] = tk.TIME_PERIOD.astype(int)
# en son tam yıl (2025'te iki il eksik: Kahramanmaraş, Şanlıurfa)
_kap = tk[tk.TRAFIK_KAZA_GOSTERGE == "10"].groupby("TIME_PERIOD").REF_AREA.nunique()
TKY = _kap[_kap == _kap.max()].index.max()
t_ = tk[(tk.TIME_PERIOD == TKY) & (tk.KAZA_OLUM_DURUM.isin(["_T", "_Z"]))]
trafik = t_.pivot_table(index="REF_AREA", columns="TRAFIK_KAZA_GOSTERGE", values="deger", aggfunc="sum")
trafik = trafik.rename(columns={"10": "trafik_olu", "11": "trafik_yarali", "3": "tasit_sayisi", "9": "olumlu_yaralanmali_kaza"})
mt = jsonstat(onbellek(HAM / "sdmx" / "DF_MOTORLU_KARA_TASIT_ILLER_V3.json",
                       lambda: al(SD.format("DF_MOTORLU_KARA_TASIT_ILLER_V3"), ZAMAN(2024, 2026))))
mt = mt[(mt.ARAC_TUR == "1") & (mt.UNIT_MEASURE == "PN")]
MTY = mt.TIME_PERIOD.max()
oto = mt[mt.TIME_PERIOD == MTY].set_index("REF_AREA").deger.rename("otomobil")
print(f"\nTrafik kazası yılı: {TKY} · otomobil dönemi: {MTY}")

# --- 3. il tablosu ------------------------------------------------------------------------------------------------
il = pd.read_csv(KOK / "03_VERI" / "islenmis" / "il_paneli_2025.csv")[["il", "ibbs3_kod", "nufus_2025", "ibbs1"]]
it = pd.read_csv(HAM / "il_intihar_2000_2018_birlesik.csv")
# 2012'de kapsam genişledi (kurumsal yerler ve ölüm nedeni verisi eklendi) -> 2012 sonrası yıllar kullanılır.
# 2012–2016 olay yeri, 2017–2018 ikamet ili. Küçük sayılar nedeniyle çok yıllı toplam: hız = Σ intihar / Σ nüfus.
it["nufus_tah"] = it.intihar_sayisi / it.kaba_intihar_hizi * 1e5
for a, b in [(2012, 2018), (2014, 2018)]:
    s = it[it.yil.between(a, b)].groupby("ibbs3_kod")[["intihar_sayisi", "erkek", "kadin", "nufus_tah"]].sum()
    il = il.merge(s.assign(**{f"intihar_hiz_{a}_{b}": s.intihar_sayisi / s.nufus_tah * 1e5,
                              f"intihar_erkek_hiz_{a}_{b}": s.erkek / s.nufus_tah * 1e5})
                  [[f"intihar_hiz_{a}_{b}", f"intihar_erkek_hiz_{a}_{b}"]].assign(**{f"intihar_n_{a}_{b}": s.intihar_sayisi,
                                                                                    f"kisi_yil_{a}_{b}": s.nufus_tah}),
                  left_on="ibbs3_kod", right_index=True, how="left")
mu = pd.read_csv(HAM / "il_mutluluk_2013.csv")[["ibbs3_kod", "mutlu_pct", "mutsuz_pct"]].rename(
    columns={"mutlu_pct": "mutlu_2013", "mutsuz_pct": "mutsuz_2013"})
ilye = pd.read_csv(HAM / "il_ilye_2015_gostergeler.csv")
IK = {"sokak_gurultusu_problemi_pct": "gurultu_sorunu_2015", "gece_yalniz_yururken_guvende_pct": "gece_guvende_2015",
      "pm10_ug_m3": "pm10_2015", "oda_sayisi_kisi_basi": "oda_kisi_basi_2015", "konut_kalite_problemi_pct": "konut_kalite_sorunu_2015",
      "sosyal_iliski_memnuniyeti_pct": "sosyal_iliski_memnun_2015", "sosyal_hayat_memnuniyeti_pct": "sosyal_hayat_memnun_2015",
      "cinayet_milyonda": "cinayet_milyonda_2015", "dogusta_yasam_suresi_yil": "yasam_suresi_2015",
      "belediye_toplu_tasima_memnuniyeti_pct": "toplu_tasima_memnun_2015"}
il = il.merge(mu, on="ibbs3_kod", how="left").merge(ilye[["ibbs3_kod"] + list(IK)].rename(columns=IK), on="ibbs3_kod", how="left")
il = il.merge(trafik[["trafik_olu", "trafik_yarali"]], left_on="ibbs3_kod", right_index=True, how="left")
il = il.merge(oto, left_on="ibbs3_kod", right_index=True, how="left")
il["trafik_olu_yarali_bin"] = (il.trafik_olu + il.trafik_yarali) / il.nufus_2025 * 1000
il["otomobil_bin"] = il.otomobil / il.nufus_2025 * 1000
fg = pd.read_csv(SON / "konut_il_fiyat_gelir_2024.csv")
fk = [c for c in fg.columns if "fiyat_gelir" in c]
if fk:
    il = il.merge(fg[["ibbs3_kod", fk[0]]].rename(columns={fk[0]: "fiyat_gelir_2024"}), on="ibbs3_kod", how="left") \
        if "ibbs3_kod" in fg else il.merge(fg[["il", fk[0]]].rename(columns={fk[0]: "fiyat_gelir_2024"}), on="il", how="left")
il["trafik_yili"], il["otomobil_donemi"] = TKY, MTY
il.to_csv(SON / "stres_il_dis_veri.csv", index=False, encoding="utf-8")
print(f"\nil tablosu: {il.shape} · eksik:", il.isna().sum()[il.isna().sum() > 0].to_dict())
w = il.nufus_2025
print("Nüfus ağırlıklı il ortalamaları:", {k: round(np.average(il[k].dropna(), weights=w[il[k].notna()]), 2) for k in
      ["intihar_hiz_2014_2018", "mutlu_2013", "gurultu_sorunu_2015", "gece_guvende_2015", "trafik_olu_yarali_bin", "otomobil_bin"]})
print(il[["il", "intihar_hiz_2014_2018", "mutlu_2013", "gurultu_sorunu_2015", "gece_guvende_2015"]]
      .sort_values("intihar_hiz_2014_2018").iloc[[0, 1, 2, -3, -2, -1]].round(2).to_string(index=False))
