"""
İsraf, fire ve kaçak analizi — TÜİK SDMX verilerini indir
=========================================================
TÜİK Dağıtım Yönetim Sistemi (databrowser2.tuik.gov.tr) komut satırından çalışır, anahtar gerekmez.
Her akış bir kez indirilir; dosya varsa yeniden indirilmez (silerek yenileyin).

Çıktı: 03_VERI/ham/israf/sdmx/<AKIŞ>.json  (JSON-stat 2.0)

Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/israf_veri_indir.py
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
CIKTI = KOK / "03_VERI" / "ham" / "israf" / "sdmx"
CIKTI.mkdir(parents=True, exist_ok=True)
B = "https://databrowser2.tuik.gov.tr/api/core/nodes/1/datasets/"
H = {"Accept": "application/json", "User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
C = lambda i, v: {"id": i, "filterValues": v, "type": "CodeValues", "period": 0}

# akış -> (sürüm, filtre gövdesi; [] = hepsi)
AKIS = {
    # su: belediyelerce çekilen ve dağıtılan su, il bazında (2020, 2022, 2024)
    "DF_SU_ATIKSU_BELEDIYE_CEKILEN_DAGITILAN_V1": ("1.0", []),
    "DF_SU_ATIKSU_BELEDIYE_GOSTERGE_V1": ("1.0", []),
    # atık: belediye atığı (Türkiye ve il), bertaraf ve geri kazanım tesisleri, imalat sanayi
    "DF_ATIK_BELEDIYE_HIZMET_YONETIM_GOSTERGE_V1": ("1.0", []),
    "DF_ATIK_BELEDIYE_ATIKYONETIMI_V1": ("1.0", []),
    "DF_ATIK_BERTARAF_GERI_KAZANIM_TESIS_V1": ("1.0", []),
    "DF_ATIK_IMALAT_SANAYI_GOSTERGELER_V1": ("1.0", []),
    # sera gazı envanteri (kaçak metan: 1.B.2; düzenli depolama: 5.A)
    "DF_SERA_GAZI_EMISYONLARI": ("1.0", []),
    # tarım ürünleri üretici fiyatları (TL/kg, aylık, 2024-01 →)
    "DF_TARIM_URUNLERI_UFE_MADDE_FIYAT_V2": ("1.0", []),
    # trafiğe kayıtlı otomobil, il, aralık ayı
    "DF_MOTORLU_KARA_TASIT_ILLER_V3": ("1.0", [C("ARAC_TUR", ["1"]), C("AY", ["M12"]), C("UNIT_MEASURE", ["PN"])]),
    # taşıt-km
    "DF_TASIT_KILOMETRE_TASIT_CINS_V2": ("1.0", []),
    # GSYH (cari fiyatlarla), Türkiye toplamı
    "UH_BH_GSYH_CARI": ("1.0", [C("REF_AREA", ["TR"]), C("FAALIYET_KOD", ["B1GQ", "A"]), C("KIRILIM_SEVIYE", ["A10"])]),
    # madde akış hesapları
    "DF_MADDE_AKIS_HESAPLARI": ("1.0", []),
    # TÜFE seçilmiş madde ortalama fiyatları (akaryakıt, elektrik, doğal gaz; yalnız son aylar)
    "DF_TUFE_SDMX_TT07": ("1.0", []),
    # TÜFE genel endeksi (2025=100), aylık — tarım fiyatlarını genel enflasyonla karşılaştırmak için
    "DF_TUFE_SDMX_TT01": ("1.0", [C("COICOP_2018", ["0"]), C("DEGISIM", ["1"]), C("FREQ", ["M"])]),
}


def istek(url, govde):
    for deneme in range(5):
        try:
            r = urllib.request.Request(url, data=json.dumps(govde).encode(), headers=H, method="POST")
            return json.load(urllib.request.urlopen(r, timeout=600))
        except Exception as e:  # ağ hatasında bekleyip yeniden dene
            print("  yeniden deneniyor:", e)
            time.sleep(8 * (deneme + 1))
    raise RuntimeError(url)


for akis, (surum, govde) in AKIS.items():
    yol = CIKTI / f"{akis}.json"
    if yol.exists():
        print("var:", yol.name)
        continue
    d = istek(f"{B}TR,{akis},{surum}/data", govde)
    json.dump(d, open(yol, "w", encoding="utf-8"), ensure_ascii=False)
    print("indirildi:", yol.name, f"{yol.stat().st_size / 1e3:,.0f} KB", d.get("size"))
    time.sleep(2)
