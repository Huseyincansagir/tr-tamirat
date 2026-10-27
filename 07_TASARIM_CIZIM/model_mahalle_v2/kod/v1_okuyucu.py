"""
Model mahalle v2 — v1 değerlerini okur (v1 dosyalarına yazmaz)
==============================================================
* v1_csv(): 07_TASARIM_CIZIM/model_mahalle/metrikler.csv satırları
* v1_geometri(): v1 plan modelini ayrı bir Python sürecinde çalıştırır (modül adları çakışmasın diye)
  ve karşılaştırma levhası ile "v1 (v2 yöntemiyle)" göstergeleri için gereken geometriyi geçici bir
  dosya üzerinden alır. v1 kodu yalnızca içe aktarılır; hiçbir v1 dosyası yazılmaz.
"""

import csv
import pickle
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

from ortak import V1_KOD

V1_CSV = V1_KOD.parent / "metrikler.csv"


@lru_cache(maxsize=1)
def v1_csv():
    d = {}
    with open(V1_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d[r["gosterge"]] = r
    return d


def v1_deger(gosterge):
    r = v1_csv().get(gosterge)
    if r is None or r["plan_degeri"] in ("", None):
        return None
    try:
        return float(r["plan_degeri"])
    except ValueError:
        return None


_BETIK = r'''
import sys, pickle
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import plan_modeli as pm
P = pm.model()
ilk = dict((id(p), m) for p, m in pm.konut_mesafeleri("ilkokul"))
asm = dict((id(p), m) for p, m in pm.konut_mesafeleri("asm"))
konak = dict((id(p), m) for p, m in pm.konut_mesafeleri("konak"))
parseller = []
for p in P["parseller"]:
    d = {k: v for k, v in p.items() if k in ("poly", "tip", "bolge", "konut", "kat", "binalar", "kapi", "ada",
                                              "ticari", "kat_alani", "dukkan", "yan_konut", "avlu", "genisleme")}
    sk = p["binalar"][0]
    if p["tip"] == "T3":
        w = sk.bounds[2] - sk.bounds[0]
        kb = max(2, round(w * pm.T3_SOKAK_KANADI / pm.KONUT_BRUT_T3))
        d["kat_basi"] = kb
        d["zemin_konut"] = max(0, min(0 if p.get("dukkan") else kb - 1, p["konut"] - p.get("yan_konut", 4)))
    d["ilkokul_m"] = ilk[id(p)]
    d["asm_m"] = asm[id(p)]
    d["konak_m"] = konak[id(p)]
    parseller.append(d)
out = dict(
    parseller=parseller,
    dusen=[dict(poly=p["poly"], tip=p["tip"]) for p in P["dusen"]],
    donatilar=[dict(tur=d["tur"], ad=d["ad"], poly=d["poly"], binalar=d["binalar"]) for d in P["donatilar"]],
    cep=P["cep"], ortaklar=P["ortaklar"], gecitler=[g for g, _ in P["gecitler"]],
    zemin=[dict(tur=z["tur"], xy=z["xy"]) for z in P["zemin"]],
    diyag=pm.DIYAG_BANT, s2=pm.S2, cadde=pm.CADDE, meydan=pm.MEYDAN, toplayici=pm.TOPLAYICI,
    kapali=pm.KAPALI_SOKAK.difference(pm.DONATI_POLY), carsi_yaya=pm.CARSI_YAYA,
    birimler=[(no, g) for no, g in pm.komsuluk_birimleri()],
)
with open(sys.argv[2], "wb") as f:
    pickle.dump(out, f)
'''


@lru_cache(maxsize=1)
def v1_geometri():
    with tempfile.TemporaryDirectory() as t:
        yol = Path(t) / "v1.pkl"
        subprocess.run([sys.executable, "-c", _BETIK, str(V1_KOD), str(yol)], check=True, cwd=t)
        with open(yol, "rb") as f:
            return pickle.load(f)
