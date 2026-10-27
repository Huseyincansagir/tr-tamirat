"""
Kentsel stres grafikleri (Faz 4 · Rapor 1)
=========================================
Girdi : 05_ANALIZ/sonuclar/stres_turkiye_ab.csv (stres_veri.py), stres_ilce_endeks.csv, stres_ilce_sinama.csv,
        stres_il_sinama.csv (stres_endeks.py), 03_VERI/islenmis/ilce_paneli_genis.csv
Çıktı : 05_ANALIZ/grafikler/stres_turkiye_ab.png|svg      Türkiye ve AB-27: konut, çevre, güvenlik, memnuniyet (EU-SILC)
        05_ANALIZ/grafikler/stres_maruziyet.png|svg       Türkiye nüfusunun PM2.5, ağaç örtüsü ve yaz yüzey sıcaklığına göre dağılımı
        05_ANALIZ/grafikler/stres_ilce_sinama.png|svg     KSY ve bileşenlerinin il içi SMR ilişkisi + dilim grafiği
        05_ANALIZ/grafikler/stres_il_sinama.png|svg       il düzeyi: intihar, mutluluk, gürültü ve güvenlik algısı
        05_ANALIZ/grafikler/stres_sema.png|svg            etken → mekanizma → sağlık sonucu şeması
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/stres_grafikler.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
SON = KOK / "05_ANALIZ" / "sonuclar"
GRAF = KOK / "05_ANALIZ" / "grafikler"
MAVI, TURUNCU, AQUA, SARI = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
YAZI, YAZI_2, YAZI_3, ZEMIN, IZGARA, GRI = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e8e7e3", "#c9c8c3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "axes.edgecolor": YAZI_3, "axes.labelcolor": YAZI_2, "xtick.color": YAZI_2, "ytick.color": YAZI_2,
                     "axes.formatter.use_locale": False})


def tr(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def iyelik(n):
    """Türkçe iyelik eki: 'nüfusun %67'si', '%64'ü', '%8'i' (sayının okunuşunun son sözcüğüne göre)"""
    n = int(round(abs(n)))
    if n == 0:
        return "ı"
    if n % 10:
        return {1: "i", 2: "si", 3: "ü", 4: "ü", 5: "i", 6: "sı", 7: "si", 8: "i", 9: "u"}[n % 10]
    if (n // 10) % 10:
        return {1: "u", 2: "si", 3: "u", 4: "ı", 5: "si", 6: "ı", 7: "i", 8: "i", 9: "ı"}[(n // 10) % 10]
    return "ü" if n % 1000 else "i"


def virgul_eksen(ax, eksen="x", nd=1):
    from matplotlib.ticker import FuncFormatter
    f = FuncFormatter(lambda v, _: tr(v, nd))
    (ax.xaxis if eksen == "x" else ax.yaxis).set_major_formatter(f)


def kaydet(fig, ad):
    for uz in ("png", "svg"):
        fig.savefig(GRAF / f"{ad}.{uz}", dpi=200, facecolor=ZEMIN)
    plt.close(fig)
    print(ad, "yazıldı")


def sade(ax, sol=False):
    for s in ("top", "right") + (() if sol else ("left",)):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)


# --- 1. Türkiye ve AB-27 -------------------------------------------------------------------------------------------
AB = pd.read_csv(SON / "stres_turkiye_ab.csv")
KISA = {"Aşırı kalabalık konutta yaşayan nüfus (%)": "Aşırı kalabalık konutta yaşayan",
        "Aşırı kalabalık konutta yaşayan 18 yaş altı (%)": "Aşırı kalabalık konutta yaşayan çocuk (<18)",
        "Konut maliyeti hane gelirinin %40'ını aşan nüfus (%)": "Konut maliyeti gelirin %40'ını aşan",
        "Konut maliyet yükü, yoksulluk riski altındakiler (%)": "Aynısı, yoksulluk riski altındakiler",
        "Komşudan ya da sokaktan gürültü sorunu (%)": "Komşudan ya da sokaktan gürültü sorunu",
        "Kirlilik, kir ya da başka çevre sorunu (%)": "Kirlilik, kir ya da başka çevre sorunu",
        "Çevrede suç, şiddet ya da vandalizm (%)": "Çevrede suç, şiddet ya da vandalizm",
        "Konutunu fazla karanlık bulan nüfus (%)": "Konutunu fazla karanlık bulan",
        "Genel yaşam memnuniyeti (0–10)": "Genel yaşam memnuniyeti", "Başkalarına güven (0–10)": "Başkalarına güven"}
yuzde = AB[AB.gosterge.str.contains("%")].iloc[::-1].reset_index(drop=True)
puan = AB[~AB.gosterge.str.contains("%")].iloc[::-1].reset_index(drop=True)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.6), gridspec_kw={"width_ratios": [2.4, 1]})
fig.subplots_adjust(left=0.235, right=0.98, top=0.80, bottom=0.12, wspace=0.62)
fig.text(0.01, 0.95, "Kalabalık ve karanlık konut, kirlilik ve düşük güven Türkiye'yi AB'den ayırıyor; gürültü ve suç algısı AB düzeyinde", fontsize=13.5, fontweight="bold", color=YAZI)
fig.text(0.01, 0.905, "EU-SILC hane anketi. Türkiye'nin son yılı ve AB-27'nin aynı yıldaki değeri; gri halka Türkiye'nin 2006 değeri. "
         "Aşırı kalabalık: Eurostat tanımıyla hanenin ihtiyacına göre oda sayısı yetersiz.", fontsize=9, color=YAZI_2)
for ax, t, nd, xlim in [(a1, yuzde, 1, (0, 66)), (a2, puan, 1, (0, 10))]:
    y = np.arange(len(t))
    for i, r in t.iterrows():
        ax.plot([r.ab27_ayni_yil, r.tr_son], [i, i], color=GRI, lw=2, zorder=1)
        if r.tr_ilk_yil == 2006:
            ax.scatter(r.tr_ilk, i, s=46, facecolor="none", edgecolor=YAZI_3, lw=1.2, zorder=2)
        ax.scatter(r.ab27_ayni_yil, i, s=70, color=MAVI, zorder=3, edgecolor=ZEMIN, lw=1.5)
        ax.scatter(r.tr_son, i, s=70, color=TURUNCU, zorder=3, edgecolor=ZEMIN, lw=1.5)
        sag = r.tr_son >= r.ab27_ayni_yil
        ax.text(r.tr_son + (1 if sag else -1) * (xlim[1] * 0.025), i + 0.27, tr(r.tr_son, nd), ha="left" if sag else "right",
                va="center", fontsize=8.5, color=YAZI, fontweight="bold")
        ax.text(r.ab27_ayni_yil + (-1 if sag else 1) * (xlim[1] * 0.025), i + 0.27, tr(r.ab27_ayni_yil, nd),
                ha="right" if sag else "left", va="center", fontsize=8.5, color=YAZI_2)
    ax.set_yticks(y, [f"{KISA.get(g, g)}  ({int(s)})" for g, s in zip(t.gosterge, t.tr_son_yil)], fontsize=8.8, color=YAZI)
    ax.set_xlim(*xlim)
    ax.set_ylim(-0.6, len(t) - 0.3)
    ax.grid(axis="x", color=IZGARA, lw=0.8)
    ax.set_axisbelow(True)
    sade(ax)
    virgul_eksen(ax, nd=0)
a1.set_xlabel("nüfus payı (%)")
a2.set_xlabel("ortalama puan (0–10)")
el = [Line2D([], [], marker="o", ls="", color=TURUNCU, ms=8, label="Türkiye"), Line2D([], [], marker="o", ls="", color=MAVI, ms=8, label="AB-27"),
      Line2D([], [], marker="o", ls="", mfc="none", mec=YAZI_3, ms=7, label="Türkiye 2006")]
a1.legend(handles=el, loc="lower right", frameon=False, fontsize=8.5, ncol=3, bbox_to_anchor=(1.0, 1.0))
fig.text(0.01, 0.02, "Kaynak: Eurostat EU-SILC (ilc_lvho05a, ilc_lvho07a, ilc_mddw01–03, ilc_mdho04, ilc_pw01, ilc_pw03), erişim 27.10.2026. "
         "Kod: 05_ANALIZ/kod/stres_veri.py, stres_grafikler.py", fontsize=7.5, color=YAZI_2)
kaydet(fig, "stres_turkiye_ab")

# --- 2. maruziyet dağılımı --------------------------------------------------------------------------------------------
d = pd.read_csv(SON / "stres_ilce_endeks.csv")
w = d.nufus_2025 / d.nufus_2025.sum() * 100
PAN = [("pm25", "PM2.5 (µg/m³, 2022–2024)", np.arange(8, 46, 2), [(5, "DSÖ kılavuzu 5"), (10, "AB 2030 sınırı 10"),
                                                                 (25, "AB bugünkü sınır 25")], MAVI),
       ("agac300", "300 m çevrede ağaç örtüsü (%, 2021)", np.arange(0, 62, 2), [(30, "model mahalle hedefi %30")], AQUA),
       ("lst", "Yaz gündüz yüzey sıcaklığı (°C, 2023–2024)", np.arange(24, 56, 1), [], TURUNCU)]
fig, axs = plt.subplots(1, 3, figsize=(14, 4.6))
fig.subplots_adjust(left=0.05, right=0.98, top=0.76, bottom=0.17, wspace=0.22)
fig.text(0.01, 0.95, "Türkiye nüfusu hangi çevrede yaşıyor?", fontsize=15, fontweight="bold", color=YAZI)
fig.text(0.01, 0.89, "Nüfusun ilçe ortalamalarına göre dağılımı (her çubuk: o aralıktaki ilçelerde yaşayan nüfus payı). "
         "İlçe ortalaması ilçe içi farkları gizler.", fontsize=9, color=YAZI_2)
for ax, (k, ad, kut, cizgi, renk) in zip(axs, PAN):
    h, b = np.histogram(d[k].clip(kut[0], kut[-1] - 1e-6), bins=kut, weights=w)
    ax.bar(b[:-1], h, width=np.diff(b) * 0.9, align="edge", color=renk, edgecolor=ZEMIN, lw=0.5)
    ort = np.average(d[k], weights=w)
    for x, et in cizgi:
        ax.axvline(x, color=YAZI, lw=0.9, ls=(0, (3, 2)))
        ax.text(x + (kut[1] - kut[0]) * 0.15, h.max() * 1.02, et, rotation=90, ha="left", va="top", fontsize=7.8, color=YAZI)
    ax.axvline(ort, color=YAZI_2, lw=1.4)
    ax.text(ort, h.max() * 1.12, f"ortalama {tr(ort)}", ha="center", va="bottom", fontsize=8.2, color=YAZI_2, fontweight="bold",
            bbox=dict(fc=ZEMIN, ec="none", pad=1.5), zorder=5)
    ax.set_title(ad, loc="left", fontsize=10.5, fontweight="bold", color=YAZI, pad=22)
    ax.set_ylabel("nüfus payı (%)" if k == "pm25" else "")
    ax.set_ylim(0, h.max() * 1.25)
    ax.set_xlim(min(kut[0], *(c[0] - 1 for c in cizgi)) if cizgi else kut[0], kut[-1])
    ax.grid(axis="y", color=IZGARA, lw=0.8)
    ax.set_axisbelow(True)
    sade(ax)
    virgul_eksen(ax, "y", 0)
axs[0].set_xlim(3, 46)
pm_ust = w[d.pm25 > 25].sum()
axs[0].text(45, h.max() * 0.0 + axs[0].get_ylim()[1] * 0.55, f"25 µg/m³ üstünde\nyaşayan nüfus: %{tr(pm_ust, 0)}", ha="right",
            fontsize=8.2, color=YAZI)
agac_alt = w[d.agac300 < 10].sum()
axs[1].text(60, axs[1].get_ylim()[1] * 0.55, f"ağaç örtüsü %10'un\naltında: nüfusun %{tr(agac_alt, 0)}'{iyelik(agac_alt)}", ha="right",
            fontsize=8.2, color=YAZI)
fig.text(0.01, 0.02, "Kaynak: ACAG V6.GL.03; ESA WorldCover 2021; MODIS MYD11A2; ilçe nüfusu TÜİK ADNKS 2025. Ölçüm: 03_VERI/kod/uydu_ulusal.py. "
         "Kod: 05_ANALIZ/kod/stres_grafikler.py", fontsize=7.5, color=YAZI_2)
kaydet(fig, "stres_maruziyet")

# --- 3. ilçe sınaması ---------------------------------------------------------------------------------------------
T = pd.read_csv(SON / "stres_ilce_sinama.csv")
T["yildiz"] = T.yildiz.fillna("")
SAT = [("KSY", "Kentsel stres yükü (KSY)"), ("s_pm25", "PM2.5"), ("s_isi", "Yaz yüzey sıcaklığı"), ("s_anayol", "Ana yol yakınlığı"),
       ("s_yapili", "Yapılı alan payı"), ("s_yesilsiz", "Ağaç ve yeşil eksikliği"), ("s_yukseklik", "Bina yüksekliği"),
       ("s_yogunluk", "Yaşanan yoğunluk"), ("C_lite_v2", "Karşılaştırma: Ç v0.2 (Rapor 13)")]
MOD = [("temel", "Temel: il sabit etkisi + kadın eğitimi + nüfus artışı", MAVI),
       ("+ kentsellik ve yaş yapısı", "Geniş: + ln yoğunluk + kent merkezi payı + 65+ payı", TURUNCU)]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw={"width_ratios": [1.25, 1]})
fig.subplots_adjust(left=0.2, right=0.98, top=0.78, bottom=0.11, wspace=0.28)
fig.text(0.01, 0.95, "Stres yükü yüksek ilçelerde ölümlülük daha yüksek (aynı il içinde)", fontsize=15, fontweight="bold", color=YAZI)
fig.text(0.01, 0.905, "973 ilçe · sonuç: yaşa göre standartlaştırılmış ölüm oranı (SMR, 2025) · nüfus ağırlıklı, il kümelenmiş güven aralığı. "
         "İlişki betimseldir, nedensellik göstermez.", fontsize=9, color=YAZI_2)
for j, (mk, mad, renk) in enumerate(MOD):
    for i, (k, ad) in enumerate(SAT):
        r = T[(T.endeks == k) & (T.model == mk)].iloc[0]
        y = len(SAT) - 1 - i + (0.17 if j == 0 else -0.17)
        a1.plot([r.ga_alt, r.ga_ust], [y, y], color=renk, lw=2, solid_capstyle="round")
        a1.scatter(r.beta, y, s=48 if k != "KSY" else 70, color=renk, zorder=3, edgecolor=ZEMIN, lw=1.2)
        a1.text(0.80, y, f"{tr(r.beta, 2)}{r.yildiz}", fontsize=8, color=YAZI, va="center", ha="left")
a1.axvline(0, color=YAZI_3, lw=0.9)
a1.axhline(0.5, color=IZGARA, lw=1)
a1.set_yticks(range(len(SAT)), [s[1] for s in SAT][::-1], fontsize=9, color=YAZI)
for t_ in a1.get_yticklabels():
    if t_.get_text().startswith("Kentsel"):
        t_.set_fontweight("bold")
a1.set_xlim(-0.6, 0.95)
a1.set_xlabel("1 SS artışta SMR'deki değişim (SS)")
a1.grid(axis="x", color=IZGARA, lw=0.8)
a1.set_axisbelow(True)
sade(a1)
virgul_eksen(a1, nd=1)
fig.legend(handles=[Line2D([], [], color=c, marker="o", lw=2, label=l) for _, l, c in MOD], loc="upper left",
           bbox_to_anchor=(0.01, 0.875), frameon=False, fontsize=8.3, ncol=2)
a1.set_title("Standartlaştırılmış katsayı ve %95 güven aralığı", loc="left", fontsize=10, color=YAZI, fontweight="bold")
# dilim grafiği: il sabit etkisi ve kontrollerden arındırılmış SMR, KSY onda birlik dilimlerine göre
p = pd.read_csv(KOK / "03_VERI" / "islenmis" / "ilce_paneli_genis.csv")[["gid", "egitim", "artis", "beklenen_olum_2025"]]
s = d.merge(p, on="gid").dropna(subset=["smr", "egitim", "artis"])
m = smf.wls("smr ~ egitim + artis + C(il)", s, weights=s.nufus_2025).fit()
s["art"] = s.smr - m.fittedvalues + np.average(s.smr, weights=s.nufus_2025)
s["dilim"] = pd.qcut(s.KSY, 10, labels=False) + 1
g = s.groupby("dilim").apply(lambda x: pd.Series({"ksy": x.KSY.mean(), "smr": np.average(x.art, weights=x.nufus_2025),
                                                  "nufus": x.nufus_2025.sum() / 1e6}))
a2.plot(g.ksy, g.smr, color=MAVI, lw=2, zorder=2)
a2.scatter(g.ksy, g.smr, s=g.nufus * 9 + 12, color=MAVI, edgecolor=ZEMIN, lw=1.5, zorder=3)
for i, (dx, dy, ha) in {1: (10, 6, "left"), 5: (10, -14, "left")}.items():
    a2.annotate(f"{i}. dilim · nüfus {tr(g.nufus[i], 1)} mn", (g.ksy[i], g.smr[i]), xytext=(dx, dy),
                textcoords="offset points", ha=ha, fontsize=7.8, color=YAZI_2)
a2.axhline(np.average(s.smr, weights=s.nufus_2025), color=YAZI_3, lw=0.8, ls=(0, (3, 2)))
a2.set_ylim(g.smr.min() - 0.01, g.smr.max() + 0.03)  # köşe notuna yer
a2.set_xlabel("KSY (onda birlik dilim ortalaması)")
a2.set_ylabel("SMR (il, eğitim ve artıştan arındırılmış)")
a2.set_title("KSY dilimlerine göre il içi SMR", loc="left", fontsize=10, color=YAZI, fontweight="bold")
a2.grid(color=IZGARA, lw=0.8)
a2.set_axisbelow(True)
sade(a2, sol=True)
virgul_eksen(a2, "y", 2)
virgul_eksen(a2, "x", 0)
r0 = T[(T.endeks == "KSY") & (T.model == "temel")].iloc[0]
r1 = T[(T.endeks == "KSY") & (T.model == "+ kentsellik ve yaş yapısı")].iloc[0]
a2.text(0.02, 0.97, f"KSY'de 10 puan artış ≈ SMR'de +%{tr(100 * r0.smr_10puan, 1)}\n(geniş modelde +%{tr(100 * r1.smr_10puan, 1)})\n"
        f"nokta büyüklüğü nüfus; 10. dilimde {tr(g.nufus[10], 1)} mn kişi",
        transform=a2.transAxes, va="top", fontsize=8.5, color=YAZI)
fig.text(0.01, 0.02, "Kaynak: stres_ilce_sinama.csv; SMR: TÜİK ölüm (MEDAS) ve ADNKS 2025 · Kod: 05_ANALIZ/kod/stres_endeks.py, "
         "stres_grafikler.py · *** p<0,001 ** p<0,01 * p<0,05 † p<0,10", fontsize=7.5, color=YAZI_2)
kaydet(fig, "stres_ilce_sinama")

# --- 4. il sınaması -------------------------------------------------------------------------------------------------
IL = pd.read_csv(SON / "stres_il_sinama.csv")
IL["yildiz"] = IL.yildiz.fillna("")
ETK = [("KSY_il", "Kentsel stres yükü (KSY)"), ("pm25_il", "PM2.5"), ("agac300_il", "Ağaç örtüsü"),
       ("s_yogunluk_il", "Yaşanan yoğunluk"), ("s_yukseklik_il", "Bina yüksekliği"), ("oda_basi_kisi_2021", "Oda başına kişi"),
       ("fiyat_gelir_2024", "Konut fiyatı / gelir"), ("tek_kisi_pay", "Tek kişilik hane payı"),
       ("otomobil_bin", "1.000 kişiye otomobil"), ("gurultu_sorunu_2015", "Sokak gürültüsü sorunu (algı)"),
       ("guvensiz_2015", "Gece güvende hissetmeyen (algı)")]
SNC = [("intihar", "Kaba intihar hızı 2014–2018", "oran oranı", 1.0), ("mutlu_2013", "Mutlu olanlar 2013", "yüzde puan", 0.0),
       ("gurultu_sorunu_2015", "Sokak gürültüsü sorunu 2015", "yüzde puan", 0.0),
       ("gece_guvende_2015", "Gece güvende hisseden 2015", "yüzde puan", 0.0)]
MD = [("kontrollü", "Kontrollü: kadın eğitim süresi, ln kişi başı GSYH, 65+ payı, doğu", MAVI),
      ("+ İBBS-1 SE", "+ 12 bölge sabit etkisi", TURUNCU)]
fig, axs = plt.subplots(1, 4, figsize=(15.5, 6.4), sharey=True)
fig.subplots_adjust(left=0.165, right=0.99, top=0.79, bottom=0.15, wspace=0.12)
fig.text(0.01, 0.95, "İl düzeyinde tablo zayıf: stres yükü intihar ve mutlulukla tutarlı ilişki vermiyor, algılanan gürültü ve güvensizlik veriyor",
         fontsize=13.5, fontweight="bold", color=YAZI)
fig.text(0.01, 0.905, "81 il · etkenlerin 1 SS artışına karşılık · intihar: Poisson (kişi-yıl ofseti), diğerleri EKK · sağlam %95 güven aralığı. "
         "Etkenler tek tek sınandı; Benjamini–Hochberg q değerleri stres_il_sinama.csv'de.", fontsize=9, color=YAZI_2)
for ax, (y, yad, birim, ref) in zip(axs, SNC):
    for j, (mk, mad, renk) in enumerate(MD):
        for i, (x, xad) in enumerate(ETK):
            r = IL[(IL.etken == x) & (IL.sonuc == y) & (IL.model == mk)]
            if r.empty:
                continue
            r = r.iloc[0]
            yy = len(ETK) - 1 - i + (0.16 if j == 0 else -0.16)
            ax.plot([r.ga_alt, r.ga_ust], [yy, yy], color=renk, lw=1.8, solid_capstyle="round", alpha=1 if r.p < 0.05 else 0.45)
            ax.scatter(r.etki, yy, s=36, color=renk, zorder=3, edgecolor=ZEMIN, lw=1, alpha=1 if r.p < 0.05 else 0.45)
    ax.axvline(ref, color=YAZI_3, lw=0.9)
    ax.axhline(len(ETK) - 1.5, color=IZGARA, lw=1)
    ax.set_title(yad, loc="left", fontsize=10, fontweight="bold", color=YAZI)
    ax.set_xlabel(birim)
    ax.grid(axis="x", color=IZGARA, lw=0.8)
    ax.set_axisbelow(True)
    sade(ax)
    virgul_eksen(ax, nd=2 if birim == "oran oranı" else 0)
axs[0].set_yticks(range(len(ETK)), [e[1] for e in ETK][::-1], fontsize=9, color=YAZI)
axs[0].get_yticklabels()[-1].set_fontweight("bold")
fig.legend(handles=[Line2D([], [], color=c, marker="o", lw=2, label=l) for _, l, c in MD] +
           [Line2D([], [], color=GRI, marker="o", lw=2, label="soluk: p ≥ 0,05")], loc="lower left", bbox_to_anchor=(0.16, 0.035),
           frameon=False, fontsize=8.3, ncol=3)
fig.text(0.01, 0.008, "Kaynak: TÜİK intihar 2014–2018 ve YMA 2013, İLYE 2015 (Wayback arşivi), Bina ve Konut Nitelikleri 2021, Aile 2025, "
         "SDMX otomobil 2026; TCMB/Rapor 04 fiyat-gelir 2024 · Kod: 05_ANALIZ/kod/stres_endeks.py, stres_grafikler.py",
         fontsize=7.3, color=YAZI_2)
kaydet(fig, "stres_il_sinama")

# --- 5. şema: etken → mekanizma → sonuç ------------------------------------------------------------------------------
ETKEN = [  # (ad, grup, kanıt etiketi, Türkiye ölçeği, mekanizmalar)
    ("Gürültü", 0, "MA", "il algı", [0, 1]), ("Hava kirliliği", 0, "MA", "ilçe", [2, 0]), ("Isı", 0, "MA", "ilçe", [1, 0]),
    ("Gece ışık kirliliği", 0, "D", "ulusal", [1]), ("Gün ışığı eksikliği", 0, "B", "ulusal", [1]),
    ("Yeşil eksikliği", 1, "MA", "ilçe", [3, 4, 2]), ("Görsel tekdüzelik", 1, "Ö", "yok", [3]),
    ("Yükseklik ve yoğunluk", 1, "D", "ilçe", [5, 0]), ("Kalabalık konut", 1, "D", "il", [0, 1, 5]),
    ("İşe gidiş ve trafik", 2, "B", "ulusal", [4, 0]), ("Yalnızlık, kopukluk", 2, "MA", "il vekil", [5, 0, 2]),
    ("Güvensizlik, suç korkusu", 2, "B", "il algı", [0, 4]), ("Konut maliyet yükü", 2, "D", "il", [0, 4]),
]
MEK = ["Kronik stres yanıtı\nHPA ekseni, kortizol, sempatik uyarılma", "Uyku ve sirkadiyen\nritim bozulması",
       "Sistemik inflamasyon,\noksidatif stres", "Dikkat yorgunluğu,\nonarım eksikliği", "Hareketsizlik ve\nzaman yoksulluğu",
       "Toplumsal destek ve\ndenetim duygusu kaybı"]
SONUC = ["Kalp-damar hastalığı,\nhipertansiyon", "Depresyon ve anksiyete", "Uyku bozukluğu", "İntihar ve kendine zarar",
         "Düşük yaşam memnuniyeti", "Erken ölüm (tüm nedenler)"]
MS = {0: [0, 1, 5], 1: [2, 1, 0], 2: [0, 5, 1], 3: [1, 4], 4: [0, 5, 4], 5: [1, 3, 4, 5]}
GRUP = [("Fiziksel çevre", MAVI), ("Biçim, yeşil ve yoğunluk", TURUNCU), ("Toplumsal ve iktisadi", AQUA)]
fig = plt.figure(figsize=(15, 9.6))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 15)
ax.set_ylim(0, 9.6)
ax.set_axis_off()
ax.text(0.3, 9.25, "Kentsel stres etkenleri nasıl sağlığa dönüşür?", fontsize=17, fontweight="bold", color=YAZI)
ax.text(0.3, 8.9, "Çizgiler ana mekanizmaları gösterir (kanıt düzeyi kutudaki etikette). Şema basitleştirilmiştir; her etken birden çok yoldan "
        "etki eder.", fontsize=9.5, color=YAZI_2)
XE, XM, XS = 0.3, 6.0, 11.3
WE, WM, WS = 3.6, 3.5, 3.4
ye = np.linspace(8.25, 1.0, len(ETKEN))
ym = np.linspace(7.7, 1.5, len(MEK))
ys = np.linspace(7.7, 1.5, len(SONUC))
for i, (ad, gr, kn, tro, mek) in enumerate(ETKEN):
    for k in mek:
        ax.plot([XE + WE, XM], [ye[i], ym[k]], color=GRUP[gr][1], lw=1.1, alpha=0.55, zorder=1)
for k, ss in MS.items():
    for j in ss:
        ax.plot([XM + WM, XS], [ym[k], ys[j]], color=YAZI_3, lw=1.1, alpha=0.6, zorder=1)
for i, (ad, gr, kn, tro, mek) in enumerate(ETKEN):
    ax.add_patch(FancyBboxPatch((XE, ye[i] - 0.22), WE, 0.44, boxstyle="round,pad=0,rounding_size=0.06", fc=ZEMIN,
                                ec=GRUP[gr][1], lw=1.4, zorder=2))
    ax.add_patch(FancyBboxPatch((XE, ye[i] - 0.22), 0.12, 0.44, boxstyle="square,pad=0", fc=GRUP[gr][1], ec="none", zorder=3))
    ax.text(XE + 0.25, ye[i], ad, va="center", fontsize=9.5, color=YAZI, zorder=4)
    ax.text(XE + WE - 0.1, ye[i], f"{kn} · TR: {tro}", va="center", ha="right", fontsize=7.6, color=YAZI_2, zorder=4)
for k, ad in enumerate(MEK):
    ax.add_patch(FancyBboxPatch((XM, ym[k] - 0.38), WM, 0.76, boxstyle="round,pad=0,rounding_size=0.08", fc="#f3f2ef", ec=YAZI_3,
                                lw=1, zorder=2))
    ax.text(XM + 0.18, ym[k], ad, va="center", fontsize=9, color=YAZI, zorder=4, linespacing=1.3)
for j, ad in enumerate(SONUC):
    ax.add_patch(FancyBboxPatch((XS, ys[j] - 0.34), WS, 0.68, boxstyle="round,pad=0,rounding_size=0.08", fc=ZEMIN, ec=YAZI, lw=1.2,
                                zorder=2))
    ax.text(XS + 0.18, ys[j], ad, va="center", fontsize=9.5, color=YAZI, zorder=4, fontweight="bold", linespacing=1.3)
for x, t in [(XE, "ETKEN"), (XM, "MEKANİZMA"), (XS, "SAĞLIK SONUCU")]:
    ax.text(x, 8.6, t, fontsize=9, color=YAZI_2, fontweight="bold")
for i, (ad, renk) in enumerate(GRUP):
    ax.add_patch(FancyBboxPatch((0.3 + i * 3.1, 0.42), 0.25, 0.18, boxstyle="square,pad=0", fc=renk, ec="none"))
    ax.text(0.65 + i * 3.1, 0.51, ad, va="center", fontsize=8.5, color=YAZI)
ax.text(0.3, 0.17, "Kanıt: MA meta-analiz · D sistematik derleme ya da derleme · B boylamsal/kohort çalışma · Ö öncül ya da nitel çalışma. "
        "TR: Türkiye'de ölçülebildiği en ince ölçek (ilçe, il, ulusal; \"algı\" anket, \"vekil\" dolaylı gösterge). "
        "Kaynaklar: 02_LITERATUR/stres_literatur.md", va="center", fontsize=8, color=YAZI_2)
kaydet(fig, "stres_sema")
