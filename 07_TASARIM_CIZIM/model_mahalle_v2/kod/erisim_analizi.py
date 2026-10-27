"""
Model mahalle v2.1 — ağ üzerinden yürüme mesafesi kontrolü
========================================================
v2: ilkokul paneli iki okulu (A güney, B kuzey) ve kayıt alanı sınırını gösterir.
Her konut parselinin kapısından en yakın donatıya, yaya ağı (sokak eksenleri,
S3 geçitleri, yeşil diyagonaller, park içi yollar) üzerinden en kısa yürüme
mesafesi. Kuş uçuşu halka yerine gerçek ağ mesafesi kullanılır; MPYY md. 12'deki
"takriben … metre" ölçütü burada "yaya ağı mesafesi" olarak yorumlanmıştır.

Üst iki sıra: sekiz donatı için harita (konutlar mesafe sınıfına göre renkli;
hedefi aşan konutlar kırmızı çerçeveli). Alt sıra: konut ağırlıklı dağılımlar.

Çalıştırma:  python erisim_analizi.py
Çıktılar  :  ../erisim_analizi.png|svg
"""

import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch, Rectangle

import metrikler as mt
import plan_modeli as pm
from ortak import (CIKTI, HALO, MESAFE_RENK, MESAFE_SINIR, R_ASIM, R_ORTAK_YESIL, R_S2, R_ZEMIN, poligon_ciz,
                   sayi, yuzde)

M = mt.metrikleri_hesapla()
P = pm.model()

PANELLER = [
    # (tür, başlık, hedef, ek kural)
    ("ilkokul", "İlkokul (A + B)", 500, None),
    ("mescit", "Mescit (ibadet kademeleri)", 150, "ibadet"),
    ("yesil05", "≥ 0,5 ha kamusal yeşil", 300, None),
    ("durak", "Otobüs durağı", 400, None),
    ("anaokulu_kres", "Anaokulu ya da kreş", 400, None),
    ("asm", "Aile sağlık merkezi", 500, None),
    ("dukkan", "Bakkal, fırın ya da dükkân", 300, None),
    ("otopark", "Mobilite noktası (bölgesel otopark)", 400, None),
]


def _renk(m):
    for k in range(len(MESAFE_SINIR) - 1):
        if m <= MESAFE_SINIR[k + 1]:
            return MESAFE_RENK[k]
    return MESAFE_RENK[-1]


def _halkalar(g):
    parcalar = [g] if g.geom_type == "Polygon" else list(g.geoms)
    return [np.asarray(p.exterior.coords) for p in parcalar]


def taban(ax):
    ax.add_patch(Rectangle((0, 0), pm.GEN, pm.YUK, fc=R_S2, ec="none", zorder=0))
    for d in P["donatilar"]:
        renk = R_ORTAK_YESIL if d["tur"] in ("park", "spor", "cep", "bostan") else "#d3d0c9"
        poligon_ciz(ax, d["poly"], renk, zorder=1)
    for g in P["cep"]:
        poligon_ciz(ax, g, R_ORTAK_YESIL, zorder=1)
    poligon_ciz(ax, pm.DIYAG_BANT, "#efe6d2", zorder=1.1)
    poligon_ciz(ax, pm.MEYDAN, "#ead9b8", zorder=1.1)
    ax.set_xlim(-5, pm.GEN + 5)
    ax.set_ylim(-5, pm.YUK + 5)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#999")
        s.set_linewidth(0.5)


def harita(ax, tur, baslik, hedef, kural):
    taban(ax)
    liste = pm.konut_mesafeleri(tur)
    asim_kural = None
    if kural == "ibadet":
        kc = [m for _, m in pm.konut_mesafeleri("kucuk_cami")]
        sc = [m for _, m in pm.konut_mesafeleri("semt_camii")]
        asim_kural = [not (m <= 150 or a <= 250 or b <= 400) for (_, m), a, b in zip(liste, kc, sc)]
    polys, renkler, asim = [], [], []
    for n, (p, m) in enumerate(liste):
        for h in _halkalar(p["poly"]):
            polys.append(h)
            renkler.append(_renk(m))
        kotu = asim_kural[n] if asim_kural is not None else m > hedef
        if kotu:
            asim += _halkalar(p["poly"])
    ax.add_collection(PolyCollection(polys, facecolors=renkler, edgecolors="white", linewidths=0.15, zorder=2))
    if asim:
        ax.add_collection(PolyCollection(asim, facecolors="none", edgecolors=R_ASIM, linewidths=0.9, zorder=3))
    # hedef noktaları
    A = pm.ag_kur()
    for kim in A["hedefler"].get(tur, []):
        if kim[0] == "konut":
            continue
        dugum, _ = A["erisim"][kim]
        ax.plot(*dugum, marker="o", ms=3.2, mfc="#111", mec="white", mew=0.4, zorder=4)
    if kural == "ibadet":
        for t in ("kucuk_cami", "semt_camii"):
            for kim in A["hedefler"].get(t, []):
                dugum, _ = A["erisim"][kim]
                ax.plot(*dugum, marker="s", ms=4.5, mfc="#2f6f66", mec="white", mew=0.5, zorder=4)
    if tur == "ilkokul":
        la, lb = pm.konut_mesafeleri("ilkokul_A"), pm.konut_mesafeleri("ilkokul_B")
        b_poly = [h for (p, a), (_, b) in zip(la, lb) if b < a for h in _halkalar(p["poly"])]
        if b_poly:
            ax.add_collection(PolyCollection(b_poly, facecolors="none", edgecolors="#f2b134", linewidths=0.55,
                                             zorder=2.5))
        for d in P["donatilar"]:
            if d.get("okul"):
                c = d["poly"].representative_point()
                ax.text(c.x, c.y, d["okul"], ha="center", va="center", fontsize=13, fontweight="bold", color="#1b2f4d",
                        zorder=5, path_effects=HALO)
        ax.text(0.01, 0.01, "sarı çerçeve: en yakın okulu B olan konut (kayıt alanı)", transform=ax.transAxes,
                fontsize=7.2, color="#7a5a00", va="bottom", bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))
    e = M["erisim"][tur]
    agirlik = sum(p["konut"] for p, _ in liste)
    pay = sum(p["konut"] for p, m in liste if m <= hedef) / agirlik
    alt = f"%{sayi(100 * pay, 1)} konut ≤ {sayi(hedef)} m · medyan {sayi(e['medyan'])} m · en uzak {sayi(e['en_fazla'])} m"
    if kural == "ibadet":
        alt = (f"mescit ≤ 150 m: %{sayi(100 * pay, 1)} · kademeli kural*: "
               f"%{sayi(100 * M['erisim']['ibadet_kademe']['pay_hedef'], 1)}")
    ax.set_title(baslik, fontsize=11, fontweight="bold", loc="left", pad=16)
    ax.text(0, 1.012, alt, transform=ax.transAxes, fontsize=8.3, color="#333", va="bottom")
    asan = sum(p["konut"] for (p, m), k in zip(liste, asim_kural or [m > hedef for _, m in liste]) if k)
    if asan:
        ax.text(0.99, 0.01, f"hedefi aşan: {sayi(asan)} konut", transform=ax.transAxes, ha="right", va="bottom",
                fontsize=7.5, color=R_ASIM, fontweight="bold",
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))


def dagilim(ax, tur, baslik, hedef, ust):
    liste = pm.konut_mesafeleri(tur)
    m = np.array([x for _, x in liste])
    w = np.array([p["konut"] for p, _ in liste], dtype=float)
    kutu = np.arange(0, 725, 25)
    h, _ = np.histogram(np.clip(m, 0, 699), bins=kutu, weights=w)
    renk = [_renk(x + 12.5) for x in kutu[:-1]]
    ax.bar(kutu[:-1] + 12.5, h, width=23, color=renk, edgecolor="none", zorder=2)
    ax.axvline(hedef, color="#222", lw=1.1, zorder=3)
    ax.text(hedef + 6, ax.get_ylim()[1] * 0.95, f"hedef {sayi(hedef)} m", fontsize=7.5, va="top")
    if ust and ust != hedef:
        ax.axvline(ust, color="#222", lw=0.8, ls=(0, (3, 2)), zorder=3)
        ax.text(ust + 6, ax.get_ylim()[1] * 0.80, f"{sayi(ust)} m", fontsize=7.5, va="top")
    ax.set_xlim(0, 700)
    ax.set_xlabel("ağ üzerinden yürüme mesafesi (m)", fontsize=8)
    ax.set_ylabel("konut sayısı", fontsize=8)
    ax.tick_params(labelsize=7.5)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    ax.grid(axis="y", color="#e5e5e5", lw=0.6, zorder=0)
    ax.set_title(baslik, fontsize=10, fontweight="bold", loc="left")


def main():
    fig = plt.figure(figsize=(22, 15.0), dpi=150)
    gs = fig.add_gridspec(3, 4, height_ratios=[1, 1, 0.46], hspace=0.20, wspace=0.06,
                          left=0.03, right=0.985, top=0.87, bottom=0.055)
    for k, (tur, baslik, hedef, kural) in enumerate(PANELLER):
        ax = fig.add_subplot(gs[k // 4, k % 4])
        harita(ax, tur, baslik, hedef, kural)
    for k, (tur, baslik, hedef, ust) in enumerate((("ilkokul", "İlkokul (A + B)", 500, 400),
                                                   ("mescit", "Mescit", 150, None),
                                                   ("yesil05", "≥ 0,5 ha yeşil", 200, 300),
                                                   ("durak", "Otobüs durağı", 300, 400))):
        ax = fig.add_subplot(gs[2, k])
        dagilim(ax, tur, baslik + " — konut ağırlıklı dağılım", hedef, ust)
        if k:
            ax.set_ylabel("")

    fig.text(0.03, 0.958, "Model mahalle v2.1 — yaya ağı üzerinden erişim", fontsize=22, fontweight="bold")
    fig.text(0.03, 0.935,
             f"{sayi(M['konut'])} konutun her biri için kapıdan en yakın donatıya en kısa yol (sokak eksenleri, S3 geçitleri, "
             "yeşil diyagonaller, park içi yollar). Kuş uçuşu halka kullanılmamıştır. Siyah nokta: donatı girişi.",
             fontsize=11, color="#444")
    # ortak renk lejantı
    el = []
    for k in range(len(MESAFE_RENK)):
        a, b = MESAFE_SINIR[k], MESAFE_SINIR[k + 1]
        et = f"{sayi(a)}–{sayi(b)} m" if b < 10_000 else f"> {sayi(a)} m"
        el.append(Patch(fc=MESAFE_RENK[k], ec="none", label=et))
    el.append(Patch(fc="white", ec=R_ASIM, lw=1.2, label="hedefi aşan konut"))
    fig.legend(handles=el, loc="upper left", bbox_to_anchor=(0.03, 0.925), ncol=len(el), fontsize=9, frameon=False,
               handlelength=1.6, columnspacing=1.4)
    fig.text(0.03, 0.012,
             "* Kademeli ibadet kuralı: mescit ≤ 150 m ya da küçük cami ≤ 250 m ya da semt camii ≤ 400 m (MPYY md. 12 kademeleri; "
             "PAİY md. 53: 250 m içinde cami varsa mescit şartı aranmaz). Mescit, kreş, bakkal ve çeşme konumları aynı ağ üzerinde "
             "açgözlü kapsama ile seçilmiştir (plan_modeli.py, _zemin_sec).",
             fontsize=8.5, color="#444")
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"erisim_analizi.{uz}", facecolor="white")
    plt.close(fig)
    print("erisim_analizi.png|svg yazıldı")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
