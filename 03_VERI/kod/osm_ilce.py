"""
OpenStreetMap'ten ilçe bazında yeşil alan erişimi ve yürünebilirlik
=================================================================
Girdi : 03_VERI/ham/osm/turkey-latest.osm.pbf (Geofabrik)
        03_VERI/ham/ghsl/tif/GHS_POP_* (nüfus, 100 m), 03_VERI/islenmis/ilce_paneli.gpkg (sınırlar)
Çıktı : 03_VERI/islenmis/osm_yesil_alanlar.gpkg (≥0,5 ha kamusal yeşil alanlar)
        03_VERI/islenmis/osm_kavsaklar.parquet, osm_noktalar.parquet (cami, okul)
        03_VERI/islenmis/ilce_osm.csv

Tanımlar
  Kamusal yeşil alan : leisure=park|recreation_ground|playground|common|garden(access≠private),
                       landuse=recreation_ground|village_green; ≥0,5 ha (DSÖ ölçütü). nature_reserve ayıklanır.
  Yeşil erişim       : nüfusun (GHS-POP 2020) ≥0,5 ha yeşil alana 300 m (kuş uçuşu) içinde olan payı
  Kavşak             : yaya-araç sokak ağında derecesi ≥3 olan düğüm (motorway/trunk/service/footway/path hariç)
  Kavşak yoğunluğu   : kavşak / yapılı alan km² (GHSL bina yüksekliği > 0 olan hücreler)
"""
import glob
import sys
from array import array
from pathlib import Path

import geopandas as gpd
import numpy as np
import osmium
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window, transform as win_transform
from scipy.ndimage import distance_transform_edt
from shapely import wkb

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
PBF = KOK / "03_VERI" / "ham" / "osm" / "turkey-latest.osm.pbf"
IS = KOK / "03_VERI" / "islenmis"
TIF = KOK / "03_VERI" / "ham" / "ghsl" / "tif"

YOL = {"primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link",
       "unclassified", "residential", "living_street", "pedestrian"}
LEISURE = {"park", "recreation_ground", "playground", "common", "garden", "nature_reserve"}
LANDUSE = {"recreation_ground", "village_green"}
KENTSEL = {"park", "garden", "playground", "recreation_ground", "common", "village_green"}
wkbf = osmium.geom.WKBFactory()


class Isleyici(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.nid, self.w, self.lon, self.lat = array("q"), array("b"), array("d"), array("d")
        self.yesil, self.nokta = [], []

    def way(self, w):
        hw = w.tags.get("highway")
        if hw not in YOL or w.tags.get("area") == "yes":
            return
        n = len(w.nodes)
        if n < 2:
            return
        for i, nd in enumerate(w.nodes):
            if not nd.location.valid():
                continue
            self.nid.append(nd.ref)
            self.w.append(1 if i in (0, n - 1) else 2)
            self.lon.append(nd.location.lon)
            self.lat.append(nd.location.lat)

    def area(self, a):
        t = a.tags
        le, lu = t.get("leisure"), t.get("landuse")
        if (le in LEISURE and not (le == "garden" and t.get("access") in ("private", "no"))) or lu in LANDUSE:
            try:
                self.yesil.append((wkb.loads(wkbf.create_multipolygon(a), hex=True), le or lu, t.get("name", "")))
            except Exception:
                pass
        am = t.get("amenity")
        if am in ("place_of_worship", "school"):
            try:
                g = wkb.loads(wkbf.create_multipolygon(a), hex=True).representative_point()
                self.nokta.append((g.x, g.y, am, t.get("religion", "")))
            except Exception:
                pass

    def node(self, n):
        am = n.tags.get("amenity")
        if am in ("place_of_worship", "school"):
            self.nokta.append((n.location.lon, n.location.lat, am, n.tags.get("religion", "")))


if not (IS / "osm_kavsaklar.parquet").exists():  # PBF okuması uzun; ara çıktılar varsa yeniden kullan
    print("PBF okunuyor:", PBF, round(PBF.stat().st_size / 1e6), "MB")
    h = Isleyici()
    h.apply_file(str(PBF), locations=True, idx="flex_mem")
    print("yol düğüm kaydı:", len(h.nid), "| yeşil alan:", len(h.yesil), "| nokta:", len(h.nokta))

    # kavşaklar
    nid = np.frombuffer(h.nid, dtype=np.int64)
    w = np.frombuffer(h.w, dtype=np.int8).astype(np.int32)
    lon, lat = np.frombuffer(h.lon), np.frombuffer(h.lat)
    sira = np.argsort(nid, kind="stable")
    nid_s = nid[sira]
    uniq, ilk, say = np.unique(nid_s, return_index=True, return_counts=True)
    derece = np.add.reduceat(w[sira], ilk)
    kav = derece >= 3
    kav_idx = sira[ilk[kav]]
    kavsak = pd.DataFrame({"lon": lon[kav_idx], "lat": lat[kav_idx], "derece": derece[kav]})
    kavsak.to_parquet(IS / "osm_kavsaklar.parquet")
    print("kavşak:", len(kavsak))
    del h.nid, h.w, h.lon, h.lat

    yesil = gpd.GeoDataFrame(h.yesil, columns=["geometry", "tur", "ad"], crs=4326).to_crs("ESRI:54009")
    yesil["ha"] = yesil.area / 1e4
    yesil = yesil[yesil.ha >= 0.5].reset_index(drop=True)
    yesil.to_file(IS / "osm_yesil_alanlar.gpkg", driver="GPKG")
    pd.DataFrame(h.nokta, columns=["lon", "lat", "amenity", "religion"]).to_parquet(IS / "osm_noktalar.parquet")
    print("≥0,5 ha yeşil alan:", len(yesil), "| toplam ha:", round(yesil.ha.sum()))

kavsak = pd.read_parquet(IS / "osm_kavsaklar.parquet")
yesil = gpd.read_file(IS / "osm_yesil_alanlar.gpkg")
# doğa koruma alanları (nature_reserve) kentsel, kullanılabilir yeşil alan sayılmaz; çok büyük alanlar erişimi şişirir
yesil = yesil[yesil.tur.isin(KENTSEL)].reset_index(drop=True)
print("kentsel yeşil alan (≥0,5 ha):", len(yesil), "| toplam ha:", round(yesil.ha.sum()))

# ilçe sınırları ve etiket rasterı ile toplama
ilce = gpd.read_file(IS / "ilce_paneli.gpkg")[["ilce_kod", "geometry"]]
ilce["gid"] = np.arange(1, len(ilce) + 1)
ilce54 = ilce.to_crs("ESRI:54009")
N = len(ilce) + 1
acc = {k: np.zeros(N) for k in ["pop", "pop_yesil300", "yapili", "yesil_hucre"]}
for pf in sorted(glob.glob(str(TIF / "GHS_POP_*" / "*.tif"))):
    karo = pf.split("_V1_0_")[-1].replace(".tif", "")
    hf = glob.glob(str(TIF / f"GHS_BUILT_H_*{karo}" / "*.tif"))[0]
    with rasterio.open(pf) as rp, rasterio.open(hf) as rh:
        alt = ilce54.cx[rp.bounds.left:rp.bounds.right, rp.bounds.bottom:rp.bounds.top]
        if alt.empty:
            continue
        geoms = list(zip(alt.geometry, alt.gid))
        B, PAY = 2500, 4  # 4 hücre (400 m) bindirme: 300 m mesafe pencere kenarında kesilmesin
        for r0 in range(0, rh.height, B):
            for c0 in range(0, rh.width, B):
                r1, c1 = max(0, r0 - PAY), max(0, c0 - PAY)
                r2, c2 = min(rh.height, r0 + B + PAY), min(rh.width, c0 + B + PAY)
                win = Window(c1, r1, c2 - c1, r2 - r1)
                tr = win_transform(win, rh.transform)
                shp = (int(win.height), int(win.width))
                lab = rasterize(geoms, out_shape=shp, transform=tr, fill=0, dtype="int32")
                if not lab.any():
                    continue
                p = rp.read(1, window=win).astype("float64")
                hh = rh.read(1, window=win).astype("float64")
                p[p < 0] = 0
                hh[(hh >= 255) | (hh < 0)] = 0
                bx = rasterio.windows.bounds(win, rh.transform)
                ys = yesil.cx[bx[0] - 400:bx[2] + 400, bx[1] - 400:bx[3] + 400]
                if len(ys):
                    ym = rasterize(((g, 1) for g in ys.geometry), out_shape=shp, transform=tr, fill=0, dtype="uint8", all_touched=True)
                    mesafe = distance_transform_edt(ym == 0) * 100
                else:
                    ym = np.zeros(shp, dtype="uint8")
                    mesafe = np.full(shp, 1e9)
                ic = np.zeros(shp, bool)
                ic[(r0 - r1):(r0 - r1) + min(B, rh.height - r0), (c0 - c1):(c0 - c1) + min(B, rh.width - c0)] = True
                m = (lab > 0) & ic
                L = lab[m]
                acc["pop"] += np.bincount(L, p[m], N)
                acc["pop_yesil300"] += np.bincount(L, p[m] * (mesafe[m] <= 300), N)
                acc["yapili"] += np.bincount(L, (hh[m] > 0).astype(float), N)
                acc["yesil_hucre"] += np.bincount(L, ym[m].astype(float), N)
    print("karo işlendi:", karo)

g = pd.DataFrame({k: v[1:] for k, v in acc.items()})
g["gid"] = np.arange(1, N)
kp = gpd.GeoDataFrame(kavsak, geometry=gpd.points_from_xy(kavsak.lon, kavsak.lat), crs=4326).to_crs("ESRI:54009")
kj = gpd.sjoin(kp[["geometry"]], ilce54[["gid", "geometry"]], predicate="within")
g = g.merge(kj.groupby("gid").size().rename("kavsak").reset_index(), on="gid", how="left").fillna({"kavsak": 0})
noktalar = pd.read_parquet(IS / "osm_noktalar.parquet")
npg = gpd.GeoDataFrame(noktalar, geometry=gpd.points_from_xy(noktalar.lon, noktalar.lat), crs=4326).to_crs("ESRI:54009")
nj = gpd.sjoin(npg, ilce54[["gid", "geometry"]], predicate="within")
g = g.merge(nj[nj.amenity == "place_of_worship"].groupby("gid").size().rename("ibadethane").reset_index(), on="gid", how="left")
g = g.merge(nj[nj.amenity == "school"].groupby("gid").size().rename("okul").reset_index(), on="gid", how="left")
g = g.fillna({"ibadethane": 0, "okul": 0})
with np.errstate(divide="ignore", invalid="ignore"):
    g["yesil300_pay"] = 100 * g.pop_yesil300 / g["pop"]
    g["kavsak_km2_yapili"] = g.kavsak / (g.yapili / 100)
    g["yesil_m2_kisi"] = g.yesil_hucre * 1e4 / g["pop"]
out = ilce[["gid", "ilce_kod"]].merge(g, on="gid").drop(columns="gid")
out.to_csv(IS / "ilce_osm.csv", index=False, encoding="utf-8")
print(out.describe().T[["mean", "50%", "min", "max"]].round(2))
print("ağırlıklı yeşil erişim (Türkiye):", round(100 * out.pop_yesil300.sum() / out["pop"].sum(), 1), "%")
