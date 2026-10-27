"""
Arazi israfı: il bazında yapılı alan ve nüfus, 2000 ve 2020 (GHSL R2023A, 1 km)
==============================================================================
Kaynak : JRC GHSL R2023A, GHS-BUILT-S (yapılı yüzey, m²/hücre) ve GHS-POP (kişi/hücre),
         Mollweide (ESRI:54009) 1 km küresel dosyalar. Zip dosyası indirilmeden, GDAL
         /vsizip//vsicurl/ ile yalnızca Türkiye penceresi okunur (≈15 sn/dosya).
Sınır  : 03_VERI/ham/sinirlar/geoBoundaries-TUR-ADM1_simplified.geojson
Çıktı  : 03_VERI/ham/israf/ghsl/*.tif  (Türkiye penceresi, LZW; her biri <5 MB)
         03_VERI/ham/israf/ghsl_il_yapili_nufus_2000_2020.csv

Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/israf_ghsl_arazi.py
"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer
from rasterio.env import Env
from rasterio.features import rasterize
from rasterio.windows import from_bounds

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "israf"
GH = HAM / "ghsl"
GH.mkdir(parents=True, exist_ok=True)

B = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL"
KATMAN = {
    "built_2000": f"{B}/GHS_BUILT_S_GLOBE_R2023A/GHS_BUILT_S_E2000_GLOBE_R2023A_54009_1000/V1-0/GHS_BUILT_S_E2000_GLOBE_R2023A_54009_1000_V1_0.zip",
    "built_2020": f"{B}/GHS_BUILT_S_GLOBE_R2023A/GHS_BUILT_S_E2020_GLOBE_R2023A_54009_1000/V1-0/GHS_BUILT_S_E2020_GLOBE_R2023A_54009_1000_V1_0.zip",
    "pop_2000": f"{B}/GHS_POP_GLOBE_R2023A/GHS_POP_E2000_GLOBE_R2023A_54009_1000/V1-0/GHS_POP_E2000_GLOBE_R2023A_54009_1000_V1_0.zip",
    "pop_2020": f"{B}/GHS_POP_GLOBE_R2023A/GHS_POP_E2020_GLOBE_R2023A_54009_1000/V1-0/GHS_POP_E2020_GLOBE_R2023A_54009_1000_V1_0.zip",
}

il = gpd.read_file(KOK / "03_VERI" / "ham" / "sinirlar" / "geoBoundaries-TUR-ADM1_simplified.geojson")
il["il"] = il.shapeName.replace({"Hakkâri": "Hakkari"})
il["kod"] = np.arange(1, len(il) + 1)

veri, prof = {}, None
with Env(CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".zip,.tif", GDAL_HTTP_TIMEOUT=120, GDAL_HTTP_MAX_RETRY=4):
    for ad, url in KATMAN.items():
        yerel = GH / f"{ad}_tr_1km.tif"
        if yerel.exists():
            with rasterio.open(yerel) as s:
                veri[ad], prof = s.read(1).astype("float64"), s.profile
            nod = prof["nodata"]
        else:
            tif = url.rsplit("/", 1)[1].replace(".zip", ".tif")
            with rasterio.open(f"/vsizip//vsicurl/{url}/{tif}") as s:
                t = Transformer.from_crs("EPSG:4326", s.crs, always_xy=True)
                xs, ys = t.transform([25.5, 45.0, 25.5, 45.0, 35.0, 35.0], [35.7, 35.7, 42.3, 42.3, 42.3, 35.7])
                w = from_bounds(min(xs), min(ys), max(xs), max(ys), s.transform).round_offsets().round_lengths()
                a = s.read(1, window=w)
                prof = s.profile | {"height": a.shape[0], "width": a.shape[1], "transform": s.window_transform(w),
                                    "compress": "lzw", "tiled": False}
                prof.pop("blockxsize", None); prof.pop("blockysize", None)
                with rasterio.open(yerel, "w", **prof) as o:
                    o.write(a, 1)
                veri[ad] = a.astype("float64")
                nod = s.nodata
        if nod is not None:
            veri[ad][veri[ad] == nod] = np.nan
        print(ad, veri[ad].shape, f"toplam {np.nansum(veri[ad]):,.0f}")

ilm = il.to_crs(prof["crs"])
etiket = rasterize(zip(ilm.geometry, ilm.kod), out_shape=veri["built_2000"].shape, transform=prof["transform"], fill=0, dtype="int32")
satir = []
for _, r in il.iterrows():
    m = etiket == r.kod
    satir.append({"il": r.il} | {k: float(np.nansum(v[m])) for k, v in veri.items()})
df = pd.DataFrame(satir)
df["yapili_ha_2000"] = df.built_2000 / 1e4
df["yapili_ha_2020"] = df.built_2020 / 1e4
df = df.drop(columns=["built_2000", "built_2020"]).rename(columns={"pop_2000": "ghs_nufus_2000", "pop_2020": "ghs_nufus_2020"})
df.to_csv(HAM / "ghsl_il_yapili_nufus_2000_2020.csv", index=False, encoding="utf-8")
print(df[["yapili_ha_2000", "yapili_ha_2020", "ghs_nufus_2000", "ghs_nufus_2020"]].sum().round(0).to_dict())
