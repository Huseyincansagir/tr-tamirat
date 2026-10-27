"""
973 ilçe paneli — il sabit etkisiyle mekânın doğurganlık üzerindeki etkisi (il içi karşılaştırma)
==============================================================================================
Girdi : 03_VERI/islenmis/ilce_paneli.csv / .gpkg (ilce_paneli_olustur.py)
Çıktı : 05_ANALIZ/sonuclar/ilce_*.csv

Sonuç değişkenleri
  cwr        : çocuk-kadın oranı = 0-4 yaş çocuk / 15-49 yaş kadın × 1000 (2025, ADNKS)
  tdh_ilce   : dolaylı standartlaştırılmış toplam doğurganlık = 1,42 × (2025 doğum / beklenen doğum);
               beklenen doğum = Σ ilçedeki 15-49 kadın (5'li yaş) × Türkiye yaşa özel doğurganlık hızı 2025
  gdh        : genel doğurganlık hızı = 2025 doğum / 15-49 kadın × 1000
Mekân      : nüfus ağırlıklı bina yüksekliği (GHSL 2018, m), 5+ kat (≥15 m) ve 1-2 kat (<6 m) hücrelerde yaşayan
             nüfus payı, ln(yaşanan yoğunluk), il/ilçe merkezinde yaşayan nüfus payı
Kontroller : 15+ kadınların ortalama eğitim yılı (MEDAS 2025), nüfus değişimi 2024→2025 (göç vekili),
             il sabit etkisi (81). Standart hatalar il düzeyinde kümelenmiş; ana modeller 15-49 kadın nüfusuyla ağırlıklı.
"""

import itertools
import math
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220)
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
SONUC = KOK / "05_ANALIZ" / "sonuclar"
RNG = np.random.default_rng(2026)

g = gpd.read_file(IS / "ilce_paneli.gpkg")
d = pd.DataFrame(g.drop(columns="geometry"))

d["cwr"] = 1000 * d.cocuk_0_4 / d.kadin_15_49
d["tdh_ilce"] = 1.42 * d.dogum_2025 / d.beklenen_dogum_2025
d["tdh_ilce_2y"] = 1.42 * (d.dogum_2024 + d.dogum_2025) / 2 / d.beklenen_dogum_2025
d["gdh"] = 1000 * d.dogum_2025 / d.kadin_15_49
d["yukseklik"] = d.yuk_nufus_agirlikli
d["ln_yogunluk"] = np.log(d.yasanan_yogunluk)
d["merkez_pay"] = 100 * d.merkez_nufus_2025 / d.nufus_2025
d["egitim"] = d.kadin15p_egitim_yil
d["yuksek_pay"] = 100 * d.kadin15p_yuksek / d.kadin15p_bilinen
d["artis"] = 100 * (d.nufus_2025 / d.nufus_2024 - 1)
d["yasli_pay"] = 100 * d.nufus_65p / d.nufus_2025
d["dogu"] = d.ibbs3_kod.str[:3].isin(["TRA", "TRB", "TRC"]).astype(int)
BUYUKSEHIR = ["Adana", "Ankara", "Antalya", "Aydın", "Balıkesir", "Bursa", "Denizli", "Diyarbakır", "Erzurum", "Eskişehir",
              "Gaziantep", "Hatay", "Mersin", "İstanbul", "İzmir", "Kayseri", "Kocaeli", "Konya", "Malatya", "Manisa",
              "Kahramanmaraş", "Mardin", "Muğla", "Ordu", "Sakarya", "Samsun", "Tekirdağ", "Trabzon", "Şanlıurfa", "Van"]
d["buyuksehir"] = d.il.isin(BUYUKSEHIR).astype(int)
d["agirlik"] = d.kadin_15_49
d["yuk_sinif"] = pd.cut(d.yukseklik, [0, 4, 6, 9, 12, 100], labels=["<4 m", "4-6 m", "6-9 m", "9-12 m", "12+ m"], right=False)
d.to_csv(IS / "ilce_paneli_analiz.csv", index=False, encoding="utf-8")

print("=" * 110)
print("BETİMSEL (973 ilçe)")
print(d[["cwr", "tdh_ilce", "gdh", "yukseklik", "pay_h15p", "pay_h6alt", "ln_yogunluk", "merkez_pay", "egitim", "artis"]]
      .describe().T[["mean", "std", "min", "50%", "max"]].round(2))
print("\nYükseklik sınıfına göre ilçe sayısı:", d.yuk_sinif.value_counts().sort_index().to_dict())
print("Kontrol: ilçe TDH (kadın ağırlıklı) =", round(np.average(d.tdh_ilce, weights=d.beklenen_dogum_2025), 3), "(Türkiye 1,42)")

# il içi korelasyonlar (il ortalamalarından sapmalar)
dm = d.copy()
for c in ["cwr", "tdh_ilce", "yukseklik", "pay_h15p", "ln_yogunluk", "merkez_pay", "egitim", "artis"]:
    dm[c] = d[c] - d.groupby("il")[c].transform("mean")
print("\nİL İÇİ KORELASYON (il ortalamasından sapmalar)")
print(dm[["tdh_ilce", "cwr", "yukseklik", "pay_h15p", "ln_yogunluk", "merkez_pay", "egitim", "artis"]].corr().round(2).iloc[:2])


def model(df, y, xs, fe="C(il)", w="agirlik", std=True):
    sub = df.dropna(subset=[y] + xs + ([w] if w else []))
    xs = [x for x in xs if sub[x].std() > 1e-9]  # büyükşehirlerde merkez payı sabit (%100)
    s = sub.copy()
    if std:
        for v in [y] + xs:
            s[v] = (s[v] - s[v].mean()) / s[v].std(ddof=0)
    f = f"{y} ~ " + " + ".join(xs) + (f" + {fe}" if fe else "")
    kw = dict(cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]}) if sub.il.nunique() > 1 else dict(cov_type="HC3")
    m = (smf.wls(f, s, weights=sub[w]) if w else smf.ols(f, s)).fit(**kw)
    return m


def yz(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "†" if p < 0.10 else ""


def satir(ad, m, xs):
    return {"model": ad, "n": int(m.nobs), "R2": round(m.rsquared, 3),
            **{x: f"{m.params[x]:+.3f}{yz(m.pvalues[x])}" for x in xs if x in m.params}}


MEKAN = ["yukseklik", "ln_yogunluk", "merkez_pay"]
KONT = ["egitim", "artis"]

print("\n" + "=" * 110)
print("ANA MODELLER (standartlaştırılmış β; il sabit etkisi; il düzeyinde kümelenmiş SH; 15-49 kadın ağırlıklı)")
tablo = []
for y in ["tdh_ilce", "cwr", "gdh"]:
    tablo.append(satir(f"{y}: yalnız mekân + il SE", model(d, y, MEKAN), MEKAN))
    tablo.append(satir(f"{y}: mekân + eğitim + göç + il SE", model(d, y, MEKAN + KONT), MEKAN + KONT))
    tablo.append(satir(f"{y}: il SE yok (iller arası+içi)", model(d, y, MEKAN + KONT, fe=None), MEKAN + KONT))
tablo = pd.DataFrame(tablo)
tablo.to_csv(SONUC / "ilce_ana_modeller.csv", index=False, encoding="utf-8")
print(tablo.to_string(index=False))

# Ham etki: +3 m (≈1 kat) nüfus ağırlıklı yükseklik → TDH
ham = model(d, "tdh_ilce", MEKAN + KONT, std=False)
print("\nHAM (TDH, il SE, ağırlıklı):", {k: f"{v:+.4f} (p={ham.pvalues[k]:.3f})" for k, v in ham.params.items() if not k.startswith("C(")})
print("→ 3 m (≈1 kat) daha yüksek yaşanan bina: TDH", f"{3 * ham.params['yukseklik']:+.3f}",
      "| 1 yıl daha fazla kadın eğitimi: TDH", f"{ham.params['egitim']:+.3f}")
pd.DataFrame({"katsayi": ham.params, "p": ham.pvalues}).filter(regex="^(?!C\\()", axis=0) \
    .to_csv(SONUC / "ilce_ham_katsayilar_tdh.csv", encoding="utf-8")

# --- il içi Shapley (il SE'leri düşüldükten sonra açıklanan varyansın bölüşümü) -----
def r2_ic(df, y, xs, w="agirlik"):
    if not xs:
        return 0.0
    sub = df.dropna(subset=[y] + xs)
    return smf.wls(f"{y} ~ " + " + ".join(xs) + " + C(il)", sub, weights=sub[w]).fit().rsquared


def shapley_ic(df, y, gruplar):
    taban = smf.wls(f"{y} ~ C(il)", df, weights=df.agirlik).fit().rsquared
    ad = list(gruplar)
    v = {}
    for k in range(len(ad) + 1):
        for s in itertools.combinations(ad, k):
            v[frozenset(s)] = (r2_ic(df, y, [x for a in s for x in gruplar[a]]) if s else taban)
    out = {}
    n = len(ad)
    for a in ad:
        top = 0
        for k in range(n):
            for s in itertools.combinations([b for b in ad if b != a], k):
                w = math.factorial(k) * math.factorial(n - k - 1) / math.factorial(n)
                top += w * (v[frozenset(s) | {a}] - v[frozenset(s)])
        out[a] = top
    out["il SE R²"] = taban
    out["toplam R²"] = v[frozenset(ad)]
    return out


print("\n" + "=" * 110)
print("İL İÇİ SHAPLEY: il sabit etkisinin açıklamadığı farkın gruplara bölüşümü")
G = {"Mekân": MEKAN, "Eğitim": ["egitim"], "Göç": ["artis"]}
shp = pd.DataFrame({y: shapley_ic(d, y, G) for y in ["tdh_ilce", "cwr"]}).T
shp["il içi açıklanan"] = shp["toplam R²"] - shp["il SE R²"]
for k in G:
    shp[f"{k} %"] = 100 * shp[k] / shp["il içi açıklanan"]
shp.round(3).to_csv(SONUC / "ilce_shapley_il_ici.csv", encoding="utf-8")
print(shp.round(3).to_string())

# --- yükseklik sınıfları (doğrusal olmayan ilişki) -----------------------------------
print("\n" + "=" * 110)
print("YÜKSEKLİK SINIFLARI (referans <4 m; ham TDH farkı; il SE + eğitim + göç + yoğunluk + merkez payı)")
sub = d.dropna(subset=["tdh_ilce", "egitim", "artis"])
ms = smf.wls("tdh_ilce ~ C(yuk_sinif) + egitim + artis + ln_yogunluk + merkez_pay + C(il)", sub, weights=sub.agirlik) \
    .fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
sinif = pd.DataFrame({"fark": ms.params, "alt": ms.conf_int()[0], "ust": ms.conf_int()[1], "p": ms.pvalues}) \
    .filter(like="yuk_sinif", axis=0)
sinif.index = [i.split("T.")[-1].rstrip("]") for i in sinif.index]
sinif.round(4).to_csv(SONUC / "ilce_yukseklik_siniflari.csv", encoding="utf-8")
print(sinif.round(3))

# --- sağlamlık -------------------------------------------------------------------------
print("\n" + "=" * 110)
print("SAĞLAMLIK — TDH (ilçe), standartlaştırılmış β, il SE")
sag = []
sag.append(satir("Ana model", model(d, "tdh_ilce", MEKAN + KONT), MEKAN + KONT))
sag.append(satir("Ağırlıksız", model(d, "tdh_ilce", MEKAN + KONT, w=None), MEKAN + KONT))
sag.append(satir("2 yıllık doğum ortalaması", model(d, "tdh_ilce_2y", MEKAN + KONT), MEKAN + KONT))
sag.append(satir("5+ kat payı (yükseklik yerine)", model(d, "tdh_ilce", ["pay_h15p", "ln_yogunluk", "merkez_pay"] + KONT), ["pay_h15p", "egitim"]))
sag.append(satir("1-2 kat payı (yükseklik yerine)", model(d, "tdh_ilce", ["pay_h6alt", "ln_yogunluk", "merkez_pay"] + KONT), ["pay_h6alt", "egitim"]))
sag.append(satir("Eğitim: yükseköğretimli kadın payı", model(d, "tdh_ilce", MEKAN + ["yuksek_pay", "artis"]), MEKAN + ["yuksek_pay"]))
sag.append(satir("+ yaşlı nüfus payı", model(d, "tdh_ilce", MEKAN + KONT + ["yasli_pay"]), MEKAN + ["egitim", "yasli_pay"]))
sag.append(satir("Yalnız yükseklik + eğitim", model(d, "tdh_ilce", ["yukseklik", "egitim"]), ["yukseklik", "egitim"]))
for ad, alt in [("Büyükşehir ilçeleri", d[d.buyuksehir == 1]), ("Büyükşehir dışı", d[d.buyuksehir == 0]),
                ("Doğu-Güneydoğu hariç", d[d.dogu == 0]), ("Doğu-Güneydoğu", d[d.dogu == 1]),
                ("İstanbul (39)", d[d.il == "İstanbul"]), ("Ankara (25)", d[d.il == "Ankara"]), ("İzmir (30)", d[d.il == "İzmir"])]:
    fe = None if alt.il.nunique() == 1 else "C(il)"
    try:
        sag.append(satir(ad, model(alt, "tdh_ilce", MEKAN + KONT, fe=fe), MEKAN + KONT))
    except Exception as e:
        sag.append({"model": ad, "hata": str(e)[:60]})
sag = pd.DataFrame(sag)
sag.to_csv(SONUC / "ilce_saglamlik.csv", index=False, encoding="utf-8")
print(sag.to_string(index=False))

# --- mekânsal otokorelasyon (il SE modeli artıkları) -------------------------------
ana = model(d, "tdh_ilce", MEKAN + KONT)
g2 = g[["ilce_kod", "geometry"]].merge(d[["ilce_kod"]], on="ilce_kod")
g2["artik"] = g2.ilce_kod.map(pd.Series(ana.resid.values, index=d.loc[ana.resid.index, "ilce_kod"]))
geom = g2.geometry.buffer(0)
n = len(g2)
W = np.zeros((n, n))
sidx = geom.sindex
for i, gi in enumerate(geom):
    for j in sidx.query(gi, predicate="intersects"):
        if j != i:
            W[i, j] = 1
rs = W.sum(1, keepdims=True)
W = np.divide(W, rs, out=np.zeros_like(W), where=rs > 0)
def moran(v):
    x = (v - v.mean()).fillna(0).values
    I = n / W.sum() * (x @ W @ x) / (x @ x)
    sims = [n / W.sum() * ((p := RNG.permutation(x)) @ W @ p) / (p @ p) for _ in range(499)]
    return I, (np.sum(np.array(sims) >= I) + 1) / 500


I, p = moran(g2.artik)
print(f"\nMoran's I (il SE ana model artıkları, 973 ilçe): {I:.3f}  p={p:.3f}")
g2[["ilce_kod", "artik"]].to_csv(SONUC / "ilce_ana_model_artiklar.csv", index=False, encoding="utf-8")

# SLX sağlamlık: komşu ilçelerin ortalama yükseklik, eğitim ve göç değerleri modele eklenir
sira = g2.ilce_kod.tolist()
dd = d.set_index("ilce_kod").loc[sira].reset_index()
for v in ["yukseklik", "egitim", "artis", "ln_yogunluk"]:
    dd[f"W_{v}"] = W @ dd[v].fillna(dd[v].mean()).values
slx = model(dd, "tdh_ilce", MEKAN + KONT + ["W_yukseklik", "W_egitim", "W_artis", "W_ln_yogunluk"])
dd["artik_slx"] = np.nan
dd.loc[slx.resid.index, "artik_slx"] = slx.resid.values
I2, p2 = moran(dd.artik_slx)
print("SLX modeli (komşu ortalamaları eklenmiş):", satir("SLX", slx, MEKAN + KONT + ["W_yukseklik", "W_egitim"]),
      f"| artık Moran's I {I2:.3f} p={p2:.3f}")
