# Durum Tespiti — Faz 1 Sentez Raporu

*25 Ekim 2026 · Sürüm 0.1*

Bu rapor, Faz 1'in dört temel derlemesini tek bir teşhis ve tez etrafında birleştiriyor:

- istatistikler,
- literatür,
- örnek uygulamalar ve tasarım parametreleri,
- mevzuat ve veri kaynakları.

Ayrıntılar ve tüm kaynaklar ilgili dosyalarda:

| Konu | Dosya |
|---|---|
| Türkiye göstergeleri (449 satır, kaynaklı) | [03_VERI/turkiye_temel_gostergeler.md](../03_VERI/turkiye_temel_gostergeler.md) · [CSV](../03_VERI/islenmis/turkiye_temel_gostergeler.csv) |
| Literatür haritası (131 kaynak, 113'ü doğrulandı) | [02_LITERATUR/literatur_haritasi.md](../02_LITERATUR/literatur_haritasi.md) · [kaynakca.csv](../02_LITERATUR/kaynakca.csv) |
| Örnek uygulamalar (20+ vaka) | [02_LITERATUR/ornek_uygulamalar.md](../02_LITERATUR/ornek_uygulamalar.md) |
| Tasarım parametreleri ve taslak mahalle programı | [07_TASARIM_CIZIM/tasarim_parametreleri.md](../07_TASARIM_CIZIM/tasarim_parametreleri.md) |
| "Aynı yoğunluk, üç biçim" teknik çizimi | [07_TASARIM_CIZIM/ayni_yogunluk_uc_bicim.png](../07_TASARIM_CIZIM/ayni_yogunluk_uc_bicim.png) |
| Mevzuat ve politika haritası | [08_MEVZUAT_POLITIKA/mevzuat_politika_haritasi.md](../08_MEVZUAT_POLITIKA/mevzuat_politika_haritasi.md) |
| Veri kaynakları kataloğu | [03_VERI/veri_kaynaklari_katalogu.md](../03_VERI/veri_kaynaklari_katalogu.md) |

---

## 1. Teşhis tek cümlede

> Türkiye'nin şehirleri **dikey, sıkışık, otomobile bağımlı, yeşilsiz ve kiraya kayan** bir yapıya dönüştü. Bu yapının içinde yaşayan insanlar **hareketsizleşiyor, yalnızlaşıyor, birbirine güvenmiyor, evliliği erteliyor ve az çocuk sahibi oluyor**. Buna karşın Türkiye'nin elinde Avrupa'da benzeri az bulunan bir sermaye hâlâ duruyor: **ayakta kalan bir aile ağı**. Sorun şu ki bugünkü mekân bu ağı taşımıyor, aşındırıyor.

---

## 2. Sayılarla tablo

### 2.1 Aile ve nüfus: düşüş genelleşti

| Gösterge | Değer | Karşılaştırma |
|---|---|---|
| Toplam doğurganlık hızı | **1,42** (2025) | 2001'de 2,38; 81 ilin 76'sı yenilenme düzeyinin altında |
| Doğurganlık: yoğun kent / kır | **1,33 / 1,75** | Fark ≈ 0,4 çocuk |
| Doğurganlık: ilkokul / yükseköğretim mezunu anne | **2,51 / 1,24** | Fark ≈ 1,3 çocuk |
| Kaba evlenme / boşanma hızı (binde) | 6,43 / 2,26 (2025) | 2001'de 8,35 / 1,41 |
| Her 100 evliliğe karşılık boşanma | **35** | 2001'de 17 |
| İlk evlenme yaşı, erkek / kadın | 28,5 / 26,0 | 2001'de 26,0 / 22,7 |
| Ebeveyniyle yaşayan, hiç evlenmemiş 25–29 yaşındakiler | **%70** | Ebeveyn evinden ayrılma yaşı 28,2 (AB 26,2) |
| Tek kişilik hane | %20,5 | 2014'te %13,9 |
| 65+ nüfus | %11,1 | 2050 projeksiyonu %23,1 |

**Dikkat:** Annenin eğitimine göre doğurganlık farkı, kent ile kır arasındaki farkın yaklaşık üç katı. Demek ki mekân doğurganlığın tek, hatta en büyük belirleyicisi değil. Projenin işi, mekânın payını diğer etkenlerden ayırarak ölçmek (Faz 2, il ve ilçe paneli).

### 2.2 Konut: dikey, sıkışık, ulaşılmaz

| Gösterge | Değer | Karşılaştırma |
|---|---|---|
| 3 ve daha çok katlı binada oturan haneler | **%71** (2021) | 7+ katlı binada oturanlar %21,4 |
| Aşırı kalabalık konutta yaşayanlar | **%37,8** | AB %16,8 |
| Kişi başına oda sayısı | 1,1 | AB 1,7 |
| Kendine ait odası olan çocuklar | %34 | — |
| Ev sahipliği | %56,9 (2025) | 2014'te %61,1; AB %68,5 |
| Piyasa fiyatından kiracılar | %27,3 | 2013'te %21,4 |
| 6 Şubat 2023: yıkık veya ağır hasarlı konut | ≈518 bin (ikincil kaynak) | 53.537 can kaybı |

### 2.3 Beden: hareketsiz

| Gösterge | Değer |
|---|---|
| İş dışında hiç aerobik aktivite yapmayanlar (15+) | **%86,6** |
| Günlük ulaşıma ayrılan süre / spora ayrılan süre | 61 dk / 12 dk |
| Obezite (15+) | %21,8; erkeklerin %61,8'i fazla kilolu ya da obez |
| Diyabet, 30+ yaşa standardize (DSÖ tahmini) | %22,2 |
| 1000 kişi başına otomobil | 135'ten 210'a (2015 → 2026) |
| PM2.5 maruziyeti | DSÖ kılavuz değerinin 4 katı; ölçütü karşılayan il yok |
| Sağlıklı yaşam süresi / beklenen yaşam süresi | 58,0 / 78,5 yıl |

### 2.4 Ruh ve toplum: güvensiz ve zamansız

| Gösterge | Değer | Karşılaştırma |
|---|---|---|
| Antidepresan tüketimi (günlük 1000 kişi başına standart doz) | 32,7 → **58,0** | 2010 → 2024, %77 artış |
| Diğer insanlara güven (0–10) | **3,3** | AB 5,8 |
| Resmî gönüllülük | **%1,9** | AB %12,3 |
| Akrabalarla en az haftada bir yüz yüze görüşme | %39,7 | AB %51 |
| Haftalık fiili çalışma süresi | **42,4 saat** | Avrupa'da 36 ülke içinde en uzun |
| Kadınların işgücüne katılımı | %36,2 | Günde 4 saat bakım işi (erkekler 58 dk) |
| Kendini mutlu beyan edenler | %53,3 | 2010'da %61,2 |

### 2.5 Sermaye: aile ağı hâlâ ayakta

| Gösterge | Değer |
|---|---|
| Çocuğuyla aynı adreste, binada ya da sokakta oturan 65+ | **%50,6** |
| İhtiyaç anında güvenebileceği biri olanlar | %90,3 (AB %88,8) |
| En çok mutlu eden kişiler: aile | %69 |
| "Çocuklar yaşlılıkta anne-babasına bakmalı" diyenler | %83,1 |

Bu son tablo projenin umut noktası. Türkiye, aile ve kuşaklar arası dayanışmanın hâlâ güçlü olduğu nadir toplumlardan biri. Uygun mekânsal çerçeve bu sermayeyi koruyup büyütebilir. Mevcut gidişat ise onu birkaç on yıl içinde tüketebilir.

### 2.6 İstatistik yanılsaması

"Nüfusun %93'ü kentli" bilgisi yanıltıcı. Bu oran, 6360 sayılı Kanun'la 2012–2013'te köylerin mahalleye dönüştürülmesinin sonucu. Uluslararası DEGURBA ölçütüyle nüfusun %67,5'i yoğun kentte yaşıyor ve bu nüfus ülke topraklarının yalnızca **%1,6'sına** sıkışmış durumda. Mekânsal politika için doğru ölçü DEGURBA.

---

## 3. Literatür ne diyor?

Kanıt gücü kısaltmaları: **G** güçlü · **O** orta · **Z** zayıf.

| # | Önerme | Kanıt | Tasarım karşılığı |
|---|---|---|---|
| 1 | Kent yaşamı psikoz, duygudurum ve anksiyete riskini artırır (şizofrenide OR 2,37) | İlişki G, nedensellik Z–O | Tanıdıklığı artıran mahalle ölçeği |
| 2 | Konuta yakın yeşil alan ruh sağlığını iyileştirir, ölümü azaltır | O–G | 300 m içinde en az 0,5 ha yeşil |
| 3 | Dışarıda geçen süre çocuklarda miyopiyi azaltır (RKÇ: %39,5'ten %30,4'e) | G, nedensel | Güvenli sokak, avlu, okul bahçesi |
| 4 | Yürünebilir ve karma mahalle haftada 68–89 dk daha fazla aktivite sağlar | O–G | Sık sokak ağı, karma kullanım |
| 5 | Yüksek katlı konut, çocuklu ailelerde komşuluk bağlarını ve iyi oluşu zayıflatır | O–Z | Yoğunluğu yükseklikle değil dokuyla sağlamak |
| 6 | Konut maliyeti kiracıların doğurganlığını düşürür (−%2,4), ev sahiplerininkini artırır (+%5) | O, yarı-deneysel | Aile ölçekli konuta mülkiyet yolu |
| 7 | Bahçeli aile konutunda doğurganlık daha yüksektir; ancak farkın çoğu seçilimden gelir | O / Z–O | Büyüyebilen ev |
| 8 | Yoğunluk arttıkça doğurganlık düşer; dindarlık bu etkiyi zayıflatır | O, korelasyonel | — |
| 9 | Büyükanne-büyükbaba yakınlığı ek çocuğu ve annenin işgücüne katılımını artırır | O | Çok kuşaklı konut karışımı |
| 10 | Uzun işe gidiş süresi iyi oluşu ve sivil katılımı düşürür | O | 15 dakikalık mahalle |
| 11 | Yalnızlık ölüm riskini %26–32 artırır; yürünebilir mahalle sosyal sermayeyi artırır | G / Z–O | Karşılaşma üreten sokak |
| 12 | Küçük yönetim birimi ve yaygın mülkiyet yerel katılımı artırır | O–Z (ampirik), G (normatif) | Mahalle yönetişimi |

**Projenin özgün katkı alanı — yoğunluk paradoksu:** Yoğunluk fiziksel aktiviteyi ve toplu taşımayı destekliyor. Öte yandan doğurganlıkla negatif, yalnızlıkla pozitif ilişkili. Literatürün işaret ettiği uzlaşma **alçak-orta katlı ama sık dokulu yerleşim**, fakat bu doğrudan test edilmiş değil. Türkiye verisiyle bunu sınamak projenin bilimsel katkısı olabilir.

**Literatürden çıkan uyarılar:**
- **Kent etkisinin kaynağı:** "Kent hastalık yapar" bulgusunun bir kısmı aile içi karıştırıcılardan kaynaklanıyor. Kardeş karşılaştırmalarında etki zayıflıyor.
- **Sayısal eşikler:** Dunbar sayısı ve Mavi Bölgeler gibi popüler kavramların verisi sorgulanıyor. Alexander'ın 4 kat sınırı normatif bir öneri, ampirik değil.
- **Geleneğin sınırları:** Yerli geleneğin de zaafları var (vakıf sisteminin kurumsal katılığı, idealize edilmiş "Türk evi"). Gelenek kopyalanmamalı, ilkeleri çıkarılmalı.
- **Uygulamanın yöntemi:** TOKİ ve kentsel dönüşüm literatürü, merkezden ve zorla dönüşümün yerinden etme ve mülkiyet transferi ürettiğinde birleşiyor. "Fıtrata uygun şehir" aynı araçlarla dayatılırsa kendi hürriyet hedefiyle çelişir.

---

## 4. Dünyadan ve geçmişten dersler

| Ders | Kanıt |
|---|---|
| Geçiş trafiğini mahalle dışına almak işe yarıyor | Pontevedra: merkez trafiği −%70, 2011–2020 arasında trafik ölümü yok |
| Yoğunluk kat yüksekliğiyle değil, ada kullanımıyla sağlanabilir | Vauban: çoğunlukla 4 kat, ≈135 kişi/ha |
| Çocuğun okula yalnız yürümesi bir tasarım ölçütü olabilir | Japonya: 5. sınıfların %92–93'ü okula yürüyor |
| Küçük parsel, çok yapımcı ve kooperatif modeli çalışıyor | Rieselfeld, Vauban yapı grupları, Ankara Batıkent |
| Mekân gerekli ama yeterli değil | Singapur ebeveyne yakın oturma hibesi verdiği hâlde doğurganlık 0,87. Macaristan'da yükseliş geri döndü. İsrail apartman yaşamına rağmen 2,87 |
| Osmanlı mahallesi bir yönetişim birimiydi | En az ≈50 hane, ≈1.000 kişi; imam, muhtar, karşılıklı kefalet |

**En önemli ders (Macaristan, Kore, İsrail ve Singapur karşılaştırması):** Doğurganlığı belirleyen bileşimde **değerler ve topluluk normları, konuta erişim ve mülkiyet, zaman ve iş düzeni ile mekân** birlikte rol oynuyor. Yalnız para teşviki de, yalnız mekân da kalıcı sonuç vermiyor. Proje bu dört kaldıracı birlikte tasarlamalı.

---

## 5. Mevzuat ve politika

**Temel tespit:** Bugünkü biçimi (kule apartman, parsel parsel yoğunluk, parsel içi otopark, küçük daire) tesadüf değil. Bu biçim, varsayılan imar kurallarının ve kat karşılığı finansman modelinin doğal ürünü. Değişimin kaldıraçları da bu yüzden belli maddelerde toplanıyor.

### 5.1 En kritik kaldıraçlar

Ayrıntı: [08_MEVZUAT_POLITIKA/mevzuat_politika_haritasi.md](../08_MEVZUAT_POLITIKA/mevzuat_politika_haritasi.md)

| # | Düzenleme | Sorun | Yön |
|---|---|---|---|
| 1 | Planlı Alanlar İmar Yönetmeliği (PAİY) md. 5(6), 9, 23; 3194 md. 8 | Varsayılan kurallar kule apartman üretiyor | "Yatay mimari"nin bağlayıcı karşılığı burada kurulabilir |
| 2 | 3194 Ek md. 8 | Değer artış payı ve donatı şartı var; riskli yapıya %20 emsal istisnası tanınıyor | İstisna, emsal artışını yeniden teşvik ediyor |
| 3 | Mekânsal Planlar Yapım Yönetmeliği (MPYY) EK-2 ve md. 12 | Donatı standardı çocuk nüfusuna göre değişmiyor; mesafe yaya ağı üzerinden ölçülmüyor | Çocuk nüfusuna duyarlı ve yürüme ağına dayalı standart |
| 4 | PAİY md. 19 | Kreş ve oyun bahçesi ancak büyük projelerde (150 / 75 bağımsız bölüm üstü) zorunlu | Küçük ölçekte de zorunlu kılmak |
| 5 | Otopark Yönetmeliği | Parsel içi otopark zorunlu; bedel geliri yalnızca otoparka harcanabiliyor | Mahalle kenarında bölgesel otopark |
| 6 | 6306 (7471 ile salt çoğunluk) ve kat karşılığı | Dönüşüm ek emsale dayanıyor | Ada bazlı, aile etkisi değerlendirilmiş dönüşüm |
| 7 | 634 Kat Mülkiyeti md. 66–74 | Yönetim planı değişiklik eşiği 7579 ile 2/3'e indi | Ortak avlu ve site yönetişimi için fırsat |
| 8 | 5393 ve 5216 | Mahalle yalnızca idari birim, planlama birimi değil | Mahalleyi planlama ve yönetişim birimi yapmak |
| 9 | 2985 (TOKİ) ve Yüzyılın Konut Projesi | Konutlar 55–80 m², 3+1 yok | 2,1 doğurganlık hedefiyle çelişiyor |
| 10 | Genelge 2026/4 md. 2 ve 9 | Aile ve nüfus etki değerlendirmesi düzenleyici etki analizine giriyor | **Tüm imar mevzuatı için giriş kapısı** |

### 5.2 Politika penceresi açık

- **"Aile ve Nüfus On Yılı" (2026–2035):** 23.05.2025'te ilan edildi. Genelge 2026/4'ün (RG 02.05.2026) md. 8'i kentsel mekânların aile ve çocuk odaklı dönüşümünü istiyor.
- **12. Kalkınma Planı:** Toplam doğurganlık hızında 2028 hedefi 2,1. Gerçekleşen değer 1,42 (2025).
- **Yeni kurumlar:** Aile Enstitüsü ve Nüfus Politikaları Kurulu (Aralık 2024).
- **Son mevzuat değişiklikleri:** 7579 sayılı Kanun (RG 22.05.2026), PAİY (RG 01.07.2026) ve MPYY (RG 22.01.2026) değişiklikleri.
- **İklim:** İklim Kanunu'na göre yerel iklim eylem planları 31.12.2027'ye kadar hazırlanacak.
- **Mekânsal Strateji Planı** hâlâ taslak. "Yatay mimari" için bağlayıcı bir metin bulunamadı.

**Çıkarım:** Devletin açıkladığı hedefler (2,1 doğurganlık, aile odaklı kentsel mekân) ile yürürlükteki imar ve konut araçları (kule üreten varsayılan kurallar, 55–80 m²'lik konut, ek emsale dayalı dönüşüm) arasında açık bir **tutarsızlık** var. Projenin politika önerileri doğrudan bu tutarsızlığı hedeflemeli. En güçlü kaldıraç, aile ve nüfus etki değerlendirmesinin imar düzenlemelerine somut ölçütlerle uygulanması.

> **Doğrulama notu:** Arama kotası dolduğu için MPYY EK-2 ve Otopark Ek-1'in sayısal tabloları ile bazı künyeler "doğrulanmadı" olarak işaretli. Resmî Gazete künyeleri bir sonraki oturumda mevzuat.gov.tr'den teyit edilecek.

---

## 6. İlk tez: "alçak-orta katlı sık doku + mahalle yönetişimi + erişilebilir mülkiyet"

Faz 1 bulgularından çıkan çalışma tezi:

1. **Biçim:** Konut ağırlıkla zemin + 2 / zemin + 3 katlı, bitişik nizam, avlulu, sık sokaklı bir dokuda olmalı. "Aynı yoğunluk, üç biçim" çizimi gösteriyor ki hektarda yaklaşık 100 hane, 12 katlı bloklarla da, 4 katlı çevre adasıyla da, 3 katlı avlulu sıra evlerle de sağlanabiliyor. Az katlı seçenekler üstelik daha fazla inşaat alanı ve her haneye zemin veya avlu teması veriyor.
2. **Ölçek:** 5.000–8.000 kişilik, 400–500 m yarıçaplı mahalle. İçinde 150–300 hanelik komşuluk birimleri ve 8–12 hanelik avlu grupları. Cami ≤400 m, mescit ≤150 m, ilkokul ≤500 m, yeşil alan ≤300 m.
3. **Aile:** Çok kuşaklı ve büyüyebilen konut tipleri, ebeveyne yakın oturma teşviki, aile ölçekli konutta mülkiyet yolu (kooperatif, küçük parsel, arsa payı).
4. **Yönetişim:** Mahalle, muhtarlığın ötesinde gerçek bir yönetişim birimi olmalı (mahalle meclisi, vakıf ve kooperatif, ortak avlunun yönetimi). Dönüşüm gönüllü ve katılımcı olmalı, zorlayıcı olmamalı.
5. **Zaman:** İş ile konutu yakınlaştırmak (karma kullanım, ev-atölye), geçiş trafiğini mahalle dışına almak, çocuğun bağımsız hareketini mümkün kılmak.

Bu tez **sınanacak**, peşinen kabul edilmeyecek. Faz 2'deki ölçümler, Faz 4'teki simülasyonlar ve pilot uygulamalar onu destekleyebilir, değiştirebilir ya da çürütebilir.

---

## 7. Veri boşlukları ve sonraki adımlar

### 7.1 Öncelikli veri boşlukları

| Konu | Durum |
|---|---|
| TAYA 2021 komşuluk ve akrabalık verisi | Bültende yok; rapor ya da mikro veri gerekiyor |
| Kişi başı aktif yeşil alan | Resmî kentsel seri yok; OSM ve uydu ile ölçülecek |
| İşe gidiş süresi ve toplu taşıma payı (İstanbul) | İBB Ulaşım Ana Planı gerekiyor |
| Konut fiyatının gelire oranı | TCMB konut fiyat endeksi gerekiyor |
| Riskli bina sayısı ve dönüşüm hedefleri | ÇŞİDB ve 12. Kalkınma Planı tabloları gerekiyor |
| 6 Şubat 2023 hasar sayıları (resmî) | Strateji ve Bütçe Başkanlığı (SBB) raporu gerekiyor |
| Kapalı site yaygınlığı | Ulusal veri yok; OSM ve uydu ile ölçülecek |
| Çocukların bağımsız hareketi | Ulusal veri yok; saha anketi gerekiyor |
| Çocukluk obezitesi (ölçüme dayalı) | COSI-TUR raporu gerekiyor |

### 7.2 Faz 2 için önerilen ilk işler

1. **81 il paneli:** Doğurganlık, evlenme, boşanma, hane yapısı, bina kat dağılımı, ev sahipliği, gelir ve eğitim verileri. İlk çok değişkenli analiz (mekânın payı) ve Türkiye koroplet haritaları.
2. **Pilot şehir seçimi** ve OSM + GHSL ile mahalle düzeyinde ölçüm (yükseklik, yeşil erişimi, 15 dakikalık erişim). İlk FUE haritaları.
3. **Persona "bir gün" simülasyonu v1:** A/B/C ortamlarında 8 persona, literatür katsayılarıyla.
4. **Geleneksel doku ölçümü:** Safranbolu, Beypazarı ve tarihî İstanbul mahallelerinin parsel, sokak ve kat ölçüleri.
5. **Taslak mahalle programının çizime dökülmesi:** Vaziyet planı, sokak kesitleri, tipolojiler.
