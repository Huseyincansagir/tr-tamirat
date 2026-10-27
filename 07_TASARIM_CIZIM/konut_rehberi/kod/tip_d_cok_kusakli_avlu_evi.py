"""
Tip (d) — T2 avlulu çok kuşaklı ev: ayrıntılı plan (karasal iklim; referans Ankara, 39,9° K)
==========================================================================================
Model mahalle v2.1'in T2 tipinin (07_TASARIM_CIZIM/model_mahalle_v2/kod/plan_modeli.py,
konut_tipolojileri.py) ayrıntılandırılması. Parsel ve bina ölçüleri modelden alınır
(K2: 9,56 × 27,4 m; ön eşik 1,0 m; bina derinliği 11,0 m; Z+2; 8 m ortak bahçe şeridi).
Model dosyaları yalnız okunur (sabitlerin aynı olduğu denetlenir, hiçbir dosya yazılmaz).

İki bağımsız bölüm, bir avlu:
  · Zemin: büyükler dairesi, eşiksiz 2+1. Bütün yaşama odaları avluya (güneye) bakar;
    kuzeyde yalnız ikinci yatak odası (sokakta göz), içte kiler ve engelsiz banyo.
  · 1.–2. kat: genç ailenin 4+1 dubleksi (karşılaştırma birimi, 5 kişi). 1. kat: sofa,
    misafir odası (selamlık), aile oturması, mutfak, balkon ve avluya inen hayat merdiveni.
    2. kat aile katıdır: üç yatak odası, sükûnet odası, banyo, yüklük.
  · Ortak taşlık (giriş eşiği): sokak kapısı tek; büyüklerin kapısı, dubleksin merdiven
    kapısı ve asansör yeri (PAİY md. 34/1: 3 kat + 2 BB → asansör yeri) buraya açılır.
Karasal iklim: kompakt kütle, kuzeyde servis tamponu (taşlık, merdiven, kiler, ıslak hacim),
güneyde geniş cam; yazın 1,8 m balkon ve 0,9 m güneş kırıcı gölgeler, kışın güneş içeri girer.
Koordinat: x doğuya (parsel batı sınırı 0), y kuzeye (parselin bahçe ucu 0, sokak 27,4).
"""

from __future__ import annotations

import math
import re
from pathlib import Path

from shapely.geometry import box

import cizim as C
from cizim import Blok, Kayit, Plan
from degerlendirme import birim_ozeti, csv_satirlari, sag_sutun
from veri import GUN, OLCUT, PAIY, SEHIR, gunes_saati, kible, ogle_yuksekligi, sayi, yagmur_potansiyeli, yapim_maliyeti

AD = "tip_d_cok_kusakli_avlu_evi"
SEHIR_AD = "Ankara"
S = SEHIR[SEHIR_AD]
KIBLE = kible(S["enlem"], S["boylam"])

# --- model mahalle v2.1 sabitleri (plan_modeli.py; yalnız okunur) ---------------------------
MODEL = dict(TY=12.0, CY=375.0, CADDE_G=18.0, S2_G=10.0, ORTA_BANT=8.0, ON_ESIK_K2=1.0, T2_EV_DER=11.0,
             T2_GEN=9.2, T1_EV_DER=9.0, T1_GENISLEME=4.0, GECIT_G=5.0, CX=400.0)


def model_denetle():
    """plan_modeli.py ve konut_tipolojileri.py'deki sabitler bu dosyadakilerle aynı mı? (yalnız okunur)"""
    kok = Path(__file__).resolve().parents[2] / "model_mahalle_v2" / "kod"
    yol, yol2 = kok / "plan_modeli.py", kok / "konut_tipolojileri.py"
    if not yol.exists() or not yol2.exists():
        return "model dosyaları bulunamadı: sabitler denetlenmedi"
    t = yol.read_text(encoding="utf-8")
    beklenen = [r"T1_EV_DER, T2_EV_DER = 9\.0, 11\.0", r"T1_GEN, T2_GEN = 6\.0, 9\.2", r"T1_GENISLEME = 4\.0",
                r"ORTA_BANT = 8\.0", r"ON_ESIK_K2 = 1\.0 if KALIBRE", r"GECIT_G = 5\.0", r"S2_G = 10\.0",
                r"CADDE_G = 18\.0", r"TY = 12\.0", r"CX, CY = 400\.0, 375\.0"]
    eksik = [b for b in beklenen if not re.search(b, t)]
    if not re.search(r"T2_W = _SIRA_W / int\(_SIRA_W // pm\.T2_GEN\)", yol2.read_text(encoding="utf-8")):
        eksik.append("T2_W")
    return "model sabitleri aynı" if not eksik else f"farklı: {eksik}"


_ADA_W = (MODEL["CX"] - MODEL["CADDE_G"] / 2 - MODEL["TY"] - 2 * MODEL["S2_G"]) / 3       # 119,67 m
_ADA_D = (MODEL["CY"] - MODEL["CADDE_G"] / 2 - MODEL["TY"] - 4 * MODEL["S2_G"]) / 5       # 62,8 m
_SIRA = (_ADA_W - MODEL["GECIT_G"]) / 2
W = _SIRA / int(_SIRA // MODEL["T2_GEN"])            # 9,56 m (K2)
PD = (_ADA_D - MODEL["ORTA_BANT"]) / 2               # 27,4 m
ON = MODEL["ON_ESIK_K2"]
YF = PD - ON                                         # ön cephe dış yüzü 26,4
YB = YF - MODEL["T2_EV_DER"]                         # arka (avlu) cephe dış yüzü 15,4
T_DIS, T_IC = 0.35, 0.15                             # karasal iklim: dış ve BB arası duvar 35 cm [V]
KAT_H, DOS = 3.10, 0.30
a_f, a_b = YF - T_DIS / 2, YB + T_DIS / 2            # cephe eksenleri
# iç akslar
X1, X2, X3, X4 = 3.4, 4.55, 6.2, 8.15
Y1, Y2, Y3, Y4 = 19.7, 21.1, 22.6, 24.275
YL = 18.5                                            # üst katlarda merdiven varış sahanlığı
Y2_2, Y3_2 = 21.05, 23.0                             # 2. kat
BALKON = 1.8                                         # 1. kat balkonu (altı büyüklerin eyvanı) [V]
SACAK1_Z, SACAK1_D = 5.40, 0.90                      # 1. kat güney camı üstünde güneş kırıcı [V]
CATI_SACAK, EGIM = 0.80, 30.0
MERD = (X4 + T_DIS / 2, Y1 + T_DIS / 2, W - T_DIS / 2, Y4)      # basamak kutusu (her katta aynı)
HAYAT_M = (8.45, 9.6, 9.4, YB - BALKON)              # avluya inen hayat merdiveni
DEPO_M3 = 3.0                                        # gömülü yağmur suyu deposu [V]
X_KESIT = 3.0
PLATFORM = (X2 + T_DIS / 2, Y4 + T_DIS / 2, X3 - T_IC / 2, a_f - T_DIS / 2)   # 1,4 × 1,6 m kuyu
ADLAR = {"buyukler": "B", "dubleks": "D", "ortak": "O"}


# =============================================================================
# Planlar
# =============================================================================
def zemin():
    p = Plan("Zemin", [Blok("B", T_DIS, T_IC), Blok("D", T_DIS, T_IC)])
    # --- büyükler dairesi (B), eşiksiz 2+1 ---
    o = dict(blok="B", birim="buyukler")
    p.oda("Oturma", (0.0, a_b, 3.85, Y1), "yasam", etiket=(1.95, 18.65), **o)
    p.oda("Mutfak", (3.85, a_b, 6.4, Y1), "mutfak", etiket=(4.75, 17.6), **o)
    p.oda("Büyükler odası", (6.4, a_b, W, Y1), "yatak", etiket=(8.25, 16.45), **o)
    p.oda("Kiler ·\nçamaşır", (0.0, Y1, 2.0, Y3), "depo", etiket=(1.05, 21.6), etiket_mod="kisa", **o)
    p.oda("Hol", [(2.0, Y1, X4, Y2), (X3, Y2, X4, Y4), (2.0, Y2, X1, Y3)], "dolasim", etiket=(5.0, 20.4),
          etiket_mod="ad", **o)
    p.oda("Banyo\n(engelsiz)", (X1, Y2, X3, Y4), "islak", etiket=(4.85, 22.35), etiket_mod="kisa", **o)
    p.oda("Yatak odası 2", [(0.0, Y3, X1, a_f), (X1, Y4, X2, a_f)], "yatak", etiket=(1.75, 24.6), **o)
    # --- ortak taşlık ve dubleksin zemindeki parçaları (D) ---
    p.oda("Taşlık\n(ortak eşik)", (X3, Y4, W, a_f), "esik", blok="D", birim="ortak", etiket=(8.15, 25.6),
          etiket_mod="ad")
    p.oda("Asansör\nyeri", (X2, Y4, X3, a_f), "depo", blok="D", birim="dubleks", etiket=(5.42, 25.8),
          etiket_mod="ad")
    m = p.oda("Merdiven", (X4, Y1, W, Y4), "merdiven", blok="D", birim="dubleks", etiket_mod="yok")
    m.yon, m.basamak, m.kesik, m.merdiven_kutu = "G", 17, 0.55, MERD
    A = p.ac
    # kapılar
    A("kapi", 6.65, a_f, 7.6, a_f, ic="-", h=0)                  # sokak kapısı (tek, ortak)
    A("kapi", 6.45, Y4, 7.4, Y4, ic="-", h=0)                    # büyükler kapısı (eşiksiz)
    A("kapi", 8.4, Y4, 9.3, Y4, ic="+", h=0)                     # dubleks kapısı (merdiven ayağı)
    A("kapi", X3, 24.6, X3, 25.45, ic="-", h=0)                  # asansör yeri (bugün depo)
    A("kapi", X3, 22.0, X3, 22.9, ic="+", h=0)                   # banyo (dışa açılır)
    A("kapi", 2.15, Y3, 3.05, Y3, ic="+", h=0)                   # yatak 2
    A("kapi", 2.0, 21.4, 2.0, 22.2, ic="-", h=0)                 # kiler
    A("bosluk", 2.15, Y1, 3.7, Y1)                               # hol → oturma
    A("kapi", 4.2, Y1, 5.05, Y1, ic="-", h=0)                    # mutfak
    A("kapi", 6.75, Y1, 7.65, Y1, ic="-", h=0)                   # büyükler odası
    A("bosluk", 3.85, 16.3, 3.85, 17.4)                          # oturma ↔ mutfak servis açıklığı
    # avlu cephesi (güney)
    A("kapi2", 0.45, a_b, 1.95, a_b, ic="+", h=2.2)              # oturma → eyvan (eşiksiz, camlı)
    A("pencere", 2.3, a_b, 3.55, a_b, h=1.6)
    A("pencere", 4.25, a_b, 5.95, a_b, h=1.3)                    # mutfak
    A("kapi", 6.7, a_b, 7.6, a_b, ic="+", h=2.1)                 # büyükler odası → eyvan (eşiksiz)
    A("pencere", 8.0, a_b, 9.15, a_b, h=1.5)
    # sokak cephesi (kuzey)
    A("pencere", 1.0, a_f, 3.2, a_f, h=1.4)                      # yatak 2 (sokakta göz)
    A("pencere", 8.35, a_f, 9.15, a_f, h=1.0)                    # taşlık
    p.bacalar += [(5.6, 23.65), (0.55, 20.25)]
    p.kolonlar += [(0.3, YB - BALKON + 0.15, 0.25), (W / 2, YB - BALKON + 0.15, 0.25),
                   (W - 0.3, YB - BALKON + 0.15, 0.25)]
    M = p.mob
    M("sedir", 0.35, 16.0, 0.65, 3.4)
    M("masa", 2.2, 16.55, 1.2, 0.8, n=4)
    M("tezgah", 5.65, 15.95, 0.6, 3.5, ocak=(5.7, 16.35), eviye=(5.75, 17.75))
    M("yatak2", 7.0, 17.3, yon="K")
    M("dolap", 8.8, 16.9, 0.5, 2.5)
    M("dus", 3.6, 23.15, 1.0, 1.0)
    M("wc", 5.15, 24.1, yon="K")
    M("lavabo", 4.55, 21.55)
    M("dolap", 0.3, 19.95, 0.45, 2.45)
    M("camasir", 1.25, 19.95)
    M("yatak1", 0.4, 23.0, yon="B")
    M("yatak1", 0.4, 25.0, yon="B")
    M("dolap", 3.55, 24.5, 0.75, 1.45)
    M("dolap", 7.45, 22.75, 0.45, 1.4)                           # vestiyer
    M("platform", PLATFORM[0] + 0.2, PLATFORM[1] + 0.15, 0.8, 1.25)
    return p


def kat1():
    p = Plan("1. kat", [Blok("D", T_DIS, T_IC)])
    o = dict(blok="D", birim="dubleks")
    p.oda("Oturma ve yemek", [(0.0, a_b, 4.6, Y1), (0.0, Y1, X1, Y3)], "yasam", etiket=(2.0, 17.55), **o)
    p.oda("Mutfak", (4.6, a_b, W, YL), "mutfak", etiket=(6.4, 17.05), **o)
    p.oda("Sofa", [(4.6, YL, W, Y1), (X3, Y1, X4, Y4), (X3, Y4, W, a_f)], "dolasim", etiket=(7.15, 22.1),
          etiket_mod="ad", **o)
    p.oda("Kiler", (X1, Y1, 4.8, Y3), "depo", etiket=(4.1, 21.15), etiket_mod="ad", **o)
    p.oda("WC", (4.8, Y1, X3, 21.25), "islak", etiket_mod="yok", **o)
    p.oda("Vestiyer", (4.8, 21.25, X3, Y3), "depo", etiket=(5.5, 21.92), etiket_mod="ad", **o)
    p.oda("Misafir odası\n(selamlık)", [(0.0, Y3, X2, a_f), (X2, Y3, X3, Y4)], "misafir", etiket=(1.95, 23.9), **o)
    p.oda("Asansör\nyeri", (X2, Y4, X3, a_f), "depo", etiket=(5.42, 25.8), etiket_mod="ad", **o)
    m = p.oda("Merdiven", (X4, Y1, W, Y4), "merdiven", acik="BGK", etiket_mod="yok", **o)
    m.yon, m.basamak, m.kesik, m.merdiven_kutu = "G", 17, 0.55, MERD
    A = p.ac
    A("kapi", X3, 22.85, X3, 23.75, ic="-", h=0)                 # misafir
    A("kapi", 5.05, Y1, 5.85, Y1, ic="+", h=0)                   # WC
    A("kapi", X3, 21.55, X3, 22.35, ic="-", h=0)                 # vestiyer
    A("kapi", X1, 20.05, X1, 20.85, ic="+", h=0)                 # kiler (yemekten)
    A("bosluk", 4.6, 18.6, 4.6, 19.6)                            # sofa → oturma
    A("kapi", 4.6, 16.55, 4.6, 17.4, ic="+", h=0)                # oturma ↔ mutfak
    A("kapi", 6.55, YL, 7.45, YL, ic="-", h=0)                   # sofa → mutfak
    A("kapi", X3, 24.6, X3, 25.45, ic="-", h=0)                  # asansör yeri
    # avlu cephesi
    A("kapi2", 0.45, a_b, 1.95, a_b, ic="+", h=2.2)              # oturma → balkon
    A("surgulu", 2.25, a_b, 4.25, a_b, h=2.2)
    A("pencere", 5.1, a_b, 6.6, a_b, h=1.3)                      # mutfak
    A("kapi", 7.25, a_b, 8.15, a_b, ic="+", h=2.1)               # mutfak → balkon
    A("pencere", 8.45, a_b, 9.15, a_b, h=1.3)
    # sokak cephesi
    A("pencere", 0.6, a_f, 3.8, a_f, h=1.5)                      # misafir (kafesli perde)
    A("pencere", 6.55, a_f, 8.0, a_f, h=1.4)                     # sofa
    p.bacalar += [(5.85, 20.85)]
    M = p.mob
    M("sedir", 0.35, 15.95, 0.65, 3.5)
    M("kanepe", 3.75, 16.15, 0.65, 2.1)
    M("masa", 0.85, 20.6, 1.8, 0.9, n=6)
    M("tezgah", 8.75, 15.95, 0.6, 2.35, ocak=(8.8, 16.4), eviye=(8.85, 17.55))
    M("dolap", 3.55, 19.9, 0.4, 2.5)                             # kiler rafı
    M("wc", 5.5, 21.05, yon="K")
    M("lavabo", 5.85, 20.0)
    M("dolap", 4.95, 21.4, 0.9, 0.45)
    M("sedir", 0.35, 25.35, 3.6, 0.65)
    M("sedir", 0.35, 22.95, 0.65, 2.35)
    M("sedir", 6.5, 25.5, 1.4, 0.5)                              # sofada pencere sediri
    M("platform", PLATFORM[0] + 0.2, PLATFORM[1] + 0.15, 0.8, 1.25)
    return p


def kat2():
    p = Plan("2. kat", [Blok("D", T_DIS, T_IC)])
    o = dict(blok="D", birim="dubleks")
    p.oda("Ebeveyn odası", (0.0, a_b, 3.6, Y1), "yatak", etiket=(1.8, 18.55), **o)
    p.oda("Çocuk odası 1", (3.6, a_b, X3, Y1), "yatak", etiket=(4.35, 17.6), **o)
    p.oda("Sükûnet odası", (X3, a_b, W, YL), "sukunet", etiket=(8.4, 16.95), etiket_mod="kisa", **o)
    p.oda("Hol", [(2.4, Y1, X3, Y2_2), (X3, YL, W, Y1), (X3, Y1, X4, Y4), (X3, Y4, W, a_f)], "dolasim",
          etiket=(7.15, 22.1), etiket_mod="ad", **o)
    p.oda("Yüklük", (0.0, Y1, 2.4, Y3_2), "depo", etiket=(1.5, 21.55), etiket_mod="kisa", **o)
    p.oda("Banyo", (2.4, Y2_2, X3, Y3_2), "islak", etiket=(4.1, 22.0), etiket_mod="kisa", **o)
    p.oda("Çocuk odası 2", [(0.0, Y3_2, X2, a_f), (X2, Y3_2, X3, Y4)], "yatak", etiket=(3.75, 24.6), **o)
    p.oda("Asansör\nyeri", (X2, Y4, X3, a_f), "depo", etiket=(5.42, 25.8), etiket_mod="ad", **o)
    m = p.oda("Merdiven", (X4, Y1, W, Y4), "merdiven", acik="BGK", etiket_mod="yok", **o)
    m.yon, m.basamak, m.kesik, m.merdiven_kutu = "G", 17, 0.0, MERD
    A = p.ac
    A("kapi", 2.55, Y1, 3.45, Y1, ic="-", h=0)                   # ebeveyn
    A("kapi", 4.4, Y1, 5.3, Y1, ic="-", h=0)                     # çocuk 1
    A("kapi", 8.25, YL, 9.1, YL, ic="-", h=0)                    # sükûnet (sahanlıktan)
    A("kapi", 2.4, 19.95, 2.4, 20.8, ic="-", h=0)                # yüklük
    A("kapi", 5.1, Y2_2, 5.9, Y2_2, ic="+", h=0)                 # banyo
    A("kapi", X3, 23.2, X3, 24.05, ic="-", h=0)                  # çocuk 2
    A("kapi", X3, 24.6, X3, 25.45, ic="-", h=0)                  # asansör yeri
    A("pencere", 0.6, a_b, 3.2, a_b, h=1.5)
    A("pencere", 4.0, a_b, 5.8, a_b, h=1.5)
    A("pencere", 6.8, a_b, 8.95, a_b, h=1.5)
    A("pencere", 0.6, a_f, 3.9, a_f, h=1.4)
    A("pencere", 6.55, a_f, 8.0, a_f, h=1.2)
    p.bacalar += [(5.85, 22.6)]
    M = p.mob
    M("yatak2", 0.35, 16.55, yon="B")
    M("dolap", 0.35, 19.0, 1.95, 0.55)
    M("calisma", 3.8, 15.85, 1.2, 0.55, yon="K")
    M("yatak1", 5.15, 16.6, yon="K")
    M("dolap", 3.75, 18.65, 0.6, 0.9)
    M("seccade", 7.2, 17.25, aci=KIBLE)
    M("sedir", 6.95, 15.85, 2.35, 0.5)
    M("dolap", 6.35, 16.55, 0.45, 1.75)
    M("dolap", 0.3, 19.9, 0.6, 2.9)
    M("dolap", 1.0, 22.35, 1.25, 0.5)
    M("dus", 5.1, 21.85, 0.95, 1.0)
    M("wc", 2.55, 22.4, yon="B")
    M("lavabo", 3.7, 22.65)
    M("camasir", 4.3, 21.25)
    M("yatak1", 0.35, 23.15, yon="K")
    M("yatak1", 1.5, 23.15, yon="K")
    M("calisma", 2.6, 25.45, 1.2, 0.55, yon="G")
    M("dolap", 4.7, 23.15, 0.5, 1.0)
    M("sedir", 6.5, 25.5, 1.4, 0.5)
    M("platform", PLATFORM[0] + 0.2, PLATFORM[1] + 0.15, 0.8, 1.25)
    return p


# =============================================================================
# Çevre: komşular, avlu, sokak (eksen sınırları içinde kalır)
# =============================================================================
XL = (-1.6, W + 1.6)
YLIM = (9.2, 28.4)


def cevre(p, kat, ax, kayit):
    """Plan çevresi. Etiket konumları eksen sınırları içinde tutulur (ax.text kırpılmaz)."""
    m = []
    for x0, x1 in ((XL[0], 0.0), (W, XL[1])):
        ax.add_patch(C.Rectangle((x0, YB), x1 - x0, YF - YB, fc="#ecebe6", ec="#b9b5ac", lw=0.5, zorder=0.6))
        kayit.poligon(ax, box(x0, YB, x1, YF), "GORUNUS")
    p.dis_alanlar.append((box(0, YF, W, PD), "#ece7de", "ön eşik · sundurma", (2.3, 26.9)))
    p.dis_alanlar.append((box(XL[0], PD, XL[1], YLIM[1]), "#e6e3dc", "S2 · yaşam sokağı", (1.15, 27.9)))
    if kat == 0:
        p.dis_alanlar.append((box(0, YB - BALKON, W, YB), "yari_acik", "Eyvan · büyüklerin terası\n(üstü balkon)",
                              (6.1, 14.45)))
        p.dis_alanlar.append((box(0, YLIM[0], W, YB - BALKON).difference(box(*HAYAT_M)), "acik",
                              "ortak avlu-bahçe (iki hane)", (5.4, 10.6)))
        C.merdiven_sembol(ax, kayit, HAYAT_M, yon="K", n=16)
        ax.add_patch(C.Rectangle(HAYAT_M[:2], HAYAT_M[2] - HAYAT_M[0], HAYAT_M[3] - HAYAT_M[1], fc="none",
                                 ec=C.YAZI2, lw=0.5, zorder=2.6))
        m.append(ax.text(7.75, 11.55, "hayat\nmerdiveni", ha="center", va="center", fontsize=5.4, color=C.YAZI2,
                         zorder=9))
        m.append(ax.text(-0.8, 21.0, "komşu T2", ha="center", va="center", fontsize=5.6, color=C.YAZI2,
                         rotation=90, zorder=9))
    elif kat == 1:
        p.dis_alanlar.append((box(0, YB - BALKON, W, YB), "teras", f"Balkon {sayi((W - 0.35) * (BALKON - 0.1), 1)} m²",
                              (3.9, 14.05)))
        p.dis_alanlar.append((box(0, YLIM[0], W, YB - BALKON), "#f3f6f3", "avlu boşluğu", (3.9, 11.4)))
        ax.plot([0.15, HAYAT_M[0]], [YB - BALKON + 0.06] * 2, color=C.DUVAR, lw=1.4, zorder=5)
        kayit.cizgi(ax, [(0.15, YB - BALKON + 0.06), (HAYAT_M[0], YB - BALKON + 0.06)], "DUVAR")
        C.merdiven_sembol(ax, kayit, HAYAT_M, yon="G", n=16, kesik=0.0)
        ax.add_patch(C.Rectangle(HAYAT_M[:2], HAYAT_M[2] - HAYAT_M[0], HAYAT_M[3] - HAYAT_M[1], fc="none",
                                 ec=C.YAZI2, lw=0.5, ls=(0, (3, 2)), zorder=2.6))
        m.append(ax.text(7.6, 11.55, "avluya\niniş", ha="center", va="center", fontsize=5.4, color=C.YAZI2,
                         zorder=9))
        m.append(ax.text(8.0, 13.88, "kapı", ha="center", va="center", fontsize=5.0, color=C.YAZI2, zorder=9))
        ax.plot([0.0, W], [YB - SACAK1_D] * 2, color=C.YAZI2, lw=0.5, ls=(0, (4, 2)), zorder=5)
    else:
        p.dis_alanlar.append((box(0, YLIM[0], W, YB), "#f3f6f3", "", None))
        ax.add_patch(C.Rectangle((0, YB - BALKON), W, BALKON, fc="none", ec=C.YAZI2, lw=0.5, ls=(0, (4, 2)),
                                 zorder=2))
        m.append(ax.text(3.9, 14.0, "alttaki balkon (kesikli)", ha="center", va="center",
                         fontsize=5.4, color=C.YAZI2, zorder=9))
        ax.plot([0.0, W], [YB - CATI_SACAK] * 2, color=C.YAZI2, lw=0.6, ls=(0, (1.5, 1.5)), zorder=5)
        m.append(ax.text(3.9, 14.95, f"çatı saçağı {sayi(CATI_SACAK, 1)} m (noktalı)", ha="center", va="center",
                         fontsize=5.4, color=C.YAZI2, zorder=9))
    return m


def vaziyet(fig, kayit, x_mm, y_mm, z):
    xl, yl = (-2.4, W + 2.4), (-6.0, PD + 1.6)
    ax = C.olcekli_eksen(fig, x_mm, y_mm, xl, yl)
    m = []
    alanlar = [(box(xl[0], yl[0], xl[1], 0.0), C.ton(C.AQUA, 0.78)), (box(0, 0, W, YB - BALKON), C.ODA_RENK["acik"]),
               (box(0, YB - BALKON, W, YB), C.ODA_RENK["yari_acik"]), (box(0, YF, W, PD), "#ece7de"),
               (box(xl[0], PD, xl[1], yl[1]), "#e6e3dc")]
    for x0 in (-W, W):
        alanlar += [(box(x0, 0, x0 + W, YB), C.ton(C.AQUA, 0.86))]
    for g, renk in alanlar:
        C.poligon_ciz(ax, g, renk, zorder=0.4)
        kayit.poligon(ax, g, "PEYZAJ")
    for x0 in (-W, W):
        ax.add_patch(C.Rectangle((x0, YB), W, YF - YB, fc="#ecebe6", ec="#b9b5ac", lw=0.5, zorder=0.7))
        kayit.poligon(ax, box(x0, YB, x0 + W, YF), "GORUNUS")
    C.poligon_ciz(ax, z.ayak.intersection(box(0, 0, W, PD)), C.ton(C.SARI, 0.82), ec=C.DUVAR, lw=0.9, zorder=2)
    kayit.poligon(ax, z.ayak, "DUVAR")
    ax.plot([0, W, W, 0, 0], [0, 0, PD, PD, 0], color=C.TURUNCU, lw=0.8, ls=(0, (6, 2)), zorder=3)
    kayit.cizgi(ax, [(0, 0), (W, 0), (W, PD), (0, PD), (0, 0)], "AKS")
    C.merdiven_sembol(ax, kayit, HAYAT_M, yon="K", n=16)
    ax.add_patch(C.Rectangle(HAYAT_M[:2], HAYAT_M[2] - HAYAT_M[0], HAYAT_M[3] - HAYAT_M[1], fc="none", ec=C.YAZI2,
                             lw=0.5, zorder=2.6))
    for (x, y, r) in ((2.4, 4.4, 2.2), (6.4, 6.6, 1.3), (W - 1.0, 2.0, 1.0)):
        ax.add_patch(C.Circle((x, y), r, fc=C.ton(C.AQUA, 0.55), ec=C.ton(C.AQUA, 0.1), lw=0.5, alpha=0.75, zorder=4.5))
        kayit.daire(ax, x, y, r, "PEYZAJ")
    ax.add_patch(C.Rectangle((4.4, 0.6), 2.8, 1.4, fc="none", ec=C.MAVI, lw=0.7, ls=(0, (3, 2)), zorder=5))
    kayit.poligon(ax, box(4.4, 0.6, 7.2, 2.0), "PEYZAJ")
    ax.add_patch(C.Rectangle((0.4, 7.6), 3.2, 2.6, fc=C.ton(C.SARI, 0.7), ec=C.ton(C.SARI, 0.2), lw=0.5, zorder=3))
    kayit.poligon(ax, box(0.4, 7.6, 3.6, 10.2), "PEYZAJ")
    m.append(ax.text(2.0, 8.9, "bostan", ha="center", va="center", fontsize=5.6, zorder=9))
    m.append(ax.text(5.8, 1.3, f"yağmur deposu\n{sayi(DEPO_M3)} m³ (gömülü)", ha="center", va="center", fontsize=5.0,
                     color=C.MAVI, zorder=9))
    m.append(ax.text(2.4, 4.4, "dut", ha="center", va="center", fontsize=5.6, zorder=9))
    m.append(ax.text(5.0, 12.2, "ortak avlu", ha="center", va="center", fontsize=5.8, zorder=9))
    m.append(ax.text(W / 2, 21.0, "T2 · Z+2\n2 bağımsız bölüm", ha="center", va="center", fontsize=6.2, zorder=9))
    m.append(ax.text(W / 2, 14.5, "eyvan", ha="center", va="center", fontsize=5.6, zorder=9))
    m.append(ax.text(W / 2 + 0.6, -2.3, "ortak bahçe şeridi (8 m; yarısı çizildi)", ha="center", va="center",
                     fontsize=5.6, zorder=9))
    m.append(ax.text(W / 2, PD + 0.8, "S2 · yaşam sokağı", ha="center", va="center", fontsize=5.6, color=C.YAZI2,
                     zorder=9))
    m.append(ax.text(-1.2, 21.0, "komşu T2", ha="center", va="center", fontsize=5.4, color=C.YAZI2, rotation=90,
                     zorder=9))
    m.append(ax.text(W + 1.2, 21.0, "komşu T2", ha="center", va="center", fontsize=5.4, color=C.YAZI2, rotation=90,
                     zorder=9))
    m += C.kesit_isareti(ax, kayit, (X_KESIT, -4.4), (X_KESIT, PD + 0.4), "A", yon=(-0.9, 0))
    m += C.olcu(ax, kayit, (0, -3.6), (W, -3.6), f"{sayi(W, 2)}", ust=True)
    m += C.olcu(ax, kayit, (W + 0.6, 0), (W + 0.6, PD), f"{sayi(PD, 2)} (parsel)", ust=False)
    for (a, b) in ((0.0, YB), (YB, YF)):
        m += C.olcu(ax, kayit, (-0.6, a), (-0.6, b), sayi(b - a, 2), ust=True)
    m += C.olcek_cubugu(ax, kayit, -2.0, -5.3, n=5, adim=1.0, h=0.14, yazi=5.2)
    m += C.plan_basligi(ax, "Vaziyet · parsel", xl[0] + 0.1, yl[1] + 0.05)
    return m


# =============================================================================
# Kesit A–A (K–G, x = 3,0; batıya bakış, güney solda)
# =============================================================================
def _ic_duvar(ax, kayit, y, t, z0, z1, kapi):
    """Kesilen iç duvar ve kapı boşluğu (camsız; motorun k_duvar'ı boşluğa cam çizgisi çizer)."""
    if kapi[1] < z1:
        C.k_dolu(ax, kayit, y - t / 2, kapi[1], y + t / 2, z1)
    if kapi[0] > z0:
        C.k_dolu(ax, kayit, y - t / 2, z0, y + t / 2, kapi[0])


def kesit(fig, kayit, x_mm, y_mm):
    s0, s1, z0, z1 = -10.5, 31.0, -2.4, 14.2
    ax = C.olcekli_eksen(fig, x_mm, y_mm, (s0, s1), (z0, z1))
    m = []
    C.k_zemin(ax, kayit, s0, s1, 0.0, kalin=0.0)
    ax.add_patch(C.Rectangle((s0, z0), s1 - s0, -z0, fc=C.ton("#8d887e", 0.82), ec="none", zorder=0.5))
    H = KAT_H
    yb0, yf0 = YB, YF
    # zemin döşemesi, kat döşemeleri
    C.k_dolu(ax, kayit, yb0, -0.3, yf0, 0.0, renk=C.ton(C.DUVAR, 0.55), z=3)
    for k in (1, 2, 3):
        C.k_doseme(ax, kayit, yb0, yf0, k * H, DOS)
    # cepheler (kesilen): güney ve kuzey
    C.k_duvar(ax, kayit, a_b, T_DIS, -0.3, 3 * H + 0.3,
              pencereler=[(0.6, 2.2), (H, H + 2.2), (2 * H + 0.9, 2 * H + 2.4)])
    C.k_duvar(ax, kayit, a_f, T_DIS, -0.3, 3 * H + 0.3,
              pencereler=[(0.9, 2.3), (H + 0.8, H + 2.3), (2 * H + 0.9, 2 * H + 2.3)])
    # iç bölmeler (x = 3,0): zeminde hol açıklığı ve yatak 2 kapısı, 2. katta ebeveyn kapısı
    _ic_duvar(ax, kayit, Y1, T_IC, 0.0, H - DOS, (0.0, 2.2))
    _ic_duvar(ax, kayit, Y3, T_IC, 0.0, H - DOS, (0.0, 2.1))
    C.k_duvar(ax, kayit, Y3, T_IC, H, 2 * H - DOS)
    _ic_duvar(ax, kayit, Y1, T_IC, 2 * H, 3 * H - DOS, (2 * H, 2 * H + 2.1))
    C.k_duvar(ax, kayit, Y2_2, T_IC, 2 * H, 3 * H - DOS)
    C.k_duvar(ax, kayit, Y3_2, T_IC, 2 * H, 3 * H - DOS)
    # balkon (dikmeli), parapet, güneş kırıcı
    C.k_dolu(ax, kayit, YB - BALKON, H - 0.22, YB, H)
    C.k_dolu(ax, kayit, YB - BALKON, H, YB - BALKON + 0.1, H + 1.1)
    C.k_gorunus(ax, kayit, YB - BALKON + 0.03, 0.0, YB - BALKON + 0.28, H - 0.22, ec=C.DUVAR, lw=0.5)
    C.k_dolu(ax, kayit, YB - SACAK1_D, SACAK1_Z, YB, SACAK1_Z + 0.1)
    # çatı (kırma, 30°)
    C.k_cati(ax, kayit, yb0, yf0, 3 * H + 0.3, egim=EGIM, sacak=CATI_SACAK)
    # avlu: ağaç, yağmur deposu, hayat merdiveni (görünüş), ortak şerit
    C.k_agac(ax, kayit, 4.4, 0.0, govde=2.6, tac=2.2)
    C.k_agac(ax, kayit, 6.6, 0.0, govde=1.6, tac=1.3)
    C.k_agac(ax, kayit, -5.5, 0.0, govde=2.8, tac=2.2)
    ax.add_patch(C.Rectangle((0.6, -1.8), 1.4, 1.4, fc=C.ton(C.MAVI, 0.85), ec=C.MAVI, lw=0.6, ls=(0, (3, 2)), zorder=2))
    kayit.poligon(ax, box(0.6, -1.8, 2.0, -0.4), "GORUNUS")
    m.append(ax.text(2.2, -1.1, f"yağmur suyu deposu ≈ {sayi(DEPO_M3)} m³ (arkada)", ha="left", va="center",
                     fontsize=5.4, color=C.MAVI, zorder=9))
    stp = [(HAYAT_M[1], 0.0), (HAYAT_M[3], H)]
    ax.plot([p[0] for p in stp], [p[1] for p in stp], color="#8d887e", lw=0.8, zorder=2)
    ax.plot([HAYAT_M[1], HAYAT_M[3]], [0.9, H + 0.9], color="#8d887e", lw=0.5, zorder=2)
    kayit.cizgi(ax, stp, "GORUNUS")
    # sokak, ön eşik, sundurma (görünüş)
    C.k_gorunus(ax, kayit, YF, 2.55, YF + 0.9, 2.65, ec=C.YAZI2, lw=0.5, ls=(0, (2, 1.5)))
    # insanlar
    C.k_insan(ax, 14.4, 0.0, yasli=True)
    C.k_insan(ax, 9.0, 0.0, cocuk=True)
    C.k_insan(ax, 14.6, H)
    C.k_insan(ax, 19.4, 2 * H, cocuk=True)
    # güneş ışınları (öğle)
    a_ara = ogle_yuksekligi(S["enlem"], GUN["21 Aralık"])
    a_haz = ogle_yuksekligi(S["enlem"], GUN["21 Haziran"])
    _, t = C.k_gunes(ax, kayit, YB - BALKON, H - 0.22, a_ara, +1, 8.0, C.MAVI, f"21 Ara öğle {sayi(a_ara, 1)}°",
                     z_min=0.0)
    m.append(t)
    C.k_gunes(ax, kayit, YB - SACAK1_D, SACAK1_Z, a_ara, +1, 8.0, C.MAVI, None, z_min=H)
    _, t = C.k_gunes(ax, kayit, YB - SACAK1_D, SACAK1_Z, a_haz, +1, 1.0, C.TURUNCU, f"21 Haz öğle {sayi(a_haz, 1)}°",
                     z_min=H)
    m.append(t)
    C.k_gunes(ax, kayit, YB - BALKON, H - 0.22, a_haz, +1, 1.0, C.TURUNCU, None, z_min=0.0)
    # metinler
    for (s, z, metin, renk) in ((17.5, 1.45, "büyükler\noturma", C.YAZI), (21.15, 1.45, "hol", C.YAZI),
                                (24.5, 1.45, "yatak 2", C.YAZI), (18.5, H + 1.45, "aile oturma\nve yemek", C.YAZI),
                                (24.5, H + 1.45, "misafir\n(selamlık)", C.YAZI), (17.5, 2 * H + 1.45, "ebeveyn", C.YAZI),
                                (20.4, 2 * H + 1.45, "hol", C.YAZI), (22.05, 2 * H + 1.45, "banyo", C.YAZI), (24.7, 2 * H + 1.45, "çocuk 2", C.YAZI),
                                (20.9, 3 * H + 1.25, "çatı arası (yalıtımlı)", C.YAZI2), (14.1, 6.0, "balkon", C.YAZI2),
                                (11.9, 0.45, "eyvan", C.YAZI2), (2.0, 0.45, "ortak avlu", C.YAZI2),
                                (-4.0, -0.75, "ortak şerit (8 m)", C.YAZI2), (29.2, -0.75, "S2 sokak", C.YAZI2),
                                (26.9, -0.75, "ön eşik", C.YAZI2), (11.2, H + 1.6, "hayat\nmerdiveni", C.YAZI2)):
        m.append(ax.text(s, z, metin, ha="center", va="center", fontsize=5.9, color=renk, zorder=9))
    m.append(ax.text(s0 + 0.2, 7.4, "← güneydeki T1 sırası:\ngenişleme 21,4 m,\nZ+2 çekirdek 25,4 m\n"
                     "güneyde [V]; 21 Ara\nöğle gölgesi şeritte biter", ha="left", va="center", fontsize=5.4,
                     color=C.YAZI2, zorder=9, linespacing=1.2))
    # ölçüler
    xo = YF + 2.2
    for k in range(3):
        m += C.olcu(ax, kayit, (xo, k * H), (xo, (k + 1) * H), sayi(H, 2), ust=False)
    m += C.olcu(ax, kayit, (22.6 + 0.9, H), (22.6 + 0.9, 2 * H - DOS), f"iç {sayi(H - DOS, 2)}", ust=False)
    for (a, b) in ((-8.0, 0.0), (0.0, YB - BALKON), (YB - BALKON, YB), (YB, YF), (YF, PD)):
        m += C.olcu(ax, kayit, (a, -2.05), (b, -2.05), sayi(b - a, 2), ust=True)
    m += C.plan_basligi(ax, "Kesit A–A", s0 + 0.2, z1 - 1.0, alt="güney solda · batıya bakış · x = 3,0 m · 1/100")
    m += C.olcek_cubugu(ax, kayit, 25.0, 12.6, n=5, adim=1.0, h=0.16)
    return m, (a_ara, a_haz)


def gorunus(fig, kayit, x_mm, y_mm):
    """Güney görünüşü (avlu cephesi), iki yanda komşu T2'lerin bir parçası."""
    xl, zl = (-4.0, W + 4.0), (-0.6, 13.6)
    ax = C.olcekli_eksen(fig, x_mm, y_mm, xl, zl)
    m = []
    H = KAT_H
    ust = 3 * H + 0.3
    ax.plot([xl[0], xl[1]], [0, 0], color=C.DUVAR, lw=0.9, zorder=2)
    kayit.cizgi(ax, [(xl[0], 0), (xl[1], 0)], "GORUNUS")
    for x0, x1, fc in ((xl[0], 0.0, "#f1f0ec"), (0.0, W, C.ton(C.SARI, 0.93)), (W, xl[1], "#f1f0ec")):
        C.k_gorunus(ax, kayit, x0, 0, x1, ust, ec=C.DUVAR if fc != "#f1f0ec" else "#b9b5ac", fc=fc, lw=0.7, z=2)
    ridge = ust + (MODEL["T2_EV_DER"] / 2 + CATI_SACAK) * math.tan(math.radians(EGIM))
    C.k_gorunus(ax, kayit, xl[0], ust, xl[1], ridge, ec=C.DUVAR, fc=C.ton(C.TURUNCU, 0.55), lw=0.7, z=3)
    ax.plot([xl[0], xl[1]], [ust - 0.1] * 2, color=C.DUVAR, lw=1.1, zorder=3.2)
    for x in (0.0, W):
        ax.plot([x, x], [0, ridge], color=C.DUVAR, lw=0.5, zorder=3.3)
    acik = [(0.45, 1.95, 0, 2.2), (2.3, 3.55, 0.6, 2.2), (4.25, 5.95, 0.9, 2.2), (6.7, 7.6, 0, 2.1), (8.0, 9.15, 0.7, 2.2),
            (0.45, 1.95, H, H + 2.2), (2.25, 4.25, H, H + 2.2), (5.1, 6.6, H + 0.9, H + 2.2), (7.25, 8.15, H, H + 2.1),
            (8.45, 9.15, H + 0.9, H + 2.2), (0.6, 3.2, 2 * H + 0.9, 2 * H + 2.4), (4.0, 5.8, 2 * H + 0.9, 2 * H + 2.4),
            (6.8, 8.95, 2 * H + 0.9, 2 * H + 2.4)]
    for (a, b, za, zb) in acik:
        C.k_gorunus(ax, kayit, a, za, b, zb, ec=C.DUVAR, fc=C.ton(C.MAVI, 0.8), lw=0.5, z=3.5)
        ax.plot([(a + b) / 2] * 2, [za, zb], color=C.DUVAR, lw=0.3, zorder=3.6)
    # komşu cephelerinde aynı açıklıklar (soluk)
    for dx in (-W, W):
        for (a, b, za, zb) in acik:
            if xl[0] < a + dx < xl[1] or xl[0] < b + dx < xl[1]:
                aa, bb = max(a + dx, xl[0]), min(b + dx, xl[1])
                C.k_gorunus(ax, kayit, aa, za, bb, zb, ec="#b9b5ac", fc=C.ton(C.MAVI, 0.9), lw=0.4, z=2.5)
    # balkon, korkuluk, dikmeler, güneş kırıcı
    for dx, ec in ((0.0, C.DUVAR), (-W, "#b9b5ac"), (W, "#b9b5ac")):
        a, b = max(dx, xl[0]), min(dx + W, xl[1])
        C.k_gorunus(ax, kayit, a, H - 0.22, b, H, ec=ec, fc="#d9d5cc" if dx == 0 else "#ecebe6", lw=0.6, z=4)
        ax.plot([a, b], [H + 1.1] * 2, color=ec, lw=0.9, zorder=4.2)
        xx = a + 0.15
        while xx < b - 0.05:
            if not (dx == 0 and HAYAT_M[0] < xx < HAYAT_M[2]):
                ax.plot([xx, xx], [H, H + 1.1], color=ec, lw=0.3, zorder=4.1)
            xx += 0.3
        C.k_gorunus(ax, kayit, a, SACAK1_Z, b, SACAK1_Z + 0.1, ec=ec, fc="#d9d5cc", lw=0.5, z=4)
        for x in (0.3, W / 2, W - 0.3):
            if xl[0] < x + dx < xl[1]:
                C.k_gorunus(ax, kayit, x + dx - 0.125, 0, x + dx + 0.125, H - 0.22, ec=ec, fc="#d9d5cc", lw=0.5, z=4)
    # hayat merdiveni (önden): basamak çizgileri ve korkuluk
    C.k_gorunus(ax, kayit, HAYAT_M[0], 0, HAYAT_M[2], H, ec=C.DUVAR, fc="none", lw=0.6, z=4.5)
    for k in range(1, 17):
        ax.plot([HAYAT_M[0], HAYAT_M[2]], [k * H / 17] * 2, color=C.DUVAR, lw=0.3, zorder=4.5)
    ax.plot([HAYAT_M[0], HAYAT_M[0]], [0, H + 1.0], color=C.DUVAR, lw=0.7, zorder=4.6)
    C.k_insan(ax, 3.0, 0.0, yasli=True)
    C.k_insan(ax, 1.5, 0.0, cocuk=True)
    C.k_insan(ax, 5.8, H)
    m.append(ax.text(W / 2, ridge + 0.25, f"beşik çatı {sayi(EGIM, 0)}°, saçak {sayi(CATI_SACAK, 1)} m · kar yükü",
                     ha="center", va="bottom", fontsize=5.6, color=C.YAZI2))
    m.append(ax.text(xl[0] + 0.2, H + 0.55, "komşu", ha="left", va="center", fontsize=5.4, color=C.YAZI2, zorder=9))
    m += C.olcu(ax, kayit, (xl[1] - 0.6, 0), (xl[1] - 0.6, ust), sayi(ust, 2), ust=False)
    m += C.olcu(ax, kayit, (xl[1] - 0.6, ust), (xl[1] - 0.6, ridge), sayi(ridge - ust, 2), ust=False)
    m += C.plan_basligi(ax, "Güney görünüşü (avlu cephesi)", xl[0] + 0.1, zl[1] + 0.05, alt=None)
    m += C.olcek_cubugu(ax, kayit, xl[0] + 0.3, -0.3, n=5, adim=1.0, h=0.12, yazi=5.0)
    return m


# =============================================================================
# Güneş ve değerlendirme
# =============================================================================
def _t1_guney():
    """Güneydeki T1 sırası (model v2.1, son durum): çekirdek Z+2 ve 4 m genişleme [V]."""
    cekirdek_kuzey = -MODEL["ORTA_BANT"] - (PD - ON - MODEL["T1_EV_DER"])            # −25,4
    gen_kuzey = cekirdek_kuzey + MODEL["T1_GENISLEME"]                                 # −21,4
    return [(-60, cekirdek_kuzey - MODEL["T1_EV_DER"], 0, 60, cekirdek_kuzey, 3 * KAT_H + 0.5),
            (-60, cekirdek_kuzey, 0, 60, gen_kuzey, KAT_H + 1.0)]


def gunes_hesabi():
    """Dubleksin aile oturması: balkon kapısının ortası (1. kat, z 4,3 m) [H].
    Engeller: 0,9 m güneş kırıcı (sıra boyunca), güneydeki T1 sırası. Ağaçlar yaprak döken [V]."""
    kutular = [(-40, YB - SACAK1_D, SACAK1_Z, 50, YB, SACAK1_Z + 0.1)] + _t1_guney()
    nokta = (1.2, YB - 0.01, KAT_H + 1.2)
    return {g: gunes_saati(nokta, 180.0, kutular, S["enlem"], GUN[g]) for g in GUN}


def gunes_buyukler():
    """Büyüklerin oturması: eyvana açılan kapının ortası (z 1,2 m) [H]. Engel: üstteki balkon, hayat merdivenleri."""
    kutular = [(-40, YB - BALKON, H_B, 50, YB, KAT_H) for H_B in (KAT_H - 0.22,)]
    kutular += [(HAYAT_M[0], HAYAT_M[1], 0, HAYAT_M[2], HAYAT_M[3], 2.0),
                (HAYAT_M[0] - W, HAYAT_M[1], 0, HAYAT_M[2] - W, HAYAT_M[3], 2.0)] + _t1_guney()
    nokta = (1.2, YB - 0.01, 1.2)
    return {g: gunes_saati(nokta, 180.0, kutular, S["enlem"], GUN[g]) for g in GUN}


def _tablo_h(n, satir_h, alt_satir=0):
    """tablo_ciz'in yüksekliği (başlıklı)."""
    return 6.5 + satir_h * (n + 1) + 1.5 + 4.5 * alt_satir


def net_birim(planlar, birim):
    return sum(o.net.area for _, p in planlar for o in p.odalar
               if o.birim == birim and o.say and not o.yari_acik and o.tur not in C.ACIK_TURLER)


def ciz():
    z, k1, k2 = zemin(), kat1(), kat2()
    planlar = [("Zemin", z), ("1. kat", k1), ("2. kat", k2)]
    kayit = Kayit()
    fig = C.pafta()
    m = C.baslik(fig, "Tip (d) · T2 avlulu çok kuşaklı ev — karasal iklim",
                 f"Model mahalle v2.1 T2 (K2): parsel {sayi(W, 2)} × {sayi(PD, 1)} m ({sayi(W * PD, 0)} m²), ön eşik "
                 f"{sayi(ON, 1)} m, bina derinliği {sayi(MODEL['T2_EV_DER'], 1)} m, Z+2, kat {sayi(KAT_H, 2)} m. "
                 f"Referans {SEHIR_AD} ({sayi(S['enlem'], 1)}° K; Ocak ort. en düşük {sayi(S['t_min'][0], 1)} °C, "
                 f"Ağustos ort. en yüksek {sayi(S['t_max'][7], 1)} °C, yıllık yağış {sayi(S['yagis_yil'])} mm; MGM "
                 f"{S['donem']} [D]). Sokak kuzeyde. Duvar 35 cm; malzeme seçenekleri Rapor 16.")
    # --- planlar -------------------------------------------------------------------------------
    yer = [(z, 0, 168, "Zemin · büyükler dairesi (2+1, eşiksiz)"), (k1, 1, 300, "1. kat · dubleks: sofa ve selamlık"),
           (k2, 2, 432, "2. kat · dubleks: aile katı")]
    for p, kat, xmm, ad in yer:
        ax = C.olcekli_eksen(fig, xmm, 364, XL, YLIM)
        m += cevre(p, kat, ax, kayit)
        m += p.ciz(ax, kayit, yazi=5.6)
        m += C.plan_basligi(ax, ad, XL[0] + 0.1, YLIM[1] + 0.05)
        m += C.olcek_cubugu(ax, kayit, 4.3, 27.95, n=5, adim=1.0, h=0.14, yazi=5.2)
        if kat == 0:
            m += C.kesit_isareti(ax, kayit, (X_KESIT, 9.75), (X_KESIT, PD + 0.1), "A", yon=(-0.9, 0))
            m += z.olcu_zinciri(ax, kayit, [0.0, 3.85, 6.4, W], 9.75, yatay=True, ust=True, yazi=5.2)
    m += vaziyet(fig, kayit, 14, 196, z)
    mk, (a_ara, a_haz) = kesit(fig, kayit, 168, 190)
    m += mk
    m += C.yon_diyagrami(fig, 14, 120, 62, S["enlem"], SEHIR_AD, KIBLE,
                         [("21 Haz", GUN["21 Haziran"], C.TURUNCU), ("21 Ara", GUN["21 Aralık"], C.MAVI)])
    lm, lh = C.lejant(fig, 84, 132, 206, ["misafir", "yasam", "yatak", "mutfak", "islak", "esik", "sukunet", "depo",
                                          "dolasim", "merdiven", "yari_acik", "acik", "teras"],
                      ek=[(C.DUVAR, "duvar (35 cm, kesilen)", "duvar"), (C.MAVI, "pencere, camlı kapı", "pencere"),
                          (C.MAVI, "asansör yeri: platform kabini 0,8 × 1,25 m", "cizgi"),
                          (C.AQUA, "kıble yönü", "kible"), (C.YAZI2, "hava bacası", "baca")])
    m += lm
    # --- hesaplar -------------------------------------------------------------------------------
    gs, gb = gunes_hesabi(), gunes_buyukler()
    for _, p in planlar:
        p.hesapla()
    brut_kat = W * MODEL["T2_EV_DER"]                            # parti duvarı ekseninden [H]
    bina_brut = 3 * brut_kat
    net_z = sum(o.net.area for o in z.odalar if o.say)
    n_b, n_dz = net_birim([("Zemin", z)], "buyukler"), net_birim([("Zemin", z)], "dubleks")
    n_o = net_birim([("Zemin", z)], "ortak")
    brut_b = brut_kat * (n_b + n_o / 2) / net_z
    brut_d = 2 * brut_kat + brut_kat * (n_dz + n_o / 2) / net_z
    balkon = (W - 0.35) * (BALKON - 0.1)
    eyvan = (W - 0.35) * BALKON
    avlu = W * (YB - BALKON) - (HAYAT_M[2] - HAYAT_M[0]) * (HAYAT_M[3] - HAYAT_M[1])
    serit = MODEL["ORTA_BANT"] / 2 * W
    cati = (W) * (MODEL["T2_EV_DER"] + 2 * CATI_SACAK)
    yil = yagmur_potansiyeli(cati, SEHIR_AD)
    bina_net = net_birim(planlar, "buyukler") + net_birim(planlar, "dubleks") + n_o
    yapim_d = yapim_maliyeti(brut_d, "III.A", balkon)
    yapim_b = yapim_maliyeti(brut_b, "III.A")
    esneklik = ("Büyükler katı ayrı BB: sonra genç çifte, bakıcıya ya da kiraya; misafir odası 4. yatak olur; "
                "asansör yeri bugün depo")
    mahremiyet = ("Tek sokak kapısı, ortak taşlık, iki ayrı kapı; dubleksin 1. katında sofaya açılan selamlık, "
                  "2. kat aile katı")
    ek = dict(kusak=("Çok kuşak", "büyükler ayrı BB, eşiksiz, aynı avlu ve taşlık", "zemin 2+1 · ortak avlu", "✓"),
              buyume_satir=("Esneklik", "ruhsatla büyüme ya da bölünme payı", "2 BB el değiştirir; misafir → 4. yatak", "✓"),
              erisim=("Erişim", "asansör yeri 1,4 × 1,6 m (PAİY 34/1); zemin eşiksiz",
                      "kuyu her katta depo · platform [V]", "✓"),
              su=("Su", f"çatı 100 m² başına ≥ {sayi(OLCUT['yagmur_m3_100m2'])} m³ depo",
                  f"depo {sayi(DEPO_M3)} m³ · {sayi(100 * DEPO_M3 / cati, 1)} m³/100 m²",
                  "✓" if DEPO_M3 / cati * 100 >= OLCUT["yagmur_m3_100m2"] else "≈"),
              deprem=("Deprem", "Z+2, düzenli aks, perde parti duvarı, balkon dikmeli", "konsol yok · Z+2", "✓"),
              isil=("Isıl konfor", "kuzeyde servis tamponu, güneyde cam; yazın gölge",
                    f"Ara öğle {sayi(a_ara, 1)}° içeri · Haz kırıcıda", "✓"),
              sessizlik=("Sessizlik", "yatak odaları avluya ya da S2'ye; BB arası 35 cm", "çift yönlü; ölçülmedi [V]",
                         "≈"))
    oz = birim_ozeti(planlar, "dubleks", acik_ozel=balkon, acik_ortak=avlu / 2 + serit / 2,
                     ic_yukseklik=KAT_H - DOS, gunes=gs, arsa=W * PD / 2, ek=ek)
    oz["esik"] = True                       # dubleksin eşiği ortak taşlık (iki hane) [H]
    ozb = birim_ozeti(planlar, "buyukler", hane=2, acik_ozel=eyvan, acik_ortak=avlu / 2 + serit / 2,
                      ic_yukseklik=KAT_H - DOS, gunes=gb, arsa=W * PD / 2)
    ozb.update(dict(brut=brut_b, yapim=yapim_b, eyvan=eyvan))
    ozet = [("Dubleks net (5 kişi) · brüt", f"{sayi(oz['net'], 1)} m² · {sayi(brut_d, 1)} m²"),
            ("Büyükler net (2 kişi) · brüt", f"{sayi(ozb['net'], 1)} m² · {sayi(brut_b, 1)} m²"),
            ("Ortak taşlık (net)", f"{sayi(n_o, 1)} m²"),
            ("Bina net · brüt (ekseninden)", f"{sayi(bina_net, 1)} m² · {sayi(bina_brut, 1)} m²"),
            ("Avlu (ortak) · eyvan · balkon", f"{sayi(avlu, 0)} · {sayi(eyvan, 1)} · {sayi(balkon, 1)} m²"),
            ("Parsel · oturum · emsal", f"{sayi(W * PD, 0)} m² · %{sayi(100 * brut_kat / (W * PD), 0)} · "
                                        f"{sayi(bina_brut / (W * PD), 2)}"),
            ("Net / kişi: dubleks · büyükler", f"{sayi(oz['net_kisi'], 1)} · {sayi(ozb['net_kisi'], 1)} m²"),
            ("Yağmur suyu potansiyeli", f"{sayi(yil, 0)} m³/yıl (çatı {sayi(cati, 0)} m² × {sayi(S['yagis_yil'])} mm × 0,8)"),
            ("Kaba yapım: dubleks · büyükler [V]", f"{sayi(yapim_d / 1e6, 2)} · {sayi(yapim_b / 1e6, 2)} mn TL (III.A)"),
            ("Model sabitleri", model_denetle())]
    mm_, y = sag_sutun(fig, 602, 560, 226, planlar, oz, ozet, birim_adlari=ADLAR, yazi=5.4, satir_h=3.3,
                       ust_baslik="Alan programı (net, m²; B büyükler · D dubleks · O ortak) [H]")
    m += mm_
    gsat = [(g, f"{sayi(ogle_yuksekligi(S['enlem'], GUN[g]), 1)}°", f"{sayi(gs[g], 1)} sa", f"{sayi(gb[g], 1)} sa")
            for g in GUN]
    h = _tablo_h(len(gsat), 3.6, 2)
    tm, th = C.tablo_ciz(fig, 602, y - h, 226, ["Gün", "Öğle yüksekliği", "Dubleks oturma", "Büyükler oturma"],
                         gsat, [0, 45, 100, 165], baslik_metin="Güneş saati: güney kapılarının ortası [H]", yazi=5.8,
                         satir_h=3.6, hizalar=["left", "right", "right", "right"],
                         alt_not="Dubleks z 4,3 m (engel 0,9 m kırıcı); büyükler z 1,2 m (engel 1,8 m balkon, hayat\n"
                                 "merdivenleri). Güneyde T1 sırası (model v2.1 son durum). Ağaçlar yaprak döken [V].")
    m += tm
    y = y - th - 9.0
    m += gorunus(fig, kayit, 602 + (226 - (W + 8.0) * 10) / 2, y - 142.0)
    y = y - 142.0 - 5.0
    notlar = [
        "• Tek sokak kapısı ortak taşlığa açılır: büyüklerin kapısı, dubleksin merdiven kapısı ve asansör yeri orada.",
        "• Büyükler dairesi eşiksiz: oturma, mutfak ve büyükler odası avluya bakar; banyo kapısı dışa açılır.",
        "• Dubleksin 1. katı sofadır: misafir odası sokak yanında, aile oturması ve mutfak avlu yanında.",
        "• 2. kat aile katıdır (harem): üç yatak odası, sükûnet odası (kıble 160°), yüklük ve banyo.",
        "• Balkon (1,8 m) dikmelerle taşınır, altı büyüklerin eyvanı. Hayat merdiveni avluya iner (üstte kapı).",
        "• Kışın öğle güneşi (26,6°) iki katta da odanın dibine ulaşır; yazın balkon ve kırıcı camı gölgeler.",
        "• Kuzeyde taşlık, merdiven, kiler ve ıslak hacimler tampon olur; iki BB arası duvar 35 cm.",
        "• Asansör yeri (1,4 × 1,6 m) her katta depo; gerekince platform takılır (≈ 0,9 mn TL [V]).",
    ]
    nh = 6 + 3.35 * len(notlar) + 1
    nt, nh = C.metin_kutusu(fig, 602, y - nh, 226, "Tasarım notları", notlar, yazi=5.7, satir_h=3.35)
    m += nt
    y = y - nh - 6.0
    gl = ["Geniş aile evi: oğul evlenince aynı avluya oda ya da kat eklenir; kuşaklar ayrı odada, ortak avluda yaşar.",
          "İç Anadolu evi: kışlık odalar kalın duvarlı ve kompakt, üst kat yazlık; sofa ve avluya inen merdiven.",
          "Beypazarı tarihî çekirdeği bu dokuya örnek (Rapor 11, örnek G3).",
          "Kaynak: Eldem 1954, 1984; Küçükerman 1988; Rapor 15 §3.3."]
    gh = 6 + 3.4 * len(gl) + 1
    gk, gh = C.metin_kutusu(fig, 602, y - gh, 226, "Geleneksel karşılığı [İ]", gl, yazi=5.7, satir_h=3.4)
    m += gk
    print(f"  sağ sütun alt kenarı: {y - gh:.1f} mm (künye üstü 38)")
    # --- alt bant: esneklik, büyükler özeti -----------------------------------------------------
    esat = [("Bugün", "büyükanne ve büyükbaba (2)", "genç aile (5)", "—"),
            ("Çocuklar büyür", "aynı", "misafir odası 4. yatak; sükûnet odası çalışma", "yalnız mobilya"),
            ("Bakım gerekir", "bakıcı yatak odası 2'de", "aynı", "banyo zaten engelsiz"),
            ("Kuşak değişir", "evlenen çocuk (2–3 kişi)", "büyükler dubleksde; asansör yerine platform",
             f"≈ {sayi(0.9, 1)} mn TL [V]"),
            ("Hane küçülür", "kiraya verilir", "aynı", "ayrı BB, ayrı tapu")]
    h = _tablo_h(len(esat), 4.2)
    tm, th = C.tablo_ciz(fig, 84, 124 - h, 206, ["Dönem", "Zemin (B)", "Dubleks (D)", "Gereken"], esat,
                         [0, 24, 72, 156], baslik_metin="Hane yaşam döngüsü: aynı bina, değişen kullanım [V]", yazi=5.6,
                         satir_h=4.2)
    m += tm
    bsat = [("Net alan · net/kişi (2 kişi)", f"{sayi(ozb['net'], 1)} m² · {sayi(ozb['net_kisi'], 1)} m²"),
            ("Oda · yatak", f"{ozb['oda']} · {ozb['yatak']} (2+1)"),
            ("Cam/taban, en düşük oda", f"{sayi(ozb['pencere_min'], 2)} ({ozb['pencere_min_oda'][:14]})"),
            ("Yönler", ozb["yonler"] + (" · karşıt" if ozb["karsit_cephe"] else "")),
            ("Güneş 21 Şubat · 21 Aralık", f"{sayi(gb['21 Şubat'], 1)} · {sayi(gb['21 Aralık'], 1)} sa (Mart–Eylül eyvan gölgesi)"),
            ("Kiler · depolama payı", f"{sayi(ozb['kiler'], 1)} m² · %{sayi(100 * ozb['depo_pay'], 1)}"),
            ("Giriş · kot farkı", "ortak taşlıktan · yok (zemin, eyvan, avlu aynı kotta)"),
            ("Özel dış mekân · ortak avlu payı", f"eyvan {sayi(eyvan, 1)} m² · {sayi(avlu / 2 + serit / 2, 0)} m²"),
            ("Kaba yapım [V]", f"{sayi(yapim_b / 1e6, 2)} mn TL (brüt {sayi(brut_b, 1)} m², III.A)")]
    h = _tablo_h(len(bsat), 4.2)
    tm, th = C.tablo_ciz(fig, 302, 184 - h, 288, ["Büyükler dairesi (zemin, 2+1)", "Değer"], bsat, [0, 110],
                         baslik_metin="Büyükler dairesi özeti [H]", yazi=6.0, satir_h=4.2, hizalar=["left", "right"])
    m += tm
    m += C.kunye(fig, 602, 14, 226, "K-d")
    sorun, dxf = C.kaydet(fig, kayit, AD)
    oz.update(dict(tip="d", ad="Çok kuşaklı avlu evi (T2)", sehir=SEHIR_AD, brut=brut_d, sinif="III.A",
                   parsel=W * PD, kat="Z+2", yapim=yapim_d, asansor=0.0, sorun=len(sorun), dxf=dxf, yari=balkon,
                   arsa_hane=W * PD / 2, hane_sayisi=2, buyume=0.0, bina_brut=bina_brut, bina_net=bina_net,
                   acik_ozel=balkon, acik_ortak=avlu / 2 + serit / 2, avlu=avlu, eyvan=eyvan, serit_payi=serit / 2,
                   sarnic=DEPO_M3, yagmur_yil=yil, cati=cati, esneklik=esneklik, mahremiyet=mahremiyet,
                   buyukler=ozb, taslik=n_o))
    return oz, csv_satirlari("d", planlar, ADLAR)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    oz, _ = ciz()
    for k, v in oz.items():
        if k not in ("gunes", "buyukler"):
            print(k, v)
    print("güneş", oz["gunes"])
    print("büyükler", {k: v for k, v in oz["buyukler"].items() if k not in ("gunes",)})
    print("büyükler güneş", oz["buyukler"]["gunes"])
