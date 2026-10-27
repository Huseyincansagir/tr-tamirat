# Faz 2 · Rapor 2 — 973 İlçe Paneli: Mekânın Etkisi Aynı İl İçinde

*25 Ekim 2026 · Sürüm 0.1*

| Ne | Nerede |
|---|---|
| Panel (973 ilçe; doğum, yaş-cinsiyet, kadın eğitimi, GHSL yükseklik ve nüfus) | [03_VERI/islenmis/ilce_paneli_analiz.csv](../03_VERI/islenmis/ilce_paneli_analiz.csv) · [.gpkg](../03_VERI/islenmis/ilce_paneli.gpkg) · [kaynaklar](../03_VERI/ham/tuik/ilce_kaynaklar.md) |
| Veri kodu | `03_VERI/kod/tuik_sdmx_ilce.py` · `ghsl_ilce.py` · `ilce_paneli_olustur.py` |
| Analiz kodu ve sonuçlar | [05_ANALIZ/kod/ilce_paneli_analiz.py](../05_ANALIZ/kod/ilce_paneli_analiz.py) · `05_ANALIZ/sonuclar/ilce_*.csv` |
| Haritalar | [04_HARITA/ilce_haritalari_2025.png](../04_HARITA/ilce_haritalari_2025.png) · [04_HARITA/istanbul_ilce_2025.png](../04_HARITA/istanbul_ilce_2025.png) |
| Grafik | [05_ANALIZ/grafikler/ilce_il_ici_yukseklik_egitim.png](../05_ANALIZ/grafikler/ilce_il_ici_yukseklik_egitim.png) |

---

## Özet

**Soru:** İl ölçeği kaba kalınca (Rapor 1), aynı il içindeki ilçeleri karşılaştırdık. İl sabit etkisi bölgeyi, kültürü ve il düzeyindeki ekonomiyi sabit tutuyor. Sorulan şu: aynı ilde daha yüksek binalarda yaşayan ilçeler daha mı az doğuruyor ve bu fark kadın eğitimiyle açıklanabiliyor mu?

**Kısa cevap:** Evet, daha az doğuruyorlar. Ama farkın çoğu eğitimden geliyor.

1. **Ham il içi ilişki belirgin.** Aynı ilde yaşanan bina yüksekliği 3 m (yaklaşık bir kat) fazla olan ilçelerde doğurganlık **0,136 çocuk daha düşük**. Standartlaştırılmış etki büyüklüğü β = −0,35.
2. **Kadın eğitimi sabit tutulunca ilişki beşte birine iniyor: 3 m başına −0,029 çocuk** (β = −0,07, p < 0,01). Yüksek binalı ilçelerde kadınlar daha eğitimli; ham ilişkinin yaklaşık **%80'i bu bileşimden** geliyor.
3. **Eğitimin etkisi bina yüksekliğinin yaklaşık 8 katı.** Bir yıl daha fazla kadın eğitimi, aynı il içinde doğurganlığı **0,17 çocuk** düşürüyor (β = −0,55). İl içi açıklanan farkın **%76'sı eğitime**, **%19–22'si mekâna** düşüyor.
4. **Kalan küçük yükseklik etkisi kırılgan.** Büyükşehir ilçelerinde ve nüfus ağırlıklı modellerde anlamlı. Ağırlıksız modelde, büyükşehir dışında, Doğu-Güneydoğu hariç örneklemde ve İstanbul, Ankara, İzmir'de tek tek bakıldığında anlamsız. Yükseklik sınıflarında (4 m altından 12 m üstüne) belirgin bir eşik yok.
5. **Çocuk-kadın oranında** (0–4 yaş / 15–49 yaş kadın) eğitim kontrolünden sonra yükseklik etkisi tamamen anlamsız (β = −0,04).

**Zihinsel simülasyon (üst sınır):** Büyükşehirlerde kadınların yaşadığı binaların ortalama yüksekliği 10,2 m. Bu 6 m'ye (yaklaşık iki kat) indirilse, eğitim sabitken doğurganlık en fazla **+0,04 çocuk** artar (%3). Mekân dönüşümünün doğurganlığa doğrudan katkısı küçük.

**Proje için anlamı:** Rapor 1'deki bulgu ilçe ölçeğinde ve il içinde de doğrulandı. Bina yüksekliği ve yoğunluk, doğurganlığın ana belirleyicileri değil. Asıl eksen eğitim ve onunla gelen evlilik ve doğum zamanlaması. "Fıtrata uygun şehir" tezinin doğurganlık iddiası bu yüzden **zayıflatılmalı ve yeniden çerçevelenmeli**:
- **Mekânın gerekçesi:** Sağlık, çocuk gelişimi, komşuluk, kuşaklar arası yakınlık ve deprem güvenliği. Bunlar literatürde daha güçlü kanıtlanmış alanlar.
- **Doğurganlık hedefi:** Eğitim ile aile kurmayı uyumlu kılan politikalar (evlilik ve doğum yaşı, konut erişimi, iş-aile dengesi) mekân politikasıyla birlikte tasarlanmalı.

---

## 1. Veri

| Bileşen | Kaynak | Not |
|---|---|---|
| İlçe kodları ve 2014–2025 doğumlar | TÜİK Dağıtım Yönetim Sistemi (SDMX), `DF_DOGUM_IL_ILCE_C` | 2025 toplamı 895.374 = Türkiye |
| İlçe nüfusu 2024–2025, merkez / belde-köy | SDMX `DF_ADNKS_T22` | 2025 toplamı 86.092.168 = Türkiye |
| İlçe × cinsiyet × 19 yaş grubu (2025) | TÜİK MEDAS, ADNKS "İl ve İlçe Nüfusları" | İlçe nüfusu SDMX ile **973 ilçenin tamamında birebir** aynı |
| 15+ yaş kadınların bitirdiği okul (2025) | TÜİK MEDAS, Ulusal Eğitim İstatistikleri | 33,8 milyon kadın; eğitim yılı bitirilen okuldan hesaplandı |
| Bina yüksekliği ve nüfus (100 m) | JRC GHSL R2023A: ANBH 2018, POP 2020 | İlçe sınırına göre toplandı (GHSL toplamı 84,0 milyon) |
| İlçe sınırları | geoBoundaries ADM2 (OSM, 973 birim) | 973 / 973 eşleşti (2'si bulanık eşleşme, ikisi de doğru) |

**Doğurganlık ölçüleri:**

| Ölçü | Tanım |
|---|---|
| **İlçe TDH (ana ölçü)** | Dolaylı standartlaştırma: 2025 doğum sayısı / beklenen doğum × 1,42. *Beklenen doğum* = her 5 yaşlık kadın grubu × Türkiye yaşa özel doğurganlık hızı 2025. |
| **Çocuk-kadın oranı** | 0–4 yaş çocuk / 15–49 yaş kadın × 1000 |
| **Genel doğurganlık hızı** | Doğum / 15–49 yaş kadın × 1000 |

İlçe TDH yaş yapısındaki farkları düzeltir. Doğrulama: beklenen doğumların toplamı (895.438) gerçek doğuma (895.374) eşit; beklenen doğumla ağırlıklı ilçe TDH ortalaması **1,42**, Türkiye değeriyle aynı.

**Mekân ölçüleri:**
- İnsanların yaşadığı binaların nüfus ağırlıklı ortalama yüksekliği (m). Not: GHSL hücre ortalamasıdır; 3 m yaklaşık bir kat.
- 5+ katlı (≥15 m) ve 1-2 katlı (<6 m) hücrelerde yaşayan nüfus payı.
- ln(yaşanan yoğunluk).
- İl/ilçe merkezinde yaşayan nüfus payı.

**Kontroller:** 15+ yaş kadınların ortalama eğitim yılı; nüfus değişimi 2024→2025 (göç vekili); **il sabit etkisi** (81 il).

**Tahmin yöntemi:** Ağırlıklı en küçük kareler (ağırlık: 15–49 yaş kadın sayısı). Standart hatalar il düzeyinde kümelenmiş.

**Uç değerler:** En yüksek ilçe TDH Harran'da (5,39), Akçakale'de (5,06) ve Eyyübiye'de (4,01). En düşük Beşiktaş'ta (0,60), Başçiftlik'te (0,62), Balçova'da, Adalar'da ve Şişli'de (0,67–0,68).

---

## 2. Bulgular

### 2.1 Ana modeller

Değerler standartlaştırılmış katsayılardır (β); il sabit etkili, il düzeyinde kümelenmiş standart hata. Anlamlılık: *** p<0,001 · ** p<0,01 · * p<0,05 · † p<0,10.

| Sonuç | Model | R² | Yükseklik | ln yoğunluk | Merkez payı | Kadın eğitimi | Göç |
|---|---|---|---|---|---|---|---|
| **İlçe TDH** | Yalnız mekân | 0,77 | **−0,35*** | +0,05 | −0,01 | | |
| | + eğitim + göç | 0,85 | **−0,07**** | −0,02 | +0,21* | **−0,55*** | +0,17 |
| | İl sabit etkisi olmadan | 0,56 | +0,00 | +0,07 | +0,28† | −0,94*** | +0,41* |
| **Çocuk-kadın oranı** | Yalnız mekân | 0,79 | −0,32*** | +0,05 | +0,09 | | |
| | + eğitim + göç | 0,87 | −0,04 | −0,01 | +0,29*** | −0,57*** | +0,26† |
| **Genel doğurganlık hızı** | + eğitim + göç | 0,86 | −0,05* | −0,02 | +0,26*** | −0,53*** | +0,19 |

**Ham etkiler (ilçe TDH):**
- **Bina yüksekliği:** 1 m başına −0,0098 çocuk (p = 0,002); 3 m (≈ bir kat) başına **−0,029 çocuk**.
- **Kadın eğitimi:** Bir yıl başına **−0,173 çocuk**.

### 2.2 İl içi farkın bölüşümü (Shapley)

İl sabit etkisi tek başına ilçe TDH'deki farkın %72'sini açıklıyor. Kalan farkın ne kadarının hangi gruba düştüğü:

| Sonuç | İl içi açıklanan R² | Mekân | Eğitim | Göç |
|---|---|---|---|---|
| İlçe TDH | 0,135 | **%22** | **%76** | %2 |
| Çocuk-kadın oranı | 0,123 | %19 | %76 | %6 |

### 2.3 Eğitim kontrolü ilişkiyi nasıl değiştiriyor?

Aynı il içinde, ilçeler yaşanan bina yüksekliğine göre 20 eşit gruba ayrıldı:

- **Sol panel (ham il içi ilişki):** Eğim 3 m başına −0,136 çocuk.
- **Sağ panel (eğitimin etkisi iki eksenden de çıkarılınca):** Eğim 3 m başına −0,029 çocuk. Noktalar yatay bir bant içinde dağılıyor.

**İstanbul örneği (39 ilçe):**
- Doğurganlığın yükseklikle korelasyonu −0,33, kadın eğitimiyle −0,78.
- İkisi birlikte modellendiğinde yükseklik β = −0,04 (anlamsız), eğitim β = −0,79***.
- En düşük doğurganlık Beşiktaş, Şişli ve Kadıköy'de: yüksek binalı ve kadın eğitimi 11–13 yıl.
- En yüksek doğurganlık Arnavutköy, Sultanbeyli ve Esenyurt'ta. Esenyurt da yüksek binalı (15 m), ama kadın eğitimi 9 yıl.

### 2.4 Yükseklik sınıfları (doğrusal olmayan ilişki var mı?)

Referans kategori 4 m'nin altı. Diğer sınıfların ham TDH farkı (eğitim, göç, yoğunluk, merkez payı ve il sabit etkisi kontrollü):

| Sınıf | İlçe sayısı | TDH farkı | %95 güven aralığı |
|---|---|---|---|
| 4–6 m | 229 | −0,05 | −0,16 / +0,07 |
| 6–9 m | 208 | −0,00 | −0,13 / +0,12 |
| 9–12 m | 81 | −0,03 | −0,18 / +0,13 |
| 12+ m | 46 | −0,10 | −0,25 / +0,05 |

Belirgin bir eşik yok. Yalnızca 12 m üstünde (yaklaşık 4+ kat ortalama) anlamsız bir düşüş eğilimi görülüyor.

### 2.5 Sağlamlık (ilçe TDH, yükseklik katsayısı β)

| Model | n | Yükseklik | Eğitim |
|---|---|---|---|
| Ana model | 973 | −0,069** | −0,545*** |
| Ağırlıksız | 973 | −0,013 | −0,333*** |
| 2 yıllık doğum ortalaması | 973 | −0,069** | −0,566*** |
| 5+ kat payı (yükseklik yerine) | 973 | **−0,063***** | −0,534*** |
| 1-2 kat payı (yükseklik yerine) | 973 | −0,028 | −0,590*** |
| Eğitim ölçüsü: yükseköğretimli kadın payı | 973 | −0,118*** | −0,369*** |
| + yaşlı nüfus payı | 973 | −0,105*** | −0,521*** |
| Komşu ilçe ortalamaları eklenmiş (SLX) | 973 | −0,064* | −0,548*** |
| Büyükşehir ilçeleri | 519 | −0,064* | −0,562*** |
| Büyükşehir dışı | 454 | −0,013 | −0,359*** |
| Doğu-Güneydoğu hariç | 762 | −0,059 | −0,824*** |
| Doğu-Güneydoğu | 211 | +0,008 | −0,500** |
| İstanbul / Ankara / İzmir (her biri ayrı) | 39 / 25 / 30 | −0,04 / −0,26 / +0,07 (hepsi anlamsız) | −0,79*** / −0,95** / −0,96*** |

**Değerlendirme:**
- **Yükseklik:** Katsayının işareti tutarlı biçimde eksi, ama büyüklüğü küçük ve anlamlılığı modele göre değişiyor. Etkinin varlığı büyük kentlere ve 5+ katlı dokuya bağlı görünüyor.
- **Eğitim:** Bütün modellerde güçlü ve kararlı.
- **Mekânsal kümelenme:** Artıklarda orta düzeyde kalıyor (Moran's I = 0,20, p = 0,002). Komşu ilçe ortalamaları eklemek bunu gidermiyor ama katsayıları da değiştirmiyor.

---

## 3. Yorum

1. **Bileşim ve seçilim.** Yüksek binalı ilçeler, eğitimli ve geç evlenen kadınları topluyor. Ham ilişkinin büyük kısmı mekânın kendisinden değil, mekânın kimleri bir araya getirdiğinden kaynaklanıyor. Eğitim de kısmen mekânsal bir seçimdir: eğitimli aileler merkezî ve yüksek binalı semtlere yerleşiyor. Bu yüzden eğitim kontrolü, mekânın gerçek etkisinin bir kısmını da "yutuyor" olabilir. Dürüst sonuç şu aralıktır: bir kat başına **−0,03 ile −0,14 çocuk**, en olası değer alt uca yakın.
2. **Yeni banliyöler karşı örnek.** Esenyurt, Başakşehir ve Sultangazi gibi yüksek binalı, yeni ve görece düşük eğitimli ilçeler yüksek doğurganlık gösteriyor. Türkiye'de yüksek bina "sosyal sınıfı yüksek merkez" ile sınırlı değil.
3. **Merkez payının artı işareti** (büyükşehir dışı iller): Aynı ilde köy nüfusu fazla olan ilçeler daha az doğuruyor. Rapor 1'deki seçici göç ve kırsal yaşlanma burada da görülüyor.
4. **Hipotez durumu:**

| Hipotez | Durum |
|---|---|
| **H1** Yüksek kat → düşük doğurganlık | İl içinde zayıf destek. Etki küçük (bir kat başına ≈ −0,03 çocuk), büyük kentlerle sınırlı ve modele duyarlı. Doğurganlığın ana belirleyicisi değil. |
| **H2** Konut → evliliğin ertelenmesi | İlçe düzeyinde evlilik yaşı verisi alınamadı; açık kaldı. Konut maliyeti verisiyle sınanmalı. |

---

## 4. Sınırlılıklar

- **Ekolojik çıkarım:** Analiz ilçe düzeyinde; bireysel nedensellik göstermez.
- **Zamanlama:** GHSL yüksekliği 2018, doğurganlık 2025. 2023 depremleri sonrasındaki yeniden yapılanma GHSL'de yok.
- **Ölçüm:** GHSL yüksekliği hücre ortalamasıdır; tek tek binaların kat sayısını vermez. TÜİK'in ilçe bazında bina-kat tablosu yok.
- **Standartlaştırma:** Dolaylı standartlaştırma, yaş deseninin Türkiye ortalamasına benzediğini varsayar. Küçük ilçelerde doğum sayısı az olduğu için tahminler gürültülü; ağırlıklandırma bunu azaltıyor.
- **Yabancı nüfus:** Eğitim verisi yabancı nüfusu kapsamıyor. Doğum ve nüfus verilerinde yabancıların kapsamı farklı olabilir; Hatay ve Şanlıurfa gibi göçmen nüfusu yoğun ilçelerde dikkat gerekir.
- **Eğitim değişkeni:** Eğitim kısmen sonuç değişkeni gibi davranıyor (yukarıdaki seçilim notu).

---

## 5. Sonraki adımlar

1. **Bireysel veri (en güçlü test):**
   - TÜİK Gelir ve Yaşam Koşulları Araştırması mikro verisinde konut tipi, hane yapısı ve çocuk sayısı var.
   - Hacettepe Türkiye Nüfus ve Sağlık Araştırması'nda doğum geçmişi ve yerleşim tipi var.
   - Amaç: aynı eğitim düzeyindeki kadınlar arasında konut tipinin etkisini ölçmek. İkisi de başvuru gerektiriyor.
2. **Konut maliyeti kanalı (H2):** İlçe ya da il bazında kira ve fiyat verisi (TCMB, ilan verisi) ile evlenme yaşı ve doğurganlık ilişkisi.
3. **Mekânın daha güçlü kanıtlanmış sonuçları:** Aynı ilçe paneliyle yeşil alan erişimi, yürünebilirlik ve kuşaklar arası yakınlık. Sonuç değişkenleri: yaşlıların çocuğuna yakınlığı (il düzeyinde var; ilçe için MEDAS'a bakılmalı) ile sağlık ve sosyal göstergeler.
4. **Pilot ölçek:** Bu panelin artıkları (eğitime ve mekâna göre beklenenden yüksek ya da düşük doğurganlıklı ilçeler) pilot mahalle seçiminde kullanılabilir.
