"""
Faz 4 · Rapor 7 — Gelir adaleti, vergi adaleti ve ticaret: veri derleme
=====================================================================
Bütün kaynaklar anahtarsız. Ham yanıtlar 03_VERI/ham/ekonomi/ altında önbelleğe alınır;
dosya varsa yeniden indirilmez. Çıktılar 05_ANALIZ/sonuclar/ekonomi_*.csv.

Kaynaklar (ayrıntı: 03_VERI/ham/ekonomi/kaynaklar.md)
- TÜİK SDMX (databrowser2.tuik.gov.tr): işgücü (temel + tamamlayıcı göstergeler), kayıt dışı istihdam,
  genel devlet vergi ve sosyal katkı gelirleri, kurumsal sektör hesapları (hanehalkı sektörü S1M)
- Eurostat (TÜİK'in AB-GYKA verisi): Gini, S80/S20, ondalık gelir payları, yoksulluk riski oranı,
  konut mülkiyeti ve konut maliyeti yükü; Hanehalkı Bütçe Anketi (HBS) gelir beşte birlik dilimine göre
  harcama yapısı
- OECD Income Distribution Database (IDD): piyasa, brüt ve kullanılabilir gelir Gini'si, gelir bileşenleri
- TCMB EVDS3 (anahtarsız portlet arka ucu): konut birim kirası (TP.BK.TR); TÜFE (2025=100) TÜİK SDMX DF_TUFE_SDMX_TT10
- Muhasebat merkezi yönetim bütçe gelirleri (2006–2025, 2026 Ocak–Eylül), OECD Revenue Statistics,
  TÜRK-İŞ açlık ve yoksulluk sınırı bültenleri (Ocak, Temmuz, Ağustos, Eylül 2026), GİB asgari ücret kesintileri
- Muhasebat mahalli idareler bütçe gelirleri 2024–2025 (emlak vergisi, harcamalara katılma payları)
- GİB Vergi Harcamaları Raporu 2025 (Tablo 4–5)
- Ortanca ücret: Eurostat earn_ses_monthly (KYA 2018), OECD Earnings DEC_I, TÜİK KYA 2022 (basın aktarımı)
- Dünya Bankası API (anahtarsız): GSYH, Gini, vergi bileşimi (Türkiye ve OECD üyeleri)
- En düşük emekli aylığı (Temmuz 2026 dahil) ve en düşük memur maaşı (Temmuz 2025 →): basın aktarımı [İ]

Çalıştırma:  PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/ekonomi_veri.py
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "ekonomi"
SON = KOK / "05_ANALIZ" / "sonuclar"
for alt in ("sdmx", "eurostat", "oecd", "evds"):
    (HAM / alt).mkdir(parents=True, exist_ok=True)
H = {"Accept": "application/json", "User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}


# ----------------------------------------------------------------------------- yardımcılar
def istek(url, govde=None, ham=False):
    for deneme in range(4):
        try:
            r = urllib.request.Request(url, data=None if govde is None else json.dumps(govde).encode(),
                                       headers=H, method="GET" if govde is None else "POST")
            b = urllib.request.urlopen(r, timeout=600).read()
            return b if ham else json.loads(b)
        except Exception as e:  # ağ hatası: bekle, yeniden dene
            print("  yeniden deneniyor:", str(e)[:120])
            time.sleep(8 * (deneme + 1))
    raise RuntimeError(url)


def onbellek(yol, getir, ham=False):
    yol = Path(yol)
    if not yol.exists():
        v = getir()
        if ham:
            yol.write_bytes(v)
        else:
            json.dump(v, open(yol, "w", encoding="utf-8"), ensure_ascii=False)
        time.sleep(1.5)
    return yol.read_bytes() if ham else json.load(open(yol, encoding="utf-8"))


def jsonstat(d):
    """JSON-stat 2.0 -> uzun tablo (TÜİK SDMX ve Eurostat aynı biçim)."""
    ids, boy = d["id"], d["size"]
    kat = {}
    for k in ids:
        ix = d["dimension"][k]["category"]["index"]
        kat[k] = [(c, i) for i, c in enumerate(ix)] if isinstance(ix, list) else sorted(ix.items(), key=lambda x: x[1])
    deger = d["value"]
    if isinstance(deger, list):
        deger = {str(i): v for i, v in enumerate(deger) if v is not None}
    satir = []
    for flat, v in deger.items():
        if v in ("", None):
            continue
        i, ix = int(flat), []
        for s in reversed(boy):
            ix.append(i % s)
            i //= s
        ix = ix[::-1]
        satir.append({k: kat[k][j][0] for k, j in zip(ids, ix)} | {"deger": float(v)})
    return pd.DataFrame(satir)


TUIK = "https://databrowser2.tuik.gov.tr/api/core/nodes/1/datasets/"


def tuik(df_ad, surum="1.0"):
    return jsonstat(onbellek(HAM / "sdmx" / f"{df_ad}.json", lambda: istek(f"{TUIK}TR,{df_ad},{surum}/data", [])))


EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"


def eurostat(tablo, sorgu, ad):
    return jsonstat(onbellek(HAM / "eurostat" / f"{ad}.json",
                             lambda: istek(f"{EUROSTAT}{tablo}?{sorgu}&format=JSON&lang=EN")))


def yaz(df, ad):
    df.to_csv(SON / f"ekonomi_{ad}.csv", index=False, encoding="utf-8")
    print(f"  -> ekonomi_{ad}.csv  {df.shape}")


# ============================================================================= 1. GELİR DAĞILIMI
print("1) Gelir dağılımı")
gini = eurostat("ilc_di12", "geo=TR&geo=EU27_2020&age=TOTAL", "ilc_di12_TR_EU")
s8020 = eurostat("ilc_di11", "geo=TR&geo=EU27_2020&age=TOTAL&sex=T", "ilc_di11_TR_EU")
yoks = eurostat("ilc_li02", "geo=TR&geo=EU27_2020&age=TOTAL&sex=T", "ilc_li02_TR_EU")
# yoksulluk riski: medyan eşdeğer gelirin %60'ı (MED_EI, B_60), nüfusa oran (PC)
yoks = yoks[(yoks.unit == "PC") & yoks.isin(["MED_EI"]).any(axis=1) & yoks.isin(["B_60"]).any(axis=1)]
g = (gini.pivot_table(index="time", columns="geo", values="deger").add_prefix("gini_")
     .join(s8020.pivot_table(index="time", columns="geo", values="deger").add_prefix("s80s20_"), how="outer")
     .join(yoks.pivot_table(index="time", columns="geo", values="deger").add_prefix("yoksulluk_md60_"), how="outer"))
IDD = HAM / "oecd" / "oecd_idd_TUR.csv"
onbellek(IDD, lambda: istek("https://sdmx.oecd.org/public/rest/data/OECD.WISE.INE,DSD_WISE_IDD@DF_IDD,/TUR.........?"
                            "startPeriod=2010&format=csvfilewithlabels", ham=True), ham=True)
idd = pd.read_csv(IDD)
idd = idd[(idd.METHODOLOGY == "METH2012") & (idd.AGE == "_T")]
ig = idd[idd.MEASURE.isin(["INC_DISP_GINI", "INC_MRKT_GINI", "INC_GROSS_GINI"])].pivot_table(
    index="TIME_PERIOD", columns="MEASURE", values="OBS_VALUE")
ig = ig.rename(columns={"INC_DISP_GINI": "oecd_gini_kullanilabilir", "INC_MRKT_GINI": "oecd_gini_piyasa",
                        "INC_GROSS_GINI": "oecd_gini_brut"})
g.index = g.index.astype(int)
g = g.join(ig, how="outer").reset_index().rename(columns={"index": "yil", "time": "yil"})
g = g[g.yil >= 2006]
yaz(g, "gelir_dagilimi")

# Ondalık gelir payları (Eurostat, eşdeğer kullanılabilir gelir) 2024–2025
d01 = eurostat("ilc_di01", "geo=TR&sinceTimePeriod=2024", "ilc_di01_TR")
d01 = d01[(d01.statinfo == "SHARE") & (d01.unit == "NAC") & d01.quant_inc.str.match(r"^D\d+$")]
dil = d01.pivot_table(index="quant_inc", columns="time", values="deger")
dil = dil.loc[[f"D{i}" for i in range(1, 11)]].reset_index().rename(columns={"quant_inc": "ondalik"})
yaz(dil, "ondalik_paylar")

# TÜİK ulusal bülten (Gelir Dağılımı İstatistikleri 2025, 26.12.2025) — basın aktarımı [İ]
tuik_bulten = pd.DataFrame([
    ("gini", 0.410, 0.413, "İ"), ("gini_sosyal_transfer_haric", 0.473, np.nan, "İ"),
    ("gini_emekli_aylik_dahil_tum_transfer_haric_degil_diger_transfer_haric", 0.420, np.nan, "İ"),
    ("gini_brut_gelir", 0.422, np.nan, "İ"), ("en_yuksek_yuzde20_pay", 48.0, 48.1, "İ"),
    ("en_dusuk_yuzde20_pay", 6.4, 6.3, "İ"), ("p80_p20", 7.5, 7.7, "İ"), ("p90_p10", 12.9, 13.3, "İ"),
    ("pay_maas_ucret", 49.7, 48.8, "İ"), ("pay_muteshebbis", 18.3, 20.8, "İ"), ("pay_sosyal_transfer", 18.2, 17.8, "İ"),
    ("pay_diger_mulk_ve_ozel_transfer_kalan", 13.8, 12.6, "H"),
    ("sosyal_transfer_icinde_emekli_dul_yetim", 89.3, np.nan, "İ"),
    ("ortalama_esdeger_fert_geliri_tl", 332882, 187728, "İ"), ("medyan_esdeger_fert_geliri_tl", 241151, np.nan, "İ"),
    ("ucretli_maasli_ort_esas_is_geliri_tl", 379047, np.nan, "İ"), ("isveren_ort_esas_is_geliri_tl", 1204791, np.nan, "İ"),
    ("kendi_hesabina_ort_esas_is_geliri_tl", 348045, np.nan, "İ"), ("yevmiyeli_ort_esas_is_geliri_tl", 186682, np.nan, "İ"),
], columns=["gosterge", "y2025", "y2024", "isaret"])
tuik_bulten["kaynak"] = ("TÜİK Gelir Dağılımı İstatistikleri 2025 (26.12.2025), ekonomigazetesi.com, dha.com.tr, "
                         "cnbce.com aktarımı; medyan: Rapor 06 (TÜİK); 2024 değerleri değişimden geri hesaplandı")
yaz(tuik_bulten, "tuik_gelir_bulteni_2025")

# OECD IDD gelir bileşenleri (eşdeğer ortalama, TL) — ücret, girişim, sermaye, transfer, vergi
bl = {"EAR": "ucret_maas", "SEIC": "girisim_ve_oz_tuketim", "CAP_INC": "sermaye_geliri", "TRRSSC": "kamu_sosyal_transfer",
      "TRROTC": "ozel_transfer", "TAC": "dogrudan_vergi_ve_prim", "INC_DISP": "kullanilabilir_gelir"}
ib = idd[idd.MEASURE.isin(bl) & (idd.STATISTICAL_OPERATION == "MEAN")].pivot_table(
    index="TIME_PERIOD", columns="MEASURE", values="OBS_VALUE").rename(columns=bl)
for c in [c for c in ib.columns if c != "kullanilabilir_gelir"]:
    ib[f"{c}_pay"] = 100 * ib[c] / ib["kullanilabilir_gelir"]
yaz(ib.reset_index().rename(columns={"TIME_PERIOD": "yil"}).round(2), "oecd_gelir_bilesenleri")

# Hanehalkı sektörü (S1M) birincil gelir ve ikincil dağılım hesapları — TÜİK SDMX
ks = tuik("DF_KURUMSAL_SEKTOR_HESAPLARI_CARI_FIYATLARLA_V2")
ks = ks[ks.REF_SEKTOR == "S1M"]
kal = {("D1X2", "C"): "D1_isgoren_odemeleri", ("B2A3G", "D"): "B2A3G_isletme_artigi_karma_gelir",
       ("D41", "C"): "D41_faiz_alinan", ("D42", "C"): "D42_dagitilan_kar_payi", ("D45", "C"): "D45_arazi_ranti",
       ("D44", "C"): "D44_diger_yatirim_geliri", ("D4", "C"): "D4_mulk_geliri_alinan", ("D4", "D"): "D4_mulk_geliri_odenen",
       ("D62", "C"): "D62_sosyal_yardimlar", ("D5", "D"): "D5_gelir_servet_vergisi_odenen",
       ("D61", "D"): "D61_sosyal_katki_odenen", ("B6G", "D"): "B6G_brut_kullanilabilir_gelir",
       ("P3", "D"): "P3_nihai_tuketim", ("B8G", "D"): "B8G_brut_tasarruf", ("B5G", "D"): "B5G_birincil_gelir_dengesi"}
ks["k"] = list(zip(ks.HESAPLAR, ks.KAYNAKLAR_KULLANIMLAR))
ks = ks[ks.k.isin(kal)]
hh = ks.pivot_table(index="TIME_PERIOD", columns="k", values="deger", aggfunc="first")
hh.columns = [kal[c] for c in hh.columns]
hh = hh / 1e6  # bin TL -> milyar TL
hh.index = hh.index.astype(int)
hh["B6G"] = hh["B6G_brut_kullanilabilir_gelir"]
taban = hh["D1_isgoren_odemeleri"] + hh["B2A3G_isletme_artigi_karma_gelir"] + hh["D4_mulk_geliri_alinan"] + hh["D62_sosyal_yardimlar"]
hh["kaynak_toplami"] = taban
for c in ["D1_isgoren_odemeleri", "B2A3G_isletme_artigi_karma_gelir", "D4_mulk_geliri_alinan", "D41_faiz_alinan",
          "D42_dagitilan_kar_payi", "D45_arazi_ranti", "D62_sosyal_yardimlar"]:
    if c in hh:
        hh[f"pay_{c.split('_')[0]}"] = 100 * hh[c] / taban
hh["gelir_vergisi_yuku_pct_B6G"] = 100 * hh["D5_gelir_servet_vergisi_odenen"] / hh["B6G"]
hh["tuketim_egilimi"] = hh["P3_nihai_tuketim"] / hh["B6G"]
yaz(hh.reset_index().rename(columns={"index": "yil", "TIME_PERIOD": "yil"}).round(3), "hanehalki_sektor_hesaplari")

# ============================================================================= 2. İŞGÜCÜ
print("2) İşgücü")
tm = tuik("DF_ISGUCU_CEYREK_TEMEL_ISGUCU_C")
tm = tm[(tm.TEMEL_YAS == "Y_GE15") & (tm.SEX == "_T") & tm.ISGUCU_GOSTERGE.isin(["1", "2", "3", "4", "6", "7", "8"])]
tp = tm.pivot_table(index="TIME_PERIOD", columns=["SEASONAL_ADJUST", "ISGUCU_GOSTERGE"], values="deger")
tp.columns = [{"1": "nufus15_bin", "2": "isgucu_bin", "3": "istihdam_bin", "4": "issiz_bin", "6": "isgucune_katilim",
               "7": "istihdam_orani", "8": "issizlik"}[g_] + ("_mda" if s == "S" else "")
              for s, g_ in tp.columns]
ta = tuik("DF_ISGUCU_CEYREK_TAMAMLAYICI_GOSTERGE_C")
ta = ta[(ta.SEX == "_T")]
tq = ta.pivot_table(index="TIME_PERIOD", columns=["SEASONAL_ADJUST", "ISGUCU_GOSTERGE"], values="deger")
tq.columns = [{"8": "t_issizlik", "9": "zamana_bagli_eksik_istihdam_ve_issizlik", "10": "potansiyel_isgucu_ve_issizlik",
               "11": "atil_isgucu"}[g_] + ("_mda" if s == "Y" else "") for s, g_ in tq.columns]
kd = tuik("DF_ISGUCU_CEYREK_SGK_KAYIT_C")
print("   kayıt dışı boyutları:", {c: kd[c].unique()[:6].tolist() for c in kd.columns if c not in ("deger", "TIME_PERIOD")})
isg = tp.join(tq, how="outer")
isg.index.name = "ceyrek"
isg = isg.reset_index()
isg["yil"] = isg.ceyrek.str[:4].astype(int)
yaz(isg.round(2), "isgucu_ceyrek")
isg["atil_kisi_bin_yaklasik"] = isg.atil_isgucu / 100 * isg.isgucu_bin  # payda genişletilmiş işgücü; alt sınır [H/V]
yil = isg.groupby("yil")[["issizlik", "atil_isgucu", "isgucune_katilim", "istihdam_orani", "nufus15_bin", "isgucu_bin",
                          "issiz_bin", "atil_kisi_bin_yaklasik"]].mean().round(2)
yil["ceyrek_sayisi"] = isg.groupby("yil").issizlik.count()
yaz(yil.reset_index(), "isgucu_yillik")

# Kayıt dışı istihdam (SGK'ya kayıtlı olmadan çalışan; tarım dışı dahil) — çeyrek ortalaması
kd_ = kd.copy()
kd_["yil"] = kd_.TIME_PERIOD.str[:4].astype(int)
kd_.to_csv(HAM / "sdmx" / "DF_ISGUCU_CEYREK_SGK_KAYIT_C_uzun.csv", index=False, encoding="utf-8")

# ============================================================================= 3. ÜCRETLER, EŞİKLER, KİRA
print("3) Ücret – açlık/yoksulluk – kira")
import fitz  # PyMuPDF

tase = {}
pdf = HAM / "turkis" / "turkis_aclik_yoksulluk_2026.09.pdf"
t = fitz.open(pdf)[3].get_text()
blok = t[t.find("ÇİZELGE 3"):]
for y in (2024, 2025, 2026):
    m = re.search(rf"{y}\s+([\d\s,|\.]+?)(?=Endeks|20\d\d|Bir)", blok.replace("\n", " "))
    sayi = [float(x.replace(",", ".")) for x in re.findall(r"\d+,\d+|\d{3,4}(?=\s)", m.group(1))]
    for i, v in enumerate(sayi[:12]):
        tase[f"{y}-{i + 1:02d}"] = v
# 2023 ayları: 2024 değerleri ve "bir önceki yılın aynı ayına göre değişim" satırından geri hesap
yoy24 = [69.76, 72.49, 75.09, 74.88, 83.06, 82.96, 64.99, 57.99, 48.72, 49.31, 46.60, 46.09]  # TÜRK-İŞ Çizelge 3
for i, r in enumerate(yoy24):
    tase[f"2023-{i + 1:02d}"] = tase[f"2024-{i + 1:02d}"] / (1 + r / 100)
tase = pd.Series(tase).sort_index()
assert abs(tase["2026-09"] - 1419.74) < 0.01 and len(tase) == 45, tase.tail()
olcek = 37800.93 / 1419.74  # Eylül 2026 açlık sınırı (TL) / TASE  [D]
esik = pd.DataFrame({"tase": tase, "aclik_siniri": tase * olcek})
esik["yoksulluk_siniri"] = esik.aclik_siniri / 0.307  # TÜRK-İŞ: gıda payı %30,7 (2003–04 HBA) [D, yöntem notu]
kontrol = {"2025-09": (27970.50, 91109.11), "2025-12": (30143.75, 98188.11), "2026-08": (37388.30, 121786.00)}
for ay, (a, yk) in kontrol.items():
    assert abs(esik.loc[ay, "aclik_siniri"] / a - 1) < 0.002 and abs(esik.loc[ay, "yoksulluk_siniri"] / yk - 1) < 0.002, ay

# Net asgari ücret (GİB "Asgari ücretten yapılan kesintiler" [D]; 2023 Ocak–Haziran tr.wikipedia aktarımı [İ])
au = [("2023-01", 8506.80, "İ"), ("2023-07", 11402.32, "D"), ("2024-01", 17002.12, "D"), ("2025-01", 22104.67, "D"),
      ("2026-01", 28075.50, "D")]
# En düşük emekli aylığı (SGK 4/a-4/b taban; tr.wikipedia ve basın aktarımı [İ]). Temmuz 2026: 20.000 TL'nin
# Ocak–Haziran 2026 TÜFE'si (%17,76) kadar artırılmasıyla 23.552 TL (TBMM'de kabul edilen kanun; ekonomist.com.tr,
# haberturk.com aktarımı, Ekim 2026 araması) [İ]
ema = [("2023-01", 5500, "İ"), ("2023-07", 7500, "İ"), ("2024-01", 10000, "İ"), ("2024-07", 12500, "İ"),
       ("2025-01", 14469, "İ"), ("2025-07", 16881, "İ"), ("2026-01", 20000, "İ"), ("2026-07", 23552, "İ")]
# En düşük memur maaşı, aile yardımı dahil, net (basın aktarımı: kariyer.net, sanayigazetesi.com.tr, haberturk.com,
# Ekim 2026 araması) [İ]. 2025 Temmuz öncesi için tutarlı bir seri bulunamadı (kaynaklar farklı tanım kullanıyor) [DY]
mem = [("2025-07", 50503, "İ"), ("2026-01", 61890, "İ"), ("2026-07", 70224, "İ")]


def basamak(liste, aylar):
    s = pd.Series({a: v for a, v, _ in liste})
    return s.reindex(sorted(set(aylar) | set(s.index))).ffill().reindex(aylar)


esik["net_asgari_ucret"] = basamak(au, esik.index)
esik["en_dusuk_emekli_ayligi"] = basamak(ema, esik.index)
esik["en_dusuk_memur_maasi"] = basamak(mem, esik.index)
esik.loc[:"2025-06", "en_dusuk_memur_maasi"] = np.nan  # öncesi doğrulanmadı [DY]

# TCMB EVDS3: konut birim kirası (TL/m²/ay, çeyreklik) ve TÜFE (aylık)
EVDS = "https://evds3.tcmb.gov.tr/igmevdsms-dis/fe"


def evds(seri, frekans, ad):
    g_ = {"type": "json", "series": seri, "aggregationTypes": "avg", "formulas": "0", "startDate": "01-01-2010",
          "endDate": "31-12-2026", "frequency": str(frekans), "decimalSeperator": ".", "decimal": "6", "dateFormat": "0",
          "lang": "tr", "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": True}
    o = onbellek(HAM / "evds" / f"{ad}.json", lambda: istek(EVDS, g_))
    d = pd.DataFrame(o["items"]).drop(columns="UNIXTIME").set_index("Tarih")
    return pd.to_numeric(d.iloc[:, 0], errors="coerce")


kira = evds("TP.BK.TR", 6, "TP_BK_TR_ceyrek")
_t = tuik("DF_TUFE_SDMX_TT10")  # TÜFE (2025=100), aylık; EVDS TP.FG.J0 (2003=100) Ocak 2026'da bitiyor
tufe = _t[_t.DEGISIM == "1"].set_index("TIME_PERIOD").deger.sort_index()
ck = {f"{q[:4]}-{int(q[5]) * 3 - 2:02d}": v for q, v in kira.dropna().items()}
kira_ay = pd.Series(ck).reindex(sorted(set(esik.index) | set(ck))).ffill()
esik["kira_100m2"] = 100 * kira_ay.reindex(esik.index)
esik["tufe_2025"] = tufe.reindex(esik.index)
for c in ["net_asgari_ucret", "en_dusuk_emekli_ayligi", "en_dusuk_memur_maasi"]:
    esik[f"{c}_aclik_orani"] = esik[c] / esik.aclik_siniri
    esik[f"{c}_yoksulluk_orani"] = esik[c] / esik.yoksulluk_siniri
    esik[f"kira_{c}_orani"] = esik.kira_100m2 / esik[c]
esik.index.name = "ay"
yaz(esik.reset_index().round(4), "ucret_esik_aylik")

# Kira serisinin uzun hali (2018→): 100 m² kira / net asgari ücret
au_uzun = [("2018-01", 1603.12), ("2019-01", 2020.90), ("2020-01", 2324.70), ("2021-01", 2825.90), ("2022-01", 4253.40),
           ("2022-07", 5500.35), ("2023-01", 8506.80), ("2023-07", 11402.32), ("2024-01", 17002.12),
           ("2025-01", 22104.67), ("2026-01", 28075.50)]
ku = pd.DataFrame({"kira_100m2": 100 * kira.dropna()})
ku["ay"] = [f"{q[:4]}-{int(q[5]) * 3 - 2:02d}" for q in ku.index]
s_au = pd.Series(dict(au_uzun))
ku["net_asgari_ucret"] = s_au.reindex(sorted(set(ku.ay) | set(s_au.index))).ffill().reindex(ku.ay).values
ku["kira_asgari_orani"] = ku.kira_100m2 / ku.net_asgari_ucret
ku["tufe_2025"] = tufe.reindex(ku.ay).values
ku["reel_kira_100m2_eylul2026tl"] = ku.kira_100m2 * tufe.dropna().iloc[-1] / ku.tufe_2025
ku["reel_asgari_ucret_eylul2026tl"] = ku.net_asgari_ucret * tufe.dropna().iloc[-1] / ku.tufe_2025
ku = ku.reset_index().rename(columns={"Tarih": "ceyrek", "index": "ceyrek"})
ku["ceyrek"] = [f"{q[:4]}-Ç{q[5]}" for q in ku.ceyrek]  # EVDS "2018-1Ç" → "2018-Ç1"
yaz(ku.round(3), "kira_asgari_ucret")

# ----------------------------------------------------------------------------- ortanca (medyan) ücret
# Türkiye için güncel bir ortanca ücret yayımlanmıyor. Üç parçadan yaklaşık değer kuruldu:
#  - Eurostat earn_ses_monthly (TÜİK Kazanç Yapısı Araştırması 2018): medyan ve ortalama aylık brüt kazanç, avro [D]
#  - OECD Earnings DEC_I: D5/D1 ve D9/D5 (2014, 2018) [D]
#  - TÜİK Kazanç Yapısı Araştırması 2022: ortalama aylık brüt ücret 11.143 TL (basın aktarımı: sabah.com.tr) [İ]
# Varsayım: medyan/ortalama oranı 2018'deki gibi [V]. Sonuç: 2022 medyan brüt ücret / brüt asgari ücret oranı.
ses = jsonstat(onbellek(HAM / "eurostat" / "earn_ses_monthly_TR.json", lambda: istek(
    f"{EUROSTAT}earn_ses_monthly?geo=TR&nace_r2=B-S_X_O&isco08=TOTAL&age=TOTAL&sex=T&worktime=TOTAL&format=JSON&lang=EN")))
ses = ses.pivot_table(index="time", columns="indic_se", values="deger")
kur = jsonstat(onbellek(HAM / "eurostat" / "ert_bil_eur_a_TRY.json", lambda: istek(
    f"{EUROSTAT}ert_bil_eur_a?currency=TRY&statinfo=AVG&format=JSON&lang=EN")))
kur = kur.set_index("time").deger
DEC = HAM / "oecd" / "oecd_earnings_dec_i_TUR.csv"
onbellek(DEC, lambda: istek("https://sdmx.oecd.org/public/rest/data/OECD.ELS.SAE,DSD_EARNINGS@DEC_I,/TUR+OECD......?"
                            "startPeriod=2014&format=csvfilewithlabels", ham=True), ham=True)
dec = pd.read_csv(DEC)
dec = dec[dec.SEX == "_T"].pivot_table(index=["REF_AREA", "AGGREGATION_OPERATION"], columns="TIME_PERIOD", values="OBS_VALUE")
AU_BRUT_2018, AU_BRUT_2022 = 2029.50, (6471.00 + 8506.80) / 2  # GİB asgari ücret tabloları [D]; 2022 iki dönem ortalaması
med18_tl = ses.loc["2018", "MED_E_EUR"] * kur["2018"]
ort18_tl = ses.loc["2018", "MEAN_E_EUR"] * kur["2018"]
oran_med_ort = med18_tl / ort18_tl
ORT22 = 11143.0  # TÜİK KYA 2022 ortalama aylık brüt ücret [İ]
med22 = ORT22 * oran_med_ort
med_au_22 = med22 / AU_BRUT_2022
# 2026: medyan brüt = oran × brüt asgari ücret [V]; net: asgari ücreti aşan kısım için işçi primi %15, GV %15 × 0,85, damga %0,759
AU_BRUT_2026, AU_NET_2026 = 33030.0, 28075.50
med26_net = AU_NET_2026 + (med_au_22 - 1) * AU_BRUT_2026 * (1 - 0.15 - 0.15 * 0.85 - 0.00759)
ortanca = pd.DataFrame([
    ("SES 2018 medyan aylık brüt kazanç (avro)", ses.loc["2018", "MED_E_EUR"], "D", "Eurostat earn_ses_monthly"),
    ("SES 2018 ortalama aylık brüt kazanç (avro)", ses.loc["2018", "MEAN_E_EUR"], "D", "Eurostat earn_ses_monthly"),
    ("Avro/TL ortalama kur 2018", kur["2018"], "D", "Eurostat ert_bil_eur_a"),
    ("SES 2018 medyan brüt kazanç (TL)", med18_tl, "H", ""),
    ("2018 medyan / brüt asgari ücret", med18_tl / AU_BRUT_2018, "H", "brüt asgari ücret 2.029,50 TL [D]"),
    ("2018 medyan / ortalama", oran_med_ort, "H", ""),
    ("OECD D5/D1 2018 (medyanın en alt ondalık sınırına oranı)", dec.loc[("TUR", "D5_1"), 2018], "D", "OECD DEC_I"),
    ("OECD D5/D1 2018, OECD ortalaması", dec.loc[("OECD", "D5_1"), 2018], "D", "OECD DEC_I"),
    ("OECD D9/D5 2018", dec.loc[("TUR", "D9_5"), 2018], "D", "OECD DEC_I"),
    ("KYA 2022 ortalama aylık brüt ücret (TL)", ORT22, "İ", "TÜİK Kazanç Yapısı Araştırması 2022, basın aktarımı"),
    ("2022 medyan aylık brüt ücret tahmini (TL)", med22, "H/V", "2018 medyan/ortalama oranı varsayımı"),
    ("2022 brüt asgari ücret ortalaması (TL)", AU_BRUT_2022, "D", "GİB"),
    ("2022 medyan / brüt asgari ücret", med_au_22, "H/V", ""),
    ("2026 ortanca net ücret tahmini (TL/ay)", med26_net, "H/V", "2022 oranı 2026'ya taşındı"),
], columns=["gosterge", "deger", "isaret", "kaynak"])
yaz(ortanca.round(3), "ortanca_ucret")
print(f"   ortanca/asgari (brüt) 2018 = {med18_tl / AU_BRUT_2018:.2f}; 2022 ≈ {med_au_22:.2f}; 2026 ortanca net ≈ {med26_net:,.0f} TL")

# Eylül 2026 karşılaştırması: tek gelirin 4 kişilik aile eşiklerine ve 100 m² kiraya oranı
e26 = esik.loc["2026-09"]
k26 = pd.DataFrame([
    ("Net asgari ücret", AU_NET_2026, "D"),
    ("Ortanca net ücret (tahmin)", med26_net, "H/V"),
    ("En düşük emekli aylığı (Temmuz 2026)", 23552.0, "İ"),
    ("En düşük memur maaşı, aile yardımı dahil (Temmuz 2026)", 70224.0, "İ"),
    ("Medyan 4 kişilik aile geliri (2026 tahmini, Rapor 06)", 67500.0, "V"),
], columns=["gelir", "tl_ay", "isaret"])
k26["aclik_siniri_eylul2026"] = e26.aclik_siniri
k26["yoksulluk_siniri_eylul2026"] = e26.yoksulluk_siniri
k26["kira_100m2_2026c3"] = e26.kira_100m2
k26["aclik_orani"] = k26.tl_ay / k26.aclik_siniri_eylul2026
k26["yoksulluk_orani"] = k26.tl_ay / k26.yoksulluk_siniri_eylul2026
k26["kira_payi"] = k26.kira_100m2_2026c3 / k26.tl_ay
yaz(k26.round(3), "gelir_esik_2026")

# GYKA ortanca ve ücretli gelirleri ile 2024 eşiklerin karşılaştırması (gelir yılı 2024 varsayımı [V])
e24 = esik.loc["2024-01":"2024-12"].mean()
karsi = pd.DataFrame([
    ("Medyan eşdeğer fert geliri × 2,1 (4 kişilik aile, aylık)", 241151 * 2.1 / 12),
    ("Ücretli-maaşlı ortalama esas iş geliri (aylık)", 379047 / 12),
    ("Kendi hesabına çalışan ortalama esas iş geliri (aylık)", 348045 / 12),
    ("Yevmiyeli ortalama esas iş geliri (aylık)", 186682 / 12),
    ("Net asgari ücret 2024", 17002.12),
    ("En düşük emekli aylığı 2024 ortalaması", (10000 * 6 + 12500 * 6) / 12),
], columns=["gelir", "tl_ay"])
karsi["aclik_2024_ort"] = e24.aclik_siniri
karsi["yoksulluk_2024_ort"] = e24.yoksulluk_siniri
karsi["kira_100m2_2024_ort"] = e24.kira_100m2
karsi["aclik_orani"] = karsi.tl_ay / karsi.aclik_2024_ort
karsi["yoksulluk_orani"] = karsi.tl_ay / karsi.yoksulluk_2024_ort
karsi["kira_payi"] = karsi.kira_100m2_2024_ort / karsi.tl_ay
yaz(karsi.round(3), "gelir_esik_2024")

# Konut maliyeti yükü ve mülkiyet (Eurostat)
yk = eurostat("ilc_lvho07c", "geo=TR&geo=EU27_2020", "ilc_lvho07c_TR_EU")
mul = eurostat("ilc_lvho02", "geo=TR", "ilc_lvho02_TR")
mul = mul[mul.hhcomp == "TOTAL"]
yk = yk.pivot_table(index="time", columns=["geo", "tenure"], values="deger")
yk.columns = [f"konut_yuku_{a}_{b}" for a, b in yk.columns]
mp = mul[(mul.unit == "PC")].pivot_table(index="time", columns=["rskpovth", "tenure"], values="deger")
mp.columns = [f"mulkiyet_{a}_{b}" for a, b in mp.columns]
yaz(yk.join(mp, how="outer").reset_index().rename(columns={"time": "yil"}), "konut_yuku_mulkiyet")

# ============================================================================= 4. VERGİ YAPISI
print("4) Vergi yapısı")
import xlrd

xlrd.biffh.unicode = lambda b, e: b.decode(e, "replace")
VG = HAM / "vergi"
sh = xlrd.open_workbook(VG / "Muhasebat_MYKB_2006-2025_Butce_Gelirleri_Tahsilatlari_Detay2.xls").sheet_by_index(0)
yillar = [int(x) for x in sh.row_values(3)[1:21]]
SATIR = {6: "vergi_toplam", 8: "gelir_vergisi", 9: "gv_beyana_dayanan", 11: "gv_tevkifat", 13: "kurumlar_vergisi",
         18: "mulkiyet_vergileri", 20: "mtv", 24: "kdv_dahilde", 27: "otv_toplam", 28: "otv_petrol_dogalgaz",
         29: "otv_motorlu_tasit", 30: "otv_alkol", 31: "otv_tutun", 32: "otv_kolali", 33: "otv_dayanikli",
         39: "bsmv", 40: "sans_oyunlari", 41: "ozel_iletisim", 42: "dijital_hizmet", 43: "konaklama",
         23: "dahilde_mal_hizmet_toplam", 45: "dis_ticaret_toplam", 46: "gumruk", 47: "kdv_ithalde", 49: "damga", 50: "harclar"}
for r, ad in SATIR.items():  # etiket denetimi
    assert sh.row_values(r)[0].strip(), (r, ad)
vy = pd.DataFrame({ad: [float(x or 0) / 1e6 for x in sh.row_values(r)[1:21]] for r, ad in SATIR.items()}, index=yillar)
vy["kdv_toplam"] = vy.kdv_dahilde + vy.kdv_ithalde
vy["dolayli_genis"] = vy.dahilde_mal_hizmet_toplam + vy.dis_ticaret_toplam + vy.damga + vy.harclar
vy["dolaysiz"] = vy.gelir_vergisi + vy.kurumlar_vergisi + vy.mulkiyet_vergileri
for c in ["dolayli_genis", "dolaysiz", "kdv_toplam", "otv_toplam", "gelir_vergisi", "kurumlar_vergisi", "bsmv",
          "mulkiyet_vergileri", "damga", "harclar"]:
    vy[f"pay_{c}"] = 100 * vy[c] / vy.vergi_toplam
vy["pay_kdv_otv"] = vy.pay_kdv_toplam + vy.pay_otv_toplam
vy["gv_icinde_tevkifat_pay"] = 100 * vy.gv_tevkifat / vy.gelir_vergisi
vy.index.name = "yil"
yaz(vy.reset_index().round(3), "vergi_yapisi_myb")

# 2026 Ocak–Eylül, aynı dönem 2025 (Muhasebat aylık tablolar, etiketle eşleştirme)
def ay_tablosu(dosya):
    s = xlrd.open_workbook(VG / dosya).sheet_by_index(0)
    out = {}
    for r in range(s.nrows):
        lab = str(s.row_values(r)[1]).strip()
        if lab and lab not in out:
            out[lab] = [float(x) if isinstance(x, float) else np.nan for x in s.row_values(r)[2:11]]  # Ocak–Eylül
    return out


a25, a26 = ay_tablosu("Muhasebat_MYKB_2025_Ay_Ici_Butce_Gelirleri_Detay2.xls"), ay_tablosu("Muhasebat_MYKB_2026_Ay_Ici_Butce_Gelirleri_Detay2.xls")
ETK = {"I-Vergi Gelirleri": "vergi_toplam", "a) Gelir Vergisi": "gelir_vergisi", "b) Kurumlar Vergisi": "kurumlar_vergisi",
       "a) Dahilde Alınan Katma Değer Vergisi": "kdv_dahilde", "b) Özel Tüketim Vergisi": "otv_toplam",
       "b) İthalde Alınan Katma Değer Vergisi": "kdv_ithalde", "Petrol ve Doğalgaz Ürünleri (I)": "otv_petrol_dogalgaz"}
oe = []
for lab, ad in ETK.items():
    k25 = next((k for k in a25 if k.replace(" ", "") == lab.replace(" ", "")), None)
    k26 = next((k for k in a26 if k.replace(" ", "") == lab.replace(" ", "")), None)
    oe.append((ad, np.nansum(a25[k25]) / 1e6 if k25 else np.nan, np.nansum(a26[k26]) / 1e6 if k26 else np.nan))
oe = pd.DataFrame(oe, columns=["kalem", "ocak_eylul_2025", "ocak_eylul_2026"])
oe["degisim_pct"] = 100 * (oe.ocak_eylul_2026 / oe.ocak_eylul_2025 - 1)
yaz(oe.round(2), "vergi_2026_ocak_eylul")

# OECD Revenue Statistics: Türkiye ve OECD ortalaması (pay ve GSYH oranları)
rv = pd.read_csv(VG / "OECD_RevenueStatistics_DF_RSOECD_TUR_OECD_2000-2024.csv")
KOD = {"_T": "toplam", "T_1100": "kisisel_gelir_vergisi", "T_1200": "kurumlar_vergisi", "T_2000": "sosyal_guvenlik",
       "T_4000": "mulk_vergileri", "T_4100": "tasinmaz_donemsel", "T_5000": "mal_hizmet", "T_5111": "kdv",
       "T_5121": "ozel_tuketim"}
rv = rv[rv.STANDARD_REVENUE.isin(KOD) & rv.UNIT_MEASURE.isin(["PT_B1GQ", "PT_OTR_SECTOR"])]
if "SECTOR" in rv:
    rv = rv[rv.SECTOR == "S13"] if (rv.SECTOR == "S13").any() else rv
rvp = rv.pivot_table(index="TIME_PERIOD", columns=["REF_AREA", "UNIT_MEASURE", "STANDARD_REVENUE"], values="OBS_VALUE",
                     aggfunc="first")
rvp.columns = [f"{a}_{'gsyh' if u == 'PT_B1GQ' else 'pay'}_{KOD[s]}" for a, u, s in rvp.columns]
yaz(rvp.reset_index().rename(columns={"TIME_PERIOD": "yil"}).round(3), "vergi_oecd")

# Genel devlet (S13) vergi ve sosyal katkı gelirleri — TÜİK SDMX (milyon TL)
gd = tuik("DF_GENEL_DEVLET_VERGI_SOSYAL_KATKI_V2")
gd = gd[gd.ALT_SEKTOR == "S13"].pivot_table(index="TIME_PERIOD", columns="KULLANIMLAR_KAYNAKLAR_T9", values="deger",
                                            aggfunc="first")
yaz(gd.reset_index().rename(columns={"TIME_PERIOD": "yil"}), "genel_devlet_vergi")

# Vergi harcamaları (GİB 2025 Vergi Harcamaları Raporu, Ek I tabloları; PDF'ten kalem kalem doğrulandı) [D]. Seçili kalemler
vh = pd.DataFrame([
    ("Asgari ücret gelir ve damga vergisi istisnası (GVK 23/18, DVK)", 848.9, 1037.8),
    ("Yatırım fonu ve ortaklık kazançları istisnası (KVK 5/1-d)", 366.0, np.nan),
    ("GVK Geçici md. 67 (menkul kıymet getirilerinde indirimli/sıfır stopaj)", 189.3, np.nan),
    ("İndirimli kurumlar vergisi (KVK 32/A, yatırım teşviki)", 139.8, np.nan),
    ("KDV'de yem ve gübre istisnası", 114.6, np.nan),
    ("Yatırım fonu işlemlerinde BSMV istisnası (6802 md. 29/t)", 95.0, np.nan),
    ("KDV 17/4-g (külçe altın-gümüş, sermaye piyasası aracı, hurda teslimi)", 73.5, np.nan),
    ("Toplama yapılmayan menkul sermaye iratları (GVK 86/1-c)", 67.4, np.nan),
    ("Taşınmaz kiralama KDV istisnası (KDVK 17/4-d)", 66.3, np.nan),
    ("Kâr payı (temettü) istisnası (GVK 22/3)", 57.9, np.nan),
    ("Konut kira geliri istisnası (GVK 21)", 18.6, np.nan),
], columns=["kalem", "milyar_tl_2025", "milyar_tl_2026"])
vh["toplam_2025"], vh["toplam_2026"], vh["gsyh_pct_2025"], vh["gsyh_pct_2026"] = 3170.3, 3597.1, 5.10, 4.66
yaz(vh, "vergi_harcamalari")
# Vergi harcamasının aynı vergiden tahsilata oranı, 2025 (GİB raporu Tablo 4–5, s. 294; PDF'ten okundu) [D]
vht = pd.DataFrame([("Gelir vergisi", 1483.706, 2813.235), ("Kurumlar vergisi", 752.854, 1223.874),
                    ("KDV", 605.020, 3280.129), ("ÖTV", 76.925, 2024.315), ("Diğer", 251.791, 1707.915),
                    ("Toplam", 3170.297, 11049.467)], columns=["vergi", "vergi_harcamasi_mlr_tl_2025", "tahsilat_mlr_tl_2025"])
vht["harcama_tahsilat_orani_pct"] = 100 * vht.vergi_harcamasi_mlr_tl_2025 / vht.tahsilat_mlr_tl_2025
vht["asgari_ucret_istisnasi_payi_pct"] = np.where(vht.vergi == "Gelir vergisi", 100 * 848.932 / 1483.706, np.nan)
yaz(vht.round(2), "vergi_harcamasi_tahsilat")

# Mahalli idareler bütçe gelirleri (Muhasebat, ekonomik kod 4. düzey), 2024–2025, milyar TL [D]
KALEM = {"BÜTÇE GELİRLERİ HESABI": "toplam_butce_geliri", "Vergi Gelirleri": "kendi_vergi_gelirleri",
         "Bina Vergisi": "bina_vergisi", "Arsa Vergisi": "arsa_vergisi", "Arazi Vergisi": "arazi_vergisi",
         "Merkezi idare Vergi Gelirlerinden Alınan Paylar": "merkezi_vergi_paylari",
         "Kamu Harcamalarına Katılma Payları": "harcamalara_katilma_paylari",
         "Otopark Yönetmeliği Uyarınca Alınan Otopark Bedeli": "otopark_bedeli",
         "3194 sayılı İmar Kanunu Kapsamında Alınan Teknik Altyapı Bedeli": "imar_teknik_altyapi_bedeli",
         "İşyeri Açma İzni Harcı": "isyeri_acma_izni_harci", "Arazi Satışı": "arazi_satisi"}
yer = {}
for y_ in (2024, 2025):
    s = xlrd.open_workbook(VG / f"Muhasebat_MahalliIdareler_{y_}_Butce_Gelirleri_Ekod4.xls").sheet_by_index(0)
    d_ = {}
    for r in range(s.nrows):
        lab = str(s.row_values(r)[4]).strip()
        if lab in KALEM and KALEM[lab] not in d_:
            d_[KALEM[lab]] = float(s.row_values(r)[9]) / 1e6
    yer[y_] = d_
yer = pd.DataFrame(yer).T
yer["emlak_vergisi"] = yer.bina_vergisi + yer.arsa_vergisi + yer.arazi_vergisi
yer["emlak_vergisi_butce_payi_pct"] = 100 * yer.emlak_vergisi / yer.toplam_butce_geliri
yer["merkezi_pay_butce_payi_pct"] = 100 * yer.merkezi_vergi_paylari / yer.toplam_butce_geliri

# Dünya Bankası (anahtarsız API): GSYH (cari TL), Gini, vergi bileşimi; Türkiye ve OECD üyeleri (OED)
(HAM / "worldbank").mkdir(exist_ok=True)


def wb(kod, ulke="TUR"):
    o = onbellek(HAM / "worldbank" / f"{ulke}_{kod}.json",
                 lambda: istek(f"https://api.worldbank.org/v2/country/{ulke}/indicator/{kod}?format=json&per_page=200"))
    return pd.Series({int(x["date"]): x["value"] for x in o[1] if x["value"] is not None}).sort_index()


gsyh = wb("NY.GDP.MKTP.CN") / 1e9  # milyar TL
yer["gsyh_mlr_tl"] = gsyh.reindex(yer.index).values
yer["emlak_vergisi_gsyh_pct"] = 100 * yer.emlak_vergisi / yer.gsyh_mlr_tl
yer["arsa_vergisi_gsyh_pct"] = 100 * yer.arsa_vergisi / yer.gsyh_mlr_tl
yer.index.name = "yil"
yaz(yer.reset_index().round(3), "yerel_gelirler")
wbt = pd.DataFrame({
    "gsyh_mlr_tl": gsyh, "gini_TUR": wb("SI.POV.GINI"),
    "mal_hizmet_vergisi_gelir_payi_TUR": wb("GC.TAX.GSRV.RV.ZS"), "mal_hizmet_vergisi_gelir_payi_OED": wb("GC.TAX.GSRV.RV.ZS", "OED"),
    "gelir_kar_vergisi_gelir_payi_TUR": wb("GC.TAX.YPKG.RV.ZS"), "gelir_kar_vergisi_gelir_payi_OED": wb("GC.TAX.YPKG.RV.ZS", "OED"),
    "vergi_gsyh_TUR": wb("GC.TAX.TOTL.GD.ZS"), "vergi_gsyh_OED": wb("GC.TAX.TOTL.GD.ZS", "OED")})
wbt = wbt[wbt.index >= 2005]
wbt.index.name = "yil"
yaz(wbt.reset_index().round(3), "dunya_bankasi")

# ============================================================================= 5. ETKİN VERGİ ORANLARI (2026, hesap)
print("5) Etkin oranlar")
DILIM_UCRET = [(190_000, .15), (400_000, .20), (1_500_000, .27), (5_300_000, .35), (np.inf, .40)]
DILIM_DIGER = [(190_000, .15), (400_000, .20), (1_000_000, .27), (5_300_000, .35), (np.inf, .40)]


def tarife(m, dilim):
    v, alt = 0.0, 0.0
    for ust, o in dilim:
        if m > alt:
            v += (min(m, ust) - alt) * o
        alt = ust
    return v


AU_BRUT = 33_030.0
satir = []
for kat in [1, 1.5, 2, 3, 5, 10]:  # brüt ücret, asgari ücretin katı
    brut_y = AU_BRUT * kat * 12
    matrah = brut_y * 0.85  # işçi SGK %14 + işsizlik %1 düşülür
    istisna = tarife(AU_BRUT * 12 * 0.85, DILIM_UCRET)  # asgari ücrete isabet eden vergi istisnası (yaklaşık, yıllık)
    gv = max(tarife(matrah, DILIM_UCRET) - istisna, 0)
    dv = max(brut_y - AU_BRUT * 12, 0) * 0.00759
    satir.append(("ücret", f"asgari ücretin {str(kat).replace('.', ',')} katı", brut_y, gv + dv, 100 * (gv + dv) / brut_y,
                  100 * (gv + dv + brut_y * .15) / brut_y))
for kira in [150_000, 300_000, 600_000, 1_200_000]:  # konut kira geliri, başka geliri olmayan kişi
    matrah = max(kira - 58_000, 0) * 0.85
    gv = tarife(matrah, DILIM_DIGER)
    satir.append(("konut kirası (beyan)", f"yıllık {kira:,.0f} TL".replace(",", "."), kira, gv, 100 * gv / kira, 100 * gv / kira))
satir += [("mevduat faizi (stopaj)", "TL mevduat, uzun vade", np.nan, np.nan, 10.0, 10.0),
          ("mevduat faizi (stopaj)", "TL mevduat, kısa vade", np.nan, np.nan, 17.5, 17.5),
          ("temettü (stopaj)", "gerçek kişi, nihai", np.nan, np.nan, 15.0, 15.0),
          ("BIST hisse satış kazancı", "1 yıldan kısa", np.nan, np.nan, 0.0, 0.0),
          ("enflasyona endeksli mevduat", "1 yıldan uzun", np.nan, np.nan, 0.0, 0.0)]
et = pd.DataFrame(satir, columns=["gelir_turu", "ornek", "yillik_brut_tl", "vergi_tl", "etkin_vergi_pct",
                                  "vergi_ve_isci_primi_pct"])
et["isaret"] = ["H"] * (len(et) - 5) + ["D"] * 5
yaz(et.round(2), "etkin_vergi_oranlari")
print(et[["gelir_turu", "ornek", "etkin_vergi_pct"]].to_string())

# Nominal faiz vergisinin reel getiriye etkisi (örnek; 2025 enflasyonu ile) [H]
print("\nveri derleme tamam.")
