"""
Ölçeklenebilir şehir — kademe şeması (semt, şehir, bölge)
=========================================================
Model mahalle (≈7.000 kişi, 60 ha, 800 × 750 m) temel birimdir. Kademeler aynı ilkeyle büyür:
  semt   : 5 mahalle + semt merkezi, toplu taşıma omurgası üzerinde ("inci dizisi"); ≈35 bin kişi; 15 dk yürüme
  şehir  : 6 semt, iki raylı hat kesişiminde şehir merkezi, semtler arasında yeşil kamalar; ≈210 bin kişi
  bölge  : 5 şehir + bölge merkezi, bölgesel tren halkası; ≈1,3 milyon kişi
Çizim şematiktir; yer seçimi değildir. Ölçek çubukları yaklaşık boyutu gösterir.
Çıktı : 07_TASARIM_CIZIM/olceklenebilir_sehir/kademe_semasi.png|svg
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch, Patch, Rectangle, Wedge

sys.stdout.reconfigure(encoding="utf-8")
CIK = Path(__file__).resolve().parents[1]
YAZI, YAZI_2, ZEMIN = "#0b0b0b", "#52514e", "#fcfcfb"
KONUT, MERKEZ, YESIL, SANAYI, RAY, TARIM, ENERJI = "#cde2fb", "#eb6834", "#bfe3cf", "#eda100", "#0b0b0b", "#f3efe2", "#1baf7a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN})


def mahalle(ax, x, y, w=0.8, h=0.75, yaricap=True):
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc=KONUT, ec="#3987e5", lw=0.6))
    ax.add_patch(Rectangle((x - 0.07, y - 0.07), 0.14, 0.14, fc="#256abf", ec="none"))  # mahalle merkezi
    if yaricap:
        ax.add_patch(Circle((x, y), 0.4, fc="none", ec="#256abf", lw=0.5, ls=(0, (2, 2))))


def olcek(ax, x, y, uz, etiket):
    ax.plot([x, x + uz], [y, y], color=YAZI, lw=2, solid_capstyle="butt")
    ax.text(x + uz / 2, y + uz * 0.08, etiket, ha="center", va="bottom", fontsize=7.5, color=YAZI)


fig, axs = plt.subplots(1, 3, figsize=(17, 6.8), gridspec_kw={"width_ratios": [1, 1.15, 1.15]})

# --- A. semt ---------------------------------------------------------------------------------------------------
ax = axs[0]
ax.add_patch(Rectangle((-2.2, -1.9), 4.4, 3.8, fc=YESIL, ec="none", alpha=0.45))
ax.plot([-2.2, 2.2], [0, 0], color=RAY, lw=2.2)
for x in (-1.5, 0, 1.5):
    ax.plot(x, 0, "o", ms=7, mfc=ZEMIN, mec=RAY, mew=1.6)
for x, y in [(-1.0, 0.85), (0.0, 0.95), (1.0, 0.85), (-0.95, -0.9), (0.95, -0.9)]:
    mahalle(ax, x, y)
ax.add_patch(FancyBboxPatch((-0.35, -0.75), 0.7, 0.6, boxstyle="round,pad=0.02", fc=MERKEZ, ec="none"))
ax.text(0, -0.45, "semt\nmerkezi", ha="center", va="center", fontsize=7.5, color="white")
ax.add_patch(Circle((0, 0), 1.25, fc="none", ec=MERKEZ, lw=0.8, ls=(0, (4, 3))))
olcek(ax, -2.0, -1.75, 1.0, "1 km")
ax.set_xlim(-2.3, 2.3)
ax.set_ylim(-1.95, 1.95)
ax.set_title("A · Semt  ≈ 35 bin kişi", loc="left", fontsize=11, fontweight="bold", color=YAZI)
ax.text(-2.25, 1.75, "5 mahalle + semt merkezi\nlise, cuma camii, haftalık pazar,\nsemt sağlık merkezi, kütüphane, spor",
        fontsize=7.8, color=YAZI_2, va="top")

# --- B. şehir ---------------------------------------------------------------------------------------------------
ax = axs[1]
ax.add_patch(Rectangle((-9, -8), 18, 16, fc=TARIM, ec="none"))
ax.add_patch(Circle((0, 0), 6.6, fc=ZEMIN, ec="none"))
for a0 in (30, 90, 150, 210, 270, 330):  # yeşil kamalar
    ax.add_patch(Wedge((0, 0), 6.6, a0 - 7, a0 + 7, width=5.0, fc=YESIL, ec="none"))
import math

for i, a in enumerate((0, 60, 120, 180, 240, 300)):
    r = 4.0
    cx, cy = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
    ax.add_patch(Circle((cx, cy), 1.45, fc=KONUT, ec="#3987e5", lw=0.6))
    ax.add_patch(Circle((cx, cy), 0.35, fc=MERKEZ, ec="none"))
ax.plot([-7.5, 7.5], [0, 0], color=RAY, lw=2.2)
ax.plot([-3.75, 3.75], [-6.5, 6.5], color=RAY, lw=2.2)
ax.add_patch(Circle((0, 0), 0.9, fc=MERKEZ, ec="white", lw=1))
ax.text(0, 0, "şehir\nmerkezi", ha="center", va="center", fontsize=7, color="white")
ax.add_patch(FancyBboxPatch((6.9, -3.3), 1.8, 1.6, boxstyle="round,pad=0.05", fc=SANAYI, ec="none"))
ax.text(7.8, -2.5, "OSB", ha="center", va="center", fontsize=8, color=YAZI)
ax.plot([5.2, 6.9], [0, -2.0], color=RAY, lw=1.2, ls=(0, (3, 2)))
ax.add_patch(FancyBboxPatch((-8.7, 3.6), 2.4, 1.6, boxstyle="round,pad=0.05", fc=ENERJI, ec="none"))
ax.text(-7.5, 4.4, "güneş ve\nrüzgâr", ha="center", va="center", fontsize=7.5, color="white")
olcek(ax, -8.6, -7.6, 5, "5 km")
ax.set_xlim(-9, 9)
ax.set_ylim(-8, 8)
ax.set_title("B · Şehir  ≈ 210 bin kişi", loc="left", fontsize=11, fontweight="bold", color=YAZI)
ax.text(-8.8, 7.75, "6 semt, iki raylı hat, yeşil kamalar, tarım kuşağı;\nOSB hâkim rüzgârın alt yönünde, yük treniyle",
        fontsize=7.8, color=YAZI_2, va="top")

# --- C. bölge ---------------------------------------------------------------------------------------------------
ax = axs[2]
ax.add_patch(Rectangle((-60, -50), 120, 100, fc=TARIM, ec="none"))
sehirler = [(0, 0, 7.5)] + [(32 * math.cos(math.radians(a)), 32 * math.sin(math.radians(a)), 5.5) for a in (18, 90, 162, 234, 306)]
xs = [s[0] for s in sehirler[1:]] + [sehirler[1][0]]
ys = [s[1] for s in sehirler[1:]] + [sehirler[1][1]]
ax.plot(xs, ys, color=RAY, lw=2)
for s in sehirler[1:]:
    ax.plot([0, s[0]], [0, s[1]], color=RAY, lw=1.2, ls=(0, (3, 2)))
for i, (x, y, r) in enumerate(sehirler):
    ax.add_patch(Circle((x, y), r, fc=MERKEZ if i == 0 else KONUT, ec="#3987e5" if i else "white", lw=0.8))
ax.add_patch(Rectangle((-58, 30), 22, 14, fc=YESIL, ec="none"))
ax.text(-47, 37, "orman ve\nkoruma alanı", ha="center", va="center", fontsize=7.5, color=YAZI)
ax.plot([-58, 58], [-39, -36], color="#b8312f", lw=1.2, ls=(0, (6, 3)))
ax.text(30, -35.2, "diri fay (tampon)", fontsize=7.5, color="#b8312f")
ax.add_patch(FancyBboxPatch((44, 30), 12, 9, boxstyle="round,pad=0.5", fc=SANAYI, ec="none"))
ax.text(50, 34.5, "liman ve\nhavalimanı", ha="center", va="center", fontsize=7.2, color=YAZI)
olcek(ax, -57, -47, 20, "20 km")
ax.set_xlim(-60, 60)
ax.set_ylim(-50, 50)
ax.set_title("C · Bölge  ≈ 1,3 milyon kişi", loc="left", fontsize=11, fontweight="bold", color=YAZI)
ax.text(-58, 48.5, "5 şehir + bölge merkezi, bölgesel tren halkası;\nfay, orman ve tarım arazisi korunur", fontsize=7.8,
        color=YAZI_2, va="top")

for ax in axs:
    ax.set_aspect("equal")
    ax.set_axis_off()
leg = [Patch(fc=KONUT, ec="#3987e5", label="Konut ağırlıklı doku (mahalle, semt, şehir)"),
       Patch(fc=MERKEZ, label="Merkez (semt, şehir, bölge)"), Patch(fc=YESIL, label="Yeşil kama, park, orman"),
       Patch(fc=TARIM, label="Tarım kuşağı"), Patch(fc=SANAYI, label="Sanayi, liman, havalimanı"),
       Patch(fc=ENERJI, label="Yenilenebilir enerji alanı"),
       Line2D([], [], color=RAY, lw=2, label="Raylı sistem (kesikli: yük ya da bağlantı)"),
       Line2D([], [], color="#256abf", lw=0.8, ls=(0, (2, 2)), label="400 m yürüme yarıçapı (mahalle)"),
       Line2D([], [], color=MERKEZ, lw=0.8, ls=(0, (4, 3)), label="1,25 km, 15 dk (semt)")]
fig.legend(handles=leg, loc="lower center", ncol=5, frameon=False, fontsize=8.2)
fig.suptitle("Ölçeklenebilir şehir: aynı ilke, beş kademe (komşuluk birimi → mahalle → semt → şehir → bölge)", x=0.01,
             ha="left", fontsize=13.5, fontweight="bold", color=YAZI)
fig.text(0.01, 0.905, "Temel birim model mahalle v2.1 (≈7.000 kişi, 60 ha). Şema kavramsaldır; ölçek çubukları yaklaşık boyuttur.",
         fontsize=9, color=YAZI_2)
fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.13, wspace=0.06)
for uz in ("png", "svg"):
    fig.savefig(CIK / f"kademe_semasi.{uz}", dpi=180)
print("kademe_semasi yazıldı")
