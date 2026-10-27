"""
Model mahalle v2'nin FUE v0.2 konumu (E ve Ç), pilot kentsel mahalle dağılımına göre
==================================================================================
Girdi : 07_TASARIM_CIZIM/model_mahalle_v2/metrikler.csv (çizimden hesaplanan değerler)
        05_ANALIZ/sonuclar/fue_mahalle.csv, fue_gosterge_tanim.csv (fue_mahalle.py)
Çıktı : 05_ANALIZ/sonuclar/fue_model_mahalle.csv

Model mahallenin her göstergesi, 300 pilot kentsel mahallenin dağılımında yüzdelik puana çevrilir (fue_mahalle.py ile
aynı kural). Göstergelerin bir kısmı çizimden doğrudan gelir [H]; GHSL'ye ya da OSM tanımına eşdeğer olmayanlar için
açık varsayım kullanılır [V] ve "kaynak" sütununda yazılır.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
SON = KOK / "05_ANALIZ" / "sonuclar"
MET = pd.read_csv(KOK / "07_TASARIM_CIZIM" / "model_mahalle_v2" / "metrikler.csv").drop_duplicates("gosterge")
# yaşanan yükseklik: konut ağırlıklı kat × 3,1 m (07_TASARIM_CIZIM/model_mahalle_v2.md §3.5) [H]
YUKSEKLIK = {"v2_0": 9.9, "v2_1": 9.6}
M = pd.read_csv(SON / "fue_mahalle.csv")
K = M[M.kentsel]
G = pd.read_csv(SON / "fue_gosterge_tanim.csv")
G = G[G.surum == "v0.1"] if "surum" in G else G  # uydu göstergeleri (v0.2) yer seçimine bağlı; tasarımdan hesaplanamaz
ERISIM = ["kavsak_yog", "temel15", "oyun400", "okul500", "esnaf1000", "karma150", "cami500", "bulusma400", "ulasim", "rayli800"]
tum = []
for surum in ["v2_0", "v2_1"]:
    mm = MET.set_index("gosterge")[surum]
    nufus = mm["Nüfus"]

    DEGER = {  # gösterge: (değer, kaynak)
        "kavsak_yog": (mm["Kavşak yoğunluğu (araç ağı)"], "[H] araç ağı kavşakları/km²; yaya yolları hariç (Faz 2 tanımı)"),
        "temel15": (100.0, "[H] ilkokul ≤500 m %100, ASM ≤500 m %96, dükkân ≤300 m %100 → hepsi ≤1.200 m"),
        "yesil300": (100.0, "[H] ≥0,5 ha yeşil ≤200 m ağ %95,8 → ≤300 m kuş uçuşu ≈ %100"),
        "yukseklik": (YUKSEKLIK[surum], "[H] konut ağırlıklı kat × 3,1 m (GHSL eşdeğeri)"),
        "yuksek_pay": (0.0, "[H] 5+ katlı bina yalnız %2,5 konut; hiçbir 100 m hücrede ortalama ≥15 m beklenmez"),
        "anayol100": (5.0, "[V] dış kenardaki 24 m toplayıcı yola bakan sıralar; birincil yol yok"),
        "zemin_pay": (mm["≤ 3 katlı binalardaki konut payı"], "[H] ≤3 katlı binalardaki konut payı"),
        "oyun400": (100.0, "[H] kapı önü oyun alanı ya da cep parkı ≤150 m %100"),
        "okul500": (mm["İlkokul ≤ 500 m"], "[H] ilkokul ≤500 m ağ"),
        "esnaf1000": (mm["Zemin kat konut dışı birim (dükkân, atölye, ofis; ≈ 70 m²)"] / nufus * 1000,
                      "[H] zemin kat konut dışı birim / 1.000 kişi"),
        "karma150": (60.0, "[V] dükkân ≤300 m ağ %100; 150 m kuş uçuşu için yaklaşık %60"),
        "cami500": (mm["İbadet yeri (mescit ≤150 / küçük cami ≤250 / semt camii ≤400 m)"], "[H] ibadet kademesi"),
        "bulusma400": (85.0, "[V] meydan-çarşı ≤400 m %74, konak ≤500 m %95, 8 komşuluk yeşili"),
        "site_pay": (0.0, "[H] kapalı site yok (Fıtrat Kodu)"),
        "muhtar_nufus": (np.log(nufus), "[H] tek mahalle (muhtarlık)"),
        "ulasim": (mm["Otobüs durağı ≤ 300 m"], "[H] otobüs durağı ≤300 m ağ"),
        "yayilma": (60.0 / (nufus / 1000), "[H] 60 ha tümüyle yapılı alan sayılır"),
        "rayli800": (0.0, "[V] raylı sistem varsayılmadı"),
    }
    satir = []
    for _, g in G.iterrows():
        v, kay = DEGER[g.kod]
        r = np.sort(K[g.kod].dropna().values)
        p = (np.searchsorted(r, v, "left") + np.searchsorted(r, v, "right")) / 2 / len(r) * 100
        satir.append({"kod": g.kod, "boyut": g.boyut, "ad": g.ad, "deger": v, "puan": p if g.yon > 0 else 100 - p,
                      "eksen": "E" if g.kod in ERISIM else "Ç", "pilot_medyan": np.median(r), "kaynak": kay})
    T = pd.DataFrame(satir)
    ozet = {"FUE": T.groupby("boyut").puan.mean().mean(), "E": T[T.eksen == "E"].puan.mean(), "Ç": T[T.eksen == "Ç"].puan.mean()}
    for k, v in ozet.items():
        T.loc[len(T)] = {"kod": k, "ad": f"{k} (özet)", "puan": v}
    T["surum"] = surum
    tum.append(T)
    print(surum, {k: round(v, 1) for k, v in ozet.items()})
T = pd.concat(tum, ignore_index=True)
T.to_csv(SON / "fue_model_mahalle.csv", index=False, encoding="utf-8")
print(T[T.surum == "v2_1"][["kod", "boyut", "deger", "pilot_medyan", "puan", "eksen"]].round(1).to_string(index=False))
iyi = K[(K.FUE_E >= 60) & (K.FUE_C >= 55)]
print(f"\nModel mahalle v2.1: FUE {ozet['FUE']:.1f} · E {ozet['E']:.1f} · Ç {ozet['Ç']:.1f}"
      f" | pilotlarda E≥60 ve Ç≥55 sağlayan mahalle: {len(iyi)}, en yüksek Ç {iyi.FUE_C.max():.1f}")
