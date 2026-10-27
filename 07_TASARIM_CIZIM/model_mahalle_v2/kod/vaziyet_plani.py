"""
Model mahalle v2.1 — vaziyet planı (≈1/2.000, 60 ha)
==================================================
v2: iki ilkokul, büyüyen ortaokul, teknik altyapı şeritleri, diyagonal köşe evleri, ağaçlar
plan_modeli.agac_noktalari()'ndan (taç örtüsü metriğiyle aynı noktalar), tahsis karması haritası.

plan_modeli.py'nin kurduğu geometriyi çizer: sokak hiyerarşisi, adalar ve
parseller, konut tipleri, merkez ve donatılar, komşuluk birimleri, yeşil sistem,
bölgesel otopark ve duraklar. Sağ panelde lejant, Fıtrat Kodu bölgeleri (transect)
ve çizimden hesaplanan ana sayılar yer alır. Ayrıca DXF (katmanlı) üretir.

Çalıştırma:  python vaziyet_plani.py
Çıktılar  :  ../vaziyet_plani.png|svg, ../vaziyet_plani.dxf
"""

import math
import sys

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Patch, Rectangle
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

import plan_modeli as pm
from ortak import (CIKTI, DONATI_RENK, HALO, HALO_INCE, R_AGAC, R_BOSTAN, R_CADDE, R_DIS, R_MEYDAN,
                   R_ORTAK_AVLU, R_ORTAK_YESIL, R_OZEL_AVLU, R_S2, R_S3, R_SPOR, R_SU, R_TICARI, R_TOPLAYICI,
                   R_ZEMIN, TIP_AD, TIP_RENK, kuzey_oku, olcek_cubugu, poligon_ciz, sayi, yuzde)
import metrikler as mt

M = mt.metrikleri_hesapla()
P = pm.model()

R_CEP = "#bcdca3"
R_KOSE = "#c0392b"          # v2: diyagonal köşe evi çerçevesi
R_KUSAK = "#e2ecd3"
R_KOMSU = "#e4e0d8"
R_PARK_YOL = "#f1ead8"


# --- ağaç üreticiler -----------------------------------------------------------
def _sokak_agaclari():
    """Cadde, toplayıcı, S2 ve diyagonal ağaçları (ölçekli konumlar)."""
    noktalar = []
    kavsak = unary_union(list(pm.KAVSAK.values()) + [pm.MEYDAN, pm.CARSI_YAYA.buffer(-1)]).buffer(3)
    engel = unary_union([kavsak, pm.DONATI_POLY.buffer(1)])
    # S1 cadde: iki yanda ±4,25 m, 10 m arayla
    for s in (-4.25, 4.25):
        for y in range(18, 740, 10):
            noktalar.append((pm.CX + s, y, 2.6))
        for x in range(18, 790, 10):
            noktalar.append((x, pm.CY + s, 2.6))
    # toplayıcı: iç ağaç şeridi (eksenden 5,75 m) ve orta refüj, 10 m arayla
    for d in (5.75, 0.0):
        for t in range(10, 800, 10):
            noktalar.append((t, d, 2.8))
            noktalar.append((t, pm.YUK - d, 2.8))
        for t in range(10, 750, 10):
            noktalar.append((d, t, 2.8))
            noktalar.append((pm.GEN - d, t, 2.8))
    # S2: ağaç + park cebi şeridi (eksenden −2 m), 12 m arayla
    for k, (pol, ln) in pm.BAGLANTI.items():
        if k in pm.KAPALI:
            continue
        L = ln.length
        for s in range(6, int(L) - 3, 12):
            q = ln.interpolate(s)
            if k[0] == "h":
                noktalar.append((q.x, q.y - 2.0, 2.0))
            else:
                noktalar.append((q.x - 2.0, q.y, 2.0))
    # diyagonaller: iki sıra
    for ln in pm.DIYAG_EKSEN:
        L = ln.length
        dx, dy = (ln.coords[1][0] - ln.coords[0][0]) / L, (ln.coords[1][1] - ln.coords[0][1]) / L
        nx_, ny_ = -dy, dx
        for s in range(6, int(L) - 30, 8):
            q = ln.interpolate(s)
            for side in (-2.6, 2.6):
                noktalar.append((q.x + nx_ * side, q.y + ny_ * side, 1.9))
    out = []
    sokak_disi = unary_union([pm.MEYDAN, pm.CARSI_YAYA])
    for x, y, r in noktalar:
        p = Point(x, y)
        if kavsak.contains(p) or sokak_disi.contains(p):
            continue
        out.append((x, y, r))
    return out


def _park_agaclari(poly, aralik=13.0, r=3.2, tohum=1):
    x0, y0, x1, y1 = poly.bounds
    out = []
    ic = poly.buffer(-3)
    k = tohum
    y = y0 + aralik / 2
    while y < y1:
        x = x0 + aralik / 2 + (aralik / 2 if int((y - y0) / aralik) % 2 else 0)
        while x < x1:
            k = (k * 1103515245 + 12345) % 2 ** 31
            jx = ((k % 1000) / 1000 - 0.5) * aralik * 0.5
            jy = (((k // 1000) % 1000) / 1000 - 0.5) * aralik * 0.5
            p = Point(x + jx, y + jy)
            if ic.contains(p):
                out.append((p.x, p.y, r * (0.8 + 0.4 * ((k // 7) % 100) / 100)))
            x += aralik
        y += aralik
    return out


# --- çizim -----------------------------------------------------------------------
def plan_ciz(ax, ayrinti=True):
    G, Y = pm.GEN, pm.YUK
    pad = 46
    # alan dışı bağlam
    ax.add_patch(Rectangle((-pad, -pad), G + 2 * pad, Y + 2 * pad, fc=R_DIS, ec="none", zorder=0))
    kusak = unary_union([box(-pad, -12, -12, Y + pad), box(-pad, Y + 12, G + pad, Y + pad)])
    komsu = unary_union([box(-pad, -pad, G + pad, -12), box(G + 12, -pad, G + pad, Y + 12)]).difference(kusak)
    poligon_ciz(ax, kusak, R_KUSAK, zorder=0.2)
    poligon_ciz(ax, komsu, R_KOMSU, zorder=0.2, hatch="////", ec="#d2cdc3", lw=0)
    # toplayıcı yolun dış yarısı
    dis_yari = box(-12, -12, G + 12, Y + 12).difference(box(0, 0, G, Y))
    poligon_ciz(ax, dis_yari, R_TOPLAYICI, zorder=0.5)
    ax.text(-30, Y / 2 + 120, "YEŞİL KUŞAK / TARIM", rotation=90, ha="center", va="center", fontsize=9,
            color="#5d7a45", fontweight="bold", zorder=2)
    ax.text(G / 2 - 180, Y + 30, "YEŞİL KUŞAK / TARIM", ha="center", va="center", fontsize=9,
            color="#5d7a45", fontweight="bold", zorder=2)
    ax.text(G / 2 + 180, -30, "KOMŞU MAHALLE (SEMT)", ha="center", va="center", fontsize=9, color="#77706a",
            fontweight="bold", zorder=2, path_effects=HALO_INCE)
    ax.text(G + 30, Y / 2 - 140, "KOMŞU MAHALLE (SEMT)", rotation=-90, ha="center", va="center", fontsize=9,
            color="#77706a", fontweight="bold", zorder=2, path_effects=HALO_INCE)

    # zemin (adalar), sokaklar
    poligon_ciz(ax, box(pm.TY, pm.TY, G - pm.TY, Y - pm.TY), R_ZEMIN, zorder=1)
    poligon_ciz(ax, pm.TOPLAYICI, R_TOPLAYICI, zorder=2)
    poligon_ciz(ax, pm.CADDE, R_CADDE, zorder=2)
    poligon_ciz(ax, pm.S2, R_S2, zorder=2)
    poligon_ciz(ax, pm.KAPALI_SOKAK.difference(pm.DONATI_POLY), R_S2, zorder=2)
    poligon_ciz(ax, unary_union([pm.MEYDAN, pm.CARSI_YAYA]), R_MEYDAN, zorder=2.2)
    # meydan döşeme deseni
    for x in range(366, 435, 7):
        ax.plot([x, x], [350, 400], color="#d8c59c", lw=0.3, zorder=2.3)
    poligon_ciz(ax, pm.DIYAG_BANT.difference(pm.DONATI_POLY), R_S3, zorder=2.4)
    for gp, _ in P["gecitler"]:
        poligon_ciz(ax, gp, R_S3, zorder=2.4)
    # kesit konum işaretleri
    # şerit çizgileri: toplayıcı orta refüj ve cadde orta çizgisi
    ax.plot([pm.CX, pm.CX], [pm.TY, pm.Y_ if hasattr(pm, "Y_") else Y - pm.TY], color="white", lw=0.4,
            ls=(0, (6, 6)), zorder=2.5)

    # donatı arsaları
    for d in P["donatilar"]:
        t = d["tur"]
        if t == "park":
            poligon_ciz(ax, d["poly"], R_ORTAK_YESIL, zorder=3)
        elif t == "spor":
            poligon_ciz(ax, d["poly"], R_SPOR, zorder=3)
        elif t == "cep":
            poligon_ciz(ax, d["poly"], R_CEP, zorder=3)
        elif t == "bostan":
            poligon_ciz(ax, d["poly"], R_BOSTAN, zorder=3)
            x0, y0, x1, y1 = d["poly"].bounds
            for yy in range(int(y0) + 3, int(y1), 4):
                ln = LineString([(x0, yy), (x1, yy)]).intersection(d["poly"].buffer(-2))
                for g in getattr(ln, "geoms", [ln]):
                    if g.length > 1:
                        ax.plot(*g.xy, color="#9fb56a", lw=0.5, zorder=3.1)
        else:
            renk = {"semt_camii": "ibadet", "kucuk_cami": "ibadet", "asm": "saglik", "carsi": "carsi",
                    "anaokulu": "egitim", "konak": "sosyal", "ilkokul": "egitim", "ortaokul": "egitim",
                    "otopark": "otopark", "teknik": "teknik"}[t]
            poligon_ciz(ax, d["poly"], DONATI_RENK[renk][1], zorder=3, ec="#8d8a84", lw=0.4)
            for b in d["binalar"]:
                poligon_ciz(ax, b, DONATI_RENK[renk][0], zorder=6, ec="white", lw=0.4)
    # park içi yollar
    for ln in pm.ag_kur()["yaya_cizgi"]:
        for d in P["donatilar"]:
            if d["tur"] in ("park", "spor", "cep") and ln.intersects(d["poly"]):
                g = ln.intersection(d["poly"])
                for gg in getattr(g, "geoms", [g]):
                    if gg.geom_type == "LineString" and gg.length > 2:
                        ax.plot(*gg.xy, color=R_PARK_YOL, lw=2.2, zorder=3.4, solid_capstyle="butt")
    poligon_ciz(ax, pm.DIYAG_BANT.intersection(pm.DONATI_POLY), R_PARK_YOL, zorder=3.3)
    # komşuluk yeşillerindeki çok amaçlı sahalar
    for d in P["donatilar"]:
        if d.get("saha") is not None:
            poligon_ciz(ax, d["saha"], "#86b886", ec="white", lw=0.7, zorder=3.5)
            x0, y0, x1, y1 = d["saha"].bounds
            ax.plot([(x0 + x1) / 2] * 2, [y0, y1], color="white", lw=0.5, zorder=3.6)
    # spor alanı çizgileri
    spor = next(d for d in P["donatilar"] if d["tur"] == "spor")
    sx0, sy0, sx1, sy1 = spor["poly"].bounds
    for (a, b, c, e) in ((sx0 + 8, sy0 + 6, 44, 24), (sx0 + 60, sy0 + 8, 28, 15), (sx0 + 92, sy0 + 8, 18, 22)):
        ax.add_patch(Rectangle((a, b), c, e, fc="#86b886", ec="white", lw=0.7, zorder=3.5))
    ax.plot([sx0 + 30, sx0 + 30], [sy0 + 6, sy0 + 30], color="white", lw=0.6, zorder=3.6)

    # konut adaları: ortak bahçe şeritleri, T4 avluları
    for o in P["ortaklar"]:
        poligon_ciz(ax, o, R_ORTAK_AVLU, zorder=3)
    for g in P["cep"]:
        poligon_ciz(ax, g, R_CEP, zorder=3)
    # parseller
    for p in P["parseller"]:
        if p["tip"] in ("T1", "T2"):
            poligon_ciz(ax, p["poly"], R_OZEL_AVLU, ec="#a4bf8f", lw=0.25, zorder=4)
        elif p["tip"] == "T3":
            poligon_ciz(ax, p["poly"], R_ORTAK_AVLU, ec="#93ad7f", lw=0.35, zorder=4)
        else:
            if p.get("avlu") is not None:
                poligon_ciz(ax, p["poly"], R_ORTAK_AVLU, ec="#93ad7f", lw=0.25, zorder=4)
    # binalar
    for p in P["parseller"]:
        renk = TIP_RENK[p["tip"]]
        for b in p["binalar"]:
            poligon_ciz(ax, b, renk, ec="white", lw=0.25, zorder=6)
        if p.get("kose"):
            poligon_ciz(ax, p["binalar"][0], "none", ec=R_KOSE, lw=0.9, zorder=6.2)
        for d_ in p.get("duvar") or []:          # v2.1: T3 kuzey grubunda 2,5 m bahçe duvarı
            poligon_ciz(ax, d_, "#5b4a3f", zorder=6.1)
        g = p.get("genisleme")
        if g is not None:
            poligon_ciz(ax, g, "none", ec=TIP_RENK["T1"], lw=0.45, zorder=6, ls=(0, (2, 1.5)))
        if p.get("dukkan"):
            b = p["binalar"][0]
            x0, y0, x1, y1 = b.bounds
            kx, ky = p["kapi"]
            if abs(ky - y0) < 0.6 or abs(ky - y1) < 0.6:
                ax.plot([x0 + 0.5, x1 - 0.5], [ky + (0.6 if abs(ky - y0) < 0.6 else -0.6)] * 2,
                        color=R_TICARI, lw=1.6, zorder=6.5, solid_capstyle="butt")
            else:
                ax.plot([kx + (0.6 if abs(kx - x0) < 0.6 else -0.6)] * 2, [y0 + 0.5, y1 - 0.5],
                        color=R_TICARI, lw=1.6, zorder=6.5, solid_capstyle="butt")
    # donatı binalarında ticari cephe: çarşı
    # ağaçlar: plan_modeli.agac_noktalari() (20 yıllık taç; çizimde çapın %80'i, örtü hesabında tam çap)
    if ayrinti:
        for x, y, r, tur in pm.agac_noktalari():
            ax.add_patch(Circle((x, y), r * 0.8, fc=R_AGAC, ec="white", lw=0.2,
                                alpha=0.80 if tur in ("bahce", "avlu", "ortak") else 0.85, zorder=7))
    # su / çeşme ve küçük semboller
    return ax


def semboller(ax):
    for z in P["zemin"]:
        x, y = z["xy"]
        if z["tur"] == "mescit":
            if z.get("bagimsiz"):
                ax.add_patch(Rectangle((x - 5, y - 5), 10, 10, fc=DONATI_RENK["ibadet"][0], ec="white", lw=0.5, zorder=11))
            ax.plot(x, y, marker="^", ms=7.5, mfc=DONATI_RENK["ibadet"][0], mec="white", mew=0.8, zorder=12)
        elif z["tur"] == "kres":
            ax.plot(x, y, marker="D", ms=6.5, mfc=DONATI_RENK["egitim"][0], mec="white", mew=0.8, zorder=12)
        elif z["tur"] == "bakkal":
            ax.plot(x, y, marker="s", ms=6.5, mfc=R_TICARI, mec="white", mew=0.8, zorder=12)
        elif z["tur"] == "cesme":
            ax.plot(x, y, marker="o", ms=6, mfc=R_SU, mec="white", mew=0.8, zorder=12)
    for hat, liste in pm.DURAKLAR.items():
        for x, y in liste:
            ax.plot(x, y, marker="o", ms=10, mfc="white", mec="#1f5fa8", mew=1.8, zorder=13)
            ax.text(x, y, "D", ha="center", va="center", fontsize=6, fontweight="bold", color="#1f5fa8", zorder=14)
    # otobüs hattı (S1)
    ax.plot([pm.CX + 1.2] * 2, [-46, pm.YUK + 46], color="#1f5fa8", lw=1.0, ls=(0, (1, 2)), zorder=11, alpha=0.8)
    # araç filtreleri (meydanda yalnız otobüs ve acil durum)
    for (x, y) in ((pm.CX - 30, pm.CY), (pm.CX + 30, pm.CY)):
        ax.plot([x, x], [y - 7, y + 7], color="#b0483f", lw=2.2, zorder=12, solid_capstyle="butt")
    for (x, y) in ((pm.CX, pm.CY - 31), (pm.CX, pm.CY + 31)):
        ax.plot([x - 7, x + 7], [y, y], color="#1f5fa8", lw=2.2, zorder=12, solid_capstyle="butt")


def etiketler(ax):
    yaz = dict(ha="center", va="center", fontsize=7.5, zorder=20, path_effects=HALO)
    ozel = {
        "Merkez parkı": ((331, 255), "Merkez parkı\n(2,0 ha)"),
        "Açık semt spor alanı": ((331, 178), "Açık semt spor alanı"),
        "Semt camii ve avlusu": ((312, 440), "Semt camii\nve avlusu"),
        "Aile sağlık merkezi ve eczane": ((373, 455), "ASM +\neczane"),
        "Çarşı ve kapalı pazar": ((480, 418), "Çarşı ve\nkapalı pazar"),
        "Anaokulu (kuzey)": ((424, 455), "Anaokulu"),
        "Mahalle konağı (muhtarlık, meclis, kütüphane, gençlik, aile, yaşlı günevi, hamam)":
            ((478, 334), "Mahalle\nkonağı"),
        "Anaokulu (güney)": ((428, 268), "Anaokulu"),
        "İlkokul A (güney)": ((469, 274), f"İlkokul A\n({M['okul']['A']['derslik']} derslik)"),
        "İlkokul B (kuzey)": ((464, 631), f"İlkokul B\n({M['okul']['B']['derslik']} derslik)"),
        "Ortaokul (komşu mahalleyle ortak)": ((612, 36), "Ortaokul"),
    }
    for d in P["donatilar"]:
        if d["ad"] in ozel:
            (x, y), m = ozel[d["ad"]]
            ax.text(x, y, m, fontweight="bold" if d["tur"] != "park" else "normal", **yaz)
        elif d["tur"] == "kucuk_cami":
            c = d["binalar"][0].centroid
            ax.text(c.x, c.y + (13 if c.y < pm.CY else -13), "Küçük cami", **{**yaz, "fontsize": 6.5})
        elif d["tur"] == "bostan":
            c = d["poly"].representative_point()
            ax.text(c.x, c.y, "Bostan", **{**yaz, "fontsize": 6.5})
        elif d["tur"] == "otopark":
            c = d["binalar"][0].centroid
            ax.text(c.x, c.y + 6, "P", ha="center", va="center", fontsize=13, fontweight="bold", color="white", zorder=21)
            ax.text(c.x, c.y - 10, "mobilite\nnoktası", ha="center", va="center", fontsize=5.8, color="white", zorder=21)
        elif d["ad"].startswith("Kenar parkı"):
            c = d["poly"].representative_point()
            ax.text(c.x + 22, c.y + 14, "Kenar\nparkı", **{**yaz, "fontsize": 6.5})
    ax.text(747, 39, "okul sahası", ha="center", va="center", fontsize=6.3, zorder=21, path_effects=HALO_INCE)
    # okul geçidi (S1'de yükseltilmiş yaya geçidi: park yolu ile ilkokul A kapısı arasında)
    for k_ in range(5):
        ax.add_patch(Rectangle((391.5 + k_ * 3.4, 296.2), 2.0, 4.0, fc="white", ec="#1f5fa8", lw=0.4, zorder=12))
    ax.text(386, 290.5, "okul geçidi", ha="right", va="center", fontsize=6.0, color="#1f5fa8", zorder=21,
            path_effects=HALO_INCE)
    ax.text(pm.CX, pm.CY + 2, "MEYDAN\n(pazar yeri)", ha="center", va="center", fontsize=7.5, fontweight="bold",
            zorder=21, path_effects=HALO)
    ax.text(pm.CX - 70, pm.CY, "Ç A R Ş I", ha="center", va="center", fontsize=6.5, color="#7a5a20", zorder=21,
            path_effects=HALO_INCE)
    ax.text(pm.CX + 70, pm.CY, "Ç A R Ş I", ha="center", va="center", fontsize=6.5, color="#7a5a20", zorder=21,
            path_effects=HALO_INCE)
    # sokak adları
    sy = dict(fontsize=6.5, color="#4a4640", zorder=21, path_effects=HALO_INCE, ha="center", va="center")
    ax.text(pm.CX, 640, "S1 · MAHALLE CADDESİ (18 m) · OTOBÜS", rotation=90, **sy)
    ax.text(170, pm.CY, "S1 · MAHALLE CADDESİ", **sy)
    ax.text(630, pm.CY, "S1 · MAHALLE CADDESİ", **sy)
    ax.text(560, 6, "TOPLAYICI YOL (24 m)", **sy)
    ax.text(pm.GEN - 6, 560, "TOPLAYICI YOL (24 m)", rotation=-90, **sy)
    ax.text(200, pm.YUK - 6, "TOPLAYICI YOL (24 m) · PARK YOLU", **sy)
    ax.text(6, 560, "TOPLAYICI YOL (24 m)", rotation=90, **sy)
    ax.text(201, pm.GY[5][0] + 5, "S2 · yaşam sokağı (10 m)", **{**sy, "fontsize": 6})
    ln = pm.DIYAG_EKSEN[0]
    q = ln.interpolate(0.27 * ln.length)
    ax.text(q.x - 12, q.y + 12, "yeşil diyagonal (8 m)", rotation=43, **{**sy, "fontsize": 6.2})
    # komşuluk birimleri
    birim = {b["no"]: b for b in M["birimler"]}
    konum = {1: (300, 116), 2: (95, 262), 3: (95, 488), 4: (300, 634), 5: (612, 597), 6: (705, 488),
             7: (705, 262), 8: (500, 116)}
    for no, g in pm.komsuluk_birimleri():
        poligon_ciz(ax, g.buffer(-2), "none", ec="#3a3632", lw=1.0, zorder=15, ls=(0, (7, 3)))
        x, y = konum[no]
        b = birim[no]
        ax.text(x, y, f"KB-{no}\n{sayi(b['konut'])} konut · {sayi(b['nufus'])} kişi", ha="center", va="center",
                fontsize=7, fontweight="bold", color="#2c2925", zorder=22,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#3a3632", lw=0.6, alpha=0.92))
    # erişim halkaları (kuş uçuşu, yalnız başvuru)
    for r, et in ((400, "400 m"), (500, "500 m")):
        ax.add_patch(Circle((pm.CX, pm.CY), r, fc="none", ec="#1f5fa8", lw=0.8, ls=(0, (2, 3)), zorder=16,
                            alpha=0.7))
        a = math.radians(57)
        ax.text(pm.CX + r * math.cos(a), pm.CY + r * math.sin(a), et, fontsize=6.5, color="#1f5fa8", zorder=21,
                path_effects=HALO_INCE, ha="center", va="center")


def lejant(ax):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    y = 0.995
    dy = 0.0242

    def baslik(m):
        nonlocal y
        y -= dy * 0.6
        ax.text(0.0, y, m, fontsize=9.5, fontweight="bold", va="top")
        y -= dy * 1.05

    def kutu(renk, m, ec="none", hatch=None, cizgi=None, isaret=None):
        nonlocal y
        if cizgi:
            ax.plot([0.01, 0.07], [y - 0.008] * 2, **cizgi)
        elif isaret:
            ax.plot(0.04, y - 0.008, **isaret)
        else:
            ax.add_patch(Rectangle((0.01, y - 0.016), 0.06, 0.016, fc=renk, ec=ec, lw=0.6, hatch=hatch))
        ax.text(0.09, y - 0.008, m, fontsize=8.2, va="center")
        y -= dy

    baslik("Sokak hiyerarşisi")
    kutu(R_TOPLAYICI, "Toplayıcı yol, 24 m (mahalle dışı; otobüs, bisiklet)")
    kutu(R_CADDE, "S1 mahalle caddesi / çarşı, 18 m (30 km/s, otobüs)")
    kutu(R_S2, "S2 yaşam sokağı, 10 m paylaşımlı yüzey (≤20 km/s)")
    kutu(R_S3, "S3 yaya yolu: T3 geçidi 6 m, T1/T2 ada ortası 5 m (v2.1); diyagonal 8 m")
    kutu(R_MEYDAN, "Meydan ve çarşı yaya kesimi (haftalık pazar)")
    kutu(None, "Araç filtresi: geçiş yok (kırmızı) · yalnız otobüs (mavi)",
         cizgi=dict(color="#b0483f", lw=2.2, solid_capstyle="butt"))
    baslik("Konut tipleri (bina)")
    for t in ("T1", "T2", "T3", "T4"):
        kutu(TIP_RENK[t], f"{TIP_AD[t]} · {sayi(M['tip'][t]['konut'])} konut")
    kutu("none", "T1 genişleme payı (arka oda)", ec=TIP_RENK["T1"])
    kutu("none", "Diyagonal köşe evi (kırpılmış parsel, v2)", ec=R_KOSE)
    kutu(None, "T3: güneyde tek katlı arka kanat, kuzeyde avlu duvarı (v2.1)",
         cizgi=dict(color="#5b4a3f", lw=2.0, solid_capstyle="butt"))
    kutu(None, "Zemin kat dükkân cephesi", cizgi=dict(color=R_TICARI, lw=2.2, solid_capstyle="butt"))
    kutu(R_OZEL_AVLU, "Özel bahçe / avlu", ec="#a4bf8f")
    kutu(R_ORTAK_AVLU, "Ortak avlu, ada içi ortak bahçe", ec="#93ad7f")
    baslik("Donatılar (arsa · bina)")
    for anahtar, m in (("ibadet", "İbadet: semt camii, küçük cami"), ("egitim", "Eğitim: ilkokul, ortaokul, anaokulu"),
                       ("saglik", "Aile sağlık merkezi ve eczane"), ("sosyal", "Mahalle konağı"),
                       ("carsi", "Çarşı ve kapalı pazar"), ("otopark", "Mobilite noktası: bölgesel otopark (Z+4)"),
                       ("teknik", "Teknik altyapı (köşeler + kapı servis şeritleri)")):
        nonlocal_y = y
        ax.add_patch(Rectangle((0.01, y - 0.016), 0.03, 0.016, fc=DONATI_RENK[anahtar][1], ec="#8d8a84", lw=0.4))
        ax.add_patch(Rectangle((0.04, y - 0.016), 0.03, 0.016, fc=DONATI_RENK[anahtar][0], ec="none"))
        ax.text(0.09, y - 0.008, m, fontsize=8.2, va="center")
        y -= dy
    baslik("Yeşil sistem")
    kutu(R_ORTAK_YESIL, "Merkez parkı (2,0 ha), komşuluk yeşili (8 × 0,5 ha)")
    kutu(R_CEP, "Cep parkı / kapı önü oyun alanı")
    kutu(R_SPOR, "Açık semt spor alanı")
    kutu(R_BOSTAN, "Bostan ve hobi bahçesi")
    kutu(None, f"Ağaç, 20 yıllık taç ({sayi(M['tac']['sayi'])} ağaç; örtü %{sayi(100 * M['tac']['oran'])})",
         isaret=dict(marker="o", ms=7, mfc=R_AGAC, mec="white"))
    baslik("Semboller")
    kutu(None, "Mescit (zemin katta)", isaret=dict(marker="^", ms=8, mfc=DONATI_RENK["ibadet"][0], mec="white"))
    kutu(None, "Kreş (zemin katta)", isaret=dict(marker="D", ms=6.5, mfc=DONATI_RENK["egitim"][0], mec="white"))
    kutu(None, "Bakkal ve fırın", isaret=dict(marker="s", ms=6.5, mfc=R_TICARI, mec="white"))
    kutu(None, "Su ve oturma noktası (çeşme)", isaret=dict(marker="o", ms=6.5, mfc=R_SU, mec="white"))
    kutu(None, "Otobüs durağı · S1 otobüs hattı", isaret=dict(marker="o", ms=9, mfc="white", mec="#1f5fa8", mew=1.8))
    kutu(None, "Komşuluk birimi sınırı (KB-1 … KB-8)", cizgi=dict(color="#3a3632", lw=1.0, ls=(0, (7, 3))))
    kutu(None, "400 / 500 m kuş uçuşu halka (başvuru)", cizgi=dict(color="#1f5fa8", lw=0.9, ls=(0, (2, 3))))
    return y


def sayilar(ax, y_ust):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.0, 0.99, "Çizimden hesaplanan ana sayılar (hedef)", fontsize=9.5, fontweight="bold", va="top")
    satirlar = M["ozet_satirlari"]
    y = 0.93
    for ad, deger, hedef in satirlar:
        ax.text(0.0, y, ad, fontsize=7.6, va="center")
        ax.text(0.66, y, deger, fontsize=7.6, va="center", ha="right", family="DejaVu Sans Mono")
        ax.text(0.69, y, hedef, fontsize=7.0, va="center", color="#666")
        y -= 0.0585


def transect_inset(ax):
    renk = {"K1": "#f1e3b5", "K2": "#e0b98a", "K3": "#b9773f", "K4": "#6e3b1c"}
    ax.set_xlim(-10, pm.GEN + 10)
    ax.set_ylim(-10, pm.YUK + 10)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#999")
        s.set_linewidth(0.5)
    ax.add_patch(Rectangle((0, 0), pm.GEN, pm.YUK, fc=R_S2, ec="none"))
    bolge_ada = {}
    for p in P["parseller"]:
        bolge_ada.setdefault(p["ada"], set()).add(p["bolge"])
    for p in P["parseller"]:
        poligon_ciz(ax, p["poly"], renk[p["bolge"]], zorder=2)
    for d in P["donatilar"]:
        poligon_ciz(ax, d["poly"], "#dedbd4" if d["tur"] not in ("park", "spor", "cep", "bostan") else R_ORTAK_YESIL,
                    zorder=2)
    for g in P["cep"]:
        poligon_ciz(ax, g, R_ORTAK_YESIL, zorder=2)
    poligon_ciz(ax, pm.DIYAG_BANT, R_S3, zorder=2.5)
    ax.set_title("Fıtrat Kodu bölgeleri", fontsize=8.5, loc="left", fontweight="bold", pad=3)
    el = [Patch(fc=renk[k], ec="none", label=m) for k, m in
          (("K1", "K1 köy kenarı"), ("K2", "K2 mahalle genel"), ("K3", "K3 merkez"), ("K4", "K4 semt çarşısı"))]
    el += [Patch(fc=R_ORTAK_YESIL, ec="none", label="yeşil"), Patch(fc="#dedbd4", ec="none", label="donatı")]
    ax.legend(handles=el, loc="upper center", bbox_to_anchor=(0.5, -0.01), fontsize=6.8, frameon=False,
              handlelength=1.0, borderaxespad=0, ncol=2, columnspacing=0.8)


TAHSIS_RENK = {"kooperatif": "#3f7f6e", "sosyal": "#d08a2e", "piyasa": "#c9c3b8"}


def tahsis_inset(ax):
    """v2: tahsis karması (kooperatif / yapı grubu · kiralık sosyal · piyasa), parsel grubu düzeyinde."""
    ax.set_xlim(-10, pm.GEN + 10)
    ax.set_ylim(-10, pm.YUK + 10)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s_ in ax.spines.values():
        s_.set_edgecolor("#999")
        s_.set_linewidth(0.5)
    ax.add_patch(Rectangle((0, 0), pm.GEN, pm.YUK, fc=R_S2, ec="none"))
    tah, _ = pm.tahsis()
    for n, p in enumerate(P["parseller"]):
        poligon_ciz(ax, p["poly"], TAHSIS_RENK.get(tah.get(n), "#eeeeee"), zorder=2)
    for d in P["donatilar"]:
        poligon_ciz(ax, d["poly"], "#dedbd4" if d["tur"] not in ("park", "spor", "cep", "bostan") else R_ORTAK_YESIL,
                    zorder=2)
    for g in P["cep"]:
        poligon_ciz(ax, g, R_ORTAK_YESIL, zorder=2)
    poligon_ciz(ax, pm.DIYAG_BANT, R_S3, zorder=2.5)
    ax.set_title("Tahsis karması (v2)", fontsize=8.5, loc="left", fontweight="bold", pad=3)
    el = [Patch(fc=TAHSIS_RENK[t], ec="none", label=f"{pm.TAHSIS_AD[t]} %{sayi(100 * M['tah_pay'].get(t, 0))}")
          for t in ("kooperatif", "sosyal", "piyasa")]
    ax.legend(handles=el, loc="upper center", bbox_to_anchor=(0.5, -0.01), fontsize=6.8, frameon=False,
              handlelength=1.0, borderaxespad=0, ncol=1)


def dxf_yaz(yol):
    try:
        import ezdxf
    except ImportError:
        print("ezdxf yok; DXF atlandı")
        return False
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.M
    msp = doc.modelspace()
    katmanlar = {
        "SINIR": 7, "YOL_TOPLAYICI": 8, "YOL_S1_CADDE": 8, "YOL_S2": 9, "YOL_S3_YAYA": 30, "MEYDAN": 40,
        "ADA_ORTAK": 82, "PARSEL_T1": 32, "PARSEL_T2": 32, "PARSEL_T3": 32, "PARSEL_T4": 32,
        "BINA_T1": 34, "BINA_T2": 24, "BINA_T3": 14, "BINA_T4": 250, "T1_GENISLEME": 34,
        "DONATI_ARSA": 150, "DONATI_BINA": 5, "YESIL": 3, "CEP_YESIL": 63, "KOMSULUK_BIRIMI": 6,
        "TEKNIK": 9, "KOSE_EVI": 1, "AGAC": 94,
        "SEMBOL": 1, "METIN": 7,
    }
    for ad, renk in katmanlar.items():
        doc.layers.add(ad, color=renk)

    def yaz(geom, katman):
        if geom is None or geom.is_empty:
            return
        parcalar = [geom] if geom.geom_type == "Polygon" else [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon"]
        for p in parcalar:
            for halka in [p.exterior] + list(p.interiors):
                msp.add_lwpolyline(list(halka.coords)[:-1], close=True, dxfattribs={"layer": katman})

    yaz(box(0, 0, pm.GEN, pm.YUK), "SINIR")
    yaz(pm.TOPLAYICI, "YOL_TOPLAYICI")
    yaz(pm.CADDE, "YOL_S1_CADDE")
    yaz(pm.S2, "YOL_S2")
    yaz(pm.DIYAG_BANT, "YOL_S3_YAYA")
    for gp, _ in P["gecitler"]:
        yaz(gp, "YOL_S3_YAYA")
    yaz(pm.MEYDAN, "MEYDAN")
    for o in P["ortaklar"]:
        yaz(o, "ADA_ORTAK")
    for g in P["cep"]:
        yaz(g, "CEP_YESIL")
    for p in P["parseller"]:
        yaz(p["poly"], f"PARSEL_{p['tip']}")
        for b in p["binalar"]:
            yaz(b, f"BINA_{p['tip']}")
        if p.get("genisleme") is not None:
            yaz(p["genisleme"], "T1_GENISLEME")
        if p.get("kose"):
            yaz(p["binalar"][0], "KOSE_EVI")
    for d in P["donatilar"]:
        yaz(d["poly"], "YESIL" if d["tur"] in ("park", "spor", "cep", "bostan")
            else ("TEKNIK" if d["tur"] == "teknik" else "DONATI_ARSA"))
        for b in d["binalar"]:
            yaz(b, "DONATI_BINA")
        c = d["poly"].representative_point()
        if d["kisa"]:
            msp.add_text(d["kisa"], height=3.0, dxfattribs={"layer": "METIN"}).set_placement((c.x, c.y))
    for no, g in pm.komsuluk_birimleri():
        yaz(g, "KOMSULUK_BIRIMI")
        c = g.centroid
        msp.add_text(f"KB-{no}", height=6.0, dxfattribs={"layer": "METIN"}).set_placement((c.x, c.y))
    for x, y, r, _ in pm.agac_noktalari():
        msp.add_circle((x, y), r, dxfattribs={"layer": "AGAC"})
    for z in P["zemin"]:
        msp.add_circle(z["xy"], 2.5, dxfattribs={"layer": "SEMBOL"})
        msp.add_text(z["tur"], height=2.0, dxfattribs={"layer": "SEMBOL"}).set_placement((z["xy"][0] + 3, z["xy"][1]))
    for liste in pm.DURAKLAR.values():
        for xy in liste:
            msp.add_circle(xy, 3.5, dxfattribs={"layer": "SEMBOL"})
            msp.add_text("DURAK", height=2.0, dxfattribs={"layer": "SEMBOL"}).set_placement((xy[0] + 4, xy[1]))
    doc.saveas(yol)
    return True


def main():
    fig = plt.figure(figsize=(25, 17.6), dpi=150)
    # basılı ölçek: plan ekseninin genişliği (mm) / gösterilen genişlik (890 m)
    pw_mm = 25 * (0.99 - 0.015) * (1.0 / 1.36) * 25.4
    olcek = f"{sayi(25 * 25.4)} × {sayi(17.6 * 25.4)} mm baskıda ≈ 1/{sayi(round(890_000 / pw_mm, -2))}"
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 0.36], wspace=0.02, left=0.015, right=0.99, top=0.935, bottom=0.02)
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(-46, pm.GEN + 46)
    ax.set_ylim(-46, pm.YUK + 46)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#888")
        s.set_linewidth(0.6)
    plan_ciz(ax)
    semboller(ax)
    etiketler(ax)
    ax.plot([0, pm.GEN, pm.GEN, 0, 0], [0, 0, pm.YUK, pm.YUK, 0], color="#333", lw=0.9, ls=(0, (10, 4, 2, 4)),
            zorder=17)
    kuzey_oku(ax, pm.GEN + 25, pm.YUK + 2, boy=26)
    olcek_cubugu(ax, 470, -38, adim=50, n=4, h=5)

    fig.text(0.015, 0.968, "Model mahalle v2.1 — vaziyet planı", fontsize=24, fontweight="bold")
    fig.text(0.015, 0.946,
             f"60,0 ha · {sayi(M['konut'])} konut · {sayi(M['nufus'])} kişi · 8 komşuluk birimi · 4 araç hücresi · 2 ilkokul "
             "(her konuta ≤ 500 m ağ). v2.1: ada ortası geçitleri, kapalı T3 avluları, S2'de 1 m ön eşik (geleneksel doku kalibrasyonu). "
             f"Ölçek çubuğu esastır ({olcek}). Bütün sayılar çizimden hesaplanmıştır.",
             fontsize=11.0, color="#444")

    sag = gs[0, 1].subgridspec(3, 1, height_ratios=[0.78, 0.36, 0.44], hspace=0.07)
    ax_l = fig.add_subplot(sag[0])
    lejant(ax_l)
    ic = sag[1].subgridspec(1, 2, wspace=0.08)
    ax_t = fig.add_subplot(ic[0])
    transect_inset(ax_t)
    ax_h = fig.add_subplot(ic[1])
    tahsis_inset(ax_h)
    ax_s = fig.add_subplot(sag[2])
    sayilar(ax_s, 0)

    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"vaziyet_plani.{uz}", facecolor="white")
    plt.close(fig)
    ok = dxf_yaz(CIKTI / "vaziyet_plani.dxf")
    print("vaziyet_plani.png|svg yazıldı; DXF:", ok)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
