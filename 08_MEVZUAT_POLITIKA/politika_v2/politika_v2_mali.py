"""
Faz 5 · Rapor 2 — Politika paketi v2: mali etki hesapları
=========================================================
Üç yeni öneri grubunun sayısal etkisi. Statik hesap; davranış tepkisi yok, bütün varsayımlar [V] ile işaretli.

1. Arsa değer vergisi (öneri E1–E5): 2029–2033 kademeli geçiş. Her yıl arsa değer vergisi (AVD) hasılatı kadar genel
   KDV indirimi. İki denge tanımı:
     A · hanehalkı-nötr: hanehalkının KDV kaybı = AVD (Rapor 20'nin S3 hesabı; hanehalkı dışı KDV ihmal)
     B · toplam-nötr: toplam KDV kaybı = AVD; hanehalkı dışı KDV (%25 [V]) aynı oranda düşer
   Dilimlere net etki Rapor 20'nin S3C tasarımıyla: konut + işletme arsası, alt iki dilimde tek konut muaf.
2. Yerel kaynak (B3, B4, E5): AVD'nin şehir genel bütçesi / semt bütçesi / mahalle bütçesi arasında bölünmesi
   (%60 / %25 / %15 [V, öneri]) ve merkezi vergi paylarıyla denkleştirme.
3. Karma kullanım (P6, O4): zemin kat dükkânının Otopark Yönetmeliği Ek-1'e göre otopark yükü; model mahalle v2.1.

Girdi : 05_ANALIZ/kod/ekonomi_dagilim.py (fonksiyonları için çalıştırılır; kendi çıktılarını aynen yeniden yazar),
        05_ANALIZ/sonuclar/ekonomi_kademe_parametre.csv, ekonomi_yerel_gelirler.csv,
        08_MEVZUAT_POLITIKA/finansman_modeli/varsayimlar.csv (M6), 07_TASARIM_CIZIM/model_mahalle_v2/metrikler.csv
Çıktı : 08_MEVZUAT_POLITIKA/politika_v2/avd_gecis.csv, yerel_kaynak.csv, karma_kullanim_otopark.csv,
        politika_v2_mali.png|svg
Çalıştırma: PYTHONIOENCODING=utf-8 python 08_MEVZUAT_POLITIKA/politika_v2/politika_v2_mali.py
            (önce 05_ANALIZ/kod/ekonomi_veri.py; ekonomi_dagilim.py bu betiğin içinde çalışır)
"""
import contextlib
import io
import runpy
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
SON = KOK / "05_ANALIZ" / "sonuclar"
CIK = Path(__file__).resolve().parent
MAVI, TURUNCU, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
YAZI, YAZI_2, YAZI_3, ZEMIN, IZGARA, GRI = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e8e7e3", "#b9b8b3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "axes.edgecolor": YAZI_3, "axes.labelcolor": YAZI_2, "xtick.color": YAZI_2, "ytick.color": YAZI_2,
                     "axes.titlesize": 10, "svg.fonttype": "none"})


def tr(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


# ---------------------------------------------------------------- 1. arsa değer vergisi geçişi
# Rapor 20'nin dağılım modeli; çıktısı gizlenir (kendi CSV'lerini birebir yeniden yazar)
tampon = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
with contextlib.redirect_stdout(tampon):
    D = runpy.run_path(str(KOK / "05_ANALIZ" / "kod" / "ekonomi_dagilim.py"), run_name="ekonomi_dagilim")
kdv_senaryo, oran, Q, Y_q = D["kdv_senaryo"], D["oran"], D["Q"], D["Y_q"]
GSYH, HANE_PAYI = D["GSYH_2025"], D["HANE_PAYI_KDV"]
yuk_C = 0.60 * D["konut_muaf"] + 0.40 * D["isletme"]   # S3C: dilimlerin AVD'deki payı


def genel_oran(hedef, kapsam):
    """Genel KDV oranı: kapsam × hanehalkı KDV kaybı = hedef olacak şekilde (ikiye bölme)."""
    lo, hi = 0.0, 0.20
    for _ in range(60):
        m = (lo + hi) / 2
        kayip = -kdv_senaryo("x", oran.where(oran != 0.20, m)).sum() * kapsam
        lo, hi = (lo, m) if kayip < hedef else (m, hi)
    return (lo + hi) / 2


GECIS = [(2028, 0.0), (2029, 0.001), (2030, 0.002), (2031, 0.003), (2032, 0.004), (2033, 0.005)]  # [V, öneri]
satir = []
for yil, pay in GECIS:
    avd = pay * GSYH
    r = {"yil": yil, "avd_gsyh_pct": 100 * pay, "avd_mlr_tl_2025": avd}
    for ad, kapsam in (("A", 1.0), ("B", 1 / HANE_PAYI)):
        g = genel_oran(avd, kapsam) if pay > 0 else 0.20
        net = kdv_senaryo("x", oran.where(oran != 0.20, g)) + avd * yuk_C
        r[f"kdv_genel_{ad}_pct"] = 100 * g
        r[f"hanehalki_net_{ad}_mlr"] = net.sum()
        for i, q in enumerate(Q):
            r[f"net_{ad}_dilim{i + 1}_gelire_pct"] = 100 * net[q] / Y_q[q]
    satir.append(r)
gecis = pd.DataFrame(satir)
son = gecis.iloc[-1]
assert abs(son.kdv_genel_A_pct - 100 * D["genel_yeni"]) < 0.01, "Rapor 20 S3 oranıyla tutarsız"
assert abs(son.net_A_dilim1_gelire_pct - (-0.9044)) < 0.01, "Rapor 20 S3C en yoksul dilim değeriyle tutarsız"
gecis.round(4).to_csv(CIK / "avd_gecis.csv", index=False, encoding="utf-8")
print("AVD geçişi (genel KDV oranı, A hanehalkı-nötr / B toplam-nötr):")
print(gecis[["yil", "avd_gsyh_pct", "avd_mlr_tl_2025", "kdv_genel_A_pct", "kdv_genel_B_pct",
             "net_A_dilim1_gelire_pct", "net_B_dilim1_gelire_pct", "net_B_dilim5_gelire_pct"]].round(2).to_string())

# ---------------------------------------------------------------- 2. yerel kaynak
kp = pd.read_csv(SON / "ekonomi_kademe_parametre.csv").set_index("parametre")
yg = pd.read_csv(SON / "ekonomi_yerel_gelirler.csv").set_index("yil").loc[2025]
nuf = kp.loc["nufus", "ulke"]
PAY = {"sehir_genel": 0.60, "semt": 0.25, "mahalle": 0.15}   # [V, öneri B4/E5]
avd_kisi = kp.loc["arsa_deger_vergisi_gsyh05_mn_tl", "ulke"] * 1e6 / nuf
emlak_kisi = kp.loc["emlak_vergisi_mevcut_mn_tl", "ulke"] * 1e6 / nuf
merkezi_kisi = yg.merkezi_vergi_paylari * 1e9 / nuf
butce_kisi = yg.toplam_butce_geliri * 1e9 / nuf
tuketim_kisi = kp.loc["kdv_otv_hanehalki_yuku_mn_tl", "ulke"] * 1e6 / nuf
yk = [("Bugün: emlak vergisi (bina + arsa + arazi)", emlak_kisi, "D/H"),
      ("v2: arsa değer vergisi, toplam (GSYH %0,5)", avd_kisi, "V/H"),
      ("  şehir belediyesi genel bütçesi (%60)", PAY["sehir_genel"] * avd_kisi, "V"),
      ("  semt bütçesi (%25; semt meclisinin önceliğiyle)", PAY["semt"] * avd_kisi, "V"),
      ("  mahalle bütçesi (%15; mahalle meclisinin önceliğiyle)", PAY["mahalle"] * avd_kisi, "V"),
      ("Bugün: merkezi vergi payları (5779 s. Kanun)", merkezi_kisi, "D/H"),
      ("Bugün: mahalli idare toplam bütçe geliri", butce_kisi, "D/H"),
      ("Bugün: hanehalkının ödediği KDV + ÖTV", tuketim_kisi, "H")]
yerel = pd.DataFrame(yk, columns=["kalem", "tl_kisi_yil", "isaret"])
for kad in ("mahalle", "semt", "sehir"):
    yerel[f"{kad}_mn_tl"] = yerel.tl_kisi_yil * kp.loc["nufus", kad] / 1e6
oranlar = pd.DataFrame([
    ("AVD / merkezi vergi payları (denkleştirme için payların azalması)", avd_kisi / merkezi_kisi),
    ("Semt + mahalle bütçesi / mahalli idare toplam bütçe geliri", (PAY["semt"] + PAY["mahalle"]) * avd_kisi / butce_kisi),
    ("Tüketim vergisi / yerel mülk vergisi, bugün (kat)", tuketim_kisi / emlak_kisi),
    ("Tüketim vergisi / yerel mülk vergisi, v2 A (kat)", (tuketim_kisi - avd_kisi) / (emlak_kisi + avd_kisi))],
    columns=["oran", "deger"])
yerel.round(1).to_csv(CIK / "yerel_kaynak.csv", index=False, encoding="utf-8")
oranlar.round(4).to_csv(CIK / "yerel_kaynak_oranlar.csv", index=False, encoding="utf-8")
print("\nYerel kaynak (TL/kişi·yıl, 2025):")
print(yerel.round(0).to_string())
print(oranlar.round(3).to_string())

# ---------------------------------------------------------------- 3. karma kullanım: zemin kat dükkânının otopark yükü
va = pd.read_csv(KOK / "08_MEVZUAT_POLITIKA" / "finansman_modeli" / "varsayimlar.csv").set_index("anahtar")["deger"]
met = pd.read_csv(KOK / "07_TASARIM_CIZIM" / "model_mahalle_v2" / "metrikler.csv")
n_birim = float(met.loc[met.gosterge.str.startswith("Zemin kat konut dışı birim"), "v2_1"].iloc[0])
BIRIM_M2 = 70.0                                   # model mahalle metrikler: "≈ 70 m²" [H]
A, B = float(va["emlak_degeri_m2"]), float(va["bm_IIIA"])
bedel_yer = (A + B) * 20 * 1.0                     # Otopark Yön. md. 12(11): (A + B) × 20 × Y; Y = 1 [V, M6 ile aynı]
bodrum_yer = float(va["bodrum_m2_yer"]) * B * float(va["bm_kar_haric"]) * float(va["bodrum_ek"])
yer_birim = BIRIM_M2 / 50                          # Ek-1: dükkân 50 m²'ye 1 [D]
kk = []
for fiyat_ad in ("fiyat_tr", "fiyat_istanbul"):
    deger = BIRIM_M2 * float(va[fiyat_ad]) * float(va["ticari_carpan"])
    for yol, tl_yer in (("bedel", bedel_yer), ("bodrum", bodrum_yer)):
        yuk = yer_birim * tl_yer
        kk.append({"fiyat": fiyat_ad, "fiyat_tl_m2": float(va[fiyat_ad]), "karsilama": yol, "birim_m2": BIRIM_M2,
                   "otopark_yer_birim": yer_birim, "tl_yer": tl_yer, "yuk_tl_birim": yuk, "birim_degeri_tl": deger,
                   "yuk_birim_degerine_pct": 100 * yuk / deger, "model_mahalle_birim": n_birim,
                   "model_mahalle_yer": n_birim * yer_birim, "model_mahalle_yuk_mn_tl": n_birim * yuk / 1e6,
                   "O4_sonrasi_yuk_tl": 0.0})
karma = pd.DataFrame(kk)
karma.round(2).to_csv(CIK / "karma_kullanim_otopark.csv", index=False, encoding="utf-8")
print("\nZemin kat dükkânı (70 m²) otopark yükü:")
print(karma[["fiyat", "karsilama", "yuk_tl_birim", "birim_degeri_tl", "yuk_birim_degerine_pct",
             "model_mahalle_yer", "model_mahalle_yuk_mn_tl"]].round(1).to_string())

# ---------------------------------------------------------------- 4. grafik
fig = plt.figure(figsize=(10.4, 4.6))
ax1 = fig.add_axes([0.06, 0.16, 0.38, 0.58])
ax2 = fig.add_axes([0.56, 0.16, 0.41, 0.58])

for ad, renk, etiket in (("A", MAVI, "A · hanehalkı-nötr"), ("B", TURUNCU, "B · toplam-nötr")):
    ax1.plot(gecis.yil, gecis[f"kdv_genel_{ad}_pct"], color=renk, lw=2, marker="o", ms=5, label=etiket,
             markeredgecolor=ZEMIN, markeredgewidth=1.5)
    ax1.annotate(f"%{tr(gecis[f'kdv_genel_{ad}_pct'].iloc[-1])}", (gecis.yil.iloc[-1], gecis[f"kdv_genel_{ad}_pct"].iloc[-1]),
                 xytext=(7, 0), textcoords="offset points", va="center", fontsize=8.5, color=YAZI)
for _, r in gecis.iloc[1:].iterrows():
    ax1.annotate(f"AVD %{tr(r.avd_gsyh_pct)}", (r.yil, 14.6), ha="center", fontsize=7.2, color=YAZI_3)
ax1.set_ylim(14.3, 20.6)
ax1.set_xlim(2027.6, 2033.9)
ax1.set_xticks(gecis.yil)
ax1.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"%{tr(v, 0)}"))
ax1.set_title("Genel KDV oranı, arsa değer vergisi (GSYH'nin %'si) arttıkça", loc="left", color=YAZI, fontsize=9.5)
ax1.legend(loc="upper right", frameon=False, fontsize=8)
for s in ("top", "right"):
    ax1.spines[s].set_visible(False)
ax1.spines["left"].set_color(IZGARA)
ax1.grid(axis="y", color=IZGARA, lw=0.7)
ax1.set_axisbelow(True)
ax1.tick_params(length=0)

satirlar = [("Bugün\nemlak vergisi", [(emlak_kisi, GRI, "")]),
            ("v2 · arsa\ndeğer vergisi", [(PAY["sehir_genel"] * avd_kisi, MAVI, "şehir"),
                                          (PAY["semt"] * avd_kisi, TURUNCU, "semt"),
                                          (PAY["mahalle"] * avd_kisi, AQUA, "mahalle")])]
for y, (ad, parcalar) in enumerate(reversed(satirlar)):
    x0 = 0.0
    for deger, renk, et in parcalar:
        ax2.barh(y, deger, left=x0, height=0.5, color=renk, edgecolor=ZEMIN, linewidth=2)
        if et:
            ax2.text(x0 + deger / 2, y, f"{et}\n{tr(deger, 0)}", ha="center", va="center", fontsize=7.8, color=YAZI)
        x0 += deger
    ax2.text(x0 + 60, y, f"{tr(x0, 0)} TL", va="center", fontsize=8.5, color=YAZI, fontweight="bold")
ax2.set_yticks(range(len(satirlar)))
ax2.set_yticklabels([s[0] for s in reversed(satirlar)])
ax2.set_xlim(0, avd_kisi * 1.18)
ax2.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: tr(v, 0)))
ax2.set_title("Yerel mülk vergisi, kişi başı TL/yıl (2025 fiyatları)", loc="left", color=YAZI, fontsize=9.5)
for s in ("top", "right", "left"):
    ax2.spines[s].set_visible(False)
ax2.grid(axis="x", color=IZGARA, lw=0.7)
ax2.set_axisbelow(True)
ax2.tick_params(length=0)

fig.text(0.012, 0.965, "Arsa değer vergisi: KDV'den arsaya kademeli kayış ve yerelde kalan kaynak", fontsize=12.5,
         fontweight="bold", color=YAZI, va="top")
fig.text(0.012, 0.895,
         "Soldaki iki çizgi iki denge tanımı: A'da hanehalkının KDV kaybı AVD'ye eşit (Rapor 20), B'de toplam KDV kaybı. "
         "Sağda AVD'nin önerilen bölünmesi: %60 şehir, %25 semt, %15 mahalle.",
         fontsize=8.6, color=YAZI_2, va="top", wrap=True)
fig.text(0.012, 0.02, "Kaynak: Rapor 20 dağılım modeli (ekonomi_dagilim.py), Muhasebat mahalli idareler 2025, "
         "politika_v2_mali.py. Statik hesap, davranış tepkisi yok.", fontsize=7.2, color=YAZI_3)
for uz in ("png", "svg"):
    fig.savefig(CIK / f"politika_v2_mali.{uz}", dpi=200)
print("\nYazıldı:", ", ".join(p.name for p in sorted(CIK.glob("*")) if p.suffix in (".csv", ".png", ".svg")))
