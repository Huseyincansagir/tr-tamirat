# Faz 3 · Rapor 3 — Uydu Verisiyle Çevre-Ölçek Ekseni (FUE v0.2)

*27 Ekim 2026 · Sürüm 0.1*

| Ne | Nerede |
|---|---|
| Kaynak notu (erişim, lisans, doğrulama) | [03_VERI/ham/uydu_kaynaklar.md](../03_VERI/ham/uydu_kaynaklar.md) |
| Pilot katmanları (10 ilçe, 30 m) | `03_VERI/islenmis/uydu/pilot_<ilçe>.tif` · sahne listesi `landsat_sahneler.csv` · kod `03_VERI/kod/uydu_pilot.py` |
| Ulusal göstergeler (973 ilçe) | `03_VERI/islenmis/ilce_uydu.csv` · kod `03_VERI/kod/uydu_ulusal.py` |
| FUE v0.2 (mahalle) | `05_ANALIZ/sonuclar/fue_mahalle.csv` (`*_v2` sütunları) · kod `05_ANALIZ/kod/fue_mahalle.py` |
| Ulusal sınama | `05_ANALIZ/sonuclar/fue_ilce_gecerlilik.csv` · `fue_ilce_cevre_kontrol.csv` · `fue_ilce_yukseklik_yeniden.csv` |
| Harita ve grafikler | [04_HARITA/uydu_ciftler.png](../04_HARITA/uydu_ciftler.png) · [fue_v02_olumluluk.png](../05_ANALIZ/grafikler/fue_v02_olumluluk.png) · [fue_v02_cevre_kontrol.png](../05_ANALIZ/grafikler/fue_v02_cevre_kontrol.png) |

---

## Özet

**Soru:** Rapor 10'da çevre-ölçek ekseni (Ç) OSM park kaydına ve GHSL yüksekliğine dayanıyordu. Uydu verisiyle ölçülen ağaç örtüsü, hava kirliliği, yüzey sıcaklığı ve yapılı alan bu ekseni güçlendirir mi? Erişim ekseninin (E) ölümlülükle beklenmedik pozitif ilişkisini açıklar mı?

**Kısa cevap:**

1. **Çevre-ölçek ekseni güçlendi.**
   - Dört uydu göstergesi eklenince Ç'nin ölümlülükle ilişkisi belirgin biçimde arttı. 973 ilçede, il içinde, eğitim ve göç sabitken β = **−0,41** (v0.1: −0,27). Kentsellik ve yaş yapısı kontrolleriyle −0,24 (v0.1: −0,17). Hepsi p<0,001.
2. **Sinyalin kaynağı hava kirliliği, yapılı alan ve ağaç örtüsü.** Geniş modelde, yani kentsellik ve yaş yapısı kontrolüyle:
   - **PM2.5:** +0,23\*\*\* (en sağlam gösterge).
   - **300 m çevredeki yapılı alan payı:** +0,27\*\*\*.
   - **Ağaç örtüsü:** −0,14†. Temel modelde −0,34\*\*\*.
   - **Yaz yüzey sıcaklığı:** Hiçbir modelde anlamlı değil.
3. **Erişimin ölümlülükle ilişkisinin yaklaşık üçte biri çevre yüklerinden geliyor.**
   - PM2.5, yüzey sıcaklığı ve ağaç eklenince E'nin katsayısı 0,44'ten **0,31**'e iniyor.
   - Kentsellik ve yaş yapısı da eklenince **0,23**'e iniyor.
   - Kalan ilişki hâlâ anlamlı. Eski merkezlerin nüfus bileşimi ve kurumsal nüfus açıklaması geçerliliğini koruyor.
4. **Faz 2'nin yükseklik bulgusu anlamlılığını yitirdi.**
   - Kat başına ölümlülük etkisi şu sırayla azaldı:
     - Faz 2: %2,56
     - Kentsellik kontrolleriyle (Rapor 10): %1,37
     - PM2.5, sıcaklık ve ağaç da eklenince: **%0,85 (p = 0,15)**
   - Dikeyleşmenin ölümlülükle ilişkisi büyük ölçüde **kirli hava ve ağaçsızlıktan** geçiyor.
5. **Mahalle ölçeğinde tablo karışık.**
   - Pilot mahallelerde v0.2 ekseni v0.1 ile güçlü ama tam olmayan biçimde örtüşüyor (ρ = 0,80). Erişimle ödünleşim sürüyor (ρ = −0,59).
   - Hedef çeyrekteki (E ≥ 60, Ç ≥ 55) mahalle sayısı 8'den **11'e** çıktı.
   - 0–17 yaş payıyla ilişki zayıfladı (+0,8 puan, p = 0,10). Yapılı alan payı yüksek mahallelerde çocuk payı daha düşük (−1,5 / −3,0 puan, p ≤ 0,006).

**Proje için anlamı:** Fıtrata uygun mahallenin sağlık gerekçesi artık daha somut:
- daha az **ince partikül**,
- daha az **sert yüzey**,
- daha çok **ağaç**.

Bunlar, kat sayısından bağımsız olarak tasarım ve şehir politikasıyla değiştirilebilir. Yükseklik kendi başına değil, bu yüklerle birlikte geldiği için önemli.

---

## 1. Veri

| Gösterge | Kaynak | Çözünürlük ve dönem | Erişim |
|---|---|---|---|
| Ağaç örtüsü, yeşil örtü, yapılı alan (300 m yarıçap içinde, %) | ESA WorldCover 2021 v200 | 10 m (pilot); 8× genel bakış ≈ 80 m (ulusal) | AWS açık kova, bulut uyumlu GeoTIFF; yalnız gereken pencereler okundu |
| Yıllık PM2.5 (µg/m³) | ACAG V6.GL.03 (Washington Üniversitesi; uydu AOD + GEOS-Chem + yer ölçümü füzyonu) | 0,01° (~1 km), 2022–2024 ortalaması | `satpmdata` açık kovası; pilotlarda Avrupa dosyaları, ulusalda küresel dosyanın yalnız Türkiye penceresi |
| Yaz gündüz yüzey sıcaklığı (°C) | Landsat 8/9 Collection 2 Level-2 (ST_B10) | 30 m; 2022–2025, 15 Haziran–15 Eylül; ilçe başına 14 bulutsuz sahne ortancası | Microsoft Planetary Computer (anonim SAS belirteci) |
| Yaz gündüz yüzey sıcaklığı, ulusal (°C) | MODIS Aqua MYD11A2 v061 | 1 km; Temmuz–Ağustos 2023 ve 2024, 8 günlük bileşiklerin ortalaması | Planetary Computer |

**CAMS kullanılmadı:** Kullanıcı CAMS PM2.5 istedi. Ancak Copernicus Atmosphere Data Store indirme için hesap ve API anahtarı gerektiriyor; bu çalışmada hesap açılamıyor. ACAG ürünü anahtarsız erişilebiliyor ve daha ince çözünürlüklü (CAMS Avrupa yeniden analizi 0,1°).

**Doğrulama:**
- **Konum:**
  - Fatih katmanında Haliç ve Marmara'nın suyu 26–27 °C.
  - Gülhane Parkı (35,3 °C), 1 km ötesindeki Aksaray'dan (45,6 °C) 10 °C serin.
  - Ağaç örtüsü Gülhane'de %46, Aksaray'da %7.
- **PM2.5:**
  - Po Ovası (18,4) Alpler'den (9,1) yüksek; deniz pikselleri boş.
  - Avrupa ve küresel dosyalar Fatih'te aynı değeri veriyor (20–21 µg/m³).
- **Kapsama:** Her pilotta 14 sahne kullanıldı. Sahnelerdeki geçerli piksel payı %95–100; nihai katmanda boş piksel %0–1.
- **WorldCover genel bakış katmanı:** Çoğunluk sınıfını koruyor (Fatih'te ağaç %12,2'ye karşı tam çözünürlükte %14,8). Ulusal ağaç payı biraz düşük, yapılı alan biraz yüksek. Il sabit etkili karşılaştırmada bu sapma büyük ölçüde sabit kalır.

**Yüzey sıcaklığı nasıl tanımlandı?** Yarı kurak ilçelerde (Kocasinan, Meram, Beypazarı) kent, çevresindeki çıplak tarladan gündüz daha serin. Kayseri merkezi 45,3 °C, Erkilet tarlaları 49,8 °C. Bu yüzden "ilçe alanına göre ısı adası" kenti yanlışlıkla serin gösterir. Göstergeler iki ölçekte farklı tanımlandı:
- **Mahalle FUE'sinde:** **kent içi fark**, yani mahallenin sıcaklığı eksi o ilçenin kentsel mahalle ortalaması.
- **Ulusal sınamada:** **nüfus ağırlıklı mutlak sıcaklık**. Bölgesel iklim il sabit etkisiyle soğuruluyor.

---

## 2. Ulusal sınama (973 ilçe)

Model kurgusu Rapor 10 ile aynı: sonuç z ~ gösterge z + kadın eğitimi + nüfus artışı + il sabit etkisi. Nüfus ağırlıklı, il düzeyinde kümelenmiş SH.

### 2.1 Ölümlülük

| Gösterge | Temel | + ln yoğunluk | + kentsellik ve yaş yapısı |
|---|---|---|---|
| Çevre-ölçek v0.1 (OSM + GHSL) | −0,27\*\*\* | −0,25\*\*\* | −0,17\*\*\* |
| **Çevre-ölçek v0.2 (+ uydu)** | **−0,41\*\*\*** | **−0,36\*\*\*** | **−0,24\*\*\*** |
| Erişim | +0,44\*\*\* | +0,41\*\*\* | +0,31\*\*\* |
| PM2.5 | +0,37\*\*\* | +0,31\*\*\* | +0,23\*\*\* |
| Yapılı alan payı (300 m) | +0,43\*\*\* | +0,40\*\*\* | +0,27\*\*\* |
| Ağaç örtüsü (300 m) | −0,34\*\*\* | −0,29\*\* | −0,14† |
| Yaz yüzey sıcaklığı (mutlak) | +0,22 | +0,14 | −0,07 |
| Yaz yüzey sıcaklığı (ilçe alanına göre fark) | +0,09\* | +0,07\* | +0,04 |

### 2.2 Erişim–ölümlülük ilişkisinin aracılık sınaması

| Model | E katsayısı | PM2.5 | Yüzey sıcaklığı | Ağaç örtüsü |
|---|---|---|---|---|
| Temel | 0,44\*\*\* | — | — | — |
| + PM2.5, sıcaklık, ağaç | **0,31\*\*\*** | +0,22\*\*\* | −0,25 | −0,23\* |
| + kentsellik ve yaş yapısı | 0,31\*\*\* | — | — | — |
| + ikisi birden | **0,23\*\*\*** | +0,20\*\*\* | −0,32† | −0,16† |

- **Çevre yüklerinin payı:** Bu üç gösterge E'nin ölümlülükle ilişkisinin yaklaşık %30'unu açıklıyor.
- **Kentselliğin katkısı:** Kentsellik ve yaş yapısıyla birlikte bu pay yaklaşık %48'e çıkıyor.
- **Kalan kısım:** Ölçülemeyen bileşim etkileri büyük olasılıkla burada: gelir, eski bina stoku, bakım evleri. Bunlar ayrıştırılamadı.

### 2.3 Yükseklik bulgusunun üçüncü sınaması

| Model | Kat başına SMR | p |
|---|---|---|
| Faz 2 modeli | +%2,56 | 0,003 |
| + 15 dk temel ihtiyaç | +%1,90 | 0,014 |
| + ulaşım ve cami | +%1,25 | 0,059 |
| + kent merkezi payı (Rapor 10) | +%1,37 | 0,032 |
| **+ PM2.5, yüzey sıcaklığı, ağaç örtüsü** | **+%0,85** | **0,145** |

Son modelde ölçek şöyle:
- **PM2.5:** +10 µg/m³ başına SMR +0,042 (≈ %4, p<0,001).
- **Ağaç örtüsü:** +10 puan başına −0,011 (≈ −%1,1, p = 0,016).

### 2.4 Aile göstergeleri
Çevre-ölçek v0.2, temel modelde doğurganlıkla (−0,10\*) ve tek kişilik haneyle (+0,45\*\*\*) ilişkili. Ama ilişkilerin hepsi kentsellik ve yaş yapısı kontrolüyle kayboluyor (+0,05). Ağaç örtüsünün doğurganlıkla temel modeldeki negatif ilişkisi (−0,22\*\*\*) bölgesel bileşimi yansıtıyor; ormanlık Karadeniz ve Marmara ilçeleri düşük doğurganlıklı. Faz 2'deki sonuç değişmedi: **mekânın sağlam izi sağlıkta, aile göstergelerinde değil.**

---

## 3. Mahalle düzeyi (10 pilot, 300 kentsel mahalle)

| İlçe | Ç v0.1 | **Ç v0.2** | FUE v0.2 | Ağaç (300 m, %) | PM2.5 | Yaz yüzey sıcaklığı (°C) | Yapılı alan (300 m, %) |
|---|---|---|---|---|---|---|---|
| Safranbolu | 54,2 | **58,2** | 57,1 | 20,2 | 20,0 | 42,2 | 67,9 |
| Antakya | 50,4 | 53,3 | 43,9 | 19,9 | 25,0 | 43,8 | 54,9 |
| Beypazarı | 51,7 | 50,5 | 51,7 | 2,3 | 17,6 | 45,4 | 76,5 |
| Meram | 51,5 | 49,9 | 49,6 | 7,2 | 24,4 | 41,4 | 68,9 |
| Silivri | 41,5 | 49,9 | 51,8 | 10,6 | 15,4 | 42,5 | 56,5 |
| Nilüfer | 45,6 | 46,8 | 51,6 | 11,5 | 24,7 | 44,0 | 75,2 |
| Başakşehir | 33,1 | 45,1 | 52,8 | 14,2 | 17,7 | 43,2 | 67,8 |
| Fatih | 42,4 | 44,0 | 68,1 | 8,5 | 21,2 | 44,7 | 88,8 |
| Kocasinan | 47,8 | 42,6 | 47,4 | 3,8 | 26,8 | 44,0 | 79,9 |
| Onikişubat | 46,6 | 42,4 | 47,7 | 6,7 | 29,0 | 45,9 | 80,3 |

Kentsel mahallelerin nüfus ağırlıklı ortalaması. Sıcaklık sütunu mutlak değerdir; endekste kent içi fark kullanıldı.

**Okuma:**
- **Kim yükseldi, kim düştü?** Başakşehir (+12) ve Silivri (+8) temiz hava ve görece ağaçlık sayesinde yükseldi. Kocasinan ve Onikişubat kirli hava ve ağaçsızlık yüzünden düştü (−5, −4).
- **İlçe içi sıcaklık farkı:** Kentsel mahalleler arasındaki en büyük fark çoğu ilçede 5 °C civarında. Antakya'da yaklaşık 10 °C (−4,1 ile +5,7 °C arası), Beypazarı'nda 1,4 °C.
- **Hedef çeyrek:** E ≥ 60 ve Ç v0.2 ≥ 55 olan mahalle sayısı 11. Bunların 6'sı Fatih'te (Cankurtaran, Mevlanakapı, Molla Hüsrev, Muhsine Hatun, Şehsuvar Bey, Yedikule). Diğerleri Silivri'de Çayırdere ve Fatih Mahallesi, Nilüfer'de 19 Mayıs, Antakya'da Kışlasaray, Safranbolu'da Yenimahalle.
- **Çocuk payıyla ilişki** (ilçe sabit etkisi, 1 SS başına puan):
  - **Ç v0.2:** +0,82 (p = 0,10).
  - **Yapılı alan payı:** −1,51 (p = 0,006). ln yoğunluk kontrolüyle −2,97 (p = 0,001).
  - **Kent içi sıcaklık farkı:** +0,95 (p = 0,008). Çocuklu aileler çeperdeki yeni, ağaçsız ve sıcak alanlarda yoğunlaşıyor.
  - **PM2.5 ve ağaç:** anlamsız.

  Bu ilişkiler betimseldir; mahalle düzeyinde eğitim ve gelir verisi yok.

---

## 4. Sınırlılıklar

- **PM2.5 modellenmiş bir alan.** ACAG ürünü 1 km'de; uydu, kimyasal taşınım modeli ve yer ölçümünün füzyonu. Sokak ölçeğindeki trafik kaynaklı farkları yakalamaz; mahalle içi farklar düzleşir.
- **Yüzey sıcaklığı hava sıcaklığı değildir.** Landsat yaklaşık 10:40'ta geçiyor; çatı, asfalt ve toprağın güneşli gündüz sıcaklığını ölçüyor. Gece ısı adası (sağlık için daha önemli) ölçülmedi.
- **MODIS 1 km kıyıda denizle karışıyor.** Fatih'te MODIS'in nüfus ağırlıklı değeri 36,8 °C; Landsat'ta kentsel mahalle ortalaması 44,7 °C.
- **Antakya'nın sahneleri depremi kapsıyor.** 2022'den 2025'e uzanıyor; ortanca deprem öncesi ve sonrası durumu karıştırıyor. WorldCover 2021 ise deprem öncesine ait.
- **Ekolojik çıkarım:** İlçe düzeyindeki ilişkiler bireysel riski göstermez. Nedensellik iddiası yok.

---

## 5. Kavramsal çerçeve ve sonraki adımlar

1. **FUE v0.2 çevre-ölçek ekseni** artık 12 gösterge: v0.1'in sekizi + PM2.5, ağaç örtüsü (300 m), yaz yüzey sıcaklığı (kent içi fark), yapılı alan payı (300 m).
2. **Dikeyleşme → ölümlülük** hipotezi "orta güçte" iken **"çevre yükleriyle açıklanıyor"** durumuna geçti. Tasarım gündeminde kat sınırı kendi başına değil, PM2.5'i düşüren ulaşım ve ısınma politikası ile ağaçlandırma ve geçirgen yüzeyle birlikte savunulmalı.
3. **Model mahalle:**
   - Ağaç örtüsü hedefi (%30) ve sert yüzeyi sınırlayan bahçe ve avlu kuralları artık ampirik destekli.
   - PM2.5 yer seçimine bağlı. Pilotlarda 15 (Silivri) ile 29 µg/m³ (Onikişubat) arasında; DSÖ yıllık kılavuz değeri 5 µg/m³.
4. **Sonraki ölçüm:**
   - Gece yüzey sıcaklığı (MODIS gece ya da ECOSTRESS).
   - Kurumsal nüfusun ölümlülükten ayrıştırılması.
   - Trafik yoğunluğu verisi (belediye sayımları).
