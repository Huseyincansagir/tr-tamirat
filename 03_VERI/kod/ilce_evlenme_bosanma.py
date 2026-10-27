"""
İlçe bazında evlenme (2001–2025) ve boşanma (2014–2025) sayıları — TÜİK SDMX
Girdi : 03_VERI/ham/tuik/sdmx/DF_EVLENME_IL_ILCE.json, DF_BOSANMA_IL_ILCE.json (boş filtreyle indirildi)
Çıktı : 03_VERI/islenmis/ilce_evlenme_bosanma.csv
Not   : Evlenmeler olay (tescil) yerine, boşanmalar karar veren mahkemenin yerine göre kaydedilir; adliyesi olmayan
        ilçelerde boşanma sıfır görünür. Bu yüzden boşanma yalnızca il ya da adliye yargı çevresi düzeyinde anlamlıdır.
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "tuik" / "sdmx"


def jsonstat_df(d):
    ids, boy = d["id"], d["size"]
    kat = {k: d["dimension"][k]["category"]["index"] for k in ids}
    satir = []
    for flat, deger in d["value"].items():
        i, kalan = int(flat), []
        for s in reversed(boy):
            kalan.append(i % s)
            i //= s
        satir.append({k: kat[k][j] for k, j in zip(ids, reversed(kalan))} | {"deger": float(deger)})
    return pd.DataFrame(satir)


ev = jsonstat_df(json.load(open(HAM / "DF_EVLENME_IL_ILCE.json", encoding="utf-8")))
bo = jsonstat_df(json.load(open(HAM / "DF_BOSANMA_IL_ILCE.json", encoding="utf-8")))
ev = ev[ev.REF_AREA.str.isdigit()].pivot_table(index="REF_AREA", columns="TIME_PERIOD", values="deger")
bo = bo[bo.REF_AREA.str.isdigit()].pivot_table(index="REF_AREA", columns="TIME_PERIOD", values="deger")
ev.columns = [f"evlenme_{c}" for c in ev.columns]
bo.columns = [f"bosanma_{c}" for c in bo.columns]
out = ev.join(bo, how="outer").reset_index().rename(columns={"REF_AREA": "ilce_kod"})
out.to_csv(KOK / "03_VERI" / "islenmis" / "ilce_evlenme_bosanma.csv", index=False, encoding="utf-8")
print(out.shape, "| evlenme 2025 toplam:", out.evlenme_2025.sum(), "| boşanma 2025 toplam:", out.bosanma_2025.sum(),
      "| boşanması 0 olan ilçe (2025):", int((out.bosanma_2025.fillna(0) == 0).sum()), "| evlenmesi 0:", int((out.evlenme_2025.fillna(0) == 0).sum()))
