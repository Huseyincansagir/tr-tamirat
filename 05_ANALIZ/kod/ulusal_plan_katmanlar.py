"""
Faz 4 · Ulusal mekânsal çerçeve — analiz katmanlarının ayıklanması
================================================================
Girdi : 03_VERI/islenmis/ulusal_altyapi/*.gpkg (ulusal_altyapi_osm.py), izgara_nufus.tif, izgara_ilce.tif (ulusal_plan_izgara.py)
Çıktı : 03_VERI/islenmis/ulusal_altyapi/
          havalimanlari_yolcu.gpkg  tarifeli yolcu taşımacılığı olan havalimanları (OSM iata + elle ayıklama)
          limanlar_yuk.gpkg         başlıca yük ve enerji limanları (konum OSM'den; sınıf ikincil kaynaktan) + demiryolu bağlantısı
          istasyonlar_yolcu.gpkg    yolcu demiryolu istasyon ve durakları (kent içi raylı hariç) + hızlı tren işareti
          diri_faylar_gem.gpkg      GEM Küresel Diri Faylar Veritabanı (harmonize), Türkiye ve 50 km çevresi
          kent_merkezleri.csv       her ilin ana kentinin nüfus ağırlıklı merkezi (≥ 1.500 kişi/km² bitişik hücreler)
        05_ANALIZ/sonuclar/ulusal_plan_ruzgar_il.csv  il merkezlerinde rüzgâr yönü sıklıkları (ERA5, Open-Meteo, 2023–2024)
Uzak kaynaklar (anonim):
  GEM GAF-DB  https://github.com/GEMScienceTools/gem-global-active-faults (CC BY-SA 4.0; Türkiye izleri EMME 2014 kataloğundan)
  Open-Meteo  https://archive-api.open-meteo.com (ERA5 yeniden analizi, 0,25°; CC BY 4.0)
"""
import json
import sys
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import requests
from scipy import ndimage
from shapely.geometry import Point, box

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
CIK = KOK / "03_VERI" / "islenmis" / "ulusal_altyapi"
SON = KOK / "05_ANALIZ" / "sonuclar"
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m +no_defs"

# ---------- 1. Yolcu havalimanları -------------------------------------------------------------------------------
h = gpd.read_file(CIK / "havalimanlari.gpkg")
h = h[h.iata.str.len() == 3].copy()
h["askeri_kayit"] = (h.military == "airfield") & ~h.aerodrome_type.str.contains("public|civil|international|regional")
h = h.sort_values("askeri_kayit").drop_duplicates("iata")  # ortak kullanımlı üslerde sivil kaydı tut
CIKAR = {
    "ADA": "Adana Şakirpaşa: 2024'te tarifeli seferler Çukurova'ya (COV) taşındı [İ]",
    "ISL": "İstanbul Atatürk: 2019'dan beri tarifeli yolcu yok [İ]",
    "IZM": "Selçuk-Efes: tarifeli sefer yok [V]", "CII": "Çıldır: tarifeli sefer yok [V]",
    "AFY": "Afyon: askerî, tarifeli sefer yok [V]", "ESK": "askerî üs", "BDM": "askerî üs", "UAB": "askerî üs (İncirlik)",
    "IGL": "askerî üs (Çiğli)", "BXN": "askerî (Imsık)", "ANK": "askerî (Etimesgut)", "NIL": "eğitim meydanı (Samsun)"}
h = h[~h.iata.isin(CIKAR)].copy()
h["geometry"] = h.geometry.representative_point()
h[["ad", "iata", "icao", "aerodrome_type", "geometry"]].to_file(CIK / "havalimanlari_yolcu.gpkg", driver="GPKG")
print(f"yolcu havalimanı: {len(h)} (DHMİ havalimanı listesi: 56 kayıt, İstanbul Atatürk dahil, Ekim 2026 [D])")

# ---------- 2. Başlıca yük ve enerji limanları ----------------------------------------------------------------------
# Konumlar OSM nesnelerinden (ad, liman alanı ya da liman düğümü); sınıf: ana = ulusal ölçekte konteyner/genel kargo
# merkezi, bolge = bölgesel genel kargo/dökme yük, enerji = ham petrol / doğal gaz terminali. Sınıflama [İ]: UAB liman
# başkanlıkları elleçleme istatistikleri (2024) ve liman işletmeleri; ayrıntılı tonaj doğrulanmadı [DY].
LIMAN = [
    ("Ambarlı (Kumport, Marport)", "İstanbul", 28.673, 40.966, "ana"),
    ("Haydarpaşa", "İstanbul", 29.018, 40.998, "bolge"),
    ("Dilovası (Yılport, Poliport, Efesanport)", "Kocaeli", 29.535, 40.768, "ana"),
    ("Evyapport / Yarımca", "Kocaeli", 29.725, 40.768, "ana"),
    ("Derince (Safiport)", "Kocaeli", 29.832, 40.751, "ana"),
    ("Gemlik (Borusan, Gemport, Roda)", "Bursa", 29.085, 40.414, "ana"),
    ("Bandırma", "Balıkesir", 27.957, 40.354, "bolge"),
    ("Tekirdağ (Asyaport)", "Tekirdağ", 27.467, 40.899, "ana"),
    ("Aliağa - Nemrut", "İzmir", 26.944, 38.770, "ana"),
    ("İzmir Alsancak", "İzmir", 27.157, 38.443, "ana"),
    ("Mersin (MIP)", "Mersin", 34.648, 36.806, "ana"),
    ("İskenderun (Limak)", "Hatay", 36.190, 36.595, "ana"),
    ("İskenderun Körfezi (Atakaş, Assan, İsdemir)", "Hatay", 36.188, 36.700, "bolge"),
    ("Samsun", "Samsun", 36.351, 41.309, "ana"),
    ("Trabzon", "Trabzon", 39.736, 41.005, "bolge"),
    ("Antalya (Port Akdeniz)", "Antalya", 30.615, 36.835, "bolge"),
    ("Zonguldak", "Zonguldak", 31.783, 41.454, "bolge"),
    ("Filyos", "Zonguldak", 32.086, 41.588, "bolge"),
    ("Eren (Çatalağzı)", "Zonguldak", 31.911, 41.524, "bolge"),
    ("Karadeniz Ereğli (Erdemir)", "Zonguldak", 31.420, 41.261, "bolge"),
    ("Karasu", "Sakarya", 30.671, 41.121, "bolge"),
    ("Bartın", "Bartın", 32.228, 41.685, "bolge"),
    ("Giresun", "Giresun", 38.383, 40.919, "bolge"),
    ("Ordu", "Ordu", 37.877, 40.996, "bolge"),
    ("Rize", "Rize", 40.512, 41.038, "bolge"),
    ("Hopa", "Artvin", 41.435, 41.413, "bolge"),
    ("Sinop", "Sinop", 35.149, 42.023, "bolge"),
    ("Taşucu", "Mersin", 33.888, 36.314, "bolge"),
    ("Dikili", "İzmir", 26.887, 39.071, "bolge"),
    ("Çanakkale (Kepez)", "Çanakkale", 26.379, 40.104, "bolge"),
    ("Yalova Ro-Ro", "Yalova", 29.431, 40.690, "bolge"),
    ("Ceyhan (BOTAŞ ham petrol)", "Adana", 35.944, 36.877, "enerji"),
    ("Dörtyol (BOTAŞ)", "Hatay", 36.131, 36.853, "enerji"),
    ("Marmara Ereğlisi (LNG)", "Tekirdağ", 27.987, 40.995, "enerji"),
]
lim = gpd.GeoDataFrame(pd.DataFrame(LIMAN, columns=["ad", "il", "lon", "lat", "sinif"]),
                       geometry=gpd.points_from_xy([r[2] for r in LIMAN], [r[3] for r in LIMAN]), crs=4326)
ray = gpd.read_file(CIK / "demiryollari.gpkg")
ray_aktif = ray[ray.railway.isin(["rail", "narrow_gauge"])].to_crs(LCC)
ray_yapim = ray[ray.railway == "construction"].to_crs(LCC)
lim_l = lim.to_crs(LCC)
lim["ray_km"] = lim_l.geometry.apply(lambda p: ray_aktif.distance(p).min() / 1000).round(2)
lim["ray_yapim_km"] = lim_l.geometry.apply(lambda p: ray_yapim.distance(p).min() / 1000).round(2)
lim["demiryolu_bagli"] = lim.ray_km <= 2.0
lim.to_file(CIK / "limanlar_yuk.gpkg", driver="GPKG")
print("liman:", len(lim), "| demiryoluna 2 km içinde:", int(lim.demiryolu_bagli.sum()))
print(lim[["ad", "sinif", "ray_km", "ray_yapim_km"]].to_string(index=False))

# ---------- 3. Yolcu demiryolu istasyonları ---------------------------------------------------------------------------
ist = gpd.read_file(CIK / "istasyonlar.gpkg")
kent_rayli = {"subway", "light_rail", "funicular", "tram", "monorail", "miniature"}
ist = ist[(ist.railway.isin(["station", "halt"])) & (~ist.station.isin(kent_rayli)) & (ist.disused == "")].to_crs(LCC)
ana_hat = ray_aktif[~ray_aktif.service.isin(["yard", "siding", "spur", "crossover"])]
hizli = ray_aktif[ray_aktif.highspeed == "yes"]
sidx = ana_hat.sindex
def en_yakin(katman, idx, p, r):
    aday = idx.query(p.buffer(r))
    return katman.geometry.iloc[aday].distance(p).min() if len(aday) else 9e9


ist["hat_m"] = [en_yakin(ana_hat, sidx, p, 1000) for p in ist.geometry]
# OSM'de "yapımda" görünen hatlar (ör. Adana–Mersin, hızlı tren dönüşümü sırasında) üzerindeki istasyonlar ayrı işaretlenir:
# ana erişim ölçüsüne girmez, duyarlılıkta ("hat açıldığında") sayılır.
yapim_hat = ray_yapim[~ray_yapim.service.isin(["yard", "siding", "spur", "crossover"])]
yidx = yapim_hat.sindex
ist["hat_yapim_m"] = [en_yakin(yapim_hat, yidx, p, 1000) for p in ist.geometry]
ist = ist[(ist.hat_m <= 300) | (ist.hat_yapim_m <= 300)].copy()
ist["hat_yapimda"] = ist.hat_m > 300
hidx = hizli.sindex
# Hızlı tren durağı: adı "YHT" içeren ve hızlı tren hattına ≤ 1 km istasyon ya da YHT/hızlı tren seferlerinin durduğu bilinen
# istasyonlardan biri [İ: TCDD Taşımacılık sefer düzeni; hat bazında doğrulanmadı]. Banliyö durakları (Başkentray,
# Marmaray ara durakları, Konya–Karaman ara durakları) bu tanıma girmez.
YHT_DURAK = {"Ankara", "Sincan", "Eskişehir", "Arifiye", "İzmit", "Gebze", "Pendik", "Bostancı", "Söğütlüçeşme",
             "Bakırköy", "Halkalı", "Konya", "Karaman", "Sivas", "Edirne", "Çerkezköy"}
# (Gebze–Halkalı, Arifiye ve Sivas girişinde OSM hatlarında highspeed etiketi yok; bu yüzden listedekiler adla kabul edilir)
ist["hizli_tren"] = [(("YHT" in a) and en_yakin(hizli, hidx, p, 1200) <= 1000) or (a in YHT_DURAK and h <= 300)
                     for a, p, h in zip(ist.ad, ist.geometry, ist.hat_m)]
# aynı istasyonun düğüm + alan çift kaydı: 300 m içindeki kayıtları birleştir
ist["k"] = (ist.geometry.x // 300).astype(int).astype(str) + "_" + (ist.geometry.y // 300).astype(int).astype(str)
ist = ist.sort_values(["hizli_tren", "railway"], ascending=[False, False]).drop_duplicates("k")
ist[["railway", "ad", "train", "hizli_tren", "hat_yapimda", "osm_id", "geometry"]].to_crs(4326).to_file(CIK / "istasyonlar_yolcu.gpkg",
                                                                                         driver="GPKG")
print(f"yolcu istasyon/durak: {len(ist)} (hızlı tren durağı: {int(ist.hizli_tren.sum())}; yalnız yapımdaki hatta: "
      f"{int(ist.hat_yapimda.sum())})")
print("  hızlı tren durakları:", sorted(ist[ist.hizli_tren].ad.tolist()))

# ---------- 4. Diri faylar (GEM GAF-DB) -----------------------------------------------------------------------------
fay_yol = CIK / "diri_faylar_gem.gpkg"
if not fay_yol.exists():
    u = ("https://raw.githubusercontent.com/GEMScienceTools/gem-global-active-faults/master/geojson/"
         "gem_active_faults_harmonized.geojson")
    g = gpd.GeoDataFrame.from_features(requests.get(u, timeout=180).json()["features"], crs=4326)
    g = g[g.intersects(box(25.0, 35.0, 45.5, 42.8))].copy()
    for k in g.columns:
        if g[k].dtype == object and k != "geometry":
            g[k] = g[k].astype(str)
    g.to_file(fay_yol, driver="GPKG")
fay = gpd.read_file(fay_yol)
print(f"diri fay izi: {len(fay)} · katalog: {fay.catalog_name.value_counts().to_dict()} · "
      f"toplam {fay.to_crs(LCC).length.sum() / 1000:,.0f} km")

# ---------- 5. Kent merkezleri (her ilin ana kenti) ------------------------------------------------------------------
with rasterio.open(CIK / "izgara_nufus.tif") as d:
    nuf, tr = d.read(1), d.transform
with rasterio.open(CIK / "izgara_ilce.tif") as d:
    ilc = d.read(1)
anahtar = pd.read_csv(CIK / "izgara_ilce_anahtar.csv", dtype={"ilce_kod": str})
il_of = np.zeros(ilc.max() + 1, dtype=object)
il_of[anahtar.sira.values] = anahtar.il.values
yogun = nuf >= 1500 * 0.0625  # 1.500 kişi/km² (250 m hücre = 0,0625 km²)
lab, n = ndimage.label(yogun, structure=np.ones((3, 3)))
kume_nuf = ndimage.sum(nuf, lab, np.arange(1, n + 1))
rows = []
rr, cc = np.nonzero(lab)
lb = lab[rr, cc]
ilad = il_of[ilc[rr, cc]]
df = pd.DataFrame({"lab": lb, "il": ilad, "p": nuf[rr, cc], "x": tr.c + (cc + 0.5) * tr.a, "y": tr.f + (rr + 0.5) * tr.e})
df = df[df.il != 0]
g = df.groupby(["il", "lab"]).apply(lambda t: pd.Series({"nufus": t.p.sum(), "x": np.average(t.x, weights=t.p),
                                                         "y": np.average(t.y, weights=t.p)}), include_groups=False)
g = g.reset_index().sort_values("nufus", ascending=False).drop_duplicates("il")
pt = gpd.GeoSeries(gpd.points_from_xy(g.x, g.y), crs=LCC).to_crs(4326)
g["lon"], g["lat"] = pt.x.round(4).values, pt.y.round(4).values
g = g.sort_values("il")[["il", "nufus", "x", "y", "lon", "lat"]]
g.to_csv(CIK / "kent_merkezleri.csv", index=False, encoding="utf-8")
print(f"kent merkezi: {len(g)} il")

# ---------- 6. Rüzgâr (ERA5, Open-Meteo) -----------------------------------------------------------------------------
RZ = SON / "ulusal_plan_ruzgar_il.csv"
if not RZ.exists():
    sonuc = []
    for i in range(0, len(g), 9):
        p = g.iloc[i:i + 9]
        url = ("https://archive-api.open-meteo.com/v1/archive?latitude=" + ",".join(map(str, p.lat)) + "&longitude="
               + ",".join(map(str, p.lon)) + "&start_date=2023-01-01&end_date=2024-12-31"
               "&hourly=wind_speed_10m,wind_direction_10m&models=era5&wind_speed_unit=ms&timezone=GMT")
        for deneme in range(6):
            r = requests.get(url, timeout=300)
            if r.status_code == 200:
                break
            print("  open-meteo", r.status_code, r.text[:120])
            time.sleep(65)
        js = r.json()
        js = js if isinstance(js, list) else [js]
        for (_, satir), j in zip(p.iterrows(), js):
            hz = np.array(j["hourly"]["wind_speed_10m"], dtype=float)
            yon = np.array(j["hourly"]["wind_direction_10m"], dtype=float)
            ok = np.isfinite(hz) & np.isfinite(yon) & (hz >= 1.0)  # sakin saatler (< 1 m/s) yön sayılmaz
            sek = ((yon[ok] + 22.5) // 45).astype(int) % 8
            frek = np.bincount(sek, minlength=8) / ok.sum() * 100
            u_ = -(hz[ok] * np.sin(np.radians(yon[ok]))).mean()
            v_ = -(hz[ok] * np.cos(np.radians(yon[ok]))).mean()
            kayit = {"il": satir.il, "lon": satir.lon, "lat": satir.lat, "saat": int(np.isfinite(hz).sum()),
                     "sakin_pay": round(100 * (1 - ok.sum() / np.isfinite(hz).sum()), 1),
                     "ort_hiz": round(float(np.nanmean(hz)), 2),
                     "hakim_yon_gelen": ["K", "KD", "D", "GD", "G", "GB", "B", "KB"][int(frek.argmax())],
                     "hakim_pay": round(float(frek.max()), 1),
                     "bileske_gidis_deg": round(float(np.degrees(np.arctan2(u_, v_)) % 360), 0),
                     "kararlilik": round(float(np.hypot(u_, v_) / hz[ok].mean()), 2)}
            for k, ad in enumerate(["K", "KD", "D", "GD", "G", "GB", "B", "KB"]):
                kayit[f"f_{ad}"] = round(float(frek[k]), 1)
            sonuc.append(kayit)
        print(f"  rüzgâr {i + len(p)}/{len(g)}", flush=True)
        time.sleep(61)
    pd.DataFrame(sonuc).to_csv(RZ, index=False, encoding="utf-8")
rz = pd.read_csv(RZ)
print("hâkim rüzgâr (gelen) dağılımı:", rz.hakim_yon_gelen.value_counts().to_dict())
