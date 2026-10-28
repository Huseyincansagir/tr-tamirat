# Mevzuat Değişiklik Paketi — Sürüm 2 (İP8)

*27 Ekim 2026 · Sürüm 2.0 · Taslak, hukuki görüş değildir*

| Ne | Nerede |
|---|---|
| Sürüm 1 (28 öneri, taslak madde dili) | [degisiklik_paketi_v1.md](degisiklik_paketi_v1.md) |
| Rapor 20'nin diğer seçenekleri için mevzuat araştırması (S, A, C, Y grupları) | [arastirma_diger_secenekler.md](arastirma_diger_secenekler.md) |
| Mali etki hesabı (kod, 5 CSV, 1 grafik) | [politika_v2/](politika_v2/) · `politika_v2_mali.py` |
| Özet rapor | [09_RAPORLAR/23_politika_paketi_v2.md](../09_RAPORLAR/23_politika_paketi_v2.md) |
| Kanıt tabanı | [Rapor 20: gelir, vergi, ticaret](../09_RAPORLAR/20_ekonomi_gelir_vergi_ticaret.md) · [Rapor 21: ölçeklenebilir şehir](../09_RAPORLAR/21_olceklenebilir_sehir.md) |

**Sürüm 2 = sürüm 1 + bu belge.** Sürüm 1'deki 28 önerinin metni aynen geçerli. Bu belge üç grup öneri ekliyor ve sürüm 1'den üç öneriyi genişletiyor:

1. **Arsa değer vergisi:** Vergi yükü tüketimden arsaya kaydırılır.
2. **Karma kullanım:** Mahalle içinde dükkân ve atölye kendiliğinden serbest olur.
3. **Semt yönetişimi:** Mahalle ile belediye arasındaki kademeye meclis ve bütçe verilir.

Rapor 20'nin diğer seçeneklerinden gelen 12 öneri dört grupta (§5):

4. **Sermaye geliri vergisi (S1–S3).**
5. **Asgari ve taban gelir (A1–A3).**
6. **Esnaf ve rekabet (C1–C4).**
7. **Gıda zinciri (Y1–Y2).**

Gıdada KDV'nin %0'a indirilmesi pakete alınmadı. Bu seçenek kanun ister ve aynı bütçe hedefli destekle 6 kat etkili (Rapor 20).

Etiketler sürüm 1'deki gibi:

- **Kaynak etiketleri:** **[D]** doğrulandı · **[K]** kısmen · **[DY]** doğrulanmadı.
- **Kanıt düzeyi:** **G** güçlü · **O** orta · **Z** zayıf · **N** normatif · **H** bu projede hesaplandı.

---

## 0. Neden bu üç grup?

Rapor 20 ve 21'in bulguları sürüm 1'de karşılığı olmayan üç boşluk gösterdi:

| Bulgu | Değer | Kaynak |
|---|---|---|
| Vergi yükü tüketimde | Mal ve hizmet vergileri toplam vergi ve primin %43,6'sı (OECD %31,2). En yoksul %20 gelirinin %15,1'ini KDV ve ÖTV'ye, en zengin %20 %7,8'ini veriyor | [D/H] Rapor 20 §2 |
| Arsa neredeyse vergisiz | Emlak vergisi GSYH'nin %0,09'u (arsa vergisi %0,02); OECD'de taşınmaz vergisi %0,95. Bir mahalle yılda emlak vergisinin 71 katı tüketim vergisi ödüyor | [D/H] Rapor 20 §2.4, §5.3 |
| Belediye merkezden gelen payla yaşıyor | Merkezi vergi payları mahalli idare gelirinin %57,2'si; emlak vergisi %2,6'sı | [D/H] Rapor 20 §2.4 |
| Mahallede dükkân açmak varsayılan olarak kapalı | Konut alanında zemin kat dükkânı ancak meclisin "yol boyu ticaret" kararı ve otopark şartıyla | [D] PAİY md. 19/1-f-1 |
| Düzenleme yükü yüksek | OECD ürün piyasası düzenlemesi ölçüsünde Türkiye 38 üye içinde en kısıtlayıcı (PMR 2,52; OECD 1,35) | [D/H] Rapor 20 §3.1 |
| Semt kademesinde organ yok | Lise, poliklinik, kütüphane, haftalık pazar ve istihdam ofisi semt (≈ 35 bin kişi) kademesinde; bu kademede ne karar ne bütçe organı var | [H] Rapor 21 §2; "semt" 5393 sayılı Kanunda geçmiyor [D] |

Üç grup birbirine bağlı. Arsa değer vergisi, semt ve mahalle bütçesinin kaynağı. Karma kullanım, aynı vergi tabanını canlı tutuyor; boş zemin kat yerine dükkân ve atölye arsanın değerini artırıyor. Semt meclisi bu bütçenin nereye harcanacağına karar veren organ.

**Sürüm 1'in üç ilkesi aynen geçerli:** varsayılanı değiştir, zorlama; karşılıksız kısıtlama yok; kanıt düzeyi açık. Bu sürümde dördüncü bir ilke ekleniyor:

4. **Mali nötrlük, tahsil edene küçük bir pay.** Arsa değer vergisi yeni bir vergi yükü olarak değil, tüketim vergisinin yerine gelir.
   - **Mahsup:** Tahsilatın %90'ı merkezi paydan düşülür ve aynı tutarda KDV indirilir; merkez nötr kalır.
   - **Belediyenin payı:** %10'u vergiyi toplayan belediyede kalır.
   - **Neden:** Paydaş oyunu (Rapor 24) bu payın olmadığı tasarımda belediyenin, yani uygulayıcının, dirence geçtiğini gösterdi.

---

## 1. Paketin özeti: 52 öneri

Öncelik sürüm 1'deki gibi: **1** = 2027 içinde, mevcut yetkiyle · **2** = 2027–2028 eylem planı dönemi · **3** = kanun değişikliği gerektirir (2028 ve sonrası).

### 1.1 Yeni öneriler (12)

| # | Araç | Mevzuat ve madde | Öneri (kısa) | Kanıt | Öncelik |
|---|---|---|---|---|---|
| E1 | Kanun | 1319 md. 8, 18, 29 | Bölünmüş oran: arsa ve arsa payı değeri vergilenir, yapı değeri üzerindeki vergi beş yılda sıfıra iner | O–G (teori, OECD); H (dağılım) | 3 |
| E2 | Yönetmelik + kanun | 1319 md. 29, 31; VUK mük. md. 49 | Değerleme: matrahın piyasa değerine yaklaşması, açık parsel değer haritası, yıllık güncelleme, mahallede itiraz | O; N | 2 (pilot) / 3 |
| E3 | Kanun | 1319 md. 8/2, 30 | Korumalar: alt iki gelir dilimindeki hanenin tek konutu muaf; 65 yaş üstü malike tapuya şerhle erteleme | H (S3C); N | 3 |
| E4 | Cumhurbaşkanı kararı | 3065 md. 28 | Genel KDV oranının her yıl, önceki yılın merkezi paydan mahsup edilen arsa değer vergisi tutarı kadar indirilmesi (2033'te %17,1) | H | 2 |
| E5 | Kanun | 5779 md. 2 | Mali denkleştirme: arsa değer vergisinin %90'ı merkezi paydan mahsup edilir, %10'u belediyede kalır; eşitleme tabanı | N; H | 3 |
| P6 | Yönetmelik | PAİY md. 19/1-f | Konut alanında meydan ve ana sokak cephesinde ≤ 150 m² mahalle işyeri ve atölye meclis kararı aranmadan serbest | O (uluslararası örnek) | 1 |
| O4 | Yönetmelik | Otopark Yön. Ek-1 | Zemin kattaki ≤ 100 m² mahalle işyerine otopark ihtiyacı aranmaz | H | 1 |
| M5 | Yönetmelik | MPYY md. 21/10, 24/9 | "Mahalle karma alanı": konut en az %70, zemin kat ticaret; karma kullanımın "ayrıştırılması esastır" kuralının kaldırılması | O; N | 1 |
| I5 | Kanun | 3194 Ek md. 8 | Emsal artırmadan zemin kat ticarete izin veren plan değişikliği değer artış payından muaf; değer artış payının yarısı değişikliğin yapıldığı semtte harcanır | N; H | 3 |
| R1 | Yönetmelik | İşyeri Açma ve Çalışma Ruhsatlarına İlişkin Yön. md. 12 | Mahalle işyeri için tek başvuru: imar uygunluğu, itfaiye beyanı ve ruhsat aynı gün; sonradan denetim; süre istatistiği | O | 2 |
| B3 | Belediye meclisi kararı + kent konseyi yönergesi | 5393 md. 18, 76; Kent Konseyi Yön. md. 12 | Semt meclisi pilotu: 4–8 mahalle, muhtarlar + kurayla seçilen sakinler + semt donatısı temsilcileri; semt donatı ve hizmet planı; pilot bütçe | O–Z (ampirik); G (normatif) | 1 |
| B4 | Kanun | 5393 (yeni md. 9/A), 41 | Semtin kanuni tanımı (tüzel kişiliği olmayan hizmet ve katılım birimi); arsa değer vergisinin %25'i semt, %15'i mahalle bütçesine | N; H | 3 |

### 1.2 Sürüm 1'den genişletilen öneriler (3)

| # | Sürüm 1 | Sürüm 2'de eklenen |
|---|---|---|
| I3 | Değer artış payı gelirinin bir kısmı aile ve çocuk donatısına | Bu kısım **plan değişikliğinin yapıldığı semtin** donatı hesabına gider; öncelik semt meclisinin önerisiyle (I5, B4) |
| K2 | Meskende küçük gündüz bakımevi ve ev-atölye için oybirliği yerine nitelikli çoğunluk (634 md. 24) | Mahalle karma alanındaki (M5) zemin kat bağımsız bölümde dükkân, kuaför, terzi ve atölye için de kat malikleri kurulunun üçte iki çoğunluğu |
| B1 | Mahalle meclisi; belediye yatırım bütçesinin %3'ü pilot mahallelere | Kalıcı düzende mahalle bütçesinin kaynağı arsa değer vergisinin %15'i (B4); mahalle meclisleri semt meclisine kurayla üye verir (B3) |

### 1.3 Sürüm 1'deki diğer 25 öneri

Değişmedi: P1–P5, M1–M4, O1–O3, I1, I2, I4, D1–D3, K1, B2, T1, G1, F1–F3. Tam liste ve metinler [sürüm 1 §"Paketin özeti"](degisiklik_paketi_v1.md#paketin-özeti-28-öneri).

### 1.4 Rapor 20'nin diğer seçeneklerinden yeni öneriler (12)

Araştırma notundaki aday kodları parantez içinde. Yeni harfler sürüm 1'deki T1 (TOKİ) ve G1 (Genelge) kodlarıyla karışmasın diye seçildi.

| # | Araç | Mevzuat ve madde | Öneri (kısa) | Kanıt | Öncelik |
|---|---|---|---|---|---|
| S1 (V4-a) | Cumhurbaşkanı kararı | GVK Geçici md. 67/17 | Bir yıldan kısa tutulan pay senedi ve pay senedi yoğun fon kazancına kanuni oran (%15); uzun vadede bugünkü düşük oran korunur | G (tutar); O (etki) | 2 |
| S2 (V4-b) | Cumhurbaşkanı kararı | GVK md. 22/3, 22/5 | Temettü yarım istisnasının oranının kademeli düşürülmesi | G (tutar); O | 2 |
| S3 (V4-c) | Kanun | GVK Geçici md. 67 | Vadesi bir yıldan uzun TL mevduat ve devlet tahvilinde stopaj matrahından enflasyon payının düşülmesi (reel getiri vergisi) | O; H (Rapor 20) | 3 |
| A1 (G1-a) | İdari ve bütçe | 3294 md. 1–2 | Genel tüketim vergisi indirimleri yerine aynı bütçeyle gelir testli düzenli nakit destek | H (Rapor 20 S5) | 2 |
| A2 (G2-a) | Kanun | 5510 Ek md. 19 | En düşük emekli aylığında sabit TL tutarı yerine "gösterge × memur aylık katsayısı" (65 yaş aylığındaki gibi) | N; H | 3 |
| A3 (G2-b) | Yönetmelik | 4857 md. 39 | Asgari ücret kararının ölçütleriyle gerekçeli yayımı | N | 2 |
| C1 (T5-a) | Kanun | GVK md. 46–48, mük. md. 20/A | Basit usulden çıkışta iki yıllık geçiş: sadeleştirilmiş defter ve indirimli oran | O (literatür) | 3 |
| C2 (T6-a) | İdari | 6197 md. 5; 5216 md. 7/1-f; 6585 md. 13 | Eczane, taksi ve çalışma saati kotalarının rekabet etkisi açısından gözden geçirilmesi | O (OECD PMR) | 2 |
| C3 (T4-a) | İdari | 6585 md. 14; 4054 md. 4–5 | Esnaf ortak alım rehberi: ortak alım ve lojistik serbest, ortak satış fiyatı yasak | Z | 2 |
| C4 (T3-a) | Belediye, semt meclisi | 5957 md. 7/2 | Semt pazarında üreticiye ayrılan en az %20 payın yıllık izlenmesi | Z–O | 1 |
| Y1 (Y1-a) | Cumhurbaşkanı kararı | 5957 md. 8/1 | Üreticiden doğrudan il içi perakendeye satışta hal rüsumunun %2'den %0,2'ye indirilmesi | O; N | 1 |
| Y2 (Y2-a) | İdari | 5488 md. 7 | Stratejik ürünlerde üretim izni ve kotası yerine havza bazlı fark ödemesi ve sözleşmeli üretim | O; N | 2 |

---

## 2. Arsa değer vergisi (1319, 3065, 5779)

**Künyeler [D]:**

- 1319 sayılı Emlak Vergisi Kanunu: RG 11.08.1970, sayı 13576. Okunan metin: `03_VERI/ham/ekonomi/vergi/mevzuat_1319_emlak_vergisi_kanunu.pdf`, mevzuat.gov.tr, 7566 sayılı Kanun değişiklikleri dahil.
- 3065 sayılı Katma Değer Vergisi Kanunu: RG 02.11.1984, sayı 18563.
- 5779 sayılı İl Özel İdarelerine ve Belediyelere Genel Bütçe Vergi Gelirlerinden Pay Verilmesi Hakkında Kanun: RG 15.07.2008, sayı 26937.

### E1 · Bölünmüş oran: arsa vergilenir, yapı vergiden çıkar (md. 8, 18, 29)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **md. 8:** Bina vergisi meskende binde 1, diğer binalarda binde 2. Büyükşehir sınırları ve mücavir alanda %100 artırımlı. Cumhurbaşkanı oranları yarısına indirebilir ya da üç katına çıkarabilir.<br>**md. 18:** Arazi binde 1, arsa binde 3; aynı artırım ve yetki.<br>**md. 29:** Arsa vergi değeri, takdir komisyonlarının cadde ve sokak bazında belirlediği asgari birim değerlerle bulunur. Bina vergi değeri, bina m² normal inşaat maliyeti ile "arsa veya arsa payı değeri" esas alınarak hesaplanır. Vergi değeri her yıl yeniden değerleme oranında artırılır (7566 sayılı Kanunla oranın yarısından tamamına). **Yani bina vergisinin matrahı zaten arsa payı ve yapı olarak iki parçadan oluşuyor.** |
| **Sorun** | **Yapı vergileniyor:** Bina vergisi yapıyı da vergiliyor; binayı yapmak ve bakımlı tutmak cezalandırılıyor.<br>**Arsa çok düşük vergileniyor:** Arsa değeri düşük matrahla ve düşük oranla vergileniyor.<br>**Rant kamuya dönmüyor:** İmar ve altyapının yarattığı değer artışı yıllık vergiyle kamuya dönmüyor. Değer artış payı (3194 Ek md. 8) yalnız plan değişikliği anında ve parsel bazında işliyor.<br>**Sonuç:** Toplam emlak vergisi 56,5 milyar TL, GSYH'nin %0,09'u (2025) [D/H]. |
| **Önerilen metin** | md. 8'e fıkra: "Bina vergi değerinin 29 uncu maddeye göre arsa veya arsa payına isabet eden kısmı (arsa payı değeri) ile yapıya isabet eden kısmı (yapı değeri) tahakkukta ayrı gösterilir. Arsa payı değerine 18 inci maddede arsalar için belirlenen oran uygulanır. Yapı değerine uygulanan oran, bu fıkranın yürürlüğe girdiği yılı izleyen beş yıl içinde her yıl eşit adımlarla sıfıra indirilir."<br>md. 18'e fıkra: "Arsa vergisinin oranı, kanunun belirlediği alt ve üst sınırlar içinde, belediye grupları itibarıyla farklı olarak Cumhurbaşkanınca belirlenir. Toplam hasılat hedefi gayrisafi yurt içi hasılanın binde beşidir." |
| **Neden oran bandı?** | Anayasa md. 73: "Vergi, resim, harç ve benzeri mali yükümlülükler kanunla konulur", oranlarda "kanunun belirttiği yukarı ve aşağı sınırlar içinde değişiklik yapmak yetkisi Cumhurbaşkanına verilebilir" [D]. Belediye meclisine oran yetkisi bu yüzden önerilmiyor. Belediye grupları itibarıyla farklılaştırma md. 29'da zaten var (2464 sayılı Kanun md. 95 grupları) [D]. Bandın sayısal sınırları, ülke arsa değeri stoku bilinmediği için E2 pilotundan sonra belirlenmeli [DY]. |
| **Beklenen etki [H]** | **Hasılat:** Hedef GSYH'nin %0,5'i, yani 315,1 milyar TL (2025). Bugünkü emlak vergisinin 5,6 katı; kişi başı yılda 656 TL yerine 3.660 TL.<br>**Arazi kullanımı:** Yapının vergiden çıkması yapım ve yenilemeyi ucuzlatır. Boş ve az kullanılan merkezi arsanın elde tutma maliyeti artar [İ, literatür; Türkiye'de ölçülmedi].<br>**Dağılım:** E3 ve E4 ile birlikte (Rapor 20 S3C tasarımı): en yoksul %20 gelirinin %0,5–0,9'u kadar kazanır, en zengin %20 %0,2–0,4'ü kadar öder. Pakete işlenen kuralla (C): %0,54 kazanç ve %0,40 yük. Aralık üç denge tanımından geliyor (bkz. E4). |
| **Kazanan / kaybeden** | **Kazanan:** tüketiciler, yapı yapan ve yenileyen malikler, kiracılar (KDV indirimiyle), değeri düşük arsalardaki haneler.<br>**Kaybeden:** büyük ve merkezi arsa sahipleri; boş tutulan arsalar.<br>**Riskler:**<br>- Arsa fiyatında bir kerelik düşüş: kademeli geçiş bunu yayar.<br>- Değerleme hatası (E2).<br>- Ev sahibi emeklinin nakit sıkıntısı (E3). |
| **Araç** | TBMM: 1319 değişikliği (öncelik 3). Bakanlık: Hazine ve Maliye, Çevre, Şehircilik ve İklim Değişikliği |

### E2 · Değerleme: piyasa değerine yakın, açık ve yıllık (md. 29, 31)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **md. 29:** Asgari birim değerleri VUK mükerrer md. 49'a göre takdir komisyonları belirliyor; aradaki yıllarda değerler yeniden değerleme oranıyla artırılıyor. Cumhurbaşkanı bu artışı sıfıra kadar indirebilir.<br>**md. 31:** Vergi değerinin takdirinde dikkate alınacak normlar (piyasa bedeli, maliyet bedeli, kira, yıllık istihsal değeri) Cumhurbaşkanınca çıkarılan yönetmelikte belirtilir.<br>**Geçici md. 23 (7566 sayılı Kanun):** 2026 vergi değerleri 2025 değerlerinin iki katını geçemez; 2027–2029 bu değerler üzerinden hesaplanır. |
| **Sorun** | **Takdir kaba:** Asgari birim değer cadde ve sokak bazında belirleniyor ve en az dört yılda bir yenileniyor.<br>**Piyasa değeriyle bağ yok:** Matrahın piyasa değerine oranı için resmî bir ölçüm yok [DY, Rapor 20 §2.4]. 2026 için konan iki kat sınırı, değerlerin piyasanın gerisinde kaldığının işareti.<br>**Değerleme sistemleri kopuk:** Değer artış payında ise 6362 sayılı Kanuna göre lisanslı iki değerleme kuruluşunun raporu kullanılıyor (3194 Ek md. 8) [D]. Aynı parsel için iki ayrı değerleme sistemi var. |
| **Önerilen metin** | md. 31 yönetmeliğine: "Asgari ölçüde birim değerler parsel bazında, piyasa satış bedelleri ve lisanslı değerleme raporları esas alınarak her yıl güncellenir ve kamuya açık değer haritasında yayımlanır. Mükellef, değer haritasındaki değere mahalle muhtarlığı veya belediye aracılığıyla itiraz edebilir. İtiraz takdir komisyonunca altmış gün içinde karara bağlanır."<br>Kanun düzeyinde: md. 29'daki dört yıllık takdir yerine yıllık güncelleme; Geçici md. 23'ün süresi 2029'da dolarken yeni değerlemeye geçiş. |
| **Pilot (öncelik 2)** | 2027–2028'de üç pilot ilçede (Faz 3 pilotlarından, örneğin Kocasinan, Meram, Nilüfer) değer haritası:<br>- tapu satış bedelleri,<br>- değer artış payı değerleme raporları,<br>- emlak vergisi matrahının piyasa değerine oranının ilk ölçümü.<br>Arsa değer vergisinin oran bandı bu pilotun sonucuna göre belirlenir. |
| **Beklenen etki** | Doğru matrah, E1'in hem hasılatının hem adaletinin ön şartı. Rapor 21 kademe tablosuna göre değer haritası bölge kademesinde tutulur, itiraz noktası mahallede kurulur |
| **Risk** | **Kapasite:** Değerleme kapasitesi zayıf. Bu yüzden önce pilot.<br>**Fiyat şoku:** İlk yıl matrah sıçrayabilir. Önlem: E1 geçişiyle birlikte yıllık artış sınırı.<br>**Kişisel veri:** Satış bedellerinin parsel bazında yayımı kişisel veri sorunu doğurur. Önlem: haritada değer bandı gösterilir, işlem bedeli gösterilmez. |
| **Araç** | Hazine ve Maliye Bakanlığı (yönetmelik; VUK takdir komisyonları), TKGM, belediyeler. TKGM'nin taşınmaz değerleme altyapısının bugünkü durumu bu çalışmada doğrulanmadı [DY] |

### E3 · Korumalar: tek konut muafiyeti ve erteleme (md. 8/2, 30)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **md. 8/2:** Cumhurbaşkanı aşağıdakilerin Türkiye'deki brüt 200 m²'yi geçmeyen tek meskeninin vergi oranını sıfıra kadar indirebilir:<br>- hiçbir geliri olmayanlar,<br>- geliri yalnız sosyal güvenlik kurumundan aldığı aylık olanlar,<br>- gaziler, engelliler, şehitlerin dul ve yetimleri.<br>**md. 30:** Kanunla tasarrufu kısıtlanan taşınmazın vergisi 1/10 oranında tahsil edilir. Tecil edilen 9/10'u satış, istimlak veya devirde muaccel olur. **Tapuda bekleyen vergi mekanizması kanunda zaten var.** |
| **Sorun** | Rapor 20'nin hesabı: arsa değer vergisi yalnız konut arsasına konsa, KDV indirimine rağmen en yoksul %20 gelirinin %0,46'sı kadar ek yük taşır (S3A) [H]. Türkiye'de yoksul hanelerin önemli kısmı ev sahibi. Emekli malikin geliri düşük, arsası değerli olabilir |
| **Önerilen metin** | md. 8/2'ye ek: "Hane gelirine göre en düşük iki beşte birlik dilimde bulunan hanelerin Türkiye'deki tek meskeninin arsa payı değeri vergiden müstesnadır. Hane geliri Gelir İdaresi ve Sosyal Güvenlik Kurumu kayıtlarından tespit edilir."<br>Yeni fıkra: "65 yaşını doldurmuş malikler ile 8 inci maddenin ikinci fıkrasında sayılanlar, tek meskenlerine ait arsa vergisinin ertelenmesini isteyebilir. Ertelenen vergi tapu kütüğüne şerh edilir ve Tüketici Fiyat Endeksindeki değişimle güncellenerek taşınmazın satışı, devri veya intikalinde ödenir." |
| **Beklenen etki [H]** | S3C tasarımı (konut + işletme arsası, alt iki dilimde tek konut muaf), E4 ile birlikte:<br>- en yoksul %20 gelirinin %0,90'ı (A), %0,62'si (B) ya da %0,54'ü (C, pakete işlenen) kadar kazanır;<br>- ikinci %20 %0,87, %0,60 ya da %0,52 kazanır;<br>- üst üç dilim %0,07–0,40 öder (C'de %0,39–0,40).<br>Kaynak: `politika_v2/avd_gecis.csv` |
| **Risk** | **Kayıt:** Hane gelirinin kayıtla tespiti, kayıt dışı gelir yüzünden kusurlu (Rapor 20 §3.3: istihdamın %25,5'i kayıt dışı). Muafiyet yanlış kişilere gidebilir.<br>**Hasılat kaybı:** Erteleme hasılatı geciktirir; yaşlı nüfus arttıkça payı büyür. |
| **Araç** | TBMM: 1319 değişikliği (E1 ile aynı pakette) |

### E4 · KDV genel oranının arsa değer vergisi kadar indirilmesi (3065 md. 28)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 28: KDV oranı %10. Cumhurbaşkanı bu oranı dört katına kadar artırmaya, %1'e kadar indirmeye ve mal, hizmet ve konut teslimleri için farklı oranlar belirlemeye yetkili. Genel oran bugün %20 (Cumhurbaşkanı kararı) [D, Rapor 20 §2.2]. **Mevcut yetkiyle yapılabilir** |
| **Önerilen kural** | "Genel KDV oranı her yıl, bir önceki yıl 5779 sayılı Kanun uyarınca merkezi paydan mahsup edilen arsa değer vergisi tutarı (tahsilatın %90'ı, E5) kadar KDV hasılatını azaltacak ölçüde indirilir." Cumhurbaşkanı kararı; Orta Vadeli Programda ilan edilir |
| **Geçiş yolu [H]** | Arsa değer vergisi GSYH'nin %0,1'inden başlayıp her yıl 0,1 puan artarak 2033'te %0,5'e çıkar [V]. Pakete işlenen kuralla (C) genel KDV oranı:<br><br>2029: %0,1 · KDV %19,4<br>2030: %0,2 · %18,8<br>2031: %0,3 · %18,2<br>2032: %0,4 · %17,7<br>2033: %0,5 · %17,1 |
| **İki denge tanımı** | **A · hanehalkı-nötr** (Rapor 20'deki hesap): Hanehalkının KDV kaybı arsa değer vergisine eşit. Oran %15,7'ye iner. Hanehalkı dışındaki KDV de düştüğü için merkezi bütçe yaklaşık 105 milyar TL kaybeder [H/V].<br>**B · toplam-nötr**: Toplam KDV kaybı arsa değer vergisine eşit; hanehalkı dışı KDV'nin payı %25 varsayıldı [V]. Oran %16,8'e iner. Hanehalkının net yükü 78,8 milyar TL artar, bu tutar hanehalkı dışı KDV indirimine gider.<br>**C · pakete işlenen kural** (B + belediyeye %10): Toplam KDV kaybı mahsup edilen tutara (arsa vergisinin %90'ı) eşit. Oran %17,1'e iner.<br>- **Merkez:** Nötr kalır.<br>- **Belediye:** Yılda ≈ 31,5 milyar TL'yi tutar (≈ 210 bin kişilik şehirde ≈ 76 milyon TL).<br>- **Hanehalkı:** Net yükü 102,4 milyar TL artar. KDV kazancı B'ye göre %10 azalır: en yoksul %20 gelirinin %0,54'ü kadar kazanır (B'de %0,62), üst üç dilim %0,39–0,40 öder.<br>**Öneri: kural C.** Merkez için mali disiplini korur, tahsil eden belediyeyi uygulamaya bağlar (Rapor 24). A, hanehalkı için üst sınırdır |
| **Risk** | **Fiyata yansıma:** KDV indirimi fiyata tam yansımayabilir; hızlı tüketimde ilk dört zincirin payı %59 [D, Rapor 20]. Önlem: Rekabet Kurumu fiyat izlemesi.<br>**Tersine dönme:** Gelir ihtiyacında oranın yeniden yükselmesi. Önlem: kural kanuna yazılır. |
| **Araç** | Cumhurbaşkanı kararı (öncelik 2; E1'in yürürlüğüne bağlı) |

### E5 · Mali denkleştirme: arsa değer vergisinin %90'ı merkezi paydan mahsup, %10'u belediyede (5779 md. 2)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **md. 2/2:** Genel bütçe vergi gelirleri tahsilatının %1,50'si büyükşehir dışındaki belediyelere, %4,50'si büyükşehirlerdeki ilçe belediyelerine, %0,5'i il özel idarelerine ayrılır.<br>**md. 2/3:** Büyükşehir belediyelerine ayrıca kendi sınırları içindeki tahsilatın %6'sı ve ilçe paylarının %30'u ayrılır.<br>**md. 2/4:** Cumhurbaşkanı bu oranları iki katına kadar artırabilir **ya da kanuni haddine kadar indirebilir**; yani kanundaki oranın altına inemez.<br>**Tutar (2025):** Merkezi vergi payları 1.239 milyar TL; mahalli idare gelirinin %57,2'si [D/H, Rapor 20]. |
| **Sorun** | Emlak vergisi belediyenin geliri; KDV merkezin. Arsa değer vergisi belediyede kalır, KDV indirimi merkezi bütçeyi azaltır. İkisini dengelemenin yolu merkezi payın azalması.<br>**Tam mahsubun sorunu:** Belediyeyi "vergiyi toplayan ama parayı tutamayan" taraf yapıyor. Paydaş oyununda (Rapor 24) belediye bu tasarımda her öneri grubunda dirençli çıktı.<br>**Hesap [H]:** Arsa değer vergisi bugünkü merkezi payların %25,4'ü; %90'ı ise %22,9'u. Bu kadar indirim mevcut Cumhurbaşkanı yetkisiyle yapılamaz, kanun ister |
| **Önerilen metin** | md. 2'ye fıkra: "Belediyelere (2) ve (3) numaralı fıkralara göre ayrılan paylardan, ilgili belediyenin bir önceki yıl tahsil ettiği arsa değer vergisinin yapı değeri üzerindeki vergiyi aşan kısmının **yüzde doksanı** mahsup edilir. Mahsup edilmeyen kısım belediyenin genel bütçe geliridir. Mahsup sonrası kişi başı pay, aynı gruptaki belediyelerin kişi başı ortalama payının yüzde sekseninin altına düşemez." |
| **Beklenen etki [H]** | **Belediyeye kalan:** Tam geçişte yılda ≈ 31,5 milyar TL (kişi başı 366 TL; ≈ 210 bin kişilik şehirde ≈ 76 milyon TL).<br>**Merkez:** Nötr, çünkü KDV indirimi mahsup edilen tutarla sınırlı (E4, kural C).<br>**Paydaş oyunu:** Çekirdek paketin (arsa vergisi + karma kullanım + semt) desteği +0,24'ten +0,32'ye çıkıyor; güçlü paydaşların hiçbirinde engel ya da direnç kalmıyor (`paydas_destek.csv`, P6) |
| **Ödünleşim** | **Mahsup hiç olmasaydı:** Belediyeler güçlenir ama KDV indirimi finanse edilemez. Mali nötrlük yerine yerelleşme seçilmiş olur.<br>**Tam mahsup (%100) olsaydı:** Merkez ve hanehalkı biraz daha kazanır (KDV %16,8), ama uygulayıcı belediye dirençli kalır.<br>**%10'u merkez üstlenseydi (KDV %16,8 korunarak):** Merkez yılda ≈ 31,5 milyar TL kaybeder. Temettü önerisi (S2, ≈ 28,9 milyar TL) bu açığı kapatır, ama varlıklı malik dirence geçer (Rapor 24, P4–P5).<br>**Eşitleme tabanı (%80) [V]:** Arsa değeri düşük kentleri korur. Ama arsa değeri yüksek kentlerin vergi toplama güdüsünü kısmen zayıflatır. |
| **Araç** | TBMM: 5779 değişikliği (öncelik 3; E1 ile aynı pakette) |

---

## 3. Karma kullanım: mahallede dükkân ve atölye (PAİY, Otopark, MPYY, 3194, ruhsat)

**Künyeler [D]:**

- PAİY: RG 03.07.2017, 30113; 13.08.2025 değişikliği dahil.
- MPYY: RG 14.06.2014, 29030.
- Otopark Yönetmeliği: RG 22.02.2018, 30340.
- İşyeri Açma ve Çalışma Ruhsatlarına İlişkin Yönetmelik: Bakanlar Kurulu Kararı 14.07.2005, 2005/9207; RG 10.08.2005, 25902.

Okunan metinler: `03_VERI/ham/ekonomi/ticaret_tarim/mevzuat_*.pdf` (mevzuat.gov.tr) ve sürüm 1 §13.1.

### P6 · Mahalle işyeri kendiliğinden serbest (PAİY md. 19/1-f)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **md. 19/1-f-1:** Konut alanında zemin kat dükkânı yalnız şu şartlar birlikte sağlanınca açılabiliyor:<br>- "İlgili idare meclisince yol boyu ticaret olarak teşekkül ettiği karar altına alınan" konut alanlarında,<br>- yoldan cephe alan zemin kat ve bodrum mekânlarında,<br>- "getirilecek kullanıma ilişkin otopark ihtiyacını karşılamak kaydıyla",<br>- gürültü ve kirlilik oluşturmayan, imalathane ve gayrisıhhi nitelikte olmayan işler.<br>İzin verilen türler: dükkân, kuaför, terzi, eczane, sağlık kabini, muayenehane, lokanta, pastane.<br>**md. 19/1-f-2:** Bunların dışındaki özel sağlık tesisi için plan değişikliği gerekiyor.<br>**md. 19/1-f-5 ve 6 (RG 13.08.2025):** 150 bağımsız bölümü aşan konut projelerinde gündüz bakımevi, 250'yi aşan konut + ticaret projelerinde aile sağlığı merkezi alanı zorunlu. |
| **Sorun** | **İzin varsayılan olarak kapalı.** Ölçüt "teşekkül etmiş" olmak; yani ticaret ancak kendiliğinden oluştuktan sonra tanınıyor. Yeni mahallede ticaret kendiliğinden doğamıyor.<br>**Otopark şartı küçük işyerini durduruyor** (O4).<br>**Küçük üretim dışarıda:** Terzi, tamir ve el sanatı atölyesi "imalathane niteliğinde" sayılırsa izin dışı kalıyor. |
| **Önerilen metin** | md. 19/1-f'ye alt bent: "8) Uygulama imar planında aksi belirtilmedikçe konut alanlarında; meydana, yaya yoluna veya plan notuyla 'mahalle ticaret cephesi' olarak belirlenen yollara cepheli parsellerin zemin kat ve yoldan cephe alan bodrum katlarında, bağımsız bölüm başına kullanım alanı 150 m²'yi geçmemek, gürültü ve koku yaymamak ve gayrisıhhi müessese niteliği taşımamak kaydıyla (1) numaralı alt bentte sayılan kullanımlar ile kreş, kütüphane, büro ve kişisel hizmet atölyeleri (terzi, tamir, el sanatı) meclis kararı aranmaksızın yer alabilir. Belediye meclisi gerekçeli kararla belirli yolları bu hükmün dışında tutabilir veya saat sınırı getirebilir." |
| **Beklenen etki [H]** | **Model mahalle v2.1:**<br>- 213 zemin kat konut dışı birim (≈ 70 m²) var.<br>- Bugün her biri için meclis kararı ve toplam 298 otopark yeri gerekiyor.<br>- Öneriyle (O4 ile birlikte) ikisi de kalkıyor.<br>- Konutların %100'ü bakkal, fırın ya da dükkâna 300 m içinde, ama ancak bu birimler açılabilirse (metrikler).<br>**Ulusal:** Mahalle başına yılda ≈ 26 esnaf açılışı oluyor (Rapor 20 kademe tablosu). Bunların açılacağı yer bu kurala bağlı. |
| **Kazanan / kaybeden** | **Kazanan:** küçük esnaf, ev-atölye, yürüyerek alışveriş yapan sakin, yaşlı ve çocuk.<br>**Riskler:**<br>- Gürültü, gece kullanımı, teslimat trafiği. Önlem: koku ve gürültü kısıtı, meclisin saat ve sokak istisnası.<br>- Zincir marketin mahalleye yayılması. Önlem: 150 m² sınırı küçük ölçeği kayırır.<br>- Rapor 12 dersi: Arz tek başına ticareti canlandırmaz; model mahallede birim sayısı esnaf talebinin üstünde. |
| **Araç** | ÇŞİDB: PAİY değişikliği (öncelik 1) |

### O4 · Küçük mahalle işyerine otopark muafiyeti (Otopark Yön. Ek-1)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **Ek-1:** Dükkân için 50 m²'ye 1 otopark.<br>**md. 12(11):** Otopark bedeli (A + B) × 20 × Y. B, Yapı Yaklaşık Birim Maliyetleri Tebliğindeki otopark birim fiyatı (III.A 19.800 TL/m²).<br>**PAİY md. 19/1-f-1:** Konut alanındaki işyeri ancak otopark ihtiyacını karşılarsa açılabilir.<br>**Sürüm 1, M6 reformu:** Ticari ihtiyacı 100 m²'ye 1 olarak hesaplamıştı. |
| **Sorun [H]** | 70 m²'lik zemin kat dükkânı 1,4 otopark yeri ister.<br>- **Bedelle karşılanırsa:** 638 bin TL (A = 3.000 TL/m² [V, M6]); dükkânın değerinin Türkiye ortalama fiyatında %17,2'si, İstanbul fiyatında %11,4'ü.<br>- **Bodrumda karşılanırsa:** 842 bin TL; değerin %15,1–22,6'sı.<br>- **Model mahallede:** 213 birim için 298 yer, 136–179 milyon TL.<br>Mahalle dükkânının müşterisi ise yürüyerek geliyor. |
| **Önerilen metin** | Ek-1 "Dükkân" satırına not: "Konut alanlarında ve mahalle karma alanlarında, zemin kat ile yoldan cephe alan bodrum katta bulunan ve bağımsız bölüm başına kullanım alanı 100 m²'yi geçmeyen işyerleri için otopark ihtiyacı aranmaz. 100 m²'yi aşan kısım için her 50 m²'ye 1 otopark ayrılır." md. 8'e: "Mahalle ticaret cephelerinde yükleme ve boşaltma cebi yol projesinde gösterilir." |
| **Beklenen etki** | Küçük işyerinin açılış maliyetinden birim değerinin %11–23'ü kadar yük kalkar [H]. Bedel gelirindeki kayıp küçük: otopark bedeli tahsilatı 2025'te 5,6 milyar TL; bunun ne kadarının küçük işyerinden geldiği bilinmiyor [DY] |
| **Risk** | Sokakta park baskısı. Sürüm 1'deki O2 (bölgesel otopark) ve trafik sakinleştirme (G1 ölçüt 19) birlikte uygulanmalı |
| **Araç** | ÇŞİDB: Otopark Yönetmeliği değişikliği (öncelik 1; O1–O2 ile aynı taslak) |

### M5 · Mahalle karma alanı (MPYY md. 21/10, 24/9)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **md. 21/10:** Ticaret + Konut, Ticaret + Turizm + Konut ve Turizm + Ticaret karma kullanım alanlarında konuta yer verilirse konut oranı belirtilir ve donatı ayrılır. "Konut kullanım oranının belirtilmediği hallerde en fazla %30 konut kullanabileceği varsayılır."<br>**md. 24/9:** "Nazım imar planlarında karma kullanım olarak belirlenen fonksiyonların, uygulama imar planlarında **ayrıştırılması esastır**." |
| **Sorun** | Mevzuatın yönü ayrıştırma. Karma kullanım ancak ticaret ağırlıklı (en fazla %30 konut) bir kategori olarak var. "Çoğu konut, zemin katı ticaret" olan geleneksel mahalle dokusunun plan dilinde karşılığı yok |
| **Önerilen metin** | md. 21/10'a cümle: "Konut alanlarında zemin ve yoldan cephe alan bodrum katlarda konut dışı kullanımlara izin veren 'mahalle karma alanı' belirlenebilir. Bu alanlarda konut kullanım oranı en az %70'tir ve sosyal altyapı konut nüfusuna göre ayrılır."<br>md. 24/9: "…uygulama imar planlarında ayrıştırılabilir. Mahalle ve semt merkezlerinde, meydanlarda ve ana yaya akslarında karma kullanım uygulama imar planında korunur."<br>Plan gösterim ekine yeni kullanım lejantı ("Mahalle karma alanı") [ekin güncel hâli DY]. |
| **Beklenen etki** | Rapor 21'in donatı merdivenindeki "çarşı" (mahalle) ve "semt merkezi" plan kararıyla kurulabilir hâle gelir. Model mahalle v2.1'in T4 çevre adaları (212 konut, zeminde dükkân) bu kategoriye girer |
| **Araç** | ÇŞİDB: MPYY değişikliği (öncelik 1; M1–M4 ile aynı taslak) |

### I5 · Değer artış payı: çift alımı önleme ve yerinde harcama (3194 Ek md. 8)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **Ek md. 8/2:** Fonksiyon değişikliği hariç, parsel bazında yoğunluk ve kat artıran plan değişikliği yapılamaz. 7534 sayılı Kanunla (05.12.2024) eklenen cümle: "bir fonksiyon, parsel bazında konut kullanımına dönüştürülemez."<br>**Ek md. 8/3:** Ada bazında değişiklikte gereken donatı adanın merkezine en fazla 500 m içinde karşılanır.<br>**Ek md. 8/4:** Bütün maliklerin talebiyle parsel bazında fonksiyon değişikliğinde ve ada bazındaki değişikliklerde değer artışının %90'ı değer artış payı olarak alınır.<br>**Gelirin dağılımı:**<br>- Büyükşehirli illerde %25 büyükşehir, %25 ilçe belediyesi, %25 6306 Dönüşüm Projeleri Özel Hesabı, kalan %25 genel bütçe.<br>- Diğer illerde %40 planı onaylayan idare, %30 dönüşüm hesabı, kalan %30 genel bütçe.<br>- Bakanlık onaylı planlarda %75 dönüşüm hesabı. |
| **Sorun** | **Değer artış payı riski:** Konut alanında zemin kat ticarete izin veren ada bazlı değişiklik "fonksiyon değişikliği" sayılırsa değer artışının %90'ı alınır. Uygulamanın böyle olup olmadığı bu çalışmada doğrulanmadı [DY, yorum]. Böyle uygulanıyorsa mahalle karma alanı (M5) küçük esnafa ağır bir giriş bedeli yükler.<br>**Para ile mekân kopuk:** Donatının 500 m içinde karşılanması isteniyor (Ek md. 8/3), ama değer artış payı gelirinin değişikliğin yapıldığı yerde harcanma zorunluluğu yok. |
| **Önerilen metin** | Ek md. 8'e fıkra: "Emsal ve kat adedi artırılmaksızın konut alanlarında zemin ve yoldan cephe alan bodrum katlarda konut dışı kullanıma izin veren mahalle karma alanı kararlarında değer artış payı alınmaz."<br>(a) ve (b) bentlerine: "İlçe belediyesine veya planı onaylayan idareye aktarılan tutarın en az yarısı, plan değişikliğinin yapıldığı semtin donatı hesabına kaydedilir ve semt meclisinin önerisiyle kullanılır." Sürüm 1'deki I3'ün yerinde harcama biçimi. |
| **Gerekçe** | Arsa değer vergisi (E1) yürürlükteyse zemin kat kullanımının yarattığı değer artışı her yıl vergileniyor. Ayrıca %90 değer artış payı almak çift alım olur [N] |
| **Araç** | TBMM: 3194 değişikliği (öncelik 3; I2–I4 ile aynı pakette) |

### R1 · Mahalle işyeri için tek başvuru (İşyeri Açma ve Çalışma Ruhsatlarına İlişkin Yönetmelik)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **md. 12:** Sıhhi işyeri başvurusu Yönetmeliğe uygunsa "başkaca bir işleme gerek kalmaksızın" ruhsat aynı gün verilir. Başvuruda Yönetmelikte sayılanlar dışında belge istenemez. İlgilinin beyanına göre düzenlenen ruhsat müktesep hak doğurmaz.<br>2. ve 3. sınıf gayrisıhhi müesseseler için süre 5 gün [D, Rapor 20]. |
| **Sorun** | Kâğıt üstündeki süre kısa. Asıl gecikme ruhsattan önce: imar durumu, kullanım değişikliği tadilatı, yapı kullanma izni, itfaiye raporu ve kat maliklerinin oybirliği (634 md. 24). Başvurudan açılışa geçen gerçek süre ölçülmüyor [DY]. Türkiye OECD PMR'de idari yükte en kısıtlayıcı ülke (2,93; OECD 1,74) [D] |
| **Öneri** | 1. P6 kapsamındaki işyeri için imar uygunluğu e-imar verisinden otomatik doğrulanır.<br>2. 150 m²'nin altında itfaiye uygunluğu öz beyanla alınır, 30 gün içinde yerinde denetlenir.<br>3. Ruhsat e-Devlet'te tek başvuruyla aynı gün verilir.<br>4. Belediyeler başvurudan açılışa geçen süreyi yıllık yayımlar. |
| **Araç** | Yönetmelik değişikliği (dayanağı 1593, 2559, 3572, 5393 sayılı kanunlar vd. [D]; Ticaret ve İçişleri Bakanlıkları); öncelik 2 |

---

## 4. Semt yönetişimi (5393, Kent Konseyi Yönetmeliği)

**Künyeler:**

- 5393 sayılı Belediye Kanunu: RG 13.07.2005, 25874 [D].
- Kent Konseyi Yönetmeliği: RG 08.10.2006, 26313. Okunan metin RG'deki ilk metin; sonraki değişiklikler bu çalışmada kontrol edilmedi [K].

### B3 · Semt meclisi pilotu (mevcut yetki)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm** | **5393 [D]:**<br>- "Semt" kanunda hiç geçmiyor. İdari birim mahalle (md. 9).<br>- Belediye meclisi mahalle kurar, birleştirir, sınırlarını belirler (md. 18/n). Stratejik planı, yatırım programını ve bütçeyi kabul eder (md. 18/a, b).<br>- Kent konseyinin görüşleri meclisin ilk toplantısında gündeme alınır (md. 76).<br>- Belediye gönüllü katılım programları uygular (md. 77).<br>**Kent Konseyi Yönetmeliği [K]:**<br>- Organlar genel kurul, yürütme kurulu, "meclisler ve çalışma grupları" (md. 9).<br>- "Kent konseyleri, görev alanına giren konularda meclis ve çalışma grupları oluşturabilir" (md. 12/1).<br>- Kent konseyinde muhtarlardan en fazla 10 temsilci bulunur (md. 8/1-f). |
| **Sorun** | Rapor 21'in donatı merdiveninde lise, poliklinik, kütüphane, haftalık pazar, itfaiye ve istihdam ofisi semt kademesinde (≈ 35 bin kişi). Bu kademede ne karar ne bütçe organı var. Mahalle meclisi (B1) bu donatılar için küçük, belediye meclisi ise uzak |
| **Önerilen karar** | **Belediye meclisi kararı** ve **kent konseyi genel kurul yönergesi**: "Belediye meclisi, birbirine komşu dört ila sekiz mahalleyi (yaklaşık 25–45 bin kişi) semt olarak belirler.<br>Her semtte kent konseyi bünyesinde bir semt meclisi kurulur. Üyeler:<br>- semtteki muhtarlar,<br>- her mahalle meclisinden (B1) kurayla belirlenen üçer üye,<br>- semtteki lise, aile sağlığı merkezi veya poliklinik ve halk kütüphanesinden birer temsilci,<br>- semt pazarı esnafından ve konut kooperatiflerinden birer temsilci.<br>Kurayla belirlenen üyelerde kadın, 18–29 yaş, 65 yaş üstü ve kiracı kotası uygulanır.<br>Meclis yılda en az dört kez toplanır, tutanakları açıktır. Semt donatı ve hizmet planını hazırlar.<br>Belediye yatırım bütçesinin %5'i pilot semtlere nüfusları oranında ayrılır. Kullanım önceliği semt meclisinin önerisiyle belirlenir. Belediye, uymadığı önerinin gerekçesini açıklar." |
| **Pilot** | 2027'de üç ilde birer semt. Sürüm 1'in mahalle pilotundaki (3 il × 3 mahalle) mahalleleri kapsayan semtler seçilir. Bir yıllık değerlendirmeyi bir üniversite yapar |
| **Beklenen etki** | **Ampirik kanıt [O–Z, İ]:** Katılımcı bütçe deneyimlerinde (Porto Alegre ve sonrası) yatırımların yoksul bölgelere ve temel hizmetlere kaydığı bulundu, ama etki tasarıma ve siyasi sahipliğe bağlı. Türkiye'de ölçülmedi.<br>**Normatif kanıt [G]:** Yerindelik ve katılım.<br>**Ölçülecekler:** katılım oranı, semt donatı açığındaki değişim (Rapor 21 kademe tablosuna göre), kurayla gelen üyelerin devamı. |
| **Risk** | **Siyasallaşma ve çatışma:** Siyasallaşma; muhtar, belediye ve semt meclisi arasında çatışma. Önlem: meclis danışma niteliğinde, kararı belediye meclisi verir.<br>**Temsil:** Toplantıya gelen azınlığın temsil sorunu. Önlem: kura ve kota.<br>**Sosyal baskı:** Önlem: açık tutanak ve gizli oyla öncelik sıralaması. |
| **Araç** | Belediye meclisi kararı (5393 md. 18); kent konseyi genel kurul yönergesi (Kent Konseyi Yön. md. 10/2, 12). Öncelik 1 |

### B4 · Semtin kanuni tanımı ve semt bütçesi (kanun)

| Başlık | İçerik |
|---|---|
| **Önerilen metin** | 5393'e md. 9/A: "(1) Semt, belediye meclisi kararıyla birbirine komşu mahallelerden oluşturulan, tüzel kişiliği olmayan hizmet planlama ve katılım birimidir. (2) Her semtte, usul ve esasları yönetmelikle belirlenen semt meclisi kurulur. Semt meclisi semt donatı ve hizmet planını hazırlar; plan, belediyenin stratejik planına ve yatırım programına (md. 41) dayanak olur. (3) Belediye, bir önceki yıl tahsil ettiği arsa değer vergisinin en az yüzde yirmi beşini semt bütçelerine, yüzde on beşini mahalle bütçelerine nüfus oranında ayırır. Bu bütçelerin kullanım önceliği semt ve mahalle meclislerinin önerisiyle belirlenir." |
| **Beklenen etki [H]** | 2025 fiyatlarıyla, arsa değer vergisi GSYH'nin %0,5'i olduğunda:<br>- **Semt bütçesi:** Kişi başı 915 TL/yıl; 35 bin kişilik semtte ≈ 32 milyon TL.<br>- **Mahalle bütçesi:** Kişi başı 549 TL/yıl; 6.900 kişilik mahallede ≈ 3,8 milyon TL.<br>- **Toplam:** İkisi mahalli idare toplam gelirinin %5,8'i.<br>- **Karşılaştırma:** Bugün bir mahallenin ödediği bütün emlak vergisi ≈ 4,5 milyon TL.<br>Kaynak: `politika_v2/yerel_kaynak.csv` |
| **Ödünleşim** | **Nüfus oranında dağıtım:** Zengin semtin topladığı vergiyi şehir içinde paylaştırır; ama "vergim mahalleme" bağını zayıflatır. Alternatif, tahsilat oranında dağıtım: bağ güçlenir ama eşitsizlik büyür. Öneri nüfus oranı.<br>**Ölçek:** Küçük bütçeler büyük yatırımı (lise binası) karşılamaz; semt bütçesi bakım, donatı küçük yatırımı ve hizmet için. Büyük yatırım belediye programında kalır.<br>**Kaynak:** Bu tutarlar belediye bütçesinden ayrılır; E5'le birlikte belediyenin toplam geliri artmaz, harcama kararı aşağı iner. |
| **Araç** | TBMM: 5393 değişikliği (öncelik 3); İçişleri Bakanlığı (yönetmelik) |

---

## 5. Rapor 20'nin diğer seçenekleri: vergi, gelir tabanı, esnaf, gıda zinciri

Dayanakların ayrıntısı ve madde alıntıları [araştırma notunda](arastirma_diger_secenekler.md). Künyeler [D]:

- 193 sayılı Gelir Vergisi Kanunu (GVK)
- 3294 sayılı Sosyal Yardımlaşma ve Dayanışmayı Teşvik Kanunu
- 2022 sayılı Kanun
- 5510 sayılı Sosyal Sigortalar ve Genel Sağlık Sigortası Kanunu
- 4857 sayılı İş Kanunu
- 6197 sayılı Eczacılar ve Eczaneler Hakkında Kanun
- 5216 sayılı Büyükşehir Belediyesi Kanunu
- 4054 sayılı Rekabetin Korunması Hakkında Kanun
- 6585 sayılı Perakende Ticaretin Düzenlenmesi Hakkında Kanun: RG 29.01.2015, 29251
- 5957 sayılı Kanun: RG 26.03.2010, 27533
- 5488 sayılı Tarım Kanunu

### 5.1 Sermaye geliri vergisi

#### S1 · Kısa süreli pay senedi kazancına kanuni oran (GVK Geçici md. 67)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **Fıkra 1:** Bankalar ve aracı kurumlar menkul kıymet alım satım kazancı, itfa farkı, dönemsel getiri ve ödünç gelirlerinden %15 tevkifat yapar.<br>**Fıkra 7:** Tevkifata tabi bu kazançlar için gerçek kişiler beyanname vermez.<br>**Fıkra 17:** Cumhurbaşkanı oranları her araç, ihraç eden, ihraç ve iktisap tarihi, hesap türü, vade, elde tutma süresi ve elde edenler itibarıyla ayrı ayrı "sıfıra kadar indirmeye veya %40'a kadar artırmaya" yetkili.<br>**Fıkra 19:** Madde 31/12/2025'e kadar uygulanır. Süre, 10680 sayılı Cumhurbaşkanı Kararıyla (RG 11.12.2025, 33104) 31/12/2030'a uzatıldı. |
| **Sorun** | **Vergi harcaması:** Geçici md. 67'deki indirimli ve sıfır oranların bedeli 189,3 milyar TL (2025, GİB) [D].<br>**Eşitsizlik:** Borsada hisse kazancı vergilenmiyor. Oysa asgari ücretin üç katı kazanan ücretlinin gelir vergisi ve primi %30,4 (Rapor 20) [H]. |
| **Önerilen karar** | Cumhurbaşkanı kararı:<br>- Pay senetlerinden ve mevzuattaki tanımıyla pay senedi yoğun fonlardan bir yıldan kısa sürede elde edilen kazançlarda oran %15 (kanuni oran) olur.<br>- Bir yıl ve daha uzun tutulanlarda bugünkü oran korunur. |
| **Beklenen etki** | Kısa vadeli alım satımdan alınan vergi artar; uzun vadeli tasarruf korunur. Hasılat hesaplanmadı [DY]. Gerekli veri: aracı kurumların elde tutma süresine göre kazanç dağılımı |
| **Risk** | İşlem hacminin düşmesi; vergilenmeyen araçlara kayış (yurt dışı hesaplar, kripto varlıklar). Önlem: oranın kademeli yükseltilmesi; aynı kararda vergilenmeyen benzer araçların taranması |
| **Araç** | Cumhurbaşkanı kararı (mevcut yetki); öncelik 2 |

#### S2 · Temettü yarım istisnasının düşürülmesi (GVK md. 22/3, 22/5)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **md. 22/3:** Tam mükellef kurumlardan elde edilen kâr paylarının yarısı gelir vergisinden müstesna. Tevkif edilen vergi, beyan edilen kâr payı üzerinden hesaplanan vergiden mahsup edilir.<br>**md. 22/5 (7491 sayılı Kanun, 27.12.2023):** "Cumhurbaşkanı … istisna oranı ile dördüncü fıkradaki %50 oranını ayrı ayrı veya birlikte sıfıra kadar indirmeye veya %100'e kadar artırmaya yetkilidir." **Mevcut yetkiyle yapılabilir** |
| **Sorun** | Temettü istisnası 57,9 milyar TL (2025, GİB) [D]. Kâr payı kurum düzeyinde kurumlar vergisiyle zaten vergilendiği için istisnanın çifte vergilemeyi hafifletme gerekçesi var [yorum]. Ama yükü emek geliriyle karşılaştırınca en yüksek gelir diliminin lehine işliyor |
| **Önerilen karar** | Cumhurbaşkanı kararı: md. 22/3'teki istisna oranı üç yılda %50'den %25'e iner. Tevkifat mahsubu sürer |
| **Beklenen etki** | Kâr payı geliri, aynı gelir dilimindeki ücretliye yaklaşan bir oranla vergilenir. Tam geçişte vergi harcamasının yarısına yakını geri gelir. Davranış etkisi hesaba katılmadı [H/V] |
| **Risk** | Şirketlerin kâr dağıtmayıp birikmesi; yatırım ortamı algısı. Önlem: kademeli geçiş; kurumlar vergisi oranıyla birlikte değerlendirme |
| **Araç** | Cumhurbaşkanı kararı (mevcut yetki); öncelik 2 |

#### S3 · Uzun vadeli TL tasarrufunda reel getirinin vergilenmesi (GVK Geçici md. 67)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | Geçici md. 67 stopajı nominal getiri üzerinden alınır. Cumhurbaşkanı oranı vadeye göre farklılaştırabilir (fıkra 17), ama matrahı enflasyona göre düzeltemez |
| **Sorun** | **Rapor 20 örneği [H/V]:** %40 faiz ve %30 enflasyonda %10 stopaj, reel getirinin %40'ını alıyor. Enflasyonlu ortamda küçük tasarrufçu, çoğu emekli, reel olarak ağır vergileniyor |
| **Önerilen metin** | Geçici md. 67'ye fıkra: "Vadesi bir yıl ve daha uzun Türk lirası mevduat, katılma hesabı ve Türk lirası cinsinden devlet iç borçlanma senetlerinde tevkifat matrahı, getiriden aynı dönemdeki Tüketici Fiyat Endeksi artışına isabet eden tutarın düşülmesiyle bulunur." |
| **Beklenen etki** | Vergi yükü reel getiriye bağlanır; uzun vadeli TL tasarrufu özendirilir. Hasılat kaybı hesaplanmadı [DY]. S1 ve S2'nin ek hasılatı bu kaybı karşılayabilir |
| **Risk** | İdari karmaşıklık (bankaların hesaplaması); düşük enflasyon döneminde etkisizleşir |
| **Araç** | TBMM: GVK değişikliği; öncelik 3 |

### 5.2 Asgari ve taban gelir

#### A1 · Gelir testli düzenli nakit destek (3294)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **3294 md. 1:** Amaç, "fakru zaruret içinde ve muhtaç durumda bulunan vatandaşlar"a yardım ve gelir dağılımının adil kılınması. md. 2: kapsam.<br>**2022 md. 1:** Muhtaç 65 yaş üstüne 4.387 gösterge × memur aylık katsayısı tutarında aylık. Muhtaçlık, kişinin ve eşinin gelirlerinden hesaplanan kişi başı ortalama gelirle belirleniyor. |
| **Sorun** | **KDV indirimi zengine de gidiyor.** Genel tüketim vergisi indiriminin kazancının yalnız %8–16'sı en yoksul %20'ye gidiyor (Rapor 20). Aynı bütçe doğrudan en yoksul %20'ye verilirse etkisi 6 kat: gelirin %2,37'si.<br>**Kayıt eksik.** Hane gelirini doğru ölçen bir kayıt yok. |
| **Öneri** | **Bütçe kuralı:** Gıda gibi temel mallarda KDV indirimi düşünüldüğünde, aynı bütçe gelir testli düzenli nakit desteğe aktarılır.<br>**Ödeme:** Sosyal Yardımlaşma ve Dayanışma Vakıfları aracılığıyla yapılır.<br>**Gelir testi:** Gelir İdaresi, SGK, tapu ve araç kayıtlarıyla yapılır.<br>**Azalma:** Ek kazançla destek kademeli azalır (azalma oranı %50'yi geçmez [V]). |
| **Risk** | Hedefleme hatası; kayıt dışı gelir; damgalanma; çalışma güdüsü. Önlem: kademeli azalma; düzenli doğrulama |
| **Araç** | Aile ve Sosyal Hizmetler Bakanlığı, vakıflar; bütçe kararı; öncelik 2 |

#### A2 · En düşük emekli aylığının endekslenmesi (5510 Ek md. 19)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | Ek md. 19: Aylıklar toplamı dosya bazında, ek ödeme dahil "23.552 Türk lirasından az olamaz"; aradaki fark Hazineden karşılanır. Maddeye bağlı 11 değişiklik dipnotu var; her artış ayrı bir kanun değişikliği. Karşılaştırma: 65 yaş aylığı (2022 md. 1) gösterge × memur aylık katsayısıyla endeksli |
| **Sorun** | Rapor 20: Taban aylık zam aylarında açlık sınırının %62–66'sına çıkıyor, sonraki zamdan önce %52–59'a iniyor [H]. Ayrıca 100 m² konutun kirası taban aylığın 1,17 katı |
| **Önerilen metin** | Ek md. 19'da "23.552 Türk lirasından" ibaresi yerine: "(…) gösterge rakamının memur aylık katsayısı ile çarpımından bulunacak tutardan". Gösterge, yürürlük tarihindeki tutara denk gelecek şekilde belirlenir |
| **Beklenen etki** | Taban aylık, memur katsayısıyla yılda iki kez kendiliğinden güncellenir [K]. Zam aralarındaki aşınma azalır. Hazine maliyeti hesaplanmadı: taban aylık alan emekli sayısı bilinmiyor [DY] |
| **Risk** | Otomatik maliyet artışı; katsayının kendisinin siyasi kararla belirlenmesi |
| **Araç** | TBMM: 5510 değişikliği; öncelik 3 |

#### A3 · Asgari ücret kararında ölçütlerin yayımı (4857 md. 39)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 39: Asgari Ücret Tespit Komisyonu ücretlerin asgari sınırlarını "en geç iki yılda bir" belirler; kararlar kesindir ve RG'de yayımlanır; çalışma esasları yönetmelikte |
| **Sorun** | Kanunda ve kararlarda ölçüt yok. Rapor 20: ortanca ücret asgari ücretin ≈ 1,1 katı [H/V]. Otomatik endeksleme kayıt dışılığı artırabilir |
| **Önerilen metin** | Asgari Ücret Yönetmeliğine: "Komisyon kararı; geçmiş dönem enflasyonu, verimlilik artışı, asgari ücretin ortanca ücrete ve açlık sınırına oranı ile kararın istihdam ve kayıt dışılık üzerindeki tahmini etkisini gösteren gerekçeyle birlikte yayımlanır." Yönetmeliğin güncel metni bu çalışmada okunmadı [DY] |
| **Beklenen etki** | Kural değil, şeffaflık. Karar tartışması ölçülebilir göstergelere dayanır |
| **Araç** | Çalışma ve Sosyal Güvenlik Bakanlığı ile Hazine ve Maliye Bakanlığı: yönetmelik değişikliği; öncelik 2 |

### 5.3 Esnaf ve rekabet

#### C1 · Basit usulden çıkışta rampa (GVK md. 46–48, mük. md. 20/A)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **md. 47 (kira sınırı):** Basit usul için yıllık kira bedeli büyükşehirde en fazla 99.000 TL, diğer yerlerde 60.000 TL.<br>**md. 48 (ciro sınırları):** Yıllık alış 1.200.000 TL'yi veya satış 1.900.000 TL'yi, hizmette hasılat 600.000 TL'yi aşmamalı (2026 tutarları). Şartı kaybeden ertesi yıl gerçek usule geçer.<br>**Mükerrer md. 20/A (7338 sayılı Kanun, 2021):** Basit usulde tespit edilen kazançlar gelir vergisinden müstesna. |
| **Sorun** | **Uçurum:** Eşiği geçen esnafın vergi yükü sıfırdan tam beyan, defter ve KDV'ye sıçrıyor.<br>**Bilinen sonuçlar [İ, literatür]:** Bu uçurum işletmeyi küçük tutma, işletmeyi bölme ve satışı kayıt dışına kaydırma güdüsü yaratır.<br>**Rapor 20:** Firmaların %50'si kayıt dışı rakiple yarıştığını söylüyor. |
| **Önerilen metin** | md. 48'e fıkra: "Basit usul şartlarını iş hacmi nedeniyle kaybedenler, izleyen iki takvim yılında, işletme hesabı esasına göre ve 103 üncü maddedeki tarifenin yarısı uygulanarak vergilendirilir." KDV tarafı için ayrı çalışma gerekir |
| **Ön şart** | GİB verisiyle eşik çevresinde işletmelerin yığılıp yığılmadığı ölçülmeli [DY] |
| **Araç** | TBMM: GVK değişikliği; öncelik 3 |

#### C2 · Sayısal giriş kotalarının gözden geçirilmesi (6197 md. 5, 5216 md. 7/1-f, 6585 md. 13)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **6197 md. 5:** Serbest eczane sayıları ilçede "en az üç bin beş yüz kişiye bir eczane olacak şekilde" düzenlenir.<br>**5216 md. 7/1-f:** Büyükşehir belediyesi taksi sayılarını, ücret ve tarifelerini belirler.<br>**6585 md. 13:** Perakende işletmelerin çalışma saatleri meslek kuruluşlarının müşterek teklifiyle vali tarafından belirlenebilir. |
| **Sorun** | OECD PMR 2023'te Türkiye giriş engelleri ve perakende fiyat kontrollerinde 38 üye içinde en kısıtlayıcı ülke (Rapor 20) [D/H]. Kademe modelinde eczane kotası bir mahallede en fazla 1–2, bir semtte 9–10 eczaneye izin veriyor [H] |
| **Öneri** | **Kim yapar:** Rekabet Kurumu ve ilgili bakanlıklar ortak bir gözden geçirme yapar.<br>**Nasıl:** Her sayısal kota ve saat kuralı için gerekçe, alternatif (mesafe ve hizmet şartı, nöbet yükümlülüğü) ve fiyat etkisi analizi yayımlanır.<br>**Ne yapılmaz:** Kotaların kaldırılması doğrudan önerilmiyor; etki ölçülmedi. |
| **Araç** | İdari çalışma; sonuca göre ilgili kanun değişiklikleri; öncelik 2 |

#### C3 · Esnaf ortak alım rehberi (6585 md. 14, 4054 md. 4–5)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **6585 md. 14:** Esnafın üye olduğu "tedarik ve dağıtım kooperatifleri" kurulabilir. Kuruluş Bakanlık iznine tabi; ortakların en az iki yıl oda kaydı şart; Bakanlık örnek ana sözleşme düzenler.<br>**4054 md. 5:** Verimlilik, tüketici yararı, rekabetin ortadan kalkmaması ve zorunluluk şartlarıyla muafiyet; Kurula muafiyet başvurusu yapılabilir. |
| **Öneri** | Ticaret Bakanlığı ve Rekabet Kurumunun ortak rehberi:<br>- ortak alım, ortak depo ve lojistik serbest,<br>- ortak satış fiyatı ve bölge paylaşımı yasak,<br>- örnek ana sözleşme. |
| **Kademe** | Semtte ortak depo (Rapor 21) |
| **Araç** | İdari; öncelik 2. Kurulmuş kooperatif sayısı bulunamadı [DY] |

#### C4 · Semt pazarında üretici payının izlenmesi (5957 md. 7/2)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 7/2: "Semt pazarında bulunan toplam satış yeri sayısının en az yüzde yirmisi özel satış yeri olarak üreticilere ayrılır." Talep yoksa diğerlerine tahsis edilebilir. md. 2/1-ş: üretici pazarı tanımı |
| **Öneri** | Semt meclisi (B3) semt pazarındaki üretici payını ve fiilen üreticinin kullandığı tezgâh oranını yılda bir izler. Belediye, tahsiste bölgedeki üretici kaydını esas alır. Oran %20'nin altına düşerse gerekçe açıklar |
| **Araç** | Belediye ve semt meclisi; öncelik 1. Fiilî üretici payı bugün ölçülmüyor [DY] |

### 5.4 Gıda zinciri

#### Y1 · Kısa zincirde hal rüsumunun indirilmesi (5957 md. 8)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | **5957 md. 8/1:** Toptancı halinde satılan maldan %1, hal dışında satılandan %2 hal rüsumu alınır. Bildirimle md. 4/1'deki (a), (b), (ç), (d), (e), (f) bentlerindeki mallar muaf; üretici örgütlerinin hal dışı satışı da bunların içinde. Üreticiden fatura veya müstahsil makbuzuyla alım olan (g) bendi muafiyet listesinde yok. "Cumhurbaşkanı, hal rüsumu oranlarını … genel olarak veya mal bazında … yüzde doksanına kadar azaltmaya veya artırmaya yetkilidir."<br>**md. 4/5:** Üreticiden yapılan bu alımlar hale bildirilmek kaydıyla hal dışında yapılabilir. |
| **Sorun** | Kısa zincirin cezası: üreticinin mahalle manavına ya da teslim noktasına doğrudan sattığı ürün, halden geçen ürünün iki katı rüsum ödüyor. Kooperatif satışı muaf, kooperatife üye olmayan küçük üretici değil |
| **Önerilen karar** | Cumhurbaşkanı kararı: "4 üncü maddenin birinci fıkrasının (g) bendi kapsamında üreticiden fatura veya müstahsil makbuzu ile yapılan ve aynı il sınırları içinde perakende satış yerine veya üretici teslim noktasına teslim edilen mallarda, toptancı hali dışında satılan mallardan alınan hal rüsumu oranı yüzde doksan indirimli uygulanır." Böylece %2 → %0,2. Hale bildirim şartı korunur |
| **Beklenen etki** | Kısa zincirde işlem maliyeti azalır; kayıt dışı kalmak yerine bildirimli satış özendirilir. Rüsum gelir kaybı hesaplanmadı [DY] |
| **Araç** | Cumhurbaşkanı kararı (mevcut yetki); öncelik 1 |

#### Y2 · Üretim izni yerine havza bazlı destek (5488 md. 7)

| Başlık | İçerik |
|---|---|
| **Mevcut hüküm [D]** | md. 7 (7442 sayılı Kanunla değişik, 23.03.2023): Bakanlıkça belirlenen ürünlerin "üretimine başlanmadan önce Bakanlıktan izin alınır". Bakanlık havza veya işletme bazında "asgari ve azami üretim miktarlarını belirler". Aykırılıkta önce uyarı, sonra yaptırım |
| **Sorun** | Rapor 20: soya yeterliliği %4, ayçiçeği %72. Açıkları kapatmak için güçlü bir yetki var. Ama izin ve kota projenin "zorlama yok" ilkesiyle ve serbest piyasa hedefiyle gerilimli |
| **Öneri** | Stratejik ürünlerde (yağlı tohum, yem bitkisi) izin ve kota yerine havza bazlı fark ödemesi, alım garantili sözleşmeli üretim ve sulama yatırımı. md. 7'deki izin yetkisi yalnız su stresi gibi kaynak kısıtı olan havzalarda kullanılır (Rapor 17 kısıt haritası) |
| **Araç** | Tarım ve Orman Bakanlığı (idari); öncelik 2. Tarımsal destek mevzuatı ayrıntılı incelenmedi [DY] |

---

## 6. Takvim (sürüm 1 takvimine eklenenler)

| Dönem | Adım | Öneri | Araç | Sorumlu |
|---|---|---|---|---|
| **Kasım – Aralık 2026** | Pilot iller için semt sınırlarının ve semt meclisi yönergesinin hazırlanması (mahalle pilotuyla birlikte); semt pazarında üretici payının ilk ölçümü | B3, C4 | Meclis kararı, kent konseyi yönergesi | Belediyeler |
| | Kısa zincirde hal rüsumunun %2'den %0,2'ye indirilmesi | Y1 | Cumhurbaşkanı kararı | Ticaret Bakanlığı |
| **Ocak – Haziran 2027** | PAİY md. 19 (P6), Otopark Yön. Ek-1 (O4) ve MPYY md. 21, 24 (M5) taslaklarının sürüm 1'deki O1–O2 ve M1–M4 taslaklarıyla birlikte görüşe açılması | P6, O4, M5 | Yönetmelik | ÇŞİDB MPGM |
| | Üç pilot ilçede parsel değer haritası; matrahın piyasa değerine oranının ölçülmesi | E2 | Pilot | Hazine ve Maliye, TKGM, belediyeler |
| | Hasılat analizi (elde tutma süresine göre kazanç dağılımı; temettü); giriş kotalarının gözden geçirilmesinin başlatılması; esnaf ortak alım rehberi | S1, S2, C2, C3 | İdari çalışma | Hazine ve Maliye, Rekabet Kurumu, Ticaret Bakanlığı |
| | Asgari Ücret Yönetmeliğinde gerekçeli karar hükmü | A3 | Yönetmelik | Çalışma ve Sosyal Güvenlik, Hazine ve Maliye |
| **Temmuz – Aralık 2027** | Karma kullanım değişikliklerinin yürürlüğü | P6, O4, M5 | Yönetmelik | ÇŞİDB |
| | Mahalle işyeri tek başvurusu | R1 | Yönetmelik | Ticaret, İçişleri |
| | Semt meclisi pilotunun bir yıllık değerlendirmesi | B3 | Değerlendirme | Üniversite |
| | Kısa süreli pay senedi kazancı ve temettü istisnası kararları (kademeli) | S1, S2 | Cumhurbaşkanı kararı | Hazine ve Maliye |
| | 2028 bütçesinde gelir testli nakit destek; stratejik ürünlerde havza bazlı fark ödemesi programı | A1, Y2 | Bütçe, idari | Aile ve Sosyal Hizmetler, Tarım ve Orman |
| **2028** | Kanun paketi (sürüm 1'deki 2028 paketine ek): 1319 (E1, E3), 5779 (E5), 3194 Ek md. 8 (I5), 5393 md. 9/A (B4); GVK Geçici md. 67 (S3) ve md. 48 (C1); 5510 Ek md. 19 (A2) | E1, E3, E5, I5, B4, S3, C1, A2 | Kanun | TBMM |
| | Değerleme yönetmeliği (md. 31) | E2 | Yönetmelik | Hazine ve Maliye |
| **2029–2033** | Arsa değer vergisi GSYH'nin %0,1'inden %0,5'ine; her yıl KDV genel oranının indirimi (kural C: %20 → %17,1) | E1, E4 | Kanun uygulaması, Cumhurbaşkanı kararı | Hazine ve Maliye |
| **2030** | İlk semt ve mahalle bütçeleri arsa değer vergisinden | B4 | Belediye bütçesi | Belediyeler |

Geçiş 2029'da başlıyor, çünkü 1319 Geçici md. 23 vergi değerlerini 2029'a kadar 2026 değerlerine bağlıyor. Yeni değerleme bu süre dolarken devreye girebilir.

---

## 7. Doğrulama durumu (sürüm 2)

### 7.1 Bu çalışmada doğrulananlar [D], 27.10.2026

| Mevzuat | Maddeler | Kaynak |
|---|---|---|
| 1319 Emlak Vergisi Kanunu (RG 11.08.1970 / 13576) | md. 8, 12, 18, 29, 30, 31; Geçici md. 23 (7566 sayılı Kanunla değişik); değerli konut vergisi tarifesi | mevzuat.gov.tr PDF (yerel kopya) |
| 3065 KDV Kanunu (RG 02.11.1984 / 18563) | md. 28 | mevzuat.gov.tr |
| 3194 İmar Kanunu (RG 09.05.1985 / 18749) | Ek md. 8 (7534 sayılı Kanunla değişik fıkralar dahil; değer artış payı gelirinin dağılımı) | mevzuat.gov.tr |
| 5393 Belediye Kanunu (RG 13.07.2005 / 25874) | md. 9, 18, 41, 76, 77; "semt" ifadesinin kanunda geçmediği | mevzuat.gov.tr |
| 5779 sayılı Kanun (RG 15.07.2008 / 26937) | md. 2 | mevzuat.gov.tr |
| PAİY | md. 19/1-f-1, 2, 5, 6, 7 (13.08.2025 değişikliği dahil) | mevzuat.gov.tr PDF (yerel kopya) |
| MPYY | md. 21/10, 24/9 | mevzuat.gov.tr PDF (yerel kopya) |
| İşyeri Açma ve Çalışma Ruhsatlarına İlişkin Yönetmelik (2005/9207) | md. 12 | mevzuat.gov.tr PDF (yerel kopya) |
| 2709 Anayasa | md. 73 | mevzuat.gov.tr |
| 193 GVK | md. 9, 22/3 ve 22/5, 46–48, mük. md. 20/A, Geçici md. 67 (fıkra 1, 6, 7, 17, 19 ve dipnotlar: 10680 sayılı Cumhurbaşkanı Kararı) | mevzuat.gov.tr |
| 5520 KVK | md. 5/1-d | mevzuat.gov.tr |
| 3294, 2022 | 3294 md. 1, 2; 2022 md. 1 | mevzuat.gov.tr |
| 5510 | Ek md. 19 | mevzuat.gov.tr |
| 4857 İş Kanunu | md. 39 | mevzuat.gov.tr |
| 6197, 5216, 4054 | 6197 md. 5; 5216 md. 7/1-f; 4054 md. 5 | mevzuat.gov.tr |
| 6585 (RG 29.01.2015 / 29251) | md. 12, 13, 14, Ek md. 1 | mevzuat.gov.tr PDF (yerel kopya) |
| 5957 (RG 26.03.2010 / 27533) | md. 2, 4, 7, 8 | mevzuat.gov.tr PDF (yerel kopya) |
| 5488 Tarım Kanunu | md. 7 (7442 sayılı Kanunla değişik) | mevzuat.gov.tr |

### 7.2 Kısmen doğrulanan [K] ve doğrulanamayanlar [DY]

1. **Kent Konseyi Yönetmeliği** (md. 8, 9, 10, 12): RG 08.10.2006'daki ilk metinden okundu; güncel konsolide metin kontrol edilmedi [K].
2. **Memur aylık katsayısı:** Yılda iki kez güncellendiği bilgisi [K]. Taban emekli aylığı alan kişi sayısı [DY].
3. **Değer artış payının kapsamı:** Mahalle karma alanı ya da yol boyu ticaret kararının değer artış payına tabi olup olmadığı. Bu bir yorum; uygulama ve yargı kararları incelenmedi [DY].
4. **Matrah ve değer haritası:** Emlak vergisi matrahının piyasa değerine oranı; TKGM'nin taşınmaz değerleme altyapısının durumu [DY].
5. **Arsa değeri stoku:** Ülke arsa değeri stoku. Arsa değer vergisinin oran bandı bu yüzden sayıyla verilmedi [DY].
6. **Plan gösterimi:** MPYY plan gösterim ekinin güncel hâli (yeni lejant önerisi için) [DY].
7. **Otopark bedeli:** Otopark bedeli tahsilatının küçük işyerlerine düşen kısmı [DY].
8. **Hasılat ve maliyet etkileri:** S1, S2, S3, A2 ve Y1'in hasılat ve maliyet etkileri hesaplanmadı [DY]. Gereken veriler:
   - aracı kurum kazançlarının elde tutma süresine göre dağılımı,
   - taban aylık alan emekli sayısı,
   - hal rüsumu tahsilatının kalemleri.
9. **Okunmayan mevzuat:** Asgari Ücret Yönetmeliğinin güncel metni; tarımsal destek mevzuatı; İŞKUR'un güncel görev dayanağı [DY].

*Bu belge hukuki görüş değildir. Önerilen metinler ilgili kurumların ve bir hukukçunun incelemesinden geçmeden kullanılmamalıdır.*
