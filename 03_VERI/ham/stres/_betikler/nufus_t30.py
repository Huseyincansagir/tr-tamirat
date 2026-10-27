import json, sys, urllib.request
sys.stdout.reconfigure(encoding="utf-8")
H = {"Accept": "application/json", "User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
B = "https://databrowser2.tuik.gov.tr/api/core/nodes/1/datasets/TR,DF_ADNKS_T30,1.1/"
out = sys.argv[1]
r = urllib.request.Request(B + "data", data=json.dumps([]).encode(), headers=H, method="POST")
raw = urllib.request.urlopen(r, timeout=600).read()
open(out, "wb").write(raw)
d = json.loads(raw)
print(d.get("id"), d.get("size"))
for k in d["id"]:
    idx = d["dimension"][k]["category"]["index"]; lab = d["dimension"][k]["category"].get("label", {})
    print(k, len(idx), [(i, lab.get(i)) for i in list(idx)[:5]])
