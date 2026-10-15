"""Check a static site folder: internal links/files exist, no old-host or injected references.

usage: check_site.py <site_dir>
"""
import os
import re
import sys
import urllib.parse
from html.parser import HTMLParser

root = sys.argv[1]


class Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src", "poster", "data-src") and value:
                self.refs.append((tag, key, value))
            if key == "srcset" and value:
                for part in value.split(","):
                    self.refs.append((tag, key, part.strip().split(" ")[0]))


def exists(path):
    path = urllib.parse.unquote(path.split("#")[0].split("?")[0])
    if path in ("", "/"):
        return os.path.isfile(os.path.join(root, "index.html"))
    full = os.path.join(root, path.lstrip("/"))
    return os.path.isfile(full) or os.path.isfile(full + ".html") or os.path.isfile(os.path.join(full, "index.html"))


problems, internal, external = [], 0, {}
pages = sorted(n for n in os.listdir(root) if n.endswith(".html"))
for name in pages:
    text = open(os.path.join(root, name), encoding="utf-8").read()
    parser = Refs()
    parser.feed(text)
    for tag, key, value in parser.refs:
        if value.startswith(("mailto:", "tel:", "javascript:", "data:", "#")):
            continue
        if value.startswith("//"):
            value = "https:" + value
        if value.startswith("http"):
            host = urllib.parse.urlparse(value).netloc
            external[host] = external.get(host, 0) + 1
            if host.endswith("nunocrato.org") and "/wp-content/" in value and tag not in ("meta",):
                problems.append(f"{name}: still points at old host: {value}")
            if "netlify.app" in host:
                problems.append(f"{name}: points at the staging host: {value}")
            continue
        internal += 1
        if not exists(value):
            problems.append(f"{name}: missing file for {tag} {key}={value}")
    if "/.netlify/" in text:
        problems.append(f"{name}: injected Netlify script still present")

# css url() references
css_path = os.path.join(root, "style.css")
if os.path.isfile(css_path):
    css = open(css_path, encoding="utf-8").read()
    for ref in re.findall(r"url\(['\"]?([^)'\"]+)", css):
        if not ref.startswith(("http", "data:")) and not exists(ref):
            problems.append(f"style.css: missing {ref}")

# social-card images referenced by meta tags
for name in pages:
    text = open(os.path.join(root, name), encoding="utf-8").read()
    for url in re.findall(r'<meta[^>]+(?:og|twitter):image"[^>]+content="([^"]+)"', text) + re.findall(r'content="([^"]+)"[^>]+(?:og|twitter):image"', text):
        path = urllib.parse.urlparse(url).path
        if not exists(path):
            problems.append(f"{name}: social image not in site: {path}")

total_files = sum(len(f) for _, _, f in os.walk(root))
size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(root) for f in fs)
print(f"pages: {len(pages)}, files: {total_files}, size: {size / 1e6:.1f} MB")
print(f"internal references checked: {internal}")
print("external hosts:", ", ".join(f"{h} ({n})" for h, n in sorted(external.items(), key=lambda x: -x[1])[:12]))
print(f"problems: {len(problems)}")
for p in problems:
    print(" -", p)
