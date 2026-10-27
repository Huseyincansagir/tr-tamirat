"""
Aynı yoğunluk, üç biçim
=======================
1 hektarlık (100 m x 100 m, çevre yolların yarısı dahil) bir hücrede ~100 haneyi
üç farklı yapılaşma biçimiyle yerleştirir; plan, kuzey-güney kesiti ve metrik
tablosu üretir.

  A) Kapalı site / yüksek blok   : 2 blok, 12 kat
  B) Bitişik nizam çevre adası   : zemin + 3 kat, ortak iç avlu, zeminde çarşı
  C) Avlulu çok kuşaklı sıra ev  : zemin + 2 kat, parsel başına 2 hane, özel avlu

Öncül çalışmalar: Martin & March (1972) "Land Use and Built Form";
Urban Task Force (1999) "Towards an Urban Renaissance".

Geometriler idealize edilmiştir; amaç biçim ile yoğunluk arasındaki ilişkiyi
göstermektir, bir proje önerisi değildir.

Çalıştırma:  python ayni_yogunluk_uc_bicim.py
Çıktılar  :  ../ayni_yogunluk_uc_bicim.png|svg|pdf, ../ayni_yogunluk_uc_bicim_metrikler.csv
"""

import csv
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

CIKTI = Path(__file__).resolve().parent.parent

# --- Ortak varsayımlar -------------------------------------------------------
HUCRE = 100.0                 # m, brüt hücre kenarı (1 ha)
HANE_BUYUKLUGU = 3.1          # kişi/hane (varsayım; TÜİK son değeriyle güncellenecek)
KONUT_BRUT_M2 = 110.0         # A ve B için ortalama brüt konut alanı
KAT_YUK = 3.0                 # m, konut katı
ZEMIN_TICARI_YUK = 4.5        # m, ticari zemin kat
ENLEM = 41.0                  # İstanbul
GUN_DONUMU_ACI = 90 - ENLEM - 23.44   # 21 Aralık öğle güneş yüksekliği (derece)
ESINLIK_ACI = 90 - ENLEM              # 21 Mart öğle güneş yüksekliği (derece)


def golge(h, aci):
    return h / math.tan(math.radians(aci))


# --- Renkler -----------------------------------------------------------------
R_SOKAK = "#d9d6d0"
R_ZEMIN = "#f4f1ea"
R_BINA = "#5b4a3f"
R_BINA_ARKA = "#b9aca2"
R_TICARI = "#e07b00"
R_ORTAK_YESIL = "#a9cf8f"
R_OZEL_AVLU = "#d6ebc4"
R_AGAC = "#5e9444"
R_OTOPARK = "#c4c4c4"
R_GOLGE = "#7d8fb3"
R_GUNES = "#e0a100"

# --- A) Kapalı site / yüksek blok -------------------------------------------
A_SINIR = 10.0                                   # yarım bulvar genişliği
A_BLOKLAR = [(20, 45, 21, 21), (59, 34, 21, 21)]  # x, y, gen, der (m)
A_KAT = 12
A_DAIRE_KAT = 4
A_YUK = A_KAT * KAT_YUK

a_taban = sum(w * d for _, _, w, d in A_BLOKLAR)
a_insaat = a_taban * A_KAT
a_hane = len(A_BLOKLAR) * A_KAT * A_DAIRE_KAT
a_net = (HUCRE - 2 * A_SINIR) ** 2
a_otopark_yuzey = 76 * 10
a_ortak_acik = a_net - a_taban

# --- B) Bitişik nizam çevre adası --------------------------------------------
B_SINIR = 12.0
B_DERINLIK = 12.0
B_KAT = 4                                        # zemin + 3
B_YUK = ZEMIN_TICARI_YUK + (B_KAT - 1) * KAT_YUK
b_ada = HUCRE - 2 * B_SINIR
b_avlu = b_ada - 2 * B_DERINLIK
b_taban = b_ada ** 2 - b_avlu ** 2
b_ticari = b_ada * B_DERINLIK                    # güney cephesi zemin kat: çarşı
b_insaat = b_taban * B_KAT
b_hane = int((b_insaat - b_ticari) // KONUT_BRUT_M2)
b_ortak_acik = b_avlu ** 2

# --- C) Avlulu çok kuşaklı sıra ev -------------------------------------------
C_SINIR = 5.0
C_ARA_SOKAK = 6.0
C_PARSEL_GEN = 7.5
C_PARSEL_DER = 21.0
C_EV_DER = 12.0
C_KAT = 3                                        # zemin + 2
C_HANE_PARSEL = 2                                # zemin: büyükler, üst dubleks: genç aile
C_YUK = C_KAT * KAT_YUK

c_net_gen = HUCRE - 2 * C_SINIR
c_parsel_sira = int(c_net_gen // C_PARSEL_GEN)
c_parsel = c_parsel_sira * 4                     # 2 şerit x sırt sırta 2 sıra
c_taban = c_parsel * C_PARSEL_GEN * C_EV_DER
c_insaat = c_taban * C_KAT
c_hane = c_parsel * C_HANE_PARSEL
c_ozel_avlu = c_parsel * C_PARSEL_GEN * (C_PARSEL_DER - C_EV_DER)
c_sokak = HUCRE ** 2 - c_net_gen ** 2 + C_ARA_SOKAK * c_net_gen

# Sıraların güney kenarları (y) ve evin parsel içindeki konumu
y0 = C_SINIR
y_serit2 = C_SINIR + 2 * C_PARSEL_DER + C_ARA_SOKAK
C_SIRALAR = [  # (parsel_y0, ev_y0) — ev her zaman sokağa bakar
    (y0, y0),                                                          # güney sokağına bakan
    (y0 + C_PARSEL_DER, y0 + 2 * C_PARSEL_DER - C_EV_DER),             # ara sokağa bakan
    (y_serit2, y_serit2),                                              # ara sokağa bakan
    (y_serit2 + C_PARSEL_DER, y_serit2 + 2 * C_PARSEL_DER - C_EV_DER), # kuzey sokağına bakan
]

# --- Metrikler ---------------------------------------------------------------
def kisi(hane):
    return hane * HANE_BUYUKLUGU


def tr(metin):
    """1,234.5 -> 1.234,5 (Türkçe sayı biçimi)."""
    return str(metin).replace(",", "§").replace(".", ",").replace("§", ".")


metrikler = [
    ("Hane sayısı (hane/ha)", a_hane, b_hane, c_hane, "{:.0f}"),
    (f"Tahmini nüfus (kişi/ha, {tr(HANE_BUYUKLUGU)} kişi/hane)", kisi(a_hane), kisi(b_hane), kisi(c_hane), "{:.0f}"),
    ("Brüt inşaat alanı (m²)", a_insaat, b_insaat, c_insaat, "{:,.0f}"),
    ("Emsal (brüt 1 ha'ya göre)", a_insaat / 1e4, b_insaat / 1e4, c_insaat / 1e4, "{:.2f}"),
    ("Yapı oturumu (%)", a_taban / 100, b_taban / 100, c_taban / 100, "{:.0f}"),
    ("Kat adedi", A_KAT, B_KAT, C_KAT, "{:.0f}"),
    ("Bina yüksekliği (m)", A_YUK, B_YUK, C_YUK, "{:.1f}"),
    ("Ortalama konut büyüklüğü (m² brüt)", a_insaat / a_hane, (b_insaat - b_ticari) / b_hane, c_insaat / c_hane, "{:.0f}"),
    ("Ortak açık alan, ada içi (m²)", a_ortak_acik, b_ortak_acik, 0, "{:,.0f}"),
    ("Özel bahçe/avlu (m²)", 0, 0, c_ozel_avlu, "{:,.0f}"),
    ("Kişi başı ada içi açık alan (m²)", a_ortak_acik / kisi(a_hane), b_ortak_acik / kisi(b_hane), c_ozel_avlu / kisi(c_hane), "{:.1f}"),
    ("Sokak ve yol alanı (m²)", HUCRE ** 2 - a_net, HUCRE ** 2 - b_ada ** 2, c_sokak, "{:,.0f}"),
    ("Zemin + 3 kat içindeki hane oranı (%)", 4 / A_KAT * 100, 100, 100, "{:.0f}"),
    ("Zemine/avluya doğrudan açılan hane oranı (%)", 2 * A_DAIRE_KAT / a_hane * 100, None, 100, "{:.0f}"),
    ("Zemin kat ticaret cephesi (m)", 0, b_ada, 0, "{:.0f}"),
    ("21 Aralık öğle gölge boyu (m)", golge(A_YUK, GUN_DONUMU_ACI), golge(B_YUK, GUN_DONUMU_ACI), golge(C_YUK, GUN_DONUMU_ACI), "{:.0f}"),
    ("21 Mart öğle gölge boyu (m)", golge(A_YUK, ESINLIK_ACI), golge(B_YUK, ESINLIK_ACI), golge(C_YUK, ESINLIK_ACI), "{:.0f}"),
    # PAİY md. 34/1 (RG 01.07.2026): bodrum dahil 4+ katta asansör tesisi, 3 katta asansör yeri zorunlu
    ("Asansör (PAİY md. 34/1)", "Zorunlu (2+ asansör)", "Zorunlu (4 kat)", "Asansör yeri bırakılır", None),
]

# B için zemine açılan hane: avluya bakan zemin kat daireleri (ticari olmayan 3 kanat)
b_zemin_konut = (b_taban - b_ticari) / KONUT_BRUT_M2
metrikler[13] = (metrikler[13][0], metrikler[13][1], b_zemin_konut / b_hane * 100, metrikler[13][3], "{:.0f}")


# --- Çizim yardımcıları ------------------------------------------------------
def plan_zemin(ax, renk_ic, sinir):
    ax.add_patch(Rectangle((0, 0), HUCRE, HUCRE, fc=R_SOKAK, ec="none", zorder=0))
    ax.add_patch(Rectangle((sinir, sinir), HUCRE - 2 * sinir, HUCRE - 2 * sinir, fc=renk_ic, ec="none", zorder=1))


def agac(ax, x, y, r=2.2):
    ax.add_patch(Circle((x, y), r, fc=R_AGAC, ec="white", lw=0.4, alpha=0.9, zorder=6))


def plan_ayar(ax, baslik):
    ax.set_xlim(0, HUCRE)
    ax.set_ylim(0, HUCRE)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#888")
        s.set_linewidth(0.6)
    ax.set_title(baslik, fontsize=13, fontweight="bold", loc="left", pad=8)


def kesit_ayar(ax, aciklama):
    ax.set_xlim(0, HUCRE)
    ax.set_ylim(-2, 42)
    ax.set_aspect("equal")
    ax.axhline(0, color="#333", lw=1.2, zorder=5)
    ax.set_yticks([0, 10, 20, 30, 40])
    ax.set_yticklabels(["0", "10", "20", "30", "40 m"], fontsize=7)
    ax.set_xticks([0, 50, 100])
    ax.set_xticklabels(["G", "kesit (K–G)", "K"], fontsize=7)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    ax.text(2, 40, aciklama, fontsize=7.5, va="top", color="#444")


def kesit_bina(ax, y0, y1, h, katlar, renk=R_BINA, zorder=4, ticari_zemin=False):
    ax.add_patch(Rectangle((y0, 0), y1 - y0, h, fc=renk, ec="white", lw=0.3, zorder=zorder))
    zemin = ZEMIN_TICARI_YUK if ticari_zemin else KAT_YUK
    for i in range(1, katlar):
        z = zemin + (i - 1) * KAT_YUK
        ax.plot([y0, y1], [z, z], color="white", lw=0.3, alpha=0.6, zorder=zorder + 0.1)
    if ticari_zemin:
        ax.add_patch(Rectangle((y0, 0), y1 - y0, ZEMIN_TICARI_YUK, fc="none", ec=R_TICARI, lw=1.2, zorder=zorder + 0.2))


def kesit_golge(ax, y_kuzey, h, etiket=True):
    uz = golge(h, GUN_DONUMU_ACI)
    ax.plot([y_kuzey, y_kuzey + uz], [h, 0], color=R_GUNES, lw=0.9, ls="--", zorder=7)
    ax.plot([y_kuzey, min(y_kuzey + uz, HUCRE)], [0.25, 0.25], color=R_GOLGE, lw=3, alpha=0.6, solid_capstyle="butt", zorder=6)
    if etiket:
        x_et = min(y_kuzey + uz / 2, HUCRE - 12)
        ax.text(x_et, 1.6, f"21 Ara. gölge {uz:.0f} m", fontsize=6.5, color="#3c4d70", ha="center", zorder=8)


# --- Şekil ---------------------------------------------------------------------
fig = plt.figure(figsize=(18, 15.5), dpi=150)
gs = fig.add_gridspec(3, 3, height_ratios=[1.0, 0.46, 1.02], hspace=0.12, wspace=0.08,
                      left=0.04, right=0.98, top=0.915, bottom=0.03)

fig.text(0.04, 0.965, "Aynı yoğunluk, üç biçim", fontsize=24, fontweight="bold")
fig.text(0.04, 0.943,
         "1 hektarda ≈100 hane: yüksek blok, bitişik nizam çevre adası ve avlulu çok kuşaklı sıra ev. "
         "Plan (üstte), kuzey–güney kesiti ve 21 Aralık öğle gölgesi (ortada, İstanbul 41°K), metrikler (altta).",
         fontsize=11, color="#444")

# A planı
ax = fig.add_subplot(gs[0, 0])
plan_zemin(ax, R_ORTAK_YESIL, A_SINIR)
ax.add_patch(Rectangle((A_SINIR, A_SINIR), HUCRE - 2 * A_SINIR, HUCRE - 2 * A_SINIR, fc="none",
                       ec="#222", lw=1.6, ls=(0, (4, 2)), zorder=7))
ax.add_patch(Rectangle((12, 12), 76, 10, fc=R_OTOPARK, ec="#999", hatch="////", lw=0.5, zorder=2))
ax.add_patch(Rectangle((46, 22), 6, 14, fc=R_OTOPARK, ec="#999", lw=0.5, zorder=2))
for x, y, w, d in A_BLOKLAR:
    ax.add_patch(Rectangle((x, y), w, d, fc=R_BINA, ec="white", lw=0.5, zorder=5))
    ax.text(x + w / 2, y + d / 2, f"{A_KAT} kat", color="white", ha="center", va="center", fontsize=9, zorder=6)
for x, y in [(16, 80), (30, 84), (82, 72), (84, 84), (16, 30), (86, 32)]:
    agac(ax, x, y)
ax.text(50, 17, "yüzey otoparkı + rampa", ha="center", va="center", fontsize=7.5, zorder=6)
ax.text(50, 4.5, "site duvarı · güvenlik kapısı", ha="center", fontsize=7.5, color="#222")
ax.plot([30.5, 30.5], [0, HUCRE], color="#c00", lw=0.7, ls="-.", zorder=8)
plan_ayar(ax, "A · Kapalı site / yüksek blok")

# B planı
ax = fig.add_subplot(gs[0, 1])
plan_zemin(ax, R_ORTAK_YESIL, B_SINIR + B_DERINLIK)
s, d = B_SINIR, B_DERINLIK
e = HUCRE - B_SINIR
for r in [(s, s, b_ada, d), (s, e - d, b_ada, d), (s, s + d, d, b_avlu), (e - d, s + d, d, b_avlu)]:
    ax.add_patch(Rectangle(r[:2], r[2], r[3], fc=R_BINA, ec="white", lw=0.5, zorder=5))
ax.add_patch(Rectangle((s, s), b_ada, d, fc="none", ec=R_TICARI, lw=2.2, zorder=6))
ax.text(50, s + d / 2, "zemin kat çarşı · üstte 3 kat konut", color="white", ha="center", va="center", fontsize=8, zorder=7)
ax.text(50, 50, "ortak iç avlu\noyun · ağaç · bostan", ha="center", va="center", fontsize=9, zorder=7)
for x, y in [(32, 34), (68, 34), (32, 66), (68, 66), (50, 70), (50, 30)]:
    agac(ax, x, y, 2.6)
for t in range(6, 100, 11):
    agac(ax, t, 5.5, 1.6)
    agac(ax, t, 94.5, 1.6)
ax.plot([50, 50], [0, HUCRE], color="#c00", lw=0.7, ls="-.", zorder=8)
plan_ayar(ax, "B · Bitişik nizam çevre adası (Z+3)")

# C planı
ax = fig.add_subplot(gs[0, 2])
plan_zemin(ax, R_ZEMIN, C_SINIR)
ax.add_patch(Rectangle((C_SINIR, y0 + 2 * C_PARSEL_DER), c_net_gen, C_ARA_SOKAK, fc=R_SOKAK, ec="none", zorder=2))
for p_y0, ev_y0 in C_SIRALAR:
    for i in range(c_parsel_sira):
        x = C_SINIR + i * C_PARSEL_GEN
        ax.add_patch(Rectangle((x, p_y0), C_PARSEL_GEN, C_PARSEL_DER, fc=R_OZEL_AVLU, ec="#7a9a64", lw=0.4, zorder=3))
        ax.add_patch(Rectangle((x, ev_y0), C_PARSEL_GEN, C_EV_DER, fc=R_BINA, ec="white", lw=0.5, zorder=5))
        avlu_orta = p_y0 + (C_PARSEL_DER - C_EV_DER) / 2 + (C_EV_DER if ev_y0 == p_y0 else 0)
        if i % 2 == 0:
            agac(ax, x + C_PARSEL_GEN / 2, avlu_orta, 1.5)
ax.text(50, y0 + 2 * C_PARSEL_DER + C_ARA_SOKAK / 2, "ara sokak (6 m) · yaya öncelikli", ha="center", va="center", fontsize=7.5, zorder=7)
ax.text(50, 2.2, f"{c_parsel} parsel × {C_HANE_PARSEL} hane · zemin: büyükler · üst dubleks: genç aile",
        ha="center", fontsize=7.5, color="#222", zorder=7)
ax.plot([46.25, 46.25], [0, HUCRE], color="#c00", lw=0.7, ls="-.", zorder=8)
plan_ayar(ax, "C · Avlulu çok kuşaklı sıra ev (Z+2)")

# Kuzey oku ve ölçek (A planına)
ax0 = fig.axes[0]
ax0.annotate("", xy=(94, 97), xytext=(94, 89), arrowprops=dict(arrowstyle="-|>", color="#222", lw=1.2), zorder=9)
ax0.text(94, 85.5, "K", ha="center", fontsize=9, fontweight="bold", zorder=9)
ax0.plot([3, 23], [1.6, 1.6], color="#222", lw=2, zorder=9)
ax0.text(13, 2.4, "20 m", ha="center", fontsize=7, zorder=9)

# Kesitler
ax = fig.add_subplot(gs[1, 0])
x_A, y_A, w_A, d_A = A_BLOKLAR[1]
kesit_bina(ax, y_A, y_A + d_A, A_YUK, A_KAT, renk=R_BINA_ARKA, zorder=3)   # arka plandaki blok (görünüş)
x_A, y_A, w_A, d_A = A_BLOKLAR[0]
kesit_bina(ax, y_A, y_A + d_A, A_YUK, A_KAT)
kesit_golge(ax, y_A + d_A, A_YUK)
kesit_ayar(ax, "Gölge komşu adaya taşar; zemin ile 12. kat arasında göz ve ses teması kopar.")

ax = fig.add_subplot(gs[1, 1])
kesit_bina(ax, B_SINIR, B_SINIR + B_DERINLIK, B_YUK, B_KAT, ticari_zemin=True)
kesit_bina(ax, HUCRE - B_SINIR - B_DERINLIK, HUCRE - B_SINIR, B_YUK, B_KAT, ticari_zemin=False)
kesit_golge(ax, B_SINIR + B_DERINLIK, B_YUK)
kesit_ayar(ax, "Kışın avlunun kuzey yarısı güneşte kalır; her pencere avluyu ya da sokağı görür.")

ax = fig.add_subplot(gs[1, 2])
for p_y0, ev_y0 in C_SIRALAR:
    kesit_bina(ax, ev_y0, ev_y0 + C_EV_DER, C_YUK, C_KAT)
for _, ev_y0 in C_SIRALAR:
    kesit_golge(ax, ev_y0 + C_EV_DER, C_YUK, etiket=(ev_y0 == C_SIRALAR[0][1]))
kesit_ayar(ax, "Kışın avlular gölgede, ilkbahar–yaz güneşte; kış güneşi üst katlara ve çatıya düşer.")

# Metrik tablosu
ax = fig.add_subplot(gs[2, :])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
sutunlar = ["Gösterge", "A · Yüksek blok", "B · Çevre adası", "C · Avlulu sıra ev"]
x_sut = [0.0, 0.43, 0.62, 0.81]
satir_h = 0.84 / (len(metrikler) + 1.5)
y = 1.0
for xs, baslik in zip(x_sut, sutunlar):
    ax.text(xs + (0.005 if xs == 0 else 0.0), y - satir_h * 0.6, baslik, fontsize=10.5, fontweight="bold", va="center")
ax.plot([0, 1], [y - satir_h * 1.15] * 2, color="#333", lw=1)
for i, (ad, a, b, c, fmt) in enumerate(metrikler):
    yy = y - satir_h * (i + 1.75)
    if i % 2 == 0:
        ax.add_patch(Rectangle((0, yy - satir_h / 2), 1, satir_h, fc="#f3f1ec", ec="none", zorder=0))
    ax.text(0.005, yy, ad, fontsize=9.5, va="center")
    for xs, v in zip(x_sut[1:], (a, b, c)):
        metin = "—" if v is None else (v if fmt is None else tr(fmt.format(v)))
        ax.text(xs, yy, metin, fontsize=9.5, va="center", family="DejaVu Sans Mono" if fmt else None)
ax.text(0.005, 0.0,
        "Varsayımlar: hücre 100 × 100 m (çevre sokakların yarısı dahil); A ve B'de ortalama brüt konut 110 m²; konut katı 3,0 m, ticari zemin 4,5 m; "
        f"hane büyüklüğü {tr(HANE_BUYUKLUGU)} (varsayım). A'da ada içi açık alanın ≈{a_otopark_yuzey + 84:.0f} m²'si yüzey otoparkı ve rampadır; "
        "otopark gereksinimi A'da bodrum, B ve C'de sokak/bodrum ile karşılanır.\n"
        "Okuma: A en çok açık alanı verir ama bu alan çoğunlukla gözetimsiz ve sahipsizdir. B, ortak ve korunaklı bir avlu ile sokakta çarşı üretir. "
        "C, aynı arazide her haneye zemin ve özel avlu, her parsele çok kuşaklı yaşam imkânı verir; buna karşılık ada içinde ortak yeşil yoktur ve kış güneşi için yönlenme kritiktir. "
        "Öncül: Martin & March (1972); Urban Task Force (1999).",
        fontsize=8, color="#444", va="bottom", wrap=True)

for uzanti in ("png", "svg", "pdf"):
    fig.savefig(CIKTI / f"ayni_yogunluk_uc_bicim.{uzanti}", facecolor="white")

with open(CIKTI / "ayni_yogunluk_uc_bicim_metrikler.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["gosterge", "A_yuksek_blok", "B_cevre_adasi", "C_avlulu_sira_ev"])
    for ad, a, b, c, fmt in metrikler:
        w.writerow([ad] + [("" if v is None else (round(v, 2) if isinstance(v, float) else v)) for v in (a, b, c)])

sys.stdout.reconfigure(encoding="utf-8")
for ad, a, b, c, fmt in metrikler:
    print(f"{ad:48s}", a, b, c)
