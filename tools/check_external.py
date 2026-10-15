"""Weekly check of external links on the English pages. Prints a Markdown report; exits 1 if links look dead.
usage: python3 tools/check_external.py docs > report.md"""
import re, sys, glob, urllib.request, urllib.error, concurrent.futures as cf
root = sys.argv[1]
SKIP = ("nunocrato.org", "calendar.google.com", "web.archive.org", "doi.org")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
urls = {}
for f in sorted(glob.glob(f"{root}/*.html")):
    for u in re.findall(r'href="(https?://[^"#]+)', open(f, encoding="utf-8").read()):
        if not any(s in u for s in SKIP):
            urls.setdefault(u.replace("&amp;", "&"), set()).add(f.split("/")[-1])

def check(u):
    for method in ("HEAD", "GET"):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, method=method, headers={"User-Agent": UA}), timeout=25)
            return u, r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 404, 405, 429, 501): continue
            return u, e.code
        except Exception as e:
            if method == "HEAD": continue
            return u, str(e)[:60]
    return u, "?"

with cf.ThreadPoolExecutor(8) as ex:
    res = list(ex.map(check, sorted(urls)))
dead = [(u, c) for u, c in res if isinstance(c, str) or c in (404, 410) or (isinstance(c, int) and c >= 500)]
print(f"# External link check\n\nChecked {len(res)} links; {len(dead)} look broken (403/429 'blocked' answers are ignored).\n")
for u, c in dead:
    print(f"- {u} → **{c}** (on: {', '.join(sorted(urls[u]))})")
sys.exit(1 if dead else 0)
