"""
Pilot ilçelerde mahalle düzeyinde Fıtrat Uyum Endeksi (FUE)
==========================================================
Girdi : 03_VERI/islenmis/pilot_mahalle_nufus_2025.csv   ADNKS 2025 mahalle nüfusu (MEDAS; 18+ ve 0–17)
        03_VERI/islenmis/uydu/pilot_<ilçe>.tif         uydu çevre katmanları (uydu_pilot.py; yoksa v0.2 sütunları boş kalır)
        03_VERI/islenmis/pilot_osm/*                     osm_pilot_mahalle.py çıktıları (sınır, yaya ağı, donatı, ana yol)
        03_VERI/islenmis/pilot_mahalle_tkgm.gpkg         TKGM kadastro mahalleleri (OSM'de eksik sınırlar için)
        03_VERI/islenmis/osm_yesil_alanlar.gpkg          ≥0,5 ha kamusal yeşil alan (osm_ilce.py)
        03_VERI/islenmis/ilce_paneli.gpkg                ilçe sınırları (geoBoundaries ADM2)
        03_VERI/ham/ghsl/tif/                            GHSL 2018 ortalama net bina yüksekliği, GHS-POP 2020 (100 m)
Çıktı : 03_VERI/islenmis/pilot_mahalleler.gpkg           mahalle birimleri + göstergeler + FUE
        05_ANALIZ/sonuclar/fue_mahalle.csv, fue_gosterge_tanim.csv, fue_eslesme.csv, fue_ilce_ozet.csv,
        fue_duyarlilik.csv, fue_gecerlilik_mahalle.csv

Yöntem özeti
  Birim     : ADNKS mahallesi. Sınır önce OSM (admin_level=8, idari ad), yoksa TKGM kadastro mahallesi (OSM ile
              çakışan kısım çıkarılır), en son bulanık ad eşleştirmesi.
  Kökenler  : GHS-POP 2020'nin 100 m hücreleri; hücre nüfusları her mahallede ADNKS 2025 toplamına ölçeklenir.
  Mesafe    : yaya ağı üzerinde (OSM, otoyol hariç) çok kaynaklı Dijkstra; hücre ve donatı en yakın ağ düğümüne
              bağlanır, bağlanma mesafesi eklenir. Yeşil alan, ana yol ve dükkân yakınlığı kuş uçuşu.
  Endeks    : 18 gösterge → kentsel mahalleler (nüfus ≥1.000 ve GHS nüfusunun ≥%50si ≥1.500 kişi/km² hücrelerde) içinde yüzdelik puan
              (0–100, yön düzeltilmiş) → boyut puanı (B1–B6, göstergelerin ortalaması) → FUE (boyutların ortalaması).
  Geçerlilik: FUE ve boyutları ile 0–17 yaş nüfus payı arasındaki ilişki, ilçe sabit etkisiyle (mahalle düzeyinde
              eğitim ve gelir verisi yok; ilişki betimseldir).
"""
import difflib
import glob
import re
import sys
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import shapely
import statsmodels.formula.api as smf
from pyproj import Transformer
from rasterio.merge import merge
from scipy import sparse
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
PO = IS / "pilot_osm"
UYDU = IS / "uydu"  # 03_VERI/kod/uydu_pilot.py
TIF = KOK / "03_VERI" / "ham" / "ghsl" / "tif"
SON = KOK / "05_ANALIZ" / "sonuclar"
bas = time.time()

PILOT = {1327: "Fatih", 1622: "Silivri", 2050: "Başakşehir", 1829: "Nilüfer", 1863: "Kocasinan", 1827: "Meram",
         2080: "Antakya", 2085: "Onikişubat", 1587: "Safranbolu", 1187: "Beypazarı"}
YOL_KAVSAK = {"primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link",
              "unclassified", "residential", "living_street", "pedestrian"}  # Faz 2 ile aynı tanım
KENTSEL = {"park", "garden", "playground", "recreation_ground", "common", "village_green"}

# --- gösterge tanımları: (kod, boyut, ad, yön, eşik/açıklama) --------------------------------------------------
GOSTERGE = [
    ("kavsak_yog", "B1", "Kavşak yoğunluğu (/km² yapılı alan)", +1, "derece ≥3 sokak düğümü"),
    ("temel15", "B1", "15 dk'da okul + sağlık + market (%)", +1, "üçüne de ≤1.200 m yaya ağı"),
    ("yesil300", "B2", "≥0,5 ha yeşile 300 m (%)", +1, "kuş uçuşu"),
    ("yukseklik", "B2", "Yaşanan bina yüksekliği (m)", -1, "GHSL 2018, nüfus ağırlıklı"),
    ("yuksek_pay", "B2", "Yüksek binalı hücrede yaşayan (%)", -1, "hücre ortalaması ≥15 m (~5+ kat)"),
    ("anayol100", "B2", "Ana yola 100 m içinde yaşayan (%)", -1, "otoyol/devlet yolu/birincil yol"),
    ("zemin_pay", "B3", "Az katlı hücrede yaşayan (%)", +1, "hücre ortalaması ≤9 m (~3 kat)"),
    ("oyun400", "B3", "Oyun alanına 400 m (%)", +1, "yaya ağı"),
    ("okul500", "B3", "İlk/ortaokula 500 m (%)", +1, "yaya ağı; lise ve yükseköğretim hariç"),
    ("esnaf1000", "B4", "Dükkân / 1.000 kişi", +1, "OSM shop=*"),
    ("karma150", "B4", "Dükkân ya da kafeye 150 m (%)", +1, "kuş uçuşu; karma kullanım vekili"),
    ("cami500", "B5", "Camiye 500 m (%)", +1, "yaya ağı"),
    ("bulusma400", "B5", "Buluşma mekânına 400 m (%)", +1, "kahve, kütüphane, kültür ve toplum merkezi, pazar, meydan"),
    ("site_pay", "B5", "Ad/etiketle kapalı site alanı (% yapılı alan)", -1, "deneysel; OSM etiketi eksik"),
    ("muhtar_nufus", "B5", "Mahalle nüfusu (muhtar başına, ln)", -1, "yerindelik"),
    ("ulasim", "B6", "Durağa 400 m ya da raylıya 800 m (%)", +1, "yaya ağı"),
    ("yayilma", "B6", "Yapılı alan / 1.000 kişi (ha)", -1, "kişi başı arazi tüketimi"),
    ("rayli800", "B6", "Raylı istasyona 800 m (%)", +1, "yaya ağı"),
]
G = pd.DataFrame(GOSTERGE, columns=["kod", "boyut", "ad", "yon", "tanim"])
# FUE v0.2: uydu tabanlı çevre göstergeleri (Faz 3, 26.10.2026); v0.1 sütunları aynen korunur, v0.2 ayrı sütunlardadır
GOSTERGE_UYDU = [
    ("pm25", "B1", "Yıllık PM2.5 (µg/m³)", -1, "ACAG V6.GL.03, 2022–2024 ortalaması, 1 km"),
    ("agac300", "B2", "Ağaç örtüsü, 300 m içinde (%)", +1, "ESA WorldCover 2021, 10 m"),
    ("lst_goreli", "B6", "Yaz yüzey sıcaklığı, kent içi fark (°C)", -1,
     "Landsat 8/9, 2022–2025 yazları, 30 m; ilçenin kentsel mahalle ortalamasına göre"),
    ("yapili300", "B6", "Yapılı (geçirimsiz) alan, 300 m içinde (%)", -1, "ESA WorldCover sınıf 50"),
]
G2 = pd.concat([G.assign(surum="v0.1"), pd.DataFrame(GOSTERGE_UYDU, columns=G.columns).assign(surum="v0.2 eki")], ignore_index=True)
UYDU_KOL = ["agac300", "yesil300w", "yapili300", "lst", "lst_fark", "pm25"]
BOYUT_AD = {"B1": "Beden ve Can", "B2": "Akıl ve Ruh", "B3": "Nesil ve Aile", "B4": "Mülk ve Geçim",
            "B5": "Topluluk ve İnanç", "B6": "Mizan"}

# --- ad normalizasyonu --------------------------------------------------------------------------------------
TRC = str.maketrans("ÇĞİÖŞÜÂÎÛ", "CGIOSUAIU")


def sade(x):
    x = re.sub(r"\(.*?\)", "", str(x)).replace("i̇", "i").replace("İ", "I").upper().replace("İ", "I").translate(TRC)
    x = re.sub(r"\b(MAHALLESI|MAH\.?|MAHALLE)\b", "", x)
    x = re.sub(r"[^A-Z0-9]", "", x)
    return re.sub(r"(KOYU|KOY)$", "", x) or x


# --- 1. girdiler ----------------------------------------------------------------------------------------------
nuf = pd.read_csv(IS / "pilot_mahalle_nufus_2025.csv")
nuf["anahtar"] = nuf.mahalle_tuik.map(sade)
ilce = gpd.read_file(IS / "ilce_paneli.gpkg")
ilce = ilce[ilce.ilce_kod.astype(int).isin(PILOT)].copy()
ilce["ilce"] = ilce.ilce_kod.astype(int).map(PILOT)
osm = gpd.read_file(PO / "idari_sinirlar.gpkg")
osm = osm[osm.admin_level == "8"].copy()
osm["anahtar"] = osm.ad.map(sade)
yer = pd.read_parquet(PO / "yer_noktalari.parquet")
yer = gpd.GeoDataFrame(yer, geometry=gpd.points_from_xy(yer.lon, yer.lat), crs=4326)
yer = yer[yer.place.isin(["suburb", "neighbourhood", "quarter", "village", "hamlet"])].copy()
yer["anahtar"] = yer.ad.map(sade)
tkgm = gpd.read_file(IS / "pilot_mahalle_tkgm.gpkg")
tkgm["anahtar"] = tkgm.mahalle_tkgm.map(sade)
tkgm["ilce_s"] = tkgm.ilce.map(sade)
yesil = gpd.read_file(IS / "osm_yesil_alanlar.gpkg")
yesil = yesil[yesil.tur.isin(KENTSEL)]
don = pd.read_parquet(PO / "donati_noktalari.parquet")
anayol = pd.read_parquet(PO / "ana_yollar.parquet")
konut = pd.read_parquet(PO / "konut_alanlari.parquet")
kenar_tum = pd.read_parquet(PO / "yaya_kenar.parquet")
dugum_tum = pd.read_parquet(PO / "yaya_dugum.parquet").set_index("id")
print(f"girdiler yüklendi · {time.time() - bas:.0f} sn")

# donatı alt kümeleri
LISE = re.compile(r"L[İI]SE|[ÜU]N[İI]VERS|FAK[ÜU]LTE|Y[ÜU]KSEKOKUL|MESLEK Y|HALK E[ĞG]|S[ÜU]R[ÜU]C[ÜU]|KURS|ET[ÜU]T|"
                  r"DERSHANE|ENST[İI]T[ÜU]|AKADEM|MYO|REHBERL|B[İI]LSEM|B[İI]L[İI]M VE SANAT|KONSERVATUVAR", re.I)
okul = don[(don.tur == "okul") & ~don.ad.str.upper().str.contains(LISE)]
BUL_ETIKET = {"cafe", "library", "community_centre", "arts_centre", "social_centre", "townhall", "marketplace", ""}
KAT = {
    "okul": okul,
    "saglik": don[don.tur.isin(["saglik", "eczane"])],
    "market": don[don.tur == "market"],
    "cami": don[don.tur == "cami"],
    "oyun": don[don.tur == "oyun"],
    "bulusma": don[(don.tur == "bulusma") & don.etiket.isin(BUL_ETIKET)],
    "durak": don[don.tur == "durak"],
    "rayli": don[don.tur == "rayli"],
}
dukkan = don[don.tur.isin(["dukkan", "bulusma"]) & (don.etiket != "")]
SITE = re.compile(r"S[İI]TES[İI]|KONUTLARI|REZ[İI]DANS|RES[İI]DENCE|EVLER[İI]|TOWERS?\b|KONAKLARI|VADİ|LOFT", re.I)
konut["site"] = (konut.access.isin(["private", "no", "residents"]) | (konut.gated == "yes")
                 | konut.ad.str.upper().str.contains(SITE))


def ghsl_oku(b54):
    """ESRI:54009 kutusu için GHSL yükseklik ve nüfus dizileri (100 m ızgaraya hizalı)."""
    x0, y0 = np.floor(b54[0] / 100) * 100, np.floor(b54[1] / 100) * 100
    x1, y1 = np.ceil(b54[2] / 100) * 100, np.ceil(b54[3] / 100) * 100
    out = {}
    for ad, desen in [("h", "GHS_BUILT_H_*"), ("p", "GHS_POP_*")]:
        ds = [rasterio.open(f) for f in sorted(glob.glob(str(TIF / desen / "*.tif")))]
        ds = [d for d in ds if not (d.bounds.right <= x0 or d.bounds.left >= x1 or d.bounds.top <= y0 or d.bounds.bottom >= y1)]
        arr, tr = merge(ds, bounds=(x0, y0, x1, y1), res=100, nodata=0)
        a = arr[0].astype("float64")
        a[a < 0] = 0
        out[ad], out["tr"] = a, tr
        for d in ds:
            d.close()
    return out


def utm_epsg(lon):
    return 32600 + int((lon + 180) // 6) + 1


def ek_anahtar(df, kolon):
    """Bileşik adlara ek anahtar: "Erkilet Osman Gazi" → OSMANGAZI, "5.Mintika/Haraparasi" → HARAPARASI,
    "Yeni" ↔ "Yenimahalle". Ek anahtar ilçede tekse ve gerçek bir anahtarla çakışmıyorsa eklenir."""
    ek = []
    for _, r_ in df.iterrows():
        ad_ = str(r_[kolon])
        adaylar = {sade(ad_.split("/")[-1])}
        kelime = re.sub(r"\b(Mahallesi|Mah\.?)\s*$", "", ad_).split()
        if len(kelime) > 1:
            adaylar.add(sade(" ".join(kelime[1:])))
        adaylar.add(r_.anahtar + "MAHALLE")
        ek += [(a_, r_.geometry) for a_ in adaylar if a_ and a_ != r_.anahtar]
    ek = pd.DataFrame(ek, columns=["anahtar", "geometry"])
    ek = ek[~ek.anahtar.duplicated(keep=False) & ~ek.anahtar.isin(df.anahtar)]
    return pd.concat([df[["anahtar", "geometry"]], ek], ignore_index=True)


# --- 2. ilçe döngüsü ------------------------------------------------------------------------------------------
birimler, eslesme_satir = [], []
for kod, ad in PILOT.items():
    t0 = time.time()
    ip = ilce[ilce.ilce == ad].geometry.iloc[0]
    epsg = utm_epsg(ip.centroid.x)
    U = Transformer.from_crs(4326, epsg, always_xy=True)
    nn = nuf[nuf.ilce == ad].copy()
    # 2a. mahalle sınırları
    # geoBoundaries ilçe sınırı sadeleştirilmiş (kenarlarda yüzlerce metre kayma); bu yüzden aday sınırlar ilçeyle
    # 2 km tamponda kesişenler arasından, aynı adı taşıyorsa ilçeyle en çok örtüşen seçilir
    ipb = ip.buffer(0.02)
    o = osm[osm.intersects(ipb)].copy()
    o["ortusme"] = o.geometry.intersection(ip).area / o.geometry.area
    o = o[o.ortusme > 0.3].sort_values("ortusme", ascending=False).drop_duplicates("anahtar")
    o = ek_anahtar(o, "ad")
    tk = tkgm[tkgm.ilce_s == sade(ad)].copy()
    tk = tk.dissolve(by="anahtar", aggfunc={"mahalle_tkgm": "first"}).reset_index()
    tk = ek_anahtar(tk, "mahalle_tkgm")
    secilen, kaynak = {}, {}
    for a in nn.anahtar:
        if a in set(o.anahtar):
            secilen[a], kaynak[a] = o.loc[o.anahtar == a, "geometry"].iloc[0], "OSM"
    birlesik = shapely.union_all(list(secilen.values())) if secilen else shapely.Polygon()
    for a in nn.anahtar:
        if a not in secilen and a in set(tk.anahtar):
            g = shapely.union_all(tk.loc[tk.anahtar == a, "geometry"].values)
            kalan = g.difference(birlesik)
            if kalan.area > 0.3 * g.area:
                secilen[a], kaynak[a] = kalan, "TKGM"
                birlesik = birlesik.union(kalan)
    # bulanık eşleştirme: kalan ADNKS adları ↔ kullanılmamış OSM/TKGM adları
    for a in nn.anahtar:
        if a in secilen:
            continue
        for kaynak_ad, df in [("OSM~", o), ("TKGM~", tk)]:
            aday = [x for x in df.anahtar if x not in secilen and x not in set(nn.anahtar)]
            m = difflib.get_close_matches(a, aday, n=1, cutoff=0.82)
            if m:
                g = df.loc[df.anahtar == m[0], "geometry"].iloc[0].difference(birlesik)
                if not g.is_empty and g.area > 0:
                    secilen[a], kaynak[a] = g, f"{kaynak_ad}{m[0]}"
                    birlesik = birlesik.union(g)
                    break
    # son çare: OSM yer düğümlerinden (place=suburb|neighbourhood|quarter|village) Voronoi; atanmamış ilçe alanıyla ve
    # düğüm çevresinde 1,5 km (köy için 2,5 km) ile sınırlı — yaklaşık sınır, raporda ayrıca işaretlenir
    kalanlar = [a for a in nn.anahtar if a not in secilen]
    yd = yer[yer.anahtar.isin(kalanlar) & yer.within(ip.buffer(0.01))].drop_duplicates("anahtar")
    if len(yd):
        bos = ip.buffer(0.005).difference(birlesik)
        vor = shapely.voronoi_polygons(shapely.multipoints(yd.geometry.values), extend_to=ip.buffer(0.1))
        for hucre_v in shapely.get_parts(vor):
            sec = yd[yd.within(hucre_v)]
            if sec.empty:
                continue
            r_ = sec.iloc[0]
            yaricap = 0.025 if r_.place in ("village", "hamlet") else 0.015
            g = hucre_v.intersection(bos).intersection(r_.geometry.buffer(yaricap))
            if not g.is_empty and g.area > 0:
                secilen[r_.anahtar], kaynak[r_.anahtar] = g, "OSM-yer (Voronoi)"
    nn["kaynak"] = nn.anahtar.map(kaynak).fillna("yok")
    eslesme_satir.append(nn[["ilce", "mahalle_tuik", "mahalle_kod", "nufus", "kaynak"]])
    mg = gpd.GeoDataFrame(nn[nn.anahtar.isin(secilen)].copy(), geometry=[secilen[a] for a in nn.anahtar if a in secilen], crs=4326)
    mg["geometry"] = mg.geometry.buffer(0)
    mg = mg[~mg.geometry.is_empty].copy()
    mg54 = mg.to_crs("ESRI:54009")
    mg["alan_ha"] = mg.to_crs(epsg).area / 1e4

    # 2b. GHSL hücreleri → mahalle
    gh = ghsl_oku(mg54.total_bounds)
    r, c = np.nonzero((gh["p"] > 0) | (gh["h"] > 0))
    xs = gh["tr"].c + (c + 0.5) * 100
    ys = gh["tr"].f - (r + 0.5) * 100
    hucre = gpd.GeoDataFrame({"p": gh["p"][r, c], "h": gh["h"][r, c]}, geometry=gpd.points_from_xy(xs, ys), crs="ESRI:54009")
    hucre = gpd.sjoin(hucre, mg54[["mahalle_kod", "geometry"]], predicate="within", how="inner").drop(columns="index_right")
    hucre = hucre[~hucre.index.duplicated()]
    # nüfusu olmayan mahalle (yeni yapılaşma vb.) için temsilî nokta
    eks = set(mg.mahalle_kod) - set(hucre[hucre.p > 0].mahalle_kod)
    if eks:
        ek = mg54[mg54.mahalle_kod.isin(eks)].copy()
        ek["geometry"] = ek.geometry.representative_point()
        ek["p"], ek["h"] = 1.0, 0.0
        hucre = pd.concat([hucre, ek[["p", "h", "geometry", "mahalle_kod"]]], ignore_index=True)
    hucre = hucre.reset_index(drop=True)
    toplam = hucre.groupby("mahalle_kod").p.transform("sum")
    hucre["w"] = hucre.p / toplam * hucre.mahalle_kod.map(mg.set_index("mahalle_kod").nufus)
    ll = hucre.to_crs(4326)
    hx, hy = U.transform(ll.geometry.x.values, ll.geometry.y.values)
    hxy = np.c_[hx, hy]

    # 2c. yaya ağı
    lon0, lat0, lon1, lat1 = shapely.union_all([ip, shapely.box(*mg.total_bounds)]).buffer(0.02).bounds
    d = dugum_tum[(dugum_tum.lon >= lon0) & (dugum_tum.lon <= lon1) & (dugum_tum.lat >= lat0) & (dugum_tum.lat <= lat1)]
    k = kenar_tum[kenar_tum.u.isin(d.index) & kenar_tum.v.isin(d.index)]
    idx = pd.Series(np.arange(len(d)), index=d.index)
    nx_, ny_ = U.transform(d.lon.values, d.lat.values)
    nxy = np.c_[nx_, ny_]
    ui, vi = idx[k.u].values, idx[k.v].values
    wgt = np.hypot(*(nxy[ui] - nxy[vi]).T) + 1e-3
    e = pd.DataFrame({"a": np.r_[ui, vi], "b": np.r_[vi, ui], "w": np.r_[wgt, wgt]}).groupby(["a", "b"]).w.min().reset_index()
    n = len(d)
    agac = cKDTree(nxy)
    h_snap, h_dug = agac.query(hxy)

    def ag_mesafe(df, limit=3000, maxsnap=300):
        if df.empty:
            return np.full(len(hxy), np.inf)
        px, py = U.transform(df.lon.values, df.lat.values)
        ds, di = agac.query(np.c_[px, py], distance_upper_bound=maxsnap)
        ok = np.isfinite(ds)
        if not ok.any():
            return np.full(len(hxy), np.inf)
        s = pd.DataFrame({"b": di[ok], "w": ds[ok] + 1e-3}).groupby("b").w.min()
        rows = np.r_[e.a.values, np.full(len(s), n)]
        cols = np.r_[e.b.values, s.index.values]
        vals = np.r_[e.w.values, s.values]
        M = sparse.csr_matrix((vals, (rows, cols)), shape=(n + 1, n + 1))
        dist = dijkstra(M, directed=True, indices=n, limit=limit)
        return h_snap + dist[h_dug]

    D = {kat: ag_mesafe(df) for kat, df in KAT.items()}

    # 2d. kuş uçuşu mesafeler
    def oklid_nokta(df):
        if df.empty:
            return np.full(len(hxy), np.inf)
        px, py = U.transform(df.lon.values, df.lat.values)
        return cKDTree(np.c_[px, py]).query(hxy)[0]

    def oklid_geom(gs, maxd):
        gs = gs[~gs.is_empty]
        if gs.empty:
            return np.full(len(hxy), np.inf)
        tr_ = shapely.STRtree(gs.values)
        pts = shapely.points(hxy)
        i_pt, i_g = tr_.query(pts, predicate="dwithin", distance=maxd)
        out = np.full(len(hxy), np.inf)
        if len(i_pt):
            dd = shapely.distance(pts[i_pt], gs.values[i_g])
            np.minimum.at(out, i_pt, dd)
        return out

    bx =gpd.GeoSeries([ip.buffer(0.02)], crs=4326).to_crs("ESRI:54009").total_bounds
    yb = yesil.cx[bx[0]:bx[2], bx[1]:bx[3]].to_crs(epsg).geometry
    D["yesil"] = oklid_geom(yb, 300)
    ay = anayol.copy()
    ay["geometry"] = shapely.from_wkb(ay.wkb.values)
    ay = gpd.GeoDataFrame(ay, geometry="geometry", crs=4326).cx[lon0:lon1, lat0:lat1].to_crs(epsg).geometry
    D["anayol"] = oklid_geom(ay, 100)
    dk = dukkan[(dukkan.lon >= lon0) & (dukkan.lon <= lon1) & (dukkan.lat >= lat0) & (dukkan.lat <= lat1)]
    D["dukkan"] = oklid_nokta(dk)

    # 2e. hücre göstergeleri → mahalle (nüfus ağırlıklı)
    H = pd.DataFrame({"mahalle_kod": hucre.mahalle_kod.values, "w": hucre.w.values, "h": hucre.h.values,
                      "yapili": (hucre.h > 0).astype(float).values})
    H["temel15"] = ((D["okul"] <= 1200) & (D["saglik"] <= 1200) & (D["market"] <= 1200)) * 100.0
    H["yesil300"] = (D["yesil"] <= 300) * 100.0
    H["yuksek_pay"] = (H.h >= 15) * 100.0
    H["zemin_pay"] = (H.h <= 9) * 100.0
    H["anayol100"] = (D["anayol"] <= 100) * 100.0
    H["oyun400"] = (D["oyun"] <= 400) * 100.0
    H["okul500"] = (D["okul"] <= 500) * 100.0
    H["okul800"] = (D["okul"] <= 800) * 100.0
    H["karma150"] = (D["dukkan"] <= 150) * 100.0
    H["cami500"] = (D["cami"] <= 500) * 100.0
    H["bulusma400"] = (D["bulusma"] <= 400) * 100.0
    H["ulasim"] = ((D["durak"] <= 400) | (D["rayli"] <= 800)) * 100.0
    H["rayli800"] = (D["rayli"] <= 800) * 100.0
    for kat in ["okul", "saglik", "market", "cami", "oyun"]:
        H[f"d_{kat}"] = np.minimum(D[kat], 3000)  # ortalama ağ mesafesi (m, 3 km'de kesilir)
    H["yukseklik"] = H.h
    # uydu katmanları: hücre merkezinde örnekleme (30 m raster)
    uf = UYDU / f"pilot_{ad}.tif"
    if uf.exists():
        with rasterio.open(uf) as u:
            if u.crs.to_epsg() == epsg:
                tx, ty = hxy[:, 0], hxy[:, 1]
            else:
                tx, ty = Transformer.from_crs(epsg, u.crs, always_xy=True).transform(hxy[:, 0], hxy[:, 1])
            ub = dict(zip(u.descriptions, np.array(list(u.sample(zip(tx, ty)))).T))
        ub["yesil300w"] = ub["yesil300"]
        for c_ in ("agac300", "yesil300w", "yapili300"):  # FFT evrişiminden kalan −0,0 değerleri
            ub[c_] = np.clip(ub[c_], 0, 100)
        for c_ in UYDU_KOL:
            H[c_] = ub[c_]
    else:
        for c_ in UYDU_KOL:
            H[c_] = np.nan
    pay = ["temel15", "yesil300", "yuksek_pay", "zemin_pay", "anayol100", "oyun400", "okul500", "okul800", "karma150",
           "cami500", "bulusma400", "ulasim", "rayli800", "yukseklik"] + [f"d_{k}" for k in ["okul", "saglik", "market", "cami", "oyun"]]
    wsum = H.groupby("mahalle_kod").w.sum()
    agg = H[pay].multiply(H.w, axis=0).groupby(H.mahalle_kod).sum().div(wsum, axis=0)
    for c_ in UYDU_KOL:  # eksik değerler ağırlığa girmez
        ok = H[c_].notna()
        agg[c_] = (H[c_].where(ok, 0) * H.w).groupby(H.mahalle_kod).sum() / H.w.where(ok, 0).groupby(H.mahalle_kod).sum()
    agg["yapili_ha"] = H.groupby("mahalle_kod").yapili.sum()
    agg["ghs_nufus"] = hucre.groupby("mahalle_kod").p.sum()
    # kentsel ölçütü (DEGURBA kent merkezi yoğunluk eşiği): GHS nüfusunun ≥1.500 kişi/km² (≥15 kişi/hücre) hücrelerdeki payı
    agg["merkez_pay"] = hucre.p.where(hucre.p >= 15, 0).groupby(hucre.mahalle_kod).sum() / agg.ghs_nufus

    # kavşak yoğunluğu, dükkân sayısı, site payı (mahalle poligonu içinde)
    kk = k[k.highway.isin(YOL_KAVSAK)]
    deg = pd.concat([kk.u, kk.v]).value_counts()
    kav = d.loc[deg.index[deg.values >= 3].intersection(d.index)]
    kav = gpd.GeoDataFrame(geometry=gpd.points_from_xy(kav.lon, kav.lat), crs=4326)
    agg["kavsak_n"] = gpd.sjoin(kav, mg[["mahalle_kod", "geometry"]], predicate="within").groupby("mahalle_kod").size()
    dkg = gpd.GeoDataFrame(geometry=gpd.points_from_xy(dk.lon, dk.lat), crs=4326)
    agg["dukkan_n"] = gpd.sjoin(dkg, mg[["mahalle_kod", "geometry"]], predicate="within").groupby("mahalle_kod").size()
    ks = konut[konut.site].copy()
    ks = gpd.GeoDataFrame(ks, geometry=shapely.from_wkb(ks.wkb.values), crs=4326).cx[lon0:lon1, lat0:lat1]
    if len(ks):
        ks = shapely.union_all(ks.to_crs(epsg).geometry.values)
        agg["site_ha"] = mg.set_index("mahalle_kod").to_crs(epsg).geometry.intersection(ks).area / 1e4
    mg = mg.merge(agg.reset_index(), on="mahalle_kod", how="left")
    for c_ in ["kavsak_n", "dukkan_n", "site_ha"]:
        mg[c_] = mg[c_].fillna(0) if c_ in mg else 0.0
    mg["kavsak_yog"] = np.where(mg.yapili_ha >= 5, mg.kavsak_n / (mg.yapili_ha / 100), np.nan)
    mg["esnaf1000"] = mg.dukkan_n / mg.nufus * 1000
    mg["site_pay"] = np.where(mg.yapili_ha >= 5, np.minimum(100, 100 * mg.site_ha / mg.yapili_ha), np.nan)
    mg["muhtar_nufus"] = np.log(mg.nufus.clip(lower=1))
    mg["yayilma"] = mg.yapili_ha / (mg.nufus.clip(lower=1) / 1000)
    mg["yogunluk"] = mg.nufus / mg.alan_ha
    mg["cocuk_pay"] = 100 * mg.nufus_0_17 / mg.nufus
    mg["dugum_n"], mg["utm"] = n, epsg
    birimler.append(mg)
    print(f"{ad:<11} mahalle {len(nn):>3} · sınır {len(mg):>3} ({mg.nufus.sum() / nn.nufus.sum():.1%} nüfus) · hücre {len(hucre):>6}"
          f" · düğüm {n:>7} · {time.time() - t0:.0f} sn")

M = gpd.GeoDataFrame(pd.concat(birimler, ignore_index=True), crs=4326)
E = pd.concat(eslesme_satir, ignore_index=True)
E.to_csv(SON / "fue_eslesme.csv", index=False, encoding="utf-8")

# --- 3. endeks ------------------------------------------------------------------------------------------------
M["kentsel"] = (M.nufus >= 1000) & (M.merkez_pay >= 0.5)
# yaz yüzey sıcaklığı: ilçenin kentsel mahallelerinin nüfus ağırlıklı ortalamasına göre fark. İlçe alanına göre fark
# (lst_fark) kurak ilçelerde kenti çıplak tarlaya göre "serin" gösterdiği için endekste kent içi fark kullanılır
_k = M[M.kentsel & M.lst.notna()]
M["lst_goreli"] = M.lst - M.ilce.map(_k.groupby("ilce").apply(lambda x: np.average(x.lst, weights=x.nufus)))
ref = M[M.kentsel]
for _, g_ in G2.iterrows():
    v = M[g_.kod].astype(float)
    r_ = ref[g_.kod].dropna().astype(float).sort_values().values
    yp = np.array([(np.searchsorted(r_, x, "left") + np.searchsorted(r_, x, "right")) / 2 / len(r_) * 100
                   if np.isfinite(x) else np.nan for x in v])
    M[f"p_{g_.kod}"] = yp if g_.yon > 0 else 100 - yp
for b in BOYUT_AD:
    M[b] = M[[f"p_{k_}" for k_ in G[G.boyut == b].kod]].mean(axis=1)
M["FUE"] = M[list(BOYUT_AD)].mean(axis=1)

# duyarlılık varyantları
M["FUE_duz"] = M[[f"p_{k_}" for k_ in G.kod]].mean(axis=1)
M["FUE_yuksekliksiz"] = M[[f"p_{k_}" for k_ in G.kod if k_ not in ("yukseklik", "yuksek_pay", "zemin_pay")]].mean(axis=1)
M["FUE_sitesiz"] = M[[f"p_{k_}" for k_ in G.kod if k_ != "site_pay"]].mean(axis=1)
# iki alt endeks (ilçe düzeyi geçerlilik sınamasından sonra; fue_ilce_gecerlilik.py): Erişim (E) ve Çevre-ölçek (Ç)
ERISIM = ["kavsak_yog", "temel15", "oyun400", "okul500", "esnaf1000", "karma150", "cami500", "bulusma400", "ulasim", "rayli800"]
CEVRE = ["yesil300", "yukseklik", "yuksek_pay", "zemin_pay", "anayol100", "yayilma", "site_pay", "muhtar_nufus"]
M["FUE_E"] = M[[f"p_{k_}" for k_ in ERISIM]].mean(axis=1)
M["FUE_C"] = M[[f"p_{k_}" for k_ in CEVRE]].mean(axis=1)
# v0.2: uydu göstergeleri eklenmiş boyutlar ve Ç ekseni (E değişmez)
for b in BOYUT_AD:
    M[b + "_v2"] = M[[f"p_{k_}" for k_ in G2[G2.boyut == b].kod]].mean(axis=1)
M["FUE_v2"] = M[[b + "_v2" for b in BOYUT_AD]].mean(axis=1)
CEVRE_V2 = CEVRE + ["agac300", "pm25", "lst_goreli", "yapili300"]
M["FUE_C_v2"] = M[[f"p_{k_}" for k_ in CEVRE_V2]].mean(axis=1)
zs = []
for _, g_ in G.iterrows():
    v = M[g_.kod].astype(float)
    if g_.kod in ("esnaf1000", "yayilma", "kavsak_yog"):
        v = np.log1p(v)
    zs.append(g_.yon * (v - v[M.kentsel].mean()) / v[M.kentsel].std())
Z = pd.concat(zs, axis=1).clip(-3, 3)
M["FUE_z"] = Z.mean(axis=1)
Zk = Z[M.kentsel].fillna(0)
ozd, ozv = np.linalg.eigh(np.corrcoef(Zk.T.values))
w1 = ozv[:, -1] * np.sign(ozv[:, -1].sum())
M["FUE_pca"] = Z.fillna(0).values @ w1
duy = []
for v in ["FUE_duz", "FUE_yuksekliksiz", "FUE_sitesiz", "FUE_z", "FUE_pca"]:
    rho = spearmanr(M.loc[M.kentsel, "FUE"], M.loc[M.kentsel, v], nan_policy="omit")[0]
    duy.append((v, round(rho, 3)))
duy.append(("PCA 1. bileşen açıklanan varyans", round(ozd[-1] / ozd.sum(), 3)))
pd.DataFrame(duy, columns=["varyant", "spearman_FUE_ile"]).to_csv(SON / "fue_duyarlilik.csv", index=False)

# --- 4. geçerlilik (betimsel): 0–17 yaş payı ile ilişki, ilçe sabit etkisi -------------------------------------
V = M[M.kentsel & M.cocuk_pay.notna()].copy()
for c_ in ["FUE", "FUE_E", "FUE_C", "FUE_v2", "FUE_C_v2"] + list(BOYUT_AD) + ["FUE_yuksekliksiz", "agac300", "pm25", "lst_goreli", "yapili300"]:
    V[c_ + "_z"] = (V[c_] - V[c_].mean()) / V[c_].std()
V["ln_yog"] = np.log(V.yogunluk)
gec = []
for x in ["FUE", "FUE_E", "FUE_C", "FUE_v2", "FUE_C_v2", "FUE_yuksekliksiz"] + list(BOYUT_AD) + ["agac300", "pm25", "lst_goreli", "yapili300"]:
    for ad_, f in [("ilçe SE", f"cocuk_pay ~ {x}_z + C(ilce)"), ("ilçe SE + ln yoğunluk", f"cocuk_pay ~ {x}_z + ln_yog + C(ilce)")]:
        Vx = V.dropna(subset=[f"{x}_z"])
        m_ = smf.wls(f, Vx, weights=Vx.nufus).fit(cov_type="HC3")
        gec.append((x, ad_, m_.params[f"{x}_z"], m_.bse[f"{x}_z"], m_.pvalues[f"{x}_z"], m_.nobs, m_.rsquared))
gec = pd.DataFrame(gec, columns=["degisken", "model", "katsayi_puan", "sh", "p", "n", "r2"])
gec.to_csv(SON / "fue_gecerlilik_mahalle.csv", index=False)
ilce_ici = V.groupby("ilce").apply(lambda x: pd.Series({"n": len(x), "spearman_FUE_cocuk": spearmanr(x.FUE, x.cocuk_pay)[0]}))

# --- 5. çıktılar ----------------------------------------------------------------------------------------------
G2.assign(boyut_ad=G2.boyut.map(BOYUT_AD)).to_csv(SON / "fue_gosterge_tanim.csv", index=False, encoding="utf-8")
kol = ["il", "ilce", "mahalle_tuik", "mahalle_kod", "kaynak", "nufus", "nufus_0_17", "cocuk_pay", "alan_ha", "yogunluk",
       "kentsel", "merkez_pay", "ghs_nufus", "yapili_ha"] + list(G.kod) + ["okul800", "d_okul", "d_saglik", "d_market", "d_cami", "d_oyun"] \
      + list(BOYUT_AD) + ["FUE", "FUE_E", "FUE_C", "FUE_duz", "FUE_yuksekliksiz", "FUE_sitesiz", "FUE_z", "FUE_pca"]       + ["pm25", "agac300", "lst_goreli", "lst_fark", "yapili300", "yesil300w", "lst"] + [b + "_v2" for b in BOYUT_AD] + ["FUE_v2", "FUE_C_v2"]
M[kol].to_csv(SON / "fue_mahalle.csv", index=False, encoding="utf-8")
M[kol + ["geometry"]].to_file(IS / "pilot_mahalleler.gpkg", driver="GPKG")


def wavg(x, c):
    x = x[x[c].notna()]
    return np.average(x[c], weights=x.nufus) if len(x) else np.nan


oz = []
for ad_, x in M.groupby("ilce"):
    k_ = x[x.kentsel]
    satir = {"ilce": ad_, "mahalle": len(x), "kentsel": len(k_), "nufus_kapsam": x.nufus.sum(),
             "nufus_adnks": nuf[nuf.ilce == ad_].nufus.sum()}
    for c_ in ["FUE", "FUE_E", "FUE_C", "FUE_v2", "FUE_C_v2", "agac300", "pm25", "lst", "lst_goreli", "yapili300"] + list(BOYUT_AD) + ["temel15", "yesil300", "okul500", "cami500", "oyun400", "yukseklik", "ulasim",
                                           "kavsak_yog", "cocuk_pay"]:
        satir[c_] = wavg(k_, c_)
    satir["FUE_min"], satir["FUE_max"] = k_.FUE.min(), k_.FUE.max()
    oz.append(satir)
OZ = pd.DataFrame(oz)
OZ["kapsam_pay"] = 100 * OZ.nufus_kapsam / OZ.nufus_adnks
OZ = OZ.merge(ilce_ici, left_on="ilce", right_index=True, how="left").sort_values("FUE", ascending=False)
OZ.to_csv(SON / "fue_ilce_ozet.csv", index=False, encoding="utf-8")

print("\nEşleşme kaynakları:\n", E.assign(k=E.kaynak.str.replace(r"~.*", "~", regex=True)).groupby(["ilce", "k"]).nufus.sum().unstack().fillna(0).astype(int))
print("\nİlçe özeti (kentsel mahalleler, nüfus ağırlıklı):\n", OZ.round(1).to_string(index=False))
print("\nDuyarlılık:", duy)
print("\nGeçerlilik:\n", gec.round(3).to_string(index=False))
print(f"\nTamam · {time.time() - bas:.0f} sn")

# --- 6. OSM kapsamı: kapsanan mahallelerde 10.000 kişiye düşen donatı kaydı (veri eksikliğinin ölçüsü) --------------
pts = gpd.GeoDataFrame(don[["tur"]], geometry=gpd.points_from_xy(don.lon, don.lat), crs=4326)
pts = pts.cx[M.total_bounds[0]:M.total_bounds[2], M.total_bounds[1]:M.total_bounds[3]]
j = gpd.sjoin(pts, M[["ilce", "geometry"]], predicate="within")
kap = j.groupby(["ilce", "tur"]).size().unstack(fill_value=0)
kap = kap.div(M.groupby("ilce").nufus.sum(), axis=0) * 10000
kap.round(2).to_csv(SON / "fue_osm_kapsam.csv", encoding="utf-8")
print("\nOSM kaydı / 10.000 kişi:\n", kap.round(1).to_string())
