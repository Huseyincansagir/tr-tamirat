"""
Model mahalle v1 — bütün çıktıları sırayla üretir
=================================================
python hepsini_calistir.py

Sıra: metrikler.csv → vaziyet planı (+DXF) → erişim analizi → sokak kesitleri →
konut tipolojileri → deprem hızlı uygulama. Hepsi plan_modeli.py'deki tek
geometriden beslenir; bir ölçü değişince bu betiği yeniden çalıştırmak yeterlidir.
"""

import runpy
import sys
import time
from pathlib import Path

KOD = Path(__file__).resolve().parent
SIRA = ["metrikler.py", "vaziyet_plani.py", "erisim_analizi.py", "sokak_kesitleri.py", "konut_tipolojileri.py",
        "deprem_hizli_uygulama.py"]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(KOD))
    for ad in SIRA:
        t = time.time()
        print(f"--- {ad}")
        runpy.run_path(str(KOD / ad), run_name="__main__")
        print(f"    {time.time() - t:.1f} sn")
