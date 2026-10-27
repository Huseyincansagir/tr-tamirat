"""
Tip (e) — Z+3 galerili blok: alt dubleks + üst dubleks, avlu tarafında galeri (İstanbul, 41,0° K)
=================================================================================================
Fıtrat Kodu §3.5'teki "avlu tarafında galeri (hayat)" ile paket P4'ün (açık galeriyle bağlı en çok
üç merdiven evine tek asansör; zeminde BB'lerin ≥ %15'i erişilebilir) ayrıntılı tipi. Bağlam: K3
mahalle merkezi, T4 çubuğu ya da T3 sokak kanadı Z+3; S2 yaşam sokağına bakan cephe [V].

Kurgu: her 7,2 m'lik modülde iki dubleks üst üste.
  · Alt dubleks (zemin + 1. kat): sokaktan eşiksiz girilir; zeminde misafir (büyükler) odası ve
    engelsiz duş; avluya 4 m'lik özel bahçe.
  · Üst dubleks (2. + 3. kat; 5 kişilik birim): 2. kattaki galeriden köprüyle girilir. Galeriye yalnız
    giriş eşiği, misafir WC'si ve misafir odası bakar (selamlık). 3. kat aile katıdır (harem): oturma,
    mutfak, ebeveyn, sükûnet odası ve güneye 1,8 m'lik loggia; önünden kimse geçmez.
  · Galeri yalnız 2. katta, cepheden 1,0 m ışık boşluğuyla ayrılır. Bir çekirdek (merdiven + asansör)
    galeri katına ve çatıya durur; galerinin iki ucunda açık kaçış merdiveni [DY].
Koordinat: x doğuya (çekirdeğin batı aksı 0), y kuzeye (güney cephe aksı 0, kuzey cephe aksı 10,4).
"""

from __future__ import annotations

import math

from shapely.geometry import box
from shapely.ops import unary_union

import cizim as C
from cizim import Blok, Kayit, Plan
from degerlendirme import birim_ozeti, csv_satirlari, olcut_satirlari, sag_sutun
from veri import (ASANSOR_TL, GUN, OLCUT, SEHIR, KAR_HARIC, BIRIM_MALIYET, YARI_ACIK_KATSAYI, gunes_saati,
                  kible, ogle_yuksekligi, sayi, yagmur_potansiyeli)

AD = "tip_e_galerili_blok"
SEHIR_AD = "İstanbul"
S = SEHIR[SEHIR_AD]
KIBLE = kible(S["enlem"], S["boylam"])

# --- ölçüler (m) [V] ------------------------------------------------------------------------------
CW, MW, D = 4.5, 7.2, 10.4          # çekirdek genişliği, modül genişliği, blok derinliği (aks)
T_DIS, T_IC = 0.30, 0.15
KAT_H, DOS = 3.10, 0.30
OX = {"A": CW, "B": CW + MW}        # modüllerin batı aksı
G_IC, G_DIS = -1.0, -2.8            # galeri iç ve dış kenarı (2. kat)
G_ALT = 2 * KAT_H - 0.25            # galeri döşemesinin alt kotu
LG = -2.1                           # 3. kat loggia dış kenarı (net derinlik 1,8 m)
SACAK = -1.15                       # çatı saçağının dış kenarı: cephe yüzünden 1,0 m; ötesi asma çardağı [V]
BAHCE = -4.0                        # alt dubleks bahçesinin avlu sınırı (çit 1,2 m)
ON_ESIK = 1.0                       # sokak tarafında ön eşik (Fıtrat Kodu K3: 0–1,5 m)
SOKAK_G = 10.0                      # S2 yaşam sokağı
KARSI_KANAT = (-15.7, 7.0)          # avlunun güney kenarındaki Z+1 kanadın yüzü ve yüksekliği [V]
PARSEL_DER = 27.4                   # T4 çubuğu parsel derinliği (model mahalle v2.1) [H/V]
N_MODUL = 9                         # bir asansörlü çekirdeğin galeriyle hizmet ettiği modül [V]
SEGMENT = CW + N_MODUL * MW         # blok kesiminin cephesi: 69,3 m
CATI_CIKIS = 4.5 * 6.6              # çatıda merdiven ve asansör çıkışı (m², kapalı) [V]
ACIK_MERDIVEN = 2 * 2.8 * 5.2 * 2   # galerinin iki ucunda açık kaçış merdiveni (Z→2), yarı açık [V]
SU_DEPO_MODUL = 3.0                 # çatıda modül başına su deposu (m³) [V]
CATI_KULLANIM = 0.60                # çatı bahçesinin kullanılabilir payı [V]
X_KESIT = OX["A"] + 5.0             # kesit A–A (merdiven ve oturma odalarından)
XLIM, YLIM = (-1.3, 20.2), (-5.3, 12.7)
BIRIM_ADLARI = {"altA": "Alt dubleks A", "ustA": "Üst dubleks A", "altB": "Alt dubleks B",
                "ustB": "Üst dubleks B", "ortak": "Ortak"}


# =============================================================================
# Yerel yardımcılar
# =============================================================================
class PlanE(Plan):
    """U merdivenli plan: motorun düz merdiven simgesi yerine iki kollu merdiven çizer."""

    def _merdiven(self, ax, o, kayit):
        if getattr(o, "u", None):
            u_merdiven(ax, kayit, *o.u)
        else:
            super()._merdiven(ax, o, kayit)


def _kesikli_kol(ax, kayit, b, yon, n):
    x0, y0, x1, y1 = b
    dikey = yon in ("K", "G")
    L = (y1 - y0) if dikey else (x1 - x0)
    for k in range(1, n):
        if dikey:
            pts = [(x0 + 0.04, y0 + k * L / n), (x1 - 0.04, y0 + k * L / n)]
        else:
            pts = [(x0 + k * L / n, y0 + 0.04), (x0 + k * L / n, y1 - 0.04)]
        ax.plot(*zip(*pts), color="#8d887e", lw=0.45, ls=(0, (2, 2)), alpha=0.6, zorder=2)
        kayit.cizgi(ax, pts, "MOBILYA")


def u_merdiven(ax, kayit, b, eksen, uc, durum, n=9):
    """İki kollu (U) merdiven. b: net kutu · eksen: kolların yönü (x/y) · uc: ara sahanlığın ucu (+/−) ·
    durum: alt (başlangıç katı), ara (ara kat), ust (son kat)."""
    bx0, by0, bx1, by1 = b
    L, gap = 1.15, 0.12
    if eksen == "x":
        land = (bx1 - L, by0, bx1, by1) if uc == "+" else (bx0, by0, bx0 + L, by1)
        f0, f1 = (bx0, bx1 - L) if uc == "+" else (bx0 + L, bx1)
        ym = (by0 + by1) / 2
        k1, k2 = (f0, by0, f1, ym - gap / 2), (f0, ym + gap / 2, f1, by1)
        y1_, y2_ = ("D", "B") if uc == "+" else ("B", "D")
        orta = [(f0, ym), (f1, ym)]
        kenar = [(land[0], by0), (land[0], by1)] if uc == "+" else [(land[2], by0), (land[2], by1)]
    else:
        land = (bx0, by1 - L, bx1, by1) if uc == "+" else (bx0, by0, bx1, by0 + L)
        f0, f1 = (by0, by1 - L) if uc == "+" else (by0 + L, by1)
        xm = (bx0 + bx1) / 2
        k1, k2 = (bx0, f0, xm - gap / 2, f1), (xm + gap / 2, f0, bx1, f1)
        y1_, y2_ = ("K", "G") if uc == "+" else ("G", "K")
        orta = [(xm, f0), (xm, f1)]
        kenar = [(bx0, land[1]), (bx1, land[1])] if uc == "+" else [(bx0, land[3]), (bx1, land[3])]
    ax.plot(*zip(*orta), color=C.YAZI2, lw=0.6, zorder=2.3)
    ax.plot(*zip(*kenar), color="#8d887e", lw=0.45, zorder=2.3)
    kayit.cizgi(ax, orta, "MOBILYA")
    kayit.cizgi(ax, kenar, "MOBILYA")
    if durum == "alt":
        C.merdiven_sembol(ax, kayit, k1, y1_, n, 0.55)
        _kesikli_kol(ax, kayit, k2, y2_, n)
    elif durum == "ara":
        C.merdiven_sembol(ax, kayit, k1, y1_, n, 0.55)
        C.merdiven_sembol(ax, kayit, k2, y2_, n)
    else:
        C.merdiven_sembol(ax, kayit, k1, y1_, n)
        C.merdiven_sembol(ax, kayit, k2, y2_, n)


def _o(r, ox):
    return (ox + r[0], r[1], ox + r[2], r[3])


def oda(p, ad, rects, tur, ox=0.0, etiket=None, **kw):
    rects = [rects] if isinstance(rects[0], (int, float)) else rects
    rr = [_o(r, ox) for r in rects]
    et = None if etiket is None else (ox + etiket[0], etiket[1])
    return p.oda(ad, rr, tur, etiket=et, **kw)


def ac(p, tur, x0, y0, x1, y1, ox=0.0, **kw):
    p.ac(tur, ox + x0, y0, ox + x1, y1, **kw)


def mob(p, tip, x, y, *a, ox=0.0, **kw):
    for k in ("ocak", "eviye"):
        if kw.get(k) is not None:
            kw[k] = (ox + kw[k][0], kw[k][1])
    p.mob(tip, ox + x, y, *a, **kw)


class Suzgec:
    """Alan programı tablosu için planın yalnız bir birime ait satırları."""

    def __init__(self, p, birim):
        self.p, self.birim = p, birim

    def tablo(self):
        return [r for r in self.p.tablo() if r["birim"] == self.birim]


# =============================================================================
# Modül planları (yerel koordinat: x 0–7,2; y 0–10,4)
# =============================================================================
U_KUTU = (3.875, 3.875, 7.05, 6.325)      # dubleks içi U merdivenin net kutusu (aks 3,8–7,2 × 3,8–6,4)


def _merdiven_oda(p, ox, blok, birim, durum):
    m = oda(p, "Merdiven", (3.8, 3.8, 7.2, 6.4), "merdiven", ox, blok=blok, birim=birim, acik="B",
            etiket_mod="yok")
    m.u = ((ox + U_KUTU[0], U_KUTU[1], ox + U_KUTU[2], U_KUTU[3]), "x", "+", durum, 9)
    return m


def _hol_islak(p, ox, blok, birim, islak_ad):
    oda(p, "Hol", (1.8, 3.8, 3.8, 6.4), "dolasim", ox, blok=blok, birim=birim, etiket=(2.8, 4.55),
        etiket_mod="ad")
    oda(p, islak_ad, (0.0, 3.8, 1.8, 6.4), "islak", ox, blok=blok, birim=birim, etiket=(0.75, 5.27),
        etiket_mod="kisa")
    ac(p, "kapi", 1.8, 4.5, 1.8, 5.3, ox, ic="-", h=0)
    mob(p, "dus", 0.2, 3.95, 0.9, 0.85, ox=ox)
    mob(p, "wc", 0.65, 6.3, yon="K", ox=ox)
    mob(p, "lavabo", 1.35, 4.2, ox=ox)
    p.bacalar.append((ox + 1.38, 6.0))


def _cocuk_odalari(p, ox, blok, birim):
    oda(p, "Çocuk odası 2", (0.0, 6.4, 2.8, 10.4), "yatak", ox, blok=blok, birim=birim, etiket=(1.8, 8.45))
    oda(p, "Çocuk odası 1\n(iki çocuk)", (2.8, 6.4, 7.2, 10.4), "yatak", ox, blok=blok, birim=birim,
        etiket=(5.0, 7.55))
    ac(p, "kapi", 1.9, 6.4, 2.7, 6.4, ox, ic="+", h=0)
    ac(p, "kapi", 2.9, 6.4, 3.7, 6.4, ox, ic="+", h=0)
    ac(p, "pencere", 0.5, D, 2.3, D, ox, h=1.4)
    ac(p, "pencere", 3.6, D, 6.6, D, ox, h=1.4)
    mob(p, "yatak1", 0.2, 7.95, yon="K", ox=ox)
    mob(p, "calisma", 1.35, 9.6, 1.2, 0.55, yon="G", ox=ox)
    mob(p, "yatak1", 4.15, 8.15, yon="K", ox=ox)
    mob(p, "yatak1", 6.05, 8.15, yon="K", ox=ox)
    mob(p, "dolap", 4.0, 6.55, 1.9, 0.55, ox=ox)


def _sukunet(p, ox, blok, birim, ad="Sükûnet odası"):
    oda(p, ad, (0.0, 0.0, 2.8, 3.8), "sukunet", ox, blok=blok, birim=birim, etiket=(1.5, 2.7))
    ac(p, "kapi", 1.9, 3.8, 2.7, 3.8, ox, ic="-", h=0)
    ac(p, "pencere", 0.5, 0.0, 2.3, 0.0, ox, h=1.5)
    mob(p, "sedir", 0.25, 0.2, 2.3, 0.5, ox=ox)
    mob(p, "seccade", 1.05, 1.45, aci=KIBLE, ox=ox)
    mob(p, "dolap", 0.2, 3.25, 1.5, 0.4, ox=ox)


def alt_zemin(p, k):
    ox, bl, br = OX[k], k, "alt" + k
    oda(p, "Giriş eşiği", [(0.0, 8.2, 2.8, 10.4), (1.4, 6.4, 2.8, 8.2)], "esik", ox, blok=bl, birim=br,
        etiket=(1.15, 9.0), etiket_mod="ad")
    oda(p, "WC", (0.0, 6.4, 1.4, 8.2), "islak", ox, blok=bl, birim=br, etiket=(0.75, 7.55), etiket_mod="kisa")
    oda(p, "Misafir odası\n(büyükler odası)", (2.8, 6.4, 7.2, 10.4), "misafir", ox, blok=bl, birim=br,
        etiket=(4.85, 8.25))
    _hol_islak(p, ox, bl, br, "Duş · WC\nengelsiz")
    _merdiven_oda(p, ox, bl, br, "alt")
    oda(p, "Mutfak", [(0.0, 0.0, 2.8, 2.0), (1.5, 2.0, 2.8, 3.8)], "mutfak", ox, blok=bl, birim=br,
        etiket=(1.45, 1.35))
    oda(p, "Kiler", (0.0, 2.0, 1.5, 3.8), "depo", ox, blok=bl, birim=br, etiket=(0.75, 3.05), etiket_mod="kisa")
    oda(p, "Oturma ve yemek", (2.8, 0.0, 7.2, 3.8), "yasam", ox, blok=bl, birim=br, etiket=(4.55, 2.55))
    # açıklıklar
    ac(p, "kapi", 0.8, D, 1.8, D, ox, ic="-", h=0)                 # sokak kapısı (eşiksiz)
    ac(p, "kapi", 1.4, 6.7, 1.4, 7.5, ox, ic="-", h=0)             # WC
    ac(p, "kapi", 2.8, 8.7, 2.8, 9.6, ox, ic="+", h=0)             # misafir ← eşik
    ac(p, "kapi", 1.9, 6.4, 2.7, 6.4, ox, ic="-", h=0)             # eşik → hol (mahremiyet kapısı)
    ac(p, "kapi", 2.9, 6.4, 3.7, 6.4, ox, ic="+", h=0)             # misafir ↔ hol (büyükler için)
    ac(p, "kapi", 1.9, 3.8, 2.7, 3.8, ox, ic="-", h=0)             # mutfak
    ac(p, "bosluk", 2.9, 3.8, 3.7, 3.8, ox)                        # oturma
    ac(p, "kapi", 1.5, 2.3, 1.5, 3.1, ox, ic="-", h=0)             # kiler
    ac(p, "pencere", 3.6, D, 6.0, D, ox, h=1.4)                    # misafir: sokakta göz
    ac(p, "pencere", 0.35, 0.0, 1.25, 0.0, ox, h=1.3)              # mutfak
    ac(p, "kapi", 1.55, 0.0, 2.45, 0.0, ox, ic="+", h=2.1)         # mutfak → bahçe (camlı)
    ac(p, "kapi2", 4.3, 0.0, 5.7, 0.0, ox, ic="+", h=2.2)          # oturma → bahçe
    ac(p, "pencere", 6.0, 0.0, 6.9, 0.0, ox, h=1.6)
    # mobilya
    mob(p, "dolap", 0.2, 8.35, 0.45, 1.5, ox=ox)
    mob(p, "wc", 0.75, 6.5, yon="G", ox=ox)
    mob(p, "lavabo", 0.75, 7.95, ox=ox)
    mob(p, "sedir", 3.75, 9.6, 3.2, 0.6, ox=ox)
    mob(p, "sedir", 6.4, 7.15, 0.6, 2.4, ox=ox)
    mob(p, "tezgah", 0.2, 0.25, 0.6, 1.6, eviye=(0.25, 0.6), ox=ox)
    mob(p, "tezgah", 2.1, 2.0, 0.6, 1.65, ocak=(2.15, 2.45), ox=ox)
    mob(p, "dolap", 0.2, 2.1, 0.4, 1.55, ox=ox)
    mob(p, "kanepe", 2.95, 0.75, 0.65, 1.9, ox=ox)
    mob(p, "masa", 5.15, 2.15, 1.5, 0.85, n=6, ox=ox)


def alt_kat1(p, k):
    ox, bl, br = OX[k], k, "alt" + k
    _sukunet(p, ox, bl, br, "Sükûnet ve\nçalışma odası")
    oda(p, "Ebeveyn odası", (2.8, 0.0, 7.2, 3.8), "yatak", ox, blok=bl, birim=br, etiket=(4.1, 2.75))
    _hol_islak(p, ox, bl, br, "Banyo")
    _merdiven_oda(p, ox, bl, br, "ust")
    _cocuk_odalari(p, ox, bl, br)
    ac(p, "kapi", 2.9, 3.8, 3.7, 3.8, ox, ic="-", h=0)
    ac(p, "pencere", 3.4, 0.0, 6.6, 0.0, ox, h=1.5)
    mob(p, "yatak2", 5.0, 0.6, yon="D", ox=ox)
    mob(p, "dolap", 4.0, 3.1, 2.9, 0.55, ox=ox)


def ust_kat2(p, k):
    ox, bl, br = OX[k], k, "ust" + k
    oda(p, "Giriş eşiği", [(0.0, 0.0, 2.8, 2.2), (1.4, 2.2, 2.8, 3.8)], "esik", ox, blok=bl, birim=br,
        etiket=(1.3, 1.45), etiket_mod="ad")
    oda(p, "Misafir WC", (0.0, 2.2, 1.4, 3.8), "islak", ox, blok=bl, birim=br, etiket_mod="yok")
    p.notlar.append((ox + 0.42, 2.5, "WC", 4.8, C.YAZI, "center"))
    oda(p, "Misafir odası\n(selamlık)", (2.8, 0.0, 7.2, 3.8), "misafir", ox, blok=bl, birim=br,
        etiket=(4.85, 1.95))
    _hol_islak(p, ox, bl, br, "Banyo")
    _merdiven_oda(p, ox, bl, br, "alt")
    _cocuk_odalari(p, ox, bl, br)
    ac(p, "kapi", 0.6, 0.0, 1.6, 0.0, ox, ic="+", h=0)             # köprüden giriş
    ac(p, "kapi", 1.4, 2.3, 1.4, 3.0, ox, ic="-", h=0)             # misafir WC
    ac(p, "kapi", 2.8, 0.6, 2.8, 1.5, ox, ic="+", h=0)             # misafir ← eşik
    ac(p, "kapi", 1.9, 3.8, 2.7, 3.8, ox, ic="+", h=0)             # eşik → aile holü
    ac(p, "pencere", 3.6, 0.0, 5.6, 0.0, ox, h=1.4)                # misafir: galeri boşluğuna (kafesli)
    mob(p, "dolap", 0.2, 1.45, 0.45, 0.65, ox=ox)
    mob(p, "wc", 0.75, 3.7, yon="K", ox=ox)
    mob(p, "sedir", 3.0, 3.1, 3.9, 0.55, ox=ox)
    mob(p, "sedir", 6.4, 0.3, 0.6, 2.6, ox=ox)


def ust_kat3(p, k):
    ox, bl, br = OX[k], k, "ust" + k
    _sukunet(p, ox, bl, br)
    oda(p, "Oturma ve yemek", (2.8, 0.0, 7.2, 3.8), "yasam", ox, blok=bl, birim=br, etiket=(5.2, 2.45))
    _hol_islak(p, ox, bl, br, "Duş · WC")
    _merdiven_oda(p, ox, bl, br, "ust")
    oda(p, "Ebeveyn odası", (0.0, 6.4, 2.8, 10.4), "yatak", ox, blok=bl, birim=br, etiket=(1.3, 9.55))
    oda(p, "Mutfak", [(2.8, 6.4, 5.7, 8.3), (2.8, 8.3, 7.2, 10.4)], "mutfak", ox, blok=bl, birim=br,
        etiket=(5.65, 8.9))
    oda(p, "Kiler", (5.7, 6.4, 7.2, 8.3), "depo", ox, blok=bl, birim=br, etiket=(6.15, 6.95), etiket_mod="kisa")
    oda(p, "Loggia", (0.0, LG, 7.2, 0.0), "teras", ox, blok="Lg" + k, birim=br, yari_acik=True,
        etiket=(5.3, -0.62), etiket_mod="kisa")
    ac(p, "bosluk", 2.9, 3.8, 3.7, 3.8, ox)
    ac(p, "kapi", 1.9, 6.4, 2.7, 6.4, ox, ic="+", h=0)
    ac(p, "kapi", 2.9, 6.4, 3.7, 6.4, ox, ic="+", h=0)
    ac(p, "kapi", 5.7, 7.35, 5.7, 8.1, ox, ic="+", h=0)
    ac(p, "surgulu", 3.2, 0.0, 5.6, 0.0, ox, h=2.2)
    ac(p, "pencere", 6.0, 0.0, 6.9, 0.0, ox, h=1.6)
    ac(p, "pencere", 0.5, D, 2.3, D, ox, h=1.4)
    ac(p, "pencere", 3.4, D, 5.4, D, ox, h=1.2)
    mob(p, "masa", 3.05, 0.7, 1.4, 0.8, n=6, ox=ox)
    mob(p, "kanepe", 6.35, 0.5, 0.65, 2.2, ox=ox)
    mob(p, "sedir", 4.2, 3.1, 2.7, 0.55, ox=ox)
    mob(p, "yatak2", 0.2, 7.45, yon="B", ox=ox)
    mob(p, "dolap", 2.15, 9.0, 0.5, 1.2, ox=ox)
    mob(p, "tezgah", 3.0, 9.6, 3.95, 0.6, ocak=(3.55, 9.65), eviye=(5.0, 9.7), ox=ox)
    mob(p, "masa", 3.95, 7.5, 1.3, 0.8, n=4, ox=ox)
    mob(p, "dolap", 6.62, 6.55, 0.4, 1.6, ox=ox)
    mob(p, "bitki", 0.55, -1.55, 0.3, ox=ox)
    mob(p, "bitki", 6.65, -1.55, 0.3, ox=ox)
    mob(p, "masa", 3.0, -1.35, 1.1, 0.6, n=4, ox=ox)


# =============================================================================
# Çekirdek (x 0–4,5): asansör, şaft, U merdiven, geçit / sahanlık
# =============================================================================
C_KUTU = (0.15, 2.275, 2.825, 6.525)


def cekirdek(p, kat):
    bl, br = "C", "ortak"
    oda(p, "Asansör", (0.8, 0.0, 2.9, 2.2), "asansor", blok=bl, birim=br, etiket=(1.85, 1.9), etiket_mod="ad",
        say=False)
    oda(p, "Şaft", (0.0, 0.0, 0.8, 2.2), "depo", blok=bl, birim=br, etiket_mod="yok", say=False)
    m = oda(p, "Merdiven", (0.0, 2.2, 2.9, 6.6), "merdiven", blok=bl, birim=br, acik="K", etiket_mod="yok",
            say=False)
    m.u = (C_KUTU, "y", "-", "alt" if kat == 0 else "ara", 10)
    p.ek_duvarlar.append(box(-0.15, 6.35, 0.15, 6.85))       # açık kenar şeridinin dış duvardaki izini kapat
    if kat == 0:
        oda(p, "Bina girişi ve\navlu geçidi", [(2.9, 0.0, 4.5, 10.4), (0.0, 6.6, 2.9, 8.2)], "ortak", blok=bl,
            birim=br, etiket=(3.7, 4.3), say=False)
        oda(p, "Bisiklet,\npuset", (0.0, 8.2, 2.9, 10.4), "depo", blok=bl, birim=br, etiket=(1.45, 9.3),
            etiket_mod="ad", say=False)
        ac(p, "kapi", 3.2, D, 4.2, D, ic="-", h=0)
        ac(p, "kapi", 3.2, 0.0, 4.2, 0.0, ic="+", h=2.1)
        ac(p, "kapi", 0.6, 8.2, 1.6, 8.2, ic="+", h=0)
        ac(p, "bosluk", 2.9, 0.4, 2.9, 1.5)
    elif kat == 2:
        oda(p, "Sahanlık ve\ngaleri kapısı", [(2.9, 0.0, 4.5, 6.6), (0.0, 6.6, 4.5, 8.2)], "ortak", blok=bl,
            birim=br, etiket=(3.7, 3.6), say=False)
        oda(p, "Ortak çamaşır", (0.0, 8.2, 4.5, 10.4), "ortak", blok=bl, birim=br, etiket=(2.25, 9.35),
            etiket_mod="ad", say=False)
        ac(p, "kapi", 3.2, 0.0, 4.2, 0.0, ic="+", h=2.1)
        ac(p, "kapi", 1.6, 8.2, 2.6, 8.2, ic="+", h=0)
        ac(p, "bosluk", 2.9, 0.4, 2.9, 1.5)
        ac(p, "pencere", 0.8, D, 3.6, D, h=1.2)
    else:
        oda(p, "Sahanlık", (0.0, 6.6, 4.5, 10.4), "ortak", blok=bl, birim=br, etiket=(2.25, 9.0), etiket_mod="ad",
            say=False)
        oda(p, "Ortak depo", (2.9, 0.0, 4.5, 6.6), "depo", blok=bl, birim=br, etiket=(3.7, 3.6), etiket_mod="ad",
            say=False)
        ac(p, "kapi", 3.2, 6.6, 4.1, 6.6, ic="-", h=0)
        ac(p, "pencere", 0.8, D, 3.6, D, h=1.2)
    p.mob("platform", 1.15, 0.45, 1.45, 1.2)


# =============================================================================
# Planlar
# =============================================================================
def bloklar(loggia=False):
    b = [Blok("C", T_DIS, T_IC), Blok("A", T_DIS, T_IC), Blok("B", T_DIS, T_IC)]
    if loggia:
        b += [Blok("LgA", T_DIS, T_IC), Blok("LgB", T_DIS, T_IC)]
    return b


def kolonlar(p):
    for x in (0.0, OX["A"], OX["B"], OX["B"] + MW):
        p.kolonlar.append((x, G_DIS + 0.15, 0.30))


def galeri_izi(p, metin=True):
    """Alt katlarda galerinin izdüşümü (kesikli)."""
    for y in (G_IC, G_DIS):
        p.cizgiler.append(([(XLIM[0], y), (XLIM[1], y)], C.YAZI2, 0.6, (0, (5, 2.5))))


def cevre(p, kat):
    """Sokak, ön eşik, komşu modüller, bahçe ve avlu (eksen içinde kalan etiketlerle)."""
    p.dis_alanlar.append((box(XLIM[0], D + 0.15 + ON_ESIK, XLIM[1], YLIM[1]), "#e6e3dc",
                          "S O K A K   (S2 yaşam sokağı, 10 m)", (12.3, D + 0.15 + ON_ESIK + 0.6)))
    p.dis_alanlar.append((box(XLIM[0], D + 0.15, XLIM[1], D + 0.15 + ON_ESIK), C.ton("#8d887e", 0.85), "", None))
    for (a, b) in ((XLIM[0], -0.15), (OX["B"] + MW + 0.15, XLIM[1])):
        p.dis_alanlar.append((box(a, -0.15, b, D + 0.15), "#ecebe6", "", None))
    if kat == 0:
        for k in ("A", "B"):
            g = box(OX[k], BAHCE, OX[k] + MW, -0.15)
            p.dis_alanlar.append((g, "acik", "", None))
        p.dis_alanlar.append((box(0.0, BAHCE, CW, -0.15), C.ODA_RENK["ortak"], "", None))
        p.dis_alanlar.append((box(XLIM[0], YLIM[0], XLIM[1], BAHCE), C.ton(C.AQUA, 0.78),
                              "O R T A K   A V L U", (11.6, BAHCE - 0.65)))
        for x in (OX["A"], OX["B"], OX["B"] + MW):
            p.cizgiler.append(([(x, BAHCE), (x, -0.15)], C.ton(C.AQUA, 0.15), 1.2, "-"))
        p.cizgiler.append(([(XLIM[0], BAHCE), (0.0, BAHCE)], C.ton(C.AQUA, 0.15), 1.6, "-"))
        p.cizgiler.append(([(CW, BAHCE), (XLIM[1], BAHCE)], C.ton(C.AQUA, 0.15), 1.6, "-"))
        p.agaclar += [(OX["A"] + 1.4, BAHCE - 1.0, 1.3, "erik"), (OX["B"] + 5.6, BAHCE - 1.0, 1.3, "dut")]
    else:
        p.dis_alanlar.append((box(XLIM[0], YLIM[0], XLIM[1], -0.15), C.ton(C.AQUA, 0.9), "", None))


def plan_zemin():
    p = PlanE("Zemin", bloklar())
    cekirdek(p, 0)
    for k in ("A", "B"):
        alt_zemin(p, k)
    cevre(p, 0)
    galeri_izi(p)
    kolonlar(p)
    return p


def plan_kat1():
    p = PlanE("1. kat", bloklar())
    cekirdek(p, 1)
    for k in ("A", "B"):
        alt_kat1(p, k)
    cevre(p, 1)
    galeri_izi(p)
    kolonlar(p)
    return p


def plan_kat2():
    p = PlanE("2. kat", bloklar())
    cekirdek(p, 2)
    for k in ("A", "B"):
        ust_kat2(p, k)
    cevre(p, 2)
    # galeri, köprüler, ışık boşluğu, çiçeklik
    kopruler = [box(3.1, G_IC, 4.3, -0.15)] + [box(OX[k] + 0.5, G_IC, OX[k] + 1.7, -0.15) for k in ("A", "B")]
    galeri = box(XLIM[0], G_DIS, XLIM[1], G_IC)
    bosluk = box(XLIM[0], G_IC, XLIM[1], -0.15).difference(unary_union(kopruler))
    cicek = box(XLIM[0], G_IC, XLIM[1], G_IC + 0.2).difference(unary_union([k.buffer(0.05) for k in kopruler]))
    p.dis_alanlar.append((bosluk, "#f4f3ef", "", None))
    p.dis_alanlar.append((galeri, C.ODA_RENK["ortak"], "GALERİ (hayat) · net 1,8 m", (OX["B"] + 1.9, -2.05)))
    for kp in kopruler:
        p.dis_alanlar.append((kp, C.ODA_RENK["ortak"], "", None))
    p.dis_alanlar.append((cicek, C.ton(C.AQUA, 0.45), "", None))
    p.cizgiler.append(([(XLIM[0], G_DIS), (XLIM[1], G_DIS)], C.DUVAR, 1.0, "-"))
    kolonlar(p)
    return p


def plan_kat3():
    p = PlanE("3. kat", bloklar(loggia=True))
    cekirdek(p, 3)
    for k in ("A", "B"):
        ust_kat3(p, k)
    cevre(p, 3)
    p.cizgiler.append(([(XLIM[0], G_DIS), (0.0, G_DIS), (0.0, LG - 0.15)], C.YAZI2, 0.6, (0, (5, 2.5))))
    p.cizgiler.append(([(CW, LG - 0.15), (CW, G_DIS), (XLIM[1], G_DIS)], C.YAZI2, 0.6, (0, (5, 2.5))))
    p.cizgiler.append(([(XLIM[0], G_IC), (0.0, G_IC)], C.YAZI2, 0.6, (0, (5, 2.5))))
    p.cizgiler.append(([(OX["A"], SACAK), (OX["B"] + MW, SACAK)], C.TURUNCU, 0.7, (0, (6, 2, 1, 2))))
    return p


# =============================================================================
# Güneş [H]
# =============================================================================
def engeller():
    x0, x1 = -60.0, 90.0
    kut = [
        (x0, G_DIS, G_ALT, x1, G_IC, 2 * KAT_H),                    # galeri döşemesi
        (x0, G_IC - 0.2, 2 * KAT_H, x1, G_IC, 2 * KAT_H + 0.6),     # galeri iç kenarındaki çiçeklik
        (x0, LG, 3 * KAT_H - 0.3, x1, 0.0, 3 * KAT_H),              # 3. kat loggia döşemesi
        (x0, LG, 3 * KAT_H, x1, LG + 0.15, 3 * KAT_H + 1.1),        # loggia dolu korkuluğu
        (x0, SACAK, 4 * KAT_H - 0.3, x1, 0.0, 4 * KAT_H),           # çatı saçağı (çardak yaprak döken: engel sayılmaz) [V]
        (x0, BAHCE - 0.1, 0.0, x1, BAHCE + 0.1, 1.2),               # bahçe çiti
        (x0, KARSI_KANAT[0] - 7.0, 0.0, x1, KARSI_KANAT[0], KARSI_KANAT[1]),   # avlunun güneyindeki Z+1 kanat [V]
    ]
    for k in range(-8, 12):                                         # galeri kolonları ve loggia yan perdeleri
        x = CW + k * MW
        kut.append((x - 0.15, G_DIS, 0.0, x + 0.15, G_DIS + 0.3, G_ALT))
        kut.append((x - 0.15, LG, 3 * KAT_H, x + 0.15, 0.0, 4 * KAT_H - 0.3))
    return kut


NOKTALAR = [
    ("Üst dubleks · 3. kat oturma (5 kişilik birim)", (OX["A"] + 4.4, -0.16, 3 * KAT_H + 1.2)),
    ("Üst dubleks · 2. kat misafir (galeri arkası)", (OX["A"] + 4.6, -0.16, 2 * KAT_H + 1.2)),
    ("Alt dubleks · 1. kat ebeveyn (galeri altı)", (OX["A"] + 5.0, -0.16, KAT_H + 1.2)),
    ("Alt dubleks · zemin oturma (bahçe kapısı)", (OX["A"] + 5.0, -0.16, 1.2)),
]


def gunes_hesabi():
    kut = engeller()
    return [(ad, {g: gunes_saati(n, 180.0, kut, S["enlem"], GUN[g]) for g in GUN}) for ad, n in NOKTALAR]


# =============================================================================
# Kesit A–A (y boyunca, x = X_KESIT; batıya bakış, güney solda)
# =============================================================================
def kesit(fig, kayit, x_mm, y_mm):
    s0, s1, z0, z1 = -17.0, 23.5, -1.2, 15.0
    ax = C.olcekli_eksen(fig, x_mm, y_mm, (s0, s1), (z0, z1))
    m = []
    H = KAT_H
    C.k_zemin(ax, kayit, s0, s1, 0.0, kalin=0.0)
    ax.add_patch(C.Rectangle((s0, z0), s1 - s0, -z0, fc=C.ton("#8d887e", 0.82), ec="none", zorder=0.5))
    # karşı kanat (avlunun güneyi) ve sokak karşısı blok — görünüş
    C.k_gorunus(ax, kayit, s0, 0.0, KARSI_KANAT[0], KARSI_KANAT[1])
    s_karsi = D + 0.15 + ON_ESIK + SOKAK_G + ON_ESIK
    C.k_gorunus(ax, kayit, s_karsi, 0.0, s1, 4 * H + 1.1)
    # döşemeler (merdiven boşlukları açık)
    C.k_dolu(ax, kayit, -0.15, -0.3, D + 0.15, 0.0, renk=C.ton(C.DUVAR, 0.55), z=3)
    C.k_doseme(ax, kayit, -0.15, 3.8, H, DOS)
    C.k_doseme(ax, kayit, 6.4, D + 0.15, H, DOS)
    C.k_doseme(ax, kayit, -0.15, D + 0.15, 2 * H, DOS)
    C.k_doseme(ax, kayit, LG, 3.8, 3 * H, DOS)
    C.k_doseme(ax, kayit, 6.4, D + 0.15, 3 * H, DOS)
    C.k_doseme(ax, kayit, SACAK, D + 0.15, 4 * H, DOS)
    # cepheler ve parapetler
    C.k_duvar(ax, kayit, 0.0, T_DIS, -0.3, 4 * H - DOS,
              pencereler=[(0.0, 2.2), (H + 0.8, H + 2.3), (2 * H + 0.9, 2 * H + 2.3), (3 * H, 3 * H + 2.2)])
    C.k_duvar(ax, kayit, D, T_DIS, -0.3, 4 * H + 1.1,
              pencereler=[(0.9, 2.3), (H + 0.9, H + 2.3), (2 * H + 0.9, 2 * H + 2.3), (3 * H + 1.0, 3 * H + 2.2)])
    C.k_dolu(ax, kayit, LG, 3 * H, LG + 0.15, 3 * H + 1.1)                      # loggia korkuluğu
    C.k_dolu(ax, kayit, SACAK, 4 * H, SACAK + 0.15, 4 * H + 1.1)                # çatı parapeti
    C.k_dolu(ax, kayit, LG, 4 * H - 0.42, SACAK, 4 * H - 0.32, renk="#6b5a45", z=5)   # asma çardağı
    ax.plot([LG + 0.08, LG + 0.08], [3 * H + 1.1, 4 * H - 0.42], color="#6b5a45", lw=0.9, zorder=5)
    # iç duvarlar (merdiven kutusu y 3,8 ve 6,4), merdiven kesitleri
    for k in range(4):
        for y in (3.8, 6.4):
            C.k_duvar(ax, kayit, y, T_IC, k * H, (k + 1) * H - DOS)
    for z_bas in (0.0, 2 * H):                                                   # alt ve üst dubleks merdiveni
        for (a, b, zz) in ((3.875, 5.05, 0.84), (5.15, 6.325, 2.26)):
            C.k_dolu(ax, kayit, a, z_bas + zz - 0.18, b, z_bas + zz, renk=C.ton(C.DUVAR, 0.25))
    # galeri: döşeme, çiçeklik, korkuluk, kolon ve köprü (görünüş)
    C.k_dolu(ax, kayit, G_DIS, G_ALT, G_IC, 2 * H)
    C.k_dolu(ax, kayit, G_IC - 0.2, 2 * H, G_IC, 2 * H + 0.6, renk=C.ton(C.AQUA, 0.2))
    ax.plot([G_DIS + 0.05, G_DIS + 0.05], [2 * H, 2 * H + 1.1], color=C.DUVAR, lw=0.8, zorder=5)
    ax.plot([G_DIS + 0.05, G_IC - 0.2], [2 * H + 1.1, 2 * H + 1.1], color=C.DUVAR, lw=0.5, zorder=5)
    kayit.cizgi(ax, [(G_DIS + 0.05, 2 * H), (G_DIS + 0.05, 2 * H + 1.1)], "KESIT")
    C.k_gorunus(ax, kayit, G_DIS, 0.0, G_DIS + 0.3, G_ALT)
    C.k_gorunus(ax, kayit, G_IC, G_ALT, -0.15, 2 * H, ls=(0, (2, 1.5)))
    # çatı: bahçe toprağı, pergola, su deposu
    C.k_dolu(ax, kayit, SACAK + 0.15, 4 * H, D, 4 * H + 0.25, renk=C.ton("#6b5a45", 0.55), z=3.5)
    C.k_gorunus(ax, kayit, 6.9, 4 * H + 0.25, 9.6, 4 * H + 1.6, ec=C.MAVI, fc=C.ton(C.MAVI, 0.85), z=3)
    for s in (0.4, 3.4):
        ax.plot([s, s], [4 * H + 0.25, 4 * H + 2.05], color="#6b5a45", lw=0.9, zorder=5)
    C.k_dolu(ax, kayit, 0.2, 4 * H + 2.0, 3.6, 4 * H + 2.1, renk="#6b5a45", z=5)
    # bahçe, avlu, sokak: çit, ağaçlar
    C.k_dolu(ax, kayit, BAHCE - 0.2, 0.0, BAHCE + 0.2, 1.2, renk=C.ton(C.AQUA, 0.35), z=3)
    C.k_agac(ax, kayit, -9.5, 0.0, govde=2.6, tac=2.2)
    C.k_agac(ax, kayit, 18.0, 0.0, govde=2.8, tac=1.8)
    # insanlar
    C.k_insan(ax, -1.9, 2 * H)
    C.k_insan(ax, -1.1, 3 * H, cocuk=True)
    C.k_insan(ax, -2.4, 0.0, cocuk=True)
    C.k_insan(ax, 0.9, 0.0, yasli=True)
    C.k_insan(ax, 8.4, 2 * H)
    C.k_insan(ax, 2.0, 4 * H + 0.25)
    C.k_insan(ax, 12.0, 0.0)
    # öğle güneşi [H]
    a_ara = ogle_yuksekligi(S["enlem"], GUN["21 Aralık"])
    a_haz = ogle_yuksekligi(S["enlem"], GUN["21 Haziran"])
    _, t = C.k_gunes(ax, kayit, SACAK, 4 * H - DOS, a_ara, +1, -SACAK, C.MAVI, f"21 Ara öğle {sayi(a_ara, 1)}°")
    m.append(t)
    C.k_gunes(ax, kayit, SACAK, 4 * H - DOS, a_haz, +1, 2.0, C.TURUNCU, None, z_min=3 * H)
    C.k_gunes(ax, kayit, G_DIS, G_ALT, a_ara, +1, -G_DIS, C.MAVI, None)
    _, t = C.k_gunes(ax, kayit, G_DIS, G_ALT, a_haz, +1, 2.6, C.TURUNCU, f"21 Haz öğle {sayi(a_haz, 1)}°",
                     z_min=0.0)
    m.append(t)
    # metinler
    for (s, z, metin, renk) in ((2.7, 2.3, "oturma", C.YAZI), (8.4, 1.75, "misafir\n(büyükler)", C.YAZI),
                                (2.1, H + 1.75, "ebeveyn", C.YAZI), (8.4, H + 1.6, "çocuk 1", C.YAZI),
                                (1.9, 2 * H + 1.6, "misafir\n(selamlık)", C.YAZI), (8.0, 2 * H + 2.25, "çocuk 1", C.YAZI),
                                (2.0, 3 * H + 1.75, "oturma", C.YAZI), (8.2, 3 * H + 1.6, "mutfak", C.YAZI),
                                (5.1, 1.45, "merdiven", C.YAZI2), (5.1, 2 * H + 1.45, "merdiven", C.YAZI2),
                                (-3.2, 0.3, "bahçe", C.YAZI2), (-11.6, 0.3, "ortak avlu", C.YAZI2),
                                (15.6, 0.3, "S2 yaşam sokağı (10 m)", C.YAZI2), (11.05, 1.55, "ön\neşik", C.YAZI2),
                                (-16.85, KARSI_KANAT[1] + 0.35, "avlunun güneyi: Z+1 kanat [V]", C.YAZI2),
                                (s_karsi + 0.15, 4 * H + 1.45, "karşı blok", C.YAZI2),
                                (8.25, 4 * H + 2.05, "su deposu\n3 m³ / modül", C.MAVI),
                                (1.9, 4 * H + 2.45, "çatı bahçesi ve çamaşır", C.YAZI2)):
        ha = "left" if s in (-16.85, s_karsi + 0.15) else "center"
        m.append(ax.text(s, z, metin, ha=ha, va="center", fontsize=5.9, color=renk, zorder=9, linespacing=1.1))
    m.append(ax.text(-1.9, 2 * H + 2.2, "galeri", ha="center", va="center", fontsize=5.9, zorder=9))
    m.append(ax.text(-0.5, 2.6, "ışık boşluğu", ha="center", va="center", fontsize=5.2, color=C.YAZI2, zorder=9,
                     rotation=90))
    m.append(ax.text(LG - 0.15, 4 * H - 0.05, "asma çardağı", ha="right", va="center", fontsize=5.4,
                     color=C.YAZI2, zorder=9))
    m.append(ax.text(-2.3, 3 * H + 1.75, "loggia", ha="right", va="center", fontsize=5.9, zorder=9))
    # ölçüler
    xo = D + 0.15 + ON_ESIK + 0.9
    for k in range(4):
        m += C.olcu(ax, kayit, (xo, k * H), (xo, (k + 1) * H), sayi(H, 2), ust=False)
    m += C.olcu(ax, kayit, (xo + 1.3, 0.0), (xo + 1.3, 4 * H + 1.1), sayi(4 * H + 1.1, 2), ust=False)
    m += C.olcu(ax, kayit, (9.8, 2 * H), (9.8, 3 * H - DOS), f"iç {sayi(H - DOS, 2)}", ust=True)
    for (a, b) in ((BAHCE, G_DIS), (G_DIS, G_IC), (G_IC, 0.0), (0.0, D), (D, D + ON_ESIK)):
        m += C.olcu(ax, kayit, (a, -0.95), (b, -0.95), sayi(b - a, 2), ust=True, yazi=5.4)
    m += C.plan_basligi(ax, "Kesit A–A", s0 + 0.2, z1 - 0.85, alt="güney solda · batıya bakış · 1/100")
    m += C.olcek_cubugu(ax, kayit, s0 + 0.4, z1 - 3.05, n=5, adim=1.0, h=0.16)
    return m, (a_ara, a_haz)


# =============================================================================
# Pafta
# =============================================================================
def maliyet():
    bm = BIRIM_MALIYET["III.B"] * KAR_HARIC
    birim_brut = MW * (D + T_DIS) * 2                                   # parti duvarı aksından, dış yüzle
    cekirdek_brut = CW * (D + T_DIS) * 4 + CATI_CIKIS
    galeri = (SEGMENT + 3.0) * (G_IC - G_DIS) + (N_MODUL * 1.2 + 1.2) * (-G_IC)
    ust_pay_kapali = cekirdek_brut / N_MODUL
    ust_pay_yari = (galeri + ACIK_MERDIVEN) / N_MODUL
    loggia = (MW - T_DIS) * (-LG - T_DIS)
    yapim_alt = birim_brut * bm
    yapim_ust = (birim_brut + ust_pay_kapali) * bm + (ust_pay_yari + loggia) * YARI_ACIK_KATSAYI * bm
    asansor = ASANSOR_TL                                                # 3 durak: zemin, galeri, çatı (≤ 4) [V]
    return dict(bm=bm, birim_brut=birim_brut, cekirdek_brut=cekirdek_brut, galeri=galeri,
                ust_pay_kapali=ust_pay_kapali, ust_pay_yari=ust_pay_yari, loggia=loggia, yapim_alt=yapim_alt,
                yapim_ust=yapim_ust, asansor_p4=asansor / N_MODUL, asansor_bugun=3 * asansor / N_MODUL,
                bina_brut=N_MODUL * 2 * birim_brut + cekirdek_brut,
                bina_yari=galeri + ACIK_MERDIVEN + 2 * N_MODUL * 0 + N_MODUL * loggia)


def ciz():
    pZ, p1, p2, p3 = plan_zemin(), plan_kat1(), plan_kat2(), plan_kat3()
    planlar = [("Zemin", pZ), ("1. kat", p1), ("2. kat", p2), ("3. kat", p3)]
    kayit = Kayit()
    fig = C.pafta()
    m = C.baslik(fig, "Tip (e) · Z+3 galerili blok — alt dubleks + üst dubleks, avlu tarafında galeri",
                 f"Referans {SEHIR_AD} ({sayi(S['enlem'], 1)}° K; yıllık yağış {sayi(S['yagis_yil'])} mm; MGM {S['donem']} [D]). "
                 f"K3 mahalle merkezi, T4 çubuğu ya da T3 sokak kanadı; S2'ye bakan cephe, sokak kuzeyde, ortak avlu güneyde [V]. "
                 f"Modül {sayi(MW, 1)} m, derinlik {sayi(D, 1)} m, kat {sayi(KAT_H, 2)} m. Çizilen: asansörlü çekirdek + iki modül "
                 "(4 konut). Duvar 30 cm; malzeme Rapor 16.")
    yer = [(pZ, 14, 372, "Zemin kat planı", "alt dubleks: sokaktan eşiksiz giriş · bahçe avluya"),
           (p1, 233, 372, "1. kat planı", "alt dubleksin yatak katı · önünde galerinin gölgeliği"),
           (p2, 14, 184, "2. kat planı — galeri katı", "üst dubleks girişi: eşik, misafir WC'si, selamlık"),
           (p3, 233, 184, "3. kat planı — aile katı", "galerisiz kat · loggia 1,8 m · saçak 1,0 m + asma çardağı")]
    for (p, xmm, ymm, ad, alt) in yer:
        ax = C.olcekli_eksen(fig, xmm, ymm, XLIM, YLIM)
        m += p.ciz(ax, kayit, yazi=5.3)
        m += C.plan_basligi(ax, ad, XLIM[0] + 0.1, YLIM[1] + 0.05)
        m.append(ax.text(XLIM[0] + 0.1, YLIM[1] - 0.25, alt, fontsize=5.3, color=C.YAZI2, ha="left", va="top",
                         zorder=10))
        m += C.olcek_cubugu(ax, kayit, XLIM[1] - 5.6, YLIM[1] - 0.65, n=5, adim=1.0, h=0.14, yazi=5.0)
        if p is pZ:
            m += C.kesit_isareti(ax, kayit, (X_KESIT, -4.55), (X_KESIT, 12.0), "A", yon=(-0.9, 0))
            m += pZ.olcu_zinciri(ax, kayit, [0.0, CW, OX["B"], OX["B"] + MW], 11.0 + 0.15, yatay=True, ust=True,
                                 yazi=5.2)
            for k in ("A", "B"):
                m.append(ax.text(OX[k] + 3.6, -2.2, "özel bahçe", ha="center", va="center", fontsize=5.3,
                                 color=C.YAZI2, zorder=9))
            m.append(ax.text(2.25, -2.2, "avlu\ngeçidi", ha="center", va="center", fontsize=5.0, color=C.YAZI2,
                             zorder=9))
            m.append(ax.text(OX["B"] + MW + 0.55, -1.9, "galeri\nizi", ha="center", va="center", fontsize=4.8,
                             color=C.YAZI2, zorder=9))
        if p is p1:
            m.append(ax.text(10.2, -1.9, "üstte galeri (2. kat): yazın gölgelik, kışın güneş altından girer",
                             ha="center", va="center", fontsize=5.2, color=C.YAZI2, zorder=9))
            m.append(ax.text(10.2, -4.3, "bahçeler (altta)", ha="center", va="center", fontsize=5.2,
                             color=C.YAZI2, zorder=9))
        if p is p2:
            m.append(ax.text(OX["A"] + 4.3, -0.57, "ışık boşluğu 1,0 m · çiçeklik", ha="center", va="center",
                             fontsize=4.9, color=C.YAZI2, zorder=9))
            m.append(ax.text(OX["B"] + 1.1, -0.57, "köprü", ha="center", va="center", fontsize=4.6, color=C.YAZI2,
                             zorder=9))
            m.append(ax.text(10.2, -4.2, "galerinin iki ucunda açık kaçış merdiveni (çizim dışında) [DY]",
                             ha="center", va="center", fontsize=5.2, color=C.YAZI2, zorder=9))
        if p is p3:
            m.append(ax.text(2.25, -1.25, "çekirdek\nçatıya çıkar", ha="center", va="center", fontsize=4.9,
                             color=C.YAZI2, zorder=9))
            m.append(ax.text(10.2, -2.45, "altta galeri", ha="center", va="center", fontsize=4.9, color=C.YAZI2,
                             zorder=9))
            m.append(ax.text(10.2, -4.2, "loggia: saçak 1,0 m + yaprak döken asma çardağı; kış güneşi girer, yaz güneşi kesilir",
                             ha="center", va="center", fontsize=5.2, color=C.YAZI2, zorder=9))
    mk, (a_ara, a_haz) = kesit(fig, kayit, 14, 10)
    m += mk
    # yön diyagramı, lejant
    m += C.yon_diyagrami(fig, 482, 482, 58, S["enlem"], SEHIR_AD, KIBLE,
                         [("21 Haz", GUN["21 Haziran"], C.TURUNCU), ("21 Ara", GUN["21 Aralık"], C.MAVI)])
    lm, lh = C.lejant(fig, 458, 395, 138, ["misafir", "yasam", "yatak", "sukunet", "mutfak", "islak", "esik", "depo",
                                           "dolasim", "merdiven", "ortak", "acik", "teras"],
                      ek=[(C.DUVAR, "duvar (kesilen)", "duvar"), (C.MAVI, "pencere, camlı kapı", "pencere"),
                          (C.ODA_RENK["asansor"], "asansör kuyusu", "kutu"), (C.YAZI2, "galeri izdüşümü", "cizgi"),
                          (C.AQUA, "kıble yönü", "kible"), (C.YAZI2, "havalandırma bacası", "baca")])
    m += lm
    # güneş, maliyet, ölçütler
    gs = gunes_hesabi()
    ml = maliyet()
    cati_modul = MW * (D + 0.15 - SACAK)
    yagmur = yagmur_potansiyeli(cati_modul, SEHIR_AD)
    avlu = SEGMENT * (PARSEL_DER - ON_ESIK - (D + T_DIS) - (-BAHCE))
    cati_bahce = N_MODUL * MW * D * CATI_KULLANIM
    hane = 2 * N_MODUL
    avlu_hane, cati_hane = avlu / hane, cati_bahce / hane
    parsel = SEGMENT * PARSEL_DER
    bahce = (MW * (-BAHCE - 0.15)) - 0.3 * 0.3
    ek_ortak = dict(
        su=("Su", f"çatı 100 m² başına ≥ {sayi(OLCUT['yagmur_m3_100m2'])} m³ depo",
            f"{sayi(SU_DEPO_MODUL)} m³ / modül · {sayi(100 * SU_DEPO_MODUL / cati_modul, 1)} m³/100 m²",
            "✓" if 100 * SU_DEPO_MODUL / cati_modul >= OLCUT["yagmur_m3_100m2"] else "≈"),
        deprem=("Deprem", "Z+3, düzenli aks, perde parti duvarı, yumuşak kat yok",
                "7,2 m aks · galeri ayrı kolonlu [V]", "✓"),
        isil=("Isıl konfor", "kış güneşi yaşam odasına, yaz güneşi gölgede",
              "saçak 1,0 m + çardak · galeri gölgeliği", "✓"))
    oz = birim_ozeti(planlar, "ustA", acik_ozel=0.0, acik_ortak=avlu_hane + cati_hane, ic_yukseklik=KAT_H - DOS,
                     gunes=gs[0][1], arsa=parsel / hane,
                     ek=dict(kusak=("Çok kuşak", "büyükler için aynı blokta eşiksiz oda",
                                    "alt dubleks zemini (misafir + duş)", "≈"),
                             buyume_satir=("Esneklik", "ruhsatla büyüme ya da bölünme payı",
                                           "misafir → büyükler odası; büyüme yok", "≈"),
                             erisim=("Erişim", "asansör galeriye; zeminde ≥ %15 eşiksiz BB",
                                     "galeri + asansör · iç merdiven", "≈"),
                             sessizlik=("Sessizlik", "yatak odası önünden geçiş yok; gece iç ≤ 30 dB",
                                        "galeri önünde yatak yok · sokak S2 [V]", "≈"),
                             **ek_ortak))
    oz_alt = birim_ozeti(planlar, "altA", acik_ozel=bahce, acik_ortak=avlu_hane + cati_hane,
                         ic_yukseklik=KAT_H - DOS, gunes=gs[3][1], arsa=parsel / hane,
                         ek=dict(kusak=("Çok kuşak", "zeminde eşiksiz yatak odası + banyo",
                                        "misafir (büyükler) odası + engelsiz duş", "✓"),
                                 erisim=("Erişim", "zeminden eşiksiz giriş", "sokaktan eşiksiz · asansör gerekmez", "✓"),
                                 sessizlik=("Sessizlik", "yatak odası önünden geçiş yok; gece iç ≤ 30 dB",
                                            "yatak katı galerinin altında, geçişsiz", "✓"),
                                 **ek_ortak))
    oz_alt["isil"] = ("Isıl konfor", "kış güneşi yaşam odasına, yaz güneşi gölgede",
                      f"zemin oturma 21 Şub {sayi(gs[3][1]['21 Şubat'], 1)} sa · Haz 0 sa", "✓")
    ozet = [("Net kapalı alan (2. + 3. kat)", f"{sayi(oz['net'], 1)} m²"),
            ("Loggia (özel, yarı açık)", f"{sayi(oz['teras'], 1)} m²"),
            ("Ortak avlu · çatı bahçesi payı [V]", f"{sayi(avlu_hane, 1)} · {sayi(cati_hane, 1)} m²/hane"),
            ("Kapalı brüt: birim + çekirdek payı", f"{sayi(ml['birim_brut'], 1)} + {sayi(ml['ust_pay_kapali'], 1)} m²"),
            ("Galeri ve kaçış merdiveni payı", f"{sayi(ml['ust_pay_yari'], 1)} m² (yarı açık)"),
            ("Net / kişi (5 kişi)", f"{sayi(oz['net_kisi'], 1)} m²"),
            ("Blok kesimi [V]", f"{sayi(SEGMENT, 1)} × {sayi(PARSEL_DER, 1)} m · {hane} konut · {sayi(parsel / hane, 0)} m²/hane"),
            ("Yağmur suyu (modül çatısı)", f"{sayi(yagmur, 0)} m³/yıl · çatı {sayi(cati_modul, 0)} m²"),
            ("Kaba yapım (birim) [V]", f"{sayi(ml['yapim_ust'] / 1e6, 2)} mn TL + asansör {sayi(ml['asansor_p4'] / 1e3, 0)} bin TL")]
    mm_, y = sag_sutun(fig, 602, 560, 226, [("2. kat", Suzgec(p2, "ustA")), ("3. kat", Suzgec(p3, "ustA"))], oz, ozet,
                       yazi=5.7, satir_h=3.6, ust_baslik="Alan programı — üst dubleks A, 5 kişi (net, m²) [H]")
    m += mm_
    # güneş saati tablosu (dört nokta)
    gsat = [(ad, *[sayi(g[k], 1) for k in ("21 Aralık", "21 Şubat", "21 Mart", "21 Haziran")]) for ad, g in gs]
    tm, th = C.tablo_ciz(fig, 602, y - 38.5, 226, ["Pencere (güney cephe, z +1,2 m)", "21 Ara", "21 Şub", "21 Mar",
                                                    "21 Haz"], gsat, [0, 128, 152, 176, 200],
                         baslik_metin="Doğrudan güneş, saat (öğle yük. 25,6° · 37,8° · 49,0° · 72,4°) [H]", yazi=5.6,
                         satir_h=3.7, hizalar=["left", "right", "right", "right", "right"],
                         alt_not="Engeller: galeri, çiçeklik, kolonlar, loggia, saçak, yan perdeler, bahçe çiti; avlunun\n"
                                 "güneyinde 15,7 m ötede Z+1 kanat (7,0 m) [V]. Asma çardağı yaprak döken sayıldı [V].")
    m += tm
    y2 = y - 38.5 - 4.0
    # blok özeti ve asansör (P4)
    bs = [("Alt dubleks (×9)", "Z+1", str(oz_alt["oda"]), sayi(oz_alt["net"], 0), sayi(ml["birim_brut"], 0),
           f"bahçe {sayi(bahce, 0)}", sayi(ml["yapim_alt"] / 1e6, 2)),
          ("Üst dubleks (×9)", "2+3", str(oz["oda"]), sayi(oz["net"], 0),
           sayi(ml["birim_brut"] + ml["ust_pay_kapali"], 0), f"loggia {sayi(oz['teras'], 0)}",
           sayi(ml["yapim_ust"] / 1e6, 2)),
          ("Çekirdek (×1)", "Z–çatı", "—", "—", sayi(ml["cekirdek_brut"], 0), "—", "payda"),
          ("Galeri + 2 açık merdiven", "2. kat", "—", "—", f"{sayi(ml['galeri'] + ACIK_MERDIVEN, 0)} y.a.", "—", "payda"),
          ("Blok kesimi", "Z+3", f"{hane} k.", "—", sayi(ml["bina_brut"], 0), f"avlu {sayi(avlu, 0)}",
           sayi((N_MODUL * (ml['yapim_alt'] + ml['yapim_ust']) + ASANSOR_TL) / 1e6, 1))]
    tm, th = C.tablo_ciz(fig, 602, y2 - 42.0, 226, ["Birim", "Kat", "Oda", "Net m²", "Brüt m²", "Açık m²", "Yapım mn TL"],
                         bs, [0, 52, 76, 96, 120, 148, 190], baslik_metin="Blok kesimi: 9 modül + 1 çekirdek [H/V]",
                         yazi=5.6, satir_h=3.7, hizalar=["left", "left", "right", "right", "right", "right", "right"],
                         kalin_satirlar=(4,),
                         alt_not="Brüt: parti duvarı aksından, dış yüzle. Üst dubleks yapımına çekirdek ve galeri payı\n"
                                 "dahil; 2026 tebliği III.B × 0,92; yarı açık × 0,5 [D/V]. Arsa, otopark, peyzaj hariç.")
    m += tm
    y3 = y2 - 42.0 - 4.0
    oran = lambda a: 100 * a / ml["yapim_ust"]
    asat = [("Bugün: her merdiven evine 1 asansör", "3", f"{sayi(ml['asansor_bugun'] / 1e3, 0)} bin TL",
             f"%{sayi(oran(ml['asansor_bugun']), 1)}"),
            ("P4: galeriyle 3 merdiven evine 1 asansör", "1", f"{sayi(ml['asansor_p4'] / 1e3, 0)} bin TL",
             f"%{sayi(oran(ml['asansor_p4']), 1)}")]
    tm, th = C.tablo_ciz(fig, 602, y3 - 29.5, 226, ["Düzen (9 üst dubleks)", "Asansör", "Hane başı", "Yapıma oranı"],
                         asat, [0, 120, 150, 190], baslik_metin="Asansör yükü: bugünkü PAİY md. 34 ve paket P4 [V]",
                         yazi=5.6, satir_h=3.7, hizalar=["left", "right", "right", "right"],
                         alt_not=f"Asansör {sayi(ASANSOR_TL / 1e6, 1)} mn TL (≤ 4 durak, kuyu dahil) [V]. P4 yürürlükte değil;\n"
                                 "galeri ve açık kaçış merdiveninin yangın yönetmeliğine uyumu doğrulanmadı [DY].")
    m += tm
    y4 = y3 - 29.5 - 4.0
    ol = olcut_satirlari(oz_alt)
    tm, th = C.tablo_ciz(fig, 602, y4 - (3.4 * (len(ol) + 1) + 8.0), 226, ["İlke", "Ölçüt (öneri)", "Alt dubleks A", ""],
                         ol, [0, 38, 145, 217], baslik_metin="İlke kontrol listesi — alt dubleks A (5 kişi) [H]",
                         yazi=5.4, satir_h=3.4, hizalar=["left", "left", "left", "left"])
    m += tm
    # orta sütun: mahremiyet ve tasarım notları
    nt, nh = C.metin_kutusu(fig, 458, 324, 138, "Mahremiyet ve galeri", [
        "• Galeri yalnız 2. katta. Alt dubleks sokaktan,",
        "  üst dubleks galeriden girer; 1. ve 3. katın",
        "  önünden kimse geçmez.",
        "• Galeriye eşik, misafir WC'si ve misafir odası",
        "  bakar (selamlık). Aile katı 3. kattır (harem).",
        "• Galeri cepheden 1,0 m ayrılır; kapıya köprüyle",
        "  varılır; iç kenardaki çiçeklik bakışı keser.",
        "• Misafir odası penceresi kafesli; köprü kapıları",
        "  komşu pencerelerinin karşısına gelmez.",
        "• Alt dubleksin misafir odası iki kapılı: eşikten",
        "  misafire, holden büyüklere; yanında engelsiz duş.",
        "• Her konut kuzeye ve güneye bakar; hol ve",
        "  merdiven boşluğu çapraz havalandırır.",
        "• Yatak odaları galeriye bakmaz; çocuklar 2. katta",
        "  sokak (S2) tarafında, ebeveyn 3. katta [V].",
    ], yazi=5.9, satir_h=3.45)
    m += nt
    tn, tnh = C.metin_kutusu(fig, 458, 280, 138, "Tasarım notları", [
        "• Bir asansör zemine, galeri katına ve çatıya durur.",
        "• Çekirdeğin zemininde sokaktan avluya geçit ve",
        "  bisiklet odası; 2. katta ortak çamaşır.",
        "• Islak hacimler üst üste; perde parti duvarları",
        "  7,2 m arayla; galeri ayrı kolonlara oturur [V].",
        "• Çatı ortak bahçedir: bostan, çamaşır, su deposu.",
        "• S1 cephesinde zemin, 4,5 m'lik esnek kata döner.",
    ], yazi=5.9, satir_h=3.45)
    m += tn
    # alt orta: güneş okuması ve geleneksel karşılığı
    g_ust, g_1, g_z = gs[0][1], gs[2][1], gs[3][1]
    gg, ggh = C.metin_kutusu(fig, 430, 132, 165, "Kesit A–A: galeri ve saçak güneşi nasıl süzer? [H]", [
        f"• 21 Aralık öğle {sayi(a_ara, 1)}°: güneş saçağın ve galerinin altından girer.",
        f"  3. kat oturma {sayi(g_ust['21 Aralık'], 1)} sa, 1. kat ebeveyn {sayi(g_1['21 Aralık'], 1)} sa, "
        f"zemin oturma {sayi(g_z['21 Aralık'], 1)} sa.",
        f"• 21 Haziran öğle {sayi(a_haz, 1)}°: saçak, loggia ve galeri camları gölgeler (0 sa).",
        f"• Bedel: 1. kat (galeri altı) 21 Şubat'ta {sayi(g_1['21 Şubat'], 1)} sa, 21 Mart'ta {sayi(g_1['21 Mart'], 1)} sa.",
        "  Galerinin derinliği (1,8 m) ve kotu bu katı ara mevsimde gölgeler.",
    ], yazi=5.9, satir_h=3.45)
    m += gg
    gk, gh = C.metin_kutusu(fig, 430, 84, 165, "Geleneksel karşılığı [İ]", [
        "Eldem'in dış sofalı tipi: odalar avluya bakan yarı açık",
        "bir galeriye (hayat) açılır. Han ve medrese avlularındaki",
        "revaklı galeriler de ortak dolaşımı avluya verir.",
        "Burada hayat paylaşılan bir galeri olur; aile odaları",
        "üst katta kalır. Kaynak: Eldem 1954, 1984; Rapor 11;",
        "Rapor 15 §3.3.",
    ], yazi=5.9, satir_h=3.45)
    m += gk
    m += C.kunye(fig, 602, 14, 226, "K-e")
    sorun, dxf = C.kaydet(fig, kayit, AD)
    esneklik = ("misafir odası büyükler odasına döner; alt ve üst dubleks birleştirilmez [V]; "
                "zemin S1 cephesinde esnek kata döner")
    mahremiyet = ("galeri yalnız 2. katta; galeriye eşik, misafir WC'si ve misafir odası bakar; "
                  "aile katı (3. kat) galerisiz; ışık boşluğu 1,0 m ve çiçeklik")
    oz.update(dict(tip="e", ad="Z+3 galerili blok (üst dubleks)", sehir=SEHIR_AD,
                   brut=ml["birim_brut"] + ml["ust_pay_kapali"], sinif="III.B", parsel=parsel, kat="Z+3",
                   yapim=ml["yapim_ust"], asansor=ml["asansor_p4"], asansor_bugun=ml["asansor_bugun"],
                   sorun=len(sorun), dxf=dxf, yari=ml["ust_pay_yari"] + ml["loggia"], arsa_hane=parsel / hane,
                   hane_sayisi=N_MODUL, buyume=0.0, bina_brut=ml["bina_brut"],
                   bina_net=N_MODUL * (oz["net"] + oz_alt["net"]), acik_ozel=0.0,
                   acik_ortak=avlu_hane + cati_hane, avlu_hane=avlu_hane, cati_bahce_hane=cati_hane,
                   esneklik=esneklik, mahremiyet=mahremiyet, gunes_noktalar=gs,
                   alt_dubleks=dict(net=oz_alt["net"], oda=oz_alt["oda"], bahce=bahce, yapim=ml["yapim_alt"],
                                    brut=ml["birim_brut"], pencere_min=oz_alt["pencere_min"],
                                    gunes=gs[3][1]), cati=cati_modul, yagmur_yil=yagmur,
                   sarnic=SU_DEPO_MODUL / 2))
    return oz, csv_satirlari("e", planlar, BIRIM_ADLARI)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    oz, sat = ciz()
    for k, v in oz.items():
        if k not in ("gunes_noktalar",):
            print(k, v)
    for ad, g in oz["gunes_noktalar"]:
        print(ad, {k: round(v, 2) for k, v in g.items()})
