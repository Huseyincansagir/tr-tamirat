"""
Faz 5 · Rapor 3 — Paydaş oyunu: politika paketi v2 kimi nasıl etkiler, kim destekler, kim engeller?
===============================================================================================
Plan §4.1(d)'deki paydaş oyununun ilk sürümü. Zihinsel simülasyon; sayılar yön ve büyüklük sırası için.

1. Hane paydaşlarının parasal etkisi (2025 fiyatları, tam geçiş, kural B): Rapor 20'nin dağılım modeli
   (ekonomi_dagilim.py) içinden çalıştırılır. Hane başına:
     KDV indirimi    = dilimin KDV kazancı / dilimdeki hane sayısı
     AVD (konut)     = AVD × 0,60 × dilimin konut arsası payı (alt iki dilim muaf) / (dilimdeki hane × ev sahipliği oranı)
     AVD (işletme)   = AVD × 0,40 × dilimin işletme arsası payı / dilimdeki hane (dilim ortalaması)
   Varsayımlar [V]: her beşlikte eşit hane sayısı; ev sahipliği her dilimde %56,9; kira yükü değişmez
   (arsa vergisi kiracıya yansımaz; Rapor 20 ile aynı varsayım).
2. Kurum paydaşlarının parasal etkisi: paket v2 ve M6 finansman modelinin hesaplanmış sayıları.
3. Tutum matrisi: 12 paydaş × 8 öneri grubu, tutum −2 … +2 ve gerekçe [V]. Destek endeksi = Σ güç × tutum / Σ güç.
   Engel riski: gücü 3 olan paydaşın tutumu −2; direnç: gücü 3 olan paydaşın tutumu −1.
4. Paketleme: grupların birlikte sunulduğu paketlerde paydaşın tutumu, içerdiği grupların ortalaması.

Girdi : 05_ANALIZ/kod/ekonomi_dagilim.py (+ çıktıları), 05_ANALIZ/sonuclar/ekonomi_kademe_parametre.csv,
        05_ANALIZ/sonuclar/ekonomi_vergi_harcamalari.csv,
        08_MEVZUAT_POLITIKA/politika_v2/yerel_kaynak.csv, karma_kullanim_otopark.csv,
        08_MEVZUAT_POLITIKA/finansman_modeli/telafi_koprusu.csv, finansman_alternatifleri.csv, tipoloji_temel_sonuclar.csv
Çıktı : 06_SIMULASYON/sonuclar/paydas_*.csv, 06_SIMULASYON/grafikler/paydas_*.png|svg
Çalıştırma: PYTHONIOENCODING=utf-8 python 06_SIMULASYON/kod/paydas_oyunu.py
            (önce 05_ANALIZ/kod/ekonomi_veri.py ve 08_MEVZUAT_POLITIKA/politika_v2/politika_v2_mali.py)
"""
import contextlib
import io
import runpy
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
SON5 = KOK / "05_ANALIZ" / "sonuclar"
PV2 = KOK / "08_MEVZUAT_POLITIKA" / "politika_v2"
M6 = KOK / "08_MEVZUAT_POLITIKA" / "finansman_modeli"
SON = KOK / "06_SIMULASYON" / "sonuclar"
GRAF = KOK / "06_SIMULASYON" / "grafikler"
MAVI, TURUNCU, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
YAZI, YAZI_2, YAZI_3, ZEMIN, IZGARA, GRI = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#e8e7e3", "#b9b8b3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN,
                     "axes.edgecolor": YAZI_3, "axes.labelcolor": YAZI_2, "xtick.color": YAZI_2, "ytick.color": YAZI_2,
                     "axes.titlesize": 10, "svg.fonttype": "none"})


def tr(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


# ---------------------------------------------------------------- 1. hane paydaşları
tampon = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
with contextlib.redirect_stdout(tampon):
    D = runpy.run_path(str(KOK / "05_ANALIZ" / "kod" / "ekonomi_dagilim.py"), run_name="ekonomi_dagilim")
kdv_senaryo, oran, Q, Y_q = D["kdv_senaryo"], D["oran"], D["Q"], D["Y_q"]
GSYH, HANE_PAYI = D["GSYH_2025"], D["HANE_PAYI_KDV"]
AVD = 0.005 * GSYH                                   # mlr TL, tam geçiş (paket v2, E1)


def genel_oran(hedef, kapsam):
    lo, hi = 0.0, 0.20
    for _ in range(60):
        m = (lo + hi) / 2
        kayip = -kdv_senaryo("x", oran.where(oran != 0.20, m)).sum() * kapsam
        lo, hi = (lo, m) if kayip < hedef else (m, hi)
    return (lo + hi) / 2


g_B = genel_oran(AVD, 1 / HANE_PAYI)                 # kural B (bütçe-nötr), paket v2 E4
d_kdv = kdv_senaryo("B", oran.where(oran != 0.20, g_B))   # mlr TL, eksi = yük azalır
kp = pd.read_csv(SON5 / "ekonomi_kademe_parametre.csv").set_index("parametre")
HANE = kp.loc["hane_sayisi", "ulke"]
hh_q = HANE / 5                                      # [V] her beşlikte eşit hane
EV_SAHIPLIGI = 0.569                                 # TÜİK 2025 [İ] (toplum_hedefleri.md)
kdv_hane = d_kdv * 1e9 / hh_q                        # TL/hane·yıl, eksi = kazanç
avd_konut_sahip = AVD * 0.60 * D["konut_muaf"] * 1e9 / (hh_q * EV_SAHIPLIGI)
avd_isletme_ort = AVD * 0.40 * D["isletme"] * 1e9 / hh_q
gelir_hane = Y_q * 1e9 / hh_q
vh = pd.read_csv(SON5 / "ekonomi_vergi_harcamalari.csv").set_index("kalem")
TEMETTU_MLR = float(vh.loc[[k for k in vh.index if k.startswith("Kâr payı")][0], "milyar_tl_2025"])  # GİB 2025 [D]
s2_mlr = TEMETTU_MLR * (1 - 25 / 50)                 # S2: istisna oranı %50 → %25, statik [H/V]
s2_hane5 = s2_mlr * 1e9 / hh_q                       # tamamı üst %20'ye düşer [V]

HANE_PAYDAS = [  # kod, ad, dilim, ev sahibi mi, işletme arsası payı, ek kalemler
    ("KIR", "Kiracı çocuklu aile (2. %20)", "QU2", False, False, 0.0),
    ("EMK", "Emekli ev sahibi, tek konut (2. %20)", "QU2", True, False, 0.0),
    ("EVS", "Orta gelirli ev sahibi (3. %20)", "QU3", True, False, 0.0),
    ("ESN", "Esnaf: ev sahibi, dükkânı kirada (3. %20)", "QU3", True, False, 0.0),
    ("GENC", "Genç çift, kirada, ilk evi arıyor (4. %20)", "QU4", False, False, 0.0),
    ("VAR", "Varlıklı malik ve yatırımcı (üst %20)", "QU5", True, True, s2_hane5),
]
hs = []
for kod, ad, q, sahip, isletme, ek in HANE_PAYDAS:
    r = {"kod": kod, "paydas": ad, "dilim": q, "hane_geliri_tl": gelir_hane[q],
         "kdv_indirimi_tl": -kdv_hane[q],
         "avd_konut_tl": avd_konut_sahip[q] if sahip else 0.0,
         "avd_isletme_tl": avd_isletme_ort[q] if isletme else 0.0,
         "temettu_s2_tl": ek}
    r["net_kazanc_tl"] = r["kdv_indirimi_tl"] - r["avd_konut_tl"] - r["avd_isletme_tl"] - r["temettu_s2_tl"]
    r["net_kazanc_gelire_pct"] = 100 * r["net_kazanc_tl"] / r["hane_geliri_tl"]
    hs.append(r)
hane = pd.DataFrame(hs)
hane.round(1).to_csv(SON / "paydas_hane_etki.csv", index=False, encoding="utf-8")
print(f"\nKural B genel KDV %{100 * g_B:.2f}; AVD {AVD:,.0f} mlr TL")
print(hane[["kod", "kdv_indirimi_tl", "avd_konut_tl", "avd_isletme_tl", "temettu_s2_tl", "net_kazanc_tl",
            "net_kazanc_gelire_pct"]].round(1).to_string())

# ---------------------------------------------------------------- 2. kurum paydaşları
yk = pd.read_csv(PV2 / "yerel_kaynak.csv").set_index("kalem")
kk = pd.read_csv(PV2 / "karma_kullanim_otopark.csv")
tk = pd.read_csv(M6 / "telafi_koprusu.csv").set_index("adim")
fa = pd.read_csv(M6 / "finansman_alternatifleri.csv")
tt = pd.read_csv(M6 / "tipoloji_temel_sonuclar.csv")
def yk_(bas): return float(yk.loc[[k for k in yk.index if k.startswith(bas)][0], "sehir_mn_tl"])
otopark = kk[(kk.fiyat == "fiyat_tr") & (kk.karsilama == "bedel")].iloc[0]
c_rows = fa[fa.tip == "C"].set_index("teslim_modeli")
akd = tt.set_index(["fiyat_senaryosu", "otopark_rejimi", "tip"])
AKD = "akd_mtl"                                      # arsa kalıntı değeri, milyon TL/ha (M6)
kurum = [
    ("MUT", "Arsa kalıntı değeri, İstanbul fiyatı: 12 katlı blok / Z+2 avlulu (mevcut kurallar)", akd.loc[("İstanbul ort.", "mevcut", "A"), AKD], akd.loc[("İstanbul ort.", "mevcut", "C"), AKD], "milyon TL/ha", "M6 [H]"),
    ("MUT", "Telafi köprüsü: otopark reformu + harç indirimi + hızlı onay (az katlı lehine)", -(tk.loc["Otopark reformu (net)", "tutar_mtl"] + tk.loc["Harç ve ücret indirimi", "tutar_mtl"] + tk.loc["Hızlı onay (−3 ay)", "tutar_mtl"]), np.nan, "milyon TL/ha", "M6 [H]"),
    ("ESN", "70 m² zemin kat dükkânının otopark yükü (bedel), O4 ile sıfır", otopark.yuk_tl_birim, otopark.yuk_birim_degerine_pct, "TL ve birim değerinin %'si", "politika_v2 [H]"),
    ("BEL", "Şehir (≈ 210 bin): arsa değer vergisi / bugünkü emlak vergisi", yk_("v2: arsa"), yk_("Bugün: emlak"), "milyon TL/yıl", "politika_v2 [H]"),
    ("BEL", "Şehir: merkezi pay mahsubu (E5) / semt + mahalle bütçesine ayrılan (B4)", -yk_("v2: arsa"), yk_("  semt") + yk_("  mahalle"), "milyon TL/yıl", "politika_v2 [H]"),
    ("HAZ", "KDV kaybı (kural B) / merkezi pay mahsubu", -AVD, AVD, "milyar TL/yıl", "politika_v2 [H]"),
    ("HAZ", "Temettü istisnası %50 → %25 (S2), statik", s2_mlr, np.nan, "milyar TL/yıl", "GİB 2025 [D] → [H]"),
    ("MUH", "Mahalle bütçesi / semt bütçesi (öncelik önerisi)", yk_("  mahalle") / 30, yk_("  semt") / 6, "milyon TL/yıl", "politika_v2 [H]"),
    ("URE", "Hal rüsumu: 1 milyon TL doğrudan satışta (Y1: %2 → %0,2)", 20000.0, 2000.0, "TL/yıl", "5957 md. 8 [D] → [H]"),
    ("GENC", "124 m² aile konutu, taksit / medyan aile geliri: piyasa kredisi / aile kredisi + kooperatif ve kamu arsası", c_rows.loc["Kat karşılığı (piyasa satışı)", "piyasa_kredisi_gelir_payi"] * 100, c_rows.loc["Kooperatif + kamu arsası yarı değerle", "aile_konut_kredisi_gelir_payi"] * 100, "%", "M6 [H]"),
]
kurum = pd.DataFrame(kurum, columns=["kod", "kalem", "deger_1", "deger_2", "birim", "kaynak"])
kurum.round(2).to_csv(SON / "paydas_kurum_etki.csv", index=False, encoding="utf-8")
print("\nKurum paydaşları:")
print(kurum[["kod", "deger_1", "deger_2", "birim"]].round(1).to_string())

# ---------------------------------------------------------------- 3. tutum matrisi
PAYDAS = [  # kod, ad, güç (1–3) [V], güç gerekçesi
    ("KIR", "Kiracı çocuklu aile", 1, "Dağınık, örgütsüz; kiracılar hanelerin ≈ %43'ü ama ortak temsilcisi yok"),
    ("GENC", "Genç çift (ilk ev)", 1, "Örgütsüz; seçmen olarak dağınık"),
    ("EMK", "Emekli ev sahibi", 2, "Geniş ve sandığa giden seçmen bloğu; emekli dernekleri"),
    ("EVS", "Orta gelirli ev sahibi", 2, "Ev sahipleri hanelerin %57'si; mülk vergisine duyarlı geniş kitle"),
    ("VAR", "Varlıklı malik ve yatırımcı", 3, "Sermaye, medya ve karar alıcıya erişim"),
    ("ESN", "Esnaf", 2, "TESK ve odalar aracılığıyla örgütlü"),
    ("MUT", "Müteahhit ve yapı sektörü", 3, "Kamu ihaleleri, istihdam, yerel siyasete erişim"),
    ("BEL", "Belediye", 3, "Uygulayıcı: plan, ruhsat, tahsil; yerel veto"),
    ("HAZ", "Hazine ve Maliye", 3, "Bütçe ve vergi kanunlarında fiilî veto"),
    ("BNK", "Banka", 2, "Kredi ve teminat; düzenleyiciye erişim"),
    ("MUH", "Muhtar", 1, "Yerel güven ve bilgi; resmî yetkisi dar"),
    ("URE", "Küçük üretici", 1, "Ziraat odaları ve kooperatifler; dağınık"),
]
GRUP = [  # kod, ad, içerik
    ("G1a", "Arsa vergisi tek başına", "E1 (KDV indirimi, muafiyet ve mahsup olmadan)"),
    ("G1", "Arsa vergisi paketi", "E1–E5: bölünmüş oran, değerleme, muafiyet ve erteleme, KDV indirimi, mahsup"),
    ("G2", "Karma kullanım", "P6, O4, M5, I5, R1"),
    ("G3", "Semt yönetişimi", "B3, B4 (+ B1)"),
    ("G4", "Sermaye geliri", "S1–S3"),
    ("G5", "Asgari ve taban gelir", "A1–A3"),
    ("G6", "Esnaf ve rekabet", "C1–C4"),
    ("G7", "Gıda zinciri", "Y1–Y2"),
]
T = {  # (paydaş, grup): (tutum, gerekçe) — [V]; parasal dayanak varsa [H]
    ("KIR", "G1a"): (0, "Arsa vergisi kiraya yansımazsa doğrudan etkisi yok; kazanç da yok"),
    ("KIR", "G1"): (2, "KDV indirimi var, arsa vergisi yok: net kazanç [H]"),
    ("KIR", "G2"): (1, "Yürüme mesafesinde dükkân ve hizmet"),
    ("KIR", "G3"): (1, "Semt hizmetlerinde söz hakkı"),
    ("KIR", "G4"): (0, "Sermaye geliri yok"),
    ("KIR", "G5"): (1, "Gelir testli destekten alt dilimde yararlanabilir (A1)"),
    ("KIR", "G6"): (1, "Kotaların gözden geçirilmesi fiyatı düşürebilir"),
    ("KIR", "G7"): (1, "Gıda harcama payı yüksek; kısa zincir fiyatı"),
    ("GENC", "G1a"): (1, "Arsa fiyatı düşer, ilk ev ucuzlar (vergi fiyata yansır) [İ]"),
    ("GENC", "G1"): (2, "KDV indirimi + ucuzlayan arsa; aile kredisi ve kooperatifle birlikte erişim [H]"),
    ("GENC", "G2"): (1, "Canlı sokak, yakın hizmet"),
    ("GENC", "G3"): (1, "Kreş ve okul önceliklerinde söz"),
    ("GENC", "G4"): (0, "Küçük tasarruf; S3 hafif lehte, S1–S2 nötr"),
    ("GENC", "G5"): (0, "Doğrudan etkisi az"),
    ("GENC", "G6"): (1, "Rekabet ve fiyat"),
    ("GENC", "G7"): (1, "Gıda fiyatı"),
    ("EMK", "G1a"): (-2, "Yeni ve görünür vergi; nakit sıkışıklığı"),
    ("EMK", "G1"): (1, "Tek konut muaf, KDV indirimi kazanç [H]; ama değerleme ve 'yeni vergi' kaygısı"),
    ("EMK", "G2"): (1, "İhtiyaçlar yürüme mesafesinde; gürültü kaygısı"),
    ("EMK", "G3"): (1, "Mahallede söz hakkı; vakit var"),
    ("EMK", "G4"): (1, "Mevduattaki reel faizin vergilenmesi lehte (S3)"),
    ("EMK", "G5"): (2, "Taban aylığın endekslenmesi (A2)"),
    ("EMK", "G6"): (0, "Az etkili"),
    ("EMK", "G7"): (1, "Gıda fiyatı"),
    ("EVS", "G1a"): (-2, "Yeni vergi, karşılığı yok"),
    ("EVS", "G1"): (-1, "Arsa vergisi KDV indiriminden fazla: net küçük yük [H]"),
    ("EVS", "G2"): (0, "Gürültü kaygısı ile zemin kat değer artışı dengede"),
    ("EVS", "G3"): (1, "Mahalle bütçesinde söz"),
    ("EVS", "G4"): (0, "Az etkili"),
    ("EVS", "G5"): (0, "Az etkili"),
    ("EVS", "G6"): (0, "Az etkili"),
    ("EVS", "G7"): (0, "Az etkili"),
    ("VAR", "G1a"): (-2, "Arsa ve kiralık mülk üzerinde yıllık vergi; mülk değeri düşer"),
    ("VAR", "G1"): (-2, "Net yük en yüksek dilimde [H]; arsa değerinde bir kerelik kayıp"),
    ("VAR", "G2"): (1, "Zemin katın ticari değeri artar"),
    ("VAR", "G3"): (0, "Az etkili"),
    ("VAR", "G4"): (-2, "Hisse kazancı ve temettüde vergi artışı (S1, S2) [H]"),
    ("VAR", "G5"): (0, "Az etkili"),
    ("VAR", "G6"): (0, "Az etkili"),
    ("VAR", "G7"): (0, "Az etkili"),
    ("ESN", "G1a"): (-1, "Konutu için öder, karşılığı yok"),
    ("ESN", "G1"): (0, "Konutta net küçük yük; KDV indirimi talebi artırır"),
    ("ESN", "G2"): (2, "Otopark yükü kalkar (70 m²'de 638 bin TL) [H]; mahallede dükkân açmak serbest"),
    ("ESN", "G3"): (1, "Semt pazarı ve ortak depoda söz"),
    ("ESN", "G4"): (0, "Az etkili"),
    ("ESN", "G5"): (0, "A3 yalnız şeffaflık; asgari ücret baskısı yok"),
    ("ESN", "G6"): (1, "Basit usulden çıkış rampası ve ortak alım (C1, C3); kota sahibi esnaf (eczane, taksi) ise karşı"),
    ("ESN", "G7"): (1, "Manavın üreticiden doğrudan alımı ucuzlar"),
    ("MUT", "G1a"): (0, "Yapı vergisi sıfırlanır, arsa ucuzlar; arsa stoku tutanın maliyeti artar"),
    ("MUT", "G1"): (1, "Yeni yapı vergisizleşir, KDV düşer, talep artar"),
    ("MUT", "G2"): (1, "Karma projelerde otopark ve süre maliyeti düşer"),
    ("MUT", "G3"): (0, "Az etkili; planlamada yeni bir söz sahibi"),
    ("MUT", "G4"): (0, "Az etkili"),
    ("MUT", "G5"): (0, "Az etkili"),
    ("MUT", "G6"): (0, "Az etkili"),
    ("MUT", "G7"): (0, "Az etkili"),
    ("BEL", "G1a"): (2, "Kendi geliri 5,6 katına çıkar, mahsup yok [H]"),
    ("BEL", "G1"): (-1, "Görünür vergiyi belediye toplar, merkezi pay aynı tutarda azalır: siyasi maliyet belediyede, net gelir aynı [H]"),
    ("BEL", "G2"): (-1, "Otopark bedeli ve değer artış payı geliri azalır; meclisin izin yetkisi daralır"),
    ("BEL", "G3"): (-1, "Arsa vergisinin %40'ı semt ve mahalle önceliğine bağlanır; takdir yetkisi azalır"),
    ("BEL", "G4"): (0, "Etkisi yok"),
    ("BEL", "G5"): (0, "Etkisi yok"),
    ("BEL", "G6"): (0, "Taksi kotası gözden geçirmesi UKOME yetkisine dokunur; pazar izlemesi lehte"),
    ("BEL", "G7"): (-1, "Toptancı halini işleten belediyenin hal dışı rüsum geliri azalır"),
    ("HAZ", "G1a"): (0, "Merkezi bütçeye etkisi yok"),
    ("HAZ", "G1"): (0, "Kural B ile bütçe-nötr; ama güvenilir KDV tabanından vazgeçme ve geçiş riski"),
    ("HAZ", "G2"): (0, "Etkisi yok"),
    ("HAZ", "G3"): (0, "Etkisi yok"),
    ("HAZ", "G4"): (1, "S2 ≈ 29 milyar TL ek hasılat [H]; S3 hasılat kaybı"),
    ("HAZ", "G5"): (-1, "Taban aylığın endekslenmesi otomatik maliyet (A2)"),
    ("HAZ", "G6"): (1, "Kayıt dışılığın azalması (C1)"),
    ("HAZ", "G7"): (0, "Etkisi yok"),
    ("BNK", "G1a"): (-1, "Teminattaki arsa değeri düşer"),
    ("BNK", "G1"): (-1, "Teminat değeri düşer; konut talebi artar"),
    ("BNK", "G2"): (0, "Küçük işletme kredisi talebi artabilir"),
    ("BNK", "G3"): (0, "Etkisi yok"),
    ("BNK", "G4"): (0, "TL mevduat cazipleşir (S3), aracı kurum hacmi düşebilir (S1)"),
    ("BNK", "G5"): (0, "Etkisi yok"),
    ("BNK", "G6"): (0, "Etkisi yok"),
    ("BNK", "G7"): (0, "Etkisi yok"),
    ("MUH", "G1a"): (-1, "Değerleme itirazları muhtarlıkta; mahallenin tepkisi"),
    ("MUH", "G1"): (0, "İtiraz yükü var ama mahalleli çoğunlukla kazançlı"),
    ("MUH", "G2"): (1, "Mahalle canlanır; şikâyet yönetimi yükü"),
    ("MUH", "G3"): (2, "Mahalle ve semt meclisinde rol; mahalle bütçesinde öncelik"),
    ("MUH", "G4"): (0, "Etkisi yok"),
    ("MUH", "G5"): (1, "Gelir testli desteğe başvuru yardımı muhtarlıkta"),
    ("MUH", "G6"): (0, "Az etkili"),
    ("MUH", "G7"): (0, "Az etkili"),
    ("URE", "G1a"): (0, "Tarım arazisi kapsam dışı"),
    ("URE", "G1"): (0, "Tarım arazisi kapsam dışı; KDV indirimi talebi artırır"),
    ("URE", "G2"): (1, "Mahallede doğrudan satış noktası"),
    ("URE", "G3"): (1, "Semt pazarında tezgâh"),
    ("URE", "G4"): (0, "Etkisi yok"),
    ("URE", "G5"): (0, "Etkisi yok"),
    ("URE", "G6"): (1, "Semt pazarında üretici payının izlenmesi (C4)"),
    ("URE", "G7"): (2, "Doğrudan satışta rüsum %2 → %0,2 (Y1); izin yerine destek (Y2)"),
}
pdf = pd.DataFrame(PAYDAS, columns=["kod", "paydas", "guc", "guc_gerekce"])
tutum = pd.DataFrame([(p, g, *T[(p, g)]) for p, *_ in PAYDAS for g, *_ in GRUP],
                     columns=["paydas", "grup", "tutum", "gerekce"])
assert len(tutum) == len(PAYDAS) * len(GRUP)
guc = pdf.set_index("kod").guc
M = tutum.pivot(index="paydas", columns="grup", values="tutum").loc[pdf.kod, [g for g, *_ in GRUP]]


# telafi senaryosu: mahsup %90 (arsa vergisinin %10'u belediyede kalır); merkezin kaybı ≈ AVD × %10
MAHSUP = 0.90
bel_kalan = (1 - MAHSUP) * float(yk.loc[[k for k in yk.index if k.startswith("v2: arsa")][0], "sehir_mn_tl"])
haz_kayip = (1 - MAHSUP) * AVD
M_t = M.copy()
M_t.loc["BEL", "G1"] = 1     # kendi geliri net artar (şehir başına ≈ bel_kalan milyon TL/yıl)
M_t.loc["HAZ", "G1"] = -1    # merkez ≈ haz_kayip milyar TL/yıl kaybeder
# paket v2'ye işlenen biçim: KDV indirimi mahsup edilen tutarla sınırlı (AVD × %90) → merkez nötr kalır
M_t2 = M.copy()
M_t2.loc["BEL", "G1"] = 1
SENARYO = {"telafi": M_t, "telafi_kdv": M_t2}


def destek(sut, mat=None):
    mat = M if mat is None else mat
    s = mat[sut] if isinstance(sut, str) else mat[sut].mean(axis=1)
    endeks = (guc * s).sum() / guc.sum()
    engel = [k for k in M.index if guc[k] == 3 and s[k] <= -1.5]
    direnc = [k for k in M.index if guc[k] == 3 and -1.5 < s[k] <= -0.5]
    lehte = int((s > 0).sum())
    aleyhte = int((s < 0).sum())
    return endeks, lehte, aleyhte, ", ".join(engel) or "—", ", ".join(direnc) or "—"


PAKET = [(g, n, g, None) for g, n, _ in GRUP] + [
    ("P1", "Çekirdek paket: arsa vergisi + karma kullanım + semt", ["G1", "G2", "G3"], None),
    ("P2", "Çekirdek + gıda zinciri + esnaf", ["G1", "G2", "G3", "G6", "G7"], None),
    ("P3", "Bütün paket v2", ["G1", "G2", "G3", "G4", "G5", "G6", "G7"], None),
    ("P4", "Çekirdek + belediyeye telafi (mahsup %90)", ["G1", "G2", "G3"], "telafi"),
    ("P5", "Çekirdek + telafi, finansmanı temettü istisnasından (S2)", ["G1", "G2", "G3", "G4"], "telafi"),
    ("P6", "Çekirdek + telafi, KDV indirimi mahsupla sınırlı (merkez nötr; pakete işlenen)", ["G1", "G2", "G3"],
     "telafi_kdv"),
]
ds = []
for kod, ad, icerik, sen in PAKET:
    e, l, a, eng, dir_ = destek(icerik, SENARYO.get(sen))
    ds.append({"kod": kod, "ad": ad, "icerik": icerik if isinstance(icerik, str) else "+".join(icerik),
               "senaryo": sen or "temel", "destek_endeksi": e, "lehte_paydas": l, "aleyhte_paydas": a,
               "engel_riski": eng, "direnc": dir_})
dest = pd.DataFrame(ds)
pdf.to_csv(SON / "paydas_tanimlari.csv", index=False, encoding="utf-8")
tutum.to_csv(SON / "paydas_tutum.csv", index=False, encoding="utf-8")
dest.round(3).to_csv(SON / "paydas_destek.csv", index=False, encoding="utf-8")
print("\nDestek (güç ağırlıklı, −2 … +2):")
print(dest[["kod", "ad", "destek_endeksi", "lehte_paydas", "aleyhte_paydas", "engel_riski", "direnc"]].round(2).to_string())
print(f"Telafi: belediyede kalan ≈ {bel_kalan:,.0f} milyon TL/yıl (şehir), merkezin kaybı ≈ {haz_kayip:,.1f} milyar TL/yıl; "
      f"S2 hasılatı ≈ {s2_mlr:,.1f} milyar TL/yıl")

# duyarlılık: güçler eşit olsaydı
esit = {kod: (SENARYO.get(sen, M)[ic] if isinstance(ic, str)
              else SENARYO.get(sen, M)[ic].mean(axis=1)).mean() for kod, _, ic, sen in PAKET}
pd.Series(esit, name="destek_esit_guc").round(3).to_csv(SON / "paydas_destek_esit_guc.csv", encoding="utf-8")

# ---------------------------------------------------------------- 4. grafikler
ad = dict((k, a) for k, a, *_ in PAYDAS)
gad = dict((g, a) for g, a, _ in GRUP)
cmap = LinearSegmentedColormap.from_list("ayrisan", [TURUNCU, "#f4c3ab", "#efeeea", "#a9c8ee", MAVI])
fig = plt.figure(figsize=(10.6, 7.6))
ax = fig.add_axes([0.25, 0.27, 0.72, 0.56])
im = ax.imshow(M.values, cmap=cmap, vmin=-2, vmax=2, aspect="auto")
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v = M.values[i, j]
        ax.text(j, i, f"{v:+d}".replace("-", "−") if v else "0", ha="center", va="center", fontsize=8.5,
                color=YAZI if abs(v) < 2 else "white")
ax.set_xticks(range(M.shape[1]))
ax.set_xticklabels([textwrap.fill(gad[g], 12) for g in M.columns], fontsize=8)
ax.xaxis.tick_top()
ax.set_yticks(range(M.shape[0]))
ax.set_yticklabels([f"{ad[k]}  (güç {guc[k]})" for k in M.index], fontsize=8.5)
ax.set_xticks(np.arange(-0.5, M.shape[1]), minor=True)
ax.set_yticks(np.arange(-0.5, M.shape[0]), minor=True)
ax.grid(which="minor", color=ZEMIN, lw=2)
ax.tick_params(which="both", length=0)
for s in ax.spines.values():
    s.set_visible(False)
# her sütunun altında o grubun güç ağırlıklı destek endeksi (aynı x konumu)
ax2 = fig.add_axes([0.25, 0.07, 0.72, 0.17])
end = dest[dest.senaryo == "temel"].set_index("kod").loc[M.columns, "destek_endeksi"]
ax2.bar(range(len(end)), end.values, color=[MAVI if v > 0 else TURUNCU for v in end.values], width=0.55)
for j, v in enumerate(end.values):
    ax2.text(j, v + (0.06 if v >= 0 else -0.06), tr(v, 2).replace("-", "−"), ha="center",
             va="bottom" if v >= 0 else "top", fontsize=8, color=YAZI)
ax2.set_xlim(-0.5, len(end) - 0.5)
ax2.set_ylim(-0.85, 0.85)
ax2.axhline(0, color=YAZI_3, lw=0.8)
ax2.set_xticks([])
ax2.set_yticks([])
for s in ax2.spines.values():
    s.set_visible(False)
fig.text(0.24, 0.155, "Güç ağırlıklı\ndestek endeksi", ha="right", va="center", fontsize=8.6, color=YAZI_2)
fig.text(0.012, 0.98, "Paydaş oyunu: kim hangi öneri grubunu destekler, kim karşı çıkar?", fontsize=12.5,
         fontweight="bold", color=YAZI, va="top")
fig.text(0.012, 0.945, "Tutum −2 (güçlü karşı) … +2 (güçlü destek). Güç 1–3 varsayım. Alttaki çubuklar her grubun "
         "güç ağırlıklı ortalama tutumu.", fontsize=8.6, color=YAZI_2, va="top")
fig.text(0.012, 0.015, "Kaynak: paydas_tutum.csv (tutum ve gerekçeler), paydas_oyunu.py. Parasal dayanaklar "
         "Rapor 20 ve paket v2 hesaplarından; tutumlar zihinsel simülasyon [V].", fontsize=7.2, color=YAZI_3)
for uz in ("png", "svg"):
    fig.savefig(GRAF / f"paydas_tutum_matrisi.{uz}", dpi=200)
plt.close(fig)

# hane paydaşlarının net etkisi
fig, ax = plt.subplots(figsize=(10.2, 4.4))
fig.subplots_adjust(left=0.33, right=0.95, top=0.74, bottom=0.14)
h = hane.iloc[::-1]
renk = [MAVI if v > 0 else TURUNCU for v in h.net_kazanc_tl]
ax.barh(range(len(h)), h.net_kazanc_tl, color=renk, height=0.55)
for i, (v, p) in enumerate(zip(h.net_kazanc_tl, h.net_kazanc_gelire_pct)):
    ax.text(v + (900 if v >= 0 else -900), i, f"{'+' if v > 0 else '−'}{tr(abs(v))} TL  (%{tr(abs(p), 1)})",
            va="center", ha="left" if v >= 0 else "right", fontsize=8.2, color=YAZI)
ax.set_yticks(range(len(h)))
ax.set_yticklabels(h.paydas, fontsize=8.6)
ax.axvline(0, color=YAZI_3, lw=0.8)
lim = max(abs(h.net_kazanc_tl))
ax.set_xlim(-lim * 2.0, lim * 0.8)
ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: tr(v)))
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.grid(axis="x", color=IZGARA, lw=0.7)
ax.set_axisbelow(True)
ax.tick_params(length=0)
fig.text(0.012, 0.965, "Arsa vergisi paketi hanelere ne getirir? Yıllık net kazanç (+) ya da yük (−)", fontsize=12.5,
         fontweight="bold", color=YAZI, va="top")
fig.text(0.012, 0.885, "Tam geçiş, kural B (KDV %20 → %16,8), 2025 fiyatları, hane başına; parantezde hane gelirine oranı. "
         "KDV indirimi eksi arsa değer vergisi; üst %20'de temettü istisnasının daralması (S2) da dahil.",
         fontsize=8.6, color=YAZI_2, va="top", wrap=True)
fig.text(0.012, 0.015, "Kaynak: paydas_hane_etki.csv; Rapor 20 dağılım modeli. Varsayımlar: eşit hane sayılı beşlikler, "
         "ev sahipliği %56,9, kira değişmez [V].", fontsize=7.2, color=YAZI_3)
for uz in ("png", "svg"):
    fig.savefig(GRAF / f"paydas_hane_etki.{uz}", dpi=200)
print("\nYazıldı: paydas_*.csv, paydas_tutum_matrisi.png|svg, paydas_hane_etki.png|svg")
