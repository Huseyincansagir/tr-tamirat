"""
M6 — Konut ekonomisi ve finansman modeli (sürüm 1.0, 26 Ekim 2026)
====================================================================

Soru
----
Aynı 1 hektarlık arsada üç yapılaşma biçimi finansal olarak nasıl karşılaştırılır?

  A) 12 katlı blok (kat karşılığı, "kapalı site")
  B) Zemin + 3 katlı bitişik nizam çevre adası (zeminde çarşı)
  C) Zemin + 2 katlı avlulu, çok kuşaklı sıra ev (parsel başına 2 hane)

Geometri ve m² değerleri `07_TASARIM_CIZIM/ayni_yogunluk_uc_bicim_metrikler.csv`
dosyasından okunur (salt okunur). A'nın emsali duyarlılık analizinde
değiştirilir; B ve C çizimdeki hâliyle sabit kalır.

Yöntem
------
1. **Arsa kalıntı değeri (AKD).** Müteahhidin istediği reel getiriyle (iskonto)
   indirgenmiş net satış geliri eksi indirgenmiş maliyet. AKD, arsa sahibine
   kat karşılığında verilebilecek en yüksek değerdir. Arsa sahibi hangi biçimi
   seçeceğine AKD'ye bakarak karar verir. AKD / bugünkü net gelir oranı,
   arsa sahibine bırakılabilecek azami pay (%) anlamına gelir.
2. **Aylık nakit akışı, reel 2026 TL.** Enflasyon modellenmez; bütün tutarlar
   2026 fiyatlarıyladır. İskonto oranı reeldir.
3. **Kırılma emsali.** Verilen satış fiyatında A'nın AKD'si C'ninkini hangi
   emsalde geçer? Plan emsali bu değerin altındaysa az katlı seçenek ayakta kalır.
4. **Telafi köprüsü.** A ile C arasındaki AKD farkını hangi araç ne kadar kapatır?
5. **Teslim ve finansman modelleri.** Kat karşılığı, arsa payı / yapı grubu,
   kooperatif, vakıf (üst hakkı), maliyet kirası; piyasa kredisi, aile konut
   kredisi (öneri), TOKİ tipi sabit taksit. Hane gelirine oranla aylık yük.
6. **Dönüşüm senaryosu (6306).** Mevcut 96 malike birer konut verilen yerinde
   dönüşümde kat karşılığının kendini finanse etmesi için gereken emsal.

Kaynak etiketleri (varsayimlar.csv): [D] doğrulandı (birincil kaynak),
[İ] ikincil aktarım, [H] bu modelde hesaplandı, [V] varsayım (doğrulanmadı).

Çalıştırma:  python m6_konut_ekonomisi.py
Çıktılar   :  bu klasördeki *.csv ve iki grafik (png + svg)
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field, replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

CIKTI = Path(__file__).resolve().parent
KOK = CIKTI.parents[1]
METRIK_CSV = KOK / "07_TASARIM_CIZIM" / "ayni_yogunluk_uc_bicim_metrikler.csv"

# Renk paleti (kullanıcı tanımı; doğrulayıcıdan geçti: CVD ΔE ≥ 9,2)
MAVI, TURUNCU, AQUA, ZEMIN = "#2a78d6", "#eb6834", "#1baf7a", "#fcfcfb"
MUREKKEP, IKINCIL, SOLUK, IZGARA = "#1f2328", "#4b5563", "#6b7280", "#e6e6e3"
NOTR = "#5b6470"


# =============================================================================
# 1. VARSAYIMLAR
# =============================================================================
@dataclass
class Prm:
    # --- Gelir ---------------------------------------------------------------
    fiyat: float = 42_488.0          # TL/m² satılabilir brüt; Türkiye ort., Ağustos 2026 [İ]
    prim: dict = field(default_factory=lambda: {"A": 0.0, "B": 0.0, "C": 0.0})
    ticari_carpan: float = 1.25      # zemin kat dükkânı / konut m² fiyatı [V]
    satis_gider: float = 0.02        # pazarlama, komisyon [V]
    satici_harc: float = 0.02        # tapu harcı satıcı payı binde 20 [D: 492 s.K. (4) s. tarife 20/a]
    on_satis: float = 0.35           # inşaat sürerken satılan pay [V]
    satis_suresi_ay: int = 12        # tamamlanma sonrası satış süresi [V]
    # --- Maliyet -------------------------------------------------------------
    bm: dict = field(default_factory=lambda: {"A": 26_450.0, "B": 21_050.0, "C": 21_050.0})
    # 2026 Yapı Yaklaşık Birim Maliyetleri Tebliği (RG 03.02.2026/33157) [D]:
    # A: IV.A konut 30,50–51,50 m · B: III.B konut ≤21,50 m, 3 kat üzeri ·
    # C: III.B müstakil/ikiz konut <200 m² (III.A apartman ≤3 kat = 19.800 alternatif)
    bm_kar_haric: float = 1.15 / 1.25  # tebliğ BM'si %15 genel gider + %10 kâr içerir [D]; kâr çıkarıldı
    maliyet_carpani: dict = field(default_factory=lambda: {"A": 1.0, "B": 1.0, "C": 1.0})
    satilabilir_oran: dict = field(default_factory=lambda: {"A": 0.82, "B": 0.86, "C": 0.92})  # [V]
    yumusak_oran: float = 0.07       # proje, ruhsat, harç, yapı denetim, sigorta / yapım [V]
    altyapi_hane: float = 60_000.0   # bina dışı bağlantılar, TL/hane [V]
    peyzaj_m2: float = 1_200.0       # açık alan düzenlemesi, TL/m² [V]
    peyzaj_doseme_m2: float = 2_500.0  # bodrum üstü avlu (toprak örtüsü, yalıtım), TL/m² [V]
    sokak_m2: float = 2_000.0        # ada içi paylaşımlı sokak, TL/m² [V]
    sure_ay: dict = field(default_factory=lambda: {"A": 30, "B": 20, "C": 16})  # [V]
    # --- Otopark -------------------------------------------------------------
    otopark_rejimi: str = "mevcut"   # "mevcut" (Ek-1) | "reform" (hane başına 0,5; bölgesel)
    yuzey_park_tl: float = 50_000.0  # açık otopark, yer başına [V]
    bodrum_m2_yer: float = 30.0      # rampa ve manevra dahil brüt alan / araç [V]
    bodrum_ek: float = 1.10          # kazı, iksa, su yalıtımı katsayısı [V]
    otopark_bm: float = 19_800.0     # III.A "garajlar, katlı/kapalı otoparklar" [D: tebliğ]
    emlak_degeri_m2: float = 3_000.0  # otopark bedeli formülündeki A terimi, TL/m² [V]
    # --- Finans --------------------------------------------------------------
    iskonto_reel: float = 0.15       # müteahhidin istediği reel yıllık getiri [V]
    # --- Telafi araçları -----------------------------------------------------
    tdr_fiyat_orani: float = 0.60    # TDR m² fiyatı = alıcı bölgede emsal m² başına arsa değeri × oran [V]


TEMEL = Prm()
FIYAT_TR = 42_488.0   # Endeksa/Emlakjet, Ağustos 2026 Türkiye ort. [İ]
FIYAT_IST = 63_788.0  # Endeksa/Emlakjet, Haziran 2026 İstanbul ort. [İ]
FIYAT_DUSUK = 30_000.0  # deprem bölgesi ve küçük Anadolu kentleri için temsilî değer [V]

ARSA_M2 = 10_000.0     # 1 ha brüt hücre (çevre yolların yarısı dahil)
NET_PARSEL_A = 6_400.0  # A'nın site sınırı içi net alanı (80 × 80 m), çizimden
YUZEY_OTOPARK_A = 760.0  # A'daki yüzey otoparkı (76 × 10 m), çizimden
C_IC_SOKAK = 540.0     # C'deki ara sokak (6 × 90 m), çizimden
PLAN_EMSALI_REF = 2.0  # telafi köprüsünde mevcut plan hakkı olarak kabul edilen emsal [V]

VARSAYIM_SATIRLARI = [
    ("fiyat_tr", FIYAT_TR, "TL/m²", "Endeksa/Emlakjet Ağustos 2026 Konut Değer Raporu, Türkiye ort. satış m² fiyatı (foreks.com aktarımı, 21.09.2026)", "İ"),
    ("fiyat_istanbul", FIYAT_IST, "TL/m²", "Endeksa/Emlakjet Haziran 2026 raporu, İstanbul ort. (basın aktarımı)", "İ"),
    ("fiyat_dusuk", FIYAT_DUSUK, "TL/m²", "Deprem bölgesi / küçük kent için temsilî değer", "V"),
    ("kira_m2_ay", 268.26, "TL/m²·ay", "Mayıs 2026 ort. kiralık konut m² bedeli (basın aktarımı, Endeksa)", "İ"),
    ("bm_IVA", 26_450, "TL/m²", "2026 Yapı Yaklaşık Birim Maliyetleri Tebliği, RG 03.02.2026/33157: IV.A konut 30,50–51,50 m", "D"),
    ("bm_IIIC", 23_400, "TL/m²", "Aynı tebliğ: III.C konut 21,50–30,50 m", "D"),
    ("bm_IIIB", 21_050, "TL/m²", "Aynı tebliğ: III.B konut ≤21,50 m (3 kat üzeri); müstakil/ikiz konut <200 m²", "D"),
    ("bm_IIIA", 19_800, "TL/m²", "Aynı tebliğ: III.A apartman tipi konut ≤3 kat; garaj ve kapalı otoparklar; kreşler", "D"),
    ("bm_kar_haric", round(1.15 / 1.25, 4), "katsayı", "Tebliğ BM'si KDV hariç, %15 genel gider + %10 yüklenici kârı dahil; kâr payı çıkarıldı", "D/H"),
    ("satilabilir_oran_A_B_C", "0,82 / 0,86 / 0,92", "oran", "Satılabilir brüt / toplam inşaat (çekirdek, merdiven, asansör, lobi payı)", "V"),
    ("yumusak_oran", 0.07, "yapımın payı", "Proje, ruhsat, harç, yapı denetim, sigorta", "V"),
    ("altyapi_hane", 60_000, "TL/hane", "Bina dışı bağlantılar (tebliğ BM'sine dahil değil)", "V"),
    ("peyzaj_m2", 1_200, "TL/m²", "Açık alan düzenlemesi (tebliğ BM'sine dahil değil)", "V"),
    ("peyzaj_doseme_m2", 2_500, "TL/m²", "Bodrum üstü avlu", "V"),
    ("sure_ay_A_B_C", "30 / 20 / 16", "ay", "Yapım süresi; 6 Şubat sonrası Z+3 deneyimi ve tünel kalıp blok pratiği", "V"),
    ("otopark_Ek1_mesken", "<80 m²: 3 daireye 1; 80–120: 2 daireye 1; 120–180: daireye 1; ≥180: daireye 2", "yer", "Otopark Yönetmeliği Ek-1 (RG 22.02.2018/30340; değişik RG 25.03.2021/31434); hesap bağımsız bölüm brüt alanı üzerinden (md. 8/3)", "D"),
    ("otopark_Ek1_dukkan", "50 m² için 1", "yer", "Otopark Yönetmeliği Ek-1", "D"),
    ("otopark_bedeli_formulu", "(A + B) × 20 × Y", "TL/yer", "Otopark Yönetmeliği md. 12(11); B = tebliğdeki otopark birim fiyatı (III.A 19.800)", "D"),
    ("emlak_degeri_m2", 3_000, "TL/m²", "Bedel formülündeki A terimi (emlak vergisi değeri / katlar alanı)", "V"),
    ("bodrum_m2_yer", 30, "m²/araç", "Rampa ve manevra dahil", "V"),
    ("bodrum_ek", 1.10, "katsayı", "Kazı, iksa, su yalıtımı", "V"),
    ("yuzey_park_tl", 50_000, "TL/yer", "Açık otopark kaplaması", "V"),
    ("tapu_harci", "binde 20 + binde 20", "oran", "492 sayılı Harçlar Kanunu (4) sayılı tarife 20/a; alıcı ve satıcı ayrı ayrı (mevzuat.gov.tr)", "D"),
    ("iskonto_reel", 0.15, "yıllık", "Müteahhidin istediği reel getiri (risk ve kâr dahil)", "V"),
    ("on_satis", 0.35, "pay", "İnşaat sürerken satılan konut payı", "V"),
    ("satis_suresi_ay", 12, "ay", "Tamamlanma sonrası satış süresi", "V"),
    ("satis_gider", 0.02, "gelirin payı", "Pazarlama ve komisyon", "V"),
    ("ticari_carpan", 1.25, "katsayı", "B'deki zemin kat dükkânı m² fiyatı / konut m² fiyatı", "V"),
    ("plan_emsali_ref", PLAN_EMSALI_REF, "emsal", "Telafi köprüsünde mevcut plan hakkı", "V"),
    ("tdr_fiyat_orani", 0.60, "oran", "TDR m² fiyatı = alıcı bölgede emsal m² başına arsa değeri × 0,60", "V"),
    ("politika_faizi", 0.37, "yıllık", "TCMB PPK 10.09.2026 (basın aktarımı)", "İ"),
    ("konut_kredisi_aylik", 0.028, "aylık", "Mayıs 2026 banka aralığı %2,49–3,10 (basın aktarımı); orta değer", "İ"),
    ("konut_kredisi_ltv", 0.80, "oran", "Kredi / değer oranı", "V"),
    ("asgari_ucret_net_2026", 28_075.50, "TL/ay", "Asgari Ücret Tespit Komisyonu 2025/1 kararı (RG 26.12.2025), ikincil aktarım", "İ"),
    ("medyan_esdeger_fert_geliri_2025", 241_151, "TL/yıl", "TÜİK Gelir ve Yaşam Koşulları 2025 (2024 gelirleri), ikincil aktarım", "İ"),
    ("esdegerlik_olcegi", 2.1, "katsayı", "OECD modifiye ölçek: 2 yetişkin + 2 çocuk (<14)", "D"),
    ("gelir_artisi_2024_2026", 1.60, "katsayı", "Nominal hane geliri artışı 2024→2026", "V"),
    ("toki_80m2_fiyat", 2_650_000, "TL", "Yüzyılın Konut Projesi 80 m² 2+1 (Anadolu); %10 peşin, 240 ay sabit taksit (basın aktarımı)", "İ"),
    ("yarisi_bizden", "875 bin hibe + 875 bin kredi + 125 bin taşınma", "TL/konut", "ÇŞİDB haberi 20.10.2026 (mevzuat haritası 1.4); RG künyesi doğrulanmadı", "İ"),
    ("aile_kredisi_reel_faiz", 0.02, "yıllık reel", "Öneri: TÜFE endeksli, 240 ay, %10 peşin", "V"),
    ("kamu_iskonto_reel", 0.05, "yıllık reel", "Kamu borçlanmasının reel maliyeti", "V"),
    ("enflasyon_varsayimi", 0.25, "yıllık", "Sabit nominal taksitlerin reel değer kaybı için ortalama TÜFE", "V"),
]


# =============================================================================
# 2. GEOMETRİ (çizimden)
# =============================================================================
def metrikleri_oku() -> dict:
    tablo = {}
    with open(METRIK_CSV, encoding="utf-8") as f:
        for satir in csv.reader(f):
            if satir and satir[0] != "gosterge":
                tablo[satir[0]] = satir[1:]

    def sayi(anahtar, i):
        return float(tablo[anahtar][i])

    g = {}
    for i, k in enumerate("ABC"):
        g[k] = dict(
            hane=sayi("Hane sayısı (hane/ha)", i),
            insaat=sayi("Brüt inşaat alanı (m²)", i),
            kat=sayi("Kat adedi", i),
            yukseklik=sayi("Bina yüksekliği (m)", i),
            ortak_acik=sayi("Ortak açık alan, ada içi (m²)", i),
            ozel_bahce=sayi("Özel bahçe/avlu (m²)", i),
            ticari_cephe=sayi("Zemin kat ticaret cephesi (m)", i),
        )
    g["B"]["ticari"] = g["B"]["ticari_cephe"] * 12.0  # 76 m cephe × 12 m derinlik (çizim)
    g["A"]["ticari"] = g["C"]["ticari"] = 0.0
    g["A"]["emsal"] = g["A"]["insaat"] / ARSA_M2
    return g


GEO = metrikleri_oku()


# =============================================================================
# 3. TİPOLOJİ HESABI
# =============================================================================
def ek1_mesken(bb_brut: float) -> float:
    """Otopark Yönetmeliği Ek-1, meskenler: daire başına yer sayısı."""
    if bb_brut < 80:
        return 1 / 3
    if bb_brut < 120:
        return 1 / 2
    if bb_brut < 180:
        return 1.0
    return 2.0


def tipoloji(kod: str, p: Prm, emsal: float | None = None) -> dict:
    g = dict(GEO[kod])
    if kod == "A" and emsal is not None:  # 12 kat sabit, blok sayısı artar
        olcek = emsal * ARSA_M2 / g["insaat"]
        g["insaat"] = emsal * ARSA_M2
        g["hane"] = round(GEO["A"]["hane"] * olcek)
        taban = g["insaat"] / 12
        g["ortak_acik"] = max(0.0, NET_PARSEL_A - taban - YUZEY_OTOPARK_A)
    g["hane"] = int(g["hane"])
    g["emsal"] = g["insaat"] / ARSA_M2
    oran = p.satilabilir_oran[kod]
    konut_insaat = g["insaat"] - g["ticari"]
    sat_konut = konut_insaat * oran
    sat_ticari = g["ticari"] * 0.95
    bb = sat_konut / g["hane"]

    # --- otopark -------------------------------------------------------------
    if p.otopark_rejimi == "mevcut":
        ihtiyac = math.ceil(g["hane"] * ek1_mesken(bb)) + math.ceil(g["ticari"] / 50)
    else:  # reform: daire büyüklüğünden bağımsız, hane başına 0,5; ticari 100 m²'ye 1
        ihtiyac = math.ceil(0.5 * g["hane"]) + math.ceil(g["ticari"] / 100)
    bedel_yer = (p.emlak_degeri_m2 + p.otopark_bm) * 20 * 1.0
    bodrum_yer = p.bodrum_m2_yer * p.otopark_bm * p.bm_kar_haric * p.bodrum_ek
    n_yuzey = n_bodrum = n_bedel = 0
    if kod == "A":
        n_yuzey = min(ihtiyac, int(YUZEY_OTOPARK_A // 20))
        kalan = ihtiyac - n_yuzey
        if p.otopark_rejimi == "mevcut":
            n_bodrum = kalan
        else:
            n_bedel = kalan
    elif kod == "B":
        if p.otopark_rejimi == "mevcut":
            n_bodrum = ihtiyac      # avlu altında bodrum
        else:
            n_bedel = ihtiyac       # bölgesel otopark
    else:  # C: dar parsel, ön bahçesiz: md. 4(1)(e)(1) teknik imkânsızlık → bedel
        n_bedel = ihtiyac
    otopark = n_yuzey * p.yuzey_park_tl + n_bodrum * bodrum_yer + n_bedel * bedel_yer

    # --- maliyet -------------------------------------------------------------
    yapim = g["insaat"] * p.bm[kod] * p.bm_kar_haric * p.maliyet_carpani[kod]
    if kod == "B" and n_bodrum > 0:
        peyzaj = g["ortak_acik"] * p.peyzaj_doseme_m2
    else:
        peyzaj = g["ortak_acik"] * p.peyzaj_m2
    peyzaj += g["ozel_bahce"] * p.peyzaj_m2 * 0.5
    if kod == "C":
        peyzaj += C_IC_SOKAK * p.sokak_m2
    altyapi = g["hane"] * p.altyapi_hane
    yumusak = yapim * p.yumusak_oran
    maliyet = yapim + otopark + peyzaj + altyapi + yumusak

    # --- gelir ---------------------------------------------------------------
    fiyat = p.fiyat * (1 + p.prim[kod])
    gdv = sat_konut * fiyat + sat_ticari * p.fiyat * p.ticari_carpan

    r = dict(kod=kod, emsal=g["emsal"], hane=g["hane"], insaat=g["insaat"], kat=g["kat"],
             sat_konut=sat_konut, sat_ticari=sat_ticari, bb_brut=bb, otopark_ihtiyac=ihtiyac,
             n_yuzey=n_yuzey, n_bodrum=n_bodrum, n_bedel=n_bedel,
             yapim=yapim, otopark=otopark, peyzaj=peyzaj, altyapi=altyapi, yumusak=yumusak,
             maliyet=maliyet, gdv=gdv, sure=p.sure_ay[kod])
    r.update(nakit_akisi(r, p))
    return r


def nakit_akisi(r: dict, p: Prm) -> dict:
    """Aylık reel nakit akışı ve bugünkü değerler (ay 0 = ruhsat)."""
    D, S = r["sure"], p.satis_suresi_ay
    n = D + S + 1
    gider = [0.0] * n
    gelir = [0.0] * n

    def yay(dizi, tutar, bas, bit):
        bas, bit = max(0, bas), max(bas, bit)
        k = bit - bas + 1
        for m in range(bas, bit + 1):
            dizi[m] += tutar / k

    yay(gider, r["yapim"], 1, D)
    gider[0] += 0.4 * r["yumusak"]
    yay(gider, 0.6 * r["yumusak"], 1, D)
    if r["n_bedel"]:
        bedel_toplam = r["otopark"] - r["n_yuzey"] * p.yuzey_park_tl - r["n_bodrum"] * (
            p.bodrum_m2_yer * p.otopark_bm * p.bm_kar_haric * p.bodrum_ek)
        gider[0] += 0.25 * bedel_toplam  # md. 12(9): %25 ruhsatta, kalan iskândan önce
        yay(gider, 0.75 * bedel_toplam, 1, D)
        diger_otopark = r["otopark"] - bedel_toplam
    else:
        diger_otopark = r["otopark"]
    yay(gider, diger_otopark, 1, max(1, D // 2))
    yay(gider, r["peyzaj"] + r["altyapi"], max(1, D - 2), D)

    net_oran = 1 - p.satis_gider - p.satici_harc
    yay(gelir, p.on_satis * r["gdv"] * net_oran, min(6, D), D)
    yay(gelir, (1 - p.on_satis) * r["gdv"] * net_oran, D + 1, D + S)

    rm = (1 + p.iskonto_reel) ** (1 / 12) - 1
    iskonto = [(1 + rm) ** -m for m in range(n)]
    bd_gelir = sum(a * b for a, b in zip(gelir, iskonto))
    bd_gider = sum(a * b for a, b in zip(gider, iskonto))
    akd = bd_gelir - bd_gider  # TDR geliri telafi fonksiyonlarında ayrıca eklenir
    return dict(bd_gelir=bd_gelir, bd_gider=bd_gider, akd=akd,
                azami_pay=akd / bd_gelir if bd_gelir else float("nan"))


def akd(kod, p, emsal=None):
    return tipoloji(kod, p, emsal)["akd"]


# =============================================================================
# 4. TELAFİ ARAÇLARI
# =============================================================================
def tdr_degeri(p: Prm, plan_emsali: float, alici_akd_m2: float) -> float:
    """Kullanılmayan emsalin (plan emsali − C emsali) alıcı bölgeye devri, TL (ay 0)."""
    devredilen = max(0.0, plan_emsali - GEO["C"]["insaat"] / ARSA_M2) * ARSA_M2
    return devredilen * max(0.0, alici_akd_m2) * p.tdr_fiyat_orani


def paket_C(p: Prm) -> Prm:
    """Reform ve telafi paketi (TDR hariç): otopark reformu, harç/ücret indirimi, hızlı onay."""
    return replace(p, otopark_rejimi="reform", satici_harc=0.005,
                   yumusak_oran=p.yumusak_oran - 0.015,
                   sure_ay={**p.sure_ay, "C": p.sure_ay["C"] - 3})


def kirilma_emsali(p: Prm, senaryo: str, ust=4.0, adim=0.01) -> float:
    """A'nın AKD'sinin C'ninkini geçtiği en küçük emsal (yoksa inf).

    "paket" senaryosunda otopark reformu genel kuraldır, A'ya da uygulanır;
    harç indirimi, hızlı onay ve TDR yalnız aile dostu az katlı projeye (C) verilir.
    """
    pA = p
    if senaryo in ("dar", "paket"):
        pA = replace(p, bm={**p.bm, "A": p.bm["C"] * 1.10})
    pC = paket_C(pA) if senaryo == "paket" else pA
    if senaryo == "paket":
        pA = replace(pA, otopark_rejimi="reform")
    akd_c0 = akd("C", pC)
    e = 1.0
    while e <= ust + 1e-9:
        a = akd("A", pA, e)
        c = akd_c0
        if senaryo == "paket":
            c += tdr_degeri(pA, e, a / (e * ARSA_M2))
        if a > c:
            return round(e, 2)
        e += adim
    return float("inf")


# =============================================================================
# 5. FİNANSMAN VE HANE BÜTÇESİ
# =============================================================================
def anuite(anapara, aylik_faiz, ay):
    if aylik_faiz == 0:
        return anapara / ay
    return anapara * aylik_faiz / (1 - (1 + aylik_faiz) ** -ay)


MEDYAN_AILE_GELIRI_AY = 241_151 * 2.1 * 1.60 / 12   # [H] ≈ 67.500 TL/ay (2026)
IKI_ASGARI = 2 * 28_075.50                             # [İ] 56.151 TL/ay
KIRA_M2 = 268.26                                       # [İ]


def kamu_maliyeti_endeksli(oran_reel, ay=240, kamu_reel=0.05):
    """1 TL reel kredinin kamuya bugünkü maliyeti (sübvansiyon payı)."""
    r = (1 + oran_reel) ** (1 / 12) - 1
    k = (1 + kamu_reel) ** (1 / 12) - 1
    t = anuite(1.0, r, ay)
    return 1 - sum(t / (1 + k) ** m for m in range(1, ay + 1))


def kamu_maliyeti_sabit_nominal(ay=240, enflasyon=0.25, kamu_reel=0.05):
    pi = (1 + enflasyon) ** (1 / 12) - 1
    k = (1 + kamu_reel) ** (1 / 12) - 1
    t = 1.0 / ay
    return 1 - sum(t / ((1 + pi) * (1 + k)) ** m for m in range(1, ay + 1))


KAMU_PAY_ENDEKSLI = kamu_maliyeti_endeksli(0.02)
KAMU_PAY_SABIT = kamu_maliyeti_sabit_nominal()


def finansman_tablosu(p: Prm) -> list[dict]:
    satirlar = []
    for kod in "AC":
        r = tipoloji(kod, p)
        alan = r["sat_konut"] / r["hane"]
        piyasa = alan * p.fiyat
        maliyet_hane = r["maliyet"] / r["hane"]
        arsa_hane = max(0.0, r["akd"]) / r["hane"]
        yuklenici = r["yapim"] * (1.25 / 1.15 - 1) / r["hane"]  # tebliğdeki %10 yüklenici kârı
        modeller = [
            ("Kat karşılığı (piyasa satışı)", piyasa, "Müteahhit getirisi ve arsa sahibi payı fiyatın içinde"),
            ("Arsa payı / yapı grubu (malik + aileler, anahtar teslim yüklenici)", maliyet_hane + yuklenici + arsa_hane,
             "Arsa piyasa değerinden; yükleniciye tebliğdeki %10 kâr; satış gideri yok"),
            ("Kooperatif (1163), arsa piyasa değerinden", maliyet_hane + arsa_hane, "Maliyetine; üyeler inşaat süresince öder"),
            ("Kooperatif + kamu arsası yarı değerle", maliyet_hane + 0.5 * arsa_hane, "TOKİ / belediye arsası, 10 yıl taksit"),
            ("Vakıf / üst hakkı (arsa vakıfta kalır)", maliyet_hane, "Arsa bedeli yok; yeniden satışta fiyat formülü"),
        ]
        for ad, bedel, aciklama in modeller:
            pesin_p = 0.20 * bedel
            t_piyasa = anuite(0.80 * bedel, 0.028, 120)
            t_aile = anuite(0.90 * bedel, (1.02) ** (1 / 12) - 1, 240)
            t_toki = 0.90 * bedel / 240
            satirlar.append(dict(
                tip=kod, konut_brut_m2=round(alan, 1), teslim_modeli=ad, konut_bedeli_tl=round(bedel),
                piyasa_fiyatina_orani=round(bedel / piyasa, 3),
                piyasa_kredisi_aylik_tl=round(t_piyasa), piyasa_kredisi_gelir_payi=round(t_piyasa / MEDYAN_AILE_GELIRI_AY, 3),
                aile_konut_kredisi_aylik_tl=round(t_aile), aile_konut_kredisi_gelir_payi=round(t_aile / MEDYAN_AILE_GELIRI_AY, 3),
                aile_konut_kredisi_2asgari_payi=round(t_aile / IKI_ASGARI, 3),
                aile_kredisi_kamu_maliyeti_tl=round(KAMU_PAY_ENDEKSLI * 0.90 * bedel),
                toki_tipi_sabit_taksit_tl=round(t_toki), toki_tipi_gelir_payi=round(t_toki / MEDYAN_AILE_GELIRI_AY, 3),
                toki_tipi_kamu_maliyeti_tl=round(KAMU_PAY_SABIT * 0.90 * bedel),
                aciklama=aciklama))
        # maliyet kirası
        kira = maliyet_hane * (0.03 + 0.01) / 12
        satirlar.append(dict(
            tip=kod, konut_brut_m2=round(alan, 1), teslim_modeli="Maliyet kirası (vakıf / belediye kiralık konutu)",
            konut_bedeli_tl=round(maliyet_hane), piyasa_fiyatina_orani=round(maliyet_hane / piyasa, 3),
            piyasa_kredisi_aylik_tl="", piyasa_kredisi_gelir_payi="",
            aile_konut_kredisi_aylik_tl=round(kira), aile_konut_kredisi_gelir_payi=round(kira / MEDYAN_AILE_GELIRI_AY, 3),
            aile_konut_kredisi_2asgari_payi=round(kira / IKI_ASGARI, 3),
            aile_kredisi_kamu_maliyeti_tl="",
            toki_tipi_sabit_taksit_tl=round(alan * KIRA_M2), toki_tipi_gelir_payi=round(alan * KIRA_M2 / MEDYAN_AILE_GELIRI_AY, 3),
            toki_tipi_kamu_maliyeti_tl="",
            aciklama="Aylık kira = maliyet × (%3 reel finansman + %1 bakım) / 12 (aile kredisi sütunlarında); "
                     "TOKİ sütunlarında karşılaştırma için piyasa kirası (268,26 TL/m²·ay)"))
    return satirlar


# =============================================================================
# 6. DÖNÜŞÜM SENARYOSU (6306, yerinde, 96 malik)
# =============================================================================
def donusum(p: Prm, n_malik=96, destek_hibe=0.0) -> dict:
    """A: kendini finanse eden en küçük emsal; C: malik başına katkı (hibe sonrası)."""
    e_gerekli = float("inf")
    e = 1.06
    while e <= 6.0:
        r = tipoloji("A", p, e)
        pay = max(0.0, 1 - n_malik / r["hane"])
        if r["bd_gelir"] * pay - r["bd_gider"] >= 0:
            e_gerekli = round(e, 2)
            break
        e += 0.02
    rC = tipoloji("C", p)
    yuklenici = rC["yapim"] * (1.25 / 1.15 - 1)
    katki = (rC["maliyet"] + yuklenici) / rC["hane"] - destek_hibe
    kira_suresi = {k: p.sure_ay[k] for k in "AC"}
    return dict(fiyat=p.fiyat, A_gerekli_emsal=e_gerekli,
                A_gerekli_hane=(tipoloji("A", p, e_gerekli)["hane"] if e_gerekli != float("inf") else ""),
                C_malik_katkisi_tl=round(katki), C_katki_aile_geliri_ay=round(katki / MEDYAN_AILE_GELIRI_AY, 1),
                A_yerinden_edilme_ay=kira_suresi["A"], C_yerinden_edilme_ay=kira_suresi["C"],
                A_kira_yuku_tl=round(100 * KIRA_M2 * kira_suresi["A"]),
                C_kira_yuku_tl=round(100 * KIRA_M2 * kira_suresi["C"]))


# =============================================================================
# 7. ÇIKTILAR
# =============================================================================
def yaz_csv(ad, satirlar):
    yol = CIKTI / ad
    with open(yol, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(satirlar[0].keys()))
        w.writeheader()
        w.writerows(satirlar)
    return yol


def tr_sayi(x, ondalik=0):
    s = f"{x:,.{ondalik}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".").replace("-", "−")


def temel_tablo():
    satirlar = []
    for fiyat_ad, fiyat in [("Türkiye ort.", FIYAT_TR), ("İstanbul ort.", FIYAT_IST), ("Düşük fiyatlı il", FIYAT_DUSUK)]:
        for rejim in ("mevcut", "reform"):
            p = replace(TEMEL, fiyat=fiyat, otopark_rejimi=rejim)
            for kod, emsal in [("A", None), ("A", PLAN_EMSALI_REF), ("B", None), ("C", None)]:
                r = tipoloji(kod, p, emsal)
                satirlar.append(dict(
                    fiyat_senaryosu=fiyat_ad, fiyat_tl_m2=fiyat, otopark_rejimi=rejim,
                    tip=kod + ("" if emsal is None else f" (emsal {tr_sayi(emsal, 1)})"),
                    emsal=round(r["emsal"], 2), hane=r["hane"], insaat_m2=round(r["insaat"]),
                    satilabilir_m2=round(r["sat_konut"] + r["sat_ticari"]), bagimsiz_bolum_brut_m2=round(r["bb_brut"], 1),
                    otopark_ihtiyaci=r["otopark_ihtiyac"], yuzey=r["n_yuzey"], bodrum=r["n_bodrum"], bedel=r["n_bedel"],
                    yapim_mtl=round(r["yapim"] / 1e6, 1), otopark_mtl=round(r["otopark"] / 1e6, 1),
                    peyzaj_altyapi_mtl=round((r["peyzaj"] + r["altyapi"]) / 1e6, 1), yumusak_mtl=round(r["yumusak"] / 1e6, 1),
                    toplam_maliyet_mtl=round(r["maliyet"] / 1e6, 1),
                    maliyet_tl_m2_satilabilir=round(r["maliyet"] / (r["sat_konut"] + r["sat_ticari"])),
                    satis_hasilati_mtl=round(r["gdv"] / 1e6, 1), yapim_suresi_ay=r["sure"],
                    akd_mtl=round(r["akd"] / 1e6, 1), akd_tl_m2_arsa=round(r["akd"] / ARSA_M2),
                    arsa_sahibi_azami_pay=round(r["azami_pay"], 3)))
    return satirlar


def kirilma_tablosu(adim=1_000):
    satirlar = []
    for fiyat in range(30_000, 90_001, adim):
        p = replace(TEMEL, fiyat=float(fiyat))
        satir = dict(fiyat_tl_m2=fiyat)
        for s, ad in [("resmi", "kirilma_emsali_resmi_maliyet_farki"),
                      ("dar", "kirilma_emsali_dar_maliyet_farki"),
                      ("paket", "kirilma_emsali_dar_fark_reform_telafi")]:
            v = kirilma_emsali(p, s)
            satir[ad] = "" if v == float("inf") else v
        satirlar.append(satir)
    return satirlar


PLAN_EMSALI_KOPRU = 2.5  # köprüde blok lehine açık fark olan bir plan hakkı seçildi [V]


def telafi_koprusu(fiyat=FIYAT_IST, plan_emsali=PLAN_EMSALI_KOPRU):
    """Dar maliyet farkı varsayımıyla (A, C'den %10 pahalı) adım adım köprü.

    Otopark reformu genel kuraldır (A'ya da uygulanır, köprüde net etkisi gösterilir);
    harç/ücret indirimi, hızlı onay ve TDR yalnız aile dostu az katlı projeye verilir.
    """
    p0 = replace(TEMEL, fiyat=fiyat, bm={**TEMEL.bm, "A": TEMEL.bm["C"] * 1.10})
    a0, c0 = akd("A", p0, plan_emsali), akd("C", p0)
    adimlar = [dict(adim="Başlangıç farkı (A − C)", tutar_mtl=round((a0 - c0) / 1e6, 1), tur="fark")]
    p1 = replace(p0, otopark_rejimi="reform")
    a1, c1 = akd("A", p1, plan_emsali), akd("C", p1)
    adimlar.append(dict(adim="Otopark reformu (net)", tutar_mtl=round(((a1 - c1) - (a0 - c0)) / 1e6, 1), tur="tesvik"))
    p2 = replace(p1, satici_harc=0.005, yumusak_oran=p1.yumusak_oran - 0.015)
    c2 = akd("C", p2)
    adimlar.append(dict(adim="Harç ve ücret indirimi", tutar_mtl=round(-(c2 - c1) / 1e6, 1), tur="tesvik"))
    p3 = replace(p2, sure_ay={**p2.sure_ay, "C": p2.sure_ay["C"] - 3})
    c3 = akd("C", p3)
    adimlar.append(dict(adim="Hızlı onay (−3 ay)", tutar_mtl=round(-(c3 - c2) / 1e6, 1), tur="tesvik"))
    alici_m2 = a1 / (plan_emsali * ARSA_M2)
    tdr = tdr_degeri(p0, plan_emsali, alici_m2)
    adimlar.append(dict(adim="Emsal transferi (TDR, %60 fiyatla)", tutar_mtl=round(-tdr / 1e6, 1), tur="tesvik"))
    tdr_oncesi = a1 - c3
    kalan = tdr_oncesi - tdr
    adimlar.append(dict(adim="Kalan fark", tutar_mtl=round(kalan / 1e6, 1), tur="fark"))
    devredilen = (plan_emsali - GEO["C"]["insaat"] / ARSA_M2) * ARSA_M2
    gereken_oran = max(0.0, tdr_oncesi) / (devredilen * alici_m2) if devredilen > 0 else float("nan")
    return adimlar, dict(fiyat=fiyat, plan_emsali=plan_emsali, akd_A=a0, akd_C0=c0, akd_C_paket=c3 + tdr, tdr=tdr,
                         tdr_oncesi_fark=tdr_oncesi, devredilen_emsal_m2=devredilen,
                         alici_akd_tl_m2_emsal=alici_m2, gereken_tdr_fiyat_orani=gereken_oran)


def tornado(fiyat=FIYAT_IST, plan_emsali=PLAN_EMSALI_REF):
    """C − A(plan emsali) AKD farkının parametre duyarlılığı (dar maliyet farkı tabanı)."""
    taban = replace(TEMEL, fiyat=fiyat, bm={**TEMEL.bm, "A": TEMEL.bm["C"] * 1.10})

    def fark(p):
        return (akd("C", p) - akd("A", p, plan_emsali)) / 1e6

    f0 = fark(taban)
    testler = [
        ("Satış fiyatı", "−%20", replace(taban, fiyat=fiyat * 0.8), "+%20", replace(taban, fiyat=fiyat * 1.2)),
        ("C fiyat primi (bahçe, avlu)", "−%10", replace(taban, prim={"A": 0, "B": 0, "C": -0.10}),
         "+%10", replace(taban, prim={"A": 0, "B": 0, "C": 0.10})),
        ("A fiyat primi (site, manzara)", "+%10", replace(taban, prim={"A": 0.10, "B": 0, "C": 0}),
         "−%10", replace(taban, prim={"A": -0.10, "B": 0, "C": 0})),
        ("A birim maliyeti", "C ile aynı", replace(taban, bm={**taban.bm, "A": taban.bm["C"]}),
         "resmî IV.A", replace(taban, bm={**taban.bm, "A": 26_450.0})),
        ("C satılabilir oran", "0,88", replace(taban, satilabilir_oran={**taban.satilabilir_oran, "C": 0.88}),
         "0,95", replace(taban, satilabilir_oran={**taban.satilabilir_oran, "C": 0.95})),
        ("Otopark kuralı", "mevcut", taban, "reform (A ve C)", replace(taban, otopark_rejimi="reform")),
        ("Reel iskonto", "%10", replace(taban, iskonto_reel=0.10), "%20", replace(taban, iskonto_reel=0.20)),
        ("C yapım süresi", "20 ay", replace(taban, sure_ay={**taban.sure_ay, "C": 20}),
         "12 ay", replace(taban, sure_ay={**taban.sure_ay, "C": 12})),
    ]
    satirlar = []
    for ad, e1, p1, e2, p2 in testler:
        satirlar.append(dict(parametre=ad, taban_C_eksi_A_mtl=round(f0, 1),
                             deger_1=e1, C_eksi_A_1_mtl=round(fark(p1), 1),
                             deger_2=e2, C_eksi_A_2_mtl=round(fark(p2), 1)))
    return satirlar


# =============================================================================
# 8. GRAFİKLER
# =============================================================================
def stil(ax):
    ax.set_facecolor(ZEMIN)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    for k in ("left", "bottom"):
        ax.spines[k].set_color("#c9c9c4")
        ax.spines[k].set_linewidth(0.8)
    ax.tick_params(colors=IKINCIL, labelsize=9, length=0, pad=6)
    ax.grid(axis="y", color=IZGARA, linewidth=0.8)
    ax.set_axisbelow(True)


def grafik_kirilma(tablo):
    x = [s["fiyat_tl_m2"] for s in tablo]
    ust = 4.0
    seriler = [
        ("kirilma_emsali_resmi_maliyet_farki", MAVI, "Mevcut kurallar · resmî maliyet farkı (IV.A / III.B)"),
        ("kirilma_emsali_dar_maliyet_farki", TURUNCU, "Mevcut kurallar · dar maliyet farkı (blok %10 pahalı)"),
        ("kirilma_emsali_dar_fark_reform_telafi", AQUA, "Dar fark + otopark reformu + harç indirimi + hızlı onay + TDR"),
    ]
    fig, ax = plt.subplots(figsize=(10.5, 6.4), dpi=150)
    fig.patch.set_facecolor(ZEMIN)
    stil(ax)
    ax.axhspan(1.5, 2.5, color="#ecebe6", zorder=0)
    ax.text(31_000, 2.45, "Konut alanlarında yaygın plan emsali aralığı (1,5–2,5)", fontsize=8.5,
            color=SOLUK, va="top")
    ax.axhline(GEO["C"]["insaat"] / ARSA_M2, color="#9aa0a6", lw=1, zorder=1)
    ax.text(31_000, 1.33, "C'nin emsali 1,30", fontsize=8.5, color=SOLUK, ha="left", va="bottom")
    for anahtar, renk, etiket in seriler:
        nokta = [(xi, s[anahtar]) for xi, s in zip(x, tablo) if s[anahtar] != "" and s[anahtar] <= ust]
        xs, ys = zip(*nokta)
        ax.plot(xs, ys, color=renk, lw=2.2, solid_capstyle="round", solid_joinstyle="round", zorder=3, label=etiket)
        ax.scatter([xs[0]], [ys[0]], s=46, color=renk, edgecolor=ZEMIN, linewidth=2, zorder=4)
        ax.text(xs[0] + 700, ys[0] + 0.03, tr_sayi(xs[0]) + " TL/m²", fontsize=8.5, color=IKINCIL, va="bottom")
    ax.text(31_000, 4.17,
            "Noktadan önceki fiyatlarda blok, 4,0'a kadar hiçbir emsalde az katlıyı geçemiyor.",
            fontsize=8.5, color=SOLUK, va="top")
    # İstanbul ve Türkiye ortalaması işaretleri
    for xf, ad in [(FIYAT_TR, "Türkiye ort.\n42.488"), (FIYAT_IST, "İstanbul ort.\n63.788")]:
        ax.axvline(xf, color="#b8b8b2", lw=0.8, ls=(0, (2, 3)), zorder=1)
        ax.text(xf + 600, 0.93, ad, fontsize=8.5, color=IKINCIL, va="bottom")
    ax.set_xlim(30_000, 90_000)
    ax.set_ylim(0.9, 4.25)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: tr_sayi(v)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: tr_sayi(v, 1)))
    ax.set_xlabel("Konut satış fiyatı (TL/m², 2026)", fontsize=10, color=IKINCIL)
    ax.set_ylabel("Kırılma emsali (12 katlı blok)", fontsize=10, color=IKINCIL)
    fig.text(0.07, 0.955, "Az katlı seçenek hangi koşulda ayakta kalıyor?", fontsize=15, fontweight="bold", color=MUREKKEP)
    fig.text(0.07, 0.915,
             "Çizginin altındaki plan emsallerinde Z+2 avlulu sıra ev (C) arsa sahibine 12 katlı bloktan (A) daha fazla değer bırakır.\n"
             "1 ha, reel 2026 TL, müteahhit reel getirisi %15. Kaynak: TR TAMİRAT M6 modeli; maliyet: ÇŞİDB 2026 yapı yaklaşık birim maliyetleri.",
             fontsize=9, color=IKINCIL, va="top")
    tutamaclar = [Line2D([0], [0], color=r, lw=2.2) for _, r, _ in seriler]
    ax.legend(tutamaclar, [e for _, _, e in seriler], loc="lower right", bbox_to_anchor=(1.0, 0.11), frameon=False, fontsize=8.8,
              labelcolor=MUREKKEP)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.83, bottom=0.11)
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"grafik1_kirilma_emsali.{uz}", facecolor=ZEMIN)
    plt.close(fig)


def grafik_kopru(adimlar, ozet):
    fig, ax = plt.subplots(figsize=(10.5, 5.6), dpi=150)
    fig.patch.set_facecolor(ZEMIN)
    stil(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=IZGARA, linewidth=0.8)
    etiketler = [a["adim"] for a in adimlar]
    y = list(range(len(adimlar)))[::-1]
    kum = 0.0
    for yi, a in zip(y, adimlar):
        v = a["tutar_mtl"]
        if a["tur"] == "fark":
            bas, uz, renk = 0.0, v, NOTR
            kum = v if a["adim"].startswith("Başlangıç") else kum
        else:
            bas, uz, renk = kum, v, MAVI
            kum = kum + v
        ax.barh(yi, uz, left=bas, height=0.52, color=renk, edgecolor=ZEMIN, linewidth=2, zorder=3)
        uc = bas + uz
        metin = tr_sayi(v, 1)
        if a["tur"] != "fark":
            metin = "−" + tr_sayi(abs(v), 1)
        sag = max(bas, uc)
        sol = min(bas, uc)
        if a["tur"] == "fark" and v < 0:
            ax.text(sol - 3, yi, metin + " mn TL", va="center", ha="right", fontsize=9.5, color=MUREKKEP)
        else:
            ax.text(sag + 3, yi, metin + " mn TL", va="center", ha="left", fontsize=9.5, color=MUREKKEP)
    ax.axvline(0, color="#9aa0a6", lw=1, zorder=2)
    ax.set_yticks(y)
    ax.set_yticklabels(etiketler, fontsize=10, color=MUREKKEP)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: tr_sayi(v)))
    ax.set_xlabel("Arsa kalıntı değeri farkı, milyon TL / ha (artı: blok önde)", fontsize=10, color=IKINCIL)
    xs = [a["tutar_mtl"] for a in adimlar]
    ax.set_xlim(min(0, min(xs), adimlar[-1]["tutar_mtl"]) - 45, max(xs) + 60)
    fig.text(0.04, 0.95, "Telafi köprüsü: blok ile az katlı arasındaki farkı hangi araç kapatıyor?", fontsize=14.5,
             fontweight="bold", color=MUREKKEP)
    fig.text(0.04, 0.905,
             f"İstanbul ort. fiyatı ({tr_sayi(ozet['fiyat'])} TL/m²), mevcut plan emsali {tr_sayi(ozet['plan_emsali'], 1)}, "
             "blok maliyeti az katlıdan %10 fazla; 1 ha, reel 2026 TL.\n"
             "Negatif kalan fark: Z+2 avlulu sıra ev (C) arsa sahibine daha fazla değer bırakır.\n"
             f"TDR'nin alıcı bölge arsa değerinin %{tr_sayi(ozet['gereken_tdr_fiyat_orani'] * 100, 1)}'i "
             "kadar bir fiyatla satılması farkı kapatmaya yetiyor. "
             "Kaynak: TR TAMİRAT M6 modeli.",
             fontsize=9, color=IKINCIL, va="top", linespacing=1.5)
    ax.legend([Patch(color=NOTR), Patch(color=MAVI)], ["Fark (A − C)", "Az katlıya teşvik / telafi"],
              loc="lower right", frameon=False, fontsize=9, labelcolor=MUREKKEP)
    fig.subplots_adjust(left=0.26, right=0.96, top=0.77, bottom=0.12)
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"grafik2_telafi_koprusu.{uz}", facecolor=ZEMIN)
    plt.close(fig)


# =============================================================================
# 9. ANA AKIŞ
# =============================================================================
def main():
    yaz_csv("varsayimlar.csv", [dict(anahtar=a, deger=d, birim=b, kaynak=k, etiket=e)
                                for a, d, b, k, e in VARSAYIM_SATIRLARI])
    temel = temel_tablo()
    yaz_csv("tipoloji_temel_sonuclar.csv", temel)
    kir = kirilma_tablosu()
    yaz_csv("duyarlilik_kirilma_emsali.csv", kir)
    adimlar, ozet = telafi_koprusu()
    yaz_csv("telafi_koprusu.csv", adimlar + [
        dict(adim="Bilgi: gereken asgari TDR fiyat oranı (alıcı bölge emsal m² değerine göre)",
             tutar_mtl=round(ozet["gereken_tdr_fiyat_orani"], 3), tur="bilgi"),
        dict(adim="Bilgi: devredilen emsal (m²)", tutar_mtl=round(ozet["devredilen_emsal_m2"]), tur="bilgi"),
        dict(adim="Bilgi: alıcı bölgede emsal m² başına AKD (TL)", tutar_mtl=round(ozet["alici_akd_tl_m2_emsal"]), tur="bilgi")])
    torn = tornado()
    yaz_csv("duyarlilik_tornado.csv", torn)
    fin = finansman_tablosu(replace(TEMEL, fiyat=FIYAT_TR))
    yaz_csv("finansman_alternatifleri.csv", fin)
    don = []
    for ad, f in [("Türkiye ort.", FIYAT_TR), ("İstanbul ort.", FIYAT_IST), ("Düşük fiyatlı il", FIYAT_DUSUK)]:
        for hibe_ad, hibe in [("destek yok", 0.0), ("Yarısı Bizden hibesi 875 bin", 875_000.0)]:
            d = donusum(replace(TEMEL, fiyat=f), destek_hibe=hibe)
            d = {"fiyat_senaryosu": ad, "destek": hibe_ad, **d}
            d["A_gerekli_emsal"] = "" if d["A_gerekli_emsal"] == float("inf") else d["A_gerekli_emsal"]
            don.append(d)
    yaz_csv("donusum_senaryosu_6306.csv", don)
    kamu = [
        dict(arac="Aile konut kredisi (TÜFE endeksli, reel %2, 240 ay)", kamu_maliyeti_kredinin_payi=round(kamu_maliyeti_endeksli(0.02), 3)),
        dict(arac="Aile konut kredisi (reel %0, 240 ay)", kamu_maliyeti_kredinin_payi=round(kamu_maliyeti_endeksli(0.0), 3)),
        dict(arac="TOKİ tipi sabit nominal taksit (240 ay, enflasyon %25)", kamu_maliyeti_kredinin_payi=round(kamu_maliyeti_sabit_nominal(), 3)),
    ]
    yaz_csv("kamu_maliyeti_kredi.csv", kamu)

    grafik_kirilma(kir)
    grafik_kopru(adimlar, ozet)

    # --- konsol özeti --------------------------------------------------------
    print(f"Medyan 4 kişilik aile geliri (2026 tahmini): {tr_sayi(MEDYAN_AILE_GELIRI_AY)} TL/ay")
    print("\nTemel sonuçlar (mevcut otopark rejimi):")
    for s in temel:
        if s["otopark_rejimi"] == "mevcut":
            print(f"  {s['fiyat_senaryosu']:<17} {s['tip']:<16} hane {s['hane']:>4}  maliyet {s['toplam_maliyet_mtl']:>7} mn"
                  f"  hasılat {s['satis_hasilati_mtl']:>7} mn  AKD {s['akd_mtl']:>7} mn  pay {s['arsa_sahibi_azami_pay']:.2f}"
                  f"  otopark {s['otopark_ihtiyaci']} (b{s['bodrum']}/bd{s['bedel']}) {s['otopark_mtl']} mn")
    print("\nReform otopark:")
    for s in temel:
        if s["otopark_rejimi"] == "reform":
            print(f"  {s['fiyat_senaryosu']:<17} {s['tip']} AKD {s['akd_mtl']} mn  otopark {s['otopark_mtl']} mn")
    print("\nKırılma emsali (seçili fiyatlar):")
    for s in kir:
        if s["fiyat_tl_m2"] in (30_000, 40_000, 42_000, 50_000, 60_000, 64_000, 70_000, 80_000, 90_000):
            print("  ", s)
    print("\nTelafi köprüsü:", [(a["adim"], a["tutar_mtl"]) for a in adimlar])
    print("  özet:", {k: (round(v / 1e6, 1) if isinstance(v, float) and v > 1e5 else v) for k, v in ozet.items()})
    print("\nTornado:")
    for t in torn:
        print("  ", t)
    print("\nFinansman (Türkiye ort.):")
    for f in fin:
        print("  ", f["tip"], f["teslim_modeli"][:45], f["konut_bedeli_tl"], f["piyasa_fiyatina_orani"],
              f["piyasa_kredisi_gelir_payi"], f["aile_konut_kredisi_aylik_tl"], f["aile_konut_kredisi_gelir_payi"],
              f["toki_tipi_gelir_payi"])
    print("\nDönüşüm:")
    for d in don:
        print("  ", d)
    print("\nKamu maliyeti:", kamu)


if __name__ == "__main__":
    main()
