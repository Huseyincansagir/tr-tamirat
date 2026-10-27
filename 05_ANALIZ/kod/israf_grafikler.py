"""
Faz 4 · Rapor 6 — İsraf, fire ve kaçak: grafikler ve haritalar
=============================================================
Girdi : 05_ANALIZ/sonuclar/israf_*.csv (önce israf_hesap.py), 03_VERI/ham/israf/sdmx/DF_TUFE_SDMX_TT01.json,
        03_VERI/ham/sinirlar/geoBoundaries-TUR-ADM1_simplified.geojson
Çıktı : 05_ANALIZ/grafikler/israf_fatura.png|svg           yıllık israf faturası (kalem bazında alt–üst aralık)
        05_ANALIZ/grafikler/israf_tarim_fiyat.png|svg      üretici fiyatlarında dalgalanma (TÜFE ile karşılaştırmalı)
        04_HARITA/israf_kayip_kacak_haritalari.png|svg     il bazında su ve elektrik kayıp-kaçak oranları

Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/israf_grafikler.py
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib import patheffects as pe
from matplotlib.patches import Patch

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
SON = KOK / "05_ANALIZ" / "sonuclar"
GRAF = KOK / "05_ANALIZ" / "grafikler"
HARITA = KOK / "04_HARITA"
GRAF.mkdir(parents=True, exist_ok=True)

MAVI, TURUNCU, AQUA, SARI = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
YAZI, YAZI_2, ZEMIN, GRI, IZGARA = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df", "#ecebe7"
MAVI_R = ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"]
TURUNCU_R = ["#fbe3d6", "#f5b392", "#ee8a5c", "#d95926", "#a8400f"]
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m +no_defs"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "savefig.facecolor": ZEMIN, "svg.fonttype": "none"})


def tr(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def acik(hex_renk, t=0.55):
    """Rengi zemine doğru açar (belirsizlik bölümü için)."""
    h = hex_renk.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    z = (252, 252, 251)
    return "#" + "".join(f"{int(c + (zc - c) * t):02x}" for c, zc in zip((r, g, b), z))


def kaydet(fig, yol):
    for uz in ("png", "svg"):
        fig.savefig(yol.with_suffix(f".{uz}"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("yazıldı:", yol.with_suffix(".png").relative_to(KOK))


# ======================================================================= 1. Yıllık israf faturası
F = pd.read_csv(SON / "israf_fatura.csv")
top = F[F.no == 99].iloc[0]
F = F[F.toplamda == True].copy()  # noqa: E712
F["orta"] = (F.deger_usd_alt + F.deger_usd_ust) / 2
F = F.sort_values("orta")
RENK = {"Enerji": MAVI, "Gıda": TURUNCU, "Su ve atık": AQUA, "Zaman ve yakıt": SARI}
KISA = {
    "Elektrik dağıtımında kayıp-kaçak": "Elektrik dağıtımında kayıp-kaçak (2025)",
    "Doğal gaz kayıpları": "Doğal gaz şebekesi kayıp ve kaçağı (2025)",
    "İçme suyu kayıp-kaçağı": "İçme suyu kayıp-kaçağı (2024)",
    "Gıda israfı: hane ve gıda hizmeti": "Gıda israfı: hane ve lokanta (2022 miktarı)",
    "Hasat ve hasat sonrası kayıplar (tahıl, sebze, meyve)": "Hasat ve hasat sonrası kayıp (2020/21 miktarı)",
    "Trafik sıkışıklığı: kaybedilen zaman (6 büyük kent)": "Trafikte kaybedilen zaman, 6 kent (2025)",
    "Trafik sıkışıklığı: ek yakıt (6 büyük kent)": "Trafikte fazladan yakılan yakıt, 6 kent (2025)",
    "Binalarda ısı kaybı (yalıtımsız konutlarda fazladan yakılan gaz)": "Yalıtımsız konutlarda fazladan yakılan gaz (2025)",
    "Depolamaya giden geri dönüştürülebilir belediye atığı": "Çöpe giden geri dönüştürülebilir atık (2024)",
    "Toplanmayan e-atıktaki malzeme": "Toplanmayan e-atıktaki metal ve malzeme (2022 miktarı)",
    "Sanayide değerlendirilmeyen atık ısı": "Sanayide kullanılmayan atık ısı (2025)",
}
fig, ax = plt.subplots(figsize=(11.5, 6.8))
y = np.arange(len(F))
h = 0.52
for i, r in enumerate(F.itertuples()):
    a, u = r.deger_usd_alt / 1e9, r.deger_usd_ust / 1e9
    c = RENK[r.grup]
    ax.barh(i, a, height=h, color=c, edgecolor=ZEMIN, linewidth=0)
    ax.barh(i, u - a, left=a, height=h, color=acik(c), edgecolor=ZEMIN, linewidth=0)
    ax.plot([a, a], [i - h / 2, i + h / 2], color=ZEMIN, lw=2, solid_capstyle="butt")  # 2 px yüzey boşluğu
    etiket = f"{tr(a, 2 if a < 0.1 else 1)}–{tr(u, 1 if u >= 0.1 else 2)} milyar $  ·  GSYH %{tr(r.gsyh_pay_alt, 2)}–{tr(r.gsyh_pay_ust, 2)}"
    ax.text(u + 0.12, i, etiket, va="center", ha="left", fontsize=8, color=YAZI_2)
ax.set_yticks(y, [KISA.get(k, k) for k in F.kalem], fontsize=8.6, color=YAZI)
ax.set_xlim(0, 13.5)
ax.set_xlabel("Milyar ABD doları / yıl (veri yılının fiyat ve kuruyla)", color=YAZI_2)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: tr(v, 0)))
ax.grid(axis="x", color=IZGARA, lw=0.8)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRI)
ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", colors=YAZI_2)
plt.subplots_adjust(left=0.37, right=0.98, top=0.86, bottom=0.12)
fig.text(0.01, 0.965, "Türkiye'nin yıllık israf faturası", ha="left", fontsize=13, fontweight="bold", color=YAZI)
fig.text(0.01, 0.925, f"Toplam {tr(top.deger_usd_alt / 1e9, 1)}–{tr(top.deger_usd_ust / 1e9, 1)} milyar $ / yıl, GSYH'nin %{tr(top.gsyh_pay_alt, 2)}–{tr(top.gsyh_pay_ust, 2)}'i.",
         ha="left", fontsize=9.5, color=YAZI)
fig.text(0.01, 0.893, "Koyu bölüm: alt tahmin (yalnız önlenebilir kısım, ihtiyatlı fiyat). Açık bölüm: üst tahmine kadar belirsizlik.",
         ha="left", fontsize=8.4, color=YAZI_2)
leg = [Patch(color=v, label=k) for k, v in RENK.items()]
ax.legend(handles=leg, loc="lower right", frameon=False, fontsize=8.4, labelcolor=YAZI, title="Kalem grubu", title_fontsize=8.4)
fig.text(0.01, 0.045, "Kaynak: EPDK 2025 elektrik ve doğal gaz gelişim raporları; TÜİK (su, atık, sera gazı, taşıt, üretici fiyatları, GSYH; SDMX); UNEP Gıda İsrafı Endeksi 2024; "
         "TZOB (2022); TomTom 2025; ETKB 2. UEVEP; Global E-waste Monitor 2024; İZODER.\nToplamda çifte sayma ayıklandı (perakende gıda israfı, ekmek, atığın organik kısmı ve boş konut, arazi, enkaz dışarıda). "
         "Hesap: 05_ANALIZ/kod/israf_hesap.py", fontsize=6.8, color=YAZI_2, ha="left", va="top")
kaydet(fig, GRAF / "israf_fatura")

# ======================================================================= 2. Tarımda fiyat dalgalanması
fa = pd.read_csv(SON / "israf_tarim_fiyat_aylik.csv", index_col=0)
d = json.load(open(KOK / "03_VERI" / "ham" / "israf" / "sdmx" / "DF_TUFE_SDMX_TT01.json", encoding="utf-8"))
idx = d["dimension"]["TIME_PERIOD"]["category"]["index"]
donem = [k for k, _ in sorted(idx.items(), key=lambda t: t[1])] if isinstance(idx, dict) else list(idx)
tufe = pd.Series({donem[int(k)]: float(v) for k, v in (d["value"].items() if isinstance(d["value"], dict) else enumerate(d["value"])) if v not in (None, "")})
tufe = tufe[tufe.index >= "2024-01"]
tufe = 100 * tufe / tufe[tufe.index.str.startswith("2024")].mean()
URUN = [("Lemons and limes", "Limon", MAVI), ("Tomatoes", "Domates", TURUNCU), ("Onion (dry)", "Kuru soğan", AQUA), ("Potatoes", "Patates", SARI)]
fig, ax = plt.subplots(figsize=(9.2, 5.0))
x_tum = sorted(set(fa.index) | set(tufe.index))
xi = {k: i for i, k in enumerate(x_tum)}
ax.plot([xi[k] for k in tufe.index], tufe.values, color=YAZI_2, lw=2, ls=(0, (4, 2)), label="TÜFE (genel)")
uclar = [("TÜFE", xi[tufe.index[-1]], tufe.values[-1], YAZI_2)]
for kol, ad, c in URUN:
    s = fa[kol]
    s = 100 * s / s[s.index.str.startswith("2024")].mean()
    s = s.reindex(x_tum)                      # fiyatlanmayan aylar boşluk olarak kalır (çizgi birleştirilmez)
    ax.plot(range(len(x_tum)), s.values, color=c, lw=2, solid_joinstyle="round", solid_capstyle="round", label=ad)
    yalniz = s[s.notna() & s.shift(1).isna() & s.shift(-1).isna()]
    ax.plot([xi[k] for k in yalniz.index], yalniz.values, "o", ms=4, color=c)
    son = s.dropna()
    ax.plot(xi[son.index[-1]], son.values[-1], "o", ms=6, color=c, mec=ZEMIN, mew=2)
    uclar.append((ad, xi[son.index[-1]], son.values[-1], YAZI))
# uç etiketlerini çakışmayacak biçimde aralıkla
uclar.sort(key=lambda t: t[2])
yer = []
for ad, x, v, c in uclar:
    yy = v if not yer else max(v, yer[-1] + 26)
    yer.append(yy)
    ax.annotate(f"{ad} {tr(v, 0)}", (x, v), xytext=(len(x_tum) + 0.3, yy), textcoords="data", va="center", fontsize=8, color=c,
                arrowprops=dict(arrowstyle="-", color=GRI, lw=0.8) if abs(yy - v) > 4 else None)
ax.axhline(100, color=GRI, lw=1)
yil_bas = [k for k in x_tum if k.endswith("-01")]
ax.set_xticks([xi[k] for k in yil_bas], [k[:4] for k in yil_bas], color=YAZI_2)
ax.set_xlim(-0.5, len(x_tum) + 6)
ax.set_ylabel("Endeks (ürünün 2024 ortalaması = 100)", color=YAZI_2)
ax.grid(axis="y", color=IZGARA, lw=0.8)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color(GRI)
ax.tick_params(colors=YAZI_2)
plt.subplots_adjust(left=0.08, right=0.98, top=0.80, bottom=0.14)
fig.text(0.01, 0.955, "Üretici fiyatlarında sert iniş-çıkış: enflasyonun altında geçen yılı ani sıçrama izliyor", ha="left",
         fontsize=12, fontweight="bold", color=YAZI)
fig.text(0.01, 0.915, "Türkiye geneli aylık üretici fiyatları (TL/kg), her ürünün kendi 2024 ortalamasına göre endeks; kesikli çizgi genel enflasyon (TÜFE)",
         ha="left", fontsize=8.6, color=YAZI_2)
fig.legend(*ax.get_legend_handles_labels(), loc="upper left", bbox_to_anchor=(0.005, 0.90), ncol=5, frameon=False, fontsize=8.4, labelcolor=YAZI)
fig.text(0.01, 0.06, "Kaynak: TÜİK, Tarım Ürünleri Üretici Fiyatları (DF_TARIM_URUNLERI_UFE_MADDE_FIYAT_V2) ve TÜFE (DF_TUFE_SDMX_TT01), 2024-01 – 2026-09. "
         "Limon yalnız hasat aylarında fiyatlanıyor (boşluklar).\nFiyat dalgalanmasında don, kuraklık ve ihracat kararları da etkili; grafik planlama sorununun dolaylı göstergesidir.",
         fontsize=7, color=YAZI_2, ha="left", va="top")
kaydet(fig, GRAF / "israf_tarim_fiyat")

# ======================================================================= 3. İl haritaları: su ve elektrik kayıp-kaçağı
il = gpd.read_file(KOK / "03_VERI" / "ham" / "sinirlar" / "geoBoundaries-TUR-ADM1_simplified.geojson")
il["il"] = il.shapeName.replace({"Hakkâri": "Hakkari"})
su = pd.read_csv(SON / "israf_su_il.csv")[["il", "kayip_oran_2024", "kayip_oran_2022"]]
ele = pd.read_csv(SON / "israf_elektrik_il.csv")[["il", "sirket", "oran_2025"]]
G = il.merge(su, on="il", how="left").merge(ele, on="il", how="left").to_crs(LCC)
assert G.kayip_oran_2024.notna().all() and G.oran_2025.notna().all()
bolge = G.assign(sirket=G.sirket.replace({"AYEDAŞ+BOĞAZİÇİ": "İSTANBUL"})).dissolve("sirket")

fig, axs = plt.subplots(2, 1, figsize=(10, 8.8))
PANEL = [
    (axs[0], "kayip_oran_2024", MAVI_R, [0, 15, 25, 35, 45, 100], ["< 15", "15–25", "25–35", "35–45", "≥ 45"],
     "İçme suyu: belediyelerin çektiği suyun dağıtılamayan payı, 2024 (%)",
     "Türkiye %32,6. Yönetmelik üst sınırı %25 (büyükşehir ve il belediyeleri). 81 ilden 55'i sınırın üstünde."),
    (axs[1], "oran_2025", TURUNCU_R, [0, 5, 7, 10, 20, 100], ["< 5", "5–7", "7–10", "10–20", "≥ 20"],
     "Elektrik: dağıtım şebekesine giren enerjinin kayıp-kaçak payı, 2025 (%)",
     "Türkiye %8,8. Her il, bağlı olduğu dağıtım şirketinin oranını alır (kalın çizgiler: 21 dağıtım bölgesi)."),
]
for ax, kol, renk, sinif, etk, baslik, alt in PANEL:
    G.plot(ax=ax, column=kol, cmap=ListedColormap(renk), norm=BoundaryNorm(sinif, len(renk)), edgecolor="white", linewidth=0.5)
    if kol == "oran_2025":
        bolge.boundary.plot(ax=ax, color=YAZI_2, linewidth=1.1)
    ax.set_axis_off()
    ax.set_title(baslik, loc="left", fontsize=10.5, fontweight="bold", color=YAZI, pad=16)
    ax.text(0, 1.0, alt, transform=ax.transAxes, fontsize=8.3, color=YAZI_2, va="bottom")
    ax.legend(handles=[Patch(color=c, label=e) for c, e in zip(renk, etk)], loc="lower left", frameon=False, fontsize=8,
              ncol=5, labelcolor=YAZI, bbox_to_anchor=(0.0, -0.08), handlelength=1.4, columnspacing=1.0)
# seçili etiketler (en yüksek değerler ve büyük kentler)
def yaz(ax, ad, metin, koyu):
    m = G[G.il == ad].geometry.iloc[0].representative_point()
    ax.annotate(metin, (m.x, m.y), ha="center", va="center", fontsize=7, color=YAZI, fontweight="bold",
                path_effects=[pe.withStroke(linewidth=2.4, foreground="white")])
for ad in G.nlargest(5, "kayip_oran_2024").il.tolist() + ["İstanbul", "Ankara", "Şanlıurfa"]:
    v = G.loc[G.il == ad, "kayip_oran_2024"].iloc[0]
    yaz(axs[0], ad, f"{ad}\n%{tr(v, 0)}", v >= 35)
for ad, bas in [("Diyarbakır", "Dicle"), ("Van", "Vangölü"), ("Erzurum", "Aras"), ("Mersin", "Toroslar"), ("Malatya", "Fırat"), ("Ankara", "Başkent")]:
    v = G.loc[G.il == ad, "oran_2025"].iloc[0]
    yaz(axs[1], ad, f"{bas}\n%{tr(v, 1)}", v >= 10)
fig.text(0.02, 0.02, "Kaynak: TÜİK Belediye Su İstatistikleri 2024 (SDMX; çekilen − dağıtılan su, kayıp-kaçağın vekili); EPDK 2025 Yılı Elektrik Piyasası Gelişim Raporu, Tablo 5.2; "
         "il sınırları geoBoundaries ADM1.\nİstanbul elektrik oranı AYEDAŞ (%3,68) ve Boğaziçi'nin (%5,69) dağıtım tüketimiyle ağırlıklı ortalamasıdır. Projeksiyon: LCC (37°–41°).",
         fontsize=7, color=YAZI_2, ha="left", va="top")
plt.subplots_adjust(hspace=0.16, bottom=0.07, top=0.95)
kaydet(fig, HARITA / "israf_kayip_kacak_haritalari")
