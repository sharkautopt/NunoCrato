"""Ask the Internet Archive (Wayback Machine) to save external press links of the Media page, so a copy exists if the article disappears.
Only links without a snapshot are submitted. Runs in the weekly GitHub workflow (the Claude sandbox cannot reach web.archive.org).
usage: python3 tools/archive_links.py docs/media.html [max]"""
import re, sys, time, json, urllib.parse, urllib.request
SKIP = ("nunocrato.org", "spotify.com", "youtube.com", "youtu.be", "calendar.google.com", "web.archive.org")
page, cap = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 30
urls = [u.replace("&amp;", "&") for u in dict.fromkeys(re.findall(r'href="(https?://[^"#]+)', open(page, encoding="utf-8").read())) if not any(s in u for s in SKIP)]
done = 0
for u in urls:
    if done >= cap: break
    try:
        a = json.load(urllib.request.urlopen("https://archive.org/wayback/available?url=" + urllib.parse.quote(u, safe=""), timeout=30))
        if a.get("archived_snapshots"): continue
        urllib.request.urlopen(urllib.request.Request("https://web.archive.org/save/" + u, headers={"User-Agent": "nunocrato.org archiver"}), timeout=120)
        print("saved", u); done += 1; time.sleep(12)
    except Exception as e:
        print("skip", u, str(e)[:80]); time.sleep(5)
print(f"submitted {done} of {len(urls)} links")
