"""
FUE geçerlilik sınaması — 973 ilçede "FUE-lite" ve sonuç göstergeleri (il içi)
============================================================================
Mahalle düzeyinde eğitim ve gelir verisi olmadığı için endeksin geçerliliği (kavramsal çerçeve §4.3, adım 5) ilçe
düzeyinde sınanır: mahalle FUE'sinin göstergeleri Türkiye geneli için kuş uçuşu mesafeyle yeniden hesaplanır,
aynı il içinde, kadın eğitimi ve göç sabitken ölümlülük, doğurganlık ve hane göstergeleriyle ilişkisine bakılır.

Girdi : 03_VERI/ham/ghsl/tif/GHS_POP_* (2020, 100 m), 03_VERI/ham/sinirlar/geoBoundaries-TUR-ADM2_simplified.geojson
        03_VERI/islenmis/pilot_osm/donati_noktalari.parquet, ana_yollar.parquet (osm_pilot_mahalle.py)
        03_VERI/islenmis/ilce_paneli_genis.csv (Faz 2: sonuçlar, kontroller, GHSL, yeşil erişim, kavşak)
        03_VERI/islenmis/ilce_uydu.csv (uydu_ulusal.py; varsa FUE v0.2 sütunları eklenir)
Çıktı : 03_VERI/islenmis/ilce_fue_lite.csv, 05_ANALIZ/sonuclar/fue_ilce_gecerlilik.csv, fue_ilce_cevre_kontrol.csv

Mesafe eşikleri: yaya ağı eşiklerinin kuş uçuşu karşılığı (ağ ≈ 1,25 × kuş uçuşu):
  okul 400 m (ağ 500), cami 400, oyun 320 (ağ 400), buluşma 320, durak 320, raylı 640 (ağ 800),
  15 dk temel ihtiyaç 960 m (ağ 1.200); dükkân 150 m ve ana yol 100 m mahalle FUE'si ile aynı.
"""
import glob
import warnings
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
from rasterio.features import rasterize
from rasterio.windows import Window, transform as win_transform
from scipy.spatial import cKDTree

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
pd.set_option("display.width", 220)
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
PO = IS / "pilot_osm"
TIF = KOK / "03_VERI" / "ham" / "ghsl" / "tif"
SON = KOK / "05_ANALIZ" / "sonuclar"
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m"
bas = time.time()

# --- 1. nüfuslu hücreler ve ilçe kimliği (ghsl_ilce.py ile aynı sıra: gid = geoBoundaries satır no + 1) -----------
ilce = gpd.read_file(KOK / "03_VERI" / "ham" / "sinirlar" / "geoBoundaries-TUR-ADM2_simplified.geojson")
ilce["gid"] = np.arange(1, len(ilce) + 1)
ilce54 = ilce.to_crs("ESRI:54009")
X, Y, P, GID = [], [], [], []
for pf in sorted(glob.glob(str(TIF / "GHS_POP_*" / "*.tif"))):
    with rasterio.open(pf) as rp:
        alt = ilce54.cx[rp.bounds.left:rp.bounds.right, rp.bounds.bottom:rp.bounds.top]
        if alt.empty:
            continue
        W = 2500
        for r0 in range(0, rp.height, W):
            for c0 in range(0, rp.width, W):
                win = Window(c0, r0, min(W, rp.width - c0), min(W, rp.height - r0))
                tr = win_transform(win, rp.transform)
                b = rasterio.windows.bounds(win, rp.transform)
                a2 = alt.cx[b[0]:b[2], b[1]:b[3]]
                if a2.empty:
                    continue
                gid = rasterize(zip(a2.geometry, a2.gid), out_shape=(win.height, win.width), transform=tr, fill=0, dtype="int32")
                p = rp.read(1, window=win)
                r, c = np.nonzero((gid > 0) & (p > 0))
                X.append(tr.c + (c + 0.5) * 100)
                Y.append(tr.f - (r + 0.5) * 100)
                P.append(p[r, c].astype("float64"))
                GID.append(gid[r, c])
X, Y, P, GID = map(np.concatenate, (X, Y, P, GID))
lx, ly = Transformer.from_crs("ESRI:54009", LCC, always_xy=True).transform(X, Y)
H = np.c_[lx, ly]
print(f"nüfuslu hücre: {len(P):,} · toplam GHS-POP {P.sum():,.0f} · {time.time() - bas:.0f} sn")

# --- 2. donatılara kuş uçuşu mesafe --------------------------------------------------------------------------------
don = pd.read_parquet(PO / "donati_noktalari.parquet")
dx, dy = Transformer.from_crs(4326, LCC, always_xy=True).transform(don.lon.values, don.lat.values)
don["x"], don["y"] = dx, dy
LISE = re.compile(r"L[İI]SE|[ÜU]N[İI]VERS|FAK[ÜU]LTE|Y[ÜU]KSEKOKUL|MESLEK Y|HALK E[ĞG]|S[ÜU]R[ÜU]C[ÜU]|KURS|ET[ÜU]T|"
                  r"DERSHANE|ENST[İI]T[ÜU]|AKADEM|MYO|REHBERL|B[İI]LSEM|B[İI]L[İI]M VE SANAT|KONSERVATUVAR", re.I)
BUL = {"cafe", "library", "community_centre", "arts_centre", "social_centre", "townhall", "marketplace", ""}
KAT = {
    "okul": don[(don.tur == "okul") & ~don.ad.str.upper().str.contains(LISE)],
    "saglik": don[don.tur.isin(["saglik", "eczane"])],
    "market": don[don.tur == "market"],
    "cami": don[don.tur == "cami"],
    "oyun": don[don.tur == "oyun"],
    "bulusma": don[(don.tur == "bulusma") & don.etiket.isin(BUL)],
    "durak": don[don.tur == "durak"],
    "rayli": don[don.tur == "rayli"],
    "dukkan": don[don.tur.isin(["dukkan", "bulusma"]) & (don.etiket != "")],
}
D = {k: cKDTree(v[["x", "y"]].values).query(H, workers=-1)[0] for k, v in KAT.items()}
ay = pd.read_parquet(PO / "ana_yollar.parquet")
g = shapely.from_wkb(ay.wkb.values)
g = shapely.transform(g, lambda c: np.c_[Transformer.from_crs(4326, LCC, always_xy=True).transform(c[:, 0], c[:, 1])])
nok = shapely.get_coordinates(shapely.segmentize(g, 50))
D["anayol"] = cKDTree(nok).query(H, workers=-1)[0]
print(f"mesafeler hesaplandı · {time.time() - bas:.0f} sn")

# --- 3. ilçe toplamları (nüfus ağırlıklı paylar) -------------------------------------------------------------------
HUC = pd.DataFrame({"gid": GID, "p": P})
HUC["temel15"] = (D["okul"] <= 960) & (D["saglik"] <= 960) & (D["market"] <= 960)
HUC["okul400"] = D["okul"] <= 400
HUC["cami400"] = D["cami"] <= 400
HUC["oyun320"] = D["oyun"] <= 320
HUC["bulusma320"] = D["bulusma"] <= 320
HUC["ulasim"] = (D["durak"] <= 320) | (D["rayli"] <= 640)
HUC["rayli640"] = D["rayli"] <= 640
HUC["karma150"] = D["dukkan"] <= 150
HUC["anayol100"] = D["anayol"] <= 100
pay = ["temel15", "okul400", "cami400", "oyun320", "bulusma320", "ulasim", "rayli640", "karma150", "anayol100"]
A = (HUC[pay].astype(float).multiply(HUC.p, axis=0).groupby(HUC.gid).sum().div(HUC.groupby("gid").p.sum(), axis=0) * 100)
dk = gpd.GeoDataFrame(geometry=gpd.points_from_xy(KAT["dukkan"].lon, KAT["dukkan"].lat), crs=4326)
A["dukkan_n"] = gpd.sjoin(dk, ilce[["gid", "geometry"]], predicate="within").groupby("gid").size()
A = A.reset_index()

d = pd.read_csv(IS / "ilce_paneli_genis.csv", dtype={"ilce_kod": str})
d = d.merge(A, on="gid", how="left")
d["dukkan_n"] = d.dukkan_n.fillna(0)
d["kavsak_yog"] = d.kavsak_km2_yapili
d["yesil300"] = d.yesil300_pay
d["yukseklik_m"] = d.yuk_nufus_agirlikli
d["yuksek_pay15"] = d.pay_h15p
d["zemin_pay"] = 100 - d.pay_h9p
d["esnaf1000"] = d.dukkan_n / d.nufus_2025 * 1000
d["yayilma"] = d.yapili_ha / d.ghs_nufus * 1000
# FUE v0.2 uydu göstergeleri (03_VERI/kod/uydu_ulusal.py): PM2.5, ağaç örtüsü, yaz yüzey sıcaklığı, yapılı alan.
# Yüzey sıcaklığı ilçede nüfus ağırlıklı mutlak değerdir; bölgesel iklim il sabit etkisiyle soğurulur
# (ilçe alanına göre fark tamamen kentsel ilçelerde sıfıra yaklaştığı için endekste kullanılmaz)
UYDU = IS / "ilce_uydu.csv"
if UYDU.exists():
    d = d.merge(pd.read_csv(UYDU), on="gid", how="left")

GOS = [("kavsak_yog", "B1", +1), ("temel15", "B1", +1),
       ("yesil300", "B2", +1), ("yukseklik_m", "B2", -1), ("yuksek_pay15", "B2", -1), ("anayol100", "B2", -1),
       ("zemin_pay", "B3", +1), ("oyun320", "B3", +1), ("okul400", "B3", +1),
       ("esnaf1000", "B4", +1), ("karma150", "B4", +1),
       ("cami400", "B5", +1), ("bulusma320", "B5", +1),
       ("ulasim", "B6", +1), ("yayilma", "B6", -1), ("rayli640", "B6", +1)]
for k, b, yon in GOS:
    r = d[k].rank(pct=True) * 100
    d["p_" + k] = r if yon > 0 else 100 - r
BOY = ["B1", "B2", "B3", "B4", "B5", "B6"]
for b in BOY:
    d[b] = d[["p_" + k for k, bb, _ in GOS if bb == b]].mean(axis=1)
d["FUE_lite"] = d[BOY].mean(axis=1)
d["FUE_lite_yuksekliksiz"] = d[["p_" + k for k, _, _ in GOS if k not in ("yukseklik_m", "yuksek_pay15", "zemin_pay")]].mean(axis=1)
# iki alt endeks: Erişim (E, "15 dakikalık şehir") ve Çevre-ölçek (Ç, doğa, yükseklik, ana yol, yayılma)
ERISIM = ["kavsak_yog", "temel15", "oyun320", "okul400", "esnaf1000", "karma150", "cami400", "bulusma320", "ulasim", "rayli640"]
CEVRE = ["yesil300", "yukseklik_m", "yuksek_pay15", "zemin_pay", "anayol100", "yayilma"]
d["E_lite"] = d[["p_" + k for k in ERISIM]].mean(axis=1)
d["C_lite"] = d[["p_" + k for k in CEVRE]].mean(axis=1)
ENDEKS = ["FUE_lite", "FUE_lite_yuksekliksiz", "E_lite", "C_lite"]
GOS_UYDU = [("pm25", "B1", -1), ("agac300", "B2", +1), ("lst", "B6", -1), ("yapili300", "B6", -1)]
TEKIL = []
if "pm25" in d:
    for k, b, yon in GOS_UYDU:
        r = d[k].rank(pct=True) * 100
        d["p_" + k] = r if yon > 0 else 100 - r
    for b in BOY:
        d[b + "_v2"] = d[["p_" + k for k, bb, _ in GOS + GOS_UYDU if bb == b]].mean(axis=1)
    d["FUE_lite_v2"] = d[[b + "_v2" for b in BOY]].mean(axis=1)
    d["C_lite_v2"] = d[["p_" + k for k in CEVRE + [k for k, _, _ in GOS_UYDU]]].mean(axis=1)
    ENDEKS += ["C_lite_v2", "FUE_lite_v2"]
    TEKIL = ["pm25", "agac300", "lst", "lst_fark", "yapili300"]
kol = ["gid", "ilce_kod", "il", "ilce_ad_tuik", "nufus_2025"] + [k for k, _, _ in GOS] + TEKIL + BOY + ENDEKS
d[kol].to_csv(IS / "ilce_fue_lite.csv", index=False, encoding="utf-8")


# --- 4. il içi geçerlilik modelleri -------------------------------------------------------------------------------
def yz(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "†" if p < 0.10 else ""


SONUC = {"smr": "Standartlaştırılmış ölüm oranı", "tdh_ilce": "Toplam doğurganlık hızı",
         "tek_kisi_pay": "Tek kişilik hane (%)", "genis_aile_pay": "Geniş aile hanesi (%)",
         "k2534_bekar_pay": "25–34 yaş kadın hiç evlenmemiş (%)", "bosanma_hiz": "Boşanma hızı (‰)"}
MODEL = [("il SE + eğitim + göç", "egitim + artis"), ("+ ln yoğunluk", "egitim + artis + ln_yogunluk"),
         ("+ kentsellik ve yaş yapısı", "egitim + artis + ln_yogunluk + merkez_pay + yasli_pay")]
satir = []
for y, yad in SONUC.items():
    for x in ENDEKS + BOY + TEKIL:
        for mad, kont in MODEL:
            sub = d.dropna(subset=[y, x, "egitim", "artis", "ln_yogunluk", "merkez_pay", "yasli_pay", "nufus_2025"]).copy()
            for v in [y, x]:
                sub[v + "_z"] = (sub[v] - sub[v].mean()) / sub[v].std(ddof=0)
            m = smf.wls(f"{y}_z ~ {x}_z + {kont} + C(il)", sub, weights=sub.nufus_2025).fit(
                cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
            satir.append({"sonuc": y, "sonuc_ad": yad, "endeks": x, "model": mad, "beta": m.params[x + "_z"],
                          "sh": m.bse[x + "_z"], "p": m.pvalues[x + "_z"], "n": int(m.nobs), "yildiz": yz(m.pvalues[x + "_z"])})
T = pd.DataFrame(satir)
T.to_csv(SON / "fue_ilce_gecerlilik.csv", index=False, encoding="utf-8")
print("\nİL İÇİ GEÇERLİLİK (standartlaştırılmış β; il SE; il kümelenmiş SH; nüfus ağırlıklı)")
print(T.assign(b=T.beta.round(3).astype(str) + T.yildiz).pivot_table(index=["sonuc", "model"], columns="endeks", values="b", aggfunc="first")
      [ENDEKS + BOY + TEKIL].to_string())

# --- 4b. Erişim–ölümlülük ilişkisi çevre yükleriyle açıklanıyor mu? (aracılık sınaması) ---------------------------
if TEKIL:
    sub = d.dropna(subset=["smr", "E_lite", "pm25", "lst", "agac300", "egitim", "artis", "ln_yogunluk", "merkez_pay",
                           "yasli_pay"]).copy()
    for v in ["smr", "E_lite", "pm25", "lst", "agac300", "yapili300"]:
        sub[v + "_z"] = (sub[v] - sub[v].mean()) / sub[v].std(ddof=0)
    CK = [("temel", "egitim + artis"),
          ("+ çevre yükleri (PM2.5, yüzey sıcaklığı, ağaç)", "egitim + artis + pm25_z + lst_z + agac300_z"),
          ("+ kentsellik ve yaş yapısı", "egitim + artis + ln_yogunluk + merkez_pay + yasli_pay"),
          ("+ çevre yükleri + kentsellik ve yaş yapısı", "egitim + artis + pm25_z + lst_z + agac300_z + ln_yogunluk + merkez_pay + yasli_pay")]
    ck = []
    for ad, kont in CK:
        m = smf.wls(f"smr_z ~ E_lite_z + {kont} + C(il)", sub, weights=sub.nufus_2025).fit(
            cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
        satir_ = {"model": ad, "n": int(m.nobs)}
        for k in ["E_lite_z", "pm25_z", "lst_z", "agac300_z"]:
            if k in m.params:
                satir_[k[:-2] + "_b"], satir_[k[:-2] + "_sh"], satir_[k[:-2] + "_p"] = m.params[k], m.bse[k], m.pvalues[k]
        ck.append(satir_)
    CK = pd.DataFrame(ck)
    CK.to_csv(SON / "fue_ilce_cevre_kontrol.csv", index=False, encoding="utf-8")
    print("\nErişim (E) → SMR, çevre yükleri kontrol edilince:\n", CK.round(3).to_string(index=False))

# --- 5. Faz 2'nin "yükseklik → ölümlülük" bulgusunun kentsellik göstergeleriyle yeniden sınanması ---------------------
d["ln_kavsak"] = np.log1p(d.kavsak_yog)
YENI = [("Faz 2 modeli", "yukseklik + ln_yogunluk + yesil300 + ln_kavsak + egitim + artis"),
        ("+ 15 dk temel ihtiyaç", "yukseklik + ln_yogunluk + yesil300 + ln_kavsak + egitim + artis + temel15"),
        ("+ temel ihtiyaç, ulaşım, cami", "yukseklik + ln_yogunluk + yesil300 + ln_kavsak + egitim + artis + temel15 + ulasim + cami400"),
        ("+ kent merkezi payı", "yukseklik + ln_yogunluk + yesil300 + ln_kavsak + egitim + artis + temel15 + ulasim + cami400 + merkez_pay")]
if TEKIL:
    YENI.append(("+ PM2.5, yüzey sıcaklığı, ağaç örtüsü", "yukseklik + ln_yogunluk + yesil300 + ln_kavsak + egitim + artis + temel15 + "
                 "ulasim + cami400 + merkez_pay + pm25 + lst + agac300"))
sub = d.dropna(subset=["smr", "yukseklik", "ln_yogunluk", "yesil300", "ln_kavsak", "egitim", "artis", "temel15", "ulasim",
                       "cami400", "merkez_pay"] + (["pm25", "lst", "agac300"] if TEKIL else []))
yy = []
for ad, f in YENI:
    m = smf.wls(f"smr ~ {f} + C(il)", sub, weights=sub.beklenen_olum_2025).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
    yy.append({"model": ad, "yukseklik_b": m.params.yukseklik, "yukseklik_sh": m.bse.yukseklik, "yukseklik_p": m.pvalues.yukseklik,
               "kat_basina_yuzde": 100 * 3 * m.params.yukseklik,
               **{f"{k}_b": m.params[k] for k in ["temel15", "ulasim", "cami400", "merkez_pay", "pm25", "lst", "agac300"] if k in m.params},
               **{f"{k}_p": m.pvalues[k] for k in ["temel15", "ulasim", "cami400", "merkez_pay", "pm25", "lst", "agac300"] if k in m.params},
               "n": int(m.nobs)})
YY = pd.DataFrame(yy)
YY.to_csv(SON / "fue_ilce_yukseklik_yeniden.csv", index=False, encoding="utf-8")
print("\nFaz 2 yükseklik–SMR bulgusu, kentsellik kontrolleriyle:\n", YY.round(4).to_string(index=False))
print("\nFUE-lite dağılımı:", d.FUE_lite.describe().round(1).to_dict())
pil = d[d.ilce_kod.astype(int).isin([1327, 1622, 2050, 1829, 1863, 1827, 2080, 2085, 1587, 1187])]
print(pil[["ilce_ad_tuik", "FUE_lite", "E_lite", "C_lite"] + (["C_lite_v2", "pm25", "agac300", "lst"] if TEKIL else []) + BOY].round(1).sort_values("FUE_lite", ascending=False).to_string(index=False))
print(f"Tamam · {time.time() - bas:.0f} sn")
