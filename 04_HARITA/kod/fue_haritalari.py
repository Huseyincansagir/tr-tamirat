"""
Pilot ilçelerde mahalle düzeyinde FUE haritaları
===============================================
Girdi : 03_VERI/islenmis/pilot_mahalleler.gpkg, 05_ANALIZ/sonuclar/fue_ilce_ozet.csv (önce fue_mahalle.py)
Çıktı : 04_HARITA/fue_mahalle_pilotlar.png|svg      10 ilçe, FUE (küçük çoklu harita, ortak sınıflar)
        04_HARITA/fue_erisim_cevre_ciftler.png|svg  Fatih–Silivri ve Kocasinan–Meram: Erişim (E) ve Çevre-ölçek (Ç)
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
IS = KOK / "03_VERI" / "islenmis"
SON = KOK / "05_ANALIZ" / "sonuclar"
HARITA = KOK / "04_HARITA"

MAVI_R = ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"]
TURUNCU_R = ["#fbe3d6", "#f5b392", "#ee8a5c", "#d95926", "#a8400f"]
YAZI, YAZI_2, ZEMIN, GRI = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
SINIF = [0, 35, 45, 55, 65, 100.01]
ETIKET = ["< 35", "35–45", "45–55", "55–65", "≥ 65"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN})


def tr(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def utm(g):
    return 32600 + int((g.unary_union.centroid.x + 180) // 6) + 1


M = gpd.read_file(IS / "pilot_mahalleler.gpkg")
OZ = pd.read_csv(SON / "fue_ilce_ozet.csv").set_index("ilce")
SIRA = ["Fatih", "Silivri", "Başakşehir", "Nilüfer", "Kocasinan", "Meram", "Antakya", "Onikişubat", "Safranbolu", "Beypazarı"]
IL = {"Fatih": "İstanbul", "Silivri": "İstanbul", "Başakşehir": "İstanbul", "Nilüfer": "Bursa", "Kocasinan": "Kayseri",
      "Meram": "Konya", "Antakya": "Hatay", "Onikişubat": "Kahramanmaraş", "Safranbolu": "Karabük", "Beypazarı": "Ankara"}


def panel(ax, ilce, kolon, renkler, baslik=True, alt=None):
    g = M[M.ilce == ilce].copy()
    g = g.to_crs(utm(g))
    k = g[g.kentsel == 1] if g.kentsel.dtype != bool else g[g.kentsel]
    x0, y0, x1, y1 = k.total_bounds
    pad = max(x1 - x0, y1 - y0) * 0.08 + 500
    cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2 + pad
    kentdisi = g[~g.index.isin(k.index)]
    kentdisi.plot(ax=ax, color=GRI, edgecolor="white", linewidth=0.4)
    k.plot(ax=ax, column=kolon, cmap=ListedColormap(renkler), norm=BoundaryNorm(SINIF, len(renkler)),
           edgecolor="white", linewidth=0.5)
    yak = g[g.kaynak.str.startswith("OSM-yer")]
    if len(yak):
        yak.boundary.plot(ax=ax, color=YAZI_2, linewidth=0.8, linestyle=(0, (2, 1.5)))
    ax.set_xlim(cx - r, cx + r)
    ax.set_ylim(cy - r, cy + r)
    ax.set_axis_off()
    # ölçek çubuğu
    uz = 1000 if r < 3000 else 2000 if r < 7000 else 5000
    bx, by = cx - r * 0.92, cy - r * 0.92
    ax.plot([bx, bx + uz], [by, by], color=YAZI, lw=2, solid_capstyle="butt")
    ax.text(bx + uz / 2, by + r * 0.035, f"{uz // 1000} km", ha="center", va="bottom", fontsize=7, color=YAZI_2)
    if baslik:
        ax.set_title(f"{ilce} ({IL[ilce]})", loc="left", fontsize=10.5, fontweight="bold", color=YAZI, pad=16)
    if alt:
        ax.text(0, 1.005, alt, transform=ax.transAxes, fontsize=8, color=YAZI_2, va="bottom")


# --- 1. FUE, 10 ilçe -----------------------------------------------------------------------------------------------
fig, axs = plt.subplots(2, 5, figsize=(17, 8.6))
for ax, ilce in zip(axs.flat, SIRA):
    o = OZ.loc[ilce]
    panel(ax, ilce, "FUE", MAVI_R,
          alt=f"FUE {tr(o.FUE)} · E {tr(o.FUE_E, 0)} · Ç {tr(o.FUE_C, 0)} · {int(o.kentsel)} kentsel mah.")
leg = [Patch(facecolor=c, edgecolor="none", label=l) for c, l in zip(MAVI_R, ETIKET)]
leg += [Patch(facecolor=GRI, edgecolor="none", label="Kentsel olmayan mahalle (endeks dışı)"),
        Patch(facecolor="none", edgecolor=YAZI_2, linestyle=(0, (2, 1.5)), label="Yaklaşık sınır (OSM yer noktası, Voronoi)")]
fig.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, 0.025), ncol=7, frameon=False, fontsize=8.5, title="Fıtrat Uyum Endeksi (0–100, kentsel mahalleler arasında yüzdelik puanların ortalaması)",
           title_fontsize=9)
fig.suptitle("Fıtrat Uyum Endeksi — 10 pilot ilçede mahalle düzeyinde (2025)", x=0.01, ha="left", fontsize=14, fontweight="bold", color=YAZI)
fig.text(0.01, 0.935, "Başlık altındaki değerler kentsel mahallelerin nüfus ağırlıklı ortalaması (E: erişim alt endeksi, Ç: çevre-ölçek alt endeksi). "
         "Her panel kentsel alana yakınlaştırıldı; ölçekler farklı.",
         fontsize=9, color=YAZI_2)
fig.text(0.01, 0.004, "Kaynak: TÜİK ADNKS 2025 (mahalle nüfusu), OpenStreetMap 25.10.2026, TKGM MEGSİS, GHSL R2023A. "
         "Hesaplama: 05_ANALIZ/kod/fue_mahalle.py", fontsize=7.5, color=YAZI_2)
fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.14, wspace=0.06, hspace=0.32)
for uz in ("png", "svg"):
    fig.savefig(HARITA / f"fue_mahalle_pilotlar.{uz}", dpi=200)
plt.close(fig)

# --- 2. Erişim ve çevre-ölçek, iki karşılaştırma çifti ---------------------------------------------------------------
fig, axs = plt.subplots(2, 4, figsize=(15.5, 8.4))
for j, ilce in enumerate(["Fatih", "Silivri", "Kocasinan", "Meram"]):
    o = OZ.loc[ilce]
    panel(axs[0, j], ilce, "FUE_E", MAVI_R, alt=f"Erişim (E) · ortalama {tr(o.FUE_E)}")
    panel(axs[1, j], ilce, "FUE_C", TURUNCU_R, baslik=False, alt=f"Çevre-ölçek (Ç) · ortalama {tr(o.FUE_C)}")
legE = [Patch(facecolor=c, edgecolor="none", label=l) for c, l in zip(MAVI_R, ETIKET)]
legC = [Patch(facecolor=c, edgecolor="none", label=l) for c, l in zip(TURUNCU_R, ETIKET)]
fig.legend(handles=legE, loc="lower left", bbox_to_anchor=(0.02, 0.01), ncol=5, frameon=False, fontsize=8.5,
           title="Erişim: 15 dk temel ihtiyaç, okul, cami, oyun alanı, durak, dükkân, kavşak", title_fontsize=8.5)
fig.legend(handles=legC, loc="lower right", bbox_to_anchor=(0.98, 0.01), ncol=5, frameon=False, fontsize=8.5,
           title="Çevre-ölçek: yeşil alan, az kat, ana yoldan uzaklık, yayılmama, mahalle ölçeği", title_fontsize=8.5)
fig.suptitle("Aynı mahallede erişim ile çevre-ölçek çoğu zaman ters yönde (Spearman ρ = −0,61)", x=0.01, ha="left",
             fontsize=14, fontweight="bold", color=YAZI)
fig.text(0.01, 0.935, "İki doğal karşılaştırma çifti: Fatih–Silivri (aynı kadın eğitimi, farklı biçim) ve Kocasinan–Meram "
         "(Anadolu'nun en dikey ve en yatay merkezleri). Gri: kentsel olmayan mahalle.", fontsize=9, color=YAZI_2)
fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.12, wspace=0.05, hspace=0.18)
for uz in ("png", "svg"):
    fig.savefig(HARITA / f"fue_erisim_cevre_ciftler.{uz}", dpi=200)
plt.close(fig)
print("haritalar yazıldı")
