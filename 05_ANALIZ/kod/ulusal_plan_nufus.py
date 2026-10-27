"""
Faz 4 · Ulusal mekânsal çerçeve — ızgara nüfusunun TÜİK ilçe toplamlarına ölçeklenmesi
===================================================================================
Neden: GHSL R2023A POP 2020 bazı ilçelerde nüfusu yanlış yere koyuyor. Örnek: Adana'da Yumurtalık'a ≈ 357 bin kişi
(TÜİK 2024: 18 bin), Sarıçam'a ≈ 22 bin kişi (TÜİK 2024: 251 bin) düşüyor; Kırıkkale Keskin'de 171 bine karşı 16 bin.
973 ilçede nüfus ağırlıklı mutlak sapma ≈ %24 [H]. Erişim ve kademe hesapları kişi saydığı için bu düzeltilir.

Yöntem (dasimetrik ölçekleme):
  1. Her ilçenin TÜİK ADNKS 2025 nüfusu (ilce_paneli_genis.csv, nufus_2025) o ilçenin ızgara hücrelerine dağıtılır.
  2. GHSL ilçe toplamı TÜİK'in 0,5–2 katı arasındaysa ağırlık GHSL hücre nüfusudur (dağılım korunur, toplam düzelir).
  3. Bu aralığın dışındaysa GHSL'nin ilçe içi dağılımına güvenilmez; ağırlık WorldCover 2021 yapılı alan payıdır
     (yapılı alan yoksa GHSL, o da yoksa düzgün dağılım).
Girdi : 03_VERI/islenmis/ulusal_altyapi/izgara_nufus_ghsl.tif, izgara_ilce.tif, izgara_ilce_anahtar.csv, izgara_ortu.tif
        03_VERI/islenmis/ilce_paneli_genis.csv (TÜİK ADNKS 2024 ve 2025)
Çıktı : 03_VERI/islenmis/ulusal_altyapi/izgara_nufus.tif  (kişi/hücre, 250 m; toplam = TÜİK 2025)
        05_ANALIZ/sonuclar/ulusal_plan_nufus_olcekleme.csv (ilçe: GHSL, TÜİK, oran, yöntem)
Sıra  : ulusal_plan_izgara.py → ulusal_plan_nufus.py → ulusal_plan_katmanlar.py → …
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
CIK = KOK / "03_VERI" / "islenmis" / "ulusal_altyapi"
SON = KOK / "05_ANALIZ" / "sonuclar"

with rasterio.open(CIK / "izgara_nufus_ghsl.tif") as d:
    g = d.read(1).astype("float64")
    prof = d.profile
with rasterio.open(CIK / "izgara_ilce.tif") as d:
    ilc = d.read(1)
with rasterio.open(CIK / "izgara_ortu.tif") as d:
    yap = d.read(3).astype("float64")
yap[yap == 255] = 0
anahtar = pd.read_csv(CIK / "izgara_ilce_anahtar.csv", dtype={"ilce_kod": str})
panel = pd.read_csv(KOK / "03_VERI" / "islenmis" / "ilce_paneli_genis.csv", dtype={"ilce_kod": str},
                    usecols=["ilce_kod", "nufus_2024", "nufus_2025"])
a = anahtar.merge(panel, on="ilce_kod", how="left")
assert a.nufus_2025.notna().all(), "TÜİK nüfusu eşleşmeyen ilçe var"
n = int(ilc.max()) + 1
G = np.bincount(ilc.ravel(), g.ravel(), n)
Y = np.bincount(ilc.ravel(), yap.ravel(), n)
a["ghsl_2020"] = G[a.sira]
a["oran_tuik_ghsl"] = a.nufus_2025 / a.ghsl_2020.replace(0, np.nan)
a["yontem"] = np.where(a.oran_tuik_ghsl.between(0.5, 2.0), "GHSL ölçekleme",
                       np.where(Y[a.sira] > 0, "yapılı alan ağırlığı", np.where(G[a.sira] > 0, "GHSL ölçekleme", "düzgün")))
yon = np.zeros(n, dtype="int8")  # 0 GHSL, 1 yapılı, 2 düzgün
yon[a.sira] = a.yontem.map({"GHSL ölçekleme": 0, "yapılı alan ağırlığı": 1, "düzgün": 2}).values
T = np.zeros(n)
T[a.sira] = a.nufus_2025.values
cy = yon[ilc]
w = np.where(cy == 0, g, np.where(cy == 1, yap, 1.0))
w[ilc == 0] = 0
W = np.bincount(ilc.ravel(), w.ravel(), n)
carpan = np.divide(T, W, out=np.zeros(n), where=W > 0)
out = (w * carpan[ilc]).astype("float32")
out[ilc == 0] = 0
prof.update(dtype="float32", nodata=None)
with rasterio.open(CIK / "izgara_nufus.tif", "w", **prof) as o:
    o.write(out, 1)
    o.update_tags(kaynak="TÜİK ADNKS 2025 ilçe toplamları; ilçe içi dağılım GHSL R2023A POP 2020 ya da WorldCover 2021 yapılı alan")
a["izgara_2025"] = np.bincount(ilc.ravel(), out.ravel().astype("float64"), n)[a.sira]
a[["sira", "ilce_kod", "ilce_ad_tuik", "il", "ghsl_2020", "nufus_2024", "nufus_2025", "oran_tuik_ghsl", "yontem",
   "izgara_2025"]].round(3).to_csv(SON / "ulusal_plan_nufus_olcekleme.csv", index=False, encoding="utf-8")
sapma = (a.ghsl_2020 - a.nufus_2025).abs().sum() / a.nufus_2025.sum() * 100
print(f"GHSL 2020 ızgara toplamı {a.ghsl_2020.sum() / 1e6:.2f} milyon · TÜİK 2025 {a.nufus_2025.sum() / 1e6:.2f} milyon · "
      f"ızgara (düzeltilmiş) {out.sum() / 1e6:.2f} milyon")
print(f"ilçe düzeyinde nüfus ağırlıklı mutlak sapma (GHSL 2020 – TÜİK 2025): %{sapma:.1f}")
print(a.yontem.value_counts().to_dict())
print("yapılı alan ağırlığına geçen ilçeler:",
      a[a.yontem != "GHSL ölçekleme"].sort_values("nufus_2025", ascending=False)[["ilce_ad_tuik", "il", "ghsl_2020",
                                                                                 "nufus_2025"]].round(0).to_string(index=False))
