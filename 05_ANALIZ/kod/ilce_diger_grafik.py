"""
İl içi mekân katsayıları — eğitim kontrolünden önce ve sonra (8 sonuç × 3 mekân ölçüsü)
Girdi : 05_ANALIZ/sonuclar/ilce_diger_modeller.csv (ilce_diger_sonuclar_analiz.py)
Çıktı : 05_ANALIZ/grafikler/ilce_mekan_katsayilari.png|svg
"""
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
t = pd.read_csv(KOK / "05_ANALIZ" / "sonuclar" / "ilce_diger_modeller.csv")
ETI = {"smr": "Standartlaştırılmış ölüm oranı", "tdh_ilce": "Doğurganlık (ilçe TDH)", "k2534_bekar_pay": "25–34 yaş kadın bekâr payı",
       "tek_kisi_pay": "Tek kişilik hane payı", "genis_aile_pay": "Geniş aile hane payı", "ort_hane": "Ortalama hane büyüklüğü",
       "bosanma_hiz": "Boşanma hızı", "evlenme_hiz": "Evlenme hızı*"}
SIRA = ["smr", "tdh_ilce", "k2534_bekar_pay", "tek_kisi_pay", "genis_aile_pay", "ort_hane", "bosanma_hiz", "evlenme_hiz"]
OLCU = [("yukseklik", "Yaşanan bina yüksekliği"), ("ln_yogunluk", "Yaşanan yoğunluk (ln)"), ("yesil300", "300 m içinde parka erişim")]
MAVI, GRI, YAZI_2, ZEMIN = "#2a78d6", "#a9a7a1", "#52514e", "#fcfcfb"


def ayir(s):
    m = re.match(r"([+-]?\d+\.\d+)(\**|†?)", str(s))
    return (float(m.group(1)), m.group(2)) if m else (np.nan, "")


fig, axs = plt.subplots(1, 3, figsize=(15, 6.2), dpi=150, sharey=True)
fig.subplots_adjust(left=0.19, right=0.98, top=0.80, bottom=0.12, wspace=0.08)
y = np.arange(len(SIRA))[::-1]
for ax, (k, ad) in zip(axs, OLCU):
    for i, s in enumerate(SIRA):
        r0 = t[(t.sonuc == s) & (t.model == "mekân")]
        r1 = t[(t.sonuc == s) & (t.model == "mekân + eğitim + göç")]
        b0, _ = ayir(r0[k].iloc[0]) if len(r0) else (np.nan, "")
        b1, y1 = ayir(r1[k].iloc[0]) if len(r1) else (np.nan, "")
        ax.plot([b0, b1], [y[i], y[i]], color="#d4d1ca", lw=2, zorder=1)
        ax.scatter(b0, y[i], s=46, facecolor=ZEMIN, edgecolor=GRI, linewidth=1.6, zorder=2)
        ax.scatter(b1, y[i], s=50, color=MAVI if y1 else "#9ec5f4", edgecolor=ZEMIN, linewidth=1, zorder=3)
        if y1:
            ax.text(b1, y[i] + 0.22, y1, ha="center", fontsize=8, color=YAZI_2)
    ax.axvline(0, color="#8a8985", lw=1)
    ax.set_title(ad, loc="left", fontsize=10.5, fontweight="bold")
    ax.set_xlim(-0.45, 0.45)
    ax.grid(axis="x", color="#e4e2dd", lw=0.6)
    for s_ in ("top", "right", "left"):
        ax.spines[s_].set_visible(False)
    ax.tick_params(length=0)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    ax.set_xlabel("standartlaştırılmış β (il içi)", color=YAZI_2)
axs[0].set_yticks(y)
axs[0].set_yticklabels([ETI[s] for s in SIRA])
fig.text(0.02, 0.94, "Aynı il içinde mekân ne kadar fark ediyor — kadın eğitimi hesaba katılınca?", fontsize=15, fontweight="bold")
fig.text(0.02, 0.89, "973 ilçe · il sabit etkisi · nüfus ağırlıklı · içi boş gri: yalnız mekân ölçüleri · mavi: + kadın eğitimi ve göç "
         "(koyu mavi ve yıldız: anlamlı; *** p<0,001 · ** p<0,01 · * p<0,05 · † p<0,10)", fontsize=8.5, color=YAZI_2)
fig.text(0.02, 0.03, "*Evlenmeler olay (tescil) yerine göre kaydedildiği için ilçe düzeyinde gürültülüdür. Ekolojik analiz; bireysel nedensellik göstermez.",
         fontsize=8, color=YAZI_2)
for uz in ("png", "svg"):
    fig.savefig(KOK / "05_ANALIZ" / "grafikler" / f"ilce_mekan_katsayilari.{uz}", facecolor=ZEMIN)
print("yazıldı")
