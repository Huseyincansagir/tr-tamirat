"""
Faz 5 · Rapor 7 — Evin biçimi ile inovasyon, üretkenlik, sağlık, güven ve aile arasındaki ilişkiler (81 il, 973 ilçe)
===============================================================================================================
Konut biçimi (TÜİK Bina ve Konut Nitelikleri 2021, il):
  kat5p_pct   5 ve daha çok katlı binada oturan hane payı (%)
  ort_kat     oturulan binanın ortalama kat sayısı
  kat12_pct   1–2 katlı binada oturan hane payı (%)
  kat34_pct   3–4 katlı binada oturan hane payı (%; Rapor 21 kademe modelinin önerdiği orta yükseklik)
  ort_oda     konut başına oda (konutun büyüklüğü)
  kisi_oda    kişi başı oda (kalabalığın tersi; hane büyüklüğünü de taşır)
  ev_sahibi   ev sahibi hane payı (%)
Sonuçlar:
  Üretkenlik ve inovasyon:
    ln kişi başı GSYH 2024;
    ln ortalama günlük kazanç ve istihdam oranı (İLYE 2015);
    patent ve faydalı model başvurusu / 100 bin (TÜRKPATENT, ilk başvuranın ili, 2021–2025 ortalaması; ln(1+x));
    kurulan şirket / 1.000 (TOBB 2024–2025 ortalaması).
  Sağlık:
    doğuşta yaşam süresi, bebek ölüm hızı (İLYE 2015);
    SMR 2024–2025 (ilçelerden toplanmış);
    kaba intihar hızı 2014–2018 ortalaması.
  Güven ve sosyal sermaye: İLYE 2015 göstergeleri (sosyal ilişki ve sosyal hayat memnuniyeti, gece yalnız yürürken
    güvende hissetme, kamu asayiş memnuniyeti, cinayet / milyon, yerel seçime katılım, sendika ve dernek ilgisi,
    mutluluk).
  Aile: çocuğuyla aynı mahallede ya da daha yakın oturan yaşlı payı; tek kişilik hane; kaba boşanma hızı.
Modeller (standartlaştırılmış β; HC1 SH):
  M0 · ham ilişki
  M1 · + kentleşme (yoğun kent payı, ln yoğunluk) + ortalama eğitim süresi 2025 + doğu kuklası
  M2 · M1 + ln nüfus (kent ölçeği) + ln kişi başı GSYH (GSYH sonucu için yalnız ln nüfus)
  Her modelde 147 test için Benjamini–Hochberg q; duyarlılık: üç büyükşehir hariç, nüfus ağırlıklı, + hane büyüklüğü.
İlçe (973): il içinde GHSL bina yüksekliği → ölüm, doğurganlık, evlenme, boşanma, hane yapısı (il SE, nüfus ağırlıklı,
  il kümelenmiş SH).

Girdi : 03_VERI/islenmis/il_paneli_2025.csv; 03_VERI/ham/stres/il_ilye_2015_gostergeler.csv,
        il_intihar_2000_2018_birlesik.csv; 03_VERI/ham/inovasyon/*.xls (TÜRKPATENT);
        03_VERI/ham/ekonomi/ticaret_tarim/tobb_kurulan_kapanan_sirket_2025-12.xls; 03_VERI/islenmis/ilce_ana_tablo.csv
Çıktı : 03_VERI/islenmis/il_konut_bicimi_tablosu.csv; 05_ANALIZ/sonuclar/konut_bicimi_*.csv;
        05_ANALIZ/grafikler/konut_bicimi_iliskiler.png|svg
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/konut_bicimi_iliskiler.py
"""
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from matplotlib.colors import LinearSegmentedColormap

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"
HAM = KOK / "03_VERI" / "ham"
SON = KOK / "05_ANALIZ" / "sonuclar"
GRAF = KOK / "05_ANALIZ" / "grafikler"
MAVI, TURUNCU, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
YAZI, YAZI_2, YAZI_3, ZEMIN, IZGARA = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e8e7e3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "axes.edgecolor": YAZI_3, "axes.labelcolor": YAZI_2, "xtick.color": YAZI_2, "ytick.color": YAZI_2,
                     "axes.titlesize": 10, "svg.fonttype": "none"})
TRMAP = str.maketrans("çğıiöşüÇĞİIÖŞÜâîû", "CGIIOSUCGIIOSUAIU")


def anahtar(s):
    return str(s).strip().translate(TRMAP).upper().replace(" ", "")


def tr(x, nd=2):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


# ---------------------------------------------------------------- 1. veri
il = pd.read_csv(IS / "il_paneli_2025.csv")
il["k"] = il.il.map(anahtar)
d = il.rename(columns={"ort_kat_2021": "ort_kat", "kisi_basi_oda_2021": "kisi_oda", "ev_sahibi_pct_2021": "ev_sahibi",
                       "ort_oda_2021": "ort_oda"})
d["kat12_pct"] = d.kat1_pct + d.kat2_pct
d["kat34_pct"] = d.kat3_pct + d.kat4_pct

ilye = pd.read_csv(HAM / "stres" / "il_ilye_2015_gostergeler.csv")
d = d.merge(ilye.drop(columns=["il", "endeks_yili", "kaynak_url"]), on="ibbs3_kod", how="left")
nt = pd.read_csv(HAM / "stres" / "il_intihar_2000_2018_birlesik.csv")
nt = nt[nt.yil.between(2014, 2018)].groupby("ibbs3_kod").kaba_intihar_hizi.mean().rename("intihar_hiz")
d = d.merge(nt, on="ibbs3_kod", how="left")


def turkpatent(dosya, ad):
    x = pd.read_excel(HAM / "inovasyon" / dosya, header=None)
    bas = x.index[x.iloc[:, 0].astype(str).str.strip() == "İl kodu"][0]
    yil = x.iloc[bas - 1]
    kol = {j: int(float(yil[j])) for j in range(x.shape[1]) if pd.notna(yil[j]) and str(yil[j]).replace(".0", "").isdigit()}
    v = x.iloc[bas + 1:].copy()
    v = v[v.iloc[:, 0].astype(str).str.strip().str.fullmatch(r"\d{1,2}")]
    out = pd.DataFrame({"k": v.iloc[:, 1].map(anahtar).replace({"AFYON": "AFYONKARAHISAR"})})
    for j, y in kol.items():
        out[f"{ad}_{y}"] = pd.to_numeric(v.iloc[:, j], errors="coerce").fillna(0).values
    return out


pt = turkpatent("patent_basvuru_iller.xls", "patent")
fm = turkpatent("faydali_model_basvuru_iller.xls", "fmodel")
d = d.merge(pt, on="k", how="left").merge(fm, on="k", how="left")
for ad in ("patent", "fmodel"):
    d[f"{ad}_100bin"] = d[[f"{ad}_{y}" for y in range(2021, 2026)]].mean(axis=1) / d.nufus_2025 * 1e5
    d[f"ln_{ad}"] = np.log1p(d[f"{ad}_100bin"])
assert d.patent_100bin.notna().sum() == 81, "TÜRKPATENT il eşleşmesi eksik"

tb = pd.read_excel(HAM / "ekonomi" / "ticaret_tarim" / "tobb_kurulan_kapanan_sirket_2025-12.xls",
                   sheet_name="İLLER ( BİRİKİMLİ)", header=None)
tb.loc[tb.iloc[:, 1].astype(str).str.strip() == "İSTANBUL", 0] = "TR100"   # TOBB dosyasında kod hücresi tarihe dönüşmüş
tb = tb[tb.iloc[:, 0].astype(str).str.match(r"TR[A-Z0-9]{3}$")]
tb = pd.DataFrame({"ibbs3_kod": tb.iloc[:, 0], "sirket_2025": pd.to_numeric(tb.iloc[:, 2]),
                   "sirket_2024": pd.to_numeric(tb.iloc[:, 10])})
d = d.merge(tb, on="ibbs3_kod", how="left")
d["sirket_1000"] = (d.sirket_2024 + d.sirket_2025) / 2 / d.nufus_2025 * 1000
assert d.sirket_1000.notna().sum() == 81, "TOBB il eşleşmesi eksik"

ana = pd.read_csv(IS / "ilce_ana_tablo.csv", dtype={"ilce_kod": str})
smr = ana.groupby("il")[["olum_2024", "olum_2025", "beklenen_olum_2024", "beklenen_olum_2025"]].sum()
smr["smr_il"] = (smr.olum_2024 + smr.olum_2025) / (smr.beklenen_olum_2024 + smr.beklenen_olum_2025)
smr.index = smr.index.map(anahtar)
d = d.merge(smr[["smr_il"]], left_on="k", right_index=True, how="left")
d["ln_kazanc"] = np.log(d.ort_gunluk_kazanc_tl)
d["egitim"] = d.ort_egitim_suresi_2025      # il_paneli'ndeki egitim_yili verinin yılıdır (2025), eğitim ölçüsü değil
d["ln_nufus"] = np.log(d.nufus_2025)
d.drop(columns=[c for c in d.columns if c.startswith(("patent_", "fmodel_")) and c[-4:].isdigit()]) \
    .to_csv(IS / "il_konut_bicimi_tablosu.csv", index=False, encoding="utf-8")

BICIM = {"kat5p_pct": "5+ katlı binada oturan hane (%)", "ort_kat": "Ortalama kat", "kat12_pct": "1–2 katlı binada oturan hane (%)",
         "kat34_pct": "3–4 katlı binada oturan hane (%)",
         "ort_oda": "Konut başına oda", "kisi_oda": "Kişi başı oda", "ev_sahibi": "Ev sahibi hane (%)"}
SONUC = [  # (değişken, ad, grup, iyi yön +1 / −1)
    ("ln_gsyh", "Kişi başı GSYH (ln)", "Üretkenlik ve inovasyon", +1),
    ("ln_kazanc", "Günlük kazanç (ln, 2015)", "Üretkenlik ve inovasyon", +1),
    ("istihdam_orani_pct", "İstihdam oranı (2015)", "Üretkenlik ve inovasyon", +1),
    ("ln_patent", "Patent başvurusu / 100 bin (ln)", "Üretkenlik ve inovasyon", +1),
    ("ln_fmodel", "Faydalı model / 100 bin (ln)", "Üretkenlik ve inovasyon", +1),
    ("sirket_1000", "Kurulan şirket / 1.000", "Üretkenlik ve inovasyon", +1),
    ("dogusta_yasam_suresi_yil", "Doğuşta yaşam süresi (2015)", "Sağlık", +1),
    ("bebek_olum_hizi_binde", "Bebek ölüm hızı (‰, 2015)", "Sağlık", -1),
    ("smr_il", "Standart ölüm oranı (2024–25)", "Sağlık", -1),
    ("intihar_hiz", "İntihar hızı (2014–18)", "Sağlık", -1),
    ("sosyal_iliski_memnuniyeti_pct", "Sosyal ilişki memnuniyeti", "Güven ve sosyal bağ", +1),
    ("sosyal_hayat_memnuniyeti_pct", "Sosyal hayat memnuniyeti", "Güven ve sosyal bağ", +1),
    ("gece_yalniz_yururken_guvende_pct", "Gece yalnız yürürken güvende", "Güven ve sosyal bağ", +1),
    ("kamu_asayis_memnuniyeti_pct", "Asayiş hizmetinden memnuniyet", "Güven ve sosyal bağ", +1),
    ("cinayet_milyonda", "Cinayet / milyon", "Güven ve sosyal bağ", -1),
    ("yerel_secim_katilim_pct", "Yerel seçime katılım", "Güven ve sosyal bağ", +1),
    ("sendika_dernek_ilgi_pct", "Sendika ve dernek ilgisi", "Güven ve sosyal bağ", +1),
    ("mutluluk_duzeyi_pct", "Mutluluk (2015)", "Güven ve sosyal bağ", +1),
    ("yasli_yakin", "Yaşlı çocuğuyla aynı mahallede ya da daha yakın", "Aile", +1),
    ("tek_kisi_pay", "Tek kişilik hane (%)", "Aile", -1),
    ("kaba_bosanma_2025", "Kaba boşanma hızı (‰)", "Aile", -1),
]
M1 = "yogun_kent_pay + ln_yogunluk + egitim + dogu"
KONT = {"M0": "", "M1": M1, "M2": M1 + " + ln_nufus + ln_gsyh"}


def z(s):
    return (s - s.mean()) / s.std(ddof=0)


def yz(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "†" if p < 0.10 else ""


def bh(p):
    """Benjamini–Hochberg q değeri."""
    p = np.asarray(p, float)
    o = np.argsort(p)
    q = p[o] * len(p) / np.arange(1, len(p) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty_like(q)
    out[o] = np.minimum(q, 1)
    return out


def tahmin(veri, y, x, kont, agirlik=None):
    gerek = [y, x] + [v.strip() for v in kont.split("+") if v.strip()] + ([agirlik] if agirlik else [])
    sub = veri.dropna(subset=gerek).copy()
    sub["y_z"], sub["x_z"] = z(sub[y]), z(sub[x])
    f = "y_z ~ x_z" + (f" + {kont}" if kont else "")
    m = (smf.wls(f, sub, weights=sub[agirlik]) if agirlik else smf.ols(f, sub)).fit(cov_type="HC1")
    return m.params["x_z"], m.bse["x_z"], m.pvalues["x_z"], int(m.nobs), m.rsquared


satir = []
for y, yad, grup, yon in SONUC:
    for x, xad in BICIM.items():
        for mad, kont in KONT.items():
            k = kont.replace(" + ln_gsyh", "") if y == "ln_gsyh" else kont
            b, sh, p, n, r2 = tahmin(d, y, x, k)
            satir.append({"sonuc": y, "sonuc_ad": yad, "grup": grup, "iyi_yon": yon, "bicim": x, "bicim_ad": xad,
                          "model": mad, "beta": b, "sh": sh, "p": p, "n": n, "r2": r2})
R = pd.DataFrame(satir)
R["beta_iyi"] = R.beta * R.iyi_yon          # + = konut biçimi değişkeni arttıkça sonuç iyileşiyor
R["q_bh"] = R.groupby("model").p.transform(bh)   # her modelde 21 sonuç × 7 biçim = 147 test
R.round(4).to_csv(SON / "konut_bicimi_iliskiler.csv", index=False, encoding="utf-8")

print("İl düzeyi, standartlaştırılmış β (1 SS konut değişkeni → SS sonuç); M1 = kentleşme + eğitim + doğu; ^ = BH q<0,05:")
t = R[R.model == "M1"].assign(b=lambda q: q.beta.round(2).astype(str) + q.p.map(yz) + np.where(q.q_bh < 0.05, "^", ""))
print(t.pivot_table(index=["grup", "sonuc_ad"], columns="bicim", values="b", aggfunc="first")[list(BICIM)].to_string())
t = R[R.bicim == "kat5p_pct"].assign(b=lambda q: q.beta.round(2).astype(str) + q.p.map(yz))
print("\n5+ kat: M0 ham / M1 / M2 (+ ln nüfus + ln GSYH):")
print(t.pivot_table(index=["grup", "sonuc_ad"], columns="model", values="b", aggfunc="first").to_string())
for mad in KONT:
    print(f"{mad}: BH q < 0,05 kalan ilişki", int((R[R.model == mad].q_bh < 0.05).sum()), "/ 147")

# ---------------------------------------------------------------- 2. duyarlılık
METRO = {"TR100", "TR510", "TR310"}   # İstanbul, Ankara, İzmir
DUY = [("Temel M1", d, M1, None),
       ("Üç büyükşehir hariç", d[~d.ibbs3_kod.isin(METRO)], M1, None),
       ("Nüfus ağırlıklı", d, M1, "nufus_2025"),
       ("+ hane büyüklüğü", d, M1 + " + hane_buyukluk_2025", None)]
dz = []
for y, yad, grup, yon in SONUC:
    for x in ("kat5p_pct", "kat34_pct", "ort_oda", "kisi_oda", "ev_sahibi"):
        for ad, veri, kont, agr in DUY:
            b, sh, p, n, _ = tahmin(veri, y, x, kont, agr)
            dz.append({"sonuc": y, "sonuc_ad": yad, "grup": grup, "bicim": x, "duyarlilik": ad, "beta": b, "p": p, "n": n})
DZ = pd.DataFrame(dz)
DZ.round(4).to_csv(SON / "konut_bicimi_duyarlilik.csv", index=False, encoding="utf-8")
for x in ("kat5p_pct", "kat34_pct", "ort_oda", "kisi_oda", "ev_sahibi"):
    print(f"\nDuyarlılık · {BICIM[x]}:")
    print(DZ[DZ.bicim == x].assign(b=lambda q: q.beta.round(2).astype(str) + q.p.map(yz))
          .pivot_table(index=["grup", "sonuc_ad"], columns="duyarlilik", values="b", aggfunc="first")
          [[a[0] for a in DUY]].to_string())

# kent ölçeği mi, yükseklik mi? inovasyon için ayrıştırma
AY = ["kat5p_pct", "kat12_pct", "ort_oda", "ln_nufus", "ln_yogunluk", "egitim", "yogun_kent_pay"]
ayr = []
for y in ("ln_patent", "ln_fmodel", "sirket_1000", "ln_gsyh", "ln_kazanc"):
    sub = d.dropna(subset=[y] + AY).copy()
    for v in [y] + AY:
        sub[v + "_z"] = z(sub[v])
    m = smf.ols(f"{y}_z ~ " + " + ".join(v + "_z" for v in AY) + " + dogu", sub).fit(cov_type="HC1")
    for v in AY:
        ayr.append({"sonuc": y, "degisken": v, "beta": m.params[v + "_z"], "p": m.pvalues[v + "_z"], "r2": m.rsquared})
AYR = pd.DataFrame(ayr)
AYR.round(4).to_csv(SON / "konut_bicimi_inovasyon_ayristirma.csv", index=False, encoding="utf-8")
print("\nİnovasyon ve üretkenlik: yükseklik mi, ölçek mi, eğitim mi? (hepsi aynı modelde, standartlaştırılmış β)")
print(AYR.assign(b=lambda q: q.beta.round(2).astype(str) + q.p.map(yz)).pivot_table(index="degisken", columns="sonuc",
      values="b", aggfunc="first").loc[AY].to_string())

# ---------------------------------------------------------------- 3. ilçe: il içinde bina yüksekliği
ana["tek_kisi_pay"] = ana.hane_tek_kisi / ana.hane_toplam * 100
ana["genis_pay"] = ana.hane_genis / ana.hane_toplam * 100
ILCE_SONUC = [("smr", "Standart ölüm oranı (2024–25)", "Sağlık", -1),
              ("tdh_ilce", "Toplam doğurganlık hızı", "Aile", +1),
              ("evlenme_hiz", "Kaba evlenme hızı (‰)", "Aile", +1),
              ("bosanma_hiz", "Kaba boşanma hızı (‰)", "Aile", -1),
              ("k3544_bosanmis_pay", "35–44 yaş boşanmış kadın (%)", "Aile", -1),
              ("tek_kisi_pay", "Tek kişilik hane (%)", "Aile", -1),
              ("genis_pay", "Geniş aile hanesi (%)", "Aile", +1),
              ("ort_hane", "Ortalama hane büyüklüğü", "Aile", +1)]
IK = {"il SE": "", "il SE + eğitim, göç": "egitim + artis",
      "il SE + kentsellik, yaş": "egitim + artis + ln_yogunluk + merkez_pay + yasli_pay"}
ilc = []
for y, yad, grup, yon in ILCE_SONUC:
    for kad, kont in IK.items():
        gerek = [y, "yukseklik", "nufus_2025", "egitim", "artis", "ln_yogunluk", "merkez_pay", "yasli_pay"]
        sub = ana.dropna(subset=gerek).copy()
        sub["y_z"], sub["x_z"] = z(sub[y]), z(sub.yukseklik)
        m = smf.wls("y_z ~ x_z" + (f" + {kont}" if kont else "") + " + C(il)", sub, weights=sub.nufus_2025).fit(
            cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.il)[0]})
        ilc.append({"sonuc": y, "sonuc_ad": yad, "grup": grup, "iyi_yon": yon, "model": kad, "beta": m.params["x_z"],
                    "sh": m.bse["x_z"], "p": m.pvalues["x_z"], "n": int(m.nobs),
                    "fiziki_birim": m.params["x_z"] * sub[y].std(ddof=0) / sub.yukseklik.std(ddof=0)})
ILC = pd.DataFrame(ilc)
ILC.round(4).to_csv(SON / "konut_bicimi_ilce_yukseklik.csv", index=False, encoding="utf-8")
YSS = ana.yukseklik.std(ddof=0)
print(f"\nİlçe (n={ILC.n.max()}), il içinde +1 SS bina yüksekliği ({tr(YSS, 1)} m), nüfus ağırlıklı, il kümelenmiş SH:")
print(ILC.assign(b=lambda q: q.beta.round(2).astype(str) + q.p.map(yz) + " (" + (q.fiziki_birim * YSS).round(3).astype(str) + ")")
      .pivot_table(index="sonuc_ad", columns="model", values="b", aggfunc="first")[list(IK)].to_string())

# ---------------------------------------------------------------- 4. grafik
SIRA = [s[1] for s in SONUC]
sutun = [("kat5p_pct", "M0"), ("kat5p_pct", "M1"), ("kat5p_pct", "M2"), ("kat34_pct", "M1"), ("ort_oda", "M1"), ("ev_sahibi", "M1")]
bas = ["5+ kat\nham", "5+ kat\n+ kentleşme,\neğitim", "5+ kat\n+ ölçek,\ngelir", "3–4 kat\n+ kentleşme,\neğitim",
       "Konut başı\noda\n+ kentleşme", "Ev sahibi\n+ kentleşme"]   # kişi başı oda hane büyüklüğüyle r = −0,95: grafikte yok


def sec(s, b, m, c):
    return R[(R.sonuc_ad == s) & (R.bicim == b) & (R.model == m)][c].iloc[0]


Mx = np.array([[sec(s, b, m, "beta_iyi") for b, m in sutun] for s in SIRA])
Px = np.array([[sec(s, b, m, "p") for b, m in sutun] for s in SIRA])
cmap = LinearSegmentedColormap.from_list("a", [TURUNCU, "#f4c3ab", "#efeeea", "#a9c8ee", MAVI])
fig = plt.figure(figsize=(12.6, 8.8))
ax = fig.add_axes([0.235, 0.06, 0.43, 0.77])
ax.imshow(Mx, cmap=cmap, vmin=-0.8, vmax=0.8, aspect="auto")
for i in range(Mx.shape[0]):
    for j in range(Mx.shape[1]):
        v, p = Mx[i, j], Px[i, j]
        ax.text(j, i, f"{v:+.2f}".replace("-", "−").replace(".", ",") + yz(p), ha="center", va="center", fontsize=7.6,
                color="white" if abs(v) > 0.55 else YAZI)
ax.set_xticks(range(len(sutun)))
ax.set_xticklabels(bas, fontsize=7.6)
ax.xaxis.tick_top()
ax.set_yticks(range(len(SIRA)))
ax.set_yticklabels(SIRA, fontsize=8)
gruplar = [s[2] for s in SONUC]
for i in range(1, len(gruplar)):
    if gruplar[i] != gruplar[i - 1]:
        ax.axhline(i - 0.5, color=YAZI_3, lw=1)
ax.axvline(2.5, color=YAZI_3, lw=1)
ax.set_xticks(np.arange(-0.5, len(sutun)), minor=True)
ax.set_yticks(np.arange(-0.5, len(SIRA)), minor=True)
ax.grid(which="minor", color=ZEMIN, lw=2)
ax.tick_params(which="both", length=0)
for s_ in ax.spines.values():
    s_.set_visible(False)
y0 = 0
for g in dict.fromkeys(gruplar):
    n = gruplar.count(g)
    fig.text(0.012, 0.83 - (y0 + n / 2) / len(SIRA) * 0.77, g.replace(" ve ", "\nve "), fontsize=8.4, fontweight="bold",
             color=YAZI_2, va="center", ha="left")
    y0 += n
ax.set_title("81 il · konut değişkeni 1 SS arttıkça sonuç (SS)", loc="left", color=YAZI, fontsize=9.5, pad=52)

# sağ: ilçe il içi yükseklik
ax2 = fig.add_axes([0.825, 0.30, 0.12, 0.53])
I = ILC[ILC.model == "il SE + kentsellik, yaş"].set_index("sonuc_ad").loc[[s[1] for s in ILCE_SONUC]]
yy = np.arange(len(I))[::-1]
bi = I.beta * I.iyi_yon
ax2.axvline(0, color=YAZI_3, lw=0.8)
ax2.errorbar(bi, yy, xerr=1.96 * I.sh, fmt="none", ecolor=IZGARA, elinewidth=3)
ax2.scatter(bi, yy, c=[MAVI if v > 0 else TURUNCU for v in bi], s=30, zorder=3)
for yi, v, p in zip(yy, bi, I.p):
    ax2.text(1.02, yi, f"{v:+.2f}".replace("-", "−").replace(".", ",") + yz(p), va="center", fontsize=7.6, color=YAZI_2,
             transform=ax2.get_yaxis_transform())
ax2.set_yticks(yy)
ax2.set_yticklabels(I.index, fontsize=8)
ax2.set_xlim(-0.45, 0.45)
ax2.set_xticks([-0.4, 0, 0.4])
ax2.set_xticklabels(["−0,4", "0", "+0,4"])
ax2.set_xlabel("SS (+ = iyileşme)", fontsize=8)
ax2.grid(axis="x", color=IZGARA, lw=0.6)
ax2.set_axisbelow(True)
for s_ in ("top", "right"):
    ax2.spines[s_].set_visible(False)
ax2.set_title(f"973 ilçe · aynı il içinde\n+1 SS bina yüksekliği ({tr(YSS, 1)} m)", loc="right", color=YAZI, fontsize=9.5)
fig.text(0.72, 0.22, "İlçe modeli: il sabit etkisi + eğitim, göç,\nyoğunluk, merkez payı, 65+ payı; nüfus\n"
         "ağırlıklı, il kümelenmiş SH; çubuk %95 GA.", fontsize=7.6, color=YAZI_3, va="top")
fig.text(0.012, 0.985, "Evin biçimi ve toplum: inovasyon, sağlık, güven, aile", fontsize=12.5, fontweight="bold",
         color=YAZI, va="top")
fig.text(0.012, 0.955, "Mavi: konut değişkeni arttıkça sonuç iyileşiyor; turuncu: kötüleşiyor (sonucun iyi yönüne çevrilmiş "
         "standartlaştırılmış β). † p<0,10 * <0,05 ** <0,01 *** <0,001; HC1 SH.", fontsize=8.2, color=YAZI_2, va="top")
fig.text(0.012, 0.012, "Kaynak: TÜİK Bina ve Konut Nitelikleri 2021, İLYE 2015, TÜRKPATENT 2021–25, TOBB 2024–25, "
         "il paneli, ilçe ana tablosu (GHSL yükseklik); konut_bicimi_iliskiler.py.", fontsize=7.2, color=YAZI_3)
for uz in ("png", "svg"):
    fig.savefig(GRAF / f"konut_bicimi_iliskiler.{uz}", dpi=200)
print("\nYazıldı: il_konut_bicimi_tablosu.csv, konut_bicimi_{iliskiler,duyarlilik,inovasyon_ayristirma,ilce_yukseklik}.csv, "
      "konut_bicimi_iliskiler.png|svg")
