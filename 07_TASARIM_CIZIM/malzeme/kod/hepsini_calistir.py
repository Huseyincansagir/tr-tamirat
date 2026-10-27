"""
Faz 4 · Rapor 3 zincirini tek komutla yeniden üretir:
    malzeme_modeli.py → karar_matrisleri.py → grafikler.py
Çalıştırma (depo kökünden, Python 3.11):
    PYTHONIOENCODING=utf-8 python 07_TASARIM_CIZIM/malzeme/kod/hepsini_calistir.py
"""
import runpy
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
KOD = Path(__file__).resolve().parent
for betik in ("malzeme_modeli.py", "karar_matrisleri.py", "grafikler.py"):
    print(f"\n===== {betik} =====")
    runpy.run_path(str(KOD / betik), run_name="__main__")
print("\nTamam: sonuç CSV'leri, karar matrisleri ve 7 grafik (PNG + SVG) 07_TASARIM_CIZIM/malzeme/ içinde.")
