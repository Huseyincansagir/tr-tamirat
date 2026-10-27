# Faz 5 · Rapor 1 — Mevzuat, Politika ve Finansman Paketi (İP8, sürüm 1)

*26 Ekim 2026 · Sürüm 0.1*

| Ne | Nerede |
|---|---|
| Değişiklik paketi (28 öneri, taslak madde dili, künyeler) | [08_MEVZUAT_POLITIKA/degisiklik_paketi_v1.md](../08_MEVZUAT_POLITIKA/degisiklik_paketi_v1.md) |
| Finansman modeli M6 (kod, 8 CSV, 2 grafik) | [08_MEVZUAT_POLITIKA/finansman_modeli/](../08_MEVZUAT_POLITIKA/finansman_modeli/) · `m6_konut_ekonomisi.py` |
| Grafikler | [grafik1_kirilma_emsali.png](../08_MEVZUAT_POLITIKA/finansman_modeli/grafik1_kirilma_emsali.png) · [grafik2_telafi_koprusu.png](../08_MEVZUAT_POLITIKA/finansman_modeli/grafik2_telafi_koprusu.png) |
| Politika notları | [(a) aile ve nüfus etki ölçütleri](../08_MEVZUAT_POLITIKA/politika_notlari/a_aile_nufus_etki_imar_olcutleri.md) · [(b) mahalle yönetişimi](../08_MEVZUAT_POLITIKA/politika_notlari/b_mahalle_yonetisim_birimi.md) · [(c) deprem bölgesinde az katlı yeniden inşa](../08_MEVZUAT_POLITIKA/politika_notlari/c_deprem_bolgesi_az_katli_yeniden_insa.md) |
| Önceki mevzuat analizi | [08_MEVZUAT_POLITIKA/mevzuat_politika_haritasi.md](../08_MEVZUAT_POLITIKA/mevzuat_politika_haritasi.md) |
| **Sürüm 2** (arsa değer vergisi, karma kullanım, semt meclisi ve Rapor 20'nin diğer seçenekleri; 52 öneri) | [Rapor 23](23_politika_paketi_v2.md) · [degisiklik_paketi_v2.md](../08_MEVZUAT_POLITIKA/degisiklik_paketi_v2.md) |

---

## Özet

**Soru:** Bugünkü şehir biçimini üreten kurallar ve para akışı nasıl değiştirilebilir ki aile ölçekli, az katlı, avlulu mahalle zorlamadan, kendi ayakları üzerinde durabilsin?

**Kısa cevap:** Mevcut kurallar az katlı seçeneği yasaklamıyor, ama **pahalılaştırıyor ve görünmez kılıyor**. Değişikliklerin çoğu yönetmelik düzeyinde ve 2027 içinde yapılabilir. Finansman modeli, aynı arsada az katlı seçeneğin yaygın plan emsallerinde zaten rekabetçi olduğunu, yüksek fiyatlı kentlerde ise düşük maliyetli birkaç telafi aracıyla rekabetçi kalabildiğini gösteriyor.

1. **Gerekçe yeniden kuruldu.** Faz 2'ye göre mekânın doğurganlığa doğrudan etkisi küçük: kadın eğitimi sabitken bir kat başına ≈−0,03 çocuk; il içi açıklanan farkın %76'sı eğitime, %19–22'si mekâna düşüyor. Paket mekânı **sağlık, çocuk gelişimi, komşuluk, kuşaklar arası yakınlık ve deprem güvenliği** gerekçesiyle savunuyor. Doğurganlık için konut erişimi, eğitim-aile uyumu ve iş-aile dengesi araçlarını birlikte öneriyor.
2. **Mevzuatta beş kritik bulgu** (mevzuat.gov.tr'den 26.10.2026'da doğrulandı):
   - Otopark Yönetmeliği 120 m²'yi aşan aile dairesinin otopark yükünü iki katına çıkarıyor.
   - 3194 Ek md. 8, 6306 alanlarını ve riskli yapı parsellerini değer artış payı ile yoğunluk kurallarının dışında tutuyor. Bu, dikey dönüşümün gizli teşviki.
   - İmar hakkı aktarımı 7534 sayılı Kanunla (RG 12.12.2024) 3194 md. 13'e girdi, ama yalnız kamuya geçen parseller için.
   - MPYY md. 12'deki yürüme mesafeleri "planlanabilir" diye yazılmış; bağlayıcı değil.
   - MPYY EK-2'nin güncel değerleri (ilkokul ve ortaokul 2,0 m²/kişi) projenin tasarım tablosundaki eski aktarımdan yüksek.
3. **Finansman modeli (M6):** Aynı 1 ha'da avlulu Z+2 sıra ev, Türkiye ortalama fiyatında arsa sahibine **100,9 milyon TL**, 12 katlı blok **2,9 milyon TL** bırakıyor. Blok ancak satış fiyatı 53.000 TL/m²'yi aşınca ve plan emsali 2,6'nın üzerindeyse öne geçiyor. Otopark reformu, harç indirimi, hızlı onay ve emsal transferiyle İstanbul fiyatında bu eşik **3,99**'a çıkıyor.
4. **Deprem bölgesi:** Düşük fiyatlı bölgelerde kat karşılığı hiçbir emsalde çalışmıyor; kamu zaten finansör. Kamu için az katlı yapım, konut başına %19–29 daha ucuz.
5. **Aileye erişim:** 124 m²'lik bir aile konutu piyasa kredisiyle medyan aile gelirinin %182'si kadar taksit gerektiriyor. Endeksli aile konut kredisi ve kooperatif ya da arsa vakfıyla bu oran %22–26'ya iniyor. Kamu maliyeti TOKİ tipi sabit taksitin yaklaşık dörtte biri.

**Proje için anlamı:** "Yatay mimari" söyleminin bağlayıcı karşılığı birkaç somut maddede kurulabilir: PAİY md. 23, Otopark Yönetmeliği Ek-1, MPYY md. 12 ve 3194 md. 13. Hiçbiri mülkiyet hakkını kısmayı ya da zorlayıcı dönüşümü gerektirmiyor. En hızlı giriş kapısı, Genelge 2026/4 kapsamında aile ve nüfus etki değerlendirmesine eklenecek 24 imar ölçütü.

---

## 1. Paket

### 1.1 İlkeler

1. **Varsayılanı değiştir, zorlama.** Az katlı, avlulu ve aile ölçekli seçenek kolaylaştırılır ve ucuzlatılır; mevcut imar hakları kısılmaz.
2. **Karşılıksız kısıtlama yok.** Daha az kat seçen malikin kullanmadığı hakkı devredilebilir (imar hakkı aktarımı).
3. **Kanıt düzeyi açık.** Her önerinin gerekçesi güçlü, orta, zayıf ya da normatif olarak işaretli.

### 1.2 En önemli on değişiklik

| # | Değişiklik | Mevzuat | Araç | Ne değişir? |
|---|---|---|---|---|
| 1 | **Aile ve nüfus etki değerlendirmesi için 24 imar ölçütü** (5'i kritik: ilkokula yürüme, kreş, yeşil erişim, zemin etüdü, yerinden edilme süresi) | Genelge 2026/4 md. 2, 9; 3194 Ek md. 8 raporu | Yönetmelik | Yoğunluk artışları ve dönüşüm projeleri aile etkisi açısından gerekçelendirilir |
| 2 | **Otopark ihtiyacı daire büyüklüğüne değil haneye bağlanır** (0,5/hane); plan kararıyla bölgesel otopark ve azami otopark | Otopark Yön. Ek-1, md. 4, 8 | Yönetmelik | Aile dairesinin otopark yükü yarıya iner (1 ha'da 43,8 → 21,9 milyon TL) |
| 3 | **"Aile dostu ada düzeni":** ön bahçe 0–3 m, bitişik nizam, ada içi ortak avlu, en fazla zemin + 3 kat | PAİY md. 4, 23 | Yönetmelik | Az katlı yoğun doku hazır ve denetlenebilir bir seçenek olur |
| 4 | **Yürüme mesafeleri bağlayıcı ve yaya ağıyla ölçülür;** ilkokul güzergâhı hızlı yolu ışıksız kesemez | MPYY md. 12 | Yönetmelik | Çocuğun okula yürüyebileceği plan |
| 5 | **Yeşil erişim standardı:** her konuta 300 m yaya ağı içinde ≥0,5 ha park | MPYY md. 12 (yeni fıkra) | Yönetmelik | Metrekare standardı erişim standardına dönüşür |
| 6 | **Çocuk donatısı yaş yapısına göre hesaplanır;** 6306 planlarında standart isteğe bağlı olmaktan çıkar | MPYY md. 11, EK-2 Not 11 | Yönetmelik | Genç ailelerin yoğun olduğu alanlarda okul ve oyun alanı açığı önlenir |
| 7 | **Gönüllü kat sınırlaması karşılığında imar hakkı aktarımı** | 3194 md. 13 | Kanun | Az katlı seçen malik hakkını kaybetmez; yoğunluk toplu taşıma koridoruna kayar |
| 8 | **6306 ve riskli yapı istisnasında 1:1 yeniden yapımı aşan emsale değer artış payı;** az katlı ada dönüşümünde muafiyet | 3194 Ek md. 8 son fıkra | Kanun | Dikey dönüşümün gizli teşviki nötrleşir |
| 9 | **TOKİ tip kataloğu:** %30 3+1, %10 4+1 ya da çok kuşaklı, büyüyebilen konut, az katlı avlulu ada, kuşak yakınlığı puanı | 2985 md. 4; idari karar | İdari | Kamu konutu aile ölçeğine gelir |
| 10 | **Mahalle meclisi ve katılımcı mahalle bütçesi pilotu** | 5393 md. 9, 13, 18, 77 | Belediye meclisi kararı | Mahalle plan ve bütçe kararlarında söz sahibi olur |

Diğer 18 öneri (ortak komşuluk odası, asansör, daire karması, otopark bedelinin kullanımı, 6306'da azınlık malik güvencesi, harç muafiyeti, 634 sayılı Kanunda ortak avlu ve meskende küçük gündüz bakımevi, tapu harcı, aile konut kredisi, kooperatif ve arsa vakfı) değişiklik paketinde.

### 1.3 Ölçütler neden doğurganlığı ölçmüyor?

| Faz 2 bulgusu | Değer |
|---|---|
| İller arası doğurganlık farkında mekânın payı | %13; 12 bölge sabit etkisiyle %5 |
| İl içinde bir kat (≈3 m) daha yüksek binada yaşanan ilçe, kadın eğitimi sabit | ≈−0,03 çocuk (ham ilişki −0,14) |
| Bir yıl daha fazla kadın eğitimi | −0,17 çocuk |
| Büyükşehirlerde yaşanan bina yüksekliği 10,2 → 6 m (üst sınır) | En fazla +0,04 çocuk |

Bu yüzden doğurganlık ve evlilik **ilçe ölçeğinde izlenir**, proje ölçeğinde nedensel hedef yapılmaz. Ölçüt listesi, mekânın güçlü kanıtlı etkilerine (yeşil ve ruh sağlığı, okula yürüme ve çocuk sağlığı, komşuluk ve yalnızlık, kuşak yakınlığı, afet güvenliği) dayanıyor.

---

## 2. Finansman bulguları (M6)

### 2.1 Model

- **Arsa:** Aynı 1 ha'da üç biçim. Geometri "Aynı yoğunluk, üç biçim" çiziminden: A 12 katlı blok (96 hane, emsal 1,06), B Z+3 çevre adası (103 hane, 1,23), C Z+2 avlulu çok kuşaklı sıra ev (96 hane, 1,30).
- **Maliyet:** 2026 Yapı Yaklaşık Birim Maliyetleri Tebliği (RG 03.02.2026, 33157) [D]. A: IV.A 26.450 TL/m². B ve C: III.B 21.050 TL/m². Tebliğdeki %10 yüklenici kârı çıkarıldı; otopark, peyzaj, altyapı ve yumuşak maliyetler eklendi.
- **Fiyat:** Türkiye ortalaması 42.488 TL/m² (Ağustos 2026), İstanbul ortalaması 63.788 TL/m² (Haziran 2026) [Endeksa/Emlakjet, basın aktarımı]. Bu değerler bütün stokun ortalaması; yeni konut genellikle daha pahalıya satılır. Grafik 1 bu yüzden 30.000–90.000 TL/m² aralığını tarıyor.
- **Ölçüt:** Arsa kalıntı değeri (AKD). Müteahhidin %15 reel getirisiyle indirgenmiş net satış geliri eksi maliyet. Arsa sahibine kat karşılığında bırakılabilecek en yüksek değer bu.

### 2.2 Aynı yoğunlukta sonuç

| | A · 12 kat | B · Z+3 | C · Z+2 avlulu |
|---|---|---|---|
| İnşaat alanı (m²) | 10.584 | 12.288 | 12.960 |
| Bağımsız bölüm brüt alanı (m²) | 90 | 95 | 124 |
| Otopark ihtiyacı (Ek-1) / maliyeti | 48 yer / 7,9 mn TL | 71 yer / 42,7 mn TL | 96 yer / 43,8 mn TL |
| Satılabilir m² başına maliyet (TL) | 34.091 | 29.132 | 26.932 |
| AKD, Türkiye ort. fiyat (mn TL) | 2,9 | 68,3 | 100,9 |
| AKD, İstanbul ort. fiyat (mn TL) | 128,9 | 241,3 | 298,1 |
| Arsa sahibine azami pay, İstanbul | %34 | %47 | %51 |

**Okuma:** Çizimdeki geometride az katlı düzen daha fazla inşaat alanı veriyor, daha ucuz bir yapı sınıfında yer alıyor ve daha verimli. Bloğun emsali bu yüzden duyarlılık analizinde artırıldı.

### 2.3 Hangi koşulda az katlı ayakta kalıyor?

*Grafik 1: kırılma emsali.* Blok aşağıdaki emsalin üzerinde az katlıdan (C) daha fazla arsa değeri bırakıyor. Emsal bunun altındaysa az katlı ayakta kalıyor.

| Satış fiyatı (TL/m²) | Mevcut kurallar, resmî maliyet farkı | Mevcut kurallar, blok yalnız %10 pahalı | Reform + telafi paketi (%10 fark) |
|---|---|---|---|
| 42.488 (Türkiye ort.) | Blok hiçbir emsalde öne geçemiyor | 5,03 (12 katla 1 ha'ya sığmıyor) | Hiçbir emsalde |
| 50.000 | Hiçbir emsalde (≤4,0) | 2,64 | Hiçbir emsalde (≤4,0) |
| 63.788 (İstanbul ort.) | **2,61** | **2,09** | **3,99** |
| 70.000 | 2,38 | 2,00 | 3,67 |
| 90.000 | 2,07 | 1,87 | 3,17 |

**Sonuç:**

- Türkiye ortalama fiyatlarında az katlı seçenek, yaygın plan emsali aralığının (1,5–2,5) tamamında önde.
- İstanbul fiyatlarında mevcut kurallarla emsal 2,1–2,6'ya kadar önde.
- Reform ve telafi paketiyle bu sınır yaklaşık 4,0'a çıkıyor.

*Grafik 2: telafi köprüsü.* İstanbul ortalama fiyatı, plan emsali 2,5, blok maliyeti az katlıdan %10 fazla:

| Adım | Fark (A − C), mn TL/ha |
|---|---|
| Başlangıç farkı | +56,6 |
| Otopark reformu (net; A'ya da uygulanır) | −9,2 |
| Harç ve ücret indirimi (satıcı tapu harcı %2 → %0,5; belediye harçları −1,5 puan) | −12,8 |
| Hızlı onay (−3 ay) | −12,6 |
| TDR'den önce kalan | +22,0 |
| Emsal transferi (12.040 m², alıcı bölge arsa değerinin %60'ıyla) | −105,7 |
| **Kalan fark** | **−83,7 (az katlı önde)** |

TDR'nin alıcı bölge arsa değerinin yalnız **%12,5'i** kadar bir fiyatla satılması farkı kapatmaya yetiyor. Yani araç, zayıf bir TDR piyasasında bile işler.

**Duyarlılık** (`duyarlilik_tornado.csv`, İstanbul fiyatı, emsal 2,0, taban fark +11,4 mn TL, az katlı önde):

| Parametre | Değişim | Sonuç |
|---|---|---|
| Fiyat primi (bloğa site veya manzara primi ya da az katlıya bahçe primi) | ±%10 | En güçlü etken: −60 ile +83 mn TL arasında |
| Bloğun birim maliyeti | Az katlıyla aynı ↔ resmî IV.A | −24 / +66 mn TL |
| Reel iskonto | %10 ↔ %20 | −14 / +31 mn TL; yüksek faiz, hızlı biten az katlıyı kayırıyor |
| Az katlı yapım süresi | 20 ↔ 12 ay | −4 / +28 mn TL |

**Proje için anlamı:** Az katlı seçeneğin geleceği büyük ölçüde **alıcının bahçeye ve avluya ne kadar değer verdiğine** bağlı. Bu, piyasada ölçülmesi gereken bir sonraki parametre (hedonik fiyat çalışması). TCMB ve ilan verisiyle yapılabilir.

### 2.4 Düşük fiyatlı bölgeler ve dönüşüm (6306)

- **30.000 TL/m²'de** üç biçimin de AKD'si negatif (A −71,0, B −33,2, C −14,7 mn TL/ha). Otopark reformuyla yalnız C pozitife geçiyor (+5,7). Bu bölgelerde kat karşılığı çalışmıyor; kamu finansmanı zorunlu.
- **Yerinde dönüşüm, 96 malik:** İstanbul fiyatında bloğun kendi kendini finanse etmesi için emsal **3,34** (303 konut, 3,2 kat) gerekiyor. Türkiye ortalama ve düşük fiyatta hiçbir emsalde (≤6) mümkün değil.
- **Az katlı yerinde dönüşümde** malik katkısı 3,57 mn TL (medyan aile gelirinin 53 ayı); Yarısı Bizden hibesi sonrası 2,70 mn TL (40 ay). Az katlı dönüşüm, kamu desteği ya da kooperatif modeli olmadan aileler için ağır.
- **Yerinden edilme:** blokta 30 ay, avlulu az katlıda 16 ay (varsayım). 100 m²'lik konutta kira yükü 805 bine karşı 429 bin TL.

### 2.5 Aileye erişim: teslim ve kredi modelleri

124 m²'lik aile konutu (C), Türkiye ortalama fiyatı. Medyan 4 kişilik aile geliri 2026 için ≈67.500 TL/ay tahmin edildi: TÜİK 2025 medyan eşdeğer fert geliri 241.151 TL × OECD ölçeği 2,1 × nominal artış varsayımı 1,60.

| Teslim modeli | Konut bedeli (mn TL) | Piyasa kredisi taksiti / gelir | Aile konut kredisi taksiti / gelir |
|---|---|---|---|
| Kat karşılığı (piyasa) | 5,28 | %182 | 23.985 TL / %35,5 |
| Arsa payı / yapı grubu | 4,62 | %159 | 21.016 TL / %31,1 |
| Kooperatif (arsa piyasa değerinden) | 4,40 | %151 | 19.983 TL / %29,6 |
| Kooperatif + kamu arsası yarı değerle | 3,87 | %133 | 17.593 TL / %26,1 |
| Arsa vakfı / üst hakkı | 3,34 | %115 | 15.203 TL / %22,5 |
| Maliyet kirası (vakıf, belediye) | aylık 11.150 TL (%16,5) | — | Piyasa kirası 33.318 TL (%49) |

- **Piyasa kredisi:** %80 kredi oranı, aylık %2,8, 120 ay.
- **Aile konut kredisi (öneri):** TÜFE'ye endeksli, reel %2, 240 ay, %10 peşin.
- **Kamu maliyeti:** Endeksli aile kredisinde kredinin %22,8'i. TOKİ tipi sabit nominal taksitte %81,9 (enflasyon %25 varsayımı). Aynı kaynakla yaklaşık **3,6 kat** daha fazla aileye ulaşılabilir.

**Okuma:** Ailenin önündeki asıl engel kat sayısı değil, **finansman**. Kooperatif ve arsa vakfı gibi modeller fiyatı %17–37 düşürüyor; endeksli uzun vadeli kredi taksiti gelirin üçte birinin altına çekiyor. Bu, Faz 2'nin "doğurganlık için konut erişimi" bulgusunun politika karşılığı.

---

## 3. Riskler

| Risk | Nerede | Önlem |
|---|---|---|
| **Fiyat primi belirsizliği.** Alıcı site ve manzaraya bahçeden fazla değer verirse az katlı geride kalır | Finansman | Hedonik fiyat çalışması; pilot adalarda satış verisi |
| **Model varsayımları.** Satılabilir alan oranı, yapım süresi ve resmî maliyet farkı doğrulanmadı | Finansman | Gerçek proje verisiyle kalibrasyon; duyarlılık tablosu |
| **TDR piyasasının kurulamaması.** Alıcı bölgede talep yoksa araç işlemez | 3194 md. 13 | Alıcı bölgeyi toplu taşıma koridorunda plan kararıyla belirlemek; düşük fiyatla bile yeterli (%12,5) |
| **Dönüşümün yavaşlaması.** 6306 istisnasına değer artış payı gelince | 3194 Ek md. 8 | 1,2 kata kadar istisna sürer; harç muafiyeti ve aile kredisiyle birlikte |
| **Talep desteğinin fiyatı şişirmesi.** Aile kredisi tek başına konut fiyatını artırabilir (Macaristan dersi, doğrulanmadı) | Finansman | Arz tarafı (kamu arsası, kooperatif) ve aile konutu kotasıyla sınırlama |
| **Zorlama algısı.** Salt çoğunluk ve re'sen plan yetkisi | 6306, 2985 | Eşik düşürülmez; azınlık malik güvencesi; etki değerlendirmesi |
| **Bürokrasi.** Etki değerlendirmesinin süreyi uzatması | Genelge 2026/4 | Kısa form; 30 gün; açık hesap aracı |
| **Mahalle meclisinin siyasallaşması ya da sosyal baskı** | 5393 | Kurayla üyelik; temsil kotası; açık tutanak |
| **Hız ile kalitenin çatışması** (deprem bölgesi) | 6306, TOKİ | Önceden onaylı tip proje; güçlü yapı denetimi; az katlı yapı da TBDY'ye tabi |
| **Yanlış beklenti.** Mekânın doğurganlığı "kurtaracağı" vaadi | Bütün paket | Gerekçe sağlık, çocuk, komşuluk, kuşak ve güvenlik; doğurganlık ilçe ölçeğinde izlenir |

---

## 4. Takvim

| Dönem | Adım | Araç | Sorumlu |
|---|---|---|---|
| **Kasım – Aralık 2026** | Deprem bölgesindeki süren ihalelerde zemin dahil 4 kat sınırı; komşu kümesi ve kuşak yakınlığı tercihleri | Bakanlık talimatı | ÇŞİDB, TOKİ |
| | Mahalle pilotu için belediye meclisi kararları (3 il × 3 mahalle) | Meclis kararı | Belediyeler |
| | Aile konutunun ilk satışında tapu harcı indirimi | Cumhurbaşkanı kararı (492 sayılı Kanun (4) sayılı tarife 20/a) | Hazine ve Maliye |
| **Ocak – Haziran 2027** | Etki ölçütlerinin teknik kurulda gözden geçirilmesi ve 20 plan değişikliğiyle geriye dönük testi | Teknik çalışma | ASHB, ÇŞİDB |
| | Otopark Yönetmeliği (Ek-1, md. 4, 8) ve MPYY (md. 11, 12, EK-2) değişiklik taslaklarının görüşe açılması | Yönetmelik | ÇŞİDB MPGM |
| | TOKİ tip proje kataloğu (3+1, 4+1, çok kuşaklı, büyüyebilen; Z+2 ve Z+3) | İdari | TOKİ |
| **Temmuz – Aralık 2027** | PAİY değişikliği (aile dostu ada düzeni, komşuluk odası, asansör, daire karması) | Yönetmelik | ÇŞİDB |
| | 6306 Uygulama Yönetmeliği (ada bazlı öncelik, etki değerlendirmesi, yerinde kalma) | Yönetmelik | ÇŞİDB, Kentsel Dönüşüm Başkanlığı |
| | Deprem bölgesinde 1–2 pilot ada; örnek yönetim planı | Pilot | Belediye, kat malikleri |
| | Mahalle pilotunun bir yıllık değerlendirmesi | Değerlendirme | Üniversite |
| **2027–2028 Eylem Planı** | Etki ölçütleri, aile konut kredisi, kooperatif ve arsa vakfı modeli, mahalle yönetişimi | Eylem planı | ASHB, Nüfus Politikaları Kurulu |
| **1 Ocak 2028** | Aile ve nüfus etki değerlendirmesinin yürürlüğü | Yönetmelik | ÇŞİDB |
| **2028** | Kanun paketi: 3194 md. 13 (TDR) ve Ek md. 8 (6306 istisnası, değer artış payının donatıya ayrılması); 6306 md. 6 ve 7/10; 634 md. 24 ve 42; 5393 md. 9 | Kanun | TBMM |

---

## 5. Sınırlılıklar ve sonraki adımlar

1. **Model tek bir arsa ve üç tip üzerine kurulu.** Gerçek parsel yapısı, mevcut yapı stoku ve kademeli dönüşüm modellenmedi. Sonraki adım: pilot şehirde gerçek bir adayla kalibrasyon.
2. **Fiyat verisi stok ortalaması.** Yeni konut ve tipolojiye göre fiyat (bahçe ve avlu primi) Türkiye için ölçülmedi. Sonraki adım: hedonik analiz.
3. **KDV modelde nötr varsayıldı**, oran ve eşikler doğrulanmadı.
4. **Doğrulanamayan künyeler:** Genelge 2026/4'ün madde metni (RG PDF'i okunamadı), Yarısı Bizden uzatma kararı, 7452 sayılı Kanunun içeriği, üst hakkı üzerinde kat mülkiyeti (ayrıntı: değişiklik paketi §13.2).
5. **Tasarım dosyalarında iki düzeltme gerekiyor** (bu çalışmada değiştirilmedi):
   - `07_TASARIM_CIZIM/tasarim_parametreleri.md` §6.2'deki EK-2 tablosu güncel değerlere göre yenilenmeli. Bu güncellemeyle taslak programın okul alanları yetersiz kalıyor.
   - Metrik tablosunda B için "asansör gerekmez" ifadesi, PAİY md. 34/1'e göre "zorunlu" olmalı.
6. **Bireysel veri hâlâ en güçlü test.** TÜİK Gelir ve Yaşam Koşulları ve Hacettepe Türkiye Nüfus ve Sağlık Araştırması mikro verisiyle konut tipi ve konut maliyetinin evlilik ve doğum zamanlamasına etkisi sınanmalı. Paket bu sonuçlarla güncellenecek.
