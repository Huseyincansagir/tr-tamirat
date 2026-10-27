"""
TR TAMİRAT — İP7 Zihinsel simülasyonlar: 30 yıllık yaşam döngüsü (sürüm 0.1, 26 Ekim 2026)
=========================================================================================
Genç bir çiftin (persona P2: Zeynep 26, öğretmen; Mert 28, merkezde satış) evlilikten
itibaren 30 yılı dört yolda izlenir:

  A       Megakent kapalı site (çeperde, araca bağımlı; aile 18 km uzakta)
  B       Eski yap-sat apartman mahallesi (aile 4 km'de; bina 30 yılda 6306'ya göre dönüşebilir)
  C       Model mahalle, piyasa fiyatıyla (aile aynı mahallede; ebeveyn bakımında çok kuşaklı T2 ev)
  C-koop  Model mahalle, kooperatif / maliyetine konut (fiyat piyasanın ≈%70'i, teslim 3 yıl sonra)

Olaylar: t=0 evlilik ve 2+1 kirada · t=2 ilk çocuk · t=3 3+1'e geçiş · t=5 ikinci çocuk (olasılık)
· peşinat birikince ev alımı · t≈19'dan itibaren ebeveyn bakımı.
Bütün tutarlar 2026 fiyatlarıyla reel TL'dir. Parametreler persona_simulasyonu.VARSAYIMLAR'da
(06_SIMULASYON/varsayimlar.csv, "Y_" önekli satırlar ve ortak fiyat satırları).

Doğurganlık etkisi Faz 2 ilçe bulgusuyla sınırlıdır: eğitim sabitken 3 m (≈1 kat) başına
−0,029 çocuk; etki yalnız verinin desteklediği yükseklik aralığında (≤15 m) uygulanır ve
akraba yakınlığı kanalı küçük tutulur. Sonuç bir öngörü değil, sınır hesabıdır.

Çalıştırma :  python yasam_dongusu.py   (ya da persona_simulasyonu.py üzerinden)
Çıktılar   :  ../sonuclar/yasam_dongusu_ozet.csv, ../sonuclar/yasam_dongusu_yillik.csv,
              ../grafikler/yasam_dongusu.png|svg
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict

sys.dont_write_bytecode = True   # kod klasörüne __pycache__ yazılmasın

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import persona_simulasyonu as ps
from persona_simulasyonu import Prm, ornekle, gun_simule, KISI, SONUC, TOHUM, tr, sade, kaydet, tr_eksen

N_MC = 3000
YIL = 30
IS_GUNU_YIL = 225
YOLLAR = ["A", "B", "C", "C-koop"]
YOL_AD = {"A": "A · Kapalı site", "B": "B · Yap-sat apartman", "C": "C · Model mahalle (piyasa)", "C-koop": "C · Model mahalle (kooperatif)",
          "A-tek-araç": "A · Kapalı site, tek araçla (duyarlılık)"}
RENK = {"A": ps.MAVI, "B": ps.TURUNCU, "C": ps.AQUA, "C-koop": ps.SARI}


def ebeveyne_sure_dk(ortam, prm):
    """Ebeveyn evine tek yön yolculuk (dk): 1,5 km'ye kadar yürüme, ötesi araç."""
    km = prm("Y_EBEVEYN_MESAFE_KM", ortam)
    if km <= 1.5:
        return km * 1000 / prm("HIZ_YETISKIN")
    return km / prm("ARAC_HIZ_YEREL") * 60 + 5


def destek_uygulanabilirligi(ortam, prm):
    """Günlük büyükanne desteğinin uygulanabilirliği: ≤10 dk tam (1), Y_DESTEK_SIFIR_DK'da 0."""
    t = ebeveyne_sure_dk(ortam, prm)
    sifir = prm("Y_DESTEK_SIFIR_DK")
    return float(np.clip((sifir - t) / (sifir - 10), 0, 1))


def dogurganlik_farki(ortam, prm):
    """A'ya göre beklenen ek çocuk: Faz 2 yükseklik kanalı + küçük akraba kanalı, tavanla sınırlı."""
    ust = prm("Y_YUKSEKLIK_UST_M")
    h_a = min(prm("Y_YASANAN_YUKSEKLIK", "A"), ust)
    h_o = min(prm("Y_YASANAN_YUKSEKLIK", ortam), ust)
    yukseklik = prm("Y_FAZ2_KAT") * (h_a - h_o) / 3
    akraba = prm("Y_AKRABA_COCUK_MAKS") * (destek_uygulanabilirligi(ortam, prm) - destek_uygulanabilirligi("A", prm))
    tavan = prm("Y_DOGURGANLIK_TAVAN")
    return float(np.clip(yukseklik + akraba, -tavan, tavan)), yukseklik, akraba


def annuite(anapara, r, n):
    if r == 0:
        return anapara / n
    return anapara * r / (1 - (1 + r) ** -n)


def yasam_simule(yol: str, prm: Prm, rng: np.random.Generator, a_tek_arac: bool = False):
    o = "C" if yol == "C-koop" else yol
    # Günlük işe gidiş (persona motorundan): Zeynep semtte toplu taşıma, Mert merkezde (A'da araç)
    gz = gun_simule(KISI["P2a"], o, prm)
    gm = gun_simule(KISI["P2b"], o, prm)
    z_tek, m_tek = gz["is_tek_yon_dk"], gm["is_tek_yon_dk"]
    m_arac_km_gun = gm["arac_km"]

    au = prm("AU_NET")
    g = prm("Y_REEL_GELIR_ARTIS")
    h = prm("Y_REEL_KONUT_ARTIS")
    f_sup = destek_uygulanabilirligi(o, prm)
    istihdam = float(np.clip(prm("Y_ANNE_ISTIHDAM_TABAN") + prm("Y_CP_ETKI") * f_sup, 0, 1))
    d_cocuk, d_yuk, d_akr = dogurganlik_farki(o, prm)
    p2 = float(np.clip(prm("Y_COCUK2_P_A") + d_cocuk, 0, 1))
    bakim_bas = prm("Y_EBEVEYN_BAKIM_BASLANGIC")
    km_deg = prm("YAKIT_TL_L") * prm("YAKIT_L_100KM") / 100 + prm("ARAC_ASINMA_TL_KM")

    # B: 6306 dönüşümü
    donusum = (yol == "B") and (rng.random() < prm("Y_B_DONUSUM_P"))
    d_yil, d_sure = prm("Y_B_DONUSUM_YIL"), prm("Y_B_DONUSUM_SURE")

    birikim = prm("Y_AILE_YARDIMI")
    sahip, alim_yili, tasinma_yili = False, np.nan, np.nan
    kredi, taksit, deger, kalan_vade = 0.0, 0.0, 0.0, 0
    aidat_m2 = prm("AIDAT_M2", o)
    donusum_uygulandi = False
    kayit = []
    kum_konut = kum_ulasim = kum_yol_saat = kum_bakim_yol_saat = kum_buyukanne_saat = 0.0

    for t in range(YIL):
        cocuk_kucuk = 2 <= t < 12
        anne_calisma = istihdam if cocuk_kucuk else 1.0
        gelir = 12 * au * (1 + g) ** t * (prm("Y_GELIR_ZEYNEP_AU") * anne_calisma + prm("Y_GELIR_MERT_AU"))
        n_cocuk = (1.0 if 2 <= t < 24 else 0.0) + (p2 if 5 <= t < 27 else 0.0)
        m2 = prm("Y_M2_ILK") if t < 3 else prm("Y_M2_AILE")
        fiyat_m2 = prm("KONUT_FIYAT_M2", o) * (1 + h) ** t * (prm("Y_KOOP_ORAN") if yol == "C-koop" else 1.0)

        # --- Ev alımı (yıl başında) ---
        if not sahip and 1 <= t <= 25:
            fiyat = fiyat_m2 * prm("Y_M2_AILE")
            gerek = fiyat * (prm("Y_PESINAT") + prm("Y_MASRAF"))
            if birikim >= gerek:
                birikim -= gerek
                kredi = fiyat * (1 - prm("Y_PESINAT"))
                taksit = annuite(kredi, prm("Y_REEL_FAIZ"), int(prm("Y_VADE")))
                kalan_vade = int(prm("Y_VADE"))
                deger = fiyat / (prm("Y_KOOP_ORAN") if yol == "C-koop" else 1.0)   # kooperatif konutun piyasa değeri
                sahip, alim_yili = True, t
                tasinma_yili = t + (round(prm("Y_KOOP_TESLIM")) if yol == "C-koop" else 0)

        # --- Konut gideri ---
        kira_yil = m2 * prm("KIRA_M2", o) * 12 * (1 + h) ** t
        evde = sahip and t >= tasinma_yili
        sahipken_donusum = donusum and sahip and alim_yili <= d_yil      # kiracıysa başka kiralık eve geçer, gider değişmez
        disarida = sahipken_donusum and d_yil <= t < d_yil + d_sure
        if sahipken_donusum and t >= d_yil + d_sure and not donusum_uygulandi:
            aidat_m2 = prm("Y_B_DONUSUM_AIDAT_M2")
            deger *= 1 + prm("Y_B_DONUSUM_DEGER")
            donusum_uygulandi = True
        konut = 0.0
        if sahip and kalan_vade > 0:
            faiz = kredi * prm("Y_REEL_FAIZ")
            konut += taksit
            kredi = max(0.0, kredi + faiz - taksit)
            kalan_vade -= 1
        if evde and not disarida:
            konut += m2 * aidat_m2 * 12 + deger * prm("Y_BAKIM_ORANI")
        else:
            kira = kira_yil * ((1 - prm("Y_KIRA_YARDIMI")) if disarida else 1.0)
            konut += kira + m2 * prm("AIDAT_M2", o) * 12 * (0 if disarida else 1)
        if sahip:
            deger *= 1 + h

        # --- Ulaşım gideri ---
        arac = prm("Y_ARAC_ILK", o) if t < 3 else prm("Y_ARAC_AILE", o)
        if a_tek_arac and o == "A":
            arac = min(arac, 1)
        km = 0.0
        if o == "A":
            km += m_arac_km_gun * IS_GUNU_YIL
        if arac >= 1:
            km += prm("HAFTASONU_ARAC_KM_AY", o) * 12
        if arac >= 2:
            km += prm("Y_IKINCI_ARAC_KM")
        ulasim = arac * (prm("ARAC_SABIT_TL_AY") + prm("OTOPARK_EV_TL_AY", o)) * 12 + km * km_deg
        if o == "A":
            ulasim += IS_GUNU_YIL * prm("MERKEZ_OTOPARK_TL_GUN")
        else:
            ulasim += 12 * prm("MAVI_KART_TL_AY")                         # Mert
        ulasim += 12 * prm("MAVI_KART_TL_AY") * anne_calisma                # Zeynep
        if o == "A":                                                        # okul servisi, 6-14 yaş
            servisli = (1.0 if 8 <= t < 17 else 0.0) + (p2 if 11 <= t < 20 else 0.0)
            ulasim += servisli * prm("OKUL_SERVISI_TL_AY") * 10
        if arac == 0 and o == "C" and t >= 3:
            ulasim += 12 * prm("PAYLASIMLI_ARAC_TL_AY")

        diger = gelir * (prm("Y_DIGER_TUKETIM") + prm("Y_COCUK_TUKETIM") * n_cocuk)
        birikim += gelir - diger - konut - ulasim

        # --- Zaman ---
        yol_saat = IS_GUNU_YIL * 2 * (z_tek * anne_calisma + m_tek) / 60
        bakim_yol = 0.0
        if t >= bakim_bas and not (o == "C"):                               # C'de ebeveyn T2 zemin dairesine taşınır
            bakim_yol = prm("Y_BAKIM_ZIYARET_HAFTA") * 52 * 2 * ebeveyne_sure_dk(o, prm) / 60
        buyukanne = prm("Y_BUYUKANNE_BAKIM_SAAT") * f_sup * 52 if cocuk_kucuk else 0.0

        kum_konut += konut
        kum_ulasim += ulasim
        kum_yol_saat += yol_saat
        kum_bakim_yol_saat += bakim_yol
        kum_buyukanne_saat += buyukanne
        net_konut = (deger - kredi) if sahip else 0.0
        mesafe = 0.0 if (o == "C" and t >= bakim_bas) else prm("Y_EBEVEYN_MESAFE_KM", o)
        kayit.append(dict(t=t, yil=2026 + t, gelir=gelir, konut=konut, ulasim=ulasim, kum_konut_ulasim=kum_konut + kum_ulasim,
                          birikim=birikim, net_konut=net_konut, net_varlik=birikim + net_konut, sahip=int(evde),
                          kusak_mesafe_km=mesafe, yol_saat=yol_saat + bakim_yol))

    ozet = dict(
        kum_konut=kum_konut, kum_ulasim=kum_ulasim, kum_konut_ulasim=kum_konut + kum_ulasim,
        alim_yili=alim_yili, tasinma_yili=tasinma_yili, net_konut_30=kayit[-1]["net_konut"], net_varlik_30=kayit[-1]["net_varlik"],
        ev_sahibi_yil=sum(r["sahip"] for r in kayit),
        isegidis_saat_30=kum_yol_saat, bakim_yolu_saat_30=kum_bakim_yol_saat, yolda_toplam_saat_30=kum_yol_saat + kum_bakim_yol_saat,
        buyukanne_bakim_saat=kum_buyukanne_saat, anne_istihdam_olasiligi=istihdam, destek_uygulanabilirligi=f_sup,
        ebeveyn_mesafe_km=prm("Y_EBEVEYN_MESAFE_KM", o), ebeveyn_sure_dk=ebeveyne_sure_dk(o, prm),
        cocuk_farki=d_cocuk, cocuk_farki_yukseklik=d_yuk, cocuk_farki_akraba=d_akr, donusum=int(donusum),
        ilk_yil_yuk_orani=(kayit[0]["konut"] + kayit[0]["ulasim"]) / kayit[0]["gelir"],
    )
    return ozet, kayit


OZET_AD = {
    "kum_konut": ("30 yılda konut gideri (kira, taksit, aidat, bakım)", "milyon TL"),
    "kum_ulasim": ("30 yılda ulaşım gideri", "milyon TL"),
    "kum_konut_ulasim": ("30 yılda konut + ulaşım", "milyon TL"),
    "alim_yili": ("Ev alım yılı (t; evlilik = 0)", "yıl"),
    "tasinma_yili": ("Kendi evine taşınma yılı", "yıl"),
    "ev_sahibi_yil": ("30 yılın kaçında kendi evinde", "yıl"),
    "net_konut_30": ("30. yılda net konut serveti (değer − kalan kredi)", "milyon TL"),
    "net_varlik_30": ("30. yılda net varlık (konut serveti + birikim)", "milyon TL"),
    "isegidis_saat_30": ("30 yılda iki eşin işe gidiş süresi", "bin saat"),
    "bakim_yolu_saat_30": ("Ebeveyn bakımı için yolda geçen süre", "bin saat"),
    "yolda_toplam_saat_30": ("30 yılda yolda toplam (işe gidiş + bakım yolu)", "bin saat"),
    "buyukanne_bakim_saat": ("Büyükanne-büyükbabadan alınan çocuk bakımı (t=2-11)", "bin saat"),
    "anne_istihdam_olasiligi": ("Küçük çocuklu dönemde annenin çalışmayı sürdürme olasılığı", "oran"),
    "destek_uygulanabilirligi": ("Günlük büyükanne desteğinin uygulanabilirliği (0-1)", "oran"),
    "ebeveyn_mesafe_km": ("Kuşaklar arası mesafe (ebeveyne)", "km"),
    "ebeveyn_sure_dk": ("Ebeveyne tek yön yolculuk", "dk"),
    "cocuk_farki": ("A'ya göre beklenen ek çocuk (toplam, tavanlı)", "çocuk"),
    "cocuk_farki_yukseklik": ("  bunun yükseklik kanalı (Faz 2)", "çocuk"),
    "cocuk_farki_akraba": ("  bunun akraba yakınlığı kanalı (varsayım)", "çocuk"),
    "donusum": ("B'de 30 yılda dönüşüm yaşanma payı", "oran"),
    "ilk_yil_yuk_orani": ("İlk yıl konut + ulaşım / gelir", "oran"),
}
OLCEK = {"milyon TL": 1e-6, "bin saat": 1e-3}


def calistir():
    ps._utf8_konsol()
    print(f"Yaşam döngüsü Monte Carlo ({N_MC} çekiliş)...")
    cek = ornekle(N_MC, tohum=TOHUM + 1)
    ozetler = defaultdict(lambda: defaultdict(list))
    yillik = defaultdict(lambda: defaultdict(list))
    for i in range(N_MC):
        p = Prm(cek, i)
        for yol in YOLLAR:
            rng = np.random.default_rng(TOHUM * 10 + i)
            oz, kayit = yasam_simule(yol, p, rng)
            for k, v in oz.items():
                ozetler[yol][k].append(v)
            for r in kayit:
                for c in ("kum_konut_ulasim", "net_varlik", "sahip", "kusak_mesafe_km", "yol_saat"):
                    yillik[(yol, r["t"])][c].append(r[c])

    # Duyarlılık: A'da hane tek araçla yetinirse (ikinci araç yok)
    for i in range(N_MC):
        oz_a1, _ = yasam_simule("A", Prm(cek, i), np.random.default_rng(TOHUM * 10 + i), a_tek_arac=True)
        for k, v in oz_a1.items():
            ozetler["A-tek-araç"][k].append(v)
    # Temel senaryo (bütün parametreler temel değerde)
    temel = {yol: yasam_simule(yol, Prm(), np.random.default_rng(TOHUM))[0] for yol in YOLLAR}
    temel["A-tek-araç"] = yasam_simule("A", Prm(), np.random.default_rng(TOHUM), a_tek_arac=True)[0]

    satir = []
    for k, (ad, birim) in OZET_AD.items():
        for yol in YOLLAR + ["A-tek-araç"]:
            a = np.asarray(ozetler[yol][k], dtype=float)
            olc = OLCEK.get(birim, 1.0)
            gecerli = a[~np.isnan(a)]
            satir.append(dict(
                gosterge=k, aciklama=ad, birim=birim, yol=yol, yol_ad=YOL_AD[yol],
                temel=round(temel[yol][k] * olc, 3) if not (isinstance(temel[yol][k], float) and math.isnan(temel[yol][k])) else np.nan,
                medyan=round(float(np.median(gecerli)) * olc, 3) if gecerli.size else np.nan,
                p5=round(float(np.percentile(gecerli, 5)) * olc, 3) if gecerli.size else np.nan,
                p95=round(float(np.percentile(gecerli, 95)) * olc, 3) if gecerli.size else np.nan,
                gecerli_pay=round(gecerli.size / a.size, 3)))
    oz = pd.DataFrame(satir)
    oz.to_csv(SONUC / "yasam_dongusu_ozet.csv", index=False, encoding="utf-8")

    satir = []
    for (yol, t), d in sorted(yillik.items(), key=lambda x: (YOLLAR.index(x[0][0]), x[0][1])):
        r = dict(yol=yol, t=t, yil=2026 + t)
        for c, v in d.items():
            a = np.asarray(v, dtype=float)
            olc = 1e-6 if c in ("kum_konut_ulasim", "net_varlik") else 1.0
            r[f"{c}_medyan"] = round(float(np.median(a)) * olc, 4)
            r[f"{c}_p5"] = round(float(np.percentile(a, 5)) * olc, 4)
            r[f"{c}_p95"] = round(float(np.percentile(a, 95)) * olc, 4)
        satir.append(r)
    yl = pd.DataFrame(satir)
    yl.to_csv(SONUC / "yasam_dongusu_yillik.csv", index=False, encoding="utf-8")
    grafik(oz, yl)
    print("  Yaşam döngüsü tamam.")
    return oz, yl


def grafik(oz, yl):
    fig, eks = plt.subplots(2, 2, figsize=(13.5, 8.6))
    # (a) kümülatif konut + ulaşım
    for k, (c, baslik, birim) in enumerate([("kum_konut_ulasim", "Konut + ulaşım harcaması, birikimli", "milyon TL, 2026 fiyatlarıyla (reel)"),
                                             ("net_varlik", "Net varlık (konut serveti + birikim)", "milyon TL, 2026 fiyatlarıyla (reel)")]):
        ax = eks[0, k]
        sonlar = []
        for yol in YOLLAR:
            d = yl[yl.yol == yol]
            ax.fill_between(d.t, d[f"{c}_p5"], d[f"{c}_p95"], color=RENK[yol], alpha=0.10, lw=0)
            ax.plot(d.t, d[f"{c}_medyan"], color=RENK[yol], lw=2)
            sonlar.append((yol, d[f"{c}_medyan"].iloc[-1]))
        # sağ uçta doğrudan etiket (çakışmayı önlemek için dikey aralık)
        sonlar.sort(key=lambda x: x[1])
        ymin, ymax = ax.get_ylim()
        aralik = (ymax - ymin) * 0.075
        son_y = -1e18
        for yol, y in sonlar:
            y_et = max(y, son_y + aralik)
            son_y = y_et
            ax.annotate(f"{yol} {tr(y, 1)}", (29, y), xytext=(31.2, y_et), textcoords="data", fontsize=8.6, color=ps.YAZI, va="center",
                        arrowprops=dict(arrowstyle="-", color=RENK[yol], lw=0.8))
        ax.set_xlim(0, 37)
        ax.set_xticks([0, 5, 10, 15, 20, 25, 29])
        ax.set_xticklabels(["evlilik", "5", "10", "15", "20", "25", "30. yıl"])
        ax.set_title(baslik, loc="left", fontsize=10.5, fontweight="bold", pad=15)
        ax.text(0, 1.015, birim + " · çizgi medyan, bant %90 aralık", transform=ax.transAxes, fontsize=7.8, color=ps.YAZI_2, va="bottom")
        sade(ax, "y")
        tr_eksen(ax, "y", 0)
    # (c) yolda geçen süre
    ax = eks[1, 0]
    for j, yol in enumerate(YOLLAR):
        r_is = oz[(oz.gosterge == "isegidis_saat_30") & (oz.yol == yol)].iloc[0]
        r_bk = oz[(oz.gosterge == "bakim_yolu_saat_30") & (oz.yol == yol)].iloc[0]
        r_t = oz[(oz.gosterge == "yolda_toplam_saat_30") & (oz.yol == yol)].iloc[0]
        ax.barh(j, r_t.medyan, height=0.56, color=RENK[yol], edgecolor=ps.ZEMIN, lw=2)
        ax.plot([r_t.p5, r_t.p95], [j, j], color=ps.YAZI_2, lw=1)
        ax.text(r_t.p95 + 0.4, j, f"{tr(r_t.medyan, 1)} bin saat  (işe gidiş {tr(r_is.medyan, 1)} + bakım yolu {tr(r_bk.medyan, 1)})",
                va="center", fontsize=8.4, color=ps.YAZI)
    ax.set_yticks(range(len(YOLLAR)))
    ax.set_yticklabels([YOL_AD[y] for y in YOLLAR], fontsize=8.6, color=ps.YAZI)
    ax.set_ylim(len(YOLLAR) - 0.4, -0.6)
    xm = oz[oz.gosterge == "yolda_toplam_saat_30"].p95.max()
    ax.set_xlim(0, xm * 2.45)
    ax.set_title("30 yılda iki eşin yolda geçirdiği süre", loc="left", fontsize=10.5, fontweight="bold", pad=15)
    ax.text(0, 1.015, "bin saat · işe gidiş + ebeveyn bakımı yolculuğu · ince çizgi %90 aralık", transform=ax.transAxes, fontsize=7.8,
            color=ps.YAZI_2, va="bottom")
    sade(ax, "x")
    tr_eksen(ax, "x", 0)
    # (d) beklenen ek çocuk
    ax = eks[1, 1]
    for j, yol in enumerate(["B", "C"]):
        r = oz[(oz.gosterge == "cocuk_farki") & (oz.yol == yol)].iloc[0]
        ry = oz[(oz.gosterge == "cocuk_farki_yukseklik") & (oz.yol == yol)].iloc[0]
        ra = oz[(oz.gosterge == "cocuk_farki_akraba") & (oz.yol == yol)].iloc[0]
        ax.plot([r.p5, r.p95], [j, j], color=RENK[yol], lw=2.2, alpha=0.55, solid_capstyle="round")
        ax.plot(r.medyan, j, "o", color=RENK[yol], ms=8, mec=ps.ZEMIN, mew=1.4, zorder=3)
        ax.annotate(f"{tr(r.medyan, 2)}  ({tr(r.p5, 2)} / {tr(r.p95, 2)})", (r.medyan, j), xytext=(0, 10), textcoords="offset points",
                    ha="center", fontsize=8.6, color=ps.YAZI)
        ax.annotate(f"yükseklik {tr(ry.medyan, 2)} · akraba {tr(ra.medyan, 2)}", (r.medyan, j), xytext=(0, -14), textcoords="offset points",
                    ha="center", fontsize=7.6, color=ps.YAZI_2)
    ax.axvline(0, color="#8a8985", lw=0.9)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["B − A", "C − A"], fontsize=9, color=ps.YAZI)
    ax.set_ylim(1.7, -0.7)
    ax.set_xlim(-0.05, 0.35)
    ax.set_title("Beklenen ek çocuk, A'ya göre (Faz 2 sınırı)", loc="left", fontsize=10.5, fontweight="bold", pad=15)
    ax.text(0, 1.015, "çocuk/kadın · medyan ve %90 aralık · eğitim sabitken 1 kat ≈ −0,03 çocuk", transform=ax.transAxes, fontsize=7.8,
            color=ps.YAZI_2, va="bottom")
    sade(ax, "x")
    tr_eksen(ax, "x", 2)

    from matplotlib.lines import Line2D
    ogeler = [Line2D([0], [0], color=RENK[y], lw=3, label=YOL_AD[y]) for y in YOLLAR]
    fig.legend(handles=ogeler, loc="upper left", bbox_to_anchor=(0.012, 0.975), ncol=4, frameon=False, fontsize=9, handlelength=1.6,
               columnspacing=1.8)
    fig.suptitle("Bir çiftin 30 yılı: evlilik → ev → çocuk → ebeveyn bakımı (senaryo, 3.000 çekiliş)", x=0.012, ha="left", y=1.005,
                 fontsize=12.5, fontweight="bold", color=ps.YAZI)
    fig.text(0.012, -0.02, "Kaynak: 06_SIMULASYON/kod/yasam_dongusu.py; 06_SIMULASYON/sonuclar/yasam_dongusu_*.csv. Gelir, faiz, fiyat artışı ve kuşak mesafeleri varsayımdır.",
             fontsize=7.6, color=ps.YAZI_2)
    fig.subplots_adjust(hspace=0.5, wspace=0.42, top=0.88)
    kaydet(fig, "yasam_dongusu")


if __name__ == "__main__":
    calistir()
