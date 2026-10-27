# Fıtrat Kodu — Biçim Temelli İmar Kodu Taslağı (Sürüm 0.2.1)

**Proje:** TR TAMİRAT
**Bölüm:** 07_TASARIM_CIZIM · İP6 (model mahalle ve tasarım)
**Tarih:** 26 Ekim 2026 · **Sürüm:** 0.2.1 (taslak, tartışma için; 0.2 + geleneksel doku kalibrasyonu)
**Önceki sürüm:** `fitrat_kodu_taslak.md` (0.1; değiştirilmedi)
**Eş dosyalar:** `model_mahalle_v2.md` (v2.1: plan, çizimler, doğrulama) · `09_RAPORLAR/11_geleneksel_doku_morfolojisi.md` (§3 kalibrasyon önerileri) · `tasarim_parametreleri.md` (§6.2 düzeltme notu) · `08_MEVZUAT_POLITIKA/degisiklik_paketi_v1.md` (P4, O1–O2, M1, G1)

## İşaret sistemi

| İşaret | Anlamı |
|---|---|
| **[D]** | Doğrulandı: mevzuat metni ya da hakemli kaynak. Mevzuat maddeleri bu çalışmada yeniden okunmadı; proje mevzuat paketinde [D] işaretiyle aktarılan hükümlerdir |
| **[İ]** | İkincil aktarım |
| **[DY]** | Doğrulanmadı |
| **[V]** | Bu çalışmanın varsayımı |
| **[H]** | Model mahalle v2 / v2.1'de hesaplandı |
| **doğrulanmalı** | Hukuki yorum ya da uygulama yolu önerisi; hukuki görüş alınmadan kullanılmamalı |

---

## 0.2'de ne değişti?

Model mahalle v2'nin çözdüğü konular koda kural olarak işlendi. Değişen hükümler metinde **(0.2)** işaretlidir.

| # | Konu | 0.1 | 0.2 | Dayanak |
|---|---|---|---|---|
| 1 | İlkokul | ≤ 500 m (ağ), alan standardı eski EK-2 aktarımı | **2,0 m²/kişi**, okul başına ≥ 5.000 m². Her konuta ≤ 500 m (%100), tercihen ≤ 400 m. Tek okulla sağlanamıyorsa **ikinci okul** açılır; alan küçültülmez, kat artırılmaz | Güncel EK-2 [D]; model v2: %100, ≤ 400 m %90,7 [H] |
| 2 | Diğer EK-2 kalemleri | Eski aktarım | Ortaokul 2,0; anaokulu 0,5; sosyal-kültürel 0,75; teknik altyapı 1,0; açık-yeşil ≥ 10 m²/kişi | Güncel EK-2 [D] |
| 3 | Dikey dolaşım | "Z+3'te zorunlu, Z+2'de yer ayrılır" | PAİY md. 34/1'e göre tipoloji başına kural; tek BB'li evde platform yeri; asansörsüz binada zeminde ≥ %15 erişilebilir BB | PAİY md. 34/1 (RG 01.07.2026) [D]; paket P4 |
| 4 | Kat yüksekliği ve ön eşik | 3,0–3,3 m; K2 ön eşik 1,5–2,5 m | Konut katı **3,1 m** (esas); K2 ön eşiği **1,5 m** (esas) | S2 H/W 0,64 → 0,72 [H] |
| 5 | Ağaç | Parsel başına ≥ 1; S2 12 m | Dikim kuralları (§3.2): bahçede 2 ağaç, S2 10 m + şaşırtma ağacı, park kenarı ve okul bahçesi sıraları | Ağaç örtüsü %25 → %31 (20 yıl) [H] |
| 6 | Eğik sokak kenarı | Kural yok (kırpılan parsel düşüyordu) | **Köşe evi kuralı** (§3.3) | 19 köşe evi; düşen parsel 98 → 85 [H] |
| 7 | Teknik altyapı | Köşelerde | Ayrıca kapıda (mobilite noktası yanında) servis şeridi; servis aracı hücreye girmez | — |
| 8 | Tahsis | Oran hedefi | Parsel grubu düzeyinde dağıtım ve sapma sınırı (§6.2) | v1 açık sorusu 8 |
| 9 | Zemin kat | "S1 ve meydan cephesinin ≥ %60'ı konut dışı" | Ek olarak **esnek zemin kat** tescili (§3.4) | Model v2'de ≈ 208 konut dışı birim, 33 kişiye 1 [H] |
| 10 | Otopark | Parsel içinde yok; 0,5–0,7 yer/hane | Aynı. Ek-1 farkı sayıyla kayıt altında; O1 + O2 olmadan uygulanamaz | Plan, Ek-1'in bugünkü gereğinin %48'ini sağlıyor [H] |

---

## 0.2.1'de ne değişti?

Model mahalle v2.1'in geleneksel doku kalibrasyonu koda işlendi (`09_RAPORLAR/11_geleneksel_doku_morfolojisi.md` §3, `model_mahalle_v2.md` §3.5). Değişen hükümler metinde **(0.2.1)** işaretlidir.

| # | Konu | 0.2 | 0.2.1 | Dayanak [H: model v2.1, 600 m pencere] |
|---|---|---|---|---|
| 11 | Ada ortası geçidi | Yalnız T3 adalarında S3 | T1/T2 adalarında da: uzun kenar > 100 m ise ortadan **5–6 m kamusal geçit** (≥ 3,5 m engelsiz). Yaya adası ≤ 0,45 ha | Yaya adası 0,79 → 0,45 ha (60 ha); kavşak 242 → 303/km² |
| 12 | Parsel cephesi | T1 ≈ 6,3 m; T2 ≈ 9,2 m | **T1 K1 6,5–7,5 m, K2 ≥ 6,3 m (hedef 6,5); T2 9–10 m** | Model: K1 7,17 · K2 6,37 · T2 9,56 m |
| 13 | K2 cephe hattı | 1,5 m | **1,0 m** (0,5–1,5 m); S2 cephe arası 12 m | S2 H/W 0,72 → 0,78 |
| 14 | T3 avlusu | Grup başına ≥ 350 m², bir kenar açık olabilir | **Dört yandan kapalı avlu, 300–450 m²** (§3.6). Dördüncü kenar tek katlı arka kanat ya da 2,5–3 m bahçe duvarı | Kapalı avlu 0 → 0,83/ha; medyan 326 m² |
| 15 | Cephe modülü | Tanımsız | T3 sokak kanadı ve T4 cephesi **9–12 m'lik modüllerle** (ayrı giriş ya da cephe kırığı, saçak ve renk değişimi) | Cephe adımı 17,9 → 17,1 m |
| 16 | Yapı oturumu | En fazla (parsel) | Ada içi net oturum **hedefi** eklendi (bilgi); T3 grubunun parsel sınırı %70'e çıktı | Net %31 → %34; brüt %22 → %24 |
| 17 | Kapı altı geçidi | Tanımsız | Kapalı avluya en az **3,5 m genişlik, 4,0 m net yükseklikte** bir geçit | Rapor §3.2 sınama 3 [DY] |

Rapordan bilerek alınmayanlar:

- **T1 derinliği 11–12 m.** Son durum zaten 6,4 × 13 m, yani 83 m².
- **Brüt emsal 0,75–0,9.** Kat artırmak gerekirdi.
- **T3/T4'ü 9–12 m'lik ayrı binalara bölmek.** Asansör kuralı yüzünden yalnız P4 ile yapılabilir.
- **Kamusal yeşilde geleneksel değerler.** Geleneksel dokuda 1 m²/kişi. Kod ≥ 10 m²/kişi'de kalır.

---

## 0. Amaç ve gerekçe

Türkiye'de imar, binayı çoğunlukla **sayılarla** tarif eder: emsal (KAKS), taban alanı (TAKS), bahçe mesafesi ve yola göre kat adedi. Bu sayılar sokağın, avlunun ve komşuluğun biçimini belirlemez. Varsayılan kurallar (ön bahçe 5 m, yan ve arka 3 m, ayrık nizam) sonuçta parselin ortasında duran apartmanı üretir [D, PAİY md. 23].

**Fıtrat Kodu** aynı yoğunluğu başka bir biçimle üretmeyi hedefler. Kodun bağlayıcı kısmı sokak cephesi, kat sınırı, avlu ve zemin kat kullanımıdır; emsal yalnız bilgi için verilir.

**Gerekçe.** Faz 2'de bina yüksekliğinin doğurganlığa doğrudan etkisi küçük çıktı: eğitim sabitken kat başına ≈ −0,03 çocuk. Buna karşılık kat başına ≈ +%2,5 standartlaştırılmış ölümlülükle ilişkili bulundu (`09_RAPORLAR/09_faz2_sentez.md`). Bu yüzden kod doğurganlık vaadine dayanmaz. Beş gerekçesi şunlardır:

1. **Sağlık:** yürüme, yeşile yakınlık, ağaç gölgesi, düşük trafik ve alçak bina.
2. **Çocuk:** okula, oyuna ve yeşile araç yolu geçmeden, göz altında erişim.
3. **Komşuluk:** avlu grubu, komşuluk birimi, mescit ve meydan.
4. **Kuşaklar arası yakınlık:** aynı parselde iki kuşak, büyüyebilen ev, zeminde erişilebilir daire.
5. **Deprem güvenliği:** alçak, düzenli ve genişlemesi baştan hesaplanmış yapı.

## 1. Kodun bileşenleri

| # | Bileşen | İçerik | Bağlayıcılık |
|---|---|---|---|
| 1 | **Düzenleyici plan** | Bölge haritası (K1–K4), sokak tipleri, zorunlu cephe hatları, zorunlu dükkân cepheleri, donatı alanları | Bağlayıcı (plan paftası) |
| 2 | **Kamusal alan standartları** | Sokak kesitleri (S0–S3, diyagonal), **ağaç dikim kuralları (0.2)**, hız, otopark cepleri | Bağlayıcı (kentsel tasarım projesi) |
| 3 | **Bina biçim standartları** | Bölge başına parsel, cephe hattı, kat, oturum, avlu, zemin kat, **dikey dolaşım (0.2)** (§3) | Bağlayıcı |
| 4 | **Tipoloji kataloğu** | T1–T4 ön onaylı tip projeler (§7) | Hızlandırıcı (ön onay) |
| 5 | **Mahalle standartları** | Ağ mesafesiyle donatı erişimi, güncel EK-2 alanları, yeşil, otopark payı (§5) | Bağlayıcı (plan notu) |
| 6 | **Tahsis ve yönetişim kuralları** | Yapımcı başına konut, kooperatif payı, **sosyal konutun dağıtılması (0.2)**, etaplama | Kamu arsasında şartname |

## 2. Bölgeler (transect)

| Bölge | Tanım | Model mahallede yeri | Baskın tipoloji |
|---|---|---|---|
| **K1 · Köy kenarı** | Yeşil kuşağa ya da tarıma bakan, en alçak ve en bahçeli doku | Kuzey ve batı kenarı | T1, T2; avlu grubu Z+2 |
| **K2 · Mahalle genel** | Yaşam sokaklarıyla örülü konut dokusu | Komşuluk birimlerinin içi | T1, T2, T3 |
| **K3 · Mahalle merkezi** | Mahalle caddesi (S1) ve meydan çevresi | Artı biçimli cadde boyunca | T3 (Z+2 / Z+3), T4 |
| **K4 · Semt çarşısı** | Toplayıcı yolun kapıları; mobilite noktası | Güney ve doğu kapıları | T4, mobilite noktası |

Bölge haritası: `model_mahalle_v2/vaziyet_plani.png`, sağ paneldeki küçük harita.

## 3. Bina biçim standartları

### 3.1 Bölge tablosu

Ölçüler parsel bazındadır. "Z+n" zemin üstünde n kat demektir.

| Kural | K1 · Köy kenarı | K2 · Mahalle genel | K3 · Mahalle merkezi | K4 · Semt çarşısı |
|---|---|---|---|---|
| **İzin verilen tipolojiler** | T1, T2, T3 (Z+2) | T1, T2, T3 | T3, T4 | T4, mobilite noktası, donatı |
| **Parsel cephesi (0.2.1)** | T1 6,5–7,5 m; T2 9–10 m; ≤ 12 m | T1 ≥ 6,3 m (hedef 6,5–7,5); T2 9–10 m; T3 ≤ 40 m | 9–40 m | 12–24 m |
| **Parsel alanı** | 150–400 m² (köşe evi ≥ 110 m²) | 150–1.300 m² (köşe evi ≥ 110 m²) | 250–1.300 m² | 300–800 m² |
| **Parsel derinliği** | 25–32 m | 25–32 m | 25–32 m | 25–32 m |
| **Nizam** | Bitişik (sıra ev) | Bitişik ya da avlu grubu | Bitişik, sürekli cephe | Bitişik, sürekli cephe |
| **Cephe hattı (sokak sınırından)** | 2,0–3,0 m geri | **1,0 m (0.2.1: esas; 0,5–1,5 m)** | 0–1,5 m | 0 m |
| **Cephe modülü (0.2.1)** | Parsel = modül | Parsel = modül; T3 sokak kanadı 9–12 m'lik modüllerle | T3 ve T4 cephesi 9–12 m'lik modüllerle: ayrı giriş ya da cephe kırığı, saçak ve renk değişimi | Aynı |
| **Ada ortası geçidi (0.2.1)** | Uzun kenarı > 100 m olan T1/T2/T3 adasında ortadan 5–6 m kamusal geçit, ≥ 3,5 m engelsiz, iki ucu sokağa açık | Aynı | Aynı; çarşı cephesi (T4) sürekli kalabilir | — |
| **Cephe doluluk oranı** | ≥ %60 | ≥ %70 | ≥ %80 | ≥ %90 |
| **Kat (en fazla)** | Z+2 | Z+2; S1 ve köşe parselde Z+3 | Z+3; köşe ve nirengi Z+4 | Z+3; köşe Z+4 |
| **Kat (en az)** | — | — | S1 cephesinde Z+2 | Z+2 |
| **Saçak yüksekliği (en fazla)** | 9,5 m | 9,5 m (S1 cephesi 12,5 m) | 13,8 m (köşe 16,9 m) **(0.2)** | 13,8 m (köşe 16,9 m) **(0.2)** |
| **Kat yüksekliği** | Konut **3,1 m (0.2: esas; 3,0–3,3)** | Aynı | Zemin ≥ 4,5 m (dönüşebilir), üstü 3,1 m | Aynı |
| **Yapı oturumu (en fazla, parsel)** | %50; T3 avlu grubu %70 (0.2.1) | %55; T3 avlu grubu %70 (0.2.1) | %70 (0.2.1; 0.2: %60) | %65 |
| **Ada içi net yapı oturumu (hedef, bilgi; 0.2.1)** | %25–30 | %35–40 | %45–55 | — |
| **Emsal (bilgi)** | ≈ 1,2 | ≈ 1,5 | ≈ 1,8 | ≈ 2,2 |
| **Özel bahçe / avlu asgarisi** | T1: ≥ 70 m² arka bahçe; T2: hane başına ≥ 50 m² | K1 gibi; T3: hane başına ≥ 30 m² ve **dört yandan kapalı 300–450 m² avlu** (dar uç parselde ≥ 260 m²) (0.2.1) | T3: hane başına ≥ 20 m²; kapalı avlu 300–450 m² (0.2.1); her daireye ≥ 6 m² balkon | Parselin ≥ %25'i arka avlu; her daireye ≥ 6 m² balkon |
| **Ada içi ortak bahçe** | T1/T2 adalarında ≥ 8 m orta şerit | Aynı | Avlular ada ortasında birleşir | — |
| **Zemin kat kullanımı** | Konut; ev-işyeri (≤ %30); mescit ve kreş serbest | Konut; köşe parselde dükkân, atölye, kreş, mescit serbest | S1 ve meydan cephesinin ≥ %60'ı konut dışı; **esnek zemin kat (0.2)** | Toplayıcı ve S1 cephesinin %100'ü konut dışı |
| **Zemin kat kotu** | 0–0,45 m; erişilebilir dairelerde eşiksiz | Aynı | Ticari: sokakla aynı kot | Aynı |
| **Dikey dolaşım (0.2)** | §3.5 | §3.5 | §3.5 | §3.5 |
| **Otopark** | Parsel içinde yok; engelli ya da yaşlı hanesi için kapı önünde 1 cep | Parsel içinde yok | Yükleme cebi S1'de | Mobilite noktası burada |
| **Ağaç (0.2)** | Parsel başına ≥ 2 (biri gölge ağacı) | Aynı; T3 avlusunda ≥ 4 | T3 avlusunda ≥ 4 | Arka avluda 100 m² başına ≥ 1 |
| **Parsel birleştirme** | En fazla 2 parsel | En fazla 2 (T3 tek parsel) | Ada başına en fazla 40 konut aynı yapımcıya | Aynı |

**Saçak yüksekliği.** K3–K4 değerleri 4,5 m zemin + 3 × 3,1 m kattan çıkar. S2'deki 9,5 m sınırı 3 × 3,1 m = 9,3 m'yi karşılar.

**Parsel cephesi ve yapı oturumu (0.2.1).**

- **K2'de T1'in alt sınırı.** 6,3 m'de bırakıldı. Model mahallede 6,5 m hedefi T1 payını %22,8'den %21,4'e indiriyor [H]. Pilotta 6,5 m önce K1'de uygulanır.
- **Parsel sınırı ve ada hedefi.** Arka kanadı olan T3 grubunun parsel oturumu ≈ %66 [H]. Ada içi net oturum hedefi bu yüzden ayrıca verildi: v2.1 modelinde %34, geleneksel medyan %34, çağdaş medyan %29 [H].

### 3.2 Ağaç dikim kuralları (0.2, yeni)

Ağaçlar kamusal alan projesinin ve ruhsatın parçasıdır. Model mahallede bu kurallarla 20 yıllık taç örtüsü **%31,1** çıkıyor [H]. Taç yarıçapları varsayımdır [V].

| Yer | Kural | 20 yılda taç yarıçapı [V] |
|---|---|---|
| S0 toplayıcı, S1 cadde | İki yanda 10 m arayla; S0'da refüjde de | 4,0 m |
| S2 yaşam sokağı | Ağaç ve park cebi şeridinde 10 m arayla (0.1: 12 m). Karşı yanda, paylaşımlı yüzeyde 24 m arayla **şaşırtma ağacı** (yavaşlatma) | 3,5 / 3,0 m |
| Yeşil diyagonal | İki sıra, 8 m arayla | 3,0 m |
| S3 geçidi (T3 ve ada ortası, 0.2.1) | Yağmur bahçesinde 10 m arayla küçük ağaç | 2,5 m |
| Park, komşuluk yeşili | 100 m² başına 1 (sahalar ve yollar hariç) + kenarda 10 m arayla gölge sırası | 4,5 m |
| Okul, cami, ASM, konak bahçesi | Kenarda 9 m arayla | 3,5 m |
| T1/T2 arka bahçesi | ≥ 2 ağaç: evden en uzakta bir gölge ağacı (dut, ceviz, ıhlamur) ve bir meyve ağacı | 3,5 / 2,5 m |
| Ada içi ortak şerit | Ortada 8 m arayla | 3,5 m |
| T3 avlusu (kapalı, 0.2.1) | ≥ 4; oyun alanı avlunun güneşli yarısında | 3,5 m |
| T4 arka avlusu | 100 m² başına 1 | 3,5 m |
| Bostan | Kenarda 9 m arayla meyve ağacı | 2,5 m |

### 3.3 Köşe evi kuralı (0.2, yeni)

Diyagonal, eğik sokak ya da meydan bir T1/T2 parselini kestiğinde parsel düşürülmez; şu koşullarla **köşe evi** olur:

1. **Bina.** Kırpılmış bina özgün oturumun ≥ %60'ını korur ve en dar boyutu ≥ 4,5 m'dir.
2. **Parsel.** Kalan parsel özgün alanın ≥ %45'idir (≥ 110 m²).
3. **T2.** Bina %80'in altına düşerse T2 tek haneli T1'e dönüşür.
4. **Eğik cephe.** Eğik kenara bakan cephe ana cephe sayılır; en az bir yaşam odası penceresi bulunur. Diyagonal okul yolunda "sokakta göz" bu cephelerden sağlanır.
5. **Genişleme payı.** Eğik kenarda kalırsa genişleme payı kaldırılır.

Bu kural model mahallede 19 köşe evi ve 21 konut geri kazandırdı. Diyagonal yüzünden düşen parsel 98'den 85'e indi [H].

### 3.4 Esnek zemin kat (0.2, yeni)

K3 ve K4'te zorunlu konut dışı zemin katlar kat irtifakında **"esnek bağımsız bölüm"** olarak tescil edilir. Bu bölüm dükkân, atölye, ofis, kreş, mescit ya da sonradan erişilebilir konut olarak kullanılabilir.

- **Gerekçe.** Model mahallede zemin kattaki konut dışı birim sayısı ≈ 208; 33 kişiye 1 birim düşüyor [H]. Simülasyonda esnafın 300 m yürüme havzası ≈ 3.500 kişi. Hepsinin dükkân olarak yaşaması beklenmez.
- **Dönüşüm koşulu.** Konuta dönüşecek zemin birim eşiksiz düzenlenir.
- **Yasal yol.** 634 sayılı Kanun md. 24'teki oybirliği şartı yüzünden paket K2'ye bağlıdır (**doğrulanmalı**).

### 3.5 Dikey dolaşım ve erişilebilirlik (0.2, yeni)

**Mevcut hüküm [D].** PAİY md. 34/1 (RG 01.07.2026): tek bağımsız bölümlü konutlar hariç, bodrum dahil 3 katlı binada asansör yeri, 4 ve daha fazla katlı binada asansör tesisi zorunludur. md. 34/4: 20'den fazla konut bağımsız bölümü olan binada en az 2 asansör.

| Tipoloji | Kat · BB | Kod hükmü | Alan ve maliyet etkisi [H/V] |
|---|---|---|---|
| T1 büyüyebilen ev | Z+2 · 1 | Asansör kuralı kapsamaz. Kod şunları ister: (i) kiler/dolap dikmesi **kaldırma platformu yeri** olarak bırakılır (1,0 × 2,3 m; 0,8 × 1,25 m kabin sığar [DY]); (ii) aşama 2'de zeminde büyükler odası ve duş eşiksiz | 3 katta 6,9 m², dolap olarak kullanılır. Platform takılırsa ≈ 0,9 milyon TL, yapımın ≈ %24'ü [V] |
| T2 çok kuşaklı ev | Z+2 · 2 | Asansör yeri, 1,4 × 1,6 m, merdivenin ucunda. Zemin 2+1 eşiksiz | 6,7 m² (%2,2); depo olarak kullanılır |
| T3 avlu grubu, Z+2 | Z+2 · 12 | İki çekirdekte asansör yeri (1,6 × 1,8 m). **Grupta BB'lerin ≥ %15'i zeminde eşiksiz.** Zemini dükkân ya da donatı olan grupta yan kanat dubleksi yerine "zemin + üst kat daire" kullanılır | 17,3 m² (%1,2) |
| T3 avlu grubu, Z+3 | Z+3 · 15 | Bugünkü uygulamada her merdiven evine asansör. Kod, tasarımda avlu tarafında galeri ("hayat") bırakılmasını ister; P4 yürürlüğe girince tek asansöre geçilir | 2 asansör ≈ 2,6 milyon TL, yapımın %7,6'sı; P4 ile %3,8 [V] |
| T4 çubuk | Z+3 / Z+4 · 9–12 | Çekirdekte 1 asansör | Yapımın %5–5,8'i [V] |

**Mahalle ölçeğinde (plan notu).**

- **Ölçüt 17.** Bütün konutlar Genelge 2026/4 ölçüt 17'yi sağlar: binada zeminde ≥ %15 erişilebilir BB ya da asansör. Model mahallede %100 [H].
- **Zemin daireler.** Eşiksiz zemin daire payı mahalle genelinde ≥ %15 hedeflenir. Model v2.0'da %14,8 (320 daire); v2.1'de T3 arka kanatlarıyla **%16,7 (362 daire)** [H].
- **Tahsis önceliği.** Zemin daireler tahsiste 65 yaş üstü ve engelli haneye öncelikli sunulur. Kiralık sosyal konut payında bu öncelik zorunludur.

### 3.6 Avlunun dördüncü kenarı ve kapı altı geçidi (0.2.1, yeni)

Sırt sırta iki avlu grubunun oluşturduğu adada:

1. **Güney sıra grup.** Ada ortasında, avlunun kuzey kenarında **tek katlı arka kanat** yapılır. Kanadın ölçüleri ve kullanımı:
   - derinlik ≤ 5 m, saçak ≤ 3,5 m;
   - zeminden girişli, eşiksiz 2+1;
   - yan kanatlar arka kanada kadar uzar, avlu dört yandan kapanır.

   **Neden tek kat?** Kanat kuzeydeki komşu avlunun güney kenarındadır. İki kat olsaydı 21 Aralık öğle gölgesi ≈ 13,6 m'yi bulurdu ve kuzey avlunun ≈ %70'ini kaplardı. Tek katta gölge 7,1 m'dir, yani ≈ %36 [H].
2. **Kuzey sıra grup.** Dördüncü kenarını güney grubun arka kanadı oluşturur. Yan kanatla arka kanat arasındaki açıklık **2,5–3 m'lik bahçe duvarıyla** kapanır. Bu gruba arka kanat yapılmaz.
3. **Avlu ölçüsü.** Kapalı avlu **300–450 m²**; dar uç parselde ≥ 260 m². Kuzey avlu daha büyük olabilir (model: 451–607 m²). Oyun alanı avlunun güneşli yarısına konur.
4. **Acil erişim.** Her kapalı avluya en az **3,5 m genişlik ve 4,0 m net yükseklikte** bir kapı altı geçidi ya da duvar kapısı açılır [DY].
   - Konut zemininde (3,1 m kat) bu, geçidin üstündeki açıklıkta döşemenin ≈ 0,9 m yükseltilmesini gerektirir.
   - Dükkânlı zeminde (4,5 m) koşul kendiliğinden sağlanır.
   - Maliyeti doğrulanmadı.
5. **Erişilebilirlik.** Arka kanat daireleri mahalledeki eşiksiz zemin daire payına sayılır; tahsiste önce 65 yaş üstü ve engelli hanelere sunulur (§3.5).

Model mahallede (v2.1) 38 güney grubunda kapalı avlu var. Ölçümde 0,83 avlu/ha ve medyan 326 m² çıkıyor; geleneksel dokunun medyanı 144 m², raporun hedefi ≈ 0,5/ha. 40 kuzey grubu duvarla kapalı [H].

## 4. Kamusal alan standartları (sokak tipleri)

Kesitler: `model_mahalle_v2/sokak_kesitleri.png`.

| Tip | Kamusal genişlik | Bileşenler | Hız | Ağaç (0.2) | H/W (model v2) | Bölgeler |
|---|---|---|---|---|---|---|
| **S0 · Toplayıcı** | 24 m | Kaldırım 3,0 · bisiklet 2,0 · ağaç/park 2,5 · şerit 3,25 · refüj 2,5 · şerit 3,25 · ağaç/park 2,5 · bisiklet 2,0 · kaldırım 3,0 | 50 km/s (öneri; doğrulanmalı) | İki yan + refüj, 10 m | 0,58 | K1 kenarı, K4 |
| **S1 · Mahalle caddesi / çarşı** | 18 m | Kaldırım 3,75 · ağaç/durak 2,0 · şerit 3,25 · şerit 3,25 · ağaç/park cebi 2,0 · kaldırım 3,75 | 30 km/s; meydanda yalnız otobüs ve acil araç | İki yan, 10 m | **0,71** | K3, K4 |
| **S2 · Yaşam sokağı** | 10 m; cephe arası K2'de **12 m (0.2.1)** | Yaya 2,0 · ağaç/park cebi 2,0 · paylaşımlı yüzey 4,0 · yaya 2,0; kot farkı yok | ≤ 20 km/s | Tek yan 10 m + paylaşımlı yüzeyde 24 m arayla şaşırtma ağacı | **0,78** (K2, son durum; 0.2: 0,72); 0,66 (K1) | K1, K2, K3 |
| **S3 · Yaya ara sokağı / geçit (0.2.1)** | 5–6 m | 6 m: yağmur bahçesi 1,25 · **yürüme 3,5 (engelsiz)** · oturma 1,25. 5 m (ada ortası): yürüme 3,5 · yağmur bahçesi ya da oturma 1,5. Boy ≤ 65 m, iki ucu açık; mahreç verilmez | Araçsız; acil durum aracı geçer | Yağmur bahçesinde 10 m | 1,29 (T3 geçidi) | K1, K2, K3 |
| **Yeşil diyagonal** | 8 m | Yürüme ve bisiklet yolu, iki sıra ağaç | Araçsız | İki sıra, 8 m | — | Köşeden meydana; köşedeki okul varsa okul kapısında biter |

**S2'de güneş (0.2 ve 0.2.1 notu).** D–B uzanan S2'nin kuzey cephesinde 21 Aralık öğle gölgesi şöyle değişti:

- 0.1'de 2,3 m;
- 0.2'de, H/W 0,72 ile 3,1 m;
- **0.2.1'de, 1,0 m eşik ve H/W 0,78 ile 3,6 m.**

Zemin kat öğle saatinde gölgede kalır; 21 Mart'ta cephe tümüyle güneştedir. Bu bilinçli bir tercihtir:

- Güney cephe saçağının 9,5 m sınırı sürer.
- K1'de cephe hattı 2,0 m kalır.
- Gerçek alanda K–G uzanan S2'lerde 1,0 m, D–B uzananlarda 1,5 m eşik seçilebilir.
- Genelge ölçüt 6 bu sokaklarda sağlanmaz; kayda geçirilmelidir.

**Okul geçidi (0.2).** Okula giden yaya yolu S1'i kesiyorsa geçit yükseltilmiş ve ışıklı ya da kavşak denetimli olur (paket M2).

**Hücre ilkesi ve okul sokağı** 0.1'deki gibidir.

## 5. Mahalle düzeyi standartlar (plan notu önerisi)

Bütün mesafeler **yaya ağı mesafesidir**: konut kapısından donatı girişine sokak, geçit ve park yolları üzerinden ölçülür. Hedef her konutun %100'üdür. Son sütun model mahalle v2'de elde edilen değerdir [H].

| Donatı | Kod standardı (ağ) | MPYY md. 12 [D] | Model v1 → v2.1 [H] |
|---|---|---|---|
| **İlkokul (0.2)** | ≤ 500 m (%100), tercihen ≤ 400 m. Tek okulla sağlanamıyorsa ikinci okul | ≈ 500 m | %96,8 → **%100** (≤ 400 m: %75 → %91) |
| Ortaokul | ≤ 1.000 m | ≈ 1.000 m | %100 → %100 |
| Anaokulu ya da kreş | ≤ 400 m | ≈ 500 m | %100 → %100 |
| İbadet yeri (kademeli: mescit 150 / küçük cami 250 / semt camii 400 m) | Kademeli kural | 150 / 250 / 400 m | %99,3 → %99,4 |
| Aile sağlık merkezi | ≤ 500 m | ≈ 500 m | %96,5 → %96,7 |
| ≥ 0,5 ha kamusal yeşil | ≤ 300 m (hedef 200 m) | Çocuk bahçesi ≈ 500 m | %100 → %100 |
| Kapı önü oyun alanı | ≤ 100–150 m | — | %100 → %100 |
| Açık spor sahası | ≤ 500 m | ≈ 500 m | %100 → %100 |
| Bakkal, fırın ya da dükkân | ≤ 300 m | — | %100 → %100 |
| Otobüs durağı | ≤ 400 m (hedef 300 m) | — | %100 → %100 |
| Bölgesel otopark | ≤ 400 m; 0,5–0,7 yer/hane | — | %100; 0,57 yer/hane |
| Komşuluk birimi | 150–300 hane | — | 214–328 → 208–309 |

**Güncel EK-2 alanları (0.2) [D, degisiklik_paketi_v1.md M1].**

| Kalem | Kod standardı | Model v1 → v2 [H] |
|---|---|---|
| Anaokulu | ≥ 0,5 m²/kişi; okul başına 1.500–3.000 m² | 0,50 → 0,51 |
| İlkokul | ≥ 2,0 m²/kişi; okul başına ≥ 5.000 m² | 1,59 → **2,11** |
| Ortaokul | ≥ 2,0 m²/kişi; ≥ 6.000 m² (komşu mahalleyle ortaksa komşu payı ayrıca) | 1,50 → **2,26** |
| Aile sağlık merkezi | 750–2.000 m² parsel. EK-2'deki 1,5 m²/kişi semt ölçeğindeki sağlık tesisleri için yorumlandı (doğrulanmalı) | 1.726 m² |
| Sosyal-kültürel | ≥ 0,75 m²/kişi | 0,74 → **0,84** |
| Teknik altyapı (yol ve otopark hariç) | ≥ 1,0 m²/kişi; bir kısmı kapı servis şeridinde | 0,49 → **1,09** |
| Açık ve yeşil alan | ≥ 10 m²/kişi | 13,2 → 12,3 |

**Otopark (0.2 notu).**

- **Bugünkü kural.** Ek-1 model mahallede (v2.1) 2.481 yer istiyor (konut 2.100 + dükkân 381). Bunun sebebi T1 son durumu ile T2 dubleksinin ≥ 180 m² sınıfına girip 2 yer gerektirmesi.
- **Plan.** 1.235 yer sağlıyor (%50).
- **O1 ile.** Gerek ≈ 1.807'ye iner.
- **Sonuç.** Kod, paket **O1 + O2** (bölgesel otopark alanında azami otopark) ve belediye meclisi kararı olmadan uygulanamaz. md. 8/2'deki küçük parsel indirimi, ihtiyacın yarısının parselde karşılanmasını şart koştuğu için bu modele uygulanamaz [D].

## 6. Tahsis ve yönetişim kuralları

### 6.1 Kamu arsasında tahsis

- Bir yapımcıya ada başına en fazla **40 konut** verilir.
- Parsellerin en az %30'u yapı grubu ve kooperatife ayrılır.
- Etaplama 10–15 yıla yayılır ve 3–4 etapta yapılır (0.1 ile aynı).

### 6.2 Dağıtılmış sosyal konut (0.2, yeni)

- **Tahsis birimi.** Parsel grubudur: T1/T2'de ortak şeridin 30 m'lik kesimi (bahçe grubu), T3'te avlu grubu, T4'te parsel.
- **Hedef paylar.** Kooperatif / yapı grubu %30, kiralık sosyal %20, piyasa %50.
- **Dağılım sınırı.** Her komşuluk biriminde her tür hedef payından en fazla **5 puan** sapabilir. Model v2.1'de en büyük sapma 2,6 puan [H].
- **T2.** Kiralık sosyal konut T2'ye (iki kuşaklı aile evi) verilmez.
- **Zemin erişilebilir daireler.** Kiralık sosyal payında önce 65 yaş üstü ve engelli haneye sunulur.
- **Sonuç.** Model mahallede (v2.1) piyasa payı en az 53 yapımcıya bölünür; tek yapımcının "site" kurması önlenir.

## 7. Tipoloji kataloğu (ön onaylı)

Ayrıntı: `model_mahalle_v2/tipoloji_T1…T4_*.png` ve `tipoloji_asansor_ozeti.png`. Değerler çizimlerden hesaplanmıştır [H].

| Tip | Parsel | Kat | Konut | Net / brüt alan | Emsal · oturum | Dikey dolaşım (0.2) | Bölge |
|---|---|---|---|---|---|---|---|
| **T1 Büyüyebilen sıra ev** | K2 6,4 × 27,4 m (175 m²); K1 7,2 × 27,4 m (196 m²) (0.2.1) | Z+1 → Z+2 + arka oda | 1 (2+1 → 4+1 + büyükler odası) | 176 / 198 m² | 1,13 · %47 | Platform yeri (kiler/dolap dikmesi) | K1, K2 |
| **T2 Avlulu çok kuşaklı ev** | 9,6 × 27,4 m (262 m²) (0.2.1) | Z+2 | 2 (zeminde 2+1 büyükler · üstte 4+1 dubleks) | 291 / 315 m² | 1,20 · %40 | Asansör yeri 1,4 × 1,6 m | K1, K2 |
| **T3 Avlu grubu, güney sıra (0.2.1)** | 36 × 31,4 m (1.130 m²) | Sokak kanadı Z+2 (K3'te Z+3), yan kanatlar Z+1, **arka kanat Z** | 14 (Z+3'te 17); 2'si arka kanatta eşiksiz 2+1 | ≈ 1.200 / 1.642 m²; **kapalı avlu ≈ 330 m²** | Z+2 1,45 · Z+3 ≈ 1,8 · %66 | Z+2: 2 asansör yeri; Z+3: asansör (P4 ile galeri + 1); arka kanat kural dışı | K1–K3 |
| **T3 Avlu grubu, kuzey sıra (0.2.1)** | 36 × 31,4 m | Sokak kanadı Z+2 / Z+3, yan kanatlar Z+1; yanlarda 2,5 m bahçe duvarı | 12 (Z+3'te 15) | ≈ 1.050 / 1.409 m²; avlu ≈ 530 m² (dördüncü kenarı komşu arka kanat) | 1,25 · %48 | Aynı | K1–K3 |
| **T4 Çevre adası çubuğu** | 24 × 27,4 m (658 m²) | Z+3 (köşe Z+4) | 9 daire + 2 dükkân | ≈ 920 / 1.152 m² | 1,75 · %44 | 1 asansör | K3, K4 |
| **T1/T2 köşe evi (0.2)** | Kırpılmış, ≥ 110 m² | Z+2 | 1 (T2 bina ≥ %80 kalırsa 2) | Kırpıntıya göre | — | T1 / T2 gibi | K1, K2 |

## 8. Mevcut mevzuatla karşılaştırma

0.1'deki tablo (`fitrat_kodu_taslak.md` §7) geçerlidir. 0.2'de şu satırlar güncellendi:

| # | Konu | Fıtrat Kodu 0.2 | Mevcut hüküm | Durum | Gereken araç (doğrulanmalı) |
|---|---|---|---|---|---|
| 6 | Asansör | §3.5 tablosu | PAİY md. 34/1 (RG 01.07.2026): 3 katta asansör yeri, ≥ 4 katta asansör (tek BB hariç); md. 34/4 [D] | Uyumlu. Z+3 avlu grubunda maliyet yükü var | Paket P4: galeriyle bağlı en çok üç merdiven evine tek asansör; zeminde ≥ %15 erişilebilir BB |
| 7 | Otopark | Parsel içinde yok; 0,5–0,7 yer/hane | Ek-1: 120 m² üstü dairede yük iki katına çıkar; md. 4/f sırası; md. 8/2 indirimi parselde karşılamaya bağlı [D] | **Çatışma**. Plan, gereğin %48'ini sağlıyor | Paket O1 (hane başına 0,5; ≥ 180 m² 1) + O2 (bölgesel otopark alanı, azami otopark) |
| 15 | Donatı alanları | Güncel EK-2 (§5) | MPYY EK-2, 17.05.2017 değişikliği [D] | Uyumlu (model v2) | — |
| 24 (0.2.1) | Ön eşik 1,0 m, ada ortası geçidi, kapalı avlu | §3.1, §3.6, §4 | PAİY varsayılanı: ön bahçe 5 m, yan ve arka 3 m [D, PAİY md. 23] | **Çatışma** (0.2'deki 1,5 m'de de vardı) | Md. 30 kentsel tasarım projesi ve plan notu; geçit için ifrazda kamuya terk |
| 21 (yeni) | Köşe evi | §3.3 | İfraz şartı plan notuyla belirlenir [DY] | Planla çözülebilir | Plan notunda en küçük köşe parseli (≥ 110 m²) |
| 22 (yeni) | Esnek zemin kat | §3.4 | 634 md. 24: meskende işyeri kullanımı oybirliğine bağlı [D] | Çatışma riski | Kat irtifakında "esnek bağımsız bölüm"; paket K2 |
| 23 (yeni) | Ağaç dikimi | §3.2 | Ağaç örtüsü standardı yok [DY] | Boşluk | Kentsel tasarım projesi eki; paket M3 ile birlikte |

## 9. Açık sorular

1. **Hukuk.** Bahçe mesafesi, nizam, en az kat, köşe evi ve esnek zemin kat kurallarının plan notuyla ne ölçüde kurulabileceği bir imar hukukçusuyla incelenmeli.
2. **Otopark.** O1 ve O2 yürürlüğe girmeden pilotta nasıl ruhsat alınır? Belediye meclisinin md. 8/2 dışındaki yetkisi ne?
3. **Asansör.** Avlu tarafındaki açık galeri ("hayat") ile tek asansör çözümü bugünkü PAİY ve yangın yönetmeliği altında kabul edilir mi?
4. **Ağaç.** Taç yarıçapları ve 20 yıllık örtü, Türkiye iklim bölgelerine göre tür listesiyle kalibre edilmeli.
5. **Okul.** İki küçük ilkokul (≈ 6 ve 10 derslik) MEB norm kadro ve tip proje kurallarıyla nasıl bağdaşır?
6. **Geleneksel doku (0.2.1'de kısmen kapandı).** Kalibrasyon model v2.1'e ve bu sürüme işlendi.
   - **Açık kalanlar:** brüt emsal 0,75–0,9; T1 derinliği; T3/T4'ün ayrı modül binaları (P4'e bağlı); eğimli arazide ızgaranın bükülmesi (gerçek alan).
   - **Sorular:** kapalı avlu gölgesi (kuzey avlunun kışın ≈ %36'sı) kabul edilebilir mi? Kapı altı geçidi 4 m yüksekliğin maliyeti ne?
7. **Güney sıra bahçeleri.** D–B uzun adalarda T1/T2 konutlarının ≈ %44'ünün bahçesi kışın gölgede. Ada yönü kuralı (K–G uzun ada seçeneği) gerçek bir alanda sınanmalı.
