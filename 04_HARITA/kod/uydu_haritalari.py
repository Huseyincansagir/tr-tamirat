"""
Uydu çevre katmanları — iki karşılaştırma çifti (Fatih–Silivri, Kocasinan–Meram)
=============================================================================
Girdi : 03_VERI/islenmis/uydu/pilot_<ilçe>.tif (uydu_pilot.py), 03_VERI/islenmis/pilot_mahalleler.gpkg (fue_mahalle.py)
Çıktı : 04_HARITA/uydu_ciftler.png|svg   satırlar: ağaç örtüsü (300 m), yaz yüzey sıcaklığı, PM2.5; sütunlar: dört ilçe
"""
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import LinearSegmentedColormap

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
HARITA = KOK / "04_HARITA"
YAZI, YAZI_2, ZEMIN = "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN})
YESIL = LinearSegmentedColormap.from_list("yesil", ["#f3f7f2", "#bfe3cf", "#6cc59b", "#1baf7a", "#0f7a54", "#0b4f37"])
TURUNCU = LinearSegmentedColormap.from_list("turuncu", ["#fbe3d6", "#f5b392", "#ee8a5c", "#d95926", "#a8400f", "#6e2a0a"])
MAVI = LinearSegmentedColormap.from_list("mavi", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281", "#0d366b"])
SATIR = [("agac300", "Ağaç örtüsü, 300 m içinde (%)", YESIL, (0, 60)),
         ("lst", "Yaz gündüz yüzey sıcaklığı (°C, Landsat ortancası)", TURUNCU, (32, 54)),
         ("pm25", "Yıllık PM2.5 (µg/m³, 2022–2024)", MAVI, (12, 30))]
ILCE = ["Fatih", "Silivri", "Kocasinan", "Meram"]
M = gpd.read_file(IS / "pilot_mahalleler.gpkg")

fig, axs = plt.subplots(3, 4, figsize=(15.5, 11.6))
for j, ilce in enumerate(ILCE):
    g = M[M.ilce == ilce]
    k = g[g.kentsel.astype(bool)]
    with rasterio.open(IS / "uydu" / f"pilot_{ilce}.tif") as d:
        bant = {b: d.read(i + 1) for i, b in enumerate(d.descriptions)}
        gk = k.to_crs(d.crs)
        gg = g.to_crs(d.crs)
        x0, y0, x1, y1 = gk.total_bounds
        pad = max(x1 - x0, y1 - y0) * 0.08 + 500
        cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2 + pad
        ext = (d.bounds.left, d.bounds.right, d.bounds.bottom, d.bounds.top)
    for i, (b, baslik, cmap, (vmin, vmax)) in enumerate(SATIR):
        ax = axs[i, j]
        im = ax.imshow(bant[b], extent=ext, cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
        gg.boundary.plot(ax=ax, color="#ffffff", linewidth=0.35, alpha=0.8)
        gk.boundary.plot(ax=ax, color=YAZI, linewidth=0.5)
        ax.set_xlim(cx - r, cx + r)
        ax.set_ylim(cy - r, cy + r)
        ax.set_axis_off()
        uz = 1000 if r < 3000 else 2000 if r < 7000 else 5000
        bx, by = cx - r * 0.92, cy - r * 0.92
        ax.plot([bx, bx + uz], [by, by], color=YAZI, lw=2, solid_capstyle="butt")
        ax.text(bx + uz / 2, by + r * 0.035, f"{uz // 1000} km", ha="center", va="bottom", fontsize=7, color=YAZI)
        ort = np.nanmean(np.where(np.isfinite(bant[b]), bant[b], np.nan)[::5, ::5])
        if i == 0:
            ax.set_title(ilce, loc="left", fontsize=11, fontweight="bold", color=YAZI)
        if j == 3:
            imler = getattr(fig, "_imler", [])
            imler.append((im, baslik))
            fig._imler = imler
fig.suptitle("Uydu çevre katmanları — iki karşılaştırma çifti", x=0.01, ha="left", fontsize=14, fontweight="bold", color=YAZI)
fig.text(0.01, 0.945, "Siyah çizgi: kentsel mahalle sınırı; beyaz: diğer mahalleler. Her satırda aynı renk ölçeği. "
         "Yüzey sıcaklığı hava sıcaklığı değildir: güneşli yaz öğleden önce çatı, asfalt ve toprağın ısısıdır.", fontsize=9, color=YAZI_2)
fig.text(0.01, 0.008, "Kaynak: ESA WorldCover 2021 (10 m); Landsat 8/9 Collection 2 Level-2, 2022–2025 yazları, 14 sahne ortancası "
         "(Microsoft Planetary Computer); ACAG V6.GL.03 PM2.5 (0,01°). Kod: 03_VERI/kod/uydu_pilot.py, 04_HARITA/kod/uydu_haritalari.py",
         fontsize=7.5, color=YAZI_2)
fig.subplots_adjust(left=0.01, right=0.9, top=0.91, bottom=0.04, wspace=0.04, hspace=0.08)
for i, (im, baslik) in enumerate(fig._imler):  # her satıra sağ kenarda kendi renk çubuğu
    p = axs[i, 3].get_position()
    cax = fig.add_axes([0.915, p.y0 + p.height * 0.1, 0.012, p.height * 0.8])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(baslik, fontsize=8.5, color=YAZI_2)
    cb.outline.set_visible(False)
for uz in ("png", "svg"):
    fig.savefig(HARITA / f"uydu_ciftler.{uz}", dpi=170)
print("uydu_ciftler yazıldı")
