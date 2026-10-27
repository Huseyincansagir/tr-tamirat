"""
Faz 4 · Ulusal mekânsal çerçeve — haritalar ve ilke şeması
=========================================================
Girdi : 03_VERI/islenmis/ulusal_altyapi/ ve 05_ANALIZ/sonuclar/ulusal_plan_*.csv (önceki ulusal_plan_* betikleri)
Çıktı : 04_HARITA/ulusal_plan/
  01_ulasim.png|svg          yol, demiryolu, havalimanı, liman
  02_enerji.png|svg          iletim hatları (≥154 kV), santraller ve üreteçler kaynağa göre
  03_nufus_sanayi.png|svg    nüfus yoğunluğu ve sanayi alanları
  04_erisim.png|svg          istasyon, havalimanı (süre), liman erişimi + il bazında istasyon açığı
  05_sanayi_yakinlik.png|svg sanayi alanlarının yerleşim, tarım ve PM2.5 ile ilişkisi
  06_kisit.png|svg           kısıt haritası
  07_sema.png|svg            ilke haritası: koridorlar, uydu kent bandı, sanayi ilke alanı (yer seçimi değil)
  08_ilke_semasi.png|svg     bölge biriminde ilkeler bir arada (kavramsal şema; kademe şemasının bölge ölçeğine devamı)
Projeksiyon: +proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35
SVG: ağır katmanlar (raster, yoğun nokta ve çizgi) rasterized=True ile gömülür; dosyalar < 20 MB.
"""
import re
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Patch, Polygon, Rectangle
from scipy import ndimage

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
CIK = KOK / "03_VERI" / "islenmis" / "ulusal_altyapi"
SON = KOK / "05_ANALIZ" / "sonuclar"
HAR = KOK / "04_HARITA" / "ulusal_plan"
HAR.mkdir(parents=True, exist_ok=True)
LCC = "+proj=lcc +lat_1=37 +lat_2=41 +lat_0=39 +lon_0=35 +datum=WGS84 +units=m +no_defs"
MAVI, TURUNCU, AQUA, SARI = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
YAZI, YAZI2, ZEMIN = "#0b0b0b", "#52514e", "#fcfcfb"
KARA, IL_C, SINIR_C = "#efeee9", "#dcdad4", "#9a9893"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "svg.fonttype": "none"})
# Türkiye LCC sınırları ≈ x −794…869 km, y −354…372 km. Güneyde 37°K altındaki boş alan (Suriye, Irak) lejanta ayrılır.
XL, YL = (-810_000, 885_000), (-500_000, 390_000)

il = gpd.read_file(KOK / "03_VERI" / "ham" / "sinirlar" / "geoBoundaries-TUR-ADM1_simplified.geojson").to_crs(LCC)
il["il"] = il.shapeName.replace({"Hakkâri": "Hakkari"})
ulke = il.dissolve()
kentler = pd.read_csv(SON / "ulusal_plan_kentler.csv") if (SON / "ulusal_plan_kentler.csv").exists() else None


def tr(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def ek(n):
    """Sayıdan sonra gelen üçüncü tekil iyelik eki: %55'i, %72'si, %99'u, %40'ı."""
    n = int(round(abs(n)))
    if n == 0:
        return "ı"
    if n % 10:
        return {1: "i", 2: "si", 3: "ü", 4: "ü", 5: "i", 6: "sı", 7: "si", 8: "i", 9: "u"}[n % 10]
    if n % 100:
        return {10: "u", 20: "si", 30: "u", 40: "ı", 50: "si", 60: "ı", 70: "i", 80: "i", 90: "ı"}[n % 100]
    return "ü"


def yuzde(v, nd=0):
    return f"%{tr(v, nd)}'{ek(v)}"


def blok_nanmin(a, k=4):
    h, w = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    b = a[:h, :w].reshape(h // k, k, w // k, k)
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return np.nanmin(b, axis=(1, 3))


def oku(ad, bant=1):
    with rasterio.open(CIK / ad) as d:
        a = d.read(bant)
        t = d.transform
    return a, [t.c, t.c + t.a * a.shape[1], t.f + t.e * a.shape[0], t.f]


def blok_max(a, k=4):
    """Ulusal ölçekte 250 m hücreler pikselden küçük; görünürlük için k×k bloğun en büyük değeri."""
    h, w = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    return a[:h, :w].reshape(h // k, k, w // k, k).max(axis=(1, 3))


def taban(ax, dolgu=KARA, il_cizgi=True):
    il.plot(ax=ax, color=dolgu, edgecolor=IL_C if il_cizgi else "none", linewidth=0.35, zorder=0)
    ulke.boundary.plot(ax=ax, color=SINIR_C, linewidth=0.6, zorder=6)
    ax.set_xlim(*XL)
    ax.set_ylim(*YL)
    ax.set_aspect("equal")
    ax.set_axis_off()


def ust_cizgi(ax):
    ulke.boundary.plot(ax=ax, color=SINIR_C, linewidth=0.6, zorder=6)
    il.boundary.plot(ax=ax, color="white", linewidth=0.3, alpha=0.7, zorder=5)


def olcek(ax, x0=-770_000, y0=-440_000, km=200, yuk=6000):
    for i, renk in enumerate([YAZI, "white", YAZI, "white"]):
        ax.add_patch(Rectangle((x0 + i * km * 250, y0), km * 250, yuk, facecolor=renk, edgecolor=YAZI, lw=0.5, zorder=20))
    for v in (0, km // 2, km):
        ax.text(x0 + v * 1000, y0 + yuk + 5000, f"{v}" + (" km" if v == km else ""), ha="center", va="bottom",
                fontsize=7, color=YAZI2, zorder=20)
    ax.annotate("", xy=(x0 + 8000, y0 + 75_000), xytext=(x0 + 8000, y0 + 32_000),
                arrowprops=dict(arrowstyle="-|>", color=YAZI, lw=1), zorder=20)
    ax.text(x0 + 8000, y0 + 79_000, "K", ha="center", va="bottom", fontsize=8, fontweight="bold", color=YAZI)


def basliklar(fig, ana, alt, kaynak, y=0.955):
    fig.text(0.015, y, ana, fontsize=17, fontweight="bold", color=YAZI)
    fig.text(0.015, y - 0.035, alt, fontsize=9.5, color=YAZI2)
    fig.text(0.015, 0.012, kaynak, fontsize=7.2, color=YAZI2)


def etiket_kent(ax, en_az=500_000, boyut=7.5, renk=YAZI):
    if kentler is None:
        return
    for r in kentler[kentler.nufus >= en_az].itertuples():
        ad = r.ad.split("–")[0]
        ax.text(r.x + 9000, r.y + 7000, ad, fontsize=boyut, color=renk, zorder=30,
                bbox=dict(facecolor="white", alpha=0.65, edgecolor="none", pad=0.4))


def kaydet(fig, ad):
    for uz in ("png", "svg"):
        fig.savefig(HAR / f"{ad}.{uz}", facecolor=ZEMIN, dpi=170 if uz == "png" else 150)
    plt.close(fig)
    print("yazıldı:", ad, f"svg {(HAR / f'{ad}.svg').stat().st_size / 1e6:.1f} MB")


def lej(ax, h, loc="lower right", ncol=1, baslik=None, bbox=None, fs=7.6):
    L = ax.legend(handles=h, loc=loc, ncol=ncol, frameon=True, fontsize=fs, title=baslik, title_fontsize=8,
                  bbox_to_anchor=bbox, borderpad=0.7, labelspacing=0.5, handlelength=2.2, columnspacing=1.4)
    L.get_frame().set_facecolor("white")
    L.get_frame().set_edgecolor("#dcdad4")
    L.get_frame().set_alpha(0.94)
    L._legend_box.align = "left"
    L.set_zorder(40)
    return L


def sadele(gdf, tol):
    g = gdf.copy()
    g["geometry"] = g.geometry.simplify(tol)
    return g


fay = gpd.clip(gpd.read_file(CIK / "diri_faylar_gem.gpkg").to_crs(LCC), ulke)

# ===================== 01 Ulaşım =========================================================================
yol = gpd.read_file(CIK / "yollar.gpkg").to_crs(LCC)
ray = gpd.read_file(CIK / "demiryollari.gpkg").to_crs(LCC)
ray = ray[~ray.service.isin(["yard", "siding", "spur", "crossover"]) & ~ray.usage.isin(["industrial", "military"])]
hav = gpd.read_file(CIK / "havalimanlari_yolcu.gpkg").to_crs(LCC)
lim = gpd.read_file(CIK / "limanlar_yuk.gpkg").to_crs(LCC)
ist = gpd.read_file(CIK / "istasyonlar_yolcu.gpkg").to_crs(LCC)
L_yol = yol.assign(km=yol.length / 1000).groupby("highway").km.sum()

fig, ax = plt.subplots(figsize=(15, 8.6))
fig.subplots_adjust(left=0.01, right=0.99, top=0.885, bottom=0.035)
taban(ax)
for hw, renk, lw in [("primary", "#c9c7c1", 0.45), ("trunk", "#a3a19b", 0.7), ("motorway", "#3d3c39", 1.3)]:
    s = sadele(yol[yol.highway == hw], 120)
    s.plot(ax=ax, color=renk, linewidth=lw, zorder=2, rasterized=hw != "motorway")
s = sadele(yol[yol.highway.isin(["yapim_motorway"])], 120)
s.plot(ax=ax, color="#3d3c39", linewidth=1.1, linestyle=(0, (2, 1.5)), zorder=2)
kon = ray[(ray.railway == "rail") & (ray.highspeed != "yes")]
hiz = ray[(ray.railway == "rail") & (ray.highspeed == "yes")]
yap = ray[ray.railway == "construction"]
sadele(kon, 80).plot(ax=ax, color=MAVI, linewidth=1.0, zorder=3)
sadele(hiz, 80).plot(ax=ax, color=MAVI, linewidth=2.8, zorder=3)
sadele(yap, 80).plot(ax=ax, color=MAVI, linewidth=1.8, linestyle=(0, (2.5, 1.5)), zorder=3)
ax.scatter(ist.geometry.x, ist.geometry.y, s=3, color=MAVI, zorder=4, linewidths=0, rasterized=True)
ax.scatter(hav.geometry.x, hav.geometry.y, s=60, marker="^", color=TURUNCU, edgecolor=YAZI, linewidth=0.6, zorder=8)
yk = lim[lim.sinif != "enerji"]
for bag, fc in [(True, AQUA), (False, "white")]:
    s = yk[yk.demiryolu_bagli == bag]
    ax.scatter(s.geometry.x, s.geometry.y, s=np.where(s.sinif == "ana", 70, 32), marker="s", color=fc, edgecolor=YAZI,
               linewidth=0.8, zorder=9)
en = lim[lim.sinif == "enerji"]
ax.scatter(en.geometry.x, en.geometry.y, s=30, marker="D", color="white", edgecolor=YAZI2, linewidth=0.7, zorder=9)
etiket_kent(ax, 700_000)
olcek(ax)
h = [Line2D([], [], color="#3d3c39", lw=1.3, label=f"Otoyol ({tr(L_yol.get('motorway', 0))} km yön çizgisi)"),
     Line2D([], [], color="#3d3c39", lw=1.1, ls=(0, (2, 1.5)), label="Otoyol, yapımda"),
     Line2D([], [], color="#a3a19b", lw=0.9, label="Devlet yolu (trunk)"),
     Line2D([], [], color="#c9c7c1", lw=0.8, label="İl yolu (primary)"),
     Line2D([], [], color=MAVI, lw=2.8, label=f"Hızlı tren hattı ({tr(hiz.length.sum() / 1000)} km iz)"),
     Line2D([], [], color=MAVI, lw=1.0, label=f"Konvansiyonel hat ({tr(kon.length.sum() / 1000)} km iz)"),
     Line2D([], [], color=MAVI, lw=1.8, ls=(0, (2.5, 1.5)), label=f"Demiryolu, yapımda ({tr(yap.length.sum() / 1000)} km)"),
     Line2D([], [], marker="o", color=MAVI, lw=0, ms=3, label=f"Yolcu istasyonu / durak ({len(ist)})"),
     Line2D([], [], marker="^", color=TURUNCU, mec=YAZI, lw=0, ms=8, label=f"Yolcu havalimanı ({len(hav)})"),
     Line2D([], [], marker="s", color=AQUA, mec=YAZI, lw=0, ms=7, label="Yük limanı, demiryolu ≤ 2 km"),
     Line2D([], [], marker="s", color="white", mec=YAZI, lw=0, ms=7, label="Yük limanı, demiryolu yok"),
     Line2D([], [], marker="D", color="white", mec=YAZI2, lw=0, ms=5, label="Enerji terminali (petrol, LNG)")]
lej(ax, h, loc="lower right", bbox=(1.0, 0.0), ncol=2)
basliklar(fig, "Ulaşım ağı: yol, demiryolu, havalimanı ve liman (Ekim 2026)",
          "Uzunluklar OSM çizgi uzunluğudur: otoyol iki yön ayrı çizildiği için yol uzunluğunun ≈ 2 katı; çift hatlı kesimler "
          "de iki iz sayılır. Büyük kare: ulusal ölçekte ana liman.",
          "Kaynak: © OpenStreetMap katkıcıları (Geofabrik Türkiye çıkarımı, Ekim 2026), ODbL · liman sınıfı ve havalimanı "
          "ayıklaması: UAB, DHMİ ikincil kaynaklar [İ] · il sınırları geoBoundaries · Projeksiyon: LCC (37°/41°)")
kaydet(fig, "01_ulasim")

# ===================== 02 Enerji ==========================================================================
hat = gpd.read_file(CIK / "iletim_hatlari.gpkg").to_crs(LCC)
sant = gpd.read_file(CIK / "santraller.gpkg").to_crs(LCC)
uret = gpd.read_file(CIK / "uretecler.gpkg").to_crs(LCC)


def mw(s):
    m = re.search(r"([\d.,]+)\s*(MW|GW|kW)", s or "", re.I)
    if not m:
        return np.nan
    v = float(m.group(1).replace(",", "."))
    return v * {"mw": 1, "gw": 1000, "kw": 0.001}[m.group(2).lower()]


sant["mw"] = sant.guc.apply(mw)
KAY = [("hydro", "Hidroelektrik", MAVI, "o"), ("solar", "Güneş", SARI, "o"), ("wind", "Rüzgâr", AQUA, "o"),
       ("gas", "Doğal gaz", TURUNCU, "o"), ("coal", "Kömür, linyit", YAZI2, "o"), ("geothermal", "Jeotermal", "white", "o"),
       ("nuclear", "Nükleer (yapımda)", YAZI, "*")]
fig, ax = plt.subplots(figsize=(15, 8.6))
fig.subplots_adjust(left=0.01, right=0.99, top=0.885, bottom=0.035)
taban(ax)
sadele(hat[hat.gerilim_v < 380000], 100).plot(ax=ax, color="#a9a7a1", linewidth=0.55, zorder=2, rasterized=True)
sadele(hat[hat.gerilim_v >= 380000], 100).plot(ax=ax, color="#3d3c39", linewidth=1.2, zorder=3)
us = uret[uret.kaynak == "solar"]
uw = uret[uret.kaynak == "wind"]
ax.scatter(us.geometry.x, us.geometry.y, s=1.2, color=SARI, alpha=0.5, linewidths=0, zorder=4, rasterized=True)
ax.scatter(uw.geometry.x, uw.geometry.y, s=1.5, color=AQUA, alpha=0.8, linewidths=0, zorder=4, rasterized=True)
for k_, ad, renk, mk in KAY:
    s = sant[sant.kaynak.str.split(";").str[0] == k_]
    boy = np.where(s.mw.notna(), np.clip(np.sqrt(s.mw.fillna(1)) * 3.2, 8, 160), 10)
    ax.scatter(s.geometry.x, s.geometry.y, s=boy if mk == "o" else 160, marker=mk, color=renk, edgecolor=YAZI,
               linewidth=0.45, alpha=0.9, zorder=7 if k_ in ("coal", "gas", "nuclear") else 6)
etiket_kent(ax, 1_000_000)
olcek(ax)
say = sant.kaynak.str.split(";").str[0].value_counts()
h = [Line2D([], [], color="#3d3c39", lw=1.2, label=f"İletim hattı ≥ 380 kV ({tr(hat[hat.gerilim_v >= 380000].length.sum() / 1000)} km)"),
     Line2D([], [], color="#a9a7a1", lw=0.8, label=f"İletim hattı 154–220 kV ({tr(hat[hat.gerilim_v < 380000].length.sum() / 1000)} km)")]
for k_, ad, renk, mk in KAY:
    h.append(Line2D([], [], marker=mk, color=renk, mec=YAZI, lw=0, ms=7 if mk == "o" else 11,
                    label=f"{ad} santrali ({say.get(k_, 0)})"))
h += [Line2D([], [], marker="o", color=SARI, lw=0, ms=3, alpha=0.7, label=f"Güneş paneli / tarlası kaydı ({tr(len(us))})"),
      Line2D([], [], marker="o", color=AQUA, lw=0, ms=3, label=f"Rüzgâr türbini ({tr(len(uw))})"),
      Line2D([], [], marker="o", color="white", mec=YAZI, lw=0, ms=4, label="Daire büyüklüğü: etiketli kurulu güç")]
lej(ax, h, loc="lower right", bbox=(1.0, 0.0), ncol=2)
basliklar(fig, "Enerji altyapısının dağılımı: iletim hatları ve üretim tesisleri (Ekim 2026)",
          "Daire alanı santralin OSM'de etiketli kurulu gücüyle orantılı; etiketsiz santraller küçük daire. OSM kaydı eksik: "
          "özellikle küçük HES ve lisanssız güneş tesisleri.",
          "Kaynak: © OpenStreetMap katkıcıları (Ekim 2026), ODbL · power=line/cable ≥ 154 kV, power=plant, power=generator · "
          "TEİAŞ'a göre iletim hattı devre uzunluğu 77.657 km (Eylül 2026) [D] · Projeksiyon: LCC (37°/41°)")
kaydet(fig, "02_enerji")

# ===================== 03 Nüfus ve sanayi ==================================================================
nuf, ext = oku("izgara_nufus.tif")
dens = np.where(nuf > 0, nuf / 0.0625, np.nan)
K4 = 4
h4_, w4_ = (nuf.shape[0] // K4) * K4, (nuf.shape[1] // K4) * K4
ext1 = [ext[0], ext[0] + w4_ * 250, ext[3] - h4_ * 250, ext[3]]
dens1 = nuf[:h4_, :w4_].reshape(h4_ // K4, K4, w4_ // K4, K4).sum(axis=(1, 3))  # kişi / km² (1 km hücre)
san = gpd.read_file(CIK / "sanayi_alanlari.gpkg").to_crs(LCC)
fig, ax = plt.subplots(figsize=(15, 8.6))
fig.subplots_adjust(left=0.01, right=0.99, top=0.885, bottom=0.035)
taban(ax, dolgu="#f6f5f2")
sinir = [5, 50, 300, 1500, 5000, 1e6]
cm = ListedColormap(["#e4effc", "#b4d2f6", "#6fa6ea", "#2f74c9", "#0f3f7d"])
ax.imshow(np.ma.masked_invalid(np.where(dens1 >= 5, dens1, np.nan)), extent=ext1, cmap=cm,
          norm=BoundaryNorm(sinir, cm.N), interpolation="nearest", zorder=1)
ust_cizgi(ax)
san.plot(ax=ax, color=TURUNCU, edgecolor=TURUNCU, linewidth=0.6, zorder=7, rasterized=True)
san[san.osb].plot(ax=ax, facecolor="none", edgecolor=YAZI, linewidth=0.5, zorder=8)
etiket_kent(ax, 700_000)
olcek(ax)
h = [Patch(facecolor=c, label=l) for c, l in zip(cm.colors, ["5–50", "50–300", "300–1.500", "1.500–5.000", "≥ 5.000"])]
h += [Patch(facecolor=TURUNCU, edgecolor=TURUNCU, label=f"Sanayi alanı, OSM landuse=industrial ({tr(san.area.sum() / 1e6)} km²)"),
      Patch(facecolor=TURUNCU, edgecolor=YAZI, label=f"…adında OSB geçen ({int(san.osb.sum())} poligon, {tr(san[san.osb].area.sum() / 1e6)} km²)")]
lej(ax, h, loc="lower right", baslik="Nüfus yoğunluğu (kişi/km², 1 km hücre, 2025)", bbox=(1.0, 0.0), ncol=2)
basliklar(fig, "Nüfus yoğunluğu ve sanayi alanları",
          "Sanayi alanları görünür olsun diye kenar çizgisiyle kalınlaştırıldı. 300 kişi/km² kentsel küme, 1.500 kişi/km² kent "
          "merkezi eşiğidir (DEGURBA, 1 km hücre). Erişim ve kademe hesapları 250 m hücrede yapıldı.",
          "Kaynak: nüfus: TÜİK ADNKS 2025 ilçe toplamları, 250 m hücrelere GHSL R2023A 2020 dağılımıyla (CC BY 4.0) [H] · © OpenStreetMap katkıcıları "
          "(Ekim 2026), ODbL · Projeksiyon: LCC (37°/41°)")
kaydet(fig, "03_nufus_sanayi")

# ===================== 04 Erişim ============================================================================
er = {}
with rasterio.open(CIK / "izgara_erisim.tif") as d:
    for i, ad in enumerate(["ist", "hiz", "hav", "lim", "san"], 1):
        a = d.read(i).astype("float32")
        a[a == 65535] = np.nan
        er[ad] = a / 10 if ad != "hav" else a  # bantlar km×10 (havalimanı: dakika)
yerlesik = dens >= 10
erisim_il = pd.read_csv(SON / "ulusal_plan_erisim_il.csv")
fig, axs = plt.subplots(2, 2, figsize=(16, 9.9))
fig.subplots_adjust(left=0.01, right=0.99, top=0.865, bottom=0.035, hspace=0.2, wspace=0.03)
PAN = [(axs[0, 0], "ist", "Yolcu demiryolu istasyonuna kuş uçuşu uzaklık", [0, 10, 30, 60, 1e9],
        ["≤ 10 km", "10–30 km", "30–60 km", "> 60 km"]),
       (axs[0, 1], "hav", "Yolcu havalimanına karayoluyla süre", [0, 60, 120, 180, 1e9],
        ["≤ 60 dk", "60–120 dk", "120–180 dk", "> 180 dk"]),
       (axs[1, 0], "lim", "Yük limanına kuş uçuşu uzaklık", [0, 50, 100, 200, 1e9],
        ["≤ 50 km", "50–100 km", "100–200 km", "> 200 km"])]
cm4 = ListedColormap(["#104281", "#3987e5", "#a9cdf5", TURUNCU])
s_tr = erisim_il[erisim_il.il == "Türkiye"].iloc[0]
for ax, k_, bas, sn, et in PAN:
    taban(ax, dolgu="#f6f5f2", il_cizgi=False)
    a = blok_nanmin(np.where(yerlesik, er[k_], np.nan), 4)  # 1 km gösterim: hücredeki yerleşik noktaların en iyisi
    ax.imshow(np.ma.masked_invalid(a), extent=ext1, cmap=cm4, norm=BoundaryNorm(sn, 4), interpolation="nearest", zorder=1)
    ust_cizgi(ax)
    ax.set_title(bas, loc="left", fontsize=11.5, fontweight="bold", color=YAZI, pad=17)
    alt = {"ist": f"Türkiye nüfusunun {yuzde(s_tr.ist_10km)} 10 km, {yuzde(s_tr.ist_30km)} 30 km içinde (2025)",
           "hav": f"Nüfusun {yuzde(s_tr.hav_60dk)} 60 dk, {yuzde(s_tr.hav_120dk)} 120 dk içinde",
           "lim": f"Nüfusun {yuzde(s_tr.liman_50km)} 50 km, {yuzde(s_tr.liman_100km)} 100 km içinde"}[k_]
    ax.text(0, 1.005, alt, transform=ax.transAxes, fontsize=8.5, color=YAZI2, va="bottom")
    lej(ax, [Patch(facecolor=c, label=l) for c, l in zip(cm4.colors, et)], loc="lower right", fs=7.5, ncol=2)
    if k_ == "ist":
        ax.scatter(ist.geometry.x, ist.geometry.y, s=1.5, color=YAZI, linewidths=0, zorder=8, rasterized=True)
    if k_ == "hav":
        ax.scatter(hav.geometry.x, hav.geometry.y, s=26, marker="^", color=TURUNCU, edgecolor=YAZI, lw=0.5, zorder=8)
    if k_ == "lim":
        yk = lim[lim.sinif != "enerji"]
        ax.scatter(yk.geometry.x, yk.geometry.y, s=20, marker="s", color=AQUA, edgecolor=YAZI, lw=0.5, zorder=8)
olcek(axs[1, 0], x0=-770_000, y0=-460_000, km=200)
ax = axs[1, 1]
g = il.merge(erisim_il, on="il", how="left")
g["acik"] = 100 - g.ist_30km
eksik = int(g.acik.isna().sum())
assert eksik == 0, f"erişim tablosunda eşleşmeyen il: {g[g.acik.isna()].il.tolist()}"
sn = [0, 10, 25, 50, 75, 100.01]
cm5 = ListedColormap(["#fde9d9", "#f9c39f", "#f39461", TURUNCU, "#a8411a"])
g.plot(ax=ax, column="acik", cmap=cm5, norm=BoundaryNorm(sn, 5), edgecolor="white", linewidth=0.4, zorder=1)
ulke.boundary.plot(ax=ax, color=SINIR_C, linewidth=0.6, zorder=6)
ax.set_xlim(*XL)
ax.set_ylim(*YL)
ax.set_aspect("equal")
ax.set_axis_off()
ax.set_title("İstasyona 30 km'den uzak oturan nüfus payı (il)", loc="left", fontsize=11.5, fontweight="bold", color=YAZI,
             pad=17)
n75 = int((g.acik >= 75).sum())
ax.text(0, 1.005, f"Demiryolu hizmetinin il içindeki dağılımı; {n75} ilde nüfusun %75'inden fazlası 30 km dışında",
        transform=ax.transAxes, fontsize=8.5, color=YAZI2, va="bottom")
lej(ax, [Patch(facecolor=c, label=l) for c, l in zip(cm5.colors, ["< %10", "%10–25", "%25–50", "%50–75", "≥ %75"])],
    loc="lower right", fs=7.5, ncol=2)
basliklar(fig, "Erişilebilirlik ve eşitsizlik: demiryolu, havalimanı, liman",
          "Renkli alanlar 10 kişi/km² ve üstü yerleşik hücreler (1 km gösterim). Havalimanı süresi 1 km ızgarada yol sınıfına göre hız "
          "varsayımıyla (otoyol 100, devlet yolu 80, il yolu 60, diğer 30 km/sa) hesaplandı [V].",
          "Kaynak: hesaplama [H] · nüfus: TÜİK ADNKS 2025 ilçe toplamları, 250 m hücrelere GHSL R2023A 2020 dağılımıyla · © OpenStreetMap katkıcıları (Ekim 2026) · istasyon: kent içi "
          "raylı hariç, OSM'de kayıtlı yolcu durakları (sefer sıklığı bilinmiyor; yapımdaki hatlar hariç) · "
          "Projeksiyon: LCC (37°/41°)", y=0.958)
kaydet(fig, "04_erisim")

# ===================== 05 Sanayi yakınlık ===================================================================
osb = pd.read_csv(SON / "ulusal_plan_sanayi_osb.csv")
san_il = pd.read_csv(SON / "ulusal_plan_sanayi_il.csv").set_index("il")
osb = osb[osb.ha >= 5]
fig = plt.figure(figsize=(16, 8.8))
ax = fig.add_axes([0.0, 0.05, 0.63, 0.80])
taban(ax)
v = osb.halka_tarim_pay.fillna(0)
sn = [0, 20, 40, 60, 101]
cmS = ListedColormap(["#fbf0d2", "#f6d98a", SARI, "#a77000"])
ax.scatter(osb.x, osb.y, s=np.clip(np.sqrt(osb.ha) * 2.2, 6, 160), c=v, cmap=cmS, norm=BoundaryNorm(sn, 4), edgecolor=YAZI,
           linewidth=0.5, zorder=8)
etiket_kent(ax, 1_000_000)
olcek(ax)
lej(ax, [Line2D([], [], marker="o", color=cc_, mec=YAZI, lw=0, ms=7, label=l) for cc_, l in
         zip(cmS.colors, ["< %20", "%20–40", "%40–60", "≥ %60"])] +
    [Line2D([], [], marker="o", color="white", mec=YAZI, lw=0, ms=4, label="küçük: 20 ha"),
     Line2D([], [], marker="o", color="white", mec=YAZI, lw=0, ms=11, label="büyük: 1.000 ha")],
    baslik="OSB çevresi (2 km halka): tarım arazisi payı", loc="lower right", ncol=2)
ax.text(0.01, 0.97, "Organize sanayi bölgeleri ve çevrelerindeki tarım arazisi", transform=ax.transAxes, fontsize=11.5,
        fontweight="bold", color=YAZI)
ax2 = fig.add_axes([0.675, 0.53, 0.305, 0.30])
t = san_il.drop(index="Türkiye").sort_values("nufus_1km_pay", ascending=False).head(12)[::-1]
ax2.barh(t.index, t.nufus_1km_pay, color=TURUNCU, height=0.62)
for y_, v_ in enumerate(t.nufus_1km_pay):
    ax2.text(v_ + 0.5, y_, f"%{tr(v_, 0)}", va="center", fontsize=7.5, color=YAZI2)
ax2.axvline(san_il.loc["Türkiye", "nufus_1km_pay"], color=YAZI, lw=0.8, ls=(0, (3, 2)))
ax2.text(san_il.loc["Türkiye", "nufus_1km_pay"] - 0.6, len(t) - 0.35, f"Türkiye %{tr(san_il.loc['Türkiye', 'nufus_1km_pay'], 0)}",
         fontsize=7.5, color=YAZI, ha="right", va="bottom")
ax2.set_title("Herhangi bir sanayi alanına 1 km içinde oturan nüfus\n(en yüksek 12 il)", loc="left", fontsize=10,
              fontweight="bold")
ax3 = fig.add_axes([0.675, 0.10, 0.305, 0.30])
pmv = pd.read_csv(SON / "ulusal_plan_sanayi_pm25.csv")
gruplar = pmv.grup.drop_duplicates().tolist()
x_ = np.arange(len(gruplar))
for j, (ol, renk) in enumerate([(pmv.olcu.unique()[0], TURUNCU), (pmv.olcu.unique()[1], MAVI)]):
    s = pmv[pmv.olcu == ol].set_index("grup").reindex(gruplar)
    xx = x_ + (j - 0.5) * 0.36
    ax3.bar(xx, s.il_ici_fark, width=0.34, color=renk, label="her sanayi alanı" if j == 0 else "yalnız OSB")
    for xi, vv in zip(xx, s.il_ici_fark):
        ax3.text(xi, vv + (0.06 if vv >= 0 else -0.22), f"{'+' if vv >= 0 else '−'}{tr(abs(vv), 1)}", ha="center",
                 fontsize=7.5, color=YAZI)
ax3.axhline(0, color=YAZI2, lw=0.8)
ax3.set_xticks(x_, [g_.replace(" (", "\n(") for g_ in gruplar], fontsize=7.5)
ax3.set_ylabel("µg/m³ (≤ 3 km eksi > 3 km)", color=YAZI2, fontsize=8)
ax3.legend(frameon=False, fontsize=7.5, loc="upper left")
ax3.set_title("Sanayiye 3 km içinde oturanların PM2.5 farkı\n(aynı il ve aynı yoğunluk sınıfı içinde, 2022–2024)",
              loc="left", fontsize=10, fontweight="bold")
for a_ in (ax2, ax3):
    for s_ in ("top", "right"):
        a_.spines[s_].set_visible(False)
    a_.tick_params(labelsize=8, colors=YAZI2)
ax2.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"%{v:g}"))
ax3.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
ax3.grid(axis="y", color="#e4e2dd", lw=0.6)
ax3.set_axisbelow(True)
basliklar(fig, "Sanayi alanları yerleşime ve tarım arazisine ne kadar yakın?",
          "Sol: adında OSB geçen OSM sanayi poligonları; renk 2 km çevredeki WorldCover tarım payı. Sağ alt: il ve yoğunluk "
          "sınıfı içinde karşılaştırma (aynı il, aynı kentsellik).",
          "Kaynak: © OpenStreetMap katkıcıları (Ekim 2026) · ESA WorldCover 2021 · ACAG V6.GL.03 PM2.5 2022–2024 · nüfus TÜİK 2025 + GHSL 2020 dağılımı "
          "· hesaplama [H] · Projeksiyon: LCC (37°/41°)")
kaydet(fig, "05_sanayi_yakinlik")

# ===================== 06 Kısıt ================================================================================
kis, ext = oku("izgara_kisit.tif")
B = {ad: (kis >> i) & 1 == 1 for i, ad in enumerate(
    ["fay_1km", "fay_5km", "ova_tarim", "tarim", "sulak", "su", "kiyi_500m", "orman", "taskin", "korunan", "dik"])}
oz = pd.read_csv(SON / "ulusal_plan_kisit_ozet.csv").set_index("katman")
KAT = [("dik", "#d3d1cb", "Eğim > %20"), ("tarim", "#f8e7b8", "Diğer tarım arazisi"),
       ("ova_tarim", SARI, "Ova tarım arazisi (eğim < %5)"), ("orman", AQUA, "Orman / ağaçlık (≥ %50 ağaç)"),
       ("taskin", "#86b6ef", "Taşkın alanı (100 yıllık)"), ("sulak", "#104281", "Sulak alan"),
       ("kiyi_500m", "#3987e5", "Kıyı bandı (500 m)"), ("fay_1km", TURUNCU, "Diri fay ±1 km")]
kod = np.zeros(kis.shape, dtype="uint8")
for i, (k_, _, _) in enumerate(KAT, 1):
    kod[B[k_]] = i
kod[B["su"]] = 0
fig, ax = plt.subplots(figsize=(15, 8.6))
fig.subplots_adjust(left=0.01, right=0.99, top=0.885, bottom=0.035)
taban(ax, dolgu="white", il_cizgi=False)
cmK = ListedColormap([c for _, c, _ in KAT])
ax.imshow(np.ma.masked_equal(kod, 0), extent=ext, cmap=cmK, norm=BoundaryNorm(np.arange(0.5, len(KAT) + 1), len(KAT)),
          interpolation="nearest", zorder=1)
kor = gpd.clip(gpd.read_file(CIK / "korunan_alanlar.gpkg").to_crs(LCC), ulke)
kor.plot(ax=ax, facecolor="none", edgecolor=YAZI, linewidth=0.35, hatch="////", zorder=4, rasterized=True)
fay.plot(ax=ax, color="#7a2f0c", linewidth=0.5, zorder=5)
ust_cizgi(ax)
etiket_kent(ax, 1_000_000)
olcek(ax)


def pay(k_):
    return f"%{tr(oz.loc[k_, 'alan_pay'], 0)}"


h = [Patch(facecolor=c, label=f"{l} · {pay(k_)}") for k_, c, l in KAT[::-1]]
h += [Patch(facecolor="none", edgecolor=YAZI, hatch="////", label=f"Korunan alan (OSM, eksik) · {pay('korunan')}"),
      Line2D([], [], color="#7a2f0c", lw=0.8, label="Diri fay izi (GEM/EMME 2014)"),
      Patch(facecolor="white", edgecolor="#bbb", label=f"Kısıtsız ve eğim ≤ %15 · {pay('elverişli (kısıtsız, eğim ≤ %15)')}")]
lej(ax, h, loc="lower right", baslik="Kısıt (katmanlar üst üste; % = kara alanının payı)", bbox=(1.0, 0.0), ncol=2)
basliklar(fig, "Kısıt haritası: diri fay, nitelikli tarım, su ve kıyı, orman, taşkın",
          "Katmanlar çakıştığında lejantta üstte olan görünür. Eşikler ulusal tarama içindir; parsel kararı için ayrıntılı "
          "etüt gerekir [V]. Faylar ve korunan alanlar kara sınırına kırpıldı.",
          "Kaynak: GEM Global Active Faults (EMME 2014 izleri), CC BY-SA 4.0 [İ] · ESA WorldCover 2021, CC BY 4.0 · Copernicus "
          "DEM GLO-90 · JRC CEMS-GloFAS taşkın tehlikesi v2.1.2 (100 yıl) · © OpenStreetMap (kıyı, sulak, korunan) · "
          "Projeksiyon: LCC (37°/41°)")
kaydet(fig, "06_kisit")

# ===================== 07 İlke haritası ==========================================================================
kor_s = gpd.read_file(CIK / "sema_koridorlar.gpkg").to_crs(LCC)
rz = pd.read_csv(SON / "ulusal_plan_ruzgar_il.csv")
with rasterio.open(CIK / "izgara_sema.tif") as d:
    bant, ilke = d.read(1), d.read(2)
    tS = d.transform
K = 4
ext4 = [tS.c, tS.c + (bant.shape[1] // K) * K * tS.a, tS.f + (bant.shape[0] // K) * K * tS.e, tS.f]
bant4 = blok_max(ndimage.binary_dilation(bant > 0, iterations=10).astype("uint8"), K)  # ≈ 2,5 km genişletme
ilke4 = blok_max(ilke, K)
h4, w4 = (B["ova_tarim"].shape[0] // K) * K, (B["ova_tarim"].shape[1] // K) * K
ova4 = (B["ova_tarim"][:h4, :w4].reshape(h4 // K, K, w4 // K, K).mean(axis=(1, 3)) >= 0.5).astype("uint8")  # alan payı korunur
fig, ax = plt.subplots(figsize=(16, 9.6))
fig.subplots_adjust(left=0.01, right=0.99, top=0.885, bottom=0.035)
taban(ax, dolgu="#f4f3ef")
ax.imshow(np.ma.masked_equal(ova4, 0), extent=ext4, cmap=ListedColormap(["#f6e2a6"]), interpolation="nearest", zorder=1)
ust_cizgi(ax)
fay.plot(ax=ax, color="#c9a48f", linewidth=0.45, zorder=2)
ax.imshow(np.ma.masked_equal(bant4, 0), extent=ext4, cmap=ListedColormap([AQUA]), alpha=0.8, interpolation="nearest",
          zorder=5)
ax.imshow(np.ma.masked_equal(ilke4, 0), extent=ext4, cmap=ListedColormap(["#f5ad86", TURUNCU]),
          norm=BoundaryNorm([0.5, 1.5, 2.5], 2), interpolation="nearest", zorder=4)
STIL = {"hizli": dict(color=MAVI, lw=3.0, ls="-"), "konvansiyonel": dict(color=MAVI, lw=1.5, ls=(0, (1, 1.2))),
        "yapim": dict(color=MAVI, lw=2.6, ls=(0, (3, 1.6))), "planli": dict(color=MAVI, lw=2.6, ls=(0, (3, 1.6))),
        "yeni": dict(color=YAZI2, lw=2.0, ls=(0, (3, 1.6)))}
for d_, st in STIL.items():
    s = kor_s[kor_s.durum == d_]
    if len(s):
        s.plot(ax=ax, color=st["color"], linewidth=st["lw"], linestyle=st["ls"], zorder=6)
yk = lim[lim.sinif != "enerji"]
ax.scatter(yk.geometry.x, yk.geometry.y, s=np.where(yk.sinif == "ana", 46, 20), marker="s",
           color=np.where(yk.demiryolu_bagli, YAZI, "white"), edgecolor=YAZI, linewidth=0.8, zorder=10)
kk = kentler[kentler.kademe.isin(["K1", "K2", "K3"])]
BOY = {"K1": 230, "K2": 90, "K3": 18}
for kd in ["K3", "K2", "K1"]:
    s = kk[kk.kademe == kd]
    ax.scatter(s.x, s.y, s=BOY[kd], color=YAZI2 if kd != "K1" else YAZI, edgecolor="white", linewidth=0.9, zorder=11)
for r in kk[kk.kademe == "K1"].itertuples():
    ax.text(r.x + 14000, r.y + 12000, r.ad.split("–")[0], fontsize=8.2, fontweight="bold", color=YAZI, zorder=13,
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=0.4))
KAYDIR = {"Çorlu": (9000, -30000), "Osmaniye": (10000, -18000), "İskenderun": (10000, -14000)}
for r in kk[kk.kademe == "K2"].itertuples():
    dx, dy = KAYDIR.get(r.ad.split("–")[0], (10000, 8000))
    ax.text(r.x + dx, r.y + dy, r.ad.split("–")[0], fontsize=6.8, color=YAZI2, zorder=13,
            ha="right" if dx < 0 else "left")
# hâkim rüzgârın gittiği yan (K1–K2): sanayi bu yanda yer alır
YON = {"K": 0, "KD": 45, "D": 90, "GD": 135, "G": 180, "GB": 225, "B": 270, "KB": 315}
rzi = rz.set_index("il")
for r in kk[kk.kademe.isin(["K1", "K2"])].itertuples():
    if r.il not in rzi.index:
        continue
    a = np.radians(YON[rzi.loc[r.il, "hakim_yon_gelen"]] + 180)
    ax.add_patch(FancyArrowPatch((r.x + 9000 * np.sin(a), r.y + 9000 * np.cos(a)),
                                 (r.x + 42000 * np.sin(a), r.y + 42000 * np.cos(a)),
                                 arrowstyle="-|>", mutation_scale=9, color="#6f6e6a", lw=1.1, zorder=12))
olcek(ax)
kad = pd.read_csv(SON / "ulusal_plan_kademe.csv").set_index("kademe")
h = [Line2D([], [], color=MAVI, lw=3, label="Hızlı tren omurgası (mevcut)"),
     Line2D([], [], color=MAVI, lw=2.6, ls=(0, (3, 1.6)), label="Hızlı tren / demiryolu (yapımda, planlı)"),
     Line2D([], [], color=MAVI, lw=1.5, ls=(0, (1, 1.2)), label="Konvansiyonel hat: yük + hızlı yolcu için iyileştirme"),
     Line2D([], [], color=YAZI2, lw=2.0, ls=(0, (3, 1.6)), label="Koridorda eksik bağlantı (şematik)"),
     Patch(facecolor=AQUA, alpha=0.8, label="Uydu kent bandı: hatta merkeze 20–70 km"),
     Patch(facecolor=TURUNCU, label="Sanayi ilke alanı, limana ≤ 50 km"),
     Patch(facecolor="#f5ad86", label="Sanayi ilke alanı, iç bölge"),
     Line2D([], [], marker="o", color=YAZI, mec="white", lw=0, ms=12, label=f"K1 metropol, ≥ 1 milyon ({int(kad.loc['K1', 'kume'])})"),
     Line2D([], [], marker="o", color=YAZI2, mec="white", lw=0, ms=8, label=f"K2 bölge kenti, 250 bin–1 milyon ({int(kad.loc['K2', 'kume'])})"),
     Line2D([], [], marker="o", color=YAZI2, mec="white", lw=0, ms=4, label=f"K3 orta kent, 50–250 bin ({int(kad.loc['K3', 'kume'])})"),
     Line2D([], [], marker="s", color=YAZI, lw=0, ms=6, label="Yük limanı (boş kare: demiryolu yok)"),
     Patch(facecolor="#f6e2a6", label="Ova tarım arazisi: yapılaşma dışı"),
     Line2D([], [], color="#c9a48f", lw=1, label="Diri fay izi: 1 km yerleşim, 5 km ağır sanayi dışı"),
     Line2D([], [], color="#6f6e6a", marker=">", lw=1, ms=4, label="Hâkim rüzgârın gittiği yan: sanayi bu yanda")]
lej(ax, h, loc="lower right", bbox=(1.0, 0.0), fs=7.2, ncol=2)
basliklar(fig, "İlke haritası: koridorlar, kademeli yerleşim, uydu kent bandı ve sanayi ilke alanı",
          "Yer seçimi değildir. Renkli bant ve alanlar ilkelerin birlikte sağlandığı yerleri gösterir; somut proje jeoloji, toprak "
          "sınıfı, su, mülkiyet ve katılım süreciyle ayrıca sınanır. Bölge ölçeğindeki karşılığı: 08_ilke_semasi.",
          "Kaynak: hesaplama [H] · nüfus kümeleri (TÜİK 2025, GHSL 2020 dağılımı) · © OpenStreetMap demiryolu (mevcut, yapımda, planlı) · GEM diri "
          "faylar [İ] · ESA WorldCover 2021 · Copernicus DEM · JRC taşkın · ERA5 (Open-Meteo) rüzgâr 2023–2024 · "
          "Projeksiyon: LCC (37°/41°)", y=0.958)
kaydet(fig, "07_sema")

# ===================== 08 İlke şeması (kavramsal) =================================================================
osb_oz = pd.read_csv(SON / "ulusal_plan_sanayi_osb_ilke_ozet.csv", index_col=0)
KONUT, KONUT_K, YESIL, TARIM, OVA, DENIZ = "#cde2fb", MAVI, "#c3e5d2", "#f3efe4", "#ecdcaa", "#dcebf8"
fig = plt.figure(figsize=(16, 9.4))
ax = fig.add_axes([0.015, 0.085, 0.585, 0.79])
ax.set_xlim(0, 130)
ax.set_ylim(0, 90)
ax.set_aspect("equal")
ax.axis("off")
ax.add_patch(Rectangle((0, 0), 130, 90, facecolor=TARIM, edgecolor="none", zorder=0))
ax.add_patch(Polygon([(0, 0), (130, 0), (130, 5), (95, 6.5), (60, 5.5), (30, 7.5), (0, 6)], facecolor=DENIZ,
                     edgecolor="#9fc2e8", lw=0.8, zorder=1))
ax.text(4, 2.2, "deniz", fontsize=8, color=MAVI, style="italic", zorder=2)
ax.add_patch(Ellipse((28, 68), 46, 26, angle=-8, facecolor=OVA, edgecolor="#c9b27a", lw=0.8, zorder=1))
ax.text(28, 70, "ova tarım arazisi\nyapılaşma yok", ha="center", fontsize=8, color="#7a6420", zorder=2)
ax.add_patch(Polygon([(90, 90), (130, 90), (130, 60), (114, 66), (100, 76)], facecolor=YESIL, edgecolor="none", zorder=1))
ax.add_patch(Polygon([(108, 8), (130, 7), (130, 40), (118, 34), (110, 20)], facecolor=YESIL, edgecolor="none", zorder=1))
ax.text(118, 82, "orman ve\ndağlık alan", ha="center", fontsize=8, color="#13764f", zorder=2)
# diri fay ve bantları
fx, fy = np.array([72, 130]), np.array([90, 55])
nv = np.array([35, 58]) / np.hypot(35, 58)
for gen, alfa in [(5, 0.10), (1, 0.28)]:
    ax.add_patch(Polygon([(fx[0] - gen * nv[0], fy[0] - gen * nv[1]), (fx[1] - gen * nv[0], fy[1] - gen * nv[1]),
                          (fx[1] + gen * nv[0], fy[1] + gen * nv[1]), (fx[0] + gen * nv[0], fy[0] + gen * nv[1])],
                         facecolor="#b22222", alpha=alfa, edgecolor="none", zorder=2))
ax.plot(fx, fy, color="#b22222", lw=1.4, ls=(0, (5, 3)), zorder=3)
ax.text(104, 77.5, "diri fay: 1 km yerleşim yok,\n5 km ağır sanayi yok", fontsize=7.4, color="#8b1a1a", rotation=-31,
        ha="center", zorder=3)
# bölge merkezi, yeşil kuşak, uydu kentler
C = np.array([62, 46])
ax.add_patch(Circle(C, 20, facecolor="none", edgecolor=YAZI2, lw=0.8, ls=(0, (4, 3)), zorder=3))
ax.add_patch(Circle(C, 40, facecolor="none", edgecolor=YAZI2, lw=0.8, ls=(0, (4, 3)), zorder=3))
ax.text(C[0] + 14.5, C[1] + 15.5, "20 km", fontsize=7, color=YAZI2, zorder=3)
ax.text(C[0] - 39.5, C[1] + 9, "40 km", fontsize=7, color=YAZI2, zorder=3, rotation=80)
ax.add_patch(Circle(C, 10.5, facecolor="none", edgecolor=YESIL, lw=7, zorder=3))
ax.add_patch(Circle(C, 8, facecolor=KONUT, edgecolor=KONUT_K, lw=1, zorder=4))
ax.add_patch(Circle(C, 2.6, facecolor=TURUNCU, edgecolor="none", zorder=6))
UY = [np.array(p) for p in [(30, 47), (86, 63), (92, 31), (64, 78)]]
for p in UY:
    ax.add_patch(Circle(p, 3.6, facecolor=KONUT, edgecolor=KONUT_K, lw=1, zorder=4))
    ax.add_patch(Circle(p, 1.1, facecolor=TURUNCU, edgecolor="none", zorder=6))
# raylı sistem: hızlı tren (merkez istasyona), bölgesel tren (uydu kentlere), yük hattı (kent dışından)
ax.plot([0, C[0], 130], [42, C[1], 49], color=YAZI, lw=3.4, zorder=7, solid_capstyle="butt")
ax.plot([0, C[0], 130], [42, C[1], 49], color="white", lw=1.0, ls=(0, (4, 4)), zorder=7)
for p in UY:
    ax.plot([C[0], p[0]], [C[1], p[1]], color=YAZI, lw=1.6, zorder=6)
    ax.scatter(*p, s=26, color="white", edgecolor=YAZI, lw=1, zorder=8)
ax.scatter(*C, s=60, color="white", edgecolor=YAZI, lw=1.3, zorder=8)
yuk = np.array([(0, 29), (30, 26), (40, 24), (62, 26), (98, 25), (130, 23)])
ax.plot(yuk[:, 0], yuk[:, 1], color=YAZI, lw=1.8, ls=(0, (3, 2)), zorder=6)
ax.plot([24, 30, 36], [7.5, 15, 22], color=YAZI, lw=1.8, ls=(0, (3, 2)), zorder=6)
# otoyol ve iletim hattı: aynı koridorda, kentin dışından; kente yalnız bağlantı kolu
oto = np.array([(0, 33), (35, 31.5), (62, 31), (100, 31.5), (130, 32)])
ax.plot(oto[:, 0], oto[:, 1], color="#8a8985", lw=4.2, zorder=5, solid_capstyle="butt")
ax.plot(oto[:, 0], oto[:, 1], color="white", lw=0.8, zorder=5)
ax.plot([62, 62], [31, 37.8], color="#8a8985", lw=2.2, zorder=5)
ax.plot([30, 30], [32, 43.4], color="#8a8985", lw=1.6, zorder=5)
ax.plot([92, 92], [31.4, 27.4], color="#8a8985", lw=1.6, zorder=5)
ilt = np.array([(0, 36), (35, 34.6), (62, 34.2), (100, 34.6), (130, 35)])
ax.plot(ilt[:, 0], ilt[:, 1], color="#3d3c39", lw=0.9, ls=(0, (6, 1.5, 1, 1.5)), zorder=5)
# sanayi, lojistik, liman, havalimanı
ax.add_patch(Rectangle((32, 18.5), 10, 6.5, facecolor=SARI, edgecolor="#8a6000", lw=0.8, zorder=7))
ax.text(37, 21.7, "OSB", ha="center", va="center", fontsize=8, fontweight="bold", color=YAZI, zorder=8)
ax.add_patch(Rectangle((58, 22.4), 8, 3.2, facecolor=SARI, edgecolor="#8a6000", lw=0.8, zorder=7))
ax.text(62, 21.0, "lojistik merkezi", ha="center", va="top", fontsize=7, color=YAZI2, zorder=8)
ax.add_patch(Rectangle((19, 5.5), 9, 4, facecolor=SARI, edgecolor="#8a6000", lw=0.8, zorder=7))
ax.text(23.5, 10.4, "liman", ha="center", fontsize=7.5, color=YAZI, zorder=8)
ax.add_patch(Rectangle((84, 12.5), 9, 5, facecolor=SARI, edgecolor="#8a6000", lw=0.8, zorder=7))
ax.text(88.5, 11.5, "havalimanı (≤ 60 dk)", ha="center", va="top", fontsize=7, color=YAZI2, zorder=8)
ax.plot([88.5, 92, 92], [17.5, 24, 31], color=YAZI, lw=1.2, zorder=6)
ax.add_patch(Rectangle((37, 26.5), 16, 3.0, facecolor=YESIL, edgecolor="none", zorder=6))
ax.text(45, 28.0, "yeşil tampon", ha="center", va="center", fontsize=6.4, color="#13764f", zorder=7)
# enerji: çatı GES (her yerleşimde), arazi güneşi ve rüzgâr marjinal arazide, semt bataryası
rng = np.random.default_rng(3)
for p, rr in [(C, 6.5)] + [(p, 2.8) for p in UY]:
    for _ in range(9 if rr > 5 else 3):
        a_, d_ = rng.uniform(0, 2 * np.pi), rng.uniform(0.35, 0.9) * rr
        ax.add_patch(Rectangle((p[0] + d_ * np.cos(a_) - 0.45, p[1] + d_ * np.sin(a_) - 0.3), 0.9, 0.6, facecolor=AQUA,
                               edgecolor="none", zorder=6))
for p in [C + (5.5, -4.5)] + [p + (2.6, -2.2) for p in UY]:
    ax.scatter(*p, s=24, marker="D", color=AQUA, edgecolor=YAZI, lw=0.6, zorder=8)
ax.add_patch(Rectangle((44, 10.5), 10, 5, facecolor=AQUA, edgecolor="#13764f", lw=0.6, zorder=6, hatch="////"))
ax.text(49, 9.6, "güneş sahası (ova dışı)", ha="center", va="top", fontsize=7, color="#13764f", zorder=8)
for xw, yw in [(114, 22), (119, 27), (123, 19), (117, 14)]:
    ax.plot([xw, xw], [yw - 2.6, yw], color="#13764f", lw=1, zorder=6)
    for aa in (90, 210, 330):
        ax.plot([xw, xw + 1.5 * np.cos(np.radians(aa))], [yw, yw + 1.5 * np.sin(np.radians(aa))], color="#13764f", lw=1,
                zorder=6)
ax.text(119, 11, "rüzgâr (tepelerde)", ha="center", va="top", fontsize=7, color="#13764f", zorder=8)
# hâkim rüzgâr: kentten OSB'ye doğru (OSB rüzgârın alt yönünde)
OK_STIL = "simple,tail_width=0.45,head_width=1.3,head_length=1.1"
ax.add_patch(FancyArrowPatch((126, 46), (110, 37.5), arrowstyle=OK_STIL, mutation_scale=16, color="#8a8985", alpha=0.95,
                             zorder=9))
ax.text(108.5, 39.5, "hâkim rüzgâr", fontsize=7.8, color=YAZI2, ha="right", va="center", zorder=9)
ax.add_patch(FancyArrowPatch((53, 37), (44.5, 28.2), arrowstyle=OK_STIL, mutation_scale=11, color="#8a8985", alpha=0.9,
                             zorder=9))
ax.text(50.5, 32.6, "rüzgâr altı", fontsize=6.8, color=YAZI2, ha="left", zorder=9)
# etiketler
ax.text(C[0] + 3.5, C[1] + 9.3, "bölge merkezi (K1–K2)\nyeşil kuşak", fontsize=7.6, color=YAZI, zorder=9)
ax.text(30, 51.2, "uydu kent", ha="center", fontsize=7.4, color=YAZI, zorder=9)
ax.text(64, 82.3, "uydu kent", ha="center", fontsize=7.4, color=YAZI, zorder=9)
ax.text(86, 67.3, "uydu kent", ha="center", fontsize=7.4, color=YAZI, zorder=9)
ax.text(96.5, 33.5, "uydu kent", ha="left", fontsize=7.4, color=YAZI, zorder=9)
ax.text(2, 44, "hızlı tren", fontsize=7.4, color=YAZI, zorder=9)
ax.text(2, 26.2, "yük demiryolu", fontsize=7.4, color=YAZI, zorder=9)
ax.text(2, 30.0, "otoyol", fontsize=7.4, color="#6f6e6a", zorder=9)
ax.text(2, 37.0, "380 kV", fontsize=7.0, color="#3d3c39", zorder=9)
ax.plot([4, 24], [86, 86], color=YAZI, lw=2)
ax.text(14, 87, "20 km", ha="center", fontsize=7.5, color=YAZI)
ax.text(0, 92.5, "A · Bölge birimi: ilkeler bir arada (≈ 1–3 milyon kişi)", fontsize=12, fontweight="bold", color=YAZI)
# sağ: ilke kartları
P = osb_oz.osb_sayisi_pay
KART = [
    ("Sanayi", SARI, [
        "Yük demiryoluna ≤ 5 km; liman ya da lojistik merkezine bağlı",
        "Kente ≥ 3 km; rüzgârın OSB'den kente estiği saat ≤ %10",
        "Ova tarım ve 1 km fay bandı dışı; ağır sanayi 5 km dışı",
        f"Bugün OSB'lerin (≥ 20 ha) {yuzde(P['p_hepsi'])} bunların hepsini sağlıyor"]),
    ("Yerleşim", MAVI, [
        "Kademe: mahalle → semt → şehir → bölge (kademe şeması)",
        "Uydu kent: mevcut kasaba, hatta merkeze 20–70 km (30–45 dk)",
        "Ova, fay bandı ve kıyı bandı dışında; her kent yeşil kuşaklı",
        "Metropolün karşısında: hızlı tren durağı olan bölge kentleri"]),
    ("Enerji", AQUA, [
        "Üretim tüketimin yanında: çatı GES, semt bataryası",
        "Arazi güneşi ve rüzgâr ova dışı marjinal arazide, OSB yanında",
        "İletim hattı ulaşım koridorunda; ormandan ve fay bandından uzak",
        "Ekonomisi ayrı raporda (Rapor 18)"]),
    ("Ulaşım", YAZI2, [
        "Yük treni kent merkezine girmez: OSB–liman–lojistik hattı",
        "Hızlı tren merkez istasyona; bölgesel tren uydu kentlere",
        "Otoyol kentin dışından; kente yalnız bağlantı kolu",
        "Havalimanı ≤ 60 dk, raylı bağlantılı"])]
y0 = 0.865
for bas, renk, mad in KART:
    fig.add_artist(FancyBboxPatch((0.625, y0 - 0.185), 0.36, 0.175, boxstyle="round,pad=0.004,rounding_size=0.006",
                                      transform=fig.transFigure, facecolor="white", edgecolor="#dcdad4", lw=0.8))
    fig.add_artist(Rectangle((0.627, y0 - 0.183), 0.005, 0.171, transform=fig.transFigure, facecolor=renk,
                                 edgecolor="none"))
    fig.text(0.642, y0 - 0.032, bas, fontsize=11.5, fontweight="bold", color=YAZI)
    for j, m in enumerate(mad):
        fig.text(0.642, y0 - 0.064 - j * 0.03, "• " + m, fontsize=8.6, color=YAZI2 if j < 3 else YAZI,
                 style="italic" if j == 3 else "normal")
    y0 -= 0.195
fig.text(0.625, 0.885, "B · Dört ilke ailesi", fontsize=12, fontweight="bold", color=YAZI)
leg = [Patch(facecolor=KONUT, edgecolor=KONUT_K, label="Konut ağırlıklı doku"),
       Patch(facecolor=TURUNCU, label="Merkez"),
       Patch(facecolor=SARI, edgecolor="#8a6000", label="Sanayi, lojistik, liman, havalimanı"),
       Patch(facecolor=AQUA, label="Yenilenebilir enerji (çatı, saha), ◆ semt bataryası"),
       Patch(facecolor=YESIL, label="Yeşil kuşak, orman"),
       Patch(facecolor=OVA, edgecolor="#c9b27a", label="Ova tarım arazisi"),
       Line2D([], [], color=YAZI, lw=3.2, label="Hızlı tren"),
       Line2D([], [], color=YAZI, lw=1.6, label="Bölgesel tren"),
       Line2D([], [], color=YAZI, lw=1.8, ls=(0, (3, 2)), label="Yük demiryolu"),
       Line2D([], [], color="#8a8985", lw=4, label="Otoyol"),
       Line2D([], [], color="#3d3c39", lw=0.9, ls=(0, (6, 1.5, 1, 1.5)), label="İletim hattı"),
       Line2D([], [], color="#b22222", lw=1.4, ls=(0, (5, 3)), label="Diri fay ve bantları")]
fig.legend(handles=leg, loc="lower left", bbox_to_anchor=(0.015, 0.025), ncol=6, frameon=False, fontsize=8,
           handlelength=2.2, columnspacing=1.4)
basliklar(fig, "İlke şeması: sanayi, yerleşim, enerji ve ulaşım bir bölgede nasıl bir araya gelir?",
          "Kavramsal şemadır, gerçek bir yer değildir. Kademe şemasının (07_TASARIM_CIZIM/olceklenebilir_sehir) bölge "
          "kademesini ulusal altyapı ilkeleriyle tamamlar. Ölçek yaklaşıktır.",
          "Kaynak: bu raporun ilkeleri [V]; OSB uyum payı hesaplama [H] (OSM 2026, GEM fay, WorldCover 2021, ERA5 rüzgâr)",
          y=0.958)
kaydet(fig, "08_ilke_semasi")
