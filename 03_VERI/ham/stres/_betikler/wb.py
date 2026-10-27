"""Kullanım: python -I wb.py <cikti> <url> [<cikti> <url> ...]  (429'da bekleyip yeniden dener)"""
import sys, time, urllib.request, urllib.error
sys.stdout.reconfigure(encoding="utf-8")
a = sys.argv[1:]
for out, url in zip(a[::2], a[1::2]):
    for d in range(5):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"}), timeout=120)
            b = r.read(); open(out, "wb").write(b)
            print("OK", r.status, len(b), r.geturl()[:200]); break
        except urllib.error.HTTPError as e:
            print("HTTP", e.code, url[:150])
            if e.code == 429: time.sleep(30 * (d + 1)); continue
            break
        except Exception as e:
            print("ERR", e); time.sleep(10)
    time.sleep(4)
