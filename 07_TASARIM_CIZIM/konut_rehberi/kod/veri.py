"""
Konut rehberi — ortak veri: iklim, güneş, kıble, mevzuat eşikleri, maliyet
==========================================================================
Faz 4 · Rapor 2 (09_RAPORLAR/15_fitrata_uygun_konut.md) çizim ve tablolarının hepsi bu
modüldeki sayıları kullanır. Her sayının yanında yılı, kaynağı ve işareti yazılıdır:

[D] doğrulandı (resmî metin ya da resmî istatistik bu çalışmada okundu) · [İ] ikincil ·
[DY] doğrulanmadı · [V] bu çalışmanın varsayımı · [H] bu çalışmada hesaplandı.
"""

from __future__ import annotations

import math

# =============================================================================
# 1. İklim: MGM "İl ve ilçelerimize ait istatistiki veriler" sayfaları, 27.10.2026'da okundu [D]
#    https://www.mgm.gov.tr/veridegerlendirme/il-ve-ilceler-istatistik.aspx?m=<IL>
#    Aylık değerler Ocak → Aralık. Konum: il merkezi (yaklaşık) [İ].
# =============================================================================
SEHIR = {
    "Diyarbakır": dict(
        enlem=37.91, boylam=40.22, donem="1929–2025",
        iklim="sıcak-kuru (karasal, kurak yaz)",
        yagis=[68.3, 66.2, 66.6, 67.8, 43.8, 8.4, 1.4, 1.0, 5.7, 32.4, 55.1, 70.3],
        t_ort=[1.8, 3.8, 8.4, 13.9, 19.3, 26.1, 31.0, 30.5, 25.1, 17.6, 9.8, 4.1],
        t_max=[6.8, 9.3, 14.5, 20.5, 26.7, 33.7, 38.5, 38.3, 33.4, 25.4, 16.4, 9.2],
        t_min=[-2.2, -1.0, 2.5, 7.0, 11.3, 16.7, 21.7, 21.1, 16.1, 10.1, 4.2, -0.1]),
    "Bursa": dict(
        enlem=40.19, boylam=29.07, donem="1927–2025",
        iklim="ılıman (Marmara geçiş)",
        yagis=[88.9, 74.9, 69.9, 61.8, 50.0, 35.2, 22.3, 17.7, 42.7, 66.0, 77.6, 99.4],
        t_ort=[5.4, 6.2, 8.4, 13.0, 17.7, 22.1, 24.6, 24.4, 20.4, 15.7, 11.2, 7.4],
        t_max=[9.6, 10.9, 13.9, 19.0, 23.9, 28.4, 31.0, 31.1, 27.3, 22.0, 16.7, 11.7],
        t_min=[1.8, 2.2, 3.6, 7.2, 11.4, 15.0, 17.3, 17.4, 13.8, 10.2, 6.5, 3.6]),
    "İstanbul": dict(
        enlem=41.01, boylam=28.98, donem="1950–2025",
        iklim="ılıman-nemli (Marmara)",
        yagis=[88.8, 70.7, 62.3, 47.8, 32.9, 27.6, 22.1, 23.9, 39.7, 66.3, 78.1, 99.2],
        t_ort=[6.8, 6.9, 8.5, 12.9, 17.6, 22.2, 24.7, 24.7, 21.2, 16.7, 12.6, 9.0],
        t_max=[9.6, 10.2, 12.4, 17.4, 22.3, 27.1, 29.7, 29.7, 25.9, 20.6, 16.1, 11.8],
        t_min=[4.2, 4.2, 5.5, 9.2, 13.6, 18.0, 20.5, 20.8, 17.6, 13.7, 9.9, 6.5]),
    "Ankara": dict(
        enlem=39.93, boylam=32.86, donem="1927–2025",
        iklim="karasal (soğuk kış, kurak yaz)",
        yagis=[39.8, 34.7, 39.2, 42.3, 52.1, 36.8, 14.5, 12.5, 17.9, 26.9, 31.4, 44.1],
        t_ort=[0.4, 1.8, 5.8, 11.3, 16.1, 20.1, 23.5, 23.6, 19.0, 13.2, 7.4, 2.6],
        t_max=[4.4, 6.5, 11.6, 17.4, 22.4, 26.7, 30.4, 30.6, 26.1, 20.0, 13.1, 6.6],
        t_min=[-3.1, -2.2, 0.8, 5.5, 9.7, 13.0, 15.9, 16.1, 11.9, 7.2, 2.6, -0.6]),
}
for _s in SEHIR.values():
    _s["yagis_yil"] = round(sum(_s["yagis"]), 1)          # [H] aylık ortalamaların toplamı

# =============================================================================
# 2. Güneş ve kıble [H]
# =============================================================================
GUN = {"21 Haziran": 172, "21 Mart": 80, "21 Şubat": 52, "21 Aralık": 355}   # yılın günü
KABE = (21.4225, 39.8262)                                                     # enlem, boylam [İ]


def deklinasyon(gun):
    """Cooper (1969) yaklaşımı, derece."""
    return 23.44 * math.sin(math.radians(360.0 * (284 + gun) / 365.0))


def gunes(enlem, gun, saat_acisi):
    """Güneş yüksekliği ve azimutu (kuzeyden saat yönünde), derece. saat_acisi: öğleden derece (15°/sa)."""
    f, d, w = (math.radians(v) for v in (enlem, deklinasyon(gun), saat_acisi))
    sin_a = math.sin(f) * math.sin(d) + math.cos(f) * math.cos(d) * math.cos(w)
    alt = math.degrees(math.asin(max(-1.0, min(1.0, sin_a))))
    az_g = math.degrees(math.atan2(math.sin(w), math.cos(w) * math.sin(f) - math.tan(d) * math.cos(f)))
    return alt, (az_g + 180.0) % 360.0


def ogle_yuksekligi(enlem, gun):
    return 90.0 - enlem + deklinasyon(gun)


def dogus_azimutu(enlem, gun):
    """Gün doğumu azimutu (kuzeyden), derece; batış = 360 − doğuş."""
    f, d = math.radians(enlem), math.radians(deklinasyon(gun))
    return math.degrees(math.acos(max(-1.0, min(1.0, math.sin(d) / math.cos(f)))))


def gun_uzunlugu(enlem, gun):
    f, d = math.radians(enlem), math.radians(deklinasyon(gun))
    return 2.0 * math.degrees(math.acos(-math.tan(f) * math.tan(d))) / 15.0


def kible(enlem, boylam):
    """Kâbe'ye büyük daire başlangıç yönü (kuzeyden saat yönünde), derece [H]."""
    f1, f2 = math.radians(enlem), math.radians(KABE[0])
    dl = math.radians(KABE[1] - boylam)
    th = math.atan2(math.sin(dl) * math.cos(f2), math.cos(f1) * math.sin(f2) - math.sin(f1) * math.cos(f2) * math.cos(dl))
    return math.degrees(th) % 360.0


def _isin_kutu(o, d, k):
    """Işın (o + t·d, t > 0) eksene hizalı kutuyu kesiyor mu? (slab yöntemi)"""
    tmin, tmax = 1e-6, 1e9
    for i in range(3):
        if abs(d[i]) < 1e-12:
            if o[i] < k[i] or o[i] > k[i + 3]:
                return False
        else:
            t1, t2 = (k[i] - o[i]) / d[i], (k[i + 3] - o[i]) / d[i]
            if t1 > t2:
                t1, t2 = t2, t1
            tmin, tmax = max(tmin, t1), min(tmax, t2)
            if tmin > tmax:
                return False
    return True


GUNES_ALT_ESIK = 5.0     # derece; bunun altındaki güneş sayılmaz [V]


def gunes_saati(nokta, normal_az, kutular, enlem, gun, adim_dk=5):
    """Pencere ortasındaki noktaya doğrudan güneşin ulaştığı süre (saat) [H].

    nokta: (x doğu, y kuzey, z) m · normal_az: cephe dış normali (kuzeyden) ·
    kutular: engeller [(x0, y0, z0, x1, y1, z1)] (komşu bina, saçak, duvar). Pencere girintisi yok sayılır."""
    toplam = 0
    adim = adim_dk / 4.0                   # derece saat açısı (1 dk = 0,25°)
    w = -180.0
    while w < 180.0:
        alt, az = gunes(enlem, gun, w + adim / 2)
        if alt > GUNES_ALT_ESIK and math.cos(math.radians(az - normal_az)) > 0.02:
            a, z = math.radians(alt), math.radians(az)
            d = (math.sin(z) * math.cos(a), math.cos(z) * math.cos(a), math.sin(a))
            if not any(_isin_kutu(nokta, d, k) for k in kutular):
                toplam += adim_dk
        w += adim
    return toplam / 60.0


# =============================================================================
# 3. Mevzuat eşikleri [D]
#    PAİY: Planlı Alanlar İmar Yönetmeliği, 01.07.2026 tarihli birleştirilmiş metin
#    (alomaliye.com kopyası "planli-alanlar-01-07-2026.pdf", 27.10.2026'da okundu).
# =============================================================================
PAIY = {
    "md28_kat_yuk_konut": 3.60,     # md. 28/1-c: konut bölgesinde döşemeden döşemeye en fazla (m)
    "md28_kat_yuk_3kat": 4.00,      # md. 28/1-c: bodrum hariç 3 katı geçmeyen binalarda en fazla (m)
    "md28_kat_yuk_tas": 4.50,       # md. 28/1-d: geleneksel kesme taş yığma, zemin dahil ≤ 3 kat
    "md28_ic_yuk": 2.60,            # md. 28/4: iskân edilen katların iç yüksekliği en az (m)
    "md28_ic_yuk_islak": 2.20,      # md. 28/5: ıslak hacim, kiler, geçit en az (m)
    "md29_oturma": (12.0, 3.00),    # md. 29/1: net alan (m²), dar kenar (m)
    "md29_yatak": (9.0, 2.50),
    "md29_mutfak": (3.30, 1.50),
    "md29_banyo": (3.00, 1.50),
    "md29_tuvalet": (1.20, 1.00),
    "md29_koridor": 1.20,           # md. 29/3: hol ve koridor genişliği en az (m)
    "md31_basamak_asansorsuz": 0.16,  # md. 31/2-a: asansörsüz binada basamak yüksekliği en fazla (m)
    "md31_ic_merdiven": 1.00,       # md. 31/1-a: bağımsız bölüm içi merdiven genişliği en az (m)
    "md32": "en az 1 oturma odası ve yatak odaları doğrudan dışarıdan ışık ve hava alır",
    "md34_1": "tek BB'li konut hariç; bodrum dahil 3 kat → asansör yeri, ≥ 4 kat → asansör",
    "md34_2_kabin": (1.20, 1.80),   # tek asansörlü binada kabin dar kenarı (m) ve alanı (m²)
    "md57_7a_yagmur": 0.06,         # yağmur suyu sistemi varsa depo ≥ yıllık toplanabilir suyun %6'sı
}

# =============================================================================
# 4. Yapım maliyeti: 2026 Yapı Yaklaşık Birim Maliyetleri Tebliği (RG 03.02.2026/33157) [D]
#    Sınıflar ve değerler proje M6 modelinden (08_MEVZUAT_POLITIKA/finansman_modeli/varsayimlar.csv)
#    aktarıldı; tebliğdeki %10 yüklenici kârı çıkarıldı (× 0,92) — model mahalle v2 ile aynı.
# =============================================================================
BIRIM_MALIYET = {
    "III.A": 19_800,   # apartman tipi konut ≤ 3 kat; garaj ve kapalı otopark
    "III.B": 21_050,   # konut ≤ 21,50 m (3 kat üzeri); müstakil/ikiz konut < 200 m²
    "III.C": 23_400,   # konut 21,50–30,50 m
    "IV.A": 26_450,    # konut 30,50–51,50 m
}
KAR_HARIC = 0.92
YARI_ACIK_KATSAYI = 0.5          # revak, sundurma, galeri: kapalı alan maliyetinin yarısı [V]
PEYZAJ_M2 = 1_200                # TL/m², açık alan düzenlemesi (M6 [V])
ASANSOR_TL = 1_300_000           # 4 durak, kuyu ve kapılar dahil (model mahalle v2 [V])
ASANSOR_EK_DURAK_TL = 100_000    # [V]
OTOPARK_YER_M2 = 30.0            # bir otopark yeri + rampa/manevra payı (m²) [V]
OTOPARK_BM = BIRIM_MALIYET["III.A"]   # tebliğ: garajlar, kapalı otoparklar III.A [D]
BOLGESEL_OTOPARK_HANE = 0.57     # model mahalle v2.1: 1.235 yer / 2.164 konut [H, metrikler.csv]
ARSA_TL_M2 = (5_000, 25_000)     # arsa birim değeri duyarlılığı: Anadolu kent çeperi · büyükşehir [V]
FIYAT_TR = 42_488                # TL/m², Türkiye ort. konut satış fiyatı, Ağustos 2026 [İ, M6]
TUFE_NOT = "2026 tebliği yıl içinde geçerli; Ekim 2026 fiyatına güncellenmedi [V]"


def yapim_maliyeti(brut_kapali, sinif, yari_acik=0.0):
    bm = BIRIM_MALIYET[sinif] * KAR_HARIC
    return brut_kapali * bm + yari_acik * YARI_ACIK_KATSAYI * bm


# =============================================================================
# 5. Türkiye durumu [D/İ] (09_RAPORLAR/15 §3; 03_VERI/islenmis/turkiye_temel_gostergeler.csv)
# =============================================================================
BKNA_KAT = {"1–2 kat": 29.0, "3–4 kat": 22.0, "5–6 kat": 27.4, "7–9 kat": 11.9, "10+ kat": 9.5}   # % hane, 2021 [D]
BKNA_KAT_TEK = {"1": 11.7, "2": 17.3, "3": 11.3, "4": 10.7, "5": 14.4, "6": 13.0, "7": 6.1, "8": 3.1, "9": 2.7,
                "10+": 9.5}                                                                     # % hane, 2021 [D]
BKNA_ODA = {"1": 0.3, "2": 6.3, "3": 38.6, "4": 47.5, "6+": 1.4}    # % hane, 2021 [İ, bülten metni aktarımı]
BKNA_ODA["5"] = round(100 - sum(BKNA_ODA.values()), 1)                # [H] kalan
BKNA_DIGER = {
    "asansorsuz_3plus": 53.6,      # 3+ katlı binada oturan hanelerin %'si asansörsüz [D]
    "asansorsuz_6plus": 23.2,      # 6+ katlı binada oturan hanelerin %'si asansörsüz [İ]
    "otoparksiz": 57.0,            # [D]
    "ev_sahibi": 60.7, "kiraci": 27.6,   # [D]
    "insa_2001_sonra": 47.4,       # [D]
}
EUROSTAT = {"kisi_basi_oda_TR_2025": 1.1, "kisi_basi_oda_AB_2025": 1.7,
            "asiri_kalabalik_TR_2025": 37.8, "asiri_kalabalik_AB_2025": 16.8}    # ilc_lvho03, ilc_lvho05a [D]
HANE_BUYUKLUGU_2025 = 3.08          # TÜİK İstatistiklerle Aile 2025 [D]
IGD_KONUT_M2 = {"tum_2010": 122.2, "tum_2025": 101.9, "daire_2010": 121.0, "daire_2025": 97.0,
                "mustakil_2025": 183.1}   # İstanbul Gayrimenkul Değerleme; Hürriyet Daily News 17.05.2026 [İ]

# =============================================================================
# 6. Bu rehberin ölçütleri (öneri) — değerlerin dayanağı raporun §2 tablosunda
# =============================================================================
HANE = 5                         # karşılaştırma hanesi: 2 ebeveyn + 3 çocuk [V]
OLCUT = {
    "net_kisi_asgari": 22.0,     # m²/kişi [V]
    "net_kisi_hedef": 25.0,      # m²/kişi; Genelge 2026/4 ölçüt 11 önerisi (proje paketi G1) [V]
    "pencere_taban": 1 / 8,      # yaşam ve yatak odalarında cam alanı / taban alanı, en az [İ/V]
    "pencere_taban_hedef": 1 / 6,
    "gunes_saat_asgari": 1.5,    # 21 Şubat'ta ana yaşam odası, saat (TS EN 17037 "asgari") [İ]
    "gunes_saat_orta": 3.0,      # TS EN 17037 "orta" [İ]
    "ic_yukseklik": 2.70,        # m, net (PAİY en az 2,60) [V]
    "acik_alan_kisi": 10.0,      # m²/kişi özel ya da ortak dış mekân (Genelge ölçüt 14'ün kişi başı karşılığı) [V]
    "balkon_derinlik": 1.8,      # m, oturulabilir balkon/teras [V]
    "depolama_pay": 0.08,        # net alanın payı (kiler, yüklük, dolap) [V]
    "kiler_m2": 2.0,             # serin kiler en az [V]
    "yagmur_m3_100m2": 2.0,      # çatı 100 m² başına depo hacmi (m³) [V]
    "gece_ic_dB": 30,            # yatak odası LAeq gece, DSÖ 1999 [İ]
    "gece_dis_dB": 45,           # dış Lnight, DSÖ 2018 karayolu [İ]
}


def yagmur_potansiyeli(cati_m2, sehir, verim=0.8):
    """Yıllık toplanabilir yağmur suyu (m³) [H]: çatı izdüşümü × yıllık yağış × verim (0,8 [V])."""
    return cati_m2 * SEHIR[sehir]["yagis_yil"] / 1000.0 * verim


def tr(metin):
    return str(metin).replace(",", "§").replace(".", ",").replace("§", ".")


def sayi(v, ond=0):
    """Türkçe sayı biçimi: binlik ayraç nokta, ondalık virgül."""
    return tr(f"{v:,.{ond}f}")


def yuzde(v, ond=0):
    return "%" + sayi(v, ond)
