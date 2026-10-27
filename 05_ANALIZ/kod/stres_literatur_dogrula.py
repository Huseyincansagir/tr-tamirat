"""
Kentsel stres literatürü — künye ve özet doğrulaması (Faz 4 · Rapor 1)
=====================================================================
Web araması kullanılmadan, anahtarsız iki açık servisle:
  1. Crossref REST API (api.crossref.org/works/<doi>): başlık, dergi, yıl, cilt, sayı, sayfa, ilk yazar.
  2. NCBI E-utilities (PubMed): DOI'den PMID, PMID'den özet metni.
  3. Özet PubMed'de yoksa: Crossref "abstract" alanı, sonra Europe PMC REST (ebi.ac.uk/europepmc).
Etki büyüklükleri 02_LITERATUR/stres_literatur.md'de yalnızca özette (ya da PMC tam metninde) görüldüyse [D] işaretlenir.

Çıktı : 03_VERI/ham/stres/literatur/crossref/*.json, pubmed/*.xml, europepmc/*.json (ham yanıtlar, önbellek)
        03_VERI/ham/stres/literatur/pmc/PMC4928945.xml (Falchi 2016 tam metni; Türkiye satırı Tablo 2'den okunur)
        05_ANALIZ/sonuclar/stres_literatur_kunye.csv   künye + özet (doğrulama tablosu)
Çalıştırma: PYTHONIOENCODING=utf-8 python 05_ANALIZ/kod/stres_literatur_dogrula.py
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
KOK = Path(__file__).resolve().parents[2]
HAM = KOK / "03_VERI" / "ham" / "stres" / "literatur"
(HAM / "crossref").mkdir(parents=True, exist_ok=True)
(HAM / "pubmed").mkdir(parents=True, exist_ok=True)
(HAM / "europepmc").mkdir(parents=True, exist_ok=True)
SON = KOK / "05_ANALIZ" / "sonuclar"
UA = {"User-Agent": "TR-TAMIRAT/0.3 (https://github.com/Huseyincansagir/tr-tamirat)"}

# (etken, kısa ad, DOI) — kısa ad yalnızca okumayı kolaylaştırır; doğrulama Crossref'ten gelir
KAYNAK = [
    ("genel", "McEwen 1998", "10.1056/NEJM199801153380307"),
    ("genel", "Lederbogen 2011", "10.1038/nature10190"),
    ("genel", "Tawakol 2017", "10.1016/S0140-6736(16)31714-7"),
    ("genel", "Steptoe ve Kivimäki 2012", "10.1038/nrcardio.2012.45"),
    ("genel", "Peen 2010", "10.1111/j.1600-0447.2009.01438.x"),
    ("gurultu", "Jarosińska 2018", "10.3390/ijerph15040813"),
    ("gurultu", "van Kempen 2018", "10.3390/ijerph15020379"),
    ("gurultu", "Basner ve McGuire 2018", "10.3390/ijerph15030519"),
    ("gurultu", "Guski 2017", "10.3390/ijerph14121539"),
    ("gurultu", "Clark ve Paunovic 2018", "10.3390/ijerph15112400"),
    ("gurultu", "Hegewald 2020", "10.3390/ijerph17176175"),
    ("gurultu", "Dzhambov ve Lercher 2019", "10.3390/ijerph16214134"),
    ("gurultu", "Münzel 2021", "10.1038/s41569-021-00532-5"),
    ("gurultu", "Osborne 2020", "10.1093/eurheartj/ehz820"),
    ("hava", "Chen ve Hoek 2020", "10.1016/j.envint.2020.105974"),
    ("hava", "Braithwaite 2019", "10.1289/EHP4595"),
    ("hava", "Borroni 2022", "10.1016/j.envpol.2021.118245"),
    ("hava", "Block ve Calderón-Garcidueñas 2009", "10.1016/j.tins.2009.05.009"),
    ("isi", "Liu 2021", "10.1016/j.envint.2021.106533"),
    ("isi", "Thompson 2018", "10.1016/j.puhe.2018.06.008"),
    ("isi", "Thompson 2023", "10.1016/S2542-5196(23)00104-3"),
    ("isi", "Burke 2018", "10.1038/s41558-018-0222-x"),
    ("isi", "Iungman 2023", "10.1016/S0140-6736(22)02585-5"),
    ("isi", "Obradovich 2017", "10.1126/sciadv.1601555"),
    ("isi", "Minor 2022", "10.1016/j.oneear.2022.04.008"),
    ("kalabalik", "Gove 1979", "10.2307/2094818"),
    ("kalabalik", "Evans 2003", "10.1093/jurban/jtg063"),
    ("kalabalik", "Evans, Saegert ve Harris 2001", "10.1177/00139160121972936"),
    ("kalabalik", "Hammoud 2021", "10.1038/s41598-021-03398-2"),
    ("isegidis", "Stutzer ve Frey 2008", "10.1111/j.1467-9442.2008.00542.x"),
    ("isegidis", "Künn-Nelen 2016", "10.1002/hec.3199"),
    ("isegidis", "Chatterjee 2020", "10.1080/01441647.2019.1649317"),
    ("isegidis", "Clark 2020", "10.1007/s11116-019-09983-9"),
    ("isegidis", "Sandow 2014", "10.1177/0042098013498280"),
    ("isegidis", "Hansson 2011", "10.1186/1471-2458-11-834"),
    ("yesil", "Twohig-Bennett ve Jones 2018", "10.1016/j.envres.2018.06.030"),
    ("yesil", "Rojas-Rueda 2019", "10.1016/S2542-5196(19)30215-3"),
    ("yesil", "Engemann 2019", "10.1073/pnas.1807504116"),
    ("yesil", "Gascon 2015", "10.3390/ijerph120404354"),
    ("yesil", "Astell-Burt ve Feng 2019", "10.1001/jamanetworkopen.2019.8209"),
    ("yesil", "Hunter 2019", "10.3389/fpsyg.2019.00722"),
    ("yesil", "Konijnendijk 2023", "10.1007/s11676-022-01523-z"),
    ("yesil", "Liu 2023", "10.1016/j.envres.2023.116303"),
    ("yesil", "South 2018", "10.1001/jamanetworkopen.2018.0298"),
    ("yesil", "Branas 2018", "10.1073/pnas.1718503115"),
    ("gece_isigi", "Falchi 2016", "10.1126/sciadv.1600377"),
    ("gece_isigi", "Paksarian 2020", "10.1001/jamapsychiatry.2020.1935"),
    ("gece_isigi", "Obayashi 2018", "10.1093/aje/kwx290"),
    ("gece_isigi", "Min ve Min 2018", "10.1016/j.jad.2017.10.039"),
    ("gece_isigi", "Tancredi 2022", "10.1016/j.scitotenv.2022.155185"),
    ("gece_isigi", "Lai 2020", "10.1016/j.envres.2020.109637"),
    ("yalnizlik", "Holt-Lunstad 2010", "10.1371/journal.pmed.1000316"),
    ("yalnizlik", "Holt-Lunstad 2015", "10.1177/1745691614568352"),
    ("yalnizlik", "Valtorta 2016", "10.1136/heartjnl-2015-308790"),
    ("yalnizlik", "Wang 2023", "10.1038/s41562-023-01617-6"),
    ("yalnizlik", "Hawkley ve Cacioppo 2010", "10.1007/s12160-010-9210-8"),
    ("yalnizlik", "Erzen ve Çikrikci 2018", "10.1177/0020764018776349"),
    ("suc", "Lorenc 2012", "10.1016/j.healthplace.2012.04.001"),
    ("suc", "Stafford 2007", "10.2105/AJPH.2006.097154"),
    ("suc", "Chalfin 2022", "10.1007/s10940-020-09490-6"),
    ("suc", "Welsh ve Farrington 2008", "10.4073/csr.2008.13"),
    ("konut", "Bentley 2011", "10.1093/aje/kwr161"),
    ("konut", "Singh 2019", "10.1016/j.amepre.2019.03.018"),
    ("konut", "Downing 2016", "10.1016/j.socscimed.2016.06.014"),
    ("konut", "Pollack 2010", "10.1016/j.amepre.2010.08.002"),
    ("yukseklik", "Gifford 2007", "10.3763/asre.2007.5002"),
    ("yukseklik", "Kalantari ve Shepley 2021", "10.1080/02673037.2020.1752630"),
    ("yukseklik", "Barros 2019", "10.1016/j.cities.2019.05.015"),
    ("yukseklik", "Sariaslan 2015", "10.1093/schbul/sbu105"),
    ("yukseklik", "Fanning 1967", "10.1136/bmj.4.5576.382"),
    ("gunisigi", "Brown ve Jacobs 2011", "10.1177/00333549111260S117"),
    ("gunisigi", "Burns 2021", "10.1016/j.jad.2021.08.056"),
    ("gunisigi", "Burns 2023", "10.1038/s44220-023-00135-8"),
    ("gunisigi", "Pjrek 2020", "10.1159/000502891"),
    ("tekduzelik", "Lindal ve Hartig 2013", "10.1016/j.jenvp.2012.09.003"),
    ("tekduzelik", "Merrifield ve Danckert 2014", "10.1007/s00221-013-3755-2"),
]


def al(url, ham=False, deneme=4):
    for i in range(deneme):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as f:
                b = f.read()
                return b.decode("utf-8") if ham else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    return None


def dosya_adi(doi):
    return re.sub(r"[^A-Za-z0-9._-]", "_", doi)


sat = []
for etken, ad, doi in KAYNAK:
    yc = HAM / "crossref" / f"{dosya_adi(doi)}.json"
    if not yc.exists():
        r = al("https://api.crossref.org/works/" + urllib.parse.quote(doi))
        json.dump(r, open(yc, "w", encoding="utf-8"), ensure_ascii=False)
        time.sleep(0.3)
    c = (json.load(open(yc, encoding="utf-8")) or {}).get("message", {})
    yp = HAM / "pubmed" / f"{dosya_adi(doi)}.xml"
    if not yp.exists():
        s = al("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term="
               + urllib.parse.quote(f"{doi}[doi]"))
        ids = (s or {}).get("esearchresult", {}).get("idlist", [])
        time.sleep(0.4)
        x = al(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=abstract&retmode=xml&id={ids[0]}",
               ham=True) if ids else ""
        open(yp, "w", encoding="utf-8").write(x or "")
        time.sleep(0.4)
    x = open(yp, encoding="utf-8").read()
    ozet, pmid = "", ""
    if x.strip():
        k = ET.fromstring(x)
        pmid = k.findtext(".//PMID") or ""
        ozet = " ".join("".join(a.itertext()) for a in k.iter("AbstractText"))
        # DOI araması bazen yanlış kayda düşer (ör. Gove 1979): başlıklar örtüşmüyorsa PubMed kaydı atılır
        pt = set(re.findall(r"\w{4,}", (k.findtext(".//ArticleTitle") or "").lower()))
        ct = set(re.findall(r"\w{4,}", ((c.get("title") or [""])[0]).lower()))
        if ct and len(pt & ct) / len(ct) < 0.5:
            print(f"  ! PubMed kaydı başlıkla uyuşmuyor, atıldı: {ad} (PMID {pmid})")
            ozet, pmid = "", ""
    ozet_kaynak = "PubMed" if ozet else ""
    if not ozet and c.get("abstract"):
        ozet, ozet_kaynak = re.sub(r"<[^>]+>", " ", c["abstract"]), "Crossref"
    if not ozet:
        ye = HAM / "europepmc" / f"{dosya_adi(doi)}.json"
        if not ye.exists():
            r = al("https://www.ebi.ac.uk/europepmc/webservices/rest/search?resultType=core&format=json&query="
                   + urllib.parse.quote(f'DOI:"{doi}"'))
            json.dump(r, open(ye, "w", encoding="utf-8"), ensure_ascii=False)
            time.sleep(0.3)
        res = ((json.load(open(ye, encoding="utf-8")) or {}).get("resultList") or {}).get("result") or []
        if res and res[0].get("abstractText"):
            ozet, ozet_kaynak = re.sub(r"<[^>]+>", " ", res[0]["abstractText"]), "Europe PMC"
    if not ozet:  # son çare: Semantic Scholar (özet; yoksa otomatik TLDR, bu durumda bulgu [İ] sayılır)
        ys = HAM / "semanticscholar" / f"{dosya_adi(doi)}.json"
        ys.parent.mkdir(exist_ok=True)
        if not ys.exists():
            r = al(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,abstract,tldr")
            json.dump(r, open(ys, "w", encoding="utf-8"), ensure_ascii=False)
            time.sleep(3.5)
        r = json.load(open(ys, encoding="utf-8")) or {}
        if r.get("abstract"):
            ozet, ozet_kaynak = r["abstract"], "Semantic Scholar"
        elif (r.get("tldr") or {}).get("text"):
            ozet, ozet_kaynak = "[otomatik TLDR] " + r["tldr"]["text"], "Semantic Scholar TLDR"
    ozet = re.sub(r"\s+", " ", ozet).strip()
    yazar = c.get("author", [{}])
    yil = (c.get("published-print") or c.get("published-online") or c.get("issued") or {}).get("date-parts", [[None]])[0][0]
    sat.append({"etken": etken, "kisa_ad": ad, "doi": doi, "crossref_bulundu": bool(c),
                "ilk_yazar": (yazar[0].get("family") or yazar[0].get("name", "")) if yazar else "",
                "yazar_sayisi": len(yazar), "yil": yil, "baslik": (c.get("title") or [""])[0],
                "dergi": (c.get("container-title") or [""])[0], "cilt": c.get("volume", ""), "sayi": c.get("issue", ""),
                "sayfa": c.get("page", "") or c.get("article-number", ""), "pmid": pmid, "ozet_var": bool(ozet), "ozet_kaynak": ozet_kaynak, "ozet": ozet})
    print(f"{'✓' if c else '✗'} {ozet_kaynak[:1] or '-'} {ad:<34} {sat[-1]['ilk_yazar']:<18} {yil} · {sat[-1]['baslik'][:80]}")

K = pd.DataFrame(sat)
K.to_csv(SON / "stres_literatur_kunye.csv", index=False, encoding="utf-8")
print(f"\n{len(K)} kaynak · Crossref'te bulunan {K.crossref_bulundu.sum()} · özeti olan {K.ozet_var.sum()} (kaynağa göre: {K.ozet_kaynak.value_counts().to_dict()})")

# --- Falchi ve ark. 2016, Tablo 2: Türkiye satırı (PMC tam metni) ------------------------------------------------
(HAM / "pmc").mkdir(exist_ok=True)
yx = HAM / "pmc" / "PMC4928945.xml"
if not yx.exists():
    open(yx, "w", encoding="utf-8").write(al("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=4928945", ham=True))
x = open(yx, encoding="utf-8").read()
i = x.find(">Turkey<")
hucre = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<td[^>]*>(.*?)</td>", x[i:x.find("</tr>", i)])]
ESIK = ["<=1.7", ">1.7", ">14", ">87", ">688", ">3000"]
print("\nFalchi 2016 Tablo 2, Türkiye (nüfus %, sonra alan %; µcd/m²):", dict(zip(ESIK, hucre[:6])), dict(zip(ESIK, hucre[6:12])))
assert hucre[2] == "97.8" and hucre[4] == "49.9" and hucre[5] == "24.3"
