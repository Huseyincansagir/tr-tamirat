"""
TKGM MEGSİS idari yapı servisinden pilot ilçelerin mahalle sınırları
====================================================================
Kaynak : https://cbsapi.tkgm.gov.tr/megsiswebapi.v3/api/idariYapi/{ilListe | ilceListe/<il_id> | mahalleListe/<ilce_id>}
         (Parsel Sorgu uygulamasının herkese açık arka ucu; anahtarsız; GeoJSON)
Çıktı  : 03_VERI/ham/tkgm/il_liste.geojson, ilce_<il_id>.geojson, mahalle_<ilce_id>.geojson
         03_VERI/islenmis/pilot_mahalle_tkgm.gpkg (10 ilçe, birleşik)
Not    : TKGM mahalleleri kadastro mahalleleridir; adları ve sınırları çoğunlukla idari (ADNKS) mahallelerle örtüşür,
         ama birebir değildir. Eşleştirme 05_ANALIZ/kod/fue_mahalle.py içinde yapılır.
"""
import json
import sys
import time
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "tkgm"
HAM.mkdir(parents=True, exist_ok=True)
API = "https://cbsapi.tkgm.gov.tr/megsiswebapi.v3/api/idariYapi/"
PILOT = {"İstanbul": ["Fatih", "Silivri", "Başakşehir"], "Bursa": ["Nilüfer"], "Kayseri": ["Kocasinan"],
         "Konya": ["Meram"], "Hatay": ["Antakya"], "Kahramanmaraş": ["Onikişubat"], "Karabük": ["Safranbolu"],
         "Ankara": ["Beypazari"]}  # TKGM listesinde "Beypazari"


def al(yol, dosya):
    f = HAM / dosya
    if not f.exists():
        for deneme in range(4):
            try:
                r = requests.get(API + yol, headers={"User-Agent": "Mozilla/5.0"}, timeout=90)
                r.raise_for_status()
                f.write_text(r.text, encoding="utf-8")
                break
            except Exception as e:
                print("  yeniden:", yol, e)
                time.sleep(5)
        time.sleep(1.5)
    return json.loads(f.read_text(encoding="utf-8"))


iller = {f["properties"]["text"]: f["properties"]["id"] for f in al("ilListe", "il_liste.geojson")["features"]}
parcalar = []
for il, ilceler in PILOT.items():
    ic = {f["properties"]["text"]: f["properties"]["id"] for f in al(f"ilceListe/{iller[il]}", f"ilce_{iller[il]}.geojson")["features"]}
    for ilce in ilceler:
        js = al(f"mahalleListe/{ic[ilce]}", f"mahalle_{ic[ilce]}.geojson")
        g = gpd.GeoDataFrame.from_features(js["features"], crs=4326)
        g["il"], g["ilce"], g["tkgm_ilce_id"] = il, ilce, ic[ilce]
        parcalar.append(g)
        print(il, ilce, "mahalle:", len(g))
m = pd.concat(parcalar, ignore_index=True).rename(columns={"text": "mahalle_tkgm", "id": "tkgm_mahalle_id"})
m.to_file(KOK / "03_VERI" / "islenmis" / "pilot_mahalle_tkgm.gpkg", driver="GPKG")
print("toplam:", len(m), "| sütunlar:", list(m.columns))
