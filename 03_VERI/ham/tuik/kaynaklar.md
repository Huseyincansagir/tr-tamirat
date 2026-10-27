# il_paneli_ham_2025.csv — kaynaklar

Tüm tablolar TÜİK Veri Portalı'ndan (https://veriportali.tuik.gov.tr) **25 Ekim 2026** tarihinde alındı. Her bültenin adresi `https://veriportali.tuik.gov.tr/tr/press/<no>` biçiminde.

| Bülten (no) | Dönem | Tablo | Panel sütunları |
|---|---|---|---|
| Doğum İstatistikleri (58018) | 2025 | İllere göre toplam doğurganlık hızı | `tdh_2020` … `tdh_2025` |
| Doğum İstatistikleri (58018) | 2025 | İl ve kent-kır sınıflamasına göre toplam doğurganlık hızı | `tdh25_top`, `tdh25_kir`, `tdh25_orta`, `tdh25_yogun` |
| Doğum İstatistikleri (58018) | 2025 | İl ve annenin eğitim durumuna göre toplam doğurganlık hızı | `tdh25_e_*` |
| Doğum İstatistikleri (58018) | 2025 | İllere göre ilk doğumdaki ortalama anne yaşı | `ilk_dogum_yasi_2025` |
| Evlenme ve Boşanma İstatistikleri (58165) | 2025 | İllere göre kaba evlenme hızı / kaba boşanma hızı / ortalama ilk evlenme yaşı | `kaba_evlenme_2025`, `kaba_bosanma_2025`, `ilk_evlenme_yasi_*` |
| Bina ve Konut Nitelikleri Araştırması (45870) | 2021 | İl ve ikamet edilen binanın kat sayısına göre hanehalkı sayısı ve oranı | `ort_kat_2021`, `kat*_pct` |
| Bina ve Konut Nitelikleri Araştırması (45870) | 2021 | Oda sayısı; kişi başı oda; mülkiyet; inşa yılı (il tabloları) | `ort_oda_2021`, `oda*_pct`, `kisi_basi_oda_2021`, `ev_sahibi_pct_2021`, `kiraci_pct_2021`, `insa_*` |
| İstatistiklerle Aile (58137) | 2025 | Ortalama hanehalkı büyüklüğü; hanehalkı tipleri; yaşlıların çocuklarına yakınlığı; akraba evliliği | `hane_*`, `yasli_*`, `akraba_evliligi_pct` |
| Adrese Dayalı Nüfus Kayıt Sistemi (53899) | 2025 | İl/ilçe merkezi, belde/köy nüfusu ve nüfus yoğunluğu; kent-kır sınıflamasına göre il nüfusları | `nufus_2025`, `nufus_yogunlugu_2025`, `kk_*` |
| İl Bazında Gayrisafi Yurt İçi Hasıla (53930) | 2024 | İl bazında kişi başına GSYH 2020–2024 | `ibbs3_kod`, `gsyh_kb_tl_2024`, `gsyh_kb_usd_2024` |
| Ulusal Eğitim İstatistikleri (58002) | 2025 | İllere göre bitirilen eğitim durumu (6+ yaş); illere göre ortalama eğitim süresi | `kadin_*`, `erkek_yuksekogretim_pct`, `*_egitim_suresi_2025` |

## Notlar

- **İkamet / olay yeri:** Doğum göstergeleri ikamet yerine, evlenme ve boşanma göstergeleri **olay yerine** göre derleniyor.
- **Boş kalan kent-kır değerleri:** `kk_yogun_kent_2025` ve `tdh25_yogun`, yoğun kent sınıfı bulunmayan 6 ilde (Artvin, Gümüşhane, Sinop, Tunceli, Bayburt, Ardahan) boş. Analizde yoğun kent payı bu iller için 0 kabul edildi.
- **`belde_koy_nufus`:** Büyükşehir illerinde boş, çünkü bu illerde belde ve köy yok (6360 sayılı Kanun).
- **Eğitim payları:** Eğitim durumu payları (`kadin_yuksekogretim_pct` vb.) 6 yaş ve üzeri, eğitim durumu bilinen kadın nüfusuna oranlandı. Yükseköğretim; yüksekokul veya fakülte, yüksek lisans ve doktora mezunlarını kapsıyor.
- **Doğrulama:** Aktarım, tarayıcıdaki tabloların sütun toplamlarıyla karşılaştırılarak doğrulandı (75 sütunun tamamı birebir). Nüfus ve hane toplamları Türkiye toplamına eşit: 86.092.168 kişi ve 26.977.795 hane.
- **Erişim:** Portal, komut satırından doğrudan istekleri engelliyor. Tablolar tarayıcı üzerinden portalın kendi arka ucuyla (`/api/tr/press/<no>`, `X-Requested-With: XMLHttpRequest` başlığı) alındı.
