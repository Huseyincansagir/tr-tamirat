"""
Model mahalle v2 — geometri, yaya ağı, ağaçlar ve tahsis
========================================================
60 ha (800 m × 750 m, çevredeki 24 m toplayıcı yolun iç yarısı dahil) bir
"fıtrata uygun mahalle" modelini parsel düzeyinde kurar. v1'in kodundan
türetilmiştir (07_TASARIM_CIZIM/model_mahalle/kod/plan_modeli.py; v1 dosyaları
değiştirilmedi).

v1 → v2 değişiklikleri (her biri aşağıda "v2:" diye işaretli):
  1. İki ilkokul: A (güney, meydana değer) ve B (kuzey). Güncel MPYY EK-2:
     ilkokul 2,0 m²/kişi, okul başına asgari 5.000 m². Her konuta ≤ 500 m (ağ).
  2. Ortaokul ≥ 2,0 m²/kişi: güneydoğu köşe adalarının tamamı; GD diyagonali okul
     kapısında (S2 ekseninde) biter.
  3. Teknik altyapı ≥ 1,0 m²/kişi: üç köşe üçgeni + her mobilite noktasında 9 m'lik
     servis şeridi (servis aracı hücreye girmez).
  4. Mobilite noktası 41 m × Z+4 (v1: 50 m × Z+3): aynı otopark oranı, daha az arazi.
  5. Diyagonalin kestiği T1/T2 parselleri düşürülmez; bina kırpılarak "köşe evi" olur
     (diyagonale bakan cephe = okul yolunda sokakta göz).
  6. Ön eşik K2'de 1,5 m (K1'de 2,0 m) ve kat yüksekliği 3,1 m: S2 H/W ≥ 0,7.
  7. İlkokul A'nın güneyindeki S2 yeniden açıldı; ada (3,2) T12 oldu. T2 adaları
     (0,2) ve (5,7) T12'ye çevrildi (T1 payı). Kuzey K3 avlu grupları Z+3.
  8. Ağaçlar tek fonksiyondan üretilir (agac_noktalari): çizim ve taç örtüsü
     metriği aynı noktalardan hesaplanır (v1'de formül).
  9. Tahsis karması (kooperatif / sosyal kiralık / piyasa) parsel grubu düzeyinde
     işaretlenir (v1 açık sorusu 8).

v2.0 → v2.1 (geleneksel doku kalibrasyonu, 09_RAPORLAR/11_geleneksel_doku_morfolojisi.md §3;
"v2.1:" diye işaretli). MM_SURUM=2.0 ortam değişkeniyle v2.0 aynı koddan yeniden üretilir:
 10. T1/T2 adalarının ortasından 5 m'lik kamusal S3 geçidi (yaya adası ≈ 0,45 ha; kavşak ↑).
 11. Parsel cephesi geçitle yeniden bölünür: T1 K2'de 6,4 m, K1'de 7,2 m; T2 9,6 m.
 12. S2 ön eşiği K2'de 1,0 m (cephe arası 12 m; H/W ≈ 0,78).
 13. T3 avlusunun dördüncü kenarı: güney sıra grupta tek katlı arka kanat (2 eşiksiz 2+1), yan kanatlar
     ona kadar uzar (kapalı avlu ≈ 330 m²); kuzey sıra grupta yan duvarlar (avlu kış güneşi korunur).

Bütün sayılar çizimden (poligonlardan) ve yaya ağından hesaplanır; elle girilmiş
bir toplam yoktur. Koordinatlar: x doğuya, y kuzeye; köken güneybatı köşe (m).
"""

from __future__ import annotations

import math
import os
from collections import defaultdict
from functools import lru_cache

import networkx as nx
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union
from shapely.strtree import STRtree

from ortak import HANE_BUYUKLUGU, KAT_YUK, ZEMIN_TICARI_YUK

# =============================================================================
# 0. v2 tasarım anahtarları (seçenekler burada değiştirilir)
# =============================================================================
SURUM = os.environ.get("MM_SURUM", "2.1")   # "2.0" ya da "2.1"
KALIBRE = SURUM != "2.0"                     # v2.1: geleneksel doku kalibrasyonu
GECIT_G = 5.0                                # v2.1: T1/T2 ada ortası S3 geçidi (m); 3,5 m engelsiz yürüme
T1_GEN_K1 = 6.5 if KALIBRE else 6.0          # v2.1: K1'de daha geniş T1 parseli (yarım sırada 8 parsel ≈ 7,2 m)
T3_ARKA_DER = 5.0                            # v2.1: T3 güney sıra grubunun tek katlı arka kanadı (m)
T3_ARKA_KONUT = 2                            # v2.1: arka kanatta eşiksiz 2+1 sayısı
ILKOKUL_B_ADA = (3, 8)            # v2: kuzey ilkokulunun adası; adaylar (2,7) (3,7) (2,8) (3,8) denendi (model_mahalle_v2.md §8)
if os.environ.get("MM_ILKOKUL_B_ADA"):   # yalnız deneme için: "i,j"
    ILKOKUL_B_ADA = tuple(int(v) for v in os.environ["MM_ILKOKUL_B_ADA"].split(","))
TEKNIK_SERIT = 9.0                # v2: mobilite noktasında teknik altyapı servis şeridi (m)
MOBILITE_LOT = 50.0               # mobilite noktası arsası (otopark + teknik şerit), m
MOBILITE_KAT = 5                  # v2: Z+4 (v1: Z+3)
KOSE_BINA_ESIK = 0.60             # v2: kırpılan bina, özgün oturumun en az bu kadarı kalırsa "köşe evi"
KOSE_PARSEL_ESIK = 0.45           # v2: kırpılan parsel için alt sınır (özgün alana oranı)
T2_KOSE_ESIK = 0.80               # v2: T2 iki bağımsız bölümü ancak bu oranın üstünde korur; altında T1 olur
BOSTAN_T1_DER = 27.4              # v2: GB bostanının kenarındaki tek sıra T1'in parsel derinliği (m)

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

ORTA_BANT = 8.0                  # T1/T2 adalarında ada içi ortak bahçe şeridi
ON_ESIK_K1 = 2.0                 # K1 köy kenarı ön eşik (v1 ile aynı)
ON_ESIK_K2 = 1.0 if KALIBRE else 1.5   # v2.1: 1,0 m (v2.0: 1,5; v1: 2,0) → S2 cephe arası 12 m
ON_ESIK = ON_ESIK_K2             # tipoloji çizimlerinin esas aldığı değer (K2)


def on_esik(bolge):
    return ON_ESIK_K1 if bolge == "K1" else ON_ESIK_K2


def _bolum(a0, a1, n, s):
    b = (a1 - a0 - (n - 1) * s) / n
    return [(a0 + k * (b + s), a0 + k * (b + s) + b) for k in range(n)]


XS = _bolum(TY, CX - CADDE_G / 2, 3, S2_G) + _bolum(CX + CADDE_G / 2, GEN - TY, 3, S2_G)
YS = _bolum(TY, CY - CADDE_G / 2, 5, S2_G) + _bolum(CY + CADDE_G / 2, YUK - TY, 5, S2_G)
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
    ("h", 3, 3),                  # ilkokul A yerleşkesi (meydana kadar). v2: ("h", 3, 2) yeniden açıldı
    ("v", 3, 0),                  # ortaokul yerleşkesi
}
PARK_ICI_KAPALI = {("h", 2, 2), ("h", 2, 3)}   # parka katılan sokaklar yaya yolu olarak kalır


def _baglantilar():
    """S2 bağlantı ve kavşak dikdörtgenleri + eksen çizgileri."""
    bag = {}
    for kx, (gx0, gx1) in enumerate(GX):
        for j in range(10):
            y0, y1 = YS[j]
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
        if any(p.buffer(0.01).intersects(BAGLANTI[k][0]) for k in BAGLANTI if k not in KAPALI):
            kav.append(p)
    return unary_union(acik + kav)


S2 = s2_poligon()
KAPALI_SOKAK = unary_union([BAGLANTI[k][0] for k in KAPALI])

# Yeşil diyagonaller: iç köşelerden meydanın ortasına.
# v2: GD diyagonali köşede değil, ortaokul yerleşkesinin kuzeyindeki S2 ekseninde başlar.
KOSELER = [(TY, TY), (GEN - TY, TY), (TY, YUK - TY), (GEN - TY, YUK - TY)]


def _diyag_baslangic(k):
    if k == (GEN - TY, TY):
        y_s = (YS[0][1] + YS[1][0]) / 2
        t = (y_s - k[1]) / (CY - k[1])
        return (k[0] + (CX - k[0]) * t, y_s)
    return k


DIYAG_BASLANGIC = [_diyag_baslangic(k) for k in KOSELER]
DIYAG_EKSEN = [LineString([k, (CX, CY)]) for k in DIYAG_BASLANGIC]
DIYAG_BANT = unary_union([l.buffer(DIYAG_G / 2, cap_style="flat") for l in DIYAG_EKSEN]).difference(MEYDAN)
DIYAG_BANT = DIYAG_BANT.intersection(box(TY, TY, GEN - TY, YUK - TY))

CARSI_YAYA = unary_union([box(XS[2][0], CY - 9, CX - 9, CY + 9), box(CX + 9, CY - 9, XS[3][1], CY + 9)])


def ada_kalan(i, j):
    """Ada dikdörtgeni − diyagonal bant − meydan."""
    return ada_kutu(i, j).difference(DIYAG_BANT).difference(MEYDAN)


def parca(i, j, ref, ek=None):
    """Adanın diyagonalle bölünmüş parçalarından ref noktasını içereni döndürür."""
    g = ada_kalan(i, j)
    if ek is not None:
        g = g.intersection(ek)
    return parca_sec(g, ref)


def parca_sec(g, ref):
    """Çok parçalı geometriden ref noktasını içeren parçayı döndürür."""
    parcalar = [g] if g.geom_type == "Polygon" else list(g.geoms)
    p = Point(ref)
    for q in parcalar:
        if q.buffer(0.5).contains(p):
            return q
    return max(parcalar, key=lambda q: q.area)


# Mobilite noktaları (bölgesel otopark + market + durak): caddelerin toplayıcıya bağlandığı dört kapıda.
# v2: 50 m'lik arsa = kapı tarafında 41 m otopark yapısı (Z+4) + iç tarafta 9 m teknik altyapı şeridi.
def _mobilite():
    L, T = MOBILITE_LOT, TEKNIK_SERIT
    m = {}
    # güney: kapı batıda (S1 caddesi)
    x0, y0, y1 = XS[3][0], YS[0][0], YS[0][1]
    m["güney"] = (box(x0, y0, x0 + L - T, y1), box(x0 + L - T, y0, x0 + L, y1))
    # doğu: kapı doğuda (toplayıcı)
    x1, y0, y1 = XS[5][1], YS[5][0], YS[5][1]
    m["doğu"] = (box(x1 - L + T, y0, x1, y1), box(x1 - L, y0, x1 - L + T, y1))
    # kuzey: kapı doğuda (S1 caddesi)
    x1, y0, y1 = XS[2][1], YS[9][0], YS[9][1]
    m["kuzey"] = (box(x1 - L + T, y0, x1, y1), box(x1 - L, y0, x1 - L + T, y1))
    # batı: kapı batıda (toplayıcı)
    x0, y0, y1 = XS[0][0], YS[4][0], YS[4][1]
    m["batı"] = (box(x0, y0, x0 + L - T, y1), box(x0 + L - T, y0, x0 + L, y1))
    return m


MOBILITE = _mobilite()
MOBILITE_ZEMIN_TICARI = 1200.0  # m² / yapı (zemin katın yarısı: market, bisiklet atölyesi, kargo)


# =============================================================================
# 3. Donatılar (merkez, okullar, köşeler, komşuluk yeşilleri)
# =============================================================================
def _okul_b(i, j):
    """v2: kuzey ilkokulu. Bütün ada; derslik kanadı caddeye ve kuzeye bakar, spor salonu güney köşede."""
    x0, x1 = XS[i]
    y0, y1 = YS[j]
    cadde_dogu = i == 2                      # ada caddenin batısındaysa cadde doğu kenarda
    poly = box(x0, y0, x1, y1)
    if cadde_dogu:
        kanat1 = box(x1 - 15, y0 + 10, x1 - 2, y1 - 2)
        kanat2 = box(x0 + 30, y1 - 15, x1 - 15, y1 - 2)
        salon = box(x0 + 3, y0 + 4, x0 + 39, y0 + 28)
        cadde_giris = (x1, (y0 + y1) / 2)
    else:
        kanat1 = box(x0 + 2, y0 + 10, x0 + 15, y1 - 2)
        kanat2 = box(x0 + 15, y1 - 15, x1 - 30, y1 - 2)
        salon = box(x1 - 39, y0 + 4, x1 - 3, y0 + 28)
        cadde_giris = (x0, (y0 + y1) / 2)
    girisler = [cadde_giris, ((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1), (x1 if not cadde_dogu else x0, (y0 + y1) / 2)]
    return poly, [kanat1, kanat2, salon], girisler


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

    # --- Semt camii + avlu ---------------------------------------------------------
    p = parca(2, 5, (300, 400))
    harim = box(296, 398, 322, 424)
    son_cemaat = box(322, 398, 330, 424)
    minare = Point(332.5, 427.5).buffer(2.2)
    ekle("Semt camii ve avlusu", "semt_camii", "ibadet", p, [harim, son_cemaat, minare],
         [(365, 392), (318, 384), (345, 425)], kat=2, kisa="Semt camii")

    # --- Aile sağlık merkezi + eczane ------------------------------------------------
    p = parca(2, 5, (382, 432))
    ekle("Aile sağlık merkezi ve eczane", "asm", "saglik", p,
         [box(358, 418, 388, 444)], [(391, 428), (375, 404)], kat=2, kisa="ASM")

    # --- Çarşı / kapalı pazar ----------------------------------------------------------
    p = parca(3, 5, (500, 400))
    carsi_bina = [box(452, 386, 526, 398), box(512, 398, 526, 444)]
    ekle("Çarşı ve kapalı pazar", "carsi", "carsi", p, carsi_bina,
         [(470, 384), (440, 395), (526, 420)], kat=3, kisa="Çarşı")

    # --- Anaokulu (kuzey) --------------------------------------------------------------
    p = parca(3, 5, (418, 432))
    ekle("Anaokulu (kuzey)", "anaokulu", "egitim", p, [box(411, 420, 437, 444)],
         [(409, 432), (430, 446.8)], kat=2, kisa="Anaokulu")

    # --- Mahalle konağı: v2'de diyagonalin doğusundaki üçgen (3,3)'e kadar uzar ----------
    #     (sosyal-kültürel ≥ 0,75 m²/kişi, güncel EK-2)
    p = parca_sec(box(XS[3][0], YS[3][0], XS[3][1], YS[4][1]).difference(DIYAG_BANT).difference(MEYDAN), (500, 340))
    konak = [box(452, 352, 526, 364), box(506, 296, 526, 352)]
    ekle("Mahalle konağı (muhtarlık, meclis, kütüphane, gençlik, aile, yaşlı günevi, hamam)",
         "konak", "sosyal", p, konak, [(470, 366), (440, 358), (528.6, 320), (528.6, 268)], kat=3, kisa="Mahalle konağı")

    # --- v2: güney eğitim yerleşkesi = ilkokul A + anaokulu (güney) -----------------------
    #     (3,3) + kapalı S2 + (3,4)'ün diyagonal batısı; meydana değer. (3,2) konuta döndü.
    kampus = parca_sec(box(XS[3][0], YS[3][0], XS[3][1], MEYDAN.bounds[1]).difference(DIYAG_BANT).difference(MEYDAN),
                       (430, 260))
    ana_s = box(XS[3][0], YS[3][0], XS[3][0] + 40, YS[3][0] + 45)
    ilk_a = kampus.difference(ana_s)
    ilk_a_bina = [box(411, 288, 424, 346), box(424, 288, 466, 300), box(452, 236, 492, 260)]
    ekle("İlkokul A (güney)", "ilkokul", "egitim", ilk_a, ilk_a_bina,
         [(416, 350), (409, 298.2), (480, YS[3][0]), (XS[3][1], 240)], kat=3, kisa="İlkokul A", okul="A")
    ekle("Anaokulu (güney)", "anaokulu", "egitim", ana_s, [box(411, 236, 437, 262)],
         [(409, 252), (430, YS[3][0])], kat=2, kisa="Anaokulu")

    # --- v2: kuzey ilkokulu (B) -----------------------------------------------------------
    pb, bb, gb = _okul_b(*ILKOKUL_B_ADA)
    ekle("İlkokul B (kuzey)", "ilkokul", "egitim", pb, bb, gb, kat=3, kisa="İlkokul B", okul="B")

    # --- v2: ortaokul = (4,0) + kapalı S2 + (5,0) bütünüyle; köşede okul sahası ------------
    orta = box(XS[4][0], YS[0][0], XS[5][1], YS[0][1])
    orta_bina = [box(552, 52, 650, 66), box(552, 18, 566, 52), box(662, 18, 702, 46)]
    ekle("Ortaokul (komşu mahalleyle ortak)", "ortaokul", "egitim", orta, orta_bina,
         [(600, YS[0][0]), (XS[4][0], 40), (620, YS[0][1]), (735, YS[0][1])], kat=3, kisa="Ortaokul",
         saha=box(714, 20, 780, 58))

    # --- Mobilite noktaları (bölgesel otopark Z+4) + teknik servis şeritleri ----------------
    for ad, (kutu, serit) in MOBILITE.items():
        x0, y0, x1, y1 = kutu.bounds
        bina = box(x0 + 3, y0 + 4, x1 - 3, y1 - 4)
        girisler = [((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)]
        ekle(f"Mobilite noktası ({ad}): bölgesel otopark, market, bisiklet", "otopark", "otopark", kutu, [bina],
             girisler, kat=MOBILITE_KAT, kisa="P", ticari=MOBILITE_ZEMIN_TICARI)
        sx0, sy0, sx1, sy1 = serit.bounds
        ekle(f"Teknik altyapı servis şeridi ({ad}): trafo, geri dönüşüm, şarj", "teknik", "teknik", serit,
             [box(sx0 + 1, sy0 + 6, sx1 - 1, sy0 + 20)], [((sx0 + sx1) / 2, sy0)], kat=1, kisa="")

    # --- Köşeler: bostan, teknik altyapı, kenar parkı ----------------------------
    ekle("Bostan ve hobi bahçesi", "bostan", "bostan",
         parca(0, 0, (110, 30)).difference(box(XS[0][0], YS[0][1] - BOSTAN_T1_DER, XS[0][1], YS[0][1])), kisa="Bostan")
    ekle("Teknik altyapı (trafo, geri dönüşüm)", "teknik", "teknik", parca(0, 0, (25, 60)),
         [box(16, 52, 34, 70)], [(12, 60)], kat=1, kisa="")
    ekle("Bostan ve hobi bahçesi", "bostan", "bostan", parca(5, 9, (mx(110), my(30))), kisa="Bostan")
    # v2: KD köşe üçgeni cep parkı yerine teknik altyapı (ısı merkezi, yağmur suyu deposu)
    ekle("Teknik altyapı (ısı merkezi, yağmur suyu deposu)", "teknik", "teknik", parca(5, 9, (mx(25), my(60))),
         [box(mx(34), my(70), mx(16), my(52))], [(mx(12), my(60))], kat=1, kisa="")
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
        sx = x0 + 6 if (x0 + x1) / 2 < CX else x1 - 36
        sy = y0 + 6 if (y0 + y1) / 2 < CY else y1 - 24
        ekle(f"Komşuluk yeşili KB-{k}", "park", "yesil", p, kisa=f"KB-{k} yeşili", kb=k,
             saha=box(sx, sy, sx + 30, sy + 18))

    # --- Küçük camiler (diyagonal üzerinde, iki birimin ortak sınırında) ---------
    def kucuk_cami(i, j, ref, kutu, harim):
        p = parca(i, j, ref).intersection(kutu)
        ekle("Küçük cami", "kucuk_cami", "ibadet", p, [harim], [harim.centroid.coords[0]], kat=1, kisa="Küçük cami")

    kucuk_cami(1, 2, (240, 170), box(226, YS[2][0], XS[1][1], 186), box(238, 163, 254, 179))
    kucuk_cami(4, 2, (mx(240), 170), box(XS[4][0], YS[2][0], mx(226), 186), box(mx(254), 163, mx(238), 179))
    kucuk_cami(1, 7, (240, my(170)), box(226, my(186), XS[1][1], YS[7][1]), box(238, my(179), 254, my(163)))
    kucuk_cami(4, 7, (mx(240), my(170)), box(XS[4][0], my(186), mx(226), YS[7][1]),
               box(mx(254), my(179), mx(238), my(163)))
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
    (0, 2): ("T12", "K1", {}),                    # v2: T2 → T12
    (1, 2): ("T1", "K2", {}),
    (3, 2): ("T12", "K2", {}),                    # v2: ilkokul güneyi yeniden konut (S2 açıldı)
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
    (0, 5): ("T3", "K3", {"kat": 3, "dukkan": "S"}),   # v2: Z+3 → Z+2 (KB-3 dengesi)
    (1, 5): ("T3", "K3", {"kat": 3, "dukkan": "S"}),   # v2: Z+3 → Z+2 (KB-3 dengesi)
    (4, 5): ("T4Y", "K3", {"dukkan": "S", "kose": "W"}),
    # sıra 6
    (1, 6): ("T12", "K2", {}),
    (2, 6): ("T3", "K3", {"kat": 4, "uc": "E"}),
    (3, 6): ("T3", "K3", {"kat": 4, "uc": "W"}),
    (4, 6): ("T12", "K2", {}),
    # sıra 7
    (0, 7): ("T2", "K1", {}),
    (1, 7): ("T1", "K2", {}),
    (2, 7): ("T3", "K3", {"kat": 4, "uc": "E"}),   # v2: Z+2 → Z+3 (S1 kuzey kolu; KB-3 dengesinin karşılığı)
    (3, 7): ("T3", "K3", {"kat": 4, "uc": "W"}),   # v2: Z+2 → Z+3
    (4, 7): ("T1", "K2", {}),
    (5, 7): ("T12", "K2", {}),                    # v2: T2 → T12
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
PROGRAM.pop(ILKOKUL_B_ADA, None)                  # v2: kuzey ilkokulunun adası

# Komşuluk yeşili adalarının kalan şeritleri ve diğer kısmi adalar
_L, _T = MOBILITE_LOT, TEKNIK_SERIT
KISMI = [
    (box(XS[1][0] + 80, YS[1][0], XS[1][1], YS[1][1]), "T3S", "K2", {"kat": 3}),       # KB-1
    (box(XS[0][0], YS[3][0], XS[0][1] - 80, YS[3][1]), "T3S", "K1", {"kat": 3}),       # KB-2
    (box(XS[0][0], YS[6][0], XS[0][1] - 80, YS[6][1]), "T3S", "K1", {"kat": 3}),       # KB-3
    (box(XS[1][0] + 80, YS[8][0], XS[1][1], YS[8][1]), "T3S", "K2", {"kat": 3}),       # KB-4
    (box(XS[4][0], YS[8][0], XS[4][1] - 80, YS[8][1]), "T3S", "K2", {"kat": 3}),       # KB-5
    (box(XS[5][0] + 80, YS[6][0], XS[5][1], YS[6][1]), "T3S", "K2", {"kat": 3}),       # KB-6
    (box(XS[5][0] + 80, YS[3][0], XS[5][1], YS[3][1]), "T3S", "K2", {"kat": 3}),       # KB-7
    (box(XS[4][0], YS[1][0], XS[4][1] - 80, YS[1][1]), "T3S", "K2", {"kat": 3}),       # KB-8
    # v2: ortaokul yanındaki T3S şeridi ve ilkokul güneyindeki T2S şeridi kaldırıldı
    # v2: GB bostanının kuzey kenarında tek sıra T1 (arka bahçeler bostana açılır; bostan 0,8 ha hedefine iner)
    (box(XS[0][0], YS[0][1] - BOSTAN_T1_DER, XS[0][1], YS[0][1]), "T1K", "K1", {}),
    # mobilite noktalarının yanında kalan kısımlar
    (box(XS[3][0] + _L, YS[0][0], XS[3][1], YS[0][1]), "T4Y", "K4", {"dukkan": "S", "kose": "E"}),
    (box(XS[5][0], YS[5][0], XS[5][1] - _L, YS[5][1]), "T3", "K3", {"kat": 4, "dukkan": "S"}),
    (box(XS[2][0], YS[9][0], XS[2][1] - _L, YS[9][1]), "T1", "K1", {}),
    (box(XS[0][0] + _L, YS[4][0], XS[0][1], YS[4][1]), "T3", "K3", {"kat": 4, "dukkan": "N"}),
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
             ada=ada, ticari=0.0, kat_alani=0.0, zemin_donati=None, kose=False)
    d.update(kw)
    return d


def _siralar(x0, x1, y0, y1, tip_g, tip_k, bolge, ada):
    """İki sıra (güney: tip_g, kuzey: tip_k) sıra ev; ortada ortak bahçe şeridi."""
    out = []
    der = (y1 - y0 - ORTA_BANT) / 2
    on = on_esik(bolge)
    for taraf, tip in (("S", tip_g), ("N", tip_k)):
        if tip is None:
            continue
        hedef = (T1_GEN_K1 if bolge == "K1" else T1_GEN) if tip == "T1" else T2_GEN
        n = max(1, int((x1 - x0) // hedef))
        w = (x1 - x0) / n
        for k in range(n):
            xa, xb = x0 + k * w, x0 + (k + 1) * w
            ev_der = T1_EV_DER if tip == "T1" else T2_EV_DER
            if taraf == "S":
                p = box(xa, y0, xb, y0 + der)
                ev = box(xa, y0 + on, xb, y0 + on + ev_der)
                gen = box(xa, y0 + on + ev_der, xb, y0 + on + ev_der + T1_GENISLEME) if tip == "T1" else None
                kapi = ((xa + xb) / 2, y0)
            else:
                p = box(xa, y1 - der, xb, y1)
                ev = box(xa, y1 - on - ev_der, xb, y1 - on)
                gen = box(xa, y1 - on - ev_der - T1_GENISLEME, xb, y1 - on - ev_der) if tip == "T1" else None
                kapi = ((xa + xb) / 2, y1)
            if tip == "T1":
                kat_alani = ev.area * 3 + gen.area
                out.append(_parsel(p, "T1", bolge, 1, 3, [ev], kapi, ada, genisleme=gen, kat_alani=kat_alani,
                                   cekirdek_kat=2, sira=taraf, on=on))
            else:
                out.append(_parsel(p, "T2", bolge, 2, 3, [ev], kapi, ada, kat_alani=ev.area * 3, sira=taraf, on=on))
    orta = box(x0, y0 + der, x1, y1 - der)
    return out, [orta], []


def _gecitli(x0, x1, y0, y1, tip_g, tip_k, bolge, ada):
    """v2.1: adanın ortasından K–G yönünde 5 m'lik kamusal S3 geçidi; iki yarıda ayrı sıralar."""
    xm = (x0 + x1) / 2
    g0, g1 = xm - GECIT_G / 2, xm + GECIT_G / 2
    p1, o1, _ = _siralar(x0, g0, y0, y1, tip_g, tip_k, bolge, ada)
    p2, o2, _ = _siralar(g1, x1, y0, y1, tip_g, tip_k, bolge, ada)
    gp = box(g0, y0, g1, y1)
    ge = LineString([(xm, y0 - S2_G / 2), (xm, y1 + S2_G / 2)])
    return p1 + p2, o1 + o2, [(gp, ge)]


def _tek_sira(x0, x1, y0, y1, tip, taraf, bolge, ada):
    """v2: tek sıra sıra ev; parsel derinliği kutunun tamamı (ortak şerit yok)."""
    D = y1 - y0
    if taraf == "N":
        out, _, _ = _siralar(x0, x1, y1 - 2 * D - ORTA_BANT, y1, None, tip, bolge, ada)
    else:
        out, _, _ = _siralar(x0, x1, y0, y0 + 2 * D + ORTA_BANT, tip, None, bolge, ada)
    return out, [], []


def _t2_tek(x0, x1, y0, y1, bolge, ada):
    out = []
    on = on_esik(bolge)
    n = max(1, int((x1 - x0) // T2_GEN))
    w = (x1 - x0) / n
    for k in range(n):
        xa, xb = x0 + k * w, x0 + (k + 1) * w
        p = box(xa, y0, xb, y1)
        ev = box(xa, y0 + on, xb, y0 + on + T2_EV_DER)
        out.append(_parsel(p, "T2", bolge, 2, 3, [ev], ((xa + xb) / 2, y0), ada, kat_alani=ev.area * 3, sira="S", on=on))
    return out, [], []


def _avlu_grubu(xa, xb, ya, yb, taraf, kat, bolge, ada, dukkan=False):
    """Tek avlu grubu: sokak kanadı (kat) + iki yan kanat (Z+1) + ortak avlu."""
    w = xb - xa
    arka, duvar = None, []
    if taraf == "S":
        sk = box(xa, ya + T3_ON, xb, ya + T3_ON + T3_SOKAK_KANADI)
        yk0 = ya + T3_ON + T3_SOKAK_KANADI
        yk_l = (yb - T3_ARKA_DER - yk0) if KALIBRE else T3_YAN_KANAT_L
        yanlar = [box(xa, yk0, xa + T3_YAN_KANAT_G, yk0 + yk_l),
                  box(xb - T3_YAN_KANAT_G, yk0, xb, yk0 + yk_l)]
        if KALIBRE:   # v2.1: dördüncü kenar = tek katlı arka kanat (kuzeyde; kendi avlusunu gölgelemez)
            arka = box(xa, yb - T3_ARKA_DER, xb, yb)
        kapi = ((xa + xb) / 2, ya)
    else:
        sk = box(xa, yb - T3_ON - T3_SOKAK_KANADI, xb, yb - T3_ON)
        yk1 = yb - T3_ON - T3_SOKAK_KANADI
        yanlar = [box(xa, yk1 - T3_YAN_KANAT_L, xa + T3_YAN_KANAT_G, yk1),
                  box(xb - T3_YAN_KANAT_G, yk1 - T3_YAN_KANAT_L, xb, yk1)]
        if KALIBRE:   # v2.1: yan kanattan karşı grubun arka kanadına 2,5 m'lik bahçe duvarı (öneri 2,5–3 m)
            y_son = yk1 - T3_YAN_KANAT_L
            duvar = [box(xa, ya, xa + 0.3, y_son), box(xb - 0.3, ya, xb, y_son)]
        kapi = ((xa + xb) / 2, yb)
    kat_basi = max(2, round(w * T3_SOKAK_KANADI / KONUT_BRUT_T3))
    zemin = 0 if dukkan else kat_basi - 1                 # kapı altı geçit + bisiklet/çöp odası
    yan_konut = 4 if w >= 28 else 2                       # yan kanatlarda dubleks
    arka_konut = T3_ARKA_KONUT if arka is not None else 0
    konut = zemin + kat_basi * (kat - 1) + yan_konut + arka_konut
    kat_alani = sk.area * kat - 3.5 * T3_SOKAK_KANADI + sum(y.area for y in yanlar) * 2 + (arka.area if arka else 0.0)
    p = box(xa, ya, xb, yb)
    binalar = [sk] + yanlar + ([arka] if arka is not None else [])
    avlu = p.difference(unary_union(binalar)).difference(box(xa, ya, xb, ya + T3_ON) if taraf == "S"
                                                         else box(xa, yb - T3_ON, xb, yb))
    ticari = (sk.area - 3.5 * T3_SOKAK_KANADI) if dukkan else 0.0
    return _parsel(p, "T3", bolge, konut, kat, binalar, kapi, ada, kat_alani=kat_alani,
                   bina_katlari=[kat, 2, 2] + ([1] if arka is not None else []), avlu=avlu, ticari=ticari,
                   dukkan=dukkan, yan_konut=yan_konut, zemin_konut=zemin, kat_basi=kat_basi, sira=taraf,
                   arka_konut=arka_konut, duvar=duvar)


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
                           ticari=b.area, dukkan=True, avlu=p.difference(b), sira=dukkan))
    _yuvarla(out)
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
    sira_f = _gecitli if (KALIBRE and x1 - x0 > 100) else _siralar
    if prog == "T1":
        return sira_f(x0, x1, y0, y1, "T1", "T1", bolge, ada)
    if prog == "T2":
        return sira_f(x0, x1, y0, y1, "T2", "T2", bolge, ada)
    if prog == "T12":
        return sira_f(x0, x1, y0, y1, "T1", "T2", bolge, ada)
    if prog == "T2S":
        return _t2_tek(x0, x1, y0, y1, bolge, ada)
    if prog == "T1K":                                  # v2: tek sıra T1, kapı kuzeyde
        return _tek_sira(x0, x1, y0, y1, "T1", "N", bolge, ada)
    if prog == "T3":
        return _t3(x0, x1, y0, y1, sec.get("kat", 3), bolge, ada, gecitli=True, dukkan=sec.get("dukkan", ""),
                   uc=sec.get("uc", ""))
    if prog == "T3S":
        return _t3(x0, x1, y0, y1, sec.get("kat", 3), bolge, ada, gecitli=False, dukkan=sec.get("dukkan", ""))
    if prog == "T4Y":
        return _t4_cubuk(x0, x1, y0, y1, sec.get("dukkan", "S"), sec.get("kose", ""), bolge, ada)
    raise ValueError(prog)


# =============================================================================
# 5. Zemin kat donatıları (mescit, kreş, bakkal-fırın, çeşme) ve duraklar
# =============================================================================
ZEMIN_KURAL = {
    #  tür      yarıçap  taban hedefler                    en çok  konuttan düşülen  m²
    "mescit": dict(r=150, taban=("kucuk_cami", "semt_camii"), tavan=16, dus=1, alan=120),
    "kres": dict(r=400, taban=("anaokulu",), tavan=6, dus=3, alan=400),
    "bakkal": dict(r=300, taban=("dukkan",), tavan=12, dus=1, alan=100),
    "cesme": dict(r=250, taban=(), tavan=20, dus=0, alan=0),
}

DURAKLAR = {
    "S1": [(CX, 150), (CX, 412), (CX, 600)],
    "toplayici": [(YAYA, CY), (GEN - YAYA, CY), (CX, YAYA), (CX, YUK - YAYA), (YAYA, 120), (GEN - YAYA, 630),
                  (200, YUK - YAYA), (600, YAYA)],
}


# =============================================================================
# 6. Planı kur (geometri)
# =============================================================================
def _kirp_t12(p, engel):
    """v2: diyagonalin kestiği T1/T2 parseli — binayı kırp ("köşe evi") ya da düşür."""
    b0 = p["binalar"][0]
    bk = b0.difference(engel)
    if bk.geom_type == "MultiPolygon":
        bk = max(bk.geoms, key=lambda g: g.area)
    boran = bk.area / b0.area if not bk.is_empty else 0.0
    pk = p["poly"].difference(engel)
    if pk.geom_type == "MultiPolygon":
        pk = max(pk.geoms, key=lambda g: g.area)
    poran = pk.area / p["poly"].area
    if bk.is_empty or boran < KOSE_BINA_ESIK or poran < KOSE_PARSEL_ESIK:
        return None
    # en dar boyut ≥ 4,5 m (yaşanabilir oda)
    mrr = bk.minimum_rotated_rectangle
    kenar = sorted(LineString(mrr.exterior.coords[k:k + 2]).length for k in range(2))
    if kenar[0] < 4.5:
        return None
    gen = p.get("genisleme")
    if gen is not None:
        gk = gen.difference(engel)
        if gk.is_empty or gk.area < 0.6 * gen.area or not pk.buffer(0.01).contains(gk):
            p["genisleme"] = None
            gen_alan = 0.0
        else:
            p["genisleme"] = gk if gk.geom_type == "Polygon" else max(gk.geoms, key=lambda g: g.area)
            gen_alan = p["genisleme"].area
    else:
        gen_alan = 0.0
    if boran < 0.999:
        p["kose"] = True
    p["binalar"] = [bk]
    p["poly"] = pk
    if p["tip"] == "T2" and boran < T2_KOSE_ESIK:
        p["tip"], p["konut"] = "T1", 1                       # küçük köşe parselinde tek hane
        p["kose_donusum"] = True
    p["kat_alani"] = bk.area * 3 + (gen_alan if p["tip"] == "T1" else 0.0)
    return p


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
        if p["tip"] in ("T1", "T2"):
            q = _kirp_t12(p, engel)
            (kalan if q is not None else dusen).append(p)
            continue
        binalar_ok = all(b.intersection(engel).area < 0.5 for b in p["binalar"])
        kirpik = p["poly"].difference(engel)
        if kirpik.geom_type == "MultiPolygon":
            kirpik = max(kirpik.geoms, key=lambda g: g.area)
        oran = kirpik.area / p["poly"].area
        if binalar_ok and oran >= 0.80:
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
    """Mescit, kreş, bakkal ve çeşmeleri açgözlü kapsama ile yerleştirir (v1 ile aynı yöntem)."""
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
        if d["tur"] == "otopark":
            q = d["binalar"][0].centroid
            ev_aday.append(dict(ad=("donati", n), dugum=erisim[("donati", n, 0)], xy=(q.x, q.y), ev=None,
                                birim=birim_bul((q.x, q.y))))
        elif (d["tur"] == "park" and d.get("kb") is None and not d.get("merkez")) or d["tur"] == "bostan":   # v2: bostanda da küçük mescit yapısı olabilir
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
                    ev["zemin_konut"] = max(0, ev.get("zemin_konut", 0) - kural["dus"])
                ev["ticari"] += kural["alan"]
                ev.setdefault("zemin_donatilari", []).append(tur)
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
    # yeşil diyagonaller (v2: GD diyagonali S2 ekseninde başlar)
    yaya_cizgi = []
    for k, b in zip(KOSELER, DIYAG_BASLANGIC):
        if k == b:
            bas = (YAYA if k[0] < CX else GEN - YAYA, YAYA if k[1] < CY else YUK - YAYA)
        else:
            bas = b
        yaya_cizgi.append(LineString([bas, (CX, CY)]))
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
            if d.get("okul"):
                hedefler["ilkokul_" + d["okul"]].append(kim)
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

    P["zemin"] = _zemin_sec(G, erisim, hedefler, P)
    # v2: asansörsüz avlu gruplarında (Z+2) BB'lerin en az %15'i zeminde erişilebilir olmalı (paket P4, Genelge
    # ölçüt 17). Zemini dükkân ya da mescit/kreş olan gruplarda yan kanat dubleksi yerine "zemin + üst kat daire"
    # varyantı kullanılır: zemin daire eşiksizdir; hane sayısı değişmez.
    for p in P["parseller"]:
        if p["tip"] == "T3" and p["kat"] <= 3 and p["konut"] > 0:
            gerek = math.ceil(0.15 * p["konut"] - 1e-9) - p.get("zemin_konut", 0) - p.get("arka_konut", 0)
            p["yan_erisilebilir"] = max(0, min(2, gerek, p.get("yan_konut", 4) // 2))
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
@lru_cache(maxsize=1)
def komsuluk_birimleri():
    """Her çeyrek kendi diyagonaliyle iki üçgene bölünür → 8 birim (KB-1 … KB-8)."""
    q = {
        "GB": box(TY, TY, CX - 9, CY - 9), "GD": box(CX + 9, TY, GEN - TY, CY - 9),
        "KB": box(TY, CY + 9, CX - 9, YUK - TY), "KD": box(CX + 9, CY + 9, GEN - TY, YUK - TY),
    }
    tanim = [
        (1, "GB", [(TY, TY), (CX, TY), (CX, CY)]),
        (2, "GB", [(TY, TY), (CX, CY), (TY, CY)]),
        (3, "KB", [(TY, YUK - TY), (TY, CY), (CX, CY)]),
        (4, "KB", [(TY, YUK - TY), (CX, CY), (CX, YUK - TY)]),
        (5, "KD", [(GEN - TY, YUK - TY), (CX, YUK - TY), (CX, CY)]),
        (6, "KD", [(GEN - TY, YUK - TY), (CX, CY), (GEN - TY, CY)]),
        (7, "GD", [(GEN - TY, TY), (GEN - TY, CY), (CX, CY)]),
        (8, "GD", [(GEN - TY, TY), (CX, CY), (CX, TY)]),
    ]
    return tuple((no, Polygon(k).intersection(q[c])) for no, c, k in tanim)


def birim_bul(xy):
    p = Point(xy)
    en, ad = 1e9, None
    for no, g in komsuluk_birimleri():
        d = g.distance(p)
        if d < en:
            en, ad = d, no
    return ad


# =============================================================================
# 9. v2: ağaçlar (çizim ve taç örtüsü aynı noktalardan)
# =============================================================================
# 20 yıl sonraki taç yarıçapı (m) — varsayım [V]; tür ve yetiştirme koşuluna göre değişir.
TAC_R20 = {
    "cadde": 4.0,       # S1 ve toplayıcı: çınar, ıhlamur (taç çapı ≈ 8 m)
    "s2": 3.5,          # S2 yaşam sokağı (≈ 7 m)
    "s2_saşırtma": 3.0, # S2 paylaşımlı yüzeydeki şaşırtma (yavaşlatma) ağaçları
    "diyagonal": 3.0,
    "s3": 2.5,
    "park": 4.5,       # park ağacı, kök sınırı yok (≈ 9 m)
    "cep": 3.5,
    "bahce": 2.5,       # meyve ağacı
    "bahce_golge": 3.5, # arka bahçenin gölge ağacı (dut, ceviz, ıhlamur)
    "avlu": 3.5,
    "ortak": 3.5,
    "okul": 3.5,
    "bostan": 2.5,
}
AGAC_ARALIK = {"cadde": 10.0, "toplayici": 10.0, "s2": 10.0, "s2_saşırtma": 24.0, "diyagonal": 8.0, "s3": 10.0,
               "park": 10.0, "park_kenar": 10.0, "cep": 10.0, "ortak": 8.0, "bostan_kenar": 9.0,
               "okul_kenar": 9.0}


def _izgara_agac(poly, aralik, r, tohum=1, tur="park"):
    x0, y0, x1, y1 = poly.bounds
    out = []
    ic = poly.buffer(-max(2.5, r * 0.6))
    if ic.is_empty:
        return out
    k = tohum
    y = y0 + aralik / 2
    while y < y1:
        x = x0 + aralik / 2 + (aralik / 2 if int((y - y0) / aralik) % 2 else 0)
        while x < x1:
            k = (k * 1103515245 + 12345) % 2 ** 31
            jx = ((k % 1000) / 1000 - 0.5) * aralik * 0.4
            jy = (((k // 1000) % 1000) / 1000 - 0.5) * aralik * 0.4
            p = Point(x + jx, y + jy)
            if ic.contains(p):
                out.append((p.x, p.y, r, tur))
            x += aralik
        y += aralik
    return out


def _uzak_noktalar(poly, n, aralik=2.0, uzak_geom=None, min_ara=4.5):
    """poly içinde, uzak_geom'dan en uzak ve birbirinden en az min_ara uzak n nokta."""
    if poly.is_empty:
        return []
    x0, y0, x1, y1 = poly.bounds
    adaylar = []
    y = y0 + aralik / 2
    while y < y1:
        x = x0 + aralik / 2
        while x < x1:
            q = Point(x, y)
            if poly.contains(q):
                adaylar.append(q)
            x += aralik
        y += aralik
    if not adaylar:
        return []
    if uzak_geom is not None:
        adaylar.sort(key=lambda q: -q.distance(uzak_geom))
    secim = []
    for q in adaylar:
        if all(q.distance(s) >= min_ara for s in secim):
            secim.append(q)
        if len(secim) == n:
            break
    return [(q.x, q.y) for q in secim]


@lru_cache(maxsize=1)
def agac_noktalari():
    """Bütün ağaçlar: [(x, y, r20, tür)]. Fıtrat Kodu v2 dikim kurallarının çizimdeki karşılığı."""
    P = model()
    A = ag_kur()
    out = []
    kavsak = unary_union(list(KAVSAK.values()) + [MEYDAN, CARSI_YAYA.buffer(-1)]).buffer(3)
    engel = unary_union([kavsak, DONATI_POLY.buffer(1)])
    # S1 cadde: iki yanda ±4,25 m, 10 m arayla
    a = AGAC_ARALIK["cadde"]
    for s in (-4.25, 4.25):
        y = 18.0
        while y < 740:
            out.append((CX + s, y, TAC_R20["cadde"], "cadde"))
            y += a
        x = 18.0
        while x < 790:
            out.append((x, CY + s, TAC_R20["cadde"], "cadde"))
            x += a
    # toplayıcı: iç ağaç şeridi (sınırdan 5,75 m) ve orta refüj (sınır çizgisi)
    for d in (5.75, 0.0):
        t = 10.0
        while t < 800:
            out.append((t, d, TAC_R20["cadde"], "cadde"))
            out.append((t, YUK - d, TAC_R20["cadde"], "cadde"))
            t += AGAC_ARALIK["toplayici"]
        t = 10.0
        while t < 750:
            out.append((d, t, TAC_R20["cadde"], "cadde"))
            out.append((GEN - d, t, TAC_R20["cadde"], "cadde"))
            t += AGAC_ARALIK["toplayici"]
    # S2: ağaç + park cebi şeridi (eksenden −2 m), 10 m arayla (v1: 12 m); karşı yanda paylaşımlı
    # yüzeyde 24 m arayla şaşırtma ağacı (+2 m)
    for k, (pol, ln) in BAGLANTI.items():
        if k in KAPALI:
            continue
        L = ln.length
        s = 5.0
        while s < L - 3:
            q = ln.interpolate(s)
            out.append((q.x, q.y - 2.0, TAC_R20["s2"], "s2") if k[0] == "h" else (q.x - 2.0, q.y, TAC_R20["s2"], "s2"))
            s += AGAC_ARALIK["s2"]
        s = 12.0
        while s < L - 10:
            q = ln.interpolate(s)
            out.append((q.x, q.y + 1.5, TAC_R20["s2_saşırtma"], "s2_saşırtma") if k[0] == "h"
                       else (q.x + 1.5, q.y, TAC_R20["s2_saşırtma"], "s2_saşırtma"))
            s += AGAC_ARALIK["s2_saşırtma"]
    # diyagonaller: iki sıra, 8 m
    for ln in DIYAG_EKSEN:
        L = ln.length
        dx, dy = (ln.coords[1][0] - ln.coords[0][0]) / L, (ln.coords[1][1] - ln.coords[0][1]) / L
        nx_, ny_ = -dy, dx
        s = 6.0
        while s < L - 30:
            q = ln.interpolate(s)
            for side in (-2.6, 2.6):
                out.append((q.x + nx_ * side, q.y + ny_ * side, TAC_R20["diyagonal"], "diyagonal"))
            s += AGAC_ARALIK["diyagonal"]
    # S3 geçitleri: yağmur bahçesinde küçük ağaç
    for gp, ge in P["gecitler"]:
        x0, y0, x1, y1 = gp.bounds
        y = y0 + 5
        while y < y1 - 3:
            out.append((x0 + 0.9, y, TAC_R20["s3"], "s3"))
            y += AGAC_ARALIK["s3"]
    sokak_disi = unary_union([MEYDAN, CARSI_YAYA])
    out = [t for t in out if not (kavsak.contains(Point(t[0], t[1])) or sokak_disi.contains(Point(t[0], t[1])))
           or t[3] not in ("cadde", "s2", "s2_saşırtma")]
    # parklar, cep parkları, bostan kenarı, okul bahçeleri, cami avlusu
    yol = unary_union([ln.buffer(2.5) for ln in A["yaya_cizgi"]] + [DIYAG_BANT])
    tohum = 3
    for d in P["donatilar"]:
        poly = d["poly"]
        if d["tur"] == "park":
            alan = poly.difference(yol)
            if d.get("saha") is not None:
                alan = alan.difference(d["saha"].buffer(2))
            out += _izgara_agac(alan, AGAC_ARALIK["park"], TAC_R20["park"], tohum, "park")
            # kenarda gölge sırası (oturma yerleri), 10 m arayla; iç ızgarayla çakışan atlanır
            kenar = poly.buffer(-3.0)
            for h in ([kenar] if kenar.geom_type == "Polygon" else list(kenar.geoms)):
                s_ = 0.0
                while s_ < h.exterior.length:
                    q = h.exterior.interpolate(s_)
                    if alan.contains(q) and all(Point(t[0], t[1]).distance(q) > 6.0 for t in out[-60:]):
                        out.append((q.x, q.y, TAC_R20["park"], "park"))
                    s_ += AGAC_ARALIK["park_kenar"]
        elif d["tur"] == "cep":
            out += _izgara_agac(poly.difference(yol), AGAC_ARALIK["cep"], TAC_R20["cep"], tohum, "cep")
        elif d["tur"] == "bostan":
            sinir = poly.buffer(-2.0).exterior
            s = 0.0
            while s < sinir.length:
                q = sinir.interpolate(s)
                out.append((q.x, q.y, TAC_R20["bostan"], "bostan"))
                s += AGAC_ARALIK["bostan_kenar"]
        elif d["tur"] in ("ilkokul", "ortaokul", "anaokulu", "semt_camii", "kucuk_cami", "asm", "konak"):
            bos = poly.difference(unary_union([b.buffer(3) for b in d["binalar"]]))
            if d.get("saha") is not None:
                bos = bos.difference(d["saha"].buffer(2))
            sinir = poly.buffer(-3.0)
            if sinir.is_empty:
                continue
            halkalar = [sinir] if sinir.geom_type == "Polygon" else list(sinir.geoms)
            for h in halkalar:
                s = 0.0
                while s < h.exterior.length:
                    q = h.exterior.interpolate(s)
                    if bos.contains(q):
                        out.append((q.x, q.y, TAC_R20["okul"], "okul"))
                    s += AGAC_ARALIK["okul_kenar"]
        tohum += 7
    for n, g in enumerate(P["cep"]):
        if g.area > 150:
            out += _izgara_agac(g, AGAC_ARALIK["cep"], TAC_R20["cep"], n % 97 + 1, "cep")
    # ada içi ortak şeritler (T1/T2): ortada ağaç sırası, 9 m
    for o in P["ortaklar"]:
        x0, y0, x1, y1 = o.bounds
        ym = (y0 + y1) / 2
        x = x0 + 4.5
        while x < x1 - 2:
            if o.buffer(-0.5).contains(Point(x, ym)):
                out.append((x, ym, TAC_R20["ortak"], "ortak"))
            x += AGAC_ARALIK["ortak"]
    # parseller: T1/T2 arka bahçede 2 ağaç (biri meyve), T3 avlusunda 4, T4 arka avluda 100 m² başına 1
    for p in P["parseller"]:
        if p["tip"] in ("T1", "T2"):
            yapili = unary_union(p["binalar"] + ([p["genisleme"]] if p.get("genisleme") is not None else []))
            bahce = p["poly"].difference(yapili.buffer(2.0)).buffer(-1.6)
            for m, (x, y) in enumerate(_uzak_noktalar(bahce, 2, 1.0, yapili, 4.0)):
                # biri gölge ağacı (dut, ceviz, ıhlamur; evden en uzakta), biri meyve ağacı
                out.append((x, y, TAC_R20["bahce_golge"] if m == 0 else TAC_R20["bahce"], "bahce"))
        elif p["tip"] == "T3" and p.get("avlu") is not None:
            avlu = p["avlu"].buffer(-2.5)
            for x, y in _uzak_noktalar(avlu, 4, 2.0, None, 7.5):
                out.append((x, y, TAC_R20["avlu"], "avlu"))
        elif p["tip"] == "T4" and p.get("avlu") is not None:
            n = max(1, int(p["avlu"].area // 100))
            for x, y in _uzak_noktalar(p["avlu"].buffer(-2.5), n, 2.0, p["binalar"][0], 6.0):
                out.append((x, y, TAC_R20["avlu"], "avlu"))
    return out


@lru_cache(maxsize=1)
def tac_ortusu():
    """20 yıl sonraki tahmini taç örtüsü: ağaç taçlarının birleşimi / brüt alan (çakışmalar bir kez sayılır)."""
    agaclar = agac_noktalari()
    taclar = unary_union([Point(x, y).buffer(r, 12) for x, y, r, _ in agaclar]).intersection(ALAN)
    tur_say = defaultdict(int)
    for *_, t in agaclar:
        tur_say[t] += 1
    return dict(alan=taclar.area, oran=taclar.area / ALAN.area, sayi=len(agaclar), tur=dict(tur_say), geom=taclar)


# =============================================================================
# 10. v2: tahsis karması (kooperatif / yapı grubu · sosyal kiralık · piyasa)
# =============================================================================
TAHSIS_HEDEF = {"kooperatif": 0.30, "sosyal": 0.20, "piyasa": 0.50}   # tasarim_parametreleri §9.4
TAHSIS_AD = {"kooperatif": "Kooperatif / yapı grubu", "sosyal": "Kiralık sosyal konut", "piyasa": "Piyasa"}
YAPIMCI_TAVAN = 40                                                    # ada başına bir yapımcıya en çok konut


@lru_cache(maxsize=1)
def tahsis():
    """Tahsis birimlerini (bahçe grubu, avlu grubu, T4 parseli) komşuluk birimi içinde, hedef paylardan
    sapmayı en aza indiren açgözlü sırayla dağıtır. Sosyal kiralık T2'ye verilmez (iki kuşaklı aile evi).
    Döndürür: {parsel indeksi: tahsis türü}, birim listesi."""
    P = model()
    birimler = defaultdict(list)          # (kb, anahtar) → parsel indeksleri
    for n, p in enumerate(P["parseller"]):
        if p["konut"] <= 0:
            continue
        kb = birim_bul(p["kapi"])
        if p["tip"] in ("T1", "T2"):
            c = p["poly"].centroid
            x0 = XS[p["ada"][0]][0]
            anahtar = ("bahce", p["ada"], p["tip"], int((c.x - x0) // 30))
        elif p["tip"] == "T3":
            anahtar = ("avlu", n)
        else:
            anahtar = ("t4", n)
        birimler[(kb, anahtar)].append(n)
    sonuc = {}
    liste = []
    for kb in range(1, 9):
        anahtarlar = sorted([a for (k, a) in birimler if k == kb], key=lambda a: (str(a[0]), str(a[1:])))
        # karıştır: türler arasında dönüşümlü sıra (aynı adada tek tür kümelenmesin)
        toplam = defaultdict(float)
        tum = 0.0
        for a in anahtarlar:
            idx = birimler[(kb, a)]
            k = sum(P["parseller"][i]["konut"] for i in idx)
            tip = P["parseller"][idx[0]]["tip"]
            izinli = [t for t in TAHSIS_HEDEF if not (t == "sosyal" and tip == "T2")]
            secim = max(izinli, key=lambda t: TAHSIS_HEDEF[t] * (tum + k) - toplam[t])
            toplam[secim] += k
            tum += k
            for i in idx:
                sonuc[i] = secim
            liste.append(dict(kb=kb, anahtar=a, tur=secim, konut=k, tip=tip))
    return sonuc, liste


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    P = model()
    tips = defaultdict(int)
    for p in P["parseller"]:
        tips[p["tip"]] += p["konut"]
    print("Konut:", dict(tips), "toplam", sum(tips.values()))
    print("Düşen parsel:", len(P["dusen"]), "köşe evi:", sum(1 for p in P["parseller"] if p.get("kose")),
          "cep:", len(P["cep"]), round(sum(g.area for g in P["cep"])))
    for d in P["donatilar"]:
        print(f"{d['ad'][:44]:44s} {d['poly'].area:9.0f}")
