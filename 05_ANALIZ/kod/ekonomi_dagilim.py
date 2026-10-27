"""
Faz 4 · Rapor 7 — Basit dağılım hesabı: KDV, ÖTV ve arsa değer vergisinin gelir dilimlerine yükü
================================================================================================
Soru: Bugünkü KDV ve ÖTV yükü gelir dilimlerine nasıl dağılıyor? Üç değişiklik (genel KDV oranında
indirim, gıdada KDV'nin sıfırlanması, KDV'den arsa değer vergisine gelir-nötr kayış) dilimleri nasıl etkiler?

Yöntem (statik, davranış tepkisi yok; bütün varsayımlar aşağıda [V] ile işaretli):
1. Dilimler: eşdeğer kullanılabilir gelire göre beşte birlik (her dilim nüfusun %20'si).
   - Gelir payları: Eurostat ilc_di01, Türkiye 2025 (TÜİK AB-GYKA verisi) ondalık payları [D].
   - Harcama yapısı: Eurostat hbs_str_t223, Türkiye 2020 dalgası (TÜİK HBA) COICOP 3 hane, ‰ [D].
   - Dilimlerin göreli harcama düzeyi: Eurostat hbs_exp_t133, yetişkin eşdeğeri başına PPS, 2020 [D].
   - Toplam hanehalkı tüketimi ve kullanılabilir geliri: TÜİK kurumsal sektör hesapları, S1M, 2025 [D].
     Dilimin tüketim/gelir oranı = (göreli harcama / göreli gelir) × toplam P3/B6G  [V: anket yapısının
     2025'e taşınabileceği varsayımı].
2. KDV: COICOP grubu başına 2026 yasal oranı (GİB "Güncel KDV oranları" kararı; karışık gruplarda ağırlıklı
   yaklaşık oran [V]). Fiyattaki vergi payı t/(1+t). Toplam, 2025 KDV tahsilatının (dahilde + ithalde) %75'inin
   hanehalkı nihai tüketiminden geldiği varsayımıyla kalibre edilir [V] (uyum ve kapsam katsayısı).
3. ÖTV: 2025 tahsilatı (Muhasebat) ilgili COICOP harcamasıyla dilimlere dağıtılır. Hanehalkının taşıdığı pay:
   tütün, alkol, kolalı içecek %100; akaryakıt %60; motorlu taşıt %70; dayanıklı mal %80 [V].
4. Vergiler tamamen tüketiciye yansır (tam yansıma) [V]; arsa değer vergisi ise tamamen arsa sahibinde kalır
   (kira ile kiracıya yansımaz; standart iktisat varsayımı, Henry George 1879; Oates & Schwab 1997) [V].
5. Arsa değeri dağılımı: hanelerin elindeki konut arsası, dilimin yükletilmiş kira harcamasıyla (CP042)
   orantılı [V, vekil]; işletme ve kiralık arsa (toplam arsa değerinin %40'ı [V]) mülk geliri yoğunlaşmasıyla:
   dilim payları %4/%6/%10/%20/%60 [V]. Üç varyant: A yalnız konut arsası, B konut + işletme,
   C = B + alt iki dilimde tek konut muafiyeti.

6. Karşılaştırma için S4–S5: gıda KDV'sinin sıfırlanmasıyla (S2) aynı bütçenin doğrudan nakit olarak herkese eşit
   (S4) ya da yalnız en yoksul %20'ye (S5) verilmesi [V: idari maliyet ve hedefleme hatası yok].
7. Temel gelirin kaba maliyeti (2025): kişi başı TÜRK-İŞ eşikleri × nüfus; mevcut sosyal yardımlarla (D62) karşılaştırma.

Çıktı: 05_ANALIZ/sonuclar/ekonomi_dagilim_*.csv, ekonomi_temel_gelir_maliyet.csv
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/ekonomi_dagilim.py  (önce ekonomi_veri.py)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "ekonomi"
SON = KOK / "05_ANALIZ" / "sonuclar"
Q = ["QU1", "QU2", "QU3", "QU4", "QU5"]


def jsonstat(d):
    ids, boy = d["id"], d["size"]
    kat = {k: sorted(d["dimension"][k]["category"]["index"].items(), key=lambda x: x[1]) for k in ids}
    out = []
    for flat, v in d["value"].items():
        i, ix = int(flat), []
        for s in reversed(boy):
            ix.append(i % s)
            i //= s
        out.append({k: kat[k][j][0] for k, j in zip(ids, ix[::-1])} | {"v": float(v)})
    return pd.DataFrame(out)


# ---------------------------------------------------------------- 1. dilimler
yap = jsonstat(json.load(open(HAM / "eurostat" / "hbs_str_t223_TR.json", encoding="utf-8")))
yap = yap[(yap.time == "2020")].pivot_table(index="coicop", columns="quant_inc", values="v")[Q] / 1000
dz = jsonstat(json.load(open(HAM / "eurostat" / "hbs_exp_t133_TR.json", encoding="utf-8")))
dz = dz[(dz.time == "2020") & (dz.unit == "PPS_AE")].set_index("quant_inc").v
goreli_harcama = dz[Q] / dz["TOTAL"]
ond = pd.read_csv(SON / "ekonomi_ondalik_paylar.csv").set_index("ondalik")["2025"]
gelir_payi = pd.Series([ond[f"D{2 * i + 1}"] + ond[f"D{2 * i + 2}"] for i in range(5)], index=Q) / 100
goreli_gelir = gelir_payi / 0.2
hh = pd.read_csv(SON / "ekonomi_hanehalki_sektor_hesaplari.csv").set_index("yil")
P3, B6G = hh.loc[2025, "P3_nihai_tuketim"], hh.loc[2025, "B6G_brut_kullanilabilir_gelir"]
toplam_egilim = P3 / B6G
c_y = goreli_harcama / goreli_gelir * toplam_egilim          # dilimin tüketim / gelir oranı
harcama_payi = goreli_harcama / goreli_harcama.sum()           # dilimin toplam tüketimdeki payı (eşit nüfus)
C_q = P3 * harcama_payi                                        # milyar TL, 2025
Y_q = B6G * gelir_payi
print(f"2025 hanehalkı P3 = {P3:,.0f} mlr TL, B6G = {B6G:,.0f}; P3/B6G = {toplam_egilim:.3f}")
print("tüketim/gelir:", c_y.round(2).to_dict())

# ---------------------------------------------------------------- 2. KDV oranları (2026)
# (oran, işaret, not)
KDV = {
    "CP011": (0.01, "D", "I sayılı liste A) gıda maddeleri (5189 s. CBK, 14.02.2022)"),
    "CP012": (0.05, "V", "su ve meyve suyu %1; ÖTV'li kolalı ve gazlı içecek %10 → ağırlıklı ≈ %5"),
    "CP021": (0.20, "D", "genel oran; ayrıca ÖTV (III-a)"),
    "CP022": (0.20, "D", "genel oran; ayrıca ÖTV (III-b)"),
    "CP031": (0.10, "D", "II sayılı liste 5: giyim eşyası"),
    "CP032": (0.10, "D", "II sayılı liste 7: ayakkabı"),
    "CP041": (0.00, "V", "gerçek kişiler arasındaki konut kirası KDV kapsamı dışında kabul edildi"),
    "CP042": (0.00, "D", "yükletilmiş kira; işlem yok"),
    "CP043": (0.20, "V", "bakım-onarım malzeme ve hizmeti genel oran"),
    "CP044": (0.10, "V", "atık su %10 (II-27); su ve çöp hizmetleri karışık → %10"),
    "CP045": (0.15, "V", "mesken elektriği %10 (II-34), doğal gaz ve kömür %20 → ≈ %15"),
    "CP051": (0.20, "D", "genel oran"), "CP052": (0.10, "D", "II-5 ev tekstili"),
    "CP053": (0.20, "D", "genel oran; ayrıca ÖTV (IV)"), "CP054": (0.20, "D", "genel oran"),
    "CP055": (0.20, "D", "genel oran"), "CP056": (0.20, "V", "temizlik malzemesi ve hizmetleri genel oran"),
    "CP061": (0.10, "D", "II-18 beşeri tıbbi ürünler, II-22 tıbbi cihaz"), "CP062": (0.10, "D", "II-21 sağlık hizmetleri"),
    "CP063": (0.10, "D", "II-21 hastane hizmetleri"),
    "CP071": (0.20, "V", "sıfır araç %20 (+ÖTV II); ikinci el özel matrah ihmal edildi"),
    "CP072": (0.20, "D", "akaryakıt ve bakım genel oran (+ÖTV I)"), "CP073": (0.20, "V", "yolcu taşımacılığı genel oran"),
    "CP081": (0.20, "D", "genel oran"), "CP082": (0.20, "D", "genel oran (+ÖTV IV)"), "CP083": (0.20, "D", "genel oran (+ÖİV)"),
    "CP091": (0.20, "D", "genel oran"), "CP092": (0.20, "D", "genel oran"), "CP093": (0.20, "D", "genel oran"),
    "CP094": (0.15, "V", "sinema-tiyatro-müze %10 (II-16), diğer hizmetler %20"),
    "CP095": (0.08, "V", "kitap ve kırtasiye %10 (II-14), gazete-dergi %1 (I-B8)"), "CP096": (0.20, "D", "genel oran"),
    "CP101": (0.10, "D", "II-15 özel eğitim"), "CP102": (0.10, "D", "II-15"), "CP103": (0.10, "D", "II-15"),
    "CP104": (0.10, "D", "II-15 üniversite"), "CP105": (0.10, "D", "II-15"),
    "CP111": (0.10, "D", "II-24 lokanta, kafe"), "CP112": (0.10, "D", "II-25 konaklama"),
    "CP121": (0.20, "V", "kişisel bakım ürün ve hizmetleri genel oran"), "CP123": (0.20, "D", "genel oran"),
    "CP124": (0.10, "D", "II-26 bakım ve huzurevi"), "CP125": (0.00, "D", "sigorta KDV'den istisna (BSMV/gider vergisi ayrı)"),
    "CP126": (0.00, "D", "finansal hizmetler KDV'den istisna (BSMV)"), "CP127": (0.20, "V", "diğer hizmetler genel oran"),
    "CP122": (0.20, "V", "-"), "CP023": (0.0, "V", "-"),
}
ust3 = [c for c in yap.index if len(c) == 5]
yap3 = yap.loc[ust3].fillna(0)
yap3 = yap3 / yap3.sum()  # yuvarlama farkını gider
oran = pd.Series({c: KDV[c][0] for c in ust3})
YIL = {"KDV_2025": 1555.94 + 1724.20}  # milyar TL, Muhasebat [D]
HANE_PAYI_KDV = 0.75  # [V]


def kdv_yuku(o):
    """dilim başına KDV (fiyat içindeki pay), tüketimin oranı olarak (kalibrasyonsuz)"""
    return (yap3.mul(o / (1 + o), axis=0)).sum()


yasal = kdv_yuku(oran)
yasal_toplam = (yasal * C_q).sum()
k_uyum = HANE_PAYI_KDV * YIL["KDV_2025"] / yasal_toplam
print(f"yasal KDV (hanehalkı tüketimi) = {yasal_toplam:,.0f} mlr TL; uyum katsayısı k = {k_uyum:.2f}")

# ---------------------------------------------------------------- 3. ÖTV dağıtımı (2025)
OTV = {  # kalem: (tahsilat mlr TL [D], COICOP, hanehalkı payı [V])
    "tütün": (428.70, ["CP022"], 1.00), "alkol": (145.35, ["CP021"], 1.00), "kolalı": (17.68, ["CP012"], 1.00),
    "akaryakıt": (522.20, ["CP072"], 0.60), "motorlu taşıt": (787.87, ["CP071"], 0.70),
    "dayanıklı mal": (122.51, ["CP053", "CP082", "CP091"], 0.80)}
otv_q = pd.Series(0.0, index=Q)
for ad, (tutar, kods, pay) in OTV.items():
    harc = yap3.loc[kods].sum() * C_q
    otv_q += tutar * pay * harc / harc.sum()
otv_yuk = otv_q / C_q

# ---------------------------------------------------------------- 4. temel tablo
kdv_q = yasal * k_uyum * C_q
temel = pd.DataFrame({
    "gelir_payi_pct": 100 * gelir_payi, "tuketim_payi_pct": 100 * harcama_payi, "tuketim_gelir_orani": c_y,
    "gida_payi_tuketim_pct": 100 * yap.loc["CP01", Q], "kira_payi_tuketim_pct": 100 * yap.loc["CP041", Q],
    "enerji_payi_tuketim_pct": 100 * yap.loc["CP045", Q],
    "kdv_mlr_tl": kdv_q, "otv_mlr_tl": otv_q,
    "kdv_tuketime_pct": 100 * kdv_q / C_q, "otv_tuketime_pct": 100 * otv_yuk,
    "kdv_gelire_pct": 100 * kdv_q / Y_q, "otv_gelire_pct": 100 * otv_q / Y_q})
temel["dolayli_gelire_pct"] = temel.kdv_gelire_pct + temel.otv_gelire_pct
temel["dolayli_tuketime_pct"] = temel.kdv_tuketime_pct + temel.otv_tuketime_pct
temel.index = [f"{i + 1}. %20" for i in range(5)]
temel.index.name = "dilim"
temel.reset_index().round(3).to_csv(SON / "ekonomi_dagilim_temel.csv", index=False, encoding="utf-8")
print(temel[["gelir_payi_pct", "tuketim_gelir_orani", "kdv_tuketime_pct", "otv_tuketime_pct", "dolayli_tuketime_pct",
             "dolayli_gelire_pct"]].round(2).to_string())

# ---------------------------------------------------------------- 5. senaryolar
GSYH_2025 = pd.read_csv(SON / "ekonomi_dunya_bankasi.csv").set_index("yil").loc[2025, "gsyh_mlr_tl"]  # Dünya Bankası [D]
senaryo = []


def kdv_senaryo(ad, yeni_oran):
    yeni = kdv_yuku(yeni_oran) * k_uyum * C_q
    d = yeni - kdv_q  # + yük artışı
    return d


# S1: genel oran %20 → %18
o1 = oran.where(oran != 0.20, 0.18)
d1 = kdv_senaryo("S1", o1)
# S2: gıdada %1 → %0
o2 = oran.copy()
o2["CP011"] = 0.0
d2 = kdv_senaryo("S2", o2)
# S3: KDV'den arsa değer vergisine gelir-nötr kayış: GSYH'nin %0,5'i kadar AVD, genel KDV oranı indirimi
AVD = 0.005 * GSYH_2025
# hanehalkının KDV kaybı AVD'ye eşit olacak şekilde genel oranı bul (hanehalkı dışı KDV ihmal [V])
lo, hi = 0.0, 0.20
for _ in range(60):
    m = (lo + hi) / 2
    kayip = -kdv_senaryo("x", oran.where(oran != 0.20, m)).sum()
    lo, hi = (lo, m) if kayip < AVD else (m, hi)
genel_yeni = (lo + hi) / 2
d3_kdv = kdv_senaryo("S3", oran.where(oran != 0.20, genel_yeni))
konut_arsa = yap.loc["CP042", Q] * C_q
konut_arsa = konut_arsa / konut_arsa.sum()
isletme = pd.Series([0.04, 0.06, 0.10, 0.20, 0.60], index=Q)
avd_A = AVD * konut_arsa
avd_B = AVD * (0.60 * konut_arsa + 0.40 * isletme)
# varyant C: B + alt iki dilimde tek konut muafiyeti (bugünkü EVK md. 8 muafiyetinin genişletilmiş hâli) [V]
konut_muaf = konut_arsa.copy()
konut_muaf[["QU1", "QU2"]] = 0
konut_muaf = konut_muaf / konut_muaf.sum()
avd_C = AVD * (0.60 * konut_muaf + 0.40 * isletme)
print(f"S3: AVD = {AVD:,.0f} mlr TL (GSYH %0,5) → genel KDV oranı %{100 * genel_yeni:.1f}")

# S4–S5: S2 ile aynı bütçe (gıda KDV'sinden vazgeçilen gelir) doğrudan transfer olarak verilseydi [V: idari maliyet yok,
# hedefleme hatası yok]. S4: herkese eşit kişi başı ödeme (temel gelir mantığı); S5: yalnız en yoksul %20'ye.
butce_S2 = -d2.sum()
d4 = pd.Series(-butce_S2 / 5, index=Q)
d5 = pd.Series([-butce_S2, 0, 0, 0, 0], index=Q)

sen = pd.DataFrame({
    "S1_genel_kdv_20den18e_mlr": d1, "S2_gida_kdv_1den0a_mlr": d2,
    "S4_ayni_butce_esit_transfer_mlr": d4, "S5_ayni_butce_alt20_transfer_mlr": d5,
    "S3A_avd_konut_arsasi_net_mlr": d3_kdv + avd_A, "S3B_avd_konut_isletme_net_mlr": d3_kdv + avd_B,
    "S3C_avd_muafiyetli_net_mlr": d3_kdv + avd_C,
    "S3_kdv_indirimi_mlr": d3_kdv, "S3A_avd_mlr": avd_A, "S3B_avd_mlr": avd_B, "S3C_avd_mlr": avd_C})
for c in ["S1_genel_kdv_20den18e", "S2_gida_kdv_1den0a", "S4_ayni_butce_esit_transfer", "S5_ayni_butce_alt20_transfer",
          "S3A_avd_konut_arsasi_net", "S3B_avd_konut_isletme_net", "S3C_avd_muafiyetli_net"]:
    sen[f"{c}_gelire_pct"] = 100 * sen[f"{c}_mlr"] / Y_q
sen["gelir_mlr"] = Y_q
sen.index = temel.index
ozet = sen.copy()
toplam = sen[[c for c in sen.columns if c.endswith("_mlr")]].sum()
print("\nGelire oran (%), eksi = yük azalır:")
print(sen[[c for c in sen.columns if c.endswith("_gelire_pct")]].round(2).to_string())
print("toplam (mlr TL):", toplam.round(1).to_dict())
sen.reset_index().round(4).to_csv(SON / "ekonomi_dagilim_senaryolar.csv", index=False, encoding="utf-8")

# senaryo özet tablosu (rapor için): gelir etkisi, en alt / en üst dilim ve 1. dilimin kazancının payı
ozet_satir = []
for kod, ad in [("S1_genel_kdv_20den18e", "Genel KDV %20 → %18"), ("S2_gida_kdv_1den0a", "Gıdada KDV %1 → %0"),
                ("S4_ayni_butce_esit_transfer", "S2 bütçesiyle herkese eşit kişi başı ödeme"),
                ("S5_ayni_butce_alt20_transfer", "S2 bütçesiyle yalnız en yoksul %20'ye ödeme"),
                ("S3A_avd_konut_arsasi_net", f"AVD (GSYH %0,5) + genel KDV %{f'{100 * genel_yeni:.1f}'.replace('.', ',')} varyant A"),
                ("S3B_avd_konut_isletme_net", f"AVD (GSYH %0,5) + genel KDV %{f'{100 * genel_yeni:.1f}'.replace('.', ',')} varyant B"),
                ("S3C_avd_muafiyetli_net", f"AVD (GSYH %0,5) + genel KDV %{f'{100 * genel_yeni:.1f}'.replace('.', ',')} varyant C")]:
    m = sen[f"{kod}_mlr"]
    g_ = sen[f"{kod}_gelire_pct"]
    ozet_satir.append((ad, m.sum(), 100 * m.sum() / GSYH_2025, g_.iloc[0], g_.iloc[2], g_.iloc[4],
                       100 * m.iloc[0] / m.sum() if abs(m.sum()) > 1 else np.nan))
oz = pd.DataFrame(ozet_satir, columns=["senaryo", "hanehalki_net_yuk_degisimi_mlr_tl", "gsyh_pct", "dilim1_gelire_pct",
                                       "dilim3_gelire_pct", "dilim5_gelire_pct", "dilim1_payi_pct"])
oz.round(3).to_csv(SON / "ekonomi_dagilim_ozet.csv", index=False, encoding="utf-8")
print(oz.round(2).to_string())

# ---------------------------------------------------------------- 6. temel gelir: kaba maliyet (2025 fiyatları)
# Evrensel, koşulsuz ödeme; davranış tepkisi ve finansman etkisi yok [V]. Eşik: TÜRK-İŞ 4 kişilik aile sınırının
# 2025 ortalamasının dörtte biri (kişi başı). Karşılaştırma: hanehalkına giden sosyal yardımlar (D62, ulusal hesaplar).
NUFUS_2025 = 86_092_168  # ADNKS 31.12.2025 [D]
es = pd.read_csv(SON / "ekonomi_ucret_esik_aylik.csv").set_index("ay")
es25 = es.loc["2025-01":"2025-12"].mean()
D62 = hh.loc[2025, "D62_sosyal_yardimlar"]
tg = []
for ad, aylik in [("Kişi başı açlık sınırı (aile sınırı / 4)", es25.aclik_siniri / 4),
                  ("Kişi başı açlık sınırının yarısı", es25.aclik_siniri / 8),
                  ("Kişi başı yoksulluk sınırı (aile sınırı / 4)", es25.yoksulluk_siniri / 4)]:
    maliyet = aylik * 12 * NUFUS_2025 / 1e9
    tg.append((ad, aylik, maliyet, 100 * maliyet / GSYH_2025, maliyet / D62))
tg = pd.DataFrame(tg, columns=["duzey", "kisi_basi_tl_ay_2025", "yillik_maliyet_mlr_tl", "gsyh_pct", "mevcut_sosyal_yardim_kati"])
tg["not"] = (f"2025 nüfusu {NUFUS_2025:,}; D62 2025 = {D62:,.0f} mlr TL".replace(",", ".")
             + f" (GSYH %{100 * D62 / GSYH_2025:.1f})".replace(".", ","))
tg.round(3).to_csv(SON / "ekonomi_temel_gelir_maliyet.csv", index=False, encoding="utf-8")
print(tg.round(2).to_string())

# varsayımlar tablosu
vs = [("KDV oranı " + c, KDV[c][0], KDV[c][1], KDV[c][2]) for c in ust3]
vs += [("Hanehalkı nihai tüketiminin KDV tahsilatındaki payı", HANE_PAYI_KDV, "V", "uyum katsayısı kalibrasyonu"),
       ("Uyum ve kapsam katsayısı k", round(k_uyum, 3), "H", "tahsil edilen / yasal KDV, hanehalkı"),
       ("P3/B6G 2025", round(toplam_egilim, 3), "D", "TÜİK kurumsal sektör hesapları S1M"),
       ("AVD hasılatı (GSYH oranı)", 0.005, "V", "bugünkü emlak vergisi ≈ %0,09; OECD taşınmaz vergisi ort. ≈ %0,95"),
       ("İşletme ve kiralık arsa payı (varyant B)", 0.40, "V", ""), ("İşletme arsası dilim payları", "4/6/10/20/60", "V", "")]
vs += [(f"ÖTV {k} hanehalkı payı", v[2], "V", f"2025 tahsilatı {v[0]} mlr TL [D]") for k, v in OTV.items()]
pd.DataFrame(vs, columns=["varsayim", "deger", "isaret", "not"]).to_csv(SON / "ekonomi_dagilim_varsayimlar.csv",
                                                                         index=False, encoding="utf-8")
print("\ndağılım hesabı tamam.")
