# Faz 2 · Rapor 4 — Mekânın Doğurganlık Dışındaki Sonuçları (973 İlçe)

*26 Ekim 2026 · Sürüm 0.1*

| Ne | Nerede |
|---|---|
| Genişletilmiş panel (973 ilçe × 130+ değişken) | [03_VERI/islenmis/ilce_paneli_genis.csv](../03_VERI/islenmis/ilce_paneli_genis.csv) |
| Yeni veri | `ilce_olum_nufus.csv` (MEDAS ölüm ve yaş-cinsiyet) · `ilce_hane_medeni.csv` (MEDAS hane tipi ve medeni durum) · `ilce_evlenme_bosanma.csv` (SDMX) · `ilce_osm.csv` (OSM park erişimi, kavşak, cami, okul) |
| Kod | `03_VERI/kod/osm_ilce.py` · `03_VERI/kod/ilce_evlenme_bosanma.py` · `05_ANALIZ/kod/ilce_diger_sonuclar_analiz.py` · `05_ANALIZ/kod/ilce_diger_grafik.py` |
| Grafik | [05_ANALIZ/grafikler/ilce_mekan_katsayilari.png](../05_ANALIZ/grafikler/ilce_mekan_katsayilari.png) |

---

## Özet

**Soru:** Rapor 2 mekânın doğurganlığa doğrudan etkisinin küçük olduğunu gösterdi. Mekânın etkisi sağlık, hane yapısı ve evlilik zamanlaması gibi diğer sonuçlarda daha mı belirgin?

**Kısa cevap:** Çoğunlukla hayır. Bir istisna var: **ölümlülük**.

1. **Yüksek binalarda yaşayan ilçelerde ölümlülük daha yüksek.**
   - Aynı il içinde, kadın eğitimi, yoğunluk, park erişimi, sokak bağlantılılığı ve göç sabitken her 3 m (≈ bir kat) daha yüksek yaşanan bina, **yaşa ve cinsiyete göre standartlaştırılmış ölüm oranında yaklaşık %2,5 artışla** ilişkili.
   - İlişki 8 farklı model kurgusunun hepsinde anlamlı: ağırlıklı ve ağırlıksız, büyükşehir içi ve dışı, ek eğitim ve hane kontrolleriyle.
   - Projenin şimdiye kadarki **en sağlam mekân bulgusu** bu. Ancak 5+ katlı doku payıyla ölçüldüğünde anlamsız; etki aşırı yüksek binalardan değil, genel dikeyleşmeden geliyor.
   - **Faz 3 düzeltmesi (26.10.2026):** Yürüyerek erişim (15 dk temel ihtiyaç, ulaşım, cami) ve kent merkezi payı da kontrol edilince etki kat başına ≈ %1,3'e iniyor (p = 0,03–0,06). Bkz. [Faz 3 · Rapor 1](10_fue_mahalle.md), §4.2. PM2.5, yüzey sıcaklığı ve ağaç örtüsü de kontrol edilince %0,85'e iniyor ve anlamlılığını yitiriyor (p = 0,15; [Faz 3 · Rapor 3](13_fue_uydu_cevre.md)).
2. **Eğitim kontrol edilince diğer ilişkiler kayboluyor.** Ham haliyle mekânla ilişkili görünen sonuçların hepsi kadın eğitimi eklenince sıfıra yaklaşıyor: geniş aile payı, 25–34 yaş kadınların bekâr payı, boşanma hızı ve doğurganlık.
3. **Yoğunluk ile tek kişilik hane arasında ters ilişki var.** Daha yoğun yaşanan ilçelerde tek kişilik hane payı daha düşük (β = −0,23***). Ancak tek kişilik hanelerin asıl belirleyicisi göç ve kırsal yaşlanma (Göç payı %47).
4. **Park erişimi hiçbir sonuçla sağlam bir ilişki göstermiyor.**
   - OSM'ye göre nüfusun yalnızca **%27,6**'sı 300 m içinde en az 0,5 ha bir parka ulaşıyor.
   - Park erişiminin ölümlülükle ham ilişkisi beklenen yönde (β = −0,14*), ama eğitim eklenince işareti dönüyor ve anlamlılığı modelden modele değişiyor.
   - OSM'de park kaydının eksik ve bölgeye göre eşitsiz olması bu sonucu zayıflatıyor.
5. **İl içi farkın bölüşümü.** Kadın eğitimi ölümlülükteki il içi farkın %80'ini, doğurganlığınkinin %73'ünü, geniş aile payınınkinin %77'sini açıklıyor. Mekânın payı %17–28.

**Proje için anlamı:** Mekânın insan üzerindeki en net izi **sağlıkta** görünüyor; aile ve evlilik göstergelerinde değil. Bu, Rapor 2'deki öneriyi güçlendiriyor: **"fıtrata uygun şehir" savunusunun ana gerekçesi sağlık ve can güvenliği olmalı** (ölümlülük, deprem, hava, hareket). Aile hedefleri ise konut erişimi ve eğitim-aile uyumu politikalarıyla birlikte ele alınmalı.

---

## 1. Yeni veriler ve doğrulama

| Veri | Kaynak | Doğrulama |
|---|---|---|
| İlçe ölümleri, cinsiyete göre, 2024–2025 | MEDAS "İlçelere göre ölüm sayısı (ikametgâh yeri)" | Toplam 489.734 ve 491.684, Türkiye toplamıyla aynı |
| Türkiye yaş-cinsiyete özel ölümler, 2024–2025 | MEDAS "İkametgâh yerine göre ölüm sayısı" (17 yaş grubu) | Toplamlar ilçe toplamıyla birebir aynı |
| İlçe × cinsiyet × 19 yaş grubu nüfus, 2024 ve 2025 | MEDAS ADNKS | 2024 ve 2025 ilçe nüfusu SDMX ile 973/973 aynı |
| Beklenen ölüm (dolaylı standartlaştırma) | Tarayıcıda hesaplandı | Σ beklenen = Σ gerçek, iki yılda da |
| Hane tipleri, 2025 | MEDAS ADNKS | 26.977.795 hane; tek kişilik 5.523.321 (il paneliyle aynı) |
| Medeni durum, 25–44 yaş kadın, 2025 | MEDAS ADNKS | 25–34 yaş kadınların %29,3'ü hiç evlenmemiş |
| Evlenme 2014–2025, boşanma 2014–2025 | SDMX `DF_EVLENME_IL_ILCE`, `DF_BOSANMA_IL_ILCE` | 2025 toplamları: evlenme 552.237, boşanma 193.793 |
| Park (≥0,5 ha), kavşak, cami, okul | OpenStreetMap, Geofabrik 25.10.2026 (652 MB, md5 doğrulandı) | 7.840 kentsel yeşil alan (24.020 ha) · 2,1 milyon kavşak · 66 bin cami ve okul noktası |

**OSM tanımları:**
- **Kentsel yeşil alan:** `leisure` = park, bahçe (özel olmayan), oyun alanı, rekreasyon alanı, ortak alan; `landuse` = recreation_ground, village_green. Doğa koruma alanları (`nature_reserve`) çıkarıldı; 330 alan toplam 4,8 milyon ha tutuyordu ve erişimi yapay olarak şişiriyordu.
- **Park erişimi:** GHSL 100 m nüfus hücrelerinin, en yakın ≥0,5 ha yeşil alana kuş uçuşu ≤300 m olan payı (DSÖ ölçütü).
- **Kavşak yoğunluğu:** Derecesi ≥3 olan sokak düğümleri / yapılı alan km². Otoyol, servis yolu, patika ve yaya yolu hariç.

---

## 2. Bulgular

### 2.1 İl içi modeller

Değerler standartlaştırılmış katsayılardır (β); il sabit etkili, nüfus ağırlıklı, il düzeyinde kümelenmiş standart hata. Anlamlılık: *** p<0,001 · ** p<0,01 · * p<0,05 · † p<0,10.

| Sonuç | Kontroller | R² | Yükseklik | ln yoğunluk | Park erişimi | ln kavşak | Kadın eğitimi | Göç |
|---|---|---|---|---|---|---|---|---|
| **Ölüm oranı (SMR)** | yalnız mekân | 0,42 | −0,11 | +0,17† | **−0,14*** | +0,09 | | |
| | + eğitim + göç | 0,62 | **+0,20*** | +0,08 | +0,06 | +0,02 | **−0,71***** | +0,15* |
| **Doğurganlık** | yalnız mekân | 0,78 | −0,26*** | +0,07 | −0,14*** | +0,01 | | |
| | + eğitim + göç | 0,84 | −0,03 | +0,02 | −0,01 | −0,04 | −0,52*** | +0,20† |
| **25–34 yaş kadın bekâr payı** | yalnız mekân | 0,53 | +0,39† | −0,19† | +0,14* | +0,04 | | |
| | + eğitim + göç | 0,70 | +0,08 | **−0,15**** | +0,01 | +0,08† | +0,72*** | −0,69* |
| **Tek kişilik hane payı** | + eğitim + göç | 0,58 | −0,02 | **−0,23***** | −0,07* | −0,03 | +0,19* | −0,43** |
| **Geniş aile hane payı** | yalnız mekân | 0,50 | −0,16** | +0,01 | −0,08† | +0,07 | | |
| | + eğitim + göç | 0,56 | −0,02 | −0,02 | +0,01 | +0,04 | −0,32*** | +0,07 |
| **Ortalama hane büyüklüğü** | + eğitim + göç | 0,80 | +0,00 | +0,09* | +0,03 | +0,02 | −0,20** | +0,27** |
| **Boşanma hızı** | yalnız mekân | 0,79 | +0,18*** | −0,06 | +0,08*** | +0,05 | | |
| | + eğitim + göç | 0,84 | +0,03 | −0,02 | −0,01 | +0,08† | +0,33*** | −0,04 |
| Evlenme hızı¹ | + eğitim + göç | 0,22 | −0,05 | −0,10 | +0,06 | −0,09 | +0,11 | −0,16 |

¹ Evlenmeler olay (tescil) yerine göre kaydediliyor; ilçe düzeyinde gürültülü, yorumlanmamalı.

### 2.2 İl içi açıklanan farkın bölüşümü (Shapley)

| Sonuç | İl sabit etkisi R² | Toplam R² | Mekân | Eğitim | Göç |
|---|---|---|---|---|---|
| Ölüm oranı | 0,39 | 0,62 | %17 | **%80** | %2 |
| Doğurganlık | 0,72 | 0,84 | %24 | **%73** | %3 |
| 25–34 yaş kadın bekâr payı | 0,43 | 0,70 | %21 | **%56** | %22 |
| Geniş aile hane payı | 0,46 | 0,56 | %21 | **%77** | %2 |
| Boşanma hızı | 0,75 | 0,84 | %28 | **%69** | %2 |
| Tek kişilik hane payı | 0,44 | 0,58 | **%47** | %6 | **%47** |
| Ortalama hane büyüklüğü | 0,76 | 0,80 | %22 | %34 | %45 |

### 2.3 Ölümlülük ve bina yüksekliği: sağlamlık

Ham etki, ölüm oranında 1 m başına değişim olarak:

| Model | Yükseklik (SMR / m) | p |
|---|---|---|
| Ana model (beklenen ölümle ağırlıklı) | +0,0085 | 0,003 |
| Ağırlıksız | +0,0084 | <0,001 |
| + yükseköğretimli kadın payı | +0,0072 | 0,001 |
| + tek kişilik hane payı | +0,0084 | 0,001 |
| Büyükşehir ilçeleri | +0,0091 | 0,004 |
| Büyükşehir dışı | +0,0099 | 0,001 |
| Yalnızca beklenen ölümü >400 olan ilçeler (küçük ilçeler hariç) | +0,0076 | 0,011 |
| 5+ katlı doku payı (yükseklik yerine) | +0,0004 / puan | 0,233 |

**Yorum:** Her 3 m daha yüksek yaşanan bina, ölüm oranında yaklaşık +0,025 artış demek. Ortalama 1,00 olduğu için bu ≈%2,5'lik bir artış. Etki büyük değil ama tutarlı.

**Olası mekanizmalar** (bu analizle ayrıştırılamaz):
- **Ana arterlere yakınlık ve hava kirliliği**
- **Isı adası**
- **Hareketsiz yaşam:** asansör, yürünecek sokak ve dış mekân azlığı.
- **Sosyal yalıtım**
- **Eğitimle yakalanamayan gelir veya göçmen bileşimi**

Ters işaretli ve beklenmeyen bir bulgu da var: eğitim kontrolünden sonra park erişiminin katsayısı küçük ama artı. Bu büyük olasılıkla OSM park kaydının merkezî, eski ve iyi haritalanmış ilçelerde yoğunlaşmasından kaynaklanıyor. Bu ilçelerin nüfusu yaşa göre düzeltilse de farklı bir sağlık profiline sahip. Sağlam bir yeşil alan ölçüsü için uydu tabanlı bitki örtüsü (Sentinel-2 NDVI) ya da belediye park envanteri gerekiyor.

---

## 3. Hipotezlere etkisi

| Hipotez / önerme | Durum |
|---|---|
| **H1** Yüksek kat → düşük doğurganlık | İl içinde zayıf; bu genişletilmiş modelde anlamsız (β = −0,03) |
| **H3** Yürünebilirlik ve yeşil → sağlık | Kavşak yoğunluğu ile ölüm arasında ilişki yok. Park erişimi kararsız; ölçüm sorunlu. **Sınanamadı.** |
| **Yeni** Dikeyleşme → ölümlülük | **Orta güçte, tutarlı bir ilişki** (kat başına ≈ +%2,5). Bireysel veriyle sınanmalı. |
| **H8** Kapalı site → zayıf komşuluk | Veri yok. Kapalı site sınırları OSM'de sistematik değil. |
| Kuşaklar arası yakınlık | İlçe düzeyinde veri yok; il düzeyinde bölge-kültür baskın (Rapor 1) |

---

## 4. Sınırlılıklar

- **Ekolojik ve kesitsel tasarım.** İlçe düzeyindeki ilişkiler bireylere aktarılamaz.
- **Ölüm oranı sağlığın kaba bir ölçüsü.** Ölüm nedenleri ilçe düzeyinde alınamadı; trafik ve kalp-damar ayrımı yapılamıyor.
- **OSM'nin eksikliği.** Parklar, özellikle küçük şehirlerde, eksik kaydediliyor. Kavşak yoğunluğu da OSM yol verisinin tamlığına bağlı.
- **Zamanlama.** GHSL yüksekliği 2018'e ait; deprem bölgesindeki ilçelerin 2024–2025 nüfus ve ölüm verisi deprem sonrası göç ve yeniden yapılanmadan etkileniyor.
- **Eksik kontrol.** Gelir ilçe düzeyinde yok; eğitim yalnızca kısmi bir sosyoekonomik vekil.

## 5. Sonraki adımlar

1. **Ölümlülük bulgusunu derinleştirmek:**
   - İlçe düzeyinde ölüm nedeni verisi (Sağlık Bakanlığı ya da TÜİK özel talep).
   - Hava kirliliği (ÇŞİDB istasyonları, CAMS) ve ısı adası (Landsat yüzey sıcaklığı) kontrolleri.
2. **Yeşil alanı uydu verisiyle yeniden ölçmek:** Sentinel-2 NDVI.
3. **Bireysel veri:** TÜİK Türkiye Sağlık Araştırması mikro verisinde konut tipi ile obezite, fiziksel aktivite ve depresyon ilişkisi (başvuru gerekiyor).
