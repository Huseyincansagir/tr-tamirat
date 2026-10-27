"""
Model mahalle v2.1 — deprem bölgesi için hızlı uygulama sürümü
============================================================
Aynı plan (sokak, ada, avlu grubu, merkez) korunur; yalnız kat ve yapım kurgusu
değişir: önce Z+1 (gerekirse Z+2) prefabrik çekirdekler, sonra onaylı projeyle
yerinde büyüme. Bu şema bir mühendislik projesi değildir; süreler ve sistem
seçenekleri tahminidir ve doğrulanmalıdır (TBDY 2018, zemin etüdü).

Çalıştırma:  python deprem_hizli_uygulama.py
Çıktılar  :  ../deprem_hizli_uygulama.png|svg
"""

import math
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle

import plan_modeli as pm
from ortak import CIKTI, HANE_BUYUKLUGU, KAT_YUK, R_ORTAK_AVLU, R_TICARI, TIP_RENK, insan, sayi

K = 0.62          # oblik izdüşüm katsayısı
R_A1 = "#6e4c3b"
R_A2 = "#e0a15a"
R_A0 = "#4f73a3"


G_D_ = (pm.YS[0][1] - pm.YS[0][0]) / 2


def izd(x, y, z):
    """Avlu tarafından bakış: sokak kanadı arkada kalır (y ters çevrilir)."""
    yy = G_D_ - y
    return (x + K * yy * math.cos(math.radians(38)), z + K * yy * math.sin(math.radians(38)))


def kutu(ax, x0, y0, z0, x1, y1, z1, renk, kesik=False, alpha=1.0, zorder=0):
    # avlu tarafından bakış: izleyiciye en yakın yüz y1'dedir
    on = [izd(x0, y1, z0), izd(x1, y1, z0), izd(x1, y1, z1), izd(x0, y1, z1)]
    ust = [izd(x0, y1, z1), izd(x1, y1, z1), izd(x1, y0, z1), izd(x0, y0, z1)]
    yan = [izd(x1, y1, z0), izd(x1, y0, z0), izd(x1, y0, z1), izd(x1, y1, z1)]
    ls = (0, (3, 2)) if kesik else "-"
    for yuz, ton in ((on, 1.0), (yan, 0.78), (ust, 1.18)):
        if kesik:
            fc = "none"
        else:
            import matplotlib.colors as mc
            r, g, b = mc.to_rgb(renk)
            fc = (min(r * ton, 1), min(g * ton, 1), min(b * ton, 1))
        ax.add_patch(MPoly(yuz, closed=True, fc=fc, ec="#2c2622" if not kesik else renk, lw=0.5 if not kesik else 0.9,
                           ls=ls, alpha=alpha, zorder=zorder))


def aksonometri(ax):
    G_W, G_D = 36.0, (pm.YS[0][1] - pm.YS[0][0]) / 2
    zemin = [izd(0, 0, 0), izd(G_W, 0, 0), izd(G_W, G_D, 0), izd(0, G_D, 0)]
    ax.add_patch(MPoly(zemin, closed=True, fc=R_ORTAK_AVLU, ec="#7a9a64", lw=0.6, zorder=0))
    sok = [izd(-4, -6, 0), izd(G_W + 4, -6, 0), izd(G_W + 4, 0, 0), izd(-4, 0, 0)]
    ort = [izd(-4, G_D, 0), izd(G_W + 4, G_D, 0), izd(G_W + 4, G_D + 4, 0), izd(-4, G_D + 4, 0)]
    ax.add_patch(MPoly(ort, closed=True, fc="#bcd9a0", ec="none", zorder=0))
    ax.add_patch(MPoly(sok, closed=True, fc="#e3dfd6", ec="none", zorder=0))
    kutular = []
    # yan kanatlar: aşama 1 zemin, aşama 2 üst kat
    for x0 in (0.0, G_W - 7.0):
        for k in range(2):
            y0 = 11.5 + k * 6.5
            kutular.append((x0, y0, 0, x0 + 7.0, y0 + 6.5, 3.0, R_A1, False))
            kutular.append((x0, y0, 3.0, x0 + 7.0, y0 + 6.5, 6.0, R_A2, True))
    # sokak kanadı: 3,6 m'lik modüller; Z+1 aşama 1, 2. kat aşama 2
    for i in range(10):
        x0 = i * 3.6
        for kat, renk, kesik in ((0, R_A1, False), (1, R_A1, False), (2, R_A2, True)):
            if kat == 0 and i == 4:
                continue      # kapı altı geçit
            kutular.append((x0, 1.5, kat * 3.0, x0 + 3.6, 11.5, kat * 3.0 + 3.0, renk, kesik))
    kutular.sort(key=lambda b: (b[1], b[2], b[0]))
    for n, (x0, y0, z0, x1, y1, z1, renk, kesik) in enumerate(kutular):
        kutu(ax, x0, y0, z0, x1, y1, z1, renk, kesik=kesik, zorder=n + 1)
    X, Y = izd(14.4 + 1.8, 11.5, 1.2)
    ax.text(X, Y, "kapı altı\ngeçit", ha="center", fontsize=6.5, zorder=500)
    X, Y = izd(18, G_D + 2, 0)
    ax.text(X, Y, "ada ortası ortak bahçe", ha="center", va="center", fontsize=7, zorder=1)
    for (x, y, t) in ((18, 18, "ortak avlu"),):
        X, Y = izd(x, y, 0)
        ax.text(X, Y, t, ha="center", va="center", fontsize=7.5, zorder=1)
    X, Y = izd(18, -3, 0)
    ax.text(X, Y, "S2 yaşam sokağı", ha="center", va="center", fontsize=7, zorder=1)
    # 3,6 m ızgara ölçüsü
    a, b = izd(G_W - 7.2, G_D + 0.5, 0), izd(G_W - 3.6, G_D + 0.5, 0)
    ax.text(*izd(G_W - 3.6, 12.5, 7.2), "3,6 m modül", ha="center", fontsize=6.5, zorder=600)
    for (x, y, t) in ((3.5, 24.5, "yan kanat\nZ → Z+1"), (32.5, 24.5, "yan kanat\nZ → Z+1")):
        X, Y = izd(x, y, 3.4)
        ax.text(X, Y, t, ha="center", fontsize=6.8, zorder=600, color="#2c2622")
    X, Y = izd(-1, 6, 9.5)
    ax.text(X, Y, "sokak kanadı Z+1 → Z+2", ha="left", fontsize=7, zorder=600)
    ax.set_xlim(-6, 56)
    ax.set_ylim(-3, 25)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("a · Avlu grubu, 3,6 m modüllerle (aşama 1 dolu, aşama 2 kesikli)", fontsize=10.5,
                 fontweight="bold", loc="left")


def kesit(ax):
    # radye temel + prefabrik çerçeve/panel; Z+1 çekirdek, Z+2 genişleme
    ax.add_patch(Rectangle((-2, -1.4), 18, 1.4, fc="#d6cfc3", ec="none", zorder=0))
    ax.add_patch(Rectangle((-0.5, -0.6), 11, 0.6, fc="#9a948a", ec="#555", lw=0.6, zorder=2))
    ax.text(5, -1.05, "radye temel (son durum yüküne göre)", ha="center", fontsize=7, zorder=3)
    for k in range(2):
        z = k * KAT_YUK
        ax.add_patch(Rectangle((0, z), 10, KAT_YUK, fc="#f3eee6", ec="none", zorder=1))
        ax.add_patch(Rectangle((0, z), 10, 0.22, fc="#4a3d34", ec="none", zorder=2))
        for x in (0, 4.9, 9.8):
            ax.add_patch(Rectangle((x, z), 0.2, KAT_YUK, fc="#4a3d34", ec="none", zorder=2))
    ax.add_patch(Rectangle((0, 2 * KAT_YUK), 10, 0.22, fc="#4a3d34", ec="none", zorder=2))
    ax.add_patch(Rectangle((0, 2 * KAT_YUK), 10, KAT_YUK, fc="none", ec=R_A2, lw=1.2, ls=(0, (3, 2)), zorder=3))
    ax.add_patch(MPoly([(-0.4, 3 * KAT_YUK), (10.4, 3 * KAT_YUK), (5, 3 * KAT_YUK + 2.6)], closed=True, fc="none",
                       ec=R_A2, lw=1.2, ls=(0, (3, 2)), zorder=3))
    for x in (0.1, 4.95, 9.9):
        ax.plot([x, x], [2 * KAT_YUK + 0.22, 2 * KAT_YUK + 0.8], color="#b0483f", lw=2.0, zorder=4)
    notlar = [
        (10.6, 0.8, "kısa açıklık (≤ 5 m), simetrik perdeler;\nzemin kat dükkânlıysa çekirdek perdesi zemine iner"),
        (10.6, 3.9, "prefabrik döşeme ve duvar paneli (betonarme)\nya da hafif çelik / ahşap karkas — seçenek, doğrulanmalı"),
        (10.6, 6.6, "aşama 2: aynı panellerle ek kat; bağlantı\nfilizleri ve hesap baştan (kırmızı)"),
        (10.6, 9.4, "hafif çatı ya da teras çatı (geçici)"),
    ]
    for x, y, t in notlar:
        ax.text(x, y, t, fontsize=7, va="center")
    insan(ax, 2.5, 0.22)
    ax.text(5, KAT_YUK * 0.5, "Z", ha="center", fontsize=8, zorder=5)
    ax.text(5, KAT_YUK * 1.5, "+1", ha="center", fontsize=8, zorder=5)
    ax.text(5, KAT_YUK * 2.5, "+2 (sonra)", ha="center", fontsize=8, color="#a5631f", zorder=5)
    ax.set_xlim(-2, 30)
    ax.set_ylim(-1.6, 12.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("b · Yapı kurgusu (şematik kesit)", fontsize=10.5, fontweight="bold", loc="left")


def takvim(ax):
    pos = ax.get_position()
    ax.set_position([pos.x0 + 0.20, pos.y0, pos.width - 0.20, pos.height])
    isler = [
        ("Yer seçimi, zemin etüdü (fay, sıvılaşma, taşkın)", 0, 6, R_A0),
        ("Altyapı omurgası: yol, su, kanal, elektrik", 3, 16, R_A0),
        ("Mahalle merkezi önce: okul, ASM, mescit, çarşı (modüler)", 6, 20, "#2f6f66"),
        ("Prefabrik üretim hattı ve saha", 4, 12, "#8a8a8a"),
        ("Aşama 1 konut: Z+1 çekirdekler, avlu grupları", 10, 40, R_A1),
        ("Ağaçlandırma ve komşuluk yeşilleri", 14, 44, "#5e9444"),
        ("Aşama 2: onaylı projeyle genişleme (Z+2)", 52, 156, R_A2),
    ]
    for k, (ad, a, b, renk) in enumerate(isler):
        y = len(isler) - k
        ax.add_patch(Rectangle((a, y - 0.32), b - a, 0.64, fc=renk, ec="none", zorder=2))
        ax.text(-2, y, ad, ha="right", va="center", fontsize=7.6)
    ax.set_xlim(0, 160)
    ax.set_ylim(0.3, len(isler) + 0.7)
    ax.set_yticks([])
    ax.set_xticks([0, 13, 26, 39, 52, 104, 156])
    ax.set_xticklabels(["0", "3 ay", "6 ay", "9 ay", "1 yıl", "2 yıl", "3 yıl"], fontsize=7.5)
    for x in (13, 26, 39, 52, 104):
        ax.axvline(x, color="#e5e5e5", lw=0.6, zorder=0)
    for k in ("top", "right", "left"):
        ax.spines[k].set_visible(False)
    ax.set_xlabel("hafta (tahmini; proje ölçeğinde doğrulanmalı)", fontsize=7.5)
    ax.set_title("c · Aşamalama", fontsize=10.5, fontweight="bold", loc="left")


def senaryolar():
    """Plan modelinin parsellerinden üç kat senaryosunun konut sayısı."""
    P = pm.model()
    s = {"Aşama 1 (Z+1)": 0.0, "Aşama 2 (Z+2 tavan)": 0.0, "Kalıcı plan (Z+3, köşe Z+4)": 0.0}
    for p in P["parseller"]:
        k = p["konut"]
        s["Kalıcı plan (Z+3, köşe Z+4)"] += k
        if p["tip"] == "T1":
            s["Aşama 1 (Z+1)"] += 1
            s["Aşama 2 (Z+2 tavan)"] += 1
        elif p["tip"] == "T2":
            s["Aşama 1 (Z+1)"] += 2          # zemin 2+1 + 1. kat 3+1 (dubleks sonra)
            s["Aşama 2 (Z+2 tavan)"] += 2
        elif p["tip"] == "T3":
            w = p["binalar"][0].bounds[2] - p["binalar"][0].bounds[0]
            kb = max(2, round(w * pm.T3_SOKAK_KANADI / pm.KONUT_BRUT_T3))
            z = 0 if p.get("dukkan") else kb - 1
            yan = p.get("yan_konut", 4)
            s["Aşama 1 (Z+1)"] += z + kb + yan          # yan kanatlar tek katlı 1+1
            s["Aşama 2 (Z+2 tavan)"] += z + 2 * kb + yan
        else:
            ust = max(p["kat"] - 1, 1)
            s["Aşama 1 (Z+1)"] += k * 1 / ust
            s["Aşama 2 (Z+2 tavan)"] += k * min(2, ust) / ust
    return s


def tablo(ax):
    s = senaryolar()
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("d · Aynı planın üç kat senaryosu (plan modelinden)", fontsize=10.5, fontweight="bold", loc="left")
    bas = ["Senaryo", "Konut", "Nüfus", "Brüt kişi/ha", "En yüksek"]
    xs = [0, 0.42, 0.56, 0.70, 0.86]
    y = 0.88
    for x, b in zip(xs, bas):
        ax.text(x, y, b, fontsize=8.4, fontweight="bold")
    ax.plot([0, 1], [y - 0.04] * 2, color="#333", lw=0.8)
    y -= 0.12
    en = {"Aşama 1 (Z+1)": "2 kat", "Aşama 2 (Z+2 tavan)": "3 kat", "Kalıcı plan (Z+3, köşe Z+4)": "5 kat (köşe)"}
    for k, (ad, v) in enumerate(s.items()):
        if k % 2 == 0:
            ax.add_patch(Rectangle((0, y - 0.05), 1, 0.11, fc="#f3f1ec", ec="none"))
        n = v * HANE_BUYUKLUGU
        for x, t in zip(xs, (ad, sayi(v), sayi(n), sayi(n / 60), en[ad])):
            ax.text(x, y, t, fontsize=8.4, va="center")
        y -= 0.12
    ax.text(0, 0.18, "Aşama 1 brüt yoğunluğu MPYY md. 12(4)'teki 100 kişi/ha eşiğinin altında kalabilir; bu dönemde\n"
                     "mesafe standartları 'artırılabilir' kapsamına düşer (doğrulanmalı). Aşama 2 ile hedef bandına girilir.",
            fontsize=7.4, color="#444", va="top")
    return s


def main():
    fig = plt.figure(figsize=(21, 13.5), dpi=150)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.72], width_ratios=[1.15, 1], hspace=0.18, wspace=0.10,
                          left=0.03, right=0.985, top=0.885, bottom=0.05)
    aksonometri(fig.add_subplot(gs[0, 0]))
    kesit(fig.add_subplot(gs[0, 1]))
    takvim(fig.add_subplot(gs[1, 0]))
    s = tablo(fig.add_subplot(gs[1, 1]))
    fig.text(0.03, 0.962, "Model mahalle v2.1 — deprem bölgesi için hızlı uygulama sürümü", fontsize=22, fontweight="bold")
    fig.text(0.03, 0.937,
             "Plan, sokak ve avlu grubu aynı kalır; konutlar önce Z+1 prefabrik çekirdek olarak kurulur, 1–3 yılda aynı "
             "panellerle Z+2'ye büyür. Konteyner kent yerine 'kalıcı ama hızlı' ve 'önce mahalle merkezi'.",
             fontsize=11, color="#444")
    for renk, ad, x in ((R_A1, "aşama 1 (0–12 ay)", 0.03), (R_A2, "aşama 2 (1–3 yıl, kesikli)", 0.16),
                        (R_A0, "altyapı ve hazırlık", 0.31)):
        fig.patches.append(Rectangle((x, 0.905), 0.012, 0.012, fc=renk, ec="none", transform=fig.transFigure, figure=fig))
        fig.text(x + 0.016, 0.911, ad, fontsize=9, va="center")
    fig.text(0.03, 0.015,
             "Uyarı: süreler, yapı sistemleri ve yoğunluk eşiği yorumu tahmindir; TBDY 2018, zemin etüdü ve ilgili afet "
             "mevzuatına göre mühendislik doğrulaması gerekir. Kaynak dersler: 02_LITERATUR/ornek_uygulamalar.md §3.3 "
             "(tip proje tekrarı, mahalle birleştirme riskleri).", fontsize=8.5, color="#444")
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"deprem_hizli_uygulama.{uz}", facecolor="white")
    plt.close(fig)
    print({k: round(v) for k, v in s.items()})


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
