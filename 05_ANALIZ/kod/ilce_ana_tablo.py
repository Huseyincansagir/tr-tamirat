"""
Faz 5 · Rapor 4 — İlçe ana tablosu ve "önlenebilir ölüm" karşı-olgusu
=====================================================================
1. İlçe ana tablosu (973 ilçe): bütün ilçe katmanları tek dosyada.
   Taban: ilce_paneli_genis.csv (nüfus, doğum ve evlenme 2014–2025, ölüm, hane, eğitim, GHSL, OSM).
   Eklenen:
   - FUE v0.2 (ilce_fue_lite.csv),
   - uydu (ilce_uydu.csv),
   - kentsel stres yükü (stres_ilce_endeks.csv),
   - 250 m ulusal ızgaradan nüfus ağırlıklı göstergeler: eğim; diri faya ≤ 1 / 5 km ve 100 yıllık taşkın alanındaki
     nüfus payı; istasyon, hızlı tren ve sanayi mesafesi; havalimanı süresi.
2. Karşı-olgu: çevre-ölçek ekseni (Ç v0.2) iyileşse yılda kaç ölüm önlenirdi?
   - Model Rapor 13 ile aynı: SMR ~ Ç + kontroller + il sabit etkisi; nüfus ağırlıklı; il kümelenmiş SH.
   - Önlenen ölüm_i = −b × ΔÇ_i × beklenen ölüm_i (2025). SMR = gözlenen / beklenen.
   - b, Ç'nin her puanı başına SMR değişimi.
   Senaryolar [V]:
     S1 · Ç'de ulusal en kötü çeyrekteki ilçeler ulusal medyana çıkar (toplum hedefleri satırının tanımı)
     S2 · her ilçe, ilinin 75. yüzdeliğinin altındaysa o düzeye çıkar (il içi; tahminin dayandığı karşılaştırma)
     S3 · ulusal medyanın altındaki bütün ilçeler medyana çıkar
3. Üçgenleme: PM2.5 için iki bağımsız hesap.
   L · literatür: RR 1,08 (1,06–1,09) / 10 µg/m³, doğal nedenli ölüm (Chen ve Hoek 2020).
       Önlenen ölüm = ölüm × (1 − RR^(−Δ/10)), Δ = PM2.5 − hedef (10 ya da 5 µg/m³).
   E · ekolojik: SMR ~ PM2.5 + kontroller + il SE; önlenen = b_pm × Δ × beklenen ölüm.

Girdi : 03_VERI/islenmis/ilce_paneli_genis.csv, ilce_fue_lite.csv, ilce_uydu.csv, ilce_paneli.gpkg,
        ulusal_altyapi/izgara_*.tif, izgara_ilce_anahtar.csv; 05_ANALIZ/sonuclar/stres_ilce_endeks.csv,
        fue_ilce_gecerlilik.csv (tutarlılık denetimi)
Çıktı : 03_VERI/islenmis/ilce_ana_tablo.csv, ilce_ana_tablo_sozluk.csv;
        05_ANALIZ/sonuclar/onlenebilir_olum_*.csv; 05_ANALIZ/grafikler/onlenebilir_olum.png|svg
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/ilce_ana_tablo.py
            (önce fue_ilce_gecerlilik.py, stres_endeks.py, ulusal_plan_kisit.py, ulusal_plan_erisim.py)
"""
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import statsmodels.formula.api as smf
from matplotlib.colors import BoundaryNorm, ListedColormap

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
UA = IS / "ulusal_altyapi"
SON = KOK / "05_ANALIZ" / "sonuclar"
GRAF = KOK / "05_ANALIZ" / "grafikler"
MAVI, TURUNCU, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
YAZI, YAZI_2, YAZI_3, ZEMIN, IZGARA, GRI = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e8e7e3", "#b9b8b3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "axes.edgecolor": YAZI_3, "axes.labelcolor": YAZI_2, "xtick.color": YAZI_2, "ytick.color": YAZI_2,
                     "axes.titlesize": 10, "svg.fonttype": "none"})


def tr(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


# ---------------------------------------------------------------- 1. ana tablo
ana = pd.read_csv(IS / "ilce_paneli_genis.csv", dtype={"ilce_kod": str})
kaynak = {c: "ilce_paneli_genis.csv" for c in ana.columns}


def ekle(df, dosya, anahtar):
    global ana
    yeni = [c for c in df.columns if c not in ana.columns]
    ana = ana.merge(df[[anahtar] + yeni], on=anahtar, how="left", validate="one_to_one")
    kaynak.update({c: dosya for c in yeni})


ekle(pd.read_csv(IS / "ilce_fue_lite.csv", dtype={"ilce_kod": str}), "ilce_fue_lite.csv", "gid")
ekle(pd.read_csv(IS / "ilce_uydu.csv"), "ilce_uydu.csv", "gid")
st = pd.read_csv(SON / "stres_ilce_endeks.csv", dtype={"ilce_kod": str})
ekle(st[["gid"] + [c for c in st.columns if c.startswith(("KSY", "s_"))]], "stres_ilce_endeks.csv", "gid")

# 250 m ızgaradan nüfus ağırlıklı ilçe göstergeleri
def oku(ad, bant=1):
    with rasterio.open(UA / f"{ad}.tif") as r:
        return r.read(bant)


sira = oku("izgara_ilce").ravel()
nuf = oku("izgara_nufus").ravel().astype("float64")
nuf = np.where(np.isfinite(nuf) & (nuf > 0), nuf, 0.0)
gecerli = (sira > 0) & (nuf > 0)
s, w = sira[gecerli], nuf[gecerli]
N = int(sira.max()) + 1
W = np.bincount(s, weights=w, minlength=N)


def agirlikli(deger, bos=None):
    v = deger.ravel()[gecerli].astype("float64")
    ok = np.isfinite(v) if bos is None else (v != bos) & np.isfinite(v)
    pay = np.bincount(s[ok], weights=w[ok] * v[ok], minlength=N)
    alt = np.bincount(s[ok], weights=w[ok], minlength=N)
    with np.errstate(invalid="ignore", divide="ignore"):
        return pay / alt


kisit = oku("izgara_kisit")
IZ = pd.DataFrame({"sira": np.arange(N)})
IZ["egim_ort"] = agirlikli(np.where(oku("izgara_egim") == 65535, np.nan, oku("izgara_egim") / 10.0))
for bit, ad in ((0, "fay1km_pay"), (1, "fay5km_pay"), (8, "taskin_pay")):
    IZ[ad] = 100 * agirlikli(((kisit >> bit) & 1).astype("float32"))
with rasterio.open(UA / "izgara_erisim.tif") as r:
    for i, ad in enumerate(r.descriptions, 1):
        b = r.read(i).astype("float64")
        b = np.where(b >= 65000, np.nan, b)
        if ad.endswith("_km10"):
            IZ[ad.replace("_km10", "_km")] = agirlikli(b / 10.0)
        else:
            IZ[ad] = agirlikli(b)
IZ["izgara_nufus"] = W
anah = pd.read_csv(UA / "izgara_ilce_anahtar.csv", dtype={"ilce_kod": str})
IZ = IZ.merge(anah[["sira", "ilce_kod"]], on="sira").drop(columns="sira")
ekle(IZ, "ulusal_altyapi/izgara_*.tif (bu betik)", "ilce_kod")
ana.to_csv(IS / "ilce_ana_tablo.csv", index=False, encoding="utf-8")

ACIKLAMA = {
    "smr": "Yaşa standartlaştırılmış ölüm oranı, gözlenen / beklenen ölüm, 2024–2025 (Rapor 07)",
    "tdh_ilce": "Toplam doğurganlık hızı, ilçe (Rapor 03)",
    "egitim": "Kadın 15+ ortalama eğitim yılı", "artis": "Nüfus artışı (göç vekili)",
    "ln_yogunluk": "ln yaşanan yoğunluk", "merkez_pay": "İl merkezi ilçe payı", "yasli_pay": "65+ payı",
    "yukseklik": "Nüfus ağırlıklı bina yüksekliği (GHSL, m)",
    "E_lite": "FUE erişim ekseni (0–100)", "C_lite": "FUE çevre-ölçek ekseni v0.1 (0–100)",
    "C_lite_v2": "FUE çevre-ölçek ekseni v0.2, uydu göstergeleriyle (0–100; Rapor 13)",
    "FUE_lite_v2": "FUE v0.2 bileşik endeks", "pm25": "PM2.5, nüfus ağırlıklı, 2022–2024 (µg/m³, ACAG)",
    "lst": "Yaz yüzey sıcaklığı, nüfus ağırlıklı (°C, MODIS)", "agac300": "300 m içinde ağaç örtüsü (%)",
    "yapili300": "300 m içinde yapılı alan (%)", "KSY": "Kentsel stres yükü endeksi (Rapor 14)",
    "egim_ort": "Nüfus ağırlıklı eğim (%)", "fay1km_pay": "Diri faya ≤ 1 km nüfus payı (%)",
    "fay5km_pay": "Diri faya ≤ 5 km nüfus payı (%)", "taskin_pay": "100 yıllık taşkın alanında nüfus payı (%)",
    "istasyon_km": "En yakın demiryolu istasyonu, nüfus ağırlıklı (km)",
    "hizli_tren_km": "En yakın hızlı tren istasyonu (km)", "havalimani_dk": "En yakın havalimanına süre (dk)",
    "yuk_limani_km": "En yakın yük limanı (km)", "sanayi_km": "En yakın sanayi alanı (km)",
    "izgara_nufus": "Izgaradaki nüfus (TÜİK 2025'e ölçekli GHSL)",
    "beklenen_olum_2025": "Ülke yaş-cinsiyet oranlarıyla beklenen ölüm, 2025", "olum_2025": "Gözlenen ölüm, 2025",
}
soz = pd.DataFrame({"degisken": ana.columns, "kaynak": [kaynak[c] for c in ana.columns],
                    "aciklama": [ACIKLAMA.get(c, "") for c in ana.columns],
                    "dolu_ilce": ana.notna().sum().values})
soz.to_csv(IS / "ilce_ana_tablo_sozluk.csv", index=False, encoding="utf-8")
print(f"ilçe ana tablosu: {ana.shape[0]} ilçe × {ana.shape[1]} değişken; ızgara nüfusu {W.sum():,.0f}")
print(IZ.drop(columns="ilce_kod").describe().T[["mean", "50%", "max"]].round(1).to_string())

# ---------------------------------------------------------------- 2. karşı-olgu
KONT = [("M1 il SE + eğitim + göç", "egitim + artis"),
        ("M2 + ln yoğunluk", "egitim + artis + ln_yogunluk"),
        ("M3 + kentsellik ve yaş yapısı", "egitim + artis + ln_yogunluk + merkez_pay + yasli_pay")]
GER = pd.read_csv(SON / "fue_ilce_gecerlilik.csv")


def model(x, kont):
    sub = ana.dropna(subset=["smr", x, "egitim", "artis", "ln_yogunluk", "merkez_pay", "yasli_pay", "nufus_2025",
                             "beklenen_olum_2025", "olum_2025"]).copy()
    m = smf.wls(f"smr ~ {x} + {kont} + C(il)", sub, weights=sub.nufus_2025).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
    return sub, m.params[x], m.bse[x], m.pvalues[x], sub[x].std(ddof=0) / sub["smr"].std(ddof=0)


def senaryo_delta(sub, x, ad, iyi_yon=+1):
    """ΔX_i ≥ 0: iyileşme miktarı (Ç için yukarı)."""
    v = sub[x]
    if ad == "S1":
        q1, med = v.quantile(0.25), v.median()
        return np.where(v < q1, med - v, 0.0)
    if ad == "S2":
        p75 = sub.groupby("il")[x].transform(lambda s: s.quantile(0.75))
        return np.clip(p75 - v, 0, None)
    if ad == "S3":
        return np.clip(v.median() - v, 0, None)


SEN = {"S1": "Ç'de en kötü çeyrek → ulusal medyan", "S2": "Her ilçe → ilinin 75. yüzdeliği (il içi)",
       "S3": "Medyanın altı → medyan"}
rows, ilce_rows = [], []
toplam_olum = None
for mad, kont in KONT:
    sub, b, sh, p, olcek = model("C_lite_v2", kont)
    beta_z = b * olcek
    ref = GER[(GER.sonuc == "smr") & (GER.endeks == "C_lite_v2") & (GER.model == mad[3:])].beta
    if len(ref):
        assert abs(ref.iloc[0] - beta_z) < 1e-3, f"Rapor 13 katsayısıyla tutarsız: {ref.iloc[0]} / {beta_z}"
    toplam_olum = sub.olum_2025.sum()
    for sk, sad in SEN.items():
        dC = senaryo_delta(sub, "C_lite_v2", sk)
        on = -b * dC * sub.beklenen_olum_2025           # önlenen ölüm (b < 0 → pozitif)
        on_lo = -(b - 1.96 * sh) * dC * sub.beklenen_olum_2025
        on_hi = -(b + 1.96 * sh) * dC * sub.beklenen_olum_2025
        etk = dC > 0
        rows.append({"yaklasim": "Ç v0.2 (ekolojik)", "model": mad, "senaryo": sk, "senaryo_ad": sad,
                     "b_puan_basi": b, "b_sh": sh, "beta_z": beta_z, "p": p,
                     "onlenen_olum": on.sum(), "alt_95": min(on_lo.sum(), on_hi.sum()),
                     "ust_95": max(on_lo.sum(), on_hi.sum()), "toplam_olum_pay_pct": 100 * on.sum() / toplam_olum,
                     "etkilenen_ilce": int(etk.sum()), "etkilenen_nufus": sub.nufus_2025[etk].sum(),
                     "ort_deltaC_etkilenen": dC[etk].mean()})
        if mad.startswith("M3"):
            ilce_rows.append(pd.DataFrame({"ilce_kod": sub.ilce_kod, "il": sub.il, "ilce": sub.ilce_ad_tuik,
                                           "senaryo": sk, "deltaC": dC, "onlenen_olum": on,
                                           "onlenen_100bin": on / sub.nufus_2025 * 1e5}))

# PM2.5 üçgenlemesi
RR = {"merkez": 1.08, "alt": 1.06, "ust": 1.09}
pmsub = ana.dropna(subset=["pm25", "olum_2025", "beklenen_olum_2025", "nufus_2025"])
for hedef in (10, 5):
    dlt = np.clip(pmsub.pm25 - hedef, 0, None)
    r = {k: (pmsub.olum_2025 * (1 - v ** (-dlt / 10))).sum() for k, v in RR.items()}
    rows.append({"yaklasim": "PM2.5 literatür (Chen ve Hoek 2020)", "model": f"RR 1,08/10 µg; hedef {hedef} µg/m³",
                 "senaryo": f"PM{hedef}", "senaryo_ad": f"PM2.5 her ilçede ≤ {hedef} µg/m³",
                 "onlenen_olum": r["merkez"], "alt_95": r["alt"], "ust_95": r["ust"],
                 "toplam_olum_pay_pct": 100 * r["merkez"] / pmsub.olum_2025.sum(),
                 "etkilenen_ilce": int((dlt > 0).sum()), "etkilenen_nufus": pmsub.nufus_2025[dlt > 0].sum()})
    for mad, kont in KONT:
        sub, b, sh, p, olcek = model("pm25", kont)
        d2 = np.clip(sub.pm25 - hedef, 0, None)
        on = b * d2 * sub.beklenen_olum_2025
        lo, hi = (b - 1.96 * sh) * d2 * sub.beklenen_olum_2025, (b + 1.96 * sh) * d2 * sub.beklenen_olum_2025
        rows.append({"yaklasim": "PM2.5 ekolojik (bu proje)", "model": mad, "senaryo": f"PM{hedef}",
                     "senaryo_ad": f"PM2.5 her ilçede ≤ {hedef} µg/m³", "b_puan_basi": b, "b_sh": sh,
                     "beta_z": b * olcek, "p": p, "onlenen_olum": on.sum(), "alt_95": min(lo.sum(), hi.sum()),
                     "ust_95": max(lo.sum(), hi.sum()), "toplam_olum_pay_pct": 100 * on.sum() / sub.olum_2025.sum(),
                     "etkilenen_ilce": int((d2 > 0).sum()), "etkilenen_nufus": sub.nufus_2025[d2 > 0].sum()})
R = pd.DataFrame(rows)
R.round(4).to_csv(SON / "onlenebilir_olum_senaryolar.csv", index=False, encoding="utf-8")
IL = pd.concat(ilce_rows)
IL.round(3).to_csv(SON / "onlenebilir_olum_ilce.csv", index=False, encoding="utf-8")
ILT = (IL.groupby(["senaryo", "il"]).onlenen_olum.sum().reset_index()
       .sort_values(["senaryo", "onlenen_olum"], ascending=[True, False]))
ILT.round(1).to_csv(SON / "onlenebilir_olum_il.csv", index=False, encoding="utf-8")
print(f"\n2025 toplam ölüm (analiz örneklemi): {toplam_olum:,.0f}")
print(R[["yaklasim", "model", "senaryo", "onlenen_olum", "alt_95", "ust_95", "toplam_olum_pay_pct", "etkilenen_ilce",
         "beta_z", "p"]].round(3).to_string())
print("\nS1, M3: en çok ölüm önlenen 10 il:")
print(ILT[ILT.senaryo == "S1"].head(10).round(0).to_string(index=False))

# ---------------------------------------------------------------- 3. grafik
fig = plt.figure(figsize=(11.2, 6.0))
ax = fig.add_axes([0.03, 0.12, 0.42, 0.68])
G = [("Ç v0.2 · S1 en kötü çeyrek → medyan", R[(R.yaklasim.str.startswith("Ç")) & (R.senaryo == "S1")]),
     ("Ç v0.2 · S2 il içi en iyi çeyrek", R[(R.yaklasim.str.startswith("Ç")) & (R.senaryo == "S2")]),
     ("PM2.5 ≤ 10 · literatür", R[(R.yaklasim.str.contains("literatür")) & (R.senaryo == "PM10")]),
     ("PM2.5 ≤ 10 · ekolojik", R[(R.yaklasim.str.contains("ekolojik")) & (R.senaryo == "PM10")])]
y = 0
for ad, g in G:
    ax.text(0, y + 0.15, ad, fontsize=8.4, fontweight="bold", color=YAZI_2, va="bottom")
    y -= 0.75
    for _, r in g.iterrows():
        renk = MAVI if r.yaklasim.startswith("Ç") else (AQUA if "literatür" in r.yaklasim else TURUNCU)
        ax.plot([r.alt_95, r.ust_95], [y, y], color=renk, lw=2, alpha=0.45, solid_capstyle="round")
        ax.plot(r.onlenen_olum, y, "o", color=renk, ms=7, markeredgecolor=ZEMIN, markeredgewidth=1.5)
        etik = r.model.split(" ")[0] if r.model.startswith("M") else "RR"
        ax.text(r.ust_95 + 400, y, f"{etik}  {tr(r.onlenen_olum)}", va="center", fontsize=7.8, color=YAZI)
        y -= 1
    y -= 0.6
ax.set_yticks([])
ax.set_ylim(y + 0.4, 1.1)
ax.set_xlim(left=0)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: tr(v)))
ax.set_title("Yılda önlenebilir ölüm (nokta) ve %95 aralık", loc="left", color=YAZI, fontsize=9.5)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.grid(axis="x", color=IZGARA, lw=0.7)
ax.set_axisbelow(True)
ax.tick_params(length=0)

ax2 = fig.add_axes([0.50, 0.08, 0.49, 0.70])
gdf = gpd.read_file(IS / "ilce_paneli.gpkg")[["ilce_kod", "geometry"]]
gdf["ilce_kod"] = gdf.ilce_kod.astype(str)
m = gdf.merge(IL[IL.senaryo == "S1"][["ilce_kod", "onlenen_100bin"]], on="ilce_kod", how="left")
sinir = [0, 0.001, 5, 10, 20, 40, 1e9]
renkler = [IZGARA, "#d6e6f8", "#a9c8ee", "#6fa3e3", MAVI, "#174f94"]
cmap, norm = ListedColormap(renkler), BoundaryNorm(sinir, len(renkler))
m.to_crs("+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35").plot(
    column=m.onlenen_100bin.fillna(0), cmap=cmap, norm=norm, ax=ax2, edgecolor=ZEMIN, linewidth=0.1)
ax2.set_axis_off()
ax2.set_title("S1, M3: 100 bin kişi başına önlenebilir ölüm (ilçe)", loc="left", color=YAZI, fontsize=9.5)
et = ["Senaryo dışı", "0–5", "5–10", "10–20", "20–40", "40+"]
x0 = 0.02
for rk, e in zip(renkler, et):
    ax2.add_patch(plt.Rectangle((x0, -0.04), 0.03, 0.035, transform=ax2.transAxes, color=rk, clip_on=False))
    ax2.text(x0 + 0.037, -0.022, e, transform=ax2.transAxes, fontsize=7.4, va="center", color=YAZI_2)
    x0 += 0.06 + 0.0115 * len(e)
fig.text(0.012, 0.97, "Mekân iyileşirse yılda kaç ölüm önlenir? Ekolojik tahmin literatürle örtüşüyor", fontsize=12.5,
         fontweight="bold", color=YAZI, va="top")
fig.text(0.012, 0.915, "Ç v0.2: il içi katsayıyla karşı-olgu (M1 temel … M3 kentsellik ve yaş yapısı kontrollü). PM2.5: "
         "literatür katsayısı (RR 1,08) ile bu projenin ilçe katsayısı. Ekolojik üst sınır; nedensellik iddiası değil.",
         fontsize=8.4, color=YAZI_2, va="top", wrap=True)
fig.text(0.012, 0.015, "Kaynak: ilce_ana_tablo.csv, onlenebilir_olum_senaryolar.csv; TÜİK 2025 ölüm, ACAG PM2.5, "
         "Chen ve Hoek 2020.", fontsize=7.2, color=YAZI_3)
for uz in ("png", "svg"):
    fig.savefig(GRAF / f"onlenebilir_olum.{uz}", dpi=200)
print("\nYazıldı: ilce_ana_tablo.csv, ilce_ana_tablo_sozluk.csv, onlenebilir_olum_*.csv, onlenebilir_olum.png|svg")
