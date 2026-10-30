# Konut Biçimi ve Toplumsal Sonuçlar — Kanıt Taraması

*29 Ekim 2026 · Sürüm 0.1 · Faz 5 · Rapor 15'in ([09_RAPORLAR/15_fitrata_uygun_konut.md](../09_RAPORLAR/15_fitrata_uygun_konut.md)) ve stres taramasının ([stres_literatur.md](stres_literatur.md)) tamamlayıcısı*

| Ne | Nerede |
|---|---|
| Kaynakça (58 kaynak; tema, künye, DOI, tasarım, bulgu, etki büyüklüğü, kanıt düzeyi, doğrulama) | [konut_bicimi_kaynakca.csv](konut_bicimi_kaynakca.csv) |
| Künye, özet ve dize denetimi tablosu | `03_VERI/ham/konut_bicimi_literatur/kunye_ozet.csv` |
| Ham yanıtlar (Crossref, PubMed, Europe PMC, Semantic Scholar, OpenAlex) | `03_VERI/ham/konut_bicimi_literatur/` |
| Doğrulama kodu | `05_ANALIZ/kod/konut_bicimi_literatur_dogrula.py` |
| İlgili önceki taramalar | [stres_literatur.md](stres_literatur.md) §4 kalabalık, §11 yükseklik; [kaynakca.csv](kaynakca.csv) tema 4, 5, 8 |

---

## Yöntem

**Soru.** Konutun biçimi şu beş alandaki sonuçlarla nasıl ilişkili?

- Konut biçimi: yüksek ya da alçak apartman bloğu, müstakil ve sıra ev, konut büyüklüğü ve kalabalık (oda başına kişi), yoğunluk, sokak ağının bağlantılılığı, avlu ve bahçe, ev sahipliği ya da kira.
- Sonuçlar: (1) inovasyon ve üretkenlik, (2) sağlık, (3) toplumsal güven ve sosyal sermaye, (4) güvenlik ve suç, (5) aile ve çocuk.

**Kaynaklar nasıl seçildi?**
- Önceden bilinen künyeler (görevde verilen öncüller dahil) ve Europe PMC, Crossref, OpenAlex konu aramaları kullanıldı. Tarama sistematik değildir; seçim yanlılığı olabilir.
- Meta-analiz, sistematik derleme ve iyi tanımlanmış çalışmalar (doğal deney, randomize deney, panel, araç değişken) öne alındı.
- Projenin eğilimine ters düşen kanıt bilerek arandı: yoğunluğun verimlilik ve inovasyonu artırdığına, yüksek kattaki sağlık farkının seçilimden geldiğine, ev sahipliğinin faydasının küçük olduğuna dair çalışmalar.

**Nasıl doğrulandı?**
1. Her DOI Crossref'te açıldı. Künye (yazar, yıl, başlık, dergi, cilt, sayfa) oradan alındı. 58 kaynağın 57'sinin DOI'si var ve 57'si de bulundu. Oda ve ark. (1989) Crossref'te yok; künyesi PubMed'den.
2. Özet sırayla PubMed, Crossref, Europe PMC, Semantic Scholar ve OpenAlex'te arandı. PubMed kaydı başlıkla örtüşmüyorsa atıldı. Semantic Scholar'ın otomatik özetleri (TLDR) kabul edilmedi.
3. Her bulgunun ve sayının özetteki İngilizce ifadesi kodda "kanıt dizesi" olarak yazıldı. Kod bu dizelerin özette geçip geçmediğini denetledi. Etki büyüklüğü yalnız dize tuttuysa yazıldı.
4. Yayımlanmış sürümün özeti hiçbir serviste yoksa, aynı çalışmanın çalışma makalesi ya da yeniden basım sürümünün özeti kullanıldı. Bu bulgular en çok [K] sayıldı. Bir istisna var: Sandler (2017) için ICPSR veri deposu kaydı, yayımlanmış özeti künyesiyle aynen aktarıyor; bu yüzden [D].
5. Elsevier dergilerinin (ör. *Journal of Urban Economics*) özetleri açık servislerde çoğunlukla yok. Ekonomi kaynaklarında [K] oranının yüksek olmasının nedeni bu.
6. Semantic Scholar ve OpenAlex özetleri, yayımlanmış sürümün DOI'sine bağlı kayıttan alındı. Bu yüzden onlar da yayımlanmış özet sayıldı.
7. İstekler Python `urllib`'in varsayılan başlıklarıyla yapıldı. Tarayıcı taklidi yapılmadı, e-posta gönderilmedi.

**Sonuç.** 58 kaynağın 47'si [D], 11'i [K], hiçbiri [DY] değil. Özet kaynağı: PubMed 18, Crossref 16, Semantic Scholar 8, OpenAlex 6; 9 kaynakta çalışma makalesi ya da yeniden basım, 1 kaynakta veri deposu kaydı. Kanıt düzeyi: 10 G, 38 O, 10 Z.

**İşaretler.**
- **[D]** Bulgu ve sayı, kaynağın yayımlanmış özetinde görüldü; kod dize eşleşmesiyle denetledi.
- **[K]** Kısmen doğrulandı. Künye Crossref'te doğrulandı, ama bulgu ya da sayı yayımlanmış özette görülmedi. Ya çalışma makalesi ya da yeniden basım özetinde görüldü (tabloda belirtilir), ya da hiç görülmedi.
- **[DY]** Doğrulanmadı.
- **[H]** Bu projede hesaplandı (önceki raporlardan).

**Kanıt düzeyi.**
- **G (güçlü):** meta-analiz ya da nicel sentez, randomize deney, doğal deney ya da güvenilir araç değişken.
- **O (orta):** büyük boylamsal ya da panel çalışma, çok büyük kesitsel örneklemde zengin düzeltme, derlemeler.
- **Z (zayıf):** tek kentte ya da küçük örneklemde kesitsel ilişki, nitel ya da kuramsal çalışma.

Aksi yazılmadıkça etki büyüklükleri gözlemseldir ve nedensellik kanıtı sayılmamalıdır. En büyük karıştırıcı seçilimdir: kimin hangi tür konutta oturduğu rastgele değildir.

---

## Özet

En güçlü kanıttan başlayarak:

1. **Yoğunluk ve yakınlık verimliliği ve inovasyonu artırıyor. Bu, taramadaki en güçlü kanıt.**
   - 102 çalışmanın sentezi: yoğunluk %10 artınca kişi başı yıllık ücret 140 $ artıyor, ama kira 243 $ artıyor (Ahlfeldt ve Pietrostefani 2019) [D].
   - Berlin'in bölünmesi ve birleşmesi doğal deneyinde yığılma faydası büyük ve "çok yerel" (Ahlfeldt ve ark. 2015) [D].
   - Laboratuvarların asbest yüzünden yer değiştirmesi doğal deneyinde yan yana olmak ortak araştırma olasılığını **3,5 kat** artırıyor (Catalini 2018) [D].
2. **Faydayı taşıyan yükseklik değil, yürüme ölçeğindeki yakınlık ve sık sokak ağı.**
   - Manhattan'da komşu firmaların faydası mesafeyle "son derece hızlı" sönüyor (Arzaghi ve Henderson 2008) [D].
   - Sokak ağı yoğunluğu bölgeler arası inovasyon farkını açıklıyor (Roche 2020, araç değişken) [D].
   - Yürüme en çok kavşak yoğunluğu ve karma kullanımla ilişkili; nüfus yoğunluğu bunlar denetlenince zayıf (Ewing ve Cervero 2010, meta-analiz) [D].
   - Yüksekliğin verimlilik primi ofis binaları için gösterildi: bir kat yukarı çıkmak, posta koduna ≈3.500 çalışan eklemekle aynı kira etkisini yapıyor (Liu ve ark. 2018) [D]. Konut kulesi için benzer bir kanıt bulunamadı.
3. **Kalabalık konut çocuğa zarar veriyor. Bulgu farklı ülke ve tasarımlarda tekrarlanıyor.**
   - Oda başına kişi 0,2 artınca 3 yaşında davranış sorunu puanı **+0,20** (0,08–0,32) artıyor (Marsh ve ark. 2019, kohort) [D].
   - Lise yıllarındaki kalabalık lise bitirmeyi ve ulaşılan eğitimi düşürüyor (Lopoo ve London 2016) [D].
   - Fransa'da yatak odası başına iki ve daha çok çocuğun düştüğü evlerde gençlerin %60'tan fazlası sınıf tekrarlamış; yazarlar ilişkinin nedensel olduğunu savunuyor (Goux ve Maurin 2005) [K].
4. **Yüksek katın genel sağlık farkı büyük ölçüde seçilimden geliyor. Ama somut bazı bedeller kalıyor.**
   - Belçika'da 6,1 milyon kişide yüksek binada iyi sağlık OR **0,67**; sosyoekonomik düzeltmeyle **1,04** (Verhaeghe ve ark. 2016) [D].
   - Kalp durmasında hayatta kalma alt katlarda %4,2, 3. kat ve üstünde %2,6; 16. katın üstünde **%0,9**; 25. katın üstünde hayatta kalan yok (Drennan ve ark. 2016) [D].
   - Derlemeler yüksek katı küçük çocuklar ve küçük çocuklu anneler için olumsuz buluyor (Gifford 2007; Evans 2003) [D].
5. **Seyreklik de sağlık için kötü.** UK Biobank'ta (419.562 kişi) km²'de 1.800 konutun altında yoğunluk arttıkça şişmanlık artıyor; üstünde azalıyor (obezite OR 1,10'a karşı **0,91**) (Sarkar ve ark. 2017) [D]. 14 kentte en elverişli ve en elverişsiz mahalle arasında haftada 68–89 dakika hareket farkı var (Sallis ve ark. 2016) [D].
6. **Yoksulluğun yoğunlaştığı toplu konut kulelerinin yıkılması suçu düşürdü ve çocukların geleceğini iyileştirdi. Ama etki kuleden çok yoğunlaşmış yoksulluktan geliyor.**
   - Chicago'da yıkımdan sonra çevrede suç **−%8,8** (Sandler 2017) [D]. Yerinden edilen çocuklar genç yetişkinlikte daha çok çalışıyor ve daha az tutuklanıyor (Chyn 2018) [D].
   - Benzer mahallelere taşınan çocukların okul başarısı değişmedi (Jacob 2004) [D]. Randomize MTO deneyinde fayda, 13 yaşından önce daha az yoksul mahalleye taşınanlarda (Chetty ve ark. 2016) [D].
7. **Sosyal sermaye için yürünebilirlik, orta yoğunluk ve ortak yeşil alan olumlu; yoğunluğun kendisi belirleyici değil. Kanıt çoğunlukla kesitsel.**
   - Yürünebilir karma mahallede oturanlar komşularını daha çok tanıyor ve başkalarına daha çok güveniyor (Leyden 2003) [D].
   - Komşuyla etkileşim orta yoğunlukta en iyi (Bramley ve ark. 2009) [D]. Konut yoğunluğu komşuluk bağlarıyla ilişkisiz, otomobil bağımlılığıyla ilişkili (Freeman 2001) [D].
   - 18 özdeş binaya rastgele yerleştirilen sakinlerde ortak alandaki ağaç ve çim komşuluk bağlarını artırıyor (Kuo ve ark. 1998) [D].
8. **Ev sahipliğinin "daha iyi yurttaş, daha başarılı çocuk" etkisi, seçilimi denetleyen çalışmalarda küçülüyor.**
   - Rastgele atamaya dayalı araç değişkenle ev sahipliğinin siyasi katılıma etkisi yok (Engelhardt ve ark. 2010) [K].
   - Eşleştirme ve araç değişkenle çocuk sonuçlarına etkisi için az kanıt var (Holupka ve Newman 2012) [D].
   - Buna karşılık Finlandiya'da kiracıların ölüm riski erkekte 2,06, kadında 1,73 kat (Laaksonen ve ark. 2008) [D]. Bu fark büyük ölçüde servet ve seçilimin göstergesi olabilir.

### Özet tablo

| Tema | Kanıt ne diyor? | Projenin eğilimine göre yön | Güç |
|---|---|---|---|
| **İnovasyon ve üretkenlik** | Yoğunluk ve yakınlık güçlü artı. Fayda yürüme ölçeğinde sönüyor. Konut arzını kısmak pahalı. | Yoğunluk lehine; ama faydanın ölçeği insan ölçeği | G |
| **Sağlık** | Yükseklikteki genel fark çoğunlukla seçilim. Acil erişim ve küçük çocuk bedeli var. Seyreklik hareketsizlik ve şişmanlık getiriyor. | Karışık: "orta yoğunluk, alçak-orta kat, sık ağ" | O |
| **Sosyal sermaye** | Yürünebilirlik, orta yoğunluk ve ortak yeşil olumlu. Yoğunluk tek başına belirleyici değil. Ev sahipliğinin nedensel etkisi küçük. | Sokak ve ortak alan tasarımı lehine | Z–O |
| **Güvenlik** | Bina büyüklüğü korkuyu artırıyor. Toplu konut kulelerinin yıkımı suçu düşürdü. Yoğunluk ile şiddet arasında ters U. | İnsan ölçeği lehine; ama mekanizma büyük ölçüde toplumsal | O–G |
| **Aile ve çocuk** | Kalabalık çocuğa zarar veriyor. Konut tipinin doğurganlık farkı çoğunlukla seçici taşınma. Kuşak yakınlığı kadın istihdamını artırıyor. | Geniş konut ve kuşak yakınlığı lehine; yükseklik için kanıt zayıf | O–G |

---

## 1. İnovasyon ve üretkenlik

**Mekanizma.** İnsanlar yakın olunca daha kolay karşılaşıyor, eşleşiyor ve birbirinden öğreniyor. Bu bilgi taşması yüz yüze ilişkiye dayanıyor ve mesafeyle hızla zayıflıyor.

| İddia | Etki büyüklüğü | Tasarım | Düzey | Kaynak | İşaret |
|---|---|---|---|---|---|
| Yoğunluk ücreti ve verimliliği artırıyor, kirayı daha çok artırıyor; kiracı ve ilk kez ev alacak olan zarar görüyor | Yoğunluk +%10 → kişi başı yılda ücret +140 $, kira +243 $; vergi sonrası reel ücret −171 $; imkân etkisi +106 $; net dış refah +29 $ | Sentez: 102 çalışma, 202 esneklik, 15 sonuç | G | Ahlfeldt ve Pietrostefani 2019 | [D] |
| Üretim ve konut dışsallıkları büyük ve çok yerel | Özette sayı yok | Doğal deney: Berlin'in bölünmesi ve birleşmesi, yapısal model | G | Ahlfeldt ve ark. 2015 | [D] |
| Yan yana olmak ortak araştırmayı artırıyor | Ortak araştırma olasılığı **3,5 kat** | Doğal deney: asbest temizliği yüzünden laboratuvar yer değişimi | G | Catalini 2018 | [D] |
| Yakın komşu firmanın faydası mesafeyle "son derece hızlı" sönüyor; fayda ücretten çok kiraya gidiyor | Özette sayı yok | Manhattan reklam ajansları, ince coğrafi ölçek | O | Arzaghi ve Henderson 2008 | [D] |
| Sokak ağı yoğunluğu inovasyon farkını açıklıyor | Özette sayı yok | Kesitsel, ABD'nin bütün blok grupları; tarihî planlardan araç değişken | O | Roche 2020 | [D] |
| İstihdam yoğunluğu patent üretimini artırıyor; bir yoğunlukta zirve yapıyor | Yoğunluk iki kat → kişi başı patent **+%20**; zirve ≈2.200 iş/mil² (≈850 iş/km²) | Metropol regresyonu | O | Carlino ve ark. 2007 | [K] (çalışma makalesi özeti) |
| İnovasyon, sanayi faaliyetinden daha yoğunlaşmış; şehir büyüklüğü ve çeşitliliği önemli | Özette sayı yok | Derleme (el kitabı bölümü) | O | Carlino ve Kerr 2015 | [K] (NBER özeti) |
| Yüksek verimli şirketler üst katta, perakende zeminde; yığılma kiraya yansıyor | İstihdam iki kat → kira **+%10,7**; bir kat yukarı ≈ posta koduna 3.500 çalışan eklemek | Ofis kat kirası, hedonik model | O | Liu, Rosenthal ve Strange 2018 | [D] |
| Yayılma emek verimliliğini düşürüyor | Özette sayı yok | ABD metropolleri; EKK ve araç değişken | O | Fallah ve ark. 2011 | [D] |
| Konut arzı kısıtları işçiyi verimli şehirden uzak tutuyor | ABD büyümesi 1964–2009'da **−%36** (model) | Uzamsal denge modeli, 220 metropol | O | Hsieh ve Moretti 2019 | [D] |
| Mahalle ölçeğinde kompakt yer pahalı, inovatif firma daha az; bölge ölçeğinde kompaktlık inovatif firmayı artırıyor | Özette sayı yok | Çok düzeyli kesitsel model | Z | Hamidi ve Zandiatashbar 2019 | [D] |
| Yoğunluk verimlilik ve erişim getiriyor; kalabalık ve maliyet de getiriyor | Özette sayı yok | Derleme | O | Duranton ve Puga 2020 | [D] |
| Evden çalışma bireysel performansı artırıyor; terfi düşüyor | Performans **+%13** (dakika +%9; daha sessiz ortam yüzünden dakika başına çağrı +%4); yeniden seçimle ≈%22; işten ayrılma yarıya iniyor | Randomize deney, 9 ay | G | Bloom ve ark. 2015 | [D] |
| Uzaktan çalışan ekipler daha az çığır açan buluş yapıyor | Özette sayı yok | 20 milyon makale, 4 milyon patent | O | Lin, Frey ve Wu 2023 | [D] |

**Okuma.**
- Yoğunluğun verimlilik faydası gerçek ve büyük. Proje bunu yok sayamaz.
- Ama faydanın ölçeği bina, blok ve yürüme mesafesi. Kanıt "kule"yi değil, sık ve yürünebilir dokuyu işaret ediyor.
- Yükseklik primi ofis kulelerinde gösterildi. Konut kulesinin inovasyona ayrıca katkısı için kanıt bulunamadı.
- Yoğunluk faydasının önemli kısmı kiraya ve arsa değerine gidiyor. Bu, kompakt mahallede küçük firmaları ve kiracıları zorluyor (Ahlfeldt ve Pietrostefani; Arzaghi ve Henderson; Hamidi ve Zandiatashbar).
- Evden çalışma bireysel üretkenliği artırabiliyor. Yazarlar artışın bir kısmını daha sessiz ve elverişli çalışma ortamına bağlıyor (Bloom ve ark.). Bu, evde çalışacak bir yer olmasının önemine işaret ediyor; ama konut büyüklüğü bu deneyde ölçülmedi.
- Buluş için ise yüz yüze karşılaşma gerekiyor (Lin ve ark.; Catalini).

---

## 2. Sağlık

**Mekanizma.**
- Yüksek kat: çocuğun dışarıyla teması ve gözetimi zorlaşıyor; acil ekibin ulaşması uzuyor; komşuluk zayıflayabiliyor.
- Yoğunluk ve sokak ağı: yürünecek yer ve yol olunca hareket artıyor; seyrek ve araba bağımlı dokuda azalıyor.
- Konut büyüklüğü ve kalabalık: mahremiyet, uyku ve çalışma alanı daralıyor.
- Bahçe ve avlu: doğa teması ve kendi dış alanı.

| İddia | Etki büyüklüğü | Tasarım | Düzey | Kaynak | İşaret |
|---|---|---|---|---|---|
| **Yükseklik** | | | | | |
| Yüksek kat çoğu insan için daha az tatmin edici, çocuklar için uygun değil; yardımlaşma daha az, suç ve korku daha fazla. Sonuçlar gelir, ebeveynlik, iç mekân yoğunluğu ve konut biçimini seçebilmeye bağlı | Özette sayı yok | Anlatı derlemesi | O | Gifford 2007 | [D] |
| Yüksek katlı konut küçük çocuklu kadınların ruh sağlığına aykırı; oda başına kişi sıkıntıyı artırıyor ama ağır ruhsal hastalık yapmıyor | Özette sayı yok | Derleme | O | Evans 2003 | [D] |
| Konut tipi, kat düzeyi ve ortak merdiven gibi alanlar ruh sağlığıyla ilişkili; kavram ve yöntem zayıf | 23 çalışma (1971–2016) | Sistematik derleme | O | Barros ve ark. 2019 | [D] |
| Yüksek binadaki kötü sağlık sosyoekonomik ayrışmadan geliyor; bina içinde 6. kata kadar sağlık hafifçe iyileşiyor | Ham OR **0,67** (0,67–0,68) → düzeltilmiş **1,04** (1,03–1,05); 6. kat OR 1,19 (1,15–1,24) | Nüfus sayımı, 6.102.820 kişi | O | Verhaeghe ve ark. 2016 | [D] |
| Galeri (deck) erişimli ve 1969 sonrası konut alanlarında depresyon daha yaygın | OR **1,28** (1,03–1,58); OR 1,43 (1,06–1,91) | Kesitsel, 1.887 kişi, Kuzey Londra | Z | Weich ve ark. 2002 | [D] |
| Yüksek katta kalp durmasında hayatta kalma düşük | Alt katlarda %4,2, 3. kat ve üstünde %2,6; 16. kat üstünde **%0,9**; 25. kat üstünde hayatta kalan yok | Geriye dönük kohort, 7.842 olay, Toronto | O | Drennan ve ark. 2016 | [D] |
| **Yoğunluk ve sokak ağı** | | | | | |
| Konut yoğunluğu ile şişmanlık arasında ters U | 1.800 konut/km² altında +1.000 konut/km² → obezite OR 1,10 (1,07–1,14); üstünde OR **0,91** (0,90–0,93) | Kesitsel, UK Biobank, 419.562 kişi | O | Sarkar ve ark. 2017 | [D] |
| Konut yoğunluğu, kavşak yoğunluğu ve park sayısı hareketi artırıyor | exp(b): 1,006 / 1,069 / 1,146; en iyi ile en kötü mahalle farkı haftada **68–89 dk** (önerinin %45–59'u) | Kesitsel, 14 kent, ivmeölçer | O | Sallis ve ark. 2016 | [D] |
| Yürüme kavşak yoğunluğu, karma kullanım ve varış noktalarıyla ilişkili; nüfus yoğunluğu zayıf | Esneklikler mutlak değerce ≤ 0,39 | Meta-analiz | O | Ewing ve Cervero 2010 | [D] |
| Yürünebilir mahallede daha çok adım | Günde **+766 adım** (250–1.271), önerinin ≈%8'i | Sistematik derleme ve meta-analiz | O | Hajna ve ark. 2015 | [D] |
| Kentsel yoğunluk ve toplu taşıma erişimi antidepresan kullanımına karşı hafif koruyucu | Özette sayı yok | Boylamsal kohort, Torino | O | Melis ve ark. 2015 | [D] |
| **Konut büyüklüğü** | | | | | |
| Küçük, manzarası ve iç mekânı kötü konutta kapanma döneminde depresif belirti fazla | <60 m² **1,31**; kötü manzara 1,368; kötü iç mekân 2,253 kat | Kesitsel web anketi, 8.177 öğrenci, Milano | Z | Amerio ve ark. 2020 | [D] |
| Kişi başı oda artışı yaşam memnuniyetini yalnız erkeklerde, zayıf artırıyor; "daha büyük eve" taşınma öznel iyi oluşu artırmıyor | Özette sayı yok | Panel, sabit etkiler (BHPS) | O | Foye 2017 | [D] |
| **Bahçe ve avlu** | | | | | |
| Özel bahçe daha iyi iyi oluşla; balkon, avlu ya da veranda fiziksel aktiviteyle ilişkili | Özette sayı yok | Kesitsel temsilî anket, 7.814 kişi | Z | de Bell ve ark. 2020 | [D] |
| **Mülkiyet** | | | | | |
| Kiracıların ölümü ev sahiplerinden yüksek; gelir, meslek ve eğitim farkın bir kısmını açıklıyor | HR erkek **2,06** (1,98–2,14), kadın 1,73 (1,65–1,81); düzeltme fazlalığı %30 ve %19 azaltıyor | Kayıt kohortu, 308.291 kişi | O | Laaksonen ve ark. 2008 | [D] |

**Okuma.**
- Yüksek katın kendisinin genel sağlığa etkisi küçük ya da seçilimle açıklanıyor. Bu, Rapor 13'teki bulguyla örtüşüyor: ilçe ölçeğinde kat başına ölümlülük etkisi PM2.5 ve ağaç denetlenince %0,85'e indi ve anlamsızlaştı [H].
- Ama iki somut bedel kalıyor: acil durumda dikey mesafe (kalp durması) ve küçük çocukların dışarıyla teması. İkisi de yaşlanan nüfus ve aile için önemli.
- Seyreklik de zararlı. 1.800 konut/km² düşük bir eşik: hektarda 18 konut. Orta katlı bitişik nizam bir doku bu eşiği genellikle aşar (bu bir çıkarım; çalışmada ölçülmedi). Yani sağlık kanıtı "alçak ve seyrek"i değil, "alçak-orta katlı ama yoğun ve sık ağlı" dokuyu destekliyor.
- Konut büyüklüğünün yetişkin iyi oluşuna etkisi sabit etkili panelde zayıf. Kalabalığın asıl bedeli çocuklarda görülüyor (§5).
- Galeri erişimi uyarısı: Weich ve ark. (2002) galeri erişimli konut alanlarında depresyonu daha yüksek buldu. Rapor 15'in (e) tipi bir Z+3 galerili blok. Çalışma kesitsel ve Kuzey Londra'daki iki bölgeye dayanıyor; galerinin kendisinin mi, yoksa o konut alanlarının sosyal yapısının mı etkili olduğu ayrılamıyor. Yine de galerinin "sokak" gibi işlemesi için ölçek, görünürlük ve sahiplenme koşulları tasarımda açıkça karşılanmalı.

---

## 3. Toplumsal güven ve sosyal sermaye

**Mekanizma.** Komşuluk bağları çoğunlukla planlanmamış, kısa karşılaşmalardan doğar: kaldırımda, avluda, merdivende. Bunların sıklığı yürüme, ortak alan kullanımı ve aynı yerde uzun süre oturmaya bağlı.

| İddia | Etki büyüklüğü | Tasarım | Düzey | Kaynak | İşaret |
|---|---|---|---|---|---|
| Yürünebilir karma mahallede oturanlar komşularını daha çok tanıyor, siyasete daha çok katılıyor, başkalarına daha çok güveniyor | Özette sayı yok | Kesitsel hane anketi, Galway | Z | Leyden 2003 | [D] |
| Komşuyla etkileşim ve gruplara katılım orta yoğunlukta en iyi; yoğun merkezde memnuniyet ve güvenlik düşük (önemli kısmı sosyal bileşimden) | Özette sayı yok | Beş İngiliz kenti, hane anketleri | O | Bramley ve ark. 2009 | [D] |
| Konut yoğunluğu komşuluk bağlarıyla ilişkisiz; otomobil bağımlılığıyla güçlü ilişkili | Özette sayı yok | Kesitsel anket, üç ABD kenti | Z | Freeman 2001 | [D] |
| Yayılma bazı sosyal sermaye türlerini destekliyor, bazılarını zayıflatıyor; ilçe ölçeğinde yoğunluk ve sokak erişilebilirliği ideal kaldıraç olmayabilir | Özette sayı yok | Üç düzeyli hiyerarşik model | O | Nguyen 2010 | [D] |
| Yoğunluk ile sosyal etkileşim (araç değişkenle) | Yön bu oturumda doğrulanmadı | Social Capital Benchmark Survey, IV | O | Brueckner ve Largey 2008 | [K] |
| Kompakt mahallede kişisel ilişki memnuniyeti yüksek ama kaygı da yüksek; güvenlik, gürültü ve temizlik denetlenince yaşam memnuniyetiyle pozitif | Özette sayı yok | Kesitsel anket, Oslo | Z | Mouratidis 2019 | [D] |
| Ortak alandaki ağaç ve çim, ortak alan kullanımını ve komşuluk bağlarını artırıyor; güvenlik duygusuyla da ilişkili | Özette sayı yok | Yarı deneysel: 18 özdeş binaya rastgele yerleşim, 145 kişi | O | Kuo ve ark. 1998 | [D] |
| Ev sahipleri sosyal sermayeye daha çok yatırım yapıyor; etkinin büyük kısmı daha az taşınmaktan | Özette sayı yok | GSS + araç değişken; SOEP + bireysel sabit etki | O | DiPasquale ve Glaeser 1999 | [K] (NBER özeti) |
| Rastgele atamaya dayalı araç değişkenle ev sahipliğinin siyasi katılıma etkisi yok | Özette sayı yok | Randomize saha deneyine dayalı IV | G | Engelhardt ve ark. 2010 | [K] (SSRN özeti) |
| Büyük apartman binaları ve sosyal sermaye | Doğrulanmadı | Doğrulanmadı | — | Glaeser ve Sacerdote 2000 | [K] (yalnız künye) |

**Okuma.**
- Ölçek önemli. Sokak, avlu ve ortak alan tasarımı (yürünebilirlik, ağaç, karma kullanım) bağlarla tutarlı biçimde ilişkili. İlçe ölçeğindeki yoğunluğun kendisi ise belirleyici değil (Nguyen; Freeman).
- Bramley ve ark. "orta yoğunlukta en iyi" sonucu, projenin orta katlı doku önerisiyle uyumlu.
- Brueckner ve Largey (2008) projenin [kaynakca.csv](kaynakca.csv) dosyasında "Yoğunluk arttıkça sosyal etkileşim ölçüleri azalıyor" diye kayıtlı. Bu oturumda okunan özet yalnız yöntemi veriyor; yön doğrulanmadı.
- Ev sahipliğinin sosyal sermaye etkisi gözlemsel çalışmalarda var; rastgele atamaya dayalı tek çalışmada yok. Ortak mekanizma "aynı yerde uzun süre oturmak" gibi görünüyor (DiPasquale ve Glaeser). Bu istikrar kirada da sağlanabilir.

---

## 4. Güvenlik ve suç

**Mekanizma.** Newman'ın "savunulabilir alan" kuramına göre küçük binalar ve bir haneye ait görünen dış alanlar, sakinlerin denetimini ve sahiplenmesini artırır. Jacobs'a göre sokaktaki gözler (karma kullanım ve yaya) gözetim sağlar. Eleştiri: mekân ancak toplumsal doku yerindeyse işe yarar.

| İddia | Etki büyüklüğü | Tasarım | Düzey | Kaynak | İşaret |
|---|---|---|---|---|---|
| Bina yüksekliği düşük gelirli projelerde soygunun önde gelen öngörücüsü; bina büyüklüğü korkuyu güçlü, kişisel suçu beklenenden zayıf etkiliyor; mekanizma dış alanın denetimi | Özette sayı yok | Hane anketi, orta ve düşük gelirli konut projeleri | O | Newman ve Franck 1982 | [K] (2017 yeniden basım özeti) |
| Toplumsal doku parçalıysa mimari olarak savunulabilir alanlar da savunulmuyor | Özette sayı yok | Etnografik saha çalışması | Z | Merry 1981 | [D] |
| Çevresel tasarımla suç önleme destekleniyor, ama kanıt kesin değil ve eleştiriliyor | Özette sayı yok | Derleme | O | Cozens, Saville ve Hillier 2005 | [D] |
| Toplu konut yıkımından sonra çevrede suç düşüyor, en çok şiddet suçu | Suç **−%8,8**; en az 5 yıl sürüyor | Farkların farkı ve olay çalışması, Chicago 1995–2010 | G | Sandler 2017 | [D] (ICPSR kaydı) |
| Yıkım mahallesinde ve yerinden edilenleri alan mahallede şiddet düşüyor; şehirde net azalma | Yıkım mahallesinde cinayet, saldırı, soygun **−%10–20**; şehirde cinayet ≈−%3, saldırı ≈−%2 | Mahalle ve şehir panelleri | G | Aliprantis ve Hartley 2015 | [K] (çalışma makalesi özeti) |
| Binanın çevresi yeşilse daha az suç; daire sayısı, bina yüksekliği ve boşluk denetlenince de | Özette sayı yok | Yarı deneysel: 98 bina, rastgele yerleşim, polis kayıtları | O | Kuo ve Sullivan 2001 | [D] |
| Ticari ve konut yoğunluğu ile cinayet ve ağır saldırı arasında ters U; soygunla doğrusal pozitif | Özette sayı yok | Columbus mahalleleri, parsel verisi | O | Browning ve ark. 2010 | [D] |

**Okuma.**
- Savunulabilir alan kuramının korku kısmı daha güçlü, suç kısmı daha zayıf destekleniyor (Newman ve Franck). Toplumsal doku olmadan mimari tek başına yetmiyor (Merry).
- Yıkım çalışmaları, yoksulluğun yoğunlaştığı yüksek toplu konutun çevresine suç yüklediğini gösteriyor. Ama bu bulgu "yükseklik" ile "yoksulluğun tek yerde toplanması"nı ayıramıyor. Türkiye'de hanelerin %70,8'i 3 ve daha çok katlı binada oturuyor (2021; Rapor 15) [D]; apartman yoksulların değil çoğunluğun konutu. Bu yüzden bulgu doğrudan aktarılamaz.
- Ağaç ve yeşil, bina yüksekliği denetlendikten sonra bile suçla ters ilişkili. Bu, avlu ve ortak yeşil önerisini destekliyor.
- Yoğunluğun suçla ilişkisi doğrusal değil: düşük düzeyde artırıyor, eşikten sonra azaltıyor (Browning ve ark.).

---

## 5. Aile ve çocuk

**Mekanizma.** Kalabalık evde çocuk uyku, ders çalışma ve dinlenme alanını kaybediyor; ebeveyn stresi ve aile içi gerginlik artıyor. Yüksek katta küçük çocuk dışarı daha az çıkıyor. Kuşakların yakın oturması çocuk bakımını kolaylaştırıyor.

| İddia | Etki büyüklüğü | Tasarım | Düzey | Kaynak | İşaret |
|---|---|---|---|---|---|
| **Kalabalık** | | | | | |
| Kalabalık evde çocukların başarı, davranış ve sağlık göstergeleri kötü; sosyoekonomik durum denetlense de | Özette sayı yok | PSID-CDS ve Los Angeles FANS | O | Solari ve Mare 2012 | [D] |
| Kalabalık 3 yaşında davranış sorununu artırıyor; anne stresi, az uyku ve gergin ilişki kısmen aracı | Oda başına kişi +0,2 → SDQ **+0,20** (0,08–0,32) | Doğum kohortu, 2.576 çocuk | O | Marsh ve ark. 2019 | [D] |
| Lise yıllarındaki kalabalık lise bitirmeyi ve 25 yaşta eğitimi düşürüyor | Özette sayı yok | Boylamsal (PSID) | O | Lopoo ve London 2016 | [D] |
| Yatak odası başına ≥2 çocuk ile sınıf tekrarı arasında nedensel ilişki | 15 yaşındakilerin ≈beşte biri böyle evde; bunların %60'tan fazlası sınıf tekrarlamış, ortalamadan 20 puandan fazla | Yarı-parametrik analiz, Fransa | O | Goux ve Maurin 2005 | [K] (CEPR özeti) |
| **Yükseklik ve toplu konut** | | | | | |
| Yüksek katta yaşayan küçük çocuklarda günlük alışkanlıklarda bağımsızlık gecikiyor; dışarı çıkma azalıyor | Özette sayı yok | Anket, 1.045 küçük çocuk, Tokyo | Z | Oda ve ark. 1989 | [D] (PubMed; Crossref'te yok) |
| Yıkımla yerinden edilip daha az yoksul mahalleye taşınan çocuklar yetişkinlikte daha çok çalışıyor, daha az tutuklanıyor | Özette sayı yok | Doğal deney, Chicago | G | Chyn 2018 | [D] |
| Benzer mahalleye taşınan çocuklarda okul başarısı değişmiyor; yazar bunu yüksek katlı toplu konutun bağımsız etkisinin sıfır olduğu biçiminde yorumluyor | Sıfır etki | Doğal deney, Chicago | G | Jacob 2004 | [D] |
| 13 yaşından önce daha az yoksul mahalleye taşınmak üniversiteye gitmeyi ve kazancı artırıyor | Özette sayı yok | Randomize deney (MTO) | G | Chetty, Hendren ve Katz 2016 | [D] |
| **Konut tipi ve doğurganlık** | | | | | |
| Doğurganlık müstakil evde en yüksek, apartmanda en düşük; ama farkın çoğu seçici taşınmadan | Özette sayı yok | Finlandiya kayıt verisi, olay tarihi modeli | O | Kulu ve Vikat 2007 | [K] (MPIDR özeti) |
| **Kuşaklar arası yakınlık** | | | | | |
| Anneye ya da kayınvalideye yakın oturmak küçük çocuklu evli kadınların çalışmasını artırıyor | İstihdam olasılığı **+4–10 yüzde puan** | NSFH ve nüfus sayımı | O | Compton ve Pollak 2014 | [K] (NBER özeti) |
| **Mülkiyet** | | | | | |
| Ev sahipliği ev ortamını ve çocuk başarısını iyileştiriyor | Ev ortamı +%13–23; matematik +%9'a, okuma +%7'ye kadar; davranış sorunu −%1–3 | Panel, tedavi etkisi modeli | O | Haurin, Parcel ve Haurin 2002 | [D] |
| Seçilim denetlenince ev sahipliğinin çocuğa yararı için az kanıt | Özette sayı yok | Eşleştirme ve araç değişken | O | Holupka ve Newman 2012 | [D] |

**Okuma.**
- Bu temada en sağlam bulgu **kalabalık**: ABD, İngiltere ve Fransa'dan farklı veri setlerinde, farklı yaşlarda ve sonuçlarda aynı yön. Türkiye'de nüfusun %37,8'i, çocukların %50,7'si aşırı kalabalık konutta (2025; Rapor 15) [D]. Bu, konut biçimi tartışmasında yükseklikten daha önemli bir hedef.
- Yüksekliğin çocuğa doğrudan etkisine dair kanıt eski ve zayıf (Oda ve ark.; derlemeler). Toplu konut çalışmalarında etki mahalle yoksulluğundan geliyor (Jacob; Chetty ve ark.).
- Konut tipiyle doğurganlık farkı çoğunlukla seçici taşınma (Kulu ve Vikat). Bu, Rapor 26'daki "bina yüksekliği → doğum düşüşü ≈ 0" bulgusuyla uyumlu [H].
- Kuşak yakınlığı kadın istihdamı için güçlü bir etken (Compton ve Pollak). Bu, çok kuşaklı konut tipini (Rapor 15, tip d) ve aynı mahallede farklı büyüklükte konut bulunmasını destekliyor.

---

## Projenin tezine ne diyor?

Projenin eğilimi alçak-orta katlı, insan ölçekli, yürünebilir, avlulu ve aileyi gözeten bir konut dokusu. Kanıt bu eğilimin bir kısmını destekliyor, bir kısmını sınırlıyor.

**Kanıtın yoğunluk ve yükseklik lehine olduğu yerler (projeye ters):**
- **Verimlilik ve inovasyon.** Taramadaki en güçlü kanıt burada ve yön açık: yoğunluk ücreti, verimliliği ve buluşu artırıyor (Ahlfeldt ve Pietrostefani; Ahlfeldt ve ark.; Catalini; Carlino ve ark.). Yayılma verimliliği düşürüyor (Fallah ve ark.).
- **Konut arzı.** Verimli şehirlerde konut arzını kısmak ülke büyümesini ciddi düşürüyor (Hsieh ve Moretti, model tahmini −%36). "Alçak kat" kuralı arzı kısarsa bu bedel doğar.
- **Seyreklik sağlığa zararlı.** Seyrek banliyöde şişmanlık artıyor; yoğunluk ve kavşak sıklığı hareketi artırıyor (Sarkar ve ark.; Sallis ve ark.; Hajna ve ark.). Torino'da yoğunluk antidepresan kullanımına karşı hafif koruyucu (Melis ve ark.).
- **Yükseklik ve genel sağlık.** Belçika'da 6,1 milyon kişide yüksek bina farkı seçilim denetlenince kayboluyor (Verhaeghe ve ark.). Projenin kendi ilçe analizi de aynı yönde (Rapor 13) [H].
- **Mülkiyet.** Ev sahipliğinin sosyal sermaye ve çocuk faydası, seçilimi denetleyen çalışmalarda küçülüyor ya da kayboluyor (Engelhardt ve ark.; Holupka ve Newman).

**Kanıtın alçak-orta kat ve insan ölçeği lehine olduğu yerler:**
- **Faydanın ölçeği.** Yığılma faydası blok ve yürüme mesafesinde sönüyor (Arzaghi ve Henderson; Ahlfeldt ve ark.). Sokak ağı yoğunluğu ve kavşak sıklığı hem inovasyonla hem yürümeyle ilişkili (Roche; Ewing ve Cervero). Bu, Rapor 11'in geleneksel doku bulgusunu (küçük tane, sık ağ) destekliyor.
- **Kalabalık.** Oda başına kişi çocuğun davranışını, okulunu ve eğitimini bozuyor (Marsh ve ark.; Lopoo ve London; Solari ve Mare; Goux ve Maurin). Rapor 15'teki kişi başı alan ve oda sayısı ölçütlerinin en güçlü gerekçesi bu.
- **Somut yükseklik bedelleri.** Kalp durmasında 16. kat üstünde hayatta kalma %0,9 (Drennan ve ark.). Küçük çocuk ve annesi için olumsuzluk (Gifford; Evans; Oda ve ark.). Rapor 27'de aynı il ve şiddette yüksek binalı ilçelerde deprem sonrası nüfus kaybı daha büyük çıktı (kesin değil) [H].
- **Ortak alan ve yeşil.** Avlu ve ortak alandaki ağaç komşuluk bağlarını artırıyor ve suçu azaltıyor; bina yüksekliği denetlendikten sonra da (Kuo ve ark.; Kuo ve Sullivan). Özel bahçe ve balkon iyi oluş ve hareketle ilişkili (de Bell ve ark.).
- **Orta yoğunluk.** Komşu etkileşimi orta yoğunlukta en iyi (Bramley ve ark.). Bina büyüklüğü suç korkusunu artırıyor (Newman ve Franck).
- **Kuşak yakınlığı.** Anneye ya da kayınvalideye yakınlık kadın istihdamını 4–10 yüzde puan artırıyor (Compton ve Pollak).

**Dikkat edilmesi gereken gerilimler:**
- **"Alçak" ile "seyrek" aynı şey değil.** Kanıt seyrek ve araba bağımlı dokuyu açıkça kötülüyor. Projenin önerisi ancak alçak-orta katlı ama yoğun, sık ağlı ve karma kullanımlı olursa kanıtla uyumlu.
- **Arsa ve kira.** Yoğunluk faydasının önemli kısmı kiraya gidiyor. Rapor 15'te avlulu tek-iki katlı tiplerin büyükşehirde 11–13 milyon TL'yi bulması bunun bir yüzü [H]. Gerçekçi kentsel tipler (sıra ev, çok kuşaklı avlu evi, Z+3 blok) daha yoğun.
- **Galeri erişimi.** Weich ve ark. (2002) galeri erişimli konut alanlarında depresyon OR 1,28 buldu. Tip (e) tasarlanırken galerinin ölçeği, görünürlüğü ve sahiplenilmesi özellikle denetlenmeli.
- **Mülkiyetin gerekçesi.** Ev sahipliği savunulacaksa gerekçe "daha iyi yurttaş" değil, istikrar ve servet olmalı. Aynı istikrar uzun süreli kira güvencesiyle de sağlanabilir.

**Kısa yargı.** Kanıt "alçak ve seyrek" bir şehri desteklemiyor. "Orta katlı, sık sokaklı, yeterince geniş konutlu, avlulu ve yoğun" bir dokuyu destekliyor. Yüksekliğin kendisi çoğu sonuçta küçük ya da seçilimle açıklanabilir. Ama yoğunluk ve yakınlık verimlilikte güçlü bir artı; seyreklik sağlıkta bir eksi; kalabalık çocuklarda açık bir zarar.

---

## Sınırlılıklar

- **Sistematik değil.** Kaynaklar bilinen künyelerden ve sınırlı konu aramalarından seçildi. Seçim yanlılığı olabilir.
- **Coğrafya.** Kanıtın çoğu ABD, İngiltere ve Kuzey Avrupa'dan. Türkiye'den çalışma yok. Batı'da yüksek kat çoğunlukla yoksulların toplu konutu; Türkiye'de apartman orta sınıfın konutu. Seçilimin yönü farklı olabilir.
- **Tasarım.** Sağlık ve sosyal sermaye kanıtının çoğu kesitsel. Kimin nerede oturduğu (seçilim) en büyük karıştırıcı. Doğal deneylerin çoğu toplu konut yıkımından; yükseklik ile yoksulluk yoğunlaşmasını ayıramıyor.
- **Ölçek karışıklığı.** Yoğunluk (bölge, mahalle, bina), yükseklik (kat) ve kalabalık (oda başına kişi) ayrı şeyler. Çalışmalar bunları farklı ölçeklerde ölçüyor.
- **Ekonomi kanıtı işyeri yoğunluğuna dayanıyor.** Konut biçimine aktarım dolaylı.
- **Yalnız özet okundu.** Tam metin okunmadı. Ayrıntılar (güven aralığı, alt grup) özetteki kadar. Amerio ve ark. (2020) özetindeki güven aralıkları biçim hatalı (ör. "1046-1637").
- **Sürüm farkı.** 9 kaynakta bulgu çalışma makalesi ya da yeniden basım özetinden. Bu sürümlerdeki sayılar yayımlanmış sürümden farklı olabilir; bu yüzden [K].
- **OpenAlex özetleri** sözcük dizininden yeniden kuruldu. Noktalamada küçük farklar olabilir.
- **Yayın yanlılığı** bu alanda olasıdır. Ayrı ayrı denetlenmedi.

---

## Doğrulanamayan ya da kapsam dışı kalan öncüller

| Öncül | Durum |
|---|---|
| Glaeser ve Sacerdote 2000, *The Social Consequences of Housing* | Künye Crossref'te doğrulandı (10.1006/jhec.2000.0262). Özet hiçbir serviste okunamadı; NBER w8034 kaydının metni bozuk. Bulgu doğrulanmadı; tabloda [K] (yalnız künye). |
| Brueckner ve Largey 2008 | Künye doğrulandı. Okunan özet yalnız yöntemi veriyor; sonucun yönü doğrulanmadı [K]. |
| Newman 1972, *Defensible Space* (kitap) | Crossref'te DOI'li kitap kaydı bulunamadı; yalnız kitap eleştirileri var. Kuramın ampirik sınaması olarak Newman ve Franck 1982 kullanıldı. |
| Coleman 1985, *Utopia on Trial* (kitap) | Aranmadı; kitap. Doğrulanmadı [DY]. |
| Johnson ve Bowers 2010, *Permeability and Burglary Risk: Are Cul-de-Sacs Safer?* (10.1007/s10940-009-9084-8) | Künye Crossref'te var; özet hiçbir serviste yok. Bulgu doğrulanamadığı için tabloya alınmadı. |
| Twinam 2017, *Danger zone* (10.1016/j.jue.2017.05.006) | Aynı durum; tabloya alınmadı. |
| Rosenthal ve Strange 2008, *The attenuation of human capital spillovers* (10.1016/j.jue.2008.02.006) | Aynı durum; tabloya alınmadı. |
| Ciccone ve Hall 1996, *Productivity and the Density of Economic Activity* (AER) | Crossref'te dergi sürümü için DOI kaydı bulunamadı (NBER w4313 var). Tabloya alınmadı. |
| Hüttenmoser 1995 (Zürih, çocuk ve konut çevresi) | Crossref aramasında bulunamadı [DY]. |
| Mouratidis 2018 (*Cities* 74) | Künye doğrulandı, özet yok; yerine aynı yazarın Mouratidis 2019 (*Cities* 92) çalışması alındı. |
| Dietz ve Haurin 2003; Green ve White 1997; Dettling ve Kearney 2014 | Künyeler keşif aşamasında Crossref'te açıldı; yayımlanmış özet yok. Kapsam sınırı yüzünden tabloya alınmadı. |

Keşif aşamasında Crossref'te açılıp kapsam sınırı (≈50 kaynak) yüzünden tabloya alınmayan başka çalışmalar da var (ör. Combes ve ark. 2012; Melo, Graham ve Noland 2009; Boudreau ve ark. 2017; Brucks ve Levav 2022; Koster ve ark. 2014; Evans ve ark. 1998; Barker ve Miller 2009). Bunlar bu dosyanın doğrulama kaydında yer almıyor.

---

## Kaynakça

Künyeler Crossref'ten üretildi (`konut_bicimi_kaynakca.csv`); Oda ve ark. 1989 PubMed'den.

**İnovasyon ve üretkenlik**

- Roche MP (2020). Taking Innovation to the Streets: Microgeography, Physical Structure, and Innovation. *The Review of Economics and Statistics* 102(5):912-928. https://doi.org/10.1162/rest_a_00866
- Liu CH, Rosenthal SS, Strange WC (2018). The vertical city: Rent gradients, spatial structure, and agglomeration economies. *Journal of Urban Economics* 106:101-122. https://doi.org/10.1016/j.jue.2018.04.001
- Carlino G, Kerr WR (2015). Agglomeration and Innovation. *Handbook of Regional and Urban Economics* 349-404. https://doi.org/10.1016/B978-0-444-59517-1.00006-4
- Carlino GA, Chatterjee S, Hunt RM (2007). Urban density and the rate of invention. *Journal of Urban Economics* 61(3):389-419. https://doi.org/10.1016/j.jue.2006.08.003
- Ahlfeldt GM, Pietrostefani E (2019). The economic effects of density: A synthesis. *Journal of Urban Economics* 111:93-107. https://doi.org/10.1016/j.jue.2019.04.006
- Ahlfeldt GM, Redding SJ, Sturm DM ve ark. (2015). The Economics of Density: Evidence From the Berlin Wall. *Econometrica* 83(6):2127-2189. https://doi.org/10.3982/ECTA10876
- Arzaghi M, Henderson JV (2008). Networking off Madison Avenue. *Review of Economic Studies* 75(4):1011-1038. https://doi.org/10.1111/j.1467-937X.2008.00499.x
- Catalini C (2018). Microgeography and the Direction of Inventive Activity. *Management Science* 64(9):4348-4364. https://doi.org/10.1287/mnsc.2017.2798
- Hsieh CT, Moretti E (2019). Housing Constraints and Spatial Misallocation. *American Economic Journal: Macroeconomics* 11(2):1-39. https://doi.org/10.1257/mac.20170388
- Fallah BN, Partridge MD, Olfert MR (2011). Urban sprawl and productivity: Evidence from US metropolitan areas. *Papers in Regional Science* 90(3):451-473. https://doi.org/10.1111/j.1435-5957.2010.00330.x
- Hamidi S, Zandiatashbar A (2019). Does urban form matter for innovation productivity? A national multi-level study of the association between neighbourhood innovation capacity and urban sprawl. *Urban Studies* 56(8):1576-1594. https://doi.org/10.1177/0042098018767002
- Duranton G, Puga D (2020). The Economics of Urban Density. *Journal of Economic Perspectives* 34(3):3-26. https://doi.org/10.1257/jep.34.3.3
- Bloom N, Liang J, Roberts J ve ark. (2015). Does Working from Home Work? Evidence from a Chinese Experiment. *The Quarterly Journal of Economics* 130(1):165-218. https://doi.org/10.1093/qje/qju032
- Lin Y, Frey CB, Wu L (2023). Remote collaboration fuses fewer breakthrough ideas. *Nature* 623(7989):987-991. https://doi.org/10.1038/s41586-023-06767-1

**Sağlık**

- Gifford R (2007). The Consequences of Living in High-Rise Buildings. *Architectural Science Review* 50(1):2-17. https://doi.org/10.3763/asre.2007.5002
- Evans GW (2003). The Built Environment and Mental Health. *Journal of Urban Health: Bulletin of the New York Academy of Medicine* 80(4):536-555. https://doi.org/10.1093/jurban/jtg063
- Barros P, Ng Fat L, Garcia LMT ve ark. (2019). Social consequences and mental health outcomes of living in high-rise residential buildings and the influence of planning, urban design and architectural decisions: A systematic review. *Cities* 93:263-272. https://doi.org/10.1016/j.cities.2019.05.015
- Verhaeghe PP, Coenen A, Van de Putte B (2016). Is Living in a High-Rise Building Bad for Your Self-Rated Health? *Journal of Urban Health* 93(5):884-898. https://doi.org/10.1007/s11524-016-0066-5
- Weich S, Blanchard M, Prince M ve ark. (2002). Mental health and the built environment: Cross - sectional survey of individual and contextual risk factors for depression. *British Journal of Psychiatry* 180(5):428-433. https://doi.org/10.1192/bjp.180.5.428
- Drennan IR, Strum RP, Byers A ve ark. (2016). Out-of-hospital cardiac arrest in high-rise buildings: delays to patient care and effect on survival. *Canadian Medical Association Journal* 188(6):413-419. https://doi.org/10.1503/cmaj.150544
- Sarkar C, Webster C, Gallacher J (2017). Association between adiposity outcomes and residential density: a full-data, cross-sectional analysis of 419 562 UK Biobank adult participants. *The Lancet Planetary Health* 1(7):e277-e288. https://doi.org/10.1016/S2542-5196(17)30119-5
- Sallis JF, Cerin E, Conway TL ve ark. (2016). Physical activity in relation to urban environments in 14 cities worldwide: a cross-sectional study. *The Lancet* 387(10034):2207-2217. https://doi.org/10.1016/S0140-6736(15)01284-2
- Ewing R, Cervero R (2010). Travel and the Built Environment. *Journal of the American Planning Association* 76(3):265-294. https://doi.org/10.1080/01944361003766766
- Hajna S, Ross NA, Brazeau AS ve ark. (2015). Associations between neighbourhood walkability and daily steps in adults: a systematic review and meta-analysis. *BMC Public Health* 15(1):768. https://doi.org/10.1186/s12889-015-2082-x
- Amerio A, Brambilla A, Morganti A ve ark. (2020). COVID-19 Lockdown: Housing Built Environment's Effects on Mental Health. *International Journal of Environmental Research and Public Health* 17(16):5973. https://doi.org/10.3390/ijerph17165973
- Foye C (2017). The Relationship Between Size of Living Space and Subjective Well-Being. *Journal of Happiness Studies* 18(2):427-461. https://doi.org/10.1007/s10902-016-9732-2
- Melis G, Gelormino E, Marra G ve ark. (2015). The Effects of the Urban Built Environment on Mental Health: A Cohort Study in a Large Northern Italian City. *International Journal of Environmental Research and Public Health* 12(11):14898-14915. https://doi.org/10.3390/ijerph121114898
- de Bell S, White M, Griffiths A ve ark. (2020). Spending time in the garden is positively associated with health and wellbeing: Results from a national survey in England. *Landscape and Urban Planning* 200:103836. https://doi.org/10.1016/j.landurbplan.2020.103836
- Laaksonen M, Martikainen P, Nihtilä E ve ark. (2008). Home ownership and mortality: a register-based follow-up study of 300 000 Finns. *Journal of Epidemiology and Community Health* 62(4):293-297. https://doi.org/10.1136/jech.2007.061309

**Toplumsal güven ve sosyal sermaye**

- Glaeser EL, Sacerdote B (2000). The Social Consequences of Housing. *Journal of Housing Economics* 9(1-2):1-23. https://doi.org/10.1006/jhec.2000.0262
- Leyden KM (2003). Social Capital and the Built Environment: The Importance of Walkable Neighborhoods. *American Journal of Public Health* 93(9):1546-1551. https://doi.org/10.2105/AJPH.93.9.1546
- Brueckner JK, Largey AG (2008). Social interaction and urban sprawl. *Journal of Urban Economics* 64(1):18-34. https://doi.org/10.1016/j.jue.2007.08.002
- Nguyen D (2010). Evidence of the Impacts of Urban Sprawl on Social Capital. *Environment and Planning B: Planning and Design* 37(4):610-627. https://doi.org/10.1068/b35120
- Freeman L (2001). The Effects of Sprawl on Neighborhood Social Ties: An Explanatory Analysis. *Journal of the American Planning Association* 67(1):69-77. https://doi.org/10.1080/01944360108976356
- Bramley G, Dempsey N, Power S ve ark. (2009). Social Sustainability and Urban Form: Evidence from Five British Cities. *Environment and Planning A: Economy and Space* 41(9):2125-2142. https://doi.org/10.1068/a4184
- Mouratidis K (2019). Compact city, urban sprawl, and subjective well-being. *Cities* 92:261-272. https://doi.org/10.1016/j.cities.2019.04.013
- DiPasquale D, Glaeser EL (1999). Incentives and Social Capital: Are Homeowners Better Citizens? *Journal of Urban Economics* 45(2):354-384. https://doi.org/10.1006/juec.1998.2098
- Engelhardt GV, Eriksen MD, Gale WG ve ark. (2010). What are the social benefits of homeownership? Experimental evidence for low-income households. *Journal of Urban Economics* 67(3):249-258. https://doi.org/10.1016/j.jue.2009.09.010
- Kuo FE, Sullivan WC, Coley RL ve ark. (1998). Fertile Ground for Community: Inner‐City Neighborhood Common Spaces. *American Journal of Community Psychology* 26(6):823-851. https://doi.org/10.1023/A:1022294028903

**Güvenlik ve suç**

- Newman O, Franck KA (1982). The effects of building size on personal crime and fear of crime. *Population and Environment* 5(4):203-220. https://doi.org/10.1007/BF01257071
- Merry SE (1981). Defensible Space Undefended. *Urban Affairs Quarterly* 16(4):397-422. https://doi.org/10.1177/107808748101600401
- Cozens PM, Saville G, Hillier D (2005). Crime prevention through environmental design (CPTED): a review and modern bibliography. *Property Management* 23(5):328-356. https://doi.org/10.1108/02637470510631483
- Sandler DH (2017). Externalities of public housing: The effect of public housing demolitions on local crime. *Regional Science and Urban Economics* 62:24-35. https://doi.org/10.1016/j.regsciurbeco.2016.10.007
- Aliprantis D, Hartley D (2015). Blowing it up and knocking it down: The local and city-wide effects of demolishing high concentration public housing on crime. *Journal of Urban Economics* 88:67-81. https://doi.org/10.1016/j.jue.2015.06.002
- Kuo FE, Sullivan WC (2001). Environment and Crime in the Inner City. *Environment and Behavior* 33(3):343-367. https://doi.org/10.1177/0013916501333002
- Browning CR, Byron RA, Calder CA ve ark. (2010). Commercial Density, Residential Concentration, and Crime: Land Use Patterns and Violence in Neighborhood Context. *Journal of Research in Crime and Delinquency* 47(3):329-357. https://doi.org/10.1177/0022427810365906

**Aile ve çocuk**

- Solari CD, Mare RD (2012). Housing crowding effects on children's wellbeing. *Social Science Research* 41(2):464-476. https://doi.org/10.1016/j.ssresearch.2011.09.012
- Goux D, Maurin E (2005). The effect of overcrowded housing on children's performance at school. *Journal of Public Economics* 89(5-6):797-819. https://doi.org/10.1016/j.jpubeco.2004.06.005
- Lopoo LM, London AS (2016). Household Crowding During Childhood and Long-Term Education Outcomes. *Demography* 53(3):699-721. https://doi.org/10.1007/s13524-016-0467-9
- Marsh R, Salika T, Crozier S ve ark. (2019). The association between crowding within households and behavioural problems in children: Longitudinal data from the Southampton Women's Survey. *Paediatric and Perinatal Epidemiology* 33(3):195-203. https://doi.org/10.1111/ppe.12550
- Oda M, Taniguchi K, Wen ML ve ark. (1989). Effects of high-rise living on physical and mental development of children. *J Hum Ergol (Tokyo)* 18(2):231-5. https://pubmed.ncbi.nlm.nih.gov/2637293/
- Chyn E (2018). Moved to Opportunity: The Long-Run Effects of Public Housing Demolition on Children. *American Economic Review* 108(10):3028-3056. https://doi.org/10.1257/aer.20161352
- Jacob BA (2004). Public Housing, Housing Vouchers, and Student Achievement: Evidence from Public Housing Demolitions in Chicago. *American Economic Review* 94(1):233-258. https://doi.org/10.1257/000282804322970788
- Chetty R, Hendren N, Katz LF (2016). The Effects of Exposure to Better Neighborhoods on Children: New Evidence from the Moving to Opportunity Experiment. *American Economic Review* 106(4):855-902. https://doi.org/10.1257/aer.20150572
- Kulu H, Vikat A (2007). Fertility differences by housing type. *Demographic Research* 17:775-802. https://doi.org/10.4054/DemRes.2007.17.26
- Compton J, Pollak RA (2014). Family proximity, childcare, and women's labor force attachment. *Journal of Urban Economics* 79:72-90. https://doi.org/10.1016/j.jue.2013.03.007
- Haurin DR, Parcel TL, Haurin RJ (2002). Does Homeownership Affect Child Outcomes? *Real Estate Economics* 30(4):635-666. https://doi.org/10.1111/1540-6229.t01-2-00053
- Holupka S, Newman SJ (2012). The Effects of Homeownership on Children's Outcomes: Real Effects or Self‐Selection? *Real Estate Economics* 40(3):566-602. https://doi.org/10.1111/j.1540-6229.2012.00330.x
