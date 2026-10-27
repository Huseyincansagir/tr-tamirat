"""
Model mahalle v2.1 — geleneksel doku ölçütleriyle ölçüm ve figür–zemin paftası
=============================================================================
03_VERI/kod/morfoloji_olcum.py'nin ölçüt fonksiyonları (olc, model_veri) içe aktarılır; o dosya
değiştirilmez. Model aynı 600 × 600 m pencereyle (x 100–700, y 75–675 m; M1) ve tam 60 ha ile (M0)
ölçülür. v2.0 ayrı bir süreçte (MM_SURUM=2.0) aynı kodla ölçülür; v1 ve gerçek alanlar
05_ANALIZ/sonuclar/morfoloji_karsilastirma.csv'den okunur.

Çıktılar:  ../morfoloji_olcum_v2.csv   (v1, v2.0, v2.1 satırları; ölçüt sütunları betikle aynı)
           ../figur_zemin_v2_1.png|svg  (Zeyrek, Beypazarı, Başakşehir, model v1, v2.0, v2.1; aynı ölçek)

Not: ölçüt betiği kat yüksekliğini 3,0 m alır (H/W); v2'nin 3,1 m'lik katıyla gerçek H/W ≈ %3 daha yüksektir.
"""

import os
import pickle
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np

KOD = Path(__file__).resolve().parent
KOK = KOD.parents[2]
MORF_KOD = KOK / "03_VERI" / "kod"
MORF_CSV = KOK / "05_ANALIZ" / "sonuclar" / "morfoloji_karsilastirma.csv"
GPKG = KOK / "03_VERI" / "islenmis" / "morfoloji_alanlar.gpkg"
PENCERE = {"M1": (100.0, 75.0, 700.0, 675.0), "M0": (0.0, 0.0, 800.0, 750.0)}
GERCEK = ["G4", "G3", "C2"]           # paftadaki gerçek alanlar: Zeyrek, Beypazarı, Başakşehir

# raporda ve CSV'de karşılaştırılan ölçütler: (sütun, ad, birim, çarpan, ondalık)
OLCUTLER = [
    ("bina_ha", "Bina", "/ha", 1, 1),
    ("taban_medyan_m2", "Bina tabanı (medyan)", "m²", 1, 0),
    ("yapi_oturumu", "Yapı oturumu (brüt)", "%", 100, 0),
    ("net_yapi_oturumu", "Net yapı oturumu (ada içi)", "%", 100, 0),
    ("emsal", "Emsal (brüt)", "", 1, 2),
    ("kat_ort", "Ortalama kat", "", 1, 1),
    ("kisi_ha", "Nüfus", "kişi/ha", 1, 0),
    ("kavsak_km2_sokak", "Kavşak (yaya dahil)", "/km²", 1, 0),
    ("kavsak_km2_arac", "Kavşak (araç)", "/km²", 1, 0),
    ("ada_alan_medyan_m2", "Yaya adası (medyan)", "ha", 1e-4, 2),
    ("ada_cevre_medyan_m", "Yaya adası çevresi (medyan)", "m", 1, 0),
    ("ada_arac_alan_medyan_m2", "Araç adası (medyan)", "ha", 1e-4, 2),
    ("cephe_arasi_medyan_m", "Cephe arası (medyan)", "m", 1, 1),
    ("hw_medyan", "H/W (medyan)", "", 1, 2),
    ("cephe_adimi_m", "Cephe adımı", "m", 1, 0),
    ("bina_cephe_medyan_m", "Bina cephesi (medyan)", "m", 1, 0),
    ("kapali_avlu_ha", "Kapalı avlu", "/ha", 1, 2),
    ("kapali_avlu_medyan_m2", "Kapalı avlu (medyan)", "m²", 1, 0),
    ("ada_ici_bos_pay_net", "Ada içi yapısız (net)", "%", 100, 0),
    ("kamusal_yesil_m2_kisi", "Kamusal yeşil", "m²/kişi", 1, 1),
    ("yakinlik_bina_400", "400 m'de ulaşılan bina", "", 1, 0),
    ("ag_verimi_400", "Ağ verimi (400 m)", "", 1, 2),
]


def _mo():
    if str(MORF_KOD) not in sys.path:
        sys.path.insert(0, str(MORF_KOD))
    import morfoloji_olcum as mo          # yalnız içe aktarılır; dosya değişmez
    mo.MODEL_KOD = KOD                    # model_veri() v2 plan modelini okusun
    return mo


def olc_model():
    """Geçerli sürümün (MM_SURUM) M1 ve M0 ölçümleri + M1 penceresindeki bina poligonları."""
    import shapely
    from shapely.geometry import box

    sys.path.insert(0, str(KOD))
    import plan_modeli as pm              # noqa: F401  (model_veri aynı modülü kullanır)
    mo = _mo()
    Bm, Ym, yesil = mo.model_veri()
    out = {}
    for kod, p in PENCERE.items():
        a = dict(kod=kod, ad=kod, S=box(*p))
        c = Bm.geometry.representative_point()
        icS = shapely.contains_xy(a["S"], c.x.values, c.y.values)
        nufus = float(Bm.loc[icS, "kisi"].sum())
        r, katman = mo.olc(a, Bm, Ym, None, yesil, None, nufus, mo.MODEL_HANE)
        r.pop("yon_hist", None)
        out[kod] = r
    S = box(*PENCERE["M1"])
    out["_bina_M1"] = [g.intersection(S) for g in Bm.geometry.values if g.intersects(S)]
    return out


@lru_cache(maxsize=1)
def v20_olcum():
    """v2.0'ı ayrı süreçte (MM_SURUM=2.0) ölçer."""
    with tempfile.TemporaryDirectory() as t:
        yol = Path(t) / "v20.pkl"
        env = dict(os.environ, MM_SURUM="2.0", PYTHONIOENCODING="utf-8")
        kod = ("import sys, pickle; sys.dont_write_bytecode = True; sys.path.insert(0, sys.argv[1]); "
               "import morfoloji_v2 as m; pickle.dump(m.olc_model(), open(sys.argv[2], 'wb'))")
        subprocess.run([sys.executable, "-c", kod, str(KOD), str(yol)], check=True, cwd=t, env=env,
                       stdout=subprocess.DEVNULL)
        with open(yol, "rb") as f:
            return pickle.load(f)


@lru_cache(maxsize=1)
def tum_olcumler():
    import pandas as pd

    d = pd.read_csv(MORF_CSV)
    satir = []
    for _, r in d.iterrows():
        satir.append(dict(r))
    v21 = olc_model()
    v20 = v20_olcum()
    for surum, o in (("v2.0", v20), ("v2.1", v21)):
        for kod in ("M1", "M0"):
            s = dict(kod=f"{kod}_{surum}", ad=f"Model mahalle {surum} ({'600 m pencere' if kod == 'M1' else 'tam 60 ha'})",
                     kisa=f"Model {surum} ({'600 m' if kod == 'M1' else '60 ha'})", grup="model")
            s.update(o[kod])
            satir.append(s)
    df = pd.DataFrame(satir)
    return df, v20["_bina_M1"], v21["_bina_M1"]


def grup_medyani(df, grup):
    g = df[(df.grup == grup) & (df.get("sokak_guvensiz").astype(str) != "True") & (df.get("kat_suphe").astype(str) != "True")]
    return g


def csv_yaz():
    from ortak import CIKTI
    df, _, _ = tum_olcumler()
    sutun = ["kod", "ad", "kisa", "grup"] + [c for c in df.columns if c not in ("kod", "ad", "kisa", "grup")]
    df[sutun].to_csv(CIKTI / "morfoloji_olcum_v2.csv", index=False, encoding="utf-8", float_format="%.4f")
    return df


def ozet():
    """metrikler.py için: {ölçüt: {v1, v2.0, v2.1, geleneksel medyan, çağdaş medyan}} (M1 penceresi)."""
    df, _, _ = tum_olcumler()
    sat = {k: df[df.kod == k].iloc[0] for k in ("M1", "M1_v2.0", "M1_v2.1", "M0", "M0_v2.0", "M0_v2.1")}
    # raporla aynı kural (§2): sokak ölçütlerinde * (sokak ağı güvensiz), kat ölçütlerinde ‡ (kat şüpheli) işaretli
    # alanlar grup medyanına katılmaz; H/W'de ikisi de
    sok = df.sokak_guvensiz.astype(str) != "True"
    kat = df.kat_suphe.astype(str) != "True"
    SOKAK = {"kavsak_km2_sokak", "kavsak_km2_arac", "ada_alan_medyan_m2", "ada_cevre_medyan_m", "ada_arac_alan_medyan_m2",
             "cephe_arasi_medyan_m", "cephe_adimi_m", "bina_cephe_medyan_m", "yakinlik_bina_400", "ag_verimi_400",
             "ada_ici_bos_pay_net", "net_yapi_oturumu"}
    KAT = {"emsal", "kat_ort"}
    out = {}
    for c, ad, birim, carpan, ond in OLCUTLER:
        m = sok & kat if c == "hw_medyan" else (sok if c in SOKAK else (kat if c in KAT else sok | True))
        gel = df[(df.grup == "geleneksel") & m]
        cag = df[(df.grup == "çağdaş") & m]
        out[c] = dict(ad=ad, birim=birim, carpan=carpan, ond=ond,
                      v1=sat["M1"].get(c), v20=sat["M1_v2.0"].get(c), v21=sat["M1_v2.1"].get(c),
                      v1_60=sat["M0"].get(c), v20_60=sat["M0_v2.0"].get(c), v21_60=sat["M0_v2.1"].get(c),
                      gel=float(np.nanmedian(gel[c].astype(float))), cag=float(np.nanmedian(cag[c].astype(float))))
    return out


# =============================================================================
# Figür–zemin paftası
# =============================================================================
def pafta():
    import geopandas as gpd
    import matplotlib.pyplot as plt
    import shapely
    from matplotlib.patches import PathPatch, Rectangle
    from matplotlib.path import Path as MPath
    from shapely.geometry import box

    from ortak import CIKTI, sayi
    import v1_okuyucu as v1

    mo = _mo()
    df, b20, b21 = tum_olcumler()
    paneller = []
    # gerçek alanlar: GPKG binaları (EPSG:4326) → alanın UTM'i
    G = gpd.read_file(GPKG, layer="binalar")
    for kod in GERCEK:
        r = df[df.kod == kod].iloc[0]
        a = mo.alan_hazirla(dict(lat=float(r.lat), lon=float(r.lon)))
        g = G[G.alan_kod == kod].to_crs(a["epsg"])
        S = a["S"]
        geoms = [x.intersection(S) for x in g.geometry.values if x is not None and x.intersects(S)]
        x0, y0, _, _ = S.bounds
        geoms = [shapely.affinity.translate(x, -x0, -y0) for x in geoms]
        paneller.append((kod, r, geoms, box(0, 0, 600, 600)))
    # model v1 (M1 penceresi): v1 geometrisi
    g1 = v1.v1_geometri()
    S1 = box(*PENCERE["M1"])
    v1g = []
    for p in g1["parseller"]:
        for b in p["binalar"] + ([p["genisleme"]] if p.get("genisleme") is not None else []):
            if b.intersects(S1):
                v1g.append(b.intersection(S1))
    for d in g1["donatilar"]:
        for b in d["binalar"]:
            if b.intersects(S1):
                v1g.append(b.intersection(S1))
    for kod, geoms in (("M1", v1g), ("M1_v2.0", b20), ("M1_v2.1", b21)):
        r = df[df.kod == kod].iloc[0]
        geoms = [shapely.affinity.translate(x, -PENCERE["M1"][0], -PENCERE["M1"][1]) for x in geoms]
        paneller.append((kod, r, geoms, box(0, 0, 600, 600)))

    ADLAR = {"G4": "Fatih Zeyrek (geleneksel)", "G3": "Beypazarı (geleneksel)", "C2": "Başakşehir (çağdaş)",
             "M1": "Model mahalle v1", "M1_v2.0": "Model mahalle v2.0", "M1_v2.1": "Model mahalle v2.1"}
    fig = plt.figure(figsize=(21, 16.6), dpi=150)
    gs = fig.add_gridspec(2, 3, hspace=0.32, wspace=0.06, left=0.02, right=0.98, top=0.885, bottom=0.085)
    for k, (kod, r, geoms, S) in enumerate(paneller):
        ax = fig.add_subplot(gs[k // 3, k % 3])
        ax.add_patch(Rectangle((0, 0), 600, 600, fc="#fcfcfb", ec="#8a877f", lw=0.6, zorder=0))
        verts, codes = [], []
        for g in geoms:
            for p in shapely.get_parts(g):
                if p.geom_type != "Polygon" or p.is_empty:
                    continue
                for halka in [p.exterior] + list(p.interiors):
                    xy = np.asarray(halka.coords)
                    verts.append(xy)
                    codes.append(np.r_[MPath.MOVETO, np.full(len(xy) - 2, MPath.LINETO), MPath.CLOSEPOLY])
        if verts:
            ax.add_patch(PathPatch(MPath(np.vstack(verts), np.concatenate(codes)), fc="#0b0b0b", ec="none", lw=0,
                                   zorder=2))
        ax.set_xlim(0, 600)
        ax.set_ylim(0, 600)
        ax.set_aspect("equal")
        ax.axis("off")
        renk = {"G": "#eb6834", "C": "#2a78d6", "M": "#0b0b0b"}[kod[0]]
        ax.add_patch(Rectangle((0, 606), 6, 22, fc=renk, ec="none", clip_on=False))
        ax.text(12, 617, ADLAR[kod], fontsize=12, fontweight="bold", va="center")
        deger = [("Bina", f"{sayi(r.bina_ha, 1)}/ha"), ("Yapı oturumu", f"%{sayi(100 * r.yapi_oturumu)}"),
                 ("Kavşak", f"{sayi(r.kavsak_km2_sokak)}/km²"), ("Yaya adası", f"{sayi(r.ada_alan_medyan_m2 / 1e4, 2)} ha"),
                 ("Cephe arası", f"{sayi(r.cephe_arasi_medyan_m, 1)} m"), ("H/W", sayi(r.hw_medyan, 2)),
                 ("Kapalı avlu", f"{sayi(r.kapali_avlu_ha, 2)}/ha"), ("Nüfus", f"{sayi(r.kisi_ha)} kişi/ha")]
        for j, (a_, v_) in enumerate(deger):
            xx = (j % 4) * 152
            yy = -40 - (j // 4) * 44
            ax.text(xx, yy, a_, fontsize=8, color="#52514e", clip_on=False)
            ax.text(xx, yy - 20, v_, fontsize=10.5, fontweight="bold", clip_on=False)
        if k == 0:
            for i, (a0, a1) in enumerate(((0, 50), (50, 100), (100, 200))):
                ax.add_patch(Rectangle((400 + a0, 8), a1 - a0, 6, fc="#0b0b0b" if i % 2 == 0 else "white", ec="#0b0b0b",
                                       lw=0.5, zorder=5))
            for v in (0, 100, 200):
                ax.text(400 + v, 18, f"{v}" + (" m" if v == 200 else ""), ha="center", fontsize=7, zorder=5,
                        bbox=dict(fc="white", ec="none", pad=0.5))
    fig.text(0.02, 0.968, "Figür–zemin: geleneksel doku, çağdaş doku ve model mahalle v1 → v2.1", fontsize=21,
             fontweight="bold")
    fig.text(0.02, 0.948,
             "Her pafta 600 × 600 m (36 ha), aynı ölçek, kuzey yukarıda. Ölçütler 03_VERI/kod/morfoloji_olcum.py'nin "
             "fonksiyonlarıyla hesaplandı (model: plan merkezli pencere x 100–700, y 75–675 m; kat yüksekliği betikteki gibi 3,0 m).\n"
             "Gerçek alanlar: OSM (Beypazarı'nda Microsoft ayak izi), GHS-POP 2020 (09_RAPORLAR/11_geleneksel_doku_morfolojisi.md). "
             "Model paftalarında bahçe duvarları bina sayılmaz; v2.1'de kapalı avlular güney sıra T3 gruplarıdır.",
             fontsize=10, color="#444", va="top")
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"figur_zemin_v2_1.{uz}", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(KOD))
    df = csv_yaz()
    o = ozet()
    for c, v in o.items():
        f = lambda x: "—" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x * v['carpan']:.{v['ond']}f}"
        print(f"{v['ad'][:30]:30s} v1 {f(v['v1']):>7s} · v2.0 {f(v['v20']):>7s} · v2.1 {f(v['v21']):>7s} · "
              f"gel. {f(v['gel']):>7s} · çağ. {f(v['cag']):>7s}")
    pafta()
    print("figur_zemin_v2_1.png|svg ve morfoloji_olcum_v2.csv yazıldı")
