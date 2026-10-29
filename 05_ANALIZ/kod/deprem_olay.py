"""
Faz 5 · Rapor 6 — 6 Şubat 2023 depremleri: ilçelerde nüfus, doğum ve evlenme ne oldu? (olay çalışması)
=====================================================================================================
Şiddet ölçüsü: USGS ShakeMap MMI (Mw 7,8 Pazarcık us6000jllz; Mw 7,5 Elbistan us6000jlqa), 30″ ızgara.
  Her nüfuslu 250 m hücreye iki depremin en büyük MMI'si atanır. İlçe değerleri nüfus ağırlıklı:
  mmi (ortalama), mmi8_pay ve mmi7_pay (MMI ≥ 8 ve ≥ 7 bölgede yaşayan nüfus payı).
Olay çalışması: Δ_it = Y_it − Y_i,2022.
  Her yıl ayrı, Δ_it ~ şiddet grubu kuklaları (kontrol: MMI < 5); nüfus ağırlıklı (2022), il kümelenmiş SH.
  Bu, ilçe ve yıl sabit etkili olay çalışmasının yıl yıl yazılmış hâli. 2014–2021 katsayıları ön eğilim sınaması.
  Gruplar: ≥ 8 · 7–8 · 6–7 · 5–6 · kontrol < 5 (ızgara dışı dahil).
Sonuçlar:
  ln nüfus ×100 (yaklaşık %), ln doğum ×100, ln evlenme ×100,
  kaba doğum ve evlenme hızı (‰; nüfus MEDAS ADNKS, 31 Aralık).
Farklılık: MMI ≥ 7 ilçelerde 2022 → 2023 ve 2022 → 2025 değişimi.
  Değişim ~ bina yüksekliği_z + MMI + diri faya ≤ 1 km nüfus payı + il SE; nüfus ağırlıklı.

Girdi : 03_VERI/ham/deprem/*_mmi_high_res.covjson (USGS, kamu malı), 03_VERI/islenmis/ilce_ana_tablo.csv,
        ilce_nufus_2014_2025.csv, ulusal_altyapi/izgara_ilce.tif, izgara_nufus.tif, izgara_ilce_anahtar.csv
Çıktı : 03_VERI/islenmis/ilce_deprem_siddet.csv; 05_ANALIZ/sonuclar/deprem_*.csv; 05_ANALIZ/grafikler/deprem_olay.png|svg
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/deprem_olay.py
"""
import json
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import statsmodels.formula.api as smf
from pyproj import Transformer

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
UA = IS / "ulusal_altyapi"
DEP = KOK / "03_VERI" / "ham" / "deprem"
SON = KOK / "05_ANALIZ" / "sonuclar"
GRAF = KOK / "05_ANALIZ" / "grafikler"
MAVI, TURUNCU, AQUA, SARI = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
YAZI, YAZI_2, YAZI_3, ZEMIN, IZGARA, GRI = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e8e7e3", "#b9b8b3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "axes.edgecolor": YAZI_3, "axes.labelcolor": YAZI_2, "xtick.color": YAZI_2, "ytick.color": YAZI_2,
                     "axes.titlesize": 10, "svg.fonttype": "none"})
YILLAR = list(range(2014, 2026))
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m"


def tr(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


# ---------------------------------------------------------------- 1. ilçe deprem şiddeti
def covjson(ad):
    d = json.load(open(DEP / f"{ad}_mmi_high_res.covjson", encoding="utf-8"))
    ax = d["domain"]["axes"]
    r = d["ranges"]["MMI"]
    assert r["axisNames"] == ["y", "x"]
    v = np.array([np.nan if x is None else x for x in r["values"]], dtype="float64").reshape(r["shape"])
    return ax["x"]["start"], ax["x"]["stop"], ax["x"]["num"], ax["y"]["start"], ax["y"]["stop"], ax["y"]["num"], v


def ornekle(lon, lat, kaynak):
    x0, x1, nx, y0, y1, ny, v = kaynak
    ix = np.rint((lon - x0) / ((x1 - x0) / (nx - 1))).astype(int)
    iy = np.rint((lat - y0) / ((y1 - y0) / (ny - 1))).astype(int)
    ok = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
    out = np.full(lon.shape, np.nan)
    out[ok] = v[iy[ok], ix[ok]]
    return out


with rasterio.open(UA / "izgara_ilce.tif") as r:
    sira = r.read(1)
    T = r.transform
with rasterio.open(UA / "izgara_nufus.tif") as r:
    nuf = r.read(1).astype("float64")
nuf = np.where(np.isfinite(nuf) & (nuf > 0), nuf, 0.0)
rr, cc = np.nonzero((sira > 0) & (nuf > 0))
xs, ys = T.c + (cc + 0.5) * T.a, T.f + (rr + 0.5) * T.e
lon, lat = Transformer.from_crs(LCC, 4326, always_xy=True).transform(xs, ys)
m1 = ornekle(lon, lat, covjson("us6000jllz"))
m2 = ornekle(lon, lat, covjson("us6000jlqa"))
mmi = np.fmax(m1, m2)
mmi_d = np.where(np.isnan(mmi), 1.0, mmi)                   # ızgara dışı: hissedilmedi sayılır (MMI 1)
s, w = sira[rr, cc], nuf[rr, cc]
N = int(sira.max()) + 1
W = np.bincount(s, weights=w, minlength=N)
SI = pd.DataFrame({"sira": np.arange(N),
                   "mmi": np.bincount(s, weights=w * mmi_d, minlength=N) / np.where(W > 0, W, np.nan),
                   "mmi8_pay": 100 * np.bincount(s, weights=w * (mmi_d >= 8), minlength=N) / np.where(W > 0, W, np.nan),
                   "mmi7_pay": 100 * np.bincount(s, weights=w * (mmi_d >= 7), minlength=N) / np.where(W > 0, W, np.nan)})
anah = pd.read_csv(UA / "izgara_ilce_anahtar.csv", dtype={"ilce_kod": str})
SI = SI.merge(anah[["sira", "ilce_kod"]], on="sira").drop(columns="sira")
SI.round(3).to_csv(IS / "ilce_deprem_siddet.csv", index=False, encoding="utf-8")
print(f"MMI ≥ 8 bölgede yaşayan nüfus (ızgara): {np.sum(w * (mmi_d >= 8)):,.0f}; MMI ≥ 7: {np.sum(w * (mmi_d >= 7)):,.0f}")

# ---------------------------------------------------------------- 2. panel
ana = pd.read_csv(IS / "ilce_ana_tablo.csv", dtype={"ilce_kod": str})
ana = ana.drop(columns=[c for c in ana.columns if c.startswith("nufus_medas_")])   # yıllık seri aşağıdaki dosyadan
nufy = pd.read_csv(IS / "ilce_nufus_2014_2025.csv", dtype={"ilce_kod": str})
d = ana.merge(nufy, on="ilce_kod", how="left").merge(SI, on="ilce_kod", how="left")
d = d[d[[f"nufus_medas_{y}" for y in YILLAR]].notna().all(axis=1)].copy()          # 2014'ten beri var olan 970 ilçe
for y in YILLAR:
    d[f"lnnuf_{y}"] = 100 * np.log(d[f"nufus_medas_{y}"])
    d[f"lndog_{y}"] = 100 * np.log(d[f"dogum_{y}"].clip(lower=1))
    d[f"lnevl_{y}"] = 100 * np.log(d[f"evlenme_{y}"].clip(lower=1))
    d[f"kdh_{y}"] = d[f"dogum_{y}"] / d[f"nufus_medas_{y}"] * 1000
    d[f"keh_{y}"] = d[f"evlenme_{y}"] / d[f"nufus_medas_{y}"] * 1000
GRUP = [("≥ 8", 8, 99), ("7–8", 7, 8), ("6–7", 6, 7), ("5–6", 5, 6)]
d["grup"] = "kontrol"
for ad, lo, hi in GRUP:
    d.loc[(d.mmi >= lo) & (d.mmi < hi), "grup"] = ad
GSUT = {ad: f"g{i}" for i, (ad, _, _) in enumerate(GRUP)}
for ad, k in GSUT.items():
    d[k] = (d.grup == ad).astype(float)
ozet = d.groupby("grup").agg(ilce=("ilce_kod", "size"), nufus_2022=("nufus_medas_2022", "sum"),
                            nufus_2025=("nufus_medas_2025", "sum"), mmi=("mmi", "mean"),
                            il_sayisi=("il", "nunique")).reset_index()
ozet["nufus_degisim_pct"] = 100 * (ozet.nufus_2025 / ozet.nufus_2022 - 1)
ozet.round(2).to_csv(SON / "deprem_gruplar.csv", index=False, encoding="utf-8")
print(ozet.round(1).to_string(index=False))

SONUC = {"lnnuf": "Nüfus (log ×100 ≈ %)", "lndog": "Doğum sayısı (log ×100 ≈ %)", "lnevl": "Evlenme sayısı (log ×100 ≈ %)",
         "kdh": "Kaba doğum hızı (‰)", "keh": "Kaba evlenme hızı (‰)"}
satir = []
for s_, sad in SONUC.items():
    for y in YILLAR:
        d["dy"] = d[f"{s_}_{y}"] - d[f"{s_}_2022"]
        if y == 2022:
            for ad in GSUT:
                satir.append({"sonuc": s_, "yil": y, "grup": ad, "b": 0.0, "sh": 0.0, "p": np.nan})
            continue
        sub = d[np.isfinite(d.dy)]
        m = smf.wls("dy ~ " + " + ".join(GSUT.values()), sub, weights=sub.nufus_medas_2022).fit(
            cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
        for ad, k in GSUT.items():
            satir.append({"sonuc": s_, "yil": y, "grup": ad, "b": m.params[k], "sh": m.bse[k], "p": m.pvalues[k]})
OC = pd.DataFrame(satir)
OC.round(4).to_csv(SON / "deprem_olay_katsayilari.csv", index=False, encoding="utf-8")
print("\nOlay çalışması (2022'ye göre, kontrol MMI < 5 farkı):")
print(OC[OC.yil.isin([2019, 2021, 2023, 2024, 2025])].assign(b=lambda t: t.b.round(2))
      .pivot_table(index=["sonuc", "grup"], columns="yil", values="b").to_string())

# ---------------------------------------------------------------- 2b. ön eğilimden arındırılmış etki
# Δ_it (2022'ye göre) uzun panelde: Δ ~ yıl SE + Σ_g g × (yıl − 2022) + Σ_g Σ_k∈{2023,24,25} g × 1[yıl = k].
# Grup eğilimi 2014–2022'den tahmin edilir; deprem sonrası katsayılar eğilimden sapma.
uz = []
for y in YILLAR:
    t = d[["ilce_kod", "il", "nufus_medas_2022"] + list(GSUT.values())].copy()
    t["yil"] = y
    for s_ in SONUC:
        t[f"d_{s_}"] = d[f"{s_}_{y}"] - d[f"{s_}_2022"]
    uz.append(t)
U = pd.concat(uz, ignore_index=True)
U["tr"] = U.yil - 2022
terim = []
for k in GSUT.values():
    U[f"{k}_tr"] = U[k] * U.tr
    terim.append(f"{k}_tr")
    for y in (2023, 2024, 2025):
        U[f"{k}_{y}"] = U[k] * (U.yil == y)
        terim.append(f"{k}_{y}")
ar = []
for s_ in SONUC:
    sub = U[np.isfinite(U[f"d_{s_}"])]
    m = smf.wls(f"d_{s_} ~ C(yil) + " + " + ".join(terim), sub, weights=sub.nufus_medas_2022).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
    for ad, k in GSUT.items():
        for y in (2023, 2024, 2025):
            ar.append({"sonuc": s_, "grup": ad, "yil": y, "b_arindirilmis": m.params[f"{k}_{y}"],
                       "sh": m.bse[f"{k}_{y}"], "p": m.pvalues[f"{k}_{y}"], "on_egilim_yillik": m.params[f"{k}_tr"],
                       "on_egilim_p": m.pvalues[f"{k}_tr"]})
AR = pd.DataFrame(ar)
AR.round(4).to_csv(SON / "deprem_olay_arindirilmis.csv", index=False, encoding="utf-8")
print("\nÖn eğilimden arındırılmış deprem sonrası sapma (2025) ve yıllık ön eğilim:")
print(AR[AR.yil == 2025][["sonuc", "grup", "b_arindirilmis", "sh", "p", "on_egilim_yillik", "on_egilim_p"]]
      .round(3).to_string(index=False))

# ---------------------------------------------------------------- 3. farklılık: bina yüksekliği
sid = d[d.mmi >= 7].copy()
fk = []
for s_ in SONUC:
    for son in (2023, 2025):
        sid["dd"] = sid[f"{s_}_{son}"] - sid[f"{s_}_2022"]
        for ad, f in (("yükseklik + MMI", "yuk_z + mmi"), ("+ fay payı", "yuk_z + mmi + fay1km_pay"),
                      ("+ il SE", "yuk_z + mmi + fay1km_pay + C(il)")):
            sub = sid.dropna(subset=["dd", "yukseklik", "mmi", "fay1km_pay"]).copy()
            sub["yuk_z"] = (sub.yukseklik - sub.yukseklik.mean()) / sub.yukseklik.std(ddof=0)
            m = smf.wls(f"dd ~ {f}", sub, weights=sub.nufus_medas_2022).fit(
                cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
            # az küme (≈ 7–8 il) olduğu için ayrıca HC1 sağlam SH
            mh = smf.wls(f"dd ~ {f}", sub, weights=sub.nufus_medas_2022).fit(cov_type="HC1")
            fk.append({"sonuc": s_, "donem": f"2022→{son}", "model": ad, "b_yukseklik_1ss": m.params["yuk_z"],
                       "sh": m.bse["yuk_z"], "p": m.pvalues["yuk_z"], "p_hc1": mh.pvalues["yuk_z"],
                       "b_mmi": m.params["mmi"], "p_mmi": m.pvalues["mmi"], "n": int(m.nobs), "il_sayisi": sub.il.nunique(),
                       "yuk_ss_m": sub.yukseklik.std(ddof=0)})
FK = pd.DataFrame(fk)
FK.round(4).to_csv(SON / "deprem_yukseklik_farki.csv", index=False, encoding="utf-8")
print(f"\nMMI ≥ 7 ilçeler: {len(sid)}; bina yüksekliği farkı (1 SS = {sid.yukseklik.std(ddof=0):.1f} m):")
print(FK[["sonuc", "donem", "model", "b_yukseklik_1ss", "sh", "p", "p_hc1", "b_mmi", "p_mmi", "n", "il_sayisi"]]
      .round(3).to_string(index=False))

# ---------------------------------------------------------------- 4. pilot ve en çok etkilenen ilçeler
kol = ["il", "ilce_ad_tuik", "mmi", "mmi8_pay", "yukseklik", "fay1km_pay", "nufus_medas_2022", "nufus_medas_2023",
       "nufus_medas_2025", "dogum_2022", "dogum_2023", "dogum_2025", "evlenme_2022", "evlenme_2023", "evlenme_2025"]
en = d.sort_values("mmi", ascending=False).head(25)[kol].copy()
for a, b_ in (("nufus", "nufus_medas"), ("dogum", "dogum"), ("evlenme", "evlenme")):
    en[f"{a}_2023_pct"] = 100 * (en[f"{b_}_2023"] / en[f"{b_}_2022"] - 1)
    en[f"{a}_2025_pct"] = 100 * (en[f"{b_}_2025"] / en[f"{b_}_2022"] - 1)
en.round(2).to_csv(SON / "deprem_en_etkilenen_ilceler.csv", index=False, encoding="utf-8")
PILOT = ["ANTAKYA", "DEFNE", "İSKENDERUN", "ONİKİŞUBAT", "DULKADİROĞLU", "ADIYAMAN MERKEZ", "BATTALGAZİ", "YEŞİLYURT",
         "NURDAĞI", "İSLAHİYE"]
pil = d[d.ilce_ad_tuik.str.upper().isin(PILOT) & d.il.isin(["Hatay", "Kahramanmaraş", "Adıyaman", "Malatya", "Gaziantep"])][kol].copy()
for a, b_ in (("nufus", "nufus_medas"), ("dogum", "dogum"), ("evlenme", "evlenme")):
    pil[f"{a}_2023_pct"] = 100 * (pil[f"{b_}_2023"] / pil[f"{b_}_2022"] - 1)
    pil[f"{a}_2025_pct"] = 100 * (pil[f"{b_}_2025"] / pil[f"{b_}_2022"] - 1)
pil.sort_values("mmi", ascending=False).round(2).to_csv(SON / "deprem_pilot_ilceler.csv", index=False, encoding="utf-8")
print("\nPilot ve büyük kent ilçeleri:")
print(pil.sort_values("mmi", ascending=False)[["il", "ilce_ad_tuik", "mmi", "yukseklik", "nufus_medas_2022", "nufus_2023_pct",
      "nufus_2025_pct", "dogum_2025_pct", "evlenme_2025_pct"]].round(1).to_string(index=False))
print("\nEn yüksek MMI'li 15 ilçe:")
print(en.head(15)[["il", "ilce_ad_tuik", "mmi", "yukseklik", "nufus_2023_pct", "nufus_2025_pct", "dogum_2023_pct",
                   "dogum_2025_pct", "evlenme_2023_pct", "evlenme_2025_pct"]].round(1).to_string(index=False))

# ---------------------------------------------------------------- 5. grafik
RENK = {"≥ 8": TURUNCU, "7–8": SARI, "6–7": AQUA, "5–6": MAVI}
fig = plt.figure(figsize=(11.6, 6.4))
paneller = [("lnnuf", "Nüfus (≈ %)"), ("lndog", "Doğum sayısı (≈ %)"), ("kdh", "Kaba doğum hızı (‰ puan)"),
            ("lnevl", "Evlenme sayısı (≈ %)")]
for k, (s_, baslik) in enumerate(paneller):
    ax = fig.add_axes([0.05 + (k % 2) * 0.485, 0.53 - (k // 2) * 0.43, 0.43, 0.3])
    for ad in ("5–6", "6–7", "7–8", "≥ 8"):
        g = OC[(OC.sonuc == s_) & (OC.grup == ad)]
        if ad == "≥ 8":
            ax.fill_between(g.yil, g.b - 1.96 * g.sh, g.b + 1.96 * g.sh, color=RENK[ad], alpha=0.15, lw=0)
        ax.plot(g.yil, g.b, color=RENK[ad], lw=2.2 if ad == "≥ 8" else 1.6, marker="o", ms=3.5, label=f"MMI {ad}")
    ax.axhline(0, color=YAZI_3, lw=0.8)
    ax.axvline(2022.5, color=YAZI_3, lw=0.8, ls=(0, (3, 3)))
    ax.set_title(baslik, loc="left", color=YAZI, fontsize=9.5)
    ax.set_xticks([2014, 2016, 2018, 2020, 2022, 2023, 2025])
    ax.tick_params(length=0, labelsize=7.8)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color=IZGARA, lw=0.7)
    if k == 0:
        ax.legend(frameon=False, fontsize=7.6, loc="lower left", ncol=2)
fig.text(0.012, 0.975, "6 Şubat 2023: deprem şiddetine göre ilçelerde nüfus, doğum ve evlenme", fontsize=12.5,
         fontweight="bold", color=YAZI, va="top")
fig.text(0.012, 0.93, "2022'ye göre değişimin, sarsıntı hissedilmeyen ilçelere (MMI < 5) göre farkı. Kesikli çizgi deprem; "
         "MMI ≥ 8 grubunda gölge %95 aralık. Nüfus ağırlıklı; il kümelenmiş SH.", fontsize=8.4, color=YAZI_2, va="top")
fig.text(0.012, 0.012, "Kaynak: USGS ShakeMap (us6000jllz, us6000jlqa), TÜİK MEDAS ilçe nüfusu, TÜİK doğum ve evlenme; "
         "deprem_olay.py.", fontsize=7.2, color=YAZI_3)
for uz in ("png", "svg"):
    fig.savefig(GRAF / f"deprem_olay.{uz}", dpi=200)
print("\nYazıldı: ilce_deprem_siddet.csv, deprem_*.csv, deprem_olay.png|svg")
