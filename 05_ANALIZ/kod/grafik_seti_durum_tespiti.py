"""
Durum tespiti grafik seti
=========================
03_VERI/islenmis/turkiye_temel_gostergeler.csv dosyasından dokuz panelli bir
özet grafik üretir (aile, konut, beden, ruh ve toplum göstergeleri).

Çalıştırma:  python grafik_seti_durum_tespiti.py
Çıktılar  :  ../grafikler/durum_tespiti_grafik_seti.png|svg
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

KOK = Path(__file__).resolve().parents[2]
VERI = KOK / "03_VERI" / "islenmis" / "turkiye_temel_gostergeler.csv"
CIKTI = KOK / "05_ANALIZ" / "grafikler"
CIKTI.mkdir(parents=True, exist_ok=True)

# Referans paletin ilk iki kategorik dilimi (doğrulandı: validate_palette.js, açık mod)
MAVI = "#2a78d6"
TURUNCU = "#eb6834"
REF = "#8a8985"
YAZI = "#0b0b0b"
YAZI_2 = "#52514e"
IZGARA = "#e4e2dd"
ZEMIN = "#fcfcfb"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": IZGARA,
    "axes.labelcolor": YAZI_2,
    "axes.titlecolor": YAZI,
    "xtick.color": YAZI_2,
    "ytick.color": YAZI_2,
    "axes.facecolor": ZEMIN,
    "figure.facecolor": ZEMIN,
})

d = pd.read_csv(VERI)
d["yil_n"] = pd.to_numeric(d["yil"].astype(str).str[:4], errors="coerce")
d["deger_n"] = pd.to_numeric(d["deger"], errors="coerce")


def seri(baslangic, cografya="Türkiye"):
    s = d[d.gosterge.str.startswith(baslangic) & (d.cografya == cografya)]
    s = s.dropna(subset=["yil_n", "deger_n"]).sort_values("yil_n")
    return s.yil_n.tolist(), s.deger_n.tolist()


def tr(x, ondalik=1):
    return f"{x:.{ondalik}f}".replace(".", ",")


def eksen(ax, baslik, alt):
    ax.set_title(baslik, loc="left", fontsize=10.5, fontweight="bold", pad=18)
    ax.text(0, 1.02, alt, transform=ax.transAxes, fontsize=8, color=YAZI_2, va="bottom")
    ax.grid(axis="y", color=IZGARA, lw=0.6)
    ax.set_axisbelow(True)
    for k in ("top", "right", "left"):
        ax.spines[k].set_visible(False)
    ax.tick_params(length=0)


def cizgi(ax, x, y, renk=MAVI, son_etiket=True, ondalik=1, ilk_etiket=True):
    ax.plot(x, y, color=renk, lw=2, marker="o", ms=4.5, mec=ZEMIN, mew=1.2, zorder=3)
    if ilk_etiket:
        ax.annotate(tr(y[0], ondalik), (x[0], y[0]), textcoords="offset points", xytext=(0, 7),
                    ha="center", fontsize=8.5, color=YAZI)
    if son_etiket:
        ax.annotate(tr(y[-1], ondalik), (x[-1], y[-1]), textcoords="offset points", xytext=(0, 7),
                    ha="center", fontsize=8.5, color=YAZI, fontweight="bold")


def referans(ax, deger, etiket, x_konum):
    ax.axhline(deger, color=REF, lw=1, ls=(0, (4, 3)), zorder=2)
    ax.text(x_konum, deger, f" {etiket}", color=YAZI_2, fontsize=8, va="bottom")


fig, eksenler = plt.subplots(3, 3, figsize=(15, 13), dpi=150)
fig.subplots_adjust(left=0.05, right=0.98, top=0.865, bottom=0.07, hspace=0.55, wspace=0.34)
fig.text(0.05, 0.955, "Türkiye'nin tablosu: aile, konut, beden, toplum", fontsize=19, fontweight="bold", color=YAZI)
fig.text(0.05, 0.932, "Faz 1 durum tespiti — temel eğilimler. Kaynak: TÜİK, Eurostat, OECD (ayrıntı: 03_VERI/turkiye_temel_gostergeler.md)",
         fontsize=10, color=YAZI_2)

# 1. Doğurganlık
ax = eksenler[0, 0]
x, y = seri("Toplam doğurganlık hızı (TDH)")
ax.plot(x[:2], y[:2], color=MAVI, lw=1.2, ls=":", zorder=3)
ax.plot(x[1:], y[1:], color=MAVI, lw=2, marker="o", ms=4.5, mec=ZEMIN, mew=1.2, zorder=3)
ax.plot(x[0], y[0], color=MAVI, marker="o", ms=4.5, mec=ZEMIN, mew=1.2, zorder=3)
ax.annotate(tr(y[0], 2), (x[0], y[0]), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8.5)
ax.annotate(tr(y[-1], 2), (x[-1], y[-1]), textcoords="offset points", xytext=(-4, -14), ha="right", fontsize=8.5, fontweight="bold")
referans(ax, 2.10, "yenilenme düzeyi 2,10", 2001)
ax.set_ylim(1.2, 2.6)
eksen(ax, "Toplam doğurganlık hızı", "kadın başına çocuk · 2002–2013 arası ara değer yok")

# 2. Doğurganlık: yerleşim ve eğitim
ax = eksenler[0, 1]
etiketler = ["Kır", "Orta yoğun kent", "Yoğun kent", "", "Anne: ilkokul", "Anne: üniversite"]
degerler = [1.75, 1.53, 1.33, None, 2.51, 1.24]
for i, (e, v) in enumerate(zip(etiketler, degerler)):
    if v is None:
        continue
    ax.barh(i, v, color=MAVI, height=0.62, zorder=3)
    ax.text(v + 0.04, i, tr(v, 2), va="center", fontsize=8.5)
ax.set_yticks(range(len(etiketler)))
ax.set_yticklabels(etiketler)
ax.invert_yaxis()
ax.axvline(2.10, color=REF, lw=1, ls=(0, (4, 3)), zorder=2)
ax.text(2.12, 3, "2,10", color=YAZI_2, fontsize=8, va="center")
ax.set_xlim(0, 2.9)
ax.grid(axis="x", color=IZGARA, lw=0.6)
eksen(ax, "Doğurganlık: yerleşim ve eğitim (2025)", "eğitim farkı, kent–kır farkının yaklaşık üç katı")
ax.grid(axis="y", visible=False)

# 3. Evlenme ve boşanma
ax = eksenler[0, 2]
x1, y1 = seri("Kaba evlenme hızı")
x2, y2 = seri("Kaba boşanma hızı")
ax.plot(x1, y1, color=MAVI, lw=2, marker="o", ms=4.5, mec=ZEMIN, mew=1.2, label="Evlenme", zorder=3)
ax.plot(x2, y2, color=TURUNCU, lw=2, marker="o", ms=4.5, mec=ZEMIN, mew=1.2, label="Boşanma", zorder=3)
for xs, ys in ((x1, y1), (x2, y2)):
    for i in (0, -1):
        ax.annotate(tr(ys[i], 2), (xs[i], ys[i]), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8.5)
ax.text(2008, 7.6, "Evlenme", color=YAZI, fontsize=8.5)
ax.text(2008, 2.0, "Boşanma", color=YAZI, fontsize=8.5)
ax.set_ylim(0, 10)
ax.legend(loc="upper right", frameon=False, fontsize=8)
eksen(ax, "Kaba evlenme ve boşanma hızı", "bin kişide · 100 evliliğe karşılık boşanma: 17 → 35")

# 4. Bina kat sayısı
ax = eksenler[1, 0]
katlar = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10+"]
paylar = [d[d.gosterge == f"Hanelerin ikamet ettiği binanın kat sayısı: {k} kat"].deger_n.iloc[0] for k in katlar]
ax.bar(katlar, paylar, color=MAVI, width=0.7, zorder=3)
for k, p in zip(katlar, paylar):
    ax.text(k, p + 0.3, tr(p), ha="center", fontsize=8)
ax.set_ylim(0, 19)
ax.set_xlabel("binanın kat sayısı")
eksen(ax, "Hanelerin oturduğu binanın kat sayısı (2021)", "hanelerin %'si · %71'i 3 ve daha çok katlı binada")

# 5. Ev sahipliği
ax = eksenler[1, 1]
x, y = seri("Ev sahipliği oranı (nüfus)")
cizgi(ax, x, y)
_, ab = seri("Ev sahipliği oranı (nüfus)", "AB-27")
referans(ax, ab[-1], f"AB-27 (2025) %{tr(ab[-1])}", 2006)
ax.set_ylim(50, 72)
eksen(ax, "Ev sahipliği oranı", "nüfusun %'si · Eurostat")

# 6. Aşırı kalabalık konut
ax = eksenler[1, 2]
x, y = seri("Aşırı kalabalık konutta yaşayan nüfus oranı")
cizgi(ax, x, y)
_, ab = seri("Aşırı kalabalık konutta yaşayan nüfus oranı", "AB-27")
referans(ax, ab[-1], f"AB-27 (2025) %{tr(ab[-1])}", 2006)
ax.set_ylim(0, 60)
eksen(ax, "Aşırı kalabalık konutta yaşayanlar", "nüfusun %'si · Eurostat")

# 7. Antidepresan
ax = eksenler[2, 0]
x, y = seri("Antidepresan tüketimi")
cizgi(ax, x, y)
oecd = d[d.gosterge.str.startswith("Antidepresan tüketimi – raporlayan")].deger_n.iloc[0]
referans(ax, oecd, f"OECD medyanı (2024) {tr(oecd)}", 2010)
ax.set_ylim(0, 80)
eksen(ax, "Antidepresan tüketimi", "günlük 1000 kişi başına standart doz (DDD) · OECD · 2010–2024 %77 artış")

# 8. Otomobil
ax = eksenler[2, 1]
s = d[d.gosterge.str.startswith("1000 kişi başına otomobil")].dropna(subset=["deger_n"])
x = [2015, 2024, 2025, 2026.7]
y = s.deger_n.tolist()
cizgi(ax, x, y)
ax.set_xticks([2015, 2018, 2021, 2024, 2026.7])
ax.set_xticklabels(["2015", "2018", "2021", "2024", "Eyl.\n2026"])
ax.set_ylim(0, 250)
eksen(ax, "1000 kişi başına otomobil", "trafiğe kayıtlı otomobil / nüfus · hesaplama (TÜİK)")

# 9. Güven
ax = eksenler[2, 2]
x, y = seri("Diğer insanlara güven ortalama puanı")
cizgi(ax, x, y)
_, ab = seri("Diğer insanlara güven ortalama puanı", "AB-27")
referans(ax, ab[-1], f"AB-27 (2025) {tr(ab[-1])}", 2013)
ax.set_ylim(0, 10)
eksen(ax, "Diğer insanlara güven", "0–10 puan, 16+ yaş · Eurostat")

virgul = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
for ax in eksenler.flat:
    if ax not in (eksenler[0, 1], eksenler[1, 0], eksenler[2, 1]):
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True, nbins=6))
    if ax is not eksenler[0, 1]:
        ax.yaxis.set_major_formatter(virgul)
eksenler[0, 1].xaxis.set_major_formatter(virgul)

fig.text(0.05, 0.02,
         "Not: Kesikli gri çizgiler karşılaştırma değerleridir. Doğurganlık serisinde 2023 ve 2024 değerleri TÜİK'in 2026 revizyonudur. "
         "Otomobil yoğunluğu, kayıtlı otomobil sayısının ADNKS nüfusuna bölünmesiyle hesaplanmıştır.",
         fontsize=8, color=YAZI_2)

for uzanti in ("png", "svg"):
    fig.savefig(CIKTI / f"durum_tespiti_grafik_seti.{uzanti}", facecolor=ZEMIN)
sys.stdout.reconfigure(encoding="utf-8")
print("yazıldı:", CIKTI)
