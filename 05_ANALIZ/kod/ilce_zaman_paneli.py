"""
Faz 5 · Rapor 5 — İlçe zaman paneli (2014–2025): doğum ve evlenme hızı kentsel biçime göre nasıl değişti?
====================================================================================================
Faz 2'nin kesitsel bulgusu: il içinde bir kat daha yüksek binada yaşanan ilçede doğurganlık ≈ 0,03 çocuk düşük.
Bu betik aynı soruyu zaman içinde soruyor: 2014–2025'te doğum ve evlenme hızı hangi ilçelerde daha hızlı düştü?

Sonuçlar (ilçe × yıl, ‰): kaba doğum hızı (KDH) = doğum / nüfus × 1000; kaba evlenme hızı (KEH) = evlenme / nüfus × 1000.

Tasarımlar:
 1. Uzun fark: Δ = ort(2023–2025) − ort(2014–2016).
    Δ ~ biçim_z + başlangıç düzeyi + eğitim + göç (Δ ln nüfus 2014→2025) + il SE;
    nüfus ağırlıklı, il kümelenmiş SH.
    Biçim değişkenleri: bina yüksekliği (GHSL 2018), Ç v0.2, E (erişim), yoğunluk değişimi (GHSL 2000→2020).
 2. Yıl yıl katsayı (olay çalışması biçiminde): Δ_t = Y_t − ort(2014–2016).
    Δ_t ~ biçim_z + aynı kontroller + il SE, her t için ayrı.
    Katsayının zaman içindeki seyri, biçimin farkı büyütüp büyütmediğini gösterir.
 3. Sağlamlık: (a) deprem bölgesi 11 il hariç; (b) en hızlı büyüyen %10 ilçe hariç; (c) başlangıç düzeyi kontrolsüz.

Girdi : 03_VERI/islenmis/ilce_ana_tablo.csv (Rapor 25), ilce_nufus_2014_2025.csv (TÜİK MEDAS, tarayıcıyla),
        ilce_ghsl_degisim.csv (ilce_ghsl_degisim.py)
Çıktı : 05_ANALIZ/sonuclar/zaman_paneli_*.csv, 05_ANALIZ/grafikler/zaman_paneli.png|svg
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/ilce_zaman_paneli.py
"""
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
SON = KOK / "05_ANALIZ" / "sonuclar"
GRAF = KOK / "05_ANALIZ" / "grafikler"
MAVI, TURUNCU, AQUA, SARI = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
YAZI, YAZI_2, YAZI_3, ZEMIN, IZGARA = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e8e7e3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "axes.edgecolor": YAZI_3, "axes.labelcolor": YAZI_2, "xtick.color": YAZI_2, "ytick.color": YAZI_2,
                     "axes.titlesize": 10, "svg.fonttype": "none"})
YILLAR = list(range(2014, 2026))
DEPREM_IL = ["Adana", "Adıyaman", "Diyarbakır", "Elazığ", "Gaziantep", "Hatay", "Kahramanmaraş", "Kilis", "Malatya",
             "Osmaniye", "Şanlıurfa"]                     # 6 Şubat 2023, genel hayata etkili afet bölgesi [D: 5779 Geçici md. 3]


def tr(x, nd=2):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


# ---------------------------------------------------------------- 1. veri
ana = pd.read_csv(IS / "ilce_ana_tablo.csv", dtype={"ilce_kod": str})
ana = ana.drop(columns=[c for c in ana.columns if c.startswith("nufus_medas_")])   # yıllık seri aşağıdaki dosyadan
nuf = pd.read_csv(IS / "ilce_nufus_2014_2025.csv", dtype={"ilce_kod": str})
gh = pd.read_csv(IS / "ilce_ghsl_degisim.csv", dtype={"ilce_kod": str})[["ilce_kod", "d_ln_yogunluk", "d_ln_yapili"]]
d = ana.merge(nuf, on="ilce_kod", how="left", suffixes=("", "_medas")).merge(gh, on="ilce_kod", how="left")

# sağlama: MEDAS 2024–2025 = SDMX 2024–2025 (Rapor 03)
sag = {y: int((d[f"nufus_{y}"] == d[f"nufus_medas_{y}"]).sum()) for y in (2024, 2025)}
print("MEDAS = SDMX nüfus eşleşen ilçe:", sag, "/", len(d))
for y in YILLAR:
    n = d[f"nufus_medas_{y}"]
    d[f"kdh_{y}"] = d[f"dogum_{y}"] / n * 1000
    d[f"keh_{y}"] = d[f"evlenme_{y}"] / n * 1000
d["d_ln_nufus"] = np.log(d.nufus_medas_2025 / d.nufus_medas_2014)
d["genc_pay"] = 100 * d.nufus_20_34 / d.nufus_medas_2024          # 20–34 yaş payı (MEDAS 2024; Rapor 07)
d["yasli65_pay"] = 100 * d.nufus_65p / d.medas_nufus               # 65+ payı (MEDAS 2025; Rapor 03)
ulusal = pd.DataFrame({"yil": YILLAR,
                       "dogum": [d[f"dogum_{y}"].sum() for y in YILLAR],
                       "evlenme": [d[f"evlenme_{y}"].sum() for y in YILLAR],
                       "nufus": [d[f"nufus_medas_{y}"].sum() for y in YILLAR]})
ulusal["kdh"] = ulusal.dogum / ulusal.nufus * 1000
ulusal["keh"] = ulusal.evlenme / ulusal.nufus * 1000
ulusal.round(3).to_csv(SON / "zaman_paneli_ulusal.csv", index=False, encoding="utf-8")
print(ulusal.round(2).to_string(index=False))

BAS, SONY = [2014, 2015, 2016], [2023, 2024, 2025]
for s in ("kdh", "keh"):
    d[f"{s}_bas"] = d[[f"{s}_{y}" for y in BAS]].mean(axis=1)
    d[f"{s}_son"] = d[[f"{s}_{y}" for y in SONY]].mean(axis=1)
    d[f"d_{s}"] = d[f"{s}_son"] - d[f"{s}_bas"]
    d[f"dpct_{s}"] = 100 * d[f"d_{s}"] / d[f"{s}_bas"]

BICIM = {"yukseklik": "Bina yüksekliği (GHSL 2018, m)", "C_lite_v2": "Çevre-ölçek ekseni Ç v0.2",
         "E_lite": "Erişim ekseni E", "d_ln_yogunluk": "Yoğunluk değişimi 2000→2020 (GHSL)"}
KONT = "egitim + d_ln_nufus"


def fit(df, y, x, kont, ek=""):
    sub = df.dropna(subset=[y, x, "egitim", "d_ln_nufus", "nufus_2025", "il", "genc_pay", "yasli65_pay"]
                    + ([v.strip() for v in ek.split("+")] if ek else [])).copy()
    sub["x_z"] = (sub[x] - sub[x].mean()) / sub[x].std(ddof=0)
    f = f"{y} ~ x_z + {kont}" + (f" + {ek}" if ek else "") + " + C(il)"
    m = smf.wls(f, sub, weights=sub.nufus_2025).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
    return m.params["x_z"], m.bse["x_z"], m.pvalues["x_z"], int(m.nobs)


def yz(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "†" if p < 0.10 else ""


# ---------------------------------------------------------------- 2. uzun fark
ORNEK = {"tümü": d,
         "deprem bölgesi hariç": d[~d.il.isin(DEPREM_IL)],
         "en hızlı büyüyen %10 hariç": d[d.d_ln_nufus < d.d_ln_nufus.quantile(0.9)]}
satir = []
for s, sad in (("kdh", "Kaba doğum hızı (‰)"), ("keh", "Kaba evlenme hızı (‰)")):
    for x, xad in BICIM.items():
        for oad, o in ORNEK.items():
            for kad, ek in (("başlangıç kontrollü", f"{s}_bas"), ("başlangıç kontrolsüz", ""),
                            ("başlangıç + yaş yapısı", f"{s}_bas + genc_pay + yasli65_pay")):
                if oad != "tümü" and kad != "başlangıç kontrollü":
                    continue
                b, sh, p, n = fit(o, f"d_{s}", x, KONT, ek)
                satir.append({"sonuc": s, "sonuc_ad": sad, "bicim": x, "bicim_ad": xad, "ornek": oad, "kontrol": kad,
                              "b_1ss": b, "sh": sh, "p": p, "n": n, "yildiz": yz(p),
                              "ort_bas": np.average(o[f"{s}_bas"].dropna(), weights=o.loc[o[f"{s}_bas"].notna(), "nufus_2025"]),
                              "ort_degisim": np.average(o[f"d_{s}"].dropna(), weights=o.loc[o[f"d_{s}"].notna(), "nufus_2025"])})
UF = pd.DataFrame(satir)
UF.round(4).to_csv(SON / "zaman_paneli_uzun_fark.csv", index=False, encoding="utf-8")
print("\nUZUN FARK (2014–16 → 2023–25), biçimde 1 SS fark başına değişim farkı (‰ puan):")
print(UF.assign(b=UF.b_1ss.round(3).astype(str) + UF.yildiz)
      .pivot_table(index=["sonuc", "bicim"], columns=["ornek", "kontrol"], values="b", aggfunc="first").to_string())

# ---------------------------------------------------------------- 2b. düşüşün ne kadarı ortak, ne kadarı biçim?
ay = []
for s in ("kdh", "keh"):
    sub = d.dropna(subset=[f"d_{s}", f"{s}_bas", "egitim", "d_ln_nufus", "genc_pay", "yasli65_pay", "nufus_2025"]
                   + list(BICIM)).copy()
    agr = sub.nufus_2025
    ort = np.average(sub[f"d_{s}"], weights=agr)
    tss = np.sum(agr * (sub[f"d_{s}"] - ort) ** 2)
    adim = [("il sabit etkisi", "C(il)"),
            ("+ başlangıç, eğitim, göç, yaş yapısı", f"C(il) + {s}_bas + egitim + d_ln_nufus + genc_pay + yasli65_pay"),
            ("+ dört biçim göstergesi", f"C(il) + {s}_bas + egitim + d_ln_nufus + genc_pay + yasli65_pay + "
                                        + " + ".join(BICIM))]
    for ad, f in adim:
        m = smf.wls(f"d_{s} ~ {f}", sub, weights=agr).fit()
        ay.append({"sonuc": s, "adim": ad, "r2": 1 - np.sum(agr * m.resid ** 2) / tss, "n": int(m.nobs),
                   "ulusal_ort_degisim": ort})
AY = pd.DataFrame(ay)
AY["r2_artisi"] = AY.groupby("sonuc").r2.diff().fillna(AY.r2)
AY.round(4).to_csv(SON / "zaman_paneli_varyans.csv", index=False, encoding="utf-8")
print("\nDeğişimin ilçeler arası farkı (nüfus ağırlıklı R²):\n", AY.round(3).to_string(index=False))

# ---------------------------------------------------------------- 3. yıl yıl katsayılar
yy = []
for s in ("kdh", "keh"):
    for x in BICIM:
        for y in YILLAR:
            d[f"dt_{s}_{y}"] = d[f"{s}_{y}"] - d[f"{s}_bas"]
            b, sh, p, n = fit(d, f"dt_{s}_{y}", x, KONT, f"{s}_bas")
            yy.append({"sonuc": s, "bicim": x, "yil": y, "b_1ss": b, "sh": sh, "p": p, "n": n})
YY = pd.DataFrame(yy)
YY.round(4).to_csv(SON / "zaman_paneli_yil_katsayilari.csv", index=False, encoding="utf-8")

# Faz 2 kesitiyle kıyas: aynı yıllarda düzey ilişkisi (KDH ~ yükseklik + kontroller + il SE)
kes = []
for y in (2014, 2025):
    b, sh, p, n = fit(d, f"kdh_{y}", "yukseklik", "egitim")
    kes.append({"yil": y, "b_1ss": b, "sh": sh, "p": p, "n": n})
KES = pd.DataFrame(kes)
KES.round(4).to_csv(SON / "zaman_paneli_kesit_kiyas.csv", index=False, encoding="utf-8")
print("\nKesit (düzey) ilişkisi, KDH ~ yükseklik_z + eğitim + il SE:\n", KES.round(3).to_string(index=False))
d[["ilce_kod", "il", "ilce_ad_tuik", "nufus_medas_2014", "nufus_medas_2025", "d_ln_nufus", "kdh_bas", "kdh_son", "d_kdh",
   "dpct_kdh", "keh_bas", "keh_son", "d_keh", "dpct_keh", "yukseklik", "C_lite_v2", "E_lite", "d_ln_yogunluk"]] \
    .round(4).to_csv(SON / "zaman_paneli_ilce.csv", index=False, encoding="utf-8")

# ---------------------------------------------------------------- 4. grafik
fig = plt.figure(figsize=(11.2, 5.6))
ax0 = fig.add_axes([0.05, 0.14, 0.26, 0.6])
ax0.plot(ulusal.yil, ulusal.kdh, color=MAVI, lw=2, marker="o", ms=4, label="Doğum ‰")
ax0.plot(ulusal.yil, ulusal.keh, color=TURUNCU, lw=2, marker="o", ms=4, label="Evlenme ‰")
for c, r in (("kdh", MAVI), ("keh", TURUNCU)):
    ax0.annotate(tr(ulusal[c].iloc[0], 1), (ulusal.yil.iloc[0], ulusal[c].iloc[0]), xytext=(0, 7), textcoords="offset points",
                 ha="center", fontsize=7.8, color=YAZI)
    ax0.annotate(tr(ulusal[c].iloc[-1], 1), (ulusal.yil.iloc[-1], ulusal[c].iloc[-1]), xytext=(0, 7),
                 textcoords="offset points", ha="center", fontsize=7.8, color=YAZI)
ax0.set_ylim(0, ulusal.kdh.max() * 1.15)
ax0.set_title("Türkiye: kaba doğum ve evlenme hızı (‰)", loc="left", color=YAZI, fontsize=9.5)
ax0.legend(frameon=False, fontsize=8, loc="lower left")
ax0.set_xticks([2014, 2017, 2020, 2023, 2025])
for sp in ("top", "right"):
    ax0.spines[sp].set_visible(False)
ax0.grid(axis="y", color=IZGARA, lw=0.7)
ax0.tick_params(length=0)

for k, (s, baslik) in enumerate((("kdh", "Doğum hızı farkı"), ("keh", "Evlenme hızı farkı"))):
    ax = fig.add_axes([0.38 + k * 0.31, 0.14, 0.27, 0.6])
    for x, renk in (("yukseklik", TURUNCU), ("C_lite_v2", AQUA), ("E_lite", MAVI)):
        g = YY[(YY.sonuc == s) & (YY.bicim == x)]
        ax.fill_between(g.yil, g.b_1ss - 1.96 * g.sh, g.b_1ss + 1.96 * g.sh, color=renk, alpha=0.13, lw=0)
        ax.plot(g.yil, g.b_1ss, color=renk, lw=2, label=BICIM[x].split(" (")[0])
    ax.axhline(0, color=YAZI_3, lw=0.8)
    ax.axvspan(2013.6, 2016.4, color=IZGARA, alpha=0.6, lw=0)
    ax.text(2015, ax.get_ylim()[1] * 0.92 if ax.get_ylim()[1] > 0 else 0, "başlangıç", ha="center", fontsize=7.2,
            color=YAZI_3)
    ax.set_title(f"{baslik}: biçimde 1 SS fark (‰ puan)", loc="left", color=YAZI, fontsize=9.5)
    ax.set_xticks([2014, 2017, 2020, 2023, 2025])
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color=IZGARA, lw=0.7)
    ax.tick_params(length=0)
    if k == 0:
        ax.legend(frameon=False, fontsize=7.8, loc="lower left")
fig.text(0.012, 0.97, "2014–2025: doğum ve evlenme hızı hangi ilçelerde daha hızlı düştü?", fontsize=12.5,
         fontweight="bold", color=YAZI, va="top")
fig.text(0.012, 0.915, "Orta ve sağ: her yıl, 2014–16 düzeyine göre değişimin biçime göre farkı. İl sabit etkisi, eğitim, "
         "göç ve başlangıç düzeyi kontrollü; nüfus ağırlıklı; gölge %95 aralık.", fontsize=8.4, color=YAZI_2, va="top")
fig.text(0.012, 0.015, "Kaynak: TÜİK doğum ve evlenme (SDMX), ilçe nüfusu 2014–2025 (MEDAS), GHSL, FUE v0.2; "
         "ilce_zaman_paneli.py.", fontsize=7.2, color=YAZI_3)
for uz in ("png", "svg"):
    fig.savefig(GRAF / f"zaman_paneli.{uz}", dpi=200)
print("\nYazıldı: zaman_paneli_*.csv, zaman_paneli.png|svg")
