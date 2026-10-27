# Faz 4 · Rapor 8 — Ölçeklenebilir Şehir: Kademeler, Altyapı ve Ekonomik Düzen

*27 Ekim 2026 · Sürüm 0.1*

| Ne | Nerede |
|---|---|
| Kademe şeması | [07_TASARIM_CIZIM/olceklenebilir_sehir/kademe_semasi.png](../07_TASARIM_CIZIM/olceklenebilir_sehir/kademe_semasi.png) |
| Kademe tablosu (tek sayfa) | [kademe_tablosu.png](../07_TASARIM_CIZIM/olceklenebilir_sehir/kademe_tablosu.png) · `kademe_tablosu.csv` · `kademe_donatilar.csv` |
| Kurallar ve parametreler | `07_TASARIM_CIZIM/olceklenebilir_sehir/donatilar.csv` · `parametreler.csv` |
| Kod | `07_TASARIM_CIZIM/olceklenebilir_sehir/kod/kademe_modeli.py` · `kademe_semasi.py` |
| Bağlı raporlar | Enerji [18](18_enerji.md) · İsraf [19](19_israf_fire_kacak.md) · Ekonomi [20](20_ekonomi_gelir_vergi_ticaret.md) · Ulusal çerçeve [17](17_ulusal_mekansal_cerceve.md) · Model mahalle [v2.1](../07_TASARIM_CIZIM/model_mahalle_v2.md) |

---

## Özet

**Soru:** Fıtrata uygun mahalle büyüdüğünde, aynı ilke semt, şehir ve bölge ölçeğinde nasıl korunur? Her kademede hangi donatı, altyapı, yönetişim ve ekonomik araç gerekir?

**Kısa cevap:** Ölçeklenebilirlik "aynı birimi tekrarlamak ve her beş-altı birimde bir üst kademe eklemek" demek. Model mahalle v2.1 bu yapının temel birimidir.

| Kademe | Nüfus | Oluşum | Yürüme ölçeği |
|---|---|---|---|
| Komşuluk birimi | ≈ 870 | 1 ada grubu | kapı önü |
| **Mahalle** | ≈ 6.900 | 8 komşuluk birimi | 400 m |
| Semt | ≈ 35 bin | 5 mahalle + semt merkezi | 15 dk, 1,25 km |
| Şehir | ≈ 210 bin | 6 semt + şehir merkezi | raylı sistem |
| Bölge | ≈ 1,25 milyon | 6 şehir | bölgesel tren |

Bulgular:

1. **Donatı merdiveni kurallı.** 32 donatı türü ilk gerektiği kademeye bağlandı.
   - **Mahalle:** 2 ilkokul, ortaokul, aile sağlığı merkezi, semt camii, çarşı.
   - **Semt:** lise, cuma camii, poliklinik, kütüphane, haftalık pazar, itfaiye.
   - **Şehir:** devlet hastanesi, organize sanayi bölgesi, arıtma, kompost ve biyogaz tesisi.
   - **Bölge:** üniversite, eğitim-araştırma hastanesi, havalimanı.

   Bir şehirde örneğin 60 ilkokul, 12 lise, 30 aile sağlığı merkezi ve 1 hastane düşüyor.
2. **Enerjide hiçbir kademe kışın kendine yetmiyor.**
   - **Mahalle ve semt:** Çatı güneşi ve bataryayla yıllık talebin %55–78'i yerinde karşılanıyor; kışın bu pay %33–51'e iniyor.
   - **Şehir:** Çevresine güneş ve rüzgâr eklenince oran %78–81'e (kışın %67–71) çıkıyor. Elektrik 76–82 $/MWh'ye mal oluyor; bu, en ucuz nükleersiz karma.
   - **Çıkarım:** Şehir, enerji için doğal planlama birimi. Bölge ve ülke şebekesi kış açığını kapatmak için şart.
   - **SMR:** Bölge ölçeğinde bugün elektriği yaklaşık %45 pahalılaştırıyor. Öneri, seçeneği açık tutmak (Rapor 18).
3. **Su ve atıkta kazanç en hızlı şehir kademesinde.**
   - **Su:** Kayıp-kaçak %32,6'dan %15'e inerse 210 bin kişilik bir şehir günde yaklaşık 10 bin m³, yani talebin %21'i kadar daha az su çeker.
   - **Atık:** Mahalle başına günde 7,5 ton belediye atığı çıkıyor; malzeme geri dönüşümü %13'ten %55'e çıkarsa bunun 4,2 tonu geri kazanılır.
   - **Gıda:** Bir mahallede yılda 907 ton gıda israf ediliyor (kişi başı 131 kg).
4. **Ekonomik düzen de kademeli.** Rapor 20'nin 17 aracı kademelere dağıldı:
   - **Ülke:** Kuralı koyar: vergi oranları, arsa değer vergisinin çerçevesi, taban gelir kuralı.
   - **Şehir:** Tahsil eder: arsa değer vergisi, değer artış payı, ruhsat.
   - **Semt:** Hizmeti verir: pazar, esnaf ortak deposu, istihdam ofisi, kooperatif birliği.
   - **Mahalle:** Mekânı sağlar: zemin kat dükkânı ve atölye, üretici tezgâhı, kooperatif konut adası.
   - **Bölge:** Tarım kuşağını ve kısa tedarik zincirini taşır.
5. **Yönetişim kademeye denk düşmeli.** Komşuluk meclisi (avlu ve bahçe), muhtarlık ve mahalle bütçesi, semt meclisi, belediye, bölge planlama birliği. Bugün Türkiye'de semt ve komşuluk düzeyinde yönetişim organı yok.

---

## 1. Kademe kuralı

- **Temel birim:** Model mahalle v2.1. Kademe değerleri (60 ha, 2.163 konut, 6.925 kişi) model mahallenin metrikler dosyasından okunuyor. Komşuluk birimi model mahallenin 8 komşuluk biriminin ortalaması (≈ 270 konut, 866 kişi).
- **Yoğunluk:** Brüt 115 kişi/ha her kademede sabit tutuldu (konut ağırlıklı doku). Şehir ve bölgede yeşil kamalar, tarım kuşağı ve sanayi bu alana eklenir. Kademe şemasında bunlar ayrıca gösteriliyor.
- **Neden 5 ve 6?**
  - **Semt:** 5 mahalle, 15 dakikalık yürüme yarıçapına (1,25 km) sığan en büyük sayı. Bir lise ve bir haftalık pazar için yeterli nüfusu (≈ 35 bin) da veriyor.
  - **Şehir ve bölge:** 6 semt ve 6 şehir, iki raylı hattın kesiştiği merkezden 30–45 dakikada erişilebilir halkayı tanımlıyor (Rapor 17, uydu kent ilkesi: merkeze 20–70 km).

## 2. Donatı merdiveni

`kademe_donatilar.csv` her donatının her kademedeki sayısını veriyor. Kural şu: bir donatı bir hizmet nüfusuna bağlı. Kademe nüfusu bu sayıya bölünüyor; en az bir birim konuyor.

| Kademede ilk eklenen | Örnekler | Dayanak |
|---|---|---|
| Komşuluk birimi | ortak avlu ve kapı önü oyun alanı, komşuluk yeşili (≥ 0,5 ha), mescit | Model mahalle v2.1 [H] |
| Mahalle | kreş (5), küçük cami (4), anaokulu (2), ilkokul (2), ortaokul, aile sağlığı merkezi, semt camii, konak, çarşı, park | Model mahalle v2.1 [H]; MPYY md. 12 mesafeleri [D] |
| Semt | 3 durak, 2 lise, cuma camii, poliklinik ve acil, kütüphane, haftalık pazar, spor salonu, itfaiye | Kademe kuralı [V]; MPYY lise ≈ 2.500 m [D] |
| Şehir | devlet hastanesi (≈ 600 yatak), meslek yüksekokulu, kent parkı, OSB, arıtma, kompost ve biyogaz, toptancı hali | Türkiye ≈ 3 yatak/1.000 kişi [İ]; Rapor 17 ve 19 [V] |
| Bölge | eğitim-araştırma hastanesi, üniversite, lojistik merkezi ve liman bağlantısı, havalimanı (≤ 60 dk) | Rapor 17 [D/V] |

## 3. Altyapı kademeleri

| | Mahalle | Semt | Şehir | Bölge |
|---|---|---|---|---|
| Elektrik talebi (kWh/kişi·yıl) | 2.273–2.839 | 2.423–2.989 | 3.473–4.039 | 4.473–5.039 |
| Yerinde karşılama, yıllık | %56–78 | %55–77 | %78–81 | %77–80 |
| Yerinde karşılama, kış | %33–51 | %33–50 | %67–71 | %68–71 |
| Su, bugün → kayıp %15 (m³/gün) | 1.654 → 1.311 | 8.269 → 6.557 | 49.617 → 39.341 | 297.702 → 236.044 |
| Belediye atığı → geri kazanım hedefi (t/gün) | 7,5 → 4,2 | 37,7 → 20,8 | 226 → 125 | 1.359 → 747 |
| Gıda israfı bugün (t/yıl) | 907 | 4.536 | 27.214 | 163.287 |

Aralıklar üç iklimi kapsıyor: Antakya (sıcak), Fatih (ılıman kıyı), Kocasinan (soğuk iç bölge).

- **Elektrik talebinin kademeyle artması:** Kademe büyüdükçe kişi başı talep artıyor, çünkü donatı, ticaret ve sanayi ekleniyor (Rapor 18).
- **Su:** 2024'te belediyeler kişi başı günde 161 litre su dağıttı; dağıtılan su, çekilen suyun %67,4'ü [H, TÜİK aracılığıyla Rapor 19].
- **Ulaşım:**
  - Mahalle yürüme ve bisiklet kademesidir.
  - Semt tramvay ya da hızlı otobüs durağı alır.
  - Şehir iki raylı hat ve OSB'ye yük treni alır.
  - Bölge, bölgesel tren halkası ile 60 dakikada erişilen havalimanını alır (Rapor 17).

## 4. Ekonomik düzen kademeleri

Rol sözlüğü Rapor 20'den: **K** karar ve kural, **U** uygulama ve tahsil, **H** hizmet ve mekân, **V** veri ve izleme.

| Kademe | Başlıca araçlar |
|---|---|
| Ülke | K: arsa değer vergisi çerçevesi; dolaylı vergiden doğrudan vergiye kayış; istisnaların daraltılması; taban gelirlerin kurala bağlanması; karma kullanımlı imarın yönetmeliğe yazılması |
| Bölge | U: esnaf ortak alım birliği, kısa tedarik zinciri, tarım kuşağı ve havza planı; V: değerleme ofisi |
| Şehir | U: arsa değer vergisi tahsili, değer artış payı, tek pencere ruhsat, hal ve soğuk depo; K: plan notu ile karma kullanım |
| Semt | H: değer artış payından semt donatısı, haftalık pazar ve üretici tezgâhı, esnaf ortak deposu, istihdam ve mesleki eğitim ofisi, kooperatif birliği |
| Mahalle | H: zemin kat dükkânı ve atölyesi, mahalle meydanında üretici tezgâhı, ada ölçeğinde kooperatif konut, değer artış payından mahalle bütçesi |

**Hesap (Rapor 20):** Bir mahalle yılda emlak vergisinin yaklaşık 71 katı tüketim vergisi ödüyor. Vergi yükünü tüketimden arsaya kaydırmak, mahallenin ürettiği değeri mahalleye geri döndürmenin en doğrudan yolu. Tasarımı kritik: yalnız konut arsası vergilenirse yoksulun yükü artar.

## 5. Kendi kendine yeterlilik: hangi kademede kapanır?

| Akış | Kapandığı kademe | Not |
|---|---|---|
| Elektrik, yıllık | Şehir (%78–81) | Kış açığı ulusal şebekeyle; hiçbir kademe kışın kendine yetmiyor |
| Isınma | Mahalle ve semt (ısı pompası, bölgesel ısıtma) | Soğuk iklimde fatura, gaz sübvansiyonu sürdükçe ancak düşük kademede avantajlı (Rapor 18) |
| İçme suyu | Şehir ve havza | Kayıp-kaçak yönetimi şehir kademesinde |
| Organik atık | Mahalle (kompost) + şehir (biyogaz) | Bugün ülkede 9 kompost tesisi var (Rapor 19) |
| Gıda | Bölge (tarım kuşağı) | Soya yeterliliği %4, ayçiçeği %72; yağlı tohum ve yemde ülke ölçeğinde açık var (Rapor 20) |
| Gündelik ticaret | Mahalle ve semt | Engel imar ve ruhsat kuralları (Rapor 20; PAİY md. 19) |

## 6. Sınırlılıklar

- **Model, kural setidir; tahmin değildir.** Donatı hizmet nüfusları model mahalleden ya da proje varsayımlarından geliyor [V]. Gerçek yer seçiminde topoğrafya ve mevcut doku belirleyicidir.
- **Değişmeyen kabuller:**
  - Brüt yoğunluk her kademede sabit tutuldu; büyük kentlerde merkezler daha yoğun olur.
  - Kişi başı su ve atık bugünkü Türkiye ortalaması; iklime ve gelire göre değişir.
  - Enerji değerleri üç iklim örneğiyle sınırlı; Doğu Anadolu gibi çok soğuk bölgeler kapsanmadı.
- **Yönetişim önerileri yasal düzenleme gerektirir.** Semt meclisi ve komşuluk meclisi bugünkü mevzuatta yok; yasal çerçeveleri ayrıca hazırlanmalı.
