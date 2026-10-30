# TR TAMİRAT — Fıtrata Uygun Şehir Araştırma Programı

**Amaç:** Türkiye'nin sürdürülebilir, insan fıtratına uygun bir şehir yapısına geçişi için gereken araştırmayı, veriyi, modeli ve uygulama planını üretmek. Hedeflenen sonuç: daha güçlü aile ve toplum yapısı; psikolojik ve fizyolojik olarak daha sağlıklı bireyler; daha güçlü ve hür vatandaşlar.

Ana belge: [00_YONETIM/ana_arastirma_plani.md](00_YONETIM/ana_arastirma_plani.md)

Güncel durum (27.10.2026): [Faz 2 sentezi](09_RAPORLAR/09_faz2_sentez.md) · [Faz 3 sentezi](09_RAPORLAR/12_faz3_sentez.md) · [Faz 4 sentezi](09_RAPORLAR/22_faz4_sentez.md) · [Toplum hedefleri](01_KAVRAMSAL_CERCEVE/toplum_hedefleri.md) · [Politika paketi v2](09_RAPORLAR/23_politika_paketi_v2.md) · [Paydaş oyunu](09_RAPORLAR/24_paydas_oyunu.md) · [Önlenebilir ölüm](09_RAPORLAR/25_ilce_ana_tablo_onlenebilir_olum.md) · [İlçe zaman paneli](09_RAPORLAR/26_ilce_zaman_paneli.md) · [Deprem olay çalışması](09_RAPORLAR/27_deprem_olay_calismasi.md) · [Evin biçimi ve toplum](09_RAPORLAR/28_konut_bicimi_iliskiler.md)

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
| `03_VERI/islenmis/ulusal_altyapi/*.tif`, `yollar.gpkg` (ulusal ızgaralar ve yol ağı) | `03_VERI/kod/ulusal_altyapi_osm.py` → `05_ANALIZ/kod/ulusal_plan_izgara.py` → `ulusal_plan_nufus.py` |
| `03_VERI/islenmis/uydu/*.tif` (pilot ilçe uydu katmanları, 30 m) | `03_VERI/kod/uydu_pilot.py` (WorldCover, Landsat ve PM2.5'i uzaktan okur) |
| `03_VERI/ham/ekonomi/**/*.pdf`, `03_VERI/ham/enerji/**/*.pdf` (resmî raporlar, mevzuat metinleri, bültenler; telif kurumlarında) | Her klasörün `kaynaklar.md` dosyasında adıyla ve kurumuyla listeli; kurumun sitesinden indirilip aynı ada konur. `ekonomi_veri.py` TÜRK-İŞ Eylül 2026 bültenini (`turkis/turkis_aclik_yoksulluk_2026.09.pdf`) okur |
| `03_VERI/ham/stres/literatur/` (makale künye ve özet önbelleği) | `05_ANALIZ/kod/stres_literatur_dogrula.py` (Crossref, PubMed, Europe PMC'den yeniden çeker) |
| `03_VERI/ham/konut_bicimi_literatur/` (makale künye ve özet önbelleği) | `05_ANALIZ/kod/konut_bicimi_literatur_dogrula.py` (Crossref, PubMed, Europe PMC, Semantic Scholar, OpenAlex'ten yeniden çeker) |

**Faz 3 mahalle ve uydu zinciri:** `osm_pilot_mahalle.py` → `tkgm_mahalle.py` → `uydu_pilot.py` → `05_ANALIZ/kod/fue_mahalle.py` → `uydu_ulusal.py` → `fue_ilce_gecerlilik.py` → `fue_grafikler.py`, `04_HARITA/kod/fue_haritalari.py`, `uydu_haritalari.py`.

**Faz 4 zincirleri** (her paket kendi başına çalışır; `05_ANALIZ/kod/` altında):

| Paket | Sıra |
|---|---|
| Stres (Rapor 14) | `stres_veri.py`, `stres_literatur_dogrula.py` → `stres_endeks.py` → `stres_grafikler.py`, `stres_harita.py` |
| Konut (Rapor 15) | `07_TASARIM_CIZIM/konut_rehberi/kod/uret.py` |
| Malzeme (Rapor 16) | `07_TASARIM_CIZIM/malzeme/kod/hepsini_calistir.py` |
| Ulusal çerçeve (Rapor 17) | `03_VERI/kod/ulusal_altyapi_osm.py` → `ulusal_plan_izgara.py` → `ulusal_plan_nufus.py` → kalan `ulusal_plan_*.py` |
| Enerji (Rapor 18) | `enerji_veri.py` → `enerji_mahalle.py` → `enerji_senaryo.py` → `enerji_kademe.py` → `enerji_grafikler.py` |
| İsraf (Rapor 19) | `israf_veri_indir.py`, `israf_ghsl_arazi.py` → `israf_hesap.py` → `israf_grafikler.py` |
| Ekonomi (Rapor 20) | `ekonomi_veri.py` → `ekonomi_dagilim.py` → `ekonomi_ticaret_yeterlilik.py` → `ekonomi_kademe.py` → `ekonomi_grafikler.py` |
| Ölçeklenebilir şehir (Rapor 21) | Enerji, israf ve ekonomi paketlerinden sonra `07_TASARIM_CIZIM/olceklenebilir_sehir/kod/kademe_modeli.py`, `kademe_semasi.py` |
| Politika paketi v2 (Rapor 23) | `ekonomi_veri.py` sonrası `08_MEVZUAT_POLITIKA/politika_v2/politika_v2_mali.py` (Rapor 20'nin dağılım modelini içinden çalıştırır) |
| Paydaş oyunu (Rapor 24) | `politika_v2_mali.py` sonrası `06_SIMULASYON/kod/paydas_oyunu.py` |
| İlçe ana tablosu ve önlenebilir ölüm (Rapor 25) | `fue_ilce_gecerlilik.py`, `stres_endeks.py` ve ulusal ızgara zinciri sonrası `05_ANALIZ/kod/ilce_ana_tablo.py` |
| Deprem olay çalışması (Rapor 27) | `ilce_ana_tablo.py` sonrası `05_ANALIZ/kod/deprem_olay.py`; USGS ShakeMap MMI dosyaları depoda (`03_VERI/ham/deprem/`) |
| İlçe zaman paneli (Rapor 26) | `05_ANALIZ/kod/ilce_ghsl_degisim.py` → `ilce_ana_tablo.py` → `ilce_zaman_paneli.py`; ilçe nüfusu 2014–2025 MEDAS'tan tarayıcıyla alındı ve depoda (`03_VERI/islenmis/ilce_nufus_2014_2025.csv`) |
| Evin biçimi ve toplum (Rapor 28) | `ilce_ana_tablo.py` sonrası `05_ANALIZ/kod/konut_bicimi_iliskiler.py`; literatür `konut_bicimi_literatur_dogrula.py`; TÜRKPATENT il tabloları depoda (`03_VERI/ham/inovasyon/`) |

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
| Landsat 8/9 (USGS), MODIS (NASA), USGS ShakeMap (2023 Kahramanmaraş depremleri) | Kamu malı |
| TÜRKPATENT (patent ve faydalı model başvurularının illere göre dağılımı) | Kurum, kaynak gösterilerek |
| Microsoft Global ML Building Footprints | ODbL 1.0 (depoya konmadı) |
| GEM Global Active Faults | CC BY-SA 4.0 |
| Copernicus DEM GLO-90 | Copernicus DEM lisansı, kaynak gösterilerek |
| Ember (elektrik verisi), Open-Meteo (iklim arşivi) | CC BY 4.0 |
| Dünya Bankası (WDI, B-READY), OECD (Revenue Statistics, PMR) | CC BY 4.0 |
| Eurostat, JRC PVGIS ve GHSL 1 km | Avrupa Komisyonu yeniden kullanım politikası, kaynak gösterilerek |
| TEİAŞ, ETKB, EPDK, GİB, HMB, SBB, Muhasebat, TESK, TOBB, TÜRK-İŞ | Kurum, kaynak gösterilerek. Sayısal tablolar depoda; PDF belgeler konmadı |

## Lisans

| Ne | Lisans | Dosya |
|---|---|---|
| Kod (`*.py`) | MIT | [LICENSE](LICENSE) |
| Raporlar, metinler, tablolar, haritalar, grafikler ve teknik çizimler | Creative Commons Atıf 4.0 Uluslararası (CC BY 4.0) | [LICENSE-CC-BY-4.0.txt](LICENSE-CC-BY-4.0.txt) |
| Üçüncü taraf kaynaklardan türetilen veriler | Kaynağın kendi lisansı (bkz. "Veri kaynakları ve atıf"). OpenStreetMap türevleri ODbL 1.0 ile paylaşılır | — |

Atıf için [CITATION.cff](CITATION.cff): Sağır, H. C. (2026). *TR TAMİRAT — Fıtrata Uygun Şehir Araştırma Programı* (Sürüm 0.3). https://github.com/Huseyincansagir/tr-tamirat
