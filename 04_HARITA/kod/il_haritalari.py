"""
81 il haritaları ve "mekânın payı" grafikleri
=============================================
Girdi : 03_VERI/islenmis/il_paneli_2025.gpkg, 05_ANALIZ/sonuclar/*.csv
        (önce 05_ANALIZ/kod/il_paneli_analiz.py çalıştırılmalı)
Çıktı : 04_HARITA/il_haritalari_2025.png|svg
        05_ANALIZ/grafikler/mekanin_payi_shapley.png|svg
        05_ANALIZ/grafikler/il_ici_kent_kir_egitim_farki.png|svg
"""

import sys
from pathlib import Path

import geopandas as gpd
import mapclassify
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
SONUC = KOK / "05_ANALIZ" / "sonuclar"
GRAFIK = KOK / "05_ANALIZ" / "grafikler"
HARITA = KOK / "04_HARITA"

# Referans palet: sıralı mavi rampa; ıraksak mavi↔kırmızı, ortada nötr gri
SIRALI = ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"]
IRAKSAK = ["#b8312f", "#ea8f8d", "#f0efec", "#86b6ef", "#256abf"]
YAZI, YAZI_2, ZEMIN, SINIR = "#0b0b0b", "#52514e", "#fcfcfb", "#ffffff"
MAVI, TURUNCU, AQUA, SARI = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN,
                     "axes.facecolor": ZEMIN, "text.color": YAZI})

g = gpd.read_file(KOK / "03_VERI" / "islenmis" / "il_paneli_2025.gpkg").to_crs(LCC)
art = pd.read_csv(SONUC / "ana_model_artiklar.csv")
g = g.merge(art, on="il", how="left")


def tr(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def harita(ax, kolon, baslik, alt, nd=1, iraksak=False, kirilim=None):
    s = g[kolon]
    if iraksak:
        m = np.nanmax(np.abs(s))
        sinirlar = kirilim or [-m, -0.6 * m / 2 * 2 / 2, -0.15 * m, 0.15 * m, 0.6 * m / 2 * 2 / 2, m]
        sinirlar = [-m - 1e-9] + list(sinirlar[1:-1]) + [m + 1e-9]
        renkler = IRAKSAK
    else:
        q = mapclassify.Quantiles(s.dropna(), k=5)
        sinirlar = [s.min() - 1e-9] + list(q.bins)
        renkler = SIRALI
    cmap = ListedColormap(renkler)
    norm = BoundaryNorm(sinirlar, cmap.N)
    g.plot(ax=ax, color="#ffffff", edgecolor="#c9c7c1", hatch="////", linewidth=0.4)
    g[s.notna()].plot(ax=ax, column=kolon, cmap=cmap, norm=norm, edgecolor=SINIR, linewidth=0.4)
    ax.set_axis_off()
    ax.set_title(baslik, loc="left", fontsize=11, fontweight="bold", pad=14, color=YAZI)
    ax.text(0, 1.0, alt, transform=ax.transAxes, fontsize=8, color=YAZI_2, va="bottom")
    eti = []
    for i in range(len(renkler)):
        a, b = sinirlar[i], sinirlar[i + 1]
        a = s.min() if i == 0 and not iraksak else a
        b = s.max() if i == len(renkler) - 1 and not iraksak else b
        eti.append(Patch(facecolor=renkler[i], edgecolor="#bbb", lw=0.3, label=f"{tr(a, nd)} – {tr(b, nd)}"))
    if s.isna().any():
        eti.append(Patch(facecolor="#ffffff", edgecolor="#9a9893", hatch="////", lw=0.3, label="veri yok"))
    ax.legend(handles=eti, loc="lower left", bbox_to_anchor=(0.0, -0.12), ncol=3, frameon=False,
              fontsize=7, handlelength=1.2, columnspacing=0.8)


fig, axs = plt.subplots(3, 3, figsize=(17, 12.5), dpi=150)
fig.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.04, hspace=0.30, wspace=0.05)
fig.text(0.02, 0.965, "81 ilde mekân, aile ve kontrol değişkenleri", fontsize=19, fontweight="bold")
fig.text(0.02, 0.942, "Beşte birlik dilimler (quantile). Kaynak: TÜİK Doğum 2025, Bina ve Konut Nitelikleri 2021, ADNKS 2025, "
         "İl GSYH 2024, Ulusal Eğitim 2025, İstatistiklerle Aile 2025.", fontsize=9.5, color=YAZI_2)

harita(axs[0, 0], "tdh_2025", "Toplam doğurganlık hızı", "2025 · kadın başına çocuk", nd=2)
harita(axs[0, 1], "ort_kat_2021", "Oturulan binanın ortalama kat sayısı", "2021 · hanelerin yaşadığı bina", nd=1)
harita(axs[0, 2], "yogun_kent_pay", "Yoğun kentte yaşayan nüfus", "2025 · % (DEGURBA)", nd=0)
harita(axs[1, 0], "kadin_egitim_suresi_2025", "Kadınların ortalama eğitim süresi", "2025 · yıl", nd=1)
g["gsyh_bin"] = g.gsyh_kb_tl_2024 / 1000
harita(axs[1, 1], "gsyh_bin", "Kişi başı GSYH", "2024 · bin TL", nd=0)
harita(axs[1, 2], "ilk_evlenme_yasi_k_2025", "Kadınların ilk evlenme yaşı", "2025 · yıl", nd=1)
harita(axs[2, 0], "kir_yogun_farki", "İl içinde kır − yoğun kent doğurganlık farkı",
       "2025 · çocuk · mavi: kırda yüksek, kırmızı: yoğun kentte yüksek", nd=2, iraksak=True,
       kirilim=[None, -0.25, -0.05, 0.05, 0.25, None])
harita(axs[2, 1], "yasli_yakin", "Çocuğuyla aynı mahallede ya da daha yakın oturan yaşlı",
       "2025 · 65+ nüfusun %'si", nd=0)
harita(axs[2, 2], "artik_tdh", "Modelin açıklayamadığı doğurganlık (artık)",
       "standart sapma · mavi: beklenenden yüksek, kırmızı: düşük", nd=1, iraksak=True,
       kirilim=[None, -1.0, -0.3, 0.3, 1.0, None])

for uz in ("png", "svg"):
    fig.savefig(HARITA / f"il_haritalari_2025.{uz}", facecolor=ZEMIN)
plt.close(fig)

# --- Shapley payları ---------------------------------------------------------------
pay = pd.read_csv(SONUC / "shapley_yuzde_paylari.csv", index_col=0)
ana = pd.read_csv(SONUC / "ana_model_sonuclari.csv", index_col="sonuc")
ETIKET = {
    "tdh_2025": "Toplam doğurganlık hızı", "kaba_evlenme_2025": "Kaba evlenme hızı*",
    "kaba_bosanma_2025": "Kaba boşanma hızı", "ilk_evlenme_yasi_k_2025": "Kadın ilk evlenme yaşı",
    "ilk_dogum_yasi_2025": "İlk doğumda anne yaşı", "hane_buyukluk_2025": "Ortalama hane büyüklüğü",
    "tek_kisi_pay": "Tek kişilik hane payı", "genis_aile_pay": "Geniş aile hane payı",
    "yasli_yakin": "Yaşlının çocuğuna yakınlığı",
}
sira = ["tdh_2025", "ilk_evlenme_yasi_k_2025", "ilk_dogum_yasi_2025", "kaba_bosanma_2025", "hane_buyukluk_2025",
        "tek_kisi_pay", "genis_aile_pay", "yasli_yakin", "kaba_evlenme_2025"]
gruplar = ["Mekân", "Gelir", "Eğitim", "Bölge-kültür"]
renk = {"Mekân": MAVI, "Gelir": TURUNCU, "Eğitim": AQUA, "Bölge-kültür": SARI}

fig, ax = plt.subplots(figsize=(12, 6.4), dpi=150)
fig.subplots_adjust(left=0.22, right=0.86, top=0.82, bottom=0.12)
y = np.arange(len(sira))[::-1]
for i, k in enumerate(sira):
    sol = 0
    r2 = ana.loc[k, "R2"]
    for gr in gruplar:
        w = pay.loc[k, gr]
        ax.barh(y[i], w, left=sol, color=renk[gr], height=0.62, edgecolor=ZEMIN, linewidth=2, zorder=3)
        if w >= 8:
            ax.text(sol + w / 2, y[i], f"{w:.0f}", ha="center", va="center", fontsize=8.5,
                    color="white" if gr in ("Mekân", "Gelir") else YAZI, zorder=4)
        sol += w
    ax.text(101.5, y[i], f"R² {tr(r2, 2)}", va="center", fontsize=8.5, color=YAZI_2)
ax.set_yticks(y)
ax.set_yticklabels([ETIKET[k] for k in sira])
ax.set_xlim(0, 100)
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xticklabels(["%0", "%25", "%50", "%75", "%100"])
for s_ in ("top", "right", "left"):
    ax.spines[s_].set_visible(False)
ax.tick_params(length=0)
ax.legend(handles=[Patch(color=renk[gr], label=gr) for gr in gruplar], loc="lower left",
          bbox_to_anchor=(0, 1.0), ncol=4, frameon=False, fontsize=9)
fig.text(0.02, 0.95, "Mekânın payı: açıklanan farkın gruplara bölüşümü (Shapley R²)", fontsize=15, fontweight="bold")
fig.text(0.02, 0.885, "81 il · Mekân = oturulan binanın ortalama kat sayısı + yoğun kentte yaşayan nüfus payı · "
         "Gelir = ln(kişi başı GSYH)\nEğitim = kadınların ortalama eğitim süresi · Bölge-kültür = Doğu-Güneydoğu kuklası "
         "(Kuzeydoğu, Ortadoğu ve Güneydoğu Anadolu)", fontsize=8.5, color=YAZI_2, linespacing=1.5)
fig.text(0.02, 0.03, "*Kaba evlenme hızı olay yerine göre kaydedilir ve yaş yapısına duyarlıdır; mekân payı bu yüzden şişkin olabilir. "
         "Bu bir il düzeyi (ekolojik) analizdir; bireysel nedensellik göstermez.", fontsize=8, color=YAZI_2)
for uz in ("png", "svg"):
    fig.savefig(GRAFIK / f"mekanin_payi_shapley.{uz}", facecolor=ZEMIN)
plt.close(fig)

# --- İl içi farklar: kent-kır vs eğitim ----------------------------------------------
f = pd.read_csv(SONUC / "il_ici_farklar.csv")
fig, axs = plt.subplots(2, 1, figsize=(11, 6.4), dpi=150, sharex=True)
fig.subplots_adjust(left=0.08, right=0.97, top=0.84, bottom=0.11, hspace=0.45)
bins = np.arange(-1.0, 2.6, 0.1)
seriler = [(f.kir_yogun_farki.dropna(), MAVI, "Kır − yoğun kent", "aynı ilde kırda yaşayan kadınlar ile yoğun kentte yaşayanlar"),
           (f.ilkokul_yuksek_farki.dropna(), TURUNCU, "İlkokul − yükseköğretim mezunu anne",
            "aynı ilde ilkokul mezunu kadınlar ile yükseköğretim mezunları")]
for ax, (s, c, ad, alt) in zip(axs, seriler):
    ax.hist(s, bins=bins, color=c, edgecolor=ZEMIN, linewidth=1.5, zorder=3)
    med = s.median()
    ax.axvline(med, color=YAZI, lw=1.2, ls=(0, (4, 3)), zorder=4)
    ax.text(med + 0.04, ax.get_ylim()[1] * 0.85, f"medyan {tr(med, 2)}", color=YAZI, fontsize=8.5, zorder=5,
            bbox=dict(facecolor=ZEMIN, edgecolor="none", pad=1.5))
    ax.axvline(0, color="#8a8985", lw=1, zorder=2)
    ax.set_title(ad, loc="left", fontsize=10.5, fontweight="bold", pad=16)
    ax.text(0, 1.02, f"{alt} · {len(s)} il", transform=ax.transAxes, fontsize=8, color=YAZI_2, va="bottom")
    ax.set_ylabel("il sayısı", color=YAZI_2)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.grid(axis="y", color="#e4e2dd", lw=0.6, zorder=0)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
axs[1].set_xlabel("aynı il içindeki doğurganlık farkı (çocuk/kadın, 2025)", color=YAZI_2)
fig.text(0.02, 0.95, "Aynı il içinde: yerleşim farkı mı, eğitim farkı mı?", fontsize=15, fontweight="bold")
fig.text(0.02, 0.905, "Kır–yoğun kent farkı 6 ilde hesaplanamıyor (yoğun kent yok). "
         "Eğitim farkının medyanı, yerleşim farkının medyanının yaklaşık beş katı.", fontsize=9, color=YAZI_2)
for uz in ("png", "svg"):
    fig.savefig(GRAFIK / f"il_ici_kent_kir_egitim_farki.{uz}", facecolor=ZEMIN)
plt.close(fig)
print("haritalar ve grafikler yazıldı")
