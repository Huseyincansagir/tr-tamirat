"""
Doğal ve geri dönüştürülmüş yapı malzemeleri: senaryo hesabı (Faz 4 · Rapor 3)
===============================================================================
Girdi (07_TASARIM_CIZIM/malzeme/, hepsi açık varsayım tablosu):
    genel_varsayimlar.csv     fiyat tabanı, işçilik, tebliğ BM'leri, TS 825 sınırları, derece-gün, deprem ve enkaz
    malzeme_parametreleri.csv yoğunluk, λ, ısı kapasitesi, karbon (A1–A3), biyojenik karbon, fiyat, işçilik
    duvar_katmanlari.csv      12 dış ve 6 iç duvar; katman sırası içten dışa
    bina_geometrisi.csv       120 m² iki katlı ev (EV120) ve 1.000 m² iki katlı okul (OKUL1000)
    bina_elemanlari.csv       sistem başına eleman miktarları (geometri ifadeleriyle)
    kubbe_sistemleri.csv      dört kubbe ve tonoz sistemi
Çıktı (aynı klasör):
    sonuc_duvar_sistemleri.csv  duvar m² başına U, kütle, karbon, maliyet, işçilik, ısı kapasitesi, ses
    sonuc_u_bolge.csv           TS 825:2024 bölgelerine göre gereken yalıtım ve yalnız toprakla gereken kalınlık
    sonuc_bina_senaryolari.csv  sistem başına TL/m², kgCO2e/m², işçilik, kütle, ömür sonu, U
    sonuc_bina_elemanlari.csv   eleman dökümü
    sonuc_enerji.csv            dış duvar ısı kaybı ve 50 yıllık işletme karbonu
    sonuc_deprem_talebi.csv     deprem kütlesi ve eşdeğer taban kesme kuvveti (S_DS'ye göre)
    sonuc_kubbe.csv             örtülen m² başına kütle, karbon, maliyet; kabuğun U değeri, ısı kapasitesi, ses
    sonuc_kubbeli_ev.csv        tek katlı 120 m² evde örtü seçeneğine göre deprem ağırlığı ve taban kesme kuvveti
    sonuc_enkaz.csv             6 Şubat enkazının geri kazanım hesabı
    sonuc_duyarlilik.csv        ana varsayımların sonuçlara etkisi
Çalıştırma (Python 3.11):
    PYTHONIOENCODING=utf-8 python 07_TASARIM_CIZIM/malzeme/kod/malzeme_modeli.py
    (bütün zincir için: PYTHONIOENCODING=utf-8 python 07_TASARIM_CIZIM/malzeme/kod/hepsini_calistir.py)
Rastgelelik yoktur; aynı girdi aynı çıktıyı verir.
Deprem kütlesi: bina_elemanlari.csv'deki deprem_kutlesi katsayısı elemanın deprem hesabına giren payıdır.
Duvarlarda 0,75 (iki katlı evde zemin kat duvarlarının alt yarısı doğrudan temele aktarılır), kolonlarda 0,9, döşeme
ve hatılda 1, temelde 0.
"""
import copy
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KLASOR = Path(__file__).resolve().parents[1]
YALITIM_LAMBDA = 0.08          # bu değerin altındaki katmanlar "yalıtım" sayılır (ısı kapasitesi hesabında durulur)
TOPRAK_SAMAN = ["RE_STAB", "RE_YALIN", "CEB14", "KERPIC", "HTS", "SAMAN", "KIL_SIVA", "KIREC_SIVA", "SUPERADOBE"]


def oku_genel():
    g = pd.read_csv(KLASOR / "genel_varsayimlar.csv")
    d = {}
    for k, v in zip(g.anahtar, g.deger):
        try:
            d[k] = float(v)
        except ValueError:
            d[k] = v
    return d


class Model:
    """Bütün hesaplar. `ayar` ile varsayımlar değiştirilebilir (duyarlılık analizi)."""

    def __init__(self, ayar=None):
        ayar = ayar or {}
        self.G = oku_genel()
        self.G.update(ayar.get("G", {}))
        self.M = pd.read_csv(KLASOR / "malzeme_parametreleri.csv").set_index("kod")
        for (kod, kolon), deger in ayar.get("M", {}).items():
            self.M.loc[kod, kolon] = deger
        for kod, carpan in ayar.get("iscilik_carpani", {}).items():
            self.M.loc[kod, "iscilik_sa"] *= carpan
        self.ucret_carpani = ayar.get("ucret_carpani", 1.0)
        self.D = pd.read_csv(KLASOR / "duvar_katmanlari.csv")
        self.GEO = pd.read_csv(KLASOR / "bina_geometrisi.csv")
        self.E = pd.read_csv(KLASOR / "bina_elemanlari.csv")
        for kol in ["sistem_ad", "kisa_ad", "aile", "deprem_R", "deprem_D", "Ct"]:
            self.E[kol] = self.E.groupby(["senaryo", "sistem"])[kol].transform("first")
        self.K = pd.read_csv(KLASOR / "kubbe_sistemleri.csv")
        self.bolge = int(self.G["tasarim_bolgesi"])
        self._turet()

    # ---------- malzeme ----------
    def _turet(self):
        G, M = self.G, self.M
        cp = M["cimento_payi"].fillna(0.0)
        bos = M["karbon_kgCO2e_kg"].isna()
        M.loc[bos, "karbon_kgCO2e_kg"] = (cp * G["cimento_kgCO2e_kg"] + (1 - cp) * G["toprak_kgCO2e_kg"])[bos]
        hacim = np.where(M["birim"] == "m2", M["kalinlik_sabit_m"].fillna(0), 1.0)
        M["cimento_TL"] = cp * M["yogunluk_kg_m3"] * hacim * G["cimento_TL_t"] / 1000
        M["malzeme_TL_top"] = M["malzeme_TL"] + M["cimento_TL"]
        u, d = G["usta_TL_sa"] * self.ucret_carpani, G["duz_isci_TL_sa"] * self.ucret_carpani
        M["ucret_TL_sa"] = M["usta_payi"] * u + (1 - M["usta_payi"]) * d
        M["iscilik_TL"] = M["iscilik_sa"] * M["ucret_TL_sa"]
        M["net_TL"] = M["malzeme_TL_top"] + M["iscilik_TL"]
        M["birim_TL"] = M["net_TL"] * (1 + G["genel_gider_kar"])          # %25 genel gider ve kâr dahil
        M["kutle_birim"] = np.select([M["birim"] == "m3", M["birim"] == "m2", M["birim"] == "t"],
                                     [M["yogunluk_kg_m3"], M["yogunluk_kg_m3"] * M["kalinlik_sabit_m"].fillna(0), 1000.0])

    def U_sinir(self, b):
        return self.G[f"U_bolge{b}"]

    # ---------- duvar ----------
    def duvar(self, kod, U_hedef=None, yalitimsiz=False):
        G, M = self.G, self.M
        kat = self.D[self.D.duvar_kod == kod].sort_values("sira").copy()
        Rs = G["Rsi"] + G["Rse"]
        kat["lam"] = kat.malzeme_kod.map(M["lambda_W_mK"])
        sabit_R = (kat.kalinlik_m / kat["lam"])[(kat.degisken == 0) & (kat.u_dahil == 1)].sum()
        if kat.degisken.sum():
            i = kat.index[kat.degisken == 1][0]
            if yalitimsiz:
                kat.loc[i, "kalinlik_m"] = 0.0
            elif U_hedef is not None:
                gerek = 1 / U_hedef - Rs - sabit_R
                kat.loc[i, "kalinlik_m"] = 0.0 if gerek <= 0 else max(0.03, math.ceil(gerek * kat.loc[i, "lam"] * 100 - 1e-9) / 100)
        sonuc = dict(kutle=0.0, karbon=0.0, biyo=0.0, TL=0.0, net_TL=0.0, isc_TL=0.0, isc_sa=0.0, R=Rs, kalinlik=0.0,
                     yalitim_cm=0.0, kappa=0.0)
        omur = {}
        kalan = None
        for _, k in kat.iterrows():
            m = M.loc[k.malzeme_kod]
            t = k.kalinlik_m
            miktar = t if m.birim == "m3" else (1.0 if t > 0 else 0.0)
            kutle = m.yogunluk_kg_m3 * t
            sonuc["kutle"] += kutle
            sonuc["karbon"] += kutle * m.karbon_kgCO2e_kg
            sonuc["biyo"] += kutle * m.biyojenik_kgCO2_kg
            sonuc["TL"] += miktar * m.birim_TL
            sonuc["net_TL"] += miktar * m.net_TL
            sonuc["isc_TL"] += miktar * m.iscilik_TL
            sonuc["isc_sa"] += miktar * m.iscilik_sa
            omur[m.omur_sonu] = omur.get(m.omur_sonu, 0.0) + kutle
            if k.u_dahil == 1:
                sonuc["R"] += t / m.lambda_W_mK
                sonuc["kalinlik"] += t
            if k.degisken == 1:
                sonuc["yalitim_cm"] = t * 100
        # iç yüze bağlı etken ısı kapasitesi (EN ISO 13786 basitleştirmesi: ilk 10 cm, kalınlığın yarısı, ilk yalıtıma kadar)
        derin = min(0.10, sonuc["kalinlik"] / 2)
        for _, k in kat[kat.u_dahil == 1].iterrows():
            m = M.loc[k.malzeme_kod]
            if m.lambda_W_mK <= YALITIM_LAMBDA or derin <= 0:
                break
            dt = min(k.kalinlik_m, derin)
            sonuc["kappa"] += m.yogunluk_kg_m3 * m.ozgul_isi_J_kgK * dt / 1000
            derin -= dt
        sonuc["U"] = 1 / sonuc["R"]
        agir = (kat.malzeme_kod.map(M["yogunluk_kg_m3"]) * kat.kalinlik_m).max()
        sonuc["Rw_dB"] = 28 * math.log10(sonuc["kutle"]) - 20 if agir >= 100 else np.nan   # kütle kuralı (DIN 4109)
        sonuc["omur"] = omur
        sonuc["katmanlar"] = kat
        return sonuc

    def duvar_tablosu(self):
        satir = []
        bilgi = self.D.drop_duplicates("duvar_kod").set_index("duvar_kod")
        for kod, b in bilgi.iterrows():
            Uh = None if b.ic_duvar else self.U_sinir(self.bolge)
            r = self.duvar(kod, U_hedef=Uh)
            r0 = self.duvar(kod, yalitimsiz=True)
            satir.append(dict(
                duvar_kod=kod, kisa_ad=b.kisa_ad, duvar_ad=b.duvar_ad, aile=b.aile, ic_duvar=int(b.ic_duvar),
                yalitim_cm=round(r["yalitim_cm"], 1), kalinlik_cm=round(r["kalinlik"] * 100, 1),
                U_W_m2K=round(r["U"], 3), U_yalin_W_m2K=round(r0["U"], 3),
                U_hedef=np.nan if b.ic_duvar else self.U_sinir(self.bolge),
                hedefi_karsilar=np.nan if b.ic_duvar else int(r["U"] <= self.U_sinir(self.bolge) + 1e-9),
                kutle_kg_m2=round(r["kutle"], 1), karbon_kgCO2e_m2=round(r["karbon"], 1),
                biyojenik_kgCO2_m2=round(r["biyo"], 1), maliyet_TL_m2=round(r["TL"]),
                iscilik_sa_m2=round(r["isc_sa"], 2), iscilik_payi=round(r["isc_TL"] / r["net_TL"], 3),
                kappa_kJ_m2K=round(r["kappa"], 1), Rw_dB_kutle_kurali=round(r["Rw_dB"], 1) if not np.isnan(r["Rw_dB"]) else np.nan,
                tasarim_bolgesi=np.nan if b.ic_duvar else self.bolge))
        return pd.DataFrame(satir)

    def u_bolge_tablosu(self):
        G, M = self.G, self.M
        bilgi = self.D[self.D.ic_duvar == 0].drop_duplicates("duvar_kod").set_index("duvar_kod")
        satir = []
        for kod, b in bilgi.iterrows():
            r0 = self.duvar(kod, yalitimsiz=True)
            s = dict(duvar_kod=kod, kisa_ad=b.kisa_ad, aile=b.aile, U_yalin=round(r0["U"], 3),
                     yalitim_malzemesi=", ".join(r0["katmanlar"].loc[r0["katmanlar"].degisken == 1, "malzeme_kod"]) or "—")
            for bl in range(1, 7):
                Us = self.U_sinir(bl)
                if s["yalitim_malzemesi"] != "—":
                    s[f"b{bl}_yalitim_cm"] = round(self.duvar(kod, U_hedef=Us)["yalitim_cm"], 0)
                else:
                    s[f"b{bl}_yalitim_cm"] = np.nan
                s[f"b{bl}_yalin_karsilar"] = int(r0["U"] <= Us + 1e-9)
            satir.append(s)
        tab = pd.DataFrame(satir)
        # yalnız ana malzemeyle gereken kalınlık (iki yüz 2,5 cm sıva dahil)
        ek = []
        for kod, ad in [("RE_YALIN", "Sıkıştırılmış toprak, stabilizesiz"), ("RE_STAB", "Sıkıştırılmış toprak, %6 çimento"),
                        ("KERPIC", "Kerpiç"), ("TAS", "Yerel taş"), ("HTS", "Hafif toprak-saman"), ("SAMAN", "Saman balya"),
                        ("TUGLA19", "Yatay delikli tuğla"), ("BIMS19", "Bims blok")]:
            lam = M.loc[kod, "lambda_W_mK"]
            Rsiva = 0.025 / M.loc["KIL_SIVA", "lambda_W_mK"] + 0.025 / M.loc["KIREC_SIVA", "lambda_W_mK"]
            s = dict(malzeme_kod=kod, malzeme=ad, lambda_W_mK=lam)
            for bl in range(1, 7):
                s[f"b{bl}_gereken_kalinlik_cm"] = round(max(0.0, (1 / self.U_sinir(bl) - G["Rsi"] - G["Rse"] - Rsiva) * lam) * 100)
            s["U_50cm"] = round(1 / (G["Rsi"] + G["Rse"] + Rsiva + 0.50 / lam), 3)
            ek.append(s)
        return tab, pd.DataFrame(ek)

    # ---------- bina ----------
    def geometri(self, senaryo):
        ns = {k: v for k, v in self.G.items() if isinstance(v, float)}
        for _, r in self.GEO[self.GEO.senaryo == senaryo].iterrows():
            ns[r.anahtar] = float(eval(str(r.ifade), {"__builtins__": {}}, ns))
        return ns

    def bina(self, senaryo, sistem):
        ns = self.geometri(senaryo)
        E = self.E[(self.E.senaryo == senaryo) & (self.E.sistem == sistem)]
        satir = []
        Uh = self.U_sinir(self.bolge)
        for _, e in E.iterrows():
            q = float(eval(str(e.miktar), {"__builtins__": {}}, ns))
            if e.tur == "malzeme":
                m = self.M.loc[e.kod]
                kutle = q * m.kutle_birim
                d = dict(kutle=kutle, karbon=kutle * m.karbon_kgCO2e_kg, biyo=kutle * m.biyojenik_kgCO2_kg,
                         TL=q * m.birim_TL, net_TL=q * m.net_TL, isc_TL=q * m.iscilik_TL, isc_sa=q * m.iscilik_sa,
                         omur={m.omur_sonu: kutle}, U=np.nan)
            else:
                ic = e.kod.startswith("I")
                w = self.duvar(e.kod, U_hedef=None if ic else Uh)
                d = dict(kutle=q * w["kutle"], karbon=q * w["karbon"], biyo=q * w["biyo"], TL=q * w["TL"],
                         net_TL=q * w["net_TL"], isc_TL=q * w["isc_TL"], isc_sa=q * w["isc_sa"],
                         omur={k: v * q for k, v in w["omur"].items()}, U=np.nan if ic else w["U"])
            d.update(senaryo=senaryo, sistem=sistem, eleman=e.eleman, tur=e.tur, kod=e.kod, miktar=q, birim=e.birim,
                     deprem_kutlesi=float(e.deprem_kutlesi))
            satir.append(d)
        return pd.DataFrame(satir), ns, E.iloc[0]

    def bina_tablosu(self):
        ozet, dokum = [], []
        for senaryo in self.E.senaryo.unique():
            ref_TL = None
            for sistem in self.E[self.E.senaryo == senaryo].sistem.unique():
                df, ns, bilgi = self.bina(senaryo, sistem)
                A = ns["A_BRUT"]
                if sistem == "R0":
                    ref_TL = df.TL.sum()
                omur = {}
                for o in df.omur:
                    for k, v in o.items():
                        omur[k] = omur.get(k, 0) + v
                top_kutle = df.kutle.sum()
                TL_bina = ns["BM"] * A - ref_TL + df.TL.sum()
                s = dict(senaryo=senaryo, sistem=sistem, kisa_ad=bilgi.kisa_ad, sistem_ad=bilgi.sistem_ad, aile=bilgi.aile,
                         A_brut_m2=A, dis_duvar_m2=round(ns["DIS_DUVAR"], 1),
                         maliyet_degisen_TL=round(df.TL.sum()), maliyet_bina_TL=round(TL_bina),
                         TL_m2_bina=round(TL_bina / A), fark_TL_m2_R0=round((df.TL.sum() - ref_TL) / A),
                         fark_yuzde_R0=round((df.TL.sum() - ref_TL) / (ns["BM"] * A) * 100, 1),
                         karbon_degisen_t=round(df.karbon.sum() / 1000, 2),
                         kgCO2e_m2_degisen=round(df.karbon.sum() / A, 1),
                         kgCO2e_m2_toplam=round(df.karbon.sum() / A + self.G["ortak_karbon_kgCO2e_m2"], 1),
                         biyojenik_depo_kgCO2_m2=round(df.biyo.sum() / A, 1),
                         iscilik_sa_m2=round(df.isc_sa.sum() / A, 2),
                         iscilik_payi_degisen=round(df.isc_TL.sum() / df.net_TL.sum(), 3),
                         kisi_yil_1000_bina=round(df.isc_sa.sum() * 1000 / self.G["calisma_sa_yil"]),
                         kutle_t_m2=round(top_kutle / 1000 / A, 2),
                         U_dis_duvar=round(df.U.dropna().iloc[0], 3))
                for k in ["dogaya_doner", "yeniden_kullanim", "geri_donusum", "asagi_donusum", "biyolojik", "depolama"]:
                    s[f"omur_{k}_pay"] = round(omur.get(k, 0) / top_kutle, 3)
                ozet.append(s)
                dokum.append(df.drop(columns=["omur"]))
        oz = pd.DataFrame(ozet)
        for senaryo in oz.senaryo.unique():
            i = oz.senaryo == senaryo
            r0 = oz.loc[i & (oz.sistem == "R0"), "kgCO2e_m2_degisen"].iloc[0]
            oz.loc[i, "karbon_fark_yuzde_R0"] = ((oz.loc[i, "kgCO2e_m2_degisen"] - r0) / r0 * 100).round(1)
        return oz, pd.concat(dokum, ignore_index=True)

    # ---------- enerji ----------
    def enerji_tablosu(self, oz):
        G = self.G
        satir = []
        for _, r in oz.iterrows():
            for bl in (3, 4):
                Q = r.U_dis_duvar * r.dis_duvar_m2 * G[f"HDD_bolge{bl}"] * 24 / 1000
                yakit = Q / G["kazan_verimi"]
                satir.append(dict(senaryo=r.senaryo, sistem=r.sistem, kisa_ad=r.kisa_ad, bolge=bl, U_dis_duvar=r.U_dis_duvar,
                                  duvar_isi_kaybi_kWh_yil=round(Q), duvar_kWh_m2_bina_yil=round(Q / r.A_brut_m2, 1),
                                  yakit_TL_yil=round(yakit * G["enerji_TL_kWh"]),
                                  isletme_CO2_t_50yil=round(yakit * G["dogalgaz_kgCO2_kWh"] * G["omur_yil"] / 1000, 1),
                                  gomulu_degisen_t=r.karbon_degisen_t))
        en = pd.DataFrame(satir)
        for (s, bl), g in en.groupby(["senaryo", "bolge"]):
            ref = g.loc[g.sistem == "R0"].iloc[0]
            i = g.index
            en.loc[i, "isletme_fark_t_50yil_R0"] = (g.isletme_CO2_t_50yil - ref.isletme_CO2_t_50yil).round(1)
            en.loc[i, "gomulu_fark_t_R0"] = (g.gomulu_degisen_t - ref.gomulu_degisen_t).round(1)
        return en

    # ---------- deprem ----------
    def deprem_tablosu(self):
        G = self.G
        satir = []
        sistemler = [("R0", None), ("T1", None), ("T1", (2.5, 1.5)), ("T2", None), ("A1", None), ("H1", None)]
        for sistem, RD in sistemler:
            df, ns, b = self.bina("EV120", sistem)
            A = ns["A_BRUT"]
            W = (df.kutle * df.deprem_kutlesi).sum() * 9.81 / 1000 + \
                (G["ortak_olu_yuk_kN_m2"] + G["hareketli_katilim"] * G["hareketli_yuk_kN_m2"]) * A
            R, D = (float(b.deprem_R), float(b.deprem_D)) if RD is None else RD
            ad = b.kisa_ad if RD is None else "T1 aynı duvar, donatısız kabul (R = 2,5)"
            H = ns["KAT"] * ns["KAT_H"]
            for sds in (0.30, 0.50, 0.75, 1.00, 1.25):
                V, T, Ra = self.taban_kesme(W, R, D, b.Ct, H, sds)
                dts = 4 if sds < 0.33 else 3 if sds < 0.50 else 2 if sds < 0.75 else 1
                tau = V / G["duvar_plan_alani_EV120_m2"] / 1000 if b.aile == "toprak" and sistem.startswith("T") else np.nan
                satir.append(dict(sistem=sistem if RD is None else "T1_donatisiz", kisa_ad=ad, R=R, D=D, T_s=round(T, 3),
                                  Ra=round(Ra, 2), W_kN=round(W), W_kN_m2=round(W / A, 2), S_DS=sds, DTS_BKS3=dts,
                                  V_kN=round(V), V_kN_m2=round(V / A, 2), V_W=round(V / W, 3),
                                  ort_kayma_gerilmesi_MPa=round(tau, 3) if not np.isnan(tau) else np.nan))
        dp = pd.DataFrame(satir)
        ref = dp[dp.sistem == "R0"].set_index("S_DS").V_kN
        dp["V_oran_R0"] = (dp.V_kN / dp.S_DS.map(ref)).round(2)
        return dp

    # ---------- kubbe ----------
    def kubbe_tablosu(self):
        M = self.M
        satir = []
        for _, k in self.K.iterrows():
            r = k.aciklik_m / 2
            if k.geometri == "kubbe":
                ortu, yuzey, halka_boy = math.pi * r ** 2, 2 * math.pi * r ** 2, math.pi * k.aciklik_m
            else:   # tonoz: 1 m boy başına, yarım daire kesit
                ortu, yuzey, halka_boy = k.aciklik_m * 1.0, math.pi * r * 1.0, 0.0
            m = M.loc[k.malzeme_kod]
            hacim = yuzey * k.kalinlik_m
            kutle = hacim * m.yogunluk_kg_m3
            karbon = kutle * m.karbon_kgCO2e_kg
            TL = hacim * m.birim_TL
            sa = hacim * m.iscilik_sa
            don_t = hacim * k.donati_kg_m3 / 1000
            karbon += don_t * 1000 * M.loc["DONATI", "karbon_kgCO2e_kg"]
            TL += don_t * M.loc["DONATI", "birim_TL"]
            sa += don_t * M.loc["DONATI", "iscilik_sa"]
            if k.kalip_carpani > 0:
                TL += yuzey * k.kalip_carpani * M.loc["KALIP", "birim_TL"]
                sa += yuzey * k.kalip_carpani * M.loc["KALIP", "iscilik_sa"]
                karbon += yuzey * k.kalip_carpani * M.loc["KALIP", "kutle_birim"] * M.loc["KALIP", "karbon_kgCO2e_kg"]
            if isinstance(k.kaplama_kod, str):
                mk = M.loc[k.kaplama_kod]
                TL += yuzey * mk.birim_TL
                sa += yuzey * mk.iscilik_sa
                karbon += yuzey * mk.kutle_birim * mk.karbon_kgCO2e_kg
                kutle += yuzey * mk.kutle_birim
            if k.cekme_halkasi:
                hv = halka_boy * 0.4 * 0.5
                hd = hv * 0.130
                b = M.loc["BET_DK"]
                kutle += hv * b.yogunluk_kg_m3
                karbon += hv * b.yogunluk_kg_m3 * b.karbon_kgCO2e_kg + hd * 1000 * M.loc["DONATI", "karbon_kgCO2e_kg"]
                TL += hv * b.birim_TL + hd * M.loc["DONATI", "birim_TL"] + halka_boy * 1.4 * M.loc["KALIP", "birim_TL"]
                sa += hv * b.iscilik_sa + hd * M.loc["DONATI", "iscilik_sa"] + halka_boy * 1.4 * M.loc["KALIP", "iscilik_sa"]
            # kabuğun yapı fiziği (kabuk yüzeyi m² başına): U (ısı akışı yukarı, Rsi 0,10), iç yüze bağlı ısı kapasitesi, ses
            R = 0.10 + self.G["Rse"] + k.kalinlik_m / m.lambda_W_mK
            m_yuzey = k.kalinlik_m * m.yogunluk_kg_m3
            if isinstance(k.kaplama_kod, str):
                mk = M.loc[k.kaplama_kod]
                R += mk.kalinlik_sabit_m / mk.lambda_W_mK
                m_yuzey += mk.kutle_birim
            kappa = m.yogunluk_kg_m3 * m.ozgul_isi_J_kgK * min(0.10, k.kalinlik_m / 2) / 1000
            satir.append(dict(kod=k.kod, ad=k.ad, aciklik_m=k.aciklik_m, kalinlik_m=k.kalinlik_m, ortulen_m2=round(ortu, 1),
                              kutle_t_m2=round(kutle / 1000 / ortu, 2), kutle_kN_m2=round(kutle * 9.81 / 1000 / ortu, 1),
                              karbon_kgCO2e_m2=round(karbon / ortu, 1),
                              maliyet_TL_m2=round(TL / ortu), iscilik_sa_m2=round(sa / ortu, 1),
                              hizmet_omru_yil=k.hizmet_omru_yil,
                              karbon_kgCO2e_m2_yil=round(karbon / ortu / k.hizmet_omru_yil, 2),
                              U_kabuk_W_m2K=round(1 / R, 2), kappa_kJ_m2K=round(kappa, 1),
                              Rw_dB_kutle_kurali=round(28 * math.log10(m_yuzey) - 20, 1),
                              pratik_en_buyuk_aciklik=k.pratik_en_buyuk_aciklik, deprem_notu=k.deprem_notu))
        return pd.DataFrame(satir)

    # ---------- tek katlı kubbeli ev: örtünün deprem talebine etkisi ----------
    def taban_kesme(self, W, R, D, Ct, H, sds, I=1.0):
        """TBDY 2018 eşdeğer deprem yükü: V = W · S_ae(T) / R_a(T); V ≥ 0,04 · W · I · S_DS."""
        T = self.G[Ct] * H ** 0.75
        TB = self.G["T_B_s"]
        TA = 0.2 * TB
        spek = 0.4 + 0.6 * T / TA if T < TA else (1.0 if T <= TB else TB / T)
        Ra = D + (R / I - D) * T / TB if T <= TB else R / I
        return max(W * sds * spek / Ra, 0.04 * W * I * sds), T, Ra

    def kubbeli_ev_tablosu(self, kb):
        """120 m² tek katlı ev: toprak duvar + toprak kubbe/tonoz, toprak duvar + hafif çatı, betonarme referans."""
        G = self.G
        A, H = G["kev_A"], G["kev_duvar_h"]
        dis = G["kev_dis_cevre"] * H * (1 - G["kev_bosluk_dis"])
        ic = G["kev_ic_duvar_boy"] * H * (1 - G["kev_bosluk_ic"])
        k = kb.set_index("kod")
        secenek = [
            ("KE1", "Toprak duvar 50 cm + superadobe kubbeler (5 m)", "W06", "I05", k.loc["K3", "kutle_kN_m2"], 2.5, 1.5,
             "Ct_diger", "donatısız toprak kubbe: E22 donatısız yığma katsayıları ödünç"),
            ("KE2", "Toprak duvar 50 cm + Nubian tonozları (kerpiç, 3,25 m)", "W06", "I05", k.loc["K4", "kutle_kN_m2"],
             2.5, 1.5, "Ct_diger", "donatısız kerpiç tonoz: E22 katsayıları ödünç"),
            ("KE3", "Donatılı toprak duvar 50 cm + hafif ahşap çatı", "W06", "I05", G["hafif_cati_kN_m2"], 4.0, 2.0,
             "Ct_diger", "donatılı toprak duvar: E11 donatılı yığma katsayıları ödünç"),
            ("KE4", "Betonarme tek katlı + tuğla + EPS + betonarme çatı (referans)", "W01", "I01", G["betonarme_cati_kN_m2"],
             8.0, 3.0, "Ct_betonarme", "TBDY A11 (R 8, D 3)"),
        ]
        satir = []
        for kod, ad, wd, wi, ortu_kN, R, D, Ct, nt in secenek:
            m_dis = self.duvar(wd, U_hedef=self.U_sinir(self.bolge))["kutle"]
            m_ic = self.duvar(wi)["kutle"]
            duvar_kN = 0.5 * (dis * m_dis + ic * m_ic) * 9.81 / 1000     # tek katta duvarların üst yarısı
            W = A * (ortu_kN + G["kev_ortak_kN_m2"]) + duvar_kN
            for sds in (0.30, 0.50, 0.75, 1.00):
                V, T, Ra = self.taban_kesme(W, R, D, Ct, H, sds)
                tau = V / G["kev_duvar_plan_alani_m2"] / 1000 if kod != "KE4" else np.nan
                satir.append(dict(kod=kod, ad=ad, ortu_kN_m2=round(ortu_kN, 1), duvar_kN=round(duvar_kN), W_kN=round(W),
                                  W_kN_m2=round(W / A, 1), ortu_payi=round(A * ortu_kN / W, 2), R=R, D=D, T_s=round(T, 3),
                                  Ra=round(Ra, 2), S_DS=sds, V_kN=round(V), V_kN_m2=round(V / A, 2),
                                  ort_kayma_gerilmesi_MPa=round(tau, 3) if not np.isnan(tau) else np.nan, not_=nt))
        df = pd.DataFrame(satir).rename(columns={"not_": "not"})
        ref = df[df.kod == "KE4"].set_index("S_DS").V_kN
        df["V_oran_KE4"] = (df.V_kN / df.S_DS.map(ref)).round(1)
        return df

    # ---------- enkaz ----------
    def enkaz_tablosu(self):
        G = self.G
        kap = G["hatay_tesis_t_gun"] * G["tesis_gun_yil"] / 1e6
        enk = G["enkaz_calisma_Mt"]
        agrega = enk * G["mineral_pay"] * G["agrega_verim"]
        beton = G["yeniden_yapim_konut"] * G["konut_m2"] * G["beton_m3_m2"] / 1e6
        talep = beton * G["agrega_t_m3"]
        yapisal = talep * G["iri_agrega_pay"] * G["gba_ikame"]
        s = [
            ("Enkaz (UNDP çalışma değeri)", enk, "Mt", "girdi", "İ"),
            ("Enkaz aralığı (UNDP ilk tahmin)", f"{G['enkaz_alt_Mt']:.0f}–{G['enkaz_ust_Mt']:.0f}", "Mt", "girdi", "İ"),
            ("Bir Hatay ölçekli tesisin yıllık kapasitesi", round(kap, 2), "Mt/yıl", "4.000 t/gün × 300 gün", "H"),
            ("Tek tesisle bütün enkazın işlenme süresi", round(enk / kap), "yıl", "enkaz / kapasite", "H"),
            (f"{G['hedef_yil']:.0f} yılda işlemek için gereken tesis sayısı", round(enk / (G['hedef_yil'] * kap)), "tesis",
             "enkaz / (hedef yıl × kapasite)", "H"),
            ("Sınıflandırılmış agrega potansiyeli", round(agrega), "Mt", "enkaz × mineral payı × verim", "H"),
            ("Yeniden yapımın beton hacmi", round(beton, 1), "milyon m³", "konut × m² × m³/m²", "H"),
            ("Bu betonun agrega ihtiyacı", round(talep, 1), "Mt", "beton × 1,85 t/m³", "H"),
            ("Yapısal betonda kullanılabilecek geri dönüştürülmüş iri agrega", round(yapisal, 1), "Mt",
             "talep × iri agrega payı × ikame sınırı", "H"),
            ("Yapısal betonun emebileceği enkaz payı", round(yapisal / enk * 100, 1), "%", "yapısal kullanım / enkaz", "H"),
            ("Agrega potansiyelinin yol, dolgu ve blok üretimine kalan kısmı", round(agrega - yapisal), "Mt",
             "agrega potansiyeli − yapısal kullanım", "H"),
        ]
        return pd.DataFrame(s, columns=["gosterge", "deger", "birim", "hesap", "etiket"])


def duyarlilik():
    toprak = ["RE_STAB", "RE_YALIN"]
    durumlar = [
        ("Taban", {}),
        ("Toprak duvar işçiliği 6 sa/m³ (makineli ekip)", {"M": {(k, "iscilik_sa"): 6 for k in toprak}}),
        ("Toprak duvar işçiliği 16 sa/m³ (el tokmağı)", {"M": {(k, "iscilik_sa"): 16 for k in toprak}}),
        ("Öz-yapım: toprak ve saman işlerinde işçiliğin yarısı hanece", {"iscilik_carpani": {k: 0.5 for k in TOPRAK_SAMAN}}),
        ("Bütün ücretler +%30", {"ucret_carpani": 1.3}),
        ("Stabilizasyon %4 çimento (CEB %5)", {"M": {("RE_STAB", "cimento_payi"): 0.04, ("CEB14", "cimento_payi"): 0.05}}),
        ("Stabilizasyon %8 çimento (CEB %9)", {"M": {("RE_STAB", "cimento_payi"): 0.08, ("CEB14", "cimento_payi"): 0.09}}),
        ("Donatı karbonu 0,45 (hurdadan ark ocağı)", {"M": {("DONATI", "karbon_kgCO2e_kg"): 0.45}}),
        ("Donatı karbonu 1,99 (ICE v3 dünya ortalaması)", {"M": {("DONATI", "karbon_kgCO2e_kg"): 1.99}}),
        ("Beton karbonu C25/30 0,11 (ICE v3 alt)", {"M": {("BET_C25", "karbon_kgCO2e_kg"): 0.11}}),
        ("CLT ve glulam fiyatı −%30", {"M": {("CLT", "malzeme_TL"): 36000 * 0.7, ("GLULAM", "malzeme_TL"): 34000 * 0.7}}),
        ("CLT ve glulam fiyatı +%30", {"M": {("CLT", "malzeme_TL"): 36000 * 1.3, ("GLULAM", "malzeme_TL"): 34000 * 1.3}}),
        ("Tasarım bölgesi 4 (U ≤ 0,35)", {"G": {"tasarim_bolgesi": 4.0}}),
        ("Tasarım bölgesi 5 (U ≤ 0,25)", {"G": {"tasarim_bolgesi": 5.0}}),
    ]
    satir = []
    for ad, ayar in durumlar:
        oz, _ = Model(ayar).bina_tablosu()
        for _, r in oz[oz.sistem != "T0"].iterrows():
            satir.append(dict(durum=ad, senaryo=r.senaryo, sistem=r.sistem, TL_m2_bina=r.TL_m2_bina,
                              maliyet_fark_yuzde_R0=r.fark_yuzde_R0, kgCO2e_m2_degisen=r.kgCO2e_m2_degisen,
                              karbon_fark_yuzde_R0=r.karbon_fark_yuzde_R0, iscilik_payi=r.iscilik_payi_degisen))
    return pd.DataFrame(satir)


def main():
    m = Model()
    duv = m.duvar_tablosu()
    ub, ub_ek = m.u_bolge_tablosu()
    oz, dok = m.bina_tablosu()
    en = m.enerji_tablosu(oz)
    dp = m.deprem_tablosu()
    kb = m.kubbe_tablosu()
    ke = m.kubbeli_ev_tablosu(kb)
    ek = m.enkaz_tablosu()
    dy = duyarlilik()
    duv.to_csv(KLASOR / "sonuc_duvar_sistemleri.csv", index=False, encoding="utf-8")
    ub.to_csv(KLASOR / "sonuc_u_bolge.csv", index=False, encoding="utf-8")
    ub_ek.to_csv(KLASOR / "sonuc_u_yalniz_malzeme.csv", index=False, encoding="utf-8")
    oz.to_csv(KLASOR / "sonuc_bina_senaryolari.csv", index=False, encoding="utf-8")
    dok.round(3).to_csv(KLASOR / "sonuc_bina_elemanlari.csv", index=False, encoding="utf-8")
    en.to_csv(KLASOR / "sonuc_enerji.csv", index=False, encoding="utf-8")
    dp.to_csv(KLASOR / "sonuc_deprem_talebi.csv", index=False, encoding="utf-8")
    kb.to_csv(KLASOR / "sonuc_kubbe.csv", index=False, encoding="utf-8")
    ke.to_csv(KLASOR / "sonuc_kubbeli_ev.csv", index=False, encoding="utf-8")
    ek.to_csv(KLASOR / "sonuc_enkaz.csv", index=False, encoding="utf-8")
    dy.to_csv(KLASOR / "sonuc_duyarlilik.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 250, "display.max_columns", 30)
    print(duv[["duvar_kod", "kisa_ad", "yalitim_cm", "U_W_m2K", "U_yalin_W_m2K", "kutle_kg_m2", "karbon_kgCO2e_m2",
               "biyojenik_kgCO2_m2", "maliyet_TL_m2", "iscilik_sa_m2", "iscilik_payi", "kappa_kJ_m2K", "Rw_dB_kutle_kurali"]])
    print(oz[["senaryo", "sistem", "TL_m2_bina", "fark_yuzde_R0", "kgCO2e_m2_degisen", "karbon_fark_yuzde_R0",
              "biyojenik_depo_kgCO2_m2", "iscilik_sa_m2", "iscilik_payi_degisen", "kisi_yil_1000_bina", "kutle_t_m2", "U_dis_duvar"]])
    print(ub_ek)
    print(en[en.senaryo == "EV120"])
    print(dp[dp.S_DS.isin([0.5, 1.0])])
    print(kb.drop(columns=["deprem_notu", "ad"]))
    print(ke[ke.S_DS.isin([0.5, 1.0])].drop(columns=["not"]))
    print(ek)
    print(dy[(dy.senaryo == "EV120") & dy.sistem.isin(["T1", "T2", "A1", "H1"])].pivot(index="durum", columns="sistem",
                                                                                     values="maliyet_fark_yuzde_R0"))


if __name__ == "__main__":
    main()
