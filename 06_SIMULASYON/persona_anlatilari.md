# Persona Anlatıları: Aynı İnsan, Üç Ortam, Bir İş Günü

*İP7 Zihinsel simülasyonlar · Sürüm 0.1 · 26 Ekim 2026*

Bu dosyada sekiz persona üç ortamda yaşatılıyor:

- **A:** Megakent kapalı sitesi. 12 katlı, çeperde, araca bağımlı.
- **B:** Eski yap-sat apartman mahallesi. 5-6 katlı, karma kullanımlı, yeşilsiz.
- **C:** Model mahalle. Z+2 / Z+3, avlulu, 15 dakikalık erişim.

Anlatılar bir hayal ürünü değil. Her cümledeki sayı `06_SIMULASYON/kod/persona_simulasyonu.py` dosyasının temel senaryosundan geliyor. Tablolar: `sonuclar/persona_gostergeler.csv`, `sonuclar/persona_zaman_butcesi.csv`, `sonuclar/hane_aylik_maliyet.csv`. Varsayımlar: `varsayimlar.csv`. Yolculuk zincirleri: `sonuclar/persona_yolculuk_tanimlari.csv`.

**Okuma kuralları:**

- **Aynı kişi, aynı gelir.** Her persona üç ortamda aynı işte çalışıyor ve aynı geliri kazanıyor. Değişen yalnızca mekân. Bu bir karşı-olgu düşünce deneyi. Gerçekte A'da oturanlar ortalamada daha varlıklı.
- **Konum.** C temel senaryoda B ile aynı konumda: merkeze 10 km. A ise çeperde: merkeze 22 km. C çeperde kurulursa ne olduğu sondaki "Konum mu, biçim mi?" kutusunda.
- **Tanıdık karşılaşma.** Selamlaşma düzeyinde, beklenen sayıdır. Model kalibre edilmedi. Yönü literatürden, büyüklüğü varsayımdan geliyor.
- **Maliyet.** 2026 İstanbul fiyatlarıyla, kaba. Kiracılar için kira + aidat, ev sahipleri için aidat + bakım. Ulaşım araç, yakıt, otopark, abonman ve servisi kapsıyor.
- **Deprem risk sınıfı.** 1 (düşük) ile 5 (çok yüksek) arası, uzman yargısına dayanan bir rubrik. A = 3, B = 4, C = 1. Tahliye süresi, asansör çalışmazken konuttan güvenli toplanma alanına kadar olan süre.

---

## 1. Emre — genç bekâr (27, merkezde ofis çalışanı; kirada, 70 m²; gelir 2 asgari ücret)

**A · Kapalı site.** Emre 7. katta oturuyor ve arabası yok.
- Sabah asansörü bekliyor, site kapısından ana yoldaki durağa 900 m yürüyor (11 dk).
- Otobüsü ortalama 10 dk bekliyor, aktarmayla merkeze ulaşıyor. İşe tek yön **93 dk**.
- Günde 148 dk toplu taşımada, 45 dk yürüyerek geçiyor.
- Eve döndüğünde kendine kalan ev içi serbest zaman **44 dk**.
- Gün ışığında dışarıda 49 dk geçiriyor ve günde ancak 6 tanıdık yüzle karşılaşıyor.
- Konut + ulaşım ayda 29.878 TL, gelirinin %53'ü.

**B · Yap-sat apartman.** Emre 3. katta, asansörsüz bir binada oturuyor.
- Durak 300 m uzakta, işe tek yön **46 dk**. Kendine kalan zaman **144 dk**.
- Spor salonu 800 m, mescit 4 dk.
- Sokak kalabalık ama tanıdık az: günde 8 karşılaşma.
- Ayda 30.648 TL (%55).
- Bina 1970-2000 yap-sat stoku: deprem sınıfı 4.

**C · Model mahalle.** Emre T4 merkez yapısında, asansörlü 2. katta oturuyor.
- İşe yolculuk B ile aynı: **46 dk**, çünkü konum aynı.
- Akşamları mahalle konağındaki spor salonuna (450 m) yürüyor. Meydanda ve komşuluk yeşilinde günde 20 dk geçiriyor.
- Tanıdık karşılaşma **16**, B'nin iki katı.
- Ama kira primi yüzünden ayda 33.868 TL ödüyor (%60). Emre için C, B'den 3.220 TL daha pahalı.
- **Ne öğretiyor:** Genç bekâr için A'nın asıl bedeli parası değil, günde fazladan ≈97 dk yol. C'nin B'ye üstünlüğü ise zaman değil, karşılaşma ve yeşil.

## 2. Zeynep ve Mert — yeni evli çift (26 ve 29; öğretmen ve merkezde satış; kirada, 90 m²; gelir 4,6 asgari ücret)

**A.**
- Mert arabayla merkeze gidiyor: tek yön **64 dk**, günde 123 dk direksiyonda, 46 km. Gün ışığında dışarıda ancak **14 dk** kalıyor.
- Zeynep'in okulu 6 km uzakta. Otobüse binmek için 900 m yürüyor: tek yön 49 dk.
- Pazar alışverişi arabayla AVM'ye.
- Tek araç hanenin aylık giderini 62.913 TL'ye (%49) çıkarıyor. Bunun 29.163 TL'si ulaşım: araç sabiti 12.000, yakıt ve aşınma 10.235, merkezde otopark 3.300 TL.
- Mert'in günlük tanıdık karşılaşması 3.

**B.**
- Arabaları yok. Mert metro-otobüsle 46 dk, Zeynep 23 dk'da işinde.
- Akşam pazara (500 m) birlikte yürüyorlar.
- Ayda 41.996 TL (%33). Kendilerine kalan zaman 152 ve 162 dk.

**C.**
- Yolculuk süreleri B ile neredeyse aynı (45 ve 22 dk).
- Avlu ve komşuluk yeşili günde 20'şer dakikalık dış mekân ekliyor. Tanıdık karşılaşma 15 ve 17.
- Ayda 47.636 TL (%37). Bunun 1.500 TL'si ara sıra kullanılan paylaşımlı araç.
- **Ne öğretiyor:** Çiftin ilk yılında A ile B arasındaki fark ayda 21 bin TL. Bu, 30 yıllık ev edinme yolunu belirleyen fark (bkz. rapor, yaşam döngüsü).

## 3. İki çocuklu aile — Ayşe (36, yarı zamanlı muhasebeci), Ahmet (39, merkezde teknisyen), Elif (8) ve Can (4); kirada, 120 m²; gelir 4 asgari ücret

**A · Kapalı site.** İki araçlı bir hane.
- Ahmet işe tek yön **64 dk**, günde 120 dk araçta. Eve döndüğünde kendine kalan zaman **84 dk**.
- Ayşe Can'ı 1,5 km'deki anaokuluna arabayla götürüyor, oradan 6 km'deki işine geçiyor. Günde 76 dk direksiyonda, 39 dk asansör, otopark ve park yeri aramada.
- **Elif** 25 dakikalık servisle okula gidiyor; servis birçok siteyi dolaşıyor. Okuldan sonra site bahçesinde 40 dk oynuyor.
- Elif'in ebeveynsiz dolaşabildiği alan **4 ha**, site duvarlarının içi. 5 gündelik hedeften 2'sine (yeşil, arkadaş) yalnız gidebiliyor. Okul, bakkal ve mescit ana yolun ötesinde.
- Aylık gider 89.419 TL (%80). Bunun 44.419 TL'si ulaşım: iki araç, yakıt, okul servisi.

**B · Yap-sat apartman.** Tek araç Ahmet'te; işe 38 dk ile üç ortamın en hızlısı.
- Ayşe günde **91 dk** yürüyor: Elif'i 600 m'deki okula, Can'ı 500 m'deki anaokuluna sabah götürüp öğleden sonra geri alıyor.
- Bu eşlik yürüyüşü Ayşe'nin aktivitesi ama Elif'in özgürlüğü değil. Elif'in bağımsız alanı **1 ha**: aynı sokak ve köşedeki bakkal. Okul yolunda trafikli cadde var. Park 700 m uzakta, haftada birkaç kez gidilebiliyor.
- Elif gün ışığında 70 dk dışarıda, üç ortamın en azı.
- Ayşe okul kapısında ve bakkalda günde 31 tanıdıkla karşılaşıyor.
- Aylık gider 70.524 TL (%63).

**C · Model mahalle.** Ailenin arabası yok.
- Ahmet raylı sisteme 300 m yürüyor: tek yön 45 dk. A'dan 19 dk kısa, B'deki arabadan 7 dk uzun.
- **Elif** 400 m'deki okula arkadaşlarıyla **6 dk**'da yürüyor. Okul sokağı araçsız. Okuldan sonra avluda ve komşuluk yeşilinde **75 dk** oynuyor.
- Elif'in bağımsız alanı **12 ha**, araç hücresinin neredeyse tamamı. 5 hedefin 5'ine yalnız ulaşıyor. Gün ışığında **115 dk** dışarıda, A'dan 34 dk fazla.
- Bu fark He ve ark. (2015) randomize deneyine göre üç yıllık miyopi riskini **%12** düşürüyor (%90 aralık: %3-23). Taşınabilirlik indirimi uygulandı; Türkiye'nin taban riski bilinmiyor.
- Ayşe Can'ı 300 m'deki kreşe bırakıyor. Kendine kalan zaman **228 dk**: B'den 28, A'dan 63 dk fazla.
- Aylık gider 60.596 TL (%54). **Uyarı:** Aile C'de bir araç tutarsa gider 73.657 TL'ye çıkıyor ve B'yi geçiyor.
- **Ne öğretiyor:** Çocuğun bağımsızlığı annenin zamanını geri veriyor. C'nin maliyet üstünlüğü ise biçimden değil, arabasız yaşamı mümkün kılmasından geliyor.

## 4. Çok kuşaklı aile — Fatma (68, büyükanne); oğlu, gelini ve iki torunuyla (ev sahibi)

**A.** Beş kişi 8. kattaki 160 m²'lik bir 4+1 dairede yaşıyor.
- Gündüz Fatma çoğunlukla yalnız. Ekmeği 900 m ötedeki kapı dükkânından gün aşırı alıyor, pazara otobüsle gidiyor.
- Mescit 13 dk uzakta.
- Komşu ziyareti günde 20 dk, tanıdık karşılaşma 15.
- Deprem anında asansör kullanılamaz: kalabalık merdivenden toplanma alanına **15 dk**.
- Hanenin nakit gideri 42.125 TL. Bunun 8.000 TL'si iki torunun okul servisi.

**B.** Fatma aynı binanın 1. katında, kendi dairesinde oturuyor. Oğlunun ailesi üst katta; kat karşılığı yapılmış binalarda yaygın bir düzen.
- Bakkal 120 m, mescit 5 dk.
- Günde bir saat komşu ziyareti var, tanıdık karşılaşma 23.
- Yeşil yok. Gün ışığında yalnızca 31 dk dışarıda.
- Gider 26.070 TL.

**C.** Fatma T2 çok kuşaklı evin zemin katında oturuyor. Aile üst iki katta, bahçe ortak.
- Avluda torunlarla günde 40 dk geçiriyor. Mescitte haftada iki sohbete 2,6 dk'da yürüyor.
- Tanıdık karşılaşma **39**, A'nın 2,7 katı.
- Tahliye **2 dk**.
- Hane araçsız. Oğul toplu taşımayla işe gidiyor; gider 11.788 TL.
- Yeşil kanalı (Rojas-Rueda 2019, nedensel pay uygulanmış): yıllık ölüm riski B'de A'ya göre **%4,2 yüksek**, C'de %1,2 düşük. C'nin %90 aralığı sıfırı kapsıyor.

## 5. Hüseyin amca — yalnız yaşlı (76, dul, dizinden rahatsız; ev sahibi; emekli aylığı 0,8 asgari ücret)

**A.** 9. kattaki dairesinden mescide (700 m) asansör dahil **18 dk**'da ulaşıyor.
- Bu yüzden cemaate günde ancak bir vakit gidiyor.
- Ekmek için 900 m yürümek 20 dk sürüyor. Gün aşırı gidiyor, kalan günler sipariş veriyor.
- Site kafesinde kahvehane kültürü yok. Tanıdık karşılaşma **18**.
- Sıcak dalgasında evden az çıkıyor. Yokluğunun bir yakın tanıdıkça 24 saat içinde fark edilme olasılığı **%35**.
- Deprem anında 9 kattan inmesi gerekiyor: tahliye **17,5 dk**.

**B.** 4. kat, asansörsüz. Her çıkışta 4 kat merdiven iniyor ve çıkıyor; bu, günde ≈36 dk merdiven demek.
- Yine de mescit merdiven dahil 10 dk. Günde iki vakit cemaate gidiyor, kahvehanede bir saat oturuyor.
- Tanıdık karşılaşma **56**.
- Yokluğunun fark edilme olasılığı %72.
- Merdiven tahliyeyi de uzatıyor: 14,8 dk.

**C.** Zemin kattaki yaşlı dairesinde oturuyor.
- Mescit 150 m, **3,6 dk**. Günde üç vakit cemaate gidiyor.
- Meydandaki çay bahçesinde 50 dk, avlu ve çeşme başında 40 dk geçiriyor.
- Gün ışığında 115 dk dışarıda. Tanıdık karşılaşma **87**. Yokluğunun fark edilme olasılığı **%86**.
- Tahliye 3,3 dk.
- **Ne öğretiyor:** B'nin karma dokusu yaşlıyı topluluğa bağlıyor, merdiveni ise onu eve kapatıyor. C, ilkini koruyup ikincisini kaldırıyor.

## 6. Selin — engelli birey (31, tekerlekli sandalye kullanıcısı; haftada üç gün semtte ofis; annesiyle kirada, 85 m²)

**A.**
- Site içi rampalı ve asansörlü. Ama site kapısının dışında sürekli bir kaldırım yok.
- Uyarlanmış aracıyla işe 23 dk'da gidiyor. Bakkala bile arabayla gidiyor.
- Günde 2,5 bağımsız yolculuk yapabiliyor; hepsi araca bağlı. Tanıdık karşılaşma 4.
- Deprem anında 4. kattan taşınarak indirilmesi gerekiyor: **28 dk**.
- Gider 47.890 TL (%66).

**B.**
- Zemin katta oturuyor ama binanın girişinde basamak var. Kaldırımlar kırık ve araçlarla dolu.
- Her çıkışı yardıma bağlı. **Bağımsız yolculuk: 0.**
- İşe erişilebilir taksiyle gidiyor; bu ayda 9.100 TL tutuyor.
- Mescide bağımsız erişemiyor. Gün ışığında 17 dk dışarıda.

**C.**
- Paylaşımlı, kotsuz sokak yüzeyi. Zemin katta oturuyor.
- 300 m'deki alçak tabanlı otobüse tekerlekli sandalyesiyle gidiyor: işe 23,5 dk.
- Bağımsız yolculuk 2,5, dış mekân 58 dk, tanıdık karşılaşma **18**.
- Tahliye 2,5 dk. Gider 36.720 TL (%50).
- **Ne öğretiyor:** Erişilebilirlik bina içinde değil, kapıdan sokağa geçişte kazanılıyor ya da kaybediliyor.

## 7. Mehmet usta — esnaf (52, bakkal; ailesiyle, ev sahibi; kazanç 2,5 asgari ücret)

**A.**
- Siteye taşınmış, dükkânı eski semtte kalmış: 12 km. Günde 61 dk araçta.
- Öğle yemeğine eve gidemiyor.
- Müşterileri komşusu değil. Konut çevresinde tanıdık karşılaşma 13.
- Kendine kalan zaman 80 dk.
- Site çevresine dükkân açsa, 300 m yürüme havzasında yalnızca ≈2.900 kişi bulunacak.

**B.**
- Dükkân evinin 150 m altında: 2,4 dk. Öğlen eve yemeğe çıkıyor. Öğle ve ikindiyi 250 m'deki camide kılıyor.
- Müşterilerinin çoğu komşusu: günde 58 tanıdık karşılaşma.
- 300 m havzasında ≈**7.800** kişi var. Üç ortamın en güçlü esnaf zemini.
- Gider 17.634 TL.

**C.**
- Dükkân meydandaki T4 yapısının zemin katında, evinden 350 m uzakta.
- Tanıdık karşılaşma 81.
- Havza ≈3.500 kişi. C'nin yoğunluğu B'den düşük, bu yüzden müşteri tabanı da küçük. Ancak mahallede 7.200 kişiye 80-120 dükkân planlanıyor.
- Toptancı için bir araç tutuyor; bölgesel otoparkla gider 19.001 TL.
- **Ne öğretiyor:** Esnafın ekonomik dayanıklılığı için yoğunluk önemli. C'nin bu açığı mahalle çarşısının ölçeği ve ticaret tahsisiyle kapatılmalı.

## 8. Deniz — üniversite öğrencisi (20; ailesiyle oturuyor)

**A.**
- Kampüs 25 km uzakta: tek yön **101 dk**, günde 164 dk toplu taşımada.
- Kendine kalan zaman 121 dk. Tanıdık karşılaşma 5.

**B.**
- Tek yön 51 dk. Evde çalışıyor; kendine kalan zaman 222 dk.

**C.**
- Tek yön 51 dk. Akşam iki saati mahalle konağının kütüphanesinde (450 m) geçiriyor.
- Tanıdık karşılaşma 17. Hanenin konut + ulaşım gideri B'den ayda ≈10 bin TL düşük (araçsız aile).

---

## Konum mu, biçim mi? (duyarlılık: `sonuclar/duyarlilik_c.csv`)

C, A'nın konumunda kurulursa sonuçlar şöyle değişiyor: merkeze 22 km, raylı sistem 32 km/sa, kira 360 TL/m².

- **Yolculuk:** C'nin işe gidiş üstünlüğü büyük ölçüde eriyor. Mert'in yolu 59 dk (A'da 64), Ahmet'in 59 dk (64), Deniz'inki 65 dk (101).
- **Biçimden gelen kazançlar:** Değişmiyor. Bunlar çocuğun bağımsız alanı, yaşlının mescide erişimi, tanıdık karşılaşma, tahliye süresi ve zemine açılan hane payı.
- **Ders:** İşe gidiş süresi konum ve toplu taşıma sorunu. Çocuk, yaşlı, deprem ve komşuluk ise biçim sorunu.
