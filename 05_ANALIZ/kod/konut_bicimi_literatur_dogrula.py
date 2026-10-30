"""
Konut biçimi literatürü — künye, özet ve bulgu doğrulaması (Faz 5 · konut biçimi kanıt taraması)
================================================================================================
Soru: konutun biçimi (yüksek/alçak blok, müstakil ve sıra ev, konut büyüklüğü ve kalabalık, yoğunluk,
sokak ağı bağlantılılığı, avlu ve bahçe, mülkiyet/kira) ile inovasyon-üretkenlik, sağlık, sosyal sermaye,
güvenlik ve aile-çocuk sonuçları arasındaki ilişki.

Web araması kullanılmadan, anahtarsız açık servislerle (urllib varsayılan başlıklarıyla; tarayıcı taklidi yok,
e-posta gönderilmez):
  1. Crossref REST API (api.crossref.org/works/<doi>): başlık, dergi, yıl, cilt, sayı, sayfa, yazarlar. Zorunlu.
  2. NCBI E-utilities (PubMed): DOI'den PMID, PMID'den özet. Başlık örtüşmesi < %50 ise kayıt atılır.
  3. Crossref "abstract" alanı.
  4. Europe PMC REST (ebi.ac.uk/europepmc): DOI eşleşmesi denetlenir.
  5. Semantic Scholar Graph API: yalnız "abstract" alanı kabul edilir (otomatik TLDR kabul edilmez).
  6. OpenAlex (api.openalex.org): "abstract_inverted_index" sözcük sırasıyla yeniden kurulur.
  7. Yalnız yayımlanmış sürümün özeti hiçbir yerde yoksa: aynı çalışmanın çalışma makalesi ya da yeniden basım
     sürümü (OpenAlex). Bu durumda bulgu en çok [K] olur.

Doğrulama kuralı (bu betik uygular):
  Her kaynak için bulgu ve etki büyüklüğünün özetteki İngilizce karşılığı "kanit" dizeleri olarak yazıldı.
  - Bütün dizeler yayımlanmış sürümün özetinde geçiyorsa             -> D
  - Yalnız çalışma makalesi / yeniden basım özetinde geçiyorsa        -> K (not düşülür)
  - Özet yok ya da dizeler geçmiyor, ama künye Crossref'te doğrulandı -> K
  - Künye de doğrulanamadıysa                                         -> DY
  İstisna: Sandler 2017 — ICPSR veri deposu kaydı yayımlanmış özeti künyesiyle aynen aktarıyor; künye dizesi de
  denetlenir, tutarsa D sayılır.

Çıktı : 03_VERI/ham/konut_bicimi_literatur/{crossref,pubmed,europepmc,semanticscholar,openalex}/ (ham yanıtlar, önbellek)
        03_VERI/ham/konut_bicimi_literatur/kunye_ozet.csv   künye + özet + dize denetimi (denetim tablosu)
        02_LITERATUR/konut_bicimi_kaynakca.csv               kaynakça (tema, künye, bulgu, etki, kanıt düzeyi, doğrulama)
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/konut_bicimi_literatur_dogrula.py
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "konut_bicimi_literatur"
for d in ("crossref", "pubmed", "europepmc", "semanticscholar", "openalex"):
    (HAM / d).mkdir(parents=True, exist_ok=True)

TEMA = {
    "inovasyon": "1-İnovasyon ve üretkenlik",
    "saglik": "2-Sağlık",
    "sosyal": "3-Toplumsal güven ve sosyal sermaye",
    "guvenlik": "4-Güvenlik ve suç",
    "aile": "5-Aile ve çocuk",
}

# Her kaynak: tema, kısa ad, DOI, (isteğe bağlı) alt sürüm, kanıt dizeleri, tasarım, bulgu, etki, kanıt düzeyi (G/O/Z).
# Kanıt dizeleri özetteki İngilizce ifadelerdir; küçük harfe çevrilip boşluk, tırnak ve tire biçimi eşitlenerek aranır.
# Türkçe alanlar insan okuması içindir; sayılar yalnız kanıt dizesi tutan özetten alınmıştır.
K = [
    # ---------------------------------------------------------------- 1. İnovasyon ve üretkenlik
    dict(tema="inovasyon", ad="Roche 2020", doi="10.1162/rest_a_00866",
         kanit=["street network density may explain regional innovation differentials beyond the traditional location externalities",
                "instruments based on historic city planning"],
         tasarim="Kesitsel; ABD'deki bütün nüfus blok grupları; işe gidiş bölgesi sabit etkileri; tarihî şehir planlarından araç değişken (IV)",
         bulgu="Sokak ağı yoğunluğu, bilinen yığılma etkilerinin ötesinde bölgeler arası inovasyon farkını açıklayabiliyor.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="inovasyon", ad="Liu, Rosenthal ve Strange 2018", doi="10.1016/j.jue.2018.04.001",
         kanit=["high productivity companies locate higher up", "10.7% increase in rent", "roughly 3,500 workers"],
         tasarim="Ofis binalarında kat düzeyinde kira verisi (ABD); hedonik kira modeli",
         bulgu="Yüksek verimli şirketler üst katlarda, daha az verimli ofisler altta, perakende zeminde. Dikey kira eğimi büyük ve monoton değil.",
         etki="Posta kodu istihdamı iki katına çıkınca kira +%10,7; bir kat yukarı çıkmak, posta koduna ≈3.500 çalışan eklemekle aynı kira etkisi", duzey="O"),
    dict(tema="inovasyon", ad="Carlino ve Kerr 2015", doi="10.1016/B978-0-444-59517-1.00006-4",
         alt=("10.3386/w20367", "NBER çalışma makalesi w20367"), yazar="Carlino G, Kerr WR",
         kanit=["innovative activity tends to be more concentrated than industrial activity", "size, industrial diversity"],
         tasarim="El kitabı bölümü; derleme",
         bulgu="İnovasyon, sanayi faaliyetinden daha yoğunlaşmış. Şehir büyüklüğü ve sanayi çeşitliliği inovasyonla bağlantılı.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="inovasyon", ad="Carlino, Chatterjee ve Hunt 2007", doi="10.1016/j.jue.2006.08.003",
         alt=("10.21799/frbp.wp.2006.14", "Philadelphia Fed çalışma makalesi 06-14"),
         kanit=["20 percent higher", "about 2,200 jobs per square mile"],
         tasarim="ABD metropol alanları; patent yoğunluğu regresyonu",
         bulgu="Kişi başı patent, metropolün kentleşmiş kesimindeki istihdam yoğunluğuyla artıyor; bir yoğunlukta zirve yapıyor.",
         etki="İstihdam yoğunluğu iki kat → kişi başı patent +%20; zirve ≈2.200 iş/mil² (≈850 iş/km²)", duzey="O"),
    dict(tema="inovasyon", ad="Ahlfeldt ve Pietrostefani 2019", doi="10.1016/j.jue.2019.04.006",
         kanit=["202 estimates of density elasticities from 102 studies", "$140 increase in wage", "$243 increase in rent",
                "real wage net of taxes of $171", "amenity effect of $106", "external welfare effect of $29", "scarcity rent"],
         tasarim="Sentez ve meta-analiz: 15 sonuç kategorisi, 102 çalışma, 202 esneklik (+16 yeni tahmin)",
         bulgu="Yoğunluk ücreti ve verimliliği artırıyor, ama kirayı daha çok artırıyor. Kiracılar ve ilk kez ev alacaklar zarar görüyor.",
         etki="Yoğunluk +%10 → kişi başı yılda ücret +140 $, kira +243 $; vergi sonrası reel ücret −171 $; imkân etkisi +106 $; net dış refah +29 $", duzey="G"),
    dict(tema="inovasyon", ad="Ahlfeldt ve ark. 2015", doi="10.3982/ECTA10876",
         kanit=["exogenous variation from the city's division and reunification",
                "substantial and highly localized production and residential externalities"],
         tasarim="Doğal deney: Berlin'in bölünmesi ve birleşmesi (1936, 1986, 2006); binlerce blokta yapısal model",
         bulgu="Üretim ve konut dışsallıkları büyük ve çok yerel. Yığılmanın faydası blok ölçeğinde sönüyor.",
         etki="Özette sayı yok", duzey="G"),
    dict(tema="inovasyon", ad="Arzaghi ve Henderson 2008", doi="10.1111/j.1467-937X.2008.00499.x",
         kanit=["extremely rapid spatial decay in the benefits of more near neighbours", "capitalized into rents rather than wages"],
         tasarim="Manhattan reklam ajansları; ince coğrafi ölçekte ekonomik sayım verisi",
         bulgu="Yakın komşu ajans sayısı verimliliği güçlü artırıyor, ama fayda güney Manhattan'da bile mesafeyle çok hızlı sönüyor. Fayda ücretten çok kiraya yansıyor.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="inovasyon", ad="Catalini 2018", doi="10.1287/mnsc.2017.2798",
         kanit=["removal of asbestos", "colocation increases the likelihood of joint research by 3.5 times"],
         tasarim="Doğal deney: Paris Jussieu kampüsünde asbest temizliği yüzünden laboratuvarların yer değiştirmesi",
         bulgu="Aynı binada/yakında olmak ortak araştırmayı artırıyor; ayrılmak önceki işbirliğini bozmuyor ama konuları ayrıştırıyor.",
         etki="Yan yana yerleşme → ortak araştırma olasılığı 3,5 kat", duzey="G"),
    dict(tema="inovasyon", ad="Hsieh ve Moretti 2019", doi="10.1257/mac.20170388",
         kanit=["stringent restrictions to new housing supply", "lowered aggregate us growth by 36 percent from 1964 to 2009"],
         tasarim="Uzamsal denge modeli; 220 metropol alanı",
         bulgu="New York ve San Francisco gibi yüksek verimli şehirlerdeki konut arzı kısıtları, işçilerin verimli yerlere erişimini sınırlıyor.",
         etki="Konut arzı kısıtları ABD toplam büyümesini 1964–2009'da %36 düşürdü (model tahmini)", duzey="O"),
    dict(tema="inovasyon", ad="Fallah, Partridge ve Olfert 2011", doi="10.1111/j.1435-5957.2010.00330.x",
         kanit=["higher levels of urban sprawl are negatively associated with average labour productivity",
                "instrumental variables"],
         tasarim="ABD metropol alanları; yoğunluk dağılımına dayalı yayılma ölçüsü; EKK ve araç değişken",
         bulgu="Yayılma arttıkça ortalama emek verimliliği düşüyor; aynı sektör ve meslek içinde de.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="inovasyon", ad="Hamidi ve Zandiatashbar 2019", doi="10.1177/0042098018767002",
         kanit=["innovative firms tend to locate more in census tracts that are less compact",
                "regional compactness positively and significantly affects the number of innovative firms"],
         tasarim="Çok düzeyli model; ABD nüfus sayım bölgeleri ve metropoller (kesitsel)",
         bulgu="Mahalle ölçeğinde inovatif firmalar daha az kompakt bölgelerde (yüksek arsa değeri yüzünden); bölge ölçeğinde kompaktlık inovatif firma sayısını artırıyor.",
         etki="Özette sayı yok", duzey="Z"),
    dict(tema="inovasyon", ad="Duranton ve Puga 2020", doi="10.1257/jep.34.3.3",
         kanit=["density boosts productivity and innovation", "density is also synonymous with crowding"],
         tasarim="Derleme",
         bulgu="Yoğunluk verimliliği ve inovasyonu artırıyor, erişimi iyileştiriyor, yolculuğu kısaltıyor; ama kalabalık getiriyor, yaşamayı ve dolaşmayı pahalılaştırıyor.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="inovasyon", ad="Bloom ve ark. 2015", doi="10.1093/qje/qju032",
         kanit=["randomly assigned", "13% performance increase", "quieter and more convenient working environment", "attrition rate halved",
                "promotion rate conditional on performance fell", "almost doubling to 22%"],
         tasarim="Randomize deney: Ctrip çağrı merkezi, 9 ay, gönüllüler arasında evden/ofisten çalışma",
         bulgu="Evden çalışma performansı artırdı, işten ayrılmayı yarıya indirdi, ama performansa göre terfi oranını düşürdü.",
         etki="Performans +%13 (dakika +%9, dakika başına çağrı +%4); yeniden seçimle kazanç ≈%22", duzey="G"),
    dict(tema="inovasyon", ad="Lin, Frey ve Wu 2023", doi="10.1038/s41586-023-06767-1",
         kanit=["20 million research articles and 4 million patent applications",
                "consistently less likely to make breakthrough discoveries relative to their on-site counterparts"],
         tasarim="Gözlemsel; 20 milyon makale ve 4 milyon patent başvurusu (yarım yüzyıl)",
         bulgu="Uzaktan (farklı şehirlerden) çalışan ekipler her alanda, dönemde ve ekip büyüklüğünde çığır açan buluşu daha az yapıyor.",
         etki="Özette sayı yok", duzey="O"),

    # ---------------------------------------------------------------- 2. Sağlık
    dict(tema="saglik", ad="Gifford 2007", doi="10.3763/asre.2007.5002",
         kanit=["not optimal for children", "helping behavior is less", "crime and fear of crime are greater",
                "independently account for some suicides", "ability to choose a housing form"],
         tasarim="Anlatı derlemesi",
         bulgu="Yüksek kat çoğu insan için daha az tatmin edici; çocuklar için uygun değil; ilişkiler daha kişiliksiz, yardımlaşma daha az; suç ve suç korkusu daha fazla; bazı intiharları bağımsız açıklayabilir. Sonuçlar gelir, mahalle, ebeveynlik, iç mekân yoğunluğu ve konut biçimini seçebilme gibi etkenlere bağlı.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="saglik", ad="Evans 2003", doi="10.1093/jurban/jtg063",
         kanit=["high-rise housing is inimical to the psychological well-being of women with young children",
                "elevate psychological distress but do not produce serious mental illness"],
         tasarim="Derleme",
         bulgu="Yüksek katlı konut küçük çocuklu kadınların ruh sağlığına aykırı. Oda başına kişi ve dış gürültü sıkıntıyı artırıyor, ama ağır ruhsal hastalık yapmıyor.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="saglik", ad="Barros ve ark. 2019", doi="10.1016/j.cities.2019.05.015",
         kanit=["23 empirical studies published between 1971 and 2016",
                "house type, floor level, as well as spaces intrinsic to high-rise residential buildings",
                "conceptual gaps and methodological inconsistencies"],
         tasarim="Sistematik derleme (PRISMA), 23 çalışma (1971–2016)",
         bulgu="Konut tipi, kat düzeyi ve ortak merdiven gibi alanlar sosyal iyi oluş ve ruh sağlığıyla ilişkili; ama kavram boşluğu ve yöntem tutarsızlığı çok.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="saglik", ad="Verhaeghe ve ark. 2016", doi="10.1007/s11524-016-0066-5",
         kanit=["6,102,820", "or 0.67", "or 1.04", "or 1.19", "refute one of the central ideas"],
         tasarim="Belçika 2001 nüfus sayımı + nüfus kaydı (N = 6.102.820); çok düzeyli lojistik regresyon",
         bulgu="Yüksek binada oturanların sağlığı ham karşılaştırmada kötü, ama fark sosyoekonomik ve demografik ayrışmadan geliyor. Bina içinde 6. kata kadar kat arttıkça sağlık hafifçe iyileşiyor.",
         etki="İyi öz-bildirimli sağlık, yüksek/alçak bina: ham OR 0,67 (0,67–0,68); düzeltilmiş OR 1,04 (1,03–1,05); 6. kat OR 1,19 (1,15–1,24)", duzey="O"),
    dict(tema="saglik", ad="Weich ve ark. 2002", doi="10.1192/bjp.180.5.428",
         kanit=["predominantly deck access (odds ratio=1.28, 95% ci 1.03-1.58", "(odds ratio=1.43, 95% ci 1.06-1.91"],
         tasarim="Kesitsel anket, Kuzey Londra'da iki seçim bölgesi, 1.887 kişi; yapılı çevre bağımsız gözlemcilerce puanlandı",
         bulgu="Sosyoekonomik durum, oturulan kat ve konut sorunları düzeltildikten sonra galeri (deck) erişimli ve 1969 sonrası yapılmış konut alanlarında depresyon daha yaygın.",
         etki="Galeri erişimli konut alanı → depresyon OR 1,28 (1,03–1,58); 1969 sonrası yapı OR 1,43 (1,06–1,91)", duzey="Z"),
    dict(tema="saglik", ad="Drennan ve ark. 2016", doi="10.1503/cmaj.150544",
         kanit=["7842 cases", "4.2% v. 2.6%", "survival was 0.9% above floor 16", "no survivors above the 25th floor"],
         tasarim="Geriye dönük gözlemsel kohort; Toronto, 2007–2012, konutta 7.842 hastane dışı kalp durması",
         bulgu="Yüksek katta kalp durmasında hayatta kalma daha düşük; ekibin hastaya ulaşma süresi uzuyor.",
         etki="Hayatta kalma: 3. katın altında %4,2, 3. kat ve üstünde %2,6; 16. kat üstünde %0,9; 25. kat üstünde hayatta kalan yok", duzey="O"),
    dict(tema="saglik", ad="Sarkar, Webster ve Gallacher 2017", doi="10.1016/S2542-5196(17)30119-5",
         kanit=["419 562", "1800 residential units per km2", "1·10, 1·07 to 1·14", "0·91, 0·90 to 0·93"],
         tasarim="Kesitsel; UK Biobank, 22 kent, 419.562 yetişkin; 1 km sokak ağı çevresinde konut yoğunluğu",
         bulgu="Konut yoğunluğu ile şişmanlık arasında ters U: seyrek banliyöde yoğunluk arttıkça şişmanlık artıyor, km²'de 1.800 konutun üstünde azalıyor.",
         etki="1.800 konut/km² altında +1.000 konut/km² → obezite OR 1,10 (1,07–1,14); üstünde OR 0,91 (0,90–0,93)", duzey="O"),
    dict(tema="saglik", ad="Sallis ve ark. 2016", doi="10.1016/S0140-6736(15)01284-2",
         kanit=["6822 adults", "1·006", "1·069", "1·146", "68 min/week to 89 min/week", "45-59%"],
         tasarim="Kesitsel, uluslararası (IPEN): 14 kent, 10 ülke, 6.822 yetişkin; ivmeölçerle ölçülen hareket",
         bulgu="Net konut yoğunluğu, kavşak yoğunluğu, toplu taşıma yoğunluğu ve park sayısı hareketle doğrusal ve pozitif ilişkili; karma kullanım ilişkisiz.",
         etki="exp(b): konut yoğunluğu 1,006; kavşak yoğunluğu 1,069; park sayısı 1,146. En elverişli ve en elverişsiz mahalle farkı haftada 68–89 dk (önerilen 150 dk'nın %45–59'u)", duzey="O"),
    dict(tema="saglik", ad="Ewing ve Cervero 2010", doi="10.1080/01944361003766766",
         kanit=["greater than 0.39",
                "walking is most strongly related to measures of land use diversity, intersection density, and the number of destinations within walking distance",
                "population and job densities to be only weakly associated with travel behavior"],
         tasarim="Meta-analiz (yapılı çevre ve yolculuk, 2009 sonuna kadar); öz-seçilimi denetleyen çalışma az",
         bulgu="Yürüme en çok arazi kullanım çeşitliliği, kavşak yoğunluğu ve yürüme mesafesindeki varış noktalarıyla ilişkili. Bunlar denetlenince nüfus ve iş yoğunluğunun etkisi zayıf.",
         etki="Hiçbir değişkenin ağırlıklı ortalama esnekliği mutlak değerce 0,39'u aşmıyor", duzey="O"),
    dict(tema="saglik", ad="Hajna ve ark. 2015", doi="10.1186/s12889-015-2082-x",
         kanit=["street connectivity, land use mix and residential density", "766 more steps per day (95 % credible interval 250, 1271)",
                "approximately 8 % of recommended daily steps"],
         tasarim="Sistematik derleme ve Bayesçi meta-analiz (6 çalışma, 4'ü havuzlandı; Avrupa ve Asya); adımsayar/ivmeölçer",
         bulgu="Sokak bağlantılılığı, karma kullanım ve konut yoğunluğu yüksek (yürünebilir) mahallede yetişkinler günde daha çok adım atıyor.",
         etki="Yürünebilirliği yüksek mahallede günde +766 adım (güvenilir aralık 250–1.271), önerilen günlük adımın ≈%8'i", duzey="O"),
    dict(tema="saglik", ad="Amerio ve ark. 2020", doi="10.3390/ijerph17165973",
         kanit=["8177 students", "apartments <60 m2", "1.31", "1.368", "2.253", "or = 4.28"],
         tasarim="Kesitsel web anketi; Milano, COVID-19 kapanması, 8.177 üniversite öğrencisi",
         bulgu="Küçük, manzarası kötü ve iç mekân kalitesi düşük konutta kapanma döneminde orta-ağır depresif belirti riski daha yüksek.",
         etki="<60 m² daire 1,31; kötü manzara 1,368; kötü iç mekân 2,253 kat; evden çalışmada performans düşüşü bildirenlerde depresyon OR 4,28 (özetteki güven aralıkları biçim hatalı)", duzey="Z"),
    dict(tema="saglik", ad="Foye 2017", doi="10.1007/s10902-016-9732-2",
         kanit=["fixed effects", "only a (weak) positive linear effect on the life satisfaction and mental health of men",
                "has no positive impact on subjective well-being"],
         tasarim="Panel, sabit etkiler (İngiltere BHPS)",
         bulgu="Kişi başı oda artışı konut memnuniyetini artırıyor; yaşam memnuniyeti ve ruh sağlığına yalnız erkeklerde zayıf pozitif etkisi var. 'Daha büyük ev için' taşınma, uyum nedeniyle öznel iyi oluşu artırmıyor.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="saglik", ad="Melis ve ark. 2015", doi="10.3390/ijerph121114898",
         kanit=["turin longitudinal study", "accessibility by public transport and urban density only are associated to mh, being slightly protective factors"],
         tasarim="Nüfus sayımına dayalı boylamsal kohort (Torino); antidepresan kullanımı",
         bulgu="Yapılı çevre göstergelerinden yalnız toplu taşıma erişimi ve kentsel yoğunluk ilişkili ve hafif koruyucu; etki mahallede çok vakit geçirenlerde (kadın, yaşlı) daha belirgin.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="saglik", ad="de Bell ve ark. 2020", doi="10.1016/j.landurbplan.2020.103836",
         kanit=["n = 7,814", "access to a private garden was associated with better evaluative wellbeing",
                "balcony, yard or patio were more likely to meet physical activity guidelines"],
         tasarim="Kesitsel temsilî anket (İngiltere MENE, 7.814 kişi)",
         bulgu="Özel bahçeye erişim daha iyi iyi oluşla; balkon, avlu ya da veranda gibi özel dış alan fiziksel aktivite önerisini karşılamakla ilişkili.",
         etki="Özette sayı yok", duzey="Z"),
    dict(tema="saglik", ad="Laaksonen ve ark. 2008", doi="10.1136/jech.2007.061309",
         kanit=["308 291", "2.06 (95% ci 1.98 to 2.14)", "1.73 (1.65 to 1.81)", "by 30% in men and 19% in women"],
         tasarim="Kayıt temelli kohort; Finlandiya, 40–80 yaş, 308.291 kişi, 1998–2003",
         bulgu="Kiracıların ölüm oranı ev sahiplerinden yüksek; gelir, meslek ve eğitim farkın ancak bir kısmını açıklıyor.",
         etki="Kiracı/ev sahibi tüm nedenli ölüm HR: erkek 2,06 (1,98–2,14), kadın 1,73 (1,65–1,81); düzeltme fazlalığı erkekte %30, kadında %19 azaltıyor", duzey="O"),

    # ---------------------------------------------------------------- 3. Toplumsal güven ve sosyal sermaye
    dict(tema="sosyal", ad="Glaeser ve Sacerdote 2000", doi="10.1006/jhec.2000.0262", kanit=[],
         tasarim="Doğrulanmadı",
         bulgu="Özet hiçbir serviste okunamadı (NBER w8034 kaydının metni bozuk). Bulgu bu oturumda doğrulanmadı.",
         etki="Doğrulanmadı", duzey="Z"),
    dict(tema="sosyal", ad="Leyden 2003", doi="10.2105/AJPH.93.9.1546",
         kanit=["galway, ireland", "more likely to know their neighbors, participate politically, trust others, and be socially engaged"],
         tasarim="Kesitsel hane anketi (Galway, İrlanda); geleneksel karma mahalleden araba bağımlı banliyöye",
         bulgu="Yürünebilir, karma kullanımlı mahallede oturanlar komşularını daha çok tanıyor, siyasete daha çok katılıyor, başkalarına daha çok güveniyor ve sosyal olarak daha etkin.",
         etki="Özette sayı yok", duzey="Z"),
    dict(tema="sosyal", ad="Brueckner ve Largey 2008", doi="10.1016/j.jue.2007.08.002", kanit=[],
         tasarim="Social Capital Benchmark Survey; nüfus sayım bölgesi yoğunluğu için araç değişken (IV) (özetten)",
         bulgu="Yoğunluk–sosyal etkileşim ilişkisini IV ile sınıyor. Okunan özet yalnız yöntemi veriyor; sonucun yönü özette görülmedi.",
         etki="Doğrulanmadı", duzey="O"),
    dict(tema="sosyal", ad="Nguyen 2010", doi="10.1068/b35120",
         kanit=["urban sprawl may support some types of social capital while negatively impacting the others",
                "population density and street accessibility at the county level may not be ideal to improve social capital"],
         tasarim="Üç düzeyli hiyerarşik model; 2000 Social Capital Community Benchmark Survey; ilçe (county) yayılma endeksi",
         bulgu="Yayılma bazı sosyal sermaye türlerini destekliyor, bazılarını zayıflatıyor. İlçe ölçeğinde yoğunluk ve sokak erişilebilirliğini değiştirmek sosyal sermayeyi artırmanın ideal yolu olmayabilir.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="sosyal", ad="Freeman 2001", doi="10.1080/01944360108976356",
         kanit=["residential density was found to be unrelated to the formation of neighborhood social ties",
                "relied on their automobiles"],
         tasarim="Kesitsel anket (Atlanta, Boston, Los Angeles) + 1990 nüfus sayımı",
         bulgu="Konut yoğunluğu komşuluk bağlarıyla ilişkisiz; ama sakinlerin otomobile ne kadar bağımlı olduğuyla güçlü ilişkili.",
         etki="Özette sayı yok", duzey="Z"),
    dict(tema="sosyal", ad="Bramley ve ark. 2009", doi="10.1068/a4184",
         kanit=["lower in higher density/central places", "due to social and demographic factors",
                "interaction with neighbours and participation in groups is better at medium densities"],
         tasarim="Beş İngiliz kentinde hane anketleri + harita ve sosyodemografik veri",
         bulgu="Konut memnuniyeti, istikrar, çevre ve güvenlik yoğun ve merkezî yerlerde düşük (bunun önemli kısmı sosyal bileşimden). Komşuyla etkileşim ve gruplara katılım orta yoğunlukta en iyi; yerel hizmet kullanımı yoğun yerde fazla.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="sosyal", ad="Mouratidis 2019", doi="10.1016/j.cities.2019.04.013",
         kanit=["compact-city residents have higher levels of personal relationships satisfaction",
                "higher levels of anxiety", "nonsignificant associations with life satisfaction",
                "significant positive association of compactness with life satisfaction"],
         tasarim="Kesitsel anket, Oslo metropol alanı",
         bulgu="Kompakt mahallede kişisel ilişki memnuniyeti ve algılanan sağlık yüksek, ama mahalleye duygusal bağ düşük ve kaygı yüksek. Yaşam memnuniyetiyle ilişki anlamsız; güvenlik, gürültü ve temizlik denetlenince pozitif.",
         etki="Özette sayı yok", duzey="Z"),
    dict(tema="sosyal", ad="DiPasquale ve Glaeser 1999", doi="10.1006/juec.1998.2098",
         alt=("10.3386/w6363", "NBER çalışma makalesi w6363"),
         kanit=["homeowners invest more in social capital", "simple instrumental variables strategy suggests that the relationship may be causal",
                "lower mobility rates for homeowners"],
         tasarim="ABD Genel Sosyal Anketi (GSS) + araç değişken; Alman SOEP paneli, bireysel sabit etki",
         bulgu="Ev sahipleri sosyal sermayeye ve yerel imkânlara daha çok yatırım yapıyor; ilişki nedensel olabilir. Etkinin büyük kısmı ev sahiplerinin daha az taşınmasından geliyor.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="sosyal", ad="Engelhardt ve ark. 2010", doi="10.1016/j.jue.2009.09.010",
         alt=("W1972657066", "SSRN çalışma makalesi 1752381 (OpenAlex)"),
         kanit=["randomly assigned treatment status from a field experiment",
                "instrumental variable probits, however, show no impact of homeownership on political involvement"],
         tasarim="Randomize saha deneyine dayalı IV (düşük gelirli kiracılara ev alımı için birikim desteği, IDA)",
         bulgu="Basit modellerde ev sahipliği siyasi katılımı artırıyor görünüyor; rastgele atamaya dayalı IV'de siyasi katılıma etkisi yok. Diğer sosyal sonuçlar belirsiz.",
         etki="Özette sayı yok (IV etkisi sıfırdan ayırt edilemiyor)", duzey="G"),
    dict(tema="sosyal", ad="Kuo ve ark. 1998", doi="10.1023/A:1022294028903",
         kanit=["randomly assigned to 18 architecturally identical buildings",
                "levels of vegetation in common spaces predict both use of common spaces and nsts", "senses of safety and adjustment"],
         tasarim="Yarı deneysel: 18 özdeş toplu konut binasına rastgele yerleştirilmiş 145 sakin (Chicago)",
         bulgu="Ortak alandaki ağaç ve çim, ortak alan kullanımını ve komşuluk bağlarını öngörüyor; kullanım aracı. Bitki örtüsü ve bağlar güvenlik duygusuyla da ilişkili.",
         etki="Özette sayı yok", duzey="O"),

    # ---------------------------------------------------------------- 4. Güvenlik ve suç
    dict(tema="guvenlik", ad="Newman ve Franck 1982", doi="10.1007/BF01257071",
         alt=("10.4324/9781315086613-7", "2017 yeniden basımı (Routledge, The Fear of Crime)"),
         kanit=["building height is one of the leading predictors of robbery rate",
                "building size affects personal crime and fear of crime through residents' control and use of the space outside their apartments",
                "building size has a large total effect on residents' fear of crime",
                "the total effect of building size on personal crime is not as strong as expected"],
         tasarim="Hane anketi; orta gelirli ve düşük gelirli kamu destekli konut projeleri (ABD)",
         bulgu="Bina büyüklüğü, sakinlerin daire dışındaki alanı denetleyip kullanması yoluyla suçu ve korkuyu etkiliyor. Korkuya toplam etkisi büyük; kişisel suça toplam etkisi beklenenden zayıf.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="guvenlik", ad="Merry 1981", doi="10.1177/107808748101600401",
         kanit=["even architecturally defensible spaces here are undefended"],
         tasarim="Saha çalışması (etnografi), ABD'de bir kent içi toplu konut projesi",
         bulgu="Toplumsal doku parçalı olduğunda mimari olarak 'savunulabilir' alanlar da savunulmuyor.",
         etki="Özette sayı yok", duzey="Z"),
    dict(tema="guvenlik", ad="Cozens, Saville ve Hillier 2005", doi="10.1108/02637470510631483",
         kanit=["growing body of research that supports the assertion", "the evidence currently available is inconclusive and much criticised"],
         tasarim="Derleme (CPTED değerlendirmeleri)",
         bulgu="Çevresel tasarımla suç önlemenin (CPTED) suçu ve korkuyu azalttığını destekleyen kanıt büyüyor; ama kanıt kesin değil ve eleştiriliyor.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="guvenlik", ad="Sandler 2017", doi="10.1016/j.regsciurbeco.2016.10.007",
         alt=("10.3886/e100512v1", "ICPSR veri deposu kaydı"), alt_yayimlanmis="regional science and urban economics, 62: 24-35",
         kanit=["crime decreases by 8.8% after a demolition", "concentrated in violent crime", "persists for at least 5 years"],
         tasarim="Farkların farkı ve olay çalışması; Chicago toplu konut yıkımları 1995–2010, blok düzeyi suç",
         bulgu="Toplu konut projeleri çevresine olumsuz dışsallık yüklüyormuş: yıkımdan sonra suç düşüyor, en çok şiddet suçunda; bakımsız projelerde düşüş en büyük.",
         etki="Yıkım sonrası çevrede suç −%8,8; en az 5 yıl sürüyor", duzey="G"),
    dict(tema="guvenlik", ad="Aliprantis ve Hartley 2015", doi="10.1016/j.jue.2015.06.002",
         alt=("10.26509/wp-201022r", "Cleveland Fed çalışma makalesi 10-22R"),
         kanit=["10 percent to 20 percent reduction in murder, assault, and robbery", "about 3 percent in a city's murder rate",
                "about 2 percent in a city's assault rate"],
         tasarim="Chicago yıkımları: mahalle paneli; yıkım yapan şehirler paneli",
         bulgu="Yüksek yoğunluklu toplu konutun yıkıldığı mahallelerde şiddet suçu düşüyor; yerinden edilenleri alan mahallelerde de düşüyor. Şehir genelinde net azalma var, ama cinayetteki azalma birkaç yıl sürüyor.",
         etki="Yıkım mahallesinde cinayet, saldırı ve soygun −%10–20; şehir genelinde ortalama yıkım cinayet ≈ −%3, saldırı ≈ −%2", duzey="G"),
    dict(tema="guvenlik", ad="Kuo ve Sullivan 2001", doi="10.1177/0013916501333002",
         kanit=["98 apartment buildings", "the fewer crimes reported", "both property crimes and violent crimes", "building height, vacancy rate"],
         tasarim="Yarı deneysel: rastgele yerleştirilmiş sakinler, 98 apartman binası, polis kayıtları (Chicago)",
         bulgu="Binanın çevresi ne kadar yeşilse o kadar az suç bildiriliyor; mülkiyet ve şiddet suçlarında. Daire sayısı, bina yüksekliği ve boşluk oranı denetlenince de sürüyor.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="guvenlik", ad="Browning ve ark. 2010", doi="10.1177/0022427810365906",
         kanit=["curvilinear association between commercial and residential density and both homicide and aggravated assault",
                "beyond a threshold, however, increasing commercial and residential density serves to reduce the likelihood of both outcomes",
                "robbery rates is positive and linear"],
         tasarim="Suç, nüfus sayımı ve parsel verisi; Columbus, Ohio mahalleleri",
         bulgu="Ticari ve konut yoğunluğu ile cinayet ve ağır saldırı arasında ters U: düşük düzeyde artırıyor, eşikten sonra azaltıyor (Jacobs'ın 'sokaktaki gözler' beklentisiyle uyumlu). Soygunla ilişki doğrusal ve pozitif.",
         etki="Özette sayı yok", duzey="O"),

    # ---------------------------------------------------------------- 5. Aile ve çocuk
    dict(tema="aile", ad="Solari ve Mare 2012", doi="10.1016/j.ssresearch.2011.09.012",
         kanit=["panel study of income dynamics", "wellbeing suffer when exposed to crowded living conditions", "even after controlling for socioeconomic status"],
         tasarim="PSID Çocuk Gelişimi Eki ve Los Angeles FANS anketleri",
         bulgu="Kalabalık evde büyüyen çocukların akademik başarı, davranış ve sağlık göstergeleri, sosyoekonomik durum denetlense de kötü; özellikle Los Angeles'ta.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="aile", ad="Goux ve Maurin 2005", doi="10.1016/j.jpubeco.2004.06.005",
         alt=("W2003522577", "CEPR tartışma metni 3818 (OpenAlex)"),
         kanit=["almost one in five 15 year olds", "more than 60% of these adolescents have been held back",
                "more than 20 points higher", "relation of cause and effect"],
         tasarim="Fransa; yarı-parametrik nedensellik analizi (çalışma makalesi özetinden)",
         bulgu="Yatak odası başına iki ya da daha çok çocuğun düştüğü evde okulda geri kalma nedensel görünüyor; ailenin yoksulluğu çocuğun okuluna büyük ölçüde konut koşulu üzerinden yansıyor.",
         etki="15 yaşındakilerin ≈beşte biri yatak odası başına ≥2 çocukla yaşıyor; bunların %60'tan fazlası sınıf tekrarlamış, ortalamadan 20 puandan fazla yüksek", duzey="O"),
    dict(tema="aile", ad="Lopoo ve London 2016", doi="10.1007/s13524-016-0467-9",
         kanit=["high school graduation by age 19 and maximum education at age 25", "housing-cost burden"],
         tasarim="Boylamsal (ABD PSID)",
         bulgu="Lise yıllarındaki kalabalık, 19 yaşına kadar lise bitirme ve 25 yaşta ulaşılan eğitimle negatif ilişkili; sosyoekonomik durum ve konut maliyet yükü denetlense de.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="aile", ad="Marsh ve ark. 2019", doi="10.1111/ppe.12550",
         kanit=["2576 children", "0.20 sdq points (95% ci 0.08, 0.32) per additional 0.2 ppr", "maternal stress, less sleep"],
         tasarim="Doğum kohortu (Southampton Women's Survey), 2.576 çocuk; kalabalık 2 yaşta, davranış 3 yaşta",
         bulgu="Daha kalabalık evde çocukta davranış sorunu daha çok; annenin stresi, az uyku ve gergin ebeveyn-çocuk ilişkisi kısmen aracı.",
         etki="Oda başına kişi +0,2 → SDQ +0,20 puan (0,08–0,32)", duzey="O"),
    dict(tema="aile", ad="Oda ve ark. 1989", doi=None, pmid="2637293",
         kanit=["1,045 infants", "delayed independence in fundamental daily customs", "reduced number of outings"],
         tasarim="Anket (anne ve öğretmen), Tokyo'da yüksek katlı konut alanı, 1.045 küçük çocuk",
         bulgu="Yüksek katta yaşayan küçük çocuklarda temel günlük alışkanlıklarda bağımsızlık gecikiyor; yazarlar bunu dışarı çıkmanın azalmasına ve annenin aşırı bağlanmasına bağlıyor.",
         etki="Özette sayı yok", duzey="Z"),
    dict(tema="aile", ad="Chyn 2018", doi="10.1257/aer.20161352",
         kanit=["public housing demolitions in chicago", "more likely to be employed and earn more in young adulthood",
                "fewer violent crime arrests", "lower high school dropout rates"],
         tasarim="Doğal deney: yıkım yüzünden yerinden edilen çocuklar ile yıkılmayan yakın projelerdeki akranları",
         bulgu="Yerinden edilip daha az yoksul mahallelere taşınan çocuklar genç yetişkinlikte daha çok çalışıyor, daha çok kazanıyor, daha az şiddet suçundan tutuklanıyor; küçük yaşta taşınanlarda okul terki daha az.",
         etki="Özette sayı yok", duzey="G"),
    dict(tema="aile", ad="Jacob 2004", doi="10.1257/000282804322970788",
         kanit=["impact of high-rise public housing on student outcomes", "do no better or worse than their peers",
                "independent impact of public housing"],
         tasarim="Doğal deney: Chicago yıkımları (taşınanların çoğu benzer mahallelere gitti)",
         bulgu="Yıkımdan etkilenen çocukların okul başarısı akranlarından ne iyi ne kötü. Yazar bu sıfır etkiyi yüksek katlı toplu konutun mahalleden bağımsız etkisi olarak yorumluyor.",
         etki="Sıfır etki (sayı özette yok)", duzey="G"),
    dict(tema="aile", ad="Chetty, Hendren ve Katz 2016", doi="10.1257/aer.20150572",
         kanit=["randomly selected families", "before age 13", "increases college attendance and earnings and reduces single parenthood rates",
                "moving as an adolescent has slightly negative impacts"],
         tasarim="Randomize deney (Moving to Opportunity), vergi kayıtları",
         bulgu="Yoksul toplu konut projelerinden daha az yoksul mahalleye 13 yaşından önce taşınan çocuklarda üniversiteye gitme ve kazanç artıyor, tek ebeveynlik azalıyor; ergenlikte taşınma hafif olumsuz.",
         etki="Özette sayı yok", duzey="G"),
    dict(tema="aile", ad="Kulu ve Vikat 2007", doi="10.4054/DemRes.2007.17.26",
         alt=("10.4054/mpidr-wp-2007-014", "MPIDR çalışma makalesi 2007-014 (dergi özeti OpenAlex'te kesik)"),
         kanit=["longitudinal register data from finland", "fertility is highest among couples in single-family houses and lowest among those in apartments",
                "attributed to selective moves", "high risk of third birth for couples in single-family houses"],
         tasarim="Finlandiya boylamsal kayıt verisi; olay tarihi (hazard) modeli",
         bulgu="Doğurganlık müstakil evde en yüksek, apartmanda en düşük. Ama taşınma sonrası yükselme, farkın çoğunun seçici taşınmadan geldiğini gösteriyor. Müstakil evde yıllar sonra üçüncü çocuk olasılığı yüksek.",
         etki="Özette sayı yok", duzey="O"),
    dict(tema="aile", ad="Compton ve Pollak 2014", doi="10.1016/j.jue.2013.03.007",
         alt=("10.3386/w17678", "NBER çalışma makalesi w17678"),
         kanit=["4-10 percentage points higher", "mothers or their mothers-in-law", "availability of childcare"],
         tasarim="ABD NSFH anketi ve nüfus sayımı mikro verisi",
         bulgu="Anneye ya da kayınvalideye yakın oturmak küçük çocuklu evli kadınların çalışmasını artırıyor; mekanizma çocuk bakımına erişim.",
         etki="İstihdam ve işgücüne katılma olasılığı 4–10 yüzde puan yüksek", duzey="O"),
    dict(tema="aile", ad="Haurin, Parcel ve Haurin 2002", doi="10.1111/1540-6229.t01-2-00053",
         kanit=["treatment effects model", "13 to 23% higher quality home environment", "math achievement is up to 9% higher",
                "reading achievement is up to 7% higher", "1 to 3% lower"],
         tasarim="Ulusal panel (dört dalga); tedavi etkisi (seçilim) modeli",
         bulgu="Ev sahipliği ev ortamını, çocuğun bilişsel becerisini ve davranışını iyileştiriyor.",
         etki="Ev ortamı kalitesi +%13–23; matematik +%9'a, okuma +%7'ye kadar; davranış sorunları −%1–3", duzey="O"),
    dict(tema="aile", ad="Holupka ve Newman 2012", doi="10.1111/j.1540-6229.2012.00330.x",
         kanit=["statistical matching and instrumental variable analysis", "little evidence of beneficial homeownership effects",
                "mistaken selection differences for the effect of homeownership itself"],
         tasarim="PSID-CDS ve NLSY; istatistiksel eşleştirme ve araç değişken",
         bulgu="Düşük gelirli ve azınlık gruplarında ev sahipliğinin çocuk başarısı, davranışı ve sağlığına yararı için az kanıt var; önceki çalışmalar seçilimi etki sanmış olabilir.",
         etki="Özette sayı yok", duzey="O"),
]


def al(url, ham=False, deneme=4, bekle=3):
    """Varsayılan urllib başlıklarıyla GET; 404 -> None."""
    for i in range(deneme):
        try:
            with urllib.request.urlopen(url, timeout=90) as f:
                b = f.read()
                return b.decode("utf-8") if ham else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(bekle * (i + 1))
        except Exception:
            time.sleep(bekle * (i + 1))
    return None


def dosya_adi(s):
    return re.sub(r"[^A-Za-z0-9._-]", "_", s)


def onbellek(yol, getir, ham=False, ara=0.35):
    if not yol.exists():
        r = getir()
        if ham:
            open(yol, "w", encoding="utf-8").write(r or "")
        else:
            json.dump(r, open(yol, "w", encoding="utf-8"), ensure_ascii=False)
        time.sleep(ara)
    return open(yol, encoding="utf-8").read() if ham else json.load(open(yol, encoding="utf-8"))


def norm(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()


def oa_ozet(r):
    ii = (r or {}).get("abstract_inverted_index") or {}
    return " ".join(t for _, t in sorted((p, t) for t, ps in ii.items() for p in ps))


def kelimeler(s):
    return set(re.findall(r"\w{4,}", (s or "").lower()))


def pubmed_ozet(x, cr_baslik):
    if not (x or "").strip():
        return "", "", ""
    k = ET.fromstring(x)
    pmid = k.findtext(".//PMID") or ""
    ozet = " ".join("".join(a.itertext()) for a in k.iter("AbstractText"))
    pt, ct = kelimeler(k.findtext(".//ArticleTitle")), kelimeler(cr_baslik)
    if ct and len(pt & ct) / len(ct) < 0.5:
        print(f"  ! PubMed kaydı başlıkla uyuşmuyor, atıldı (PMID {pmid})")
        return "", "", ""
    return ozet, pmid, k.findtext(".//ArticleTitle") or ""


def bas_harf(given):
    return "".join(p[0].upper() for p in re.split(r"[\s\-.]+", given or "") if p)


def yazar_dizesi(yazarlar):
    ad = []
    for a in yazarlar:
        f = a.get("family") or a.get("name") or ""
        if f.isupper():
            f = f.title()
        ad.append(f"{f} {bas_harf(a.get('given'))}".strip())
    return ", ".join(ad[:3]) + (" ve ark." if len(ad) > 3 else "")


sat, kay, md = [], [], []
for s in K:
    doi = s["doi"]
    anahtar = dosya_adi(doi) if doi else dosya_adi(s["ad"])
    # 1) Crossref (zorunlu). DOI yoksa bibliyografik arama kaydedilir.
    if doi:
        c = (onbellek(HAM / "crossref" / f"{anahtar}.json",
                      lambda: al("https://api.crossref.org/works/" + urllib.parse.quote(doi))) or {}).get("message", {})
    else:
        q = onbellek(HAM / "crossref" / f"{anahtar}_sorgu.json",
                     lambda: al("https://api.crossref.org/works?rows=3&query.bibliographic="
                                + urllib.parse.quote("Oda Taniguchi Wen Higurashi 1989 Effects of high-rise living on physical and mental development of children")))
        c = {}
        for it in ((q or {}).get("message") or {}).get("items", []):
            ct = kelimeler((it.get("title") or [""])[0])
            if ct and len(ct & kelimeler("Effects of high-rise living on physical and mental development of children")) / len(ct) >= 0.8:
                c = it
    baslik = norm((c.get("title") or [""])[0]).rstrip(" *")

    # 2) Özet zinciri: PubMed -> Crossref -> Europe PMC -> Semantic Scholar -> OpenAlex
    adaylar = []  # (kaynak, metin)

    def pubmed():
        if doi:
            yp = HAM / "pubmed" / f"{anahtar}.xml"

            def getir():
                r = al("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term="
                       + urllib.parse.quote(f"{doi}[doi]"))
                ids = (r or {}).get("esearchresult", {}).get("idlist", [])
                time.sleep(0.4)
                return al(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=abstract&retmode=xml&id={ids[0]}",
                          ham=True) if len(ids) == 1 else ""
            x = onbellek(yp, getir, ham=True)
        else:
            x = onbellek(HAM / "pubmed" / f"pmid_{s['pmid']}.xml",
                         lambda: al(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=abstract&retmode=xml&id={s['pmid']}", ham=True),
                         ham=True)
        return pubmed_ozet(x, baslik)

    def europepmc():
        r = onbellek(HAM / "europepmc" / f"{anahtar}.json",
                     lambda: al("https://www.ebi.ac.uk/europepmc/webservices/rest/search?resultType=core&format=json&query="
                                + urllib.parse.quote(f'DOI:"{doi}"')))
        res = ((r or {}).get("resultList") or {}).get("result") or []
        return res[0].get("abstractText", "") if res and (res[0].get("doi") or "").lower() == doi.lower() else ""

    def semantic():
        r = onbellek(HAM / "semanticscholar" / f"{anahtar}.json",
                     lambda: al(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi)}?fields=title,abstract",
                                deneme=5, bekle=8), ara=3.5)  # anahtarsız kullanımda istek aralığı
        return (r or {}).get("abstract") or ""

    def openalex(kimlik):
        yol = "https://api.openalex.org/works/" + (kimlik if kimlik.startswith("W") else "https://doi.org/" + urllib.parse.quote(kimlik))
        return oa_ozet(onbellek(HAM / "openalex" / f"{dosya_adi(kimlik)}.json", lambda: al(yol)))

    kanit = [norm(k).lower() for k in s["kanit"]]

    def tutuyor(metin):
        m = norm(metin).lower()
        return [k for k in kanit if k not in m]

    pmid = ""
    secili, secili_kaynak, eksik = "", "", kanit
    zincir = [("PubMed", None)]
    if doi:
        zincir += [("Crossref", lambda: c.get("abstract", "")), ("Europe PMC", europepmc),
                   ("Semantic Scholar", semantic), ("OpenAlex", lambda: openalex(doi))]
    for ad_k, f in zincir:
        if ad_k == "PubMed":
            metin, pmid, _ = pubmed()
        else:
            metin = f()
        metin = norm(metin)
        if not metin:
            continue
        ek = tutuyor(metin)
        if not secili or len(ek) < len(eksik):
            secili, secili_kaynak, eksik = metin, ad_k, ek
        if not ek:
            break

    alt_metin, alt_eksik = "", None
    if eksik or not secili:
        if s.get("alt"):
            alt_metin = norm(openalex(s["alt"][0]))
            alt_eksik = tutuyor(alt_metin) if alt_metin else kanit

    # 3) Doğrulama işareti
    if kanit and secili and not eksik:
        isaret, notu = "D", f"özet: {secili_kaynak}"
    elif kanit and alt_metin and not alt_eksik:
        if s.get("alt_yayimlanmis") and s["alt_yayimlanmis"] in alt_metin.lower():
            isaret, notu = "D", f"yayımlanmış özet {s['alt'][1]} içinde künyesiyle aynen aktarılmış"
        else:
            isaret, notu = "K", f"bulgu {s['alt'][1]} özetinden; yayımlanmış sürümün özeti okunamadı"
    elif c:
        isaret, notu = "K", ("künye Crossref'te doğrulandı; " +
                             ("özet okunamadı" if not secili else "bulgu özette görülmedi: " + "; ".join(eksik or ["(kanıt dizesi yok)"])))
    else:
        isaret, notu = "DY", "künye Crossref'te bulunamadı"
    if not doi:
        notu += "; Crossref'te DOI kaydı yok, künye PubMed'den"

    # 4) Künye
    if c:
        yil = (c.get("published-print") or c.get("published-online") or c.get("issued") or {}).get("date-parts", [[None]])[0][0]
        dergi = norm((c.get("container-title") or [""])[0])
        cilt, sayi, sayfa = c.get("volume", ""), c.get("issue", ""), c.get("page", "") or c.get("article-number", "")
        yazar = yazar_dizesi(c.get("author") or []) or s.get("yazar", "")
    else:  # Oda 1989: künye PubMed XML'inden
        k = ET.fromstring(open(HAM / "pubmed" / f"pmid_{s['pmid']}.xml", encoding="utf-8").read())
        yil = int(k.findtext(".//PubDate/Year") or 0) or None
        dergi = k.findtext(".//Journal/ISOAbbreviation") or ""
        cilt, sayi, sayfa = k.findtext(".//JournalIssue/Volume") or "", k.findtext(".//JournalIssue/Issue") or "", k.findtext(".//MedlinePgn") or ""
        baslik = norm(k.findtext(".//ArticleTitle")).rstrip(".")
        ad = [f"{a.findtext('LastName')} {a.findtext('Initials')}" for a in k.iter("Author")]  # PubMed baş harfleri hazır verir
        yazar = ", ".join(ad[:3]) + (" ve ark." if len(ad) > 3 else "")
    yer = f"{cilt}" + (f"({sayi})" if sayi else "") + ((":" if cilt else "") + sayfa if sayfa else "")
    nokta = "" if baslik[-1:] in "?!." else "."
    kunye = f"{yazar} ({yil}). {baslik}{nokta} {dergi} {yer}".strip()

    print(f"{'✓' if c else '✗'} {isaret:<2} {(secili_kaynak or '-')[:10]:<10} {s['ad']:<34} {yil} · {baslik[:70]}")
    if isaret != "D":
        print(f"      {notu}")

    sat.append({"tema": TEMA[s["tema"]], "kisa_ad": s["ad"], "doi": doi or "", "pmid": pmid, "crossref_bulundu": bool(c),
                "yil": yil, "baslik": baslik, "dergi": dergi, "yer": yer, "ozet_kaynak": secili_kaynak,
                "ozet": secili, "alt_surum": (s.get("alt") or ("", ""))[1], "alt_ozet": alt_metin,
                "kanit_dizeleri": " | ".join(s["kanit"]),
                "eksik_dizeler_ozet": " | ".join(eksik), "eksik_dizeler_alt": " | ".join(alt_eksik or []),
                "dogrulama": isaret, "not": notu})
    kay.append({"tema": TEMA[s["tema"]], "kunye": kunye, "doi": doi or f"PMID {s['pmid']}", "yil": yil, "dergi": dergi,
                "tasarim": s["tasarim"], "bulgu": s["bulgu"], "etki_buyuklugu": s["etki"], "kanit_duzeyi": s["duzey"],
                "dogrulama": f"{isaret} ({notu})"})
    url = f"https://doi.org/{doi}" if doi else f"https://pubmed.ncbi.nlm.nih.gov/{s['pmid']}/"
    md.append((TEMA[s["tema"]], f"- {yazar} ({yil}). {baslik}{nokta} *{dergi}* {yer}. {url}"))

T = pd.DataFrame(sat)
T.to_csv(HAM / "kunye_ozet.csv", index=False, encoding="utf-8")
KC = pd.DataFrame(kay)
KC.to_csv(KOK / "02_LITERATUR" / "konut_bicimi_kaynakca.csv", index=False, encoding="utf-8")

print(f"\n{len(T)} kaynak · Crossref'te bulunan {T.crossref_bulundu.sum()} · özeti olan {(T.ozet != '').sum()} "
      f"(kaynağa göre: {T[T.ozet != ''].ozet_kaynak.value_counts().to_dict()})")
print("Doğrulama:", T.dogrulama.value_counts().to_dict(), "· tema:", T.groupby("tema").size().to_dict())
print("Kanıt düzeyi:", KC.kanit_duzeyi.value_counts().to_dict())

# Markdown kaynakçası (02_LITERATUR/konut_bicimi_literatur.md'ye aktarılır)
print("\n--- Kaynakça (Markdown) ---")
onceki = None
for t, satir in md:
    if t != onceki:
        print(f"\n**{t.split('-', 1)[1]}**\n")
        onceki = t
    print(satir)
