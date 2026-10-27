"""
Faz 4 · Rapor 7 — Seçenekler ve kademe tablosu (ölçeklenebilir şehir modeline girdi)
===================================================================================
Soru: Gelir ve vergi adaletini, ticareti ve kendi kendine yeterliliği güçlendiren araçlardan hangisi hangi kademede
(mahalle ≈ 7 bin, semt ≈ 35 bin, şehir ≈ 210 bin, bölge ≈ 1,25 milyon kişi, ülke) uygulanır?

Girdi: 05_ANALIZ/sonuclar/ekonomi_*.csv (ekonomi_veri.py, ekonomi_dagilim.py, ekonomi_ticaret_yeterlilik.py)
Çıktı:
  ekonomi_kademe.csv            araç × kademe rol tablosu (metin; modelin "kim ne yapar" katmanı)
  ekonomi_kademe_parametre.csv  kademe başına sayısal büyüklükler, 2025 fiyatları (modelin sayısal katmanı)
  ekonomi_secenekler.csv        her seçenek için kanıt, etki, maliyet, yan etki, kazanan ve kaybeden
Kademe nüfusları Rapor 18 (enerji_kademe.csv) ve kademe şemasıyla aynı: 6.925 / 34.624 / 207.744 / 1.246.464.
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/ekonomi_kademe.py  (önce öteki üç ekonomi betiği)
"""
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
SON = KOK / "05_ANALIZ" / "sonuclar"


def oku(ad):
    return pd.read_csv(SON / f"ekonomi_{ad}.csv")


def tr(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")


# ----------------------------------------------------------------------------- girdiler
NUFUS = 86_092_168            # ADNKS 31.12.2025 [D]
HANE = 26_977_795             # ADNKS 2025 [D]
KADEME = {"mahalle": 6_925, "semt": 34_624, "sehir": 207_744, "bolge": 1_246_464, "ulke": NUFUS}
wbt = oku("dunya_bankasi").set_index("yil")
GSYH = wbt.loc[2025, "gsyh_mlr_tl"]
hh = oku("hanehalki_sektor_hesaplari").set_index("yil")
B6G = hh.loc[2025, "B6G_brut_kullanilabilir_gelir"]
D62 = hh.loc[2025, "D62_sosyal_yardimlar"]
yer = oku("yerel_gelirler").set_index("yil").loc[2025]
temel = oku("dagilim_temel")
oz = oku("dagilim_ozet").set_index("senaryo")
sen = oku("dagilim_senaryolar")
vht = oku("vergi_harcamasi_tahsilat").set_index("vergi")
vh = oku("vergi_harcamalari").set_index("kalem")
isg = oku("isgucu_yillik").set_index("yil").loc[2025]
esn = oku("ticaret_esnaf_kayitdisi").set_index("gosterge").deger
htm = oku("ticaret_perakende").set_index("gosterge")
tg = oku("temel_gelir_maliyet")
NUFUS_2021 = 84_680_273       # ADNKS 2021 [D]; HTM mağaza sayıları 2021 yılına ait
AVM_M2 = 13.9e6               # AVM kiralanabilir alanı, 2025 sonu (basın aktarımı) [İ]

avd_kisi = 0.005 * GSYH * 1e9 / NUFUS
s2 = [k for k in oz.index if k.startswith("Gıdada")][0]
s3 = [k for k in oz.index if k.endswith("varyant C")][0]
genel_yeni = re.search(r"genel KDV %([\d,]+)", s3).group(1)
s2_maliyet = -oz.loc[s2, "hanehalki_net_yuk_degisimi_mlr_tl"]
s2_dilim1 = oz.loc[s2, "dilim1_gelire_pct"]
s5_dilim1 = oz.loc[[k for k in oz.index if "en yoksul" in k][0], "dilim1_gelire_pct"]

# ----------------------------------------------------------------------------- 1. kademe parametreleri (sayısal)
kisi_basi = {
    # ad: (kişi başı değer, birim, işaret, kaynak)
    "hane_sayisi": (HANE / NUFUS, "hane", "D", "ADNKS 2025"),
    "hanehalki_brut_kullanilabilir_gelir_mn_tl": (B6G * 1e3 / NUFUS, "milyon TL/yıl", "D/H", "TÜİK sektör hesapları S1M 2025"),
    "sosyal_yardimlar_D62_mn_tl": (D62 * 1e3 / NUFUS, "milyon TL/yıl", "D/H", "TÜİK sektör hesapları S1M 2025 (çoğu emekli aylığı)"),
    "kdv_otv_hanehalki_yuku_mn_tl": ((temel.kdv_mlr_tl.sum() + temel.otv_mlr_tl.sum()) * 1e3 / NUFUS, "milyon TL/yıl", "H/V",
                                     "ekonomi_dagilim.py, 2025"),
    "emlak_vergisi_mevcut_mn_tl": (yer.emlak_vergisi * 1e3 / NUFUS, "milyon TL/yıl", "D/H", "Muhasebat mahalli idareler 2025"),
    "arsa_vergisi_mevcut_mn_tl": (yer.arsa_vergisi * 1e3 / NUFUS, "milyon TL/yıl", "D/H", "Muhasebat mahalli idareler 2025"),
    "arsa_deger_vergisi_gsyh05_mn_tl": (avd_kisi / 1e6, "milyon TL/yıl", "V/H", "GSYH'nin %0,5'i (OECD taşınmaz vergisi ort. %0,95)"),
    "harcamalara_katilma_payi_mevcut_mn_tl": (yer.harcamalara_katilma_paylari * 1e3 / NUFUS, "milyon TL/yıl", "D/H",
                                              "Muhasebat mahalli idareler 2025"),
    "issiz_kisi": (isg.issiz_bin * 1e3 / NUFUS, "kişi", "D/H", "TÜİK SDMX işgücü 2025 ortalaması"),
    "atil_isgucu_kisi_yaklasik": (isg.atil_kisi_bin_yaklasik * 1e3 / NUFUS, "kişi", "H/V", "atıl işgücü oranı × işgücü (alt sınır)"),
    "kayitli_esnaf": (esn["TESK kayıtlı esnaf ve sanatkâr (30.09.2026)"] / NUFUS, "işletme", "D/H", "TESK sicil 30.09.2026"),
    "esnaf_acilis_yillik": (esn["TESK esnaf açılış 2025"] / NUFUS, "işletme/yıl", "D/H", "TESK 2025"),
    "esnaf_kapanis_yillik": (esn["TESK esnaf kapanış 2025"] / NUFUS, "işletme/yıl", "D/H", "TESK 2025"),
    "htm_geleneksel_magaza": (htm.loc["Mağaza sayısı: geleneksel kanal", "y2021"] / NUFUS_2021, "mağaza", "D/H",
                              "Rekabet Kurumu HTM raporu, 2021"),
    "htm_zincir_magaza": (htm.loc["Mağaza sayısı: organize kanal", "y2021"] / NUFUS_2021, "mağaza", "D/H",
                          "Rekabet Kurumu HTM raporu, 2021"),
    "avm_kiralanabilir_alan_m2": (AVM_M2 / NUFUS, "m²", "İ/H", "AYD ve değerleme raporları, 2025 sonu"),
    "temel_gelir_yarim_aclik_mn_tl": (tg.yillik_maliyet_mlr_tl.iloc[1] * 1e3 / NUFUS, "milyon TL/yıl", "H/V",
                                      "kişi başı açlık sınırının yarısı, 2025"),
}
par = []
for ad, (v, birim, isaret, kaynak) in kisi_basi.items():
    satir = {"parametre": ad, "birim": birim}
    for k, n in KADEME.items():
        satir[k] = v * n
    satir["kisi_basi"] = v
    satir["isaret"] = isaret
    satir["kaynak"] = kaynak
    par.append(satir)
par = pd.DataFrame(par)
par.insert(2, "fiyat_yili", 2025)
par.loc[par.birim.isin(["hane", "kişi", "işletme", "işletme/yıl", "mağaza", "m²"]), "fiyat_yili"] = None
par = pd.concat([pd.DataFrame([{"parametre": "nufus", "birim": "kişi", **KADEME, "kisi_basi": 1, "isaret": "D/V",
                                "kaynak": "kademe şeması; ülke = ADNKS 2025"}]), par], ignore_index=True)
par.round(3).to_csv(SON / "ekonomi_kademe_parametre.csv", index=False, encoding="utf-8")
print(par[["parametre", "mahalle", "semt", "sehir", "bolge"]].round(1).to_string())

# ----------------------------------------------------------------------------- 2. kademe rol tablosu
# Rol sözlüğü: K = karar ve kural; U = uygulama ve tahsil; H = hizmet ve mekân; V = veri ve izleme; — = rol yok
K = ["kod", "arac", "grup", "birincil_kademe", "mahalle", "semt", "sehir", "bolge", "ulke", "yasal_dayanak_bugun",
     "gereken_islem", "olcum_gostergesi"]
satirlar = [
    ("V1", "Arsa değer vergisi (emlak vergisinin arsa değerine kaydırılması)", "vergi", "ülke (kural) + şehir (tahsil)",
     "V: parsel değer haritasının mahalle muhtarlığıyla güncellenmesi; itiraz noktası",
     "—", "U: tahsil, oran bandı içinde oran seçimi, ödeme erteleme başvurusu",
     "V: bölge değerleme ofisi (TKGM/SPK lisanslı değerleme), yıllık değer haritası",
     "K: 1319 sayılı Emlak Vergisi Kanunu değişikliği; değerleme standardı; muafiyet ve erteleme kuralı; KDV indirimiyle eşleme",
     "1319 s. Kanun md. 8 ve 18: mesken binde 1, diğer bina binde 2, arsa binde 3, arazi binde 1; büyükşehirde %100 artırımlı; matrah takdir komisyonunun asgari birim değeri (md. 29) [D]",
     "Kanun", "Taşınmaz vergisi / GSYH (2024: %0,10; OECD %0,95); arsa vergisi / emlak vergisi"),
    ("V2", "Dolaylı vergiden doğrudan vergiye kayış (KDV oranı ↓, gelir vergisi tabanı ↑)", "vergi", "ülke",
     "—", "—", "—", "—",
     "K: KDV ve GVK oranları; beyan sistemi; vergi idaresi kapasitesi",
     "3065 s. KDV Kanunu; 193 s. GVK", "Kanun ve Cumhurbaşkanı kararı (KDV oranları)",
     "Dolaylı vergilerin vergi gelirindeki payı (2025: %62,4 merkezi bütçe, geniş tanım)"),
    ("V3", "Temel gıdada KDV'nin sıfırlanması (%1 → %0)", "vergi", "ülke",
     "V: mahalle fiyat izleme (yansıma denetimi)", "—", "—", "—",
     "K: Cumhurbaşkanı kararı; KDV iadesi düzeni (indirimli orana tabi teslimlerde iade)",
     "3065 s. Kanun md. 28; I sayılı liste", "Cumhurbaşkanı kararı",
     "Gıda TÜFE'si ile üretici fiyatı arasındaki fark; vergiden vazgeçilen gelir"),
    ("V4", "Vergi tabanının genişletilmesi: sermaye ve kira gelirindeki istisna ve indirimli stopajların daraltılması",
     "vergi", "ülke", "—", "—", "—", "—",
     "K: GVK Geçici md. 67, GVK 22/3, KVK 5/1-d, GVK 86/1-c gibi istisnaların gözden geçirilmesi; asgari ücret istisnası korunur",
     "GİB Vergi Harcamaları Raporu 2025 (3.170 mlr TL)", "Kanun",
     "Vergi harcaması / tahsilat (2025: %28,7); ücret dışı gelirlerin etkin oranı"),
    ("V5", "Belediyeye arsa değer artışından pay (değer artış payı, harcamalara katılma payı)", "vergi / imar",
     "şehir (karar) + semt (harcama)",
     "H: payın bir kısmı mahalle bütçesine (park, kreş, okul yolu)",
     "H: semt donatısı (lise, sağlık, pazar yeri) bu gelirle", "K/U: plan değişikliği, değerleme ve tahsil; gelirin ayrı hesapta tutulması",
     "V: bölge planında yoğunluk koridorları", "K: 3194 Ek md. 8 istisnalarının daraltılması (6306); gelirin donatıya ayrılması",
     "3194 s. İmar Kanunu Ek md. 8 (%90 DAP) [D, Rapor 06]; 2464 s. Belediye Gelirleri Kanunu harcamalara katılma payları",
     "Kanun (istisna), yönetmelik, meclis kararı", "DAP tahsilatı (bugün bütçede ayrı görünmüyor [DY]); donatı açığı"),
    ("T1", "Karma kullanımlı imar: konut alanında zemin kat dükkân ve atölyeye kendiliğinden izin", "ticaret / imar",
     "ülke (kural) + şehir (plan)",
     "H: zemin kat dükkânı, atölye, kreş (gürültüsüz kullanımlar listesi)", "H: çarşı ve semt merkezi",
     "K: plan notu; otopark yükünün küçük işyerinden kaldırılması", "—",
     "K: PAİY md. 19/1-f-1'de meclis 'yol boyu ticaret' kararı ve otopark şartının yerine izinli kullanım listesi",
     "PAİY md. 19/1-f-1 (meclis kararı + otopark şartı) [D]; MPYY md. 21/10 [D]", "Yönetmelik",
     "Zemin kat konut dışı birim / 1.000 kişi; boş dükkân oranı"),
    ("T2", "Ruhsat ve izin sadeleştirme (beyan esası, tek pencere, kademeli denetim)", "ticaret", "şehir",
     "—", "U: semt hizmet binasında tek pencere", "U: ruhsat, yapı kullanma izni, itfaiye raporu tek süreçte",
     "—", "K: işyeri ruhsatı ve otopark yönetmeliklerinde küçük işyeri istisnası",
     "İşyeri Açma ve Çalışma Ruhsatlarına İlişkin Yönetmelik (2005/9207): sıhhi işyerinde aynı gün, 2.–3. sınıf gayrisıhhide 5 gün [D]",
     "Yönetmelik, belediye iş akışı", "Başvurudan açılışa geçen gün (ölçülmüyor [DY]); OECD PMR idari yük"),
    ("T3", "Açık pazarlar ve üretici pazarları", "ticaret / yeterlilik", "semt",
     "H: haftalık küçük üretici tezgâhı (mahalle meydanı)", "H: haftalık semt pazarı; üretici tezgâhı kotası",
     "K/U: pazar yeri planı, işgaliye ve yer tahsisi; toptancı hali bağlantısı", "V: bölge üretici kayıtları",
     "K: üretici satışında belge ve kayıt kolaylığı",
     "5393 s. Belediye Kanunu (görev ve yetkiler); pazar yerleri yönetmeliği (künye doğrulanmadı [DY])", "Meclis kararı",
     "Pazar sayısı / 35 bin kişi; üretici tezgâhı payı; üretici–tüketici fiyat farkı"),
    ("T4", "Esnaf ortak alım ve hizmet kooperatifleri", "ticaret", "semt + şehir",
     "—", "H: ortak depo ve teslim noktası", "U: ortak alım, lojistik, dijital satış altyapısı",
     "U: bölge toptan alım birliği", "K: kooperatif mevzuatı; rekabet hukukunda ortak alım sınırları",
     "1163 s. Kooperatifler Kanunu; 5362 s. Esnaf ve Sanatkârlar Meslek Kuruluşları Kanunu", "İdari, gönüllü",
     "Esnaf kapanış/açılış oranı; geleneksel kanalın HTM payı"),
    ("T5", "Kayıt dışılığı azaltan sade vergi ve prim rejimi", "ticaret / vergi", "ülke",
     "—", "V: semt vergi ve SGK danışma noktası", "—", "—",
     "K: basit usul ve götürü rejimin sadeleştirilmesi; ilk yıl prim indirimi; e-belge",
     "193 s. GVK md. 46–48 (basit usul); 5510 s. Kanun", "Kanun",
     "Kayıt dışı istihdam oranı (2025: %25,5; tarım dışı %16,4)"),
    ("T6", "Perakende fiyat kontrolleri ve giriş engellerinin gözden geçirilmesi", "ticaret", "ülke",
     "—", "—", "V: belediye fiyat tarifeleri envanteri", "—",
     "K: OECD PMR'de en kısıtlayıcı çıkan alanların (fiyat kontrolü, idari yük) gözden geçirilmesi",
     "OECD PMR 2023 (genel PMR 38/38) [D]", "Kanun ve yönetmelik", "OECD PMR puanı"),
    ("K1", "Kooperatif konut ve arsa vakfı (üst hakkı)", "konut", "şehir (arsa) + semt (proje)",
     "H: ada ölçeğinde kooperatif (40–100 konut)", "U: semt ölçeğinde kooperatif birliği; ortak avlu ve dükkân",
     "K/U: kamu arsası tahsisi, üst hakkı, maliyet kirası", "—",
     "K: 1163 Ek md. 6 düzeltmesi; endeksli aile konut kredisi",
     "1163 s. Kanun; Rapor 06 F3 [D]", "Yönetmelik, meclis kararı",
     "Ev sahipliği (2025: %56,9); kira yükü; kooperatif konut payı"),
    ("G1", "Negatif gelir vergisi ve temel gelir tartışması", "gelir", "ülke",
     "V: başvuru ve kayıt yardımı (muhtarlık)", "—", "—", "—",
     "K: finansman, eşik ve azalma oranı; mevcut yardımlarla birleştirme",
     "Bugün yok; dağınık sosyal yardımlar (SYDV, 3294 s. Kanun)", "Kanun",
     "Yoksulluk oranı (medyan %60: 2025'te %23,4); yardım kapsamı"),
    ("G2", "Taban gelirlerin kurala bağlanması (asgari ücret, en düşük emekli aylığı, memur tabanı)", "gelir", "ülke",
     "—", "—", "—", "—", "K: taban gelirlerin ortanca ücrete ya da sepet maliyetine bağlanması (endeks kuralı)",
     "4857 s. İş Kanunu md. 39; 5510 s. Kanun; toplu sözleşme", "Kanun",
     "Taban gelir / açlık sınırı; taban gelir / ortanca ücret"),
    ("G3", "Atıl işgücünü işe bağlama: semt istihdam ve mesleki eğitim merkezi", "gelir / işsizlik", "semt",
     "V: mahallede iş arayan ve bakım yükü olan kadın kaydı", "H: semt istihdam ofisi, çıraklık, kreş bağlantısı",
     "U: OSB ve esnafla eşleştirme", "V: bölge işgücü talep tahmini", "K: İŞKUR programlarının yerelleştirilmesi",
     "4904 s. İŞKUR Kanunu; 3308 s. Mesleki Eğitim Kanunu", "İdari",
     "Atıl işgücü oranı (2025: %29,7); kadın işgücüne katılımı"),
    ("Y1", "Kısa tedarik zinciri: üretici kooperatifi, doğrudan satış, hal kaydı", "yeterlilik", "bölge + şehir",
     "H: teslim noktası, abonelik sepeti", "H: semt pazarı üretici tezgâhı", "U: belediye hali ve soğuk depo",
     "U: tarım kuşağı, üretici kooperatifi, lisanslı depo", "K: 5957 s. Hal Kanunu'nda üreticinin doğrudan satışının kolaylaştırılması",
     "5957 s. Hal Kanunu [D, PDF]", "Yönetmelik", "Üretici–market fiyat farkı; hal dışı satış payı"),
    ("Y2", "Stratejik ürünlerde yeterlilik (yağlı tohum, baklagil, yem) ve havza üretim planlaması", "yeterlilik", "bölge + ülke",
     "—", "—", "—", "U: havza planı, sözleşmeli üretim, sulama", "K: destekleme ve planlama (2027 üretim yılından itibaren izne bağlı)",
     "Tarımsal üretim planlaması yönetmeliği (2023) [İ, Rapor 19]", "İdari",
     "Yeterlilik derecesi: soya %4, ayçiçeği %72, mısır %73 (son yıllar)"),
]
kad = pd.DataFrame(satirlar, columns=K)
kad.to_csv(SON / "ekonomi_kademe.csv", index=False, encoding="utf-8")
print(f"\n-> ekonomi_kademe.csv {kad.shape}")

# ----------------------------------------------------------------------------- 3. seçenekler: kanıt, etki, maliyet, yan etki
S = ["kod", "secenek", "kanit_duzeyi", "kanit", "beklenen_etki", "maliyet_veya_hasilat", "yan_etkiler", "yukunu_tasiyan",
     "fayda_goren", "belirsizlik"]
v4_kalem = vh.loc[[k for k in vh.index if "Geçici md. 67" in k or "temettü" in k or "KVK 5/1-d" in k or "86/1-c" in k],
                  "milyar_tl_2025"].sum()
secenek = [
    ("V1", "Arsa değer vergisi", "Orta–güçlü (teori ve ülke deneyimi); Türkiye'de ölçülmedi",
     "Taşınmaz vergisi büyümeye en az zarar veren vergiler arasında (OECD, Arnold vd. 2011) [İ]. Türkiye'de taşınmaz vergisi "
     "GSYH'nin %0,10'u, OECD ortalaması %0,95 (2023–24) [D]. Arsa vergisi 2025'te 12,8 mlr TL, GSYH'nin %0,02'si [D/H].",
     f"GSYH'nin %0,5'i kadar AVD, genel KDV oranını %20'den %{genel_yeni} düzeyine indirmeye yeter (statik) [H]. Dağılım tasarıma bağlı: "
     f"yalnız konut arsası vergilenirse en yoksul %20'nin yükü gelirin %{tr(sen.S3A_avd_konut_arsasi_net_gelire_pct[0], 2)} artar; "
     f"işletme arsası dahil ve alt iki dilim muafsa %{tr(-sen.S3C_avd_muafiyetli_net_gelire_pct[0], 2)} azalır [H].",
     f"Hasılat ≈ {tr(0.005 * GSYH, 0)} mlr TL/yıl (kişi başı ≈ {tr(avd_kisi, 0)} TL). Değerleme altyapısı maliyeti bilinmiyor [DY].",
     "Arsa fiyatları vergi kadar düşer (kapitalizasyon): bugünkü sahipler bir kerelik servet kaybı yaşar. Geliri düşük ev sahibi "
     "emeklilerde nakit sıkışıklığı. Değerleme hatası ve itiraz yükü. Tarım arazisine yanlış uygulanırsa çiftçiye yük.",
     "Arsa ve arazi sahipleri, özellikle boş ve değeri artan kent arsası", "Tüketiciler (KDV indirimiyle), kiracılar, yeni alıcılar",
     "Yansıma ve kapitalizasyonun hızı; değerleme kalitesi; siyasi uygulanabilirlik"),
    ("V2", "Dolaylı vergiden doğrudan vergiye kayış", "Orta",
     f"KDV ve ÖTV yükü gelire oranla en yoksul %20'de %{tr(temel.dolayli_gelire_pct[0])}, en zengin %20'de "
     f"%{tr(temel.dolayli_gelire_pct[4])} (2025, statik) [H]. Mal ve hizmet vergilerinin toplam vergideki payı Türkiye'de %43,6 "
     "(2024), OECD'de %31,2 (2023); kişisel gelir vergisi %14,7'ye karşı %23,7 [D].",
     "Genel KDV oranında 2 puan indirim hanehalkı yükünü 145 mlr TL azaltır; kazancın %8'i en yoksul %20'ye gider [H]. "
     "Aynı tutar gelir vergisinden telafi edilirse yük üst dilimlere kayar.",
     "Gelir-nötr tasarlanabilir; idari maliyet gelir vergisinde daha yüksek.",
     "Gelir vergisi beyanı kayıt dışılığa daha açık; çalışma ve tasarruf güdüsüne etki; sermayenin yurt dışına kayması. "
     "Tüketimle ölçülen ömür boyu yük, yıllık gelirle ölçülenden daha az geriye doğrudur (Poterba 1989) [İ].",
     "Yüksek gelirli ücretliler ve sermaye geliri sahipleri", "Gelirinin tamamını tüketen haneler, emekliler, asgari ücretliler",
     "Vergi idaresinin kapasitesi; kayıt dışı tepkinin büyüklüğü"),
    ("V3", "Temel gıdada KDV'nin sıfırlanması", "Orta (hesap güçlü, yansıma belirsiz)",
     f"Gıda KDV'si zaten %1 [D]. Sıfırlamanın bütçe maliyeti ≈ {tr(s2_maliyet, 0)} mlr TL (GSYH %0,08); en yoksul %20'nin "
     f"kazançtaki payı %{tr(oz.loc[s2, 'dilim1_payi_pct'], 0)} [H].",
     f"En yoksul %20'nin geliri %{tr(-s2_dilim1, 2)} artar. Aynı bütçe yalnız en yoksul %20'ye nakit verilseydi %{tr(-s5_dilim1, 2)} "
     f"artardı (≈{tr(s5_dilim1 / s2_dilim1, 1)} kat) [H].",
     f"≈ {tr(s2_maliyet, 0)} mlr TL/yıl vergi kaybı.",
     "İndirimin fiyata tam yansımayabilir (perakende yoğunlaşması CR4 %59). Sıfır oranda üreticinin girdi KDV'si iade "
     "gerektirir; iade gecikirse maliyet artar. Zenginler de mutlak olarak daha çok kazanır.",
     "Bütçe (başka harcama ya da vergi)", "Bütün tüketiciler; görece en çok alt dilimler",
     "Fiyata yansıma oranı (Türkiye için ölçüm yok [DY])"),
    ("V4", "Vergi tabanının genişletilmesi ve istisnaların kaldırılması", "Güçlü (tutarlar resmî rapordan)",
     f"Vergi harcaması 2025'te 3.170 mlr TL; vergi tahsilatının %28,7'si [D]. Gelir vergisinde harcama tahsilatın "
     f"%{tr(vht.loc['Gelir vergisi', 'harcama_tahsilat_orani_pct'])}'si; bunun %57'si asgari ücret istisnası [D/H]. "
     "Ücrette etkin oran asgari ücretin 10 katında %25; mevduat faizinde %10–17,5 (nominal), hisse satış kazancında %0 [H/D].",
     f"Sermaye geliriyle ilgili dört kalem (Geçici md. 67, temettü, yatırım fonu KV istisnası, toplanmayan menkul sermaye iradı) "
     f"2025'te ≈{tr(v4_kalem, 0)} mlr TL [D]. Daraltılırsa hasılatın bir kısmı geri gelir; davranış tepkisi hesaplanmadı.",
     "Hasılat artışı; idari maliyet düşük (tanımlı kalemler).",
     "Sermaye piyasası ve yatırım teşviki kaygısı; fonların yurt dışına ya da altına kayması; geçiş döneminde belirsizlik. "
     "Asgari ücret istisnasının kaldırılması en düşük ücretliye yük bindirir (öneri dışı).",
     "Sermaye geliri ve istisnadan yararlanan kurumlar", "Bütçe; dolaylı vergi indirimi için alan",
     "Sermaye hareketliliği; istisnaların yatırıma gerçek katkısı ölçülmemiş [DY]"),
    ("V5", "Belediyeye arsa değer artışından pay", "Orta (literatür) / zayıf (Türkiye tahsilat verisi yok)",
     "3194 Ek md. 8 plan değişikliğiyle oluşan artışın %90'ını alıyor; 6306 alanları ve riskli yapı parselleri istisna [D, Rapor 06]. "
     f"Belediyelerin 2025 bütçesinde harcamalara katılma payları {tr(yer.harcamalara_katilma_paylari)} mlr TL; DAP ayrı görünmüyor [DY].",
     "İmar kararının yarattığı rantın kamuya dönmesi; donatı finansmanı; dikey dönüşümün gizli teşvikinin nötrleşmesi (Rapor 06).",
     "Gelir belirsiz; değerleme ve denetim maliyeti.",
     "Plan değişikliği taleplerini ve dönüşümü yavaşlatabilir; değerleme keyfîliği ve yolsuzluk riski; istisnalar kaçış yolu olur.",
     "Plan değişikliğinden yararlanan malik ve geliştirici", "Mahalle ve semt donatısı; yerel bütçe",
     "Tahsilat verisi yok; uygulama tutarlılığı"),
    ("T1", "Karma kullanımlı imar", "Orta (uluslararası örnek; Türkiye'de nedensel kanıt yok)",
     "PAİY md. 19/1-f-1: konut alanında zemin kat dükkânı ancak meclisin 'yol boyu ticaret' kararı ve otopark şartıyla [D]. "
     "Japonya'nın kümülatif imarı küçük dükkânlı alçak doku üretiyor [İ]. Rapor 10–12: erişim (E) ekseni mahallede ölçüldü, "
     "sağlıkla ilişkisi doğrulanmadı.",
     "Mahalle içinde dükkân ve atölye arzı; kira rekabeti; yürüme mesafesinde ihtiyaç. Sayısal etki ölçülmedi.",
     "Kamuya doğrudan maliyeti düşük (yönetmelik).",
     "Gürültü, koku, teslimat trafiği; komşu şikâyetleri; zemin kat konut arzının azalması; bazı caddelerde kira artışı.",
     "Sessiz konut sokağı isteyen sakinler", "Küçük esnaf, yürüyerek alışveriş yapanlar, yaşlılar",
     "Talep yeterli mi (model mahallede zemin kat birimi fazla çıktı, Rapor 12)"),
    ("T2", "Ruhsat sadeleştirme", "Orta",
     "Kâğıt üstünde ruhsat hızlı: sıhhi işyerinde aynı gün [D]. Asıl engel imar, otopark, yapı kullanma izni ve denetim. "
     "OECD PMR 2023: idari ve düzenleyici yük 2,93 (OECD 1,74), 38 üye içinde en kısıtlayıcı [D]. B-READY 2025 'işyeri yeri' 72,3 [D].",
     "Giriş maliyetinin düşmesi; kayıt içinde kalma.", "Düşük; tek pencere için yazılım ve personel.",
     "Denetim zayıflarsa yangın ve yapı güvenliği riski; haksız rekabet şikâyeti.", "Denetim yükü artan belediye",
     "Yeni girişimci ve esnaf", "Başvurudan açılışa süre Türkiye'de ölçülmüyor [DY]"),
    ("T3", "Açık pazarlar ve üretici pazarları", "Zayıf–orta",
     "TZOB Aralık 2025: havuç markette üreticinin 4,2 katı, mandalina 3,5, kabak ve yeşil soğan 3,4 [İ]. "
     "Organize perakendenin HTM payı 2019'da %47, 2021'de %54; ilk 4 zincirin payı %59 [D].",
     "Üreticiye daha yüksek, tüketiciye daha düşük fiyat beklenir; pazar ile market fiyatının sistematik karşılaştırması bulunamadı [DY].",
     "Belediye için yer, temizlik ve denetim maliyeti; işgaliye geliri.",
     "Trafik ve temizlik yükü; aracıların pazarda da baskın olması; gıda güvenliği denetimi.",
     "Pazar çevresindeki sakinler; zincir perakende", "Küçük üretici, düşük gelirli tüketici",
     "Fiyat farkının ne kadarı lojistik ve fire, ne kadarı pazar gücü?"),
    ("T4", "Esnaf ortak alım ve hizmet kooperatifleri", "Zayıf",
     "TESK'e kayıtlı 2,28 milyon esnaf (Eylül 2026); 2025'te 323 bin açılış, 120 bin kapanış [D]. Zincir mağaza sayısı hızla arttı "
     "(A101: 2011'de 1.287, 2021'de 11.227) [D].",
     "Satın alma gücü ve lojistikte ölçek; zincirlerle fiyat rekabeti. Türkiye'de ölçülmüş etki yok.",
     "Gönüllü; kuruluş ve yönetim maliyeti üyelerde.",
     "Kooperatif yönetim sorunları; ortak fiyatlamaya kayarsa rekabet hukuku ihlali.", "Üyeler", "Küçük esnaf",
     "Başarılı örnek verisi bulunamadı [DY]"),
    ("T5", "Kayıt dışılığı azaltan sade rejim", "Orta",
     "Kayıt dışı istihdam 2025'te %25,5; tarımda %81,9, tarım dışında %16,4 [D]. Kayıt dışı ekonomi GSYH'nin %24–31'i (2020) [D]. "
     "Firmaların %50'si kayıt dışı rakiple yarışıyor (2019) [D].",
     "Kayıtlı rekabet; vergi tabanı genişler; işçinin emeklilik hakkı oluşur.", "Kısa vadede prim ve vergi kaybı olabilir.",
     "Basit usul kötüye kullanılabilir (büyük işletmenin bölünmesi).", "Bütçe (kısa vade)", "Kayıt dışı çalışan, dürüst esnaf",
     "Davranış tepkisi"),
    ("T6", "Fiyat kontrolleri ve giriş engellerinin gözden geçirilmesi", "Orta",
     "OECD PMR 2023: genel PMR 2,52 (OECD 1,35); perakende fiyat kontrolleri 3,89 (OECD 1,11), ikisinde de 38/38 [H/D]. "
     "Perakende dağıtımın kendi kuralları OECD ortalamasında (1,00) [D].",
     "Rekabet ve giriş artar; uzun vadede verimlilik.", "Düşük.",
     "Kısa vadede bazı fiyatlarda artış; korunan kesimlerin tepkisi.", "Korunan sektörler", "Tüketici ve yeni girişimci",
     "Hangi kontrolün hangi fiyatı etkilediği ayrıştırılmadı"),
    ("K1", "Kooperatif konut ve arsa vakfı", "Orta (Rapor 06 modeli; Viyana, Batıkent)",
     "Rapor 06 (M6): 124 m² aile konutu kat karşılığında 5,28 mn TL; kooperatifte 4,40 (−%17), kamu arsasıyla 3,87 (−%27), "
     "arsa vakfı ve üst hakkıyla 3,34 mn TL (−%37) [H]. 100 m² kira 2026'da net asgari ücretin %98'i [H].",
     "Kira yükünün ve konut edinme maliyetinin düşmesi; ev sahipliğinin artması (2025: %56,9).",
     "Kamu arsasının fırsat maliyeti; aile konut kredisinde kamu maliyeti kredinin %22,8'i (Rapor 06).",
     "Geçmişte kooperatif iflasları ve gecikmeleri; arsa tahsisinde kayırma; talep desteği fiyatı şişirebilir.",
     "Kamu (arsa geliri), mevcut ev sahipleri (fiyat baskısı)", "Kiracılar, genç aileler", "Kooperatif yönetişimi"),
    ("G1", "Negatif gelir vergisi ve temel gelir", "Orta (deneyler var; Türkiye'de yok)",
     f"Evrensel temel gelirin GSYH'ye oranı: kişi başı açlık sınırının yarısı verilirse %{tr(tg.gsyh_pct.iloc[1])}, tamamı "
     f"verilirse %{tr(tg.gsyh_pct.iloc[0])} (2025) [H]. Bugünkü sosyal yardımların (çoğu emekli aylığı) GSYH'ye oranı %{tr(100 * D62 / GSYH)} [D/H]. "
     "Finlandiya deneyi (2017–18): istihdama etki küçük, refah algısı arttı [İ].",
     "NGV gelir eşiğinin altına doğru azalan oranla ödeme yapar; evrensel temel gelirden ucuzdur. Damgalanmayı ve "
     "'çalışırsam yardımı kaybederim' tuzağını azaltır.",
     "Evrensel sürüm çok pahalı; hedefli NGV için hane gelir kaydı gerekir.",
     "Çalışma güdüsü (azalma oranına bağlı); finansman için vergi artışı; enflasyon; mevcut yardımlarla çakışma.",
     "Vergi mükellefleri", "Gelirsiz ve düşük gelirliler, işsizler, kayıt dışı çalışanlar",
     "Türkiye'de pilot yok; davranış tepkisi bilinmiyor"),
    ("G2", "Taban gelirlerin kurala bağlanması", "Orta",
     "Eylül 2026: net asgari ücret açlık sınırının %74'ü, en düşük emekli aylığı %62'si, ortanca net ücret (tahmin) %79'u [H]. "
     "Ortanca ücret asgari ücretin ≈1,1 katı (2022) [H/V]: ücret dağılımı asgari ücrette yığılıyor (OECD D5/D1 1,42) [D].",
     "Öngörülebilirlik; yılda iki kez yapılan pazarlığın yerini kural alır.",
     "Endeksleme kuralı enflasyonda bütçe ve işveren maliyetini otomatik artırır.",
     "Asgari ücretin ortancaya yakınlığı kayıt dışılığı ve 'asgari ücretli bordro'yu artırabilir.",
     "İşveren, bütçe", "Asgari ücretli, emekli, memur", "Kuralın seviyesi"),
    ("G3", "Atıl işgücünü işe bağlama", "Orta (meta-analiz: eğitim programlarının etkisi uzun vadede büyür; Card, Kluve ve Weber 2018) [İ]",
     f"İşsizlik oranı 2025'te %{tr(isg.issizlik)}, ama atıl işgücü %{tr(isg.atil_isgucu)}; fark iş aramayan ama çalışmaya hazır olanlar "
     "ve daha çok çalışmak isteyenler [D].",
     "Atıl kalan ≈10 milyon kişinin bir kısmının kayıtlı işe geçmesi; hane gelirinin artması.",
     "Program maliyeti; kreş ve ulaşım desteği.", "Etkisiz programlara kaynak; yerel kayırmacılık.", "Bütçe",
     "İşsizler, ev kadınları, gençler", "Yerel programların etkisi ölçülmemiş"),
    ("Y1", "Kısa tedarik zinciri", "Zayıf–orta",
     "Üretici–market fiyat farkı birçok sebze ve meyvede 3–4 kat (TZOB, Aralık 2025) [İ]. Fiyat dalgalanması yüksek (Rapor 19).",
     "Üretici payının artması; fire ve israfın azalması (Rapor 19).", "Soğuk depo, teslim noktası, kooperatif kuruluşu.",
     "Ölçek ekonomisinin kaybı; küçük üreticide gıda güvenliği denetimi zorluğu.", "Aracılar", "Üretici ve tüketici",
     "Farkın ne kadarının kapanabileceği bilinmiyor"),
    ("Y2", "Stratejik ürünlerde yeterlilik", "Güçlü (yeterlilik verisi) / orta (çözüm)",
     "Yeterlilik derecesi: soya %4, kolza değişken, ayçiçeği %72, mısır %73, pirinç %72, kırmızı mercimek %91; buğday 2024/25'te %104; "
     "sebze %109, tavuk eti %115, yumurta %117 [D/İ/H].",
     "Yağlı tohum ve yemde dışa bağımlılığın azalması; fiyat şoklarına dayanıklılık.",
     "Destekleme ödemesi; sulama yatırımı; su kısıtı.",
     "Her üründe tam yeterlilik verimsizdir (iklim ve su); karşılaştırmalı üstünlükten vazgeçmenin maliyeti; susuz bölgede su stresi.",
     "Bütçe, su kaynakları", "Çiftçi, tüketici (istikrar)", "İklim ve su kısıtı"),
]
sec = pd.DataFrame(secenek, columns=S)
sec.to_csv(SON / "ekonomi_secenekler.csv", index=False, encoding="utf-8")
print(f"-> ekonomi_secenekler.csv {sec.shape}")
print(f"-> ekonomi_kademe_parametre.csv {par.shape}")
