"""
Tip (b) — Dış sofalı (hayatlı) iki katlı ev (ılıman iklim; referans Bursa, 40,2° K)
=================================================================================
Eldem'in "dış sofalı" plan tipinin çağdaş karşılığı: odalar bir sıra hâlinde kuzeyde, sofa
(camlı hayat) bütün güney cephe boyunca. Kışın sofa güneş odası, yazın geniş saçak ve açılan
kanatlarla gölgeli sundurma. Zeminde misafir odası girişe, büyükler odası bahçeye açılır;
üst kat aile katıdır (haremin çağdaş karşılığı). İkiz nizam: batı duvarı komşu sınırında.
Ölçüler eksen koordinatıdır; x doğuya, y kuzeye; köken evin GB aks köşesi.
"""

from __future__ import annotations

from shapely.geometry import box

import cizim as C
from cizim import Blok, Kayit, Plan
from degerlendirme import birim_ozeti, csv_satirlari, sag_sutun
from veri import GUN, OLCUT, SEHIR, gunes_saati, kible, ogle_yuksekligi, sayi, yagmur_potansiyeli, yapim_maliyeti

AD = "tip_b_sofali_ev"
SEHIR_AD = "Bursa"
S = SEHIR[SEHIR_AD]
KIBLE = kible(S["enlem"], S["boylam"])
T_DIS, T_IC = 0.30, 0.15
KAT_H = 3.10
DOS = 0.30
SACAK = 1.0
EGIM = 30.0
X = [0.0, 3.6, 6.2, 9.6, 13.4]
Y = [0.0, 2.6, 6.8]
# parsel: batıda komşu (ikiz), doğuda 3 m yan bahçe; kuzeyde 3 m ön bahçe, güneyde 10 m bahçe
P0X, P1X = -0.15, 13.4 + 0.15 + 3.0
P0Y, P1Y = -0.15 - 10.0, 6.8 + 0.15 + 3.0
MERDIVEN = (5.025, 1.3, 6.125, 5.7)       # merdiven basamak kutusu: tepe güneyde (y 1,3), ayak kuzeyde
X_KESIT = 8.6


def zemin_plani():
    p = Plan("Zemin", [Blok("A", T_DIS, T_IC)])
    p.oda("Zemin sofası\n(oturma ve yemek)", (0.0, 0.0, 9.6, 2.6), "yasam", etiket=(2.3, 1.3))
    p.oda("Misafir odası\n(selamlık)", [(0.0, 4.2, 3.6, 6.8), (0.0, 2.6, 2.4, 4.2)], "misafir", etiket=(1.55, 5.45))
    p.oda("WC", (2.4, 2.6, 3.6, 4.2), "islak", etiket_mod="kisa")
    p.oda("Giriş eşiği", (3.6, 5.0, 6.2, 6.8), "esik", etiket=(5.5, 6.0), etiket_mod="ad")
    g = p.oda("Geçit", (3.6, 2.6, 4.95, 5.0), "dolasim", acik="DG", etiket_mod="yok")
    m = p.oda("Merdiven", (4.95, 2.6, 6.2, 5.0), "merdiven", acik="BGK", etiket_mod="yok")
    m.yon, m.basamak, m.kesik, m.merdiven_kutu = "G", 17, 0.45, MERDIVEN
    p.oda("Mutfak", (6.2, 2.6, 9.6, 6.8), "mutfak", etiket=(7.5, 4.0))
    p.oda("Kiler", (9.6, 4.3, 11.2, 6.8), "depo", etiket_mod="kisa")
    p.oda("Duş · WC\n(engelsiz)", (11.2, 4.3, 13.4, 6.8), "islak", etiket=(12.3, 5.75))
    p.oda("Büyükler odası", (9.6, 0.0, 13.4, 4.3), "yatak", etiket=(11.5, 2.75))
    A = p.ac
    A("kapi", 3.9, 6.8, 4.8, 6.8, ic="-", h=0)               # sokak kapısı
    A("kapi", 3.75, 5.0, 4.8, 5.0, ic="-", h=2.1)             # rüzgârlık kapısı (camlı)
    A("kapi", 3.6, 5.6, 3.6, 6.5, ic="-", h=0)                # misafir
    A("kapi", 3.6, 2.85, 3.6, 3.55, ic="-", h=0)              # WC
    A("bosluk", 6.5, 2.6, 8.3, 2.6)                           # mutfak–sofa geniş geçit
    A("kapi", 9.6, 4.8, 9.6, 5.6, ic="+", h=0)                # kiler
    A("kapi", 9.6, 0.5, 9.6, 1.4, ic="+", h=0)                # büyükler
    A("kapi", 11.5, 4.3, 12.4, 4.3, ic="+", h=0)              # duş
    A("surgulu", 0.5, 0.0, 2.3, 0.0, h=2.2)                   # sofa: bahçe cephesi camlı
    A("kapi2", 2.9, 0.0, 4.3, 0.0, ic="+", h=2.2)
    A("surgulu", 6.6, 0.0, 8.9, 0.0, h=2.2)
    A("pencere", 10.2, 0.0, 11.6, 0.0, h=1.5)
    A("kapi", 12.2, 0.0, 13.1, 0.0, ic="+", h=2.1)            # büyükler: bahçeye eşiksiz
    A("pencere", 13.4, 1.6, 13.4, 3.0, h=1.5)
    A("pencere", 0.7, 6.8, 1.9, 6.8, h=1.3)                   # misafir: sokak (kafes)
    A("pencere", 6.9, 6.8, 8.9, 6.8, h=1.2)                   # mutfak: sokakta göz
    A("yuksek", 9.9, 6.8, 10.9, 6.8, h=0.5)                   # kiler
    A("yuksek", 11.6, 6.8, 12.9, 6.8, h=0.6)                  # duş
    A("pencere", 13.4, 4.9, 13.4, 6.2, h=0.7)
    p.mob("sedir", 0.2, 0.2, 0.7, 2.2)
    p.mob("masa", 6.8, 0.75, 1.8, 0.9, n=6)
    p.mob("kanepe", 1.2, 1.75, 1.9, 0.65)
    p.mob("sedir", 0.2, 6.0, 3.25, 0.65)
    p.mob("sedir", 0.2, 3.0, 0.65, 3.0)
    p.mob("tezgah", 6.4, 6.0, 3.0, 0.6, ocak=(7.0, 6.05), eviye=(8.4, 6.1))
    p.mob("tezgah", 8.85, 3.5, 0.6, 2.5)
    p.mob("dolap", 9.75, 4.45, 1.3, 0.4)
    p.mob("dus", 12.25, 5.6, 1.0, 1.0)
    p.mob("wc", 11.6, 6.6, yon="K")
    p.mob("lavabo", 11.65, 4.95)
    p.mob("yatak2", 9.85, 1.9, yon="B")
    p.mob("dolap", 12.6, 2.0, 0.6, 2.0)
    p.mob("wc", 3.0, 4.0, yon="K")
    p.mob("lavabo", 2.85, 2.95)
    return p


def ust_plani():
    p = Plan("1. kat", [Blok("A", T_DIS, T_IC)])
    p.oda("Sofa (aile oturma)", [(0.0, 0.0, 4.95, 2.6), (4.95, 0.0, 6.2, 1.3), (6.2, 0.0, 13.4, 2.6)], "yasam",
          etiket=(9.85, 1.35))
    p.oda("Köşk", (0.6, -0.8, 3.0, 0.0), "yasam", acik="K", etiket=(1.8, -0.45), etiket_mod="ad")
    p.oda("Geçit", (3.6, 2.6, 4.95, 4.8), "dolasim", acik="DG", etiket_mod="yok")
    v = p.oda("Merdiven boşluğu", (4.95, 1.3, 6.2, 4.8), "merdiven", acik="BG", etiket_mod="yok")
    v.yon, v.basamak, v.kesik, v.merdiven_kutu = "G", 17, 0.0, MERDIVEN
    p.oda("Banyo", (3.6, 4.8, 6.2, 6.8), "islak", etiket=(4.3, 5.75), etiket_mod="kisa")
    p.oda("Ebeveyn odası", (0.0, 2.6, 3.6, 6.8), "yatak", etiket=(1.8, 3.6))
    p.oda("Çocuk odası 1", (6.2, 2.6, 9.6, 6.8), "yatak", etiket=(7.9, 3.55))
    p.oda("Çocuk odası 2", (9.6, 2.6, 13.4, 6.8), "yatak", etiket=(11.5, 3.55))
    A = p.ac
    A("kapi", 1.2, 2.6, 2.1, 2.6, ic="+", h=0)
    A("kapi", 8.4, 2.6, 9.3, 2.6, ic="+", h=0)
    A("kapi", 10.0, 2.6, 10.9, 2.6, ic="+", h=0)
    A("kapi", 3.75, 4.8, 4.6, 4.8, ic="+", h=0)                # banyo
    A("surgulu", 4.2, 0.0, 4.95, 0.0, h=2.2)
    A("surgulu", 6.4, 0.0, 8.8, 0.0, h=2.2)
    A("surgulu", 9.4, 0.0, 11.6, 0.0, h=2.2)
    A("pencere", 11.9, 0.0, 13.1, 0.0, h=1.6)
    A("pencere", 0.6, -0.8, 3.0, -0.8, h=1.6)                 # köşk
    A("pencere", 13.4, 0.5, 13.4, 2.1, h=1.6)                 # sofa doğu ucu
    A("pencere", 0.8, 6.8, 2.6, 6.8, h=1.4)                   # ebeveyn
    A("yuksek", 4.0, 6.8, 5.6, 6.8, h=0.6)                    # banyo
    A("pencere", 7.0, 6.8, 8.8, 6.8, h=1.4)                   # çocuk 1
    A("pencere", 10.4, 6.8, 12.4, 6.8, h=1.4)                 # çocuk 2
    A("pencere", 13.4, 4.0, 13.4, 5.6, h=1.4)
    A("pencere", 2.5, 2.6, 3.4, 2.6, h=0.9)                   # oda–sofa iç pencereleri (gün ışığı)
    A("pencere", 6.5, 2.6, 8.1, 2.6, h=0.9)
    A("pencere", 11.2, 2.6, 13.1, 2.6, h=0.9)
    p.mob("yatak2", 0.2, 4.6, yon="B")
    p.mob("dolap", 2.9, 4.4, 0.55, 2.2)
    p.mob("yatak1", 6.4, 5.85, yon="B")
    p.mob("yatak1", 6.4, 4.75, yon="B")
    p.mob("calisma", 8.2, 6.0, 1.2, 0.55, yon="G")
    p.mob("yatak1", 12.4, 4.4, yon="K")
    p.mob("yatak1", 11.35, 4.4, yon="K")
    p.mob("dolap", 9.75, 4.5, 0.55, 2.1)
    p.mob("dus", 5.1, 5.6, 0.95, 1.05)
    p.mob("wc", 3.95, 6.55, yon="K")
    p.mob("lavabo", 4.55, 5.05)
    p.mob("sedir", 0.75, -0.65, 2.1, 0.5)
    p.mob("seccade", 1.8, 1.4, aci=KIBLE)
    p.mob("sedir", 6.4, 0.2, 2.2, 0.55)
    p.mob("kanepe", 11.8, 1.8, 1.5, 0.6)
    p.mob("dolap", 0.2, 2.05, 1.1, 0.4)
    return p


def kesit(fig, kayit, x_mm, y_mm):
    s0, s1, z0, z1 = -11.0, 13.0, -1.6, 10.6
    ax = C.olcekli_eksen(fig, x_mm, y_mm, (s0, s1), (z0, z1))
    m = []
    C.k_zemin(ax, kayit, s0, s1, 0.0, kalin=0.0)
    ax.add_patch(C.Rectangle((s0, z0), s1 - s0, -z0, fc=C.ton("#8d887e", 0.82), ec="none", zorder=0.5))
    H1, H2 = KAT_H, 2 * KAT_H
    C.k_dolu(ax, kayit, -0.15, -0.3, 6.95, 0.0, renk=C.ton(C.DUVAR, 0.55), z=3)
    # güney cephe (sofa): camlı, iki kat
    C.k_duvar(ax, kayit, 0.0, T_DIS, -0.3, H2 + 0.3, pencereler=[(0.0, 2.2), (H1, H1 + 2.2)])
    # oda–sofa iç duvarı (y 2,6): zeminde mutfak geçişi, üstte iç pencere
    C.k_duvar(ax, kayit, 2.6, T_IC, 0.0, H1 - DOS, pencereler=[(0.0, 2.3)])
    C.k_duvar(ax, kayit, 2.6, T_IC, H1, H2 - DOS, pencereler=[(H1 + 0.0, H1 + 2.1)])
    # kuzey cephe
    C.k_duvar(ax, kayit, 6.8, T_DIS, -0.3, H2 + 0.3, pencereler=[(1.0, 2.2), (H1 + 0.9, H1 + 2.3)])
    C.k_doseme(ax, kayit, -0.15, 6.95, H1, DOS)
    C.k_doseme(ax, kayit, -0.15, 6.95, H2, DOS)
    tepe = C.k_cati(ax, kayit, -0.15, 6.95, H2 + 0.3, egim=EGIM, sacak=SACAK)
    # bahçe ve ön bahçe
    C.k_agac(ax, kayit, -7.0, 0.0, govde=2.6, tac=2.4)
    C.k_agac(ax, kayit, 8.5, 0.0, govde=2.2, tac=1.3)
    C.k_gorunus(ax, kayit, 9.95, 0.0, 10.15, 1.2)
    m.append(ax.text(11.6, 0.35, "sokak", ha="center", va="bottom", fontsize=6.2, color=C.YAZI2))
    m.append(ax.text(-5.0, 0.4, "güney bahçesi (10 m)", ha="center", va="bottom", fontsize=6.2, color=C.YAZI2))
    m.append(ax.text(8.45, -0.6, "ön bahçe 3 m", ha="center", va="center", fontsize=5.8, color=C.YAZI2))
    m.append(ax.text(1.05, 1.6, "zemin\nsofası", ha="center", va="center", fontsize=6.2))
    m.append(ax.text(4.7, 1.25, "mutfak", ha="center", va="center", fontsize=6.2))
    m.append(ax.text(1.3, H1 + 1.25, "sofa", ha="center", va="center", fontsize=6.2))
    m.append(ax.text(4.7, H1 + 1.25, "çocuk\nodası 1", ha="center", va="center", fontsize=6.2))
    m.append(ax.text(3.4, H2 + 1.1, "çatı arası\n(havalandırmalı)", ha="center", va="center", fontsize=5.8,
                     color=C.YAZI2))
    C.k_insan(ax, 2.2, 0.0, yasli=True)
    C.k_insan(ax, 0.9, H1, cocuk=True)
    C.k_insan(ax, -3.0, 0.0)
    a_ara = ogle_yuksekligi(S["enlem"], GUN["21 Aralık"])
    a_haz = ogle_yuksekligi(S["enlem"], GUN["21 Haziran"])
    z_s = H2 + 0.3
    _, t = C.k_gunes(ax, kayit, -0.15 - SACAK, z_s, a_haz, +1, 1.3, C.TURUNCU, f"21 Haz öğle {sayi(a_haz, 1)}°")
    m.append(t)
    _, t = C.k_gunes(ax, kayit, -0.15 - SACAK, z_s, a_ara, +1, 8.0, C.MAVI, f"21 Ara öğle {sayi(a_ara, 1)}°",
                     z_min=H1)
    m.append(t)
    m += C.olcu(ax, kayit, (-1.6, 0.0), (-1.6, H1), sayi(H1, 2))
    m += C.olcu(ax, kayit, (-1.6, H1), (-1.6, H2), sayi(KAT_H, 2))
    m += C.olcu(ax, kayit, (5.6, 0.0), (5.6, H1 - DOS), f"iç {sayi(H1 - DOS, 2)}", ust=False)
    m += C.olcu(ax, kayit, (-0.15 - SACAK, H2 + 0.05), (-0.15, H2 + 0.05), sayi(SACAK, 2), ust=False)
    m.append(ax.text(-0.15 - SACAK - 0.2, H2 - 0.1, "saçak", ha="right", va="top", fontsize=5.8, color=C.YAZI2))
    for (a, b) in ((0.0, 2.6), (2.6, 6.8)):
        m += C.olcu(ax, kayit, (a, -1.3), (b, -1.3), sayi(b - a, 2))
    m += C.plan_basligi(ax, "Kesit A–A", s0 + 0.2, z1 - 1.0, alt="güney solda · batıya bakış · 1/100")
    m += C.olcek_cubugu(ax, kayit, 7.6, 9.4, n=5, adim=1.0, h=0.16)
    return m, (a_ara, a_haz)


def gorunus(fig, kayit, x_mm, y_mm):
    """Güney görünüşü (bahçe cephesi)."""
    import math
    ax = C.olcekli_eksen(fig, x_mm, y_mm, (-2.0, 16.0), (-0.6, 10.0))
    m = []
    H1, H2 = KAT_H, 2 * KAT_H
    zs = H2 + 0.3
    ax.plot([-2.0, 16.0], [0, 0], color=C.DUVAR, lw=0.9, zorder=2)
    C.k_gorunus(ax, kayit, -0.15, 0, 13.55, zs, ec=C.DUVAR, fc=C.ton(C.SARI, 0.93), lw=0.7, z=2)
    for (a, b, za, zb) in ((0.5, 2.3, 0, 2.2), (2.9, 4.3, 0, 2.2), (6.6, 8.9, 0, 2.2), (10.2, 11.6, 0.8, 2.3),
                           (12.2, 13.1, 0, 2.1), (4.2, 4.95, H1, H1 + 2.2), (6.4, 8.8, H1, H1 + 2.2),
                           (9.4, 11.6, H1, H1 + 2.2), (11.9, 13.1, H1 + 0.8, H1 + 2.4)):
        C.k_gorunus(ax, kayit, a, za, b, zb, ec=C.DUVAR, fc=C.ton(C.MAVI, 0.8), lw=0.5, z=3)
        ax.plot([(a + b) / 2, (a + b) / 2], [za, zb], color=C.DUVAR, lw=0.3, zorder=3.1)
    C.k_gorunus(ax, kayit, 0.45, H1 - 0.15, 3.15, zs - 0.05, ec=C.DUVAR, fc=C.ton(C.SARI, 0.85), lw=0.7, z=3.5)
    C.k_gorunus(ax, kayit, 0.6, H1 + 0.7, 3.0, H1 + 2.3, ec=C.DUVAR, fc=C.ton(C.MAVI, 0.8), lw=0.5, z=3.6)
    for x in (1.4, 2.2):
        ax.plot([x, x], [H1 + 0.7, H1 + 2.3], color=C.DUVAR, lw=0.3, zorder=3.7)
    for k in range(4):
        ax.plot([0.45 + 0.1 * k, 3.15 - 0.1 * k], [H1 - 0.15 - 0.08 * k] * 2, color=C.DUVAR, lw=0.5, zorder=3.6)
    ust = zs + (7.1 / 2 + SACAK) * math.tan(math.radians(EGIM))
    cati = [(-0.15 - SACAK, zs), (13.55 + SACAK, zs), (13.55 + SACAK - (7.1 / 2 + SACAK), ust),
            (-0.15 - SACAK + (7.1 / 2 + SACAK), ust)]
    ax.add_patch(C.MPoly(cati, closed=True, fc=C.ton(C.TURUNCU, 0.55), ec=C.DUVAR, lw=0.7, zorder=4))
    kayit.poligon(ax, C.Polygon(cati), "GORUNUS")
    ax.plot([-0.15 - SACAK, 13.55 + SACAK], [zs - 0.12] * 2, color=C.DUVAR, lw=1.2, zorder=4)
    C.k_agac(ax, kayit, 15.0, 0, govde=2.0, tac=0.9)
    C.k_insan(ax, 5.4, 0.0)
    C.k_insan(ax, 5.9, 0.0, cocuk=True)
    m.append(ax.text(1.8, H1 - 0.75, "köşk (çıkma)", ha="center", va="center", fontsize=5.8))
    m.append(ax.text(6.7, ust + 0.35, "kırma çatı 30°, saçak 1,0 m", ha="center", va="bottom", fontsize=5.8,
                     color=C.YAZI2))
    m += C.plan_basligi(ax, "Güney görünüşü (bahçe cephesi)", -1.8, 9.2, alt="1/100")
    m += C.olcu(ax, kayit, (-1.2, 0), (-1.2, zs), sayi(zs, 2))
    return m


def gunes_hesabi():
    """Üst sofanın güney camı ortası (z = 3,1 + 1,1) [H]. Güneyde 10 m bahçe, ardından komşu ev (Z+1, 7,5 m) [V]."""
    H2 = 2 * KAT_H
    kutular = [
        (-0.15 - SACAK, -0.15 - SACAK, H2 + 0.25, 13.55 + SACAK, 0.0, H2 + 0.45),   # saçak
        (-20, -10.15 - 8.0, 0, 35, -10.15, 7.5),                                   # güney komşu (bahçe arkası)
        (-17.0, -12, 0, -0.15, 7.0, 9.0),                                          # batı ikiz komşu
    ]
    nokta = (6.9, -0.16, KAT_H + 1.1)
    return {g: gunes_saati(nokta, 180.0, kutular, S["enlem"], GUN[g]) for g in GUN}


def ciz():
    z = zemin_plani()
    u = ust_plani()
    kayit = Kayit()
    fig = C.pafta()
    m = C.baslik(fig, "Tip (b) · Dış sofalı (hayatlı) iki katlı ev — ılıman iklim",
                 f"Referans {SEHIR_AD} ({sayi(S['enlem'], 1)}° K; Ağustos ort. en yüksek {sayi(S['t_max'][7], 1)} °C, "
                 f"Ocak ort. en düşük {sayi(S['t_min'][0], 1)} °C, yıllık yağış {sayi(S['yagis_yil'])} mm; MGM {S['donem']} [D]). "
                 f"Parsel {sayi(P1X - P0X, 1)} × {sayi(P1Y - P0Y, 1)} m, ikiz nizam, sokak kuzeyde. "
                 "Duvar 30 cm; toprak, ahşap (hımış) ya da betonarme seçeneklere açık (Rapor 16).")
    for p, xmm, ad in ((z, 14, "Zemin kat planı"), (u, 214, "1. kat planı (aile katı)")):
        ax = C.olcekli_eksen(fig, xmm, 405, (-2.2, 17.6), (-3.6, 10.6))
        p.hesapla()
        p.dis_alanlar.append((box(P0X, -3.6, P1X, P1Y).difference(p.ayak), "acik" if p is z else "#f3f6f3",
                              "güney bahçesi" if p is z else "", (8.0, -2.4)))
        p.dis_alanlar.append((box(-2.2, P1Y, 17.6, 10.6), "#e6e3dc", "S O K A K", (2.5, 10.2)))
        m += p.ciz(ax, kayit, yazi=6.0)
        m += C.plan_basligi(ax, ad, -2.0, 10.65)
        if p is z:
            m += C.kesit_isareti(ax, kayit, (X_KESIT, -3.2), (X_KESIT, 9.5), "A", yon=(-0.9, 0))
            m += z.olcu_zinciri(ax, kayit, X, -1.25, yatay=True, ust=False)
            m += z.olcu_zinciri(ax, kayit, Y, -1.25, yatay=False, ust=True)
            m.append(ax.text(15.1, 2.5, "yan bahçe\n3 m", ha="center", va="center", fontsize=5.8, color=C.YAZI2))
            m.append(ax.text(-1.1, 4.0, "komşu (ikiz)", ha="center", va="center", fontsize=5.8, color=C.YAZI2,
                             rotation=90))
            ax.add_patch(C.Circle((11.0, -2.3), 1.0, fc=C.ton(C.AQUA, 0.55), ec=C.ton(C.AQUA, 0.1), lw=0.5,
                                  alpha=0.75, zorder=4.5))
            m.append(ax.text(13.6, 8.2, "ön bahçe 3 m", ha="center", va="center", fontsize=5.8, color=C.YAZI2))
        else:
            m.append(ax.text(-0.9, -1.8, "çıkma\n0,9 m", ha="center", va="center", fontsize=5.6, color=C.YAZI2))
            m.append(ax.text(5.6, 3.05, "iniş", ha="center", va="center", fontsize=5.4, color=C.YAZI2, zorder=9,
                             rotation=90))
            m.append(ax.text(9.85, -1.1, "geniş saçak 1,0 m (yazın gölge)", ha="center", va="center", fontsize=5.6,
                             color=C.YAZI2))
            ax.plot([-0.15 - SACAK, 13.55 + SACAK, 13.55 + SACAK, -0.15 - SACAK, -0.15 - SACAK],
                    [-0.15 - SACAK, -0.15 - SACAK, 6.95 + SACAK, 6.95 + SACAK, -0.15 - SACAK], color=C.YAZI2, lw=0.5,
                    ls=(0, (4, 2)), zorder=5)
        m += C.olcek_cubugu(ax, kayit, 11.8, 9.25, n=5, adim=1.0, h=0.16)
    mk, (a_ara, a_haz) = kesit(fig, kayit, 14, 262)
    m += mk
    m += gorunus(fig, kayit, 14, 120)
    m += C.yon_diyagrami(fig, 272, 312, 62, S["enlem"], SEHIR_AD, KIBLE,
                         [("21 Haz", GUN["21 Haziran"], C.TURUNCU), ("21 Ara", GUN["21 Aralık"], C.MAVI)])
    lm, lh = C.lejant(fig, 215, 112, 190, ["misafir", "yasam", "yatak", "mutfak", "islak", "esik", "depo", "dolasim",
                                          "merdiven", "acik"],
                      ek=[(C.DUVAR, "duvar (kesilen)", "duvar"), (C.MAVI, "pencere, camlı kapı", "pencere"),
                          (C.MAVI, "yüksek pencere", "yuksek"), (C.AQUA, "kıble yönü", "kible")])
    m += lm
    gs = gunes_hesabi()
    brut_z, ya_z = z.brut()
    brut_u, ya_u = u.brut()
    brut = brut_z + brut_u
    bahce_alan = (P1X - P0X) * (P1Y - P0Y) - z.ayak.area
    cati = (13.7 + 2 * SACAK) * (7.1 + 2 * SACAK)
    depo = 2.0 * cati / 100.0
    oz = birim_ozeti([("Zemin", z), ("1. kat", u)], None, acik_ozel=bahce_alan, ic_yukseklik=KAT_H - DOS, gunes=gs,
                     arsa=(P1X - P0X) * (P1Y - P0Y),
                     ek=dict(erisim=("Erişim", "eşiksiz giriş; zeminde yatak + duş", "üst kat merdivenle; platform yeri yok", "≈"),
                             buyume_satir=("Esneklik", "ruhsatla büyüme ya da bölünme payı", "çatı arası; zemin ayrı daireye dönebilir", "≈"),
                             kusak=("Çok kuşak", "zeminde eşiksiz yatak odası + engelsiz duş", "büyükler odası + duş",
                                    "✓"),
                             su=("Su", f"çatı 100 m² başına ≥ {sayi(OLCUT['yagmur_m3_100m2'])} m³ depo",
                                 f"bahçede {sayi(depo, 1)} m³ depo", "✓"),
                             deprem=("Deprem", "Z+1, düzenli aks, çıkma ≤ 0,9 m, hafif çatı",
                                     "Z+1 · çıkma 0,9 m", "✓"),
                             sessizlik=("Sessizlik", "yatak odası sokağa bakmaz; gece iç ≤ 30 dB (DSÖ 1999)",
                                        "yataklar sokağa (3 m ön bahçe, S2) [V]", "≈"),
                             isil=("Isıl konfor", "kışın camlı sofa güneş toplar, yazın saçak gölgeler",
                                   f"Haz öğle 0 sa · Ara {sayi(gs['21 Aralık'], 1)} sa", "✓")))
    ozet = [("Net kapalı alan (iki kat)", f"{sayi(oz['net'], 1)} m²"), ("Bahçe (ön, yan, güney)", f"{sayi(bahce_alan, 1)} m²"),
            ("Kapalı brüt (dış yüz)", f"{sayi(brut, 1)} m² (zemin {sayi(brut_z, 0)} · 1. kat {sayi(brut_u, 0)})"),
            ("Parsel · yapı oturumu", f"{sayi((P1X - P0X) * (P1Y - P0Y), 0)} m² · %{sayi(100 * z.ayak.area / ((P1X - P0X) * (P1Y - P0Y)), 0)}"),
            ("Net / kişi (5 kişi; büyüklerle 7)", f"{sayi(oz['net_kisi'], 1)} · {sayi(oz['net'] / 7, 1)} m²"),
            ("Yağmur suyu potansiyeli", f"{sayi(yagmur_potansiyeli(cati, SEHIR_AD), 0)} m³/yıl (çatı izdüşümü {sayi(cati, 0)} m²)"),
            ("Kaba yapım maliyeti [V]", f"{sayi(yapim_maliyeti(brut, 'III.B') / 1e6, 2)} milyon TL (III.B)")]
    mm_, y = sag_sutun(fig, 602, 560, 226, [("Zemin", z), ("1. kat", u)], oz, ozet)
    m += mm_
    gsat = [(g, f"{sayi(ogle_yuksekligi(S['enlem'], GUN[g]), 1)}°", f"{sayi(gs[g], 1)} sa") for g in GUN]
    tm, th = C.tablo_ciz(fig, 602, y - 39, 226, ["Gün", "Öğle güneş yüksekliği", "Doğrudan güneş"], gsat, [0, 60, 150],
                         baslik_metin="Güneş saati: üst sofanın güney camı (z 4,2 m) [H]", yazi=5.9, satir_h=3.8,
                         hizalar=["left", "right", "right"],
                         alt_not="Engeller: 1,0 m saçak, batıda ikiz komşu, 10 m bahçenin ardında\nZ+1 komşu (7,5 m) [V].")
    m += tm
    gk, gh = C.metin_kutusu(fig, 352, 330, 125, "Geleneksel karşılığı [İ]", [
        "Eldem'in en eski tipi: dış sofa (hayat).",
        "Odalar sofaya açılır; sofa günlük yaşamın",
        "yeri, köşk baş köşedir.",
        "Safranbolu, Bursa, Kula, Birgi evleri.",
        "Zemin taşlık; üst kat aile katı.",
        "Kaynak: Eldem 1954, 1984.",
    ], yazi=5.9, satir_h=3.4)
    m += gk
    nt, nh = C.metin_kutusu(fig, 215, 190, 230, "Tasarım notları", [
        "• Giriş eşiği misafir odasına ve WC'ye açılır; aile sofasına camlı bir kapıdan geçilir.",
        "• Üst kat aile katıdır: misafir merdivene ve odalara ulaşmaz.",
        "• Her oda iki yöne bakar: kuzeyde dış pencere, güneyde sofaya iç pencere.",
        "• Sofa kışın güneş odası (21 Aralık öğlesinde güneş odaların içine kadar),",
        "  yazın saçak camı gölgeler; sofanın iki ucu açılınca çapraz hava akar.",
        "• Merdiven sofaya iner (geleneksel düzen); boşluk iki katı birleştirir.",
        "• Büyükler odası eşiksiz, bahçeye açılır; engelsiz duş ve WC odanın içinden.",
        "• Kiler kuzeyde, mutfağın yanında; sedirler ve yüklük dolaplar depolamayı taşır.",
    ], yazi=6.0, satir_h=3.5)
    m += nt
    m += C.kunye(fig, 602, 14, 226, "K-b")
    sorun, dxf = C.kaydet(fig, kayit, AD)
    oz.update(dict(tip="b", ad="Dış sofalı iki katlı ev", sehir=SEHIR_AD, brut=brut, sinif="III.B",
                   parsel=(P1X - P0X) * (P1Y - P0Y), kat="Z+1", yapim=yapim_maliyeti(brut, "III.B"), asansor=0.0,
                   sarnic=depo, cati=cati, bahce=bahce_alan, sorun=len(sorun), dxf=dxf, yari=0.0,
                   arsa_hane=(P1X - P0X) * (P1Y - P0Y), hane_sayisi=1, buyume=0.0,
                   esneklik="zemin büyükler odası ayrı daireye çevrilebilir; çatı arası", mahremiyet="eşik + selamlık; üst kat aile katı"))
    return oz, csv_satirlari("b", [("Zemin", z), ("1. kat", u)])


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    oz, _ = ciz()
    for k, v in oz.items():
        print(k, v)
