# Kentsel Stres Etkenleri — Kanıt Taraması

*27 Ekim 2026 · Sürüm 0.1 · Faz 4 · Rapor 1'in eki ([09_RAPORLAR/14_kentsel_stres.md](../09_RAPORLAR/14_kentsel_stres.md))*

| Ne | Nerede |
|---|---|
| Künye ve özet doğrulama tablosu (76 kaynak) | `05_ANALIZ/sonuclar/stres_literatur_kunye.csv` |
| Ham yanıtlar (Crossref, PubMed, Europe PMC, Semantic Scholar, PMC tam metni) | `03_VERI/ham/stres/literatur/` |
| Doğrulama kodu | `05_ANALIZ/kod/stres_literatur_dogrula.py` |
| Etken → mekanizma → sağlık şeması | [05_ANALIZ/grafikler/stres_sema.png](../05_ANALIZ/grafikler/stres_sema.png) |
| Projenin önceki kaynakçası | [kaynakca.csv](kaynakca.csv) (tema 1, 2, 5) |

---

## Yöntem

**Soru.** Günümüz şehirlerinde insanın stresini artıran 13 etkenin her biri için şunlar arandı:
- Hangi biyolojik ya da psikolojik yoldan etki ediyor (mekanizma)?
- Sağlık sonucuyla ilişkisi ne büyüklükte (tercihen meta-analiz)?
- Kanıt ne kadar güçlü?

**Nasıl doğrulandı?**
1. Kaynaklar önceden bilinen künyelerden seçildi. Literatür taraması sistematik değildir; seçim yanlılığı olabilir.
2. Her DOI Crossref'te açıldı. Başlık, dergi, yıl, cilt ve sayfa oradan alındı. 76 kaynağın 76'sı bulundu.
3. Özet PubMed'den okundu. PubMed'de yoksa sırayla Crossref, Europe PMC ve Semantic Scholar denendi. 71 kaynağın özeti okundu.
4. Bir DOI yanlıştı (Min ve Min 2018). PubMed'de başlıkla düzeltildi. Gove 1979'un DOI araması PubMed'de ilgisiz bir kayda düştü; kod başlık karşılaştırmasıyla bunu yakalayıp attı.
5. Falchi ve ark. 2016'nın Türkiye değerleri PMC tam metnindeki Tablo 2'den okundu.

**İşaretler.**
- **[D]** Sayı özette ya da tam metinde görüldü.
- **[D·k]** Sayı bu oturumda görülmedi. Projenin `kaynakca.csv` dosyasında önceki oturumda doğrulandı diye kayıtlı.
- **[İ]** İkincil kaynaktan ya da otomatik özetten (Semantic Scholar TLDR).
- **[DY]** Doğrulanmadı. Künye doğru, ama sayı ya da bulgu okunamadı.

**Kanıt düzeyi** (şemadaki etiketler):
- **MA:** meta-analiz.
- **D:** sistematik derleme ya da anlatı derlemesi.
- **B:** boylamsal ya da kohort çalışma.
- **Ö:** öncül, laboratuvar ya da nitel çalışma.

Etki büyüklükleri gözlemsel çalışmalardandır. Aksi yazmadıkça nedensellik kanıtı sayılmamalıdır.

---

## Özet tablo

| # | Etken | Ana mekanizma | En güçlü nicel kanıt | Düzey | Türkiye'de ölçüm |
|---|---|---|---|---|---|
| 1 | **Gürültü** | Uyku bölünmesi, stres hormonu, amigdala → arter iltihabı | Karayolu gürültüsü +10 dB Lden → iskemik kalp hastalığı RR **1,08** (1,01–1,15) [D] | MA | İl algı anketi (İLYE 2015), ulusal SILC; maruziyet haritası açık değil |
| 2 | **Hava kirliliği** | Sistemik ve beyin iltihabı, oksidatif stres | PM2.5 +10 µg/m³ → doğal nedenli ölüm RR **1,08** (1,06–1,09); depresyon OR **1,10** [D] | MA | İlçe (ACAG) |
| 3 | **Isı** | Uyku kaybı, termoregülasyon yükü, saldırganlık | +1 °C → ruh sağlığı ölümü RR **1,022**; aylık intihar **+%1,5** [D] | MA | İlçe (MODIS yüzey sıcaklığı) |
| 4 | **Kalabalık konut** | Mahremiyet ve denetim kaybı, uyku, çatışma | Oda başına kişi ↔ çocukta psikolojik sağlık (iki örneklem) [D] | D | Ulusal (SILC), il (oda başına kişi 2021) |
| 5 | **İşe gidiş süresi** | Zaman yoksulluğu, öngörülemezlik, hareketsizlik | Toplu taşımada > 60 dk → sağlık şikâyeti OR **1,2–1,6** [D] | B | Ulusal (ZKA 2014–15), 11 il (TomTom) |
| 6 | **Yeşil eksikliği** | Stres onarımı, dikkat yenilenmesi, serinlik, hareket | 0,1 NDVI → ölüm HR **0,96**; ≥ %30 ağaç → yeni psikolojik sıkıntı OR **0,69** [D] | MA | İlçe (WorldCover) |
| 7 | **Gece ışığı** | Melatonin baskılanması, sirkadiyen ritim | Yatak odası ≥ 5 lüks → depresif belirti HR **1,89** [D] | D | Ulusal (Falchi 2016) |
| 8 | **Yalnızlık** | Tehdit uyanıklığı, uyku, iltihap | Sosyal izolasyon → ölüm **1,32**; yalnızlık **1,14** [D] | MA | İl vekili (tek kişilik hane), ulusal anket |
| 9 | **Suç korkusu** | Kronik tetikte olma, dışarı çıkmama | Yüksek korku → depresyon **1,93** kat [D] | B | Ulusal (YMA 2017), il (İLYE 2015) |
| 10 | **Konut maliyet yükü** | Mali gerginlik, ödünleşimler, taşınma | Karşılanamaz konuta geçiş → ruh sağlığı puanı **−1,19** [D] | D | Ulusal (SILC), il (fiyat/gelir 2024) |
| 11 | **Yükseklik ve yoğunluk** | Komşuluk ve çocuk gözetimi kaybı, kalabalık | Yoğunluk → şizofreni OR 1,10, kardeşler arasında **1,02** (anlamsız) [D] | D | İlçe (GHSL) |
| 12 | **Gün ışığı eksikliği** | Sirkadiyen ritim, duygudurum | Yetersiz doğal ışık → depresyon **1,4** kat [D] | B | Ulusal (SILC) |
| 13 | **Görsel tekdüzelik** | Can sıkıntısı, uyarılma, onarım eksikliği | Can sıkıntısında kalp hızı ve kortizol artışı (laboratuvar) [D] | Ö | Ölçüm yok |

---

## 0. Ortak mekanizma: kronik stres yanıtı

Şehirdeki etkenlerin çoğu aynı son yola çıkıyor: vücudun stres sistemlerinin uzun süre açık kalması.

- **Allostatik yük.** McEwen (1998), stres hormonlarının kısa vadede koruyucu, uzun vadede yıpratıcı olduğunu savunur. Bu yıpranmaya "allostatik yük" der [İ, TLDR].
- **İki eksen.** Psikolojik stres hipotalamus-hipofiz-böbreküstü ekseniyle (kortizol) ve sempatik sinir sistemiyle yürür. Kronik stres koroner kalp hastalığını öngörür. Yalnızlık ve iş stresi de ilk kalp olayının riskini artırır (Steptoe ve Kivimäki 2012) [D].
- **Beyinden damara.** Amigdalanın dinlenme aktivitesi 3,7 yıllık izlemde kalp-damar olaylarını öngörüyor: standart sapma başına HR **1,59** (1,27–1,98). Yol, kemik iliği aktivitesi ve arter iltihabından geçiyor. Örneklem küçük: 293 kişi, 22 olay (Tawakol ve ark. 2017) [D].
- **Şehir ve beyin.** Şehirde yaşamak, sosyal stres altında amigdala aktivitesini artırıyor. Şehirde büyümek ise amigdalayı düzenleyen ön singulat bölgeyi etkiliyor (Lederbogen ve ark. 2011, fMRI) [D].
- **Şehir ve ruh sağlığı.** 20 nüfus taramasının meta-analizinde şehir/kır farkı toplam ruhsal bozuklukta, duygudurum ve kaygı bozukluklarında anlamlı. Madde kullanımında anlamlı değil. Karıştırıcıların düzeltilmesi farkı az değiştiriyor (Peen ve ark. 2010) [D]. Toplam OR 1,38, düzeltilmiş 1,21 [D·k].

---

## 1. Gürültü

**Mekanizma.**
- Gece gürültüsü uykuyu bölüyor ve kısaltıyor. Stres hormonlarını ve damar ile beyindeki oksidatif stresi artırıyor. Bunlar damar işlev bozukluğu, iltihap ve hipertansiyona yol açıyor (Münzel ve ark. 2021) [D].
- 498 kişilik bir PET çalışmasında 24 saatlik ulaşım gürültüsü +5 dBA arttıkça şunlar ölçüldü (Osborne ve ark. 2020) [D]:
  - majör kalp-damar olayı HR **1,34** (1,15–1,57),
  - daha yüksek amigdala aktivitesi,
  - daha yüksek arter iltihabı.
  - Bu iki aracı ilişkinin %12–26'sını açıklıyor.

**DSÖ 2018 Avrupa gürültü kılavuzu.**
- Önerilen üst sınırlar: karayolu **Lden 53 dB, Lnight 45 dB**; demiryolu 54 / 44; uçak 45 / 40. Bu üç öneri "güçlü" derecede [İ]. Değerler birincil belgeden okunamadı (WHO IRIS erişimi 403). İkincil özetlerden alındı: WBM Acoustics (2018), ISGlobal, İrlanda EPA.
- Kılavuz, sistematik derlemelere dayanır ve kanıtı GRADE yöntemiyle derecelendirir (Jarosińska ve ark. 2018) [D].

**Etki büyüklükleri (DSÖ için yapılan derlemeler ve sonrası).**

| Sonuç | Etki (10 dB başına) | Kanıt kalitesi | Kaynak |
|---|---|---|---|
| İskemik kalp hastalığı insidansı, karayolu | RR **1,08** (1,01–1,15), 7 boylamsal çalışma | Yüksek | van Kempen ve ark. 2018 [D] |
| "Uykusu çok bozulan" payı, Lnight (soru gürültüye atıf yaptığında) | Karayolu OR **2,13** (1,82–2,48); demiryolu 3,06; uçak 1,94 | Orta | Basner ve McGuire 2018 [D] |
| Aynı, soru gürültüyü anmadığında | Karayolu OR 1,09 (0,94–1,27), anlamsız | — | aynı [D] |
| Gece uyanma olasılığı, iç mekân Lmax | Karayolu OR **1,36** (1,19–1,55) | Orta | aynı [D] |
| Rahatsızlık (%HA) | Doz-yanıt ilişkileri; yeni çalışmalarda aynı dB'de daha çok rahatsızlık | Orta–yüksek | Guski ve ark. 2017 [D] |
| Depresyon, uçak | ES **1,12** (1,02–1,23) | — | Hegewald ve ark. 2020 [D] |
| Depresyon, karayolu ve demiryolu | +%2–3, anlamsız | — | aynı [D] |
| Depresyon / kaygı, karayolu | OR 1,04 (0,97–1,11) / 1,12 (0,96–1,30), anlamsız | Çok düşük | Dzhambov ve Lercher 2019 [D] |

**Okuma.**
- Gürültünün **uyku ve kalp** üzerindeki etkisi sağlam.
- **Ruh sağlığı** üzerindeki etkisi zayıf ve belirsiz. DSÖ derlemesindeki çalışmaların %90'ı kesitsel; kanıt çoğunlukla "çok düşük" kalitede (Clark ve Paunovic 2018) [D].
- Münzel ve ark. (2021), DSÖ'ye atıfla Batı Avrupa'da trafik gürültüsü yüzünden yılda en az 1,6 milyon sağlıklı yaşam yılı kaybedildiğini aktarıyor [D].

---

## 2. Hava kirliliği

**Mekanizma.** İnce partiküller akciğerden sistemik iltihap başlatıyor. Bir kısmı beyne ulaşıyor. Beyinde mikroglia hücrelerini etkinleştiriyor ve kan-beyin bariyerini bozuyor. Sonuç süreğen nöroinflamasyon ve oksidatif stres (Block ve Calderón-Garcidueñas 2009) [D].

**Etki büyüklükleri.**
- **Ölüm:** PM2.5 +10 µg/m³ → doğal nedenli ölüm RR **1,08** (1,06–1,09) [D].
  - 107 çalışma; DSÖ 2021 kılavuzunun dayanağı.
  - İlişki 10 µg/m³'ün altında da sürüyor.
  - Kanıt kesinliği "yüksek" (Chen ve Hoek 2020).
- **Depresyon:**
  - Uzun dönem PM2.5 +10 µg/m³ → OR **1,102** (1,023–1,189); 5 çalışma, I² = %0 (Braithwaite ve ark. 2019) [D].
  - Güncellenmiş meta-analizde RR **1,074** (1,021–1,129). Yayın yanlılığı yok, heterojenlik yok (Borroni ve ark. 2022) [D].
- **İntihar:** Kısa dönem PM10 ile intihar arasında 0–2 günlük gecikmede anlamlı ilişki var (Braithwaite ve ark. 2019) [D].

**Sınır değerler.**
- DSÖ 2021 yıllık PM2.5 kılavuz değeri 5 µg/m³; ara hedefler 35, 25, 15 ve 10 [İ].
- AB'de bugünkü sınır 25 µg/m³ (2008/50/AT). 2030'dan itibaren 10 µg/m³ (2024/2881 sayılı direktif) [İ].

**Bu projede.** Rapor 13'te 973 ilçede, il içinde PM2.5 +10 µg/m³ başına standartlaştırılmış ölüm oranı (SMR) +0,042 (≈ %4) çıktı [H]. Bu değer Chen ve Hoek'in %8'inin yarısı. Ekolojik bir tahmin için tutarlı bir büyüklük.

---

## 3. Isı

**Mekanizma.**
- Gece sıcaklığı uykuyu kısaltıyor. 765 bin kişilik ABD verisinde gece sıcaklığı arttıkça "yetersiz uyku" geceleri artıyor. Etki yazın, düşük gelirlilerde ve yaşlılarda en büyük (Obradovich ve ark. 2017) [D].
- Minor ve ark. (2022) aynı bulguyu dünya ölçeğinde giyilebilir cihaz verisiyle gösteriyor. Sayılar okunamadı [DY].

**Etki büyüklükleri.**
- **Ruh sağlığı:** +1 °C → ruh sağlığı nedenli ölüm RR **1,022** (1,015–1,029), başvuru ve yatış RR **1,009** (1,007–1,015). 53 çalışma; tropik bölgelerde ve 65 yaş üstünde daha güçlü (Liu ve ark. 2021) [D].
- **İntihar:**
  - Aylık ortalama sıcaklık +1 °C → intihar **+%1,5** (0,8–2,2) (Thompson ve ark. 2023) [D].
  - Günlük ortalama sıcaklık +1 °C → **+%1,7** (0,3–3,0) (aynı) [D].
- **Sıcak hava dalgası:** Ruh sağlığı başvuru ve yatışlarında **+%9,7** (7,6–11,9) (aynı) [D].
- **İlk derleme:** 15 çalışmada intihar riski 1 °C başına %1,4 ile %37 arasında artıyor (Thompson ve ark. 2018) [D].
- **Burke ve ark. (2018):** ABD ve Meksika'da sıcaklık–intihar ilişkisini gösteriyor. Sayılar okunamadı [DY].

**Şehir ısısı ve ağaç.**
- 93 Avrupa kentinde 2015 yazında kentsel ısı adası, nüfus ağırlıklı **+1,5 °C** (Iungman ve ark. 2023) [D].
- Yaz ölümlerinin **%4,33'ü** (6.700 erken ölüm) ısı adasına bağlanıyor (aynı) [D].
- Ağaç örtüsü **%30'a** çıkarılırsa kentler ortalama 0,4 °C serinliyor. **2.644 ölüm** önleniyor; bu, yaz ölümlerinin %1,84'ü (aynı) [D].

---

## 4. Kalabalık konut

**Mekanizma.** Kalabalık, mahremiyeti ve "kendi ortamını denetleme" duygusunu azaltır. Uyku, çalışma ve dinlenme alanı daralır; aile içi çatışma artar.

**Kanıt.**
- **Psikolojik sıkıntı:** Oda başına kişi sayısı ve yüksek dış gürültü sıkıntıyı artırıyor, ama ağır ruhsal hastalık üretmiyor (Evans 2003, derleme) [D].
- **Çocuklar:** Yoksul ailelerde oda başına kişi arttıkça çocukların psikolojik sağlığı kötüleşiyor. İki bağımsız örneklem var; kalabalık evdeki çocuklar zor görevde daha çabuk vazgeçiyor (Evans, Saegert ve Harris 2001) [D].
- **Kalabalıkta yalnızlık:** 756 kişinin 16.602 anlık ölçümünde kalabalık ve yoğunluk anlık yalnızlığı artırıyor. Doğa teması ve sosyal kapsayıcılık azaltıyor (Hammoud ve ark. 2021) [D].
- **Boylamsal kanıt:** Kalabalık, konut dezavantajının ruh sağlığını etkileyen boyutlarından biri (Singh ve ark. 2019; §10) [D].
- **Gove ve ark. (1979):** Klasik ev içi kalabalık çalışması. Ayrıntılı bulgu okunamadı [DY].

**Düzey:** D. Doz-yanıt meta-analizi bulunamadı.

---

## 5. İşe gidiş süresi

**Mekanizma.** Uzun yolculuk boş zamanı ve aile zamanını yer. Sıkışıklık, kalabalık ve öngörülemezlik yolculuk sırasında stres yaratır. Araçta geçen süre hareketsizliktir.

**Kanıt.**
- **İşe gidiş paradoksu:** Alman panelinde (GSOEP) işe gidiş süresi uzun olanların öznel iyi oluşu sistematik olarak daha düşük (Stutzer ve Frey 2008) [D].
  - Tek yön 22 dakikanın tam telafisi ayda yaklaşık 470 €. Bu, ortalama aylık iş gelirinin %35,4'ü [D·k].
- **İngiltere paneli (BHPS, sabit etkiler):** Uzun işe gidiş öznel sağlığı düşürüyor ve pratisyen hekim ziyaretini artırıyor (Künn-Nelen 2016) [D].
  - Nesnel sağlık ve sağlık davranışı neredeyse etkilenmiyor.
  - Kadınlarda egzersiz azalıyor, hastalık izni artıyor.
- **İngiltere, 26 bin çalışan:** Uzun işe gidiş iş ve boş zaman memnuniyetini düşürüyor, gerginliği artırıyor, ruh sağlığı puanını (GHQ-12) kötüleştiriyor (Clark ve ark. 2020) [D].
  - Genel yaşam memnuniyeti ise etkilenmiyor. Yalnız altı dalga boyunca uzun yolculuğu sürdürenlerde düşüyor.
  - Yürüyerek işe gidenlerde boş zaman memnuniyeti yüksek, gerginlik düşük.
- **İsveç, 21.088 kişi:** Toplu taşımayla 60 dakikadan uzun yolculukta uyku, stres, ruh sağlığı ve öz-bildirimli sağlık şikâyetleri için OR 1,2–1,6 (Hansson ve ark. 2011, kesitsel) [D].
- **Aile:** İsveç'te uzun mesafe işe gidiş yapan çiftlerin ayrılma oranı daha yüksek (Sandow 2014) [D].
- **Derleme:** Yolculuk sırasında ruh hali günün diğer işlerinden düşük. Memnuniyet süre uzadıkça her ulaşım türünde düşüyor. Yürüyen ve bisiklet kullananlar en memnun, toplu taşıma kullananlar en az memnun. Uzun yolculuk ile genel yaşam memnuniyeti arasında tutarlı bir bağ kurulamamış (Chatterjee ve ark. 2020) [D].

**Okuma.** İşe gidişin bedeli genel mutlulukta değil; **zaman, gerginlik ve boş zamanda** ödeniyor. Kısa ve yürünebilir yolculuk bunları geri veriyor.

---

## 6. Yeşil eksikliği

**Mekanizma.** İki kuram öne çıkıyor:
- **Stres azaltma kuramı:** Doğal sahne fizyolojik toparlanmayı hızlandırır (Ulrich ve ark. 1991) [D·k].
- **Dikkat restorasyon kuramı:** Doğa, zahmetsiz ilgiyle yorgun dikkati dinlendirir (Kaplan ve Kaplan 1989) [D·k].

Bunlara ek olarak ağaç gölgesi serinlik sağlar (§3), yeşil alan hareketi ve buluşmayı kolaylaştırır.

**Etki büyüklükleri.**

| Sonuç | Etki | Kaynak |
|---|---|---|
| Tüm nedenli ölüm | 500 m içinde +0,1 NDVI → HR **0,96** (0,94–0,97); 8,3 milyon kişi, I² %95 | Rojas-Rueda ve ark. 2019 [D] |
| Biyobelirteçler | Tükürük kortizolü −0,05; kalp hızı −2,57; diyastolik tansiyon −1,97 | Twohig-Bennett ve Jones 2018 [D] |
| Hastalık | Tip 2 diyabet OR 0,72; tüm nedenli ölüm 0,69; kalp-damar ölümü 0,84 | aynı [D] (çalışma kalitesi düşük, heterojenlik yüksek) |
| Depresyon | Yeşil payı +%10 → OR **0,963** (0,948–0,979); +0,1 NDVI → 0,931 (0,887–0,977) | Liu ve ark. 2023 [D] |
| Kaygı | Yeşil payı +%10 → OR 0,938 (0,858–1,025), anlamsız | aynı [D] |
| Çocuklukta yeşil | En az yeşilde büyüyenlerde sonraki psikiyatrik bozukluk riski **%55'e kadar** yüksek; ~1 milyon kişi, Danimarka | Engemann ve ark. 2019 [D] |
| Ağaç ile çim farkı | ≥ %30 ağaç örtüsü (%0–9'a göre) → yeni psikolojik sıkıntı OR **0,69** (0,54–0,88). ≥ %30 çim ise *yüksek* sıkıntıyla ilişkili (OR 1,71) | Astell-Burt ve Feng 2019 [D] |
| Doz | 20–30 dakikalık doğa teması tükürük kortizolünü saatte ek **%21,3** düşürüyor | Hunter ve ark. 2019 [D] |
| Deney | Boş arsaları yeşillendirmek komşularda "depresif hissetme"yi **−%41,5** (−63,6; −5,9) azaltıyor; yoksulluk sınırı altındaki mahallelerde −%68,7. Randomize küme deneyi | South ve ark. 2018 [D] |

**Kanıtın sınırı.** Gascon ve ark. (2015), çevre yeşilliği ile yetişkin ruh sağlığı arasında nedensel ilişki için "sınırlı", çocuklar için "yetersiz" kanıt buluyor [D].

**Hedef kuralı.** 3–30–300 kuralı: her evden en az 3 ağaç görünsün, her mahallede ağaç örtüsü en az %30 olsun, en yakın kamusal yeşil 300 m'den uzak olmasın (Konijnendijk 2023) [D]. Model mahallenin %30 ağaç hedefi (Rapor 13) bu kuralla ve Iungman ile Astell-Burt'un %30 eşiğiyle örtüşüyor.

---

## 7. Gece ışığı

**Mekanizma.** Gece ışığı melatonini baskılar ve iç saati kaydırır. Sonuçları uyku kaybı, duygudurum bozukluğu ve metabolik bozulmadır.

**Kanıt.**
- **Yatak odası ışığı:** Ortalama ≥ 5 lüks olan yaşlılarda depresif belirti riski HR **1,89** (1,13–3,14). Uyku ve hastalık düzeltmesiyle 1,72. Japonya'da 863 kişi, ışık cihazla ölçüldü (Obayashi ve ark. 2018) [D].
- **Dış ışık, ergenler:** Uydu ölçümünde en aydınlık çeyrekte yaşayan ergenler (Paksarian ve ark. 2020) [D]:
  - 29 dakika geç yatıyor ve 11 dakika az uyuyor.
  - Duygudurum bozukluğu OR 1,07; kaygı bozukluğu OR 1,10 (dış ışıkta bir medyan mutlak sapma başına).
- **Dış ışık, Kore:** En aydınlık bölgede depresif belirti OR **1,29** (1,15–1,46), intihar davranışı OR 1,27 (1,16–1,39). 113 bin kişi, kesitsel (Min ve Min 2018) [D].
- **Derleme:** 9 çalışmada depresif belirtilerle ilişki için orta düzey kanıt var. Gelir, gürültü ve hava kirliliği karıştırıcı olabilir (Tancredi ve ark. 2022) [D].
- **Kilo:** Meta-analizde gece ışığı fazla kiloyla (OR 1,13; 1,10–1,16) ve obeziteyle (OR 1,22; 1,07–1,38) ilişkili (Lai ve ark. 2020) [D].

**Türkiye.** Nüfusun **%97,8'i** ışık kirli gökyüzü altında yaşıyor. **%49,9'u** Samanyolu'nu göremiyor. **%24,3'ü** gözün karanlığa uyum sağlayamadığı parlaklıkta (>3.000 µcd/m²) yaşıyor (Falchi ve ark. 2016, Tablo 2; 2015 uydu verisi) [D].

---

## 8. Yalnızlık ve sosyal kopukluk

**Mekanizma.** Yalnızlık, sosyal tehdide karşı süreğen bir tetikte olma hali yaratıyor. Bu hal uyku kalitesini düşürüyor, fizyolojiyi bozuyor, hastalık ve ölümü artırıyor (Hawkley ve Cacioppo 2010) [D].

**Etki büyüklükleri.**
- **Sosyal ilişki:** Güçlü sosyal ilişkisi olanlarda hayatta kalma olasılığı **%50** yüksek; OR 1,50 (1,42–1,59), 148 çalışma (Holt-Lunstad ve ark. 2010) [D].
  - "Yalnız yaşıyor / yaşamıyor" gibi kaba ölçüyle ilişki zayıf: OR 1,19 (0,99–1,44) (aynı) [D].
- **Ölüm, ilk meta-analiz:** Sosyal izolasyon OR **1,29**, yalnızlık **1,26**, yalnız yaşamak **1,32** (Holt-Lunstad ve ark. 2015) [D].
- **Ölüm, en büyük meta-analiz:** 90 kohort, 2,2 milyon kişi (Wang ve ark. 2023) [D]:
  - Sosyal izolasyon tüm nedenli ölüm **1,32** (1,26–1,39).
  - Yalnızlık **1,14** (1,08–1,20).
  - İzolasyon kalp-damar ölümü **1,34**.
- **Kalp ve inme:** Zayıf sosyal ilişki koroner kalp hastalığı riski RR **1,29** (1,04–1,59), inme RR **1,32** (1,04–1,68) (Valtorta ve ark. 2016) [D].
- **Depresyon:** 88 çalışma ve 40.068 kişilik meta-analizde yalnızlığın depresyona orta düzeyde anlamlı etkisi var (Erzen ve Çikrikci 2018; Türk yazarlar) [D].

**Okuma.** Tek kişilik hane yalnızlığın kaba bir vekilidir. Asıl risk taşıyan şey **algılanan yalnızlık ve sosyal izolasyon**.

---

## 9. Suç ve suç korkusu

**Mekanizma.** Suç korkusu sürekli tetikte olma yaratır. İnsanlar dışarı çıkmayı, yürümeyi ve komşuyla görüşmeyi azaltır. Etki büyük ölçüde bu kısıtlanma üzerinden gelir.

**Kanıt.**
- **Whitehall II (Londra, 10 bin+ memur):** Suç korkusu yüksek olanlarda depresyon **1,93** (1,55–2,41) kat. Ruh sağlığı puanı 0,9 puan daha düşük (Stafford ve ark. 2007) [D].
  - Bu kişiler daha az egzersiz yapıyor, arkadaşlarını daha az görüyor.
  - Kısıtlanan fiziksel ve sosyal etkinlik, korku ile sağlık arasındaki bağı kısmen açıklıyor.
- **Haritalama derlemesi:** Suç ve korkunun iyi oluşa etkisi çoğunlukla dolaylı ve çevre üzerinden geliyor (Lorenc ve ark. 2012) [D].
  - Uyarı: suç önleme müdahaleleri farkındalığı artırıp korkuyu yükseltebilir.
- **Sokak aydınlatması:** 13 değerlendirmenin meta-analizinde iyileştirilmiş aydınlatma suçu anlamlı azaltıyor (Welsh ve Farrington 2008) [D].
  - Gece suçları gündüzden fazla azalmıyor. Yazarlara göre etki, gözetimden çok "mahallenin sahiplenilmesi" ve enformel denetim üzerinden geliyor.
  - Yüzde etki okunamadı [DY].
- **Randomize deneyler:**
  - Chalfin ve ark. (2022) New York'ta sokak aydınlatmasını deneyle sınıyor. Sayılar okunamadı [DY].
  - Philadelphia'da boş arsaların onarılması, yoksul mahallelerde silahlı şiddeti **−%29,1**, suç algısını **−%36,8**, dışarı çıkarken güvenlik kaygısını **−%57,8** azaltıyor. Dışarıyı dinlenme ve buluşma için kullanma +%75,7 (Branas ve ark. 2018) [D].

**Düzey:** B (boylamsal ve deneysel). Suç korkusu–ruh sağlığı için meta-analiz bulunamadı.

---

## 10. Konut maliyet yükü

**Mekanizma.** Gelirin büyük kısmı konuta gidince yiyecek, sağlık ve dinlenmeden kısılır. Borç ve tahliye kaygısı oluşur, sık taşınma sosyal bağı koparır.

**Kanıt.**
- **Avustralya paneli (HILDA, sabit etkiler):** Düşük ve orta gelirli hanelerde konut giderinin gelirin %30'unu aşmasına geçiş, ruh sağlığı puanında **−1,19** (−1,97; −0,41) düşüşle ilişkili (Bentley ve ark. 2011) [D].
  - Yüksek gelirlilerde ilişki yok.
- **Philadelphia, 10 bin kişi:** Karşılanamaz konutta yaşayanlarda (Pollack ve ark. 2010) [D]:
  - kötü öz-bildirimli sağlık AOR **1,75** (1,33–2,29),
  - hipertansiyon AOR **1,34** (1,07–1,69),
  - maliyet yüzünden tedaviyi aksatma AOR 2,94.
  - Psikiyatrik durumlarla anlamlı ilişki yok. Kiracılarda ilişkiler daha güçlü.
- **Sistematik derleme:** 12 boylamsal çalışmanın hepsinde en az bir konut dezavantajı ölçüsü sonraki ruh sağlığı sorunuyla ilişkili (Singh ve ark. 2019) [D].
  - Ölçüler: kalabalık, ipotek gecikmesi, sık taşınma, mülkiyet durumu, tahliye.
- **Haciz krizi:** Haciz yaşamak ve hacizli konutların yakınında oturmak kaygı ve şiddet davranışıyla ilişkili (Downing 2016) [D].

---

## 11. Yükseklik ve yoğunluk

**Mekanizma.**
- Çok katlı konutta çocuğun sokakla teması ve ebeveyn gözetimi zorlaşıyor.
- Merdiven ve asansör gibi ortak alanlar tanışıklık üretmiyor.
- Yoğunluk kalabalık ve gürültü duygusunu artırabiliyor.

**Kanıt.**
- **Derleme:** Yüksek katlı konut küçük çocuklu kadınların psikolojik iyi oluşu için olumsuz (Evans 2003) [D].
- **Gifford (2007):** Yüksek kat çocuklar için uygun görülmüyor. Yardımlaşma ve arkadaşlık daha az, korku ve suç daha fazla. Ama kimin yüksek katta oturduğu, yani seçilim, önemli [D·k].
- **Barros ve ark. (2019):** 23 çalışmalık sistematik derleme. Konut tipi, kat düzeyi ve ortak merdiven gibi alanlar sosyal iyi oluş ve ruh sağlığıyla ilişkili. Ancak kavramsal boşluk ve yöntem tutarsızlığı çok [D].
- **Kalantari ve Shepley (2021):** Bazı olumsuz psikolojik ve sosyal etkiler tutarlı biçimde tekrarlıyor, en çok düşük gelirlilerde. Tasarımla azaltılabiliyor [D].
- **Seçilim ve aile etkisi:** İsveç'te 2,4 milyon kişide nüfus yoğunluğu şizofreniyi öngörüyor: OR **1,10** (1,09–1,11) (Sariaslan ve ark. 2015) [D].
  - Kuzenler karşılaştırılınca 1,06'ya iniyor.
  - Kardeşler arasında 1,02'ye (0,97–1,08) iniyor ve anlamsızlaşıyor.
  - Depresyonda da benzer sonuç var. Yoğunluğun "etkisi" büyük ölçüde ailesel seçilim.
- **Fanning (1967):** Yeni apartman bloklarında oturan ailelerin sağlığının, eski evlerde oturanlardan kötü olduğunu bildiriyor [İ, TLDR]. Oranlar okunamadı [DY].

**Bu projede.** Faz 2'de kat başına SMR'de ≈ +%2,5 bulunmuştu. Rapor 13'te PM2.5, yüzey sıcaklığı ve ağaç kontrolüyle bu ilişki %0,85'e indi ve anlamsızlaştı (p = 0,15) [H]. Yüksekliğin sağlık bedeli çoğunlukla **onunla birlikte gelen** kirli hava ve ağaçsızlıktan geçiyor.

---

## 12. Gün ışığı eksikliği

**Mekanizma.** Gündüz parlak ışık iç saati ayarlıyor, gece melatoninini güçlendiriyor ve duygudurumu destekliyor. Karanlık konut ve gün boyu kapalı mekân bu sinyali zayıflatıyor.

**Kanıt.**
- **Derleme:** Yetersiz gün ışığı depresif belirtilerle güvenilir biçimde ilişkili (Evans 2003) [D].
- **Sekiz Avrupa kenti (LARES, 6.017 kişi):** Evini yetersiz aydınlık bulanlarda (Brown ve Jacobs 2011) [D]:
  - depresyon **1,4** (1,2–1,7) kat,
  - düşme 1,5 kat (düzeltmeyle 2,5).
- **UK Biobank (400 bin+ kişi):** Gün ışığında dışarıda geçen her ek saat şunlarla ilişkili (Burns ve ark. 2021) [D]:
  - majör depresyon OR 0,92–0,98 (güven aralığı),
  - antidepresan kullanımı 0,92–0,98,
  - uykusuzluk belirtisi 0,94–0,97.
  - Boylamsal modeller de aynı yönde, ama etkiler daha küçük.
- **Cihazla ölçüm (85 bin+ kişi):** Gece ışığından bağımsız olarak gündüz daha çok ışık alanlarda majör depresyon, TSSB, psikoz ve kendine zarar riski daha düşük (Burns ve ark. 2023) [İ, TLDR].
- **Tedavi:** Parlak ışık tedavisi mevsimsel depresyonda etkili; standartlaştırılmış ortalama fark −0,37 (−0,63; −0,12). 19 randomize deney (Pjrek ve ark. 2020) [D].

---

## 13. Görsel tekdüzelik

**Mekanizma (önerilen).** Uzun, boş ve tekrar eden cepheler yürüyene uyarı vermez. Bu durum can sıkıntısı ve dikkatin dağılmasıyla sonuçlanır. Çeşitli ve ayrıntılı cephe ise "zahmetsiz ilgi" ve onarım sağlar (dikkat restorasyonu kuramıyla uyumlu).

**Kanıt.**
- **Laboratuvar:** Can sıkıntısı hissettiren videolar izleyen 72 öğrencide üzüntüye göre kalp hızı ve kortizol daha yüksek. Yani can sıkıntısı edilgen değil, uyarılmış bir stres hali (Merrifield ve Danckert 2014) [D].
- **Sokak görüntüsü:** Lindal ve Hartig (2013), mimari çeşitlilik ve bina yüksekliğinin konut sokaklarının "onarıcılık" algısına etkisini deneysel olarak sınıyor. Özet okunamadı; bulgu bu oturumda doğrulanmadı [DY].
- **Cephe tekdüzeliği ile sağlık sonucu arasında** kohort ya da meta-analiz bulunamadı. Kentsel tasarım literatürü (Gehl, Alexander; `kaynakca.csv`) güçlü gözlemler içeriyor, ama ölçülmüş sağlık sonucu yok.

**Düzey:** Ö. Bu etken tasarım için akla yatkın, ama kanıt bakımından en zayıf halka.

---

## Kanıt düzeyine göre sıralama (bu taramanın yargısı)

| Güç | Etkenler | Gerekçe |
|---|---|---|
| **Güçlü** (MA, sert sonuç, tutarlı) | Hava kirliliği, ısı, yalnızlık ve sosyal izolasyon, gürültünün uyku ve kalbe etkisi | Ölüm ya da kalp hastalığı için doz-yanıtlı meta-analizler; kesinlik yüksek ya da orta |
| **Orta** | Yeşil eksikliği, gece ışığı, gün ışığı, kalabalık, konut maliyeti, işe gidiş, suç korkusu | Boylamsal ve deneysel kanıt var. Ama ölçüler farklı, heterojenlik yüksek, meta-analiz az |
| **Zayıf ya da karışık** | Gürültünün ruh sağlığına etkisi, yükseklik ve yoğunluk, görsel tekdüzelik | Kesitsel ağırlıklı; seçilim ve karıştırıcılarla açıklanabiliyor |

**Proje için ders.** Ölçülebilir ve sağlıkla güçlü ilişkili etkenler (hava, ısı, ağaç, gürültü) aynı zamanda şehir tasarımıyla en doğrudan değiştirilebilenler. Toplumsal etkenler (yalnızlık, güvensizlik, konut yükü) güçlü ama mekânla bağları dolaylı.

---

## Kaynakça

Künyeler Crossref'ten üretildi (`stres_literatur_kunye.csv`). Ayrıca: DSÖ 2018 *Environmental Noise Guidelines for the European Region* (ISBN 978-92-890-5356-3; değerler ikincil özetlerden [İ]); DSÖ 2021 *Global Air Quality Guidelines* [İ]; Ulrich ve ark. 1991, Kaplan ve Kaplan 1989, Gehl, Alexander (`kaynakca.csv`).

**Ortak mekanizma**

- McEwen BS (1998). Protective and Damaging Effects of Stress Mediators. *New England Journal of Medicine* 338(3):171-179. https://doi.org/10.1056/NEJM199801153380307
- Lederbogen F, Kirsch P, Haddad L ve ark. (2011). City living and urban upbringing affect neural social stress processing in humans. *Nature* 474(7352):498-501. https://doi.org/10.1038/nature10190
- Tawakol A, Ishai A, Takx RA ve ark. (2017). Relation between resting amygdalar activity and cardiovascular events: a longitudinal and cohort study. *The Lancet* 389(10071):834-845. https://doi.org/10.1016/S0140-6736(16)31714-7
- Steptoe A, Kivimäki M (2012). Stress and cardiovascular disease. *Nature Reviews Cardiology* 9(6):360-370. https://doi.org/10.1038/nrcardio.2012.45
- Peen J, Schoevers RA, Beekman AT ve ark. (2010). The current status of urban-rural differences in psychiatric disorders. *Acta Psychiatrica Scandinavica* 121(2):84-93. https://doi.org/10.1111/j.1600-0447.2009.01438.x

**Gürültü**

- Jarosińska D, Héroux MÈ, Wilkhu P ve ark. (2018). Development of the WHO Environmental Noise Guidelines for the European Region: An Introduction. *IJERPH* 15(4):813. https://doi.org/10.3390/ijerph15040813
- van Kempen E, Casas M, Pershagen G ve ark. (2018). WHO Environmental Noise Guidelines for the European Region: A Systematic Review on Environmental Noise and Cardiovascular and Metabolic Effects: A Summary. *IJERPH* 15(2):379. https://doi.org/10.3390/ijerph15020379
- Basner M, McGuire S (2018). WHO Environmental Noise Guidelines for the European Region: A Systematic Review on Environmental Noise and Effects on Sleep. *IJERPH* 15(3):519. https://doi.org/10.3390/ijerph15030519
- Guski R, Schreckenberg D, Schuemer R (2017). WHO Environmental Noise Guidelines for the European Region: A Systematic Review on Environmental Noise and Annoyance. *IJERPH* 14(12):1539. https://doi.org/10.3390/ijerph14121539
- Clark C, Paunovic K (2018). WHO Environmental Noise Guidelines for the European Region: A Systematic Review on Environmental Noise and Quality of Life, Wellbeing and Mental Health. *IJERPH* 15(11):2400. https://doi.org/10.3390/ijerph15112400
- Hegewald J, Schubert M, Freiberg A ve ark. (2020). Traffic Noise and Mental Health: A Systematic Review and Meta-Analysis. *IJERPH* 17(17):6175. https://doi.org/10.3390/ijerph17176175
- Dzhambov AM, Lercher P (2019). Road Traffic Noise Exposure and Depression/Anxiety: An Updated Systematic Review and Meta-Analysis. *IJERPH* 16(21):4134. https://doi.org/10.3390/ijerph16214134
- Münzel T, Sørensen M, Daiber A (2021). Transportation noise pollution and cardiovascular disease. *Nature Reviews Cardiology* 18(9):619-636. https://doi.org/10.1038/s41569-021-00532-5
- Osborne MT, Radfar A, Hassan MZO ve ark. (2020). A neurobiological mechanism linking transportation noise to cardiovascular disease in humans. *European Heart Journal* 41(6):772-782. https://doi.org/10.1093/eurheartj/ehz820

**Hava kirliliği**

- Chen J, Hoek G (2020). Long-term exposure to PM and all-cause and cause-specific mortality: A systematic review and meta-analysis. *Environment International* 143:105974. https://doi.org/10.1016/j.envint.2020.105974
- Braithwaite I, Zhang S, Kirkbride JB ve ark. (2019). Air Pollution (Particulate Matter) Exposure and Associations with Depression, Anxiety, Bipolar, Psychosis and Suicide Risk: A Systematic Review and Meta-Analysis. *Environmental Health Perspectives* 127(12):126002. https://doi.org/10.1289/EHP4595
- Borroni E, Pesatori AC, Bollati V ve ark. (2022). Air pollution exposure and depression: A comprehensive updated systematic review and meta-analysis. *Environmental Pollution* 292:118245. https://doi.org/10.1016/j.envpol.2021.118245
- Block ML, Calderón-Garcidueñas L (2009). Air pollution: mechanisms of neuroinflammation and CNS disease. *Trends in Neurosciences* 32(9):506-516. https://doi.org/10.1016/j.tins.2009.05.009

**Isı**

- Liu J, Varghese BM, Hansen A ve ark. (2021). Is there an association between hot weather and poor mental health outcomes? A systematic review and meta-analysis. *Environment International* 153:106533. https://doi.org/10.1016/j.envint.2021.106533
- Thompson R, Hornigold R, Page L ve ark. (2018). Associations between high ambient temperatures and heat waves with mental health outcomes: a systematic review. *Public Health* 161:171-191. https://doi.org/10.1016/j.puhe.2018.06.008
- Thompson R, Lawrance EL, Roberts LF ve ark. (2023). Ambient temperature and mental health: a systematic review and meta-analysis. *The Lancet Planetary Health* 7(7):e580-e589. https://doi.org/10.1016/S2542-5196(23)00104-3
- Burke M, González F, Baylis P ve ark. (2018). Higher temperatures increase suicide rates in the United States and Mexico. *Nature Climate Change* 8(8):723-729. https://doi.org/10.1038/s41558-018-0222-x
- Iungman T, Cirach M, Marando F ve ark. (2023). Cooling cities through urban green infrastructure: a health impact assessment of European cities. *The Lancet* 401(10376):577-589. https://doi.org/10.1016/S0140-6736(22)02585-5
- Obradovich N, Migliorini R, Mednick SC ve ark. (2017). Nighttime temperature and human sleep loss in a changing climate. *Science Advances* 3(5):e1601555. https://doi.org/10.1126/sciadv.1601555
- Minor K, Bjerre-Nielsen A, Jonasdottir SS ve ark. (2022). Rising temperatures erode human sleep globally. *One Earth* 5(5):534-549. https://doi.org/10.1016/j.oneear.2022.04.008

**Kalabalık konut**

- Gove WR, Hughes M, Galle OR (1979). Overcrowding in the Home: An Empirical Investigation of Its Possible Pathological Consequences. *American Sociological Review* 44(1):59. https://doi.org/10.2307/2094818
- Evans GW (2003). The Built Environment and Mental Health. *Journal of Urban Health* 80(4):536-555. https://doi.org/10.1093/jurban/jtg063
- Evans GW, Saegert S, Harris R (2001). Residential Density and Psychological Health among Children in Low-Income Families. *Environment and Behavior* 33(2):165-180. https://doi.org/10.1177/00139160121972936
- Hammoud R, Tognin S, Bakolis I ve ark. (2021). Lonely in a crowd: investigating the association between overcrowding and loneliness using smartphone technologies. *Scientific Reports* 11(1):24134. https://doi.org/10.1038/s41598-021-03398-2

**İşe gidiş**

- Stutzer A, Frey BS (2008). Stress that Doesn't Pay: The Commuting Paradox. *Scandinavian Journal of Economics* 110(2):339-366. https://doi.org/10.1111/j.1467-9442.2008.00542.x
- Künn-Nelen A (2016). Does Commuting Affect Health? *Health Economics* 25(8):984-1004. https://doi.org/10.1002/hec.3199
- Chatterjee K, Chng S, Clark B ve ark. (2020). Commuting and wellbeing: a critical overview of the literature with implications for policy and future research. *Transport Reviews* 40(1):5-34. https://doi.org/10.1080/01441647.2019.1649317
- Clark B, Chatterjee K, Martin A ve ark. (2020). How commuting affects subjective wellbeing. *Transportation* 47(6):2777-2805. https://doi.org/10.1007/s11116-019-09983-9
- Sandow E (2014). Til Work Do Us Part: The Social Fallacy of Long-distance Commuting. *Urban Studies* 51(3):526-543. https://doi.org/10.1177/0042098013498280
- Hansson E, Mattisson K, Björk J ve ark. (2011). Relationship between commuting and health outcomes in a cross-sectional population survey in southern Sweden. *BMC Public Health* 11(1):834. https://doi.org/10.1186/1471-2458-11-834

**Yeşil eksikliği**

- Twohig-Bennett C, Jones A (2018). The health benefits of the great outdoors: A systematic review and meta-analysis of greenspace exposure and health outcomes. *Environmental Research* 166:628-637. https://doi.org/10.1016/j.envres.2018.06.030
- Rojas-Rueda D, Nieuwenhuijsen MJ, Gascon M ve ark. (2019). Green spaces and mortality: a systematic review and meta-analysis of cohort studies. *The Lancet Planetary Health* 3(11):e469-e477. https://doi.org/10.1016/S2542-5196(19)30215-3
- Engemann K, Pedersen CB, Arge L ve ark. (2019). Residential green space in childhood is associated with lower risk of psychiatric disorders from adolescence into adulthood. *PNAS* 116(11):5188-5193. https://doi.org/10.1073/pnas.1807504116
- Gascon M, Triguero-Mas M, Martínez D ve ark. (2015). Mental Health Benefits of Long-Term Exposure to Residential Green and Blue Spaces: A Systematic Review. *IJERPH* 12(4):4354-4379. https://doi.org/10.3390/ijerph120404354
- Astell-Burt T, Feng X (2019). Association of Urban Green Space With Mental Health and General Health Among Adults in Australia. *JAMA Network Open* 2(7):e198209. https://doi.org/10.1001/jamanetworkopen.2019.8209
- Hunter MR, Gillespie BW, Chen SYP (2019). Urban Nature Experiences Reduce Stress in the Context of Daily Life Based on Salivary Biomarkers. *Frontiers in Psychology* 10:722. https://doi.org/10.3389/fpsyg.2019.00722
- Konijnendijk CC (2023). Evidence-based guidelines for greener, healthier, more resilient neighbourhoods: Introducing the 3–30–300 rule. *Journal of Forestry Research* 34(3):821-830. https://doi.org/10.1007/s11676-022-01523-z
- Liu Z, Chen X, Cui H ve ark. (2023). Green space exposure on depression and anxiety outcomes: A meta-analysis. *Environmental Research* 231:116303. https://doi.org/10.1016/j.envres.2023.116303
- South EC, Hohl BC, Kondo MC ve ark. (2018). Effect of Greening Vacant Land on Mental Health of Community-Dwelling Adults. *JAMA Network Open* 1(3):e180298. https://doi.org/10.1001/jamanetworkopen.2018.0298
- Branas CC, South E, Kondo MC ve ark. (2018). Citywide cluster randomized trial to restore blighted vacant land and its effects on violence, crime, and fear. *PNAS* 115(12):2946-2951. https://doi.org/10.1073/pnas.1718503115

**Gece ışığı**

- Falchi F, Cinzano P, Duriscoe D ve ark. (2016). The new world atlas of artificial night sky brightness. *Science Advances* 2(6):e1600377. https://doi.org/10.1126/sciadv.1600377
- Paksarian D, Rudolph KE, Stapp EK ve ark. (2020). Association of Outdoor Artificial Light at Night With Mental Disorders and Sleep Patterns Among US Adolescents. *JAMA Psychiatry* 77(12):1266. https://doi.org/10.1001/jamapsychiatry.2020.1935
- Obayashi K, Saeki K, Kurumatani N (2018). Bedroom Light Exposure at Night and the Incidence of Depressive Symptoms: A Longitudinal Study of the HEIJO-KYO Cohort. *American Journal of Epidemiology* 187(3):427-434. https://doi.org/10.1093/aje/kwx290
- Min JY, Min KB (2018). Outdoor light at night and the prevalence of depressive symptoms and suicidal behaviors: A cross-sectional study in a nationally representative sample of Korean adults. *Journal of Affective Disorders* 227:199-205. https://doi.org/10.1016/j.jad.2017.10.039
- Tancredi S, Urbano T, Vinceti M ve ark. (2022). Artificial light at night and risk of mental disorders: A systematic review. *Science of the Total Environment* 833:155185. https://doi.org/10.1016/j.scitotenv.2022.155185
- Lai KY, Sarkar C, Ni MY ve ark. (2020). Exposure to light at night (LAN) and risk of obesity: A systematic review and meta-analysis of observational studies. *Environmental Research* 187:109637. https://doi.org/10.1016/j.envres.2020.109637

**Yalnızlık**

- Holt-Lunstad J, Smith TB, Layton JB (2010). Social Relationships and Mortality Risk: A Meta-analytic Review. *PLoS Medicine* 7(7):e1000316. https://doi.org/10.1371/journal.pmed.1000316
- Holt-Lunstad J, Smith TB, Baker M ve ark. (2015). Loneliness and Social Isolation as Risk Factors for Mortality. *Perspectives on Psychological Science* 10(2):227-237. https://doi.org/10.1177/1745691614568352
- Valtorta NK, Kanaan M, Gilbody S ve ark. (2016). Loneliness and social isolation as risk factors for coronary heart disease and stroke: systematic review and meta-analysis of longitudinal observational studies. *Heart* 102(13):1009-1016. https://doi.org/10.1136/heartjnl-2015-308790
- Wang F, Gao Y, Han Z ve ark. (2023). A systematic review and meta-analysis of 90 cohort studies of social isolation, loneliness and mortality. *Nature Human Behaviour* 7(8):1307-1319. https://doi.org/10.1038/s41562-023-01617-6
- Hawkley LC, Cacioppo JT (2010). Loneliness Matters: A Theoretical and Empirical Review of Consequences and Mechanisms. *Annals of Behavioral Medicine* 40(2):218-227. https://doi.org/10.1007/s12160-010-9210-8
- Erzen E, Çikrikci Ö (2018). The effect of loneliness on depression: A meta-analysis. *International Journal of Social Psychiatry* 64(5):427-435. https://doi.org/10.1177/0020764018776349

**Suç ve suç korkusu**

- Lorenc T, Clayton S, Neary D ve ark. (2012). Crime, fear of crime, environment, and mental health and wellbeing: Mapping review of theories and causal pathways. *Health & Place* 18(4):757-765. https://doi.org/10.1016/j.healthplace.2012.04.001
- Stafford M, Chandola T, Marmot M (2007). Association Between Fear of Crime and Mental Health and Physical Functioning. *American Journal of Public Health* 97(11):2076-2081. https://doi.org/10.2105/AJPH.2006.097154
- Chalfin A, Hansen B, Lerner J ve ark. (2022). Reducing Crime Through Environmental Design: Evidence from a Randomized Experiment of Street Lighting in New York City. *Journal of Quantitative Criminology* 38(1):127-157. https://doi.org/10.1007/s10940-020-09490-6
- Welsh BC, Farrington DP (2008). Effects of Improved Street Lighting on Crime. *Campbell Systematic Reviews* 4(1). https://doi.org/10.4073/csr.2008.13

**Konut maliyet yükü**

- Bentley R, Baker E, Mason K ve ark. (2011). Association Between Housing Affordability and Mental Health: A Longitudinal Analysis of a Nationally Representative Household Survey in Australia. *American Journal of Epidemiology* 174(7):753-760. https://doi.org/10.1093/aje/kwr161
- Singh A, Daniel L, Baker E ve ark. (2019). Housing Disadvantage and Poor Mental Health: A Systematic Review. *American Journal of Preventive Medicine* 57(2):262-272. https://doi.org/10.1016/j.amepre.2019.03.018
- Downing J (2016). The health effects of the foreclosure crisis and unaffordable housing: A systematic review and explanation of evidence. *Social Science & Medicine* 162:88-96. https://doi.org/10.1016/j.socscimed.2016.06.014
- Pollack CE, Griffin BA, Lynch J (2010). Housing Affordability and Health Among Homeowners and Renters. *American Journal of Preventive Medicine* 39(6):515-521. https://doi.org/10.1016/j.amepre.2010.08.002

**Yükseklik ve yoğunluk**

- Gifford R (2007). The Consequences of Living in High-Rise Buildings. *Architectural Science Review* 50(1):2-17. https://doi.org/10.3763/asre.2007.5002
- Kalantari S, Shepley M (2021). Psychological and social impacts of high-rise buildings: a review of the post-occupancy evaluation literature. *Housing Studies* 36(8):1147-1176. https://doi.org/10.1080/02673037.2020.1752630
- Barros P, Ng Fat L, Garcia LMT ve ark. (2019). Social consequences and mental health outcomes of living in high-rise residential buildings and the influence of planning, urban design and architectural decisions: A systematic review. *Cities* 93:263-272. https://doi.org/10.1016/j.cities.2019.05.015
- Sariaslan A, Larsson H, D'Onofrio B ve ark. (2015). Does Population Density and Neighborhood Deprivation Predict Schizophrenia? A Nationwide Swedish Family-Based Study of 2.4 Million Individuals. *Schizophrenia Bulletin* 41(2):494-502. https://doi.org/10.1093/schbul/sbu105
- Fanning DM (1967). Families in flats. *BMJ* 4(5576):382-386. https://doi.org/10.1136/bmj.4.5576.382

**Gün ışığı**

- Brown MJ, Jacobs DE (2011). Residential Light and Risk for Depression and Falls: Results from the LARES Study of Eight European Cities. *Public Health Reports* 126(Suppl 1):131-140. https://doi.org/10.1177/00333549111260S117
- Burns AC, Saxena R, Vetter C ve ark. (2021). Time spent in outdoor light is associated with mood, sleep, and circadian rhythm-related outcomes: A cross-sectional and longitudinal study in over 400,000 UK Biobank participants. *Journal of Affective Disorders* 295:347-352. https://doi.org/10.1016/j.jad.2021.08.056
- Burns AC, Windred DP, Rutter MK ve ark. (2023). Day and night light exposure are associated with psychiatric disorders: an objective light study in >85,000 people. *Nature Mental Health* 1(11):853-862. https://doi.org/10.1038/s44220-023-00135-8
- Pjrek E, Friedrich ME, Cambioli L ve ark. (2020). The Efficacy of Light Therapy in the Treatment of Seasonal Affective Disorder: A Meta-Analysis of Randomized Controlled Trials. *Psychotherapy and Psychosomatics* 89(1):17-24. https://doi.org/10.1159/000502891

**Görsel tekdüzelik**

- Lindal PJ, Hartig T (2013). Architectural variation, building height, and the restorative quality of urban residential streetscapes. *Journal of Environmental Psychology* 33:26-36. https://doi.org/10.1016/j.jenvp.2012.09.003
- Merrifield C, Danckert J (2014). Characterizing the psychophysiological signature of boredom. *Experimental Brain Research* 232(2):481-491. https://doi.org/10.1007/s00221-013-3755-2
