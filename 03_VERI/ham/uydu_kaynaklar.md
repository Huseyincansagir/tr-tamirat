# Uydu verisi (Faz 3, FUE v0.2) — kaynaklar, erişim ve doğrulama

*İndirme ve uzaktan okuma: 26–27 Ekim 2026, kullanıcı onayıyla. Hiçbir kaynak hesap ya da API anahtarı gerektirmedi.*

| Veri | Sağlayıcı · lisans | Erişim | Projede |
|---|---|---|---|
| ESA WorldCover 2021 v200, 10 m arazi örtüsü | ESA · CC BY 4.0 | `https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_<karo>_Map.tif` (3°×3° bulut uyumlu GeoTIFF; GDAL `/vsicurl/` ile yalnız gereken pencere okunur, dosya indirilmez) | Pilot: tam çözünürlük. Ulusal: 8× genel bakış katmanı (≈ 80 m, çoğunluk sınıfı) |
| ACAG V6.GL.03 yüzey PM2.5 (CNN hibrit), 0,01° | Washington Üniversitesi Atmospheric Composition Analysis Group · CC BY 4.0 · atıf: satpm.org | `https://satpmdata.s3.amazonaws.com/V6GL03/CNNPM25/Annual/<EU|GL>/` (anonim S3) | Pilot: Avrupa dosyaları 2022–2024 (`pm25/*.nc`, depoya konmadı). Ulusal: küresel dosyanın Türkiye penceresi uzaktan HDF5 okumasıyla alındı → `pm25/V6GL03_CNNPM25_TR_2022_2024.tif` |
| Landsat 8/9 Collection 2 Level-2 yüzey sıcaklığı (ST_B10) ve QA_PIXEL | USGS · kamu malı | Microsoft Planetary Computer STAC (`landsat-c2-l2`); anonim SAS belirteci `https://planetarycomputer.microsoft.com/api/sas/v1/token/landsat-c2-l2` | Pilot ilçe başına 14 yaz sahnesi (2022–2025), bulut ve gölge maskeli ortanca; liste `islenmis/uydu/landsat_sahneler.csv` |
| MODIS Aqua MYD11A2 v061, 8 günlük 1 km gündüz yüzey sıcaklığı | NASA LP DAAC · kamu malı | Planetary Computer (`modis-11A2-061`); belirteç depolama kabı için alınır: `.../sas/v1/token/modiseuwest/modis-061-cogs` | Karolar h19v04, h20v04, h21v04, h20v05, h21v05; Temmuz–Ağustos 2023 ve 2024 ortalaması → `modis/MYD11A2_yaz_<karo>.tif` |

**Kullanılmayan:** Copernicus CAMS Avrupa hava kalitesi yeniden analizi (0,1°). Atmosphere Data Store indirme için hesap ve API anahtarı istiyor; bu çalışmada hesap açılamıyor.

**Ölçüler:** Dönüşümler WorldCover sınıflarıyla yapıldı (10 ağaç; 20, 30, 90 çalı, çayır, sulak alan; 50 yapılı alan).

- **Ağaç, yeşil ve yapılı alan payı:** 300 m yarıçaplı daire içindeki pay, FFT evrişimiyle hesaplandı.
- **Landsat yüzey sıcaklığı:** °C = DN × 0,00341802 + 149,0 − 273,15. Maskelenen pikseller (QA_PIXEL bit 0–4): dolgu, genişletilmiş bulut, sirrus, bulut, gölge.
- **MODIS yüzey sıcaklığı:** °C = DN × 0,02 − 273,15.

**Doğrulama:**

| Sınama | Sonuç |
|---|---|
| Landsat, Fatih — su yüzeyi | Haliç 27,3 °C, Marmara 26,5 °C |
| Landsat, Fatih — park ve doku | Gülhane Parkı 35,3 °C, Aksaray 45,6 °C |
| Landsat, Kayseri — kent ve tarla | Merkez 45,3 °C, Erkilet tarlaları 49,8 °C (yarı kurak bölgede gündüz kent serin) |
| WorldCover ağaç payı, Fatih | 8× genel bakışta %12,2, tam çözünürlükte %14,8 |
| PM2.5 yönü | Po Ovası 18,4 > Alpler 9,1 µg/m³; deniz boş; Avrupa ve küresel dosyalar Fatih'te aynı (≈ 20–21 µg/m³) |
| Ulusal kapsama | 973 ilçenin hepsinde değer var |
