"""
Doğal ve geri dönüştürülmüş malzemeler: grafikler (Faz 4 · Rapor 3)
===================================================================
Girdi : 07_TASARIM_CIZIM/malzeme/sonuc_*.csv (malzeme_modeli.py), karar_matrisi_*.csv (karar_matrisleri.py)
Çıktı : 07_TASARIM_CIZIM/malzeme/
        maliyet_karbon_dagilim.png|svg   duvar ve bina ölçeğinde maliyet–karbon dağılımı
        sistem_karsilastirma.png|svg     ev ve okulda maliyet, karbon (biyojenik depo ayrı) ve işçilik çubukları
        u_degeri_bolge.png|svg           yalın duvar U değerleri ve TS 825:2024 sınırları
        deprem_talebi.png|svg            deprem kütlesi ve eşdeğer taban kesme kuvveti
        kubbe_karsilastirma.png|svg      kubbe ve tonoz sistemleri; tek katlı kubbeli evin deprem yükü
        karar_matrisi.png|svg            malzeme × ölçüt puanları (1–5)
        karar_matrisi_bina_tipi.png|svg  bina tipi × sistem × deprem tasarım sınıfı
Çalıştırma: PYTHONIOENCODING=utf-8 python 07_TASARIM_CIZIM/malzeme/kod/grafikler.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import FuncFormatter, MultipleLocator

sys.stdout.reconfigure(encoding="utf-8")
KLASOR = Path(__file__).resolve().parents[1]
MAVI, TURUNCU, AQUA, SARI = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
YAZI, YAZI_2, YAZI_3, ZEMIN, IZGARA = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e8e7e3"
AILE_RENK = {"betonarme": MAVI, "toprak": TURUNCU, "biyojenik": AQUA, "tas": SARI, "kagir": MAVI, "yalitim": YAZI_3,
             "sıva": YAZI_3}
AILE_AD = {"betonarme": "Betonarme ve endüstriyel kâgir", "toprak": "Toprak", "biyojenik": "Ahşap ve saman",
           "tas": "Taş"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "axes.edgecolor": YAZI_3, "axes.labelcolor": YAZI_2, "xtick.color": YAZI_2, "ytick.color": YAZI_2,
                     "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none"})
KAYNAK = "Kaynak: TR TAMİRAT, 07_TASARIM_CIZIM/malzeme/kod/malzeme_modeli.py. Fiyatlar Şubat 2026, KDV hariç, %25 genel gider ve kâr dahil."
ETIKET_ZEMIN = dict(boxstyle="square,pad=0.08", fc=ZEMIN, ec="none")


def tr(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".").replace("-", "−")


def fmt(nd=0):
    return FuncFormatter(lambda v, _: tr(v, nd))


def kaydet(fig, ad):
    for uz in ("png", "svg"):
        fig.savefig(KLASOR / f"{ad}.{uz}", dpi=200, facecolor=ZEMIN)
    plt.close(fig)
    print("yazıldı:", ad)


def izgara(ax, eksen="both"):
    ax.grid(axis=eksen, color=IZGARA, lw=0.8, zorder=0)
    ax.set_axisbelow(True)


def aile_lejant(ax, aileler, loc="upper left", ek=None):
    h = [Line2D([], [], marker="o", ls="", ms=7, mfc=AILE_RENK[a], mec=ZEMIN, label=AILE_AD[a]) for a in aileler]
    if ek:
        h += ek
    ax.legend(handles=h, loc=loc, frameon=False, fontsize=8)


# ------------------------------------------------------------------ 1. maliyet–karbon
def maliyet_karbon():
    duv = pd.read_csv(KLASOR / "sonuc_duvar_sistemleri.csv")
    duv = duv[duv.ic_duvar == 0]
    oz = pd.read_csv(KLASOR / "sonuc_bina_senaryolari.csv")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 6.2), gridspec_kw=dict(wspace=0.22))
    # (a) duvar: etiket konumu (veri koordinatı) ve hizası; kalabalık noktalarda kılavuz çizgi
    kay = {"W01": (1400, 47, "left"), "W02": (2850, 29, "left"), "W03": (1150, 34, "left"), "W04": (4100, 91, "left"),
           "W05": (2900, 81, "left"), "W06": (3800, 46, "left"), "W07": (700, 9, "left"), "W08": (3900, 19, "left"),
           "W09": (3350, 9, "left"), "W10": (6300, 31, "left"), "W11": (3900, 70, "left"), "W12": (5150, 76, "left"),
           "W13": (3400, 24, "left")}
    for _, r in duv.iterrows():
        dolu = r.hedefi_karsilar == 1
        c = AILE_RENK[r.aile]
        a1.scatter(r.maliyet_TL_m2, r.karbon_kgCO2e_m2, s=90, zorder=3, facecolor=c if dolu else ZEMIN,
                   edgecolor=c if not dolu else ZEMIN, linewidth=2 if not dolu else 1.5)
        x, y, ha = kay.get(r.duvar_kod, (r.maliyet_TL_m2 + 120, r.karbon_kgCO2e_m2 + 3, "left"))
        a1.annotate(f"{r.kisa_ad} · U {tr(r.U_W_m2K, 2)}", (r.maliyet_TL_m2, r.karbon_kgCO2e_m2), xytext=(x, y),
                    textcoords="data", fontsize=7.3, color=YAZI_2, ha=ha, va="center",
                    arrowprops=dict(arrowstyle="-", color=YAZI_3, lw=0.6, shrinkA=0, shrinkB=5))
    izgara(a1)
    a1.set_xlim(500, 7600)
    a1.set_ylim(0, 100)
    a1.xaxis.set_major_formatter(fmt())
    a1.set_xlabel("Maliyet (TL / m² duvar)")
    a1.set_ylabel("Gömülü karbon, A1–A3 fosil (kgCO2e / m² duvar)")
    a1.set_title("a) Dış duvar m² başına", loc="left", fontsize=10.5, fontweight="bold", color=YAZI)
    # (b) bina: etiketler sağda bir sütunda, ince kılavuz çizgiyle
    yer = {("OKUL1000", "R0"): 190, ("EV120", "R0"): 176, ("EV120", "T1"): 238, ("EV120", "T0"): 222,
           ("EV120", "T2"): 160, ("EV120", "H1"): 146, ("OKUL1000", "H1"): 133, ("OKUL1000", "R1"): 120,
           ("EV120", "R1"): 106, ("EV120", "A1"): 64}
    for _, r in oz.iterrows():
        c = AILE_RENK[r.aile]
        mk = "o" if r.senaryo == "EV120" else "s"
        bos = r.sistem == "T0"
        a2.scatter(r.TL_m2_bina, r.kgCO2e_m2_degisen, s=110, marker=mk, zorder=3, facecolor=ZEMIN if bos else c,
                   edgecolor=c if bos else ZEMIN, linewidth=2 if bos else 1.5)
        ad = r.kisa_ad.split(" ", 1)
        etiket = f"{ad[0]} {('ev' if r.senaryo == 'EV120' else 'okul')}: {ad[1]} ({tr(r.TL_m2_bina)} TL · {tr(r.kgCO2e_m2_degisen)} kg)"
        if (r.senaryo, r.sistem) in yer:
            xy, ha = (23750, yer[(r.senaryo, r.sistem)]), "left"
        else:
            xy, ha = (30500, 92), "right"
        a2.annotate(etiket, (r.TL_m2_bina, r.kgCO2e_m2_degisen), xytext=xy, textcoords="data", fontsize=7.3,
                    color=YAZI_2, ha=ha, va="center",
                    arrowprops=dict(arrowstyle="-", color=YAZI_3, lw=0.6, shrinkA=0, shrinkB=5,
                                    relpos=(0.0, 0.5) if ha == "left" else (1.0, 1.0)))
    izgara(a2)
    a2.set_xlim(20500, 32000)
    a2.set_ylim(0, 260)
    a2.xaxis.set_major_formatter(fmt())
    a2.set_xlabel("Bina maliyeti (TL / m² kat alanı); referans = 2026 tebliği III.B 21.050 TL/m²")
    a2.set_ylabel("Gömülü karbon, değişen kalemler (kgCO2e / m² kat alanı)")
    a2.set_title("b) Bina m² başına: 120 m² ev ve 1.000 m² okul", loc="left", fontsize=10.5, fontweight="bold", color=YAZI)
    h = [Line2D([], [], marker="o", ls="", ms=7, mfc=AILE_RENK[a], mec=ZEMIN, label=AILE_AD[a])
         for a in ["betonarme", "toprak", "biyojenik", "tas"]]
    h += [Line2D([], [], marker="o", ls="", ms=7, mfc=ZEMIN, mec=YAZI_3, mew=2, label="Boş: yalıtımsız, U sınırı aşıyor"),
          Line2D([], [], marker="o", ls="", ms=7, mfc=YAZI_3, mec=ZEMIN, label="Daire: ev"),
          Line2D([], [], marker="s", ls="", ms=7, mfc=YAZI_3, mec=ZEMIN, label="Kare: okul")]
    fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.055, 0.905), ncol=7, frameon=False, fontsize=8.2)
    fig.suptitle("Maliyet ve gömülü karbon: yalıtımlı toprak duvar tuğla + EPS ile başa baş, ahşap ve saman en düşük",
                 x=0.06, ha="left", fontsize=12.5, fontweight="bold", color=YAZI)
    fig.text(0.06, 0.925, "Karbon A1–A3 fosil; ahşap ve samanın biyojenik karbon deposu dahil değil. Değişen kalemler: temel, taşıyıcı "
             "sistem, ara döşeme, dış ve iç duvar. Dolu işaret: U ≤ 0,40 (TS 825:2024, 3. bölge).",
             fontsize=8.3, color=YAZI_2)
    fig.text(0.06, 0.02, KAYNAK + " Karbon: ICE v3/v4.1, EPD ve derleme makaleleri (kaynaklar.md).", fontsize=7.3, color=YAZI_3)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.83, bottom=0.12)
    kaydet(fig, "maliyet_karbon_dagilim")


# ------------------------------------------------------------------ 2. sistem karşılaştırma
def sistem_karsilastirma():
    oz = pd.read_csv(KLASOR / "sonuc_bina_senaryolari.csv")
    oz = oz[oz.sistem != "T0"]
    fig, eks = plt.subplots(2, 3, figsize=(13.5, 7.6), gridspec_kw=dict(height_ratios=[6, 4], hspace=0.42, wspace=0.42))
    for i, (sen, baslik) in enumerate([("EV120", "120 m² iki katlı ev (Z+1)"), ("OKUL1000", "1.000 m² iki katlı okul (BKS 1)")]):
        d = oz[oz.senaryo == sen].iloc[::-1].reset_index(drop=True)
        y = np.arange(len(d))
        renk = [AILE_RENK[a] for a in d.aile]
        ref = d[d.sistem == "R0"].iloc[0]
        # maliyet
        ax = eks[i, 0]
        ax.barh(y, d.TL_m2_bina, color=renk, height=0.62, edgecolor=ZEMIN, linewidth=2, zorder=3)
        ax.axvline(ref.TL_m2_bina, color=YAZI_3, ls="--", lw=1, zorder=2)
        for yy, v, f in zip(y, d.TL_m2_bina, d.fark_yuzde_R0):
            ax.text(v + 250, yy, f"{tr(v)}" + ("" if f == 0 else f"  ({'+' if f > 0 else '−'}%{tr(abs(f), 1)})"),
                    va="center", fontsize=7.8, color=YAZI_2, zorder=5)
        ax.set_yticks(y, list(d.kisa_ad), fontsize=8)
        ax.set_xlim(0, d.TL_m2_bina.max() * 1.38)
        ax.xaxis.set_major_locator(MultipleLocator(10000))
        ax.xaxis.set_major_formatter(fmt())
        izgara(ax, "x")
        ax.set_xlabel("TL / m² kat alanı")
        ax.set_title(f"{baslik}\nMaliyet", loc="left", fontsize=9.5, fontweight="bold", color=YAZI)
        # karbon
        ax = eks[i, 1]
        ax.barh(y, d.kgCO2e_m2_degisen, color=renk, height=0.62, edgecolor=ZEMIN, linewidth=2, zorder=3)
        ax.barh(y, d.biyojenik_depo_kgCO2_m2, color=[c + "55" for c in renk], height=0.62, edgecolor=renk, linewidth=0.8,
                hatch="////", zorder=3)
        ax.axvline(0, color=YAZI_3, lw=0.8, zorder=4)
        ax.axvline(ref.kgCO2e_m2_degisen, color=YAZI_3, ls="--", lw=1, zorder=2)
        for yy, v, f in zip(y, d.kgCO2e_m2_degisen, d.karbon_fark_yuzde_R0):
            ax.text(v + 6, yy, f"{tr(v)}" + ("" if f == 0 else f"  ({'+' if f > 0 else '−'}%{tr(abs(f), 0)})"),
                    va="center", fontsize=7.8, color=YAZI_2, zorder=5, bbox=ETIKET_ZEMIN)
        for yy, b in zip(y, d.biyojenik_depo_kgCO2_m2):
            if b < 0:
                ax.text(b - 6, yy, tr(b), va="center", ha="right", fontsize=7.8, color=YAZI_2)
        ax.set_yticks(y, [""] * len(y))
        ax.set_xlim(-300, 330)
        ax.xaxis.set_major_formatter(fmt())
        izgara(ax, "x")
        ax.set_xlabel("kgCO2e / m² (değişen kalemler; taralı: biyojenik depo)")
        ax.set_title("Gömülü karbon (A1–A3 fosil)", loc="left", fontsize=9.5, fontweight="bold", color=YAZI)
        # işçilik
        ax = eks[i, 2]
        ax.barh(y, d.iscilik_sa_m2, color=renk, height=0.62, edgecolor=ZEMIN, linewidth=2, zorder=3)
        ax.axvline(ref.iscilik_sa_m2, color=YAZI_3, ls="--", lw=1, zorder=2)
        for yy, v, p in zip(y, d.iscilik_sa_m2, d.iscilik_payi_degisen):
            ax.text(v + 0.25, yy, f"{tr(v, 1)} sa  (işçilik payı %{tr(p * 100, 0)})", va="center", fontsize=7.8,
                    color=YAZI_2, zorder=5, bbox=ETIKET_ZEMIN)
        ax.set_yticks(y, [""] * len(y))
        ax.set_xlim(0, d.iscilik_sa_m2.max() * 1.9)
        ax.xaxis.set_major_locator(MultipleLocator(5 if d.iscilik_sa_m2.max() > 10 else 2))
        ax.xaxis.set_major_formatter(fmt())
        izgara(ax, "x")
        ax.set_xlabel("İşçilik saati / m² kat alanı (değişen kalemler)")
        ax.set_title("Şantiye işçiliği (yerel istihdam)", loc="left", fontsize=9.5, fontweight="bold", color=YAZI)
    h = [Patch(facecolor=AILE_RENK[a], label=AILE_AD[a]) for a in ["betonarme", "toprak", "biyojenik"]]
    h += [Patch(facecolor=YAZI_3 + "55", edgecolor=YAZI_3, hatch="////", label="Biyojenik karbon deposu (ayrı raporlanır)"),
          Line2D([], [], color=YAZI_3, ls="--", label="Referans R0")]
    fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.012, 0.935), ncol=5, frameon=False, fontsize=8.3)
    fig.suptitle("Karbonu en ucuza düşük karbonlu betonarme, en çok ahşap ve saman azaltıyor; en pahalısı evde toprak "
                 "taşıyıcı, okulda CLT",
                 x=0.012, ha="left", fontsize=12.5, fontweight="bold", color=YAZI)
    fig.text(0.012, 0.015, KAYNAK + " Okulda CLT ithal kabul edildi; işçilik payı fabrika işçiliğini içermez.",
             fontsize=7.3, color=YAZI_3)
    fig.subplots_adjust(left=0.17, right=0.985, top=0.84, bottom=0.11)
    kaydet(fig, "sistem_karsilastirma")


# ------------------------------------------------------------------ 3. U değerleri
def u_degeri():
    ub = pd.read_csv(KLASOR / "sonuc_u_bolge.csv")
    duv = pd.read_csv(KLASOR / "sonuc_duvar_sistemleri.csv").set_index("duvar_kod")
    sira = ["W11", "W05", "W06", "W01", "W07", "W02", "W03", "W10", "W08", "W09"]
    ad = {"W11": "Yerel taş 50 cm", "W05": "Sıkıştırılmış toprak 50 cm, %6 çimento", "W06": "Sıkıştırılmış toprak 50 cm, stabilizesiz",
          "W01": "Yatay delikli tuğla 19 cm", "W07": "Kerpiç 40 cm", "W02": "Bims blok 19 cm", "W03": "CEB 14 cm",
          "W10": "CLT 10 cm", "W08": "Hafif toprak-saman 45 cm", "W09": "Saman balya 46 cm"}
    ek_y = {"W05": "W04", "W06": "W06", "W01": "W01", "W02": "W02", "W03": "W03", "W10": "W10", "W11": "W12", "W07": "W13"}
    d = ub.set_index("duvar_kod").loc[sira].iloc[::-1]
    fig, ax = plt.subplots(figsize=(11.5, 6.4))
    y = np.arange(len(d))
    ax.barh(y, d.U_yalin, color=[AILE_RENK[a] for a in d.aile], height=0.62, edgecolor=ZEMIN, linewidth=2, zorder=3)
    for yy, (kod, r) in zip(y, d.iterrows()):
        metin = f"U {tr(r.U_yalin, 2)}"
        if kod in ek_y:
            w = duv.loc[ek_y[kod]]
            yal = "iç ahşap lifi" if kod == "W11" else ("EPS" if kod == "W01" else "taş yünü")
            metin += f"  →  3. bölge için +{tr(w.yalitim_cm, 0)} cm {yal}"
        else:
            metin += "  (yalıtımsız)"
        if r.U_yalin > 2.4:
            ax.text(r.U_yalin - 0.04, yy, metin, va="center", ha="right", fontsize=8, color="white", fontweight="bold")
        else:
            ax.text(max(r.U_yalin + 0.03, 0.5), yy, metin, va="center", fontsize=8, color=YAZI_2)
    ust = len(d) - 0.35
    for v, e, xt in [(0.25, "5–6. bölge 0,25", 0.03), (0.35, "4. bölge 0,35", 0.62), (0.40, "2–3. bölge 0,40", 1.02),
                     (0.45, "1. bölge 0,45", 1.45)]:
        ax.plot([v, v], [-0.6, ust], color=YAZI, lw=0.9, ls=(0, (3, 2)), zorder=4)
        ax.annotate(e, (v, ust), xytext=(xt, ust + 0.75), fontsize=7.8, color=YAZI, va="center",
                    ha="left", arrowprops=dict(arrowstyle="-", color=YAZI_3, lw=0.7, shrinkA=1, shrinkB=0,
                                               relpos=(0.0, 0.5) if xt > v else (1.0, 0.5)))
    ax.set_yticks(y, [ad[k] for k in d.index], fontsize=8.5)
    ax.set_xlim(0, 3.1)
    ax.set_ylim(-0.6, len(d) + 0.75)
    ax.xaxis.set_major_formatter(fmt(1))
    izgara(ax, "x")
    ax.set_xlabel("Isıl geçirgenlik U (W/m²K), sıvalar dahil, ek yalıtım yokken")
    aile_lejant(ax, ["betonarme", "toprak", "biyojenik", "tas"], loc="lower right")
    fig.suptitle("50 cm sıkıştırılmış toprak duvar tek başına TS 825:2024'ü hiçbir bölgede karşılamıyor",
                 x=0.02, ha="left", fontsize=12.5, fontweight="bold", color=YAZI)
    fig.text(0.02, 0.905, "U ≈1,5–1,6 W/m²K; sınır 0,25–0,45. Yalnız toprakla 2,2–4,5 m duvar gerekir. "
             "Yalıtımsız geçen yalnız saman balya (her bölge) ve 45 cm hafif toprak-saman (1.–3. bölge).", fontsize=8.5,
             color=YAZI_2)
    fig.text(0.02, 0.02, "Kaynak: TR TAMİRAT malzeme_modeli.py; U sınırları TS 825:2024 (01.04.2025'ten zorunlu; İZODER yazarları "
             "aktarımı, İ); λ değerleri malzeme_parametreleri.csv.", fontsize=7.3, color=YAZI_3)
    fig.subplots_adjust(left=0.24, right=0.98, top=0.86, bottom=0.12)
    kaydet(fig, "u_degeri_bolge")


# ------------------------------------------------------------------ 4. deprem talebi
def deprem():
    dp = pd.read_csv(KLASOR / "sonuc_deprem_talebi.csv")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.8), gridspec_kw=dict(width_ratios=[1, 1.25], wspace=0.3))
    k = dp[dp.S_DS == 1.0].drop_duplicates("sistem")
    k = k[k.sistem != "T1_donatisiz"].set_index("sistem").loc[["A1", "R0", "H1", "T2", "T1"]]
    aile = {"A1": "biyojenik", "R0": "betonarme", "H1": "toprak", "T2": "toprak", "T1": "toprak"}
    y = np.arange(len(k))
    a1.barh(y, k.W_kN_m2, color=[AILE_RENK[aile[s]] for s in k.index], height=0.62, edgecolor=ZEMIN, linewidth=2, zorder=3)
    for yy, (s, r) in zip(y, k.iterrows()):
        a1.text(r.W_kN_m2 + 0.3, yy, f"{tr(r.W_kN_m2, 1)} kN/m²  ({tr(r.W_kN_m2 / k.loc['R0', 'W_kN_m2'], 1)} × R0)",
                va="center", fontsize=8, color=YAZI_2)
    a1.set_yticks(y, list(k.kisa_ad), fontsize=8.3)
    a1.set_xlim(0, 28)
    izgara(a1, "x")
    a1.set_xlabel("Deprem hesabına giren ağırlık (kN / m² kat alanı)")
    a1.set_title("a) Deprem kütlesi: 120 m² iki katlı ev", loc="left", fontsize=10.5, fontweight="bold", color=YAZI)
    seri = [("R0", MAVI, "-", "R0 betonarme (R = 8)"), ("A1", AQUA, "-", "A1 ahşap + saman (R = 3)"),
            ("T1", TURUNCU, "-", "T1 donatılı toprak (R = 4 kabulü)"),
            ("T1_donatisiz", TURUNCU, (0, (4, 2)), "T1 donatısız kabul (R = 2,5)")]
    for s, c, ls, e in seri:
        d = dp[dp.sistem == s].sort_values("S_DS")
        a2.plot(d.S_DS, d.V_kN_m2, color=c, ls=ls, lw=2, marker="o", ms=6, mec=ZEMIN, zorder=3)
        son = d.iloc[-1]
        a2.text(son.S_DS + 0.03, son.V_kN_m2, e, va="center", fontsize=8, color=YAZI_2)
    ymax = dp.V_kN_m2.max() * 1.12
    for x in (0.33, 0.50, 0.75):
        a2.axvline(x, color=YAZI_3, lw=0.8, ls=":", zorder=1)
    for x, e in [(0.265, "DTS 4"), (0.415, "DTS 3"), (0.625, "DTS 2"), (1.0, "DTS 1 (konut, BKS 3)")]:
        a2.text(x, ymax * 0.965, e, fontsize=7.3, color=YAZI_2, ha="center")
    t1 = dp[(dp.sistem == "T1") & (dp.S_DS == 1.0)].iloc[0]
    t1d = dp[(dp.sistem == "T1_donatisiz") & (dp.S_DS == 1.0)].iloc[0]
    a2.annotate(f"S_DS = 1,0'da toprak duvarda ortalama\nkayma gerilmesi ≈ {tr(t1.ort_kayma_gerilmesi_MPa, 2)} MPa "
                f"(donatısız: {tr(t1d.ort_kayma_gerilmesi_MPa, 2)})",
                (1.0, t1.V_kN_m2), xytext=(1.03, ymax * 0.25), fontsize=7.8, color=YAZI_2,
                arrowprops=dict(arrowstyle="-", color=YAZI_3, lw=0.8))
    a2.set_xlim(0.22, 1.75)
    a2.set_ylim(0, ymax)
    a2.xaxis.set_major_formatter(fmt(2))
    a2.yaxis.set_major_formatter(fmt(0))
    izgara(a2)
    a2.set_xlabel("Kısa periyot tasarım spektral ivme katsayısı S_DS (parsele göre AFAD haritasından)")
    a2.set_ylabel("Eşdeğer taban kesme kuvveti (kN / m² kat alanı)")
    a2.set_title(f"b) Tasarım deprem yükü: toprak evde betonarmenin ≈{tr(t1.V_oran_R0, 1)} katı", loc="left",
                 fontsize=10.5, fontweight="bold", color=YAZI)
    fig.suptitle("Deprem açısından toprağın asıl sorunu ağırlık: kütle, deprem kuvveti demek",
                 x=0.02, ha="left", fontsize=12.5, fontweight="bold", color=YAZI)
    fig.text(0.02, 0.9, "TBDY 2018 eşdeğer deprem yükü yaklaşımıyla kaba karşılaştırma: V = W · S_ae(T) / R_a(T), I = 1,0, T_B = 0,5 s [V]. "
             "Toprak duvar TBDY'de tanımlı değil; R değerleri donatılı (E11) ve donatısız (E22) yığmadan ödünç alındı.",
             fontsize=8.3, color=YAZI_2)
    fig.text(0.02, 0.02, "Kaynak: TR TAMİRAT malzeme_modeli.py; TBDY 2018 Tablo 3.2 ve 4.1, Denk. 4.27 (RG 18.03.2018/30364). "
             "Zemin kat duvarlarının alt yarısı temele aktarılır. Proje hesabı değildir; büyüklük sırası gösterir.",
             fontsize=7.3, color=YAZI_3)
    fig.subplots_adjust(left=0.185, right=0.86, top=0.8, bottom=0.13)
    kaydet(fig, "deprem_talebi")


# ------------------------------------------------------------------ 5. kubbe
def kubbe():
    kb = pd.read_csv(KLASOR / "sonuc_kubbe.csv").set_index("kod")
    ke = pd.read_csv(KLASOR / "sonuc_kubbeli_ev.csv")
    ad = {"K1": "İnce kabuk betonarme\n(12 m, 10 cm)", "K2": "Kâgir tuğla kubbe\n(12 m, 30 cm)",
          "K3": "Superadobe toprak\nkubbe (5 m, 40 cm)", "K4": "Nubian kerpiç\ntonozu (3,25 m, 25 cm)"}
    renk = {"K1": MAVI, "K2": SARI, "K3": TURUNCU, "K4": TURUNCU}
    fig = plt.figure(figsize=(13.5, 8.2))
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1.05], hspace=0.45, wspace=0.55)
    sira = ["K1", "K2", "K3", "K4"]
    y = np.arange(len(sira))[::-1]
    paneller = [("kutle_t_m2", "Örtü ağırlığı (t / m² örtü)", 2, "a) Ağırlık = deprem kuvveti"),
                ("karbon_kgCO2e_m2", "kgCO2e / m² örtü (A1–A3)", 0, "b) Gömülü karbon"),
                ("karbon_kgCO2e_m2_yil", "kgCO2e / m² örtü · yıl", 2, "c) Ömre bölünmüş karbon"),
                ("maliyet_TL_m2", "TL / m² örtü", 0, "d) Maliyet")]
    for j, (kol, xl, nd, baslik) in enumerate(paneller):
        ax = fig.add_subplot(gs[0, j])
        v = kb.loc[sira, kol]
        ax.barh(y, v, color=[renk[k] for k in sira], height=0.62, edgecolor=ZEMIN, linewidth=2, zorder=3)
        for yy, k in zip(y, sira):
            ek = f"  ({tr(kb.loc[k, 'hizmet_omru_yil'])} yıl)" if kol == "karbon_kgCO2e_m2_yil" else ""
            ax.text(kb.loc[k, kol] + v.max() * 0.03, yy, tr(kb.loc[k, kol], nd) + ek, va="center", fontsize=7.8,
                    color=YAZI_2)
        ax.set_yticks(y, [ad[k] for k in sira] if j == 0 else [""] * 4, fontsize=7.8)
        ax.set_xlim(0, v.max() * (1.75 if kol == "karbon_kgCO2e_m2_yil" else 1.45))
        ax.xaxis.set_major_formatter(fmt(1 if v.max() < 3 else 0))
        ax.xaxis.set_major_locator(plt.MaxNLocator(3))
        izgara(ax, "x")
        ax.set_xlabel(xl, fontsize=8)
        ax.set_title(baslik, loc="left", fontsize=9.5, fontweight="bold", color=YAZI)
    if True:   # hafif çatı referansı (ağırlık paneli)
        ax0 = fig.axes[0]
        ax0.axvline(0.10, color=AQUA, lw=1.2, ls="--", zorder=4)
        ax0.text(0.13, -0.85, "hafif ahşap çatı ≈0,10", fontsize=7.3, color=YAZI_2, va="center")
        ax0.set_ylim(-1.2, 3.5)
    # (e) tek katlı kubbeli ev: deprem yükü
    ax = fig.add_subplot(gs[1, :])
    e = ke[ke.S_DS == 1.0].set_index("kod").loc[["KE4", "KE3", "KE2", "KE1"]]
    e5 = ke[ke.S_DS == 0.5].set_index("kod")
    rk = {"KE1": TURUNCU, "KE2": TURUNCU, "KE3": TURUNCU, "KE4": MAVI}
    yy = np.arange(len(e))
    ax.barh(yy + 0.19, e.V_kN_m2, color=[rk[k] for k in e.index], height=0.36, edgecolor=ZEMIN, linewidth=1.5, zorder=3)
    ax.barh(yy - 0.19, e5.loc[e.index, "V_kN_m2"], color=[rk[k] + "88" for k in e.index], height=0.36, edgecolor=ZEMIN,
            linewidth=1.5, zorder=3)
    for y0, (k, r) in zip(yy, e.iterrows()):
        tau = "" if np.isnan(r.ort_kayma_gerilmesi_MPa) else f" · duvarda kayma ≈{tr(r.ort_kayma_gerilmesi_MPa, 2)} MPa"
        oran = "" if k == "KE4" else f"  ({tr(r.V_oran_KE4, 1)} × betonarme)"
        ax.text(r.V_kN_m2 + 0.15, y0 + 0.19, f"S_DS 1,0: {tr(r.V_kN_m2, 1)} kN/m²{oran}{tau}", va="center", fontsize=7.8,
                color=YAZI_2)
        v5 = e5.loc[k, "V_kN_m2"]
        ax.text(v5 + 0.15, y0 - 0.19, f"S_DS 0,5: {tr(v5, 1)} kN/m²", va="center", fontsize=7.8, color=YAZI_2)
    kisa = {"KE1": "Toprak duvar + superadobe kubbe (5 m)", "KE2": "Toprak duvar + Nubian kerpiç tonozu",
            "KE3": "Donatılı toprak duvar + hafif ahşap çatı", "KE4": "Betonarme tek kat (referans)"}
    etik = {k: f"{kisa[k]}\n(ağırlık {tr(r.W_kN_m2, 1)} kN/m²; örtü payı %{tr(r.ortu_payi * 100)})" for k, r in e.iterrows()}
    ax.set_yticks(yy, [etik[k] for k in e.index], fontsize=7.8)
    ax.set_xlim(0, e.V_kN_m2.max() * 1.7)
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.xaxis.set_major_formatter(fmt(0))
    izgara(ax, "x")
    ax.set_xlabel("Eşdeğer taban kesme kuvveti (kN / m² kat alanı); koyu: S_DS = 1,0 (yüksek tehlike), açık: S_DS = 0,5")
    ax.set_title("e) 120 m² tek katlı ev: örtü seçeneğine göre tasarım deprem yükü", loc="left", fontsize=10,
                 fontweight="bold", color=YAZI)
    fig.suptitle("Toprak kubbe ucuz ve düşük karbonlu, ama tek katlı evde bile deprem yükünü betonarmenin "
                 f"≈{tr(e.loc['KE1', 'V_oran_KE4'], 0)} katına çıkarıyor", x=0.012, ha="left", fontsize=12, fontweight="bold",
                 color=YAZI)
    fig.text(0.012, 0.935, "Kubbe ve halka dahil, örtülen m² başına. Kalınlık, ömür ve fiyatlar varsayım [V]; açıklıklar farklı, "
             "karşılaştırma büyüklük sırası verir. Kubbeli evde donatısız toprak için E22, donatılı toprak için E11 katsayıları ödünç alındı.",
             fontsize=8, color=YAZI_2)
    fig.text(0.012, 0.012, KAYNAK + " Deprem: TBDY 2018 eşdeğer deprem yükü, I = 1,0, T_B = 0,5 s [V].", fontsize=7.3,
             color=YAZI_3)
    fig.subplots_adjust(left=0.2, right=0.985, top=0.86, bottom=0.08)
    kaydet(fig, "kubbe_karsilastirma")


# ------------------------------------------------------------------ 6. karar matrisi: malzeme × ölçüt
def karar_matrisi():
    km = pd.read_csv(KLASOR / "karar_matrisi_malzeme.csv")
    olc = [("maliyet", "Maliyet"), ("gomulu_karbon", "Gömülü\nkarbon"), ("isi_yalitimi", "Isı yalıtımı\n(yalın U)"),
           ("isil_kutle", "Isıl kütle\n(κ)"), ("saglik", "Sağlık"), ("yangin", "Yangın"), ("akustik", "Akustik"),
           ("dayaniklilik", "Dayanıklılık\nve bakım"), ("deprem_tasiyici", "Deprem:\ntaşıyıcı"),
           ("deprem_dolgu", "Deprem:\ndolgu"), ("mevzuat_tedarik", "Mevzuat ve\ntedarik")]
    V = km[[c for c, _ in olc]].to_numpy(dtype=float)
    n = len(km)
    fig, ax = plt.subplots(figsize=(13.6, 11.2))
    renk = ["#f2b79b", "#f8dccd", "#ecebe7", "#86b6ef", "#2a78d6"]
    cmap = ListedColormap(renk)
    cmap.set_bad(ZEMIN)
    norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5, 4.5, 5.5], cmap.N)
    ax.imshow(np.ma.masked_invalid(V), cmap=cmap, norm=norm, aspect="auto")
    for i in range(n):
        H = {s.strip() for s in str(km.hesaplanan_olcutler.iloc[i]).split(",")}
        for j, (c, _) in enumerate(olc):
            v = V[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center", fontsize=8.5, color=YAZI_3)
                continue
            ax.text(j, i, f"{int(v)}", ha="center", va="center", fontsize=9, color="white" if v >= 4.5 else YAZI,
                    fontweight="bold" if c == "deprem_tasiyici" else "normal")
            if c in H:
                ax.add_patch(Rectangle((j - 0.44, i - 0.40), 0.88, 0.80, fill=False, ec=YAZI_2, lw=0.9, zorder=4))
    ax.set_xticks(range(len(olc)), [a for _, a in olc], fontsize=8.5)
    ax.xaxis.tick_top()
    ax.set_yticks(range(n), list(km.malzeme), fontsize=8.2)
    for i, a in enumerate(km.aile):
        ax.add_patch(Rectangle((-0.5 - 0.18, i - 0.5), 0.12, 1, color=AILE_RENK.get(a, YAZI_3), clip_on=False))
    ax.set_xticks(np.arange(-0.5, len(olc)), minor=True)
    ax.set_yticks(np.arange(-0.5, n), minor=True)
    ax.grid(which="minor", color=ZEMIN, lw=2)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(length=0)
    ax.tick_params(axis="y", pad=20)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.axvline(7.5, color=YAZI, lw=1.2)
    ax.axvline(9.5, color=YAZI, lw=1.2)
    h = [Patch(facecolor=c, label=e) for c, e in zip(renk, ["1 zayıf", "2", "3 orta (referans düzeyi)", "4", "5 güçlü"])]
    h += [Patch(facecolor=ZEMIN, edgecolor=YAZI_3, label="— uygulanmaz"),
          Patch(facecolor="none", edgecolor=YAZI_2, label="Çerçeveli: modelden hesaplandı [H]; çerçevesiz: uzman puanı [V]")]
    fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.2, 0.028), ncol=7, frameon=False, fontsize=8.2)
    fig.suptitle("Karar matrisi: 25 malzeme ve sistem × 11 ölçüt. Toprağın güçlü yanı ısıl kütle, ses ve sağlık; zayıf yanı "
                 "deprem ve mevzuat", x=0.02, ha="left", fontsize=12, fontweight="bold", color=YAZI)
    fig.text(0.02, 0.948, "Maliyet ve karbon: TS 825'i (3. bölge) sağlayan duvarın tuğla + EPS duvarına oranı (kubbede 12 m ince "
             "kabuğa); 3 = referansın ±%15'i. Eşikler karar_esikleri.csv'de, gerekçeler karar_matrisi_malzeme.csv'de.\n"
             "Deprem sütunları Türkiye'nin yüksek tehlikeli bölgeleri ve TBDY 2018'e göre.", fontsize=8.3, color=YAZI_2,
             va="top")
    fig.text(0.02, 0.008, "Sol şerit: malzeme ailesi (mavi betonarme ve kâgir, turuncu toprak, yeşil ahşap ve saman, sarı taş, "
             "gri yalıtım ve sıva). Kaynak: TR TAMİRAT karar_matrisleri.py.", fontsize=7.3, color=YAZI_3)
    fig.subplots_adjust(left=0.3, right=0.99, top=0.855, bottom=0.07)
    kaydet(fig, "karar_matrisi")


# ------------------------------------------------------------------ 7. karar matrisi: bina tipi × sistem
def bina_sistem_matrisi():
    bm = pd.read_csv(KLASOR / "karar_matrisi_bina_sistem.csv")
    S = pd.read_csv(KLASOR / "karar_girdi_sistemler.csv").set_index("kod")
    sis = list(S.index)
    binalar = list(dict.fromkeys(bm.bina_kod))
    DR = {"onerilir": (AQUA, "white", "Önerilir"), "kosullu": ("#9fd8c2", YAZI, "Koşullu"),
          "pilot": (SARI, YAZI, "Pilot"), "onerilmez": ("#f6c3ab", YAZI, "Önerilmez"),
          "yasak": (TURUNCU, "white", "Yasak"), "yok": (ZEMIN, YAZI_3, "—")}
    satirlar = [(b, d) for b in binalar for d in ("1–2", "3–4")]
    fig, ax = plt.subplots(figsize=(16, 12.4))
    for i, (b, d) in enumerate(satirlar):
        for j, s in enumerate(sis):
            r = bm[(bm.bina_kod == b) & (bm.sistem_kod == s) & (bm.DTS == d)].iloc[0]
            fc, tc, ad = DR[r.sonuc]
            ax.add_patch(Rectangle((j + 0.03, i + 0.04), 0.94, 0.92, fc=fc, ec="none"))
            if r.sonuc == "yok":
                ax.text(j + 0.5, i + 0.5, "—", ha="center", va="center", color=YAZI_3, fontsize=9)
                continue
            ax.text(j + 0.07, i + 0.27, ad + (" *" if r.tavanla_duzeltildi else ""), ha="left", va="center", fontsize=8.2,
                    fontweight="bold", color=tc)
            nt = str(r["not"]).split(" | ") if isinstance(r["not"], str) else []
            ax.text(j + 0.07, i + 0.64, "\n".join(nt[:2]), ha="left", va="center", fontsize=6.6, color=tc,
                    linespacing=1.15)
    ax.set_xlim(0, len(sis))
    ax.set_ylim(len(satirlar), 0)
    ax.set_xticks(np.arange(len(sis)) + 0.5, [S.loc[s, "baslik"].replace("\\n", "\n") for s in sis], fontsize=8.4)
    ax.xaxis.tick_top()
    B = bm.drop_duplicates("bina_kod").set_index("bina_kod")
    etik = []
    for b, d in satirlar:
        r = B.loc[b]
        etik.append(f"{r.bina_tipi}, {r.kat}\nBKS {r.BKS}, I = {tr(r.I, 1)}  ·  DTS {d}" if d == "1–2" else f"DTS {d}")
    ax.set_yticks(np.arange(len(satirlar)) + 0.5, etik, fontsize=8)
    for i in range(0, len(satirlar), 2):
        ax.axhline(i, color=YAZI_3, lw=0.8)
    ax.axvline(6, color=YAZI, lw=1.2)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    h = [Patch(facecolor=DR[k][0], edgecolor=YAZI_3 if k == "yok" else "none", label=DR[k][2])
         for k in ["onerilir", "kosullu", "pilot", "onerilmez", "yasak", "yok"]]
    fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.2, 0.035), ncol=6, frameon=False, fontsize=8.5)
    fig.suptitle("Bina tipine göre sistem: toprak taşıyıcı yalnız düşük-orta tehlikede müstakil ev pilotu; kamu binasında "
                 "toprak yalnız iç kabuk", x=0.012, ha="left", fontsize=12.5, fontweight="bold", color=YAZI)
    fig.text(0.012, 0.947, "Sonuç = en düşüğü (uzman yargısı [V], TBDY 2018 tavanı). Tavan: md. 11.2.4 ve 4.3.4.1(a), Tablo 4.1 + 3.3 "
             "yükseklik sınırları, kapsam dışı sistemde (md. 1.1.9, 12.1.2) en çok pilot ya da koşullu. "
             "* Yargı TBDY tavanıyla düşürüldü.\nDTS 1–2: yüksek tehlike (konutta S_DS ≥ 0,50); DTS 3–4: düşük-orta tehlike "
             "(S_DS < 0,50). Kubbe sütunları örtü sistemidir. Yüzdeler bu çalışmanın senaryo hesabından (R0'a göre).",
             fontsize=8.2, color=YAZI_2, va="top")
    fig.text(0.012, 0.01, "Kaynak: TR TAMİRAT karar_matrisleri.py; karar_matrisi_bina_sistem.csv. TBDY 2018 (RG 18.03.2018/30364).",
             fontsize=7.3, color=YAZI_3)
    fig.subplots_adjust(left=0.2, right=0.99, top=0.87, bottom=0.07)
    kaydet(fig, "karar_matrisi_bina_tipi")


if __name__ == "__main__":
    maliyet_karbon()
    sistem_karsilastirma()
    u_degeri()
    deprem()
    kubbe()
    karar_matrisi()
    bina_sistem_matrisi()
