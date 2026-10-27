# Mahalle nüfusu (Faz 3) — kaynak ve doğrulama

| Ne | Ayrıntı |
|---|---|
| Kaynak | TÜİK MEDAS (biruni.tuik.gov.tr/medas) → Adrese Dayalı Nüfus Kayıt Sistemi Sonuçları → **Belediye, köy ve mahalle nüfusları** |
| Kırılım | 18 yaş ve üzeri: Evet / Hayır |
| Yıl | 2025 (31 Aralık) |
| Düzey | Mahalle (yalnızca belediye mahalleleri; büyükşehir dışı ilçelerde köyler bu düzeyde yok) |
| Kapsam | 10 pilot ilçe, 658 mahalle |
| Erişim tarihi | 26.10.2026 |
| Dosya | `03_VERI/islenmis/pilot_mahalle_nufus_2025.csv` |

**Sütunlar:** `il, ilce, belediye, mahalle_tuik, mahalle_kod` (TÜİK mahalle kodu), `nufus_18p`, `nufus_0_17`, `nufus` (= ikisinin toplamı).

**Gizleme:** TÜİK küçük sayıları göstermiyor. 64 mahallede 0–17 yaş hücresi boş (değer yaklaşık 10'un altında); bu mahallelerin çocuk payı hesaplanmadı. 18+ hücrelerinin hepsi dolu.

**Doğrulama (ilçe toplamı, 2025):**

| İlçe | Mahalle | Mahalle toplamı | ADNKS ilçe (merkez) nüfusu | Fark |
|---|---|---|---|---|
| Fatih | 57 | 351.748 | 351.786 | −38 (gizlenen çocuk hücreleri) |
| Silivri | 35 | 240.029 | 240.029 | 0 |
| Başakşehir | 10 | 536.669 | 536.797 | −128 |
| Nilüfer | 64 | 577.940 | 578.059 | −119 |
| Beypazarı | 78 | 48.199 | 48.359 | −160 |
| Meram | 69 | 349.675 | 349.685 | −10 |
| Kocasinan | 88 | 421.440 | 421.472 | −32 |
| Antakya | 95 | 301.839 | 301.855 | −16 |
| Onikişubat | 141 | 447.538 | 447.591 | −53 |
| Safranbolu | 21 | 52.318 | 52.343 (merkez; ilçe 69.592) | −25 |

Tarayıcı içinde hesaplanan sütun toplamları (18+: 2.465.623; 0–17: 861.772) diske yazılan dosyayla aynı.
