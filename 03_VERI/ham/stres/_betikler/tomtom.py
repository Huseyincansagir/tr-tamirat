import site, sys as _s; _s.path.append(site.getusersitepackages())
import re, sys, html, json
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
s = html.unescape(open(sys.argv[1], encoding="utf-8", errors="replace").read())
rows = []
for blok in ["centerRanking", "metroRanking"]:
    i = s.find(f'"{blok}":[1,[')
    seg = s[i:i + 200000]
    for m in re.finditer(r'\{"key":\[0,"([a-z-]+)"\],"name":\[0,"([^"]+)"\],"country":\[0,"TR"\],"continent":\[0,"EUROPE"\],"cRank":\[0,(\d+)\],"c":\[0,([\d.]+)\],"cDelta":\[0,(-?[\d.]+)\],"v":\[0,([\d.]+)\],"d15":\[0,([\d.]+)\],"tLostRush":\[0,([\d.]+)\]', seg):
        k, n, rank, c, cd, v, d15, tl = m.groups()
        rows.append(dict(kapsam="sehir_merkezi" if blok == "centerRanking" else "metropol_alan", sehir=n, dunya_sirasi=int(rank), sikisiklik_pct=float(c),
                         sikisiklik_degisim_puan_2024e_gore=float(cd), ort_hiz_kmsa=float(v), dk_10km_hesap=round(600 / float(v), 2), km_15dk=float(d15), tLostRush_ham=float(tl)))
        if m.start() > 0 and '"metroRanking"' in seg[:m.start()] and blok == "centerRanking": break
df = pd.DataFrame(rows).drop_duplicates(["kapsam", "sehir"])
print(df.to_string())
df.to_csv(sys.argv[2], index=False, encoding="utf-8")
