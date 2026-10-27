# Model Mahalle v1 — Vaziyet Planı, Kesitler, Tipolojiler ve Sayısal Doğrulama

**Proje:** TR TAMİRAT
**Bölüm:** 07_TASARIM_CIZIM · İP6 (model mahalle ve tasarım)
**Tarih:** 26 Ekim 2026 · **Sürüm:** v1
**Girdi:** `tasarim_parametreleri.md` §9 (taslak program 0.1) · `02_LITERATUR/ornek_uygulamalar.md` · `09_RAPORLAR/03_ilce_paneli_il_ici.md`
**Eş belge:** `fitrat_kodu_taslak.md` (biçim temelli imar kodu)
**Kod:** `model_mahalle/kod/` · bütün çıktılar için `python hepsini_calistir.py`

İşaretler projedeki gibidir: **[D]** doğrulandı · **[İ]** ikincil · **[DY]** doğrulanmadı · **[H]** bu çalışmada hesaplandı. Bu belgedeki bütün plan sayıları [H] türündedir. Hepsi çizimin poligonlarından ve yaya ağından hesaplanmıştır; elle girilmiş toplam yoktur.

---

## Özet

- **Ölçek ve yoğunluk.** 60 ha'lık model mahallede (800 × 750 m) **2.222 konut** ve **7.110 kişi** var. Hedef 2.250 konut ve 7.200 kişiydi (fark −%1,2). Brüt yoğunluk **119 kişi/ha** (hedef 120), net konut yoğunluğu **81 konut/ha** (bant 50–90).
- **İnsan ölçeği.** Konutların **%70'i** en fazla 3 katlı, **%97,5'i** en fazla 4 katlı binalarda. 5 katlı binada oturan pay %2,5; 5 katın üzerinde konut yok. Binaların %93'ü en fazla 3 katlı.
- **Erişim (yaya ağı mesafesi).** Konutların %100'ü şunlara yakın: ≥ 0,5 ha yeşile 300 m, anaokulu ya da kreşe 400 m, bakkal ya da dükkâna 300 m, otobüs durağına 400 m, açık spor sahasına 500 m, otoparka 400 m. İlkokula 500 m içinde kalan pay **%96,8** (en uzak 553 m). Kademeli ibadet kuralını (mescit 150 / küçük cami 250 / semt camii 400 m) sağlayan pay **%99,3**.
- **Yeşil ve sokak.** Kamusal yeşil **13,2 m²/kişi** (hedef ≥ 10). Sokak ağı **25,7 km/km²**. Kavşak yoğunluğu araç ağında **117/km²**, yaya dahil **203/km²**.
- **Yapı ve otopark.** 86 avlu grubu ve 106 bahçe grubu var (toplam 192; hedef 190–280). 4 mobilite noktasında **0,56 yer/hane** bölgesel otopark var; parsel içinde otopark yok.
- **Düzeltilen tutarsızlıklar.** Taslak programdaki bazı hedefler 60 ha'lık kare alanda birlikte sağlanamıyordu (bkz. §3.3):
  - tek ilkokul için 500 m,
  - 8 mescit için 150 m,
  - 2 otopark için 400 m.
  Plan, ilkokulu meydana değdirerek, otoparkı 4 kapıya dağıtarak ve mescitleri ağ üzerinde seçerek düzeltildi. Kalan farklar raporlandı.
- **Gerekçe.** Faz 2'de mekânın doğurganlığa doğrudan etkisi küçük çıktı. Bu yüzden tasarımın gerekçesi sağlık, çocuğun bağımsızlığı, komşuluk, kuşaklar arası yakınlık ve deprem güvenliğidir (§7).

---

## 1. Çizimler

Bütün dosyalar `07_TASARIM_CIZIM/model_mahalle/` altındadır. PNG 150 dpi; SVG vektördür.

| Dosya | İçerik |
|---|---|
| `vaziyet_plani.png` · `.svg` · `.dxf` | 60 ha vaziyet planı. Çizimde şunlar var: sokak hiyerarşisi, 60 ada ve 791 parsel, konut tipleri, merkez, 8 komşuluk birimi, mescitler, küçük camiler, yeşil sistem, 4 mobilite noktası, 11 durak. Ayrıca lejant, kuzey oku, ölçek çubuğu, 400/500 m kuş uçuşu başvuru halkaları ve Fıtrat Kodu bölgeleri (transect) haritası bulunur. Sağ panelde çizimden hesaplanan ana sayılar yer alır. DXF katmanlıdır (yol, parsel, bina, donatı, yeşil, sembol; ezdxf denetimi 0 hata) |
| `erisim_analizi.png` · `.svg` | Her konut için kapıdan en yakın donatıya **ağ üzerinden** yürüme mesafesi. Sekiz harita: ilkokul, ibadet kademeleri, ≥ 0,5 ha yeşil, durak, anaokulu ya da kreş, ASM, dükkân, otopark. Altında dört konut ağırlıklı dağılım (histogram) var |
| `sokak_kesitleri.png` · `.svg` | Dört tip, aynı ölçekte: toplayıcı yol (24 m), S1 mahalle caddesi / çarşı (18 m), S2 yaşam sokağı (10 m), S3 yaya ara sokağı (6 m). Şerit genişlikleri, kaldırım, ağaç ve bina yüksekliği gösterilir. Her kesitte H/W oranı ve 21 Aralık (25,6°) ile 21 Mart (49,0°) öğle güneş ışınları çizilidir (İstanbul 41°K) |
| `tipoloji_T1_buyuyebilen_ev.png` | Parsel planı, 3 kat planı (çekirdek ve genişleme), kesit, aşamalı alan tablosu |
| `tipoloji_T2_cok_kusakli_ev.png` | Zeminde büyükler dairesi (2+1, eşiksiz), üstte ayrı girişli 4+1 dubleks. Parsel planı, 3 kat planı, kesit, alan tablosu |
| `tipoloji_T3_avlu_grubu.png` | 12 haneli avlu grubu. Zemin planı, üst kat planı (3 × 3+1 oda ayrıntısı), iki grubu kesen ada kesiti, alan tablosu |
| `tipoloji_T4_cevre_adasi.png` | 24 m'lik dükkânlı çubuk parseli. Zemin (2 dükkân), normal kat (2+1 · 1+1 · 2+1), adadaki yeri, ada kesiti, alan tablosu |
| `deprem_hizli_uygulama.png` · `.svg` | Prefabrik Z+1 → Z+2 kurgusu. Modüler aksonometri, şematik yapı kesiti, aşamalama takvimi ve aynı planın üç kat senaryosu |
| `metrikler.csv` | 84 gösterge. Sütunlar: plan değeri, hedef, kaynak, durum (uyumlu / yakın / sapma), not |

Kod dosyaları (`model_mahalle/kod/`):

| Dosya | Görevi |
|---|---|
| `plan_modeli.py` | Bütün geometri, yaya ağı ve zemin kat donatılarının seçimi |
| `metrikler.py` | Doğrulama ve CSV |
| `vaziyet_plani.py`, `erisim_analizi.py`, `sokak_kesitleri.py`, `konut_tipolojileri.py`, `deprem_hizli_uygulama.py` | Çizimler |
| `ortak.py` | Renk dili (`ayni_yogunluk_uc_bicim.py` ile ortak), Türkçe sayı biçimi, çizim yardımcıları |

---

## 2. Plan kurgusu

### 2.1 Alan ve sokak hiyerarşisi

- **Alan.** 800 × 750 m = 60,0 ha. Çevredeki 24 m'lik toplayıcı yolun iç yarısı brüt alana dahildir. Kuzey ve batı kenarı yeşil kuşağa, güney ve doğu kenarı komşu mahalleye (semt) bakar.
- **Toplayıcı yol (S0, 24 m).** Mahallenin dışındadır. Semt otobüs hattı, bisiklet yolu ve iki sıra ağaç taşır.
- **S1 mahalle caddesi (18 m).** Artı biçiminde, merkezde meydanla kesişir. K–G kolunda mahalle içi otobüs hattı (3 durak) var. Meydanda **araç filtresi** bulunur: yalnız otobüs, bisiklet ve acil araç geçer. Böylece mahalle dört **araç hücresine** bölünür; araç hücreye toplayıcıdan girer ve aynı yerden çıkar (Houten ve süper blok mantığı).
  - Merkez adalarına bakan D–B kesimi yaya çarşısı ve haftalık pazar yeridir.
- **S2 yaşam sokağı (10 m).** Paylaşımlı yüzeydir, en fazla 20 km/s. Bir yanında ağaç ve kısa park cepleri vardır.
- **S3 geçitleri (6 m).** Avlu grubu adalarını K–G yönünde keser.
- **4 yeşil diyagonal (8 m).** Köşelerden meydana uzanır. İşlevleri:
  - Köşe konutlarının merkeze ağ mesafesini ≈ 750 m'den ≈ 520 m'ye indirir.
  - Okul yoludur; merkez parkını ve küçük camileri birbirine bağlar.
  - Kestikleri adalarda kalan üçgenler cep parkı ve kapı önü oyun alanı oldu.
- **Ada.** 119,7 × 62,8 m (çevre 365 m). Uzun kenarlar D–B yönündedir; böylece cepheler güneye ve kuzeye bakar.

### 2.2 Merkez

Merkez, meydanı çevreleyen 8 adadır:

| Konum | Donatı | Not |
|---|---|---|
| Kuzeybatı | Semt camii ve avlusu (0,48 ha); aile sağlık merkezi ve eczane (0,17 ha) | Caminin avlusu meydanın ve diyagonalin kavuştuğu köşeye açılır |
| Kuzeydoğu | Çarşı ve kapalı pazar (0,48 ha); kuzey anaokulu | — |
| Güneydoğu | Mahalle konağı (0,52 ha; muhtarlık, meclis salonu, kütüphane, gençlik ve aile merkezi, yaşlı günevi, hamam) | — |
| Güneydoğu | **İlkokul** (1,13 ha); güney anaokulu yerleşkenin köşesinde | İlkokul meydanın güney kenarına değer |
| Güneybatı | Merkez parkı (1,96 ha) ve açık semt spor alanı (0,50 ha) | Diyagonal parkın içinden geçer |

### 2.3 Komşuluk birimleri ve yeşil

- **Komşuluk birimleri.** Her çeyrek kendi diyagonaliyle iki üçgen birime bölünür (KB-1…KB-8). Birimler 214–328 hanedir. Küçük camiler diyagonal üzerinde, iki birimin ortak sınırında durur.
- **Her birimde bulunanlar:**
  - 0,50 ha'lık bir komşuluk yeşili ve içinde 30 × 18 m çok amaçlı saha,
  - en az bir zemin kat mescidi, bakkal-fırın ve su-oturma noktası (çeşme).
- **Köşeler.** İki köşede bostan, birinde ortaokul (komşu mahalleyle ortak), birinde kenar parkı var. Teknik altyapı köşe kırpıntılarındadır.

### 2.4 Mobilite noktaları

Bölgesel otopark, S1 caddelerinin toplayıcıya bağlandığı dört kapıda yer alır. Dört yapı fırıldak düzeninde dizilir; her biri Z+3'tür ve toplam ≈ 1.240 araç alır. Zemin katlarında market, bisiklet atölyesi ve kargo noktası var. Durak da bu noktalardadır. Taslak programda "kuzeydoğu ve güneybatı kenarında 2 otopark" öngörülmüştü; bu dört kapıya dağıtıldı (§3.3).

### 2.5 Fıtrat Kodu bölgeleri (transect)

| Bölge | Yeri | Tipoloji |
|---|---|---|
| K1 köy kenarı | Yeşil kuşak kenarı | T1, T2, alçak avlu grubu |
| K2 mahalle genel | Birimlerin içi | — |
| K3 mahalle merkezi | Cadde ve meydan çevresi | T3 Z+3, T4 |
| K4 semt çarşısı | Güney ve doğu kapıları | T4, mobilite noktası |

### 2.6 Zemin kat donatılarının yerleşimi

Mescit, kreş, bakkal ve çeşmenin konumu elle verilmedi. Yaya ağı üzerinde **açgözlü kapsama** ile seçildi: her adımda hedef yarıçap içinde henüz karşılanmamış en çok konutu kapsayan aday alınır. Mescit, bakkal ve çeşme için her komşuluk biriminde en az bir tane zorunludur.

- **Adaylar:** T3 ve T4 zemin katları, mobilite noktaları, ≥ 300 m²'lik cep parkları (bağımsız küçük mescit).
- **Bedel:** Seçilen zemin katlar konut sayısından düşüldü (mescit 1, kreş 3, bakkal 1 konut).
- **Sonuç:** 16 mescit (4'ü cep parkında bağımsız yapı), 5 kreş, 8 bakkal-fırın, 10 çeşme.

---

## 3. Sayısal doğrulama

Tam tablo `model_mahalle/metrikler.csv` dosyasındadır (84 satır). Hedefler `tasarim_parametreleri.md` §9'dan alınmıştır.

### 3.1 Ana metrikler

| Gösterge | Plan (çizimden) | Hedef (§9) | Durum |
|---|---|---|---|
| Brüt alan | 60,0 ha | 60 ha | uyumlu |
| Konut | **2.222** | 2.250 | uyumlu (−%1,2) |
| Nüfus (3,2 kişi/hane) | **7.110** | 7.200 (6.000–8.000) | uyumlu |
| Brüt yoğunluk | 118,5 kişi/ha · 37,0 konut/ha | 120 · 37,5 | uyumlu |
| Net konut alanı | 27,3 ha | 32,0 ha | yakın (−%15) |
| Net konut yoğunluğu | 81 konut/ha | ≈ 70 (50–90) | uyumlu |
| T1 · T2 · T3 · T4 konut | 447 · 470 · 1.093 · 212 | 650 · 400 · 1.050 · 150 | karma farklı (§3.3) |
| ≤ 3 katlı binada oturan | %70,1 | ≈ %70 | uyumlu |
| ≤ 4 katlı binada oturan | %97,5 | ≈ %93 | uyumlu |
| 5 katlı binada oturan | %2,5 | ≤ %7 | uyumlu |
| 3+1 ve üstü · 2+1 · 1+1 | %58,9 · %35,2 · %5,9 | ≥ %55–60 · ≈ %20 · %5–10 | uyumlu (2+1 fazla) |
| Çok kuşaklı kullanıma uygun | %31 | ≥ %15 | uyumlu |
| Konut dışı kat alanı payı | %14,9 | %15–25 | yakın |
| Sokak, yaya yolu ve meydan | 16,6 ha (%27,6) | 15,0 ha (%25) | yakın (+%11) |
| Kamusal yeşil | 9,41 ha · 13,2 m²/kişi | 7,2 ha · ≥ 10 m²/kişi | hedefin üstünde |
| Merkez parkı · komşuluk yeşilleri | 1,96 ha · 8 × 0,50 ha (+ kenar parkı 0,50) | 2,0 · 8 × 0,5 | uyumlu |
| Cep parkı · bostan | 1,92 ha · 1,01 ha | 0,4 · 0,8 | fazla (diyagonal kırpıntıları) |
| Eğitim alanı | 2,55 ha · 3,6 m²/kişi; ilkokul arsası 11.312 m² | 2,52 ha · 3,5 (EK-2) | uyumlu |
| İbadet · ASM · konak · çarşı | 0,88 · 0,17 · 0,52 · 0,48 ha | 0,76 · 0,15 · 0,36 · 0,50 | uyumlu / konak fazla (hamam dahil) |
| Bölgesel otopark | 1,26 ha · 1.243 araç · 0,56/hane | 0,65 ha · 0,5–0,7/hane | oran uyumlu; alan 2 katı (4 yapı) |
| Sokak ağı · kavşak yoğunluğu | 25,7 km/km² · 117 (araç) / 203 (yaya dahil) /km² | ≥ 18 (≈25) · ≥ 80–120 | uyumlu |
| Avlu + bahçe grubu | 192 (8–15 hane) | 190–280 (8–12 hane) | uyumlu |
| Komşuluk birimi | 214–328 hane (685–1.050 kişi) | 150–300 hane | KB-3 ve KB-7 sınırın biraz üstünde |
| Ağaç örtüsü (20 yıl, kaba tahmin) | %25 | ≥ %30 | sapma |

### 3.2 Erişim: her konut için ağ mesafesi

| Donatı | Hedef | Hedefi sağlayan konut | Medyan | En uzak | MPYY / dış ölçüt |
|---|---|---|---|---|---|
| İlkokul | ≤ 500 m | **%96,8** | 323 m | 553 m | ≈ 500 m |
| Ortaokul | ≤ 1.000 m | %100 | 623 m | 958 m | ≈ 1.000 m |
| Anaokulu ya da kreş | ≤ 400 m | %100 | 194 m | 398 m | (yalnız anaokulu: ≤ 500 m'de %98,8) |
| Mescit | ≤ 150 m | %75,4 | 124 m | 230 m | kademeli kural: **%99,3** |
| Küçük cami · semt camii | ≤ 250 · ≤ 400 m | %61,8 · %69,2 | 223 · 341 m | 472 · 561 m | kademe olarak |
| Aile sağlık merkezi | ≤ 500 m | %96,5 | 350 m | 558 m | ≈ 500 m |
| ≥ 0,5 ha yeşil | ≤ 200 m (≤ 300 m) | %96,1 (%100) | 85 m | 245 m | DSÖ 300 m |
| Merkez parkı (2 ha) | ≤ 500 m (≤ 800 m) | %98,4 (%100) | 274 m | 552 m | ANGSt |
| Kapı önü oyun alanı (avlu, ortak şerit ya da cep parkı ≤ 150 m) | — | %100 | — | — | yalnız kamusal cep parkı: %85 |
| Açık spor sahası (herhangi) | ≤ 500 m | %100 | 168 m | 349 m | 0,5 ha semt alanı: %75 |
| Bakkal, fırın ya da dükkân | ≤ 300 m | %100 | 89 m | 298 m | — |
| Otobüs durağı | ≤ 300 m (≤ 400 m) | %99,1 (%100) | 158 m | 311 m | — |
| Meydan ve çarşı | ≤ 400 m (≤ 500 m) | %73,9 (%98,8) | 331 m | 516 m | — |
| Mahalle konağı | ≤ 500 m | %95,1 | 339 m | 568 m | — |
| Bölgesel otopark | ≤ 400 m | %100 | 188 m | 350 m | — |
| Su ve oturma noktası | ≤ 250 m | %100 | 140 m | 245 m | — |

### 3.3 Tasarım parametreleriyle tutarsızlıklar ve yapılan düzeltmeler

Planın ilk kurgusu (v0) ölçüldü, sonra düzeltildi. v0'da ilkokul meydandan ≈ 120 m güneydeydi, köşelerde 2 otopark vardı ve mescitler elle yerleştirilmişti.

| Konu | v0 ölçümü | Neden | v1 düzeltmesi | v1 sonucu |
|---|---|---|---|---|
| İlkokul ≤ 500 m | %87,9 (en uzak 620 m) | Kuzey yarıdakiler meydanı geçip ≈ 120 m daha yürüyordu | Okul yerleşkesi meydanın güney kenarına değecek biçimde büyütüldü (diyagonal kırpıntısı ve iki S2 parçası okula katıldı); okulun meydanda kapısı var | %96,8 (553 m) |
| Otopark ≤ 400 m | %53,6 (2 köşe otoparkı) | İki köşeden merkeze ağ mesafesi ≈ 520 m | 4 mobilite noktası caddelerin toplayıcıya bağlandığı kapılarda | %100; 0,56 yer/hane |
| Mescit ≤ 150 m / kademeli | %77,9 / %96,0 (24 elle konmuş mescit) | 150 m ağ yarıçapı ≈ 4,5 ha kapsar; 8 mescit 60 ha'yı kapsayamaz | Ağ üzerinde açgözlü seçim; 16 mescit, 4'ü cep parkında bağımsız | %75,4 / %99,3 |
| Spor ≤ 500 m | %75 | Tek spor alanı merkezin batısında | Her komşuluk yeşiline 30 × 18 m saha; ortaokul sahası okul dışı saatlerde açık | %100 (herhangi saha) |
| Su ve oturma noktası ≤ 250 m | %76,6 | Birim başına 1 çeşme yetmiyor | Açgözlü seçimle 10 çeşme | %100 |
| Konut dışı kat alanı | %9,7 | Neredeyse saf konut | Caddeye bakan T3 uçlarında zemin dükkân, mobilite noktası zemininde market, çarşı Z+2, okul ve camide gerçekçi bina alanı | %14,9 |
| Kat profili ≤ 3 kat | %77 → %64 (ara) → %70 | Konut sayısı ile kat sınırı arasında denge | T1 parseli 6,65 → 6,30 m; T3 Z+3 yalnız caddeler boyunca | %70,1; 2.222 konut |

**60 ha'lık kare alandan doğan, kalan sınırlar:**

1. **Tek ilkokul ve 500 m.** Kare 60 ha'da merkezden köşeye kuş uçuşu ≈ 530 m. Diyagonallerle bile en uzak konut 553 m'de kaldı. %100 için şu seçenekler var:
   - alan ≈ 52–55 ha'ya indirilir,
   - kenarlar yuvarlatılır,
   - ikinci küçük bir ilkokul şubesi açılır.
   Aynı sınır ASM (%96,5) ve mahalle konağı (%95,1) için de geçerli. Taslak programın kendisi de "en uzak konuttan merkeze ≈ 550–650 m" diyordu (§9.2).
2. **Mescit 150 m.** Ağ mesafesiyle 150 m herkes için ancak ≈ 25–30 mescitle sağlanabilir. Plan, MPYY'nin kademeli yapısını ve PAİY md. 53'ün mantığını izleyen kademeli kuralı (%99,3) esas aldı.
3. **Arazi bütçesi.** Diyagonaller ve 4 mobilite noktası sokak ve otopark payını büyüttü. Net konut alanı 32 ha yerine 27,3 ha oldu; buna karşın net yoğunluk 81 konut/ha ile bandın içinde kaldı. Diyagonal kırpıntıları 1,9 ha cep parkı üretti; bu yüzden yeşil hedefin üstünde.
4. **Tipoloji karması.** T1 payı %20'ye düştü (hedef %29), T3 payı %49 (hedef %47), T4 payı %10 (hedef %7). Nedeni: diyagonallerin kestiği adalar T1 sıralarından parsel düşürdü ve çarşı cephesi T4 gerektirdi. T2 (çok kuşaklı) %21 ile hedefin üstünde.
5. **2+1 payı** %35 (hedef ≈ %20). T3 yan kanatlarındaki dubleksler ve T4 daireleri 2+1. 3+1 ve üstü yine %59.

---

## 4. Sokak kesitleri

| Kesit | Kamusal yol | Cephe arası W | Saçak H (G / K) | H/W | 21 Ara. öğle gölgesi · karşı cephede gölge | 21 Mar. öğle gölgesi · karşı cephe |
|---|---|---|---|---|---|---|
| A–A Toplayıcı | 24,0 m | 24,0 m | 13,5 / 13,5 m | 0,56 (hedef 0,40–0,67) | 28,2 m · 2,0 m'ye kadar | 11,7 m · güneşte |
| B–B S1 cadde / çarşı | 18,0 m | 19,5 m | 13,5 / 13,5 m | 0,69 (hedef 0,7–0,8) | 28,2 m · 4,2 m'ye kadar | 11,7 m · güneşte |
| C–C S2 yaşam sokağı | 10,0 m | 14,0 m | 9,0 / 6,0 m (son durum 9,0) | 0,54 / 0,64 son durum (hedef 0,7–1,0) | 18,8 m · 2,3 m'ye kadar | 7,8 m · güneşte |
| D–D S3 yaya ara sokağı | 6,0 m | 6,0 m | 6,0 / 9,0 m | 1,25 (hedef 1,0–1,5) | 12,5 m · 3,1 m'ye kadar | 5,2 m · güneşte |

**Okuma.**

- **Mart.** Dört kesitte de 21 Mart öğlesinde karşı cephe tümüyle güneşte.
- **Aralık.** 21 Aralık öğlesinde S2'de karşı cephenin yalnız zemin kat pencere altı gölgede kalır. S1'de ise zemin kat (dükkân) gölgededir.
- **S2'nin H/W oranı** hedefin biraz altında. 2,0 m'lik ön eşik ile iki tarafta Z+2 cephe 0,64 veriyor. 0,7'ye çıkmak için iki seçenek var: ön eşik 1,5 m'ye indirilir ya da S2'nin bir tarafında T3 Z+2 sokak kanadı kullanılır. Fıtrat Kodu K2'de ön eşiği 1,5–2,5 m bırakır.
- **MPYY md. 26(5)(b).** Bu maddenin K formülü S2 için 14,5 m, S1 için 20,5 m isterdi. Formül yalnız kat artıran plan değişikliklerinde aranır (doğrulanmalı; bkz. `fitrat_kodu_taslak.md` §7).

## 5. Konut tipolojileri

| Tip | Parsel | Kat | Hane ve oda | Net / brüt | Emsal · oturum | Plandaki sayı |
|---|---|---|---|---|---|---|
| T1 Büyüyebilen sıra ev | 6,30 × 27,4 m (173 m²) | Z+1 çekirdek → Z+2 + arka oda | 1 · aşama 1: 2+1 (101 / 113 m²) → son: 4+1 + büyükler odası | 173 / 195 m² | 1,13 · %47 | 447 konut |
| T2 Avlulu çok kuşaklı ev | 9,21 × 27,4 m (252 m²) | Z+2 | 2 · zemin 2+1 büyükler (78 / 85 m², eşiksiz) + 4+1 dubleks (194 / 219 m², ayrı giriş) | 280 / 304 m² | 1,20 · %40 | 235 bina, 470 konut |
| T3 Avlu grubu | 36 × 31,4 m (1.130 m²) | Sokak kanadı Z+2 (K3'te Z+3), yan kanatlar Z+1 | 12 · zemin 2+1 erişilebilir + 1+1; üst katlarda 6 × 3+1; yan kanatlarda 4 × 2+1 dubleks | ≈ 1.050 / 1.409 m²; ortak avlu ≈ 440 m² | 1,25 · %48 | 86 grup, 1.093 konut |
| T4 Çevre adası çubuğu | 24 × 27,4 m (658 m²) | Z+3 (köşe Z+4), zemin 4,5 m | 2 dükkân + 9 daire (her katta 2+1 · 1+1 · 2+1) | ≈ 920 / 1.152 m² | 1,75 · %44 | 23 parsel, 212 konut |

**Tasarım kararları.**

- **T1.** Çekirdek teras çatılıdır; statik sistem son duruma göre baştan hesaplanır. Arka oda zeminde eşiksizdir (büyükler odası ve duş).
- **T2.** T12 adalarının kuzey sırasına konur; böylece avlu güneydedir. Güneydeki T1'in son durumdaki gölgesi 21 Aralık'ta bile ortak şeritte biter.
- **T3.** Kapı altı geçitten girilir. Güney sıradaki grupların avlusu kışın gölgede kalır, bu yüzden oyun alanı avlunun kuzey ucuna konur. Z+3'te asansör zorunludur.
- **T4.** Ada başına 5 parsel, yani 5 ayrı yapımcı olur. 2+1'ler çift cephelidir. Dükkânlı zemin kat yumuşak kat riski taşır; çekirdek perdeleri zemine kadar kesintisiz iner.

## 6. Deprem bölgesi için hızlı uygulama sürümü

Aynı plan, aynı sokak ve aynı avlu grubu kullanılır; yalnız kat ve yapım kurgusu değişir.

- **Yapım.** Konutlar 3,6 m'lik modüllerle kurulur. Sistem prefabrik betonarme panel, ya da hafif çelik veya ahşap karkas olabilir; seçenek doğrulanmalıdır. Temel son durum yüküne göre radye olarak yapılır.
- **Aşama 1 (0–12 ay).** Z+1 çekirdekler kurulur: T3'te yan kanatlar tek katlı, sokak kanadı Z+1. **Önce mahalle merkezi** gelir: okul, ASM, mescit ve çarşı modüler olarak konutlardan önce kurulur.
- **Aşama 2 (1–3 yıl).** Onaylı projeyle, aynı panellerle Z+2'ye büyünür. Bağlantı filizleri ve statik hesap baştan hazırlanmıştır.

Aynı planın üç kat senaryosu:

| Senaryo | Konut | Nüfus | Brüt kişi/ha | En yüksek kat |
|---|---|---|---|---|
| Aşama 1 (Z+1) | 1.707 | 5.463 | 91 | 2 kat |
| Aşama 2 (Z+2 tavanı) | 2.031 | 6.500 | 108 | 3 kat |
| Kalıcı plan (Z+3, köşe Z+4) | 2.222 | 7.110 | 119 | 5 kat (köşe) |

**Not.** Aşama 1'de brüt yoğunluk 100 kişi/ha'nın altına iner. MPYY md. 12(4) bu eşiğin altındaki yerleşimlerde yürüme mesafelerinin artırılabileceğini söyler [D]; bu dönem o kapsama düşebilir (doğrulanmalı).

**Gerekçe.** 6 Şubat sonrasında devlet "zemin dahil 3–4 kat" ilkesini benimsedi [K]. Literatürde ise tip proje tekrarı ve mahallelerin birleştirilmesi riski not edilmişti (`ornek_uygulamalar.md` §3.3). Hızlı sürüm bu ikisini birleştirir: konteyner kent yerine kalıcı ama hızlı, tek tip yerine avlu grubu ve küçük parsel.

Süreler, yapı sistemleri ve yoğunluk yorumu tahmindir; TBDY 2018 ve zemin etüdüyle doğrulanmalıdır.

---

## 7. Tasarım gerekçeleri

Faz 2'nin bulgusu bu planın savunusunu değiştirdi. İl içinde bina yüksekliğinin doğurganlıkla ham ilişkisi belirgindi; ama farkın ≈ %80'i kadın eğitiminden geliyordu. Kalan etki bir kat başına ≈ −0,03 çocuk ve modele duyarlı (`09_RAPORLAR/03_ilce_paneli_il_ici.md`). Bu yüzden model mahalle bir **doğurganlık vaadi** olarak değil, aile hayatını kolaylaştıran bir **zemin** olarak savunulur. Gerekçeler şunlardır:

| Hedef | Planda karşılığı | Kanıt düzeyi (literatür dosyalarından) |
|---|---|---|
| **Sağlık** | Her konuta 300 m içinde ≥ 0,5 ha yeşil; 13,2 m²/kişi; kapıya kadar ağaç; mahalle içinde ≤ 20–30 km/s; geçiş trafiği yok | DSÖ 300 m ölçütü [İ]; 3-30-300 ve Barselona ruh sağlığı bulgusu [D]; süper blok NO₂ düşüşü [D] |
| **Çocuğun bağımsızlığı** | Okul yolu araç yolu geçmeden, diyagonal ve S2 üzerinden; okul sokağı; avluda ve ortak şeritte kapı önü oyun (%100); kreş ya da anaokulu ≤ 400 m (%100) | Japonya'da okula yürüme %92–93 [D]; Pontevedra %81 [K] |
| **Komşuluk** | 8–15 hanelik avlu ve bahçe grupları; 214–328 haneli komşuluk birimleri; mescit, çeşme, bakkal; meydan ve haftalık pazar | Alexander ve Osmanlı mahallesi ölçüleri [D]; Gifford derlemesi [İ] |
| **Kuşaklar arası yakınlık** | T2'de aynı parselde iki kuşak (%21); T1'de büyükler odası; T3 ve T4'te 1+1 ve erişilebilir zemin daireleri; komşuluk biriminde konut çeşitliliği, böylece aynı birimde kalarak ev değiştirmek mümkün | Singapur yakınlık hibesi ve 3Gen dersleri [D/K] |
| **Deprem güvenliği** | Konutların %97,5'i en fazla 4 katlı; düzenli ve kısa açıklıklı tipler; büyüme payı statik projede; dükkânlı zeminde perde sürekliliği; hızlı uygulama sürümü | "Zemin dahil 3–4 kat" söylemi [K]; TBDY uyumu doğrulanmalı |
| **Hürriyet ve sahiplik** | 791 parsel; ada başına en fazla 40 konut aynı yapımcıya; T4'te 24 m'lik parseller | Rieselfeld kuralı [K]; Vauban yapı grupları [İ] |
| **Araç bağımlılığını azaltma** | Otopark konuttan ayrı; 4 mobilite noktası, 0,56 yer/hane; her konuta 400 m içinde durak | Vauban [K]; Poundbury uyarısı [İ] |

## 8. Varsayımlar ve sınırlılıklar

1. **Hane büyüklüğü** 3,2 kişi kabul edildi (§9.2 varsayımı). TÜİK verisiyle kalibre edilmeli. 3,0 kişi alınırsa nüfus 6.666 olur.
2. **Arazi düz kabul edildi.** Eğimli arazide teraslama ve sokak yönü değişir.
3. **Daire alanları** tipoloji çizimlerinden geldi. Plan modelinde T3'te ≈ 120 m², T4'te ≈ 100 m² brüt kabul edildi; çizimlerde T4 ortalaması ≈ 96 m².
4. **Yaya ağı.** Sokak eksenleri, S3 geçitleri, diyagonaller, park içi yollar ve meydan kullanıldı. Avlu grupları ve ada içi şeritler ağa dahil değil (yarı özel). Karşıdan karşıya geçiş her kavşakta serbest kabul edildi.
5. **Ağaç örtüsü** kaba bir tahmindir (sokak ağacı tacı 38 m², parkların %45'i, bahçe başına 1 ağaç).
6. **Kesitlerdeki güneş** yalnız öğle güneşidir; sabah ve akşam saatleri, yamaç ve komşu binalar hesaba katılmadı.
7. **Mevzuat.** Bütün maddeler proje mevzuat haritasından aktarıldı; yorumlar doğrulanmalıdır (`fitrat_kodu_taslak.md` §7).

## 9. Açık sorular

1. **Alan büyüklüğü.** Tek ilkokulla %100 erişim için mahalle 52–55 ha'ya mı indirilmeli, yoksa ikinci bir küçük ilkokul mu açılmalı? Küçük okul Japonya örneğine yakın. Seçim nüfus ve öğrenci sayısına bağlı; çocuk yaş yapısı TÜİK ile kalibre edilmeli.
2. **Mescit ölçütü.** "150 m'de mescit" ölçütü kademeli kuralla mı yazılmalı? Kademeli kural 16 mescitle %99,3 sağlıyor; saf 150 m için ≈ 25–30 mescit gerekir.
3. **Diyagonallerin bedeli.** Diyagonaller erişimi iyileştirdi ama ≈ 80 T1, 12 T2 ve 6 T3 parselini ve ≈ 1,9 ha araziyi götürdü. Bu kırpıntılar cep parkı mı kalmalı, özel köşe parsellerine mi dönüşmeli? İkinci seçenek kaba tahminle ≈ 40–60 konut geri kazandırır.
4. **Güney sıra bahçeleri.** T12 adalarının güney sırasındaki T1 bahçeleri kışın gölgede kalıyor. Uzun kenarı K–G uzanan adalar (D–B cepheli evler) denenmeli.
5. **Otopark.** 0,56 yer/hane bölgesel otopark ve parsel içinde otopark olmaması Otopark Yönetmeliği ile nasıl bağdaşır? Belediye meclisinin rolü ne?
6. **Maliyet ve deprem.** Z+2 / Z+3 bitişik nizamın birim maliyeti ve TBDY 2018 kapsamındaki değerlendirmesi 06_SIMULASYON ayağına devredilmeli.
7. **Gerçek bir alan.** Model 60 ha'lık soyut bir kareye uygulandı. Faz 2 panelinin artıklarından seçilecek bir pilot ilçede gerçek bir parsel üzerinde (topoğrafya, mülkiyet, mevcut yapı) yeniden kurulmalı.
8. **Sosyal karma.** Plan yalnız konut tipini belirliyor. %30 kooperatif ve %20 kiralık sosyal konut kotasının adalara dağılımı (§9.4) bir sonraki sürümde parsel düzeyinde işaretlenmeli.

## 10. Yeniden üretim

```
cd 07_TASARIM_CIZIM/model_mahalle/kod
python hepsini_calistir.py
```

Gerekenler: Python 3.11, matplotlib, shapely ≥ 2, networkx, numpy; DXF için ezdxf.

Bütün ölçüler `plan_modeli.py`'nin başındadır: `PROGRAM` (ada tipolojileri), `KISMI` (kısmi adalar), `KAPALI` (kapanan sokaklar), `ZEMIN_KURAL`, `DURAKLAR`. Bir değer değiştirilip betik yeniden çalıştırılınca bütün çizimler ve `metrikler.csv` güncellenir.

---

## Ek düzeltme (26.10.2026, mevzuat paketinden)

- **Okul alanları:** Güncel MPYY EK-2'ye göre ilkokul ve ortaokulun her biri 2,0 m²/kişi olmalı (asgari 5.000–8.000 ve 6.000–10.000 m²). 7.110 kişi için bu ≈ 1,42 ha ediyor. v1'deki ilkokul arsası 11.312 m², yani ≈ 0,3 ha eksik. v2'de ilkokul arsası büyütülmeli; tercihen "ikinci küçük ilkokul" seçeneğiyle birlikte (açık sorun 1).
- **Asansör:** PAİY md. 34/1'e göre (RG 01.07.2026) bodrum dahil 4 ve daha fazla katlı binalarda asansör tesisi, 3 katlı binalarda asansör yeri bırakılması zorunlu. T4 çevre adası (Z+3) asansörlü, T1–T3 (≤ Z+2) asansör yeri bırakılarak tasarlanmalı. Maliyet etkisi `08_MEVZUAT_POLITIKA/degisiklik_paketi_v1.md` P4'te.
