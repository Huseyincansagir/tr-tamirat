"""
Kentsel Stres Yükü (KSY) — 973 ilçe bileşik göstergesi ve sınaması (Faz 4 · Rapor 1)
===================================================================================
Ölçülebilen yedi etken, ilçeler arası yüzdelik puana çevrilir (0–100, yüksek = daha çok stres yükü) ve eşit
ağırlıkla ortalanır:
  1 PM2.5 (ACAG, 2022–2024)                 2 yaz gündüz yüzey sıcaklığı (MODIS, Temmuz–Ağustos 2023–2024)
  3 ana yola 100 m içinde yaşayan nüfus payı  4 300 m içinde yapılı alan payı (WorldCover 2021)
  5 ağaç ve yeşil eksikliği (WorldCover ağaç ve yeşil örtü, 300 m; iki göstergenin yüzdelik ortalaması)
  6 yaşanan bina yüksekliği (GHSL 2018)      7 yaşanan yoğunluk (GHSL 2020, kişi/ha, Σp²/Σp)
Tümü nüfus ağırlıklıdır (100 m nüfus hücrelerinden). Endeks yalnızca mekân ve çevre göstergelerinden oluşur;
sonuç göstergeleri (ölümlülük, intihar, mutluluk) endekse girmez, sınamada kullanılır.

Sınama 1 (ilçe, n = 973): SMR z ~ KSY z + kadın eğitimi + nüfus artışı (+ ln yoğunluk) (+ kent merkezi payı + 65+ payı)
                          + il sabit etkisi; nüfus ağırlıklı WLS, il kümelenmiş SH (fue_ilce_gecerlilik.py ile aynı kurgu).
Sınama 2 (il, n = 81):    intihar 2014–2018 (Poisson, kişi-yıl ofseti, sağlam SH), mutluluk 2013 ve İLYE 2015 algı
                          göstergeleri (EKK, HC3) ~ il KSY z + kadın eğitim süresi + ln kişi başı GSYH + 65+ payı + doğu.

Girdi : 03_VERI/islenmis/ilce_fue_lite.csv, ilce_uydu.csv, ilce_paneli_genis.csv, il_paneli_2025.csv
        05_ANALIZ/sonuclar/stres_il_dis_veri.csv, stres_turkiye_ab.csv (stres_veri.py)
Çıktı : 05_ANALIZ/sonuclar/stres_ilce_endeks.csv, stres_ilce_sinama.csv, stres_ilce_duyarlilik.csv,
        stres_il_veri.csv, stres_il_sinama.csv, stres_turkiye_yayginlik.csv
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/stres_endeks.py
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
SON = KOK / "05_ANALIZ" / "sonuclar"

# --- 1. veri -----------------------------------------------------------------------------------------------------
f = pd.read_csv(IS / "ilce_fue_lite.csv")
u = pd.read_csv(IS / "ilce_uydu.csv")[["gid", "yesil300w"]]
p = pd.read_csv(IS / "ilce_paneli_genis.csv", dtype={"ilce_kod": str})
PK = ["gid", "ibbs3_kod", "yasanan_yogunluk", "smr", "egitim", "artis", "ln_yogunluk", "merkez_pay", "yasli_pay",
      "beklenen_olum_2025", "olum_2025", "tek_kisi_pay", "nufus_65p", "yuksek_pay15" if "yuksek_pay15" in p else "pay_h15p"]
d = f.merge(u, on="gid").merge(p[PK], on="gid")
print("ilçe:", len(d), "· eksik:", d[["pm25", "lst", "anayol100", "yapili300", "agac300", "yesil300w", "yukseklik_m",
                                     "yasanan_yogunluk", "smr"]].isna().sum().sum())

BIL = [  # (kod, ad, yön, değişkenler)
    ("pm25", "PM2.5", +1, ["pm25"]),
    ("isi", "Yaz yüzey sıcaklığı", +1, ["lst"]),
    ("anayol", "Ana yol yakınlığı", +1, ["anayol100"]),
    ("yapili", "Yapılı alan payı", +1, ["yapili300"]),
    ("yesilsiz", "Ağaç ve yeşil eksikliği", -1, ["agac300", "yesil300w"]),
    ("yukseklik", "Bina yüksekliği", +1, ["yukseklik_m"]),
    ("yogunluk", "Yaşanan yoğunluk", +1, ["yasanan_yogunluk"]),
]
BK = [b[0] for b in BIL]


def yuzdelik(s, yon):
    r = s.rank(pct=True) * 100
    return r if yon > 0 else 100 - r


for k, ad, yon, deg in BIL:
    d["s_" + k] = pd.concat([yuzdelik(d[v], yon) for v in deg], axis=1).mean(axis=1)
d["KSY"] = d[["s_" + k for k in BK]].mean(axis=1)

# duyarlılık türleri
w = d.nufus_2025


def nufus_yuzdelik(s, yon):
    """nüfus ağırlıklı yüzdelik: Türkiye nüfusunun yüzde kaçı daha düşük değerli ilçelerde yaşıyor"""
    o = s.sort_values(kind="mergesort")
    c = (w.loc[o.index].cumsum() - w.loc[o.index] / 2) / w.sum() * 100
    r = c.reindex(s.index)
    return r if yon > 0 else 100 - r


def kirp_z(s):
    s = s.clip(s.quantile(0.01), s.quantile(0.99))
    return (s - s.mean()) / s.std(ddof=0)


ZD = {"yasanan_yogunluk": np.log}
for k, ad, yon, deg in BIL:
    d["n_" + k] = pd.concat([nufus_yuzdelik(d[v], yon) for v in deg], axis=1).mean(axis=1)
    d["z_" + k] = pd.concat([yon * kirp_z(ZD.get(v, lambda x: x)(d[v])) for v in deg], axis=1).mean(axis=1)
d["KSY_nufus"] = d[["n_" + k for k in BK]].mean(axis=1)
d["KSY_z"] = d[["z_" + k for k in BK]].mean(axis=1)
d["KSY_cevre"] = d[["s_" + k for k in ["pm25", "isi", "anayol", "yesilsiz"]]].mean(axis=1)
d["KSY_bicim"] = d[["s_" + k for k in ["yapili", "yukseklik", "yogunluk", "anayol"]]].mean(axis=1)
for k in BK:
    d["KSY_eksi_" + k] = d[["s_" + j for j in BK if j != k]].mean(axis=1)
# birinci temel bileşen ağırlıkları (z puanlarından)
Z = d[["z_" + k for k in BK]]
deg_, vek = np.linalg.eigh(np.corrcoef(Z.T.values))
v1 = vek[:, -1] * np.sign(vek[:, -1].sum())
d["KSY_pca"] = ((Z - Z.mean()) / Z.std(ddof=0)).values @ v1
PCA = pd.Series(v1, index=BK)
print("\nPCA 1. bileşen payı: %.1f%% · ağırlıklar:" % (100 * deg_[-1] / deg_.sum()), PCA.round(2).to_dict())

print("\nKSY dağılımı:", d.KSY.describe().round(1).to_dict())
print("Bileşenler arası Spearman ρ:\n", d[["s_" + k for k in BK]].corr("spearman").round(2).to_string())
rho = {"C_lite_v2": d.KSY.corr(d.C_lite_v2, method="spearman"), "E_lite": d.KSY.corr(d.E_lite, method="spearman"),
       "KSY_nufus": d.KSY.corr(d.KSY_nufus, method="spearman"), "KSY_z": d.KSY.corr(d.KSY_z, method="spearman"),
       "KSY_pca": d.KSY.corr(d.KSY_pca, method="spearman")}
print("KSY ile Spearman ρ:", {k: round(v, 2) for k, v in rho.items()})

ENDEKS_KOL = ["gid", "ilce_kod", "il", "ilce_ad_tuik", "nufus_2025", "pm25", "lst", "anayol100", "yapili300", "agac300",
              "yesil300w", "yukseklik_m", "yasanan_yogunluk"] + ["s_" + k for k in BK] + \
             ["KSY", "KSY_nufus", "KSY_z", "KSY_cevre", "KSY_bicim", "KSY_pca", "C_lite_v2", "E_lite", "smr"]
d["KSY_dilim"] = pd.qcut(d.KSY, 5, labels=[1, 2, 3, 4, 5]).astype(int)
d[ENDEKS_KOL + ["KSY_dilim"]].to_csv(SON / "stres_ilce_endeks.csv", index=False, encoding="utf-8")

# pilot ilçeler: adlar koddan değil TÜİK ilçe adından alınır (önceki sürümde kod–ad eşlemesi kaymıştı)
PILOT = [1327, 1622, 2050, 1829, 1863, 1827, 2080, 2085, 1587, 1187]
pil = d[d.ilce_kod.astype(int).isin(PILOT)].assign(ad=lambda x: x.ilce_ad_tuik)
assert len(pil) == 10 and {"FATİH", "SİLİVRİ", "ANTAKYA", "SAFRANBOLU"} <= set(pil.ad)
print("\nPilot ilçeler:\n", pil[["ad", "KSY", "KSY_dilim"] + ["s_" + k for k in BK] + ["smr"]].sort_values("KSY").round(1).to_string(index=False))
print("\nEn yüksek KSY (10):\n", d.nlargest(10, "KSY")[["il", "ilce_ad_tuik", "KSY", "nufus_2025"]].round(1).to_string(index=False))
print("En düşük KSY (10):\n", d.nsmallest(10, "KSY")[["il", "ilce_ad_tuik", "KSY", "nufus_2025"]].round(1).to_string(index=False))
print("En kalabalık 15 ilçe:\n", d.nlargest(15, "nufus_2025")[["il", "ilce_ad_tuik", "KSY", "KSY_dilim"]].round(1).to_string(index=False))
dil = d.groupby("KSY_dilim").apply(lambda g: pd.Series({"ilce": len(g), "nufus_pay": g.nufus_2025.sum() / w.sum() * 100,
                                                        "smr_agirlikli": np.average(g.smr, weights=g.beklenen_olum_2025)}))
print("Beşte birlik dilimler:\n", dil.round(2).to_string())


# --- 2. Türkiye'de yaygınlık (nüfus ağırlıklı, ilçe ortalamalarından) [H] -----------------------------------------
def nap(kosul):
    return float(w[kosul].sum() / w.sum() * 100)


def nort(s):
    return float(np.average(s, weights=w))


il25 = pd.read_csv(IS / "il_paneli_2025.csv")
YG = [
    ("Hava", "PM2.5, nüfus ağırlıklı ilçe ortalaması (µg/m³)", nort(d.pm25), "2022–2024", "ACAG V6.GL.03; ilce_uydu.csv", "[H]"),
    ("Hava", "DSÖ kılavuz değeri 5 µg/m³'ü aşan ilçelerde yaşayan nüfus (%)", nap(d.pm25 > 5), "2022–2024", "ACAG; DSÖ 2021", "[H]"),
    ("Hava", "AB 2030 sınırı 10 µg/m³'ü aşan ilçelerde yaşayan nüfus (%)", nap(d.pm25 > 10), "2022–2024", "ACAG; AB 2024/2881", "[H]"),
    ("Hava", "DSÖ ara hedefi 15 µg/m³'ü aşan ilçelerde yaşayan nüfus (%)", nap(d.pm25 > 15), "2022–2024", "ACAG; DSÖ 2021", "[H]"),
    ("Hava", "AB'nin bugünkü sınırı 25 µg/m³'ü aşan ilçelerde yaşayan nüfus (%)", nap(d.pm25 > 25), "2022–2024", "ACAG; AB 2008/50", "[H]"),
    ("Isı", "Yaz gündüz yüzey sıcaklığı, nüfus ağırlıklı (°C)", nort(d.lst), "Tem–Ağu 2023–2024", "MODIS MYD11A2; ilce_uydu.csv", "[H]"),
    ("Isı", "Yaz yüzey sıcaklığı 45 °C'yi aşan ilçelerde yaşayan nüfus (%)", nap(d.lst > 45), "Tem–Ağu 2023–2024", "MODIS", "[H]"),
    ("Trafik ve gürültü", "Ana yola 100 m içinde yaşayan nüfus (%)", nort(d.anayol100), "2025 OSM, 2020 GHSL", "ilce_fue_lite.csv", "[H]"),
    ("Yeşil", "300 m çevrede ağaç örtüsü, nüfus ağırlıklı (%)", nort(d.agac300), "2021", "ESA WorldCover", "[H]"),
    ("Yeşil", "Ağaç örtüsü %10'un altında olan ilçelerde yaşayan nüfus (%)", nap(d.agac300 < 10), "2021", "ESA WorldCover", "[H]"),
    ("Yapılı çevre", "300 m çevrede yapılı alan, nüfus ağırlıklı (%)", nort(d.yapili300), "2021", "ESA WorldCover", "[H]"),
    ("Yükseklik", "Ortalaması ≥15 m (≈5+ kat) olan 100 m hücrelerde yaşayan nüfus (%)", nort(d.pay_h15p), "2018/2020", "GHSL R2023A", "[H]"),
    ("Yükseklik", "Yaşanan bina yüksekliği, nüfus ağırlıklı (m)", nort(d.yukseklik_m), "2018", "GHSL R2023A", "[H]"),
    ("Yoğunluk", "Yaşanan yoğunluk, nüfus ağırlıklı (kişi/ha)", nort(d.yasanan_yogunluk), "2020", "GHSL R2023A", "[H]"),
    ("Yalnızlık", "Tek kişilik hane payı (%)", float(il25.hane_tek_kisi.sum() / il25.hane_sayisi_2025.sum() * 100), "2025",
     "TÜİK İstatistiklerle Aile 2025 (il_paneli_2025.csv)", "[H]"),
]
AB = pd.read_csv(SON / "stres_turkiye_ab.csv")
for _, r in AB.iterrows():
    YG.append(("EU-SILC (Türkiye)", r.gosterge, r.tr_son, str(int(r.tr_son_yil)), f"Eurostat {r.veri_seti}; AB-27 aynı yıl {r.ab27_ayni_yil:.1f}", "[D]"))
DIS = [  # arşiv tablolarından ve birincil yayınlardan derlenen ulusal değerler (03_VERI/ham/stres/kaynaklar.md)
    ("Güvenlik", "Gece yalnız yürürken kendini güvende hissedenler (%)", 57.08, "2017", "TÜİK YMA, istab_id=938 (Wayback)", "[D]"),
    ("İşe gidiş", "Çalışanların günlük ulaşım ve belirlenmemiş zamanı (dk)", 82, "2014–15", "TÜİK Zaman Kullanım Araştırması, istab_id=2402", "[D]"),
    ("İşe gidiş", "İstanbul şehir merkezi trafik sıkışıklığı (%)", 62.0, "2025", "TomTom Traffic Index", "[İ]"),
    # Falchi ve ark. 2016, Sci Adv 2:e1600377, Tablo 2 (PMC4928945 tam metninden okundu; 03_VERI/ham/stres/literatur/)
    ("Gece ışığı", "Işık kirli gökyüzü altında yaşayan nüfus (%; yapay parlaklık >14 µcd/m²)", 97.8, "2015 verisi", "Falchi ve ark. 2016, Tablo 2", "[D]"),
    ("Gece ışığı", "Samanyolu'nu göremeyen nüfus (%; >688 µcd/m²)", 49.9, "2015 verisi", "Falchi ve ark. 2016, Tablo 2", "[D]"),
    ("Gece ışığı", "Gözün karanlığa uyum sağlayamadığı gökyüzü altındaki nüfus (%; >3.000 µcd/m²)", 24.3, "2015 verisi",
     "Falchi ve ark. 2016, Tablo 2", "[D]"),
]
# proje ana gösterge tablosundan (03_VERI/islenmis/turkiye_temel_gostergeler.csv): stresle ilgili en güncel ulusal değerler
TG = pd.read_csv(IS / "turkiye_temel_gostergeler.csv", dtype={"yil": str})
TGS = [  # (etken, Türkçe ad, tablo göstergesinin başı, yıl, coğrafya)
    ("Mutluluk", "Kendini mutlu beyan edenler, 18+ (%)", "Kendini mutlu beyan edenler", "2025", "Türkiye"),
    ("Mutluluk", "Kendini mutlu beyan edenler, 18+ (%)", "Kendini mutlu beyan edenler", "2010", "Türkiye"),
    ("Mutluluk", "Kendini mutsuz beyan edenler, 18+ (%)", "Kendini mutsuz beyan edenler", "2025", "Türkiye"),
    ("Hava", "Yıllık ortalama PM2.5 maruziyeti, DSÖ model tahmini (µg/m³)", "Yıllık ortalama PM2.5 maruziyeti (model", "2023", "Türkiye"),
    ("Yalnızlık", "Sık sık yalnız hissedenler, 18–70 (%; çevrimiçi anket)", "Sık sık yalnız hissedenler, 18-70", "2022", "Türkiye"),
    ("Yalnızlık", "İhtiyaç anında güvenebileceği birinin olması, 16+ (%)", "İhtiyaç anında güvenebileceği", "2022", "Türkiye"),
    ("Sağlık sonucu", "Kaba intihar hızı (yüz binde)", "Kaba intihar hızı (kaynaklar: 5,35", "2025", "Türkiye"),
    ("Sağlık sonucu", "Depresif belirti (PHQ-8), 15+ (%)", "Depresif belirti (PHQ-8, son 2 hafta)", "2019", "Türkiye"),
    ("Sağlık sonucu", "Antidepresan tüketimi (günlük doz / 1.000 kişi)", "Antidepresan tüketimi", "2024", "Türkiye"),
    ("Sağlık sonucu", "Antidepresan tüketimi (günlük doz / 1.000 kişi)", "Antidepresan tüketimi", "2010", "Türkiye"),
    ("Sağlık sonucu", "Son 12 ayda hipertansiyon (beyan), 15+ (%)", "Son 12 ayda hipertansiyon", "2025", "Türkiye"),
    ("Sağlık sonucu", "İş dışında aerobik aktivite yapmayanlar, 15+ (%)", "İşle ilgili olmayan aerobik", "2025", "Türkiye"),
]
for et, ad, bas_, yil_, cog in TGS:
    r = TG[TG.gosterge.str.startswith(bas_) & (TG.yil == yil_) & (TG.cografya == cog)]
    assert len(r) == 1, (bas_, yil_, len(r))
    r = r.iloc[0]
    DIS.append((et, ad, float(r.deger), yil_, r.kaynak, "[D]" if r.guven_notu == "birincil" else "[İ]"))
DIS.append(("Sağlık sonucu", "Kaba intihar hızı (yüz binde)", 4.12, "2019", "TÜİK, istab_id=1594 (Wayback)", "[D]"))
YG += DIS
YGT = pd.DataFrame(YG, columns=["etken", "gosterge", "deger", "yil", "kaynak", "isaret"])
YGT.to_csv(SON / "stres_turkiye_yayginlik.csv", index=False, encoding="utf-8")
print("\nTürkiye'de yaygınlık:\n", YGT[["etken", "gosterge", "deger", "yil", "isaret"]].round(2).to_string(index=False))


# --- 3. ilçe sınaması: SMR -------------------------------------------------------------------------------------------
def yz(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "†" if p < 0.10 else ""


MODEL = [("temel", "egitim + artis"), ("+ ln yoğunluk", "egitim + artis + ln_yogunluk"),
         ("+ kentsellik ve yaş yapısı", "egitim + artis + ln_yogunluk + merkez_pay + yasli_pay")]
sub = d.dropna(subset=["smr", "egitim", "artis", "ln_yogunluk", "merkez_pay", "yasli_pay"]).copy()
sub["smr_z"] = (sub.smr - sub.smr.mean()) / sub.smr.std(ddof=0)
TEST = ["KSY"] + ["s_" + k for k in BK] + ["KSY_nufus", "KSY_z", "KSY_pca", "KSY_cevre", "KSY_bicim"] + \
       ["KSY_eksi_" + k for k in BK] + ["C_lite_v2"]
sat = []
for x in TEST:
    sub[x + "_z"] = (sub[x] - sub[x].mean()) / sub[x].std(ddof=0)
    for mad, kont in MODEL:
        m = smf.wls(f"smr_z ~ {x}_z + {kont} + C(il)", sub, weights=sub.nufus_2025).fit(
            cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
        # ham ölçek: KSY'de 10 puan başına SMR değişimi (yüzde puan)
        mh = smf.wls(f"smr ~ {x} + {kont} + C(il)", sub, weights=sub.nufus_2025).fit(
            cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
        sat.append({"endeks": x, "model": mad, "beta": m.params[x + "_z"], "sh": m.bse[x + "_z"], "p": m.pvalues[x + "_z"],
                    "ga_alt": m.conf_int().loc[x + "_z", 0], "ga_ust": m.conf_int().loc[x + "_z", 1],
                    "smr_10puan": 10 * mh.params[x] if not x.startswith(("KSY_z", "KSY_pca", "C_lite")) else np.nan,
                    "n": int(m.nobs), "yildiz": yz(m.pvalues[x + "_z"])})
# karşılaştırma: il sabit etkisi olmadan (iller arası farklar da katılınca ilişki ne oluyor?)
for x in ["KSY", "C_lite_v2"]:
    m = smf.wls(f"smr_z ~ {x}_z + egitim + artis", sub, weights=sub.nufus_2025).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
    sat.append({"endeks": x, "model": "il sabit etkisi yok", "beta": m.params[x + "_z"], "sh": m.bse[x + "_z"],
                "p": m.pvalues[x + "_z"], "ga_alt": m.conf_int().loc[x + "_z", 0], "ga_ust": m.conf_int().loc[x + "_z", 1],
                "smr_10puan": np.nan, "n": int(m.nobs), "yildiz": yz(m.pvalues[x + "_z"])})
T = pd.DataFrame(sat)
# bütün bileşenler aynı modelde (hangisi birlikte ayakta kalıyor?)
for mad, kont in MODEL:
    m = smf.wls(f"smr_z ~ {' + '.join('s_' + k + '_z' for k in BK)} + {kont} + C(il)", sub, weights=sub.nufus_2025).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
    for k in BK:
        v = "s_" + k + "_z"
        T.loc[len(T)] = {"endeks": "birlikte:" + k, "model": mad, "beta": m.params[v], "sh": m.bse[v], "p": m.pvalues[v],
                         "ga_alt": m.conf_int().loc[v, 0], "ga_ust": m.conf_int().loc[v, 1], "smr_10puan": np.nan,
                         "n": int(m.nobs), "yildiz": yz(m.pvalues[v])}
T.to_csv(SON / "stres_ilce_sinama.csv", index=False, encoding="utf-8")
print("\nİLÇE SINAMASI — SMR (standartlaştırılmış β; il SE; il kümelenmiş SH; nüfus ağırlıklı)")
print(T.assign(b=T.beta.round(3).astype(str) + T.yildiz).pivot_table(index="endeks", columns="model", values="b", aggfunc="first")
      [[m[0] for m in MODEL]].reindex(T.endeks.unique()).to_string())
print("KSY'de 10 puan başına SMR değişimi:", T[T.endeks == "KSY"][["model", "smr_10puan"]].round(4).to_dict("records"))
# duyarlılık özeti (temel ve geniş model, KSY türleri)
DUY = T[T.endeks.str.startswith(("KSY", "C_lite"))]
DUY.to_csv(SON / "stres_ilce_duyarlilik.csv", index=False, encoding="utf-8")

# --- 4. il düzeyi: intihar, mutluluk, algı göstergeleri --------------------------------------------------------------
ag = d.assign(wk=w).groupby("ibbs3_kod").apply(lambda g: pd.Series(
    {"KSY_il": np.average(g.KSY, weights=g.wk), **{"s_" + k + "_il": np.average(g["s_" + k], weights=g.wk) for k in BK},
     "pm25_il": np.average(g.pm25, weights=g.wk), "agac300_il": np.average(g.agac300, weights=g.wk),
     "yasli65_pay": g.nufus_65p.sum() / g.nufus_2025.sum() * 100,
     "smr_il": g.olum_2025.sum() / g.beklenen_olum_2025.sum(), "ilce_n": len(g)})).reset_index()
dis = pd.read_csv(SON / "stres_il_dis_veri.csv")
il = il25[["il", "ibbs3_kod", "kadin_egitim_suresi_2025", "ln_gsyh", "dogu", "ibbs1", "kisi_basi_oda_2021", "tek_kisi_pay",
           "nufus_yogunlugu_2025"]].merge(ag, on="ibbs3_kod").merge(dis.drop(columns=["il", "ibbs1"]), on="ibbs3_kod")
il["oda_basi_kisi_2021"] = 1 / il.kisi_basi_oda_2021
il["guvensiz_2015"] = 100 - il.gece_guvende_2015
il.to_csv(SON / "stres_il_veri.csv", index=False, encoding="utf-8")
print(f"\nil tablosu: {il.shape}")
print("İl düzeyinde Spearman ρ (KSY_il ile):", {k: round(il.KSY_il.corr(il[k], method="spearman"), 2) for k in
      ["intihar_hiz_2014_2018", "mutlu_2013", "mutsuz_2013", "gurultu_sorunu_2015", "gece_guvende_2015", "pm10_2015",
       "sosyal_iliski_memnun_2015", "smr_il", "otomobil_bin", "oda_basi_kisi_2021", "tek_kisi_pay", "fiyat_gelir_2024"]})

ETKEN_IL = [("KSY_il", "Kentsel stres yükü (il, nüfus ağırlıklı)"), ("pm25_il", "PM2.5"), ("agac300_il", "Ağaç örtüsü"),
            ("s_yogunluk_il", "Yaşanan yoğunluk puanı"), ("s_yukseklik_il", "Bina yüksekliği puanı"),
            ("oda_basi_kisi_2021", "Oda başına kişi (kalabalık)"), ("fiyat_gelir_2024", "Konut fiyatı / gelir"),
            ("tek_kisi_pay", "Tek kişilik hane payı"), ("otomobil_bin", "1.000 kişiye otomobil"),
            ("gurultu_sorunu_2015", "Sokak gürültüsü sorunu (algı)"), ("guvensiz_2015", "Gece güvende hissetmeyen (algı)")]
SONUC_IL = [("intihar", "Kaba intihar hızı 2014–2018", "poisson"), ("intihar12", "Kaba intihar hızı 2012–2018", "poisson"),
            ("mutlu_2013", "Mutlu olanlar 2013 (%)", "ekk"), ("mutsuz_2013", "Mutsuz olanlar 2013 (%)", "ekk"),
            ("gurultu_sorunu_2015", "Sokak gürültüsü sorunu 2015 (%)", "ekk"),
            ("gece_guvende_2015", "Gece güvende hisseden 2015 (%)", "ekk"),
            ("sosyal_iliski_memnun_2015", "Sosyal ilişkilerden memnun 2015 (%)", "ekk"),
            ("smr_il", "SMR 2025 (il)", "ekk")]
KONT = [("kontrollü", "kadin_egitim_suresi_2025 + ln_gsyh + yasli65_pay + dogu"),
        ("+ İBBS-1 SE", "kadin_egitim_suresi_2025 + ln_gsyh + yasli65_pay + C(ibbs1)")]
ils = []
for x, xad in ETKEN_IL:
    for y, yad, tur in SONUC_IL:
        if y == x or (x, y) == ("guvensiz_2015", "gece_guvende_2015"):  # aynı değişkenin iki yüzü
            continue
        for kad, kont in [("ham", "1")] + KONT:
            s = il.dropna(subset=[x, "kadin_egitim_suresi_2025", "ln_gsyh", "yasli65_pay"]).copy()
            s["x_z"] = (s[x] - s[x].mean()) / s[x].std(ddof=0)
            if tur == "poisson":
                a, b = (2014, 2018) if y == "intihar" else (2012, 2018)
                m = smf.glm(f"intihar_n_{a}_{b} ~ x_z + {kont}", s, family=sm.families.Poisson(),
                            offset=np.log(s[f"kisi_yil_{a}_{b}"])).fit(cov_type="HC1")
                b_, lo, hi = np.exp(m.params.x_z), np.exp(m.conf_int().loc["x_z", 0]), np.exp(m.conf_int().loc["x_z", 1])
                birim = "oran oranı (1 SS)"
            else:
                s = s.dropna(subset=[y])
                m = smf.ols(f"{y} ~ x_z + {kont}", s).fit(cov_type="HC3")
                b_, lo, hi = m.params.x_z, m.conf_int().loc["x_z", 0], m.conf_int().loc["x_z", 1]
                birim = "SMR birimi (1 SS)" if y == "smr_il" else "yüzde puan (1 SS)"
            ils.append({"etken": x, "etken_ad": xad, "sonuc": y, "sonuc_ad": yad, "model": kad, "etki": b_, "ga_alt": lo,
                        "ga_ust": hi, "p": m.pvalues.x_z, "birim": birim, "n": int(m.nobs), "yildiz": yz(m.pvalues.x_z)})
IL = pd.DataFrame(ils)
# çoklu karşılaştırma: her model ailesinde (ham / kontrollü / + İBBS-1 SE) Benjamini–Hochberg yanlış keşif oranı
IL["q_bh"] = IL.groupby("model").p.transform(lambda p_: multipletests(p_, method="fdr_bh")[1])
print("\nİl sınaması, BH q < 0,05 kalan ilişkiler (kontrollü ve + İBBS-1 SE):")
print(IL[(IL.q_bh < 0.05) & (IL.model != "ham")][["etken", "sonuc", "model", "etki", "p", "q_bh"]].round(4).to_string(index=False))
IL.to_csv(SON / "stres_il_sinama.csv", index=False, encoding="utf-8")
print("\nİL SINAMASI (intihar: oran oranı / 1 SS; diğerleri: puan / 1 SS; kontroller: kadın eğitim süresi, ln GSYH, 65+, doğu)")
for kad in ["ham", "kontrollü", "+ İBBS-1 SE"]:
    t = IL[IL.model == kad]
    print(f"\n[{kad}]\n", t.assign(e=t.etki.round(3).astype(str) + t.yildiz).pivot_table(
        index="etken", columns="sonuc", values="e", aggfunc="first").reindex([e[0] for e in ETKEN_IL])
          [[s_[0] for s_ in SONUC_IL]].to_string())
print("\nTamam.")
