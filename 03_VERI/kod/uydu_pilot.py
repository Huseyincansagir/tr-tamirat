"""
Pilot ilçeler için uydu tabanlı çevre katmanları (30 m, UTM)
==========================================================
Kaynaklar (hepsi anonim erişim; indirme kullanıcı onayıyla, 26.10.2026)
  ESA WorldCover 2021 v200, 10 m       https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/  (bulut uyumlu GeoTIFF;
                                       yalnız gereken pencereler okunur)
  Landsat 8/9 Collection 2 Level-2     Microsoft Planetary Computer STAC (landsat-c2-l2), anonim SAS belirteci;
  yüzey sıcaklığı (ST_B10, lwir11)     yaz (15 Haziran–15 Eylül) 2022–2025, bulut < %20, QA_PIXEL ile bulut ve gölge maskesi
  ACAG V6.GL.03 PM2.5, 0,01°           https://satpmdata.s3.amazonaws.com/V6GL03/CNNPM25/Annual/EU/ (2022–2024 ortalaması;
                                       03_VERI/ham/pm25/). CAMS Avrupa yeniden analizi hesap ve API anahtarı gerektirdiği için
                                       kullanılmadı.
Girdi : 03_VERI/islenmis/ilce_paneli.gpkg (ilçe sınırları; kapsam = sınır + 3 km)
Çıktı : 03_VERI/islenmis/uydu/pilot_<ilçe>.tif   bantlar (30 m):
          1 agac300   ağaç örtüsü payı, 300 m yarıçaplı daire içinde (%)
          2 yesil300  ağaç + çalı + çayır + sulak alan payı, 300 m içinde (%)
          3 yapili300 yapılı alan (WorldCover sınıf 50) payı, 300 m içinde (%) — geçirimsiz yüzey vekili
          4 lst       yaz ortanca gündüz yüzey sıcaklığı (°C)
          5 lst_n     geçerli gözlem sayısı
          6 lst_fark  yüzey ısı adası: lst − ilçe alanı (su hariç) ortalaması (°C)
          7 pm25      yıllık ortalama PM2.5, 2022–2024 (µg/m³; 1 km'den çift doğrusal)
          8 agac      30 m pikselde ağaç payı (%)
        03_VERI/islenmis/uydu/landsat_sahneler.csv  kullanılan sahneler
"""
import sys
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import rasterio.features
import requests
import shapely
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.vrt import WarpedVRT
from rasterio.warp import reproject
from scipy.signal import fftconvolve

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
CIK = IS / "uydu"
CIK.mkdir(exist_ok=True)
PM = KOK / "03_VERI" / "ham" / "pm25"
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
WC = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{}_Map.tif"
ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF", GDAL_HTTP_MAX_RETRY="5",
           GDAL_HTTP_RETRY_DELAY="3", VSI_CACHE="TRUE")
R30, YARICAP = 30, 300
bas = time.time()


def utm_epsg(lon):
    return 32600 + int((lon + 180) // 6) + 1


def disk_ortalama(a, gecerli, r_px):
    """Geçerli piksellere göre normalize edilmiş daire içi ortalama (FFT evrişimi)."""
    y, x = np.mgrid[-r_px:r_px + 1, -r_px:r_px + 1]
    k = (x ** 2 + y ** 2 <= r_px ** 2).astype("float32")
    pay = fftconvolve(np.where(gecerli, a, 0).astype("float32"), k, mode="same")
    payda = fftconvolve(gecerli.astype("float32"), k, mode="same")
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(payda > 0.5, pay / payda, np.nan)


def wc_karolar(b):
    """4326 kutusunu kesen WorldCover 3°×3° karo adları."""
    ad = set()
    for lat in np.arange(np.floor(b[1] / 3) * 3, b[3], 3):
        for lon in np.arange(np.floor(b[0] / 3) * 3, b[2], 3):
            ad.add(f"{'N' if lat >= 0 else 'S'}{int(abs(lat)):02d}{'E' if lon >= 0 else 'W'}{int(abs(lon)):03d}")
    return sorted(ad)


_belirtec = {}


def imzala(href, kol="landsat-c2-l2"):
    if kol not in _belirtec or time.time() - _belirtec[kol][1] > 1800:
        t = requests.get(f"https://planetarycomputer.microsoft.com/api/sas/v1/token/{kol}", timeout=60).json()["token"]
        _belirtec[kol] = (t, time.time())
    return href + "?" + _belirtec[kol][0]


def stac_ara(govde):
    out, url, g = [], STAC + "/search", dict(govde)
    while True:
        for deneme in range(4):
            try:
                r = requests.post(url, json=g, timeout=120)
                r.raise_for_status()
                break
            except Exception as e:
                print("   STAC yeniden:", e)
                time.sleep(5)
        j = r.json()
        out += j["features"]
        nxt = [l for l in j.get("links", []) if l.get("rel") == "next"]
        if not nxt:
            return out
        url, g = nxt[0]["href"], nxt[0].get("body", g)


# PM2.5: 2022–2024 ortalaması (Avrupa alanı 15°B–40°D; pilotların hepsi içinde)
pm_ort, pm_tr = None, None
for y in (2022, 2023, 2024):
    with rasterio.open(PM / f"V6GL03.CNNPM25.EU.{y}01-{y}12.nc") as d:
        a = d.read(1).astype("float32")
        a[(a < 0) | (a > 1000)] = np.nan
        pm_ort = a if pm_ort is None else pm_ort + a
        pm_tr = d.transform
pm_ort /= 3

ilce = gpd.read_file(IS / "ilce_paneli.gpkg")
PILOT = {1327: "Fatih", 1622: "Silivri", 2050: "Başakşehir", 1829: "Nilüfer", 1863: "Kocasinan", 1827: "Meram",
         2080: "Antakya", 2085: "Onikişubat", 1587: "Safranbolu", 1187: "Beypazarı"}
sahne_kayit = []
for kod, ad in PILOT.items():
    t0 = time.time()
    out = CIK / f"pilot_{ad}.tif"
    if out.exists():
        print(ad, "var, atlandı")
        continue
    ip = ilce[ilce.ilce_kod.astype(int) == kod].geometry.iloc[0]
    epsg = utm_epsg(ip.centroid.x)  # fue_mahalle.py ile aynı UTM dilimi
    # kapsam: ilçe sınırı (geoBoundaries, sadeleştirilmiş) + 3 km tampon — mahalle sınırları bu alanın içinde kalır
    x0, y0, x1, y1 = gpd.GeoSeries([ip], crs=4326).to_crs(epsg).buffer(3000).total_bounds
    x0, y0 = np.floor(x0 / R30) * R30, np.floor(y0 / R30) * R30
    x1, y1 = np.ceil(x1 / R30) * R30, np.ceil(y1 / R30) * R30
    W, H = int((x1 - x0) / R30), int((y1 - y0) / R30)
    T30 = from_origin(x0, y1, R30, R30)
    T10 = from_origin(x0, y1, 10, 10)
    kutu = gpd.GeoSeries([shapely.box(x0, y0, x1, y1)], crs=epsg).to_crs(4326).total_bounds

    # --- WorldCover: 10 m sınıf → 30 m sınıf payları → 300 m daire ortalaması ---
    wc = np.zeros((H * 3, W * 3), dtype="uint8")
    with rasterio.Env(**ENV):
        for karo in wc_karolar(kutu):
            with rasterio.open("/vsicurl/" + WC.format(karo)) as src, \
                    WarpedVRT(src, crs=f"EPSG:{epsg}", transform=T10, width=W * 3, height=H * 3,
                              resampling=Resampling.nearest, nodata=0) as vrt:
                a = vrt.read(1)
                wc = np.where(wc == 0, a, wc)

    def pay(siniflar):
        m = np.isin(wc, siniflar).astype("float32")
        return m.reshape(H, 3, W, 3).mean(axis=(1, 3))

    gecerli = pay([10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]) > 0
    kara = pay([80]) < 0.5
    agac, yesil, yapili, su = pay([10]), pay([10, 20, 30, 90]), pay([50]), pay([80])
    r_px = int(YARICAP / R30)
    agac300 = disk_ortalama(agac, gecerli, r_px) * 100
    yesil300 = disk_ortalama(yesil, gecerli, r_px) * 100
    yapili300 = disk_ortalama(yapili, gecerli, r_px) * 100
    print(f"  {ad}: WorldCover {wc_karolar(kutu)} · {W}×{H} · {time.time() - t0:.0f} sn", flush=True)

    # --- Landsat yüzey sıcaklığı: yaz sahneleri, bulut maskeli ortanca ---
    aday = []
    for yil in (2022, 2023, 2024, 2025):
        aday += stac_ara({"collections": ["landsat-c2-l2"], "bbox": [float(v) for v in kutu],
                          "datetime": f"{yil}-06-15T00:00:00Z/{yil}-09-15T23:59:59Z",
                          "query": {"eo:cloud_cover": {"lt": 20}, "platform": {"in": ["landsat-8", "landsat-9"]}},
                          "limit": 100})
    kutu_g = shapely.box(*kutu)
    for f in aday:
        f["_ortusme"] = shapely.geometry.shape(f["geometry"]).intersection(kutu_g).area / kutu_g.area
    aday = [f for f in aday if f["_ortusme"] > 0.3]
    aday.sort(key=lambda f: (-round(f["_ortusme"], 1), f["properties"]["eo:cloud_cover"]))
    sec = aday[:14]
    yigin = []
    with rasterio.Env(**ENV):
        for f in sec:
            try:
                with rasterio.open(imzala(f["assets"]["lwir11"]["href"])) as s1, \
                        WarpedVRT(s1, crs=f"EPSG:{epsg}", transform=T30, width=W, height=H,
                                  resampling=Resampling.bilinear, nodata=0) as v1:
                    st = v1.read(1).astype("float32")
                with rasterio.open(imzala(f["assets"]["qa_pixel"]["href"])) as s2, \
                        WarpedVRT(s2, crs=f"EPSG:{epsg}", transform=T30, width=W, height=H,
                                  resampling=Resampling.nearest, nodata=1) as v2:
                    qa = v2.read(1)
            except Exception as e:
                print("   sahne okunamadı:", f["id"], e)
                continue
            iyi = (st > 0) & ((qa & 0b11111) == 0)
            lst = np.where(iyi, st * 0.00341802 + 149.0 - 273.15, np.nan)
            yigin.append(lst)
            sahne_kayit.append({"ilce": ad, "sahne": f["id"], "tarih": f["properties"]["datetime"][:10],
                                "bulut": f["properties"]["eo:cloud_cover"], "ortusme": round(f["_ortusme"], 3),
                                "gecerli_pay": round(float(iyi.mean()), 3)})
    Y = np.stack(yigin)
    lst_n = np.isfinite(Y).sum(axis=0).astype("float32")
    with np.errstate(all="ignore"):
        lst = np.nanmedian(Y, axis=0)
    lst[lst_n < 2] = np.nan
    # ilçe alanı (su hariç) ortalaması → yüzey ısı adası farkı
    ic = rasterio.features.geometry_mask([gpd.GeoSeries([ip], crs=4326).to_crs(epsg).iloc[0]], (H, W), T30, invert=True)
    ref = np.nanmean(np.where(ic & kara, lst, np.nan))
    lst_fark = lst - ref

    # --- PM2.5 (1 km) → 30 m ---
    pm = np.full((H, W), np.nan, dtype="float32")
    reproject(pm_ort, pm, src_transform=pm_tr, src_crs="EPSG:4326", dst_transform=T30, dst_crs=f"EPSG:{epsg}",
              resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan)

    bantlar = [("agac300", agac300), ("yesil300", yesil300), ("yapili300", yapili300), ("lst", lst), ("lst_n", lst_n),
               ("lst_fark", lst_fark), ("pm25", pm), ("agac", agac * 100)]
    with rasterio.open(out, "w", driver="GTiff", width=W, height=H, count=len(bantlar), dtype="float32",
                       crs=f"EPSG:{epsg}", transform=T30, nodata=np.nan, compress="deflate", predictor=3, tiled=True) as d:
        for i, (b, a) in enumerate(bantlar, 1):
            d.write(a.astype("float32"), i)
            d.set_band_description(i, b)
        d.update_tags(lst_ref_c=f"{ref:.2f}", sahne_sayisi=len(yigin))
    print(f"{ad:<11} Landsat sahne {len(yigin)} (aday {len(aday)}) · LST ilçe ort. {ref:.1f} °C · "
          f"PM2.5 {np.nanmean(pm):.1f} · ağaç %{np.nanmean(agac) * 100:.1f} · {time.time() - t0:.0f} sn", flush=True)

if sahne_kayit:
    f = CIK / "landsat_sahneler.csv"
    parca = ([pd.read_csv(f)] if f.exists() else []) + [pd.DataFrame(sahne_kayit)]
    pd.concat(parca, ignore_index=True).to_csv(f, index=False)
print(f"Tamam · {time.time() - bas:.0f} sn")
