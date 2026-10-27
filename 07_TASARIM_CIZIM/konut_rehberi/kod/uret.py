"""
Konut rehberi — bütün çıktıları tek komutla üretir (Faz 4 · Rapor 2)
====================================================================
Çalıştırma (bu klasörden):  PYTHONIOENCODING=utf-8 python uret.py
Python 3.11 · matplotlib, shapely, ezdxf (DXF için; yoksa DXF atlanır).

Sıra: tip (a) … (e) paftaları → referans 3+1 daire → karşılaştırma → Türkiye durumu → tablolar.
Çıktılar 07_TASARIM_CIZIM/konut_rehberi/ altına yazılır. Model mahalle dosyaları yalnız okunur.
"""

from __future__ import annotations

import sys

import karsilastirma
import referans_daire
import tip_a_avlulu_ev
import tip_b_sofali_ev
import tip_c_buyuyen_sira_ev
import tip_d_cok_kusakli_avlu_evi
import tip_e_galerili_blok
import turkiye_durumu
from cizim import CIKTI
from degerlendirme import CSV_ALANLAR, csv_yaz, olcut_satirlari

MODULLER = [tip_a_avlulu_ev, tip_b_sofali_ev, tip_c_buyuyen_sira_ev, tip_d_cok_kusakli_avlu_evi, tip_e_galerili_blok,
            referans_daire]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ozler, odalar, olcutler = [], [], []
    for mod in MODULLER:
        print(f"→ {mod.__name__}")
        oz, sat = mod.ciz()
        ozler.append(oz)
        odalar += sat
        for (ilke, olcut, deger, durum) in olcut_satirlari(oz):
            olcutler.append(dict(tip=oz["tip"], ilke=ilke, olcut=olcut, deger=deger, durum=durum))
    csv_yaz(CIKTI / "konut_alan_programi.csv", odalar, CSV_ALANLAR)
    csv_yaz(CIKTI / "konut_olcutleri.csv", olcutler, ["tip", "ilke", "olcut", "deger", "durum"])
    print("→ karşılaştırma")
    satirlar = karsilastirma.calistir(ozler)
    print("→ Türkiye durumu")
    turkiye_durumu.calistir()
    # özet ve boyut denetimi
    print()
    print(f"{'tip':<4}{'net':>7}{'net/kişi':>10}{'dış/kişi':>10}{'güneş 21 Şub':>14}{'kaba mn TL':>12}{'ilke':>7}")
    for s in satirlar:
        print(f"{s['tip']:<4}{s['net_m2']:>7}{s['net_kisi']:>10}{s['dis_mekan_kisi']:>10}{s['gunes_21sub_sa']:>14}"
              f"{s['kaba_tl'] / 1e6:>12.2f}{s['ilke_puan']:>7}")
    buyuk = [(p.name, p.stat().st_size) for p in CIKTI.iterdir() if p.is_file() and p.stat().st_size > 20 * 2 ** 20]
    print("20 MB üstü dosya:", buyuk or "yok")
    sorunlu = [oz["tip"] for oz in ozler if oz.get("sorun")]
    print("etiket sorunu olan pafta:", sorunlu or "yok")


if __name__ == "__main__":
    main()
