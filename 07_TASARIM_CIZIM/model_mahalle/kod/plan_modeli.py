"""
Model mahalle — geometri, yaya ağı ve metrikler
===============================================
60 ha (800 m × 750 m, çevredeki 24 m toplayıcı yolun iç yarısı dahil) bir
"fıtrata uygun mahalle" modelini parsel düzeyinde kurar:

  * sokak hiyerarşisi: toplayıcı yol (dış, 24 m) · S1 mahalle caddesi / çarşı (18 m,
    artı biçiminde) · S2 yaşam sokağı (10 m, paylaşımlı yüzey) · S3 yaya yolu
    (6 m ada içi geçitler) · 4 yeşil diyagonal (8 m, köşeden meydana)
  * 60 ada (≈120 × 63 m), her adada tipolojiye göre parseller ve binalar
  * merkez (meydan, semt camii, ilkokul, aile sağlık merkezi, mahalle konağı,
    çarşı, pazar, merkez parkı), 8 komşuluk birimi, mescitler, küçük camiler,
    yeşil sistem, bölgesel otoparklar, otobüs durakları
  * yaya ağı (shapely + networkx) ve her konut için ağ üzerinden yürüme mesafesi

Bütün sayılar çizimden (poligonlardan) hesaplanır; elle girilmiş bir toplam yoktur.
Bu modül hem çizim betiklerine hem de doğrulama betiğine veri sağlar.

Koordinatlar: x doğuya, y kuzeye; köken brüt alanın güneybatı köşesi (m).
"""

from __future__ import annotations

import math
from collections import defaultdict
from functools import lru_cache

import networkx as nx
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union
from shapely.strtree import STRtree

from ortak import HANE_BUYUKLUGU, KAT_YUK, ZEMIN_TICARI_YUK

# =============================================================================
# 1. Temel ölçüler
# =============================================================================
GEN, YUK = 800.0, 750.0          # brüt alan = 60,0 ha
TY = 12.0                        # 24 m toplayıcı yolun brüt alana giren iç yarısı
CADDE_G = 18.0                   # S1
S2_G = 10.0                      # S2
S3_G = 6.0                       # S3 (ada içi yaya geçidi)
DIYAG_G = 8.0                    # yeşil diyagonal
CX, CY = 400.0, 375.0            # meydanın ortası
YAYA = 10.5                      # toplayıcı yolun iç kaldırım ekseni (sınırdan, m)
ALAN = box(0, 0, GEN, YUK)
MEYDAN = box(365, 350, 435, 400)  # 70 × 50 m (cadde kesişimi dahil)

# Ada ölçüleri: her yarıda 3 sütun (x) ve 5 sıra (y)
ORTA_BANT = 8.0                  # T1/T2 adalarında ada içi ortak bahçe şeridi
ON_ESIK = 2.0                    # T1/T2 ön bahçe ("yumuşak kenar")


def _bolum(a0, a1, n, s):
    b = (a1 - a0 - (n - 1) * s) / n
    return [(a0 + k * (b + s), a0 + k * (b + s) + b) for k in range(n)]


XS = _bolum(TY, CX - CADDE_G / 2, 3, S2_G) + _bolum(CX + CADDE_G / 2, GEN - TY, 3, S2_G)
YS = _bolum(TY, CY - CADDE_G / 2, 5, S2_G) + _bolum(CY + CADDE_G / 2, YUK - TY, 5, S2_G)
# S2 aralıkları
GX = [(XS[0][1], XS[1][0]), (XS[1][1], XS[2][0]), (XS[3][1], XS[4][0]), (XS[4][1], XS[5][0])]
GY = [(YS[j][1], YS[j + 1][0]) for j in (0, 1, 2, 3, 5, 6, 7, 8)]


def ada_kutu(i, j):
    return box(XS[i][0], YS[j][0], XS[i][1], YS[j][1])


def mx(x):
    return GEN - x


def my(y):
    return YUK - y


# =============================================================================
# 2. Sokaklar
# =============================================================================
# Kapalı S2 bağlantıları: ("h", sütun i, y-aralığı ky) ya da ("v", x-aralığı kx, sıra j)
KAPALI = {
    ("h", 2, 2), ("h", 2, 3),     # merkez parkı + spor alanı (S2 parka katıldı)
    ("h", 3, 2), ("h", 3, 3),     # ilkokul yerleşkesi (meydana kadar)
    ("v", 3, 0),                  # ortaokul yerleşkesi
}
PARK_ICI_KAPALI = {("h", 2, 2), ("h", 2, 3)}   # parka katılan sokaklar yaya yolu olarak kalır


def _baglantilar():
    """S2 bağlantı ve kavşak dikdörtgenleri + eksen çizgileri."""
    bag = {}
    for kx, (gx0, gx1) in enumerate(GX):
        for j in range(10):
            y0, y1 = YS[j]
            # eksen: alt ve üst komşunun ortasına kadar uzat
            alt = YAYA if j == 0 else (CY if j == 5 else (YS[j - 1][1] + y0) / 2)
            ust = YUK - YAYA if j == 9 else (CY if j == 4 else (y1 + YS[j + 1][0]) / 2)
            xm = (gx0 + gx1) / 2
            bag[("v", kx, j)] = (box(gx0, y0, gx1, y1), LineString([(xm, alt), (xm, ust)]))
    for ky, (gy0, gy1) in enumerate(GY):
        for i in range(6):
            x0, x1 = XS[i]
            sol = YAYA if i == 0 else (CX if i == 3 else (XS[i - 1][1] + x0) / 2)
            sag = GEN - YAYA if i == 5 else (CX if i == 2 else (x1 + XS[i + 1][0]) / 2)
            ym = (gy0 + gy1) / 2
            bag[("h", i, ky)] = (box(x0, gy0, x1, gy1), LineString([(sol, ym), (sag, ym)]))
    return bag


BAGLANTI = _baglantilar()


def _kavsaklar():
    kav = {}
    for kx, (gx0, gx1) in enumerate(GX):
        for ky, (gy0, gy1) in enumerate(GY):
            kav[(kx, ky)] = box(gx0, gy0, gx1, gy1)
    return kav


KAVSAK = _kavsaklar()

TOPLAYICI = ALAN.difference(box(TY, TY, GEN - TY, YUK - TY))
CADDE = unary_union([box(CX - CADDE_G / 2, TY, CX + CADDE_G / 2, YUK - TY),
                     box(TY, CY - CADDE_G / 2, GEN - TY, CY + CADDE_G / 2)])


def s2_poligon():
    acik = [p for k, (p, _) in BAGLANTI.items() if k not in KAPALI]
    kav = []
    for (kx, ky), p in KAVSAK.items():
        # kavşağa bağlanan dört bağlantıdan biri açıksa kavşak sokaktır
        if any(p.buffer(0.01).intersects(BAGLANTI[k][0]) for k in BAGLANTI
               if k not in KAPALI):
            kav.append(p)
    return unary_union(acik + kav)


S2 = s2_poligon()
KAPALI_SOKAK = unary_union([BAGLANTI[k][0] for k in KAPALI])

# Yeşil diyagonaller: iç köşelerden meydanın ortasına
KOSELER = [(TY, TY), (GEN - TY, TY), (TY, YUK - TY), (GEN - TY, YUK - TY)]
DIYAG_EKSEN = [LineString([k, (CX, CY)]) for k in KOSELER]
DIYAG_BANT = unary_union([l.buffer(DIYAG_G / 2, cap_style="flat") for l in DIYAG_EKSEN]).difference(MEYDAN)
DIYAG_BANT = DIYAG_BANT.intersection(box(TY, TY, GEN - TY, YUK - TY))

# Çarşı yaya bölümü (E-W caddenin merkez adalarına bakan kesimi) — pazar yeri
CARSI_YAYA = unary_union([box(XS[2][0], CY - 9, CX - 9, CY + 9), box(CX + 9, CY - 9, XS[3][1], CY + 9)])


def ada_kalan(i, j):
    """Ada dikdörtgeni − diyagonal bant − meydan."""
    return ada_kutu(i, j).difference(DIYAG_BANT).difference(MEYDAN)


def parca(i, j, ref, ek=None):
    """Adanın diyagonalle bölünmüş parçalarından ref noktasını içereni döndürür."""
    g = ada_kalan(i, j)
    if ek is not None:
        g = g.intersection(ek)
    parcalar = [g] if g.geom_type == "Polygon" else list(g.geoms)
    p = Point(ref)
    for q in parcalar:
        if q.buffer(0.5).contains(p):
            return q
    return max(parcalar, key=lambda q: q.area)


def parca_sec(g, ref):
    """Çok parçalı geometriden ref noktasını içeren parçayı döndürür."""
    parcalar = [g] if g.geom_type == "Polygon" else list(g.geoms)
    p = Point(ref)
    for q in parcalar:
        if q.buffer(0.5).contains(p):
            return q
    return max(parcalar, key=lambda q: q.area)


# Mobilite noktaları (bölgesel otopark + market + durak): caddelerin toplayıcıya bağlandığı dört kapıda,
# fırıldak düzeninde. Her biri Z+3 otopark yapısı; zemin katta market, bisiklet atölyesi, kargo noktası.
MOBILITE = {
    "güney": box(XS[3][0], YS[0][0], XS[3][0] + 50, YS[0][1]),
    "doğu": box(XS[5][1] - 50, YS[5][0], XS[5][1], YS[5][1]),
    "kuzey": box(XS[2][1] - 50, YS[9][0], XS[2][1], YS[9][1]),
    "batı": box(XS[0][0], YS[4][0], XS[0][0] + 50, YS[4][1]),
}
MOBILITE_ZEMIN_TICARI = 1200.0  # m² / yapı (zemin katın yarısı)


# =============================================================================
# 3. Donatılar (merkez, köşeler, komşuluk yeşilleri)
# =============================================================================
def _donatilar():
    D = []

    def ekle(ad, tur, renk, poly, binalar=(), girisler=(), kat=1, kisa=None, **kw):
        D.append(dict(ad=ad, tur=tur, renk=renk, poly=poly, binalar=list(binalar), girisler=list(girisler),
                      kat=kat, kisa=kisa or ad, **kw))

    # --- Merkez parkı + açık semt spor alanı (sütun 2, sıra 2–4) ----------------
    park = box(XS[2][0], 199.0, XS[2][1], YS[4][1]).difference(MEYDAN)
    ekle("Merkez parkı", "park", "yesil", park, kisa="Merkez parkı", merkez=True)
    spor = box(XS[2][0], YS[2][0], XS[2][1], 199.0)
    ekle("Açık semt spor alanı", "spor", "spor", spor, kisa="Spor alanı")

    # --- Semt camii + avlu (ada 2,5 diyagonalin batısı) --------------------------
    p = parca(2, 5, (300, 400))
    harim = box(296, 398, 322, 424)
    son_cemaat = box(322, 398, 330, 424)
    minare = Point(332.5, 427.5).buffer(2.2)
    ekle("Semt camii ve avlusu", "semt_camii", "ibadet", p, [harim, son_cemaat, minare],
         [(365, 392), (318, 384), (345, 425)], kat=2, kisa="Semt camii")

    # --- Aile sağlık merkezi + eczane (ada 2,5 diyagonalin doğusu) ---------------
    p = parca(2, 5, (382, 432))
    ekle("Aile sağlık merkezi ve eczane", "asm", "saglik", p,
         [box(358, 418, 388, 444)], [(391, 428), (375, 404)], kat=2, kisa="ASM")

    # --- Çarşı / kapalı pazar (ada 3,5 diyagonalin doğusu) -----------------------
    p = parca(3, 5, (500, 400))
    carsi_bina = [box(452, 386, 526, 398), box(512, 398, 526, 444)]
    ekle("Çarşı ve kapalı pazar", "carsi", "carsi", p, carsi_bina,
         [(470, 384), (440, 395), (526, 420)], kat=3, kisa="Çarşı")

    # --- Anaokulu (kuzey) (ada 3,5 diyagonalin batısı) ---------------------------
    p = parca(3, 5, (418, 432))
    ekle("Anaokulu (kuzey)", "anaokulu", "egitim", p, [box(411, 420, 437, 444)],
         [(409, 432), (430, 446.8)], kat=2, kisa="Anaokulu")

    # --- Mahalle konağı (ada 3,4 diyagonalin doğusu + kapanan S2 parçası) ------------
    p = parca_sec(box(XS[3][0], YS[3][1], XS[3][1], YS[4][1]).difference(DIYAG_BANT).difference(MEYDAN), (500, 340))
    konak = [box(452, 352, 526, 364), box(506, 306, 526, 352)]
    ekle("Mahalle konağı (muhtarlık, meclis, kütüphane, gençlik, aile, yaşlı günevi, hamam)",
         "konak", "sosyal", p, konak, [(470, 366), (440, 358), (528.6, 330)], kat=3, kisa="Mahalle konağı")

    # --- Eğitim yerleşkesi: ilkokul meydana değer; anaokulu (güney) cadde köşesinde --
    ana_s = box(XS[3][0], 195.0, XS[3][0] + 40, 240.0)
    ilk = parca_sec(box(XS[3][0], 195.0, XS[3][1], MEYDAN.bounds[1]).difference(DIYAG_BANT).difference(MEYDAN),
                    (430, 250)).difference(ana_s)
    ilk_bina = [box(411, 318, 424, 348), box(424, 318, 446, 331), box(452, 252, 466, 300), box(411, 252, 452, 266)]
    ekle("İlkokul (≈18 derslik)", "ilkokul", "egitim", ilk, ilk_bina,
         [(418, 350), (409, 290), (475, 300), (500, 222)], kat=3, kisa="İlkokul")
    ekle("Anaokulu (güney)", "anaokulu", "egitim", ana_s, [box(411, 212, 437, 236)],
         [(409, 222), (430, 195)], kat=2, kisa="Anaokulu")

    # --- Ortaokul (güneydoğu köşesi, komşu mahalleyle ortak) ---------------------
    p5 = parca(5, 0, (690, 30))
    orta = unary_union([box(XS[4][1] - 80, YS[0][0], XS[4][1], YS[0][1]), BAGLANTI[("v", 3, 0)][0], p5])
    orta_bina = [box(590, 50, 660, 64), box(590, 30, 604, 50), box(604, 30, 650, 42)]
    ekle("Ortaokul (komşu mahalleyle ortak)", "ortaokul", "egitim", orta, orta_bina,
         [(620, 12), (690, 74.8), (728, 60)], kat=3, kisa="Ortaokul")
    ekle("Okul önü cep parkı", "cep", "yesil", parca(5, 0, (775, 60)), kisa="")

    # --- Mobilite noktaları (bölgesel otopark Z+3) -------------------------------
    for ad, kutu in MOBILITE.items():
        x0, y0, x1, y1 = kutu.bounds
        bina = box(x0 + 3, y0 + 4, x1 - 3, y1 - 4)
        girisler = [((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)]
        ekle(f"Mobilite noktası ({ad}): bölgesel otopark, market, bisiklet", "otopark", "otopark", kutu, [bina],
             girisler, kat=4, kisa="P", ticari=MOBILITE_ZEMIN_TICARI)

    # --- Köşeler: bostan, teknik altyapı, kenar parkı ----------------------------
    ekle("Bostan ve hobi bahçesi", "bostan", "bostan", parca(0, 0, (110, 30)), kisa="Bostan")
    ekle("Teknik altyapı (trafo, geri dönüşüm)", "teknik", "teknik", parca(0, 0, (25, 60)),
         [box(16, 52, 34, 70)], [(12, 60)], kat=1, kisa="")
    ekle("Bostan ve hobi bahçesi", "bostan", "bostan", parca(5, 9, (mx(110), my(30))), kisa="Bostan")
    ekle("Kenar cep parkı", "cep", "yesil", parca(5, 9, (mx(25), my(60))), kisa="")
    ekle("Kenar parkı (yeşil kuşak girişi)", "park", "yesil", parca(0, 9, (100, my(40))), kisa="Kenar parkı")
    ekle("Teknik altyapı (su deposu, yağmur suyu)", "teknik", "teknik", parca(0, 9, (25, my(60))),
         [box(16, 680, 34, 698)], [(12, 690)], kat=1, kisa="")

    # --- Komşuluk yeşilleri (8 × 0,5 ha) -----------------------------------------
    kb_park = {
        1: box(XS[1][0], YS[1][0], XS[1][0] + 80, YS[1][1]),
        2: box(XS[0][1] - 80, YS[3][0], XS[0][1], YS[3][1]),
        3: box(XS[0][1] - 80, YS[6][0], XS[0][1], YS[6][1]),
        4: box(XS[1][0], YS[8][0], XS[1][0] + 80, YS[8][1]),
        5: box(XS[4][1] - 80, YS[8][0], XS[4][1], YS[8][1]),
        6: box(XS[5][0], YS[6][0], XS[5][0] + 80, YS[6][1]),
        7: box(XS[5][0], YS[3][0], XS[5][0] + 80, YS[3][1]),
        8: box(XS[4][1] - 80, YS[1][0], XS[4][1], YS[1][1]),
    }
    for k, p in kb_park.items():
        x0, y0, x1, y1 = p.bounds
        # çok amaçlı saha (30 × 18 m): parkın merkeze uzak köşesinde
        sx = x0 + 6 if (x0 + x1) / 2 < CX else x1 - 36
        sy = y0 + 6 if (y0 + y1) / 2 < CY else y1 - 24
        ekle(f"Komşuluk yeşili KB-{k}", "park", "yesil", p, kisa=f"KB-{k} yeşili", kb=k,
             saha=box(sx, sy, sx + 30, sy + 18))

    # --- Küçük camiler (diyagonal üzerinde, iki birimin ortak sınırında) ---------
    def kucuk_cami(i, j, ref, kutu, harim):
        p = parca(i, j, ref).intersection(kutu)
        ekle("Küçük cami", "kucuk_cami", "ibadet", p, [harim], [harim.centroid.coords[0]], kat=1, kisa="Küçük cami")

    # (1,2): diyagonalin doğusunda, alt köşe
    kucuk_cami(1, 2, (240, 170), box(226, YS[2][0], XS[1][1], 186),
               box(238, 163, 254, 179))
    kucuk_cami(4, 2, (mx(240), 170), box(XS[4][0], YS[2][0], mx(226), 186),
               box(mx(254), 163, mx(238), 179))
    kucuk_cami(1, 7, (240, my(170)), box(226, my(186), XS[1][1], YS[7][1]),
               box(238, my(179), 254, my(163)))
    kucuk_cami(4, 7, (mx(240), my(170)), box(XS[4][0], my(186), mx(226), YS[7][1]),
               box(mx(254), my(179), mx(238), my(163)))

    # Alan düzeltmesi: girişleri olmayan donatılara poligon merkezini giriş say
    for d in D:
        if not d["girisler"]:
            d["girisler"] = []
    return D


DONATILAR = _donatilar()
DONATI_POLY = unary_union([d["poly"] for d in DONATILAR])


# =============================================================================
# 4. Konut adaları: program tablosu
# =============================================================================
# Bölgeler (transect): K1 köy kenarı · K2 mahalle genel · K3 mahalle merkezi · K4 semt çarşısı
# Program kodları:
#   T1      iki sıra büyüyebilen sıra ev
#   T2      iki sıra avlulu çok kuşaklı ev
#   T12     güney sıra T1, kuzey sıra T2 (T2'nin bahçesi güneyde kalır)
#   T3      iki sıra avlu grubu + iki S3 geçidi
#   T4      çevre adası, zeminde dükkân (taraf: hangi cephede dükkân)
#   T4Y     tek sıra çevre adası çubuğu (dükkânlı) + arkada T1 sırası
#   T2S     tek sıra T2 (derin parsel)
#   T3S     dar şerit: her sırada tek avlu grubu
PROGRAM = {
    # sıra 0 (güney kenarı: semt tarafı)
    (1, 0): ("T12", "K2", {}),
    (2, 0): ("T4Y", "K4", {"dukkan": "S", "kose": "E"}),
    # sıra 1
    (0, 1): ("T12", "K1", {}),
    (2, 1): ("T3", "K3", {"kat": 4, "uc": "E"}),
    (3, 1): ("T3", "K3", {"kat": 4, "uc": "W"}),
    (5, 1): ("T12", "K2", {}),
    # sıra 2
    (0, 2): ("T2", "K1", {}),
    (1, 2): ("T1", "K2", {}),
    (4, 2): ("T1", "K2", {}),
    (5, 2): ("T12", "K2", {}),
    # sıra 3
    (1, 3): ("T12", "K2", {}),
    (4, 3): ("T12", "K2", {}),
    # sıra 4 (E-W caddenin güneyi)
    (1, 4): ("T4Y", "K3", {"dukkan": "N", "kose": "E"}),
    (4, 4): ("T3", "K3", {"kat": 4, "dukkan": "N"}),
    (5, 4): ("T4Y", "K4", {"dukkan": "N", "kose": "E"}),
    # sıra 5 (E-W caddenin kuzeyi)
    (0, 5): ("T3", "K3", {"kat": 4, "dukkan": "S"}),
    (1, 5): ("T3", "K3", {"kat": 4, "dukkan": "S"}),
    (4, 5): ("T4Y", "K3", {"dukkan": "S", "kose": "W"}),
    # sıra 6
    (1, 6): ("T12", "K2", {}),
    (2, 6): ("T3", "K3", {"kat": 4, "uc": "E"}),
    (3, 6): ("T3", "K3", {"kat": 4, "uc": "W"}),
    (4, 6): ("T12", "K2", {}),
    # sıra 7
    (0, 7): ("T2", "K1", {}),
    (1, 7): ("T1", "K2", {}),
    (2, 7): ("T3", "K3", {"kat": 3, "uc": "E"}),
    (3, 7): ("T3", "K3", {"kat": 3, "uc": "W"}),
    (4, 7): ("T1", "K2", {}),
    (5, 7): ("T2", "K2", {}),
    # sıra 8
    (0, 8): ("T12", "K1", {}),
    (2, 8): ("T3", "K2", {"kat": 3}),
    (3, 8): ("T3", "K2", {"kat": 3}),
    (5, 8): ("T12", "K2", {}),
    # sıra 9 (kuzey kenarı: yeşil kuşak)
    (1, 9): ("T12", "K1", {}),
    (3, 9): ("T1", "K1", {}),
    (4, 9): ("T12", "K1", {}),
}

# Komşuluk yeşili adalarının kalan şeritleri ve diğer kısmi adalar
KISMI = [
    # (alt dikdörtgen, program, bölge, seçenekler)
    (box(XS[1][0] + 80, YS[1][0], XS[1][1], YS[1][1]), "T3S", "K2", {"kat": 3}),       # KB-1
    (box(XS[0][0], YS[3][0], XS[0][1] - 80, YS[3][1]), "T3S", "K1", {"kat": 3}),       # KB-2
    (box(XS[0][0], YS[6][0], XS[0][1] - 80, YS[6][1]), "T3S", "K1", {"kat": 3}),       # KB-3
    (box(XS[1][0] + 80, YS[8][0], XS[1][1], YS[8][1]), "T3S", "K2", {"kat": 3}),       # KB-4
    (box(XS[4][0], YS[8][0], XS[4][1] - 80, YS[8][1]), "T3S", "K2", {"kat": 3}),       # KB-5
    (box(XS[5][0] + 80, YS[6][0], XS[5][1], YS[6][1]), "T3S", "K2", {"kat": 3}),       # KB-6
    (box(XS[5][0] + 80, YS[3][0], XS[5][1], YS[3][1]), "T3S", "K2", {"kat": 3}),       # KB-7
    (box(XS[4][0], YS[1][0], XS[4][1] - 80, YS[1][1]), "T3S", "K2", {"kat": 3}),       # KB-8
    (box(XS[4][0], YS[0][0], XS[4][1] - 80, YS[0][1]), "T3S", "K4", {"kat": 4}),       # ortaokul yanı
    (box(XS[3][0], YS[2][0], XS[3][1], 195.0), "T2S", "K2", {}),                       # ilkokul güneyi
    # mobilite noktalarının yanında kalan kısımlar
    (box(XS[3][0] + 50, YS[0][0], XS[3][1], YS[0][1]), "T4Y", "K4", {"dukkan": "S", "kose": "E"}),
    (box(XS[5][0], YS[5][0], XS[5][1] - 50, YS[5][1]), "T3", "K3", {"kat": 4, "dukkan": "S"}),
    (box(XS[2][0], YS[9][0], XS[2][1] - 50, YS[9][1]), "T1", "K1", {}),
    (box(XS[0][0] + 50, YS[4][0], XS[0][1], YS[4][1]), "T3", "K3", {"kat": 4, "dukkan": "N"}),
]

# Tipoloji ölçüleri
T1_GEN, T2_GEN = 6.0, 9.2        # hedef parsel genişlikleri (m)
T1_EV_DER, T2_EV_DER = 9.0, 11.0  # bina derinliği (T1: çekirdek)
T1_GENISLEME = 4.0                # T1 arka genişleme payı (zemin)
T3_GEN, T3_GECIT = 36.0, 6.0
T3_SOKAK_KANADI, T3_YAN_KANAT_G, T3_YAN_KANAT_L = 10.0, 7.0, 13.0
T3_ON = 1.5
T4_DER = 12.0
T4_MODUL = 24.0                   # T4 parsel cephesi (m): kat başına 2+1 + 1+1 + 2+1
KONUT_BRUT_T3 = 120.0             # m² / daire (sokak kanadı, dolaşım payı dahil)
KONUT_BRUT_T4 = 100.0             # m² / daire (T4: 1+1, 2+1, 3+1 karışık; dolaşım dahil)


def _parsel(poly, tip, bolge, konut, kat, binalar, kapi, ada, **kw):
    d = dict(poly=poly, tip=tip, bolge=bolge, konut=konut, kat=kat, binalar=binalar, kapi=kapi,
             ada=ada, ticari=0.0, kat_alani=0.0, zemin_donati=None)
    d.update(kw)
    return d


def _siralar(x0, x1, y0, y1, tip_g, tip_k, bolge, ada):
    """İki sıra (güney: tip_g, kuzey: tip_k) sıra ev; ortada ortak bahçe şeridi."""
    out = []
    der = (y1 - y0 - ORTA_BANT) / 2
    for taraf, tip in (("S", tip_g), ("N", tip_k)):
        if tip is None:
            continue
        hedef = T1_GEN if tip == "T1" else T2_GEN
        n = max(1, int((x1 - x0) // hedef))
        w = (x1 - x0) / n
        for k in range(n):
            xa, xb = x0 + k * w, x0 + (k + 1) * w
            if taraf == "S":
                p = box(xa, y0, xb, y0 + der)
                ev_der = T1_EV_DER if tip == "T1" else T2_EV_DER
                ev = box(xa, y0 + ON_ESIK, xb, y0 + ON_ESIK + ev_der)
                gen = box(xa, y0 + ON_ESIK + ev_der, xb, y0 + ON_ESIK + ev_der + T1_GENISLEME) if tip == "T1" else None
                kapi = ((xa + xb) / 2, y0)
            else:
                p = box(xa, y1 - der, xb, y1)
                ev_der = T1_EV_DER if tip == "T1" else T2_EV_DER
                ev = box(xa, y1 - ON_ESIK - ev_der, xb, y1 - ON_ESIK)
                gen = box(xa, y1 - ON_ESIK - ev_der - T1_GENISLEME, xb, y1 - ON_ESIK - ev_der) if tip == "T1" else None
                kapi = ((xa + xb) / 2, y1)
            if tip == "T1":
                # son durum: çekirdek Z+1 + üst kat (Z+2) + arka zemin genişlemesi
                kat_alani = ev.area * 3 + gen.area
                out.append(_parsel(p, "T1", bolge, 1, 3, [ev], kapi, ada, genisleme=gen, kat_alani=kat_alani,
                                   cekirdek_kat=2))
            else:
                out.append(_parsel(p, "T2", bolge, 2, 3, [ev], kapi, ada, kat_alani=ev.area * 3))
    orta = box(x0, y0 + der, x1, y1 - der)
    return out, [orta], []


def _t2_tek(x0, x1, y0, y1, bolge, ada):
    out = []
    n = max(1, int((x1 - x0) // T2_GEN))
    w = (x1 - x0) / n
    for k in range(n):
        xa, xb = x0 + k * w, x0 + (k + 1) * w
        p = box(xa, y0, xb, y1)
        ev = box(xa, y0 + ON_ESIK, xb, y0 + ON_ESIK + T2_EV_DER)
        out.append(_parsel(p, "T2", bolge, 2, 3, [ev], ((xa + xb) / 2, y0), ada, kat_alani=ev.area * 3))
    return out, [], []


def _avlu_grubu(xa, xb, ya, yb, taraf, kat, bolge, ada, dukkan=False):
    """Tek avlu grubu: sokak kanadı (kat) + iki yan kanat (Z+1) + ortak avlu."""
    w = xb - xa
    if taraf == "S":
        sk = box(xa, ya + T3_ON, xb, ya + T3_ON + T3_SOKAK_KANADI)
        yk0 = ya + T3_ON + T3_SOKAK_KANADI
        yanlar = [box(xa, yk0, xa + T3_YAN_KANAT_G, yk0 + T3_YAN_KANAT_L),
                  box(xb - T3_YAN_KANAT_G, yk0, xb, yk0 + T3_YAN_KANAT_L)]
        kapi = ((xa + xb) / 2, ya)
    else:
        sk = box(xa, yb - T3_ON - T3_SOKAK_KANADI, xb, yb - T3_ON)
        yk1 = yb - T3_ON - T3_SOKAK_KANADI
        yanlar = [box(xa, yk1 - T3_YAN_KANAT_L, xa + T3_YAN_KANAT_G, yk1),
                  box(xb - T3_YAN_KANAT_G, yk1 - T3_YAN_KANAT_L, xb, yk1)]
        kapi = ((xa + xb) / 2, yb)
    kat_basi = max(2, round(w * T3_SOKAK_KANADI / KONUT_BRUT_T3))
    zemin = 0 if dukkan else kat_basi - 1                 # kapı altı geçit + bisiklet/çöp odası
    yan_konut = 4 if w >= 28 else 2                       # yan kanatlarda dubleks
    konut = zemin + kat_basi * (kat - 1) + yan_konut
    kat_alani = sk.area * kat - 3.5 * T3_SOKAK_KANADI + sum(y.area for y in yanlar) * 2
    p = box(xa, ya, xb, yb)
    avlu = p.difference(unary_union([sk] + yanlar)).difference(box(xa, ya, xb, ya + T3_ON) if taraf == "S"
                                                               else box(xa, yb - T3_ON, xb, yb))
    ticari = (sk.area - 3.5 * T3_SOKAK_KANADI) if dukkan else 0.0
    return _parsel(p, "T3", bolge, konut, kat, [sk] + yanlar, kapi, ada, kat_alani=kat_alani,
                   bina_katlari=[kat, 2, 2], avlu=avlu, ticari=ticari, dukkan=dukkan, yan_konut=yan_konut)


def _t3(x0, x1, y0, y1, kat, bolge, ada, gecitli=True, dukkan="", uc=""):
    out, gecit_poly, gecit_eksen = [], [], []
    W = x1 - x0
    if gecitli and W >= 60:
        n = max(1, round((W + T3_GECIT) / (T3_GEN + T3_GECIT)))
        w = (W - (n - 1) * T3_GECIT) / n
    else:
        n, w = 1, W
    ym = (y0 + y1) / 2
    for k in range(n):
        xa = x0 + k * (w + T3_GECIT)
        xb = xa + w
        uc_mu = (uc == "W" and k == 0) or (uc == "E" and k == n - 1)
        out.append(_avlu_grubu(xa, xb, y0, ym, "S", kat, bolge, ada, dukkan=("S" in dukkan) or uc_mu))
        out.append(_avlu_grubu(xa, xb, ym, y1, "N", kat, bolge, ada, dukkan=("N" in dukkan) or uc_mu))
        if k < n - 1:
            g0, g1 = xb, xb + T3_GECIT
            gecit_poly.append(box(g0, y0, g1, y1))
            gecit_eksen.append(LineString([((g0 + g1) / 2, y0 - S2_G / 2), ((g0 + g1) / 2, y1 + S2_G / 2)]))
    return out, [], list(zip(gecit_poly, gecit_eksen))


def _t4(x0, x1, y0, y1, dukkan, kose, bolge, ada, kat=4):
    """Çevre adası: 12 m derinlikte halka bina, ortada ortak avlu; ~20 m'lik küçük parseller."""
    out = []
    ic = box(x0 + T4_DER, y0 + T4_DER, x1 - T4_DER, y1 - T4_DER)
    halka = box(x0, y0, x1, y1).difference(ic)
    # cephe parçaları: uzun kenarlarda ~20 m, kısa kenarlarda köşe kareleri dahil
    kenarlar = {
        "S": [(x0, y0, x1, y0 + T4_DER)], "N": [(x0, y1 - T4_DER, x1, y1)],
        "W": [(x0, y0 + T4_DER, x0 + T4_DER, y1 - T4_DER)], "E": [(x1 - T4_DER, y0 + T4_DER, x1, y1 - T4_DER)],
    }
    for taraf, [(a0, b0, a1, b1)] in kenarlar.items():
        uzun = (a1 - a0) > (b1 - b0)
        L = (a1 - a0) if uzun else (b1 - b0)
        n = max(1, round(L / T4_MODUL))
        for k in range(n):
            if uzun:
                pa = box(a0 + k * L / n, b0, a0 + (k + 1) * L / n, b1)
                kapi = ((pa.bounds[0] + pa.bounds[2]) / 2, y0 if taraf == "S" else y1)
            else:
                pa = box(a0, b0 + k * L / n, a1, b0 + (k + 1) * L / n)
                kapi = (x0 if taraf == "W" else x1, (pa.bounds[1] + pa.bounds[3]) / 2)
            dukkanli = taraf in dukkan
            kose_mu = False
            if uzun:
                cx_ = (pa.bounds[0] + pa.bounds[2]) / 2
                for kk in kose.split(",") if kose else []:
                    if not kk:
                        continue
                    if ("E" in kk and cx_ > x1 - L / n) or ("W" in kk and cx_ < x0 + L / n):
                        if ("N" in kk and taraf == "N") or ("S" in kk and taraf == "S") or len(kk) == 1:
                            kose_mu = True
            k_kat = kat + (1 if kose_mu else 0)
            alan = pa.area
            zemin_konut = 0.0 if dukkanli else alan * 0.85    # dükkânsız zeminde konut / atölye
            konut_alan = alan * (k_kat - 1) + zemin_konut
            konut = konut_alan / KONUT_BRUT_T4
            out.append(_parsel(pa, "T4", bolge, konut, k_kat, [pa], kapi, ada, kat_alani=alan * k_kat,
                               ticari=alan if dukkanli else 0.0, dukkan=dukkanli))
    # konut sayısını parsel bazında tamsayıya yuvarla (toplam korunur)
    _yuvarla(out)
    return out, [ic], []


def _t4_cubuk(x0, x1, y0, y1, dukkan, kose, bolge, ada, kat=4):
    """Tek sıra çevre adası çubuğu (dükkân cephesi) + arkada T1 sırası."""
    out = []
    der = (y1 - y0 - ORTA_BANT) / 2
    if dukkan == "S":
        bant = (y0, y0 + T4_DER)
        p_y = (y0, y0 + der)
    else:
        bant = (y1 - T4_DER, y1)
        p_y = (y1 - der, y1)
    L = x1 - x0
    n = max(1, round(L / T4_MODUL))
    for k in range(n):
        xa, xb = x0 + k * L / n, x0 + (k + 1) * L / n
        b = box(xa, bant[0], xb, bant[1])
        p = box(xa, p_y[0], xb, p_y[1])
        kose_mu = (kose == "E" and k == n - 1) or (kose == "W" and k == 0)
        k_kat = kat + (1 if kose_mu else 0)
        konut = b.area * (k_kat - 1) / KONUT_BRUT_T4
        kapi = ((xa + xb) / 2, y0 if dukkan == "S" else y1)
        out.append(_parsel(p, "T4", bolge, konut, k_kat, [b], kapi, ada, kat_alani=b.area * k_kat,
                           ticari=b.area, dukkan=True, avlu=p.difference(b)))
    _yuvarla(out)
    # arka sıra: T1
    if dukkan == "S":
        t1, orta, _ = _siralar(x0, x1, y0, y1, None, "T1", bolge, ada)
    else:
        t1, orta, _ = _siralar(x0, x1, y0, y1, "T1", None, bolge, ada)
    return out + t1, orta, []


def _yuvarla(parseller):
    toplam = sum(p["konut"] for p in parseller)
    hedef = round(toplam)
    tam = [math.floor(p["konut"]) for p in parseller]
    kalan = sorted(range(len(parseller)), key=lambda i: -(parseller[i]["konut"] - tam[i]))
    for i in kalan[: hedef - sum(tam)]:
        tam[i] += 1
    for p, t in zip(parseller, tam):
        p["konut"] = t


def _program_uret(prog, x0, x1, y0, y1, bolge, sec, ada):
    if prog == "T1":
        return _siralar(x0, x1, y0, y1, "T1", "T1", bolge, ada)
    if prog == "T2":
        return _siralar(x0, x1, y0, y1, "T2", "T2", bolge, ada)
    if prog == "T12":
        return _siralar(x0, x1, y0, y1, "T1", "T2", bolge, ada)
    if prog == "T2S":
        return _t2_tek(x0, x1, y0, y1, bolge, ada)
    if prog == "T3":
        return _t3(x0, x1, y0, y1, sec.get("kat", 3), bolge, ada, gecitli=True, dukkan=sec.get("dukkan", ""),
                   uc=sec.get("uc", ""))
    if prog == "T3S":
        return _t3(x0, x1, y0, y1, sec.get("kat", 3), bolge, ada, gecitli=False, dukkan=sec.get("dukkan", ""))
    if prog == "T4":
        return _t4(x0, x1, y0, y1, sec.get("dukkan", ""), sec.get("kose", ""), bolge, ada)
    if prog == "T4Y":
        return _t4_cubuk(x0, x1, y0, y1, sec.get("dukkan", "S"), sec.get("kose", ""), bolge, ada)
    raise ValueError(prog)


# =============================================================================
# 5. Zemin kat donatıları (mescit, kreş, bakkal-fırın, çeşme) ve duraklar
# =============================================================================
# Mescit, kreş ve bakkal-fırın T3/T4 zemin katlarına, çeşmeler sokak kenarına yerleşir.
# Konumlar elle değil, yaya ağı üzerinde "en çok konutu kapsayan" açgözlü seçimle bulunur
# (bkz. _zemin_sec). Her komşuluk biriminde en az bir mescit, bakkal ve çeşme bulunması zorunludur.
ZEMIN_KURAL = {
    #  tür      yarıçap  taban hedefler                    en çok  konuttan düşülen  m²
    "mescit": dict(r=150, taban=("kucuk_cami", "semt_camii"), tavan=16, dus=1, alan=120),
    "kres": dict(r=400, taban=("anaokulu",), tavan=6, dus=3, alan=400),
    "bakkal": dict(r=300, taban=("dukkan",), tavan=12, dus=1, alan=100),
    "cesme": dict(r=250, taban=(), tavan=20, dus=0, alan=0),
}

# Otobüs durakları: S1 hattı (mahalle içinden geçen tek hat) + toplayıcı yol (semt hattı)
DURAKLAR = {
    "S1": [(CX, 150), (CX, 412), (CX, 600)],
    "toplayici": [(YAYA, CY), (GEN - YAYA, CY), (CX, YAYA), (CX, YUK - YAYA), (YAYA, 120), (GEN - YAYA, 630),
                  (200, YUK - YAYA), (600, YAYA)],
}


# =============================================================================
# 6. Planı kur (geometri)
# =============================================================================
@lru_cache(maxsize=1)
def plan_kur():
    engel = unary_union([DIYAG_BANT, MEYDAN, DONATI_POLY])
    parseller, ortaklar, gecitler = [], [], []
    for (i, j), (prog, bolge, sec) in PROGRAM.items():
        x0, x1 = XS[i]
        y0, y1 = YS[j]
        p, o, g = _program_uret(prog, x0, x1, y0, y1, bolge, sec, (i, j))
        parseller += p
        ortaklar += o
        gecitler += g
    for kutu, prog, bolge, sec in KISMI:
        x0, y0, x1, y1 = kutu.bounds
        ada = next((i, j) for i in range(6) for j in range(10) if ada_kutu(i, j).contains(kutu.centroid))
        p, o, g = _program_uret(prog, x0, x1, y0, y1, bolge, sec, ada)
        parseller += p
        ortaklar += o
        gecitler += g

    # --- diyagonal / donatı ile kırpma -----------------------------------------
    kalan, dusen = [], []
    for p in parseller:
        if p["poly"].intersection(engel).area < 1.0:
            kalan.append(p)
            continue
        binalar_ok = all(b.intersection(engel).area < 0.5 for b in p["binalar"])
        gen = p.get("genisleme")
        if gen is not None and gen.intersection(engel).area > 0.5:
            p["genisleme"] = None                    # genişleme payı diyagonale taşmasın
            p["kat_alani"] -= gen.area
        kirpik = p["poly"].difference(engel)
        if kirpik.geom_type == "MultiPolygon":
            kirpik = max(kirpik.geoms, key=lambda g: g.area)
        oran = kirpik.area / p["poly"].area
        esik = 0.55 if p["tip"] in ("T1", "T2") else 0.80
        if binalar_ok and oran >= esik:
            p["poly"] = kirpik
            if p.get("avlu") is not None:
                p["avlu"] = p["avlu"].difference(engel)
            kalan.append(p)
        else:
            dusen.append(p)
    parseller = kalan
    ortaklar = [o.difference(engel) for o in ortaklar]
    ortaklar = [o for o in ortaklar if o.area > 1]
    gecitler = [(gp.difference(engel), ge) for gp, ge in gecitler if gp.difference(engel).area > 10]

    # --- cep yeşilleri: adalarda parsel/ortak/geçit/donatı dışında kalan -------
    dolu = unary_union([p["poly"] for p in parseller] + ortaklar + [g for g, _ in gecitler] + [DONATI_POLY])
    adalar = unary_union([ada_kutu(i, j) for i in range(6) for j in range(10)])
    artik = adalar.difference(dolu).difference(DIYAG_BANT).difference(MEYDAN).difference(KAPALI_SOKAK)
    ceple = [g for g in (artik.geoms if hasattr(artik, "geoms") else [artik]) if g.area >= 40]

    return dict(parseller=parseller, dusen=dusen, ortaklar=ortaklar, gecitler=gecitler,
                zemin=[], cep=ceple, donatilar=DONATILAR)


# =============================================================================
# 7. Yaya ağı, zemin kat donatılarının seçimi ve erişim
# =============================================================================
def _coklu_kaynak(G, kaynaklar, cutoff=None):
    """kaynaklar: [(düğüm, başlangıç uzaklığı)] → {düğüm: en kısa mesafe}."""
    k = "__KAYNAK__"
    G.add_node(k)
    for dugum, bag in kaynaklar:
        if G.has_edge(k, dugum):
            G[k][dugum]["weight"] = min(G[k][dugum]["weight"], bag)
        else:
            G.add_edge(k, dugum, weight=bag)
    d = nx.single_source_dijkstra_path_length(G, k, cutoff=cutoff, weight="weight")
    G.remove_node(k)
    d.pop(k, None)
    return d


def _zemin_sec(G, erisim, hedefler, P):
    """Mescit, kreş, bakkal ve çeşmeleri açgözlü kapsama ile yerleştirir.

    Adaylar: mescit, kreş, bakkal için T3/T4 zemin katları (mescit ayrıca ≥ 300 m² cep parkında
    küçük bir yapı olabilir); çeşme için konut önlerindeki sokak noktaları. Amaç, yarıçap içinde
    kalan ve henüz karşılanmamış konut sayısını en çoklamaktır. Sonra her komşuluk biriminde en az bir
    tane olacak biçimde tamamlanır.
    """
    parseller = P["parseller"]
    konut_dugum = {n: erisim[("konut", n)] for n in range(len(parseller))}
    dugum_parsel = defaultdict(list)
    for n, (dg, bg) in konut_dugum.items():
        dugum_parsel[dg].append((n, bg))
    agirlik = {n: max(p["konut"], 0) for n, p in enumerate(parseller)}

    def kapsam(dugum, bag, r):
        d = nx.single_source_dijkstra_path_length(G, dugum, cutoff=max(r - bag, 0), weight="weight")
        out = set()
        for dg, m in d.items():
            for n, bg in dugum_parsel.get(dg, []):
                if m + bg + bag <= r:
                    out.add(n)
        return out

    def taban_karsilanan(turler_r):
        k = set()
        for t, rr in turler_r:
            d = _coklu_kaynak(G, [erisim[x] for x in hedefler.get(t, [])], cutoff=rr)
            k |= {n for n, (dg, bg) in konut_dugum.items() if d.get(dg, 1e9) + bg <= rr}
        return k

    ev_aday = []
    for n, p in enumerate(parseller):
        if p["tip"] in ("T3", "T4"):
            bx = p["binalar"][0].centroid
            kx, ky = p["kapi"]
            ev_aday.append(dict(ad=("ev", n), dugum=konut_dugum[n], xy=(kx + (bx.x - kx) * 0.35, ky + (bx.y - ky) * 0.35),
                                ev=n, birim=birim_bul(p["kapi"])))
    cep_aday = []
    for n, g in enumerate(P["cep"]):
        if g.area >= 300 and ("cep", n) in erisim:
            q = g.representative_point()
            cep_aday.append(dict(ad=("cep", n), dugum=erisim[("cep", n)], xy=(q.x, q.y), ev=None, birim=birim_bul((q.x, q.y))))
    for n, d in enumerate(P["donatilar"]):
        if d["tur"] == "otopark":                      # mobilite noktasının zemin katı
            q = d["binalar"][0].centroid
            ev_aday.append(dict(ad=("donati", n), dugum=erisim[("donati", n, 0)], xy=(q.x, q.y), ev=None,
                                birim=birim_bul((q.x, q.y))))
        elif d["tur"] == "park" and d.get("kb") is None and not d.get("merkez"):   # kenar parkı
            q = d["poly"].representative_point()
            cep_aday.append(dict(ad=("donati", n), dugum=erisim[("donati", n, 0)], xy=(q.x, q.y), ev=None,
                                 birim=birim_bul((q.x, q.y))))
    sokak_aday = []
    gorulen = set()
    for n in range(0, len(parseller), 2):
        dg = konut_dugum[n][0]
        if dg not in gorulen:
            gorulen.add(dg)
            sokak_aday.append(dict(ad=("sokak", dg), dugum=(dg, 0.0), xy=dg, ev=None, birim=birim_bul(dg)))

    kullanilan = set()
    secim = []
    for tur, kural in ZEMIN_KURAL.items():
        r = kural["r"]
        if tur == "mescit":
            karsilanan = taban_karsilanan([("kucuk_cami", 250), ("semt_camii", 400)])
            adaylar = ev_aday + cep_aday
        elif tur == "cesme":
            karsilanan = set()
            adaylar = list(sokak_aday)
        else:
            karsilanan = taban_karsilanan([(t, r) for t in kural["taban"]])
            adaylar = list(ev_aday)
        adaylar = [a for a in adaylar if a["ad"] not in kullanilan]
        kap = {a["ad"]: kapsam(*a["dugum"], r) for a in adaylar}
        saf = set()
        secilen = []

        def kazanc(a):
            g1 = sum(agirlik[n] for n in kap[a["ad"]] - karsilanan)
            g2 = sum(agirlik[n] for n in kap[a["ad"]] - saf) if tur == "mescit" else 0
            return (g1, g2)

        while len(secilen) < kural["tavan"] and adaylar:
            en = max(adaylar, key=kazanc)
            if kazanc(en) == (0, 0):
                break
            secilen.append(en)
            karsilanan |= kap[en["ad"]]
            saf |= kap[en["ad"]]
            adaylar = [a for a in adaylar if a["ad"] != en["ad"]]
        for no in range(1, 9):
            if tur == "kres" or any(a["birim"] == no for a in secilen):
                continue
            yerel = [a for a in adaylar if a["birim"] == no]
            if yerel:
                en = max(yerel, key=lambda a: sum(agirlik[n] for n in kap[a["ad"]] - saf))
                secilen.append(en)
                saf |= kap[en["ad"]]
                adaylar = [a for a in adaylar if a["ad"] != en["ad"]]
        for a in secilen:
            kullanilan.add(a["ad"])
            ev = parseller[a["ev"]] if a["ev"] is not None else None
            if ev is not None:
                if not ev.get("dukkan"):
                    ev["konut"] = max(0, ev["konut"] - kural["dus"])
                ev["ticari"] += kural["alan"]
            secim.append(dict(tur=tur, xy=a["xy"], ev=ev, erisim=a["dugum"], bagimsiz=(a["ad"][0] in ("cep", "donati"))))
    return secim


@lru_cache(maxsize=1)
def ag_kur():
    P = plan_kur()
    sokak_cizgi = []
    halka = LineString([(YAYA, YAYA), (GEN - YAYA, YAYA), (GEN - YAYA, YUK - YAYA), (YAYA, YUK - YAYA), (YAYA, YAYA)])
    sokak_cizgi.append(halka)
    sokak_cizgi.append(LineString([(CX, YAYA), (CX, YUK - YAYA)]))
    sokak_cizgi.append(LineString([(YAYA, CY), (GEN - YAYA, CY)]))
    for k, (_, ln) in BAGLANTI.items():
        if k not in KAPALI:
            sokak_cizgi.append(ln)
    for _, ge in P["gecitler"]:
        sokak_cizgi.append(ge)
    yaya_cizgi = [LineString([(YAYA if x < CX else GEN - YAYA, YAYA if y < CY else YUK - YAYA), (CX, CY)])
                  for (x, y) in KOSELER]
    for k in PARK_ICI_KAPALI:
        yaya_cizgi.append(BAGLANTI[k][1])
    sokak_birlesik = unary_union(sokak_cizgi)
    for d in P["donatilar"]:
        if d["tur"] in ("park", "spor", "cep", "bostan"):
            c = d["poly"].centroid if d["poly"].contains(d["poly"].centroid) else d["poly"].representative_point()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                uzun = LineString([(c.x, c.y), (c.x + dx * 300, c.y + dy * 300)])
                kes = uzun.intersection(sokak_birlesik)
                if kes.is_empty:
                    continue
                noktalar = [kes] if kes.geom_type == "Point" else [g for g in getattr(kes, "geoms", []) if g.geom_type == "Point"]
                if not noktalar:
                    continue
                en = min(noktalar, key=lambda q: q.distance(c))
                if en.distance(c) < 120:
                    yaya_cizgi.append(LineString([(c.x, c.y), (en.x, en.y)]))
    for (x, y) in MEYDAN.exterior.coords[:-1]:
        yaya_cizgi.append(LineString([(x, y), (CX, CY)]))

    tum = unary_union(sokak_cizgi + yaya_cizgi)
    parcalar = []
    for ln in (tum.geoms if hasattr(tum, "geoms") else [tum]):
        c = list(ln.coords)
        for a, b in zip(c[:-1], c[1:]):
            if Point(a).distance(Point(b)) > 1e-6:
                parcalar.append((a, b))
    seg_cizgi = [LineString(s) for s in parcalar]
    seg_agac = STRtree(seg_cizgi)
    sokak_agac = STRtree(sokak_cizgi)

    def anahtar(xy):
        return (round(xy[0], 2), round(xy[1], 2))

    eklemeler = defaultdict(list)
    erisim = {}

    def bagla(kimlik, xy, yalniz_sokak=False):
        pt = Point(xy)
        if yalniz_sokak:
            idx = sokak_agac.query_nearest(pt)[0]
            q = sokak_cizgi[idx].interpolate(sokak_cizgi[idx].project(pt))
        else:
            q = pt
        sidx = int(seg_agac.query_nearest(q)[0])
        s = seg_cizgi[sidx]
        t = s.project(q)
        q2 = s.interpolate(t)
        eklemeler[sidx].append((t, anahtar(q2.coords[0])))
        erisim[kimlik] = (anahtar(q2.coords[0]), pt.distance(q2))

    for n, p in enumerate(P["parseller"]):
        bagla(("konut", n), p["kapi"], yalniz_sokak=True)
    hedefler = defaultdict(list)
    for n, d in enumerate(P["donatilar"]):
        girisler = list(d["girisler"])
        if d["tur"] in ("park", "spor", "cep", "bostan"):
            sinir = d["poly"].exterior
            girisler = [sinir.interpolate(s).coords[0] for s in range(0, int(sinir.length), 20)]
        for m, xy in enumerate(girisler):
            kim = ("donati", n, m)
            bagla(kim, xy)
            hedefler[d["tur"]].append(kim)
            if d["tur"] == "park" and d["poly"].area >= 4999:
                hedefler["yesil05"].append(kim)
            if d["tur"] in ("park", "cep"):
                hedefler["oyun"].append(kim)
            if d.get("merkez"):
                hedefler["merkez_parki"].append(kim)
            if d["tur"] == "anaokulu":
                hedefler["anaokulu_kres"].append(kim)
            if d["tur"] in ("spor", "ortaokul"):
                hedefler["spor_saha"].append(kim)
            if d["tur"] == "otopark":
                hedefler["dukkan"].append(kim)
        if d.get("saha") is not None:
            kim = ("saha", n)
            bagla(kim, d["saha"].centroid.coords[0])
            hedefler["spor_saha"].append(kim)
    for n, g in enumerate(P["cep"]):
        if g.area >= 150:
            kim = ("cep", n)
            bagla(kim, g.representative_point().coords[0])
            hedefler["oyun"].append(kim)
    for hat, liste in DURAKLAR.items():
        for n, xy in enumerate(liste):
            kim = ("durak", hat, n)
            bagla(kim, xy)
            hedefler["durak"].append(kim)
    bagla(("meydan",), (CX, CY))
    hedefler["meydan"].append(("meydan",))
    for n, p in enumerate(P["parseller"]):
        if p.get("dukkan"):
            hedefler["dukkan"].append(("konut", n))
    hedefler["dukkan"] += hedefler["carsi"]

    G = nx.Graph()
    for sidx, (a, b) in enumerate(parcalar):
        L = Point(a).distance(Point(b))
        dizi = [(0.0, anahtar(a))] + sorted(eklemeler.get(sidx, [])) + [(L, anahtar(b))]
        for (t0, n0), (t1, n1) in zip(dizi[:-1], dizi[1:]):
            if n0 != n1:
                w = max(t1 - t0, 0.0)
                if G.has_edge(n0, n1):
                    w = min(w, G[n0][n1]["weight"])
                G.add_edge(n0, n1, weight=w)

    # --- zemin kat donatıları -----------------------------------------------------
    P["zemin"] = _zemin_sec(G, erisim, hedefler, P)
    for n, z in enumerate(P["zemin"]):
        kim = ("zemin", n)
        erisim[kim] = z["erisim"]
        hedefler[z["tur"]].append(kim)
        if z["tur"] == "kres":
            hedefler["anaokulu_kres"].append(kim)
        if z["tur"] == "bakkal":
            hedefler["dukkan"].append(kim)
    return dict(G=G, erisim=erisim, hedefler=dict(hedefler), sokak_cizgi=sokak_cizgi, yaya_cizgi=yaya_cizgi,
                parcalar=parcalar)


def model():
    """Tam model: geometri + yaya ağı + zemin kat donatıları (konut sayıları kesinleşmiş)."""
    ag_kur()
    return plan_kur()


@lru_cache(maxsize=None)
def mesafe_haritasi(tur):
    """Bir donatı türüne her ağ düğümünden en kısa yürüme mesafesi."""
    A = ag_kur()
    return _coklu_kaynak(A["G"], [A["erisim"][k] for k in A["hedefler"].get(tur, [])])


def konut_mesafeleri(tur):
    """Her konut parseli için (parsel, mesafe) listesi."""
    A = ag_kur()
    P = plan_kur()
    d = mesafe_haritasi(tur)
    out = []
    for n, p in enumerate(P["parseller"]):
        dugum, bag = A["erisim"][("konut", n)]
        out.append((p, d.get(dugum, math.inf) + bag))
    return out


# =============================================================================
# 8. Komşuluk birimleri
# =============================================================================
def komsuluk_birimleri():
    """Her çeyrek kendi diyagonaliyle iki üçgene bölünür → 8 birim (KB-1 … KB-8)."""
    q = {
        "GB": box(TY, TY, CX - 9, CY - 9), "GD": box(CX + 9, TY, GEN - TY, CY - 9),
        "KB": box(TY, CY + 9, CX - 9, YUK - TY), "KD": box(CX + 9, CY + 9, GEN - TY, YUK - TY),
    }
    tanim = [  # (no, çeyrek, üçgenin köşeleri)
        (1, "GB", [(TY, TY), (CX, TY), (CX, CY)]),
        (2, "GB", [(TY, TY), (CX, CY), (TY, CY)]),
        (3, "KB", [(TY, YUK - TY), (TY, CY), (CX, CY)]),
        (4, "KB", [(TY, YUK - TY), (CX, CY), (CX, YUK - TY)]),
        (5, "KD", [(GEN - TY, YUK - TY), (CX, YUK - TY), (CX, CY)]),
        (6, "KD", [(GEN - TY, YUK - TY), (CX, CY), (GEN - TY, CY)]),
        (7, "GD", [(GEN - TY, TY), (GEN - TY, CY), (CX, CY)]),
        (8, "GD", [(GEN - TY, TY), (CX, CY), (CX, TY)]),
    ]
    return [(no, Polygon(k).intersection(q[c])) for no, c, k in tanim]


def birim_bul(xy):
    p = Point(xy)
    en, ad = 1e9, None
    for no, g in komsuluk_birimleri():
        d = g.distance(p)
        if d < en:
            en, ad = d, no
    return ad


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    P = model()
    tips = defaultdict(int)
    for p in P["parseller"]:
        tips[p["tip"]] += p["konut"]
    print("Konut:", dict(tips), "toplam", sum(tips.values()))
    print("Düşen parsel:", len(P["dusen"]), "cep:", len(P["cep"]), round(sum(g.area for g in P["cep"])))
    for d in P["donatilar"]:
        print(f"{d['ad'][:40]:40s} {d['poly'].area:9.0f}")
