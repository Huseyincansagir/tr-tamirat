"""
Model mahalle v2.1 — bütün çıktıları sırayla üretir
===================================================
python hepsini_calistir.py

Sıra: metrikler.csv (v1, v2.0, v2.1 sütunları) → geleneksel doku ölçümü ve figür–zemin paftası → vaziyet planı (+DXF) →
erişim analizi → sokak kesitleri → konut tipolojileri →
asansör özeti → deprem hızlı uygulama → okul seçenekleri → v1 → v2.1 değişiklikler levhası.
Hepsi plan_modeli.py'deki tek geometriden beslenir; v1 değerleri v1_okuyucu.py ile v1 kodundan okunur
(v1 dosyalarına yazılmaz). Bir ölçü değişince bu betiği yeniden çalıştırmak yeterlidir.

Gerekenler: Python 3.11, matplotlib, shapely ≥ 2, networkx, numpy; DXF için ezdxf; geleneksel doku ölçümü için
03_VERI/kod/morfoloji_olcum.py'nin bağımlılıkları (geopandas, pyproj, rasterio, scipy, pandas). v2.0 sütunu
MM_SURUM=2.0 ile ayrı süreçte aynı koddan hesaplanır.
"""

import runpy
import sys
import time
from pathlib import Path

KOD = Path(__file__).resolve().parent
SIRA = ["metrikler.py", "morfoloji_v2.py", "vaziyet_plani.py", "erisim_analizi.py", "sokak_kesitleri.py", "konut_tipolojileri.py",
        "tipoloji_asansor_ozeti.py", "deprem_hizli_uygulama.py", "okul_secenekleri.py", "v1_v2_karsilastirma.py"]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(KOD))
    for ad in SIRA:
        t = time.time()
        print(f"--- {ad}")
        runpy.run_path(str(KOD / ad), run_name="__main__")
        print(f"    {time.time() - t:.1f} sn")
