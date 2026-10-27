"""
Model mahalle v2.1 — ilkokula ≤ 500 m için üç seçeneğin karşılaştırması (şematik ağ)
================================================================================
v1 açık sorusu 1: tek ilkokulla %100 erişim için (a) alanı 52–55 ha'ya indirmek, (b) ikinci küçük
ilkokul şubesi, (c) kare yerine daha kompakt ya da uzun biçim. Seçenekler aynı kurallarla üretilmiş
şematik bir yaya ağında karşılaştırılır:

  * ada 119,7 × 62,8 m, 10 m S2, 18 m artı biçimli cadde, köşelerden meydana yeşil diyagonaller,
    çevrede toplayıcı yolun iç kaldırımı; merkezde ≈ 3,7 ha donatı (meydan, cami, okul, park) konutsuz
  * konut kapıları D–B sokak eksenlerinin iki yanında 6,6 m arayla (eşit ağırlık)
  * okul kapıları v1/v2 planındaki yerleriyle aynı göreli konumda

Şematik ağ önce v1 planıyla kalibre edilir (v1 kurgusu: tam modelde %96,8). Seçilen seçenek (b) tam
modelde (plan_modeli.py) ayrıca doğrulanır. Bu karşılaştırmadaki sayılar şematiktir; plan sayısı değildir.

Çalıştırma:  python okul_secenekleri.py
Çıktılar  :  ../okul_secenekleri.png|svg
"""

import math
import sys

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon as MPoly, Rectangle
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

import metrikler as mt
from ortak import CIKTI, HALO, MESAFE_RENK, MESAFE_SINIR, R_ASIM, sayi

ADA_X, ADA_Y, S2, CADDE, TY, YAYA = 119.67, 62.8, 10.0, 18.0, 12.0, 10.5
KONUT = 2200                       # karşılaştırma için sabit konut sayısı (v2 planına yakın)
HANE = 3.2


def _eksenler(a0, a1, ada, sokak):
    """a0–a1 aralığına sığan adaların arasındaki sokak eksenleri."""
    n = max(1, round((a1 - a0 + sokak) / (ada + sokak)))
    b = (a1 - a0 - (n - 1) * sokak) / n
    return [a0 + k * (b + sokak) + b + sokak / 2 for k in range(n - 1)]


def secenek(ad, W, H, okullar, kirpik=0.0, aciklama=""):
    """W × H dikdörtgen (kirpik > 0 ise köşeleri 45° pahlanmış sekizgen) için şematik ağ ve erişim."""
    CX, CY = W / 2, H / 2
    if kirpik > 0:
        c = kirpik
        alan = Polygon([(c, 0), (W - c, 0), (W, c), (W, H - c), (W - c, H), (c, H), (0, H - c), (0, c)])
    else:
        alan = box(0, 0, W, H)
    ic = alan.buffer(-YAYA, join_style="mitre")
    cizgiler = [ic.exterior]
    cizgiler.append(LineString([(CX, 0), (CX, H)]).intersection(ic))
    cizgiler.append(LineString([(0, CY), (W, CY)]).intersection(ic))
    xs = _eksenler(TY, CX - CADDE / 2, ADA_X, S2) + _eksenler(CX + CADDE / 2, W - TY, ADA_X, S2)
    ys = _eksenler(TY, CY - CADDE / 2, ADA_Y, S2) + _eksenler(CY + CADDE / 2, H - TY, ADA_Y, S2)
    for x in xs:
        cizgiler.append(LineString([(x, 0), (x, H)]).intersection(ic))
    for y in ys:
        cizgiler.append(LineString([(0, y), (W, y)]).intersection(ic))
    # diyagonaller: iç köşelerden (sekizgende pah ortasından) merkeze
    if kirpik > 0:
        koseler = [(kirpik / 2 + 7, kirpik / 2 + 7), (W - kirpik / 2 - 7, kirpik / 2 + 7),
                   (kirpik / 2 + 7, H - kirpik / 2 - 7), (W - kirpik / 2 - 7, H - kirpik / 2 - 7)]
    else:
        koseler = [(YAYA, YAYA), (W - YAYA, YAYA), (YAYA, H - YAYA), (W - YAYA, H - YAYA)]
    diyag = [LineString([k, (CX, CY)]) for k in koseler]
    cizgiler += diyag
    tum = unary_union([c for c in cizgiler if not c.is_empty])
    G = nx.Graph()
    for ln in getattr(tum, "geoms", [tum]):
        if ln.geom_type != "LineString":
            continue
        c = list(ln.coords)
        for a, b in zip(c[:-1], c[1:]):
            G.add_edge((round(a[0], 2), round(a[1], 2)), (round(b[0], 2), round(b[1], 2)),
                       weight=math.dist(a, b))
    dugumler = list(G.nodes)

    def bagla(xy):
        """Noktayı en yakın kenara bağlar (kenar bölünür)."""
        p = Point(xy)
        en, kenar = 1e9, None
        for a, b in G.edges:
            d = LineString([a, b]).distance(p)
            if d < en:
                en, kenar = d, (a, b)
        a, b = kenar
        ln = LineString([a, b])
        q = ln.interpolate(ln.project(p))
        n = (round(q.x, 2), round(q.y, 2))
        if n not in (a, b):
            w = G[a][b]["weight"]
            G.remove_edge(a, b)
            G.add_edge(a, n, weight=math.dist(a, n))
            G.add_edge(n, b, weight=math.dist(n, b))
        return n, en

    # konutsuz merkez (meydan, cami, ilkokul A, park) ve diyagonal bandı
    merkez = unary_union([box(CX - 130, CY - 72, CX + 130, CY + 72), box(CX - 130, CY - 218, CX - 9, CY - 72)])
    diyag_bant = unary_union([d.buffer(4) for d in diyag])
    okul_poly = unary_union([o[1] for o in okullar])
    kapilar = []
    for y in ys:
        ln = LineString([(0, y), (W, y)]).intersection(ic)
        if ln.is_empty:
            continue
        s = 3.3
        while s < ln.length:
            q = ln.interpolate(s)
            if not (merkez.contains(q) or diyag_bant.contains(q) or okul_poly.buffer(6).contains(q)):
                kapilar.append((q.x, q.y))
            s += 6.6
    # okul kapıları (göreli konumlar merkezden)
    kaynak = []
    for girisler, _poly in okullar:
        for g in girisler:
            n, d = bagla(g)
            kaynak.append((n, d))
    k = "__K__"
    G.add_node(k)
    for n, d in kaynak:
        G.add_edge(k, n, weight=d)
    dist = nx.single_source_dijkstra_path_length(G, k, weight="weight")
    # kapıları ağ düğümüne eşle: aynı eksen üzerindeki en yakın iki düğüm arası doğrusal
    eksen_dugum = {}
    for n in G.nodes:
        if n == k:
            continue
        eksen_dugum.setdefault(n[1], []).append(n)
    for y in eksen_dugum:
        eksen_dugum[y].sort()
    mesafe = []
    for x, y in kapilar:
        sira = eksen_dugum.get(round(y, 2), [])
        sol = max((n for n in sira if n[0] <= x), default=None)
        sag = min((n for n in sira if n[0] >= x), default=None)
        aday = []
        if sol is not None and sol in dist:
            aday.append(dist[sol] + (x - sol[0]))
        if sag is not None and sag in dist:
            aday.append(dist[sag] + (sag[0] - x))
        mesafe.append(min(aday) + 6.0 if aday else math.inf)    # parsel kapısından sokağa ≈ 6 m
    n = len(mesafe)
    sirali = sorted(mesafe)
    return dict(ad=ad, W=W, H=H, alan=alan, ha=alan.area / 1e4, cizgiler=[c for c in cizgiler if not c.is_empty],
                kapilar=kapilar, mesafe=mesafe, okullar=okullar, merkez=merkez,
                pay500=sum(1 for m in mesafe if m <= 500) / n, pay400=sum(1 for m in mesafe if m <= 400) / n,
                medyan=sirali[n // 2], en=sirali[-1], aciklama=aciklama)


def _okul_merkez(CX, CY):
    """v1/v2 ilkokul A: meydanın güneydoğusu; meydan kapısı + cadde kapısı + park yolu karşısı."""
    poly = box(CX + 9, CY - 145, CX + 100, CY - 25)
    return ([(CX + 16, CY - 25), (CX + 9, CY - 77), (CX + 80, CY - 145)], poly)


def _okul_b(CX, CY, W, H):
    """v2 ilkokul B: kuzey yarıda, caddenin doğusunda (ada 3,8 karşılığı)."""
    y0 = CY + 9 + 3 * (ADA_Y + S2)
    poly = box(CX + 9, y0, CX + 9 + ADA_X, y0 + ADA_Y)
    return ([(CX + 9, y0 + ADA_Y / 2), (CX + 9 + ADA_X / 2, y0), (CX + 9 + ADA_X / 2, y0 + ADA_Y),
             (CX + 9 + ADA_X, y0 + ADA_Y / 2)], poly)


def secenekler():
    S = []
    W, H = 800, 750
    S.append(secenek("v1 kurgusu (kalibrasyon)", W, H, [_okul_merkez(W / 2, H / 2)],
                     aciklama="60 ha kare, tek okul meydanda"))
    for ha in (55, 52):
        a = math.sqrt(ha * 1e4)
        S.append(secenek(f"(a) {ha} ha kare, tek okul", a, a, [_okul_merkez(a / 2, a / 2)],
                         aciklama=f"{sayi(a)} × {sayi(a)} m"))
    S.append(secenek("(b) 60 ha, ikinci okul (seçilen)", W, H, [_okul_merkez(W / 2, H / 2), _okul_b(W / 2, H / 2, W, H)],
                     aciklama="A meydanda, B kuzeyde"))
    # (c1) sekizgen: köşeler 45° pahlı, alan 60 ha
    c = 170.0
    s = math.sqrt(60e4 + 2 * c * c)
    S.append(secenek("(c1) 60 ha sekizgen, tek okul", s, s, [_okul_merkez(s / 2, s / 2)], kirpik=c,
                     aciklama=f"{sayi(s)} m kare, köşe pahı {sayi(c)} m"))
    S.append(secenek("(c2) 60 ha uzun dikdörtgen, tek okul", 1000, 600, [_okul_merkez(500, 300)],
                     aciklama="1.000 × 600 m"))
    return S


def _renk(m):
    for k in range(len(MESAFE_SINIR) - 1):
        if m <= MESAFE_SINIR[k + 1]:
            return MESAFE_RENK[k]
    return MESAFE_RENK[-1]


def harita(ax, s, olcek):
    ax.set_aspect("equal")
    ax.axis("off")
    x0, y0, x1, y1 = s["alan"].bounds
    ax.set_xlim(-20, olcek[0] + 20)
    ax.set_ylim(-20, olcek[1] + 20)
    ax.add_patch(MPoly(list(s["alan"].exterior.coords), closed=True, fc="#f4f1ea", ec="#888", lw=0.6))
    segs = []
    for c in s["cizgiler"]:
        for g in getattr(c, "geoms", [c]):
            if g.geom_type == "LineString":
                segs.append(list(g.coords))
            elif g.geom_type == "LinearRing":
                segs.append(list(g.coords))
    ax.add_collection(LineCollection(segs, colors="#cfcac0", linewidths=0.6, zorder=1))
    m = s["merkez"]
    for g in getattr(m, "geoms", [m]):
        ax.add_patch(MPoly(list(g.exterior.coords), closed=True, fc="#e6e1d6", ec="none", zorder=0.5))
    xs = [k[0] for k in s["kapilar"]]
    ys = [k[1] for k in s["kapilar"]]
    ax.scatter(xs, ys, s=3.2, c=[_renk(d) for d in s["mesafe"]], linewidths=0, zorder=2)
    asan = [(x, y) for (x, y), d in zip(s["kapilar"], s["mesafe"]) if d > 500]
    if asan:
        ax.scatter([a[0] for a in asan], [a[1] for a in asan], s=10, facecolors="none", edgecolors=R_ASIM,
                   linewidths=0.6, zorder=3)
    for k, (_, poly) in enumerate(s["okullar"]):
        ax.add_patch(MPoly(list(poly.exterior.coords), closed=True, fc="#4f73a3", ec="white", lw=0.6, zorder=4))
        c = poly.centroid
        ax.text(c.x, c.y, "AB"[k], ha="center", va="center", fontsize=8, color="white", fontweight="bold", zorder=5)
    ax.set_title(s["ad"], fontsize=10, fontweight="bold", loc="left", pad=14)
    ax.text(0, 1.0, f"{s['aciklama']} · ≤ 500 m %{sayi(100 * s['pay500'], 1)} · en uzak {sayi(s['en'])} m",
            transform=ax.transAxes, fontsize=8, color="#333", va="bottom")


def main():
    S = secenekler()
    M = mt.metrikleri_hesapla()
    fig = plt.figure(figsize=(21, 15.5), dpi=150)
    gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 0.72], hspace=0.22, wspace=0.06,
                          left=0.03, right=0.985, top=0.855, bottom=0.03)
    olcek = (1000, 1000 * 0.75)
    for k, s in enumerate(S):
        harita(fig.add_subplot(gs[k // 3, k % 3]), s, (1000, 800))
    # tablo
    ax = fig.add_subplot(gs[2, :])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    bas = ["Seçenek", "Alan", "≤ 500 m", "≤ 400 m", "Medyan", "En uzak", "Okul", "Nüfus (2.200 konut)",
           "Sonuç ve bedeli"]
    xs = [0.0, 0.17, 0.215, 0.26, 0.305, 0.35, 0.395, 0.43, 0.52]
    y = 0.97
    for x, b in zip(xs, bas):
        ax.text(x, y, b, fontsize=8.8, fontweight="bold", va="top")
    y -= 0.12
    ax.plot([0, 1], [y + 0.04] * 2, color="#333", lw=0.8)
    def _y(k):
        return S[k]

    yorum = {
        0: f"Tam modelde %96,8 / 553 m; şematik ağ %{sayi(100 * _y(0)['pay500'], 1)} / {sayi(_y(0)['en'])} m veriyor "
           "(kalibrasyon tutarlı).",
        1: f"55 ha da %100 vermiyor (en uzak {sayi(_y(1)['en'])} m). 2.200 konut için "
           f"{sayi(KONUT * HANE / _y(1)['ha'])} kişi/ha: daha çok Z+3/T4; ≤ 3 kat payı ve T1 düşer.",
        2: f"%{sayi(100 * _y(2)['pay500'], 1)}, en uzak {sayi(_y(2)['en'])} m: yine sınırda. "
           f"{sayi(KONUT * HANE / _y(2)['ha'])} kişi/ha; ya nüfus ≈ {sayi(120 * _y(2)['ha'])}'a iner ya da dikeyleşir.",
        3: f"%100 (tam modelde %{sayi(100 * M['erisim']['ilkokul']['pay_hedef'])}, en uzak "
           f"{sayi(M['erisim']['ilkokul']['en_fazla'])} m). Alan, yoğunluk ve kat profili aynı; okullar "
           f"{M['okul']['A']['derslik']} + {M['okul']['B']['derslik']} derslik.",
        4: f"%{sayi(100 * _y(4)['pay500'], 1)}, en uzak {sayi(_y(4)['en'])} m: pah köşe konutlarını azaltır, 22,5° "
           "doğrultusundaki ara bölgeler kalır; pahlarda düzensiz parsel.",
        5: f"%{sayi(100 * _y(5)['pay500'], 1)}: tek merkezde uzun kenarlar 500 m'yi aşar; uzun biçim ancak iki okulla "
           "anlamlı.",
    }
    for k, s in enumerate(S):
        if k % 2 == 0:
            ax.add_patch(Rectangle((0, y - 0.115), 1, 0.12, fc="#f3f1ec", ec="none"))
        vals = [s["ad"], f"{sayi(s['ha'], 1)} ha", f"%{sayi(100 * s['pay500'], 1)}", f"%{sayi(100 * s['pay400'], 1)}",
                f"{sayi(s['medyan'])} m", f"{sayi(s['en'])} m", "2" if "(b)" in s["ad"] else "1",
                f"{sayi(KONUT * HANE)} · {sayi(KONUT * HANE / s['ha'])} kişi/ha", yorum[k]]
        for x, v in zip(xs, vals):
            ax.text(x, y - 0.055, v, fontsize=8.3, va="center", fontweight="bold" if "(b)" in s["ad"] else "normal")
        y -= 0.12
    ax.text(0, y - 0.03,
            "Seçim: (b). Gerekçe: alan, yoğunluk ve kat profili korunur; güncel EK-2'nin 2,0 m²/kişi'lik ilkokul alanı iki okula "
            "bölünür (her biri ≥ 5.000 m²); konutların %" + sayi(100 * M["ilk_400"]) + "'i okula 400 m içinde (v1: %75). Bedeli: ikinci okul binası ve "
            "yönetimi (MEB norm kadrosu; doğrulanmalı).\n(a) aynı nüfusu daha küçük alana sığdırmak için dikeyleşmeyi gerektirir "
            "(Faz 2'de kat başına ≈ +%2,5 ölümlülük); (c) tek okulla %100'ü sağlamaz ve düzensiz parsel üretir. Gerçek bir "
            "alanda topoğrafya ve mülkiyet (c) türü biçimi zorunlu kılarsa iki okul kuralı yine geçerlidir.",
            fontsize=8.8, va="top", color="#333")
    fig.text(0.03, 0.955, "İlkokula ≤ 500 m: üç seçenek (şematik ağ)", fontsize=22, fontweight="bold")
    fig.text(0.03, 0.927,
             "Aynı sokak kuralları (ada 120 × 63 m, S2 10 m, artı cadde, köşe diyagonalleri), konutsuz merkez ≈ 3,7 ha; nokta = "
             "D–B sokaklarda 6,6 m arayla konut kapısı (eşit ağırlık). Renk: ağ mesafesi; kırmızı halka: > 500 m. Mavi: ilkokul.",
             fontsize=10.5, color="#444")
    for k_ in range(len(MESAFE_RENK)):
        a, b = MESAFE_SINIR[k_], MESAFE_SINIR[k_ + 1]
        et = f"{sayi(a)}–{sayi(b)} m" if b < 10_000 else f"> {sayi(a)} m"
        fig.patches.append(Rectangle((0.03 + k_ * 0.075, 0.900), 0.012, 0.010, fc=MESAFE_RENK[k_], ec="none",
                                     transform=fig.transFigure, figure=fig))
        fig.text(0.045 + k_ * 0.075, 0.905, et, fontsize=8.5, va="center")
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"okul_secenekleri.{uz}", facecolor="white")
    plt.close(fig)
    for s in S:
        print(f"{s['ad']:40s} {s['ha']:.1f} ha  ≤500 {100 * s['pay500']:.1f}%  ≤400 {100 * s['pay400']:.1f}%  "
              f"medyan {s['medyan']:.0f}  en {s['en']:.0f}")
    return S


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
