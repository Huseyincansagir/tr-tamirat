"""
Pilot ilçe seçimi — veriye dayalı
================================
Girdi : 03_VERI/islenmis/ilce_paneli_genis.csv (ilce_diger_sonuclar_analiz.py), 03_VERI/islenmis/ilce_paneli.gpkg
Çıktı : 05_ANALIZ/sonuclar/pilot_*.csv, 04_HARITA/pilot_ilceler.png|svg

Pilot türleri
  1. Megakent karşılaştırma çifti (İstanbul): kadın eğitimi farkı < 0,5 yıl ve 15-49 kadın nüfusu benzer (oran < 2),
     yaşanan bina yüksekliği ve yeşil erişim farkı en büyük çiftler → "doğal karşılaştırma"
  2. Anadolu karşılaştırması: Kayseri (en dikey il) ve Konya (yatay, kültürel olarak benzer) merkez ilçeleri
  3. Deprem sonrası yeniden inşa: 6 Şubat 2023'te en ağır etkilenen il merkez ilçeleri (GHSL 2018 = deprem öncesi durum)
  4. Geleneksel doku referansı: Safranbolu, Beypazarı, Ödemiş (Birgi), Göynük, Mudurnu, Taraklı
  5. Pozitif sapma: il içinde, eğitim ve göç sabitken doğurganlığı beklenenden yüksek, ölümlülüğü beklenenden düşük ilçeler
"""
import itertools
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 230)
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
SONUC = KOK / "05_ANALIZ" / "sonuclar"
d = pd.read_csv(IS / "ilce_paneli_genis.csv", dtype={"ilce_kod": str})
GOSTER = ["il", "ilce_ad_tuik", "nufus_2025", "tdh_ilce", "smr", "egitim", "yukseklik", "pay_h15p", "yesil300", "kavsak_km2_yapili",
          "tek_kisi_pay", "k2534_bekar_pay"]

# 1) İstanbul çiftleri
ist = d[d.il == "İstanbul"].set_index("ilce_ad_tuik")
ciftler = []
for a, b in itertools.combinations(ist.index, 2):
    x, y = ist.loc[a], ist.loc[b]
    if abs(x.egitim - y.egitim) < 0.5 and max(x.kadin_15_49, y.kadin_15_49) / min(x.kadin_15_49, y.kadin_15_49) < 2:
        ciftler.append({"ilce_a": a, "ilce_b": b, "egitim_fark": round(abs(x.egitim - y.egitim), 2),
                        "yukseklik_fark": round(abs(x.yukseklik - y.yukseklik), 1), "yesil_fark": round(abs(x.yesil300 - y.yesil300), 1),
                        "skor": abs(x.yukseklik - y.yukseklik) / ist.yukseklik.std() + abs(x.yesil300 - y.yesil300) / ist.yesil300.std()})
ciftler = pd.DataFrame(ciftler).sort_values("skor", ascending=False)
ciftler.head(10).to_csv(SONUC / "pilot_istanbul_ciftleri.csv", index=False, encoding="utf-8")
print("İSTANBUL — en iyi karşılaştırma çiftleri (eğitim benzer, biçim farklı)")
print(ciftler.head(8).to_string(index=False))

# 2-4) aday listeleri
ADAY = {
    "Anadolu: Kayseri (dikey)": ("Kayseri", ["MELİKGAZİ", "KOCASİNAN", "TALAS"]),
    "Anadolu: Konya (yatay)": ("Konya", ["SELÇUKLU", "MERAM", "KARATAY"]),
    "Deprem: Hatay": ("Hatay", ["ANTAKYA", "DEFNE", "İSKENDERUN"]),
    "Deprem: Kahramanmaraş": ("Kahramanmaraş", ["ONİKİŞUBAT", "DULKADİROĞLU"]),
    "Deprem: Malatya": ("Malatya", ["BATTALGAZİ", "YEŞİLYURT"]),
    "Referans doku": (None, ["SAFRANBOLU", "BEYPAZARI", "ÖDEMİŞ", "GÖYNÜK", "MUDURNU", "TARAKLI"]),
}
satir = []
for grup, (il, adlar) in ADAY.items():
    sec = d[d.ilce_ad_tuik.isin(adlar) & ((d.il == il) if il else True)]
    for _, r in sec.iterrows():
        satir.append({"grup": grup, **{k: r[k] for k in GOSTER}})
aday = pd.DataFrame(satir)
for c in GOSTER[2:]:
    aday[c] = aday[c].astype(float).round(2)
aday.to_csv(SONUC / "pilot_adaylar.csv", index=False, encoding="utf-8")
print("\nADAYLAR")
print(aday.to_string(index=False))

# 5) pozitif sapma
sub = d.dropna(subset=["tdh_ilce", "smr", "egitim", "artis", "yukseklik"]).copy()
for y, w in [("tdh_ilce", "kadin_15_49"), ("smr", "beklenen_olum_2025")]:
    m = smf.wls(f"{y} ~ egitim + artis + C(il)", sub, weights=sub[w]).fit()
    sub[f"{y}_artik"] = m.resid
sub["z_tdh"] = sub.tdh_ilce_artik / sub.tdh_ilce_artik.std()
sub["z_smr"] = -sub.smr_artik / sub.smr_artik.std()
sub["pozitif_skor"] = sub.z_tdh + sub.z_smr
poz = sub[sub.kadin_15_49 > 20000].sort_values("pozitif_skor", ascending=False)
poz[["il", "ilce_ad_tuik", "pozitif_skor", "z_tdh", "z_smr"] + GOSTER[2:]].head(15).round(2) \
    .to_csv(SONUC / "pilot_pozitif_sapma.csv", index=False, encoding="utf-8")
print("\nPOZİTİF SAPMA (eğitim ve göç sabitken il içinde beklenenden yüksek doğurganlık + düşük ölümlülük; 20 bin+ kadın 15-49)")
print(poz[["il", "ilce_ad_tuik", "pozitif_skor", "z_tdh", "z_smr", "yukseklik", "yesil300", "egitim"]].head(12).round(2).to_string(index=False))
print("\nPozitif sapma ilk 50 ilçe ile diğerlerinin ortalama mekân farkı:")
ust = poz.head(50)
print(pd.DataFrame({"ilk50": ust[["yukseklik", "pay_h15p", "yesil300", "kavsak_km2_yapili", "egitim"]].mean(),
                    "diger": poz.iloc[50:][["yukseklik", "pay_h15p", "yesil300", "kavsak_km2_yapili", "egitim"]].mean()}).round(2))

# harita
g = gpd.read_file(IS / "ilce_paneli.gpkg")[["ilce_kod", "il", "ilce_ad_tuik", "geometry"]]
g["ilce_kod"] = g.ilce_kod.astype(str)
g = g.to_crs("+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m")
renk = {"İstanbul çifti": "#2a78d6", "Anadolu": "#eb6834", "Deprem": "#e34948", "Referans doku": "#1baf7a", "Pozitif sapma": "#eda100"}
# Son seçim (gerekçeler 09_RAPORLAR/08_pilot_secimi.md'de): İstanbul'da eğitimi neredeyse aynı (fark 0,09 yıl) ama
# biçimi çok farklı Fatih–Silivri çifti; Anadolu'da eğitimi benzer (9,4–9,3 yıl), yüksekliği farklı Kocasinan–Meram çifti
SECIM = {("İstanbul", "FATİH"): "İstanbul çifti", ("İstanbul", "SİLİVRİ"): "İstanbul çifti",
         ("Kayseri", "KOCASİNAN"): "Anadolu", ("Konya", "MERAM"): "Anadolu",
         ("Hatay", "ANTAKYA"): "Deprem", ("Kahramanmaraş", "ONİKİŞUBAT"): "Deprem",
         ("Karabük", "SAFRANBOLU"): "Referans doku", ("Ankara", "BEYPAZARI"): "Referans doku",
         ("İstanbul", "BAŞAKŞEHİR"): "Pozitif sapma", ("Bursa", "NİLÜFER"): "Pozitif sapma"}
etiket = {d[(d.il == il) & (d.ilce_ad_tuik == ad)].ilce_kod.iloc[0]: t for (il, ad), t in SECIM.items()}
secim_tablo = d[[(il, ad) in SECIM for il, ad in zip(d.il, d.ilce_ad_tuik)]].copy()
secim_tablo["pilot_turu"] = [SECIM[(il, ad)] for il, ad in zip(secim_tablo.il, secim_tablo.ilce_ad_tuik)]
secim_tablo[["pilot_turu"] + GOSTER].round(2).to_csv(SONUC / "pilot_secim_son.csv", index=False, encoding="utf-8")
print(secim_tablo[["pilot_turu"] + GOSTER].round(2).to_string(index=False))
g["pilot"] = g.ilce_kod.map(etiket)
fig, ax = plt.subplots(figsize=(14, 7.2), dpi=150)
fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.04)
g.plot(ax=ax, color="#ece9e2", edgecolor="white", linewidth=0.2)
g.dissolve(by="il").boundary.plot(ax=ax, color="#9a9893", linewidth=0.3)
for t, c in renk.items():
    s = g[g.pilot == t]
    if len(s):
        s.plot(ax=ax, color=c, edgecolor="#333", linewidth=0.4)
for _, r in g[g.pilot.notna()].iterrows():
    p = r.geometry.representative_point()
    ax.annotate(r.ilce_ad_tuik.title(), (p.x, p.y), fontsize=6, ha="center", va="bottom",
                xytext=(0, 3), textcoords="offset points", bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=0.4))
ax.set_axis_off()
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c, label=t) for t, c in renk.items()], loc="lower left", frameon=False, fontsize=8, ncol=5)
fig.text(0.01, 0.94, "Önerilen pilot ilçeler", fontsize=17, fontweight="bold")
fig.text(0.01, 0.905, "10 pilot ilçe: İstanbul karşılaştırma çifti (Fatih–Silivri), Anadolu çifti (Kocasinan–Meram), deprem bölgesi, geleneksel doku ve pozitif sapma",
         fontsize=9, color="#52514e")
for uz in ("png", "svg"):
    fig.savefig(KOK / "04_HARITA" / f"pilot_ilceler.{uz}", facecolor="#fcfcfb")
print("harita yazıldı")
