"""
Ölçeklenebilir şehir — kademe modeli (komşuluk birimi → mahalle → semt → şehir → bölge)
=====================================================================================
Her kademe bir alt kademenin katlarıdır; donatı, altyapı ve yönetişim aynı kuralla büyür.
Girdi : 07_TASARIM_CIZIM/model_mahalle_v2/metrikler.csv        model mahalle v2.1 (temel birim)
        05_ANALIZ/sonuclar/enerji_kademe.csv                    Rapor 18 (enerji, iklime göre üç ilçe)
        05_ANALIZ/sonuclar/israf_su_il.csv, 09_RAPORLAR/19_*    Rapor 19 (su ve atık)
        05_ANALIZ/sonuclar/ekonomi_kademe.csv                   Rapor 20 (varsa: ekonomi araçları)
        07_TASARIM_CIZIM/olceklenebilir_sehir/parametreler.csv  donatı kuralları ve kişi başı değerler (kaynaklı)
Çıktı : 07_TASARIM_CIZIM/olceklenebilir_sehir/kademe_tablosu.csv, kademe_donatilar.csv, kademe_tablosu.png|svg
"""
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[3]
CIK = KOK / "07_TASARIM_CIZIM" / "olceklenebilir_sehir"
SON = KOK / "05_ANALIZ" / "sonuclar"
YAZI, YAZI_2, ZEMIN, IZGARA = "#0b0b0b", "#52514e", "#fcfcfb", "#e8e7e3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN})


def tr(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


# --- 1. kademeler: model mahalleden türetilir -------------------------------------------------------------------
met = pd.read_csv(KOK / "07_TASARIM_CIZIM" / "model_mahalle_v2" / "metrikler.csv").drop_duplicates("gosterge").set_index("gosterge")
NUF_MAH = float(met.loc["Nüfus", "v2_degeri"])
KB = met[met.kategori == "Komşuluk birimi"]
NUF_KB = KB.v2_degeri.mean() * 3.2  # konut × 3,2 kişi/hane (model varsayımı)
KADEME = [("Komşuluk birimi", NUF_KB, None), ("Mahalle", NUF_MAH, 1), ("Semt", 5 * NUF_MAH, 5),
          ("Şehir", 30 * NUF_MAH, 30), ("Bölge", 180 * NUF_MAH, 180)]
P = pd.read_csv(CIK / "parametreler.csv").set_index("kod")
par = lambda k: float(P.loc[k, "deger"])

# --- 2. donatılar: eşik kuralları --------------------------------------------------------------------------------
D = pd.read_csv(CIK / "donatilar.csv")  # ad, kademe, kisi_basina (bir birimin hizmet nüfusu), kaynak
don = []
for _, r in D.iterrows():
    for ad, nuf, _m in KADEME:
        if KADEME.index((ad, nuf, _m)) < [k[0] for k in KADEME].index(r.kademe):
            continue
        n = max(1, round(nuf / r.hizmet_nufusu)) if r.hizmet_nufusu > 0 else 1
        don.append({"donati": r.donati, "ilk_kademe": r.kademe, "kademe": ad, "adet": n, "hizmet_nufusu": r.hizmet_nufusu,
                    "kaynak": r.kaynak})
DON = pd.DataFrame(don)
DON.to_csv(CIK / "kademe_donatilar.csv", index=False, encoding="utf-8")

# --- 3. altyapı: enerji (Rapor 18), su ve atık (Rapor 19) ----------------------------------------------------------
E = pd.read_csv(SON / "enerji_kademe.csv")
E = E[E.kademe.str.match(r"^\d (mahalle|semt|şehir|bölge)$")]
E["kad"] = E.kademe.str.split(" ").str[1].str.capitalize().replace({"Şehir": "Şehir", "Bölge": "Bölge"})
su = pd.read_csv(SON / "israf_su_il.csv")
su_tr = su[su.il != "Türkiye"]
NUF_TR = pd.read_csv(KOK / "03_VERI" / "islenmis" / "ilce_paneli_genis.csv").nufus_2024.sum()
SU_KB = su_tr.dagitilan_bin_m3_2024.sum() * 1000 * 1000 / NUF_TR / 365  # L/kişi/gün, şebekeye verilen (belediye)
KAYIP = 1 - su_tr.dagitilan_bin_m3_2024.sum() / su_tr.cekilen_bin_m3_2024.sum()
satir = []
for ad, nuf, _m in KADEME:
    s = {"kademe": ad, "nufus": round(nuf), "alan_ha": nuf / par("brut_yogunluk")}
    e = E[E.kad == ad]
    if len(e):
        s["elektrik_kwh_kisi_min"], s["elektrik_kwh_kisi_max"] = e.elektrik_kisi_basi_kwh.min(), e.elektrik_kisi_basi_kwh.max()
        s["yerinde_karsilama_min"], s["yerinde_karsilama_max"] = e.yerinde_karsilama.min(), e.yerinde_karsilama.max()
        s["yerinde_kis_min"], s["yerinde_kis_max"] = e.yerinde_karsilama_kis.min(), e.yerinde_karsilama_kis.max()
        s["depolama_kwh_kisi_max"] = e.depolama_kwh_kisi.max()
    s["su_m3_gun_bugun"] = nuf * SU_KB / 1000 / (1 - KAYIP)
    s["su_m3_gun_hedef"] = nuf * SU_KB / 1000 / (1 - par("su_kayip_hedef"))
    s["atik_ton_gun"] = nuf * par("atik_kg_kisi_gun") / 1000
    s["geri_kazanim_ton_gun_hedef"] = s["atik_ton_gun"] * par("geri_kazanim_hedef")
    s["gida_israf_ton_yil_bugun"] = nuf * par("gida_israf_kg_kisi_yil") / 1000
    satir.append(s)
T = pd.DataFrame(satir)
T["yonetisim"] = ["Komşuluk meclisi, ortak avlu ve bahçe yönetimi", "Muhtarlık + mahalle meclisi, mahalle bütçesi",
                  "Semt meclisi (mahalle temsilcileri), semt merkezi işletmesi", "Belediye", "Bölge planlama ve kalkınma birliği"]
T["ulasim"] = ["Yürüme, kapı önü", "Yürüme ≤ 400 m, bisiklet", "Tramvay ya da BRT durağı, 15 dk yürüme",
               "Raylı sistem (iki hat), yük treni OSB'ye", "Bölgesel tren halkası, hızlı tren, havalimanı ≤ 60 dk"]
EK = SON / "ekonomi_kademe.csv"
if EK.exists():
    ek = pd.read_csv(EK)
    print("ekonomi_kademe sütunları:", list(ek.columns))
T.to_csv(CIK / "kademe_tablosu.csv", index=False, encoding="utf-8")
print(f"Şebekeye verilen su: {SU_KB:.0f} L/kişi/gün; kayıp-kaçak %{100 * KAYIP:.1f}")
print(T.round(1).to_string(index=False))
print(DON.pivot_table(index="donati", columns="kademe", values="adet", aggfunc="first")[[k[0] for k in KADEME]].to_string())

# --- 4. ekonomi araçları (Rapor 20) ve tek sayfalık kademe tablosu ----------------------------------------------
KOLON = {"Mahalle": "mahalle", "Semt": "semt", "Şehir": "sehir", "Bölge": "bolge"}
if EK.exists():
    for ad, k in KOLON.items():
        rol = ek[k].fillna("—").astype(str).str.split(":").str[0]
        T.loc[T.kademe == ad, "ekonomi_arac_sayisi"] = int(rol.str.contains("K|U|H").sum())
    T.to_csv(CIK / "kademe_tablosu.csv", index=False, encoding="utf-8")


def kisalt(s):
    return s.split(" (")[0]


ADLAR = [k[0] for k in KADEME]
yeni = {a: [kisalt(x) for x in D[D.kademe == a].donati] for a in ADLAR}
ek_arac = {a: [] for a in ADLAR}
if EK.exists():
    for _, r in ek.iterrows():
        for a, k in KOLON.items():
            v = str(r[k]).strip()
            rol = v.split(":")[0].strip() if ":" in v else ""
            # Rapor 20 rol sözlüğü: K karar ve kural, U uygulama ve tahsil, H hizmet ve mekân, V veri ve izleme
            if any(h in rol for h in ("K", "U", "H")):
                ek_arac[a].append(f"{rol} · {kisalt(r.arac).split(':')[0]}")
SATIR = []
SATIR.append(("Nüfus", [tr(r.nufus) for _, r in T.iterrows()]))
SATIR.append(("Konut ağırlıklı doku", [f"{tr(r.alan_ha)} ha" for _, r in T.iterrows()]))
SATIR.append(("Bu kademede eklenen donatı", ["\n".join(yeni[a][:7]) + ("\n…" if len(yeni[a]) > 7 else "") for a in ADLAR]))
SATIR.append(("Elektrik talebi\n(kWh/kişi·yıl)", ["—" if pd.isna(r.get("elektrik_kwh_kisi_min")) else
              f"{tr(r.elektrik_kwh_kisi_min)}–{tr(r.elektrik_kwh_kisi_max)}" for _, r in T.iterrows()]))
SATIR.append(("Yerinde karşılama\nyıllık / kış", ["—" if pd.isna(r.get("yerinde_karsilama_min")) else
              f"%{tr(100 * r.yerinde_karsilama_min)}–{tr(100 * r.yerinde_karsilama_max)} / %{tr(100 * r.yerinde_kis_min)}–{tr(100 * r.yerinde_kis_max)}"
              for _, r in T.iterrows()]))
SATIR.append(("Su (m³/gün)\nbugün → kayıp %15", [f"{tr(r.su_m3_gun_bugun)} → {tr(r.su_m3_gun_hedef)}" for _, r in T.iterrows()]))
SATIR.append(("Belediye atığı (t/gün)\ngeri kazanım hedefi", [f"{tr(r.atik_ton_gun, 1)} → {tr(r.geri_kazanim_ton_gun_hedef, 1)}" for _, r in T.iterrows()]))
SATIR.append(("Gıda israfı bugün (t/yıl)", [tr(r.gida_israf_ton_yil_bugun) for _, r in T.iterrows()]))
SATIR.append(("Ulaşım", list(T.ulasim)))
SATIR.append(("Yönetişim", list(T.yonetisim)))
SATIR.append(("Ekonomi araçları\n(K kural, U uygulama\nve tahsil, H hizmet)", ["\n".join(ek_arac[a][:6]) + ("\n…" if len(ek_arac[a]) > 6 else "") if ek_arac[a] else "—"
                                                      for a in ADLAR]))

import textwrap

fig, ax = plt.subplots(figsize=(17, 12.5))
ax.set_axis_off()
x0, w0, wc = 0.0, 0.16, 0.168
yuk = [0.05 if i in (0, 1, 3, 4, 5, 6, 7) else 0.075 for i in range(len(SATIR))]
yuk[2], yuk[-1] = 0.17, 0.18
toplam = sum(yuk) + 0.06
y = 1 - 0.06
for j, a in enumerate(ADLAR):
    ax.add_patch(plt.Rectangle((w0 + j * wc, y), wc - 0.004, 0.05, color="#2a78d6" if j else "#86b6ef", transform=ax.transAxes))
    ax.text(w0 + j * wc + wc / 2, y + 0.025, a, ha="center", va="center", fontsize=10.5, fontweight="bold",
            color="white" if j else YAZI, transform=ax.transAxes)
for i, (etiket, degerler) in enumerate(SATIR):
    y -= yuk[i]
    renk = "#f3f2ee" if i % 2 == 0 else ZEMIN
    ax.add_patch(plt.Rectangle((0, y), w0 + 5 * wc, yuk[i], color=renk, transform=ax.transAxes, zorder=0))
    ax.text(0.005, y + yuk[i] / 2, etiket, ha="left", va="center", fontsize=8.8, fontweight="bold", color=YAZI, transform=ax.transAxes)
    for j, v in enumerate(degerler):
        metin = "\n".join(textwrap.fill(s, 30) for s in str(v).split("\n"))
        ax.text(w0 + j * wc + 0.006, y + yuk[i] / 2, metin, ha="left", va="center", fontsize=7.8, color=YAZI_2,
                transform=ax.transAxes, linespacing=1.25)
ax.set_ylim(0, 1)
fig.suptitle("Ölçeklenebilir şehir: beş kademede donatı, altyapı, yönetişim ve ekonomi", x=0.01, ha="left", fontsize=14,
             fontweight="bold", color=YAZI)
fig.text(0.01, 0.935, "Temel birim model mahalle v2.1. Enerji: Rapor 18 (üç iklim: Antakya, Fatih, Kocasinan; aralık). Su, atık, gıda: Rapor 19. "
         "Ekonomi araçları: Rapor 20. Donatı kuralları: donatilar.csv.", fontsize=8.8, color=YAZI_2)
fig.text(0.01, 0.01, "Kod: 07_TASARIM_CIZIM/olceklenebilir_sehir/kod/kademe_modeli.py · tablolar: kademe_tablosu.csv, kademe_donatilar.csv",
         fontsize=7.5, color=YAZI_2)
fig.subplots_adjust(left=0.01, right=0.99, top=0.91, bottom=0.03)
for uz in ("png", "svg"):
    fig.savefig(CIK / f"kademe_tablosu.{uz}", dpi=170)
print("kademe_tablosu yazıldı")
