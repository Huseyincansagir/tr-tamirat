# Faz 3 Sentezi — Mahalle Ölçeğinde Ne Öğrendik, Model Mahalle Nereye Vardı?

*26 Ekim 2026 · Sürüm 0.1*

| # | Çıktı | Soru | Ana sonuç |
|---|---|---|---|
| 10 | [Mahalle düzeyinde FUE](10_fue_mahalle.md) | Pilot ilçelerin mahalleleri fıtrata ne kadar uygun? Endeks gerçekten "insana iyi geleni" ölçüyor mu? | Endeks **iki ters eksene** ayrıldı. Çevre-ölçek (Ç) ölümlülükle doğrulandı, erişim (E) doğrulanmadı |
| 11 | [Geleneksel doku morfolojisi](11_geleneksel_doku_morfolojisi.md) | Geleneksel doku hangi ölçülerde çağdaştan ayrılıyor? | Fark yükseklikte değil, **tane büyüklüğünde**. Zaafları: yeşil, dar sokak, boşalan çekirdek |
| 13 | [Uydu verisiyle çevre-ölçek ekseni (FUE v0.2)](13_fue_uydu_cevre.md) | Ağaç, PM2.5, yüzey sıcaklığı ve yapılı alan Ç'yi güçlendirir mi? | Evet: ölümlülükle ilişki −0,27'den **−0,41**'e. Yükseklik etkisi çevre yükleriyle açıklanıyor |
| — | [Model mahalle v2 / v2.1](../07_TASARIM_CIZIM/model_mahalle_v2.md) · [Fıtrat Kodu v0.2.1](../07_TASARIM_CIZIM/fitrat_kodu_taslak_v2.md) | v1'in açıkları kapanabilir mi? Morfoloji dersleri uygulanabilir mi? | İki ilkokulla %100 erişim; ada içi geçit, kapalı avlu. FUE'de **E 82, Ç 63**, hedef çeyrekte |

Bütün çıktılar betiklerle yeniden üretildi; sonuçlar birebir aynı çıktı (FUE, morfoloji, model mahalle v2 ve v2.1).

---

## 1. Altı bulgu

1. **"Fıtrata uygun mahalle" tek bir eksen değil.**
   - Mahalle ölçeğindeki 18 gösterge iki aileye ayrılıyor:
     - **Erişim (E):** okul, cami, market, durak, oyun alanına yürüyerek ulaşmak.
     - **Çevre-ölçek (Ç):** yeşil, az kat, ana yoldan uzaklık, yayılmama, küçük mahalle.
   - 300 kentsel pilot mahallede bu iki eksen ters ilişkili (ρ = −0,61). İkisinde birden medyanın üstünde olan mahalle yalnızca **39**.
   - Türkiye'de erişimin iyi olduğu yer eski kent merkezi; çevre-ölçeğin iyi olduğu yer çeper.
2. **Sağlıkla doğrulanan eksen çevre-ölçek.**
   - 973 ilçede, il içinde, kadın eğitimi ve göç sabitken Ç'si yüksek ilçelerde standartlaştırılmış ölümlülük daha düşük (β = −0,27; kentsellik ve yaş yapısı kontrolleriyle −0,17; hepsi p<0,001).
   - Erişim ise aynı koşullarda daha **yüksek** ölümlülükle ilişkili (β = +0,44 / +0,31). Bu büyük olasılıkla eski merkezlerin bileşiminden kaynaklanıyor: yaşlı ve yoksul nüfus, kurumsal nüfus, hava kirliliği, OSM kaydı.
   - Bu yüzden ilk tasarımıyla FUE geçerlilik sınavını geçemedi. **FUE v0.2 iki eksenli** raporlanacak.
3. **Faz 2'nin en sağlam bulgusu yarıya indi.**
   - Erişim ve kent merkezi payı kontrol edilince yaşanan bina yüksekliğinin ölümlülükle ilişkisi kat başına %2,56'dan **%1,25–1,37'ye** iniyor (p = 0,03–0,06).
   - Dikeyleşmenin kendine özgü bir etkisi kalıyor, ama etkinin yarısı genel kentsellikten geliyor. Faz 2 raporları ve kavramsal çerçeve düzeltildi.
4. **Geleneksel dokunun dersi: küçük tane, sık ağ, sınırlı yükseklik.**
   - 7 geleneksel ve 6 çağdaş alanın medyanlarını karşılaştırınca:

     | Ölçüt | Geleneksel | Çağdaş |
     |---|---|---|
     | Bina tabanı | 118 m² | 347 m² |
     | Sokağa bakan cephe | 6–9 m | 12–18 m |
     | Ada (yaya dahil ağ) | 0,36 ha | 0,68 ha |
     | Kavşak yoğunluğu | 315/km² | 221/km² |

   - Yapı oturumu ise yakın (%30'a karşı %25). Yani fark yükseklikte değil, **tanede ve ağda**.
   - Silivri merkezinin eski kasaba ızgarası çağdaş binalarla bile geleneksel değerlere yakın. Ada ve ağ ölçüsünü yapı tipinden çok plan belirliyor.
5. **Geleneksel doku örnek alınmamalı olan yönleriyle de ölçüldü.**
   - **Yeşil:** Kamusal yeşil 0,3–2,5 m²/kişi; MPYY'nin 10 m²'sinin beşte biri.
   - **Dar sokak:** Antakya'da sokak örneklerinin %27'sinde cephe arası 6 m'nin altında; acil erişim ve enkaz açısından kritik.
   - **Gölge:** Zeyrek'te örneklerin %58'inde H/W > 1; kışın zemin kat gölgede.
   - **Boşalan çekirdek:** Safranbolu Çarşı'da yalnızca 28 kişi/ha oturuyor. Doku korunmuş ama boşalmış.
   - Ancak dengeyi en iyi kuran pilot yine **Safranbolu**: kentsel mahallelerinin 5/8'i, nüfusunun %61'i iki eksende de medyanın üstünde.
6. **Model mahalle v2.1 hedef çeyreğe girdi.**
   - **Okul:** İkinci ilkokulla bütün konutlar 500 m içinde (v1: %96,8).
   - **Morfoloji kalibrasyonu:**
     - ada ortası geçitler (22'den 43'e),
     - yaya adası medyanı 0,79'dan 0,45 ha'ya,
     - kavşak yoğunluğu 242'den 303/km²'ye,
     - kapalı avlu 0'dan 0,83/ha'ya,
     - S2 H/W 0,72'den 0,78'e.
   - **Korunanlar:** ağaç örtüsü %31, yeşil 12,3 m²/kişi, ≤3 katlı konut %70, 5 kat üstü yok.
   - **FUE konumu:** **E 82, Ç 63**. Pilotlarda E ≥ 60 ve Ç ≥ 55 olan 8 mahalle var; en yükseğinin Ç'si 62,9.
   - **Bedeli:**
     - T1 payı %22,8 (hedef 29).
     - Net konut alanı 26,5 ha.
     - Otopark mevcut yönetmeliğin gerektirdiğinin yalnızca %50'si. Plan ancak O1 ve O2 otopark reformlarıyla ruhsat alabilir.

---

## 2. Tez nasıl değişti?

| Faz 2 sonrası | Faz 3 sonrası |
|---|---|
| Mekânın en net izi sağlıkta: kat başına ≈ +%2,5 ölümlülük | Sağlık izi **çevre-ölçek ekseninde**: yeşil, alçak doku, trafikten uzaklık, yayılmama. Dikeyleşmenin kendine özgü payı kat başına ≈ %1,3 |
| Fıtrata uygun şehir aileye zaman, para, güvenlik ve bağımsızlık kazandırır | Aynı tez, iki eksenli bir hedefle: **erişimi çevre-ölçeği bozmadan sağlamak.** "15 dakikalık şehir" tek başına yeterli değil; Türkiye'de erişim, yoğun ve yorucu merkezle birlikte geliyor |
| Plan kalitesi önemli (Başakşehir, Nilüfer) | Başakşehir'in iyi sağlık sonucu Ç ile açıklanmıyor (pilotların en düşük Ç'si). Pozitif sapmanın kaynağı büyük olasılıkla nüfus bileşimi ve kurumlar; nitel inceleme gerekli |
| Geleneksel doku referans | Referans olan şey **tane, ağ ve kat sınırı**. Yeşil, sokak genişliği ve güneş geleneksel dokudan alınmamalı |

**Güncel çalışma tezi:**

> Fıtrata uygun mahalle, günlük ihtiyaçlara yürüyerek ulaşılan (E) ama bunun bedelini yükseklik, trafik ve yeşilsizlikle ödetmeyen (Ç) mahalledir. Geleneksel dokudan küçük taneyi ve sık ağı, çağdaş standartlardan yeşili, güneşi ve acil erişimi alır.
>
> Sağlık gerekçesi bugün ölçülebilir düzeyde çevre-ölçek eksenine dayanıyor. Erişim ekseninin gerekçesi (zaman, çocuk ve yaşlı bağımsızlığı, araç bağımlılığı) henüz ampirik olarak sınanmadı. Bir sonraki ölçümün konusu bu.

---

## 3. Veri altyapısına eklenenler

| Katman | Kapsam | Dosya |
|---|---|---|
| Mahalle nüfusu 2025 (18+ / 0–17) | 10 ilçe, 658 mahalle | `03_VERI/islenmis/pilot_mahalle_nufus_2025.csv` |
| Mahalle sınırları | OSM (Türkiye geneli 13.872), TKGM (10 ilçe, 810), birleştirilmiş pilot birimleri (654) | `03_VERI/islenmis/pilot_osm/idari_sinirlar.gpkg`, `pilot_mahalle_tkgm.gpkg`, `pilot_mahalleler.gpkg` |
| OSM donatı noktaları | Türkiye geneli 302 bin: okul, cami, sağlık, eczane, market, dükkân, durak, raylı, oyun, buluşma | `03_VERI/islenmis/pilot_osm/donati_noktalari.parquet` |
| Yaya ağı ve binalar | 10 pilot kutusu: 2,36 milyon kenar, 793 bin bina | `03_VERI/islenmis/pilot_osm/` |
| FUE-lite | 973 ilçe, 16 gösterge, E ve Ç | `03_VERI/islenmis/ilce_fue_lite.csv` |
| Morfoloji | 13 alan + model, ≈50 ölçüt; Microsoft ayak izleri (4 karo) | `05_ANALIZ/sonuclar/morfoloji_karsilastirma.csv`, `03_VERI/ham/bina/` |
| Erişim yolları | MEDAS mahalle düzeyi, TKGM MEGSİS API | `03_VERI/ham/tuik/mahalle_kaynaklar.md`, `03_VERI/kod/tkgm_mahalle.py` |

---

## 4. Açık sorular ve kararlar

### Kullanıcı kararı gerekenler
1. **Kurum verisi talepleri:** OSM'deki donatı kaydı ilçeden ilçeye çok değişiyor. 10.000 kişiye düşen cami kaydı 1,5 ile 12,4, dükkân kaydı 3 ile 168 arasında. E'yi ilçeler arasında güvenilir kılmak için şu kurumlardan adresli listeler gerekiyor:
   - MEB (okul),
   - Diyanet (cami),
   - Sağlık Bakanlığı (ASM ve eczane),
   - büyükşehir belediyeleri (GTFS).
   Bunlar resmî talep ya da açık veri başvurusu gerektirebilir.
2. **Uydu verisi indirme onayı:** ESA WorldCover 10 m (ağaç ve yeşil), Copernicus CAMS (PM2.5), Landsat (yüzey sıcaklığı). Pilot ilçeler için birkaç yüz MB. Ç'nin yeşil bileşenini ve E–ölümlülük ilişkisinin çevre açıklamasını sınamak için.
3. **Saha anketi ortaklığı (Faz 2'den açık):** Rapor 10 §3.3, anket için mahalle adaylarını verdi. İkisinde birden iyi 8 mahalle, iki karşılaştırma çiftinin karşıt mahalleleriyle eşleştirilecek. Etik kurul ve izin süreci kullanıcıda ve ortaklarda.
4. **Mikro veri başvuruları (Faz 2'den açık).**

### Analiz ve tasarım gündemi (Faz 4)
1. **Simülasyon v2:**
   - C ortamındaki "zemine açılan hane ≈ %90" varsayımı planda %62,6 çıktı; düzeltilecek.
   - Paydaş oyununda otopark reformu (O1, O2) olmadan planın ruhsat alamadığı gerçeği işlenecek.
   - E ekseninin zaman ve bağımsızlık kazancı sayısallaştırılacak.
2. **Deprem pilotları:**
   - Antakya ve Onikişubat'ta deprem sonrası güncel bina verisi.
   - TOKİ ve yeniden yapılanma projelerinin FUE v0.2 ve morfoloji ölçütleriyle karşılaştırılması.
3. **Pozitif sapma incelemesi:** Başakşehir ve Nilüfer. Ç'si düşük olduğu halde sağlık sonucu neden iyi?
4. **Model mahalle v3:**
   - güney sıra bahçelerinin kış gölgesi (%44),
   - kapı altı geçidi (3,1 m'ye karşı gereken 4 m),
   - ASM ve konak erişimi (%95–96),
   - zemin kattaki 208 konut dışı birimin esnaf için fazlalığı,
   - T1 hedefinin %22–25'e çekilmesi.
5. **FUE–ölümlülük ilişkisinden kurumsal nüfusun ayrıştırılması:** Bakım evleri ve hastane çevresi.

---

## 5. Güncelleme (27.10.2026): uydu verisi

[Faz 3 · Rapor 3](13_fue_uydu_cevre.md) çevre-ölçek eksenine dört uydu göstergesi ekledi: ağaç örtüsü, PM2.5, yaz yüzey sıcaklığı, yapılı alan payı. Sonuçlar bu sentezin iki bulgusunu güncelliyor:

- **Bulgu 2 güçlendi.**
  - Ç v0.2'nin ölümlülükle ilişkisi β = −0,41\*\*\* (kentsellik ve yaş yapısı kontrolüyle −0,24\*\*\*).
  - Sinyal en çok PM2.5'te (+0,23\*\*\*), yapılı alan payında (+0,27\*\*\*) ve ağaç örtüsünde (−0,14†; temel modelde −0,34\*\*\*).
  - Erişimin ölümlülükle ters yöndeki ilişkisinin ≈ %30'unu bu çevre yükleri açıklıyor.
- **Bulgu 3 değişti.** Yükseklik–ölümlülük ilişkisi PM2.5, sıcaklık ve ağaç kontrol edilince kat başına %0,85'e iniyor ve anlamsızlaşıyor (p = 0,15). Dikeyleşmenin sağlık maliyeti büyük ölçüde onunla birlikte gelen kirli hava ve ağaçsızlıktan geçiyor.

**Tez için anlamı:** Sağlık gerekçesi artık "az kat" değil, **temiz hava, ağaç ve az sert yüzey**. Kat sınırı bu üçünü kolaylaştırdığı ölçüde savunulmalı; tek başına bir hedef değil.

