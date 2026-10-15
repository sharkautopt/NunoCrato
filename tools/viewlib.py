"""Shared helpers for the document viewer pages (docs/view/<slug>.html)."""
import json, os, re, unicodedata

REGISTRY = "tools/documents.json"


def load():
    return json.load(open(REGISTRY, encoding="utf-8")) if os.path.exists(REGISTRY) else {}


def save(reg):
    json.dump(reg, open(REGISTRY, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)


def make_slug(path, taken):
    base = os.path.splitext(os.path.basename(path))[0]
    s = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:70] or "document"
    cand, n = s, 2
    while cand in taken:
        cand = f"{s}-{n}"; n += 1
    return cand


def slug_for(path):
    """Viewer slug for a site-relative file path, or None."""
    return load().get(path, {}).get("slug")
