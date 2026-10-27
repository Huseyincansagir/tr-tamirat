"""
TR TAMİRAT — İP7 Zihinsel simülasyonlar, sürüm 0.1 (26 Ekim 2026)
==================================================================
Persona "bir gün" simülasyonu, kriz senaryoları ve sağlık/iyi oluş yansıması.

Üç ortam karşılaştırılıyor:
  A) Megakent kapalı site: 12 katlı bloklar, çeperde, araca bağımlı
  B) Eski yap-sat apartman mahallesi: 5-6 kat, karma kullanım, yeşilsiz
  C) Model mahalle: Z+2 / Z+3, avlulu, 15 dakikalık erişim
     (07_TASARIM_CIZIM/tasarim_parametreleri.md, Bölüm 9)

Simülasyon kehanet değil, düşünme aracıdır. Bütün parametreler aşağıdaki
VARSAYIMLAR listesinde değer, aralık ve kaynakla durur ve
06_SIMULASYON/varsayimlar.csv dosyasına yazılır. Kaynağı olmayan her değer
açıkça "[V] varsayım" diye işaretlidir.

Belirsizlik: her parametre üçgen dağılımla (düşük, temel, yüksek) örneklenir
(Sallis aralığı düzgün dağılım). Monte Carlo, sabit tohumla tekrarlanabilir.

Çalıştırma :  python persona_simulasyonu.py     (sonunda yasam_dongusu.py'yi de çalıştırır)
Çıktılar   :  ../varsayimlar.csv
              ../sonuclar/*.csv
              ../grafikler/persona_gostergeler.png|svg, saglik_iyi_olus.png|svg,
              kriz_dayaniklilik.png|svg  (yaşam döngüsü grafiği yasam_dongusu.py'de)
Bağımlılık :  numpy, pandas, matplotlib
"""

from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parents[1]          # 06_SIMULASYON
SONUC = KOK / "sonuclar"
GRAFIK = KOK / "grafikler"
SONUC.mkdir(parents=True, exist_ok=True)
GRAFIK.mkdir(parents=True, exist_ok=True)

TOHUM = 2026
N_MC = 2000
ORTAMLAR = ["A", "B", "C"]
ORTAM_AD = {
    "A": "A · Kapalı site",
    "B": "B · Yap-sat apartman",
    "C": "C · Model mahalle",
}

# =============================================================================
# 1. KAYNAK KISALTMALARI
# =============================================================================
K = {
    "AU": "ÇSGB açıklaması: 2026 net asgari ücret 28.075,50 TL (KPMG ve EY özetleri; kpmgvergi.com, ey.com/tr_tr/insights/tax/2026-asgari-ucret)",
    "YAKIT": "İstanbul Avrupa Yakası benzin pompa fiyatı 79,60 TL/L, 20.10.2026 (hisse.net haberi); Ekim içinde 79,4-83,8 TL",
    "IBB": "İBB 20.07.2026 tarifesi: tam bilet 46,20 TL, Mavi Kart aylık 3.628 TL, öğrenci abonman 653 TL (haberturk.com, gzt.com haberleri)",
    "KIRA": "Emlakjet-Endeksa Ağustos 2026: İstanbul ortalama kira 45.510 TL (cnbce.com); Endeksa 2026 ilçe m² kiraları Esenyurt 228 – Kadıköy 651 TL (internethaber.com)",
    "FIYAT": "Emlakjet-Endeksa Ağustos 2026: İstanbul ortalama konut fiyatı 7.359.550 TL; Türkiye 42.488 TL/m², ortalama 5.311.000 TL (foreks.com) → ortalama konut ≈125 m², İstanbul ≈58.900 TL/m² [H]",
    "YAPIM": "ÇŞİDB 2026 Yapı Yaklaşık Birim Maliyetleri Tebliği, RG 03.02.2026/33157 (hukukihaber.net metni)",
    "TOMTOM": "TomTom Traffic Index 2025: İstanbul'da 10 km = 22 dk 54 sn → 26,2 km/sa (03_VERI/turkiye_temel_gostergeler.md)",
    "ZKA": "TÜİK Zaman Kullanım 2025: günlük ulaşım 61 dk, spor 12 dk, kadın bakım 4 sa 3 dk (03_VERI/turkiye_temel_gostergeler.md)",
    "CSV": "07_TASARIM_CIZIM/ayni_yogunluk_uc_bicim_metrikler.csv",
    "TAS": "07_TASARIM_CIZIM/tasarim_parametreleri.md",
    "MPYY": "MPYY Md. 12 yürüme mesafeleri (tasarim_parametreleri.md, Bölüm 6.1)",
    "BKNA": "TÜİK BKNA 2021: hanelerin %27,4'ü 5-6 katlı binada; 3+ katlı binadaki hanelerin %53,6'sı asansörsüz (03_VERI/turkiye_temel_gostergeler.md)",
    "SALLIS": "Sallis ve ark. 2016, Lancet 387:2207 — en ve en az aktivite dostu mahalle farkı 68-89 dk/hafta (02_LITERATUR/literatur_haritasi.md)",
    "FRANK": "Frank ve ark. 2004, Am J Prev Med 27:87 — arabada her ek saat/gün obezite +%6; her ek km yürüme/gün −%4,8 (kesitsel)",
    "SF": "Stutzer & Frey 2008, Scand J Econ 110:339 — tek yön 22 dk için tam telafi aylık gelirin %35,4'ü; karşı kanıt Hirte & Illmann 2018",
    "PUTNAM": "Putnam 2000 — her +10 dk işe gidiş ≈ %10 daha az topluluk katılımı (ikincil aktarım)",
    "WHITE": "White ve ark. 2019, Sci Rep 9:7730 — haftada ≥120 dk doğa teması: iyi sağlık OR 1,59 (1,31-1,92) (kesitsel)",
    "ROJAS": "Rojas-Rueda ve ark. 2019, Lancet Planet Health 3:e469 — 500 m'de her 0,1 NDVI: ölüm HR 0,96 (0,94-0,97)",
    "HE": "He ve ark. 2015, JAMA 314:1142 (küme RKÇ) — günde ek 40 dk dış mekân: 3 yıllık miyopi %39,5 → %30,4 (fark −9,1; −14,1/−4,1)",
    "XIONG": "Xiong ve ark. 2017, Acta Ophthalmol 95:551 — doz-yanıt doğrusal değil",
    "HOLT": "Holt-Lunstad ve ark. 2015, Perspect Psychol Sci 10:227 — sosyal izolasyon ölüm OR 1,29",
    "CP": "Compton & Pollak 2014, J Urban Econ 79:72 — anneye/kayınvalideye yakın oturmak istihdamı 4-10 puan artırıyor",
    "KAPTIJN": "Kaptijn ve ark. 2010 (büyükanne desteği → ek çocuk olasılığı, yön); Tanskanen ve ark. 2014 (etki soy hattına göre zıt olabilir)",
    "FAZ2": "09_RAPORLAR/03_ilce_paneli_il_ici.md — eğitim sabitken 3 m (≈1 kat) başına −0,029 çocuk; dürüst aralık −0,03 / −0,14; 12 m üstünde ek ayrışma yok",
    "GIFFORD": "Gifford 2007; Evans 2003 — yüksek katta çocuk gözetimi ve dış mekân kullanımı zayıf (orta-zayıf kanıt)",
    "PSI": "Shaw ve ark. 2015 (PSI) — çocuğun bağımsız hareketi; trafik ana kısıt",
    "TAYA": "TAYA 2016: hane olarak komşu ziyareti TR %45,2, İstanbul %37,2 (03_VERI/turkiye_temel_gostergeler.md)",
    "DEPREM": "6 Şubat 2023: 518.009 yıkık/ağır hasarlı konut, 53.537 can kaybı (ikincil aktarım; 03_VERI/turkiye_temel_gostergeler.md)",
    "TUIK_HANE": "TÜİK İstatistiklerle Aile 2025: ortalama hane 3,08 kişi",
    "OTOMOBIL": "1000 kişiye 210 otomobil (Eylül 2026) × 3,08 kişi/hane ≈ 0,65 otomobil/hane [H]",
}


# =============================================================================
# 2. VARSAYIM TABLOSU (tek doğruluk kaynağı)
# =============================================================================
# Her satır: kod, açıklama, birim, işaret, kaynak/gerekçe, kullanım, ortam değerleri.
# Ortam değeri: sayı (sabit) ya da (temel, düşük, yüksek). "ortak" bütün ortamlar.
VARSAYIMLAR: list[dict] = []
PARAM: dict[tuple[str, str], tuple[float, float, float, str]] = {}


def _p(kod, aciklama, birim, isaret, kaynak, kullanim, dagilim="üçgen", **ortamlar):
    for ortam, deger in ortamlar.items():
        if isinstance(deger, (tuple, list)):
            temel, dusuk, yuksek = deger
        else:
            temel = dusuk = yuksek = deger
        if not (dusuk <= temel <= yuksek):
            raise ValueError(f"{kod}/{ortam}: düşük ≤ temel ≤ yüksek değil")
        PARAM[(kod, ortam)] = (float(temel), float(dusuk), float(yuksek), dagilim)
        VARSAYIMLAR.append(dict(
            parametre_kodu=kod, aciklama=aciklama, birim=birim, ortam=ortam,
            temel=temel, dusuk=dusuk, yuksek=yuksek,
            dagilim="sabit" if dusuk == yuksek else dagilim,
            isaret=isaret, kaynak_gerekce=kaynak, kullanildigi_yer=kullanim))


V = "[V]"   # varsayım
D = "[D]"   # doğrulanmış kaynak (literatür haritasında 'dogrulandi = evet' ya da proje verisi)
I = "[İ]"   # ikincil aktarım (basın, kurum özeti)
H = "[H]"   # bu çalışmada hesaplandı

# --- 2.1 Gelir, fiyat ve ücretler (2026) ------------------------------------
_p("AU_NET", "Net asgari ücret (2026)", "TL/ay", I, K["AU"], "Hane gelirleri asgari ücret katı olarak", ortak=28075.5)
_p("ISGUNU_AY", "Aylık iş günü", "gün/ay", V, "Varsayım: haftada 5 gün", "Aylık ulaşım maliyeti", ortak=22)
_p("ESNAF_GUN_AY", "Esnafın aylık çalışma günü", "gün/ay", V, "Varsayım: haftada 6 gün", "Esnaf ulaşım maliyeti", ortak=26)
_p("OFIS_GUN_AY_SELIN", "Engelli personanın aylık ofis günü", "gün/ay", V, "Varsayım: haftada 3 gün ofis, 2 gün uzaktan", "P6 ulaşım maliyeti", ortak=13)
_p("YAKIT_TL_L", "Benzin fiyatı", "TL/L", I, K["YAKIT"] + "; aralık varsayım", "Araç değişken maliyeti", ortak=(79.6, 75, 90))
_p("YAKIT_L_100KM", "Ortalama yakıt tüketimi (kent içi)", "L/100 km", V, "Varsayım: binek otomobil, kent içi trafik", "Araç değişken maliyeti", ortak=(7.0, 6.0, 8.5))
_p("ARAC_ASINMA_TL_KM", "Lastik, bakım, aşınma", "TL/km", V, "Varsayım", "Araç değişken maliyeti", ortak=(1.5, 1.0, 2.5))
_p("ARAC_SABIT_TL_AY", "Araç başına sabit maliyet (kasko, trafik sigortası, MTV, bakım, değer kaybı)", "TL/ay", V,
   "Varsayım: ≈1,5 milyon TL'lik aracın yıllık %4-6 değer kaybı + sigorta ve vergiler", "Aylık ulaşım maliyeti", ortak=(12000, 7000, 18000))
_p("OTOPARK_EV_TL_AY", "Konutta otopark bedeli", "TL/ay", V,
   "A: aidata dahil kapalı otopark; B: sokak ya da ücretli otopark; C: bölgesel otopark, fiyatı konuttan ayrı (" + K["TAS"] + ", Bölüm 7)",
   "Aylık ulaşım maliyeti", A=0, B=(750, 0, 2000), C=(1500, 800, 3000))
_p("MERKEZ_OTOPARK_TL_GUN", "İş merkezinde günlük otopark", "TL/gün", V, "Varsayım; alt uç 0 = işyeri otoparkı", "Araçla işe gidenlerin maliyeti", ortak=(150, 0, 350))
_p("MAVI_KART_TL_AY", "Aylık tam abonman (Mavi Kart)", "TL/ay", I, K["IBB"], "Toplu taşıma maliyeti", ortak=3628)
_p("OGRENCI_ABONMAN_TL_AY", "Öğrenci aylık abonman", "TL/ay", I, K["IBB"], "Toplu taşıma maliyeti", ortak=653)
_p("TEK_BINIS_TL", "Tam bilet (tek biniş)", "TL", I, K["IBB"], "Seyrek toplu taşıma kullanımı", ortak=46.2)
_p("OKUL_SERVISI_TL_AY", "Okul servisi", "TL/ay", V, "Varsayım", "A'da çocuk ulaşımı", ortak=(4000, 3000, 6000))
_p("ERISILEBILIR_TAKSI_TL", "Erişilebilir taksi, tek yolculuk", "TL", V, "Varsayım", "B'de tekerlekli sandalye kullanıcısının işe gidişi", ortak=(350, 250, 500))
_p("PAYLASIMLI_ARAC_TL_AY", "Araçsız hanede paylaşımlı araç/taksi", "TL/ay", V, "Varsayım: ayda birkaç büyük alışveriş ve ziyaret", "C'de araçsız hane", ortak=(1500, 800, 3000))
_p("HAFTASONU_ARAC_KM_AY", "Hafta sonu ve iş dışı araç kullanımı", "km/ay", V,
   "Varsayım: A'da AVM, park ve akraba ziyaretleri araçla; C'de çoğu ihtiyaç yürüme mesafesinde", "Araç değişken maliyeti",
   A=(400, 250, 600), B=(200, 100, 300), C=(150, 80, 250))
_p("KIRA_M2", "Piyasa kirası (kira eşdeğeri)", "TL/m²·ay", I + V,
   K["KIRA"] + ". Ortam farkları varsayım: A çeper indirimi + site primi; B eski stok ama iç-orta halka; C yeni yapı ve yeşil primi",
   "Aylık konut maliyeti", A=(340, 250, 450), B=(380, 300, 480), C=(420, 340, 550))
_p("AIDAT_M2", "Aidat / ortak alan bakımı", "TL/m²·ay", V,
   "Varsayım: A havuz, güvenlik, peyzaj, asansör, kapalı otopark; B apartman aidatı; C avlu ve ortak bahçe bakımı",
   "Aylık konut maliyeti", A=(35, 25, 60), B=(6, 3, 12), C=(12, 8, 20))
_p("KONUT_FIYAT_M2", "Konut satış fiyatı", "TL/m²", I + H + V, K["FIYAT"] + ". Ortam farkları varsayım",
   "Yaşam döngüsü: ev edinme", A=(52000, 45000, 62000), B=(55000, 45000, 65000), C=(60000, 50000, 75000))
_p("YAPIM_III_A", "Resmî yaklaşık birim maliyet: apartman tipi konut, üç kata kadar (III-A)", "TL/m²", I, K["YAPIM"],
   "Rapor: yapım maliyeti karşılaştırması (hesaplarda kullanılmadı)", ortak=19800)
_p("YAPIM_III_B", "Resmî yaklaşık birim maliyet: konut, üç kat üzeri ve ≤21,5 m; müstakil/ikiz <200 m² (III-B)", "TL/m²", I, K["YAPIM"],
   "Rapor: yapım maliyeti karşılaştırması (hesaplarda kullanılmadı)", ortak=21050)
_p("YAPIM_IV_A", "Resmî yaklaşık birim maliyet: konut, 30,5-51,5 m (IV-A)", "TL/m²", I, K["YAPIM"],
   "Rapor: yapım maliyeti karşılaştırması (hesaplarda kullanılmadı)", ortak=26450)

# --- 2.2 Ulaşım hızları ve süreleri ------------------------------------------
_p("ARAC_HIZ_MERKEZ", "Merkeze araçla ortalama hız (sıkışık)", "km/sa", I + V, K["TOMTOM"] + "; aralık varsayım", "Araçla işe gidiş", ortak=(26.2, 20, 32))
_p("ARAC_HIZ_YEREL", "Yerel araç yolculuğu hızı", "km/sa", V, "Varsayım", "Kısa araç yolculukları", ortak=(25, 18, 30))
_p("TOPLU_HIZ", "Toplu taşımada araç içi ortalama hız (aktarmalı otobüs + raylı)", "km/sa", V,
   "Varsayım; A'nın dezavantajı hızda değil durağa erişim ve beklemede (MES_DURAK, BEKLEME_DK)", "Toplu taşıma süresi", A=(22, 16, 28), B=(22, 16, 28), C=(22, 16, 28))
_p("RAYLI_HIZ_CEPER", "C çeperde kurulursa raylı sistem hızı", "km/sa", V, "Varsayım (yalnız C-çeper duyarlılığı)", "C-çeper duyarlılığı", ortak=(32, 26, 38))
_p("BEKLEME_DK", "Durakta ortalama bekleme (sefer aralığının yarısı)", "dk", V, "Varsayım", "Toplu taşıma süresi",
   A=(10, 6, 15), B=(5, 3, 8), C=(5, 3, 8))
_p("AKTARMA_DK", "Aktarma cezası (5 km üstü yolculuk)", "dk", V, "Varsayım", "Toplu taşıma süresi", ortak=(4, 2, 8))
_p("VARIS_YURUME_DK", "Varış ucunda yürüme", "dk", V, "Varsayım", "Toplu taşıma ve araç", ortak=(5, 3, 8))
_p("ARAC_ERISIM_DK", "Evden araca erişim (tek yön)", "dk", V,
   "A: kapalı otoparkta araca yürüme (asansör dikey dolaşımda sayılır); B: sokakta park; C: bölgesel otopark 300-400 m (" + K["TAS"] + ", Bölüm 9.5)",
   "Araç yolculuğu", A=(1.5, 1, 3), B=(1.5, 1, 3), C=(5, 4, 7))
_p("PARK_ARAMA_MERKEZ_DK", "Merkezde park yeri arama", "dk", V, "Varsayım", "Araçla işe gidiş", ortak=(8, 3, 15))
_p("PARK_ARAMA_YEREL_DK", "Yerel varışta park etme", "dk", V, "Varsayım", "Kısa araç yolculukları", ortak=(3, 1, 6))
_p("PARK_ARAMA_EV_DK", "Eve dönüşte park yeri arama", "dk", V, "Varsayım: B'de sokak parkı", "Araç yolculuğu",
   A=0, B=(6, 2, 12), C=0)
_p("SERVIS_DK", "Okul servisinde geçen süre (tek yön)", "dk", V, "Varsayım: servis güzergâhı birçok siteyi dolaşır", "A'da çocuğun okula gidişi", A=(25, 15, 40))
_p("SERVIS_BEKLEME_DK", "Servis noktasında bekleme", "dk", V, "Varsayım", "A'da çocuğun okula gidişi", ortak=(5, 3, 10))

# --- 2.3 Yürüme ve dikey dolaşım --------------------------------------------
_p("HIZ_YETISKIN", "Yürüme hızı, yetişkin", "m/dk", H, "4,8 km/sa; " + K["TAS"] + " (4-5 km/sa ile 15 dk'da 1,0-1,25 km)", "Bütün yürüme süreleri", ortak=(80, 70, 90))
_p("HIZ_YASLI_SAGLIKLI", "Yürüme hızı, sağlıklı yaşlı", "m/dk", V, "Varsayım", "P4", ortak=(65, 55, 75))
_p("HIZ_YASLI_KISITLI", "Yürüme hızı, diz sorunu olan yaşlı", "m/dk", V, "Varsayım", "P5", ortak=(45, 35, 55))
_p("HIZ_COCUK", "Yürüme hızı, 8 yaş çocuk", "m/dk", V, "Varsayım", "P3c", ortak=(65, 55, 75))
_p("HIZ_TEKERLEKLI", "Tekerlekli sandalye hızı, erişilebilir güzergâhta", "m/dk", V, "Varsayım", "P6", ortak=(60, 50, 70))
_p("MERDIVEN_DK_KAT_YETISKIN", "Merdivende kat başına süre, yetişkin", "dk/kat", V, "Varsayım", "Dikey dolaşım, tahliye", ortak=(0.25, 0.2, 0.35))
_p("MERDIVEN_DK_KAT_YASLI", "Merdivende kat başına süre, yaşlı", "dk/kat", V, "Varsayım", "Dikey dolaşım, tahliye", ortak=(1.0, 0.7, 1.5))
_p("ASANSOR_DK", "Asansör bekleme + yolculuk (tek yön)", "dk", V, "Varsayım; A'da 48 daireli kule; C'de yalnız T3 (4 kat) ve T4", "Dikey dolaşım",
   A=(2.5, 1.5, 4.0), C=(1.0, 0.5, 1.5))
_p("KAT_SAYISI", "Bina kat adedi", "kat", H + V, "A ve C: " + K["CSV"] + "; B: kullanıcı tanımı (5-6 kat), " + K["BKNA"],
   "Deprem, gölge, dikey dolaşım", A=12, B=(5.5, 5, 6), C=3)
_p("BINA_BASINA_DAIRE", "Bir yapıyı paylaşan daire (= dikey dolaşımı paylaşan hane ≈ malik sayısı)", "daire", H + V,
   "A: 96 hane/ha, 12 kat, 2 kule (" + K["CSV"] + "); B: 5,5 kat × 2 daire [V]; C: tipoloji payları T1-T4, T3'te bina başına ≈12 daire [H, " + K["TAS"] + " 9.4]",
   "Deprem, salgın", A=48, B=(11, 10, 12), C=(7, 5, 10))

# --- 2.4 Ağ mesafeleri ---------------------------------------------------------
_mes = "Varsayım (ağ mesafesi); C: " + K["TAS"] + " Bölüm 9.5 hedefleri"
_p("MES_BAKKAL", "Bakkal / fırın", "m", V, _mes + "; A: site içinde dükkân yok (CSV: zemin kat ticaret cephesi 0 m)", "Günlük alışveriş",
   A=(900, 500, 1500), B=(120, 60, 250), C=(200, 150, 300))
_p("MES_MARKET", "Haftalık pazar / market", "m", V, _mes + "; A: araçla AVM", "Haftalık alışveriş",
   A=(3000, 2000, 5000), B=(500, 300, 900), C=(450, 300, 600))
_p("MES_MESCIT", "En yakın mescit / cami", "m", D + V, "C: " + K["MPYY"] + " (mescit ≈150 m) [D]; A, B varsayım", "İbadete erişim",
   A=(700, 400, 1200), B=(250, 150, 400), C=(150, 100, 200))
_p("MES_ILKOKUL", "İlkokul", "m", D + V, "C: MPYY ≈500 m, tasarım hedefi 400 m [D]; A, B varsayım", "Çocuğun okul yolu",
   A=(1400, 800, 2500), B=(600, 400, 900), C=(400, 300, 500))
_p("MES_ANAOKULU", "Anaokulu / kreş", "m", V, _mes + " (kreş 300-400 m)", "Ebeveynin bakım yolculuğu",
   A=(1500, 800, 2500), B=(500, 300, 800), C=(300, 200, 400))
_p("MES_SERVIS_NOKTASI", "Okul servisinin alındığı site kapısı", "m", V, "Varsayım", "A'da ebeveynin eşliği", A=(150, 80, 300))
_p("MES_YESIL", "En yakın kullanılabilir yeşil (≥0,5 ha ya da site bahçesi)", "m", V,
   "A: site içi ortak alan, kişi başı 18,5 m² (" + K["CSV"] + "); B: yeşilsiz doku; C: komşuluk yeşili 150-200 m (" + K["TAS"] + ")",
   "Dış mekân serbest zaman", A=(80, 50, 150), B=(700, 400, 1200), C=(180, 150, 250))
_p("MES_ASM", "Aile sağlık merkezi", "m", V, _mes + " (≤500 m)", "Yaşlının sağlık yolculuğu", A=(1800, 1000, 3000), B=(600, 300, 1000), C=(450, 300, 500))
_p("MES_DURAK", "Toplu taşıma durağı", "m", V, _mes + " (S1 caddesinde ≤300-400 m); A: site kapısından ana yola", "Toplu taşıma erişimi",
   A=(900, 500, 1500), B=(300, 150, 500), C=(300, 200, 400))
_p("MES_KAHVE", "Kahvehane / çay ocağı / çay bahçesi", "m", V, "Varsayım; A: site kafesi; C: meydan çay bahçesi", "Yaşlının sosyal zamanı",
   A=(200, 100, 400), B=(150, 80, 300), C=(300, 200, 450))
_p("MES_SPOR", "Spor salonu", "m", V, "Varsayım; A: site içi fitness; C: mahalle konağı (≤500 m)", "Spor yolculuğu",
   A=(100, 50, 200), B=(800, 400, 1500), C=(450, 300, 500))
_p("MES_KUTUPHANE", "Kütüphane / çalışma salonu", "m", V, "C: mahalle konağı (" + K["TAS"] + "); A, B evde çalışılır", "Öğrencinin çalışması", C=(450, 300, 500))
_p("MES_DUKKAN_CAMI", "Esnafın dükkânından camiye", "m", V, "Varsayım; A'da esnafın dükkânı eski semtte (B ile aynı doku)", "Esnafın öğle ve ikindi cemaati",
   A=(250, 150, 400), B=(250, 150, 400), C=(150, 100, 200))
_p("MES_TOPLANMA", "Güvenli toplanma alanına (bina yüksekliği kadar uzak açık alan)", "m", V,
   "Varsayım; A: site bahçesi ama 36 m'lik bloğun yıkılma alanı dışında; B: en yakın park; C: komşuluk yeşili", "Deprem tahliyesi",
   A=(60, 40, 100), B=(450, 250, 800), C=(150, 100, 200))
_p("UZ_MERKEZ_KM", "Merkezî iş alanına uzaklık", "km", V,
   "Varsayım: A çeperde; B iç-orta halkada; C temel senaryoda B ile aynı konumda (dönüşüm ya da raylı hat üzerinde yeni mahalle). C-çeper duyarlılığında 22 km",
   "İşe gidiş", A=(22, 15, 30), B=(10, 6, 15), C=(10, 6, 15))
_p("UZ_SEMT_KM", "Semt ölçeğinde işe (okul, büro) uzaklık", "km", V, "Varsayım", "İşe gidiş", A=(6, 4, 10), B=(3, 2, 5), C=(3, 2, 5))
_p("UZ_UNIVERSITE_KM", "Üniversiteye uzaklık", "km", V, "Varsayım", "Öğrencinin yolculuğu", A=(25, 18, 35), B=(12, 8, 18), C=(12, 8, 18))
_p("UZ_DUKKAN_KM", "Esnafın konutundan dükkânına", "km", V,
   "Varsayım: A'da esnaf siteye taşınmış, dükkânı eski semtte; B ve C'de aynı mahallede (C'de çarşı ve zemin kat ticareti)", "Esnafın işe gidişi",
   A=(12, 6, 20), B=(0.15, 0.05, 0.3), C=(0.35, 0.2, 0.5))

# --- 2.5 Serbest zaman ve davranış ----------------------------------------------
_dis = ("Varsayım. Yön: zemine/avluya doğrudan açılan hane A %8, B ≈%18, C ≈%90 (" + K["CSV"] + "); "
        + K["GIFFORD"] + "; " + K["PSI"])
_p("DIS_SERBEST_CALISAN", "Dış mekân serbest zaman, çalışan yetişkin / genç (iş günü)", "dk/gün", V, _dis, "Dış mekân, karşılaşma, doğa teması",
   A=(10, 5, 20), B=(5, 0, 12), C=(20, 10, 30))
_p("DIS_SERBEST_BAKIMVEREN", "Dış mekân serbest zaman, çocuk bakan yetişkin (anne, büyükanne)", "dk/gün", V, _dis, "Dış mekân, karşılaşma, doğa teması",
   A=(25, 15, 40), B=(15, 5, 25), C=(40, 25, 60))
_p("DIS_SERBEST_COCUK", "Dış mekân oyun, 8 yaş (okul dışı)", "dk/gün", V, _dis, "Çocuğun dış mekân süresi, miyopi",
   A=(40, 25, 60), B=(20, 10, 40), C=(75, 45, 100))
_p("DIS_SERBEST_YASLI", "Dış mekân oturma / yürüyüş, yaşlı", "dk/gün", V, _dis, "Yaşlının dış mekân süresi",
   A=(20, 10, 35), B=(10, 5, 20), C=(40, 25, 60))
_p("DIS_SERBEST_TEKERLEKLI", "Dış mekân serbest zaman, tekerlekli sandalye kullanıcısı", "dk/gün", V,
   _dis + "; B'de kaldırım ve giriş basamakları", "Dış mekân", A=(15, 5, 25), B=(5, 0, 10), C=(30, 15, 45))
_p("YESIL_ZIYARET_FREK", "Yeşile gidiş sıklığı (günlük)", "kez/gün", V, "Varsayım: uzak parka daha seyrek ama daha uzun gidilir", "Yeşile yürüme süresi",
   A=1.0, B=(0.3, 0.2, 0.5), C=1.0)
_p("HAFTASONU_DIS_CARPAN", "Hafta sonu dış mekân süresi / iş günü", "kat", V, "Varsayım", "Haftalık doğa teması", ortak=(1.5, 1.0, 2.5))
_p("KAHVE_DK", "Kahvehane / çay bahçesinde geçen süre (yaşlı erkek)", "dk/gün", V,
   "Varsayım: B ve C'de karma doku kahvehane ve çay bahçesi barındırır; A'da site kafesi", "P5 sosyal zaman",
   A=(15, 0, 30), B=(60, 30, 90), C=(50, 30, 80))
_p("KOMSU_ZIYARET_DK", "Komşu ziyareti / gün (büyükanne)", "dk/gün", V, "Varsayım; " + K["TAYA"], "P4 sosyal zaman",
   A=(20, 5, 40), B=(60, 30, 90), C=(60, 30, 90))
_p("CEMAAT_VAKIT_YASLI", "Mescitte cemaate katılınan vakit (dindar yaşlı)", "vakit/gün", V,
   "Varsayım: erişim süresi kısaldıkça katılım artar; B'de asansörsüz 4. kat katılımı sınırlar", "P5 ibadet ve karşılaşma",
   A=(1.0, 0.5, 2.0), B=(2.0, 1.0, 3.0), C=(3.0, 2.0, 4.0))
_p("ESNAF_AKSAM_CAMI_FREK", "Esnafın akşam/yatsı cemaati (evden)", "kez/gün", V, "Varsayım: mesafeye bağlı", "P7",
   A=(0.2, 0.0, 0.4), B=(0.5, 0.3, 0.8), C=(0.6, 0.4, 0.9))

# --- 2.6 Komşuyla karşılaşma modeli ----------------------------------------------
_kars = ("Varsayım (kalibre edilmedi; M3 ajan tabanlı modelde sınanacak). Yön: Gifford 2007 (yüksek katta 'tanıdık çok, arkadaş az'), "
         "Wood ve ark. 2010 (yürürken komşu görmek), Leyden 2003; karşı kanıt Brueckner & Largey 2008; ölçek: Alexander 8-12 haneli avlu grubu")
for alan, ac, lam, tan in [
    ("BINA", "bina içi ortak alan (asansör, merdiven, avlu kapısı)",
     dict(A=(0.4, 0.2, 0.6), B=(0.25, 0.1, 0.4), C=(0.3, 0.15, 0.45)),
     dict(A=(0.25, 0.1, 0.4), B=(0.7, 0.5, 0.85), C=(0.85, 0.7, 0.95))),
    ("SOKAK", "mahalle içinde yürürken",
     dict(A=(0.5, 0.2, 0.8), B=(2.0, 1.2, 3.0), C=(1.2, 0.7, 1.8)),
     dict(A=(0.15, 0.05, 0.25), B=(0.12, 0.06, 0.2), C=(0.3, 0.15, 0.45))),
    ("AVLU", "avlu, site bahçesi, park",
     dict(A=(0.5, 0.3, 0.8), B=(0.6, 0.3, 0.9), C=(0.5, 0.3, 0.8)),
     dict(A=(0.3, 0.15, 0.45), B=(0.15, 0.05, 0.25), C=(0.6, 0.4, 0.8))),
    ("DUKKAN", "yerel dükkân ve pazar (müşteri olarak)",
     dict(A=(1.0, 0.5, 1.5), B=(0.5, 0.3, 0.8), C=(0.5, 0.3, 0.8)),
     dict(A=(0.05, 0.0, 0.1), B=(0.4, 0.25, 0.55), C=(0.45, 0.3, 0.6))),
    ("CAMI", "mescit / cami",
     dict(A=(1.0, 0.6, 1.4), B=(1.0, 0.6, 1.4), C=(1.0, 0.6, 1.4)),
     dict(A=(0.3, 0.15, 0.45), B=(0.5, 0.35, 0.65), C=(0.65, 0.5, 0.8))),
    ("KAHVE", "kahvehane / çay bahçesi",
     dict(A=(0.3, 0.15, 0.45), B=(0.4, 0.2, 0.6), C=(0.4, 0.2, 0.6)),
     dict(A=(0.3, 0.15, 0.45), B=(0.6, 0.4, 0.8), C=(0.6, 0.4, 0.8))),
    ("OKUL", "okul kapısı / servis noktası",
     dict(A=(0.8, 0.4, 1.2), B=(1.0, 0.5, 1.5), C=(1.0, 0.5, 1.5)),
     dict(A=(0.1, 0.05, 0.2), B=(0.35, 0.2, 0.5), C=(0.45, 0.3, 0.6))),
]:
    _p(f"LAMBDA_{alan}", f"Karşılaşılan kişi, {ac}", "kişi/dk", V, _kars, "Komşuyla karşılaşma", **lam)
    _p(f"TANIDIK_{alan}", f"Karşılaşılanlardan tanıdık komşu payı, {ac}", "oran", V, _kars, "Komşuyla karşılaşma", **tan)
_p("ESNAF_MUSTERI_LAMBDA", "Esnafın dükkânda müşteri teması", "kişi/dk", V, "Varsayım", "P7 karşılaşma", ortak=(0.08, 0.05, 0.12))
_p("ESNAF_MAHALLELI_PAY", "Müşterilerden esnafın kendi konut mahallesinden olanların payı", "oran", V,
   "Varsayım: A'da dükkân başka semtte, konut komşusu müşteri olmaz", "P7 karşılaşma", A=0.0, B=(0.6, 0.4, 0.8), C=(0.7, 0.5, 0.85))
_p("ZIYARET_KISI_SAAT", "Komşu ziyaretinde saat başına görüşülen kişi", "kişi/sa", V, "Varsayım", "P4 karşılaşma", ortak=(2.5, 1.5, 4.0))

# --- 2.7 Çocuğun bağımsız hareketi ------------------------------------------------
_p("COCUK_ALAN_HA", "8 yaşındaki çocuğun ebeveynsiz dolaşabildiği alan", "ha", V + H,
   "A: site duvarları içi (varsayım); B: aynı sokak ve blok (varsayım); C: araç hücresi 60 ha / 4 = 15 ha [H, " + K["TAS"] + " 9.6], 8 yaşta tamamı kullanılmaz; " + K["PSI"],
   "Çocuğun bağımsız hareket alanı", A=(4, 2, 8), B=(1.0, 0.5, 2.0), C=(12, 8, 15))
_p("COCUK_IZIN_MESAFE_M", "Ebeveynin 8 yaşa yalnız izin verdiği en uzak mesafe", "m", V, "Varsayım; " + K["PSI"], "Bağımsız hedef sayısı", ortak=(500, 400, 700))
for hedef, a, b, c in [("OKUL", 1, 1, 0), ("YESIL", 0, 1, 0), ("BAKKAL", 1, 0, 0), ("ARKADAS", 0, 0, 0), ("MESCIT", 1, 1, 0)]:
    _p(f"ANA_YOL_{hedef}", f"Çocuğun {hedef.lower()} yolunda ana yol / trafikli cadde geçişi (1 = var)", "0/1", V,
       "Varsayım: A'da site dışı her hedef ana yol gerektirir; C'de okul sokağı araçsız ve hücre içinde geçiş trafiği yok (" + K["TAS"] + " 9.6)",
       "Bağımsız hedef sayısı", A=a, B=b, C=c)

# --- 2.8 Sağlık ve iyi oluş katsayıları --------------------------------------------
_p("SALLIS_FARK_DK_HAFTA", "En ve en az aktivite dostu mahalle arasındaki aktivite farkı", "dk/hafta", D, K["SALLIS"],
   "Haftalık aktivite farkı (sınır)", dagilim="düzgün", ortak=(78.5, 68, 89))
_p("NET_KONUT_YOG_1KM", "1 km çevrede net konut yoğunluğu", "konut/ha", V + H, "C: 70 konut/ha (" + K["TAS"] + "); A çevresinde otoyol ve boş arazi; B 5-6 katlı sık doku",
   "Aktivite dostu puan", A=(60, 40, 90), B=(180, 130, 250), C=(70, 60, 90))
_p("KAVSAK_YOG", "Kavşak yoğunluğu", "kavşak/km²", V + H, "C: ≈90 [H, " + K["TAS"] + "]; A süper blok; B organik sık ağ", "Aktivite dostu puan",
   A=(30, 20, 50), B=(120, 90, 160), C=(90, 80, 120))
_p("PARK_SAYISI_500M", "500 m içinde park / kullanılabilir yeşil sayısı", "adet", V + H, "C: 8 komşuluk yeşili + merkez parkı (" + K["TAS"] + ")", "Aktivite dostu puan",
   A=(1, 0, 2), B=(0.5, 0, 1), C=(4, 3, 5))
_p("CAPA_YOG", "Aktivite puanı ölçeği: net yoğunluk alt-üst çapa", "konut/ha", V, "Varsayım: 20 → 200", "Aktivite dostu puan", alt=20, ust=200)
_p("CAPA_KAVSAK", "Aktivite puanı ölçeği: kavşak alt-üst çapa", "kavşak/km²", V, "Varsayım: 20 → 150", "Aktivite dostu puan", alt=20, ust=150)
_p("CAPA_DURAK", "Aktivite puanı ölçeği: durak mesafesi kötü-iyi çapa", "m", V, "Varsayım: 1.200 → 150", "Aktivite dostu puan", alt=1200, ust=150)
_p("CAPA_PARK", "Aktivite puanı ölçeği: park sayısı alt-üst çapa", "adet", V, "Varsayım: 0 → 4", "Aktivite dostu puan", alt=0, ust=4)
_p("NEDENSEL_PAY", "Kesitsel/gözlemsel katsayıların nedensel kabul edilen payı", "oran", V,
   "Varsayım: seçilim ve karıştırıcılık nedeniyle gözlemsel ilişkinin yalnız bir kısmı mekânın etkisi (Faz 2 dersi). RKÇ'ye (He 2015) uygulanmaz",
   "Bütün sağlık yansımaları", ortak=(0.5, 0.25, 1.0))
_p("FRANK_ARAC_SAAT_OR", "Arabada her ek saat/gün için obezite olasılık oranı", "OR", D + V, K["FRANK"] + "; aralık (±%50) varsayım", "Obezite", ortak=(1.06, 1.03, 1.09))
_p("FRANK_YURUME_KM_OR", "Her ek km yürüme/gün için obezite olasılık oranı", "OR", D + V, K["FRANK"] + "; aralık (±%50) varsayım", "Obezite", ortak=(0.952, 0.928, 0.976))
_p("SF_TELAFI_DK", "İşe gidiş: tek yön her dakikanın iyi oluş eşdeğeri", "aylık gelir payı/dk", D + V,
   K["SF"] + ". %35,4 / 22 dk = %1,61/dk üst uç; alt uç 0 (karşı kanıt); temel ikisinin ortası (varsayım)", "İşe gidiş iyi oluş eşdeğeri",
   ortak=(0.008, 0.0, 0.0161))
_p("PUTNAM_10DK", "Her ek 10 dk işe gidişte topluluk katılımı kaybı", "oran", I + V, K["PUTNAM"] + "; alt uç 0 (varsayım)", "Topluluk katılımı",
   ortak=(0.05, 0.0, 0.10))
_p("WHITE_ESIK_DK", "Doğa teması eşiği", "dk/hafta", D, K["WHITE"], "Doğa teması", ortak=120)
_p("WHITE_OR_SAGLIK", "≥120 dk/hafta doğa teması: iyi sağlık olasılık oranı", "OR", D, K["WHITE"], "Doğa teması", ortak=(1.59, 1.31, 1.92))
_p("IYI_SAGLIK_TABAN", "Eşik altında 'iyi sağlık' beyan olasılığı", "oran", V, "Varsayım (Türkiye değeri bu çalışmada yok)", "Doğa teması", ortak=(0.60, 0.50, 0.70))
_p("NDVI_500M", "Konut çevresinde 500 m NDVI", "NDVI", V,
   "Varsayım; A site peyzajı; B yeşilsiz; C başlangıç (ağaç örtüsü hedefi %30'a 15-20 yılda ulaşır)", "Yeşil ve ölüm",
   A=(0.30, 0.20, 0.40), B=(0.12, 0.08, 0.18), C=(0.35, 0.25, 0.45))
_p("ROJAS_HR", "Her 0,1 NDVI için tüm nedenli ölüm tehlike oranı", "HR", D, K["ROJAS"], "Yeşil ve ölüm", ortak=(0.96, 0.94, 0.97))
_p("YASLI_YILLIK_OLUM", "75 yaş civarı yıllık ölüm olasılığı", "oran", V, "Varsayım; TÜİK Hayat Tabloları ile teyit edilmeli", "Yeşil ve ölüm", ortak=(0.04, 0.03, 0.05))
_p("HE_FARK_PP", "Günde ek 40 dk dış mekânın 3 yıllık miyopi insidansına etkisi", "yüzde puan", D, K["HE"], "Miyopi", ortak=(9.1, 4.1, 14.1))
_p("HE_TABAN", "Kontrol grubunda 3 yıllık miyopi insidansı (Guangzhou)", "%", D, K["HE"], "Miyopi", ortak=39.5)
_p("MIYOPI_TASINABILIRLIK", "Okul saatindeki yapılandırılmış dış mekân etkisinin mahalle oyununa ve Türkiye'ye aktarılabilir payı", "oran", V,
   "Varsayım: RKÇ okul saatinde Guangzhou'da yapıldı; Türkiye taban riski bilinmiyor (veri boşluğu)", "Miyopi", ortak=(0.75, 0.5, 1.0))
_p("MIYOPI_TAVAN_DK", "Doğrusal varsayılan en büyük dış mekân farkı", "dk/gün", V, "Varsayım; " + K["XIONG"], "Miyopi", ortak=(80, 60, 100))

# --- 2.9 Kriz senaryoları -------------------------------------------------------
_p("AGIR_HASAR_P", "Senaryo depremi (yakın alanda büyük deprem): yapının ağır hasar görme ya da yıkılma olasılığı", "oran", V,
   "Varsayım; kalibrasyon için SBB 2023 raporu ve yapım yılına göre hasar verisi gerekli. Bağlam: " + K["DEPREM"]
   + ". A: 2007/2018 sonrası, mühendislik hizmeti ve denetimli; B: 1970-2000 yap-sat, yumuşak kat ve kaçak kat riski; C: TBDY 2018, az katlı, düzenli",
   "Deprem", A=(0.02, 0.005, 0.06), B=(0.15, 0.05, 0.30), C=(0.01, 0.003, 0.04))
_p("OLUM_AGIR_HASARDA", "Ağır hasarlı/yıkık konutta yaşayan kişi başına can kaybı", "oran", H + I,
   "53.537 / (518.009 × 3,1 kişi) ≈ 0,033 [H, ikincil verilerle]; aralık varsayım", "Deprem", ortak=(0.033, 0.01, 0.08))
_p("TAHLIYE_YOGUNLUK", "Merdivende tahliye yoğunluk çarpanı", "kat", V, "Varsayım: A'da 48 daireli tek çekirdek", "Deprem tahliyesi",
   A=(1.8, 1.3, 2.5), B=(1.2, 1.0, 1.5), C=1.0)
_p("TEKERLEKLI_KAT_DK", "Tekerlekli sandalye kullanıcısının yardımla merdiven inişi", "dk/kat", V, "Varsayım", "Deprem tahliyesi", ortak=(3, 2, 5))
_p("YARDIM_BEKLEME_DK", "Yardım bekleme süresi", "dk", V, "Varsayım", "Deprem tahliyesi", ortak=(5, 2, 15))
_p("SOKAK_HW", "Sokak bina yüksekliği / sokak genişliği", "oran", V + H, "C: S2 kesiti H:W 0,7-1,0 (" + K["TAS"] + "); A bloklar arası açık; B 7-10 m sokak, 16,5 m bina",
   "Enkazla yol kapanması", A=(0.3, 0.2, 0.5), B=(1.8, 1.2, 2.5), C=(0.9, 0.7, 1.0))
_p("ZEMINE_ACILAN", "Zemine / avluya doğrudan açılan hane payı", "oran", H + V,
   "A: " + K["CSV"] + " (%8,33); B: 5-6 katta zemin kat payı ≈1/5,5 [V]; C: T1-T3 avluya açılır, T4 üst katları hariç [H]",
   "Salgın", A=0.083, B=(0.18, 0.15, 0.20), C=(0.90, 0.80, 1.0))
_p("OZEL_DIS_M2_KISI", "Kişi başı özel bahçe/avlu", "m²/kişi", H, K["CSV"] + " (C: 3.240 m² / 96 hane / 3,1 kişi)", "Salgın", A=0, B=0, C=10.9)
_p("AGAC_ORTUSU", "Ağaç örtüsü (başlangıç)", "oran", V, "Varsayım; C hedefi 15-20 yılda %30 (" + K["TAS"] + ", 3-30-300)", "Sıcak dalgası",
   A=(0.20, 0.10, 0.30), B=(0.05, 0.02, 0.10), C=(0.15, 0.10, 0.20))
_p("SICAK_DISARI_CARPAN", "Sıcak dalgasında dış mekân ve karşılaşmanın kalan payı", "oran", V, "Varsayım", "Sıcak dalgası", ortak=(0.4, 0.2, 0.6))
_p("YAKIN_TANIDIK_PAYI", "Selamlaşma düzeyindeki karşılaşmalardan, yokluğu fark edip kapıyı çalacak yakınlıktakilerin payı", "oran", V,
   "Varsayım; yalnızlık-ölüm ilişkisinin ağırlığı için " + K["HOLT"], "Sıcak dalgası, yalnız yaşlı", ortak=(0.05, 0.02, 0.10))
_p("GELIR_SOKU", "Ekonomik kriz: reel hane geliri değişimi", "oran", V, "Senaryo varsayımı", "Ekonomik kriz", ortak=(-0.20, -0.30, -0.10))
_p("YAKIT_SOKU", "Ekonomik kriz: yakıt fiyatı değişimi", "oran", V, "Senaryo varsayımı", "Ekonomik kriz", ortak=(0.50, 0.30, 0.80))
_p("BRUT_YOG_KISI_HA", "Brüt nüfus yoğunluğu (300 m çevre)", "kişi/ha", V + H, "C: 120 kişi/ha (" + K["TAS"] + "); A çevresi otoyol ve boş arazi; B 5-6 katlı sık doku",
   "Esnafın yürüme havzası", A=(100, 60, 150), B=(280, 200, 350), C=(120, 100, 150))

# --- 2.10 Yaşam döngüsü (yasam_dongusu.py) -------------------------------------
_p("Y_GELIR_ZEYNEP_AU", "Eş 1 (öğretmen) net geliri", "asgari ücret katı", V, "Varsayım: iki üniversite mezunu, orta-üst gelirli çift", "Yaşam döngüsü geliri", ortak=(2.2, 1.8, 2.6))
_p("Y_GELIR_MERT_AU", "Eş 2 (satış, merkez) net geliri", "asgari ücret katı", V, "Varsayım: iki üniversite mezunu, orta-üst gelirli çift", "Yaşam döngüsü geliri", ortak=(2.4, 1.8, 3.0))
_p("Y_REEL_GELIR_ARTIS", "Reel gelir artışı (kariyer)", "oran/yıl", V, "Varsayım", "Yaşam döngüsü geliri", ortak=(0.015, 0.0, 0.03))
_p("Y_DIGER_TUKETIM", "Konut ve ulaşım dışı tüketimin gelire oranı (çocuksuz)", "oran", V, "Varsayım", "Tasarruf", ortak=(0.35, 0.28, 0.45))
_p("Y_COCUK_TUKETIM", "Çocuk başına ek tüketim", "gelir payı", V, "Varsayım", "Tasarruf", ortak=(0.07, 0.04, 0.10))
_p("Y_AILE_YARDIMI", "Evlilikte aileden gelen birikim / yardım", "TL", V, "Varsayım", "Peşinat", ortak=(1000000, 400000, 2000000))
_p("Y_PESINAT", "Peşinat oranı", "oran", V, "Varsayım", "Ev edinme", ortak=(0.25, 0.20, 0.35))
_p("Y_MASRAF", "Tapu harcı ve alım masrafı", "fiyat payı", V, "Varsayım (tapu harcı alıcı+satıcı %4 uygulaması [DY] + masraf)", "Ev edinme", ortak=(0.05, 0.04, 0.06))
_p("Y_REEL_FAIZ", "Konut kredisinde reel faiz", "oran/yıl", V, "Varsayım", "Ev edinme", ortak=(0.05, 0.02, 0.09))
_p("Y_VADE", "Kredi vadesi", "yıl", V, "Varsayım", "Ev edinme", ortak=10)
_p("Y_REEL_KONUT_ARTIS", "Reel konut fiyatı ve kira artışı", "oran/yıl", V,
   "Varsayım; Ağustos 2026'da İstanbul m² fiyatı reel −%3,4, kira reel +%9,4 (foreks.com, cnbce.com)", "Konut maliyeti ve servet", ortak=(0.01, -0.02, 0.03))
_p("Y_BAKIM_ORANI", "Ev sahibinin yıllık bakım gideri", "değer payı/yıl", V, "Varsayım", "Konut maliyeti", ortak=(0.005, 0.003, 0.01))
_p("Y_M2_ILK", "İlk konut (2+1)", "m²", V, "Varsayım", "Konut maliyeti", ortak=90)
_p("Y_M2_AILE", "Aile konutu (3+1)", "m²", V, "Varsayım", "Konut maliyeti", ortak=120)
_p("Y_COCUK2_P_A", "A'da ikinci çocuk olasılığı (referans)", "oran", V, "Varsayım; mutlak düzey değil, ortamlar arası fark yorumlanmalı", "Doğurganlık", ortak=(0.55, 0.35, 0.75))
_p("Y_ARAC_ILK", "Araç sayısı, çocuk öncesi (t<3)", "araç", V, "Varsayım; " + K["OTOMOBIL"], "Ulaşım maliyeti", A=1, B=0, C=0)
_p("Y_ARAC_AILE", "Araç sayısı, çocuklu dönem (t≥3)", "araç", V, "Varsayım: A'da çocuk lojistiği ikinci aracı zorunlu kılar; C'de araçsız + paylaşımlı araç", "Ulaşım maliyeti", A=2, B=1, C=0)
_p("Y_IKINCI_ARAC_KM", "İkinci aracın yıllık kullanımı", "km/yıl", V, "Varsayım", "Ulaşım maliyeti", ortak=(6000, 3000, 9000))
_p("Y_B_DONUSUM_P", "B'de 30 yıl içinde binanın 6306'ya göre yıkılıp yeniden yapılma olasılığı", "oran", V,
   "Varsayım; 6306 md. 5 kira yardımı, md. 6 salt çoğunluk (08_MEVZUAT_POLITIKA/mevzuat_politika_haritasi.md)", "B yaşam döngüsü", ortak=(0.5, 0.3, 0.7))
_p("Y_B_DONUSUM_YIL", "B'de dönüşüm yılı", "yıl", V, "Varsayım", "B yaşam döngüsü", ortak=(12, 8, 20))
_p("Y_B_DONUSUM_SURE", "Dönüşümde evden uzak kalma süresi", "yıl", V, "Varsayım", "B yaşam döngüsü", ortak=(2.5, 2, 4))
_p("Y_B_DONUSUM_DEGER", "Dönüşüm sonrası konut değer artışı", "oran", V, "Varsayım (yeni bina, kat karşılığı)", "B yaşam döngüsü", ortak=(0.30, 0.15, 0.50))
_p("Y_B_DONUSUM_AIDAT_M2", "Dönüşüm sonrası aidat (asansörlü yeni bina)", "TL/m²·ay", V, "Varsayım", "B yaşam döngüsü", ortak=(15, 8, 25))
_p("Y_KIRA_YARDIMI", "Dönüşüm süresince kira yardımının kiraya oranı", "oran", V, "Varsayım; tutar 6306 md. 5 uygulamasına bağlı", "B yaşam döngüsü", ortak=(0.3, 0.0, 0.5))
_p("Y_KOOP_ORAN", "Kooperatif / maliyetine konut fiyatı / C piyasa fiyatı", "oran", V,
   "Varsayım (Batıkent, Vauban yapı grupları; " + K["TAS"] + " 9.4: en az %30 kooperatif); Türkiye için ölçülmüş veri yok", "C-kooperatif yolu", ortak=(0.70, 0.60, 0.85))
_p("Y_KOOP_TESLIM", "Kooperatife girişten teslime", "yıl", V, "Varsayım", "C-kooperatif yolu", ortak=(3, 2, 5))
_p("Y_EBEVEYN_MESAFE_KM", "Genç çiftin ebeveyn evine uzaklığı", "km", V,
   "Senaryo varsayımı: A'da yeni site çifti aileden uzaklaştırır; B'de kök salmış eski mahalle (TÜİK 2025: 65+'ların %50,6'sı çocuğuyla aynı adres/bina/sokakta); C'de kuşak yakınlık desteği ve çok kuşaklı tip",
   "Kuşaklar arası mesafe", A=(18, 10, 30), B=(4, 1, 8), C=(0.5, 0.1, 1.5))
_p("Y_DESTEK_SIFIR_DK", "Günlük büyükanne desteğinin imkânsızlaştığı tek yön yolculuk", "dk", V, "Varsayım: ≤10 dk tam, bu değerde sıfır, arası doğrusal", "Kuşak desteği", ortak=(45, 35, 60))
_p("Y_BUYUKANNE_BAKIM_SAAT", "Tam erişimde haftalık büyükanne çocuk bakımı", "saat/hafta", V, "Varsayım", "Kuşak desteği", ortak=(15, 10, 20))
_p("Y_ANNE_ISTIHDAM_TABAN", "Küçük çocuklu dönemde annenin çalışmayı sürdürme olasılığı (destek yokken)", "oran", V,
   "Varsayım (kadın işgücüne katılımı %36,2 genel; yükseköğretimli öğretmende daha yüksek)", "Anne istihdamı", ortak=(0.70, 0.55, 0.85))
_p("Y_CP_ETKI", "Büyükanneye yakınlığın istihdam etkisi", "yüzde puan", D, K["CP"], "Anne istihdamı", ortak=(0.07, 0.04, 0.10))
_p("Y_EBEVEYN_BAKIM_BASLANGIC", "Ebeveyn bakımının başladığı yıl", "yıl (t)", V, "Varsayım: ebeveyn ≈75 yaş", "Ebeveyn bakımı", ortak=(19, 16, 23))
_p("Y_BAKIM_ZIYARET_HAFTA", "Ebeveyn bakımı için haftalık ziyaret", "kez/hafta", V, "Varsayım", "Ebeveyn bakımı", ortak=(3, 2, 5))
_p("Y_FAZ2_KAT", "Bina yüksekliğinin doğurganlık etkisi (3 m başına, eğitim sabit)", "çocuk/3 m", D, K["FAZ2"] + "; alt uç 0 (birçok modelde anlamsız), üst uç 0,136 (ham)",
   "Doğurganlık (sınır)", ortak=(0.029, 0.0, 0.136))
_p("Y_YUKSEKLIK_UST_M", "Faz 2 verisinin desteklediği en yüksek yaşanan yükseklik", "m", H, K["FAZ2"] + " (yükseklik sınıfları 4 → 12+ m)", "Doğurganlık (sınır)", ortak=(15, 12, 18))
_p("Y_YASANAN_YUKSEKLIK", "Yaşanan bina yüksekliği", "m", H + V, "A, C: " + K["CSV"] + "; B: 5,5 kat × 3 m", "Doğurganlık (sınır)", A=36, B=(16.5, 15, 18), C=9)
_p("Y_AKRABA_COCUK_MAKS", "Tam büyükanne desteğinin beklenen çocuk sayısına en büyük katkısı", "çocuk", V,
   "Varsayım; yön " + K["KAPTIJN"], "Doğurganlık (sınır)", ortak=(0.05, 0.0, 0.10))
_p("Y_DOGURGANLIK_TAVAN", "Ortamlar arası toplam doğurganlık farkı tavanı", "çocuk", V,
   "Varsayım; 09_RAPORLAR/02 (yoğun kent → orta yoğun kent senaryosu +0,13, üst sınır) ile tutarlı", "Doğurganlık (sınır)", ortak=0.3)


def varsayim_tablosu() -> pd.DataFrame:
    return pd.DataFrame(VARSAYIMLAR)


# =============================================================================
# 3. PARAMETRE ERİŞİMİ VE MONTE CARLO ÖRNEKLEME
# =============================================================================
class Prm:
    """Temel değerleri ya da i'inci Monte Carlo çekilişini döndürür."""

    def __init__(self, cekilis: dict | None = None, i: int = 0, degisiklik: dict | None = None):
        self.cekilis = cekilis
        self.i = i
        self.degisiklik = degisiklik or {}

    def __call__(self, kod: str, ortam: str = "ortak") -> float:
        if (kod, ortam) in self.degisiklik:
            return self.degisiklik[(kod, ortam)]
        anahtar = (kod, ortam) if (kod, ortam) in PARAM else (kod, "ortak")
        if anahtar not in PARAM:
            raise KeyError(f"Parametre yok: {kod}/{ortam}")
        if self.cekilis is None:
            return PARAM[anahtar][0]
        return float(self.cekilis[anahtar][self.i])

    def degistir(self, degisiklik: dict) -> "Prm":
        d = dict(self.degisiklik)
        d.update(degisiklik)
        return Prm(self.cekilis, self.i, d)


def ornekle(n: int, tohum: int = TOHUM) -> dict:
    rng = np.random.default_rng(tohum)
    cek = {}
    for anahtar in sorted(PARAM):
        temel, dusuk, yuksek, dagilim = PARAM[anahtar]
        if dusuk == yuksek:
            cek[anahtar] = np.full(n, temel)
        elif dagilim == "düzgün":
            cek[anahtar] = rng.uniform(dusuk, yuksek, n)
        else:
            cek[anahtar] = rng.triangular(dusuk, temel, yuksek, n)
    return cek


# =============================================================================
# 4. PERSONALAR
# =============================================================================
def Y(amac, hedef, frek, mod, kalis=0, kat=None, alan=None, gunisigi=0.7, evden=True, yerel=True, is_yolu=False, kalis_dis=0.0, cikis=1.0):
    """Bir yolculuk tanımı (gidiş-dönüş). hedef: MES_* (m) ya da UZ_* (km) parametresi ya da ortam sözlüğü.
    frek, kalis: sayı, ortam sözlüğü ya da parametre kodu. mod: ortam -> 'yuruyus' | 'toplu' | 'arac' | 'servis' | 'taksi' | 'yok'."""
    return dict(amac=amac, hedef=hedef, frek=frek, mod=mod, kalis=kalis, kat=kat, alan=alan, gunisigi=gunisigi,
                evden=evden, yerel=yerel, is_yolu=is_yolu, kalis_dis=kalis_dis, cikis=cikis)


HER = lambda m: {"A": m, "B": m, "C": m}   # noqa: E731

KISILER = [
    dict(kod="P1", persona="Genç bekâr", ad="Emre", yas=27, hane="H1", hiz="HIZ_YETISKIN", dis_tip="CALISAN",
         kat={"A": 7, "B": 3, "C": 2}, asansor={"A": True, "B": False, "C": True}, gelir_au=2.0, rol="çalışan",
         sabit={"uyku": 450, "kisisel_bakim_yemek": 120, "ucretli_is_okul": 540, "ev_isi_bakim": 40},
         yol=[Y("İşe gidiş (merkez)", "UZ_MERKEZ_KM", 1, HER("toplu"), gunisigi=0.6, yerel=False, is_yolu=True),
              Y("Bakkal-fırın", "MES_BAKKAL", {"A": 0.4, "B": 0.7, "C": 0.7}, HER("yuruyus"), 8, "ev_isi_bakim", "DUKKAN", 0.4),
              Y("Spor salonu", "MES_SPOR", 0.43, HER("yuruyus"), 60, "spor", None, 0.3)]),
    dict(kod="P2a", persona="Yeni evli çift", ad="Zeynep (eş, öğretmen)", yas=26, hane="H2", hiz="HIZ_YETISKIN", dis_tip="CALISAN",
         kat={"A": 7, "B": 3, "C": 1}, asansor={"A": True, "B": False, "C": False}, gelir_au=2.2, rol="çalışan",
         sabit={"uyku": 450, "kisisel_bakim_yemek": 120, "ucretli_is_okul": 480, "ev_isi_bakim": 150},
         yol=[Y("İşe gidiş (semt)", "UZ_SEMT_KM", 1, HER("toplu"), gunisigi=0.8, yerel=False, is_yolu=True),
              Y("Pazar / market (eşiyle)", "MES_MARKET", 0.3, {"A": "arac", "B": "yuruyus", "C": "yuruyus"}, 40, "ev_isi_bakim", "DUKKAN", 0.5),
              Y("Bakkal-fırın", "MES_BAKKAL", {"A": 0.3, "B": 0.5, "C": 0.5}, HER("yuruyus"), 8, "ev_isi_bakim", "DUKKAN", 0.6)]),
    dict(kod="P2b", persona="Yeni evli çift", ad="Mert (eş, satış)", yas=29, hane="H2", hiz="HIZ_YETISKIN", dis_tip="CALISAN",
         kat={"A": 7, "B": 3, "C": 1}, asansor={"A": True, "B": False, "C": False}, gelir_au=2.4, rol="çalışan",
         sabit={"uyku": 450, "kisisel_bakim_yemek": 120, "ucretli_is_okul": 540, "ev_isi_bakim": 60},
         yol=[Y("İşe gidiş (merkez)", "UZ_MERKEZ_KM", 1, {"A": "arac", "B": "toplu", "C": "toplu"}, gunisigi=0.6, yerel=False, is_yolu=True),
              Y("Pazar / market (eşiyle)", "MES_MARKET", 0.3, {"A": "arac", "B": "yuruyus", "C": "yuruyus"}, 40, "ev_isi_bakim", "DUKKAN", 0.5)]),
    dict(kod="P3a", persona="İki çocuklu aile", ad="Ayşe (anne, yarı zamanlı)", yas=36, hane="H3", hiz="HIZ_YETISKIN", dis_tip="BAKIMVEREN",
         kat={"A": 7, "B": 3, "C": 0}, asansor={"A": True, "B": False, "C": False}, gelir_au=1.2, rol="çalışan",
         sabit={"uyku": 450, "kisisel_bakim_yemek": 110, "ucretli_is_okul": 300, "ev_isi_bakim": 210},
         yol=[Y("Anaokulu (küçük çocuk, bırak-al)", "MES_ANAOKULU", 2, {"A": "arac", "B": "yuruyus", "C": "yuruyus"}, 3, "ev_isi_bakim", "OKUL", 0.9, cikis=0.5),
              Y("Okul eşliği (8 yaş)", {"A": "MES_SERVIS_NOKTASI", "B": "MES_ILKOKUL", "C": "MES_ILKOKUL"}, 2,
                {"A": "yuruyus", "B": "yuruyus", "C": "yok"}, 5, "ev_isi_bakim", "OKUL", 0.9, cikis=0.5),
              Y("İşe gidiş (semt)", "UZ_SEMT_KM", 1, {"A": "arac", "B": "toplu", "C": "toplu"}, gunisigi=0.9, yerel=False, is_yolu=True),
              Y("Bakkal-fırın", "MES_BAKKAL", 1, {"A": "arac", "B": "yuruyus", "C": "yuruyus"}, 8, "ev_isi_bakim", "DUKKAN", 0.8),
              Y("Pazar / market", "MES_MARKET", 0.3, {"A": "arac", "B": "yuruyus", "C": "yuruyus"}, 45, "ev_isi_bakim", "DUKKAN", 0.9)]),
    dict(kod="P3b", persona="İki çocuklu aile", ad="Ahmet (baba, teknisyen)", yas=39, hane="H3", hiz="HIZ_YETISKIN", dis_tip="CALISAN",
         kat={"A": 7, "B": 3, "C": 0}, asansor={"A": True, "B": False, "C": False}, gelir_au=2.8, rol="çalışan",
         sabit={"uyku": 450, "kisisel_bakim_yemek": 110, "ucretli_is_okul": 570, "ev_isi_bakim": 60},
         yol=[Y("İşe gidiş (merkez)", "UZ_MERKEZ_KM", 1, {"A": "arac", "B": "arac", "C": "toplu"}, gunisigi=0.6, yerel=False, is_yolu=True),
              Y("Akşam / yatsı cemaati", "MES_MESCIT", 0.3, HER("yuruyus"), 15, "ibadet_cemaat", "CAMI", 0.2),
              Y("Bakkal-fırın", "MES_BAKKAL", 0.3, {"A": "arac", "B": "yuruyus", "C": "yuruyus"}, 6, "ev_isi_bakim", "DUKKAN", 0.3)]),
    dict(kod="P3c", persona="İki çocuklu aile", ad="Elif (8 yaş)", yas=8, hane="H3", hiz="HIZ_COCUK", dis_tip="COCUK",
         kat={"A": 7, "B": 3, "C": 0}, asansor={"A": True, "B": False, "C": False}, gelir_au=0, rol="çocuk",
         sabit={"uyku": 600, "kisisel_bakim_yemek": 120, "ucretli_is_okul": 420}, sabit_dis=30,
         yol=[Y("Okul", "MES_ILKOKUL", 1, {"A": "servis", "B": "yuruyus", "C": "yuruyus"}, 3, None, "OKUL", 0.9),
              Y("Bakkala tek başına", "MES_BAKKAL", 0.3, {"A": "yok", "B": "yok", "C": "yuruyus"}, 5, "ev_isi_bakim", "DUKKAN", 0.9)]),
    dict(kod="P4", persona="Çok kuşaklı aile", ad="Fatma (büyükanne)", yas=68, hane="H4", hiz="HIZ_YASLI_SAGLIKLI", dis_tip="BAKIMVEREN",
         kat={"A": 8, "B": 1, "C": 0}, asansor={"A": True, "B": False, "C": False}, gelir_au=0.7, rol="ev",
         sabit={"uyku": 480, "kisisel_bakim_yemek": 150, "ev_isi_bakim": 300},
         yol=[Y("Bakkal-fırın", "MES_BAKKAL", {"A": 0.5, "B": 1, "C": 1}, HER("yuruyus"), 10, "ev_isi_bakim", "DUKKAN", 0.9),
              Y("Pazar", "MES_MARKET", 0.3, {"A": "toplu", "B": "yuruyus", "C": "yuruyus"}, 45, "ev_isi_bakim", "DUKKAN", 1.0),
              Y("Mescitte sohbet / Kur'an kursu", "MES_MESCIT", 0.3, HER("yuruyus"), 60, "ibadet_cemaat", "CAMI", 1.0),
              Y("Aile sağlık merkezi", "MES_ASM", 0.1, {"A": "toplu", "B": "yuruyus", "C": "yuruyus"}, 30, "kisisel_bakim_yemek", None, 1.0)]),
    dict(kod="P5", persona="Yalnız yaşlı", ad="Hüseyin (76, dul, dizinden rahatsız)", yas=76, hane="H5", hiz="HIZ_YASLI_KISITLI", dis_tip="YASLI",
         kat={"A": 9, "B": 4, "C": 0}, asansor={"A": True, "B": False, "C": False}, gelir_au=0.8, rol="emekli",
         sabit={"uyku": 480, "kisisel_bakim_yemek": 150, "ev_isi_bakim": 90},
         yol=[Y("Bakkal-fırın", "MES_BAKKAL", {"A": 0.5, "B": 1, "C": 1}, HER("yuruyus"), 10, "ev_isi_bakim", "DUKKAN", 0.9),
              Y("Mescitte cemaat", "MES_MESCIT", "CEMAAT_VAKIT_YASLI", HER("yuruyus"), 20, "ibadet_cemaat", "CAMI", 0.6),
              Y("Kahvehane / çay bahçesi", "MES_KAHVE", 1, HER("yuruyus"), "KAHVE_DK", "sosyal_ziyaret", "KAHVE", 1.0, kalis_dis={"A": 0.3, "B": 0.3, "C": 0.7}),
              Y("Aile sağlık merkezi", "MES_ASM", 0.15, {"A": "toplu", "B": "yuruyus", "C": "yuruyus"}, 30, "kisisel_bakim_yemek", None, 1.0)]),
    dict(kod="P6", persona="Engelli birey", ad="Selin (31, tekerlekli sandalye)", yas=31, hane="H6", hiz="HIZ_TEKERLEKLI", dis_tip="TEKERLEKLI",
         kat={"A": 4, "B": 0, "C": 0}, asansor={"A": True, "B": False, "C": False}, gelir_au=1.8, rol="çalışan",
         giris_basamak={"A": False, "B": True, "C": False},
         sabit={"uyku": 450, "kisisel_bakim_yemek": 150, "ucretli_is_okul": 480, "ev_isi_bakim": 60},
         yol=[Y("İşe gidiş (semt, ofis günü)", "UZ_SEMT_KM", 1, {"A": "arac", "B": "taksi", "C": "toplu"}, gunisigi=0.8, yerel=False, is_yolu=True),
              Y("Bakkal / eczane", "MES_BAKKAL", 0.5, {"A": "arac", "B": "yok", "C": "yuruyus"}, 10, "ev_isi_bakim", "DUKKAN", 0.6)]),
    dict(kod="P7", persona="Esnaf", ad="Mehmet usta (52, bakkal)", yas=52, hane="H7", hiz="HIZ_YETISKIN", dis_tip="CALISAN",
         kat={"A": 6, "B": 2, "C": 0}, asansor={"A": True, "B": False, "C": False}, gelir_au=2.5, rol="esnaf",
         sabit={"uyku": 420, "kisisel_bakim_yemek": 110, "ucretli_is_okul": 660, "ev_isi_bakim": 30}, sabit_dis=30,
         yol=[Y("Dükkâna gidiş", "UZ_DUKKAN_KM", 1, {"A": "arac", "B": "yuruyus", "C": "yuruyus"}, gunisigi=0.5, is_yolu=True,
                yerel={"A": False, "B": True, "C": True}),
              Y("Öğle yemeğine eve", "UZ_DUKKAN_KM", {"A": 0, "B": 1, "C": 1}, {"A": "yok", "B": "yuruyus", "C": "yuruyus"}, 0, None, None, 1.0,
                evden=False),
              Y("Öğle ve ikindi cemaati (dükkândan)", "MES_DUKKAN_CAMI", 2, HER("yuruyus"), 15, "ibadet_cemaat", "CAMI", 1.0, evden=False,
                yerel={"A": False, "B": True, "C": True}),
              Y("Akşam / yatsı cemaati (evden)", "MES_MESCIT", "ESNAF_AKSAM_CAMI_FREK", HER("yuruyus"), 15, "ibadet_cemaat", "CAMI", 0.1)]),
    dict(kod="P8", persona="Öğrenci", ad="Deniz (20, üniversite)", yas=20, hane="H8", hiz="HIZ_YETISKIN", dis_tip="CALISAN",
         kat={"A": 7, "B": 3, "C": 1}, asansor={"A": True, "B": False, "C": False}, gelir_au=0, rol="öğrenci",
         sabit={"uyku": 450, "kisisel_bakim_yemek": 120, "ucretli_is_okul": {"A": 480, "B": 480, "C": 360}, "ev_isi_bakim": 30},
         yol=[Y("Üniversite", "UZ_UNIVERSITE_KM", 1, HER("toplu"), gunisigi=0.7, yerel=False, is_yolu=True),
              Y("Mahalle kütüphanesi", "MES_KUTUPHANE", {"A": 0, "B": 0, "C": 1}, {"A": "yok", "B": "yok", "C": "yuruyus"}, 120, "ucretli_is_okul", None, 0.3),
              Y("Spor salonu", "MES_SPOR", 0.3, HER("yuruyus"), 60, "spor", None, 0.3)]),
]
KISI = {k["kod"]: k for k in KISILER}

# Haneler: konut ve ulaşım maliyeti hane düzeyinde. "kopya": simüle edilmeyen ama ulaşımı benzer üye.
HANELER = {
    "H1": dict(ad="Emre (tek kişi)", kisi=1, m2=70, gelir_au=2.0, arac={"A": 0, "B": 0, "C": 0}, uyeler=["P1"], kopya=[], servis={}),
    "H2": dict(ad="Zeynep ve Mert", kisi=2, m2=90, gelir_au=4.6, paylasimli=True, arac={"A": 1, "B": 0, "C": 0}, uyeler=["P2a", "P2b"], kopya=[], servis={}),
    "H3": dict(ad="Ayşe, Ahmet, Elif ve 4 yaşındaki Can", kisi=4, m2=120, gelir_au=4.0, paylasimli=True, arac={"A": 2, "B": 1, "C": 0},
               uyeler=["P3a", "P3b", "P3c"], kopya=[], servis={"A": 1}),
    "H4": dict(ad="Fatma, oğlu, gelini ve iki torunu", kisi=5, m2={"A": 160, "B": 190, "C": 180}, gelir_au=3.5, mulkiyet="sahip", paylasimli=True, arac={"A": 1, "B": 1, "C": 0},
               uyeler=["P4"], kopya=["P3b"], servis={"A": 2}),
    "H5": dict(ad="Hüseyin (yalnız)", kisi=1, m2=75, gelir_au=0.8, mulkiyet="sahip", arac={"A": 0, "B": 0, "C": 0}, uyeler=["P5"], kopya=[], servis={}),
    "H6": dict(ad="Selin ve emekli annesi", kisi=2, m2=85, gelir_au=2.6, arac={"A": 1, "B": 0, "C": 0}, uyeler=["P6"], kopya=[], servis={}),
    "H7": dict(ad="Mehmet usta ve ailesi", kisi=4, m2=120, gelir_au=2.5, mulkiyet="sahip", arac={"A": 1, "B": 1, "C": 1}, uyeler=["P7"], kopya=[], servis={}),
    "H8": dict(ad="Deniz ve ailesi", kisi=4, m2=120, gelir_au=4.0, paylasimli=True, arac={"A": 1, "B": 1, "C": 0}, uyeler=["P8"], kopya=["P3b"], servis={}),
}
ZAMAN_KATEGORI = ["uyku", "kisisel_bakim_yemek", "ucretli_is_okul", "ev_isi_bakim", "ulasim_yuruyus", "ulasim_toplu", "ulasim_arac",
                  "ulasim_diger", "ibadet_cemaat", "spor", "dis_mekan_serbest", "sosyal_ziyaret", "ev_ici_serbest"]
KATEGORI_AD = {
    "uyku": "Uyku", "kisisel_bakim_yemek": "Kişisel bakım ve yemek", "ucretli_is_okul": "Ücretli iş / okul ve ders",
    "ev_isi_bakim": "Ev işi, bakım ve alışveriş", "ulasim_yuruyus": "Ulaşım: yürüme (merdiven dahil)",
    "ulasim_toplu": "Ulaşım: toplu taşıma (bekleme dahil)", "ulasim_arac": "Ulaşım: otomobil, servis, taksi",
    "ulasim_diger": "Ulaşım: asansör, park, bekleme", "ibadet_cemaat": "İbadet ve cemaat", "spor": "Spor (kapalı)",
    "dis_mekan_serbest": "Dış mekân serbest zaman", "sosyal_ziyaret": "Sosyal ziyaret, kahvehane", "ev_ici_serbest": "Ev içi serbest zaman (kalan)",
}


# =============================================================================
# 5. "BİR GÜN" MOTORU
# =============================================================================
def _deger(x, ortam, prm):
    if isinstance(x, dict):
        x = x[ortam]
    if isinstance(x, str):
        return prm(x, ortam)
    return float(x)


def _mesafe_m(hedef, ortam, prm):
    if isinstance(hedef, dict):
        hedef = hedef[ortam]
    v = prm(hedef, ortam)
    return v * 1000 if hedef.startswith("UZ_") else v


def dikey_tek_yon(kisi, ortam, prm):
    """Konuttan sokağa tek yön: (dakika, kategori)."""
    kat = kisi["kat"][ortam]
    if kat <= 0:
        return 0.3, "ulasim_yuruyus"
    if kisi["asansor"][ortam]:
        return prm("ASANSOR_DK", ortam), "ulasim_diger"
    if kisi["hiz"] == "HIZ_TEKERLEKLI":
        return float("nan"), "ulasim_diger"
    kat_dk = prm("MERDIVEN_DK_KAT_YASLI") if kisi["hiz"] in ("HIZ_YASLI_KISITLI", "HIZ_YASLI_SAGLIKLI") else prm("MERDIVEN_DK_KAT_YETISKIN")
    return kat * kat_dk, "ulasim_yuruyus"


def bacak(mod, d_m, kisi, ortam, prm, v, hedef_kodu, yerel):
    """Tek yön yolculuk. Dakikalar kategoriye göre + dış mekân + yerel yürüyüş + araç km."""
    r = defaultdict(float)
    km = d_m / 1000
    merkez = isinstance(hedef_kodu, str) and hedef_kodu in ("UZ_MERKEZ_KM", "UZ_UNIVERSITE_KM")
    if mod == "yuruyus":
        t = d_m / v
        r["ulasim_yuruyus"] += t
        r["_dis"] += t
        r["_yerel_yuruyus"] += t if yerel else 0
        r["_yuruyus_m"] += d_m
    elif mod == "toplu":
        erisim = prm("MES_DURAK", ortam) / v
        bekle = prm("BEKLEME_DK", ortam)
        hiz = prm("TOPLU_HIZ", ortam)
        ic = km / hiz * 60
        aktarma = prm("AKTARMA_DK") if km > 5 else 0.0
        varis = prm("VARIS_YURUME_DK")
        r["ulasim_yuruyus"] += erisim + varis
        r["ulasim_toplu"] += bekle + ic + aktarma
        r["_dis"] += erisim + varis + bekle + 0.5 * aktarma
        r["_yerel_yuruyus"] += erisim
        r["_yuruyus_m"] += prm("MES_DURAK", ortam) + varis * v
    elif mod == "arac":
        erisim = prm("ARAC_ERISIM_DK", ortam)
        hiz = prm("ARAC_HIZ_MERKEZ") if merkez or km > 5 else prm("ARAC_HIZ_YEREL")
        surus = km / hiz * 60
        park = prm("PARK_ARAMA_MERKEZ_DK") if merkez else prm("PARK_ARAMA_YEREL_DK")
        ev_park = 0.5 * prm("PARK_ARAMA_EV_DK", ortam)       # gidiş-dönüş ortalaması
        varis = 2.0
        if ortam == "A":
            r["ulasim_diger"] += erisim
        else:
            r["ulasim_yuruyus"] += erisim
            r["_dis"] += erisim
            r["_yerel_yuruyus"] += erisim
            r["_yuruyus_m"] += erisim * v
        r["ulasim_arac"] += surus + park + ev_park
        r["ulasim_yuruyus"] += varis
        r["_dis"] += varis
        r["_yuruyus_m"] += varis * v
        r["_arac_km"] += km
    elif mod == "servis":
        bekle = prm("SERVIS_BEKLEME_DK")
        yur = prm("MES_SERVIS_NOKTASI", "A") / v
        r["ulasim_yuruyus"] += yur
        r["ulasim_diger"] += bekle
        r["ulasim_arac"] += prm("SERVIS_DK", ortam)
        r["_dis"] += yur + bekle
        r["_yerel_yuruyus"] += yur
        r["_yuruyus_m"] += yur * v
    elif mod == "taksi":
        r["ulasim_diger"] += 8.0
        r["ulasim_arac"] += km / prm("ARAC_HIZ_YEREL") * 60
        r["_taksi"] += 1
    else:
        raise ValueError(mod)
    return r


def gun_simule(kisi: dict, ortam: str, prm: Prm) -> dict:
    zaman = defaultdict(float)
    maruz = defaultdict(float)          # karşılaşma için dakika (alan -> dk)
    ek = defaultdict(float)             # dış mekân, gün ışığı, km vb.
    for k, deg in kisi["sabit"].items():
        zaman[k] += deg[ortam] if isinstance(deg, dict) else deg
    if kisi.get("sabit_dis"):
        ek["dis"] += kisi["sabit_dis"]
        ek["gunisigi"] += kisi["sabit_dis"]
    v = prm(kisi["hiz"])
    tekerlekli = kisi["hiz"] == "HIZ_TEKERLEKLI"
    dk_dikey, kat_dikey = dikey_tek_yon(kisi, ortam, prm)
    yardim_gerekir = tekerlekli and (math.isnan(dk_dikey) or kisi.get("giris_basamak", {}).get(ortam, False))
    if math.isnan(dk_dikey):
        dk_dikey = prm("YARDIM_BEKLEME_DK")
    evden_cikis = 0.0
    is_tek_yon = 0.0
    bagimsiz, yardimli = 0.0, 0.0

    for y in kisi["yol"]:
        mod = y["mod"][ortam]
        f = _deger(y["frek"], ortam, prm)
        if mod == "yok" or f <= 0:
            continue
        hedef = y["hedef"][ortam] if isinstance(y["hedef"], dict) else y["hedef"]
        d = _mesafe_m(hedef, ortam, prm)
        yerel = y["yerel"][ortam] if isinstance(y["yerel"], dict) else y["yerel"]
        b = bacak(mod, d, kisi, ortam, prm, v, hedef, yerel)
        for kat, dk in b.items():
            if not kat.startswith("_"):
                zaman[kat] += 2 * f * dk
        ek["dis"] += 2 * f * b["_dis"]
        ek["gunisigi"] += 2 * f * b["_dis"] * y["gunisigi"]
        ek["yuruyus_m"] += 2 * f * b["_yuruyus_m"]
        ek["arac_km"] += 2 * f * b["_arac_km"]
        ek["taksi"] += 2 * f * b["_taksi"]
        maruz["SOKAK"] += 2 * f * b["_yerel_yuruyus"]
        if y["evden"]:
            evden_cikis += f * y["cikis"]
        if y["is_yolu"]:
            is_tek_yon += sum(dk for kat, dk in b.items() if not kat.startswith("_")) + (dk_dikey if y["evden"] else 0)
        if tekerlekli:
            if yardim_gerekir or mod == "taksi":
                yardimli += f
            else:
                bagimsiz += f
        kalis = _deger(y["kalis"], ortam, prm)
        if kalis > 0:
            if y["kat"]:
                zaman[y["kat"]] += f * kalis
            if y["alan"]:
                maruz[y["alan"]] += f * kalis
            kd = _deger(y["kalis_dis"], ortam, prm) if y["kalis_dis"] else 0.0
            ek["dis"] += f * kalis * kd
            ek["gunisigi"] += f * kalis * kd * y["gunisigi"]

    # Dış mekân serbest zaman ve yeşile yürüme
    L = prm(f"DIS_SERBEST_{kisi['dis_tip']}", ortam)
    if L > 0:
        frek = prm("YESIL_ZIYARET_FREK", ortam)
        yesil_m = prm("MES_YESIL", ortam)
        hiz_y = v * (0.5 if (tekerlekli and ortam == "B") else 1.0)
        t_yol = 2 * frek * yesil_m / hiz_y
        zaman["dis_mekan_serbest"] += L
        zaman["ulasim_yuruyus"] += t_yol
        ek["dis"] += L + t_yol
        ek["gunisigi"] += 0.9 * (L + t_yol)
        ek["yuruyus_m"] += 2 * frek * yesil_m
        maruz["AVLU"] += L
        maruz["SOKAK"] += t_yol
        evden_cikis += frek
        ek["doga_dk"] += L
        if tekerlekli:
            if yardim_gerekir:
                yardimli += frek
            else:
                bagimsiz += frek

    # Komşu ziyareti (büyükanne)
    if kisi["kod"] == "P4":
        z = prm("KOMSU_ZIYARET_DK", ortam)
        zaman["sosyal_ziyaret"] += z
        ek["ziyaret_dk"] += z

    # Dikey dolaşım: her evden çıkış gidiş-dönüş iki geçiş
    zaman[kat_dikey] += 2 * evden_cikis * dk_dikey
    maruz["BINA"] += 2 * evden_cikis * (dk_dikey if kat_dikey == "ulasim_diger" else dk_dikey + 0.5)

    # Kalan zaman
    toplam = sum(zaman[k] for k in ZAMAN_KATEGORI if k != "ev_ici_serbest")
    zaman["ev_ici_serbest"] = 1440 - toplam

    # Karşılaşma
    kars = 0.0
    for alan, dk in maruz.items():
        kars += dk * prm(f"LAMBDA_{alan}", ortam) * prm(f"TANIDIK_{alan}", ortam)
    if kisi["rol"] == "esnaf":
        kars += zaman["ucretli_is_okul"] * prm("ESNAF_MUSTERI_LAMBDA") * prm("ESNAF_MAHALLELI_PAY", ortam)
    kars += ek["ziyaret_dk"] / 60 * prm("ZIYARET_KISI_SAAT")

    # İbadete erişim (tek yön, dikey dahil)
    if tekerlekli and ortam == "B":
        ibadet = float("nan")          # basamak ve kaldırım: bağımsız erişilemez
    else:
        ibadet = dikey_tek_yon(kisi, ortam, prm)[0]
        if math.isnan(ibadet):
            ibadet = prm("YARDIM_BEKLEME_DK")
        ibadet += prm("MES_MESCIT", ortam) / v

    sonuc = {k: zaman[k] for k in ZAMAN_KATEGORI}
    sonuc.update(
        yurume_dk=zaman["ulasim_yuruyus"],
        yurume_km=ek["yuruyus_m"] / 1000,
        arac_dk=zaman["ulasim_arac"],
        arac_km=ek["arac_km"],
        toplu_dk=zaman["ulasim_toplu"],
        ulasim_toplam_dk=zaman["ulasim_yuruyus"] + zaman["ulasim_toplu"] + zaman["ulasim_arac"] + zaman["ulasim_diger"],
        dis_mekan_dk=ek["dis"],
        gun_isigi_dk=ek["gunisigi"],
        doga_dk=ek["doga_dk"],
        komsu_karsilasma=kars,
        ibadet_erisim_dk=ibadet,
        is_tek_yon_dk=is_tek_yon if is_tek_yon > 0 else float("nan"),
        taksi_yolculuk=ek["taksi"],
        bagimsiz_yolculuk=bagimsiz if tekerlekli else float("nan"),
        yardimli_yolculuk=yardimli if tekerlekli else float("nan"),
        evden_cikis=evden_cikis,
    )
    return sonuc


# =============================================================================
# 6. ÇOCUĞUN BAĞIMSIZ HAREKETİ, HANE MALİYETİ, TAHLİYE
# =============================================================================
def persona_tanimlari() -> pd.DataFrame:
    """Persona senaryolarını (yolculuk zinciri, sıklık, mod, kalış) şeffaflık için tabloya döker."""
    satir = []
    for k in KISILER:
        for y in k["yol"]:
            r = dict(kisi=k["kod"], persona=k["persona"], ad=k["ad"], yas=k["yas"], hane=k["hane"], yuruyus_hizi=k["hiz"],
                     dis_mekan_tipi=k["dis_tip"], amac=y["amac"],
                     hedef_parametresi=y["hedef"] if isinstance(y["hedef"], str) else "; ".join(f"{o}:{v}" for o, v in y["hedef"].items()),
                     kalis_dk=y["kalis"] if not isinstance(y["kalis"], dict) else "; ".join(f"{o}:{v}" for o, v in y["kalis"].items()),
                     kalis_kategori=y["kat"] or "", karsilasma_alani=y["alan"] or "", gun_isigi_payi=y["gunisigi"])
            for o in ORTAMLAR:
                f = y["frek"]
                r[f"frekans_{o}"] = f[o] if isinstance(f, dict) else f
                r[f"mod_{o}"] = y["mod"][o]
                r[f"konut_kati_{o}"] = k["kat"][o]
                r[f"asansor_{o}"] = "var" if k["asansor"][o] else "yok"
            satir.append(r)
    return pd.DataFrame(satir)


def cocuk_bagimsizlik(ortam, prm):
    izin = prm("COCUK_IZIN_MESAFE_M")
    hedefler = {"OKUL": prm("MES_ILKOKUL", ortam), "YESIL": prm("MES_YESIL", ortam), "BAKKAL": prm("MES_BAKKAL", ortam),
                "ARKADAS": 150.0, "MESCIT": prm("MES_MESCIT", ortam)}
    ulasilir = [h for h, m in hedefler.items() if m <= izin and prm(f"ANA_YOL_{h}", ortam) < 0.5]
    return dict(cocuk_alan_ha=prm("COCUK_ALAN_HA", ortam), cocuk_hedef_sayisi=len(ulasilir), cocuk_hedefler=", ".join(ulasilir),
                okula_yalniz=int("OKUL" in ulasilir))


def hane_maliyet(hane_kod, ortam, prm, gunler, gelir_carpani=1.0, yakit_carpani=1.0):
    """Aylık konut + ulaşım maliyeti (TL). gunler: kişi kodu -> gun_simule sonucu (aynı ortam)."""
    h = HANELER[hane_kod]
    m2 = h["m2"][ortam] if isinstance(h["m2"], dict) else h["m2"]
    kira = m2 * prm("KIRA_M2", ortam)
    aidat = m2 * prm("AIDAT_M2", ortam)
    sahip = h.get("mulkiyet") == "sahip"
    bakim = m2 * prm("KONUT_FIYAT_M2", ortam) * prm("Y_BAKIM_ORANI") / 12 if sahip else 0.0
    konut = (aidat + bakim) if sahip else (kira + aidat)
    n_arac = h["arac"][ortam]
    km_deg = prm("YAKIT_TL_L") * yakit_carpani * prm("YAKIT_L_100KM") / 100 + prm("ARAC_ASINMA_TL_KM")
    is_gunu = prm("ISGUNU_AY")
    arac_km_ay, toplu, merkez_park, taksi = 0.0, 0.0, 0.0, 0.0
    for kod in h["uyeler"] + h["kopya"]:
        k = KISI[kod]
        g = gunler[kod]
        gun = prm("ESNAF_GUN_AY") if k["rol"] == "esnaf" else (prm("OFIS_GUN_AY_SELIN") if kod == "P6" else is_gunu)
        arac_km_ay += g["arac_km"] * gun
        if g["taksi_yolculuk"] > 0:
            taksi += g["taksi_yolculuk"] * gun * prm("ERISILEBILIR_TAKSI_TL")
        # Toplu taşıma: düzenli kullanan abonman, seyrek kullanan tek biniş
        duzenli = any(y["mod"][ortam] == "toplu" and _deger(y["frek"], ortam, prm) >= 0.5 for y in k["yol"])
        seyrek = sum(_deger(y["frek"], ortam, prm) for y in k["yol"] if y["mod"][ortam] == "toplu" and _deger(y["frek"], ortam, prm) < 0.5)
        ucretsiz = k["yas"] >= 65 or kod == "P6"
        if not ucretsiz:
            if duzenli:
                toplu += prm("OGRENCI_ABONMAN_TL_AY") if k["rol"] == "öğrenci" else prm("MAVI_KART_TL_AY")
            elif seyrek > 0:
                toplu += 2 * seyrek * 30 * prm("TEK_BINIS_TL")
        if any(y["mod"][ortam] == "arac" and y["is_yolu"] and y["hedef"] == "UZ_MERKEZ_KM" for y in k["yol"]):
            merkez_park += gun * prm("MERKEZ_OTOPARK_TL_GUN")
    if n_arac > 0:
        arac_km_ay += prm("HAFTASONU_ARAC_KM_AY", ortam)
    arac_sabit = n_arac * prm("ARAC_SABIT_TL_AY")
    arac_degisken = arac_km_ay * km_deg
    otopark = n_arac * prm("OTOPARK_EV_TL_AY", ortam) + merkez_park
    servis = h["servis"].get(ortam, 0) * prm("OKUL_SERVISI_TL_AY")
    paylasimli = prm("PAYLASIMLI_ARAC_TL_AY") if (n_arac == 0 and ortam == "C" and h.get("paylasimli")) else 0.0
    ulasim = arac_sabit + arac_degisken + otopark + toplu + servis + taksi + paylasimli
    gelir = h["gelir_au"] * prm("AU_NET") * gelir_carpani
    return dict(hane=hane_kod, ortam=ortam, mulkiyet="ev sahibi" if sahip else "kiracı", m2=m2, kira_esdegeri=kira, aidat=aidat,
                sahip_bakim=bakim, konut_toplam=konut,
                arac_sayisi=n_arac, arac_km_ay=arac_km_ay, arac_sabit=arac_sabit, arac_degisken=arac_degisken, otopark=otopark,
                toplu_tasima=toplu, servis_taksi_paylasimli=servis + taksi + paylasimli, ulasim_toplam=ulasim,
                konut_ulasim_toplam=konut + ulasim, hane_geliri=gelir, yuk_orani=(konut + ulasim) / gelir)


def tahliye_dk(kisi, ortam, prm):
    """Deprem sonrası konuttan güvenli toplanma alanına (asansör kullanılamaz)."""
    kat = kisi["kat"][ortam]
    v = prm(kisi["hiz"])
    yog = prm("TAHLIYE_YOGUNLUK", ortam)
    if kisi["hiz"] == "HIZ_TEKERLEKLI":
        t = (prm("YARDIM_BEKLEME_DK") + kat * prm("TEKERLEKLI_KAT_DK") * yog) if (kat > 0 or kisi.get("giris_basamak", {}).get(ortam)) else 0.0
        if kisi.get("giris_basamak", {}).get(ortam) and kat == 0:
            t += prm("TEKERLEKLI_KAT_DK")
        v = v * (0.5 if ortam == "B" else 1.0)
    else:
        kd = prm("MERDIVEN_DK_KAT_YASLI") if kisi["hiz"] in ("HIZ_YASLI_KISITLI", "HIZ_YASLI_SAGLIKLI") else prm("MERDIVEN_DK_KAT_YETISKIN")
        t = kat * kd * yog
    return t + prm("MES_TOPLANMA", ortam) / v


def aktivite_puani(ortam, prm):
    """Sallis 2016'nın dört özelliği, 0-1 ölçeğine çevrilip ortalaması (varsayımsal çapalar)."""
    def olcek(x, alt, ust):
        return float(np.clip((x - alt) / (ust - alt), 0, 1))
    return np.mean([
        olcek(prm("NET_KONUT_YOG_1KM", ortam), prm("CAPA_YOG", "alt"), prm("CAPA_YOG", "ust")),
        olcek(prm("KAVSAK_YOG", ortam), prm("CAPA_KAVSAK", "alt"), prm("CAPA_KAVSAK", "ust")),
        olcek(prm("MES_DURAK", ortam), prm("CAPA_DURAK", "alt"), prm("CAPA_DURAK", "ust")),
        olcek(prm("PARK_SAYISI_500M", ortam), prm("CAPA_PARK", "alt"), prm("CAPA_PARK", "ust")),
    ])


def risk_sinifi(ortam, prm):
    """Uzman yargısına dayalı deprem risk rubriği (varsayım). Puan 0-9 → sınıf 1-5."""
    puan = {"A": 1, "B": 3, "C": 0}[ortam]                     # yapım dönemi ve denetim
    yuk = prm("KAT_SAYISI", ortam) * 3
    puan += 2 if yuk > 30 else (1 if yuk > 12 else 0)           # yükseklik
    puan += 1 if ortam == "B" else 0                            # zemin kat dükkân, yumuşak kat
    puan += 1 if prm("MES_TOPLANMA", ortam) > 300 else 0        # toplanma alanına uzaklık
    puan += 1 if prm("SOKAK_HW", ortam) > 1.5 else 0            # enkazla yol kapanması
    puan += 1 if prm("BINA_BASINA_DAIRE", ortam) > 30 else 0    # tek yapıda çok kişi, karar güçlüğü
    sinif = 1 if puan <= 1 else 2 if puan <= 3 else 3 if puan <= 5 else 4 if puan <= 7 else 5
    return puan, sinif


# =============================================================================
# 7. TEK ÇEKİLİŞ İÇİN BÜTÜN GÖSTERGELER
# =============================================================================
def saglik_ve_kriz(prm: Prm, gun: dict) -> dict:
    """Bir çekiliş için sağlık yansımaları (A'ya göre) ve kriz göstergeleri."""
    s = {}
    theta = prm("NEDENSEL_PAY")
    puan = {o: aktivite_puani(o, prm) for o in ORTAMLAR}
    fark = prm("SALLIS_FARK_DK_HAFTA")
    for o in ORTAMLAR:
        s[("aktivite_puani", "Ortam", o)] = puan[o]
        s[("mvpa_fark_dk_hafta", "Ortam (bütün yetişkinler)", o)] = theta * (puan[o] - puan["A"]) * fark
    # Kişi bazlı
    for k in KISILER:
        kod = k["kod"]
        a = gun["A"][kod]
        for o in ORTAMLAR:
            g = gun[o][kod]
            # Mekanik yürüme farkı (haftalık; hafta sonu iş günü yürüyüşünün %70'i varsayılır)
            s[("mekanik_yurume_fark_dk_hafta", kod, o)] = (g["yurume_dk"] - a["yurume_dk"]) * (5 + 2 * 0.7)
            if k["rol"] in ("çalışan", "esnaf", "öğrenci", "emekli", "ev"):
                d_arac_sa = (g["arac_dk"] - a["arac_dk"]) / 60
                d_km = g["yurume_km"] - a["yurume_km"]
                or_ = prm("FRANK_ARAC_SAAT_OR") ** (theta * d_arac_sa) * prm("FRANK_YURUME_KM_OR") ** (theta * d_km)
                s[("obezite_or_degisim_yuzde", kod, o)] = (or_ - 1) * 100
            if k["rol"] in ("çalışan", "esnaf") and not math.isnan(g["is_tek_yon_dk"]):
                d_tek = g["is_tek_yon_dk"] - a["is_tek_yon_dk"]
                s[("isegidis_iyi_olus_gelir_yuzde", kod, o)] = -d_tek * prm("SF_TELAFI_DK") * 100
                s[("isegidis_iyi_olus_tl_ay", kod, o)] = -d_tek * prm("SF_TELAFI_DK") * k["gelir_au"] * prm("AU_NET")
                s[("topluluk_katilimi_degisim_yuzde", kod, o)] = -d_tek / 10 * prm("PUTNAM_10DK") * 100
                s[("isegidis_tek_yon_dk", kod, o)] = g["is_tek_yon_dk"]
            # Doğa teması
            haftalik = g["doga_dk"] * (5 + 2 * prm("HAFTASONU_DIS_CARPAN"))
            s[("doga_dk_hafta", kod, o)] = haftalik
            p0 = prm("IYI_SAGLIK_TABAN")
            odds = p0 / (1 - p0)

            def p_iyi(hft):
                if hft >= prm("WHITE_ESIK_DK"):
                    od = odds * prm("WHITE_OR_SAGLIK") ** theta
                    return od / (1 + od)
                return p0
            haftalik_a = a["doga_dk"] * (5 + 2 * prm("HAFTASONU_DIS_CARPAN"))
            s[("iyi_saglik_olasiligi_fark_puan", kod, o)] = (p_iyi(haftalik) - p_iyi(haftalik_a)) * 100
    # Yaşlılarda yeşil-ölüm
    for kod in ("P4", "P5"):
        for o in ORTAMLAR:
            hr = prm("ROJAS_HR") ** (theta * (prm("NDVI_500M", o) - prm("NDVI_500M", "A")) / 0.1)
            s[("yasli_olum_riski_degisim_yuzde", kod, o)] = (hr - 1) * 100
            s[("yasli_olum_fark_binde_yil", kod, o)] = (hr - 1) * prm("YASLI_YILLIK_OLUM") * 1000
    # Miyopi (RKÇ; nedensel pay yerine taşınabilirlik payı)
    for o in ORTAMLAR:
        d_dis = gun[o]["P3c"]["gun_isigi_dk"] - gun["A"]["P3c"]["gun_isigi_dk"]
        tavan = prm("MIYOPI_TAVAN_DK")
        d_dis = float(np.clip(d_dis, -tavan, tavan))
        s[("miyopi_3yil_goreli_degisim_yuzde", "P3c", o)] = -(d_dis / 40) * prm("HE_FARK_PP") / prm("HE_TABAN") * 100 * prm("MIYOPI_TASINABILIRLIK")
        s[("cocuk_gun_isigi_dk", "P3c", o)] = gun[o]["P3c"]["gun_isigi_dk"]

    # ---- Kriz göstergeleri ----
    for o in ORTAMLAR:
        p_h = prm("AGIR_HASAR_P", o)
        s[("deprem_agir_hasarli_yapida_kisi_10bin", "Ortam", o)] = 10000 * p_h
        s[("deprem_can_kaybi_10bin", "Ortam", o)] = 10000 * p_h * prm("OLUM_AGIR_HASARDA")
        s[("deprem_tek_yapida_kisi", "Ortam", o)] = prm("BINA_BASINA_DAIRE", o) * 3.1
        for kod in ("P1", "P5", "P4", "P6"):
            s[("deprem_tahliye_dk", kod, o)] = tahliye_dk(KISI[kod], o, prm)
        s[("deprem_risk_puani", "Ortam", o)], s[("deprem_risk_sinifi", "Ortam", o)] = risk_sinifi(o, prm)
        s[("salgin_zemine_acilan_hane_yuzde", "Ortam", o)] = prm("ZEMINE_ACILAN", o) * 100
        s[("salgin_ozel_dis_m2_kisi", "Ortam", o)] = prm("OZEL_DIS_M2_KISI", o)
        s[("salgin_dikey_dolasim_paylasan_hane", "Ortam", o)] = prm("BINA_BASINA_DAIRE", o)
        s[("salgin_bakkal_yurume_dk", "P3a", o)] = prm("MES_BAKKAL", o) / prm("HIZ_YETISKIN")
        s[("salgin_bakkal_yurume_dk", "P5", o)] = prm("MES_BAKKAL", o) / prm("HIZ_YASLI_KISITLI") + dikey_tek_yon(KISI["P5"], o, prm)[0]
        s[("tanidik_karsilasma_gun", "P4", o)] = gun[o]["P4"]["komsu_karsilasma"]
        s[("sicak_agac_ortusu_yuzde", "Ortam", o)] = prm("AGAC_ORTUSU", o) * 100
        s[("sicak_serin_siginak_dk", "P5", o)] = gun[o]["P5"]["ibadet_erisim_dk"]
        e = gun[o]["P5"]["komsu_karsilasma"] * prm("SICAK_DISARI_CARPAN") * prm("YAKIN_TANIDIK_PAYI")
        s[("sicak_yasliya_24sa_temas_olasiligi", "P5", o)] = 1 - math.exp(-e)
        s[("ekonomi_havza_nufusu_300m", "Ortam", o)] = math.pi * 0.3 ** 2 * 100 * prm("BRUT_YOG_KISI_HA", o)
    # Ekonomik kriz: aile (H3) ve genç çift (H2)
    for hane, uyeler in (("H3", ["P3a", "P3b", "P3c"]), ("H2", ["P2a", "P2b"])):
        for o in ORTAMLAR:
            gunler = {kod: gun[o][kod] for kod in KISI}
            once = hane_maliyet(hane, o, prm, gunler)
            sonra = hane_maliyet(hane, o, prm, gunler, gelir_carpani=1 + prm("GELIR_SOKU"), yakit_carpani=1 + prm("YAKIT_SOKU"))
            s[("ekonomi_yuk_once_yuzde", hane, o)] = once["yuk_orani"] * 100
            s[("ekonomi_yuk_sonra_yuzde", hane, o)] = sonra["yuk_orani"] * 100
            s[("ekonomi_yakit_soku_tl_ay", hane, o)] = sonra["ulasim_toplam"] - once["ulasim_toplam"]
    for o in ORTAMLAR:
        g = gun[o]["P3b"]
        # Arabasız erişim: aynı yolculuğun toplu taşımayla süresi / araçla süresi
        kisi_t = dict(KISI["P3b"])
        kisi_t = {**kisi_t, "yol": [dict(y, mod=HER("toplu")) if y["is_yolu"] else y for y in kisi_t["yol"]]}
        kisi_a = {**KISI["P3b"], "yol": [dict(y, mod=HER("arac")) if y["is_yolu"] else y for y in KISI["P3b"]["yol"]]}
        t_toplu = gun_simule(kisi_t, o, prm)["is_tek_yon_dk"]
        t_arac = gun_simule(kisi_a, o, prm)["is_tek_yon_dk"]
        s[("ekonomi_arabasiz_sure_orani", "P3b", o)] = t_toplu / t_arac
    return s


# =============================================================================
# 8. ÇALIŞTIRMA, ÖZETLEME, YAZMA
# =============================================================================
def ozetle(dizi):
    a = np.asarray(dizi, dtype=float)
    a = a[~np.isnan(a)]
    if a.size == 0:
        return np.nan, np.nan, np.nan
    return float(np.median(a)), float(np.percentile(a, 5)), float(np.percentile(a, 95))


GOSTERGE_AD = {
    "yurume_dk": "Yürüme (dk/gün)", "yurume_km": "Yürüme (km/gün)", "arac_dk": "Otomobil, servis, taksi (dk/gün)",
    "arac_km": "Araç kilometresi (km/gün)", "toplu_dk": "Toplu taşıma (dk/gün)", "ulasim_toplam_dk": "Toplam ulaşım (dk/gün)",
    "dis_mekan_dk": "Dış mekân (dk/gün)", "gun_isigi_dk": "Gün ışığında dış mekân (dk/gün)", "doga_dk": "Doğa / yeşil teması (dk/gün)",
    "komsu_karsilasma": "Tanıdık komşuyla karşılaşma (beklenen, /gün)", "ibadet_erisim_dk": "En yakın mescide tek yön (dk)",
    "is_tek_yon_dk": "İşe / okula tek yön (dk)", "ev_ici_serbest": "Ev içi serbest zaman (dk/gün)",
    "bagimsiz_yolculuk": "Bağımsız yapılabilen yolculuk (/gün)",
}


def _utf8_konsol():
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def calistir():
    _utf8_konsol()
    print("Varsayım tablosu yazılıyor...")
    vt = varsayim_tablosu()
    vt.to_csv(KOK / "varsayimlar.csv", index=False, encoding="utf-8")
    print(f"  {len(vt)} satır, {vt.parametre_kodu.nunique()} parametre")

    # ---- 8.1 Temel senaryo: zaman bütçesi ve göstergeler ----
    p0 = Prm()
    gun0 = {o: {k["kod"]: gun_simule(k, o, p0) for k in KISILER} for o in ORTAMLAR}
    satir = []
    for k in KISILER:
        for o in ORTAMLAR:
            g = gun0[o][k["kod"]]
            r = dict(kisi=k["kod"], persona=k["persona"], ad=k["ad"], ortam=o)
            r.update({c: round(g[c], 1) for c in ZAMAN_KATEGORI})
            r["toplam_dk"] = round(sum(g[c] for c in ZAMAN_KATEGORI), 1)
            satir.append(r)
    zb = pd.DataFrame(satir)
    assert (zb.toplam_dk.round(0) == 1440).all(), "Zaman bütçesi 1440 dakikaya eşit değil"
    assert (zb.ev_ici_serbest >= 0).all(), "Temel senaryoda negatif serbest zaman"
    zb.to_csv(SONUC / "persona_zaman_butcesi.csv", index=False, encoding="utf-8")
    persona_tanimlari().to_csv(SONUC / "persona_yolculuk_tanimlari.csv", index=False, encoding="utf-8")

    # ---- 8.2 Monte Carlo ----
    print(f"Monte Carlo ({N_MC} çekiliş)...")
    cek = ornekle(N_MC)
    mc_gun = defaultdict(list)
    mc_s = defaultdict(list)
    mc_maliyet = defaultdict(list)
    mc_cocuk = defaultdict(list)
    for i in range(N_MC):
        p = Prm(cek, i)
        gun = {o: {k["kod"]: gun_simule(k, o, p) for k in KISILER} for o in ORTAMLAR}
        for o in ORTAMLAR:
            for kod, g in gun[o].items():
                for c in GOSTERGE_AD:
                    mc_gun[(kod, o, c)].append(g[c])
            for hk in HANELER:
                m = hane_maliyet(hk, o, p, gun[o])
                for c in ("konut_toplam", "ulasim_toplam", "konut_ulasim_toplam", "yuk_orani"):
                    mc_maliyet[(hk, o, c)].append(m[c])
            cb = cocuk_bagimsizlik(o, p)
            mc_cocuk[(o, "cocuk_alan_ha")].append(cb["cocuk_alan_ha"])
            mc_cocuk[(o, "cocuk_hedef_sayisi")].append(cb["cocuk_hedef_sayisi"])
        for anahtar, deger in saglik_ve_kriz(p, gun).items():
            mc_s[anahtar].append(deger)

    # ---- 8.3 Persona göstergeleri tablosu (temel + MC aralığı) ----
    maliyet0 = {(hk, o): hane_maliyet(hk, o, p0, gun0[o]) for hk in HANELER for o in ORTAMLAR}
    cocuk0 = {o: cocuk_bagimsizlik(o, p0) for o in ORTAMLAR}
    satir = []
    for k in KISILER:
        for o in ORTAMLAR:
            g = gun0[o][k["kod"]]
            r = dict(kisi=k["kod"], persona=k["persona"], ad=k["ad"], ortam=o)
            for c in GOSTERGE_AD:
                med, p5, p95 = ozetle(mc_gun[(k["kod"], o, c)])
                r[c] = round(g[c], 2) if not (isinstance(g[c], float) and math.isnan(g[c])) else np.nan
                r[c + "_p5"] = round(p5, 2) if not math.isnan(p5) else np.nan
                r[c + "_p95"] = round(p95, 2) if not math.isnan(p95) else np.nan
            if k["kod"] == "P3c":
                r["cocuk_alan_ha"] = cocuk0[o]["cocuk_alan_ha"]
                r["cocuk_hedef_sayisi_5te"] = cocuk0[o]["cocuk_hedef_sayisi"]
                r["cocuk_yalniz_ulasilan"] = cocuk0[o]["cocuk_hedefler"]
                r["okula_yalniz"] = "evet" if cocuk0[o]["okula_yalniz"] else "hayır"
            m = maliyet0[(k["hane"], o)]
            r["hane"] = k["hane"]
            r["hane_konut_tl_ay"] = round(m["konut_toplam"])
            r["hane_ulasim_tl_ay"] = round(m["ulasim_toplam"])
            r["hane_konut_ulasim_tl_ay"] = round(m["konut_ulasim_toplam"])
            r["hane_yuk_orani_yuzde"] = round(m["yuk_orani"] * 100, 1)
            r["deprem_risk_sinifi"] = risk_sinifi(o, p0)[1]
            r["deprem_tahliye_dk"] = round(tahliye_dk(k, o, p0), 1)
            satir.append(r)
    pg = pd.DataFrame(satir)
    pg.to_csv(SONUC / "persona_gostergeler.csv", index=False, encoding="utf-8")

    # ---- 8.4 Hane maliyetleri ----
    satir = []
    for hk in HANELER:
        for o in ORTAMLAR:
            m = {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in maliyet0[(hk, o)].items()}
            m["hane_ad"] = HANELER[hk]["ad"]
            for c in ("konut_ulasim_toplam", "yuk_orani"):
                med, p5, p95 = ozetle(mc_maliyet[(hk, o, c)])
                m[c + "_p5"], m[c + "_p95"] = round(p5, 3), round(p95, 3)
            satir.append(m)
    hm = pd.DataFrame(satir)
    hm.to_csv(SONUC / "hane_aylik_maliyet.csv", index=False, encoding="utf-8")

    # ---- 8.5 Duyarlılık: C çeperde; C'de araç tutulursa ----
    satir = []
    ceper = {("UZ_MERKEZ_KM", "C"): 22.0, ("UZ_SEMT_KM", "C"): 6.0, ("UZ_UNIVERSITE_KM", "C"): 25.0,
             ("TOPLU_HIZ", "C"): PARAM[("RAYLI_HIZ_CEPER", "ortak")][0], ("KIRA_M2", "C"): 360.0}
    p_ceper = p0.degistir(ceper)
    gun_ceper = {k["kod"]: gun_simule(k, "C", p_ceper) for k in KISILER}
    for k in KISILER:
        if k["rol"] in ("çalışan", "öğrenci", "esnaf"):
            satir.append(dict(senaryo="C-çeper (merkeze 22 km, raylı sistem 32 km/sa, kira 360 TL/m²)", kisi=k["kod"], ad=k["ad"],
                              gosterge="İşe / okula tek yön (dk)", A=round(gun0["A"][k["kod"]]["is_tek_yon_dk"], 1),
                              B=round(gun0["B"][k["kod"]]["is_tek_yon_dk"], 1), C_temel=round(gun0["C"][k["kod"]]["is_tek_yon_dk"], 1),
                              C_duyarlilik=round(gun_ceper[k["kod"]]["is_tek_yon_dk"], 1)))
    for hk in ("H2", "H3", "H8"):
        m_c = hane_maliyet(hk, "C", p_ceper, gun_ceper)
        satir.append(dict(senaryo="C-çeper (merkeze 22 km, raylı sistem 32 km/sa, kira 360 TL/m²)", kisi=hk, ad=HANELER[hk]["ad"],
                          gosterge="Konut + ulaşım (TL/ay)", A=round(maliyet0[(hk, "A")]["konut_ulasim_toplam"]),
                          B=round(maliyet0[(hk, "B")]["konut_ulasim_toplam"]), C_temel=round(maliyet0[(hk, "C")]["konut_ulasim_toplam"]),
                          C_duyarlilik=round(m_c["konut_ulasim_toplam"])))
    # C'de araç tutulursa
    for hk in ("H2", "H3", "H8"):
        h_eski = HANELER[hk]["arac"]["C"]
        HANELER[hk]["arac"]["C"] = 1
        m_c = hane_maliyet(hk, "C", p0, gun0["C"])
        HANELER[hk]["arac"]["C"] = h_eski
        satir.append(dict(senaryo="C'de hane bir araç tutarsa (araç işe kullanılmaz)", kisi=hk, ad=HANELER[hk]["ad"],
                          gosterge="Konut + ulaşım (TL/ay)", A=round(maliyet0[(hk, "A")]["konut_ulasim_toplam"]),
                          B=round(maliyet0[(hk, "B")]["konut_ulasim_toplam"]), C_temel=round(maliyet0[(hk, "C")]["konut_ulasim_toplam"]),
                          C_duyarlilik=round(m_c["konut_ulasim_toplam"])))
    pd.DataFrame(satir).to_csv(SONUC / "duyarlilik_c.csv", index=False, encoding="utf-8")

    # ---- 8.6 Sağlık ve kriz özet tabloları ----
    saglik_kaynak = {
        "aktivite_puani": ("Aktivite dostu mahalle puanı (0-1)", "puan", K["SALLIS"] + " özellikleri; çapalar varsayım", "Orta (kesitsel)"),
        "mvpa_fark_dk_hafta": ("Orta-şiddetli aktivite farkı, A'ya göre (Sallis sınırlı, nedensel pay uygulanmış)", "dk/hafta", K["SALLIS"], "Orta (kesitsel)"),
        "mekanik_yurume_fark_dk_hafta": ("Zaman bütçesindeki ulaşım yürüyüşü farkı, A'ya göre (sınırsız, mekanik)", "dk/hafta", "Bu çalışma [H]", "—"),
        "obezite_or_degisim_yuzde": ("Obezite olasılığında göreli değişim, A'ya göre", "%", K["FRANK"], "Orta (kesitsel)"),
        "isegidis_iyi_olus_gelir_yuzde": ("İşe gidiş süresinin iyi oluş eşdeğeri, A'ya göre (+ kazanç)", "aylık gelirin %'si", K["SF"], "Orta (panel)"),
        "isegidis_iyi_olus_tl_ay": ("İşe gidiş süresinin iyi oluş eşdeğeri, A'ya göre (+ kazanç)", "TL/ay", K["SF"], "Orta (panel)"),
        "topluluk_katilimi_degisim_yuzde": ("Topluluk katılımında değişim, A'ya göre", "%", K["PUTNAM"], "Orta-zayıf (ikincil)"),
        "isegidis_tek_yon_dk": ("İşe tek yön süre", "dk", "Bu çalışma [H]", "—"),
        "doga_dk_hafta": ("Haftalık doğa / yeşil teması", "dk/hafta", "Bu çalışma [H]", "—"),
        "iyi_saglik_olasiligi_fark_puan": ("'İyi sağlık' beyan olasılığı farkı, A'ya göre (≥120 dk/hafta eşiği)", "yüzde puan", K["WHITE"], "Orta-zayıf (kesitsel)"),
        "yasli_olum_riski_degisim_yuzde": ("Yıllık ölüm riskinde göreli değişim, A'ya göre (yeşil)", "%", K["ROJAS"], "Orta-güçlü (korelasyonel)"),
        "yasli_olum_fark_binde_yil": ("Yıllık ölüm farkı, A'ya göre (yeşil)", "binde/yıl", K["ROJAS"], "Orta-güçlü (korelasyonel)"),
        "miyopi_3yil_goreli_degisim_yuzde": ("3 yıllık miyopi insidansında göreli değişim, A'ya göre", "%", K["HE"], "Güçlü (RKÇ)"),
        "cocuk_gun_isigi_dk": ("Çocuğun gün ışığında dış mekân süresi", "dk/gün", "Bu çalışma [H]", "—"),
    }
    satir = []
    for (gost, kisi, o), dizi in mc_s.items():
        if gost not in saglik_kaynak:
            continue
        med, p5, p95 = ozetle(dizi)
        ad, birim, kaynak, guc = saglik_kaynak[gost]
        satir.append(dict(gosterge=gost, aciklama=ad, kisi=kisi, kisi_ad=KISI[kisi]["ad"] if kisi in KISI else kisi, ortam=o,
                          birim=birim, medyan=round(med, 3), p5=round(p5, 3), p95=round(p95, 3), kaynak=kaynak, kanit_gucu=guc))
    sg = pd.DataFrame(satir)
    sg.to_csv(SONUC / "saglik_iyi_olus.csv", index=False, encoding="utf-8")

    kriz_tanim = {
        "deprem_agir_hasarli_yapida_kisi_10bin": ("Deprem", "Ağır hasarlı / yıkık yapıda kalan kişi (10.000 sakinde)", "kişi", "düşük iyi"),
        "deprem_can_kaybi_10bin": ("Deprem", "Beklenen can kaybı (10.000 sakinde, senaryo)", "kişi", "düşük iyi"),
        "deprem_tek_yapida_kisi": ("Deprem", "Tek yapıda yaşayan kişi (bir göçmede etkilenen)", "kişi", "düşük iyi"),
        "deprem_tahliye_dk": ("Deprem", "Konuttan güvenli toplanma alanına tahliye", "dk", "düşük iyi"),
        "deprem_risk_puani": ("Deprem", "Risk rubriği puanı (0-9, varsayım)", "puan", "düşük iyi"),
        "deprem_risk_sinifi": ("Deprem", "Deprem risk sınıfı (1 düşük – 5 çok yüksek)", "sınıf", "düşük iyi"),
        "salgin_zemine_acilan_hane_yuzde": ("Salgın", "Zemine / avluya doğrudan açılan hane", "%", "yüksek iyi"),
        "salgin_ozel_dis_m2_kisi": ("Salgın", "Kişi başı özel bahçe / avlu", "m²/kişi", "yüksek iyi"),
        "salgin_dikey_dolasim_paylasan_hane": ("Salgın", "Aynı asansör / merdiveni paylaşan hane", "hane", "düşük iyi"),
        "salgin_bakkal_yurume_dk": ("Salgın", "Bakkala tek yön yürüme (merdiven/asansör dahil)", "dk", "düşük iyi"),
        "tanidik_karsilasma_gun": ("Salgın", "Büyükannenin günlük tanıdık komşu teması (yardımlaşma kapasitesi)", "kişi/gün", "yüksek iyi"),
        "sicak_agac_ortusu_yuzde": ("Sıcak dalgası", "Ağaç örtüsü (başlangıç; C hedefi %30)", "%", "yüksek iyi"),
        "sicak_serin_siginak_dk": ("Sıcak dalgası", "Yalnız yaşlının en yakın serin kamusal yere (mescit) tek yön", "dk", "düşük iyi"),
        "sicak_yasliya_24sa_temas_olasiligi": ("Sıcak dalgası", "Yalnız yaşlının yokluğunun 24 saat içinde bir yakın tanıdıkça fark edilme olasılığı", "oran", "yüksek iyi"),
        "ekonomi_yuk_once_yuzde": ("Ekonomik kriz", "Konut + ulaşım / hane geliri, şok öncesi", "%", "düşük iyi"),
        "ekonomi_yuk_sonra_yuzde": ("Ekonomik kriz", "Konut + ulaşım / hane geliri, şok sonrası (gelir −%20, yakıt +%50)", "%", "düşük iyi"),
        "ekonomi_yakit_soku_tl_ay": ("Ekonomik kriz", "Yakıt şokunun aylık ek maliyeti", "TL/ay", "düşük iyi"),
        "ekonomi_havza_nufusu_300m": ("Ekonomik kriz", "Esnafın 300 m yürüme havzasındaki nüfus", "kişi", "yüksek iyi"),
        "ekonomi_arabasiz_sure_orani": ("Ekonomik kriz", "Arabasız yaşanabilirlik: işe toplu taşıma süresi / araç süresi", "kat", "düşük iyi"),
    }
    satir = []
    for (gost, kisi, o), dizi in mc_s.items():
        if gost not in kriz_tanim:
            continue
        med, p5, p95 = ozetle(dizi)
        kriz, ad, birim, yon = kriz_tanim[gost]
        satir.append(dict(kriz=kriz, gosterge=gost, aciklama=ad, kisi=kisi, kisi_ad=KISI[kisi]["ad"] if kisi in KISI else HANELER.get(kisi, {}).get("ad", kisi),
                          ortam=o, birim=birim, yon=yon, medyan=round(med, 3), p5=round(p5, 3), p95=round(p95, 3)))
    kz = pd.DataFrame(satir)
    kz.to_csv(SONUC / "kriz_senaryolari.csv", index=False, encoding="utf-8")

    # Çocuk göstergeleri MC
    satir = []
    for o in ORTAMLAR:
        for c in ("cocuk_alan_ha", "cocuk_hedef_sayisi"):
            med, p5, p95 = ozetle(mc_cocuk[(o, c)])
            satir.append(dict(ortam=o, gosterge=c, temel=cocuk0[o][c], medyan=med, p5=p5, p95=p95,
                              yalniz_ulasilan_temel=cocuk0[o]["cocuk_hedefler"]))
    pd.DataFrame(satir).to_csv(SONUC / "cocuk_bagimsiz_hareket.csv", index=False, encoding="utf-8")

    # Sağlama: ortalama ulaşım süresi TÜİK ile kıyas
    ort = zb.assign(ulasim=zb.ulasim_yuruyus + zb.ulasim_toplu + zb.ulasim_arac + zb.ulasim_diger).groupby("ortam").ulasim.mean()
    print("  Personaların ortalama günlük ulaşım süresi (dk):", ort.round(0).to_dict(), "| TÜİK ZKA 2025 Türkiye ortalaması 61 dk")

    grafikler(pg, sg, kz, mc_s)
    return pg, sg, kz


# =============================================================================
# 9. GRAFİKLER
# =============================================================================
MAVI, TURUNCU, AQUA, SARI = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
RENK = {"A": MAVI, "B": TURUNCU, "C": AQUA}
YAZI, YAZI_2, IZGARA, ZEMIN = "#0b0b0b", "#52514e", "#e4e2dd", "#fcfcfb"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": IZGARA, "axes.labelcolor": YAZI_2,
    "axes.titlecolor": YAZI, "xtick.color": YAZI_2, "ytick.color": YAZI_2, "axes.facecolor": ZEMIN,
    "figure.facecolor": ZEMIN, "savefig.facecolor": ZEMIN, "svg.fonttype": "none",
})


def tr(x, d=0):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    if abs(x) < 0.5 * 10 ** -d:
        x = 0.0
    s = f"{x:,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return "−" + s[1:] if s.startswith("-") else s


def tr_eksen(ax, eksen="x", d=None):
    """Türkçe sayı biçimli eksen; d=None ise tamsayı olmayan işaretlerde 1 ondalık."""
    from matplotlib.ticker import FuncFormatter

    def _f(v, _):
        if d is None:
            return tr(v, 0 if abs(v - round(v)) < 1e-9 else 1)
        return tr(v, d)
    fmt = FuncFormatter(_f)
    (ax.xaxis if eksen == "x" else ax.yaxis).set_major_formatter(fmt)


def sade(ax, izgara="x"):
    for k in ("top", "right", "left"):
        ax.spines[k].set_visible(False)
    ax.spines["bottom"].set_color(IZGARA)
    ax.tick_params(length=0)
    ax.grid(axis=izgara, color=IZGARA, lw=0.6)
    ax.set_axisbelow(True)


def kaydet(fig, ad):
    for uz in ("png", "svg"):
        fig.savefig(GRAFIK / f"{ad}.{uz}", dpi=170 if uz == "png" else None, bbox_inches="tight")
    plt.close(fig)


def gosterge_lejant(fig, y=0.985, ekler=()):
    from matplotlib.lines import Line2D
    ogeler = [Line2D([0], [0], marker="o", color="none", markerfacecolor=RENK[o], markeredgecolor=ZEMIN, markersize=8, label=ORTAM_AD[o])
              for o in ORTAMLAR] + list(ekler)
    fig.legend(handles=ogeler, loc="upper left", bbox_to_anchor=(0.012, y), ncol=len(ogeler), frameon=False, fontsize=9,
               handletextpad=0.3, columnspacing=1.6)


def grafikler(pg, sg, kz, mc_s):
    # ---- Grafik 1: persona göstergeleri (nokta grafiği, 90% aralık çizgileri) ----
    paneller = [("yurume_dk", "Yürüme", "dk/gün"), ("arac_dk", "Otomobil, servis, taksi", "dk/gün"),
                ("gun_isigi_dk", "Gün ışığında dış mekân", "dk/gün"), ("komsu_karsilasma", "Tanıdık komşuyla karşılaşma", "beklenen, /gün")]
    kisiler = [k["kod"] for k in KISILER]
    etiket = {k["kod"]: f"{k['ad'].split(' (')[0]} · {k['persona'].lower()}" for k in KISILER}
    etiket["P3c"] = "Elif (8) · iki çocuklu aile"
    fig, eks = plt.subplots(1, 4, figsize=(15, 6.4), sharey=True)
    ofset = {"A": -0.22, "B": 0.0, "C": 0.22}
    for ax, (c, baslik, birim) in zip(eks, paneller):
        for j, kod in enumerate(kisiler):
            for o in ORTAMLAR:
                r = pg[(pg.kisi == kod) & (pg.ortam == o)].iloc[0]
                y = j + ofset[o]
                ax.plot([r[c + "_p5"], r[c + "_p95"]], [y, y], color=RENK[o], lw=1.2, alpha=0.45, solid_capstyle="round")
                ax.plot(r[c], y, "o", color=RENK[o], ms=6.5, mec=ZEMIN, mew=1.2, zorder=3)
        ax.set_title(baslik, loc="left", fontsize=10.5, fontweight="bold", pad=16)
        ax.text(0, 1.012, birim + " · nokta: temel, çizgi: %90 aralık", transform=ax.transAxes, fontsize=7.8, color=YAZI_2, va="bottom")
        sade(ax)
        ax.set_xlim(left=0)
        tr_eksen(ax, "x", 0)
        for j in range(len(kisiler)):
            if j % 2 == 0:
                ax.axhspan(j - 0.5, j + 0.5, color="#f3f2ee", zorder=0, lw=0)
    eks[0].set_yticks(range(len(kisiler)))
    eks[0].set_yticklabels([etiket[k] for k in kisiler], fontsize=8.6, color=YAZI)
    eks[0].set_ylim(len(kisiler) - 0.5, -0.5)
    fig.suptitle("Aynı insan, üç ortam: bir iş gününün göstergeleri (senaryo, 2026)", x=0.012, ha="left", y=0.995,
                 fontsize=12.5, fontweight="bold", color=YAZI)
    gosterge_lejant(fig, y=0.955)
    fig.text(0.012, -0.035, "Kaynak: 06_SIMULASYON/kod/persona_simulasyonu.py; parametreler 06_SIMULASYON/varsayimlar.csv. "
             "Karşılaşma modeli kalibre edilmemiş varsayımdır (yön literatürden, büyüklük varsayım).", fontsize=7.6, color=YAZI_2)
    fig.subplots_adjust(wspace=0.12, top=0.84)
    kaydet(fig, "persona_gostergeler")

    # ---- Grafik 2: sağlık yansımaları (orman grafiği; B−A ve C−A) ----
    secim = [
        ("mvpa_fark_dk_hafta", "Ortam (bütün yetişkinler)", "Haftalık orta-şiddetli aktivite", "dk/hafta (Sallis ile sınırlı)", 0),
        ("obezite_or_degisim_yuzde", "P3b", "Obezite olasılığı · baba", "% değişim (Frank 2004)", 1),
        ("isegidis_iyi_olus_gelir_yuzde", "P3b", "İşe gidişin iyi oluş eşdeğeri · baba", "aylık gelirin %'si (Stutzer-Frey)", 1),
        ("miyopi_3yil_goreli_degisim_yuzde", "P3c", "3 yıllık miyopi riski · 8 yaş", "% göreli değişim (He 2015, RKÇ)", 0),
        ("iyi_saglik_olasiligi_fark_puan", "P3b", "'İyi sağlık' beyanı · baba", "yüzde puan (≥120 dk/hafta doğa; White 2019)", 1),
        ("yasli_olum_riski_degisim_yuzde", "P5", "Yıllık ölüm riski · yalnız yaşlı", "% değişim (Rojas-Rueda 2019)", 1),
    ]
    fig, eks = plt.subplots(2, 3, figsize=(14, 6.6))
    for ax, (g, kisi, baslik, birim, d) in zip(eks.flat, secim):
        for j, o in enumerate(["B", "C"]):
            r = sg[(sg.gosterge == g) & (sg.kisi == kisi) & (sg.ortam == o)].iloc[0]
            ax.plot([r.p5, r.p95], [j, j], color=RENK[o], lw=2.2, solid_capstyle="round", alpha=0.55)
            ax.plot(r.medyan, j, "o", color=RENK[o], ms=8, mec=ZEMIN, mew=1.4, zorder=3)
            ax.annotate(f"{tr(r.medyan, d)}  ({tr(r.p5, d)} / {tr(r.p95, d)})", (r.medyan, j), xytext=(0, 9),
                        textcoords="offset points", ha="center", fontsize=8.2, color=YAZI)
        ax.axvline(0, color="#8a8985", lw=0.9)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["B − A", "C − A"], fontsize=9, color=YAZI)
        ax.set_ylim(1.7, -0.7)
        ax.set_title(baslik, loc="left", fontsize=10, fontweight="bold", pad=15)
        ax.text(0, 1.015, birim, transform=ax.transAxes, fontsize=7.8, color=YAZI_2, va="bottom")
        sade(ax)
        lo = min(sg[(sg.gosterge == g) & (sg.kisi == kisi) & (sg.ortam.isin(["B", "C"]))].p5.min(), 0)
        hi = max(sg[(sg.gosterge == g) & (sg.kisi == kisi) & (sg.ortam.isin(["B", "C"]))].p95.max(), 0)
        pad = (hi - lo) * 0.18 + 1e-9
        ax.set_xlim(lo - pad, hi + pad)
        tr_eksen(ax, "x", None)
    fig.suptitle("Sağlık ve iyi oluş yansıması: A'ya (kapalı site) göre fark, medyan ve %90 aralık (Monte Carlo, 2.000 çekiliş)",
                 x=0.012, ha="left", y=1.035, fontsize=12, fontweight="bold", color=YAZI)
    fig.text(0.012, 0.985, "Gözlemsel katsayılara nedensel pay (0,25-1,0) uygulandı; miyopi katsayısı randomize deneyden. Sıfır çizgisinin solu/sağı göstergeye göre iyi ya da kötü olabilir.",
             fontsize=8, color=YAZI_2)
    fig.text(0.012, -0.03, "Kaynak: 06_SIMULASYON/sonuclar/saglik_iyi_olus.csv; katsayılar 02_LITERATUR/literatur_haritasi.md.", fontsize=7.6, color=YAZI_2)
    fig.subplots_adjust(hspace=0.75, wspace=0.28, top=0.88)
    kaydet(fig, "saglik_iyi_olus")

    # ---- Grafik 4: kriz dayanıklılığı (küçük çoklu yatay çubuk) ----
    secim = [
        ("deprem_can_kaybi_10bin", "Ortam", "Deprem: beklenen can kaybı", "10.000 sakinde (senaryo; varsayımsal hasar olasılığı)", 0, True),
        ("deprem_tahliye_dk", "P5", "Deprem: yalnız yaşlının tahliyesi", "dk, toplanma alanına (asansör yok)", 0, True),
        ("salgin_zemine_acilan_hane_yuzde", "Ortam", "Salgın: zemine / avluya açılan hane", "%", 0, False),
        ("sicak_yasliya_24sa_temas_olasiligi", "P5", "Sıcak dalgası: yalnız yaşlının fark edilmesi", "yokluğunun 24 saatte fark edilme olasılığı, %", 0, True),
        ("ekonomi_yuk_sonra_yuzde", "H3", "Ekonomik kriz: aile bütçesi", "konut + ulaşım / gelir, %, şok sonrası", 0, True),
        ("ekonomi_havza_nufusu_300m", "Ortam", "Ekonomik kriz: esnafın havzası", "300 m yürüme havzasındaki nüfus, kişi", 0, True),
    ]
    fig, eks = plt.subplots(2, 3, figsize=(14, 6.2))
    for ax, (g, kisi, baslik, birim, d, aralik) in zip(eks.flat, secim):
        vals = []
        for j, o in enumerate(ORTAMLAR):
            r = kz[(kz.gosterge == g) & (kz.kisi == kisi) & (kz.ortam == o)].iloc[0].copy()
            if g == "sicak_yasliya_24sa_temas_olasiligi":
                r[["medyan", "p5", "p95"]] = r[["medyan", "p5", "p95"]].astype(float) * 100
            vals.append(r)
            ax.barh(j, r.medyan, height=0.56, color=RENK[o], edgecolor=ZEMIN, linewidth=2)
            if aralik and r.p95 > r.p5:
                ax.plot([r.p5, r.p95], [j, j], color=YAZI_2, lw=1.0, alpha=0.8)
        xmax = max(max(r.p95 for r in vals), max(r.medyan for r in vals))
        for j, r in enumerate(vals):
            x_et = max(r.p95 if aralik else r.medyan, r.medyan) + xmax * 0.03
            ax.text(x_et, j, tr(r.medyan, d), va="center", fontsize=8.8, color=YAZI, fontweight="bold")
        ax.set_yticks(range(3))
        ax.set_yticklabels([ORTAM_AD[o] for o in ORTAMLAR], fontsize=8.6, color=YAZI)
        ax.set_ylim(2.6, -0.6)
        ax.set_xlim(0, xmax * 1.25)
        ax.set_title(baslik, loc="left", fontsize=10, fontweight="bold", pad=15)
        ax.text(0, 1.015, birim, transform=ax.transAxes, fontsize=7.8, color=YAZI_2, va="bottom")
        sade(ax)
        tr_eksen(ax, "x", 0)
    fig.suptitle("Kriz senaryolarında mahalle dayanıklılığı (medyan; ince çizgi %90 aralık)", x=0.012, ha="left", y=1.02,
                 fontsize=12, fontweight="bold", color=YAZI)
    fig.text(0.012, -0.03, "Kaynak: 06_SIMULASYON/sonuclar/kriz_senaryolari.csv. Hasar olasılıkları ve karşılaşma oranları varsayımdır; sınıflama değil büyüklük sırası olarak okunmalı.",
             fontsize=7.6, color=YAZI_2)
    fig.subplots_adjust(hspace=0.7, wspace=0.55, top=0.9)
    kaydet(fig, "kriz_dayaniklilik")


if __name__ == "__main__":
    import sys
    sys.dont_write_bytecode = True   # kod klasörüne __pycache__ yazılmasın
    calistir()
    import yasam_dongusu   # noqa: E402  (aynı klasör)
    yasam_dongusu.calistir()
