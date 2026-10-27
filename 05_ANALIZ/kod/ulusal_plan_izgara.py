"""
Faz 4 · Ulusal mekânsal çerçeve — 250 m'lik ulusal ızgara (LCC)
===============================================================
Bütün erişilebilirlik, kısıt ve öneri hesapları bu ortak ızgarada yapılır.
Projeksiyon: +proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 (metre), hücre 250 m, 6.760 × 3.020 hücre.

Katmanlar (03_VERI/islenmis/ulusal_altyapi/izgara_*.tif, her biri < 50 MB):
  izgara_nufus_ghsl.tif GHSL R2023A POP 2020 (100 m, Mollweide) hücre merkezlerinin LCC'ye taşınıp toplanmasıyla (toplam
                       korunur). Analizde kullanılan izgara_nufus.tif bundan ulusal_plan_nufus.py ile TÜİK 2025 ilçe
                       toplamlarına ölçeklenerek üretilir.
  izgara_ortu.tif      ESA WorldCover 2021 v200, 8× genel bakış (≈ 80 m) → hücredeki pay (%):
                       1 ağaç (10) · 2 tarım (40) · 3 yapılı (50) · 4 su (80) · 5 sulak (90) · 6 çayır (30) · 7 geçerli piksel payı
  izgara_yukselti.tif  Copernicus DEM GLO-90, 2× genel bakış (≈ 180 m) → 250 m (bilinear), m (int16)
  izgara_egim.tif      eğim (% × 10, uint16), 250 m yükselti üzerinden (yerel dik yamaçları yumuşatır; eşikler buna göre seçildi)
  izgara_taskin.tif    JRC CEMS-GloFAS küresel nehir taşkın tehlikesi v2.1.2, 100 yıllık dönüş, 3" (≈ 90 m) → taşkın alanı payı (%)
  izgara_pm25.tif      ACAG V6.GL.03 PM2.5, 2022–2024 ortalaması (µg/m³; 03_VERI/ham/pm25)
  izgara_ilce.tif      ilçe sıra no (ilce_paneli.gpkg satırı + 1); kıyıda boş kalan nüfuslu hücreler en yakın ilçeye atanır
  izgara_ilce_anahtar.csv  sıra no → ilçe kodu, ilçe, il
Uzak okumalar anonimdir; dosya indirilmez, yalnız gereken pencereler okunur.
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/ulusal_plan_izgara.py   (≈ 10–20 dk)
"""
import glob
import sys
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.enums import Resampling
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.warp import reproject, transform_bounds
from rasterio.windows import Window
from scipy import ndimage

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
CIK = KOK / "03_VERI" / "islenmis" / "ulusal_altyapi"
CIK.mkdir(parents=True, exist_ok=True)
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m +no_defs"
H = 250.0
X0, Y1, NX, NY = -810_000.0, 385_000.0, 6760, 3020
TR = from_origin(X0, Y1, H, H)
ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF", GDAL_HTTP_MAX_RETRY="5",
           GDAL_HTTP_RETRY_DELAY="3")
WC = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{}_Map.tif"
DEM = ("https://copernicus-dem-90m.s3.amazonaws.com/Copernicus_DSM_COG_30_{n}_00_{e}_00_DEM/"
       "Copernicus_DSM_COG_30_{n}_00_{e}_00_DEM.tif")
TASKIN = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/RP100/{}_RP100_depth_reclass.tif"
TASKIN_KARO = ["ID134_N50_E20", "ID135_N40_E20", "ID146_N50_E30", "ID147_N40_E30", "ID157_N50_E40", "ID158_N40_E40"]
bas = time.time()


def yaz(ad, dizi, dtype="float32", nodata=None, aciklama=None):
    if dizi.ndim == 2:
        dizi = dizi[np.newaxis]
    prof = dict(driver="GTiff", width=NX, height=NY, count=dizi.shape[0], dtype=dtype, crs=LCC, transform=TR,
                compress="deflate", predictor=2 if dtype.startswith("u") or dtype.startswith("i") else 3, tiled=True,
                nodata=nodata, zlevel=6)
    with rasterio.open(CIK / ad, "w", **prof) as o:
        o.write(dizi.astype(dtype))
        if aciklama:
            for i, a in enumerate(aciklama, 1):
                o.set_band_description(i, a)
    print(f"  {ad}: {(CIK / ad).stat().st_size / 1e6:.1f} MB · {time.time() - bas:.0f} sn", flush=True)


def pencereye(kaynak, src_tr, hedef, yontem=Resampling.bilinear, src_nodata=np.nan):
    """EPSG:4326 kaynak dizisini ulusal ızgaranın ilgili penceresine taşır; NaN olmayan değerleri hedefe yazar."""
    h, w = kaynak.shape
    west, south, east, north = rasterio.transform.array_bounds(h, w, src_tr)
    x0, y0, x1, y1 = transform_bounds("EPSG:4326", LCC, west, south, east, north, densify_pts=50)
    c0, c1 = max(int((x0 - X0) // H) - 2, 0), min(int((x1 - X0) // H) + 3, NX)
    r0, r1 = max(int((Y1 - y1) // H) - 2, 0), min(int((Y1 - y0) // H) + 3, NY)
    if c1 <= c0 or r1 <= r0:
        return
    alt = np.full((r1 - r0, c1 - c0), np.nan, dtype="float32")
    reproject(kaynak.astype("float32"), alt, src_transform=src_tr, src_crs="EPSG:4326",
              dst_transform=rasterio.windows.transform(Window(c0, r0, c1 - c0, r1 - r0), TR), dst_crs=LCC,
              resampling=yontem, src_nodata=src_nodata, dst_nodata=np.nan)
    hd = hedef[..., r0:r1, c0:c1]
    m = np.isfinite(alt)
    if hd.ndim == 2:
        hd[m] = alt[m]
    return m


# ---------- 1. ilçe ızgarası ----------------------------------------------------------------------------------
ilce = gpd.read_file(KOK / "03_VERI" / "islenmis" / "ilce_paneli.gpkg")[["ilce_kod", "ilce_ad_tuik", "il", "geometry"]]
ilce["sira"] = np.arange(1, len(ilce) + 1)
ilce[["sira", "ilce_kod", "ilce_ad_tuik", "il"]].to_csv(CIK / "izgara_ilce_anahtar.csv", index=False, encoding="utf-8")
il_lcc = ilce.to_crs(LCC)
ilce_r = rasterize(zip(il_lcc.geometry, il_lcc.sira), out_shape=(NY, NX), transform=TR, fill=0, dtype="int32")
print("ilçe ızgarası:", (ilce_r > 0).sum(), "hücre", f"· {time.time() - bas:.0f} sn")

# ---------- 2. GHSL nüfusu (hücre merkezleri → LCC, toplam korunur) --------------------------------------------
nufus = np.zeros(NY * NX, dtype="float64")
moll = Transformer.from_crs("ESRI:54009", LCC, always_xy=True)
for pf in sorted(glob.glob(str(KOK / "03_VERI" / "ham" / "ghsl" / "tif" / "GHS_POP_*" / "*.tif"))):
    with rasterio.open(pf) as rp:
        for r0 in range(0, rp.height, 2000):
            win = Window(0, r0, rp.width, min(2000, rp.height - r0))
            a = rp.read(1, window=win)
            rr, cc = np.nonzero(a > 0)
            if rr.size == 0:
                continue
            v = a[rr, cc].astype("float64")
            x = rp.transform.c + (cc + 0.5) * rp.transform.a
            y = rp.transform.f + (rr + r0 + 0.5) * rp.transform.e
            lx, ly = moll.transform(x, y)
            ci = ((lx - X0) // H).astype(np.int64)
            ri = ((Y1 - ly) // H).astype(np.int64)
            ok = (ci >= 0) & (ci < NX) & (ri >= 0) & (ri < NY)
            nufus += np.bincount(ri[ok] * NX + ci[ok], v[ok], NY * NX)
nufus = nufus.reshape(NY, NX)
print(f"GHSL nüfus toplamı (ızgara): {nufus.sum() / 1e6:.2f} milyon; ilçe sınırı içinde {nufus[ilce_r > 0].sum() / 1e6:.2f} milyon")
# Sadeleştirilmiş sınırın kıyıda dışarıda bıraktığı hücreler → en yakın ilçe. Yalnız kıyı çizgisine (OSM) 3 km'den yakın
# ve sınıra 1,5 km'den yakın hücreler; kara sınırındaki komşu ülke nüfusu (ör. Kamışlı, Halep çevresi) alınmaz.
kiyi = gpd.read_file(CIK / "kiyi.gpkg").to_crs(LCC)
kiyi_r = rasterize(((g, 1) for g in kiyi.geometry), out_shape=(NY, NX), transform=TR, fill=0, dtype="uint8")
kiyi_uzak = ndimage.distance_transform_edt(kiyi_r == 0) * H
uzak, (iy, ix) = ndimage.distance_transform_edt(ilce_r == 0, return_indices=True)
ek = (ilce_r == 0) & (uzak * H <= 1500) & (kiyi_uzak <= 3000)
del kiyi_uzak, kiyi_r
ilce_r[ek] = ilce_r[iy[ek], ix[ek]]
print(f"  ilçeye atanmış nüfus: {nufus[ilce_r > 0].sum() / 1e6:.2f} milyon")
yaz("izgara_ilce.tif", ilce_r, "int32", 0)
nufus_tr = np.where(ilce_r > 0, nufus, 0).astype("float32")
yaz("izgara_nufus_ghsl.tif", nufus_tr, "float32", None)
del uzak, iy, ix

# ---------- 3. PM2.5 ----------------------------------------------------------------------------------------
pm = np.full((NY, NX), np.nan, dtype="float32")
with rasterio.open(KOK / "03_VERI" / "ham" / "pm25" / "V6GL03_CNNPM25_TR_2022_2024.tif") as d:
    reproject(d.read(1), pm, src_transform=d.transform, src_crs=d.crs, dst_transform=TR, dst_crs=LCC,
              resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan)
yaz("izgara_pm25.tif", pm, "float32", np.nan)

# ---------- 4. WorldCover (8× genel bakış) → sınıf payları ----------------------------------------------------
SINIF = [("agac", [10]), ("tarim", [40]), ("yapili", [50]), ("su", [80]), ("sulak", [90, 95]), ("cayir", [30])]
ortu = np.full((len(SINIF) + 1, NY, NX), np.nan, dtype="float32")
with rasterio.Env(**ENV):
    for lat in (33, 36, 39, 42):
        for lon in range(24, 45, 3):
            karo = f"N{lat:02d}E{lon:03d}"
            t0 = time.time()
            try:
                src = rasterio.open("/vsicurl/" + WC.format(karo), overview_level=2)
            except Exception:
                continue
            with src:
                s = src.read(1)
                st = src.transform
            k = 3  # 3 × 80 m ≈ 240 m bloklar
            h, w = (s.shape[0] // k) * k, (s.shape[1] // k) * k
            s = s[:h, :w]
            blk = lambda m: m.reshape(h // k, k, w // k, k).mean(axis=(1, 3)).astype("float32")
            gec = blk(s > 0)
            st3 = rasterio.Affine(st.a * k, 0, st.c, 0, st.e * k, st.f)
            for i, (ad, sn) in enumerate(SINIF):
                pay = np.where(gec > 0, blk(np.isin(s, sn)) / np.maximum(gec, 1e-6) * 100, np.nan)
                pencereye(pay, st3, ortu[i])
            pencereye(gec * 100, st3, ortu[len(SINIF)])
            print(f"  WorldCover {karo}: {time.time() - t0:.0f} sn", flush=True)
del s
yaz("izgara_ortu.tif", np.nan_to_num(np.round(ortu), nan=255).astype("uint8"), "uint8", 255,
    [a for a, _ in SINIF] + ["gecerli"])

# ---------- 5. Copernicus DEM GLO-90 → yükselti ve eğim --------------------------------------------------------
yuk = np.full((NY, NX), np.nan, dtype="float32")
with rasterio.Env(**ENV):
    for lat in range(35, 43):
        for lon in range(25, 45):
            u = DEM.format(n=f"N{lat:02d}", e=f"E{lon:03d}")
            try:
                with rasterio.open(u, overview_level=0) as d:
                    a, dt = d.read(1).astype("float32"), d.transform
            except Exception:
                continue  # denizde karo yok
            pencereye(a, dt, yuk)
    print(f"  DEM bitti · {time.time() - bas:.0f} sn", flush=True)
gy, gx = np.gradient(np.where(np.isfinite(yuk), yuk, 0), H)
egim = (np.hypot(gx, gy) * 100).astype("float32")
egim[~np.isfinite(yuk)] = np.nan
# 50 MB sınırı için tamsayı: yükselti m (int16, boş −32768), eğim ‰ (uint16 = % × 10, boş 65535)
yaz("izgara_yukselti.tif", np.where(np.isfinite(yuk), np.round(yuk), -32768), "int16", -32768)
yaz("izgara_egim.tif", np.where(np.isfinite(egim), np.clip(np.round(egim * 10), 0, 65534), 65535), "uint16", 65535)
del gx, gy

# ---------- 6. JRC taşkın tehlikesi (100 yıl) ----------------------------------------------------------------------
taskin = np.full((NY, NX), np.nan, dtype="float32")
with rasterio.Env(**ENV):
    for karo in TASKIN_KARO:
        t0 = time.time()
        with rasterio.open("/vsicurl/" + TASKIN.format(karo)) as d:
            # yalnız Türkiye çevresi (25–45° D, 35–43° K)
            b = d.bounds
            w = rasterio.windows.from_bounds(max(b.left, 25.0), max(b.bottom, 35.0), min(b.right, 45.5),
                                             min(b.top, 43.0), d.transform).round_offsets().round_lengths()
            if w.width <= 0 or w.height <= 0:
                continue
            a = d.read(1, window=w)
            dt = d.window_transform(w)
        k = 3
        h, wd = (a.shape[0] // k) * k, (a.shape[1] // k) * k
        a = a[:h, :wd]
        pay = ((a >= 1) & (a <= 4)).reshape(h // k, k, wd // k, k).mean(axis=(1, 3)).astype("float32") * 100
        pencereye(pay, rasterio.Affine(dt.a * k, 0, dt.c, 0, dt.e * k, dt.f), taskin)
        print(f"  taşkın {karo}: {time.time() - t0:.0f} sn", flush=True)
yaz("izgara_taskin.tif", taskin, "float32", np.nan)
print(f"Tamam · {time.time() - bas:.0f} sn")
