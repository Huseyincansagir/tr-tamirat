# Konut paneli (H2) — kaynaklar

Bütün tablolar **26 Ekim 2026** tarihinde, giriş, hesap ya da API anahtarı gerektirmeyen herkese açık uç noktalardan alındı. İndirme ve panel kurma kodu: [`05_ANALIZ/kod/konut_h2_veri.py`](../../../05_ANALIZ/kod/konut_h2_veri.py). Ham yanıtlar bu klasörde JSON olarak duruyor; betik bunları önbellek olarak kullanır (`--yenile` ile yeniden indirir).

## 1. TCMB — Elektronik Veri Dağıtım Sistemi (EVDS3)

**Erişim yolu.** EVDS'in belgelenmiş API'si (`evds2.tcmb.gov.tr/service/evds/...`) kullanıcı anahtarı istiyor; hesap açılmadı, anahtar alınmadı. Bunun yerine TCMB'nin herkese açık Konut Fiyat Endeksi sayfasındaki (https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB+TR/Main+Menu/Istatistikler/Reel+Sektor+Istatistikleri/Konut+Fiyat+Endeksi/) tablo bağlantıları izlendi. Bunlar EVDS3'ün herkese açık "portlet" sayfalarına gidiyor. Portletlerin veriyi çektiği arka uç, oturum ve anahtar olmadan komut satırından çalışıyor:

- Seri listesi: `GET https://evds3.tcmb.gov.tr/igmevdsms-dis/serieList/fe/type=json&code=<veri grubu>`
- Veri: `POST https://evds3.tcmb.gov.tr/igmevdsms-dis/fe`; gövde `{"type":"json","series":"TP.KFE.TR-TP.KFE.TR10-...","aggregationTypes":"avg-...","formulas":"0-...","startDate":"01-01-2009","endDate":"31-12-2026","frequency":"5|6",...}`. Seri kodlarında nokta kullanılıyor (`TP.KFE.TR`); yanıtta noktalar alt çizgiye dönüşüyor.
- Portlet tanımı (hangi serilerin tabloda olduğu): `GET https://evds3.tcmb.gov.tr/igmevdsms-dis/public/charts/portlet/<kod>`

| Dosya | Veri grubu | İçerik | Kapsam | Panel sütunları |
|---|---|---|---|---|
| `evds_bie_birimfiyat.json` (+ `_seri_listesi`) | `bie_birimfiyat` | **Değerlemesi yapılan konutların birim fiyatları (TL/m²)**, çeyreklik | Türkiye + 81 il; 2010-1Ç → 2026-3Ç. 60 ilde 2010'dan, 10 ilde 2014'ten, 7 ilde 2022–2023'ten başlıyor; Ardahan, Bayburt, Gümüşhane, Hakkari ve Tunceli'de hiç yok | `birim_fiyat` (yıllık ortalama), `birim_fiyat_ceyrek` |
| `evds_bie_bk.json` | `bie_bk` | **Değerlemesi yapılan konutların birim kiraları (TL/m²/ay)**, çeyreklik | Türkiye + 81 il; 2018-1Ç → 2026-3Ç; 7 ilde yok | `birim_kira`, `birim_kira_ceyrek` |
| `evds_bie_kfe.json` | `bie_kfe` | **Konut Fiyat Endeksi (2023=100)**, aylık, kalite etkisinden arındırılmış (hedonik) | Türkiye + 19 bölge; 2010-01 → 2026-09 | `konut_paneli_kfe_bolge.csv: kfe` |
| `evds_bie_ykke.json` | `bie_ykke` | **Yeni Kiracı Kira Endeksi (2023=100)**, aylık | Türkiye + 19 bölge; 2018-01 → 2026-09 | `konut_paneli_kfe_bolge.csv: ykke` |
| `evds_TP_FG_J0.json` | `bie_tukfiy4` | TÜFE genel endeksi (2003=100), arşiv seri | 2005-01 → 2026-01 | yalnızca doğrulama |

**KFE bölgeleri 26 değil 19.** TCMB KFE'yi 13 İBBS-2 bölgesi (TR10, TR21, TR22, TR31, TR32, TR33, TR41, TR42, TR51, TR52, TR61, TR62, TR63) ve 6 birleşik İBBS-1 bölgesi (TR7, TR8, TR9, TRA, TRB, TRC) için yayımlıyor. Panelde `kfe_bolge` sütunu bu eşleşmeyi taşıyor.

**Doğrulama.**
- KFE Türkiye Eylül 2026 = 239,38; İstanbul = 230,85. TCMB'nin Eylül 2026 bülteni (`KFE.pdf`, aynı sayfadan) Tablo 1: 239,4 ve 230,9. Bülten de yıllık artışı %22,3 (Türkiye) ve %26,8 (İstanbul) veriyor.
- TÜFE (2003=100) yıllık ortalamaları EVDS ile TÜİK SDMX'te 2005–2025 boyunca birebir aynı (en büyük fark 0,0000).
- Birim fiyat ve birim kira değerleri değerleme raporlarına dayanıyor (konut kredisi için yapılan ekspertizler). Endeks değil düzey verisi; kalite düzeltmesi yok. Bileşim etkisine açık; özellikle küçük illerde gürültülü.

## 2. TÜİK — Dağıtım Yönetim Sistemi (SDMX, databrowser2.tuik.gov.tr)

Veri akışları kataloğu `GET https://databrowser2.tuik.gov.tr/api/core/nodes/1/catalog` ile listelendi. Veri `POST https://databrowser2.tuik.gov.tr/api/core/nodes/1/datasets/TR,<akış>,<sürüm>/data` ile alındı; yanıt JSON-stat. Tarayıcı gerekmedi.

| Dosya | Akış | İçerik | Kapsam | Panel sütunları |
|---|---|---|---|---|
| `sdmx_DF_KABA_EVLENME_HIZI.json` | DF_KABA_EVLENME_HIZI 1.0 | Kaba evlenme hızı (‰), il | 2005–2025 | `kaba_evlenme` |
| `sdmx_DF_EVLENME_ORT_ILK_EVL_YAS.json` | DF_EVLENME_ORT_ILK_EVL_YAS 1.0 | Ortalama ilk evlenme yaşı, il × cinsiyet | 2005–2025 | `ilk_evlenme_yasi_k`, `ilk_evlenme_yasi_e` |
| `sdmx_DF_EVLENME_ILK_YASGR.json` | DF_EVLENME_ILK_YASGR 1.0 | İlk evlenme sayısı, il × cinsiyet × yaş grubu | 2005–2025 (kadın yaş dağılımı 2024–2025 kullanılamaz, aşağıya bakınız) | `ilk_evlenme_k_sayi`, `tieh_k`, `iehk_*` |
| `sdmx_DF_DOGUM_IL_TDH_C.json` | DF_DOGUM_IL_TDH_C 1.0 | Toplam doğurganlık hızı, il | 2009–2025 | `tdh` |
| `sdmx_DF_DOGUM_ORTYAS_ILKDOG_C.json` | DF_DOGUM_ORTYAS_ILKDOG_C 1.0 | İlk doğumda ortalama anne yaşı, il | 2014–2025 | `ilk_dogum_yasi` |
| `sdmx_DF_UH_BH_KISI_BASI.json` | DF_UH_BH_KISI_BASI 1.0 | Kişi başı GSYH (cari TL), İBBS-3 (il) | 2005–2024 | `gsyh_kb_tl` |
| `sdmx_DF_ADNKS_T16.json` | DF_ADNKS_T16 1.0 | Kadın nüfusu, il × 5'li yaş grubu | 2007–2025 | `kadin_20_34`, `kadin_15_49`, `kadin_top` |
| `sdmx_DF_ULUSAL_EGITIM_ISTATISTIK_BED_NUFUS.json` | DF_ULUSAL_EGITIM_ISTATISTIK_BED_NUFUS 1.0 | 15+ yaş kadınların bitirdiği eğitim düzeyi, il | 2008–2025 | `kadin_yuksek_pct` |
| `sdmx_DF_TUFE_SDMX_2003.json` | DF_TUFE_SDMX_2003 1.0 | TÜFE genel endeksi (2003=100), aylık | 2005–2025 | `tufe_2003`, `reel_birim_fiyat` |

**Doğrulama.** 2025 (ve TDH için 2020) il değerleri, Veri Portalı bültenlerinden alınmış `03_VERI/islenmis/il_paneli_2025.csv` ile karşılaştırıldı (81 il):

| Değişken | En büyük fark | Açıklama |
|---|---|---|
| Kaba evlenme hızı 2025 | 0,005 | Bülten 2 ondalık, SDMX tam değer: yuvarlama |
| Kadın / erkek ilk evlenme yaşı 2025 | 0,05 | Bülten 1 ondalık: yuvarlama |
| TDH 2025 ve 2020 | 0,005 | Yuvarlama |
| İlk doğum yaşı 2025 | 0,05 | Yuvarlama |
| Kişi başı GSYH 2024 | 0,5 TL | Yuvarlama |

**Bulunan veri hatası: kadın ilk evlenme yaş dağılımı 2024–2025.** `DF_EVLENME_ILK_YASGR` akışında kadın satırlarının yaş dağılımından türetilen ortalama ilk evlenme yaşı, TÜİK'in yayımladığı ortalamayla 2005–2023'te ±0,2 yıl içinde uyuşuyor. 2024 ve 2025'te ise bütün illerde **+2,1 ile +4,3 yıl** sapıyor. Örneğin Türkiye'de 16–19 yaş kadın ilk evliliği 2023'te 46.748, 2024'te 5.492 görünüyor; ancak yayımlanan ortalama yaş yalnızca 25,74'ten 25,84'e çıkıyor. 2024–2025 kadın dağılımı erkek dağılımına benziyor. Toplam ilk evlenme sayıları ve erkek satırları tutarlı. Bu yüzden kadın toplam ilk evlenme hızı (`tieh_k`) ve yaşa özel hızlar (`iehk_*`) 2024–2025 için boş bırakıldı. Durum TÜİK'e bildirilmeye değer; Veri Portalı'ndaki bülten tablosuyla karşılaştırılmadı.

## 3. Türetilen değişkenler (`03_VERI/islenmis/konut_paneli.csv`)

| Sütun | Tanım |
|---|---|
| `fiyat_gelir` | `birim_fiyat` × 100 / `gsyh_kb_tl`: 100 m² konutun, ilin kişi başı yıllık GSYH'sinin kaç katı olduğu |
| `kira_gelir_pct` | 100 × `birim_kira` × 12 × 100 / `gsyh_kb_tl`: 100 m² konutun yıllık kirası, kişi başı GSYH'nin yüzdesi |
| `reel_birim_fiyat` | `birim_fiyat` / TÜFE(2003=100) × 100 |
| `tieh_k` | Kadın toplam ilk evlenme hızı = 5 × Σ (yaş grubundaki kadın ilk evlenmeleri / o yaş grubundaki kadın nüfusu), 15–49 yaş. 16–19 yaş evlenmeleri 15–19 yaş nüfusuna bölündü. TDH'nin evlilik karşılığı, yaş yapısından bağımsız; ancak 1'i aşabilir, çünkü il dışından gelip evlenenler (olay yeri) ve dönem etkileri var |
| `iehk_15_19` … `iehk_30_34` | Yaşa özel kadın ilk evlenme hızı (‰) |
| `kadin_yuksek_pct` | 15+ yaş kadınlar içinde yüksekokul, fakülte, yüksek lisans veya doktora mezunu payı (eğitimi bilinmeyenler paydadan çıkarıldı) |
| `ibbs2`, `ibbs1`, `kfe_bolge` | İBBS-3 kodundan türetilen bölge kodları; `kfe_bolge` TCMB'nin 19 KFE bölgesi |

**Notlar**
- **Olay yeri.** Evlenme göstergeleri olay yerine, doğum ve nüfus göstergeleri ikamet yerine göre derleniyor (TÜİK).
- **Gelir ölçüsü.** Kişi başı GSYH hanehalkı harcanabilir geliri değildir. İl düzeyinde başka uzun gelir serisi yok. Sanayi ağırlıklı illerde (Kocaeli gibi) erişilebilirliği olduğundan iyi gösterir.
- **2025 geliri yok.** İl GSYH'si 2024'te bitiyor; bu yüzden fiyat/gelir 2010–2024 arasında hesaplanabiliyor (1.025 il-yıl).
- **Bölge paneli** (`konut_paneli_kfe_bolge.csv`): il göstergeleri bölgeye ağırlıklı ortalamayla toplandı. Ağırlıklar: kaba evlenme ve kişi başı GSYH için kadın nüfusu; TDH ve ilk doğum yaşı için 15–49 yaş kadın; ilk evlenme yaşı için kadın ilk evlenme sayısı; TİEH için 20–34 yaş kadın. Bölgedeki illerden biri bile eksikse o bölge-yıl boş.

## 4. Erişilemeyen ya da kullanılmayan kaynaklar

- **EVDS resmî API'si (anahtarlı):** kullanılmadı; hesap açılmadı.
- **TÜİK TÜFE "gerçek kira" alt endeksi, İBBS-2:** SDMX'teki TÜFE akışlarında (`DF_TUFE_SDMX_TT01`–`TT10`, `DF_TUFE_SDMX_2003`) yalnızca Türkiye düzeyi var. Bölgesel TÜFE tabloları yalnızca Veri Portalı bülten eklerinde duruyor. TCMB'nin il düzeyindeki birim kira serisi bundan daha ayrıntılı olduğu için bu yola gidilmedi.
- **Konut satış istatistikleri** (`DF_SATIS_SEKLI_DURUMU_ILILCE_V3`): mevcut, bu turda kullanılmadı (ipotekli satış payı ileride kredi erişimi değişkeni olabilir).
