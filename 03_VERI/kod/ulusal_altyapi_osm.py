"""
OpenStreetMap'ten Faz 4 ulusal mekânsal çerçeve katmanları (tek geçiş)
=====================================================================
Girdi : 03_VERI/ham/osm/turkey-latest.osm.pbf (Geofabrik çıkarımı)
Çıktı : 03_VERI/islenmis/ulusal_altyapi/  (her dosya < 50 MB; geometriler WGS84, ~10–20 m sadeleştirilmiş)
  yollar.gpkg          highway = motorway / trunk / primary (+ _link) ve bu sınıflarda inşaat hâlindekiler
  demiryollari.gpkg    railway = rail / narrow_gauge / construction / proposed (+ highspeed, usage, service, electrified)
  demiryolu_ag.parquet aynı çizgilerin tam çözünürlüklü kenarları (OSM düğüm kimlikleriyle; ağ analizi için)
  istasyonlar.gpkg     railway = station / halt (metro, tramvay, hafif raylı, füniküler hariç işaretli)
  havalimanlari.gpkg   aeroway = aerodrome (iata, icao, askerî işaret, alan)
  limanlar.gpkg        landuse = port, industrial = port, harbour = yes (alan) + harbour / seamark liman düğümleri
  iletim_hatlari.gpkg  power = line / cable, en yüksek gerilim ≥ 154 kV
  santraller.gpkg      power = plant (alan ya da düğüm) — kaynak, güç
  uretecler.gpkg       power = generator (düğüm ya da kapalı çizginin merkezi) — kaynak, güç
  sanayi_alanlari.gpkg landuse = industrial (alan) — ad, industrial etiketi, OSB işareti
  kiyi.gpkg            natural = coastline
  korunan_alanlar.gpkg boundary = protected_area, leisure = nature_reserve (alan)
  sulak_alanlar.gpkg   natural = wetland (alan)
Kalıp: 03_VERI/kod/osm_pilot_mahalle.py (FileProcessor + KeyFilter, alan kurma TagFilter ile)
Çalıştırma: PYTHONIOENCODING=utf-8 python 03_VERI/kod/ulusal_altyapi_osm.py   (≈ 10–20 dk, ≈ 6 GB bellek)
"""
import re
import sys
import time
from pathlib import Path

import geopandas as gpd
import osmium
import pandas as pd
from osmium.filter import KeyFilter, TagFilter
from shapely import wkb
from shapely.geometry import LineString, Point

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
PBF = KOK / "03_VERI" / "ham" / "osm" / "turkey-latest.osm.pbf"
CIK = KOK / "03_VERI" / "islenmis" / "ulusal_altyapi"
CIK.mkdir(parents=True, exist_ok=True)

YOL = {"motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link"}
RAY = {"rail", "narrow_gauge", "construction", "proposed"}
KENT_RAYLI = {"subway", "light_rail", "tram", "monorail", "funicular", "miniature"}
WKBF = osmium.geom.WKBFactory()


def gerilim(v):
    """'380000;154000' → 380000 (V). Okunamazsa 0."""
    s = [int(float(x)) for x in re.findall(r"\d+(?:\.\d+)?", v or "")]
    s = [x * 1000 if x < 1000 else x for x in s]  # '154' kV yazılmışsa
    return max(s) if s else 0


def cizgi(nd):
    xy = [(n.lon, n.lat) for n in nd if n.location.valid()]
    return LineString(xy) if len(xy) >= 2 else None


def merkez(nd):
    xs = [n.lon for n in nd if n.location.valid()]
    ys = [n.lat for n in nd if n.location.valid()]
    return (sum(xs) / len(xs), sum(ys) / len(ys)) if xs else (None, None)


def alan_geom(o):
    try:
        return wkb.loads(WKBF.create_multipolygon(o), hex=True)
    except Exception:
        return None


bas = time.time()
print("PBF:", PBF, round(PBF.stat().st_size / 1e6), "MB")
ALAN_FILTRE = TagFilter(("landuse", "industrial"), ("landuse", "port"), ("industrial", "port"), ("harbour", "yes"),
                        ("aeroway", "aerodrome"), ("power", "plant"), ("boundary", "protected_area"),
                        ("leisure", "nature_reserve"), ("natural", "wetland"))
fp = (osmium.FileProcessor(str(PBF))
      .with_locations("flex_mem")
      .with_areas(ALAN_FILTRE)
      .with_filter(KeyFilter("highway", "railway", "aeroway", "harbour", "landuse", "industrial", "power", "natural",
                             "boundary", "leisure", "seamark:type", "public_transport")))

yol, ray, ist, hav, lim, hat, sant, uret, san, kiyi, kor, sulak, ray_ag = ([] for _ in range(13))
sayac = 0
for o in fp:
    sayac += 1
    if sayac % 5_000_000 == 0:
        print(f"  {sayac:,} nesne · {time.time() - bas:.0f} sn", flush=True)
    t = o.tags
    if o.is_node():
        lon, lat = o.location.lon, o.location.lat
        rw = t.get("railway")
        if rw in ("station", "halt") or (t.get("public_transport") == "station" and t.get("train") == "yes"):
            ist.append((Point(lon, lat), rw or "station", t.get("station", ""), t.get("usage", ""), t.get("train", ""),
                        t.get("name", ""), t.get("operator", ""), t.get("disused", ""), "n", o.id))
        if t.get("aeroway") == "aerodrome":
            hav.append((Point(lon, lat), t.get("name", ""), t.get("iata", ""), t.get("icao", ""),
                        t.get("aerodrome:type", ""), t.get("aerodrome", ""), t.get("military", ""), 0.0, "n", o.id))
        if t.get("harbour") or t.get("seamark:type") in ("harbour", "port"):
            lim.append((Point(lon, lat), t.get("name", ""), "dugum", t.get("harbour", ""),
                        t.get("seamark:harbour:category", "") or t.get("harbour:category", ""), 0.0, "n", o.id))
        pw = t.get("power")
        if pw == "plant":
            sant.append((Point(lon, lat), t.get("name", ""), t.get("plant:source", ""), t.get("plant:method", ""),
                         t.get("plant:output:electricity", ""), t.get("operator", ""), 0.0, "n", o.id))
        elif pw == "generator":
            uret.append((lon, lat, t.get("generator:source", ""), t.get("generator:method", ""),
                         t.get("generator:output:electricity", ""), "n", o.id))
    elif o.is_way():
        nd = o.nodes
        if len(nd) < 2:
            continue
        hw, rw, pw = t.get("highway"), t.get("railway"), t.get("power")
        if hw in YOL or (hw == "construction" and t.get("construction") in YOL):
            g = cizgi(nd)
            if g is not None:
                yol.append((g, hw if hw != "construction" else "yapim_" + t.get("construction"), t.get("ref", ""),
                            t.get("name", ""), t.get("lanes", ""), t.get("maxspeed", ""), o.id))
        if rw in RAY:
            alt = t.get("construction", "") or t.get("construction:railway", "") or t.get("proposed", "")
            if rw in ("construction", "proposed") and alt and alt not in ("rail", "narrow_gauge", "yes"):
                pass  # metro, tramvay vb. inşaatlar
            else:
                g = cizgi(nd)
                gec = [n for n in nd if n.location.valid()]
                for a, b in zip(gec[:-1], gec[1:]):  # tam çözünürlüklü topoloji (ortak düğüm kimlikleriyle)
                    ray_ag.append((o.id, a.ref, b.ref, a.lon, a.lat, b.lon, b.lat))
                if g is not None:
                    ray.append((g, rw, t.get("usage", ""), t.get("service", ""), t.get("highspeed", ""),
                                t.get("electrified", ""), t.get("maxspeed", ""), t.get("gauge", ""),
                                t.get("passenger", "") or t.get("railway:traffic_mode", ""), t.get("name", ""), o.id))
        if rw in ("station", "halt"):
            x, y = merkez(nd)
            if x is not None:
                ist.append((Point(x, y), rw, t.get("station", ""), t.get("usage", ""), t.get("train", ""),
                            t.get("name", ""), t.get("operator", ""), t.get("disused", ""), "w", o.id))
        if pw in ("line", "cable"):
            v = gerilim(t.get("voltage"))
            if v >= 154000:
                g = cizgi(nd)
                if g is not None:
                    hat.append((g, pw, v, t.get("voltage", ""), t.get("circuits", ""), t.get("name", ""),
                                t.get("operator", ""), o.id))
        elif pw == "generator":
            x, y = merkez(nd)
            if x is not None:
                uret.append((x, y, t.get("generator:source", ""), t.get("generator:method", ""),
                             t.get("generator:output:electricity", ""), "w", o.id))
        if t.get("natural") == "coastline":
            g = cizgi(nd)
            if g is not None:
                kiyi.append((g, o.id))
    elif o.is_area():
        lu, ind = t.get("landuse"), t.get("industrial")
        kim = (o.orig_id(), "w" if o.from_way() else "r")
        if t.get("aeroway") == "aerodrome":
            g = alan_geom(o)
            if g is not None:
                c = g.representative_point()
                hav.append((c, t.get("name", ""), t.get("iata", ""), t.get("icao", ""), t.get("aerodrome:type", ""),
                            t.get("aerodrome", ""), t.get("military", ""), g.area, kim[1], kim[0]))
        if lu == "port" or ind == "port" or t.get("harbour") == "yes":
            g = alan_geom(o)
            if g is not None:
                lim.append((g, t.get("name", ""), "port" if (lu == "port" or ind == "port") else "harbour",
                            t.get("harbour", ""), t.get("seamark:harbour:category", "") or t.get("harbour:category", ""),
                            g.area, kim[1], kim[0]))
        if t.get("power") == "plant":
            g = alan_geom(o)
            if g is not None:
                sant.append((g.representative_point(), t.get("name", ""), t.get("plant:source", ""),
                             t.get("plant:method", ""), t.get("plant:output:electricity", ""), t.get("operator", ""),
                             g.area, kim[1], kim[0]))
        if lu == "industrial":
            g = alan_geom(o)
            if g is not None:
                san.append((g, t.get("name", ""), ind or "", t.get("operator", ""), kim[1], kim[0]))
        if t.get("boundary") == "protected_area" or t.get("leisure") == "nature_reserve":
            g = alan_geom(o)
            if g is not None:
                kor.append((g, t.get("name", ""), t.get("protect_class", ""), t.get("protection_title", ""),
                            t.get("leisure", ""), kim[1], kim[0]))
        if t.get("natural") == "wetland":
            g = alan_geom(o)
            if g is not None:
                sulak.append((g, t.get("wetland", ""), t.get("name", ""), kim[1], kim[0]))

print(f"Okuma bitti: {sayac:,} nesne, {time.time() - bas:.0f} sn")
print("yol", len(yol), "| ray", len(ray), "| istasyon", len(ist), "| havalimanı", len(hav), "| liman", len(lim),
      "| hat", len(hat), "| santral", len(sant), "| üreteç", len(uret), "| sanayi", len(san), "| kıyı", len(kiyi),
      "| korunan", len(kor), "| sulak", len(sulak))


def yaz(satirlar, kolonlar, ad, tolerans=None):
    if not satirlar:
        print("  boş:", ad)
        return
    g = gpd.GeoDataFrame(satirlar, columns=kolonlar, geometry="geometry", crs=4326)
    if tolerans:
        g["geometry"] = g.geometry.simplify(tolerans, preserve_topology=True)
    for k in g.columns:
        if g[k].dtype == object and k != "geometry":
            g[k] = g[k].astype(str)
    yol_ = CIK / ad
    if yol_.exists():
        yol_.unlink()
    g.to_file(yol_, driver="GPKG", engine="pyogrio")
    print(f"  {ad}: {len(g):,} satır · {yol_.stat().st_size / 1e6:.1f} MB")


yaz(yol, ["geometry", "highway", "ref", "ad", "lanes", "maxspeed", "osm_id"], "yollar.gpkg", 0.0002)
yaz(ray, ["geometry", "railway", "usage", "service", "highspeed", "electrified", "maxspeed", "gauge", "yolcu", "ad",
          "osm_id"], "demiryollari.gpkg", 0.0001)
pd.DataFrame(ray_ag, columns=["osm_id", "u", "v", "lon_u", "lat_u", "lon_v", "lat_v"]).to_parquet(CIK / "demiryolu_ag.parquet")
print(f"  demiryolu_ag.parquet: {len(ray_ag):,} kenar · {(CIK / 'demiryolu_ag.parquet').stat().st_size / 1e6:.1f} MB")
yaz(ist, ["geometry", "railway", "station", "usage", "train", "ad", "operator", "disused", "nesne", "osm_id"],
    "istasyonlar.gpkg")
yaz(hav, ["geometry", "ad", "iata", "icao", "aerodrome_type", "aerodrome", "military", "alan_derece2", "nesne", "osm_id"],
    "havalimanlari.gpkg")
yaz(lim, ["geometry", "ad", "tur", "harbour", "kategori", "alan_derece2", "nesne", "osm_id"], "limanlar.gpkg", 0.0001)
yaz(hat, ["geometry", "power", "gerilim_v", "voltage", "circuits", "ad", "operator", "osm_id"], "iletim_hatlari.gpkg",
    0.0002)
yaz(sant, ["geometry", "ad", "kaynak", "yontem", "guc", "operator", "alan_derece2", "nesne", "osm_id"],
    "santraller.gpkg")
u = pd.DataFrame(uret, columns=["lon", "lat", "kaynak", "yontem", "guc", "nesne", "osm_id"])
yaz(list(zip(gpd.points_from_xy(u.lon, u.lat), u.kaynak, u.yontem, u.guc, u.nesne, u.osm_id)),
    ["geometry", "kaynak", "yontem", "guc", "nesne", "osm_id"], "uretecler.gpkg")
s = pd.DataFrame(san, columns=["geometry", "ad", "industrial", "operator", "nesne", "osm_id"])
s["osb"] = s.ad.str.contains(r"organize sanayi|\bOSB\b|O\.S\.B|organize san", case=False, regex=True)
yaz(s.values.tolist(), list(s.columns), "sanayi_alanlari.gpkg", 0.00005)
yaz(kiyi, ["geometry", "osm_id"], "kiyi.gpkg", 0.0002)
yaz(kor, ["geometry", "ad", "protect_class", "protection_title", "leisure", "nesne", "osm_id"], "korunan_alanlar.gpkg",
    0.0002)
yaz(sulak, ["geometry", "wetland", "ad", "nesne", "osm_id"], "sulak_alanlar.gpkg", 0.0001)
print(f"Tamam · {time.time() - bas:.0f} sn")
