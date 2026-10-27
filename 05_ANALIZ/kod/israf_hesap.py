"""
Faz 4 · Rapor 6 — İsraf, fire ve kaçak: Türkiye'nin yıllık israf faturası
========================================================================
Girdi : 03_VERI/ham/israf/sdmx/*.json          (israf_veri_indir.py; TÜİK SDMX)
        03_VERI/ham/israf/israf_parametreler.csv (her sayı: değer, yıl, kaynak, işaret)
        03_VERI/ham/israf/epdk_elektrik_dagitim_kayip.csv (EPDK 2024 ve 2025 Gelişim Raporları)
        03_VERI/ham/israf/ghsl_il_yapili_nufus_2000_2020.csv (israf_ghsl_arazi.py)
Çıktı : 05_ANALIZ/sonuclar/israf_*.csv

Yöntem (kısaca)
- Her kalem için ALT ve ÜST tahmin. Alt: yalnızca teknik referansın üstündeki (önlenebilir) kısım,
  ihtiyatlı fiyatla. Üst: daha geniş önlenebilir kısım, daha yüksek (ama yine maliyete yakın) fiyatla.
- Değer her kalemin veri yılı fiyatlarıyla TL; USD o yılın ortalama kuruyla; GSYH payı o yılın GSYH'siyle.
- Çifte sayma önlemleri: (1) Belediye atığında yalnız kuru geri dönüştürülebilirler değerlenir; organik
  kısım gıda israfı kaleminde. (2) UNEP perakende israfı, TZOB'un "son tüketiciye ulaşmadan" kayıplarıyla
  örtüşebileceği için toplama katılmaz. (3) Ekmek israfı hane ve gıda hizmeti israfının içindedir; ayrıca
  eklenmez. (4) Boş konut, arazi yayılması ve deprem enkazı yıllık akış değil; "fırsat maliyeti / tek
  seferlik" olarak ayrı tabloda, toplama katılmaz. (5) Şebeke suyunun pompaj elektriği su kaleminde
  değerlenir; elektrik kalemi yalnız dağıtım kaybıdır. (6) Doğal gaz iletiminde kompresör yakıtı israf
  sayılmaz.

Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/israf_hesap.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "israf"
SD = HAM / "sdmx"
SON = KOK / "05_ANALIZ" / "sonuclar"
SON.mkdir(parents=True, exist_ok=True)

P = pd.read_csv(HAM / "israf_parametreler.csv").set_index("kod")
p = lambda k: float(P.loc[k, "deger"])


def jsonstat(ad):
    d = json.load(open(SD / f"{ad}.json", encoding="utf-8"))
    ids, boy = d["id"], d["size"]
    kat = {}
    for k in ids:
        idx = d["dimension"][k]["category"]["index"]
        kat[k] = [c for c, _ in sorted(idx.items(), key=lambda t: t[1])] if isinstance(idx, dict) else idx
    satir = []
    vals = d["value"]
    for flat, v in (vals.items() if isinstance(vals, dict) else enumerate(vals)):
        if v is None or v == "":
            continue
        i, kalan = int(flat), []
        for s in reversed(boy):
            kalan.append(i % s)
            i //= s
        satir.append({k: kat[k][j] for k, j in zip(ids, reversed(kalan))} | {"deger": float(v)})
    df = pd.DataFrame(satir)
    etiket = {k: d["dimension"][k]["category"].get("label", {}) for k in ids}
    return df, etiket


# ---------------------------------------------------------------- genel: GSYH ve kur
g, _ = jsonstat("UH_BH_GSYH_CARI")
g = g[(g.FAALIYET_KOD == "B1GQ") & (g.UNIT_MEASURE == "TTRY")]
GSYH = {int(r.TIME_PERIOD): r.deger * 1e3 for r in g.itertuples()}
GSYH[2025] = p("gsyh_2025_tl")
KUR = {2024: p("usd_2024"), 2025: p("usd_2025")}
print("GSYH 2024:", f"{GSYH[2024] / 1e12:,.3f} trilyon TL", "| 2025:", f"{GSYH[2025] / 1e12:,.3f}")

fatura = []  # her satır bir kalem


def kalem(no, ad, grup, fiz_alt, fiz_ust, birim, tl_alt, tl_ust, yil, isaret, kaynak, yontem, toplamda=True):
    fatura.append(dict(no=no, kalem=ad, grup=grup, fiziksel_alt=fiz_alt, fiziksel_ust=fiz_ust, fiziksel_birim=birim,
                       deger_tl_alt=tl_alt, deger_tl_ust=tl_ust, deger_usd_alt=tl_alt / KUR[yil], deger_usd_ust=tl_ust / KUR[yil],
                       gsyh_pay_alt=100 * tl_alt / GSYH[yil], gsyh_pay_ust=100 * tl_ust / GSYH[yil], deger_yili=yil,
                       isaret=isaret, kaynak=kaynak, yontem=yontem, toplamda=toplamda))


# ---------------------------------------------------------------- 1. Elektrik dağıtım kayıp-kaçağı (2025)
el = pd.read_csv(HAM / "epdk_elektrik_dagitim_kayip.csv")
assert abs(el.fat_dagitim_gwh_2025.sum() - 214756.70) < 1 and abs(el.fat_iletim_gwh_2025.sum() - 73723.27) < 1
r = el.kayip_2025 / 100
el["giren_gwh_2025"] = el.fat_dagitim_gwh_2025 / (1 - r)          # EPDK: kayıp oranı = kayıp / dağıtıma giren enerji
el["kayip_gwh_2025"] = el.giren_gwh_2025 * r
for ad, esik in [("alt", p("el_esik_alt")), ("ust", p("el_esik_ust"))]:
    el[f"onlenebilir_gwh_{ad}"] = el.giren_gwh_2025 * np.clip(r - esik / 100, 0, None)
el["kayip_deger_tl"] = el.kayip_gwh_2025 * 1e3 * p("ptf_2025")
el["kayip_deger_usd"] = el.kayip_deger_tl / KUR[2025]
el["pay_turkiye_kaybi"] = 100 * el.kayip_gwh_2025 / el.kayip_gwh_2025.sum()
el.round(3).to_csv(SON / "israf_elektrik_bolge.csv", index=False, encoding="utf-8")
top_kayip = el.kayip_gwh_2025.sum()
top_oran = 100 * top_kayip / el.giren_gwh_2025.sum()
print(f"Elektrik: kayıp {top_kayip:,.0f} GWh (%{top_oran:.2f}); Dicle payı %{el.set_index('sirket').pay_turkiye_kaybi['DİCLE']:.1f}")
kalem(1, "Elektrik dağıtımında kayıp-kaçak", "Enerji", el.onlenebilir_gwh_alt.sum(), el.onlenebilir_gwh_ust.sum(), "GWh",
      el.onlenebilir_gwh_alt.sum() * 1e3 * p("ptf_2025"), el.onlenebilir_gwh_ust.sum() * 1e3 * p("ptf_2025"), 2025, "D/H",
      "EPDK 2025 Elektrik Piyasası Gelişim Raporu (Tablo 1.11, 5.2); PTF",
      f"Brüt kayıp {top_kayip:,.0f} GWh (%{top_oran:.1f}). Alt: %6'nın, üst: %3,68'in (AYEDAŞ) üstündeki kayıp; PTF ile değerlendi")

# il haritası için: il -> dağıtım bölgesi oranı (İstanbul: iki yakanın dağıtım tüketimiyle ağırlıklı ortalaması)
il_el = []
for t in el.itertuples():
    for il in t.iller.split(";"):
        il_el.append({"il": il.split(" (")[0], "sirket": t.sirket, "oran_2024": t.kayip_2024, "oran_2025": t.kayip_2025,
                      "giren": t.giren_gwh_2025, "kayip": t.kayip_gwh_2025})
il_el = pd.DataFrame(il_el)
ist = il_el[il_el.il == "İstanbul"]
il_el = il_el[il_el.il != "İstanbul"]
il_el = pd.concat([il_el, pd.DataFrame([{"il": "İstanbul", "sirket": "AYEDAŞ+BOĞAZİÇİ",
                                         "oran_2024": np.nan, "oran_2025": 100 * ist.kayip.sum() / ist.giren.sum()}])])
il_el[["il", "sirket", "oran_2024", "oran_2025"]].round(2).to_csv(SON / "israf_elektrik_il.csv", index=False, encoding="utf-8")
assert il_el.il.nunique() == 81

# ---------------------------------------------------------------- 2. Doğal gaz kayıpları (2025)
ghg, _ = jsonstat("DF_SERA_GAZI_EMISYONLARI")
ch4 = ghg[(ghg.SERAGAZ_KAYNAK_SEKTOR == "1_B_2") & (ghg.SERAGAZ_TUR == "2") & (ghg.TIME_PERIOD == "2024")].deger.iloc[0]  # bin ton
co2e_1b2 = ghg[(ghg.SERAGAZ_KAYNAK_SEKTOR == "1_B_2") & (ghg.SERAGAZ_TUR == "_T") & (ghg.TIME_PERIOD == "2024")].deger.iloc[0]
gaz_kacak_m3 = ch4 * 1e6 / p("ch4_yogunluk") / p("ch4_pay_gaz")   # üst sınır: 1.B.2 metanının tamamı doğal gazdan sayılırsa
kalem(2, "Doğal gaz kayıpları", "Enerji", p("gaz_kayip_epdk_2025"), gaz_kacak_m3 / 1e6, "milyon Sm³",
      p("gaz_kayip_epdk_2025") * 1e6 * p("gaz_fiyat_konut_2025"), gaz_kacak_m3 * p("gaz_fiyat_sanayi_2025"), 2025, "D/H",
      "EPDK 2025 Doğal Gaz Gelişim Raporu (Tablo 8.2, 9.1); TÜİK sera gazı envanteri 1.B.2",
      f"Alt: EPDK'nın kayıt ettiği kayıp, konut gaz bedeliyle. Üst: envanterdeki kaçak metan ({ch4:,.1f} bin ton CH4, 2024) gaz hacmine çevrildi, sanayi gaz bedeliyle")
print(f"Gaz: EPDK kayıp {p('gaz_kayip_epdk_2025')} milyon Sm3; envanter kaçağı ≈ {gaz_kacak_m3 / 1e6:,.0f} milyon Sm3 "
      f"(%{100 * gaz_kacak_m3 / 1e6 / p('gaz_tuketim_2024'):.2f}); 1.B.2 = {co2e_1b2 / 1e3:,.2f} Mt CO2e")

# ---------------------------------------------------------------- 3. İçme suyu kayıp-kaçağı (2024, il)
su, lab = jsonstat("DF_SU_ATIKSU_BELEDIYE_CEKILEN_DAGITILAN_V1")
cek = su[(su.SU_MIKTAR == "4") & (su.SU_KAYNAK_TUR == "_T")].pivot_table(index="REF_AREA", columns="TIME_PERIOD", values="deger")
dag = su[(su.SU_MIKTAR == "5")].pivot_table(index="REF_AREA", columns="TIME_PERIOD", values="deger")
sui = pd.DataFrame({"il": [lab["REF_AREA"][k] for k in cek.index]}, index=cek.index)
for y in ["2020", "2022", "2024"]:
    sui[f"cekilen_bin_m3_{y}"] = cek[y]
    sui[f"dagitilan_bin_m3_{y}"] = dag[y]
    sui[f"kayip_oran_{y}"] = 100 * (cek[y] - dag[y]) / cek[y]
sui["fark_bin_m3_2024"] = sui.cekilen_bin_m3_2024 - sui.dagitilan_bin_m3_2024
sui["onlenebilir_alt_bin_m3"] = np.clip(sui.fark_bin_m3_2024 - p("su_hedef") / 100 * sui.cekilen_bin_m3_2024, 0, None)
sui["onlenebilir_ust_bin_m3"] = np.clip(sui.fark_bin_m3_2024 - p("su_esik_ust") / 100 * sui.cekilen_bin_m3_2024, 0, None)
sui["hedef_ustu"] = sui.kayip_oran_2024 > p("su_hedef")
sui.index.name = "ibbs3_kod"
tr_su = sui.loc["TR"]
sui_il = sui.drop(index="TR").reset_index()
sui_il.round(2).to_csv(SON / "israf_su_il.csv", index=False, encoding="utf-8")
su_birim_alt = p("su_enerji") * p("ptf_2024") / 1e3            # TL/m³: yalnız pompaj-arıtma elektriği
su_birim_ust = p("su_deger_ust") * KUR[2024]                  # TL/m³
alt_m3, ust_m3 = sui_il.onlenebilir_alt_bin_m3.sum() * 1e3, sui_il.onlenebilir_ust_bin_m3.sum() * 1e3
print(f"Su 2024: çekilen {tr_su.cekilen_bin_m3_2024 / 1e6:,.3f} milyar m3, dağıtılan {tr_su.dagitilan_bin_m3_2024 / 1e6:,.3f}; "
      f"fark %{tr_su.kayip_oran_2024:.1f}; hedef üstü il {int(sui_il.hedef_ustu.sum())}")
kalem(3, "İçme suyu kayıp-kaçağı", "Su ve atık", alt_m3 / 1e6, ust_m3 / 1e6, "milyon m³", alt_m3 * su_birim_alt, ust_m3 * su_birim_ust,
      2024, "D/H/V", "TÜİK Belediye Su İstatistikleri 2024 (SDMX); Su Kayıpları Yönetmeliği md. 9",
      f"Çekilen − dağıtılan = {tr_su.fark_bin_m3_2024 / 1e6:,.2f} milyar m³ (%{tr_su.kayip_oran_2024:.1f}). Alt: %25 hedefinin üstü × pompaj elektriği "
      f"({su_birim_alt:,.2f} TL/m³). Üst: %10'un üstü × 0,50 USD/m³")

# ---------------------------------------------------------------- 4. Gıda (tüketim aşaması ve üretim-dağıtım kayıpları)
tf, tlab = jsonstat("DF_TARIM_URUNLERI_UFE_MADDE_FIYAT_V2")
tf["urun"] = tf.TAORBA_2008_2_678.map(tlab["TAORBA_2008_2_678"])
tf = tf[tf.UNIT_MEASURE == "TRY_KG"]
f24 = tf[tf.TIME_PERIOD.str.startswith("2024")].groupby("urun").deger.mean()
SEBZE = ["Tomatoes", "Potatoes", "Onion (dry)", "Pepper (green)", "Cucumbers and gherkins", "Eggplants (aubergines)",
         "Cabbages (white)", "Carrots", "Watermelons", "Squash"]
MEYVE = ["Apples", "Oranges", "Grapes", "Peaches", "Lemons and limes", "Mandarins", "Pears", "Apricots", "Cherries", "Strawberries"]
fiyat_sebze, fiyat_meyve, fiyat_bugday = f24[SEBZE].mean(), f24[MEYVE].mean(), f24["Wheat"]
sepet = pd.Series({"tahıl (buğday)": fiyat_bugday, "sebze": fiyat_sebze, "meyve": fiyat_meyve,
                   "çiğ süt": f24["Raw milk from dairy cattle (exclude buffalo)"]})
fiyat_sepet = sepet.mean()   # tüketim aşamasındaki israfın çiftçi eline geçen değeri (TL/kg)
print("Üretici fiyatları 2024 (TL/kg):", sepet.round(2).to_dict(), "| sepet", round(fiyat_sepet, 2))

tuk_ton = p("fwi_hane_2022") + p("fwi_hizmet_2022")
tuk_alt = tuk_ton * 1e3 * p("yenilebilir_alt") * fiyat_sepet
tuk_ust = tuk_ton * 1e3 * p("yenilebilir_ust") * fiyat_sepet * p("perakende_carpan_ust")
kalem(4, "Gıda israfı: hane ve gıda hizmeti", "Gıda", tuk_ton * p("yenilebilir_alt") / 1e6, tuk_ton * p("yenilebilir_ust") / 1e6,
      "milyon ton (yenilebilir)", tuk_alt, tuk_ust, 2024, "D/V",
      "UNEP Food Waste Index 2024 (2022 verisi; Türkiye için 'düşük güven'); TÜİK tarım ürünleri üretici fiyatları 2024",
      f"Toplam {tuk_ton / 1e6:,.2f} milyon ton (perakende {p('fwi_perakende_2022') / 1e6:,.2f} Mt hariç). Alt: %50'si yenilebilir × üretici fiyatı; "
      f"üst: %70 × üretici fiyatının 2,5 katı")
uretim = {"tahıl": (p("tzob_tahil"), fiyat_bugday), "sebze": (p("tzob_sebze"), fiyat_sebze), "meyve": (p("tzob_meyve"), fiyat_meyve)}
ur_ton = sum(v[0] for v in uretim.values())
ur_deger = sum(v[0] * 1e9 * v[1] for v in uretim.values())
kalem(5, "Hasat ve hasat sonrası kayıplar (tahıl, sebze, meyve)", "Gıda", ur_ton * p("uretim_onlenebilir_alt"), ur_ton, "milyon ton",
      ur_deger * p("uretim_onlenebilir_alt"), ur_deger, 2024, "İ/D/V", "TZOB (2022), TÜBA (2024) aktarımı; TÜİK üretici fiyatları 2024",
      f"Son tüketiciye ulaşmadan {ur_ton:,.1f} milyon ton (2020/21). Alt: yarısı önlenebilir; üst: tamamı. 2024 üretici fiyatlarıyla")
ekmek_ton = p("ekmek_gunluk_2013") * 1e6 * 365 * p("ekmek_gram") / 1e3

# tarımda fiyat dalgalanması (planlama göstergesi)
tfa = tf[tf.urun.isin(["Potatoes", "Onion (dry)", "Tomatoes", "Lemons and limes", "Apples", "Wheat", "Oranges", "Cabbages (white)"])]
dal = tfa.groupby("urun").deger.agg(["min", "max", "mean", "std", "count"])
dal["max_min_kat"] = dal["max"] / dal["min"]
dal["degisim_katsayisi"] = dal["std"] / dal["mean"]
yillik = tfa.assign(yil=tfa.TIME_PERIOD.str[:4]).groupby(["urun", "yil"]).deger.mean().unstack()
dal = dal.join(yillik.add_prefix("ort_"))
dal.round(3).to_csv(SON / "israf_tarim_fiyat_dalgalanmasi.csv", encoding="utf-8")
tfa.pivot_table(index="TIME_PERIOD", columns="urun", values="deger").round(3).to_csv(SON / "israf_tarim_fiyat_aylik.csv", encoding="utf-8")

# ---------------------------------------------------------------- 5. Trafik sıkışıklığı: zaman ve yakıt (2025)
ar, alab = jsonstat("DF_MOTORLU_KARA_TASIT_ILLER_V3")
ar["il"] = ar.REF_AREA.map(alab["REF_AREA"])
oto = ar[ar.TIME_PERIOD == "2025-12"].set_index("il").deger
SEHIR = {"İstanbul": "istanbul", "Ankara": "ankara", "İzmir": "izmir", "Antalya": "antalya", "Bursa": "bursa", "Adana": "adana"}
tr_rows = []
for il, k in SEHIR.items():
    saat = p(f"tomtom_saat_{k}")
    tr_rows.append({"il": il, "otomobil_2025": oto[il], "tomtom_kayip_saat": saat,
                    "arac_saat_alt": oto[il] * p("yolcu_pay_alt") * saat * p("trafik_onlenebilir_alt"),
                    "arac_saat_ust": oto[il] * p("yolcu_pay_ust") * saat})
trf = pd.DataFrame(tr_rows)
saat_ucret = p("asgari_net_2025") / p("ayda_saat")
trf["zaman_tl_alt"] = trf.arac_saat_alt * saat_ucret * p("zaman_degeri_alt")
trf["zaman_tl_ust"] = trf.arac_saat_ust * saat_ucret * p("zaman_degeri_ust") * p("doluluk_ust")
trf["yakit_l_alt"] = trf.arac_saat_alt * p("ek_yakit_alt")
trf["yakit_l_ust"] = trf.arac_saat_ust * p("ek_yakit_ust")
trf["yakit_tl_alt"] = trf.yakit_l_alt * p("yakit_fiyat_alt")
trf["yakit_tl_ust"] = trf.yakit_l_ust * p("yakit_fiyat_ust")
trf["co2_bin_ton_alt"] = trf.yakit_l_alt * p("co2_yakit") / 1e6
trf["co2_bin_ton_ust"] = trf.yakit_l_ust * p("co2_yakit") / 1e6
trf.round(1).to_csv(SON / "israf_trafik_sehir.csv", index=False, encoding="utf-8")
s = trf.sum(numeric_only=True)
kalem(6, "Trafik sıkışıklığı: kaybedilen zaman (6 büyük kent)", "Zaman ve yakıt", s.arac_saat_alt / 1e6, s.arac_saat_ust / 1e6,
      "milyon araç-saat", s.zaman_tl_alt, s.zaman_tl_ust, 2025, "D/V", "TomTom Traffic Index 2025; TÜİK motorlu kara taşıtları (Aralık 2025)",
      f"Saat değeri: net asgari ücretin saatliği ({saat_ucret:,.1f} TL) × 0,5 (alt) / × 1,0 ve 1,3 kişi/araç (üst)")
kalem(7, "Trafik sıkışıklığı: ek yakıt (6 büyük kent)", "Zaman ve yakıt", s.yakit_l_alt / 1e6, s.yakit_l_ust / 1e6, "milyon litre",
      s.yakit_tl_alt, s.yakit_tl_ust, 2025, "D/V", "TomTom 2025; TÜİK; yakıt tüketimi ve fiyatı varsayım",
      f"Gecikme saati başına 0,6–1,2 L; 45–55 TL/L. CO2: {s.co2_bin_ton_alt:,.0f}–{s.co2_bin_ton_ust:,.0f} bin ton")

# ---------------------------------------------------------------- 6. Binalar: yalıtımsızlık yüzünden fazla yakılan konut gazı (2025)
b_alt = p("gaz_konut_2025") * p("isinma_pay_alt") * p("yalitimsiz_alt") * p("yalitim_tasarruf_alt")   # milyon Sm³
b_ust = p("gaz_konut_2025") * p("isinma_pay_ust") * p("yalitimsiz_ust") * p("yalitim_tasarruf_ust")
kalem(8, "Binalarda ısı kaybı (yalıtımsız konutlarda fazladan yakılan gaz)", "Enerji", b_alt, b_ust, "milyon Sm³",
      b_alt * 1e6 * p("gaz_fiyat_konut_2025"), b_ust * 1e6 * p("gaz_fiyat_sanayi_2025"), 2025, "D/İ/V",
      "EPDK 2025 (konut gaz tüketimi 20,86 milyar Sm³); İZODER (%75 yalıtımsız); 2. UEVEP",
      "Konut gazı × ısınma payı (%70–85) × yalıtımsız pay (%50–75) × yalıtım tasarrufu (%30–50). Alt: konut gaz bedeli; üst: sanayi gaz bedeli. "
      "Kömür ve odunla ısınan konutlar dahil değil")

# ---------------------------------------------------------------- 7. Atık: düzenli depolamaya giden geri dönüştürülebilir malzeme (2024)
at, _ = jsonstat("DF_ATIK_BELEDIYE_HIZMET_YONETIM_GOSTERGE_V1")
gos = lambda kod, y: at[(at.BELEDIYE_ATIK_GOSTERGE == kod) & (at.TIME_PERIOD == y)].deger
msw_uretilen = gos("12", "2024").iloc[0] * 1e3      # ton
msw_toplanan = gos("13", "2024").iloc[0] * 1e3
yon = at[(at.BELEDIYE_ATIK_GOSTERGE == "14") & (at.TIME_PERIOD == "2024")].set_index("BERTARAF_YONTEM").deger * 1e3
kayip_alt = max(msw_uretilen * p("kuru_geri_donusur_alt") - p("belediye_geri_donusum_2021") * 1e6, 0)
kayip_ust = max(msw_uretilen * p("kuru_geri_donusur_ust") - p("belediye_geri_donusum_2021") * 1e6, 0)
kalem(9, "Depolamaya giden geri dönüştürülebilir belediye atığı", "Su ve atık", kayip_alt / 1e6, kayip_ust / 1e6, "milyon ton",
      kayip_alt * p("ikincil_deger_alt") * KUR[2024], kayip_ust * p("ikincil_deger_ust") * KUR[2024], 2024, "D/V",
      "TÜİK Atık İstatistikleri 2024 (SDMX); UN SDG 12.5.1 (2021 geri dönüşüm 4,32 Mt)",
      f"Üretilen belediye atığı {msw_uretilen / 1e6:,.2f} Mt × kuru geri dönüştürülebilir pay (%20–30) − geri dönüştürülen 4,32 Mt; 60–150 USD/t")
ew_kayip = (p("eatik_uretim_2022") - p("eatik_toplama_2022")) * 1e3        # ton
ew_deger_t = p("eatik_dunya_deger") * 1e9 / (p("eatik_dunya_miktar") * 1e6)  # USD/ton
kalem(10, "Toplanmayan e-atıktaki malzeme", "Su ve atık", ew_kayip / 1e3, ew_kayip / 1e3, "bin ton",
      ew_kayip * ew_deger_t * p("eatik_kayit_disi_pay") * KUR[2024], ew_kayip * ew_deger_t * KUR[2024], 2024, "D/V",
      "Global E-waste Monitor 2024 (2022 verisi)",
      f"Toplanmayan {ew_kayip / 1e3:,.0f} bin ton × dünya ortalaması {ew_deger_t:,.0f} USD/t; alt: değerin dörtte biri (kayıt dışı geri kazanım düşüldü)")

# ---------------------------------------------------------------- 9. Sanayi atık ısısı (2025 fiyatlarıyla)
isi_m3 = p("atik_isi_ktep") * 1e3 * 1e7 / p("gaz_kalori")    # Sm³ doğal gaz eşdeğeri
kalem(11, "Sanayide değerlendirilmeyen atık ısı", "Enerji", isi_m3 * p("atik_isi_gerceklesebilir_alt") / 1e6, isi_m3 / 1e6,
      "milyon Sm³ gaz eşdeğeri", isi_m3 * p("atik_isi_gerceklesebilir_alt") * p("gaz_fiyat_sanayi_2025"),
      p("atik_isi_kojen_tasarruf") * 1e9 * KUR[2025], 2025, "D/V", "ETKB 2. UEVEP 2024–2030 (Dünya Bankası atık ısı projesi)",
      "1.600 kTEP potansiyel. Alt: yarısı, sanayi gaz bedeliyle; üst: UEVEP'in atık ısı + kojenerasyon yıllık tasarruf tahmini (1,6 milyar USD)")

F = pd.DataFrame(fatura)
toplam = F[F.toplamda][["deger_tl_alt", "deger_tl_ust", "deger_usd_alt", "deger_usd_ust", "gsyh_pay_alt", "gsyh_pay_ust"]].sum()
F = pd.concat([F, pd.DataFrame([{"no": 99, "kalem": "TOPLAM (yıllık akış kalemleri)", "grup": "Toplam", **toplam.to_dict(),
                                 "deger_yili": "2024–2025", "toplamda": False}])], ignore_index=True)
F.to_csv(SON / "israf_fatura.csv", index=False, encoding="utf-8")
pd.set_option("display.width", 250)
print(F[["kalem", "fiziksel_alt", "fiziksel_ust", "fiziksel_birim", "deger_usd_alt", "deger_usd_ust", "gsyh_pay_alt", "gsyh_pay_ust"]]
      .assign(deger_usd_alt=lambda d: d.deger_usd_alt / 1e9, deger_usd_ust=lambda d: d.deger_usd_ust / 1e9).round(3).to_string())

# ---------------------------------------------------------------- 8. Fırsat maliyetleri ve tek seferlik stoklar (toplama katılmaz)
firsat = []
fazla = p("konut_stoku") - p("hane_2025")
atil_alt = fazla - p("surtunme_bos_ust") * p("konut_stoku")
atil_ust = fazla - p("surtunme_bos_alt") * p("konut_stoku")
kira_yil = p("birim_kira_2024") * 12 * p("konut_m2")
firsat.append(dict(kalem="Atıl (yerleşilmeyen) konut stoku", fiziksel_alt=atil_alt, fiziksel_ust=atil_ust, birim="milyon konut",
                   deger_tl_alt=atil_alt * 1e6 * kira_yil * p("bos_konut_deger_alt"), deger_tl_ust=atil_ust * 1e6 * kira_yil * p("bos_konut_deger_ust"),
                   yil=2024, tur="yıllık fırsat maliyeti (kira karşılığı)", isaret="İ/D/V",
                   not_=f"Konut stoku ≈31 milyon (ikincil) − 26,98 milyon hane − %3–5 sürtünme boşluğu; yazlıklar dahil. Kira {kira_yil:,.0f} TL/yıl × %30–60"))
gh = pd.read_csv(HAM / "ghsl_il_yapili_nufus_2000_2020.csv")
gh["m2_kisi_2000"] = gh.yapili_ha_2000 * 1e4 / gh.ghs_nufus_2000
gh["m2_kisi_2020"] = gh.yapili_ha_2020 * 1e4 / gh.ghs_nufus_2020
gh["yayilma_fazlasi_ha"] = gh.yapili_ha_2020 - gh.yapili_ha_2000 * gh.ghs_nufus_2020 / gh.ghs_nufus_2000
gh["yapili_artis_pct"] = 100 * (gh.yapili_ha_2020 / gh.yapili_ha_2000 - 1)
gh["nufus_artis_pct"] = 100 * (gh.ghs_nufus_2020 / gh.ghs_nufus_2000 - 1)
gh.round(2).to_csv(SON / "israf_arazi_il.csv", index=False, encoding="utf-8")
T = gh[["yapili_ha_2000", "yapili_ha_2020", "ghs_nufus_2000", "ghs_nufus_2020"]].sum()
yay = T.yapili_ha_2020 - T.yapili_ha_2000 * T.ghs_nufus_2020 / T.ghs_nufus_2000
yay_il = gh.yayilma_fazlasi_ha.clip(lower=0).sum()
firsat.append(dict(kalem="Nüfus artışını aşan yapılı alan büyümesi (2000–2020)", fiziksel_alt=yay, fiziksel_ust=yay_il, birim="ha (20 yılda)",
                   deger_tl_alt=np.nan, deger_tl_ust=np.nan, yil=2020, tur="stok (parasal değer biçilmedi)", isaret="D/H",
                   not_=f"GHSL 1 km: yapılı alan {T.yapili_ha_2000:,.0f} → {T.yapili_ha_2020:,.0f} ha (+%{100 * (T.yapili_ha_2020 / T.yapili_ha_2000 - 1):.1f}); "
                        f"nüfus +%{100 * (T.ghs_nufus_2020 / T.ghs_nufus_2000 - 1):.1f}; kişi başı {T.yapili_ha_2000 * 1e4 / T.ghs_nufus_2000:,.1f} → "
                        f"{T.yapili_ha_2020 * 1e4 / T.ghs_nufus_2020:,.1f} m². Alt: ulusal hesap; üst: il bazında pozitif fazlaların toplamı"))
enk_alt, enk_ust = p("enkaz_m3_alt") * p("enkaz_yogunluk"), p("enkaz_m3_ust") * p("enkaz_yogunluk")   # milyon ton
firsat.append(dict(kalem="2023 depremi enkazı: geri kazanılabilir agrega", fiziksel_alt=enk_alt, fiziksel_ust=enk_ust, birim="milyon ton enkaz",
                   deger_tl_alt=enk_alt * 1e6 * p("enkaz_agrega_pay") * p("agrega_deger_alt") * KUR[2024],
                   deger_tl_ust=enk_ust * 1e6 * p("enkaz_agrega_pay") * p("agrega_deger_ust") * KUR[2024], yil=2024, tur="tek seferlik",
                   isaret="D/V", not_="SBB: 100–120 milyon m³, 2,5 t/m³; bertaraf maliyeti 41,85 milyar TL (2,22 milyar USD, 2023). Agrega payı %80 × 3–8 USD/t"))
FM = pd.DataFrame(firsat)
FM["deger_usd_alt"] = FM.deger_tl_alt / FM.yil.map(lambda y: KUR.get(y, KUR[2024]))
FM["deger_usd_ust"] = FM.deger_tl_ust / FM.yil.map(lambda y: KUR.get(y, KUR[2024]))
FM["gsyh_pay_alt"] = 100 * FM.deger_tl_alt / GSYH[2024]
FM["gsyh_pay_ust"] = 100 * FM.deger_tl_ust / GSYH[2024]
FM.rename(columns={"not_": "not"}).to_csv(SON / "israf_firsat_maliyeti.csv", index=False, encoding="utf-8")
print(FM[["kalem", "fiziksel_alt", "fiziksel_ust", "birim", "deger_usd_alt", "deger_usd_ust"]].round(2).to_string())

# ---------------------------------------------------------------- yardımcı tablolar: atık (il) ve ekmek, diğer göstergeler
ay, aylab = jsonstat("DF_ATIK_BELEDIYE_ATIKYONETIMI_V1")
ay = ay[(ay.TIME_PERIOD == "2024") & (ay.UNIT_MEASURE == "TN")]
ail = ay.pivot_table(index="REF_AREA", columns="BELEDIYE_ATIK_GOSTERGE", values="deger", aggfunc="sum")
ail = ail.rename(columns={"6": "toplanan_ton", "8": "belediye_coplugu_ton", "9": "atik_isleme_tesisi_ton", "10": "diger_ton"})
ail.insert(0, "il", [aylab["REF_AREA"][k] for k in ail.index])
ail["coplugu_pay"] = 100 * ail.belediye_coplugu_ton / ail.toplanan_ton
ail.index.name = "ibbs3_kod"
ail.round(1).to_csv(SON / "israf_atik_il.csv", encoding="utf-8")

tes, teslab = jsonstat("DF_ATIK_BERTARAF_GERI_KAZANIM_TESIS_V1")
tes = tes[tes.TIME_PERIOD == "2024"]
ims, _ = jsonstat("DF_ATIK_IMALAT_SANAYI_GOSTERGELER_V1")
ims = ims[(ims.TIME_PERIOD == "2024") & (ims.ATIK_NITELIK_DURUM == "_T")]
ek = pd.DataFrame([
    ("Belediye atığı üretilen (2024)", msw_uretilen / 1e6, "milyon ton", "TÜİK SDMX", "D"),
    ("Belediye atığı toplanan (2024)", msw_toplanan / 1e6, "milyon ton", "TÜİK SDMX", "D"),
    ("Toplanan atığın atık işleme tesislerine giden payı (2024)", 100 * yon["3"] / msw_toplanan, "%", "TÜİK SDMX", "D"),
    ("Toplanan atığın belediye çöplüklerine giden payı (2024)", 100 * yon["8"] / msw_toplanan, "%", "TÜİK SDMX", "D"),
    ("Kişi başı belediye atığı (2024)", gos("7", "2024").iloc[0], "kg/kişi/gün", "TÜİK SDMX", "D"),
    ("Düzenli depolama tesislerine giden toplam atık, tüm türler (2024)",
     tes[(tes.BERTARAF_KAZANIM_TESIS == "1_1_1") & (tes.TESIS_NITELIK_ATIK == "5") & (tes.ATIK_NITELIK_DURUM == "_T")].deger.iloc[0] / 1e6, "milyon ton", "TÜİK SDMX", "D"),
    ("Kompost tesislerinde işlenen atık (2024)", tes[(tes.BERTARAF_KAZANIM_TESIS == "1_2_1") & (tes.TESIS_NITELIK_ATIK == "7")].deger.iloc[0] / 1e3, "bin ton", "TÜİK SDMX", "D"),
    ("Kompost tesisi sayısı (2024)", tes[(tes.BERTARAF_KAZANIM_TESIS == "1_2_1") & (tes.TESIS_NITELIK_ATIK == "1")].deger.iloc[0], "adet", "TÜİK SDMX", "D"),
    ("İmalat sanayi atığı üretilen (2024)", ims[ims.ATIK_MIKTAR == "1"].deger.sum() / 1e3, "milyon ton", "TÜİK SDMX", "D"),
    ("İmalat sanayi atığının düzenli depolamaya giden kısmı (2024)", ims[(ims.ATIK_MIKTAR == "2") & (ims.KAZANIM_YONTEM == "6")].deger.iloc[0] / 1e3, "milyon ton", "TÜİK SDMX", "D"),
    ("Düzenli depolamadan metan (5.A) (2024)", ghg[(ghg.SERAGAZ_KAYNAK_SEKTOR == "5_A") & (ghg.SERAGAZ_TUR == "_T") & (ghg.TIME_PERIOD == "2024")].deger.iloc[0] / 1e3, "milyon ton CO2e", "TÜİK sera gazı envanteri", "D"),
    ("Petrol ve doğal gaz kaçak emisyonları (1.B.2) (2024)", co2e_1b2 / 1e3, "milyon ton CO2e", "TÜİK sera gazı envanteri", "D"),
    ("İsraf edilen ekmek, ağırlık (2013 ölçümü × 250 g)", ekmek_ton / 1e3, "bin ton/yıl", "TMO 2013 (İ); ağırlık V", "İ/V"),
    ("Çekilen şebeke suyu (2024)", tr_su.cekilen_bin_m3_2024 / 1e6, "milyar m³", "TÜİK SDMX", "D"),
    ("Dağıtılan şebeke suyu (2024)", tr_su.dagitilan_bin_m3_2024 / 1e6, "milyar m³", "TÜİK SDMX", "D"),
    ("Çekilen ile dağıtılan arasındaki fark (2020 / 2022 / 2024)", np.nan, f"%{tr_su.kayip_oran_2020:.1f} / %{tr_su.kayip_oran_2022:.1f} / %{tr_su.kayip_oran_2024:.1f}", "TÜİK SDMX", "H"),
    ("Elektrik dağıtım kaybı, brüt (2025)", top_kayip, "GWh", "EPDK", "H"),
    ("Elektrik dağıtım kaybı, brüt değer (2025, PTF)", el.kayip_deger_usd.sum() / 1e9, "milyar USD", "EPDK", "H"),
    ("Dicle + Vangölü + Aras'ın brüt kayıptaki payı (2025)", el[el.sirket.isin(["DİCLE", "VANGÖLÜ", "ARAS"])].pay_turkiye_kaybi.sum(), "%", "EPDK", "H"),
], columns=["gosterge", "deger", "birim", "kaynak", "isaret"])
ek.to_csv(SON / "israf_ek_gostergeler.csv", index=False, encoding="utf-8")
print(ek.round(3).to_string())
print("TOPLAM (milyar USD):", round(toplam.deger_usd_alt / 1e9, 2), "–", round(toplam.deger_usd_ust / 1e9, 2),
      "| GSYH %:", round(toplam.gsyh_pay_alt, 2), "–", round(toplam.gsyh_pay_ust, 2))
