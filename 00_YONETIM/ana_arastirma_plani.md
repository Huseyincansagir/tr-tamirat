# TR TAMİRAT — Ana Araştırma ve Dönüşüm Planı

*Sürüm 0.1 — 25 Ekim 2026*

---

## 0. Özet

Bu program, Türkiye'nin son yarım yüzyılda kurduğu şehir yapısının (kat karşılığı apartmanlaşma, yüksek bloklu toplu konut, kapalı siteler, otomobile bağımlı yayılma, mahalle kurumlarının çözülmesi) insan, aile ve toplum üzerindeki etkilerini kanıta dayalı olarak incelemeyi amaçlıyor. Ardından insan fıtratına uygun, sürdürülebilir bir şehir modelini tanımlayıp sınamayı ve bu modele geçişin hukuki, mali ve kurumsal yol haritasını çıkarmayı hedefliyor.

Program on iş paketinden ve beş fazdan oluşuyor. Somut çıktılar şunlar:

- Türkiye durum tespiti raporu ve il/ilçe veri paneli
- Fıtrat Uyum Endeksi (FUE) ve haritaları
- Literatür ve kanıt haritası
- Geleneksel doku ve örnek vaka analizleri
- Model mahalle tasarımı ve teknik çizimler
- Zihinsel ve hesaplamalı simülasyonlar
- Mevzuat değişiklik önerileri
- Pilot uygulama planı

**Temel ilke:** Büyük iddialar ancak büyük kanıtla kurulur. Program, "apartman aileyi bitirdi" gibi sezgileri peşinen doğru kabul etmez. Bunları **sınanabilir hipotezlere** çevirir, etki büyüklüklerini ölçer ve yapılı çevrenin gelir, eğitim, kültür ve ekonomi gibi diğer etkenler yanındaki payını dürüstçe ortaya koyar.

---

## 1. Problem tanımı

### 1.1 Gözlenen eğilimler (durum tespitiyle sayısallaştırılacak)

- **Aile ve nüfus:** Doğurganlığın nüfusun kendini yenileme düzeyinin (2,1) belirgin biçimde altına düşmesi, ilk evlenme yaşının yükselmesi, boşanmanın ve tek kişilik hanelerin artması, hızlı yaşlanma.
- **Beden:** Obezite, fiziksel hareketsizlik ve diyabetin yüksek düzeyleri.
- **Ruh:** Antidepresan kullanımında artış, yalnızlık, düşük yaşam memnuniyeti.
- **Toplum:** Düşük genelleştirilmiş güven, zayıf sivil katılım, komşuluk ilişkilerinin zayıflaması.
- **Mekân:** Çok katlı konutun baskın hâle gelmesi, kişi başı yeşil alanın standartların altında kalması, otomobil sayısında hızlı artış, deprem riski taşıyan büyük bina stoku, megakentte (İstanbul) aşırı yığılma.
- **Ekonomi:** Konut fiyatı/gelir ve kira yükündeki sert artış, gençlerin ev sahibi olmasının zorlaşması, uzun çalışma ve ulaşım süreleri.

### 1.2 Ana soru

> Türkiye'nin şehir yapısı aile kurma, sağlıklı yaşama ve hür yurttaşlık üzerinde ne ölçüde belirleyicidir? Hangi mekânsal değişiklikler, hangi araçlarla, hangi maliyetle ve hangi sürede bu sonuçları iyileştirir?

### 1.3 Alt araştırma soruları

| Kod | Soru | İlgili iş paketi |
|---|---|---|
| AS1 | Türkiye'de il/ilçe/mahalle düzeyinde yapılı çevre özellikleri (kat, yoğunluk, yeşil, yürünebilirlik, araç bağımlılığı) ile aile, sağlık ve sosyal sermaye göstergeleri arasındaki ilişki nedir? | İP3, İP4 |
| AS2 | Uluslararası kanıt hangi mekanizmaları, hangi etki büyüklükleriyle destekliyor? | İP2 |
| AS3 | Türkiye'nin geleneksel yerleşim dokularının ölçüleri ve işleyişi nedir? Bunların hangi unsurları bugüne aktarılabilir? | İP5 |
| AS4 | Fıtrata uygun mahalle hangi sayısal parametrelerle tanımlanır? Aynı nüfusu deprem güvenliği, arazi ve maliyet kısıtları içinde barındırabilir mi? | İP6 |
| AS5 | Mevcut mevzuat ve teşvik yapısı hangi şehir biçimini üretiyor? Hangi değişiklikler gerekiyor? | İP8 |
| AS6 | Geçiş senaryolarının (yeni yerleşim, dönüşüm, mevcut dokunun onarımı) maliyeti, süresi ve beklenen etkileri nedir? | İP7, İP9 |
| AS7 | Ülke ölçeğinde nüfus şehirler arasında nasıl dağılmalı (megakent dengesi, orta ölçekli şehirler, kasaba-köy canlanması)? | İP4, İP7 |

---

## 2. Kavramsal çerçeve (özet)

Ayrıntısı: [01_KAVRAMSAL_CERCEVE/kavramsal_cerceve.md](../01_KAVRAMSAL_CERCEVE/kavramsal_cerceve.md)

Çerçeve **altı boyuttan** oluşuyor ve her boyut iki dilde ifade ediliyor:

| Boyut | Değer dili | Bilim dili |
|---|---|---|
| B1 Beden ve Can | Hıfz-ı nefs | Fiziksel sağlık, afet güvenliği |
| B2 Akıl ve Ruh | Hıfz-ı akl | Ruh sağlığı, çevre psikolojisi |
| B3 Nesil ve Aile | Hıfz-ı nesl | Demografi, çocuk gelişimi |
| B4 Mülk ve Geçim | Hıfz-ı mal | Konut ekonomisi, zaman bütçesi |
| B5 Topluluk, İnanç ve Hürriyet | Hıfz-ı din, hürriyet | Sosyal sermaye, yerindelik |
| B6 Mizan | Denge, israfsızlık | Ekoloji, iklim, kaynak verimliliği |

Bu boyutlar altı ölçekte (ev → sokak → mahalle → semt → şehir → ülke) ele alınıyor ve **Fıtrat Uyum Endeksi (FUE)** ile ölçülüyor. FUE yalnızca mekân göstergelerinden oluşuyor. İnsan sonuç göstergeleri endeksin geçerliliğini sınamak için ayrıca kullanılıyor.

---

## 3. İş paketleri

### İP0 — Yönetim ve yöntem
- **Amaç:** Planı, karar kayıtlarını, kalite ve kanıt standartlarını yönetmek.
- **Çıktılar:** Bu plan; `00_YONETIM/karar_kaydi.md`; kanıt derecelendirme kılavuzu (GRADE benzeri: güçlü / orta / zayıf / yalnızca kuram).

### İP1 — Kavramsal çerçeve ve gösterge seti
- **Amaç:** "Fıtrata uygun şehir"i ölçülebilir kılmak.
- **Yöntem:** Literatür + uzman görüşü; gösterge kartları (tanım, formül, veri, yön, ölçek); hipotez kümesi.
- **Çıktılar:** `kavramsal_cerceve.md` (v0.1 hazır), gösterge kartları, FUE yöntem notu.

### İP2 — Literatür ve kanıt tabanı
- **Amaç:** Yapılı çevre ile aile, sağlık, sosyal sermaye ve hürriyet arasındaki mekanizmaları ve etki büyüklüklerini çıkarmak; yerli düşünce geleneğini (İbn Haldun, Cansever, Osmanlı mahallesi) sistemli biçimde derlemek.
- **Yöntem:** Tematik derleme. Sonraki aşamada öncelikli sorular için PRISMA uyumlu sistematik derleme protokolü.
- **Çıktılar:** `literatur_haritasi.md`, `kaynakca.csv`, tema bazlı kanıt özetleri, okuma listesi.

### İP3 — Durum tespiti: veri ve istatistik
- **Amaç:** Türkiye'nin aile, sağlık, kentleşme, konut, ulaşım ve sosyal sermaye göstergelerini zaman serisi ve coğrafi kırılımla ortaya koymak.
- **Yöntem:** TÜİK, bakanlıklar, OECD, Eurostat, WVS verilerinin derlenmesi. 81 il (ve mümkünse 973 ilçe) için **panel veri seti**.
- **Çıktılar:** `turkiye_temel_gostergeler.csv/.md`, il paneli (`03_VERI/islenmis/il_paneli.csv`), grafik seti, durum tespiti raporu.

### İP4 — Mekânsal analiz ve haritalar
- **Amaç:** Türkiye ve pilot şehirlerde şehir biçimini ölçmek ve FUE'yi haritalamak.
- **Yöntem:** OSM + GHSL (yapılaşma ve bina yüksekliği) + WorldPop + Sentinel-2 + idari sınırlar. Python (OSMnx, GeoPandas, r5py), QGIS. Yürüme erişilebilirliği (15 dk izokronlar), yeşil alan erişimi, kavşak yoğunluğu, bina yüksekliği dağılımı, morfolojik tipoloji sınıflaması.
- **Çıktılar (haritalar):**
  1. Türkiye il düzeyi: doğurganlık, evlenme ve boşanma, obezite, kentleşme, konut tipi (koroplet)
  2. Türkiye yapılaşma ve bina yüksekliği ızgarası (GHSL)
  3. Pilot şehirlerde mahalle düzeyi FUE ve boyut haritaları
  4. 15 dakikalık erişim izokronları (okul, cami, sağlık, pazar, park)
  5. Yeşil alan erişim açığı haritası (WHO 300 m ölçütü)
  6. Deprem tehlikesi × bina stoku × nüfus yoğunluğu çakıştırması
  7. Ülke ölçeği şehir sistemi ve nüfus dağılımı (rank-size)

### İP5 — Geleneksel doku ve örnek vaka incelemeleri
- **Amaç:** İyi işleyen dokuların ölçülerini çıkarmak: yerli dokular (Safranbolu, Beypazarı, Cumalıkızık, Mardin, Birgi vb. ve tarihî İstanbul mahalleleri) ile uluslararası örnekler (Pontevedra, Barselona süper blokları, Vauban, Tokyo, Singapur HDB vb.).
- **Yöntem:** Uydu/OSM üzerinden morfolojik ölçüm (parsel, ada, sokak genişliği, kat, avlu); arşiv ve literatür.
- **Çıktılar:** `ornek_uygulamalar.md`; her doku için ölçülü plan ve kesit çizimi; karşılaştırma tablosu.

### İP6 — Model mahalle ve tasarım
- **Amaç:** Fıtrata uygun mahallenin sayısal programını, konut tipolojilerini ve tasarım kodunu üretmek.
- **Yöntem:** Parametrik tasarım. İlk aşamada Python ile SVG/DXF üretimi; ileride CAD/Rhino-Grasshopper.
- **Çıktılar:**
  - `tasarim_parametreleri.md`
  - **"Aynı yoğunluk, üç biçim"** çizimi (yüksek blok – kapalı site / bitişik nizam ada / az katlı avlulu doku)
  - Konut tipolojileri: büyüyebilen ev, çok kuşaklı ev, avlulu sıra ev, zemin + 3 karma bina
  - Model mahalle vaziyet planı, sokak kesitleri, donatı yerleşimi
  - **Fıtrat Kodu:** biçim temelli imar kodu taslağı (form-based code)
  - Deprem bölgesi için hızlı uygulanabilir sürüm

### İP7 — Simülasyonlar
Ayrıntı: Bölüm 4.
- **Çıktılar:** `06_SIMULASYON/` altında persona senaryoları, yaşam döngüsü modeli, erişilebilirlik ve karşılaşma modelleri, demografik senaryolar, kriz senaryoları; hepsi kodlu ve tekrarlanabilir.

### İP8 — Mevzuat, politika ve finansman
- **Amaç:** Bugünkü biçimi üreten hukuki ve mali teşvikleri çözümlemek ve değişiklik paketleri hazırlamak.
- **Kapsam:** İmar Kanunu ve yönetmelikleri (emsal, kat, çekme, otopark), Kat Mülkiyeti, kentsel dönüşüm (6306), belediye ve muhtarlık yetkileri, TOKİ ve Emlak Konut modeli, kat karşılığı inşaat ekonomisi, vergi ve tapu harçları, aile ve konut teşvikleri.
- **Çıktılar:** `mevzuat_politika_haritasi.md`; madde bazlı değişiklik önerileri; finansman modelleri (arsa payı, kooperatif, vakıf, aile konut kredisi); paydaş haritası; etki analizi.

### İP9 — Pilot ve uygulama yol haritası
- **Amaç:** Modeli üç farklı bağlamda uygulanabilir planlara dönüştürmek.
- **Önerilen pilot seti (karar bekliyor):**
  1. **Megakent dönüşümü:** İstanbul'da karşıtlık oluşturan iki ilçe (ör. yeni yoğun site bölgesi ile tarihî doku)
  2. **Orta ölçekli Anadolu şehri:** ör. Konya veya Kayseri (düz arazi, büyüme alanı, güçlü esnaf geleneği)
  3. **Deprem sonrası yeniden inşa:** ör. Antakya veya Kahramanmaraş (yeniden kurma fırsatı)
  4. **Referans geleneksel doku:** ör. Safranbolu veya Beypazarı
- **Çıktılar:** Pilot başına durum analizi, müdahale planı, maliyet tahmini, aşamalandırma, izleme göstergeleri.

### İP10 — Raporlama ve iletişim
- **Çıktılar:** Ara raporlar, nihai rapor (MD → PDF/DOCX), yönetici özeti, etkileşimli gösterge paneli, sunum, politika notları (karar vericiler için 2–4 sayfa).

---

## 4. Simülasyon tasarımı

Simülasyonlar **kehanet değil, düşünme aracıdır**. Her modelin varsayımları açık yazılır, parametreler literatürden alınır ve belirsizlik aralıklarıyla verilir.

### 4.1 Zihinsel simülasyonlar (nitel + yarı nicel)

**a) Persona "bir gün" simülasyonu.** Sekiz persona (genç bekâr, yeni evli çift, iki çocuklu aile, çok kuşaklı aile, yalnız yaşlı, engelli birey, esnaf, öğrenci) üç ortamda yaşatılır:

- (A) megakent sitesi (yüksek blok, kapalı site)
- (B) eski apartman mahallesi (1970–2000 yap-sat dokusu)
- (C) model mahalle

Ölçülenler: 24 saatlik zaman bütçesi, yürüme dakikası, araç kilometresi, dış mekân ve gün ışığı süresi, komşuyla karşılaşma sayısı, çocuğun bağımsız hareket alanı, cemaate ve ibadete erişim, aylık konut ve ulaşım maliyeti, deprem riski.

**b) Yaşam döngüsü simülasyonu (30 yıl).** Genç bir çiftin evlenme, ev edinme, çocuk sahibi olma, ebeveyn bakımı ve emeklilik yolu A/B/C ortamlarında izlenir. Maliyet, zaman, kuşaklar arası yakınlık ve mülkiyet karşılaştırılır.

**c) Kriz simülasyonları.** Deprem, salgın, ekonomik kriz ve sıcak dalgası karşısında mahallenin dayanıklılığı: tahliye, karşılıklı yardım, gıda ve su, yaşlılara erişim.

**d) Paydaş oyunu (politika simülasyonu).** "Konutta 4 kat sınırı + emsalin yeniden dağıtımı" gibi bir düzenleme uygulanırsa malik, müteahhit, belediye, banka, kiracı, genç çift ve muhtar nasıl tepki verir? Kim kazanır, kim kaybeder, hangi telafi mekanizması gerekir?

### 4.2 Hesaplamalı modeller

| Model | Soru | Araç | Girdi |
|---|---|---|---|
| M1 Erişilebilirlik | Nüfusun yüzde kaçı temel ihtiyaçlarına 15 dakikada yürüyerek ulaşıyor? | OSMnx, r5py, pandana | OSM, WorldPop |
| M2 Morfoloji ve yoğunluk | Aynı nüfusu hangi biçim kaç katla, ne kadar araziyle, ne kadar yeşille barındırır? | Python parametrik model | Tipoloji parametreleri |
| M3 Karşılaşma (ajan tabanlı) | Sokak ağı, yoğunluk ve zemin kat kullanımı komşular arası karşılaşmayı ve zayıf bağları nasıl etkiler? | Mesa / NetLogo | Morfoloji + zaman bütçesi |
| M4 Demografik senaryo | Konut maliyeti, konut tipi ve kuşaklar arası yakınlık değişirse doğurganlık ve evlilik nasıl değişir? | Mikro simülasyon / kohort-bileşen | TÜİK, literatür esneklikleri |
| M5 Deprem kaybı | Farklı yapılaşma biçimlerinde beklenen can ve mal kaybı ile toparlanma süresi | Senaryo modeli | AFAD tehlike, 2023 hasar verisi |
| M6 Konut ekonomisi | Kat karşılığı modelin alternatifleri (kooperatif, arsa payı, vakıf, aile kredisi) finansal olarak ayakta kalır mı? | Nakit akışı modeli | Maliyet ve fiyat verisi |
| M7 Ülke sistemi | Nüfusun megakentten orta ölçekli şehirlere dağılımı senaryoları | Sistem dinamiği | ADNKS göç verisi |

---

## 5. Yöntem ilkeleri ve kalite standartları

1. **Kaynak hiyerarşisi:** Birincil resmî veri ve hakemli meta-analiz → hakemli tekil çalışma → kurum raporu → basın. Her sayının yılı ve URL'si olur.
2. **Kanıt derecelendirmesi:** Her önerme *güçlü / orta / zayıf / kuramsal* olarak işaretlenir; nedensel kanıt ile korelasyonel kanıt ayrılır.
3. **Karıştırıcı etkenler:** Gelir, eğitim (özellikle kadın eğitimi), yaş yapısı, göç, kültürel/dinî eğilim ve bölgesel farklar analizlerde kontrol edilir. Türkiye'de doğurganlığın doğu-batı farkı, mekân etkisini kültürel etkiden ayırmayı zorunlu kılar.
4. **Karşı kanıta açıklık:** Yoğunluğun ve yüksek yapılaşmanın faydalarını savunan literatür (verimlilik, toplu taşıma, arazi tasarrufu) ciddiyetle ele alınır.
5. **Tekrarlanabilirlik:** Tüm analiz kodları `05_ANALIZ/` ve `06_SIMULASYON/` altında, ham veri `03_VERI/ham/` altında saklanır.
6. **Etik ve hürriyet:** Mahalle düzeyi verilerde kişisel veri gizliliği korunur. Önerilen dönüşümler zorlayıcı, mülksüzleştirici veya soylulaştırıcı olamaz; gönüllülük, hakkaniyet ve katılım esastır. Kadınların, çocukların, yaşlıların ve engellilerin erişimi her tasarım kararında ayrıca sınanır.

---

## 6. Fazlar ve yol haritası

| Faz | İçerik | Ana çıktılar |
|---|---|---|
| **Faz 1 — Temel** | Çerçeve, literatür haritası, durum tespiti, veri kataloğu, mevzuat haritası | Bu plan, kavramsal çerçeve, 4 temel derleme, durum tespiti özeti |
| **Faz 2 — Ölçüm** | İl paneli, Türkiye haritaları, pilot seçimi, pilot şehirlerin mekânsal analizi, FUE v1 | Veri paneli, harita seti, FUE haritaları, ilk istatistiksel analizler |
| **Faz 3 — Model** | Geleneksel doku ölçümleri, tasarım parametreleri, tipolojiler, model mahalle, teknik çizimler | "Aynı yoğunluk, üç biçim", model mahalle planı, Fıtrat Kodu taslağı |
| **Faz 4 — Sistemler ve ölçek** | Kentsel stres, konut, malzeme, ulusal mekânsal çerçeve, enerji, israf, gelir-vergi-ticaret, kademe modeli, toplum hedefleri (27.10.2026'da kullanıcı talebiyle yeniden kapsamlandı) | Rapor 14–22, `toplum_hedefleri.md` |
| **Faz 5 — Simülasyon, politika ve pilot** | Paydaş simülasyonu v2, politika paketi v2, deprem pilotları, finansman, izleme sistemi | Politika notları, pilot planları, nihai rapor, gösterge paneli |

---

## 7. Riskler

| Risk | Etki | Önlem |
|---|---|---|
| İdeolojik algılanma (çalışmanın tek bir dünya görüşünün savunusu sanılması) | Teknik ve akademik kamuoyunun ilgisini kaybetmek | İki dilli çerçeve; her önermenin bilimsel kanıtla desteklenmesi |
| Nedensellik hatası | Yanlış politika | Karıştırıcı kontrolü, doğal deney arayışı, kanıt derecelendirmesi |
| İlçe/mahalle düzeyi veri eksikliği | Analizin il düzeyinde kalması | Açık mekânsal veri (OSM, GHSL), vekil göstergeler, gerekirse saha anketi |
| Ekonomik uygulanabilirlik (az katlı = daha az inşaat alanı = müteahhit ve malik direnci) | Önerilerin uygulanamaması | M6 konut ekonomisi modeli, telafi mekanizmaları, kademeli geçiş |
| Deprem güvenliği önceliğiyle çatışma | Hızlı ve yüksek yapılaşma baskısı | Az katlı ve hızlı uygulanabilir tipolojiler, deprem bölgesi sürümü |
| Kapsam şişmesi | Çıktı üretilememesi | Faz bazlı ilerleme, pilotlara odaklanma |

---

## 8. Karar bekleyen konular

1. **Pilot şehirler:** Bölüm 3, İP9'daki öneri seti onaylanacak mı?
2. **Hedef kitle önceliği:** Merkezî yönetim, belediyeler, akademi ve kamuoyu arasında öncelik sırası (dil ve format buna göre ayarlanacak).
3. **Çerçeve dili:** İki dilli yaklaşım uygun mu, yoksa ağırlık değer diline mi bilim diline mi verilmeli?
4. **Çıktı formatı:** Yerel dosyalar (MD/CSV/PNG/SVG) + gerektiğinde PDF/DOCX + çevrim içi gösterge paneli.

---

## 9. Faz 1 durum kaydı

| Çıktı | Dosya | Durum |
|---|---|---|
| Klasör yapısı ve README | `README.md` | ✅ |
| Kavramsal çerçeve v0.1 | `01_KAVRAMSAL_CERCEVE/kavramsal_cerceve.md` | ✅ |
| Ana plan v0.1 | `00_YONETIM/ana_arastirma_plani.md` | ✅ |
| Türkiye temel göstergeler (449 satır) | `03_VERI/turkiye_temel_gostergeler.md`, `03_VERI/islenmis/turkiye_temel_gostergeler.csv` | ✅ |
| Literatür haritası ve kaynakça (131 kaynak) | `02_LITERATUR/literatur_haritasi.md`, `02_LITERATUR/kaynakca.csv` | ✅ |
| Örnek uygulamalar | `02_LITERATUR/ornek_uygulamalar.md` | ✅ |
| Tasarım parametreleri ve taslak mahalle programı | `07_TASARIM_CIZIM/tasarim_parametreleri.md` | ✅ |
| "Aynı yoğunluk, üç biçim" çizimi | `07_TASARIM_CIZIM/ayni_yogunluk_uc_bicim.png` (kod: `kod/`) | ✅ |
| Mevzuat ve politika haritası | `08_MEVZUAT_POLITIKA/mevzuat_politika_haritasi.md` | ✅ |
| Veri kaynakları kataloğu | `03_VERI/veri_kaynaklari_katalogu.md` | ✅ |
| Durum tespiti grafik seti | `05_ANALIZ/grafikler/durum_tespiti_grafik_seti.png` (kod: `05_ANALIZ/kod/`) | ✅ |
| Durum tespiti sentez raporu | `09_RAPORLAR/01_durum_tespiti_ozet.md` | ✅ |
| Açık doğrulamalar | TAYA 2021, SBB deprem raporu, TCMB konut fiyat endeksi, MPYY EK-2 ve Otopark Ek-1 tabloları, RG künyeleri | ⏳ |

## 10. Faz 2 durum kaydı

| Çıktı | Dosya | Durum |
|---|---|---|
| 81 il paneli (TÜİK, 75 değişken, doğrulanmış) | `03_VERI/ham/tuik/il_paneli_ham_2025.csv`, `03_VERI/islenmis/il_paneli_2025.csv` / `.gpkg` | ✅ |
| İl analizi: mekânın payı (Shapley, eğitim-içi, il-içi, sağlamlık, Moran's I) | `05_ANALIZ/kod/il_paneli_analiz.py`, `05_ANALIZ/sonuclar/` | ✅ |
| Türkiye il haritaları (9 harita) | `04_HARITA/il_haritalari_2025.png` | ✅ |
| Rapor: 81 il paneli, mekânın payı | `09_RAPORLAR/02_il_paneli_mekanin_payi.md` | ✅ |
| İlçe paneli (973 ilçe; doğum, yaş-cinsiyet, kadın eğitimi, GHSL yükseklik; doğrulanmış) | `03_VERI/islenmis/ilce_paneli_analiz.csv` / `ilce_paneli.gpkg`, `03_VERI/kod/` | ✅ |
| İlçe analizi: il sabit etkisi, Shapley, sınıflar, sağlamlık, SLX, Moran's I | `05_ANALIZ/kod/ilce_paneli_analiz.py`, `05_ANALIZ/sonuclar/ilce_*.csv` | ✅ |
| İlçe haritaları ve İstanbul haritası | `04_HARITA/ilce_haritalari_2025.png`, `04_HARITA/istanbul_ilce_2025.png` | ✅ |
| Rapor: 973 ilçe, il içi mekân etkisi | `09_RAPORLAR/03_ilce_paneli_il_ici.md` | ✅ |
| İlçe sonuçları: ölüm oranı (SMR), hane tipi, medeni durum, evlenme ve boşanma (MEDAS + SDMX; doğrulanmış) | `03_VERI/islenmis/ilce_olum_nufus.csv`, `ilce_hane_medeni.csv`, `ilce_evlenme_bosanma.csv` | ✅ |
| OSM: park erişimi (300 m), kavşak yoğunluğu, cami ve okul noktaları | `03_VERI/kod/osm_ilce.py`, `03_VERI/islenmis/ilce_osm.csv` | ✅ |
| Rapor: mekânın doğurganlık dışındaki sonuçları | `09_RAPORLAR/07_ilce_diger_sonuclar.md` | ✅ |
| Pilot seçimi (10 ilçe, veriye dayalı) | `09_RAPORLAR/08_pilot_secimi.md`, `04_HARITA/pilot_ilceler.png` | ✅ kullanıcı onayladı (26.10.2026) |
| H2 konut maliyeti (TCMB EVDS3 il fiyat ve kira + TÜİK SDMX; 81 il × 2005–2025) | `09_RAPORLAR/04_konut_maliyeti_h2.md`, `05_ANALIZ/kod/konut_h2_*.py` | ✅ il ölçeğinde desteklenmedi |
| İP7 zihinsel simülasyonlar v1 (8 persona × 3 ortam, 30 yıllık yaşam döngüsü, kriz senaryoları) | `09_RAPORLAR/05_zihinsel_simulasyonlar.md`, `06_SIMULASYON/` | ✅ (paydaş oyunu v2'ye) |
| İP6 model mahalle v1 (vaziyet planı + DXF, erişim analizi, kesitler, 4 tipoloji, deprem şeması) ve Fıtrat Kodu taslağı | `07_TASARIM_CIZIM/model_mahalle_v1.md`, `07_TASARIM_CIZIM/model_mahalle/`, `07_TASARIM_CIZIM/fitrat_kodu_taslak.md` | ✅ v2 düzeltmeleri listelendi |
| İP8 mevzuat değişiklik paketi (28 öneri), M6 finansman modeli, 3 politika notu | `09_RAPORLAR/06_politika_paketi_ozet.md`, `08_MEVZUAT_POLITIKA/` | ✅ bazı künyeler doğrulama bekliyor |
| **Faz 2 sentezi ve güncellenmiş çalışma tezi** | `09_RAPORLAR/09_faz2_sentez.md` | ✅ |
| Mikro veri başvuruları (TÜİK Gelir ve Yaşam Koşulları, Hacettepe Türkiye Nüfus ve Sağlık Araştırması) | — | ⏳ kullanıcı kararı |
| Pilot şehir seçimi ve mahalle düzeyi Fıtrat Uyum Endeksi | → Faz 3 (§11) | ✅ |

## 11. Faz 3 durum kaydı

| Çıktı | Dosya | Durum |
|---|---|---|
| Mahalle nüfusu 2025, 10 pilot ilçe, 658 mahalle (MEDAS; ilçe toplamlarıyla doğrulanmış) | `03_VERI/islenmis/pilot_mahalle_nufus_2025.csv`, `03_VERI/ham/tuik/mahalle_kaynaklar.md` | ✅ |
| OSM tek geçiş: Türkiye geneli mahalle/köy sınırları, 302 bin donatı noktası, ana yollar; pilotlarda yaya ağı ve binalar | `03_VERI/kod/osm_pilot_mahalle.py`, `03_VERI/islenmis/pilot_osm/` | ✅ |
| TKGM kadastro mahalle sınırları (10 ilçe, 810 mahalle) | `03_VERI/kod/tkgm_mahalle.py`, `03_VERI/islenmis/pilot_mahalle_tkgm.gpkg` | ✅ |
| Mahalle düzeyi FUE: 654 mahallede sınır, 300 kentsel mahalle, 18 gösterge, yaya ağı mesafeleri, E ve Ç alt endeksleri | `05_ANALIZ/kod/fue_mahalle.py`, `03_VERI/islenmis/pilot_mahalleler.gpkg`, `05_ANALIZ/sonuclar/fue_*.csv` | ✅ |
| FUE geçerlilik sınaması: 973 ilçede FUE-lite, il içi; Faz 2 yükseklik–ölümlülük bulgusunun yeniden sınanması | `05_ANALIZ/kod/fue_ilce_gecerlilik.py`, `03_VERI/islenmis/ilce_fue_lite.csv` | ✅ Ç doğrulandı, E ters yönde; yükseklik etkisi yarıya indi |
| FUE haritaları ve grafikleri | `04_HARITA/fue_*.png`, `05_ANALIZ/grafikler/fue_*.png` | ✅ |
| Rapor: mahalle düzeyinde FUE | `09_RAPORLAR/10_fue_mahalle.md` | ✅ |

| Geleneksel doku morfolojisi: 7 geleneksel + 6 çağdaş alan + model v1, 600 × 600 m, ≈50 ölçüt; OSM + Microsoft ayak izleri + GHSL | `03_VERI/kod/morfoloji_olcum.py`, `05_ANALIZ/sonuclar/morfoloji_karsilastirma.csv`, `04_HARITA/morfoloji/` | ✅ yeniden üretim birebir |
| Rapor: geleneksel doku morfolojisi ve kalibrasyon önerileri | `09_RAPORLAR/11_geleneksel_doku_morfolojisi.md` | ✅ |
| Model mahalle v2: iki ilkokul (%100 ≤ 500 m), asansör kuralı, EK-2 dengesi, S2 H/W 0,72, ağaç örtüsü %31 | `07_TASARIM_CIZIM/model_mahalle_v2.md`, `07_TASARIM_CIZIM/model_mahalle_v2/`, `07_TASARIM_CIZIM/fitrat_kodu_taslak_v2.md` | ✅ yeniden üretim birebir |
| Model mahallenin FUE v0.2 konumu (E 82, Ç 63) | `05_ANALIZ/kod/fue_model_mahalle.py`, `05_ANALIZ/sonuclar/fue_model_mahalle.csv` | ✅ |
| Model mahalle v2.1: morfoloji kalibrasyonu (ada ortası geçit, kapalı T3 avlusu, S2 H/W 0,78, kavşak 303/km²) | `07_TASARIM_CIZIM/model_mahalle_v2.md` §3.5, `model_mahalle_v2/figur_zemin_v2_1.png`, `fitrat_kodu_taslak_v2.md` (0.2.1) | ✅ yeniden üretim birebir; FUE E 82, Ç 63 |
| **Faz 3 sentezi ve güncellenmiş çalışma tezi** | `09_RAPORLAR/12_faz3_sentez.md` | ✅ |
| Kurum verisi talepleri (MEB, Diyanet, Sağlık, GTFS), saha anketi ortaklığı | — | ⏳ kullanıcı kararı |
| Uydu çevre katmanları: WorldCover 10 m, ACAG PM2.5 0,01°, Landsat 8/9 yüzey sıcaklığı (pilot, 30 m), MODIS (ulusal, 1 km) | `03_VERI/kod/uydu_pilot.py`, `uydu_ulusal.py`, `03_VERI/ham/uydu_kaynaklar.md`, `03_VERI/islenmis/ilce_uydu.csv` | ✅ kullanıcı onayıyla (CAMS hesap gerektirdiği için ACAG) |
| FUE v0.2: Ç eksenine 4 uydu göstergesi; ulusal sınama, aracılık testi, yükseklik bulgusunun üçüncü sınaması | `05_ANALIZ/kod/fue_mahalle.py`, `fue_ilce_gecerlilik.py`, `05_ANALIZ/sonuclar/fue_ilce_cevre_kontrol.csv` | ✅ Ç v0.2 ölümlülükte −0,41; yükseklik etkisi anlamsızlaştı |
| Rapor: uydu verisiyle çevre-ölçek ekseni | `09_RAPORLAR/13_fue_uydu_cevre.md`, `04_HARITA/uydu_ciftler.png`, `05_ANALIZ/grafikler/fue_v02_*.png` | ✅ |
| GitHub deposu (herkese açık; kod MIT, içerik CC BY 4.0) | `github.com/Huseyincansagir/tr-tamirat` | ✅ |

## 12. Faz 4 durum kaydı

Kapsam 27.10.2026'da kullanıcının talebiyle belirlendi: stres, konut, malzeme, ulusal altyapı, enerji, israf, gelir ve vergi adaleti, ticaret, ölçeklenebilir şehir. Yedi paket ayrı ajanlarla (en fazla ikisi aynı anda) hazırlandı. Her paketin betikleri bağımsız olarak yeniden çalıştırıldı ve sonuç tablolarının md5 değerleri karşılaştırıldı.

| Çıktı | Dosya | Durum |
|---|---|---|
| Toplum hedefleri: 29 gösterge, bugün, 2050 hedefi, mekânın payı | `01_KAVRAMSAL_CERCEVE/toplum_hedefleri.md` | ✅ |
| Kentsel stres: literatür (76 kaynak doğrulandı), ilçe stres yükü endeksi, sınama | `09_RAPORLAR/14_kentsel_stres.md`, `02_LITERATUR/stres_literatur.md`, `05_ANALIZ/kod/stres_*.py` | ✅ 9/9 tablo birebir; endeks Ç v0.2 ile örtüşüyor (ρ −0,91) |
| Fıtrata uygun konut: 17 ilke, 5 tip ve referans daire, A1 paftalar | `09_RAPORLAR/15_fitrata_uygun_konut.md`, `07_TASARIM_CIZIM/konut_rehberi/` | ✅ 4/4 tablo birebir |
| Doğal ve geri dönüştürülmüş malzemeler: maliyet, karbon, sağlık, deprem; kamu yapıları | `09_RAPORLAR/16_dogal_ve_geri_donusturulmus_malzemeler.md`, `07_TASARIM_CIZIM/malzeme/` | ✅ 26/26 tablo birebir; taşıyıcı toprak için standart boşluğu |
| Ulusal mekânsal çerçeve: ulaşım, enerji, sanayi, kısıtlar, 1 km ızgara, şema | `09_RAPORLAR/17_ulusal_mekansal_cerceve.md`, `05_ANALIZ/kod/ulusal_plan_*.py`, `04_HARITA/ulusal_plan/` | ✅ 21/21 tablo birebir |
| Enerji: mahalle, şehir, bölge dengesi; 2050 senaryoları; SMR | `09_RAPORLAR/18_enerji.md`, `05_ANALIZ/kod/enerji_*.py` | ✅ 27/27 tablo birebir |
| İsraf, fire, kaçak: gıda, su, enerji, malzeme, arazi | `09_RAPORLAR/19_israf_fire_kacak.md`, `05_ANALIZ/kod/israf_*.py` | ✅ 11/11 tablo birebir |
| Gelir, vergi, ticaret: dağılım, etkin vergi oranları, ticaret engelleri, yeterlilik | `09_RAPORLAR/20_ekonomi_gelir_vergi_ticaret.md`, `05_ANALIZ/kod/ekonomi_*.py` | ✅ 39/39 tablo birebir; mikro veri yok, dilim hesapları vekil |
| Ölçeklenebilir şehir: beş kademe, donatı merdiveni, altyapı ve ekonomi araçları | `09_RAPORLAR/21_olceklenebilir_sehir.md`, `07_TASARIM_CIZIM/olceklenebilir_sehir/` | ✅ |
| **Faz 4 sentezi ve güncellenmiş çalışma tezi** | `09_RAPORLAR/22_faz4_sentez.md` | ✅ |
| Toprak yapı standardı önerisi, pilot uygulama yeri, mikro veri başvuruları | — | ⏳ kullanıcı kararı |

## 13. Faz 5 durum kaydı

| Çıktı | Dosya | Durum |
|---|---|---|
| Politika paketi v2: arsa değer vergisi (E1–E5), karma kullanım (P6, O4, M5, I5, R1), semt meclisi (B3, B4); sermaye geliri (S1–S3), asgari ve taban gelir (A1–A3), esnaf ve rekabet (C1–C4), gıda zinciri (Y1–Y2); I3, K2, B1 genişletildi; toplam 52 öneri | `08_MEVZUAT_POLITIKA/degisiklik_paketi_v2.md` | ✅ künyeler mevzuat.gov.tr'den doğrulandı (Anayasa md. 73 dahil); Kent Konseyi Yön. kısmen |
| Mali etki: arsa değer vergisi geçişi 2029–2033, KDV %20 → %16,8 (bütçe-nötr), yerel kaynak, otopark yükü | `08_MEVZUAT_POLITIKA/politika_v2/politika_v2_mali.py`, 5 CSV, 1 grafik | ✅ Rapor 20 çıktıları birebir korunuyor |
| Rapor: politika paketi v2 | `09_RAPORLAR/23_politika_paketi_v2.md` | ✅ |
| Araştırma notu: Rapor 20'nin pakete girmeyen seçenekleri (vergi istisnaları, taban gelirler, sade rejim, giriş kotaları, pazar ve hal, tarımsal planlama); 12 aday öneri | `08_MEVZUAT_POLITIKA/arastirma_diger_secenekler.md` | ✅ 15 kanunda madde doğrulandı; 12 aday kullanıcı kararıyla pakete alındı (S, A, C, Y) |
| Paydaş oyunu (§4.1-d, ilk sürüm): 12 paydaş × 8 öneri grubu, hane ve kurum etkileri, destek endeksi, paketleme ve telafi senaryoları | `06_SIMULASYON/kod/paydas_oyunu.py`, `06_SIMULASYON/sonuclar/paydas_*.csv`, `09_RAPORLAR/24_paydas_oyunu.md` | ✅ tutumlar varsayım; görüşmelerle sınanmalı. Bulgu: belediyeye %10 telafi (mahsup %90) direnci kaldırıyor; paket v2'ye işlendi (E4–E5, KDV 2033'te %17,1, merkez nötr) |
| İlçe ana tablosu (973 × 186; 250 m ızgaradan fay, taşkın, eğim, erişim) ve önlenebilir ölüm karşı-olgusu | `05_ANALIZ/kod/ilce_ana_tablo.py`, `03_VERI/islenmis/ilce_ana_tablo.csv`, `09_RAPORLAR/25_ilce_ana_tablo_onlenebilir_olum.md` | ✅ Ç en kötü çeyrek → medyan: 10–17 bin ölüm/yıl; PM2.5 ≤ 10: literatür 43 bin, ekolojik 33–53 bin (örtüşüyor) |
| İlçe zaman paneli 2014–2025 (öneri B): yıllık ilçe nüfusu MEDAS'tan; doğum ve evlenme hızı × kentsel biçim; uzun fark, yıl katsayıları, varyans ayrıştırması | `05_ANALIZ/kod/ilce_zaman_paneli.py`, `03_VERI/islenmis/ilce_nufus_2014_2025.csv`, `09_RAPORLAR/26_ilce_zaman_paneli.md` | ✅ Doğum hızı düşüşü (−%40) ortak: il SE %67, biçim %0,4; yükseklik → doğum ≈ 0; evlenmede küçük ve salgına bağlı iz |
| Deprem olay çalışması (öneri C): USGS ShakeMap MMI (kullanıcı onayıyla), şiddet grupları, ön eğilimden arındırma, bina yüksekliği farkı, pilot ilçeler | `05_ANALIZ/kod/deprem_olay.py`, `03_VERI/islenmis/ilce_deprem_siddet.csv`, `09_RAPORLAR/27_deprem_olay_calismasi.md` | ✅ MMI ≥ 8: nüfus −%13 kalıcı (≈ 170 bin), doğum sayısı −%15, kişi başı doğum hızı değişmedi; aynı il ve şiddette +1 kat ≈ +%4–5 nüfus kaybı (46 ilçe, kesin değil); Antakya −%24 |
| Evin biçimi ↔ inovasyon, üretkenlik, sağlık, güven, aile: 81 il × 21 sonuç × 7 konut değişkeni (BH q, dört duyarlılık), 973 ilçede il içi yükseklik; TÜRKPATENT patent ve faydalı model (kullanıcı onayıyla), TOBB şirket kuruluşu; literatür taraması | `05_ANALIZ/kod/konut_bicimi_iliskiler.py`, `03_VERI/islenmis/il_konut_bicimi_tablosu.csv`, `02_LITERATUR/konut_bicimi_literatur.md`, `09_RAPORLAR/28_konut_bicimi_iliskiler.md` | ✅ Yükseklik → inovasyon ilişkisi eğitim ve ölçekle kayboluyor (+0,43 → +0,17, anlamsız); 3–4 kat sosyal hayat, güvenlik duygusu ve katılımla olumlu (q 0,03); konut başına oda intiharla −0,45 (q < 0,001); ev sahipliği güvenlik ve katılımla olumlu; il içinde +3,1 m → ölüm +%2,1, TDH −0,044. Literatür: 58 kaynak (47 [D], 11 [K]); yoğunluk ve yakınlık verimlilikte güçlü artı ama yürüme ölçeğinde, ev sahipliğinin nedensel etkisi küçük. Ekolojik, nedensellik için mikro veri gerekiyor |
| Donatı açığı haritası (D), genel doğurganlık hızıyla panel | — | ⏳ ana tablo ve ilçe nüfus serisine dayanır |
| Deprem pilotları, gece ısısı ve gürültü, izleme paneli | — | ⏳ Faz 5 gündemi (Rapor 22 §3) |

