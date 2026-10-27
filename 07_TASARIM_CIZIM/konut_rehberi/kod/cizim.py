"""
Konut rehberi — çizim motoru (plan, kesit, pafta, DXF, etiket çakışma denetimi)
==============================================================================
Bütün paftalar A1 (841 × 594 mm) yatay; plan ve kesitler kâğıtta tam 1/100 ölçekte durur
(1 m = 10 mm). PNG 150 dpi, SVG vektör (yazılar metin olarak), DXF metre biriminde ve
paftadaki yerleşimle aynı (model uzayında 1 birim = 1 m).

Plan modeli: odalar duvar eksenleri üzerinden dikdörtgenlerle tanımlanır. Her "blok" (bir
bağımsız bölüm ya da ortak çekirdek) kendi dış duvar kalınlığını taşır; iki blok arasındaki
duvar iki yarımdan oluşur (bağımsız bölümler arası 2 × t_dış/2, ses ve yangın ayrımı).
Net oda poligonu = oda dikdörtgeni − t_iç/2 ∩ blok ekseni − t_dış/2. Duvar = blok dış yüzü −
net odalar. Alanlar bu poligonlardan hesaplanır [H]; elle girilmiş toplam yoktur.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, PathPatch, Polygon as MPoly, Rectangle
from matplotlib.path import Path as MPath
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

from veri import sayi

KOD = Path(__file__).resolve().parent
CIKTI = KOD.parent                               # 07_TASARIM_CIZIM/konut_rehberi

# --- Palet (proje) ---------------------------------------------------------------
MAVI, TURUNCU, AQUA, SARI = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
YAZI, YAZI2, ZEMIN = "#0b0b0b", "#52514e", "#fcfcfb"
DUVAR = "#2b2926"
MOBILYA = "#9c988f"
BOSLUK = "#f7f6f2"


def ton(renk, t):
    """Rengi beyazla karıştır (t = 0 → renk, 1 → beyaz)."""
    r, g, b = (int(renk[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(round(c + (255 - c) * t) for c in (r, g, b))


ODA_RENK = {
    "yasam": ton(SARI, 0.80), "mutfak": ton(TURUNCU, 0.84), "misafir": ton(TURUNCU, 0.70),
    "yatak": ton(MAVI, 0.84), "islak": "#e6ebef", "dolasim": "#efede8", "esik": "#e9e4da",
    "sukunet": ton(AQUA, 0.80), "depo": "#e2dfd7", "yari_acik": ton(SARI, 0.90), "ortak": "#f1e9dd",
    "merdiven": "#e7e4dd", "acik": ton(AQUA, 0.88), "teras": ton(AQUA, 0.80), "asansor": ton(MAVI, 0.70),
}
TUR_AD = {
    "yasam": "yaşam (oturma, sofa, eyvan)", "mutfak": "mutfak ve kiler", "misafir": "misafir bölümü (selamlık)",
    "yatak": "yatak odası", "islak": "ıslak hacim", "dolasim": "dolaşım", "esik": "giriş eşiği",
    "sukunet": "sükûnet (namaz, okuma)", "depo": "depolama (kiler, yüklük)", "yari_acik": "yarı açık (revak, sundurma)",
    "ortak": "ortak alan", "acik": "avlu, bahçe", "teras": "teras, balkon", "merdiven": "merdiven",
}
YASANAN = {"yasam", "yatak", "misafir", "mutfak", "sukunet"}         # pencere ölçütü uygulanan odalar
ACIK_TURLER = {"acik", "teras"}

plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "font.size": 7,
                     "text.color": YAZI, "axes.edgecolor": YAZI2})

PAFTA_MM = (841.0, 594.0)
PT_MM = 25.4 / 72.0


# =============================================================================
# DXF kaydı
# =============================================================================
class Kayit:
    """Çizilen geometriyi DXF için toplar (metre, paftadaki yerleşimle)."""

    KATMAN = {"DUVAR": 7, "ODA": 8, "ACIKLIK": 5, "MOBILYA": 9, "YAZI": 7, "OLCU": 3, "KESIT": 7,
              "PEYZAJ": 3, "GUNES": 30, "AKS": 1, "GORUNUS": 8}

    def __init__(self):
        self.ogeler = []

    @staticmethod
    def _tr(ax, x, y):
        o = getattr(ax, "_dxf", None)
        if o is None:
            return None
        return (x - o[2] + o[0], y - o[3] + o[1])

    def poligon(self, ax, geom, katman, dolgu=False):
        if getattr(ax, "_dxf", None) is None or geom is None or geom.is_empty:
            return
        for p in ([geom] if geom.geom_type == "Polygon" else [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon"]):
            halkalar = [[self._tr(ax, x, y) for x, y in h.coords] for h in [p.exterior] + list(p.interiors)]
            self.ogeler.append(("poligon", katman, halkalar, dolgu))

    def cizgi(self, ax, pts, katman):
        if getattr(ax, "_dxf", None) is None:
            return
        self.ogeler.append(("cizgi", katman, [self._tr(ax, x, y) for x, y in pts]))

    def daire(self, ax, x, y, r, katman):
        if getattr(ax, "_dxf", None) is None:
            return
        self.ogeler.append(("daire", katman, self._tr(ax, x, y), r))

    def yay(self, ax, x, y, r, a0, a1, katman):
        if getattr(ax, "_dxf", None) is None:
            return
        self.ogeler.append(("yay", katman, self._tr(ax, x, y), r, a0, a1))

    def yazi(self, ax, x, y, metin, pt, katman="YAZI", aci=0.0):
        if getattr(ax, "_dxf", None) is None or not metin:
            return
        boy = pt * PT_MM * 0.1 * 0.72            # kâğıtta pt → model uzayında m (1/100), büyük harf yüksekliği
        for k, satir in enumerate(str(metin).split("\n")):
            n = len(str(metin).split("\n"))
            dy = ((n - 1) / 2 - k) * boy * 1.45
            if aci:
                xx, yy = x - dy * math.sin(math.radians(aci)) * -1, y
                self.ogeler.append(("yazi", katman, self._tr(ax, x + dy, y), satir, boy, aci))
            else:
                self.ogeler.append(("yazi", katman, self._tr(ax, x, y + dy), satir, boy, aci))

    def yaz(self, yol):
        try:
            import ezdxf
            from ezdxf.enums import TextEntityAlignment
        except ImportError:
            print("  ezdxf yok: DXF atlandı")
            return False
        doc = ezdxf.new("R2010", setup=True)
        doc.units = ezdxf.units.M
        for ad, renk in self.KATMAN.items():
            if ad not in doc.layers:
                doc.layers.add(ad, color=renk)
        msp = doc.modelspace()
        for o in self.ogeler:
            if o[0] == "poligon":
                _, kat, halkalar, dolgu = o
                for h in halkalar:
                    msp.add_lwpolyline(h, close=True, dxfattribs={"layer": kat})
                if dolgu:
                    ht = msp.add_hatch(color=250, dxfattribs={"layer": kat})
                    for k, h in enumerate(halkalar):
                        ht.paths.add_polyline_path(h, is_closed=True, flags=1 if k == 0 else 16)
            elif o[0] == "cizgi":
                msp.add_lwpolyline(o[2], dxfattribs={"layer": o[1]})
            elif o[0] == "daire":
                msp.add_circle(o[2], o[3], dxfattribs={"layer": o[1]})
            elif o[0] == "yay":
                msp.add_arc(o[2], o[3], o[4], o[5], dxfattribs={"layer": o[1]})
            elif o[0] == "yazi":
                _, kat, p, metin, boy, aci = o
                t = msp.add_text(metin, height=boy, rotation=aci, dxfattribs={"layer": kat})
                t.set_placement(p, align=TextEntityAlignment.MIDDLE_CENTER)
        doc.saveas(yol)
        return True


# =============================================================================
# Pafta ve ölçekli eksen
# =============================================================================
def pafta():
    fig = plt.figure(figsize=(PAFTA_MM[0] / 25.4, PAFTA_MM[1] / 25.4), dpi=150)
    fig.patch.set_facecolor(ZEMIN)
    return fig


def olcekli_eksen(fig, x_mm, y_mm, xlim, ylim, olcek=100):
    """Kâğıtta (x_mm, y_mm) sol alt köşeye, tam 1/olcek ölçekte eksen yerleştirir."""
    w = (xlim[1] - xlim[0]) * 1000.0 / olcek
    h = (ylim[1] - ylim[0]) * 1000.0 / olcek
    ax = fig.add_axes([x_mm / PAFTA_MM[0], y_mm / PAFTA_MM[1], w / PAFTA_MM[0], h / PAFTA_MM[1]])
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    ax.patch.set_alpha(0)
    ax._dxf = (x_mm * olcek / 1000.0, y_mm * olcek / 1000.0, xlim[0], ylim[0])
    ax._mm = (x_mm, y_mm, w, h)
    return ax


def mm_eksen(fig, x_mm, y_mm, w_mm, h_mm):
    """Kâğıt milimetresiyle çalışan ölçeksiz eksen (tablolar, lejant)."""
    ax = fig.add_axes([x_mm / PAFTA_MM[0], y_mm / PAFTA_MM[1], w_mm / PAFTA_MM[0], h_mm / PAFTA_MM[1]])
    ax.set_xlim(0, w_mm)
    ax.set_ylim(0, h_mm)
    ax.axis("off")
    ax.patch.set_alpha(0)
    return ax


def poligon_ciz(ax, geom, fc, ec="none", lw=0.0, zorder=1, hatch=None, ls="-", alpha=1.0):
    if geom is None or geom.is_empty:
        return
    for p in ([geom] if geom.geom_type == "Polygon" else [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon"]):
        verts, codes = [], []
        for h in [p.exterior] + list(p.interiors):
            xy = list(h.coords)
            verts += xy
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY]
        ax.add_patch(PathPatch(MPath(verts, codes), fc=fc, ec=ec, lw=lw, zorder=zorder, hatch=hatch, ls=ls,
                               alpha=alpha))


# =============================================================================
# Plan modeli
# =============================================================================
@dataclass
class Oda:
    ad: str
    rects: list
    tur: str
    blok: str = "A"
    acik: str = ""                 # duvarsız kenarlar: K G D B (yalnız tek dikdörtgenli odada)
    etiket: tuple | None = None    # etiket merkezi (x, y); None → otomatik
    etiket_mod: str = "tam"        # tam · kisa · ad · yok
    yari_acik: bool = False
    birim: str = "konut"
    say: bool = True               # net alan toplamına girer mi
    net: object = None


@dataclass
class Aciklik:
    tur: str                       # pencere · yuksek · kapi · kapi2 · surgulu · bosluk
    x0: float
    y0: float
    x1: float
    y1: float
    ic: str = "+"                  # kapının açıldığı yön (+ / −: eksenin artan / azalan yanı)
    h: float = 1.4                 # pencere cam yüksekliği (m); kapıda camlı ise > 0
    mentese: str = "0"             # 0: başlangıç ucunda, 1: bitiş ucunda


@dataclass
class Blok:
    ad: str
    t_dis: float = 0.30
    t_ic: float = 0.15


class Plan:
    def __init__(self, ad, bloklar=None, t_dis=0.30, t_ic=0.15):
        self.ad = ad
        self.bloklar = {b.ad: b for b in (bloklar or [Blok("A", t_dis, t_ic)])}
        self.odalar: list[Oda] = []
        self.acikliklar: list[Aciklik] = []
        self.mobilyalar = []
        self.dis_alanlar = []      # (geom, tür, etiket, etiket_xy)
        self.agaclar = []          # (x, y, r, ad)
        self.ek_duvarlar = []      # (geom)
        self.kolonlar = []         # (x, y, s)
        self.bacalar = []          # rüzgâr/hava bacası (x, y)
        self.notlar = []           # (x, y, metin, pt, renk, ha)
        self.cizgiler = []         # (pts, renk, lw, ls)
        self._hazir = False

    # --- tanım ---------------------------------------------------------------
    def oda(self, ad, rects, tur, **kw):
        if isinstance(rects[0], (int, float)):
            rects = [rects]
        o = Oda(ad, rects, tur, **kw)
        self.odalar.append(o)
        return o

    def ac(self, tur, x0, y0, x1, y1, **kw):
        self.acikliklar.append(Aciklik(tur, x0, y0, x1, y1, **kw))

    def mob(self, tip, *a, **kw):
        self.mobilyalar.append((tip, a, kw))

    # --- geometri ----------------------------------------------------------------
    def hesapla(self):
        if self._hazir:
            return
        self.U = {}
        for b in self.bloklar:
            rs = [box(*r) for o in self.odalar if o.blok == b for r in o.rects]
            self.U[b] = unary_union(rs) if rs else Polygon()
        self.tum_U = unary_union(list(self.U.values()))
        for o in self.odalar:
            b = self.bloklar[o.blok]
            R = unary_union([box(*r) for r in o.rects])
            net = R.buffer(-b.t_ic / 2, join_style=2).intersection(self.U[o.blok].buffer(-b.t_dis / 2, join_style=2))
            if o.acik and len(o.rects) == 1:
                x0, y0, x1, y1 = o.rects[0]
                ti, td = b.t_ic / 2, b.t_dis / 2
                ser = []
                if "K" in o.acik:
                    ser.append(box(x0 + ti, y1 - td - 0.01, x1 - ti, y1 + td + 0.01))
                if "G" in o.acik:
                    ser.append(box(x0 + ti, y0 - td - 0.01, x1 - ti, y0 + td + 0.01))
                if "D" in o.acik:
                    ser.append(box(x1 - td - 0.01, y0 + ti, x1 + td + 0.01, y1 - ti))
                if "B" in o.acik:
                    ser.append(box(x0 - td - 0.01, y0 + ti, x0 + td + 0.01, y1 - ti))
                net = unary_union([net] + ser)
            o.net = net
        ayak = unary_union([self.U[b].buffer(self.bloklar[b].t_dis / 2, join_style=2) for b in self.U])
        self.ayak = ayak
        self.duvar = ayak.difference(unary_union([o.net for o in self.odalar]))
        if self.ek_duvarlar:
            self.duvar = unary_union([self.duvar] + self.ek_duvarlar)
        self._hazir = True

    def kalinlik(self, x, y, yatay):
        """Eksen üzerindeki bir noktada duvar kalınlığı."""
        d = 0.06
        if yatay:
            a, c = Point(x, y + d), Point(x, y - d)
        else:
            a, c = Point(x + d, y), Point(x - d, y)
        for b, U in self.U.items():
            ia, ic = U.contains(a), U.contains(c)
            if ia != ic:            # blok sınırı
                return self.bloklar[b].t_dis
        for b, U in self.U.items():
            if U.contains(a) and U.contains(c):
                return self.bloklar[b].t_ic
        return max(bl.t_dis for bl in self.bloklar.values())

    # --- ölçüler -------------------------------------------------------------------
    def oda_olcu(self, o):
        x0, y0, x1, y1 = o.net.bounds
        dik = abs(o.net.area - (x1 - x0) * (y1 - y0)) < 0.02 or (bool(o.acik) and len(o.rects) == 1)
        return (x1 - x0, y1 - y0, dik)

    def pencere_alani(self, o):
        """Odaya ait cam alanı (m²) ve pencere yönleri."""
        alan, yon = 0.0, set()
        cx, cy = o.net.centroid.x, o.net.centroid.y
        for a in self.acikliklar:
            if a.tur not in ("pencere", "yuksek", "kapi", "kapi2", "surgulu") or a.h <= 0:
                continue
            if a.tur in ("kapi", "kapi2") and a.h < 1.0:
                continue
            yatay = abs(a.y0 - a.y1) < 1e-6
            t = self.kalinlik((a.x0 + a.x1) / 2, (a.y0 + a.y1) / 2, yatay)
            g = box(min(a.x0, a.x1) - (0 if yatay else t / 2 + 0.05), min(a.y0, a.y1) - (t / 2 + 0.05 if yatay else 0),
                    max(a.x0, a.x1) + (0 if yatay else t / 2 + 0.05), max(a.y0, a.y1) + (t / 2 + 0.05 if yatay else 0))
            if not g.intersects(o.net):
                continue
            # karşı yan bir başka kapalı oda ise (iç kapı) pencere sayılmaz
            mx, my = (a.x0 + a.x1) / 2, (a.y0 + a.y1) / 2
            if yatay:
                dis = Point(mx, my + (t / 2 + 0.1) * (1 if my > cy else -1))
            else:
                dis = Point(mx + (t / 2 + 0.1) * (1 if mx > cx else -1), my)
            komsu = [p for p in self.odalar if p is not o and p.net.contains(dis)]
            if komsu and not any(p.yari_acik or p.tur in ACIK_TURLER for p in komsu):
                continue
            uz = math.hypot(a.x1 - a.x0, a.y1 - a.y0)
            cam = uz * a.h * (0.75 if a.tur in ("kapi", "kapi2", "surgulu") else 0.85)   # kasa payı [V]
            alan += cam
            if yatay:
                yon.add("K" if my > cy else "G")
            else:
                yon.add("D" if mx > cx else "B")
        return alan, yon

    def tablo(self):
        self.hesapla()
        sat = []
        for o in self.odalar:
            if o.tur == "acik":
                continue
            w, h, dik = self.oda_olcu(o)
            cam, yon = self.pencere_alani(o)
            sat.append(dict(plan=self.ad, oda=o.ad.replace("\n", " "), tur=o.tur, birim=o.birim,
                            net_m2=round(o.net.area, 2), en=round(min(w, h), 2), boy=round(max(w, h), 2), dik=dik,
                            yari_acik=o.yari_acik, say=o.say, cam_m2=round(cam, 2),
                            pencere_taban=round(cam / o.net.area, 3) if o.net.area else 0.0,
                            yonler="".join(sorted(yon))))
        return sat

    def brut(self):
        """Kapalı brüt (dış yüzlerle) ve yarı açık örtülü alan."""
        self.hesapla()
        ya = sum(o.net.area for o in self.odalar if o.yari_acik)
        return self.ayak.area - ya, ya

    # --- çizim --------------------------------------------------------------------
    def ciz(self, ax, kayit: Kayit, yazi=6.6, olculer=True):
        self.hesapla()
        metinler = []
        for g, tur, et, exy in self.dis_alanlar:
            poligon_ciz(ax, g, ODA_RENK.get(tur, tur) if not tur.startswith("#") else tur, zorder=0.5)
            kayit.poligon(ax, g, "PEYZAJ")
            if et:
                p = g.representative_point() if exy is None else Point(*exy)
                metinler.append(ax.text(p.x, p.y, et, ha="center", va="center", fontsize=yazi - 0.4, color=YAZI2,
                                        zorder=6, linespacing=1.1))
                kayit.yazi(ax, p.x, p.y, et, yazi - 0.4)
        for o in self.odalar:
            poligon_ciz(ax, o.net, ODA_RENK[o.tur], zorder=1)
            kayit.poligon(ax, o.net, "ODA")
            if o.tur == "merdiven":
                self._merdiven(ax, o, kayit)
        for (x, y, r, ad) in self.agaclar:
            ax.add_patch(Circle((x, y), r, fc=ton(AQUA, 0.55), ec=ton(AQUA, 0.1), lw=0.5, alpha=0.75, zorder=4.5))
            ax.plot([x - 0.15, x + 0.15], [y, y], color=ton(AQUA, 0.1), lw=0.5, zorder=4.6)
            ax.plot([x, x], [y - 0.15, y + 0.15], color=ton(AQUA, 0.1), lw=0.5, zorder=4.6)
            kayit.daire(ax, x, y, r, "PEYZAJ")
        for tip, a, kw in self.mobilyalar:
            mobilya(ax, kayit, tip, *a, **kw)
        poligon_ciz(ax, self.duvar, DUVAR, zorder=3)
        kayit.poligon(ax, self.duvar, "DUVAR", dolgu=True)
        for (x, y, s) in self.kolonlar:
            ax.add_patch(Rectangle((x - s / 2, y - s / 2), s, s, fc=DUVAR, ec="none", zorder=3.1))
            kayit.poligon(ax, box(x - s / 2, y - s / 2, x + s / 2, y + s / 2), "DUVAR", dolgu=True)
        for a in self.acikliklar:
            self._aciklik(ax, a, kayit)
        for (x, y) in self.bacalar:
            ax.add_patch(Rectangle((x - 0.3, y - 0.3), 0.6, 0.6, fc="none", ec=YAZI2, lw=0.5, zorder=5))
            ax.plot([x - 0.3, x + 0.3], [y - 0.3, y + 0.3], color=YAZI2, lw=0.4, zorder=5)
            ax.plot([x - 0.3, x + 0.3], [y + 0.3, y - 0.3], color=YAZI2, lw=0.4, zorder=5)
            kayit.poligon(ax, box(x - 0.3, y - 0.3, x + 0.3, y + 0.3), "MOBILYA")
        for (pts, renk, lw, ls) in self.cizgiler:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color=renk, lw=lw, ls=ls, zorder=5.5)
            kayit.cizgi(ax, pts, "AKS")
        for o in self.odalar:
            if o.etiket_mod != "yok":
                metinler += self._etiket(ax, o, kayit, yazi)
        for (x, y, m, pt, renk, ha) in self.notlar:
            metinler.append(ax.text(x, y, m, fontsize=pt, color=renk, ha=ha, va="center", zorder=7, linespacing=1.1))
            kayit.yazi(ax, x, y, m, pt)
        return metinler

    def _merdiven(self, ax, o, kayit):
        bounds = getattr(o, "merdiven_kutu", None) or o.net.bounds
        merdiven_sembol(ax, kayit, bounds, getattr(o, "yon", None), getattr(o, "basamak", None),
                        getattr(o, "kesik", None))

    def _aciklik(self, ax, a, kayit):
        yatay = abs(a.y0 - a.y1) < 1e-6
        mx, my = (a.x0 + a.x1) / 2, (a.y0 + a.y1) / 2
        t = self.kalinlik(mx, my, yatay)
        e = 0.012
        if yatay:
            xa, xb = sorted((a.x0, a.x1))
            g = box(xa, a.y0 - t / 2 - e, xb, a.y0 + t / 2 + e)
        else:
            ya, yb = sorted((a.y0, a.y1))
            g = box(a.x0 - t / 2 - e, ya, a.x0 + t / 2 + e, yb)
        poligon_ciz(ax, g, BOSLUK, zorder=3.2)
        if a.tur == "bosluk":
            return
        lw = 0.45
        if a.tur in ("pencere", "yuksek"):
            if yatay:
                ls = [[(xa, a.y0 - t / 2), (xb, a.y0 - t / 2)], [(xa, a.y0 + t / 2), (xb, a.y0 + t / 2)],
                      [(xa, a.y0), (xb, a.y0)]]
            else:
                ls = [[(a.x0 - t / 2, ya), (a.x0 - t / 2, yb)], [(a.x0 + t / 2, ya), (a.x0 + t / 2, yb)],
                      [(a.x0, ya), (a.x0, yb)]]
            for k, p in enumerate(ls):
                ax.plot(*zip(*p), color=DUVAR if k < 2 else MAVI, lw=lw if k < 2 else 0.8,
                        ls="-" if (k < 2 or a.tur == "pencere") else (0, (2.5, 1.5)), zorder=3.3)
                kayit.cizgi(ax, p, "ACIKLIK")
            # kasa uçları
            for p in ([[(xa, a.y0 - t / 2), (xa, a.y0 + t / 2)], [(xb, a.y0 - t / 2), (xb, a.y0 + t / 2)]] if yatay else
                      [[(a.x0 - t / 2, ya), (a.x0 + t / 2, ya)], [(a.x0 - t / 2, yb), (a.x0 + t / 2, yb)]]):
                ax.plot(*zip(*p), color=DUVAR, lw=lw, zorder=3.3)
            return
        if a.tur == "surgulu":
            if yatay:
                L = xb - xa
                for k, dy in enumerate((-0.04, 0.04)):
                    p = [(xa + k * L * 0.45, a.y0 + dy), (xa + (k * 0.45 + 0.55) * L, a.y0 + dy)]
                    ax.plot(*zip(*p), color=MAVI, lw=0.8, zorder=3.3)
                    kayit.cizgi(ax, p, "ACIKLIK")
            else:
                L = yb - ya
                for k, dx in enumerate((-0.04, 0.04)):
                    p = [(a.x0 + dx, ya + k * L * 0.45), (a.x0 + dx, ya + (k * 0.45 + 0.55) * L)]
                    ax.plot(*zip(*p), color=MAVI, lw=0.8, zorder=3.3)
                    kayit.cizgi(ax, p, "ACIKLIK")
            return
        # kapı: kanat ve yay
        s = 1 if a.ic == "+" else -1
        kanatlar = [(0, 1.0)] if a.tur == "kapi" else [(0, 0.5), (1, 0.5)]
        for (uc, oran) in kanatlar:
            if yatay:
                L = (xb - xa) * oran
                if (uc == 0) == (a.mentese == "0"):
                    hx = xa
                    ang0 = 0 if s > 0 else 0
                    p_kanat = [(hx, a.y0 + s * t / 2), (hx, a.y0 + s * (t / 2 + L))]
                    yay = (hx, a.y0 + s * t / 2, L, 0 if s > 0 else 270, 90 if s > 0 else 360)
                else:
                    hx = xb
                    p_kanat = [(hx, a.y0 + s * t / 2), (hx, a.y0 + s * (t / 2 + L))]
                    yay = (hx, a.y0 + s * t / 2, L, 90 if s > 0 else 180, 180 if s > 0 else 270)
            else:
                L = (yb - ya) * oran
                if (uc == 0) == (a.mentese == "0"):
                    hy = ya
                    p_kanat = [(a.x0 + s * t / 2, hy), (a.x0 + s * (t / 2 + L), hy)]
                    yay = (a.x0 + s * t / 2, hy, L, 0 if s > 0 else 90, 90 if s > 0 else 180)
                else:
                    hy = yb
                    p_kanat = [(a.x0 + s * t / 2, hy), (a.x0 + s * (t / 2 + L), hy)]
                    yay = (a.x0 + s * t / 2, hy, L, 270 if s > 0 else 180, 360 if s > 0 else 270)
            ax.plot(*zip(*p_kanat), color=DUVAR, lw=0.7, zorder=3.4)
            kayit.cizgi(ax, p_kanat, "ACIKLIK")
            cx, cy, r, a0, a1 = yay
            ax.add_patch(Arc((cx, cy), 2 * r, 2 * r, theta1=a0, theta2=a1, color=DUVAR, lw=0.35, zorder=3.4))
            kayit.yay(ax, cx, cy, r, a0, a1, "ACIKLIK")

    def _etiket(self, ax, o, kayit, yazi):
        w, h, dik = self.oda_olcu(o)
        A = o.net.area
        ad = o.ad
        if o.etiket_mod == "ad":
            satirlar = [ad]
        elif o.etiket_mod == "kisa" or not dik:
            satirlar = [ad, f"{sayi(A, 1)} m²"]
        else:
            satirlar = [ad, f"{sayi(w, 2)} × {sayi(h, 2)}", f"{sayi(A, 1)} m²"]
        if o.yari_acik and o.etiket_mod != "ad":
            satirlar[-1] += " (yarı açık)"
        if o.etiket is not None:
            x, y = o.etiket
        else:
            p = o.net.representative_point() if not dik else o.net.centroid
            # en büyük dikdörtgen parçanın merkezi
            if len(o.rects) > 1:
                en = max(o.rects, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
                p = box(*en).intersection(o.net).centroid
            x, y = p.x, p.y
        dar = w < 1.35 and h > w
        metin = "\n".join(satirlar)
        t = ax.text(x, y, metin, ha="center", va="center", fontsize=yazi, color=YAZI, zorder=8, linespacing=1.12,
                    rotation=90 if dar else 0)
        t._oda = o
        kayit.yazi(ax, x, y, metin, yazi, aci=90 if dar else 0)
        return [t]

    def olcu_zinciri(self, ax, kayit, eksenler, sabit, yatay=True, ofs=1.2, yazi=5.8, ust=True):
        """Eksenler arası ölçü zinciri (aks aralıkları)."""
        metinler = []
        for a, b in zip(eksenler[:-1], eksenler[1:]):
            metinler += olcu(ax, kayit, (a, sabit), (b, sabit), sayi(b - a, 2), yazi=yazi, ust=ust) if yatay else \
                olcu(ax, kayit, (sabit, a), (sabit, b), sayi(b - a, 2), yazi=yazi, ust=ust)
        return metinler


def olcu(ax, kayit, p0, p1, metin, yazi=5.8, ust=True, renk=YAZI2):
    """Mimari ölçü çizgisi: 45° kesme işaretli. p0–p1 yatay ya da düşey."""
    (x0, y0), (x1, y1) = p0, p1
    yatay = abs(y1 - y0) < 1e-9
    ax.plot([x0, x1], [y0, y1], color=renk, lw=0.4, zorder=9)
    kayit.cizgi(ax, [p0, p1], "OLCU")
    for (x, y) in (p0, p1):
        ax.plot([x - 0.12, x + 0.12], [y - 0.12, y + 0.12], color=renk, lw=0.7, zorder=9)
        kayit.cizgi(ax, [(x - 0.12, y - 0.12), (x + 0.12, y + 0.12)], "OLCU")
        if yatay:
            ax.plot([x, x], [y - 0.25, y + 0.25], color=renk, lw=0.3, zorder=9)
        else:
            ax.plot([x - 0.25, x + 0.25], [y, y], color=renk, lw=0.3, zorder=9)
    if yatay:
        t = ax.text((x0 + x1) / 2, y0 + (0.12 if ust else -0.12), metin, ha="center", va="bottom" if ust else "top",
                    fontsize=yazi, color=renk, zorder=9)
        kayit.yazi(ax, (x0 + x1) / 2, y0 + (0.3 if ust else -0.3), metin, yazi, "OLCU")
    else:
        t = ax.text(x0 + (-0.12 if ust else 0.12), (y0 + y1) / 2, metin, ha="right" if ust else "left", va="center",
                    rotation=90, fontsize=yazi, color=renk, zorder=9, rotation_mode="anchor")
        t.set_ha("center")
        t.set_va("bottom" if ust else "top")
        kayit.yazi(ax, x0 + (-0.3 if ust else 0.3), (y0 + y1) / 2, metin, yazi, "OLCU", aci=90)
    return [t]


def merdiven_sembol(ax, kayit, bounds, yon=None, n=None, kesik=None):
    """Merdiven basamakları ve çıkış oku. yon: çıkış yönü (K G D B); kesik: kesim çizgisi (0–1)."""
    x0, y0, x1, y1 = bounds
    yon = yon or ("K" if (y1 - y0) >= (x1 - x0) else "D")
    dikey = yon in ("K", "G")
    L = (y1 - y0) if dikey else (x1 - x0)
    n = n or max(2, int(round(L / 0.27)))
    adim = L / n
    for k in range(1, n):
        f = k / n
        if kesik is not None and f > kesik + 0.02:
            ls, al = (0, (2, 2)), 0.6
        else:
            ls, al = "-", 1.0
        if dikey:
            yy = y0 + k * adim
            pts = [(x0 + 0.04, yy), (x1 - 0.04, yy)]
        else:
            xx = x0 + k * adim
            pts = [(xx, y0 + 0.04), (xx, y1 - 0.04)]
        ax.plot(*zip(*pts), color="#8d887e", lw=0.45, ls=ls, alpha=al, zorder=2)
        kayit.cizgi(ax, pts, "MOBILYA")
    # çıkış oku
    if dikey:
        xm = (x0 + x1) / 2
        ya, yb = (y0 + 0.3, y1 - 0.3) if yon == "K" else (y1 - 0.3, y0 + 0.3)
        if kesik is not None:
            yb = ya + (yb - ya) * kesik
        ax.annotate("", xy=(xm, yb), xytext=(xm, ya), arrowprops=dict(arrowstyle="-|>", lw=0.6, color=YAZI2,
                                                                      mutation_scale=6), zorder=2.5)
        kayit.cizgi(ax, [(xm, ya), (xm, yb)], "MOBILYA")
        if kesik is not None:
            yk = y0 + (y1 - y0) * (kesik if yon == "K" else 1 - kesik)
            ax.plot([x0, x1], [yk - 0.15, yk + 0.15], color=YAZI2, lw=0.6, zorder=2.6)
    else:
        ym = (y0 + y1) / 2
        xa, xb = (x0 + 0.3, x1 - 0.3) if yon == "D" else (x1 - 0.3, x0 + 0.3)
        if kesik is not None:
            xb = xa + (xb - xa) * kesik
        ax.annotate("", xy=(xb, ym), xytext=(xa, ym), arrowprops=dict(arrowstyle="-|>", lw=0.6, color=YAZI2,
                                                                      mutation_scale=6), zorder=2.5)
        kayit.cizgi(ax, [(xa, ym), (xb, ym)], "MOBILYA")



# =============================================================================
# Mobilya ve peyzaj sembolleri (1/100'de okunur, ince gri)
# =============================================================================
def _dik(ax, kayit, x, y, w, h, fc="none", ec=MOBILYA, lw=0.45, z=2.2, ls="-"):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z, ls=ls))
    kayit.poligon(ax, box(x, y, x + w, y + h), "MOBILYA")


def mobilya(ax, kayit, tip, x, y, w=None, h=None, yon="K", aci=0.0, **kw):
    if tip == "yatak2" or tip == "yatak1":
        W = w or (1.6 if tip == "yatak2" else 0.9)
        H = h or 2.0
        if yon in ("D", "B"):
            W, H = H, W
        _dik(ax, kayit, x, y, W, H)
        # yastık başucunda (yon: başucu duvarı)
        n = 2 if tip == "yatak2" else 1
        if yon in ("K", "G"):
            yy = y + H - 0.45 if yon == "K" else y + 0.1
            for k in range(n):
                _dik(ax, kayit, x + 0.1 + k * (W - 0.2) / n, yy, (W - 0.2) / n - 0.05, 0.35)
            yb = y + H - 0.6 if yon == "K" else y + 0.6
            ax.plot([x, x + W], [yb, yb], color=MOBILYA, lw=0.3, zorder=2.2)
        else:
            xx = x + W - 0.45 if yon == "D" else x + 0.1
            for k in range(n):
                _dik(ax, kayit, xx, y + 0.1 + k * (H - 0.2) / n, 0.35, (H - 0.2) / n - 0.05)
    elif tip == "dolap":
        _dik(ax, kayit, x, y, w, h)
        ax.plot([x, x + w], [y, y + h], color=MOBILYA, lw=0.3, zorder=2.2)
    elif tip == "sedir":       # duvar boyu oturma
        _dik(ax, kayit, x, y, w, h, fc=ton(SARI, 0.65))
    elif tip == "masa":
        _dik(ax, kayit, x, y, w, h)
        n = kw.get("n", 6)
        ks = 0.4
        if w >= h:
            k_uzun = max(1, n // 2)
            for k in range(k_uzun):
                xx = x + (k + 0.5) * w / k_uzun - ks / 2
                _dik(ax, kayit, xx, y - ks - 0.05, ks, ks)
                _dik(ax, kayit, xx, y + h + 0.05, ks, ks)
        else:
            k_uzun = max(1, n // 2)
            for k in range(k_uzun):
                yy = y + (k + 0.5) * h / k_uzun - ks / 2
                _dik(ax, kayit, x - ks - 0.05, yy, ks, ks)
                _dik(ax, kayit, x + w + 0.05, yy, ks, ks)
    elif tip == "yer_sofrasi":
        ax.add_patch(Circle((x, y), w / 2, fc="none", ec=MOBILYA, lw=0.45, zorder=2.2))
        kayit.daire(ax, x, y, w / 2, "MOBILYA")
    elif tip == "tezgah":
        _dik(ax, kayit, x, y, w, h)
        if kw.get("ocak") is not None:
            ox, oy = kw["ocak"]
            for dx in (0.15, 0.4):
                for dy in (0.15, 0.4):
                    ax.add_patch(Circle((ox + dx, oy + dy), 0.09, fc="none", ec=MOBILYA, lw=0.35, zorder=2.3))
        if kw.get("eviye") is not None:
            ex, ey = kw["eviye"]
            _dik(ax, kayit, ex, ey, 0.5 if w >= h else 0.4, 0.4 if w >= h else 0.5, lw=0.35)
    elif tip == "wc":
        if yon in ("K", "G"):
            _dik(ax, kayit, x - 0.2, y if yon == "G" else y - 0.2, 0.4, 0.2, lw=0.35)
            ax.add_patch(matplotlib.patches.Ellipse((x, (y + 0.45) if yon == "G" else (y - 0.45)), 0.38, 0.5, fc="none",
                                                    ec=MOBILYA, lw=0.4, zorder=2.2))
        else:
            _dik(ax, kayit, x if yon == "B" else x - 0.2, y - 0.2, 0.2, 0.4, lw=0.35)
            ax.add_patch(matplotlib.patches.Ellipse(((x + 0.45) if yon == "B" else (x - 0.45), y), 0.5, 0.38, fc="none",
                                                    ec=MOBILYA, lw=0.4, zorder=2.2))
    elif tip == "lavabo":
        ax.add_patch(matplotlib.patches.Ellipse((x, y), 0.5, 0.36, fc="none", ec=MOBILYA, lw=0.4, zorder=2.2))
    elif tip == "dus":
        s = w or 0.9
        _dik(ax, kayit, x, y, s, h or s)
        ax.plot([x, x + s], [y, y + (h or s)], color=MOBILYA, lw=0.3, zorder=2.2)
        ax.plot([x, x + s], [y + (h or s), y], color=MOBILYA, lw=0.3, zorder=2.2)
    elif tip == "camasir":
        _dik(ax, kayit, x, y, 0.6, 0.6)
        ax.add_patch(Circle((x + 0.3, y + 0.3), 0.2, fc="none", ec=MOBILYA, lw=0.35, zorder=2.3))
    elif tip == "seccade":    # kıble yönünde seccade (aci: kıble azimutu, kuzeyden)
        L, B = 1.15, 0.7
        th = math.radians(aci)
        ux, uy = math.sin(th), math.cos(th)            # kıble yönü
        vx, vy = uy, -ux
        pts = [(x - vx * B / 2 - ux * L / 2, y - vy * B / 2 - uy * L / 2),
               (x + vx * B / 2 - ux * L / 2, y + vy * B / 2 - uy * L / 2),
               (x + vx * B / 2 + ux * L / 2, y + vy * B / 2 + uy * L / 2),
               (x - vx * B / 2 + ux * L / 2, y - vy * B / 2 + uy * L / 2)]
        ax.add_patch(MPoly(pts, closed=True, fc=ton(AQUA, 0.55), ec=AQUA, lw=0.5, zorder=2.4))
        kayit.poligon(ax, Polygon(pts), "MOBILYA")
        tip_ = (x + ux * (L / 2 + 0.25), y + uy * (L / 2 + 0.25))
        ax.annotate("", xy=tip_, xytext=(x + ux * L * 0.1, y + uy * L * 0.1),
                    arrowprops=dict(arrowstyle="-|>", color=AQUA, lw=0.8, mutation_scale=7), zorder=2.5)
    elif tip == "havuz":
        _dik(ax, kayit, x, y, w, h, fc=ton(MAVI, 0.6), ec=MAVI, lw=0.6, z=2.1)
    elif tip == "pergola":
        _dik(ax, kayit, x, y, w, h, fc="none", ec=ton(AQUA, 0.2), lw=0.5, ls=(0, (3, 2)), z=4.8)
        n = int(w / 0.6) if w >= h else int(h / 0.6)
        for k in range(1, n):
            if w >= h:
                ax.plot([x + k * w / n] * 2, [y, y + h], color=ton(AQUA, 0.35), lw=0.35, zorder=4.8)
            else:
                ax.plot([x, x + w], [y + k * h / n] * 2, color=ton(AQUA, 0.35), lw=0.35, zorder=4.8)
    elif tip == "platform":   # kaldırma platformu ya da asansör kabini (kesikli)
        _dik(ax, kayit, x, y, w, h, ec=MAVI, lw=0.7, ls=(0, (2, 1.5)), z=2.6)
        ax.plot([x, x + w], [y, y + h], color=MAVI, lw=0.4, ls=(0, (2, 1.5)), zorder=2.6)
        ax.plot([x, x + w], [y + h, y], color=MAVI, lw=0.4, ls=(0, (2, 1.5)), zorder=2.6)
    elif tip == "kanepe":
        _dik(ax, kayit, x, y, w, h, fc=ton(SARI, 0.7))
    elif tip == "calisma":
        _dik(ax, kayit, x, y, w, h)
        _dik(ax, kayit, x + w / 2 - 0.22, y - 0.5 if yon == "G" else y + h + 0.05, 0.44, 0.44, lw=0.35)
    elif tip == "bitki":
        ax.add_patch(Circle((x, y), w or 0.4, fc=ton(AQUA, 0.7), ec=ton(AQUA, 0.3), lw=0.4, zorder=2.2))


# =============================================================================
# Kesit yardımcıları
# =============================================================================
def k_zemin(ax, kayit, x0, x1, z=0.0, renk="#8d887e", kalin=0.6):
    ax.add_patch(Rectangle((x0, z - kalin), x1 - x0, kalin, fc=ton("#8d887e", 0.75), ec="none", zorder=1))
    ax.plot([x0, x1], [z, z], color=DUVAR, lw=0.8, zorder=2)
    kayit.cizgi(ax, [(x0, z), (x1, z)], "KESIT")


def k_dolu(ax, kayit, x0, z0, x1, z1, renk=DUVAR, z=4):
    ax.add_patch(Rectangle((min(x0, x1), min(z0, z1)), abs(x1 - x0), abs(z1 - z0), fc=renk, ec="none", zorder=z))
    kayit.poligon(ax, box(min(x0, x1), min(z0, z1), max(x0, x1), max(z0, z1)), "KESIT", dolgu=True)


def k_duvar(ax, kayit, x, t, z0, z1, pencereler=()):
    """Kesilen duvar (x: eksen). pencereler: [(z_alt, z_üst)] boşluk ve cam çizgisi."""
    parcalar = [(z0, z1)]
    for (pa, pu) in sorted(pencereler):
        yeni = []
        for (a, b) in parcalar:
            if pu <= a or pa >= b:
                yeni.append((a, b))
            else:
                if pa > a:
                    yeni.append((a, pa))
                if pu < b:
                    yeni.append((pu, b))
        parcalar = yeni
    for (a, b) in parcalar:
        k_dolu(ax, kayit, x - t / 2, a, x + t / 2, b)
    for (pa, pu) in pencereler:
        ax.plot([x, x], [pa, pu], color=MAVI, lw=0.9, zorder=4.5)
        ax.plot([x - t / 2, x + t / 2], [pa, pa], color=DUVAR, lw=0.5, zorder=4.5)
        kayit.cizgi(ax, [(x, pa), (x, pu)], "ACIKLIK")


def k_doseme(ax, kayit, x0, x1, z_ust, t=0.30):
    k_dolu(ax, kayit, x0, z_ust - t, x1, z_ust)


def k_gorunus(ax, kayit, x0, z0, x1, z1, ec="#8d887e", fc="none", lw=0.5, ls="-", z=2):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))
    kayit.poligon(ax, box(x0, z0, x1, z1), "GORUNUS")


def k_cati(ax, kayit, x0, x1, z, egim=30.0, sacak=0.9, t=0.25, tip="kirma"):
    """Eğik çatı kesiti (iki yöne). x0, x1: dış duvar yüzleri; z: saçak altı kotu (duvar üstü)."""
    xa, xb = x0 - sacak, x1 + sacak
    xm = (x0 + x1) / 2
    h = (xm - xa) * math.tan(math.radians(egim))
    dis = [(xa, z), (xm, z + h), (xb, z), (xb, z + t / math.cos(math.radians(egim))), (xm, z + h + t / math.cos(math.radians(egim))),
           (xa, z + t / math.cos(math.radians(egim)))]
    ax.add_patch(MPoly(dis, closed=True, fc=DUVAR, ec="none", zorder=4))
    kayit.poligon(ax, Polygon(dis), "KESIT", dolgu=True)
    return z + h + t


def k_tek_egim(ax, kayit, x_dusuk, x_yuksek, z_dusuk, z_yuksek, t=0.25, sacak=0.6):
    s = 1 if x_yuksek > x_dusuk else -1
    xa = x_dusuk - s * sacak
    m = (z_yuksek - z_dusuk) / (x_yuksek - x_dusuk)
    za = z_dusuk - m * (x_dusuk - xa)
    pts = [(xa, za), (x_yuksek, z_yuksek), (x_yuksek, z_yuksek + t), (xa, za + t)]
    ax.add_patch(MPoly(pts, closed=True, fc=DUVAR, ec="none", zorder=4))
    kayit.poligon(ax, Polygon(pts), "KESIT", dolgu=True)


def k_insan(ax, x, z=0.0, boy=1.75, renk=YAZI2, cocuk=False, yasli=False):
    if cocuk:
        boy = 1.2
    bas = boy * 0.13
    ax.add_patch(Circle((x, z + boy - bas), bas, fc=renk, ec="none", zorder=8))
    ax.add_patch(Rectangle((x - boy * 0.09, z + boy * 0.45), boy * 0.18, boy * 0.30, fc=renk, ec="none", zorder=8))
    ax.plot([x - boy * 0.05, x - boy * 0.07], [z + boy * 0.46, z], color=renk, lw=1.0, zorder=8, solid_capstyle="round")
    ax.plot([x + boy * 0.05, x + boy * 0.07], [z + boy * 0.46, z], color=renk, lw=1.0, zorder=8, solid_capstyle="round")
    if yasli:
        ax.plot([x + boy * 0.2, x + boy * 0.2], [z, z + boy * 0.55], color=renk, lw=0.8, zorder=8)


def k_agac(ax, kayit, x, z=0.0, govde=2.4, tac=2.2):
    ax.plot([x, x], [z, z + govde + tac * 0.5], color="#6b5a45", lw=1.4, zorder=7)
    ax.add_patch(Circle((x, z + govde + tac), tac, fc=ton(AQUA, 0.55), ec=ton(AQUA, 0.15), lw=0.5, alpha=0.85, zorder=7.1))
    kayit.daire(ax, x, z + govde + tac, tac, "PEYZAJ")


def k_gunes(ax, kayit, x, z, aci, yon, uzunluk, renk, etiket=None, yazi=5.8, etiket_konum=0.55, z_min=None):
    """Saçak ya da kenardan inen öğle güneş ışını. yon: +1 → +x yönüne (güneyden kuzeye) iner."""
    dz = uzunluk * math.tan(math.radians(aci))
    x1, z1 = x + yon * uzunluk, z - dz
    if z_min is not None and z1 < z_min:
        f = (z - z_min) / dz
        x1, z1 = x + yon * uzunluk * f, z_min
    geri = min(2.2, 1.8 / max(math.tan(math.radians(aci)), 1e-6))     # ışının saçak gerisindeki kısmı (≤ 1,8 m yükselir)
    xs, zs = x - yon * geri, z + geri * math.tan(math.radians(aci))
    ax.plot([xs, x1], [zs, z1], color=renk, lw=0.9, ls=(0, (5, 2)), zorder=9)
    kayit.cizgi(ax, [(xs, zs), (x1, z1)], "GUNES")
    t = None
    if etiket:
        import matplotlib.patheffects as pe
        t = ax.text(xs - yon * 0.1, zs + 0.12, etiket, fontsize=yazi, color=renk, ha="right" if yon > 0 else "left",
                    va="bottom", zorder=9, path_effects=[pe.withStroke(linewidth=2.2, foreground=ZEMIN)])
    return (x1, z1), t


def kesit_isareti(ax, kayit, p0, p1, harf="A", renk=TURUNCU, yon=(0, 1), yazi=8):
    """Planda kesit çizgisi: uçlarda bakış oku ve harf."""
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=renk, lw=0.9, ls=(0, (8, 2, 1, 2)), zorder=10)
    kayit.cizgi(ax, [p0, p1], "AKS")
    metinler = []
    for p in (p0, p1):
        ax.annotate("", xy=(p[0] + yon[0] * 0.9, p[1] + yon[1] * 0.9), xytext=p,
                    arrowprops=dict(arrowstyle="-|>", color=renk, lw=1.0, mutation_scale=8), zorder=10)
        dx = 0.55 if p is p1 else -0.55
        if abs(p1[0] - p0[0]) < 1e-6:     # düşey kesit çizgisi → harf yukarıda/aşağıda
            dzp = 0.6 if p[1] >= max(p0[1], p1[1]) else -0.6
            metinler.append(ax.text(p[0] - 0.55, p[1] + dzp, harf, fontsize=yazi, fontweight="bold", color=renk,
                                    ha="center", va="center", zorder=10))
        else:
            metinler.append(ax.text(p[0] + dx, p[1], harf, fontsize=yazi, fontweight="bold", color=renk, ha="center",
                                    va="center", zorder=10))
        kayit.yazi(ax, p[0] - 0.55, p[1], harf, yazi, "AKS")
    return metinler


# =============================================================================
# Pafta öğeleri: başlık, künye, lejant, kuzey-güneş-kıble diyagramı, tablo
# =============================================================================
def baslik(fig, metin, alt):
    t1 = fig.text(14 / PAFTA_MM[0], 1 - 14 / PAFTA_MM[1], metin, fontsize=19, fontweight="bold", color=YAZI, va="top")
    t2 = fig.text(14 / PAFTA_MM[0], 1 - 25.5 / PAFTA_MM[1], alt, fontsize=9, color=YAZI2, va="top")
    return [t1, t2]


def kunye(fig, x_mm, y_mm, w_mm, kod, tarih="27.10.2026"):
    ax = mm_eksen(fig, x_mm, y_mm, w_mm, 24)
    ax.add_patch(Rectangle((0, 0), w_mm, 24, fc="none", ec=YAZI2, lw=0.6))
    ax.plot([0, w_mm], [12, 12], color=YAZI2, lw=0.4)
    ax.plot([w_mm * 0.55, w_mm * 0.55], [0, 24], color=YAZI2, lw=0.4)
    m = [ax.text(2, 18, "TR TAMİRAT · Faz 4 · Rapor 2", fontsize=6.8, fontweight="bold", va="center"),
         ax.text(2, 6, "Fıtrata uygun konut rehberi", fontsize=6.3, color=YAZI2, va="center"),
         ax.text(w_mm * 0.55 + 2, 18, f"Pafta {kod} · Ölçek 1/100 (A1)", fontsize=6.8, fontweight="bold", va="center"),
         ax.text(w_mm * 0.55 + 2, 6, f"{tarih} · CC BY 4.0", fontsize=6.3, color=YAZI2, va="center")]
    return m


def lejant(fig, x_mm, y_mm, w_mm, turler, ek=()):
    """Oda renkleri ve semboller. turler: kullanılan oda türleri."""
    n = len(turler) + len(ek)
    sutun = 2
    satir = math.ceil(n / sutun)
    h = 7 + satir * 5.2
    ax = mm_eksen(fig, x_mm, y_mm, w_mm, h)
    m = [ax.text(0, h - 2, "Lejant", fontsize=7.5, fontweight="bold", va="center")]
    ogeler = [(ODA_RENK[t], TUR_AD[t], "kutu") for t in turler] + list(ek)
    for k, (renk, ad, tip) in enumerate(ogeler):
        c, r = k % sutun, k // sutun
        x = c * w_mm / sutun
        y = h - 8 - r * 5.2
        if tip == "kutu":
            ax.add_patch(Rectangle((x, y - 1.6), 5, 3.2, fc=renk, ec=YAZI2, lw=0.3))
        elif tip == "cizgi":
            ax.plot([x, x + 5], [y, y], color=renk, lw=1.0, ls=(0, (2.5, 1.5)))
        elif tip == "duvar":
            ax.add_patch(Rectangle((x, y - 1.6), 5, 3.2, fc=DUVAR, ec="none"))
        elif tip == "pencere":
            ax.add_patch(Rectangle((x, y - 1.0), 5, 2.0, fc=BOSLUK, ec=DUVAR, lw=0.4))
            ax.plot([x, x + 5], [y, y], color=MAVI, lw=0.8)
        elif tip == "yuksek":
            ax.add_patch(Rectangle((x, y - 1.0), 5, 2.0, fc=BOSLUK, ec=DUVAR, lw=0.4))
            ax.plot([x, x + 5], [y, y], color=MAVI, lw=0.8, ls=(0, (2.5, 1.5)))
        elif tip == "agac":
            ax.add_patch(Circle((x + 2.5, y), 1.7, fc=ton(AQUA, 0.55), ec=ton(AQUA, 0.1), lw=0.4))
        elif tip == "kible":
            ax.annotate("", xy=(x + 5, y), xytext=(x, y), arrowprops=dict(arrowstyle="-|>", color=AQUA, lw=0.9,
                                                                         mutation_scale=7))
        elif tip == "baca":
            ax.add_patch(Rectangle((x + 1, y - 1.5), 3, 3, fc="none", ec=YAZI2, lw=0.4))
            ax.plot([x + 1, x + 4], [y - 1.5, y + 1.5], color=YAZI2, lw=0.3)
            ax.plot([x + 1, x + 4], [y + 1.5, y - 1.5], color=YAZI2, lw=0.3)
        m.append(ax.text(x + 6.5, y, ad, fontsize=5.9, va="center", color=YAZI))
    return m, h


def yon_diyagrami(fig, x_mm, y_mm, d_mm, enlem, sehir, kible_az, gunler):
    """Kuzey oku, 21 Haziran ve 21 Aralık güneş doğuş-batış yönleri, öğle yüksekliği ve kıble."""
    from veri import dogus_azimutu, ogle_yuksekligi
    ax = mm_eksen(fig, x_mm, y_mm, d_mm, d_mm)
    c = d_mm / 2
    R = d_mm * 0.34
    m = []
    ax.add_patch(Circle((c, c), R, fc="none", ec=YAZI2, lw=0.5))
    for a in range(0, 360, 30):
        r0 = R * (0.92 if a % 90 else 0.85)
        ax.plot([c + r0 * math.sin(math.radians(a)), c + R * math.sin(math.radians(a))],
                [c + r0 * math.cos(math.radians(a)), c + R * math.cos(math.radians(a))], color=YAZI2, lw=0.4)
    ax.annotate("", xy=(c, c + R * 1.12), xytext=(c, c - R * 0.25),
                arrowprops=dict(arrowstyle="-|>", color=YAZI, lw=1.3, mutation_scale=12))
    m.append(ax.text(c, c + R * 1.25, "K", ha="center", va="bottom", fontsize=9, fontweight="bold"))
    for (ad, gun, renk) in gunler:
        dg = dogus_azimutu(enlem, gun)
        for az in (dg, 360 - dg):
            ax.plot([c, c + R * 0.98 * math.sin(math.radians(az))], [c, c + R * 0.98 * math.cos(math.radians(az))],
                    color=renk, lw=1.0, ls=(0, (3, 1.5)))
        ax.add_patch(Arc((c, c), 2 * R * 0.98, 2 * R * 0.98, theta1=90 - (360 - dg), theta2=90 - dg, color=renk, lw=1.6))
    ax.annotate("", xy=(c + R * 0.95 * math.sin(math.radians(kible_az)), c + R * 0.95 * math.cos(math.radians(kible_az))),
                xytext=(c, c), arrowprops=dict(arrowstyle="-|>", color=AQUA, lw=1.4, mutation_scale=10))
    satirlar = [f"{sehir} · {sayi(enlem, 1)}° K", f"Kıble {sayi(kible_az, 0)}°"]
    for (ad, gun, renk) in gunler:
        satirlar.append(f"{ad}: doğuş {sayi(dogus_azimutu(enlem, gun), 0)}°, öğle {sayi(ogle_yuksekligi(enlem, gun), 1)}°")
    m.append(ax.text(c, c - R * 1.12, "\n".join(satirlar), ha="center", va="top", fontsize=5.8, color=YAZI2,
                     linespacing=1.25))
    return m


def tablo_ciz(fig, x_mm, y_mm, w_mm, basliklar, satirlar, sutun_x, baslik_metin=None, yazi=6.0, satir_h=4.2,
              kalin_satirlar=(), hizalar=None, alt_not=None):
    """mm ızgaralı tablo. sutun_x: sütun başlangıçları (mm, tablo içinde). Dönüş: (metinler, yükseklik)."""
    n = len(satirlar)
    h = (6.5 if baslik_metin else 0) + satir_h * (n + 1) + 1.5 + (4.5 * (alt_not.count("\n") + 1) if alt_not else 0)
    ax = mm_eksen(fig, x_mm, y_mm, w_mm, h)
    m = []
    y = h
    if baslik_metin:
        m.append(ax.text(0, y - 2.5, baslik_metin, fontsize=7.5, fontweight="bold", va="center"))
        y -= 6.5
    hizalar = hizalar or ["left"] * len(basliklar)

    def _x(k):
        if hizalar[k] == "right":
            return (sutun_x[k + 1] - 1.2) if k + 1 < len(sutun_x) else (w_mm - 0.5)
        return sutun_x[k]

    for k, b in enumerate(basliklar):
        m.append(ax.text(_x(k), y - satir_h / 2, b, fontsize=yazi, fontweight="bold", va="center", ha=hizalar[k],
                         color=YAZI2))
    y -= satir_h
    ax.plot([0, w_mm], [y, y], color=YAZI2, lw=0.6)
    for i, s in enumerate(satirlar):
        if i % 2 == 0:
            ax.add_patch(Rectangle((0, y - satir_h), w_mm, satir_h, fc="#f1f0ec", ec="none"))
        kalin = i in kalin_satirlar
        for k, v in enumerate(s):
            m.append(ax.text(_x(k), y - satir_h / 2, str(v), fontsize=yazi, va="center", ha=hizalar[k],
                             fontweight="bold" if kalin else "normal"))
        y -= satir_h
    ax.plot([0, w_mm], [y, y], color=YAZI2, lw=0.4)
    if alt_not:
        m.append(ax.text(0, y - 1.2, alt_not, fontsize=yazi - 0.6, va="top", color=YAZI2, linespacing=1.25))
    return m, h


def metin_kutusu(fig, x_mm, y_mm, w_mm, baslik_metin, satirlar, yazi=6.0, satir_h=3.6):
    h = 6 + satir_h * sum(s.count("\n") + 1 for s in satirlar) + 1
    ax = mm_eksen(fig, x_mm, y_mm, w_mm, h)
    m = [ax.text(0, h - 2.5, baslik_metin, fontsize=7.5, fontweight="bold", va="center")]
    y = h - 6.5
    for s in satirlar:
        m.append(ax.text(0, y, s, fontsize=yazi, va="top", linespacing=1.3))
        y -= satir_h * (s.count("\n") + 1)
    return m, h


def olcek_cubugu(ax, kayit, x, y, n=5, adim=1.0, h=0.18, yazi=5.8):
    m = []
    for i in range(n):
        ax.add_patch(Rectangle((x + i * adim, y), adim, h, fc=YAZI if i % 2 == 0 else ZEMIN, ec=YAZI, lw=0.5, zorder=9))
        kayit.poligon(ax, box(x + i * adim, y, x + (i + 1) * adim, y + h), "OLCU")
    for i in range(0, n + 1, max(1, n // 5)):
        m.append(ax.text(x + i * adim, y - 0.15, f"{i * adim:g}" + (" m" if i == n else ""), ha="center", va="top",
                         fontsize=yazi, zorder=9))
    if n % max(1, n // 5):
        m.append(ax.text(x + n * adim, y - 0.15, f"{n * adim:g} m", ha="center", va="top", fontsize=yazi, zorder=9))
    return m


def plan_basligi(ax, metin, x, y, yazi=8.5, alt=None):
    t = [ax.text(x, y, metin, fontsize=yazi, fontweight="bold", ha="left", va="bottom", zorder=10)]
    if alt:
        t.append(ax.text(x, y - 0.25, alt, fontsize=yazi - 2.3, color=YAZI2, ha="left", va="top", zorder=10))
    return t


# =============================================================================
# Etiket çakışma denetimi
# =============================================================================
def cakisma_denetle(fig, ad, tolerans=0.5):
    """Bütün metinlerin pencere kutularını karşılaştırır; çakışan çiftleri ve sayfa dışına taşanları döndürür.
    Ayrıca oda etiketinin net oda poligonundan taşmasını denetler."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    metinler = []
    for t in fig.texts:
        if t.get_visible() and t.get_text().strip():
            metinler.append(t)
    for ax in fig.axes:
        for t in ax.texts:
            if t.get_visible() and t.get_text().strip():
                metinler.append(t)
    kutular = []
    for t in metinler:
        try:
            bb = t.get_window_extent(renderer=r)
        except Exception:
            continue
        kutular.append((t, bb))
    W, H = fig.bbox.width, fig.bbox.height
    sorunlar = []
    for i in range(len(kutular)):
        t1, b1 = kutular[i]
        if b1.x0 < -1 or b1.y0 < -1 or b1.x1 > W + 1 or b1.y1 > H + 1:
            sorunlar.append(("taşma", t1.get_text()[:40], ""))
        for j in range(i + 1, len(kutular)):
            t2, b2 = kutular[j]
            ix = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
            iy = min(b1.y1, b2.y1) - max(b1.y0, b2.y0)
            if ix > tolerans and iy > tolerans:
                sorunlar.append(("çakışma", t1.get_text()[:40].replace("\n", " / "), t2.get_text()[:40].replace("\n", " / ")))
    # oda etiketi oda içinde mi?
    for t, bb in kutular:
        o = getattr(t, "_oda", None)
        if o is None:
            continue
        ax = t.axes
        inv = ax.transData.inverted()
        (x0, y0), (x1, y1) = inv.transform((bb.x0, bb.y0)), inv.transform((bb.x1, bb.y1))
        kutu = box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        if not o.net.buffer(0.04).contains(kutu):
            sorunlar.append(("oda dışı", o.ad.replace("\n", " "), f"{sayi(kutu.difference(o.net).area, 2)} m² taşıyor"))
    if sorunlar:
        print(f"  [{ad}] {len(sorunlar)} etiket sorunu:")
        for s in sorunlar[:40]:
            print("    ", s)
    else:
        print(f"  [{ad}] etiket çakışması yok ({len(kutular)} metin)")
    return sorunlar


def kaydet(fig, kayit, ad):
    sorun = cakisma_denetle(fig, ad)
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"{ad}.{uz}", facecolor=ZEMIN, dpi=150)
    dxf = kayit.yaz(CIKTI / f"{ad}.dxf") if kayit is not None else False
    plt.close(fig)
    return sorun, dxf
