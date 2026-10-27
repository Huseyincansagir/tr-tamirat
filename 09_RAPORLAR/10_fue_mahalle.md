# Faz 3 · Rapor 1 — Pilot İlçelerde Mahalle Düzeyinde Fıtrat Uyum Endeksi

*26 Ekim 2026 · Sürüm 0.1*

> **Güncelleme (27.10.2026):** Çevre-ölçek ekseni uydu verisiyle (ağaç örtüsü, PM2.5, yüzey sıcaklığı, yapılı alan) güçlendirildi; FUE v0.2. Yükseklik–ölümlülük ilişkisi PM2.5 ve ağaç örtüsü kontrol edilince anlamlılığını yitiriyor (kat başına %0,85, p = 0,15). Bu rapordaki v0.1 sayıları geçerli; v0.2 için bkz. [Faz 3 · Rapor 3](13_fue_uydu_cevre.md).

| Ne | Nerede |
|---|---|
| Mahalle birimleri, göstergeler ve endeks (656 mahalle, 18 gösterge) | [03_VERI/islenmis/pilot_mahalleler.gpkg](../03_VERI/islenmis/pilot_mahalleler.gpkg) · `05_ANALIZ/sonuclar/fue_mahalle.csv` |
| Tablolar | `fue_gosterge_tanim.csv` · `fue_ilce_ozet.csv` · `fue_eslesme.csv` · `fue_duyarlilik.csv` · `fue_gecerlilik_mahalle.csv` · `fue_osm_kapsam.csv` · `fue_ilce_gecerlilik.csv` · `fue_ilce_yukseklik_yeniden.csv` (hepsi `05_ANALIZ/sonuclar/`) |
| Ulusal sınama verisi (973 ilçe) | `03_VERI/islenmis/ilce_fue_lite.csv` |
| Yeni ham veri | `03_VERI/islenmis/pilot_mahalle_nufus_2025.csv` (MEDAS, [kaynak notu](../03_VERI/ham/tuik/mahalle_kaynaklar.md)) · `03_VERI/islenmis/pilot_mahalle_tkgm.gpkg` (TKGM) · `03_VERI/islenmis/pilot_osm/` (OSM: sınır, yaya ağı, donatı, bina) |
| Kod | `03_VERI/kod/osm_pilot_mahalle.py` · `03_VERI/kod/tkgm_mahalle.py` · `05_ANALIZ/kod/fue_mahalle.py` · `05_ANALIZ/kod/fue_ilce_gecerlilik.py` · `05_ANALIZ/kod/fue_grafikler.py` · `04_HARITA/kod/fue_haritalari.py` |
| Haritalar | [04_HARITA/fue_mahalle_pilotlar.png](../04_HARITA/fue_mahalle_pilotlar.png) · [04_HARITA/fue_erisim_cevre_ciftler.png](../04_HARITA/fue_erisim_cevre_ciftler.png) |
| Grafikler | [fue_ilce_profili.png](../05_ANALIZ/grafikler/fue_ilce_profili.png) · [fue_erisim_cevre_odunlesim.png](../05_ANALIZ/grafikler/fue_erisim_cevre_odunlesim.png) · [fue_gecerlilik_ilce.png](../05_ANALIZ/grafikler/fue_gecerlilik_ilce.png) · [fue_yukseklik_yeniden.png](../05_ANALIZ/grafikler/fue_yukseklik_yeniden.png) |

---

## Özet

**Soru:** Kavramsal çerçevedeki Fıtrat Uyum Endeksi (FUE) pilot ilçelerin mahallelerinde nasıl dağılıyor? Endeks gerçekten "insana iyi gelen" mekânı ölçüyor mu?

**Kısa cevap:** Endeks hesaplandı. Ama geçerlilik sınamasında **iki parçaya ayrıldı** ve bu parçalar ters yönde çalışıyor.

1. **Endeks kuruldu.**
   - 10 pilot ilçedeki 656 mahallenin 654'üne sınır bulundu; bu mahallelerde 3,32 milyon kişi yaşıyor.
   - Bunların 300'ü kentsel; 3,02 milyon kişi, yani pilot nüfusun %91'i.
   - Her kentsel mahalle için 18 mekân göstergesi hesaplandı. Mesafeler kuş uçuşu değil, **gerçek yaya ağı üzerinden** ölçüldü (2,36 milyon sokak parçası).
   - En yüksek FUE **Fatih**'te (72). En düşük **Antakya**'da (41; deprem sonrası, OSM kaydı da çok eksik). Diğer sekiz ilçe 48–55 arasında.
2. **Endeksin içinde bir ödünleşim var.**
   - Göstergeler iki aileye ayrılıyor:
     - **Erişim (E):** okula, camiye, markete, durağa yürüyerek ulaşmak ("15 dakikalık şehir").
     - **Çevre-ölçek (Ç):** yeşil alan, az kat, ana yoldan uzaklık, yayılmama, küçük mahalle.
   - Mahalleler arasında ikisi **ters ilişkili** (Spearman ρ = −0,61).
   - 300 kentsel mahallenin yalnızca **39'u** ikisinde birden pilot medyanının üstünde. Bu mahallelerde 311 bin kişi yaşıyor.
   - Bu dengeyi en iyi kuran ilçe **Safranbolu**: 8 kentsel mahallenin 5'i, nüfusun %61'i. **Başakşehir ve Antakya'da hiç yok.**
3. **Ulusal geçerlilik sınaması (973 ilçe, il içi, eğitim ve göç sabit).**
   - **Çevre-ölçek, düşük ölümlülükle sağlam biçimde ilişkili:** β = −0,27***. Kentsellik ve yaş yapısı kontrolleriyle de β = −0,17***.
   - **Erişim ise yüksek ölümlülükle ilişkili:** β = +0,44***; geniş modelde +0,31***.
   - Toplam FUE, iki etkinin bileşkesi olarak ölümlülükle **pozitif** çıkıyor (+0,36***). Yani ilk tasarımıyla geçerlilik sınavını **geçemedi**.
4. **Faz 2'nin "yükseklik → ölümlülük" bulgusu yarıya iniyor.**
   - Erişim ve kent merkezi göstergeleri eklenince kat başına etki **%2,56'dan %1,25–1,37'ye** düşüyor.
   - İlişki zayıflıyor ama kaybolmuyor (p = 0,03–0,06).
   - Faz 2'deki etkinin bir kısmı dikeyleşmeden değil, genel olarak **kent merkezinde yaşamaktan** geliyor.
5. **Mahalle düzeyinde de aynı örüntü var.**
   - İlçe içinde Ç'si yüksek mahallelerde 0–17 yaş payı daha yüksek: Ç'de 1 SS artış başına +1,4 puan, p = 0,001.
   - E'si yüksek mahallelerde daha düşük: −1,5 puan, p = 0,04.
   - Mahalle düzeyinde eğitim ve gelir verisi olmadığı için bu bulgu **betimseldir**. Ailelerin çocuk sahibi olunca yeşil ve az katlı çepere taşınması aynı örüntüyü üretir.

**Proje için anlamı:**
- "15 dakikalık şehir" erişimi tek başına sağlıklı şehir ölçüsü değil. Türkiye'de erişimin iyi olduğu yer eski kent merkezi; orada hava, gürültü, yaşlı bina stoku ve seçici göç de var.
- Fıtrata uygun mahalle **erişimi çevre-ölçeği bozmadan** sağlayan mahalledir.
- FUE bundan sonra **iki eksenli** raporlanmalı (E ve Ç). Hedef, ikisinde birden iyi olmak.
- Model mahalle v2'nin tasarım problemi tam olarak bu: Safranbolu tipi bir denge.

---

## 1. Veri ve birimler

### 1.1 Mahalle nüfusu
TÜİK MEDAS'tan "Belediye, köy ve mahalle nüfusları" alındı: ADNKS 2025, 18 yaş üstü ve altı. 10 pilot ilçede 658 mahalle var. Mahalle toplamları ilçe nüfuslarıyla birebir tutuyor; farklar yalnızca TÜİK'in 10'un altındaki çocuk sayılarını gizlemesinden kaynaklanıyor ([kaynak notu](../03_VERI/ham/tuik/mahalle_kaynaklar.md)). İki not:
- Safranbolu büyükşehir dışında olduğu için köyleri bu tabloda yok. Burada yalnızca 21 belediye mahallesi var.
- Fatih'in tarihî ticaret mahallelerinde nüfus çok az (Sarıdemir 11, Rüstempaşa 17 kişi). Bu mahalleler kentsel kapsamın dışında kaldı.

### 1.2 Mahalle sınırları: üç kaynak, sırayla

| Sıra | Kaynak | Eşleşen mahalle | Nüfus | Not |
|---|---|---|---|---|
| 1 | OSM `admin_level=8` (idari ad) | 421 | 2.798.756 | Fatih, Silivri, Başakşehir, Beypazarı'nda %100 |
| 2 | TKGM MEGSİS kadastro mahallesi (OSM ile çakışan kısım çıkarılarak) | 182 + 9 bulanık eşleşme | 364.498 | Safranbolu ve Antakya'nın çoğu buradan |
| 3 | OSM yer noktası → Voronoi (ilçenin atanmamış alanı, 1,5–2,5 km yarıçap) | 44 | 155.595 | **Yaklaşık sınır**; haritalarda kesikli çizgi |
| — | Eşleşmedi | 2 | 8.546 | Kocasinan Camikebir (7.512), Onikişubat Kale (1.034) |

- Ad eşleştirmede Türkçe karakterler sadeleştirildi ve "Mahallesi/Köyü" ekleri atıldı.
- Bileşik adlar ayrıştırıldı: "Erkilet Osman Gazi" → Osmangazi, "5.Mıntıka/Haraparası" → Haraparası, "Yeni" ↔ Yenimahalle.
- Son adımda difflib ile bulanık eşleştirme yapıldı (eşik 0,82). Kalan dokuz bulanık eşleşmenin hepsi elle kontrol edildi (ör. Allazı ↔ Alazı, Bohşin ↔ Boşin).
- geoBoundaries ilçe sınırı sadeleştirilmiş olduğu için mahalle sınırları ona göre kırpılmadı.

### 1.3 Kentsel mahalle tanımı
Kentsel mahalle iki koşulu birlikte sağlıyor:
- ADNKS nüfusu en az 1.000.
- GHS-POP nüfusunun en az yarısı ≥1.500 kişi/km² yoğunluktaki hücrelerde (AB-DEGURBA kent merkezi yoğunluk eşiği).

Bu tanımla **300 mahalle** kentsel. Endeksin yüzdelik puanları bu 300 mahalle arasında hesaplandı. Kentsel olmayan mahalleler (eski köyler, sanayi, ticaret çekirdeği) haritalarda gri.

### 1.4 Mesafe ölçümü
- **Kökenler:** GHS-POP 2020'nin 100 m hücreleri. Hücre nüfusları her mahallede ADNKS 2025 toplamına ölçeklendi.
- **Yaya ağı:** OSM'deki bütün yürünebilir yollar (otoyol hariç). Hücreler ve donatılar en yakın ağ düğümüne bağlandı, bağlanma mesafesi toplam mesafeye eklendi. Her donatı türü için çok kaynaklı Dijkstra hesaplandı (scipy).
- **Kuş uçuşu ölçülenler:** yeşil alan (300 m, DSÖ ölçütü), ana yol (100 m) ve dükkân yakınlığı (150 m).
- **Tutarlılık kontrolü:** Ağ üzerinden ölçülen erişim payları, ulusal sınamadaki kuş uçuşu eşdeğerleriyle (§4.1) 10 ilçede r = 0,86–0,95 korelasyonlu. Sokak ağının dolambaçlı ya da eksik olduğu yerlerde ağ değerleri belirgin biçimde düşük. Örneğin Antakya'da ilk/ortaokula 500 m ağ erişimi %7,6, kuş uçuşu 400 m erişimi %22. Kuş uçuşu ölçü, erişimi kopuk dokularda abartıyor.

---

## 2. Göstergeler

| Boyut | Gösterge | Yön | Alt endeks | Kentsel medyan |
|---|---|---|---|---|
| B1 Beden ve Can | Kavşak yoğunluğu (/km² yapılı alan) | + | E | 133 |
| B1 | 15 dk'da okul + sağlık/eczane + market (≤1.200 m ağ) | + | E | %57 |
| B2 Akıl ve Ruh | ≥0,5 ha yeşil alana 300 m | + | Ç | %15 |
| B2 | Yaşanan bina yüksekliği (GHSL, nüfus ağırlıklı) | − | Ç | 8,4 m |
| B2 | Yüksek binalı hücrede yaşayan (≥15 m, ~5+ kat) | − | Ç | %0 |
| B2 | Ana yola (otoyol, devlet yolu, birincil yol) 100 m | − | Ç | %9 |
| B3 Nesil ve Aile | Az katlı hücrede yaşayan (≤9 m, ~3 kat) | + | Ç | %58 |
| B3 | Oyun alanına 400 m (ağ) | + | E | %0 |
| B3 | İlk/ortaokula 500 m (ağ) | + | E | %28 |
| B4 Mülk ve Geçim | Dükkân / 1.000 kişi | + | E | 0,4 |
| B4 | Dükkân ya da kafeye 150 m | + | E | %13 |
| B5 Topluluk ve İnanç | Camiye 500 m (ağ) | + | E | %64 |
| B5 | Buluşma mekânına 400 m (kahve, kütüphane, toplum merkezi, pazar, meydan) | + | E | %3 |
| B5 | Ad ya da etiketle kapalı site alanı (deneysel) | − | Ç | %0 |
| B5 | Mahalle nüfusu (muhtar başına, ln) | − | Ç | 6.800 kişi |
| B6 Mizan | Durağa 400 m ya da raylıya 800 m (ağ) | + | E | %6 |
| B6 | Yapılı alan / 1.000 kişi | − | Ç | 16 ha |
| B6 | Raylı istasyona 800 m (ağ) | + | E | %0 |

- **Hesaplama:**
  - Her gösterge 300 kentsel mahalle arasında yüzdelik puana (0–100) çevrildi ve yönü düzeltildi.
  - Boyut puanı, o boyuttaki göstergelerin ortalaması.
  - **FUE**, altı boyutun eşit ağırlıklı ortalaması (çerçeve §4.3).
  - **E** ve **Ç** alt endeksleri, geçerlilik sınamasından sonra eklendi (bkz. §4).
- **Bu turda hesaplanamayanlar:** PM2.5, ağaç örtüsü (NDVI), geçirimsiz yüzey, yaya kazası ve riskli bina payı. Hepsi ek uydu ya da kurum verisi gerektiriyor.

---

## 3. Bulgular

### 3.1 İlçe profilleri

Değerler kentsel mahallelerin nüfus ağırlıklı ortalamasıdır; puanlar 0–100 arasıdır.

| İlçe | Kentsel mah. | FUE | E | Ç | 15 dk temel (%) | İlk/ortaokul 500 m (%) | Cami 500 m (%) | Yeşil 300 m (%) | Yükseklik (m) | Ana yol 100 m (%) | 0–17 yaş (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Fatih | 32 | **72,1** | **88,3** | 42,4 | 99,7 | 89,1 | 98,5 | 53,5 | 13,2 | 20,8 | 19,3 |
| Safranbolu | 8 | 54,5 | 55,4 | **54,2** | 69,5 | 29,5 | 75,6 | 8,3 | 8,8 | 1,3 | 23,3 |
| Nilüfer | 36 | 53,1 | 56,4 | 45,6 | 59,3 | 32,9 | 35,4 | 43,4 | 8,7 | 15,0 | 22,1 |
| Kocasinan | 34 | 51,5 | 54,2 | 47,8 | 57,9 | 46,6 | 71,1 | 59,3 | 10,0 | 21,7 | 25,8 |
| Onikişubat | 59 | 51,2 | 52,9 | 46,6 | 75,6 | 54,5 | 68,9 | 29,5 | 10,5 | 9,3 | 31,1 |
| Beypazarı | 5 | 50,5 | 50,6 | 51,7 | 67,6 | 41,2 | 74,4 | 53,8 | 8,8 | 14,7 | 25,4 |
| Başakşehir | 9 | 50,0 | 59,6 | **33,1** | 71,8 | 33,7 | 44,8 | 54,8 | 12,5 | 16,9 | 29,1 |
| Meram | 41 | 49,9 | 49,9 | 51,5 | 47,3 | 31,0 | 77,6 | 18,3 | 6,6 | 9,2 | 27,4 |
| Silivri | 20 | 47,9 | 50,3 | 41,5 | 42,4 | 18,6 | 27,7 | 20,0 | 6,9 | 20,8 | 20,3 |
| Antakya | 56 | **40,9** | **34,0** | 50,4 | 26,0 | 7,6 | 25,5 | 7,1 | 7,0 | 11,1 | 31,3 |

**Okuma notu:**
- Cami, okul, oyun alanı ve durak göstergeleri OSM kaydına bağlı. OSM'nin kapsamı ilçeden ilçeye çok değişiyor (§6.1).
- Bu yüzden **E'yi ilçeler arasında karşılaştırırken temkinli olun**. İlçe içinde mahalleleri karşılaştırmak daha güvenilir.
- Antakya'nın düşük E'si hem depremin yıkımını hem OSM'nin deprem sonrası güncellenmemesini yansıtıyor.

### 3.2 Doğal karşılaştırma çiftleri

**Fatih–Silivri** (kadın eğitimi aynı: 9,6 ve 9,7 yıl)
- **Erişim:** Fatih'te en yakın ilk/ortaokula ortalama ağ mesafesi **314 m**, Silivri'de **1.528 m**. Camiye 182 m ile 989 m, markete 129 m ile 1.005 m.
- **Çevre-ölçek:** İki ilçe aynı düzeyde (42 ve 41,5), ama farklı nedenlerle. Fatih'te sorun yükseklik (13,2 m) ve ana yol. Silivri'de sorun yeşil alan eksikliği (%20) ve yayılma.
- **Çocuk payı:** Neredeyse aynı (%19,3 ve %20,3). Biçim çok farklı olduğu halde aile göstergesi farklılaşmıyor; bu, Faz 2'nin "doğurganlıkta mekânın payı küçük" bulgusuyla tutarlı.

**Kocasinan–Meram**
- **Biçim:** Meram belirgin biçimde daha az katlı. Az katlı hücrede yaşayanların payı %78'e karşı %40.
- **Yeşil erişim:** Meram'da çok zayıf (%18'e karşı %59).
- **Sonuç:** Ç değerleri yakın (51,5 ve 47,8). Az katlı doku tek başına iyi çevre demek değil. Konya'nın yatay dokusu park sistemiyle desteklenmemiş.

### 3.3 Erişim–çevre ödünleşimi ve "ikisinde birden iyi" mahalleler

E ile Ç arasındaki ters ilişki her ilçede var. İlçe içi Spearman katsayısı Kocasinan'da −0,71, Meram'da −0,70, Antakya'da −0,66; Başakşehir'de −0,17 ve Fatih'te −0,14 ile en zayıf.

| İlçe | İki alt endekste de ≥50 olan mahalle | Nüfus payı |
|---|---|---|
| Safranbolu | 5 / 8 | **%61** |
| Meram | 6 / 41 | %18 |
| Fatih | 6 / 32 | %16 |
| Kocasinan | 5 / 34 | %16 |
| Nilüfer | 6 / 36 | %13 |
| Onikişubat | 8 / 59 | %11 |
| Silivri | 2 / 20 | %4 |
| Beypazarı | 1 / 5 | %3 |
| Başakşehir | 0 / 9 | %0 |
| Antakya | 0 / 56 | %0 |

Daha sıkı ölçütle (E ≥ 60 ve Ç ≥ 55) dengeli mahalleler şunlar:
- Fatih: Molla Hüsrev, Şehsuvar Bey, Muhsine Hatun
- Silivri: Fatih Mahallesi
- Onikişubat: Mağralı
- Nilüfer: 19 Mayıs
- Silivri: Çayırdere
- Kocasinan: Beyazşehir (18.517 kişi)

Bunlar Faz 3 saha anketi ve "pozitif sapma" incelemesi için mahalle adaylarıdır.

**Başakşehir notu:** Faz 2'de beklenenden düşük ölümlülükle pozitif sapma gösteren Başakşehir'de Ç pilotların en düşüğü (33). Başakşehir'in iyi sağlık sonucu mekânın Ç bileşeniyle açıklanmıyor. Genç, eğitimli ve yeni konutlu nüfus bileşimi ile kurumlar daha olası açıklamalar.

---

## 4. Geçerlilik

Kavramsal çerçeve (§4.3, adım 5) endeksin sonuç göstergeleriyle, eğitim ve göç kontrol edilerek sınanmasını şart koşuyor. Mahalle düzeyinde eğitim ve gelir verisi yok. Bu yüzden sınama iki düzeyde yapıldı.

### 4.1 Ulusal sınama: 973 ilçede FUE-lite

- **Kurulum:** Aynı 16 gösterge Türkiye geneli için hesaplandı. Mahalle sınırı ve muhtar başına nüfus gerektiren iki gösterge hariç tutuldu.
  - Mesafeler kuş uçuşu. Eşikler ağ eşiklerinin 1/1,25'i: okul 400 m, 15 dk 960 m.
  - Hesap 3,32 milyon nüfuslu 100 m hücre üzerinden yapıldı.
- **Model:** Sonuç z ~ endeks z + kadın eğitim yılı + nüfus artışı + il sabit etkisi. Nüfus ağırlıklı, il düzeyinde kümelenmiş SH.
- **Geniş model:** ln yoğunluk, kent merkezi payı ve 65+ payı da eklendi.

| Sonuç | E (temel) | E (+ln yoğunluk) | E (geniş) | Ç (temel) | Ç (+ln yoğunluk) | Ç (geniş) |
|---|---|---|---|---|---|---|
| Standartlaştırılmış ölüm oranı | **+0,44\*\*\*** | +0,41\*\*\* | +0,31\*\*\* | **−0,27\*\*\*** | −0,25\*\*\* | −0,17\*\*\* |
| Toplam doğurganlık hızı | −0,02 | −0,01 | −0,12\*\* | −0,02 | −0,02 | +0,06 |
| Tek kişilik hane payı | −0,34\*\*\* | −0,19\* | +0,01 | +0,18\*\* | +0,16\*\*\* | +0,02 |
| 25–34 yaş kadında hiç evlenmemiş | −0,14\* | −0,12 | +0,10† | +0,22\*\*\* | +0,21\*\*\* | +0,06 |
| Geniş aile hanesi payı | −0,03 | −0,04 | −0,10† | +0,02 | +0,02 | +0,06 |
| Boşanma hızı | +0,12\* | +0,13\*\*\* | +0,14\*\* | −0,10\*\*\* | −0,10\*\*\* | −0,10\*\*\* |

\*\*\* p<0,001 · \*\* p<0,01 · \* p<0,05 · † p<0,10. Toplam FUE-lite'ın ölümlülükle ilişkisi +0,36\*\*\* (temel) ve +0,25\*\*\* (geniş).

**Okuma:**
- **Sağlamlık:** Ç'nin ölümlülük ve boşanmayla ilişkisi üç model kurgusunda da anlamlı ve beklenen yönde.
- **Erişim ve ölümlülük:** E'nin ölümlülükle ilişkisi beklenenin **tersi** ve o da sağlam.
- **Bastırma etkisi:** Ham korelasyonlar sıfıra yakın (E ile SMR r = 0,06; Ç ile −0,07). Ama iki eksen de kadın eğitimiyle güçlü ilişkili: E pozitif (r = 0,73), Ç negatif (r = −0,57). Eğitimli nüfus kent merkezinde ve yüksek dokuda yaşıyor. Eğitim sabitlenince E "aynı eğitimde daha kentsel ve merkezî olmayı", Ç ise "aynı eğitimde daha yeşil ve alçak dokuda yaşamayı" ölçmeye başlıyor.
- **Muhtemel açıklamalar** (bu veriyle ayrıştırılamıyor):
  1. Eski merkezlerde seçici göç ve yaşlı, yoksul nüfusun yoğunlaşması. Eğitim SES'in yalnızca bir parçası.
  2. Hava kirliliği, gürültü ve ısı adası.
  3. Kurumsal nüfus. Bakım evleri ve hastaneye yakın konutlar merkezde; ADNKS'de kurum adresi ikamet sayılıyor.
  4. OSM'nin merkezlerde daha iyi haritalanması.
- **Ne söylenemez:** "Okula yakınlık ölümlülüğü artırır" demek mümkün değil. Söylenebilecek olan şu: **erişim, çevre yükleri ve nüfus bileşiminden ayrıştırılmadan sağlık göstergesi olarak kullanılamaz.**

### 4.2 Faz 2 bulgusunun yeniden sınanması: yükseklik ve ölümlülük

| Model | Kat başına (+3 m) SMR değişimi | p |
|---|---|---|
| Faz 2 modeli (yükseklik, yoğunluk, yeşil, kavşak, eğitim, göç, il SE) | **+%2,56** | 0,003 |
| + 15 dk temel ihtiyaç erişimi | +%1,90 | 0,014 |
| + ulaşım ve cami erişimi | +%1,25 | 0,059 |
| + kent merkezi payı | +%1,37 | 0,032 |

- Faz 2'nin "en sağlam mekân bulgusu" **yaklaşık yarıya iniyor**, ama sıfıra inmiyor.
- **Düzeltilmiş ifade:** "Aynı il içinde, eğitim, göç, yoğunluk ve kentsellik göstergeleri sabitken yaşanan bina yüksekliğindeki her kat ≈ %1,3 daha yüksek standartlaştırılmış ölümlülükle ilişkili (p ≈ 0,03–0,06)."
- Kavramsal çerçeve §7 ve Faz 2 sentezi buna göre güncellenmeli (bkz. §7).

### 4.3 Mahalle düzeyi (300 kentsel mahalle, ilçe sabit etkisi)

| Değişken (1 SS artış) | 0–17 yaş payında değişim (puan) | p |
|---|---|---|
| FUE | −0,91 | 0,27 |
| Erişim (E) | −1,53 | 0,04 |
| Çevre-ölçek (Ç) | **+1,39** | 0,001 |
| B2 Akıl ve Ruh | +1,07 | 0,002 |
| B6 Mizan | −1,33 | <0,001 |

İlçe sabit etkili, nüfus ağırlıklı WLS, HC3 standart hata. ln yoğunluk eklenince yönler ve büyüklükler korunuyor.

Ulusal örüntü mahalle düzeyinde de var. Çocuklu haneler yeşil ve az katlı mahallelerde, yetişkin ve yaşlı haneler erişimi yüksek merkezlerde yoğunlaşıyor. Bu ilişki **yaşam döngüsüne göre yer seçimini** de yansıtır ve eğitim, gelir kontrolü olmadan yorumlanamaz.

---

## 5. Duyarlılık

| Varyant | FUE ile Spearman ρ (300 mahalle) |
|---|---|
| Göstergelere eşit ağırlık (boyut yerine) | 0,978 |
| Yükseklik göstergeleri çıkarıldığında | 0,976 |
| Kapalı site göstergesi çıkarıldığında | 0,981 |
| Yüzdelik yerine z-puanı (±3'te kesilmiş) | 0,899 |
| PCA birinci bileşen ağırlıkları | 0,904 |

- **Sıralama:** Mahallelerin FUE sıralaması ağırlık ve normalizasyon seçimlerine duyarlı değil.
- **Tek boyutluluk:** Göstergeler tek bir boyut oluşturmuyor. PCA'nın birinci bileşeni varyansın yalnızca %48'ini açıklıyor. İki alt endeksli yapı (§4) bu nedenle hem kuramsal hem istatistiksel olarak daha doğru.

---

## 6. Sınırlılıklar

### 6.1 OSM kapsamı: 10.000 kişiye düşen kayıt

| İlçe | Dükkân | Market | Cami | Okul | Durak | Oyun alanı | Eczane |
|---|---|---|---|---|---|---|---|
| Fatih | 167,6 | 34,3 | 9,2 | 4,4 | 8,1 | 1,0 | 11,3 |
| Silivri | 11,8 | 7,2 | 2,5 | 1,8 | 12,3 | 1,8 | 2,5 |
| Başakşehir | 5,3 | 2,0 | 1,5 | 2,0 | 11,8 | 4,3 | 1,7 |
| Nilüfer | 4,8 | 1,9 | 1,6 | 1,8 | 2,4 | 1,8 | 1,5 |
| Kocasinan | 3,0 | 1,6 | 6,1 | 3,4 | 14,4 | 0,2 | 3,4 |
| Meram | 3,0 | 1,5 | 12,4 | 2,6 | 5,5 | 1,1 | 3,2 |
| Antakya | 10,3 | 5,3 | 2,3 | 1,0 | 0,2 | 0,1 | 3,8 |
| Onikişubat | 3,0 | 1,6 | 4,2 | 2,8 | 1,4 | 0,5 | 2,6 |
| Safranbolu | 7,6 | 4,8 | 5,7 | 2,3 | 4,4 | 0,8 | 1,1 |
| Beypazarı | 4,4 | 1,2 | 11,4 | 2,1 | 0,2 | 1,5 | 4,1 |

- **Cami:** Türkiye'de 10.000 kişiye yaklaşık 10 cami düşüyor (Diyanet'e göre ~90 bin cami). Nilüfer, Başakşehir, Silivri ve Antakya'da OSM bunun yalnızca %14–24'ünü kaydetmiş.
- **Diğer kayıtlar:** Dükkân ve market kaydı Fatih dışında çok eksik. Durak kaydı Antakya ve Beypazarı'nda neredeyse yok.
- **Çözüm önerisi:** E'nin ilçeler arası karşılaştırması için MEB okul listesi (adres), Diyanet cami listesi, Sağlık Bakanlığı ASM listesi ve belediyelerin GTFS verisi gerekli (§8).

### 6.2 Diğer sınırlılıklar
- **Zaman uyumsuzluğu:** GHSL yükseklik verisi 2018, nüfus dağılımı 2020 yılına ait. Antakya ve Onikişubat'ta 2023 depremi bina stokunu ve nüfus dağılımını değiştirdi. Bu iki ilçenin mahalle değerleri **deprem öncesi dokuyu** gösteriyor.
- **Yaklaşık sınırlar:** 44 mahallenin (155.595 kişi) sınırı Voronoi ile kuruldu. TKGM kadastro mahalleleri de idari mahallelerle her zaman örtüşmüyor.
- **Kapalı site göstergesi zayıf:** OSM'de `access=private` ya da `gated=yes` etiketi neredeyse hiç yok. Ad tabanlı tahmin ("Sitesi", "Konutları") eksik kalıyor. Uydu görüntüsü ya da belediye verisi gerekli.
- **Kesitsel veri:** Nedensellik iddiası yok. Seçici yer seçimi (ailelerin çocukla birlikte çepere taşınması) mahalle sonuçlarını açıklayabilir.

---

## 7. Kavramsal çerçeve için sonuçlar (FUE v0.2 önerisi)

1. **İki eksen:** FUE iki alt endeksle raporlanmalı.
   - **E — Erişim:** Günlük ihtiyaçlara yürüyerek ulaşma.
   - **Ç — Çevre-ölçek:** Doğa, insan ölçeğinde yükseklik, trafikten uzaklık, yayılmama, küçük mahalle.
   - Tek bileşik puan, eksenler arasındaki ödünleşimi gizliyor.
2. **Hedef tanımı:** "Fıtrata uygun mahalle" = **E ≥ 60 ve Ç ≥ 55**. Pilotlardaki 8 mahalle bu ölçütü sağlıyor; model mahalle v2 için de bu ölçüt hedef olmalı.
3. **Sağlık gerekçesi Ç'ye dayanmalı:** Ulusal veride ölümlülükle doğrulanan eksen Ç. E'nin gerekçesi zaman, çocuk ve yaşlı bağımsızlığı ve araç bağımlılığının azalması. Bunlar Faz 2 simülasyonlarında büyük çıktı, ama ampirik olarak henüz ölçülmedi. Saha anketi ve Zaman Kullanım Araştırması mikro verisi gerekli.
4. **Faz 2 bulgu 3'ün güncellenmesi:** Kat başına ölümlülük etkisi kentsellik kontrolleriyle ≈ %1,3'e iniyor (Faz 2'de %2,5).

---

## 8. Sonraki adımlar

| # | İş | Gerekçe |
|---|---|---|
| 1 | MEB okul, Diyanet cami, Sağlık Bakanlığı ASM/eczane ve belediye GTFS verilerini toplamak | E'nin OSM eksikliği; ilçeler arası karşılaştırma |
| 2 | Sentinel-2 NDVI ve ağaç örtüsü (ESA WorldCover 10 m) | Ç'nin yeşil bileşenini parka bağımlı olmaktan çıkarmak |
| 3 | Copernicus CAMS PM2.5 ve Landsat yüzey sıcaklığı | E–ölümlülük ilişkisini açıklayacak çevre yükleri |
| 4 | Deprem sonrası güncel bina verisi (Antakya, Onikişubat) | GHSL 2018 deprem öncesini gösteriyor |
| 5 | Saha anketi: "ikisinde birden iyi" mahalleler ile her iki çiftin karşıt mahalleleri | Zaman, bağımsızlık ve komşuluk sonuçları, mekânın asıl iddiası |
| 6 | Bakım evleri ve kurumsal nüfusun SMR'den ayrıştırılması | E–ölümlülük ilişkisinin artefakt olup olmadığı |
