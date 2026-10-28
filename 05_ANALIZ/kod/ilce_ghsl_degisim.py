"""
Zaman paneli hazırlığı — ilçe başına GHSL 2000 → 2020 değişimi
==============================================================
GHSL R2023A, 1 km: yapılı yüzey (GHS-BUILT-S, m²) ve nüfus (GHS-POP), 2000 ve 2020 (Rapor 19'un indirdiği karolar).
İlçe sınırları geoBoundaries ADM2 (gid = satır no + 1; fue_ilce_gecerlilik.py ve ghsl_ilce.py ile aynı).

Çıktı değişkenleri (ilçe):
  yapili_km2_2000/2020, ghs_pop_2000/2020,
  yogunluk_yapili_2000/2020 (kişi / yapılı km²; yayılmanın tersi),
  d_ln_yapili, d_ln_pop, d_ln_yogunluk (2000 → 2020 log değişim),
  yapili_kisi_m2_2000/2020 (kişi başı yapılı alan)

Girdi : 03_VERI/ham/israf/ghsl/{built,pop}_{2000,2020}_tr_1km.tif, 03_VERI/ham/sinirlar/geoBoundaries-TUR-ADM2_simplified.geojson,
        03_VERI/islenmis/ilce_fue_lite.csv (gid → ilce_kod)
Çıktı : 03_VERI/islenmis/ilce_ghsl_degisim.csv
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/ilce_ghsl_degisim.py  (önce israf_ghsl_arazi.py)
"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
G = KOK / "03_VERI" / "ham" / "israf" / "ghsl"
IS = KOK / "03_VERI" / "islenmis"

ilce = gpd.read_file(KOK / "03_VERI" / "ham" / "sinirlar" / "geoBoundaries-TUR-ADM2_simplified.geojson")
ilce["gid"] = np.arange(1, len(ilce) + 1)
with rasterio.open(G / "pop_2020_tr_1km.tif") as r:
    prof = r.profile
    gid = rasterize(zip(ilce.to_crs(r.crs).geometry, ilce.gid), out_shape=r.shape, transform=r.transform, fill=0,
                    dtype="int32", all_touched=False)


def oku(ad):
    with rasterio.open(G / f"{ad}_tr_1km.tif") as r:
        assert r.transform == prof["transform"] and r.shape == (prof["height"], prof["width"])
        a = r.read(1).astype("float64")
        a[(a == r.nodata) | ~np.isfinite(a) | (a < 0)] = 0.0
        return a


N = len(ilce) + 1
out = pd.DataFrame({"gid": np.arange(N)})
for ad in ("built_2000", "built_2020", "pop_2000", "pop_2020"):
    out[ad] = np.bincount(gid.ravel(), weights=oku(ad).ravel(), minlength=N)
out = out[out.gid > 0].copy()
out["yapili_km2_2000"] = out.built_2000 / 1e6
out["yapili_km2_2020"] = out.built_2020 / 1e6
out["ghs_pop_2000"], out["ghs_pop_2020"] = out.pop_2000, out.pop_2020
for y in (2000, 2020):
    out[f"yogunluk_yapili_{y}"] = out[f"ghs_pop_{y}"] / out[f"yapili_km2_{y}"].replace(0, np.nan)
    out[f"yapili_kisi_m2_{y}"] = out[f"yapili_km2_{y}"] * 1e6 / out[f"ghs_pop_{y}"].replace(0, np.nan)
out["d_ln_yapili"] = np.log(out.yapili_km2_2020 / out.yapili_km2_2000.replace(0, np.nan))
out["d_ln_pop"] = np.log(out.ghs_pop_2020 / out.ghs_pop_2000.replace(0, np.nan))
out["d_ln_yogunluk"] = out.d_ln_pop - out.d_ln_yapili
kod = pd.read_csv(IS / "ilce_fue_lite.csv", usecols=["gid", "ilce_kod", "il", "ilce_ad_tuik"], dtype={"ilce_kod": str})
out = kod.merge(out.drop(columns=["built_2000", "built_2020", "pop_2000", "pop_2020"]), on="gid", how="left")
out.to_csv(IS / "ilce_ghsl_degisim.csv", index=False, encoding="utf-8")
print(f"{len(out)} ilçe; GHS-POP 2000 {out.ghs_pop_2000.sum():,.0f} → 2020 {out.ghs_pop_2020.sum():,.0f}; "
      f"yapılı alan {out.yapili_km2_2000.sum():,.0f} → {out.yapili_km2_2020.sum():,.0f} km²")
print(out[["d_ln_yapili", "d_ln_pop", "d_ln_yogunluk", "yapili_kisi_m2_2000", "yapili_kisi_m2_2020"]]
      .describe().round(3).to_string())
