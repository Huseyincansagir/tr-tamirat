"""
Konut rehberi — konut biriminin ölçüt değerlendirmesi ve paftanın sağ sütunu
===========================================================================
Her tip modülü planlarını kurar, birimin (5 kişilik hane) ölçütlerini bu modülle hesaplar.
Değerlerin hepsi plan poligonlarından ve güneş hesabından gelir [H].
"""

from __future__ import annotations

import csv

from cizim import ACIK_TURLER, YASANAN, YAZI2, metin_kutusu, tablo_ciz
from veri import HANE, OLCUT, PAIY, sayi

KAT_SIRA = {"Zemin": 0, "1. kat": 1, "2. kat": 2, "3. kat": 3, "Dam": 9}


def birim_odalari(planlar, birim):
    out = []
    for kat, p in planlar:
        p.hesapla()
        for o in p.odalar:
            if birim is None or o.birim == birim:
                out.append((kat, p, o))
    return out


def gomme_dolap(planlar, birim=None):
    """Gömme dolap ve yüklüklerin taban izi (m²) [H]: planlardaki "dolap" mobilyaları, merkezi birimin
    sayılan bir odasında kalanlar. Kiler ve depo odaları ayrıca sayılır."""
    from shapely.geometry import Point
    top = 0.0
    for _, p in planlar:
        p.hesapla()
        for tip, a, kw in p.mobilyalar:
            if tip != "dolap":
                continue
            w = a[2] if len(a) > 2 else kw.get("w")
            h = a[3] if len(a) > 3 else kw.get("h")
            if not w or not h:
                continue
            c = Point(a[0] + w / 2, a[1] + h / 2)
            oda = next((o for o in p.odalar if o.net is not None and o.net.contains(c)), None)
            if oda is None or not oda.say or oda.tur == "depo":
                continue
            if birim is not None and oda.birim != birim:
                continue
            top += w * h
    return top


def birim_ozeti(planlar, birim=None, hane=HANE, acik_ozel=0.0, acik_ortak=0.0, ic_yukseklik=2.80,
                gunes=None, arsa=None, ek=None):
    """planlar: [(kat_adı, Plan)] · birim: oda.birim etiketi (None → hepsi)."""
    odalar = birim_odalari(planlar, birim)
    net = sum(o.net.area for _, _, o in odalar if o.say and not o.yari_acik and o.tur not in ACIK_TURLER)
    yari = sum(o.net.area for _, _, o in odalar if o.yari_acik and o.say)
    teras = sum(o.net.area for _, _, o in odalar if o.tur == "teras" and o.say)
    oda_say = sum(1 for _, _, o in odalar if o.tur in ("yasam", "yatak", "misafir", "sukunet") and not o.yari_acik
                  and o.say and o.net.area >= 6.0)
    yatak = sum(1 for _, _, o in odalar if o.tur == "yatak" and o.say)
    depo_oda = sum(o.net.area for _, _, o in odalar if o.tur == "depo" and o.say)
    dolap = gomme_dolap(planlar, birim)
    depo = depo_oda + dolap
    kiler = max([o.net.area for _, _, o in odalar if o.tur == "depo" and "iler" in o.ad] + [0.0])
    oranlar, yonler = [], set()
    for _, p, o in odalar:
        if o.tur in YASANAN and not o.yari_acik and o.say:
            cam, yon = p.pencere_alani(o)
            oranlar.append((o.ad.replace("\n", " "), cam / o.net.area if o.net.area else 0))
            yonler |= yon
    karsit = ("K" in yonler and "G" in yonler) or ("D" in yonler and "B" in yonler)
    oz = dict(net=net, yari_acik=yari, teras=teras, acik_ozel=acik_ozel, acik_ortak=acik_ortak,
              net_kisi=net / hane, oda=oda_say, yatak=yatak, depo=depo, depo_oda=depo_oda, dolap=dolap,
              depo_pay=depo / net if net else 0,
              kiler=kiler, pencere_min=min((r for _, r in oranlar), default=0),
              pencere_min_oda=min(oranlar, key=lambda t: t[1])[0] if oranlar else "",
              pencere_ort=sum(r for _, r in oranlar) / len(oranlar) if oranlar else 0,
              yonler="".join(sorted(yonler)), cift_cephe=len(yonler) >= 2, karsit_cephe=karsit,
              ic_yukseklik=ic_yukseklik, acik_kisi=(acik_ozel + acik_ortak + teras) / hane,
              esik=any(o.tur == "esik" for _, _, o in odalar),
              misafir=any(o.tur == "misafir" for _, _, o in odalar),
              sukunet=any(o.tur == "sukunet" for _, _, o in odalar),
              gunes=gunes or {}, arsa=arsa)
    if ek:
        oz.update(ek)
    return oz


def durum(kosul, kismen=False):
    return "✓" if kosul else ("≈" if kismen else "✗")


def olcut_satirlari(oz):
    """İlke → ölçüt → değer → durum satırları (paftadaki kontrol listesi)."""
    g = oz.get("gunes", {})
    sat = [
        ("Büyüklük", f"net ≥ {sayi(OLCUT['net_kisi_asgari'])} m²/kişi (hedef {sayi(OLCUT['net_kisi_hedef'])})",
         f"{sayi(oz['net_kisi'], 1)} m²/kişi", durum(oz["net_kisi"] >= OLCUT["net_kisi_hedef"],
                                                     oz["net_kisi"] >= OLCUT["net_kisi_asgari"])),
        ("Oda", "5 kişiye ≥ 4 oda (TÜİK tanımı), ≥ 3 yatak",
         f"{oz['oda']} oda · {oz['yatak']} yatak", durum(oz["oda"] >= 4 and oz["yatak"] >= 3, oz["oda"] >= 4)),
        ("Gün ışığı", f"cam/taban ≥ 1/8 (hedef 1/6), en düşük oda",
         f"{sayi(oz['pencere_min'], 2)} ({oz['pencere_min_oda'][:16]})",
         durum(oz["pencere_min"] >= OLCUT["pencere_taban"] - 1e-9, oz["pencere_min"] >= 0.10)),
        ("Havalandırma", "iki yöne bakan konut (karşıt cephe tercih)",
         f"yönler {oz['yonler']}" + (" · karşıt" if oz["karsit_cephe"] else ""),
         durum(oz["karsit_cephe"], oz["cift_cephe"])),
    ]
    if g:
        sat.append(("Güneş", "ana yaşam odası 21 Şubat ≥ 1,5 sa (TS EN 17037 asgari)",
                    f"{sayi(g.get('21 Şubat', 0), 1)} sa · 21 Ara {sayi(g.get('21 Aralık', 0), 1)} sa",
                    durum(g.get("21 Şubat", 0) >= OLCUT["gunes_saat_orta"], g.get("21 Şubat", 0) >= OLCUT["gunes_saat_asgari"])))
    sat += [
        ("Tavan", f"net iç yükseklik ≥ {sayi(OLCUT['ic_yukseklik'], 2)} m (PAİY ≥ {sayi(PAIY['md28_ic_yuk'], 2)})",
         f"{sayi(oz['ic_yukseklik'], 2)} m", durum(oz["ic_yukseklik"] >= OLCUT["ic_yukseklik"])),
        ("Toprakla temas", f"dış mekân ≥ {sayi(OLCUT['acik_alan_kisi'])} m²/kişi (özel + ortak + teras)",
         f"{sayi(oz['acik_kisi'], 1)} m²/kişi", durum(oz["acik_kisi"] >= OLCUT["acik_alan_kisi"], oz["acik_kisi"] >= 5)),
        ("Mahremiyet", "giriş eşiği + aileden ayrı misafir bölümü",
         ("eşik " + ("var" if oz["esik"] else "yok") + " · misafir " + ("var" if oz["misafir"] else "yok")),
         durum(oz["esik"] and oz["misafir"], oz["esik"] or oz["misafir"])),
        ("Sükûnet", "namaz ve okuma için sessiz oda ya da niş, kıble planda",
         "oda" if oz["sukunet"] else oz.get("sukunet_not", "niş"),
         durum(oz["sukunet"], oz.get("sukunet_not", "niş") != "yok")),
        ("Depolama", f"kiler ≥ {sayi(OLCUT['kiler_m2'])} m², kiler + depo + gömme dolap ≥ %{sayi(100 * OLCUT['depolama_pay'])} net",
         f"kiler {sayi(oz['kiler'], 1)} m² · %{sayi(100 * oz['depo_pay'], 1)}",
         durum(oz["kiler"] >= OLCUT["kiler_m2"] and oz["depo_pay"] >= OLCUT["depolama_pay"],
               oz["kiler"] >= OLCUT["kiler_m2"] or oz["depo_pay"] >= 0.05)),
    ]
    for k in ("kusak", "buyume_satir", "erisim", "su", "deprem", "sessizlik", "isil"):
        if k in oz:
            sat.append(oz[k])
    return sat


def alan_programi_satirlari(planlar, birim_adlari=None):
    """Pafta tablosu için oda satırları: (kat, oda, en × boy, net m², cam/taban)."""
    sat = []
    for kat, p in planlar:
        for r in p.tablo():
            if not r["say"]:
                continue
            olcu = f"{sayi(r['en'], 2)} × {sayi(r['boy'], 2)}" if r["dik"] else "L biçimli"
            ct = sayi(r["pencere_taban"], 2) if r["tur"] in YASANAN and not r["yari_acik"] else "—"
            ad = r["oda"]
            if birim_adlari and r["birim"] in birim_adlari:
                ad = f"{birim_adlari[r['birim']]} · {ad}"
            if r["yari_acik"]:
                ad += " (yarı açık)"
            sat.append((kat, ad[:34], olcu, sayi(r["net_m2"], 1), ct))
    return sat


def csv_satirlari(tip, planlar, birim_adlari=None):
    out = []
    for kat, p in planlar:
        for r in p.tablo():
            out.append(dict(tip=tip, kat=kat, birim=(birim_adlari or {}).get(r["birim"], r["birim"]), oda=r["oda"],
                            tur=r["tur"], net_m2=r["net_m2"], en_m=r["en"], boy_m=r["boy"],
                            dikdortgen=int(r["dik"]), yari_acik=int(r["yari_acik"]), toplama_girer=int(r["say"]),
                            cam_m2=r["cam_m2"], cam_taban=r["pencere_taban"], pencere_yonleri=r["yonler"]))
    return out


CSV_ALANLAR = ["tip", "kat", "birim", "oda", "tur", "net_m2", "en_m", "boy_m", "dikdortgen", "yari_acik",
               "toplama_girer", "cam_m2", "cam_taban", "pencere_yonleri"]


def sag_sutun(fig, x_mm, y_ust, w_mm, planlar, oz, ozet_satirlari, birim_adlari=None, yazi=5.7, satir_h=3.55,
              ust_baslik="Alan programı (net: duvar içi, m²) [H]"):
    """Alan programı + özet + ölçüt kontrol listesi. Dönüş: (metinler, alt y)."""
    m = []
    sat = alan_programi_satirlari(planlar, birim_adlari)
    tm, h = tablo_ciz(fig, x_mm, y_ust - (6.5 + satir_h * (len(sat) + 1) + 1.5), w_mm,
                      ["Kat", "Oda", "En × boy (m)", "Net m²", "Cam/taban"], sat,
                      [0, 13, w_mm * 0.56, w_mm * 0.78, w_mm * 0.89], baslik_metin=ust_baslik, yazi=yazi,
                      satir_h=satir_h, hizalar=["left", "left", "left", "right", "right"])
    m += tm
    y = y_ust - h - 2.5
    tm, h = tablo_ciz(fig, x_mm, y - (satir_h * (len(ozet_satirlari) + 1) + 1.5 + 6.5), w_mm, ["Özet", "Değer"],
                      ozet_satirlari, [0, w_mm * 0.62], baslik_metin="Birim özeti (5 kişilik hane) [H]", yazi=yazi,
                      satir_h=satir_h, hizalar=["left", "right"])
    m += tm
    y = y - h - 2.5
    ol = olcut_satirlari(oz)
    tm, h = tablo_ciz(fig, x_mm, y - (satir_h * (len(ol) + 1) + 1.5 + 6.5), w_mm, ["İlke", "Ölçüt (öneri)", "Bu tip", ""],
                      ol, [0, w_mm * 0.17, w_mm * 0.64, w_mm * 0.96], baslik_metin="İlke kontrol listesi [H]",
                      yazi=yazi - 0.25, satir_h=satir_h, hizalar=["left", "left", "left", "left"])
    m += tm
    y = y - h - 2.0
    return m, y


def csv_yaz(yol, satirlar, alanlar):
    with open(yol, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=alanlar)
        w.writeheader()
        for s in satirlar:
            w.writerow(s)
