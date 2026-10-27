# Fıtrat Kodu — Biçim Temelli İmar Kodu Taslağı

**Proje:** TR TAMİRAT
**Bölüm:** 07_TASARIM_CIZIM · İP6 (model mahalle ve tasarım)
**Tarih:** 26 Ekim 2026 · **Sürüm:** 0.1 (taslak, tartışma için)
**Eş dosyalar:** `model_mahalle_v1.md` (plan, çizimler, doğrulama) · `tasarim_parametreleri.md` (sayısal standartlar) · `08_MEVZUAT_POLITIKA/mevzuat_politika_haritasi.md` (mevzuat maddeleri)

## İşaret sistemi

| İşaret | Anlamı |
|---|---|
| **[D]** | Doğrulandı: mevzuat metni ya da hakemli kaynak. Mevzuat maddeleri bu çalışmada yeniden okunmadı; proje mevzuat haritasında [D] işaretiyle aktarılan hükümlerdir |
| **[İ]** | İkincil aktarım |
| **[DY]** | Doğrulanmadı: alan bilgisine dayanıyor |
| **[H]** | Bu çalışmada hesaplandı (model mahalle v1) |
| **doğrulanmalı** | Hukuki yorum ya da uygulama yolu önerisidir; hukuki görüş alınmadan kullanılmamalı |

---

## 0. Amaç ve gerekçe

Türkiye'de imar, binayı çoğunlukla **sayılarla** tarif eder: emsal (KAKS), taban alanı (TAKS), bahçe mesafesi ve yola göre kat adedi. Bu sayılar sokağın, avlunun ve komşuluğun biçimini belirlemez. Varsayılan kurallar (ön bahçe 5 m, yan ve arka 3 m, ayrık nizam) sonuçta parselin ortasında duran, çevresi kullanılamaz şeritlerle çevrili apartman üretir [D, PAİY md. 23; mevzuat haritası].

**Fıtrat Kodu** aynı yoğunluğu başka bir biçimle üretmeyi hedefler. Kodun bağlayıcı kısmı sokak cephesi, kat sınırı, avlu ve zemin kat kullanımıdır. Emsal yalnız bilgi için verilir.

**Gerekçe (Faz 2 bulgusuyla uyumlu).** İlçe panelinde bina yüksekliğinin doğurganlığa doğrudan etkisi küçük ve kırılgan çıktı. Kadın eğitimi sabit tutulunca etki bir kat başına ≈ −0,03 çocuktur (`09_RAPORLAR/03_ilce_paneli_il_ici.md`). Bu yüzden kod doğurganlık vaadine dayanmaz. Kodun beş gerekçesi şunlardır:

1. **Sağlık:** yürüme, yeşile yakınlık, düşük trafik.
2. **Çocuk:** okula ve oyuna araç yolu geçmeden, göz altında erişim.
3. **Komşuluk:** avlu grubu, komşuluk birimi, mescit ve meydan.
4. **Kuşaklar arası yakınlık:** aynı parselde iki kuşak, büyüyebilen ev.
5. **Deprem güvenliği:** alçak, düzenli ve genişlemesi baştan hesaplanmış yapı.

## 1. Kodun bileşenleri

| # | Bileşen | İçerik | Bağlayıcılık |
|---|---|---|---|
| 1 | **Düzenleyici plan** | Bölge haritası (K1–K4), sokak tipleri, zorunlu cephe hatları, zorunlu dükkân cepheleri, donatı alanları | Bağlayıcı (plan paftası) |
| 2 | **Kamusal alan standartları** | Sokak kesitleri (S0–S3, diyagonal), ağaç, hız, otopark cepleri | Bağlayıcı (kentsel tasarım projesi) |
| 3 | **Bina biçim standartları** | Bölge başına parsel, cephe hattı, kat, oturum, avlu, zemin kat (§3) | Bağlayıcı |
| 4 | **Tipoloji kataloğu** | T1–T4 ön onaylı tip projeler (§6); katalog dışı projeler §3'ü sağlamalı | Hızlandırıcı (ön onay) |
| 5 | **Mahalle standartları** | Ağ mesafesiyle donatı erişimi, yeşil, otopark payı (§5) | Bağlayıcı (plan notu) |
| 6 | **Tahsis ve yönetişim kuralları** | Yapımcı başına konut, kooperatif payı, sosyal konut dağılımı, etaplama | Kamu arsasında şartname |

## 2. Bölgeler (transect)

| Bölge | Tanım | Model mahallede yeri | Baskın tipoloji |
|---|---|---|---|
| **K1 · Köy kenarı** | Yeşil kuşağa ya da tarıma bakan, en alçak ve en bahçeli doku | Kuzey ve batı kenarı (yeşil kuşak tarafı) | T1, T2; avlu grubu Z+2 |
| **K2 · Mahalle genel** | Yaşam sokaklarıyla örülü konut dokusu; küçük ticaret serbest | Komşuluk birimlerinin içi | T1, T2, T3 |
| **K3 · Mahalle merkezi** | Mahalle caddesi (S1) ve meydan çevresi; zeminde dükkân ve donatı | Artı biçimli cadde boyunca, merkez halkası | T3 (Z+3), T4 |
| **K4 · Semt çarşısı** | Toplayıcı yolun komşu mahalleyle paylaşılan kapıları; mobilite noktası | Güney ve doğu kapıları | T4, mobilite noktası |

Bölge haritası: `model_mahalle/vaziyet_plani.png`, sağ paneldeki küçük harita.

## 3. Bina biçim standartları (bölge tablosu)

Ölçüler parsel bazındadır. "Z+n" zemin üstünde n kat demektir.

| Kural | K1 · Köy kenarı | K2 · Mahalle genel | K3 · Mahalle merkezi | K4 · Semt çarşısı |
|---|---|---|---|---|
| **İzin verilen tipolojiler** | T1, T2, T3 (Z+2) | T1, T2, T3 | T3, T4 | T4, mobilite noktası, donatı |
| **Parsel cephesi** | 6–12 m | 6–40 m | 9–40 m | 12–24 m |
| **Parsel alanı** | 150–400 m² | 150–1.300 m² | 250–1.300 m² | 300–800 m² |
| **Parsel derinliği** | 25–32 m | 25–32 m | 25–32 m | 25–32 m |
| **Nizam** | Bitişik (sıra ev) | Bitişik ya da avlu grubu | Bitişik, sürekli cephe | Bitişik, sürekli cephe |
| **Cephe hattı (sokak sınırından)** | 2,0–3,0 m geri; ön eşik bahçe | 1,5–2,5 m geri | 0–1,5 m | 0 m (sınıra bitişik) |
| **Cephe doluluk oranı** (cephe hattında yapılı cephe / parsel cephesi) | ≥ %60 | ≥ %70 | ≥ %80 | ≥ %90 |
| **Kat (en fazla)** | Z+2 (3 kat) | Z+2; S1 ve köşe parselde Z+3 | Z+3 (4 kat); köşe ve nirengi Z+4 | Z+3; köşe Z+4 (5 kat) |
| **Kat (en az)** | — | — | S1 cephesinde Z+2 | Z+2 |
| **Saçak yüksekliği (en fazla)** | 9,5 m | 9,5 m (S1 cephesi 12,5 m) | 13,5 m (köşe 16,5 m) | 13,5 m (köşe 16,5 m) |
| **Kat yüksekliği** | Konut 3,0–3,3 m | Konut 3,0–3,3 m | Zemin ≥ 4,5 m (dönüşebilir), üst katlar 3,0–3,3 m | Zemin ≥ 4,5 m, üst katlar 3,0–3,3 m |
| **Yapı oturumu (en fazla)** | %50 | %55 | %60 | %65 |
| **Emsal (bilgi; biçim kuralı bağlar)** | ≈ 1,2 | ≈ 1,5 | ≈ 1,8 | ≈ 2,2 |
| **Özel bahçe / avlu asgarisi** | T1: ≥ 70 m² arka bahçe; T2: hane başına ≥ 50 m² ortak avlu | K1 gibi; T3: hane başına ≥ 30 m² ve grup başına ≥ 350 m² ortak avlu | T3: hane başına ≥ 20 m² ortak avlu; her daireye ≥ 6 m² balkon ya da teras | Parselin ≥ %25'i arka avlu; her daireye ≥ 6 m² balkon |
| **Ada içi ortak bahçe** | T1/T2 adalarında ≥ 8 m genişlikte orta şerit | Aynı | Avlu gruplarının avluları ada ortasında birleşir | — |
| **Zemin kat kullanımı** | Konut; ev-işyeri (zemin alanının ≤ %30'u); mescit ve kreş serbest | Konut; köşe parselde dükkân, atölye, kreş, mescit serbest | S1 ve meydan cephesinin ≥ %60'ı konut dışı (dükkân, ofis, atölye, donatı) | Toplayıcı ve S1 cephesinin %100'ü konut dışı; konut girişi ≤ %20 cephe |
| **Zemin kat kotu** | Konut: sokaktan 0–0,45 m; erişilebilir dairelerde eşiksiz giriş | Aynı | Ticari: sokakla aynı kot | Ticari: sokakla aynı kot |
| **Otopark** | Parsel içinde yok; engelli ya da yaşlı hanesi için kapı önünde 1 cep | Parsel içinde yok | Parsel içinde yok; yükleme cebi S1'de | Mobilite noktası (bölgesel otopark) burada |
| **Bisiklet** | Konut başına ≥ 2 güvenli yer (parsel içi) | Aynı | Aynı; kapı altında bisiklet odası | Mobilite noktasında ortak park |
| **Cephe aldığı sokak** | S2, toplayıcının yeşil kuşak kenarı (park yolu) | S2 (S3 yalnız ikincil cephe) | S1, S2, meydan | Toplayıcı, S1 |
| **Çatı** | Eğik (≈ 30°) ya da teras | Eğik ya da teras | Teras ya da eğik | Teras |
| **Ağaç** | Parsel başına ≥ 1 | Parsel başına ≥ 1; T3 avlusunda ≥ 3 | T3 avlusunda ≥ 3 | Arka avluda 100 m² başına ≥ 1 |
| **Parsel birleştirme** | En fazla 2 parsel | En fazla 2 parsel (T3 tek parsel) | Ada başına en fazla 40 konut aynı yapımcıya | Aynı |

### 3.1 Bütün bölgelerde ortak kurallar

1. **Sokağa bakış.** Her konutun sokak cephesinde en az bir yaşam odası (salon ya da mutfak) penceresi bulunur. Sokak cephesinde kör duvar en fazla 6 m olabilir. Bu "sokakta göz" ilkesi çocuk ve yaşlı güvenliği içindir.
2. **Avluya bakış.** Avlu grubu ve çevre adasında her daire avluyu da görür. 2+1 ve daha büyük dairelerde çift cephe zorunludur.
3. **Konut karması.** 40'tan fazla konutlu her geliştirmede konutların ≥ %55'i 3+1 ve üstü, %5–10'u 1+1 olur. Konutların ≥ %15'i çok kuşaklı kullanıma uygundur (T2 ya da genişleme payında büyükler odası olan T1).
4. **Büyüme payı.** T1'de arka oda ve 2. kat; T3 ve T2'de yalnız katalogdaki kat. Büyüme payı statik projede baştan hesaplanır ve ruhsat ekinde gösterilir.
5. **Deprem.**
   - Plan ve düşey düzenlilik sağlanır; taşıyıcı açıklıklar kısa tutulur (≤ 5–6 m).
   - Dükkânlı zemin katlarda çekirdek perdeleri ve parsel arası duvarlar zemine kadar kesintisiz iner (yumuşak kat önlemi).
   - Bu kurallar Türkiye Bina Deprem Yönetmeliği'nin (TBDY 2018) yerine geçmez; ona ek koşuldur (doğrulanmalı).
6. **Işık.**
   - S2'de güney cephenin saçağı 9,5 m'yi geçmez. Böylece 21 Mart öğlesinde karşı cephe tümüyle güneşte kalır; model kesitte 21 Aralık öğlesinde karşı cephenin 2,3 m'ye kadarı gölgededir [H].
   - T12 adalarında güneye bakan bahçeler T2'ye verilir.
7. **Ağaç ve su.** Sokak ağacı S1 ve toplayıcıda 10 m, S2'de 12 m arayla dikilir. Ön eşik ve bahçe yüzeylerinin ≥ %50'si geçirimlidir. Yağmur suyu S3 ve diyagonallerde yüzeyde toplanır.
8. **Mahremiyet.** Konut zemin katında mahremiyet kot farkıyla değil, ön eşik bahçesi, alçak duvar (≤ 0,9 m) ve bitkiyle sağlanır. Böylece erişilebilirlik bozulmaz.

## 4. Kamusal alan standartları (sokak tipleri)

Kesitler: `model_mahalle/sokak_kesitleri.png`.

| Tip | Kamusal genişlik | Bileşenler (soldan sağa) | Hız | Otopark | Ağaç | H/W (model) | Bölgeler |
|---|---|---|---|---|---|---|---|
| **S0 · Toplayıcı (mahalle dışı)** | 24 m | Kaldırım 3,0 · bisiklet 2,0 · ağaç/park 2,5 · şerit 3,25 · refüj 2,5 · şerit 3,25 · ağaç/park 2,5 · bisiklet 2,0 · kaldırım 3,0 | 50 km/s (öneri; doğrulanmalı) | Ağaç şeridinde cep | İki yan + refüj, 10 m | 0,56 | K1 kenarı, K4 |
| **S1 · Mahalle caddesi / çarşı** | 18 m | Kaldırım 3,75 · ağaç/durak 2,0 · şerit 3,25 · şerit 3,25 · ağaç/park cebi 2,0 · kaldırım 3,75 | 30 km/s; meydanda yalnız otobüs ve acil araç geçer | Kısa süreli ve yükleme cebi | İki yan, 10 m | 0,69 | K3, K4 |
| **S2 · Yaşam sokağı** | 10 m | Yaya 2,0 · ağaç/park cebi 2,0 · paylaşımlı yüzey 4,0 · yaya 2,0; kot farkı yok | ≤ 20 km/s (yürüme hızı) | Yalnız engelli, yaşlı ve yükleme cebi | Tek yan, 12 m | 0,54 (çekirdek) / 0,64 (son durum) | K1, K2, K3 |
| **S3 · Yaya ara sokağı / geçit** | 6 m | Yağmur bahçesi 1,5 · yürüme 3,0 (acil araç) · oturma ve bitki 1,5 | Araçsız | Yok | Küçük ağaç ve yağmur bahçesi | 1,25 | K2, K3 (ikincil cephe) |
| **Yeşil diyagonal** | 8 m | Yürüme ve bisiklet yolu, iki sıra ağaç | Araçsız | Yok | İki sıra, 8 m | — | Köşeden meydana |

**Hücre ilkesi.** Mahalle dört araç hücresine bölünür. Araç her hücreye toplayıcı yoldan girer ve aynı yerden çıkar. Meydanda yalnız otobüs, bisiklet ve acil durum araçları geçebilir. Bu ilke Houten'den ve süper bloklardan alınmıştır (`02_LITERATUR/ornek_uygulamalar.md` §1.2 ve §1.6).

**Okul sokağı.** İlkokul ve anaokulu önündeki S2'ler okul giriş ve çıkış saatlerinde araca kapalıdır.

## 5. Mahalle düzeyi standartlar (plan notu önerisi)

Bütün mesafeler **yaya ağı mesafesidir**: konut kapısından donatı girişine sokak, geçit ve park yolları üzerinden ölçülür. Hedef her konutun %100'üdür. Sağ sütun model mahallede elde edilen değerdir [H].

| Donatı | Kod standardı (ağ) | MPYY md. 12 [D] | Model mahalle v1 [H] |
|---|---|---|---|
| İlkokul | ≤ 500 m | ≈ 500 m | %96,8 (en uzak 553 m) |
| Ortaokul | ≤ 1.000 m | ≈ 1.000 m | %100 |
| Anaokulu ya da kreş | ≤ 400 m | ≈ 500 m | %100 |
| İbadet yeri (mescit ≤ 150 m ya da küçük cami ≤ 250 m ya da semt camii ≤ 400 m) | Kademeli kural | 150 / 250 / 400 m | %99,3 |
| Aile sağlık merkezi | ≤ 500 m | ≈ 500 m | %96,5 |
| ≥ 0,5 ha kamusal yeşil | ≤ 300 m (hedef 200 m) | Çocuk bahçesi ≈ 500 m | %100 (≤ 200 m'de %96,1) |
| Kapı önü oyun alanı (avlu ya da ada içi ortak bahçe) | ≤ 100–150 m | — | %100 |
| Açık spor sahası | ≤ 500 m | Semt spor alanı ≈ 500 m | %100 |
| Bakkal, fırın ya da dükkân | ≤ 300 m | — | %100 |
| Otobüs durağı | ≤ 400 m (hedef 300 m) | — | %100 (≤ 300 m'de %99,1) |
| Bölgesel otopark | ≤ 400 m; hane başına 0,5–0,7 yer | — | %100; 0,56 yer/hane |
| Kamusal yeşil | ≥ 10 m²/kişi | 10 m²/kişi (EK-2) [İ] | 13,2 m²/kişi |
| Komşuluk birimi | 150–300 hane, her birinde mescit, ≥ 0,5 ha yeşil, bakkal, çeşme | — | 214–328 hane |

## 6. Tipoloji kataloğu (ön onaylı)

Ayrıntı: `model_mahalle/tipoloji_T1…T4_*.png`. Değerler çizimlerden hesaplanmıştır [H].

| Tip | Parsel | Kat | Konut | Net / brüt alan | Emsal · oturum | Bölge |
|---|---|---|---|---|---|---|
| **T1 Büyüyebilen sıra ev** | 6,3 × 27,4 m (173 m²) | Z+1 çekirdek → Z+2 + arka oda | 1 (2+1 → 4+1 + büyükler odası) | 173 / 195 m² (son durum) | 1,13 · %47 | K1, K2 |
| **T2 Avlulu çok kuşaklı ev** | 9,2 × 27,4 m (252 m²) | Z+2 | 2 (zemin 2+1 büyükler · üst 4+1 dubleks) | 280 / 304 m² | 1,20 · %40 | K1, K2 |
| **T3 Avlu grubu** | 36 × 31,4 m (1.130 m²) | Sokak kanadı Z+2 (K3'te Z+3), yan kanatlar Z+1 | 12 (K3'te 15) | ≈ 1.050 / 1.409 m²; avlu ≈ 440 m² | 1,25 · %48 | K1–K3 |
| **T4 Çevre adası çubuğu** | 24 × 27,4 m (658 m²) | Z+3 (köşe Z+4); zemin 4,5 m dükkân | 9 daire (2+1 · 1+1 · 2+1 her katta) + 2 dükkân | ≈ 920 (konut ≈ 695) / 1.152 m² | 1,75 · %44 | K3, K4 |

---

## 7. Mevcut mevzuatla karşılaştırma

Sütun 3'teki hükümler proje mevzuat haritasından aktarılmıştır (o çalışmada [D]). Planlı Alanlar İmar Yönetmeliği (PAİY), Resmî Gazete 03.07.2017, sayı 30113; son değişiklik 01.07.2026 (mevzuat haritasına göre). Sütun 5'teki araçlar **öneridir ve doğrulanmalıdır**. Burada hiçbir hukuki sonuç kesin olarak ileri sürülmemektedir.

| # | Konu | Fıtrat Kodu | Mevcut hüküm (kaynak) | Durum | Gereken araç / değişiklik (doğrulanmalı) |
|---|---|---|---|---|---|
| 1 | Ön bahçe | Cephe hattı 0–3 m | PAİY md. 23: ön bahçe ≥ 5 m, yan ve arka ≥ 3 m; 4 kattan fazlasında her ek kat için +0,50 m [D] | Çatışma (varsayılan kural) | Planda ve plan notunda bölge başına cephe hattı; MPYY md. 30 kentsel tasarım projesi [D]. PAİY'nin planla farklı bahçe mesafesine ne ölçüde izin verdiği **doğrulanmalı**. Kalıcı çözüm: PAİY'ye "biçim temelli kod alanı" tanımı |
| 2 | Nizam | Bitişik nizam ve avlu grubu | Plan nizam belirlemezse ayrık nizam kurguları uygulanır; sonuç kule apartmandır [D, mevzuat haritası özeti] | Çatışma (varsayılan) | Plan lejantında bitişik ya da blok nizam ve avlu grubu gösterimi. EK-1 gösterimlerinin 2026 değişikliği incelenmeli [İ] |
| 3 | Taban alanı (TAKS) | %50–65 (parsel bazında) | PAİY md. 5(6): plan vermiyorsa ≤ %40, bazı koşullarda %60 [D] | Planla çözülebilir | Bölge başına TAKS'ın plan kararı olarak verilmesi |
| 4 | Kat adedi | Bölge başına en fazla ve en az kat; konutta 5 katın üzeri yok | PAİY md. 9: plan kat göstermiyorsa kat adedi yol genişliğine göre (≤ 7 m: 2 kat … > 50 m: 18 kat) [D]; 3194 md. 8: bina yükseklikleri serbest bırakılamaz [D] | Planla çözülebilir | Planda saçak kotu ve kat adedi. "En az kat" kuralının hukuki dayanağı **doğrulanmalı** |
| 5 | Kat yüksekliği | Konut 3,0–3,3 m; K3–K4'te zemin ≥ 4,5 m zorunlu | PAİY md. 28: konut katı 3,60 m (3 kattan az binada 4,00 m); ticari zemin 4,50 m; iç yükseklik ≥ 2,60 m [D] | Uyumlu (üst sınırların altında) | Zorunlu 4,5 m "dönüşebilir zemin kat" için plan notu |
| 6 | Asansör | Z+3'te zorunlu, Z+2'de yer ayrılır | PAİY md. 5(27): 3 katta asansör yeri, 4 ve daha fazla katta zorunlu (tek bağımsız bölümlüler hariç); md. 34 ve 59(5) 01.07.2026'da değişti [D] | Uyumlu | T2'nin (3 kat, 2 bağımsız bölüm) ve T1 genişlemesinin durumu **doğrulanmalı** |
| 7 | Otopark | Parsel içinde otopark yok; mobilite noktasında 0,5–0,7 yer/hane (azami) | Otopark Yönetmeliği md. 4/a: ihtiyaç parselde karşılanır; md. 4/f: önce ortak ve ada içi, sonra bölge ya da genel otopark ve bedel; md. 8/2: küçük parselde konut ihtiyacı en fazla %50 azaltılabilir; md. 12–13: bedel yalnız otoparka harcanır [D]. 2026 MPYY değişikliği bölgesel otopark yolunu açtı [İ] | Kısmi çatışma | Plan notu ve belediye meclisi kararıyla bölge otoparkına yönlendirme (md. 4/f sırası nedeniyle **doğrulanmalı**). Yönetmelik değişikliği: toplu taşıma koridorunda azami otopark, bedelin yaya ve bisiklet güvenliğine harcanabilmesi |
| 8 | Yol genişliği ve mahreç | S2 10 m, S3 6 m; S3'e cephe veren parsel yok | MPYY md. 26(6)(c): gelişme alanında trafik yolu ≥ 10 m, yaya yolu ≥ 3 m; parsel 7 m'den dar yoldan mahreç alamaz [D] | Uyumlu | — |
| 9 | Cephe arası mesafe | S2'de 14 m, S1'de 19,5 m | MPYY md. 26(5)(b): kat artıran plan değişikliğinde K = [(Y1+Y2)/2] + 7 m; model kesitlerde bu S2 için 14,5 m, S1 için 20,5 m eder [D/H] | Yeni planda geçerli değil (yorum) | Kuralın yalnız plan değişikliklerinde arandığı yorumu **doğrulanmalı**; kentsel dönüşümde S2 kesiti için istisna gerekebilir |
| 10 | Karma kullanım | K3–K4'te zemin kat konut dışı zorunlu; K1–K2'de küçük ticaret ve atölye serbest | "Konut alanı" lejantı zemin kat ticaretini kısıtlayabilir [DY]; 634 sayılı Kat Mülkiyeti Kanunu md. 24: meskende dükkân gibi kullanımlar oybirliğine bağlı [D] | Çatışma riski | Plan notunda zemin kat kullanım listesi; kat irtifakında zemin katın baştan "dükkân" ya da "esnek" bağımsız bölüm olarak tescili (**doğrulanmalı**) |
| 11 | Çatı arası | T1'de çatı katı ve çatı terası | PAİY md. 40: mahya ≤ 5,00 m; çatı arasına bağımsız bölüm yapılamaz [D] | Muhtemelen uyumlu | Çatı arasının alttaki dairenin parçası olarak kullanımı (**doğrulanmalı**); öneri: az katlı binalarda çatı arası kullanımının esnetilmesi |
| 12 | Çıkma ve cumba | ≤ 1,0 m, ağaç ve ışık koşuluyla | PAİY md. 41: çıkmalar ≤ 1,50 m [D] | Uyumlu | — |
| 13 | Mescit ve oyun alanı | 16 mescit (12 zemin kat, 4 cep parkında küçük yapı) ve her avlu grubunda kapı önü oyun alanı | PAİY md. 19(h): 75'ten fazla bağımsız bölümde mescit ve çocuk oyun alanı; md. 53: 250 m içinde cami varsa mescit şartı aranmaz [D] | Uyumlu, ötesinde | Mescidin "komşuluk odası" olarak çok amaçlı tasarlanabilmesi |
| 14 | Kreş | Mahalle ölçeğinde zemin kat kreşleri (≤ 400 m) | PAİY md. 19(f)(5): 15.000 m²'yi ya da 150 bağımsız bölümü aşan parselde gündüz bakımevi; md. 5(8): 150 m²'si emsal dışı [D] | Uyumlu; eşik küçük parsellerde devreye girmiyor | Eşiğin parsel yerine ada ya da mahalle ölçeğinde tanımlanması |
| 15 | Donatı alanları | EK-2 m²/kişi değerleri sağlanır | MPYY EK-2 [İ, TBB aktarımı]; md. 12 mesafeleri [D] | Uyumlu | — |
| 16 | Yürüme mesafesi tanımı | Yaya ağı mesafesi | MPYY md. 12: "takriben … metre"; kuş uçuşu mu ağ mı belirtilmiyor [D] | Belirsiz | Plan notunda "yaya ağı mesafesi" tanımı |
| 17 | Kat ilavesi (büyüme) | T1 genişlemesi; T2 ve T3'te katalog katları | Kat Mülkiyeti md. 44: kat ilavesi oybirliğine bağlı [D] | Çok malikli yapıda risk | Tek malikli T1'de sorun beklenmez; T2 ve T3'te kat irtifakı kurulurken genişleme hakkının önceden tanımlanması (**doğrulanmalı**) |
| 18 | Parsel bölme | En az 6 m cephe ve 150 m² | İfraz şartı plan notuyla belirleniyor [DY] | Planla çözülebilir | Plan notu |
| 19 | Yapımcı başına konut | Ada başına en fazla 40 konut aynı yapımcıya | Mevzuatta karşılığı bulunamadı [DY] | Boşluk | Kamu arsasında tahsis şartnamesi (TOKİ, Emlak Konut, belediye) |
| 20 | Deprem | Alçak ve düzenli yapı; yumuşak kat önlemi; büyüme payı statik projede | TBDY 2018 [D: yönetmelik adı; maddeler bu çalışmada okunmadı] | Tamamlayıcı | Kod TBDY'ye ek koşul getirir, onun yerine geçmez; uyum mühendislik incelemesiyle **doğrulanmalı** |

### 7.1 Uygulama yolu (öneri; doğrulanmalı)

1. **Kısa vade (pilot):** Kamu arsasında uygulama imar planı ve plan notları. MPYY md. 30 kapsamında kentsel tasarım projesi ve tasarım rehberi [D]. Belediye meclisi otopark kararı. Tip proje kataloğunun ön onayı.
2. **Orta vade:** PAİY'ye isteğe bağlı bir "biçim temelli kod alanı" bölümü eklenmesi. Bu bölüm md. 9, 23 ve 5(6) varsayılanlarının yerine bölge tablosunu koyar. Otopark Yönetmeliği'ne azami otopark ve bölge otoparkı önceliği eklenmesi.
3. **İzleme:** Her pilot mahallede `tasarim_parametreleri.md` §9.8 göstergeleri (çocukların okula yürümesi, kaza, yeşile erişim, komşuluk) önce ve sonra ölçülür.

## 8. Açık sorular

1. **Hukuk.** Bahçe mesafesi, nizam ve en az kat kurallarının plan notuyla ne ölçüde değiştirilebileceği bir imar hukukçusuyla incelenmeli. Bu çalışmada hiçbir hukuki görüş alınmadı.
2. **Otopark.** Otopark Yönetmeliği md. 4/f'deki öncelik sırası (önce ada içi, sonra bölge otoparkı) "parsel içinde otopark yok" kuralıyla nasıl bağdaşır? Belediye meclisinin yetkisi ne kadar?
3. **Kat Mülkiyeti.** T2 ve T3'te büyüme payının ve zemin kat esnek kullanımının kat irtifakına nasıl yazılacağı belirsiz.
4. **Deprem ve maliyet.** Z+2 / Z+3 bitişik nizam yapının TBDY 2018 kapsamındaki tasarım ve maliyet karşılaştırması 06_SIMULASYON ayağında yapılmalı.
5. **Bölge eşikleri.** Parsel cephesi, oturum ve saçak sınırları tek bir model mahalleden türetildi. Eğimli arazide (teraslama) ve dar parselli tarihî dokularda sınanmalı.
6. **Karşı mahalle.** K4 ve toplayıcı yolun karşı yakası (komşu mahalle) aynı kodla mı planlanacak? Semt ölçeğinde bir kod gerekir.
