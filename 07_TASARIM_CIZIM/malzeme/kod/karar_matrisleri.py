"""
Doğal ve geri dönüştürülmüş malzemeler: karar matrisleri (Faz 4 · Rapor 3)
=========================================================================
Girdi (07_TASARIM_CIZIM/malzeme/):
    sonuc_*.csv                     malzeme_modeli.py çıktıları (önce o çalışır)
    karar_esikleri.csv              sayısal ölçütlerin 1–5 puan eşikleri
    karar_girdi_malzeme.csv         25 malzeme: modeldeki karşılığı (duvar, kubbe, bina sistemi) ve uzman puanları [V]
    karar_girdi_bina_tipleri.csv    8 bina tipi: BKS, I, yükseklik
    karar_girdi_sistemler.csv       9 taşıyıcı ya da örtü sistemi: TBDY 2018 sınıfı, süneklik, izinli yükseklik
    karar_girdi_bina_sistem.csv     bina tipi × sistem × deprem tasarım sınıfı için uzman yargısı [V] ve kısa not
Çıktı:
    karar_matrisi_malzeme.csv       malzeme × 11 ölçüt. Maliyet, karbon, ısı yalıtımı, ısıl kütle ve ses modelden [H];
                                    sağlık, yangın, dayanıklılık, deprem ve mevzuat uzman puanı [V]
    karar_matrisi_denetim.csv       hesaplanan puanın önceki uzman puanından ayrıldığı hücreler
    karar_matrisi_bina_sistem.csv   bina tipi × sistem × DTS: uzman yargısı, TBDY tavanı, sonuç
Kural: sonuç = min(uzman yargısı, TBDY tavanı). Tavan TBDY 2018'den kurallı türetilir:
    md. 11.2.4 (kerpiç, moloz taş, ponza, dolgu tuğlası taşıyıcı olamaz) → yasak
    md. 4.3.4.1(a) (BKS 1'de süneklik düzeyi sınırlı sistem yok) → yasak
    Tablo 4.1 izinli en üst BYS + Tablo 3.3 yükseklik aralığı → aşılırsa yasak
    kapsam dışı sistem (md. 1.1.9, 12.1.2) → en çok "pilot" ya da "koşullu"; kanıt sınırını aşan yükseklikte "önerilmez"
Çalıştırma: PYTHONIOENCODING=utf-8 python 07_TASARIM_CIZIM/malzeme/kod/karar_matrisleri.py
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KLASOR = Path(__file__).resolve().parents[1]
SAYISAL = ["maliyet", "gomulu_karbon", "isi_yalitimi", "isil_kutle", "akustik"]
UZMAN = ["saglik", "yangin", "dayaniklilik", "deprem_tasiyici", "deprem_dolgu", "mevzuat_tedarik"]
SIRA = ["maliyet", "gomulu_karbon", "isi_yalitimi", "isil_kutle", "saglik", "yangin", "akustik", "dayaniklilik",
        "deprem_tasiyici", "deprem_dolgu", "mevzuat_tedarik"]
DURUM = {"yok": 0, "yasak": 1, "onerilmez": 2, "pilot": 3, "kosullu": 4, "onerilir": 5}
DURUM_AD = {0: "—", 1: "Yasak", 2: "Önerilmez", 3: "Pilot", 4: "Koşullu", 5: "Önerilir"}
# TBDY 2018 Tablo 3.3: BYS → en büyük bina yüksekliği (m) [DTS 1, 1a, 2, 2a ; DTS 3, 3a, 4, 4a]
HMAX = {8: (7.0, 10.5), 7: (10.5, 17.5), 6: (17.5, 28.0), 5: (28.0, 42.0), 4: (42.0, 56.0), 3: (56.0, 70.0)}


def tr(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".").replace("-", "−")


def yuzde(x, nd=1):
    """+%1,4 / −%31 biçimi."""
    if abs(x) < 0.05:
        return "±%0"
    return ("+" if x > 0 else "−") + "%" + tr(abs(x), nd)


def puan(deger, esik):
    if deger is None or (isinstance(deger, float) and np.isnan(deger)):
        return np.nan
    e = [esik.esik_5, esik.esik_4, esik.esik_3, esik.esik_2]
    for p, s in zip((5, 4, 3, 2), e):
        if (esik.yon == "kucuk_iyi" and deger <= s + 1e-9) or (esik.yon == "buyuk_iyi" and deger >= s - 1e-9):
            return p
    return 1


# ------------------------------------------------------------------ malzeme × ölçüt
def malzeme_matrisi():
    es = pd.read_csv(KLASOR / "karar_esikleri.csv").set_index("olcut")
    g = pd.read_csv(KLASOR / "karar_girdi_malzeme.csv")
    duv = pd.read_csv(KLASOR / "sonuc_duvar_sistemleri.csv").set_index("duvar_kod")
    kub = pd.read_csv(KLASOR / "sonuc_kubbe.csv").set_index("kod")
    oz = pd.read_csv(KLASOR / "sonuc_bina_senaryolari.csv").set_index(["senaryo", "sistem"])
    ref = duv.loc["W01"]
    kref = kub.loc["K1"]
    satir, denetim = [], []
    for _, r in g.iterrows():
        h = {}                      # hesaplanan ham değerler
        dayanak = []
        if isinstance(r.duvar_uygun, str):
            w = duv.loc[r.duvar_uygun]
            h["maliyet"] = w.maliyet_TL_m2 / ref.maliyet_TL_m2
            h["gomulu_karbon"] = w.karbon_kgCO2e_m2 / ref.karbon_kgCO2e_m2
            h["akustik"] = w.Rw_dB_kutle_kurali
            yal = f" ({tr(w.yalitim_cm)} cm yalıtım)" if w.yalitim_cm > 0 else " (yalıtımsız)"
            dayanak.append(f"Duvar {w.kisa_ad}{yal}, U {tr(w.U_W_m2K, 2)}: {tr(w.maliyet_TL_m2)} TL/m² "
                           f"(×{tr(h['maliyet'], 2)}), {tr(w.karbon_kgCO2e_m2, 1)} kgCO2e/m² (×{tr(h['gomulu_karbon'], 2)})"
                           + (f", biyojenik {tr(w.biyojenik_kgCO2_m2, 0)} kgCO2/m²" if w.biyojenik_kgCO2_m2 < 0 else "")
                           + (f", R'w {tr(w.Rw_dB_kutle_kurali, 0)} dB" if not np.isnan(w.Rw_dB_kutle_kurali) else ""))
        if isinstance(r.duvar_yalin, str):
            w = duv.loc[r.duvar_yalin]
            h["isi_yalitimi"] = w.U_yalin_W_m2K
            h["isil_kutle"] = w.kappa_kJ_m2K
            dayanak.append(f"yalın U {tr(w.U_yalin_W_m2K, 2)} W/m²K, κ {tr(w.kappa_kJ_m2K)} kJ/m²K")
        if isinstance(r.kubbe, str):
            k = kub.loc[r.kubbe]
            h["maliyet"] = k.maliyet_TL_m2 / kref.maliyet_TL_m2
            h["gomulu_karbon"] = k.karbon_kgCO2e_m2 / kref.karbon_kgCO2e_m2
            h["isi_yalitimi"] = k.U_kabuk_W_m2K
            h["isil_kutle"] = k.kappa_kJ_m2K
            h["akustik"] = k.Rw_dB_kutle_kurali
            dayanak.append(f"{tr(k.aciklik_m, 2 if k.aciklik_m % 1 else 0)} m: {tr(k.kutle_t_m2, 2)} t/m², "
                           f"{tr(k.karbon_kgCO2e_m2)} kgCO2e/m² (×{tr(h['gomulu_karbon'], 2)}), {tr(k.maliyet_TL_m2)} TL/m² "
                           f"örtü (×{tr(h['maliyet'], 2)}; taban 12 m ince kabuk); kabuk U {tr(k.U_kabuk_W_m2K, 1)}")
        if isinstance(r.bina_sistemi, str):
            for parca in r.bina_sistemi.split(";"):
                sen, sis = parca.split(":")
                b = oz.loc[(sen, sis)]
                b0 = oz.loc[(sen, "R0")]
                if sis != "R0":
                    dayanak.append(f"bina ({'ev' if sen == 'EV120' else 'okul'} {sis}): {yuzde(b.fark_yuzde_R0)} TL, "
                                   f"{yuzde(b.karbon_fark_yuzde_R0, 0)} CO2")
                if "maliyet" not in h:          # duvarı olmayan sistem (ahşap karkas): bina oranı
                    h["maliyet"] = b.TL_m2_bina / b0.TL_m2_bina
                    h["gomulu_karbon"] = b.kgCO2e_m2_degisen / b0.kgCO2e_m2_degisen
        s = dict(kod=r.kod, malzeme=r.malzeme, aile=r.aile)
        H = []
        for o in SAYISAL:
            p = puan(h.get(o, np.nan), es.loc[o])
            v = r[f"{o}_V"]
            if not np.isnan(p):
                s[o] = int(p)
                H.append(o)
                if not np.isnan(v) and int(v) != int(p):
                    denetim.append(dict(kod=r.kod, malzeme=r.malzeme, olcut=o, onceki_uzman_puani=int(v), hesaplanan=int(p),
                                        ham_deger=round(h[o], 3)))
            else:
                s[o] = v
        for o in UZMAN:
            s[o] = r[o]
        s["hesaplanan_olcutler"] = ", ".join(H) if H else "—"
        s["sayisal_dayanak"] = "; ".join(dayanak) if dayanak else "—"
        s.update(onerilen_rol=r.onerilen_rol, temel_gerekce=r.temel_gerekce, kanit=r.kanit)
        satir.append(s)
    km = pd.DataFrame(satir)[["kod", "malzeme", "aile"] + SIRA + ["hesaplanan_olcutler", "sayisal_dayanak",
                                                                 "onerilen_rol", "temel_gerekce", "kanit"]]
    for o in SIRA:
        km[o] = km[o].astype("Int64")
    return km, pd.DataFrame(denetim)


# ------------------------------------------------------------------ bina tipi × sistem
def yer_tutucu(metin, oz, dp, ke, kub):
    if not isinstance(metin, str):
        return ""

    def cevir(m):
        p = m.group(1).split(":")
        if p[0] == "M":
            return yuzde(oz.loc[(p[1], p[2]), "fark_yuzde_R0"])
        if p[0] == "C":
            return yuzde(oz.loc[(p[1], p[2]), "karbon_fark_yuzde_R0"], 0)
        if p[0] == "V":
            return tr(dp[(dp.sistem == p[1]) & (dp.S_DS == 1.0)].V_oran_R0.iloc[0], 1) + "×"
        if p[0] == "TAU":
            return tr(dp[(dp.sistem == p[1]) & (dp.S_DS == float(p[2]))].ort_kayma_gerilmesi_MPa.iloc[0], 2)
        if p[0] == "KE":
            return tr(ke[(ke.kod == p[1]) & (ke.S_DS == 1.0)].V_oran_KE4.iloc[0], 0) + "×"
        if p[0] == "KBT":
            return tr(kub.loc[p[1], "kutle_t_m2"], 2)
        raise KeyError(m.group(0))

    return re.sub(r"\{([^}]+)\}", cevir, metin).replace("\\n", " | ")     # " | ": grafikte satır sonu


def tbdy_tavani(b, s, dts):
    """(tavan, gerekçe): TBDY 2018'den kurallı."""
    if s.suneklik == "yasak":
        return "yasak", s.madde
    if s.suneklik == "sinirli" and b.BKS == 1:
        return "yasak", "md. 4.3.4.1(a)"
    if not np.isnan(s.izinli_en_ust_BYS):
        hmax = HMAX[int(s.izinli_en_ust_BYS)][0 if dts == "1–2" else 1]
        if b.H_m > hmax + 1e-9:
            return "yasak", f"Tablo 4.1 + 3.3: H ≤ {tr(hmax, 1 if hmax % 1 else 0)} m"
    if s.suneklik == "kapsam_disi":
        if not np.isnan(s.kanit_H_max_m) and b.H_m > s.kanit_H_max_m:
            return "onerilmez", f"kapsam dışı; kanıt sınırı H ≤ {tr(s.kanit_H_max_m, 1)} m"
        return s.kapsam_disi_tavan, "kapsam dışı (md. 1.1.9)"
    return "onerilir", "TBDY kapsamında"


def bina_matrisi():
    B = pd.read_csv(KLASOR / "karar_girdi_bina_tipleri.csv").set_index("kod")
    S = pd.read_csv(KLASOR / "karar_girdi_sistemler.csv").set_index("kod")
    Y = pd.read_csv(KLASOR / "karar_girdi_bina_sistem.csv")
    oz = pd.read_csv(KLASOR / "sonuc_bina_senaryolari.csv").set_index(["senaryo", "sistem"])
    dp = pd.read_csv(KLASOR / "sonuc_deprem_talebi.csv")
    ke = pd.read_csv(KLASOR / "sonuc_kubbeli_ev.csv")
    kub = pd.read_csv(KLASOR / "sonuc_kubbe.csv").set_index("kod")
    satir = []
    for _, y in Y.iterrows():
        b, s = B.loc[y.bina], S.loc[y.sistem]
        for dts, yk, nk in (("1–2", "yargi_12", "not_12"), ("3–4", "yargi_34", "not_34")):
            yargi = y[yk]
            if yargi == "yok":
                tavan, gerekce, sonuc = "yok", "", "yok"
            else:
                tavan, gerekce = tbdy_tavani(b, s, dts)
                sonuc = min(yargi, tavan, key=DURUM.get)
            satir.append(dict(bina_kod=y.bina, bina_tipi=b.bina_tipi, kat=b.kat_profili, BKS=b.BKS, I=b.I, H_m=b.H_m,
                              sistem_kod=y.sistem, sistem=s.sistem, DTS=dts, uzman_yargisi=yargi, tbdy_tavani=tavan,
                              tavan_gerekcesi=gerekce, sonuc=sonuc, sonuc_ad=DURUM_AD[DURUM[sonuc]],
                              tavanla_duzeltildi=int(DURUM[yargi] > DURUM[tavan]) if yargi != "yok" else 0,
                              not_=yer_tutucu(y[nk], oz, dp, ke, kub)))
    return pd.DataFrame(satir).rename(columns={"not_": "not"})


def main():
    km, den = malzeme_matrisi()
    km.to_csv(KLASOR / "karar_matrisi_malzeme.csv", index=False, encoding="utf-8")
    den.to_csv(KLASOR / "karar_matrisi_denetim.csv", index=False, encoding="utf-8")
    bm = bina_matrisi()
    bm.to_csv(KLASOR / "karar_matrisi_bina_sistem.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 250, "display.max_columns", 30, "display.max_colwidth", 40)
    print(km[["kod"] + SIRA + ["hesaplanan_olcutler"]].to_string(index=False))
    print(f"\nHesaplanan puanın önceki uzman puanından ayrıldığı hücre: {len(den)}")
    print(den.to_string(index=False))
    dz = bm[bm.tavanla_duzeltildi == 1]
    print(f"\nTBDY tavanıyla düşürülen yargı: {len(dz)}")
    print(dz[["bina_tipi", "sistem_kod", "DTS", "uzman_yargisi", "tbdy_tavani", "tavan_gerekcesi"]].to_string(index=False))
    pv = bm.pivot_table(index=["bina_tipi", "DTS"], columns="sistem_kod", values="sonuc_ad", aggfunc="first", sort=False)
    print(pv.to_string())


if __name__ == "__main__":
    main()
