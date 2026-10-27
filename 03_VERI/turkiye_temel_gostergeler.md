# Türkiye Temel Göstergeler: Durum Tespiti (Veri Ayağı)

*Hazırlanma tarihi: 25 Ekim 2026. Makinece okunabilir tam veri seti (449 satır, her satırda yıl, kaynak ve URL var): `03_VERI/islenmis/turkiye_temel_gostergeler.csv`*

**Yöntem notu.**
- **TÜİK bültenleri:** Doğrudan TÜİK Veri Portalı'ndan (veriportali.tuik.gov.tr) okundu. Eski `data.tuik.gov.tr` adresleri bu portala yönleniyor. Yıllara göre eğilim değerlerinin bir kısmı bülten grafiklerinin üzerindeki etiketlerden okundu; CSV'de bu satırlar "grafik" notuyla işaretli.
- **Uluslararası veriler:** Eurostat, DSÖ (GHO), OECD ve Dünya Bankası verileri doğrudan bu kurumların resmî API'lerinden çekildi.
- **Haber kaynakları:** Yalnızca birincil kaynağa ulaşılamadığında kullanıldı. Bu satırlar CSV'de "ikincil" olarak işaretli.
- **Arama kotası:** Çalışma sırasında web arama kotası doldu. Bu yüzden bazı göstergeler doğrulanamadı; bunlar en sondaki "Veri boşlukları" bölümünde listeleniyor.
- **Sayı biçimi:** Bu belgede ondalık ayırıcı olarak virgül, CSV'de nokta kullanıldı.

---

## En çarpıcı 10 bulgu

1. **Doğurganlık çöküşü.** Toplam doğurganlık hızı (TDH) 2001'de 2,38 iken 2025'te 1,42 oldu ve 2014'ten bu yana kesintisiz düşüyor. 81 ilin 76'sı yenilenme düzeyinin (2,10) altında, 59'u 1,50'nin altında. Yoğun kentte TDH 1,33, kırda 1,75 (TÜİK, Doğum İstatistikleri 2025).
2. **Ailenin küçülmesi ve yalnızlaşma.** Ortalama hane büyüklüğü 2008'de 4,00 kişiydi, 2025'te 3,08'e indi. Tek kişilik hanelerin oranı 2014'te %13,9 iken 2025'te %20,5 oldu. Geniş aile oranı %16,7'den %13,5'e geriledi. Tek başına yaşayan yaşlı sayısı 1,07 milyondan 1,84 milyona çıktı (TÜİK, İstatistiklerle Aile 2025).
3. **Evlilik geriliyor, boşanma artıyor.** Kaba boşanma hızı 2001'de binde 1,41 iken 2025'te binde 2,26 oldu. Kaba evlenme hızı aynı dönemde binde 8,35'ten 6,43'e indi. 2025'te her 100 evliliğe karşılık 35 boşanma var; bu oran 2001'de 17'ydi (TÜİK, Evlenme ve Boşanma İstatistikleri 2025; oran bizim hesabımız).
4. **Gençler ebeveyn evinde kalıyor.** Hiç evlenmemiş 25-29 yaşındakilerin %70'i ebeveyniyle yaşıyor (TÜİK 2025). Gençlerin ebeveyn evinden ayrılma yaşı 28,2; AB ortalaması 26,2 (Eurostat 2024).
5. **"Kentlileşme" oranı idari bir yanılsama.** İl ve ilçe merkezlerinde yaşayanların oranı 2012'de %77,3 iken 2013'te tek yılda %91,3'e sıçradı (2025'te %93,6). Bunun nedeni insanların yer değiştirmesi değil, 6360 sayılı Kanun'la köylerin mahalleye dönüştürülmesi. Uluslararası DEGURBA ölçütüyle 2025'te nüfusun %67,5'i yoğun kentte, %16,8'i kırda yaşıyor (TÜİK ADNKS 2013 ve 2025).
6. **Sıkışık ve kiraya kayan konut.** Nüfusun %37,8'i aşırı kalabalık konutta yaşıyor; AB'de bu oran %16,8. Kişi başına oda sayısı 1,1 (AB 1,7). Ev sahipliği 2014'te %61,1 iken 2025'te %56,9 oldu (Eurostat). Hanelerin %71'i 3 ve daha çok katlı binalarda oturuyor (TÜİK, Bina ve Konut Nitelikleri Araştırması 2021).
7. **Hareketsiz beden.** 15 yaş ve üstündekilerin %86,6'sı iş dışında hiç aerobik fiziksel aktivite yapmıyor. Önerilen 150-300 dakikalık haftalık aktiviteye ulaşanlar erkeklerde %4,1, kadınlarda %2,7. Spora ayrılan ortalama süre günde 12 dakika. Obezite oranı %21,8; erkeklerin %61,8'i fazla kilolu ya da obez (TÜİK, Türkiye Sağlık Araştırması 2025 ve Zaman Kullanım Araştırması 2025).
8. **Ruh sağlığında yükselen sinyaller.** Antidepresan tüketimi 2010'da günlük 1000 kişi başına 32,7 standart doz (DDD) iken 2024'te 58,0 oldu; bu %77'lik bir artış (OECD). Kaba intihar hızı 2019'da yüz binde 4,20 iken 2025'te 5,35 (TÜİK verisi, ikincil aktarım). Doğuşta sağlıklı yaşam süresi 58 yıl, beklenen yaşam süresi 78,5 yıl; yani yaklaşık 20 yıl sağlık sorunlarıyla kısıtlı geçiyor (TÜİK, Hayat Tabloları 2023-2025).
9. **Güven ve sivil katılım çok düşük.** Diğer insanlara güven puanı 10 üzerinden 3,3; AB'de 5,8 (Eurostat 2025). "Çoğu insana güvenilebilir" diyenlerin oranı %14 (Dünya Değerler Araştırması/WVS 2022 ve Pew 2025). Resmî gönüllülük %1,9 (AB %12,3). Dernek üyelik kaydının nüfusa oranı yaklaşık %10.
10. **Uzun çalışma, düşük kadın katılımı, kirli hava.** Haftalık fiili çalışma süresi 42,4 saatle veri veren 36 Avrupa ülkesi arasında en yüksek (AB 35,9; Eurostat 2025). Kadınların işgücüne katılım oranı %36,2 (TÜİK 2025). Yıllık ortalama ince partikül (PM2.5) maruziyeti metreküpte 20,6 mikrogram; bu, DSÖ kılavuz değerinin dört katı (DSÖ 2023). 2024'te DSÖ kılavuz değerlerini karşılayan tek bir il yok (Kara Rapor 2025, ikincil).

---

## 1. Demografi ve aile

| Gösterge | Değer (eğilim) | Yıl | Kaynak |
|---|---|---|---|
| Toplam doğurganlık hızı (TDH) | 2,38 → 2,19 → 2,08 → 1,77 → 1,52 → 1,49 → **1,42** | 2001 / 2014 / 2017 / 2020 / 2023 / 2024 / 2025 | TÜİK Doğum 2025 |
| TDH, en yüksek iller | Şanlıurfa 3,15 · Şırnak 2,53 · Mardin 2,23 | 2025 | TÜİK |
| TDH, en düşük iller | Bartın 1,09 · İzmir 1,10 · Ankara, Eskişehir, Zonguldak 1,11 | 2025 | TÜİK |
| 2,10'un altında / 1,50'nin altında kalan il sayısı | 57 → 76 / 4 → 59 | 2017 → 2025 | TÜİK |
| TDH, kır / orta yoğun kent / yoğun kent | 1,80 / 1,64 / 1,43 → **1,75 / 1,53 / 1,33** | 2023 → 2025 | TÜİK |
| TDH, ilkokul mezunu / yükseköğretim mezunu anne | 2,51 / 1,24 | 2025 | TÜİK |
| Canlı doğum sayısı | 1.323.341 → 1.351.088 → 940.273 → 895.374 | 2001 / 2014 / 2024 / 2025 | TÜİK |
| Annenin ortalama doğum yaşı | 26,7 → 28,4 → 29,4 | 2001 / 2014 / 2025 | TÜİK |
| İlk doğumda ortalama anne yaşı | 25,5 → 27,5 (İstanbul 28,9, Şanlıurfa 24,4) | 2014 → 2025 | TÜİK |
| Kaba evlenme hızı (binde) | 8,35 → 7,77 → 6,67 → 6,43 | 2001 / 2014 / 2024 / 2025 | TÜİK Evlenme-Boşanma 2025 |
| Kaba boşanma hızı (binde) | 1,41 → 1,70 → 2,21 → 2,26 | 2001 / 2014 / 2024 / 2025 | TÜİK |
| Boşanma sayısının evlenme sayısına oranı | %16,9 → %35,1 | 2001 → 2025 | Hesaplama (TÜİK) |
| Ortalama ilk evlenme yaşı, erkek / kadın | 26,0 / 22,7 → 27,5 / 24,4 → 28,5 / 26,0 | 2001 / 2015 / 2025 | TÜİK |
| Ortalama hanehalkı büyüklüğü | 4,00 → 3,30 → 3,08 (Şırnak 4,84, Tunceli 2,49) | 2008 / 2020 / 2025 | TÜİK İstatistiklerle Aile 2025 |
| Tek kişilik hane oranı | %13,9 → %20,5 | 2014 → 2025 | TÜİK |
| Tek çekirdek aile / geniş aile / tek ebeveynli hane | %67,4 / %16,7 / %7,6 → %62,7 / %13,5 / %11,3 | 2014 → 2025 | TÜİK |
| Çocuğuyla aynı adreste yaşayan 65+ | %37,9 (aynı adres, bina veya sokakta: %50,6) | 2025 | TÜİK |
| Hiç evlenmemiş 25-29 yaşındakilerden ebeveyniyle yaşayan | %70,0 | 2025 | TÜİK |
| Ebeveyn evinden ayrılma yaşı, TR (AB) | 26,5 → 27,3 → 28,2 (AB: 26,2) | 2006 / 2015 / 2024 | Eurostat yth_demo_030 |
| 65+ nüfus oranı | %7,1 → %11,1; projeksiyon: %23,1 (2050), %31,7 (2075) | 2007 → 2025 | TÜİK ADNKS ve Projeksiyon |
| Ortanca yaş | 34,9; projeksiyon: 44,8 (2050) | 2025 | TÜİK |
| Nüfus projeksiyonu (ana / düşük senaryo) | 2050'lerin ortasında zirve; 2100'de 77 milyonun / 55 milyonun altı | 2023 bazlı | TÜİK |
| Aile ya da akrabalarla en az haftada bir yüz yüze görüşme | TR %39,7 (2022) · AB %51,0 (2015) | — | Eurostat ilc_scp09 |
| Son 12 ayda aile ya da akrabayla hiç görüşmeyen | TR %8,6 (2022) · AB %3,0 (2015) | — | Eurostat |
| İhtiyaç anında güvenebileceği birinin olması | TR %90,3 · AB %88,8 | 2022 | Eurostat ilc_pw06 |
| Anneyle her gün veya haftada birkaç kez görüşme | %67,4 | 2016 | TAYA 2016 |
| Hane olarak komşu ziyareti (bazen ya da sıklıkla) | TR %45,2 · İstanbul %37,2 · İzmir %27,2 | 2016 | TAYA 2016 |
| Yardım alan haneler içinde aileden yardım alanlar / devletten yardım alanlar | %34,1 / %39,2 (yardım alan hane oranı %11,5) | 2016 | TAYA 2016 |
| Görücü usulü evlilik / çocuğu tarafından haftada birkaç kez ziyaret edilen 60+ | %56,8 / %56,7 | 2021 | TAYA 2021 (TÜİK bülteni) |
| "Çocuklar yaşlılıkta anne-babasına bakmalı" diyenler | %83,1 (huzurevini tercih edenler %15,0) | 2021 | TAYA 2021 |

**Ne anlatıyor?**
- **Doğurganlık her yerde düşüyor.** Düşüş artık bölgesel değil, ülke geneline yayılmış durumda. En hızlı düşüş yoğun kentte ve eğitimli kadınlarda; yoğun kent ile kır arasında yaklaşık 0,4 çocukluk fark var.
- **Aile küçülüyor ama aile bağları sürüyor.** Hanehalkı yapısı küçülüyor ve parçalanıyor. Buna karşın yaşlıların yarısı çocuğuyla aynı sokakta ya da daha yakında oturuyor, insanların %90'ı ihtiyaç anında güvenebileceği birini bildiriyor. Yani aile, bir sosyal güvenlik ağı olarak hâlâ güçlü.
- **Yüz yüze temas Avrupa'nın altında.** Akrabalarla yüz yüze görüşme sıklığı Avrupa'nın gerisinde. Büyük kentlerde, özellikle İzmir'de, komşuluk zayıf.
- **Evlilik giderek erteleniyor.** İlk evlenme yaşı yükseliyor ve 25-29 yaşındaki bekârların %70'i ebeveyn evinde kalıyor. Bu tablo, evliliğin önünde konut ve gelir gibi engellerin bulunduğuna işaret ediyor.

**Kaynaklar:**
- TÜİK bültenleri: [Doğum İstatistikleri 2025](https://veriportali.tuik.gov.tr/tr/press/58018) · [Evlenme ve Boşanma 2025](https://veriportali.tuik.gov.tr/tr/press/58165) · [İstatistiklerle Aile 2025](https://veriportali.tuik.gov.tr/tr/press/58137) · [ADNKS 2025](https://veriportali.tuik.gov.tr/tr/press/53899) · [Nüfus Projeksiyonları 2023-2100](https://veriportali.tuik.gov.tr/tr/press/53699) · [TAYA 2021](https://veriportali.tuik.gov.tr/tr/press/45813)
- Aile ve Sosyal Hizmetler Bakanlığı: [TAYA 2016 raporu](https://www.aile.gov.tr/media/35811/taya-2016.pdf)
- Eurostat: [yth_demo_030](https://ec.europa.eu/eurostat/databrowser/view/yth_demo_030/default/table) · [ilc_scp09](https://ec.europa.eu/eurostat/databrowser/view/ilc_scp09/default/table) · [ilc_pw06](https://ec.europa.eu/eurostat/databrowser/view/ilc_pw06/default/table)

> **Revizyon notu:** TÜİK doğum verilerini 5 yıl geriye dönük olarak güncelliyor. 2024 TDH ilk yayımda 1,48 idi, 2026 bülteninde 1,49 oldu; 2023 TDH 1,51'den 1,52'ye çıktı. 2024 doğum sayısı da 937.559'dan 940.273'e güncellendi.

---

## 2. Kentleşme ve konut

| Gösterge | Değer | Yıl | Kaynak |
|---|---|---|---|
| İl ve ilçe merkezlerinde yaşayanlar (idari "kent" tanımı) | %77,3 → **%91,3** → %93,6 | 2012 → 2013 → 2025 | TÜİK ADNKS 2013 ve 2025 |
| Kentleşme derecesi (DEGURBA): yoğun kent / orta yoğun kent / kır | %67,9 / %14,8 / %17,3 → %67,5 / %15,8 / %16,8 | 2022 → 2025 | TÜİK |
| Yoğun kentin ve kırın yüzölçümündeki payı | %1,6 / %93,5 | 2022 | TÜİK Kent-Kır 2022 |
| BM ve Dünya Bankası kentli nüfus serisi | %69,3 → %73,8 → %78,5 → %87,2 → %89,5 | 2010 / 2012 / 2013 / 2015 / 2025 | Dünya Bankası (ikincil) |
| 30 büyükşehir ilinde yaşayan nüfus payı | ≈%78,0 | 2021 | Hesaplama (Wikipedia il tablosu, ADNKS 2021) |
| İstanbul nüfusu ve Türkiye içindeki payı | 15.754.053 · %18,3 | 2025 | TÜİK ADNKS |
| Nüfus yoğunluğu, İstanbul / Türkiye | 2.943 / 112 kişi/km² | 2025 | TÜİK |
| İstanbul'da yoğun kentte yaşayanların payı | %96,4 | 2022 | TÜİK |
| Hanelerin oturduğu binanın kat sayısı | 1-2 kat %29,0 · 3-4 kat %22,0 · 5-6 kat %27,4 · 7-9 kat %11,9 · 10+ kat %9,5 | 2021 | TÜİK Bina ve Konut Nitelikleri 2021 |
| 3+ katlı binalarda yaşayan haneler içinde asansörsüz binada oturanlar / otoparksız binada oturan haneler | %53,6 / %57,0 | 2021 | TÜİK |
| Ev sahipliği (nüfus bazında) | %60,7 → %61,1 → %58,8 → %55,8 → %56,9 (AB %68,5) | 2006 / 2014 / 2019 / 2024 / 2025 | Eurostat ilc_lvho02 |
| Ev sahibi / kiracı / kira ödemeyen (TÜİK Gelir ve Yaşam Koşulları Araştırması, GYKA) | %57,1 / %27,0 / %15,0 | 2025 | TÜİK Yoksulluk ve Yaşam Koşulları 2025 |
| Piyasa fiyatından kiracı | %21,4 → %27,3 | 2013 → 2025 | Eurostat |
| Aşırı kalabalık konutta yaşayanlar | %51,5 → %46,0 → %40,0 → **%37,8** (AB %16,8) | 2006 / 2015 / 2020 / 2025 | Eurostat ilc_lvho05a |
| Kişi başına oda sayısı | 0,9 → 1,1 (AB 1,7) | 2006 → 2025 | Eurostat ilc_lvho03 |
| Konut maliyeti aşırı yükü (konut gideri gelirin %40'ından fazla) | %14,4 → %14,8 → %10,0 (AB %7,7) | 2023 / 2024 / 2025 | Eurostat ilc_lvho07a |
| TÜFE konut grubundaki yıllık artış (genel TÜFE) | %39,99 (%29,73) | Eylül 2026 | TÜİK TÜFE |
| Konutunda nem veya çürüme sorunu / ısınma (yalıtım) sorunu yaşayanlar | %28,8 / %27,9 | 2025 | TÜİK |
| Kendine ait odası olan çocuklar (0-17 yaş) | %34,0 | 2022 | TÜİK Türkiye Çocuk Araştırması |
| 6 Şubat 2023 depremleri: yıkık veya ağır hasarlı konut / bina / can kaybı | 518.009 konut · 164.000 bina (23.02.2023 itibarıyla) · 53.537 kişi | 2023 | Wikipedia'daki resmî hasar tespitine dayanan aktarım (ikincil) |

**Ne anlatıyor?**
- **"Kentli nüfus %93" bir yanılsama.** Bu oran 6360 sayılı Kanun'un yarattığı bir istatistik kırılması. 2012-2013 arasında köyler kâğıt üzerinde mahalleye dönüştü; BM ve Dünya Bankası serisinde de aynı sıçrama görülüyor. Gerçek yerleşim dokusunu DEGURBA ölçütü yansıtıyor: nüfusun yaklaşık üçte ikisi, ülke topraklarının yalnızca %1,6'sında sıkışık biçimde yaşıyor.
- **Konut stoku dikey ve sıkışık.** Haneler ağırlıklı olarak çok katlı ve büyük ölçüde asansörsüz binalarda oturuyor. Aşırı kalabalık konut oranı AB'nin iki katından fazla.
- **Ev sahipliği geriliyor, kiracılık artıyor.** Ev sahipliği 2014'ten bu yana yaklaşık 4 puan düştü, piyasa fiyatından kiracılık 6 puan arttı. Konut enflasyonu genel enflasyonun üzerinde seyrediyor.

**Kaynaklar:**
- TÜİK bültenleri: [ADNKS 2013](https://veriportali.tuik.gov.tr/tr/press/15974) · [ADNKS 2025](https://veriportali.tuik.gov.tr/tr/press/53899) · [Kent-Kır Nüfus 2022](https://veriportali.tuik.gov.tr/tr/press/49755) · [Bina ve Konut Nitelikleri 2021](https://veriportali.tuik.gov.tr/tr/press/45870) · [Yoksulluk ve Yaşam Koşulları 2025](https://veriportali.tuik.gov.tr/tr/press/53994) · [TÜFE Eylül 2026](https://veriportali.tuik.gov.tr/tr/press/58298)
- Eurostat: [ilc_lvho02](https://ec.europa.eu/eurostat/databrowser/view/ilc_lvho02/default/table) · [ilc_lvho05a](https://ec.europa.eu/eurostat/databrowser/view/ilc_lvho05a/default/table) · [ilc_lvho03](https://ec.europa.eu/eurostat/databrowser/view/ilc_lvho03/default/table) · [ilc_lvho07a](https://ec.europa.eu/eurostat/databrowser/view/ilc_lvho07a/default/table)
- [Dünya Bankası, SP.URB.TOTL.IN.ZS](https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS?locations=TR)
- İkincil: [Wikipedia, 2023 depremleri](https://en.wikipedia.org/wiki/2023_Turkey%E2%80%93Syria_earthquakes)

> **Çelişki notu:** 2024 ev sahipliği oranı Eurostat'ta %55,8, TÜİK bülteninde %56,1 olarak geçiyor. Farkın nedeni muhtemelen tanım ve revizyon farkı. Eurostat "kira ödemeyen" grubu indirimli kiracı (RENT_FR) olarak sınıflıyor.

---

## 3. Ulaşım ve mekân

| Gösterge | Değer | Yıl | Kaynak |
|---|---|---|---|
| Trafiğe kayıtlı toplam taşıt | 33.612.650 (Aralık 2025) → 35.065.235 | Eylül 2026 | TÜİK Motorlu Kara Taşıtları (2025 değeri ikincil aktarım) |
| Trafiğe kayıtlı otomobil | 10.589.337 → 16.232.458 → 17.373.581 → 18.115.875 | 2015 / 2024 / 2025 / Eylül 2026 | TÜİK (2015, 2024 ve 2025 değerleri ikincil aktarım) |
| 1000 kişi başına otomobil | 134,5 → 189,5 → 201,8 → 210,4 | 2015 / 2024 / 2025 / Eylül 2026 | Hesaplama (otomobil sayısı ve ADNKS nüfusu) |
| Yeni otomobil kayıtlarında elektrikli / hibrit payı | %18,6 / %31,8 | Ocak-Eylül 2026 | TÜİK |
| İstanbul: 10 km'lik yolculuk süresi / trafik sıkışıklığı | 22 dk 54 sn / %62 | 2025 | TomTom Traffic Index (ikincil) |
| Günlük ulaşıma ayrılan süre / spora ayrılan süre (10+ yaş ortalaması) | 61 dk / 12 dk | 2025 | TÜİK Zaman Kullanım 2025 |
| Kamuya açık alanların kentsel alandaki payı (Sürdürülebilir Kalkınma Amacı 11.7.1) | TR %13,56 · İstanbul %21,1 · Bingöl %6,2 | 2019-2020 civarı | TÜİK SKG |
| Planlarda kişi başı aktif yeşil alan standardı | 10 m²/kişi (doğrulanmadı) | 2014 yönetmeliği | Mekânsal Planlar Yapım Yönetmeliği |
| Yıllık ortalama PM2.5 maruziyeti (DSÖ kılavuz değeri: 5 µg/m³) | 19,5 → 19,7 → 20,3 → 20,6 µg/m³ (kentsel alanlarda 21,1) | 2012 / 2015 / 2019 / 2023 | DSÖ GHO SDGPM25 |
| DSÖ kılavuz değerlerini karşılayan il sayısı | 0 | 2024 | Kara Rapor 2025 (ikincil) |
| PM2.5 kaynaklı erken ölüm | 62.644 | 2024 | Kara Rapor 2025 (ikincil) |
| En kirli il (partikül madde ortalaması) | Osmaniye 83,6 µg/m³ | 2024 | Kara Rapor 2025 (ikincil) |

**Ne anlatıyor?**
- **Otomobil sahipliği hızla artıyor.** 1000 kişi başına otomobil sayısı on yılda yaklaşık 135'ten 210'a çıktı. Kentler giderek araç merkezli büyüyor; İstanbul'da 10 km'lik yol ortalama 23 dakika sürüyor.
- **Hava, DSÖ ölçütüne göre hiçbir yerde temiz değil.** Ulusal PM2.5 ortalaması DSÖ kılavuz değerinin dört katı ve 2012'den bu yana neredeyse hiç iyileşmedi.
- **Yeşil alan kentsel ölçekte izlenmiyor.** Kişi başı aktif yeşil alan için güncel ve resmî bir kentsel seri bulunamadı; bu, politika açısından kritik bir izleme boşluğu.

**Kaynaklar:**
- TÜİK bültenleri: [Motorlu Kara Taşıtları Eylül 2026](https://veriportali.tuik.gov.tr/tr/press/58046) · [Zaman Kullanım 2025](https://veriportali.tuik.gov.tr/tr/press/62065) · [Sürdürülebilir Kalkınma Göstergeleri](https://veriportali.tuik.gov.tr/tr/press/37194)
- [DSÖ GHO API, SDGPM25](https://ghoapi.azureedge.net/api/SDGPM25)
- [TomTom Traffic Index, İstanbul](https://www.tomtom.com/traffic-index/istanbul-traffic/)
- [Mekânsal Planlar Yapım Yönetmeliği](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=19788&MevzuatTur=7&MevzuatTertip=5)
- İkincil: [Diken'de Kara Rapor 2025 haberi](https://www.diken.com.tr/?p=1644213) · otomobil stoku için [Mynet 2015](https://finans.mynet.com/haber/detay/ekonomi/trafikteki-arac-sayisi-2015te-1-milyon-166-bin-artti/114400/), [Forbes Türkiye 2025](https://www.forbes.com.tr/otomobil/tuik-motorlu-kara-tasitlari-istatistiklerini-acikladi-elektrikli-ve-hibrit-arac-satislari-iki-kat-artti)

---

## 4. Sağlık (fizyolojik ve psikolojik)

| Gösterge | Değer | Yıl | Kaynak |
|---|---|---|---|
| Obezite (15+) | %19,6 → %21,1 → %20,2 → **%21,8** | 2016 / 2019 / 2022 / 2025 | TÜİK Türkiye Sağlık Araştırması (TSA) |
| Obezite, kadın / erkek | %18,5 / %12,3 → %24,8 / %18,7 | 2008 → 2025 | TÜİK TSA |
| Fazla kilolu + obez (vücut kitle indeksi 25 ve üzeri), kadın / erkek | %57,0 / %61,8 | 2025 | Hesaplama (TSA) |
| Çocuk ve ergen obezitesi, 5-19 yaş (model tahmini) | %4,6 → %6,9 → %9,7 (fazla kilolu dahil: %27,5) | 2000 / 2010 / 2024 | DSÖ GHO |
| İş dışında aerobik fiziksel aktivite yapmayanlar (15+) | **%86,6** (erkek %83,5, kadın %89,7) | 2025 | TÜİK TSA 2025 |
| Olağan bir haftada hiç fiziksel aktivite ya da boş zaman faaliyeti olmayanlar | %63,3 | 2025 | TÜİK Sağlık Modülü |
| Yetersiz fiziksel aktivite, 18+ (DSÖ model tahmini) | %40,7 → %44,5 | 2010 → 2022 | DSÖ GHO |
| Diyabet, beyana dayalı (15+) | %10,2 → %11,4 → %11,9 | 2019 / 2022 / 2025 | TÜİK TSA |
| Diyabet, ölçüme dayalı (TURDEP-II, 20+) | %16,5 (yaşa standardize %13,7; TURDEP-I'e göre +%90) | 2010 | Satman ve ark. 2013 |
| Diyabet, 30+ yaşa standardize (DSÖ model tahmini) | %16,3 → %22,2 | 2010 → 2022 | DSÖ GHO |
| Depresif belirti (PHQ-8 ölçeği) / majör depresif belirti | %6,6 / %3,1 (AB %7,0 / %2,7) | 2019 | Eurostat Avrupa Sağlık Görüşme Araştırması (EHIS) |
| Annesince her gün kaygılı ya da depresif olarak tanımlanan çocuklar (5-17) | %7,3 / %4,7 | 2022 | TÜİK Türkiye Çocuk Araştırması |
| Antidepresan tüketimi (günlük 1000 kişi başına DDD) | 32,7 → 40,7 → 48,9 → 60,8 → 58,0 (31 OECD ülkesinin medyanı: 66,7) | 2010 / 2015 / 2020 / 2023 / 2024 | OECD |
| Kaba intihar hızı (yüz binde) | 4,20 → 4,79 → 5,27 → 5,35 (2025'te 4.599 kişi) | 2019 / 2023 / 2024 / 2025 | TÜİK verisi (ikincil); 2024 ve 2025'te kaynaklar arasında küçük fark var |
| İntihar hızı, yaşa standardize (DSÖ tahmini) | 2,9 → 3,7 | 2010 → 2023 | DSÖ GHO |
| Her gün tütün kullananlar (15+) | %28,3 → %30,1 | 2022 → 2025 | TÜİK TSA |
| Doğuşta beklenen yaşam süresi (erkek / kadın) | 78,5 yıl (75,9 / 81,1) | 2023-2025 | TÜİK Hayat Tabloları |
| Doğuşta sağlıklı yaşam süresi (erkek / kadın) | **58,0** yıl (59,1 / 56,9); kısıtlı geçen yıl ≈ 20,5 | 2023-2025 | TÜİK |
| Günde 2 saat ve üzeri internette olan çocuklar, hafta içi / hafta sonu (6-15 yaş) | %42,9 / %53,6 (11-15 yaşta hafta sonu %63,5) | 2024 | TÜİK Çocuklarda Bilişim Teknolojileri Kullanımı |

**Ne anlatıyor?**
- **Asıl sorun hareketsizlik.** En çarpıcı fizyolojik bulgu, nüfusun neredeyse tamamının yürüyüş dışında hiç egzersiz yapmaması. Obezite ve diyabet bu tabloyla birlikte yükseliyor.
- **Ruh sağlığında karışık sinyaller.** Beyana dayalı depresyon oranı AB düzeyinde görünüyor. Buna karşın antidepresan kullanımı 15 yılda yaklaşık iki katına çıktı ve kaba intihar hızı yükseliyor; bu ikisi ruh sağlığı yükünün arttığını gösteriyor.
- **Ömrün yaklaşık dörtte biri kısıtlı geçiyor.** Beklenen yaşam süresi uzarken ömrün yaklaşık dörtte biri sağlık sorunlarıyla kısıtlı geçiyor. Kadınlar daha uzun yaşıyor ama daha kısa süre sağlıklı kalıyor.

**Kaynaklar:**
- TÜİK bültenleri: [TSA 2025](https://veriportali.tuik.gov.tr/tr/press/53990) · [TSA 2019](https://veriportali.tuik.gov.tr/tr/press/33661) · [Sağlık Modülü 2025](https://veriportali.tuik.gov.tr/tr/press/62059) · [Hayat Tabloları 2023-2025](https://veriportali.tuik.gov.tr/tr/press/58232) · [Türkiye Çocuk Araştırması 2022](https://veriportali.tuik.gov.tr/tr/press/49744) · [Çocuklarda Bilişim Teknolojileri 2024](https://veriportali.tuik.gov.tr/tr/press/53638) · [Ölüm ve Ölüm Nedeni 2025](https://veriportali.tuik.gov.tr/tr/press/58233)
- [Eurostat hlth_ehis_mh1e](https://ec.europa.eu/eurostat/databrowser/view/hlth_ehis_mh1e/default/table)
- [OECD Pharmaceutical consumption](https://sdmx.oecd.org/public/rest/data/OECD.ELS.HD,HEALTH_PHMC@DF_PHMC_CONSUM,1.1/all?startPeriod=2010)
- DSÖ GHO göstergeleri: NCD_PAC, NCD_BMI_30A, NCD_BMI_PLUS2C, NCD_DIABETES_PREVALENCE_AGESTD, MH_12
- [TURDEP-II (Eur J Epidemiol 2013)](https://pubmed.ncbi.nlm.nih.gov/23407904/)
- İkincil: [24 Saat, intihar verisi](https://www.24saatgazetesi.com/doc-dr-gulin-ozdamar-unal-6-yilda-yuzde-32-artan-ihtihar-orani-toplumsal-dayanikliligin-kirilmasini-gosteriyor)

---

## 5. Sosyal sermaye, güven, mutluluk ve yurttaşlık

| Gösterge | Değer | Yıl | Kaynak |
|---|---|---|---|
| Diğer insanlara güven puanı (0-10) | 4,5 → 2,7 → 3,4 → **3,3** (AB 5,8) | 2013 / 2018 / 2022 / 2025 | Eurostat ilc_pw03 |
| "Çoğu insana güvenilebilir" diyenler | %9,8 → %15,5 → %8,8 → %11,6 → %14,0 | 1993 / 2004 / 2010 / 2014 / 2022 | Dünya Değerler Araştırması (WVS), Our World in Data üzerinden (ikincil) |
| "Çoğu insana güvenilebilir" / "güvenilemez" diyenler | %14 / %84 | 2025 | Pew (ikincil) |
| Yaşam memnuniyeti puanı (0-10) | 5,8 → 5,4 → 5,7 (AB 7,2) | 2013 / 2022 / 2025 | Eurostat ilc_pw01 |
| Kendini mutlu beyan edenler | %59,6 → %61,2 → %52,4 → %48,2 → %53,3 | 2003 / 2010 / 2019 / 2020 / 2025 | TÜİK Yaşam Memnuniyeti Araştırması |
| Kendini mutsuz beyan edenler | %7,3 → %13,1 → %13,0 | 2003 / 2019 / 2025 | TÜİK |
| En çok mutlu eden kişiler: aile / çocuklar | %69,0 / %15,6 | 2025 | TÜİK |
| En çok mutlu eden değerler: sağlık / sevgi / para | %64,9 / %14,7 / %7,7 | 2025 | TÜİK |
| Faal dernek sayısı / dernek üye kaydı | 103.191 / 8.766.962 (nüfusa oranı ≤%10,2) | 25.10.2026 | İçişleri Bakanlığı Sivil Toplumla İlişkiler Genel Müdürlüğü |
| Resmî / gayriresmî gönüllülük (16+) | %1,9 / %2,6 (AB %12,3 / %13,8) | 2022 | Eurostat ilc_scp19 |
| Sık sık yalnız hissedenler (kadın / erkek / 18-24 yaş) | %34 (%40 / %26 / %40) | 2022 | Üsküdar Üniversitesi ve Method Araştırma, çevrimiçi anket (ikincil) |
| Haftalık fiili çalışma süresi (20-64 yaş) | 46,9 → 44,7 → 43,1 → **42,4** saat (AB 35,9) · Avrupa'da 36 ülke içinde 1. | 2014 / 2019 / 2024 / 2025 | Eurostat lfsa_ewhan2 |
| Tam zamanlı çalışanların haftalık fiili çalışma süresi | 45,9 saat (AB 38,7) | 2025 | Eurostat |
| İşgücüne katılım, kadın / erkek | %36,2 / %71,3 (atıl işgücü oranı %29,7) | 2025 | TÜİK İşgücü 2025 |
| Hane ve aile bakımına ayrılan günlük süre, kadın / erkek | 4 sa 3 dk / 58 dk | 2025 | TÜİK Zaman Kullanım |
| Son 4 haftada sosyal medyada vakit geçirenler | %33,9 → %71,7 | 2015 → 2025 | TÜİK Zaman Kullanım |
| Son 4 haftada gazete ya da dergi okuyanlar / akraba ziyaretinde bulunanlar | %39,4 → %20,1 / %67,5 | 2015 → 2025 / 2025 | TÜİK |

**Ne anlatıyor?**
- **Kişilerarası güven Avrupa'nın en altında.** Türkiye'de güven Avrupa ölçeğinde en düşük düzeyde ve 2013'ten bu yana belirgin biçimde azaldı. Resmî gönüllülük AB'nin altıda biri kadar; aile dışı örgütlü sivil hayat zayıf.
- **Mutluluk aileye dayanıyor.** Mutluluğun ana kaynağı aile, ancak mutlu olanların oranı 2003-2010 düzeyinin yaklaşık 8 puan altında.
- **Zaman yoksulluğu.** Avrupa'nın en uzun çalışma haftası, kadınlara düşen ağır bakım yükü ve hızla yaygınlaşan sosyal medya kullanımı birlikte değerlendirildiğinde, yüz yüze toplumsallaşmaya ve yurttaşlık katılımına ayrılabilecek zamanın daraldığı görülüyor.

**Kaynaklar:**
- Eurostat: [ilc_pw03](https://ec.europa.eu/eurostat/databrowser/view/ilc_pw03/default/table) · [ilc_pw01](https://ec.europa.eu/eurostat/databrowser/view/ilc_pw01/default/table) · [ilc_scp19](https://ec.europa.eu/eurostat/databrowser/view/ilc_scp19/default/table) · [lfsa_ewhan2](https://ec.europa.eu/eurostat/databrowser/view/lfsa_ewhan2/default/table)
- TÜİK bültenleri: [Yaşam Memnuniyeti 2025](https://veriportali.tuik.gov.tr/tr/press/54199) · [Yaşam Memnuniyeti 2019](https://veriportali.tuik.gov.tr/tr/press/33729) · [İşgücü 2025](https://veriportali.tuik.gov.tr/tr/press/57996) · [Zaman Kullanım 2025](https://veriportali.tuik.gov.tr/tr/press/62065)
- [Sivil Toplumla İlişkiler Genel Müdürlüğü](https://www.siviltoplum.gov.tr/)
- İkincil: [Our World in Data, WVS güven serisi](https://ourworldindata.org/grapher/self-reported-trust-attitudes?tab=table&country=~TUR) · [Pew 2025](https://www.pewresearch.org/short-reads/2025/12/01/where-most-people-trust-others-and-where-they-dont-around-the-world/) · [Üsküdar Üniversitesi](https://uskudar.edu.tr/en/new/women-and-young-people-feel-more-lonely/8773)

---

## Veri boşlukları

| Konu | Durum | Nasıl elde edilebilir? |
|---|---|---|
| **TAYA 2021 komşuluk ve akrabalık ilişkileri** (görüşme sıklığı, komşuyla yardımlaşma) | TÜİK bülteninde yok; TAYA 2016'nın da ayrı bir komşuluk bölümü yok. Bu belgede 2016 verisi ve Eurostat 2022 verisi kullanıldı. | TÜİK portalındaki "TAYA 2021 raporu" (indirilebilir rapor) ve tablolar; ASHB Aile ve Toplum Hizmetleri Genel Müdürlüğü'nden mikro veri talebi. TAYA 2006 ve 2011 komşuluk bölümleri karşılaştırma için kullanılabilir. |
| **Kişi başı aktif yeşil alan** (Türkiye ve büyük şehirler) | Güncel resmî bir seri bulunamadı. 10 m²/kişi standardı yönetmelik ekinden (EK-2) doğrudan okunamadı. | Mevzuat.gov.tr'deki yönetmelik eki; İBB, ABB ve İBB İzmir park envanterleri; Çevre, Şehircilik ve İklim Değişikliği Bakanlığı (ÇŞİDB) millet bahçesi istatistikleri; uydu tabanlı ölçüm (Copernicus Urban Atlas, OSM). |
| **İstanbul'da işe gidiş süresi ve toplu taşıma payı** | Yalnızca TomTom verisi var. İBB'nin Ulaşım Ana Planı'ndaki türel dağılım (modal split) bulunamadı. | İBB Ulaşım Ana Planı ve hanehalkı seyahat anketi; TÜİK Zaman Kullanım Araştırması mikro verisi; Moovit Public Transit Index. |
| **Konut fiyatının gelire oranı, kira artışı** | TCMB Konut Fiyat Endeksi'ne ve kira alt endeksine ulaşılamadı; yalnızca TÜFE'deki konut grubu verisi kullanıldı. | TCMB EVDS (KFE, Yeni Konut Fiyat Endeksi); TÜİK TÜFE "gerçek kira" alt kalemi; Endeksa ve Sahibinden kira endeksleri. |
| **Riskli bina sayısı ve kentsel dönüşüm hedefleri** | ÇŞİDB sitesine erişim reddedildi, arama kotası doldu. Resmî sayı doğrulanamadı. | ÇŞİDB Kentsel Dönüşüm Genel Müdürlüğü istatistikleri; 12. Kalkınma Planı (2024-2028) hedef tabloları; İBB ve KOERİ deprem senaryoları. |
| **6 Şubat 2023 resmî hasar sayıları** | Yalnızca ikincil aktarım (Wikipedia) var. Strateji ve Bütçe Başkanlığı (SBB) raporu çok büyük olduğu için okunamadı. | [SBB, 2023 Kahramanmaraş ve Hatay Depremleri Raporu](https://www.sbb.gov.tr/wp-content/uploads/2023/03/2023-Kahramanmaras-ve-Hatay-Depremleri-Raporu.pdf); ÇŞİDB hasar tespit açıklamaları. |
| **Kapalı site (gated community) yaygınlığı** | Ulusal istatistik yok. | Akademik çalışmalar (İstanbul ve Ankara örneklemleri); TÜİK Bina ve Konut Nitelikleri Araştırması mikro verisinde site ve güvenlik değişkenleri; MAKS verisi. |
| **Çocukluk obezitesi (COSI-TUR, ölçüme dayalı)** | Sağlık Bakanlığı raporuna ulaşılamadı; yalnızca DSÖ model tahmini var. | Halk Sağlığı Genel Müdürlüğü'nün COSI-TUR 2013/2016/2022 raporları; DSÖ Avrupa COSI 6. tur bilgi notu. |
| **D vitamini eksikliği, çocuklarda miyopi** | Ulusal temsilî veri bulunamadı. | Hakemli bölgesel çalışmalar (DergiPark, PubMed); Sağlık Bakanlığı e-Nabız laboratuvar verileri. |
| **Antidepresan kutu sayısı (TİTCK)** | Kutu bazlı veri bulunamadı; OECD'nin DDD verisi kullanıldı. | Türkiye İlaç ve Tıbbi Cihaz Kurumu (TİTCK) veya IQVIA satış verisi; meclis soru önergesi yanıtları. |
| **İntihar istatistikleri (birincil tablo)** | TÜİK tablosu indirilebilir dosya olduğu için okunamadı; sayılar haber aktarımından alındı. 2024 ve 2025 hızlarında küçük farklar var (5,22 / 5,27 ve 5,35 / 5,36). | TÜİK Ölüm ve Ölüm Nedeni İstatistikleri 2025 bülteninin "İntihar sayısı ve kaba intihar hızı" tablosu. |
| **Yalnızlık (resmî, temsilî ölçüm)** | Yalnızca çevrimiçi ve resmî olmayan bir anket var (Üsküdar Üniversitesi ve Method, 2022). | Eurostat EU-SILC 2022 refah modülü (yalnızlık sorusu Türkiye için yayımlanmışsa); TÜİK Yaşam Memnuniyeti mikro verisi. |
| **Büyükşehirlerde yaşayan nüfus payı (2025)** | Yalnızca 2021 için ikincil kaynaktan hesaplandı (≈%78). | TÜİK ADNKS 2025 il nüfusu tablosundan 30 büyükşehir toplanarak. |
| **Çocukların sokakta oyunu ve bağımsız hareketi** | Türkiye için ulusal veri yok. | UNICEF ve TÜİK Türkiye Çocuk Araştırması mikro verisi; Children's Independent Mobility (PSI) yöntemiyle yeni bir anket. |
| **Haftalık çalışma saatinde OECD yıllık saat karşılaştırması** | Bu belgede Eurostat'ın haftalık verisi kullanıldı; OECD'nin yıllık saat serisi çekilmedi. | OECD veri tabanı, "Average annual hours actually worked per worker". |
| **Mutluluk serisi (2004-2009 ve 2011-2017)** | Yalnızca grafikteki işaretli yıllar okundu. | TÜİK Yaşam Memnuniyeti zaman serisi tablosu. |
| **Kara Rapor 2026 (2025 verisi)** | Arama kotası dolduğu için kontrol edilemedi. | [Temiz Hava Hakkı Platformu](https://temizhavahakki.org); Çevre Bakanlığı Ulusal Hava Kalitesi İzleme Ağı. |

**Güvenilirlik uyarıları:**
- **6360 kırılması:** "Kentli nüfus" için TÜİK'in idari il ve ilçe merkezi serisi ve BM ile Dünya Bankası serisi, 2012-2015 arasında yapısal bir kırılma içeriyor. Zaman serisi karşılaştırmalarında DEGURBA kullanılmalı; bu seri ancak 2022 ve sonrası için mevcut.
- **Grafikten okunan değerler:** TÜİK grafiklerinden okunan ara yıl değerleri bültenlerdeki etiketlere dayanıyor. Ondalık hassasiyet için TÜİK tablolarıyla teyit önerilir.
- **Model tahminleri:** DSÖ model tahminleri (obezite, diyabet, fiziksel aktivite, intihar) ulusal anketlerden farklı yöntemle üretilir. Bu yüzden düzeylerini TÜİK verisiyle doğrudan kıyaslamak yerine eğilimleri karşılaştırmak daha doğru olur.
