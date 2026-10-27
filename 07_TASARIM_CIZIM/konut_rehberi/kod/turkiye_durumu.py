"""
Konut rehberi — Türkiye'de konutun bugünkü durumu (Rapor 15 §2)
===============================================================
Kaynaklar (yalnız okunur):
  · TÜİK Bina ve Konut Nitelikleri Araştırması 2021 (bülten 45870): veri.py BKNA_* ve
    03_VERI/ham/tuik/il_paneli_ham_2025.csv (il tabloları; 25.10.2026'da alındı) [D]
  · Eurostat EU-SILC: 05_ANALIZ/sonuclar/stres_turkiye_ab.csv (Rapor 14) [D]
  · TÜİK İstatistiklerle Aile 2025, Çocuk Araştırması 2022: 03_VERI/islenmis/turkiye_temel_gostergeler.csv [D]
Çıktılar: turkiye_konut_durumu.csv · turkiye_konut_durumu.png/svg
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from cizim import CIKTI, MAVI, YAZI, YAZI2, ZEMIN
from veri import BKNA_DIGER, BKNA_KAT_TEK, BKNA_ODA, EUROSTAT, HANE_BUYUKLUGU_2025, IGD_KONUT_M2, sayi

KOK = Path(__file__).resolve().parents[3]
GRI = "#9c988f"
plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "font.size": 9, "text.color": YAZI,
                     "axes.edgecolor": YAZI2, "axes.labelcolor": YAZI2, "xtick.color": YAZI2, "ytick.color": YAZI2})


def oda_il_paneli():
    """İl tablolarından Türkiye oda dağılımı [H]: il payları 2025 hane sayısıyla ağırlıklı (2021 hane sayısı
    panelde yok; ağırlık farkı küçük sayıldı [V])."""
    yol = KOK / "03_VERI" / "ham" / "tuik" / "il_paneli_ham_2025.csv"
    with open(yol, encoding="utf-8") as f:
        r = list(csv.DictReader(f))
    w = [float(x["hane_sayisi_2025"]) for x in r]
    W = sum(w)
    out = {}
    for k, ad in (("oda12_pct", "1–2"), ("oda3_pct", "3"), ("oda4_pct", "4"), ("oda5p_pct", "5+")):
        out[ad] = sum(float(x[k]) * wi for x, wi in zip(r, w)) / W
    out["ort_oda"] = sum(float(x["ort_oda_2021"]) * wi for x, wi in zip(r, w)) / W
    out["kisi_basi_oda"] = sum(float(x["kisi_basi_oda_2021"]) * wi for x, wi in zip(r, w)) / W
    return out


def eurostat():
    yol = KOK / "05_ANALIZ" / "sonuclar" / "stres_turkiye_ab.csv"
    with open(yol, encoding="utf-8") as f:
        r = {x["gosterge"]: x for x in csv.DictReader(f)}
    sec = [("Aşırı kalabalık konutta yaşayan nüfus (%)", "Aşırı kalabalık konut"),
           ("Aşırı kalabalık konutta yaşayan 18 yaş altı (%)", "Aşırı kalabalık (18 yaş altı)"),
           ("Konutunu fazla karanlık bulan nüfus (%)", "Konutunu karanlık bulan"),
           ("Komşudan ya da sokaktan gürültü sorunu (%)", "Komşu ya da sokak gürültüsü")]
    return [(ad, float(r[k]["tr_son"]), float(r[k]["ab27_ayni_yil"]), r[k]["tr_son_yil"], r[k]["veri_seti"])
            for k, ad in sec]


def calistir():
    il = oda_il_paneli()
    eu = eurostat()
    sat = []
    for k, v in BKNA_KAT_TEK.items():
        sat.append(("Hanelerin oturduğu binanın kat sayısı: " + k, v, "% hane", 2021, "TÜİK BKNA 2021 (45870)", "D"))
    sat.append(("3 ve daha çok katlı binada oturan hane", round(sum(v for k, v in BKNA_KAT_TEK.items()
                                                                     if k not in ("1", "2")), 1), "% hane", 2021,
                "TÜİK BKNA 2021; hesaplama", "H"))
    for k, v in BKNA_ODA.items():
        sat.append((f"Konutun oda sayısı: {k} (bülten)", v, "% hane", 2021, "TÜİK BKNA 2021 bülten metni", "İ"))
    for k in ("1–2", "3", "4", "5+"):
        sat.append((f"Konutun oda sayısı: {k} (il tabloları, hane ağırlıklı)", round(il[k], 1), "% hane", 2021,
                    "TÜİK BKNA 2021 il tabloları; 2025 hane ağırlığı", "H"))
    sat.append(("Ortalama oda sayısı (il tabloları, hane ağırlıklı)", round(il["ort_oda"], 2), "oda", 2021,
                "TÜİK BKNA 2021 il tabloları", "H"))
    sat += [("3+ katlı binadaki hanelerden asansörsüz binada oturan", BKNA_DIGER["asansorsuz_3plus"], "%", 2021,
             "TÜİK BKNA 2021", "D"),
            ("Otoparksız binada oturan hane", BKNA_DIGER["otoparksiz"], "% hane", 2021, "TÜİK BKNA 2021", "D"),
            ("Konutunun sahibi olan hane", BKNA_DIGER["ev_sahibi"], "% hane", 2021, "TÜİK BKNA 2021", "D"),
            ("Kiracı hane", BKNA_DIGER["kiraci"], "% hane", 2021, "TÜİK BKNA 2021", "D"),
            ("2001 ve sonrası yapılmış binada oturan hane", BKNA_DIGER["insa_2001_sonra"], "% hane", 2021,
             "TÜİK BKNA 2021", "D"),
            ("Ortalama hanehalkı büyüklüğü", HANE_BUYUKLUGU_2025, "kişi", 2025, "TÜİK İstatistiklerle Aile 2025", "D"),
            ("Kişi başına oda (Türkiye)", EUROSTAT["kisi_basi_oda_TR_2025"], "oda/kişi", 2025, "Eurostat ilc_lvho03",
             "D"),
            ("Kişi başına oda (AB-27)", EUROSTAT["kisi_basi_oda_AB_2025"], "oda/kişi", 2025, "Eurostat ilc_lvho03",
             "D"),
            ("Kendine ait odası olan çocuk (0–17)", 34.0, "%", 2022, "TÜİK Türkiye Çocuk Araştırması 2022", "D"),
            ("Satılan konutların ortalama büyüklüğü (daire)", IGD_KONUT_M2["daire_2025"], "m²", 2025,
             "İstanbul Gayrimenkul Değerleme; Hürriyet Daily News 17.05.2026", "İ"),
            ("Yapı ruhsatı verilen daire", 1_111_852, "daire", 2025, "TÜİK Yapı İzin İstatistikleri 2025; Posta "
                                                                     "aktarımı (27.10.2026'da okundu)", "İ"),
            ("Yapı kullanma izni verilen daire", 673_575, "daire", 2025, "TÜİK Yapı İzin İstatistikleri 2025; Posta "
                                                                         "aktarımı", "İ")]
    for ad, tr, ab, yil, vs in eu:
        sat.append((ad + " (Türkiye)", tr, "% nüfus", int(yil), f"Eurostat {vs}", "D"))
        sat.append((ad + " (AB-27)", ab, "% nüfus", int(yil), f"Eurostat {vs}", "D"))
    with open(CIKTI / "turkiye_konut_durumu.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["gosterge", "deger", "birim", "yil", "kaynak", "isaret"])
        w.writerows(sat)
    # --- grafik ------------------------------------------------------------------------------
    fig, axs = plt.subplots(1, 3, figsize=(16, 5.6), dpi=150, gridspec_kw=dict(width_ratios=[1.15, 0.75, 1.1]))
    fig.patch.set_facecolor(ZEMIN)
    ax = axs[0]
    ks = list(BKNA_KAT_TEK.keys())
    vs = [BKNA_KAT_TEK[k] for k in ks]
    ax.bar(range(len(ks)), vs, color=[GRI if k in ("1", "2") else MAVI for k in ks], width=0.72, edgecolor=ZEMIN,
           linewidth=2)
    for i, v in enumerate(vs):
        ax.text(i, v + 0.3, sayi(v, 1), ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(ks)))
    ax.set_xticklabels(ks)
    ax.set_xlabel("binanın kat sayısı")
    ax.set_ylabel("% hane")
    uc = sum(v for k, v in BKNA_KAT_TEK.items() if k not in ("1", "2"))
    ax.set_title(f"Hanelerin oturduğu binanın kat sayısı (2021)\n%{sayi(uc, 1)}'i 3 ve daha çok katlı binada; "
                 f"bunların %{sayi(BKNA_DIGER['asansorsuz_3plus'], 1)}'i asansörsüz", loc="left", fontsize=10,
                 fontweight="bold", color=YAZI)
    ax = axs[1]
    oks = ["1–2", "3", "4", "5+"]
    ovs = [il[k] for k in oks]
    ax.bar(range(4), ovs, color=[MAVI if k == "4" else GRI for k in oks], width=0.68, edgecolor=ZEMIN, linewidth=2)
    for i, v in enumerate(ovs):
        ax.text(i, v + 0.6, sayi(v, 1), ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(4))
    ax.set_xticklabels([f"{k} oda" for k in oks])
    ax.set_ylabel("% hane")
    ax.set_title("Konutun oda sayısı (2021)\n4 oda = 3+1; ortalama hane 3,08 kişi (2025)", loc="left", fontsize=10,
                 fontweight="bold", color=YAZI)
    ax = axs[2]
    ys = list(range(len(eu)))[::-1]
    for y, (ad, tr, ab, yil, _) in zip(ys, eu):
        ax.barh(y + 0.19, tr, height=0.36, color=MAVI, edgecolor=ZEMIN, linewidth=1.5)
        ax.barh(y - 0.19, ab, height=0.36, color=GRI, edgecolor=ZEMIN, linewidth=1.5)
        ax.text(tr + 0.6, y + 0.19, f"TR {sayi(tr, 1)}", va="center", fontsize=8)
        ax.text(ab + 0.6, y - 0.19, f"AB {sayi(ab, 1)}", va="center", fontsize=8, color=YAZI2)
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{ad.replace(' konut', chr(10) + 'konut').replace(' (18', chr(10) + '(18').replace(' ya da', chr(10) + 'ya da')} ({yil})"
                        for ad, _, _, yil, _ in eu], fontsize=8.5)
    ax.set_xlabel("% nüfus")
    ax.set_xlim(0, 62)
    ax.set_title("Türkiye ve AB-27 (Eurostat EU-SILC)", loc="left", fontsize=10, fontweight="bold", color=YAZI)
    for a in axs:
        for k in ("top", "right"):
            a.spines[k].set_visible(False)
        a.set_facecolor(ZEMIN)
    fig.text(0.01, 0.015, "Kaynak: TÜİK Bina ve Konut Nitelikleri Araştırması 2021 (bülten 45870; oda dağılımı il "
                          "tablolarından, hane ağırlıklı [H]); Eurostat ilc_lvho05a, ilc_mdho04, ilc_mddw01 [D]. "
                          "Gri: AB ya da 1–2 katlı / diğer oda sınıfları.", fontsize=7.5, color=YAZI2)
    from matplotlib.ticker import FuncFormatter
    for a in axs:
        f = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
        a.yaxis.set_major_formatter(f) if a is not axs[2] else a.xaxis.set_major_formatter(f)
    fig.subplots_adjust(left=0.05, right=0.985, top=0.82, bottom=0.16, wspace=0.5)
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"turkiye_konut_durumu.{uz}", facecolor=ZEMIN)
    plt.close(fig)
    return il, eu


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    il, eu = calistir()
    print(il)
