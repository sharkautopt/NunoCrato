"""Write docs/sitemap.xml and docs/robots.txt (run from the repo root, after make_pt.py and make_events.py)."""
import datetime
B = "https://www.nunocrato.org/"
pages = ["", "research", "publications", "education", "presentations", "media", "events", "about"]
today = datetime.date.today().isoformat()
rows = []
for p in pages:
    en, pt = B + p, B + "pt/" + p
    for url in (en, pt):
        rows.append(f"<url><loc>{url}</loc><lastmod>{today}</lastmod>"
                    f'<xhtml:link rel="alternate" hreflang="en" href="{en}"/><xhtml:link rel="alternate" hreflang="pt" href="{pt}"/></url>')
import os
for n in sorted(os.listdir("docs/view")):
    if n.endswith(".html"):
        s = n[:-5]; en, pt = B + "view/" + s, B + "pt/view/" + s
        for url in (en, pt):
            rows.append(f"<url><loc>{url}</loc><lastmod>{today}</lastmod>"
                        f'<xhtml:link rel="alternate" hreflang="en" href="{en}"/><xhtml:link rel="alternate" hreflang="pt" href="{pt}"/></url>')
open("docs/sitemap.xml", "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + "\n".join(rows) + "\n</urlset>\n")
open("docs/robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {B}sitemap.xml\n")
print(len(rows), "sitemap entries")
