"""
Model mahalle v1 — dört sokak tipinin ölçekli kesitleri
======================================================
Toplayıcı yol (24 m) · S1 mahalle caddesi / çarşı (18 m) · S2 yaşam sokağı (10 m) ·
S3 yaya ara sokağı (6 m). Kesitler güney (solda) – kuzey (sağda) doğrultusundadır,
yani D–B uzanan sokakları keser; öğle güneşi soldan gelir. Her kesitte:
şerit genişlikleri, kaldırım, ağaç, bina yüksekliği, H/W oranı ve İstanbul (41°K)
için 21 Aralık (25,6°) ve 21 Mart (49,0°) öğle güneş ışınları çizilir.

Bütün kesitler aynı ölçektedir (1 birim = 1 m).

Çalıştırma:  python sokak_kesitleri.py
Çıktılar  :  ../sokak_kesitleri.png|svg
"""

import math
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon as MPoly, Rectangle

from ortak import (ARALIK_ACI, CIKTI, KAT_YUK, MART_ACI, R_AGAC, R_GOLGE, R_GUNES, R_ORTAK_YESIL, R_TICARI,
                   ZEMIN_TICARI_YUK, golge, insan, kesit_agac, olcu_cizgisi, sayi)

# yüzey renkleri
YUZEY = {
    "kaldirim": "#cfcac1", "bisiklet": "#c9907d", "agac": "#a9cf8f", "serit": "#8f8b85", "refuj": "#a9cf8f",
    "paylasim": "#d9d0bf", "yaya": "#e3dccd", "park": "#bdb6aa", "bahce": "#c8e2b0", "yagmur": "#9cc59a",
    "oturma": "#e3dccd", "yesil": "#a9cf8f",
}
R_IC = "#f3eee6"
R_DUVAR = "#4a3d34"

KESITLER = [
    dict(
        kod="A–A", ad="Toplayıcı yol (mahalle dışı)", genislik=24.0, hiz="50 km/s (öneri; doğrulanmalı)",
        hedef_hw="1:1,5–1:2,5 (0,40–0,67)", konum="güney kenarı, ada (2,0) önü",
        bilesen=[("kaldırım", 3.0, "kaldirim"), ("bisiklet", 2.0, "bisiklet"), ("ağaç / park", 2.5, "agac"),
                 ("şerit", 3.25, "serit"), ("refüj", 2.5, "refuj"), ("şerit", 3.25, "serit"),
                 ("ağaç / park", 2.5, "agac"), ("bisiklet", 2.0, "bisiklet"), ("kaldırım", 3.0, "kaldirim")],
        sol=dict(ad="komşu mahalle çevre adası (varsayım)", kat=4, ticari=True, on=0.0, derin=12, cati="duz", gri=True),
        sag=dict(ad="T4 çevre adası çubuğu Z+3, zeminde dükkân", kat=4, ticari=True, on=0.0, derin=12, cati="duz"),
        tasit=[("otobus", 4), ("araba", 6)], bordur=0.15,
    ),
    dict(
        kod="B–B", ad="S1 · mahalle caddesi / çarşı", genislik=18.0, hiz="30 km/s",
        hedef_hw="0,7–0,8 (§9.6)", konum="E–W cadde, ada (1,4) ile (1,5) arası",
        bilesen=[("kaldırım", 3.75, "kaldirim"), ("ağaç/durak", 2.0, "agac"), ("şerit", 3.25, "serit"),
                 ("şerit", 3.25, "serit"), ("ağaç/park", 2.0, "agac"), ("kaldırım", 3.75, "kaldirim")],
        sol=dict(ad="T4 çubuk Z+3, zeminde dükkân", kat=4, ticari=True, on=0.0, derin=12, cati="duz"),
        sag=dict(ad="T3 avlu grubu sokak kanadı Z+3, zeminde dükkân", kat=4, ticari=True, on=1.5, derin=10, cati="duz"),
        tasit=[("otobus", 2), ("bisiklet", 3)], bordur=0.15,
    ),
    dict(
        kod="C–C", ad="S2 · yaşam sokağı (paylaşımlı yüzey)", genislik=10.0, hiz="≤ 20 km/s (yürüme hızı)",
        hedef_hw="0,7–1,0 (§9.6)", konum="T12 adaları arası D–B sokak",
        bilesen=[("yaya", 2.0, "yaya"), ("ağaç/park", 2.0, "agac"), ("paylaşımlı yüzey", 4.0, "paylasim"),
                 ("yaya", 2.0, "yaya")],
        sol=dict(ad="T2 çok kuşaklı ev Z+2", kat=3, ticari=False, on=2.0, derin=11, cati="egik"),
        sag=dict(ad="T1 büyüyebilen ev: Z+1 çekirdek (teras çatı) + Z+2 genişleme", kat=2, ek_kat=1, ticari=False,
                 on=2.0, derin=9, cati="duz"),
        tasit=[("cocuk", 2)], bordur=0.0,
    ),
    dict(
        kod="D–D", ad="S3 · yaya ara sokağı / avlu geçidi", genislik=6.0, hiz="araçsız (acil durum aracı geçebilir)",
        hedef_hw="1,0–1,5 (UDC)", konum="avlu grupları arası geçit",
        bilesen=[("yağmur", 1.5, "yagmur"), ("yürüme", 3.0, "yaya"), ("oturma", 1.5, "oturma")],
        sol=dict(ad="T3 yan kanat Z+1 (dubleks)", kat=2, ticari=False, on=0.0, derin=7, cati="duz"),
        sag=dict(ad="T3 sokak kanadı Z+2", kat=3, ticari=False, on=0.0, derin=10, cati="duz"),
        tasit=[], bordur=0.0,
    ),
]


def sacak(b):
    if b["ticari"]:
        return ZEMIN_TICARI_YUK + (b["kat"] - 1) * KAT_YUK
    return b["kat"] * KAT_YUK


def bina_ciz(ax, x_cephe, yon, b):
    """yon=-1: bina cephenin solunda (güney), +1: sağında (kuzey)."""
    d = b["derin"]
    xa, xb = (x_cephe - d, x_cephe) if yon < 0 else (x_cephe, x_cephe + d)
    H = sacak(b)
    gri = b.get("gri")
    ic = "#ecebe8" if gri else R_IC
    duvar = "#8d8a84" if gri else R_DUVAR
    ax.add_patch(Rectangle((xa, 0), d, H, fc=ic, ec="none", zorder=3))
    # döşemeler
    z = 0.0
    katlar = [ZEMIN_TICARI_YUK if b["ticari"] else KAT_YUK] + [KAT_YUK] * (b["kat"] - 1)
    for k, kh in enumerate(katlar):
        ax.add_patch(Rectangle((xa, z), d, 0.25, fc=duvar, ec="none", zorder=4))
        # pencere (sokak cephesinde)
        if not (k == 0 and b["ticari"]):
            wx = x_cephe - 0.28 if yon < 0 else x_cephe
            ax.add_patch(Rectangle((wx, z + 0.95), 0.28, 1.45, fc="#bcd3e6", ec="none", zorder=5))
        z += kh
    ax.add_patch(Rectangle((xa, H - 0.25), d, 0.25, fc=duvar, ec="none", zorder=4))
    # dış duvarlar
    for xw in (xa, xb - 0.28):
        ax.add_patch(Rectangle((xw, 0), 0.28, H, fc=duvar, ec="none", zorder=4.5))
    if b["ticari"]:
        wx = x_cephe - 0.28 if yon < 0 else x_cephe
        ax.add_patch(Rectangle((wx, 0.25), 0.28, ZEMIN_TICARI_YUK - 0.8, fc="#bcd3e6", ec="none", zorder=5))
        ax.add_patch(Rectangle((xa, 0), d, ZEMIN_TICARI_YUK, fc="none", ec=R_TICARI, lw=1.6, zorder=6))
        # tente
        tx = x_cephe if yon < 0 else x_cephe
        ax.plot([tx, tx - yon * 1.4], [ZEMIN_TICARI_YUK - 0.6, ZEMIN_TICARI_YUK - 1.1], color=R_TICARI, lw=2, zorder=6)
    # çatı
    if b["cati"] == "egik":
        ax.add_patch(MPoly([(xa - 0.4, H), (xb + 0.4, H), ((xa + xb) / 2, H + d * 0.5 * math.tan(math.radians(30)))],
                           closed=True, fc="#9a5b3c" if not gri else "#b9b5ae", ec="none", zorder=4))
    else:
        ax.add_patch(Rectangle((xa, H), 0.25, 0.9, fc=duvar, ec="none", zorder=4))
        ax.add_patch(Rectangle((xb - 0.25, H), 0.25, 0.9, fc=duvar, ec="none", zorder=4))
    if b.get("ek_kat"):
        h2 = KAT_YUK * b["ek_kat"]
        ax.add_patch(Rectangle((xa, H), d, h2, fc="none", ec=R_DUVAR, lw=1.0, ls=(0, (3, 2)), zorder=6))
        ax.add_patch(MPoly([(xa - 0.4, H + h2), (xb + 0.4, H + h2),
                            ((xa + xb) / 2, H + h2 + d * 0.5 * math.tan(math.radians(30)))],
                           closed=True, fc="none", ec="#9a5b3c", lw=1.0, ls=(0, (3, 2)), zorder=6))
        ax.text((xa + xb) / 2, H + h2 / 2, "genişleme\npayı", ha="center", va="center", fontsize=6.8, color=R_DUVAR,
                zorder=7)
    return H, (xa, xb)


def tasit_ciz(ax, tur, x, z):
    if tur == "araba":
        ax.add_patch(FancyBboxPatch((x - 0.9, z + 0.25), 1.8, 1.25, boxstyle="round,pad=0,rounding_size=0.35",
                                    fc="#6d6a66", ec="none", zorder=7))
        for dx in (-0.6, 0.6):
            ax.add_patch(Circle((x + dx, z + 0.3), 0.3, fc="#2c2a28", ec="none", zorder=7.1))
    elif tur == "otobus":
        ax.add_patch(FancyBboxPatch((x - 1.27, z + 0.3), 2.55, 2.9, boxstyle="round,pad=0,rounding_size=0.3",
                                    fc="#1f5fa8", ec="none", zorder=7))
        ax.add_patch(Rectangle((x - 1.0, z + 1.6), 2.0, 1.1, fc="#bcd3e6", ec="none", zorder=7.1))
        ax.text(x, z + 1.0, "otobüs", ha="center", va="center", fontsize=5.5, color="white", zorder=7.2)
    elif tur == "bisiklet":
        ax.add_patch(Circle((x, z + 0.35), 0.35, fc="none", ec="#333", lw=1, zorder=7))
        insan(ax, x, z + 0.55, boy=1.55)
    elif tur == "cocuk":
        insan(ax, x - 0.8, z, cocuk=True, renk="#5a4a8a")
        insan(ax, x + 0.6, z, cocuk=True, renk="#8a4a5a")
        ax.add_patch(Circle((x + 1.4, z + 0.12), 0.12, fc="#e07b00", ec="none", zorder=8))


def kesit_ciz(ax, K):
    W_yol = K["genislik"]
    x0 = -W_yol / 2
    zemin_y = -0.6
    ax.add_patch(Rectangle((-30, zemin_y - 1.4), 60, 1.4, fc="#d6cfc3", ec="none", zorder=1))
    # bileşenler
    x = x0
    merkezler = []
    for ad, g, tur in K["bilesen"]:
        yukseklik = K["bordur"] if tur in ("kaldirim", "agac", "bisiklet", "yaya", "oturma") and K["bordur"] else 0.0
        if tur in ("bisiklet",) and K["bordur"]:
            yukseklik = 0.08
        ax.add_patch(Rectangle((x, zemin_y), g, -zemin_y + yukseklik, fc=YUZEY[tur], ec="white", lw=0.4, zorder=2))
        merkezler.append((x + g / 2, ad, g, tur, yukseklik))
        x += g
    # ağaç, insan
    for k, (cx, ad, g, tur, yk) in enumerate(merkezler):
        if tur in ("agac", "refuj"):
            kesit_agac(ax, cx, yk, govde=3.2 if W_yol > 12 else 2.6, tac_r=2.6 if W_yol > 12 else 2.0)
        if tur in ("kaldirim", "yaya") and g >= 2.0:
            insan(ax, cx + (0.3 if k % 2 else -0.3), yk, renk="#3b3b3b")
        if tur == "oturma":
            ax.add_patch(Rectangle((cx - 0.5, 0), 1.0, 0.45, fc="#8a6a4a", ec="none", zorder=6))
            insan(ax, cx + 0.2, 0.0, boy=1.25, renk="#555")
        if tur == "yagmur":
            ax.plot([cx - 0.5, cx, cx + 0.5], [0.0, -0.25, 0.0], color="#4f8fc0", lw=1.2, zorder=5)
            ax.add_patch(Circle((cx, 0.6), 0.6, fc=R_AGAC, ec="none", alpha=0.8, zorder=5))
    seritler = [m for m in merkezler if m[3] in ("serit", "paylasim")]
    for (tur, sira) in K["tasit"]:
        cx, _, _, _, yk = merkezler[sira - 1]
        tasit_ciz(ax, tur, cx, 0.0)
    # binalar
    sol, sag = K["sol"], K["sag"]
    xs = x0 - sol["on"]
    xn = x0 + W_yol + sag["on"]
    if sol["on"] > 0:
        ax.add_patch(Rectangle((xs, 0), sol["on"], 0.05, fc=YUZEY["bahce"], ec="none", zorder=2))
        kesit_agac(ax, xs + sol["on"] / 2, 0, govde=1.0, tac_r=0.8)
        ax.plot([x0, x0], [0, 0.9], color="#6b5a45", lw=1.5, zorder=5)    # alçak bahçe duvarı / çit
    if sag["on"] > 0:
        ax.add_patch(Rectangle((x0 + W_yol, 0), sag["on"], 0.05, fc=YUZEY["bahce"], ec="none", zorder=2))
        kesit_agac(ax, x0 + W_yol + sag["on"] / 2, 0, govde=1.0, tac_r=0.8)
        ax.plot([x0 + W_yol] * 2, [0, 0.9], color="#6b5a45", lw=1.5, zorder=5)
    Hs, (sa, sb) = bina_ciz(ax, xs, -1, sol)
    Hn, (na, nb) = bina_ciz(ax, xn, +1, sag)
    # arka bahçe / avlu işareti
    ax.add_patch(Rectangle((-30, 0), sa + 30, 0.05, fc=YUZEY["bahce"], ec="none", zorder=2))
    ax.add_patch(Rectangle((nb, 0), 30 - nb, 0.05, fc=YUZEY["bahce"], ec="none", zorder=2))
    W = xn - xs
    # güneş ışınları (güney binanın kuzey saçağından)
    sonuc = {}
    for aci, renk, ad, lw in ((ARALIK_ACI, R_GOLGE, "21 Ara", 1.3), (MART_ACI, R_GUNES, "21 Mar", 1.1)):
        uz = golge(Hs, aci)
        if uz <= W:
            x_son, z_son = xs + uz, 0.0
            karsi = 0.0
        else:
            x_son = xn
            z_son = Hs - W * math.tan(math.radians(aci))
            karsi = z_son
        ax.plot([xs, x_son], [Hs, z_son], color=renk, lw=lw, ls=(0, (5, 2)), zorder=9)
        # ışının üstünden gelen güneş oku
        L = 7.5 if ad == "21 Mar" else 5.5
        ax.annotate("", xy=(xs, Hs), xytext=(xs - L * math.cos(math.radians(aci)), Hs + L * math.sin(math.radians(aci))),
                    arrowprops=dict(arrowstyle="-|>", color=renk, lw=lw), zorder=9)
        ax.text(xs - L * math.cos(math.radians(aci)) - 0.3, Hs + L * math.sin(math.radians(aci)) + 0.2,
                f"{ad} öğle {sayi(aci, 1)}°", fontsize=7.3, color=renk if renk != R_GUNES else "#9a6d00", ha="right",
                va="bottom", zorder=9)
        if karsi > 0:
            ax.plot([xn + 0.15, xn + 0.15], [0, karsi], color=renk, lw=3.5, alpha=0.55, solid_capstyle="butt", zorder=8)
        else:
            ax.plot([xs, x_son], [0.12, 0.12], color=renk, lw=3, alpha=0.45, solid_capstyle="butt", zorder=8)
        sonuc[ad] = (uz, karsi)
    # ölçüler
    y_olcu = -2.6
    x = x0
    for ad, g, tur in K["bilesen"]:
        ax.annotate("", xy=(x, y_olcu), xytext=(x + g, y_olcu),
                    arrowprops=dict(arrowstyle="-", color="#555", lw=0.5), zorder=10)
        ax.plot([x, x], [y_olcu - 0.2, y_olcu + 0.2], color="#555", lw=0.5, zorder=10)
        ax.text(x + g / 2, y_olcu - 0.35, f"{sayi(g, 2 if g % 0.5 else 1)}", ha="center", va="top", fontsize=7, zorder=10)
        dar = g < 2.6
        sira = sum(1 for _ in range(0))
        ax.text(x + g / 2, y_olcu + (0.3 if not dar or (int(round(x * 4)) // 1) % 2 == 0 else 0.3), ad, ha="center",
                va="bottom", fontsize=6.0 if dar else 6.6, color="#444", zorder=10,
                rotation=0 if g >= 2.0 else 90)
        x += g
    ax.plot([x, x], [y_olcu - 0.2, y_olcu + 0.2], color="#555", lw=0.5, zorder=10)
    olcu_cizgisi(ax, x0, x0 + W_yol, -4.6, f"kamusal yol {sayi(W_yol, 1)} m", yazi=7.5, ust=False)
    if abs(W - W_yol) > 0.01:
        olcu_cizgisi(ax, xs, xn, -6.0, f"cephe arası W = {sayi(W, 1)} m", yazi=7.5, ust=False)
    # yükseklik ölçüleri
    for xh, H, yon in ((sa - 1.2, Hs, -1), (nb + 1.2, Hn, 1)):
        ax.annotate("", xy=(xh, 0), xytext=(xh, H), arrowprops=dict(arrowstyle="<->", color="#333", lw=0.6), zorder=10)
        ax.text(xh + (-0.3 if yon < 0 else 0.3), H / 2, f"H = {sayi(H, 1)} m", rotation=90, ha="right" if yon < 0 else "left",
                va="center", fontsize=7.5, zorder=10)
    for (a_, b_, ad_, hz) in ((sa, sb, sol["ad"], "right"), (na, nb, sag["ad"], "left")):
        ax.text(b_ if hz == "right" else a_, -1.3, ad_, ha=hz, va="center", fontsize=7.2, color="#333", zorder=10,
                style="italic")
    ax.text(-29.5, 18.6, "G (güney)", fontsize=8, fontweight="bold", va="top")
    ax.text(29.5, 18.6, "K (kuzey)", fontsize=8, fontweight="bold", va="top", ha="right")
    ax.set_xlim(-30, 30)
    ax.set_ylim(-7.2, 19)
    ax.set_aspect("equal")
    ax.axis("off")
    # ölçek çubuğu
    for i in range(5):
        ax.add_patch(Rectangle((19 + i * 2, -6.9), 2, 0.35, fc="#222" if i % 2 == 0 else "white", ec="#222", lw=0.5,
                               zorder=10))
    ax.text(19, -6.3, "0", fontsize=6.5, ha="center")
    ax.text(29, -6.3, "10 m", fontsize=6.5, ha="center")
    H_ort = (Hs + Hn) / 2
    ek = KAT_YUK * (sol.get("ek_kat", 0) + sag.get("ek_kat", 0)) / 2
    return dict(W=W, Hs=Hs, Hn=Hn, HW=H_ort / W, HW_son=(H_ort + ek) / W if ek else None, sonuc=sonuc)


def tablo(ax, K, R):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    satir = [
        ("Kamusal yol genişliği", f"{sayi(K['genislik'], 1)} m"),
        ("Cephe arası (W)", f"{sayi(R['W'], 1)} m"),
        ("Saçak yüksekliği G / K", f"{sayi(R['Hs'], 1)} / {sayi(R['Hn'], 1)} m"),
        ("H/W (ortalama saçak)", f"{sayi(R['HW'], 2)}" + (f" (son durum {sayi(R['HW_son'], 2)})" if R["HW_son"] else "")),
        ("Hedef H/W", K["hedef_hw"]),
        ("Tasarım hızı", K["hiz"]),
        ("21 Ara. öğle: gölge boyu", f"{sayi(R['sonuc']['21 Ara'][0], 1)} m"),
        ("   karşı cephede gölge", f"{sayi(R['sonuc']['21 Ara'][1], 1)} m yüksekliğe kadar" if R['sonuc']['21 Ara'][1] > 0
         else "yok (cephe güneşte)"),
        ("21 Mar. öğle: gölge boyu", f"{sayi(R['sonuc']['21 Mar'][0], 1)} m"),
        ("   karşı cephede gölge", f"{sayi(R['sonuc']['21 Mar'][1], 1)} m yüksekliğe kadar" if R['sonuc']['21 Mar'][1] > 0
         else "yok (cephe güneşte)"),
        ("MPYY 26/5-b K = (Y1+Y2)/2 + 7*", f"{sayi((R['Hs'] + R['Hn']) / 2 + 7, 1)} m (plan: {sayi(R['W'], 1)} m)"),
        ("Plandaki yeri", K["konum"]),
    ]
    ax.text(0.0, 0.97, f"{K['kod']}  {K['ad']}", fontsize=11.5, fontweight="bold", va="top")
    y = 0.84
    for k, (a, b) in enumerate(satir):
        if k % 2 == 0:
            ax.add_patch(Rectangle((0, y - 0.035), 1, 0.07, fc="#f3f1ec", ec="none"))
        ax.text(0.01, y, a, fontsize=8.2, va="center")
        ax.text(0.56, y, b, fontsize=8.2, va="center", family="DejaVu Sans" if len(b) > 22 else "DejaVu Sans Mono",
                wrap=True)
        y -= 0.07


def main():
    fig = plt.figure(figsize=(21, 24), dpi=150)
    gs = fig.add_gridspec(4, 2, width_ratios=[1, 0.36], hspace=0.10, wspace=0.03,
                          left=0.02, right=0.985, top=0.935, bottom=0.04)
    sonuclar = []
    for k, K in enumerate(KESITLER):
        ax = fig.add_subplot(gs[k, 0])
        R = kesit_ciz(ax, K)
        sonuclar.append(R)
        ax_t = fig.add_subplot(gs[k, 1])
        tablo(ax_t, K, R)
    fig.text(0.02, 0.968, "Model mahalle v1 — sokak kesitleri", fontsize=24, fontweight="bold")
    fig.text(0.02, 0.950,
             "Dört sokak tipi, aynı ölçekte (ölçek çubuğu 10 m). Güney solda, kuzey sağda; ışınlar güney cephenin saçağından "
             "çizildi (İstanbul 41°K). Mavi: 21 Aralık, sarı: 21 Mart öğle.",
             fontsize=11.5, color="#444")
    fig.text(0.02, 0.018,
             "* MPYY md. 26(5)(b) formülü yalnız kat adedini artıran plan değişikliklerinde aranır; yeni planda bu kesitlerin "
             "Md. 30 kapsamındaki kentsel tasarım projesiyle tanımlanabileceği hukuki görüşle doğrulanmalıdır. "
             "Kat yüksekliği 3,0 m (ticari zemin 4,5 m); PAİY md. 28 üst sınırı 3,60 m'dir.",
             fontsize=9, color="#444")
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"sokak_kesitleri.{uz}", facecolor="white")
    plt.close(fig)
    for K, R in zip(KESITLER, sonuclar):
        print(K["kod"], K["ad"], f"W={R['W']:.1f} H/W={R['HW']:.2f}", R["sonuc"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
