"""
Model mahalle v2.1 — "v1 → v2.1 değişiklikler" levhası
=================================================
Üst sıra: v1 ve v2 vaziyet şemaları (tip renkleri), v2'de numaralı değişiklik işaretleri.
Alt sıra: ilkokula ağ mesafesi, v1 (tek okul) ve v2 (iki okul).
Sağ: ana göstergeler hedefe göre (hedef = 100) v1 → v2; tek eksen.
v1 geometrisi v1_okuyucu.py ile v1 kodundan okunur (v1 dosyaları değişmez).

Çalıştırma:  python v1_v2_karsilastirma.py
Çıktılar  :  ../v1_v2_degisiklikler.png|svg
"""

import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Patch, Rectangle

import metrikler as mt
import plan_modeli as pm
import v1_okuyucu as v1
from ortak import (CIKTI, DONATI_RENK, HALO, MESAFE_RENK, MESAFE_SINIR, R_ASIM, R_ORTAK_YESIL, R_S2, R_S3, R_TOPLAYICI,
                   TIP_RENK, poligon_ciz, sayi)

M = mt.metrikleri_hesapla()
G1 = v1.v1_geometri()
P = pm.model()
R_V1 = "#eb6834"      # kategorik 2
R_V2 = "#2a78d6"      # kategorik 1 (v2.1)
R_V20 = "#1baf7a"     # kategorik 3 (v2.0)
METIN2 = "#52514e"
R_DEGISIKLIK = "#c0392b"

DONATI_TUR_RENK = {"semt_camii": "ibadet", "kucuk_cami": "ibadet", "asm": "saglik", "carsi": "carsi", "anaokulu": "egitim",
                   "konak": "sosyal", "ilkokul": "egitim", "ortaokul": "egitim", "otopark": "otopark", "teknik": "teknik"}


def _halkalar(g):
    parcalar = [g] if g.geom_type == "Polygon" else [q for q in getattr(g, "geoms", []) if q.geom_type == "Polygon"]
    return [np.asarray(p.exterior.coords) for p in parcalar]


def _eksen(ax, baslik, alt=None):
    ax.set_xlim(-8, pm.GEN + 8)
    ax.set_ylim(-8, pm.YUK + 8)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#999")
        s.set_linewidth(0.5)
    ax.set_title(baslik, fontsize=12, fontweight="bold", loc="left", pad=16 if alt else 4)
    if alt:
        ax.text(0, 1.008, alt, transform=ax.transAxes, fontsize=8.6, color="#333", va="bottom")


def sema(ax, g, surum):
    """Tip renkli vaziyet şeması (v1 ya da v2 geometrisi)."""
    ax.add_patch(Rectangle((0, 0), pm.GEN, pm.YUK, fc=R_S2, ec="none", zorder=0))
    poligon_ciz(ax, g["toplayici"], R_TOPLAYICI, zorder=0.5)
    poligon_ciz(ax, g["cadde"], "#cbc6bc", zorder=0.5)
    poligon_ciz(ax, g["diyag"], R_S3, zorder=0.6)
    for d in g["donatilar"]:
        t = d["tur"]
        if t in ("park", "spor", "cep", "bostan"):
            poligon_ciz(ax, d["poly"], R_ORTAK_YESIL, zorder=1)
        else:
            poligon_ciz(ax, d["poly"], DONATI_RENK[DONATI_TUR_RENK[t]][1], ec="#8d8a84", lw=0.3, zorder=1)
            for b in d["binalar"]:
                poligon_ciz(ax, b, DONATI_RENK[DONATI_TUR_RENK[t]][0], zorder=2)
    for c in g["cep"]:
        poligon_ciz(ax, c, R_ORTAK_YESIL, zorder=1)
    for o in g["ortaklar"]:
        poligon_ciz(ax, o, "#c3dfa9", zorder=1)
    polys, renk = [], []
    for p in g["parseller"]:
        for h in _halkalar(p["poly"]):
            polys.append(h)
            renk.append("#e9e3d4")
        for b in p["binalar"]:
            for h in _halkalar(b):
                polys.append(h)
                renk.append(TIP_RENK[p["tip"]])
    ax.add_collection(PolyCollection(polys, facecolors=renk, edgecolors="white", linewidths=0.12, zorder=2))
    if surum == "v2":
        kose = [h for p in g["parseller"] if p.get("kose") for h in _halkalar(p["binalar"][0])]
        ax.add_collection(PolyCollection(kose, facecolors="none", edgecolors=R_DEGISIKLIK, linewidths=0.8, zorder=3))
        duvar = [h for p in g["parseller"] for d in (p.get("duvar") or []) for h in _halkalar(d)]
        if duvar:
            ax.add_collection(PolyCollection(duvar, facecolors="#5b4a3f", edgecolors="#5b4a3f", linewidths=0.4, zorder=3))
        gecit = [h for gp in g.get("gecitler", []) for h in _halkalar(gp)]
        if gecit:
            ax.add_collection(PolyCollection(gecit, facecolors=R_S3, edgecolors="none", zorder=1.5))


def _v2_geom():
    return dict(toplayici=pm.TOPLAYICI, cadde=pm.CADDE, diyag=pm.DIYAG_BANT, donatilar=P["donatilar"], cep=P["cep"],
                ortaklar=P["ortaklar"], parseller=P["parseller"], gecitler=[gp for gp, _ in P["gecitler"]])


# v2'deki değişikliklerin yeri: (no, x, y, kısa metin)
DEGISIKLIK = [
    (1, 470, 300, "İlkokul A küçüldü (11.312 → 7.076 m²), meydana değmeye devam ediyor; okul geçidi"),
    (2, 469, 634, "İlkokul B (7.515 m²): kuzey yarı ≤ 500 m; iki okul 2,1 m²/kişi"),
    (3, 660, 43, "Ortaokul GD köşe adalarının tamamı (15.658 m²); GD diyagonali okul kapısında biter"),
    (4, 469, 189, "Ada (3,2) yeniden konut (T12), S2 açıldı; konak (3,3) üçgenine uzadı"),
    (5, 455, 43, "Mobilite noktaları 41 m × Z+4; kalan 9 m teknik altyapı şeridi (×4)"),
    (6, 770, 700, "KD köşe üçgeni cep parkı yerine teknik altyapı (1,1 m²/kişi)"),
    (7, 90, 62, "GB bostanının kenarında tek sıra T1 (bostan 1,0 → 0,8 ha)"),
    (8, 245, 165, "Diyagonal köşe evleri: kırpılmış T1/T2 (kırmızı çerçeve)"),
    (9, 72, 189, "T2 adaları (0,2) ve (5,7) T12 oldu (T1 payı)"),
]
# v2.1: geleneksel doku kalibrasyonu
DEGISIKLIK_21 = [
    (10, 201.5, 262, "Ada ortası 5 m S3 geçidi (T1/T2 adaları): yaya adası 0,79 → 0,45 ha (60 ha)"),
    (11, 40, 640, "Parsel cephesi geçitle yeniden bölündü: T1 K2 6,4 m · K1 7,2 m; T2 9,6 m"),
    (12, None, None, "S2 ön eşiği 1,5 → 1,0 m: cephe arası 12 m, H/W 0,72 → 0,78"),
    (13, 300, 631, "T3 avlusunun dördüncü kenarı: güney grupta tek katlı arka kanat (+2 eşiksiz 2+1), kuzeyde duvar"),
]


def degisiklik_isaretleri(ax):
    # 8: bir köşe evinin yanı (çizimden); 9: ikinci T12'ye çevrilen ada (5,7)
    kose = [p for p in P["parseller"] if p.get("kose")]
    yer = {}
    if kose:
        en = min(kose, key=lambda p: abs(p["poly"].centroid.x - 300) + abs(p["poly"].centroid.y - 560))
        c = en["poly"].centroid
        yer[8] = (c.x - 22, c.y + 22)
    isaret = [(no, *yer.get(no, (x, y))) for no, x, y, _ in DEGISIKLIK] + [(9, mx_(72), 563)]
    isaret += [(no, x, y) for no, x, y, _ in DEGISIKLIK_21 if x is not None]
    for no, x, y in isaret:
        ax.add_patch(Circle((x, y), 17, fc=R_DEGISIKLIK, ec="white", lw=1.2, zorder=10))
        ax.text(x, y, str(no), ha="center", va="center", fontsize=9, color="white", fontweight="bold", zorder=11)


def mx_(x):
    return pm.GEN - x


def ilkokul_haritasi(ax, parseller, mesafe_al, okul_polys):
    ax.add_patch(Rectangle((0, 0), pm.GEN, pm.YUK, fc=R_S2, ec="none", zorder=0))
    polys, renk, asan = [], [], []
    for p in parseller:
        m = mesafe_al(p)
        r = MESAFE_RENK[-1]
        for k in range(len(MESAFE_SINIR) - 1):
            if m <= MESAFE_SINIR[k + 1]:
                r = MESAFE_RENK[k]
                break
        for h in _halkalar(p["poly"]):
            polys.append(h)
            renk.append(r)
            if m > 500 and p["konut"] > 0:
                asan.append(h)
    ax.add_collection(PolyCollection(polys, facecolors=renk, edgecolors="white", linewidths=0.12, zorder=2))
    if asan:
        ax.add_collection(PolyCollection(asan, facecolors="none", edgecolors=R_ASIM, linewidths=0.9, zorder=3))
    for ad, g in okul_polys:
        poligon_ciz(ax, g, "#4f73a3", zorder=4)
        c = g.representative_point()
        ax.text(c.x, c.y, ad, ha="center", va="center", fontsize=11, fontweight="bold", color="white", zorder=5)


def _csv():
    import csv
    d = {}
    with open(CIKTI / "metrikler.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d[(r["kategori"], r["gosterge"])] = r
    return d


def _f(r, k):
    try:
        return float(r[k])
    except (ValueError, TypeError, KeyError):
        return None


def gosterge_grafigi(ax):
    """v1 → v2.0 → v2.1, hedefe göre endeks (hedef = 100). Tek eksen; değerler metrikler.csv'den."""
    C = _csv()
    S = [
        # (ad, (kategori, gösterge), hedef, biçim)
        ("İlkokul ≤ 500 m (% konut)", ("Erişim (ağ mesafesi)", "İlkokul ≤ 500 m"), 100, "%{:.1f}"),
        ("İlkokul ≤ 400 m (% konut, tercih)", ("Erişim (ağ mesafesi)", "İlkokul ≤ 400 m (tercih)"), 100, "%{:.0f}"),
        ("İlkokul arsası (m²/kişi; EK-2 2,0)", ("Güncel EK-2 dengesi", "İlkokul"), 2.0, "{:.2f}"),
        ("Ortaokul arsası (m²/kişi; EK-2 2,0)", ("Güncel EK-2 dengesi", "Ortaokul"), 2.0, "{:.2f}"),
        ("Teknik altyapı (m²/kişi; EK-2 1,0)", ("Güncel EK-2 dengesi", "Teknik altyapı"), 1.0, "{:.2f}"),
        ("Ağaç örtüsü, 20 yıl (%; ≥ 30)*", ("Yeşil", "Tahmini ağaç örtüsü (20 yıl)"), 30, "%{:.1f}"),
        ("S2 yaşam sokağı H/W (0,7–1,0)", ("Sokak kesiti", "S2 yaşam sokağı H/W (son durum, K2)"), 0.7, "{:.2f}"),
        ("Kavşak, yaya dahil (/km²; ≥ 300)†", ("Morfoloji (600 m pencere)", "Kavşak (yaya dahil)"), 300, "{:.0f}"),
        ("Kapalı avlu ortası (m²; 300–450)†", ("Morfoloji (600 m pencere)", "Kapalı avlu (medyan)"), 300, "{:.0f} m²"),
        ("Net yapı oturumu (%; K2 35–40)†", ("Morfoloji (600 m pencere)", "Net yapı oturumu (ada içi)"), 35, "%{:.0f}"),
        ("T1 payı (%; hedef 29)", ("Konut tipleri", "T1 payı"), 29, "%{:.1f}"),
        ("Net konut alanı (ha; 32)", ("Yoğunluk", "Net konut alanı (parsel + ada içi ortak bahçe)"), 32, "{:.1f} ha"),
        ("≤ 3 katlı binada oturan (%; ≈ 70)", ("Kat profili", "≤ 3 katlı binalardaki konut payı"), 70, "%{:.0f}"),
        ("Konut sayısı (2.250)", ("Ölçek", "Konut sayısı"), 2250, "{:,.0f}"),
        ("Zemin katta erişilebilir daire (%; ≥ 15)", ("Asansör ve erişilebilirlik",
                                                      "Zemin katta erişilebilir (eşiksiz) daire payı"), 15, "%{:.1f}"),
        ("Kamusal yeşil (m²/kişi; ≥ 10)", ("Yeşil", "Kamusal yeşil / kişi"), 10, "{:.1f}"),
        ("FUE çevre-ölçek Ç (puan; ≥ 55)", ("FUE konumu", "FUE çevre-ölçek ekseni (Ç)"), 55, "{:.1f}"),
    ]
    ys = np.arange(len(S))[::-1]
    ax.axvline(100, color="#222", lw=1.0, zorder=1)
    ax.axvspan(95, 105, color="#eceae4", zorder=0)
    for y, (ad, anahtar, h, f) in zip(ys, S):
        r = C.get(anahtar, {})
        a, b, c = _f(r, "v1_degeri"), _f(r, "v2_0"), _f(r, "v2_1")
        ix = [None if v is None else max(40.0, min(150.0, 100 * v / h)) for v in (a, b, c)]
        dolu = [v for v in ix if v is not None]
        if len(dolu) >= 2:
            ax.plot([min(dolu), max(dolu)], [y, y], color="#b9b5ad", lw=1.6, zorder=2, solid_capstyle="round")
        for v, renk, boy, z in ((ix[0], R_V1, 44, 3), (ix[1], R_V20, 44, 3.5), (ix[2], R_V2, 58, 4)):
            if v is not None:
                ax.scatter([v], [y], s=boy, color=renk, edgecolor="white", linewidth=1.4, zorder=z)
        if c is not None:
            etiket = f.format(c).replace(",", "§").replace(".", ",").replace("§", ".")
            ax.text(max(dolu) + 2.5, y, etiket, va="center", fontsize=8.4, color="#0b0b0b")
    ax.set_yticks(ys)
    ax.set_yticklabels([s_[0] for s_ in S], fontsize=8.6)
    ax.set_xlim(40, 150)
    ax.set_xlabel("hedefin yüzdesi (hedef = 100; gri bant ±%5; 40–150 dışı kenara kırpıldı)", fontsize=8.6, color=METIN2)
    ax.grid(axis="x", color="#e5e3df", lw=0.6, zorder=0)
    for kk in ("top", "right", "left"):
        ax.spines[kk].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(labelsize=8.2, colors=METIN2)
    ax.legend(handles=[Line2D([0], [0], marker="o", ls="", mfc=R_V1, mec="white", ms=8, label="v1"),
                       Line2D([0], [0], marker="o", ls="", mfc=R_V20, mec="white", ms=8, label="v2.0"),
                       Line2D([0], [0], marker="o", ls="", mfc=R_V2, mec="white", ms=9, label="v2.1 (değeri yazılı)")],
              loc="upper right", fontsize=8.6, frameon=False)
    ax.set_title("Ana göstergeler: v1 → v2.0 → v2.1", fontsize=12, fontweight="bold", loc="left", pad=40)
    ax.text(-0.02, 1.012, "* v1 kaba formül, v2 çizimdeki ağaçların taç birleşimi.\n† morfoloji_olcum.py ölçütleri, 600 m pencere. "
                          "Net konut alanının\ngüncel EK-2 ile tutarlı hedefi v2.0 27,5 · v2.1 26,8 ha.",
            transform=ax.transAxes, fontsize=7.6, color=METIN2, va="bottom")


def main():
    fig = plt.figure(figsize=(24, 15.6), dpi=150)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1.05], height_ratios=[1, 1], hspace=0.14, wspace=0.05,
                          left=0.015, right=0.985, top=0.865, bottom=0.17)
    ax = fig.add_subplot(gs[0, 0])
    sema(ax, G1, "v1")
    _eksen(ax, "v1 (26.10.2026)", f"2.222 konut · tek ilkokul 11.312 m² · diyagonalde düşen parsel {len(G1['dusen'])}")
    ax = fig.add_subplot(gs[0, 1])
    sema(ax, _v2_geom(), "v2")
    degisiklik_isaretleri(ax)
    _eksen(ax, "v2.1", f"{sayi(M['konut'])} konut · iki ilkokul {sayi(sum(M['ilkokul'].values()))} m² · köşe evi {M['kose']} · "
                       f"kapalı avlu {sum(1 for p_ in P['parseller'] if p_.get('arka_konut'))}")
    ax = fig.add_subplot(gs[1, 0])
    okul1 = [("", d["poly"]) for d in G1["donatilar"] if d["tur"] == "ilkokul"]
    ilkokul_haritasi(ax, G1["parseller"], lambda p: p["ilkokul_m"], okul1)
    _eksen(ax, "İlkokula ağ mesafesi — v1", f"≤ 500 m %96,8 · en uzak 553 m · ≤ 400 m %{sayi(100 * M['v1']['ilk400'], 1)}")
    ax = fig.add_subplot(gs[1, 1])
    mes = {id(p): m for p, m in pm.konut_mesafeleri("ilkokul")}
    okul2 = [(d["okul"], d["poly"]) for d in P["donatilar"] if d["tur"] == "ilkokul"]
    ilkokul_haritasi(ax, P["parseller"], lambda p: mes[id(p)], okul2)
    e = M["erisim"]["ilkokul"]
    _eksen(ax, "İlkokula ağ mesafesi — v2.1",
           f"≤ 500 m %{sayi(100 * e['pay_hedef'], 1)} · en uzak {sayi(e['en_fazla'])} m · ≤ 400 m %{sayi(100 * M['ilk_400'], 1)}")
    ic = gs[:, 2].subgridspec(1, 2, width_ratios=[0.40, 0.60], wspace=0.0)
    gosterge_grafigi(fig.add_subplot(ic[1]))

    # değişiklik listesi
    y0 = 0.135
    fig.text(0.015, y0 + 0.012, "v2.0'daki (1–9) ve v2.1'deki (10–13) plan değişiklikleri (numaralar v2.1 şemasında)",
             fontsize=11, fontweight="bold")
    for k, (no, _, _, m) in enumerate(DEGISIKLIK_21):
        fig.text(0.015 + 0.66, y0 - 0.02 - k * 0.022, f"{no}  {m}", fontsize=9.4, color="#0b4f8a")
    for k, (no, _, _, m) in enumerate(DEGISIKLIK):
        sut, sat = divmod(k, 5)
        fig.text(0.015 + sut * 0.33, y0 - 0.02 - sat * 0.022, f"{no}  {m}", fontsize=9.4, color="#222")
    fig.text(0.015 + 0.33, y0 - 0.02 - 4 * 0.022,
             "+  Tipoloji ve kesit: PAİY md. 34/1 asansör kuralı (T1 platform yeri, T2 ve T3 Z+2 asansör yeri, Z+3 ve T4 asansör);\n"
             "    kat 3,0 → 3,1 m; K2'de ön eşik 2,0 → 1,5 m; ağaç dikim kuralları; tahsis karması; T3 Z+2'de ≥ %15 zemin erişilebilir.",
             fontsize=9.4, color="#222", va="top", linespacing=1.6)
    # lejant
    el = [Patch(fc=TIP_RENK[t], label=t) for t in ("T1", "T2", "T3", "T4")]
    el += [Patch(fc=DONATI_RENK["egitim"][1], ec="#8d8a84", label="eğitim arsası"),
           Patch(fc=DONATI_RENK["teknik"][1], ec="#8d8a84", label="teknik / otopark"),
           Patch(fc=R_ORTAK_YESIL, label="yeşil"), Patch(fc="none", ec=R_DEGISIKLIK, label="köşe evi")]
    for k in range(len(MESAFE_RENK)):
        a, b = MESAFE_SINIR[k], MESAFE_SINIR[k + 1]
        el.append(Patch(fc=MESAFE_RENK[k], label=(f"{sayi(a)}–{sayi(b)} m" if b < 10_000 else f"> {sayi(a)} m")))
    el.append(Patch(fc="white", ec=R_ASIM, label="> 500 m"))
    fig.legend(handles=el, loc="upper left", bbox_to_anchor=(0.015, 0.932), ncol=len(el), fontsize=8.4, frameon=False,
               handlelength=1.3, columnspacing=1.0)
    fig.text(0.015, 0.965, "Model mahalle v1 → v2.1: değişiklikler", fontsize=24, fontweight="bold")
    fig.text(0.015, 0.945,
             "Aynı 60 ha, aynı sokak ağı. v2: güncel MPYY EK-2 (ilkokul ve ortaokul 2,0, teknik altyapı 1,0, sosyal-kültürel 0,75 m²/kişi), "
             "PAİY md. 34/1 asansör kuralı, Fıtrat Kodu hedefleri. v2.1: geleneksel doku kalibrasyonu (09_RAPORLAR/11). "
             "Bütün sayılar çizimden hesaplandı.",
             fontsize=11, color="#444")
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"v1_v2_degisiklikler.{uz}", facecolor="white")
    plt.close(fig)
    print("v1_v2_degisiklikler.png|svg yazıldı")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
