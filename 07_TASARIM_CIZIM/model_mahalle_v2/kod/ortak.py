"""
Ortak sabitler, renkler ve çizim yardımcıları (model mahalle v2)
================================================================
Model mahalle v2 çizimlerinin hepsi bu modülü kullanır (v1'den kopyalandı; değişenler
"v2:" diye işaretli). Renk dili
07_TASARIM_CIZIM/kod/ayni_yogunluk_uc_bicim.py ile aynıdır; yalnızca donatı
ve konut tipleri için yeni tonlar eklenmiştir.
"""

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe
from matplotlib.patches import Circle, FancyArrow, Polygon as MplPolygon, Rectangle

KOD = Path(__file__).resolve().parent
CIKTI = KOD.parent                      # 07_TASARIM_CIZIM/model_mahalle_v2
V1_KOD = KOD.parent.parent / "model_mahalle" / "kod"   # v1 kodu (yalnız okunur; karşılaştırma için)
SURUM = "v2"
TASARIM = CIKTI.parent                  # 07_TASARIM_CIZIM

# --- Güneş (İstanbul 41°K) ---------------------------------------------------
ENLEM = 41.0
EGIM = 23.44
ARALIK_ACI = 90 - ENLEM - EGIM          # 21 Aralık öğle güneş yüksekliği ≈ 25,6°
MART_ACI = 90 - ENLEM                   # 21 Mart öğle güneş yüksekliği = 49,0°


def golge(h, aci):
    """h yüksekliğindeki saçağın düz zemine düşürdüğü gölge boyu (m)."""
    return h / math.tan(math.radians(aci))


# --- Varsayımlar --------------------------------------------------------------
HANE_BUYUKLUGU = 3.2          # kişi/hane (tasarim_parametreleri.md §9.2; TÜİK ile kalibre edilmeli)
KAT_YUK = 3.1                 # m, konut katı (döşemeden döşemeye; v1: 3,0). v2: 2,80 m net tavan; derin planlarda
                              # gün ışığı; S1 ve S2 H/W hedefine katkı. PAİY md. 28 üst sınırı 3,60 m [D]
ZEMIN_TICARI_YUK = 4.5        # m, ticari zemin kat

# --- Renkler: ayni_yogunluk_uc_bicim.py ile ortak olanlar ---------------------
R_SOKAK = "#d9d6d0"
R_ZEMIN = "#f4f1ea"
R_BINA = "#5b4a3f"
R_BINA_ARKA = "#b9aca2"
R_TICARI = "#e07b00"
R_ORTAK_YESIL = "#a9cf8f"
R_OZEL_AVLU = "#d6ebc4"
R_AGAC = "#5e9444"
R_OTOPARK = "#c4c4c4"
R_GOLGE = "#7d8fb3"
R_GUNES = "#e0a100"

# --- Yeni tonlar (aynı aile) ---------------------------------------------------
R_TOPLAYICI = "#bdb8ae"       # mahalle dışı toplayıcı yol
R_CADDE = "#cbc6bc"           # S1 mahalle caddesi
R_S2 = "#e3dfd6"              # S2 yaşam sokağı (paylaşımlı yüzey)
R_S3 = "#efe6d2"              # S3 yaya yolu, diyagonal
R_MEYDAN = "#ead9b8"          # meydan ve çarşı yaya yüzeyi
R_DIS = "#ebe8e1"             # alan dışı
R_ORTAK_AVLU = "#c3dfa9"      # avlu grubu ortak avlusu, ada içi ortak bahçe
R_SPOR = "#9cc59a"
R_BOSTAN = "#d9e6b0"
R_SU = "#4f8fc0"

# Konut tipleri (bina rengi: açık → koyu = alçak → yüksek)
TIP_RENK = {
    "T1": "#c4946a",   # büyüyebilen sıra ev (Z+1 → Z+2)
    "T2": "#9c6446",   # avlulu çok kuşaklı sıra ev (Z+2)
    "T3": "#6e4c3b",   # avlu grubu (Z+2 / Z+3)
    "T4": "#3f322b",   # çevre adası (Z+3, köşe Z+4), zeminde dükkân
}
TIP_AD = {
    "T1": "T1 Büyüyebilen sıra ev",
    "T2": "T2 Avlulu çok kuşaklı ev",
    "T3": "T3 Avlu grubu",
    "T4": "T4 Çevre adası (zeminde dükkân)",
}

# Donatılar: (bina rengi, arsa rengi)
DONATI_RENK = {
    "egitim": ("#4f73a3", "#dde6f1"),
    "ibadet": ("#2f6f66", "#d6e9e4"),
    "saglik": ("#b0483f", "#f2dad6"),
    "sosyal": ("#7d5384", "#ebdff0"),
    "carsi": ("#c46a00", "#f8e2c6"),
    "otopark": ("#8a8a8a", "#dcdcdc"),
    "teknik": ("#9a9a9a", "#e4e4e4"),
}

# Erişim haritaları: tek tonlu ardışık mavi rampa (dataviz başvuru paleti, ordinal adımlar)
MESAFE_SINIR = [0, 100, 200, 300, 400, 500, 650, 10_000]
MESAFE_RENK = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
R_ASIM = "#d03b3b"            # hedef aşımı (durum: kritik) — her zaman etiketle birlikte


# --- Biçim ---------------------------------------------------------------------
def tr(metin):
    """1,234.5 -> 1.234,5 (Türkçe sayı biçimi)."""
    return str(metin).replace(",", "§").replace(".", ",").replace("§", ".")


def sayi(v, ond=0):
    """Türkçe biçimde sayı (binlik ayraç nokta, ondalık virgül)."""
    return tr(f"{v:,.{ond}f}")


def yuzde(v, ond=0):
    return "%" + sayi(v, ond)


HALO = [pe.withStroke(linewidth=2.6, foreground="white")]
HALO_INCE = [pe.withStroke(linewidth=1.6, foreground="white")]


# --- Çizim yardımcıları ---------------------------------------------------------
def poligon_ciz(ax, geom, fc, ec="none", lw=0.0, zorder=1, alpha=1.0, hatch=None, ls="-"):
    """Shapely Polygon / MultiPolygon çizer (delikler beyaz değil, gerçek delik)."""
    from matplotlib.path import Path as MPath
    from matplotlib.patches import PathPatch

    if geom is None or geom.is_empty:
        return
    parcalar = [geom] if geom.geom_type == "Polygon" else [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon"]
    for p in parcalar:
        verts, codes = [], []
        for halka in [p.exterior] + list(p.interiors):
            xy = list(halka.coords)
            verts += xy
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY]
        patch = PathPatch(MPath(verts, codes), fc=fc, ec=ec, lw=lw, zorder=zorder, alpha=alpha,
                          hatch=hatch, ls=ls)
        ax.add_patch(patch)


def agac(ax, x, y, r=2.2, zorder=6, alpha=0.9):
    ax.add_patch(Circle((x, y), r, fc=R_AGAC, ec="white", lw=0.3, alpha=alpha, zorder=zorder))


def kuzey_oku(ax, x, y, boy=30, yazi=9):
    ax.annotate("", xy=(x, y + boy), xytext=(x, y),
                arrowprops=dict(arrowstyle="-|>", color="#222", lw=1.4, mutation_scale=16), zorder=30)
    ax.text(x, y - boy * 0.35, "K", ha="center", va="center", fontsize=yazi, fontweight="bold", zorder=30)


def olcek_cubugu(ax, x, y, adim=50, n=4, h=5, yazi=7.5, birim="m"):
    """Siyah-beyaz dönüşümlü ölçek çubuğu."""
    for i in range(n):
        ax.add_patch(Rectangle((x + i * adim, y), adim, h, fc="#222" if i % 2 == 0 else "white",
                               ec="#222", lw=0.6, zorder=30))
    for i in range(n + 1):
        etiket = f"{i * adim:g}" + (f" {birim}" if i == n else "")
        ax.text(x + i * adim, y - h * 0.9, etiket, ha="center", va="top", fontsize=yazi, zorder=30)


def insan(ax, x, z=0.0, boy=1.75, renk="#333", zorder=8, cocuk=False):
    """Kesitler için basit insan figürü (ölçekli)."""
    if cocuk:
        boy = 1.2
    bas = boy * 0.13
    ax.add_patch(Circle((x, z + boy - bas), bas, fc=renk, ec="none", zorder=zorder))
    ax.add_patch(Rectangle((x - boy * 0.09, z + boy * 0.45), boy * 0.18, boy * 0.30, fc=renk, ec="none", zorder=zorder))
    ax.plot([x - boy * 0.05, x - boy * 0.07], [z + boy * 0.46, z], color=renk, lw=1.2, zorder=zorder, solid_capstyle="round")
    ax.plot([x + boy * 0.05, x + boy * 0.07], [z + boy * 0.46, z], color=renk, lw=1.2, zorder=zorder, solid_capstyle="round")


def kesit_agac(ax, x, z=0.0, govde=2.6, tac_r=2.6, renk=R_AGAC, zorder=7):
    """Kesitte ağaç: gövde + taç (olgun, ≈15–20 yıl)."""
    ax.plot([x, x], [z, z + govde + tac_r * 0.6], color="#6b5a45", lw=1.6, zorder=zorder)
    ax.add_patch(Circle((x, z + govde + tac_r), tac_r, fc=renk, ec="white", lw=0.4, alpha=0.85, zorder=zorder + 0.1))


def olcu_cizgisi(ax, x0, x1, y, metin, yazi=7, renk="#333", ust=True, zorder=20):
    """Yatay ölçü çizgisi (oklu) ve metni."""
    ax.annotate("", xy=(x0, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="<->", color=renk, lw=0.6, shrinkA=0, shrinkB=0), zorder=zorder)
    ax.plot([x0, x0], [y - 0.25, y + 0.25], color=renk, lw=0.6, zorder=zorder)
    ax.plot([x1, x1], [y - 0.25, y + 0.25], color=renk, lw=0.6, zorder=zorder)
    ax.text((x0 + x1) / 2, y + (0.15 if ust else -0.15), metin, ha="center", va="bottom" if ust else "top",
            fontsize=yazi, color=renk, zorder=zorder)
