"""
Referans — tipik 3+1 apartman dairesi (karşılaştırma ölçütü; İstanbul, 41,0° K)
================================================================================
Rapor 15 §5'teki karşılaştırmanın "bugünkü" tarafı. Plan temsilîdir [V]: ayrık nizam,
Z+7 (bodrum otopark + zemin + 7 kat), katta dört daire, ortada merdiven ve iki asansör
(PAİY md. 34/4: 20'den çok bağımsız bölüm → en az 2 asansör [D]). Daire güneydoğu köşesinde:
salon, mutfak ve bir yatak odası güneye, iki yatak odası doğuya bakar; kuzey ve batı yüzleri
çekirdeğe ve komşu dairelere yaslanır. Islak hacimler şafttan havalanır.

Bloklar arası 20 m: 5 m ön bahçe + 10 m yol + 5 m ön bahçe (PAİY md. 23 varsayılanı [D]).
Güneş saati salonun güney penceresinde, katlara göre hesaplanır [H].
Koordinat: x doğuya, y kuzeye; köken dairenin GB aks köşesi.
"""

from __future__ import annotations

import math

from shapely.geometry import box

import cizim as C
from cizim import Blok, Kayit, Plan
from degerlendirme import birim_ozeti, csv_satirlari, sag_sutun
from veri import (ASANSOR_EK_DURAK_TL, ASANSOR_TL, BIRIM_MALIYET, GUN, KAR_HARIC, OLCUT, PAIY, SEHIR, gunes_saati,
                  kible, ogle_yuksekligi, sayi, yapim_maliyeti)

AD = "referans_3+1_daire"
SEHIR_AD = "İstanbul"
S = SEHIR[SEHIR_AD]
KIBLE = kible(S["enlem"], S["boylam"])
T_DIS, T_IC = 0.30, 0.15
KAT_H = 2.90                 # döşemeden döşemeye; yükseklik sınırında kat sayısını artırmak için sık seçilen değer [V]
DOS = 0.30
SUBASMAN = 1.0               # [V]
KAT_SAYISI = 8               # zemin + 7 [V]
DAIRE_KAT = 4                # [V]
BB = KAT_SAYISI * DAIRE_KAT  # 32
BLOK = (-12.2, -0.15, 11.75, 21.0)        # blok dış yüzleri (dört daire + çekirdek) [V]
ARA = 20.0                   # karşı bloğun cephesine uzaklık: 5 + 10 + 5 m [V]
CATI_Z = SUBASMAN + KAT_SAYISI * KAT_H + 1.0   # parapet dahil
CEKIRDEK_PAY = 9.5           # daire başına ortak alan: kat holü, merdiven, asansör, giriş holü (m²) [V]
TAKS = 0.40                  # [V]
REF_KAT = 2                  # karşılaştırmada kullanılan kat (zemin = 0) [V]
BALKON = (0.3, -1.4, 4.5, 0.0)


def plan():
    p = Plan("Normal kat", [Blok("A", T_DIS, T_IC), Blok("BK", 0.12, 0.12)])
    p.oda("Salon", [(0.0, 0.0, 4.8, 5.6), (0.0, 5.6, 2.4, 8.4)], "yasam", etiket=(2.4, 3.0))
    p.oda("Mutfak", (4.8, 0.0, 8.4, 2.8), "mutfak", etiket=(6.6, 1.65))
    p.oda("Hol", [(4.8, 2.8, 8.4, 6.8), (7.0, 6.8, 8.4, 8.4)], "dolasim", etiket=(6.4, 4.9), etiket_mod="ad")
    p.oda("Yatak odası 2", (8.4, 0.0, 11.6, 3.8), "yatak", etiket=(10.0, 2.0))
    p.oda("Yatak odası 3", (8.4, 3.8, 11.6, 7.0), "yatak", etiket=(10.0, 5.2))
    p.oda("Ebeveyn odası", (8.4, 7.0, 11.6, 10.4), "yatak", etiket=(10.05, 8.25))
    p.oda("Ebeveyn\nbanyosu", (7.0, 8.4, 8.4, 10.4), "islak", etiket=(7.7, 9.75), etiket_mod="ad")
    p.oda("Banyo", (4.8, 6.8, 7.0, 8.8), "islak", etiket=(5.95, 8.15), etiket_mod="kisa")
    p.oda("Vestiyer", (4.8, 8.8, 7.0, 10.4), "depo", etiket=(5.9, 9.65), etiket_mod="kisa")
    p.oda("Antre", (2.4, 5.6, 4.8, 10.4), "esik", etiket=(3.6, 8.3), etiket_mod="kisa")
    p.oda("WC ·\nçamaşır", (0.0, 8.4, 2.4, 10.4), "islak", etiket=(1.2, 9.6), etiket_mod="ad")
    p.oda("Balkon", BALKON, "teras", blok="BK", etiket=(2.4, -0.75), etiket_mod="kisa")
    A = p.ac
    A("kapi", 3.0, 10.4, 4.0, 10.4, ic="-", h=0)                 # daire kapısı (kat holünden)
    A("bosluk", 4.8, 5.75, 4.8, 6.65)                            # antre → hol
    A("kapi2", 2.4, 6.0, 2.4, 7.4, ic="-", h=0)                  # antre → salon
    A("kapi", 2.4, 8.8, 2.4, 9.6, ic="-", h=0)                   # WC
    A("kapi", 4.8, 9.1, 4.8, 9.9, ic="+", h=0)                   # vestiyer
    A("kapi", 5.6, 2.8, 6.5, 2.8, ic="-", h=0)                   # mutfak
    A("kapi", 5.3, 6.8, 6.1, 6.8, ic="+", h=0)                   # banyo
    A("kapi", 8.4, 2.95, 8.4, 3.7, ic="+", h=0)                  # yatak 2
    A("kapi", 8.4, 4.3, 8.4, 5.2, ic="+", h=0)                   # yatak 3
    A("kapi", 8.4, 7.3, 8.4, 8.2, ic="+", h=0, mentese="0")      # ebeveyn
    A("kapi", 8.4, 8.9, 8.4, 9.6, ic="-", h=0)                   # ebeveyn banyosu
    A("surgulu", 0.6, 0.0, 2.6, 0.0, h=2.2)                      # salon → balkon
    A("pencere", 3.0, 0.0, 4.4, 0.0, h=1.5)
    A("pencere", 5.6, 0.0, 7.6, 0.0, h=1.2)                      # mutfak
    A("pencere", 9.2, 0.0, 10.8, 0.0, h=1.5)                     # yatak 2
    A("pencere", 11.6, 4.6, 11.6, 6.0, h=1.5)                    # yatak 3
    A("pencere", 11.6, 8.0, 11.6, 9.6, h=1.5)                    # ebeveyn
    p.bacalar += [(6.6, 8.45), (1.85, 8.85), (7.7, 8.85)]
    M = p.mob
    M("kanepe", 0.25, 2.2, 0.8, 2.4)
    M("kanepe", 1.5, 4.6, 2.2, 0.75)
    M("masa", 0.6, 6.2, 1.2, 1.6, n=6)
    M("dolap", 3.6, 0.2, 1.0, 0.45)
    M("tezgah", 4.95, 0.2, 3.3, 0.6, ocak=(5.2, 0.25), eviye=(6.6, 0.3))
    M("tezgah", 7.6, 0.8, 0.6, 1.8)
    M("masa", 5.3, 1.3, 1.1, 0.7, n=4)
    M("yatak1", 10.65, 0.25, yon="G")
    M("dolap", 8.6, 2.6, 1.6, 0.6)
    M("calisma", 9.0, 0.2, 1.1, 0.55, yon="K")
    M("yatak1", 10.65, 4.0, yon="D")
    M("yatak1", 8.95, 5.9, yon="B")
    M("dolap", 8.6, 3.95, 0.6, 1.5)
    M("yatak2", 9.6, 8.2, yon="D")
    M("dolap", 8.6, 9.6, 1.6, 0.6)
    M("dus", 4.95, 6.95, 0.9, 0.9)
    M("wc", 6.6, 7.6, yon="D")
    M("lavabo", 6.5, 8.35)
    M("wc", 7.7, 10.05, yon="K")
    M("dus", 7.15, 8.55, 0.8, 0.8)
    M("wc", 0.45, 10.0, yon="K")
    M("camasir", 0.15, 8.55)
    M("dolap", 4.95, 9.0, 1.9, 0.5)
    M("dolap", 2.55, 9.6, 0.5, 0.65)
    return p


def gunes_kat(kat):
    """Salonun güney penceresi (x 3,7; z = kat + 1,2 m) [H]. Engeller: üst katın balkon döşemesi,
    20 m güneydeki Z+7 blok sırası, yan bloklar (10 m ara) [V]."""
    zf = SUBASMAN + kat * KAT_H
    W0, W1 = BLOK[0], BLOK[2]
    kutular = [
        (W0, -ARA - 21.15, 0, W1, -ARA - 0.15 + 0.0, CATI_Z),             # karşı blok
        (W1 + 10.0, -ARA - 21.15, 0, W1 + 10.0 + 23.95, -ARA - 0.15, CATI_Z),
        (W0 - 10.0 - 23.95, -ARA - 21.15, 0, W0 - 10.0, -ARA - 0.15, CATI_Z),
        (W1 + 10.0, BLOK[1], 0, W1 + 10.0 + 23.95, BLOK[3], CATI_Z),       # doğu yan blok
        (W0 - 10.0 - 23.95, BLOK[1], 0, W0 - 10.0, BLOK[3], CATI_Z),       # batı yan blok
    ]
    if kat < KAT_SAYISI - 1:
        zb = zf + KAT_H
        kutular.append((BALKON[0], BALKON[1], zb - DOS, BALKON[2], -0.15, zb))   # üst balkon döşemesi
    nokta = (3.7, -0.16, zf + 1.2)
    return {g: gunes_saati(nokta, 180.0, kutular, S["enlem"], GUN[g]) for g in GUN}


def blok_kesiti(fig, kayit, x_mm, y_mm):
    """1/200 kesit: karşı blok, yol, bizim blok; öğle güneş ışınları."""
    s0, s1, z0, z1 = -27.0, 23.0, -4.0, 30.0
    ax = C.olcekli_eksen(fig, x_mm, y_mm, (s0, s1), (z0, z1), olcek=200)
    m = []
    ax.add_patch(C.Rectangle((s0, z0), s1 - s0, -z0, fc=C.ton("#8d887e", 0.82), ec="none", zorder=0.5))
    ax.plot([s0, s1], [0, 0], color=C.DUVAR, lw=0.7, zorder=2)
    y_k = -ARA - 0.15                                    # karşı blok kuzey yüzü
    for (a, b, etiket) in ((s0, y_k, "karşı blok (Z+7)"), (BLOK[1], BLOK[3], "")):
        ax.add_patch(C.Rectangle((a, -3.0), b - a, CATI_Z + 3.0, fc=C.ton(C.SARI, 0.92), ec=C.DUVAR, lw=0.7,
                                 zorder=2))
        for k in range(KAT_SAYISI + 1):
            z = SUBASMAN + k * KAT_H
            ax.plot([a, b], [z, z], color=C.DUVAR, lw=0.9 if k in (0, KAT_SAYISI) else 0.5, zorder=3)
        ax.plot([a, b], [0, 0], color=C.DUVAR, lw=0.5, zorder=3)
        if etiket:
            m.append(ax.text((a + b) / 2, SUBASMAN + 4.5 * KAT_H, etiket, ha="center", va="center", fontsize=5.6,
                             color=C.YAZI2, rotation=90, zorder=4))
    # bodrum otopark
    ax.add_patch(C.Rectangle((BLOK[1] - 4.0, -3.0), BLOK[3] - BLOK[1] + 4.0, 3.0, fc=C.ton("#8d887e", 0.6),
                             ec=C.DUVAR, lw=0.5, zorder=2.5))
    m.append(ax.text(10.0, -1.5, "bodrum otopark", ha="center", va="center", fontsize=5.4, color=C.YAZI))
    # balkonlar (güney cephesi)
    for k in range(1, KAT_SAYISI):
        z = SUBASMAN + k * KAT_H
        ax.add_patch(C.Rectangle((-1.55, z - 0.2), 1.4, 0.2, fc=C.DUVAR, ec="none", zorder=3))
        ax.plot([-1.55, -1.55], [z, z + 1.1], color=C.DUVAR, lw=0.6, zorder=3)
    # referans daire
    zr = SUBASMAN + REF_KAT * KAT_H
    ax.add_patch(C.Rectangle((BLOK[1], zr), 10.55, KAT_H, fc=C.ton(C.MAVI, 0.7), ec=C.MAVI, lw=0.8, zorder=3.5))
    m.append(ax.text(BLOK[1] + 5.3, zr + KAT_H / 2, "referans daire (2. kat)", ha="center", va="center", fontsize=5.6,
                     zorder=4))
    # ışınlar
    import math
    import matplotlib.patheffects as pe
    for (gun, renk, dy) in (("21 Aralık", C.MAVI, 0.0), ("21 Şubat", C.AQUA, 0.0)):
        a = ogle_yuksekligi(S["enlem"], GUN[gun])
        x_a, z_a = y_k, CATI_Z
        x_b = BLOK[1]
        z_b = z_a - (x_b - x_a) * math.tan(math.radians(a))
        ax.plot([x_a - 3.0, x_b], [z_a + 3.0 * math.tan(math.radians(a)), z_b], color=renk, lw=0.9, ls=(0, (5, 2)),
                zorder=6)
        ax.plot([x_b - 0.6, x_b + 0.6], [z_b, z_b], color=renk, lw=1.4, zorder=6)
        m.append(ax.text(x_b - 0.8, z_b + (0.3 if gun == "21 Aralık" else -0.3), f"{gun} öğle {sayi(a, 1)}°: "
                         f"{sayi(z_b, 1)} m altı gölgede", ha="right", va="bottom" if gun == "21 Aralık" else "top",
                         fontsize=5.6, color=renk, zorder=7,
                         path_effects=[pe.withStroke(linewidth=2.2, foreground=C.ZEMIN)]))
    for (a, b, t) in ((y_k, y_k + 5.0, "5"), (y_k + 5.0, y_k + 15.0, "10 (yol)"), (y_k + 15.0, BLOK[1], "5")):
        m += C.olcu(ax, kayit, (a, -3.4), (b, -3.4), t, yazi=5.4)
    m += C.olcu(ax, kayit, (BLOK[3] + 0.8, 0), (BLOK[3] + 0.8, CATI_Z), sayi(CATI_Z, 1), yazi=5.4, ust=False)
    m += C.plan_basligi(ax, "Blok kesiti (1/200)", s0 + 0.4, z1 - 1.6, yazi=8.0,
                        alt="güney solda · batıya bakış · ayrık nizam Z+7")
    m += C.olcek_cubugu(ax, kayit, 4.0, 27.2, n=5, adim=2.0, h=0.32, yazi=5.4)
    return m


def ciz():
    p = plan()
    p.hesapla()
    kayit = Kayit()
    fig = C.pafta()
    m = C.baslik(fig, "Referans · Tipik 3+1 apartman dairesi — karşılaştırma ölçütü",
                 f"Temsilî plan [V]: ayrık nizam, Z+7, katta {DAIRE_KAT} daire ({BB} bağımsız bölüm), iki asansör "
                 f"(PAİY md. 34/4 [D]), bodrum otopark. Kat {sayi(KAT_H, 2)} m, net iç {sayi(KAT_H - DOS, 2)} m "
                 f"(PAİY md. 28/4 en az {sayi(PAIY['md28_ic_yuk'], 2)} [D]). Referans {SEHIR_AD} "
                 f"({sayi(S['enlem'], 1)}° K). Daire güneydoğu köşesinde; bloklar arası 20 m.")
    ax = C.olcekli_eksen(fig, 14, 330, (-3.6, 14.6), (-4.2, 13.6))
    # bağlam: çekirdek, komşu daireler
    p.dis_alanlar.append((box(-3.6, 10.55, 5.4, 13.6), C.ton("#8d887e", 0.8),
                          "ortak çekirdek: merdiven + 2 asansör", (0.9, 12.1)))
    p.dis_alanlar.append((box(5.4, 10.55, 11.75, 13.6), "#ecebe6", "komşu daire (KD)", (8.6, 12.1)))
    p.dis_alanlar.append((box(-3.6, -0.15, -0.15, 10.55), "#ecebe6", "komşu\ndaire\n(GB)", (-1.9, 5.2)))
    p.dis_alanlar.append((box(-3.6, -4.2, 14.6, -1.55), C.ton(C.AQUA, 0.86), "ön bahçe 5 m → yol (güney)",
                          (8.0, -3.25)))
    m += p.ciz(ax, kayit, yazi=6.0)
    m += p.olcu_zinciri(ax, kayit, [0.0, 4.8, 8.4, 11.6], -2.15, yatay=True, ust=False)
    m += p.olcu_zinciri(ax, kayit, [0.0, 3.8, 7.0, 10.4], 12.9, yatay=False, ust=False)
    m += C.olcek_cubugu(ax, kayit, 9.2, 13.0, n=5, adim=1.0, h=0.16)
    m += C.plan_basligi(ax, "Normal kat planı · 1/100", -3.4, 13.65)
    m.append(ax.text(12.5, 1.9, "doğu\ncephesi", ha="center", va="center", fontsize=5.6, color=C.YAZI2))
    # kesit 1/200
    m += blok_kesiti(fig, kayit, 14, 40)
    m += C.yon_diyagrami(fig, 222, 465, 58, S["enlem"], SEHIR_AD, KIBLE,
                         [("21 Haz", GUN["21 Haziran"], C.TURUNCU), ("21 Ara", GUN["21 Aralık"], C.MAVI)])
    lm, lh = C.lejant(fig, 222, 368, 150, ["yasam", "yatak", "mutfak", "islak", "esik", "depo", "dolasim", "teras"],
                      ek=[(C.DUVAR, "duvar (kesilen)", "duvar"), (C.MAVI, "pencere, balkon kapısı", "pencere"),
                          (C.YAZI2, "şaft (mekanik havalandırma)", "baca")])
    m += lm
    # güneş: katlara göre
    katlar = [0, 2, 4, 7]
    gk = {k: gunes_kat(k) for k in katlar}
    gs = gk[REF_KAT]
    # maliyet ve arsa
    brut_daire = p.ayak.area
    brut_daire = 11.6 * 10.4 + 0.15 * (11.6 + 10.4)                  # parti duvarı ekseninden; dış yüz cepheden [H]
    balkon_m2 = (BALKON[2] - BALKON[0]) * (BALKON[3] - BALKON[1])
    brut_bb = brut_daire + balkon_m2 + CEKIRDEK_PAY
    sinif = "III.C"
    yapim = yapim_maliyeti(brut_daire + CEKIRDEK_PAY, sinif, balkon_m2)
    asansor = 2 * (ASANSOR_TL + (KAT_SAYISI + 1 - 4) * ASANSOR_EK_DURAK_TL) / BB
    oturum = (BLOK[2] - BLOK[0]) * (BLOK[3] - BLOK[1])
    parsel = oturum / TAKS
    acik_ortak = (parsel - oturum) / BB
    oz = birim_ozeti([("Normal kat", p)], None, acik_ozel=0.0, acik_ortak=acik_ortak, ic_yukseklik=KAT_H - DOS,
                     gunes=gs, arsa=parsel / BB,
                     ek=dict(sukunet_not="yok",
                             kusak=("Çok kuşak", "zeminde eşiksiz yatak odası + banyo", "5 kişiye oda kalmıyor", "✗"),
                             buyume_satir=("Esneklik", "ruhsatla büyüme ya da bölünme payı", "yok (kat mülkiyeti)", "✗"),
                             erisim=("Erişim", "asansör ya da zeminde eşiksiz daire", "2 asansör", "✓"),
                             su=("Su", f"çatı 100 m² başına ≥ {sayi(OLCUT['yagmur_m3_100m2'])} m³ depo",
                                 "yağmur deposu yok [V]", "✗"),
                             deprem=("Deprem", "düzenli aks; TBDY 2018'e uygun proje ve denetim", "Z+7 · varsayılan [V]",
                                     "≈"),
                             sessizlik=("Sessizlik", "yatak odası sokağa bakmaz; gece iç ≤ 30 dB (DSÖ 1999)",
                                        "yatak 2 yola bakar [V]", "≈"),
                             isil=("Isıl konfor", "kış güneşi yaşam odasına, yaz güneşi gölgede",
                                   f"2. kat 21 Ara {sayi(gs['21 Aralık'], 1)} sa · zemin {sayi(gk[0]['21 Aralık'], 1)} sa",
                                   "✓" if gs["21 Aralık"] >= 3 else ("≈" if gs["21 Aralık"] >= 1.5 else "✗"))))
    ozet = [("Net kapalı alan", f"{sayi(oz['net'], 1)} m²"), ("Balkon", f"{sayi(oz['teras'], 1)} m²"),
            ("Daire brüt (dış yüz, balkon hariç)", f"{sayi(brut_daire, 1)} m²"),
            ("BB brüt (balkon + ortak pay)", f"{sayi(brut_bb, 1)} m² → Otopark Ek-1: 1 yer [D]"),
            ("Parsel (TAKS 0,40 [V]) · hane payı", f"{sayi(parsel, 0)} m² · {sayi(parsel / BB, 1)} m²"),
            ("Ortak açık alan / hane", f"{sayi(acik_ortak, 1)} m² (çoğu otopark rampası, yol) [V]"),
            ("Net / kişi (5 kişi)", f"{sayi(oz['net_kisi'], 1)} m²"),
            ("Kaba yapım (III.C, bina > 21,50 m)", f"{sayi(yapim / 1e6, 2)} mn TL"),
            ("Asansör payı (2 × 9 durak / 32 BB)", f"{sayi(asansor / 1e3, 0)} bin TL [V]")]
    mm_, y = sag_sutun(fig, 602, 560, 226, [("Normal kat", p)], oz, ozet)
    m += mm_
    gsat = [(("zemin" if k == 0 else f"{k}. kat") + (" (referans)" if k == REF_KAT else ""),
             *[f"{sayi(gk[k][g], 1)} sa" for g in ("21 Aralık", "21 Şubat", "21 Mart", "21 Haziran")]) for k in katlar]
    tm, th = C.tablo_ciz(fig, 602, y - 44, 226, ["Kat", "21 Ara", "21 Şub", "21 Mar", "21 Haz"], gsat,
                         [0, 70, 110, 150, 190], baslik_metin="Güneş saati: salonun güney penceresi (z = kat + 1,2 m) [H]",
                         yazi=5.9, satir_h=3.8, hizalar=["left", "right", "right", "right", "right"],
                         alt_not="Engeller: 20 m güneyde Z+7 blok sırası (25,2 m), yan bloklar (10 m ara),\n"
                                 "üst katın 1,4 m balkonu [V]. Doğu ve batı cepheli dairelerde durum farklıdır.")
    m += tm
    nt, nh = C.metin_kutusu(fig, 290, 150, 200, "Neden bu plan? [V]", [
        "• 3+1 = üç yatak odası + salon. Türkiye'de en yaygın daire tipi",
        "  (hanelerin %47,5'i 4 odalı konutta; TÜİK BKNA 2021 [İ]).",
        "• Salon misafire ayrılır; aile çoğu zaman mutfakta ya da bir",
        "  yatak odasında oturur: ayrı misafir bölümü yok.",
        "• Antre doğrudan hole ve salona açılır; eşik kısa.",
        "• İki cephe birbirine dik: karşıt cephe yok, çapraz hava zayıf.",
        "• Islak hacimler penceresiz, şafttan havalanır.",
        "• Bahçe mesafeleri otopark rampası ve yola gider.",
        "• Alt katlar kışın karşı bloğun gölgesinde kalır.",
    ], yazi=6.0, satir_h=3.5)
    m += nt
    zk = SUBASMAN + REF_KAT * KAT_H
    nt, nh = C.metin_kutusu(fig, 290, 70, 200, "Kesitten okunan [H]", [
        f"• Karşı blok 25,2 m, bloklar arası 20 m: sokak oranı H/W ≈ {sayi(CATI_Z / ARA, 2)}.",
        f"• 21 Aralık öğlesinde güney cephenin alt {sayi(CATI_Z - ARA * math.tan(math.radians(ogle_yuksekligi(S['enlem'], GUN['21 Aralık']))), 1)} m'si gölgede:",
        "  zemin ile 4. kat arası kışın öğle güneşi almaz.",
        f"• 2. kattaki salon 21 Şubat'ta {sayi(gs['21 Şubat'], 1)} sa güneş alır; TS EN 17037 asgarisi 1,5 sa.",
        "• Kuzeye bakan dairelerde güneş saati sıfırdır.",
    ], yazi=6.0, satir_h=3.5)
    m += nt
    m += C.kunye(fig, 602, 14, 226, "K-R")
    sorun, dxf = C.kaydet(fig, kayit, AD)
    oz.update(dict(tip="R", ad="Tipik 3+1 apartman dairesi", sehir=SEHIR_AD, brut=brut_bb, sinif=sinif,
                   parsel=parsel, kat="Z+7", yapim=yapim, asansor=asansor, sorun=len(sorun), dxf=dxf,
                   yari=balkon_m2, arsa_hane=parsel / BB, hane_sayisi=BB, buyume=0.0, otopark_yer=1.0,
                   gunes_katlar=gk, esneklik="yok; kat mülkiyetinde büyüme ya da bölünme pratikte kapalı",
                   mahremiyet="antre var; misafir bölümü yok, salon hem misafir hem aile"))
    return oz, csv_satirlari("R", [("Normal kat", p)])


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    oz, _ = ciz()
    for k, v in oz.items():
        print(k, v)
