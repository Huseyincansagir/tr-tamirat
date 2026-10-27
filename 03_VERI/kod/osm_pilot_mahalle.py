"""
OpenStreetMap'ten Faz 3 mahalle analizi için ham katmanlar (tek geçiş)
=====================================================================
Girdi : 03_VERI/ham/osm/turkey-latest.osm.pbf (Geofabrik, 25.10.2026)
Çıktı : 03_VERI/islenmis/pilot_osm/
  Türkiye geneli
    idari_sinirlar.gpkg      boundary=administrative, admin_level 7–10 (mahalle/köy/belde)
    yer_noktalari.parquet    place=neighbourhood|suburb|quarter|village|hamlet|town|city düğümleri
    donati_noktalari.parquet okul, anaokulu, cami, sağlık, eczane, market, pazar, dükkân, buluşma, oyun alanı,
                             durak, raylı istasyon (düğüm ya da çizginin köşe ortalaması)
    ana_yollar.parquet       motorway/trunk/primary (+link) çizgileri (WKB)
  Pilot ilçe kutuları (10 ilçe, 0,02° tampon)
    yaya_dugum.parquet, yaya_kenar.parquet  yürünebilir sokak ağı (motorway hariç)
    binalar.parquet          building=* kapalı çizgiler (WKB) + kat/yükseklik etiketleri
    konut_alanlari.parquet   landuse=residential alanları (ad, access, gated)
    kapilar.parquet          barrier=gate|lift_gate düğümleri
"""
import sys
import time
from array import array
from pathlib import Path

import geopandas as gpd
import numpy as np
import osmium
import pandas as pd
from osmium.filter import KeyFilter, TagFilter
from shapely import wkb
from shapely.geometry import LineString, Polygon

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
PBF = KOK / "03_VERI" / "ham" / "osm" / "turkey-latest.osm.pbf"
CIK = KOK / "03_VERI" / "islenmis" / "pilot_osm"
CIK.mkdir(parents=True, exist_ok=True)

# pilot ilçelerin sınır kutuları (geoBoundaries ADM2, WGS84) — 05_ANALIZ/sonuclar/pilot_secim_son.csv
KUTU = {
    "SAFRANBOLU": (32.591, 41.128, 32.981, 41.530), "ANTAKYA": (35.923, 36.111, 36.400, 36.424),
    "NİLÜFER": (28.637, 40.064, 29.010, 40.301), "SİLİVRİ": (27.971, 41.032, 28.395, 41.363),
    "BEYPAZARI": (31.658, 39.849, 32.199, 40.508), "KOCASİNAN": (34.960, 38.721, 35.748, 39.066),
    "ONİKİŞUBAT": (36.453, 37.345, 36.982, 38.010), "MERAM": (31.971, 37.456, 32.617, 37.950),
    "BAŞAKŞEHİR": (28.640, 41.058, 28.851, 41.149), "FATİH": (28.919, 40.988, 28.988, 41.041),
}
TAMPON, HUCRE = 0.02, 20  # 1/20° = 0,05° ızgarayla hızlı kutu sınaması
IZGARA = set()
for x0, y0, x1, y1 in KUTU.values():
    for i in range(int((x0 - TAMPON) * HUCRE), int((x1 + TAMPON) * HUCRE) + 1):
        for j in range(int((y0 - TAMPON) * HUCRE), int((y1 + TAMPON) * HUCRE) + 1):
            IZGARA.add((i, j))


def kutuda(lon, lat):
    return (int(lon * HUCRE), int(lat * HUCRE)) in IZGARA


ANA = {"motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link"}
YURUNMEZ = {"motorway", "motorway_link", "construction", "proposed", "raceway", "bus_guideway", "abandoned",
            "platform", "corridor", "elevator", "bridleway"}
MARKET = {"supermarket", "convenience", "greengrocer", "bakery", "butcher", "general", "grocery", "deli",
          "dairy", "pastry", "frozen_food", "farm"}
BULUSMA = {"cafe", "library", "community_centre", "arts_centre", "social_centre", "townhall", "fountain",
           "public_bookcase", "teahouse"}
SAGLIK = {"clinic", "hospital", "doctors"}


def donati_turu(t):
    """Bir nesnenin etiketlerinden donatı türlerini döndürür (bir nesne birden çok türe girebilir)."""
    tur = []
    am, sh, le = t.get("amenity"), t.get("shop"), t.get("leisure")
    if am == "school":
        tur.append("okul")
    elif am in ("kindergarten", "childcare"):
        tur.append("anaokulu")
    elif am == "place_of_worship":
        rel, ad = t.get("religion", ""), t.get("name", "").lower()
        if rel == "muslim" or "cami" in ad or "mescid" in ad:
            tur.append("cami")
    elif am in SAGLIK or t.get("healthcare") in ("clinic", "hospital", "doctor", "centre"):
        tur.append("saglik")
    elif am == "pharmacy":
        tur.append("eczane")
    elif am == "marketplace":
        tur += ["pazar", "bulusma"]
    elif am in BULUSMA:
        tur.append("bulusma")
    elif am == "bus_station":
        tur.append("durak")
    if sh:
        tur.append("dukkan")
        if sh in MARKET:
            tur.append("market")
    if le == "playground":
        tur.append("oyun")
    if t.get("highway") == "bus_stop" or t.get("public_transport") in ("platform", "stop_position"):
        if t.get("railway") in (None, "", "platform") or t.get("bus") == "yes":
            tur.append("durak")
    if t.get("railway") in ("station", "halt", "tram_stop", "subway_entrance") or t.get("station") == "subway":
        tur.append("rayli")
    if t.get("place") == "square":
        tur.append("bulusma")
    return tur


bas = time.time()
print("PBF:", PBF, round(PBF.stat().st_size / 1e6), "MB")
fp = (osmium.FileProcessor(str(PBF))
      .with_locations("flex_mem")
      .with_areas(TagFilter(("boundary", "administrative"), ("landuse", "residential")))
      .with_filter(KeyFilter("building", "highway", "amenity", "shop", "leisure", "landuse", "boundary",
                             "place", "public_transport", "railway", "healthcare", "barrier")))

donati, yer, sinir, anayol, bina, konut, kapi = [], [], [], [], [], [], []
k_way, k_hw, k_u, k_v = array("q"), [], array("q"), array("q")
dugum = {}
sayac = 0
for o in fp:
    sayac += 1
    if sayac % 5_000_000 == 0:
        print(f"  {sayac:,} nesne · {time.time() - bas:.0f} sn", flush=True)
    t = o.tags
    if o.is_node():
        lon, lat = o.location.lon, o.location.lat
        for tur in donati_turu(t):
            donati.append((lon, lat, tur, t.get("amenity") or t.get("shop") or t.get("leisure") or "",
                           t.get("name", ""), "n", o.id))
        pl = t.get("place")
        if pl in ("neighbourhood", "suburb", "quarter", "village", "hamlet", "town", "city"):
            yer.append((lon, lat, pl, t.get("name", ""), o.id))
        if t.get("barrier") in ("gate", "lift_gate") and kutuda(lon, lat):
            kapi.append((lon, lat, t.get("barrier"), t.get("access", ""), o.id))
    elif o.is_way():
        nd = o.nodes
        if len(nd) < 2 or not nd[0].location.valid():
            continue
        lon0, lat0 = nd[0].location.lon, nd[0].location.lat
        hw = t.get("highway")
        tur = donati_turu(t)
        if tur:
            xs = [n.location.lon for n in nd if n.location.valid()]
            ys = [n.location.lat for n in nd if n.location.valid()]
            for tr in tur:
                donati.append((sum(xs) / len(xs), sum(ys) / len(ys), tr,
                               t.get("amenity") or t.get("shop") or t.get("leisure") or "",
                               t.get("name", ""), "w", o.id))
        if hw in ANA:
            try:
                anayol.append((LineString([(n.lon, n.lat) for n in nd]).wkb, hw, o.id))
            except Exception:
                pass
        if not kutuda(lon0, lat0):
            continue
        if hw and hw not in YURUNMEZ and t.get("area") != "yes" and t.get("foot") != "no":
            refs = [n.ref for n in nd if n.location.valid()]
            for n in nd:
                if n.location.valid():
                    dugum[n.ref] = (n.location.lon, n.location.lat)
            for a, b in zip(refs[:-1], refs[1:]):
                k_way.append(o.id)
                k_hw.append(hw)
                k_u.append(a)
                k_v.append(b)
        if "building" in t and o.is_closed() and len(nd) >= 4:
            try:
                g = Polygon([(n.lon, n.lat) for n in nd])
                bina.append((g.wkb, t.get("building"), t.get("building:levels", ""), t.get("height", ""),
                             t.get("amenity", ""), t.get("name", ""), o.id))
            except Exception:
                pass
    elif o.is_area():
        if t.get("boundary") == "administrative" and t.get("admin_level") in ("7", "8", "9", "10"):
            try:
                g = wkb.loads(osmium.geom.WKBFactory().create_multipolygon(o), hex=True)
                sinir.append((g, t.get("admin_level"), t.get("name", ""), t.get("place", ""),
                              t.get("ref", ""), o.orig_id(), o.from_way()))
            except Exception:
                pass
        elif t.get("landuse") == "residential":
            try:
                g = wkb.loads(osmium.geom.WKBFactory().create_multipolygon(o), hex=True)
            except Exception:
                continue
            c = g.representative_point()
            if kutuda(c.x, c.y):
                konut.append((g.wkb, t.get("name", ""), t.get("access", ""), t.get("gated", ""),
                              t.get("barrier", ""), t.get("residential", ""), o.orig_id()))

print(f"Okuma bitti: {sayac:,} nesne, {time.time() - bas:.0f} sn")
print("donatı:", len(donati), "| yer:", len(yer), "| sınır:", len(sinir), "| ana yol:", len(anayol),
      "| bina:", len(bina), "| konut alanı:", len(konut), "| kapı:", len(kapi), "| yaya kenar:", len(k_u))

pd.DataFrame(donati, columns=["lon", "lat", "tur", "etiket", "ad", "nesne", "osm_id"]).to_parquet(
    CIK / "donati_noktalari.parquet")
pd.DataFrame(yer, columns=["lon", "lat", "place", "ad", "osm_id"]).to_parquet(CIK / "yer_noktalari.parquet")
gpd.GeoDataFrame(sinir, columns=["geometry", "admin_level", "ad", "place", "ref", "osm_id", "yoldan"],
                 crs=4326).to_file(CIK / "idari_sinirlar.gpkg", driver="GPKG")
pd.DataFrame(anayol, columns=["wkb", "highway", "osm_id"]).to_parquet(CIK / "ana_yollar.parquet")
pd.DataFrame(bina, columns=["wkb", "building", "levels", "height", "amenity", "ad", "osm_id"]).to_parquet(
    CIK / "binalar.parquet")
pd.DataFrame(konut, columns=["wkb", "ad", "access", "gated", "barrier", "residential", "osm_id"]).to_parquet(
    CIK / "konut_alanlari.parquet")
pd.DataFrame(kapi, columns=["lon", "lat", "barrier", "access", "osm_id"]).to_parquet(CIK / "kapilar.parquet")
pd.DataFrame({"way": np.frombuffer(k_way, dtype=np.int64), "highway": k_hw,
              "u": np.frombuffer(k_u, dtype=np.int64), "v": np.frombuffer(k_v, dtype=np.int64)}).to_parquet(
    CIK / "yaya_kenar.parquet")
d = pd.DataFrame.from_dict(dugum, orient="index", columns=["lon", "lat"])
d.index.name = "id"
d.reset_index().to_parquet(CIK / "yaya_dugum.parquet")
print(f"Tamam · {time.time() - bas:.0f} sn")
