"""
Model mahalle v2.1 — konut tipolojileri (plan + kesit + alan tablosu)
==================================================================
v2: PAİY md. 34/1 (RG 01.07.2026) asansör kuralı işlendi — T1'de kaldırma platformu yeri (zorunlu değil, tek BB),
T2'de asansör (platform) yeri, T3 Z+2'de iki çekirdekte asansör yeri / Z+3'te asansör, T4'te asansör. Alan ve
maliyet etkisi alan tablolarında (maliyet varsayımları tipoloji_verisi.py, [V]). Kat yüksekliği 3,1 m; ön eşik 1,5 m.
T1 büyüyebilen sıra ev · T2 avlulu çok kuşaklı ev · T3 avlu grubu · T4 çevre adası
(zeminde dükkân). Parsel ve bina ölçüleri plan_modeli.py ile aynıdır; oda alanları
aşağıdaki dikdörtgenlerden hesaplanır (net, duvar içi). Planlar şematiktir: duvar,
oda, merdiven ve giriş gösterilir; kapı-pencere ayrıntısı yoktur.

Çalıştırma:  python konut_tipolojileri.py
Çıktılar  :  ../tipoloji_T1_buyuyebilen_ev.png|svg, ../tipoloji_T2_cok_kusakli_ev.png|svg,
             ../tipoloji_T3_avlu_grubu.png|svg, ../tipoloji_T4_cevre_adasi.png|svg
"""

import math
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon as MPoly, Rectangle

import metrikler as mt
import plan_modeli as pm
import tipoloji_verisi as tv
from ortak import (ARALIK_ACI, CIKTI, KAT_YUK, MART_ACI, R_AGAC, R_GOLGE, R_GUNES, R_ORTAK_AVLU, R_OZEL_AVLU, R_S2,
                   R_TICARI, TIP_RENK, ZEMIN_TICARI_YUK, golge, insan, kesit_agac, olcek_cubugu, sayi)

DUVAR = "#3b322c"
ODA = {"yasam": "#f6efe3", "yatak": "#eef2f7", "islak": "#e3eef3", "dolasim": "#f3f1ec", "merdiven": "#e6e1d8",
       "ticari": "#fbe3c6", "ortak": "#eef0e4", "esnek": "#f1e6f2", "asansor": "#cfdbe8"}
M = mt.metrikleri_hesapla()


def _mtl(x):
    return f"{sayi(x / 1e6, 2)} milyon TL"


def oda_turu(ad):
    a = ad.lower()
    if any(k in a for k in ("platform", "asansör")):
        return "asansor"
    if any(k in a for k in ("yatak", "büyükler", "çalışma")):
        return "yatak"
    if any(k in a for k in ("banyo", "wc", "duş", "çamaşır")):
        return "islak"
    if any(k in a for k in ("hol", "giriş", "dolap", "kiler", "geçit", "çekirdek")):
        return "dolasim"
    if "merdiven" in a:
        return "merdiven"
    if "dükkân" in a:
        return "ticari"
    if any(k in a for k in ("ortak", "bisiklet")):
        return "ortak"
    if "esnek" in a:
        return "esnek"
    return "yasam"


def alan(rects):
    return sum((x1 - x0) * (y1 - y0) for x0, y0, x1, y1 in rects)


def plan_ciz(ax, ox, oy, dis_gen, dis_der, odalar, duvar=0.2, kesik=False, yazi=6.8, m2=True, etiket_min=1.5):
    """Dış ölçüler dis_gen × dis_der; odalar iç koordinatta (duvar içi, köken iç GB köşe)."""
    ls = (0, (3, 2)) if kesik else "-"
    ax.add_patch(Rectangle((ox, oy), dis_gen, dis_der, fc=DUVAR if not kesik else "none", ec=DUVAR, lw=1.0, ls=ls,
                           zorder=2))
    toplam = 0.0
    from shapely.geometry import box as sbox
    from shapely.ops import unary_union
    from ortak import poligon_ciz
    for ad, rects in odalar:
        tur = oda_turu(ad)
        g = unary_union([sbox(ox + duvar + x0, oy + duvar + y0, ox + duvar + x1, oy + duvar + y1) for x0, y0, x1, y1 in rects])
        poligon_ciz(ax, g.buffer(-0.05, join_style="mitre"), ODA[tur], zorder=3)
        if tur == "merdiven":
            x0, y0, x1, y1 = rects[0]
            n = int((y1 - y0) / 0.28) if (y1 - y0) > (x1 - x0) else int((x1 - x0) / 0.28)
            for k in range(1, n):
                if (y1 - y0) > (x1 - x0):
                    yy = oy + duvar + y0 + k * 0.28
                    ax.plot([ox + duvar + x0 + 0.1, ox + duvar + x1 - 0.1], [yy, yy], color="#8d8478", lw=0.4, zorder=4)
                else:
                    xx = ox + duvar + x0 + k * 0.28
                    ax.plot([xx, xx], [oy + duvar + y0 + 0.1, oy + duvar + y1 - 0.1], color="#8d8478", lw=0.4, zorder=4)
        a = alan(rects)
        toplam += a
        en = max(rects, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
        cx = ox + duvar + (en[0] + en[2]) / 2
        cy = oy + duvar + (en[1] + en[3]) / 2
        dar = (en[2] - en[0]) < 1.7
        if a >= etiket_min and tur != "merdiven":
            ax.text(cx, cy, (f"{ad} · {sayi(a, 1)} m²" if dar else f"{ad}\n{sayi(a, 1)} m²") if m2 else ad,
                    ha="center", va="center", fontsize=yazi - (1.0 if dar else 0), color="#2c2622", zorder=5,
                    linespacing=1.05, rotation=90 if dar else 0)
        elif tur == "merdiven":
            ax.text(cx, cy, "merd.", ha="center", va="center", fontsize=yazi - 1, color="#555", rotation=90, zorder=5)
    if kesik:
        ax.add_patch(Rectangle((ox, oy), dis_gen, dis_der, fc="none", ec=DUVAR, lw=1.0, ls=ls, zorder=6))
    return toplam


def tablo(ax, basliklar, satirlar, x_sut, baslik=None, yazi=8.3, kalin_son=True):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    y = 0.97
    if baslik:
        ax.text(0, y, baslik, fontsize=10.5, fontweight="bold", va="top")
        y -= 0.09
    h = min(0.075, (y - 0.02) / (len(satirlar) + 1.2))
    for xs, b in zip(x_sut, basliklar):
        ax.text(xs, y, b, fontsize=yazi, fontweight="bold", va="top")
    y -= h * 1.1
    ax.plot([0, 1], [y + h * 0.15] * 2, color="#333", lw=0.8)
    for k, sat in enumerate(satirlar):
        if k % 2 == 0:
            ax.add_patch(Rectangle((0, y - h * 0.85), 1, h, fc="#f3f1ec", ec="none"))
        kalin = kalin_son and k == len(satirlar) - 1
        for xs, v in zip(x_sut, sat):
            ax.text(xs, y - h * 0.35, v, fontsize=yazi, va="center", fontweight="bold" if kalin else "normal")
        y -= h


def eksen(ax, xlim, ylim, baslik=None):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    if baslik:
        ax.set_title(baslik, fontsize=10.5, fontweight="bold", loc="left", pad=4)


def sokak_bandi(ax, x0, x1, y0, y1, metin="SOKAK"):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=R_S2, ec="none", zorder=1))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, metin, ha="center", va="center", fontsize=7.5, color="#6a655d", zorder=2)


def baslik_yaz(fig, baslik, alt):
    fig.text(0.03, 0.965, baslik, fontsize=22, fontweight="bold")
    fig.text(0.03, 0.940, alt, fontsize=11, color="#444")


def kesit_bina(ax, x0, x1, katlar, renk_ic="#f3eee6", cati="duz", ticari=False, kesik_ust=0, golge_isini=False):
    """Kesitte bina: katlar = kat adedi; ticari: zemin 4,5 m."""
    z = 0.0
    yuk = [ZEMIN_TICARI_YUK if ticari else KAT_YUK] + [KAT_YUK] * (katlar - 1)
    H = sum(yuk)
    ax.add_patch(Rectangle((x0, 0), x1 - x0, H, fc=renk_ic, ec="none", zorder=3))
    for k, kh in enumerate(yuk):
        ax.add_patch(Rectangle((x0, z), x1 - x0, 0.25, fc=DUVAR, ec="none", zorder=4))
        z += kh
    ax.add_patch(Rectangle((x0, H - 0.25), x1 - x0, 0.25, fc=DUVAR, ec="none", zorder=4))
    for xw in (x0, x1 - 0.25):
        ax.add_patch(Rectangle((xw, 0), 0.25, H, fc=DUVAR, ec="none", zorder=4))
    if ticari:
        ax.add_patch(Rectangle((x0, 0), x1 - x0, ZEMIN_TICARI_YUK, fc="none", ec=R_TICARI, lw=1.5, zorder=5))
    if cati == "egik":
        ax.add_patch(MPoly([(x0 - 0.4, H), (x1 + 0.4, H), ((x0 + x1) / 2, H + (x1 - x0) / 2 * math.tan(math.radians(30)))],
                           closed=True, fc="#9a5b3c", ec="none", zorder=4))
    else:
        for xw in (x0, x1 - 0.25):
            ax.add_patch(Rectangle((xw, H), 0.25, 0.9, fc=DUVAR, ec="none", zorder=4))
    if kesik_ust:
        h2 = KAT_YUK * kesik_ust
        ax.add_patch(Rectangle((x0, H), x1 - x0, h2, fc="none", ec=DUVAR, lw=1.0, ls=(0, (3, 2)), zorder=5))
        ax.add_patch(MPoly([(x0 - 0.4, H + h2), (x1 + 0.4, H + h2),
                            ((x0 + x1) / 2, H + h2 + (x1 - x0) / 2 * math.tan(math.radians(30)))],
                           closed=True, fc="none", ec="#9a5b3c", lw=1.0, ls=(0, (3, 2)), zorder=5))
    return H


def gunes(ax, x, H, yon=1, uzunluk=None, etiket_y=-0.55):
    """x: güney binanın kuzey saçağı; ışınlar kuzeye (yon=+1) iner."""
    for aci, renk, ad in ((ARALIK_ACI, R_GOLGE, "21 Ara"), (MART_ACI, R_GUNES, "21 Mar")):
        L = golge(H, aci) if uzunluk is None else min(golge(H, aci), uzunluk)
        z_son = H - L * math.tan(math.radians(aci))
        ax.plot([x, x + yon * L], [H, max(z_son, 0)], color=renk, lw=1.1, ls=(0, (5, 2)), zorder=9)
        ax.text(x + yon * L, etiket_y, f"{ad}: {sayi(golge(H, aci), 1)} m", fontsize=6.5, ha="center", va="top",
                color="#3c4d70" if renk == R_GOLGE else "#8a6400", zorder=9)


# ============================================================================
# T1 — büyüyebilen sıra ev
# ============================================================================
_ADA_W = pm.XS[0][1] - pm.XS[0][0]
_SIRA_W = (_ADA_W - pm.GECIT_G) / 2 if pm.KALIBRE else _ADA_W      # v2.1: ada ortası geçidiyle yarım sıra
T1_W = _SIRA_W / int(_SIRA_W // pm.T1_GEN)                            # K2 parseli (K1'de daha geniş)
T1_W_K1 = _SIRA_W / int(_SIRA_W // pm.T1_GEN_K1)
T1_D = (pm.YS[0][1] - pm.YS[0][0] - pm.ORTA_BANT) / 2
T1_IC = T1_W - 0.4
T1_ZEMIN = [("Mutfak", [(0, 0, 3.4, 3.6)]), ("Giriş", [(3.4, 0, T1_IC, 2.0)]), ("WC", [(3.4, 2.0, 4.9, 3.6)]),
            ("Merdiven", [(4.9, 2.0, T1_IC, 6.3)]), ("Oturma ve yemek", [(0, 3.6, 4.9, 8.6)]),
            ("Platform/kiler", [(4.9, 6.3, T1_IC, 8.6)])]
T1_KAT1 = [("Yatak 2", [(0, 0, 3.2, 4.0)]), ("Banyo", [(3.2, 0, 4.9, 2.4)]),
           ("Hol", [(3.2, 2.4, 4.9, 4.0), (0, 4.0, 4.9, 5.0)]), ("Merdiven", [(4.9, 2.0, T1_IC, 6.3)]),
           ("Dolap", [(4.9, 0, T1_IC, 2.0)]), ("Yatak 1", [(0, 5.0, 4.9, 8.6)]), ("Platform/dolap", [(4.9, 6.3, T1_IC, 8.6)])]
T1_KAT2 = [(a.replace("Yatak 2", "Yatak 3").replace("Yatak 1", "Yatak 4").replace("Banyo", "Banyo 2"), r)
           for a, r in T1_KAT1]
T1_ARKA = [("Büyükler odası / çalışma", [(0, 0, 3.9, 3.6)]), ("Duş · WC", [(3.9, 0, T1_IC, 3.6)])]


def t1():
    fig = plt.figure(figsize=(21, 14), dpi=150)
    gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 0.62], width_ratios=[1.25, 1, 1, 1], hspace=0.12,
                          wspace=0.05, left=0.03, right=0.985, top=0.9, bottom=0.04)
    # parsel planı
    ax = fig.add_subplot(gs[0, 0])
    eksen(ax, (-2.5, T1_W * 2 + 2), (-4, T1_D + 5.5), "Parsel planı (iki komşu parsel)")
    sokak_bandi(ax, -2.5, T1_W * 2 + 2, -4, 0, "S2 yaşam sokağı")
    for k in range(2):
        x0 = k * T1_W
        ax.add_patch(Rectangle((x0, 0), T1_W, T1_D, fc=R_OZEL_AVLU, ec="#7a9a64", lw=0.6, zorder=1))
        ax.add_patch(Rectangle((x0, pm.ON_ESIK), T1_W, pm.T1_EV_DER, fc=TIP_RENK["T1"], ec="white", lw=0.6, zorder=2))
        ax.add_patch(Rectangle((x0, pm.ON_ESIK + pm.T1_EV_DER), T1_W, pm.T1_GENISLEME, fc="none", ec=TIP_RENK["T1"],
                               lw=1.0, ls=(0, (3, 2)), zorder=2))
        ax.add_patch(Circle((x0 + T1_W / 2, T1_D - 4), 2.0, fc=R_AGAC, ec="white", lw=0.4, alpha=0.9, zorder=3))
    ax.add_patch(Rectangle((-2.5, T1_D), T1_W * 2 + 4.5, pm.ORTA_BANT / 2, fc=R_ORTAK_AVLU, ec="none", zorder=1))
    ax.text(T1_W, T1_D + 2, "ada içi ortak bahçe şeridi (8 m'nin yarısı)", ha="center", va="center", fontsize=7)
    ax.text(T1_W / 2, pm.ON_ESIK + pm.T1_EV_DER / 2, "çekirdek\nZ+1 → Z+2", ha="center", va="center", fontsize=7,
            color="white", zorder=4)
    ax.text(T1_W / 2, pm.ON_ESIK + pm.T1_EV_DER + pm.T1_GENISLEME / 2, "genişleme", ha="center", va="center",
            fontsize=6.5, zorder=4)
    ax.text(T1_W / 2, 1.0, "ön eşik", ha="center", va="center", fontsize=6.5, zorder=4)
    ax.text(T1_W * 1.5, (pm.ON_ESIK + pm.T1_EV_DER + pm.T1_GENISLEME + T1_D) / 2, "arka bahçe", ha="center",
            va="center", fontsize=7, zorder=4)
    for (a, b, m) in ((0, pm.ON_ESIK, f"{sayi(pm.ON_ESIK, 1)}"), (pm.ON_ESIK, pm.ON_ESIK + pm.T1_EV_DER, f"{sayi(pm.T1_EV_DER, 1)}"),
                      (pm.ON_ESIK + pm.T1_EV_DER, pm.ON_ESIK + pm.T1_EV_DER + pm.T1_GENISLEME, f"{sayi(pm.T1_GENISLEME, 1)}"),
                      (pm.ON_ESIK + pm.T1_EV_DER + pm.T1_GENISLEME, T1_D, f"{sayi(T1_D - pm.ON_ESIK - pm.T1_EV_DER - pm.T1_GENISLEME, 1)}")):
        ax.annotate("", xy=(-1.2, a), xytext=(-1.2, b), arrowprops=dict(arrowstyle="<->", lw=0.5))
        ax.text(-1.5, (a + b) / 2, m, rotation=90, ha="right", va="center", fontsize=6.5)
    ax.annotate("", xy=(0, -2.6), xytext=(T1_W, -2.6), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(T1_W / 2, -2.4, f"{sayi(T1_W, 2)} m", ha="center", va="bottom", fontsize=6.5)
    olcek_cubugu(ax, T1_W * 2 - 8.5, T1_D + 3.8, adim=2, n=4, h=0.35, yazi=6)
    # kat planları
    pls = [("Zemin kat (aşama 1: çekirdek)", T1_ZEMIN, True), ("1. kat (aşama 1)", T1_KAT1, False),
           ("2. kat (aşama 2: genişleme)", T1_KAT2, False)]
    net = {}
    for k, (bas, odalar, arka) in enumerate(pls):
        ax = fig.add_subplot(gs[0, k + 1])
        eksen(ax, (-0.6, T1_W + 0.6), (-2.2, pm.T1_EV_DER + pm.T1_GENISLEME + 1.2), bas)
        sokak_bandi(ax, -0.6, T1_W + 0.6, -2.2, -0.2, "sokak")
        net[bas] = plan_ciz(ax, 0, 0, T1_W, pm.T1_EV_DER, odalar, kesik=(k == 2))
        # v2: kaldırma platformu kabini (0,8 × 1,25 m), kesikli
        ax.add_patch(Rectangle((0.2 + 4.95, 0.2 + 6.7), 0.8, 1.25, fc="none", ec="#1f5fa8", lw=0.8, ls=(0, (2, 1.5)),
                               zorder=6))
        if arka:
            net["arka"] = plan_ciz(ax, 0, pm.T1_EV_DER, T1_W, pm.T1_GENISLEME + 0.2, T1_ARKA, kesik=True)
            ax.text(T1_W / 2, pm.T1_EV_DER + pm.T1_GENISLEME + 0.6, "aşama 2: arka oda (zemin)", ha="center",
                    fontsize=6.5, color="#555")
        else:
            ax.add_patch(Rectangle((0, pm.T1_EV_DER), T1_W, pm.T1_GENISLEME, fc=R_OZEL_AVLU, ec="none", zorder=1))
            ax.text(T1_W / 2, pm.T1_EV_DER + 2, "teras / bahçe" if k == 1 else "", ha="center", fontsize=6.5)
        olcek_cubugu(ax, 0, -1.65, adim=1, n=3, h=0.18, yazi=5.5)
    # kesit
    ax = fig.add_subplot(gs[1, 0:3])
    xs = 0
    sokak_bandi(ax, -6, 0, -0.35, 0, "")
    ax.text(-3, 0.3, "S2 sokak", ha="center", fontsize=7)
    ax.add_patch(Rectangle((0, -0.35), T1_D + 4, 0.35, fc="#c8e2b0", ec="none", zorder=1))
    H = kesit_bina(ax, pm.ON_ESIK, pm.ON_ESIK + pm.T1_EV_DER, 2, cati="duz", kesik_ust=1)
    ax.add_patch(Rectangle((pm.ON_ESIK + pm.T1_EV_DER, 0), pm.T1_GENISLEME, KAT_YUK, fc="none", ec=DUVAR, lw=1.0,
                           ls=(0, (3, 2)), zorder=5))
    ax.text(pm.ON_ESIK + pm.T1_EV_DER / 2, KAT_YUK * 2.5, "genişleme payı\n(2. kat)", ha="center", va="center",
            fontsize=7)
    ax.text(pm.ON_ESIK + pm.T1_EV_DER + pm.T1_GENISLEME / 2, KAT_YUK / 2, "arka\noda", ha="center", va="center", fontsize=7)
    ax.text(pm.ON_ESIK + pm.T1_EV_DER / 2, KAT_YUK * 0.5, "zemin\n(oturma, mutfak)", ha="center", va="center", fontsize=6.8)
    ax.text(pm.ON_ESIK + pm.T1_EV_DER / 2, KAT_YUK * 1.5, "1. kat (2 yatak)", ha="center", va="center", fontsize=6.8)
    kesit_agac(ax, T1_D - 4, 0, govde=2.2, tac_r=2.0)
    insan(ax, 0.8, 0)
    insan(ax, pm.ON_ESIK + pm.T1_EV_DER + pm.T1_GENISLEME + 3, 0, cocuk=True, renk="#5a4a8a")
    insan(ax, T1_D + 1.5, 0, cocuk=True, renk="#8a4a5a")
    ax.text(T1_D + 2, 1.6, "ortak bahçe\nşeridi", ha="center", fontsize=6.5)
    ax.annotate("", xy=(-1.2, 0), xytext=(-1.2, H), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(-1.4, H / 2, f"{sayi(H, 1)} m (çekirdek)", rotation=90, ha="right", va="center", fontsize=6.5)
    ax.annotate("", xy=(-0.4, 0), xytext=(-0.4, H + KAT_YUK), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(-0.15, H + KAT_YUK + 0.3, f"{sayi(H + KAT_YUK, 1)} m (son durum)", ha="left", fontsize=6.5)
    gunes(ax, pm.ON_ESIK + pm.T1_EV_DER, 3 * KAT_YUK, yon=1)
    for x in (0, pm.ON_ESIK, pm.ON_ESIK + pm.T1_EV_DER, pm.ON_ESIK + pm.T1_EV_DER + pm.T1_GENISLEME, T1_D):
        ax.plot([x, x], [-1.6, -1.3], color="#555", lw=0.5)
    ax.plot([0, T1_D], [-1.45, -1.45], color="#555", lw=0.5)
    ax.text(T1_D / 2, -2.2, f"parsel derinliği {sayi(T1_D, 1)} m · kat yüksekliği {sayi(KAT_YUK, 1)} m", ha="center",
            fontsize=7)
    eksen(ax, (-7, T1_D + 5), (-2.8, 13), "Kesit (parsel boyunca; sokak solda)")
    _bahce = T1_D - pm.ON_ESIK - pm.T1_EV_DER - pm.T1_GENISLEME
    _mart = golge(3 * KAT_YUK, MART_ACI) - pm.T1_GENISLEME
    ax.text(-6.5, 12.5, f"T12 adasının güney sırası: bahçe evin kuzeyinde. Son durumda (Z+2) 21 Mart öğle gölgesi "
                        f"{sayi(golge(3 * KAT_YUK, MART_ACI), 1)} m\n(bahçenin ≈ %{sayi(100 * (_bahce - _mart) / _bahce)}'i "
                        "güneşte), 21 Aralık'ta bahçe gölgede. Bu yüzden güneye bakan bahçeler T2'ye verildi.",
            fontsize=7, va="top", color="#444")
    # alan tablosu
    ax = fig.add_subplot(gs[1, 3])
    a1 = net["Zemin kat (aşama 1: çekirdek)"] + net["1. kat (aşama 1)"]
    a2 = net["2. kat (aşama 2: genişleme)"] + net["arka"]
    brut_kat = T1_W * pm.T1_EV_DER
    brut_arka = T1_W * pm.T1_GENISLEME
    parsel = T1_W * T1_D
    sat = [
        ("Aşama 1 · çekirdek (Z+1)", "2+1", sayi(a1, 1), sayi(2 * brut_kat, 1), "oturma-mutfak, 2 yatak, banyo, WC"),
        ("Aşama 2a · arka oda (zemin)", "+1 oda", sayi(net["arka"], 1), sayi(brut_arka, 1), "büyükler odası + duş, eşiksiz"),
        ("Aşama 2b · 2. kat", "+2 oda", sayi(net["2. kat (aşama 2: genişleme)"], 1), sayi(brut_kat, 1), "2 yatak + banyo"),
        ("Son durum (Z+2)", "4+1 + büyükler", sayi(a1 + a2, 1), sayi(3 * brut_kat + brut_arka, 1),
         f"parsel {sayi(parsel)} m² · emsal {sayi((3 * brut_kat + brut_arka) / parsel, 2)} · "
         f"oturum %{sayi(100 * T1_W * (pm.T1_EV_DER + pm.T1_GENISLEME) / parsel)}"),
    ]
    sat = [(a, b, c, d) for a, b, c, d, e in sat]
    tablo(ax, ["Aşama", "Oda", "Net m²", "Brüt m²"], sat, [0, 0.52, 0.74, 0.88],
          baslik="Alan tablosu (net: duvar içi; brüt: dış ölçü)", yazi=7.6)
    ax.text(0, 0.30, f"Son durum: parsel {sayi(parsel)} m² · emsal {sayi((3 * brut_kat + brut_arka) / parsel, 2)} · yapı oturumu "
                     f"%{sayi(100 * T1_W * (pm.T1_EV_DER + pm.T1_GENISLEME) / parsel)} · bahçe ≈ "
                     f"{sayi(T1_W * (T1_D - pm.ON_ESIK - pm.T1_EV_DER - pm.T1_GENISLEME))} m²", fontsize=7.4, va="top")
    _yapim = tv.tip_yapim_maliyeti(tv.SINIF["T1"], 3 * brut_kat + brut_arka)
    ax.text(0, 0.02,
            "Asansör: PAİY md. 34/1 tek bağımsız bölümlü konutu\n"
            "kapsamaz [D]. v2: kiler/dolap dikmesi (1,0 × 2,3 m; 3 katta\n"
            f"≈ {sayi(3 * 2.3, 1)} m²) kaldırma platformu yeri. Takılırsa ≈ {_mtl(tv.PLATFORM_TL)} [V],\n"
            f"yapım maliyetinin (≈ {_mtl(_yapim)}) %{sayi(100 * tv.PLATFORM_TL / _yapim)}'i. Zeminde büyükler\n"
            "odası ve duş eşiksiz. Statik sistem son duruma göre (deprem).",
            fontsize=7.0, color="#444", va="bottom")
    baslik_yaz(fig, "T1 · Büyüyebilen sıra ev",
               f"Parsel {sayi(T1_W, 2)} × {sayi(T1_D, 1)} m ({sayi(parsel)} m²; K1'de {sayi(T1_W_K1, 2)} m). Çekirdek Z+1 ile başlar; arka oda "
               f"ve 2. kat eklenir. Plandaki {sayi(M['tip']['T1']['konut'])} konutun tipi (v1: 447); kat profili son duruma (Z+2) "
               "göre sayılır. Mavi kesikli: platform kabini.")
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"tipoloji_T1_buyuyebilen_ev.{uz}", facecolor="white")
    plt.close(fig)
    return dict(net=a1 + a2, brut=3 * brut_kat + brut_arka)


# ============================================================================
# T2 — avlulu çok kuşaklı ev
# ============================================================================
T2_W = _SIRA_W / int(_SIRA_W // pm.T2_GEN)
T2_D = T1_D
T2_IC = T2_W - 0.4
T2_ZEMIN = [("Mutfak", [(0, 0, 3.0, 3.6)]), ("Giriş ve hol", [(3.0, 0, 7.4, 1.6), (3.0, 1.6, 4.4, 4.6)]),
            ("Banyo (engelsiz)", [(4.4, 1.6, 7.4, 4.6)]), ("Oturma ve yemek", [(0, 3.6, 3.0, 4.6), (0, 4.6, 4.4, 10.6)]),
            ("Yatak 2", [(4.4, 4.6, 7.4, 7.4)]), ("Yatak 1", [(4.4, 7.4, 7.4, 10.6)]),
            ("Merdiven", [(7.4, 1.4, T2_IC, 5.4)]), ("Dubleks girişi", [(7.4, 0, T2_IC, 1.4)]),
            ("Asansör yeri", [(7.4, 5.4, T2_IC, 7.0)]), ("Ortak çamaşır", [(7.4, 7.0, T2_IC, 10.6)])]
T2_KAT1 = [("Mutfak", [(0, 0, 3.6, 3.6)]), ("Hol", [(3.6, 0, 7.4, 2.0)]), ("WC", [(5.8, 2.0, 7.4, 3.6)]),
           ("Kiler", [(3.6, 2.0, 5.8, 3.6)]), ("Yemek", [(0, 3.6, 4.0, 6.2)]),
           ("Oturma", [(0, 6.2, 7.4, 10.6), (4.0, 3.6, 7.4, 6.2)]), ("Sahanlık", [(7.4, 0, T2_IC, 1.4)]),
           ("Merdiven", [(7.4, 1.4, T2_IC, 5.4)]), ("Asansör yeri", [(7.4, 5.4, T2_IC, 7.0)]),
           ("Çalışma", [(7.4, 7.0, T2_IC, 10.6)])]
T2_KAT2 = [("Yatak 2", [(0, 0, 3.6, 3.8)]), ("Yatak 3", [(3.6, 0, 7.4, 3.8)]), ("Aile holü", [(0, 3.8, 4.4, 6.6)]),
           ("Banyo", [(4.4, 3.8, 7.4, 6.6)]), ("Yatak 1", [(0, 6.6, 4.4, 10.6)]), ("Yatak 4", [(4.4, 6.6, 7.4, 10.6)]),
           ("Sahanlık", [(7.4, 0, T2_IC, 1.4)]), ("Merdiven", [(7.4, 1.4, T2_IC, 5.4)]),
           ("Asansör yeri", [(7.4, 5.4, T2_IC, 7.0)]), ("Dolap", [(7.4, 7.0, T2_IC, 10.6)])]


def t2():
    fig = plt.figure(figsize=(21, 14), dpi=150)
    gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 0.62], width_ratios=[1.15, 1, 1, 1], hspace=0.12, wspace=0.05,
                          left=0.03, right=0.985, top=0.9, bottom=0.04)
    ax = fig.add_subplot(gs[0, 0])
    eksen(ax, (-2.5, T2_W + 3), (-4, T2_D + 5.5), "Parsel planı")
    sokak_bandi(ax, -2.5, T2_W + 3, -4, 0, "")
    ax.text(T2_W / 2, -3.1, "S2 yaşam sokağı", ha="center", va="center", fontsize=7.5, color="#6a655d", zorder=2)
    ax.add_patch(Rectangle((0, 0), T2_W, T2_D, fc=R_OZEL_AVLU, ec="#7a9a64", lw=0.6, zorder=1))
    ax.add_patch(Rectangle((0, pm.ON_ESIK), T2_W, pm.T2_EV_DER, fc=TIP_RENK["T2"], ec="white", lw=0.6, zorder=2))
    ax.add_patch(Rectangle((-2.5, T2_D), T2_W + 5.5, pm.ORTA_BANT / 2, fc=R_ORTAK_AVLU, ec="none", zorder=1))
    for (x, y) in ((2.5, T2_D - 5), (7, T2_D - 9)):
        ax.add_patch(Circle((x, y), 2.0, fc=R_AGAC, ec="white", lw=0.4, alpha=0.9, zorder=3))
    ax.add_patch(Rectangle((0.5, pm.ON_ESIK + pm.T2_EV_DER + 0.5), 4.5, 3.0, fc="#e8dcc2", ec="none", zorder=2))
    ax.text(2.75, pm.ON_ESIK + pm.T2_EV_DER + 2, "büyüklerin\nterası", ha="center", va="center", fontsize=6.3, zorder=3)
    ax.text(T2_W / 2, pm.ON_ESIK + pm.T2_EV_DER / 2, "Z+2\n2 bağımsız bölüm", ha="center", va="center", fontsize=7,
            color="white", zorder=4)
    ax.text(T2_W / 2, (pm.ON_ESIK + pm.T2_EV_DER + T2_D) / 2 + 2, "ortak avlu-bahçe\n(iki hane)", ha="center",
            va="center", fontsize=7, zorder=4)
    ax.text(T2_W / 2, T2_D + 2, "ada içi ortak bahçe şeridi", ha="center", va="center", fontsize=6.8)
    ax.annotate("", xy=(0, -1.5), xytext=(T2_W, -1.5), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(T2_W / 2, -1.35, f"{sayi(T2_W, 2)} m", ha="center", va="bottom", fontsize=6.5)
    for (a, b) in ((0, pm.ON_ESIK), (pm.ON_ESIK, pm.ON_ESIK + pm.T2_EV_DER), (pm.ON_ESIK + pm.T2_EV_DER, T2_D)):
        ax.annotate("", xy=(-1.2, a), xytext=(-1.2, b), arrowprops=dict(arrowstyle="<->", lw=0.5))
        ax.text(-1.5, (a + b) / 2, sayi(b - a, 1), rotation=90, ha="right", va="center", fontsize=6.5)
    olcek_cubugu(ax, T2_W - 6, T2_D + 3.8, adim=2, n=3, h=0.35, yazi=6)
    pls = [("Zemin: büyükler dairesi + dubleks girişi", T2_ZEMIN), ("1. kat: dubleks yaşam katı", T2_KAT1),
           ("2. kat: dubleks yatak katı", T2_KAT2)]
    net = {}
    for k, (bas, odalar) in enumerate(pls):
        ax = fig.add_subplot(gs[0, k + 1])
        eksen(ax, (-0.6, T2_W + 0.6), (-2.2, pm.T2_EV_DER + 2.6), bas)
        sokak_bandi(ax, -0.6, T2_W + 0.6, -2.2, -0.2, "sokak")
        net[k] = plan_ciz(ax, 0, 0, T2_W, pm.T2_EV_DER, odalar, yazi=6.6)
        ax.add_patch(Rectangle((0, pm.T2_EV_DER), T2_W, 2.4, fc=R_OZEL_AVLU, ec="none", zorder=1))
        ax.text(T2_W / 2, pm.T2_EV_DER + 1.2, "avlu" if k == 0 else ("avluya balkon" if k == 1 else ""), ha="center",
                va="center", fontsize=6.5)
        if k == 0:
            ax.add_patch(Rectangle((0.2, 0.2), 7.4, 10.6, fc="none", ec="#1f5fa8", lw=1.4, ls=(0, (4, 2)), zorder=6))
            ax.text(3.9, -0.95, "büyükler dairesi (eşiksiz)", ha="center", fontsize=6.5, color="#1f5fa8")
        olcek_cubugu(ax, 0, -1.65, adim=1, n=3, h=0.18, yazi=5.5)
    ax = fig.add_subplot(gs[1, 0:2])
    # T12 adasının kuzey sırası: sokak kuzeyde (sağda), bahçe güneyde (solda)
    x_ev0 = T2_D - pm.ON_ESIK - pm.T2_EV_DER
    ax.add_patch(Rectangle((-35, -0.35), T2_D + 35, 0.35, fc="#c8e2b0", ec="none", zorder=1))
    ax.add_patch(Rectangle((-pm.ORTA_BANT, -0.35), pm.ORTA_BANT, 0.35, fc="#a9cf8f", ec="none", zorder=1.5))
    sokak_bandi(ax, T2_D, T2_D + 6, -0.35, 0, "")
    ax.text(T2_D + 3, 0.3, "S2 sokak", ha="center", fontsize=7)
    H = kesit_bina(ax, x_ev0, x_ev0 + pm.T2_EV_DER, 3, cati="egik")
    for k, m in enumerate(("büyükler (2+1)", "dubleks: yaşam", "dubleks: yatak")):
        ax.text(x_ev0 + pm.T2_EV_DER / 2, KAT_YUK * (k + 0.5), m, ha="center", va="center", fontsize=7)
    # güneydeki komşu T1 (son durum) — görünüş
    t1x1 = -pm.ORTA_BANT - (T1_D - pm.ON_ESIK - pm.T1_EV_DER - pm.T1_GENISLEME)
    ax.add_patch(Rectangle((t1x1 - pm.T1_GENISLEME - pm.T1_EV_DER, 0), pm.T1_EV_DER, 3 * KAT_YUK, fc="#e4ded5",
                           ec="#8d8478", lw=0.6, zorder=2))
    ax.add_patch(Rectangle((t1x1 - pm.T1_GENISLEME, 0), pm.T1_GENISLEME, KAT_YUK, fc="#e4ded5", ec="#8d8478", lw=0.6,
                           zorder=2))
    ax.text(t1x1 - pm.T1_GENISLEME - pm.T1_EV_DER / 2 + 2, 3 * KAT_YUK + 0.5, "güneydeki T1 (son durum)", ha="center",
            fontsize=6.5)
    gunes(ax, t1x1 - pm.T1_GENISLEME, 3 * KAT_YUK, yon=1)
    kesit_agac(ax, 6, 0, govde=2.4, tac_r=2.2)
    insan(ax, x_ev0 - 2.5, 0, renk="#555", boy=1.6)
    insan(ax, x_ev0 - 4, 0, cocuk=True, renk="#5a4a8a")
    ax.text(-pm.ORTA_BANT / 2, 1.2, "ortak\nşerit", ha="center", fontsize=6.5)
    ax.text(x_ev0 - 3.9, 3.0, "ortak avlu-bahçe (güneyde)", ha="center", fontsize=6.5)
    ax.annotate("", xy=(T2_D + 0.6, 0), xytext=(T2_D + 0.6, H), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(T2_D + 0.9, H / 2, f"{sayi(H, 1)} m", rotation=90, ha="left", va="center", fontsize=6.5)
    eksen(ax, (-35, T2_D + 7), (-2.8, 14), "Kesit (parsel boyunca; güney solda, sokak kuzeyde)")
    ax.text(-34.5, 13.5, "Güneydeki T1'in son durumdaki gölgesi 21 Aralık'ta bile ortak şeritte biter; T2 avlusu kışın öğle "
                         "güneşini alır.", fontsize=7, va="top", color="#444")
    ax = fig.add_subplot(gs[1, 2:])
    brut = T2_W * pm.T2_EV_DER
    oran_b = 78.44 / 93.28
    sat = [
        ("Büyükler dairesi (zemin)", "2+1", sayi(78.44, 1), sayi(brut * oran_b, 1), "eşiksiz giriş, engelsiz banyo, avluya açılır"),
        ("Genç aile dubleksi (1.–2. kat)", "4+1", sayi(net[1] + net[2] + 1.96 + 5.6, 1),
         sayi(brut * (1 - oran_b) + 2 * brut, 1), "ayrı giriş ve merdiven"),
        ("Ortak çamaşır (zemin)", "—", sayi(alan([(7.4, 7.0, T2_IC, 10.6)]), 1), "—", "iki hanenin ortak alanı"),
        ("Asansör yeri (3 kat)", "PAİY 34/1", sayi(3 * alan([(7.4, 5.4, T2_IC, 7.0)]), 1), "—",
         f"depo; platform takılırsa ≈ {_mtl(tv.PLATFORM_TL)} [V]"),
        ("Bina toplamı (Z+2)", "2 bağımsız bölüm", sayi(net[0] + net[1] + net[2], 1), sayi(3 * brut, 1),
         f"parsel {sayi(T2_W * T2_D)} m² · emsal {sayi(3 * brut / (T2_W * T2_D), 2)} · oturum %{sayi(100 * brut / (T2_W * T2_D))}"),
    ]
    tablo(ax, ["Birim", "Oda", "Net m²", "Brüt m²", "Not"], sat, [0, 0.27, 0.42, 0.53, 0.64],
          baslik="Alan tablosu", yazi=8)
    _yapim = tv.tip_yapim_maliyeti(tv.SINIF["T2"], 3 * brut)
    ax.text(0, 0.04, "Kat Mülkiyeti Kanunu'na göre iki bağımsız bölüm; ortak avlu ve çamaşırlık ortak yer. Büyükler katı kira ya da\n"
                     "tapu olarak ayrılabilir. Asansör: 3 kat + 2 BB → PAİY md. 34/1 asansör yeri [D]; v2: merdivenin ucunda\n"
                     f"1,4 × 1,6 m kuyu. Platform takılırsa ≈ {_mtl(tv.PLATFORM_TL)} [V] = yapım maliyetinin (≈ {_mtl(_yapim)}) "
                     f"%{sayi(100 * tv.PLATFORM_TL / _yapim)}'i; zemin 2+1 zaten eşiksiz.",
            fontsize=7.3, color="#444", va="bottom")
    baslik_yaz(fig, "T2 · Avlulu çok kuşaklı ev",
               f"Parsel {sayi(T2_W, 2)} × {sayi(T2_D, 1)} m ({sayi(T2_W * T2_D)} m²). Zeminde büyükanne-büyükbaba dairesi, üstte "
               f"ayrı girişli genç aile dubleksi; ortak avlu. Plandaki {sayi(M['tip']['T2']['parsel'])} binanın "
               f"({sayi(M['tip']['T2']['konut'])} konut) tipi (v1: 235 bina). Asansör yeri merdivenin kuzey ucunda.")
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"tipoloji_T2_cok_kusakli_ev.{uz}", facecolor="white")
    plt.close(fig)


# ============================================================================
# T3 — avlu grubu (8–12 hane)
# ============================================================================
G_W, G_D = 36.0, (pm.YS[0][1] - pm.YS[0][0]) / 2
SK = pm.T3_SOKAK_KANADI
ON = pm.T3_ON
YK_G = pm.T3_YAN_KANAT_G
ARKA = pm.T3_ARKA_DER if pm.KALIBRE else 0.0                          # v2.1: güney grubun arka kanadı
YK_L = (G_D - ARKA - pm.T3_ON - pm.T3_SOKAK_KANADI) if pm.KALIBRE else pm.T3_YAN_KANAT_L
YK_L_K = pm.T3_YAN_KANAT_L                                            # kuzey grubun yan kanadı
# zemin birimleri (sokak kanadı, x boyunca)
T3_ZEMIN_BIRIM = [("2+1 erişilebilir", 0, 11, "yasam"), ("Çekirdek A", 11, 13.5, "dolasim"),
                  ("Ortak oda", 13.5, 16.25, "ortak"), ("Kapı altı geçit", 16.25, 19.75, "dolasim"),
                  ("Bisiklet · çöp", 19.75, 22.5, "ortak"), ("Çekirdek B", 22.5, 25, "dolasim"),
                  ("Esnek oda", 25, 28, "esnek"), ("1+1", 28, 36, "yasam")]
T3_UST_BIRIM = [("3+1 (D1)", 0, 11), ("Çekirdek A", 11, 13.5), ("3+1 kompakt (D2)", 13.5, 22.5), ("Çekirdek B", 22.5, 25),
                ("3+1 (D3)", 25, 36)]
T3_D1 = [("Salon", [(0, 0, 5.6, 4.4)]), ("Mutfak", [(5.6, 0, 8.6, 4.4)]), ("Banyo", [(8.6, 0, 10.6, 4.4)]),
         ("Hol", [(0, 4.4, 10.6, 5.6)]), ("Yatak 1", [(0, 5.6, 4.0, 9.6)]), ("Yatak 2", [(4.0, 5.6, 7.2, 9.6)]),
         ("Yatak 3", [(7.2, 5.6, 10.6, 9.6)])]
T3_DUBLEKS_Z = [("Oturma-mutfak", [(0, 0, 6.6, 4.2)]), ("WC", [(0, 4.2, 1.6, 6.1)]), ("Merdiven", [(1.6, 4.2, 6.6, 6.1)])]
T3_DUBLEKS_U = [("Yatak 1", [(0, 0, 3.6, 3.6)]), ("Yatak 2", [(3.6, 0, 6.6, 3.6)]), ("Banyo", [(0, 3.6, 2.4, 6.1)]),
                ("Hol", [(2.4, 3.6, 6.6, 6.1)])]


def t3():
    fig = plt.figure(figsize=(21, 15), dpi=150)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.58], width_ratios=[1.25, 0.95, 0.9], hspace=0.10, wspace=0.05,
                          left=0.03, right=0.985, top=0.9, bottom=0.04)
    # grup planı (zemin)
    ax = fig.add_subplot(gs[0, 0])
    eksen(ax, (-6, G_W + 3), (-5.5, G_D + 4),
          "Avlu grubu planı (güney sıra, zemin; 14 hane)" if pm.KALIBRE else "Avlu grubu planı (zemin kat, 12 hane)")
    sokak_bandi(ax, -6, G_W + 3, -5.5, 0, "S2 yaşam sokağı")
    ax.add_patch(Rectangle((0, 0), G_W, G_D, fc=R_ORTAK_AVLU, ec="#7a9a64", lw=0.6, zorder=1))
    ax.add_patch(Rectangle((-6, G_D), G_W + 9, 4, fc="#bcd9a0", ec="none", zorder=1))
    ax.text(G_W / 2, G_D + 2, "ada ortası: kuzey grubun avlusu (yanlarda 2,5 m bahçe duvarı)" if pm.KALIBRE else
            "ada ortası: karşı avlu grubunun ortak bahçesiyle birleşir", ha="center", fontsize=7)
    if pm.KALIBRE:   # v2.1: dördüncü kenar — tek katlı arka kanat
        ax.add_patch(Rectangle((0, G_D - ARKA), G_W, ARKA, fc=ODA["yasam"], ec=DUVAR, lw=1.0, zorder=3))
        ax.plot([G_W / 2, G_W / 2], [G_D - ARKA, G_D], color=DUVAR, lw=1.0, zorder=3.5)
        for xm_ in (G_W / 4, 3 * G_W / 4):
            ax.text(xm_, G_D - ARKA / 2 + 0.9, "2+1 eşiksiz (Z)", ha="center", va="center", fontsize=6.4, zorder=4)
            ax.text(xm_, G_D - ARKA / 2 - 1.0, "arka kanat (v2.1)", ha="center", va="center", fontsize=5.8,
                    color="#7a5a20", zorder=4)
    ax.add_patch(Rectangle((-6, 0), 6, G_D, fc="#efe6d2", ec="none", zorder=1))
    ax.text(-3, G_D / 2, "S3 geçidi (6 m)", rotation=90, ha="center", va="center", fontsize=7)
    for ad, x0, x1, tur in T3_ZEMIN_BIRIM:
        ax.add_patch(Rectangle((x0, ON), x1 - x0, SK, fc=ODA[tur], ec=DUVAR, lw=1.0, zorder=3))
        ax.text((x0 + x1) / 2, ON + SK / 2, ad, ha="center", va="center", fontsize=6.6 if x1 - x0 > 4 else 6.0,
                rotation=0 if x1 - x0 > 4 else 90, zorder=4)
    for xw in (0, G_W - YK_G):
        for k in range(2):
            y0 = ON + SK + k * YK_L / 2
            ax.add_patch(Rectangle((xw, y0), YK_G, YK_L / 2, fc=ODA["yasam"], ec=DUVAR, lw=1.0, zorder=3))
            ax.text(xw + YK_G / 2, y0 + YK_L / 4, "2+1\ndubleks", ha="center", va="center", fontsize=6.4, zorder=4)
            px = xw + YK_G if xw == 0 else xw - 3.0
            ax.add_patch(Rectangle((px, y0 + 0.4), 3.0, YK_L / 2 - 0.8, fc="#e8dcc2", ec="none", zorder=2))
    # avlu öğeleri
    oyun = (12.5, 20.8, 7, 4) if pm.KALIBRE else (13, 17.5, 7, 4.5)
    ax.add_patch(Rectangle(oyun[:2], oyun[2], oyun[3], fc="#f1dfb5", ec="#c9b27a", lw=0.6, zorder=2))
    ax.text(oyun[0] + oyun[2] / 2, oyun[1] + oyun[3] / 2, "kum · oyun", ha="center", va="center", fontsize=6.5, zorder=3)
    agac_yer = ((9.6, 13.8, 1.8), (26.4, 13.8, 1.8), (9.8, 23.9, 1.7), (26.4, 18.6, 1.8)) if pm.KALIBRE else \
        ((11, 14.5, 2.3), (24, 15, 2.6), (18, 26.5, 3.0), (29.5, 27.5, 2.2), (6, 27.5, 2.2))
    for (x, y, r) in agac_yer:
        ax.add_patch(Circle((x, y), r, fc=R_AGAC, ec="white", lw=0.4, alpha=0.9, zorder=4))
    cy_ = 21.6 if pm.KALIBRE else 21.5
    ax.add_patch(Rectangle((21.0, cy_), 4.6, 1.1, fc="#8a6a4a", ec="none", zorder=3))
    ax.text(23.3, cy_ + 1.5, "oturma · çardak", ha="center", fontsize=6.3, zorder=4)
    ax.text(G_W / 2, 16.6 if pm.KALIBRE else 23.6,
            f"ORTAK AVLU ≈ {sayi((G_W - 2 * YK_G) * YK_L)} m²" if pm.KALIBRE else "ORTAK AVLU",
            ha="center", va="center", fontsize=8.5, fontweight="bold", color="#3f5b2a", zorder=5,
            bbox=dict(fc=R_ORTAK_AVLU, ec="none", pad=1.0))
    ax.annotate("", xy=(17.1, ON + SK + 2.5), xytext=(17.1, -1.0), arrowprops=dict(arrowstyle="->", color="#1f5fa8", lw=1.2),
                zorder=5)
    ax.text(15.6, -0.9, "giriş", fontsize=6.5, color="#1f5fa8", ha="right")
    ax.annotate("", xy=(0, -3.8), xytext=(G_W, -3.8), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(G_W / 2, -3.6, f"{sayi(G_W, 1)} m", ha="center", va="bottom", fontsize=6.5)
    ax.annotate("", xy=(G_W + 1.4, 0), xytext=(G_W + 1.4, G_D), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(G_W + 1.7, G_D / 2, f"{sayi(G_D, 1)} m", rotation=90, ha="left", va="center", fontsize=6.5)
    olcek_cubugu(ax, 0, G_D + 3.3, adim=5, n=2, h=0.3, yazi=6)
    # üst kat planı
    ax = fig.add_subplot(gs[0, 1:])
    eksen(ax, (-0.8, G_W + 0.8), (-3.2, SK + 3.8), "Sokak kanadı 1. ve 2. kat planı (3 × 3+1); D1 oda ayrıntısı")
    sokak_bandi(ax, -0.8, G_W + 0.8, -3.2, -1.6, "sokak")
    ax.add_patch(Rectangle((-0.8, -1.6), G_W + 1.6, ON, fc=R_OZEL_AVLU, ec="none"))
    for ad, x0, x1 in T3_UST_BIRIM:
        if ad == "3+1 (D1)":
            nd1 = plan_ciz(ax, x0, 0, x1 - x0, SK, T3_D1, yazi=6.5)
        elif ad == "3+1 (D3)":
            yansit = [(a, [(10.6 - r[2], r[1], 10.6 - r[0], r[3]) for r in rr]) for a, rr in T3_D1]
            plan_ciz(ax, x0, 0, x1 - x0, SK, yansit, yazi=6.5)
        else:
            tur = "dolasim" if "Çekirdek" in ad else "yasam"
            ax.add_patch(Rectangle((x0, 0), x1 - x0, SK, fc=DUVAR, ec=DUVAR, zorder=2))
            ax.add_patch(Rectangle((x0 + 0.2, 0.2), x1 - x0 - 0.4, SK - 0.4, fc=ODA[tur], ec="none", zorder=3))
            if "Çekirdek" in ad:
                for k in range(1, 15):
                    yy = 0.4 + k * 0.28
                    ax.plot([x0 + 0.3, x0 + 1.4], [yy, yy], color="#8d8478", lw=0.4, zorder=4)
                ax.add_patch(Rectangle((x0 + 1.5, 6.4), 0.8, 1.6, fc="#cfd6de", ec="#777", lw=0.5, zorder=4))
                ax.text((x0 + x1) / 2, 8.4, "asansör\nyeri*", ha="center", fontsize=5.5, zorder=5)
            ax.text((x0 + x1) / 2, SK / 2, ad, ha="center", va="center", fontsize=6.8,
                    rotation=0 if x1 - x0 > 4 else 90, zorder=5)
    ax.add_patch(Rectangle((-0.8, SK), G_W + 1.6, 3.8, fc=R_ORTAK_AVLU, ec="none", zorder=1))
    for x in (2.0, 7.5, 27.0, 32.5):
        ax.add_patch(Rectangle((x, SK), 2.6, 1.2, fc="none", ec=DUVAR, lw=0.8, zorder=4))
    ax.text(G_W / 2, SK + 2.4, "avluya bakan balkonlar · yan kanatların çatı terasları", ha="center", fontsize=6.8)
    olcek_cubugu(ax, G_W - 6.5, SK + 2.0, adim=2, n=3, h=0.25, yazi=5.5)
    # kesit: tüm ada boyunca iki avlu grubu
    ax = fig.add_subplot(gs[1, 0:2])
    blok = pm.YS[0][1] - pm.YS[0][0]
    kat = 3
    ax.add_patch(Rectangle((-5, -0.35), blok + 10, 0.35, fc="#c8e2b0", ec="none", zorder=1))
    sokak_bandi(ax, -5, 0, -0.35, 0, "")
    sokak_bandi(ax, blok, blok + 5, -0.35, 0, "")
    ax.text(-2.5, 0.3, "S2", ha="center", fontsize=7)
    ax.text(blok + 2.5, 0.3, "S2", ha="center", fontsize=7)
    H1 = kesit_bina(ax, ON, ON + SK, kat)
    H2 = kesit_bina(ax, blok - ON - SK, blok - ON, kat)
    ax.add_patch(Rectangle((ON + SK, 0), YK_L, 2 * KAT_YUK, fc="#ddd6cb", ec="#8d8478", lw=0.6, zorder=2))
    ax.add_patch(Rectangle((blok - ON - SK - YK_L_K, 0), YK_L_K, 2 * KAT_YUK, fc="#ddd6cb", ec="#8d8478", lw=0.6, zorder=2))
    ax.text(ON + SK + YK_L / 2, KAT_YUK, "yan kanat\n(görünüş)", ha="center", va="center", fontsize=6.5, zorder=3)
    ax.text(blok - ON - SK - YK_L_K / 2, KAT_YUK, "yan kanat\n(görünüş)", ha="center", va="center", fontsize=6.5, zorder=3)
    if pm.KALIBRE:   # v2.1: güney grubun arka kanadı (Z) ve kuzey avluya düşen gölgesi
        Ha = kesit_bina(ax, G_D - ARKA, G_D, 1)
        ax.text(G_D - ARKA / 2, KAT_YUK / 2, "arka\nkanat", ha="center", va="center", fontsize=6.3, zorder=6)
        gunes(ax, G_D, Ha + 0.3, yon=1, etiket_y=-1.15)
    ax.add_patch(Rectangle((ON, 0), SK, KAT_YUK, fc="#efe6d2", ec="none", zorder=3.5))
    ax.text(ON + SK / 2, KAT_YUK / 2, "kapı altı\ngeçit", ha="center", va="center", fontsize=6.5, zorder=4)
    ax.add_patch(Rectangle((blok - ON - SK, 0), SK, KAT_YUK, fc="#efe6d2", ec="none", zorder=3.5))
    ax.text(blok - ON - SK / 2, KAT_YUK / 2, "kapı altı\ngeçit", ha="center", va="center", fontsize=6.5, zorder=4)
    for x in ((20, 35.5, 45) if pm.KALIBRE else (20, 31, 42)):
        kesit_agac(ax, x, 0, govde=2.6, tac_r=2.4)
    insan(ax, 24, 0, cocuk=True, renk="#5a4a8a")
    insan(ax, 25.5, 0, cocuk=True, renk="#8a4a5a")
    insan(ax, 41 if pm.KALIBRE else 37, 0, renk="#555")
    gunes(ax, ON + SK, H1, yon=1)
    ax.text(blok * 0.25, H1 + 2.5, "güney avlu grubu", ha="center", fontsize=7.5, fontweight="bold")
    ax.text(blok * 0.75, H1 + 2.5, "kuzey avlu grubu", ha="center", fontsize=7.5, fontweight="bold")
    if not pm.KALIBRE:
        ax.plot([G_D, G_D], [0, 1.0], color="#7a9a64", lw=1.2)
        ax.text(G_D, 1.2, "çit / alçak duvar", ha="center", fontsize=6.3)
    ax.annotate("", xy=(0, -2.25), xytext=(blok, -2.25), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(blok / 2, -2.4, f"ada derinliği {sayi(blok, 1)} m (iki avlu grubu sırt sırta)", ha="center", va="top",
            fontsize=7)
    eksen(ax, (-6, blok + 6), (-3.2, 14), "Ada kesiti (güney solda; kapı altı geçitlerden)")
    ax.text(-5.5, 13.6, ("Güney grubun avlusu 21 Aralık öğlesinde gölgede, 21 Mart'ta yarısı güneşte. v2.1: güney grubun tek katlı "
                         "arka kanadı kuzey avlunun güney\nkenarında; kuzey avluda 21 Aralık öğle gölgesi "
                         f"{sayi(golge(KAT_YUK + 0.3, ARALIK_ACI), 1)} m (avlu derinliğinin ≈ %"
                         f"{sayi(100 * golge(KAT_YUK + 0.3, ARALIK_ACI) / (G_D - ON - SK))}'i), 21 Mart'ta "
                         f"{sayi(golge(KAT_YUK + 0.3, MART_ACI), 1)} m. Oyun alanı kuzey avlunun ortasına konur.")
            if pm.KALIBRE else
            ("Güney grubun avlusu 21 Aralık öğlesinde gölgede, 21 Mart'ta büyük ölçüde güneşte; kuzey grubun avlusu "
             "yıl boyu güneşli.\nBu yüzden güney sırada oyun alanı avlunun kuzey ucuna, kuzey sırada sokak kanadının "
             "dibine konur."), fontsize=7, va="top", color="#444")
    # tablo
    ax = fig.add_subplot(gs[1, 2])
    nd_z = 9.6 * 6.6 + 2.0 * 6.0 * 0  # yer tutucu
    d_z = alan([r for _, rr in T3_DUBLEKS_Z for r in rr])
    _as3 = tv.asansor_maliyeti(4)
    _yapim3 = tv.tip_yapim_maliyeti(tv.SINIF["T3_Z+3"], SK * G_W * 4 - 3.5 * SK + 2 * YK_G * YK_L * 2)
    d_u = alan([r for _, rr in T3_DUBLEKS_U for r in rr])
    sat = [
        ("Zemin: 2+1 erişilebilir", "1", "≈ 92", "110", "eşiksiz, avluya açılır"),
        ("Zemin: 1+1", "1", "≈ 66", "80", "yalnız yaşayan yaşlı, genç çift"),
        ("1.–2. kat: 3+1 (D1, D3)", "4", sayi(nd1, 1), "110", "salon sokakta, yatak avluda"),
        ("1.–2. kat: 3+1 kompakt (D2)", "2", "≈ 80", "90", "çekirdekler arası"),
        ("Yan kanat: 2+1 dubleks", "4", sayi(d_z + d_u, 1), sayi(YK_G * YK_L, 1), "her birine avlu terası"),
        ("Asansör yeri, Z+2 (2 çekirdek)", "2", sayi(2 * 3 * tv.KUYU_ASANSOR[0] * tv.KUYU_ASANSOR[1], 1), "—",
         "kuyu 1,6 × 1,8 m; depo olarak"),
        (f"Asansör, Z+3 ({17 if pm.KALIBRE else 15} hane)", "2 (P4: 1)", "—", "—", f"2 × {sayi(_as3 / 1e6, 1)} milyon TL [V]"),
    ] + ([("Arka kanat (Z): 2+1 eşiksiz", "2", "≈ 76", sayi(G_W * ARKA / 2, 0), "v2.1; avluyu kapatır")]
          if pm.KALIBRE else []) + [
        ("Grup toplamı (Z+2)", "14 hane" if pm.KALIBRE else "12 hane",
         sayi(92 + 66 + 4 * nd1 + 2 * 80 + 4 * (d_z + d_u) + (152 if pm.KALIBRE else 0), 0),
         sayi(SK * G_W * 3 - 3.5 * SK + 2 * YK_G * YK_L * 2 + G_W * ARKA, 0),
         f"avlu ≈ {sayi((G_W - 2 * YK_G) * YK_L)} m²" if pm.KALIBRE else
         f"avlu ≈ {sayi((G_W - 2 * YK_G) * (G_D - ON - SK))} m²"),
    ]
    tablo(ax, ["Birim", "Adet", "Net m²", "Brüt m²", "Not"], sat, [0, 0.40, 0.50, 0.62, 0.74],
          baslik=("Alan tablosu (güney grup Z+2; K3'te Z+3 → 17 hane)" if pm.KALIBRE else
                  "Alan tablosu (Z+2 grup; K3'te Z+3 → 15 hane)"), yazi=7.0)
    _h3 = 17 if pm.KALIBRE else 15
    ax.text(0, 0.0, "* PAİY md. 34/1 [D]: Z+2'de asansör yeri, Z+3'te asansör. Bugün her merdiven evine bir\n"
                    f"asansör: Z+3 grubunda 2 × {_mtl(_as3)} [V] (yapımın %{sayi(100 * 2 * _as3 / _yapim3, 1)}'i, hane başına ≈ "
                    f"{sayi(2 * _as3 / _h3 / 1e3)} bin TL);\nP4 (galeri + tek asansör) bunu yarıya indirir. Zemin daireler ve arka "
                    "kanat eşiksiz.", fontsize=6.4, color="#444", va="bottom")
    baslik_yaz(fig, "T3 · Avlu grubu",
               f"Parsel {sayi(G_W, 0)} × {sayi(G_D, 1)} m ({sayi(G_W * G_D)} m²). Sokak kanadı Z+2 (K3'te Z+3), iki yan kanat Z+1, "
               f"ortada 8–12 hanenin ortak avlusu. Plandaki {sayi(M['avlu_grubu'])} grubun ({sayi(M['tip']['T3']['konut'])} "
               "konut) tipi. Kapı altı geçitten girilir.")
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"tipoloji_T3_avlu_grubu.{uz}", facecolor="white")
    plt.close(fig)


# ============================================================================
# T4 — çevre adası çubuğu, zeminde dükkân
# ============================================================================
M_W, M_D = pm.T4_MODUL, pm.T4_DER
T4_2P1 = [("Salon", [(0, 0, 4.6, 5.6)]), ("Mutfak", [(4.6, 0, 8.1, 3.2)]), ("Banyo", [(4.6, 3.2, 8.1, 5.6)]),
          ("Hol", [(0, 5.6, 8.1, 7.0)]), ("Yatak 1", [(0, 7.0, 4.4, 11.6)]), ("Yatak 2", [(4.4, 7.0, 8.1, 11.6)])]
T4_1P1 = [("Salon ve mutfak", [(0, 0, 6.6, 3.8)]), ("Yatak", [(0, 3.8, 4.0, 6.6)]), ("Banyo", [(4.0, 3.8, 6.6, 6.6)])]


def t4():
    fig = plt.figure(figsize=(21, 15), dpi=150)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.62], width_ratios=[1, 1, 0.85], hspace=0.12, wspace=0.05,
                          left=0.03, right=0.985, top=0.9, bottom=0.04)
    # zemin kat
    ax = fig.add_subplot(gs[0, 0])
    eksen(ax, (-1, M_W + 1), (-3.5, M_D + 8.5), "Zemin kat: iki dükkân + konut girişi (24 m modül)")
    sokak_bandi(ax, -1, M_W + 1, -3.5, -0.2, "S1 mahalle caddesi / çarşı")
    for (x0, x1, ad) in ((0, 10, "Dükkân 1"), (14, 24, "Dükkân 2")):
        ax.add_patch(Rectangle((x0, 0), x1 - x0, M_D, fc=DUVAR, ec=DUVAR, zorder=2))
        ax.add_patch(Rectangle((x0 + 0.2, 0.2), x1 - x0 - 0.4, M_D - 0.4, fc=ODA["ticari"], ec="none", zorder=3))
        ax.text((x0 + x1) / 2, M_D / 2, f"{ad}\n{sayi((x1 - x0 - 0.4) * (M_D - 0.4), 1)} m²\n(4,5 m kat yük.)",
                ha="center", va="center", fontsize=7, zorder=4)
        ax.plot([x0 + 0.5, x1 - 0.5], [-0.05, -0.05], color=R_TICARI, lw=3, zorder=5)
    ax.add_patch(Rectangle((10, 0), 4, M_D, fc=DUVAR, ec=DUVAR, zorder=2))
    ax.add_patch(Rectangle((10.2, 0.2), 3.6, M_D - 0.4, fc=ODA["dolasim"], ec="none", zorder=3))
    for k in range(1, 18):
        yy = 6.6 + k * 0.28
        if yy < M_D - 0.3:
            ax.plot([10.3, 12.0], [yy, yy], color="#8d8478", lw=0.4, zorder=4)
    ax.add_patch(Rectangle((12.1, 7.0), 1.6, 1.8, fc="#cfd6de", ec="#777", lw=0.5, zorder=4))
    ax.text(12.9, 9.4, "asansör", ha="center", fontsize=5.5, zorder=5)
    ax.text(12, 3.4, "konut\ngirişi\nposta\nbisiklet", ha="center", va="center", fontsize=6.3, zorder=5)
    ax.add_patch(Rectangle((-1, M_D), M_W + 2, 8.5, fc=R_ORTAK_AVLU, ec="none", zorder=1))
    ax.add_patch(Rectangle((1, M_D + 1.5), 7, 5, fc="#e4dccf", ec="#8d8478", lw=0.6, zorder=2))
    ax.text(4.5, M_D + 4, "atölye / depo\n(Z, esnek)", ha="center", va="center", fontsize=6.5, zorder=3)
    for x in (13, 19, 22):
        ax.add_patch(Circle((x, M_D + 4.5), 2.0, fc=R_AGAC, ec="white", lw=0.4, alpha=0.9, zorder=3))
    ax.text(16.5, M_D + 7.6, "arka avlu: servis, ağaç, oyun (parsel içi ortak)", ha="center", fontsize=6.6, zorder=3)
    olcek_cubugu(ax, M_W - 6.5, -2.9, adim=2, n=3, h=0.25, yazi=5.5)
    # normal kat
    ax = fig.add_subplot(gs[0, 1])
    eksen(ax, (-1, M_W + 1), (-3.5, M_D + 8.5), "1.–3. kat: 2+1 · 1+1 · 2+1")
    sokak_bandi(ax, -1, M_W + 1, -3.5, -0.2, "sokak")
    n_2 = plan_ciz(ax, 0, 0, 8.5, M_D, T4_2P1, yazi=6.5)
    yans = [(a, [(8.1 - r[2], r[1], 8.1 - r[0], r[3]) for r in rr]) for a, rr in T4_2P1]
    plan_ciz(ax, 15.5, 0, 8.5, M_D, yans, yazi=6.5)
    n_1 = plan_ciz(ax, 8.5, 0, 7.0, 7.0, T4_1P1, yazi=6.3)
    ax.add_patch(Rectangle((8.5, 7.0), 7.0, 5.0, fc=DUVAR, ec=DUVAR, zorder=2))
    ax.add_patch(Rectangle((8.7, 7.2), 6.6, 4.6, fc=ODA["dolasim"], ec="none", zorder=3))
    for k in range(1, 15):
        xx = 8.9 + k * 0.28
        ax.plot([xx, xx], [9.7, 11.6], color="#8d8478", lw=0.4, zorder=4)
    ax.add_patch(Rectangle((13.4, 7.4), 1.6, 1.8, fc="#cfd6de", ec="#777", lw=0.5, zorder=4))
    ax.text(12, 8.3, "çekirdek\n(merdiven + asansör)", ha="center", va="center", fontsize=6, zorder=5)
    ax.add_patch(Rectangle((-1, M_D), M_W + 2, 8.5, fc=R_ORTAK_AVLU, ec="none", zorder=1))
    for x in (1.0, 17.0):
        ax.add_patch(Rectangle((x, M_D), 6.0, 1.4, fc="none", ec=DUVAR, lw=0.8, zorder=4))
        ax.text(x + 3, M_D + 0.7, "balkon", ha="center", va="center", fontsize=6, zorder=5)
    ax.text(M_W / 2, M_D + 5, "her daire hem sokağı hem avluyu görür (2+1'ler çift cepheli)", ha="center", fontsize=6.8)
    olcek_cubugu(ax, M_W - 6.5, -2.9, adim=2, n=3, h=0.25, yazi=5.5)
    # anahtar plan
    ax = fig.add_subplot(gs[0, 2])
    W = pm.XS[1][1] - pm.XS[1][0]
    Dd = pm.YS[4][1] - pm.YS[4][0]
    eksen(ax, (-4, W + 4), (-21, Dd + 6), "Ada içindeki yeri: açık çevre adası (ada 1,4)")
    sokak_bandi(ax, -4, W + 4, Dd, Dd + 6, "S1 · E–W mahalle caddesi / çarşı")
    sokak_bandi(ax, -4, W + 4, -6, 0, "S2 yaşam sokağı")
    ax.add_patch(Rectangle((0, 0), W, Dd, fc=R_OZEL_AVLU, ec="none", zorder=1))
    der = (Dd - pm.ORTA_BANT) / 2
    ax.add_patch(Rectangle((0, der), W, pm.ORTA_BANT, fc=R_ORTAK_AVLU, ec="none", zorder=1))
    n = round(W / pm.T4_MODUL)
    for k in range(n):
        x0 = k * W / n
        ax.add_patch(Rectangle((x0, Dd - M_D), W / n, M_D, fc=TIP_RENK["T4"], ec="white", lw=0.6, zorder=2))
        if k == 1:
            ax.add_patch(Rectangle((x0, Dd - der), W / n, der, fc="none", ec="#e07b00", lw=1.6, zorder=3))
    ax.plot([0, W], [Dd + 0.4, Dd + 0.4], color=R_TICARI, lw=2.5, zorder=3)
    m = int(W // pm.T1_GEN)
    for k in range(m):
        ax.add_patch(Rectangle((k * W / m, pm.ON_ESIK), W / m, pm.T1_EV_DER, fc=TIP_RENK["T1"], ec="white", lw=0.4, zorder=2))
    ax.text(W / 2, Dd - M_D / 2, "T4 çubuk Z+3 (köşe Z+4)", ha="center", va="center", color="white", fontsize=7, zorder=4)
    ax.text(W / 2, pm.ON_ESIK + pm.T1_EV_DER / 2, "T1 sıra evler", ha="center", va="center", fontsize=7, zorder=4)
    ax.text(W / 2, der + pm.ORTA_BANT / 2, "ortak bahçe şeridi", ha="center", va="center", fontsize=6.5, zorder=4)
    ax.text(W / 2, -7.5, "turuncu çerçeve: bu sayfadaki 24 m'lik parsel\n(5 parsel = 5 ayrı yapımcı)", ha="center",
            va="top", fontsize=7)
    olcek_cubugu(ax, 0, -19.5, adim=10, n=3, h=0.8, yazi=5.5)
    # kesit
    ax = fig.add_subplot(gs[1, 0:2])
    D2 = Dd
    ax.add_patch(Rectangle((-10, -0.35), D2 + 20, 0.35, fc="#c8e2b0", ec="none", zorder=1))
    sokak_bandi(ax, D2, D2 + 9, -0.35, 0, "")
    ax.text(D2 + 4.5, 0.3, "S1 caddenin yarısı (9 m)", ha="center", fontsize=7)
    sokak_bandi(ax, -5, 0, -0.35, 0, "")
    ax.text(-2.5, 0.3, "S2", ha="center", fontsize=7)
    H = kesit_bina(ax, D2 - M_D, D2, 4, ticari=True)
    ax.add_patch(Rectangle((D2 - M_D, H), M_D, 0.01, fc="none"))
    for k, m_ in enumerate(("dükkân (4,5 m)", "2+1 · 1+1 · 2+1", "2+1 · 1+1 · 2+1", "2+1 · 1+1 · 2+1")):
        z = ZEMIN_TICARI_YUK / 2 if k == 0 else ZEMIN_TICARI_YUK + (k - 0.5) * KAT_YUK
        ax.text(D2 - M_D / 2, z, m_, ha="center", va="center", fontsize=6.8, zorder=6)
    Ht1 = kesit_bina(ax, pm.ON_ESIK, pm.ON_ESIK + pm.T1_EV_DER, 2, kesik_ust=1)
    ax.text(pm.ON_ESIK + pm.T1_EV_DER / 2, KAT_YUK, "T1", ha="center", va="center", fontsize=7, zorder=6)
    ax.add_patch(Rectangle((D2 - der + 1.5, 0), 6, KAT_YUK, fc="#e4dccf", ec="#8d8478", lw=0.6, zorder=2))
    ax.text(D2 - der + 4.5, KAT_YUK / 2, "atölye", ha="center", va="center", fontsize=6.5, zorder=3)
    for x in (D2 - 14, D2 + 4.25):
        kesit_agac(ax, x, 0, govde=3.0, tac_r=2.4)
    insan(ax, D2 + 1.8, 0)
    insan(ax, D2 - 17, 0, cocuk=True, renk="#5a4a8a")
    gunes(ax, pm.ON_ESIK + pm.T1_EV_DER, Ht1, yon=1)
    ax.annotate("", xy=(D2 + 9.5, 0), xytext=(D2 + 9.5, H), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(D2 + 9.8, H / 2, f"{sayi(H, 1)} m", rotation=90, ha="left", va="center", fontsize=6.5)
    ax.annotate("", xy=(0, -1.6), xytext=(D2, -1.6), arrowprops=dict(arrowstyle="<->", lw=0.5))
    ax.text(D2 / 2, -1.8, f"ada derinliği {sayi(D2, 1)} m", ha="center", va="top", fontsize=7)
    eksen(ax, (-6, D2 + 12), (-3.2, 17), "Ada kesiti (güney solda, cadde kuzeyde): avlu güneşte kalır")
    ax.text(-5.5, 16.5, "Dükkânlı zemin kat 'yumuşak kat' riskidir: çekirdek perdeleri ve parsel arası duvarlar zemine kadar "
                        "kesintisiz iner\n(TBDY 2018 düzensizlik kontrolü; doğrulanmalı).", fontsize=7, va="top", color="#444")
    # tablo
    ax = fig.add_subplot(gs[1, 2])
    brut_kat = M_W * M_D
    sat = [
        ("Zemin: 2 dükkân", "2", sayi(2 * 9.6 * 11.6, 1), sayi(brut_kat - 4 * M_D, 0), "esnek: ofis, klinik, atölye"),
        ("1.–3. kat: 2+1", "6", sayi(n_2, 1), "≈ 102 + pay", "çift cepheli, balkon avluda"),
        ("1.–3. kat: 1+1", "3", sayi(n_1, 1), "49 + pay", "genç çift, yalnız yaşlı, öğrenci"),
        ("Asansör (4 durak; köşe 5)", "1", "—", "—", f"{sayi(tv.asansor_maliyeti(4) / 1e6, 1)} milyon TL [V]; "
         f"{sayi(tv.asansor_maliyeti(4) / 9 / 1e3)} bin/daire"),
        ("Parsel toplamı (Z+3)", "9 daire", sayi(2 * 9.6 * 11.6 + 6 * n_2 + 3 * n_1, 0), sayi(brut_kat * 4, 0),
         "2 dükkân + 9 daire"),
    ]
    tablo(ax, ["Birim", "Adet", "Net m²", "Brüt m²", "Not"], sat, [0, 0.36, 0.46, 0.58, 0.72],
          baslik="Alan tablosu (24 m'lik parsel)", yazi=7.4)
    ax.text(0, 0.30, f"Parsel {sayi(M_W * der)} m² · emsal {sayi(brut_kat * 4 / (M_W * der), 2)} · yapı oturumu "
                     f"%{sayi(100 * M_D / der)}", fontsize=7.4, va="top")
    _yapim4 = tv.tip_yapim_maliyeti(tv.SINIF["T4"], brut_kat * 4)
    ax.text(0, 0.03, "Ortalama brüt daire ≈ 96 m²; plan modelinde 100 m² kabul edildi.\n"
                     f"4 kat: asansör zorunlu (PAİY md. 34/1) [D]; yapımın %{sayi(100 * tv.asansor_maliyeti(4) / _yapim4, 1)}'i "
                     f"(≈ {_mtl(_yapim4)} üzerinden) [V].\nOtopark parsel dışında, mobilite noktasında.",
            fontsize=7, color="#444", va="bottom")
    baslik_yaz(fig, "T4 · Çevre adası çubuğu (zeminde dükkân)",
               f"{sayi(M_W, 0)} m cepheli küçük parseller, {sayi(M_D, 0)} m derin çubuk, Z+3 (köşede Z+4). Zemin 4,5 m dükkân; "
               f"üstte 2+1 · 1+1 · 2+1. Caddede sürekli cephe, arkada sakin avlu. Plandaki {sayi(M['tip']['T4']['konut'])} "
               "konutun tipi.")
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"tipoloji_T4_cevre_adasi.{uz}", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    pm.model()
    print("T1", t1())
    t2()
    t3()
    t4()
    print("tipolojiler yazıldı")
