import site, sys; sys.path.append(site.getusersitepackages())
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
O = "C:/Users/b1601/OneDrive/Desktop/TR TAMIRAT/03_VERI/ham/stres/"
sira = {k: i for i, k in enumerate(pd.read_csv("C:/Users/b1601/OneDrive/Desktop/TR TAMIRAT/03_VERI/ham/tuik/il_paneli_ham_2025.csv").ibbs3_kod)}
a = pd.read_csv(O + "il_intihar_2000_2016.csv")
for c in ["intihar_sayisi", "erkek", "kadin"]: a[c] = a[c].astype(int)
a["kaba_intihar_hizi"] = a.kaba_intihar_hizi.round(6)
a = a.sort_values(["yil", "ibbs3_kod"], key=lambda s: s.map(sira) if s.name == "ibbs3_kod" else s)
a.to_csv(O + "il_intihar_2000_2016.csv", index=False, encoding="utf-8")
parca = [a.assign(hiz_isaret="[D]")[["il", "ibbs3_kod", "yil", "intihar_sayisi", "erkek", "kadin", "kaba_intihar_hizi", "hiz_isaret", "kapsam", "kaynak_url_sayi"]].rename(columns={"kaynak_url_sayi": "kaynak_url"})]
for y in (2017, 2018):
    b = pd.read_csv(O + f"il_intihar_{y}.csv")
    for c in ["intihar_sayisi", "erkek", "kadin"]: b[c] = b[c].astype(int)
    b["kaba_intihar_hizi_hesap"] = b.kaba_intihar_hizi_hesap.round(3)
    b = b.sort_values("ibbs3_kod", key=lambda s: s.map(sira))
    b.to_csv(O + f"il_intihar_{y}.csv", index=False, encoding="utf-8")
    parca.append(b.rename(columns={"kaba_intihar_hizi_hesap": "kaba_intihar_hizi"}).assign(hiz_isaret="[H]")[parca[0].columns])
u = pd.concat(parca, ignore_index=True)
u.to_csv(O + "il_intihar_2000_2018_birlesik.csv", index=False, encoding="utf-8")
print(u.groupby("yil").agg(n=("il", "size"), toplam=("intihar_sayisi", "sum")).T.to_string())
print("2016 en yüksek kaba hız:", a[a.yil == 2016].nlargest(5, "kaba_intihar_hizi")[["il", "kaba_intihar_hizi"]].round(2).values.tolist())
b18 = pd.read_csv(O + "il_intihar_2018.csv")
print("2018 en yüksek hesaplanan hız:", b18.nlargest(5, "kaba_intihar_hizi_hesap")[["il", "intihar_sayisi", "kaba_intihar_hizi_hesap"]].values.tolist())
e = pd.read_csv(O + "il_ilye_2015_endeks.csv")
print(e[e.il.isin(["Isparta", "Sakarya", "Bolu", "Muş", "Mardin", "Ağrı"])][["il", "genel_sira", "genel_endeks"]].round(4).values.tolist())

# trafik / işe gidiş
tt = pd.read_csv("../stres_veri/tomtom/tomtom_tr.csv")
TU = "https://www.tomtom.com/traffic-index/country/turkey"
r = []
for _, x in tt.iterrows():
    for g, v, br in [("sikisiklik_duzeyi", x.sikisiklik_pct, "%"), ("ort_hiz", x.ort_hiz_kmsa, "km/sa"), ("10km_sure_hesap", x.dk_10km_hesap, "dk"),
                     ("dunya_sirasi_sikisiklik", x.dunya_sirasi, "sıra"), ("km_15dk", x.km_15dk, "km"), ("tLostRush_ham", x.tLostRush_ham, "saat? (anlamı doğrulanmadı)")]:
        r.append(dict(kaynak="TomTom Traffic Index", yil=2025, birim_alan=x.sehir + " (" + x.kapsam + ")", gosterge=g, deger=v, birim=br, kaynak_url=TU, isaret="[İ]"))
for sehir, sure, cong, rs in [("Istanbul", "22 dk 54 sn", 62.0, 20.7), ("Ankara", "21 dk 3 sn", 55.8, 20.9), ("Izmir", "22 dk 59 sn", 54.1, 19.9)]:
    url = f"https://www.tomtom.com/traffic-index/{sehir.lower()}-traffic/"
    r += [dict(kaynak="TomTom Traffic Index (şehir sayfası metni)", yil=2025, birim_alan=sehir + " (sehir_merkezi)", gosterge="10km_ortalama_sure", deger=sure, birim="dk:sn", kaynak_url=url, isaret="[İ]"),
          dict(kaynak="TomTom Traffic Index (şehir sayfası metni)", yil=2025, birim_alan=sehir + " (sehir_merkezi)", gosterge="zirve_saat_ort_hiz", deger=rs, birim="km/sa", kaynak_url=url, isaret="[İ]"),
          dict(kaynak="TomTom Traffic Index (şehir sayfası metni)", yil=2025, birim_alan=sehir + " (sehir_merkezi)", gosterge="zirve_saatte_kaybedilen_sure", deger=112, birim="saat/yıl (üç şehirde aynı; şüpheli)", kaynak_url=url, isaret="[İ]")]
ZU = "https://web.archive.org/web/20170710125853id_/http://www.tuik.gov.tr/PreIstatistikTablo.do?istab_id=2402"
for grup, dk06, dk15 in [("15+ yaş toplam", 78, 64.4), ("15+ erkek", 103, 82.5), ("15+ kadın", 55, 46.8), ("çalışan toplam", 95, 82.4),
                         ("çalışan erkek", 105, 89.5), ("çalışan kadın", 69, 65.2), ("çalışmayan toplam", 62, 48.9)]:
    for y, d in [("2006", dk06), ("2014-15", dk15)]:
        r.append(dict(kaynak="TÜİK Zaman Kullanım Araştırması", yil=y, birim_alan="Türkiye - " + grup, gosterge="ulasim_ve_belirlenmemis_zaman_gunluk",
                      deger=d, birim="dk/gün", kaynak_url=ZU, isaret="[D]"))
pd.DataFrame(r).to_csv(O + "tr_trafik_isegidis.csv", index=False, encoding="utf-8")
print(len(r), "trafik satırı")
