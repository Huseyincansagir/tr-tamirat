"""
973 ilçe için uydu tabanlı çevre göstergeleri (GHS-POP 100 m hücreleri üzerinden, nüfus ağırlıklı)
=============================================================================================
Kaynaklar (anonim erişim; indirme kullanıcı onayıyla, 26.10.2026)
  ESA WorldCover 2021 v200   bulut uyumlu GeoTIFF'in 8× genel bakış katmanı (≈ 80 m; çoğunluk sınıfı). Tam çözünürlüğe göre
                             ağaç payını biraz düşük, yapılı alanı biraz yüksek veriyor (Fatih sınaması: %12,2 / %14,8 ağaç)
  ACAG V6.GL.03 PM2.5        0,01°, 2022–2024 ortalaması; küresel dosyadan yalnız Türkiye penceresi uzaktan okunur
                             (HDF5 parça okuma) ve 03_VERI/ham/pm25/V6GL03_CNNPM25_TR_2022_2024.tif olarak saklanır
  MODIS Aqua MYD11A2 v061    8 günlük 1 km gündüz yüzey sıcaklığı, Temmuz–Ağustos 2023 ve 2024 ortalaması
                             (Planetary Computer, anonim SAS belirteci; karo ortalamaları 03_VERI/ham/modis/)
Girdi : 03_VERI/ham/ghsl/tif/GHS_POP_* (2020), 03_VERI/ham/sinirlar/geoBoundaries-TUR-ADM2_simplified.geojson
Çıktı : 03_VERI/islenmis/ilce_uydu.csv
  agac300, yesil300w, yapili300 : 300 m yarıçap içinde ağaç / yeşil (ağaç+çalı+çayır+sulak) / yapılı alan payı (%), nüfus ağırlıklı
  pm25                          : yıllık ortalama PM2.5 (µg/m³), nüfus ağırlıklı
  lst, lst_alan, lst_fark       : yaz gündüz yüzey sıcaklığı (°C) — nüfus ağırlıklı, ilçe alanı (su hariç) ortalaması, farkı
"""
import glob
import sys
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import rasterio.errors
import requests
from rasterio.enums import Resampling
from rasterio.features import rasterize
from rasterio.merge import merge
from rasterio.warp import reproject, transform_bounds
from rasterio.windows import Window, from_bounds, transform as win_transform
from scipy.signal import fftconvolve

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
TIF = KOK / "03_VERI" / "ham" / "ghsl" / "tif"
PM = KOK / "03_VERI" / "ham" / "pm25"
MOD = KOK / "03_VERI" / "ham" / "modis"
MOD.mkdir(exist_ok=True)
IS = KOK / "03_VERI" / "islenmis"
WC = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{}_Map.tif"
ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF,.nc", GDAL_HTTP_MAX_RETRY="5",
           GDAL_HTTP_RETRY_DELAY="3")
bas = time.time()

# --- 1. MODIS: karo başına yaz ortalaması -------------------------------------------------------------------------
KAROLAR = ["h19v04", "h20v04", "h21v04", "h20v05", "h21v05"]
if not all((MOD / f"MYD11A2_yaz_{k}.tif").exists() for k in KAROLAR):
    # SAS belirteci depolama kabı başına alınır (koleksiyon adıyla alınan belirteç bu kapta 403 veriyor)
    tok = requests.get("https://planetarycomputer.microsoft.com/api/sas/v1/token/modiseuwest/modis-061-cogs", timeout=60).json()["token"]
    ogeler = []
    for yil in (2023, 2024):
        g = {"collections": ["modis-11A2-061"], "bbox": [25.6, 35.7, 44.9, 42.2],
             "datetime": f"{yil}-07-01T00:00:00Z/{yil}-08-31T23:59:59Z", "limit": 500}
        ogeler += requests.post("https://planetarycomputer.microsoft.com/api/stac/v1/search", json=g, timeout=120).json()["features"]
    for k in KAROLAR:
        sec = [f for f in ogeler if f["id"].startswith("MYD11A2") and f".{k}." in f["id"]]
        top, n, prof = None, None, None
        with rasterio.Env(**ENV):
            for f in sec:
                with rasterio.open(f["assets"]["LST_Day_1km"]["href"] + "?" + tok) as d:
                    a = d.read(1).astype("float64")
                    prof = d.profile
                v = a > 0
                top = np.where(v, a * 0.02, 0) if top is None else top + np.where(v, a * 0.02, 0)
                n = v.astype(int) if n is None else n + v
        ort = np.where(n > 0, top / np.maximum(n, 1) - 273.15, np.nan).astype("float32")
        prof.update(dtype="float32", nodata=np.nan, count=1, compress="deflate")
        with rasterio.open(MOD / f"MYD11A2_yaz_{k}.tif", "w", **prof) as o:
            o.write(ort, 1)
        print(f"MODIS {k}: {len(sec)} bileşik, ortalama {np.nanmean(ort):.1f} °C")
mod_ds = [rasterio.open(f) for f in sorted(MOD.glob("MYD11A2_yaz_*.tif"))]
mod_arr, mod_tr = merge(mod_ds, nodata=np.nan)
mod_arr, mod_crs = mod_arr[0], mod_ds[0].crs

# --- 2. PM2.5 2022–2024: küresel 0,01° dosyasından yalnız Türkiye penceresi (HDF5 parça okuma; dosya indirilmez) ---------
PM_TR = PM / "V6GL03_CNNPM25_TR_2022_2024.tif"
if not PM_TR.exists():
    URL = "https://satpmdata.s3.amazonaws.com/V6GL03/CNNPM25/Annual/GL/V6GL03.CNNPM25.GL.{y}01-{y}12.nc"
    # ızgara: satır 0 = 59,995°G (güneyden kuzeye), sütun 0 = 179,995°B; 0,01°
    r0, r1 = int((35.5 + 60) / 0.01), int((42.5 + 60) / 0.01)
    c0, c1 = int((25.5 + 180) / 0.01), int((45.0 + 180) / 0.01)
    top = None
    with rasterio.Env(**ENV):
        for y in (2022, 2023, 2024):
            for deneme in range(5):  # uzak HDF5 okumasında geçici HTTP hataları oluyor
                try:
                    with rasterio.open(f'HDF5:"/vsicurl/{URL.format(y=y)}"://PM25') as d:
                        a = d.read(1, window=Window(c0, r0, c1 - c0, r1 - r0)).astype("float32")[::-1]  # kuzey yukarı
                    break
                except rasterio.errors.RasterioIOError as e:
                    print("  PM2.5 yeniden:", y, deneme + 1, str(e)[:80])
                    time.sleep(10)
            else:
                raise RuntimeError(f"PM2.5 {y} okunamadı")
            a[(a < 0) | (a > 1000)] = np.nan
            top = a if top is None else top + a
    from rasterio.transform import from_origin
    with rasterio.open(PM_TR, "w", driver="GTiff", width=c1 - c0, height=r1 - r0, count=1, dtype="float32", crs="EPSG:4326",
                       transform=from_origin(-180 + c0 * 0.01, -60 + r1 * 0.01, 0.01, 0.01), nodata=np.nan, compress="deflate") as o:
        o.write(top / 3, 1)
with rasterio.open(PM_TR) as d:
    pm_kaynak = [(d.read(1), d.transform)]
print("PM2.5 Türkiye penceresi:", pm_kaynak[0][0].shape)


def disk(a, gecerli, r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    k = (x ** 2 + y ** 2 <= r ** 2).astype("float32")
    p = fftconvolve(np.where(gecerli, a, 0).astype("float32"), k, mode="same")
    q = fftconvolve(gecerli.astype("float32"), k, mode="same")
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(q > 0.5, p / q, np.nan)


def wc_karolar(b):
    ad = set()
    for lat in np.arange(np.floor(b[1] / 3) * 3, b[3], 3):
        for lon in np.arange(np.floor(b[0] / 3) * 3, b[2], 3):
            ad.add(f"{'N' if lat >= 0 else 'S'}{int(abs(lat)):02d}{'E' if lon >= 0 else 'W'}{int(abs(lon)):03d}")
    return sorted(ad)


# --- 3. GHS pencereleri: ilçe kimliği, nüfus, uydu katmanları ----------------------------------------------------
ilce = gpd.read_file(KOK / "03_VERI" / "ham" / "sinirlar" / "geoBoundaries-TUR-ADM2_simplified.geojson")
ilce["gid"] = np.arange(1, len(ilce) + 1)
ilce54 = ilce.to_crs("ESRI:54009")
N = len(ilce) + 1
acc = {k: np.zeros(N) for k in ["p", "agac", "yesil", "yapili", "pm", "p_pm", "lst", "p_lst", "alan_lst", "n_lst"]}
SINIF = {"agac": [10], "yesil": [10, 20, 30, 90], "yapili": [50]}
for pf in sorted(glob.glob(str(TIF / "GHS_POP_*" / "*.tif"))):
    with rasterio.open(pf) as rp:
        alt = ilce54.cx[rp.bounds.left:rp.bounds.right, rp.bounds.bottom:rp.bounds.top]
        if alt.empty:
            continue
        W = 2500
        for r0 in range(0, rp.height, W):
            for c0 in range(0, rp.width, W):
                win = Window(c0, r0, min(W, rp.width - c0), min(W, rp.height - r0))
                tr = win_transform(win, rp.transform)
                b = rasterio.windows.bounds(win, rp.transform)
                a2 = alt.cx[b[0]:b[2], b[1]:b[3]]
                if a2.empty:
                    continue
                t0 = time.time()
                sh = (win.height, win.width)
                gid = rasterize(zip(a2.geometry, a2.gid), out_shape=sh, transform=tr, fill=0, dtype="int32")
                if not (gid > 0).any():
                    continue
                pop = rp.read(1, window=win).astype("float64")
                pop[pop < 0] = 0
                # WorldCover (8× genel bakış) → 100 m pay → 300 m daire
                b4326 = transform_bounds("ESRI:54009", "EPSG:4326", *b, densify_pts=50)
                kat = {k: np.zeros(sh, dtype="float32") for k in list(SINIF) + ["su", "gecerli"]}
                with rasterio.Env(**ENV):
                    for karo in wc_karolar(b4326):
                        try:
                            src = rasterio.open("/vsicurl/" + WC.format(karo), overview_level=2)
                        except Exception:
                            continue  # denizde karo yok
                        with src:
                            ww = from_bounds(*b4326, src.transform).intersection(Window(0, 0, src.width, src.height))
                            s = src.read(1, window=ww)
                            st = src.window_transform(ww)
                        for k, sn in list(SINIF.items()) + [("su", [80]), ("gecerli", list(range(1, 101)))]:
                            m = np.isin(s, sn).astype("float32") if k != "gecerli" else (s > 0).astype("float32")
                            hedef = np.full(sh, np.nan, dtype="float32")
                            reproject(m, hedef, src_transform=st, src_crs="EPSG:4326", dst_transform=tr,
                                      dst_crs="ESRI:54009", resampling=Resampling.average, src_nodata=None, dst_nodata=np.nan)
                            kat[k] = np.where(np.isfinite(hedef), np.maximum(kat[k], hedef), kat[k])
                gec = kat["gecerli"] > 0.5
                yuzde = {k: disk(kat[k], gec, 3) * 100 for k in SINIF}
                # PM2.5
                pm = np.full(sh, np.nan, dtype="float32")
                for arr, ptr in pm_kaynak:
                    h = np.full(sh, np.nan, dtype="float32")
                    reproject(arr, h, src_transform=ptr, src_crs="EPSG:4326", dst_transform=tr, dst_crs="ESRI:54009",
                              resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan)
                    pm = np.where(np.isfinite(h), h, pm)
                # MODIS
                lst = np.full(sh, np.nan, dtype="float32")
                reproject(mod_arr, lst, src_transform=mod_tr, src_crs=mod_crs, dst_transform=tr, dst_crs="ESRI:54009",
                          resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan)
                # birikim
                g = gid.ravel()
                p = pop.ravel()
                acc["p"] += np.bincount(g, p, N)
                for k in SINIF:
                    v = yuzde[k].ravel()
                    ok = np.isfinite(v)
                    acc[k] += np.bincount(g[ok], (p * v)[ok], N)
                v = pm.ravel()
                ok = np.isfinite(v)
                acc["pm"] += np.bincount(g[ok], (p * v)[ok], N)
                acc["p_pm"] += np.bincount(g[ok], p[ok], N)
                v = lst.ravel()
                ok = np.isfinite(v)
                acc["lst"] += np.bincount(g[ok], (p * v)[ok], N)
                acc["p_lst"] += np.bincount(g[ok], p[ok], N)
                kara = ok & (kat["su"].ravel() < 0.5)
                acc["alan_lst"] += np.bincount(g[kara], v[kara], N)
                acc["n_lst"] += np.bincount(g[kara], minlength=N)
                print(f"  {Path(pf).parent.name[-6:]} pencere ({r0},{c0}) · {(gid > 0).sum():,} hücre · {time.time() - t0:.0f} sn", flush=True)

with np.errstate(invalid="ignore", divide="ignore"):
    out = pd.DataFrame({"gid": np.arange(N),
                        "agac300": acc["agac"] / acc["p"], "yesil300w": acc["yesil"] / acc["p"],
                        "yapili300": acc["yapili"] / acc["p"], "pm25": acc["pm"] / acc["p_pm"],
                        "lst": acc["lst"] / acc["p_lst"], "lst_alan": acc["alan_lst"] / acc["n_lst"]})
out["lst_fark"] = out.lst - out.lst_alan
out = out[out.gid > 0]
out.to_csv(IS / "ilce_uydu.csv", index=False, encoding="utf-8")
print(out.describe().round(2).T)
print(f"Tamam · {time.time() - bas:.0f} sn")
