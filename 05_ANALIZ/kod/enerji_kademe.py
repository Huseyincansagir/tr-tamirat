"""
Kademe enerji tablosu (Faz 4 · Rapor 5): mahalle → semt → şehir → bölge → ülke
==============================================================================
Ölçeklenebilir şehir modeline (07_TASARIM_CIZIM/olceklenebilir_sehir) girdi verir.
Her kademe aynı saatlik modelle (2019–2023, 5 hava yılı) ve kendi sınırı içinde hesaplanır:

  mahalle : 1 model mahalle v2.1 (≈6.925 kişi). Yerel kaynak: çatı GES. Depolama: mahalle bataryası.
  semt    : 5 mahalle + semt merkezi (≈35 bin). Yerel kaynak: çatı GES (semt merkezi çatısı dahil). Depolama: semt bataryası.
  şehir   : 6 semt = 30 mahalle + şehir hizmetleri (≈210 bin). Yerel kaynak: çatı + şehir çevresinde güneş ve rüzgâr.
            Üretim karması enerji_senaryo.py'nin taramasından gelir (K2: en ucuz nükleersiz karma).
  bölge   : 6 şehir eşdeğeri + ağır sanayi, liman, havalimanı (≈1,25 milyon). Yerel kaynak: çatı + bölgesel güneş ve rüzgâr;
            ayrıca 1–2 adet 300 MWe SMR seçeneği. Karma burada taranır.
  ülke    : 2050 senaryoları S2 ve S3 (enerji_senaryo.py).

Depolama seçimi:
  mahalle ve semt: son eklenen 1 MWh'nin yılda ≥ 250 MWh ek deşarj getirdiği en büyük batarya [V]
  şehir ve bölge : üretim karması maliyet taramasından (en ucuz nükleersiz); batarya aynı marjinal kuralla [V]

"Yerinde karşılama" = 1 − (kademe sınırı dışından, yani üst kademeden alınan elektrik / talep), saatlik.

Girdi : enerji_mahalle.py ve enerji_senaryo.py modülleri; enerji_kent_senaryolar.csv, enerji_kent_tarama.csv,
        enerji_ulke_2050.csv, enerji_turkiye_nihai_sektor.csv (önce enerji_senaryo.py ve enerji_veri.py çalışmalı)
Çıktı : 05_ANALIZ/sonuclar/enerji_kademe.csv · enerji_kademe_bolge_tarama.csv
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/enerji_kademe.py   (≈ 2–4 dk)
"""
from __future__ import annotations

import itertools
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enerji_ortak import SON, YILLAR, pilot_pv, v  # noqa: E402
import enerji_mahalle as em  # noqa: E402
import enerji_senaryo as es  # noqa: E402

NY = len(YILLAR)
ILCELER = {"Kocasinan": "soğuk iç bölge (referans)", "Fatih": "ılıman kıyı", "Antakya": "sıcak güney"}
BAT = em.BATARYA_MWH                           # batarya boyları, mahalle başına MWh; üst kademede mahalle eşdeğeriyle çarpılır
NUFUS_2050 = 93_774_618                        # TÜİK Nüfus Projeksiyonları 2023–2100, ana senaryo [İ]
SMR_BIRIM = 300                                # MWe, BWRX-300


def secilen_batarya(tar: pd.DataFrame, esik: float = em.MARJINAL_ESIK) -> pd.Series:
    t = tar.sort_values("batarya_mwh").copy()
    t["desarj_mwh"] = t["uretim_depolama_twh"] * 1e6
    t["marjinal"] = t["desarj_mwh"].diff() / t["batarya_mwh"].diff()
    uygun = t[t.marjinal >= esik]
    return (uygun.iloc[-1] if len(uygun) else t.iloc[0]), t


def satir(kademe, sira, ilce, kisi, mahalle_esd, isi_gwh, sec, bos, kaynaklar, kural, sanayi_isi=np.nan):
    T = sec["talep_twh"] * 1000
    # uretim_gunes_twh çatıyı da içerir (sevk'te güneş = çatı + arazi)
    uretim = (sec["uretim_gunes_twh"] + sec["uretim_ruzgar_twh"] + sec["uretim_nukleer_twh"]) * 1000
    ort = T * 1000 / 8766
    return dict(
        kademe=kademe, sira=sira, iklim_ilce=ilce, iklim=ILCELER[ilce], nufus=round(kisi), mahalle_esdegeri=mahalle_esd,
        elektrik_talep_gwh=T, elektrik_kisi_basi_kwh=T * 1e6 / kisi,
        isi_talep_gwh=isi_gwh, isi_kisi_basi_kwh=isi_gwh * 1e6 / kisi if pd.notna(isi_gwh) else np.nan,
        sanayi_proses_isi_kisi_basi_kwh=sanayi_isi,
        puant_mw=sec["puant_mw"], puant_w_kisi=sec["puant_mw"] * 1e6 / kisi,
        cati_ges_mwp=sec["gunes_cati_mwp"], cati_ges_kwp_kisi=sec["gunes_cati_mwp"] * 1000 / kisi,
        arazi_gunes_mw=sec["gunes_arazi_mw"], ruzgar_mw=sec["ruzgar_mw"], smr_mw=sec["nukleer_mw"],
        yerinde_uretim_gwh=uretim, cati_uretim_gwh=sec["uretim_cati_twh"] * 1000, uretim_talep_orani=uretim / T,
        yerinde_karsilama_depolamasiz=bos["yerel_karsilama"],
        depolama_mwh=sec["batarya_mwh"], depolama_kwh_kisi=sec["batarya_mwh"] * 1000 / kisi,
        depolama_saat_ort_yuk=sec["batarya_mwh"] / ort if ort else np.nan,
        yerinde_karsilama=sec["yerel_karsilama"], yerinde_karsilama_kis=sec.get("yerel_karsilama_kis", np.nan),
        sebeke_alis_gwh=sec["sebeke_alis_twh"] * 1000, sebeke_veris_gwh=sec["sebeke_veris_twh"] * 1000,
        puant_alis_mw=sec["puant_alis_mw"], puant_veris_mw=sec.get("puant_veris_mw", np.nan),
        maliyet_usd_mwh=sec["maliyet_usd_mwh"], secim_kurali=kural, kaynaklar=kaynaklar)


def mahalle_semt(ilce: str, ruz: np.ndarray) -> tuple[list, dict]:
    e = em.envanter()
    pv = pilot_pv(ilce)
    m = em.mahalle(ilce, e, pv=pv)
    sifir = np.zeros_like(m["talep"])
    isi_m = (m["isi"]["isitma"].sum() + m["isi"]["sicak_su"].sum()) / NY / 1e6           # GWh
    out = []
    # --- mahalle ---
    t = m["talep"] / 1000
    ort = t.mean()
    tar = es.yerel_karma(t, m["uretim"] / 1000, e.kwp.sum() / 1000, sifir, ruz,
                         [(0, 0, b, 0) for b in BAT], ilce, m["n_kisi"], olcek="mahalle")
    sec, tt = secilen_batarya(tar)
    out.append(satir("1 mahalle", 1, ilce, m["n_kisi"], 1, isi_m, sec, tt.iloc[0],
                     "çatı GES (konut, donatı, mobilite noktası)", "batarya: marjinal deşarj ≥ 250 MWh/MWh·yıl"))
    # --- semt: 5 mahalle + semt merkezi ---
    n = v("semt_mahalle")
    kisi = m["n_kisi"] * n
    t = (m["talep"] * n + kisi * v("semt_merkezi_el") * es.hizmet_profili()) / 1000
    semt_kwp = v("semt_merkezi_cati") * v("duz_pay") * v("kwp_m2")
    u = (m["uretim"] * n + semt_kwp * (pv["D10"] + pv["B10"]) / 2) / 1000
    ort = t.mean()
    tar2 = es.yerel_karma(t, u, (e.kwp.sum() * n + semt_kwp) / 1000, sifir, ruz,
                          [(0, 0, b * n, 0) for b in BAT], ilce, kisi, olcek="semt")
    sec, tt = secilen_batarya(tar2)
    out.append(satir("2 semt", 2, ilce, kisi, n, isi_m * n + kisi * v("semt_merkezi_isi") / 1e6, sec, tt.iloc[0],
                     "çatı GES (semt merkezi çatısı dahil)", "batarya: marjinal deşarj ≥ 250 MWh/MWh·yıl"))
    return out, dict(isi_mahalle_gwh=isi_m, mahalle_batarya=pd.concat([tar, tar2]))


def batarya_kurali(talep_mw, cati_mw, cati_mwp, arazi, ruz, ga, rz, nk, ilce, kisi, olcek, n_mahalle):
    tar = es.yerel_karma(talep_mw, cati_mw, cati_mwp, arazi, ruz, [(ga, rz, b * n_mahalle, nk) for b in BAT], ilce, kisi,
                         olcek=olcek)
    sec, tt = secilen_batarya(tar)
    return sec, tt.iloc[0], tar


def sehir(ilce: str, isi_m: float, ruz: np.ndarray) -> tuple[list, pd.DataFrame]:
    """Üretim karması: enerji_senaryo.py taramasındaki K1 (yalnız çatı) ve K2 (en ucuz nükleersiz).
    Depolama: aynı karma üzerinde mahalle ile aynı marjinal kural."""
    k = pd.read_csv(SON / "enerji_kent_senaryolar.csv")
    k = k[k.ilce == ilce]
    st = es.sehir_talebi(ilce)
    n = es.KENT_MAHALLE
    kisi = st["kisi"]
    isi = isi_m * n + kisi * (v("semt_merkezi_isi") + v("sehir_hizmet_isi")) / 1e6
    out, tara = [], []
    for ad, sira, kay in [("K2", 3, "çatı + şehir çevresinde güneş ve rüzgâr + batarya"), ("K1", 3.1, "çatı GES + batarya")]:
        r = k[k.senaryo.str.startswith(ad + " ")].iloc[0]
        sec, bos, tar = batarya_kurali(st["talep_mw"], st["cati_mw"], st["cati_mwp"], st["arazi"], ruz,
                                        r.gunes_arazi_mw, r.ruzgar_mw, 0, ilce, kisi, "şehir", n)
        tara.append(tar)
        kural = ("karma: maliyet taramasında en ucuz nükleersiz (K2); " if ad == "K2" else "karma: yalnız çatı (K1); ") +             "batarya: marjinal deşarj ≥ 250 MWh/MWh·yıl"
        o = satir("3 şehir" + ("" if ad == "K2" else " (yalnız çatı)"), sira, ilce, kisi, n, isi, sec, bos, kay, kural)
        o["maliyet_usd_mwh_bataryasiz"] = bos["maliyet_usd_mwh"]
        out.append(o)
    return out, pd.concat(tara)


def bolge(ilce: str, isi_m: float, ruz: np.ndarray, sanayi_isi: float) -> tuple[list, pd.DataFrame]:
    st = es.sehir_talebi(ilce)
    nb = v("bolge_sehir")
    kisi = st["kisi"] * nb
    t = st["talep_mw"] * nb + kisi * v("bolge_ek_el") * es.sanayi_profili() / 1000
    cati = st["cati_mw"] * nb
    ort = t.mean()
    izgara = [(ga * ort, rz * ort, bt * ort, nk) for ga, rz, bt, nk in
              itertools.product([0, 0.5, 1.0, 1.5, 2.0, 3.0], [0, 0.5, 1.0, 1.5, 2.0, 3.0], [0, 2, 4, 8],
                                [0, SMR_BIRIM, 2 * SMR_BIRIM])]
    tar = es.yerel_karma(t, cati, st["cati_mwp"] * nb, st["arazi"], ruz, izgara, ilce, kisi, olcek="bölge")
    for c in ("t_gunes", "t_ruzgar", "t_batarya_saat"):
        tar[c] = tar[c].round(2)
    tar["secim"] = "tarama"
    isi = isi_m * es.KENT_MAHALLE * nb + kisi * (v("semt_merkezi_isi") + v("sehir_hizmet_isi")) / 1e6
    nks = tar[tar.nukleer_mw == 0]
    b2 = nks.sort_values("maliyet_usd_mwh").iloc[0]
    b3 = tar[tar.nukleer_mw == SMR_BIRIM].sort_values("maliyet_usd_mwh").iloc[0]
    esit = nks[nks.yerel_karsilama >= b3.yerel_karsilama - 0.005].sort_values("maliyet_usd_mwh")
    out, ek = [], []
    sec, bos, tb = batarya_kurali(t, cati, st["cati_mwp"] * nb, st["arazi"], ruz, b2.gunes_arazi_mw, b2.ruzgar_mw, 0, ilce, kisi,
                                  "bölge", es.KENT_MAHALLE * nb)
    tb["secim"] = "B2 batarya kuralı"
    ek.append(tb)
    o = satir("4 bölge", 4, ilce, kisi, es.KENT_MAHALLE * nb, isi, sec, bos, "çatı + bölgesel güneş ve rüzgâr + batarya",
              "karma: maliyet taramasında en ucuz nükleersiz (B2); batarya: marjinal deşarj ≥ 250 MWh/MWh·yıl", sanayi_isi)
    o["maliyet_usd_mwh_bataryasiz"] = bos["maliyet_usd_mwh"]
    out.append(o)
    o = satir("4 bölge (1 SMR seçeneği)", 4.1, ilce, kisi, es.KENT_MAHALLE * nb, isi, b3,
              tar[(tar.t_gunes == b3.t_gunes) & (tar.t_ruzgar == b3.t_ruzgar) & (tar.nukleer_mw == b3.nukleer_mw)
                  & (tar.t_batarya_saat == 0)].iloc[0],
              "çatı + güneş + rüzgâr + 1 × 300 MWe SMR (Darlington maliyeti)",
              "karma: 1 SMR'li karmalar içinde en ucuz (B3)", sanayi_isi)
    o["maliyet_usd_mwh_smr_iyimser"] = b3["maliyet_usd_mwh_smr_noak"]
    o["maliyet_usd_mwh_ayni_karsilama_nukleersiz"] = esit.iloc[0].maliyet_usd_mwh if len(esit) else np.nan
    o["ayni_karsilama_nukleersiz_karma"] = (f"güneş {esit.iloc[0].t_gunes:g}, rüzgâr {esit.iloc[0].t_ruzgar:g}, batarya "
                                            f"{esit.iloc[0].t_batarya_saat:g} saat × ortalama yük") if len(esit) else ""
    out.append(o)
    return out, pd.concat([tar] + ek)


def ulke() -> list:
    u = pd.read_csv(SON / "enerji_ulke_2050.csv")
    out = []
    for kod, sira in (("S2", 5), ("S3", 5.1)):
        r = u[u.senaryo.str.startswith(kod)].iloc[0]
        T = r.talep_twh * 1000
        dep = r.batarya_mwh + r.pompaj_mwh
        out.append(dict(kademe="5 ülke 2050 (" + r.senaryo + ")", sira=sira, iklim_ilce="ulusal", iklim="10 pilot ortalaması",
                        nufus=NUFUS_2050, mahalle_esdegeri=np.nan, elektrik_talep_gwh=T,
                        elektrik_kisi_basi_kwh=T * 1e6 / NUFUS_2050, puant_mw=r.puant_mw,
                        puant_w_kisi=r.puant_mw * 1e6 / NUFUS_2050, arazi_gunes_mw=r.gunes_mw, ruzgar_mw=r.ruzgar_mw,
                        smr_mw=r.smr_mw, yenilenebilir_pay=r.yenilenebilir_pay, nukleer_pay=r.nukleer_pay,
                        fosil_pay=r.fosil_pay, depolama_mwh=dep,
                        depolama_kwh_kisi=dep * 1000 / NUFUS_2050, depolama_saat_ort_yuk=dep / (T * 1000 / 8766),
                        maliyet_usd_mwh=r.maliyet_usd_mwh,
                        secim_kurali="fosil ≤ %10 koşuluyla en ucuz güneş–rüzgâr–batarya karması",
                        kaynaklar="ulusal karma; yerinde karşılama yerine yenilenebilir, nükleer ve fosil payı verildi"))
    return out


def main():
    sek = pd.read_csv(SON / "enerji_turkiye_nihai_sektor.csv")
    s = sek[sek.sektor == "Sanayi"].iloc[0]
    sanayi_isi = (s.toplam_twh - s.elektrik_twh) * 1e9 / s.nufus   # kWh/kişi, elektrik dışı nihai enerji [H]
    ruz = es.ruzgar_profili()
    sat, tara = [], []
    for ilce in ILCELER:
        a, ek = mahalle_semt(ilce, ruz)
        sat += a
        a, t1 = sehir(ilce, ek["isi_mahalle_gwh"], ruz)
        sat += a
        b, t = bolge(ilce, ek["isi_mahalle_gwh"], ruz, sanayi_isi)
        sat += b
        tara += [t1, t]
        tara.append(ek["mahalle_batarya"])
        print(f"  {ilce}: hazır")
    sat += ulke()
    d = pd.DataFrame(sat).sort_values(["sira", "iklim_ilce"])
    d.to_csv(SON / "enerji_kademe.csv", index=False)
    pd.concat(tara).to_csv(SON / "enerji_kademe_tarama.csv", index=False)
    cols = ["kademe", "iklim_ilce", "nufus", "elektrik_kisi_basi_kwh", "isi_kisi_basi_kwh", "puant_w_kisi", "uretim_talep_orani",
            "yerinde_karsilama_depolamasiz", "depolama_kwh_kisi", "yerinde_karsilama", "yerinde_karsilama_kis", "maliyet_usd_mwh"]
    print(d[cols].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
