"""
Tip (c) — T1 büyüyebilen sıra ev: ayrıntılı plan ve üç büyüme aşaması (İstanbul, 41,0° K)
=========================================================================================
Model mahalle v2.1'in T1 tipinin (07_TASARIM_CIZIM/model_mahalle_v2/kod/plan_modeli.py,
konut_tipolojileri.py) ayrıntılandırılması. Parsel ve çekirdek ölçüleri modelden alınır
(K2: 6,37 × 27,4 m; ön eşik 1,0 m; çekirdek 9,0 m; arka genişleme; 8 m ortak bahçe şeridi).
Model dosyaları yalnız okunur (sabitlerin aynı olduğu denetlenir, hiçbir dosya yazılmaz).

Aşama 1: çekirdek Z+1 (2+1, 3–4 kişi) · Aşama 2: zeminde L biçimli arka oda (büyükler odası +
engelsiz duş) ve üstünde teras · Aşama 3: 2. kat (+2 yatak, banyo) → 4+1 + büyükler odası.
Ayrıntılı tasarımın modelden farkı: genişleme parselin tamamını değil doğu 3,9 m'sini kaplar;
oturma odası bahçe ışığını korur. Komşu evler çift çift aynalanır (avlucuklar yan yana).
Koordinat: x doğuya (parsel batı sınırı 0), y kuzeye (parselin bahçe ucu 0, sokak 27,4).
"""

from __future__ import annotations

import re
from pathlib import Path

from shapely.geometry import box

import cizim as C
from cizim import Blok, Kayit, Plan
from degerlendirme import birim_ozeti, csv_satirlari, olcut_satirlari, sag_sutun
from veri import GUN, OLCUT, SEHIR, gunes_saati, kible, ogle_yuksekligi, sayi, yagmur_potansiyeli, yapim_maliyeti

AD = "tip_c_buyuyen_sira_ev"
SEHIR_AD = "İstanbul"
S = SEHIR[SEHIR_AD]
KIBLE = kible(S["enlem"], S["boylam"])

# --- model mahalle v2.1 sabitleri (plan_modeli.py; yalnız okunur) ---------------------------
MODEL = dict(TY=12.0, CY=375.0, CADDE_G=18.0, S2_G=10.0, ORTA_BANT=8.0, ON_ESIK_K2=1.0, T1_EV_DER=9.0,
             T1_GENISLEME=4.0, GECIT_G=5.0, T1_GEN=6.0, CX=400.0)


def model_denetle():
    """plan_modeli.py'deki sabitler bu dosyadakilerle aynı mı? (yalnız metin okunur)"""
    yol = Path(__file__).resolve().parents[2] / "model_mahalle_v2" / "kod" / "plan_modeli.py"
    if not yol.exists():
        return "plan_modeli.py bulunamadı: sabitler denetlenmedi"
    t = yol.read_text(encoding="utf-8")
    beklenen = [r"T1_EV_DER, T2_EV_DER = 9\.0, 11\.0", r"T1_GENISLEME = 4\.0", r"ORTA_BANT = 8\.0",
                r"ON_ESIK_K2 = 1\.0 if KALIBRE", r"T1_GEN, T2_GEN = 6\.0, 9\.2", r"GECIT_G = 5\.0", r"S2_G = 10\.0",
                r"CADDE_G = 18\.0", r"TY = 12\.0", r"CX, CY = 400\.0, 375\.0"]
    eksik = [b for b in beklenen if not re.search(b, t)]
    return "model sabitleri aynı" if not eksik else f"farklı: {eksik}"


_ADA_W = (MODEL["CX"] - MODEL["CADDE_G"] / 2 - MODEL["TY"] - 2 * MODEL["S2_G"]) / 3       # 119,67 m
_ADA_D = (MODEL["CY"] - MODEL["CADDE_G"] / 2 - MODEL["TY"] - 4 * MODEL["S2_G"]) / 5       # 62,8 m
_SIRA = (_ADA_W - MODEL["GECIT_G"]) / 2
W = _SIRA / int(_SIRA // MODEL["T1_GEN"])            # 6,37 m (K2)
PD = (_ADA_D - MODEL["ORTA_BANT"]) / 2               # 27,4 m
ON = MODEL["ON_ESIK_K2"]
YF = PD - ON                                         # ön cephe dış yüzü 26,4
YB = YF - MODEL["T1_EV_DER"]                         # çekirdek arka yüzü 17,4
EK_D, EK_W = 5.0, 3.9                                # L genişleme: derinlik, genişlik [V]
T_DIS, T_IC = 0.30, 0.15
KAT_H, DOS = 3.10, 0.30
a_f, a_b = YF - 0.15, YB + 0.15                      # cephe eksenleri
XM, XS = 3.65, 5.0                                   # iç aks: mutfak/yatak | hol | merdiven
MERD = (XS + 0.075, 19.85, W - 0.15, 24.25)         # basamak kutusu: ayak güneyde, tepe kuzeyde
EK_Y = YB - EK_D


def zemin(ek=False):
    p = Plan("Zemin" + (" (aşama 2–3)" if ek else " (aşama 1)"), [Blok("A", T_DIS, T_IC)])
    p.oda("Mutfak", (0.0, 22.1, XM, a_f), "mutfak", etiket=(1.75, 24.6))
    p.oda("Giriş eşiği", (XM, 24.3, W, a_f), "esik", etiket=(4.55, 25.55), etiket_mod="ad")
    p.oda("WC", (XS, 22.7, W, 24.3), "islak", etiket_mod="ad", etiket=(5.65, 23.55))
    p.oda("Hol", (XM, 22.1, XS, 24.3), "dolasim", acik="G", etiket_mod="yok")
    m = p.oda("Merdiven", (XS, 19.7, W, 22.7), "merdiven", acik="B", etiket_mod="yok")
    m.yon, m.basamak, m.kesik, m.merdiven_kutu = "K", 17, 0.55, MERD
    p.oda("Oturma ve yemek", (0.0, a_b, XS, 22.1), "yasam", etiket=(2.3, 20.85))
    p.oda("Kiler\n(platform yeri)", (XS, a_b, W, 19.7), "depo", etiket=(5.65, 18.6), etiket_mod="ad")
    A = p.ac
    A("kapi", 4.15, a_f, 5.05, a_f, ic="-", h=0)
    A("pencere", 0.6, a_f, 3.0, a_f, h=1.4)
    A("kapi", XM, 22.5, XM, 23.4, ic="-", h=0)
    A("kapi", XS + 0.15, 24.3, XS + 0.85, 24.3, ic="-", h=0)
    A("kapi", XS, 18.0, XS, 18.8, ic="+", h=0)
    A("kapi2", 0.35, a_b, 2.15, a_b, ic="+", h=2.2)          # oturma → bahçe / avlucuk (camlı)
    if not ek:
        A("pencere", 2.6, a_b, 4.85, a_b, h=1.6)
    else:
        A("kapi", 2.75, a_b, 3.65, a_b, ic="-", h=0)           # oturma → arka oda geçidi
    p.mob("tezgah", 0.25, 25.4, 3.3, 0.6, ocak=(0.8, 25.45), eviye=(2.3, 25.5))
    p.mob("tezgah", 0.25, 22.35, 0.6, 2.9)
    p.mob("masa", 1.4, 23.1, 1.4, 0.85, n=4)
    p.mob("kanepe", 0.3, 18.0 if not ek else 18.9, 0.7, 2.2)
    p.mob("masa", 2.0, 20.6, 1.8, 0.9, n=6)
    p.mob("wc", W - 0.45, 23.55, yon="D")
    p.mob("dolap", XM + 0.15, 24.45, 0.4, 1.5)
    if ek:
        x0 = W - EK_W + 0.15
        p.oda("Büyükler odası", (x0, EK_Y + 0.15, W, 15.8), "yatak", etiket=(x0 + 1.95, 14.0))
        p.oda("Duş · WC\n(engelsiz)", (x0 + 1.7, 15.8, W, a_b), "islak", etiket=(x0 + 2.85, 16.65), etiket_mod="ad")
        p.oda("Geçit", (x0, 15.8, x0 + 1.7, a_b), "dolasim", etiket_mod="yok")
        A("kapi", x0 + 0.2, 15.8, x0 + 1.1, 15.8, ic="-", h=0)
        A("kapi", x0 + 1.7, 16.0, x0 + 1.7, 16.8, ic="+", h=0)
        A("pencere", x0, 12.9, x0, 15.3, h=1.5)
        A("kapi", x0 + 0.3, EK_Y + 0.15, x0 + 1.2, EK_Y + 0.15, ic="+", h=2.1)
        A("pencere", x0 + 1.6, EK_Y + 0.15, x0 + 3.3, EK_Y + 0.15, h=1.5)
        p.mob("yatak1", W - 2.3, 13.15, yon="D")
        p.mob("dolap", W - 1.85, 15.15, 1.6, 0.5)
        p.mob("dus", W - 1.15, 16.4, 1.0, 1.0)
        p.mob("wc", x0 + 2.2, 17.15, yon="K")
    return p


def ust(kat, asama3=False, teras=False):
    """1. ve 2. kat (aynı düzen). asama3: üstte merdiven var (2. kata)."""
    adlar = {1: ("Ebeveyn odası", "Çocuk odası 1", "Banyo"), 2: ("Çocuk odası 2", "Çocuk odası 3", "Banyo 2")}
    a_s, a_k, a_b_ = adlar[kat]
    p = Plan(f"{kat}. kat", [Blok("A", T_DIS, T_IC)])
    p.oda(a_s, (0.0, a_b, XM, 21.4), "yatak", etiket=(1.75, 19.75))
    p.oda(a_b_, (0.0, 21.4, XM, 23.1), "islak", etiket=(1.75, 22.25), etiket_mod="kisa")
    p.oda(a_k, (0.0, 23.1, XM, a_f), "yatak", etiket=(1.75, 24.85))
    p.oda("Hol", [(XM, 19.7, XS, 24.3), (XM, 24.3, W, a_f)], "dolasim", etiket=(4.6, 25.45), etiket_mod="ad")
    p.oda("Sükûnet nişi", (XM, a_b, XS, 19.7), "sukunet", etiket=(4.32, 18.7), etiket_mod="ad")
    p.oda("Dolap\n(platform)", (XS, a_b, W, 19.7), "depo", etiket=(5.65, 18.6), etiket_mod="ad")
    m = p.oda("Merdiven", (XS, 19.7, W, 24.3), "merdiven", acik="BK", etiket_mod="yok")
    if kat == 1:
        m.yon, m.basamak, m.merdiven_kutu = "K", 17, MERD
        m.kesik = 0.55 if asama3 else 0.0
    else:
        m.yon, m.basamak, m.kesik, m.merdiven_kutu = "K", 17, 0.0, MERD
    A = p.ac
    A("kapi", XM, 20.4, XM, 21.2, ic="-", h=0)
    A("kapi", XM, 21.6, XM, 22.35, ic="-", h=0)
    A("kapi", XM, 23.3, XM, 24.1, ic="-", h=0)
    A("pencere", 0.5, a_f, 3.1, a_f, h=1.4)
    A("pencere", 3.9, a_f, 5.9, a_f, h=1.4)
    A("pencere", 3.8, a_b, 4.85, a_b, h=1.4)
    if teras and kat == 1:
        A("kapi", 2.6, a_b, 3.5, a_b, ic="+", h=2.2)
        A("pencere", 0.4, a_b, 2.2, a_b, h=1.5)
    else:
        A("pencere", 0.6, a_b, 3.0, a_b, h=1.5)
    p.mob("yatak2" if kat == 1 else "yatak1", 0.25, 19.3 if kat == 1 else 19.9, yon="B")
    if kat == 2:
        p.mob("yatak1", 0.25, 18.0, yon="B")
    p.mob("dolap", 2.95, 17.85, 0.55, 2.0)
    p.mob("yatak1", 0.25, 24.0, yon="B")
    p.mob("calisma", 2.4, 25.4, 1.1, 0.55, yon="G")
    p.mob("dus", 0.25, 21.55, 0.9, 0.95)
    p.mob("lavabo", 1.7, 22.65)
    p.mob("wc", 3.05, 21.95, yon="D")
    p.mob("seccade", 4.32, 18.15, aci=KIBLE)
    p.mob("platform", XS + 0.2, a_b + 0.4, 0.8, 1.25)
    return p


def komsular(ax, kayit, yazi=5.6, sadece_cekirdek=False):
    """Çift çift aynalanan komşu evler (gri çizgi): batı komşu ayna, doğu komşu ayna."""
    m = []
    for x0 in (-W, W):
        ax.add_patch(C.Rectangle((x0, YB), W, YF - YB, fc="#ecebe6", ec="#b9b5ac", lw=0.5, zorder=0.6))
        if not sadece_cekirdek:   # aynalı komşunun genişlemesi kendi batı yanında
            ax.add_patch(C.Rectangle((x0, EK_Y), EK_W, EK_D, fc="#ecebe6", ec="#b9b5ac", lw=0.5, zorder=0.6))
    return m


def gunes_hesabi():
    """Oturma odasının bahçe kapısı ortası (son durum, z 1,2 m) [H].
    Engeller: kendi L genişlemesi, doğudaki aynalı komşunun genişlemesi, avlucuk çiti (1,8 m),
    güneydeki sıranın çekirdekleri (Z+2, 9,8 m) ve genişlemeleri; ada uzun ekseni D–B [V]."""
    H3, he = 3 * KAT_H + 0.5, KAT_H + 1.0
    güney_cephe = -MODEL["ORTA_BANT"] - (PD - ON - MODEL["T1_EV_DER"])      # karşı sıranın çekirdek kuzey yüzü
    kutular = [
        (W - EK_W, EK_Y, 0, W, YB, he),                          # kendi genişlemesi (doğu yanında)
        (W, EK_Y, 0, W + EK_W, YB, he),                          # doğu komşu (aynalı) genişleme
        (-W, EK_Y, 0, -W + EK_W, YB, he),                        # batı komşu (aynalı) genişleme
        (-0.05, EK_Y, 0, 0.05, YB, 1.8),                         # iki avlucuk arası çit
        (-60, güney_cephe - 9.0, 0, 60, güney_cephe, H3),        # güney sıranın çekirdekleri
        (-60, güney_cephe, 0, 60, güney_cephe + EK_D, he),       # güney sıranın genişlemeleri (yaklaşık)
    ]
    nokta = (1.25, YB - 0.01, 1.2)
    return {g: gunes_saati(nokta, 180.0, kutular, S["enlem"], GUN[g]) for g in GUN}


def kesit(fig, kayit, x_mm, y_mm):
    s0, s1, z0, z1 = -4.5, 31.5, -1.4, 11.6
    ax = C.olcekli_eksen(fig, x_mm, y_mm, (s0, s1), (z0, z1))
    m = []
    C.k_zemin(ax, kayit, s0, s1, 0.0, kalin=0.0)
    ax.add_patch(C.Rectangle((s0, z0), s1 - s0, -z0, fc=C.ton("#8d887e", 0.82), ec="none", zorder=0.5))
    H = KAT_H
    # döşemeler: zemin, 1. kat, 2. kat, çatı (aşama 3)
    C.k_dolu(ax, kayit, EK_Y, -0.3, YF, 0.0, renk=C.ton(C.DUVAR, 0.55), z=3)
    for k in (1, 2, 3):
        C.k_doseme(ax, kayit, YB, YF, k * H, DOS)
    C.k_doseme(ax, kayit, EK_Y, YB, H, DOS)
    # cepheler
    C.k_duvar(ax, kayit, YF - 0.15, T_DIS, -0.3, 3 * H + 0.9, pencereler=[(0.9, 2.3), (H + 0.9, H + 2.3), (2 * H + 0.9, 2 * H + 2.3)])
    C.k_duvar(ax, kayit, YB + 0.15, T_DIS, -0.3, 3 * H + 0.9, pencereler=[(0.0, 2.2), (H + 0.0, H + 2.2), (2 * H + 0.8, 2 * H + 2.3)])
    C.k_duvar(ax, kayit, EK_Y + 0.15, T_DIS, -0.3, H + 1.0, pencereler=[(0.0, 2.1)])
    # iç bölmeler (kesilen): yatak|banyo|yatak (x ≈ 1,75 kesiti)
    for y in (21.4, 23.1):
        C.k_duvar(ax, kayit, y, T_IC, H, 2 * H - DOS)
        C.k_duvar(ax, kayit, y, T_IC, 2 * H, 3 * H - DOS)
    C.k_duvar(ax, kayit, 22.1, T_IC, 0.0, H - DOS, pencereler=[(0.0, 2.1)])
    C.k_duvar(ax, kayit, 15.8, T_IC, 0.0, H - DOS, pencereler=[(0.0, 2.1)])
    # aşama 3 kesikli değil: tüm son durum; aşama 1 sınırı kesikli çizgi
    ax.plot([YB - 0.3, YF + 0.3], [2 * H + 0.05] * 2, color=C.TURUNCU, lw=0.9, ls=(0, (4, 2)), zorder=9)
    m.append(ax.text(YF + 0.4, 2 * H + 0.15, "aşama 1 çatısı\n(aşama 3'te döşeme)", ha="left", va="bottom", fontsize=5.6,
                     color=C.TURUNCU))
    # ortak bahçe şeridi, bahçe, sokak, karşı ev
    C.k_agac(ax, kayit, 4.5, 0.0, govde=2.6, tac=2.3)
    C.k_agac(ax, kayit, 9.5, 0.0, govde=1.6, tac=1.4)
    C.k_agac(ax, kayit, -2.0, 0.0, govde=2.6, tac=2.0)
    C.k_gorunus(ax, kayit, PD + 10.0, 0, s1, 3 * H + 0.5)
    C.k_insan(ax, 7.0, 0.0, cocuk=True)
    C.k_insan(ax, 13.1, 0.0, yasli=True)
    C.k_insan(ax, 20.9, 0.0)
    C.k_insan(ax, 20.3, H, cocuk=True)
    C.k_insan(ax, 15.8, H)
    a_ara = ogle_yuksekligi(S["enlem"], GUN["21 Aralık"])
    a_haz = ogle_yuksekligi(S["enlem"], GUN["21 Haziran"])
    a_mar = ogle_yuksekligi(S["enlem"], GUN["21 Mart"])
    _, t = C.k_gunes(ax, kayit, EK_Y, H + 1.0, a_ara, +1, 6.0, C.MAVI, f"21 Ara öğle {sayi(a_ara, 1)}°", z_min=H)
    m.append(t)
    # metinler
    for (s, z, metin) in ((22.0, 1.2, "mutfak"), (19.6, 1.2, "oturma"), (15.0, 1.9, "büyükler\nodası"),
                          (19.0, H + 1.6, "ebeveyn"), (24.7, H + 1.6, "çocuk 1"), (19.0, 2 * H + 1.6, "çocuk 2"),
                          (24.7, 2 * H + 1.6, "çocuk 3"), (14.9, H + 1.4, "teras"), (2.2, 0.45, "bahçe"),
                          (-2.3, -0.75, "ortak şerit"), (28.9, -0.75, "S2 yaşam sokağı"), (26.9, 0.45, "ön\neşik")):
        m.append(ax.text(s, z, metin, ha="center", va="center", fontsize=6.0,
                         color=C.YAZI if z > 0 else C.YAZI2))
    m += C.olcu(ax, kayit, (YF + 1.6, 0.0), (YF + 1.6, H), sayi(H, 2), ust=False)
    m += C.olcu(ax, kayit, (YF + 1.6, H), (YF + 1.6, 2 * H), sayi(H, 2), ust=False)
    m += C.olcu(ax, kayit, (YF + 1.6, 2 * H), (YF + 1.6, 3 * H), sayi(H, 2), ust=False)
    m += C.olcu(ax, kayit, (22.8, H), (22.8, 2 * H - DOS), f"iç {sayi(H - DOS, 2)}", ust=False)
    for (a, b) in ((0.0, EK_Y), (EK_Y, YB), (YB, YF), (YF, PD)):
        m += C.olcu(ax, kayit, (a, -1.1), (b, -1.1), sayi(b - a, 2), ust=True)
    m += C.plan_basligi(ax, "Kesit A–A (son durum)", s0 + 0.2, z1 - 1.0, alt="güney solda · batıya bakış · 1/100")
    m += C.olcek_cubugu(ax, kayit, 25.0, 10.6, n=5, adim=1.0, h=0.16)
    return m, (a_ara, a_haz, a_mar)


def ciz():
    z1 = zemin(ek=False)
    z2 = zemin(ek=True)
    k1 = ust(1, asama3=False, teras=False)
    k1b = ust(1, asama3=True, teras=True)
    k2 = ust(2)
    kayit = Kayit()
    fig = C.pafta()
    m = C.baslik(fig, "Tip (c) · T1 büyüyebilen sıra ev — ayrıntılı plan, üç büyüme aşaması",
                 f"Model mahalle v2.1 T1 (K2): parsel {sayi(W, 2)} × {sayi(PD, 1)} m ({sayi(W * PD, 0)} m²), ön eşik "
                 f"{sayi(ON, 1)} m, çekirdek {sayi(MODEL['T1_EV_DER'], 1)} m, kat {sayi(KAT_H, 2)} m. Referans {SEHIR_AD} "
                 f"({sayi(S['enlem'], 1)}° K). Sokak kuzeyde, bahçe güneyde (adanın kuzey sırası). "
                 "Duvar 30 cm; toprak, ahşap ya da betonarme seçeneklere açık (Rapor 16).")
    # --- vaziyet: son durum zemini, bahçe, ortak şerit ---------------------------------------
    axv = C.olcekli_eksen(fig, 14, 198, (-2.2, W + 2.2), (-4.6, PD + 3.4))
    z2v = zemin(ek=True)          # vaziyet kopyası (dış alanlar yalnız burada)
    z2v.hesapla()
    z2.hesapla()
    bahce = box(0, 0, W, YF).difference(z2v.ayak)
    z2v.dis_alanlar.append((bahce, "acik", "", None))
    z2v.dis_alanlar.append((box(-2.2, -4.0, W + 2.2, 0.0), C.ton(C.AQUA, 0.78), "ortak bahçe şeridi", (W / 2, -2.0)))
    z2v.dis_alanlar.append((box(0, YF, W, PD), C.ton("#8d887e", 0.85), "", None))
    z2v.dis_alanlar.append((box(-2.2, PD, W + 2.2, PD + 3.4), "#e6e3dc", "S2 · yaşam sokağı", (W / 2 + 0.9, PD + 2.55)))
    z2v.agaclar += [(3.2, 3.2, 2.0, "gölge ağacı"), (4.9, 8.6, 1.3, "meyve")]
    m += komsular(axv, kayit)
    m += z2v.ciz(axv, kayit, yazi=5.6)
    m += C.kesit_isareti(axv, kayit, (3.0, -3.6), (3.0, PD + 0.9), "A", yon=(-0.9, 0))
    m += C.plan_basligi(axv, "Vaziyet · zemin (son durum)", -2.0, PD + 3.45)
    m.append(axv.text(1.2, 14.9, "avlucuk", ha="center", va="center", fontsize=5.6, color=C.YAZI2, rotation=90))
    m.append(axv.text(W / 2, 10.9, f"bahçe ≈ {sayi(bahce.area, 0)} m²", ha="center", va="center", fontsize=5.8))
    m.append(axv.text(W / 2, YF + 0.5, "ön eşik 1,0 m", ha="center", va="center", fontsize=5.0, color=C.YAZI2))
    m += C.olcu(axv, kayit, (0, -4.3), (W, -4.3), f"{sayi(W, 2)}", ust=True)
    m += C.olcu(axv, kayit, (W + 1.3, 0), (W + 1.3, PD), f"{sayi(PD, 2)} (parsel)", ust=False)
    m += C.olcek_cubugu(axv, kayit, -2.0, PD + 2.3, n=5, adim=1.0, h=0.14, yazi=5.2)
    # --- aşama planları ------------------------------------------------------------------------
    ylim_u = (16.6, PD + 1.5)
    yer = [(z1, 130, 430, ylim_u, "Aşama 1 · zemin", "çekirdek Z+1 · 2+1"),
           (k1, 222, 430, ylim_u, "Aşama 1 · 1. kat", "merdiven boşluğu üstte kapalı"),
           (k2, 314, 430, ylim_u, "Aşama 3 · 2. kat", "+2 yatak, banyo; merdiven boşluğu üstte kapalı"),
           (z2, 130, 222, (11.2, PD + 1.5), "Aşama 2 · zemin", "L genişleme: büyükler odası + duş"),
           (k1b, 222, 222, (11.2, PD + 1.5), "Aşama 2–3 · 1. kat", "genişlemenin damı teras")]
    for (p, xmm, ymm, yl, ad, alt) in yer:
        ax = C.olcekli_eksen(fig, xmm, ymm, (-1.1, W + 1.2), yl)
        if p is k1b:
            p.dis_alanlar.append((box(W - EK_W, EK_Y, W, YB), "teras", "Teras\n" + sayi((EK_W - 0.3) * (EK_D - 0.15), 1) +
                                  " m²", (W - EK_W / 2, EK_Y + 2.4)))
            ax.add_patch(C.Rectangle((W - EK_W, EK_Y), EK_W, EK_D, fc="none", ec=C.DUVAR, lw=1.6, zorder=3))
        p.hesapla()
        if p is z2:
            p.dis_alanlar.append((box(0, yl[0], W, YB).difference(p.ayak), "acik", "", None))
        m += p.ciz(ax, kayit, yazi=5.6)
        if p is z2:
            ax.add_patch(C.Rectangle((W - EK_W, EK_Y), EK_W, EK_D, fc="none", ec=C.TURUNCU, lw=1.2, ls=(0, (4, 2)), zorder=9))
        m += C.plan_basligi(ax, ad, -1.0, yl[1] + 0.05)
        m.append(ax.text(-1.0, yl[1] - 0.45, alt, fontsize=5.2, color=C.YAZI2, ha="left", va="top"))
    # --- kesit ---------------------------------------------------------------------------------
    mk, (a_ara, a_haz, a_mar) = kesit(fig, kayit, 14, 48)
    m += mk
    # --- yön, lejant ----------------------------------------------------------------------------
    m += C.yon_diyagrami(fig, 325, 262, 62, S["enlem"], SEHIR_AD, KIBLE,
                         [("21 Haz", GUN["21 Haziran"], C.TURUNCU), ("21 Ara", GUN["21 Aralık"], C.MAVI)])
    lm, lh = C.lejant(fig, 412, 478, 178, ["yasam", "yatak", "mutfak", "islak", "esik", "sukunet", "depo", "dolasim",
                                           "merdiven", "acik", "teras"],
                      ek=[(C.DUVAR, "duvar (kesilen)", "duvar"), (C.MAVI, "pencere, camlı kapı", "pencere"),
                          (C.MAVI, "platform kabini 0,8 × 1,25 m", "cizgi"), (C.AQUA, "kıble yönü", "kible"),
                          (C.TURUNCU, "aşama 2 genişlemesi", "cizgi")])
    m += lm
    # --- ölçütler ve aşama tablosu ----------------------------------------------------------------
    gs = gunes_hesabi()
    asamalar = []
    for (ad, planlar, kisi) in (("Aşama 1", [("Zemin", z1), ("1. kat", k1)], 4),
                               ("Aşama 2", [("Zemin", z2), ("1. kat", k1b)], 5),
                               ("Aşama 3", [("Zemin", z2), ("1. kat", k1b), ("2. kat", k2)], 7)):
        net = sum(o.net.area for _, p in planlar for o in p.odalar if o.say and o.tur not in ("acik", "teras"))
        kat_sayi = len(planlar)
        brut = W * MODEL["T1_EV_DER"] * kat_sayi + (EK_W * EK_D if ad != "Aşama 1" else 0.0)   # parti duvarı aks ortası
        oda = sum(1 for _, p in planlar for o in p.odalar if o.tur in ("yasam", "yatak") and o.net.area >= 6)
        asamalar.append(dict(asama=ad, net=net, brut=brut, oda=oda, kisi=kisi,
                             yapim=yapim_maliyeti(brut, "III.B"), planlar=planlar))
    son = asamalar[2]
    bahce_son = bahce.area
    teras = (EK_W - 0.3) * (EK_D - 0.15)
    oz = birim_ozeti(son["planlar"], None, acik_ozel=bahce_son + teras,
                     acik_ortak=MODEL["ORTA_BANT"] / 2 * W, ic_yukseklik=KAT_H - DOS, gunes=gs,
                     arsa=W * PD,
                     ek=dict(kusak=("Çok kuşak", "zeminde eşiksiz yatak odası + engelsiz duş", "büyükler odası (aşama 2)", "✓"),
                             isil=("Isıl konfor", "kış güneşi yaşam odasına, yaz güneşi gölgede",
                                   f"Ara {sayi(gs['21 Aralık'], 1)} sa · saçak yok, ağaç gölgesi [V]", "≈"),
                             buyume_satir=("Esneklik", "statik sistem son duruma göre; +%60 kat alanı",
                                    f"{sayi(asamalar[0]['brut'], 0)} → {sayi(son['brut'], 0)} m² brüt", "✓"),
                             su=("Su", f"çatı 100 m² başına ≥ {sayi(OLCUT['yagmur_m3_100m2'])} m³ depo",
                                 "bahçede 1,5 m³ depo", "✓"),
                             deprem=("Deprem", "Z+2, perde parti duvarları, yumuşak kat yok", "Z+2 · düzenli", "✓"),
                             erisim=("Erişim", "zeminde eşiksiz oda + duş; platform yeri", "aşama 2'den itibaren", "✓"),
                             sessizlik=("Sessizlik", "yatak odası sokağa bakmaz; gece iç ≤ 30 dB (DSÖ 1999)",
                                        "çocuk 1 ve 3 S2'ye (yavaş sokak) [V]", "≈")))
    ozet = [(a["asama"], f"{a['oda']} oda · net {sayi(a['net'], 0)} m² · brüt {sayi(a['brut'], 0)} m² · "
                         f"{sayi(a['yapim'] / 1e6, 2)} mn TL") for a in asamalar]
    ozet += [("Bahçe (son durum) · teras", f"{sayi(bahce_son, 0)} m² · {sayi(teras, 1)} m²"),
             ("Ortak bahçe şeridi payı", f"{sayi(MODEL['ORTA_BANT'] / 2 * W, 1)} m²"),
             ("Net / kişi (son durum, 5 kişi)", f"{sayi(oz['net_kisi'], 1)} m²"),
             ("Model T1 (şematik) son durum", "net 176 · brüt 198 m² [H, Fıtrat Kodu §7]"),
             ("Model sabitleri", model_denetle())]
    mm_, y = sag_sutun(fig, 602, 560, 226, son["planlar"], oz, ozet, yazi=5.4, satir_h=3.25,
                       ust_baslik="Alan programı — son durum (net, m²) [H]")
    m += mm_
    gsat = [(g, f"{sayi(ogle_yuksekligi(S['enlem'], GUN[g]), 1)}°", f"{sayi(gs[g], 1)} sa") for g in GUN]
    tm, th = C.tablo_ciz(fig, 602, y - 39, 226, ["Gün", "Öğle güneş yüksekliği", "Doğrudan güneş"], gsat, [0, 60, 150],
                         baslik_metin="Güneş saati: oturmanın bahçe kapısı (z 1,2 m) [H]", yazi=5.8, satir_h=3.6,
                         hizalar=["left", "right", "right"],
                         alt_not="Engeller: kendi ve komşunun L genişlemesi, 1,8 m çit, karşı sıranın Z+2\nçekirdekleri (34,8 m güneyde) ve genişlemeleri [V].")
    m += tm
    nt, nh = C.metin_kutusu(fig, 412, 318, 178, "Tasarım notları", [
        "• Mutfak sokağa bakar (sokakta göz); oturma bahçeye. Giriş eşiğinde WC ve vestiyer.",
        "• Merdiven baştan son duruma göre: kollar üst üste, her katta hol boyunca geri dönülür.",
        "• Platform yeri (1,15 × 2,08 m) zeminde kiler, üstte dolap; gerekince kabin takılır.",
        "• Aşama 2'de genişleme yalnız doğu 3,9 m'de: oturma bahçe ışığını korur (avlucuk).",
        "• Komşular çift çift aynalanır: iki avlucuk yan yana ≈ 4,9 m genişlik kazanır.",
        "• Genişlemenin damı ebeveyn odasının terası olur; parapet 1,0 m.",
        "• Sükûnet nişi her katta güney penceresinde; seccade kıbleye (152°) döner.",
        "• Aşama 3'ün statik yükü ve deprem hesabı aşama 1'de yapılır; ruhsat tek seferde.",
    ], yazi=5.9, satir_h=3.45)
    m += nt
    asat = [(a["asama"], e, str(a["oda"]), sayi(a["net"], 0), sayi(a["brut"], 0), str(a["kisi"]),
             sayi(a["yapim"] / 1e6, 2)) for a, e in zip(asamalar, ("çekirdek Z+1", "L arka oda + teras",
                                                                    "2. kat (+2 yatak, banyo)"))]
    tm, th = C.tablo_ciz(fig, 392, 112, 196, ["Aşama", "Eklenen", "Oda", "Net m²", "Brüt m²", "Kişi", "Yapım mn TL"],
                         asat, [0, 22, 82, 100, 122, 146, 162], baslik_metin="Büyüme aşamaları [H]", yazi=5.9, satir_h=4.0,
                         hizalar=["left", "left", "right", "right", "right", "right", "right"],
                         alt_not="Brüt: parti duvarı ekseninden. Yapım: 2026 tebliği III.B × 0,92 (kâr hariç) [D/V];\n"
                                 "arsa, otopark, peyzaj ve yumuşak maliyetler hariç.")
    m += tm
    m += C.kunye(fig, 602, 14, 226, "K-c")
    sorun, dxf = C.kaydet(fig, kayit, AD)
    oz.update(dict(tip="c", ad="T1 büyüyebilen sıra ev", sehir=SEHIR_AD, brut=son["brut"], sinif="III.B",
                   parsel=W * PD, kat="Z+1 → Z+2", yapim=son["yapim"], asansor=0.0, sorun=len(sorun), dxf=dxf,
                   yari=0.0, arsa_hane=W * PD + MODEL["ORTA_BANT"] / 2 * W, hane_sayisi=1,
                   buyume=son["brut"] - asamalar[0]["brut"], asamalar=[{k: v for k, v in a.items() if k != "planlar"}
                                                                       for a in asamalar],
                   bahce=bahce_son, teras_m2=teras,
                   esneklik="3 aşama: 2+1 → 4+1 + büyükler odası; platform yeri", mahremiyet="eşik; misafir için oturma (ayrı oda yok)"))
    satirlar = []
    for a in asamalar:
        satirlar += csv_satirlari(f"c ({a['asama']})", a["planlar"])
    return oz, satirlar


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    oz, _ = ciz()
    for k, v in oz.items():
        print(k, v)
