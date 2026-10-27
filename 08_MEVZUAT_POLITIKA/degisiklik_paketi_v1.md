# Mevzuat Değişiklik Paketi — Sürüm 1 (İP8)

*26 Ekim 2026 · Sürüm 1.0 · Taslak, hukuki görüş değildir*

| Ne | Nerede |
|---|---|
| Önceki mevzuat analizi (kaldıraçlar, paydaşlar) | [mevzuat_politika_haritasi.md](mevzuat_politika_haritasi.md) |
| Finansman modeli (M6): kod, CSV, iki grafik | [finansman_modeli/](finansman_modeli/) · ana dosya `m6_konut_ekonomisi.py` |
| Politika notları (3 adet) | [politika_notlari/](politika_notlari/) |
| Özet rapor | [09_RAPORLAR/06_politika_paketi_ozet.md](../09_RAPORLAR/06_politika_paketi_ozet.md) |
| Kanıt tabanı (Faz 2) | [02_il_paneli_mekanin_payi.md](../09_RAPORLAR/02_il_paneli_mekanin_payi.md) · [03_ilce_paneli_il_ici.md](../09_RAPORLAR/03_ilce_paneli_il_ici.md) |
| **Sürüm 2 (27.10.2026): +24 öneri** (arsa değer vergisi, karma kullanım, semt meclisi; sermaye geliri, taban gelir, esnaf ve rekabet, gıda zinciri); I3, K2, B1 genişletildi | [degisiklik_paketi_v2.md](degisiklik_paketi_v2.md) |

---

## Okuma kılavuzu

**Doğrulama yöntemi.** Madde metinleri 26.10.2026'da mevzuat.gov.tr'deki güncel konsolide metinden (`MevzuatFihristDetayIframe` uç noktası) okundu. Yönetmelik ekleri (MPYY EK-2, Otopark Yönetmeliği Ek-1) mevzuat.gov.tr'deki ek dosyalardan açıldı. Resmî Gazete künyeleri iki yoldan teyit edildi: mevzuat.gov.tr'deki künye tablosu ya da resmigazete.gov.tr günlük fihristi.

| Etiket | Anlamı |
|---|---|
| **[D]** | Doğrulandı: birincil kaynaktan (mevzuat.gov.tr, Resmî Gazete) 26.10.2026'da okundu |
| **[K]** | Kısmen doğrulandı: ikincil yayından (mevzuat yayın siteleri, basın) |
| **[DY]** | Doğrulanmadı: kullanmadan önce birincil kaynakta kontrol edilmeli |

**Kanıt düzeyi** (önerilerin gerekçesi için): **G** güçlü · **O** orta · **Z** zayıf · **N** normatif (hak, hakkaniyet, usul gerekçesi; ampirik iddia yok).

**Taslak metin dili.** "Önerilen metin" sütunlarındaki ifadeler madde yazımı için çalışma taslağıdır. Fıkra numaraları, mevcut metne eklendiğinde yeniden düzenlenmelidir. Bir hukukçu ve ilgili kurum (ÇŞİDB MPGM, Adalet Bakanlığı, İçişleri Bakanlığı) incelemesinden geçmeden kullanılmamalıdır.

---

## 0. Paketin mantığı: neyi, hangi gerekçeyle, hangi yoldan?

### 0.1 Kanıt neyi söylüyor, neyi söylemiyor?

Faz 2'nin iki paneli mekânın doğurganlığa **doğrudan** etkisinin küçük olduğunu gösterdi:

- **İl paneli (81 il):** Mekân, iller arası doğurganlık farkının %13'ünü açıklıyor. 12 bölge sabit etkili modelde bu pay **%5'e** iniyor.
- **İlçe paneli (973 ilçe, il sabit etkili):** Kadın eğitimi sabit tutulunca bir kat (≈3 m) daha yüksek binada yaşanan ilçelerde doğurganlık **≈0,03 çocuk** daha düşük. Dürüst aralık bir kat başına −0,03 ile −0,14 çocuk; en olası değer alt uca yakın. İl içi açıklanan farkın %76'sı eğitime, %19–22'si mekâna düşüyor.
- **Üst sınır simülasyonu:** Büyükşehirlerde yaşanan bina yüksekliği 10,2 m'den 6 m'ye indirilse, eğitim sabitken doğurganlık en fazla **+0,04 çocuk** artar.

Bu yüzden paket, mekân düzenlemelerini doğurganlık vaadiyle değil şu **beş gerekçeyle** savunur:

| Gerekçe | Kanıt (02_LITERATUR, Faz 1 raporu) |
|---|---|
| Sağlık | Konuta yakın yeşil alan ruh sağlığını iyileştirir (O–G). Dışarıda geçen süre çocuklarda miyopiyi azaltır (G, nedensel). Yürünebilir mahallede haftada 68–89 dk daha fazla fiziksel aktivite (O–G) |
| Çocuk gelişimi | Güvenli sokak, avlu ve okula yürüme. Japonya'da 5. sınıfların %92–93'ü okula yürüyor (D) |
| Komşuluk ve yalnızlık | Yalnızlık ölüm riskini %26–32 artırır (G). Yüksek katlı konut çocuklu ailelerde komşuluk bağlarını zayıflatır (O–Z) |
| Kuşaklar arası yakınlık | Büyükanne-büyükbaba yakınlığı ek çocuk ve annenin işgücüne katılımıyla ilişkili (O). 65+ nüfusun %50,6'sı çocuğuyla aynı adreste, binada ya da sokakta (TÜİK) |
| Deprem güvenliği | 6 Şubat 2023: ≈518 bin yıkık veya ağır hasarlı konut (ikincil kaynak). Az katlı yeniden yapımda yapım ve yerinden edilme süresi kısa (M6 modeli; bkz. Bölüm 10) |

**Doğurganlık için** asıl kaldıraçlar mekân dışında: kadın eğitimiyle aile kurmayı uyumlu kılmak (evlilik ve ilk doğum zamanlaması), **konut erişimi** (konut maliyeti kiracıların doğurganlığını %2,4 düşürüyor, ev sahiplerininkini %5 artırıyor; O, yarı deneysel) ve iş-aile dengesi. Paket bu yüzden imar araçlarını **konut finansmanı** (Bölüm 11) ile birlikte sunar ve her önerinin kanıt düzeyini ayrıca yazar.

### 0.2 Üç ilke

1. **Varsayılanı değiştir, zorlama.** Bugünkü biçim (ayrık nizam kule, parsel içi otopark, küçük daire) büyük ölçüde varsayılan kuralların ürünü. Paket mevcut imar haklarını kısmaz. Az katlı, avlulu ve aile ölçekli seçeneği kolaylaştırır, ucuzlatır ve hızlandırır. Hak kısıtlaması gereken her yerde karşılık (emsal transferi, harç indirimi) önerilir.
2. **Mülkiyet ve hürriyet.** Zorlayıcı dönüşüm yok. 6306'daki salt çoğunluk kuralı genişletilmez; tersine azınlıktaki malik için güvenceler önerilir (Bölüm 5).
3. **Ölçülebilirlik.** Her öneri için izlenecek gösterge ve veri kaynağı tanımlıdır (Genelge 2026/4 kapsamındaki ölçüt listesi, Bölüm 9).

### 0.3 Bu çalışmada ortaya çıkan beş mevzuat bulgusu

1. **Otopark Yönetmeliği aile konutunu cezalandırıyor.** Ek-1'e göre bağımsız bölüm brüt alanı 120 m²'yi geçen dairede otopark ihtiyacı iki katına çıkıyor (2 daireye 1 yerden daireye 1 yere) [D]. M6 modelinde 124 m²'lik çok kuşaklı sıra evin otopark yükü 43,8 milyon TL/ha. Bu, 90 m²'lik dairelerden oluşan bloğun yükünün 5,5 katı.
2. **6306 ve riskli yapı istisnası dikey dönüşümün gizli teşviki.** 3194 Ek md. 8'in son fıkrasına göre 6306 kapsamındaki alanlarda ve emsalin en fazla %20 artırıldığı riskli yapı parsellerinde maddenin tamamı uygulanmaz [D]. Bu alanlarda parsel bazlı yoğunluk artışı yasağı da %90'lık değer artış payı da işlemez.
3. **Emsal transferi hukuken var, ama dar.** 3194 md. 13, 7534 sayılı Kanunla (RG 12.12.2024, 32750) "imar hakkı aktarımı" yolunu açtı [D]. Ancak yalnız umumi hizmet alanına ayrılan ve kamuya bedelsiz devredilen parseller için. Gönüllü olarak daha az katı seçen malikin kullanmadığı hakkı devredebileceği bir yol yok.
4. **MPYY'nin yürüme mesafeleri bağlayıcı değil.** md. 12/2, kreş, ilkokul, oyun alanı ve aile sağlık merkezinin yaklaşık 500 m mesafe dikkate alınarak "planlanabilir" olduğunu söylüyor [D]. Ölçümün yaya ağı mı kuş uçuşu mu olduğu yazılı değil.
5. **EK-2'nin güncel değerleri projede eski bir aktarımla kullanılmış.** EK-2'nin 17.05.2017 değişikliğiyle güncel tablosunda ilkokul ve ortaokul **2,0 m²/kişi** (asgari 5.000–8.000 ve 6.000–10.000 m²), aile sağlık merkezi 1,5 m²/kişi, sosyal-kültürel tesis 0,75–1,5 m²/kişi, teknik altyapı 1,0–2,0 m²/kişi, açık-yeşil alan ilçe ölçeğinde 10, il ölçeğinde +5 m²/kişi [D]. `07_TASARIM_CIZIM/tasarim_parametreleri.md` §6.2'deki tablo (TBB aktarımı, ilkokul 1,5–1,6) bu değerlerin gerisinde. 7.200 kişilik taslak mahalle programındaki 1,08 ha'lık ilkokul ve ortaokul alanları güncel standardın (her biri 1,44 ha) altında kalıyor. Tasarım ekibinin bu tabloyu güncellemesi gerekiyor.

**Ayrıca iki küçük düzeltme:**

- PAİY md. 19/1-f-5'teki gündüz bakımevi eşiği "15.000 m² **ve** 150 bağımsız bölüm" [D]. Mevzuat haritasında "ya da" yazılmıştı.
- "Aynı yoğunluk, üç biçim" metrik tablosunda B (zemin + 3, toplam 4 kat) için "asansör gerekmez" yazıyor. PAİY md. 34/1'e göre (01.07.2026 değişik) bodrum dahil kat adedi 4 ve üzeri binalarda asansör tesisi, 3 katlı binalarda asansör yeri bırakılması zorunlu [D]. C'de de (3 kat, parsel başına 2 bağımsız bölüm) asansör yeri bırakılmalı.

---

## Paketin özeti: 28 öneri

Öncelik: **1** = 2027 içinde, mevcut yetkiyle (yönetmelik, genelge, idari karar) · **2** = 2027–2028 eylem planı dönemi · **3** = kanun değişikliği gerektirir (2028 ve sonrası).

| # | Araç | Mevzuat ve madde | Öneri (kısa) | Kanıt | Öncelik |
|---|---|---|---|---|---|
| P1 | Yönetmelik | PAİY md. 23 | "Aile dostu ada düzeni": ön bahçe 0–3 m, bitişik nizam, ada içi ortak avlu | O (sağlık, çocuk); N | 1 |
| P2 | Yönetmelik | PAİY md. 9 | Plansız parselde malik talebiyle daha az kat + kullanılmayan emsalin aktarımı | N | 2 |
| P3 | Yönetmelik | PAİY md. 5/8, 19 | Komşuluk odası ve oyun avlusu emsal dışı; eşikler 30–50 bağımsız bölüme | O | 1 |
| P4 | Yönetmelik | PAİY md. 34 | Az katlı bitişik nizamda ortak asansör ve zemin katta erişilebilir daire seçeneği | Z (maliyet); N (erişim) | 2 |
| P5 | Yönetmelik / plan notu | PAİY md. 5/25 | 50+ bağımsız bölümlü projelerde daire karması; aile konutu tanımı | O (konut erişimi) | 2 |
| M1 | Yönetmelik | MPYY md. 11, EK-2 | Çocuk donatısını yaş yapısına bağlamak | O; 12. KP 851.6 | 1 |
| M2 | Yönetmelik | MPYY md. 12 | "Planlanabilir" yerine "planlanır"; yaya ağı mesafesi; araç yolu geçmeden okul | O–G | 1 |
| M3 | Yönetmelik | MPYY md. 12 (yeni fıkra) | Yeşil erişim standardı: her konuta 300 m yaya ağı içinde ≥ 0,5 ha | O–G | 1 |
| M4 | Yönetmelik | MPYY md. 7 ve 26 | Mahalle donatı dengesi tablosu; plan değişikliğinde aile ve nüfus etki bölümü | N | 1 |
| O1 | Yönetmelik | Otopark Yön. Ek-1 | Daire büyüklüğü eşiği yerine hane başına ihtiyaç; aile konutuna ek yük yok | Modelde hesaplandı (H) | 1 |
| O2 | Yönetmelik | Otopark Yön. md. 4 ve 8 | Plan kararıyla "bölgesel otopark alanı"; raylı sistem çevresinde azami otopark | O (Vauban, Poundbury dersi) | 1 |
| O3 | Yönetmelik (+ kanun teyidi) | Otopark Yön. md. 13 | Bedel gelirinin yaya, bisiklet, okul yolu ve durak güvenliğine de harcanabilmesi | Z–O | 2 |
| I1 | Kanun / yönetmelik | 3194 Ek md. 8 | Altyapı etki raporuna aile ve nüfus etki bölümü; 500 m'nin yaya ağı mesafesi olması | N; O | 1 (yönetmelik) |
| I2 | Kanun | 3194 Ek md. 8 son fıkra | 6306 ve %20 istisnasında 1:1 yeniden yapımı aşan emsale değer artış payı | N (hakkaniyet); H | 3 |
| I3 | Kanun | 3194 Ek md. 8/a–c | Değer artış payı gelirinin bir kısmının aile ve çocuk donatısına ayrılması | N | 3 |
| I4 | Kanun + yönetmelik | 3194 md. 5 ve 13 | Gönüllü kat sınırlaması karşılığında imar hakkı aktarımı (TDR) | H (M6) | 3 |
| D1 | Yönetmelik | 6306 Uygulama Yön. | Ada bazlı uygulama önceliği; aile ve nüfus etki değerlendirmesi; yerinde kalma | O; N | 1 |
| D2 | Kanun | 6306 md. 6 | Salt çoğunlukla karar verilen projelerde azınlık malike güvence | N | 3 |
| D3 | Kanun | 6306 md. 7/10 | Az katlı ada projelerinde harç ve ücret muafiyetinin genişletilmesi | H | 3 |
| K1 | Rehber + kanun | 634 md. 28, 42, 66–74 | Örnek yönetim planı: ortak avlu ve komşuluk alanları; kapatılmalarının zorlaştırılması | Z–O; N | 1 (rehber) |
| K2 | Kanun | 634 md. 24 | Meskende küçük gündüz bakımevi ve ev-atölye için oybirliği yerine nitelikli çoğunluk | Z; N | 3 |
| B1 | Belediye meclisi kararı | 5393 md. 18, 76, 77 | Mahalle meclisi ve katılımcı mahalle bütçesi pilotu | O–Z (ampirik); G (normatif) | 1 |
| B2 | Kanun | 5393 md. 9 | Mahalle ihtiyaç planı ve mahalle danışma kurulu | Aynı | 3 |
| T1 | İdari karar | 2985 md. 4; TOKİ tip projeleri | Kalan etaplarda 3+1, 4+1, büyüyebilen ve çok kuşaklı tipler; az katlı avlulu ada | O; N | 1 |
| G1 | Genelge uygulaması | Genelge 2026/4 md. 2 ve 9 | Aile ve Nüfus Etki Değerlendirmesi için 24 imar ölçütü | Ölçüt bazında | 1 |
| F1 | Cumhurbaşkanı kararı | 492 sayılı Kanun (4) sayılı tarife 20/a | Aile konutunun ilk satışında tapu harcının indirilmesi | H | 1 |
| F2 | Kanun / program | Aile konut kredisi | TÜFE endeksli, reel %2, 240 ay | H (M6) | 2 |
| F3 | Yönetmelik / idari | 1163 Ek md. 6; kamu arsası | Aile konut kooperatifi ve arsa vakfı (üst hakkı) modeli | H; Viyana, Batıkent dersi | 2 |

---

## 1. Planlı Alanlar İmar Yönetmeliği (PAİY)

**Künye [D]:** RG 03.07.2017, sayı 30113. 23 değişiklik yönetmeliği. Son değişiklik RG 01.07.2026, sayı 33297. Dayanak: 3194 sayılı İmar Kanunu ve 1 sayılı CBK (md. 3).

### P1 · Bahçe mesafeleri ve "aile dostu ada düzeni" (md. 23)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 23/1: "Uygulama imar planında, aksine bir hüküm bulunmadığı durumlarda" ön bahçe ve kamusal alana komşu bahçe en az 5,00 m; yan ve arka bahçe en az 3,00 m; dörtten fazla katlı binalarda 4. kattan sonraki her kat için yan ve arka bahçeye +0,50 m. md. 4: avlu "kısa kenarı 5,00 metreden az olmayan" üstü açık yapı bölümü; md. 20/8-a: zemin seviyesindeki avlular taban alanına dahil değil. md. 5/6 (01.07.2026 değişik): planda belirtilmemişse ayrık ve blok nizamda TAKS %40'ı geçemez |
| **Sorun** | Planlar çoğunlukla bu varsayılanı kullanıyor. Sonuç: ayrık nizamda parsel çevresinde kullanılamaz bahçe şeritleri, yola 5 m geri çekilmiş, sokakla ilişkisi kopuk binalar. Plan notuyla farklı bir düzen kurmak zaten mümkün ("aksine bir hüküm"). Ancak hazır, denetlenebilir bir alternatif tanım olmadığı için uygulanmıyor |
| **Önerilen metin** | md. 23'e fıkra: "(10) Uygulama imar planında 'aile dostu ada düzeni' olarak belirlenen adalarda; a) ön bahçe mesafesi 0 ile 3,00 metre arasında plan notuyla belirlenir; b) yapılar bitişik nizamda düzenlenir, yan bahçe aranmaz; c) arka bahçeler birleştirilerek ada içinde kısa kenarı bina yüksekliklerinin ortalamasından ve 15,00 metreden az olmayan ortak avlu oluşturulur; ortak avlu taban alanı ve emsal hesabına dahil edilmez, üzerinde bina yapılamaz, kat mülkiyeti kütüğünde ortak alan olarak gösterilir; ç) bina yüksekliği zemin kat dahil 4 katı geçemez; d) bu düzende yan ve arka bahçeler için birinci fıkranın (ç) bendindeki artış uygulanmaz." md. 4'e tanım: "Aile dostu ada düzeni: konutların zemin dahil en fazla 4 katlı bitişik nizam yapılarla ada çevresine dizildiği, ada içinin ortak avlu olarak bırakıldığı yapı düzeni." |
| **Beklenen etki** | M6 modelinde aynı 1 ha'da avlulu Z+2 sıra ev (C) 12.960 m², Z+3 çevre adası (B) 12.288 m² inşaat alanı veriyor; 12 katlı blok (A) 10.584 m². Yani az katlı düzen aynı yoğunlukta **daha fazla** alan üretebiliyor (emsal 1,23–1,30). Konutların %100'ü zemin + 3 kat içinde (A'da %33) |
| **Kazanan / kaybeden** | Kazanan: çocuklu aileler, yaşlılar, küçük yapımcılar, arsa sahibi (bkz. finansman, Bölüm 12). Kaybeden yok; düzen isteğe bağlı. Risk: ada içi avlunun bakım sorumluluğu (bkz. K1); güney cephesi az olan adalarda gün ışığı (avlu kısa kenarı kuralı bunun için) |
| **Araç** | ÇŞİDB: PAİY değişikliği. Uygulamada belediye meclisi: plan notu |

### P2 · Plansız kat adedi (md. 9)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 9/1: yönetmeliğin yürürlüğünden önceki planlarda kat adedi belirtilmemiş parsellerde kat adedi yol genişliğine göre bulunur: yol ≤7 m: 2 · 7–10 m: 3 · 10–12 m: 4 · 12–15 m: 5 · 15–20 m: 6 · 20–25 m: 8 · 25–35 m: 10 · 35–50 m: 14 · >50 m: 18 kat (bodrum hariç) |
| **Sorun** | Tablo, 15 m'nin üzerindeki her yol için 6–18 katlık bir "hak" üretiyor. Bu hak mülkiyetin parçası sayıldığı için kısılması hem hukuken hem siyaseten zor. Az katlı seçen malik ise hakkını kaybediyor |
| **Önerilen metin** | md. 9'a fıkra: "(2) Birinci fıkraya göre kat adedi belirlenen parsellerde, malik veya maliklerin talebi üzerine, ada bazında 23 üncü maddenin onuncu fıkrasındaki aile dostu ada düzeni uygulanabilir. Bu durumda kullanılmayan emsale esas inşaat alanı, 3194 sayılı Kanunun 13 üncü maddesindeki imar hakkı aktarımı usulüyle aktarılabilir ve tapu kütüğünün beyanlar hanesine şerh edilir." (Aktarım hükmü için I4'teki kanun değişikliği gerekir) |
| **Beklenen etki** | Hak kısıtlaması yok. Az katlı seçenek, kullanılmayan hakkın değeriyle telafi ediliyor (M6: İstanbul fiyatında aktarılan emsal başına ≈14.600 TL arsa değeri) |
| **Kazanan / kaybeden** | Kazanan: az katlıyı seçmek isteyen malik. Risk: alıcı bölgede yoğunluk birikmesi. Alıcı bölge plan kararıyla ve toplu taşıma koridorunda seçilmeli |
| **Araç** | ÇŞİDB: PAİY değişikliği + 3194 md. 13 değişikliği (I4) |

### P3 · Ortak komşuluk alanları (md. 5/8 ve md. 19)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 19/1-f-5 (RG 13.08.2025): konut parsellerinde yapı inşaat alanı 15.000 m²'den **ve** bağımsız bölüm sayısı 150'den fazla ise 0–66 aylık çocuklar için ≤200 m² gündüz bakımevi ve korunaklı oyun bahçesi. md. 19 (h bendi): 75'ten fazla bağımsız bölümlü konut parsellerinde mescit ve çocuk oyun alanı. md. 5/8: emsal harici alanların toplamı emsale esas alanın %30'unu aşamaz; ortak alan niteliğindeki mescidin konutlarda 150 m²'si emsal dışı |
| **Sorun** | Eşikler yüksek. Orta ölçekli apartman ve küçük ada projeleri ortak alansız kalıyor. Ortak alan emsal içinde sayıldığı için müteahhit açısından satılamayan bir maliyet |
| **Önerilen metin** | md. 5/8'e bent: "Konut yapılarında zemin katta veya ada içi ortak avluya açılan, her bağımsız bölüm için 1,5 m² ve toplam 300 m²'yi aşmayan ortak komşuluk odası (çocuk oyun, yaşlı buluşma, ev ödevi, ortak mutfak kullanımlı); bu alan %30 tavanına dahil edilmez ve bağımsız bölüme dönüştürülemez." md. 19 (h bendi): "yetmiş beşten fazla" ibaresi "otuzdan fazla" olarak; md. 19/1-f-5: "15.000 m²'den ve bağımsız bölüm sayısı 150'den fazla" ibaresi "10.000 m²'den veya bağımsız bölüm sayısı 100'den fazla" olarak; ada bazında komşu parsellerle ortak gündüz bakımevi kurulmasına izin |
| **Beklenen etki** | 30–150 bağımsız bölümlü projelerde ortak çocuk ve yaşlı alanı. Kanıt: ortak alanın komşuluk ve yalnızlık üzerindeki etkisi O–Z; kreşe erişimin iş-aile uyumuna etkisi O (12. KP 721.1–721.2 ile uyumlu) |
| **Kazanan / kaybeden** | Kazanan: aileler, yaşlılar. Maliyet: müteahhide küçük ek maliyet (emsal dışı olduğu için satılabilir alan kaybı yok). Risk: odanın zamanla depo ya da bağımsız bölüme dönüşmesi; tapuda ortak alan şerhi şart |
| **Araç** | ÇŞİDB: PAİY değişikliği |

### P4 · Asansör (md. 34) — az katlı düzende erişilebilirliği ucuzlatmak

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 34/1 (RG 01.07.2026 değişik): tek bağımsız bölümlü konutlar hariç, bodrum dahil kat adedi 3 olan binalarda asansör yeri bırakılması, 4 ve daha fazla olan binalarda asansör tesisi zorunlu. md. 34/4: zemin üzerinde 20'den fazla konut bağımsız bölümü olan yapılarda en az 2 asansör |
| **Sorun** | Zemin + 3 bitişik nizam bloklarda her merdiven evine asansör, az katlı düzenin maliyet avantajını aşındırıyor. Ama erişilebilirlik (12. KP 806.1–806.5) vazgeçilemez |
| **Önerilen metin** | md. 34'e fıkra: "(9) Aile dostu ada düzeninde, zemin dahil 4 katı geçmeyen ve her merdiven evinde 8'den az bağımsız bölüm bulunan konut yapılarında; açık galeri veya köprüyle birbirine bağlanan en fazla üç merdiven evine tek asansör tesisi yeterlidir. Bu yapılarda zemin katta, bağımsız bölümlerin en az %15'i erişilebilirlik standardına uygun düzenlenir." |
| **Beklenen etki** | Asansör sayısında yaklaşık üçte iki azalma; yaşlı ve engelli için zemin kat dairesi (çok kuşaklı tipolojiyle uyumlu) |
| **Kazanan / kaybeden** | Risk: galeri ve köprü düzeninin yangın güvenliği (Binaların Yangından Korunması Hakkında Yönetmelik ile uyum) ve mahremiyet. Kanıt: maliyet etkisi bu çalışmada ölçülmedi (Z) |
| **Araç** | ÇŞİDB: PAİY değişikliği; TSE erişilebilirlik standartları |

### P5 · Daire karması ve "aile konutu" tanımı (md. 5/25)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 5/25: her müstakil konutta en az bir oturma, bir yatak odası, mutfak, banyo ve tuvalet; bağımsız bölümlerin en fazla %20'sinde ayrı yatak odası aranmaz. Üst sınır ya da daire tipi karması şartı yok |
| **Sorun** | Piyasa ve kamu (Yüzyılın Konut Projesi: 55–80 m², 3+1 yok) küçük daire üretiyor. Türkiye'de kalabalık konutta yaşayanlar %37,8 (AB %16,8); kişi başı oda 1,1 |
| **Önerilen metin** | md. 4'e tanım: "Aile konutu: net kullanım alanı en az 100 m² olan, en az üç yatak odası bulunan bağımsız bölüm." md. 5'e fıkra: "Uygulama imar planında belirlenen alanlarda ve elli ve daha fazla bağımsız bölümlü konut projelerinde, bağımsız bölümlerin en az %30'unun aile konutu olarak projelendirilmesi plan notuyla şart koşulabilir." |
| **Beklenen etki** | Doğrudan doğurganlık etkisi beklenmez. Beklenen: aşırı kalabalığın ve "evden geç ayrılma"nın azalması, çok çocuklu ailelerin konut erişimi. Kanıt: konut maliyeti ve büyüklüğü kanalı O |
| **Kazanan / kaybeden** | Zorunlu değil, plan kararına bağlı. Risk: büyük daire fiyatı; bu yüzden F1–F3 finansman araçlarıyla birlikte |
| **Araç** | ÇŞİDB: PAİY değişikliği; belediye meclisi: plan notu |

---

## 2. Mekânsal Planlar Yapım Yönetmeliği (MPYY)

**Künye [D]:** RG 14.06.2014, sayı 29030. Değişiklikler: RG 17.05.2017/30069, 13.03.2022/31777, 11.05.2023/32187, 07.06.2024/32569, 22.01.2026/33145.

### M1 · Çocuk donatısını yaş yapısına bağlamak (md. 11 ve EK-2)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 11/1: imar planlarında EK-2 tablosundaki asgari standartlara uyulur. EK-2 (17.05.2017 değişik), 0–75.000 nüfus grubunda: anaokulu 0,5 m²/kişi (1.500–3.000 m²); ilkokul 2,0 (5.000–8.000 m²); ortaokul 2,0 (6.000–10.000 m²); gündüzlü lise 2,0; aile sağlık merkezi 1,5 (750–2.000 m²); sosyal-kültürel 0,75; küçük ibadet yeri 0,5 (1.000 m²); teknik altyapı 1,0; açık ve yeşil alan (çocuk bahçesi, park, meydan, semt spor alanı vb.) ilçe ölçeğinde 10 m²/kişi, il bütününde +5. Not 9: düzenleme ortaklık payına tabi çocuk bahçesi, oyun alanı, park, meydan ve semt spor alanının bu standarttaki payı %75'in altına düşemez. Not 11: 6306 kapsamındaki planlarda bu standartlar plan kararıyla ya da "gerekli görülmesi halinde" uygulanır |
| **Sorun** | Kişi başı standart, nüfusun yaş yapısından bağımsız. 0–14 yaş payı yüksek bir mahalle ile yaşlı bir mahalle aynı okul ve oyun alanını alıyor. Kreş (0–3 yaş) ayrı satır değil. 6306 planlarında standart isteğe bağlı. 12. KP 851.6 standartların "demografik, kültürel ve sosyal özelliklere göre" geliştirilmesini öngörüyor |
| **Önerilen metin** | md. 11'e fıkra: "(7) Eğitim, kreş ve çocuk oyun alanı standartları, planlama alanının plan hedef yılındaki yaş yapısı projeksiyonuna göre hesaplanır. EK-2'deki kişi başı değerler alt sınırdır. Plan hedef yılında 0–14 yaş nüfus payı Türkiye ortalamasını aşan alanlarda bu değerler aynı oranda artırılır. Kreş ve gündüz bakımevi alanı, 0–3 yaş nüfus için çocuk başına en az 8 m² açık ve kapalı alan esas alınarak ayrılır." EK-2 Not 11: "gerekli görülmesi halinde" ibaresi çıkarılır; 6306 planlarında standartların düşürülmesi ancak gerekçeli rapor ve hizmet etki alanında eşdeğer alanla mümkün olur |
| **Beklenen etki** | Çocuklu ailelerin yoğun olduğu yeni gelişme ve dönüşüm alanlarında okul ve oyun alanı açığının önlenmesi. Kanıt: okula yürüme ve dışarıda geçen sürenin sağlık etkisi O–G |
| **Kazanan / kaybeden** | Maliyet: daha fazla düzenleme ortaklık payı veya kamulaştırma. 3194 md. 18'deki %45 DOP tavanı içinde kalınmalı. Risk: projeksiyon belirsizliği; her 5 yılda gözden geçirme |
| **Araç** | ÇŞİDB MPGM: MPYY değişikliği; TÜİK ve ASHB veri platformu (Vizyon Belgesi "Veri Altyapısı" bileşeni) |

### M2 · Yürüme mesafeleri bağlayıcı ve yaya ağıyla ölçülür (md. 12)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 12/1: mesafeler topoğrafya, yapılaşma, yoğunluk ve eşikler dikkate alınarak planlanır. md. 12/2: çocuk bahçesi, oyun alanı, açık semt spor alanı, aile sağlık merkezi, kreş, anaokulu ve ilkokul "takriben 500 metre", ortaokul 1.000 m, lise 2.500 m mesafe dikkate alınarak yaya erişimli hizmet etki alanında "planlanabilir". md. 12/3: küçük cami 250 m, orta cami 400 m, mescit 150 m. md. 12/4: brüt yoğunluğu 100 kişi/ha ve altındaki yerleşimlerde mesafeler artırılabilir |
| **Sorun** | "Planlanabilir" ifadesi standardı tavsiyeye çeviriyor. Kuş uçuşu 500 m, yaya ağında 700–900 m'ye çıkabiliyor. İlkokul ile konut arasında çok şeritli yol olması ölçütte yok |
| **Önerilen metin** | md. 12/2'de "planlanabilir" ibaresi "planlanır" olarak değiştirilir. Fıkra eklenir: "(5) Bu maddedeki mesafeler, konut parselinin girişinden donatı alanının girişine kadar yaya ağı üzerinden ölçülür. İlkokul, anaokulu ve kreş ile hizmet ettiği konutlar arasındaki yaya güzergâhı, hızı 50 km/s'yi aşan veya ışıksız ve hemzemin yaya geçidi olmayan iki şeritten geniş bir taşıt yolunu kesemez; kesmesi kaçınılmazsa okul yolu güvenlik projesi plan eki olarak hazırlanır." md. 12/4'teki istisnalar korunur |
| **Beklenen etki** | Çocukların okula yürüyerek gitmesinin önünün açılması. Kanıt: Japonya (%92–93 yürüyor, D), Pontevedra (%81, K) |
| **Kazanan / kaybeden** | Risk: mevcut yapılaşmış alanlarda donatı yeri bulunamaması; 12/4'teki istisna bu durum için. Plan maliyeti: ağ analizi (OSM, açık araçlar) düşük maliyetli |
| **Araç** | ÇŞİDB MPGM: MPYY değişikliği |

### M3 · Yeşil alana erişim standardı (md. 12'ye yeni fıkra)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | EK-2: açık ve yeşil alan 10 m²/kişi (ilçe ölçeği). md. 12/2: çocuk bahçesi ve oyun alanı için yaklaşık 500 m. Park büyüklüğüne bağlı bir erişim standardı yok |
| **Sorun** | Metrekare standardı, yeşilin nerede ve ne büyüklükte olduğunu söylemiyor. Kent kenarındaki büyük bir park kâğıt üzerinde standardı sağlıyor |
| **Önerilen metin** | "(6) Konut alanlarındaki her konut parseli, yaya ağı üzerinden en fazla 300 metre mesafede en az 5.000 m²'lik kamuya açık park veya çocuk bahçesine erişir. En fazla 100 metre mesafede küçük çocuklar için oyun alanı ayrılması esastır. Bu fıkradaki alanlar, en kısa kenarı 40 metreden az olmamak üzere düzenlenir." |
| **Beklenen etki** | DSÖ'nün 300 m / 0,5–1 ha göstergesiyle uyum. Kanıt: yeşil alan ve ruh sağlığı O–G; Barselona 3-30-300 çalışmasında psikolog veya psikiyatri başvurusu daha az (OR 0,31) [D, 02_LITERATUR] |
| **Kazanan / kaybeden** | Risk: yapılaşmış alanlarda uygulanamaması; mevcut alanlarda "hedef", yeni planlarda "zorunlu" olarak kademelendirilmeli |
| **Araç** | ÇŞİDB MPGM: MPYY değişikliği; yerel iklim eylem planları (7552 md. 7; son tarih 31.12.2027) |

### M4 · Mahalle donatı dengesi ve plan değişikliğinde aile etkisi (md. 7 ve 26)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 26/1–2: plan değişikliği sosyal ve teknik altyapı dengesini bozamaz; yürürlükteki standartları düşüren değişiklik yapılamaz. md. 26/5-a: nüfus yoğunluğunu artıran değişiklikte artan nüfusun ihtiyacı olan alanlar standartlara uygun ayrılır. md. 26/5-b: kat artışında karşılıklı cepheler arası mesafe K = [(Y1+Y2)/2] + 7,00 m |
| **Sorun** | Denge, plan bütününde hesaplanıyor; mahalle ölçeğinde açık kalabiliyor. Plan açıklama raporunda mahalle bazında donatı tablosu şartı yok |
| **Önerilen metin** | Uygulama imar planı açıklama raporuna ilişkin hükme bent: "Planlama alanındaki her mahalle için nüfus, yaş yapısı, EK-2 standartlarına göre gereken ve ayrılan donatı alanları ile 12 nci maddedeki erişim mesafelerinin sağlanma oranını gösteren mahalle donatı dengesi tablosu." md. 26'ya fıkra: "Nüfus yoğunluğunu artıran plan değişikliklerinde, 3194 sayılı Kanunun ek 8 inci maddesindeki etki değerlendirme raporunda aile ve nüfus etkisi bölümü yer alır." (Ölçütler: Bölüm 9) |
| **Beklenen etki** | Mahallenin plan birimi olarak görünür hâle gelmesi (bkz. politika notu b) |
| **Araç** | ÇŞİDB MPGM: MPYY değişikliği |

---

## 3. Otopark Yönetmeliği

**Künye [D]:** RG 22.02.2018, sayı 30340. 13 değişiklik yönetmeliği; son değişiklik RG 27.12.2025, sayı 33120. Yürürlük 15.09.2018 (md. 16). Kanuni dayanak: 3194 md. 37 [D].

### O1 · Daire büyüklüğü eşiği aile konutunu cezalandırıyor (Ek-1)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | Ek-1, meskenler (RG 25.03.2021 değişik): 80 m² altı her 3 daireye 1; 80–120 m² (120 hariç) her 2 daireye 1; 120–180 m² (180 hariç) her daireye 1; 180 m² ve üzeri her daireye 2 otopark. md. 8/3: meskenlerde sayı bağımsız bölüm brüt alanı üzerinden belirlenir. md. 8/2: belediye meclisleri asgari miktarları artırabilir; cephesi 9 m'den veya alanı 250 m²'den küçük parsellerde, ihtiyacın en az yarısı parselde karşılanıyorsa, konut ihtiyacı %50'ye kadar azaltılabilir |
| **Sorun** | 120 m² eşiği, 3+1 ve 4+1 aile konutunun otopark yükünü iki katına çıkarıyor. Hane büyüklüğü ile araç sayısı arasında böyle bir ilişki için gerekçe yok. M6 modelinde 124 m²'lik çok kuşaklı sıra evde (C) 96 yer, 90 m²'lik blok dairede (A) 48 yer; C'nin otopark maliyeti 43,8 milyon TL/ha (bedel yoluyla), A'nınki 7,9 milyon TL/ha |
| **Önerilen metin** | Ek-1 "1- Meskenler" satırı: "Her bağımsız bölüm için 0,5 adet; bağımsız bölüm brüt alanı 180 m² ve üzeri olanlarda 1 adet. Uygulama imar planında 'bölgesel otopark alanı' olarak belirlenen yerlerde ve raylı sistem istasyonlarına 500 metre yaya mesafesindeki parsellerde bu miktarlar azami miktarlardır." |
| **Beklenen etki** | M6: reform C'nin otopark yükünü 43,8'den 21,9 milyon TL/ha'ya indiriyor, arsa kalıntı değerini (Türkiye ort. fiyatla) 100,9'dan 121,3 milyon TL'ye çıkarıyor. Blok (A) ile farkın net kapanması 9,2 milyon TL (İstanbul, emsal 2,5) |
| **Kazanan / kaybeden** | Kazanan: büyük daire alan aileler, az katlı yapımcı. Kaybeden: otopark talebi yüksek bölgelerde yol kenarı park baskısı artabilir; Poundbury dersi: otopark kısılmadan araç bağımlılığı düşmüyor, toplu taşıma eşlik etmeli |
| **Araç** | ÇŞİDB: Otopark Yönetmeliği değişikliği |

### O2 · Bölgesel otopark ve azami otopark (md. 4 ve 8)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 4/1-a: otopark ihtiyacının bina içinde veya parselde karşılanması, (e) bendindeki durumlar dışında zorunlu. md. 4/1-e: parselde karşılanamama halleri (teknik rapor, tescilli yapı, zemin, yaya yolu, bitişik nizamda temel riski). md. 4/1-f: karşılanamayan miktar önce komşu parselle ortak veya ada içi otopark, sonra 1.500 m yarıçap veya 2.000 m yürüme mesafesinde başka parsel, en son bedel karşılığı bölge otoparkı. md. 12/9: bedelin %25'i ruhsatta, kalanı iskândan önce 36 ayda 6 taksit. MPYY md. 11/6: planda semt ve bölge otoparkı ayrılabilir [D] |
| **Sorun** | Bölge otoparkı yalnız "teknik imkânsızlık" hâlinde açılan bir kapı. Planla bilinçli olarak "otoparkı mahalle kenarında topla" kararı verilemiyor. Bu da avlulu ve yaya öncelikli mahalle modelini fiilen engelliyor |
| **Önerilen metin** | md. 4/1-e'ye alt bent: "7) Uygulama imar planında 'bölgesel otopark alanı' olarak belirlenen ada veya mahallelerde bulunması." md. 8/2'ye cümle: "Büyükşehir ve belediye meclisleri, uygulama imar planında bölgesel otopark alanı olarak belirlenen yerlerde ve raylı sistem istasyonlarına 500 metre yaya mesafesindeki parsellerde konut otopark ihtiyacını %50'ye kadar azaltmaya ve azami miktar belirlemeye yetkilidir." md. 4/1-c'ye cümle: "Bölgesel otoparktan tahsis edilen yerler, bağımsız bölümden ayrı olarak satılabilir veya kiralanabilir." |
| **Beklenen etki** | Vauban modeli: otoparkın konuttan ayrılması, araç sahipliğini kent ortalamasının yaklaşık beşte ikisine indirdi (K, 02_LITERATUR). Ada içi avlunun bodrum otoparkla delinmemesi |
| **Kazanan / kaybeden** | Risk: bölge otoparkının zamanında yapılmaması. md. 12/7'deki 5 yıllık süre korunmalı; süre aşılırsa bedelin faiziyle iadesi |
| **Araç** | ÇŞİDB: Otopark Yönetmeliği değişikliği; belediye meclisleri |

### O3 · Otopark bedelinin kullanım alanı (md. 13)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 13/1: otopark hesabındaki tutar bölge ve genel otopark için arsa alımı ve inşaatında kullanılır. md. 13/2: başka bir amaçla kullanılamaz. md. 13/4: İçişleri Bakanlığı denetler |
| **Sorun** | Bedel, aracı mahalle kenarında tutan altyapıya (yaya yolu, okul yolu, bisiklet parkı, durak) harcanamıyor |
| **Önerilen metin** | md. 13/1'e cümle: "Otopark hesabında toplanan tutarın en fazla %30'u, bedelin tahsil edildiği mahalle ve komşu mahallelerde bölge otoparklarına erişimi sağlayan yaya yolları, okul yolu güvenliği düzenlemeleri, bisiklet park yerleri ve toplu taşıma durakları için kullanılabilir." |
| **Beklenen etki** | Düşük maliyetli, hızlı uygulanabilir yaya güvenliği. Kanıt: Z–O |
| **Kazanan / kaybeden** | Risk: bedelin otopark dışı işlere kaydırılıp bölge otoparkının gecikmesi; %30 tavanı ve md. 12/7'deki süre şartı bunu sınırlar |
| **Araç** | ÇŞİDB: yönetmelik değişikliği. **Hukuki teyit gerekir:** bedelin amaca bağlılığı 3194 md. 37'den mi yönetmelikten mi doğuyor, kanun değişikliği gerekip gerekmediği [DY] |

---

## 4. 3194 sayılı İmar Kanunu

**Künye [D]:** kabul 03.05.1985; RG 09.05.1985, sayı 18749. Ek md. 8: 7221 sayılı Kanunla (RG 20.02.2020, 31045) eklendi, 7534 sayılı Kanunla (RG 12.12.2024, 32750) değişti. Son değişiklik 7579 sayılı Kanun (RG 22.05.2026, 33261).

### I1 · Altyapı etki raporuna aile ve nüfus bölümü; 500 m'nin yaya ağıyla ölçülmesi (Ek md. 8)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | Ek md. 8/1: plan değişikliği tekliflerinde ihtiyaç analizini içeren "sosyal ve teknik altyapı etki değerlendirme raporu" hazırlanır. Parsel bazında nüfus, yoğunluk, kat adedi ve yükseklik artıran değişiklik yapılamaz. En az 1.000 m²'lik adalarda ada bazında artışlarda gereken donatı "adanın merkezine en fazla 500 metre yarı çaplı alanda" karşılanır |
| **Sorun** | Raporun içeriği tanımsız; aile ve çocuk boyutu yok. "Yarıçap" kuş uçuşu ölçü |
| **Önerilen metin** | Kanunda: "500 metre yarı çaplı alanda" ibaresi "500 metre yaya erişim mesafesinde" olarak değiştirilir. İmar Planı Değişikliğine Dair Değer Artış Payı Hakkında Yönetmelik (RG 15.09.2020, 31245) [D] ile MPYY'ye hüküm: etki raporunun içeriğine Bölüm 9'daki aile ve nüfus etki ölçütleri eklenir |
| **Beklenen etki** | Yoğunluk artışlarının çocuk donatısı açığı yaratmadan yapılması |
| **Araç** | Rapor içeriği: yönetmelik (öncelik 1). Ölçü değişikliği: kanun (öncelik 3) |

### I2 · Dikey dönüşümün gizli teşvikini nötrleştirmek (Ek md. 8, son fıkra)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | Ek md. 8: plan değişikliğiyle oluşan değer artışının %90'ı değer artış payı (DAP) olarak alınır. Son fıkra: riskli yapının bulunduğu parsellerde emsale esas inşaat alanını en fazla %20 artıran plan değişikliklerinde, 6306 kapsamındaki alanlarda, kamu yatırımlarında ve vakıf alanlarında "bu madde hükümleri uygulanmaz" |
| **Sorun** | 6306 kapsamındaki alanlarda maddenin tamamı devre dışı: parsel bazlı yoğunluk artışı yasağı da, DAP da, 500 m donatı şartı da. M6 dönüşüm senaryosu: İstanbul ortalama fiyatında 96 malikli bir adanın kat karşılığıyla kendi kendini finanse etmesi için emsalin 3,34'e (303 konut, mevcudun 3,2 katı) çıkması gerekiyor. Bu artışın değeri kamuya dönmüyor; dönüşümü dikeye itiyor |
| **Önerilen metin** | Son fıkraya cümle: "Ancak 6306 sayılı Kanun kapsamındaki alanlarda ve riskli yapı parsellerinde, mevcut inşaat alanını aşan ve hak sahiplerine verilen bağımsız bölümlerin toplam alanının 1,2 katından fazla olan emsal artışları için birinci ve ikinci fıkra hükümleri ile değer artış payının yarısı uygulanır. Aile dostu ada düzeninde (zemin dahil 4 katı aşmayan) yapılan dönüşümlerde değer artış payı alınmaz." |
| **Beklenen etki** | Yerinde dönüşümün maliyeti değişmez (1,2 kata kadar istisna sürer); yalnız müteahhide satış için üretilen ek emsalin değerinin bir kısmı kamuya döner. Az katlı ada dönüşümü göreli olarak avantajlı hâle gelir |
| **Kazanan / kaybeden** | Kaybeden: yüksek fiyatlı bölgelerde ek emsalden kazanç sağlayan müteahhit ve malikler. Risk: dönüşüm hızının yavaşlaması; bu yüzden D3 (harç muafiyeti) ve F2 (aile konut kredisi) ile birlikte uygulanmalı. Kanıt: N (hakkaniyet); etkinin büyüklüğü H (M6) |
| **Araç** | TBMM: kanun değişikliği |

### I3 · Değer artış payının bir kısmını aile donatısına ayırmak (Ek md. 8/a–c)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | Büyükşehirlerde DAP'ın %25'i büyükşehir, %25'i ilçe belediyesi, %25'i Dönüşüm Projeleri Özel Hesabı, kalan %25'i genel bütçe. Belediye paylarının harcama yeri belirtilmemiş |
| **Önerilen metin** | (a) ve (b) bentlerine cümle: "Belediyelere aktarılan tutarların en az yarısı, değer artışının oluştuğu ilçede kreş, çocuk oyun alanı, park ve yeşil alan ile okul yolu güvenliği için kamulaştırma ve yapım işlerinde kullanılır." |
| **Beklenen etki** | Yoğunluk artışı ile donatı arasında kurumsal bağ. Kanıt: N |
| **Araç** | TBMM: kanun değişikliği |

### I4 · Gönüllü kat sınırlaması karşılığında imar hakkı aktarımı (md. 5 ve 13)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 13 (7534 sayılı Kanunun 5. maddesiyle eklenen fıkralar): umumi hizmet alanına ayrılan özel mülkiyetteki taşınmazlar "imar hakkı aktarımı yapılarak" kamuya geçirilebilir. Alıcı parselin emsale esas alanı en fazla plan oranları kadar ve her halde %30'u geçmeyecek kadar artırılabilir. Verici parselin hakkı en yakın komşu parselin hakkını aşamaz. Değerler en az iki lisanslı değerleme kuruluşu ve kıymet takdir komisyonuyla belirlenir. Aktarım il içinde, alıcı parselin m² birim değeri verici parselinkinden fazla olmamak ve verici parsel idareye bedelsiz devredilmek şartıyla yapılır |
| **Sorun** | Kurum var ama yalnız kamuya geçen parsel için. Malikin mülkünü elinde tutup **kullanmadığı emsali** devretmesi mümkün değil. Bu yüzden az katlı seçen malik hakkını bedelsiz bırakıyor |
| **Önerilen metin** | md. 13'e fıkra: "Uygulama imar planında aile dostu ada düzeni veya koruma amacıyla kat adedi sınırlanan ya da malikin talebiyle planın izin verdiğinden daha az emsal kullanılan parsellerde, kullanılmayan emsale esas inşaat alanı, verici parsel malikin mülkiyetinde kalmak ve kullanılmayan hak tapu kütüğünün beyanlar hanesine şerh edilmek kaydıyla, imar planında alıcı alan olarak belirlenen parsellere bu madde hükümlerine göre aktarılabilir. Alıcı alanlar, öncelikle raylı sistem ve ana toplu taşıma koridorlarında ve sosyal altyapısı yeterli adalarda belirlenir." md. 13'teki "alıcı parselin metrekare birim değerinin verici parselden daha fazla olmaması" şartı bu fıkra için değer eşitleme katsayısıyla değiştirilir |
| **Beklenen etki** | M6 telafi köprüsü (İstanbul ort. fiyat, plan emsali 2,5, blok maliyeti az katlıdan %10 fazla): blok ile avlulu sıra ev arasındaki 56,6 milyon TL/ha'lık arsa değeri farkının 34,6 milyon TL'sini otopark reformu, harç indirimi ve hızlı onay kapatıyor. Kalan 22,0 milyon TL için devredilen 12.040 m² emsalin, alıcı bölgedeki arsa değerinin yalnız **%12,5'i** kadar bir fiyatla satılması yetiyor |
| **Kazanan / kaybeden** | Kazanan: az katlı seçen malik; toplu taşıma koridorunda yoğunluk. Risk: alıcı bölgede donatı açığı (Ek md. 8 ve M1 ile önlenir); değerleme manipülasyonu (iki değerleme + komisyon şartı korunur); talep yetersizliği (TDR piyasası kurulmazsa araç işlemez) |
| **Araç** | TBMM: 3194 md. 13 değişikliği; ÇŞİDB: uygulama yönetmeliği (md. 13'ün son cümlesi usul ve esasları Bakanlığa bırakıyor) |

---

## 5. 6306 sayılı Afet Riski Altındaki Alanların Dönüştürülmesi Hakkında Kanun

**Künye [D]:** kabul 16.05.2012; RG 31.05.2012, sayı 28309. Uygulama Yönetmeliği: RG 15.12.2012, sayı 28498 [D].

### D1 · Ada bazlı uygulama önceliği, aile ve nüfus etki değerlendirmesi, yerinde kalma (Uygulama Yönetmeliği)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | 6306 md. 6/1: riskli alanlarda etap veya adada, riskli yapılarda parselde; tevhit, "münferit veya birleştirilerek veya imar adası bazında uygulama", yeniden yapım, kat karşılığı veya hasılat paylaşımı kararları hisseleri oranında paydaşların **salt çoğunluğuyla** alınır (7471 sayılı Kanun, kabul 07.11.2023). md. 5/1: tahliye ve yıkımda önce anlaşma esastır; malik, kiracı ve sınırlı ayni hak sahiplerine geçici konut, kira yardımı ve yapım yardımı yapılabilir |
| **Sorun** | Uygulama ağırlıkla bina bazlı. Ada bazlı uygulama hukuken mümkün ama teşvik edilmiyor. Komşuluk ağı, kiracı ve yaşlı sakin için etki değerlendirmesi yok. Yerinden edilme süresi uzun (M6: blokta 30 ay, avlulu az katlıda 16 ay; ailenin kira yükü 805 bine karşı 429 bin TL) |
| **Önerilen metin** | Uygulama Yönetmeliğine hüküm: "(1) Riskli alan ve rezerv yapı alanlarındaki projeler ile aynı adada üç veya daha fazla riskli yapıyı kapsayan uygulamalarda ada bazında uygulama esastır; bina bazında uygulama gerekçelendirilir. (2) Elli ve daha fazla bağımsız bölümü kapsayan projelerde, proje onayından önce Aile ve Nüfus Etki Değerlendirmesi hazırlanır ve hak sahiplerine açıklanır. (3) Hak sahiplerine, talep etmeleri halinde, aynı ada veya mahallede bağımsız bölüm tahsisi önceliklidir. (4) Projede yer alan kiracılara, tahsis edilecek kiralık veya satılık konutlarda öncelik ve geçici kira yardımı sağlanır." |
| **Beklenen etki** | Komşuluk ve kuşaklar arası yakınlığın korunması; kiracı ve yaşlının yerinden edilme riskinin azalması. Kanıt: O (TOKİ ve dönüşüm literatürü, yerinden edilme); N |
| **Araç** | ÇŞİDB / Kentsel Dönüşüm Başkanlığı: Uygulama Yönetmeliği değişikliği |

### D2 · Salt çoğunlukla karar verilen projelerde azınlık malike güvence (md. 6)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 6/1: salt çoğunluk kararına katılmayanların arsa payları Başkanlıkça rayiç değer tespit ettirilerek anlaşan paydaşlara açık artırmayla satılabilir |
| **Sorun** | Hürriyet ve mülkiyet ilkesiyle gerilim. Paket bu eşiği düşürmeyi **önermiyor**; mevcut eşik için güvence öneriyor |
| **Önerilen metin** | md. 6/1'e cümle: "Karara katılmayan paydaşa, satış işleminden önce, payı oranında projede eşdeğer bağımsız bölüm alma veya bağımsız iki değerleme kuruluşunun tespit ettiği değerin ortalaması üzerinden payını devretme seçeneği yazılı olarak sunulur; bu seçenekler için en az 60 günlük süre verilir. Aile dostu ada düzeninde yapılan projelerde karara katılmayan paydaşın talebi halinde payına düşen alan zemin veya avluya açılan bağımsız bölümden karşılanır." |
| **Beklenen etki** | Zorlama riskinin azalması, dava sayısının düşmesi (12. KP 846: uzlaşma ve katılım). Kanıt: N |
| **Araç** | TBMM: kanun değişikliği |

### D3 · Az katlı ada projelerine harç ve ücret muafiyeti (md. 7/10)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 7/10: riskli alan, rezerv yapı alanı ve riskli yapı parsellerinde gerçek ve özel hukuk tüzel kişilerince yapılan uygulamalarda, mevcut inşaat alanının **bir buçuk katına** kadar yeni inşaat alanı için belediyelerce harç ve ücret alınmaz |
| **Önerilen metin** | Cümle eklenir: "Aile dostu ada düzeninde yapılan ada bazlı uygulamalarda bu oran iki kat olarak uygulanır; bu uygulamalarda hak sahiplerine verilen bağımsız bölümlerin ilk satışında 492 sayılı Harçlar Kanununa bağlı (4) sayılı tarifenin 20/a bendindeki tapu harcı binde 5 oranında alınır." |
| **Beklenen etki** | M6: harç ve ücret indirimi (satıcı tapu harcı %2'den %0,5'e, belediye harç ve ücretleri yapım maliyetinin 1,5 puanı) az katlı seçeneğin arsa değerini 12,8 milyon TL/ha artırıyor (İstanbul fiyatı) |
| **Araç** | TBMM: kanun değişikliği. Tapu harcı kısmı F1 ile Cumhurbaşkanı kararıyla da yapılabilir |

---

## 6. 634 sayılı Kat Mülkiyeti Kanunu

**Künye [D]:** kabul 23.06.1965; RG 02.07.1965, sayı 12038. Son değişiklik 7579 sayılı Kanun (RG 22.05.2026, 33261).

### K1 · Ortak avlu ve komşuluk alanlarının yönetimi (md. 28, 42, 66–74)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 28: yönetim planı bütün kat maliklerini bağlayan sözleşme hükmünde; değişikliği için kat maliklerinin **beşte dördünün** oyu şart. md. 42: ortak yerlerde faydalı yenilik ve ilaveler kat maliklerinin sayı ve arsa payı çoğunluğuyla. md. 66: toplu yapı, bir veya birden çok imar parseli üzerinde onaylı yerleşim planına göre yapılmış, ortak yerleri ve yönetimi bağlantılı birden çok yapı; parsellerin bitişik veya komşu olması şart, aralarında yol, park gibi kamu alanı kalabilir. md. 70: toplu yapı yönetim planının değişikliği için temsilciler kurulu üyelerinin temsil ettiği bağımsız bölümlerin **üçte ikisinin** oyu (7579/5 ile eklenen fıkra: yönetim planlarının bu maddeye aykırı hükümleri uygulanmaz) |
| **Sorun** | Ortak avlu ve oyun alanı, bakım ve kullanım kuralı olmadığında ya otoparka ya da kilitli "dekor alan"a dönüşüyor. Örnek bir yönetim planı yok |
| **Önerilen metin** | (a) **Rehber (öncelik 1):** Adalet Bakanlığı ve ÇŞİDB ortak "aile dostu ada örnek yönetim planı": avlu grubu kurulu; çocuk oyun, yaşlı oturma, bostan ve ortak oda kullanım saatleri; ortak alan bakım fonu (aidatın sabit bir payı); avlunun otopark veya bağımsız bölüme dönüştürülememesi. (b) **Kanun (öncelik 3):** md. 42'ye fıkra: "Ortak yerlerde çocuk oyun alanı, gölgelik, oturma yeri, bostan ve benzeri komşuluk düzenlemeleri faydalı yenilik sayılır. İmar planında ortak avlu olarak belirlenen alanların otopark, depo veya bağımsız bölüm eklentisine dönüştürülmesi ancak kat maliklerinin beşte dördünün kararı ve imar planına uygunlukla mümkündür." |
| **Beklenen etki** | Komşuluk mekânının kalıcılığı. Kanıt: Z–O (ortak alan ve komşuluk ilişkisi); N |
| **Araç** | Rehber: idari; kanun: TBMM |

### K2 · Meskende küçük gündüz bakımevi ve ev-atölye (md. 24)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 24/2: mesken olarak kayıtlı bağımsız bölümde eğlence ve toplantı yerleri; fırın, lokanta gibi gıda yerleri; imalathane, basımevi, dükkân, galeri ve çarşı gibi yerler ancak kat malikleri kurulunun **oybirliği** ile açılabilir |
| **Sorun** | Mahalle ölçekli küçük hizmetler (komşu çocuklarına bakım, terzi, ev-atölye) için oybirliği şartı fiilen yasak. İş ile evin yakınlaşması (Faz 1 tezi, "zaman" ilkesi) önünde engel |
| **Önerilen metin** | md. 24'e fıkra: "Zemin katta veya bahçeye, avluya ya da yola doğrudan girişi bulunan mesken bağımsız bölümlerinde; en fazla on çocuğa hizmet veren ve Aile ve Sosyal Hizmetler Bakanlığınca izin verilen gündüz bakım hizmeti ile gürültü ve koku yaymayan ev-atölye ve büro kullanımları, kat maliklerinin sayı ve arsa payı bakımından üçte iki çoğunluğu ve bitişik bağımsız bölüm maliklerinin yazılı rızasıyla açılabilir." |
| **Beklenen etki** | Kreş erişimi ve iş-aile uyumu (12. KP 721.1). Kanıt: Z (mekânsal etki); O (kreş erişimi ve kadın istihdamı) |
| **Kazanan / kaybeden** | Risk: komşu rahatsızlığı. Bitişik malik rızası ve ASHB denetimi bunu sınırlar |
| **Araç** | TBMM: kanun değişikliği |

---

## 7. 5393 sayılı Belediye Kanunu — mahalle yönetişimi

**Künye [D]:** kabul 03.07.2005; RG 13.07.2005, sayı 25874. Kent Konseyi Yönetmeliği: RG 08.10.2006, sayı 26313 [D].

### B1 · Mevcut yetkiyle pilot: mahalle meclisi ve katılımcı mahalle bütçesi

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 9: mahalle, muhtar ve ihtiyar heyetince yönetilir; muhtar "mahalle sakinlerinin gönüllü katılımıyla ortak ihtiyaçları belirlemek" ve mahalleyle ilgili konularda görüş bildirmekle yükümlü; belediye mahallenin ihtiyaçları için "bütçe imkânları ölçüsünde" destek sağlar ve "mahallelinin ortak isteklerini göz önünde bulundurur"; belediye sınırları içinde 500'ün altında nüfuslu mahalle kurulamaz. md. 13: hemşehrilerin belediye karar ve hizmetlerine katılma hakkı. md. 76: kent konseyi görüşleri meclisin ilk toplantısında gündeme alınır. md. 77: gönüllü katılım programları |
| **Sorun** | Mahalle idari birim; plan, donatı ve bütçe birimi değil. Katılım danışma düzeyinde |
| **Önerilen metin** | **Belediye meclisi kararı (öncelik 1):** "Pilot mahallelerde, muhtarın başkanlığında, ihtiyar heyeti, mahallede bulunan okul ve aile sağlık merkezi temsilcileri ile gönüllü sakinler arasından kurayla belirlenen en az 15 üyeden oluşan mahalle meclisi kurulur. Meclis yılda en az dört kez toplanır; mahalle donatı dengesi tablosu (M4) ve mahalle göstergeleri üzerinden ihtiyaç listesi hazırlar. Belediye yatırım bütçesinin %3'ü pilot mahallelere nüfusları oranında ayrılır ve kullanım önceliği mahalle meclisinin önerisiyle belirlenir." Dayanak: 5393 md. 9 (belediyenin mahalleye destek yükümlülüğü), 13, 18 (meclis yetkileri), 77 |
| **Beklenen etki** | Karar ile kullanıcı arasındaki mesafenin kısalması; plan değişikliklerinde erken katılım (12. KP 852.1, 953.1–953.3). Kanıt: O–Z (ampirik); G (normatif). Ayrıntı: politika notu (b) |
| **Araç** | Belediye meclisi kararı; Kent Konseyi Yönetmeliği kapsamında mahalle çalışma grubu |

### B2 · Kanuni çerçeve: mahalle ihtiyaç planı ve danışma kurulu (md. 9)

| Başlık | İçerik |
|---|---|
| **Önerilen metin** | md. 9'a fıkralar: "Muhtar, mahalle danışma kurulunun görüşünü alarak her yıl mahalle ihtiyaç planı hazırlar ve belediyeye sunar. Belediye, plan ve bütçe kararlarında mahalle ihtiyaç planlarını değerlendirir ve sonucunu gerekçesiyle açıklar." "Uygulama imar planı ve plan değişikliği teklifleri, askıdan önce ilgili mahallelerin muhtarlıklarına bildirilir ve mahallede bilgilendirme toplantısı yapılır." |
| **Kazanan / kaybeden** | Risk: siyasallaşma; belediye-muhtar çatışması; mahalle içinde sosyal baskı (Osmanlı kefalet sisteminin denetim baskısı dersi). Önlem: kura ile seçim, kapsayıcılık kotası (kadın, genç, yaşlı, kiracı), açık toplantı tutanakları |
| **Araç** | TBMM: kanun değişikliği; İçişleri Bakanlığı |

---

## 8. TOKİ (2985 sayılı Toplu Konut Kanunu) ve konut tipleri

**Künye [D]:** kabul 02.03.1984; RG 17.03.1984, sayı 18344 (mevzuat.gov.tr künyesinde "Sayfa" başlığıyla gösteriliyor). md. 4: TOKİ'nin kendi arsalarında ve dönüşüm alanlarında her ölçekte plan yetkisi; belediye üç ayda onaylamazsa re'sen onay. Ek md. 9: TOKİ yapılarına avan projeye göre 15 günde ruhsat [D].

### T1 · Tip proje kataloğunun aile ve kuşak odaklı revizyonu

| Başlık | İçerik |
|---|---|
| **Mevcut durum [K]** | Yüzyılın Konut Projesi: 500 bin konut; 55 m² 1+1, 65 ve 80 m² 2+1; 3+1 yok. 80 m² 2+1 Anadolu'da 2.650.000 TL, İstanbul'da 2.950.000 TL; %10 peşin, 240 ay sabit taksit; üç ve daha fazla çocuklu ailelere %10 kontenjan (basın aktarımı) |
| **Sorun** | Kamu, çok çocuklu ve çok kuşaklı aileye uygun konut üretmiyor. 12. KP'nin doğurganlık hedefiyle (2,1) ve Vizyon Belgesinin "konut politikasını demografik hedeflerle ilişkilendirme" önceliğiyle çelişki |
| **Önerilen karar (idari)** | (1) Kalan etaplarda ve yeni programlarda konutların en az %30'u 3+1 (net ≥100 m²), en az %10'u 4+1 veya çok kuşaklı (aynı parselde iki bağımsız bölüm). (2) Üç ve daha fazla çocuklu ailelerin kontenjanı 3+1 ve 4+1 tiplerle eşleştirilir. (3) Büyüyebilen konut: zemin + 2 tiplerde çatı arası ve arka bahçede projede gösterilmiş genişleme hakkı. (4) Yerleşim: zemin dahil en fazla 4 katlı avlulu ada (P1); yüklenici başına en fazla 40 konutluk parsel paketleri (Rieselfeld dersi). (5) Hak sahipliğinde "kuşak yakınlığı" puanı: ebeveyn veya evlatla aynı projede veya 4 km içinde başvuru (Singapur Yakınlık Hibesi dersi). (6) md. 4 kapsamındaki re'sen planlarda Bölüm 9'daki ölçüt listesiyle aile ve nüfus etki değerlendirmesi |
| **Beklenen etki** | Kamu konut stokunda aile ölçekli tip. M6: 124 m²'lik avlulu sıra ev, resmî birim maliyetle satılabilir m² başına 26.932 TL'ye üretilebiliyor (12 katlı blokta 34.091 TL). TOKİ'nin 80 m² 2+1 için açıkladığı 33.125 TL/m² (Anadolu) seviyesinde, aile ölçekli az katlı konut mümkün |
| **Kazanan / kaybeden** | Maliyet: konut başına daha yüksek bedel (daha büyük daire); taksit yükü için F2. Risk: yer seçiminin kent dışına kayması; donatı önce yapılmalı |
| **Araç** | ÇŞİDB ve TOKİ yönetimi; Aile ve Nüfus On Yılı 2027–2028 Eylem Planı |

---

## 9. Genelge 2026/4 — Aile ve Nüfus Etki Değerlendirmesi için imar ölçütleri (G1)

**Künye:** 2026/4 sayılı Cumhurbaşkanlığı Genelgesi, RG 02.05.2026, sayı 33241 [D: RG fihristi]. Madde içerikleri ikincil yayından [K]: md. 2 (bütün kamu politika ve düzenlemelerinin aile ve nüfus etkisi açısından değerlendirilmesi), md. 8 (kentsel mekânların aile ve çocuk odaklı dönüşümü), md. 9 (mevzuatın gözden geçirilmesi). Vizyon Belgesine göre ASHB metodolojisi düzenleyici etki analizlerine yansıtılacak; yayımlanmış metodoloji bu çalışmada bulunamadı [DY].

**Kapsam önerisi.** (i) Nüfus yoğunluğunu artıran plan değişiklikleri (3194 Ek md. 8 raporu); (ii) 6306 kapsamında 50+ bağımsız bölümlü projeler; (iii) TOKİ re'sen planları; (iv) 150+ bağımsız bölümlü yapı ruhsatları (kısa form: ölçüt 1–12); (v) imar mevzuatı değişiklik taslakları (DEA eki).

**Puanlama.** Kritik ölçütler (★): 1, 2, 5, 22 ve 24. Her ölçüt: 2 = sağlanıyor · 1 = kısmen · 0 = sağlanmıyor · U = uygulanamaz. Rapor sonucu: (a) kritik ölçütlerin (★) hiçbiri 0 değilse ve toplam puan uygulanabilir azami puanın en az %70'iyse "olumlu"; (b) kritik ölçütlerden biri 0 ise "düzeltme gerekli". Rapor karar vericiyi bağlamaz, gerekçeli değerlendirmeyi zorunlu kılar.

| # | Alan | Ölçüt | Eşik (2 puan) | Veri ve yöntem | Kanıt |
|---|---|---|---|---|---|
| 1 ★ | Çocuk donatısı | İlkokula yaya ağı mesafesi | Konutların ≥%90'ı ≤500 m; güzergâh 50 km/s üstü yolu ışıksız kesmiyor | Plan + OSM ağı | O–G |
| 2 ★ | Çocuk donatısı | Kreş ve anaokulu kapasitesi | 0–5 yaş projeksiyonunun ≥%30'una yer; ≤400 m | TÜİK ADNKS, MEB | O |
| 3 | Çocuk donatısı | Oyun alanı | Konutların ≥%90'ı ≤100–200 m'de oyun alanına erişiyor | Plan | O |
| 4 | Çocuk donatısı | EK-2 eğitim standardı, yaş yapısına göre (M1) | Gereken alanın ≥%100'ü | Plan + projeksiyon | N |
| 5 ★ | Yeşil ve sağlık | Yeşil erişim | Konutların ≥%90'ı 300 m ağ mesafesinde ≥0,5 ha kamusal yeşile erişiyor | Plan + ağ analizi | O–G |
| 6 | Yeşil ve sağlık | Gün ışığı | 21 Aralık öğle gölgesi konutların ≥%80'inde zemin kat cephesine ulaşmıyor | 3B model | O |
| 7 | Yeşil ve sağlık | Hava ve gürültü | Konutların ≥%90'ı otoyol veya 4+ şeritli yoldan ≥100 m | Plan | O |
| 8 | Yeşil ve sağlık | Aile sağlık merkezi | ≤500 m | Sağlık Bakanlığı | O |
| 9 | Konut | Aile konutu payı | Bağımsız bölümlerin ≥%30'u 3+1 ve üstü (net ≥100 m²) | Proje | O (konut erişimi) |
| 10 | Konut | Çok kuşaklı ve büyüyebilir konut | ≥%10 | Proje | O (kuşak yakınlığı) |
| 11 | Konut | Kişi başı kullanım alanı | Proje ortalaması ≥25 m² net/kişi (hane büyüklüğü varsayımıyla) | Proje | O |
| 12 | Konut | Uygun fiyatlı konut | ≥%20 kooperatif, maliyet kirası veya sosyal konut | Proje | O |
| 13 | Bina-zemin | Zemin ile ilişki | Konutların ≥%70'i zemin + 3 kat içinde | Proje | O–Z |
| 14 | Bina-zemin | Avlu ve bahçe | Her konutun doğrudan eriştiği özel veya ortak dış mekân ≥10 m²/konut | Proje | O–Z |
| 15 | Komşuluk | Ortak alan | Komşuluk odası ve ortak avlu (P3) | Proje | Z–O |
| 16 | Komşuluk | İbadet ve buluşma yeri | Mescit ≤150 m, cami ≤400 m; mahalle konağı ≤500 m | Plan | N |
| 17 | Kuşaklar | Yaşlı erişilebilirliği | Zemin katta erişilebilir bağımsız bölüm ≥%15 veya asansör | Proje | N; 12. KP 806 |
| 18 | Kuşaklar | Yerinde kalma (dönüşüm) | Mevcut sakinlerin ≥%70'ine aynı ada veya mahallede yer önerisi | Hak sahipliği listesi | O |
| 19 | Hareket | Trafik sakinleştirme | Konut sokaklarında ≤30 km/s; okul önü sokağı giriş-çıkışta araca kapalı | Ulaşım projesi | O |
| 20 | Hareket | Otopark | ≤0,7 yer/hane; bölgesel otopark ≤400 m | Proje | O |
| 21 | Hareket | Toplu taşıma | Konutların ≥%90'ı ≤400 m'de durağa erişiyor | Plan | O |
| 22 ★ | Afet | Zemin ve fay | Onaylı jeolojik-jeoteknik ya da mikrobölgeleme etüdü (MPYY md. 21/6) ve diri fay sakınım bandı dışında | Etüt | G |
| 23 | Afet | Toplanma alanı | ≤500 m | AFAD | O |
| 24 ★ | Süreç | Yerinden edilme süresi | Dönüşümde ≤18 ay; kira yardımı | Proje takvimi | N; M6 |

**Ne ölçülmez?** Doğurganlık ve evlilik proje ölçeğinde nedensel olarak ölçülmez. İlçe ölçeğinde izlenir. Faz 2 bulgusu bu ayrımı zorunlu kılıyor. Ayrıntı ve uygulama takvimi: politika notu (a).

---

## 10. Deprem bölgesine özgü hükümler

Ayrıntı politika notu (c)'de. Mevzuat kaldıraçları:

| Konu | Mevcut hüküm | Öneri | Araç |
|---|---|---|---|
| Zemin | MPYY md. 21/6 (07.06.2024): onaylı jeolojik-jeoteknik ya da mikrobölgeleme etüdü olmayan alanda imar planı yapılamaz [D, mevzuat haritası] | Mikrobölgeleme verisinin açık veri olarak yayımı; ölçüt 22 | ÇŞİDB, AFAD |
| Yapı | Türkiye Bina Deprem Yönetmeliği, RG 18.03.2018, sayı 30364 (Mükerrer) [D] | Tip proje kataloğu: Z+2 ve Z+3 avlulu, çok kuşaklı tipler için önceden onaylı statik projeler | ÇŞİDB, TOKİ |
| Yeniden yapım | 7452 sayılı Kanun (içerik [DY]); 6306 | Yeniden yapımda konut için azami zemin dahil 4 kat, tercihen 3; aynı ada ve sokaktan gelen hak sahiplerine "komşu kümesi" tahsisi | Plan notu; idari karar |
| Finansman | "Yarısı Bizden": 875 bin TL hibe + 875 bin TL kredi + 125 bin TL taşınma desteği; Cumhurbaşkanı Kararıyla 31.12.2027'ye uzatıldı [K; RG künyesi DY] | Ada bazlı ve az katlı projelere ek hibe puanı | Cumhurbaşkanı kararı |

---

## 11. Finansman ve vergi araçları

### F1 · Aile konutunun ilk satışında tapu harcı indirimi

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | 492 sayılı Harçlar Kanunu (RG 17.07.1964, 11756), (4) sayılı tarife 20/a: gayrimenkul devrinde devir alan ve devreden için ayrı ayrı **binde 20**. Aynı bendin son paragrafı Cumhurbaşkanına gayrimenkullerin türleri ve "yeni inşa edilen konut veya işyerlerinin ilk satışı" itibarıyla farklı oranlar belirleme yetkisi veriyor (ibare 7143 sayılı Kanunla eklendi; RG 18.05.2018, 30425) |
| **Önerilen karar** | Cumhurbaşkanı kararı: "Net kullanım alanı en az 100 m² ve en az üç yatak odası bulunan konutların (aile konutu) ilk satışında tapu harcı, devir alan ve devreden için ayrı ayrı binde 5 olarak uygulanır. Aile dostu ada düzeninde yapılan konutlarda bu oran devreden için binde 0'dır." |
| **Beklenen etki** | M6: satıcı payı indirimi az katlı seçeneğin arsa değerine ≈9,2 milyon TL/ha katkı (İstanbul fiyatı; belediye harç ve ücret indirimiyle birlikte 12,8 milyon TL). Alıcı tarafında 5,3 milyon TL'lik konutta ≈80 bin TL tasarruf |
| **Kamu maliyeti** | Harç geliri kaybı. Kapsam aile konutuyla sınırlı tutulursa düşük; tutar bu çalışmada hesaplanmadı |
| **Araç** | Cumhurbaşkanı kararı (mevcut yetki; öncelik 1) |

### F2 · Aile konut kredisi (öneri)

| Başlık | İçerik |
|---|---|
| **Sorun** | M6 (Türkiye ort. fiyat, 124 m² aile konutu, 5,28 milyon TL): piyasa koşullarında (%80 kredi, aylık %2,8, 120 ay) ilk taksit 122.667 TL, 4 kişilik medyan aile gelirinin (tahmini 67.522 TL/ay) **%182'si**. Piyasa kredisi aile konutuna erişimde fiilen kapalı |
| **Öneri** | TÜFE'ye endeksli, reel faizi %2, 240 ay vadeli, %10 peşinatlı "aile konut kredisi". Hak: ilk konut; evli çift; aile konutu (P5 tanımı) veya kooperatif ve vakıf modeliyle edinilen konut |
| **Beklenen etki** | Aynı konut için ilk yıl aylık taksit 23.985 TL (gelirin %35,5'i); kooperatif ve kamu arsasıyla 17.593 TL (%26,1); arsa vakfı ve üst hakkı modeliyle 15.203 TL (%22,5) |
| **Kamu maliyeti** | M6 (kamu reel borçlanma maliyeti %5 varsayımıyla): kredi tutarının **%22,8'i**. Karşılaştırma: TOKİ tipi sabit nominal taksit (240 ay, ortalama enflasyon %25 varsayımı) kredi tutarının **%81,9'u**. Endeksli kredi, aynı kamu kaynağıyla yaklaşık 3,6 kat daha fazla aileye ulaşır |
| **Risk** | Talep tarafı desteği fiyatı şişirebilir (Macaristan dersi, DY). Arz tarafıyla (kamu arsası, kooperatif, P1) birlikte ve aile konutu kotasıyla sınırlı tutulmalı |
| **Araç** | Kanun veya kamu bankaları programı; Aile ve Gençlik Fonu ile ilişkisi incelenmeli [DY] |

### F3 · Kooperatif, yapı grubu ve arsa vakfı

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | 1163 sayılı Kooperatifler Kanunu (RG 10.05.1969, 13195). Ek md. 6 (7579 sayılı Kanun, 2026): inşaatı tamamlayıp etaplar hâlinde yeniden inşaata başlayan yapı kooperatifleri, bütün inşaatlar tamamlanmadan tahsis ettikleri konutların tapusunu devredemez |
| **Sorun** | Kooperatif modeli, kat karşılığına göre aileye %17 daha ucuz konut sağlıyor (M6) ama arsa ve finansmana erişemiyor. Ek md. 6 etaplı modelde tapu devrini geciktiriyor |
| **Öneri** | (1) Belediye ve TOKİ arsalarının bir kısmı küçük parseller (≤40 konut) hâlinde aile konut kooperatiflerine ve yapı gruplarına maliyetine veya yarı değerle, 10 yıl taksitle tahsis edilir (Batıkent, Vauban dersi). (2) Etaplı ada projelerinde her etap için ayrı kooperatif kurulması teşvik edilir; Ek md. 6 bu durumda sorun olmaz. (3) Belediye veya vakıf mülkiyetinde kalan arsa üzerinde üst hakkıyla konut (yeniden satışta fiyat formülü) ve maliyet kirası modeli pilot olarak denenir. Kat mülkiyetinin üst hakkı üzerine kurulmasının hukuki çerçevesi bu çalışmada doğrulanmadı [DY] |
| **Beklenen etki** | M6 (Türkiye ort. fiyat, 124 m²): kat karşılığı piyasa fiyatı 5,28 milyon TL; arsa payı / yapı grubu 4,62 (−%12); kooperatif 4,40 (−%17); kooperatif + yarı değerli kamu arsası 3,87 (−%27); arsa vakfı ve üst hakkı 3,34 milyon TL (−%37). Maliyet kirası aylık 11.150 TL; aynı konutun piyasa kirası 33.318 TL |
| **Araç** | Belediye meclisi ve TOKİ kararları (arsa tahsisi); Ticaret Bakanlığı (kooperatif mevzuatı); vakıf modeli için hukuki inceleme |

---

## 12. Finansman modelinin özeti (M6)

Ayrıntı: `finansman_modeli/` ve [06_politika_paketi_ozet.md](../09_RAPORLAR/06_politika_paketi_ozet.md).

**Yöntem.** Aynı 1 ha'da üç biçim (çizimdeki geometri). Maliyet: 2026 Yapı Yaklaşık Birim Maliyetleri Tebliği (RG 03.02.2026, 33157) [D]; 12 katlı blok IV.A 26.450 TL/m², Z+3 ve Z+2 III.B 21.050 TL/m² (tebliğdeki %10 yüklenici kârı çıkarıldı). Satış fiyatı: Türkiye ortalaması 42.488 TL/m² (Ağustos 2026) ve İstanbul ortalaması 63.788 TL/m² (Haziran 2026) [K, Endeksa/Emlakjet aktarımı]. Ölçüt: arsa kalıntı değeri (müteahhidin %15 reel getirisiyle indirgenmiş net gelir eksi maliyet), yani arsa sahibine kat karşılığında bırakılabilecek en yüksek değer.

**Ana sonuçlar.**

1. **Aynı yoğunlukta az katlı önde.** Çizimdeki geometride (emsal A 1,06 · B 1,23 · C 1,30) arsa kalıntı değeri Türkiye ortalama fiyatında A 2,9 · B 68,3 · C 100,9 milyon TL/ha; İstanbul fiyatında A 128,9 · B 241,3 · C 298,1 milyon TL/ha. Az katlı düzen aynı arsada daha fazla inşaat alanı veriyor ve satılabilir m² başına daha ucuz (C 26.932, A 34.091 TL).
2. **Blok ancak yüksek fiyat ve yüksek emsalde öne geçiyor.** Blok, resmî maliyet farkıyla ancak 53.000 TL/m²'nin üzerindeki fiyatlarda ve İstanbul fiyatında emsal **2,61**'in üzerinde az katlıyı geçebiliyor. Blok maliyeti az katlıdan yalnız %10 fazla varsayılırsa eşikler 44.000 TL/m² ve emsal **2,09**. Türkiye ortalama fiyatında blok, bu iyimser varsayımla bile ancak emsal 5,03'ün üzerinde öne geçiyor; bu yoğunluk 12 katla 1 ha'ya sığmıyor.
3. **Reform ve telafi paketiyle eşik yükseliyor.** Otopark reformu, harç ve ücret indirimi, 3 ay hızlı onay ve TDR birlikte uygulanınca İstanbul fiyatında kırılma emsali **3,99**'a çıkıyor. 64.000 TL/m²'nin altındaki fiyatlarda blok 4,0'a kadar hiçbir emsalde öne geçemiyor.
4. **Düşük fiyatlı bölgelerde piyasa modeli çalışmıyor.** 30.000 TL/m²'de üç biçimin de arsa değeri negatif (A −71,0 · B −33,2 · C −14,7 milyon TL/ha). Kat karşılığı bu bölgelerde hiçbir emsalde kendini finanse etmiyor; kamu finansmanı zorunlu. Kamu için az katlı seçenek birim maliyette daha ucuz.

---

## 13. Doğrulama durumu

### 13.1 Bu çalışmada doğrulanan künyeler [D]

| Mevzuat | Künye | Kaynak |
|---|---|---|
| 3194 İmar Kanunu | RG 09.05.1985 / 18749 | mevzuat.gov.tr |
| 7221 sayılı Kanun (Ek md. 8'i ekleyen) | RG 20.02.2020 / 31045 | mevzuat.gov.tr |
| 7534 sayılı Kanun (Köy Kanunu ile Bazı Kanunlarda Değişiklik; 3194 md. 13 imar hakkı aktarımı) | RG 12.12.2024 / 32750 | RG fihristi |
| 7579 sayılı Kanun | RG 22.05.2026 / 33261 | mevzuat.gov.tr |
| 7143 sayılı Kanun (492 tarife yetkisine "ilk satış" ibaresi) | RG 18.05.2018 / 30425 | mevzuat.gov.tr |
| Planlı Alanlar İmar Yönetmeliği | RG 03.07.2017 / 30113; son değişiklik 01.07.2026 / 33297 | mevzuat.gov.tr |
| Mekânsal Planlar Yapım Yönetmeliği ve EK-2 | RG 14.06.2014 / 29030; EK-2 değişik 17.05.2017 / 30069; son değişiklik 22.01.2026 / 33145 | mevzuat.gov.tr (ek dosya dahil) |
| Otopark Yönetmeliği ve Ek-1 | RG 22.02.2018 / 30340; son değişiklik 27.12.2025 / 33120 | mevzuat.gov.tr (ek dosya dahil) |
| 6306 sayılı Kanun | RG 31.05.2012 / 28309 | mevzuat.gov.tr |
| 6306 Uygulama Yönetmeliği | RG 15.12.2012 / 28498 | RG fihristi |
| 634 Kat Mülkiyeti Kanunu | RG 02.07.1965 / 12038 | mevzuat.gov.tr |
| 5393 Belediye Kanunu | RG 13.07.2005 / 25874 | mevzuat.gov.tr |
| Kent Konseyi Yönetmeliği | RG 08.10.2006 / 26313 | RG fihristi |
| 2985 Toplu Konut Kanunu | RG 17.03.1984 / 18344 | mevzuat.gov.tr |
| 1163 Kooperatifler Kanunu | RG 10.05.1969 / 13195 | mevzuat.gov.tr |
| 492 Harçlar Kanunu | RG 17.07.1964 / 11756 | mevzuat.gov.tr |
| İmar Planı Değişikliğine Dair Değer Artış Payı Hakkında Yönetmelik | RG 15.09.2020 / 31245 | RG fihristi |
| Türkiye Bina Deprem Yönetmeliği | RG 18.03.2018 / 30364 (Mükerrer) | RG fihristi |
| 2026 Yılı Yapı Yaklaşık Birim Maliyetleri Tebliği | RG 03.02.2026 / 33157 | resmigazete.gov.tr (metin) |
| 2026/4 sayılı Cumhurbaşkanlığı Genelgesi | RG 02.05.2026 / 33241 | RG fihristi (PDF metni okunamadı; içerik [K]) |

### 13.2 Doğrulanamayanlar [DY]

1. Genelge 2026/4'ün madde metni (RG PDF'i metin olarak çözülemedi; içerik ikincil yayından).
2. "Yarısı Bizden" süre uzatımına ilişkin Cumhurbaşkanı Kararının RG künyesi.
3. 7471 sayılı Kanunun RG künyesi (kabul tarihi 07.11.2023 mevzuat dipnotlarından).
4. 7452 sayılı Kanunun içeriği.
5. Konut teslimlerinde KDV oranları ve 150 m² eşiği (bu nedenle modelde KDV nötr varsayıldı).
6. Kat mülkiyetinin üst hakkı üzerine kurulmasının çerçevesi (F3).
7. Değer artış payı yönetmeliği değişiklik taslağının (28.04.2025) yürürlüğe girip girmediği.
8. Otopark bedelinin amaca bağlılığının kanuni dayanağı (O3).
9. ASHB aile ve nüfus etki değerlendirmesi metodolojisi ve 2027–2028 Eylem Planı (yayımlanmış metin bulunamadı).
10. Aile ve Gençlik Fonu kredilerinin güncel koşulları (F2).

*Bu belge hukuki görüş değildir. Önerilen metinler, ilgili kurumların ve bir hukukçunun incelemesinden geçmeden kullanılmamalıdır. Mevzuat hızla değişiyor: 2024–2026 arasında PAİY 6, MPYY 2, Otopark Yönetmeliği 1 kez değişti; 3194 üç kanunla (7534, 7557, 7579) değişti.*
