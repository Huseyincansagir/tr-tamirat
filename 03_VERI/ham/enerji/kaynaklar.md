# Enerji analizi: ham veri ve kaynaklar

*27 Ekim 2026 · Faz 4 · Rapor 5 ([09_RAPORLAR/18_enerji.md](../../../09_RAPORLAR/18_enerji.md))*

Bu klasördeki her dosya `05_ANALIZ/kod/enerji_veri.py` ile kaynağından indirilir ya da önbellekten okunur. Elle derlenen sayılar betiğin içinde iki listede durur: `GOSTERGELER` (→ `enerji_turkiye_gostergeler.csv`) ve `MALIYET` (→ `enerji_lcoe_karsilastirma.csv`). Her satırda değer, yıl, kaynak ve işaret var. Model varsayımları tek yerde: `enerji_ortak.py` → `enerji_varsayimlar.csv`; teknoloji maliyetleri `enerji_senaryo.py` → `enerji_maliyet_varsayim.csv`.

**İşaretler:** [D] birincil kaynakta okundu · [İ] ikincil aktarım (haber, derleyici, kurum bülteni) · [DY] doğrulanamadı · [V] varsayım · [H] hesaplandı.

## 1. Dosyalar

| Klasör / dosya | İçerik | Nasıl elde edildi | Boyut | İşaret |
|---|---|---|---|---|
| `teias/T63_uretim_kaynak_2000_2025.xls` | Kaynak bazında brüt üretim, 2000–2025 (2025 geçici) | `https://webim.teias.gov.tr/file/<kimlik>` (kimlikler betikte) | < 0,1 MB | [D] |
| `teias/T9_kurulu_guc_2006_2025.xls` | Kaynak bazında kurulu güç, yıl sonu | aynı | < 0,1 MB | [D] |
| `teias/T74_aylik_uretim_2024.xls`, `..._2025.xls` | Aylık üretim (rüzgâr ve jeotermal ayrı) | aynı | < 0,1 MB | [D] |
| `teias/T75_gunes_lisansli_lisanssiz_*.xls` | Güneşte lisanslı / lisanssız ayrımı | aynı | < 0,1 MB | [D] |
| `teias/T48, T58, T60, T26` | Brüt talep, kişi başı tüketim, net tüketim ve kayıplar, anlık puant | aynı | < 0,1 MB | [D] |
| `etkb/ulusal_enerji_denge_2024.xlsx` | 2024 Ulusal Enerji Denge Tablosu (orijinal birim ve bin TEP; yayım 15.11.2025) | `enerji.gov.tr/Media/Dizin/EIGM/tr/Raporlar/Ulusal_Enerji_Denge_Tablolari/2024_r1.xlsx` | 0,07 MB | [D] |
| `etkb/sebeke_emisyon_faktoru_2023.pdf` | 2023 elektrik üretimi ve tüketim noktası emisyon faktörleri (yayım 26.12.2025) | ETKB-EVÇED (adres betikte) | 0,15 MB | [D] |
| `ember/ember_turkiye_yillik.csv` | Ember yıllık tam sürümünün yalnız Türkiye satırları | Ember açık veri (≈ 50 MB tam dosya indirilir, Türkiye süzülür, tam dosya silinir) | 0,2 MB | [İ] |
| `pvgis/seri_<ilçe>_<yönelim>.json.gz` | 10 pilot ilçe × 5 yönelim (G20, D20, B20, D10, B10), saatlik PV üretimi ve sıcaklık, 2019–2023 | PVGIS 5.3 `seriescalc` | ≈ 0,5 MB/dosya | [D] |
| `pvgis/seri_ruzgar_<saha>.json.gz` | 6 rüzgâr bölgesi noktası, saatlik 10 m rüzgâr hızı (ERA5) | PVGIS 5.3 `seriescalc` | ≈ 0,5 MB/dosya | [D] |
| `pvgis/il_opt_<il>.json.gz`, `il_yatay_<il>.json.gz` | 81 il: optimum eğimli ve yatay 1 kWp yıllık/aylık üretim | PVGIS 5.3 `PVcalc` | ≈ 1,5 kB/dosya | [D] |
| `pvgis/pilot_opt_<ilçe>.json.gz`, `pilot_g20_<ilçe>.json.gz` | 10 pilot nokta: `PVcalc?peakpower=1&loss=14` (optimum ve 20° güney) | PVGIS 5.3 `PVcalc` | ≈ 1,5 kB/dosya | [D] |

Toplam ≈ 32 MB; en büyük dosya < 1 MB.

## 2. PVGIS (JRC) erişimi

- **Uç noktalar:** `https://re.jrc.ec.europa.eu/api/v5_3/PVcalc` ve `.../seriescalc`. Anahtar gerekmiyor.
- **Ortak parametreler:** `peakpower=1`, `loss=14`, kristal silisyum, `outputformat=json`. Işınım veritabanı SARAH3 (PVcalc: 2005–2023 ortalaması; seriescalc: 2019–2023 saatlik).
- **Çatı serileri:** `mountingplace=building` (çatıya bitişik montaj, panel daha sıcak). Bu yüzden aynı noktada PVcalc'ın serbest montajlı değerinden ≈ %3–5 düşük çıkar. Sağlama `enerji_pilot_noktalar.csv` içinde (`pvcalc_g20_kwh_kwp` ↔ `seri_g20_2019_2023_kwh_kwp`).
- **Önbellek:** Her yanıt `gzip` JSON olarak saklanır; dosya varsa istek atılmaz. İlk çalıştırma ≈ 250 istek, 10–20 dk.
- **Nokta seçimi:** Pilot ilçede kentsel mahallelerin nüfus ağırlıklı merkezine en yakın mahallenin iç noktası. İllerde en kalabalık ilçenin iç noktası. **Uyarı:** Osmaniye'de bu nokta Amanos eteğine düştü; ufuk gölgesiyle 1.226 kWh/kWp çıktı (kent merkezi değeri daha yüksek olmalı) [DY].
- **Saat dilimi:** PVGIS UTC verir. Seriler UTC+3'e kaydırıldı (Türkiye 2016'dan beri kalıcı yaz saatinde).

## 3. Bu oturumda doğrulanan kaynaklar (27.10.2026)

| Konu | Bulunan | Kaynak | İşaret |
|---|---|---|---|
| Lazard LCOE+ v19 | Yayım 13.07.2026. Sübvansiyonsuz: kamu ölçekli güneş 40–98, güneş + depolama 61–156, kara rüzgârı 37–99, deniz üstü 105–167, ticari/topluluk çatı GES 88–197, jeotermal 67–111, doğal gaz kombine çevrim 51–129, kömür 72–177, yeni nükleer (Vogtle) 175–255 $/MWh. SMR örneği 214 $/MWh (Clinch River, Darlington, Natrium; "örnek niteliğinde", 2030 sonrası işletme). WACC ≈ %7,7 | `lazard.com/media/kcfconhf/lazards-lcoeplus_vf.pdf` (metin pdftotext ile okundu; PDF projeye konmadı) | [D] |
| Darlington (OPG, BWRX-300) | 4 × 300 MWe; toplam 20,9 milyar CAD (2024 doları, faiz ve beklenmedik gider dahil); ilk ünite ortak altyapıyla 7,7 milyar CAD; ilk ünite 2030'da hizmete; inşaat lisansı Nisan 2025, yatırım kararı Mayıs 2025 | World Nuclear News; Wikipedia (BWRX-300); Neutronbytes / Globe and Mail | [İ] |
| NuScale – UAMPS | 6 × 77 MWe = 462 MWe; hedef fiyat 58'den 89 $/MWh'e (Ocak 2023, sübvansiyon sonrası); abone %80'e ulaşmadı; Kasım 2023'te iptal; 49,8 milyon $ fesih bedeli | E&E News; Power Engineering; Canary Media | [İ] |
| NuScale toplam maliyet | 9,3 milyar $ (önceki 5,3) | IEEFA (Ocak 2023), bu oturumda yeniden bulunamadı | [İ/DY] |
| IEA, nükleer raporu (Ocak 2025) | SMR'nin yaygınlaşması için 2040'a kadar ≈ 60–80 $/MWh'e inmesi gerekir; IEA tahmini satıcı beyanlarından yüksek | World Nuclear News, IEA basın bülteni | [İ] |
| Akkuyu | 4 × VVER-1200 (4,8 GW). Bakan: 1. ünitede ilk elektrik 2026 sonu (Haziran 2026). Temsili yakıt yüklemesi yapıldı. 27.10.2026 itibarıyla gerçek yakıt yüklemesi doğrulanamadı. Önceki 2024 ve 2025 hedefleri kaçtı | TRT Haber, memurlar.net, NTV, Donanımhaber | [İ] / [DY] |
| Nükleer hedefi | 2050'ye kadar en az 20 GW: 12 büyük reaktör (Akkuyu 4, Sinop, Trakya) + 5 GW SMR (Kasım 2025). İlk SMR 2030'ların ilk yarısında. USTDA ile 4 ABD SMR tasarımının fizibilite hibesi (Eylül 2026); Nuclean – i-SMRDA (Kore) işbirliği (Haziran 2026) | WNA World Nuclear Outlook (Türkiye), CNBC-e, Daily Sabah, Forbes TR | [İ] |
| Nükleer Düzenleme Kanunu | 7381 sayılı, RG 08.03.2022 / 31772; aynı gün 95 sayılı CBK ile NDK'nın teşkilatı | mevzuat derleyicileri (Alomaliye, Erdem & Erdem) | [İ] |
| YEKA 2025 | GES-2025: tavan 5,50, taban 3,25 €¢/kWh, 8 yarışma, 77 başvuru. RES-2025 (09.12.2025): 1.150 MW, kazananlar 3,50 €¢/kWh + MW başına 212–312 bin € katkı payı | QNB Yatırım, Bloomberg HT, Forbes TR, Borsagündem | [İ] |
| Lisanssız üretim mevzuatı | Yönetmelik RG 12.05.2019 / 30772. 2022 değişikliği: satışa konu üretim, ilişkili tüketim tesisinin tüketimini aşamaz. 01.10.2022 / 31970: aynı kişinin farklı dağıtım bölgesindeki tüketimiyle ilişkilendirme. 25.11.2025 / 33088: devir, öncelik ve bağlantı süreleri. EPDK 30.04.2026: mahsuplaşma usul ve esasları. CB Kararı 11415 (RG 13.06.2026 / 33279): YEKDEM'de 10 yılı dolan tesisler | Erdem & Erdem bilgi bankası; Milliyet | [İ] (metinlerin tamamı okunmadı) |
| Nüfus 2050 | 93.774.618 (TÜİK Nüfus Projeksiyonları 2023–2100, ana senaryo) | basın aktarımı | [İ] |

## 4. Önceki oturumda okunan, bu oturumda yeniden açılmayan kaynaklar

Aşağıdakiler `GOSTERGELER` ve `MALIYET` listelerinde [D] olarak duruyor. Değerler önceki oturumda kaynağında okundu; bu oturumda yalnız tutarlılıkları sınandı (TEİAŞ toplamları, ETKB denge toplamları, PTF kuru).

- EPDK Elektrik Piyasası Gelişim Raporu 2025 (mesken 78.197 GWh, PTF 2.651,81 TL/MWh, dağıtım kaybı bölge tablosu), EPDK Doğal Gaz Piyasası Gelişim Raporu 2025 (59,07 milyar Sm³; konut fiyatı 13,19 TL/Sm³), EPDK Petrol ve LPG Piyasası raporları 2025.
- EPDK mesken tarifesi (4.4.2026; düşük kademe 291,90 kr/kWh, yüksek kademe 432,07 kr/kWh). Vergi oranları (%5 ETV, %20 KDV) belgeden doğrulanmadı [DY].
- IRENA Renewable Power Generation Costs 2025 (küresel ağırlıklı LCOE; Türkiye güneş 86, rüzgâr 61, jeotermal 33 $/MWh; kurulum maliyetleri).
- ETKB Türkiye Ulusal Enerji Planı (2022): 2035 için 189,7 GW kurulu güç, 52,9 GW güneş, 29,6 GW rüzgâr, 7,2 GW nükleer, 7,5 GW batarya, 510,5 TWh tüketim.
- HEAL/CREA (2021) "Chronic Coal Pollution – Türkiye": 2019'da kömür santrallerine bağlı 4.818 erken ölüm. Temiz Hava Hakkı Platformu Kara Rapor 2025: 2024'te PM2.5'e bağlı 62.644 erken ölüm. OWID (Ritchie 2020; Markandya ve Wilkinson 2007) TWh başına ölüm.
- ÇŞİDB IIR 2024 (birincil PM2.5'te konut yanmasının payı %54,0).
- İzmir Jeotermal 2025–26 tarifesi; Fraunhofer ISE 2024 çatı GES maliyeti; DOE Pathways to Commercial Liftoff: Advanced Nuclear (2023): n'inci örnek ≈ 3.600 $/kW, iyi yürütülmüş ilk örnek ≈ 6.200 $/kW [İ].
- TÜİK Motorlu Kara Taşıtları (Ocak–Eylül 2026 elektrikli otomobil payı %18,6), SBB 2027 Yıllık Programı (şarj noktası 45.871).

## 5. Bulunamayanlar ve boşluklar

- **Enerji ithalat faturası 2025 (fasıl 27):** TÜİK dış ticaret tablosuna bu oturumda erişilmedi [DY]. Raporda yalnız fiziksel bağımlılık (ETKB denge) kullanıldı.
- **Türkiye'de çatı GES anahtar teslim fiyatı:** Resmî ya da derlenmiş bir seri bulunamadı. Model 900 $/kWp varsaydı (Almanya > 30 kWp aralığının alt ucu) [V].
- **Lisanssız yönetmeliğin 2025 değişikliğindeki ihtiyaç fazlası hükümleri:** Metnin tamamı okunmadı [DY].
- **Jeotermal akışkanının CO2'si:** Türkiye'deki sahalara göre çok değişken; ısıtma seçeneklerinde sıfır alındı ve grafikte not düşüldü [DY].
- **Saatlik ulusal yük verisi (EPİAŞ şeffaflık):** Bu çalışmada kullanılmadı. Ulusal yük biçimi TEİAŞ aylık üretimine ve sıcaklığa kalibre edildi (`enerji_kalibrasyon.csv`) [V/H].
