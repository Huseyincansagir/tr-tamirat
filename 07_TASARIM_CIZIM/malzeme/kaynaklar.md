# Kaynaklar ve doğrulama notu: doğal ve geri dönüştürülmüş yapı malzemeleri

*27 Ekim 2026 · Sürüm 1.0 · Faz 4 · Rapor 3'ün eki ([09_RAPORLAR/16_dogal_ve_geri_donusturulmus_malzemeler.md](../../09_RAPORLAR/16_dogal_ve_geri_donusturulmus_malzemeler.md))*

## İşaretler

| İşaret | Anlamı |
|---|---|
| **[D]** | Doğrulandı. Birincil metin (Resmî Gazete, yönetmelik eki, resmî kurum sayfası) bu çalışmada okundu |
| **[İ]** | İkincil. Değer bir derlemeden, basından, makale özetinden ya da arama motoru özetinden alındı. Birincil kaynak açılamadı |
| **[DY]** | Doğrulanmadı. Alan bilgisine ya da hatırlanan değere dayanıyor; kullanmadan önce teyit edilmeli |
| **[V]** | Bu çalışmanın varsayımı |
| **[H]** | Bu çalışmada hesaplandı (`kod/malzeme_modeli.py`) |

## Erişim sınırları (27.10.2026)

- **Web araması.** İlk oturumda arama kotası araştırmanın ortasında doldu. ICE tablolarının çoğu, Peru E.080, sarsma masası deneyleri ve 2023 kerpiç gözlemleri bu yüzden doğrulanamadı. 27.10.2026 öğleden sonraki tamamlama oturumunda arama yeniden çalıştı; üç arama yapıldı (hastane sismik izolasyonu, Türkiye'de CLT üretimi, 2023 kerpiç hasarı). Üçüncüsü sonuç vermedi.
- **Sıkıştırılmış PDF'ler.** ÇŞİDB birim fiyat ve rayiç PDF'leri (6–10 MB) ve ODTÜ'nün 2023 deprem raporu araçla okunamadı. Bu PDF'lerden gelen sayılar arama motoru özetinden alındı ve **[İ]** işaretlendi.
- **TBDY 2018 ve DBYBHY 2007.** Resmî Gazete ek PDF'lerinin metni yerelde, salt okunur biçimde çıkarıldı. Bu iki kaynaktan gelen maddeler **[D]**. TBDY 2018 eki 27.10.2026'da yeniden indirildi (WebFetch, 7 MB) ve `pdftotext` ile okundu; aşağıdaki maddeler bu okumayla yeniden doğrulandı. PDF ve metin depoya konmadı.
- **Yerleşik tarayıcı.** Kullanılmadı.

## 1. Mevzuat ve standartlar

| Kaynak | Ne alındı | İşaret |
|---|---|---|
| Türkiye Bina Deprem Yönetmeliği, RG 18.03.2018, sayı 30364 (Mükerrer), yürürlük 01.01.2019. Ek: https://www.resmigazete.gov.tr/eskiler/2018/03/20180318M1-2-1.pdf | Tablo 3.1 (BKS 1/2/3, I = 1,5/1,2/1,0); Tablo 3.2 (DTS); Tablo 3.3 (BYS yükseklikleri); Tablo 4.1 (E22 donatısız yığma R 2,5, D 1,5, BYS 8; E21 kuşatılmış R 3; E11 donatılı yığma R 4, D 2; F1 ahşap levha kaplamalı R 4, D 2; F2 ahşap çaprazlı R 3, D 2); md. 1.1.2 (kapsam), 1.1.8 (tescilli yapı), 1.1.9 (kapsam dışı yapı için TS ve uluslararası eşdeğer standart); md. 4.3.4.1(a) (sınırlı süneklikli sistemler DTS 1a–4a'da, yani BKS 1'de kullanılamaz); md. 11.1.3, 11.2.2, **11.2.4 (kerpiç, moloz taş, ponza ve boşluklu briket taşıyıcı duvar malzemesi olarak kullanılamaz)**; Tablo 11.4 (asgari duvar kalınlıkları); birim ≥5 MPa, harç ≥5 / ≥10 MPa; hatıl ≥300 mm, 6φ12; döşeme ≥100 mm; Bölüm 12 (ahşap) | D |
| Aynı yönetmelik, 27.10.2026 yeniden okuma | Tablo 4.1: A11 betonarme çerçeve R 8, D 3, BYS ≥ 3; E11 donatılı yığma R 4, D 2, **BYS ≥ 7**; E21 kuşatılmış R 3, D 2, BYS = 8; E22 donatısız R 2,5, D 1,5, BYS = 8; F1 kaplamalı panel ahşap R 4, D 2, BYS ≥ 7; F2 çaprazlı ahşap R 3, D 2, BYS = 8. Tablo 3.3: BYS 8 H ≤ 7 m (DTS 1–2), ≤ 10,5 m (DTS 3–4); BYS 7 7–10,5 / 10,5–17,5 m. md. 4.7.3.4 Denk. 4.27: T = Ct·H^0,75, Ct 0,1 (betonarme çerçeve), 0,08 (çelik), 0,07 (diğer). md. 11.1.2: donatısız ve kuşatılmış yığma "süneklik düzeyi sınırlı", donatılı yığma "yüksek". md. 11.2.4 tam metni (boşluklu briket, dolgu tuğlası, kerpiç, moloz taş, ponza "ve benzeri biçim verilmiş bloklar"). md. 11.3.7: döşeme ≥100 mm, yatay hatıl ≥300 mm, 6φ12, ≤4 m. Şekil 11.3: mesnetlenmemiş duvar <5,5 m (DTS 1–2), <7,5 m (DTS 3–4). md. 11.5.7–11.5.8: donatılı yığmada yatay donatı ≥%0,05, düşey ≥%0,08, aralık ≤600 mm. Tablo 11.4: donatısız kesme taşta etkin kalınlık ≥350 mm. **md. 12.1.2: ahşap binaların yatay yük taşıyıcı sistemi yalnız kaplamalı ya da ahşap çaprazlı panellerden oluşabilir (CLT ve glulam çerçeve kapsam dışı).** Tablo 3.1: BKS 1 başlığında "değerli eşyanın saklandığı binalar"; kütüphane adı geçmiyor | D |
| Deprem Bölgelerinde Yapılacak Binalar Hakkında Yönetmelik 2007, RG 06.03.2007. https://www.resmigazete.gov.tr/eskiler/2007/03/20070306-3-1.pdf | Kerpiç: her bölgede en çok 1 kat, kat yüksekliği ≤2,70 m, desteksiz duvar ≤4,5 m, 1. ve 2. bölgede toprak dam yasak; yığma Tablo 5.1 (1. bölgede 2 kat) | D |
| 2026 Yılında Uygulanacak Yapı Yaklaşık Birim Maliyetleri Hakkında Tebliğ, RG 03.02.2026, sayı 33157. https://www.resmigazete.gov.tr/eskiler/2026/02/20260203-4.htm | I.A 2.600 … V.E 103.500 TL/m²; III.A 19.800; III.B 21.050; III.C 23.400; IV.A 26.450; IV.B 33.900; IV.C 40.500; V.B 43.850; V.C 48.750 TL/m². Sınıflar: ilkokul ve ortaokul III.B, lise III.C, ibadethane <500 kişi III.B / 500–1.500 IV.B / ≥1.500 V.B, kütüphane <1.000 m² III.B / ≥1.000 m² IV.C, ilçe tipi kamu binası IV.A, büyükşehir belediye hizmet binası IV.C, hastane <200 yatak IV.C / 200–400 V.B / ≥400 V.C, ASM III.B, müstakil konut <200 m² III.B. BM'ye %15 genel gider ve %10 kâr dahil, KDV hariç | D |
| TS 825:2024 Binalarda ısı yalıtım kuralları. TSE Teknik Kurul onayı 21.10.2024; zorunlu 01.04.2025. Aktaran: T. Diz ve B. Tanyol (İZODER), Yapı İnşaat Dergisi, 27.03.2025. https://www.yapiinsaatdergisi.com/ts-8252024-binalarda-isi-yalitimi-kurallari-standardi-ile-ilgili-yenilikler/ | Dış duvar U sınırı: 1. bölge 0,45; 2. ve 3. bölge 0,40; 4. bölge 0,35; 5. ve 6. bölge 0,25 W/m²K. Kaynak tablo kısmen bozuk | İ |
| İZODER il dosyası (Kayseri): https://www.izoder.org.tr/ts825/kayseri.pdf | Kayseri merkez 4. bölge; Pınarbaşı, Sarız, Tomarza 5. bölge | İ |
| Gül (2026), DÜMF Mühendislik Dergisi: https://dergipark.org.tr/en/pub/dumf/article/2009017 | TS 825:2024 bölgeleri il bazında 1992–2021 istasyon verisiyle atanmış; derece-gün eşikleri yayımlanmamış | İ |
| Yeşil Çimento Kullanımının Teşvikine İlişkin Tebliğ, RG 16.03.2024, sayı 32791, yürürlük 01.01.2025 (aktaran: aksan.av.tr; ecobuild.com.tr) | Kamu ihalesinde klinker/çimento oranı 2025–2029 ≤0,80, 2030'dan sonra ≤0,75 | İ |
| Hafriyat Toprağı, İnşaat ve Yıkıntı Atıklarının Kontrolü Yönetmeliği, RG 18.03.2004, sayı 25406 (mevzuat.gov.tr, MevzuatNo 5401) | Yürürlükteki çerçeve | İ |
| Hafriyat Toprağı ile İnşaat ve Yıkıntı Atıklarının Yönetimi Yönetmeliği Taslağı, ÇŞİDB, Mart 2026. https://webdosya.csb.gov.tr/v2/cygm/2026/03/HTIYAYYonTslk20260313-20260317140904.docx | Döngüsel ekonomi ve atık hiyerarşisi; RG'de yayımı doğrulanmadı; dosya okunamadı | İ |
| TS 706 EN 12620+A1 Beton agregaları | Geri dönüştürülmüş agregayı kapsar | İ |
| TS EN 206 Ek E (bilgilendirici) | İri geri dönüştürülmüş agrega X0'da ≈%50, XC/XD1/XF1/XA1'de ≈%30; ince geri dönüştürülmüş agrega yok | DY |
| TS 2514 ve TS 2515 (kerpiç blok ve kerpiç yapı kuralları, 1977) | Durumları (yürürlükte mi, iptal mi) doğrulanmadı | DY |
| NZS 4297:2020, NZS 4298:2020, NZS 4299:2020. Aktaran: Walker ve Morris, SESOC 2021 konferansı (standart yazarları). https://2021conf.sesoc.org.nz/PDFs/S4B%20P3%20-%20Walker_Morris.pdf ve BRANZ Bulletin 667 (Aralık 2021) https://www.branz.co.nz/documents/4080/Bulletin667_EARTH_BUILDINGS_1.pdf | NZS 4297: donatılı duvar ≤6,5 m, donatısız yalnız kısıtlı ve ≤3,3 m; asgari duvar 250 mm; standart sınıf tasarım basınç dayanımı 0,5 MPa. NZS 4299: tek kat, hafif çatı, ≤600 m², önem düzeyi 1–2, deprem bölgesi 1–3; bütün duvarlar düşey ve yatay donatılı | İ |
| Peru E.080 (2017), DS 003-2017-VIVIENDA. https://sni.org.pe/ | Adı "donatılı toprakla tasarım ve yapım" oldu. Kat sınırları doğrulanmadı | İ / DY |
| DIN 18945–18948 (toprak blok, harç, sıva, levha) ve DIN 18940 (taşıyıcı toprak blok kâgir) | Örnek standart paketi olarak anıldı; içerik okunmadı | DY |
| Euratom 2013/59 (radon başvuru düzeyi 300 Bq/m³) | | DY |
| Sağlık Bakanlığı genelgesi (2012 ya da 2013; numara ve künye bulunamadı). Aktaran: MEF Üniversitesi tez kaydı https://gcris.mef.edu.tr/entities/publication/9653fae7-b520-4e16-8656-c21929b8d3b0 ve basın | 1. ve 2. derece deprem bölgelerinde 100 ve üzeri yataklı (devlet) hastanelerde sismik izolasyon zorunlu. Kaynaklar yılda ayrışıyor | İ |

## 2. Fiyat ve ekonomi

| Kaynak | Ne alındı | İşaret |
|---|---|---|
| ÇŞİDB 2026 Şubat rayiçleri. https://webdosya.csb.gov.tr/v2/yfk/2026/02/2026-ubat-rayi-ler-20260204120913.pdf | Düz işçi 205 TL/sa (10.100.1062); duvarcı, betoncu, demirci, kalıpçı ustası 310 TL/sa; usta yardımcısı 230 TL/sa | İ (arama özeti; PDF açılamadı) |
| ÇŞİDB 2026 Şubat birim fiyatları. https://webdosya.csb.gov.tr/v2/yfk/2026/02/2026-ubat-birim-fiyatlar-20260204120934.pdf | C25/30 hazır beton 3.524 TL/m³ (15.150.1005); nervürlü çelik Ø8–12 46.482 TL/t (15.160.1003), Ø14–28 44.681 TL/t (15.160.1004) | İ |
| ÇŞİDB 2026 Eylül birim fiyatları. https://webdosya.csb.gov.tr/v2/yfk/2026/09/2026-Eyl-l-n-aat-b-f-20260903141226.pdf | 13,5 cm yatay delikli tuğla duvar ≈923,65 TL/m²; EPS mantolama ≈1.251,20 TL/m²; Ø14–28 çelik 52.158 TL/t | İ (özet bozuk) |
| herpoz.com | Hazır beton Temmuz 2026 ≈3.986 TL/m³ | İ |
| vitalbeton.com, 20.02.2026 | İnşaat demiri piyasa fiyatı 28.600–29.900 TL/t, KDV dahil | İ |
| birimfiyat.com (DSİ birim fiyatı) | Çimento Ocak 2025 3.121,88 TL/t | İ |
| ekonomigazetesi.com; alomaliye.com (09.10.2026); gazeteoksijen.com (05.10.2026) | İnşaat maliyet endeksi Aralık 2025 yıllık %24,50 (malzeme %21,47, işçilik %30,67), Ağustos 2026 %29,59; TÜFE Aralık 2025 %30,89, Eylül 2026 %29,73 | İ |
| Ağırlık türetmesi | İnşaat maliyet endeksinde malzeme ≈%64–67, işçilik ≈%33–36 (yayımlanan değişimlerden geri hesap) | H |
| CLT, glulam, saman balyası, kerpiç blok, Avrupa sıkıştırılmış toprak duvar fiyatları | CLT fabrika çıkışı €450–700/m³, kurulmuş €900–1.300/m³; balya 100–250 TL; kerpiç blok 10–30 TL; Avrupa'da sıkıştırılmış toprak duvar €250–600/m² | DY |
| Türkiye'de CLT: Kastamonu ve Yozgat için 2021 ön fizibilite raporları (yatirimadestek.gov.tr: https://www.yatirimadestek.gov.tr/pdf/assets/upload/fizibiliteler/kastamonu-ili-clt-capraz-lamine-tesisi-on-fizibilite-raporu2021.pdf ve …/yozgat-ili-clt-uretimi-on-fizibilite-raporu--2021.pdf); KTÜ'nün yerli sarıçam ve doğu ladininden CLT deneyi (avesis.ktu.edu.tr) | Üretim yapan yerli tesis bu aramada doğrulanamadı; CLT ithal kabul edildi | İ |

## 3. Gömülü karbon

| Kaynak | Ne alındı | İşaret |
|---|---|---|
| ICE (Inventory of Carbon and Energy), Circular Ecology. https://circularecology.com/embodied-carbon-footprint-database.html | Sürümler: v3.0 Kasım 2019; v4.0 Aralık 2024; v4.1 Ekim 2025 (GGBS ekonomik tahsis); v5.0 Haziran 2026, yalnız eğitim amaçlı. **30.09.2026'dan sonra eğitim dışı kullanım serbest değil**; ticari ardılı IC+. Bu çalışma akademik araştırmadır; değerler aralık ve kaynakla verildi, ticari kullanımda EPD'ye başvurulmalı | D |
| greencalculus.com (ICE v4.1 aktarımı). https://greencalculus.com/standards/ice-database-embodied-carbon/ | CEM I ≈0,91; CEM II/A ≈0,80; CEM III/A ≈0,50; 30 MPa beton ≈0,13; 40 MPa ≈0,16; çelik 1,00–1,55, birincil ≈2,46, %100 hurdadan ark ocağı ≈0,45; tuğla ≈0,23; EPS 3,29; taş yünü 1,28; cam yünü 1,35; kereste 0,31; alçı ≈0,13, alçı levha ≈0,39 | İ |
| MPA Factsheet 18 (2012) | CEM I 0,913; GGBS 0,067; uçucu kül 0,004 | İ |
| IStructE blog (mass timber factors) | ICE v3 glulam 0,512, CLT 0,437; Arup Avrupa EPD derlemesi glulam 0,28, CLT 0,25 | İ |
| ICE v3 değerleri (hatırlanan) | Dünya ortalaması inşaat demiri 1,99; tuğla 0,213; kereste 0,263; taş yünü 1,12 | DY |
| Fernandes vd. 2019. https://core.ac.uk/works/9877790 | Stabilizesiz sıkıştırılmış toprak 47,5 kgCO2e/m³ ≈0,024 kg/kg | İ |
| Journal of Green Building derlemesi. https://jgb.kglmeridian.com/downloadpdf/view/journals/jgrb/5/1/article-p101.pdf | %5–10 çimentolu sıkıştırılmış toprak için 0,04–0,05 "gerçekçi" | İ |
| Build up Nepal 2022. https://www.buildupnepal.com/wp-content/uploads/2022/08/carbon-evaluation-of-compressed-stabilised-earth-blocks-cseb-in-nepal-summary.pdf | CSEB 0,085–0,12 kgCO2e/kg, nakliye dahil | İ |
| OEKOBAUDAT, climatiq aktarımı. https://www.climatiq.io/data/emission-factor/2ea05a3d-0a53-43dc-824c-62d7cacd6268 | %100 doğal pomza blok 42,97 kgCO2e/m³ (2018 verisi, 2023 sürümü) | İ |
| Türk EPD'leri: Işıklar tuğla EPD-IES-0017324 (13.12.2024); STT Türk Gazbeton EPD-IES-0010629; Gaziantep Ytong (epd1804). https://www.environdec.com/library/ | Varlıkları doğrulandı; GWP değerleri okunamadı | D (yalnız varlık) |
| TÇÜD 2025 (steelradar aktarımı) | Türkiye ham çelik üretimi 38,1 Mt; ark ocağı payı %72,2 | İ |
| Türkçimento, S&P Global röportajı (Nisan 2026) | Gri klinker ≈0,88 tCO2/t; AB SKDM Türkiye varsayılanı 1,551 | İ |
| Frontiers in Built Environment 2025. https://www.frontiersin.org/articles/10.3389/fbuil.2025.1568067/full | Mısır'da 100 m² ev, beşikten mezara 60 yıl: CSEB 368, betonarme 698 kgCO2e/m² (makale içinde 350/652 de geçiyor; tutarsız) | D (makale) |
| LETI, RIBA 2030 konut ölçütleri | Avrupa konut A1–A5 ≈300–600 kgCO2e/m² | DY |
| IPCC 2006 | Doğalgaz 56,1 tCO2/TJ = 0,202 kgCO2/kWh | İ |

## 4. Yapı fiziği ve sağlık

| Kaynak | Ne alındı | İşaret |
|---|---|---|
| Lehmbau Regeln yoğunluk–λ tablosu (hatırlanan) | 2000 kg/m³ → 1,1; 1600 → 0,73; 600 → 0,17 W/mK | DY |
| de.wikipedia "Leichtlehm" | 400–1200 kg/m³ için λ 0,25–0,45 | İ |
| ETA-17/0247; Shea 2013 (de/en.wikipedia aktarımı) | Saman balya λD 0,048; tasarım 0,064; c ≈2000 J/kgK; Avusturya deneyi (2000) 5 cm kil-kireç sıvayla F90; Alman taşıyıcı saman duvar deneyi F30 | İ |
| en.wikipedia "Cross-laminated timber" | CLT λ ≈0,10; REI 90 örnekleri | İ |
| EN ISO 10456 değerleri (hatırlanan) | Kireçtaşı 1,1–1,7; yumuşak ağaç 0,13 | DY |
| NORDTEST nem tamponu sınıfları (Rode vd. 2005); McGregor vd. 2014 | MBV: <0,2 ihmal edilebilir … ≥2 mükemmel; kil sıva ≈1,0–2,5; alçı ≈0,6–1,0; çimento ≈0,3–0,5 | DY |
| WHO radon bilgi notu, 25.01.2023. https://www.who.int/news-room/fact-sheets/detail/radon-and-health | Başvuru düzeyi 100 Bq/m³ (olmazsa ≤300); her 100 Bq/m³ için akciğer kanseri riski ≈%16 artar | D |
| TAEK/TENMAK ulusal radon taraması (hatırlanan) | Türkiye ortalaması ≈81 Bq/m³ | DY |
| Stockholm Sözleşmesi, HBCD (Mayıs 2013) | EPS/XPS alev geciktiricisi yasaklandı | İ |
| AB 2023/1464 formaldehit tüzüğü | Ağustos 2026'dan sonra 0,062 mg/m³ | DY |
| IRC Appendix AS | Saman balya nemi yerleştirmede ≤%15, kullanımda ≤%20 | DY |
| DIN 4109 kütle kuralı (R'w = 28·log m' − 20) | Ses yalıtımı tahmini | DY |

## 5. Deprem kanıtı

| Kaynak | Ne alındı | İşaret |
|---|---|---|
| ODTÜ DMAM ön raporu, 2023. https://eerc.metu.edu.tr/en/announcements/metu-eerc-preliminary-report-pazarcik-kahramanmaras-mw-77-and-elbistan-kahramanmaras | Pazarcık Mw 7,7, Elbistan Mw 7,6 (AFAD) | D |
| en.wikipedia "2023 Turkey–Syria earthquakes" (resmî açıklamalar aktarımı) | Türkiye'de 53.537 can kaybı (İçişleri Bakanı, Şubat 2024); 518.009 konut yıkık ya da ağır hasarlı; 1,25 milyon incelenen binada ≈164.000 yıkık veya ağır hasarlı (23.02.2023); Hatay 13.517 yıkık; Malatya Yeni Cami kısmen göçtü | İ |
| en.wikipedia "Habib-i Neccar Mosque" | 2023'te yıkıldı; 1853'te de yıkılıp ≈1857'de yeniden yapılmıştı | İ |
| ODTÜ ve SBB'nin tam 2023 raporları | Kerpiç, moloz taş ve hımış hasarı için sayısal veri alınamadı (dosya boyutu); 27.10.2026 aramasında da kırsal kerpiç hasar oranı veren kaynak çıkmadı | DY |
| Harran (Şanlıurfa) konik kerpiç kubbeli evleri | Türkiye'deki geleneksel toprak kubbe örneği; kaynak okunmadı | DY |
| en.wikipedia "2003 Bam earthquake"; Encyclopaedia Iranica (Berberian) | 26.271 can kaybı (İran İstatistik Merkezi); konutların ≈%70'i tamamen yıkıldı; ≈25.000 bina | İ |
| en.wikipedia "Arg-e Bam" | Kale "neredeyse tamamen" yıkıldı; UNESCO tehlike listesi 2004–2013 | İ |
| en.wikipedia "2007 Peru earthquake" (BM SitRep 20) | 595 can kaybı; 58.581 konut yıkıldı | İ |
| PUCP geogrid donatılı kerpiç evlerin Pisco'daki performansı | Az ya da hiç hasar | DY |
| Walker ve Morris, SESOC 2021 (yukarıda) | Yeni Zelanda: Darfield 2010'da 14, Christchurch 2011'de 26, Kaikōura 2016'da 42 toprak ve saman yapı incelendi. 1990'lardan sonra donatılı yapılanlar iyi davrandı; 1998 standartlarıyla yapılanlarda göçme yok; donatısız preslenmiş blok kötü; düşük yoğunluklu kerpiç duvar deneyinde 2,2–3,1 g | D (makale) |
| en.wikipedia "Superadobe" | "M 7,2'ye dayandı" iddiası (BBC 2019) | İ (zayıf) |
| en.wikipedia "Nubian vault" | Sahel'de 2000'den beri 1.600'den fazla yapı | İ |
| en.wikipedia "Fatih Mosque, Istanbul" | 1509, 1557, 1754'te hasar; 22.05.1766'da yıkıldı | İ |

## 6. Deprem enkazı

| Kaynak | Ne alındı | İşaret |
|---|---|---|
| UNDP ilk tahmini, medyascope 25.02.2023 | 116–210 Mt enkaz (1999 Marmara ≈13 Mt) | İ |
| Hürriyet Daily News, 16.08.2024 | ≈200 Mt ≈100 milyon m³; 86 geçici depolama alanı (26 Hatay, 18 Kahramanmaraş) | İ |
| UNDP–ÇŞİDB–Japonya projesi | 4,83 milyon $; protokol 16.08.2023; Hatay ve Kahramanmaraş'ta iki tesis ve üç mobil kırıcı | İ |
| TRT Haber (Hatay Altınözü/Enek tesisi, açılış 04.02.2025) | 4.000 t/gün; üç boy agrega | İ |
| Milliyet, 01.08.2026 | Kahramanmaraş merkezde 750.000 m³ yıkıntı atığı geri kazanım tesisine | İ |
| ekonomim.com köşe yazısı | ≈1 Mt/yıl kapasiteyle "neredeyse iki yüzyıl" | İ |
| bianet, 2023 | Hatay Valiliği ölçümü sınır altında; bağımsız ölçümlerde örneklerin yaklaşık yarısında asbest | İ |
