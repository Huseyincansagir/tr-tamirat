"""
Konut rehberi — 5 kişilik hane için karşılaştırma: tipik 3+1 daire ile önerilen tipler
=====================================================================================
Girdi: her tip modülünün ciz() çıktısındaki özet sözlük (oz). Çıktılar:
  karsilastirma.csv · karsilastirma.png/svg (küçük çoklu çubuk grafik) ·
  karsilastirma_ilke_matrisi.png/svg (tip × ilke, ✓ ≈ ✗)

Maliyet "kaba"dır [V]: yapım (2026 tebliği, kâr hariç) + asansör payı + otopark + peyzaj; arsa
ayrı bir aralık olarak gösterilir (5.000–25.000 TL/m² [V]). Malzeme farkları Rapor 16'da.
"""

from __future__ import annotations

import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from cizim import AQUA, CIKTI, MAVI, SARI, TURUNCU, YAZI, YAZI2, ZEMIN, ton
from degerlendirme import olcut_satirlari
from veri import (ARSA_TL_M2, BOLGESEL_OTOPARK_HANE, KAR_HARIC, OLCUT, OTOPARK_BM, OTOPARK_YER_M2, PEYZAJ_M2, sayi)

GRI = "#9c988f"
SIRA = ["R", "a", "b", "c", "d", "e"]
KISA = {"R": "R · 3+1 daire (Z+7)", "a": "a · avlulu tek katlı", "b": "b · sofalı iki katlı",
        "c": "c · büyüyen sıra ev", "d": "d · çok kuşaklı avlu evi", "e": "e · Z+3 galerili blok"}
ILKELER = ["Büyüklük", "Oda", "Gün ışığı", "Havalandırma", "Güneş", "Tavan", "Toprakla temas", "Mahremiyet",
           "Sükûnet", "Depolama", "Çok kuşak", "Esneklik", "Erişim", "Su", "Deprem", "Sessizlik", "Isıl konfor"]
PUAN = {"✓": 2, "≈": 1, "✗": 0}

plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "font.size": 9, "text.color": YAZI,
                     "axes.edgecolor": YAZI2, "axes.labelcolor": YAZI2, "xtick.color": YAZI2, "ytick.color": YAZI2})


def satir(oz):
    """Bir tipin karşılaştırma satırı [H]."""
    otopark_yer = oz.get("otopark_yer", BOLGESEL_OTOPARK_HANE)
    otopark = otopark_yer * OTOPARK_YER_M2 * OTOPARK_BM * KAR_HARIC
    acik = oz["acik_ozel"] + oz["acik_ortak"]
    peyzaj = acik * PEYZAJ_M2
    kaba = oz["yapim"] + oz["asansor"] + otopark + peyzaj
    ol = {r[0]: r[3] for r in olcut_satirlari(oz)}
    durumlar = [ol.get(i, "") for i in ILKELER]
    g = oz["gunes"]
    return dict(
        tip=oz["tip"], ad=oz["ad"], sehir=oz["sehir"], kat=oz["kat"], hane_sayisi=oz["hane_sayisi"],
        net_m2=round(oz["net"], 1), net_kisi=round(oz["net_kisi"], 1), oda=oz["oda"], yatak=oz["yatak"],
        brut_m2=round(oz["brut"], 1), dis_mekan_kisi=round(oz["acik_kisi"], 1), ozel_acik_m2=round(oz["acik_ozel"], 1),
        teras_m2=round(oz["teras"], 1), ortak_acik_m2=round(oz["acik_ortak"], 1),
        gunes_21sub_sa=round(g.get("21 Şubat", 0), 1), gunes_21ara_sa=round(g.get("21 Aralık", 0), 1),
        cam_taban_min=round(oz["pencere_min"], 3), karsit_cephe=int(oz["karsit_cephe"]),
        ic_yukseklik_m=round(oz["ic_yukseklik"], 2), esik=int(oz["esik"]), misafir_bolumu=int(oz["misafir"]),
        sukunet_odasi=int(oz["sukunet"]), depolama_pay=round(oz["depo_pay"], 3),
        esneklik=oz.get("esneklik", ""), mahremiyet=oz.get("mahremiyet", ""),
        yapim_tl=round(oz["yapim"]), asansor_tl=round(oz["asansor"]), otopark_yer=round(otopark_yer, 2),
        otopark_tl=round(otopark), peyzaj_tl=round(peyzaj), kaba_tl=round(kaba),
        kaba_net_m2_tl=round(kaba / oz["net"]), arsa_hane_m2=round(oz["arsa_hane"], 1),
        arsa_dusuk_tl=round(oz["arsa_hane"] * ARSA_TL_M2[0]), arsa_yuksek_tl=round(oz["arsa_hane"] * ARSA_TL_M2[1]),
        toplam_dusuk_tl=round(kaba + oz["arsa_hane"] * ARSA_TL_M2[0]),
        toplam_yuksek_tl=round(kaba + oz["arsa_hane"] * ARSA_TL_M2[1]),
        ilke_tam=durumlar.count("✓"), ilke_kismen=durumlar.count("≈"), ilke_yok=durumlar.count("✗"),
        ilke_puan=sum(PUAN.get(d, 0) for d in durumlar), **{f"ilke_{i}": d for i, d in zip(ILKELER, durumlar)})


def csv_yaz(satirlar, yol):
    with open(yol, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(satirlar[0].keys()))
        w.writeheader()
        for s in satirlar:
            w.writerow(s)


def _cubuk(ax, satirlar, alan, baslik, birim, esikler=(), ond=1, fmt=None):
    ys = list(range(len(satirlar)))[::-1]
    for y, s in zip(ys, satirlar):
        v = s[alan]
        ax.barh(y, v, height=0.62, color=GRI if s["tip"] == "R" else MAVI, edgecolor=ZEMIN, linewidth=2)
        ax.text(v, y, " " + (fmt(v) if fmt else sayi(v, ond)), va="center", ha="left", fontsize=8.5, color=YAZI)
    for k, (x, ad) in enumerate(esikler):
        ax.axvline(x, color=YAZI2, lw=0.8, ls=(0, (3, 2)), zorder=0)
        ha = "center" if len(esikler) == 1 else ("right" if k == 0 else "left")
        ax.text(x, len(satirlar) - 0.35, ad if ha == "center" else f" {ad} ", ha=ha, va="bottom", fontsize=7.5,
                color=YAZI2)
    ax.set_yticks(ys)
    ax.set_yticklabels([KISA[s["tip"]] for s in satirlar], fontsize=8.5)
    ax.set_title(baslik, loc="left", fontsize=10, fontweight="bold", color=YAZI, pad=16)
    ax.set_xlabel(birim, fontsize=8)
    ax.set_ylim(-0.6, len(satirlar) - 0.1)
    xmax = max(s[alan] for s in satirlar)
    ax.set_xlim(0, max(xmax * 1.28, max((x for x, _ in esikler), default=0) * 1.15))
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    ax.grid(axis="x", color="#e6e4df", lw=0.6)
    ax.set_axisbelow(True)
    ax.set_facecolor(ZEMIN)


def ciz(satirlar):
    satirlar = sorted(satirlar, key=lambda s: SIRA.index(s["tip"]))
    fig, axs = plt.subplots(2, 3, figsize=(16, 9.6), dpi=150)
    fig.patch.set_facecolor(ZEMIN)
    _cubuk(axs[0, 0], satirlar, "net_kisi", "Net alan, kişi başına", "m²/kişi (5 kişilik hane)",
           [(OLCUT["net_kisi_asgari"], "asgari 22"), (OLCUT["net_kisi_hedef"], "hedef 25")])
    _cubuk(axs[0, 1], satirlar, "dis_mekan_kisi", "Dış mekân, kişi başına", "m²/kişi (özel + ortak + teras)",
           [(OLCUT["acik_alan_kisi"], "ölçüt 10")])
    _cubuk(axs[0, 2], satirlar, "gunes_21sub_sa", "Doğrudan güneş, 21 Şubat", "saat (ana yaşam odası penceresi)",
           [(OLCUT["gunes_saat_asgari"], "asgari 1,5"), (OLCUT["gunes_saat_orta"], "orta 3")])
    _cubuk(axs[1, 0], satirlar, "cam_taban_min", "Gün ışığı: en düşük cam/taban", "oran (yaşanan odalar)",
           [(OLCUT["pencere_taban"], "1/8"), (OLCUT["pencere_taban_hedef"], "1/6")], ond=2)
    # maliyet: çubuk (arsa hariç) + arsa aralığı
    ax = axs[1, 1]
    ys = list(range(len(satirlar)))[::-1]
    for y, s in zip(ys, satirlar):
        v = s["kaba_tl"] / 1e6
        lo, hi = s["toplam_dusuk_tl"] / 1e6, s["toplam_yuksek_tl"] / 1e6
        ax.barh(y, v, height=0.62, color=GRI if s["tip"] == "R" else MAVI, edgecolor=ZEMIN, linewidth=2)
        ax.plot([v, hi], [y, y], color=TURUNCU, lw=1.6, solid_capstyle="butt")
        ax.plot([lo, lo], [y - 0.2, y + 0.2], color=TURUNCU, lw=1.6)
        ax.plot([hi, hi], [y - 0.2, y + 0.2], color=TURUNCU, lw=1.6)
        ax.text(v / 2, y, sayi(v, 2), va="center", ha="center", fontsize=8.5, color="white", fontweight="bold")
        ax.text(hi, y, f" {sayi(lo, 1)}–{sayi(hi, 1)}", va="center", ha="left", fontsize=8, color=YAZI)
    ax.set_yticks(ys)
    ax.set_yticklabels([KISA[s["tip"]] for s in satirlar], fontsize=8.5)
    ax.set_title("Kaba maliyet, hane başına", loc="left", fontsize=10, fontweight="bold", color=YAZI, pad=16)
    ax.set_xlabel("milyon TL (2026) · çubuk: yapım + asansör + otopark + peyzaj\nturuncu çizgi: arsa eklenince "
                  "(5.000–25.000 TL/m² [V])", fontsize=7.5)
    ax.set_xlim(0, max(s["toplam_yuksek_tl"] for s in satirlar) / 1e6 * 1.32)
    ax.set_ylim(-0.6, len(satirlar) - 0.1)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    ax.grid(axis="x", color="#e6e4df", lw=0.6)
    ax.set_axisbelow(True)
    ax.set_facecolor(ZEMIN)
    # ilke uyumu: ✓ ≈ ✗ yığılmış
    ax = axs[1, 2]
    for y, s in zip(ys, satirlar):
        x = 0
        for (alan, renk, isaret) in (("ilke_tam", AQUA, "✓"), ("ilke_kismen", SARI, "≈"), ("ilke_yok", TURUNCU, "✗")):
            n = s[alan]
            if n:
                ax.barh(y, n, left=x, height=0.62, color=renk, edgecolor=ZEMIN, linewidth=2)
                ax.text(x + n / 2, y, f"{isaret}{n}", va="center", ha="center", fontsize=8, color=YAZI)
            x += n
    ax.set_yticks(ys)
    ax.set_yticklabels([KISA[s["tip"]] for s in satirlar], fontsize=8.5)
    ax.set_title(f"İlke kontrol listesi ({len(ILKELER)} ilke)", loc="left", fontsize=10, fontweight="bold",
                 color=YAZI, pad=16)
    ax.set_xlabel("ilke sayısı · ✓ sağlıyor · ≈ kısmen · ✗ sağlamıyor", fontsize=8)
    ax.set_xlim(0, len(ILKELER))
    ax.set_ylim(-0.6, len(satirlar) - 0.1)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    ax.set_facecolor(ZEMIN)
    fig.text(0.012, 0.985, "5 kişilik hane için karşılaştırma: tipik 3+1 apartman dairesi (R) ve önerilen tipler (a–e)",
             fontsize=13, fontweight="bold", va="top")
    fig.text(0.012, 0.95, "Değerler çizimlerden hesaplandı [H]. R temsilî bir plandır [V]. c son durum (aşama 3), "
                          "d dubleks birimi, e üst dubleks. Gri: bugünkü tip · mavi: önerilen tipler. "
                          "Kaynak: 07_TASARIM_CIZIM/konut_rehberi/karsilastirma.csv",
             fontsize=8.5, color=YAZI2, va="top")
    from matplotlib.ticker import FuncFormatter
    for a in axs.flat:
        a.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    fig.subplots_adjust(left=0.13, right=0.985, top=0.86, bottom=0.08, wspace=0.62, hspace=0.55)
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"karsilastirma.{uz}", facecolor=ZEMIN)
    plt.close(fig)
    ilke_matrisi(satirlar)


def ilke_matrisi(satirlar):
    fig, ax = plt.subplots(figsize=(13, 5.2), dpi=150)
    fig.patch.set_facecolor(ZEMIN)
    renk = {"✓": ton(AQUA, 0.45), "≈": ton(SARI, 0.45), "✗": ton(TURUNCU, 0.35), "": "#efede8"}
    for i, s in enumerate(satirlar):
        y = len(satirlar) - 1 - i
        for j, il in enumerate(ILKELER):
            d = s[f"ilke_{il}"]
            ax.add_patch(Rectangle((j + 0.04, y + 0.06), 0.92, 0.88, fc=renk[d], ec="none"))
            ax.text(j + 0.5, y + 0.5, d or "–", ha="center", va="center", fontsize=12, color=YAZI)
        ax.text(len(ILKELER) + 0.2, y + 0.5, f"{s['ilke_puan']}/{2 * len(ILKELER)}", ha="left", va="center",
                fontsize=10, fontweight="bold")
    ax.set_xlim(0, len(ILKELER) + 1.4)
    ax.set_ylim(0, len(satirlar))
    ax.set_xticks([j + 0.5 for j in range(len(ILKELER))])
    ax.set_xticklabels(ILKELER, rotation=40, ha="right", fontsize=9)
    ax.set_yticks([len(satirlar) - 1 - i + 0.5 for i in range(len(satirlar))])
    ax.set_yticklabels([KISA[s["tip"]] for s in satirlar], fontsize=9)
    ax.tick_params(length=0)
    for k in ax.spines.values():
        k.set_visible(False)
    ax.set_facecolor(ZEMIN)
    ax.set_title("İlke kontrol listesi: ✓ sağlıyor (2) · ≈ kısmen (1) · ✗ sağlamıyor (0); sağda toplam puan [H]",
                 loc="left", fontsize=11, fontweight="bold", pad=10)
    fig.subplots_adjust(left=0.17, right=0.98, top=0.9, bottom=0.27)
    for uz in ("png", "svg"):
        fig.savefig(CIKTI / f"karsilastirma_ilke_matrisi.{uz}", facecolor=ZEMIN)
    plt.close(fig)


def calistir(ozler):
    satirlar = [satir(oz) for oz in ozler]
    satirlar = sorted(satirlar, key=lambda s: SIRA.index(s["tip"]))
    csv_yaz(satirlar, CIKTI / "karsilastirma.csv")
    ciz(satirlar)
    return satirlar
