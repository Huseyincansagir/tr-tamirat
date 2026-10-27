# Faz 2 · Rapor 1 — 81 İl Paneli: Mekânın Doğurganlık ve Aile Üzerindeki Payı

*25 Ekim 2026 · Sürüm 0.1*

| Ne | Nerede |
|---|---|
| Veri (81 il × 75 değişken, TÜİK) | [03_VERI/islenmis/il_paneli_2025.csv](../03_VERI/islenmis/il_paneli_2025.csv) · [.gpkg](../03_VERI/islenmis/il_paneli_2025.gpkg) · [kaynaklar](../03_VERI/ham/tuik/kaynaklar.md) |
| Analiz kodu | [05_ANALIZ/kod/il_paneli_analiz.py](../05_ANALIZ/kod/il_paneli_analiz.py) · sonuç tabloları: `05_ANALIZ/sonuclar/` |
| Haritalar | [04_HARITA/il_haritalari_2025.png](../04_HARITA/il_haritalari_2025.png) (kod: `04_HARITA/kod/il_haritalari.py`) |
| Grafikler | [mekanin_payi_shapley.png](../05_ANALIZ/grafikler/mekanin_payi_shapley.png) · [il_ici_kent_kir_egitim_farki.png](../05_ANALIZ/grafikler/il_ici_kent_kir_egitim_farki.png) |

---

## Özet

**Soru:** Gelir, eğitim ve bölge sabit tutulduğunda şehrin biçimi (ne kadar dikey, ne kadar yoğun kentsel) illerin doğurganlık ve aile göstergelerini ne kadar açıklıyor?

**Kısa cevap:** İl ölçeğinde **az**. Bulgular şöyle:

1. **Doğurganlıktaki iller arası farkın büyük kısmını bölge-kültür, gelir ve eğitim açıklıyor.**
   - Ana modelde mekânın payı açıklanan farkın **%13'ü**.
   - 12 bölge sabit etkili, mekânsal olarak doğru belirtilmiş modelde bu pay **%5'e** iniyor.
2. **"Ölçek paradoksu" var.**
   - İller arasında, yoğun kentte yaşayan nüfus payı yüksek olan illerin doğurganlığı (kontrollerden sonra) daha *yüksek*.
   - Aynı il içinde ise tablo ters: 75 ilin 57'sinde kırda doğurganlık yoğun kentten yüksek (medyan fark **+0,18 çocuk**).
   - En olası açıklama **seçici göç**. Genç ve doğurgan nüfus büyük kentlere gidiyor, geride yaşlanan ve düşük doğurganlıklı kırsal iller kalıyor.
   - Sonuç: il ölçeği, mekânın etkisini ölçmek için fazla kaba.
3. **Aynı il içinde eğitim farkı, yerleşim farkının yaklaşık 5 katı.** İlkokul mezunu ile yükseköğretim mezunu anne arasındaki medyan fark **0,99 çocuk**.
4. **Dikeyleşme (oturulan binanın ortalama kat sayısı) doğurganlıkla sağlam bir ilişki göstermiyor.**
   - Kadınların ilk evlenme yaşı ve ilk doğum yaşıyla ilişkisi beklenen yönde ve ana modelde anlamlı.
   - Ancak bölge sabit etkileri eklenince anlamlılık kayboluyor: kanıt **zayıf**.
5. **Zihinsel simülasyon (üst sınır):** Yoğun kentte yaşayan kadınların doğurganlığı orta yoğun kent düzeyine çıksaydı Türkiye'nin doğurganlık hızı 1,42'den yaklaşık **1,55'e** yükselirdi. Herkes kır düzeyinde doğursaydı **1,75** olurdu. İki senaryo da yenilenme düzeyinin (2,10) altında.

**Proje için anlamı:** Mekân, doğurganlığı tek başına kurtaracak bir kaldıraç olarak sunulmamalı. Mekânın etkisi il ölçeğinde değil, ilçe, mahalle ve konut tipi ölçeğinde ölçülmeli. Mekân politikası; konuta erişim, eğitim ve değer politikalarıyla birlikte tasarlanmalı. Bu sonuç, Faz 1'deki "mekân gerekli ama yeterli değil" dersini il verisiyle sayısallaştırıyor.

---

## 1. Veri ve yöntem

**Birim:** 81 il. **Kaynak:** TÜİK Veri Portalı'ndaki 2025 doğum, evlenme-boşanma, aile, ADNKS ve eğitim bültenleri; 2024 il GSYH bülteni; 2021 Bina ve Konut Nitelikleri Araştırması. Tablo bazında künye `03_VERI/ham/tuik/kaynaklar.md` dosyasında.

| Grup | Değişken | Not |
|---|---|---|
| **Mekân** | Oturulan binanın ortalama kat sayısı (2021) | 2,2 (Ardahan) – 8,2 (Kayseri); İstanbul 6,9, Ankara 7,1 |
| | Yoğun kentte yaşayan nüfus payı (DEGURBA, 2025) | %0 – %96 |
| | *Sağlamlık için:* 5+ katlı ve 1-2 katlı binada oturan hane payı, ln(nüfus yoğunluğu) | |
| **Gelir** | ln(kişi başı GSYH, 2024) | |
| **Eğitim** | Kadınların ortalama eğitim süresi (2025) | 6,3 – 10,4 yıl |
| **Bölge-kültür** | Doğu-Güneydoğu kuklası (İBBS-1: TRA, TRB, TRC; 24 il) | Sağlamlıkta 12 İBBS-1 bölgesinin sabit etkisi |
| **Sonuçlar** | Toplam doğurganlık hızı; kaba evlenme ve boşanma hızları; kadınların ilk evlenme yaşı; ilk doğumda anne yaşı; hane büyüklüğü; tek kişilik ve geniş aile hane payı; çocuğuyla aynı mahallede ya da daha yakın oturan yaşlı payı | |

**Analiz adımları:**

1. **Ana model:** Her sonuç için standartlaştırılmış en küçük kareler regresyonu (OLS), heteroskedasiteye dayanıklı (HC3) standart hatalarla. Biçimi: z(Y) ~ ortalama kat + yoğun kent payı + ln(GSYH) + kadın eğitim süresi + Doğu-Güneydoğu kuklası.
2. **Pay ayrıştırması (Shapley R²):** Toplam R², dört değişken grubuna adil biçimde bölüştürüldü. Bu, değişkenler birbiriyle ilişkili olduğunda payları ayırmanın standart yoludur.
3. **Eğitim-içi analiz:** Aynı eğitim düzeyindeki annelerin il doğurganlığı mekân ve kontrollerle modellendi; kadın nüfusuyla ağırlıklı en küçük kareler (WLS).
4. **İl-içi farklar:** Kır ile yoğun kent ve ilkokul ile yükseköğretim mezunu anne arasındaki doğurganlık farkları, aynı il içinde.
5. **Sağlamlık testleri:** Alternatif mekân ölçüleri, 12 bölge sabit etkisi, nüfus ağırlığı, batı alt örneklemi, 2020→2025 uzun fark, akraba evliliği oranı (kültür vekili).
6. **Mekânsal otokorelasyon:** Moran's I, komşuluk matrisiyle.

**Çoklu doğrusallık:** Gelir ile eğitim arasındaki korelasyon r = 0,85; VIF değerleri 4,1 ve 3,9. Bu yüzden ikisinin ayrı ayrı payları dikkatle okunmalı; toplam etkileri sağlam.

---

## 2. Bulgular

### 2.1 Ham ilişkiler zayıf

Doğurganlığın açıklayıcılarla Pearson korelasyonu:

| Açıklayıcı | r |
|---|---|
| Ortalama kat sayısı | −0,12 |
| 5+ katlı binada oturan hane payı | −0,20 |
| Yoğun kent payı | +0,07 |
| ln(kişi başı GSYH) | **−0,63** |
| Kadın eğitim süresi | **−0,58** |
| Doğu-Güneydoğu | **+0,66** |

Haritada da görülüyor: doğurganlık haritası, kat sayısı haritasına değil bölge, eğitim ve gelir haritalarına benziyor.

### 2.2 Ana model ve mekânın payı

Değerler standartlaştırılmış katsayılardır (β). Anlamlılık: *** p<0,001 · ** p<0,01 · * p<0,05 · † p<0,10.

| Sonuç | R² | Ortalama kat | Yoğun kent | ln GSYH | Kadın eğitimi | Doğu-GD | **Mekân payı** |
|---|---|---|---|---|---|---|---|
| Toplam doğurganlık hızı | 0,63 | −0,01 | +0,35*** | −0,23* | −0,31* | +0,92*** | **%13** |
| Kadın ilk evlenme yaşı | 0,49 | +0,29* | −0,53** | +0,12 | +0,65* | +0,50 | %32 |
| İlk doğumda anne yaşı | 0,64 | +0,22* | −0,47*** | +0,31† | +0,54** | +0,01 | %20 |
| Kaba boşanma hızı | 0,74 | −0,20† | +0,27* | +0,25 | +0,16 | −1,16*** | %10 |
| Ortalama hane büyüklüğü | 0,67 | +0,01 | +0,36*** | −0,21 | −0,25 | +1,14*** | %14 |
| Tek kişilik hane payı | 0,60 | +0,00 | −0,62*** | +0,11 | +0,30 | −0,89*** | %46 |
| Geniş aile hane payı | 0,24 | −0,17 | +0,07 | +0,06 | −0,31 | +0,52 | %17 |
| Yaşlının çocuğuna yakınlığı | 0,53 | −0,07 | +0,40*** | −0,14 | −0,11 | +1,19*** | %21 |
| Kaba evlenme hızı¹ | 0,45 | −0,19† | +0,76*** | −0,45** | +0,08 | −0,37 | %86 |

¹ Kaba evlenme hızı olay yerine göre kaydediliyor ve yaş yapısına çok duyarlı. Mekân payı bu yüzden şişkin; yorumlanmamalı.

**Mekânsal yapı:** Ana modelin artıklarında anlamlı kümelenme kalıyor (Moran's I = 0,32, p = 0,001). Tek bir Doğu-Güneydoğu kuklası bölgesel farkı yakalamaya yetmiyor; Güneydoğu, Kuzeydoğu'dan belirgin biçimde ayrışıyor. **12 bölge sabit etkili modelde** artıklarda kümelenme kalmıyor (I = 0,03, p = 0,30). Bu yüzden asıl güvenilecek model bu:

| Sonuç (12 bölge sabit etkisiyle) | R² | Ortalama kat | Yoğun kent | Mekân payı | Bölge payı |
|---|---|---|---|---|---|
| Toplam doğurganlık hızı | 0,82 | +0,02 | +0,08 | **%5** | %57 |
| Kadın ilk evlenme yaşı | 0,70 | +0,18 | −0,23 | %13 | %45 |
| İlk doğumda anne yaşı | 0,82 | +0,12 | −0,19* | %9 | %37 |
| Tek kişilik hane payı | 0,72 | −0,15 | −0,35** | %25 | %53 |
| Yaşlının çocuğuna yakınlığı | 0,67 | +0,04 | +0,18 | %10 | %67 |

### 2.3 Ölçek paradoksu: iller arasında artı, il içinde eksi

- **İller arasında:** Kontrollerden sonra yoğun kent payı yüksek iller *daha* doğurgan (β = +0,35).
- **Aynı il içinde:** Yoğun kentte yaşayan kadınlar kırdakilerden daha az doğuruyor. Fark hesaplanabilen 75 ilin 57'sinde kır daha yüksek; ortalama fark +0,19, medyan +0,18 çocuk.

İki bulgu birbiriyle çelişmiyor; farklı süreçleri yakalıyor. Karadeniz ve İç Anadolu'nun kırsal illeri (Sinop, Kastamonu, Bartın, Tunceli, Gümüşhane) gençlerini büyük kentlere gönderiyor. Bu iller yaşlı ve düşük doğurganlıklı, yoğun kent payları da düşük. Büyük kentler ise genç ve doğurgan yaştaki nüfusu topluyor. Bu **seçici göç**, il ölçeğinde "kentsellik" ile doğurganlık arasında yanıltıcı bir artı ilişki üretiyor. Tek kişilik hane payının yoğun kentle *ters* ilişkisi de (β = −0,62) aynı nedenden: tek yaşayan yaşlılar kırsal illerde birikiyor.

**Yöntemsel ders:** İl düzeyinde ölçülen bir "mekân etkisi", göç ve yaş yapısıyla karışıyor. Mekânın etkisi ancak aynı il içinde (ilçe, mahalle) ya da bireysel veriyle ayrıştırılabilir.

### 2.4 Aynı il içinde: yerleşim farkı mı, eğitim farkı mı?

| Aynı il içindeki fark (2025) | İl sayısı | Ortalama | Medyan | Farkın pozitif olduğu il |
|---|---|---|---|---|
| Kır − yoğun kent | 75 | +0,19 | +0,18 | 57 |
| İlkokul − yükseköğretim mezunu anne | 81 | +0,94 | +0,99 | 76 |

Eğitim farkı yerleşim farkının yaklaşık **5 katı**. Üstelik yerleşim farkının bir kısmı zaten eğitim bileşiminden kaynaklanıyor, çünkü yoğun kentteki kadınlar daha eğitimli. Saf mekân etkisi bu yüzden 0,18'den küçük olabilir.

### 2.5 Eğitim sabit tutulduğunda dikeyleşme

Aynı eğitim düzeyindeki annelerin il doğurganlığı (WLS; mekân, gelir ve Doğu kontrollü):

| Annenin eğitimi | Ortalama kat | Yoğun kent | R² |
|---|---|---|---|
| İlkokul | **−0,24*** | +0,38* | 0,46 |
| Ortaokul | −0,02 | +0,38* | 0,71 |
| Lise | −0,12 | +0,36** | 0,70 |
| Yükseköğretim | +0,21 | +0,04 | 0,49 |

Dikeyleşme yalnızca **ilkokul mezunu annelerde** anlamlı ve beklenen yönde çıkıyor. Daha geleneksel aile kalıbındaki kadınlar apartman dokusunun daha yoğun olduğu illerde daha az doğuruyor. Bu, **zayıf ama ilginç bir sinyal**. Diğer eğitim gruplarında bir ilişki yok.

### 2.6 Dikeyleşme ve evliliğin ertelenmesi

- **Ana model:** Ortalama kat sayısı bir standart sapma (≈1 kat) arttığında kadınların ilk evlenme yaşı +0,29 standart sapma, ilk doğum yaşı +0,22 standart sapma artıyor (ikisi de p<0,05).
- **12 bölge sabit etkili model:** Katsayılar +0,18 ve +0,12'ye düşüyor ve anlamlılık kayboluyor.

**Değerlendirme:** Yön, H2 hipoteziyle (konut → evliliğin ertelenmesi) tutarlı. Kanıt ise **zayıf**. Konut maliyeti ve kira verisi eklenmeden kesin bir şey söylenemez.

### 2.7 Sağlamlık özeti (toplam doğurganlık hızı)

| Model | n | R² | Mekân katsayıları |
|---|---|---|---|
| Ana model | 81 | 0,63 | ort. kat −0,01 · yoğun kent +0,35*** |
| 5+ katlı bina payı (ort. kat yerine) | 81 | 0,64 | 5+ kat −0,13 · yoğun kent +0,40*** |
| 1-2 katlı bina payı | 81 | 0,64 | 1-2 kat +0,15 · yoğun kent +0,40*** |
| ln yoğunluk (yoğun kent yerine) | 81 | 0,68 | ort. kat +0,01 · ln yoğunluk +0,42*** |
| + akraba evliliği (kültür vekili) | 81 | 0,73 | ort. kat −0,16* · yoğun kent +0,23** · akraba +0,62*** |
| 12 bölge sabit etkisi | 81 | 0,82 | ort. kat +0,02 · yoğun kent +0,08 |
| Nüfus ağırlıklı | 81 | 0,75 | ort. kat −0,04 · yoğun kent +0,41* |
| Batı alt örneklemi (Doğu hariç) | 57 | **0,08** | ort. kat −0,11 · yoğun kent +0,30† |
| Uzun fark: ΔTDH 2020→2025 | 81 | 0,77 | ort. kat −0,00 · yoğun kent +0,05 · TDH 2020 −0,73*** |

**Öne çıkanlar:**
- **Dikeyleşmenin işareti modelden modele değişiyor:** −0,16 ile +0,15 arasında. Doğurganlıkla sağlam bir ilişki yok.
- **Batı'daki 57 ilde model neredeyse hiçbir şey açıklamıyor (R² = 0,08).** Batı'da doğurganlık 1,09–1,81 aralığında; en yüksek değerler Doğu Akdeniz'de (Hatay 1,81, Osmaniye 1,71, Kahramanmaraş 1,70). İller arası fark küçük ve ne mekân ne de gelir-eğitim onu açıklıyor. Bu, düşük doğurganlığın Batı'da ortak bir "denge" hâline geldiğini düşündürüyor.
- **Uzun fark:** 2020–2025 düşüşü en çok yüksek doğurganlıklı illerde hızlı (yakınsama). Mekân düşüşün hızını açıklamıyor.
- **Kültür vekili:** Akraba evliliği oranı eklendiğinde kültür etkisi çok güçlü çıkıyor (+0,62).

---

## 3. Zihinsel simülasyon: mekân ne kadar fark yaratabilir?

Ulusal doğurganlık hızı kent-kır sınıfına göre (2025): kır **1,75**, orta yoğun kent **1,53**, yoğun kent **1,33**. Nüfusun %67,5'i yoğun kentte yaşıyor.

| Senaryo | Varsayım | Türkiye TDH |
|---|---|---|
| Mevcut | — | 1,42 |
| S1: "Yoğun kent, orta yoğun kent gibi" | Yoğun kentteki kadınların doğurganlığı orta yoğun kent düzeyine çıkar | ≈ **1,55** |
| S2: "Herkes kır gibi" | Bütün kadınlar kır düzeyinde doğurur | ≈ **1,75** |
| Yenilenme düzeyi | | 2,10 |

**Bu hesaplar üst sınırdır.** Sınıflar arası farkın bir kısmı eğitim, yaş ve tercih bileşiminden kaynaklanıyor; yani mekâna atfedilebilecek gerçek kazanç daha küçük. Hesap yine de iki şeyi açıkça gösteriyor:

1. **En iyimser varsayımla bile mekân dönüşümü doğurganlığı yenilenme düzeyine taşımaz.**
2. **Yine de 0,1–0,3 çocukluk bir fark küçük değil.** Bu, mevcut düzeyin %10–20'si ve 2020–2025 arasındaki düşüşün (−0,35) üçte biri ile tamamı arasında bir büyüklük. Mekân politikası, diğer politikalarla birleştiğinde anlamlı bir katkı yapabilir.

---

## 4. Hipotezlere etkisi

| Hipotez | Faz 2 il bulgusu | Durum |
|---|---|---|
| **H1** Yüksek katlı konut payı → düşük doğurganlık | İl düzeyinde sağlam ilişki yok. Yalnızca ilkokul mezunu annelerde −0,24*. | **İl ölçeğinde desteklenmedi.** İlçe ve mahalle ölçeğinde sınanmalı. |
| **H2** Konut → evliliğin ertelenmesi | Ortalama kat ile ilk evlenme ve ilk doğum yaşı arasında artı yönlü ilişki; bölge sabit etkileriyle anlamsız. | **Zayıf destek.** Konut maliyeti verisi gerekli. |
| **H7** Kuşaklar arası yakınlık | Yaşlıların çocuğuna yakınlığını ağırlıkla bölge-kültür açıklıyor (%53–67); mekânın payı %10–21. | Bilgi notu: yakınlık daha çok kültürel bir sermaye. |
| **Yeni bulgu** | Ölçek paradoksu ve seçici göç | Analiz tasarımı buna göre değişmeli. |

---

## 5. Sınırlılıklar

- **Ekolojik çıkarım:** İl düzeyinde bulunan ilişkiler bireylere aktarılamaz. Bireysel nedensellik iddiası yok.
- **Kaba ölçek:** 81 gözlem, il içindeki büyük mekânsal çeşitliliği (İstanbul'da Fatih ile Esenyurt gibi) tek bir ortalamaya indiriyor.
- **Mekân ölçüleri sınırlı:** Ortalama kat sayısı (2021) ve DEGURBA payı mekânı yalnızca iki boyutuyla ölçüyor. Yeşil alan, yürünebilirlik, konut büyüklüğü ve maliyeti henüz modelde yok.
- **Zamanlama:** Kat verisi 2021'e, doğurganlık verisi 2025'e ait. Ters nedensellik (çok çocuklu ailelerin az katlı konutu seçmesi) il ölçeğinde zayıf olsa da tamamen dışlanamaz.
- **Göç ve yaş yapısı:** Doğrudan kontrol edilmedi. Toplam doğurganlık hızı yaş yapısından bağımsız, ama kaba evlenme ve boşanma hızları ile hane göstergeleri değil.
- **Çoklu doğrusallık:** Gelir ile eğitim arasında r = 0,85.

---

## 6. Sonraki adımlar

1. **İlçe paneli (973 ilçe), il sabit etkisiyle:**
   - Bölge ve kültürü il içinde sabit tutmanın en güçlü yolu bu.
   - Doğurganlık vekili: ADNKS'deki ilçe yaş-cinsiyet tablolarından *çocuk-kadın oranı* (0–4 yaş çocuk / 15–49 yaş kadın).
   - Mekân ölçüsü: GHSL bina yüksekliği ve yapılaşma verisinin ilçe ortalamaları ile OSM yeşil alan ve yürünebilirlik.
2. **Bireysel veri:**
   - TÜİK Gelir ve Yaşam Koşulları Araştırması mikro verisi (konut tipi: müstakil / apartman / 10+ daireli bina).
   - Hacettepe Türkiye Nüfus ve Sağlık Araştırması mikro verisi.
   - Amaç: hanede çocuk sayısı ve evlenme yaşını konut tipiyle, bireysel kontrollerle modellemek. İkisi de başvuru gerektiriyor.
3. **Konut maliyeti:** Merkez Bankası konut fiyat endeksi (26 İBBS-2 bölgesi) ve kira verisiyle H2'yi doğrudan sınamak.
4. **Göç:** ADNKS il ve ilçe göç tablolarıyla seçici göçü modellemek; yaş yapısı kontrolü eklemek.
5. **Pilot ölçek:** Seçilecek pilot şehirlerde mahalle düzeyi ölçüm (Fıtrat Uyum Endeksi).
