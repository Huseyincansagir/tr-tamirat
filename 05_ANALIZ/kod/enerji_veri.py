"""
Enerji (Faz 4 · Rapor 5) — veri indirme, önbellek ve Türkiye tabloları
=====================================================================
Ne yapar?
  1. TEİAŞ, ETKB ve Ember dosyalarını kaynağından indirir (varsa önbellekten okur):
     03_VERI/ham/enerji/{teias,etkb,ember}/
  2. PVGIS 5.3 (JRC, anahtarsız) yanıtlarını önbelleğe alır: 03_VERI/ham/enerji/pvgis/
       - 10 pilot ilçe: saatlik seri 2019–2023, 5 yönelim (çatı GES modeli için)
       - 6 rüzgâr sahası: saatlik 10 m rüzgâr hızı ve sıcaklık (ERA5, PVGIS üzerinden)
       - 81 il: aylık/yıllık üretim (optimum eğim) ve yatay ışınım
  3. Türkiye tablolarını yazar:
       05_ANALIZ/sonuclar/enerji_turkiye_uretim.csv       (2000–2025, kaynak bazında GWh)
       05_ANALIZ/sonuclar/enerji_turkiye_kurulu_guc.csv   (2006–2025, kaynak bazında MW)
       05_ANALIZ/sonuclar/enerji_turkiye_aylik_2024_2025.csv
       05_ANALIZ/sonuclar/enerji_il_gunes.csv             (81 il, PVGIS)
       05_ANALIZ/sonuclar/enerji_pilot_noktalar.csv

Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/enerji_veri.py
İlk çalıştırma PVGIS'e ≈ 230 istek atar (≈ 10–20 dk); sonra her şey önbellekten gelir.
"""
from __future__ import annotations

import gzip
import json
import sys
import time
import warnings
from pathlib import Path

import pandas as pd
import requests

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")

KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "enerji"
PVG = HAM / "pvgis"
SON = KOK / "05_ANALIZ" / "sonuclar"
ISL = KOK / "03_VERI" / "islenmis"
for d in (HAM / "teias", HAM / "etkb", HAM / "ember", PVG):
    d.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "TR-TAMIRAT arastirma (python-requests)"}

# --------------------------------------------------------------------------------------
# 1. Kurum dosyaları (URL'ler 27.10.2026'da doğrulandı)
# --------------------------------------------------------------------------------------
TEIAS = {  # TEİAŞ "Türkiye Elektrik Üretim-İletim İstatistikleri" (2025 değerleri geçici)
    "T63_uretim_kaynak_2000_2025.xls": "c7c504e8-7656-42b0-8034-4ae46992127d",
    "T9_kurulu_guc_2006_2025.xls": "a54df758-ab25-4c41-87c1-5359c986d77d",
    "T74_aylik_uretim_2024.xls": "0a7b91c7-59d3-41cd-bf0e-1129ef7f5325",
    "T74_aylik_uretim_2025.xls": "9c2686ce-b8be-4c4a-81bc-c9df3320400f",
    "T75_gunes_lisansli_lisanssiz_2024.xls": "bc1b6134-5db4-4536-92d2-b056e9a6c8cc",
    "T75_gunes_lisansli_lisanssiz_2025.xls": "08eba7a9-9f3a-468c-acf0-78afca161f3c",
    "T48_brut_talep.xlsx": "3ecae1f1-1713-417d-97f7-83755a327b9f",
    "T58_kisi_basi.xls": "789fc9d7-3c3a-4feb-8717-42756d803652",
    "T60_net_tuketim_kayiplar.xls": "7007bd85-40fe-412d-8f75-8ae297af2efa",
    "T26_puant.xls": "04975c61-4cba-4fb2-87fa-dc5c2133a8dd",
}
ETKB = {
    "ulusal_enerji_denge_2024.xlsx":
        "https://enerji.gov.tr//Media/Dizin/EIGM/tr/Raporlar/Ulusal_Enerji_Denge_Tablolari/2024_r1.xlsx",
    "sebeke_emisyon_faktoru_2023.pdf":
        "https://enerji.gov.tr//Media/Dizin/EVCED/tr/%C3%87evreVe%C4%B0klim/%C4%B0klimDe%C4%9Fi%C5%9Fikli%C4%9Fi/"
        "EmisyonFaktorleri/2023_Turkiye_Elektrik_UretimiveElektrik_Tuketim_Noktasi_Emisyon_Faktorleri.pdf",
}
EMBER_URL = ("https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/"
             "yearly_full_release_long_format.csv")


def indir(url: str, hedef: Path, zaman=180) -> Path:
    if hedef.exists() and hedef.stat().st_size > 0:
        return hedef
    r = requests.get(url, headers=UA, timeout=zaman)
    r.raise_for_status()
    hedef.write_bytes(r.content)
    print(f"  indirildi: {hedef.name} ({len(r.content) / 1e6:.2f} MB)")
    return hedef


def kurum_dosyalari():
    for ad, kimlik in TEIAS.items():
        try:
            indir(f"https://webim.teias.gov.tr/file/{kimlik}", HAM / "teias" / ad)
        except Exception as e:  # noqa: BLE001
            print(f"  ! TEİAŞ {ad}: {e}")
    for ad, url in ETKB.items():
        try:
            indir(url, HAM / "etkb" / ad)
        except Exception as e:  # noqa: BLE001
            print(f"  ! ETKB {ad}: {e}")
    hedef = HAM / "ember" / "ember_turkiye_yillik.csv"
    if not hedef.exists():
        print("  Ember tam sürümü indiriliyor (≈ 50 MB), yalnız Türkiye satırları saklanır …")
        gecici = HAM / "ember" / "_tam.csv"
        indir(EMBER_URL, gecici, zaman=600)
        df = pd.read_csv(gecici)
        df[df["ISO 3 code"] == "TUR"].to_csv(hedef, index=False)
        gecici.unlink()


# --------------------------------------------------------------------------------------
# 2. TEİAŞ tablolarının okunması
# --------------------------------------------------------------------------------------
def teias_uretim() -> pd.DataFrame:
    x = pd.read_excel(HAM / "teias" / "T63_uretim_kaynak_2000_2025.xls", header=None)
    x = x[pd.to_numeric(x[1], errors="coerce").between(2000, 2030)]
    kol = {1: "yil", 2: "taskomuru_asfaltit", 3: "ithal_komur", 4: "linyit", 5: "komur",
           10: "sivi", 11: "dogal_gaz", 12: "yenilenebilir_atik", 13: "termik", 14: "hidro",
           15: "jeotermal_ruzgar", 16: "gunes", 17: "toplam"}
    d = x[list(kol)].rename(columns=kol).apply(pd.to_numeric, errors="coerce").fillna(0.0)
    d["yil"] = d["yil"].astype(int)
    # rüzgâr–jeotermal ayrımı: 2024–2025 TEİAŞ Tablo 74; önceki yıllar Ember rüzgâr serisi
    em = pd.read_csv(HAM / "ember" / "ember_turkiye_yillik.csv")
    ruz = em[(em.Category == "Electricity generation") & (em.Variable == "Wind") & (em.Unit == "TWh")]
    ruz = ruz.set_index("Year")["Value"] * 1000
    d["ruzgar"] = d["yil"].map(ruz).fillna(0.0)
    ay = teias_aylik()
    for y in (2024, 2025):
        d.loc[d.yil == y, "ruzgar"] = ay[(ay.yil == y)]["ruzgar"].sum()
    d["ruzgar"] = d[["ruzgar", "jeotermal_ruzgar"]].min(axis=1)
    d["jeotermal"] = d["jeotermal_ruzgar"] - d["ruzgar"]
    d["kaynak"] = "TEİAŞ Tablo 63 (2025 geçici); rüzgâr–jeotermal ayrımı: 2024–25 TEİAŞ Tablo 74, önceki yıllar Ember"
    return d


def teias_aylik() -> pd.DataFrame:
    satir = []
    aylar = ["OCAK", "ŞUBAT", "MART", "NİSAN", "MAYIS", "HAZİRAN", "TEMMUZ", "AĞUSTOS", "EYLÜL", "EKİM",
             "KASIM", "ARALIK"]
    for y in (2024, 2025):
        x = pd.read_excel(HAM / "teias" / f"T74_aylik_uretim_{y}.xls", header=None)
        for _, r in x.iterrows():
            ad = str(r[2]).strip()
            if ad in aylar:
                v = pd.to_numeric(r, errors="coerce")
                satir.append(dict(yil=y, ay=aylar.index(ad) + 1, komur=v[5], sivi=v[9], dogal_gaz=v[10],
                                  yenilenebilir_atik=v[11], hidro=v[13], jeotermal=v[14], ruzgar=v[15],
                                  gunes=v[16], toplam=v[17]))
    return pd.DataFrame(satir)


def teias_kurulu() -> pd.DataFrame:
    x = pd.read_excel(HAM / "teias" / "T9_kurulu_guc_2006_2025.xls", header=None)
    x = x[pd.to_numeric(x[2], errors="coerce").between(2000, 2030)]
    kol = {2: "yil", 3: "taskomuru_ithal", 4: "linyit", 5: "sivi", 6: "dogal_gaz", 7: "yenilenebilir_atik",
           9: "kati_sivi", 10: "sivi_gaz", 11: "cok_yakitli", 12: "termik", 13: "hidro", 14: "jeotermal", 15: "ruzgar", 16: "gunes", 17: "toplam"}
    d = x[list(kol)].rename(columns=kol).apply(pd.to_numeric, errors="coerce").fillna(0.0)
    d["yil"] = d["yil"].astype(int)
    d["kaynak"] = "TEİAŞ Tablo 9 (MW, yıl sonu; 2025 geçici)"
    return d


# --------------------------------------------------------------------------------------
# 3. PVGIS (JRC) — anahtarsız API, önbellekli
# --------------------------------------------------------------------------------------
API = "https://re.jrc.ec.europa.eu/api/v5_3"
YON = {  # ad: (eğim, azimut; PVGIS'te 0 = güney, −90 = doğu, 90 = batı)
    "G20": (20, 0), "D20": (20, -90), "B20": (20, 90), "D10": (10, -90), "B10": (10, 90),
}
RUZGAR_SAHALARI = {  # [V] Türkiye RES kapasitesinin yoğunlaştığı bölgeler (Ege, Marmara, Hatay)
    "Izmir_Aliaga": (38.85, 26.95), "Balikesir_Bandirma": (40.30, 27.95), "Canakkale_Ezine": (39.80, 26.35),
    "Manisa_Soma": (39.15, 27.55), "Tekirdag_Sarkoy": (40.65, 27.15), "Hatay_Belen": (36.50, 36.20),
}


def pvgis(uc: str, params: dict, ad: str) -> dict:
    hedef = PVG / f"{ad}.json.gz"
    if hedef.exists():
        with gzip.open(hedef, "rt", encoding="utf-8") as f:
            return json.load(f)
    p = dict(params, outputformat="json")
    for deneme in range(5):
        try:
            r = requests.get(f"{API}/{uc}", params=p, headers=UA, timeout=180)
            if r.status_code == 200:
                js = r.json()
                with gzip.open(hedef, "wt", encoding="utf-8") as f:
                    json.dump(js, f)
                time.sleep(0.4)
                return js
            print(f"  PVGIS {r.status_code} {ad}: {r.text[:200]}")
        except Exception as e:  # noqa: BLE001
            print(f"  PVGIS hata {ad}: {e}")
        time.sleep(3 * (deneme + 1))
    raise RuntimeError(f"PVGIS isteği başarısız: {ad}")


def pilot_noktalar() -> pd.DataFrame:
    """Her pilot ilçede kentsel mahallelerin nüfus ağırlıklı merkezine en yakın mahallenin iç noktası."""
    import geopandas as gpd
    g = gpd.read_file(ISL / "pilot_mahalleler.gpkg")
    g = g[g["kentsel"] == True].copy()  # noqa: E712
    g = g.to_crs(3035)  # ETRS89 / LAEA (metrik)
    g["ic"] = g.geometry.representative_point()
    sat = []
    for ilce, h in g.groupby("ilce"):
        w = h["nufus"].fillna(0)
        cx = (h["ic"].x * w).sum() / w.sum()
        cy = (h["ic"].y * w).sum() / w.sum()
        en = h.iloc[((h["ic"].x - cx) ** 2 + (h["ic"].y - cy) ** 2).values.argmin()]
        p = gpd.GeoSeries([en["ic"]], crs=3035).to_crs(4326).iloc[0]
        sat.append(dict(il=en["il"], ilce=ilce, mahalle=en["mahalle_tuik"], lat=round(p.y, 4), lon=round(p.x, 4),
                        kentsel_nufus=int(w.sum()), pm25_nufus_agirlikli=float((h["pm25"] * w).sum() / w.sum())))
    return pd.DataFrame(sat)


def il_noktalar() -> pd.DataFrame:
    """Her ilin en kalabalık ilçesinin iç noktası (kara üstünde kalması için)."""
    import geopandas as gpd
    g = gpd.read_file(ISL / "ilce_paneli.gpkg")
    g = g.sort_values("nufus_2025", ascending=False).drop_duplicates("il")
    g = g.to_crs(3035)
    g["ic"] = g.geometry.representative_point()
    ic = gpd.GeoSeries(g["ic"].values, crs=3035).to_crs(4326)
    il_nuf = gpd.read_file(ISL / "ilce_paneli.gpkg").groupby("il")["nufus_2025"].sum()
    return pd.DataFrame(dict(il=g["il"].values, ilce=g["ilce_ad_tuik"].values, lat=ic.y.round(4).values,
                             lon=ic.x.round(4).values, il_nufus_2025=g["il"].map(il_nuf).values))


def pvgis_hepsi():
    pil = pilot_noktalar()
    pil.to_csv(SON / "enerji_pilot_noktalar.csv", index=False)
    print(pil[["ilce", "mahalle", "lat", "lon"]].to_string(index=False))
    for _, r in pil.iterrows():
        anahtar = r.ilce.replace("ı", "i").replace("ş", "s").replace("ü", "u").replace("ğ", "g").replace(
            "ç", "c").replace("ö", "o").replace("İ", "I").replace("Ş", "S").replace(" ", "_")
        for yad, (egim, az) in YON.items():
            pvgis("seriescalc", dict(lat=r.lat, lon=r.lon, startyear=2019, endyear=2023, pvcalculation=1,
                                     peakpower=1, loss=14, angle=egim, aspect=az, mountingplace="building"),
                  f"seri_{anahtar}_{yad}")
        print(f"  {r.ilce}: 5 yönelim hazır")
    for ad, (la, lo) in RUZGAR_SAHALARI.items():
        pvgis("seriescalc", dict(lat=la, lon=lo, startyear=2019, endyear=2023, pvcalculation=1, peakpower=1,
                                 loss=14, angle=30, aspect=0, mountingplace="free"), f"seri_ruzgar_{ad}")
    print("  rüzgâr sahaları hazır")
    il = il_noktalar()
    sat = []
    for _, r in il.iterrows():
        a = r.il.replace(" ", "_")
        js = pvgis("PVcalc", dict(lat=r.lat, lon=r.lon, peakpower=1, loss=14, optimalangles=1), f"il_opt_{a}")
        jy = pvgis("PVcalc", dict(lat=r.lat, lon=r.lon, peakpower=1, loss=14, angle=0, aspect=0), f"il_yatay_{a}")
        t = js["outputs"]["totals"]["fixed"]
        m = js["inputs"]["mounting_system"]["fixed"]
        sat.append(dict(il=r.il, ilce=r.ilce, lat=r.lat, lon=r.lon, il_nufus_2025=r.il_nufus_2025,
                        verim_opt_kwh_kwp=t["E_y"], egim_opt=m["slope"]["value"], azimut_opt=m["azimuth"]["value"],
                        isinim_egik_kwh_m2=t["H(i)_y"],
                        isinim_yatay_kwh_m2=jy["outputs"]["totals"]["fixed"]["H(i)_y"],
                        verim_yatay_kwh_kwp=jy["outputs"]["totals"]["fixed"]["E_y"],
                        aralik_kis_kwh_kwp=sum(x["E_m"] for x in js["outputs"]["monthly"]["fixed"] if x["month"] in (12, 1)),
                        haziran_temmuz_kwh_kwp=sum(x["E_m"] for x in js["outputs"]["monthly"]["fixed"] if x["month"] in (6, 7))))
    d = pd.DataFrame(sat).sort_values("verim_opt_kwh_kwp", ascending=False)
    d["kaynak"] = "PVGIS 5.3 (JRC), SARAH3 2005–2023, kayıp %14, c-Si; nokta: ilin en kalabalık ilçesinin iç noktası"
    d.to_csv(SON / "enerji_il_gunes.csv", index=False)
    print(f"  81 il: verim {d.verim_opt_kwh_kwp.min():.0f}–{d.verim_opt_kwh_kwp.max():.0f} kWh/kWp")


def pilot_pvcalc():
    """10 pilot noktada PVGIS PVcalc (peakpower=1, loss=14): optimum eğim ve 20° güney; saatlik serinin sağlaması."""
    pil = pd.read_csv(SON / "enerji_pilot_noktalar.csv")
    sat = []
    for _, r in pil.iterrows():
        a = r.ilce.replace("ı", "i").replace("ş", "s").replace("ü", "u").replace("ğ", "g").replace("ç", "c").replace(
            "ö", "o").replace("İ", "I").replace("Ş", "S").replace(" ", "_")
        jo = pvgis("PVcalc", dict(lat=r.lat, lon=r.lon, peakpower=1, loss=14, optimalangles=1), f"pilot_opt_{a}")
        jg = pvgis("PVcalc", dict(lat=r.lat, lon=r.lon, peakpower=1, loss=14, angle=20, aspect=0), f"pilot_g20_{a}")
        sr = saatlik_seri(f"seri_{a}_G20")
        sat.append(dict(ilce=r.ilce, pvcalc_opt_kwh_kwp=jo["outputs"]["totals"]["fixed"]["E_y"],
                        egim_opt=jo["inputs"]["mounting_system"]["fixed"]["slope"]["value"],
                        pvcalc_g20_kwh_kwp=jg["outputs"]["totals"]["fixed"]["E_y"],
                        seri_g20_2019_2023_kwh_kwp=sr["P"].sum() / 1000 / 5,
                        isinim_opt_kwh_m2=jo["outputs"]["totals"]["fixed"]["H(i)_y"]))
    d = pil.merge(pd.DataFrame(sat), on="ilce")
    d.to_csv(SON / "enerji_pilot_noktalar.csv", index=False)
    print(d[["ilce", "pvcalc_opt_kwh_kwp", "egim_opt", "pvcalc_g20_kwh_kwp", "seri_g20_2019_2023_kwh_kwp"]].round(0).to_string(index=False))


NUFUS_2024 = 85_664_944    # TÜİK ADNKS 2024 [İ]
TWH_KTEP = 11.63 / 1000   # 1 bin tep = 11,63 GWh = 0,01163 TWh


def nihai_sektor() -> pd.DataFrame:
    """ETKB 2024 Ulusal Enerji Denge Tablosu (bin TEP sayfası) → sektör ve yakıt bazında nihai tüketim (TWh)."""
    x = pd.read_excel(HAM / "etkb" / "ulusal_enerji_denge_2024.xlsx", header=None, sheet_name="BİN TEP 2024")
    x[0] = x[0].astype(str).str.strip()
    kol = {"komur": [1, 2, 3, 4, 5, 9], "petrol": [10, 11], "dogal_gaz": [26], "biyokutle_atik": [27], "hidro": [31],
           "ruzgar": [32], "elektrik": [33], "isi": [34], "jeotermal": [35], "gunes": [36]}   # alt toplamlar tekrar sayılmaz
    satirlar = {"Birincil arz": "ENERJİ ÜRÜNLERİ ARZI", "Yerli üretim": "Yerli Üretim", "İthalat": "İthalat (+)",
                "İhracat": "İhracat (-)", "Nihai tüketim": "TOPLAM NİHAİ", "Sanayi": "SANAYİ TÜKETİMİ",
                "Ulaştırma": "ULAŞTIRMA", "Konut": "Konut", "Ticaret ve hizmetler": "Ticaret ve Hizmetler",
                "Tarım": "Tarım ve Hayvancılık", "Enerji dışı": "ENERJİ DIŞI"}
    sat = []
    for ad, bas in satirlar.items():
        r = x[x[0].str.startswith(bas)].iloc[0]
        d = {k: float(pd.to_numeric(r[c], errors="coerce").fillna(0).sum()) * TWH_KTEP for k, c in kol.items()}
        top = float(pd.to_numeric(r[37], errors="coerce")) * TWH_KTEP
        assert abs(sum(d.values()) - top) < 0.01 * abs(top) + 0.1, ad
        sat.append(dict(sektor=ad, **{f"{k}_twh": val for k, val in d.items()}, toplam_twh=top, toplam_ktep=top / TWH_KTEP,
                        elektrik_kisi_basi_kwh=d["elektrik"] * 1e9 / NUFUS_2024,
                        toplam_kisi_basi_kwh=top * 1e9 / NUFUS_2024, nufus=NUFUS_2024))
    d = pd.DataFrame(sat)
    d["yil"] = 2024
    d["kaynak"] = "ETKB 2024 Ulusal Enerji Denge Tablosu (yayım 15.11.2025), bin TEP; nüfus TÜİK ADNKS 2024"
    d.to_csv(SON / "enerji_turkiye_nihai_sektor.csv", index=False)
    arz = d.set_index("sektor")
    print(f"  dışa bağımlılık 1 − yerli/arz = {1 - arz.loc['Yerli üretim', 'toplam_twh'] / arz.loc['Birincil arz', 'toplam_twh']:.1%}")
    return d


def saatlik_seri(ad: str) -> pd.DataFrame:
    """Önbellekteki PVGIS saatlik serisini DataFrame olarak verir (P: W/kWp, T2m, WS10m)."""
    with gzip.open(PVG / f"{ad}.json.gz", "rt", encoding="utf-8") as f:
        js = json.load(f)
    d = pd.DataFrame(js["outputs"]["hourly"])
    d["zaman"] = pd.to_datetime(d["time"], format="%Y%m%d:%H%M")
    return d


# --------------------------------------------------------------------------------------
# 4. Derlenmiş göstergeler ve maliyet karşılaştırması (kaynak ve işaretle)
# --------------------------------------------------------------------------------------
GOSTERGELER = [
    # (başlık, gösterge, değer, birim, yıl, kaynak, işaret)
    ("Elektrik", "Brüt üretim", 366.92, "TWh", 2025, "TEİAŞ Tablo 63 (geçici)", "D"),
    ("Elektrik", "Brüt üretim", 354.57, "TWh", 2024, "TEİAŞ Tablo 63", "D"),
    ("Elektrik", "Brüt talep", 364.83, "TWh", 2025, "TEİAŞ Tablo 48", "D"),
    ("Elektrik", "Net tüketim", 319.71, "TWh", 2025, "TEİAŞ Tablo 60", "D"),
    ("Elektrik", "Kurulu güç (yıl sonu)", 123.303, "GW", 2025, "TEİAŞ Tablo 9", "D"),
    ("Elektrik", "Kurulu güç (31.08.2026)", 126.944, "GW", 2026, "ETKB Ağustos 2026 aylık özet", "D"),
    ("Elektrik", "Güneş kurulu gücü (lisanssız 23,4 GW dahil)", 25.927, "GW", 2025, "TEİAŞ Tablo 9, 14", "D"),
    ("Elektrik", "Rüzgâr kurulu gücü", 14.792, "GW", 2025, "TEİAŞ Tablo 9", "D"),
    ("Elektrik", "Eklenen güneş / rüzgâr", "5,7 / 1,9", "GW", 2025, "TEİAŞ Tablo 9 farkı", "H"),
    ("Elektrik", "Anlık puant", 60.406, "GW", 2025, "TEİAŞ Tablo 26 (28.07.2025, 15:00)", "D"),
    ("Elektrik", "Kişi başı brüt talep", 4241, "kWh/kişi", 2025, "TEİAŞ Tablo 58", "D"),
    ("Elektrik", "Kişi başı net tüketim", 3717, "kWh/kişi", 2025, "TEİAŞ Tablo 58", "D"),
    ("Elektrik", "Mesken tüketimi", 78.197, "TWh", 2025, "EPDK Elektrik Piyasası Gelişim Raporu 2025, Tablo 1.13", "D"),
    ("Elektrik", "Hane başı mesken tüketimi", 2899, "kWh/hane", 2025, "78.197 GWh / 26.977.795 hane (TÜİK)", "H"),
    ("Elektrik", "Dağıtım kaybı", 6.33, "%", 2025, "TEİAŞ Tablo 60", "D"),
    ("Elektrik", "Dağıtım kaybı, Dicle / Vangölü", "35,5 / 23,5", "%", 2025, "EPDK 2025 Tablo 5.2", "D"),
    ("Elektrik", "İletim kaybı", 1.68, "%", 2025, "TEİAŞ Tablo 60 (EPDK: %1,96)", "D"),
    ("Elektrik", "PTF ağırlıklı ortalaması", 2651.81, "TL/MWh", 2025, "EPDK 2025 (≈ 67 $/MWh, TCMB yıllık kur 39,48)", "D"),
    ("Elektrik", "Şebeke emisyon faktörü", 0.430, "tCO2/MWh", 2023, "ETKB-EVÇED (yayım 26.12.2025)", "D"),
    ("Elektrik", "Elektrik sektörü CO2", 168.3, "Mt", 2025, "Ember yıllık verisi", "İ"),
    ("Birincil enerji", "Birincil enerji arzı", 165.21, "Mtep", 2024, "ETKB Ulusal Enerji Denge Tablosu 2024", "D"),
    ("Birincil enerji", "Pay: petrol / gaz / kömür / yenilenebilir ve diğer", "29,2 / 26,6 / 25,6 / 18,6", "%", 2024, "ETKB denge tablosu", "D"),
    ("Birincil enerji", "Dışa bağımlılık (net ithalat / arz)", 66.9, "%", 2024, "ETKB denge tablosu (SBB: %67)", "H"),
    ("Birincil enerji", "Enerji ithalat faturası (fasıl 27)", None, "milyar $", 2025, "TÜİK erişilemedi", "DY"),
    ("Nihai enerji", "Sanayi / ulaştırma / konut / ticaret-hizmet / tarım", "31,8 / 28,5 / 24,1 / 10,7 / 4,8", "% (enerji dışı hariç)", 2024, "ETKB denge tablosu", "H"),
    ("Isınma", "Doğal gaz tüketimi", 59.07, "milyar Sm³", 2025, "EPDK Doğal Gaz Piyasası Gelişim Raporu 2025", "D"),
    ("Isınma", "Doğal gazda konut payı", 35.3, "%", 2025, "EPDK 2025 (20,86 milyar Sm³)", "H"),
    ("Isınma", "Doğal gaz ithalatı / yerli üretim", "58,34 / 3,11", "milyar Sm³", 2025, "EPDK 2025", "D"),
    ("Isınma", "Gaz verilen yerleşim", "81 il, 840 ilçe, 142 belde", "—", 2025, "EPDK 2025", "D"),
    ("Isınma", "Konut nihai enerjisinde gaz / elektrik / kömür / odun", "53,6 / 22,0 / 9,9 / 4,5", "%", 2024, "ETKB denge tablosu", "H"),
    ("Isınma", "Konut doğal gaz fiyatı (vergiler dahil)", 13.19, "TL/Sm³", 2025, "EPDK 2025 Tablo 9.1, II. yarıyıl (sanayi 19,29)", "D"),
    ("Ulaşım", "Motorin / benzin / otogaz satışı", "27,08 / 5,70 / 3,28", "milyon ton", 2025, "EPDK Petrol ve LPG Piyasası Gelişim Raporları 2025", "D"),
    ("Ulaşım", "Elektrikli otomobilin yeni kayıt payı", 18.6, "%", 2026, "TÜİK Motorlu Kara Taşıtları, Ocak–Eylül 2026", "D"),
    ("Ulaşım", "Şarj noktası", 45871, "adet", 2026, "SBB 2027 Yıllık Programı (Temmuz 2026)", "D"),
    ("Hedef", "Ulusal Enerji Planı 2035: kurulu güç / güneş / rüzgâr / nükleer", "189,7 / 52,9 / 29,6 / 7,2", "GW", 2035, "ETKB TUEP (2022)", "D"),
    ("Hedef", "Ulusal Enerji Planı 2035: elektrik tüketimi", 510.5, "TWh", 2035, "ETKB TUEP", "D"),
    ("Hedef", "Ulusal Enerji Planı 2035: batarya", 7.5, "GW", 2035, "ETKB TUEP", "D"),
    ("Hedef", "2050'ler nükleer hedefi (12 büyük reaktör + 5 GW SMR)", 20, "GW", 2050, "Bakan açıklaması Kasım 2025; WNA World Nuclear Outlook, Türkiye", "İ"),
    ("Nükleer", "Akkuyu: 4 × VVER-1200; 1. ünitede ilk elektrik hedefi", "2026 sonu", "—", 2026, "ETKB Bakanı açıklamaları (Haziran 2026); 2024 ve 2025 hedefleri kaçtı", "İ"),
    ("Nükleer", "Akkuyu 1. ünitede gerçek yakıt yüklemesi (27.10.2026 itibarıyla)", "doğrulanamadı", "—", 2026, "basın taraması; yalnız temsili yakıt yüklemesi bildirildi", "DY"),
    ("Nükleer", "İlk SMR'nin devreye alınma hedefi", "2030'ların ilk yarısı", "—", 2025, "ETKB Bakanı; Daily Sabah", "İ"),
    ("Nükleer", "Nükleer Düzenleme Kanunu", "7381", "sayı", 2022, "RG 08.03.2022, 31772 (mevzuat derleyicileri)", "İ"),
    ("Nüfus", "2050 nüfus projeksiyonu (ana senaryo)", 93.77, "milyon", 2050, "TÜİK Nüfus Projeksiyonları 2023–2100", "İ"),
    ("Hedef", "Net sıfır", 2053, "yıl", 2021, "SBB; TUEP", "D"),
    ("Sağlık", "PM2.5'e bağlı erken ölüm", 62644, "kişi", 2024, "Temiz Hava Hakkı Platformu, Kara Rapor 2025", "D"),
    ("Sağlık", "Kömür santrallerine bağlı erken ölüm", 4818, "kişi", 2019, "HEAL/CREA, Chronic Coal Pollution – Türkiye (2021)", "D"),
    ("Sağlık", "Birincil PM2.5'te konut yanmasının payı", 54.0, "%", 2022, "ÇŞİDB IIR 2024 (1A4bi); kamu elektrik ve ısı üretimi %6,2", "D"),
]

MALIYET = [
    # (grup, teknoloji, alt, üst, birim, yıl, kaynak, işaret)
    ("Lazard LCOE+ 2026 (ABD, sübvansiyonsuz)", "Kamu ölçekli güneş", 40, 98, "$/MWh", 2026, "Lazard v19", "D"),
    ("Lazard LCOE+ 2026 (ABD, sübvansiyonsuz)", "Güneş + depolama", 61, 156, "$/MWh", 2026, "Lazard v19", "D"),
    ("Lazard LCOE+ 2026 (ABD, sübvansiyonsuz)", "Kara rüzgârı", 37, 99, "$/MWh", 2026, "Lazard v19", "D"),
    ("Lazard LCOE+ 2026 (ABD, sübvansiyonsuz)", "Rüzgâr + depolama", 49, 140, "$/MWh", 2026, "Lazard v19", "D"),
    ("Lazard LCOE+ 2026 (ABD, sübvansiyonsuz)", "Deniz üstü rüzgâr", 105, 167, "$/MWh", 2026, "Lazard v19", "D"),
    ("Lazard LCOE+ 2026 (ABD, sübvansiyonsuz)", "Çatı GES (ticari, topluluk)", 88, 197, "$/MWh", 2026, "Lazard v19", "D"),
    ("Lazard LCOE+ 2026 (ABD, sübvansiyonsuz)", "Jeotermal", 67, 111, "$/MWh", 2026, "Lazard v19", "D"),
    ("Lazard LCOE+ 2026 (ABD, sübvansiyonsuz)", "Doğal gaz kombine çevrim", 51, 129, "$/MWh", 2026, "Lazard v19", "D"),
    ("Lazard LCOE+ 2026 (ABD, sübvansiyonsuz)", "Kömür", 72, 177, "$/MWh", 2026, "Lazard v19", "D"),
    ("Lazard LCOE+ 2026 (ABD, sübvansiyonsuz)", "Yeni nükleer (Vogtle verisi)", 175, 255, "$/MWh", 2026, "Lazard v19", "D"),
    ("Lazard LCOE+ 2026 (ABD, sübvansiyonsuz)", "SMR (Clinch River, Darlington, Natrium örnekleri)", 214, 214, "$/MWh", 2026,
     "Lazard v19 (13.07.2026), 'örnek niteliğinde, 2030 sonrası işletme'", "D"),
    ("IRENA 2025, küresel ağırlıklı ortalama", "Güneş", 44, 44, "$/MWh", 2025, "IRENA RPGC 2025", "D"),
    ("IRENA 2025, küresel ağırlıklı ortalama", "Kara rüzgârı", 33, 33, "$/MWh", 2025, "IRENA RPGC 2025", "D"),
    ("IRENA 2025, küresel ağırlıklı ortalama", "Deniz üstü rüzgâr", 78, 78, "$/MWh", 2025, "IRENA RPGC 2025", "D"),
    ("IRENA 2025, küresel ağırlıklı ortalama", "Hidro", 62, 62, "$/MWh", 2025, "IRENA RPGC 2025", "D"),
    ("IRENA 2025, küresel ağırlıklı ortalama", "Jeotermal", 89, 89, "$/MWh", 2025, "IRENA RPGC 2025", "D"),
    ("IRENA 2025, küresel ağırlıklı ortalama", "Biyokütle", 86, 86, "$/MWh", 2025, "IRENA RPGC 2025", "D"),
    ("IRENA, Türkiye", "Güneş (kamu ölçekli, 2025)", 86, 86, "$/MWh", 2025, "IRENA RPGC 2025, Şekil 3.7", "D"),
    ("IRENA, Türkiye", "Kara rüzgârı (2025)", 61, 61, "$/MWh", 2025, "IRENA RPGC 2025, Şekil 2.11", "D"),
    ("IRENA, Türkiye", "Jeotermal (2024)", 33, 33, "$/MWh", 2024, "IRENA RPGC 2024", "D"),
    ("Türkiye sözleşme fiyatları", "YEKA GES-2024 (20 yıl, önce 5 yıl piyasa)", 32.5, 32.5, "$/MWh", 2025, "BGEN, Şubat 2025", "İ"),
    ("Türkiye sözleşme fiyatları", "YEKA RES-2024 (20 yıl, önce 6 yıl piyasa)", 35, 35, "$/MWh", 2025, "BGEN, Ocak 2025", "İ"),
    ("Türkiye sözleşme fiyatları", "YEKA GES-2025 (taban 3,25 €¢/kWh + katkı payı)", 36.7, 36.7, "$/MWh", 2025,
     "ETKB ilanı; basın (QNB, Bloomberg HT); 1,13 $/€ [V]", "İ"),
    ("Türkiye sözleşme fiyatları", "YEKA RES-2025 (3,50 €¢/kWh + 212–312 bin €/MW katkı payı)", 39.6, 39.6, "$/MWh", 2025,
     "AA/Forbes, 09.12.2025; 1,13 $/€ [V]", "İ"),
    ("Türkiye sözleşme fiyatları", "Akkuyu alım garantisi (12,35 ¢/kWh, 15 yıl)", 123.5, 123.5, "$/MWh", 2010, "Hükümetlerarası anlaşma; WNA", "D"),
    ("Türkiye sözleşme fiyatları", "PTF ortalaması 2025 (piyasa)", 67.2, 67.2, "$/MWh", 2025, "EPDK; TCMB kuru", "H"),
]


def derleme_tablolari():
    pd.DataFrame(GOSTERGELER, columns=["baslik", "gosterge", "deger", "birim", "yil", "kaynak", "isaret"]).to_csv(
        SON / "enerji_turkiye_gostergeler.csv", index=False)
    pd.DataFrame(MALIYET, columns=["grup", "teknoloji", "alt", "ust", "birim", "yil", "kaynak", "isaret"]).to_csv(
        SON / "enerji_lcoe_karsilastirma.csv", index=False)


def main():
    print("1) Kurum dosyaları")
    kurum_dosyalari()
    print("2) TEİAŞ tabloları")
    u = teias_uretim()
    u.to_csv(SON / "enerji_turkiye_uretim.csv", index=False)
    teias_kurulu().to_csv(SON / "enerji_turkiye_kurulu_guc.csv", index=False)
    a = teias_aylik()
    a["kaynak"] = "TEİAŞ Tablo 74 (GWh; 2025 geçici)"
    a.to_csv(SON / "enerji_turkiye_aylik_2024_2025.csv", index=False)
    son = u[u.yil == 2025].iloc[0]
    print(f"  2025 brüt üretim {son.toplam / 1000:.1f} TWh; kömür {son.komur / son.toplam:.1%}")
    derleme_tablolari()
    print("3) PVGIS")
    pvgis_hepsi()
    pilot_pvcalc()
    print("4) ETKB nihai enerji (sektör)")
    nihai_sektor()


if __name__ == "__main__":
    main()
