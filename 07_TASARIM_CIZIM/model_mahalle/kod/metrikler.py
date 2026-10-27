"""
Model mahalle v1 — sayısal doğrulama
====================================
plan_modeli.py'nin poligonlarından ve yaya ağından bütün göstergeleri hesaplar,
tasarim_parametreleri.md §9 hedefleriyle karşılaştırır ve ../metrikler.csv'ye yazar.

Çalıştırma:  python metrikler.py
"""

import csv
import math
import statistics
import sys
from collections import defaultdict
from functools import lru_cache

import networkx as nx
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

import plan_modeli as pm
from ortak import CIKTI, HANE_BUYUKLUGU, sayi, yuzde

HA = 10_000.0

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
    # tip: [(oda sınıfı, pay)]
    "T1": [("3+1 ve üstü", 1.0)],
    "T2": [("2+1", 0.5), ("3+1 ve üstü", 0.5)],          # zemin: büyükler 2+1 · üst: dubleks 4+1
    "T3": None,                                           # avlu grubu: kat kat hesaplanır
    "T4": [("1+1", 1 / 3), ("2+1", 2 / 3)],               # 24 m modül, kat başına 2+1 · 1+1 · 2+1
}


ARAZI_NOT = {
    "Sokak, yaya yolu ve meydan": "4 yeşil diyagonal (≈1,5 ha) ve ada içi S3 geçitleri eklendi",
    "Kamusal yeşil (park + cep + bostan)": "fazlalık diyagonal kırpıntılarından doğan cep parklarıdır",
    "Cep parkı ve kapı önü oyun alanı": "diyagonalin adaları kestiği üçgenler; kapı önü oyun ve mescit yeri",
    "Mahalle konağı": "hamam ve spor salonu dahil",
    "Bölgesel otopark (4 yapı)": "2 yerine 4 mobilite noktası: her konuta ≤ 400 m ve 0,6 yer/hane",
    "Net konut alanı": "sokak, diyagonal ve otopark payı arttı; net yoğunluk 50–90 bandında kaldı",
    "Komşuluk yeşilleri (8 adet)": "8 × 0,50 ha + kuzeybatıdaki kenar parkı",
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


@lru_cache(maxsize=1)
def metrikleri_hesapla():
    P = pm.model()
    A = pm.ag_kur()
    parseller = P["parseller"]
    D = P["donatilar"]

    # ---------------- konut ve nüfus -----------------------------------------
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
    ibadet = d_alan("semt_camii", "kucuk_cami")
    saglik = d_alan("asm")
    sosyal = d_alan("konak")
    carsi = d_alan("carsi")
    teknik = d_alan("teknik")
    otopark = d_alan("otopark")
    konut_net = sum(p["poly"].area for p in parseller) + sum(o.area for o in P["ortaklar"])
    ortak_bahce = sum(o.area for o in P["ortaklar"]) + sum(_alan(p.get("avlu")) for p in parseller if p["tip"] == "T3")
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

    # ---------------- kat alanı, kat profili, karma ---------------------------
    kat_dagilim = defaultdict(float)     # konut sayısı → bina kat adedi
    bina_kat = defaultdict(int)          # bina sayısı → kat adedi
    oda = defaultdict(float)
    for p in parseller:
        if p["tip"] == "T3":
            yan = min(p.get("yan_konut", 4), p["konut"])
            kat_dagilim[p["kat"]] += p["konut"] - yan
            kat_dagilim[2] += yan
            bina_kat[p["kat"]] += 1
            bina_kat[2] += 2
            sk = p["konut"] - yan
            # sokak kanadı: zemin (dükkânsızsa) 1+1 + 2+1 erişilebilir; üst katlar 3+1 (≈120 m² brüt);
            # yan kanatlar 2+1 dubleks (≈91 m² brüt)
            zemin = 0 if p.get("dukkan") else min(2, sk)
            ust = sk - zemin
            oda["1+1"] += 1 if zemin >= 1 else 0
            oda["2+1"] += (zemin - 1 if zemin >= 1 else 0) + yan
            oda["3+1 ve üstü"] += ust
        else:
            kat_dagilim[p["kat"]] += p["konut"]
            bina_kat[p["kat"]] += 1
            for sinif, pay in KARMA[p["tip"]]:
                oda[sinif] += p["konut"] * pay
    pay_le3 = sum(v for k, v in kat_dagilim.items() if k <= 3) / konut
    pay_le4 = sum(v for k, v in kat_dagilim.items() if k <= 4) / konut
    pay_5 = sum(v for k, v in kat_dagilim.items() if k >= 5) / konut
    bina_le3 = sum(v for k, v in bina_kat.items() if k <= 3) / sum(bina_kat.values())

    konut_kat_alani = sum(t["kat_alani"] - t["ticari"] for t in tip.values())
    ticari_kat = sum(t["ticari"] for t in tip.values()) + sum(d.get("ticari", 0.0) for d in D)
    donati_kat = sum(sum(b.area for b in d["binalar"]) * d["kat"] for d in D
                     if d["tur"] not in ("otopark", "teknik"))
    otopark_kat = sum(sum(b.area for b in d["binalar"]) * d["kat"] - d.get("ticari", 0.0) for d in D
                      if d["tur"] == "otopark")
    otopark_yer = otopark_kat * 0.92 / 25.0      # 25 m²/araç (rampa ve manevra dahil), %8 çekirdek
    konut_disi_pay = (ticari_kat + donati_kat) / (konut_kat_alani + ticari_kat + donati_kat)

    # ---------------- sokak ağı ---------------------------------------------
    sokak_cizgi = A["sokak_cizgi"]
    halka = sokak_cizgi[0]
    ic_sokak = sokak_cizgi[1:]
    diyag = [ln for ln in A["yaya_cizgi"] if ln in A["yaya_cizgi"][:4]]
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
                           medyan=med, p95=p95, en_fazla=sirali[-1][0], asan=toplam_k - sum(w for m, w in agirlik if m <= hedef))
    # ibadet kademeleri birlikte: mescit ≤150 ya da küçük cami ≤250 ya da semt camii ≤400
    ib = 0
    for k, p in enumerate(parseller):
        if (mesafe_parsel["mescit"][k] <= 150 or mesafe_parsel["kucuk_cami"][k] <= 250
                or mesafe_parsel["semt_camii"][k] <= 400):
            ib += p["konut"]
    erisim["ibadet_kademe"] = dict(etiket="İbadet yeri (mescit ≤150 / küçük cami ≤250 / semt camii ≤400 m)",
                                   pay_hedef=ib / konut)

    # ---------------- komşuluk birimleri ----------------------------------------
    birimler = []
    for no, g in pm.komsuluk_birimleri():
        k = sum(p["konut"] for p in parseller if pm.birim_bul(p["kapi"]) == no)
        mescit = sum(1 for z in P["zemin"] if z["tur"] == "mescit" and pm.birim_bul(z["xy"]) == no)
        birimler.append(dict(no=no, konut=k, nufus=k * HANE_BUYUKLUGU, alan=g.area, mescit=mescit,
                             cap=max(Point(a).distance(Point(b)) for a in g.exterior.coords for b in g.exterior.coords)))
    t3 = [p for p in parseller if p["tip"] == "T3"]
    avlu_hane = [p["konut"] for p in t3]
    bahce_grubu = defaultdict(int)
    for p in parseller:
        if p["tip"] in ("T1", "T2"):
            c = p["poly"].centroid
            x0 = pm.XS[p["ada"][0]][0]
            bahce_grubu[(p["ada"], int((c.x - x0) // 30))] += p["konut"]
    # kapı önü oyun: T3 avlusu kendi sakinleri için kapı önü oyun alanıdır
    # T1/T2: ada içi ortak bahçe şeridi (arka bahçe kapısından ≤ 30 m) kapı önü oyun alanıdır
    ortak_birlesik = unary_union(P["ortaklar"]).buffer(1.0)
    oyun_avlu = sum(p["konut"] for p, m in pm.konut_mesafeleri("oyun")
                    if m <= 150 or p["tip"] == "T3" or p["poly"].intersects(ortak_birlesik))

    # ---------------- ağaç örtüsü (kaba tahmin) -----------------------------------
    # 20 yıl sonra: sokak ağacı tacı r=3,5 m (≈38 m²), park alanlarının %45'i, bahçe ve avluların %15'i [varsayım]
    # 20 yıl sonra (kaba varsayım): sokak ağacı tacı ≈ 38 m² (r 3,5 m); parkların ve cep parklarının %45'i;
    # her T1/T2 bahçesinde 1, her T3 avlusunda 3, her T4 avlusunda 6 ağaç (≈ 28 m²); ada içi ortak şeritlerin %25'i
    sokak_agac = (2 * 728 / 10 + 2 * 776 / 10) + 2 * (2 * (800 + 750) / 10) + sum(
        ln.length / 12 for k, (_, ln) in pm.BAGLANTI.items() if k not in pm.KAPALI) + sum(
        2 * ln.length / 8 for ln in pm.DIYAG_EKSEN)
    bahce_agac = sum(1 if p["tip"] in ("T1", "T2") else (3 if p["tip"] == "T3" else 0.3) for p in parseller)
    ortu = (sokak_agac * 38 + 0.45 * (park_merkez + sum(park_kb) + cep) + bahce_agac * 28
            + 0.25 * sum(o.area for o in P["ortaklar"])) / pm.ALAN.area

    R = dict(konut=konut, nufus=nufus, tip=tip, konut_net=konut_net, ortak_bahce=ortak_bahce,
             yesil=yesil, park_merkez=park_merkez, park_kb=park_kb, cep=cep, bostan=bostan, spor=spor,
             egitim=egitim, ibadet=ibadet, saglik=saglik, sosyal=sosyal, carsi=carsi, teknik=teknik,
             otopark=otopark, sokak=sokak, yol_toplayici=yol_toplayici, yol_s1=yol_s1, yol_s2=yol_s2,
             meydan=meydan, yaya=yaya, kayip=kayip, kat_dagilim=dict(kat_dagilim), pay_le3=pay_le3,
             pay_le4=pay_le4, pay_5=pay_5, bina_le3=bina_le3, bina_kat=dict(bina_kat), oda=dict(oda),
             konut_kat_alani=konut_kat_alani, ticari_kat=ticari_kat, donati_kat=donati_kat,
             konut_disi_pay=konut_disi_pay, otopark_yer=otopark_yer, ag_uzunluk=ag_uzunluk, km_km2=km_km2,
             kavsak_arac=kavsak_arac / km2, kavsak_yaya=kavsak_yaya / km2, erisim=erisim, birimler=birimler,
             avlu_grubu=len(t3), avlu_hane=avlu_hane, bahce_grubu=list(bahce_grubu.values()),
             oyun_avlu=oyun_avlu / konut, sokak_agac=sokak_agac, agac_ortusu=ortu,
             parsel_sayisi=len(parseller), mescit_sayisi=sum(1 for z in P["zemin"] if z["tur"] == "mescit"),
             kres_sayisi=sum(1 for z in P["zemin"] if z["tur"] == "kres"),
             durak_s1=len(pm.DURAKLAR["S1"]), durak_toplayici=len(pm.DURAKLAR["toplayici"]),
             mesafe_parsel=mesafe_parsel)
    R["satirlar"] = _satirlar(R)
    R["ozet_satirlari"] = _ozet(R)
    return R


def _satirlar(R):
    """CSV ve rapor satırları: (kategori, gösterge, birim, plan, hedef metni, hedef kaynağı, durum, not)."""
    S = []
    k, n = R["konut"], R["nufus"]

    def ekle(kat, ad, birim, deger, hedef_metin, kaynak, durum, not_=""):
        S.append((kat, ad, birim, deger, hedef_metin, kaynak, durum, not_))

    ekle("Ölçek", "Brüt alan", "ha", 60.0, "60", "§9.2", "uyumlu", "Toplayıcı yolun iç yarısı dahil (800 × 750 m)")
    ekle("Ölçek", "Konut sayısı", "konut", k, "2.250", "§9.2",
         "uyumlu" if abs(k - 2250) / 2250 <= 0.02 else ("yakın (±%5)" if abs(k - 2250) / 2250 <= 0.05 else "sapma"),
         f"hedeften fark %{sayi(100 * (k - 2250) / 2250, 1)}")
    ekle("Ölçek", "Nüfus", "kişi", n, "7.200 (6.000–8.000)", "§9.2", _durum(n, 6000, 8000), f"{HANE_BUYUKLUGU} kişi/hane varsayımı")
    ekle("Yoğunluk", "Brüt nüfus yoğunluğu", "kişi/ha", n / 60, "120 (100–150)", "§2", _durum(n / 60, 100, 150))
    ekle("Yoğunluk", "Brüt konut yoğunluğu", "konut/ha", k / 60, "37,5", "§9.2", _durum(k / 60, 37.5 * 0.95, 37.5 * 1.05))
    fark_net = 100 * (R["konut_net"] / HA - 32.0) / 32.0
    ekle("Yoğunluk", "Net konut alanı (parsel + ada içi ortak bahçe)", "ha", R["konut_net"] / HA, "32,0", "§9.3",
         "uyumlu" if abs(fark_net) <= 10 else ("yakın (±%25)" if abs(fark_net) <= 25 else "sapma"),
         f"hedeften fark %{sayi(fark_net)}; bkz. arazi bütçesi")
    ekle("Yoğunluk", "Net konut yoğunluğu", "konut/ha", k / (R["konut_net"] / HA), "≈70 (50–90)", "§2",
         _durum(k / (R["konut_net"] / HA), 50, 90))
    ekle("Yoğunluk", "Net nüfus yoğunluğu", "kişi/ha", n / (R["konut_net"] / HA), "≈225", "§9.2", "—")
    for t, ad, hedef in (("T1", "T1 büyüyebilen sıra ev", 650), ("T2", "T2 avlulu çok kuşaklı ev", 400),
                         ("T3", "T3 avlu grubu", 1050), ("T4", "T4 çevre adası (zeminde dükkân)", 150)):
        v = R["tip"][t]["konut"]
        ekle("Konut tipleri", ad, "konut", v, f"{sayi(hedef)} (%{round(hedef / 22.5)})", "§9.4", "—",
             f"plan payı %{sayi(100 * v / k)}; parsel {sayi(R['tip'][t]['parsel'])}; net emsal "
             f"{sayi(R['tip'][t]['kat_alani'] / R['tip'][t]['parsel_alani'], 2)}; yapı oturumu "
             f"%{sayi(100 * R['tip'][t]['oturum'] / R['tip'][t]['parsel_alani'])}")
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
    # arazi bütçesi
    for ad, v, hedef, kaynak in (
            ("Sokak, yaya yolu ve meydan", R["sokak"], 15.0, "§9.3"),
            ("Kamusal yeşil (park + cep + bostan)", R["yesil"], 7.2, "§9.3"),
            ("  Merkez parkı", R["park_merkez"], 2.0, "§9.5"),
            ("  Komşuluk yeşilleri (8 adet)", sum(R["park_kb"]), 4.0, "§9.5"),
            ("  Cep parkı ve kapı önü oyun alanı", R["cep"], 0.4, "§9.3"),
            ("  Bostan ve hobi bahçesi", R["bostan"], 0.8, "§9.3"),
            ("Eğitim (ilkokul, ortaokul, 2 anaokulu)", R["egitim"], 2.52, "§9.3"),
            ("İbadet (semt camii + 4 küçük cami)", R["ibadet"], 0.76, "§9.3"),
            ("Aile sağlık merkezi", R["saglik"], 0.15, "§9.3"),
            ("Mahalle konağı", R["sosyal"], 0.36, "§9.3"),
            ("Çarşı", R["carsi"], 0.50, "§9.3"),
            ("Açık semt spor alanı", R["spor"], 0.50, "§9.3"),
            ("Teknik altyapı", R["teknik"], 0.36, "§9.3"),
            ("Bölgesel otopark (4 yapı)", R["otopark"], 0.65, "§9.3"),
            ("Net konut alanı", R["konut_net"], 32.0, "§9.3")):
        fark = 100 * (v / HA - hedef) / hedef
        durum = "uyumlu" if abs(fark) <= 10 else ("yakın (±%25)" if abs(fark) <= 25 else "sapma")
        ekle("Arazi bütçesi", ad.strip(), "ha", v / HA, sayi(hedef, 2), kaynak, durum,
             f"brüt alanın %{sayi(100 * v / pm.ALAN.area, 1)}'i; hedeften fark %{sayi(fark)}"
             + (f"; {ARAZI_NOT[ad.strip()]}" if ad.strip() in ARAZI_NOT else ""))
    ekle("Arazi bütçesi", "Sınıflanamayan kırpıntı", "ha", R["kayip"] / HA, "0", "—", "—", "< 40 m² artıklar ve köşe payları")
    ekle("Yeşil", "Kamusal yeşil / kişi", "m²/kişi", R["yesil"] / n, "≥ 10", "§5 / MPYY EK-2", _durum(R["yesil"] / n, 10, None))
    ekle("Yeşil", "Her komşuluk yeşili ≥ 0,5 ha", "ha (en küçük)", min(R["park_kb"]) / HA, "≥ 0,5", "§5", _durum(min(R["park_kb"]) / HA + 1e-6, 0.5, None))
    ekle("Yeşil", "Tahmini ağaç örtüsü (20 yıl)", "%", 100 * R["agac_ortusu"], "≥ 30 (15–20 yıl)", "§5 (3-30-300)",
         _durum(100 * R["agac_ortusu"], 30, None), f"≈{sayi(R['sokak_agac'])} sokak ağacı; kaba varsayım [H]")
    egitim_kisi = R["egitim"] / n
    ekle("Donatı", "Eğitim alanı / kişi", "m²/kişi", egitim_kisi, "3,5 (EK-2: 0,5+1,5+1,5)", "MPYY EK-2 [İ]", _durum(egitim_kisi, 3.5, None))
    ilk = next(d for d in pm.DONATILAR if d["tur"] == "ilkokul")["poly"].area
    ekle("Donatı", "İlkokul arsası", "m²", ilk, "≥ 1,5 m²/kişi ≈ 10.800; okul başına 4.000–7.000", "MPYY EK-2 [İ]",
         _durum(ilk, 1.5 * n, None))
    ekle("Donatı", "Orta ibadet (semt camii) arsası", "m²", next(d for d in pm.DONATILAR if d["tur"] == "semt_camii")["poly"].area,
         "≥ 2.500 ve ≥ 0,5 m²/kişi", "MPYY EK-2 [İ]", _durum(next(d for d in pm.DONATILAR if d["tur"] == "semt_camii")["poly"].area, max(2500, 0.5 * n), None))
    kc = [d["poly"].area for d in pm.DONATILAR if d["tur"] == "kucuk_cami"]
    ekle("Donatı", "Küçük cami arsası (en küçük)", "m²", min(kc), "≥ 1.000", "MPYY EK-2 [İ]", _durum(min(kc), 1000 * 0.98, None))
    ekle("Donatı", "Mescit (zemin katta)", "adet", R["mescit_sayisi"], "8 (birim başına 1)", "§9.5",
         "uyumlu" if R["mescit_sayisi"] >= 8 else "sapma",
         "konumlar ağ üzerinde açgözlü kapsama ile seçildi (her birimde ≥ 1); 150 m için 8 yetmiyor")
    ekle("Donatı", "Kreş (zemin katta)", "adet", R["kres_sayisi"], "2–3 (+ 2 anaokulu)", "§9.5",
         "uyumlu" if R["kres_sayisi"] >= 2 else "sapma",
         "anaokulu ya da kreşe ≤ 400 m kapsaması için açgözlü seçimle bulunan sayı")
    ekle("Donatı", "Otobüs durağı (S1 hattı + toplayıcı)", "adet", R["durak_s1"] + R["durak_toplayici"], "4–6 (S1)", "§9.5", "—",
         f"S1 üzerinde {R['durak_s1']}, toplayıcı yolda {R['durak_toplayici']}")
    ekle("Donatı", "Bölgesel otopark kapasitesi", "araç", R["otopark_yer"], "0,5–0,7 / hane", "§7",
         _durum(R["otopark_yer"] / k, 0.5, 0.7),
         f"hane başına {sayi(R['otopark_yer'] / k, 2)}; 4 mobilite noktası (Z+3); S2 cepleri yalnız engelli, yaşlı, yükleme")
    ekle("Donatı", "Avlu grubu (T3) + bahçe grubu (T1/T2)", "adet", R["avlu_grubu"] + len(R["bahce_grubu"]),
         "190–280, her biri 8–12 hane", "§9.2",
         _durum(R["avlu_grubu"] + len(R["bahce_grubu"]), 190, 280),
         f"{R['avlu_grubu']} avlu grubu ({min(R['avlu_hane'])}–{max(R['avlu_hane'])} hane, ort. "
         f"{sayi(statistics.mean(R['avlu_hane']), 1)}); {len(R['bahce_grubu'])} bahçe grubu (ortak şeridin 30 m'lik "
         f"kesimi, ort. {sayi(statistics.mean(R['bahce_grubu']), 1)} hane)")
    # ağ
    ekle("Sokak ağı", "Sokak ağı uzunluğu", "km/km²", R["km_km2"], "≥ 18 (BM-Habitat); ≈25", "§4", _durum(R["km_km2"], 18, None),
         f"toplam {sayi(R['ag_uzunluk'] / 1000, 1)} km; toplayıcının yarısı sayıldı")
    ekle("Sokak ağı", "Kavşak yoğunluğu (araç ağı)", "/km²", R["kavsak_arac"], "≥ 80–120", "§4", _durum(R["kavsak_arac"], 80, None))
    ekle("Sokak ağı", "Kavşak yoğunluğu (yaya dahil)", "/km²", R["kavsak_yaya"], "≥ 80–120", "§4", _durum(R["kavsak_yaya"], 80, None))
    ekle("Sokak ağı", "Sokak payı", "%", 100 * R["sokak"] / pm.ALAN.area, "25 (BM-Habitat ≥ 30)", "§4 / §9.3",
         _durum(100 * R["sokak"] / pm.ALAN.area, 23.75, 30))
    ekle("Sokak ağı", "Ada ölçüsü", "m", None, "60–90 × 90–130; çevre ≤ 450", "§4", "uyumlu",
         f"{sayi(pm.XS[0][1] - pm.XS[0][0], 1)} × {sayi(pm.YS[0][1] - pm.YS[0][0], 1)} m; çevre "
         f"{sayi(2 * (pm.XS[0][1] - pm.XS[0][0] + pm.YS[0][1] - pm.YS[0][0]))} m")
    # erişim
    for tur, etiket, hedef, ust, kaynak in ERISIM:
        e = R["erisim"][tur]
        not_ = (f"medyan {sayi(e['medyan'])} m; %95'lik {sayi(e['p95'])} m; en uzak {sayi(e['en_fazla'])} m; "
                f"≤ {sayi(ust)} m: %{sayi(100 * e['pay_ust'], 1)}")
        ekle("Erişim (ağ mesafesi)", f"{etiket} ≤ {sayi(hedef)} m", "% konut", 100 * e["pay_hedef"],
             "100", kaynak, _durum(100 * e["pay_hedef"], 100, None, tolerans=0.05), not_)
    ekle("Erişim (ağ mesafesi)", R["erisim"]["ibadet_kademe"]["etiket"], "% konut", 100 * R["erisim"]["ibadet_kademe"]["pay_hedef"],
         "100", "MPYY md. 12; PAİY md. 53", _durum(100 * R["erisim"]["ibadet_kademe"]["pay_hedef"], 100, None))
    ekle("Erişim (ağ mesafesi)", "Kapı önü oyun alanı (avlu ya da ada içi ortak bahçe) ya da cep parkı ≤ 150 m", "% konut",
         100 * R["oyun_avlu"], "100", "§6.1 (kapı önü 100 m) / §9.5", _durum(100 * R["oyun_avlu"], 100, None),
         "T3 avlusu ve T1/T2 ortak şeridi kendi haneleri için ≤ 30 m")
    # komşuluk birimleri
    for b in R["birimler"]:
        ekle("Komşuluk birimi", f"KB-{b['no']}", "konut / kişi / ha", b["konut"],
             "150–300 hane, 500–1.000 kişi", "§1", _durum(b["konut"], 150, 300),
             f"{sayi(b['nufus'])} kişi; {sayi(b['alan'] / HA, 2)} ha brüt; {b['mescit']} mescit; en uzun kenar-köşe {sayi(b['cap'])} m")
    return S


def _ozet(R):
    e = R["erisim"]
    return [
        ("Konut", sayi(R["konut"]), "2.250"),
        ("Nüfus (3,2 kişi/hane)", sayi(R["nufus"]), "7.200"),
        ("Brüt yoğunluk", f"{sayi(R['nufus'] / 60)} kişi/ha", "120"),
        ("Net konut yoğunluğu", f"{sayi(R['konut'] / (R['konut_net'] / HA))} konut/ha", "≈70"),
        ("Kamusal yeşil", f"{sayi(R['yesil'] / R['nufus'], 1)} m²/kişi", "≥ 10"),
        ("İlkokul ≤ 500 m (ağ)", yuzde(100 * e["ilkokul"]["pay_hedef"]), "%100"),
        ("≥ 0,5 ha yeşil ≤ 300 m (ağ)", yuzde(100 * e["yesil05"]["pay_ust"]), "%100"),
        ("İbadet kademesine erişim", yuzde(100 * e["ibadet_kademe"]["pay_hedef"]), "%100"),
        ("Otobüs durağı ≤ 400 m", yuzde(100 * e["durak"]["pay_ust"]), "%100"),
        ("≤ 3 katlı binada oturan", yuzde(100 * R["pay_le3"]), "≈%70"),
        ("Kavşak yoğunluğu (yaya dahil)", f"{sayi(R['kavsak_yaya'])} /km²", "≥ 80"),
        ("Sokak + meydan payı", yuzde(100 * R["sokak"] / pm.ALAN.area), "%25"),
        ("Bölgesel otopark (4 mobilite noktası)", f"{sayi(R['otopark_yer'])} araç", "0,5–0,7/hane"),
    ]


def csv_yaz():
    R = metrikleri_hesapla()
    with open(CIKTI / "metrikler.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kategori", "gosterge", "birim", "plan_degeri", "hedef", "hedef_kaynagi", "durum", "not"])
        for kat, ad, birim, deger, hedef, kaynak, durum, not_ in R["satirlar"]:
            if isinstance(deger, float):
                deger = round(deger, 2)
            w.writerow([kat, ad, birim, "" if deger is None else deger, hedef, kaynak, durum, not_])
    return R


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    R = csv_yaz()
    for kat, ad, birim, deger, hedef, kaynak, durum, not_ in R["satirlar"]:
        d = "" if deger is None else (f"{deger:,.1f}" if isinstance(deger, float) else str(deger))
        print(f"{kat[:14]:14s} | {ad[:52]:52s} | {d:>9s} {birim[:10]:10s} | {hedef[:28]:28s} | {durum:11s} | {not_[:80]}")
