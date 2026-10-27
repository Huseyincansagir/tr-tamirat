"""
81 il paneli — mekânın doğurganlık ve aile göstergeleri üzerindeki payı
=======================================================================
Girdi : 03_VERI/ham/tuik/il_paneli_ham_2025.csv (TÜİK Veri Portalı tabloları, bkz. kaynaklar.md)
        03_VERI/ham/sinirlar/geoBoundaries-TUR-ADM1_simplified.geojson
Çıktı : 03_VERI/islenmis/il_paneli_2025.csv / .gpkg
        05_ANALIZ/sonuclar/*.csv

Yöntem özeti
  1. Türetilmiş değişkenler (mekân, kontrol, sonuç)
  2. Ana model (her sonuç için): z(Y) ~ z(ort. kat) + z(yoğun kent payı) + z(ln GSYH/kişi)
                                 + z(kadın eğitim süresi) + Doğu-Güneydoğu kuklası   [HC3]
  3. Shapley R² ayrıştırması: Mekân / Gelir / Eğitim / Bölge-kültür grupları
  4. Eğitim-içi analiz: aynı eğitim düzeyindeki annelerin il doğurganlığı ~ mekân + kontroller (WLS)
  5. İl-içi kent-kır ve eğitim farkları (betimsel)
  6. Sağlamlık: alternatif mekân ölçüleri, bölge sabit etkileri, ağırlıklandırma, batı alt örneklemi,
     uzun fark (2020→2025), Moran's I (mekânsal otokorelasyon)

Bu bir ekolojik (il düzeyi) ve kesitsel analizdir; bireysel nedensellik iddiası taşımaz.
"""

import itertools
import math
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham"
ISLENMIS = KOK / "03_VERI" / "islenmis"
SONUC = KOK / "05_ANALIZ" / "sonuclar"
SONUC.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(2026)

# --- 1. Veri ve türetilmiş değişkenler ------------------------------------------------
d = pd.read_csv(HAM / "tuik" / "il_paneli_ham_2025.csv")
d["ibbs1"] = d.ibbs3_kod.str[:3]
d["dogu"] = d.ibbs1.isin(["TRA", "TRB", "TRC"]).astype(int)          # Kuzeydoğu, Ortadoğu, Güneydoğu Anadolu

d["kk_yogun_kent_2025"] = d.kk_yogun_kent_2025.fillna(0)
d["yogun_kent_pay"] = 100 * d.kk_yogun_kent_2025 / d.kk_toplam_2025
d["kir_pay"] = 100 * d.kk_kir_2025 / d.kk_toplam_2025
d["kat5p_pct"] = d.kat5_pct + d.kat6p_pct
d["kat12_pct"] = d.kat1_pct + d.kat2_pct
d["ln_yogunluk"] = np.log(d.nufus_yogunlugu_2025)
d["ln_gsyh"] = np.log(d.gsyh_kb_tl_2024)
d["tek_kisi_pay"] = 100 * d.hane_tek_kisi / d.hane_sayisi_2025
d["genis_aile_pay"] = 100 * d.hane_genis / d.hane_sayisi_2025
d["yasli_yakin"] = d[["yasli_cocuk_ayni_adres", "yasli_cocuk_ayni_bina",
                      "yasli_cocuk_ayni_sokak", "yasli_cocuk_ayni_mahalle"]].sum(axis=1)
d["d_tdh_20_25"] = d.tdh_2025 - d.tdh_2020
d["kir_yogun_farki"] = d.tdh25_kir - d.tdh25_yogun
d["ilkokul_yuksek_farki"] = d.tdh25_e_ilkokul - d.tdh25_e_yuksek

ETIKET = {
    "tdh_2025": "Toplam doğurganlık hızı",
    "kaba_evlenme_2025": "Kaba evlenme hızı (‰)",
    "kaba_bosanma_2025": "Kaba boşanma hızı (‰)",
    "ilk_evlenme_yasi_k_2025": "Kadın ilk evlenme yaşı",
    "ilk_dogum_yasi_2025": "İlk doğumda anne yaşı",
    "hane_buyukluk_2025": "Ortalama hane büyüklüğü",
    "tek_kisi_pay": "Tek kişilik hane payı (%)",
    "genis_aile_pay": "Geniş aile hane payı (%)",
    "yasli_yakin": "Çocuğuyla aynı mahallede ya da daha yakın oturan yaşlı (%)",
    "ort_kat_2021": "Ortalama kat sayısı",
    "kat5p_pct": "5+ katlı binada oturan hane (%)",
    "kat12_pct": "1-2 katlı binada oturan hane (%)",
    "yogun_kent_pay": "Yoğun kentte yaşayan nüfus (%)",
    "ln_yogunluk": "ln(nüfus yoğunluğu)",
    "insa_2001_sonra_pct": "2001 sonrası binada oturan hane (%)",
    "kisi_basi_oda_2021": "Kişi başı oda",
    "ln_gsyh": "ln(kişi başı GSYH)",
    "kadin_egitim_suresi_2025": "Kadın ort. eğitim süresi (yıl)",
    "kadin_yuksekogretim_pct": "Yükseköğretimli kadın (%)",
    "dogu": "Doğu-Güneydoğu kuklası",
    "akraba_evliligi_pct": "Akraba evliliği (%)",
}

g = gpd.read_file(HAM / "sinirlar" / "geoBoundaries-TUR-ADM1_simplified.geojson")
g["il"] = g.shapeName.replace({"Hakkâri": "Hakkari"})
gd = g[["il", "geometry"]].merge(d, on="il", how="inner")
assert len(gd) == 81, "il eşleşmesi eksik"
d.to_csv(ISLENMIS / "il_paneli_2025.csv", index=False, encoding="utf-8")
gd.to_file(ISLENMIS / "il_paneli_2025.gpkg", layer="il_paneli", driver="GPKG")


# --- yardımcılar ---------------------------------------------------------------------
def z(s):
    return (s - s.mean()) / s.std(ddof=0)


def ols(df, y, xs, std=True, weights=None, cov="HC3"):
    sub = df[[y] + xs + ([weights] if weights else [])].dropna()
    Y = z(sub[y]) if std else sub[y]
    X = pd.DataFrame({x: (z(sub[x]) if (std and sub[x].nunique() > 2) else sub[x]) for x in xs})
    X = sm.add_constant(X)
    if weights:
        m = sm.WLS(Y, X, weights=sub[weights]).fit(cov_type=cov)
    else:
        m = sm.OLS(Y, X).fit(cov_type=cov)
    return m


def r2(df, y, xs):
    if not xs:
        return 0.0
    sub = df[[y] + xs].dropna()
    return sm.OLS(sub[y], sm.add_constant(sub[xs])).fit().rsquared


def shapley(df, y, gruplar):
    adlar = list(gruplar)
    n = len(adlar)
    deger = {}
    for k in range(n + 1):
        for s in itertools.combinations(adlar, k):
            deger[frozenset(s)] = r2(df, y, [v for a in s for v in gruplar[a]])
    out = {}
    for a in adlar:
        diger = [b for b in adlar if b != a]
        top = 0.0
        for k in range(n):
            for s in itertools.combinations(diger, k):
                w = math.factorial(k) * math.factorial(n - k - 1) / math.factorial(n)
                top += w * (deger[frozenset(s) | {a}] - deger[frozenset(s)])
        out[a] = top
    out["Toplam R²"] = deger[frozenset(adlar)]
    return out


def yildiz(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "†" if p < 0.10 else ""


def morans_i(gdf, kolon, perm=999):
    sub = gdf.dropna(subset=[kolon]).reset_index(drop=True)
    geom = sub.geometry.buffer(0)
    n = len(sub)
    W = np.zeros((n, n))
    for i in range(n):
        W[i] = geom.touches(geom.iloc[i]) | geom.intersects(geom.iloc[i])
        W[i, i] = 0
    rs = W.sum(1, keepdims=True)
    W = np.divide(W, rs, out=np.zeros_like(W), where=rs > 0)
    x = sub[kolon].values - sub[kolon].mean()
    I = n / W.sum() * (x @ W @ x) / (x @ x)
    sims = np.array([(lambda p: n / W.sum() * (p @ W @ p) / (p @ p))(RNG.permutation(x)) for _ in range(perm)])
    p = (np.sum(sims >= I) + 1) / (perm + 1)
    return I, p


MEKAN = ["ort_kat_2021", "yogun_kent_pay"]
KONTROL = ["ln_gsyh", "kadin_egitim_suresi_2025", "dogu"]
SONUCLAR = ["tdh_2025", "kaba_evlenme_2025", "kaba_bosanma_2025", "ilk_evlenme_yasi_k_2025",
            "ilk_dogum_yasi_2025", "hane_buyukluk_2025", "tek_kisi_pay", "genis_aile_pay", "yasli_yakin"]
GRUPLAR = {"Mekân": MEKAN, "Gelir": ["ln_gsyh"], "Eğitim": ["kadin_egitim_suresi_2025"], "Bölge-kültür": ["dogu"]}

# --- 2. Betimsel ve korelasyon ---------------------------------------------------------
print("=" * 100)
print("BETİMSEL (81 il)")
bet = d[["tdh_2025", "ort_kat_2021", "kat5p_pct", "yogun_kent_pay", "gsyh_kb_tl_2024",
         "kadin_egitim_suresi_2025", "kaba_evlenme_2025", "kaba_bosanma_2025", "yasli_yakin"]].describe().T
print(bet[["mean", "std", "min", "50%", "max"]].round(2))

kor_x = ["ort_kat_2021", "kat5p_pct", "yogun_kent_pay", "ln_yogunluk", "ln_gsyh", "kadin_egitim_suresi_2025", "dogu"]
kor = d[SONUCLAR + kor_x].corr().loc[SONUCLAR, kor_x].round(2)
kor.to_csv(SONUC / "korelasyon_matrisi.csv", encoding="utf-8")
print("\nKORELASYON (Pearson) — sonuçlar × açıklayıcılar")
print(kor)
print("\nMekân–kontrol korelasyonları")
print(d[kor_x].corr().round(2))

# --- 3. Ana modeller --------------------------------------------------------------------
print("\n" + "=" * 100)
print("ANA MODEL (standartlaştırılmış β, HC3): z(Y) ~ ort.kat + yoğun kent payı + ln GSYH + kadın eğitim + Doğu")
satirlar = []
for y in SONUCLAR:
    m = ols(d, y, MEKAN + KONTROL)
    sh = shapley(d, y, GRUPLAR)
    r = {"sonuc": y, "n": int(m.nobs), "R2": m.rsquared, "R2_adj": m.rsquared_adj}
    for x in MEKAN + KONTROL:
        r[f"b_{x}"] = m.params[x]
        r[f"p_{x}"] = m.pvalues[x]
    for k, v in sh.items():
        r[f"shapley_{k}"] = v
    satirlar.append(r)
ana = pd.DataFrame(satirlar)
ana.to_csv(SONUC / "ana_model_sonuclari.csv", index=False, encoding="utf-8")
for _, r in ana.iterrows():
    parca = " | ".join(f"{x.split('_')[0][:6]} {r['b_'+x]:+.2f}{yildiz(r['p_'+x])}" for x in MEKAN + KONTROL)
    print(f"{ETIKET[r.sonuc][:38]:38s} R²={r.R2:.2f} | {parca}")
print("\nSHAPLEY R² PAYLARI (toplam R²'nin gruplara bölüşümü)")
shp_k = [c for c in ana.columns if c.startswith("shapley_")]
tab = ana.set_index("sonuc")[shp_k]
tab.columns = [c.replace("shapley_", "") for c in shp_k]
print(tab.round(3))
pay = tab.drop(columns="Toplam R²").div(tab["Toplam R²"], axis=0) * 100
pay.round(1).to_csv(SONUC / "shapley_yuzde_paylari.csv", encoding="utf-8")
print("\nYüzde olarak (açıklanan varyans içindeki pay):")
print(pay.round(1))

vif_X = sm.add_constant(d[MEKAN + KONTROL])
vif = pd.Series([variance_inflation_factor(vif_X.values, i) for i in range(1, vif_X.shape[1])], index=MEKAN + KONTROL)
print("\nVIF:", vif.round(2).to_dict())

# --- 4. Eğitim-içi analiz ---------------------------------------------------------------
print("\n" + "=" * 100)
print("EĞİTİM-İÇİ ANALİZ: aynı eğitim düzeyindeki annelerin il TDH'si ~ mekân + gelir + Doğu (WLS, kadın nüfusu)")
egt = []
for e in ["tdh25_e_ilkokul", "tdh25_e_ortaokul", "tdh25_e_lise", "tdh25_e_yuksek"]:
    m = ols(d, e, MEKAN + ["ln_gsyh", "dogu"], weights="kadin_6p_nufus")
    egt.append({"egitim": e.replace("tdh25_e_", ""), "n": int(m.nobs), "R2": m.rsquared,
                **{f"b_{x}": m.params[x] for x in MEKAN + ["ln_gsyh", "dogu"]},
                **{f"p_{x}": m.pvalues[x] for x in MEKAN + ["ln_gsyh", "dogu"]}})
egt = pd.DataFrame(egt)
egt.to_csv(SONUC / "egitim_ici_modeller.csv", index=False, encoding="utf-8")
for _, r in egt.iterrows():
    print(f"{r.egitim:10s} R²={r.R2:.2f} | ort.kat {r.b_ort_kat_2021:+.2f}{yildiz(r.p_ort_kat_2021)} | "
          f"yoğun kent {r.b_yogun_kent_pay:+.2f}{yildiz(r.p_yogun_kent_pay)} | ln GSYH {r.b_ln_gsyh:+.2f}{yildiz(r.p_ln_gsyh)} | "
          f"Doğu {r.b_dogu:+.2f}{yildiz(r.p_dogu)}")

# --- 5. İl-içi farklar ------------------------------------------------------------------
print("\n" + "=" * 100)
print("İL-İÇİ FARKLAR (2025)")
kk = d.dropna(subset=["kir_yogun_farki"])
print(f"Kır − yoğun kent TDH farkı: {len(kk)} il, ortalama {kk.kir_yogun_farki.mean():+.2f}, "
      f"medyan {kk.kir_yogun_farki.median():+.2f}, pozitif olan il {int((kk.kir_yogun_farki > 0).sum())}")
print(f"İlkokul − yükseköğretim mezunu anne TDH farkı: ortalama {d.ilkokul_yuksek_farki.mean():+.2f}, "
      f"medyan {d.ilkokul_yuksek_farki.median():+.2f}, pozitif olan il {int((d.ilkokul_yuksek_farki > 0).sum())}")
kk_m = ols(kk, "kir_yogun_farki", ["ort_kat_2021", "ln_gsyh", "dogu"], std=False)
print("Kır−yoğun kent farkı ~ ort.kat + ln GSYH + Doğu (ham katsayı):",
      {k: f"{v:+.3f}{yildiz(kk_m.pvalues[k])}" for k, v in kk_m.params.items()})
d[["il", "tdh25_kir", "tdh25_orta", "tdh25_yogun", "kir_yogun_farki", "tdh25_e_ilkokul", "tdh25_e_yuksek",
   "ilkokul_yuksek_farki"]].to_csv(SONUC / "il_ici_farklar.csv", index=False, encoding="utf-8")

# --- 6. Sağlamlık (TDH) -----------------------------------------------------------------
print("\n" + "=" * 100)
print("SAĞLAMLIK — TDH 2025, mekân katsayıları (standartlaştırılmış)")
sag = []


def kaydet(ad, m, xs):
    r = {"model": ad, "n": int(m.nobs), "R2": m.rsquared}
    for x in xs:
        if x in m.params:
            r[x] = f"{m.params[x]:+.2f}{yildiz(m.pvalues[x])}"
    sag.append(r)


kaydet("Ana model", ols(d, "tdh_2025", MEKAN + KONTROL), MEKAN)
kaydet("5+ kat payı", ols(d, "tdh_2025", ["kat5p_pct", "yogun_kent_pay"] + KONTROL), ["kat5p_pct", "yogun_kent_pay"])
kaydet("1-2 kat payı", ols(d, "tdh_2025", ["kat12_pct", "yogun_kent_pay"] + KONTROL), ["kat12_pct", "yogun_kent_pay"])
kaydet("ln yoğunluk", ols(d, "tdh_2025", ["ort_kat_2021", "ln_yogunluk"] + KONTROL), ["ort_kat_2021", "ln_yogunluk"])
kaydet("Yalnız ort. kat", ols(d, "tdh_2025", ["ort_kat_2021"] + KONTROL), ["ort_kat_2021"])
kaydet("+ akraba evliliği", ols(d, "tdh_2025", MEKAN + KONTROL + ["akraba_evliligi_pct"]), MEKAN + ["akraba_evliligi_pct"])
kaydet("+ yükseköğretimli kadın (eğitim süresi yerine)",
       ols(d, "tdh_2025", MEKAN + ["ln_gsyh", "kadin_yuksekogretim_pct", "dogu"]), MEKAN)
bolge = pd.get_dummies(d.ibbs1, prefix="b", drop_first=True, dtype=float)
dfb = pd.concat([d, bolge], axis=1)
kaydet("İBBS-1 sabit etkileri (12 bölge)", ols(dfb, "tdh_2025", MEKAN + ["ln_gsyh", "kadin_egitim_suresi_2025"] + list(bolge.columns)), MEKAN)
kaydet("Nüfus ağırlıklı (WLS)", ols(d, "tdh_2025", MEKAN + KONTROL, weights="nufus_2025"), MEKAN)
bati = d[d.dogu == 0]
kaydet(f"Batı alt örneklemi (Doğu hariç)", ols(bati, "tdh_2025", MEKAN + ["ln_gsyh", "kadin_egitim_suresi_2025"]), MEKAN)
kaydet("Uzun fark ΔTDH 2020→25 (+TDH 2020)", ols(d, "d_tdh_20_25", MEKAN + KONTROL + ["tdh_2020"]), MEKAN + ["tdh_2020"])
kaydet("Kadın ilk evlenme yaşı kontrol", ols(d, "tdh_2025", MEKAN + KONTROL + ["ilk_evlenme_yasi_k_2025"]), MEKAN + ["ilk_evlenme_yasi_k_2025"])
sag = pd.DataFrame(sag)
sag.to_csv(SONUC / "saglamlik_tdh.csv", index=False, encoding="utf-8")
print(sag.to_string(index=False))

# --- 7. Mekânsal otokorelasyon ----------------------------------------------------------
print("\n" + "=" * 100)
ana_m = ols(d, "tdh_2025", MEKAN + KONTROL)
# gd, sınır dosyasının sırasında; artıklar il adıyla eşlenmeli
gd["artik_tdh"] = gd.il.map(pd.Series(ana_m.resid.values, index=d.loc[ana_m.resid.index, "il"]))
gd["yordanan_tdh_z"] = gd.il.map(pd.Series(ana_m.fittedvalues.values, index=d.loc[ana_m.fittedvalues.index, "il"]))
assert gd.artik_tdh.notna().all()
I1, p1 = morans_i(gd, "tdh_2025")
I2, p2 = morans_i(gd, "artik_tdh")
fe_m = ols(dfb, "tdh_2025", MEKAN + ["ln_gsyh", "kadin_egitim_suresi_2025"] + list(bolge.columns))
gd["artik_tdh_fe"] = gd.il.map(pd.Series(fe_m.resid.values, index=d.loc[fe_m.resid.index, "il"]))
I3, p3 = morans_i(gd, "artik_tdh_fe")
print(f"Moran's I — TDH 2025: {I1:.3f} (p={p1:.3f}); ana model artıkları: {I2:.3f} (p={p2:.3f}); "
      f"İBBS-1 sabit etkili model artıkları: {I3:.3f} (p={p3:.3f})")
GRUPLAR_FE = {"Mekân": MEKAN, "Gelir": ["ln_gsyh"], "Eğitim": ["kadin_egitim_suresi_2025"],
              "Bölge (12 İBBS-1)": list(bolge.columns)}
shp_fe = []
for y in SONUCLAR:
    sh = shapley(dfb, y, GRUPLAR_FE)
    shp_fe.append({"sonuc": y, **{k: v for k, v in sh.items()}})
shp_fe = pd.DataFrame(shp_fe).set_index("sonuc")
shp_fe_pct = shp_fe.drop(columns="Toplam R²").div(shp_fe["Toplam R²"], axis=0) * 100
shp_fe_pct["Toplam R²"] = shp_fe["Toplam R²"]
shp_fe_pct.round(3).to_csv(SONUC / "shapley_bolge_sabit_etkili.csv", encoding="utf-8")
print("\nSHAPLEY (12 bölge sabit etkisiyle) — açıklanan varyans içindeki % pay ve toplam R²")
print(shp_fe_pct.round(2))
gd[["il", "artik_tdh", "yordanan_tdh_z"]].to_csv(SONUC / "ana_model_artiklar.csv", index=False, encoding="utf-8")
pd.DataFrame([{"degisken": "tdh_2025", "morans_I": I1, "p": p1}, {"degisken": "ana_model_artiklari", "morans_I": I2, "p": p2}]) \
    .to_csv(SONUC / "morans_i.csv", index=False, encoding="utf-8")

# Ham katsayı yorumu: ort. kat 1 birim (1 kat) artışının TDH'ye etkisi (ana model, standartlaştırılmamış)
ham = ols(d, "tdh_2025", MEKAN + KONTROL, std=False)
print("\nHAM KATSAYILAR (TDH, çocuk/kadın):", {k: f"{v:+.3f} (p={ham.pvalues[k]:.3f})" for k, v in ham.params.items()})
print("ort.kat 1 SS =", round(d.ort_kat_2021.std(ddof=0), 2), "kat; yoğun kent payı 1 SS =", round(d.yogun_kent_pay.std(ddof=0), 1), "puan")
