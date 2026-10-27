"""
Enerji (Faz 4 · Rapor 5) — grafikler
====================================
Girdi : 05_ANALIZ/sonuclar/enerji_*.csv (enerji_veri.py → enerji_mahalle.py → enerji_senaryo.py → enerji_kademe.py)
Çıktı : 05_ANALIZ/grafikler/enerji_*.png|svg
  enerji_turkiye_durum      üretim karması 2010–2025 ve 2024 nihai enerji (sektör × yakıt)
  enerji_lcoe               maliyet karşılaştırması; SMR ayrı grupta
  enerji_mahalle_denge      model mahalle: aylık denge, 10 pilot, batarya eğrisi
  enerji_mahalle_hafta      model mahalle: kış ve yaz haftası (saatlik)
  enerji_isitma             ısıtma seçenekleri: hane başı maliyet ve CO2
  enerji_sehir_tarama       şehir: yerinde karşılama ↔ maliyet taraması
  enerji_kademe             kademe tablosunun özeti
  enerji_ulke_2050          ülke 2050 senaryoları: karma, maliyet, CO2, PM2.5 ölümleri
  enerji_ulke_hafta         S2: kış ve yaz haftası sevk
  enerji_il_gunes           81 il çatı/arazi GES verimi (PVGIS)
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/enerji_grafikler.py
"""
from __future__ import annotations

import os
import sys
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enerji_ortak import (AQUA, GRAF, KOK, MAVI, SARI, SON, TURUNCU, YAZI, YAZI_2, ZEMIN, saat_ekseni, tr)  # noqa: E402

GRI_K, GRI_A, IZGARA = "#52514e", "#b9b8b3", "#ecebe7"
MAVI_R = ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "savefig.facecolor": ZEMIN, "svg.fonttype": "none", "axes.edgecolor": GRI_A, "axes.labelcolor": YAZI_2,
                     "xtick.color": YAZI_2, "ytick.color": YAZI_2, "text.color": YAZI, "axes.titlecolor": YAZI,
                     "legend.frameon": False, "text.parse_math": False})
GRAF.mkdir(parents=True, exist_ok=True)


def kaydet(fig, ad):
    yol = GRAF / ad
    for uz in ("png", "svg"):
        fig.savefig(yol.with_suffix(f".{uz}"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("yazıldı:", yol.with_suffix(".png").relative_to(KOK))


def sade(ax, eksen="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis=eksen, color=IZGARA, lw=0.6)
    ax.set_axisbelow(True)


def fmt(nd=0):
    return mt.FuncFormatter(lambda x, _: tr(x, nd))


def yuzde(nd=0):
    return mt.FuncFormatter(lambda x, _: "%" + tr(x * 100, nd))


def baslik(fig, ust, alt=None, y=1.02):
    fig.suptitle(ust, x=0.01, y=y, ha="left", va="bottom", fontsize=12, fontweight="bold", color=YAZI)
    if alt:
        fig.text(0.01, y - 0.06 / fig.get_figheight() * 4.6, alt, ha="left", va="bottom", fontsize=8.5, color=YAZI_2)


def kaynak(fig, metin, y=-0.02):
    fig.text(0.01, y, metin, ha="left", va="top", fontsize=7, color=YAZI_2)


# --------------------------------------------------------------------------------------
def turkiye_durum():
    u = pd.read_csv(SON / "enerji_turkiye_uretim.csv")
    u = u[u.yil >= 2010].copy()
    u["diger"] = u.toplam - u.komur - u.dogal_gaz - u.hidro - u.ruzgar - u.gunes
    kat = [("komur", "Kömür", GRI_K), ("dogal_gaz", "Doğal gaz", GRI_A), ("hidro", "Hidro", MAVI),
           ("ruzgar", "Rüzgâr", AQUA), ("gunes", "Güneş", SARI), ("diger", "Jeotermal, biyokütle", MAVI_R[1])]
    s = pd.read_csv(SON / "enerji_turkiye_nihai_sektor.csv").set_index("sektor")
    sek = ["Sanayi", "Ulaştırma", "Konut", "Ticaret ve hizmetler", "Tarım"]
    s = s.loc[sek]
    s["yenilenebilir_isi"] = s.biyokutle_atik_twh + s.jeotermal_twh + s.gunes_twh + s.isi_twh
    yk = [("petrol_twh", "Petrol ürünleri", "#8a8984"), ("dogal_gaz_twh", "Doğal gaz", GRI_A), ("komur_twh", "Kömür", GRI_K),
          ("elektrik_twh", "Elektrik", MAVI), ("yenilenebilir_isi", "Biyokütle, jeotermal, güneş ısısı", AQUA)]

    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.6), gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.5))
    ax = axs[0]
    alt = np.zeros(len(u))
    for c, ad, renk in kat:
        ax.bar(u.yil, u[c] / 1000, bottom=alt, color=renk, width=0.78, edgecolor=ZEMIN, lw=0.8, label=ad)
        alt += u[c].to_numpy() / 1000
    son = u.iloc[-1]
    y0 = 0
    for c, ad, renk in kat:
        h = son[c] / 1000
        ax.text(2025.6, y0 + h / 2, f"{ad} %{tr(son[c] / son.toplam * 100, 0)}", va="center", fontsize=7.5, color=YAZI_2)
        y0 += h
    ax.set_xlim(2009.4, 2025.5)
    ax.set_ylabel("TWh")
    ax.yaxis.set_major_formatter(fmt())
    ax.set_xticks(range(2010, 2026, 3))
    sade(ax)
    ax.set_title("a · Elektrik üretimi kaynak bazında, 2010–2025 (TWh; 2025 geçici)", loc="left", fontsize=9.5)

    ax = axs[1]
    sol = np.zeros(len(s))
    for c, ad, renk in yk:
        ax.barh(range(len(s)), s[c], left=sol, color=renk, height=0.62, edgecolor=ZEMIN, lw=0.8, label=ad)
        sol += s[c].to_numpy()
    for i, (ad, top) in enumerate(zip(sek, s.toplam_twh)):
        ax.text(top + 6, i, f"{tr(top, 0)} TWh · elektrik %{tr(s.elektrik_twh.iloc[i] / top * 100, 0)}", va="center",
                fontsize=7.5, color=YAZI_2)
    ax.set_yticks(range(len(s)), sek)
    ax.invert_yaxis()
    ax.set_xlim(0, 560)
    ax.xaxis.set_major_formatter(fmt())
    ax.set_xlabel("TWh (nihai enerji)")
    sade(ax, "x")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.16), fontsize=7.5, handlelength=1, ncol=3)
    ax.set_title("b · Nihai enerji tüketimi, sektör ve yakıt, 2024 (TWh)", loc="left", fontsize=9.5)
    baslik(fig, "Türkiye'nin enerjisi: elektriğin üçte biri kömürden; ısı ve ulaşım hâlâ gaz ve petrolle",
           "Elektrik nihai enerjinin yalnız %20'si; birincil enerjinin %67'si ithal (2024).")
    kaynak(fig, "Kaynak: TEİAŞ Türkiye Elektrik Üretim-İletim İstatistikleri Tablo 63 ve 74 (rüzgâr–jeotermal ayrımı 2024 öncesi Ember); "
                "ETKB 2024 Ulusal Enerji Denge Tablosu. [D] veri, [H] paylar.", y=-0.1)
    kaydet(fig, "enerji_turkiye_durum")


# --------------------------------------------------------------------------------------
def lcoe():
    m = pd.read_csv(SON / "enerji_lcoe_karsilastirma.csv")
    smr = pd.read_csv(SON / "enerji_smr_lcoe.csv")

    def renk(t):
        t = t.lower()
        if "smr" in t or "nükleer" in t or "akkuyu" in t or "nuscale" in t or "darlington" in t or "doe" in t or "iea" in t:
            return TURUNCU
        if "güneş" in t or "çatı" in t or "ges" in t:
            return SARI
        if "rüzgâr" in t or "res" in t:
            return AQUA
        if "hidro" in t or "jeotermal" in t or "biyokütle" in t:
            return MAVI
        return GRI_K
    gruplar = [
        ("Türkiye: sözleşme ve piyasa fiyatı", m[m.grup == "Türkiye sözleşme fiyatları"]),
        ("IRENA: Türkiye'de gerçekleşen LCOE", m[m.grup == "IRENA, Türkiye"]),
        ("IRENA 2025: küresel ağırlıklı ortalama", m[m.grup.str.startswith("IRENA 2025")]),
        ("Lazard 2026: ABD, sübvansiyonsuz aralık", m[m.grup.str.startswith("Lazard") & ~m.teknoloji.str.contains("SMR")]),
    ]
    satir = []
    for g, d in gruplar:
        satir.append(("başlık", g, None, None, None))
        for _, r in d.iterrows():
            ad = r.teknoloji
            satir.append(("veri", ad, r.alt, r.ust, renk(r.teknoloji)))
    satir.append(("başlık", "SMR: beyan edilen hedef ↔ gözlenen maliyet (aynı varsayımla LCOE: %7, 60 yıl, KF %90)", None, None, None))
    for _, r in smr[~smr.durum.str.startswith("Akkuyu")].iterrows():
        if "IEA" in r.durum:
            satir.append(("veri", r.durum, 60, 80, TURUNCU))
        else:
            satir.append(("veri", r.durum, r.lcoe_usd_mwh, r.lcoe_usd_mwh, TURUNCU))
    n = len(satir)
    fig, ax = plt.subplots(figsize=(11, 0.24 * n + 1.2))
    fig.subplots_adjust(left=0.37, right=0.97)
    for i, (tur, ad, a, b, c) in enumerate(satir):
        if tur == "başlık":
            ax.text(-0.01, i, ad, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=8.2,
                    fontweight="bold", color=YAZI)
            continue
        if a == b:
            ax.plot(a, i, "o", ms=6.5, color=c, mec=ZEMIN, mew=1.2, zorder=3)
            et = tr(a, 0)
        else:
            ax.plot([a, b], [i, i], color=c, lw=5.5, solid_capstyle="round", zorder=3)
            et = f"{tr(a, 0)}–{tr(b, 0)}"
        ax.text(max(a, b) + 4, i, et, va="center", fontsize=7.3, color=YAZI_2)
        ax.text(-0.01, i, ad, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=7.6, color=YAZI_2)
    ax.axvspan(30, 45, color=SARI, alpha=0.08, lw=0)
    ax.text(37.5, -0.9, "YEKA bandı", ha="center", fontsize=7, color=YAZI_2)
    ax.set_ylim(n - 0.4, -1.4)
    ax.set_yticks([])
    ax.set_xlim(0, 280)
    ax.xaxis.set_major_formatter(fmt())
    ax.set_xlabel("$/MWh (nominal; Lazard ve IRENA kendi yıllarının doları)")
    sade(ax, "x")
    ax.spines["left"].set_visible(False)
    leg = [Patch(color=SARI, label="Güneş"), Patch(color=AQUA, label="Rüzgâr"), Patch(color=MAVI, label="Hidro, jeotermal, biyokütle"),
           Patch(color=TURUNCU, label="Nükleer ve SMR"), Patch(color=GRI_K, label="Fosil ve piyasa fiyatı")]
    ax.legend(handles=leg, loc="upper right", fontsize=7.5, ncol=1)
    baslik(fig, "Elektrik maliyeti: Türkiye'de güneş ve rüzgâr 32–40 $/MWh; SMR'de gözlenen maliyet 145–215 $/MWh",
           "Nokta: tek değer; çubuk: aralık. SMR satırlarında DOE n'inci örnek ve IEA 2040 hedefi beyan ya da hedeftir, gözlenmiş değildir.", y=1.0)
    kaynak(fig, "Kaynak: Lazard LCOE+ v19 (13.07.2026) [D]; IRENA Renewable Power Generation Costs 2025 [D/İ]; YEKA 2025 sonuçları (basın) [İ]; "
                "EPDK PTF 2025 [D]; OPG Darlington 20,9 milyar CAD / 4 × 300 MWe [İ] → LCOE [H]; NuScale–UAMPS 89 $/MWh (2023, iptal) [İ]; "
                "IEA 2025 [İ]. Ayrıntı: enerji_lcoe_karsilastirma.csv, enerji_smr_lcoe.csv.", y=0.0)
    kaydet(fig, "enerji_lcoe")


# --------------------------------------------------------------------------------------
def mahalle_denge(ref="Kocasinan"):
    a = pd.read_csv(SON / "enerji_mahalle_aylik.csv")
    y = pd.read_csv(SON / "enerji_mahalle_yillik.csv")
    b = pd.read_csv(SON / "enerji_mahalle_batarya.csv")
    d = a[a.ilce == ref].sort_values("ay")
    gr = [("aletler", "Ev aletleri ve pişirme", MAVI), ("isi", "Isıtma ve sıcak su (ısı pompası)", TURUNCU),
          ("ev_sarj", "Elektrikli otomobil", AQUA), ("diger", "Konut dışı, otopark, sokak, soğutma", GRI_A)]
    d = d.assign(isi=d.isitma + d.sicak_su, diger=d.konut_disi + d.otopark + d.kamusal + d.sogutma)
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.6), gridspec_kw=dict(width_ratios=[1.25, 1, 1], wspace=0.34))
    ax = axs[0]
    alt = np.zeros(12)
    for c, ad, rk in gr:
        ax.bar(d.ay, d[c], bottom=alt, color=rk, width=0.72, edgecolor=ZEMIN, lw=0.8, label=ad)
        alt += d[c].to_numpy()
    ax.plot(d.ay, d.uretim, "-o", color=SARI, lw=2, ms=5, mec=ZEMIN, mew=1, label="Çatı GES üretimi", zorder=4)
    ax.plot(d.ay, d.oz, "--", color=YAZI_2, lw=1.2, label="Saatlik öz tüketim (bataryasız)", zorder=4)
    ax.set_xticks(range(1, 13), ["O", "Ş", "M", "N", "M", "H", "T", "A", "E", "E", "K", "A"])
    ax.set_ylabel("MWh / ay")
    ax.yaxis.set_major_formatter(fmt())
    sade(ax)
    ax.legend(fontsize=7, loc="upper left", ncol=1, handlelength=1.2)
    ax.set_ylim(0, alt.max() * 1.45)
    ax.set_title(f"a · {ref} iklimi: aylık talep ve çatı GES (MWh)", loc="left", fontsize=9.5)

    ax = axs[1]
    y = y.sort_values("oz_yeterlilik_mahalle")
    bo = b[b.onerilen].set_index("ilce")
    for i, (_, r) in enumerate(y.iterrows()):
        x0, x1, x2 = r.oz_yeterlilik_mahalle, bo.loc[r.ilce, "oz_yeterlilik"], r.oz_yeterlilik_aylik_mahsup
        ax.plot([x0, x2], [i, i], color=IZGARA, lw=3, zorder=1)
        ax.plot(x0, i, "o", color=GRI_K, ms=6, zorder=3)
        ax.plot(x1, i, "o", color=MAVI, ms=6, zorder=3)
        ax.plot(x2, i, "D", color=SARI, ms=5.5, zorder=3)
        ax.text(1.0, i, f"{tr(r.uretim_talep_orani, 2)}", va="center", ha="right", fontsize=7.3, color=YAZI_2,
                transform=ax.get_yaxis_transform())
    ax.text(1.0, len(y) - 0.25, "yıllık\nGES/talep", ha="right", va="bottom", fontsize=6.8, color=YAZI_2,
            transform=ax.get_yaxis_transform())
    ax.set_ylim(-0.6, len(y) + 0.5)
    ax.set_yticks(range(len(y)), y.ilce)
    ax.set_xlim(0.3, 0.98)
    ax.xaxis.set_major_formatter(yuzde())
    sade(ax, "x")
    leg = [plt.Line2D([], [], marker="o", ls="", color=GRI_K, label="saatlik, bataryasız"),
           plt.Line2D([], [], marker="o", ls="", color=MAVI, label="saatlik, önerilen batarya"),
           plt.Line2D([], [], marker="D", ls="", color=SARI, label="aylık mahsup (fatura)")]
    ax.legend(handles=leg, fontsize=7, loc="upper center", bbox_to_anchor=(0.45, -0.09), ncol=3, handletextpad=0.2,
              columnspacing=0.8)
    ax.set_title("b · Yerinde karşılama, 10 pilot iklim", loc="left", fontsize=9.5)

    ax = axs[2]
    vurgu = {"Kocasinan": TURUNCU, "Fatih": MAVI, "Antakya": SARI}
    for ilce, g in b.groupby("ilce"):
        if ilce in vurgu:
            continue
        ax.plot(g.batarya_mwh, g.oz_yeterlilik, color=GRI_A, lw=1)
    for ilce, rk in vurgu.items():
        g = b[b.ilce == ilce]
        ax.plot(g.batarya_mwh, g.oz_yeterlilik, color=rk, lw=2, label=ilce)
        o = g[g.onerilen]
        ax.plot(o.batarya_mwh, o.oz_yeterlilik, "o", color=rk, ms=7, mec=ZEMIN, mew=1.2)
        ax.text(30.6, g.oz_yeterlilik.iloc[-1], ilce, va="center", fontsize=7.5, color=YAZI_2)
    ax.set_xlabel("Mahalle bataryası (MWh; güç = kapasite / 2 saat)")
    ax.yaxis.set_major_formatter(yuzde())
    ax.xaxis.set_major_formatter(fmt())
    ax.set_xlim(0, 37)
    sade(ax)
    ax.set_title("c · Batarya büyüdükçe kazanç azalır", loc="left", fontsize=9.5)
    ax.text(0.98, 0.04, "Nokta: önerilen boy (son 1 MWh yılda ≥ 250 MWh deşarj)", ha="right", fontsize=7, color=YAZI_2,
            transform=ax.transAxes)
    baslik(fig, "Model mahalle: çatılar yılda talebin %84–118'ini üretiyor ama saat saat ancak %39–51'ini karşılıyor",
           "Model mahalle v2.1 (2.164 konut, 6.925 kişi, 13,0 MWp çatı GES), ısı pompası ve elektrikli araçla tam elektrik. PVGIS 5.3 saatlik, 2019–2023.")
    kaynak(fig, "Kaynak: [H] enerji_mahalle.py; PVGIS 5.3 (JRC) SARAH3 saatlik seriler [D]; talep profilleri ve bina ısı katsayıları [V] (enerji_varsayimlar.csv).")
    kaydet(fig, "enerji_mahalle_denge")


def mahalle_hafta(ref="Kocasinan"):
    import enerji_mahalle as em
    from enerji_ortak import pilot_pv
    e = em.envanter()
    m = em.mahalle(ref, e, pv=pilot_pv(ref))
    ek = saat_ekseni()
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.0), sharey=True, gridspec_kw=dict(wspace=0.06))
    for ax, (ad, bas) in zip(axs, [("Kış haftası (17–23 Ocak 2022)", "2022-01-17"), ("Yaz haftası (18–24 Temmuz 2022)", "2022-07-18")]):
        i = (ek >= pd.Timestamp(bas)) & (ek < pd.Timestamp(bas) + pd.Timedelta(days=7))
        x = np.arange(i.sum())
        bil = m["bilesen"]
        katlar = [("Ev aletleri ve pişirme", bil["aletler"][i], MAVI),
                  ("Isıtma ve sıcak su", (bil["isitma"] + bil["sicak_su"])[i], TURUNCU),
                  ("Elektrikli otomobil", bil["ev_sarj"][i], AQUA),
                  ("Konut dışı, otopark, sokak, soğutma", (bil["konut_disi"] + bil["otopark"] + bil["kamusal"] + bil["sogutma"])[i], GRI_A)]
        ax.stackplot(x, *[k[1] / 1000 for k in katlar], colors=[k[2] for k in katlar], labels=[k[0] for k in katlar],
                     edgecolor=ZEMIN, lw=0.3)
        ax.plot(x, m["uretim"][i] / 1000, color=SARI, lw=1.8, label="Çatı GES")
        ax.plot(x, m["uretim"][i] / 1000, color=YAZI, lw=0.4)
        ax.set_xticks(range(0, 168, 24), ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"])
        ax.set_xlim(0, 167)
        ax.yaxis.set_major_formatter(fmt())
        sade(ax)
        ax.set_title(ad, loc="left", fontsize=9.5)
    axs[0].set_ylabel("MW (saatlik ortalama)")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=5)
    baslik(fig, f"Kışın açık akşamda, yazın fazla öğlende: model mahallenin iki haftası ({ref} iklimi)",
           "Kış akşam puantı ısı pompasından gelir ve bataryayla kapanmaz; yazın öğle fazlası günde birkaç saat için bataryaya alınabilir.")
    kaynak(fig, "Kaynak: [H] enerji_mahalle.py; PVGIS 5.3 saatlik ışınım ve sıcaklık (2022) [D].", y=-0.07)
    kaydet(fig, "enerji_mahalle_hafta")


# --------------------------------------------------------------------------------------
def isitma():
    d = pd.read_csv(SON / "enerji_mahalle_isitma.csv")
    ilceler = ["Kocasinan", "Beypazarı", "Fatih", "Antakya"]
    kisa = {"Doğal gaz kombi (yoğuşmalı)": "Doğal gaz kombi", "Hava kaynaklı ısı pompası (bireysel)": "Hava kaynaklı ısı pompası",
            "5. nesil toprak kaynaklı bölgesel şebeke": "5. nesil bölgesel şebeke", "Jeotermal bölgesel ısıtma (uygun sahada)": "Jeotermal bölgesel"}
    renk = {"Doğal gaz kombi": GRI_K, "Hava kaynaklı ısı pompası": TURUNCU, "5. nesil bölgesel şebeke": MAVI, "Jeotermal bölgesel": AQUA}
    d["kisa"] = d.secenek.map(kisa)
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.3), gridspec_kw=dict(wspace=0.25))
    w = 0.2
    for j, (s, rk) in enumerate(renk.items()):
        g = d[d.kisa == s].set_index("ilce").loc[ilceler]
        x = np.arange(len(ilceler)) + (j - 1.5) * w
        axs[0].bar(x, g.hane_basi_tl / 1000, width=w * 0.92, color=rk, label=s)
        if s in ("Hava kaynaklı ısı pompası", "5. nesil bölgesel şebeke"):
            axs[0].plot(x, g.hane_basi_tl_dusuk_kademe / 1000, "_", color=YAZI, ms=9, mew=1.6)
        hane = d[(d.kisa == s)].set_index("ilce").loc[ilceler]
        co2 = hane.co2_t_gesli / (2164)
        axs[1].bar(x, co2, width=w * 0.92, color=rk, label=s)
    axs[0].set_xticks(range(len(ilceler)), ilceler)
    axs[0].set_ylim(0, d.hane_basi_tl.max() / 1000 * 1.2)
    axs[0].set_ylabel("bin TL / hane · yıl (2025–26 tarifesiyle)")
    axs[0].yaxis.set_major_formatter(fmt(0))
    sade(axs[0])
    axs[0].legend(fontsize=7.3, loc="upper right")
    axs[0].set_title("a · Hane başı ısınma ve sıcak su faturası", loc="left", fontsize=9.5)
    axs[0].text(0.01, 0.97, "Kısa çizgi: elektrik düşük kademe tarifesiyle", transform=axs[0].transAxes, fontsize=7, color=YAZI_2, va="top")
    axs[1].set_xticks(range(len(ilceler)), ilceler)
    axs[1].set_ylabel("t CO2 / hane · yıl")
    axs[1].yaxis.set_major_formatter(fmt(1))
    sade(axs[1])
    axs[1].set_title("b · Mahallenin ısı CO2'si, hane başına (2023 şebeke faktörü; çatı GES saatleri düşüldü)", loc="left", fontsize=9.5)
    axs[1].text(0.99, 0.97, "Jeotermal: akışkandan çıkan CO2 sahaya göre\ndeğişir; hesaplanmadı [DY]", transform=axs[1].transAxes,
                ha="right", va="top", fontsize=7.2, color=YAZI_2)
    baslik(fig, "Isı pompası ısınmanın CO2'sini yarıdan fazla düşürüyor; bugünkü tarifelerle fatura çoğu iklimde ancak düşük kademede gazın altına iniyor",
           "Model mahalle ısı talebi (TS 825 üstü yalıtım, H = 1,0 W/m²K). Mahalle toplamı 2.164 hane.")
    kaynak(fig, "Kaynak: [H] enerji_mahalle.py; konut gazı 13,19 TL/Sm³ (EPDK 2025 II. yarıyıl) [D]; mesken elektrik 3,68 / 5,44 TL/kWh vergiler dahil [D/DY]; "
                "İzmir Jeotermal 2025–26 tarifesi [D]; şebeke faktörü 0,430 tCO2/MWh (ETKB 2023) [D].")
    kaydet(fig, "enerji_isitma")


# --------------------------------------------------------------------------------------
def sehir_tarama(ref="Kocasinan"):
    t = pd.read_csv(SON / "enerji_kent_tarama.csv")
    k = pd.read_csv(SON / "enerji_kent_senaryolar.csv")
    t = t[t.ilce == ref]
    k = k[(k.ilce == ref) & k.senaryo.str.match(r"K[123]b? ")]
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    nk = t[t.t_nukleer == 0]
    sm = t[t.t_nukleer > 0]
    ax.scatter(sm.yerel_karsilama, sm.maliyet_usd_mwh, s=10, color=TURUNCU, alpha=0.25, lw=0, label="SMR payı olan karmalar (Darlington maliyeti)")
    ax.scatter(nk.yerel_karsilama, nk.maliyet_usd_mwh, s=12, color=MAVI, alpha=0.45, lw=0, label="Nükleersiz karmalar")
    ax.axhline(85, color=GRI_K, lw=1, ls="--")
    ax.text(0.99, 0.03, "Kesikli çizgi: tamamen şebekeden alış (K1a) 85 $/MWh = ülke S2/S3 sistem maliyeti", fontsize=7.3,
            color=YAZI_2, ha="right", va="bottom", transform=ax.transAxes)
    for _, r in k.iterrows():
        kod = r.senaryo.split(" ")[0]
        ax.plot(r.yerel_karsilama, r.maliyet_usd_mwh, "o", ms=9, color=YAZI, mfc=ZEMIN, mew=1.6, zorder=5)
        ax.annotate(f"{kod}: %{tr(r.yerel_karsilama * 100, 0)} · {tr(r.maliyet_usd_mwh, 0)} $/MWh", (r.yerel_karsilama, r.maliyet_usd_mwh),
                    xytext={"K2": (-150, -16), "K3b": (8, -14)}.get(kod, (8, 6)), textcoords="offset points", fontsize=7.8,
                    color=YAZI)
    ax.xaxis.set_major_formatter(yuzde())
    ax.yaxis.set_major_formatter(fmt())
    ax.set_xlabel("Yerinde karşılama (saatlik; şehir sınırı içindeki üretim ve depolamadan)")
    ax.set_ylabel("Şehrin elektrik maliyeti, $/MWh talep")
    ax.set_ylim(60, min(t.maliyet_usd_mwh.max() * 1.02, 260))
    sade(ax, "both")
    ax.legend(fontsize=7.5, loc="upper left")
    baslik(fig, f"Şehir (≈208 bin kişi): yerinde karşılamayı %80'e çıkarmak ucuz; SMR payı her düzeyde pahalılaştırıyor",
           f"{ref} iklimi; {len(t)} karma (çatı + çevrede güneş, rüzgâr, batarya, SMR payı). K1 yalnız çatı, K2 en ucuz nükleersiz, K3 aynı karşılamaya SMR ile.", y=1.03)
    kaynak(fig, "Kaynak: [H] enerji_senaryo.py. Maliyet: yerel varlıkların yıllık bedeli (%7, 2040'lar teknoloji maliyeti; çatı 900 $/kWp) + şebekeden alış 85 $/MWh − satış 30 $/MWh [V]. "
                "K3b: aynı karma, SMR'nin iyimser n'inci örnek maliyetiyle (3.600 $/kW).")
    kaydet(fig, "enerji_sehir_tarama")


# --------------------------------------------------------------------------------------
def kademe(ref="Kocasinan"):
    d = pd.read_csv(SON / "enerji_kademe.csv")
    r = d[(d.iklim_ilce == ref) & d.sira.isin([1, 2, 3, 4])].sort_values("sira")
    u = d[d.sira == 5].iloc[0]
    etk = ["Mahalle\n6.925", "Semt\n34.624", "Şehir\n208 bin", "Bölge\n1,25 mn"]
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.4), gridspec_kw=dict(wspace=0.32))
    x = np.arange(4)
    ax = axs[0]
    ax.bar(x - 0.19, r.elektrik_kisi_basi_kwh, width=0.36, color=MAVI, label="Elektrik")
    ax.bar(x + 0.19, r.isi_kisi_basi_kwh, width=0.36, color=TURUNCU, label="Bina ısısı (ısıtma + sıcak su)")
    for i, (e, h) in enumerate(zip(r.elektrik_kisi_basi_kwh, r.isi_kisi_basi_kwh)):
        ax.text(i - 0.19, e + 60, tr(e, 0), ha="center", fontsize=7.2, color=YAZI_2)
        ax.text(i + 0.19, h + 60, tr(h, 0), ha="center", fontsize=7.2, color=YAZI_2)
    ax.axhline(u.elektrik_kisi_basi_kwh, color=GRI_K, lw=1, ls="--")
    ax.text(-0.45, u.elektrik_kisi_basi_kwh + 90, f"Ülke 2050 (S2): {tr(u.elektrik_kisi_basi_kwh, 0)} kWh/kişi", fontsize=7, color=YAZI_2)
    ax.set_xticks(x, etk)
    ax.yaxis.set_major_formatter(fmt())
    ax.set_ylabel("kWh / kişi · yıl")
    sade(ax)
    ax.legend(fontsize=7.3, loc="upper left", bbox_to_anchor=(0, 0.93))
    ax.set_title("a · Kişi başı talep", loc="left", fontsize=9.5)

    ax = axs[1]
    for i, (_, s) in enumerate(r.iterrows()):
        ax.plot([i, i], [s.yerinde_karsilama_depolamasiz, s.yerinde_karsilama], color=IZGARA, lw=4, zorder=1)
        ax.plot(i, s.yerinde_karsilama_depolamasiz, "o", color=GRI_K, ms=7, zorder=3)
        ax.plot(i, s.yerinde_karsilama, "o", color=MAVI, ms=8, zorder=3)
        ax.plot(i, s.yerinde_karsilama_kis, "v", color=TURUNCU, ms=7, zorder=3)
        ax.text(i + 0.12, s.yerinde_karsilama, f"%{tr(s.yerinde_karsilama * 100, 0)}", fontsize=7.5, va="center", color=YAZI)
    ax.set_xticks(x, etk)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(yuzde())
    sade(ax)
    leg = [plt.Line2D([], [], marker="o", ls="", color=GRI_K, label="depolamasız"),
           plt.Line2D([], [], marker="o", ls="", color=MAVI, label="depolamalı (yıl)"),
           plt.Line2D([], [], marker="v", ls="", color=TURUNCU, label="depolamalı, Aralık–Şubat")]
    ax.legend(handles=leg, fontsize=7.3, loc="upper left")
    ax.set_title("b · Yerinde karşılama (saatlik)", loc="left", fontsize=9.5)

    ax = axs[2]
    ax.bar(x, r.depolama_kwh_kisi, width=0.55, color=AQUA)
    for i, (_, s) in enumerate(r.iterrows()):
        ax.text(i, s.depolama_kwh_kisi + 0.15, f"{tr(s.depolama_kwh_kisi, 1)} kWh/kişi\n{tr(s.depolama_mwh, 0)} MWh",
                ha="center", fontsize=7.2, color=YAZI_2)
    ax.axhline(u.depolama_kwh_kisi, color=GRI_K, lw=1, ls="--")
    ax.text(-0.45, u.depolama_kwh_kisi + 0.15, f"Ülke 2050 (S2, batarya + pompaj): {tr(u.depolama_kwh_kisi, 1)} kWh/kişi", fontsize=7, color=YAZI_2)
    ax.set_xticks(x, etk)
    ax.set_ylim(0, max(r.depolama_kwh_kisi.max(), u.depolama_kwh_kisi) * 1.35)
    ax.yaxis.set_major_formatter(fmt(0))
    ax.set_ylabel("kWh / kişi")
    sade(ax)
    ax.set_title("c · Depolama ihtiyacı", loc="left", fontsize=9.5)
    baslik(fig, "Kademe büyüdükçe yerinde karşılama artıyor (mahallede %56, şehir ve bölgede %78); kişi başı depolama ihtiyacı azalıyor",
           f"{ref} iklimi. Mahalle ve semtte yalnız çatı GES; şehir ve bölgede çevrede güneş ve rüzgâr da var. Bölgede sanayi yükü eklenir.")
    kaynak(fig, "Kaynak: [H] enerji_kademe.py → enerji_kademe.csv. Batarya her kademede aynı kuralla: son 1 MWh yılda ≥ 250 MWh deşarj getirmeli [V]. "
                "Şehir ve bölgede üretim karması, maliyet taramasındaki en ucuz nükleersiz karma [H]. Ülke çizgisi bütün sektörleri içerir.")
    kaydet(fig, "enerji_kademe")


# --------------------------------------------------------------------------------------
def ulke_2050():
    u = pd.read_csv(SON / "enerji_ulke_2050.csv")
    g25 = pd.read_csv(SON / "enerji_turkiye_uretim.csv").set_index("yil").loc[2025]
    kat = [("komur", "Kömür", GRI_K), ("gaz", "Doğal gaz", GRI_A), ("nukleer", "Nükleer", TURUNCU),
           ("hidro", "Hidro", MAVI), ("diger", "Jeotermal, biyokütle", MAVI_R[1]), ("ruzgar", "Rüzgâr", AQUA),
           ("gunes", "Güneş", SARI), ("kisinti", "Kısılan güneş ve rüzgâr", "#ecebe7")]
    sat = [dict(ad="2025\ngözlenen", komur=g25.komur, gaz=g25.dogal_gaz + g25.sivi, nukleer=0, hidro=g25.hidro, ruzgar=g25.ruzgar,
                gunes=g25.gunes, diger=g25.jeotermal + g25.yenilenebilir_atik, kisinti=0)]
    for _, r in u.iterrows():
        ad = "2025\nmodel" if r.senaryo.startswith("2025") else r.senaryo.split(" ")[0] + "\n2050"
        k = r.uretim_kisinti_twh / (r.uretim_gunes_twh + r.uretim_ruzgar_twh)     # kısıntı güneş ve rüzgâra orantılı
        sat.append(dict(ad=ad, komur=r.uretim_komur_twh * 1000, gaz=r.uretim_gaz_twh * 1000, nukleer=r.uretim_nukleer_twh * 1000,
                        hidro=(r.uretim_hidro_baraj_twh + r.uretim_hidro_akarsu_twh) * 1000,
                        ruzgar=r.uretim_ruzgar_twh * 1000 * (1 - k), gunes=r.uretim_gunes_twh * 1000 * (1 - k),
                        diger=(r.uretim_jeotermal_twh + r.uretim_biyokutle_twh) * 1000, kisinti=r.uretim_kisinti_twh * 1000))
    d = pd.DataFrame(sat)
    fig = plt.figure(figsize=(14, 5.0))
    gs = fig.add_gridspec(2, 4, width_ratios=[2.0, 1, 1, 1], wspace=0.42, hspace=0.55)
    ax = fig.add_subplot(gs[:, 0])
    alt = np.zeros(len(d))
    for c, ad, rk in kat:
        ax.bar(range(len(d)), d[c] / 1000, bottom=alt, color=rk, width=0.66, edgecolor=ZEMIN if c != "kisinti" else GRI_A,
               lw=0.8 if c != "kisinti" else 0.5, hatch="////" if c == "kisinti" else None, label=ad)
        alt += d[c].to_numpy() / 1000
    for i, (_, r) in enumerate(u.iterrows()):
        ax.text(i + 1, alt[i + 1] + 8, f"talep {tr(r.talep_twh, 0)}", ha="center", fontsize=7, color=YAZI_2)
    ax.set_xticks(range(len(d)), d.ad, fontsize=8)
    ax.set_ylabel("TWh üretim (depolamadan çıkış ayrıca gösterilmez)")
    ax.yaxis.set_major_formatter(fmt())
    sade(ax)
    ax.legend(fontsize=7.2, loc="upper left", ncol=2)
    ax.set_ylim(0, alt.max() * 1.25)
    ax.set_title("a · Üretim karması", loc="left", fontsize=9.5)
    sen = u[~u.senaryo.str.startswith("2025")]
    lab = [s.split(" ")[0] for s in sen.senaryo]
    rk = [GRI_K, AQUA, TURUNCU]          # S1 kömürlü, S2 yenilenebilir, S3 nükleerli
    for k, (col, bas, nd, carp) in enumerate([("maliyet_usd_mwh", "b · Sistem maliyeti, $/MWh", 0, 1),
                                               ("co2_mt", "c · Elektrik CO2, Mt/yıl", 0, 1),
                                               ("pm25_olum", "d · Erken ölüm / yıl", 0, 1)]):
        ax = fig.add_subplot(gs[0 if k < 2 else 1, 1 + (k % 2) if k < 2 else 1])
        v = sen[col] * carp
        ax.bar(lab, v, color=rk, width=0.6)
        for i, x in enumerate(v):
            ax.text(i, x * 1.02, tr(x, nd), ha="center", va="bottom", fontsize=7.5, color=YAZI)
        ax.set_ylim(0, v.max() * 1.25)
        ax.yaxis.set_major_formatter(fmt())
        sade(ax)
        ax.set_title(bas, loc="left", fontsize=9)
    duy = pd.read_csv(SON / "enerji_ulke_2050_duyarlilik.csv")
    ax = fig.add_subplot(gs[1, 2:])
    durumlar = ["temel", "WACC %10", "karbon 75 $/t", "nükleer ucuz (büyük 4.500 $/kW, SMR 3.600 $/kW)",
                "nükleer pahalı (büyük 12.000 $/kW, SMR 18.800 $/kW)", "batarya 200 $/kWh", "kurak yıl (su 50 TWh)"]
    kis = ["temel", "WACC %10", "karbon 75 $/t", "nükleer ucuz", "nükleer pahalı", "batarya 200 $/kWh", "kurak yıl"]
    for j, (s, renk) in enumerate(zip(sen.senaryo, rk)):
        dd = duy[duy.senaryo == s].set_index("durum").reindex(durumlar)
        ax.plot(dd.maliyet_usd_mwh.to_numpy(), np.arange(len(durumlar)) + (j - 1) * 0.2, "o", color=renk, ms=5, label=lab[j])
    ax.set_yticks(range(len(durumlar)), kis, fontsize=7.3)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(fmt())
    ax.set_xlabel("$/MWh")
    sade(ax, "x")
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    ax.set_title("e · Maliyetin duyarlılığı", loc="left", fontsize=9)
    baslik(fig, "Türkiye 2050: kömürü bırakmak elektriğin CO2'sini altıda bire, santral kaynaklı ölümü %93 indiriyor; nükleer ancak iyimser maliyetle ucuzlatıyor",
           "Üç senaryoda da aynı talep (737 TWh: ısı pompası ve elektrikli araç dahil). S2 ve S3'te fosil payı ≤ %10 koşuluyla en ucuz karma seçildi.", y=1.04)
    kaynak(fig, "Kaynak: [H] enerji_senaryo.py, 5 hava yılı (2019–2023) saatlik sevk. Maliyet 2025 $, %7 WACC, karbon fiyatı yok (duyarlılıkta 75 $/t). "
                "Ölüm katsayısı: kömür 42,7/TWh (HEAL/CREA 2021 Türkiye ölümleri / TEİAŞ 2019 kömür üretimi [H]), diğerleri OWID [D].")
    kaydet(fig, "enerji_ulke_2050")


def ulke_hafta():
    h = pd.read_csv(SON / "enerji_ulke_2050_hafta.csv", parse_dates=["zaman"])
    s2 = [s for s in h.senaryo.unique() if s.startswith("S2")][0]
    kat = [("nukleer", "Nükleer", TURUNCU), ("diger", "Jeotermal, biyokütle", MAVI_R[1]), ("hidro", "Hidro", MAVI),
           ("ruzgar", "Rüzgâr", AQUA), ("gunes", "Güneş", SARI), ("depolama", "Depolamadan", MAVI_R[0]),
           ("gaz", "Doğal gaz", GRI_A)]
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.2), sharey=True, gridspec_kw=dict(wspace=0.06))
    for ax, hafta in zip(axs, ["kış", "yaz"]):
        d = h[(h.senaryo == s2) & (h.hafta == hafta)].copy()
        d["hidro"] = d.hidro_akarsu + d.hidro_baraj
        d["diger"] = d.jeotermal + d.biyokutle
        x = np.arange(len(d))
        ys = [d[c] / 1000 for c, _, _ in kat]
        ax.stackplot(x, *ys, colors=[k[2] for k in kat], labels=[k[1] for k in kat], edgecolor=ZEMIN, lw=0.2)
        ax.plot(x, d.talep / 1000, color=YAZI, lw=1.4, label="Talep")
        ax.set_xticks(range(0, 168, 24), ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"])
        ax.set_xlim(0, len(d) - 1)
        sade(ax)
        ax.set_title(("Kış haftası (17–23 Ocak 2022 havası)" if hafta == "kış" else "Yaz haftası (18–24 Temmuz 2022 havası)"),
                     loc="left", fontsize=9.5)
    axs[0].set_ylabel("GW")
    axs[0].yaxis.set_major_formatter(fmt())
    axs[1].legend(fontsize=7.2, loc="upper right", ncol=2)
    baslik(fig, "S2 (yüksek yenilenebilir, 2050): kış haftasında gaz yedeği devreye giriyor, yazın batarya geceyi taşıyor",
           "Talep çizgisinin üstünde kalan üretim depolamaya gider ya da kısılır.")
    kaynak(fig, "Kaynak: [H] enerji_senaryo.py; güneş ve rüzgâr profilleri PVGIS 5.3 (SARAH3, ERA5) [D] → [V] ölçekleme.")
    kaydet(fig, "enerji_ulke_hafta")


def il_gunes():
    import geopandas as gpd
    g = gpd.read_file(KOK / "03_VERI" / "islenmis" / "ilce_paneli.gpkg")[["il", "geometry"]]
    g = g.dissolve("il").reset_index()
    d = pd.read_csv(SON / "enerji_il_gunes.csv")
    g = g.merge(d[["il", "verim_opt_kwh_kwp"]], on="il", how="left")
    g = g.to_crs("+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m +no_defs")
    sinir = [0, 1300, 1400, 1500, 1600, 2000]
    from matplotlib.colors import BoundaryNorm, ListedColormap
    cm = ListedColormap(MAVI_R)
    fig, ax = plt.subplots(figsize=(11, 5.0))
    g.plot(column="verim_opt_kwh_kwp", cmap=cm, norm=BoundaryNorm(sinir, cm.N), ax=ax, edgecolor=ZEMIN, lw=0.4)
    ax.set_axis_off()
    for i, (a, b) in enumerate(zip(sinir[:-1], sinir[1:])):
        et = f"< {tr(b, 0)}" if a == 0 else (f"≥ {tr(a, 0)}" if b == 2000 else f"{tr(a, 0)}–{tr(b, 0)}")
        ax.add_patch(plt.Rectangle((0.02 + i * 0.085, 0.04), 0.08, 0.035, transform=ax.transAxes, color=MAVI_R[i]))
        ax.text(0.06 + i * 0.085, 0.0, et, transform=ax.transAxes, ha="center", fontsize=7, color=YAZI_2)
    ax.text(0.02, 0.1, "kWh/kWp · yıl (optimum eğim, kayıp %14)", transform=ax.transAxes, fontsize=7.5, color=YAZI_2)
    en = d.sort_values("verim_opt_kwh_kwp")
    ax.text(0.99, 0.02, f"En yüksek: {en.il.iloc[-1]} {tr(en.verim_opt_kwh_kwp.iloc[-1], 0)} · en düşük: {en.il.iloc[0]} "
            f"{tr(en.verim_opt_kwh_kwp.iloc[0], 0)} · nüfus ağırlıklı ortalama "
            f"{tr((d.verim_opt_kwh_kwp * d.il_nufus_2025).sum() / d.il_nufus_2025.sum(), 0)}",
            transform=ax.transAxes, ha="right", fontsize=7.5, color=YAZI_2)
    baslik(fig, "Güneşten 1 kWp panelin yıllık üretimi: güneyde ve iç bölgede 1.500–1.680 kWh, Karadeniz kıyısında 1.000–1.300 kWh",
           "Her ilin en kalabalık ilçesinin iç noktası. Almanya ortalaması ≈ 950–1.000 kWh/kWp.", y=0.98)
    kaynak(fig, "Kaynak: PVGIS 5.3 PVcalc (JRC), SARAH3 2005–2023, c-Si [D]; il sınırları proje ilçe paneli. Almanya karşılaştırması [İ]. Osmaniye'nin noktası Amanos eteğinde; ufuk gölgesiyle düşük [DY].", y=0.02)
    kaydet(fig, "enerji_il_gunes")


if __name__ == "__main__":
    turkiye_durum()
    lcoe()
    mahalle_denge()
    mahalle_hafta()
    isitma()
    il_gunes()
    if (SON / "enerji_kent_senaryolar.csv").exists():
        sehir_tarama()
        ulke_2050()
        ulke_hafta()
    if (SON / "enerji_kademe.csv").exists():
        kademe()
