"""
FUE grafikleri (Faz 3)
=====================
Girdi : 05_ANALIZ/sonuclar/fue_mahalle.csv, fue_ilce_ozet.csv (fue_mahalle.py)
        05_ANALIZ/sonuclar/fue_ilce_gecerlilik.csv, fue_ilce_yukseklik_yeniden.csv (fue_ilce_gecerlilik.py)
Çıktı : 05_ANALIZ/grafikler/fue_gecerlilik_ilce.png|svg     E ve Ç alt endekslerinin sonuçlarla il içi ilişkisi
        05_ANALIZ/grafikler/fue_yukseklik_yeniden.png|svg   Faz 2 yükseklik–ölümlülük katsayısı, kentsellik kontrolleriyle
        05_ANALIZ/grafikler/fue_erisim_cevre_odunlesim.png|svg   mahalle E–Ç dağılımı, ilçe başına küçük çoklu
        05_ANALIZ/grafikler/fue_ilce_profili.png|svg        ilçe × boyut ısı tablosu
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

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
SON = KOK / "05_ANALIZ" / "sonuclar"
GRAF = KOK / "05_ANALIZ" / "grafikler"
MAVI, TURUNCU, GRI_N = "#2a78d6", "#eb6834", "#c9c8c3"
YAZI, YAZI_2, YAZI_3, ZEMIN, IZGARA = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e8e7e3"
MAVI_R = ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "axes.edgecolor": YAZI_3, "axes.labelcolor": YAZI_2, "xtick.color": YAZI_2, "ytick.color": YAZI_2})


def tr(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def kaydet(fig, ad):
    for uz in ("png", "svg"):
        fig.savefig(GRAF / f"{ad}.{uz}", dpi=200)
    plt.close(fig)


def sade_eksen(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)


# --- 1. ulusal geçerlilik: E ve Ç ---------------------------------------------------------------------------------
T = pd.read_csv(SON / "fue_ilce_gecerlilik.csv")
T["yildiz"] = T.yildiz.fillna("")
SONUC = [("smr", "Standartlaştırılmış ölüm oranı"), ("tdh_ilce", "Toplam doğurganlık hızı"),
         ("tek_kisi_pay", "Tek kişilik hane payı"), ("k2534_bekar_pay", "25–34 yaş kadında hiç evlenmemiş payı"),
         ("genis_aile_pay", "Geniş aile hanesi payı"), ("bosanma_hiz", "Boşanma hızı")]
MODELLER = [("il SE + eğitim + göç", "Temel model\nil sabit etkisi + kadın eğitimi + nüfus artışı"),
            ("+ kentsellik ve yaş yapısı", "Geniş model\n+ ln yoğunluk + kent merkezi payı + 65+ payı")]
fig, axs = plt.subplots(1, 2, figsize=(13.5, 6.0), sharey=True)
for ax, (mk, mad) in zip(axs, MODELLER):
    for i, (y, yad) in enumerate(SONUC):
        for dy, (e, renk, ad) in zip((-0.17, 0.17), (("E_lite", MAVI, "Erişim (E)"), ("C_lite", TURUNCU, "Çevre-ölçek (Ç)"))):
            r = T[(T.sonuc == y) & (T.endeks == e) & (T.model == mk)].iloc[0]
            yy = i + dy
            ax.plot([r.beta - 1.96 * r.sh, r.beta + 1.96 * r.sh], [yy, yy], color=renk, lw=2, solid_capstyle="round")
            ax.plot(r.beta, yy, "o", ms=8, color=renk, mec=ZEMIN, mew=2)
            ax.text(r.beta + 1.96 * r.sh + 0.015, yy, f"{tr(r.beta, 2)}{r.yildiz}", va="center", fontsize=7.5, color=YAZI_2)
    ax.axvline(0, color=YAZI_3, lw=1)
    ax.set_yticks(range(len(SONUC)), [s[1] for s in SONUC])
    ax.invert_yaxis()
    ax.set_xlim(-0.55, 0.75)
    ax.grid(axis="x", color=IZGARA, lw=0.8)
    ax.set_axisbelow(True)
    sade_eksen(ax)
    ax.set_title(mad, loc="left", fontsize=9.5, color=YAZI, fontweight="bold")
    ax.set_xlabel("Standartlaştırılmış katsayı (β, %95 güven aralığı)")
leg = [Line2D([], [], color=MAVI, marker="o", ms=8, lw=2, label="Erişim (E): 15 dk temel ihtiyaç, okul, cami, durak, dükkân, kavşak"),
       Line2D([], [], color=TURUNCU, marker="o", ms=8, lw=2, label="Çevre-ölçek (Ç): yeşil alan, az kat, ana yoldan uzaklık, yayılmama")]
fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.01, 0.93), ncol=2, frameon=False, fontsize=8.5)
fig.suptitle("Çevre-ölçek düşük ölümlülükle, erişim yüksek ölümlülükle ilişkili (973 ilçe, il içi)", x=0.01, ha="left",
             fontsize=13, fontweight="bold", color=YAZI)
fig.text(0.01, 0.005, "Her iki endeks 0–100 yüzdelik puanların ortalaması, modelde z-puanı. Nüfus ağırlıklı WLS, il düzeyinde kümelenmiş SH. "
         "*** p<0,001 ** p<0,01 * p<0,05 † p<0,10. Sağdaki pozitif değer sonucu artırır (ölümlülükte kötü yön).\n"
         "Kaynak: 05_ANALIZ/kod/fue_ilce_gecerlilik.py; TÜİK 2024–2025, OSM 25.10.2026, GHSL R2023A.", fontsize=7.5, color=YAZI_2)
fig.subplots_adjust(left=0.235, right=0.98, top=0.76, bottom=0.17, wspace=0.08)
kaydet(fig, "fue_gecerlilik_ilce")

# --- 2. Faz 2 yükseklik bulgusu yeniden ---------------------------------------------------------------------------
Y = pd.read_csv(SON / "fue_ilce_yukseklik_yeniden.csv")
fig, ax = plt.subplots(figsize=(9, 4.3))
for i, r in Y.iterrows():
    b, lo, hi = 300 * r.yukseklik_b, 300 * (r.yukseklik_b - 1.96 * r.yukseklik_sh), 300 * (r.yukseklik_b + 1.96 * r.yukseklik_sh)
    renk = MAVI if i == 0 else "#256abf"
    ax.plot([lo, hi], [i, i], color=renk, lw=2, solid_capstyle="round")
    ax.plot(b, i, "o", ms=8, color=renk, mec=ZEMIN, mew=2)
    ax.text(hi + 0.08, i, f"kat başına %{tr(b, 2)}  (p = {tr(r.yukseklik_p, 3)})", va="center", fontsize=8, color=YAZI_2)
ax.axvline(0, color=YAZI_3, lw=1)
ax.set_yticks(range(len(Y)), ["Faz 2 modeli", "+ 15 dk temel ihtiyaç erişimi", "+ ulaşım ve cami erişimi", "+ kent merkezi payı",
                              "+ PM2.5, yüzey sıcaklığı, ağaç"][:len(Y)])
ax.invert_yaxis()
ax.set_xlim(-0.6, 7.2)
ax.grid(axis="x", color=IZGARA, lw=0.8)
ax.set_axisbelow(True)
sade_eksen(ax)
ax.set_xlabel("Yaşanan bina yüksekliğinde +3 m (≈ 1 kat) başına standartlaştırılmış ölüm oranındaki değişim (%, %95 GA)")
fig.suptitle("Faz 2'nin yükseklik–ölümlülük bulgusu kentsellik ve çevre kontrolleriyle zayıflıyor", x=0.01, ha="left",
             fontsize=12, fontweight="bold", color=YAZI)
fig.text(0.01, 0.885, "973 ilçe, il sabit etkisi, kadın eğitimi, nüfus artışı, ln yoğunluk, yeşil erişim ve kavşak yoğunluğu her modelde var.",
         fontsize=8.5, color=YAZI_2)
fig.subplots_adjust(left=0.25, right=0.97, top=0.8, bottom=0.18)
kaydet(fig, "fue_yukseklik_yeniden")

# --- 3. E–Ç ödünleşimi, ilçe başına küçük çoklu -----------------------------------------------------------------------
M = pd.read_csv(SON / "fue_mahalle.csv")
K = M[M.kentsel].copy()
SIRA = ["Fatih", "Silivri", "Başakşehir", "Nilüfer", "Kocasinan", "Meram", "Antakya", "Onikişubat", "Safranbolu", "Beypazarı"]
fig, axs = plt.subplots(2, 5, figsize=(15, 6.6), sharex=True, sharey=True)
for ax, ilce in zip(axs.flat, SIRA):
    ax.add_patch(plt.Rectangle((50, 50), 50, 50, color="#eef4fc", zorder=0))
    ax.scatter(K.FUE_E, K.FUE_C, s=np.sqrt(K.nufus) / 3, color=GRI_N, alpha=0.5, lw=0)
    s = K[K.ilce == ilce]
    ax.scatter(s.FUE_E, s.FUE_C, s=np.sqrt(s.nufus) / 3, color=MAVI, edgecolor=ZEMIN, lw=0.8, zorder=3)
    ax.axhline(50, color=YAZI_3, lw=0.7)
    ax.axvline(50, color=YAZI_3, lw=0.7)
    iki = s[(s.FUE_E >= 50) & (s.FUE_C >= 50)]
    ax.set_title(f"{ilce}", loc="left", fontsize=10, fontweight="bold", color=YAZI)
    ax.text(0.02, 0.97, f"ikisi de ≥50: {len(iki)}/{len(s)} mahalle\n(nüfusun %{tr(100 * iki.nufus.sum() / s.nufus.sum(), 0)}'i)",
            transform=ax.transAxes, fontsize=7.5, va="top", color=YAZI_2)
    ax.set_xlim(5, 100)
    ax.set_ylim(15, 85)
    ax.grid(color=IZGARA, lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
for ax in axs[1]:
    ax.set_xlabel("Erişim (E)")
for ax in axs[:, 0]:
    ax.set_ylabel("Çevre-ölçek (Ç)")
fig.suptitle("Erişim ile çevre-ölçek arasında ödünleşim: ikisinde birden iyi mahalle az", x=0.01, ha="left",
             fontsize=13, fontweight="bold", color=YAZI)
fig.text(0.01, 0.915, "300 kentsel mahalle (gri: diğer pilotlar). Nokta alanı nüfusla orantılı. Mavi zeminli çeyrek: iki alt endekste de "
         f"pilot medyanı (50) üstü — toplam {((K.FUE_E >= 50) & (K.FUE_C >= 50)).sum()} mahalle. Spearman ρ = −0,61.",
         fontsize=8.5, color=YAZI_2)
fig.subplots_adjust(left=0.05, right=0.99, top=0.84, bottom=0.09, wspace=0.08, hspace=0.3)
kaydet(fig, "fue_erisim_cevre_odunlesim")

# --- 4. ilçe profili ısı tablosu ----------------------------------------------------------------------------------
OZ = pd.read_csv(SON / "fue_ilce_ozet.csv").set_index("ilce").loc[SIRA]
KOL = [("B1", "B1 Beden\nve Can"), ("B2", "B2 Akıl\nve Ruh"), ("B3", "B3 Nesil\nve Aile"), ("B4", "B4 Mülk\nve Geçim"),
       ("B5", "B5 Topluluk\nve İnanç"), ("B6", "B6\nMizan"), ("FUE_E", "Erişim\n(E)"), ("FUE_C", "Çevre-\nölçek (Ç)"), ("FUE", "FUE")]
V = OZ[[k for k, _ in KOL]].values
fig, ax = plt.subplots(figsize=(11, 5.4))
cmap, norm = ListedColormap(MAVI_R), BoundaryNorm([0, 35, 45, 55, 65, 101], 5)
ax.imshow(V, cmap=cmap, norm=norm, aspect="auto")
for i in range(V.shape[0]):
    for j in range(V.shape[1]):
        ax.text(j, i, tr(V[i, j], 0), ha="center", va="center", fontsize=9, color="white" if V[i, j] >= 55 else YAZI,
                fontweight="bold" if j == V.shape[1] - 1 else "normal")
ax.set_xticks(range(len(KOL)), [a for _, a in KOL], fontsize=8.5)
ax.set_yticks(range(len(SIRA)), [f"{s}  ({int(OZ.loc[s, 'kentsel'])} mah.)" for s in SIRA])
ax.xaxis.tick_top()
for x in (5.5, 7.5):
    ax.axvline(x, color=ZEMIN, lw=4)
for sp in ax.spines.values():
    sp.set_visible(False)
ax.tick_params(length=0)
fig.suptitle("Pilot ilçelerin boyut profili — kentsel mahallelerin nüfus ağırlıklı ortalaması (0–100)", x=0.01, ha="left",
             fontsize=12, fontweight="bold", color=YAZI)
fig.text(0.01, 0.015, "Puanlar 300 kentsel mahalle arasında yüzdelik sıradır; 50 = pilot medyanı. Renk sınıfları: <35, 35–45, 45–55, 55–65, ≥65. "
         "Kaynak: 05_ANALIZ/sonuclar/fue_ilce_ozet.csv", fontsize=7.5, color=YAZI_2)
fig.subplots_adjust(left=0.17, right=0.99, top=0.8, bottom=0.07)
kaydet(fig, "fue_ilce_profili")
print("grafikler yazıldı")

# --- 5. FUE v0.2: uydu göstergeleri ve ölümlülük (973 ilçe) --------------------------------------------------------
if (SON / "fue_ilce_cevre_kontrol.csv").exists():
    SATIRLAR = [("C_lite", "Çevre-ölçek v0.1 (OSM + GHSL)"), ("C_lite_v2", "Çevre-ölçek v0.2 (+ uydu)"),
                ("E_lite", "Erişim"), ("pm25", "PM2.5"), ("yapili300", "Yapılı alan payı (300 m)"),
                ("agac300", "Ağaç örtüsü (300 m)"), ("lst", "Yaz yüzey sıcaklığı")]
    MOD3 = [("il SE + eğitim + göç", "Temel model", MAVI), ("+ ln yoğunluk", "+ ln yoğunluk", TURUNCU),
            ("+ kentsellik ve yaş yapısı", "+ kentsellik ve yaş yapısı", "#1baf7a")]
    fig, ax = plt.subplots(figsize=(11, 5.6))
    for i, (k, ad) in enumerate(SATIRLAR):
        for dy, (mk, mad, renk) in zip((-0.22, 0, 0.22), MOD3):
            r = T[(T.sonuc == "smr") & (T.endeks == k) & (T.model == mk)].iloc[0]
            ax.plot([r.beta - 1.96 * r.sh, r.beta + 1.96 * r.sh], [i + dy, i + dy], color=renk, lw=2, solid_capstyle="round")
            ax.plot(r.beta, i + dy, "o", ms=7, color=renk, mec=ZEMIN, mew=1.5)
            if mk == "+ kentsellik ve yaş yapısı":
                if r.beta >= 0:
                    ax.text(r.beta + 1.96 * r.sh + 0.015, i + dy, f"{tr(r.beta, 2)}{r.yildiz}", va="center", fontsize=7.5, color=YAZI_2)
                else:
                    ax.text(r.beta - 1.96 * r.sh - 0.015, i + dy, f"{tr(r.beta, 2)}{r.yildiz}", va="center", ha="right", fontsize=7.5,
                            color=YAZI_2)
    ax.axvline(0, color=YAZI_3, lw=1)
    ax.set_xlim(-0.65, 0.65)
    ax.set_yticks(range(len(SATIRLAR)), [a for _, a in SATIRLAR])
    ax.invert_yaxis()
    ax.grid(axis="x", color=IZGARA, lw=0.8)
    ax.set_axisbelow(True)
    sade_eksen(ax)
    ax.set_xlabel("Standartlaştırılmış ölüm oranıyla ilişki (β, %95 GA; sağ = daha yüksek ölümlülük)")
    leg = [Line2D([], [], color=c, marker="o", ms=7, lw=2, label=a) for _, a, c in MOD3]
    fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.01, 0.9), ncol=3, frameon=False, fontsize=8.5)
    fig.suptitle("Uydu verisi çevre-ölçek eksenini güçlendiriyor: sinyal hava kirliliği ve ağaç örtüsünde", x=0.01, ha="left",
                 fontsize=12.5, fontweight="bold", color=YAZI)
    fig.text(0.01, 0.005, "973 ilçe, il sabit etkisi, kadın eğitimi ve nüfus artışı her modelde. Nüfus ağırlıklı WLS, il düzeyinde kümelenmiş SH; "
             "sayılar geniş modelin katsayısı. *** p<0,001 ** p<0,01 * p<0,05 † p<0,10.\nKaynak: 05_ANALIZ/kod/fue_ilce_gecerlilik.py; "
             "ESA WorldCover 2021, ACAG V6.GL.03 PM2.5 2022–2024, MODIS MYD11A2 Temmuz–Ağustos 2023–2024.", fontsize=7.5, color=YAZI_2)
    fig.subplots_adjust(left=0.25, right=0.97, top=0.8, bottom=0.17)
    kaydet(fig, "fue_v02_olumluluk")

    # --- 6. Erişim ve yükseklik katsayıları çevre yükleri kontrol edilince ------------------------------------------
    CK = pd.read_csv(SON / "fue_ilce_cevre_kontrol.csv")
    Y = pd.read_csv(SON / "fue_ilce_yukseklik_yeniden.csv")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6))
    ck_ad = ["Temel", "+ PM2.5, sıcaklık, ağaç", "+ kentsellik ve yaş", "+ ikisi birden"]
    for i, r in CK.iterrows():
        renk = MAVI if i == 0 else "#256abf"
        a1.plot([r.E_lite_b - 1.96 * r.E_lite_sh, r.E_lite_b + 1.96 * r.E_lite_sh], [i, i], color=renk, lw=2, solid_capstyle="round")
        a1.plot(r.E_lite_b, i, "o", ms=8, color=renk, mec=ZEMIN, mew=2)
        a1.text(r.E_lite_b + 1.96 * r.E_lite_sh + 0.015, i, f"β = {tr(r.E_lite_b, 2)}", va="center", fontsize=8, color=YAZI_2)
    a1.set_yticks(range(len(CK)), ck_ad)
    a1.set_xlim(0, 0.65)
    a1.set_title("Erişim (E) → ölümlülük", loc="left", fontsize=10, fontweight="bold", color=YAZI)
    a1.set_xlabel("Standartlaştırılmış katsayı (%95 GA)")
    y_ad = ["Faz 2 modeli", "+ 15 dk temel ihtiyaç", "+ ulaşım ve cami", "+ kent merkezi payı", "+ PM2.5, sıcaklık, ağaç"]
    for i, r in Y.iterrows():
        b, lo, hi = 300 * r.yukseklik_b, 300 * (r.yukseklik_b - 1.96 * r.yukseklik_sh), 300 * (r.yukseklik_b + 1.96 * r.yukseklik_sh)
        renk = MAVI if i == 0 else "#256abf"
        a2.plot([lo, hi], [i, i], color=renk, lw=2, solid_capstyle="round")
        a2.plot(b, i, "o", ms=8, color=renk, mec=ZEMIN, mew=2)
        a2.text(hi + 0.1, i, f"%{tr(b, 2)} (p = {tr(r.yukseklik_p, 3)})", va="center", fontsize=8, color=YAZI_2)
    a2.set_yticks(range(len(Y)), y_ad[:len(Y)])
    a2.set_xlim(-1, 6.5)
    a2.axvline(0, color=YAZI_3, lw=1)
    a2.set_title("Yükseklik → ölümlülük (kat başına %)", loc="left", fontsize=10, fontweight="bold", color=YAZI)
    a2.set_xlabel("+3 m yaşanan yükseklik başına SMR değişimi (%, %95 GA)")
    for a in (a1, a2):
        a.invert_yaxis()
        a.grid(axis="x", color=IZGARA, lw=0.8)
        a.set_axisbelow(True)
        sade_eksen(a)
    fig.suptitle("Çevre yükleri eklenince: erişimin ilişkisi %30 azalıyor, yükseklik etkisi anlamlılığını yitiriyor", x=0.01, ha="left",
                 fontsize=12, fontweight="bold", color=YAZI)
    fig.subplots_adjust(left=0.13, right=0.97, top=0.82, bottom=0.15, wspace=0.55)
    kaydet(fig, "fue_v02_cevre_kontrol")
    print("v0.2 grafikleri yazıldı")
