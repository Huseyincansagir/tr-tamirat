"""
H2 — konut maliyeti, evlilik ve doğurganlık: veri derleme
=========================================================
Kaynaklar (hepsi herkese açık, giriş/anahtar gerektirmeyen uç noktalar):
  TCMB EVDS3 (evds3.tcmb.gov.tr/igmevdsms-dis) — EVDS'in web arayüzünün kendi arka ucu; anahtar istemiyor.
      bie_kfe        Konut Fiyat Endeksi (2023=100), aylık, Türkiye + 19 bölge (İBBS-2 ve birleşik İBBS-1)
      bie_ykke       Yeni Kiracı Kira Endeksi (2023=100), aylık, aynı bölgeler, 2018→
      bie_birimfiyat Değerlemesi yapılan konutların birim fiyatları (TL/m²), çeyreklik, Türkiye + 81 il, 2010→
      bie_bk         Değerlemesi yapılan konutların birim kiraları (TL/m²/ay), çeyreklik, Türkiye + 81 il, 2018→
      bie_tukfiy4    TÜFE (2003=100) genel endeks TP.FG.J0, aylık (arşiv seri; doğrulama için)
  TÜİK Dağıtım Yönetim Sistemi SDMX (databrowser2.tuik.gov.tr/api/core/nodes/1/datasets)
      DF_KABA_EVLENME_HIZI, DF_EVLENME_ORT_ILK_EVL_YAS, DF_EVLENME_ILK_YASGR, DF_DOGUM_IL_TDH_C,
      DF_DOGUM_ORTYAS_ILKDOG_C, DF_UH_BH_KISI_BASI, DF_ADNKS_T16, DF_ULUSAL_EGITIM_ISTATISTIK_BED_NUFUS,
      DF_TUFE_SDMX_2003
Çıktı:
  03_VERI/ham/konut/*.json                 ham yanıtlar (yeniden indirmemek için önbellek; --yenile ile tazelenir)
  03_VERI/islenmis/konut_paneli.csv        il × yıl paneli (2005–2025)
  03_VERI/islenmis/konut_paneli_kfe_bolge.csv   KFE bölgesi (19) × yıl paneli
Kullanım: python 05_ANALIZ/kod/konut_h2_veri.py [--yenile]
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "konut"
HAM.mkdir(parents=True, exist_ok=True)
ISLENMIS = KOK / "03_VERI" / "islenmis"
YENILE = "--yenile" in sys.argv
H = {"Accept": "application/json", "User-Agent": "Mozilla/5.0", "Content-Type": "application/json",
     "Accept-Language": "tr"}


def istek(url, govde=None):
    for deneme in range(4):
        try:
            r = urllib.request.Request(url, data=None if govde is None else json.dumps(govde).encode(),
                                       headers=H, method="GET" if govde is None else "POST")
            return json.load(urllib.request.urlopen(r, timeout=600))
        except Exception as e:  # ağ hatasında bekleyip yeniden dene
            print("  yeniden deneniyor:", e)
            time.sleep(10 * (deneme + 1))
    raise RuntimeError(url)


def onbellek(ad, fn):
    p = HAM / ad
    if p.exists() and not YENILE:
        return json.load(open(p, encoding="utf-8"))
    v = fn()
    json.dump(v, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    time.sleep(1.5)
    return v


# --- 1. TCMB EVDS3 ---------------------------------------------------------------------
EVDS = "https://evds3.tcmb.gov.tr/igmevdsms-dis"


def evds_liste(grup):
    return istek(f"{EVDS}/serieList/fe/type=json&code={grup}")


def evds_veri(kodlar, frekans):
    """frekans: 5 = aylık, 6 = çeyreklik (EVDS kodlaması). Düzey (formül 0), ortalama toplulaştırma."""
    parca = []
    for i in range(0, len(kodlar), 30):
        k = kodlar[i:i + 30]
        g = {"type": "json", "series": "-".join(k), "aggregationTypes": "-".join(["avg"] * len(k)),
             "formulas": "-".join(["0"] * len(k)), "startDate": "01-01-2009", "endDate": "31-12-2026",
             "frequency": str(frekans), "decimalSeperator": ".", "decimal": "6", "dateFormat": "0", "lang": "tr",
             "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": True}
        parca.append(istek(f"{EVDS}/fe", g))
        time.sleep(1.5)
    return parca


def evds_df(parca):
    df = None
    for o in parca:
        d = pd.DataFrame(o["items"]).drop(columns="UNIXTIME").set_index("Tarih")
        df = d if df is None else df.join(d)
    return df.apply(pd.to_numeric, errors="coerce")


ev = {}
for grup, frekans in [("bie_kfe", 5), ("bie_ykke", 5), ("bie_birimfiyat", 6), ("bie_bk", 6)]:
    liste = onbellek(f"evds_{grup}_seri_listesi.json", lambda: evds_liste(grup))
    kodlar = [x["SERIE_CODE"] for x in liste]
    veri = onbellek(f"evds_{grup}.json", lambda: evds_veri(kodlar, frekans))
    ev[grup] = (liste, evds_df(veri))
    print(f"EVDS {grup}: {len(kodlar)} seri, {ev[grup][1].shape[0]} dönem")
tufe_evds = evds_df(onbellek("evds_TP_FG_J0.json", lambda: evds_veri(["TP.FG.J0"], 5)))

# --- 2. TÜİK SDMX ----------------------------------------------------------------------
SDMX = "https://databrowser2.tuik.gov.tr/api/core/nodes/1/datasets/"


def sdmx(df_ad, surum="1.0", filtre=(), bas=2005, son=2026):
    g = [{"id": k, "filterValues": v, "type": "CodeValues", "period": 0} for k, v in filtre]
    g.append({"id": "TIME_PERIOD", "filterValues": [], "type": "TimeRange", "period": 0,
              "from": f"{bas}-01-01T00:00:00", "to": f"{son}-12-31T00:00:00"})
    return onbellek(f"sdmx_{df_ad}.json", lambda: istek(f"{SDMX}TR,{df_ad},{surum}/data", g))


def jsonstat_df(d):
    """JSON-stat 2.0 -> uzun tablo (kodlar)"""
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
        kalan = list(reversed(kalan))
        satir.append({k: kat[k][j] for k, j in zip(ids, kalan)} | {"deger": float(deger)})
    return pd.DataFrame(satir)


def il_yil(df, alan="REF_AREA", ad="deger"):
    out = df.rename(columns={alan: "ibbs3_kod", "TIME_PERIOD": "yil"})[["ibbs3_kod", "yil", "deger"]]
    out["yil"] = out.yil.astype(int)
    return out.rename(columns={"deger": ad})


keh = il_yil(jsonstat_df(sdmx("DF_KABA_EVLENME_HIZI")), ad="kaba_evlenme")
iey = jsonstat_df(sdmx("DF_EVLENME_ORT_ILK_EVL_YAS"))
iey_k = il_yil(iey[iey.SEX == "2"], ad="ilk_evlenme_yasi_k")
iey_e = il_yil(iey[iey.SEX == "1"], ad="ilk_evlenme_yasi_e")
tdh = il_yil(jsonstat_df(sdmx("DF_DOGUM_IL_TDH_C")), ad="tdh")
idy = il_yil(jsonstat_df(sdmx("DF_DOGUM_ORTYAS_ILKDOG_C")), ad="ilk_dogum_yasi")
gs = jsonstat_df(sdmx("DF_UH_BH_KISI_BASI"))
gs = gs[(gs.UNIT_MEASURE == "TRY") & (gs.DUZEY_SEVIYE.isin(["0", "3"]))]
gsyh = il_yil(gs, ad="gsyh_kb_tl")

# ilk evlenmeler (kadın, yaş grubu) ve kadın nüfusu (yaş grubu) -> kadın toplam ilk evlenme hızı
ie = jsonstat_df(sdmx("DF_EVLENME_ILK_YASGR"))
ie = ie[ie.SEX == "2"].rename(columns={"REF_AREA": "ibbs3_kod", "TIME_PERIOD": "yil", "YAS_GRUP": "yas"})
ie["yil"] = ie.yil.astype(int)
nf = jsonstat_df(sdmx("DF_ADNKS_T16", filtre=[("SEX", ["2"])], bas=2007))
nf = nf.rename(columns={"IKAMET_YERI": "ibbs3_kod", "TIME_PERIOD": "yil", "YAS_GRUBU": "yas"})
nf["yil"] = nf.yil.astype(int)
nf["ibbs3_kod"] = nf.ibbs3_kod.replace({"_T": "TR"})
# tutarlılık denetimi: yaş grubu dağılımından türetilen ortalama ilk evlenme yaşı, TÜİK'in yayımladığı ortalamayla
# uyuşmalı. 2005–2023'te fark ±0,2 yıl; 2024–2025'te KADIN satırlarında +2,1…+4,3 yıl (yaş dağılımı erkeklerinkine
# benziyor) -> bu yıllar için kadın yaş dağılımı kullanılmaz (TİEH ve yaşa özel hızlar boş bırakılır).
ORTA = {"Y16T19": 17.5, "Y20T24": 22.5, "Y25T29": 27.5, "Y30T34": 32.5, "Y35T39": 37.5, "Y40T44": 42.5,
        "Y45T49": 47.5, "Y50T54": 52.5, "Y55T59": 57.5, "Y_GE60": 65}
_t = ie[ie.yas.isin(ORTA)].assign(o=lambda x: x.yas.map(ORTA))
tureyen = _t.groupby(["ibbs3_kod", "yil"]).apply(lambda x: (x.o * x.deger).sum() / x.deger.sum(), include_groups=False)
uyum = (tureyen.rename("tureyen").reset_index().merge(iey_k, on=["ibbs3_kod", "yil"]))
uyum["fark"] = uyum.tureyen - uyum.ilk_evlenme_yasi_k
print("Kadın ilk evlenme yaş dağılımı tutarlılığı (türetilen − yayımlanan ortalama, yıl):")
print(uyum.groupby("yil").fark.agg(["min", "max"]).round(2).T.to_string())
bozuk = set(map(tuple, uyum.loc[uyum.fark.abs() > 0.5, ["ibbs3_kod", "yil"]].values))
print(f"  tutarsız il-yıl: {len(bozuk)} (yıllar: {sorted({y for _, y in bozuk})}) -> TİEH bu gözlemlerde boş")
ie_top = ie[ie.yas == "_T"][["ibbs3_kod", "yil", "deger"]].rename(columns={"deger": "ilk_evlenme_k_sayi"})
ie = ie[[(k, y) not in bozuk for k, y in zip(ie.ibbs3_kod, ie.yil)]]
YAS_ESLE = {"Y16T19": "Y15T19", "Y20T24": "Y20T24", "Y25T29": "Y25T29", "Y30T34": "Y30T34", "Y35T39": "Y35T39",
            "Y40T44": "Y40T44", "Y45T49": "Y45T49"}
ie5 = ie[ie.yas.isin(YAS_ESLE)].assign(yas=lambda x: x.yas.map(YAS_ESLE))
oran = ie5.merge(nf[["ibbs3_kod", "yil", "yas", "deger"]].rename(columns={"deger": "kadin"}),
                 on=["ibbs3_kod", "yil", "yas"], how="inner")
oran["asr"] = oran.deger / oran.kadin
tieh = (oran.groupby(["ibbs3_kod", "yil"]).asr.sum() * 5).rename("tieh_k").reset_index()
# yaşa özel kadın ilk evlenme hızları (‰): erteleme testi için
yoh = oran[oran.yas.isin(["Y15T19", "Y20T24", "Y25T29", "Y30T34"])].pivot_table(
    index=["ibbs3_kod", "yil"], columns="yas", values="asr") * 1000
yoh.columns = ["iehk_" + c[1:3] + "_" + c[4:6] for c in yoh.columns]
tieh = tieh.merge(yoh.reset_index(), on=["ibbs3_kod", "yil"], how="left")
nfw = nf.pivot_table(index=["ibbs3_kod", "yil"], columns="yas", values="deger").reset_index()
nfw["kadin_20_34"] = nfw[["Y20T24", "Y25T29", "Y30T34"]].sum(axis=1)
nfw["kadin_15_49"] = nfw[["Y15T19", "Y20T24", "Y25T29", "Y30T34", "Y35T39", "Y40T44", "Y45T49"]].sum(axis=1)
nfw["kadin_top"] = nfw["_T"]
nfw = nfw[["ibbs3_kod", "yil", "kadin_20_34", "kadin_15_49", "kadin_top"]]

# kadın eğitimi (15+): yükseköğretim payı (eğitim durumu bilinenler içinde)
eg = jsonstat_df(sdmx("DF_ULUSAL_EGITIM_ISTATISTIK_BED_NUFUS", filtre=[("CINSIYET", ["2"]), ("YAS_GRUP", ["Y_GE15"])]))
eg = eg.pivot_table(index=["REF_AREA", "TIME_PERIOD"], columns="EGITIM_SEVIYESI", values="deger").reset_index()
eg["kadin_yuksek_pct"] = 100 * eg[["516", "52", "53"]].sum(axis=1) / (eg["_T"] - eg["_U"].fillna(0))
egit = eg.rename(columns={"REF_AREA": "ibbs3_kod", "TIME_PERIOD": "yil"})[["ibbs3_kod", "yil", "kadin_yuksek_pct"]]
egit["yil"] = egit.yil.astype(int)

# TÜFE (2003=100), yıllık ortalama
tf = jsonstat_df(sdmx("DF_TUFE_SDMX_2003", filtre=[("DEGISIM", ["1"])]))
tf["yil"] = tf.TIME_PERIOD.str[:4].astype(int)
tufe = tf.groupby("yil").deger.agg(["mean", "size"])
tufe = tufe[tufe["size"] == 12]["mean"].rename("tufe_2003")
# doğrulama: TÜİK SDMX ile TCMB EVDS'teki aynı seri
te = tufe_evds.TP_FG_J0.dropna()
te.index = te.index.str[:4].astype(int)
te = te.groupby(level=0).agg(["mean", "size"])
fark = (te[te["size"] == 12]["mean"] - tufe).abs().max()
print(f"TÜFE (2003=100) yıllık ort.: TÜİK SDMX ile EVDS arasındaki en büyük fark {fark:.4f}")

# --- 3. Konut göstergelerini il × yıla indir -----------------------------------------------
il_ad = pd.read_csv(ISLENMIS / "il_paneli_2025.csv")[["il", "ibbs3_kod"]]
ad2kod = dict(zip(il_ad.il, il_ad.ibbs3_kod)) | {"Türkiye": "TR"}


def ceyrek_yillik(grup, ek, ad):
    liste, df = ev[grup]
    sutun = {x["SERIE_CODE"].replace(".", "_"): ad2kod[x["SERIE_NAME"].replace(ek, "").strip()] for x in liste}
    df = df.rename(columns=sutun)
    df["yil"] = df.index.str[:4].astype(int)
    uzun = df.melt(id_vars="yil", var_name="ibbs3_kod", value_name=ad).dropna()
    g = uzun.groupby(["ibbs3_kod", "yil"])[ad].agg(["mean", "size"]).reset_index()
    return g.rename(columns={"mean": ad, "size": f"{ad}_ceyrek"})


bf = ceyrek_yillik("bie_birimfiyat", " Konut Birim Fiyatları", "birim_fiyat")
bk = ceyrek_yillik("bie_bk", " Konut Birim Kiraları", "birim_kira")

# --- 4. il × yıl paneli -------------------------------------------------------------------
iskelet = pd.MultiIndex.from_product([sorted(set(il_ad.ibbs3_kod) | {"TR"}), range(2005, 2026)],
                                     names=["ibbs3_kod", "yil"]).to_frame(index=False)
p = iskelet
for t in [keh, iey_k, iey_e, tdh, idy, gsyh, tieh, ie_top, nfw, egit, bf, bk]:
    p = p.merge(t, on=["ibbs3_kod", "yil"], how="left")
p = p.merge(tufe, left_on="yil", right_index=True, how="left")
p = il_ad.merge(p, on="ibbs3_kod", how="right")
p["il"] = p.il.fillna("Türkiye")
p["ibbs2"] = np.where(p.ibbs3_kod == "TR", "TR", p.ibbs3_kod.str[:4])
p["ibbs1"] = np.where(p.ibbs3_kod == "TR", "TR", p.ibbs3_kod.str[:3])
KFE_TEK = {"TR10", "TR21", "TR22", "TR31", "TR32", "TR33", "TR41", "TR42", "TR51", "TR52", "TR61", "TR62", "TR63"}
p["kfe_bolge"] = np.where(p.ibbs2.isin(KFE_TEK) | (p.ibbs2 == "TR"), p.ibbs2, p.ibbs1)

# türetilmiş konut erişilebilirlik ölçüleri
p["fiyat_gelir"] = p.birim_fiyat * 100 / p.gsyh_kb_tl          # 100 m² konut = kişi başı GSYH'nin kaç yılı
p["kira_gelir_pct"] = 100 * p.birim_kira * 12 * 100 / p.gsyh_kb_tl  # 100 m² yıllık kira / kişi başı GSYH (%)
p["reel_birim_fiyat"] = p.birim_fiyat / p.tufe_2003 * 100        # 2003 TL'si ile TL/m²
p = p.sort_values(["ibbs3_kod", "yil"]).reset_index(drop=True)
p.to_csv(ISLENMIS / "konut_paneli.csv", index=False, encoding="utf-8")
print(f"il × yıl paneli: {p.shape}, birim fiyatı olan il-yıl: {p.birim_fiyat.notna().sum()}, "
      f"fiyat/gelir hesaplanabilen: {p.fiyat_gelir.notna().sum()}")

# --- 5. KFE bölge × yıl paneli ----------------------------------------------------------------
liste, kfe = ev["bie_kfe"]
kfe.columns = [c.replace("TP_KFE_", "") for c in kfe.columns]
_, ykke = ev["bie_ykke"]
ykke.columns = [c.replace("TP_YKKE_", "") for c in ykke.columns]


def aylik_yillik(df, ad):
    d = df.copy()
    d["yil"] = d.index.str[:4].astype(int)
    u = d.melt(id_vars="yil", var_name="kfe_bolge", value_name=ad).dropna()
    g = u.groupby(["kfe_bolge", "yil"])[ad].agg(["mean", "size"]).reset_index()
    return g[g["size"] == 12].drop(columns="size").rename(columns={"mean": ad})


kb = aylik_yillik(kfe, "kfe").merge(aylik_yillik(ykke, "ykke"), on=["kfe_bolge", "yil"], how="left")
q = p[p.ibbs3_kod != "TR"].copy()
# il düzeyindeki oranları bölgeye ağırlıklı ortalamayla toplulaştır (ağırlıklar ADNKS kadın nüfusu ya da
# ilk evlenme sayısı; ADNKS yaş tablosu 2007'den başladığı için 2005–2006 bölge değerleri boş kalır)
agg = []
for (b, y), g in q.groupby(["kfe_bolge", "yil"]):
    r = {"kfe_bolge": b, "yil": y, "il_sayisi": len(g)}
    for c, ww in [("kaba_evlenme", g.kadin_top), ("tdh", g.kadin_15_49), ("ilk_evlenme_yasi_k", g.ilk_evlenme_k_sayi),
                  ("tieh_k", g.kadin_20_34), ("ilk_dogum_yasi", g.kadin_15_49), ("gsyh_kb_tl", g.kadin_top),
                  ("kadin_yuksek_pct", g.kadin_top)]:
        m = g[c].notna() & ww.notna()
        r[c] = np.average(g.loc[m, c], weights=ww[m]) if m.sum() == len(g) and ww[m].sum() > 0 else np.nan
    agg.append(r)
bol = pd.DataFrame(agg).merge(kb, on=["kfe_bolge", "yil"], how="left")
bol = bol.merge(tufe, left_on="yil", right_index=True, how="left")
bol["reel_kfe"] = bol.kfe / bol.tufe_2003 * 100
bol.to_csv(ISLENMIS / "konut_paneli_kfe_bolge.csv", index=False, encoding="utf-8")
print(f"KFE bölge × yıl paneli: {bol.shape}; bölgeler: {sorted(bol.kfe_bolge.unique())}")

# --- 6. Doğrulama: il_paneli_2025.csv (TÜİK Veri Portalı bültenleri) ile karşılaştırma --------
ip = pd.read_csv(ISLENMIS / "il_paneli_2025.csv")
kontrol = []
for kol_p, kol_i, yil in [("kaba_evlenme", "kaba_evlenme_2025", 2025), ("ilk_evlenme_yasi_k", "ilk_evlenme_yasi_k_2025", 2025),
                          ("ilk_evlenme_yasi_e", "ilk_evlenme_yasi_e_2025", 2025), ("tdh", "tdh_2025", 2025),
                          ("tdh", "tdh_2020", 2020), ("ilk_dogum_yasi", "ilk_dogum_yasi_2025", 2025),
                          ("gsyh_kb_tl", "gsyh_kb_tl_2024", 2024)]:
    a = p[p.yil == yil].set_index("ibbs3_kod")[kol_p]
    b = ip.set_index("ibbs3_kod")[kol_i]
    ab = pd.concat([a, b], axis=1, join="inner").dropna()
    kontrol.append({"degisken": kol_p, "yil": yil, "n": len(ab), "en_buyuk_fark": (ab.iloc[:, 0] - ab.iloc[:, 1]).abs().max()})
kontrol = pd.DataFrame(kontrol)
print("\nDOĞRULAMA (SDMX ↔ Veri Portalı bülten tabloları, il_paneli_2025.csv):")
print(kontrol.to_string(index=False))
tr = p[p.ibbs3_kod == "TR"].set_index("yil")
print("\nTürkiye özet (yıllık ortalamalar):")
print(tr[["birim_fiyat", "birim_kira", "gsyh_kb_tl", "fiyat_gelir", "kira_gelir_pct", "kaba_evlenme",
          "ilk_evlenme_yasi_k", "tieh_k", "tdh"]].loc[2010:2025].round(2).to_string())
print("\nSon gözlemler — KFE 2026-09 (TR, İstanbul):", kfe.loc["2026-09", ["TR", "TR10"]].round(2).to_dict(),
      "| birim fiyat 2026-3Ç TR:", ev["bie_birimfiyat"][1].loc["2026-3Ç", "TP_BIRIMFIYAT_TR"])
