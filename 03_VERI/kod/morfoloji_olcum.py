"""
Geleneksel ve çağdaş dokuların morfolojisi — 600 × 600 m örneklem kareleri
==========================================================================
Faz 3 · geleneksel doku morfolojisi. Her çalışma alanı için 600 × 600 m'lik (36 ha) bir
kare örneklem alınır; bina, sokak, ada ve nüfus aynı ölçütlerle ölçülür. Model mahalle v1
de aynı ölçütlerle (merkezli 600 m pencere ve tam 60 ha) hesaplanır.

Girdi
  03_VERI/ham/osm/turkey-latest.osm.pbf           Geofabrik, 25.10.2026
  03_VERI/ham/bina/ms_<quadkey>/<quadkey>.csv.gz  Microsoft Global ML Building Footprints
                                                  (yalnız OSM kapsaması eksik alanlarda ek kaynak)
  03_VERI/ham/ghsl/tif/GHS_BUILT_H_ANBH_E2018_*   ortalama net bina yüksekliği, 100 m, ESRI:54009
  03_VERI/ham/ghsl/tif/GHS_POP_E2020_*            nüfus, 100 m, ESRI:54009
  03_VERI/islenmis/ilce_paneli_genis.csv          ilçe ortalama hane büyüklüğü (nüfus 2025 / hane)
  07_TASARIM_CIZIM/model_mahalle/kod/plan_modeli.py  model mahalle v1 geometrisi (yalnız okunur)

Çıktı
  03_VERI/islenmis/morfoloji_alanlar.gpkg         katmanlar: alanlar, binalar, sokaklar, adalar (EPSG:4326)
  05_ANALIZ/sonuclar/morfoloji_karsilastirma.csv  her alan bir satır
  05_ANALIZ/sonuclar/morfoloji_kat_dogrulama.csv  OSM kat etiketi ile GHSL yüksekliği karşılaştırması
  04_HARITA/morfoloji/figur_zemin_<kod>.png|svg, figur_zemin_levha.png|svg, morfoloji_olcutler.png|svg

Çalıştırma
  python morfoloji_olcum.py            kesit (gerekirse) + ölçüm + çizim
  python morfoloji_olcum.py --cizim    yalnız çizim (GPKG ve CSV'den)
  PBF'den alan kesiti ilk çalıştırmada çıkarılır (≈3 dk) ve önbelleğe yazılır
  (MORFOLOJI_ONBELLEK ortam değişkeni; varsayılan sistem geçici klasörü).

Tanımlar (ayrıntı: 09_RAPORLAR/11_geleneksel_doku_morfolojisi.md §2)
  Arazi              kare − OSM su alanları
  Yapı oturumu (GSI) Σ bina taban alanı (kareye kırpılmış) / arazi
  Kat                building:levels → height/3 → GHSL ANBH/3 (yuvarlanmış, en az 1) → alandaki etiketli medyan
  Emsal (FSI)        Σ taban × kat / arazi (brüt). GHSL/3 orta ve yüksek binalarda katı düşük tahmin eder;
                     etiketli binalarla karşılaştırma morfoloji_kat_dogrulama.csv dosyasında
  Nüfus              GHS-POP 2020, karenin hücrelerle kesişim oranına göre; konut ≈ nüfus / ilçe hane büyüklüğü
  Sokak ağı          "araç": araç trafiğine açık kamusal yollar (service yalnız service=alley ya da
                     alt türü boşsa); "sokak": araç + yaya sokağı, merdiven, patika, yaya yolu
                     (kaldırım ve yaya geçidi çizgileri hariç); "yürüme": tüm yürünebilir yollar
  Kavşak             ≥ 3 yöne bağlanan düğüm; 5 m içindeki düğümler tek kavşak sayılır
  Ada                sokak ağı eksenlerinin çevrelediği çokgen (eksenden eksene, brüt); 20 ha üstü hariç
  Cephe arası (W)    sokak ekseninden 3 m arayla dik ışın; iki yanda 30 m içindeki ilk bina cephesi
  Yakınlık           bina girişinden (en yakın yol noktası) 400 m yürüme ağı mesafesindeki bina,
                     inşaat alanı ve nüfus
"""
from __future__ import annotations

import argparse
import glob
import gzip
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

import geopandas as gpd
import matplotlib
import networkx as nx
import numpy as np
import pandas as pd
import rasterio
import shapely
from pyproj import Transformer
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
from shapely import wkb
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box, shape
from shapely.strtree import STRtree

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
PBF = KOK / "03_VERI" / "ham" / "osm" / "turkey-latest.osm.pbf"
MS_KLASOR = KOK / "03_VERI" / "ham" / "bina"
TIF = KOK / "03_VERI" / "ham" / "ghsl" / "tif"
PANEL = KOK / "03_VERI" / "islenmis" / "ilce_paneli_genis.csv"
MODEL_KOD = KOK / "07_TASARIM_CIZIM" / "model_mahalle" / "kod"
GPKG = KOK / "03_VERI" / "islenmis" / "morfoloji_alanlar.gpkg"
CSV = KOK / "05_ANALIZ" / "sonuclar" / "morfoloji_karsilastirma.csv"
CSV_KAT = KOK / "05_ANALIZ" / "sonuclar" / "morfoloji_kat_dogrulama.csv"
HARITA = KOK / "04_HARITA" / "morfoloji"
ONBELLEK = Path(os.environ.get("MORFOLOJI_ONBELLEK", tempfile.gettempdir())) / "tr_tamirat_morfoloji"

KENAR = 600.0          # m, örneklem karesi
PAY = 500.0            # m, kare çevresinde okunan şerit (ağ ve yakınlık kenar etkisi)
KAT_YUK = 3.0          # m, kat yüksekliği
ISIN = 30.0            # m, cephe arama ışını (eksenden bir yana)
ISIN_ADIM = 3.0        # m, ışın aralığı
KAVSAK_TAMPON = 10.0   # m, ışın örneklemesinde kavşak çevresi dışlama
CEPHE_ESIK = 15.0      # m, "sokağa cephe veren bina" için eksenden en fazla uzaklık
KAVSAK_TOL = 5.0       # m, kavşak birleştirme yarıçapı
YAKINLIK = 400.0       # m, yürüme ağı mesafesi
YAKINLIK_ORNEK = 700   # başlangıç binası sayısı (rastgele, tohum 7)
ADA_UST = 200_000.0    # m², bundan büyük çokgen "ada" sayılmaz
MS_ORTUSME = 0.2       # MS izi, alanının bu payından fazlası OSM binasıyla örtüşüyorsa eklenmez
OSM_YETERLI = 0.85     # karedeki MS izlerinin bu payı OSM'de bir binaya (≤ 1 m) değiyorsa yalnız OSM kullanılır
MODEL_HANE = 3.2       # kişi/hane (model mahalle v1 varsayımı)

# --- Çalışma alanları ------------------------------------------------------------
# lat/lon: 600 × 600 m karenin merkezi (UTM ızgarasına hizalı). Merkezler OSM yer adları,
# bina dokusu, GHSL yüksekliği ve ilçe sınırlarıyla doğrulandı (rapor §2.1).
# ms: Microsoft ayak izi karosu (quadkey, seviye 9); yalnız OSM kapsaması yetersizse kullanılır.
ALANLAR = [
    dict(kod="G1", ad="Safranbolu Çarşı", kisa="Safranbolu Çarşı", grup="geleneksel", il="Karabük",
         ilce="SAFRANBOLU", lat=41.2450, lon=32.6930, ms="120323332",
         dayanak="İzzet Mehmet Paşa Camii, Cinci Hamamı, Saat Kulesi",
         uyari="OSM'de iç sokakların çoğu yok: sokak, ada, cephe ve yakınlık ölçütleri güvenilmez"),
    dict(kod="G2", ad="Safranbolu Bağlar", kisa="Safranbolu Bağlar", grup="geleneksel", il="Karabük",
         ilce="SAFRANBOLU", lat=41.2620, lon=32.6700, ms="120323332",
         dayanak="Çarşı'nın ≈2,5 km kuzeybatısı; bahçe içinde ayrık evler"),
    dict(kod="G3", ad="Beypazarı tarihî çekirdek", kisa="Beypazarı", grup="geleneksel", il="Ankara",
         ilce="BEYPAZARI", lat=40.1695, lon=31.9180, ms="122101103",
         dayanak="Alaaddin Camii çevresi, tarihî konut dokusu"),
    dict(kod="G4", ad="İstanbul Fatih — Zeyrek", kisa="Fatih Zeyrek", grup="geleneksel", il="İstanbul",
         ilce="FATİH", lat=41.0187, lon=28.9535, ms=None,
         dayanak="Zeyrek Camii, Zeyrek Çinili Hamam, Fatih Camii; Atatürk Bulvarı'nın batısı"),
    dict(kod="G5", ad="İstanbul Fatih — Süleymaniye–Vefa", kisa="Fatih Süleymaniye", grup="geleneksel",
         il="İstanbul", ilce="FATİH", lat=41.0168, lon=28.9620, ms=None,
         dayanak="Süleymaniye Camii, Vefa Kilise Camii, Kalenderhane; Atatürk Bulvarı'nın doğusu"),
    dict(kod="G6", ad="Birgi (Ödemiş, İzmir)", kisa="Birgi", grup="geleneksel", il="İzmir", ilce="ÖDEMİŞ",
         lat=38.2545, lon=28.0650, ms="122100313", dayanak="Birgi köy dokusu (Ödemiş ilçesi)"),
    dict(kod="G7", ad="Antakya eski şehir", kisa="Antakya", grup="geleneksel", il="Hatay", ilce="ANTAKYA",
         lat=36.2015, lon=36.1645, ms=None, dayanak="Asi'nin doğusu, Kurtuluş Caddesi çevresi", yikilan_dahil=True,
         uyari="OSM binaları Şubat 2023 durumunda; 'destroyed:building' etiketli binalar deprem öncesi dokuya dahil edildi"),
    dict(kod="C1", ad="Esenyurt (yüksek bloklu banliyö)", kisa="Esenyurt", grup="çağdaş", il="İstanbul",
         ilce="ESENYURT", lat=41.0170, lon=28.6840, ms="120323222", dayanak="site blokları ve kuleler"),
    dict(kod="C2", ad="Başakşehir 1.–2. Etap (planlı yüksek)", kisa="Başakşehir", grup="çağdaş",
         il="İstanbul", ilce="BAŞAKŞEHİR", lat=41.1025, lon=28.7890, ms="120323222",
         dayanak="Başakşehir 1. ve 2. Etap Konutları"),
    dict(kod="C3", ad="Silivri merkez (orta katlı)", kisa="Silivri", grup="çağdaş", il="İstanbul",
         ilce="SİLİVRİ", lat=41.0750, lon=28.2477, ms="120323222", dayanak="Silivri kent merkezi"),
    dict(kod="C4", ad="Konya Meram (yeni konut alanı)", kisa="Konya Meram", grup="çağdaş", il="Konya",
         ilce="MERAM", lat=37.8705, lon=32.4565, ms=None, dayanak="4–6 katlı apartman ızgarası"),
    dict(kod="C5", ad="Kayseri Kocasinan (yeni konut alanı)", kisa="Kayseri Kocasinan", grup="çağdaş",
         il="Kayseri", ilce="KOCASİNAN", lat=38.7435, lon=35.4610, ms=None,
         dayanak="site kuleleri ve apartman sıraları"),
    dict(kod="C6", ad="Ankara Mamak TOKİ", kisa="Ankara Mamak TOKİ", grup="çağdaş", il="Ankara",
         ilce="MAMAK", lat=39.9410, lon=32.9010, ms=None,
         dayanak="TOKİ 1–2, TOKİ Aydoğdu Sitesi, Toki 510 Konutları, Mamak TOKİ İlkokulu (OSM adları)"),
]
MODEL_ALANLAR = [
    dict(kod="M1", ad="Model mahalle v1 (600 m pencere)", kisa="Model v1 (600 m)", grup="model",
         il="—", ilce=None, pencere=(100.0, 75.0, 700.0, 675.0), dayanak="plan merkezli 600 × 600 m"),
    dict(kod="M0", ad="Model mahalle v1 (tam 60 ha)", kisa="Model v1 (60 ha)", grup="model",
         il="—", ilce=None, pencere=(0.0, 0.0, 800.0, 750.0), dayanak="800 × 750 m"),
]

# --- Sokak sınıfları -----------------------------------------------------------------
ARAC = {"motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary",
        "secondary_link", "tertiary", "tertiary_link", "unclassified", "residential", "living_street",
        "road", "busway"}
YAYA = {"pedestrian", "footway", "steps", "path"}
KALDIRIM = {"sidewalk", "crossing", "traffic_island", "access_aisle", "link"}
YURUNMEZ = {"motorway", "motorway_link", "trunk", "trunk_link"}
DISLA = {"construction", "proposed", "platform", "bus_stop", "elevator", "raceway", "rest_area",
         "services", "escape", "emergency_bay", "abandoned", "disused", "razed", "bridleway",
         "via_ferrata", "no"}
YARIM_GEN = {  # m, sınıf varsayılan yarım genişliği (net ada tahmini; varsayım)
    "motorway": 15, "trunk": 12, "primary": 10, "secondary": 8, "tertiary": 6, "unclassified": 4,
    "residential": 4, "living_street": 3, "road": 4, "busway": 4, "service": 2.5, "pedestrian": 3,
    "footway": 1.5, "steps": 1.5, "path": 1.0, "track": 2.0, "cycleway": 1.0, "corridor": 1.0,
}
BINA_DISI = {"no", "roof", "ruins", "demolished", "destroyed", "collapsed", "razed", "removed",
             "abandoned", "damaged", "carport", "canopy", "shelter"}
YASAM = ("demolished", "destroyed", "razed", "removed", "was", "abandoned", "ruins", "disused")
YESIL_LEISURE = {"park", "playground", "recreation_ground", "common", "dog_park", "garden"}
YESIL_LANDUSE = {"recreation_ground", "village_green"}
DEPREM = "2023-02-06"

# --- Görsel dil --------------------------------------------------------------------------
R_BINA = "#0b0b0b"
R_ZEMIN = "#fcfcfb"
R_MAVI = "#2a78d6"      # çağdaş
R_TURUNCU = "#eb6834"   # geleneksel
R_SU = "#dfe6ec"
R_IZGARA = "#e6e4de"
R_METIN = "#1f1d1a"
R_METIN2 = "#5d5a54"
R_BANT = "#ecebe7"
GRUP_RENK = {"geleneksel": R_TURUNCU, "çağdaş": R_MAVI, "model": R_BINA}
GRUP_AD = {"geleneksel": "Geleneksel doku", "çağdaş": "Çağdaş doku", "model": "Model mahalle v1"}
GRUP_IM = {"geleneksel": "o", "çağdaş": "s", "model": "D"}
plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})


def tr(metin):
    """1,234.5 -> 1.234,5 (Türkçe sayı biçimi)."""
    return str(metin).replace(",", "§").replace(".", ",").replace("§", ".")


def sayi(v, ond=0):
    if v is None or (isinstance(v, (float, np.floating)) and not np.isfinite(v)):
        return "—"
    return tr(f"{v:,.{ond}f}")


def yuzde(v, ond=0):
    if v is None or not np.isfinite(v):
        return "—"
    return "%" + sayi(100 * v, ond)


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# =============================================================================
# 1. Alan geometrisi
# =============================================================================
def utm_epsg(lon):
    return 32600 + int((lon + 180) // 6) + 1


def donustur(g, tf):
    return shapely.transform(g, lambda c: np.column_stack(tf.transform(c[:, 0], c[:, 1])))


def alan_hazirla(a):
    epsg = utm_epsg(a["lon"])
    ileri = Transformer.from_crs(4326, epsg, always_xy=True)
    geri = Transformer.from_crs(epsg, 4326, always_xy=True)
    x0, y0 = ileri.transform(a["lon"], a["lat"])
    h = KENAR / 2
    S = box(x0 - h, y0 - h, x0 + h, y0 + h)
    E = box(x0 - h - PAY, y0 - h - PAY, x0 + h + PAY, y0 + h + PAY)
    El = donustur(E.segmentize(50), geri)
    w, s, e, n = El.bounds
    a.update(epsg=epsg, ileri=ileri, geri=geri, S=S, E=E, x0=x0, y0=y0, bbox=(s - 0.001, w - 0.001, n + 0.001, e + 0.001))
    return a


# =============================================================================
# 2. OSM kesiti ve okuma
# =============================================================================
def kesit_yolu(alanlar):
    anahtar = json.dumps([[round(v, 5) for v in a["bbox"]] for a in alanlar]) + str(PBF.stat().st_size)
    return ONBELLEK / f"kesit_{hashlib.md5(anahtar.encode()).hexdigest()[:10]}.osm.pbf"


def kesit_olustur(alanlar, hedef):
    import osmium
    hedef.parent.mkdir(parents=True, exist_ok=True)
    kutular = [a["bbox"] for a in alanlar]

    def icinde(lat, lon):
        return any(s <= lat <= n and w <= lon <= e for s, w, n, e in kutular)

    def yakin(lat, lon):
        return any(s - 0.25 <= lat <= n + 0.25 and w - 0.25 <= lon <= e + 0.25 for s, w, n, e in kutular)

    log("PBF kesiti çıkarılıyor:", PBF.name, round(PBF.stat().st_size / 1e6), "MB →", hedef)
    yollar = set()
    gecici = hedef.with_suffix(".tmp.pbf")
    with osmium.BackReferenceWriter(str(gecici), ref_src=str(PBF), overwrite=True, remove_tags=False) as yaz:
        fp = osmium.FileProcessor(str(PBF)).with_locations().with_filter(
            osmium.filter.EntityFilter(osmium.osm.WAY | osmium.osm.RELATION))
        for o in fp:
            if o.is_way():
                nds = o.nodes
                if len(nds) == 0 or not nds[0].location.valid() or not yakin(nds[0].location.lat, nds[0].location.lon):
                    continue
                for nd in nds:
                    L = nd.location
                    if L.valid() and icinde(L.lat, L.lon):
                        yaz.add(o)
                        yollar.add(o.id)
                        break
            elif o.is_relation():
                if any(m.type == "w" and m.ref in yollar for m in o.members):
                    yaz.add(o)
    gecici.replace(hedef)
    log("kesit hazır:", round(hedef.stat().st_size / 1e6, 1), "MB")


def osm_oku(kesit, alanlar):
    """Kesitten her alanın bina, yol, su, yeşil ve mahalle sınırı nesnelerini toplar (WGS84)."""
    import osmium
    wf = osmium.geom.WKBFactory()
    kutular = [(a["kod"], a["bbox"]) for a in alanlar]

    def hangi(lat, lon):
        return [k for k, (s, w, n, e) in kutular if s <= lat <= n and w <= lon <= e]

    V = {k: dict(bina=[], yol=[], su=[], yesil=[], mezar=[], meydan=[], dongu=[], sinir=[], kiyi=[], bina_disi=Counter())
         for k, _ in kutular}
    for o in osmium.FileProcessor(str(kesit)).with_areas():
        if o.is_area():
            t = o.tags
            tur = None
            b = t.get("building")
            if b is not None:
                tur = "bina" if b not in BINA_DISI else "bina_disi"
            elif any(f"{p}:building" in t for p in YASAM):
                tur = "dongu"
            elif t.get("natural") == "water" or t.get("waterway") == "riverbank" or t.get("landuse") in ("reservoir", "basin"):
                tur = "su"
            elif (t.get("leisure") in YESIL_LEISURE and not (t.get("leisure") == "garden" and (
                    t.get("access") in ("private", "no") or t.get("garden:type") == "residential"))) or t.get("landuse") in YESIL_LANDUSE:
                tur = "yesil"
            elif t.get("landuse") == "cemetery" or t.get("amenity") == "grave_yard":
                tur = "mezar"
            elif t.get("place") == "square" or (t.get("highway") == "pedestrian" and t.get("area") == "yes"):
                tur = "meydan"
            elif t.get("boundary") == "administrative" and t.get("admin_level") in ("8", "9", "10") and "name" in t:
                tur = "sinir"
            if tur is None:
                continue
            try:
                g = wkb.loads(wf.create_multipolygon(o), hex=True)
            except Exception:
                continue
            if tur == "sinir":
                for k, (s, w, n, e) in kutular:
                    if g.intersects(box(w, s, e, n)):
                        V[k]["sinir"].append((g, t.get("name"), t.get("admin_level")))
                continue
            c = g.representative_point()
            for k in hangi(c.y, c.x):
                if tur == "bina":
                    V[k]["bina"].append(dict(geometry=g, building=b, levels=t.get("building:levels"),
                                             height=t.get("height"), name=t.get("name"), osm_id=o.orig_id(),
                                             yol=o.from_way(), zaman=str(o.timestamp)[:10], surum=o.version))
                elif tur == "bina_disi":
                    V[k]["bina_disi"][b] += 1
                elif tur == "dongu":
                    V[k]["dongu"].append(dict(geometry=g, zaman=str(o.timestamp)[:10],
                                              anahtar=[a for a in dict(t) if a.endswith(":building")]))
                else:
                    V[k][tur].append(g)
        elif o.is_way():
            t = o.tags
            if "highway" in t and t.get("area") != "yes":
                ids, lon, lat = [], [], []
                for nd in o.nodes:
                    if nd.location.valid():
                        ids.append(nd.ref)
                        lon.append(nd.location.lon)
                        lat.append(nd.location.lat)
                if len(ids) < 2:
                    continue
                ks = set()
                for la_, lo_ in zip(lat[:: max(1, len(lat) // 8)] + [lat[-1]], lon[:: max(1, len(lon) // 8)] + [lon[-1]]):
                    ks.update(hangi(la_, lo_))
                for k in ks:
                    V[k]["yol"].append(dict(ids=ids, lon=np.array(lon), lat=np.array(lat), hw=t["highway"],
                                            footway=t.get("footway"), service=t.get("service"), foot=t.get("foot"),
                                            access=t.get("access"), name=t.get("name"), osm_id=o.id))
            if t.get("natural") == "coastline":
                c = [(nd.location.lon, nd.location.lat) for nd in o.nodes if nd.location.valid()]
                if len(c) >= 2:
                    for k in set(sum((hangi(la_, lo_) for lo_, la_ in c), [])):
                        V[k]["kiyi"].append(LineString(c))
    return V


# =============================================================================
# 3. Microsoft ayak izleri (ek kaynak)
# =============================================================================
def ms_oku(a):
    p = MS_KLASOR / f"ms_{a['ms']}" / f"{a['ms']}.csv.gz"
    if not p.exists():
        log("  MS karosu yok:", p)
        return []
    s, w, n, e = a["bbox"]
    out = []
    with gzip.open(p, "rt", encoding="utf-8") as f:
        for satir in f:
            if not satir.strip():
                continue
            o = json.loads(satir)
            c = o["geometry"]["coordinates"][0][0]
            if not (w - 0.002 <= c[0] <= e + 0.002 and s - 0.002 <= c[1] <= n + 0.002):
                continue
            g = shape(o["geometry"])
            if g.is_valid and not g.is_empty:
                out.append(donustur(g, a["ileri"]))
    return out


# =============================================================================
# 4. GHSL
# =============================================================================
def ghsl_oku(a):
    to54 = Transformer.from_crs(a["epsg"], "ESRI:54009", always_xy=True)
    E54 = donustur(a["E"].segmentize(50), to54).buffer(200)
    out = {}
    for tur in ("POP", "BUILT_H"):
        for f in sorted(glob.glob(str(TIF / f"GHS_{tur}_*" / "*.tif"))):
            with rasterio.open(f) as r:
                b = r.bounds
                x0, y0, x1, y1 = E54.bounds
                if not (b.left <= x0 and b.right >= x1 and b.bottom <= y0 and b.top >= y1):
                    continue
                win = rasterio.windows.from_bounds(x0, y0, x1, y1, transform=r.transform).round_offsets().round_lengths()
                arr = r.read(1, window=win, boundless=True, fill_value=0).astype(float)
                out[tur] = (arr, r.window_transform(win))
                break
    P, trP = out["POP"]
    H, trH = out["BUILT_H"]
    P[P < 0] = 0
    H[(H < 0) | (H > 250)] = 0
    return dict(P=P, trP=trP, H=H, trH=trH, to54=to54)


def hucre_indeksi(gh, x, y, anahtar="trH"):
    tr_ = gh[anahtar]
    X, Y = gh["to54"].transform(np.asarray(x), np.asarray(y))
    col = np.floor((X - tr_.c) / tr_.a).astype(int)
    row = np.floor((Y - tr_.f) / tr_.e).astype(int)
    return row, col


def ghsl_kare(gh, S):
    """Karenin GHS-POP toplamı (kesişim oranıyla), GHSL yapılı hücre sayısı ve ortalama yükseklik."""
    S54 = donustur(S.segmentize(20), gh["to54"])
    P, trP, H = gh["P"], gh["trP"], gh["H"]
    x0, y0, x1, y1 = S54.bounds
    c0 = int(np.floor((x0 - trP.c) / trP.a)) - 1
    c1 = int(np.floor((x1 - trP.c) / trP.a)) + 1
    r0 = int(np.floor((y1 - trP.f) / trP.e)) - 1
    r1 = int(np.floor((y0 - trP.f) / trP.e)) + 1
    nufus, hucre, hucre_tam, hsum, yapili = 0.0, [], 0.0, 0.0, 0.0
    for r in range(max(r0, 0), min(r1 + 1, P.shape[0])):
        for c in range(max(c0, 0), min(c1 + 1, P.shape[1])):
            hb = box(trP.c + c * trP.a, trP.f + (r + 1) * trP.e, trP.c + (c + 1) * trP.a, trP.f + r * trP.e)
            pay = hb.intersection(S54).area / hb.area
            if pay <= 0:
                continue
            nufus += P[r, c] * pay
            hucre_tam += pay
            if H[r, c] > 0:
                yapili += pay
                hsum += H[r, c] * pay
            hucre.append((r, c, pay))
    return dict(nufus=nufus, yapili_pay=yapili / hucre_tam if hucre_tam else np.nan,
                ghsl_h_ort=hsum / yapili if yapili else np.nan, hucreler=hucre)


# =============================================================================
# 5. Binalar
# =============================================================================
def ilce_ad(s):
    """'FATİH' -> 'Fatih' (Türkçe büyük-küçük harf)."""
    if not s:
        return ""
    k = s.replace("İ", "i").replace("I", "ı").lower()
    return ("İ" if k[0] == "i" else k[0].upper()) + k[1:]


def kat_ayikla(v):
    if v is None:
        return np.nan
    m = re.match(r"\s*(\d+(?:[.,]\d+)?)", str(v))
    if not m:
        return np.nan
    x = float(m.group(1).replace(",", "."))
    return x if 0 < x <= 80 else np.nan


def yukseklik_ayikla(v):
    if v is None:
        return np.nan
    m = re.match(r"\s*(\d+(?:[.,]\d+)?)\s*(m)?\s*$", str(v))
    if not m:
        return np.nan
    x = float(m.group(1).replace(",", "."))
    return x if 2 <= x <= 300 else np.nan


def binalari_kur(a, V, gh, ms):
    """OSM (+ gerekirse MS) binalarını UTM'de toplar; kat ve kaynak sütunlarını doldurur."""
    rows = []
    for b in V["bina"]:
        g = donustur(b["geometry"], a["ileri"]).buffer(0)
        if g.is_empty or g.area < 2:
            continue
        rows.append(dict(geometry=g, kaynak="OSM", building=b["building"], kat_etiket=kat_ayikla(b["levels"]),
                         yuk_etiket=yukseklik_ayikla(b["height"]), ad=b["name"], osm_id=b["osm_id"],
                         zaman=b["zaman"]))
    if a.get("yikilan_dahil"):
        # deprem öncesi dokuyu ölçmek için deprem sonrası "yıkıldı" etiketlenen binalar da alınır
        for d in V["dongu"]:
            if any(k.split(":")[0] in ("destroyed", "demolished", "razed") for k in d["anahtar"]):
                g = donustur(d["geometry"], a["ileri"]).buffer(0)
                if not g.is_empty and g.area >= 2:
                    rows.append(dict(geometry=g, kaynak="OSM (deprem sonrası yıkıldı)", building="yes",
                                     kat_etiket=np.nan, yuk_etiket=np.nan, ad=None, osm_id=None, zaman=d["zaman"]))
    B = gpd.GeoDataFrame(rows, geometry="geometry", crs=a["epsg"]) if rows else gpd.GeoDataFrame(
        columns=["geometry", "kaynak"], geometry="geometry", crs=a["epsg"])
    B = B[B.intersects(a["E"])].reset_index(drop=True)
    a["kapsama"] = {}
    if ms:
        M = gpd.GeoDataFrame(geometry=[g.buffer(0) for g in ms], crs=a["epsg"])
        M = M[M.intersects(a["E"]) & (M.area >= 4)].reset_index(drop=True)
        tree = STRtree(B.geometry.values) if len(B) else None
        ortusme = np.zeros(len(M))
        if tree is not None and len(M):
            pi, pj = tree.query(M.geometry.values, predicate="intersects")
            ints = shapely.area(shapely.intersection(M.geometry.values[pi], B.geometry.values[pj]))
            np.add.at(ortusme, pi, ints)
        pay = ortusme / M.area.values
        S = a["S"]
        Ms = M.geometry.intersection(S).area.values
        kap = float((np.minimum(ortusme, M.area.values) * (Ms / np.maximum(M.area.values, 1e-9))).sum() / max(Ms.sum(), 1e-9))
        # sayıca kapsama: karedeki MS izlerinden OSM'de bir binaya değenlerin payı (MS–OSM kayıklığına dayanıklı)
        icM = M.intersects(S).values
        degen = np.zeros(len(M), bool)
        if tree is not None and len(M):
            degen[np.unique(tree.query(M.geometry.values, predicate="dwithin", distance=1.0)[0])] = True
        kap_sayi = float(degen[icM].mean()) if icM.any() else np.nan
        # iki kaynağın karede ayrı ayrı yapı oturumu ve bina sayısı (MS doğrulaması)
        cM = M.geometry.representative_point()
        cB = B.geometry.representative_point() if len(B) else gpd.GeoSeries([], crs=a["epsg"])
        a["kapsama"].update(ms_iz_kare=int(icM.sum()), osm_ms_alan_kapsama=kap, osm_ms_sayi_kapsama=kap_sayi,
                            ms_n=int(shapely.contains_xy(S, cM.x.values, cM.y.values).sum()),
                            osm_n=int(shapely.contains_xy(S, cB.x.values, cB.y.values).sum()) if len(B) else 0,
                            ms_gsi=float(Ms.sum() / S.area),
                            osm_gsi=float(B.geometry.intersection(S).area.sum() / S.area) if len(B) else 0.0)
        if not (kap_sayi >= OSM_YETERLI):
            # yalnız OSM'de hiçbir binaya 1 m'den yakın olmayan MS izleri eklenir (kayık kopyaları önler)
            ek = M[(~degen) & (pay <= MS_ORTUSME)].copy()
            ek["kaynak"] = "MS"
            ek["building"] = "yes"
            for c in ("kat_etiket", "yuk_etiket"):
                ek[c] = np.nan
            B = pd.concat([B, ek], ignore_index=True)
            a["bina_kaynagi"] = "OSM + Microsoft"
        else:
            a["bina_kaynagi"] = "OSM"
        a["ms_birlesik"] = not (kap_sayi >= OSM_YETERLI)
    else:
        a["bina_kaynagi"] = "OSM"
        a["ms_birlesik"] = False
    B = gpd.GeoDataFrame(B, geometry="geometry", crs=a["epsg"])
    # --- kat ---
    c = B.geometry.representative_point()
    row, col = hucre_indeksi(gh, c.x.values, c.y.values, "trH")
    Hh = gh["H"]
    ok = (row >= 0) & (row < Hh.shape[0]) & (col >= 0) & (col < Hh.shape[1])
    hg = np.zeros(len(B))
    hg[ok] = Hh[row[ok], col[ok]]
    B["ghsl_h"] = hg
    kat = B["kat_etiket"].astype(float).values.copy()
    kaynak = np.where(np.isfinite(kat), "etiket", "")
    yk = B["yuk_etiket"].astype(float).values
    m = ~np.isfinite(kat) & np.isfinite(yk)
    kat[m] = np.maximum(1, np.round(yk[m] / KAT_YUK))
    kaynak[m] = "yükseklik"
    m = ~np.isfinite(kat) & (hg > 0)
    kat[m] = np.maximum(1, np.round(hg[m] / KAT_YUK))
    kaynak[m] = "GHSL"
    m = ~np.isfinite(kat)
    etik = kat[(kaynak == "etiket") | (kaynak == "yükseklik")]
    yedek = float(np.median(etik)) if len(etik) >= 5 else (float(np.median(kat[np.isfinite(kat)])) if np.isfinite(kat).any() else 1.0)
    kat[m] = yedek
    kaynak[m] = "medyan"
    B["kat"] = kat
    B["kat_kaynak"] = kaynak
    B["taban"] = B.area
    B["ic_halka"] = [sum(1 for r in getattr(g, "geoms", [g]) for i in r.interiors if Polygon(i).area >= 10) for g in B.geometry]
    B["kisi"] = 0.0
    return B


def nufus_dagit(B, gh):
    """GHS-POP hücre nüfusunu hücredeki binalara inşaat alanı oranında dağıtır."""
    c = B.geometry.representative_point()
    row, col = hucre_indeksi(gh, c.x.values, c.y.values, "trP")
    P = gh["P"]
    ok = (row >= 0) & (row < P.shape[0]) & (col >= 0) & (col < P.shape[1])
    gfa = (B["taban"] * B["kat"]).values
    anahtar = row * 100000 + col
    top = pd.Series(gfa[ok]).groupby(anahtar[ok]).sum()
    kisi = np.zeros(len(B))
    idx = np.where(ok)[0]
    kisi[idx] = P[row[idx], col[idx]] * gfa[idx] / top.reindex(anahtar[idx]).values
    B["kisi"] = kisi
    return B


def kat_kalibrasyonu(tum):
    """Etiketli binalarda OSM katı ile GHSL/3 karşılaştırması, GHSL yükseklik sınıfına göre (yalnız tanı amaçlı)."""
    sinif = [(0.1, 7), (7, 10), (10, 15), (15, 20), (20, 300)]
    out = []
    for lo, hi in sinif:
        m = (tum["kat_kaynak"] == "etiket") & (tum["ghsl_h"] >= lo) & (tum["ghsl_h"] < hi)
        if m.sum() >= 15:
            osm = tum.loc[m, "kat"].median()
            gh = np.maximum(1, np.round(tum.loc[m, "ghsl_h"] / KAT_YUK)).median()
            out.append((lo, hi, int(m.sum()), osm, gh, max(1.0, osm / gh)))
        else:
            out.append((lo, hi, int(m.sum()), np.nan, np.nan, 1.0))
    return out


# =============================================================================
# 6. Sokaklar
# =============================================================================
def yollari_kur(a, V):
    Y = []
    for y in V["yol"]:
        hw = y["hw"]
        if hw in DISLA:
            continue
        x, yy = a["ileri"].transform(y["lon"], y["lat"])
        xy = np.column_stack([x, yy])
        kaldirim = (y["footway"] in KALDIRIM) or (hw == "path" and y["footway"] in KALDIRIM)
        servis_sokak = hw == "service" and (y["service"] in (None, "alley"))
        ozel = y["access"] in ("private", "no") and y["foot"] not in ("yes", "designated", "permissive")
        arac = (hw in ARAC or servis_sokak) and not ozel
        sokak = (arac or (hw in YAYA and not kaldirim)) and not ozel
        yuru = (hw not in YURUNMEZ or y["foot"] in ("yes", "designated")) and not (y["access"] in ("private", "no") and y["foot"] not in ("yes", "designated", "permissive"))
        Y.append(dict(ids=y["ids"], xy=xy, hw=hw, arac=arac, sokak=sokak, yuru=yuru,
                      yarim=YARIM_GEN.get(hw.replace("_link", ""), 2.0), ad=y["name"], osm_id=y["osm_id"]))
    return Y


def graf(Y, anahtar):
    G = nx.Graph()
    P = {}
    for y in Y:
        if not y[anahtar]:
            continue
        ids, xy = y["ids"], y["xy"]
        for i in range(len(ids) - 1):
            u, v = ids[i], ids[i + 1]
            if u == v:
                continue
            L = float(np.hypot(*(xy[i + 1] - xy[i])))
            if L <= 0.01:
                continue
            P[u] = xy[i]
            P[v] = xy[i + 1]
            if not G.has_edge(u, v):
                G.add_edge(u, v, uz=L, hw=y["hw"], yarim=y["yarim"])
    return G, P


def zincirler(G):
    uc = {n for n, d in G.degree() if d != 2}
    gor = set()
    out = []
    for u in uc:
        for v in G.neighbors(u):
            if (u, v) in gor:
                continue
            yol = [u, v]
            gor.add((u, v))
            gor.add((v, u))
            while yol[-1] not in uc:
                son, onc = yol[-1], yol[-2]
                ad = [w for w in G.neighbors(son) if w != onc]
                if not ad or (son, ad[0]) in gor:
                    break
                gor.add((son, ad[0]))
                gor.add((ad[0], son))
                yol.append(ad[0])
            out.append(yol)
    return out


def ag_olc(G, P, S, arazi_km2):
    """Kavşak, çıkmaz, uzunluk, segment ve yönelim ölçütleri (karenin içi)."""
    r = {}
    if G.number_of_edges() == 0:
        return dict(kavsak=0, cikmaz=0, uzunluk_m=0.0, seg=[], entropi=np.nan, duzen=np.nan, kavsak_dugum=[])
    kv = [n for n, d in G.degree() if d >= 3]
    ck = [n for n, d in G.degree() if d == 1]
    if kv:
        U = shapely.union_all(shapely.buffer(shapely.points([P[n] for n in kv]), KAVSAK_TOL))
        parcalar = list(getattr(U, "geoms", [U]))
        r["kavsak"] = sum(1 for p in parcalar if S.contains(p.centroid))
    else:
        r["kavsak"] = 0
    r["cikmaz"] = sum(1 for n in ck if S.contains(Point(P[n])))
    r["kavsak_dugum"] = [P[n] for n in kv]
    ed = list(G.edges(data=True))
    lines = shapely.linestrings([[P[u], P[v]] for u, v, _ in ed])
    ic = shapely.intersection(lines, S)
    Lic = shapely.length(ic)
    r["uzunluk_m"] = float(Lic.sum())
    # yönelim: Boeing (2019), 36 kutu, iki yön, uzunluk ağırlıklı
    dx = np.array([P[v][0] - P[u][0] for u, v, _ in ed])
    dy = np.array([P[v][1] - P[u][1] for u, v, _ in ed])
    yon = np.degrees(np.arctan2(dx, dy)) % 360
    w = Lic
    yonler = np.concatenate([yon, (yon + 180) % 360])
    ww = np.concatenate([w, w])
    kutu = np.floor(((yonler + 5) % 360) / 10).astype(int)
    h = np.bincount(kutu, weights=ww, minlength=36)
    if h.sum() > 0:
        p = h[h > 0] / h.sum()
        H = float(-(p * np.log(p)).sum())
        Hmax, Hg = np.log(36), np.log(4)
        r["entropi"] = H
        r["duzen"] = 1 - ((H - Hg) / (Hmax - Hg)) ** 2
        r["yon_hist"] = h / h.sum()
    else:
        r["entropi"] = r["duzen"] = np.nan
        r["yon_hist"] = np.zeros(36)
    # segmentler
    seg = []
    for z in zincirler(G):
        ln = LineString([P[n] for n in z])
        if S.contains(ln.interpolate(0.5, normalized=True)):
            seg.append(ln.length)
    r["seg"] = seg
    return r


def adalar_kur(G, P, S, B):
    lines = shapely.linestrings([[P[u], P[v]] for u, v in G.edges()])
    if len(lines) == 0:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry")
    U = shapely.union_all(lines)
    polys = list(shapely.get_parts(shapely.polygonize(list(shapely.get_parts(U)))))
    out = []
    for p in polys:
        if p.area < 50 or p.area > ADA_UST:
            continue
        if not S.contains(p.representative_point()):
            continue
        out.append(p)
    return gpd.GeoDataFrame(geometry=out)


def net_adalar(A, G, P):
    """Net ada: sokak eksenlerinin sınıf yarım genişliği kadar tamponu düşülür (varsayım)."""
    if len(A) == 0:
        return A
    bx = box(*A.total_bounds).buffer(30)
    ls, ws = [], []
    for u, v, d in G.edges(data=True):
        ln = LineString([P[u], P[v]])
        if ln.intersects(bx):
            ls.append(ln)
            ws.append(d.get("yarim", 2.0))
    T = shapely.union_all(shapely.buffer(np.array(ls, dtype=object), np.array(ws), cap_style="round")) if ls else Polygon()
    A["net"] = [g.difference(T) for g in A.geometry]
    return A


# =============================================================================
# 7. Cephe ışınları: sokak genişliği, H/W, cephe sürekliliği, bina cephesi
# =============================================================================
def isin_olc(G, P, S, B):
    if G.number_of_edges() == 0 or len(B) == 0:
        return {}
    kv = np.array([P[n] for n, d in G.degree() if d >= 3]) if any(d >= 3 for _, d in G.degree()) else np.zeros((0, 2))
    kd = cKDTree(kv) if len(kv) else None
    parcalar, sahip = [], []
    for i, g in enumerate(B.geometry.values):
        for p in getattr(g, "geoms", [g]):
            parcalar.append(Polygon(p.exterior))
            sahip.append(i)
    parcalar = np.array(parcalar, dtype=object)
    sahip = np.array(sahip)
    agac = STRtree(parcalar)
    yuk = (B["kat"].values * KAT_YUK)
    ornek = []   # (zincir, sıra, x, y, nx, ny)
    for zi, z in enumerate(zincirler(G)):
        ln = LineString([P[n] for n in z])
        if not ln.intersects(S) or ln.length < ISIN_ADIM:
            continue
        ss = np.arange(ISIN_ADIM / 2, ln.length, ISIN_ADIM)
        pts = shapely.line_interpolate_point(ln, ss)
        p1 = shapely.line_interpolate_point(ln, np.maximum(ss - 1, 0))
        p2 = shapely.line_interpolate_point(ln, np.minimum(ss + 1, ln.length))
        X, Yc = shapely.get_x(pts), shapely.get_y(pts)
        tx = shapely.get_x(p2) - shapely.get_x(p1)
        ty = shapely.get_y(p2) - shapely.get_y(p1)
        nrm = np.hypot(tx, ty)
        nrm[nrm == 0] = 1
        for k in range(len(ss)):
            ornek.append((zi, k, X[k], Yc[k], -ty[k] / nrm[k], tx[k] / nrm[k]))
    if not ornek:
        return {}
    O = np.array(ornek)
    icS = shapely.contains_xy(S, O[:, 2], O[:, 3])
    if kd is not None:
        d_kv, _ = kd.query(O[:, 2:4])
        icS &= d_kv > KAVSAK_TAMPON
    O = O[icS]
    n = len(O)
    if n == 0:
        return {}
    ori = shapely.points(O[:, 2:4])
    sonuc = {}
    for taraf, isaret in (("sol", 1), ("sag", -1)):
        uc = O[:, 2:4] + isaret * ISIN * O[:, 4:6]
        rays = shapely.linestrings(np.stack([O[:, 2:4], uc], axis=1))
        ri, pj = agac.query(rays, predicate="intersects")
        d = np.full(n, np.inf)
        bid = np.full(n, -1)
        if len(ri):
            kes = shapely.intersection(rays[ri], parcalar[pj])
            dd = shapely.distance(ori[ri], kes)
            sira = np.lexsort((dd, ri))
            ri_s, dd_s, pj_s = ri[sira], dd[sira], pj[sira]
            ilk = np.unique(ri_s, return_index=True)[1]
            d[ri_s[ilk]] = dd_s[ilk]
            bid[ri_s[ilk]] = sahip[pj_s[ilk]]
        sonuc[taraf] = (d, bid)
    dL, bL = sonuc["sol"]
    dR, bR = sonuc["sag"]
    gecerli = (dL > 0.3) & (dR > 0.3)          # eksen bir binanın içinden geçmiyor
    iki = gecerli & np.isfinite(dL) & np.isfinite(dR)
    W = dL[iki] + dR[iki]
    Hm = (yuk[bL[iki]] + yuk[bR[iki]]) / 2
    yan_d = np.concatenate([dL[gecerli], dR[gecerli]])
    # bina cephe koşuları
    kosu, yan_uzunluk, kosu_say = [], 0.0, 0
    Og = O[gecerli]
    for taraf_d, taraf_b in ((dL[gecerli], bL[gecerli]), (dR[gecerli], bR[gecerli])):
        cid = np.where(taraf_d <= CEPHE_ESIK, taraf_b, -1)
        z = Og[:, 0].astype(int)
        sira = Og[:, 1].astype(int)
        for zi in np.unique(z):
            m = z == zi
            seq = cid[m][np.argsort(sira[m])]
            yan_uzunluk += len(seq) * ISIN_ADIM
            onceki, say = None, 0
            for v in list(seq) + [None]:
                if v == onceki and v is not None:
                    say += 1
                    continue
                if onceki is not None and onceki >= 0:
                    kosu.append(say * ISIN_ADIM)
                    kosu_say += 1
                onceki, say = v, 1
    return dict(
        ornek=int(gecerli.sum()),
        W=W, HW=Hm / W if len(W) else np.array([]),
        iki_yan_pay=float(iki.sum() / max(gecerli.sum(), 1)),
        cephe_surekliligi=float((yan_d <= CEPHE_ESIK).mean()) if len(yan_d) else np.nan,
        bina_cephe=np.array(kosu),
        cephe_adimi=yan_uzunluk / kosu_say if kosu_say else np.nan,
    )


# =============================================================================
# 8. Yakınlık (400 m yürüme ağı)
# =============================================================================
def yakinlik_olc(Gy, Py, B, S, tohum=7):
    if Gy.number_of_edges() == 0 or len(B) == 0:
        return {}
    dugum = list(Gy.nodes())
    ix = {d: i for i, d in enumerate(dugum)}
    ed = list(Gy.edges(data="uz"))
    u = np.array([ix[a] for a, b, w in ed])
    v = np.array([ix[b] for a, b, w in ed])
    w = np.array([w for a, b, w in ed])
    N = len(dugum)
    M = coo_matrix((np.concatenate([w, w]), (np.concatenate([u, v]), np.concatenate([v, u]))), shape=(N, N)).tocsr()
    lines = shapely.linestrings([[Py[a], Py[b]] for a, b, _ in ed])
    agac = STRtree(lines)
    c = B.geometry.representative_point().values
    qi, qj = agac.query_nearest(c, return_distance=False, all_matches=False)
    kenar = np.full(len(B), -1)
    kenar[qi] = qj
    t = shapely.line_locate_point(lines[kenar], c)
    snap = shapely.distance(c, shapely.line_interpolate_point(lines[kenar], t))
    Lk = w[kenar]
    bu, bv = u[kenar], v[kenar]
    gfa = (B["taban"] * B["kat"]).values
    kisi = B["kisi"].values
    cx, cy = shapely.get_x(c), shapely.get_y(c)
    ic = np.where(shapely.contains_xy(S, cx, cy))[0]
    rng = np.random.default_rng(tohum)
    if len(ic) > YAKINLIK_ORNEK:
        ic = np.sort(rng.choice(ic, YAKINLIK_ORNEK, replace=False))
    kd = cKDTree(np.column_stack([cx, cy]))
    sonuc_b, sonuc_g, sonuc_k, sonuc_e = [], [], [], []
    for parca in np.array_split(ic, max(1, len(ic) // 40)):
        if len(parca) == 0:
            continue
        kaynak = np.concatenate([bu[parca], bv[parca]])
        D = dijkstra(M, directed=False, indices=kaynak, limit=YAKINLIK)
        k = len(parca)
        for j, o in enumerate(parca):
            Du = D[j] + t[o] + snap[o]
            Dv = D[k + j] + (Lk[o] - t[o]) + snap[o]
            Do = np.minimum(Du, Dv)
            db = np.minimum(Do[bu] + t, Do[bv] + (Lk - t)) + snap
            if kenar[o] >= 0:                      # aynı kenar üzerindeki binalar: doğrudan mesafe
                ayni = kenar == kenar[o]
                db[ayni] = np.minimum(db[ayni], np.abs(t[ayni] - t[o]) + snap[ayni] + snap[o])
            m = db <= YAKINLIK
            m[o] = False
            sonuc_b.append(m.sum())
            sonuc_g.append(gfa[m].sum())
            sonuc_k.append(kisi[m].sum())
            sonuc_e.append(kd.query_ball_point([cx[o], cy[o]], YAKINLIK, return_length=True) - 1)
    b, e = np.array(sonuc_b), np.array(sonuc_e)
    return dict(bina=np.median(b), gfa=np.median(sonuc_g), kisi=np.median(sonuc_k), kus=np.median(e),
                verim=float(np.median(b / np.maximum(e, 1))), n=len(b))


# =============================================================================
# 9. Ölçüm (OSM alanı ve model için ortak)
# =============================================================================
def avlu_olc(B, S):
    """Kapalı avlu: bina birleşiminin iç boşlukları (10–5.000 m²); OSM iç halkaları dahil."""
    if len(B) == 0:
        return dict(kapali_avlu=0, kapali_avlu_alan=0.0, kapali_avlu_medyan=np.nan)
    U = shapely.union_all(shapely.buffer(B.geometry.values, 0.25, join_style="mitre")).buffer(-0.25, join_style="mitre")
    delikler = []
    for p in getattr(U, "geoms", [U]):
        if p.geom_type != "Polygon":
            continue
        for i in p.interiors:
            h = Polygon(i)
            if 10 <= h.area <= 5000 and S.contains(h.representative_point()):
                delikler.append(h.area)
    return dict(kapali_avlu=len(delikler), kapali_avlu_alan=float(sum(delikler)),
                kapali_avlu_medyan=float(np.median(delikler)) if delikler else np.nan)


def min_dikdortgen(g):
    r = g.minimum_rotated_rectangle
    if r.geom_type != "Polygon":
        return np.nan, np.nan
    c = np.array(r.exterior.coords)
    k = np.hypot(*(c[1] - c[0]).T), np.hypot(*(c[2] - c[1]).T)
    return min(k), max(k)


def olc(a, B, Y, su, yesil, mezar, nufus_kare, hane):
    S = a["S"]
    arazi = S.difference(su) if su is not None and not su.is_empty else S
    A_ha = arazi.area / 1e4
    A_km2 = arazi.area / 1e6
    r = {}
    r["arazi_ha"] = A_ha
    r["su_ha"] = (S.area - arazi.area) / 1e4
    # --- binalar ---
    c = B.geometry.representative_point()
    icS = shapely.contains_xy(S, c.x.values, c.y.values)
    Bi = B[icS]
    kir = B.geometry.intersection(arazi)
    taban_k = kir.area.values
    gfa_k = taban_k * B["kat"].values
    r["bina_sayisi"] = int(icS.sum())
    r["bina_ha"] = icS.sum() / A_ha
    r["yapi_oturumu"] = taban_k.sum() / arazi.area
    r["taban_ort_m2"] = Bi["taban"].mean()
    r["taban_medyan_m2"] = Bi["taban"].median()
    ed = np.array([min_dikdortgen(g) for g in Bi.geometry.values]) if len(Bi) else np.zeros((0, 2))
    r["bina_en_medyan_m"] = float(np.nanmedian(ed[:, 0])) if len(ed) else np.nan
    r["bina_boy_medyan_m"] = float(np.nanmedian(ed[:, 1])) if len(ed) else np.nan
    kat = B["kat"].values
    w = taban_k
    r["kat_ort"] = float((kat * w).sum() / w.sum()) if w.sum() else np.nan
    r["kat_medyan"] = float(np.median(Bi["kat"])) if len(Bi) else np.nan
    kk = Bi["kat_kaynak"].value_counts(normalize=True) if "kat_kaynak" in Bi else pd.Series(dtype=float)
    r["kat_etiket_pay"] = float(kk.get("etiket", 0) + kk.get("yükseklik", 0))
    r["kat_ghsl_pay"] = float(kk.get("GHSL", 0))
    r["kat_medyan_yedek_pay"] = float(kk.get("medyan", 0))
    for ad, lo, hi in (("le2", 0, 2.5), ("3_4", 2.5, 4.5), ("5_7", 4.5, 7.5), ("8p", 7.5, 999)):
        m = (kat > lo) & (kat <= hi)
        r[f"insaat_pay_kat_{ad}"] = gfa_k[m].sum() / gfa_k.sum() if gfa_k.sum() else np.nan
    r["bina_pay_kat_le3"] = float((Bi["kat"] <= 3).mean()) if len(Bi) else np.nan
    r["bina_pay_kat_le4"] = float((Bi["kat"] <= 4).mean()) if len(Bi) else np.nan
    r["insaat_alani_m2"] = gfa_k.sum()
    r["emsal"] = gfa_k.sum() / arazi.area
    # duyarlılık: her bina en az 2 kat (GHSL'nin küçük kasabalarda katı düşük tahmin etmesine karşı)
    r["emsal_en_az_2_kat"] = (taban_k * np.maximum(kat, 2)).sum() / arazi.area
    r["katman_L"] = r["emsal"] / r["yapi_oturumu"] if r["yapi_oturumu"] else np.nan
    r["acik_alan_orani_OSR"] = (1 - r["yapi_oturumu"]) / r["emsal"] if r["emsal"] else np.nan
    # --- nüfus ---
    r["nufus"] = nufus_kare
    r["kisi_ha"] = nufus_kare / A_ha
    r["hane_buyuklugu"] = hane
    r["konut_ha"] = nufus_kare / hane / A_ha if hane else np.nan
    r["insaat_m2_kisi"] = gfa_k.sum() / nufus_kare if nufus_kare > 0 else np.nan
    # --- açık alan ---
    r["acik_alan_pay"] = 1 - r["yapi_oturumu"]
    r["acik_alan_m2_kisi"] = arazi.area * (1 - r["yapi_oturumu"]) / nufus_kare if nufus_kare > 0 else np.nan
    yes = yesil.intersection(arazi).area if yesil is not None and not yesil.is_empty else 0.0
    r["kamusal_yesil_pay"] = yes / arazi.area
    r["kamusal_yesil_m2_kisi"] = yes / nufus_kare if nufus_kare > 0 else np.nan
    r["mezarlik_pay"] = (mezar.intersection(arazi).area / arazi.area) if mezar is not None and not mezar.is_empty else 0.0
    # --- avlu ---
    av = avlu_olc(B, S)
    r["ic_halkali_bina_pay"] = float((Bi["ic_halka"] > 0).mean()) if len(Bi) else np.nan
    r["kapali_avlu_sayisi"] = av["kapali_avlu"]
    r["kapali_avlu_ha"] = av["kapali_avlu"] / A_ha
    r["kapali_avlu_alan_pay"] = av["kapali_avlu_alan"] / arazi.area
    r["kapali_avlu_medyan_m2"] = av["kapali_avlu_medyan"]
    # --- ağlar ---
    katman = {}
    for ag in ("arac", "sokak"):
        G, P = graf(Y, ag)
        m = ag_olc(G, P, S, A_km2)
        r[f"kavsak_km2_{ag}"] = m["kavsak"] / A_km2
        r[f"sokak_km_km2_{ag}"] = m["uzunluk_m"] / 1000 / A_km2
        r[f"cikmaz_pay_{ag}"] = m["cikmaz"] / (m["cikmaz"] + m["kavsak"]) if (m["cikmaz"] + m["kavsak"]) else np.nan
        r[f"segment_ort_m_{ag}"] = float(np.mean(m["seg"])) if m["seg"] else np.nan
        r[f"segment_medyan_m_{ag}"] = float(np.median(m["seg"])) if m["seg"] else np.nan
        r[f"yonelim_entropi_{ag}"] = m["entropi"]
        r[f"yonelim_duzen_{ag}"] = m["duzen"]
        katman[ag] = (G, P, m)
    G, P, _ = katman["sokak"]
    r["yon_hist"] = katman["sokak"][2].get("yon_hist")
    # sokak ağı uzunluğunda yaya yolu ve merdiven payı (erişilebilirlik göstergesi)
    uz = defaultdict(float)
    for u, v, d in G.edges(data=True):
        uz[d["hw"]] += float(shapely.length(shapely.intersection(LineString([P[u], P[v]]), S)))
    top = sum(uz.values())
    r["merdiven_pay"] = uz.get("steps", 0.0) / top if top else np.nan
    r["yaya_yolu_pay"] = sum(v for k, v in uz.items() if k in YAYA | {"s3", "diyagonal", "park_yolu"}) / top if top else np.nan
    # --- adalar ---
    A = adalar_kur(G, P, S, B)
    A = net_adalar(A, G, P)
    katman["adalar"] = A
    if len(A):
        alan = A.area.values
        r["ada_sayisi"] = len(A)
        r["ada_km2"] = len(A) / A_km2
        r["ada_alan_ort_m2"] = alan.mean()
        r["ada_alan_medyan_m2"] = float(np.median(alan))
        r["ada_cevre_medyan_m"] = float(np.median(A.length.values))
        ed = np.array([min_dikdortgen(g) for g in A.geometry.values])
        r["ada_kisa_medyan_m"] = float(np.nanmedian(ed[:, 0]))
        r["ada_uzun_medyan_m"] = float(np.nanmedian(ed[:, 1]))
        # alan ağırlıklı ada boyu (kişinin içinde yaşadığı adanın tipik büyüklüğü)
        r["ada_alan_agirlikli_m2"] = float((alan ** 2).sum() / alan.sum())
        Ut = shapely.union_all(B.geometry.values) if len(B) else Polygon()
        net = A["net"].values
        net_alan = shapely.area(net)
        bina_net = shapely.area(shapely.intersection(net, Ut))
        bina_brut = shapely.area(shapely.intersection(A.geometry.values, Ut))
        r["ada_ici_bos_pay_brut"] = 1 - bina_brut.sum() / alan.sum()
        r["ada_ici_bos_pay_net"] = 1 - bina_net.sum() / net_alan.sum() if net_alan.sum() else np.nan
        r["net_yapi_oturumu"] = bina_net.sum() / net_alan.sum() if net_alan.sum() else np.nan
        r["sokak_alan_pay_tahmini"] = 1 - net_alan.sum() / alan.sum()
        A["bina_pay_net"] = np.where(net_alan > 0, bina_net / np.maximum(net_alan, 1e-9), np.nan)
    Ga, Pa, _ = katman["arac"]
    Aa = adalar_kur(Ga, Pa, S, B)
    if len(Aa):
        r["ada_arac_alan_medyan_m2"] = float(np.median(Aa.area.values))
        r["ada_arac_cevre_medyan_m"] = float(np.median(Aa.length.values))
    # --- ışınlar ---
    iz = isin_olc(G, P, S, B)
    if iz:
        W = iz["W"]
        r["cephe_arasi_medyan_m"] = float(np.median(W)) if len(W) else np.nan
        r["cephe_arasi_p25_m"] = float(np.percentile(W, 25)) if len(W) else np.nan
        r["cephe_arasi_p75_m"] = float(np.percentile(W, 75)) if len(W) else np.nan
        r["hw_medyan"] = float(np.median(iz["HW"])) if len(W) else np.nan
        r["hw_p25"] = float(np.percentile(iz["HW"], 25)) if len(W) else np.nan
        r["hw_p75"] = float(np.percentile(iz["HW"], 75)) if len(W) else np.nan
        r["cephe_arasi_alt6_pay"] = float((W < 6).mean()) if len(W) else np.nan
        r["cephe_arasi_alt8_pay"] = float((W < 8).mean()) if len(W) else np.nan
        r["hw_ust1_pay"] = float((iz["HW"] > 1).mean()) if len(W) else np.nan
        r["iki_yani_cevrili_pay"] = iz["iki_yan_pay"]
        r["cephe_surekliligi"] = iz["cephe_surekliligi"]
        r["bina_cephe_medyan_m"] = float(np.median(iz["bina_cephe"])) if len(iz["bina_cephe"]) else np.nan
        r["cephe_adimi_m"] = iz["cephe_adimi"]
        r["isin_ornek"] = iz["ornek"]
        katman["W"] = W
    # --- yakınlık ---
    Gy, Py = graf(Y, "yuru")
    yk = yakinlik_olc(Gy, Py, B, S)
    if yk:
        r["yakinlik_bina_400"] = yk["bina"]
        r["yakinlik_insaat_400_m2"] = yk["gfa"]
        r["yakinlik_nufus_400"] = yk["kisi"]
        r["yakinlik_kus_bina_400"] = yk["kus"]
        r["ag_verimi_400"] = yk["verim"]
    return r, katman


# =============================================================================
# 10. Model mahalle v1
# =============================================================================
def model_veri():
    sys.path.insert(0, str(MODEL_KOD))
    import plan_modeli as pm  # noqa
    A = pm.ag_kur()
    Pm = pm.plan_kur()
    rows = []
    for p in Pm["parseller"]:
        katlar = p.get("bina_katlari") or [p["kat"]] * len(p["binalar"])
        parcalar = [(b, k) for b, k in zip(p["binalar"], katlar)]
        if p.get("genisleme") is not None:
            parcalar.append((p["genisleme"], 1))
        gfa = sum(b.area * k for b, k in parcalar)
        for b, k in parcalar:
            rows.append(dict(geometry=b, kat=float(k), kisi=p["konut"] * MODEL_HANE * b.area * k / gfa if gfa else 0.0,
                             tip=p["tip"], kaynak="model"))
    for d in Pm["donatilar"]:
        for b in d["binalar"]:
            rows.append(dict(geometry=b, kat=float(d["kat"]), kisi=0.0, tip=d["tur"], kaynak="model"))
    B = gpd.GeoDataFrame(rows, geometry="geometry")
    B["geometry"] = B.geometry.buffer(0)
    B = B[B.area > 1].reset_index(drop=True)
    B["taban"] = B.area
    B["kat_kaynak"] = "model"
    B["ic_halka"] = [len(g.interiors) if g.geom_type == "Polygon" else 0 for g in B.geometry]
    # yollar: sınıflar
    halka = A["sokak_cizgi"][0]
    s1 = A["sokak_cizgi"][1:3]
    s2 = [ln for k, (_, ln) in pm.BAGLANTI.items() if k not in pm.KAPALI]
    gecit = [ge for _, ge in Pm["gecitler"]]
    diyag = list(pm.DIYAG_EKSEN)
    park_ici = [pm.BAGLANTI[k][1] for k in pm.PARK_ICI_KAPALI]
    sinif = [("toplayici", [halka], dict(arac=True, sokak=True, yuru=True, yarim=12.0)),
             ("s1", s1, dict(arac=True, sokak=True, yuru=True, yarim=9.0)),
             ("s2", s2, dict(arac=True, sokak=True, yuru=True, yarim=5.0)),
             ("s3", gecit, dict(arac=False, sokak=True, yuru=True, yarim=3.0)),
             ("diyagonal", diyag, dict(arac=False, sokak=True, yuru=True, yarim=4.0)),
             ("park_yolu", park_ici, dict(arac=False, sokak=False, yuru=True, yarim=2.0)),
             ("baglanti", [ln for ln in A["yaya_cizgi"] if ln not in diyag and ln not in park_ici],
              dict(arac=False, sokak=False, yuru=True, yarim=1.0))]
    tum = shapely.union_all([ln for _, ls, _ in sinif for ln in ls])
    Y = []
    kaynaklar = [(ln, ad, oz) for ad, ls, oz in sinif for ln in ls]
    agac = STRtree([k[0] for k in kaynaklar])
    for ln in shapely.get_parts(tum):
        c = np.array(ln.coords)
        for i in range(len(c) - 1):
            seg = LineString(c[i:i + 2])
            orta = seg.interpolate(0.5, normalized=True)
            idx = agac.query(orta.buffer(0.05), predicate="intersects")
            if len(idx) == 0:
                continue
            oz = dict(arac=False, sokak=False, yuru=False, yarim=1.0)
            hw = None
            for j in idx:
                ad, o = kaynaklar[j][1], kaynaklar[j][2]
                for kk in ("arac", "sokak", "yuru"):
                    oz[kk] = oz[kk] or o[kk]
                if o["yarim"] > oz["yarim"] or hw is None:
                    oz["yarim"] = max(oz["yarim"], o["yarim"])
                    hw = ad
            ids = [(round(c[i][0], 2), round(c[i][1], 2)), (round(c[i + 1][0], 2), round(c[i + 1][1], 2))]
            Y.append(dict(ids=ids, xy=c[i:i + 2], hw=hw, **oz))
    yesil = shapely.union_all([d["poly"] for d in Pm["donatilar"] if d["tur"] in ("park", "cep", "bostan")] + list(Pm["cep"]))
    return B, Y, yesil


# =============================================================================
# 11. Ana akış
# =============================================================================
def hane_buyuklugu():
    d = pd.read_csv(PANEL, usecols=["ilce_ad_tuik", "il", "nufus_2025", "hane_toplam"])
    d["oh"] = d.nufus_2025 / d.hane_toplam
    return d


def birlesik(gs):
    gs = [g for g in gs if g is not None and not g.is_empty]
    return shapely.union_all(gs) if gs else Polygon()


def olcum():
    t0 = time.time()
    secim = os.environ.get("MORFOLOJI_ALANLAR")          # deneme için alan alt kümesi: "G4,C2"
    alanlar = [alan_hazirla(dict(a)) for a in ALANLAR if not secim or a["kod"] in secim.split(",")]
    kesit = Path(os.environ["MORFOLOJI_KESIT"]) if "MORFOLOJI_KESIT" in os.environ else kesit_yolu(
        [alan_hazirla(dict(a)) for a in ALANLAR])
    if not kesit.exists():
        kesit_olustur([alan_hazirla(dict(a)) for a in ALANLAR], kesit)
    log("OSM kesiti okunuyor:", kesit)
    V = osm_oku(kesit, alanlar)
    hb = hane_buyuklugu()
    satirlar, gpkg_alan, gpkg_bina, gpkg_yol, gpkg_ada, cizim = [], [], [], [], [], {}
    hazir = []
    for a in alanlar:
        log(a["kod"], a["ad"])
        gh = ghsl_oku(a)
        ms = ms_oku(a) if a.get("ms") else []
        B = binalari_kur(a, V[a["kod"]], gh, ms)
        B = nufus_dagit(B, gh)
        hazir.append((a, B, gh))
    # kat kalibrasyonu (tüm alanların genişletilmiş kutularındaki etiketli binalar)
    tum = pd.concat([B[["kat", "kat_kaynak", "ghsl_h"]] for _, B, _ in hazir], ignore_index=True)
    kalib = kat_kalibrasyonu(tum)
    log("kat doğrulama (etiketli binalar):", [(lo, hi, n, o, g) for lo, hi, n, o, g, k in kalib])
    kat_dog = []
    for a, B, gh in hazir:
        Vk = V[a["kod"]]
        su = birlesik([donustur(g, a["ileri"]).buffer(0) for g in Vk["su"]]).intersection(a["E"])
        yesil = birlesik([donustur(g, a["ileri"]).buffer(0) for g in Vk["yesil"] + Vk["meydan"]])
        mezar = birlesik([donustur(g, a["ileri"]).buffer(0) for g in Vk["mezar"]])
        Y = yollari_kur(a, Vk)
        gk = ghsl_kare(gh, a["S"])
        oh = hb[(hb.ilce_ad_tuik == a["ilce"]) & (hb.il == a["il"])]["oh"]
        hane = float(oh.iloc[0]) if len(oh) else np.nan
        r, katman = olc(a, B, Y, su, yesil, mezar, gk["nufus"], hane)
        # kapsama: GHSL yapılı hücrelerin (kesişim payıyla) OSM/MS bina izi değen payı
        S = a["S"]
        Bs = B[B.intersects(S)]
        tree = STRtree(Bs.geometry.values) if len(Bs) else None
        tr_ = gh["trH"]
        yap, deg = 0.0, 0.0
        for rr, cc, pay in gk["hucreler"]:
            if gh["H"][rr, cc] <= 0:
                continue
            hb54 = box(tr_.c + cc * tr_.a, tr_.f + (rr + 1) * tr_.e, tr_.c + (cc + 1) * tr_.a, tr_.f + rr * tr_.e)
            hu = donustur(hb54.segmentize(25), Transformer.from_crs("ESRI:54009", a["epsg"], always_xy=True)).intersection(S)
            yap += pay
            if tree is not None and len(tree.query(hu, predicate="intersects")):
                deg += pay
        icS = shapely.contains_xy(S, *np.array([g.coords[0] for g in B.geometry.representative_point()]).T)
        Bi = B[icS]
        zaman = Bi.loc[Bi.kaynak == "OSM", "zaman"] if "zaman" in Bi else pd.Series(dtype=str)
        dongu = [d for d in V[a["kod"]]["dongu"] if S.intersects(donustur(d["geometry"], a["ileri"]))]
        bdis = V[a["kod"]]["bina_disi"]
        kiyi = any(S.intersects(donustur(k, a["ileri"])) for k in V[a["kod"]]["kiyi"])
        mah = sorted({n for g, n, lv in V[a["kod"]]["sinir"] if g.contains(Point(a["lon"], a["lat"])) and lv in ("8", "10")})
        kap = dict(
            ghsl_yapili_hucre_pay=gk["yapili_pay"], ghsl_h_ort_m=gk["ghsl_h_ort"],
            hucre_kapsama=deg / yap if yap else np.nan,
            ms_iz_kare=a["kapsama"].get("ms_iz_kare", np.nan),
            osm_ms_alan_kapsama=a["kapsama"].get("osm_ms_alan_kapsama", np.nan),
            osm_ms_sayi_kapsama=a["kapsama"].get("osm_ms_sayi_kapsama", np.nan),
            dogrulama_osm_n=a["kapsama"].get("osm_n", np.nan), dogrulama_ms_n=a["kapsama"].get("ms_n", np.nan),
            dogrulama_osm_gsi=a["kapsama"].get("osm_gsi", np.nan), dogrulama_ms_gsi=a["kapsama"].get("ms_gsi", np.nan),
            ms_bina_pay=float((Bi.kaynak == "MS").mean()) if len(Bi) else 0.0,
            osm_son_duzenleme_medyan=str(zaman.sort_values().iloc[len(zaman) // 2]) if len(zaman) else "",
            osm_deprem_sonrasi_duzenlenen_pay=float((zaman >= DEPREM).mean()) if len(zaman) else np.nan,
            yasam_dongusu_etiketli=len(dongu),
            yikik_vb_etiketli=int(sum(v for k, v in bdis.items() if k in ("ruins", "collapsed", "destroyed", "demolished", "damaged"))),
            kiyi_kesiyor=kiyi,
        )
        durum = "iyi" if (kap["hucre_kapsama"] >= 0.9) else ("orta" if kap["hucre_kapsama"] >= 0.75 else "eksik")
        if a["kod"] == "G7":
            durum = "deprem öncesi durum"
        # kat şüphesi: kat çoğunlukla GHSL'den geliyor ve GHSL ortalaması < 5 m (tek katın altında kalan
        # küçük kasaba binaları) ya da inşaat alanı kişi başına < 25 m² (yüksek bloklarda düşük tahmin)
        kat_suphe = bool(r["kat_ghsl_pay"] > 0.5 and (kap["ghsl_h_ort_m"] < 5 or r["insaat_m2_kisi"] < 25))
        uyari = [a["uyari"]] if a.get("uyari") else []
        if kat_suphe:
            uyari.append("kat GHSL/3'ten ve muhtemelen düşük tahmin: emsal ve H/W alt sınır")
        meta = dict(kod=a["kod"], ad=a["ad"], kisa=a["kisa"], grup=a["grup"], il=a["il"], ilce=ilce_ad(a["ilce"]),
                    mahalle=", ".join(mah), lat=a["lat"], lon=a["lon"], epsg=a["epsg"], bina_kaynagi=a["bina_kaynagi"],
                    kapsama_durumu=durum, sokak_guvensiz="sokak" in (a.get("uyari") or ""), kat_suphe=kat_suphe,
                    uyari=" | ".join(uyari), dayanak=a["dayanak"])
        yh = r.pop("yon_hist", None)
        satirlar.append({**meta, **{k: v for k, v in kap.items()}, **r})
        log(f"  bina {r['bina_sayisi']}, GSI {r['yapi_oturumu']:.2f}, FSI {r['emsal']:.2f}, "
            f"kişi/ha {r['kisi_ha']:.0f}, kavşak {r['kavsak_km2_sokak']:.0f}, W {r.get('cephe_arasi_medyan_m', np.nan):.1f}, "
            f"kapsama {kap['hucre_kapsama']:.2f}, kaynak {a['bina_kaynagi']}")
        # kat doğrulama
        et = Bi[(Bi.kat_kaynak == "etiket") & (Bi.ghsl_h > 0)]
        kat_dog.append(dict(kod=a["kod"], kisa=a["kisa"], etiketli_bina=len(et),
                            osm_kat_medyan=et.kat.median() if len(et) else np.nan,
                            ghsl_kat_medyan=np.maximum(1, np.round(et.ghsl_h / KAT_YUK)).median() if len(et) else np.nan))
        # GPKG katmanları
        geri = a["geri"]
        gpkg_alan.append(dict(geometry=donustur(S.segmentize(50), geri), **meta,
                              **{k: r.get(k) for k in ("bina_ha", "yapi_oturumu", "emsal", "kisi_ha", "kavsak_km2_sokak",
                                                      "ada_alan_medyan_m2", "cephe_arasi_medyan_m", "hw_medyan")}))
        Bs = B[B.intersects(S)].copy()
        for _, b in Bs.iterrows():
            gpkg_bina.append(dict(geometry=donustur(b.geometry, geri), alan_kod=a["kod"], kaynak=b.kaynak,
                                  building=b.get("building"), kat=b.kat, kat_kaynak=b.kat_kaynak, taban_m2=round(b.taban, 1),
                                  ghsl_h=b.ghsl_h, kisi=round(b.kisi, 2), osm_id=b.get("osm_id")))
        for y in Y:
            ln = LineString(y["xy"])
            if ln.intersects(S):
                gpkg_yol.append(dict(geometry=donustur(ln, geri), alan_kod=a["kod"], highway=y["hw"], arac=y["arac"],
                                     sokak=y["sokak"], yuru=y["yuru"], ad=y["ad"], osm_id=y["osm_id"]))
        A = katman.get("adalar")
        if A is not None and len(A):
            for g, bp in zip(A.geometry.values, A.get("bina_pay_net", pd.Series([np.nan] * len(A))).values):
                gpkg_ada.append(dict(geometry=donustur(g, geri), alan_kod=a["kod"], alan_m2=round(g.area, 1),
                                     cevre_m=round(g.length, 1), net_bina_pay=bp))
        cizim[a["kod"]] = dict(B=B[B.intersects(S)].geometry.intersection(S).values, su=su.intersection(S), S=S, yon=yh,
                               W=katman.get("W"))
    # --- model ---
    log("Model mahalle v1")
    Bm, Ym, yesil_m = model_veri()
    for ma in MODEL_ALANLAR:
        a = dict(ma)
        a["S"] = box(*ma["pencere"])
        c = Bm.geometry.representative_point()
        icS = shapely.contains_xy(a["S"], c.x.values, c.y.values)
        nufus = float(Bm.loc[icS, "kisi"].sum())
        r, katman = olc(a, Bm, Ym, None, yesil_m, None, nufus, MODEL_HANE)
        yh = r.pop("yon_hist", None)
        meta = dict(kod=a["kod"], ad=a["ad"], kisa=a["kisa"], grup="model", il="—", ilce="—", mahalle="", lat=np.nan,
                    lon=np.nan, epsg="", bina_kaynagi="model_mahalle/kod/plan_modeli.py", kapsama_durumu="model",
                    sokak_guvensiz=False, kat_suphe=False,
                    uyari="kenar etkisi: plan dışında bina ve yol yok (yakınlık kenarda düşük)" if a["kod"] == "M1" else "",
                    dayanak=a["dayanak"])
        satirlar.append({**meta, **r})
        log(f"  {a['kod']}: bina {r['bina_sayisi']}, GSI {r['yapi_oturumu']:.2f}, FSI {r['emsal']:.2f}, kişi/ha {r['kisi_ha']:.0f}, "
            f"kavşak {r['kavsak_km2_sokak']:.0f}, W {r.get('cephe_arasi_medyan_m', np.nan):.1f}")
        if a["kod"] == "M1":
            cizim["M1"] = dict(B=Bm[Bm.intersects(a["S"])].geometry.intersection(a["S"]).values, su=Polygon(), S=a["S"], yon=yh,
                               W=katman.get("W"))
    df = pd.DataFrame(satirlar)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV, index=False, encoding="utf-8", float_format="%.4f")
    pd.DataFrame(kat_dog).to_csv(CSV_KAT, index=False, encoding="utf-8", float_format="%.2f")
    with open(CSV_KAT, "a", encoding="utf-8") as f:
        f.write("\n# havuz (tüm genişletilmiş kutulardaki etiketli binalar): ghsl_alt_m,ghsl_ust_m,n_etiketli,osm_kat_medyan,ghsl_kat_medyan,oran\n")
        for lo, hi, n_, o_, g_, k_ in kalib:
            f.write(f"# {lo},{hi},{n_},{o_},{g_},{k_:.2f}\n")
    if GPKG.exists():
        GPKG.unlink()
    gpd.GeoDataFrame(gpkg_alan, geometry="geometry", crs=4326).to_file(GPKG, layer="alanlar", driver="GPKG")
    gpd.GeoDataFrame(gpkg_bina, geometry="geometry", crs=4326).to_file(GPKG, layer="binalar", driver="GPKG")
    gpd.GeoDataFrame(gpkg_yol, geometry="geometry", crs=4326).to_file(GPKG, layer="sokaklar", driver="GPKG")
    gpd.GeoDataFrame(gpkg_ada, geometry="geometry", crs=4326).to_file(GPKG, layer="adalar", driver="GPKG")
    log("yazıldı:", CSV, GPKG, f"({time.time() - t0:.0f} s)")
    pd.to_pickle(cizim, ONBELLEK / "cizim.pkl")
    return df, cizim


# =============================================================================
# 12. Çizim
# =============================================================================
def poligon_ciz(ax, geoms, fc, zorder=2):
    verts, codes = [], []
    for g in geoms:
        for p in shapely.get_parts(g):
            if p.geom_type != "Polygon" or p.is_empty:
                continue
            for halka in [p.exterior] + list(p.interiors):
                xy = np.asarray(halka.coords)
                verts.append(xy)
                codes.append(np.r_[MPath.MOVETO, np.full(len(xy) - 2, MPath.LINETO), MPath.CLOSEPOLY])
    if verts:
        ax.add_patch(PathPatch(MPath(np.vstack(verts), np.concatenate(codes)), fc=fc, ec="none", lw=0, zorder=zorder))


def olcek(ax, x, y, h=5, yazi=7):
    for i, (a0, a1) in enumerate(((0, 50), (50, 100), (100, 200))):
        ax.add_patch(Rectangle((x + a0, y), a1 - a0, h, fc=R_BINA if i % 2 == 0 else "white", ec=R_BINA, lw=0.5, zorder=20))
    for v in (0, 100, 200):
        ax.text(x + v, y + h + 3, f"{v}" + (" m" if v == 200 else ""), ha="center", va="bottom", fontsize=yazi, color=R_METIN, zorder=20)


def figur_zemin_tekil(kod, satir, cz):
    S = cz["S"]
    x0, y0, x1, y1 = S.bounds
    W_, H_ = 6.4, 8.0
    fig = plt.figure(figsize=(W_, H_), dpi=200)
    fig.patch.set_facecolor("white")
    mw = 0.88
    mh = mw * W_ / H_
    ax = fig.add_axes([0.06, 0.205, mw, mh])
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=R_ZEMIN, ec="none", zorder=0))
    poligon_ciz(ax, [cz["su"]], R_SU, 1)
    poligon_ciz(ax, cz["B"], R_BINA, 2)
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec="#8a877f", lw=0.6, zorder=5))
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.axis("off")
    renk = GRUP_RENK[satir["grup"]]
    fig.add_artist(Rectangle((0.06, 0.944), 0.008, 0.036, transform=fig.transFigure, fc=renk, ec="none"))
    fig.text(0.078, 0.98, satir["ad"], fontsize=12.5, fontweight="bold", color=R_METIN, va="top")
    alt = f"{GRUP_AD[satir['grup']]}"
    if satir["grup"] != "model":
        alt += f" · {satir['il']} / {satir['ilce']} · merkez {tr(f'{satir.lat:.4f}')}, {tr(f'{satir.lon:.4f}')}"
    fig.text(0.078, 0.955, alt, fontsize=7.5, color=R_METIN2, va="top")
    # ölçek ve kuzey: haritanın altında, harita ile aynı ölçekte
    sx = fig.add_axes([0.06, 0.17, mw, 0.025])
    sx.set_xlim(0, x1 - x0)
    sx.set_ylim(0, 10)
    sx.axis("off")
    for k, (a0, a1) in enumerate(((0, 50), (50, 100), (100, 200))):
        sx.add_patch(Rectangle((a0, 1), a1 - a0, 3, fc=R_BINA if k % 2 == 0 else "white", ec=R_BINA, lw=0.5))
    for v in (0, 100, 200):
        sx.text(v, 5, f"{v}" + (" m" if v == 200 else ""), ha="center", va="bottom", fontsize=7, color=R_METIN)
    sx.annotate("", xy=(x1 - x0 - 10, 9.5), xytext=(x1 - x0 - 10, 1),
                arrowprops=dict(arrowstyle="-|>", color=R_BINA, lw=1.0, mutation_scale=9))
    sx.text(x1 - x0 - 22, 4, "K", ha="right", va="center", fontsize=8, fontweight="bold", color=R_METIN)
    yd = " *" if satir.get("sokak_guvensiz") in (True, "True") else ""
    kd = " ‡" if satir.get("kat_suphe") in (True, "True") else ""
    olc_ = [("Bina", f"{sayi(satir.bina_ha, 1)} /ha"), ("Yapı oturumu", yuzde(satir.yapi_oturumu)),
            ("Emsal", f"{sayi(satir.emsal, 2)}{kd}"), ("Ortalama kat", f"{sayi(satir.kat_ort, 1)}{kd}"),
            ("Nüfus (GHS-POP)", f"{sayi(satir.kisi_ha)} kişi/ha"), ("Kavşak (yaya dahil)", f"{sayi(satir.kavsak_km2_sokak)} /km²{yd}"),
            ("Ada alanı (medyan)", f"{sayi(satir.ada_alan_medyan_m2 / 1e4, 2)} ha{yd}"),
            ("Cephe arası (medyan)", f"{sayi(satir.cephe_arasi_medyan_m, 1)} m{yd}")]
    for k, (ad, v) in enumerate(olc_):
        xx = 0.06 + (k % 4) * 0.225
        yy = 0.135 - (k // 4) * 0.052
        fig.text(xx, yy, ad, fontsize=6.8, color=R_METIN2)
        fig.text(xx, yy - 0.022, v, fontsize=9.5, color=R_METIN, fontweight="bold")
    kay = ("Model mahalle v1 çizimi (plan_modeli.py)" if satir["grup"] == "model" else
           f"Bina: {satir['bina_kaynagi']} · nüfus: GHS-POP 2020 · kat: OSM etiketi, yoksa GHSL/3")
    notlar = [f"600 × 600 m · {kay}"]
    if yd:
        notlar.append("* OSM'de iç sokakların çoğu yok; sokak ölçütleri güvenilmez.")
    if kd:
        notlar.append("‡ Kat GHSL/3'ten; muhtemelen düşük tahmin (emsal alt sınır).")
    if isinstance(satir.get("uyari"), str) and "Şubat 2023" in satir.get("uyari"):
        notlar.append("† OSM binaları Şubat 2023 durumunda (deprem öncesi doku); yıkılan binalar dahil.")
    fig.text(0.06, 0.012, "\n".join(notlar), fontsize=6.2, color=R_METIN2, va="bottom", linespacing=1.4)
    for uz in ("png", "svg"):
        fig.savefig(HARITA / f"figur_zemin_{kod}.{uz}", facecolor="white")
    plt.close(fig)


def levha(df, cizim):
    sira = [k for k in [a["kod"] for a in ALANLAR] + ["M1"] if k in cizim]
    ust = [k for k in sira if k.startswith("G")]
    alt_ = [k for k in sira if not k.startswith("G")]
    ncol = max(len(ust), len(alt_))
    pw = 2.55
    fig = plt.figure(figsize=(ncol * pw + 0.6, 2 * (pw + 1.05) + 1.25), dpi=200)
    fig.patch.set_facecolor("white")
    W_, H_ = fig.get_size_inches()
    fig.text(0.3 / W_, 1 - 0.28 / H_, "Figür–zemin: geleneksel ve çağdaş dokular, model mahalle v1",
             fontsize=15, fontweight="bold", color=R_METIN, va="top")
    fig.text(0.3 / W_, 1 - 0.58 / H_, "Her pafta 600 × 600 m (36 ha), aynı ölçek ve yön (kuzey yukarı). Siyah: bina taban izi. "
             "Alt yazı: bina/ha · yapı oturumu (GSI) · emsal (FSI) · ortalama kat · kişi/ha (GHS-POP 2020) · medyan ada alanı.",
             fontsize=8.5, color=R_METIN2, va="top")
    for satir_i, kodlar in enumerate((ust, alt_)):
        for j, kod in enumerate(kodlar):
            s = df.set_index("kod").loc[kod]
            cz = cizim[kod]
            left = (0.3 + j * pw) / W_
            bottom = 1 - (0.95 + satir_i * (pw + 1.05) + pw) / H_
            ax = fig.add_axes([left, bottom, (pw - 0.12) / W_, (pw - 0.12) / H_])
            x0, y0, x1, y1 = cz["S"].bounds
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=R_ZEMIN, ec="none", zorder=0))
            poligon_ciz(ax, [cz["su"]], R_SU, 1)
            poligon_ciz(ax, cz["B"], R_BINA, 2)
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec="#8a877f", lw=0.5, zorder=5))
            ax.set_xlim(x0, x1)
            ax.set_ylim(y0, y1)
            ax.set_aspect("equal")
            ax.axis("off")
            renk = GRUP_RENK[s["grup"]]
            ty = bottom - 0.05 / H_
            fig.add_artist(Rectangle((left, ty - 0.005 / H_), 0.22 / W_, 0.05 / H_, transform=fig.transFigure, fc=renk, ec="none"))
            ad = (s["kisa"] + (" °" if s.get("bina_kaynagi", "") == "OSM + Microsoft" else "") + (" †" if kod == "G7" else "")
                  + (" *" if s.get("sokak_guvensiz") in (True, "True") else "")
                  + (" ‡" if s.get("kat_suphe") in (True, "True") else ""))
            fig.text(left, ty - 0.1 / H_, ad, fontsize=8.6, fontweight="bold", color=R_METIN, va="top")
            fig.text(left, ty - 0.32 / H_,
                     f"{sayi(s.bina_ha, 0)} bina/ha · GSI {sayi(s.yapi_oturumu, 2)} · FSI {sayi(s.emsal, 2)}",
                     fontsize=6.6, color=R_METIN2, va="top")
            fig.text(left, ty - 0.5 / H_,
                     f"{sayi(s.kat_ort, 1)} kat · {sayi(s.kisi_ha, 0)} kişi/ha · ada {sayi(s.ada_alan_medyan_m2 / 1e4, 2)} ha",
                     fontsize=6.6, color=R_METIN2, va="top")
    # ortak ölçek ve açıklama
    ax = fig.add_axes([0.3 / W_, 0.12 / H_, (pw - 0.12) / W_, 0.3 / H_])
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 30)
    ax.axis("off")
    for i, (a0, a1) in enumerate(((0, 100), (100, 200), (200, 400))):
        ax.add_patch(Rectangle((a0, 4), a1 - a0, 7, fc=R_BINA if i % 2 == 0 else "white", ec=R_BINA, lw=0.5))
    for v in (0, 100, 200, 400):
        ax.text(v, 13, f"{v}" + (" m" if v == 400 else ""), ha="center", va="bottom", fontsize=7)
    lej = [Patch(fc=GRUP_RENK[g], label=GRUP_AD[g]) for g in ("geleneksel", "çağdaş", "model")]
    fig.legend(handles=lej, loc="lower left", bbox_to_anchor=((0.3 + pw + 0.2) / W_, 0.1 / H_), ncol=3, frameon=False, fontsize=8,
               handlelength=1.2, handleheight=0.5)
    fig.text(1 - 0.3 / W_, 0.16 / H_,
             "° Bina izleri OSM + Microsoft Global ML Building Footprints (OSM eksik). † Antakya: OSM binaları Şubat 2023 durumunda (deprem öncesi doku). "
             "* OSM'de iç sokaklar eksik. ‡ Kat GHSL/3'ten, muhtemelen düşük (emsal alt sınır).\n"
             "GSI: yapı oturumu · FSI: emsal (kat OSM etiketinden, yoksa GHSL/3) · ada: sokak eksenleriyle çevrili ada alanının medyanı. "
             "Kaynak: OSM 25.10.2026, GHSL R2023A, 03_VERI/kod/morfoloji_olcum.py",
             fontsize=6.6, color=R_METIN2, ha="right", va="bottom")
    for uz in ("png", "svg"):
        fig.savefig(HARITA / f"figur_zemin_levha.{uz}", facecolor="white")
    plt.close(fig)


OLCUT_GRAFIK = [
    # (sütun, başlık, çarpan, biçim, hedef bandı (alt, üst) ya da None, hedef etiketi)
    ("bina_ha", "Bina sayısı (/ha)", 1, 0, None, ""),
    ("yapi_oturumu", "Yapı oturumu (%)", 100, 0, None, ""),
    ("emsal", "Emsal (brüt FSI)", 1, 2, None, ""),
    ("kat_ort", "Ortalama kat (taban ağırlıklı)", 1, 1, (2, 4), "§3: 2–4 kat"),
    ("kisi_ha", "Nüfus yoğunluğu (kişi/ha)", 1, 0, (100, 150), "§2: 100–150"),
    ("kavsak_km2_sokak", "Kavşak yoğunluğu (/km², yaya dahil)", 1, 0, (80, 120), "§4: ≥ 80–120"),
    ("sokak_km_km2_sokak", "Sokak uzunluğu (km/km²)", 1, 0, (18, 25), "§4: ≥ 18"),
    ("ada_alan_medyan_m2", "Ada alanı, medyan (ha)", 1e-4, 2, (0.70, 1.40), "§4: 60–90 × 90–130 m (eksenden ≈ 0,7–1,4)"),
    ("cephe_arasi_medyan_m", "Cephe arası mesafe, medyan (m)", 1, 1, None, ""),
    ("hw_medyan", "Yükseklik / genişlik (H/W), medyan", 1, 2, (0.7, 1.0), "§9.6: S2 0,7–1,0"),
    ("ada_ici_bos_pay_net", "Ada içi yapısız alan (net, %)", 100, 0, None, ""),
    ("yakinlik_bina_400", "400 m yürüyüşte ulaşılan bina", 1, 0, None, ""),
]


SOKAK_OLCUT = {"kavsak_km2_sokak", "sokak_km_km2_sokak", "ada_alan_medyan_m2", "cephe_arasi_medyan_m", "hw_medyan",
               "ada_ici_bos_pay_net", "yakinlik_bina_400"}
KAT_OLCUT = {"kat_ort", "emsal", "hw_medyan"}


def _bicim(x, p=None):
    return tr(f"{x:,.6g}")


def olcut_grafigi(df):
    d = df[df.kod != "M0"].copy()
    sira = [a["kod"] for a in ALANLAR if a["grup"] == "geleneksel"] + ["M1"] + [a["kod"] for a in ALANLAR if a["grup"] == "çağdaş"]
    d = d.set_index("kod").loc[[k for k in sira if k in set(d.kod)]]
    sg = d["sokak_guvensiz"].astype(str).eq("True").values
    ks = d["kat_suphe"].astype(str).eq("True").values
    gruplar = d["grup"].values
    yy, kay, onceki = [], 0.0, None
    for g in gruplar:
        if onceki is not None and g != onceki:
            kay += 0.8
        yy.append(kay)
        kay += 1
        onceki = g
    yy = -np.array(yy)
    ncol = 4
    fig = plt.figure(figsize=(17, 13.8), dpi=170)
    fig.patch.set_facecolor("white")
    fig.text(0.02, 0.985, "Aynı ölçütlerle: geleneksel dokular, çağdaş dokular ve model mahalle v1", fontsize=16,
             fontweight="bold", color=R_METIN, va="top")
    fig.text(0.02, 0.963, "600 × 600 m örneklem kareleri. Gri bant: tasarim_parametreleri.md hedefi (varsa). Boş işaret: güvenilmez değer "
             "(OSM sokak ağı eksik ya da kat GHSL'den düşük tahmin); grup medyanına katılmadı. Model: merkezli 600 m pencere.",
             fontsize=9.5, color=R_METIN2, va="top")
    for i, (col, bas, carp, ond, bant, betik) in enumerate(OLCUT_GRAFIK):
        ax = fig.add_axes([0.13 + (i % ncol) * 0.218, 0.70 - (i // ncol) * 0.305, 0.17, 0.225])
        v = d[col].astype(float).values * carp
        bos = (sg & (col in SOKAK_OLCUT)) | (ks & (col in KAT_OLCUT))
        ust = np.nanmax(v) * 1.15 if np.isfinite(v).any() else 1
        if bant:
            ust = max(ust, bant[1] * 1.1)
            ax.axvspan(bant[0], min(bant[1], ust), color=R_BANT, zorder=0, lw=0)
            ax.text(bant[0], yy.min() - 1.35, betik, fontsize=6.8, color=R_METIN2, va="center")
        for yv, vv, g, b in zip(yy, v, gruplar, bos):
            if not np.isfinite(vv):
                ax.text(0, yv, " —", fontsize=7, va="center", color=R_METIN2)
                continue
            ax.plot([0, vv], [yv, yv], color=R_IZGARA, lw=1.2, zorder=1, solid_capstyle="butt")
            ax.scatter([vv], [yv], s=36 if g != "model" else 44, marker=GRUP_IM[g],
                       color="white" if b else GRUP_RENK[g], edgecolor=GRUP_RENK[g] if b else "white",
                       linewidth=1.3 if b else 1.2, zorder=3)
            if g == "model":
                ax.text(vv + ust * 0.03, yv, sayi(vv, ond), fontsize=7.4, va="center", color=R_METIN, fontweight="bold")
        for g in ("geleneksel", "çağdaş"):
            m_ = (gruplar == g) & ~bos & np.isfinite(v)
            if not m_.any():
                continue
            md = np.median(v[m_])
            yg = yy[gruplar == g]
            ax.plot([md, md], [yg.min() - 0.4, yg.max() + 0.4], color=GRUP_RENK[g], lw=1, ls=(0, (2, 2)), zorder=2)
            ax.text(md, yg.max() + 0.55, f"medyan {sayi(md, ond)}", fontsize=6.6, color=R_METIN2, ha="center", va="bottom")
        ax.set_xlim(0, ust)
        ax.set_ylim(yy.min() - 1.8, 1.6)
        ax.set_title(bas, fontsize=9.5, loc="left", color=R_METIN, fontweight="bold", pad=4)
        ax.set_yticks(yy)
        ax.set_yticklabels(d["kisa"].values if i % ncol == 0 else [], fontsize=7.6, color=R_METIN)
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", labelsize=7, colors=R_METIN2, length=2)
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(5))
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(_bicim))
        ax.grid(axis="x", color=R_IZGARA, lw=0.6)
        ax.set_axisbelow(True)
        for s_ in ("top", "right", "left"):
            ax.spines[s_].set_visible(False)
        ax.spines["bottom"].set_color("#bdbab3")
    lej = [Line2D([], [], marker=GRUP_IM[g], color=GRUP_RENK[g], ls="", markersize=7, markeredgecolor="white", label=GRUP_AD[g])
           for g in ("geleneksel", "çağdaş", "model")]
    lej.append(Line2D([], [], marker="o", color="white", markeredgecolor=R_METIN2, ls="", markersize=7, label="güvenilmez değer"))
    lej.append(Line2D([], [], color=R_METIN2, ls=(0, (2, 2)), lw=1, label="grup medyanı"))
    lej.append(Patch(fc=R_BANT, label="tasarım hedefi"))
    fig.legend(handles=lej, loc="lower left", bbox_to_anchor=(0.13, 0.022), ncol=6, frameon=False, fontsize=9)
    fig.text(0.98, 0.006, "Kaynak: OSM 25.10.2026 (+ Microsoft ayak izleri), GHS-POP 2020, GHSL ANBH 2018; 03_VERI/kod/morfoloji_olcum.py",
             fontsize=7, color=R_METIN2, ha="right")
    for uz in ("png", "svg"):
        fig.savefig(HARITA / f"morfoloji_olcutler.{uz}", facecolor="white")
    plt.close(fig)


def cizimler(df, cizim):
    HARITA.mkdir(parents=True, exist_ok=True)
    dfi = df.set_index("kod")
    for kod, cz in cizim.items():
        figur_zemin_tekil(kod, dfi.loc[kod], cz)
    levha(df, cizim)
    olcut_grafigi(df)
    log("çizimler:", HARITA)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cizim", action="store_true", help="yalnız çizim (CSV ve önbellekteki çizim verisinden)")
    arg = ap.parse_args()
    ONBELLEK.mkdir(parents=True, exist_ok=True)
    if arg.cizim and (ONBELLEK / "cizim.pkl").exists():
        df = pd.read_csv(CSV)
        cizim = pd.read_pickle(ONBELLEK / "cizim.pkl")
    else:
        df, cizim = olcum()
    cizimler(df, cizim)
