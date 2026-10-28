# İlçe paneli — kaynaklar ve erişim

Bütün veriler 25 Ekim 2026'da alındı.

## TÜİK Dağıtım Yönetim Sistemi (SDMX)

- **Adres:** `https://databrowser2.tuik.gov.tr`
- **Arka uç:** `https://databrowser2.tuik.gov.tr/api/core/nodes/1/datasets/<akış>/...`
- **Erişim:** Komut satırından erişilebiliyor. İstek gövdesi `[{"id": boyut, "filterValues": [...], "type": "CodeValues"}, {"id": "TIME_PERIOD", "type": "TimeRange", ...}]` biçiminde; yanıt JSON-stat 2.0.
- **Kod:** `03_VERI/kod/tuik_sdmx_ilce.py`. Ham yanıtlar `03_VERI/ham/tuik/sdmx/` klasöründe.

| Akış | İçerik | Panel sütunları |
|---|---|---|
| `TR,DF_DOGUM_IL_ILCE_C,1.0` | İl ve ilçeye göre doğumlar (bebeğin cinsiyetine göre), 2014–2025 | `dogum_2014` … `dogum_2025` |
| `TR,DF_ADNKS_T22,1.1` | İlçelere göre il/ilçe merkezi ve belde/köy nüfusu (2024–2025) | `nufus_2024`, `nufus_2025`, `merkez_nufus_*` |
| CL_IBBS 1.2 kod listesi | 973 ilçe kodu (4 haneli; üst kodu İBBS-3 il kodu) | `ilce_kod`, `ilce_ad_tuik`, `ibbs3_kod`, `il` |

## TÜİK MEDAS (biruni.tuik.gov.tr/medas)

MEDAS bir ZK arayüzü. Seçimler, tarayıcıda ZK istemci API'si (`zk.Widget.$(...)`, `fire('onSelect'|'onClick'|'onPaging')`) ile yapıldı. Pivot tablo DOM'dan okundu; 33 sayfalık rapor tek tek gezildi.

| Ölçüm | Seçim | Dosya |
|---|---|---|
| ADNKS → "İBBS-Düzey1, İBBS-Düzey2, İl ve İlçe Nüfusları" | Cinsiyet × Yaş Grubu (19 grup) · 2025 · İlçe düzeyi, 973 ilçe | `03_VERI/islenmis/ilce_yas_cinsiyet.csv` (15–49 yaş kadın, 0–4 yaş çocuk, 65+, beklenen doğum) |
| Ulusal Eğitim İstatistikleri → "Bitirilen Eğitim Düzeyi" | Kadın × 15+ Yaş × 9 eğitim düzeyi + bilinmeyen · 2025 · 973 ilçe | `03_VERI/islenmis/ilce_kadin_egitim.csv` |

**Doğrulama:** Aktarım sonrası sütun toplamları tarayıcıdaki toplamlarla birebir aynı.
- MEDAS ilçe nüfusu SDMX ilçe nüfusuyla 973 ilçenin tamamında aynı.
- Kadın toplamı il paneliyle aynı (43.032.734).
- Türkiye yaşa özel doğurganlık hızlarıyla hesaplanan beklenen doğum (895.438), gerçek doğuma (895.374) eşit.

**Beklenen doğum hesabı:** Türkiye yaşa özel doğurganlık hızları 2025 (binde; TÜİK Doğum İstatistikleri 2025, "Yaşa özel doğurganlık hızları" tablosu): 15–19: 9, 20–24: 53, 25–29: 96, 30–34: 80, 35–39: 37, 40–44: 8, 45–49: 1.

**Eğitim yılı varsayımı** (bitirilen okula göre): okuma yazma bilmeyen 0 · okuryazar ama okul bitirmemiş 2 · ilkokul 5 · ilköğretim 8 · ortaokul 8 · lise 11,5 · yüksekokul/fakülte 15,5 · yüksek lisans 17,5 · doktora 21,5.

## GHSL (JRC)

- **Ürünler:** GHS-BUILT-H ANBH E2018 (ortalama net bina yüksekliği) ve GHS-POP E2020, R2023A, 100 m, ESRI:54009.
- **Karolar:** R4_C21, R4_C22, R5_C21, R5_C22.
- **Kaynak:** `https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/`
- **İlçe toplama kodu:** `03_VERI/kod/ghsl_ilce.py`

## Sınırlar

geoBoundaries gbOpen TUR ADM2 (OSM, 2021; 973 birim), ADM1 (81 il).

## İlçe nüfusu 2014–2025 (MEDAS, 28 Ekim 2026)

- **Ölçüm:** ADNKS → "İBBS-Düzey1, İBBS-Düzey2, İl ve İlçe Nüfusları", ölçüm düzeyindeki toplam gösterge (kırılımsız). Zaman: yıllık 2014–2025. Düzey: İlçe Düzeyi, HEPSİ (976 öğe).
- **Okuma:** Yerleşik tarayıcıda; pivot raporun 389 sayfası (30 satır) ZK `onPaging` ile gezildi. Satır başlığındaki ilçe etiketi TÜİK ilçe kodunu taşıyor ("Adana(Aladağ)-1757").
- **Dosyalar:**
  - Ham uzun biçim: `03_VERI/ham/tuik/medas_ilce_nufus_2014_2025.csv` (11.666 satır).
  - Geniş biçim: `03_VERI/islenmis/ilce_nufus_2014_2025.csv`.
- **Doğrulama:**
  - Yıllık Türkiye toplamları ADNKS bültenleriyle aynı (2014: 77.695.904 … 2025: 86.092.168).
  - 2024 ve 2025 değerleri SDMX (DF_ADNKS_T22) ile 973 ilçenin tamamında birebir aynı.
  - 2105, 2106, 2107 kodlu üç ilçe 2017'de kuruldu; 2014–2016 değerleri yok.
- **Not:** SDMX'teki ilçe akışları (T22, T38) yalnız 2024–2025'i içeriyor.
