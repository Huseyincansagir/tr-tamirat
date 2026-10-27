# Faz 2 · Rapor 5 — Pilot İlçe Seçimi

*26 Ekim 2026 · Sürüm 0.1 · Karar önerisi; kullanıcı onayıyla kesinleşir*

| Ne | Nerede |
|---|---|
| Seçim kodu | [05_ANALIZ/kod/pilot_secimi.py](../05_ANALIZ/kod/pilot_secimi.py) |
| Tablolar | `05_ANALIZ/sonuclar/pilot_secim_son.csv` · `pilot_istanbul_ciftleri.csv` · `pilot_adaylar.csv` · `pilot_pozitif_sapma.csv` |
| Harita | [04_HARITA/pilot_ilceler.png](../04_HARITA/pilot_ilceler.png) |

---

## Özet

Ana plandaki dört pilot türü veriye dayanarak somutlaştırıldı ve buna bir beşinci tür eklendi: "pozitif sapma". **10 ilçe** öneriliyor:

| Pilot türü | İlçeler | Neden |
|---|---|---|
| **1. Megakent karşılaştırma çifti** | İstanbul **Fatih** – **Silivri** | Kadın eğitimi neredeyse aynı (9,62 ile 9,71 yıl; fark 0,09), biçim çok farklı. Fatih: tarihî, sık dokulu, 14 m, kavşak 272/km², park erişimi %60. Silivri: çeper, 6 m, kavşak 69/km², park erişimi %19. "Aynı eğitim, farklı şehir" doğal karşılaştırması. |
| **2. Anadolu karşılaştırma çifti** | Kayseri **Kocasinan** – Konya **Meram** | Kültür, bölge ve eğitim benzer (9,41 ile 9,33 yıl), yükseklik farklı (7,9 m ile 4,8 m). Türkiye'nin en dikey ili Kayseri ile yatay Konya. |
| **3. Deprem sonrası yeniden inşa** | Hatay **Antakya**, Kahramanmaraş **Onikişubat** | Yeniden kurma penceresi açık. GHSL 2018, deprem öncesi durumun kaydı. |
| **4. Geleneksel doku referansı** | **Safranbolu**, **Beypazarı** | Ölçülecek tarihî dokular (parsel, sokak, avlu); sonraki çalışma (morfoloji ölçümü). |
| **5. Pozitif sapma** | İstanbul **Başakşehir**, Bursa **Nilüfer** | İl içinde, eğitim ve göç sabitken beklenenden düşük ölümlülük ve beklenene yakın ya da üstünde doğurganlık. İkisi de planlı, yeşil ve **yüksek** yeni yerleşim. |

**Dürüstlük notu:** Pozitif sapma gösteren ilk 50 ilçe, mekân bakımından diğerlerinden farklı değil. Yükseklik 9,3'e karşı 9,3 m, park erişimi %25,5'e karşı %26,1. Başakşehir ve Nilüfer ise yüksek binalı ama planlı ve yeşil. Bu, "az kat her zaman iyidir" tezini değil, **"plan kalitesi, yeşil ve kurumlar önemlidir"** tezini destekliyor. Pilotlar bu iki tezi ayırt edebilecek biçimde seçildi.

---

## 1. Seçilen ilçelerin profili (2025)

| İlçe | Nüfus | TDH | Ölüm oranı (SMR) | Kadın eğitimi (yıl) | Yükseklik (m) | 5+ kat (%) | Park erişimi (%) | Kavşak/km² | Tek kişilik hane (%) | 25–34 yaş kadın bekâr (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| Fatih (İst.) | 351.786 | 1,07 | 1,10 | 9,62 | 13,99 | 34,8 | 59,9 | 272 | 28,8 | 45,9 |
| Silivri (İst.) | 240.029 | 1,35 | 0,99 | 9,71 | 6,30 | 6,0 | 19,2 | 69 | 22,1 | 25,6 |
| Kocasinan (Kayseri) | 421.472 | 1,40 | 1,06 | 9,41 | 7,89 | 7,6 | 48,1 | 89 | 16,8 | 24,8 |
| Meram (Konya) | 349.685 | 1,53 | 0,96 | 9,33 | 4,84 | 0,7 | 13,6 | 89 | 15,7 | 24,2 |
| Antakya (Hatay) | 301.855 | 1,81 | 1,07 | 8,73 | 9,04 | 8,9 | 13,1 | 77 | 24,9 | 21,4 |
| Onikişubat (K.Maraş) | 447.591 | 1,58 | 0,88 | 9,50 | 11,48 | 24,2 | 34,2 | 87 | 13,8 | 21,1 |
| Safranbolu (Karabük) | 69.592 | 1,16 | 0,99 | 9,94 | 7,47 | 0,0 | 8,5 | 37 | 22,4 | 29,9 |
| Beypazarı (Ankara) | 48.359 | 1,52 | 0,91 | 8,82 | 7,97 | 2,1 | 40,7 | 70 | 23,3 | 22,5 |
| Başakşehir (İst.) | 536.797 | 1,39 | **0,76** | 10,72 | 13,09 | 30,6 | 48,3 | 67 | 13,9 | 31,3 |
| Nilüfer (Bursa) | 578.059 | 1,06 | **0,82** | 11,64 | 8,29 | 2,9 | 38,5 | 85 | 19,5 | 32,1 |

**Notlar:**
- Yükseklik değerleri GHSL hücre ortalamasıdır; ilçe merkezlerinde gerçek bina yükseklikleri daha fazladır.
- Safranbolu ve Beypazarı'nın ilçe ortalamaları, tarihî çekirdek dışındaki yeni dokuyu da içeriyor. Tarihî dokunun kendi ölçümü ayrı yapılacak (Faz 3 morfoloji ölçümü).
- Antakya ve Onikişubat'ın 2025 değerleri deprem sonrası durumu yansıtıyor.

## 2. Seçim yöntemi

1. **İstanbul çiftleri:**
   - Koşullar: kadın eğitimi farkı <0,5 yıl, 15–49 yaş kadın nüfusu oranı <2.
   - Puan: (yükseklik farkı / SS) + (park erişimi farkı / SS).
   - İlk 8 çift `pilot_istanbul_ciftleri.csv` dosyasında; en yüksek puanlı çiftlerin hepsi Silivri'yi içeriyor.
   - Fatih–Silivri, eğitim farkı en küçük olduğu (0,09) ve Fatih tarihî bitişik doku taşıdığı için seçildi. Silivri–Beyoğlu çifti daha yüksek puanlı, ama Beyoğlu'nun nüfusu ve dokusu daha karışık.
2. **Anadolu:** Kayseri ve Konya'nın merkez ilçeleri karşılaştırıldı. Eğitimi en yakın ve yüksekliği en farklı ikili Kocasinan–Meram.
3. **Pozitif sapma:**
   - Kriter: il sabit etkisi + eğitim + göç modelinden doğurganlık artığı (z) + ölüm artığı (z, ters işaretli). Örneklem: 20 binden fazla 15–49 yaş kadını olan ilçeler.
   - Listenin başındaki Harran, Akçakale ve Reyhanlı'da sapmanın başlıca kaynağı yüksek doğurganlık ve kültürel bağlam. Bu nedenle pilot için mekânsal ders çıkarılabilecek planlı yerleşimler, Başakşehir ve Nilüfer, seçildi.

## 3. Her pilotta yapılacaklar

1. **Mahalle düzeyinde Fıtrat Uyum Endeksi.** Mahalle sınırları, OSM bina ve sokak verisi ve GHSL ile her mahallede yükseklik, park erişimi, 15 dakikada okul, cami ve sağlık erişimi, kavşak yoğunluğu ve kapalı site payı ölçülecek.
2. **Saha anketi** (komşuluk, çocuğun bağımsız hareketi, kuşaklar arası mesafe, aile kurma niyeti). Fatih–Silivri ve Kocasinan–Meram çiftlerinde aynı anketle.
3. **Morfoloji ölçümü.** Safranbolu ve Beypazarı tarihî çekirdeklerinde parsel, ada, sokak genişliği, kat ve avlu; model mahalle parametrelerinin kalibrasyonu.
4. **Deprem pilotları.** Mevcut yeniden yapılanma projelerinin (TOKİ, köy evi) model mahalle ölçütleriyle karşılaştırılması.
5. **Pozitif sapma incelemesi.** Başakşehir ve Nilüfer'de hangi kurumların ve tasarım kararlarının (park sistemi, okul ve cami ağı, yeni yerleşim planı) fark yarattığının nitel analizi.

## 4. Karar noktaları

- Seçimin onaylanması ya da değiştirilmesi.
- Saha anketi için üniversite ve belediye ortaklığı. Etik kurul ve izin süreçleri bu projenin dışında, kullanıcı ve ortaklar tarafından yürütülmeli.
