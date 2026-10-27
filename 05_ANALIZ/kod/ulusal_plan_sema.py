"""
Faz 4 · Ulusal mekânsal çerçeve — kademeli yerleşim ve koridor şeması (ilke haritası)
=================================================================================
Bu betik yer seçimi yapmaz, aday sıralamaz. İlkelerin ulusal ölçekte nerede geçerli olduğunu (bant, alan) ve mevcut
yapının ilkelere ne ölçüde uyduğunu hesaplar. Her somut proje ayrıntılı etüt (jeoloji, toprak sınıfı, su, mülkiyet,
katılım) gerektirir.

Girdi : 03_VERI/islenmis/ulusal_altyapi/ (izgara_*, kisit, demiryollari, istasyonlar_yolcu, limanlar_yuk, sanayi_alanlari,
        iletim_hatlari, santraller, uretecler, kent_merkezleri.csv), 05_ANALIZ/sonuclar/ulusal_plan_ruzgar_il.csv,
        03_VERI/islenmis/pilot_osm/yer_noktalari.parquet (yer adları)
Çıktı : 03_VERI/islenmis/ulusal_altyapi/sema_kentler.gpkg, sema_koridorlar.gpkg,
        izgara_sema.tif (bant 1 uydu kent bandı, bant 2 sanayi ilke alanı: 1 iç bölge, 2 limana ≤ 50 km)
        05_ANALIZ/sonuclar/ulusal_plan_kademe.csv, ulusal_plan_kentler.csv, ulusal_plan_koridorlar.csv,
        ulusal_plan_karsi_miknatis.csv, ulusal_plan_uydu_kentler.csv (büyük kent başına sayı),
        ulusal_plan_sanayi_ilke_alani.csv (il), ulusal_plan_sanayi_osb_ilke.csv, ulusal_plan_sanayi_osb_ilke_ozet.csv,
        ulusal_plan_enerji.csv, ulusal_plan_enerji_kaynak_bolge.csv
Kurallar [V]:
  Kentsel küme      ≥ 300 kişi/km² bitişik 250 m hücreler (8 komşu); nüfus TÜİK 2025, dağılım GHSL 2020
  Kademe            K1 ≥ 1 milyon · K2 250 bin–1 milyon · K3 50–250 bin · K4 10–50 bin · K5 2–10 bin
  Koridor           il ana kentleri arasında OSM demiryolu ağında (mevcut + yapımda + planlı) en kısa yol; ağ yoksa ya da
                    yol kuş uçuşunun 2,2 katı + 20 km’den uzunsa "yeni bağlantı" (düz çizgi, şematik)
  Uydu kent bandı   koridor hattının K1–K2 merkezine 20–70 km (≥ 3 milyonluk metropolde hızlı tren hattında 110 km) uzak ve
                    K1–K3 kent dokusuna ≥ 5 km kesimi. Bantta "ilkeyi sağlayan istasyon": mevcut K4–K5 kasabasına ≤ 2 km;
                    3 km çevresinde ≥ 5 km² elverişli arazi; diri faya > 1 km; 3 km çevrenin < %50'si ova tarım
  Sanayi ilke alanı mutlak kısıt (1 km fay bandı dahil) ve ova tarım dışında; eğim ≤ %8; demiryoluna ≤ 5 km;
                    K1–K3 kentinin kentsel dokusuna ≥ 3 km, ≥ 2.000 nüfuslu her kümeye ≥ 1 km; en yakın K1–K3 kentine 8–40 km;
                    rüzgârın alandan kente doğru estiği saatlerin payı ≤ %10 (ERA5 2023–2024 sekiz yön sıklığı).
                    5 km fay bandına düşen pay ağır ve tehlikeli madde içeren sanayi için ayrıca raporlanır
"""
import sys
from pathlib import Path

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize, shapes
from scipy import ndimage
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point, shape
from shapely.ops import linemerge, unary_union

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
CIK = KOK / "03_VERI" / "islenmis" / "ulusal_altyapi"
SON = KOK / "05_ANALIZ" / "sonuclar"
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m +no_defs"
H = 250.0
HA = H * H / 1e6  # km²


def oku(ad, bant=1):
    with rasterio.open(CIK / ad) as d:
        return d.read(bant), d.transform


nuf, TR = oku("izgara_nufus.tif")
NY, NX = nuf.shape
ilc, _ = oku("izgara_ilce.tif")
kara = ilc > 0
anahtar = pd.read_csv(CIK / "izgara_ilce_anahtar.csv", dtype={"ilce_kod": str})
IL = np.array([""] + anahtar.il.tolist(), dtype=object)
ILCE = np.array([""] + anahtar.ilce_ad_tuik.str.title().tolist(), dtype=object)
kisit, _ = oku("izgara_kisit.tif")
egim, _ = oku("izgara_egim.tif")
egim = np.where(egim == 65535, np.nan, egim / 10.0)
B = {ad: (kisit >> i) & 1 == 1 for i, ad in enumerate(
    ["fay_1km", "fay_5km", "ova_tarim", "tarim", "sulak", "su", "kiyi_500m", "orman", "taskin", "korunan", "dik"])}
mutlak = B["fay_1km"] | B["sulak"] | B["su"] | B["kiyi_500m"] | B["orman"] | B["taskin"] | B["korunan"]
elverisli = kara & ~mutlak & ~B["ova_tarim"] & ~B["dik"] & (np.nan_to_num(egim, nan=99) <= 15)


def rc(x, y):
    return (np.asarray((TR.f - np.asarray(y)) // H, int).clip(0, NY - 1),
            np.asarray((np.asarray(x) - TR.c) // H, int).clip(0, NX - 1))


def xy(r, c):
    return TR.c + (np.asarray(c) + 0.5) * H, TR.f - (np.asarray(r) + 0.5) * H


# =============================== A. Kademeli yerleşim sistemi (bugün) =========================================
kentsel = (nuf >= 300 * HA) & kara
# Köprüleme: kentsel hücrelere ≤ 1 km'lik su / deniz ya da yapılı (WorldCover ≥ %30) hücreler bağlantıya katılır;
# kara üzerindeki boşluklar kapatılmaz (kıyı şeridi boyunca kesintili yerleşimler ayrı kalır). Etiket yalnız kentsel hücrelere.
with rasterio.open(CIK / "izgara_ortu.tif") as d:
    su_, yap_ = d.read(4), d.read(3)
su_m = ((su_ >= 30) & (su_ != 255)) | ((yap_ >= 30) & (yap_ != 255)) | ~kara  # su, deniz ya da yapılı (yol, sanayi, nehir kıyısı)
kopru = ndimage.binary_dilation(kentsel, iterations=4) & su_m
lab, n = ndimage.label(kentsel | kopru, structure=np.ones((3, 3)))
lab = np.where(kentsel, lab, 0)
del su_, yap_, kopru
idx = np.arange(1, n + 1)
kp = ndimage.sum(nuf, lab, idx)
alan = ndimage.sum(np.ones_like(nuf), lab, idx) * HA
com = np.array(ndimage.center_of_mass(nuf, lab, idx))
k = pd.DataFrame({"lab": idx, "nufus": kp, "alan_km2": alan, "r": com[:, 0], "c": com[:, 1]})
k = k[k.nufus >= 2000].copy()
k["x"], k["y"] = xy(k.r, k.c)
k["kademe"] = pd.cut(k.nufus, [2000, 10_000, 50_000, 250_000, 1_000_000, 1e9], right=False,
                     labels=["K5", "K4", "K3", "K2", "K1"]).astype(str)
# küme içindeki illerin nüfus payları → ad
rr, cc = np.nonzero(lab)
lb = lab[rr, cc]
sec = np.isin(lb, k.lab.values)
t = pd.DataFrame({"lab": lb[sec], "il": IL[ilc[rr[sec], cc[sec]]], "ilce": ILCE[ilc[rr[sec], cc[sec]]],
                  "p": nuf[rr[sec], cc[sec]]})
il_pay = t.groupby(["lab", "il"]).p.sum().reset_index().sort_values(["lab", "p"], ascending=[True, False])
ilce_bas = t.groupby(["lab", "ilce", "il"]).p.sum().reset_index().sort_values("p", ascending=False).drop_duplicates("lab")
yer = pd.read_parquet(KOK / "03_VERI" / "islenmis" / "pilot_osm" / "yer_noktalari.parquet")
yer = yer[yer.place.isin(["city", "town"])]
yg = gpd.GeoSeries(gpd.points_from_xy(yer.lon, yer.lat), crs=4326).to_crs(LCC)
yr, yc = rc(yg.x.values, yg.y.values)
yer = yer.assign(lab=lab[yr, yc], oncelik=yer.place.map({"city": 0, "town": 1}))
kk = k.set_index("lab")
yer = yer[yer.lab.isin(kk.index)]


def kume_adi(lb_):
    s = il_pay[il_pay.lab == lb_]
    tot = s.p.sum()
    ils = s[s.p >= 0.08 * tot].il.tolist()
    if len(ils) > 1:
        return "–".join(ils[:3])
    y = yer[yer.lab == lb_].sort_values("oncelik")
    if len(y):
        return y.iloc[0].ad
    b = ilce_bas[ilce_bas.lab == lb_]
    return b.iloc[0].ilce if len(b) else ils[0]


k["ad"] = [kume_adi(v) for v in k.lab]
# il adıyla anılan kent kümelerinde kent adını kullan (haritada il adı iki kez görünmesin)
k["ad"] = k.ad.replace({"Hatay": "Antakya", "Sakarya": "Adapazarı", "Kocaeli": "İzmit", "Elâzığ": "Elazığ"})
k["il"] = [il_pay[il_pay.lab == v].iloc[0].il for v in k.lab]
pt = gpd.GeoSeries(gpd.points_from_xy(k.x, k.y), crs=LCC).to_crs(4326)
k["lon"], k["lat"] = pt.x.values.round(4), pt.y.values.round(4)
k = k.sort_values("nufus", ascending=False)
k[["lab", "ad", "il", "kademe", "nufus", "alan_km2", "x", "y", "lon", "lat"]].round(1).to_csv(
    SON / "ulusal_plan_kentler.csv", index=False, encoding="utf-8")
gpd.GeoDataFrame(k[["lab", "ad", "il", "kademe", "nufus", "alan_km2"]], geometry=gpd.points_from_xy(k.x, k.y),
                 crs=LCC).to_crs(4326).to_file(CIK / "sema_kentler.gpkg", driver="GPKG")
P = nuf[kara].sum()
kad = k.groupby("kademe").agg(kume=("lab", "size"), nufus=("nufus", "sum")).reindex(["K1", "K2", "K3", "K4", "K5"])
kad.loc["küme dışı (kır, dağınık)"] = [np.nan, P - k.nufus.sum()]
kad["nufus_pay"] = 100 * kad.nufus / P
kad.round(1).to_csv(SON / "ulusal_plan_kademe.csv", encoding="utf-8")
print("Kademeler (nüfus 2025):")
print(kad.round(1))
print(k[k.kademe.isin(["K1"])][["ad", "nufus", "alan_km2"]].round(0).to_string(index=False))

# =============================== B. Koridorlar (demiryolu ağı üzerinde) =======================================
ray = gpd.read_file(CIK / "demiryollari.gpkg")
ray = ray[ray.railway.isin(["rail", "construction", "proposed"]) & ~ray.usage.isin(["industrial", "military"])].to_crs(LCC)
ray["servis"] = ray.service.isin(["yard", "siding", "spur", "crossover"])  # istasyon içi hatlar: süreklilik için grafa girer
ray["durum"] = np.select([(ray.railway == "rail") & (ray.highspeed == "yes"), ray.railway == "rail",
                          ray.railway == "construction"], ["hizli", "konvansiyonel", "yapim"], "planli")
# Ağ: tam çözünürlüklü OSM kenarları (demiryolu_ag.parquet); ortak OSM düğümü = aynı koordinat = aynı graf düğümü
ag = pd.read_parquet(CIK / "demiryolu_ag.parquet")
ag = ag.merge(ray[["osm_id", "durum", "servis"]].drop_duplicates("osm_id"), on="osm_id")
from pyproj import Transformer
_t = Transformer.from_crs(4326, LCC, always_xy=True)
ux, uy_ = _t.transform(ag.lon_u.values, ag.lat_u.values)
vx, vy = _t.transform(ag.lon_v.values, ag.lat_v.values)
ux, uy_, vx, vy = (np.round(a_, 1) for a_ in (ux, uy_, vx, vy))
L_ = np.hypot(ux - vx, uy_ - vy)
w_ = L_ * np.where(ag.durum == "planli", 1.15, 1.0) * np.where(ag.servis, 1.5, 1.0)
G = nx.Graph()
G.add_edges_from(((a1, a2), (b1, b2), {"w": w, "L": L, "durum": d})
                 for a1, a2, b1, b2, w, L, d in zip(ux, uy_, vx, vy, w_, L_, ag.durum) if L > 0)
dugum = np.array(list(G.nodes))
tree = cKDTree(dugum)
# OSM'de kopuk kalan küçük boşluklar (ör. köprü onarımı, eksik çizim): uç düğümü BAŞKA bileşenden 1,5 km içindeki en
# yakın düğüme bağla (üç tur; her turda bileşenler yeniden hesaplanır)
for tur in range(3):
    bil = {v: i for i, c in enumerate(nx.connected_components(G)) for v in c}
    eklenen = 0
    for u in [v for v in G.nodes if G.degree(v) == 1]:
        ds, ii = tree.query(u, k=60, distance_upper_bound=1500)
        for d_, i_ in zip(ds, ii):
            if not np.isfinite(d_):
                break
            v = tuple(dugum[i_])
            if bil[v] != bil[u]:
                G.add_edge(u, v, w=d_, L=d_, durum="baglanti")
                eklenen += 1
                break
    if not eklenen:
        break
print(f"Demiryolu ağı: {G.number_of_nodes():,} düğüm, {G.number_of_edges():,} kenar, "
      f"{nx.number_connected_components(G)} bileşen")

# hub yakalama yalnız uzunluğu ≥ 30 km olan bileşenlerin düğümlerine (kopuk kısa parçalara takılmamak için)
buyuk_bil = [c for c in nx.connected_components(G) if sum(G[u][v]["L"] for u, v in G.subgraph(c).edges) >= 30_000]
dugum = np.array([v for c in buyuk_bil for v in c])
tree = cKDTree(dugum)
print(f"  yakalama için {len(buyuk_bil)} bileşen, {len(dugum):,} düğüm")
# koridor düğümleri: il merkezlerinin OSM place=city noktaları (yoksa nüfus ağırlıklı kent merkezi)
km = pd.read_csv(CIK / "kent_merkezleri.csv")
HUB = {r.il: (r.x, r.y) for r in km.itertuples()}
sehir = pd.read_parquet(KOK / "03_VERI" / "islenmis" / "pilot_osm" / "yer_noktalari.parquet")
sehir = sehir[sehir.place == "city"].drop_duplicates("ad")
sg = gpd.GeoSeries(gpd.points_from_xy(sehir.lon, sehir.lat), crs=4326).to_crs(LCC)
for ad, x_, y_ in zip(sehir.ad.str.replace("â", "a"), sg.x, sg.y):
    if ad in HUB:
        HUB[ad] = (x_, y_)
lim = gpd.read_file(CIK / "limanlar_yuk.gpkg").to_crs(LCC)
for r in lim.itertuples():
    HUB["L:" + r.ad.split(" (")[0].split(" -")[0]] = (r.geometry.x, r.geometry.y)
KORIDOR = {
    "Y1 Kuzey ana koridor (Edirne–İstanbul–Ankara–Kars)": ["Edirne", "İstanbul", "Kocaeli", "Sakarya", "Bilecik", "Eskişehir",
                                                           "Ankara", "Kırıkkale", "Yozgat", "Sivas", "Erzincan", "Erzurum", "Kars"],
    "Y2 Ege–Ankara": ["Ankara", "Afyonkarahisar", "Uşak", "Manisa", "İzmir"],
    "Y3 Güney koridoru (Ankara–Konya–Adana–Mardin)": ["Ankara", "Konya", "Karaman", "Adana", "Osmaniye", "Gaziantep",
                                                    "Şanlıurfa", "Mardin"],
    "Y4 Karadeniz–Güneydoğu (Samsun–Sivas–Diyarbakır)": ["Samsun", "Amasya", "Sivas", "Malatya", "Elazığ", "Diyarbakır", "Batman"],
    "Y5 Orta Anadolu (Kırıkkale–Kayseri–Adana–Mersin)": ["Kırıkkale", "Kayseri", "Niğde", "Adana", "Mersin"],
    "Y6 Güney Marmara (Bandırma–Bursa–Bilecik)": ["L:Bandırma", "Bursa", "Bilecik"],
    "Y7 Ege iç (İzmir–Balıkesir–Eskişehir)": ["İzmir", "Balıkesir", "Kütahya", "Eskişehir"],
    "Y8 Güney Ege (İzmir–Denizli–Afyon)": ["İzmir", "Aydın", "Denizli", "Afyonkarahisar"],
    "Y9 Akdeniz bağlantısı (Antalya–Isparta–Afyon, Antalya–Konya)": ["Antalya", "Burdur", "Afyonkarahisar"],
    "Y9b Antalya–Konya": ["Antalya", "Konya"],
    "Y10 Doğu Karadeniz–Erzincan": ["Trabzon", "Gümüşhane", "Erzincan"],
    "Y11 Karadeniz kıyısı (Samsun–Rize)": ["Samsun", "Ordu", "Giresun", "Trabzon", "Rize"],
    "Y12 Batı Karadeniz (Filyos–Karabük–Kırıkkale)": ["L:Filyos", "Zonguldak", "Karabük", "Çankırı", "Kırıkkale"],
    "Y13 Doğu (Elazığ–Muş–Van)": ["Elazığ", "Muş", "Bitlis", "Van"],
    "Y14 İskenderun–Gaziantep–Malatya": ["L:İskenderun", "Osmaniye", "Gaziantep", "Kahramanmaraş", "Malatya"],
    "Y15 Trakya (Tekirdağ–İstanbul)": ["L:Tekirdağ", "Tekirdağ", "İstanbul"],
}


def yakala(p, esik=15000):
    d_, i_ = tree.query(p)
    return tuple(dugum[i_]) if d_ <= esik else None


seg = []
for kor, dizi in KORIDOR.items():
    for a, b in zip(dizi[:-1], dizi[1:]):
        pa, pb = HUB[a], HUB[b]
        duz = float(np.hypot(pa[0] - pb[0], pa[1] - pb[1]))
        na, nb = yakala(pa), yakala(pb)
        yol = None
        if na and nb and nx.has_path(G, na, nb):
            yol = nx.shortest_path(G, na, nb, weight="w")
            L = sum(G[u][v]["L"] for u, v in zip(yol[:-1], yol[1:]))
            if L > 2.2 * duz + 20000:
                yol = None
        if yol is None:
            neden = ("düğüm yok" if not (na and nb) else "ağ kopuk" if not nx.has_path(G, na, nb) else "dolambaçlı")
            # OSM'de kesintili görünen ama sahada var olan hat: Adana–Osmaniye kesimi OSM'de "Mersin-Adana-Gaziantep
            # yüksek standartlı demiryolu" adıyla yapımda etiketli ve parçalı [İ]. Kuş uçuşu çizilir, "yapımda" sayılır.
            durum_ = "yapim" if (a, b) in {("Adana", "Osmaniye")} else "yeni"
            print(f"  {'yeni bağlantı' if durum_ == 'yeni' else 'OSM kopukluğu (yapımda sayıldı)'} {a}–{b}: {neden}")
            seg.append((kor, a, b, durum_, duz / 1000, LineString([pa, pb])))
            continue
        # aynı durumdaki ardışık kenarları birleştir
        cur, pts = None, []
        for u, v in zip(yol[:-1], yol[1:]):
            d = G[u][v]["durum"]
            d = "konvansiyonel" if d == "baglanti" else d
            if d != cur and pts:
                ls = LineString(pts)
                seg.append((kor, a, b, cur, ls.length / 1000, ls))
                pts = [u]
            cur = d
            pts = pts or [u]
            pts.append(v)
        ls = LineString(pts)
        seg.append((kor, a, b, cur, ls.length / 1000, ls))
kor_g = gpd.GeoDataFrame(seg, columns=["koridor", "a", "b", "durum", "km", "geometry"], crs=LCC)
kor_g.to_crs(4326).to_file(CIK / "sema_koridorlar.gpkg", driver="GPKG")
kor_ozet = kor_g.pivot_table(index="koridor", columns="durum", values="km", aggfunc="sum", fill_value=0).round(0)
kor_ozet["toplam"] = kor_ozet.sum(axis=1)
kor_ozet.loc["Toplam (tekrarsız değil)"] = kor_ozet.sum()
kor_ozet.to_csv(SON / "ulusal_plan_koridorlar.csv", encoding="utf-8")
print(kor_ozet)
yeni = kor_g[kor_g.durum == "yeni"]
print("yeni bağlantılar:", [(r.a, r.b, round(r.km)) for r in yeni.itertuples()])

# =============================== C. Uydu kent ilkesi: raylı koridorda 20–70 km bandı ============================
# Yer seçimi yapılmaz. İlke: uydu kent, büyük kentin (K1–K2) merkezine 20–70 km (hızlı trenle ≤ 45 dk) uzaklıkta, koridor
# hattı üzerinde ve mevcut bir kasabanın büyütülmesiyle kurulur. Haritada bu ilkenin geçerli olduğu hat kesimleri (bant)
# gösterilir; tabloda her büyük kent için bantta ilkenin bütün koşullarını sağlayan mevcut istasyon SAYISI verilir (ad yok).
hat = kor_g[kor_g.durum.isin(["hizli", "konvansiyonel", "yapim"])]
hat_m = rasterize(((g, 1) for g in hat.geometry), out_shape=(NY, NX), transform=TR, fill=0, all_touched=True,
                  dtype="uint8").astype(bool)
hiz_m = rasterize(((g, 1) for g in hat[hat.durum == "hizli"].geometry), out_shape=(NY, NX), transform=TR, fill=0,
                  all_touched=True, dtype="uint8").astype(bool)
d_hat = ndimage.distance_transform_edt(~hat_m) * H
buyuk = k[k.kademe.isin(["K1", "K2"])].reset_index(drop=True)
mr, mc = rc(buyuk.x.values, buyuk.y.values)
merkez_m = np.zeros((NY, NX), bool)
merkez_m[mr, mc] = True
merkez_no = np.full((NY, NX), -1, dtype="int32")
merkez_no[mr, mc] = np.arange(len(buyuk))
d_merk, (my, mx) = ndimage.distance_transform_edt(~merkez_m, return_indices=True)
d_merk *= H
en_yakin_merkez = merkez_no[my, mx]
del my, mx
d_k13 = ndimage.distance_transform_edt(~np.isin(lab, k[k.kademe.isin(["K1", "K2", "K3"])].lab.values)) * H
# ≥ 3 milyonluk metropollerde hızlı tren hattı boyunca bant 110 km'ye (≈ 45 dk) uzar
uc3m = (buyuk.nufus.values >= 3e6)[en_yakin_merkez]
ust_m = np.where(uc3m & hiz_m, 110_000, 70_000)
bant = hat_m & (d_merk >= 20_000) & (d_merk <= ust_m) & (d_k13 >= 5000)
bant_merkez = np.where(bant, en_yakin_merkez, -1)
del uc3m, ust_m

ist = gpd.read_file(CIK / "istasyonlar_yolcu.gpkg").to_crs(LCC)
ist["r"], ist["c"] = rc(ist.geometry.x.values, ist.geometry.y.values)
ist = ist[(d_hat[ist.r, ist.c] <= 1500) & ~ist.ad.str.contains(
    r"Kömür|İşl\.|Maden|Fabrika|Lojistik|OSB|Liman|Sanayi|^KM\s?\d", regex=True)].copy()
# istasyon bant içinde mi? (istasyon hücresinin 1,5 km çevresinde bant hücresi)
bant_y = ndimage.binary_dilation(bant, iterations=6)
ist = ist[bant_y[ist.r, ist.c] & (d_merk[ist.r, ist.c] >= 20_000)].copy()
ist["merkez_i"] = en_yakin_merkez[ist.r, ist.c]
R = int(3000 / H)
yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
disk = ((xx ** 2 + yy ** 2) <= R ** 2).astype("float32")
el_say = ndimage.convolve(elverisli.astype("float32"), disk, mode="constant")
ova_say = ndimage.convolve(B["ova_tarim"].astype("float32"), disk, mode="constant")
kara_say = ndimage.convolve(kara.astype("float32"), disk, mode="constant")
kasaba_m = np.isin(lab, k[k.kademe.isin(["K4", "K5"])].lab.values)
d_kas = ndimage.distance_transform_edt(~kasaba_m) * H
ist["elverisli_km2"] = el_say[ist.r, ist.c] * HA
ist["ova_pay"] = 100 * ova_say[ist.r, ist.c] / np.maximum(kara_say[ist.r, ist.c], 1)
ist["kosul"] = ((ist.elverisli_km2 >= 5) & (ist.ova_pay < 50) & ~B["fay_1km"][ist.r, ist.c]
                & (d_kas[ist.r, ist.c] <= 2000) & (d_k13[ist.r, ist.c] >= 5000))
uy = []
for i, b_ in buyuk.iterrows():
    s = ist[ist.merkez_i == i]
    uy.append({"merkez": b_.ad, "il": b_.il, "kademe": b_.kademe, "nufus": round(b_.nufus),
               "bant_ust_km": 110 if b_.nufus >= 3e6 else 70,
               "bant_hat_km": round((bant_merkez == i).sum() * H / 1000),
               "bant_istasyon": len(s), "ilkeyi_saglayan_istasyon": int(s.kosul.sum()),
               "hizli_tren_duragi": int((s.kosul & s.hizli_tren).sum())})
uy = pd.DataFrame(uy).sort_values("nufus", ascending=False)
uy.to_csv(SON / "ulusal_plan_uydu_kentler.csv", index=False, encoding="utf-8")
print(f"Uydu kent bandı: {bant.sum() * H / 1000:,.0f} km hat; bantta {len(ist)} istasyon, bütün koşulları sağlayan "
      f"{int(ist.kosul.sum())}; hiç uygun istasyonu olmayan büyük kent: {int((uy.ilkeyi_saglayan_istasyon == 0).sum())}/{len(uy)}")
print(uy.to_string(index=False))

# ---- C2. Karşı mıknatıs: metropole 40–250 km uzakta, hızlı tren durağına ≤ 5 km olan mevcut K2–K4 kentleri ------------
hd = gpd.read_file(CIK / "istasyonlar_yolcu.gpkg").to_crs(LCC)
hd = hd[hd.hizli_tren]
hdt = cKDTree(np.c_[hd.geometry.x, hd.geometry.y])
km_ = []
for r in k[k.kademe.isin(["K2", "K3", "K4"])].itertuples():
    d_h, i_h = hdt.query([r.x, r.y])
    m1 = k[k.kademe == "K1"]
    d_m = np.hypot(m1.x - r.x, m1.y - r.y) / 1000
    if d_h <= 5000 and 40 <= d_m.min() <= 250:
        km_.append({"kent": r.ad, "il": r.il, "kademe": r.kademe, "nufus": round(r.nufus), "durak": hd.ad.iloc[i_h],
                    "metropol": m1.ad.iloc[int(np.argmin(d_m.values))], "metropol_km": round(float(d_m.min()), 1),
                    "x": r.x, "y": r.y})
km_ = pd.DataFrame(km_).sort_values(["metropol", "metropol_km"])
km_.to_csv(SON / "ulusal_plan_karsi_miknatis.csv", index=False, encoding="utf-8")
print("Karşı mıknatıs kentleri:", km_[["kent", "metropol", "metropol_km", "nufus", "durak"]].to_string(index=False))

# =============================== D. Sanayi ilkesi: ilkelerin birlikte sağlandığı alan ====================================
# Yer seçimi yapılmaz; aday sıralanmaz. Sanayi ilkeleri bir arada uygulanınca geriye ne kadar ve nerede alan kaldığı,
# mevcut OSB'lerin bu ilkeleri ne ölçüde sağladığı hesaplanır.
ray_ana = ray[ray.durum.isin(["hizli", "konvansiyonel", "yapim"])]
ray_m = rasterize(((g, 1) for g in ray_ana.geometry), out_shape=(NY, NX), transform=TR, fill=0, all_touched=True,
                  dtype="uint8").astype(bool)
d_ray = ndimage.distance_transform_edt(~ray_m) * H
yuk_lim = lim[lim.sinif.isin(["ana", "bolge"])]
lm = np.zeros((NY, NX), bool)
lr, lc = rc(yuk_lim.geometry.x.values, yuk_lim.geometry.y.values)
lm[lr, lc] = True
d_lim = ndimage.distance_transform_edt(~lm) * H
# tampon: K1–K3 kentlerinin kentsel hücrelerine ≥ 3 km, herhangi bir ≥ 2.000 nüfuslu kentsel kümeye ≥ 1 km
d_merkez = d_k13
d_kentsel = ndimage.distance_transform_edt(~np.isin(lab, k.lab.values)) * H
san = gpd.read_file(CIK / "sanayi_alanlari.gpkg").to_crs(LCC)
osb_m = rasterize(((g, 1) for g in san[san.osb.astype(str).isin(["True", "1"])].geometry), out_shape=(NY, NX), transform=TR,
                  fill=0, all_touched=True, dtype="uint8").astype(bool)
d_osb = ndimage.distance_transform_edt(~osb_m) * H
taban = (kara & ~mutlak & ~B["ova_tarim"] & (np.nan_to_num(egim, nan=99) <= 8) & (d_ray <= 5000)
         & (d_merkez >= 3000) & (d_kentsel >= 1000))
orta = k[k.kademe.isin(["K1", "K2", "K3"])].reset_index(drop=True)
ct = cKDTree(orta[["x", "y"]].values)
rz = pd.read_csv(SON / "ulusal_plan_ruzgar_il.csv").set_index("il")
YON = ["K", "KD", "D", "GD", "G", "GB", "B", "KB"]
f = np.array([[rz.loc[il, f"f_{y}"] if il in rz.index else np.nan for y in YON] for il in orta.il])


def ruzgar_kente(px, py):
    """Noktadan en yakın K1–K3 kentine doğru esen rüzgârın saat payı (%) ve kente uzaklık (m).
    Nokta kentten 'aci' yönünde ise o yönden gelen rüzgâr noktadan kente eser (ERA5 sekiz yön sıklığı, kent ilinin merkezi)."""
    dd, ii = ct.query(np.c_[px, py])
    aci = np.degrees(np.arctan2(px - orta.x.values[ii], py - orta.y.values[ii])) % 360
    return f[ii, ((aci + 22.5) // 45).astype(int) % 8], dd, ii


rr, cc = np.nonzero(taban)
px, py = xy(rr, cc)
f_kente, dd, ii = ruzgar_kente(px, py)
ok = (dd >= 8000) & (dd <= 40000) & (f_kente <= 10)
ilke_m = np.zeros((NY, NX), "uint8")
ilke_m[rr[ok], cc[ok]] = np.where(d_lim[rr[ok], cc[ok]] <= 50_000, 2, 1)  # 2: limana ≤ 50 km, 1: iç bölge
alab, an = ndimage.label(ilke_m > 0, structure=np.ones((3, 3)))
asay = ndimage.sum(ilke_m > 0, alab, np.arange(1, an + 1)) * HA
buyuk_parca = np.isin(alab, np.nonzero(asay >= 4)[0] + 1)
P_IL = IL[ilc]
ib = gpd.read_file(KOK / "03_VERI" / "islenmis" / "ilce_paneli.gpkg")[["il", "ibbs3_kod"]].drop_duplicates("il")
il_bolge = dict(zip(ib.il, ib.ibbs3_kod.str[:3]))
m_ = ilke_m > 0
t = pd.DataFrame({"il": P_IL[m_], "liman": ilke_m[m_] == 2, "fay5": B["fay_5km"][m_], "buyuk": buyuk_parca[m_]})
il_alan = pd.Series(P_IL[kara]).value_counts() * HA
sa = t.groupby("il").agg(ilke_alani_km2=("liman", "size"), liman_50km_pay=("liman", "mean"),
                         fay_5km_disi_pay=("fay5", lambda s: 1 - s.mean()), bitisik_4km2_pay=("buyuk", "mean"))
sa["ilke_alani_km2"] *= HA
sa[["liman_50km_pay", "fay_5km_disi_pay", "bitisik_4km2_pay"]] *= 100
sa["il_alani_pay"] = 100 * sa.ilke_alani_km2 / il_alan.reindex(sa.index)
sa["bolge"] = [il_bolge.get(v, "") for v in sa.index]
sa = sa.reindex(sorted(il_alan.index)).fillna({"ilke_alani_km2": 0, "il_alani_pay": 0})
sa["bolge"] = [il_bolge.get(v, "") for v in sa.index]
sa.loc["Türkiye"] = [m_.sum() * HA, 100 * (ilke_m[m_] == 2).mean(), 100 * (1 - B["fay_5km"][m_].mean()),
                     100 * buyuk_parca[m_].mean(), 100 * m_.sum() / kara.sum(), ""]
sa.index.name = "il"
sa.round(1).to_csv(SON / "ulusal_plan_sanayi_ilke_alani.csv", encoding="utf-8")
print(f"Sanayi ilke alanı: taban koşulu {taban.sum() * HA:,.0f} km²; rüzgâr ve uzaklıkla {m_.sum() * HA:,.0f} km² "
      f"(%{100 * m_.sum() / kara.sum():.1f}); limana ≤ 50 km {(ilke_m == 2).sum() * HA:,.0f} km²; ≥ 4 km² bitişik parça "
      f"{int((asay >= 4).sum())}; ilke alanı olmayan il: {int((sa.ilke_alani_km2 == 0).sum())}")

# ---- D2. Mevcut OSB'ler sanayi ilkelerini sağlıyor mu? (≥ 20 ha, adında OSB geçen OSM poligonları) -------------------
osb_t = pd.read_csv(SON / "ulusal_plan_sanayi_osb.csv")
osb_t = osb_t[osb_t.ha >= 20].copy()
orr, occ = rc(osb_t.x.values, osb_t.y.values)
fk, dk, _ = ruzgar_kente(osb_t.x.values, osb_t.y.values)
osb_t["p_demiryolu_5km"] = osb_t.demiryolu_km <= 5
osb_t["p_ova_disi"] = osb_t.halka_ova_pay < 25           # 2 km halkanın < %25'i ova tarım arazisi
osb_t["p_fay_1km_disi"] = ~B["fay_1km"][orr, occ]
osb_t["p_fay_5km_disi"] = ~B["fay_5km"][orr, occ]
osb_t["p_kentten_3km"] = d_k13[orr, occ] >= 3000
osb_t["p_ruzgar_alti"] = (fk <= 10) | (dk > 40000)        # kente doğru esen rüzgâr ≤ %10 ya da 40 km'de K1–K3 kent yok
osb_t["p_hepsi"] = osb_t[["p_demiryolu_5km", "p_ova_disi", "p_fay_1km_disi", "p_kentten_3km", "p_ruzgar_alti"]].all(axis=1)
osb_t["ruzgar_kente_pay"] = fk.round(1)
osb_t.round(2).to_csv(SON / "ulusal_plan_sanayi_osb_ilke.csv", index=False, encoding="utf-8")
pk = [c for c in osb_t.columns if c.startswith("p_")]
oz_ = pd.DataFrame({"osb_sayisi_pay": osb_t[pk].mean() * 100,
                    "osb_alani_pay": [100 * osb_t.ha[osb_t[c]].sum() / osb_t.ha.sum() for c in pk]}).round(1)
oz_.loc["n_osb"] = [len(osb_t), osb_t.ha.sum()]
oz_.to_csv(SON / "ulusal_plan_sanayi_osb_ilke_ozet.csv", encoding="utf-8")
print("Mevcut OSB'lerin ilke uyumu (%):")
print(oz_)

# ---- ızgara çıktısı: bant 1 = uydu kent bandı (raylı hat kesimi), bant 2 = sanayi ilke alanı (1 iç bölge, 2 liman ≤ 50 km)
with rasterio.open(CIK / "izgara_sema.tif", "w", driver="GTiff", width=NX, height=NY, count=2, dtype="uint8", crs=LCC,
                   transform=TR, compress="deflate", predictor=2, tiled=True) as o:
    o.write(bant.astype("uint8"), 1)
    o.write(ilke_m, 2)
    o.set_band_description(1, "uydu_kent_bandi")
    o.set_band_description(2, "sanayi_ilke_alani")
del d_merk, d_kas, el_say, ova_say, kara_say

# =============================== E. Enerji: mekânsal dağılım ve koridorlar ===================================
hatlar = gpd.read_file(CIK / "iletim_hatlari.gpkg").to_crs(LCC)
hatlar["km"] = hatlar.length / 1000
h380 = hatlar[hatlar.gerilim_v >= 380000]
seg2 = []
for g in h380.geometry.segmentize(250):
    a = np.asarray(g.coords)
    m = (a[1:] + a[:-1]) / 2
    seg2.append(np.c_[m, np.hypot(*(a[1:] - a[:-1]).T)])
seg2 = np.vstack(seg2)
r2, c2 = rc(seg2[:, 0], seg2[:, 1])
yol = gpd.read_file(CIK / "yollar.gpkg").to_crs(LCC)
yol_m = rasterize(((g, 1) for g in yol[yol.highway.isin(["motorway", "trunk"])].geometry), out_shape=(NY, NX), transform=TR,
                  fill=0, all_touched=True, dtype="uint8").astype(bool)
d_yol = ndimage.distance_transform_edt(~yol_m) * H
Lt = seg2[:, 2].sum()
en = {"380_kV_ve_ustu_km": Lt / 1000, "154_kV_km": hatlar[hatlar.gerilim_v < 380000].km.sum(),
      "380kV_demiryolu_veya_anayol_2km_icinde_pay": 100 * seg2[(d_ray[r2, c2] <= 2000) | (d_yol[r2, c2] <= 2000), 2].sum() / Lt,
      "380kV_orman_pay": 100 * seg2[B["orman"][r2, c2], 2].sum() / Lt,
      "380kV_fay_1km_pay": 100 * seg2[B["fay_1km"][r2, c2], 2].sum() / Lt,
      "380kV_korunan_pay": 100 * seg2[B["korunan"][r2, c2], 2].sum() / Lt}
h380_m = rasterize(((g, 1) for g in h380.geometry), out_shape=(NY, NX), transform=TR, fill=0, all_touched=True,
                   dtype="uint8").astype(bool)
d380 = ndimage.distance_transform_edt(~h380_m) * H
osb = san[san.osb.astype(str).isin(["True", "1"])]
oc = osb.geometry.representative_point()
orr, occ = rc(oc.x.values, oc.y.values)
en["osb_380kV_10km_pay"] = 100 * (d380[orr, occ] <= 10000).mean()
en["nufus_380kV_1km_pay"] = 100 * nuf[kara & (d380 <= 1000)].sum() / P
# santral ve üreteçler: İBBS-1 bölgesine göre sayı (OSM kaydı; kapasite etiketleri eksik)
ibbs = gpd.read_file(KOK / "03_VERI" / "islenmis" / "ilce_paneli.gpkg")[["il", "ibbs3_kod"]].drop_duplicates("il")
il_bolge = dict(zip(ibbs.il, ibbs.ibbs3_kod.str[:3]))
sant = gpd.read_file(CIK / "santraller.gpkg").to_crs(LCC)
uret = gpd.read_file(CIK / "uretecler.gpkg").to_crs(LCC)
satir = []
for ad, g in [("santral", sant), ("uretec", uret)]:
    r_, c_ = rc(g.geometry.x.values, g.geometry.y.values)
    t = pd.DataFrame({"tur": ad, "kaynak": g.kaynak.replace("", "bilinmiyor").str.split(";").str[0].values,
                      "bolge": [il_bolge.get(v, "dışarıda") for v in IL[ilc[r_, c_]]]})
    satir.append(t)
st = pd.concat(satir)
st_tab = st.pivot_table(index=["tur", "kaynak"], columns="bolge", aggfunc="size", fill_value=0)
st_tab["toplam"] = st_tab.sum(axis=1)
st_tab = st_tab.sort_values("toplam", ascending=False)
pd.concat([pd.DataFrame([en]).T.rename(columns={0: "deger"}).round(1)]).to_csv(SON / "ulusal_plan_enerji.csv",
                                                                                encoding="utf-8")
st_tab.to_csv(SON / "ulusal_plan_enerji_kaynak_bolge.csv", encoding="utf-8")
print(pd.Series(en).round(1))
print(st_tab.head(12))
