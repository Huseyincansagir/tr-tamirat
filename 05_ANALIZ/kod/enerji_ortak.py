"""
Enerji modeli — ortak sabitler, varsayımlar ve yardımcı işlevler (Faz 4 · Rapor 5)
=================================================================================
enerji_mahalle.py, enerji_senaryo.py ve enerji_grafikler.py bu modülü kullanır.

İşaretler: [D] doğrulandı · [İ] ikincil · [DY] doğrulanmadı · [V] varsayım · [H] hesaplandı.
Bütün varsayımlar VARSAYIM sözlüğünde tek yerde; enerji_varsayimlar.csv'ye aynen yazılır.
"""
from __future__ import annotations

import gzip
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "enerji"
PVG = HAM / "pvgis"
SON = KOK / "05_ANALIZ" / "sonuclar"
GRAF = KOK / "05_ANALIZ" / "grafikler"
MM_KOD = KOK / "07_TASARIM_CIZIM" / "model_mahalle_v2" / "kod"

YILLAR = (2019, 2020, 2021, 2022, 2023)          # PVGIS SARAH3 saatlik seri yılları
PILOT_ANAHTAR = {"Antakya": "Antakya", "Başakşehir": "Basaksehir", "Beypazarı": "Beypazari", "Fatih": "Fatih",
                 "Kocasinan": "Kocasinan", "Meram": "Meram", "Nilüfer": "Nilufer", "Onikişubat": "Onikisubat",
                 "Safranbolu": "Safranbolu", "Silivri": "Silivri"}

# --------------------------------------------------------------------------------------
# Varsayımlar: (değer, birim, işaret, kaynak / gerekçe)
# --------------------------------------------------------------------------------------
VARSAYIM = {
    # --- talep: konut ---
    "hane_elektrik": (2500, "kWh/hane·yıl", "V", "Ev aletleri, aydınlatma ve indüksiyon pişirme; ısıtma, soğutma ve sıcak su hariç. "
                      "Karşılaştırma: Türkiye 2025 mesken tüketimi 78.197 GWh / 26,98 milyon hane ≈ 2.899 kWh/hane (EPDK 2025, TÜİK) [D-h]"),
    "net_brut_oran": (0.85, "—", "V", "Isıtılan net alan / brüt kat alanı"),
    "H_yeni": (1.0, "W/m²K", "V", "Yeni yapı (TS 825 + BEP 2022 NSEB, EKB en az B) için ısı kaybı katsayısı (havalandırma dahil, net alan başına)"),
    "H_iyi": (0.6, "W/m²K", "V", "Yüksek yalıtım ve ısı geri kazanımlı havalandırma (pasif eve yakın)"),
    "H_stok": (2.0, "W/m²K", "V", "Mevcut yalıtımsız stok (karşılaştırma)"),
    "H_ts825": (1.5, "W/m²K", "V", "TS 825'in asgarisiyle yapılmış yeni bina; uygulamadaki tipik durum (duyarlılık)"),
    "T_denge": (15.0, "°C", "V", "Isıtma denge sıcaklığı (iç kazanç ve güneş kazancı sonrası)"),
    "sicak_su": (40, "L/kişi·gün", "V", "45 °C kullanım; dağıtım ve depo kaybı %15"),
    "sogutma_pay": (0.5, "—", "V", "Soğutulan net alan payı"),
    "H_sogutma": (2.5, "W/m²K", "V", "Soğutma yükü katsayısı (güneş kazancı dahil), 24 °C üstü saatlik derece-saat"),
    "EER": (3.5, "—", "V", "Split klima mevsimlik verim"),
    # --- talep: konut dışı ve ulaşım ---
    "konut_disi_elektrik": (70, "kWh/m²·yıl", "V", "Dükkân, okul, konak, sağlık, cami karışımı (ısıtma hariç)"),
    "otopark_elektrik": (8, "kWh/m²·yıl", "V", "Kapalı otopark aydınlatma ve havalandırma"),
    "kamusal": (40, "kWh/kişi·yıl", "V", "Sokak aydınlatması, su ve atık su pompası payı"),
    "arac_km": (12000, "km/araç·yıl", "V", "Otomobil yıllık yol"),
    "ev_tuketim": (0.18, "kWh/km", "V", "Elektrikli otomobil, prizden"),
    "icten_yanmali": (0.065, "L/km", "V", "Benzinli/dizel otomobil, ortalama"),
    # --- ısı pompası ---
    "isi_pompasi_eta": (0.45, "—", "V", "Carnot verimine oran (hava kaynaklı)"),
    "T_gidis_isitma": (40, "°C", "V", "Düşük sıcaklıklı ısıtma (yerden ya da büyük radyatör)"),
    "T_gidis_sicaksu": (55, "°C", "V", "Sıcak su"),
    "T_kaynak_toprak": (8, "°C", "V", "Toprak kaynaklı / 5. nesil şebekede ısı pompası kaynak sıcaklığı"),
    "toprak_eta": (0.42, "—", "V", "Carnot verimine oran (toprak kaynaklı)"),
    "sebeke_kaybi_5g": (0.08, "—", "V", "5. nesil şebekede pompa ve ısı kaybı payı"),
    "sondaj_ozgul": (40, "W/m", "V", "Sondaj başına ısı çekme gücü (VDI 4640 orta değer aralığı 30–55 W/m) [İ]"),
    "sondaj_derinlik": (150, "m", "V", "Sondaj derinliği"),
    "sondaj_aralik": (7, "m", "V", "Sondajlar arası mesafe (kare ızgara)"),
    "kombi_verim": (0.92, "—", "V", "Yoğuşmalı kombi mevsimlik verimi"),
    # --- çatı GES ---
    "kwp_m2": (0.20, "kWp/m²", "V", "Kullanılabilir çatı alanı başına güç (2026 modülleri ≈ 0,21–0,23 kWp/m² modül alanı)"),
    "egimli_guney_pay": (0.40, "—", "V", "Mahyası D–B uzanan eğimli çatıda yalnız güney yüzü; yüzün %80'i kullanılır"),
    "egimli_dogu_bati_pay": (0.80, "—", "V", "Mahyası K–G uzanan çatıda doğu ve batı yüzlerinin %80'i"),
    "duz_pay": (0.65, "—", "V", "Düz çatıda doğu–batı 10° dizi; servis yolu, kule ve gölge payı düşülür"),
    "cati_egim": (20, "°", "V", "Türkiye'de kiremit çatı eğimi ≈ %30–35 (17–19°)"),
    "pv_kayip": (14, "%", "D", "PVGIS varsayılan sistem kaybı"),
    # --- batarya ---
    "batarya_saat": (2.0, "h", "V", "Güç/kapasite oranı (2 saatlik)"),
    "batarya_verim": (0.90, "—", "V", "Gidiş-dönüş verimi (her yönde 0,949)"),
    # --- emisyon ---
    "ef_sebeke_2023": (0.430, "tCO2/MWh", "D", "ETKB-EVÇED Türkiye ulusal elektrik şebekesi emisyon faktörü 2023 (yayım 26.12.2025)"),
    "ef_gaz": (0.202, "tCO2/MWh yakıt", "D", "IPCC 2006: doğal gaz 56,1 tCO2/TJ"),
    "ef_benzin": (2.31, "kgCO2/L", "D", "IPCC 2006 (benzin 69,3 tCO2/TJ, 33,4 MJ/L)"),
    "gaz_kwh_sm3": (10.64, "kWh/Sm³", "V", "Üst ısıl değer 9.155 kcal/Sm³ (BOTAŞ faturalama esası)"),
    # --- fiyatlar (2025–2026) ---
    "tarife_dusuk": (3.68, "TL/kWh", "DY", "EPDK mesken AG tek zamanlı düşük kademe 291,90 kr/kWh (4.4.2026) [D]; %5 ETV + %20 KDV ile [DY: vergi oranı belgeden doğrulanmadı]"),
    "tarife_yuksek": (5.44, "TL/kWh", "DY", "EPDK mesken yüksek kademe 432,07 kr/kWh (günlük ort. > 8 kWh) [D]; vergiler aynı varsayımla"),
    "gaz_konut": (13.19, "TL/Sm³", "D", "EPDK 2025 Doğal Gaz Piyasası Gelişim Raporu Tablo 9.1, konut 2025 II. yarıyıl ortalaması (vergiler dahil); sanayi 19,29"),
    "jeotermal_tarife": (1.3335, "TL/kWh", "D", "İzmir Jeotermal (Balçova) 2025–26 sezonu kalorimetreli tarife, KDV dahil"),
    "usd_try": (39.48, "TL/$", "D", "TCMB 2025 yıllık ortalama döviz alış kuru (2026 için güncellenmedi)"),
    # --- kademeler (07_TASARIM_CIZIM/olceklenebilir_sehir/kademe_semasi.py) ---
    "semt_mahalle": (5, "mahalle", "D", "Kademe şeması: semt = 5 mahalle + semt merkezi (≈35 bin kişi)"),
    "sehir_semt": (6, "semt", "D", "Kademe şeması: şehir = 6 semt (≈210 bin kişi)"),
    "bolge_sehir": (6, "şehir eşdeğeri", "V", "Kademe şeması: bölge = 5 şehir + bölge merkezi (≈1,3 milyon); merkez bir şehir eşdeğeri sayıldı"),
    "semt_merkezi_el": (150, "kWh/kişi·yıl", "V", "Lise, cuma camii, semt sağlık merkezi, kütüphane, spor, pazar (ısıtma-soğutma dahil, ısı pompalı)"),
    "semt_merkezi_isi": (60, "kWh/kişi·yıl", "V", "Semt merkezi binalarının ısıtma ve sıcak su ısısı"),
    "semt_merkezi_cati": (15000, "m²", "V", "Semt merkezindeki düz çatı tabanı (≈1,5 ha)"),
    "sehir_hizmet_el": (1050, "kWh/kişi·yıl", "V", "Hastane, üniversite, büro, AVM, su ve atık su arıtma, raylı sistem, OSB'de hafif ve orta sanayi; "
                        "semt merkezi ile toplam 1.200. Karşılaştırma 2024: ulusal ticaret-hizmet 977, sanayi 1.528 kWh/kişi [H: ETKB denge]"),
    "sehir_hizmet_isi": (300, "kWh/kişi·yıl", "V", "Şehir ölçeğindeki hizmet binalarının ısısı (proses ısısı hariç)"),
    "bolge_ek_el": (1000, "kWh/kişi·yıl", "V", "Ağır sanayi, liman, havalimanı, bölgesel tren; konut dışı toplamı ulusal 2024 düzeyine (≈2.680 kWh/kişi) yaklaştırır"),
}


def v(ad):
    return VARSAYIM[ad][0]


def varsayim_tablosu() -> pd.DataFrame:
    return pd.DataFrame([dict(ad=k, deger=d[0], birim=d[1], isaret=d[2], kaynak=d[3]) for k, d in VARSAYIM.items()])


# --------------------------------------------------------------------------------------
# PVGIS serileri (UTC → yerel saat UTC+3)
# --------------------------------------------------------------------------------------
def seri(ad: str) -> pd.DataFrame:
    with gzip.open(PVG / f"{ad}.json.gz", "rt", encoding="utf-8") as f:
        js = json.load(f)
    d = pd.DataFrame(js["outputs"]["hourly"])
    t = pd.to_datetime(d["time"], format="%Y%m%d:%H%M").dt.floor("h") + pd.Timedelta(hours=3)
    d.index = t
    d = d[~d.index.duplicated()]
    return d


def saat_ekseni() -> pd.DatetimeIndex:
    """2019-01-01 00:00 – 2023-12-31 23:00 yerel saat (UTC+3, Türkiye 2016'dan beri yaz saati yok)."""
    return pd.date_range("2019-01-01 00:00", "2023-12-31 23:00", freq="h")


def hizala(s: pd.Series) -> np.ndarray:
    """UTC+3 kaydırmasıyla baştaki 3 saat boşalır; ilk değerle doldurulur."""
    ek = saat_ekseni()
    return s.reindex(ek).ffill().bfill().to_numpy()


def pilot_pv(ilce: str) -> dict[str, np.ndarray]:
    """kWh/kWp (saatlik) — 5 yönelim + sıcaklık."""
    a = PILOT_ANAHTAR[ilce]
    cikti = {}
    for y in ("G20", "D20", "B20", "D10", "B10"):
        d = seri(f"seri_{a}_{y}")
        cikti[y] = hizala(d["P"] / 1000.0)
        if y == "G20":
            cikti["T"] = hizala(d["T2m"])
    return cikti


# --------------------------------------------------------------------------------------
# Profiller [V]
# --------------------------------------------------------------------------------------
KONUT_GUN = np.array([3.0, 2.5, 2.2, 2.1, 2.1, 2.4, 3.3, 4.3, 4.5, 4.2, 4.0, 4.1, 4.4, 4.3, 4.0, 3.9, 4.2, 5.0, 6.0, 6.8,
                      7.0, 6.5, 5.4, 4.0])                      # ev aletleri + aydınlatma, iş günü
KONUT_TATIL = np.array([3.2, 2.7, 2.3, 2.1, 2.0, 2.1, 2.4, 3.0, 3.9, 4.6, 4.9, 5.0, 5.1, 4.8, 4.5, 4.3, 4.4, 5.0, 5.9, 6.6,
                        6.9, 6.5, 5.6, 4.3])
SICAKSU_GUN = np.array([1.0, 0.6, 0.5, 0.5, 0.6, 1.5, 4.5, 7.0, 6.5, 4.5, 3.5, 3.5, 4.0, 3.5, 3.0, 3.0, 3.5, 4.5, 6.0, 7.5,
                        8.0, 7.5, 5.5, 3.0])
KONUT_DISI = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.5, 3.0, 6.0, 7.5, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 7.5, 7.0, 6.0, 5.0,
                       4.0, 2.5, 1.5, 1.0])
SOKAK = np.array([1, 1, 1, 1, 1, 1, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 1, 1, 1, 1, 1], dtype=float)
EV_DENETIMSIZ = np.array([4, 2, 1, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 3, 6, 8, 8, 7, 6, 5],
                         dtype=float)
EV_AKILLI = np.array([2, 1.5, 1, 0.5, 0.5, 0.5, 0.5, 1, 2, 4, 6, 7, 7.5, 7.5, 7, 5.5, 3.5, 2, 2, 2.5, 3, 3, 3, 2.5],
                     dtype=float)  # gün ortası güneşe kaydırılmış (işyeri/merkez otoparkında şarj ve uzaktan yönetim)


def gunluk_profil(ek: pd.DatetimeIndex, is_gunu: np.ndarray, tatil: np.ndarray | None = None) -> np.ndarray:
    """Saatlik profil, yıllık toplamı 1 olacak şekilde (5 yıl için 5)."""
    tatil = is_gunu if tatil is None else tatil
    sa = ek.hour.to_numpy()
    hs = ek.dayofweek.to_numpy() >= 5
    p = np.where(hs, tatil[sa] / tatil.sum(), is_gunu[sa] / is_gunu.sum())
    return p / p.sum() * len(YILLAR)


def mevsim_aydinlatma(ek: pd.DatetimeIndex, genlik=0.12) -> np.ndarray:
    gun = ek.dayofyear.to_numpy()
    return 1 + genlik * np.cos(2 * np.pi * (gun - 355) / 365.25)


def okul_tatil_carpani(ek: pd.DatetimeIndex) -> np.ndarray:
    """Konut dışı yükte Pazar ve Temmuz–Ağustos azalması (okul tatili)."""
    c = np.ones(len(ek))
    c[ek.dayofweek.to_numpy() == 6] = 0.45
    c[np.isin(ek.month.to_numpy(), (7, 8))] *= 0.8
    return c


def cop_hava(T, T_gidis, eta=None):
    eta = v("isi_pompasi_eta") if eta is None else eta
    T = np.asarray(T, dtype=float)
    dT = np.maximum(T_gidis - T, 10.0)
    c = eta * (T_gidis + 273.15) / dT
    c = np.where(T < 5, c * 0.92, c)            # buzlanma çözme payı [V]
    return np.clip(c, 1.5, 5.5)


def cop_toprak(T_gidis):
    dT = max(T_gidis - v("T_kaynak_toprak"), 10.0)
    return min(v("toprak_eta") * (T_gidis + 273.15) / dT, 5.5)


# --------------------------------------------------------------------------------------
# Batarya benzetimi (saatlik, açgözlü)
# --------------------------------------------------------------------------------------
def batarya(net: np.ndarray, kap: float, guc: float | None = None, verim: float | None = None):
    """net = talep − üretim (kWh/saat; + açık, − fazla). Döner: şebekeden alım, şebekeye veriş, deşarj toplamı."""
    if kap <= 0:
        return np.maximum(net, 0), np.maximum(-net, 0), 0.0
    guc = kap / v("batarya_saat") if guc is None else guc
    ek = math.sqrt(v("batarya_verim") if verim is None else verim)
    soc = 0.5 * kap
    al = np.empty_like(net)
    ver = np.empty_like(net)
    desarj = 0.0
    for i, x in enumerate(net):
        if x < 0:                                   # fazla: şarj et
            s = min(-x, guc, (kap - soc) / ek)
            soc += s * ek
            al[i] = 0.0
            ver[i] = -x - s
        else:                                       # açık: deşarj et
            d = min(x, guc, soc * ek)
            soc -= d / ek
            desarj += d
            al[i] = x - d
            ver[i] = 0.0
    return al, ver, desarj


# --------------------------------------------------------------------------------------
# Biçim ve grafik yardımcıları
# --------------------------------------------------------------------------------------
MAVI, TURUNCU, AQUA, SARI = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
YAZI, YAZI_2, YAZI_3, ZEMIN, IZGARA = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e8e7e3"
GRI = "#c9c8c3"
GRI_KOYU = "#8a8984"


def tr(x, nd=1):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def crf(oran, yil):
    return oran * (1 + oran) ** yil / ((1 + oran) ** yil - 1)
