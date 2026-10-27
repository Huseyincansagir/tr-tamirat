# Faz 3 · Rapor 2 — Geleneksel Doku Morfolojisi: Ölçülen Dokular ve Model Mahalle v2 İçin Kalibrasyon

*26 Ekim 2026 · Sürüm 0.1*

| Ne | Nerede |
|---|---|
| Ölçüm kodu (tekrarlanabilir) | [03_VERI/kod/morfoloji_olcum.py](../03_VERI/kod/morfoloji_olcum.py) |
| Alanlar, binalar, sokaklar, adalar (EPSG:4326; 13 gerçek alan, model mahalle yerel koordinatlı olduğu için GPKG'de yok) | [03_VERI/islenmis/morfoloji_alanlar.gpkg](../03_VERI/islenmis/morfoloji_alanlar.gpkg) |
| Karşılaştırma tablosu (15 satır × 120 sütun) | [05_ANALIZ/sonuclar/morfoloji_karsilastirma.csv](../05_ANALIZ/sonuclar/morfoloji_karsilastirma.csv) · kat doğrulaması: `morfoloji_kat_dogrulama.csv` |
| Figür–zemin levhası | [04_HARITA/morfoloji/figur_zemin_levha.png](../04_HARITA/morfoloji/figur_zemin_levha.png) (+ `.svg`) |
| Tek tek figür–zemin planları | `04_HARITA/morfoloji/figur_zemin_G1…G7, C1…C6, M1.png|svg` |
| Ölçüt karşılaştırma grafiği | [04_HARITA/morfoloji/morfoloji_olcutler.png](../04_HARITA/morfoloji/morfoloji_olcutler.png) (+ `.svg`) |
| Ek ham veri | `03_VERI/ham/bina/ms_<quadkey>/` — Microsoft Global ML Building Footprints, 4 karo (§1.2) |

İşaretler projedeki gibidir: **[D]** doğrulandı · **[İ]** ikincil · **[DY]** doğrulanmadı · **[H]** bu çalışmada hesaplandı. Bu belgedeki bütün ölçüler [H] türündedir: OSM, Microsoft ayak izleri, GHSL ve model mahalle v1 çiziminden betikle hesaplandı; elle girilmiş ölçü yoktur.

---

## Özet

**Soru:** İyi işlediği düşünülen geleneksel Türk dokuları hangi ölçülere sahip? Bu ölçüler çağdaş dokulardan ve model mahalle v1'den ne kadar farklı? Model mahalle v2'nin parametreleri buna göre nasıl ayarlanmalı?

**Yöntem:** 7 geleneksel, 6 çağdaş alanda 600 × 600 m'lik (36 ha) birer kare alındı. Model mahalle v1, plan merkezli aynı büyüklükte bir pencereyle (ve ayrıca tam 60 ha ile) aynı betikten geçirildi. Her alanda yaklaşık 50 ölçüt hesaplandı: bina, yapı oturumu, kat ve emsal, nüfus, ada, sokak ağı, cephe arası mesafe ve H/W, avlu, 400 m yakınlık.

**Kısa cevap:** Geleneksel dokuların asıl farkı yükseklikte değil, **tane büyüklüğünde**. Bina tabanı çağdaş dokunun üçte biri, ada yarısı, cephe arası mesafe dörtte üçü kadar. Model mahalle v1 bu tanelilikte geleneksel dokuya yakın ama iki noktada geride kalıyor: ada içi geçirgenlik ve sokak kapalılığı.

1. **Bina tanesi küçük.** Geleneksel alanlarda medyan bina taban alanı **≈ 120 m²** (en × boy ≈ 9 × 14 m), çağdaş alanlarda **≈ 350 m²** (16 × 22 m). Sokağa bakan medyan bina cephesi geleneksel dokuda **6–9 m** (bahçeli Bağlar'da 12 m), yeni konut alanlarında **12–18 m**. Bir sokak kenarında bina başına düşen uzunluk (cephe adımı) **13–24 m**'ye karşı **39–79 m**. Eski kasaba ızgarası üzerindeki Silivri merkezi (9 m ve 21 m) geleneksel değerlere yakın.
2. **Ada küçük, ağ sık.** Medyan ada (sokak eksenlerinden, yaya yolları dahil) yoğun geleneksel dokularda **0,13–0,45 ha** (Zeyrek 0,27; Süleymaniye 0,23), çağdaşlarda **0,29–0,79 ha**. Kavşak yoğunluğu (yaya dahil) Zeyrek'te **467/km²**, geleneksel medyanda **315/km²**, çağdaş medyanda **221/km²**. Medyan sokak parçası **43 m**'ye karşı **59 m**.
3. **Sokak dar ve kapalı.** Yoğun geleneksel dokularda (Zeyrek, Süleymaniye, Antakya) cephe arası medyan mesafe **9,5–11,3 m**; örneklerin dörtte biri **5,4–7,3 m**'nin altında. Çağdaş medyan **18,7 m**. Zeyrek'te sokak örneklerinin **%58**'inde H/W > 1.
4. **Yoğunluk geniş bir aralıkta.** Geleneksel dokular tek tip değil: Birgi ve Safranbolu Bağlar **10 kişi/ha**, Safranbolu Çarşı **28**, Beypazarı **76**, Antakya **162**, Zeyrek ve Süleymaniye **≈ 290–320 kişi/ha** (GHS-POP 2020). Yüksek değerler, ince taneli doku ile GHSL'ye göre 4–5 kata ulaşan yenilenmiş apartman stokunun birleşiminden geliyor.
5. **Model v1 nerede duruyor?** Bina tanesi (medyan 57 m², cephe 6 m) ve cephe adımı (19 m) geleneksel aralıkta. Kavşak yoğunluğu 239/km² (600 m pencere), geleneksel medyanın (315) altında. Ada içi yapısız alan payı (net) **%70**, yoğun geleneksel dokuda **%42–66**. Cephe arası **13,5 m**, yoğun geleneksel dokunun (9,5–11,3 m) üstünde. H/W **0,67** ile hem geleneksel (0,99) hem çağdaş medyanın (0,82) altında; model sokakları daha açık. Ağ verimi (400 m yürüyüşle ulaşılan binanın kuş uçuşu 400 m'dekine oranı) ise en yüksek: **0,67**, geleneksel **0,37–0,55**.
6. **Geleneksel dokunun zaafları da ölçülebiliyor.**
   - Yoğun dokularda kişi başı yapısız alan **19–22 m²**, kamusal yeşil **0,3–2,5 m²/kişi**. Model v1'de bu değerler 65 ve 14 m².
   - Antakya'da sokak örneklerinin **%27**'sinde, Süleymaniye'de **%23**'ünde cephe arası 6 m'nin altında. Bu, itfaiye ve ambulans erişimi ile deprem enkazı açısından kritik.
   - Zeyrek'teki H/W değerleriyle 21 Aralık öğlesinde karşı cephenin zemin katı gölgede kalıyor.
   - Safranbolu Çarşı'da GHS-POP yalnız 28 kişi/ha veriyor; kişi başı inşaat alanı 169 m². Doku korunmuş, ama içinde oturan nüfus azalmış görünüyor (turizm ve konaklamaya dönüşüm; [DY]).

**Veri uyarısı:** OSM'de **Safranbolu Çarşı ve Beypazarı** binalarının %95'ten fazlası yok. Bu iki alan Microsoft ayak izleriyle tamamlandı. Safranbolu Çarşı'nın iç sokakları da OSM'de eksik; sokak ölçütleri güvenilmez. **Antakya**'da OSM binaları Şubat 2023 durumunda donmuş; ölçüler deprem öncesi dokuyu gösteriyor. OSM'de kat etiketi neredeyse yok (Başakşehir hariç %0–1); kat GHSL'den tahmin edildi. GHSL küçük kasabalarda (Birgi, Bağlar) ve yüksek bloklarda (Mamak TOKİ) katı düşük tahmin ediyor (§1.2).

**Model mahalle v2 için ana öneriler (§3):**
- Parsel ve cephe: 6–9 m'lik cephe modülü.
- Yaya adası ≤ 0,35–0,45 ha; her araç adasını en az bir kamusal geçitle bölmek.
- Yaya dahil kavşak yoğunluğu ≥ 300/km².
- S2'de cephe arası 14 m yerine 11–12 m.
- Merkezde net yapı oturumu %45–55.
- T3 avlularının dördüncü kenarını kapatmak, 300–450 m²'lik kapalı avlular.
- Kat profili 2–4 olarak kalmalı.
- Yeşil ve açık alan standartlarında geleneksel doku örnek alınmamalı; v1'deki 13 m²/kişi korunmalı.

---

## 1. Veri ve yöntem

### 1.1 Çalışma alanları

Her alan için 600 × 600 m'lik bir kare alındı. Kare UTM ızgarasına hizalı, kuzey yukarıda. Merkezler şu dört kaynakla doğrulandı:
- OSM yer ve yapı adları (cami, han, hamam, konut sitesi),
- bina dokusu,
- GHSL yükseklik haritası,
- ilçe sınırları (geoBoundaries ADM2).

Seçim kurgusu şöyle: önce 1,6 km'lik ön izleme haritaları çizildi; sonra 600 m'lik pencereler GHSL yapılı hücrelerin OSM kapsamasına göre tarandı. Çağdaş alanlarda hedef ilçenin içinde kalan, tipolojiyi temsil eden ve kapsaması tam bir kare seçildi.

| Kod | Alan | Merkez (enlem, boylam) | İl / ilçe · OSM mahallesi | Dayanak | Bina kaynağı · kapsama |
|---|---|---|---|---|---|
| G1 | Safranbolu Çarşı | 41,2450 · 32,6930 | Karabük / Safranbolu | İzzet Mehmet Paşa Camii, Cinci Hamamı, Saat Kulesi | OSM + Microsoft (%95 MS) · **sokak ağı eksik** |
| G2 | Safranbolu Bağlar | 41,2620 · 32,6700 | Karabük / Safranbolu | Çarşı'nın ≈ 2,5 km kuzeybatısı; bahçe içinde ayrık evler | OSM + Microsoft (%22 MS) |
| G3 | Beypazarı tarihî çekirdek | 40,1695 · 31,9180 | Ankara / Beypazarı · İstiklal | tarihî konut dokusu | OSM + Microsoft (%97 MS) |
| G4 | Fatih — Zeyrek | 41,0187 · 28,9535 | İstanbul / Fatih · Zeyrek | Zeyrek Camii, Çinili Hamam, Fatih Camii; Atatürk Bulvarı'nın batısı | OSM |
| G5 | Fatih — Süleymaniye–Vefa | 41,0168 · 28,9620 | İstanbul / Fatih · Hoca Gıyasettin | Süleymaniye Camii, Vefa Kilise Camii, Kalenderhane | OSM |
| G6 | Birgi | 38,2545 · 28,0650 | İzmir / Ödemiş · Birgi | köy dokusu | OSM |
| G7 | Antakya eski şehir | 36,2015 · 36,1645 | Hatay / Antakya · Ulucami | Asi'nin doğusu, Kurtuluş Caddesi çevresi | OSM (Şubat 2023 durumu) |
| C1 | Esenyurt | 41,0170 · 28,6840 | İstanbul / Esenyurt · Zafer | site blokları ve kuleler | OSM + Microsoft (%5 MS) |
| C2 | Başakşehir 1.–2. Etap | 41,1025 · 28,7890 | İstanbul / Başakşehir · Başakşehir | Başakşehir 1. ve 2. Etap Konutları | OSM |
| C3 | Silivri merkez | 41,0750 · 28,2477 | İstanbul / Silivri · Piri Mehmet Paşa | kent merkezi | OSM |
| C4 | Konya Meram | 37,8705 · 32,4565 | Konya / Meram · Aşkan | 4–6 katlı apartman ızgarası | OSM |
| C5 | Kayseri Kocasinan | 38,7435 · 35,4610 | Kayseri / Kocasinan · Turgut Reis | site kuleleri ve apartman sıraları | OSM |
| C6 | Ankara Mamak TOKİ | 39,9410 · 32,9010 | Ankara / Mamak · Bahçelerüstü | OSM adları: TOKİ 1–2, TOKİ Aydoğdu Sitesi, Toki 510 Konutları, Mamak TOKİ İlkokulu | OSM |
| M1 | Model mahalle v1, 600 m pencere | plan merkezi (x 100–700, y 75–675 m) | — | `07_TASARIM_CIZIM/model_mahalle/kod/plan_modeli.py` | çizim |
| M0 | Model mahalle v1, tam 60 ha | 800 × 750 m | — | aynı | çizim |

**Seçilmeyenler ve nedenleri:**
- **Mudurnu, Göynük, Taraklı:** OSM'de 2–3 km'lik aday kutularda yalnız 194–374 bina vardı; tarihî çekirdeklerde birkaç düzine. Anadolu kasabası olarak OSM kapsaması iyi olan **Birgi** alındı (hücre kapsaması %92). Birgi aynı zamanda Microsoft ayak izlerini doğrulamak için kullanıldı.
- **Esenyurt'ta "yeni yüksek bloklu banliyö":** İlk aday kare (41,020 · 28,645) OSM'de neredeyse boştu (12 bina). Yüksek blokların bulunduğu ve OSM kapsaması tam olan Zafer Mahallesi karesi seçildi.
- **Ankara TOKİ:** Tüm Türkiye PBF'inde Ankara için adında "TOKİ" geçen 116 nesne tarandı. Gültepe TOKİ (Altındağ) için OSM'de 20 katlı üç bina etiketli. Ancak GHSL 2018'de yükseklik yalnız ≈ 9 m çıkıyor ve alanın yarısı vadi. Bunun yerine Mamak'taki TOKİ kümesi seçildi: adları OSM'de doğrulanıyor ve kapsaması tam.
- **Konya Meram:** İlk aday (37,881 · 32,462) geoBoundaries'e göre Selçuklu'da kaldı; Meram sınırı içindeki Aşkan Mahallesi karesine geçildi.

### 1.2 Veri, kapsama ve doğrulama

| Veri | Kullanım | Not |
|---|---|---|
| OSM Türkiye (Geofabrik, 25.10.2026, 652 MB) | Bina, sokak, su, yeşil, mahalle sınırı | Betik yalnız karelerin 500 m tamponlu kutularını, referansları tam bir kesit olarak çıkarır (ilk çalıştırmada ≈ 3 dk, ≈ 5 MB). Kesit tek geçişte okunur |
| Microsoft Global ML Building Footprints (2026-02-03 sürümü) | OSM'nin eksik kaldığı alanlarda bina | Seviye 9 quadkey karoları, yalnız ilgili 4 karo: 120323332 (Safranbolu, 7,3 MB), 122101103 (Beypazarı, 4,6 MB), 120323222 (İstanbul batı, 26,6 MB), 122100313 (Birgi, doğrulama için, 24,8 MB). Toplam ≈ 63 MB. İndirmeden önce boyutlar dizin dosyasından okundu. Yükseklik alanı Türkiye için boş (−1) |
| GHS-BUILT-H ANBH 2018 (100 m) | Kat etiketi olmayan binaların katı = round(ANBH / 3 m), en az 1 | Etiket ve yükseklikle karşılaştırma aşağıda |
| GHS-POP 2020 (100 m) | Karenin nüfusu (kare–hücre kesişim oranıyla); bina başına nüfus (hücre nüfusu binaların inşaat alanı oranında dağıtıldı) | Modellenmiş nüfus; konut sayımı değil |
| İlçe paneli (ADNKS 2025 nüfusu / MEDAS hane sayısı) | Konut yoğunluğu ≈ nüfus / ilçe ortalama hane büyüklüğü | Boş konut ve ikinci konut hesaba katılmadı |

**OSM ile Microsoft'un birleştirilmesi:**
- **Karar kuralı.** Karedeki Microsoft izlerinin en az %85'i OSM'de bir binaya 1 m'den yakınsa, yalnız OSM kullanıldı.
- **Ekleme kuralı.** Aksi halde yalnız iki koşulu birlikte sağlayan Microsoft izleri eklendi: hiçbir OSM binasına 1 m'den yakın değil ve alanının %20'sinden azı OSM ile örtüşüyor. Bu, iki kaynak arasındaki kaymadan doğacak kopyaları önler.
- **Sonuç.**
  - Safranbolu Çarşı ve Beypazarı'nda OSM, Microsoft izlerinin yalnız %7 ve %5'ini karşılıyor. Bu iki karede binaların %95 ve %97'si Microsoft'tan geldi.
  - Bağlar'da (%78) ve Esenyurt'ta (%84) eksik kısımlar tamamlandı.
  - Başakşehir (%87), Silivri (%91) ve Birgi (%97) yalnız OSM ile ölçüldü.

**Microsoft izleri geleneksel dokuda ne kadar güvenilir?** OSM'nin iyi olduğu karelerde iki kaynak ayrı ayrı ölçüldü:

| Kare | OSM bina | MS iz | MS / OSM (sayı) | OSM yapı oturumu | MS yapı oturumu |
|---|---|---|---|---|---|
| Birgi (ayrık geleneksel ev) | 585 | 434 | 0,74 | %17,9 | %16,5 |
| Silivri merkez (bitişik nizam) | 641 | 242 | 0,38 | %35,2 | %40,5 |
| Başakşehir (ayrık bloklar) | 133 | 147 | 1,11 | %19,7 | %19,8 |
| Safranbolu Bağlar (bahçeli ayrık ev) | 230 | 284 | 1,23 | %9,4 | %11,3 |

Okuma:
- **Yapı oturumu** iki kaynakta ±%20 içinde tutarlı (Birgi −%8, Başakşehir %0, Silivri +%15, Bağlar +%20).
- **Bina sayısı** güvenilmez. Microsoft bitişik binaları birleştiriyor: Silivri'de sayı OSM'nin %38'i. Ayrık dokuda küçük binaları kaçırabiliyor (Birgi %74).
- **Sonuç.** Safranbolu Çarşı ve Beypazarı'nın "bina/ha" ve "taban alanı" değerleri dikkatli okunmalı. Ayrık evli Çarşı'da gerçek bina sayısı muhtemelen daha yüksek, ortalama taban alanı daha düşük [H].

**GHSL ile OSM kapsaması:** Karelerdeki GHSL yapılı hücrelerin (ANBH > 0) **%92–100**'ünde en az bir bina izi var (`hucre_kapsama`). Bu ölçüt gevşek; tek bir bina bir hücreyi "kapsanmış" saydırır. Asıl denetim Microsoft karşılaştırması ve gözle kontrol oldu. Her alanın bina kaynağı ve sokak sınıfı ayrı renkte çizilerek tanı haritasında incelendi.

**Sokak ağı:** Safranbolu Çarşı'da OSM yalnız ana ve tali sokakları içeriyor; konakların arasındaki dar sokakların çoğu yok. Bu yüzden G1'in kavşak, ada, cephe arası, H/W ve yakınlık değerleri **güvenilmez** olarak işaretlendi. Grafik ve grup medyanlarına katılmadılar. Diğer alanlarda sokak ağı gözle bakıldığında tutarlı.

**Antakya'nın durumu (2023 depremi):**
- Karedeki OSM binalarının **%99,5'i en son 6 Şubat 2023 ve sonrasında**, neredeyse tamamı Şubat 2023'te düzenlenmiş. Bu, deprem sonrası hızlı haritalama dalgası; ≈ 110 bina `source=microsoft/BuildingFootprints` etiketli.
- ≈ 85 bina `earthquake:damage=yes` taşıyor; 81 nesne `destroyed:building=yes` gibi yaşam döngüsü etiketiyle "yıkıldı" olarak işaretli. Şubat 2023'ten sonra karede yalnız birkaç (≈ 7) düzenleme var.
- Yani OSM, yıkım ve enkaz kaldırma sonrasındaki durumu göstermiyor. Eski şehirdeki yıkımın gerçek boyutu bu çalışmada doğrulanmadı [DY].
- Ölçüm bu yüzden bilerek **deprem öncesi dokuyu** hedefledi: "yıkıldı" etiketli binalar da dahil edildi (karede toplam 1.190 bina).
- GHSL 2018 ve GHS-POP 2020 de deprem öncesine ait. Antakya satırı bugünkü durumu değil, kaybedilen dokuyu ve yeniden kurulacak dokunun referansını gösteriyor.

**Kat bilgisi ve GHSL'nin yanlılığı:**
- **Kat etiketi seyrek.** OSM'de `building:levels` etiketi Başakşehir'de binaların %83'ünde var. Diğer 12 alanda %0–1.
- **Ne kullanıldı?** Kat çoğunlukla GHSL ANBH / 3 m'den geldi.
- **Karşılaştırma.** Tüm genişletilmiş kutulardaki 409 etiketli bina kullanıldı (`morfoloji_kat_dogrulama.csv`):

| GHSL ANBH sınıfı | Etiketli bina | OSM katı (medyan) | GHSL/3 (medyan) |
|---|---|---|---|
| 7–10 m | 49 | 3 | 3 |
| 10–15 m | 169 | 6 | 4 |
| 15–20 m | 106 | 15 | 6 |
| ≥ 20 m | 71 | 15 | 8 |

Okuma:
- **Düşük yapılarda tutarlı.** 3 kata kadar GHSL/3 OSM ile örtüşüyor.
- **Orta ve yüksek yapılarda düşük.** 5 katın üstünde GHSL/3 katı **yarı yarıya** düşük tahmin ediyor. Örneklem Başakşehir'in 15 katlı bloklarının ağırlığında.
- **Küçük kasabalarda da düşük.** Birgi'de ortalama ANBH 2,5 m, Bağlar'da 4,4 m çıkıyor; bu tek katın altı. GHSL'nin 100 m çözünürlükteki yükseklik modeli küçük, dağınık yapılarda yüksekliği düşürüyor [H].

Betik bu iki durumu otomatik işaretliyor (`kat_suphe`): kat çoğunlukla GHSL'den geliyor **ve** şu iki koşuldan biri sağlanıyor:
- GHSL ortalaması < 5 m: Birgi, Bağlar;
- kişi başı inşaat alanı < 25 m²: Mamak TOKİ, 18 m²/kişi; GHS-POP'un verdiği 563 kişi/ha ile tutarsız.

İşaretlenen alanlarda emsal ve H/W **alt sınırdır**. Duyarlılık için "her bina en az 2 kat" varsayımıyla ikinci bir emsal (`emsal_en_az_2_kat`) de verildi. Bu bir varsayımdır [DY].

### 1.3 Ölçütler

| Ölçüt | Tanım |
|---|---|
| Arazi | Kare − OSM su alanları (Birgi'de 1,2 ha dere, Antakya'da 0,6 ha Asi, Silivri'de 0,6 ha dere) |
| Bina/ha, taban alanı, bina eni × boyu | Merkezi karede kalan binalar; en ve boy en küçük döndürülmüş dikdörtgenden |
| Yapı oturumu (GSI) | Kareye kırpılmış taban alanı / arazi |
| Ortalama kat | Taban ağırlıklı |
| Emsal (FSI), katman L, açık alan oranı OSR | Σ taban × kat / arazi; L = FSI / GSI; OSR = (1 − GSI) / FSI (Berghauser Pont ve Haupt, *Spacematrix*, 2010 [DY]) |
| Nüfus, konut | GHS-POP 2020; konut ≈ nüfus / ilçe hane büyüklüğü |
| Yapısız alan, kamusal yeşil | 1 − GSI ve kişi başına; OSM park, oyun alanı, rekreasyon, kamusal bahçe ve meydan |
| Sokak ağı | "Araç": trafiğe açık yollar (`service` yalnız `alley` ya da alt türsüz). "Sokak" (yaya dahil): araç yolları + `pedestrian`, `footway`, `steps`, `path`; kaldırım ve geçit çizgileri hariç |
| Kavşak yoğunluğu | ≥ 3 yöne bağlanan düğüm; 5 m içindekiler tek kavşak; karedeki sayı / arazi km² |
| Çıkmaz payı | Çıkmaz uç / (çıkmaz uç + kavşak) |
| Sokak parçası | Kavşaktan kavşağa ya da çıkmaz uca kadar; orta noktası karede olanlar |
| Yönelim entropisi ve düzen φ | Boeing (2019) yöntemi: 36 kutulu, uzunluk ağırlıklı yön histogramı. Tam ızgarada φ = 1, tam dağınıklıkta φ = 0 [İ] |
| Ada | Sokak ağı (yaya dahil) eksenlerinin çevrelediği çokgen; eksenden eksene, brüt; 50 m² altı ve 20 ha üstü hariç. "Araç adası": yalnız araç ağıyla |
| Net ada, ada içi yapısız alan | Ada − sokak eksenine sınıf yarım genişliği kadar tampon (konut sokağı 4 m, tali 6 m, yaya yolu 1,5 m vb.; varsayım). Net ada içindeki bina dışı alan payı |
| Kapalı avlu | Bina birleşiminin (0,25 m kapanış) içinde kalan, 10–5.000 m²'lik boşluklar. OSM iç halkaları dahil |
| Cephe arası mesafe (W), H/W | Sokak (yaya dahil) ekseninde 3 m arayla örnek nokta. Her noktadan iki yana 30 m'lik dik ışın, ilk bina cephesine uzaklık; kavşaklara 10 m'den yakın noktalar hariç. W = sol + sağ, iki yanda da bina varsa. H = iki cephenin ortalama kat × 3 m |
| Cephe sürekliliği | Sokak kenarı örneklerinden 15 m içinde bina cephesi bulunanların payı |
| Bina cephesi, cephe adımı | Aynı binaya çarpan ardışık ışınların uzunluğu (bina cephesi). Sokak kenarı uzunluğu / cephe sayısı (cephe adımı = bina başına sokak kenarı; parsel cephesinin vekili) |
| Yakınlık | Binanın yürüme ağındaki en yakın noktasından 400 m ağ mesafesinde ulaşılan bina sayısı, inşaat alanı ve nüfus. Karedeki en çok 700 rastgele bina; medyan. "Ağ verimi" = ağ üzerinden ulaşılan / kuş uçuşu 400 m'deki bina |

**Model mahalle v1 nasıl ölçüldü?**
- **Geometri.** Bütün geometri `plan_modeli.py`'den okundu: parsellerin binaları, donatı binaları ve sokak eksenleri.
- **Katlar.** T1 için son durum Z+2 ve 1 katlı arka genişleme alındı; T2 3 kat; T3 sokak kanadında 3–4, yan kanatlarda 2 kat; T4 4–5 kat.
- **Nüfus.** Konut × 3,2 kişi.
- **Sokak sınıfları.** Araç ağı: toplayıcı, S1 ve S2. Yaya dahil ağ: ek olarak S3 geçitleri ve diyagonaller.
- **Kontrol.** Betiğin tam 60 ha için verdiği değerler `metrikler.csv` ile tutarlı: brüt yoğunluk 118,5 kişi/ha; araç ağında kavşak 117/km² (CSV 116,7). Yaya dahil kavşak 212/km² (CSV 203); fark, 5 m'lik birleştirme ve diyagonal–kenar kesişmelerinden. S2'de cephe arası 13,5 m çıkıyor; model belgesi 14,0 m diyor.
- **Pencere seçimi.** Ana karşılaştırmada 600 m pencere (M1) kullanıldı. Merkezi içeren bu pencere 60 ha'nın ortalamasından biraz daha sık. Tam 60 ha değerleri (M0) tablolarda ayrıca verildi.

---

## 2. Bulgular

Tablolarda **°** Microsoft ayak izi katkısını, **†** Antakya'nın deprem öncesi durumunu, **\*** güvenilmez sokak ölçütlerini, **‡** muhtemelen düşük tahmin edilmiş katı gösterir. Grup medyanlarında \* ve ‡ işaretli değerler dışarıda bırakıldı. Model satırları kalın.

### 2.1 Bina, yapı oturumu ve kat

| Alan | Bina/ha | Yapı oturumu | Taban ort. (m²) | Taban medyan (m²) | Bina eni × boyu (m) | Ort. kat | ≤ 3 katlı bina | Emsal | Emsal (≥ 2 kat varsayımı) |
|---|---|---|---|---|---|---|---|---|---|
| Safranbolu Çarşı ° \* | 12,2 | %23 | 188 | 140 | 10,5 × 13,9 | 2,1 | %100 | 0,48 | 0,49 |
| Safranbolu Bağlar ° ‡ | 8,1 | %10 | 128 | 118 | 9,8 × 12,1 | 1,5 | %100 | 0,16 | 0,21 |
| Beypazarı ° | 13,7 | %30 | 219 | 136 | 10,4 × 14,0 | 3,4 | %60 | 1,03 | 1,04 |
| Fatih Zeyrek | 27,6 | %45 | 157 | 111 | 8,6 × 13,9 | 4,3 | %19 | 1,90 | 1,90 |
| Fatih Süleymaniye | 12,5 | %31 | 249 | 127 | 9,4 × 14,4 | 5,4 | %8 | 1,69 | 1,70 |
| Birgi ‡ | 16,8 | %19 | 110 | 99 | 8,7 × 12,0 | 1,0 | %100 | 0,19 | 0,37 |
| Antakya † | 33,6 | %30 | 92 | 54 | 6,3 × 9,1 | 3,0 | %86 | 0,93 | 0,93 |
| **Model v1 (600 m)** | **21,2** | **%21** | **100** | **57** | **6,3 × 9,0** | **2,8** | **%94** | **0,61** | **0,63** |
| **Model v1 (60 ha)** | **23,9** | **%23** | **94** | **57** | **6,3 × 9,0** | **2,9** | **%95** | **0,66** | **0,68** |
| Esenyurt ° | 6,3 | %26 | 393 | 200 | 13,0 × 16,5 | 6,4 | %13 | 1,63 | 1,63 |
| Başakşehir | 3,7 | %20 | 545 | 475 | 18,2 × 27,4 | 10,5 | %11 | 2,07 | 2,07 |
| Silivri | 18,1 | %36 | 194 | 143 | 10,2 × 16,4 | 5,1 | %0 | 1,84 | 1,84 |
| Konya Meram | 5,7 | %28 | 495 | 429 | 18,2 × 24,4 | 4,2 | %11 | 1,20 | 1,20 |
| Kayseri Kocasinan | 5,9 | %19 | 323 | 286 | 14,5 × 19,9 | 4,8 | %20 | 0,90 | 0,90 |
| Ankara Mamak TOKİ ‡ | 5,6 | %24 | 419 | 408 | 18,3 × 24,7 | 4,2 | %3 | 1,01 | 1,01 |
| *Geleneksel medyanı* | *13,7* | *%30* | *157* | *118* | *9,4 × 13,9* | *3,4* | *%86* | *1,03* | |
| *Çağdaş medyanı* | *5,8* | *%25* | *406* | *347* | *16,3 × 22,2* | *5,1* | *%11* | *1,63* | |

Okuma:
- **Asıl fark tanede.** Yapı oturumu geleneksel ve çağdaş dokuda birbirine yakın (%30'a karşı %25). Asıl fark bina tanesinde. Aynı arazi payını geleneksel doku hektar başına ≈ 14, çağdaş doku ≈ 6 binayla örtüyor. Geleneksel bina tabanı çağdaşın üçte biri.
- **Zeyrek en sık doku.** %45 yapı oturumu ve 27,6 bina/ha ile en sık geleneksel doku. Ancak ortalama 4,3 kat (GHSL ortalaması 13 m) geleneksel ahşap evden değil, büyük olasılıkla 20. yüzyılda yerlerine yapılan 4–6 katlı apartmanlardan geliyor [DY]. Süleymaniye'de de benzer: Bina stoku yenilenmiş, sokak ve parsel dokusu korunmuş. Zeyrek'in emsali 1,9.
- **Model v1 geleneksele yakın.** Bina tanesi (medyan 57 m², 6,3 × 9 m) geleneksel dokuya, hatta Antakya'nın ince tanesine yakın. Yapı oturumu ise (%21) geleneksel medyanın (%30) altında.
- **Çağdaş emsaller alt sınır.** Çağdaş alanlardaki emsaller (0,9–2,1) GHSL katlarına dayanıyor ve muhtemelen düşük (§1.2). Etiketli Başakşehir'de emsal 2,07. Mamak TOKİ'de kişi başı inşaat alanı yalnız 18 m²; bu, emsalin en az iki katı olabileceğini düşündürüyor [H].

### 2.2 Nüfus, konut ve açık alan

| Alan | Kişi/ha | Hane büy. | Konut/ha (tahmin) | İnşaat m²/kişi | Yapısız alan | Yapısız m²/kişi | Kamusal yeşil | Yeşil m²/kişi |
|---|---|---|---|---|---|---|---|---|
| Safranbolu Çarşı ° \* | 28 | 3,00 | 9 | 169 | %77 | 272 | %0,3 | 1,1 |
| Safranbolu Bağlar ° ‡ | 10 | 3,00 | 3 | 158 | %90 | 889 | %0,0 | 0,0 |
| Beypazarı ° | 76 | 2,79 | 27 | 135 | %70 | 92 | %0,1 | 0,1 |
| Fatih Zeyrek | 287 | 2,92 | 98 | 66 | %55 | 19 | %5,2 | 1,8 |
| Fatih Süleymaniye | 317 | 2,92 | 108 | 53 | %69 | 22 | %7,9 | 2,5 |
| Birgi ‡ | 10 | 2,78 | 4 | 188 | %81 | 823 | %2,8 | 28,0 |
| Antakya † | 162 | 3,29 | 49 | 57 | %70 | 43 | %0,4 | 0,3 |
| **Model v1 (600 m)** | **121** | **3,20** | **38** | **50** | **%79** | **65** | **%17,2** | **14,2** |
| **Model v1 (60 ha)** | **119** | **3,20** | **37** | **56** | **%77** | **65** | **%15,7** | **13,2** |
| Esenyurt ° | 294 | 3,40 | 87 | 55 | %74 | 25 | %2,7 | 0,9 |
| Başakşehir | 157 | 3,66 | 43 | 132 | %80 | 51 | %3,6 | 2,3 |
| Silivri | 198 | 3,38 | 59 | 93 | %64 | 32 | %0,8 | 0,4 |
| Konya Meram | 101 | 3,42 | 30 | 119 | %72 | 71 | %3,3 | 3,3 |
| Kayseri Kocasinan | 223 | 3,20 | 70 | 41 | %81 | 36 | %3,2 | 1,4 |
| Ankara Mamak TOKİ ‡ | 563 | 3,03 | 186 | 18 | %76 | 14 | %2,7 | 0,5 |
| *Geleneksel medyanı* | *76* | | *27* | | *%70* | *92* | *%0,4* | *1,1* |
| *Çağdaş medyanı* | *210* | | *64* | | *%75* | *34* | *%3,0* | *1,2* |

Okuma:
- **Yoğunluk aralığı geniş.** Geleneksel dokuların yoğunluğu 10 ile 317 kişi/ha arasında değişiyor. Tek bir "geleneksel yoğunluk" yok:
  - kasaba ve bağ evi dokuları 10–76 kişi/ha,
  - İstanbul tarihî yarımadası 290–320 kişi/ha,
  - Antakya 162 kişi/ha.
  Model v1'in 120 kişi/ha'sı bu aralığın ortasında. Tasarım parametrelerindeki 100–150 kişi/ha bandı geleneksel kent dokusunun alt yarısına denk geliyor.
- **Korunan dokuda nüfus az.** Safranbolu Çarşı ve Beypazarı'nda kişi başı inşaat alanı 135–169 m². GHS-POP oturan nüfusu düşük veriyor. Bu, konutların pansiyon, dükkân ve müzeye dönüşmesiyle uyumlu [DY]. Korunan doku canlı bir mahalle olarak işlemiyor olabilir. `ornek_uygulamalar.md` §3.2 Beypazarı ve Cumalıkızık için aynı uyarıyı yapmıştı.
- **Açık alan ve yeşil zayıf.** Bu, geleneksel dokunun en açık zaafı. Zeyrek ve Süleymaniye'de kişi başı yapısız alan 19–22 m², kamusal yeşil 1,8–2,5 m²/kişi; MPYY EK-2'nin 10 m²'sinin beşte biri. Model v1'de 65 ve 14 m². Birgi'deki 28 m²/kişi, karenin içindeki dere kenarı yeşilinden ve çok düşük nüfustan geliyor.
- **Çağdaş dokular yeşilde daha iyi değil.** OSM'ye göre kamusal yeşil yalnız %1–4. Ancak OSM'nin park kaydı eksik (Faz 2, Rapor 4).

### 2.3 Ada ve sokak ağı

| Alan | Ada medyan (ha) | Ada kısa × uzun (m) | Ada çevresi (m) | Araç adası (ha) | Kavşak/km² (yaya dahil) | Kavşak/km² (araç) | Sokak km/km² | Parça medyan (m) | Çıkmaz (araç) | Yönelim φ |
|---|---|---|---|---|---|---|---|---|---|---|
| Safranbolu Çarşı ° \* | 0,49 | 56 × 105 | 314 | 0,59 | 197 | 164 | 23,0 | 46 | %6 | 0,03 |
| Safranbolu Bağlar ° ‡ | 1,65 | 114 × 251 | 586 | 1,65 | 47 | 47 | 11,1 | 124 | %6 | 0,15 |
| Beypazarı ° | 0,13 | 31 × 55 | 157 | 0,13 | 322 | 300 | 26,9 | 30 | %18 | 0,11 |
| Fatih Zeyrek | 0,27 | 38 × 74 | 231 | 0,29 | 467 | 353 | 39,3 | 39 | %12 | 0,43 |
| Fatih Süleymaniye | 0,23 | 43 × 76 | 214 | 0,26 | 392 | 264 | 33,1 | 40 | %6 | 0,11 |
| Birgi ‡ | 0,58 | 64 × 146 | 386 | 0,87 | 175 | 138 | 22,1 | 46 | %13 | 0,14 |
| Antakya † | 0,45 | 65 × 102 | 295 | 0,50 | 308 | 178 | 29,8 | 48 | %18 | 0,17 |
| **Model v1 (600 m)** | **0,35** | **48 × 73** | **241** | **0,97** | **239** | **119** | **34,5** | **48** | **%0** | **0,94** |
| **Model v1 (60 ha)** | **0,79** | **73 × 126** | **368** | **0,94** | **212** | **117** | **30,6** | **69** | **%0** | **0,95** |
| Esenyurt ° | 0,51 | 44 × 138 | 373 | 0,51 | 164 | 156 | 22,2 | 58 | %11 | 0,30 |
| Başakşehir | 0,79 | 92 × 144 | 490 | 1,04 | 161 | 128 | 22,2 | 48 | %28 | 0,31 |
| Silivri | 0,29 | 45 × 83 | 243 | 0,29 | 409 | 398 | 36,9 | 42 | %7 | 0,28 |
| Konya Meram | 0,67 | 67 × 115 | 359 | 0,67 | 211 | 208 | 27,4 | 68 | %0 | 0,65 |
| Kayseri Kocasinan | 0,72 | 63 × 135 | 360 | 0,72 | 231 | 231 | 25,1 | 60 | %1 | 0,73 |
| Ankara Mamak TOKİ ‡ | 0,69 | 77 × 108 | 338 | 0,73 | 233 | 200 | 25,0 | 62 | %5 | 0,09 |
| *Geleneksel medyanı* | *0,36* | *54 × 89* | *263* | *0,40* | *315* | *221* | *28,4* | *43* | *%12* | *0,14* |
| *Çağdaş medyanı* | *0,68* | *65 × 125* | *360* | *0,69* | *221* | *204* | *25,1* | *59* | *%6* | *0,31* |

Okuma:
- **Ada ölçüsü.** Yoğun geleneksel dokularda ada eksenden eksene 0,13–0,45 ha, kısa kenar 31–65 m, çevre 157–314 m. Çağdaş dokularda ada yaklaşık iki kat büyük (0,5–0,8 ha, çevre 340–490 m). Silivri merkezi çağdaş grupta ama eski kasaba ızgarası üzerinde; değerleri geleneksel dokuya benziyor (0,29 ha, 409 kavşak/km²). Bu, ada ölçüsünü yapı tipinden çok **plan dokusunun** belirlediğini gösteriyor.
- **Model v1'in ikili yapısı:**
  - Araç adası 0,94–0,97 ha. Bu, çağdaş dokunun da üstünde; tasarımda istenen "araç hücresi" etkisi.
  - Yaya geçitleri ve diyagonallerle bölünen merkez penceresinde yaya adası 0,35 ha'ya iniyor; geleneksel medyana eşit.
  - Tam 60 ha'da ise yaya adası medyanı 0,79 ha. T1/T2 adalarında ada içi geçit yok; bu adalar çağdaş ölçüde kalıyor.
- **Kavşak yoğunluğu.** Model 212–239/km² ile tasarım hedefini (≥ 80–120) rahatça aşıyor. Ama yoğun geleneksel dokunun (308–467) gerisinde kalıyor.
- **Araç ağında geleneksel doku daha sık.** Zeyrek'te araç ağının kavşak yoğunluğu 353/km²; dar sokakların çoğu araca açık. Model v1'de 119/km². Geleneksel dokunun bu "her sokağa araç" özelliği bugünkü trafik ve otoparkla birleşince zaafa dönüşüyor (§2.7).
- **Yönelim.** Geleneksel dokular düzensiz (φ 0,03–0,43), model tam ızgara (φ 0,94). Konya ve Kayseri'nin imar ızgaraları (φ 0,65–0,73) arada. Düzensizliğin kendisi bir erdem değil; geleneksel dokuda düzensizlik topoğrafyadan ve parça parça büyümeden geliyor (§3.2).

### 2.4 Sokak kesiti: cephe arası mesafe, H/W ve cephe

| Alan | Cephe arası medyan (m) | P25–P75 (m) | < 6 m payı | H/W medyan | H/W > 1 payı | Cephe sürekliliği | Bina cephesi medyan (m) | Cephe adımı (m) |
|---|---|---|---|---|---|---|---|---|
| Safranbolu Çarşı ° \* | 18,9 | 11,8–28,3 | %6 | 0,33 | %7 | %44 | 9 | 23 |
| Safranbolu Bağlar ° ‡ | 20,9 | 13,5–29,2 | %4 | 0,22 | %3 | %32 | 12 | 34 |
| Beypazarı ° | 16,9 | 9,6–24,8 | %14 | 0,64 | %29 | %58 | 6 | 17 |
| Fatih Zeyrek | 9,5 | 7,3–18,6 | %12 | 1,20 | %58 | %73 | 9 | 13 |
| Fatih Süleymaniye | 10,3 | 6,4–22,0 | %23 | 1,46 | %65 | %49 | 9 | 24 |
| Birgi ‡ | 15,7 | 8,8–25,1 | %10 | 0,19 | %3 | %48 | 9 | 20 |
| Antakya † | 11,3 | 5,4–20,6 | %27 | 0,78 | %41 | %56 | 6 | 15 |
| **Model v1 (600 m)** | **13,5** | **10,0–15,5** | **%5** | **0,67** | **%13** | **%51** | **6** | **19** |
| **Model v1 (60 ha)** | **13,5** | **10,0–15,5** | **%4** | **0,67** | **%12** | **%48** | **6** | **21** |
| Esenyurt ° | 16,4 | 9,2–31,7 | %0 | 1,04 | %53 | %35 | 12 | 45 |
| Başakşehir | 31,4 | 23,2–39,5 | %0 | 0,82 | %42 | %22 | 18 | 79 |
| Silivri | 9,2 | 6,6–16,4 | %18 | 1,58 | %72 | %52 | 9 | 21 |
| Konya Meram | 20,8 | 15,7–30,7 | %0 | 0,59 | %10 | %44 | 18 | 42 |
| Kayseri Kocasinan | 18,9 | 16,9–25,6 | %0 | 0,65 | %0 | %41 | 18 | 39 |
| Ankara Mamak TOKİ ‡ | 18,6 | 17,5–23,6 | %0 | 0,67 | %2 | %42 | 18 | 40 |
| *Geleneksel medyanı* | *13,5* | | *%13* | *0,99* | | *%52* | *9* | *19* |
| *Çağdaş medyanı* | *18,7* | | *%0* | *0,82* | | *%41* | *18* | *41* |

Cephe arası mesafe kamusal yol genişliği değildir. Ön bahçeyi ve cephe çekmelerini de içerir. Bahçeli ayrık evlerin olduğu Safranbolu, Bağlar ve Birgi'de yüksek çıkması bu yüzden.

Okuma:
- **Yoğun geleneksel sokak 9,5–11,3 m.** Zeyrek, Süleymaniye ve Antakya'da medyan cephe arası 9,5–11,3 m, alt çeyrek 5,4–7,3 m. Model v1'in S2 yaşam sokağı 13,5 m, S3 yaya geçidi 6 m.
- **Yeni konut alanlarında 6 m altı sokak yok.** Silivri merkezi dışındaki beş çağdaş alanda cephe arası 6 m'nin altına hiç inmiyor. Bunun nedeni MPYY'nin 7 m mahreç ve 10 m trafik yolu alt sınırı ile 5 m ön bahçe uygulaması [D/DY].
- **Kapalılık yükseklikten geliyor.** Zeyrek ve Süleymaniye'de örneklerin %58–65'inde H/W > 1. Ama bu kapalılık geleneksel ahşap evden değil, dar sokakta yükselen apartmandan geliyor (§2.1). Silivri merkezinde H/W 1,58 ile en kapalı doku; dar eski kasaba sokakları 5 kata çıkmış.
- **Model v1 orta kapalılıkta.** H/W 0,67; yoğun geleneksel (0,8–1,5) ile ferah çağdaş arasında. Tasarım parametrelerindeki S2 hedefinin (0,7–1,0) biraz altında; model belgesi de aynı açığı not etmişti.
- **Cephe ritmi.** Geleneksel dokuda sokağa bakan bina cephesi 6–9 m, cephe adımı (bina başına sokak kenarı) 13–24 m. Çağdaş dokuda 12–18 m ve 39–79 m. Yani çağdaş sokakta bir yaya, geleneksel sokaktakinin iki ila dört katı yürüyerek bir sonraki kapıya ulaşıyor. Model v1 6 m ve 19 m ile geleneksel ritimde. Ancak T3'ün 36 m'lik ve T4'ün 24 m'lik tek cephesi bu ritmi bozuyor.

### 2.5 Avlu ve ada içi boşluk

| Alan | Kapalı avlu /ha | Kapalı avlu medyan (m²) | Ada içi yapısız (net) | Net yapı oturumu | Sokak alanı payı (tahmin) |
|---|---|---|---|---|---|
| Safranbolu Çarşı ° \* | 0,03 | 16 | %76 | %24 | %20 |
| Safranbolu Bağlar ° ‡ | 0 | — | %88 | %12 | %10 |
| Beypazarı ° | 0,11 | 131 | %66 | %34 | %23 |
| Fatih Zeyrek | 0,53 | 206 | %42 | %58 | %30 |
| Fatih Süleymaniye | 0,36 | 345 | %63 | %37 | %21 |
| Birgi ‡ | 0,03 | 63 | %69 | %31 | %23 |
| Antakya † | 0,14 | 157 | %65 | %35 | %23 |
| **Model v1 (600 m)** | **0** | **—** | **%70** | **%30** | **%27** |
| **Model v1 (60 ha)** | **0** | **—** | **%70** | **%30** | **%29** |
| Esenyurt ° | 0,03 | 195 | %72 | %28 | %19 |
| Başakşehir | 0 | — | %79 | %21 | %19 |
| Silivri | 0 | — | %46 | %54 | %37 |
| Konya Meram | 0 | — | %62 | %38 | %24 |
| Kayseri Kocasinan | 0 | — | %75 | %25 | %20 |
| Ankara Mamak TOKİ ‡ | 0 | — | %70 | %30 | %19 |

Okuma:
- **OSM'de iç halka neredeyse yok.** OSM'de iç halkalı bina (avlusu ayrı çizilmiş bina) yalnız Süleymaniye'de %2,2 (medrese ve hanlar).
- **Kapalı avlu yalnız İstanbul'da belirgin.** Bina birleşiminin çevrelediği kapalı avlular Zeyrek'te hektar başına 0,53 (medyan 206 m²), Süleymaniye'de 0,36 (345 m²). Bunlar bitişik nizam çevre adalarının iç bahçeleri.
- **Anadolu dokusunda avlu duvarla kapanıyor.** Safranbolu, Birgi ve Beypazarı'nda avlular binayla değil bahçe duvarıyla kapanıyor. Bu yüzden bina izinden ölçülemiyor; bu dokularda avlu göstergesi ada içi yapısız alan payıdır (%66–88).
- **Model v1'de kapalı avlu yok.** T3 avlu grupları U biçiminde; dördüncü kenar açık ve sıradaki grupla aralarında 6,9 m'lik boşluk var. T4 halkaları parsel parsel bölündüğü için birleşimde kapalı bir boşluk oluşmuyor. Ada içi yapısız alan payı (%70) geleneksel kasaba dokusuna yakın, Zeyrek'in (%42) çok üstünde.

### 2.6 Yakınlık: 400 m yürüyüşle ulaşılan

| Alan | Ulaşılan bina | Ulaşılan inşaat alanı (bin m²) | Ulaşılan nüfus | Kuş uçuşu 400 m'deki bina | Ağ verimi |
|---|---|---|---|---|---|
| Safranbolu Çarşı ° \* | 188 | 73 | 422 | 489 | 0,41 |
| Safranbolu Bağlar ° ‡ | 148 | 33 | 216 | 411 | 0,37 |
| Beypazarı ° | 243 | 178 | 1.262 | 572 | 0,43 |
| Fatih Zeyrek | 712 | 452 | 7.259 | 1.236 | 0,55 |
| Fatih Süleymaniye | 308 | 355 | 6.344 | 624 | 0,55 |
| Birgi ‡ | 362 | 41 | 249 | 698 | 0,52 |
| Antakya † | 1.048 | 238 | 4.035 | 1.941 | 0,52 |
| **Model v1 (600 m)** | **483** | **139** | **2.565** | **740** | **0,67** |
| **Model v1 (60 ha)** | **436** | **120** | **2.214** | **644** | **0,68** |
| Esenyurt ° | 187 | 286 | 3.652 | 385 | 0,45 |
| Başakşehir | 39 | 213 | 1.708 | 145 | 0,28 |
| Silivri | 451 | 422 | 4.691 | 831 | 0,56 |
| Konya Meram | 116 | 208 | 1.825 | 257 | 0,46 |
| Kayseri Kocasinan | 168 | 217 | 4.239 | 311 | 0,55 |
| Ankara Mamak TOKİ ‡ | 146 | 250 | 13.123 | 312 | 0,49 |

Okuma:
- **Kapı sayısında geleneksel önde.** Zeyrek'te bir kişi kapısından 5 dakikalık yürüyüşte 712 binaya ulaşıyor; Antakya'da 1.048. Çağdaş dokularda 39–451. Model v1'de 483.
- **Nüfusta çağdaş önde olabilir.** Ulaşılan nüfusta durum farklı: Mamak TOKİ (13.123) ve Esenyurt (3.652), bina sayısı az olsa da yükseklik sayesinde çok insana ulaşıyor. Geleneksel dokunun avantajı **nüfus** değil **kapı sayısı**: dükkân, atölye, mescit ve komşu için çok sayıda ayrı giriş.
- **Ağ verimi.** Model v1'in ağ verimi (0,67) bütün alanlardan yüksek. Izgara ve diyagonaller kuş uçuşu mesafeyi iyi karşılıyor. Başakşehir 0,28 ile en düşük: büyük süper adalar ve site içi çıkmazlar. Araç ağında çıkmaz payı %28.

### 2.7 Geleneksel dokunun zaafları

Bu ölçüler geleneksel dokuyu romantize etmemek için de kullanılmalı:

1. **Afet ve acil erişim.**
   - Antakya'da sokak örneklerinin %27'sinde, Süleymaniye'de %23'ünde, Zeyrek'te %12'sinde iki cephe arası 6 m'nin altında.
   - Bu sokaklarda itfaiye merdivenli aracı ve ambulans dönüşü zor [DY]. Çökme durumunda enkaz sokağı kapatıyor; enkaz yayılımı yapı yüksekliğinin yarısı kadar varsayılırsa H/W > 1 olan sokaklar tamamen kapanır [DY, kaba kural].
   - Antakya 2023 bunun en ağır örneği oldu; ancak bu çalışmada yıkım oranı ölçülemedi (§1.2).
   - Yoğun dokuda yapı stoku eski. İstanbul'daki ahşap ev dokusunda yangın riski tarihsel olarak yüksek [DY].
2. **Erişilebilirlik.**
   - Yoğun dokularda çıkmaz payı araç ağında %12–18 (Zeyrek, Beypazarı, Antakya).
   - Safranbolu, Beypazarı ve Birgi yamaçta kurulu; eğim bu çalışmada ölçülmedi.
   - OSM'de merdiven payı düşük çıktı (%0–1,2); bu muhtemelen merdivenlerin eksik haritalanmasından [DY].
   - Tekerlekli sandalye, bebek arabası ve yaşlı erişimi bu dokularda doğal olarak zor.
3. **Sıkışıklık, gün ışığı, açık alan.**
   - Zeyrek'te kişi başı yapısız alan 19 m², kamusal yeşil 1,8 m².
   - 21 Aralık öğlesinde (İstanbul, 41°K, güneş yüksekliği 25,6°) karşı cephenin zemin katının güneş alması için H/W < 0,48 gerekir [H]. Zeyrek'te sokak örneklerinin %58'inde H/W > 1; zemin katlar kışın güneş görmüyor.
   - Bu sıkışıklık büyük ölçüde geleneksel parsel üzerine 4–6 katlı apartman yapılmasından doğdu. Yani "geleneksel" dokunun bugünkü hali, ince taneli parselin aşırı katla birleşmesinin sonucu.
4. **Otopark ve servis.**
   - Dar sokaklar araç trafiğine açık; Zeyrek'te araç ağında kavşak yoğunluğu 353/km².
   - Bu dokuda park eden araç, yaya alanını ve acil erişimi tüketiyor [DY].
   - Model v1'in araç hücresi ile bölgesel otopark çözümü bu zaafı gidermeye yönelik.
5. **Korunan dokunun boşalması.**
   - Safranbolu Çarşı (28 kişi/ha) ve Beypazarı (76 kişi/ha) korunmuş ama seyrek oturulan dokular.
   - Kişi başı 135–169 m² inşaat alanı, konutların büyük kısmının konut dışı kullanıma geçtiğini düşündürüyor [DY].
   - Morfoloji tek başına mahalle hayatını garanti etmiyor.

---

## 3. Model mahalle v2 için kalibrasyon önerileri

Öneriler geleneksel dokunun **ölçülmüş iyi yanlarını** alıyor, **ölçülmüş zaaflarını** dışarıda bırakıyor. Mevzuat sınırlarına da uyuyor:
- MPYY md. 26(6)(c): gelişme alanlarında 10 m'den dar trafik yolu ve 3 m'den dar yaya yolu yok; 7 m'den dar yoldan mahreç yok [D, `tasarim_parametreleri.md` §4].

### 3.1 Sayısal öneriler

| Parametre | v1 (ölçülen) | Geleneksel (ölçülen) | Çağdaş (ölçülen) | **v2 önerisi** | Gerekçe |
|---|---|---|---|---|---|
| **Parsel cephesi / cephe modülü** | T1 6,3 m · T2 9,2 m · T3 36 m · T4 24 m; bina cephesi medyanı 6 m, cephe adımı 19 m | Bina cephesi 6–9 m; cephe adımı 13–24 m (yoğun dokuda 13–17) | 12–18 m; 39–79 m | **T1 6,5–7,5 m; T2 9–10 m; T3 ve T4 cepheleri 9–12 m'lik modüllere bölünsün** (ayrı giriş, ayrı cephe ya da ayrı parsel). Hedef cephe adımı ≤ 15–20 m | Geleneksel ritim, model v1'de T1/T2'de var, T3/T4'te yok. T1'in 6,3 m'si geleneksel alt sınırda; 3+1 için dar |
| **Bina derinliği ve tabanı** | T1 çekirdeği 6,3 × 9 m (57 m²) | Medyan taban 99–140 m²; en × boy ≈ 9 × 13–14 m | 286–475 m² | **T1 bina derinliği 11–12 m** (≈ 75–90 m² taban, genişleme payı dahil); T2 9,2 × 11 m korunsun | Geleneksel evin 9 × 13 m'lik tanesine yaklaşmak; arka bahçe derinliği ≥ 10 m kalacak biçimde |
| **Ada (yaya ağı)** | 600 m pencerede 0,35 ha; tam 60 ha'da 0,79 ha | Yoğun dokuda 0,13–0,45 ha; çevre 157–314 m | 0,29–0,79 ha | **Yaya adası ≤ 0,35–0,45 ha, çevre ≤ 280 m.** Her T1/T2 adasının uzun kenarı ortasından 4–6 m'lik bir kamusal geçit (S3) geçsin; 120 m'lik kenar 2 × 60 m olur | v1'in merkezindeki bölünme bütün adalara yayılmalı; tam 60 ha'daki 0,79 ha çağdaş ölçek |
| **Ada (araç ağı)** | 0,94–0,97 ha (eksenden), 119,7 × 62,8 m net | 0,26–0,87 ha | 0,29–1,04 ha | **Korunsun** (net 110–120 × 60–65 m) | Araç hücresi ve geçiş trafiği yok ilkesi; geleneksel dokunun "her sokağa araç" zaafını tekrarlamamak |
| **Kavşak yoğunluğu (yaya dahil)** | 212 (60 ha) – 239 (merkez) /km² | 308–467 /km² (medyan 315) | 161–409 (medyan 221) | **≥ 300 /km²**; araç ağında 110–130 /km² | Ada içi geçitlerle yaya kavşağı artar, araç kavşağı aynı kalır |
| **S2 yaşam sokağı: cephe arası** | 14,0 m (10 m yol + 2 × 2 m eşik); H/W 0,54–0,64 | Yoğun dokuda medyan 9,5–11,3 m | 16–31 m | **11–12 m** (10 m yol + 0,5–1 m eşik); Z+2 ile **H/W ≈ 0,75–0,8** | MPYY 10 m alt sınırı korunur; kapalılık hedefe (0,7–1,0) girer; kış güneşi için yönlenme v1'deki gibi D–B |
| **S3 yaya ara sokağı** | 6 m | P25 5,4–7,3 m; Antakya ve Süleymaniye'de < 6 m payı %23–27 | yok | **5–6 m cephe arası, en az 3,5 m engelsiz geçiş**; boyu ≤ 60 m, iki ucu açık; mahreç S2'den | Geleneksel "dar sokak" ölçeği; ama 4,5 m altına inmemek (acil erişim) |
| **S1 mahalle caddesi** | 19,5 m cephe arası, H/W 0,69 | Yoğun dokuda P75 18–22 m | 16–31 m | **Korunsun (18–20 m)**; köşe ve çarşı cephesinde Z+3 ile H/W ≈ 0,7–0,8 | Geleneksel dokunun en geniş sokakları zaten bu aralıkta |
| **Yapı oturumu** | Brüt %21–23; net ada içi %30 | Brüt %19–45 (medyan %30); net %31–58 | Brüt %19–36; net %21–54 | **Brüt %25–30.** Net ada içi: K3 merkez %45–55, K2 %35–40, K1 %25–30 | Daha az kat ile aynı yoğunluk; arazi tüketimi riskine (§9.10) karşı |
| **Kat profili** | Ortalama 2,8; binaların %94'ü ≤ 3 kat | Kasabalarda 1–3,4 (GHSL; muhtemelen 2–3); İstanbul'da 4,3–5,4 (yenilenmiş stok) | 4,2–10,5 | **2–4 kat korunsun**; ortalama 2,8–3,2; K3'te Z+3 payı artırılabilir; konutta 5 katın üstü yok | İstanbul örneği 4–6 katın dar sokakta H/W > 1 ve gün ışığı kaybı ürettiğini gösteriyor |
| **Brüt yoğunluk** | 119–121 kişi/ha; emsal 0,61–0,66 | 10–317 kişi/ha | 101–563 kişi/ha | **120–150 kişi/ha**; brüt emsal 0,75–0,9 | Yapı oturumundaki artışla, kat artırmadan |
| **Avlu** | Kapalı avlu 0; ada içi yapısız (net) %70 | Kapalı avlu 0,36–0,53 /ha (İstanbul), medyan 206–345 m²; ada içi yapısız %42–69 | Kapalı avlu ≈ 0 | **T3'te dördüncü kenar** kapı binası ya da 2,5–3 m'lik bahçe duvarıyla kapansın: **300–450 m² kapalı avlu, ≈ 0,5 /ha** (K2–K3). Ada içi yapısız alan payı (net) K3'te %45–55, K2'de %60–65 | Çocuğun gözetimli oyun alanı; geleneksel avlu ölçüsü (200–350 m²) |
| **Kamusal yeşil ve açık alan** | 13,2–14,2 m²/kişi; yapısız 65 m²/kişi | 0–2,5 m²/kişi (Birgi hariç); yoğun dokuda yapısız 19–22 m²/kişi | 0,4–3,3 m²/kişi | **≥ 10 m²/kişi korunsun** (geleneksel doku örnek alınmasın) | Geleneksel dokunun en zayıf yanı |
| **Yönelim ve ağ biçimi** | Tam ızgara (φ 0,94), ağ verimi 0,67 | φ 0,03–0,43; ağ verimi 0,52–0,55 | φ 0,09–0,73 | **Izgara mantığı korunsun**; eğimli arazide eş yükselti eğrisine göre bükülsün, ada boyları 50–75 m arasında çeşitlensin | Ağ verimi modelde zaten en yüksek; düzensizlik hedef değil, topoğrafyaya uyumun yan ürünü |

### 3.2 Sınamalar

1. **Arazi bütçesi.** Geçitsiz konut adalarına (≈ 40–60 ada) birer geçit eklemek ada başına ≈ 60 × 5 m = 300 m², toplam ≈ 1,2–1,8 ha tutar [H]. Sokak payı %27,6'dan ≈ %30'a çıkar; BM-Habitat'ın %30 hedefine ulaşır. Kaybedilen konutun T1 derinliği ve K3 yapı oturumu artışıyla telafi edilebileceği v2 plan modelinde sınanmalı [DY].
2. **S2 eşiği.** 0,5–1 m'lik eşik, Planlı Alanlar İmar Yönetmeliği'nin 5 m ön bahçe varsayılanına aykırı. Fıtrat Kodu'nda ve Md. 30 kapsamındaki kentsel tasarım projesinde açıkça tanımlanmalı (`fitrat_kodu_taslak.md` §7) [DY].
3. **Kapalı avlu ve deprem.** Dördüncü kenarı kapatan kapı binası, avluya acil durum aracı girişini engellememeli. En az 3,5 m genişlik ve 4 m yükseklikte bir kapı altı geçit bırakılmalı [DY].
4. **Sonraki ölçüm.** v2 çizildiğinde aynı betikle ölçülmeli (`MODEL_ALANLAR` model geometrisini doğrudan okur). Önerilen hedefler §3.1'deki tabloyla karşılaştırılmalı.

---

## 4. Sınırlılıklar

1. **Örneklem küçük ve amaçlı.** Her türden 6–7 alan, her alanda tek bir 600 m kare var. Ölçüler kare konumuna duyarlı: Zeyrek karesi Fatih Camii külliyesinin bir kısmını, Süleymaniye karesi külliyeyi içeriyor. "Geleneksel medyan" bir istatistik değil, bir özet.
2. **Bina verisi karışık.**
   - Safranbolu Çarşı ve Beypazarı'nda binaların %95–97'si Microsoft ayak izi. Bu izler sokak çizgileriyle birkaç metre kayık olabilir ve bitişik binaları birleştirebilir (Silivri'de sayı OSM'nin %38'i).
   - Bu iki alanda yapı oturumu güvenilir (±%15). Bina sayısı ve cephe ölçütleri daha az güvenilir.
3. **Kat ve yükseklik.** Kat etiketi olan bina çok az. GHSL ANBH 2018, 5 katın üstünde katı yarı yarıya düşük, küçük kasabalarda tek katın altında tahmin ediyor. Emsal, H/W ve kişi başı inşaat alanı bu yüzden belirsiz; işaretli alanlarda alt sınır.
4. **Nüfus modelli.** GHS-POP 2020, nüfus sayımını yapı hacmine dağıtır; konut sayımı değildir. Turistik ve ticari dokularda (Safranbolu Çarşı, Fatih) oturan nüfusu yanlış verebilir. Konut yoğunluğu ilçe ortalama hane büyüklüğüyle kabaca türetildi.
5. **Sokak ağı.**
   - OSM'de Safranbolu Çarşı'nın iç sokakları eksik; diğer kasabalarda da merdivenler ve dar geçitler eksik olabilir. Kaldırımı ayrı çizilmiş caddeler kaldırımlar çıkarılarak ölçüldü. Çift yönlü bulvarlar iki kez sayılıyor.
   - Cephe arası mesafe ve H/W ışın örneklemesinden geliyor; kamusal yol genişliği değil, bina cephesinden cepheye mesafedir. Bahçe duvarları ölçülmedi.
6. **Topoğrafya yok.** Eğim, sokak eğimi ve merdivenli bağlantılar ölçülmedi. Safranbolu, Beypazarı ve Birgi'de erişilebilirlik zaafı muhtemelen tablolarda göründüğünden büyük.
7. **Antakya geçmişi gösteriyor.** Ölçüm deprem öncesi dokunun kaydıdır; bugünkü durumu yansıtmaz.
8. **Model penceresinde kenar etkisi.** Model mahallenin dışında bina ve yol yok. 600 m pencerenin kenarındaki binalarda 400 m yakınlık az sayılıyor. Model tam ızgara ve düz arazide çizildi.

## 5. Yeniden üretim

```
cd 03_VERI/kod
python morfoloji_olcum.py            # kesit (ilk çalıştırmada ≈ 3 dk) + ölçüm (≈ 1 dk) + çizim
python morfoloji_olcum.py --cizim    # yalnız çizim
```

Gerekenler: Python 3.11, pyosmium 4, geopandas, shapely ≥ 2, rasterio, networkx, scipy, matplotlib.
- **Alan değiştirme.** Alan eklemek ya da kareyi kaydırmak için betiğin başındaki `ALANLAR` listesi düzenlenir; kesit yeniden çıkarılır.
- **Deneme.** `MORFOLOJI_ALANLAR="G4,C2"` ile alt küme çalıştırılır. `MORFOLOJI_KESIT` ile hazır bir kesit verilir.
- **Model v2.** v2 plan modeli aynı arayüzle (`plan_modeli.plan_kur()` ve `ag_kur()`) hazırlanırsa `MODEL_ALANLAR` doğrudan v2'yi ölçer.

### Kaynaklar

- OpenStreetMap katkıcıları, Türkiye kesiti, Geofabrik, 25.10.2026 (ODbL).
- Microsoft, Global ML Building Footprints, sürüm 2026-02-03: https://github.com/microsoft/GlobalMLBuildingFootprints (ODbL).
- Pesaresi, M. ve ark., GHSL Data Package 2023 (GHS-BUILT-H R2023A, GHS-POP R2023A), Avrupa Komisyonu JRC.
- Boeing, G. (2019), "Urban spatial order: street network orientation, configuration, and entropy", *Applied Network Science* 4: 67 [İ].
- Berghauser Pont, M. ve Haupt, P. (2010), *Spacematrix: Space, Density and Urban Form*, NAi Publishers [DY].
- Proje içi: `07_TASARIM_CIZIM/tasarim_parametreleri.md`, `07_TASARIM_CIZIM/model_mahalle_v1.md`, `02_LITERATUR/ornek_uygulamalar.md` §3.1–3.2, `09_RAPORLAR/08_pilot_secimi.md`, `09_RAPORLAR/09_faz2_sentez.md`.
