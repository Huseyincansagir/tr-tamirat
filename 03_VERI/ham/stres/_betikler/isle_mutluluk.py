import site, sys; sys.path.append(site.getusersitepackages())
import re, xlrd
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
DL = "../stres_veri/dl/"
OUT = r"C:\Users\b1601\OneDrive\Desktop\TR TAMIRAT\03_VERI\ham\stres" + "\\"
panel = pd.read_csv(r"C:\Users\b1601\OneDrive\Desktop\TR TAMIRAT\03_VERI\ham\tuik\il_paneli_ham_2025.csv", usecols=["il", "ibbs3_kod"])
IL = list(panel.il); il2kod = dict(zip(panel.il, panel.ibbs3_kod))
WB = "https://web.archive.org/web/{ts}id_/http://www.tuik.gov.tr/PreIstatistikTablo.do?istab_id={id}"
U = {2421: WB.format(ts="20200613054855", id=2421), 2420: WB.format(ts="20190921125502", id=2420),
     2235: WB.format(ts="20200928023820", id=2235), 2238: WB.format(ts="20200920023907", id=2238),
     2240: WB.format(ts="20200203080610", id=2240), 925: WB.format(ts="20200920025505", id=925),
     938: WB.format(ts="20180317103247", id=938), 1597: WB.format(ts="20200928014020", id=1597)}


def ad(x):
    x = re.sub(r"\s+", " ", str(x)).strip()
    return x if x in il2kod else None


def il_satirlari(sh, start=6):
    out = {}
    for r in range(start, sh.nrows):
        v = sh.row_values(r)
        a = ad(v[0])
        if a:
            out[a] = v
    eks = set(IL) - set(out)
    assert not eks, eks
    return out


def f(x):
    return None if x in ("", "-") else float(x)


# İLYE gösterge değerleri
KISA = {2: "oda_sayisi_kisi_basi", 3: "tuvalet_konut_ici_pct", 4: "konut_kalite_problemi_pct", 6: "istihdam_orani_pct", 7: "issizlik_orani_pct",
        8: "ort_gunluk_kazanc_tl", 9: "is_memnuniyeti_pct", 11: "kisi_basi_tasarruf_mevduati_tl", 12: "orta_ustu_gelir_hane_pct",
        13: "temel_ihtiyac_karsilayamayan_hane_pct", 15: "bebek_olum_hizi_binde", 16: "dogusta_yasam_suresi_yil", 17: "hekim_basi_muracaat",
        18: "saglik_memnuniyeti_pct", 19: "kamu_saglik_memnuniyeti_pct", 21: "okuloncesi_net_okullasma_pct", 22: "teog_puan_ort",
        23: "ygs_puan_ort", 24: "yuksekogretim_mezun_pct", 25: "kamu_egitim_memnuniyeti_pct", 27: "pm10_ug_m3", 28: "orman_alani_pct",
        29: "atik_hizmeti_nufus_pct", 30: "sokak_gurultusu_problemi_pct", 31: "belediye_temizlik_memnuniyeti_pct", 33: "cinayet_milyonda",
        34: "olumlu_yaralanmali_kaza_binde", 35: "gece_yalniz_yururken_guvende_pct", 36: "kamu_asayis_memnuniyeti_pct",
        38: "yerel_secim_katilim_pct", 39: "siyasi_parti_uyelik_pct", 40: "sendika_dernek_ilgi_pct", 42: "internet_abone_yuzkiside",
        43: "kanalizasyon_sebeke_erisim_pct", 44: "havalimani_erisim_orani", 45: "belediye_toplu_tasima_memnuniyeti_pct",
        47: "sinema_tiyatro_seyirci_yuzkiside", 48: "avm_alani_m2_binkiside", 49: "sosyal_iliski_memnuniyeti_pct",
        50: "sosyal_hayat_memnuniyeti_pct", 52: "mutluluk_duzeyi_pct"}
sh = xlrd.open_workbook(DL + "istab_2421.bin").sheet_by_index(0)
assert "2015" in sh.row_values(0)[0]
for i in KISA:
    assert sh.row_values(5)[i], i
rows = il_satirlari(sh, 7)
g = pd.DataFrame([{"il": a, "ibbs3_kod": il2kod[a], "endeks_yili": 2015} | {k: f(rows[a][i]) for i, k in KISA.items()} for a in IL])
g["kaynak_url"] = U[2421]
print("İLYE gösterge: satır", len(g), "sütun", len(KISA), "boş hücre:", int(g[list(KISA.values())].isna().sum().sum()))
g.to_csv(OUT + "il_ilye_2015_gostergeler.csv", index=False, encoding="utf-8")
sec = g[["il", "ibbs3_kod", "endeks_yili", "mutluluk_duzeyi_pct", "gece_yalniz_yururken_guvende_pct", "sokak_gurultusu_problemi_pct",
         "oda_sayisi_kisi_basi", "konut_kalite_problemi_pct", "pm10_ug_m3", "sosyal_hayat_memnuniyeti_pct",
         "belediye_toplu_tasima_memnuniyeti_pct", "kaynak_url"]].copy()
sec.insert(7, "kisi_sayisi_oda_basi_hesap", (1 / sec.oda_sayisi_kisi_basi).round(3))
sec.to_csv(OUT + "il_ilye_2015_stres_secilmis.csv", index=False, encoding="utf-8")

# İLYE endeks ve sıralamalar
sh = xlrd.open_workbook(DL + "istab_2420.bin").sheet_by_index(0)
alan = ["genel", "konut", "calisma_hayati", "gelir_servet", "saglik", "egitim", "cevre", "guvenlik", "sivil_katilim", "altyapi",
        "sosyal_yasam", "yasam_memnuniyeti"]
rows = il_satirlari(sh, 7)
e = []
for a in IL:
    v = rows[a]
    d = {"il": a, "ibbs3_kod": il2kod[a], "endeks_yili": 2015}
    for j, k in enumerate(alan):
        d[f"{k}_sira"] = int(v[2 + 3 * j])
        d[f"{k}_endeks"] = float(v[3 + 3 * j])
    e.append(d)
e = pd.DataFrame(e)
e["kaynak_url"] = U[2420]
tam = [k for k in alan if sorted(e[f"{k}_sira"]) == list(range(1, 82))]
print("İLYE endeks: sırası 1..81 tam olan alan sayısı:", len(tam), "/", len(alan), " genel ilk 3:", e.sort_values("genel_sira").il.head(3).tolist(),
      " son 3:", e.sort_values("genel_sira").il.tail(3).tolist())
e.to_csv(OUT + "il_ilye_2015_endeks.csv", index=False, encoding="utf-8")

# YMA 2013 il mutluluk
sh = xlrd.open_workbook(DL + "istab_2235.bin").sheet_by_index(0)
rows = il_satirlari(sh, 8)
trv = [sh.row_values(r) for r in range(6, 9) if str(sh.row_values(r)[0]).strip() == "Türkiye"][0]
m = pd.DataFrame([{"il": a, "ibbs3_kod": il2kod[a], "yil": 2013, "mutlu_pct": rows[a][2], "mutlu_erkek_pct": rows[a][3], "mutlu_kadin_pct": rows[a][4],
                   "orta_pct": rows[a][6], "mutsuz_pct": rows[a][10], "mutsuz_erkek_pct": rows[a][11], "mutsuz_kadin_pct": rows[a][12]} for a in IL])
m["kaynak_url"] = U[2235]
top = m.mutlu_pct + m.orta_pct + m.mutsuz_pct
print("YMA2013: Türkiye mutlu", trv[2], "orta", trv[6], "mutsuz", trv[10], "| il mutlu+orta+mutsuz min/maks:", round(top.min(), 2), round(top.max(), 2))
cmp = m.merge(g[["il", "mutluluk_duzeyi_pct"]], on="il")
print("YMA2013 mutlu_pct vs İLYE mutluluk_duzeyi maks fark:", round((cmp.mutlu_pct - cmp.mutluluk_duzeyi_pct).abs().max(), 4))
print("en yüksek 3:", m.nlargest(3, "mutlu_pct")[["il", "mutlu_pct"]].values.tolist(), " en düşük 3:", m.nsmallest(3, "mutlu_pct")[["il", "mutlu_pct"]].values.tolist())
m.to_csv(OUT + "il_mutluluk_2013.csv", index=False, encoding="utf-8")

# YMA 2013 il mutluluk kaynağı
sh = xlrd.open_workbook(DL + "istab_2238.bin").sheet_by_index(0)
rows = il_satirlari(sh, 8)
ks = {1: "kaynak_kisi_tum_aile_pct", 3: "kaynak_kisi_cocuklar_pct", 5: "kaynak_kisi_es_pct", 7: "kaynak_kisi_anne_baba_pct", 9: "kaynak_kisi_kendisi_pct",
      11: "kaynak_kisi_torunlar_pct", 13: "kaynak_kisi_diger_pct", 15: "kaynak_deger_saglik_pct", 17: "kaynak_deger_sevgi_pct", 19: "kaynak_deger_basari_pct",
      21: "kaynak_deger_para_pct", 23: "kaynak_deger_is_pct", 25: "kaynak_deger_diger_pct"}
k = pd.DataFrame([{"il": a, "ibbs3_kod": il2kod[a], "yil": 2013} | {n: f(rows[a][i]) for i, n in ks.items()} for a in IL])
k["kaynak_url"] = U[2238]
k.to_csv(OUT + "il_mutluluk_kaynagi_2013.csv", index=False, encoding="utf-8")

# YMA 2013 il kamu hizmetleri memnuniyeti (seçilmiş)
sh = xlrd.open_workbook(DL + "istab_2240.bin").sheet_by_index(0)
rows = il_satirlari(sh, 8)
ks = {1: "sgk_memnun_pct", 6: "saglik_memnun_pct", 10: "egitim_memnun_pct", 14: "adli_memnun_pct", 19: "asayis_memnun_pct", 20: "asayis_orta_pct",
      21: "asayis_memnun_degil_pct", 23: "ulastirma_memnun_pct", 24: "ulastirma_orta_pct", 25: "ulastirma_memnun_degil_pct"}
k = pd.DataFrame([{"il": a, "ibbs3_kod": il2kod[a], "yil": 2013} | {n: f(rows[a][i]) for i, n in ks.items()} for a in IL])
k["kaynak_url"] = U[2240]
k.to_csv(OUT + "il_kamu_hizmet_memnuniyeti_2013.csv", index=False, encoding="utf-8")

# Ulusal seriler (YMA)
uz = []
for tid, gost in [(925, "genel_mutluluk_duzeyi"), (938, "gece_yalniz_yururken_guvende_hissetme"), (1597, "mutluluk_kaynagi")]:
    sh = xlrd.open_workbook(DL + f"istab_{tid}.bin").sheet_by_index(0)
    yil = sh.row_values(3)
    grup = ""
    for r in range(4, sh.nrows):
        v = sh.row_values(r)
        if v[0] and not v[1]:
            if str(v[0]).startswith(("TÜİK", "TurkStat", "Tablo", "Figures", "-")):
                break
            grup = re.sub(r"\s+", " ", str(v[0]))
            continue
        if v[1]:
            for j in range(2, len(v)):
                if yil[j] != "" and v[j] not in ("", "-"):
                    uz.append(dict(gosterge=gost, grup=grup, kategori=v[1], yil=int(yil[j]), deger_pct=float(v[j]), kaynak_url=U[tid]))
uz = pd.DataFrame(uz)
uz.to_csv(OUT + "tr_yasam_memnuniyeti_ulusal_2003_2019.csv", index=False, encoding="utf-8")
t = uz[uz.grup == "Toplam-Total"]
for gost in ["genel_mutluluk_duzeyi", "gece_yalniz_yururken_guvende_hissetme"]:
    p = t[t.gosterge == gost].pivot_table(index="yil", columns="kategori", values="deger_pct")
    print(gost, "son yıl:", p.index.max(), p.loc[p.index.max()].round(2).to_dict())
print(uz.groupby(["gosterge", "grup"]).size())
