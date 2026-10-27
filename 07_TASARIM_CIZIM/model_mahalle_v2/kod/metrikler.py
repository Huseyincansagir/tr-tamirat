"""
Model mahalle v2.1 — sayısal doğrulama
======================================
v2.1: metrikler.csv'de v1, v2.0 (MM_SURUM=2.0 ile ayrı süreçte aynı koddan) ve v2.1 sütunları; ayrıca geleneksel
doku ölçütleri (morfoloji_v2.py, 03_VERI/kod/morfoloji_olcum.py fonksiyonlarıyla) ve FUE konumu (E, Ç;
05_ANALIZ/kod/fue_model_mahalle.py ile aynı kural, salt okunur girdiler).

plan_modeli.py'nin poligonlarından ve yaya ağından bütün göstergeleri hesaplar, hedeflerle
(tasarim_parametreleri.md §9 ve güncel MPYY EK-2) karşılaştırır ve ../metrikler.csv'ye yazar.
Her satırda v1 değeri de vardır (v1'in metrikler.csv'sinden; v1'de olmayan göstergeler için v1
geometrisine v2 yöntemi uygulanır: v1_okuyucu.py).

Çalıştırma:  python metrikler.py
"""

import csv
import math
import os
import pickle
import statistics
import subprocess
import sys
import tempfile
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import networkx as nx
from shapely.geometry import Point
from shapely.ops import unary_union

import plan_modeli as pm
import tipoloji_verisi as tv
import v1_okuyucu as v1
from ortak import ARALIK_ACI, CIKTI, HANE_BUYUKLUGU, KAT_YUK, ZEMIN_TICARI_YUK, sayi, yuzde

HA = 10_000.0
OGRENCI_PAYI = 0.06          # 6–9 yaş / nüfus, aile odaklı yaş yapısı varsayımı (§9.2) [V]
DERSLIK_MEVCUT = 28          # öğrenci / derslik [V]

# Erişim hedefleri: (tür, etiket, hedef m, MPYY / dış ölçüt m, kaynak)
ERISIM = [
    ("ilkokul", "İlkokul", 500, 500, "§6.1 / MPYY md. 12"),
    ("ortaokul", "Ortaokul", 1000, 1000, "§6.1 / MPYY md. 12"),
    ("anaokulu", "Anaokulu", 400, 500, "§6.1 (Perry) / MPYY md. 12"),
    ("anaokulu_kres", "Anaokulu ya da kreş", 400, 500, "§9.5"),
    ("mescit", "Mescit", 150, 150, "§6.1 / MPYY md. 12"),
    ("kucuk_cami", "Küçük cami", 250, 250, "§6.1 / MPYY md. 12"),
    ("semt_camii", "Semt camii", 400, 400, "§6.1 / MPYY md. 12"),
    ("asm", "Aile sağlık merkezi", 500, 500, "§6.1 / MPYY md. 12"),
    ("yesil05", "≥ 0,5 ha kamusal yeşil", 200, 300, "§5 (hedef 200 m; DSÖ 300 m)"),
    ("merkez_parki", "Merkez parkı (2 ha)", 500, 800, "§5 (≤ 500–800 m'de ≥ 2 ha)"),
    ("oyun", "Oyun alanı / cep parkı", 150, 500, "§9.5 (150 m) / MPYY 500 m"),
    ("spor", "Açık semt spor alanı (0,5 ha)", 500, 500, "§6.1 / MPYY md. 12"),
    ("spor_saha", "Herhangi bir açık spor sahası", 500, 500, "§6.1 / MPYY md. 12"),
    ("durak", "Otobüs durağı", 300, 400, "§6.1 (300–400 m)"),
    ("dukkan", "Bakkal, fırın ya da dükkân", 300, 300, "§6.1 (200–300 m)"),
    ("meydan", "Meydan ve çarşı", 400, 500, "§9.5"),
    ("konak", "Mahalle konağı", 500, 500, "§6.1"),
    ("otopark", "Bölgesel otopark", 400, 400, "§9.5 (300–400 m)"),
    ("cesme", "Su ve oturma noktası", 250, 250, "§9.5"),
]

# Daire karması varsayımları (tipoloji çizimleriyle aynı) [H]
KARMA = {
    "T1": [("3+1 ve üstü", 1.0)],
    "T2": [("2+1", 0.5), ("3+1 ve üstü", 0.5)],
    "T3": None,
    "T4": [("1+1", 1 / 3), ("2+1", 2 / 3)],
}

# Güncel MPYY EK-2 (17.05.2017 değişik), 0–75.000 nüfus kademesi [D, degisiklik_paketi_v1.md M1]
EK2 = [
    # (anahtar, ad, m²/kişi, asgari parsel m², not)
    ("anaokulu", "Anaokulu", 0.5, (1500, 3000), ""),
    ("ilkokul", "İlkokul", 2.0, (5000, 8000), "her okul ≥ 5.000 m²"),
    ("ortaokul", "Ortaokul", 2.0, (6000, 10000), "komşu mahalleyle ortak; komşu payı ayrıca"),
    ("saglik", "Aile sağlık merkezi", None, (750, 2000), "EK-2'deki 1,5 m²/kişi sağlık tesisleri için yorumlandı (hastane semtte; doğrulanmalı)"),
    ("sosyal", "Sosyal-kültürel tesis", 0.75, None, "mahalle konağı"),
    ("ibadet", "İbadet (küçük ve orta)", 0.5, (1000, None), "küçük ibadet yeri ≥ 1.000 m²"),
    ("teknik", "Teknik altyapı", 1.0, None, "yol ve otopark hariç"),
    ("yesil", "Açık ve yeşil alan (park, oyun, bostan)", 10.0, None, "ilçe ölçeği; spor alanı ayrı satırda"),
]

ARAZI_NOT = {
    "Sokak, yaya yolu ve meydan": "4 yeşil diyagonal ve ada içi S3 geçitleri; v2'de ilkokul A güneyindeki S2 yeniden açıldı",
    "Kamusal yeşil (park + cep + bostan)": "cep parkları köşe evleri, teknik altyapı ve okullar için azaldı; ≥ 10 m²/kişi korunur",
    "Cep parkı ve kapı önü oyun alanı": "diyagonal kırpıntıları; v2'de bir kısmı köşe evi parseli oldu",
    "Mahalle konağı": "sosyal-kültürel ≥ 0,75 m²/kişi (güncel EK-2) için (3,3) üçgenine uzatıldı",
    "Bölgesel otopark (4 yapı)": "v2: 4 × 41 m Z+4 (v1: 4 × 50 m Z+3); kalan 9 m teknik altyapı şeridi",
    "Net konut alanı": "güncel EK-2 donatısı (+1,1 ha) diyagonal ve köşe kazanımlarını karşıladı; bkz. tutarlı hedef",
    "Komşuluk yeşilleri (8 adet)": "8 × 0,50 ha + kuzeybatıdaki kenar parkı",
    "Eğitim (2 ilkokul, ortaokul, 2 anaokulu)": "güncel EK-2: 0,5 + 2,0 + 2,0 = 4,5 m²/kişi",
    "Teknik altyapı": "üç köşe üçgeni + mobilite noktalarında 4 × 9 m servis şeridi (güncel EK-2 ≥ 1,0 m²/kişi)",
}


def _durum(deger, hedef_min=None, hedef_max=None, tolerans=0.05):
    if deger is None:
        return "—"
    ok_min = hedef_min is None or deger >= hedef_min
    ok_max = hedef_max is None or deger <= hedef_max
    if ok_min and ok_max:
        return "uyumlu"
    yakin_min = hedef_min is None or deger >= hedef_min * (1 - tolerans)
    yakin_max = hedef_max is None or deger <= hedef_max * (1 + tolerans)
    return "yakın (±%5)" if (yakin_min and yakin_max) else "sapma"


def _alan(geom):
    return 0.0 if geom is None or geom.is_empty else geom.area


# =============================================================================
# Parsel düzeyinde yardımcılar (v1 parsellerine de uygulanır)
# =============================================================================
def kat_profili(parseller):
    kat_dagilim = defaultdict(float)
    bina_kat = defaultdict(int)
    for p in parseller:
        if p["tip"] == "T3":
            yan = min(p.get("yan_konut", 4), p["konut"])
            arka = min(p.get("arka_konut", 0), p["konut"] - yan)
            kat_dagilim[p["kat"]] += p["konut"] - yan - arka
            kat_dagilim[2] += yan
            kat_dagilim[1] += arka
            bina_kat[p["kat"]] += 1
            bina_kat[2] += 2
            if arka:
                bina_kat[1] += 1
        else:
            kat_dagilim[p["kat"]] += p["konut"]
            bina_kat[p["kat"]] += 1
    return kat_dagilim, bina_kat


def erisilebilirlik(parseller):
    """Zemin katta erişilebilir BB, basamaksız ulaşılan konut, zemine/avluya doğrudan açılan hane, yapı başına hane."""
    konut = sum(p["konut"] for p in parseller)
    zemin_erisilebilir = 0.0      # eşiksiz zemin kat dairesi (T2 zemin, T3 zemin)
    asansorlu = 0.0               # asansörlü binadaki daireler (T3 Z+3 sokak kanadı, T4)
    t1_zemin_oda = 0.0            # T1: zeminde büyükler odası + duş (aşama 2)
    dogrudan = 0.0                # kendi kapısından bahçeye/avluya çıkan hane
    yapi_hane = []                # (bina hane sayısı, ağırlık = hane)
    for p in parseller:
        k = p["konut"]
        if k <= 0:
            continue
        t = p["tip"]
        if t == "T1":
            t1_zemin_oda += k
            dogrudan += k
            yapi_hane.append((1, k))
        elif t == "T2":
            zemin_erisilebilir += 1
            dogrudan += k
            yapi_hane.append((k, k))
        elif t == "T3":
            yan = min(p.get("yan_konut", 4), k)
            arka = min(p.get("arka_konut", 0), k - yan)
            z = min(p.get("zemin_konut", 0), k - yan - arka)
            zemin_erisilebilir += z + p.get("yan_erisilebilir", 0) + arka
            if p["kat"] >= 4:
                asansorlu += k - yan - z - arka
            dogrudan += z + yan + arka
            yapi_hane.append((k - yan - arka, k - yan - arka))
            if arka:
                yapi_hane.append((arka, arka))
            if yan:
                yapi_hane.append((yan / 2, yan / 2))
                yapi_hane.append((yan / 2, yan / 2))
        else:
            asansorlu += k
            yapi_hane.append((k, k))
    ort_yapi = sum(h * w for h, w in yapi_hane) / sum(w for _, w in yapi_hane)
    return dict(zemin=zemin_erisilebilir / konut, basamaksiz=(zemin_erisilebilir + asansorlu) / konut,
                t1_zemin=t1_zemin_oda / konut, dogrudan=dogrudan / konut, yapi_hane=ort_yapi,
                zemin_adet=zemin_erisilebilir, asansorlu_adet=asansorlu)


def asansor_ozeti(parseller):
    toplam = defaultdict(float)
    tip_say = defaultdict(lambda: defaultdict(float))
    for p in parseller:
        for b in tv.bina_dikey_dolasim(p):
            toplam["asansor_mevcut"] += b["asansor_mevcut"]
            toplam["asansor_p4"] += b["asansor_p4"]
            toplam["yer"] += b["yer"]
            toplam["platform_yeri"] += b["platform_yeri"]
            ad = b["bina"] + (f" Z+{b['kat'] - 1}" if b["bina"].startswith(("T3 sokak", "T4")) else "")
            tip_say[ad]["bina"] += 1
            tip_say[ad]["bb"] += b["bb"]
            tip_say[ad]["asansor_mevcut"] += b["asansor_mevcut"]
            tip_say[ad]["asansor_p4"] += b["asansor_p4"]
            tip_say[ad]["yer"] += b["yer"]
            tip_say[ad]["platform_yeri"] += b["platform_yeri"]
            # maliyet: durak sayısı = kat
            m = tv.asansor_maliyeti(b["kat"])
            tip_say[ad]["maliyet_mevcut"] += b["asansor_mevcut"] * m
            tip_say[ad]["maliyet_p4"] += b["asansor_p4"] * m
            toplam["maliyet_mevcut"] += b["asansor_mevcut"] * m
            toplam["maliyet_p4"] += b["asansor_p4"] * m
    return dict(toplam), {k: dict(v) for k, v in tip_say.items()}


def otopark_ek1(parseller):
    mevcut = reform = dukkan = 0.0
    sinif = defaultdict(int)
    for p in parseller:
        for ad, brut in tv.parsel_bb(p):
            mevcut += tv.ek1_mevcut(brut)
            reform += tv.ek1_reform(brut)
            sinif[ad] += 1
        dukkan += p.get("ticari", 0.0) / tv.DUKKAN_M2_YER
    return dict(mevcut=mevcut, reform=reform, dukkan=dukkan, sinif=dict(sinif))


def bahce_avlu(parseller, ortaklar):
    ozel = 0.0
    for p in parseller:
        if p["tip"] in ("T1", "T2"):
            yapili = unary_union(p["binalar"] + ([p["genisleme"]] if p.get("genisleme") is not None else []))
            ozel += p["poly"].difference(yapili).area
        elif p.get("avlu") is not None:
            ozel += p["avlu"].area
    ortak = sum(o.area for o in ortaklar)
    return ozel, ortak


def kuzey_bahce_payi(parseller):
    """Kapısı parselin güney kenarında olan T1/T2 (bahçe evin kuzeyinde → kışın gölgede) payı."""
    t12 = [p for p in parseller if p["tip"] in ("T1", "T2") and p["konut"] > 0]
    kuz = 0
    for p in t12:
        y0 = p["poly"].bounds[1]
        if abs(p["kapi"][1] - y0) < 1.0 and p["poly"].bounds[3] - p["kapi"][1] > 15:
            kuz += p["konut"]
    return kuz / sum(p["konut"] for p in t12)


def dukkan_sayisi(parseller, donatilar):
    n = 0.0
    for p in parseller:
        if p["tip"] == "T4" and p.get("dukkan"):
            n += 2                                         # 24 m modülde iki dükkân
        elif p["tip"] == "T3" and p.get("dukkan"):
            n += max(1, round((p.get("ticari", 0) or 0) / tv.DUKKAN_BIRIM_M2))
    for d in donatilar:
        if d["tur"] == "carsi":
            n += round(sum(b.area for b in d["binalar"]) / 60)     # çarşı zemininde ≈ 60 m²'lik birimler
        elif d["tur"] == "otopark":
            n += 2                                         # market + bisiklet atölyesi
    return n


def _agac_v1_formulu(P):
    """v1 metrikler.py'deki kaba formül, v2 geometrisine aynen uygulanır (karşılaştırma için)."""
    sokak_agac = (2 * 728 / 10 + 2 * 776 / 10) + 2 * (2 * (800 + 750) / 10) + sum(
        ln.length / 12 for k, (_, ln) in pm.BAGLANTI.items() if k not in pm.KAPALI) + sum(
        2 * ln.length / 8 for ln in pm.DIYAG_EKSEN)
    D = P["donatilar"]
    park = sum(d["poly"].area for d in D if d["tur"] in ("park", "cep")) + sum(g.area for g in P["cep"])
    bahce = sum(1 if p["tip"] in ("T1", "T2") else (3 if p["tip"] == "T3" else 0.3) for p in P["parseller"])
    return (sokak_agac * 38 + 0.45 * park + bahce * 28 + 0.25 * sum(o.area for o in P["ortaklar"])) / pm.ALAN.area


# =============================================================================
# Ana hesap
# =============================================================================
@lru_cache(maxsize=1)
def metrikleri_hesapla():
    P = pm.model()
    A = pm.ag_kur()
    parseller = P["parseller"]
    D = P["donatilar"]

    tip = defaultdict(lambda: defaultdict(float))
    for p in parseller:
        t = tip[p["tip"]]
        t["konut"] += p["konut"]
        t["parsel"] += 1
        t["parsel_alani"] += p["poly"].area
        t["oturum"] += sum(b.area for b in p["binalar"])
        t["kat_alani"] += p["kat_alani"]
        t["ticari"] += p["ticari"]
    konut = sum(t["konut"] for t in tip.values())
    nufus = konut * HANE_BUYUKLUGU

    # ---------------- arazi bütçesi ------------------------------------------
    def d_alan(*turler):
        return sum(d["poly"].area for d in D if d["tur"] in turler)

    park_merkez = sum(d["poly"].area for d in D if d.get("merkez"))
    park_kb = [d["poly"].area for d in D if d["tur"] == "park" and not d.get("merkez")]
    cep = sum(g.area for g in P["cep"]) + d_alan("cep")
    bostan = d_alan("bostan")
    yesil = park_merkez + sum(park_kb) + cep + bostan
    spor = d_alan("spor")
    egitim = d_alan("ilkokul", "ortaokul", "anaokulu")
    ilkokul = {d["okul"]: d["poly"].area for d in D if d["tur"] == "ilkokul"}
    ortaokul = d_alan("ortaokul")
    anaokulu = [d["poly"].area for d in D if d["tur"] == "anaokulu"]
    ibadet = d_alan("semt_camii", "kucuk_cami")
    saglik = d_alan("asm")
    sosyal = d_alan("konak")
    carsi = d_alan("carsi")
    teknik = d_alan("teknik")
    otopark = d_alan("otopark")
    konut_net = sum(p["poly"].area for p in parseller) + sum(o.area for o in P["ortaklar"])
    yol_toplayici = pm.TOPLAYICI.area
    yol_s1 = pm.CADDE.difference(pm.MEYDAN).area
    yol_s2 = pm.S2.area
    meydan = pm.MEYDAN.area
    arac_yol = unary_union([pm.TOPLAYICI, pm.CADDE, pm.S2, pm.MEYDAN])
    yaya = (pm.DIYAG_BANT.difference(pm.DONATI_POLY).difference(arac_yol).area + sum(g.area for g, _ in P["gecitler"])
            + pm.KAPALI_SOKAK.difference(pm.DONATI_POLY).area)
    sokak = yol_toplayici + yol_s1 + yol_s2 + meydan + yaya
    toplam = konut_net + sokak + yesil + spor + egitim + ibadet + saglik + sosyal + carsi + teknik + otopark
    kayip = pm.ALAN.area - toplam

    # tutarlı hedef: §9.3 bütçesi güncel EK-2 ve v1/v2 kurgusuyla yeniden hesaplanır [H]
    n0 = 7200
    tutarli = dict(
        eski=32.0,
        ek2=60 - 15.0 - 7.2 - (0.5 + 2.0 + 2.0) * n0 / HA - 0.76 - 0.15 - 0.75 * n0 / HA - 0.50 - 0.50 - 1.0 * n0 / HA - 0.65,
    )
    tutarli["diyagonal"] = tutarli["ek2"] - (sokak - 15.0 * HA) / HA
    tutarli["otopark4"] = tutarli["diyagonal"] - (otopark - 0.65 * HA) / HA
    tutarli["yesil"] = tutarli["otopark4"] - max(0.0, yesil - 10.0 * n0) / HA

    # ---------------- kat alanı, kat profili, karma ---------------------------
    kat_dagilim, bina_kat = kat_profili(parseller)
    oda = defaultdict(float)
    for p in parseller:
        if p["tip"] == "T3":
            yan = min(p.get("yan_konut", 4), p["konut"])
            arka = min(p.get("arka_konut", 0), p["konut"] - yan)
            sk = p["konut"] - yan - arka
            zemin = min(p.get("zemin_konut", 0), sk)
            ust = sk - zemin
            oda["1+1"] += 1 if zemin >= 1 else 0
            oda["2+1"] += (zemin - 1 if zemin >= 1 else 0) + yan + arka
            oda["3+1 ve üstü"] += ust
        else:
            for sinif, pay in KARMA[p["tip"]]:
                oda[sinif] += p["konut"] * pay
    pay_le3 = sum(v for k, v in kat_dagilim.items() if k <= 3) / konut
    pay_le4 = sum(v for k, v in kat_dagilim.items() if k <= 4) / konut
    pay_5 = sum(v for k, v in kat_dagilim.items() if k >= 5) / konut
    bina_le3 = sum(v for k, v in bina_kat.items() if k <= 3) / sum(bina_kat.values())
    ort_kat = sum(k * v for k, v in kat_dagilim.items()) / konut

    konut_kat_alani = sum(t["kat_alani"] - t["ticari"] for t in tip.values())
    ticari_kat = sum(t["ticari"] for t in tip.values()) + sum(d.get("ticari", 0.0) for d in D)
    donati_kat = sum(sum(b.area for b in d["binalar"]) * d["kat"] for d in D if d["tur"] not in ("otopark", "teknik"))
    otopark_kat = sum(sum(b.area for b in d["binalar"]) * d["kat"] - d.get("ticari", 0.0) for d in D
                      if d["tur"] == "otopark")
    otopark_yer = otopark_kat * 0.92 / 25.0      # 25 m²/araç (rampa ve manevra dahil), %8 çekirdek
    konut_disi_pay = (ticari_kat + donati_kat) / (konut_kat_alani + ticari_kat + donati_kat)

    # ---------------- sokak ağı ---------------------------------------------
    sokak_cizgi = A["sokak_cizgi"]
    halka = sokak_cizgi[0]
    ic_sokak = sokak_cizgi[1:]
    ag_uzunluk = 0.5 * halka.length + sum(l.length for l in ic_sokak) + sum(l.length for l in pm.DIYAG_EKSEN)
    km_km2 = (ag_uzunluk / 1000) / (pm.ALAN.area / 1e6)

    def kavsak_say(cizgiler):
        u = unary_union(cizgiler)
        G = nx.Graph()
        for ln in getattr(u, "geoms", [u]):
            c = list(ln.coords)
            for a, b in zip(c[:-1], c[1:]):
                G.add_edge((round(a[0], 1), round(a[1], 1)), (round(b[0], 1), round(b[1], 1)))
        return sum(1 for n, d in G.degree() if d >= 3)

    arac_cizgi = [halka] + [ln for k, (_, ln) in pm.BAGLANTI.items() if k not in pm.KAPALI] + sokak_cizgi[1:3]
    kavsak_arac = kavsak_say(arac_cizgi)
    kavsak_yaya = kavsak_say(sokak_cizgi + list(pm.DIYAG_EKSEN))
    km2 = pm.ALAN.area / 1e6

    # ---------------- sokak kesitleri (çizimdeki ölçülerle) ----------------------
    W_s2 = pm.S2_G + 2 * pm.ON_ESIK_K2
    W_s2_k1 = pm.S2_G + 2 * pm.ON_ESIK_K1
    H_s2 = 3 * KAT_YUK
    W_s1 = pm.CADDE_G + pm.T3_ON
    H_s1 = ZEMIN_TICARI_YUK + 3 * KAT_YUK
    tan_ara = math.tan(math.radians(ARALIK_ACI))
    kesit = dict(s2_hw=H_s2 / W_s2, s2_hw_k1=H_s2 / W_s2_k1, s2_hw_cekirdek=(H_s2 + 2 * KAT_YUK) / 2 / W_s2,
                 s1_hw=H_s1 / W_s1, s2_aralik_golge=max(0.0, H_s2 - W_s2 * tan_ara),
                 s1_aralik_golge=max(0.0, H_s1 - W_s1 * tan_ara), W_s2=W_s2, H_s2=H_s2, W_s1=W_s1, H_s1=H_s1)

    # ---------------- erişim ------------------------------------------------
    erisim = {}
    mesafe_parsel = {}
    for tur, etiket, hedef, ust, kaynak in ERISIM:
        liste = pm.konut_mesafeleri(tur)
        mesafe_parsel[tur] = [m for _, m in liste]
        agirlik = [(m, p["konut"]) for p, m in liste if p["konut"] > 0]
        toplam_k = sum(w for _, w in agirlik)
        pay_h = sum(w for m, w in agirlik if m <= hedef) / toplam_k
        pay_u = sum(w for m, w in agirlik if m <= ust) / toplam_k
        sirali = sorted(agirlik)
        kum, med, p95 = 0, None, None
        for m, w in sirali:
            kum += w
            if med is None and kum >= toplam_k * 0.5:
                med = m
            if p95 is None and kum >= toplam_k * 0.95:
                p95 = m
        erisim[tur] = dict(etiket=etiket, hedef=hedef, ust=ust, kaynak=kaynak, pay_hedef=pay_h, pay_ust=pay_u,
                           medyan=med, p95=p95, en_fazla=sirali[-1][0])
    ilk_400 = sum(p["konut"] for p, m in pm.konut_mesafeleri("ilkokul") if m <= 400) / konut
    ib = 0
    for k, p in enumerate(parseller):
        if (mesafe_parsel["mescit"][k] <= 150 or mesafe_parsel["kucuk_cami"][k] <= 250
                or mesafe_parsel["semt_camii"][k] <= 400):
            ib += p["konut"]
    erisim["ibadet_kademe"] = dict(etiket="İbadet yeri (mescit ≤150 / küçük cami ≤250 / semt camii ≤400 m)",
                                   pay_hedef=ib / konut)

    # okul kayıt alanları: her konut en yakın ilkokula
    la, lb = pm.konut_mesafeleri("ilkokul_A"), pm.konut_mesafeleri("ilkokul_B")
    hane = {"A": 0.0, "B": 0.0}
    for (p, a), (_, b) in zip(la, lb):
        hane["A" if a <= b else "B"] += p["konut"]
    okul = {}
    for o in ("A", "B"):
        ogr = hane[o] * HANE_BUYUKLUGU * OGRENCI_PAYI
        okul[o] = dict(alan=ilkokul[o], hane=hane[o], ogrenci=ogr, derslik=tv.sayi_tavan(ogr / DERSLIK_MEVCUT),
                       m2_ogrenci=ilkokul[o] / ogr)

    # ---------------- komşuluk birimleri ----------------------------------------
    birimler = []
    for no, g in pm.komsuluk_birimleri():
        k = sum(p["konut"] for p in parseller if pm.birim_bul(p["kapi"]) == no)
        mescit = sum(1 for z in P["zemin"] if z["tur"] == "mescit" and pm.birim_bul(z["xy"]) == no)
        birimler.append(dict(no=no, konut=k, nufus=k * HANE_BUYUKLUGU, alan=g.area, mescit=mescit))
    t3 = [p for p in parseller if p["tip"] == "T3"]
    avlu_hane = [p["konut"] for p in t3]
    bahce_grubu = defaultdict(int)
    for p in parseller:
        if p["tip"] in ("T1", "T2"):
            c = p["poly"].centroid
            x0 = pm.XS[p["ada"][0]][0]
            bahce_grubu[(p["ada"], int((c.x - x0) // 30))] += p["konut"]
    ortak_birlesik = unary_union(P["ortaklar"]).buffer(1.0)
    oyun_avlu = sum(p["konut"] for p, m in pm.konut_mesafeleri("oyun")
                    if m <= 150 or p["tip"] == "T3" or p["poly"].intersects(ortak_birlesik))

    # ---------------- v2: ağaç, erişilebilirlik, asansör, otopark, tahsis --------------------
    tac = pm.tac_ortusu()
    agac_v1_formul = _agac_v1_formulu(P)
    eris = erisilebilirlik(parseller)
    g17 = 0.0
    for p in parseller:
        k_ = p["konut"]
        if k_ <= 0:
            continue
        if p["tip"] in ("T1", "T2", "T4") or p["kat"] >= 4:
            g17 += k_
        else:
            yan_ = min(p.get("yan_konut", 4), k_)
            if (min(p.get("zemin_konut", 0), k_ - yan_) + p.get("yan_erisilebilir", 0) + p.get("arka_konut", 0)) / k_ \
                    >= 0.15 - 1e-9:
                g17 += k_
    asn_toplam, asn_tip = asansor_ozeti(parseller)
    ek1 = otopark_ek1(parseller)
    ozel_bahce, ortak_bahce = bahce_avlu(parseller, P["ortaklar"])
    kuzey_bahce = kuzey_bahce_payi(parseller)
    dukkan = dukkan_sayisi(parseller, D)
    kose = sum(1 for p in parseller if p.get("kose"))
    kose_konut = sum(p["konut"] for p in parseller if p.get("kose"))
    tah, tah_liste = pm.tahsis()
    tah_pay = defaultdict(float)
    tah_kb = defaultdict(lambda: defaultdict(float))
    piyasa_ada = defaultdict(float)
    for n, t in tah.items():
        k = parseller[n]["konut"]
        tah_pay[t] += k
        tah_kb[pm.birim_bul(parseller[n]["kapi"])][t] += k
        if t == "piyasa":
            piyasa_ada[parseller[n]["ada"]] += k
    yapimci_asgari = sum(tv.sayi_tavan(v / pm.YAPIMCI_TAVAN) for v in piyasa_ada.values())
    kb_sapma = max(abs(tah_kb[kb][t] / sum(tah_kb[kb].values()) - h) for kb in tah_kb for t, h in pm.TAHSIS_HEDEF.items())

    R = dict(konut=konut, nufus=nufus, tip=tip, konut_net=konut_net, yesil=yesil, park_merkez=park_merkez,
             park_kb=park_kb, cep=cep, bostan=bostan, spor=spor, egitim=egitim, ilkokul=ilkokul, ortaokul=ortaokul,
             anaokulu=anaokulu, ibadet=ibadet, saglik=saglik, sosyal=sosyal, carsi=carsi, teknik=teknik,
             otopark=otopark, sokak=sokak, yol_toplayici=yol_toplayici, yol_s1=yol_s1, yol_s2=yol_s2, meydan=meydan,
             yaya=yaya, kayip=kayip, tutarli=tutarli, kat_dagilim=dict(kat_dagilim), pay_le3=pay_le3, pay_le4=pay_le4,
             pay_5=pay_5, bina_le3=bina_le3, ort_kat=ort_kat, bina_kat=dict(bina_kat), oda=dict(oda),
             konut_kat_alani=konut_kat_alani, ticari_kat=ticari_kat, donati_kat=donati_kat,
             konut_disi_pay=konut_disi_pay, otopark_yer=otopark_yer, ag_uzunluk=ag_uzunluk, km_km2=km_km2,
             kavsak_arac=kavsak_arac / km2, kavsak_yaya=kavsak_yaya / km2, kesit=kesit, erisim=erisim, ilk_400=ilk_400,
             okul=okul, birimler=birimler, avlu_grubu=len(t3), avlu_hane=avlu_hane,
             bahce_grubu=list(bahce_grubu.values()), oyun_avlu=oyun_avlu / konut, tac=tac, g17=g17 / konut,
             agac_v1_formul=agac_v1_formul, eris=eris, asn_toplam=asn_toplam, asn_tip=asn_tip, ek1=ek1,
             ozel_bahce=ozel_bahce, ortak_bahce=ortak_bahce, kuzey_bahce=kuzey_bahce, dukkan=dukkan, kose=kose,
             kose_konut=kose_konut, dusen=len(P["dusen"]), tah_pay={k: v / konut for k, v in tah_pay.items()},
             tah_kb={kb: dict(v) for kb, v in tah_kb.items()}, piyasa_ada=dict(piyasa_ada),
             yapimci_asgari=yapimci_asgari, kb_sapma=kb_sapma, parsel_sayisi=len(parseller),
             mescit_sayisi=sum(1 for z in P["zemin"] if z["tur"] == "mescit"),
             kres_sayisi=sum(1 for z in P["zemin"] if z["tur"] == "kres"),
             durak_s1=len(pm.DURAKLAR["S1"]), durak_toplayici=len(pm.DURAKLAR["toplayici"]),
             mesafe_parsel=mesafe_parsel)
    R["v1"] = v1_ek_degerler()
    R["fue"] = fue_konum(R)
    R["fue_iki"] = fue_konum(R, muhtarlik=2)
    R["morf"] = None if os.environ.get("MM_ALT") == "1" else _morf_ozet()
    R["satirlar"] = _satirlar(R)
    R["ozet_satirlari"] = _ozet(R)
    return R


def _morf_ozet():
    try:
        import morfoloji_v2
        return morfoloji_v2.ozet()
    except Exception as e:                     # ölçüm betiğinin bağımlılıkları yoksa morfoloji satırları atlanır
        print("morfoloji ölçümü atlandı:", e)
        return None


# FUE v0.2 (09_RAPORLAR/10_fue_mahalle.md): 05_ANALIZ/kod/fue_model_mahalle.py ile aynı kural; girdiler salt okunur
FUE_KOK = Path(__file__).resolve().parents[3] / "05_ANALIZ" / "sonuclar"
FUE_ERISIM = ["kavsak_yog", "temel15", "oyun400", "okul500", "esnaf1000", "karma150", "cami500", "bulusma400", "ulasim",
              "rayli800"]


def fue_konum(R, muhtarlik=1):
    """Model mahallenin E, Ç ve FUE puanı (300 pilot kentsel mahallenin dağılımında yüzdelik).
    yukseklik: konut ağırlıklı kat × kat yüksekliği [H]; fue_model_mahalle.py v2.0 için 9,5 m varsaymıştı [V]."""
    try:
        import numpy as np
        import pandas as pd
        Mf = pd.read_csv(FUE_KOK / "fue_mahalle.csv")
        Gf = pd.read_csv(FUE_KOK / "fue_gosterge_tanim.csv")
    except Exception:
        return None
    K = Mf[Mf.kentsel]
    n = R["nufus"]
    e = R["erisim"]
    deger = {
        "kavsak_yog": R["kavsak_arac"], "temel15": 100.0, "yesil300": 100.0, "yukseklik": R["ort_kat"] * KAT_YUK,
        "yuksek_pay": 0.0, "anayol100": 5.0, "zemin_pay": 100 * R["pay_le3"], "oyun400": 100.0,
        "okul500": 100 * e["ilkokul"]["pay_hedef"], "esnaf1000": R["dukkan"] / n * 1000, "karma150": 60.0,
        "cami500": 100 * e["ibadet_kademe"]["pay_hedef"], "bulusma400": 85.0, "site_pay": 0.0,
        "muhtar_nufus": math.log(n / muhtarlik), "ulasim": 100 * e["durak"]["pay_hedef"], "yayilma": 60.0 / (n / 1000),
        "rayli800": 0.0,
    }
    puan = []
    for _, g in Gf.iterrows():
        r = np.sort(K[g.kod].dropna().values)
        v = deger[g.kod]
        p = (np.searchsorted(r, v, "left") + np.searchsorted(r, v, "right")) / 2 / len(r) * 100
        puan.append((g.kod, g.boyut, p if g.yon > 0 else 100 - p))
    import pandas as pd  # noqa
    T = pd.DataFrame(puan, columns=["kod", "boyut", "puan"])
    E = T[T.kod.isin(FUE_ERISIM)].puan.mean()
    C = T[~T.kod.isin(FUE_ERISIM)].puan.mean()
    return dict(E=E, C=C, FUE=T.groupby("boyut").puan.mean().mean(), yukseklik=deger["yukseklik"],
                puan=dict(zip(T.kod, T.puan)))


@lru_cache(maxsize=1)
def v20_degerleri():
    """v2.0 satırları: aynı kod MM_SURUM=2.0 ile ayrı süreçte çalıştırılır. {(kategori, gösterge): değer}"""
    if os.environ.get("MM_SURUM", "2.1") == "2.0" or os.environ.get("MM_ALT") == "1":
        return {}
    with tempfile.TemporaryDirectory() as t:
        yol = Path(t) / "v20.pkl"
        env = dict(os.environ, MM_SURUM="2.0", MM_ALT="1", PYTHONIOENCODING="utf-8")
        kod = ("import sys, pickle; sys.dont_write_bytecode = True; sys.path.insert(0, sys.argv[1]); "
               "import metrikler as m; R = m.metrikleri_hesapla(); "
               "pickle.dump({(r[0], r[1]): r[4] for r in R['satirlar']}, open(sys.argv[2], 'wb'))")
        subprocess.run([sys.executable, "-c", kod, str(Path(__file__).resolve().parent), str(yol)], check=True, cwd=t,
                       env=env, stdout=subprocess.DEVNULL)
        with open(yol, "rb") as f:
            return pickle.load(f)


@lru_cache(maxsize=1)
def v1_ek_degerler():
    """v1 geometrisine v2 yöntemi: v1'in CSV'sinde olmayan göstergeler için."""
    g = v1.v1_geometri()
    ps = g["parseller"]
    konut = sum(p["konut"] for p in ps)
    ilk400 = sum(p["konut"] for p in ps if p["ilkokul_m"] <= 400) / konut
    eris = erisilebilirlik(ps)
    asn, _ = asansor_ozeti(ps)
    ek1 = otopark_ek1(ps)
    ozel, ortak = bahce_avlu(ps, g["ortaklar"])
    egit = {d["tur"]: 0.0 for d in g["donatilar"]}
    for d in g["donatilar"]:
        egit[d["tur"]] = egit.get(d["tur"], 0.0) + d["poly"].area
    return dict(konut=konut, ilk400=ilk400, eris=eris, asn=asn, ek1=ek1, ozel_bahce=ozel, ortak_bahce=ortak,
                kuzey_bahce=kuzey_bahce_payi(ps), dukkan=dukkan_sayisi(ps, g["donatilar"]),
                alan=egit, dusen=len(g["dusen"]), kose=0, nufus=konut * HANE_BUYUKLUGU)


# =============================================================================
# CSV satırları
# =============================================================================
def _satirlar(R):
    """(kategori, gösterge, birim, v1, v2, hedef metni, hedef kaynağı, durum, not)."""
    S = []
    k, n = R["konut"], R["nufus"]
    V1 = R["v1"]
    n1 = V1["nufus"]

    def ekle(kat, ad, birim, deger, hedef_metin, kaynak, durum, not_="", v1_deger="csv"):
        if v1_deger == "csv":
            v1_deger = v1.v1_deger(ad)
        S.append((kat, ad, birim, v1_deger, deger, hedef_metin, kaynak, durum, not_, None))

    ekle("Ölçek", "Brüt alan", "ha", 60.0, "60", "§9.2", "uyumlu", "Toplayıcı yolun iç yarısı dahil (800 × 750 m)")
    ekle("Ölçek", "Konut sayısı", "konut", k, "2.250", "§9.2",
         "uyumlu" if abs(k - 2250) / 2250 <= 0.02 else ("yakın (±%5)" if abs(k - 2250) / 2250 <= 0.05 else "sapma"),
         f"hedeften fark %{sayi(100 * (k - 2250) / 2250, 1)}; iki okul, büyük ortaokul ve ≤ 3 kat payı için kabul edildi")
    ekle("Ölçek", "Nüfus", "kişi", n, "7.200 (6.000–8.000)", "§9.2", _durum(n, 6000, 8000), f"{HANE_BUYUKLUGU} kişi/hane varsayımı")
    ekle("Yoğunluk", "Brüt nüfus yoğunluğu", "kişi/ha", n / 60, "120 (100–150)", "§2", _durum(n / 60, 100, 150))
    ekle("Yoğunluk", "Brüt konut yoğunluğu", "konut/ha", k / 60, "37,5", "§9.2", _durum(k / 60, 37.5 * 0.95, 37.5 * 1.05))
    fark_net = 100 * (R["konut_net"] / HA - 32.0) / 32.0
    ekle("Yoğunluk", "Net konut alanı (parsel + ada içi ortak bahçe)", "ha", R["konut_net"] / HA,
         f"32,0 (güncel EK-2 ile tutarlı: {sayi(R['tutarli']['yesil'], 1)})", "§9.3 / [H]",
         "uyumlu" if abs(fark_net) <= 10 else ("yakın (±%25)" if abs(fark_net) <= 25 else "sapma"),
         f"32 ha'dan fark %{sayi(fark_net)}; tutarlı hedeften fark %"
         f"{sayi(100 * (R['konut_net'] / HA - R['tutarli']['yesil']) / R['tutarli']['yesil'])}")
    ekle("Yoğunluk", "Net konut yoğunluğu", "konut/ha", k / (R["konut_net"] / HA), "≈70 (50–90)", "§2",
         _durum(k / (R["konut_net"] / HA), 50, 90))
    ekle("Yoğunluk", "Net nüfus yoğunluğu", "kişi/ha", n / (R["konut_net"] / HA), "≈225", "§9.2", "—")
    for t, ad, hedef in (("T1", "T1 büyüyebilen sıra ev", 650), ("T2", "T2 avlulu çok kuşaklı ev", 400),
                         ("T3", "T3 avlu grubu", 1050), ("T4", "T4 çevre adası (zeminde dükkân)", 150)):
        v = R["tip"][t]["konut"]
        ekle("Konut tipleri", ad, "konut", v, f"{sayi(hedef)} (%{round(hedef / 22.5)})", "§9.4",
             _durum(100 * v / k, round(hedef / 22.5) - 2, round(hedef / 22.5) + 2) if t == "T1" else "—",
             f"plan payı %{sayi(100 * v / k, 1)}; parsel {sayi(R['tip'][t]['parsel'])}; net emsal "
             f"{sayi(R['tip'][t]['kat_alani'] / R['tip'][t]['parsel_alani'], 2)}; yapı oturumu "
             f"%{sayi(100 * R['tip'][t]['oturum'] / R['tip'][t]['parsel_alani'])}")
    v1_t1 = v1.v1_deger("T1 büyüyebilen sıra ev")
    ekle("Konut tipleri", "T1 payı", "%", 100 * R["tip"]["T1"]["konut"] / k, "29", "§9.4",
         _durum(100 * R["tip"]["T1"]["konut"] / k, 27, None), "bkz. model_mahalle_v2.md §3 (neden 29'a ulaşmadı)",
         v1_deger=100 * v1_t1 / 2222)
    ekle("Konut tipleri", "Diyagonal köşe evi (kırpılmış T1/T2 parseli)", "parsel", R["kose"], "—", "v2", "—",
         f"{sayi(R['kose_konut'])} konut; v1'de bu parseller düşürülüyordu (v2'de düşen parsel {R['dusen']}, v1'de "
         f"{V1['dusen']})", v1_deger=0)
    ekle("Kat profili", "≤ 3 katlı binalardaki konut payı", "%", 100 * R["pay_le3"], "≈70", "§9.4",
         "uyumlu" if abs(100 * R["pay_le3"] - 70) <= 5 else "sapma", "T1 son durumuna (Z+2) göre")
    ekle("Kat profili", "≤ 4 katlı binalardaki konut payı", "%", 100 * R["pay_le4"], "≈93", "§9.4", _durum(100 * R["pay_le4"], 93, None))
    ekle("Kat profili", "5 katlı binalardaki konut payı", "%", 100 * R["pay_5"], "≤ 7", "§9.4", _durum(100 * R["pay_5"], None, 7))
    ekle("Kat profili", "5 katın üzerinde konut", "konut", sum(v for kk, v in R["kat_dagilim"].items() if kk > 5), "0", "§3", "uyumlu")
    ekle("Kat profili", "≤ 3 katlı bina payı (bina sayısı)", "%", 100 * R["bina_le3"], "çoğunluk", "§3 (Alexander 21)", _durum(100 * R["bina_le3"], 50, None))
    oda = R["oda"]
    ekle("Konut karması", "3+1 ve üstü", "%", 100 * oda.get("3+1 ve üstü", 0) / k, "≥ 55–60", "§9.4", _durum(100 * oda.get("3+1 ve üstü", 0) / k, 55, None), "tipoloji varsayımlarından [H]")
    ekle("Konut karması", "2+1", "%", 100 * oda.get("2+1", 0) / k, "≈20", "§9.4", "—")
    ekle("Konut karması", "1+1", "%", 100 * oda.get("1+1", 0) / k, "5–10", "§9.4", _durum(100 * oda.get("1+1", 0) / k, 5, 10))
    ekle("Konut karması", "Çok kuşaklı kullanıma uygun (T2 + ek odalı T1)", "%",
         100 * (R["tip"]["T2"]["konut"] + R["tip"]["T1"]["konut"] * 0.5) / k, "≥ 15", "§9.4",
         _durum(100 * (R["tip"]["T2"]["konut"] + R["tip"]["T1"]["konut"] * 0.5) / k, 15, None),
         "T1'lerin yarısında genişleme payı büyükler odası olarak kullanılır varsayımı")
    ekle("Konut karması", "Konut dışı kat alanı payı", "%", 100 * R["konut_disi_pay"], "15–25", "§2",
         _durum(100 * R["konut_disi_pay"], 15, 25), "zemin kat dükkân + donatı binaları")
    ekle("Konut karması", "Zemin kat konut dışı birim (dükkân, atölye, ofis; ≈ 70 m²)", "adet", R["dukkan"], "80–120 dükkân",
         "§9.5; persona C", "—",
         f"≈ {sayi(R['nufus'] / R['dukkan'])} kişiye 1 birim; dükkân olarak hepsinin yaşaması zor (B ortamında ≈ 72 kişi/dükkân): "
         "T3 dükkânlı kanatlar 'esnek zemin kat' (atölye, ofis, kreş, konuta dönüşebilir) olarak tescil edilmeli",
         v1_deger=V1["dukkan"])

    # arazi bütçesi
    for ad, v, hedef, kaynak in (
            ("Sokak, yaya yolu ve meydan", R["sokak"], 15.0, "§9.3"),
            ("Kamusal yeşil (park + cep + bostan)", R["yesil"], 7.2, "§9.3"),
            ("  Merkez parkı", R["park_merkez"], 2.0, "§9.5"),
            ("  Komşuluk yeşilleri (8 adet)", sum(R["park_kb"]), 4.0, "§9.5"),
            ("  Cep parkı ve kapı önü oyun alanı", R["cep"], 0.4, "§9.3"),
            ("  Bostan ve hobi bahçesi", R["bostan"], 0.8, "§9.3"),
            ("Eğitim (2 ilkokul, ortaokul, 2 anaokulu)", R["egitim"], 4.5 * n / HA, "güncel EK-2"),
            ("İbadet (semt camii + 4 küçük cami)", R["ibadet"], 0.76, "§9.3"),
            ("Aile sağlık merkezi", R["saglik"], 0.15, "§9.3"),
            ("Mahalle konağı", R["sosyal"], 0.75 * n / HA, "güncel EK-2 (0,75 m²/kişi)"),
            ("Çarşı", R["carsi"], 0.50, "§9.3"),
            ("Açık semt spor alanı", R["spor"], 0.50, "§9.3"),
            ("Teknik altyapı", R["teknik"], 1.0 * n / HA, "güncel EK-2 (1,0 m²/kişi)"),
            ("Bölgesel otopark (4 yapı)", R["otopark"], 0.65, "§9.3"),
            ("Net konut alanı", R["konut_net"], 32.0, "§9.3")):
        fark = 100 * (v / HA - hedef) / hedef
        durum = "uyumlu" if abs(fark) <= 10 else ("yakın (±%25)" if abs(fark) <= 25 else "sapma")
        if ad.strip() in ("Eğitim (2 ilkokul, ortaokul, 2 anaokulu)", "Mahalle konağı", "Teknik altyapı"):
            durum = "uyumlu" if v / HA >= hedef else "sapma"
        v1d = v1.v1_deger(ad.strip()) if ad.strip() != "Eğitim (2 ilkokul, ortaokul, 2 anaokulu)" else v1.v1_deger("Eğitim (ilkokul, ortaokul, 2 anaokulu)")
        ekle("Arazi bütçesi", ad.strip(), "ha", v / HA, sayi(hedef, 2), kaynak, durum,
             f"brüt alanın %{sayi(100 * v / pm.ALAN.area, 1)}'i; hedeften fark %{sayi(fark)}"
             + (f"; {ARAZI_NOT[ad.strip()]}" if ad.strip() in ARAZI_NOT else ""), v1_deger=v1d)
    ekle("Arazi bütçesi", "Sınıflanamayan kırpıntı", "ha", R["kayip"] / HA, "0", "—", "—", "< 40 m² artıklar ve köşe payları")
    t = R["tutarli"]
    ekle("Arazi bütçesi", "Net konut alanı için tutarlı hedef", "ha", t["yesil"], "32,0 (§9.3, eski EK-2)", "[H]", "—",
         f"§9.3 bütçesi güncel EK-2 ile {sayi(t['ek2'], 1)} ha; diyagonaller ve S3 ile {sayi(t['diyagonal'], 1)}; "
         f"4 mobilite noktasıyla {sayi(t['otopark4'], 1)}; yeşil 10 m²/kişinin üstünde tutulunca {sayi(t['yesil'], 1)} ha",
         v1_deger=None)

    # güncel EK-2 dengesi
    alanlar = dict(anaokulu=sum(R["anaokulu"]), ilkokul=sum(R["ilkokul"].values()), ortaokul=R["ortaokul"],
                   saglik=R["saglik"], sosyal=R["sosyal"], ibadet=R["ibadet"], teknik=R["teknik"], yesil=R["yesil"])
    v1a = V1["alan"]
    v1_alan = dict(anaokulu=v1a.get("anaokulu", 0), ilkokul=v1a.get("ilkokul", 0), ortaokul=v1a.get("ortaokul", 0),
                   saglik=v1a.get("asm", 0), sosyal=v1a.get("konak", 0),
                   ibadet=v1a.get("semt_camii", 0) + v1a.get("kucuk_cami", 0), teknik=v1a.get("teknik", 0),
                   yesil=v1.v1_deger("Kamusal yeşil (park + cep + bostan)") * HA)
    for anahtar, ad, m2k, asgari, not_ in EK2:
        v = alanlar[anahtar]
        if m2k is not None:
            deger = v / n
            hedef_metin = f"≥ {sayi(m2k, 2)} m²/kişi" + (f"; asgari {sayi(asgari[0])} m²" if asgari else "")
            durum = "uyumlu" if deger >= m2k - 1e-9 else ("yakın (±%5)" if deger >= 0.95 * m2k else "sapma")
            ekle("Güncel EK-2 dengesi", ad, "m²/kişi", deger, hedef_metin, "MPYY EK-2 (17.05.2017) [D]", durum,
                 f"{sayi(v)} m²; {not_}", v1_deger=v1_alan[anahtar] / n1)
        else:
            ekle("Güncel EK-2 dengesi", ad, "m²", v, f"{sayi(asgari[0])}–{sayi(asgari[1])} m² parsel", "MPYY EK-2 [D]",
                 _durum(v, asgari[0], None), not_, v1_deger=v1_alan[anahtar])
    for o in ("A", "B"):
        ok = R["okul"][o]
        ekle("Güncel EK-2 dengesi", f"İlkokul {o} arsası", "m²", ok["alan"], "≥ 5.000", "MPYY EK-2 [D]",
             _durum(ok["alan"], 5000, None),
             f"kayıt alanı {sayi(ok['hane'])} hane ≈ {sayi(ok['ogrenci'])} öğrenci (6–9 yaş %6 [V]) → "
             f"{ok['derslik']} derslik; {sayi(ok['m2_ogrenci'], 1)} m²/öğrenci",
             v1_deger=v1a.get("ilkokul") if o == "A" else None)
    ekle("Güncel EK-2 dengesi", "Ortaokul arsası", "m²", R["ortaokul"], f"≥ 2,0 × nüfus = {sayi(2 * n)}", "MPYY EK-2 [D]",
         _durum(R["ortaokul"], 2 * n, None), "GD köşe adalarının tamamı; okul sahası mesai dışı mahalleye açık",
         v1_deger=v1a.get("ortaokul"))

    # yeşil
    ekle("Yeşil", "Kamusal yeşil / kişi", "m²/kişi", R["yesil"] / n, "≥ 10", "§5 / MPYY EK-2", _durum(R["yesil"] / n, 10, None))
    ekle("Yeşil", "Her komşuluk yeşili ≥ 0,5 ha", "ha (en küçük)", min(R["park_kb"]) / HA, "≥ 0,5", "§5", _durum(min(R["park_kb"]) / HA + 1e-6, 0.5, None))
    tac = R["tac"]
    ekle("Yeşil", "Tahmini ağaç örtüsü (20 yıl)", "%", 100 * tac["oran"], "≥ 30 (15–20 yıl)", "§5 (3-30-300)",
         _durum(100 * tac["oran"], 30, None),
         f"v2: çizimdeki {sayi(tac['sayi'])} ağacın 20 yıllık taç birleşimi (yarıçaplar [V]); aynı v2 geometrisi v1 "
         f"formülüyle %{sayi(100 * R['agac_v1_formul'], 1)}; v1 değeri v1 formülüyle")
    ekle("Yeşil", "Özel bahçe ve avlu (konut başına)", "m²/konut", R["ozel_bahce"] / k, "≥ 10", "Genelge 2026/4 ölçüt 14 (paket G1)",
         _durum(R["ozel_bahce"] / k, 10, None),
         f"ada içi ortak şerit dahil {sayi((R['ozel_bahce'] + R['ortak_bahce']) / k, 1)} m²/konut; kişi başı "
         f"{sayi(R['ozel_bahce'] / n, 1)} m² (simülasyon C: 10,9)", v1_deger=V1["ozel_bahce"] / V1["konut"])
    ekle("Yeşil", "Bahçesi evin kuzeyinde kalan T1/T2 konut payı (kışın gölgede)", "%", 100 * R["kuzey_bahce"], "düşük", "v1 açık soru 4",
         "—", "güney sıra; ada yönü değişmeden çözülemez (bkz. kalan sorunlar)", v1_deger=100 * V1["kuzey_bahce"])

    # okul ve donatı
    ilk_kisi = sum(R["ilkokul"].values()) / n
    ekle("Donatı", "Eğitim alanı / kişi", "m²/kişi", R["egitim"] / n, "4,5 (güncel EK-2: 0,5+2,0+2,0)", "MPYY EK-2 [D]",
         _durum(R["egitim"] / n, 4.5, None))
    ekle("Donatı", "İlkokul arsası", "m²", sum(R["ilkokul"].values()), f"≥ 2,0 m²/kişi = {sayi(2 * n)}; okul başına ≥ 5.000",
         "MPYY EK-2 (17.05.2017) [D]", _durum(ilk_kisi, 2.0, None),
         f"2 okul: A {sayi(R['ilkokul']['A'])} + B {sayi(R['ilkokul']['B'])} m²; {sayi(ilk_kisi, 2)} m²/kişi")
    ekle("Donatı", "Orta ibadet (semt camii) arsası", "m²", next(d for d in pm.DONATILAR if d["tur"] == "semt_camii")["poly"].area,
         "≥ 2.500 ve ≥ 0,5 m²/kişi", "MPYY EK-2 [İ]",
         _durum(next(d for d in pm.DONATILAR if d["tur"] == "semt_camii")["poly"].area, max(2500, 0.5 * n), None))
    kc = [d["poly"].area for d in pm.DONATILAR if d["tur"] == "kucuk_cami"]
    ekle("Donatı", "Küçük cami arsası (en küçük)", "m²", min(kc), "≥ 1.000", "MPYY EK-2 [İ]", _durum(min(kc), 1000 * 0.98, None))
    ekle("Donatı", "Mescit (zemin katta)", "adet", R["mescit_sayisi"], "8 (birim başına 1)", "§9.5",
         "uyumlu" if R["mescit_sayisi"] >= 8 else "sapma", "ağ üzerinde açgözlü kapsama ile seçildi (her birimde ≥ 1)")
    ekle("Donatı", "Kreş (zemin katta)", "adet", R["kres_sayisi"], "2–3 (+ 2 anaokulu)", "§9.5",
         "uyumlu" if R["kres_sayisi"] >= 2 else "sapma", "anaokulu ya da kreşe ≤ 400 m kapsaması için")
    ekle("Donatı", "Otobüs durağı (S1 hattı + toplayıcı)", "adet", R["durak_s1"] + R["durak_toplayici"], "4–6 (S1)", "§9.5", "—",
         f"S1 üzerinde {R['durak_s1']}, toplayıcı yolda {R['durak_toplayici']}")
    ekle("Donatı", "Bölgesel otopark kapasitesi", "araç", R["otopark_yer"], "0,5–0,7 / hane", "§7",
         _durum(R["otopark_yer"] / k, 0.5, 0.7),
         f"hane başına {sayi(R['otopark_yer'] / k, 2)}; 4 mobilite noktası (Z+4); S2 cepleri yalnız engelli, yaşlı, yükleme")
    ekle("Donatı", "Avlu grubu (T3) + bahçe grubu (T1/T2)", "adet", R["avlu_grubu"] + len(R["bahce_grubu"]),
         "190–280, her biri 8–12 hane", "§9.2", _durum(R["avlu_grubu"] + len(R["bahce_grubu"]), 190, 280),
         f"{R['avlu_grubu']} avlu grubu ({min(R['avlu_hane'])}–{max(R['avlu_hane'])} hane, ort. "
         f"{sayi(statistics.mean(R['avlu_hane']), 1)}); {len(R['bahce_grubu'])} bahçe grubu (ort. "
         f"{sayi(statistics.mean(R['bahce_grubu']), 1)} hane)")

    # otopark yönetmeliği
    e = R["ek1"]
    v1e = V1["ek1"]
    ekle("Otopark Yönetmeliği", "Ek-1'e göre gereken otopark (mevcut kural, konut)", "yer", e["mevcut"], "—",
         "Otopark Yön. Ek-1 (RG 25.03.2021) [D]", "—",
         f"hane başına {sayi(e['mevcut'] / k, 2)}; T1 son durum (195 m²) ve T2 dubleksi (219 m²) ≥ 180 m² olduğu için 2 yer",
         v1_deger=v1e["mevcut"])
    ekle("Otopark Yönetmeliği", "Ek-1'e göre gereken otopark (dükkân, 50 m²'ye 1)", "yer", e["dukkan"], "—", "Otopark Yön. Ek-1 [D]", "—",
         "zemin kat dükkânları ve zemin donatıları", v1_deger=v1e["dukkan"])
    ekle("Otopark Yönetmeliği", "Ek-1 gereği (paket O1 reformuyla, konut)", "yer", e["reform"], "—", "paket O1 (öneri)", "—",
         f"her BB 0,5; ≥ 180 m² 1; hane başına {sayi(e['reform'] / k, 2)}", v1_deger=v1e["reform"])
    ekle("Otopark Yönetmeliği", "Planın sağladığı / Ek-1 mevcut gereği", "%",
         100 * R["otopark_yer"] / (e["mevcut"] + e["dukkan"]), "≥ 100 (mevcut kural)", "Otopark Yön. md. 4 [D]",
         "sapma" if R["otopark_yer"] < e["mevcut"] + e["dukkan"] else "uyumlu",
         "fark ancak O2 (bölgesel otopark alanında azami otopark) ve belediye meclisi kararıyla kapanır; md. 8/2 indirimi "
         "parselde yarısının karşılanmasını şart koştuğu için uygulanamaz", v1_deger=None)

    # asansör ve erişilebilirlik
    a = R["asn_toplam"]
    va = V1["asn"]
    er, ve = R["eris"], V1["eris"]
    ekle("Asansör ve erişilebilirlik", "Asansör tesisi (bugünkü uygulama: her merdiven evine)", "adet", a.get("asansor_mevcut", 0),
         "PAİY md. 34/1", "PAİY md. 34/1 (RG 01.07.2026) [D]", "uyumlu",
         f"maliyet ≈ {sayi(a.get('maliyet_mevcut', 0) / 1e6, 1)} milyon TL [V]; T3 Z+3 sokak kanadında 2, T4'te 1",
         v1_deger=va.get("asansor_mevcut", 0))
    ekle("Asansör ve erişilebilirlik", "Asansör tesisi (paket P4: galeriyle tek asansör)", "adet", a.get("asansor_p4", 0), "—", "paket P4 (öneri)", "—",
         f"maliyet ≈ {sayi(a.get('maliyet_p4', 0) / 1e6, 1)} milyon TL [V]", v1_deger=va.get("asansor_p4", 0))
    ekle("Asansör ve erişilebilirlik", "Asansör yeri (3 katlı, birden çok BB)", "adet", a.get("yer", 0), "PAİY md. 34/1", "[D]", "uyumlu",
         "T2'de platform yeri (1,4 × 1,6 m), T3 Z+2 sokak kanadında 2 çekirdekte kuyu", v1_deger=None)
    ekle("Asansör ve erişilebilirlik", "Kaldırma platformu yeri (T1, tek BB; zorunlu değil)", "adet", a.get("platform_yeri", 0), "—", "v2 tasarım kararı", "—",
         "kiler/dolap dikmesi (1,0 × 2,3 m); yaşlanınca platform takılabilir", v1_deger=0)
    ekle("Asansör ve erişilebilirlik", "Zemin katta erişilebilir (eşiksiz) daire payı", "%", 100 * er["zemin"], "≥ 15",
         "paket P4; Genelge ölçüt 17", _durum(100 * er["zemin"], 15, None),
         f"{sayi(er['zemin_adet'])} daire: T2 zemin büyükler dairesi + T3 zemin 2+1 ve 1+1 + gereken gruplarda yan kanat zemin dairesi", v1_deger=100 * ve["zemin"])
    ekle("Asansör ve erişilebilirlik", "Basamaksız ulaşılan konut payı (zemin + asansörlü)", "%", 100 * er["basamaksiz"], "—", "[H]", "—",
         f"T1'lerin zemininde büyükler odası ve duş (aşama 2) ayrıca %{sayi(100 * er['t1_zemin'])}", v1_deger=100 * ve["basamaksiz"])
    ekle("Asansör ve erişilebilirlik", "Binası ölçüt 17'yi sağlayan konut (zemin ≥ %15 erişilebilir BB ya da asansör)", "%",
         100 * R["g17"], "100", "Genelge 2026/4 ölçüt 17 (paket G1)", _durum(100 * R["g17"], 100, None),
         "T1: tek BB, zeminde büyükler odası; T2: 2 BB'den 1'i zeminde; T3 Z+2: grupta ≥ %15 zemin (gerekirse yan kanatta); T3 Z+3 ve T4: asansör",
         v1_deger=None)
    ekle("Asansör ve erişilebilirlik", "Kendi kapısından bahçeye ya da avluya çıkan hane", "%", 100 * er["dogrudan"], "≈90 (simülasyon C varsayımı)",
         "05_zihinsel_simulasyonlar §1.1", _durum(100 * er["dogrudan"], 85, None),
         "T1, T2, T3 zemin daireleri ve yan kanat dubleksleri; T3 üst katları ortak avluya merdivenle iner",
         v1_deger=100 * ve["dogrudan"])
    ekle("Asansör ve erişilebilirlik", "Bir yapıyı paylaşan hane (konut ağırlıklı ortalama)", "hane", er["yapi_hane"], "≈7 (simülasyon C)",
         "05_zihinsel_simulasyonlar §1.1", "—", "", v1_deger=ve["yapi_hane"])

    # ağ
    ekle("Sokak ağı", "Sokak ağı uzunluğu", "km/km²", R["km_km2"], "≥ 18 (BM-Habitat); ≈25", "§4", _durum(R["km_km2"], 18, None),
         f"toplam {sayi(R['ag_uzunluk'] / 1000, 1)} km; toplayıcının yarısı sayıldı")
    ekle("Sokak ağı", "Kavşak yoğunluğu (araç ağı)", "/km²", R["kavsak_arac"], "≥ 80–120", "§4", _durum(R["kavsak_arac"], 80, None))
    ekle("Sokak ağı", "Kavşak yoğunluğu (yaya dahil)", "/km²", R["kavsak_yaya"], "≥ 80–120", "§4", _durum(R["kavsak_yaya"], 80, None))
    ekle("Sokak ağı", "Sokak payı", "%", 100 * R["sokak"] / pm.ALAN.area, "25 (BM-Habitat ≥ 30)", "§4 / §9.3",
         _durum(100 * R["sokak"] / pm.ALAN.area, 23.75, 30))
    ks = R["kesit"]
    ekle("Sokak kesiti", "S2 yaşam sokağı H/W (son durum, K2)", "oran", ks["s2_hw"], "0,7–1,0", "§9.6", _durum(ks["s2_hw"], 0.7, 1.0),
         f"W = {sayi(ks['W_s2'], 1)} m (10 + 2 × {sayi(pm.ON_ESIK_K2, 1)} ön eşik), H = {sayi(ks['H_s2'], 1)} m (3 × 3,1); "
         f"T1 çekirdek döneminde {sayi(ks['s2_hw_cekirdek'], 2)}; K1'de (ön eşik 2,0) {sayi(ks['s2_hw_k1'], 2)}; 21 Aralık "
         f"öğlesi karşı cephede {sayi(ks['s2_aralik_golge'], 1)} m'ye kadar gölge (v1: 2,3 m)", v1_deger=0.64)
    ekle("Sokak kesiti", "S1 mahalle caddesi H/W", "oran", ks["s1_hw"], "0,7–0,8", "§9.6", _durum(ks["s1_hw"], 0.7, 0.8),
         f"W = {sayi(ks['W_s1'], 1)} m, H = {sayi(ks['H_s1'], 1)} m (4,5 + 3 × 3,1)", v1_deger=0.69)

    # erişim
    for tur, etiket, hedef, ust, kaynak in ERISIM:
        e_ = R["erisim"][tur]
        not_ = (f"medyan {sayi(e_['medyan'])} m; %95'lik {sayi(e_['p95'])} m; en uzak {sayi(e_['en_fazla'])} m; "
                f"≤ {sayi(ust)} m: %{sayi(100 * e_['pay_ust'], 1)}")
        ekle("Erişim (ağ mesafesi)", f"{etiket} ≤ {sayi(hedef)} m", "% konut", 100 * e_["pay_hedef"],
             "100", kaynak, _durum(100 * e_["pay_hedef"], 100, None, tolerans=0.05), not_)
    ekle("Erişim (ağ mesafesi)", "İlkokul ≤ 400 m (tercih)", "% konut", 100 * R["ilk_400"], "tercihen 100", "§6.1 (tercihen 400 m)",
         "—", "iki okul; medyan ve kayıt alanları için bkz. EK-2 satırları", v1_deger=100 * V1["ilk400"])
    ekle("Erişim (ağ mesafesi)", R["erisim"]["ibadet_kademe"]["etiket"], "% konut", 100 * R["erisim"]["ibadet_kademe"]["pay_hedef"],
         "100", "MPYY md. 12; PAİY md. 53", _durum(100 * R["erisim"]["ibadet_kademe"]["pay_hedef"], 100, None))
    ekle("Erişim (ağ mesafesi)", "Kapı önü oyun alanı (avlu ya da ada içi ortak bahçe) ya da cep parkı ≤ 150 m", "% konut",
         100 * R["oyun_avlu"], "100", "§6.1 (kapı önü 100 m) / §9.5", _durum(100 * R["oyun_avlu"], 100, None),
         "T3 avlusu ve T1/T2 ortak şeridi kendi haneleri için ≤ 30 m")

    # komşuluk birimleri
    for b in R["birimler"]:
        tk = R["tah_kb"].get(b["no"], {})
        tt = sum(tk.values()) or 1
        ekle("Komşuluk birimi", f"KB-{b['no']}", "konut", b["konut"], "150–300 hane, 500–1.000 kişi", "§1",
             _durum(b["konut"], 150, 300),
             f"{sayi(b['nufus'])} kişi; {sayi(b['alan'] / HA, 2)} ha brüt; {b['mescit']} mescit; tahsis "
             f"K %{sayi(100 * tk.get('kooperatif', 0) / tt)} · S %{sayi(100 * tk.get('sosyal', 0) / tt)} · "
             f"P %{sayi(100 * tk.get('piyasa', 0) / tt)}")

    # v2.1: geleneksel doku ölçütleri (600 m pencere; 09_RAPORLAR/11 §3.1 önerileri)
    mo = R.get("morf")
    if mo:
        hedef = {
            "bina_ha": ("—", "—"), "taban_medyan_m2": ("T1 tabanı 75–90", "uygulanmadı"),
            "yapi_oturumu": ("%25–30", "kısmen"), "net_yapi_oturumu": ("K3 %45–55 · K2 %35–40", "kısmen"),
            "emsal": ("0,75–0,9", "uygulanmadı"), "kat_ort": ("2–4 kat (ort. 2,8–3,2)", "korundu"),
            "kisi_ha": ("120–150", "—"), "kavsak_km2_sokak": ("≥ 300", "uygulandı"),
            "kavsak_km2_arac": ("110–130", "korundu"), "ada_alan_medyan_m2": ("≤ 0,35–0,45 ha", "uygulandı"),
            "ada_cevre_medyan_m": ("≤ 280", "uygulandı"), "ada_arac_alan_medyan_m2": ("≈ 0,95 ha (korunsun)", "korundu"),
            "cephe_arasi_medyan_m": ("S2 11–12", "uygulandı"), "hw_medyan": ("S2 ≈ 0,75–0,8", "uygulandı"),
            "cephe_adimi_m": ("≤ 15–20", "kısmen"), "bina_cephe_medyan_m": ("T1 6,5–7,5; modül 9–12", "kısmen"),
            "kapali_avlu_ha": ("≈ 0,5", "uygulandı"), "kapali_avlu_medyan_m2": ("300–450", "uygulandı"),
            "ada_ici_bos_pay_net": ("K3 %45–55 · K2 %60–65", "kısmen"), "kamusal_yesil_m2_kisi": ("≥ 10", "korundu"),
            "yakinlik_bina_400": ("—", "—"), "ag_verimi_400": ("—", "—"),
        }
        for c, v in mo.items():
            f = v["carpan"]

            def d(x):
                return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else float(x) * f
            h, karar = hedef.get(c, ("—", "—"))
            S.append(("Morfoloji (600 m pencere)", v["ad"], v["birim"], d(v["v1"]), d(v["v21"]), h,
                      "09_RAPORLAR/11 §3.1", karar,
                      f"geleneksel medyan {sayi(d(v['gel']) or 0, v['ond'])} · çağdaş medyan {sayi(d(v['cag']) or 0, v['ond'])}"
                      f" · tam 60 ha: v1 {sayi(d(v['v1_60']) or 0, v['ond'])}, v2.0 {sayi(d(v['v20_60']) or 0, v['ond'])}, "
                      f"v2.1 {sayi(d(v['v21_60']) or 0, v['ond'])}", d(v["v20"])))
    # v2.1: FUE konumu (pilot kentsel mahalle dağılımında yüzdelik puan)
    fu = R.get("fue")
    if fu:
        for k, ad in (("E", "FUE erişim ekseni (E)"), ("C", "FUE çevre-ölçek ekseni (Ç)"), ("FUE", "FUE (altı boyut)")):
            ekle("FUE konumu", ad, "puan", fu[k], "Ç ≥ 55, E ≥ 60" if k != "FUE" else "—", "09_RAPORLAR/10 §7",
                 ("uyumlu" if (k == "E" and fu[k] >= 60) or (k == "C" and fu[k] >= 55) else
                  ("sapma" if k in ("E", "C") else "—")),
                 (f"yaşanan yükseklik {sayi(fu['yukseklik'], 1)} m (konut ağırlıklı kat × 3,1; pilot medyanı 8,4); "
                  f"tek muhtarlık {sayi(R['nufus'])} kişi. İki muhtarlıkla (≈ {sayi(R['nufus'] / 2)} kişi) Ç = "
                  f"{sayi(R['fue_iki']['C'], 1)}") if k == "C" else "05_ANALIZ/kod/fue_model_mahalle.py kuralı",
                 v1_deger=None)
    # tahsis
    for t, ad in pm.TAHSIS_AD.items():
        ekle("Tahsis karması", ad, "% konut", 100 * R["tah_pay"].get(t, 0), f"{sayi(100 * pm.TAHSIS_HEDEF[t])}",
             "§9.4", _durum(100 * R["tah_pay"].get(t, 0), 100 * pm.TAHSIS_HEDEF[t] - 2, 100 * pm.TAHSIS_HEDEF[t] + 2),
             "bahçe grubu, avlu grubu ve T4 parseli düzeyinde; sosyal kiralık T2'ye verilmez", v1_deger=None)
    ekle("Tahsis karması", "Komşuluk biriminde hedef paydan en büyük sapma", "puan", 100 * R["kb_sapma"], "≤ 5", "v2 (dağıtılmış sosyal konut)",
         _durum(100 * R["kb_sapma"], None, 5), "", v1_deger=None)
    ekle("Tahsis karması", "Piyasa payının yapımcılara bölünmesi (ada başına ≤ 40 konut)", "yapımcı (asgari)", R["yapimci_asgari"],
         "—", "Rieselfeld kuralı (§9.7)", "—", f"en kalabalık adada piyasa konutu {sayi(max(R['piyasa_ada'].values()))}",
         v1_deger=None)
    return S


def _ozet(R):
    e = R["erisim"]
    return [
        ("Konut", sayi(R["konut"]), "2.250"),
        ("Nüfus (3,2 kişi/hane)", sayi(R["nufus"]), "7.200"),
        ("Brüt yoğunluk", f"{sayi(R['nufus'] / 60)} kişi/ha", "120"),
        ("Net konut yoğunluğu", f"{sayi(R['konut'] / (R['konut_net'] / HA))} konut/ha", "≈70"),
        ("İlkokul ≤ 500 m (ağ; 2 okul)", yuzde(100 * e["ilkokul"]["pay_hedef"]), "%100"),
        ("İlkokul arsası (A + B)", f"{sayi(sum(R['ilkokul'].values()) / R['nufus'], 2)} m²/kişi", "≥ 2,0"),
        ("≥ 0,5 ha yeşil ≤ 300 m (ağ)", yuzde(100 * e["yesil05"]["pay_ust"]), "%100"),
        ("Kamusal yeşil", f"{sayi(R['yesil'] / R['nufus'], 1)} m²/kişi", "≥ 10"),
        ("Ağaç örtüsü (20 yıl, çizimden)", yuzde(100 * R["tac"]["oran"]), "≥ %30"),
        ("İbadet kademesine erişim", yuzde(100 * e["ibadet_kademe"]["pay_hedef"]), "%100"),
        ("≤ 3 katlı binada oturan", yuzde(100 * R["pay_le3"]), "≈%70"),
        ("T1 payı", yuzde(100 * R["tip"]["T1"]["konut"] / R["konut"]), "%29"),
        ("S2 H/W (son durum)", sayi(R["kesit"]["s2_hw"], 2), "0,7–1,0"),
        ("Zemin katta erişilebilir daire", yuzde(100 * R["eris"]["zemin"]), "≥ %15"),
        ("Bölgesel otopark", f"{sayi(R['otopark_yer'])} araç", "0,5–0,7/hane"),
    ]


def csv_yaz():
    """Sütunlar: v1_degeri · v2_0 · v2_1 · v2_degeri (= v2_1; 05_ANALIZ/kod/fue_model_mahalle.py bu sütunu okur)."""
    R = metrikleri_hesapla()
    v20 = v20_degerleri()
    with open(CIKTI / "metrikler.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kategori", "gosterge", "birim", "v1_degeri", "v2_0", "v2_1", "v2_degeri", "hedef", "hedef_kaynagi",
                    "durum", "not"])
        for kat, ad, birim, v1d, deger, hedef, kaynak, durum, not_, v20_ez in R["satirlar"]:
            def yuv(x):
                return "" if x is None else (round(x, 2) if isinstance(x, float) else x)
            d20 = v20_ez if v20_ez is not None else v20.get((kat, ad))
            w.writerow([kat, ad, birim, yuv(v1d), yuv(d20), yuv(deger), yuv(deger), hedef, kaynak, durum, not_])
    return R


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    R = csv_yaz()
    for kat, ad, birim, v1d, deger, hedef, kaynak, durum, not_, _ in R["satirlar"]:
        d = "" if deger is None else (f"{deger:,.1f}" if isinstance(deger, float) else str(deger))
        e = "" if v1d is None else (f"{v1d:,.1f}" if isinstance(v1d, float) else str(v1d))
        print(f"{kat[:14]:14s} | {ad[:50]:50s} | {e:>9s} → {d:>9s} {birim[:8]:8s} | {hedef[:24]:24s} | {durum:11s} | {not_[:70]}")
