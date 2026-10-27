"""
Model mahalle v2.1 — enerji dengesi (Faz 4 · Rapor 5)
====================================================
Girdi:
  07_TASARIM_CIZIM/model_mahalle_v2/kod/plan_modeli.py  (yalnız içe aktarılır; çatı ve kat alanı çizimden)
  03_VERI/ham/enerji/pvgis/seri_<ilçe>_<yönelim>.json.gz (enerji_veri.py; PVGIS 5.3, 2019–2023 saatlik)
Çıktı (05_ANALIZ/sonuclar/):
  enerji_mahalle_envanter.csv      parsel/donatı düzeyinde çatı, kWp, konut, kat alanı
  enerji_mahalle_yillik.csv        10 pilot × talep bileşenleri, GES, öz tüketim, puant (5 yıl ortalaması)
  enerji_mahalle_aylik.csv         10 pilot × 12 ay denge
  enerji_mahalle_batarya.csv       10 pilot × batarya boyu → öz tüketim, öz yeterlilik, puant
  enerji_mahalle_isitma.csv        10 pilot × ısıtma seçeneği → enerji, CO2, hane başı maliyet, sondaj alanı
  enerji_mahalle_duyarlilik.csv    yalıtım, şarj, çatı payı duyarlılığı
  enerji_varsayimlar.csv           bütün varsayımlar (enerji_ortak.VARSAYIM)

Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/enerji_mahalle.py   (≈ 1–2 dk)
"""
from __future__ import annotations

import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enerji_ortak import (EV_AKILLI, EV_DENETIMSIZ, KONUT_DISI, KONUT_GUN, KONUT_TATIL, MM_KOD, PILOT_ANAHTAR, SICAKSU_GUN,  # noqa: E402
                          SOKAK, SON, YILLAR, batarya, cop_hava, cop_toprak, crf, gunluk_profil, mevsim_aydinlatma,
                          okul_tatil_carpani, pilot_pv, saat_ekseni, v, varsayim_tablosu)

os.environ.setdefault("MM_SURUM", "2.1")
sys.path.insert(0, str(MM_KOD))
_cwd = os.getcwd()
os.chdir(MM_KOD)
import plan_modeli as pm  # noqa: E402
from ortak import HANE_BUYUKLUGU  # noqa: E402

os.chdir(_cwd)

NY = len(YILLAR)
PISIRME = 300.0          # [V] kWh/hane·yıl — indüksiyon pişirme (bugünkü senaryoda gazla)


# --------------------------------------------------------------------------------------
# 1. Bina ve çatı envanteri (çizimden)
# --------------------------------------------------------------------------------------
def envanter() -> pd.DataFrame:
    P = pm.model()
    sat = []
    for i, p in enumerate(P["parseller"]):
        tip = p["tip"]
        binalar = p["binalar"]
        katlar = p.get("bina_katlari", [p["kat"]] * len(binalar))
        minx, miny, maxx, maxy = p["poly"].bounds
        r = dict(birim=f"P{i:04d}", tur="konut_parsel", tip=tip, konut=float(p["konut"]), taban=0.0, kat_alani=p["kat_alani"],
                 ticari=float(p.get("ticari", 0.0)), otopark_alan=0.0, G20=0.0, D20=0.0, B20=0.0, D10=0.0, B10=0.0)
        for b, k in zip(binalar, katlar):
            a = b.area
            r["taban"] += a
            bx0, by0, bx1, by1 = b.bounds
            if tip == "T4":                                            # düz çatı, doğu–batı 10°
                r["D10"] += a * v("duz_pay") / 2
                r["B10"] += a * v("duz_pay") / 2
                continue
            if tip in ("T1", "T2"):                                    # sıra ev: mahya sıra boyunca (cephe yönü)
                db = (maxx - minx) <= (maxy - miny)
            else:                                                      # T3: kanadın uzun ekseni
                db = (bx1 - bx0) >= (by1 - by0)
            if db:
                r["G20"] += a * v("egimli_guney_pay")
            else:
                r["D20"] += a * v("egimli_dogu_bati_pay") / 2
                r["B20"] += a * v("egimli_dogu_bati_pay") / 2
        sat.append(r)
    for j, d in enumerate(P["donatilar"]):
        if not d["binalar"]:
            continue
        taban = sum(b.area for b in d["binalar"])
        tur = d["tur"]
        r = dict(birim=f"D{j:02d}", tur=tur, tip="donatı", konut=0.0, taban=taban, kat_alani=taban * d["kat"],
                 ticari=0.0, otopark_alan=0.0, G20=0.0, D20=0.0, B20=0.0, D10=0.0, B10=0.0)
        if tur == "otopark":
            r["ticari"] = pm.MOBILITE_ZEMIN_TICARI
            r["otopark_alan"] = taban * d["kat"] - pm.MOBILITE_ZEMIN_TICARI
        elif tur == "teknik":
            r["ticari"] = 0.0
        else:
            r["ticari"] = r["kat_alani"]                               # ısıtılan konut dışı alan
        if tur not in ("semt_camii", "kucuk_cami"):                    # [V] kubbe/minare ve görünüm: camide GES yok
            r["D10"] = taban * v("duz_pay") / 2
            r["B10"] = taban * v("duz_pay") / 2
        r["ad"] = d["ad"]
        sat.append(r)
    e = pd.DataFrame(sat)
    for y in ("G20", "D20", "B20", "D10", "B10"):
        e[f"kwp_{y}"] = e[y] * v("kwp_m2")
    e["kwp"] = e[[c for c in e.columns if c.startswith("kwp_")]].sum(axis=1)
    e["konut_alan_net"] = (e["kat_alani"] - e["ticari"]).clip(lower=0) * v("net_brut_oran")
    e.loc[e.tip == "donatı", "konut_alan_net"] = 0.0
    e["konut_disi_alan_net"] = e["ticari"] * v("net_brut_oran")
    return e


# --------------------------------------------------------------------------------------
# 2. Birim talep profilleri (hane başına, m² başına) — saatlik, 2019–2023
# --------------------------------------------------------------------------------------
def birim_profiller(T: np.ndarray, H: float, ev_profil: str = "akilli", isitma: str = "hava") -> dict:
    ek = saat_ekseni()
    ay_isik = mevsim_aydinlatma(ek)
    p_konut = gunluk_profil(ek, KONUT_GUN, KONUT_TATIL) * ay_isik
    p_konut *= NY / p_konut.sum()          # profiller: her yıl toplamı 1 (5 yılda 5)
    p_kd = gunluk_profil(ek, KONUT_DISI) * okul_tatil_carpani(ek)
    p_kd *= NY / p_kd.sum()
    p_sokak = gunluk_profil(ek, SOKAK) * (1 + 0.25 * np.cos(2 * np.pi * (ek.dayofyear.to_numpy() - 355) / 365.25))
    p_sokak *= NY / p_sokak.sum()
    p_ev = gunluk_profil(ek, EV_AKILLI if ev_profil == "akilli" else EV_DENETIMSIZ)

    # soğuk su sıcaklığı: 30 günlük hareketli ortalama hava sıcaklığı, 7–22 °C
    T_su = pd.Series(T).rolling(24 * 30, min_periods=1, center=True).mean().clip(7, 22).to_numpy()
    ss_isi = (v("sicak_su") * 4.186 * (45 - T_su) / 3600 * 1.15) * HANE_BUYUKLUGU   # kWh/hane·gün
    ss_isi_saat = ss_isi * SICAKSU_GUN[ek.hour.to_numpy()] / SICAKSU_GUN.sum()          # günlük enerjiyi saatlere dağıt
    isitma_isi = H * np.maximum(v("T_denge") - T, 0) / 1000                            # kWh/m²·saat (net)
    sogutma_isi = v("H_sogutma") * v("sogutma_pay") * np.maximum(T - 24, 0) / 1000

    if isitma == "hava":
        cop_h, cop_s = cop_hava(T, v("T_gidis_isitma")), cop_hava(T, v("T_gidis_sicaksu"))
        k = 1.0
    elif isitma == "5g":
        cop_h, cop_s = cop_toprak(v("T_gidis_isitma")), cop_toprak(v("T_gidis_sicaksu"))
        k = 1 + v("sebeke_kaybi_5g")
    else:                                                                              # gaz: elektrik yok
        cop_h = cop_s = np.inf
        k = 0.0
    return dict(
        hane_aletler=v("hane_elektrik") * p_konut,                                 # kWh/hane·saat
        hane_ss_isi=ss_isi_saat,                                                         # kWh/hane·saat (ısı)
        hane_ss_el=ss_isi_saat * k / cop_s if k else np.zeros(len(ek)),
        m2_isitma_isi=isitma_isi,
        m2_isitma_el=isitma_isi * k / cop_h if k else np.zeros(len(ek)),
        m2_sogutma_el=sogutma_isi / v("EER"),
        m2_konut_disi_el=v("konut_disi_elektrik") * p_kd,
        m2_otopark_el=v("otopark_elektrik") * p_sokak,
        kisi_kamusal_el=v("kamusal") * p_sokak,
        arac_el=v("arac_km") * v("ev_tuketim") * p_ev,
        cop_h=cop_h, cop_s=cop_s,
    )


# --------------------------------------------------------------------------------------
# 3. Mahalle dengesi
# --------------------------------------------------------------------------------------
def mahalle(ilce: str, e: pd.DataFrame, H: float | None = None, ev_profil="akilli", isitma="hava",
            cati_carpan=1.0, pv=None):
    pv = pilot_pv(ilce) if pv is None else pv
    T = pv["T"]
    H = v("H_yeni") if H is None else H
    b = birim_profiller(T, H, ev_profil, isitma)
    n_konut = e["konut"].sum()
    A_k = e["konut_alan_net"].sum()
    A_kd = e["konut_disi_alan_net"].sum()
    A_op = e["otopark_alan"].sum()
    n_kisi = n_konut * HANE_BUYUKLUGU
    n_arac = round(n_konut * 0.57)                                   # plan: 1.235 yer, 0,57/hane [D: metrikler.csv]
    bil = dict(
        aletler=n_konut * b["hane_aletler"],
        sicak_su=n_konut * b["hane_ss_el"],
        isitma=(A_k + A_kd) * b["m2_isitma_el"],
        sogutma=(A_k + A_kd) * b["m2_sogutma_el"],
        konut_disi=A_kd * b["m2_konut_disi_el"],
        otopark=A_op * b["m2_otopark_el"],
        kamusal=n_kisi * b["kisi_kamusal_el"],
        ev_sarj=n_arac * b["arac_el"],
    )
    talep = sum(bil.values())
    uretim = sum(e[f"kwp_{y}"].sum() * pv[y] for y in ("G20", "D20", "B20", "D10", "B10")) * cati_carpan
    isi = dict(isitma=(A_k + A_kd) * b["m2_isitma_isi"], sicak_su=n_konut * b["hane_ss_isi"])
    return dict(talep=talep, uretim=uretim, bilesen=bil, isi=isi, b=b, T=T, n_konut=n_konut, A_k=A_k, A_kd=A_kd,
                n_kisi=n_kisi, n_arac=n_arac, pv=pv)


def parsel_oz_tuketim(ilce: str, e: pd.DataFrame, m: dict) -> float:
    """Bugünkü mevzuat: her parsel (bina) kendi çatısıyla kendi tüketimini karşılar (m.29 birleştirme bina içinde)."""
    b, pv = m["b"], m["pv"]
    hane = b["hane_aletler"] + b["hane_ss_el"]
    m2 = b["m2_isitma_el"] + b["m2_sogutma_el"]
    m2kd = b["m2_konut_disi_el"]
    top = 0.0
    for _, r in e.iterrows():
        u = sum(r[f"kwp_{y}"] * pv[y] for y in ("G20", "D20", "B20", "D10", "B10"))
        if r["kwp"] == 0:
            continue
        t = r["konut"] * hane + r["konut_alan_net"] * m2 + r["konut_disi_alan_net"] * (m2kd + m2)
        if r["tur"] == "otopark":                                   # mobilite noktası: şarj ve otopark bu sayaçta
            t = t + m["bilesen"]["ev_sarj"] / 4 + r["otopark_alan"] * b["m2_otopark_el"]
        top += np.minimum(u, t).sum()
    return top


BATARYA_MWH = [0, 1, 2, 3, 5, 7.5, 10, 15, 20, 30]
MARJINAL_ESIK = 250.0    # [V] MWh/MWh·yıl: son eklenen 1 MWh yılda ≥ 250 MWh (≈ 0,7 döngü/gün) ek deşarj getirmeli


def calistir():
    e = envanter()
    e.to_csv(SON / "enerji_mahalle_envanter.csv", index=False)
    print(f"Envanter: {len(e)} birim, konut {e.konut.sum():.0f}, taban {e.taban.sum() / 1e4:.2f} ha, "
          f"kWp {e.kwp.sum() / 1000:.2f} MWp, konut net alan {e.konut_alan_net.sum():,.0f} m², "
          f"konut dışı {e.konut_disi_alan_net.sum():,.0f} m²")
    yillik, aylik, bat, isit, duy = [], [], [], [], []
    ek = saat_ekseni()
    for ilce in PILOT_ANAHTAR:
        pv = pilot_pv(ilce)
        m = mahalle(ilce, e, pv=pv)
        t, u = m["talep"], m["uretim"]
        oz = np.minimum(t, u).sum()
        oz_parsel = parsel_oz_tuketim(ilce, e, m)
        T = m["T"]
        # --- bugünkü kullanım (doğal gaz ısıtma ve pişirme, benzinli araç, GES yok) ---
        b = m["b"]
        bugun = (m["bilesen"]["aletler"] * (v("hane_elektrik") - PISIRME) / v("hane_elektrik")
                 + m["bilesen"]["sogutma"] + m["bilesen"]["konut_disi"] + m["bilesen"]["otopark"] + m["bilesen"]["kamusal"])
        r = dict(ilce=ilce, kwp=e.kwp.sum(), verim_kwh_kwp=u.sum() / NY / e.kwp.sum(),
                 T_ort=T.mean(), HDH15=np.maximum(15 - T, 0).sum() / NY, CDH24=np.maximum(T - 24, 0).sum() / NY,
                 uretim_mwh=u.sum() / NY / 1000, talep_mwh=t.sum() / NY / 1000,
                 **{f"talep_{k}_mwh": x.sum() / NY / 1000 for k, x in m["bilesen"].items()},
                 isi_isitma_mwh=m["isi"]["isitma"].sum() / NY / 1000, isi_sicaksu_mwh=m["isi"]["sicak_su"].sum() / NY / 1000,
                 isitma_kwh_m2=m["isi"]["isitma"].sum() / NY / (m["A_k"] + m["A_kd"]),
                 scop_isitma=m["isi"]["isitma"].sum() / m["bilesen"]["isitma"].sum(),
                 uretim_talep_orani=u.sum() / t.sum(),
                 oz_tuketim_mahalle=oz / u.sum(), oz_yeterlilik_mahalle=oz / t.sum(),
                 oz_tuketim_parsel=oz_parsel / u.sum(), oz_yeterlilik_parsel=oz_parsel / t.sum(),
                 puant_talep_kw=t.max(), puant_bugun_kw=bugun.max(), talep_bugun_mwh=bugun.sum() / NY / 1000,
                 puant_veris_kw=np.maximum(u - t, 0).max(), puant_alis_gesli_kw=np.maximum(t - u, 0).max(),
                 kisi_basi_talep_kwh=t.sum() / NY / m["n_kisi"], hane_basi_talep_kwh=t.sum() / NY / m["n_konut"])
        # aylık netleşme (mesken mahsuplaşması aylık): öz yeterlilik fatura düzeyinde
        dfm = pd.DataFrame({"t": t, "u": u}, index=ek)
        ay = dfm.groupby([dfm.index.year, dfm.index.month]).sum()
        r["oz_yeterlilik_aylik_mahsup"] = np.minimum(ay.t, ay.u).sum() / ay.t.sum()
        yillik.append(r)
        # --- aylık denge (5 yıl ortalaması) ---
        bl = pd.DataFrame({k: x for k, x in m["bilesen"].items()}, index=ek)
        bl["uretim"] = u
        bl["oz"] = np.minimum(t, u)
        ma = bl.groupby(bl.index.month).sum() / NY / 1000
        ma["ilce"] = ilce
        ma["T_ort"] = pd.Series(T, index=ek).groupby(ek.month).mean()
        aylik.append(ma.reset_index(names="ay"))
        # --- batarya ---
        net = t - u
        for c in BATARYA_MWH:
            al, ver, des = batarya(net, c * 1000)
            bat.append(dict(ilce=ilce, batarya_mwh=c, guc_mw=c / v("batarya_saat"),
                            oz_yeterlilik=1 - al.sum() / t.sum(), oz_tuketim=1 - ver.sum() / u.sum(),
                            alis_mwh=al.sum() / NY / 1000, veris_mwh=ver.sum() / NY / 1000,
                            desarj_mwh=des / NY / 1000, puant_alis_kw=al.max(), puant_veris_kw=ver.max(),
                            dongu_yil=des / NY / (c * 1000) if c else np.nan))
        # --- ısıtma seçenekleri ---
        isi_top = (m["isi"]["isitma"] + m["isi"]["sicak_su"]).sum() / NY       # kWh ısı/yıl
        hane = m["n_konut"]
        el_hava = (m["bilesen"]["isitma"] + m["bilesen"]["sicak_su"]).sum() / NY
        m5 = mahalle(ilce, e, isitma="5g", pv=pv)
        el_5g = (m5["bilesen"]["isitma"] + m5["bilesen"]["sicak_su"]).sum() / NY
        gaz_kwh = isi_top / v("kombi_verim")
        ef = v("ef_sebeke_2023")
        # hane başı maliyet yalnız konut ısısıyla: konut alanının ısıtması + sıcak su
        kp = m["A_k"] / (m["A_k"] + m["A_kd"])
        isi_konut = (m["isi"]["isitma"].sum() * kp + m["isi"]["sicak_su"].sum()) / NY
        el_hava_k = (m["bilesen"]["isitma"].sum() * kp + m["bilesen"]["sicak_su"].sum()) / NY
        el_5g_k = (m5["bilesen"]["isitma"].sum() * kp + m5["bilesen"]["sicak_su"].sum()) / NY
        # GES'in saatlik olarak karşıladığı pay (ısı pompası yükü kışa yığıldığı için yıllık ortalamadan düşük)
        yerel = np.minimum(t, u) / np.maximum(t, 1e-9)
        pay_yerel = ((m["bilesen"]["isitma"] + m["bilesen"]["sicak_su"]) * yerel).sum() / (
            m["bilesen"]["isitma"] + m["bilesen"]["sicak_su"]).sum()
        r["isi_pompasi_ges_payi"] = pay_yerel
        # CO2: bugünkü yol (gaz ısınma ve pişirme, benzinli araç) ↔ tam elektrik + çatı GES (şebeke alışı × 2023 faktörü)
        benzin_l = m["n_arac"] * v("arac_km") * v("icten_yanmali")
        gaz_bugun = gaz_kwh + PISIRME * hane / 0.5                                # pişirme ocağı verimi 0,5 [V]
        r["co2_bugun_t"] = (bugun.sum() / NY * ef + gaz_bugun * v("ef_gaz")) / 1000 + benzin_l * v("ef_benzin") / 1000
        r["co2_elektrik_ges_t"] = np.maximum(t - u, 0).sum() / NY * ef / 1000
        r["co2_elektrik_ges_mahsup_t"] = (t - u).sum() / NY * ef / 1000
        r["co2_elektrik_gessiz_t"] = t.sum() / NY * ef / 1000
        # sondaj alanı (5. nesil): en yüksek saatlik ısı çekişi
        cop5 = cop_toprak(v("T_gidis_isitma"))
        cekis = (m["isi"]["isitma"] + m["isi"]["sicak_su"]) * (1 + v("sebeke_kaybi_5g")) * (1 - 1 / cop5)
        sondaj_kw = v("sondaj_ozgul") * v("sondaj_derinlik") / 1000
        n_sondaj = int(np.ceil(cekis.max() / sondaj_kw))
        alan_ha = n_sondaj * v("sondaj_aralik") ** 2 / 1e4
        ozgul_kwh_m = cekis.sum() / NY / (n_sondaj * v("sondaj_derinlik"))
        gk = isi_konut / v("kombi_verim")
        for ad, el, gaz, el_k, tl_k, tl_k_dusuk in [
            ("Doğal gaz kombi (yoğuşmalı)", 0.0, gaz_kwh, 0.0, gk / v("gaz_kwh_sm3") * v("gaz_konut"),
             gk / v("gaz_kwh_sm3") * v("gaz_konut")),
            ("Hava kaynaklı ısı pompası (bireysel)", el_hava, 0.0, el_hava_k, el_hava_k * v("tarife_yuksek"),
             el_hava_k * v("tarife_dusuk")),
            ("5. nesil toprak kaynaklı bölgesel şebeke", el_5g, 0.0, el_5g_k, el_5g_k * v("tarife_yuksek"),
             el_5g_k * v("tarife_dusuk")),
            ("Jeotermal bölgesel ısıtma (uygun sahada)", 0.0, 0.0, 0.0, isi_konut * v("jeotermal_tarife"),
             isi_konut * v("jeotermal_tarife")),
        ]:
            isit.append(dict(ilce=ilce, secenek=ad, isi_mwh=isi_top / 1000, elektrik_mwh=el / 1000, gaz_mwh=gaz / 1000,
                             co2_t=(gaz * v("ef_gaz") + el * ef) / 1000,
                             co2_t_gesli=(gaz * v("ef_gaz") + el * ef * (1 - pay_yerel)) / 1000,
                             hane_isi_kwh=isi_konut / hane, hane_elektrik_kwh=el_k / hane,
                             hane_basi_tl=tl_k / hane, hane_basi_tl_dusuk_kademe=tl_k_dusuk / hane,
                             scop=(isi_top / el) if el else np.nan,
                             sondaj_adet=n_sondaj if "5." in ad else np.nan, sondaj_alan_ha=alan_ha if "5." in ad else np.nan,
                             sondaj_kwh_m_yil=ozgul_kwh_m if "5." in ad else np.nan))
        # --- duyarlılık ---
        for ad, kw in [("Temel (H 1,0; akıllı şarj; çatı %100)", {}),
                       ("Yüksek yalıtım (H 0,6)", dict(H=v("H_iyi"))),
                       ("TS 825 asgarisi (H 1,5)", dict(H=v("H_ts825"))),
                       ("Mevcut stok yalıtımı (H 2,0)", dict(H=v("H_stok"))),
                       ("Denetimsiz akşam şarjı", dict(ev_profil="denetimsiz")),
                       ("Çatı payı −%30", dict(cati_carpan=0.7)),
                       ("5. nesil şebeke", dict(isitma="5g"))]:
            mm = mahalle(ilce, e, pv=pv, **kw) if kw else m
            tt, uu = mm["talep"], mm["uretim"]
            ozz = np.minimum(tt, uu).sum()
            al, ver, des = batarya(tt - uu, 5000)
            duy.append(dict(ilce=ilce, durum=ad, talep_mwh=tt.sum() / NY / 1000, uretim_mwh=uu.sum() / NY / 1000,
                            oz_yeterlilik=ozz / tt.sum(), oz_tuketim=ozz / uu.sum(),
                            oz_yeterlilik_5mwh=1 - al.sum() / tt.sum(), puant_kw=tt.max(),
                            aralik_acik_mwh=(np.maximum(tt - uu, 0)[ek.month == 12]).sum() / NY / 1000))
        print(f"  {ilce:11s} GES {r['uretim_mwh']:6.0f} MWh ({r['verim_kwh_kwp']:.0f} kWh/kWp) · talep {r['talep_mwh']:6.0f} MWh"
              f" · oran {r['uretim_talep_orani']:.2f} · öz yet. mahalle {r['oz_yeterlilik_mahalle']:.1%} / parsel "
              f"{r['oz_yeterlilik_parsel']:.1%} · ısıtma {r['isitma_kwh_m2']:.0f} kWh/m² · SCOP {r['scop_isitma']:.2f}")
    pd.DataFrame(yillik).to_csv(SON / "enerji_mahalle_yillik.csv", index=False)
    pd.concat(aylik).to_csv(SON / "enerji_mahalle_aylik.csv", index=False)
    b = pd.DataFrame(bat)
    # önerilen batarya: ek 1 MWh'nin yılda ≥ MARJINAL_ESIK MWh ek deşarj getirdiği en büyük boy [V]
    b["marjinal_desarj_mwh_per_mwh"] = b.groupby("ilce")["desarj_mwh"].diff() / b.groupby("ilce")["batarya_mwh"].diff()
    uygun = b[b.marjinal_desarj_mwh_per_mwh >= MARJINAL_ESIK].groupby("ilce")["batarya_mwh"].max()
    b["onerilen"] = b.batarya_mwh == b.ilce.map(uygun)
    b.to_csv(SON / "enerji_mahalle_batarya.csv", index=False)
    pd.DataFrame(isit).to_csv(SON / "enerji_mahalle_isitma.csv", index=False)
    pd.DataFrame(duy).to_csv(SON / "enerji_mahalle_duyarlilik.csv", index=False)
    varsayim_tablosu().to_csv(SON / "enerji_varsayimlar.csv", index=False)
    print("Yazıldı: enerji_mahalle_*.csv, enerji_varsayimlar.csv")


if __name__ == "__main__":
    calistir()
