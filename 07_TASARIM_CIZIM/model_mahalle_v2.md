# Model Mahalle v2.1 — Güncel EK-2, Asansör Kuralı, v1 Açık Sorunları ve Geleneksel Doku Kalibrasyonu

**Proje:** TR TAMİRAT
**Bölüm:** 07_TASARIM_CIZIM · İP6 (model mahalle ve tasarım)
**Tarih:** 26 Ekim 2026 · **Sürüm:** v2.1 (v2.0 aynı gün; v2.0 değerleri `metrikler.csv`'nin `v2_0` sütununda ve `MM_SURUM=2.0` ile aynı koddan yeniden üretilebilir)
**Önceki sürüm:** `model_mahalle_v1.md` ve `model_mahalle/` (değiştirilmedi)
**Girdi:** `tasarim_parametreleri.md` (§6.2 düzeltme notu, §9) · `08_MEVZUAT_POLITIKA/degisiklik_paketi_v1.md` (M1, P4, O1–O2, G1) · `08_MEVZUAT_POLITIKA/finansman_modeli/` (M6) · `06_SIMULASYON/persona_anlatilari.md` · `09_RAPORLAR/05_zihinsel_simulasyonlar.md` · `09_RAPORLAR/09_faz2_sentez.md` · **v2.1:** `09_RAPORLAR/11_geleneksel_doku_morfolojisi.md` (§3), `05_ANALIZ/sonuclar/morfoloji_karsilastirma.csv`, `03_VERI/kod/morfoloji_olcum.py` (üçü de yalnız okundu)
**Eş belge:** `fitrat_kodu_taslak_v2.md` (Sürüm 0.2.1)
**Kod:** `model_mahalle_v2/kod/` · bütün çıktılar için `python hepsini_calistir.py` (≈ 40 sn)

İşaretler projedeki gibidir: **[D]** doğrulandı · **[İ]** ikincil · **[DY]** doğrulanmadı · **[V]** bu çalışmanın varsayımı · **[H]** bu çalışmada hesaplandı. Plan sayılarının hepsi [H] türündedir: çizimin poligonlarından ve yaya ağından hesaplanır, elle girilmiş toplam yoktur. v1 değerleri v1'in `metrikler.csv`'sinden okunur; v1'de olmayan göstergelerde v2 yöntemi v1 geometrisine uygulanır (`v1_okuyucu.py`, v1 kodunu ayrı bir süreçte yalnız okur).

Bu belgede üç sürüm karşılaştırılır: **v1**, **v2.0** (güncel EK-2, asansör, v1 sorunları) ve **v2.1** (v2.0 + geleneksel doku kalibrasyonu). Tablolarda tek "v2" sütunu varsa değer v2.1'dir ve v2.0'dan farklı değildir.

---

## Özet

### v2.1: geleneksel doku kalibrasyonu

- **Uygulandı.**
  - **Ada ortası geçitleri.** T1/T2 adalarının uzun kenarının ortasından 5 m'lik kamusal S3 geçidi geçiyor (3,5 m engelsiz). Geçit sayısı 22'den **43'e** çıktı (0,82 → 1,46 ha). Tam 60 ha'da yaya adası medyanı **0,79'dan 0,45 ha'ya**, çevresi 368'den 268 m'ye indi. Araç adası 0,97 ha'da kaldı.
  - **Kavşak yoğunluğu (yaya dahil).** Raporun 600 m'lik penceresinde **242'den 303/km²'ye** çıktı; hedef ≥ 300. Araç ağı 122/km²'de kaldı.
  - **S2.** K2 ön eşiği 1,5'ten 1,0 m'ye indi: cephe arası 13'ten **12 m'ye**, H/W **0,72'den 0,78'e**.
  - **S3.** Bütün geçitlerde ≥ 3,5 m engelsiz yürüme bandı var. T3 geçidi 6 m, ada ortası geçidi 5 m.
  - **T3 avlusunun dördüncü kenarı.** Güney sıra grupta tek katlı arka kanat var (2 eşiksiz 2+1). Kuzey sıra grupta 2,5 m'lik bahçe duvarı var. Kapalı avlu **0'dan 0,83/ha'ya** çıktı (60 ha: 0,63); medyanı **326 m²**.
- **Kısmen.**
  - **T1 cephesi.** K1'de **7,2 m**, K2'de 6,4 m (v2.0: 6,3). T2 9,2'den 9,6 m'ye çıktı.
  - **Yapı oturumu.** Brüt %22,2'den %23,6'ya, net %31,1'den %33,6'ya çıktı. Hedef brüt %25–30.
  - **T3/T4 cephesi 9–12 m'lik modüllere bölündü.** Bölme yalnız cephe ve giriş düzeyinde. Ayrı binalara bölmek asansör sayısını ikiye katlardı.
- **Uygulanmadı.**
  - **T1 derinliği 11–12 m.** Son durumda T1 zaten 6,4 × 13 m (83 m²). Ölçüm yalnız 9 m'lik çekirdeği görüyor.
  - **Brüt emsal 0,75–0,9.** Modelde 0,64; ulaşmak için kat artırmak gerekirdi.
- **Korundu.**
  - İlkokula ≤ 500 m **%100** (en uzak 493 m).
  - Ağaç örtüsü **%31,1**.
  - Kamusal yeşil **12,3 m²/kişi**.
  - ≤ 3 katlı binada oturan pay **%70,1**.
  - 5 kattan yüksek bina yok.
  - FUE Ç **62,3'ten 62,8'e** çıktı, yani düşmedi.
- **Bedeli.**
  - T1 payı %24,7'den **%22,8'e** indi.
  - Net konut alanı 27,15'ten 26,51 ha'ya indi; geçitler 0,64 ha tuttu.
  - Konut sayısı aynı kaldı (2.164): 75 T1/T2 konutunun kaybı 76 arka kanat konutuyla karşılandı.
  - S2'de 21 Aralık öğle gölgesi karşı cephede 3,1 m'den **3,6 m'ye** çıktı.
  - Kuzey avlunun 21 Aralık öğlesinde ≈ %36'sı gölgede.

### v2.0: EK-2, asansör, v1 sorunları (değişmeden geçerli)

- **Okul.** İlkokul alanı güncel EK-2'ye göre **2,11 m²/kişi** (v1: 1,59). İkinci ilkokul açıldı: **A** meydanın güneydoğusunda (7.076 m², 10 derslik), **B** kuzeyde (7.515 m², 6 derslik). Okula 500 m içinde oturan konut payı **%96,8'den %100'e** çıktı. Ortaokul **2,26 m²/kişi** (v1: 1,50).
- **Neden ikinci okul?** Üç seçenek aynı kurallarla şematik bir ağda karşılaştırıldı (`okul_secenekleri.png`):
  - Alanı **55 ya da 52 ha'ya indirmek %100 vermedi** (%99,2 ve %99,7) ve 128–135 kişi/ha yoğunluk gerektiriyor.
  - **Sekizgen biçim** %97,8'de kaldı, **uzun dikdörtgen** %89,4'e düştü.
  - Yoğunluğu ve kat profilini değiştirmeden %100 sağlayan tek seçenek ikinci okul.
- **Asansör (PAİY md. 34/1).**
  - T1 tek bağımsız bölümlü; kuralın kapsamı dışında, ama platform yeri bırakıldı.
  - T2 ve Z+2 avlu gruplarında asansör yeri, Z+3 avlu gruplarında ve T4'te asansör var.
  - Zorunlu asansör yapım maliyetinin **%5–7,6'sı** [V]. P4 galeri çözümü asansör sayısını **111'den 67'ye** indirir.
  - Binaların %100'ü ölçüt 17'yi sağlıyor.
- **Diğer.**
  - Köşe evi kuralı, tahsis karması (her komşuluk biriminde sapma ≤ 3 puan) ve teknik altyapı ile sosyal-kültürel alan güncel EK-2'ye göre düzenlendi.
  - Otopark Yönetmeliği farkı sayıyla gösterildi: plan, Ek-1'in bugünkü gereğinin ≈ %50'sini sağlıyor.
- **32 ha net konut alanı** güncel EK-2 ile tutarlı değil. Tutarlı hedef v2.0'da 27,5 ha, v2.1'de geçitlerle 26,8 ha (§3.3).

---

## 1. Çizimler ve kod

Bütün dosyalar `07_TASARIM_CIZIM/model_mahalle_v2/` altındadır. PNG'ler 150 dpi, SVG'ler vektördür. Hepsi v2.1 geometrisinden üretilir.

| Dosya | İçerik |
|---|---|
| `vaziyet_plani.png` · `.svg` · `.dxf` | 60 ha vaziyet planı. İçinde: iki ilkokul, ortaokul, teknik altyapı şeritleri, köşe evleri, okul geçidi ve 5.558 ağaç. **v2.1:** ada ortası S3 geçitleri, T3 arka kanatları ve bahçe duvarları. Sağ panelde Fıtrat Kodu bölgeleri, tahsis karması ve ana sayılar var. DXF katmanlıdır |
| `erisim_analizi.png` · `.svg` | Her konut için ağ mesafesi, 8 harita |
| `okul_secenekleri.png` · `.svg` | (a) 55 / 52 ha, (b) ikinci okul, (c) sekizgen ve uzun biçim; şematik ağda karşılaştırma |
| `sokak_kesitleri.png` · `.svg` | Dört kesit. Kat yüksekliği 3,1 m. **v2.1:** S2 ön eşiği 1,0 m; S3'te 3,5 m engelsiz bant (1,25 + 3,5 + 1,25) |
| `tipoloji_T1…T4_*.png` · `.svg` | Asansör ya da platform yeri, alan ve maliyet. **v2.1:** T1 parsel 6,37 m (K1 7,17 m); T2 9,56 m; T3'te arka kanat, kapalı avlu ve kuzey avluya düşen gölge |
| `tipoloji_asansor_ozeti.png` · `.svg` | PAİY md. 34/1'in tipoloji başına etkisi. v2.1'de T3 arka kanadı satırı eklendi (tek katlı, kural dışı) |
| `deprem_hizli_uygulama.png` · `.svg` | v2.1 planıyla aşamalama |
| `v1_v2_degisiklikler.png` · `.svg` | **v1 → v2.1 levhası.** Numaralı 13 değişiklik (1–9 v2.0, 10–13 v2.1), iki ilkokul erişim haritası, 17 gösterge (v1 · v2.0 · v2.1; morfoloji ve FUE satırları dahil) |
| **`figur_zemin_v2_1.png` · `.svg`** (yeni) | Figür–zemin paftası, aynı 600 × 600 m ölçekte 6 pano: Zeyrek (G4), Beypazarı (G3), Başakşehir (C2), model v1, v2.0 ve v2.1. Her panoda raporun ölçütleri yazılı |
| **`morfoloji_olcum_v2.csv`** (yeni) | `morfoloji_olcum.py`'nin ölçüt fonksiyonlarıyla v2.0 ve v2.1 ölçümü. 600 m pencere (M1) ve tam 60 ha (M0), raporun 12 alanı ve v1 satırlarıyla aynı sütunlar |
| `metrikler.csv` | 146 gösterge. Sütunlar: `v1_degeri`, **`v2_0`**, **`v2_1`**, `v2_degeri`, hedef, kaynak, durum, not. `v2_degeri` = `v2_1`; bu sütun `05_ANALIZ/kod/fue_model_mahalle.py` uyumluluğu için tutuldu. v2.1'de "Morfoloji (600 m pencere)" ve "FUE konumu" bölümleri eklendi |

Kod dosyaları (`model_mahalle_v2/kod/`):

| Dosya | Görevi |
|---|---|
| `plan_modeli.py` | Geometri, yaya ağı, zemin kat donatıları, ağaçlar, tahsis. `MM_SURUM` ortam değişkeni (`2.0` / `2.1`, varsayılan 2.1) ve `KALIBRE` anahtarı. v2.1 değişiklikleri "v2.1:" diye işaretli. Parametreler: `GECIT_G`, `T1_GEN_K1`, `ON_ESIK_K2`, `T3_ARKA_DER`, `T3_ARKA_KONUT` |
| `metrikler.py` | Doğrulama ve CSV. v2.0 sütununu ayrı süreçte `MM_SURUM=2.0` ile hesaplar. Morfoloji satırları ve FUE konumu (E, Ç; tek ve iki muhtarlık) bu dosyada |
| **`morfoloji_v2.py`** (yeni) | `03_VERI/kod/morfoloji_olcum.py`'yi değiştirmeden içe aktarır (`model_veri`, `olc`, `alan_hazirla`). v2.0 ve v2.1'i raporun ölçütleriyle ölçer, grup medyanlarını raporun dışlama kuralıyla hesaplar, figür–zemin paftasını çizer |
| `tipoloji_verisi.py` | PAİY md. 34/1, bağımsız bölüm kataloğu (v2.1: `T3_arka_2+1` 90 m²), Otopark Ek-1, maliyet varsayımları [V] |
| `v1_okuyucu.py` | v1 değerlerini okur; v1 kodunu ayrı süreçte çalıştırır ve hiçbir v1 dosyasına yazmaz |
| `vaziyet_plani.py`, `erisim_analizi.py`, `sokak_kesitleri.py`, `konut_tipolojileri.py`, `deprem_hizli_uygulama.py`, `okul_secenekleri.py`, `tipoloji_asansor_ozeti.py`, `v1_v2_karsilastirma.py`, `hepsini_calistir.py` | Levhalar ve sırayla çalıştırma |

---

## 2. Değişiklik tabloları

### 2.1 v1 → v2.0

| # | Konu | v1 | v2.0 | Gerekçe |
|---|---|---|---|---|
| 1 | İlkokul | Tek okul, 11.312 m² (1,59 m²/kişi); %96,8 ≤ 500 m | **İki okul.** A 7.076 m² meydanda; B 7.515 m² kuzeyde (ada 3,8). Toplam 2,11 m²/kişi; %100 ≤ 500 m | Güncel EK-2 (2,0 m²/kişi; okul başına ≥ 5.000 m²) [D]. Seçenek karşılaştırması §3.1'de |
| 2 | İlkokul A kapısı | Meydan + cadde (y 320) | Meydan + **okul geçidi**: park yolunun karşısında, S1'de yükseltilmiş geçit | Güneybatıdan gelen 18 konut 500 m'yi aşıyordu |
| 3 | Ortaokul | 10.692 m² (1,50 m²/kişi), yanında T3S şeridi ve cep parkı | **15.658 m²** (2,26 m²/kişi). Güneydoğu köşe adalarının tamamı; okul sahası mesai dışında açık | Güncel EK-2 [D] |
| 4 | Ada (3,2) | İlkokul yerleşkesi + T2S şeridi; S2 kapalı | S2 yeniden açıldı; ada T12 oldu (T1 + T2) | Okul küçüldü, arazi konuta döndü |
| 5 | Mahalle konağı | 5.232 m² (0,74 m²/kişi) | 5.818 m² (0,84); (3,3)'teki üçgene uzadı | Sosyal-kültürel alan ≥ 0,75 m²/kişi [D] |
| 6 | Teknik altyapı | 3.512 m² (0,49 m²/kişi), iki köşe | **7.529 m²** (1,09): üç köşe üçgeni ve 4 mobilite noktasında 9 m'lik servis şeridi | Güncel EK-2 ≥ 1,0 m²/kişi [D] |
| 7 | Mobilite noktası | 4 × 50 m, Z+3 (1,26 ha) | 4 × 41 m, **Z+4** (1,03 ha); 1.235 araç, 0,57/hane | Aynı otopark oranı daha az arazide |
| 8 | Diyagonal kırpıntısı | Kesilen parsel düşürülüyordu (98 parsel) | **Köşe evi kuralı:** bina en az %60 kalıyorsa kırpılır; T2 %80'in altında kalırsa T1 olur | v1 açık sorusu 3 |
| 9 | T1 payı | 447 konut (%20) | **534** (%24,7) | §3.3 |
| 10 | Kat yüksekliği ve ön eşik | 3,0 m; ön eşik 2,0 m | **3,1 m**; K2'de ön eşik **1,5 m** (K1'de 2,0 m) | S2 H/W 0,64 → 0,72 |
| 11 | Asansör | Z+3'te asansör; Z+2'de "asansör yeri" yalnız T3 çiziminde | PAİY md. 34/1 bütün tipolojilere işlendi (§3.2) | PAİY md. 34/1 (RG 01.07.2026) [D]; paket P4 |
| 12 | Ağaç | Kaba formül (%25) | Ağaç noktaları çizimle ortak; dikim kuralları. **%31,1** | 3-30-300 hedefi |
| 13 | Tahsis | İşaretlenmemişti | Bahçe grubu, avlu grubu ve T4 parseli düzeyinde (§3.4) | v1 açık sorusu 8 |
| 14 | Kat dengesi | KB-3 328 hane | (0,5) ve (1,5) Z+3 → Z+2; (2,7) ve (3,7) Z+2 → Z+3 | KB-3 aşımı |
| 15 | Mescit adayı | T3/T4 zemini, cep parkı, kenar parkı | Bostan da aday | İbadet kademesi %98,9 → %99,4 |

### 2.2 v2.0 → v2.1 (geleneksel doku kalibrasyonu)

Levhada (`v1_v2_degisiklikler.png`) 10–13 numaralarıyla gösterilir.

| Levha # | Konu | v2.0 | v2.1 | Rapor önerisi (§3.1) |
|---|---|---|---|---|
| 10 | Ada ortası geçidi | Yalnız T3 adalarında 6 m geçit (22 geçit, 0,82 ha) | 120 m'yi aşan T1, T2 ve T12 adalarında uzun kenarın ortasından **5 m S3 geçidi** (3,5 m engelsiz + 1,5 m yağmur bahçesi ve oturma). 43 geçit, 1,46 ha | Yaya adası ≤ 0,35–0,45 ha; adaya 4–6 m geçit |
| 11 | Parsel cephesi | T1 6,3 m, T2 9,2 m | Yarım sıra yeniden bölünür. **T1 K1 7,17 m** (yarım sırada 8 parsel), **K2 6,37 m**; **T2 9,56 m** | T1 6,5–7,5 m; T2 9–10 m |
| 12 | S2 ön eşiği | K2 1,5 m (cephe arası 13 m) | **K2 1,0 m** (cephe arası **12 m**); K1'de 2,0 m korundu | S2 cephe arası 11–12 m, H/W 0,75–0,8 |
| 13 | T3'ün dördüncü kenarı | Avlu kuzeyde ya da güneyde açık | **Güney sıra grup:** ada ortasında 5 m derin, tek katlı arka kanat (2 eşiksiz 2+1, 90 m²), yan kanatlar ona kadar uzar; 38 kanat, 76 konut. **Kuzey sıra grup:** yanlarda 2,5 m bahçe duvarı; dördüncü kenarı komşunun arka kanadı oluşturur | Kapı binası ya da 2,5–3 m duvar; 300–450 m² kapalı avlu, ≈ 0,5/ha |

---

## 3. Görevler: önce ve sonra

### 3.1 Okul alanları ve ilkokula ≤ 500 m

**Güncel standart [D, degisiklik_paketi_v1.md M1].** İlkokul ve ortaokul için 2,0 m²/kişi gerekir. Asgari parsel ilkokulda 5.000–8.000, ortaokulda 6.000–10.000 m²'dir. Model mahallenin nüfusuyla her biri ≥ 13.850 m² eder.

**Seçenekler.** Seçenekler şematik bir ağda karşılaştırıldı (`okul_secenekleri.py`):

- **Ağ.** v1'le aynı kurallarla kuruldu: ada 120 × 63 m, S2 10 m, artı cadde, köşe diyagonalleri, konutsuz merkez.
- **Kalibrasyon.** Ağ önce v1 kurgusuyla sınandı. Tam model %96,8 / 553 m, şematik ağ %97,6 / 545 m verdi.

| Seçenek | Alan | ≤ 500 m | ≤ 400 m | En uzak | 2.200 konutla yoğunluk | Değerlendirme |
|---|---|---|---|---|---|---|
| v1 kurgusu (kalibrasyon) | 60 ha | %97,6 | %74,7 | 545 m | 117 kişi/ha | — |
| (a) 55 ha kare, tek okul | 55 ha | %99,2 | %80,1 | 519 m | 128 kişi/ha | %100 değil. Aynı nüfus daha çok Z+3/T4 ister |
| (a) 52 ha kare, tek okul | 52 ha | %99,7 | %83,2 | 506 m | 135 kişi/ha | Hâlâ sınırda |
| **(b) 60 ha, iki okul** | 60 ha | **%100** | **%89,9** | **488 m** | 117 kişi/ha | **Seçildi** |
| (c1) Sekizgen, köşe pahı 170 m | 60 ha | %97,8 | %73,3 | 524 m | 117 kişi/ha | Pahlarda düzensiz parsel |
| (c2) Uzun dikdörtgen 1.000 × 600 m | 60 ha | %89,4 | %66,0 | 592 m | 117 kişi/ha | Tek merkezle daha kötü |

**Seçim: (b), ikinci okul.**

- **Ne korunur?** Alan, brüt yoğunluk ve ≤ 3 kat payı.
- **Neden (a) değil?** (a), aynı nüfusu daha küçük alana sığdırmak için dikeyleşme ister. Faz 2'de kat başına ≈ +%2,5 standartlaştırılmış ölüm bulundu (`09_faz2_sentez.md`).
- **Bedeli.** İkinci okul binası, yönetimi ve öğretmen kadrosu (MEB norm kadro [DY]).

**Sonuç (tam model).**

| Gösterge | v1 | v2.0 | v2.1 | Hedef |
|---|---|---|---|---|
| İlkokul ≤ 500 m (% konut) | 96,8 | **100,0** | **100,0** | 100 |
| İlkokul ≤ 400 m (% konut) | 74,5 | 90,7 | **91,0** | tercihen 100 |
| Medyan · en uzak (m) | 323 · 553 | 244 · 494 | **239 · 493** | — |
| İlkokul arsası (m²/kişi) | 1,59 | **2,11** | **2,11** (A 7.076 + B 7.515 m²) | ≥ 2,0; okul başına ≥ 5.000 |
| Kayıt alanı (en yakın okul) | — | A 1.376 · B 787 hane | A 1.390 hane ≈ 267 öğrenci, 10 derslik · B 774 hane ≈ 149 öğrenci, 6 derslik ([V]: 6–9 yaş %6, 28 öğrenci/derslik) | — |
| Ortaokul arsası (m²/kişi) | 1,50 | **2,26** | **2,26** | ≥ 2,0 |
| Eğitim toplamı (m²/kişi) | 3,59 | **4,88** | **4,88** | 4,5 |

**İki okulun dengesi.** Okullar eşit değil. A meydana değiyor ve merkezin her yönden en kolay ulaşılan noktası. Kayıt alanı "en yakın okul" kuralıyla tanımlandı.

### 3.2 Asansör kuralı (PAİY md. 34/1)

**Mevcut hüküm [D, degisiklik_paketi_v1.md P4].**

- Tek bağımsız bölümlü konutlar hariç, bodrum dahil 3 katlı binada asansör yeri, 4 ve daha fazla katlı binada asansör tesisi zorunlu.
- md. 34/4'e göre 20'den fazla konut bağımsız bölümü olan binada en az 2 asansör gerekir; modelde buna ulaşan bina yok.

**Maliyet varsayımları [V].** Asansör 1,3 milyon TL (4 durak), kaldırma platformu 0,9 milyon TL. Yapım maliyeti M6 finansman modeliyle aynı: 2026 tebliği, %10 kâr hariç.

| Tipoloji (bina) | Kat · BB | PAİY 34/1 | Çözüm | Kuyu alanı (binanın %'si) | Zorunlu maliyet · yapıma oranı | Hane başına (bugün · P4) | Plandaki bina (v2.1) |
|---|---|---|---|---|---|---|---|
| T1 büyüyebilen sıra ev | Z+2 · 1 | yok (tek BB) | Kiler/dolap dikmesi platform yeri (1,0 × 2,3 m) | 6,9 m² (%3,5) | — (platform takılırsa %23,8) | — | 493 |
| T2 çok kuşaklı ev | Z+2 · 2 | asansör yeri | 1,4 × 1,6 m kuyu; zemin 2+1 eşiksiz | 6,7 m² (%2,2) | — | — | 194 |
| T3 avlu grubu, Z+2 | Z+2 · 12 | asansör yeri | 2 çekirdekte kuyu; zeminde 2 eşiksiz daire | 17,3 m² (%1,2) | — | — | 34 |
| T3 avlu grubu, Z+3 | Z+3 · 15 | asansör | 2 asansör; P4: galeri + 1 | 23,0 m² (%1,3) | 2,6 milyon TL · **%7,6** (P4: %3,8) | 173 · 87 bin TL | 44 |
| **T3 arka kanat (v2.1)** | Z · 2 | yok (tek kat) | Zeminden girişli, eşiksiz 2+1 | — | — | — | 38 |
| T4 çubuk, Z+3 | Z+3 · 9 | asansör | 1 asansör | 11,5 m² (%1,0) | 1,3 milyon TL · %5,8 | 144 bin TL | 18 |
| T4 köşe, Z+4 | Z+4 · 12 | asansör | 1 asansör (5 durak) | 14,4 m² (%1,0) | 1,4 milyon TL · %5,0 | 117 bin TL | 5 |

**Plan geneli.**

| Gösterge | v1 (v2 kuralıyla) | v2.0 | v2.1 |
|---|---|---|---|
| Asansör, bugünkü uygulama | 115 | 111 | **111** (≈ 144,8 milyon TL [V]) |
| Asansör, paket P4 ile | 69 | 67 | **67** (≈ 87,6 milyon TL; −%40) |
| Asansör yeri · platform yeri | — · 0 | 279 · 534 | 262 · 493 |
| Zemin katta eşiksiz daire | %16,1 | %14,8 (320) | **%16,7 (362)** |
| Basamaksız ulaşılan konut (zemin + asansörlü) | %43,7 | %42,8 | %44,7 |
| Binası ölçüt 17'yi sağlayan konut | — | %100 | **%100** |

**Okuma.**

- **Z+2'de maliyet küçük.** Kural yalnız yer istiyor. Kuyu binanın %1–3,5'i kadar ve depo olarak kullanılabilir.
- **Asıl yük Z+3 avlu gruplarında.** Asansör yapımın %7,6'sını tutuyor. Paket P4 (galeri ve tek asansör) bunu yarıya indirir.
- **v2.1'in katkısı.** Tek katlı arka kanatlar asansörsüz 76 eşiksiz daire ekledi. Zemin erişilebilir pay %15 eşiğinin üstüne çıktı (%16,7).
- **Persona C.** Erişilebilirlik ilk olarak asansörle değil, zemin kat dairesi ve eşiksiz sokakla sağlanır.

### 3.3 Net konut alanı, T1 payı, S2 H/W ve ağaç örtüsü

| Gösterge | v1 | v2.0 | v2.1 | Hedef | Durum (v2.1) |
|---|---|---|---|---|---|
| **S2 yaşam sokağı H/W** (son durum, K2) | 0,64 | 0,72 | **0,78** | 0,7–1,0 (rapor: 0,75–0,8) | **Sağlandı.** W 12,0 m, H 9,3 m. K1'de (ön eşik 2,0 m) 0,66; T1 çekirdek döneminde 0,65 |
| S1 mahalle caddesi H/W | 0,69 | 0,71 | 0,71 | 0,7–0,8 | Sağlandı |
| **Ağaç örtüsü** (20 yıl) | %25,4 (formül) | %31,1 | **%31,1** (5.558 ağaç) | ≥ %30 | Sağlandı |
| **T1 payı** | %20,1 (447) | %24,7 (534) | **%22,8** (493) | %29 | **Geriledi.** Geniş parsel ve geçitlerin bedeli |
| **Net konut alanı** | 27,30 ha | 27,15 ha | **26,51 ha** | 32 ha (tutarlı: 26,8 ha) | Tutarlı hedefin %1,2 altında |

**S2'nin bedeli (v2.1'de büyüdü).**

- 21 Aralık öğlesinde karşı cephenin gölgelenen kısmı v1'de 2,3 m, v2.0'da 3,1 m, v2.1'de **3,6 m**. Zemin kat penceresi öğle saatinde tümüyle gölgede.
- 21 Mart'ta cephe tümüyle güneşte.
- Genelge 2026/4 ölçüt 6, D–B uzanan S2'nin kuzey cephesinde v1'den beri sağlanmıyor. Çelişki ve karar §3.5.3'te.

**Ağaç örtüsü.** Ağaçlar tek bir fonksiyondan üretiliyor (`plan_modeli.agac_noktalari`). 20 yıllık taçlar birleştirilir, çakışanlar bir kez sayılır. Dikim kuralları Fıtrat Kodu §3.2'de.

v2.1'deki değişikliklerin örtüye etkisi:
- 43 geçidin yağmur bahçelerine ağaç dikildi.
- Kapalı avlulara 4'er ağaç kondu.
- Örtü %31,1'de kaldı.

**T1 payı neden %29'a ulaşmadı, v2.1'de neden geriledi?**

- **Arazi farkı.** Bir T1 adası konut başına ≈ 198 m², Z+2 avlu grubu adası ≈ 104 m² ister.
- **v2.1'deki gerileme.** Raporun T1 için önerdiği 6,5–7,5 m'lik cephe ve ada ortası geçitleri T1 parsel sayısını 534'ten 493'e indirdi (−41). Geçitler ve 9,56 m'lik T2 parseli T2'yi 17 bina (−34 konut) azalttı. Kayıp, T3 arka kanatlarının 76 konutuyla karşılandı.
- **Seçenekler.** Konut sayısı ve ≤ 3 kat payı sabitken T1 payını yükseltmenin tek yolu yeşilden ya da konut sayısından vermek (§3.3, v2.0 analizi). **Tipoloji hedefinin %22–25'e indirilmesi önerilir.** Raporun bulgusu bu yönde: geleneksel dokuda T1'in 6,3 m'si "3+1 için dar".

**Net konut alanı: tutarlı hedef** [H, metrikler.csv].

| Adım | v2.0 | v2.1 |
|---|---|---|
| §9.3 (eski EK-2, diyagonalsiz) | 32,0 ha | 32,0 ha |
| Güncel EK-2: eğitim 4,5, teknik 1,0, sosyal 0,75 m²/kişi | 30,7 ha | 30,7 ha |
| Diyagonaller ve S3 geçitleri | 29,2 ha | 28,5 ha |
| 4 mobilite noktası | 28,8 ha | 28,2 ha |
| Yeşilin 10 m²/kişinin üstünde tutulması | **27,5 ha** | **26,8 ha** |

**Arazi akışı (ha).**

| Değişen | v1 → v2.0 | v2.0 → v2.1 |
|---|---|---|
| Eğitim | +0,83 | 0 |
| Teknik altyapı | +0,40 | 0 |
| Konak | +0,06 | 0 |
| Otopark | −0,23 | 0 |
| Yeşil | −0,89 | +0,01 |
| Sokak, yaya yolu, meydan | −0,03 | **+0,64** (geçitler) |
| Net konut | −0,15 | **−0,64** |

### 3.4 Diğer v1 açık sorunları

| v1 açık sorusu | Durum (v2.1) |
|---|---|
| 1. Alan büyüklüğü / ikinci okul | **Çözüldü** (§3.1). Tek merkez sınırı ASM (%96,7) ve mahalle konağı (%95,7) için sürüyor |
| 2. Mescit ölçütü | Kademeli kural: **%99,4**. Saf 150 m'de %74,1. Karar politika düzeyinde |
| 3. Diyagonallerin bedeli | **Kısmen çözüldü.** Köşe evi kuralıyla 17 parsel ve 19 konut geri geldi; düşen parsel 98'den 84'e indi |
| 4. Güney sıra bahçeleri | **Çözülmedi.** Bahçesi evin kuzeyinde kalan T1/T2 konut payı %43,6. Ada yönü gerçek alanda yeniden kurulmalı |
| 5. Otopark | **Sayıyla gösterildi.** Ek-1'in bugünkü kuralı 2.481 yer istiyor: konut 2.100, dükkân 381. Plan 1.235 yer sağlıyor (%50). O1 reformuyla gerek ≈ 1.807'ye iner (plan %68'ini sağlar). Kalan fark O2 ve belediye meclisi kararıyla kapanır |
| 6. Maliyet ve deprem | **Kısmen.** Asansör maliyeti tipolojilere işlendi; TBDY 2018 değerlendirmesi yok |
| 7. Gerçek bir alan | **Açık** (pilot ilçe; v3) |
| 8. Sosyal karma | **Çözüldü.** Kooperatif %30,3, kiralık sosyal %19,8, piyasa %49,9. Komşuluk biriminde en büyük sapma 2,6 puan. Piyasa payı 53 yapımcıya bölünüyor |
| KB aşımı | KB-3 301, **KB-4 306**, **KB-7 309** hane; üçü de 300 sınırının %3'ü içinde ("yakın") |

### 3.5 Geleneksel doku kalibrasyonu (v2.1)

**Yöntem.**

- **Ölçüm.** v2.0 ve v2.1, raporun ölçüm betiğiyle ölçüldü. `morfoloji_olcum.py` değiştirilmeden içe aktarıldı. `MODEL_KOD` v2 koduna yönlendirildi; `model_veri()` ve `olc()` çağrıldı.
- **Pencereler.** Raporla aynı iki pencere kullanıldı: merkezde 600 × 600 m (**M1**, rapordaki alanlarla aynı ölçek) ve tam 60 ha (**M0**). H/W'de betiğin kat yüksekliği (3,0 m) kullanıldı; bu yüzden H/W plan değerinden (3,1 m) biraz düşük.
- **Grup medyanları.** Raporun kuralıyla hesaplandı:
  - sokak ölçütlerinde \* (sokak güvensiz) işaretli alanlar dışlandı;
  - emsal ve ortalama katta ‡ (kat şüpheli) işaretli alanlar dışlandı;
  - H/W'de ikisi birden dışlandı.
- **Çıktılar.** Sonuçlar `morfoloji_olcum_v2.csv`'de ve `metrikler.csv`'nin "Morfoloji" bölümünde. Figür–zemin karşılaştırması `figur_zemin_v2_1.png`'de.

#### 3.5.1 Öneri öneri karar ve önce / sonra

M1 = 600 m pencere, M0 = tam 60 ha. "Geleneksel · çağdaş" sütunu raporun 12 alanından grup medyanıdır. Raporun dışlama kuralıyla hesaplandı (`morfoloji_v2.ozet`); raporun tablosundaki yoğun doku aralıkları ayrıca §3.1'dedir.

| Öneri (rapor §3.1) | Karar | v1 | v2.0 | **v2.1** | Geleneksel · çağdaş | Not |
|---|---|---|---|---|---|---|
| **Yaya adası ≤ 0,35–0,45 ha**, çevre ≤ 280 m, adaya 4–6 m geçit | **Uygulandı** | M0 0,79 ha · 368 m | M0 0,79 · 368 | **M0 0,45 ha · 268 m** (M1 0,35 · 247) | 0,36 · 0,68 ha; çevre 263 · 360 m | 43 geçit (v2.0: 22). Geçitsiz kalanlar: T4 çevre adaları ve T3S şeritleri (çarşı cephesi sürekliliği) |
| **Kavşak (yaya dahil) ≥ 300/km²** | **Uygulandı** | M1 239 · M0 212 | M1 242 · M0 208 | **M1 303 · M0 268** | 315 · 221 | Planın kendi ağıyla 205 → 265/km² |
| Araç kavşağı 110–130/km², araç adası ≈ 0,95 ha | **Korundu** | 119 · 0,97 | 122 · 0,97 | 122 · 0,97 | 221 · 204; 0,40 · 0,69 ha | Araç hücresi ilkesi aynı |
| **S2 cephe arası 11–12 m, H/W 0,75–0,8** | **Uygulandı** | S2 14 m · 0,64 | 13 m · 0,72 | **12 m · 0,78** (M1 medyanı: cephe arası 13,0 → 12,5 m; H/W, 3,0 m katla, 0,69 → 0,75) | cephe arası 13,5 · 18,7 m; H/W 0,99 · 0,82 | K1'de 2,0 m eşik korundu (0,66). Çelişki §3.5.3 |
| **S3 5–6 m, ≥ 3,5 m engelsiz** | **Uygulandı** | 6 m (1,5 + 3,0 + 1,5) | aynı | **T3 geçidi 6 m (1,25 + 3,5 + 1,25); ada ortası 5 m (3,5 + 1,5)** | P25 5,4–7,3 m | Boy ≈ 63 m (ada derinliği). Öneri ≤ 60 m'nin %5 üstünde; iki ucu S2'ye açık |
| **T1 cephesi 6,5–7,5 m**, T2 9–10 m | **Kısmen** | 6,3 · 9,2 | 6,3 · 9,2 | **K1 7,17 · K2 6,37 · K3 6,30; T2 9,56** | bina cephesi 9 · 18 m | K2'de 6,5 m'lik hedef yarım sırada 8 parsel ve 7,2 m verirdi: −31 T1, T1 payı %21,4, konut 2.156 (sınandı). K2 6,4 m'de bırakıldı. Ölçülen bina cephesi medyanı 6 m'de kaldı (T1 çekirdeği) |
| **T1 derinliği 11–12 m** (taban 75–90 m²) | **Uygulanmadı** | taban medyanı 57 m² | 57 | 57 | 118 · 347 m² | Son durumda T1 6,4 × 13 m (çekirdek 9 m + genişleme 4 m), yani 83 m². Ölçüm yalnız Z+1 çekirdeği görüyor. Arka bahçe derinliği ≥ 10 m kaldı |
| **T3/T4 cephesi 9–12 m'lik modüller** | **Kısmen** | cephe adımı M1 19,3 m | 17,9 | **17,1 m** | 19 · 41 m | Modül cephe ve giriş düzeyinde (Fıtrat Kodu §3.1); ayrı bina olarak değil. Gerekçe §3.5.3 |
| **Yapı oturumu brüt %25–30**; net K3 %45–55, K2 %35–40 | **Kısmen** | brüt M1 %21,4 · net %29,8 | %22,2 · %31,1 | **%23,6 · %33,6** (M0 brüt %24) | brüt 30 · 25; net 34 · 29 | Tipolojide: T3 grubu %57 (K3 aralığında), T2 %40, T1 %33. Brüt hedef geçitler, EK-2 donatısı ve ≥ 10 m² yeşil yüzünden tutmuyor |
| Ada içi yapısız (net) K2 %60–65 | **Kısmen** | %70,2 | %68,9 | **%66,4** | 66 · 71 | Hedefe 1,4 puan |
| **Kat 2–4** (ort. 2,8–3,2; konutta 5 katın üstü yok) | **Korundu** | ort. 2,84 | 2,86 | **2,73** (M0 2,8) | 3,4 · 5,1 | ≤ 3 kat %70,1; ≤ 4 kat %97,5; 5 köşe binası Z+4 (%2,5); 5 katın üstü yok. Ortalamayı tek katlı arka kanatlar düşürüyor |
| **T3 dördüncü kenar; 300–450 m² kapalı avlu, ≈ 0,5/ha** | **Uygulandı** | 0 | 0 | **M1 0,83/ha · M0 0,63/ha; medyan 326 m²** | 0,11/ha · 144 m² (çağdaş 0) | Kapalı avlular güney sıra gruplarda (38 avlu, 266–382 m²). Kuzey avlular (40 avlu, 451–607 m²) duvarla kapalı; ölçüm duvarı bina saymadığı için açık sayılıyor |
| **Kamusal yeşil ≥ 10 m²/kişi** | **Korundu** | 13,2 (EK-2) | 12,3 | **12,3** (ölçüm M1: 13,3) | 1,1 · 1,2 | Geleneksel dokunun en zayıf yanı alınmadı |
| Brüt yoğunluk 120–150 kişi/ha, brüt emsal 0,75–0,9 | **Uygulanmadı** | 119 · 0,61 | 115 · 0,63 | **115 · 0,64** (M1 123 kişi/ha) | 76 · 210 kişi/ha; emsal 1,03 · 1,63 | +%17 kat alanı ya Z+3 ya da daha az yeşil ister. ≤ 3 kat payı ve EK-2 donatısı korundu |
| Izgara korunsun, ağ verimi | **Korundu** | 0,67 | 0,67 | 0,67 | 0,52 · 0,47 | — |

**Önce / sonra (plan).**

| Gösterge | v2.0 | v2.1 |
|---|---|---|
| Konut | 2.163 | 2.164 |
| T1 · T2 · T3 · T4 | 534 · 422 · 995 · 212 | 493 · 388 · 1.071 · 212 |
| 3+1 ve üstü · 2+1 · 1+1 | %62,0 · %32,4 · %5,6 | %59,3 · %35,1 · %5,6 |
| Özel bahçe ve avlu (konut başına) | 59,7 m² | 54,6 m² (kişi başı 17,1) |
| Sokak, yaya yolu, meydan | 16,56 ha (%27,6) | 17,20 ha (%28,7) |

#### 3.5.2 Uygulama

Değişiklikler `plan_modeli.py`'de `KALIBRE` anahtarına bağlı. Aynı kod `MM_SURUM=2.0` ile v2.0'ı yeniden üretir.

- **Geçit (`_gecitli`).** 100 m'den geniş T1, T2 ve T12 adalarında her yarım sıra iki parçaya bölünür. Ortada `GECIT_G` = 5 m'lik kamusal geçit kalır. Geçit yaya ağına S2'den S2'ye bir kenar olarak eklenir.
- **Parsel genişliği.** Yarım sıra (≈ 57 m) yeniden bölünür. K1'de hedef `T1_GEN_K1` = 6,5 m olduğu için 8 parsel ve 7,17 m çıkar. K2'de 6,0 m hedefle 9 parsel ve 6,37 m çıkar.
- **Ön eşik.** `ON_ESIK_K2` = 1,0 m.
- **Arka kanat.** `T3_ARKA_DER` = 5 m, `T3_ARKA_KONUT` = 2. Güney sıra grubun yan kanatları arka kanada kadar uzar. Kuzey sıra grupta yan kanatla komşu arka kanat arasındaki açıklık 0,3 m'lik duvar poligonuyla kapanır. Avlu poligonu bütün binalar çıkarılarak hesaplanır.

#### 3.5.3 Çelişkiler ve kararlar

1. **H/W 0,78 ↔ kış güneşi.**
   - **Etki.** D–B uzanan S2'de kuzey sıranın güneye bakan cephesinde 21 Aralık öğle gölgesi 3,1 m'den 3,6 m'ye çıkıyor. Zemin kat tümüyle, birinci kat penceresinin alt kenarı da gölgede kalıyor. 21 Mart'ta cephe tümüyle güneşte.
   - **Karar.** Yalnız K2'de uygulandı. Sokak kapalılığı, yavaşlatma ve "insan ölçeği" kış öğlesinde zemin kat güneşine yeğlendi.
   - **Sınırlar.** K1'de 2,0 m eşik (H/W 0,66) ve S2'de güney cephe saçağının 9,5 m sınırı korundu. T1 çekirdek döneminde (Z+1) H/W 0,65'tir; sokak genişleme tamamlanana kadar daha açık kalır.
   - **Kayıt.** Ölçüt 6 bu sokaklarda sağlanmıyor ve bu durum kayda geçti.
   - **Yerel ayar.** Gerçek alanda K–G uzanan S2'lerde 1,0 m, D–B uzananlarda 1,5 m eşik düşünülebilir.
2. **Avluyu kapatma ↔ gölge.**
   - **Kuzey avlu.** Güney grubun arka kanadı kuzey avlunun güney kenarında duruyor. 21 Aralık öğlesinde kuzey avlunun ≈ %36'sı (7,1 m), 21 Mart'ta ≈ %15'i (3,0 m) gölgede.
   - **Neden tek kat?** İki katlı bir kanadın gölgesi ≈ 13,6 m olur ve kışın kuzey avlunun ≈ %70'ini kaplardı. Kanat bu yüzden tek katlı tutuldu. Kuzey avlu daha büyük bırakıldı (medyan 532 m²) ve oyun alanı ortasına kondu.
   - **Kuzey grubun kendi kenarı.** Kuzey gruba kendi arka kanadı verilmedi; kenarını 2,5 m'lik duvarlar kapatıyor.
   - **Güney avlu.** Kış öğlesinde kendi sokak kanadının gölgesinde; bu v2.0'da da öyleydi.
3. **9–12 m modül ↔ asansör kuralı.**
   - **Ayrı binaya bölmenin bedeli.** T3 sokak kanadı ya da T4 çubuğu 9–12 m'lik ayrı binalara bölünseydi her Z+3 bina kendi asansörünü isterdi. T4'te 24 m'lik parselde asansör sayısı 1'den 2'ye çıkardı; hane başına bedel 144'ten ≈ 290 bin TL'ye yükselirdi. T3 Z+3'te 2'den 3–4'e çıkardı.
   - **Karar.** Modül cephe ritmi olarak uygulandı: her 9–12 m'de ayrı giriş ya da cephe kırığı, saçak ve renk değişimi (Fıtrat Kodu §3.1). Ölçülen cephe adımı 17,1 m oldu (≤ 20).
   - **Sonraki adım.** P4 (galeriyle bağlı en çok üç merdiven evine tek asansör) yürürlüğe girerse T4 2 × 12 m'lik ayrı binalara bölünebilir.
4. **Geçit ↔ arazi ve T1.**
   - **Bedel.** Geçitler 0,64 ha tuttu. Raporun tahmini 1,2–1,8 ha idi; T3 adaları zaten geçitliydi. Net konut alanı 26,51 ha'ya, T1 payı %22,8'e indi.
   - **Telafi.** Rapor iki telafi yolu öneriyordu: T1 derinliği ve K3 oturumu. Telafi, T3 grubunun oturumunu artıran arka kanatla sağlandı.
5. **Kapalı avlu ↔ acil durum erişimi** (rapor §3.2 sınama 3).
   - **Durum.** Güney avlulara giriş sokak kanadındaki kapı altı geçitten. Geçit 3,5 m geniş, ama net yüksekliği konut zemininde 3,1 m; dükkânlı zeminde 4,5 m.
   - **Eksik.** 4 m net yükseklik için geçidin üstündeki tek açıklıkta döşemenin ≈ 0,9 m yükseltilmesi gerekir. Bu, Fıtrat Kodu'na kural olarak yazıldı; maliyeti ve tipoloji çizimi doğrulanmadı [DY].
   - **Kuzey avlular.** Duvara 3,5 m'lik kapı açılabilir.
6. **1,0 m ön eşik ↔ PAİY'nin 5 m ön bahçe varsayılanı** (sınama 2). v2.0'daki 1,5 m'de de aynı çatışma vardı. Md. 30 kapsamındaki kentsel tasarım projesi ve plan notu gerekir [DY].

#### 3.5.4 FUE kontrolü ve mahalle ölçeği

FUE puanı `05_ANALIZ/kod/fue_model_mahalle.py`'nin yüzdelik kuralıyla, 300 kentsel pilot mahallenin dağılımına göre yeniden hesaplandı.

| Eksen | v2.0 | v2.1 |
|---|---|---|
| Erişim (E) | 82,4 | 82,4 |
| Çevre-ölçek (Ç), tek muhtarlık | 62,3 | **62,8** |
| Çevre-ölçek (Ç), iki muhtarlık | 65,2 | **65,6** |
| FUE (altı boyut) | 74,5 | 74,7 |
| Yaşanan yükseklik (konut ağırlıklı kat × 3,1) | 9,9 m | **9,6 m** |

- **Kalibrasyon Ç'yi düşürmedi.** Tek katlı arka kanatlar yaşanan yüksekliği pilot medyanına (8,4 m) 0,3 m yaklaştırdı. `fue_model_mahalle.py` v2.0 için 9,5 m varsaymıştı. Kavşak, zemin payı ve donatı göstergeleri ya aynı kaldı ya da arttı.
- **Ç'yi aşağı çeken girdi yaşanan yükseklik.** Tek muhtarlıktaki 6.925 kişi ise pilot kentsel mahallelerin medyanında (6.778 kişi); bu gösterge ≈ 50 puan veriyor ve tek başına Ç'yi aşağı çekmiyor.

**Ölçek notu.** Model mahalle, idari anlamda tek bir mahalle olarak okunmamalı. Model 60 ha ve ≈ 6.900 kişi; iki muhtarlık ya da 8 komşuluk biriminden oluşan bir **semt parçasını** temsil ediyor.

- **İki muhtarlık önerisi.** Doğal sınır E–W mahalle caddesi (S1):
  - kuzey yarı KB-3, 4, 5, 6: 1.126 hane ≈ 3.600 kişi, ilkokul B;
  - güney yarı KB-1, 2, 7, 8: 1.038 hane ≈ 3.320 kişi, ilkokul A.
- **Etkisi.** İki muhtarlıkla muhtarlık başına ≈ 3.460 kişi düşer; bu, pilotların %29'undan küçük demek. Ç 65,6'ya çıkar.
- **Komşuluk birimi.** 208–309 hane, ≈ 650–990 kişi. Yüz yüze tanışma ölçeği budur; muhtarlık yönetim ölçeğidir.

---

## 4. Ana metrikler (hedeflerle)

Tam tablo `model_mahalle_v2/metrikler.csv`'dedir (146 satır; v1, v2.0 ve v2.1 sütunları).

| Gösterge | v1 | v2.0 | v2.1 | Hedef | Durum |
|---|---|---|---|---|---|
| Konut | 2.222 | 2.163 | **2.164** | 2.250 | yakın (−%3,8) |
| Nüfus (3,2 kişi/hane) | 7.110 | 6.922 | 6.925 | 7.200 (6.000–8.000) | uyumlu |
| Brüt yoğunluk (kişi/ha) | 118,5 | 115,4 | 115,4 | 120 (100–150) | uyumlu |
| Net konut yoğunluğu (konut/ha) | 81,4 | 79,7 | 81,6 | ≈ 70 (50–90) | uyumlu |
| T1 · T2 · T3 · T4 konut | 447 · 470 · 1.093 · 212 | 534 · 422 · 995 · 212 | **493 · 388 · 1.071 · 212** | 650 · 400 · 1.050 · 150 | T1 geride |
| ≤ 3 · ≤ 4 katlı binada oturan | %70,1 · %97,5 | %70,1 · %97,5 | **%70,1 · %97,5** | ≈ %70 · ≈ %93 | uyumlu |
| 3+1 ve üstü · 2+1 · 1+1 | %58,9 · %35,2 · %5,9 | %62,0 · %32,4 · %5,6 | %59,3 · %35,1 · %5,6 | ≥ %55–60 · ≈ %20 · %5–10 | uyumlu (2+1 fazla) |
| Konut dışı kat alanı | %14,4 | %17,5 | %17,5 | %15–25 | uyumlu |
| Sokak, yaya yolu, meydan | 16,6 ha | 16,6 ha | 17,2 ha | 15,0 | yakın |
| Kamusal yeşil | 9,41 ha · 13,2 m²/kişi | 8,52 ha · 12,3 | 8,53 ha · **12,3** | ≥ 10 m²/kişi | uyumlu |
| Eğitim | 2,55 ha · 3,59 | 3,38 ha · 4,88 | 3,38 ha · 4,88 | 4,5 | uyumlu |
| Teknik altyapı | 0,35 ha · 0,49 | 0,75 ha · 1,09 | 0,75 ha · 1,09 | ≥ 1,0 | uyumlu |
| Sosyal-kültürel (konak) | 0,52 ha · 0,74 | 0,58 ha · 0,84 | 0,58 ha · 0,84 | ≥ 0,75 | uyumlu |
| Bölgesel otopark | 1,26 ha · 0,56/hane | 1,03 ha · 0,57 | 1,03 ha · 0,57 | 0,5–0,7 / hane | uyumlu |
| Net konut alanı | 27,30 ha | 27,15 ha | 26,51 ha | tutarlı: 27,5 / 26,8 | yakın |
| Ağaç örtüsü (20 yıl) | %25,4 | %31,1 | **%31,1** | ≥ %30 | uyumlu |
| S2 · S1 H/W | 0,64 · 0,69 | 0,72 · 0,71 | **0,78 · 0,71** | 0,7–1,0 · 0,7–0,8 | uyumlu |
| Özel bahçe ve avlu (konut başına) | 59,1 m² | 59,7 m² | 54,6 m² | ≥ 10 m²/kişi (ölçüt 14) | uyumlu |
| Avlu + bahçe grubu | 192 | 186 | 186 | 190–280 | yakın |
| Sokak ağı · kavşak (yaya dahil) | 25,7 km/km² · 203 | 25,5 · 205 | **28,1 · 265** | ≥ 18 · ≥ 80–120 (rapor ≥ 300) | uyumlu |
| Kapalı avlu (M1) | 0 | 0 | **0,83/ha** | ≈ 0,5 | uyumlu |
| Komşuluk birimi (hane) | 214–328 | 204–311 | 208–309 | 150–300 | KB-4, KB-7 yakın |
| Tahsis: kooperatif · sosyal · piyasa | — | %29,5 · %19,6 · %50,9 | %30,3 · %19,8 · %49,9 | 30 · 20 · 50 | uyumlu |
| FUE Ç (tek muhtarlık) | — | 62,3 | **62,8** | ≥ 55 | uyumlu |

### Erişim (her konut için ağ mesafesi)

| Donatı | Hedef | v1 | v2.0 | v2.1 | v2.1 medyan · en uzak |
|---|---|---|---|---|---|
| **İlkokul** | ≤ 500 m | %96,8 | %100 | **%100** | 239 · 493 m |
| İlkokul (tercih) | ≤ 400 m | %74,5 | %90,7 | %91,0 | — |
| Ortaokul | ≤ 1.000 m | %100 | %100 | %100 | 559 · 913 m |
| Anaokulu ya da kreş | ≤ 400 m | %100 | %100 | %100 | 167 · 397 m |
| İbadet kademesi (mescit 150 / küçük cami 250 / semt camii 400 m) | %100 | %99,3 | %99,4 | %99,4 | — |
| Aile sağlık merkezi | ≤ 500 m | %96,5 | %96,4 | %96,7 | 349 · 558 m |
| ≥ 0,5 ha yeşil | ≤ 300 m (≤ 200 m) | %100 (%96,1) | %100 (%95,8) | %100 (%95,6) | 87 · 244 m |
| Kapı önü oyun alanı | avlu / ortak şerit / cep ≤ 150 m | %100 | %100 | %100 | — |
| Açık spor sahası (herhangi) | ≤ 500 m | %100 | %100 | %100 | 160 · 348 m |
| Bakkal, fırın ya da dükkân | ≤ 300 m | %100 | %100 | %100 | 88 · 295 m |
| Otobüs durağı | ≤ 300 m (≤ 400 m) | %99,1 (%100) | %98,8 (%100) | %98,8 (%100) | 154 · 329 m |
| Mahalle konağı | ≤ 500 m | %95,1 | %95,1 | %95,7 | 312 · 567 m |
| Bölgesel otopark | ≤ 400 m | %100 | %100 | %100 | 198 · 350 m |
| Su ve oturma noktası | ≤ 250 m | %100 | %100 | %100 | 129 · 248 m |

Geçitler erişim medyanlarını birkaç metre kısalttı (ilkokul 244 → 239 m, bakkal 94 → 88 m). Sınırdaki konutların sonucu değişmedi.

---

## 5. Simülasyonun C ortamı varsayımlarıyla karşılaştırma

Simülasyonun C ortamı (`05_zihinsel_simulasyonlar.md` §1.1, `persona_anlatilari.md`) taslak programdan türetilmişti. Sonuçlar 06_SIMULASYON'a geri bildirim olarak verilmeli.

| Varsayım (C) | Simülasyon | v2.1 planı [H] | Yorum |
|---|---|---|---|
| Zemine ya da avluya doğrudan açılan hane | ≈ %90 | **%62,6** | **İyimser.** T3 üst kat daireleri ortak avluya merdivenle iner. Salgın senaryosu yeniden hesaplanmalı |
| Bir yapıyı paylaşan daire | ≈ 7 | 4,7 | Simülasyon temkinli |
| Kişi başı özel bahçe / avlu | 10,9 m² | 17,1 m² | Simülasyon temkinli |
| Asansör | yalnız T3 (4 kat) ve T4 | Aynı; ayrıca T2 ve T3 Z+2'de asansör yeri | Tutarlı |
| Bakkal / mescit / ilkokul | 200 / 150 / 400 m | Medyan 88 / 125 / 239 m | Simülasyon temkinli |
| Komşuluk yeşili / durak | 180 / 300 m | Medyan 87 / 154 m | Simülasyon temkinli |
| Ağaç örtüsü | başlangıçta %15, 15–20 yılda %30 | 20 yılda %31 | Tutarlı |
| Yaşlı ve engelli zemin katta | Hüseyin ve Selin zemin katta | 362 eşiksiz zemin daire (%16,7) | Arz var; tahsis kuralı gerekir |
| Kapalı avlu (v2.1) | "avlu" genel | 38 kapalı + 40 duvarla kapalı avlu | Çocuğun göz altında oyunu için simülasyonla tutarlı |
| Dükkân | 80–120 dükkân, havza ≈ 3.500 kişi | ≈ 213 zemin kat konut dışı birim (≈ 33 kişiye 1) | Zemin ticaret fazla; esnaf riski (§6) |

---

## 6. Kalan açık sorunlar

1. **T1 payı %22,8** (hedef %29).
   - Raporun T1 cephesi önerisi ve geçitler payı v2.0'a göre 1,9 puan düşürdü.
   - Öneri: tipoloji hedefini %22–25'e indirmek. Geleneksel ölçüm 6,3 m'lik T1'i dar buluyor.
2. **Net konut alanı ve konut sayısı.** 26,51 ha (tutarlı hedef 26,8) ve 2.164 konut (−%3,8). Güncel EK-2, ≤ 3 kat payı ve geçitlerin bedeli.
3. **Yapı oturumu ve emsal.**
   - Brüt %23,6, hedef %25–30. Emsal 0,64, hedef 0,75–0,9.
   - Hedefe ancak kat artırarak ya da T1'i derinleştirip bahçeyi kısaltarak ulaşılır. Bu çalışmada ikisi de seçilmedi.
4. **S2'de kış güneşi.** H/W 0,78 için 21 Aralık öğlesinde karşı cephenin zemin katı gölgede (3,6 m). Ölçüt 6 ile çatışma bilinçli bir tercih olarak kayda geçti (§3.5.3-1).
5. **Kuzey avlunun gölgesi.** Kışın ≈ %36'sı gölgede (§3.5.3-2).
6. **Kapı altı geçidin yüksekliği.** Acil erişim için 4 m gerekiyor; konut zemininde 3,1 m [DY] (§3.5.3-5).
7. **T3/T4'ün 9–12 m modülü** yalnız cephe ritmi olarak uygulandı. Ayrı binaya bölmek paket P4'e bağlı.
8. **Tek merkezin sınırı.** ASM (%96,7) ve mahalle konağı (%95,7) 500 m'de %100 değil. Seçenek: okul B'nin yanında bir sağlık noktası ya da konak şubesi.
9. **Güney sıra bahçeleri.** T1/T2 konutlarının %43,6'sında bahçe evin kuzeyinde. Ada yönü gerçek alanda yeniden kurulmalı.
10. **Zemin kat konut dışı birim fazlası.** ≈ 213 birim, 33 kişiye 1. Çözüm "esnek zemin kat" tescili (paket K2).
11. **Otopark Yönetmeliği.** Plan, Ek-1'in bugünkü gereğinin %50'sini sağlıyor. O1 + O2 olmadan ruhsat yok [D/DY].
12. **KB-4 (306) ve KB-7 (309)** 300 hane sınırını biraz aşıyor.
13. **Maliyet, deprem, MEB ve EK-2 yorumları** [V/DY]: asansör fiyatları, TBDY 2018, okul B norm kadrosu, ASM'nin 1,5 m²/kişi yorumu.
14. **Mescit 150 m.** Saf ölçütle %74,1. Kademeli kuralın kalıp kalmayacağı karar bekliyor.
15. **Gerçek alan.** Topoğrafya, mülkiyet, pilot ilçe. Rapor eğimli arazide ızgaranın eş yükselti eğrisine göre bükülmesini öneriyor; v3'e kaldı.

## 7. Varsayımlar ve sınırlılıklar

v1'in varsayımları (§8) geçerlidir: hane büyüklüğü 3,2, düz arazi, ağda her kavşakta serbest geçiş. Ek olarak:

1. **Öğrenci sayısı.** 6–9 yaş payı %6 ve 28 öğrenci/derslik [V].
2. **Ağaç taç yarıçapları** 20 yıl içindir [V].
3. **Maliyet.**
   - Asansör 1,3 milyon TL (4 durak), her ek durak +0,1 milyon TL; platform 0,9 milyon TL; bakım 48 bin TL/yıl [V].
   - Yapım maliyeti 2026 tebliğinden, %10 kâr hariç [D, M6 ile aynı].
   - Arka kanat 2+1 brüt 90 m² [V].
4. **Otopark Ek-1 hesabı.** Brüt alanlar tipoloji çizimlerinden (`tipoloji_verisi.BB`).
5. **Şematik seçenek ağı.** Sayıları plan sayısı değildir.
6. **Morfoloji ölçümü.**
   - Model ölçümü betiğin `MODEL_ALANLAR` yolunu izler: bina poligonları, kat, nüfus ve hane plandan, sokak ağı yaya ağından gelir.
   - Bahçe duvarları bina sayılmaz.
   - H/W 3,0 m kat yüksekliğiyle hesaplanır (plan 3,1 m).
   - Gerçek dokularla karşılaştırma raporun kapsama ve güvenilirlik işaretlerine (\*, ‡) bağlıdır.
7. **FUE.** Yaşanan yükseklik, konut ağırlıklı kat × 3,1 m ile hesaplandı [H]. Pilot mahallelerde GHSL ölçümü kullanılıyor; iki büyüklük tam eşdeğer değil [DY].
8. **Mevzuat.** Bütün maddeler proje mevzuat paketinden aktarıldı; yorumlar hukuki görüşle doğrulanmalı.

## 8. Yeniden üretim

```
cd 07_TASARIM_CIZIM/model_mahalle_v2/kod
python hepsini_calistir.py              # v2.1 (varsayılan): bütün çizimler, metrikler.csv, morfoloji
MM_SURUM=2.0 python vaziyet_plani.py    # v2.0'ı aynı koddan çizmek için (çıktının üzerine yazar)
```

**Gerekenler.**

- Python 3.11, matplotlib, shapely ≥ 2, networkx, numpy; DXF için ezdxf.
- Morfoloji için `03_VERI/kod/morfoloji_olcum.py`'nin bağımlılıkları: geopandas, pyproj, rasterio, scipy, pandas. Raporun alan verileri `03_VERI/` altında olmalı.
- FUE için `05_ANALIZ/sonuclar/fue_mahalle.csv` ve `fue_gosterge_tanim.csv`.
- Bunlar yoksa ilgili satırlar atlanır.

**Yalnız okunan dosyalar.** v1 kodu (`../../model_mahalle/kod`) ve morfoloji betiği ayrı süreçte ya da içe aktarılarak yalnız okunur. Bayt kodu yazılmaz; hiçbir v1 dosyası, morfoloji dosyası ya da FUE dosyası değişmez.

**Tasarım anahtarları** `plan_modeli.py`'nin başındadır:

- v2.0: `ILKOKUL_B_ADA`, `TEKNIK_SERIT`, `MOBILITE_KAT`, `KOSE_BINA_ESIK`, `ON_ESIK_K1/K2`, `PROGRAM`, `KISMI`, `TAC_R20`, `AGAC_ARALIK`, `TAHSIS_HEDEF`;
- v2.1: `GECIT_G`, `T1_GEN_K1`, `T3_ARKA_DER`, `T3_ARKA_KONUT`.

Kuzey okulunun yeri `MM_ILKOKUL_B_ADA=3,7` ile denenebilir. v2.0'daki aday sonuçları:

| Ada | ≤ 500 m | ≤ 400 m |
|---|---|---|
| (3,8): seçilen | %100 | %90,7 |
| (2,8) | %100 | %91,0 |
| (3,7) | %100 | %90,9 |
| (2,7) | %100 | %91,6 |

**Neden (3,8)?** (3,8) ile (2,8) neredeyse eşit sonuç veriyor. Kuzey mobilite noktası (2,9)'da olduğu için (3,8)'de okul kapıları otopark trafiğinden uzak kalıyor.
