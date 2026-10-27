"""
Model mahalle v2.1 — asansör kuralının tipolojilere etkisi (özet levha)
====================================================================
PAİY md. 34/1 (RG 01.07.2026) [D]: bodrum dahil 3 katlı binada asansör yeri, ≥ 4 katta asansör tesisi
(tek bağımsız bölümlü konut hariç). Her tipoloji için kural, v2 çözümü, alan etkisi, maliyet etkisi
(bugünkü uygulama ve paket P4) ve plandaki bina sayısı. Maliyetler tipoloji_verisi.py'de [V].

Çalıştırma:  python tipoloji_asansor_ozeti.py
Çıktı     :  ../tipoloji_asansor_ozeti.png|svg
"""

import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

import metrikler as mt
import plan_modeli as pm
import tipoloji_verisi as tv
from ortak import CIKTI, KAT_YUK, sayi

M = mt.metrikleri_hesapla()
R_MEVCUT = "#2a78d6"     # kategorik 1: bugünkü uygulama
R_P4 = "#eb6834"         # kategorik 2: paket P4
METIN = "#0b0b0b"
METIN2 = "#52514e"
IZGARA = "#e5e3df"


def satirlar():
    """Tipoloji başına bir satır: (ad, kural, çözüm, alan, alan_payı, maliyet_mevcut/konut, %, p4/konut, %, bina, hane)."""
    T1_W = (pm.XS[0][1] - pm.XS[0][0]) / int((pm.XS[0][1] - pm.XS[0][0]) // pm.T1_GEN)
    T2_W = (pm.XS[0][1] - pm.XS[0][0]) / int((pm.XS[0][1] - pm.XS[0][0]) // pm.T2_GEN)
    k_as = tv.KUYU_ASANSOR[0] * tv.KUYU_ASANSOR[1]
    t1_brut = 3 * T1_W * pm.T1_EV_DER + T1_W * pm.T1_GENISLEME
    t2_brut = 3 * T2_W * pm.T2_EV_DER
    sk, gw = pm.T3_SOKAK_KANADI, 36.0
    yan = 2 * pm.T3_YAN_KANAT_G * pm.T3_YAN_KANAT_L * 2
    t3_2 = sk * gw * 3 - 3.5 * sk + yan
    t3_3 = sk * gw * 4 - 3.5 * sk + yan
    t4_3 = pm.T4_MODUL * pm.T4_DER * 4
    t4_4 = pm.T4_MODUL * pm.T4_DER * 5
    tip = M["asn_tip"]

    def bina(ad):
        return int(tip.get(ad, {}).get("bina", 0)), tip.get(ad, {}).get("bb", 0)

    out = []
    # (ad, kat, BB/bina, kural, çözüm, ek alan m², brüt m², zorunlu maliyet, P4 maliyeti, isteğe bağlı maliyet, sınıf, plan anahtarı)
    out.append(("T1 büyüyebilen sıra ev", "Z+2", 1, "yok (tek BB)", "platform yeri: kiler/dolap dikmesi",
                3 * tv.KUYU_PLATFORM[0] * tv.KUYU_PLATFORM[1], t1_brut, 0, 0, tv.PLATFORM_TL, "T1", "T1 sıra ev"))
    out.append(("T2 çok kuşaklı ev", "Z+2", 2, "asansör yeri", "1,4 × 1,6 m kuyu (depo); zemin 2+1 eşiksiz",
                3 * tv.KUYU_T2[0] * tv.KUYU_T2[1], t2_brut, 0, 0, tv.PLATFORM_TL, "T2", "T2 çok kuşaklı ev"))
    out.append(("T3 avlu grubu, Z+2", "Z+2", 12, "asansör yeri", "2 çekirdekte kuyu; zemin 2 daire eşiksiz",
                2 * 3 * k_as, t3_2, 0, 0, 2 * tv.asansor_maliyeti(3), "T3_Z+2", "T3 sokak kanadı Z+2"))
    out.append(("T3 avlu grubu, Z+3", "Z+3", 15, "asansör", "2 asansör (P4: galeri + 1)",
                2 * 4 * k_as, t3_3, 2 * tv.asansor_maliyeti(4), tv.asansor_maliyeti(4), 0, "T3_Z+3", "T3 sokak kanadı Z+3"))
    if pm.KALIBRE:
        out.append(("T3 arka kanat (v2.1)", "Z", 2, "yok (1 kat)", "tek katlı; 2 eşiksiz 2+1 (avluyu kapatır)",
                    0.0, 36.0 * pm.T3_ARKA_DER, 0, 0, 0, "T3_Z+2", "T3 arka kanat (Z, v2.1)"))
    out.append(("T4 çubuk, Z+3", "Z+3", 9, "asansör", "1 asansör (çekirdekte)",
                4 * k_as, t4_3, tv.asansor_maliyeti(4), tv.asansor_maliyeti(4), 0, "T4", "T4 çubuk parseli Z+3"))
    out.append(("T4 köşe, Z+4", "Z+4", 12, "asansör", "1 asansör (5 durak)",
                5 * k_as, t4_4, tv.asansor_maliyeti(5), tv.asansor_maliyeti(5), 0, "T4", "T4 çubuk parseli Z+4"))
    sonuc = []
    for ad, kat, bb, kural, cozum, alan, brut, zor, p4, iste, sinif, anahtar in out:
        yapim = tv.tip_yapim_maliyeti(tv.SINIF[sinif], brut)
        n_bina, n_bb = bina(anahtar)
        if anahtar.startswith("T3"):
            n_hane = n_bina * bb               # sokak kanadı + yan kanatlar
        else:
            n_hane = n_bb
        sonuc.append(dict(ad=ad, kat=kat, bb=bb, kural=kural, cozum=cozum, alan=alan, alan_pay=alan / brut,
                          yapim=yapim, zor=zor, p4=p4, iste=iste, zor_k=zor / bb, p4_k=p4 / bb,
                          zor_pay=zor / yapim, p4_pay=p4 / yapim, iste_pay=iste / yapim, bina=n_bina, hane=n_hane))
    return sonuc


def tablo(ax, S):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    bas = ["Tipoloji (bina)", "Kat", "BB", "PAİY 34/1", "v2 çözümü", "Kuyu / yer alanı", "Zorunlu maliyet\n(bugünkü)",
           "Hane başına\nbugün · P4", "Yapıma oranı\nbugün · P4", "Plandaki\nbina"]
    xs = [0.0, 0.17, 0.21, 0.245, 0.33, 0.55, 0.65, 0.75, 0.855, 0.95]
    y = 0.95
    for x, b in zip(xs, bas):
        ax.text(x, y, b, fontsize=8.6, fontweight="bold", va="top", color=METIN)
    y -= 0.15
    ax.plot([0, 1], [y + 0.03] * 2, color="#333", lw=0.8)
    h = 0.12
    for k, s in enumerate(S):
        if k % 2 == 0:
            ax.add_patch(Rectangle((0, y - h * 0.7), 1, h, fc="#f3f1ec", ec="none"))
        vals = [s["ad"], s["kat"], str(s["bb"]), s["kural"], s["cozum"],
                f"{sayi(s['alan'], 1)} m² (%{sayi(100 * s['alan_pay'], 1)})",
                "—" if s["zor"] == 0 else f"{sayi(s['zor'] / 1e6, 1)} milyon TL",
                "—" if s["zor"] == 0 else f"{sayi(s['zor_k'] / 1e3)} · {sayi(s['p4_k'] / 1e3)} bin TL",
                "—" if s["zor"] == 0 else f"%{sayi(100 * s['zor_pay'], 1)} · %{sayi(100 * s['p4_pay'], 1)}",
                sayi(s["bina"])]
        for x, v in zip(xs, vals):
            ax.text(x, y - h * 0.2, v, fontsize=8.2, va="center", color=METIN)
        y -= h


def grafik(ax, S):
    """Yapım maliyetine oranı: zorunlu asansör (bugün / P4) ve isteğe bağlı platform; tek eksen."""
    adlar = [s["ad"] for s in S]
    ys = list(range(len(S)))[::-1]
    for y, s in zip(ys, S):
        if s["zor"] > 0:
            ax.barh(y + 0.18, 100 * s["zor_pay"], height=0.32, color=R_MEVCUT, edgecolor="white", linewidth=1.5)
            ax.barh(y - 0.18, 100 * s["p4_pay"], height=0.32, color=R_P4, edgecolor="white", linewidth=1.5)
            ax.text(100 * s["zor_pay"] + 0.3, y + 0.18, f"%{sayi(100 * s['zor_pay'], 1)}", va="center", fontsize=8,
                    color=METIN2)
            ax.text(100 * s["p4_pay"] + 0.3, y - 0.18, f"%{sayi(100 * s['p4_pay'], 1)}", va="center", fontsize=8,
                    color=METIN2)
        elif s["iste"] == 0:
            ax.text(0.3, y, "gerekmez (tek katlı, zeminden girişli)", va="center", fontsize=8, color=METIN2)
        else:
            ax.barh(y, 100 * s["iste_pay"], height=0.32, color="white", edgecolor=R_MEVCUT, linewidth=1.0,
                    hatch="////")
            ax.text(100 * s["iste_pay"] + 0.3, y, f"%{sayi(100 * s['iste_pay'], 1)} (isteğe bağlı)", va="center",
                    fontsize=8, color=METIN2)
    ax.set_yticks(ys)
    ax.set_yticklabels(adlar, fontsize=8.5)
    ax.set_xlabel("yapım maliyetine oranı (%; 2026 tebliğ birim maliyeti, kâr hariç)", fontsize=8.5, color=METIN2)
    ax.set_xlim(0, 30)
    ax.grid(axis="x", color=IZGARA, lw=0.6)
    ax.set_axisbelow(True)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    ax.tick_params(labelsize=8, colors=METIN2)
    ax.set_title("Dikey dolaşımın maliyet payı (bina başına)", fontsize=10.5, fontweight="bold", loc="left")
    ax.legend(handles=[Patch(fc=R_MEVCUT, label="zorunlu asansör, bugünkü uygulama (her merdiven evine)"),
                       Patch(fc=R_P4, label="zorunlu asansör, paket P4 (galeriyle tek asansör)"),
                       Patch(fc="white", ec=R_MEVCUT, hatch="////", label="yerine sonradan platform ya da asansör (isteğe bağlı)")],
              fontsize=8, frameon=False, loc="lower right")


def main():
    S = satirlar()
    fig = plt.figure(figsize=(21, 12.5), dpi=150)
    gs = fig.add_gridspec(2, 2, height_ratios=[0.78, 1.0], width_ratios=[1.15, 1], hspace=0.20, wspace=0.10,
                          left=0.03, right=0.985, top=0.88, bottom=0.085)
    tablo(fig.add_subplot(gs[0, :]), S)
    ic = gs[1, 0].subgridspec(1, 2, width_ratios=[0.16, 0.84], wspace=0.0)
    grafik(fig.add_subplot(ic[1]), S)
    ax = fig.add_subplot(gs[1, 1])
    ax.axis("off")
    a = M["asn_toplam"]
    e = M["eris"]
    k = M["konut"]
    metin = [
        ("Plan geneli (çizimden)", True),
        (f"Asansör (bugünkü uygulama): {sayi(a.get('asansor_mevcut', 0))} adet ≈ "
         f"{sayi(a.get('maliyet_mevcut', 0) / 1e6, 1)} milyon TL; konut başına ortalama "
         f"{sayi(a.get('maliyet_mevcut', 0) / k / 1e3)} bin TL [V]", False),
        (f"Paket P4 ile: {sayi(a.get('asansor_p4', 0))} adet ≈ {sayi(a.get('maliyet_p4', 0) / 1e6, 1)} milyon TL "
         f"(−%{sayi(100 * (1 - a.get('maliyet_p4', 0) / a.get('maliyet_mevcut', 1)))})", False),
        (f"Asansör bakımı: yılda ≈ {sayi(a.get('asansor_mevcut', 0) * tv.ASANSOR_BAKIM_YIL / 1e6, 1)} milyon TL "
         f"(bugün) · {sayi(a.get('asansor_p4', 0) * tv.ASANSOR_BAKIM_YIL / 1e6, 1)} milyon TL (P4) [V]", False),
        (f"Asansör yeri: {sayi(a.get('yer', 0))} kuyu (T2 ve T3 Z+2) · platform yeri: "
         f"{sayi(a.get('platform_yeri', 0))} T1", False),
        ("", False),
        ("Erişilebilirlik", True),
        (f"Zemin katta eşiksiz daire: {sayi(e['zemin_adet'])} (%{sayi(100 * e['zemin'], 1)}; P4 eşiği %15)", False),
        (f"Asansörle ulaşılan daire: {sayi(e['asansorlu_adet'])} · basamaksız toplam %{sayi(100 * e['basamaksiz'])}", False),
        (f"T1: zeminde büyükler odası + duş, ayrıca %{sayi(100 * e['t1_zemin'])} (aşama 2)", False),
        (f"Binası ölçüt 17'yi sağlayan konut: %{sayi(100 * M['g17'])}", False),
        ("", False),
        ("Okuma", True),
        ("Kural 3 katta yalnız yer, 4 katta asansör istiyor. Z+2 tipolojilerde maliyet etkisi", False),
        ("küçük (kuyu alanının %1–3'ü); asıl yük Z+3 avlu gruplarında. P4'ün galeri", False),
        ("çözümü bu yükü yarıya indirir. Yaşlı ve engelli için ilk çözüm asansör değil, zemin kat", False),
        ("dairesi ve eşiksiz sokak (persona C: Hüseyin ve Selin zemin katta).", False),
    ]
    y = 0.98
    for m, kalin in metin:
        ax.text(0.0, y, m, fontsize=9.6 if kalin else 8.8, fontweight="bold" if kalin else "normal", va="top",
                color=METIN if kalin else METIN2)
        y -= 0.062
    fig.text(0.03, 0.955, "Model mahalle v2.1 — asansör kuralı ve tipolojiler", fontsize=22, fontweight="bold")
    fig.text(0.03, 0.925,
             "PAİY md. 34/1 (RG 01.07.2026) [D]: bodrum dahil 3 katta asansör yeri, ≥ 4 katta asansör (tek bağımsız bölümlü "
             "konut hariç). Kuyu 1,6 × 1,8 m (T2: 1,4 × 1,6; T1 platform: 1,0 × 2,3). Asansör 1,3 milyon TL (4 durak), "
             "platform 0,9 milyon TL — piyasa varsayımı [V].",
             fontsize=10.5, color="#444")
    fig.text(0.03, 0.012, f"Yapım maliyeti: 2026 Yapı Yaklaşık Birim Maliyetleri Tebliği (III.A {sayi(tv.BIRIM_MALIYET['III.A'])}, "
                          f"III.B {sayi(tv.BIRIM_MALIYET['III.B'])} TL/m²; %10 yüklenici kârı çıkarıldı) — M6 finansman modeliyle "
                          f"aynı varsayım. Kat yüksekliği {sayi(KAT_YUK, 1)} m. Tebliğ birim maliyetinin asansörü kısmen kapsayıp "
                          "kapsamadığı doğrulanmadı; burada ayrı kalem.", fontsize=8.5, color="#444")
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"tipoloji_asansor_ozeti.{uz}", facecolor="white")
    plt.close(fig)
    for s in S:
        print(s["ad"], s["bina"], round(s["zor_pay"] * 100, 1), round(s["iste_pay"] * 100, 1))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
