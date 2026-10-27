"""
973 ilçe — mekânın doğurganlık dışındaki sonuçlarla ilişkisi (il içi karşılaştırma)
================================================================================
Girdi : 03_VERI/islenmis/ilce_paneli_analiz.csv (ilce_paneli_analiz.py), ilce_olum_nufus.csv (MEDAS),
        ilce_evlenme_bosanma.csv (SDMX), ilce_osm.csv (osm_ilce.py), ilce_hane_medeni.csv (MEDAS; varsa)
Çıktı : 03_VERI/islenmis/ilce_paneli_genis.csv, 05_ANALIZ/sonuclar/ilce_diger_*.csv

Sonuçlar
  smr          : yaşa ve cinsiyete göre standartlaştırılmış ölüm oranı 2024–2025 (1 = Türkiye; dolaylı standartlaştırma,
                 Türkiye yaş-cinsiyete özel ölüm hızları × ilçe yaş-cinsiyet nüfusu)
  evlenme_hiz  : 2024–2025 ortalama evlenme / 20–34 yaş nüfus × 1000 (olay yerine göre kayıt — dikkat)
  bosanma_hiz  : 2024–2025 ortalama boşanma / 25–64 yaş nüfus × 1000
  hane, medeni : MEDAS'tan geliyorsa tek kişilik hane payı, ortalama hane büyüklüğü, 25–34 yaş kadınlarda hiç evlenmemiş payı
Mekân : yaşanan bina yüksekliği, ln yaşanan yoğunluk, ≥0,5 ha yeşil alana 300 m içinde nüfus payı, ln kavşak yoğunluğu
Kontrol: kadın eğitim yılı, nüfus değişimi (göç vekili), il sabit etkisi; il düzeyinde kümelenmiş SH; nüfus ağırlıklı
"""
import itertools
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 230)
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
SONUC = KOK / "05_ANALIZ" / "sonuclar"
oku = lambda f: pd.read_csv(IS / f, dtype={"ilce_kod": str})

d = oku("ilce_paneli_analiz.csv")
for f in ["ilce_olum_nufus.csv", "ilce_evlenme_bosanma.csv", "ilce_osm.csv", "ilce_hane_medeni.csv"]:
    if (IS / f).exists():
        ek = oku(f)
        d = d.merge(ek[[c for c in ek.columns if c == "ilce_kod" or c not in d.columns]], on="ilce_kod", how="left")
        print("eklendi:", f, ek.shape)

d["smr"] = (d.olum_2024 + d.olum_2025) / (d.beklenen_olum_2024 + d.beklenen_olum_2025)
d["evlenme_hiz"] = 1000 * (d.evlenme_2024 + d.evlenme_2025) / 2 / d.nufus_20_34
d["bosanma_hiz"] = 1000 * (d.bosanma_2024 + d.bosanma_2025) / 2 / d.nufus_25_64
d["yesil300"] = d.yesil300_pay
d["ln_kavsak"] = np.log1p(d.kavsak_km2_yapili)
d["yasli75_pay"] = 100 * d.nufus_75p / d.nufus_2025
if "hane_toplam" in d:
    d["tek_kisi_pay"] = 100 * d.hane_tek_kisi / d.hane_toplam
    d["genis_aile_pay"] = 100 * d.hane_genis / d.hane_toplam
    d["ort_hane"] = d.nufus_2025 / d.hane_toplam  # kurumsal nüfus dahil yaklaşık değer
    d["k2534_bekar_pay"] = 100 * d.k2534_bekar / (d.k2534_bekar + d.k2534_evli + d.k2534_bosanmis)
    d["k3544_bosanmis_pay"] = 100 * d.k3544_bosanmis / (d.k3544_evli + d.k3544_bosanmis)
d.to_csv(IS / "ilce_paneli_genis.csv", index=False, encoding="utf-8")

SONUCLAR = [c for c in ["smr", "evlenme_hiz", "bosanma_hiz", "tek_kisi_pay", "ort_hane", "genis_aile_pay", "k2534_bekar_pay",
                        "tdh_ilce"] if c in d and d[c].notna().sum() > 500]
MEKAN = ["yukseklik", "ln_yogunluk", "yesil300", "ln_kavsak"]
KONT = ["egitim", "artis"]
print("\nBETİMSEL")
print(d[SONUCLAR + MEKAN].describe().T[["mean", "std", "min", "50%", "max"]].round(3))
print("\nKontrol — Türkiye SMR (beklenen ağırlıklı):", round((d.olum_2024 + d.olum_2025).sum() / (d.beklenen_olum_2024 + d.beklenen_olum_2025).sum(), 4))
print("Nüfus ağırlıklı yeşil erişim %:", round(np.average(d.yesil300.fillna(0), weights=d.nufus_2025), 1))


def yz(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "†" if p < 0.10 else ""


def model(df, y, xs, fe=True, w="nufus_2025"):
    sub = df.dropna(subset=[y] + xs + [w]).copy()
    xs = [x for x in xs if sub[x].std() > 1e-9]
    for v in [y] + xs:
        sub[v + "_z"] = (sub[v] - sub[v].mean()) / sub[v].std(ddof=0)
    f = f"{y}_z ~ " + " + ".join(x + "_z" for x in xs) + (" + C(il)" if fe else "")
    m = smf.wls(f, sub, weights=sub[w]).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
    return m, xs


satirlar = []
for y in SONUCLAR:
    for ad, xs in [("mekân", MEKAN), ("mekân + eğitim + göç", MEKAN + KONT)]:
        m, xs2 = model(d, y, xs)
        satirlar.append({"sonuc": y, "model": ad, "n": int(m.nobs), "R2": round(m.rsquared, 3),
                         **{x: f"{m.params[x + '_z']:+.3f}{yz(m.pvalues[x + '_z'])}" for x in xs2}})
tab = pd.DataFrame(satirlar)
tab.to_csv(SONUC / "ilce_diger_modeller.csv", index=False, encoding="utf-8")
print("\nİL İÇİ MODELLER (standartlaştırılmış β; il SE; il düzeyinde kümelenmiş SH; nüfus ağırlıklı)")
print(tab.to_string(index=False))


def r2(df, y, xs):
    sub = df.dropna(subset=[y] + MEKAN + KONT + ["nufus_2025"])
    f = f"{y} ~ " + (" + ".join(xs) + " + " if xs else "") + "C(il)"
    return smf.wls(f, sub, weights=sub.nufus_2025).fit().rsquared


G = {"Mekân": MEKAN, "Eğitim": ["egitim"], "Göç": ["artis"]}
shp = []
for y in SONUCLAR:
    v = {frozenset(s): r2(d, y, [x for a in s for x in G[a]]) for k in range(4) for s in itertools.combinations(G, k)}
    row = {"sonuc": y, "il_SE_R2": v[frozenset()], "toplam_R2": v[frozenset(G)]}
    for a in G:
        top = 0
        for k in range(3):
            for s in itertools.combinations([b for b in G if b != a], k):
                top += math.factorial(k) * math.factorial(2 - k) / 6 * (v[frozenset(s) | {a}] - v[frozenset(s)])
        row[a + "_%"] = 100 * top / (row["toplam_R2"] - row["il_SE_R2"])
    shp.append(row)
shp = pd.DataFrame(shp).round(3)
shp.to_csv(SONUC / "ilce_diger_shapley.csv", index=False, encoding="utf-8")
print("\nİL İÇİ SHAPLEY (il SE sonrası açıklanan farkın bölüşümü)")
print(shp.to_string(index=False))

# yeşil erişim: ham etki (SMR, il SE + eğitim + göç + yükseklik + yoğunluk + kavşak)
sub = d.dropna(subset=["smr"] + MEKAN + KONT)
m = smf.wls("smr ~ yesil300 + yukseklik + ln_yogunluk + ln_kavsak + egitim + artis + C(il)", sub, weights=sub.beklenen_olum_2025) \
    .fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
print("\nHAM (SMR):", {k: f"{v:+.5f} (p={m.pvalues[k]:.3f})" for k, v in m.params.items() if not k.startswith("C(")})
print("→ yeşil erişimde +10 puan: SMR", f"{10 * m.params['yesil300']:+.4f}", "| +1 yıl kadın eğitimi:", f"{m.params['egitim']:+.4f}")
pd.DataFrame({"katsayi": m.params, "p": m.pvalues}).filter(regex="^(?!C\\()", axis=0).to_csv(SONUC / "ilce_diger_ham_smr.csv", encoding="utf-8")
