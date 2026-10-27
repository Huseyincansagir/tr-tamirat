"""
Faz 4 · Rapor 7 — grafikler
==========================
Girdi: 05_ANALIZ/sonuclar/ekonomi_*.csv (ekonomi_veri.py, ekonomi_dagilim.py, ekonomi_ticaret_yeterlilik.py)
Çıktı: 05_ANALIZ/grafikler/ekonomi_*.png|svg
"""
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
SON = KOK / "05_ANALIZ" / "sonuclar"
GRAF = KOK / "05_ANALIZ" / "grafikler"
MAVI, TURUNCU, AQUA, SARI = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
YAZI, YAZI_2, YAZI_3, ZEMIN, IZGARA = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e8e7e3"
GRI = "#b9b8b3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "axes.edgecolor": YAZI_3, "axes.labelcolor": YAZI_2, "xtick.color": YAZI_2, "ytick.color": YAZI_2,
                     "axes.titlesize": 10, "svg.fonttype": "none"})


def tr(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


VIRGUL = mt.FuncFormatter(lambda v, _: tr(v, 0) if abs(v - round(v)) < 1e-9 else tr(v, 1))
BINLIK = mt.FuncFormatter(lambda v, _: tr(v / 1000, 0))


def sade(ax, y_izgara=True):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(IZGARA)
    if y_izgara:
        ax.grid(axis="y", color=IZGARA, lw=0.7)
        ax.set_axisbelow(True)
    ax.tick_params(length=0)


def baslik(fig, ust, alt, kaynak):
    """Başlık, alt başlık ve kaynak; uzun metinleri figür genişliğine göre satırlara böler ve eksenleri gerekirse
    aşağı/yukarı sıkıştırarak metinle çakışmayı önler (eksenlerin göreli düzeni korunur)."""
    W, H = fig.get_figwidth(), fig.get_figheight()
    alt_s = textwrap.fill(alt, width=int(W * 15.3))
    kay_s = textwrap.fill(kaynak, width=int(W * 17.5))
    n_alt, n_kay = alt_s.count("\n") + 1, kay_s.count("\n") + 1
    y_ust = 1 - 0.10 / H
    fig.text(0.012, y_ust, ust, fontsize=12.5, fontweight="bold", color=YAZI, va="top")
    y_alt = y_ust - 0.27 / H
    fig.text(0.012, y_alt, alt_s, fontsize=8.8, color=YAZI_2, va="top", linespacing=1.3)
    fig.text(0.012, 0.012, kay_s, fontsize=7.2, color=YAZI_3, va="bottom", linespacing=1.3)
    ust_sinir = y_alt - (n_alt * 0.165 + 0.40) / H          # eksen başlığı için yer
    eksenler = [a for a in fig.axes if a.get_visible()]
    y0 = min(a.get_position().y0 for a in eksenler)
    y1 = max(a.get_position().y1 for a in eksenler)
    alt_ek = max(0.0, (n_kay - 1) * 0.13 / H)                 # ikinci kaynak satırı için yer
    yeni0, yeni1 = y0 + alt_ek, min(y1, ust_sinir)
    if yeni0 != y0 or yeni1 != y1:
        olcek = (yeni1 - yeni0) / (y1 - y0)
        for a in eksenler:
            p = a.get_position()
            a.set_position([p.x0, yeni0 + (p.y0 - y0) * olcek, p.width, p.height * olcek])


def kaydet(fig, ad):
    for uz in ("png", "svg"):
        fig.savefig(GRAF / f"{ad}.{uz}", dpi=200)
    plt.close(fig)
    print("  ->", ad)


# =========================================================================== 1. Eşitsizlik
g = pd.read_csv(SON / "ekonomi_gelir_dagilimi.csv")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.4))
fig.subplots_adjust(left=0.06, right=0.97, top=0.76, bottom=0.14, wspace=0.28)
d = g.dropna(subset=["gini_TR"])
a1.plot(d.yil, d.gini_TR / 100, color=MAVI, lw=2.2)
a1.plot(d.yil, d.gini_EU27_2020 / 100, color=GRI, lw=2)
o = g.dropna(subset=["oecd_gini_piyasa"])
for parca in (o[o.yil <= 2015], o[o.yil >= 2017]):  # 2016 yok; 2017'de seri kırılması
    a1.plot(parca.yil, parca.oecd_gini_piyasa, color=TURUNCU, lw=1.6, ls="--")
    a1.plot(parca.yil, parca.oecd_gini_kullanilabilir, color=TURUNCU, lw=1.6)
a1.axvline(2016, color=IZGARA, lw=0.8, ls=":")
a1.text(2016.15, 0.552, "OECD serisinde\nkırılma", fontsize=6.8, color=YAZI_3, va="top")
a1.text(2025.3, d.gini_TR.iloc[-1] / 100, "Türkiye\n(Eurostat)", color=MAVI, fontsize=7.8, va="center")
a1.text(2025.3, d.gini_EU27_2020.iloc[-1] / 100, "AB-27", color=YAZI_3, fontsize=7.8, va="center")
a1.text(2022.3, o.oecd_gini_piyasa.iloc[-1], "piyasa geliri\n(OECD)", color=TURUNCU, fontsize=7.5, va="center")
a1.text(2011.0, 0.383, "kullanılabilir gelir (OECD)", color=TURUNCU, fontsize=7.5, va="top")
a1.scatter([2025], [0.410], color=YAZI, s=22, zorder=5)
a1.annotate("TÜİK ulusal\nbülten 0,410", (2025, 0.410), xytext=(2019.2, 0.345), fontsize=7.5, color=YAZI_2,
            arrowprops=dict(arrowstyle="-", color=YAZI_3, lw=0.7))
a1.set_xlim(2010.5, 2028.3)
a1.set_ylim(0.27, 0.56)
a1.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: tr(v, 2)))
a1.set_title("Gini katsayısı (eşdeğer gelir)", loc="left", fontweight="bold")
sade(a1)
d2 = g.dropna(subset=["s80s20_TR"])
a2.plot(d2.yil, d2.s80s20_TR, color=MAVI, lw=2.2)
e = g.dropna(subset=["s80s20_EU27_2020"])
a2.plot(e.yil, e.s80s20_EU27_2020, color=GRI, lw=2)
a2.text(2025.3, d2.s80s20_TR.iloc[-1], f"Türkiye {tr(d2.s80s20_TR.iloc[-1])}", color=MAVI, fontsize=7.8, va="center")
a2.text(2025.3, e.s80s20_EU27_2020.iloc[-1], f"AB-27 {tr(e.s80s20_EU27_2020.iloc[-1])}", color=YAZI_3, fontsize=7.8, va="center")
a2.set_xlim(2005.5, 2029.5)
a2.set_ylim(0, 12.5)
a2.yaxis.set_major_formatter(VIRGUL)
a2.set_title("S80/S20: en zengin %20 / en yoksul %20", loc="left", fontweight="bold")
sade(a2)
baslik(fig, "Türkiye'de Gini AB'nin 1,5, S80/S20 oranı 2 katı; eşitsizlik 2014'ten beri yatay",
       "Gini 2014'ten beri 0,41–0,45 bandında; en zengin beşte bir, en yoksul beşte birin ≈9 katı gelir alıyor. "
       "Vergi ve transferler piyasa Gini'sini ≈0,10 puan düşürüyor (OECD, 2022). OECD serisinde 2017'de kırılma var: kamu "
       "transferlerinin gelirdeki payı %5'ten %20'ye sıçrıyor; emekli aylıkları büyük olasılıkla bu yıldan itibaren transfer sayılıyor.",
       "Kaynak: Eurostat ilc_di12, ilc_di11 (TÜİK AB-GYKA verisi, anket yılı); OECD IDD (gelir yılı); TÜİK Gelir Dağılımı "
       "İstatistikleri 2025 (basın aktarımı). Eurostat ve TÜİK ulusal değerleri yöntem farkı nedeniyle ayrışıyor.")
kaydet(fig, "ekonomi_gelir_esitsizlik")

# =========================================================================== 2. Ücret, eşik, kira
e = pd.read_csv(SON / "ekonomi_ucret_esik_aylik.csv")
e["t"] = pd.to_datetime(e.ay + "-01")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.2, 4.8), gridspec_kw={"width_ratios": [1.45, 1]})
fig.subplots_adjust(left=0.06, right=0.93, top=0.77, bottom=0.12, wspace=0.5)
# (sütun, etiket, renk, çizgi kalınlığı, etiketin y konumu: bin TL; çakışmayı önlemek için elle)
seri = [("yoksulluk_siniri", "Yoksulluk sınırı", YAZI_3, 1.6, 123),
        ("en_dusuk_memur_maasi", "En düşük memur", YAZI, 1.4, 70),
        ("aclik_siniri", "Açlık sınırı", TURUNCU, 2.0, 44),
        ("net_asgari_ucret", "Net asgari ücret", MAVI, 2.2, 36),
        ("kira_100m2", "100 m² kira", SARI, 2.0, 28),
        ("en_dusuk_emekli_ayligi", "En düşük emekli", AQUA, 2.0, 20)]
for c, ad, renk, lw, y_et in seri:
    a1.plot(e.t, e[c], color=renk, lw=lw,
            drawstyle="steps-post" if c in ("net_asgari_ucret", "en_dusuk_emekli_ayligi", "en_dusuk_memur_maasi") else "default")
    son = e.dropna(subset=[c]).iloc[-1]
    a1.text(son.t + pd.Timedelta(days=25), y_et * 1000, f"{ad} {tr(son[c] / 1000, 1)}", color=renk, fontsize=7.2,
            va="center")
a1.yaxis.set_major_formatter(BINLIK)
a1.set_ylabel("bin TL / ay")
a1.set_title("Aylık tutarlar (bin TL), Ocak 2023 – Eylül 2026", loc="left", fontweight="bold")
a1.xaxis.set_major_locator(matplotlib.dates.YearLocator())
a1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y"))
a1.set_xlim(e.t.iloc[0], e.t.iloc[-1] + pd.Timedelta(days=20))
sade(a1)
for c, ad, renk in [("net_asgari_ucret_aclik_orani", "asgari ücret / açlık sınırı", MAVI),
                    ("en_dusuk_emekli_ayligi_aclik_orani", "en düşük emekli aylığı / açlık sınırı", AQUA),
                    ("kira_net_asgari_ucret_orani", "100 m² kira / asgari ücret", SARI)]:
    a2.plot(e.t, e[c], color=renk, lw=2)
    son = e.dropna(subset=[c]).iloc[-1]
    a2.text(son.t + pd.Timedelta(days=25), son[c], f"{tr(son[c], 2)}", color=renk, fontsize=7.8, va="center")
a2.axhline(1, color=YAZI_3, lw=0.8, ls=":")
a2.text(e.t.iloc[-1], 1.035, "1 = tam karşılıyor", fontsize=7, color=YAZI_3, ha="right")
a2.text(e.t.iloc[1], 1.21, "100 m² kira / asgari ücret", color=SARI, fontsize=7.3)
a2.text(e.t.iloc[1], 0.70, "en düşük emekli aylığı / açlık sınırı", color=AQUA, fontsize=7.3)
a2.text(e.t.iloc[16], 1.14, "asgari ücret / açlık sınırı", color=MAVI, fontsize=7.3)
a2.set_ylim(0.4, 1.3)
a2.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: tr(v, 1)))
a2.xaxis.set_major_locator(matplotlib.dates.YearLocator())
a2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y"))
a2.set_title("Oranlar", loc="left", fontweight="bold")
sade(a2)
baslik(fig, "Asgari ücret açlık sınırının altına indi; 100 m² konutun kirası bir asgari ücrete yaklaştı",
       "Eylül 2026: net asgari ücret açlık sınırının %74'ü, yoksulluk sınırının %23'ü; en düşük emekli aylığı açlık sınırının "
       "%62'si; en düşük memur maaşı (aile yardımı dahil) 1,86 katı. Açlık ve yoksulluk sınırı 4 kişilik aile için; gelirler tek "
       "kişinin geliri. Kira: TCMB birim kirası × 100 m².",
       "Kaynak: TÜRK-İŞ Açlık ve Yoksulluk Sınırı (Eylül 2026, TASE endeksinden aylık seri); GİB asgari ücret kesintileri; "
       "SGK taban aylığı ve memur maaşı (basın aktarımı); TCMB EVDS TP.BK.TR (değerleme raporlarına dayalı birim kira, çeyreklik).")
kaydet(fig, "ekonomi_ucret_esik")

# =========================================================================== 3. İşgücü
i = pd.read_csv(SON / "ekonomi_isgucu_ceyrek.csv")
i = i[i.ceyrek >= "2014-Q1"].copy()
i["x"] = i.ceyrek.str[:4].astype(int) + (i.ceyrek.str[-1].astype(int) - 1) / 4
fig, ax = plt.subplots(figsize=(9, 4.2))
fig.subplots_adjust(left=0.07, right=0.83, top=0.76, bottom=0.14)
ax.plot(i.x, i.atil_isgucu_mda, color=TURUNCU, lw=2.2)
ax.plot(i.x, i.issizlik_mda, color=MAVI, lw=2.2)
for c, ad, renk in [("atil_isgucu_mda", "Atıl işgücü oranı\n(geniş tanımlı işsizlik)", TURUNCU), ("issizlik_mda", "İşsizlik oranı", MAVI)]:
    son = i.dropna(subset=[c]).iloc[-1]
    ax.text(son.x + 0.2, son[c], f"{ad}\n%{tr(son[c])} ({son.ceyrek.replace('-Q', ' Ç')})", color=renk, fontsize=7.8, va="center")
ax.fill_between(i.x, i.issizlik_mda, i.atil_isgucu_mda, color=TURUNCU, alpha=0.08, lw=0)
ax.text(2020.6, 17, "aradaki fark: iş aramayan ama çalışmaya hazır olanlar\nve daha çok çalışmak isteyen eksik istihdamdakiler",
        fontsize=7.4, color=YAZI_2)
ax.set_ylim(0, 35)
ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"%{tr(v, 0)}"))
ax.set_xlim(2014, 2026.6)
sade(ax)
baslik(fig, "İşsizlik düşerken geniş tanımlı işsizlik yükseldi",
       "Mevsim etkisinden arındırılmış çeyreklik seriler, 15+ yaş. Dar tanım %8 dolayında; atıl işgücü 2026'da %30'u aştı.",
       "Kaynak: TÜİK SDMX DF_ISGUCU_CEYREK_TEMEL_ISGUCU_C ve DF_ISGUCU_CEYREK_TAMAMLAYICI_GOSTERGE_C (27.10.2026).")
kaydet(fig, "ekonomi_isgucu")

# =========================================================================== 4. Gelir türleri
h = pd.read_csv(SON / "ekonomi_hanehalki_sektor_hesaplari.csv")
h = h[h.yil >= 2014].reset_index(drop=True)  # 2009–2013'te B2A3G ve D42 arasında olası tanım farkı [DY]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.5), gridspec_kw={"width_ratios": [1.5, 1]})
fig.subplots_adjust(left=0.06, right=0.97, top=0.76, bottom=0.14, wspace=0.35)
kat = [("pay_D1", "Ücret ve maaş (işgören ödemeleri)", MAVI), ("pay_B2A3G", "İşletme artığı ve karma gelir\n(esnaf, çiftçi, ev sahipliği)", AQUA),
       ("pay_D4", "Mülk geliri (faiz, kâr payı, rant)", TURUNCU), ("pay_D62", "Sosyal yardımlar (çoğu emekli aylığı)", SARI)]
alt = np.zeros(len(h))
for c, ad, renk in kat:
    a1.fill_between(h.yil, alt, alt + h[c], color=renk, alpha=0.85, lw=0, step=None)
    orta = alt[-1] + h[c].iloc[-1] / 2
    a1.text(2025.4, orta, f"{ad}  %{tr(h[c].iloc[-1], 0)}", fontsize=7.2, color=renk if renk != SARI else "#9a6a00", va="center")
    alt = alt + h[c].values
a1.set_xlim(2014, 2025)
a1.set_ylim(0, 100)
a1.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"%{tr(v, 0)}"))
a1.set_title("Hanehalkının gelir kaynakları (ulusal hesaplar)", loc="left", fontweight="bold")
sade(a1, False)
a1.set_position([0.06, 0.14, 0.38, 0.62])
gy = [("Maaş ve ücret", 49.7, MAVI), ("Müteşebbis geliri", 18.3, AQUA), ("Sosyal transferler", 18.2, SARI),
      ("Diğer (mülk geliri ve\nhaneler arası transfer)", 13.8, TURUNCU)]
a2.barh(range(4)[::-1], [v for _, v, _ in gy], color=[r for *_, r in gy], height=0.6)
for k, (ad, v, _) in enumerate(gy):
    a2.text(v + 1, 3 - k, f"%{tr(v)}", va="center", fontsize=8, color=YAZI)
a2.set_yticks(range(4)[::-1], [a for a, *_ in gy], fontsize=8)
a2.set_xlim(0, 62)
a2.xaxis.set_visible(False)
a2.set_title("Anket (GYKA 2025)", loc="left", fontweight="bold")
sade(a2, False)
a2.set_position([0.76, 0.14, 0.21, 0.62])
baslik(fig, "Hanehalkı geliri, 2014–2025: ücretin payı %36 → %42, mülk gelirinin payı %29 → %17",
       "Ulusal hesaplarda birincil gelir ve sosyal yardımların bileşimi. Mülk geliri içinde faizin payı 2020'den sonra arttı "
       "(%3 → %8). Sağ: GYKA 2025 anketinde kullanılabilir gelirin kaynakları; emekli ve dul-yetim aylıkları sosyal transferlerin %89'u.",
       "Kaynak: TÜİK SDMX DF_KURUMSAL_SEKTOR_HESAPLARI_CARI_FIYATLARLA_V2 (S1M; D1, B2A3G, D4, D62 alacak); TÜİK Gelir Dağılımı "
       "İstatistikleri 2025 (basın aktarımı); 'diğer' kalan olarak hesaplandı.")
kaydet(fig, "ekonomi_gelir_turleri")

# =========================================================================== 5. Vergi yapısı
v = pd.read_csv(SON / "ekonomi_vergi_yapisi_myb.csv")
ro = pd.read_csv(SON / "ekonomi_vergi_oecd.csv").set_index("yil")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.8, 4.6), gridspec_kw={"width_ratios": [1.25, 1]})
fig.subplots_adjust(left=0.06, right=0.98, top=0.76, bottom=0.14, wspace=0.55)
for c, ad, renk in [("pay_dolayli_genis", "Dolaylı vergiler (geniş)", TURUNCU), ("pay_kdv_otv", "KDV + ÖTV", SARI),
                    ("pay_gelir_vergisi", "Gelir vergisi", MAVI), ("pay_kurumlar_vergisi", "Kurumlar vergisi", AQUA),
                    ("pay_mulkiyet_vergileri", "Mülkiyet vergileri (MTV, veraset)", YAZI_3)]:
    a1.plot(v.yil, v[c], color=renk, lw=2.1)
    a1.text(2025.4, v[c].iloc[-1] + (1.6 if c == "pay_gelir_vergisi" else -1.6 if c == "pay_kurumlar_vergisi" else 0),
            f"{ad} %{tr(v[c].iloc[-1], 0)}", color=renk, fontsize=7.3, va="center")
a1.set_xlim(2006, 2025)
a1.xaxis.set_major_locator(mt.MultipleLocator(4))
a1.xaxis.set_major_formatter(mt.FuncFormatter(lambda v_, _: f"{v_:.0f}"))
a1.set_ylim(0, 75)
a1.yaxis.set_major_formatter(mt.FuncFormatter(lambda v_, _: f"%{tr(v_, 0)}"))
a1.set_title("Merkezi bütçe vergi gelirleri içindeki pay", loc="left", fontweight="bold")
sade(a1)
a1.set_position([0.06, 0.14, 0.33, 0.62])
kal = [("mal_hizmet", "Mal ve hizmet vergileri"), ("kdv", "  KDV"), ("ozel_tuketim", "  Özel tüketim vergileri"),
       ("sosyal_guvenlik", "Sosyal güvenlik primleri"), ("kisisel_gelir_vergisi", "Kişisel gelir vergisi"),
       ("kurumlar_vergisi", "Kurumlar vergisi"), ("mulk_vergileri", "Mülk vergileri")]
yy = np.arange(len(kal))[::-1]
trv = [ro.loc[2024, f"TUR_pay_{k}"] for k, _ in kal]
oev = [ro.loc[2023, f"OECD_REP_pay_{k}"] for k, _ in kal]
a2.barh(yy + 0.18, trv, height=0.34, color=MAVI, label="Türkiye 2024")
a2.barh(yy - 0.18, oev, height=0.34, color=GRI, label="OECD ortalaması 2023")
for y_, a_, b_ in zip(yy, trv, oev):
    a2.text(a_ + 0.6, y_ + 0.18, tr(a_, 1), va="center", fontsize=7.2, color=MAVI)
    a2.text(b_ + 0.6, y_ - 0.18, tr(b_, 1), va="center", fontsize=7.2, color=YAZI_3)
a2.set_yticks(yy, [a for _, a in kal], fontsize=8)
a2.set_xlim(0, 52)
a2.xaxis.set_major_formatter(mt.FuncFormatter(lambda v_, _: f"%{tr(v_, 0)}"))
a2.legend(frameon=False, fontsize=7.6, loc="lower right")
a2.set_title("Toplam vergi ve prim gelirindeki pay", loc="left", fontweight="bold")
sade(a2, False)
a2.grid(axis="x", color=IZGARA, lw=0.7)
a2.set_position([0.66, 0.14, 0.32, 0.62])
baslik(fig, "Vergi yükünün ağırlığı tüketimde; gelir ve mülk vergisi OECD'nin çok altında",
       "Dolaylı vergilerin bütçe vergi gelirindeki payı 2006'da %68, 2025'te %62. Taşınmaz vergileri GSYH'nin %0,10'u "
       "(OECD %0,95).",
       "Kaynak: Muhasebat 2006–2025 merkezi yönetim bütçe gelirleri; OECD Revenue Statistics (DF_RSOECD). Geniş tanım: dahilde mal ve "
       "hizmet vergileri + dış ticaret vergileri + damga + harç.")
kaydet(fig, "ekonomi_vergi_yapisi")

# =========================================================================== 6. Etkin oranlar
et = pd.read_csv(SON / "ekonomi_etkin_vergi_oranlari.csv")
et["etiket"] = et.gelir_turu + " — " + et.ornek
et = et.iloc[::-1].reset_index(drop=True)
renk = et.gelir_turu.map(lambda s: MAVI if s == "ücret" else SARI if "kira" in s else TURUNCU if ("faiz" in s or "temettü" in s)
                         else AQUA)
fig, ax = plt.subplots(figsize=(9.2, 5.4))
fig.subplots_adjust(left=0.37, right=0.95, top=0.82, bottom=0.11)
ax.barh(range(len(et)), et.etkin_vergi_pct, color=renk, height=0.62)
for k, r in et.iterrows():
    ax.text(r.etkin_vergi_pct + 0.4, k, f"%{tr(r.etkin_vergi_pct, 1)}", va="center", fontsize=7.8, color=YAZI)
ax.set_yticks(range(len(et)), et.etiket, fontsize=8)
ax.set_xlim(0, 30)
ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v_, _: f"%{tr(v_, 0)}"))
sade(ax, False)
ax.grid(axis="x", color=IZGARA, lw=0.7)
baslik(fig, "Aynı tutarda gelir, türüne göre çok farklı vergileniyor (2026)",
       "Gelir vergisi + damga vergisinin brüt gelire oranı. Ücrette işçi primleri (%15) hariç; kira örneği başka geliri olmayan "
       "kişi, 58.000 TL istisna ve %15 götürü gider.",
       "Kaynak: GİB 2026 gelir vergisi tarifesi, konut kira istisnası, GVK 94 ve Geçici md. 67 kesinti oranları (hesap: "
       "05_ANALIZ/kod/ekonomi_veri.py). Faizde oran nominal getiriye uygulanır; reel getiriye oranla etkin yük daha yüksektir.")
kaydet(fig, "ekonomi_etkin_oranlar")

# =========================================================================== 7. Ticaret
pm = pd.read_csv(SON / "ekonomi_ticaret_pmr.csv")
pm = pm[pm.TIME_PERIOD == 2023].sort_values("turkiye")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.8, 4.6), gridspec_kw={"width_ratios": [1.5, 1]})
fig.subplots_adjust(left=0.27, right=0.97, top=0.76, bottom=0.14, wspace=0.45)
yy = np.arange(len(pm))
a1.hlines(yy, pm.oecd_ortalama, pm.turkiye, color=IZGARA, lw=3)
a1.scatter(pm.oecd_ortalama, yy, color=GRI, s=40, zorder=3, label="OECD ortalaması")
a1.scatter(pm.turkiye, yy, color=MAVI, s=46, zorder=4, label="Türkiye")
for y_, r in zip(yy, pm.itertuples()):
    a1.text(max(r.turkiye, r.oecd_ortalama) + 0.12, y_, f"{tr(r.turkiye, 2)} ({int(r.turkiye_sira_kisitlayicidan)}./38)",
            va="center", fontsize=7.2, color=MAVI)
a1.set_yticks(yy, pm.olcu, fontsize=8)
a1.set_xlim(0, 5.2)
a1.xaxis.set_major_formatter(VIRGUL)
a1.set_xlabel("0 = en serbest, 6 = en kısıtlayıcı")
a1.legend(frameon=False, fontsize=7.6, loc="lower right")
a1.set_title("OECD ürün piyasası düzenlemesi (PMR) 2023", loc="left", fontweight="bold")
sade(a1, False)
ht = pd.read_csv(SON / "ekonomi_ticaret_perakende.csv").set_index("gosterge")
lab = [("Organize kanalın HTM cirosundaki payı (%)", "Zincir ve organize\nmarketlerin ciro payı"),
       ("Toplam HTM pazarında ilk 4 zincirin payı, CR4 (%)", "İlk 4 zincirin\ntoplam pazardaki payı")]
for k, (anah, ad) in enumerate(lab):
    a2.bar(k - 0.18, ht.loc[anah, "y2019"], width=0.34, color=GRI)
    a2.bar(k + 0.18, ht.loc[anah, "y2021"], width=0.34, color=TURUNCU)
    a2.text(k - 0.18, ht.loc[anah, "y2019"] + 1.2, f"%{tr(ht.loc[anah, 'y2019'])}", ha="center", fontsize=7.6, color=YAZI_2)
    a2.text(k + 0.18, ht.loc[anah, "y2021"] + 1.2, f"%{tr(ht.loc[anah, 'y2021'])}", ha="center", fontsize=7.6, color=TURUNCU)
a2.set_xticks([0, 1], [b for _, b in lab], fontsize=8)
a2.set_ylim(0, 70)
a2.yaxis.set_visible(False)
a2.text(-0.36, 64, "■ 2019", color=GRI, fontsize=8)
a2.text(0.15, 64, "■ 2021", color=TURUNCU, fontsize=8)
a2.set_title("HTM perakendesinde yoğunlaşma", loc="left", fontweight="bold")
sade(a2, False)
baslik(fig, "Türkiye OECD'nin en kısıtlayıcı ürün piyasası düzenlemesine sahip; perakende hızla yoğunlaşıyor",
       "Genel PMR, idari yük, giriş engelleri ve fiyat kontrollerinde 38 üye içinde son sırada. Perakende dağıtımın "
       "kendi kuralları ise OECD ortalamasında.",
       "Kaynak: OECD PMR 2023 (DSD_PMR@DF_PMR, 38 üyenin basit ortalaması hesaplandı); Rekabet Kurumu HTM Perakendeciliği Sektör "
       "İncelemesi Nihai Raporu 2023, Tablo 2 ve 6 (Nielsen verisi).")
kaydet(fig, "ekonomi_ticaret")

# =========================================================================== 8. Yeterlilik
bt = pd.read_csv(SON / "ekonomi_yeterlilik_bitkisel.csv").set_index("urun")
yil_k = [c for c in bt.columns if "/" in c]
bt = bt.drop(index=["Fındık", "Tahıl toplamı", "Sebze toplamı"])
son = bt[yil_k].apply(lambda r: r.dropna().iloc[-1], axis=1)
son_yil = bt[yil_k].apply(lambda r: r.dropna().index[-1], axis=1)
bt = bt.assign(son=son, son_yil=son_yil, ust=bt[yil_k].max(axis=1)).sort_values("son")
fig, ax = plt.subplots(figsize=(9.2, 6.0))
fig.subplots_adjust(left=0.27, right=0.95, top=0.84, bottom=0.1)
yy = np.arange(len(bt))
ax.hlines(yy, bt[yil_k].min(axis=1), bt[yil_k].max(axis=1), color=IZGARA, lw=4)
renk = [TURUNCU if s < 90 else SARI if s < 100 else AQUA for s in bt.son]
ax.scatter(bt.son, yy, color=renk, s=46, zorder=3)
for y_, r in zip(yy, bt.itertuples()):
    ax.text(max(r.son, r.ust) + 4, y_,
            f"%{tr(r.son, 0)} ({r.son_yil})", va="center", fontsize=7.4, color=YAZI_2)
ax.axvline(100, color=YAZI_3, lw=0.9, ls=":")
ax.text(101, len(bt) - 0.4, "%100 = üretim tüketime eşit", fontsize=7.2, color=YAZI_3)
ax.set_yticks(yy, bt.index, fontsize=8.2)
ax.set_xlim(0, 200)
ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v_, _: f"%{tr(v_, 0)}"))
sade(ax, False)
ax.grid(axis="x", color=IZGARA, lw=0.7)
baslik(fig, "Tahılda dalgalı, yağlı tohum ve baklagilde sürekli açık",
       "Bitkisel ürünlerde yeterlilik derecesi (üretim / yurt içi kullanım). Nokta: son yıl; gri çubuk: 2015/16–2024/25 aralığı. "
       "Fındık (%574) ölçek dışı bırakıldı. Kırmızı: %90 altı; sarı: %90–100; yeşil: %100 ve üstü.",
       "Kaynak: TÜİK Bitkisel Ürün Denge Tabloları (bülten arşivi); 2024/25 basın aktarımı [İ]. Soya ve ayçiçeği: yağ sanayii "
       "ithal tohuma bağımlı.")
kaydet(fig, "ekonomi_yeterlilik")

# =========================================================================== 9. Dağılım hesabı
t = pd.read_csv(SON / "ekonomi_dagilim_temel.csv")
s = pd.read_csv(SON / "ekonomi_dagilim_senaryolar.csv")
oz = pd.read_csv(SON / "ekonomi_dagilim_ozet.csv")
genel = oz.senaryo.str.extract(r"genel KDV %([\d,]+)").dropna().iloc[0, 0]
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13.2, 5.2), gridspec_kw={"width_ratios": [1, 1.15, 1]})
fig.subplots_adjust(left=0.05, right=0.99, top=0.73, bottom=0.27, wspace=0.3)
x = np.arange(5)
DIL = ["en yoksul\n%20", "2.", "3.", "4.", "en zengin\n%20"]
a1.bar(x - 0.19, t.dolayli_tuketime_pct, width=0.36, color=GRI, label="tüketime oranı")
a1.bar(x + 0.19, t.dolayli_gelire_pct, width=0.36, color=TURUNCU, label="gelire oranı")
for k in range(5):
    a1.text(k - 0.19, t.dolayli_tuketime_pct[k] + 0.3, tr(t.dolayli_tuketime_pct[k], 1), ha="center", fontsize=7.3, color=YAZI_2)
    a1.text(k + 0.19, t.dolayli_gelire_pct[k] + 0.3, tr(t.dolayli_gelire_pct[k], 1), ha="center", fontsize=7.3, color=TURUNCU)
a1.set_xticks(x, DIL)
a1.set_ylim(0, 18)
a1.yaxis.set_major_formatter(mt.FuncFormatter(lambda v_, _: f"%{tr(v_, 0)}"))
a1.legend(frameon=False, fontsize=7.8, loc="upper right")
a1.set_title("A · KDV + ÖTV yükü, 2025", loc="left", fontweight="bold")
sade(a1)


def cubuk(ax, seriler, ylim):
    w = 0.8 / len(seriler)
    for k, (c, ad, renk) in enumerate(seriler):
        ax.bar(x + (k - (len(seriler) - 1) / 2) * w, s[c], width=w, color=renk, label=ad)
    ax.axhline(0, color=YAZI_3, lw=0.8)
    ax.set_xticks(x, DIL)
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v_, _: tr(v_, 1)))
    ax.set_ylim(*ylim)
    sade(ax)


cubuk(a2, [("S1_genel_kdv_20den18e_gelire_pct", "Genel KDV %20 → %18 (145 mlr TL)", MAVI),
           ("S2_gida_kdv_1den0a_gelire_pct", "Gıdada KDV %1 → %0 (52 mlr TL)", AQUA),
           ("S3A_avd_konut_arsasi_net_gelire_pct", f"Arsa vergisi + KDV %{genel}: yalnız konut arsası (A)", SARI),
           ("S3C_avd_muafiyetli_net_gelire_pct", f"Arsa vergisi + KDV %{genel}: işletme arsası dahil, alt iki dilim muaf (C)",
            TURUNCU)], (-1.2, 0.6))
a2.set_ylabel("yük değişimi, gelirin %'si (eksi = kazanç)")
a2.legend(frameon=False, fontsize=6.9, loc="upper left", bbox_to_anchor=(-0.05, -0.16), ncol=1)
a2.set_title("B · Değişikliklerin dilimlere etkisi", loc="left", fontweight="bold")
cubuk(a3, [("S2_gida_kdv_1den0a_gelire_pct", "Gıdada KDV'yi sıfırlamak", AQUA),
           ("S4_ayni_butce_esit_transfer_gelire_pct", "Herkese eşit kişi başı ödeme", MAVI),
           ("S5_ayni_butce_alt20_transfer_gelire_pct", "Yalnız en yoksul %20'ye ödeme", TURUNCU)], (-2.6, 0.3))
a3.text(0.4, s.S5_ayni_butce_alt20_transfer_gelire_pct[0], tr(s.S5_ayni_butce_alt20_transfer_gelire_pct[0], 2), fontsize=7.3,
        color=TURUNCU, va="center")
a3.legend(frameon=False, fontsize=6.9, loc="upper left", bbox_to_anchor=(-0.05, -0.16), ncol=1)
a3.set_title("C · Aynı bütçe (52 mlr TL), üç yol", loc="left", fontweight="bold")
baslik(fig, "KDV ve ÖTV, gelire oranla en yoksula iki kat ağır; arsa vergisinin etkisi tasarıma bağlı",
       f"Statik hesap, davranış tepkisi yok. Arsa değer vergisi (GSYH'nin %0,5'i) genel KDV oranını %20'den %{genel} düzeyine "
       "indirmeye yetiyor. Gıda KDV'sinden vazgeçilen gelir doğrudan en yoksul %20'ye verilseydi etkisi ≈6 kat olurdu.",
       "Kaynak: 05_ANALIZ/kod/ekonomi_dagilim.py — Eurostat HBS 2020 (TÜİK HBA) harcama yapısı, Eurostat ilc_di01 2025 gelir payları, "
       "TÜİK sektör hesapları 2025, Muhasebat 2025 KDV/ÖTV tahsilatı. Varsayımlar: ekonomi_dagilim_varsayimlar.csv.")
kaydet(fig, "ekonomi_dagilim")

# =========================================================================== 10. Bir mahallenin vergi ve transfer akışı
pa = pd.read_csv(SON / "ekonomi_kademe_parametre.csv").set_index("parametre")
kal = [("kdv_otv_hanehalki_yuku_mn_tl", "Hanehalkının ödediği KDV + ÖTV (tahmin)", TURUNCU),
       ("sosyal_yardimlar_D62_mn_tl", "Hanehalkına giden sosyal yardımlar (çoğu emekli aylığı)", AQUA),
       ("temel_gelir_yarim_aclik_mn_tl", "Temel gelir: kişi başı açlık sınırının yarısı (seçenek)", GRI),
       ("arsa_deger_vergisi_gsyh05_mn_tl", "Arsa değer vergisi, GSYH'nin %0,5'i (seçenek)", MAVI),
       ("emlak_vergisi_mevcut_mn_tl", "Bugünkü emlak vergisi (bina + arsa + arazi)", SARI),
       ("harcamalara_katilma_payi_mevcut_mn_tl", "Bugünkü harcamalara katılma payları", SARI),
       ("arsa_vergisi_mevcut_mn_tl", "Bugünkü arsa vergisi", SARI)]
fig, ax = plt.subplots(figsize=(9.6, 4.6))
fig.subplots_adjust(left=0.43, right=0.93, top=0.76, bottom=0.14)
yy = np.arange(len(kal))[::-1]
deg = [pa.loc[k, "mahalle"] for k, *_ in kal]
ax.barh(yy, deg, color=[r for *_, r in kal], height=0.62)
for y_, v_ in zip(yy, deg):
    ax.text(v_ + 5, y_, f"{tr(v_, 1)} mn TL", va="center", fontsize=8, color=YAZI)
ax.set_yticks(yy, [a for _, a, _ in kal], fontsize=8.2)
ax.set_xlim(0, 480)
ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v_, _: tr(v_, 0)))
ax.set_xlabel("milyon TL / yıl (2025 fiyatları)")
sade(ax, False)
ax.grid(axis="x", color=IZGARA, lw=0.7)
oran_bugun = pa.loc["kdv_otv_hanehalki_yuku_mn_tl", "mahalle"] / pa.loc["emlak_vergisi_mevcut_mn_tl", "mahalle"]
oran_avd = pa.loc["kdv_otv_hanehalki_yuku_mn_tl", "mahalle"] / (pa.loc["emlak_vergisi_mevcut_mn_tl", "mahalle"]
                                                                 + pa.loc["arsa_deger_vergisi_gsyh05_mn_tl", "mahalle"])
baslik(fig, f"Bir mahalle (≈7 bin kişi) yılda emlak vergisinin {tr(oran_bugun, 0)} katı tüketim vergisi ödüyor",
       f"Ulusal toplamların kişi başı değeri × model mahalle nüfusu (6.925). Arsa değer vergisi eklenirse oran ≈{tr(oran_avd, 0)} kata "
       "iner; bu gelir belediyede kalır.",
       "Kaynak: 05_ANALIZ/sonuclar/ekonomi_kademe_parametre.csv — TÜİK sektör hesapları 2025, Muhasebat mahalli idareler 2025, "
       "ekonomi_dagilim.py, Dünya Bankası GSYH 2025, ADNKS 2025.")
kaydet(fig, "ekonomi_mahalle_akis")

# =========================================================================== 11. Vergi harcamaları
vh = pd.read_csv(SON / "ekonomi_vergi_harcamalari.csv")
vt = pd.read_csv(SON / "ekonomi_vergi_harcamasi_tahsilat.csv").set_index("vergi")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 4.9), gridspec_kw={"width_ratios": [1.7, 1]})
fig.subplots_adjust(left=0.37, right=0.98, top=0.76, bottom=0.12, wspace=0.42)
vh = vh.sort_values("milyar_tl_2025").reset_index(drop=True)
renk = [MAVI if "Asgari" in k else SARI if "kira" in k.lower() else TURUNCU
        if any(w in k for w in ["Geçici", "temettü", "fonu", "menkul", "17/4-g", "külçe"]) else GRI for k in vh.kalem]
a1.barh(range(len(vh)), vh.milyar_tl_2025, color=renk, height=0.62)
for k, v_ in enumerate(vh.milyar_tl_2025):
    a1.text(v_ + 8, k, tr(v_, 1), va="center", fontsize=7.6, color=YAZI)
a1.set_yticks(range(len(vh)), [k if len(k) < 64 else k[:62] + "…" for k in vh.kalem], fontsize=7.6)
a1.set_xlim(0, 980)
a1.xaxis.set_major_formatter(mt.FuncFormatter(lambda v_, _: tr(v_, 0)))
a1.set_xlabel("milyar TL, 2025 tahmini")
a1.set_title("Seçili 11 kalem", loc="left", fontweight="bold")
sade(a1, False)
a1.grid(axis="x", color=IZGARA, lw=0.7)
vt = vt.drop(index="Toplam")
yy = np.arange(len(vt))[::-1]
a2.barh(yy, vt.harcama_tahsilat_orani_pct, color=MAVI, height=0.6)
for y_, v_ in zip(yy, vt.harcama_tahsilat_orani_pct):
    a2.text(v_ + 1, y_, f"%{tr(v_, 1)}", va="center", fontsize=7.8)
a2.set_yticks(yy, vt.index, fontsize=8)
a2.set_xlim(0, 75)
a2.xaxis.set_visible(False)
a2.set_title("Vazgeçilen / tahsil edilen", loc="left", fontweight="bold")
sade(a2, False)
baslik(fig, "Devlet 2025'te tahsil ettiği verginin %28,7'si kadarından istisna ve indirimle vazgeçti",
       "Toplam vergi harcaması 3.170 milyar TL (GSYH'nin %5,1'i). En büyük kalem asgari ücret istisnası (mavi); turuncu: sermaye "
       "ve finansal gelir istisnaları; sarı: kira.",
       "Kaynak: GİB, 2025 Yılı Vergi Harcamaları Raporu (Tablo 4–5 ve kalem tabloları; PDF'ten okundu).")
kaydet(fig, "ekonomi_vergi_harcamalari")
print("grafikler tamam.")
