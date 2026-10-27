"""
H2 — Konut maliyeti evliliği erteler ve doğurganlığı düşürür mü?
================================================================
Girdi : 03_VERI/islenmis/konut_paneli.csv, konut_paneli_kfe_bolge.csv (05_ANALIZ/kod/konut_h2_veri.py üretir)
        03_VERI/islenmis/il_paneli_2025.csv (kiracı payı 2021, kadın eğitim süresi 2025, bölge)
Çıktı : 05_ANALIZ/sonuclar/konut_*.csv, 05_ANALIZ/grafikler/konut_*.png|svg

Ana ölçü: fiyat/gelir = (TCMB konut birim fiyatı, TL/m² × 100 m²) / kişi başı GSYH (TL)
          → "100 m²'lik bir konut, ilin kişi başı yıllık gelirinin kaç katı?"
Tasarım
  1. İl × yıl paneli (76 il, 2011–2025): Y_it = b·ln(F/G)_{i,t-1} + il SE + yıl SE (ya da 12 bölge × yıl SE)
     Standart hata il düzeyinde kümelenmiş (reghdfe tipi serbestlik düzeltmesi). Öncü (t+1) testi, ağırlıklı,
     deprem bölgesi hariç, 2011–2019, il trendi, fiyat ve gelir ayrı, kiracı payı etkileşimi, dağıtılmış gecikme.
  2. Kira/gelir paneli (2019–2025), yaşa özel ilk evlenme hızları (erteleme testi)
  3. KFE bölge paneli (19 bölge, kalite düzeltilmiş endeks): yabani küme bootstrap p-değerleri
  4. Uzun fark (2012→2023 fiyat/gelir değişimi → 2013→2024 sonuç değişimi), 12 bölge SE
  5. 2025 kesiti: fiyat/gelir 2024 → 2025 sonuçları, kadın eğitimi ve 12 bölge kontrollü
Ekolojik (il düzeyi) gözlemsel analiz; bireysel nedensellik iddiası taşımaz.
"""
import os
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)

KOK = Path(__file__).resolve().parents[2]
ISLENMIS = KOK / "03_VERI" / "islenmis"
SONUC = KOK / "05_ANALIZ" / "sonuclar"
GRAFIK = KOK / "05_ANALIZ" / "grafikler"
RNG = np.random.default_rng(2026)
BOOT = 0 if os.environ.get("KONUT_HIZLI") else 1999  # KONUT_HIZLI=1: bootstrap atlanır (grafik denemeleri için)
LN10 = np.log(1.10)  # %10 artışın log karşılığı

# --- 0. Veri -------------------------------------------------------------------------------
p0 = pd.read_csv(ISLENMIS / "konut_paneli.csv")
ip = pd.read_csv(ISLENMIS / "il_paneli_2025.csv")
tr = p0[p0.ibbs3_kod == "TR"].set_index("yil")
p = p0[p0.ibbs3_kod != "TR"].merge(ip[["ibbs3_kod", "kiraci_pct_2021", "dogu"]], on="ibbs3_kod", how="left")
p["ln_fg"] = np.log(p.fiyat_gelir)
p["ln_kg"] = np.log(p.kira_gelir_pct)
p["ln_p"] = np.log(p.birim_fiyat)
p["ln_y"] = np.log(p.gsyh_kb_tl)
p = p.sort_values(["ibbs3_kod", "yil"]).reset_index(drop=True)
g = p.groupby("ibbs3_kod")
for c in ["ln_fg", "ln_kg", "ln_p", "ln_y"]:
    p[c + "_l1"] = g[c].shift(1)
    p[c + "_l2"] = g[c].shift(2)
    p[c + "_f1"] = g[c].shift(-1)
p["kira_z"] = (p.kiraci_pct_2021 - p.kiraci_pct_2021.mean()) / p.kiraci_pct_2021.std()
p["bolge_yil"] = p.ibbs1 + "_" + p.yil.astype(str)
p["t"] = p.yil - 2010
DEPREM = ["Kahramanmaraş", "Hatay", "Adıyaman", "Malatya", "Gaziantep", "Osmaniye", "Diyarbakır", "Şanlıurfa",
          "Adana", "Kilis", "Elazığ"]  # 6 Şubat 2023 depremlerinden etkilenen 11 il
SONUCLAR = {"ilk_evlenme_yasi_k": "Kadın ilk evlenme yaşı (yıl)", "kaba_evlenme": "Kaba evlenme hızı (‰)",
            "tieh_k": "Kadın toplam ilk evlenme hızı", "tdh": "Toplam doğurganlık hızı",
            "ilk_dogum_yasi": "İlk doğumda anne yaşı (yıl)"}


def tr_sayi(x, nd=2):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def yildiz(pv):
    return "***" if pv < 0.001 else "**" if pv < 0.01 else "*" if pv < 0.05 else "†" if pv < 0.10 else ""


# --- yardımcı: yüksek boyutlu sabit etkili regresyon (FWL) -------------------------------------
def fe_reg(d, y, xs, fe=("ibbs3_kod", "yil"), trend=False, w=None, kume="ibbs3_kod", boot=0):
    """Sabit etkileri dummy matrisiyle ayrıştırır (Frisch-Waugh-Lovell), kalan değişkenlerle OLS/WLS.
    Kümelenmiş SH: V = G/(G-1)·(N-1)/(N-K)·(X'X)⁻¹ Σ_g X_g'u_g u_g'X_g (X'X)⁻¹, K = x sayısı + kümelerin içine
    yuvalanmamış sabit etki sayısı (reghdfe tipi). p-değerleri t(G-1) dağılımından.
    boot>0: tek değişken için kısıtlı yabani küme bootstrap (Rademacher) p-değeri."""
    kol = [y] + list(xs) + list(fe) + ([w] if w else []) + ([kume] if kume not in fe else [])
    s = d.dropna(subset=list(dict.fromkeys(kol))).copy()
    s = s[s.groupby(kume)[y].transform("size") > 1] if kume == fe[0] else s  # tekil kümeler
    n = len(s)
    D = pd.get_dummies(s[list(fe)].astype(str), drop_first=False, dtype=float)
    if trend:
        tt = pd.get_dummies(s[fe[0]].astype(str), dtype=float).mul(s["t"].values, axis=0)
        D = pd.concat([D, tt.add_prefix("tr_")], axis=1)
    sw = np.sqrt(s[w].values) if w else np.ones(n)
    Dm = D.values * sw[:, None]
    Y = s[y].values * sw
    X = s[list(xs)].values * sw[:, None]
    rk = np.linalg.matrix_rank(Dm)
    proj = lambda M: M - Dm @ np.linalg.lstsq(Dm, M, rcond=None)[0]
    Yr, Xr = proj(Y), proj(X)
    b = np.linalg.lstsq(Xr, Yr, rcond=None)[0]
    u = Yr - Xr @ b
    grp = s[kume].values
    G = len(np.unique(grp))
    yuvali = s.groupby(fe[0])[kume].nunique().max() == 1  # il SE kümelerin içinde mi?
    n_ic = s[fe[0]].nunique() if yuvali else 0
    if trend:
        n_ic += s[fe[0]].nunique()
    K = len(xs) + max(rk - n_ic, 0)
    bread = np.linalg.inv(Xr.T @ Xr)
    meat = np.zeros((len(xs), len(xs)))
    for gg in np.unique(grp):
        m = grp == gg
        sc = Xr[m].T @ u[m]
        meat += np.outer(sc, sc)
    V = G / (G - 1) * (n - 1) / (n - K) * bread @ meat @ bread
    se = np.sqrt(np.diag(V))
    tst = b / se
    pv = 2 * stats.t.sf(np.abs(tst), G - 1)
    out = {"n": n, "il_sayisi": s.ibbs3_kod.nunique(), "kume": G,
           "b": dict(zip(xs, b)), "se": dict(zip(xs, se)), "p": dict(zip(xs, pv)),
           "V": pd.DataFrame(V, index=xs, columns=xs)}
    if boot and len(xs) == 1:
        gid = pd.factorize(grp)[0]
        tb = []
        for _ in range(boot):
            v = RNG.choice([-1.0, 1.0], size=G)[gid]
            ys = Yr * v  # H0: b = 0 altında kısıtlı artıklar = Yr
            bb = np.linalg.lstsq(Xr, ys, rcond=None)[0]
            uu = ys - Xr @ bb
            mt = 0.0
            for gg in range(G):
                m = gid == gg
                mt += (Xr[m, 0] @ uu[m]) ** 2
            seb = np.sqrt(G / (G - 1) * (n - 1) / (n - K) * bread[0, 0] ** 2 * mt)
            tb.append(bb[0] / seb)
        out["p_boot"] = float(np.mean(np.abs(tb) >= abs(tst[0])))
    return out


satirlar = []


def kaydet(blok, model, sonuc, x, r, ek=None):
    b, se, pv = r["b"][x], r["se"][x], r["p"][x]
    crit = stats.t.ppf(0.975, r["kume"] - 1)
    satirlar.append({"blok": blok, "model": model, "sonuc": sonuc, "degisken": x, "b": b, "se": se, "p": pv,
                     "ga_alt": b - crit * se, "ga_ust": b + crit * se, "etki_10pct": b * LN10,
                     "etki_10pct_alt": (b - crit * se) * LN10, "etki_10pct_ust": (b + crit * se) * LN10,
                     "n": r["n"], "il_sayisi": r["il_sayisi"], "kume": r["kume"], "p_boot": r.get("p_boot"),
                     **(ek or {})})


# --- 1. Betimsel -------------------------------------------------------------------------------
print("=" * 110)
print("1. BETİMSEL")
seri = tr[["birim_fiyat", "birim_kira", "gsyh_kb_tl", "fiyat_gelir", "kira_gelir_pct", "reel_birim_fiyat",
           "kaba_evlenme", "ilk_evlenme_yasi_k", "tieh_k", "tdh", "ilk_dogum_yasi"]].loc[2010:2025]
dag = p.groupby("yil").fiyat_gelir.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])[["count", "10%", "25%", "50%", "75%", "90%"]]
seri = seri.join(dag.add_prefix("il_fg_"))
seri.round(3).to_csv(SONUC / "konut_turkiye_seri.csv", encoding="utf-8")
print(seri[["fiyat_gelir", "kira_gelir_pct", "ilk_evlenme_yasi_k", "tdh", "il_fg_count", "il_fg_10%", "il_fg_90%"]].round(2))
s24 = p[p.yil == 2024].dropna(subset=["fiyat_gelir"]).sort_values("fiyat_gelir")
print("\nFiyat/gelir 2024 — en düşük 5:", ", ".join(f"{r.il} {r.fiyat_gelir:.1f}" for r in s24.head(5).itertuples()))
print("Fiyat/gelir 2024 — en yüksek 5:", ", ".join(f"{r.il} {r.fiyat_gelir:.1f}" for r in s24.tail(5).itertuples()))
s24[["il", "ibbs3_kod", "birim_fiyat", "birim_kira", "gsyh_kb_tl", "fiyat_gelir", "kira_gelir_pct"]].round(2) \
    .to_csv(SONUC / "konut_il_fiyat_gelir_2024.csv", index=False, encoding="utf-8")
ss = p.dropna(subset=["ln_fg"])
art = ss.ln_fg - ss.groupby("ibbs3_kod").ln_fg.transform("mean") - ss.groupby("yil").ln_fg.transform("mean") + ss.ln_fg.mean()
print(f"ln(fiyat/gelir): ham SS {ss.ln_fg.std():.3f}; il ve yıl ortalamaları çıkarıldıktan sonra SS ≈ {art.std():.3f}")

# --- 2. İl × yıl paneli -----------------------------------------------------------------------
print("\n" + "=" * 110)
print("2. İL × YIL PANELİ — ln(fiyat/gelir)_{t-1} katsayısı; %10 artışın etkisi sonuç biriminde")
FE_IY = ("ibbs3_kod", "yil")
FE_BY = ("ibbs3_kod", "bolge_yil")
for y in SONUCLAR:
    d = p[p.yil >= 2011]
    kaydet("panel", "A: il + yıl SE", y, "ln_fg_l1", fe_reg(d, y, ["ln_fg_l1"], FE_IY))
    r = fe_reg(d, y, ["ln_fg_l1", "ln_fg_f1"], FE_IY)
    kaydet("panel", "B: A + öncü (t+1)", y, "ln_fg_f1", r)
    kaydet("panel", "B: A + öncü (t+1)", y, "ln_fg_l1", r)
    kaydet("panel", "C: il + 12 bölge×yıl SE", y, "ln_fg_l1", fe_reg(d, y, ["ln_fg_l1"], FE_BY))
    kaydet("panel", "C2: C, İBBS-2 kümeli", y, "ln_fg_l1", fe_reg(d, y, ["ln_fg_l1"], FE_BY, kume="ibbs2"))
    r = fe_reg(d, y, ["ln_fg_l1", "ln_fg_f1"], FE_BY)
    kaydet("panel", "C3: C + öncü (t+1)", y, "ln_fg_f1", r)
    kaydet("panel", "D: C, kadın 20–34 ağırlıklı", y, "ln_fg_l1", fe_reg(d, y, ["ln_fg_l1"], FE_BY, w="kadin_20_34"))
    kaydet("panel", "E: C, deprem illeri hariç", y, "ln_fg_l1", fe_reg(d[~d.il.isin(DEPREM)], y, ["ln_fg_l1"], FE_BY))
    kaydet("panel", "F: C, 2011–2019", y, "ln_fg_l1", fe_reg(d[d.yil <= 2019], y, ["ln_fg_l1"], FE_BY))
    kaydet("panel", "G: C + il trendi", y, "ln_fg_l1", fe_reg(d, y, ["ln_fg_l1"], FE_BY, trend=True))
    r = fe_reg(d, y, ["ln_fg_l1", "ln_fg_f1"], FE_BY, trend=True)
    kaydet("panel", "G2: G + öncü (t+1)", y, "ln_fg_f1", r)
    kaydet("panel", "G2: G + öncü (t+1)", y, "ln_fg_l1", r)
    r = fe_reg(d, y, ["ln_p_l1", "ln_y_l1"], FE_BY)
    kaydet("panel", "H: C, fiyat ve gelir ayrı", y, "ln_p_l1", r)
    kaydet("panel", "H: C, fiyat ve gelir ayrı", y, "ln_y_l1", r)
    d2 = d.assign(etk=d.ln_fg_l1 * d.kira_z)
    r = fe_reg(d2, y, ["ln_fg_l1", "etk"], FE_BY)
    kaydet("panel", "I: C × kiracı payı (z)", y, "etk", r)
    r = fe_reg(d, y, ["ln_fg_l1", "ln_fg_l2"], FE_BY)
    toplam = r["b"]["ln_fg_l1"] + r["b"]["ln_fg_l2"]
    se_t = np.sqrt(r["V"].values.sum())
    r2 = {**r, "b": {"toplam": toplam}, "se": {"toplam": se_t},
          "p": {"toplam": 2 * stats.t.sf(abs(toplam / se_t), r["kume"] - 1)}}
    kaydet("panel", "J: C, gecikme t-1 + t-2 toplamı", y, "toplam", r2)
pan = pd.DataFrame(satirlar)
for y in SONUCLAR:
    print(f"\n{SONUCLAR[y]}")
    for rr in pan[(pan.sonuc == y)].itertuples():
        print(f"   {rr.model:34s} {rr.degisken:9s} b={rr.b:+.3f} ({rr.se:.3f}){yildiz(rr.p):3s} p={rr.p:.3f} "
              f"| %10 → {rr.etki_10pct:+.3f} [{rr.etki_10pct_alt:+.3f}; {rr.etki_10pct_ust:+.3f}] n={rr.n} il={rr.il_sayisi}")

# --- 3. Kira/gelir paneli ve yaşa özel ilk evlenme hızları -------------------------------------------
print("\n" + "=" * 110)
print("3a. KİRA/GELİR PANELİ (2019–2025): ln(kira/gelir)_{t-1}")
for y in SONUCLAR:
    d = p[p.yil >= 2019]
    if d[y].notna().sum() < 100:
        continue
    kaydet("kira", "A: il + yıl SE", y, "ln_kg_l1", fe_reg(d, y, ["ln_kg_l1"], FE_IY))
    r = fe_reg(d, y, ["ln_kg_l1", "ln_kg_f1"], FE_IY)
    kaydet("kira", "B: A + öncü (t+1)", y, "ln_kg_f1", r)
    kaydet("kira", "C: il + 12 bölge×yıl SE", y, "ln_kg_l1", fe_reg(d, y, ["ln_kg_l1"], FE_BY))
print("3b. YAŞA ÖZEL KADIN İLK EVLENME HIZLARI (‰, 2011–2023): erteleme varsa 20–24'te düşüş, 30–34'te artış beklenir")
for y in ["iehk_15_19", "iehk_20_24", "iehk_25_29", "iehk_30_34"]:
    d = p[p.yil >= 2011]
    kaydet("yas", "A: il + yıl SE", y, "ln_fg_l1", fe_reg(d, y, ["ln_fg_l1"], FE_IY))
    kaydet("yas", "C: il + 12 bölge×yıl SE", y, "ln_fg_l1", fe_reg(d, y, ["ln_fg_l1"], FE_BY))
tab = pd.DataFrame(satirlar)
for rr in tab[tab.blok.isin(["kira", "yas"])].itertuples():
    print(f"   {rr.blok:5s} {rr.sonuc:20s} {rr.model:26s} {rr.degisken:9s} b={rr.b:+.3f} ({rr.se:.3f}){yildiz(rr.p):3s} "
          f"| %10 → {rr.etki_10pct:+.3f} [{rr.etki_10pct_alt:+.3f}; {rr.etki_10pct_ust:+.3f}] n={rr.n}")

# --- 4. KFE bölge paneli ---------------------------------------------------------------------------
print("\n" + "=" * 110)
print("4. KFE BÖLGE PANELİ (19 bölge, kalite düzeltilmiş endeks): ln(KFE / kişi başı GSYH)_{t-1}; yabani küme bootstrap")
b = pd.read_csv(ISLENMIS / "konut_paneli_kfe_bolge.csv")
b = b[b.kfe_bolge != "TR"].sort_values(["kfe_bolge", "yil"]).reset_index(drop=True)
b["ibbs3_kod"] = b.kfe_bolge  # fe_reg arayüzü için
b["ln_kg"] = np.log(b.kfe) - np.log(b.gsyh_kb_tl)
gb = b.groupby("kfe_bolge")
b["ln_kg_l1"] = gb.ln_kg.shift(1)
b["ln_kg_f1"] = gb.ln_kg.shift(-1)
for y in ["ilk_evlenme_yasi_k", "kaba_evlenme", "tieh_k", "tdh"]:
    d = b[b.yil >= 2011]
    kaydet("kfe_bolge", "A: bölge + yıl SE", y, "ln_kg_l1", fe_reg(d, y, ["ln_kg_l1"], FE_IY, boot=BOOT))
    kaydet("kfe_bolge", "B: öncü (t+1) yalnız", y, "ln_kg_f1", fe_reg(d, y, ["ln_kg_f1"], FE_IY, boot=BOOT))
tab = pd.DataFrame(satirlar)
for rr in tab[tab.blok == "kfe_bolge"].itertuples():
    print(f"   {rr.sonuc:20s} {rr.model:22s} b={rr.b:+.3f} ({rr.se:.3f}) p={rr.p:.3f} p_boot={rr.p_boot if rr.p_boot is None else round(rr.p_boot, 3)} "
          f"| %10 → {rr.etki_10pct:+.3f} n={rr.n}")

# --- 5. Uzun fark ------------------------------------------------------------------------------------
print("\n" + "=" * 110)
print("5. UZUN FARK: Δ sonuç (t0+1 → t1+1) ~ Δ ln(fiyat/gelir) (t0 → t1) + başlangıç düzeyi + 12 bölge SE  [HC1]")
pp = p.set_index(["ibbs3_kod", "yil"])
uf = []


def uzun_fark(x0, x1, egitim=False, haric=()):
    y0, y1 = x0 + 1, x1 + 1
    rows = []
    for k in p.ibbs3_kod.unique():
        try:
            r = {"ibbs3_kod": k, "d_lnfg": np.log(pp.loc[(k, x1), "fiyat_gelir"] / pp.loc[(k, x0), "fiyat_gelir"]),
                 "d_egt": pp.loc[(k, y1), "kadin_yuksek_pct"] - pp.loc[(k, y0), "kadin_yuksek_pct"]}
            for y in ["ilk_evlenme_yasi_k", "kaba_evlenme", "tdh", "tieh_k"]:
                r[f"d_{y}"] = pp.loc[(k, y1), y] - pp.loc[(k, y0), y]
                r[f"b_{y}"] = pp.loc[(k, y0), y]
            rows.append(r)
        except KeyError:
            pass
    L = pd.DataFrame(rows).merge(ip[["ibbs3_kod", "ibbs1", "il"]], on="ibbs3_kod")
    L = L[~L.il.isin(haric)]
    for y in ["ilk_evlenme_yasi_k", "kaba_evlenme", "tdh", "tieh_k"]:
        s = L.dropna(subset=[f"d_{y}", "d_lnfg", f"b_{y}"])
        s = s[s.groupby("ibbs1").ibbs1.transform("size") > 1]  # tekil bölge (İstanbul) SE'ye katkı vermez
        if len(s) < 30:
            continue
        f = f"d_{y} ~ d_lnfg + b_{y} + C(ibbs1)" + (" + d_egt" if egitim else "")
        m = smf.ols(f, s).fit(cov_type="HC1")
        crit = stats.norm.ppf(0.975)
        uf.append({"pencere": f"{x0}→{x1}", "egitim_kontrol": egitim, "haric": ", ".join(haric), "sonuc": y,
                   "n": int(m.nobs),
                   "b": m.params.d_lnfg, "se": m.bse.d_lnfg, "p": m.pvalues.d_lnfg,
                   "etki_10pct": m.params.d_lnfg * LN10,
                   "etki_10pct_alt": (m.params.d_lnfg - crit * m.bse.d_lnfg) * LN10,
                   "etki_10pct_ust": (m.params.d_lnfg + crit * m.bse.d_lnfg) * LN10,
                   "ort_d_lnfg": s.d_lnfg.mean(), "ss_d_lnfg": s.d_lnfg.std()})
    return L


L_ana = uzun_fark(2012, 2023)
uzun_fark(2012, 2023, egitim=True)
uzun_fark(2012, 2023, haric=("Muğla", "Antalya"))
for a, c in [(2010, 2023), (2014, 2023), (2012, 2018), (2017, 2023), (2012, 2022)]:
    uzun_fark(a, c)
uf = pd.DataFrame(uf)
uf.to_csv(SONUC / "konut_uzun_fark.csv", index=False, encoding="utf-8")
for rr in uf.itertuples():
    print(f"   {rr.pencere} eğitim={'E' if rr.egitim_kontrol else 'H'} hariç=[{rr.haric}] {rr.sonuc:20s} n={rr.n} b={rr.b:+.3f} ({rr.se:.3f}){yildiz(rr.p):3s}"
          f" | %10 → {rr.etki_10pct:+.3f} [{rr.etki_10pct_alt:+.3f}; {rr.etki_10pct_ust:+.3f}]")

# --- 6. 2025 kesiti ------------------------------------------------------------------------------------
print("\n" + "=" * 110)
print("6. 2025 KESİTİ: fiyat/gelir 2024 → 2025 sonuçları (standartlaştırılmış β; HC1)")
k = ip.merge(p[p.yil == 2024][["ibbs3_kod", "fiyat_gelir", "kira_gelir_pct", "birim_fiyat", "gsyh_kb_tl"]], on="ibbs3_kod")
k["ln_fg"] = np.log(k.fiyat_gelir)
k["ln_kg"] = np.log(k.kira_gelir_pct)
k["ln_p"] = np.log(k.birim_fiyat)
k["ln_y"] = np.log(k.gsyh_kb_tl)


def z(s):
    return (s - s.mean()) / s.std(ddof=0)


kes = []
for y in ["ilk_evlenme_yasi_k_2025", "kaba_evlenme_2025", "tdh_2025", "ilk_dogum_yasi_2025"]:
    for ad, xs, bolge in [("ham", ["ln_fg"], False), ("+ kadın eğitimi + 12 bölge", ["ln_fg", "kadin_egitim_suresi_2025"], True),
                          ("fiyat ve gelir ayrı + eğitim + bölge", ["ln_p", "ln_y", "kadin_egitim_suresi_2025"], True),
                          ("kira/gelir + eğitim + bölge", ["ln_kg", "kadin_egitim_suresi_2025"], True)]:
        s = k.dropna(subset=[y] + xs).copy()
        if bolge:
            s = s[s.groupby("ibbs1").ibbs1.transform("size") > 1]
        zz = pd.DataFrame({c: z(s[c]) for c in [y] + xs})
        zz["ibbs1"] = s.ibbs1.values
        m = smf.ols(f"{y} ~ {' + '.join(xs)}" + (" + C(ibbs1)" if bolge else ""), zz).fit(cov_type="HC1")
        mh = smf.ols(f"{y} ~ {' + '.join(xs)}" + (" + C(ibbs1)" if bolge else ""), s).fit(cov_type="HC1")
        x0 = xs[0]
        kes.append({"sonuc": y, "model": ad, "degisken": x0, "n": int(m.nobs), "R2": m.rsquared, "beta": m.params[x0],
                    "p": m.pvalues[x0], "ham_b": mh.params[x0], "etki_10pct": mh.params[x0] * LN10})
kes = pd.DataFrame(kes)
kes.to_csv(SONUC / "konut_kesit_2025.csv", index=False, encoding="utf-8")
for rr in kes.itertuples():
    print(f"   {rr.sonuc:24s} {rr.model:38s} n={rr.n} R²={rr.R2:.2f} β={rr.beta:+.2f}{yildiz(rr.p):3s} (p={rr.p:.3f}) "
          f"| %10 → {rr.etki_10pct:+.3f}")
print("Korelasyon (2024 fiyat/gelir ile): kadın eğitim süresi r =",
      round(k[["fiyat_gelir", "kadin_egitim_suresi_2025"]].corr().iloc[0, 1], 2),
      "| ln GSYH r =", round(np.corrcoef(k.dropna(subset=["fiyat_gelir"]).fiyat_gelir,
                                         np.log(k.dropna(subset=["fiyat_gelir"]).gsyh_kb_tl))[0, 1], 2))

tab = pd.DataFrame(satirlar)
tab.drop(columns=[c for c in tab.columns if c == "V"], errors="ignore").to_csv(
    SONUC / "konut_panel_modeller.csv", index=False, encoding="utf-8")

# --- 7. Grafikler ----------------------------------------------------------------------------------------
YAZI, YAZI_2, ZEMIN = "#0b0b0b", "#52514e", "#fcfcfb"
MAVI, TURUNCU, IZGARA = "#2a78d6", "#eb6834", "#e4e2dd"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN,
                     "axes.facecolor": ZEMIN, "text.color": YAZI, "axes.edgecolor": "#8a8985"})
virgul = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def sade(ax):
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.grid(axis="y", color=IZGARA, lw=0.6, zorder=0)
    ax.tick_params(length=0)


# 7.1 Türkiye seyri: fiyat/gelir (il dağılımıyla), kadın ilk evlenme yaşı, TDH
fig, axs = plt.subplots(1, 3, figsize=(13, 4.7), dpi=150)
fig.subplots_adjust(left=0.05, right=0.98, top=0.73, bottom=0.13, wspace=0.28)
yy = seri.index.values
ax = axs[0]
ax.fill_between(yy, seri["il_fg_25%"], seri["il_fg_75%"], color=MAVI, alpha=0.15, lw=0, zorder=2)
ax.plot(yy, seri["il_fg_50%"], color=MAVI, lw=1, ls=(0, (3, 2)), zorder=3)
ax.plot(yy, seri.fiyat_gelir, color=MAVI, lw=2, marker="o", ms=3.5, zorder=4)
ax.text(2024.4, seri.fiyat_gelir.loc[2024], "Türkiye", va="center", fontsize=8, color=YAZI)
ax.text(2024.4, seri["il_fg_50%"].loc[2024], "il medyanı", va="center", fontsize=8, color=YAZI_2)
ax.text(2010.0, 4.12, "mavi alan: illerin ortadaki yarısı", fontsize=7.5, color=YAZI_2)
ax.set_title("100 m² konut, kişi başı GSYH'nin kaç katı?", loc="left", fontsize=10, fontweight="bold", pad=20)
ax.set_xlim(2009.5, 2027.2)
ax.set_ylim(3.8, 9.0)
axs[1].plot(yy, seri.ilk_evlenme_yasi_k, color=TURUNCU, lw=2, marker="o", ms=3.5, zorder=3)
axs[1].set_title("Kadınların ilk evlenme yaşı", loc="left", fontsize=10, fontweight="bold", pad=20)
axs[2].plot(yy, seri.tdh, color=TURUNCU, lw=2, marker="o", ms=3.5, zorder=3)
axs[2].set_title("Toplam doğurganlık hızı", loc="left", fontsize=10, fontweight="bold", pad=20)
for a_, alt in zip(axs, ["kat · 2010–2024", "yıl · 2010–2025", "kadın başına çocuk · 2010–2025"]):
    sade(a_)
    a_.yaxis.set_major_formatter(virgul)
    a_.text(0, 1.025, alt, transform=a_.transAxes, fontsize=8, color=YAZI_2, va="bottom")
    a_.set_xticks([2010, 2013, 2016, 2019, 2022, 2025])
fig.text(0.05, 0.955, "Konut erişilebilirliği dalgalı; evlilik yaşı ve doğurganlık tek yönde ilerliyor",
         fontsize=14, fontweight="bold")
fig.text(0.05, 0.875, f"Türkiye'de fiyat/gelir 2010'da {tr_sayi(seri.fiyat_gelir.loc[2010], 1)}, 2019'da "
         f"{tr_sayi(seri.fiyat_gelir.loc[2019], 1)}, 2023'te {tr_sayi(seri.fiyat_gelir.loc[2023], 1)}, 2024'te "
         f"{tr_sayi(seri.fiyat_gelir.loc[2024], 1)}. Kadın ilk evlenme yaşı her yıl yükseldi; doğurganlık 2014'ten beri düşüyor.\n"
         "Türkiye değeri, pahalı büyük kentlerin ağırlığı yüzünden il medyanının üstünde.",
         fontsize=9, color=YAZI_2, linespacing=1.45)
fig.text(0.05, 0.025, "Kaynak: TCMB EVDS konut birim fiyatları (değerleme raporları, TL/m²); TÜİK il GSYH, evlenme ve doğum "
         "istatistikleri. Fiyat/gelir = birim fiyat × 100 m² / kişi başı GSYH.", fontsize=7.5, color=YAZI_2)
for uz in ("png", "svg"):
    fig.savefig(GRAFIK / f"konut_turkiye_seyir.{uz}", facecolor=ZEMIN)
plt.close(fig)

# 7.2 Katsayı grafiği: %10 daha yüksek fiyat/gelirin etkisi — geçmiş ve gelecek (plasebo) fiyat, sıkı modeller, uzun fark
SECIM = [("A: il + yıl SE", "ln_fg_l1", "İl + yıl SE · geçen yılın fiyatı", MAVI),
         ("B: A + öncü (t+1)", "ln_fg_f1", "İl + yıl SE · gelecek yılın fiyatı (plasebo)", TURUNCU),
         ("C: il + 12 bölge×yıl SE", "ln_fg_l1", "+ bölge×yıl SE · geçen yılın fiyatı", MAVI),
         ("C3: C + öncü (t+1)", "ln_fg_f1", "+ bölge×yıl SE · gelecek yılın fiyatı (plasebo)", TURUNCU),
         ("G: C + il trendi", "ln_fg_l1", "+ bölge×yıl SE + il trendi · geçen yılın fiyatı", MAVI),
         ("UF", None, "Uzun fark 2012→2023 (12 bölge SE)", MAVI)]
GOSTER = ["ilk_evlenme_yasi_k", "kaba_evlenme", "tdh"]
BIRIM = {"ilk_evlenme_yasi_k": "yıl", "kaba_evlenme": "binde puan", "tdh": "çocuk"}
H2_YON = {"ilk_evlenme_yasi_k": "H2: sağda", "kaba_evlenme": "H2: solda", "tdh": "H2: solda"}
fig, axs = plt.subplots(1, 3, figsize=(13, 5.6), dpi=150, sharey=True)
fig.subplots_adjust(left=0.255, right=0.985, top=0.71, bottom=0.15, wspace=0.14)
for ax, y in zip(axs, GOSTER):
    for i, (model, x, et, renk) in enumerate(SECIM):
        if model == "UF":
            r = uf[(uf.pencere == "2012→2023") & (~uf.egitim_kontrol) & (uf.haric == "") & (uf.sonuc == y)].iloc[0]
        else:
            r = tab[(tab.blok == "panel") & (tab.model == model) & (tab.sonuc == y) & (tab.degisken == x)].iloc[0]
        yp = len(SECIM) - 1 - i
        ax.plot([r.etki_10pct_alt, r.etki_10pct_ust], [yp, yp], color=renk, lw=2, solid_capstyle="round", zorder=3)
        ax.plot(r.etki_10pct, yp, "o", color=renk, ms=8, mec=ZEMIN, mew=2, zorder=4)
    ax.axvline(0, color="#8a8985", lw=1, zorder=2)
    ax.set_title(SONUCLAR[y].split(" (")[0], loc="left", fontsize=10.5, fontweight="bold", pad=34)
    ax.text(0, 1.06, f"%10 daha yüksek fiyat/gelirin etkisi, {BIRIM[y]}", transform=ax.transAxes,
            fontsize=8, color=YAZI_2, va="bottom")
    ax.text(0, 1.015, f"nokta: tahmin · çizgi: %95 güven aralığı · {H2_YON[y]}", transform=ax.transAxes,
            fontsize=8, color=YAZI_2, va="bottom")
    for s_ in ("top", "right", "left"):
        ax.spines[s_].set_visible(False)
    ax.grid(axis="x", color=IZGARA, lw=0.6, zorder=0)
    ax.tick_params(length=0)
    ax.xaxis.set_major_formatter(virgul)
    ax.set_ylim(-0.6, len(SECIM) - 0.4)
axs[0].set_yticks(range(len(SECIM)))
axs[0].set_yticklabels([s_[2] for s_ in SECIM][::-1], fontsize=8.5)
fig.text(0.02, 0.955, "Gelecek yılın fiyatı bugünkü evliliği, geçen yılın fiyatından daha iyi \"açıklıyor\"",
         fontsize=14, fontweight="bold")
fig.text(0.02, 0.86, "76 il, 2011–2025; il düzeyinde kümelenmiş standart hata. Turuncu satırlar plasebo: henüz oluşmamış bir fiyat "
         "bugünkü evliliği etkileyemez. Bu satırların güçlü çıkması,\nilişkinin ters yönde (evlilik → konut talebi → fiyat) "
         "ya da ortak bölgesel şoklar üzerinden kurulduğunu gösterir. Bölge×yıl sabit etkileriyle geçen yılın fiyatının "
         "katsayısı sıfıra iner.", fontsize=8.5, color=YAZI_2, linespacing=1.5)
fig.text(0.02, 0.03, "Bölge: 12 İBBS-1 bölgesi. Uzun fark: 2012→2023 fiyat/gelir değişimi ile 2013→2024 sonuç değişimi, başlangıç "
         "düzeyi ve bölge kontrollü (58 il). Kaynak: TCMB EVDS, TÜİK.", fontsize=7.5, color=YAZI_2)
for uz in ("png", "svg"):
    fig.savefig(GRAFIK / f"konut_katsayilar.{uz}", facecolor=ZEMIN)
plt.close(fig)

# 7.3 Uzun fark: fiyat/gelir değişimi ile sonuç değişimi (bölge ortalamalarından arındırılmış)
L = L_ana.dropna(subset=["d_lnfg", "d_ilk_evlenme_yasi_k", "d_tdh"]).copy()
L = L[L.groupby("ibbs1").ibbs1.transform("size") > 1]
for c in ["d_lnfg", "d_ilk_evlenme_yasi_k", "d_tdh"]:
    L[c + "_r"] = L[c] - L.groupby("ibbs1")[c].transform("mean")
fig, axs = plt.subplots(1, 2, figsize=(12, 5.6), dpi=150)
fig.subplots_adjust(left=0.07, right=0.98, top=0.72, bottom=0.14, wspace=0.22)
for ax, (c, et) in zip(axs, [("d_ilk_evlenme_yasi_k_r", "Kadın ilk evlenme yaşındaki artış"),
                             ("d_tdh_r", "Toplam doğurganlık hızındaki değişim")]):
    ax.scatter(L.d_lnfg_r * 100, L[c], s=36, color=MAVI, edgecolor=ZEMIN, linewidth=1.2, zorder=3)
    bb = np.polyfit(L.d_lnfg_r * 100, L[c], 1)
    xx = np.linspace(L.d_lnfg_r.min() * 100, L.d_lnfg_r.max() * 100, 10)
    ax.plot(xx, np.polyval(bb, xx), color=YAZI, lw=1.2, ls=(0, (4, 3)), zorder=2)
    for r in L.itertuples():
        if abs(r.d_lnfg_r) > 0.25 or abs(getattr(r, c)) > np.nanpercentile(np.abs(L[c]), 95):
            ax.annotate(r.il, (r.d_lnfg_r * 100, getattr(r, c)), xytext=(4, 3), textcoords="offset points",
                        fontsize=7.5, color=YAZI_2)
    ax.axhline(0, color="#8a8985", lw=0.8, zorder=1)
    ax.axvline(0, color="#8a8985", lw=0.8, zorder=1)
    sade(ax)
    ax.grid(axis="x", color=IZGARA, lw=0.6, zorder=0)
    ax.set_title(et, loc="left", fontsize=10.5, fontweight="bold", pad=20)
    ax.text(0, 1.025, ("yıl" if "yasi" in c else "çocuk") + " · 2013→2024 · aynı bölgedeki illerin ortalamasından sapma",
            transform=ax.transAxes, fontsize=8, color=YAZI_2, va="bottom")
    ax.set_xlabel("fiyat/gelirdeki değişim 2012→2023 (log puan × 100, bölge ortalamasından sapma)", color=YAZI_2)
    ax.yaxis.set_major_formatter(virgul)
    ax.xaxis.set_major_formatter(virgul)


def sec(**k):
    m = np.logical_and.reduce([uf[a] == b for a, b in k.items()])
    return uf[m].iloc[0]


r1 = sec(pencere="2012→2023", egitim_kontrol=False, haric="", sonuc="ilk_evlenme_yasi_k")
r2 = sec(pencere="2012→2023", egitim_kontrol=True, haric="", sonuc="ilk_evlenme_yasi_k")
r3 = sec(pencere="2012→2023", egitim_kontrol=False, haric="Muğla, Antalya", sonuc="ilk_evlenme_yasi_k")
r4 = sec(pencere="2012→2023", egitim_kontrol=False, haric="", sonuc="tdh")
fig.text(0.02, 0.955, "Orta vadede H2 yönünde zayıf bir iz: fiyat/geliri hızlı artan illerde evlilik yaşı biraz daha çok yükseldi",
         fontsize=13, fontweight="bold")
fig.text(0.02, 0.835, f"{len(L)} il (İstanbul tek başına bir bölge olduğu için dışarıda). Kesikli çizgi: basit eğim. "
         f"Regresyonda (başlangıç düzeyi ve bölge kontrollü) fiyat/gelirde %10 artış:\n"
         f"ilk evlenme yaşı +{tr_sayi(r1.etki_10pct)} yıl (p = {tr_sayi(r1.p, 3)}), doğurganlık {tr_sayi(r4.etki_10pct, 3)} "
         f"çocuk (p = {tr_sayi(r4.p, 3)}). Kadın yükseköğretim payındaki artış kontrol edilince ilk evlenme yaşı etkisi "
         f"+{tr_sayi(r2.etki_10pct)} yıl (p = {tr_sayi(r2.p, 2)});\nMuğla ve Antalya çıkarılınca +{tr_sayi(r3.etki_10pct)} yıl "
         f"(p = {tr_sayi(r3.p, 2)}). Başka dönem seçimlerinde etki zayıflıyor ya da kayboluyor (rapor §2.8).",
         fontsize=8.5, color=YAZI_2, linespacing=1.5)
fig.text(0.02, 0.03, "Kaynak: TCMB EVDS konut birim fiyatları; TÜİK il GSYH, evlenme ve doğum istatistikleri. "
         "Bu bir il düzeyi (ekolojik) analizdir; bireysel nedensellik göstermez.", fontsize=7.5, color=YAZI_2)
for uz in ("png", "svg"):
    fig.savefig(GRAFIK / f"konut_uzun_fark.{uz}", facecolor=ZEMIN)
plt.close(fig)
print("\ngrafikler yazıldı: konut_turkiye_seyir, konut_katsayilar, konut_uzun_fark")
