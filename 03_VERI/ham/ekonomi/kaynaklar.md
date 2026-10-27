# Gelir, vergi ve ticaret analizi: ham veri ve kaynaklar

*27 Ekim 2026 · Faz 4 · Rapor 7 ([09_RAPORLAR/20_ekonomi_gelir_vergi_ticaret.md](../../../09_RAPORLAR/20_ekonomi_gelir_vergi_ticaret.md))*

Bu klasördeki her dosya ya bir betikle yeniden indirilir ya da resmî bir belgenin kendisidir. Makine tarafından okunabilen kaynaklar betiklerde dosyadan hesaplanır. PDF'ten elle aktarılan sayıların sayfa ya da tablo numarası betikteki satırın yanında yazılı.

**İşaretler:** [D] birincil kaynakta okundu · [İ] ikincil aktarım (haber, kurum bülteni) · [DY] doğrulanamadı · [V] varsayım · [H] hesaplandı.

**Betik zinciri:** `05_ANALIZ/kod/ekonomi_veri.py` → `ekonomi_dagilim.py` → `ekonomi_ticaret_yeterlilik.py` → `ekonomi_kademe.py` → `ekonomi_grafikler.py`. İlk betik eksik dosyaları anahtarsız uç noktalardan indirir; dosya varsa yeniden indirmez.

## 1. Makine tarafından okunan kaynaklar

| Dosya | İçerik | Uç nokta | İşaret |
|---|---|---|---|
| `sdmx/DF_ISGUCU_CEYREK_TEMEL_ISGUCU_C.json` | Çeyreklik işgücü: nüfus, işgücü, istihdam, işsiz (bin kişi), oranlar; mevsim etkisinden arındırılmış ve ham | TÜİK SDMX `POST https://databrowser2.tuik.gov.tr/api/core/nodes/1/datasets/TR,<AKIŞ>,1.0/data`, gövde `[]` | [D] |
| `sdmx/DF_ISGUCU_CEYREK_TAMAMLAYICI_GOSTERGE_C.json` | Atıl işgücü ve tamamlayıcı oranlar | aynı | [D] |
| `sdmx/DF_ISGUCU_CEYREK_SGK_KAYIT_C.json` (+ `_uzun.csv`) | SGK'ya kayıtlı olmadan çalışanların oranı (kayıt dışı istihdam), tarım / tarım dışı | aynı | [D] |
| `sdmx/DF_KURUMSAL_SEKTOR_HESAPLARI_CARI_FIYATLARLA_V2.json` | Hanehalkı sektörü (S1M): işgören ödemeleri, karma gelir, mülk geliri, sosyal yardımlar, vergiler, tüketim, 2009–2025 | aynı | [D] |
| `sdmx/DF_GENEL_DEVLET_VERGI_SOSYAL_KATKI_V2.json` | Genel devlet vergi ve sosyal katkı gelirleri (ESA kodları) | aynı | [D] |
| `sdmx/DF_TUFE_SDMX_TT10.json` | TÜFE (2025=100), aylık | aynı | [D] |
| `sdmx/catalog.json` | TÜİK SDMX akış kataloğu (keşif için) | `GET .../api/core/nodes/1/catalog` | — |
| `sdmx/test_*.json` | Önceki oturumun deneme indirmeleri; betiklerde kullanılmıyor | — | — |
| `eurostat/ilc_di12`, `ilc_di11`, `ilc_li02`, `ilc_di01` | Gini, S80/S20, yoksulluk riski (medyanın %60'ı), ondalık gelir payları; Türkiye ve AB-27 | `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<tablo>?...&format=JSON` | [D] |
| `eurostat/ilc_lvho07c`, `ilc_lvho02` | Konut maliyeti aşırı yükü ve mülkiyet durumu | aynı | [D] |
| `eurostat/hbs_str_t223_TR.json`, `hbs_exp_t133_TR.json` | Hanehalkı Bütçe Anketi 2020 (TÜİK HBA): gelir beşte birlik dilimine göre COICOP harcama yapısı ve harcama düzeyi | aynı | [D] |
| `eurostat/earn_ses_monthly_TR.json` | Kazanç Yapısı Araştırması: medyan ve ortalama aylık brüt kazanç (avro), 2006–2018 | aynı | [D] |
| `eurostat/ert_bil_eur_a_TRY.json` | Avro/TL yıllık ortalama kur | aynı | [D] |
| `oecd/oecd_idd_TUR.csv` | OECD Income Distribution Database: piyasa, brüt, kullanılabilir gelir Gini'si ve gelir bileşenleri | `https://sdmx.oecd.org/public/rest/data/OECD.WISE.INE,DSD_WISE_IDD@DF_IDD,/TUR.........` | [D] |
| `oecd/oecd_earnings_dec_i_TUR.csv` | Ücret ondalık oranları (D5/D1, D9/D5), Türkiye ve OECD | `OECD.ELS.SAE,DSD_EARNINGS@DEC_I` | [D] |
| `vergi/OECD_RevenueStatistics_DF_RSOECD_TUR_OECD_2000-2024.csv` | OECD Revenue Statistics: vergi bileşimi, Türkiye ve OECD ortalaması | OECD SDMX `DF_RSOECD` | [D] |
| `evds/TP_BK_TR_ceyrek.json` | TCMB konut birim kirası (TL/m², çeyreklik; değerleme raporlarına dayalı) | EVDS3 anahtarsız arka uç `https://evds3.tcmb.gov.tr/igmevdsms-dis/fe` (bkz. `05_ANALIZ/kod/konut_h2_veri.py`) | [D] |
| `worldbank/TUR_*.json`, `OED_*.json` | GSYH (cari TL), Gini, vergi bileşimi; Türkiye ve OECD üyeleri | `https://api.worldbank.org/v2/country/<ülke>/indicator/<kod>?format=json` | [D] |
| `ticaret_tarim/oecd_pmr_2018_2023.csv` | OECD Ürün Piyasası Düzenlemesi (PMR) göstergeleri, bütün üyeler | OECD SDMX `DSD_PMR@DF_PMR` | [D] |
| `ticaret_tarim/B-READY_ALL_DATA_2025.zip` | Dünya Bankası B-READY 2025 sütun ve konu puanları | Dünya Bankası B-READY veri sayfası | [D] |
| `ticaret_tarim/worldbank_informal_economy_database.xlsx` | Kayıt dışı ekonominin GSYH'ye oranı (MIMIC, DGE) | Dünya Bankası Informal Economy Database | [D] |
| `ticaret_tarim/comtrade_*.csv` | Tarım-gıda ve enerji ithalatı (HS fasıl), 2018–2025 | UN Comtrade public preview | [D] |
| `ticaret_tarim/tuik_sdmx_*.csv` | H-ÜFE gayrimenkul kiralama; kayıt dışı istihdam (uzun biçim) | TÜİK SDMX | [D] |

## 2. Resmî belgeler (PDF, XLS)

| Dosya | Ne için kullanıldı | Doğrulama |
|---|---|---|
| `turkis/turkis_aclik_yoksulluk_2026.0{1,7,8,9}.pdf` | TÜRK-İŞ açlık ve yoksulluk sınırı. Eylül 2026 bülteninin Çizelge 3'ündeki TASE endeksinden Ocak 2023–Eylül 2026 aylık seri | Betikte `assert`: Eylül 2025, Aralık 2025 ve Ağustos 2026 bülten değerleriyle ±%0,2 içinde. Yoksulluk sınırı = açlık sınırı / 0,307 (TÜRK-İŞ'in gıda payı yöntemi) |
| `vergi/Muhasebat_MYKB_2006-2025_Butce_Gelirleri_Tahsilatlari_Detay2.xls` | Merkezi yönetim bütçe vergi gelirleri, 2006–2025 | Satır etiketleri betikte denetleniyor |
| `vergi/Muhasebat_MYKB_202{5,6}_Ay_Ici_Butce_Gelirleri_Detay2.xls` | Ocak–Eylül 2025 ve 2026 karşılaştırması | Etiketle eşleştirme |
| `vergi/Muhasebat_MahalliIdareler_202{4,5}_Butce_Gelirleri_Ekod4.xls` | Belediye ve il özel idareleri bütçe gelirleri: bina, arsa, arazi vergisi; merkezi vergi payları; harcamalara katılma payları; otopark bedeli | Etiketle eşleştirme. Değer artış payı (3194 Ek md. 8) bu ekonomik kod düzeyinde ayrı görünmüyor [DY] |
| `vergi/GIB_Vergi_Harcamalari_Raporu_2025.pdf` | Vergi harcamaları 2025–2026; Tablo 4–5 (s. 294): harcama / tahsilat oranı; Ek I kalem tabloları | Toplam (3.170,3 / 3.597,1 mlr TL), asgari ücret istisnası (848,9) ve 10 kalem PDF'ten tek tek okundu. KDV 17/4-g kalemi önceki taslakta yanlışlıkla "arsa satışı" diye etiketlenmişti; düzeltildi (külçe altın-gümüş, sermaye piyasası aracı ve hurda teslimi) |
| `vergi/GIB_Gelir_Vergisi_Tarifesi_2026.pdf`, `GIB_Asgari_Ucretten_Kesintiler.pdf`, `GIB_Mesken_Kira_Istisna_Tutarlari.pdf`, `GIB_GVK94_Kesinti_Oranlari.pdf`, `GIB_GVK_Gecici67_Kesinti_Oranlari.pdf`, `GIB_KDV_Oranlari.pdf`, `GIB_Deger_Artisi_Kazanci_Istisna.pdf` | 2026 tarifesi, net asgari ücret, kira istisnası, stopaj oranları, KDV oranları (etkin oran ve dağılım hesabı) | [D] |
| `vergi/mevzuat_1319_emlak_vergisi_kanunu.pdf` | Emlak vergisi oranları: md. 8 (mesken binde 1, diğer bina binde 2), md. 18 (arazi binde 1, arsa binde 3), büyükşehirde %100 artırımlı; Cumhurbaşkanının yarıya indirme / üç katına çıkarma yetkisi | mevzuat.gov.tr, 27.10.2026 [D] |
| `vergi/HMB_2025_Aralik_Aylik_Butce_Gerceklesme_Raporu.pdf`, `SBB_*_MYB_Gerceklesmeleri.pdf`, `GIB_2025_Faaliyet_Raporu.pdf`, `OECD_Revenue_Statistics_Turkiye_country_note.pdf` | Bağlam ve çapraz kontrol | — |
| `ticaret_tarim/mevzuat_paiy_23722.pdf` | Planlı Alanlar İmar Yönetmeliği md. 19/1-f-1: konut alanında zemin kat dükkânı ancak meclisin "yol boyu ticaret" kararı ve otopark şartıyla | mevzuat.gov.tr, 27.10.2026 [D] |
| `ticaret_tarim/mevzuat_mpyy_19788.pdf` | Mekânsal Planlar Yapım Yönetmeliği md. 21/10: karma kullanımda oran belirtilmemişse en fazla %30 konut | mevzuat.gov.tr, 27.10.2026 [D] |
| `ticaret_tarim/mevzuat_isyeri_acma_calisma_ruhsati_yonetmelik_2005-9207.pdf` | Ruhsat süreleri: sıhhi işyeri aynı gün (md. 12), 2.–3. sınıf gayrisıhhi beş gün | [D] |
| `ticaret_tarim/mevzuat_5957_hal_kanunu.pdf`, `mevzuat_6585_perakende_kanunu.pdf` | Hal ve perakende mevzuatı | [D] |
| `ticaret_tarim/rekabet_htm_sektor_incelemesi_nihai_rapor_2023.pdf` | Hızlı tüketim perakendesi: organize kanal payı, CR3/CR4, mağaza sayıları (Tablo 1–2, 6–8, 19) | Sayılar PDF'te arandı ve bulundu |
| `ticaret_tarim/tesk_sicil_*.pdf` | TESK esnaf sicili: kayıtlı esnaf (30.09.2026: 2.282.188), 2024–2025 açılış ve kapanış | [D] |
| `ticaret_tarim/tobb_kurulan_kapanan_sirket_2025-12.xls` | 2025 kurulan ve kapanan şirket | [D] |
| `ticaret_tarim/doing_business_2020_turkiye_TUR.pdf` | İşletme kurma ve inşaat izni süreleri (2020; seri durduruldu) | [D] |
| `ticaret_tarim/tepge_*_durum_tahmin_2025.pdf` | Kırmızı et, tavuk eti, yumurta, süt, ayçiçeği: TÜİK kaynaklı üretim ve tüketim → yeterlilik derecesi [H] | — |
| `ticaret_tarim/etkb_ulusal_enerji_denge_tablosu_2024.xlsx` | Enerji dengesi (bağlam; Rapor 18 ile ortak) | — |
| `tuik_bulten/tuik_gelir_dagilimi_2025_bulten_kopya.pdf` | İbn Haldun Üniversitesi haftalık ekonomik bülteni (26.12.2025); TÜİK Gelir Dağılımı İstatistikleri 2025'in Gini (0,410), transfer hariç Gini (0,473 ve 0,420), brüt gelir Gini'si (0,422) ve %20'lik pay değerlerini aktarıyor | [İ]: TÜİK veri portalı komut satırına kapalı; değerler basın aktarımlarıyla tutarlı |

## 3. İkincil aktarımla alınan sayılar [İ]

| Sayı | Değer | Kaynak (Ekim 2026 web araması) |
|---|---|---|
| TÜİK Gelir Dağılımı 2025: Gini, ücret / müteşebbis / transfer payları, ortalama ve medyan eşdeğer gelir | `ekonomi_tuik_gelir_bulteni_2025.csv` | ekonomigazetesi.com, dha.com.tr, cnbce.com; medyan: Rapor 06 |
| En düşük emekli aylığı, Ocak 2023 – Temmuz 2026 | 5.500 → 23.552 TL | tr.wikipedia ve basın; Temmuz 2026: TBMM'de kabul edilen kanun (ekonomist.com.tr, haberturk.com) |
| En düşük memur maaşı (aile yardımı dahil) | Temmuz 2025: 50.503 · Ocak 2026: 61.890 · Temmuz 2026: 70.224 TL | kariyer.net, sanayigazetesi.com.tr, haberturk.com. Daha önceki dönemler için kaynaklar farklı tanım kullandığından seri kurulmadı [DY] |
| Kazanç Yapısı Araştırması 2022 ortalama aylık brüt ücret | 11.143 TL | sabah.com.tr, benguturk.com (TÜİK bülten aktarımı) |
| AVM sayısı ve kiralanabilir alan, 2025 sonu | 445 AVM (AYD); 13,9 milyon m² | bloomberght.com, ekonomist.com.tr |
| TZOB üretici–market fiyat farkı, Aralık 2025 | havuç 4,2 kat; mandalina 3,5; kabak ve yeşil soğan 3,4 | haberturk.com, ekonomim.com |
| Bitkisel ürün denge tabloları 2024/25 sütunu | `ekonomi_yeterlilik_bitkisel.csv` | iscihaber.net, alomaliye.com (27.03.2026) |

## 4. Bulunamayanlar [DY]

- TÜİK GYKA mikro verisi ve resmî bülten tabloları (veri portalı komut satırına kapalı; bu oturumda tarayıcı kullanılmadı).
- Güncel ortanca (medyan) ücret: TÜİK yayımlamıyor; 2018 Kazanç Yapısı Araştırması oranından ve 2022 ortalamasından tahmin edildi [H/V].
- TÜİK hayvansal ürün denge tabloları (TEPGE raporlarındaki TÜİK kaynaklı değerlerle yerine kondu).
- Değer artış payı (3194 Ek md. 8) tahsilatı; işyeri ruhsatında başvurudan açılışa gerçek süre; pazar yeri ile market fiyatlarının sistematik karşılaştırması; esnaf kooperatiflerinin performans verisi.
- KDV indiriminin fiyata yansıma oranı için Türkiye ölçümü.
- Pazar Yerleri Hakkında Yönetmelik künyesi.
