# İsraf, fire ve kaçak analizi: ham veri ve kaynaklar

*27 Ekim 2026 · Faz 4 · Rapor 6 ([09_RAPORLAR/19_israf_fire_kacak.md](../../../09_RAPORLAR/19_israf_fire_kacak.md))*

Bu klasördeki her dosya ya bir betikle yeniden indirilir ya da bir resmî belgeden elle aktarıldı. Her sayının değeri, yılı, kaynağı ve işareti `israf_parametreler.csv` içinde tek satırda durur. Hesap betikleri bu dosyayı okur; elle sayı yazılmaz.

**İşaretler:** [D] birincil kaynakta okundu · [İ] ikincil aktarım (haber, köşe yazısı, kurum bülteni) · [DY] doğrulanamadı · [V] varsayım · [H] hesaplandı.

## 1. Dosyalar

| Dosya | İçerik | Nasıl elde edildi | İşaret |
|---|---|---|---|
| `sdmx/*.json` (14 akış) | TÜİK SDMX yanıtları (JSON-stat 2.0) | `05_ANALIZ/kod/israf_veri_indir.py` | [D] |
| `epdk_elektrik_dagitim_kayip.csv` | 21 dağıtım şirketi: illeri, 2023–2025 kayıp oranları, 2024 ve 2025 hedefleri, 2025 faturalanan tüketim (dağıtım ve iletim bağlı) | EPDK raporlarından elle aktarıldı. Toplamlar rapordaki genel toplamla karşılaştırıldı (214.756,70 ve 73.723,27 GWh; betikte `assert`) | [D] |
| `israf_parametreler.csv` | Hesaplarda kullanılan bütün sayılar | Elle derlendi; her satırda kaynak ve işaret | karışık |
| `ghsl/*_tr_1km.tif` | GHSL R2023A yapılı yüzey ve nüfus, 2000 ve 2020, 1 km, Türkiye penceresi | `05_ANALIZ/kod/israf_ghsl_arazi.py` (zip indirilmeden uzaktan okundu) | [D] |
| `ghsl_il_yapili_nufus_2000_2020.csv` | İl bazında yapılı alan (ha) ve GHSL nüfusu | aynı betik | [H] |

## 2. TÜİK SDMX akışları

Uç nokta: `POST https://databrowser2.tuik.gov.tr/api/core/nodes/1/datasets/TR,<AKIŞ>,1.0/data`. Gövde `[]` hepsini, `[{"id":boyut,"filterValues":[...],"type":"CodeValues","period":0}]` süzülmüş veriyi döndürür. Katalog: `GET .../api/core/nodes/1/catalog`. Anahtar gerekmiyor. Veri portalı (veriportali.tuik.gov.tr) komut satırına kapalı olduğu için bültenlere değil bu akışlara dayanıldı.

| Akış | Kullanım | Dönem |
|---|---|---|
| `DF_SU_ATIKSU_BELEDIYE_CEKILEN_DAGITILAN_V1` | İl bazında belediyelerce çekilen ve dağıtılan su (bin m³) → kayıp-kaçak vekili | 2020, 2022, 2024 |
| `DF_SU_ATIKSU_BELEDIYE_GOSTERGE_V1` | Türkiye: şebeke nüfusu, kişi başı su, arıtma | 1994–2024 |
| `DF_ATIK_BELEDIYE_HIZMET_YONETIM_GOSTERGE_V1` | Türkiye: üretilen ve toplanan belediye atığı, bertaraf yöntemleri | 1994–2024 |
| `DF_ATIK_BELEDIYE_ATIKYONETIMI_V1` | İl bazında toplanan atık ve belediye çöplüğüne giden miktar | 2020–2024 |
| `DF_ATIK_BERTARAF_GERI_KAZANIM_TESIS_V1` | Düzenli depolama, yakma, kompost, ortak yakma ve geri kazanım tesisleri | 2020–2024 |
| `DF_ATIK_IMALAT_SANAYI_GOSTERGELER_V1` | İmalat sanayi atığı ve bertaraf yolu | 2000–2024 |
| `DF_SERA_GAZI_EMISYONLARI` | Kaçak metan (1.B.2), düzenli depolama metanı (5.A) | 1990–2024 |
| `DF_TARIM_URUNLERI_UFE_MADDE_FIYAT_V2` | Tarım ürünleri üretici fiyatları (TL/kg, aylık) | 2024-01 – 2026-09 |
| `DF_MOTORLU_KARA_TASIT_ILLER_V3` | İl bazında trafiğe kayıtlı otomobil (Aralık) | 2005–2025 |
| `DF_TASIT_KILOMETRE_TASIT_CINS_V2` | Taşıt-km | 2015–2024 |
| `UH_BH_GSYH_CARI` | GSYH, cari fiyatlarla (2024: 44,587 trilyon TL) | 2000–2024 |
| `DF_MADDE_AKIS_HESAPLARI` | Madde akış hesapları (yurt içi malzeme tüketimi) | 2010–2023 |
| `DF_TUFE_SDMX_TT07` | TÜFE seçilmiş madde ortalama fiyatları (akaryakıt, elektrik, gaz) | yalnız 2026-08, 2026-09 |
| `DF_TUFE_SDMX_TT01` | TÜFE genel endeksi (2025=100) | 2005-01 – 2026-09 |

**Su verisinin tanımı:** "Çekilen su", belediyelerin içme ve kullanma suyu şebekesi için kaynaklardan çektiği; "dağıtılan su", şebekeyle dağıtılan sudur. Aradaki fark; fiziksel kaçakları, sayaç hatalarını, kaçak kullanımı, faturalanmayan resmî kullanımı ve arıtma sürecindeki kayıpları birlikte içerir. Bu yüzden IWA tanımındaki "gelir getirmeyen su"ya yakın bir **vekil** olarak kullanıldı [H].

## 3. Belgeler

| Belge | Kurum, yıl | Kullanılan bölüm | URL | İşaret |
|---|---|---|---|---|
| 2025 Yılı Elektrik Piyasası Gelişim Raporu | EPDK, 2026 | Tablo 1.11 (bölgelere göre faturalanan tüketim), Tablo 5.2 (kayıp oranları), PTF, iletim kaybı | https://www.epdk.gov.tr/Detay/DownloadDocument?id=aetLyVmDSsI= | [D] |
| 2024 Yılı Elektrik Piyasası Gelişim Raporu | EPDK, 2025 | 2023 kayıp oranları ve 2024 hedefleri | https://www.epdk.gov.tr/Detay/DownloadDocument?id=fANZARDA1UU= | [D] |
| 2025 Yılı Doğal Gaz Piyasası Gelişim Raporu | EPDK, 2026 | Tablo 8.1–8.2 (tüketim, kayıplar, sistem kullanımı), Tablo 9.1 (fiyatlar), 7.5 (kaçak kullanım kesintileri) | https://www.epdk.gov.tr/Detay/DownloadDocument?id=fSTHy8vYN/Q= | [D] |
| İl → dağıtım bölgesi eşlemesi | ELDER, Üyelerimiz | 81 il, 21 şirket | https://elder.org.tr/kurumsal/uyelerimiz | [D] |
| İçme Suyu Temin ve Dağıtım Sistemlerindeki Su Kayıplarının Kontrolü Yönetmeliği | Orman ve Su İşleri Bakanlığı, RG 08.05.2014/28994 | md. 9 (kayıp hedefleri). Sonraki değişikliklerle sürelerin uzayıp uzamadığı doğrulanmadı [DY] | https://www.resmigazete.gov.tr/eskiler/2014/05/20140508-1.htm | [D] |
| Food Waste Index Report 2024 | UNEP, 2024 | Türkiye hane, gıda hizmeti, perakende (2022). Türkiye'nin kendi ölçümü yok; tahmin "düşük güven" | https://digitallibrary.un.org/record/4042857 ; https://unstats.un.org/sdgapi/v1/sdg/Indicator/Data?indicator=12.3.1&areaCode=792 | [D] |
| Gıda, Su Kaybı ve İsrafı, böl. 1 | TÜBA, 2024 | TZOB (2022) kayıp rakamları; TMO ekmek araştırması; Ticaret Bakanlığı 2018 İsraf Raporu (%23) | https://tuba.gov.tr/files/yayinlar/raporlar/TUBA-978-625-6110-08-3_ch01.pdf | [İ] |
| Ekmek israfı ölçümleri (2012: günde 6 milyon; 2013: 4,9 milyon) | Bakanlık soru önergesi yanıtı, AA 20.04.2014 | — | https://www.memurlar.net/haber/464907/ekmek-israfi-azaldi.html | [İ] |
| "Her yıl 18,8 milyon ton gıda çöpe gidiyor" | Bakan Pakdemirli, Gıdanı Koru lansmanı, TRT Haber 20.05.2020 | Yöntemi açıklanmamış; hesaba katılmadı | https://www.trthaber.com/haber/yasam/bakan-pakdemirli-her-yil-188-milyon-ton-gida-cope-gidiyor-486236.html | [İ] |
| Tarımsal Üretimin Planlanması Hakkında Yönetmelik | RG 14.09.2023/32309 | Üretim izni; 2027'den havza ürün deseni | https://www.alomaliye.com/2023/09/14/tarimsal-uretimin-planlanmasi-hakkinda-yonetmelik/ | [İ] |
| KDV Kanunu md. 17/2-b | 3065 s. Kanun | Gıda bankacılığına bağışlanan gıdada KDV istisnası | https://www.mevzuat.gov.tr/MevzuatMetin/1.5.3065.pdf | [D] |
| TomTom Traffic Index 2025 | TomTom, 2026 | İstanbul, Ankara, İzmir, Antalya, Bursa, Adana: yoğun saatte yıllık kayıp | https://www.tomtom.com/traffic-index/istanbul-traffic/ (diğer kentler aynı kalıpla) | [D] |
| 2. Ulusal Enerji Verimliliği Eylem Planı 2024–2030 | ETKB | Bina ve hizmetler 39,2 MTEP; atık ısı 1.600 kTEP; kojenerasyon 2.515 MWe; 1,6 milyar USD/yıl | https://enerji.gov.tr/bilgi-merkezi-enerji-verimliligi-ulusal-enerji-verimliligi-eylem-plani | [D] |
| UEVEP 2025 Gelişim Raporu Yönetici Özeti | ETKB | 2025'te ≈99 bin binada yalıtım, 260 bin TEP tasarruf | aynı sayfa | [D] |
| Basın bültenleri (30.10.2024; 03.04.2025; Eylül 2025) | İZODER | %75 yalıtımsız; 12–15 milyar USD; TÜİK GYKA 2024'ten %30,2 aktarımı | https://www.izoder.org.tr/dosyalar/basinBultenleri/dunya-tasarruf-gunu-bulteni-r2.pdf | [İ] |
| Global E-waste Monitor 2024 | ITU/UNITAR, 2024 | Türkiye 1.077 milyon kg, 12,7 kg/kişi, belgelenmiş toplama 186,9 milyon kg; dünya malzeme değeri 91 milyar USD | https://ewastemonitor.info/wp-content/uploads/2024/03/GEM_2024_18-03_web_page_per_page_web.pdf | [D] |
| SDG 12.5.1 belediye atığı geri dönüşümü | OECD/Eurostat, UN SDG veri tabanı | 2021: 4,32 Mt (%12,83) | https://unstats.un.org/sdgapi/v1/sdg/Indicator/Data?indicator=12.5.1&areaCode=792 | [D] |
| Sıfır Atık geri kazanım oranı (%36,08, 2024; %37,53, 2025) | ÇŞİDB açıklaması, Milliyet 30.03.2026 | Tanımı OECD'den geniş | https://www.milliyet.com.tr/7562916 | [İ] |
| 2023 Kahramanmaraş ve Hatay Depremleri Raporu | SBB, Mart 2023 | s. 65–66: 100–120 milyon m³ enkaz, 2,5 t/m³, bertaraf 41,85 milyar TL | https://www.sbb.gov.tr/wp-content/uploads/2023/03/2023-Kahramanmaras-ve-Hatay-Depremleri-Raporu.pdf | [D] |
| Konut stoku ≈31 milyon (Bakan aktarımı) | N. Bakır, Dünya, 29.07.2025 | Resmî boş konut sayısı değil | https://www.dunya.com/kose-yazisi/ulkede-85-milyon-konut-bos-tutuluyor/787130 | [İ] |
| Kur ve kira | TCMB EVDS | USD/TL yıllık ortalama; birim kira (bie_bk) | https://evds3.tcmb.gov.tr | [D] |
| GSYH 2025 | World Bank WDI (TÜİK kaynaklı), 08.10.2026 | 63,021 trilyon TL | https://api.worldbank.org/v2/country/TUR/indicator/NY.GDP.MKTP.CN?format=json | [İ] |
| GHSL R2023A | JRC | GHS-BUILT-S ve GHS-POP, 1 km | https://human-settlement.emergency.copernicus.eu/download.php | [D] |

## 4. Bulunamayanlar (arama kotası doldu ya da kaynak yok)

- Ambalaj atığı: piyasaya sürülen ve geri kazanılan miktar; Depozito Yönetim Sistemi'nin (TÜDAM) başlangıç tarihi ve hedefleri [DY].
- İnşaat ve yıkıntı atığının yıllık miktarı ve geri kazanım oranı; deprem enkazının fiilen geri kazanılan payı [DY].
- Belediye atığının bileşimi (karakterizasyon) ve ikincil hammadde fiyatları [DY]. Hesapta [V] aralıklar kullanıldı.
- Doğal gaz dağıtım şebekesinde kayıp-kaçak oranı ve ithal gazın birim maliyeti (USD/1000 m³) [DY]. BOTAŞ ithalatı gümrük istatistiklerinde (Comtrade HS 2711) görünmüyor.
- İBB'nin trafik sıkışıklığı maliyeti, INRIX İstanbul, kamyonlarda boş sefer oranı [DY].
- Endüstriyel simbiyoz projelerinin (İskenderun Körfezi, BEBKA, OSTİM) sayısal sonuçları [DY].
- Fiyat düşüşü yüzünden tarlada bırakılan ürün miktarı; sözleşmeli üretimin payı; gıda bankalarının kurtardığı gıda [DY].
- İl bazında boş konut oranı (TÜİK BKNA 2021 hane temellidir, boş konutu saymaz) [DY].
- Belediye su tarifeleri (İSKİ vb. sayfalar içeriği komut satırına açmadı) [DY].
