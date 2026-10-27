"""
Şehir (≈210 bin kişi) ve ülke (2050) enerji senaryoları (Faz 4 · Rapor 5)
=========================================================================
Saatlik (2019–2023, 5 hava yılı) basit sevk modeli: önce zorunlu üretim (nükleer, jeotermal, biyokütle,
akarsu HES, kömürün asgari yükü), sonra güneş ve rüzgâr, sonra aylık su bütçesiyle barajlı HES
(en yüksek artık yüke), sonra batarya ve pompaj (kronolojik), en son kömür ve doğal gaz. Fazla
üretim kısılır ya da dışarı verilir. Maliyet yıllıklandırılmış yatırım + sabit ve değişken giderle
hesaplanır (LCOE'yi kapasite faktörüyle birlikte modelin kendisi üretir).

Girdi : enerji_mahalle.py (model mahalle saatlik talebi ve çatı GES'i), PVGIS önbelleği, TEİAŞ aylık üretim
Çıktı : 05_ANALIZ/sonuclar/enerji_kent_senaryolar.csv, enerji_kent_tarama.csv,
        enerji_ulke_2050.csv, enerji_ulke_2050_duyarlilik.csv, enerji_maliyet_varsayim.csv,
        enerji_kalibrasyon.csv, enerji_smr_lcoe.csv, enerji_saglik_ucgenleme.csv
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/enerji_senaryo.py   (≈ 3–6 dk)
"""
from __future__ import annotations

import itertools
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enerji_ortak import (KOK, PILOT_ANAHTAR, SON, YILLAR, batarya, cop_hava, crf, hizala, pilot_pv,  # noqa: E402
                          saat_ekseni, seri, v)

NY = len(YILLAR)
EK = saat_ekseni()
NH = len(EK)

# --------------------------------------------------------------------------------------
# 1. Maliyet ve teknoloji varsayımları (2040'lar–2050; 2025 $) [V] — kaynak sütunu dayanağı verir
# --------------------------------------------------------------------------------------
WACC = 0.07
TEK = pd.DataFrame([
    # ad, yatırım $/kW (ya da $/kWh), sabit $/kW·yıl, değişken $/MWh, ömür, dayanak
    ("gunes", 550, 12, 0, 30, "IRENA 2025: küresel 667 $/kW, Türkiye 1.095 $/kW (2025); arazi %65 + çatı %35 karması, 2040'lara düşüş [V]"),
    ("ruzgar_kara", 1100, 35, 0, 25, "IRENA 2025: küresel 976, Türkiye 1.345 $/kW [D]; 2050 [V]"),
    ("ruzgar_deniz", 2500, 80, 0, 25, "IRENA 2025 küresel 2.931 $/kW [D]; 2050 [V]"),
    ("hidro", 0, 25, 0, 60, "Mevcut ve tamamlanan barajlar; yatırım batık [V]"),
    ("pompaj", 1200, 15, 0, 60, "IEA/NEA 2020 pompaj 897 $/kW (2018 $) [D]; 10 saatlik, 2025 $ [V]"),
    ("batarya_kwh", 110, 0, 0, 15, "IRENA 2025: anahtar teslim 117 $/kWh (4 saat 111) [D]; 2040'lar [V]; sabit gider yatırımın %2,5'i"),
    ("jeotermal", 3000, 100, 0, 30, "IRENA 2024 Türkiye 1.217 $/kW, küresel 4.015–5.997 [D]; orta değer [V]"),
    ("biyokutle", 3000, 100, 30, 25, "IRENA 2025 küresel 3.606 $/kW [D]; yakıt 30 $/MWh [V]"),
    ("nukleer_buyuk", 7000 * 1.35, 120, 10, 60, "Gece maliyeti 7.000 $/kW [V] (Barakah ≈4.400, Akkuyu 2010–12 ≈4.200–5.200; Vogtle ≈15.900, Flamanville ≈14.400) × 1,35 inşaat dönemi faizi (≈9,5 yıl)"),
    ("smr", 12700, 150, 10, 60, "Darlington BWRX-300: 4 ünite 20,9 milyar CAD / 1.200 MWe ≈ 17.400 CAD/kW ≈ 12.700 $/kW (0,73 $/CAD) [H]; faiz dahil sayıldı [V]"),
    ("komur", 0, 50, 35, 40, "Mevcut santral; yakıt ithal kömür/linyit karması ≈ 35 $/MWh [V]"),
    ("gaz", 1000, 25, 70, 30, "Kombine çevrim + gaz türbini karması; 10 $/MMBtu × 7,0 MMBtu/MWh [V]"),
], columns=["teknoloji", "yatirim", "sabit", "degisken", "omur", "dayanak"])
TEK = TEK.set_index("teknoloji")
EF = {"komur": 0.91, "gaz": 0.40, "biyokutle": 0.0}  # tCO2/MWh doğrudan; kömür ETKB 2023 linyit 1,122 / ithal 0,800 karması [H]
OLUM_TWH = {  # erken ölüm / TWh
    "komur": 42.7,  # HEAL/CREA 2021: 2019 kömür santrali emisyonları → 4.818 ölüm; TEİAŞ 2019 kömür üretimi 112,9 TWh [H]
    "gaz": 2.821, "biyokutle": 4.63, "hidro": 1.3, "ruzgar": 0.035, "gunes": 0.019, "nukleer": 0.03, "jeotermal": 0.0,
}  # diğerleri OWID (Ritchie 2020; Markandya & Wilkinson 2007) [D]; jeotermal OWID'de yok
OLUM_KOMUR_DUSUK = 24.62  # OWID kömür [D]
SEBEKE_EKI = 8.0          # $/MWh güneş+rüzgâr üretimi — iletim güçlendirmesi [V]
KARBON = 0.0              # $/tCO2 temel; duyarlılıkta 75


def yillik_maliyet(tek: str, kap_mw: float, uretim_mwh: float, wacc=WACC, tablo=None) -> float:
    t = (TEK if tablo is None else tablo).loc[tek]
    if tek == "batarya_kwh":                                          # kap = MWh
        y = t.yatirim * 1000 * kap_mw
        return y * crf(wacc, t.omur) + 0.025 * y
    return kap_mw * 1000 * (t.yatirim * crf(wacc, t.omur) + t.sabit) + uretim_mwh * t.degisken


def smr_lcoe_tablosu() -> pd.DataFrame:
    """SMR için gözlenen ve beyan edilen maliyetlerden LCOE (%7, 60 yıl, KF %90, sabit 150 $/kW·yıl, yakıt 10 $/MWh)."""
    sat = []
    for ad, kw, kaynak in [
        ("DOE Liftoff NOAK (10–20 üniteden sonra)", 3600, "DOE 2023 Liftoff: n'inci örnek ≈3.600 $/kW [İ]"),
        ("DOE Liftoff, iyi yürütülmüş ilk örnek", 6200, "DOE 2023 Liftoff ≈6.200 $/kW [İ]"),
        ("Darlington 4 ünite ortalaması", 12700, "OPG 20,9 milyar CAD / 1.200 MWe [H]"),
        ("Darlington ilk ünite (ortak altyapı dahil)", 18800, "OPG 7,7 milyar CAD / 300 MWe ≈ 25.700 CAD/kW [H]"),
    ]:
        y = kw * crf(WACC, 60) + 150
        sat.append(dict(durum=ad, yatirim_usd_kw=kw, lcoe_usd_mwh=y / (8760 * 0.9) * 1000 + 10, kaynak=kaynak))
    sat += [dict(durum="Lazard LCOE+ 2026, SMR örneği", yatirim_usd_kw=np.nan, lcoe_usd_mwh=214, kaynak="Lazard v19 (Temmuz 2026) [D]"),
            dict(durum="IEA 2025: 2040'a kadar inmesi gereken düzey", yatirim_usd_kw=np.nan, lcoe_usd_mwh=70,
                 kaynak="IEA, The Path to a New Era for Nuclear Energy, 60–80 $/MWh [İ]"),
            dict(durum="NuScale UAMPS (sübvansiyon sonrası, iptal)", yatirim_usd_kw=9.3e9 / 462e3, lcoe_usd_mwh=89,
                 kaynak="IEEFA Ocak 2023: 9,3 milyar $, 462 MWe; >4 milyar $ sübvansiyon sonrası 89 $/MWh [İ]"),
            dict(durum="Akkuyu alım garantisi (büyük reaktör)", yatirim_usd_kw=np.nan, lcoe_usd_mwh=123.5,
                 kaynak="2010 HGA: 12,35 ¢/kWh, 15 yıl [D: WNA]")]
    return pd.DataFrame(sat)


# --------------------------------------------------------------------------------------
# 2. Profiller: güneş, rüzgâr, ulusal sıcaklık, su
# --------------------------------------------------------------------------------------
RUZGAR_FILO_UST = 0.80   # [V] filonun saatlik çıkışı kurulu gücün %80'ini geçmez (arıza, bakım, iz kaybı, coğrafi çeşitlilik)


def ruzgar_profili(kf_hedef=0.34) -> np.ndarray:
    """ERA5 10 m rüzgârı (PVGIS) → 100 m (α 0,143) → genel güç eğrisi → altı sahanın ortalaması → filo üst sınırı;
    KF hedefe ölçeklenir [V]. Altı saha Ege–Marmara meltem kuşağında yoğun; çeşitlilik az olduğu için üst sınır gerekli."""
    sahalar = ["Izmir_Aliaga", "Balikesir_Bandirma", "Canakkale_Ezine", "Manisa_Soma", "Tekirdag_Sarkoy", "Hatay_Belen"]
    W = np.vstack([hizala(seri(f"seri_ruzgar_{s}")["WS10m"]) for s in sahalar]) * (100 / 10) ** 0.143

    def kf(k):
        u = W * k
        p = np.where(u < 3, 0, np.where(u < 12, (u ** 3 - 27) / (12 ** 3 - 27), np.where(u < 25, 1.0, 0.0)))
        return np.minimum(p.mean(axis=0), RUZGAR_FILO_UST)

    lo, hi = 0.5, 3.0
    for _ in range(40):
        k = (lo + hi) / 2
        lo, hi = (k, hi) if kf(k).mean() < kf_hedef else (lo, k)
    return kf((lo + hi) / 2)


def gunes_ac(g20_dc: np.ndarray, yil_saat=1750.0, dc_ac=1.25) -> np.ndarray:
    """kWp başına DC profili → kW_AC başına üretim; yıllık eşdeğer saat hedefe ölçeklenir.
    Hedef: TEİAŞ 2025 güneş 43,52 TWh / ortalama kurulu güç 23,1 GW ≈ 1.890 saat; yeni kapasite girişini düşerek 1.750 [V]."""
    p = g20_dc * dc_ac
    lo, hi = 0.5, 2.0
    for _ in range(40):
        k = (lo + hi) / 2
        lo, hi = (k, hi) if np.minimum(p * k, 1).sum() / NY < yil_saat else (lo, k)
    return np.minimum(p * (lo + hi) / 2, 1.0)


def hidro_aylik_pay() -> np.ndarray:
    a = pd.read_csv(SON / "enerji_turkiye_aylik_2024_2025.csv")
    h = a.groupby("ay")["hidro"].mean()
    return (h / h.sum()).to_numpy()


# --------------------------------------------------------------------------------------
# 3. Sevk
# --------------------------------------------------------------------------------------
def baraj_sevk(artik: np.ndarray, kap: float, aylik_enerji: np.ndarray) -> np.ndarray:
    """Her ay için su bütçesini en yüksek artık yüke dağıt (eşik kesme)."""
    out = np.zeros_like(artik)
    ay = EK.month.to_numpy()
    yil = EK.year.to_numpy()
    for y in YILLAR:
        for m in range(1, 13):
            i = (yil == y) & (ay == m)
            r = artik[i]
            E = aylik_enerji[m - 1]
            if E <= 0 or kap <= 0:
                continue
            ust = np.minimum(np.maximum(r, 0), kap).sum()
            if E >= ust:
                out[i] = np.minimum(np.maximum(r, 0), kap)
                continue
            lo, hi = r.min() - kap, r.max()
            for _ in range(50):
                L = (lo + hi) / 2
                s = np.clip(r - L, 0, kap).sum()
                lo, hi = (L, hi) if s > E else (lo, L)
            out[i] = np.clip(r - (lo + hi) / 2, 0, kap)
    return out


def sevk(talep, gunes, ruzgar, s):
    """s: senaryo sözlüğü (MW, MWh). Döner: kaynak bazında saatlik üretim ve özet."""
    g = {}
    g["nukleer"] = np.full(NH, s.get("nukleer", 0) * 0.90)
    g["jeotermal"] = np.full(NH, s.get("jeotermal", 0) * 0.75)
    g["biyokutle"] = np.full(NH, s.get("biyokutle", 0) * 0.50)      # TEİAŞ 2025: 10,58 TWh / 2.405 MW ≈ 0,50 [H]
    pay = s.get("hidro_aylik_pay")
    gun_ay = np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    hid_E = s.get("hidro_twh", 0) * 1e6 * (pay if pay is not None else np.full(12, 1 / 12))     # MWh/ay
    akarsu_E = hid_E * s.get("akarsu_pay", 0.3)
    g["hidro_akarsu"] = (akarsu_E / (gun_ay * 24))[EK.month.to_numpy() - 1]
    g["komur_asgari"] = np.full(NH, s.get("komur", 0) * s.get("komur_asgari", 0.0))
    g["gunes"] = gunes * s.get("gunes", 0)
    g["ruzgar"] = ruzgar * s.get("ruzgar", 0)
    zorunlu = sum(g.values())
    artik = talep - zorunlu
    g["hidro_baraj"] = baraj_sevk(artik, s.get("baraj_mw", 0), hid_E - akarsu_E)
    artik = artik - g["hidro_baraj"]
    al, ver, des_b = batarya(artik, s.get("batarya_mwh", 0), s.get("batarya_mw"))
    net = al - ver
    al2, ver2, des_p = batarya(net, s.get("pompaj_mwh", 0), s.get("pompaj_mw"), verim=0.78)
    g["depolama"] = (np.maximum(artik, 0) - al) + (np.maximum(net, 0) - al2)                     # deşarj
    acik = al2
    fazla = ver2
    komur_esnek = np.minimum(acik, s.get("komur", 0) * (s.get("komur_kullanilabilir", 0.75) - s.get("komur_asgari", 0.0)))
    g["komur"] = g.pop("komur_asgari") + komur_esnek
    acik = acik - komur_esnek
    g["gaz"] = acik.copy()
    g["kisinti"] = fazla
    return g


def ozet(g, talep, s, ad, olcek="ulke", tablo=None, wacc=WACC, karbon=KARBON, olum_komur=None):
    olum_komur = OLUM_TWH["komur"] if olum_komur is None else olum_komur
    T = talep.sum() / NY
    u = {k: x.sum() / NY for k, x in g.items()}
    gaz_mw = np.percentile(g["gaz"], 100) * 1.15 if g["gaz"].max() > 0 else 0.0         # %15 yedekle gereken gaz gücü
    gaz_mw = max(gaz_mw, s.get("gaz_asgari", 0))
    m = {
        "gunes": yillik_maliyet("gunes", s.get("gunes", 0), u["gunes"], wacc, tablo),
        "ruzgar": (yillik_maliyet("ruzgar_kara", s.get("ruzgar", 0) * (1 - s.get("deniz_pay", 0)), 0, wacc, tablo)
                   + yillik_maliyet("ruzgar_deniz", s.get("ruzgar", 0) * s.get("deniz_pay", 0), 0, wacc, tablo)),
        "hidro": yillik_maliyet("hidro", s.get("hidro_mw", 0), 0, wacc, tablo),
        "jeotermal": yillik_maliyet("jeotermal", s.get("jeotermal", 0), 0, wacc, tablo),
        "biyokutle": yillik_maliyet("biyokutle", s.get("biyokutle", 0), u["biyokutle"], wacc, tablo),
        "nukleer": (yillik_maliyet("nukleer_buyuk", s.get("nukleer", 0) - s.get("smr", 0), u["nukleer"] * (1 - s.get("smr", 0) / max(s.get("nukleer", 1), 1)), wacc, tablo)
                    + yillik_maliyet("smr", s.get("smr", 0), u["nukleer"] * s.get("smr", 0) / max(s.get("nukleer", 1), 1), wacc, tablo)),
        "depolama": (yillik_maliyet("batarya_kwh", s.get("batarya_mwh", 0), 0, wacc, tablo)
                     + yillik_maliyet("pompaj", s.get("pompaj_mw", 0), 0, wacc, tablo)),
        "komur": yillik_maliyet("komur", s.get("komur", 0), u["komur"], wacc, tablo),
        "gaz": yillik_maliyet("gaz", gaz_mw, u["gaz"], wacc, tablo),
        "sebeke": SEBEKE_EKI * (u["gunes"] + u["ruzgar"]),
    }
    co2 = (u["komur"] * EF["komur"] + u["gaz"] * EF["gaz"])
    m["karbon"] = karbon * co2
    olum = (u["komur"] * olum_komur + u["gaz"] * OLUM_TWH["gaz"] + u["biyokutle"] * OLUM_TWH["biyokutle"]
            + (u["hidro_baraj"] + u["hidro_akarsu"]) * OLUM_TWH["hidro"] + u["ruzgar"] * OLUM_TWH["ruzgar"]
            + u["gunes"] * OLUM_TWH["gunes"] + u["nukleer"] * OLUM_TWH["nukleer"]) / 1e6
    top = sum(m.values())
    r = dict(senaryo=ad, olcek=olcek, talep_twh=T / 1e6,
             **{f"uretim_{k}_twh": x / 1e6 for k, x in u.items()},
             gunes_mw=s.get("gunes", 0), ruzgar_mw=s.get("ruzgar", 0), nukleer_mw=s.get("nukleer", 0), smr_mw=s.get("smr", 0),
             batarya_mwh=s.get("batarya_mwh", 0), pompaj_mwh=s.get("pompaj_mwh", 0), komur_mw=s.get("komur", 0),
             gaz_gerekli_mw=gaz_mw, puant_mw=talep.max(),
             fosil_pay=(u["komur"] + u["gaz"]) / T, gaz_pay=u["gaz"] / T, komur_pay=u["komur"] / T,
             # teslim edilen talebin kaynağı: fosil ve nükleer dışındaki her şey yenilenebilir (depolama kaybı ve kısıntı yenilenebilirden)
             nukleer_pay=u["nukleer"] / T,
             yenilenebilir_pay=1 - (u["komur"] + u["gaz"] + u["nukleer"]) / T,
             kisinti_pay=u["kisinti"] / (u["gunes"] + u["ruzgar"] + 1e-9),
             co2_mt=co2 / 1e6, co2_g_kwh=co2 / T * 1000, pm25_olum=olum,
             maliyet_milyar_usd=top / 1e9, maliyet_usd_mwh=top / T,
             **{f"maliyet_{k}_milyar_usd": x / 1e9 for k, x in m.items()})
    return r


# --------------------------------------------------------------------------------------
# 4. Şehir ölçeği (≈210 bin kişi = 30 model mahalle, kademe şeması) — ulusal şebekeye bağlı
# --------------------------------------------------------------------------------------
KENT_MAHALLE = int(v("semt_mahalle") * v("sehir_semt"))          # 5 × 6 = 30
KENT_HIZMET = v("semt_merkezi_el") + v("sehir_hizmet_el")        # 150 + 1.050 = 1.200 kWh/kişi·yıl [V]
P_ALIS = 85.0            # [H/V] $/MWh — şebekeden alış: ülke S2/S3 sistem maliyeti (≈ 84–86 $/MWh, aşağıda hesaplanır)
P_VERIS = 30.0           # [V] $/MWh — öğle fazlasının şebekeye satış değeri (güneşin yoğun olduğu sistemde düşük)
CATI_YATIRIM = 900.0     # [V] $/kWp çatı GES (Fraunhofer 2024 Almanya >30 kWp: 900–1.600 €/kWp [D]; Türkiye fiyatı [DY])
SMR_NOAK = 3600 * 1.2    # DOE Liftoff n'inci örnek 3.600 $/kW × 1,2 inşaat faizi [İ/V]


def hizmet_profili() -> np.ndarray:
    """Konut dışı hizmet yükü: gündüz ağırlıklı + taban; her yıl toplamı 1 [V]."""
    from enerji_ortak import KONUT_DISI, gunluk_profil, okul_tatil_carpani
    p = gunluk_profil(EK, KONUT_DISI) * okul_tatil_carpani(EK) * 0.6 + 0.4 * NY / NH
    return p / p.sum() * NY


def sanayi_profili() -> np.ndarray:
    """Ağır sanayi, liman, havalimanı: düze yakın, gündüz %20 fazla [V]."""
    from enerji_ortak import KONUT_DISI, gunluk_profil
    p = 0.8 * NY / NH + 0.2 * gunluk_profil(EK, KONUT_DISI) * 1.0
    return p / p.sum() * NY


def yerel_karma(talep_mw, cati_mw, cati_mwp, arazi, ruz, izgara, ilce, kisi, ef_2050=0.04, olcek="şehir"):
    """Ulusal şebekeye bağlı bir kademe için yerel karma taraması. izgara: (güneş MW, rüzgâr MW, batarya MWh, nükleer MW).
    Maliyet = yerel varlıkların yıllık bedeli + şebekeden alış (P_ALIS) − şebekeye satış (P_VERIS), talebin MWh'ı başına."""
    ort = talep_mw.mean()
    T = talep_mw.sum() / NY
    sat = []
    for ga, rz, bt, nk in izgara:
        s = dict(gunes=1.0, ruzgar=rz, batarya_mwh=bt, nukleer=nk)
        g = sevk(talep_mw, cati_mw + arazi * ga, ruz, s)
        u = {k: x.sum() / NY for k, x in g.items()}
        alis, veris = u["gaz"], u["kisinti"]
        mal = dict(
            cati=cati_mwp * 1000 * (CATI_YATIRIM * crf(WACC, 25) + 13.5),
            arazi=yillik_maliyet("gunes", ga, 0),
            ruzgar=yillik_maliyet("ruzgar_kara", rz, 0),
            batarya=yillik_maliyet("batarya_kwh", bt, 0),
            nukleer=nk * 1000 * (TEK.loc["smr", "yatirim"] * crf(WACC, 60) + TEK.loc["smr", "sabit"]) + u["nukleer"] * 10,
            alis=alis * P_ALIS, veris=-veris * P_VERIS)
        nk_noak = nk * 1000 * (SMR_NOAK * crf(WACC, 60) + TEK.loc["smr", "sabit"]) + u["nukleer"] * 10
        top = sum(mal.values())
        ic = 1 - g["gaz"] / np.maximum(talep_mw, 1e-9)
        kis = np.isin(EK.month.to_numpy(), (12, 1, 2))
        sat.append(dict(olcek=olcek, ilce=ilce, kisi=kisi, talep_twh=T / 1e6, ort_talep_mw=ort, puant_mw=talep_mw.max(),
                        gunes_cati_mwp=cati_mwp, gunes_arazi_mw=ga, ruzgar_mw=rz, batarya_mwh=bt, nukleer_mw=nk,
                        t_gunes=ga / ort, t_ruzgar=rz / ort, t_batarya_saat=bt / ort, t_nukleer=nk / ort,
                        uretim_cati_twh=cati_mw.sum() / NY / 1e6, uretim_gunes_twh=u["gunes"] / 1e6,
                        uretim_ruzgar_twh=u["ruzgar"] / 1e6, uretim_nukleer_twh=u["nukleer"] / 1e6,
                        uretim_depolama_twh=u["depolama"] / 1e6,
                        sebeke_alis_twh=alis / 1e6, sebeke_veris_twh=veris / 1e6,
                        yerel_karsilama=1 - alis / T, yerel_karsilama_kis=1 - g["gaz"][kis].sum() / talep_mw[kis].sum(),
                        kis_alis_twh=g["gaz"][kis].sum() / NY / 1e6,
                        puant_alis_mw=g["gaz"].max(), puant_veris_mw=g["kisinti"].max(),
                        tam_yerel_saat_payi=float((ic > 0.999).mean()),
                        co2_mt=alis * v("ef_sebeke_2023") / 1e6, co2_mt_2050_sebeke=alis * ef_2050 / 1e6,
                        maliyet_usd_mwh=top / T, maliyet_usd_mwh_smr_noak=(top - mal["nukleer"] + nk_noak) / T,
                        **{f"maliyet_{k}_usd_mwh": x / T for k, x in mal.items()}))
    return pd.DataFrame(sat)


def sehir_talebi(ilce="Kocasinan"):
    """30 model mahalle + 6 semt merkezi + şehir hizmetleri. Döner: sözlük (MW saatlik seriler ve bileşenler)."""
    import enerji_mahalle as em
    e = em.envanter()
    pv = pilot_pv(ilce)
    m = em.mahalle(ilce, e, pv=pv)
    kisi = m["n_kisi"] * KENT_MAHALLE
    hizmet = kisi * KENT_HIZMET * hizmet_profili()                     # kWh/saat
    talep_mw = (m["talep"] * KENT_MAHALLE + hizmet) / 1000
    n_semt = KENT_MAHALLE / v("semt_mahalle")
    semt_kwp = n_semt * v("semt_merkezi_cati") * v("duz_pay") * v("kwp_m2")
    cati_mw = (m["uretim"] * KENT_MAHALLE + semt_kwp * (pv["D10"] + pv["B10"]) / 2) / 1000
    cati_mwp = (e.kwp.sum() * KENT_MAHALLE + semt_kwp) / 1000
    ort_verim = np.mean([pilot_pv(i)["G20"].sum() / NY for i in PILOT_ANAHTAR])
    arazi = gunes_ac(pv["G20"], yil_saat=1750 * (pv["G20"].sum() / NY) / ort_verim)   # yerel ışınıma göre [H]
    return dict(e=e, pv=pv, m=m, kisi=kisi, hizmet=hizmet, talep_mw=talep_mw, cati_mw=cati_mw, cati_mwp=cati_mwp,
                arazi=arazi)


def kent(ilce="Kocasinan", ef_2050=0.04, ruz=None):
    import enerji_mahalle as em
    st = sehir_talebi(ilce)
    m, kisi, hizmet, talep_mw = st["m"], st["kisi"], st["hizmet"], st["talep_mw"]
    ruz = ruzgar_profili() if ruz is None else ruz
    ort = talep_mw.mean()
    sat = []
    # K0 bugünkü yol: ısınma ve pişirme gazla, araç benzinle, elektrik ulusal karmadan (2023 faktörü)
    bugun_el = (m["bilesen"]["aletler"] * (v("hane_elektrik") - em.PISIRME) / v("hane_elektrik") + m["bilesen"]["sogutma"]
                + m["bilesen"]["konut_disi"] + m["bilesen"]["otopark"] + m["bilesen"]["kamusal"]) * KENT_MAHALLE / 1000 + hizmet / 1000
    isi = (m["isi"]["isitma"] + m["isi"]["sicak_su"]) * KENT_MAHALLE / 1000
    gaz_mwh = isi.sum() / NY / v("kombi_verim") + em.PISIRME * m["n_konut"] * KENT_MAHALLE / 1000 / 0.5
    benzin_l = m["n_arac"] * KENT_MAHALLE * v("arac_km") * v("icten_yanmali")
    co2_bugun = (bugun_el.sum() / NY * v("ef_sebeke_2023") + gaz_mwh * v("ef_gaz")) + benzin_l * v("ef_benzin") / 1000
    sat.append(dict(senaryo="K0 Bugünkü yol", aciklama="gaz ısınma ve pişirme, benzinli araç, elektrik ulusal şebekeden",
                    olcek="şehir", ilce=ilce, kisi=kisi, talep_twh=bugun_el.sum() / NY / 1e6, co2_mt=co2_bugun / 1e6,
                    co2_mt_2050_sebeke=np.nan, gaz_twh_yakit=gaz_mwh / 1e6, benzin_milyon_l=benzin_l / 1e6,
                    puant_mw=bugun_el.max(), yerel_karsilama=0.0))
    T = talep_mw.sum() / NY
    sat.append(dict(senaryo="K1a Tam elektrik, yerel üretim yok", aciklama="ısı pompası ve elektrikli araç; bütün elektrik şebekeden",
                    olcek="şehir", ilce=ilce, kisi=kisi, talep_twh=T / 1e6, ort_talep_mw=ort, puant_mw=talep_mw.max(),
                    sebeke_alis_twh=T / 1e6, yerel_karsilama=0.0, maliyet_usd_mwh=P_ALIS, maliyet_alis_usd_mwh=P_ALIS,
                    co2_mt=T * v("ef_sebeke_2023") / 1e6, co2_mt_2050_sebeke=T * ef_2050 / 1e6, puant_alis_mw=talep_mw.max()))
    izgara = [(ga * ort, rz * ort, bt * ort, nk * ort) for ga, rz, bt, nk in
              itertools.product([0, 0.5, 1.0, 1.5, 2.0, 3.0], [0, 0.5, 1.0, 1.5, 2.0, 3.0], [0, 2, 4, 8], [0, 0.2, 0.4, 0.6])]
    tr_ = yerel_karma(talep_mw, st["cati_mw"], st["cati_mwp"], st["arazi"], ruz, izgara, ilce, kisi, ef_2050)
    tr_["t_gunes"], tr_["t_ruzgar"] = tr_["t_gunes"].round(2), tr_["t_ruzgar"].round(2)
    tr_["t_batarya_saat"], tr_["t_nukleer"] = tr_["t_batarya_saat"].round(2), tr_["t_nukleer"].round(2)
    secim = [("K1 Çatı GES + şebeke", "ısı pompası ve elektrikli araç; bütün uygun çatılar", (0, 0, 0, 0)),
             ("K2 Yüksek yenilenebilir", "en ucuz nükleersiz karma: çatı + bölgesel güneş/rüzgâr sözleşmesi + ilçe bataryası",
              None),
             ("K3 Yenilenebilir + SMR payı", "K2 ile aynı yerel karşılama düzeyine nükleer payıyla ulaşan en ucuz karma (Darlington maliyeti)",
              None)]
    k2 = None
    for ad, ac, sabit in secim:
        if sabit is not None:
            b = tr_[(tr_.t_gunes == 0) & (tr_.t_ruzgar == 0) & (tr_.t_batarya_saat == 0) & (tr_.t_nukleer == 0)].iloc[0]
        elif ad.startswith("K2"):
            b = tr_[tr_.t_nukleer == 0].sort_values("maliyet_usd_mwh").iloc[0]
            k2 = b
        else:
            hedef = k2.yerel_karsilama
            aday = tr_[(tr_.t_nukleer > 0) & (tr_.yerel_karsilama >= hedef - 0.01)]
            b = aday.sort_values("maliyet_usd_mwh").iloc[0]
        r = b.to_dict()
        r.update(senaryo=ad, aciklama=ac)
        sat.append(r)
    # K3b: aynı karma, SMR'nin n'inci örnek (iyimser) maliyetiyle
    r = dict(sat[-1])
    r.update(senaryo="K3b Aynı karma, SMR iyimser maliyetle", aciklama="DOE n'inci örnek 3.600 $/kW (10–20 üniteden sonra)",
             maliyet_usd_mwh=r["maliyet_usd_mwh_smr_noak"])
    sat.append(r)
    tr_["senaryo"] = "tarama"
    d = pd.DataFrame(sat)
    d["kisi_basi_co2_t"] = d["co2_mt"] * 1e6 / d["kisi"]
    return d, tr_


# --------------------------------------------------------------------------------------
# 5. Ülke 2050
# --------------------------------------------------------------------------------------
NAT_GUN = np.array([0.86, 0.82, 0.80, 0.79, 0.79, 0.80, 0.84, 0.92, 1.00, 1.05, 1.07, 1.08, 1.07, 1.07, 1.08, 1.08, 1.07,
                    1.06, 1.07, 1.10, 1.10, 1.06, 1.00, 0.93])    # [V] ulusal yük günlük biçimi


SOG_ESIK = 18.0


def gunluk_sicaklik(T):
    """7 günlük (168 saat) merkezli hareketli ortalama: bina ataleti ve davranış [V].
    Eşik 18 °C, öğleden sonra genliği 0,3 ile model 2025'te yıllık puant/ortalama 1,48 veriyor (gözlenen 1,45) [H]."""
    return pd.Series(T).rolling(168, min_periods=1, center=True).mean().to_numpy()


def ulusal_sicaklik() -> np.ndarray:
    return np.mean([pilot_pv(i)["T"] for i in PILOT_ANAHTAR], axis=0)


def ulusal_talep_kalibrasyon(T):
    """TEİAŞ 2024–2025 aylık brüt üretimine (≈ talep) gün sayısı, soğutma ve ısıtma derece-saatiyle uyum (EKK)."""
    a = pd.read_csv(SON / "enerji_turkiye_aylik_2024_2025.csv")
    s = pd.Series(gunluk_sicaklik(T), index=EK)
    cdh = s.sub(SOG_ESIK).clip(lower=0).groupby(EK.month).sum() / NY
    hdh = (15 - s).clip(lower=0).groupby(EK.month).sum() / NY
    gun = pd.Series(np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]), index=range(1, 13))
    a["gun"] = a.ay.map(gun)
    a["cdh"] = a.ay.map(cdh)
    a["hdh"] = a.ay.map(hdh)
    a["trend"] = (a.yil == 2025).astype(float)
    X = np.column_stack([a.gun * 24, a.cdh, a.hdh, a.gun * 24 * a.trend])
    b, *_ = np.linalg.lstsq(X, a.toplam.to_numpy() * 1000, rcond=None)    # MWh
    a["tahmin_gwh"] = X @ b / 1000
    return b, a


def ulusal_talep(T, toplam_twh, b, isi_pompasi_twh=0.0, ev_twh=0.0):
    sa = EK.hour.to_numpy()
    hg = EK.dayofweek.to_numpy()
    gun = NAT_GUN[sa] / NAT_GUN.mean() * np.where(hg == 5, 0.94, np.where(hg == 6, 0.86, 1.0))
    Ts = gunluk_sicaklik(T)
    sog = 1 + 0.3 * np.cos(2 * np.pi * (sa - 15) / 24)                 # soğutma yükü öğleden sonra [V]
    isi = 1 + 0.25 * np.cos(2 * np.pi * (sa - 19) / 24)                # ısıtma yükü akşam [V]
    taban = b[0] * gun + b[1] * np.maximum(Ts - SOG_ESIK, 0) * sog + b[2] * np.maximum(15 - Ts, 0) * isi
    taban = taban / taban.sum() * toplam_twh * 1e6 * NY
    ek_ = np.zeros(NH)
    if isi_pompasi_twh:
        isi = np.maximum(15 - T, 0)
        el = isi / cop_hava(T, v("T_gidis_isitma"))
        el = 0.75 * el / el.sum() + 0.25 / NH                          # %25 sıcak su, düz [V]
        ek_ += el / el.sum() * isi_pompasi_twh * 1e6 * NY
    if ev_twh:
        from enerji_ortak import EV_AKILLI, gunluk_profil
        ek_ += gunluk_profil(EK, EV_AKILLI) * ev_twh * 1e6                # profil her yıl 1'e toplanır
    return taban + ek_


ULKE = {
    # kapasiteler MW (2050) [V]; dayanaklar raporda
    "S1 Mevcut eğilim (UEP 2035 uzatması, kömür sürer)": dict(
        talep_twh=637, gunes=100_000, ruzgar=50_000, deniz_pay=0.10, hidro_mw=36_000, baraj_mw=27_000, hidro_twh=65,
        jeotermal=3_000, biyokutle=3_000, nukleer=7_200, smr=0, komur=20_000, komur_asgari=0.35,
        batarya_mwh=30_000, batarya_mw=15_000, pompaj_mwh=0, pompaj_mw=0, gaz_asgari=25_000, hp=40, ev=60),
    "S2 Yüksek yenilenebilir (kömür 2035'te biter, Akkuyu)": dict(
        talep_twh=637, gunes=210_000, ruzgar=78_000, deniz_pay=0.26, hidro_mw=36_000, baraj_mw=27_000, hidro_twh=65,
        jeotermal=4_500, biyokutle=4_000, nukleer=4_800, smr=0, komur=0, komur_asgari=0.0,
        batarya_mwh=320_000, batarya_mw=80_000, pompaj_mwh=100_000, pompaj_mw=10_000, gaz_asgari=0, hp=40, ev=60, tara=True),
    "S3 Yenilenebilir + nükleer/SMR (20 GW; 5 GW SMR)": dict(
        talep_twh=637, gunes=150_000, ruzgar=60_000, deniz_pay=0.20, hidro_mw=36_000, baraj_mw=27_000, hidro_twh=65,
        jeotermal=4_500, biyokutle=4_000, nukleer=20_000, smr=5_000, komur=0, komur_asgari=0.0,
        batarya_mwh=160_000, batarya_mw=40_000, pompaj_mwh=50_000, pompaj_mw=5_000, gaz_asgari=0, hp=40, ev=60, tara=True),
}


def ulke():
    T = ulusal_sicaklik()
    b, kal = ulusal_talep_kalibrasyon(T)
    kal.to_csv(SON / "enerji_kalibrasyon.csv", index=False)
    pay = hidro_aylik_pay()
    gun = gunes_ac(np.mean([pilot_pv(i)["G20"] for i in PILOT_ANAHTAR], axis=0))
    ruz = ruzgar_profili()
    # 2025 doğrulaması: TEİAŞ kurulu gücüyle ve 2025 talebiyle model
    t25 = ulusal_talep(T, 364.83, b)
    s25 = dict(gunes=25_927, ruzgar=14_792, hidro_mw=32_299, baraj_mw=23_867, hidro_twh=57.44, hidro_aylik_pay=pay,
               jeotermal=1_758, biyokutle=2_405, nukleer=0, komur=21_217, komur_asgari=0.45, batarya_mwh=400, batarya_mw=200)
    g25 = sevk(t25, gun, ruzgar_profili(0.328), s25)                   # 2025 filo KF: 39,77 TWh / 13,8 GW [H]
    r25 = ozet(g25, t25, s25, "2025 doğrulama (TEİAŞ kurulu gücü)")
    r25["puant_gozlenen_mw"] = 60_405.61
    r25["puant_ortalama_orani_model"] = t25.max() / t25.mean()
    r25["puant_ortalama_orani_gozlenen"] = 60_405.61 / (364.83e6 / 8760)
    sat = [r25]
    profiller = {}
    tarama = []
    for ad, s in ULKE.items():
        s = dict(s, hidro_aylik_pay=pay)
        talep = ulusal_talep(T, s["talep_twh"], b, s["hp"], s["ev"])
        if s.get("tara"):
            # nükleer düzeyi sabitken fosil ≤ %10 koşuluyla en ucuz güneş–rüzgâr–batarya karması [H]
            for gu, rz, bt in itertools.product((150_000, 180_000, 210_000, 240_000, 270_000), (60_000, 70_000, 80_000, 90_000, 100_000, 110_000),
                                                (160_000, 240_000, 320_000, 480_000, 640_000)):
                ss = dict(s, gunes=gu, ruzgar=rz, batarya_mwh=bt, batarya_mw=bt / 4)
                rr = ozet(sevk(talep, gun, ruz, ss), talep, ss, ad)
                tarama.append(rr)
            tt = pd.DataFrame([x for x in tarama if x["senaryo"] == ad])
            en = tt[tt.fosil_pay <= 0.10].sort_values("maliyet_usd_mwh").iloc[0]
            s.update(gunes=en.gunes_mw, ruzgar=en.ruzgar_mw, batarya_mwh=en.batarya_mwh, batarya_mw=en.batarya_mwh / 4)
            ULKE[ad].update(gunes=en.gunes_mw, ruzgar=en.ruzgar_mw, batarya_mwh=en.batarya_mwh, batarya_mw=en.batarya_mwh / 4)
        g = sevk(talep, gun, ruz, s)
        r = ozet(g, talep, s, ad)
        sat.append(r)
        profiller[ad] = (talep, g)
        print(f"  {ad[:40]:40s} talep {r['talep_twh']:.0f} TWh · fosil {r['fosil_pay']:.1%} · kısıntı {r['kisinti_pay']:.1%}"
              f" · {r['maliyet_usd_mwh']:.0f} $/MWh · CO2 {r['co2_mt']:.0f} Mt · ölüm {r['pm25_olum']:.0f}")
    d = pd.DataFrame(sat)
    pd.DataFrame(tarama).to_csv(SON / "enerji_ulke_tarama.csv", index=False)
    # duyarlılık
    duy = []
    for ad, s in ULKE.items():
        s = dict(s, hidro_aylik_pay=pay)
        talep, g = profiller[ad]
        for dur, kw in [("temel", {}), ("WACC %10", dict(wacc=0.10)), ("karbon 75 $/t", dict(karbon=75)),
                        ("kömür ölüm katsayısı OWID 24,6", dict(olum_komur=OLUM_KOMUR_DUSUK))]:
            r = ozet(g, talep, s, ad, **kw)
            duy.append(dict(senaryo=ad, durum=dur, maliyet_usd_mwh=r["maliyet_usd_mwh"], maliyet_milyar_usd=r["maliyet_milyar_usd"],
                            pm25_olum=r["pm25_olum"], co2_mt=r["co2_mt"]))
        for dur, deg in [("nükleer ucuz (büyük 4.500 $/kW, SMR 3.600 $/kW)", (4500 * 1.35, 3600 * 1.2)),
                         ("nükleer pahalı (büyük 12.000 $/kW, SMR 18.800 $/kW)", (12000 * 1.35, 18800)),
                         ("batarya 200 $/kWh", None), ("gaz 14 $/MMBtu", None)]:
            tb = TEK.copy()
            if deg:
                tb.loc["nukleer_buyuk", "yatirim"], tb.loc["smr", "yatirim"] = deg
            elif "batarya" in dur:
                tb.loc["batarya_kwh", "yatirim"] = 200
            else:
                tb.loc["gaz", "degisken"] = 14 * 7.0
            r = ozet(g, talep, s, ad, tablo=tb)
            duy.append(dict(senaryo=ad, durum=dur, maliyet_usd_mwh=r["maliyet_usd_mwh"], maliyet_milyar_usd=r["maliyet_milyar_usd"],
                            pm25_olum=r["pm25_olum"], co2_mt=r["co2_mt"]))
        # kurak yıl: su 50 TWh
        s2 = dict(s, hidro_twh=50)
        g2 = sevk(talep, gun, ruz, s2)
        r = ozet(g2, talep, s2, ad)
        duy.append(dict(senaryo=ad, durum="kurak yıl (su 50 TWh)", maliyet_usd_mwh=r["maliyet_usd_mwh"],
                        maliyet_milyar_usd=r["maliyet_milyar_usd"], pm25_olum=r["pm25_olum"], co2_mt=r["co2_mt"],
                        fosil_pay=r["fosil_pay"]))
    pd.DataFrame(duy).to_csv(SON / "enerji_ulke_2050_duyarlilik.csv", index=False)
    # örnek hafta profilleri (grafik için): kış ve yaz haftası, 2022
    hafta = []
    for ad, (talep, g) in profiller.items():
        for etiket, bas in [("kış", "2022-01-17"), ("yaz", "2022-07-18")]:
            i = (EK >= pd.Timestamp(bas)) & (EK < pd.Timestamp(bas) + pd.Timedelta(days=7))
            df = pd.DataFrame({k: x[i] for k, x in g.items()}, index=EK[i])
            df["talep"] = talep[i]
            df["senaryo"], df["hafta"] = ad, etiket
            hafta.append(df.reset_index(names="zaman"))
    pd.concat(hafta).to_csv(SON / "enerji_ulke_2050_hafta.csv", index=False)
    return d


def saglik_ucgenleme():
    """Kömür santrali ölüm tahminlerini proje katsayısıyla (Rapor 13) karşılaştır."""
    import geopandas as gpd  # noqa: F401
    u = pd.read_csv(KOK / "03_VERI" / "islenmis" / "ilce_uydu.csv")
    p = pd.read_csv(KOK / "03_VERI" / "islenmis" / "ilce_paneli.csv", usecols=["gid", "nufus_2025"])
    x = u.merge(p, on="gid")
    pm_nufus = (x.pm25 * x.nufus_2025).sum() / x.nufus_2025.sum()
    olum_2025 = 491_684           # TÜİK 2025 [İ: Wikipedia, TÜİK'e atıfla]
    komur_olum = 4_818            # HEAL/CREA 2021, 2019 emisyonları [D]
    pay = komur_olum / olum_2025
    sat = [dict(gosterge="Nüfus ağırlıklı PM2.5, 2022–2024 (ACAG V6.GL.03, 973 ilçe)", deger=pm_nufus, birim="µg/m³", isaret="H"),
           dict(gosterge="Kömür santrallerine bağlı erken ölüm (2019)", deger=komur_olum, birim="kişi/yıl", isaret="D"),
           dict(gosterge="Toplam ölüm (2025)", deger=olum_2025, birim="kişi", isaret="İ"),
           dict(gosterge="Kömür santrali ölümlerinin toplam ölüme oranı", deger=pay * 100, birim="%", isaret="H"),
           dict(gosterge="PM2.5'e bağlı erken ölüm (Kara Rapor 2025, 2024 yılı)", deger=62_644, birim="kişi/yıl", isaret="D"),
           dict(gosterge="Kömür santrallerinin PM2.5 ölümlerindeki payı (4.818 / 62.644)", deger=komur_olum / 62_644 * 100, birim="%", isaret="H")]
    for ad, beta10 in [("Rapor 13 ilçe katsayısı (+%4,2 / 10 µg/m³)", 0.042), ("Literatür RR 1,08 / 10 µg/m³ (Chen ve Hoek 2020)", 0.08)]:
        dpm = 10 * np.log(1 + pay) / np.log(1 + beta10)
        sat.append(dict(gosterge=f"Bu ölümleri doğuracak nüfus ağırlıklı PM2.5 katkısı — {ad}", deger=dpm, birim="µg/m³",
                        isaret="H" if "Rapor" in ad else "DY"))
    for dpm in (1.0, 2.0, 4.0):        # evsel kömür ve odunun nüfus ağırlıklı katkısı [V]
        for ad, beta10 in [("Rapor 13", 0.042), ("RR 1,08", 0.08)]:
            sat.append(dict(gosterge=f"Evsel katı yakıt katkısı {dpm:g} µg/m³ kalkarsa önlenen ölüm — {ad}",
                            deger=olum_2025 * (1 - 1 / (1 + beta10) ** (dpm / 10)), birim="kişi/yıl", isaret="V"))
    d = pd.DataFrame(sat)
    d.to_csv(SON / "enerji_saglik_ucgenleme.csv", index=False)
    return d


def main():
    TEK.reset_index().to_csv(SON / "enerji_maliyet_varsayim.csv", index=False)
    smr_lcoe_tablosu().to_csv(SON / "enerji_smr_lcoe.csv", index=False)
    print("Sağlık üçgenlemesi")
    print(saglik_ucgenleme().to_string(index=False))
    print("Ülke 2050")
    u = ulke()
    u.to_csv(SON / "enerji_ulke_2050.csv", index=False)
    print("Şehir (≈210 bin kişi = 30 model mahalle)")
    ef50 = u.loc[u.senaryo.str.startswith("S2"), "co2_g_kwh"].iloc[0] / 1000
    sonuc = [kent(i, ef50) for i in ("Kocasinan", "Fatih", "Antakya")]
    k = pd.concat([x[0] for x in sonuc])
    k.to_csv(SON / "enerji_kent_senaryolar.csv", index=False)
    pd.concat([x[1] for x in sonuc]).to_csv(SON / "enerji_kent_tarama.csv", index=False)
    cols = ["senaryo", "ilce", "talep_twh", "yerel_karsilama", "maliyet_usd_mwh", "co2_mt", "co2_mt_2050_sebeke", "gunes_arazi_mw",
            "ruzgar_mw", "batarya_mwh", "nukleer_mw"]
    print(k[[c for c in cols if c in k.columns]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
