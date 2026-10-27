import site, sys as _s; _s.path.append(site.getusersitepackages())
import json, re, sys, xlrd
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
DL = "../stres_veri/dl/"
OUT = r"C:\Users\b1601\OneDrive\Desktop\TR TAMIRAT\03_VERI\ham\stres" + "\\"
panel = pd.read_csv(r"C:\Users\b1601\OneDrive\Desktop\TR TAMIRAT\03_VERI\ham\tuik\il_paneli_ham_2025.csv", usecols=["il", "ibbs3_kod"])
kod2il = dict(zip(panel.ibbs3_kod, panel.il))
WB = "https://web.archive.org/web/{ts}id_/http://www.tuik.gov.tr/PreIstatistikTablo.do?istab_id={id}"
U109 = WB.format(ts="20171002153024", id=109); U110 = WB.format(ts="20171002155329", id=110)
U2754_17 = WB.format(ts="20180626152637", id=2754); U2754_18 = WB.format(ts="20191220230131", id=2754)

def num(x):
    if isinstance(x, float): return x
    x = str(x).strip()
    return 0.0 if x in ("-", "") else float(x)

def kod_bul(cells):
    for c in cells:
        m = re.search(r"\b(TR[0-9A-C]{3})\b", str(c))
        if m and len(m.group(1)) == 5: return m.group(1)
    return None

# --- 109: sayılar (olay yeri), 2000-2016
sh = xlrd.open_workbook(DL + "istab_109.bin").sheet_by_index(0)
yillar = [int(str(y)[:4]) for y in sh.row_values(4)[4:]]
rows, tr = [], {}
for r in range(5, sh.nrows):
    v = sh.row_values(r)
    if str(v[3]).startswith("Toplam"):
        k = kod_bul(v[:3])
        if v[0].startswith("TR Türkiye"): k = "TR"
        if k is None: continue
        e, kd = sh.row_values(r + 1), sh.row_values(r + 2)
        assert str(e[3]).startswith("Erkek") and str(kd[3]).startswith("Kad")
        for j, y in enumerate(yillar):
            rec = dict(kod=k, yil=y, intihar_sayisi=num(v[4 + j]), erkek=num(e[4 + j]), kadin=num(kd[4 + j]))
            (tr.setdefault(y, rec) if k == "TR" else rows.append(rec))
c109 = pd.DataFrame(rows)
# --- 110: kaba hız, 2001-2016
sh = xlrd.open_workbook(DL + "istab_110.bin").sheet_by_index(0)
yillar2 = [int(str(y)[:4]) for y in sh.row_values(5)[4:]]
rows, trh = [], {}
for r in range(6, sh.nrows):
    v = sh.row_values(r)
    k = "TR" if str(v[0]).startswith("TR Türkiye") else kod_bul(v[:3])
    if k is None or v[4] == "": continue
    for j, y in enumerate(yillar2):
        (trh.__setitem__(y, v[4 + j]) if k == "TR" else rows.append(dict(kod=k, yil=y, kaba_intihar_hizi=num(v[4 + j]))))
h110 = pd.DataFrame(rows)
print("109 il sayısı:", c109.kod.nunique(), " 110 il sayısı:", h110.kod.nunique())
eks = set(kod2il) - set(c109.kod); print("109 eksik:", eks, " 110 eksik:", set(kod2il) - set(h110.kod))
a = c109.merge(h110, on=["kod", "yil"], how="left")
a.insert(0, "il", a.kod.map(kod2il)); a = a.rename(columns={"kod": "ibbs3_kod"})
# toplam kontrolü
chk = a.groupby("yil")[["intihar_sayisi", "erkek", "kadin"]].sum()
chk["tr_tablo"] = [tr[y]["intihar_sayisi"] for y in chk.index]
chk["fark"] = chk.intihar_sayisi - chk.tr_tablo
chk["erkek+kadin-toplam(il)"] = (a.erkek + a.kadin - a.intihar_sayisi).abs().groupby(a.yil).sum()
print(chk)

# --- nüfus
d = json.load(open("../stres_veri/DF_ADNKS_T30.json", encoding="utf-8"))
ids, boy = d["id"], d["size"]; kat = {k: list(d["dimension"][k]["category"]["index"]) for k in ids}
rec = []
for flat, val in d["value"].items():
    i, idx = int(flat), []
    for s in reversed(boy): idx.append(i % s); i //= s
    idx = idx[::-1]; rec.append({k: kat[k][j] for k, j in zip(ids, idx)} | {"v": float(val)})
nf = pd.DataFrame(rec)
print(nf.groupby(["ADNKS_GOSTERGE"]).TIME_PERIOD.agg(["min", "max", "count"]))
pop = nf[nf.ADNKS_GOSTERGE == "NUFUS"].pivot_table(index="IKAMET_YERI", columns="TIME_PERIOD", values="v")
pop.columns = pop.columns.astype(int)
est = nf[nf.ADNKS_GOSTERGE == "NUFUS_TAHMINI"].pivot_table(index="IKAMET_YERI", columns="TIME_PERIOD", values="v")
est.columns = est.columns.astype(int)
pop_all = pop.combine_first(est)
def mid(k, y):
    return (pop_all.loc[k, y - 1] + pop_all.loc[k, y]) / 2 if (y - 1) in pop_all.columns else float("nan")
for meth in ["yil_sonu", "yil_ortasi"]:
    f = (lambda k, y: pop_all.loc[k, y]) if meth == "yil_sonu" else mid
    t = a[(a.yil >= 2009) & a.kaba_intihar_hizi.notna()].copy()
    t["hes"] = [s / f(k, y) * 1e5 for s, k, y in zip(t.intihar_sayisi, t.ibbs3_kod, t.yil)]
    t["fark"] = (t.hes - t.kaba_intihar_hizi).abs()
    print(meth, "2009-2016 ort. mutlak fark:", round(t.fark.mean(), 4), "maks:", round(t.fark.max(), 4))
    print(t.groupby("yil").fark.max().round(4).to_dict())
a["kaynak_url_sayi"] = U109; a["kaynak_url_hiz"] = U110
a["kapsam"] = "olay yeri"; a["isaret"] = "[D] arşivlenmiş TÜİK tablosu"
a.to_csv(OUT + "il_intihar_2000_2016.csv", index=False, encoding="utf-8")

# --- 2754: ikamet ili 2017, 2018
ad2kod = {v: k for k, v in kod2il.items()}
def oku2754(fn, url, yil):
    sh = xlrd.open_workbook(DL + fn).sheet_by_index(0)
    assert str(yil) in sh.row_values(0)[0], sh.row_values(0)[0]
    rows, toplam = [], None
    for r in range(4, sh.nrows):
        v = sh.row_values(r)
        if str(v[0]).startswith("Türkiye"): toplam = [num(x) for x in v[1:4]]; continue
        for o in (0, 5):
            ad = str(v[o]).strip()
            if ad and isinstance(v[o + 1], float) or (ad and str(v[o + 1]).strip() == "-"):
                if ad not in ad2kod: print("  eşleşmeyen ad:", repr(ad)); continue
                rows.append(dict(il=ad, ibbs3_kod=ad2kod[ad], yil=yil, intihar_sayisi=num(v[o + 1]), erkek=num(v[o + 2]), kadin=num(v[o + 3])))
    df = pd.DataFrame(rows)
    print(yil, "il:", len(df), "toplam(il):", df.intihar_sayisi.sum(), "TR tablo:", toplam, "E+K tutarsız satır:", int(((df.erkek + df.kadin) != df.intihar_sayisi).sum()))
    df["kaba_intihar_hizi_hesap"] = [s / mid(k, yil) * 1e5 for s, k in zip(df.intihar_sayisi, df.ibbs3_kod)]
    df["nufus_yil_ortasi"] = [mid(k, yil) for k in df.ibbs3_kod]
    df["kaynak_url"] = url; df["kapsam"] = "ikamet ili"
    df["isaret"] = "[D] sayı arşivlenmiş TÜİK tablosu; hız [H] hesaplanmış (ADNKS yıl ortası)"
    return df, toplam
for fn, url, y in [("istab_2754_2018snap.bin", U2754_17, 2017), ("istab_2754.bin", U2754_18, 2018)]:
    df, t = oku2754(fn, url, y)
    trm = (pop_all.loc["TR", y - 1] + pop_all.loc["TR", y]) / 2 if "TR" in pop_all.index else None
    print("  TR hız (hesap, yıl ortası):", t[0] / trm * 1e5 if trm else None)
    df.to_csv(OUT + f"il_intihar_{y}.csv", index=False, encoding="utf-8")
print(pop_all.index[:5].tolist(), "TR" in pop_all.index)
t = a[a.kaba_intihar_hizi.notna() & (a.yil < 2009)].copy()
t["hes"] = [s / mid(k, y) * 1e5 for s, k, y in zip(t.intihar_sayisi, t.ibbs3_kod, t.yil)]
print("2001-2008 maks fark (yıl ortası):", (t.hes - t.kaba_intihar_hizi).abs().groupby(t.yil).max().round(3).to_dict())
