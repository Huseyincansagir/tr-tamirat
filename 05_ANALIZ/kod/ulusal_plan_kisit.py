"""
Faz 4 · Ulusal mekânsal çerçeve — kısıt katmanları
================================================
Girdi : 03_VERI/islenmis/ulusal_altyapi/izgara_*.tif, diri_faylar_gem.gpkg, kiyi.gpkg, sulak_alanlar.gpkg,
        korunan_alanlar.gpkg, sanayi_alanlari.gpkg
Çıktı : 03_VERI/islenmis/ulusal_altyapi/izgara_kisit.tif  (uint16 bit maskesi; bitler aşağıda)
        05_ANALIZ/sonuclar/ulusal_plan_kisit_ozet.csv      katman başına alan, bugünkü nüfus ve sanayi alanı
        05_ANALIZ/sonuclar/ulusal_plan_kisit_il.csv        il başına kısıtsız ve yapılaşmaya elverişli arazi payı
Eşikler [V] (ulusal ölçekte tarama amaçlı; parsel kararı için değil):
  bit 0  fay_1km     GEM/EMME diri fay izine ≤ 1 km (1:1 milyon ölçekli izlerin konum belirsizliği ≈ 0,5–1 km)
  bit 1  fay_5km     diri fay izine ≤ 5 km (tehlikeli madde içeren sanayi için dikkat bandı)
  bit 2  ova_tarim   WorldCover tarım ≥ %50 ve eğim < %5 (nitelikli tarım arazisi vekili; 5403 s. Kanun sınıfları açık değil)
  bit 3  tarim       WorldCover tarım ≥ %50 (eğimden bağımsız)
  bit 4  sulak       WorldCover sulak ≥ %25 ya da OSM natural=wetland
  bit 5  su          WorldCover su ≥ %50 (göl, baraj, deniz kıyısı)
  bit 6  kiyi_500m   OSM kıyı çizgisine ≤ 500 m (3621 s. Kıyı Kanunu'nun 100 m sahil şeridi + kıyı ekosistemi)
  bit 7  orman       WorldCover ağaç ≥ %50 (yasal orman sınırı değil; OGM verisi açık değil)
  bit 8  taskin      JRC GloFAS 100 yıllık taşkın alanı hücrenin ≥ %25'i
  bit 9  korunan     OSM boundary=protected_area / leisure=nature_reserve (eksik kayıtlı)
  bit 10 dik         eğim > %20 (250 m üzerinden)
"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from scipy import ndimage

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
CIK = KOK / "03_VERI" / "islenmis" / "ulusal_altyapi"
SON = KOK / "05_ANALIZ" / "sonuclar"
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m +no_defs"
H = 250.0


def oku(ad, bant=1):
    with rasterio.open(CIK / ad) as d:
        return d.read(bant), d.transform


nuf, TR = oku("izgara_nufus.tif")
NY, NX = nuf.shape
ilc, _ = oku("izgara_ilce.tif")
kara = ilc > 0
anahtar = pd.read_csv(CIK / "izgara_ilce_anahtar.csv", dtype={"ilce_kod": str})
IL = np.array([""] + anahtar.il.tolist(), dtype=object)[ilc]
with rasterio.open(CIK / "izgara_ortu.tif") as d:
    ortu = {ad: d.read(i + 1).astype("float32") for i, ad in enumerate(["agac", "tarim", "yapili", "su", "sulak", "cayir"])}
for k in ortu:
    ortu[k][ortu[k] == 255] = np.nan
egim, _ = oku("izgara_egim.tif")
egim = np.where(egim == 65535, np.nan, egim / 10.0)
taskin, _ = oku("izgara_taskin.tif")


def rast(gdf, all_touched=True):
    g = gdf.to_crs(LCC)
    return rasterize(((x, 1) for x in g.geometry if x is not None and not x.is_empty), out_shape=(NY, NX), transform=TR,
                     fill=0, all_touched=all_touched, dtype="uint8").astype(bool)


def uzaklik(m):
    return ndimage.distance_transform_edt(~m) * H


fay = gpd.read_file(CIK / "diri_faylar_gem.gpkg")
d_fay = uzaklik(rast(fay))
d_kiyi = uzaklik(rast(gpd.read_file(CIK / "kiyi.gpkg")))
sulak_osm = rast(gpd.read_file(CIK / "sulak_alanlar.gpkg"), all_touched=False)
korunan = rast(gpd.read_file(CIK / "korunan_alanlar.gpkg"), all_touched=False)

K = {}
K["fay_1km"] = d_fay <= 1000
K["fay_5km"] = d_fay <= 5000
K["ova_tarim"] = (ortu["tarim"] >= 50) & (egim < 5)
K["tarim"] = ortu["tarim"] >= 50
K["sulak"] = (ortu["sulak"] >= 25) | sulak_osm
K["su"] = ortu["su"] >= 50
K["kiyi_500m"] = d_kiyi <= 500
K["orman"] = ortu["agac"] >= 50
K["taskin"] = np.nan_to_num(taskin) >= 25
K["korunan"] = korunan
K["dik"] = np.nan_to_num(egim) > 20
bit = np.zeros((NY, NX), dtype="uint16")
for i, (ad, m) in enumerate(K.items()):
    bit |= (m & kara).astype("uint16") << i
with rasterio.open(CIK / "izgara_kisit.tif", "w", driver="GTiff", width=NX, height=NY, count=1, dtype="uint16", crs=LCC,
                   transform=TR, compress="deflate", predictor=2, tiled=True) as o:
    o.write(bit, 1)
    o.update_tags(bitler=";".join(f"{i}={ad}" for i, ad in enumerate(K)))

# Bileşik kısıtlar: mutlak (yapılaşma dışı) ve güçlü (gerekçeyle aşılabilir)
MUTLAK = ["fay_1km", "sulak", "su", "kiyi_500m", "orman", "taskin", "korunan"]
GUCLU = ["ova_tarim", "dik"]
mutlak = np.zeros((NY, NX), bool)
for k in MUTLAK:
    mutlak |= K[k]
guclu = np.zeros((NY, NX), bool)
for k in GUCLU:
    guclu |= K[k]
elverisli = kara & ~mutlak & ~guclu & (np.nan_to_num(egim, nan=99) <= 15)

san = gpd.read_file(CIK / "sanayi_alanlari.gpkg")
san_m = rast(san, all_touched=False)
osb_m = rast(san[san.osb == "True"] if san.osb.dtype == object else san[san.osb], all_touched=False)
alan_km2 = H * H / 1e6
tr_alan = kara.sum() * alan_km2
P = nuf[kara].sum()
satir = []
for ad, m in list(K.items()) + [("MUTLAK (birleşik)", mutlak), ("GÜÇLÜ (birleşik)", guclu),
                                ("herhangi bir kısıt", mutlak | guclu), ("elverişli (kısıtsız, eğim ≤ %15)", elverisli)]:
    mm = m & kara
    satir.append({"katman": ad, "alan_km2": round(mm.sum() * alan_km2), "alan_pay": round(100 * mm.sum() / kara.sum(), 1),
                  "nufus_2025": round(nuf[mm].sum()), "nufus_pay": round(100 * nuf[mm].sum() / P, 1),
                  "sanayi_alani_pay": round(100 * (mm & san_m).sum() / max(san_m.sum(), 1), 1),
                  "osb_alani_pay": round(100 * (mm & osb_m).sum() / max(osb_m.sum(), 1), 1)})
oz = pd.DataFrame(satir)
oz.to_csv(SON / "ulusal_plan_kisit_ozet.csv", index=False, encoding="utf-8")
print(f"Türkiye kara alanı (ızgara): {tr_alan:,.0f} km²")
print(oz.to_string(index=False))

df = pd.DataFrame({"il": IL[kara], "elv": elverisli[kara], "mut": mutlak[kara], "ova": K["ova_tarim"][kara],
                   "fay": K["fay_1km"][kara], "p": nuf[kara]})
il = df.groupby("il").agg(alan_km2=("elv", "size"), elverisli=("elv", "mean"), mutlak=("mut", "mean"),
                          ova_tarim=("ova", "mean"), fay_1km=("fay", "mean"))
il["alan_km2"] *= alan_km2
il[["elverisli", "mutlak", "ova_tarim", "fay_1km"]] *= 100
il["nufus_fay_1km_pay"] = df.groupby("il").apply(lambda t: 100 * t.p[t.fay].sum() / t.p.sum(), include_groups=False)
il["nufus_taskin_pay"] = pd.DataFrame({"il": IL[kara], "m": K["taskin"][kara], "p": nuf[kara]}).groupby("il").apply(
    lambda t: 100 * t.p[t.m].sum() / t.p.sum(), include_groups=False)
il.round(1).to_csv(SON / "ulusal_plan_kisit_il.csv", encoding="utf-8")
print(il.sort_values("nufus_fay_1km_pay", ascending=False).head(12).round(1))
