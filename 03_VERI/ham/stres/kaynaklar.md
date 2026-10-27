# Kentsel stres: veri kaynakları (il ve ulusal düzey)

Erişim tarihi: 27.10.2026. İşaretler: **[D]** birincil TÜİK tablosu (eski TÜİK sitesinin Wayback Machine'deki arşiv kopyası), **[H]** bizim hesapladığımız değer, **[İ]** ikincil kaynak.

## Yöntem

- Web arama kotası çalışmanın başında dolduğu için hiç arama yapılamadı. Yalnız bilinen adresler doğrudan açıldı (curl ve Python).
- Eski TÜİK sitesinin konu sayfaları Wayback'ten açıldı. Bunlar `tuik.gov.tr/PreTablo.do?alt_id=1060` (Hayati İstatistikler), `alt_id=1106` (İLYE), `alt_id=1068` (Toplumsal Yapı ve Cinsiyet) ve `alt_id=1009` (Zaman Kullanımı). Tablo kimlikleri (`istab_id`) bu sayfalardan alındı. Her tablonun arşivlenmiş .xls dosyası `web.archive.org/web/<zaman>id_/http://www.tuik.gov.tr/PreIstatistikTablo.do?istab_id=<no>` adresinden indirildi. Tam adres her satırın `kaynak_url` sütununda.
- Ham .xls dosyaları `tuik_arsiv_xls/` klasöründe. Betikler `_betikler/` klasöründe; geçici klasörden çalıştırıldıkları için içlerindeki yolların düzeltilmesi gerekir.
- İl adları ve İBBS-3 kodları `03_VERI/ham/tuik/il_paneli_ham_2025.csv` dosyasından alındı.
- Nüfus TÜİK SDMX'teki `DF_ADNKS_T30` akışından alındı: 2007 sonrası ADNKS, 2000–2006 nüfus tahmini.
- veriportali.tuik.gov.tr'ye ve SDMX'teki intihar ve ölüm akışlarına erişilmedi.

## Dosyalar

| Dosya | İçerik | Kapsam | İşaret |
|---|---|---|---|
| `il_intihar_2000_2016.csv` | İl × yıl intihar sayısı (toplam, erkek, kadın) ve TÜİK kaba intihar hızı (yüz binde). Sayılar istab_id=109, hızlar istab_id=110 tablosundan; ikisinin de arşiv tarihi 02.10.2017. | 81 il, 2000–2016 (2000 için hız yok). **Olay yerine** göre. | [D] |
| `il_intihar_2017.csv`, `il_intihar_2018.csv` | **İkamet iline** göre intihar sayısı (toplam, erkek, kadın), istab_id=2754 (arşiv tarihleri 26.06.2018 ve 20.12.2019). `kaba_intihar_hizi_hesap` = sayı / yıl ortası nüfus × 100.000. | 81 il | sayı [D], hız [H] |
| `il_intihar_2000_2018_birlesik.csv` | Yukarıdaki iki dosyanın uzun birleşimi. `kapsam` ve `hiz_isaret` sütunlarıyla. | 81 il × 19 yıl | [D]/[H] |
| `il_intihar_2019_kismi.csv` | 2019 için yalnız 5 il (İstanbul 419, Ankara 228, İzmir 193, Bursa 114, Antalya 105). Kaynak Vikipedi "Türkiye'de intihar" maddesi; madde TÜİK 2019 bültenine atıf yapıyor. | 5 il | [İ] |
| `il_ilye_2015_gostergeler.csv` | İllerde Yaşam Endeksi 2015, 41 göstergenin tamamı (istab_id=2421). | 81 il | [D] |
| `il_ilye_2015_stres_secilmis.csv` | Seçilmiş İLYE göstergeleri: mutluluk düzeyi, gece yalnız yürürken güvende hissetme, sokak gürültüsü, fert başına oda, konut kalitesi problemi, PM10, sosyal hayat memnuniyeti, toplu taşıma memnuniyeti. `kisi_sayisi_oda_basi_hesap` = 1 / oda sayısı. | 81 il | [D], ters oran [H] |
| `il_ilye_2015_endeks.csv` | İLYE genel ve 11 alt boyutun sırası ve endeks değeri (istab_id=2420). | 81 il | [D] |
| `il_mutluluk_2013.csv` | Yaşam Memnuniyeti Araştırması 2013 il sonuçları. Mutlu, orta ve mutsuz oranları, cinsiyete göre (istab_id=2235). | 81 il | [D] |
| `il_mutluluk_kaynagi_2013.csv` | İllere göre mutluluk kaynağı (kişiler ve değerler), YMA 2013 (istab_id=2238). | 81 il | [D] |
| `il_kamu_hizmet_memnuniyeti_2013.csv` | İllere göre kamu hizmetlerinden memnuniyet, YMA 2013 (istab_id=2240). Seçilen sütunlar: SGK, sağlık, eğitim, adli, asayiş, ulaştırma. | 81 il | [D] |
| `tr_yasam_memnuniyeti_ulusal_2003_2019.csv` | Ulusal YMA serileri: genel mutluluk 2003–2019 (istab_id=925), gece yalnız yürürken güvende hissetme 2003–2017 (istab_id=938), mutluluk kaynağı 2004–2019 (istab_id=1597). Toplam, erkek, kadın. | Türkiye | [D] |
| `tr_trafik_isegidis.csv` | TomTom Trafik Endeksi 2025: 11 il, şehir merkezi ve metropol alanı. Ayrıca TÜİK Zaman Kullanım Araştırması 2006 ve 2014–15'ten "ulaşım ve belirlenmemiş zaman" (dk/gün; istab_id=2402). | Şehir ve Türkiye | [İ] / [D] |

## Doğrulama

- **İntihar 2000–2016:** 81 il eksiksiz. Her yıl il toplamı tablodaki Türkiye toplamına eşit (fark 0). Her ilde erkek + kadın = toplam.
- **Kaba hız tutarlılığı:** Hız, sayı / ((nüfus₍t−1₎ + nüfus₍t₎)/2) × 100.000 ile yeniden hesaplandı. 2001–2016 için TÜİK hızlarıyla tüm il ve yıllarda birebir aynı çıktı (maksimum fark 0,0000). Yıl sonu nüfusuyla hesaplanınca maksimum fark 0,68 oluyor. Bu nedenle 2017–2018 hızları yıl ortası yöntemiyle hesaplandı [H].
- **İntihar 2017–2018:** 81 il eksiksiz. İl toplamları tablodaki Türkiye toplamlarına eşit (2017: 3.069, 2018: 3.161). Erkek + kadın = toplam.
- **Revizyon uyarısı:** İl tabloları TÜİK'in sonraki revizyonundan önceki değerleri içeriyor. 2020 tarihli istab_id=1594 tablosundaki revize Türkiye toplamları: 2016 3.193, 2017 3.168, 2018 3.342, 2019 3.406 (yüz binde 4,12). İl tablolarındaki toplamlar ise 3.064, 3.069 ve 3.161. Revize il dağılımı bulunamadı.
- **Seri kırılmaları:** 2016'ya kadar olay yeri, 2017–2018 ikamet ili esas alınıyor. TÜİK dipnotuna göre 2012'de kapsam genişledi: kurumsal yerlerdeki intiharlar ve ölüm nedeni verisi eklendi. 2011/2012 arasında düzey sıçraması var.
- **Küçük sayılar:** Birçok ilde yılda 10'dan az intihar var, bu yüzden hızlar oynak. Çok yıllı ortalama önerilir. 2016'da en yüksek hızlar Tunceli 10,7, Ardahan 9,1 ve Burdur 8,5.
- **İLYE:** 81 il ve 41 gösterge eksiksiz, boş hücre yok. 12 sıralamanın her biri 1–81 tam. Bülten metniyle de karşılaştırıldı (Sayı 24561, 22.01.2016): Isparta 0,6745, Sakarya 0,6737, Bolu 0,6553 ilk üç; Muş 0,2765, Mardin 0,2936, Ağrı 0,2975 son üç. Değerler dosyayla aynı. Göstergelerin referans yılları ayrıca doğrulanmadı.
- **Mutluluk:** YMA 2013 il "mutlu" oranı, İLYE'deki "mutluluk düzeyi" ile 81 ilde birebir aynı (fark 0). Yani İLYE'nin mutluluk göstergesi YMA 2013 verisi. İl satırlarında mutlu + orta + mutsuz = 100 ± 0,01. Türkiye 2013 değeri 59,02 ve ulusal tablodaki çok mutlu + mutlu (9,57 + 49,45) ile tutuyor. En yüksek iller Sinop 77,66, Afyonkarahisar 76,43 ve Bayburt 75,91; en düşük iller Tunceli 41,98, Osmaniye 45,77 ve Diyarbakır 48,67.
- **TomTom:** Ortalama hız (v) ile şehir sayfasındaki "10 km süre" tutarlı. Örneğin İstanbul 26,2 km/sa → 22,9 dk; sayfada 22 dk 54 sn. Zirve saatte kaybedilen süre sayfa metninde üç şehir için de 112 saat, sayfa verisinde (`tLostRush`) üçü için de 88. Bu alan şüpheli, kullanılmamalı.

## Ulusal sayılar (özet)

- Mutlu (çok mutlu + mutlu): 2019 %52,35 (6,61 + 45,74) [D] istab_id=925. 2020–2025 değerleri bulunamadı.
- Gece yalnız yürürken güvende (çok güvenli + güvenli): 2017 %57,08 (5,67 + 51,41) [D] istab_id=938.
- Mutluluk kaynağı 2019: kişi olarak tüm aile %74,1; değer olarak sağlık %69,9 [D] istab_id=1597.
- İntihar 2019: 3.406 kişi, yüz binde 4,12 [D] istab_id=1594.
- ZKA 2014–15: çalışanların "ulaşım ve belirlenmemiş zaman" süresi günde 82 dk (erkek 90, kadın 65); 15 yaş üstü ortalama 64 dk [D]. Bu yalnız işe gidiş değil, tüm ulaşım süresi.
- TomTom 2025 sıkışıklık (şehir merkezi): İstanbul %62,0, Ankara %55,8, İzmir %54,1. 10 km süre: İstanbul 22 dk 54 sn, Ankara 21 dk 3 sn, İzmir 22 dk 59 sn [İ].

## Bulunamayanlar

- İl düzeyi intihar 2019–2024. Yeni portal döneminin tabloları arşivde yok; istab_id=2831 ve 2832'nin hiç arşiv kopyası yok, 2019 bülten tabloları 404 veriyor. 2019 için yalnız 5 il var [İ].
- YMA 2020–2025 ulusal sonuçları. veriportali engelli ve arama yapılamadı.
- İl veya büyükşehir düzeyinde ortalama işe gidiş süresi (Moovit, ulaşım ana planları). Arama yapılamadığı için bakılamadı.
- 2017 sonrası "gece yalnız yürürken güvende" serisi. istab_id=2818 arşivlenmemiş.

---

## Güncelleme (27.10.2026, ikinci oturum)

Dosyanın adı `kaynaklar_ikincil.md` iken `kaynaklar.md` yapıldı (README'deki `03_VERI/ham/*/kaynaklar.md` düzeni).

### Eklenen ham veriler

| Klasör | İçerik | Kod | İşaret |
|---|---|---|---|
| `eurostat/` | EU-SILC JSON-stat yanıtları: `ilc_lvho05a` (aşırı kalabalık), `ilc_lvho07a` (konut maliyet yükü), `ilc_mddw01–03` (gürültü, kirlilik, suç), `ilc_mdho04` (karanlık konut), `ilc_pw01` (yaşam memnuniyeti), `ilc_pw03` (güven). Türkiye ve AB-27 | `05_ANALIZ/kod/stres_veri.py` | [D] |
| `sdmx/` | TÜİK SDMX: `DF_TRAFIK_KAZA_OLU_YARALI_V2` (il, 2015–2025; 2025'te iki il eksik olduğu için 2024 kullanıldı), `DF_MOTORLU_KARA_TASIT_ILLER_V3` (aylık, son dönem 2026-09) | `stres_veri.py` | [D] |
| `literatur/crossref/`, `pubmed/`, `europepmc/` | 76 kaynağın Crossref künyesi ve özeti (PubMed, yoksa Crossref ya da Europe PMC) | `05_ANALIZ/kod/stres_literatur_dogrula.py` | [D] |
| `literatur/pmc/PMC4928945.xml` | Falchi ve ark. 2016 tam metni. Tablo 2 Türkiye satırı: nüfusun %97,8'i ışık kirli gökyüzü altında (>14 µcd/m²), %49,9'u Samanyolu'nu göremiyor (>688), %24,3'ü >3.000 µcd/m² altında | aynı | [D] |

### Düzeltmeler ve notlar

- **YMA 2020–2025 bulundu.** Yukarıda "bulunamadı" denen ulusal değerler projenin ana gösterge tablosunda var (`03_VERI/islenmis/turkiye_temel_gostergeler.csv`, TÜİK basın bülteni 54199): 2025'te kendini mutlu beyan edenler %53,3, mutsuz %13,0 [D]. `stres_turkiye_yayginlik.csv` artık bu değerleri kullanıyor. İl kırılımı 2013'ten sonra yok.
- **İntihar 2025:** yüz binde 5,35, ikincil haber kaynağından [İ]. Revize il dağılımı hâlâ yok.
- **DSÖ 2018 gürültü kılavuzu değerleri** (karayolu Lden 53 / Lnight 45 dB, demiryolu 54 / 44, uçak 45 / 40) birincil belgeden okunamadı (WHO IRIS 403). Değerler web aramasındaki ikincil özetlerden alındı [İ].
- **Türkiye gürültü maruziyeti:** Bakanlığın stratejik gürültü haritaları (TÜBİTAK MAM, 17 il, 2017) var. 55 dB üstüne maruz nüfusu veren açık bir ulusal tablo bulunamadı [DY].
- **Yeniden üretim sınırı:** `_betikler/` içindeki işleme betikleri ilk oturumun geçici klasöründeki ara dosyalara (`../stres_veri/...`) başvuruyor. Türetilmiş CSV'ler ve ham .xls dosyaları burada; betikler olduğu gibi çalışmaz, ancak işlemenin kaydı olarak duruyor.
- Web araması bu oturumda iki kez çalıştı (DSÖ gürültü değerleri, Türkiye gürültü haritaları); literatür doğrulaması aramaya değil Crossref ve PubMed'e dayanıyor.
