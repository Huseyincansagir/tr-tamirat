"""
Faz 4 · Rapor 7 — Ticaretin önündeki engeller ve kendi kendine yeterlilik: tablolar
==================================================================================
Ham dosyalar: 03_VERI/ham/ekonomi/ticaret_tarim/ (indirme yolları kaynaklar.md'de) ve 03_VERI/ham/ekonomi/sdmx/.
Makine tarafından okunabilen kaynaklar (OECD PMR, B-READY sütun puanları, TÜİK SDMX kayıt dışı istihdam,
UN Comtrade) dosyadan hesaplanır. PDF ve bülten kaynaklı değerler (Rekabet Kurumu HTM raporu, TESK, TOBB,
TÜİK bitkisel ürün denge tabloları, TEPGE) elle aktarıldı; sayfa ve tablo numaraları satırlarda yazılı.

Çıktı: 05_ANALIZ/sonuclar/ekonomi_ticaret_*.csv, ekonomi_yeterlilik_*.csv
"""
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "ekonomi"
TT = HAM / "ticaret_tarim"
SON = KOK / "05_ANALIZ" / "sonuclar"


def yaz(df, ad):
    df.to_csv(SON / f"ekonomi_{ad}.csv", index=False, encoding="utf-8")
    print(f"  -> ekonomi_{ad}.csv  {df.shape}")


# ----------------------------------------------------------------------------- 1. OECD PMR 2018 ve 2023
pmr = pd.read_csv(TT / "oecd_pmr_2018_2023.csv")
OLC = {"PMR": "Genel PMR", "ADREG_BURDEN": "İdari ve düzenleyici yük",
       "ADBURDEN": "LŞ ve şahıs işletmesi kurmanın idari şartları", "BARRIER_ENTRY": "Yerli ve yabancı girişe engeller",
       "BARRIER_DOM": "Hizmet ve şebeke sektörlerinde engeller", "RETAIL_TRADE": "Perakende dağıtım",
       "PRICE": "Perakende fiyat kontrolleri", "STATE_INVOL": "Devlet müdahalesinden kaynaklı bozulma",
       "INVOL_BUSINESS": "Devletin iş faaliyetine katılımı", "PUBLIC_PROCUREMENT": "Kamu alımları"}
OECD38 = ["AUS", "AUT", "BEL", "CAN", "CHL", "COL", "CRI", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "ISL", "IRL",
          "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX", "MEX", "NLD", "NZL", "NOR", "POL", "PRT", "SVK", "SVN", "ESP", "SWE",
          "CHE", "TUR", "GBR", "USA"]
mev = pmr.MEASURE.unique().tolist()
print("PMR ölçüleri (ilk 40):", mev[:40])
secili = [m for m in OLC if m in mev]
p = pmr[pmr.MEASURE.isin(secili) & pmr.REF_AREA.isin(OECD38)].pivot_table(index=["MEASURE", "TIME_PERIOD"],
                                                                         columns="REF_AREA", values="OBS_VALUE")
out = pd.DataFrame({"turkiye": p["TUR"], "oecd_ortalama": p.mean(axis=1), "oecd_ulke_sayisi": p.notna().sum(axis=1),
                    "turkiye_sira_kisitlayicidan": p.rank(axis=1, ascending=False)["TUR"]}).reset_index()
out["olcu"] = out.MEASURE.map(OLC)
yaz(out.round(3), "ticaret_pmr")
print(out[out.TIME_PERIOD == 2023][["olcu", "turkiye", "oecd_ortalama", "turkiye_sira_kisitlayicidan", "oecd_ulke_sayisi"]].to_string())

# ----------------------------------------------------------------------------- 2. B-READY 2025
z = zipfile.ZipFile(TT / "B-READY_ALL_DATA_2025.zip")
bp = pd.read_excel(io.BytesIO(z.read("01_B-READY-2025-PILLAR-TOPIC-SCORES.xlsx")), sheet_name="00_B-READY_Pillar_Score")
bp.columns = ["ulke", "kod", "duzenleyici_cerceve", "kamu_hizmetleri", "operasyonel_verimlilik"]
bp = bp.dropna(subset=["kod"])
tr = bp[bp.kod == "TUR"].iloc[0]
ort = bp[["duzenleyici_cerceve", "kamu_hizmetleri", "operasyonel_verimlilik"]].astype(float).mean()
sira = bp[["duzenleyici_cerceve", "kamu_hizmetleri", "operasyonel_verimlilik"]].astype(float).rank(ascending=False)[bp.kod == "TUR"].iloc[0]
br = pd.DataFrame({"sutun": ort.index, "turkiye": [float(tr[c]) for c in ort.index], "orneklem_ortalama": ort.values,
                   "turkiye_sira": sira.values, "ulke_sayisi": len(bp)})
yaz(br.round(2), "ticaret_bready_sutun")
# konu puanları (alt ajan okuması, aynı dosyanın konu sayfaları) [D]
konu = pd.DataFrame([("İşletme kurma", 80.4), ("İşyeri yeri (imar, mülk, çevre izni)", 72.3), ("Altyapı hizmetleri", 86.5),
                     ("İşgücü", 67.2), ("Finansal hizmetler", 75.9), ("Uluslararası ticaret", 58.1), ("Vergilendirme", 46.4),
                     ("Uyuşmazlık çözümü", 60.9), ("Piyasa rekabeti", 57.9), ("İflas", 71.5)], columns=["konu", "turkiye_puan"])
yaz(konu, "ticaret_bready_konu")

# ----------------------------------------------------------------------------- 3. Perakende yoğunlaşması ve esnaf
# Rekabet Kurumu, HTM Perakendeciliği Sektör İncelemesi Nihai Raporu (2023): Tablo 1–2 (s. 35–36), 6–8 (s. 41–44), 19 (s. 47)
htm = pd.DataFrame([
    ("Organize kanalın HTM cirosundaki payı (%)", 47.0, 54.2, "Tablo 2, s. 36 (Nielsen)"),
    ("Toplam HTM pazarında ilk 3 zincirin payı, CR3 (%)", 43.69, 49.88, "Tablo 6, s. 41"),
    ("Toplam HTM pazarında ilk 4 zincirin payı, CR4 (%)", 51.92, 59.15, "Tablo 6, s. 41"),
    ("Organize pazarda CR4 (%)", np.nan, 77.45, "Tablo 7–8, s. 42–44 (2011: 66,47)"),
    ("Mağaza sayısı: geleneksel kanal", np.nan, 188915, "Tablo 1, s. 35"),
    ("Mağaza sayısı: organize kanal", np.nan, 39147, "Tablo 1, s. 35"),
    ("A101 mağaza", np.nan, 11227, "Tablo 19, s. 47 (2011: 1.287)"), ("BİM mağaza", np.nan, 9611, "Tablo 19 (2011: 3.315)"),
    ("ŞOK mağaza", np.nan, 9247, "Tablo 19"), ("Migros mağaza", np.nan, 2565, "Tablo 19"),
], columns=["gosterge", "y2019", "y2021", "kaynak_yeri"])
yaz(htm, "ticaret_perakende")
esnaf = pd.DataFrame([
    ("TESK kayıtlı esnaf ve sanatkâr (30.09.2026)", 2282188, "D", "TESK sicil istatistiği 4.pdf"),
    ("TESK esnaf açılış (tescil) 2024", 287624, "D", "TESK sicil 2024"), ("TESK esnaf açılış 2025", 323480, "D", "TESK sicil 2025"),
    ("TESK esnaf kapanış (terkin) 2024", 120005, "D", "TESK sicil 2024"), ("TESK esnaf kapanış 2025", 120423, "D", "TESK sicil 2025"),
    ("TOBB kurulan şirket 2025 (kooperatif dahil)", 115627, "D", "TOBB 2025-12.xls"), ("TOBB kapanan şirket 2025", 34546, "D", "TOBB 2025-12.xls"),
    ("Doing Business 2020: işletme kurma, gün", 7, "D", "DB2020 Türkiye profili s. 4"),
    ("Doing Business 2020: inşaat izni, gün", 100, "D", "DB2020 Türkiye profili s. 10"),
    ("Doing Business 2020: inşaat izni, prosedür", 18, "D", "DB2020 Türkiye profili s. 10"),
    ("Kayıt dışı üretim / GSYH 2020, MIMIC (%)", 31.0, "D", "Dünya Bankası Informal Economy Database"),
    ("Kayıt dışı üretim / GSYH 2020, DGE (%)", 24.2, "D", "Dünya Bankası Informal Economy Database"),
    ("Kayıt dışı firmalarla rekabet eden firma payı 2019 (%)", 50.2, "D", "Dünya Bankası Enterprise Survey"),
    ("H-ÜFE gayrimenkul kiralama (NACE 68.20) yıllık değişim, Ara 2024 (%)", 47.2, "D", "TÜİK SDMX"),
    ("H-ÜFE gayrimenkul kiralama yıllık değişim, Ağu 2026 (%)", 20.8, "D", "TÜİK SDMX"),
], columns=["gosterge", "deger", "isaret", "kaynak"])
yaz(esnaf, "ticaret_esnaf_kayitdisi")

# Kayıt dışı istihdam oranı (TÜİK SDMX, SGK_KAYIT=3: kayıtsız oranı) — yıllık çeyrek ortalaması
kd = pd.read_csv(HAM / "sdmx" / "DF_ISGUCU_CEYREK_SGK_KAYIT_C_uzun.csv", dtype=str)
kd["deger"] = kd.deger.astype(float)
kd = kd[(kd.SGK_KAYIT == "3") & (kd.SEX == "_T")]
kdy = kd.pivot_table(index="yil", columns="TARIM_TARIMDISI", values="deger", aggfunc="mean").rename(
    columns={"_T": "toplam", "1": "tarim", "2": "tarim_disi"})
kdy["ceyrek_sayisi"] = kd[kd.TARIM_TARIMDISI == "_T"].groupby("yil").deger.count()
yaz(kdy.reset_index().round(2), "kayit_disi_istihdam")
print(kdy.round(1).tail(6).to_string())

# ----------------------------------------------------------------------------- 4. Kendi kendine yeterlilik
# TÜİK Bitkisel Ürün Denge Tabloları (bültenler 24584, 27644, 30693, 33740, 37246, 45505, 49456, 53451, 53941;
# eski bülten sayfalarının arşiv kopyalarından okundu) [D]; 2024/25 sütunu basın aktarımı (iscihaber.net,
# alomaliye.com, 27.03.2026) [İ]. Boş = kaynakta yok.
Y = ["2015/16", "2016/17", "2017/18", "2018/19", "2019/20", "2020/21", "2021/22", "2022/23", "2023/24", "2024/25"]
n = np.nan
bit = {
    "Tahıl toplamı": [110.2, 97.2, 98.0, 92.4, 87.8, 97.4, 80.3, 92.3, 111.9, 91.1],
    "Buğday": [113.6, 103.8, 111.7, 100.5, 89.5, 102.3, 87.3, 95.9, 118.4, 104.3],
    "Arpa": [106.5, 89.2, 90.2, 94.7, 94.8, 97.1, 66.8, 90.0, 115.7, 84.6],
    "Mısır": [105.0, 87.8, 73.3, 70.3, 75.5, 84.9, 76.6, 85.8, 96.5, 73.1],
    "Pirinç": [n, n, n, n, n, 81.2, 75.4, 74.3, 71.8, n],
    "Kuru fasulye": [n, n, n, 72.1, 76.0, 92.0, 106.7, 91.4, 84.5, n],
    "Kırmızı mercimek": [81.6, 76.7, 89.6, 74.9, 71.7, 71.2, 57.0, 85.9, 91.0, n],
    "Yeşil mercimek": [n, n, n, 86.8, 85.3, 58.7, 50.9, 60.2, 77.5, n],
    "Nohut": [98.1, 92.1, 87.5, 114.0, 127.5, 122.3, 96.0, 117.8, 115.3, n],
    "Patates": [100.8, 108.2, 103.5, 103.3, 104.1, 106.5, 106.1, 103.6, 102.0, n],
    "Kuru soğan": [n, n, n, 97.4, 113.1, 114.2, 114.7, 102.9, 105.1, n],
    "Domates": [n, n, n, 110.6, 110.7, 117.0, 123.7, 117.5, 117.1, 112.3],
    "Sebze toplamı": [n, n, n, 106.4, 107.2, 110.9, 113.5, 111.3, 111.3, 108.8],
    "Ayçiçeği": [78.9, 64.0, 64.3, 66.4, 60.1, 62.5, 59.6, 51.3, 71.9, n],
    "Soya": [6.9, 7.1, 4.8, 5.7, 4.7, 5.4, 6.0, 5.2, 4.1, 4.2],
    "Kolza": [26.9, 76.7, 70.3, 132.9, 95.1, 111.2, 116.7, 47.9, 100.3, n],
    "Şeker pancarı (2015–18: şeker)": [94.4, 103.0, 116.1, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, n],
    "Pamuk (çiğit)": [n, n, n, 104.3, 104.8, 103.7, 101.1, 105.9, 97.7, n],
    "Elma": [n, n, n, 142.5, 128.5, 143.9, 170.0, 143.6, 151.6, n],
    "Fındık": [n, n, n, 445.5, 563.9, 552.9, 560.9, 683.5, 573.6, n],
    "Çay": [n, n, n, 96.8, 95.5, 94.1, 97.9, 97.9, 95.8, 96.1],
}
bt = pd.DataFrame(bit, index=Y).T
bt.index.name = "urun"
bt["son_5_ort"] = bt[Y[-5:]].mean(axis=1)
bt["en_dusuk"] = bt[Y].min(axis=1)
yaz(bt.reset_index().round(1), "yeterlilik_bitkisel")

# Hayvansal ürünler: TÜİK hayvansal denge tablolarına erişilemedi; TEPGE Durum-Tahmin 2025 raporlarındaki TÜİK
# kaynaklı üretim ve tüketim değerlerinden üretim / tüketim × 100 (TÜİK yeterlilik formülüne denk) [H]
hay = pd.DataFrame({"Kırmızı et": [n, n, 99.8, 100.0, 100.2, 98.5, 96.4],
                    "Tavuk eti": [126.1, 125.5, 128.6, 131.8, 133.1, 122.5, 114.8],
                    "Yumurta": [140.5, 127.6, 124.8, 122.1, 121.4, 118.3, 117.4]},
                   index=[2018, 2019, 2020, 2021, 2022, 2023, 2024]).T
hay.index.name = "urun"
yaz(hay.reset_index(), "yeterlilik_hayvansal")

# Tarım-gıda ve enerji dış ticareti (UN Comtrade, Türkiye beyanı) [D]
ct = pd.read_csv(TT / "comtrade_turkiye_ithalat_secili_HS_2018_2025.csv")
ct["hs"] = ct.hs.astype(str)
ADLAR = {"102": "Canlı sığır (0102)", "2": "Et (HS 02)", "12": "Yağlı tohum (HS 12)", "15": "Bitkisel ve hayvansal yağ (HS 15)",
         "1512": "Ayçiçek yağı (1512)"}
cti = ct[ct.hs.isin(ADLAR) & (ct.akis == "M")].pivot_table(index="hs", columns="yil", values="deger_usd") / 1e6
cti.index = [ADLAR[i] for i in cti.index]
yaz(cti.reset_index().rename(columns={"index": "kalem"}).round(0), "yeterlilik_ithalat_mn_usd")
tp = pd.read_csv(TT / "comtrade_turkiye_2025_fasil_01-24_27_toplam.csv")
print(tp.head(10).to_string())
print("\nticaret ve yeterlilik tabloları tamam.")
