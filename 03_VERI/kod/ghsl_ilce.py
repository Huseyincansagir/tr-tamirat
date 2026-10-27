"""
GHSL'den ilçe bazında bina yüksekliği ve nüfus göstergeleri
==========================================================
Girdi : 03_VERI/ham/ghsl/tif/  GHS_BUILT_H_ANBH_E2018 (ortalama net bina yüksekliği, m, 100 m)
                               GHS_POP_E2020 (nüfus, 100 m)          — 4'er karo, ESRI:54009
        03_VERI/ham/sinirlar/geoBoundaries-TUR-ADM2_simplified.geojson (973 ilçe)
        03_VERI/ham/sinirlar/geoBoundaries-TUR-ADM1_simplified.geojson (81 il)
Çıktı : 03_VERI/islenmis/ilce_ghsl.csv

Göstergeler (ilçe başına)
  ghs_nufus            : GHS-POP 2020 toplamı
  yapili_ha            : bina bulunan (yükseklik > 0) 100 m hücre sayısı (= ha)
  yuk_ort_yapili       : yapılı hücrelerde ortalama bina yüksekliği (m)
  yuk_nufus_agirlikli  : nüfus ağırlıklı ortalama bina yüksekliği (m) — "insanların yaşadığı binaların ortalama yüksekliği"
  pay_h15p / pay_h9p / pay_h6alt : nüfusun ortalama yüksekliği ≥15 m (~5+ kat), ≥9 m (~3+ kat), <6 m (~1-2 kat) olan hücrelerde yaşayan payı (%)
  yasanan_yogunluk     : nüfus ağırlıklı hücre yoğunluğu (kişi/ha) — Σp²/Σp
Yöntem: ilçeler karo pencerelerine rasterleştirilir, hücre değerleri ilçe kimliğiyle np.bincount ile toplanır.
"""
import glob
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window, transform as win_transform

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
TIF = KOK / "03_VERI" / "ham" / "ghsl" / "tif"
SINIR = KOK / "03_VERI" / "ham" / "sinirlar"

ilce = gpd.read_file(SINIR / "geoBoundaries-TUR-ADM2_simplified.geojson")
il = gpd.read_file(SINIR / "geoBoundaries-TUR-ADM1_simplified.geojson")
ilce["gid"] = np.arange(1, len(ilce) + 1)
nokta = ilce.copy()
nokta["geometry"] = ilce.geometry.representative_point()
eslesme = gpd.sjoin(nokta, il[["shapeName", "geometry"]].rename(columns={"shapeName": "il_gb"}), how="left", predicate="within")
ilce["il_gb"] = eslesme.groupby(level=0).il_gb.first()
ilce54 = ilce.to_crs("ESRI:54009")
N = len(ilce) + 1

acc = {k: np.zeros(N) for k in ["pop", "yapili", "h_sum_yapili", "ph", "pop_h15", "pop_h9", "pop_h6alt", "p2"]}
h_files = sorted(glob.glob(str(TIF / "GHS_BUILT_H_*" / "*.tif")))
for hf in h_files:
    karo = hf.split("_V1_0_")[-1].replace(".tif", "")
    pf = glob.glob(str(TIF / f"GHS_POP_*{karo}" / "*.tif"))[0]
    with rasterio.open(hf) as rh, rasterio.open(pf) as rp:
        # sol-üst köşe ve çözünürlük aynı olmalı; R5_C21'de yükseklik karosu 9000 satır (güneyi deniz), nüfus 10000
        assert rh.transform.almost_equals(rp.transform) and rh.width == rp.width and rh.height <= rp.height
        alt = ilce54.cx[rh.bounds.left:rh.bounds.right, rh.bounds.bottom:rh.bounds.top]
        if alt.empty:
            continue
        geoms = list(zip(alt.geometry, alt.gid))
        W = 2500
        for r0 in range(0, rh.height, W):
            for c0 in range(0, rh.width, W):
                win = Window(c0, r0, min(W, rh.width - c0), min(W, rh.height - r0))
                tr = win_transform(win, rh.transform)
                lab = rasterize(geoms, out_shape=(int(win.height), int(win.width)), transform=tr, fill=0, dtype="int32")
                if not lab.any():
                    continue
                h = rh.read(1, window=win).astype("float64")
                p = rp.read(1, window=win).astype("float64")
                h[(h >= 255) | (h < 0)] = 0
                p[p < 0] = 0
                m = lab > 0
                L, H_, P = lab[m], h[m], p[m]
                acc["pop"] += np.bincount(L, P, N)
                acc["yapili"] += np.bincount(L, (H_ > 0).astype(float), N)
                acc["h_sum_yapili"] += np.bincount(L, H_, N)
                acc["ph"] += np.bincount(L, P * H_, N)
                acc["pop_h15"] += np.bincount(L, P * (H_ >= 15), N)
                acc["pop_h9"] += np.bincount(L, P * (H_ >= 9), N)
                acc["pop_h6alt"] += np.bincount(L, P * (H_ < 6), N)
                acc["p2"] += np.bincount(L, P * P, N)
    print("işlendi:", karo)

g = pd.DataFrame({k: v[1:] for k, v in acc.items()})
g["gid"] = np.arange(1, N)
with np.errstate(divide="ignore", invalid="ignore"):
    g["ghs_nufus"] = g["pop"]
    g["yapili_ha"] = g["yapili"]
    g["yuk_ort_yapili"] = g.h_sum_yapili / g.yapili
    g["yuk_nufus_agirlikli"] = g.ph / g["pop"]
    g["pay_h15p"] = 100 * g.pop_h15 / g["pop"]
    g["pay_h9p"] = 100 * g.pop_h9 / g["pop"]
    g["pay_h6alt"] = 100 * g.pop_h6alt / g["pop"]
    g["yasanan_yogunluk"] = g.p2 / g["pop"]
alan = ilce54.geometry.area / 1e6
out = ilce[["gid", "shapeName", "shapeID", "il_gb"]].assign(alan_km2=alan.values).merge(
    g[["gid", "ghs_nufus", "yapili_ha", "yuk_ort_yapili", "yuk_nufus_agirlikli", "pay_h15p", "pay_h9p", "pay_h6alt", "yasanan_yogunluk"]], on="gid")
out.to_csv(KOK / "03_VERI" / "islenmis" / "ilce_ghsl.csv", index=False, encoding="utf-8")
print(out.describe().T[["mean", "min", "50%", "max"]].round(2))
print("il eşleşmesi olmayan ilçe:", out.il_gb.isna().sum(), "| GHS toplam nüfus:", round(out.ghs_nufus.sum()))
