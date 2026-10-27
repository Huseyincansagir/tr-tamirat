"""
973 ilçe haritaları ve il içi etki grafikleri
============================================
Girdi : 03_VERI/islenmis/ilce_paneli.gpkg, 03_VERI/islenmis/ilce_paneli_analiz.csv,
        05_ANALIZ/sonuclar/ilce_ana_model_artiklar.csv   (önce ilce_paneli_analiz.py çalıştırılmalı)
Çıktı : 04_HARITA/ilce_haritalari_2025.png|svg, 04_HARITA/istanbul_ilce_2025.png|svg,
        05_ANALIZ/grafikler/ilce_il_ici_yukseklik_egitim.png|svg
"""

import sys
from pathlib import Path

import geopandas as gpd
import mapclassify
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
SONUC = KOK / "05_ANALIZ" / "sonuclar"
GRAFIK = KOK / "05_ANALIZ" / "grafikler"
HARITA = KOK / "04_HARITA"

SIRALI = ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"]
IRAKSAK = ["#b8312f", "#ea8f8d", "#f0efec", "#86b6ef", "#256abf"]
YAZI, YAZI_2, ZEMIN = "#0b0b0b", "#52514e", "#fcfcfb"
MAVI, TURUNCU = "#2a78d6", "#eb6834"
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN})

g = gpd.read_file(IS / "ilce_paneli.gpkg")[["ilce_kod", "geometry"]]
g["ilce_kod"] = g.ilce_kod.astype(str)
d = pd.read_csv(IS / "ilce_paneli_analiz.csv", dtype={"ilce_kod": str})
art = pd.read_csv(SONUC / "ilce_ana_model_artiklar.csv", dtype={"ilce_kod": str})
g = g.merge(d, on="ilce_kod").merge(art, on="ilce_kod", how="left").to_crs(LCC)
il_sinir = g.dissolve(by="il").boundary


def tr(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def harita(ax, gdf, kolon, baslik, alt, nd=1, sinirlar=None, renkler=SIRALI, il_cizgi=True, kenar=0.15):
    s = gdf[kolon]
    if sinirlar is None:
        q = mapclassify.Quantiles(s.dropna(), k=5)
        sinirlar = [s.min() - 1e-9] + list(q.bins)
    cmap, norm = ListedColormap(renkler), BoundaryNorm(sinirlar, len(renkler))
    gdf.plot(ax=ax, column=kolon, cmap=cmap, norm=norm, edgecolor="white", linewidth=kenar)
    if il_cizgi:
        gpd.GeoSeries(il_sinir).plot(ax=ax, color="#3d3d3a", linewidth=0.35)
    ax.set_axis_off()
    ax.set_title(baslik, loc="left", fontsize=11, fontweight="bold", pad=14)
    ax.text(0, 1.0, alt, transform=ax.transAxes, fontsize=8, color=YAZI_2, va="bottom")
    eti = []
    for i in range(len(renkler)):
        a = max(sinirlar[i], s.min()) if i == 0 else sinirlar[i]
        b = min(sinirlar[i + 1], s.max()) if i == len(renkler) - 1 else sinirlar[i + 1]
        eti.append(Patch(facecolor=renkler[i], edgecolor="#bbb", lw=0.3, label=f"{tr(a, nd)} – {tr(b, nd)}"))
    ax.legend(handles=eti, loc="lower left", bbox_to_anchor=(0, -0.13), ncol=3, frameon=False, fontsize=7,
              handlelength=1.2, columnspacing=0.8)


# --- Türkiye ilçe haritaları -----------------------------------------------------------
fig, axs = plt.subplots(2, 2, figsize=(16, 10.5), dpi=150)
fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.05, hspace=0.32, wspace=0.05)
fig.text(0.02, 0.955, "973 ilçede doğurganlık, bina yüksekliği ve kadın eğitimi", fontsize=19, fontweight="bold")
fig.text(0.02, 0.928, "Beşte birlik dilimler · koyu çizgiler il sınırları · Kaynak: TÜİK ADNKS 2025 ve doğum 2025 (MEDAS, SDMX), "
         "GHSL R2023A bina yüksekliği 2018 ve nüfus 2020", fontsize=9.5, color=YAZI_2)
harita(axs[0, 0], g, "tdh_ilce", "Toplam doğurganlık hızı (ilçe tahmini)",
       "2025 · dolaylı standartlaştırma: doğum / (15-49 kadın × Türkiye yaş hızları) × 1,42", nd=2)
harita(axs[0, 1], g, "yukseklik", "İnsanların yaşadığı binaların ortalama yüksekliği",
       "metre · nüfus ağırlıklı (GHSL) · 3 m ≈ 1 kat", nd=1)
harita(axs[1, 0], g, "egitim", "15 yaş üstü kadınların ortalama eğitim yılı", "2025 · bitirilen okuldan hesaplandı", nd=1)
harita(axs[1, 1], g, "pay_h15p", "5+ katlı dokuda yaşayan nüfus",
       "% · ortalama bina yüksekliği ≥15 m olan 100 m hücreler (GHSL)", nd=1,
       sinirlar=[-1e-9, 0.5, 5, 15, 35, 100.1], renkler=["#f0efec"] + SIRALI[1:])
for uz in ("png", "svg"):
    fig.savefig(HARITA / f"ilce_haritalari_2025.{uz}", facecolor=ZEMIN)
plt.close(fig)

# --- İstanbul -----------------------------------------------------------------------------
ist = g[g.il == "İstanbul"].copy()
fig, axs = plt.subplots(1, 3, figsize=(17, 6.2), dpi=150)
fig.subplots_adjust(left=0.01, right=0.99, top=0.80, bottom=0.10, wspace=0.04)
fig.text(0.01, 0.94, "İstanbul'un 39 ilçesi: doğurganlığı yükseklik mi, eğitim mi izliyor?", fontsize=17, fontweight="bold")
fig.text(0.01, 0.895, "İlçeler arası korelasyon: doğurganlık–yükseklik r = −0,33 · doğurganlık–kadın eğitimi r = −0,78. "
         "İkisi birlikte modellendiğinde yüksekliğin etkisi kayboluyor (β = −0,04, anlamsız).", fontsize=9.5, color=YAZI_2)
harita(axs[0], ist, "tdh_ilce", "Toplam doğurganlık hızı", "2025 · ilçe tahmini", nd=2, il_cizgi=False, kenar=0.5)
harita(axs[1], ist, "yukseklik", "Yaşanan binaların ortalama yüksekliği", "metre · nüfus ağırlıklı", nd=1, il_cizgi=False, kenar=0.5)
harita(axs[2], ist, "egitim", "Kadınların ortalama eğitim yılı", "15+ yaş · 2025", nd=1, il_cizgi=False, kenar=0.5)
for ax in axs:
    for _, r in ist[ist.ilce_ad_tuik.isin(["BEŞİKTAŞ", "ESENYURT", "ARNAVUTKÖY", "KADIKÖY", "SULTANBEYLİ", "FATİH"])].iterrows():
        p = r.geometry.representative_point()
        ax.annotate(r.ilce_ad_tuik.title(), (p.x, p.y), fontsize=6.5, ha="center", color=YAZI,
                    bbox=dict(facecolor="white", alpha=0.75, edgecolor="none", pad=0.6))
for uz in ("png", "svg"):
    fig.savefig(HARITA / f"istanbul_ilce_2025.{uz}", facecolor=ZEMIN)
plt.close(fig)

# --- İl içi ilişki: kademeli kontrol --------------------------------------------------
sub = d.dropna(subset=["tdh_ilce", "yukseklik", "egitim", "artis"]).copy()
for c in ["tdh_ilce", "yukseklik", "egitim"]:
    sub[c + "_ic"] = sub[c] - sub.groupby("il")[c].transform("mean")
# eğitim etkisi çıkarılmış artıklar (il içi)
r_t = smf.wls("tdh_ilce_ic ~ egitim_ic", sub, weights=sub.agirlik).fit().resid
r_h = smf.wls("yukseklik_ic ~ egitim_ic", sub, weights=sub.agirlik).fit().resid


def kutular(x, y, w, k=20):
    q = pd.qcut(x.rank(method="first"), k, labels=False)
    return pd.DataFrame({"x": x, "y": y, "w": w, "q": q}).groupby("q").apply(
        lambda t: pd.Series({"x": np.average(t.x, weights=t.w), "y": np.average(t.y, weights=t.w)}))


fig, axs = plt.subplots(1, 2, figsize=(13, 5.6), dpi=150, sharey=True)
fig.subplots_adjust(left=0.07, right=0.98, top=0.78, bottom=0.13, wspace=0.08)
b1 = kutular(sub.yukseklik_ic, sub.tdh_ilce_ic, sub.agirlik)
b2 = kutular(pd.Series(r_h.values, index=sub.index), pd.Series(r_t.values, index=sub.index), sub.agirlik)
for ax, b, ad, alt, x_ad in [
    (axs[0], b1, "Yalnız aynı il içinde", "il ortalamasından sapmalar", "yaşanan bina yüksekliği farkı (m)"),
    (axs[1], b2, "Aynı il içinde + kadın eğitimi sabit", "eğitimin etkisi her iki eksenden çıkarıldı", "yükseklik farkı, eğitimden arındırılmış (m)")]:
    ax.axhline(0, color="#8a8985", lw=1)
    ax.scatter(b.x, b.y, s=42, color=MAVI, edgecolor=ZEMIN, linewidth=1.2, zorder=3)
    eg = np.polyfit(b.x, b.y, 1)
    xx = np.linspace(b.x.min(), b.x.max(), 10)
    ax.plot(xx, np.polyval(eg, xx), color=MAVI, lw=2, zorder=2)
    ax.text(0.98, 0.94, f"eğim: 3 m başına {tr(3 * eg[0], 3)} çocuk", transform=ax.transAxes, ha="right", fontsize=9)
    ax.set_title(ad, loc="left", fontsize=11, fontweight="bold", pad=16)
    ax.text(0, 1.02, alt, transform=ax.transAxes, fontsize=8, color=YAZI_2)
    ax.set_xlabel(x_ad, color=YAZI_2)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.grid(axis="y", color="#e4e2dd", lw=0.6)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
axs[0].set_ylabel("doğurganlık farkı (çocuk/kadın)", color=YAZI_2)
fig.text(0.02, 0.94, "İl içinde daha yüksek binalarda yaşayan ilçeler daha az mı doğuruyor?", fontsize=15, fontweight="bold")
fig.text(0.02, 0.885, "973 ilçe, 20 eşit gruba ayrıldı (15-49 kadın nüfusuyla ağırlıklı ortalamalar). "
         "Sol: ham il içi ilişki. Sağ: kadın eğitimi sabit tutulduğunda kalan ilişki.", fontsize=9, color=YAZI_2)
for uz in ("png", "svg"):
    fig.savefig(GRAFIK / f"ilce_il_ici_yukseklik_egitim.{uz}", facecolor=ZEMIN)
plt.close(fig)
print("ilçe haritaları ve grafikleri yazıldı")
