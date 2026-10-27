# TR TAMİRAT — Fıtrata Uygun Şehir Araştırma Programı

**Amaç:** Türkiye'nin sürdürülebilir, insan fıtratına uygun bir şehir yapısına geçişi için gereken araştırmayı, veriyi, modeli ve uygulama planını üretmek. Hedeflenen sonuç: daha güçlü aile ve toplum yapısı; psikolojik ve fizyolojik olarak daha sağlıklı bireyler; daha güçlü ve hür vatandaşlar.

Ana belge: [00_YONETIM/ana_arastirma_plani.md](00_YONETIM/ana_arastirma_plani.md)

Güncel durum (26.10.2026): [Faz 2 sentezi](09_RAPORLAR/09_faz2_sentez.md) · [Faz 3 sentezi](09_RAPORLAR/12_faz3_sentez.md)

## Klasör yapısı

| Klasör | İçerik |
|---|---|
| `00_YONETIM` | Ana araştırma planı, yol haritası, karar kayıtları |
| `01_KAVRAMSAL_CERCEVE` | "Fıtrata uygun şehir" tanımı, boyutlar, Fıtrat Uyum Endeksi (FUE), hipotezler |
| `02_LITERATUR` | Literatür haritası, kaynakça, örnek uygulamalar (vaka analizleri) |
| `03_VERI` | Veri kaynakları kataloğu; `ham/` indirilen veriler, `islenmis/` temizlenmiş tablolar |
| `04_HARITA` | Türkiye ve pilot şehir haritaları (PNG/SVG, GeoPackage, etkileşimli HTML) |
| `05_ANALIZ` | İstatistiksel ve mekânsal analizler, kodlar, sonuç tabloları |
| `06_SIMULASYON` | Zihinsel simülasyonlar (persona senaryoları) ve hesaplamalı modeller |
| `07_TASARIM_CIZIM` | Tasarım parametreleri, mahalle modeli, tipolojiler, teknik çizimler |
| `08_MEVZUAT_POLITIKA` | Mevzuat analizi, politika önerileri, finansman modelleri |
| `09_RAPORLAR` | Ara ve nihai raporlar, özetler |

## Çalışma ilkeleri

1. **Kanıta dayalılık:** Her sayının yılı ve kaynağı olur. Doğrulanamayan bilgi "doğrulanmadı" diye işaretlenir.
2. **Nedensellik dikkati:** Korelasyon nedensellik sayılmaz; gelir, eğitim, kültür gibi karıştırıcı etkenler ayrıca ele alınır.
3. **İki dilli çerçeve:** Değer dili (fıtrat, makāsıd) ile bilim dili (sağlık, sosyal sermaye, sürdürülebilirlik) birbirine çevrilebilir tutulur.
4. **Hürriyetle tutarlılık:** Önerilen hiçbir dönüşüm zorlayıcı olamaz; gönüllülük, mülkiyet hakkı ve katılım esastır.
5. **Tekrarlanabilirlik:** Analizler kodla (Python) yapılır, veri ve kod klasörlerde saklanır.

## Yeniden üretim

Kod Python 3.11 ile yazıldı. Kullanılan başlıca paketler: pandas, geopandas, rasterio, shapely, scipy, statsmodels, matplotlib, osmium (pyosmium), requests. Bütün veri kaynakları anahtarsız erişilebilir; erişim yolları ve doğrulamalar `03_VERI/ham/*/kaynaklar.md` dosyalarında yazılı.

Depo boyutunu makul tutmak için aşağıdaki büyük dosyalar yüklenmedi (`.gitignore`). Hepsi kaynağından indirilir ya da betikle yeniden üretilir:

| Dışarıda kalan | Nasıl geri gelir |
|---|---|
| `03_VERI/ham/osm/turkey-latest.osm.pbf` (652 MB) | Geofabrik: `https://download.geofabrik.de/europe/turkey-latest.osm.pbf` |
| `03_VERI/ham/ghsl/` (GHSL R2023A bina yüksekliği 2018 ve nüfus 2020, 100 m, 4'er karo: R4_C21, R4_C22, R5_C21, R5_C22) | JRC GHSL veri portalı |
| `03_VERI/ham/bina/` (Microsoft Global ML Building Footprints, 4 karo) | Microsoft'un dizin dosyasından (`dataset-links.csv`, Türkiye) quadkey 120323222, 120323332, 122100313, 122101103 karoları; `ms_<quadkey>/<quadkey>.csv.gz` olarak konur (ayrıntı: Rapor 11 §1.2) |
| `03_VERI/ham/pm25/*.nc` (ACAG V6.GL.03 PM2.5, Avrupa, 2022–2024) | `https://satpmdata.s3.amazonaws.com/V6GL03/CNNPM25/Annual/EU/` |
| `03_VERI/islenmis/pilot_osm/`, `osm_kavsaklar.parquet` | `03_VERI/kod/osm_pilot_mahalle.py`, `03_VERI/kod/osm_ilce.py` (PBF'ten) |
| `03_VERI/islenmis/uydu/*.tif` (pilot ilçe uydu katmanları, 30 m) | `03_VERI/kod/uydu_pilot.py` (WorldCover, Landsat ve PM2.5'i uzaktan okur) |

**Faz 3 mahalle ve uydu zinciri:** `osm_pilot_mahalle.py` → `tkgm_mahalle.py` → `uydu_pilot.py` → `05_ANALIZ/kod/fue_mahalle.py` → `uydu_ulusal.py` → `fue_ilce_gecerlilik.py` → `fue_grafikler.py`, `04_HARITA/kod/fue_haritalari.py`, `uydu_haritalari.py`.

## Veri kaynakları ve atıf

Depodaki işlenmiş veriler aşağıdaki kaynaklardan türetildi. Yeniden kullanırken kaynaklara atıf yapın.

| Kaynak | Lisans / koşul |
|---|---|
| OpenStreetMap (Geofabrik Türkiye çıkarımı) | © OpenStreetMap katkıcıları, ODbL 1.0. OSM'den türetilen tablolar (`osm_*`, `pilot_osm`, mahalle sınırları) aynı lisansla paylaşılır |
| TÜİK (ADNKS, doğum, ölüm, evlenme-boşanma, MEDAS) | TÜİK, kaynak gösterilerek |
| TCMB EVDS (konut fiyat ve kira) | TCMB, kaynak gösterilerek |
| GHSL R2023A (JRC) | CC BY 4.0 |
| geoBoundaries (ADM1, ADM2) | CC BY 4.0 |
| TKGM MEGSİS mahalle sınırları | Kamuya açık servis; yeniden dağıtım koşulları belirtilmemiş |
| ESA WorldCover 2021 | CC BY 4.0 |
| ACAG V6.GL.03 PM2.5 (Washington Üniversitesi, satpm.org) | CC BY 4.0 |
| Landsat 8/9 (USGS), MODIS (NASA) | Kamu malı |
| Microsoft Global ML Building Footprints | ODbL 1.0 (depoya konmadı) |
