"""
Kentsel Stres Yükü haritaları (Faz 4 · Rapor 1)
==============================================
Girdi : 05_ANALIZ/sonuclar/stres_ilce_endeks.csv (stres_endeks.py), 03_VERI/islenmis/ilce_paneli.gpkg (ilçe sınırları, gid)
Çıktı : 04_HARITA/stres_ksy_ilce.png|svg          973 ilçe KSY (beşte birlik dilimler) + İstanbul, Ankara, İzmir
        04_HARITA/stres_bilesenler_ilce.png|svg   yedi bileşenin yüzdelik puanları (küçük çoklu)
        SVG'lerde ilçe ve il sınırı katmanları 150 dpi raster (rasterized=True), yazı ve lejant vektör; dosyalar < 20 MB.
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/stres_harita.py
"""
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
SON = KOK / "05_ANALIZ" / "sonuclar"
HARITA = KOK / "04_HARITA"
YAZI, YAZI_2, ZEMIN = "#0b0b0b", "#52514e", "#fcfcfb"
TURUNCU_R = ["#fbe3d6", "#f5b392", "#ee8a5c", "#d95926", "#a8400f"]  # tek ton, açıktan koyuya
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN})


def tr(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def iyelik(n):
    """Türkçe iyelik eki: 'nüfusun %64'ü', '%2'si', '%8'i' (sayının okunuşunun son sözcüğüne göre)"""
    n = int(round(abs(n)))
    if n == 0:
        return "ı"
    if n % 10:
        return {1: "i", 2: "si", 3: "ü", 4: "ü", 5: "i", 6: "sı", 7: "si", 8: "i", 9: "u"}[n % 10]
    if (n // 10) % 10:
        return {1: "u", 2: "si", 3: "u", 4: "ı", 5: "si", 6: "ı", 7: "i", 8: "i", 9: "ı"}[(n // 10) % 10]
    return "ü" if n % 1000 else "i"


g = gpd.read_file(KOK / "03_VERI" / "islenmis" / "ilce_paneli.gpkg")[["gid", "geometry"]]
d = pd.read_csv(SON / "stres_ilce_endeks.csv")
g = g.merge(d, on="gid").to_crs(LCC)
assert len(g) == 973, len(g)
il_sinir = g.dissolve(by="il").boundary

sinir = list(np.quantile(g.KSY, [0, 0.2, 0.4, 0.6, 0.8, 1.0]))
sinir[0] -= 1e-9
sinir[-1] += 1e-9
cmap, norm = ListedColormap(TURUNCU_R), BoundaryNorm(sinir, 5)


def ciz(ax, gdf, kolon, norm_, il_cizgi=True, kenar=0.12, sinir_gs=None):
    gdf.plot(ax=ax, column=kolon, cmap=cmap, norm=norm_, edgecolor="white", linewidth=kenar, rasterized=True)
    if il_cizgi:
        (sinir_gs if sinir_gs is not None else gpd.GeoSeries(il_sinir)).plot(ax=ax, color="#3d3d3a", linewidth=0.35, rasterized=True)
    ax.set_axis_off()


# --- 1. KSY haritası ----------------------------------------------------------------------------------------------
fig = plt.figure(figsize=(16, 11.2))
fig.text(0.02, 0.962, "Kentsel stres yükü: 973 ilçe", fontsize=19, fontweight="bold", color=YAZI)
fig.text(0.02, 0.936, "Yedi ölçülebilen etkenin yüzdelik puan ortalaması (0–100; yüksek = daha çok yük): PM2.5, yaz yüzey sıcaklığı, "
         "ana yol yakınlığı, yapılı alan payı, ağaç ve yeşil eksikliği, bina yüksekliği, yaşanan yoğunluk. Hepsi nüfus ağırlıklı.",
         fontsize=9.5, color=YAZI_2)
ax = fig.add_axes([0.01, 0.30, 0.98, 0.62])
ciz(ax, g, "KSY", norm)
nuf = g.groupby("KSY_dilim").nufus_2025.sum() / g.nufus_2025.sum() * 100
eti = [Patch(facecolor=TURUNCU_R[i], edgecolor="#bbb", lw=0.3,
             label=f"{tr(max(sinir[i], g.KSY.min()))} – {tr(min(sinir[i + 1], g.KSY.max()))}  ·  nüfusun %{tr(nuf.loc[i + 1], 0)}'{iyelik(nuf.loc[i + 1])}")
       for i in range(5)]
ax.legend(handles=eti, loc="lower left", bbox_to_anchor=(0.0, 0.0), frameon=False, fontsize=8.5, title="Beşte birlik dilim (ilçe sayısı eşit)",
          title_fontsize=8.5, alignment="left")
METRO = [("İstanbul", "İstanbul (39 ilçe)"), ("Ankara", "Ankara (25 ilçe)"), ("İzmir", "İzmir (30 ilçe)")]
for i, (il_ad, baslik) in enumerate(METRO):
    a = fig.add_axes([0.02 + i * 0.325, 0.045, 0.31, 0.235])
    gi = g[g.il == il_ad]
    ciz(a, gi, "KSY", norm, il_cizgi=False, kenar=0.4)
    a.set_title(baslik, loc="left", fontsize=10.5, fontweight="bold", color=YAZI, pad=14)
    # en yüksek ve en düşük ilçe: haritada nokta ve puan, adları başlığın altında
    ust, alt = gi.nlargest(1, "KSY").iloc[0], gi.nsmallest(1, "KSY").iloc[0]

    def kisa(s):
        s = s.replace(il_ad.upper() + " ", "")
        return s[0] + s[1:].replace("I", "ı").replace("İ", "i").lower()  # Türkçe küçük harf

    for r in (ust, alt):
        c = r.geometry.representative_point()
        a.plot(c.x, c.y, "o", ms=4, color=YAZI, mec="white", mew=0.6)
        a.annotate(tr(r.KSY, 0), (c.x, c.y), xytext=(4, 3), textcoords="offset points", fontsize=8, fontweight="bold",
                   color=YAZI, bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
    a.text(0, 1.0, f"en yüksek {kisa(ust.ilce_ad_tuik)} {tr(ust.KSY, 0)} · en düşük {kisa(alt.ilce_ad_tuik)} {tr(alt.KSY, 0)}",
           transform=a.transAxes, fontsize=8, color=YAZI_2, va="bottom")
fig.text(0.02, 0.012, "Kaynak: ACAG V6.GL.03 PM2.5 (2022–2024); MODIS MYD11A2 (Temmuz–Ağustos 2023–2024); ESA WorldCover 2021; GHSL R2023A "
         "(bina yüksekliği 2018, nüfus 2020); OpenStreetMap ana yollar (2025). İlçe sınırları geoBoundaries ADM2. "
         "Kod: 05_ANALIZ/kod/stres_endeks.py, stres_harita.py", fontsize=7.5, color=YAZI_2)
for uz in ("png", "svg"):
    fig.savefig(HARITA / f"stres_ksy_ilce.{uz}", dpi=150, facecolor=ZEMIN)
plt.close(fig)
print("stres_ksy_ilce yazıldı")

# --- 2. bileşenler -----------------------------------------------------------------------------------------------
PM_ORT = np.average(g.pm25, weights=g.nufus_2025)
BIL = [("s_pm25", "PM2.5", f"ACAG 2022–2024 · nüfus ağırlıklı ort. {tr(PM_ORT)} µg/m³"), ("s_isi", "Yaz yüzey sıcaklığı", "MODIS 2023–2024"),
       ("s_anayol", "Ana yol yakınlığı", "ana yola 100 m içindeki nüfus payı"), ("s_yapili", "Yapılı alan payı", "300 m çevrede"),
       ("s_yesilsiz", "Ağaç ve yeşil eksikliği", "300 m çevrede ağaç ve yeşil örtü"), ("s_yukseklik", "Bina yüksekliği",
                                                                                     "yaşanan, GHSL 2018"),
       ("s_yogunluk", "Yaşanan yoğunluk", "kişi/ha, GHSL 2020")]
norm_y = BoundaryNorm([-1e-9, 20, 40, 60, 80, 100.01], 5)
fig, axs = plt.subplots(2, 4, figsize=(16, 5.0))
fig.subplots_adjust(left=0.01, right=0.99, top=0.80, bottom=0.02, wspace=0.03, hspace=0.30)
fig.text(0.01, 0.94, "Kentsel stres yükünün yedi bileşeni", fontsize=17, fontweight="bold", color=YAZI)
fig.text(0.01, 0.885, "İlçeler arası yüzdelik puan (0–100; koyu = Türkiye'deki ilçelerin çoğundan daha yüklü). "
         "Ağaç ve yeşil eksikliği iki uydu göstergesinin ortalaması.", fontsize=9.5, color=YAZI_2)
for ax, (k, ad, alt) in zip(axs.flat, BIL):
    g.plot(ax=ax, column=k, cmap=cmap, norm=norm_y, edgecolor="white", linewidth=0.05, rasterized=True)
    gpd.GeoSeries(il_sinir).plot(ax=ax, color="#3d3d3a", linewidth=0.2, rasterized=True)
    ax.set_axis_off()
    ax.set_title(ad, loc="left", fontsize=11, fontweight="bold", color=YAZI, pad=10)
    ax.text(0, 1.0, alt, transform=ax.transAxes, fontsize=7.5, color=YAZI_2, va="bottom")
son = axs.flat[-1]
son.set_axis_off()
son.legend(handles=[Patch(facecolor=TURUNCU_R[i], edgecolor="#bbb", lw=0.3, label=f"{i * 20}–{(i + 1) * 20}. yüzdelik")
                    for i in range(5)], loc="upper left", bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=9, title="Yüzdelik puan",
            title_fontsize=9, alignment="left")
son.text(0.0, 0.0, "Kaynak: stres_ilce_endeks.csv\nKod: 05_ANALIZ/kod/stres_harita.py", transform=son.transAxes, fontsize=7.5,
         color=YAZI_2)
for uz in ("png", "svg"):
    fig.savefig(HARITA / f"stres_bilesenler_ilce.{uz}", dpi=150, facecolor=ZEMIN)
plt.close(fig)
print("stres_bilesenler_ilce yazıldı")
