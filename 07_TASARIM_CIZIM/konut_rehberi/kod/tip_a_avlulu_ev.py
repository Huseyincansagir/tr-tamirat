"""
Tip (a) — Avlulu tek katlı ev (sıcak-kuru iklim; referans Diyarbakır, 37,9° K)
==============================================================================
Geleneksel Diyarbakır–Urfa avlu evinin çağdaş karşılığı: sokakta kırık giriş (dehliz),
kışlık odalar avlunun kuzeyinde (güneye bakar), eyvan ve yazlık odalar güneyde (kuzeye bakar),
batıya bakan cephede servis tamponu yerine revak, damda yaz terası, avlu altında sarnıç.
Ölçüler eksen (duvar ortası) koordinatıdır; x doğuya, y kuzeye, köken parselin GB köşesi.
"""

from __future__ import annotations

from shapely.geometry import box

import cizim as C
from cizim import Blok, Kayit, Plan
from degerlendirme import birim_ozeti, csv_satirlari, sag_sutun
from veri import (GUN, OLCUT, PAIY, SEHIR, gunes_saati, kible, ogle_yuksekligi, sayi, yagmur_potansiyeli,
                  yapim_maliyeti)

AD = "tip_a_avlulu_ev"
SEHIR_AD = "Diyarbakır"
S = SEHIR[SEHIR_AD]
KIBLE = kible(S["enlem"], S["boylam"])
PW, PD = 14.4, 19.6                     # parsel (m)
T_DIS, T_IC = 0.40, 0.20
KAT_H = 3.60                            # döşemeden dam üstüne (PAİY md. 28/1-c: ≤ 3 kat binada ≤ 4,00) [V]
DAM_T = 0.45                            # toprak dam: döşeme + yalıtım + toprak [V]
PARAPET = 1.0
SACAK_Z, SACAK_D = 2.90, 0.80           # avlu cephesinde gölgelik (kuzey kanat) [V]
SARNIC_M3 = 12.0                        # [V]
X_KESIT = 10.25
Y_KESIT_B = 13.0


def zemin_plani():
    p = Plan("Zemin", [Blok("A", T_DIS, T_IC)])
    # kuzey kanat (sokak tarafı)
    p.oda("Misafir odası\n(baş oda)", (0.2, 14.4, 4.0, 19.4), "misafir")
    p.oda("Dehliz", [(4.0, 16.1, 6.8, 19.4), (5.4, 14.4, 6.8, 16.1)], "esik", etiket=(5.85, 17.25), etiket_mod="ad")
    p.oda("WC", (4.0, 14.4, 5.4, 16.1), "islak", etiket_mod="kisa", etiket=(4.7, 15.55))
    p.oda("Kışlık oturma\nve yemek", (6.8, 14.4, 11.4, 19.4), "yasam", etiket=(9.1, 17.05))
    p.oda("Mutfak", [(11.4, 14.4, 14.2, 17.6), (11.4, 17.6, 12.4, 19.4)], "mutfak", etiket=(12.75, 16.55))
    p.oda("Kiler", (12.4, 17.6, 14.2, 19.4), "depo", etiket_mod="kisa")
    # batı kanat (doğuya, revaka bakar)
    p.oda("Çocuk odası 1", (0.2, 10.8, 4.0, 14.4), "yatak", etiket=(2.6, 12.0))
    p.oda("Banyo", (0.2, 8.4, 4.0, 10.8), "islak", etiket=(2.15, 9.55))
    p.oda("Çocuk odası 2", (0.2, 4.8, 4.0, 8.4), "yatak", etiket=(2.6, 5.85))
    rv = p.oda("Revak", (4.0, 4.8, 5.5, 14.4), "yari_acik", acik="DG", yari_acik=True, etiket_mod="ad",
               etiket=(4.85, 9.6))
    # güney kanat (kuzeye, avluya bakar)
    p.oda("Serdap · kiler\n(yarı gömme, −0,90)", (0.2, 0.2, 4.0, 4.8), "depo", etiket=(2.15, 2.7))
    p.oda("Eyvan", (4.0, 0.2, 8.0, 4.8), "yasam", acik="K", yari_acik=True, etiket=(6.0, 2.05))
    p.oda("Sükûnet odası", (8.0, 0.2, 10.6, 4.8), "sukunet", etiket=(9.2, 3.55))
    p.oda("Ebeveyn odası", (10.6, 0.2, 14.2, 4.8), "yatak", etiket=(12.35, 3.35))
    # revak tek dikdörtgen; iki açık kenar (D: avlu, G: eyvan)
    # ek duvarlar: dehlizde görüş perdesi, doğuda avlu duvarı (komşu sınırı, 3,0 m)
    p.ek_duvarlar += [box(4.1, 18.0, 5.7, 18.2), box(14.0, 4.6, 14.4, 14.6)]
    for y in (5.75, 8.15, 10.55, 12.95):
        p.kolonlar.append((5.5, y, 0.32))
    # açıklıklar ----------------------------------------------------------------
    A = p.ac
    A("kapi", 4.25, 19.4, 5.15, 19.4, ic="-", h=0)                 # sokak kapısı
    A("kapi", 5.75, 14.4, 6.65, 14.4, ic="+", h=0)                 # avlu kapısı
    A("kapi", 4.0, 16.6, 4.0, 17.5, ic="-", h=0)                   # misafir
    A("kapi", 4.3, 16.1, 5.0, 16.1, ic="-", h=0)                   # WC
    A("kapi", 6.8, 17.1, 6.8, 18.0, ic="+", h=0)                   # oturma ← dehliz
    A("kapi2", 9.4, 14.4, 10.8, 14.4, ic="+", h=2.2)               # oturma → avlu (camlı)
    A("kapi", 11.4, 15.0, 11.4, 15.9, ic="+", h=0)                 # mutfak ← oturma
    A("kapi", 12.0, 14.4, 12.9, 14.4, ic="+", h=2.0)               # mutfak → avlu (camlı)
    A("kapi", 12.4, 18.0, 12.4, 18.8, ic="+", h=0)                 # kiler
    A("kapi", 4.0, 11.25, 4.0, 12.15, ic="-", h=0)                 # çocuk 1
    A("kapi", 4.0, 9.0, 4.0, 9.8, ic="-", h=0)                     # banyo
    A("kapi", 4.0, 5.4, 4.0, 6.3, ic="-", h=0)                     # çocuk 2
    A("kapi", 4.0, 3.0, 4.0, 3.9, ic="-", h=0)                     # serdap
    A("kapi", 8.0, 3.0, 8.0, 3.9, ic="+", h=0)                     # sükûnet
    A("kapi", 11.0, 4.8, 11.9, 4.8, ic="-", h=0)                   # ebeveyn
    A("pencere", 0.8, 19.4, 1.9, 19.4, h=1.3)                      # misafir: sokak, kafesli
    A("pencere", 2.6, 19.4, 3.6, 19.4, h=1.3)
    A("yuksek", 7.4, 19.4, 8.6, 19.4, h=0.6)                       # oturma: sokak, yüksek pencere
    A("yuksek", 9.6, 19.4, 10.8, 19.4, h=0.6)
    A("pencere", 7.3, 14.4, 9.0, 14.4, h=1.6)                      # oturma: avlu
    A("pencere", 13.15, 14.4, 13.95, 14.4, h=1.2)                  # mutfak
    A("pencere", 4.0, 12.5, 4.0, 13.9, h=1.5)                      # çocuk 1
    A("yuksek", 4.0, 9.95, 4.0, 10.55, h=0.6)                      # banyo
    A("pencere", 4.0, 6.75, 4.0, 8.0, h=1.5)                       # çocuk 2
    A("yuksek", 4.0, 1.0, 4.0, 2.0, h=0.5)                         # serdap ← eyvan
    A("pencere", 8.9, 4.8, 10.3, 4.8, h=1.5)                       # sükûnet
    A("pencere", 12.35, 4.8, 13.75, 4.8, h=1.5)                    # ebeveyn
    p.bacalar += [(0.95, 15.3), (11.0, 18.75), (0.95, 13.65), (0.95, 7.65), (13.45, 0.95), (10.05, 0.95),
                  (0.95, 0.95), (3.35, 8.95)]
    # mobilya -------------------------------------------------------------------
    M = p.mob
    M("sedir", 0.45, 18.45, 3.4, 0.7)
    M("sedir", 0.45, 14.95, 0.7, 3.45)
    M("sedir", 6.95, 18.45, 4.3, 0.7)
    M("masa", 7.6, 15.55, 2.0, 1.0, n=6)
    M("tezgah", 13.35, 14.65, 0.6, 2.75, ocak=(13.4, 15.2), eviye=(13.45, 16.4))
    M("dolap", 12.55, 18.85, 1.45, 0.35)
    M("yatak1", 0.45, 13.15, yon="B")
    M("yatak1", 0.45, 11.0, yon="B")
    M("dolap", 2.6, 13.75, 1.3, 0.55)
    M("dus", 0.45, 8.55, 0.9)
    M("lavabo", 2.1, 10.45)
    M("wc", 3.45, 10.65, yon="K")
    M("camasir", 1.45, 8.55)
    M("wc", 4.7, 14.55, yon="G")
    M("lavabo", 5.0, 15.75)
    M("yatak1", 0.45, 7.2, yon="B")
    M("calisma", 0.45, 4.95, 1.3, 0.6, yon="K")
    M("dolap", 3.3, 4.95, 0.6, 1.2)
    M("yatak2", 11.5, 0.45, yon="G")
    M("dolap", 13.4, 1.0, 0.55, 2.4)
    M("seccade", 9.3, 1.6, aci=KIBLE)
    M("dolap", 8.15, 0.45, 0.4, 1.6)
    M("sedir", 4.15, 0.45, 3.7, 0.7)
    M("sedir", 4.15, 1.15, 0.7, 2.2)
    M("sedir", 7.15, 1.15, 0.7, 2.2)
    M("dolap", 0.45, 0.45, 3.4, 0.45)
    # avlu ---------------------------------------------------------------------
    M("havuz", 9.0, 8.4, 1.4, 2.2)
    M("pergola", 7.0, 12.45, 4.2, 1.65)
    p.agaclar += [(7.6, 11.4, 2.0, "dut"), (11.5, 6.5, 1.4, "nar")]
    return p


def avlu_poligonu(p):
    p.hesapla()
    parsel = box(0, 0, PW, PD)
    kalan = parsel.difference(p.ayak).difference(unary(p.ek_duvarlar))
    parcalar = [g for g in getattr(kalan, "geoms", [kalan])]
    return max(parcalar, key=lambda g: g.area)


def unary(g):
    from shapely.ops import unary_union
    return unary_union(g)


def dam_plani():
    p = Plan("Dam", [Blok("A", T_DIS, 0.0)])
    p.oda("Yaz terası (damda yatma)", [(0.2, 14.4, 14.2, 19.4)], "teras", etiket=(7.6, 17.6), etiket_mod="kisa")
    p.oda("Dam (toprak örtü)", [(0.2, 0.2, 14.2, 4.8)], "teras", etiket=(10.8, 2.2), etiket_mod="kisa", say=False)
    p.oda("Dam", [(0.2, 4.8, 5.5, 14.4)], "teras", etiket=(2.55, 9.0), etiket_mod="kisa", say=False)
    p.bacalar += [(0.95, 15.3), (11.0, 18.75), (0.95, 13.65), (0.95, 7.65), (13.45, 0.95), (10.05, 0.95),
                  (0.95, 0.95), (3.35, 8.95)]
    p.ek_duvarlar += [box(14.0, 4.6, 14.4, 14.6)]
    return p


def kesit(fig, kayit, x_mm, y_mm):
    s0, s1, z0, z1 = -3.0, 27.0, -3.2, 8.0
    ax = C.olcekli_eksen(fig, x_mm, y_mm, (s0, s1), (z0, z1))
    m = []
    C.k_zemin(ax, kayit, s0, s1, 0.0, kalin=0.0)
    ax.add_patch(C.Rectangle((s0, z0), s1 - s0, -z0, fc=C.ton("#8d887e", 0.82), ec="none", zorder=0.5))
    H = KAT_H
    top = H + PARAPET
    # güney komşu (görünüş) ve sokak karşısı ev
    C.k_gorunus(ax, kayit, s0, 0, 0.0, top)
    C.k_gorunus(ax, kayit, 25.0, 0, s1, top)
    # zemin döşemeleri
    for (a, b) in ((0.0, 5.0), (14.2, 19.6), (5.0, 14.2)):
        C.k_dolu(ax, kayit, a, -0.25, b, 0.0, renk=C.ton(C.DUVAR, 0.55), z=3)
    # güney kanat (sükûnet odası): duvarlar, dam, parapet
    C.k_duvar(ax, kayit, 0.2, T_DIS, -0.25, top)
    C.k_duvar(ax, kayit, 4.8, T_DIS, -0.25, top, pencereler=[(0.9, 2.4)])
    C.k_doseme(ax, kayit, 0.0, 5.0, H, DAM_T)
    # kuzey kanat (oturma): avlu cephesi camlı kapı, sokak cephesi yüksek pencere
    C.k_duvar(ax, kayit, 14.4, T_DIS, -0.25, top, pencereler=[(0.0, 2.2)])
    C.k_duvar(ax, kayit, 19.4, T_DIS, -0.25, top, pencereler=[(2.0, 2.6)])
    C.k_doseme(ax, kayit, 14.2, 19.6, H, DAM_T)
    # avlu cephesinde gölgelik (saçak)
    C.k_dolu(ax, kayit, 14.2 - SACAK_D, SACAK_Z, 14.2, SACAK_Z + 0.12)
    # iç kapı görünüşleri
    C.k_gorunus(ax, kayit, 15.2, 0, 16.1, 2.1, ls=(0, (2, 1.5)))
    # havuz, sarnıç, pergola
    C.k_dolu(ax, kayit, 8.4, -0.45, 10.6, -0.05, renk=C.ton(C.MAVI, 0.55), z=3.5)
    ax.add_patch(C.Rectangle((10.9, -2.6), 2.8, 2.2, fc=C.ton(C.MAVI, 0.85), ec=C.MAVI, lw=0.6, ls=(0, (3, 2)), zorder=2))
    kayit.poligon(ax, box(10.9, -2.6, 13.7, -0.4), "KESIT")
    m.append(ax.text(12.3, -1.5, f"sarnıç\n≈ {sayi(SARNIC_M3)} m³", ha="center", va="center", fontsize=5.6, color=C.MAVI,
                     zorder=9))
    ax.plot([13.0, 13.0, 14.2], [-0.4, -0.1, -0.1], color=C.MAVI, lw=0.6, ls=(0, (2, 1.5)), zorder=3)
    for s in (12.45, 14.1):
        ax.plot([s, s], [0, SACAK_Z], color="#6b5a45", lw=1.0, zorder=5)
    C.k_dolu(ax, kayit, 12.3, SACAK_Z - 0.08, 14.2 - SACAK_D, SACAK_Z + 0.02, renk="#6b5a45", z=5)
    C.k_agac(ax, kayit, 11.4, 0.0, govde=2.0, tac=2.0)
    # rüzgâr bacası (sükûnet odası) ve oturma bacası (görünüş)
    C.k_dolu(ax, kayit, 0.65, H, 1.25, top + 1.0)
    C.k_gorunus(ax, kayit, 18.45, H, 19.05, top + 1.0)
    m.append(ax.text(-0.15, 3.9, "rüzgâr\nbacası", ha="right", va="center", fontsize=5.6, color=C.YAZI2))
    # insanlar
    C.k_insan(ax, 9.3, 0.0, yasli=True)
    C.k_insan(ax, 7.0, 0.0, cocuk=True)
    C.k_insan(ax, 16.9, 0.0)
    ax.add_patch(C.Rectangle((16.2, H + 0.05), 1.9, 0.35, fc=C.ton(C.MAVI, 0.7), ec=C.MAVI, lw=0.4, zorder=6))
    m.append(ax.text(17.15, H + 0.55, "yazın damda yatak", ha="center", va="bottom", fontsize=5.6, color=C.YAZI2))
    # güneş ışınları (öğle)
    a_ara = ogle_yuksekligi(S["enlem"], GUN["21 Aralık"])
    a_haz = ogle_yuksekligi(S["enlem"], GUN["21 Haziran"])
    (xe, ze), t = C.k_gunes(ax, kayit, 5.0, top, a_ara, +1, 14.0, C.MAVI,
                            f"21 Ara öğle {sayi(a_ara, 1)}°", z_min=0.0)
    m.append(t)
    (xh, zh), _ = C.k_gunes(ax, kayit, 14.2 - SACAK_D, SACAK_Z, a_haz, +1, 0.8, C.TURUNCU, None, z_min=0.0)
    import matplotlib.patheffects as pe
    m.append(ax.text(13.6, 5.05, f"21 Haz öğle {sayi(a_haz, 1)}°", ha="left", va="bottom", fontsize=5.8,
                     color=C.TURUNCU, zorder=9, path_effects=[pe.withStroke(linewidth=2.2, foreground=C.ZEMIN)]))
    # ölçüler
    m += C.olcu(ax, kayit, (20.6, 0.0), (20.6, H), sayi(H, 2), ust=False)
    m += C.olcu(ax, kayit, (20.6, H), (20.6, top), sayi(PARAPET, 2), ust=False)
    m += C.olcu(ax, kayit, (17.9, 0.0), (17.9, H - DAM_T), f"iç {sayi(H - DAM_T, 2)}", ust=False)
    for (a, b) in ((0.0, 5.0), (5.0, 14.2), (14.2, 19.6)):
        m += C.olcu(ax, kayit, (a, -2.85), (b, -2.85), sayi(b - a, 2), ust=True)
    m.append(ax.text(9.6, -0.95, "avlu", ha="center", va="center", fontsize=6.2, color=C.YAZI2))
    m.append(ax.text(2.6, 1.6, "sükûnet\nodası", ha="center", va="center", fontsize=6.2))
    m.append(ax.text(17.0, 1.5 + 0.9, "kışlık\noturma", ha="center", va="center", fontsize=6.2))
    m.append(ax.text(22.3, 0.35, "sokak", ha="center", va="bottom", fontsize=6.2, color=C.YAZI2))
    m.append(ax.text(-1.5, 2.2, "komşu", ha="center", va="center", fontsize=5.8, color=C.YAZI2))
    m.append(ax.text(5.6, 3.05, "gölgelik ve\nasma çardağı", ha="left", va="center", fontsize=5.6, color=C.YAZI2))
    m += C.plan_basligi(ax, "Kesit A–A", s0 + 0.2, z1 - 1.0, alt="güney solda · batıya bakış · 1/100")
    m += C.olcek_cubugu(ax, kayit, 21.6, 5.9, n=5, adim=1.0, h=0.16)
    return ax, m, (a_ara, a_haz)


def kesit_b(fig, kayit, x_mm, y_mm):
    """B–B: doğu-batı, y = 13,0 (çocuk odası 1, revak, avlu, avlu duvarı); kuzeye bakış."""
    s0, s1, z0, z1 = -3.0, 17.6, -1.6, 6.6
    ax = C.olcekli_eksen(fig, x_mm, y_mm, (s0, s1), (z0, z1))
    m = []
    H, top = KAT_H, KAT_H + PARAPET
    C.k_zemin(ax, kayit, s0, s1, 0.0, kalin=0.0)
    ax.add_patch(C.Rectangle((s0, z0), s1 - s0, -z0, fc=C.ton("#8d887e", 0.82), ec="none", zorder=0.5))
    C.k_gorunus(ax, kayit, s0, 0, 0.0, top)
    C.k_gorunus(ax, kayit, PW, 0, s1, top)
    # arkada (kuzey kanadın avlu cephesi) görünüş
    C.k_gorunus(ax, kayit, 5.7, 0, 14.0, top, ec="#b9b5ac")
    for (a, b, za, zb) in ((5.75, 6.65, 0, 2.1), (7.3, 9.0, 0.9, 2.5), (9.4, 10.8, 0, 2.2), (12.0, 12.9, 0, 2.0),
                           (13.15, 13.95, 1.0, 2.2)):
        C.k_gorunus(ax, kayit, a, za, b, zb, ec="#b9b5ac")
    C.k_dolu(ax, kayit, 5.7, SACAK_Z, 14.0, SACAK_Z + 0.12, renk="#b9b5ac", z=2.5)
    # döşemeler
    C.k_dolu(ax, kayit, 0.0, -0.25, 5.7, 0.0, renk=C.ton(C.DUVAR, 0.55), z=3)
    C.k_dolu(ax, kayit, 5.7, -0.25, 14.0, -0.05, renk=C.ton(C.DUVAR, 0.55), z=3)
    # batı kanat ve revak
    C.k_duvar(ax, kayit, 0.2, T_DIS, -0.25, top)
    C.k_duvar(ax, kayit, 4.0, T_IC, -0.25, H, pencereler=[(0.9, 2.4)])
    C.k_doseme(ax, kayit, 0.0, 5.7, H, DAM_T)
    C.k_dolu(ax, kayit, 5.3, H, 5.7, top)
    C.k_dolu(ax, kayit, 5.34, 0.0, 5.66, H - DAM_T)
    # avlu: pergola, ağaç, avlu duvarı
    for s in (7.0, 11.2):
        ax.plot([s, s], [0, SACAK_Z], color="#6b5a45", lw=1.0, zorder=5)
    C.k_dolu(ax, kayit, 6.9, SACAK_Z - 0.08, 11.3, SACAK_Z + 0.02, renk="#6b5a45", z=5)
    C.k_duvar(ax, kayit, 14.2, 0.4, -0.25, 3.0)
    C.k_insan(ax, 2.4, 0.0, cocuk=True)
    C.k_insan(ax, 4.8, 0.0)
    C.k_insan(ax, 10.0, 0.0, yasli=True)
    m += C.olcu(ax, kayit, (16.6, 0.0), (16.6, H), sayi(H, 2), ust=False)
    m += C.olcu(ax, kayit, (16.6, 0.0), (16.6, 3.0), "", ust=False)
    for (a, b) in ((0.0, 4.0), (4.0, 5.7), (5.7, 14.0), (14.0, PW)):
        m += C.olcu(ax, kayit, (a, -1.25), (b, -1.25), sayi(b - a, 2), ust=True)
    m.append(ax.text(2.15, 1.75, "çocuk\nodası 1", ha="center", va="center", fontsize=6.2))
    m.append(ax.text(4.9, 3.0 - 0.2, "revak", ha="center", va="center", fontsize=6.2))
    m.append(ax.text(12.4, 0.5, "avlu", ha="center", va="center", fontsize=6.2, color=C.YAZI2))
    m.append(ax.text(14.25, 3.2, "avlu duvarı 3,0 m", ha="right", va="bottom", fontsize=5.6, color=C.YAZI2))
    m.append(ax.text(9.1, SACAK_Z + 0.4, "asma çardağı (yaprak döken)", ha="center", va="bottom", fontsize=5.6,
                     color=C.YAZI2))
    m += C.plan_basligi(ax, "Kesit B–B", s0 + 0.2, z1 - 0.95, alt="kuzeye bakış · 1/100")
    return m


def gunes_hesabi():
    """Kışlık oturmanın avlu kapısı ortası (z 1,2 m) [H]."""
    top = KAT_H + PARAPET
    kutular = [
        (-30, -40, 0, 45, 0.0, top),            # güney komşular (bitişik, tek kat + parapet) [V]
        (0, 0, 0, PW, 5.0, top),                # güney kanat
        (0, 4.8, 0, 5.7, 14.4, top),            # batı kanat + revak
        (14.0, 4.6, 0, 14.4, 14.6, 3.0),        # doğu avlu duvarı
        (14.4, -40, 0, 45, 19.6, top),          # doğu komşu
        (-30, -40, 0, 0.0, 19.6, top),          # batı komşu
        (5.5, 14.2 - SACAK_D, SACAK_Z, 14.2, 14.2, SACAK_Z + 0.12),   # gölgelik
    ]
    nokta = (10.1, 14.2 - 0.01, 1.2)
    return {g: gunes_saati(nokta, 180.0, kutular, S["enlem"], GUN[g]) for g in GUN}


def avlu_golge_payi(avlu, gun, saat, agaclar=()):
    """Avlunun gölgede kalan payı [H]. Engeller dikdörtgen prizma; gölge = taban ve tepe izdüşümünün
    dışbükey zarfı. agaclar: [(x, y, r, taç merkezi yüksekliği)] — taç düz disk sayılır [V]."""
    import math
    from shapely.affinity import translate
    from shapely.geometry import Point
    from shapely.ops import unary_union
    from veri import gunes
    alt, az = gunes(S["enlem"], gun, 15.0 * (saat - 12.0))
    if alt <= 1.0:
        return None
    L = 1.0 / math.tan(math.radians(alt))
    ux, uy = -math.sin(math.radians(az)), -math.cos(math.radians(az))
    top = KAT_H + PARAPET
    kutular = [(0, 0, 0, PW, 5.0, top), (0, 4.8, 0, 5.7, 14.4, top), (0, 14.2, 0, PW, PD, top),
               (14.0, 4.6, 0, 14.4, 14.6, 3.0), (14.4, 4.6, 0, 20.0, 14.6, top),      # doğu komşu [V]
               (5.5, 14.2 - SACAK_D, SACAK_Z, 14.2, 14.2, SACAK_Z + 0.12)]
    parca = []
    for (x0, y0, z0, x1, y1, z1) in kutular:
        r = box(x0, y0, x1, y1)
        parca.append(unary_union([translate(r, ux * L * z0, uy * L * z0),
                                  translate(r, ux * L * z1, uy * L * z1)]).convex_hull)
    for (x, y, r, zc) in agaclar:
        parca.append(translate(Point(x, y).buffer(r), ux * L * zc, uy * L * zc))
    return unary_union(parca).intersection(avlu).area / avlu.area


def ciz():
    z = zemin_plani()
    d = dam_plani()
    avlu = avlu_poligonu(z)
    z.dis_alanlar.append((avlu, "acik", f"AVLU\n{sayi(avlu.area, 1)} m²", (7.3, 7.4)))
    z.dis_alanlar.append((box(-2.5, PD, PW + 2.5, PD + 3.2), "#e6e3dc", "S O K A K", (7.2, PD + 1.9)))
    d.dis_alanlar.append((avlu, "#eef6f1", "avlu boşluğu", (9.9, 9.6)))
    d.dis_alanlar.append((box(-2.5, PD, PW + 2.5, PD + 3.2), "#e6e3dc", "S O K A K", (7.2, PD + 1.9)))
    kayit = Kayit()
    fig = C.pafta()
    m = C.baslik(fig, "Tip (a) · Avlulu tek katlı ev — sıcak-kuru iklim",
                 f"Referans {SEHIR_AD} ({sayi(S['enlem'], 1)}° K; Temmuz ort. en yüksek {sayi(S['t_max'][6], 1)} °C, "
                 f"Ocak ort. en düşük {sayi(S['t_min'][0], 1)} °C, yıllık yağış {sayi(S['yagis_yil'])} mm; MGM "
                 f"{S['donem']} [D]). Parsel {sayi(PW, 1)} × {sayi(PD, 1)} m, bitişik nizam, sokak kuzeyde. "
                 "Duvar 40 cm (ısıl kütle); malzeme toprak, taş, ahşap ya da betonarme seçeneklere açık (Rapor 16).")
    # zemin planı
    ax = C.olcekli_eksen(fig, 14, 292, (-2.6, PW + 2.6), (-2.6, PD + 3.4))
    m += z.ciz(ax, kayit, yazi=6.1)
    m += C.kesit_isareti(ax, kayit, (X_KESIT, -1.6), (X_KESIT, PD + 0.2 + 2.9), "A", yon=(-0.9, 0))
    m += C.kesit_isareti(ax, kayit, (-1.5, Y_KESIT_B), (14.8, Y_KESIT_B), "B", yon=(0, 0.9))
    m += C.plan_basligi(ax, "Zemin kat planı", -2.4, PD + 3.45 - 0.05, alt=None)
    # ölçü zincirleri
    m += z.olcu_zinciri(ax, kayit, [0.0, 4.0, 8.0, 10.6, 14.4], -1.0, yatay=True, ust=False)
    m += z.olcu_zinciri(ax, kayit, [0.0, 4.8, 14.4, 19.6], -1.0, yatay=False, ust=True)
    m += C.olcu(ax, kayit, (0.0, -2.1), (PW, -2.1), f"{sayi(PW, 2)} (parsel)", ust=False)
    m += C.olcu(ax, kayit, (PW + 1.2, 0.0), (PW + 1.2, PD), f"{sayi(PD, 2)} (parsel)", ust=False)
    m += C.olcek_cubugu(ax, kayit, PW - 4.9, PD + 2.55, n=5, adim=1.0, h=0.16)
    m.append(ax.text(13.15, 8.3, "dama\nçıkış", ha="center", va="center", fontsize=5.6, color=C.YAZI2, zorder=9))
    C.merdiven_sembol(ax, kayit, (13.05, 6.0, 14.0, 10.6), yon="G", n=19)
    ax.add_patch(C.Rectangle((13.05, 6.0), 0.95, 4.6, fc="none", ec=C.YAZI2, lw=0.5, zorder=2.6))
    m.append(ax.text(6.3, 18.75, "görüş\nperdesi", ha="center", va="center", fontsize=5.0, color=C.YAZI2, zorder=9))
    # dam planı
    ax2 = C.olcekli_eksen(fig, 207, 292, (-2.6, PW + 2.6), (-2.6, PD + 3.4))
    m += d.ciz(ax2, kayit, yazi=6.1)
    C.merdiven_sembol(ax2, kayit, (13.05, 6.0, 14.0, 10.6), yon="G", n=19)
    ax2.add_patch(C.Rectangle((13.05, 6.0), 0.95, 4.6, fc="none", ec=C.YAZI2, lw=0.5, zorder=2.6))
    ax2.add_patch(C.Rectangle((13.05, 5.0), 0.95, 1.0, fc=C.ODA_RENK["dolasim"], ec=C.YAZI2, lw=0.5, zorder=2.6))
    m += C.plan_basligi(ax2, "Dam planı", -2.4, PD + 3.45 - 0.05)
    # yağmur oluğu ve sarnıç (kesikli)
    for (x0, y0, x1, y1) in ((5.9, 14.2, 13.9, 14.2), (5.9, 5.0, 13.9, 5.0), (5.7, 5.2, 5.7, 14.0)):
        ax2.plot([x0, x1], [y0, y1], color=C.MAVI, lw=1.0, ls=(0, (3, 1.5)), zorder=6)
    ax2.add_patch(C.Rectangle((10.9, 11.0), 2.8, 1.6, fc="none", ec=C.MAVI, lw=0.7, ls=(0, (3, 2)), zorder=6))
    cati = z.ayak.area
    yil = yagmur_potansiyeli(cati, SEHIR_AD)
    m.append(ax2.text(12.3, 11.8, "sarnıç\n(altta)", ha="center", va="center", fontsize=5.6, color=C.MAVI, zorder=9))
    m.append(ax2.text(9.75, 12.6, "oluk → sarnıç", ha="center", va="center", fontsize=5.6, color=C.MAVI, zorder=9))
    m.append(ax2.text(11.3, 7.5, "dama\nmerdiven", ha="center", va="center", fontsize=5.6, color=C.YAZI2, zorder=9))
    m.append(ax2.text(7.6, 16.55, "parapet 1,0 m · yazın gece serinliği", ha="center", va="center", fontsize=5.5,
                      color=C.YAZI2, zorder=9))
    m += C.olcek_cubugu(ax2, kayit, PW - 4.9, PD + 2.55, n=5, adim=1.0, h=0.16)
    # kesit
    axk, mk, (a_ara, a_haz) = kesit(fig, kayit, 14, 150)
    m += mk
    # yön diyagramı ve lejant
    m += C.yon_diyagrami(fig, 398, 470, 62, S["enlem"], SEHIR_AD, KIBLE,
                         [("21 Haz", GUN["21 Haziran"], C.TURUNCU), ("21 Ara", GUN["21 Aralık"], C.MAVI)])
    lm, lh = C.lejant(fig, 398, 382, 190, ["misafir", "yasam", "yatak", "mutfak", "islak", "esik", "sukunet", "depo",
                                           "yari_acik", "acik", "teras"],
                      ek=[(C.DUVAR, "duvar (40 cm, kesilen)", "duvar"), (C.MAVI, "pencere", "pencere"),
                          (C.MAVI, "yüksek pencere (denizlik 1,8–2,0 m)", "yuksek"), (C.AQUA, "kıble yönü", "kible"),
                          (C.YAZI2, "rüzgâr / hava bacası", "baca"), (C.AQUA, "ağaç (dut, nar)", "agac")])
    m += lm
    # güneş saatleri
    gs = gunes_hesabi()
    brut, yari = z.brut()
    hane_net = None
    # ölçütler
    oz = birim_ozeti([("Zemin", z), ("Dam", d)], None, acik_ozel=avlu.area, acik_ortak=0.0,
                     ic_yukseklik=KAT_H - DAM_T, gunes=gs, arsa=PW * PD,
                     ek=dict(erisim=("Erişim", "eşiksiz giriş; yatak ve banyo zeminde", "tek kat, avlu kotunda [V]", "✓"),
                             buyume_satir=("Esneklik", "ruhsatla büyüme ya da bölünme payı", "kanat eklemek avluyu daraltır", "≈"),
                             kusak=("Çok kuşak", "zeminde eşiksiz yatak odası + banyo", "hepsi zeminde",
                                    "✓"),
                             su=("Su", f"çatı 100 m² başına ≥ {sayi(OLCUT['yagmur_m3_100m2'])} m³ depo",
                                 f"sarnıç {sayi(SARNIC_M3)} m³ · {sayi(100 * SARNIC_M3 / cati, 1)} m³/100 m²",
                                 "✓" if SARNIC_M3 / cati * 100 >= OLCUT["yagmur_m3_100m2"] else "≈"),
                             deprem=("Deprem", "tek kat, düzenli duvar ızgarası, ağır dam hafifletilir",
                                     "tek kat · dam 0,45 m [V]", "≈"),
                             sessizlik=("Sessizlik", "yatak odası sokağa bakmaz; gece iç ≤ 30 dB (DSÖ 1999)",
                                        "yataklar avluya · sokakta yüksek pencere", "✓"),
                             isil=("Isıl konfor", "kış güneşi kışlık odaya, yaz güneşi gölgede",
                                   f"Ara öğle {sayi(a_ara, 1)}° içeri · Haz gölgelik", "✓")))
    cam_alan = cati
    ozet = [("Net kapalı alan", f"{sayi(oz['net'], 1)} m²"), ("Yarı açık (eyvan, revak)", f"{sayi(oz['yari_acik'], 1)} m²"),
            ("Avlu (özel)", f"{sayi(avlu.area, 1)} m²"), ("Yaz terası (dam)", f"{sayi(oz['teras'], 1)} m²"),
            ("Kapalı brüt (dış yüz)", f"{sayi(brut, 1)} m²"), ("Parsel · yapı oturumu",
                                                              f"{sayi(PW * PD, 0)} m² · %{sayi(100 * z.ayak.area / (PW * PD), 0)}"),
            ("Net / kişi (5 kişi)", f"{sayi(oz['net_kisi'], 1)} m²"),
            ("Yağmur suyu potansiyeli", f"{sayi(yil, 0)} m³/yıl (çatı {sayi(cati, 0)} m² × {sayi(S['yagis_yil'])} mm × 0,8)"),
            ("Kaba yapım maliyeti [V]", f"{sayi(yapim_maliyeti(brut, 'III.B', yari) / 1e6, 2)} milyon TL (III.B)")]
    mm_, y = sag_sutun(fig, 602, 560, 226, [("Zemin", z), ("Dam", d)], oz, ozet)
    m += mm_
    # kesit B–B
    m += kesit_b(fig, kayit, 14, 24)
    # güneş saatleri tablosu
    gsat = [(g, f"{sayi(ogle_yuksekligi(S['enlem'], GUN[g]), 1)}°", f"{sayi(gs[g], 1)} sa") for g in GUN]
    tm, th = C.tablo_ciz(fig, 602, y - 39, 226, ["Gün", "Öğle güneş yüksekliği", "Doğrudan güneş"], gsat,
                         [0, 60, 150], baslik_metin="Güneş saati: kışlık oturmanın avlu kapısı (z 1,2 m) [H]",
                         yazi=5.9, satir_h=3.8, hizalar=["left", "right", "right"],
                         alt_not="Engeller: kanatlar ve parapet, avlu duvarı, 0,8 m gölgelik, bitişik komşular.\n"
                                 "Asma çardağı ve ağaçlar yaprak döken sayıldı (kışın engel değil) [V].")
    m += tm
    # avlu gölgesi
    agac_yaz = [(7.6, 11.4, 2.0, 4.0), (11.5, 6.5, 1.4, 3.0)]           # dut, nar: taç merkezi [V]
    cardak = box(7.0, 12.45, 11.2, 14.1)
    golge_sat, golge_veri = [], []
    for s in (8, 10, 12, 14, 16):
        h1 = avlu_golge_payi(avlu, GUN["21 Haziran"], s)
        h2 = avlu_golge_payi(avlu, GUN["21 Haziran"], s, agac_yaz + [(9.1, 13.275, 1.6, 2.9)])
        a1 = avlu_golge_payi(avlu, GUN["21 Aralık"], s)
        golge_veri.append((s, h1, h2, a1))
        golge_sat.append((f"{s:02d}.00", "—" if h1 is None else f"%{sayi(100 * h1)}",
                          "—" if h2 is None else f"%{sayi(100 * h2)}", "—" if a1 is None else f"%{sayi(100 * a1)}"))
    tm, th2 = C.tablo_ciz(fig, 602, y - 39 - 47, 226, ["Güneş saati", "21 Haz: yapı", "21 Haz: + ağaç, çardak",
                                                    "21 Ara: yapı"], golge_sat, [0, 50, 110, 175],
                          baslik_metin="Avlunun gölgede kalan payı [H]", yazi=5.9, satir_h=3.8,
                          hizalar=["left", "right", "right", "right"],
                          alt_not="Yapı: kanatlar, parapet, avlu duvarı, gölgelik, doğu komşu (Z, 4,6 m) [V].\n"
                                  "Ağaç tacı ve çardak düz disk/levha sayıldı; yaprak döken türler kışın engel değil [V].")
    m += tm
    gk, gh = C.metin_kutusu(fig, 232, 66, 175, "Geleneksel karşılığı [İ]", [
        "Diyarbakır ve Urfa avlu evleri: oda dizileri avluya açılır, sokağa sağır.",
        "Haremlik ve selamlık ayrı avlu ya da ayrı kanat; burada misafir odası dehlizde.",
        "Eyvan avlunun güneyinde, kuzeye açık: yazın gölgeli oturma.",
        "Serdap (zerzembe): yarı gömme serin oda ve kiler.",
        "Havuz ve ağaç avluyu nemlendirir; yazın damda yatılır.",
        "Kaynak: Eldem 1984; Küçükerman 1988; bölgesel çalışmalar (Rapor 15 §3.3).",
    ], yazi=5.9, satir_h=3.5)
    m += gk
    # notlar
    nt, nh = C.metin_kutusu(fig, 398, 298, 190, "Tasarım notları", [
        "• Kırık giriş: sokak kapısından avlu görünmez (görüş perdesi 1,2 m içeride).",
        "• Misafir odası ve WC dehlize açılır; aile avlusu misafire kapalı kalır.",
        "• Kışlık odalar avlunun kuzeyinde: kış öğlesinde güneş içeri girer.",
        "• Eyvan ve yazlık odalar güneyde, kuzeye bakar; yazın gölgede kalır.",
        "• Batı kanat revakla korunur; odalar doğuya, sabah güneşine bakar.",
        "• Yan duvarlar komşu sınırında, penceresiz; odalar baca ile çift yönlü havalanır.",
        "• Dam yaz terası: gece serinliği; oluklar avlu altındaki sarnıca iner.",
        "• Sarnıç: bahçe sulama ve WC (PAİY md. 57/7-a: depo ≥ yıllık suyun %6'sı).",
    ], yazi=6.0, satir_h=3.5)
    m += nt
    m += C.kunye(fig, 602, 14, 226, "K-a")
    sorun, dxf = C.kaydet(fig, kayit, AD)
    oz.update(dict(tip="a", ad="Avlulu tek katlı ev", sehir=SEHIR_AD, brut=brut, sinif="III.B", parsel=PW * PD,
                   kat="Z", yapim=yapim_maliyeti(brut, "III.B", yari), asansor=0.0, sarnic=SARNIC_M3,
                   yagmur_yil=yil, cati=cati, avlu=avlu.area, sorun=len(sorun), dxf=dxf, yari=yari,
                   arsa_hane=PW * PD, hane_sayisi=1, buyume=0.0, avlu_golge=golge_veri,
                   esneklik="avluya ek oda (kanat) yapılabilir; tek kat", mahremiyet="dehliz + selamlık + iç avlu"))
    satirlar = csv_satirlari("a", [("Zemin", z), ("Dam", d)])
    return oz, satirlar


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    oz, _ = ciz()
    for k, v in oz.items():
        if k not in ("gunes",):
            print(k, v)
    print("güneş", oz["gunes"])
