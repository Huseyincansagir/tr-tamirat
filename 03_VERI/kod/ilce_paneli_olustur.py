"""
İlçe paneli: TÜİK ilçe kodları ↔ geoBoundaries ADM2 sınırları ↔ GHSL göstergeleri
==================================================================================
Girdi : 03_VERI/islenmis/ilce_dogum_nufus.csv (tuik_sdmx_ilce.py)
        03_VERI/islenmis/ilce_ghsl.csv        (ghsl_ilce.py)
        03_VERI/islenmis/ilce_yas_cinsiyet.csv (varsa; MEDAS ilçe × yaş × cinsiyet)
Çıktı : 03_VERI/islenmis/ilce_paneli.csv / .gpkg, eşleşme raporu
Eşleştirme: (il, ilçe) adları Türkçe küçük harfe ve sadeleştirilmiş biçime çevrilir; il merkez ilçeleri
("MERKEZ", "<İl> Merkez", il adıyla aynı) özel olarak ele alınır; kalanlar il içinde bulanık eşleştirilir.
"""
import difflib
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
IS = KOK / "03_VERI" / "islenmis"


def sade(s):
    s = str(s).replace("İ", "i").replace("I", "ı").lower()
    for a, b in [("ı", "i"), ("ğ", "g"), ("ü", "u"), ("ş", "s"), ("ö", "o"), ("ç", "c"), ("â", "a"), ("î", "i"), ("û", "u")]:
        s = s.replace(a, b)
    return "".join(ch for ch in s if ch.isalnum())


t = pd.read_csv(IS / "ilce_dogum_nufus.csv", dtype={"ilce_kod": str})
g = pd.read_csv(IS / "ilce_ghsl.csv")
# geoBoundaries'te İngilizce kalan adlar
g["shapeName"] = g.shapeName.replace({"Prince Islands": "Adalar", "Imbros": "Gökçeada"})
g["il_s"], g["ad_s"] = g.il_gb.map(sade), g.shapeName.map(sade)
t["il_s"], t["ad_s"] = t.il.map(sade), t.ilce_ad_tuik.map(sade)


def kok(ad, il_s):
    """'BALIKESİR EDREMİT' -> 'edremit'; 'X MERKEZ', 'X (Merkez İlçe)', 'X District', 'X' -> 'merkez'; 'Gediz Merkez' -> 'gediz'"""
    for ek in ("merkezilce", "district", "merkez"):
        if ad.endswith(ek) and ad != ek:
            kalan = ad[: -len(ek)]
            ad = "merkez" if kalan == il_s else kalan
            break
    if ad.startswith(il_s) and ad != il_s:
        ad = ad[len(il_s):]
    return ad


t["ad_s"] = [kok(a, i) for a, i in zip(t.ad_s, t.il_s)]
g["ad_s"] = [kok(a, i) for a, i in zip(g.ad_s, g.il_s)]
# il adıyla aynı olan sınır, o ilde aynı adlı bir TÜİK ilçesi yoksa merkez ilçedir
g["ad_s"] = np.where((g.ad_s == g.il_s) & ~g.il_s.isin(t.loc[t.ad_s == t.il_s, "il_s"]), "merkez", g.ad_s)

m = t.merge(g, on=["il_s", "ad_s"], how="left", suffixes=("", "_gb"))
eksik = m[m.gid.isna()]
kullanilan = set(m.gid.dropna())
duzeltme = []
for i, r in eksik.iterrows():
    aday = g[(g.il_s == r.il_s) & ~g.gid.isin(kullanilan)]
    if aday.empty:
        continue
    en = difflib.get_close_matches(r.ad_s, aday.ad_s.tolist(), n=1, cutoff=0.6)
    if en:
        gid = aday.loc[aday.ad_s == en[0], "gid"].iloc[0]
        kullanilan.add(gid)
        duzeltme.append((r.il, r.ilce_ad_tuik, aday.loc[aday.gid == gid, "shapeName"].iloc[0]))
        for c in g.columns:
            if c not in ("il_s", "ad_s"):
                m.loc[i, c if c not in t.columns else c + "_gb"] = aday.loc[aday.gid == gid, c].iloc[0]
print("bulanık eşleşen:", len(duzeltme))
for d in duzeltme:
    print("   ", d)
kalan = m[m.gid.isna()]
print("eşleşmeyen TÜİK ilçesi:", len(kalan), kalan[["il", "ilce_ad_tuik"]].values.tolist())
print("kullanılmayan sınır:", sorted(set(g.gid) - set(m.gid.dropna()))[:20])
m = m.drop(columns=["il_s", "ad_s"])

for ek in ("ilce_yas_cinsiyet.csv", "ilce_kadin_egitim.csv"):  # MEDAS 2025: yaş-cinsiyet; 15+ kadın eğitim düzeyi
    if (IS / ek).exists():
        m = m.merge(pd.read_csv(IS / ek, dtype={"ilce_kod": str}), on="ilce_kod", how="left")

sinir = gpd.read_file(KOK / "03_VERI" / "ham" / "sinirlar" / "geoBoundaries-TUR-ADM2_simplified.geojson")
sinir["gid"] = np.arange(1, len(sinir) + 1)
gp = sinir[["gid", "geometry"]].merge(m.dropna(subset=["gid"]).astype({"gid": int}), on="gid")
m.to_csv(IS / "ilce_paneli.csv", index=False, encoding="utf-8")
gp.to_file(IS / "ilce_paneli.gpkg", layer="ilce_paneli", driver="GPKG")
print("panel:", m.shape, "| geometrili:", len(gp))
