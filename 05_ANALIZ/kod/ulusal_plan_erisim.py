"""
Faz 4 · Ulusal mekânsal çerçeve — erişilebilirlik, sanayi yakınlığı ve otoyol-kent ilişkisi
=========================================================================================
Girdi : 03_VERI/islenmis/ulusal_altyapi/ (ulusal_altyapi_osm.py, ulusal_plan_izgara.py, ulusal_plan_katmanlar.py)
Çıktı : 05_ANALIZ/sonuclar/ulusal_plan_erisim_il.csv     81 il + Türkiye: istasyon, havalimanı, liman erişimi (nüfus payı)
        05_ANALIZ/sonuclar/ulusal_plan_erisim_ozet.csv   ulusal özet ve duyarlılık (kuş uçuşu ile süre karşılaştırması)
        05_ANALIZ/sonuclar/ulusal_plan_sanayi_il.csv     il bazında sanayi alanı, yakın nüfus, PM2.5 farkı
        05_ANALIZ/sonuclar/ulusal_plan_sanayi_osb.csv    OSB poligonları: eğim, 2 km halkada tarım, yakın nüfus, PM2.5
        05_ANALIZ/sonuclar/ulusal_plan_otoyol_kent.csv   il bazında yoğun kent dokusu içinden geçen otoyol ve devlet yolu
        03_VERI/islenmis/ulusal_altyapi/izgara_erisim.tif  (uint16) 1 istasyon km×10 · 2 hızlı tren istasyonu km×10 ·
                                                          3 havalimanı dakika · 4 yük limanı km×10 · 5 sanayi alanı km×10
Yöntem:
  Mesafe   : 250 m ızgarada Öklid mesafe dönüşümü (kuş uçuşu).
  Süre     : 1 km ızgarada en kısa yol (Dijkstra, 8 komşu). Hücre hızı, hücreden geçen en hızlı yol sınıfı [V]:
             otoyol 100 · devlet yolu (trunk) 80 · il yolu (primary) 60 · bağlantı kolu 50 · diğer 30 km/saat.
             Feribot ve köprüsüz deniz geçişi yok. Havalimanında bekleme süresi eklenmedi.
  Nüfus    : TÜİK ADNKS 2025 ilçe toplamları, 250 m hücrelere GHSL 2020 dağılımıyla (ulusal_plan_nufus.py).
  Yoğun kent: nüfusu ≥ 1.500 kişi/km² olan 250 m hücreler (DEGURBA kent merkezi eşiği).
"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
CIK = KOK / "03_VERI" / "islenmis" / "ulusal_altyapi"
SON = KOK / "05_ANALIZ" / "sonuclar"
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m +no_defs"
H = 250.0


def oku(ad, bant=1):
    with rasterio.open(CIK / ad) as d:
        return d.read(bant), d.transform


nuf, TR = oku("izgara_nufus.tif")
NY, NX = nuf.shape
ilc, _ = oku("izgara_ilce.tif")
pm, _ = oku("izgara_pm25.tif")
tarim, _ = oku("izgara_ortu.tif", 2)
egim, _ = oku("izgara_egim.tif")
egim = np.where(egim == 65535, np.nan, egim / 10.0).astype("float32")  # % 
anahtar = pd.read_csv(CIK / "izgara_ilce_anahtar.csv", dtype={"ilce_kod": str})
il_ad = np.array([""] + anahtar.il.tolist(), dtype=object)
IL = il_ad[ilc]
kara = ilc > 0
yogun = nuf >= 1500 * 0.0625


def hucre(gdf):
    g = gdf.to_crs(LCC)
    c = ((g.geometry.x - TR.c) // H).astype(int).values
    r = ((TR.f - g.geometry.y) // H).astype(int).values
    ok = (c >= 0) & (c < NX) & (r >= 0) & (r < NY)
    return r[ok], c[ok]


def mesafe_nokta(gdf):
    m = np.ones((NY, NX), dtype=bool)
    r, c = hucre(gdf)
    m[r, c] = False
    return (ndimage.distance_transform_edt(m) * H).astype("float32")


def mesafe_alan(maske):
    return (ndimage.distance_transform_edt(~maske) * H).astype("float32")


ist = gpd.read_file(CIK / "istasyonlar_yolcu.gpkg")
hav = gpd.read_file(CIK / "havalimanlari_yolcu.gpkg")
lim = gpd.read_file(CIK / "limanlar_yuk.gpkg")
yuk_lim = lim[lim.sinif.isin(["ana", "bolge"])]

d_ist = mesafe_nokta(ist[~ist.hat_yapimda])
d_ist_g = mesafe_nokta(ist)  # duyarlılık: yapımdaki hatlar açıldığında
d_hiz = mesafe_nokta(ist[ist.hizli_tren])
d_lim = mesafe_nokta(yuk_lim)
d_lim_ray = mesafe_nokta(yuk_lim[yuk_lim.demiryolu_bagli])
d_hav = mesafe_nokta(hav)
print("mesafeler hazır")

# ---------- Havalimanı süresi (1 km, Dijkstra) --------------------------------------------------------------------
K = 4
ny, nx = NY // K, NX // K
yol = gpd.read_file(CIK / "yollar.gpkg").to_crs(LCC)
HIZ = {"motorway": 100, "trunk": 80, "primary": 60, "motorway_link": 50, "trunk_link": 50, "primary_link": 50}
yol = yol[yol.highway.isin(HIZ)].copy()
yol["hiz"] = yol.highway.map(HIZ)
yol = yol.sort_values("hiz")  # sonra çizilen (daha hızlı) üstte kalır
tr1 = rasterio.Affine(H * K, 0, TR.c, 0, -H * K, TR.f)
hiz1 = rasterize(zip(yol.geometry, yol.hiz), out_shape=(ny, nx), transform=tr1, fill=0, all_touched=True, dtype="uint8")
kara1 = kara[:ny * K, :nx * K].reshape(ny, K, nx, K).any(axis=(1, 3))
gecilir = kara1 | (hiz1 > 0)
hiz1 = np.where(hiz1 > 0, hiz1, 30).astype("float64")
maliyet = np.where(gecilir, 60.0 / hiz1, np.inf)  # dakika / km
idx = np.arange(ny * nx).reshape(ny, nx)
sat, sut, agr = [], [], []
for dy, dx in [(0, 1), (1, 0), (1, 1), (1, -1)]:
    xs, xb = (slice(0, nx - dx), slice(dx, nx)) if dx >= 0 else (slice(-dx, nx), slice(0, nx + dx))
    a = idx[0:ny - dy, xs].ravel()
    b = idx[dy:ny, xb].ravel()
    w = (maliyet.ravel()[a] + maliyet.ravel()[b]) / 2 * (np.sqrt(2) if dx and dy else 1.0) * (H * K / 1000)
    ok = np.isfinite(w)
    sat += [a[ok], b[ok]]
    sut += [b[ok], a[ok]]
    agr += [w[ok], w[ok]]
G = coo_matrix((np.concatenate(agr), (np.concatenate(sat), np.concatenate(sut))), shape=(ny * nx, ny * nx)).tocsr()
hg = hav.to_crs(LCC)
kaynak = np.unique(((tr1.f - hg.geometry.y) // (H * K)).astype(int) * nx + ((hg.geometry.x - tr1.c) // (H * K)).astype(int))
sure1 = dijkstra(G, directed=False, indices=kaynak, min_only=True).reshape(ny, nx)
t_hav = np.full((NY, NX), np.inf, dtype="float32")
t_hav[:ny * K, :nx * K] = np.repeat(np.repeat(sure1, K, axis=0), K, axis=1)
print("havalimanı süresi hazır; Türkiye nüfus ağırlıklı ortalama:",
      round(float(np.average(np.minimum(t_hav[kara], 600), weights=nuf[kara])), 1), "dk")

# sanayi alanları
san = gpd.read_file(CIK / "sanayi_alanlari.gpkg").to_crs(LCC)
san["ha"] = san.area / 1e4
san_r = rasterize(((g, 1) for g in san.geometry), out_shape=(NY, NX), transform=TR, fill=0, all_touched=True,
                  dtype="uint8").astype(bool)
d_san = mesafe_alan(san_r)

with rasterio.open(CIK / "izgara_erisim.tif", "w", driver="GTiff", width=NX, height=NY, count=5, dtype="uint16", crs=LCC,
                   transform=TR, compress="deflate", predictor=2, tiled=True, nodata=65535) as o:
    for i, (a, olcek) in enumerate([(d_ist, 0.01), (d_hiz, 0.01), (t_hav, 1), (d_lim, 0.01), (d_san, 0.01)], 1):
        v = np.where(np.isfinite(a), np.round(a * olcek), 65535)
        o.write(np.clip(v, 0, 65535).astype("uint16"), i)
    for i, ad in enumerate(["istasyon_km10", "hizli_tren_km10", "havalimani_dk", "yuk_limani_km10", "sanayi_km10"], 1):
        o.set_band_description(i, ad)

# ---------- İl tablosu ------------------------------------------------------------------------------------------
w = nuf[kara]
df = pd.DataFrame({"il": IL[kara], "p": w, "ist": d_ist[kara], "ist_g": d_ist_g[kara], "hiz": d_hiz[kara], "hav": t_hav[kara],
                   "hav_km": d_hav[kara], "lim": d_lim[kara], "lim_ray": d_lim_ray[kara], "san": d_san[kara],
                   "pm": pm[kara], "yog": yogun[kara]})


def ozet(t):
    p = t.p.sum()
    f = lambda m: 100 * t.p[m].sum() / p
    return pd.Series({
        "nufus_2025": round(p), "ist_10km": f(t.ist <= 10_000), "ist_30km": f(t.ist <= 30_000),
        "ist_10km_yapim_dahil": f(t.ist_g <= 10_000), "ist_30km_yapim_dahil": f(t.ist_g <= 30_000),
        "hizli_tren_30km": f(t.hiz <= 30_000), "hizli_tren_60km": f(t.hiz <= 60_000),
        "hav_60dk": f(t.hav <= 60), "hav_120dk": f(t.hav <= 120), "hav_50km_kus": f(t.hav_km <= 50_000),
        "hav_100km_kus": f(t.hav_km <= 100_000), "liman_50km": f(t.lim <= 50_000), "liman_100km": f(t.lim <= 100_000),
        "liman_ray_100km": f(t.lim_ray <= 100_000),
        "ort_ist_km": np.average(t.ist, weights=t.p) / 1000, "ort_hav_dk": np.average(np.minimum(t.hav, 900), weights=t.p),
        "ort_liman_km": np.average(t.lim, weights=t.p) / 1000})


il_tab = df.groupby("il").apply(ozet, include_groups=False)
tr_satir = ozet(df).to_frame("Türkiye").T
il_tab = pd.concat([il_tab.sort_index(), tr_satir]).round(1)
il_tab.index.name = "il"
il_tab.to_csv(SON / "ulusal_plan_erisim_il.csv", encoding="utf-8")
print(tr_satir.round(1).T)

# kentsel-kırsal ayrımı ve en zayıf iller
oz = []
for ad, m in [("Türkiye", df.p > 0), ("yoğun kent (≥1.500/km²)", df.yog), ("yoğun kent dışı", ~df.yog)]:
    s = ozet(df[m])
    oz.append(s.rename(ad))
oz = pd.DataFrame(oz).round(1)
oz.to_csv(SON / "ulusal_plan_erisim_ozet.csv", encoding="utf-8")
print(oz.T)
print("istasyona 30 km'de nüfusun %25'inden azı olan iller:",
      il_tab[il_tab.ist_30km < 25].index.tolist())
print("havalimanına 120 dk'da nüfusun %90'ından azı olan iller:", il_tab[il_tab.hav_120dk < 90].index.tolist())

# ---------- Sanayi: il tablosu ve PM2.5 -----------------------------------------------------------------------------
san_c = san.geometry.representative_point()
sr = ((TR.f - san_c.y) // H).astype(int).clip(0, NY - 1)
sc = ((san_c.x - TR.c) // H).astype(int).clip(0, NX - 1)
san["il"] = IL[sr, sc]
dfp = df[np.isfinite(df.pm)].copy()
dfp["yakin3"] = dfp.san <= 3000
dfp["yog_sinif"] = pd.cut(dfp.p / 0.0625, [-1, 300, 1500, 1e9], labels=["kir", "kentsel_kume", "kent_merkezi"])
# il × yoğunluk sınıfı içinde, 3 km içinde oturanlar ile dışındakilerin PM2.5 farkı (nüfus ağırlıklı)
fark = []
for (il, ys), t in dfp.groupby(["il", "yog_sinif"], observed=True):
    a, b = t[t.yakin3], t[~t.yakin3]
    if a.p.sum() > 1000 and b.p.sum() > 1000:
        fark.append((il, ys, np.average(a.pm, weights=a.p) - np.average(b.pm, weights=b.p), a.p.sum()))
fark = pd.DataFrame(fark, columns=["il", "yog", "fark", "p"])
fark_ulusal = np.average(fark.fark, weights=fark.p)
fark_il = dfp.groupby("il").apply(
    lambda t: (np.average(t.pm[t.yakin3], weights=t.p[t.yakin3]) - np.average(t.pm[~t.yakin3], weights=t.p[~t.yakin3]))
    if t.p[t.yakin3].sum() > 1000 and t.p[~t.yakin3].sum() > 1000 else np.nan, include_groups=False)
san_il = pd.DataFrame({
    "sanayi_ha": san.groupby("il").ha.sum(), "sanayi_poligon": san.groupby("il").size(),
    "osb_poligon": san[san.osb].groupby("il").size(), "osb_ha": san[san.osb].groupby("il").ha.sum(),
    "nufus_1km_pay": df.groupby("il").apply(lambda t: 100 * t.p[t.san <= 1000].sum() / t.p.sum(), include_groups=False),
    "nufus_3km_pay": df.groupby("il").apply(lambda t: 100 * t.p[t.san <= 3000].sum() / t.p.sum(), include_groups=False),
    "pm25_fark_3km_il_ici": fark_il}).fillna({"osb_poligon": 0, "osb_ha": 0}).round(2)
san_il.index.name = "il"
san_il.loc["Türkiye"] = [san.ha.sum(), len(san), int(san.osb.sum()), san[san.osb].ha.sum(),
                         100 * df.p[df.san <= 1000].sum() / df.p.sum(), 100 * df.p[df.san <= 3000].sum() / df.p.sum(),
                         fark_ulusal]
san_il.round(2).to_csv(SON / "ulusal_plan_sanayi_il.csv", encoding="utf-8")
pm_grup = []
for ad, t in [("kır (< 300/km²)", dfp[dfp.yog_sinif == "kir"]),
              ("kentsel küme (300–1.500)", dfp[dfp.yog_sinif == "kentsel_kume"]),
              ("kent merkezi (≥ 1.500)", dfp[dfp.yog_sinif == "kent_merkezi"]), ("Türkiye", dfp)]:
    a, b = t[t.yakin3], t[~t.yakin3]
    ys = {"kır (< 300/km²)": "kir", "kentsel küme (300–1.500)": "kentsel_kume", "kent merkezi (≥ 1.500)": "kent_merkezi"}
    ff = fark[fark.yog == ys[ad]] if ad in ys else fark
    pm_grup.append({"grup": ad, "yakin": np.average(a.pm, weights=a.p), "uzak": np.average(b.pm, weights=b.p),
                    "yakin_nufus": a.p.sum(), "uzak_nufus": b.p.sum(),
                    "il_ici_fark": np.average(ff.fark, weights=ff.p), "il_sayisi": ff.il.nunique()})
pm_yakin = np.average(dfp.pm[dfp.yakin3], weights=dfp.p[dfp.yakin3])
pm_uzak = np.average(dfp.pm[~dfp.yakin3], weights=dfp.p[~dfp.yakin3])
d_osb_t = mesafe_alan(rasterize(((g, 1) for g in san[san.osb].geometry), out_shape=(NY, NX), transform=TR, fill=0,
                                 all_touched=True, dtype="uint8").astype(bool))[kara]
# Aynı karşılaştırma yalnız OSB'ler için: OSB'ye ≤ 3 km oturanlar ile > 3 km oturanlar (il × yoğunluk sınıfı içinde)
dfp["osb3"] = d_osb_t[np.isfinite(df.pm.values)] <= 3000
fo = []
for (il_, ys), t in dfp.groupby(["il", "yog_sinif"], observed=True):
    a, b = t[t.osb3], t[~t.osb3]
    if a.p.sum() > 1000 and b.p.sum() > 1000:
        fo.append((il_, ys, np.average(a.pm, weights=a.p) - np.average(b.pm, weights=b.p), a.p.sum()))
fo = pd.DataFrame(fo, columns=["il", "yog", "fark", "p"])
for ad, ys in [("kır (< 300/km²)", "kir"), ("kentsel küme (300–1.500)", "kentsel_kume"),
               ("kent merkezi (≥ 1.500)", "kent_merkezi"), ("Türkiye", None)]:
    t = dfp if ys is None else dfp[dfp.yog_sinif == ys]
    ff = fo if ys is None else fo[fo.yog == ys]
    a, b = t[t.osb3], t[~t.osb3]
    pm_grup.append({"grup": ad, "yakin": np.average(a.pm, weights=a.p), "uzak": np.average(b.pm, weights=b.p),
                    "yakin_nufus": a.p.sum(), "uzak_nufus": b.p.sum(),
                    "il_ici_fark": np.average(ff.fark, weights=ff.p) if len(ff) else np.nan, "il_sayisi": ff.il.nunique()})
pmt = pd.DataFrame(pm_grup)
pmt.insert(0, "olcu", ["sanayi alanı (OSM landuse=industrial) ≤ 3 km"] * 4 + ["OSB ≤ 3 km"] * 4)
pmt.round(2).to_csv(SON / "ulusal_plan_sanayi_pm25.csv", index=False, encoding="utf-8")
print(pmt.round(2).to_string(index=False))
osb_yakin = {"nufus_osb_1km_pay": 100 * w[d_osb_t <= 1000].sum() / w.sum(),
             "nufus_osb_3km_pay": 100 * w[d_osb_t <= 3000].sum() / w.sum()}
pd.Series(osb_yakin).round(2).to_csv(SON / "ulusal_plan_sanayi_osb_yakinlik.csv", header=["deger"], encoding="utf-8")
print("OSB yakınlığı:", {k: round(v, 1) for k, v in osb_yakin.items()})
print(f"Sanayi: {len(san):,} poligon, {san.ha.sum():,.0f} ha; OSB adlı {int(san.osb.sum())} poligon, "
      f"{san[san.osb].ha.sum():,.0f} ha")
print(f"  nüfusun %{san_il.loc['Türkiye', 'nufus_1km_pay']:.1f}'i 1 km, %{san_il.loc['Türkiye', 'nufus_3km_pay']:.1f}'i "
      f"3 km içinde; PM2.5 yakın {pm_yakin:.1f} / uzak {pm_uzak:.1f}; il × yoğunluk içi fark {fark_ulusal:+.2f} µg/m³")

# ---------- OSB poligonları ---------------------------------------------------------------------------------------
osb = san[san.osb].reset_index(drop=True)
osb["sira"] = np.arange(1, len(osb) + 1)
osb_r = rasterize(zip(osb.geometry, osb.sira), out_shape=(NY, NX), transform=TR, fill=0, all_touched=True, dtype="int32")
d_osb, (iy, ix) = ndimage.distance_transform_edt(osb_r == 0, return_indices=True)
d_osb *= H
en_yakin_osb = osb_r[iy, ix]
del iy, ix
halka = (d_osb > 0) & (d_osb <= 2000)
ova = (tarim >= 50) & (egim < 5)
lab = en_yakin_osb[halka]
n = len(osb) + 1
cnt = np.bincount(lab, minlength=n)
osb["halka_tarim_pay"] = (np.bincount(lab, tarim[halka].astype(float) * (tarim[halka] <= 100), n) / np.maximum(cnt, 1))[1:]
osb["halka_ova_pay"] = (100 * np.bincount(lab, ova[halka].astype(float), n) / np.maximum(cnt, 1))[1:]
osb["nufus_2km"] = np.bincount(en_yakin_osb[d_osb <= 2000], nuf[d_osb <= 2000], n)[1:]
icerde = osb_r > 0
osb["egim_ort"] = (np.bincount(osb_r[icerde], np.nan_to_num(egim[icerde]), n) / np.maximum(np.bincount(osb_r[icerde], minlength=n), 1))[1:]
osb["pm25"] = (np.bincount(osb_r[icerde], np.nan_to_num(pm[icerde]), n) / np.maximum(np.bincount(osb_r[icerde], minlength=n), 1))[1:]
cc = osb.geometry.representative_point()
osb["ray_km"] = cc.apply(lambda p: d_ist[int((TR.f - p.y) // H), int((p.x - TR.c) // H)] / 1000)  # istasyon (yakın değer)
ray = gpd.read_file(CIK / "demiryollari.gpkg")
ray = ray[ray.railway.isin(["rail"]) & ~ray.service.isin(["yard", "siding", "spur", "crossover"])].to_crs(LCC)
ray_m = rasterize(((g, 1) for g in ray.geometry), out_shape=(NY, NX), transform=TR, fill=0, all_touched=True,
                  dtype="uint8").astype(bool)
d_ray = mesafe_alan(ray_m)
osb["demiryolu_km"] = cc.apply(lambda p: d_ray[int((TR.f - p.y) // H), int((p.x - TR.c) // H)] / 1000)
osb["liman_km"] = cc.apply(lambda p: d_lim[int((TR.f - p.y) // H), int((p.x - TR.c) // H)] / 1000)
osb["x"], osb["y"] = cc.x.round(0), cc.y.round(0)
osb[["ad", "il", "ha", "egim_ort", "halka_tarim_pay", "halka_ova_pay", "nufus_2km", "pm25", "demiryolu_km",
     "liman_km", "x", "y"]].round(2).sort_values("ha", ascending=False).to_csv(SON / "ulusal_plan_sanayi_osb.csv", index=False,
                                                                     encoding="utf-8")
o = osb[osb.ha >= 20]
print(f"OSB (≥20 ha, n={len(o)}): ort. eğim %{o.egim_ort.median():.1f} (medyan); 2 km halkada tarım %{o.halka_tarim_pay.median():.0f}"
      f" (medyan); ova tarım %{o.halka_ova_pay.median():.0f}; 2 km içinde nüfus medyanı {o.nufus_2km.median():,.0f}; "
      f"demiryoluna ≤2 km: %{100 * (o.demiryolu_km <= 2).mean():.0f}; ≤10 km: %{100 * (o.demiryolu_km <= 10).mean():.0f}")
tr_tarim = np.nanmean(np.where(kara & (tarim <= 100), tarim, np.nan))
tr_ova = 100 * ova[kara].mean()
print(f"  karşılaştırma: Türkiye karasında tarım payı %{tr_tarim:.0f}, ova tarım %{tr_ova:.1f}")

# ---------- Otoyol ve devlet yolu yoğun kent içinde ------------------------------------------------------------------
yol2 = gpd.read_file(CIK / "yollar.gpkg").to_crs(LCC)
yol2 = yol2[yol2.highway.isin(["motorway", "trunk"])].copy()
# segment uzunluğu: ardışık köşeler arası
seg = []
for _, g in yol2.geometry.segmentize(50).items():
    xy = np.asarray(g.coords)
    m = (xy[1:] + xy[:-1]) / 2
    seg.append(np.c_[m, np.hypot(*(xy[1:] - xy[:-1]).T)])
hw = np.repeat(yol2.highway.values, [len(s) for s in seg])
seg = np.vstack(seg)
r = ((TR.f - seg[:, 1]) // H).astype(int).clip(0, NY - 1)
c = ((seg[:, 0] - TR.c) // H).astype(int).clip(0, NX - 1)
ok = kara[r, c]
okt = pd.DataFrame({"il": IL[r, c], "hw": hw, "km": seg[:, 2] / 1000, "yogun": yogun[r, c]})[ok]
okt_il = okt.pivot_table(index="il", columns=["hw", "yogun"], values="km", aggfunc="sum", fill_value=0)
okt_il.columns = [f"{a}_{'yogun_kent' if b else 'diger'}_km" for a, b in okt_il.columns]
yol_m = rasterize(((g, 1) for g in yol2.geometry), out_shape=(NY, NX), transform=TR, fill=0, all_touched=True,
                  dtype="uint8").astype(bool)
d_yol = mesafe_alan(yol_m)
okt_il["nufus_500m_pay"] = df.assign(dy=d_yol[kara]).groupby("il").apply(
    lambda t: 100 * t.p[t.dy <= 500].sum() / t.p.sum(), include_groups=False)
okt_il.loc["Türkiye"] = okt_il.sum()
okt_il.loc["Türkiye", "nufus_500m_pay"] = 100 * w[d_yol[kara] <= 500].sum() / w.sum()
okt_il.round(1).to_csv(SON / "ulusal_plan_otoyol_kent.csv", encoding="utf-8")
t = okt_il.loc["Türkiye"]
print(f"Otoyol (OSM yön çizgileri): toplam {t.filter(like='motorway').sum():,.0f} km, yoğun kent içinde "
      f"{t.get('motorway_yogun_kent_km', 0):,.0f} km; devlet yolu yoğun kentte {t.get('trunk_yogun_kent_km', 0):,.0f} km; "
      f"nüfusun %{t.nufus_500m_pay:.1f}'i otoyol/devlet yoluna 500 m içinde")
