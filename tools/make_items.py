"""Own pages for every event (docs/events/<slug>.html) and every book (docs/books/<slug>.html), EN and PT, with schema.org JSON-LD.

usage (repo root):
  python3 tools/make_items.py links   # before make_pt.py: add a "Details" link to every book card in publications.html
  python3 tools/make_items.py build   # after make_pt.py and make_events.py: write the pages
Sources: tools/events.json (events) and the .bookcard blocks of docs/publications.html (books).
"""
import datetime, html, json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
import make_docs as md
import pt_strings

DOCS, BASE = "docs", "https://www.nunocrato.org/"
PERSON = {"@type": "Person", "name": "Nuno Crato", "url": BASE}
UI = {"en": dict(back_e="← Events", back_b="← Publications", add="Add to calendar", when="When", where="Where", cover="Cover of",
                 ev_label="Event", bk_label="Book", pub="Publisher"),
      "pt": dict(back_e="← Eventos", back_b="← Publicações", add="Adicionar ao calendário", when="Quando", where="Onde", cover="Capa de",
                 ev_label="Evento", bk_label="Livro", pub="Editora")}


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]


def pt_text(s):
    return pt_strings.T.get(s) or pt_strings.T.get(html.escape(s, quote=False)) or s


def books():
    text = open(f"{DOCS}/publications.html", encoding="utf-8").read()
    out = []
    for line in text.splitlines():
        if '<div class="bookcard">' not in line:
            continue
        img = re.search(r'<img src="([^"]+)" alt="([^"]*)" width="(\d+)" height="(\d+)"', line)
        title = md.strip_tags(re.search(r'<div class="bt">(.*?)</div>', line).group(1))
        title = re.sub(r"\s+(EN|ES|PT)$", "", title)
        lang = re.search(r'vertical-align:middle">(EN|ES|PT)<', line)
        bm = md.strip_tags(re.search(r'<div class="bm">(.*?)</div>', line).group(1))
        pubr, _, year = bm.rpartition("·")
        desc = re.findall(r'<div style="[^"]*">(.*?)</div>', line)[-1]
        by = re.search(r'<div class="ba">(.*?)</div>', line)
        out.append(dict(slug=slugify(title), title=title, publisher=pubr.strip(), year=year.strip(), desc=desc, by=by.group(1) if by else "",
                        img=img.group(1), w=int(img.group(3)), h=int(img.group(4)), lang=(lang.group(1).lower() if lang else "pt")))
    return out


def add_links():
    p = f"{DOCS}/publications.html"
    lines = open(p, encoding="utf-8").read().split("\n")
    byt = {b["title"]: b["slug"] for b in books()}
    for i, line in enumerate(lines):
        if '<div class="bookcard">' not in line:
            continue
        t = re.sub(r"\s+(EN|ES|PT)$", "", md.strip_tags(re.search(r'<div class="bt">(.*?)</div>', line).group(1)))
        href = f"books/{byt[t]}"
        if f'<a href="{href}"><img' not in line:
            line = re.sub(r'(<img [^>]*>)', rf'<a href="{href}">\1</a>', line, 1)
            line = re.sub(r'(<div class="bt">)(.*?)(</div>)', rf'\1<a href="{href}">\2</a>\3', line, 1)
        if f'class="dl" href="{href}"' not in line:
            k = line.rindex("</div>")
            line = line[:k] + f'<a class="dl" href="{href}">Details</a>' + line[k:]
        lines[i] = line
    open(p, "w", encoding="utf-8").write("\n".join(lines))


def shell(lang, kind, slug, title, desc, section, thumb, body, ld):
    path = f"{'pt/' if lang == 'pt' else ''}{kind}/{slug}"
    head, tail = md.head_for(lang, title, desc, path, slug, thumb)
    head = head.replace(f"{BASE}view/{slug}", f"{BASE}{kind}/{slug}").replace(f"{BASE}pt/view/{slug}", f"{BASE}pt/{kind}/{slug}")
    head = md.absolutize(head, lang).replace(" class='active'", "")
    head = re.sub(rf"<a href='(/(?:pt/)?{section})'>", r"<a class='active' href='\1'>", head)
    head = re.sub(r'<span class="lang">.*?</span>',
                  (f'<span class="lang"><a href="/{kind}/{slug}">EN</a><a href="/pt/{kind}/{slug}" class="on">PT</a></span>' if lang == "pt"
                   else f'<span class="lang"><a href="#" class="on">EN</a><a href="/pt/{kind}/{slug}">PT</a></span>'), head, flags=re.S)
    head = head.replace("</head>", '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>\n</head>", 1)
    os.makedirs(f"{DOCS}/{'pt/' if lang == 'pt' else ''}{kind}", exist_ok=True)
    open(f"{DOCS}/{path}.html", "w", encoding="utf-8").write(head + body + tail)


def build():
    import make_events as me  # also regenerates the events pages (cheap)
    n_e = n_b = 0
    for e in me.events:
        slug = e["start"] + "-" + slugify(e["title"])[:40]
        for lang in ("en", "pt"):
            ui = UI[lang]
            title = e.get("title_pt", e["title"]) if lang == "pt" else e["title"]
            desc = e["desc_" + lang]
            when = me.fmt_date(e, lang) + (f" · {e['time']}" if e.get("time") else "")
            links = ""
            if e["end"] >= me.today:
                links += f'<a class="dl" href="{html.escape(me.gcal(e, lang))}" target="_blank" rel="noopener">{ui["add"]}</a>'
            for l in e["links"]:
                u = l["url"]
                if not re.match(r"https?:", u):
                    s = md.viewlib.slug_for(u); u = "/view/" + s if s else "/" + u
                links += f'<a class="dl" href="{html.escape(u)}"' + (' target="_blank" rel="noopener"' if u.startswith("http") else "") + f'>{l[lang]}</a>'
            img = f'<img class="still" src="/{e["image"]}" alt="" style="max-width:520px">' if e.get("image") else ""
            body = (f'<section class="pagehead"><p class="eyebrow"><a href="{"/pt" if lang == "pt" else ""}/events">{ui["back_e"]}</a></p><h1 class="doc-title">{html.escape(title, quote=False)}</h1></section>\n'
                    f'<div class="container"><p class="docmeta">{html.escape(when)} · {html.escape(e["place_" + lang])}</p>\n'
                    f'<p class="body">{html.escape(desc, quote=False)}</p>\n<p>{links}</p>\n{img}</div>\n')
            off = f"{me.lisbon_offset_hours(me.d(e['start'])):+03d}:00"
            ld = {"@context": "https://schema.org", "@type": "Event", "name": title, "description": desc, "inLanguage": lang,
                  "startDate": e["start"] + (f"T{e['time']}:00{off}" if e.get("time") else ""),
                  "endDate": e["end"] + (f"T{me.end_of(e)}:00{off}" if e.get("time") else ""),
                  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                  "location": {"@type": "Place", "name": e["place_" + lang]}, "performer": PERSON,
                  "url": f"{BASE}{'pt/' if lang == 'pt' else ''}events/{slug}"}
            if e.get("image"): ld["image"] = BASE + e["image"]
            shell(lang, "events", slug, title, desc, "events", e.get("image") or "wp-content/uploads/2025/02/Prof-Nuno-Crato.jpg", body, ld)
        n_e += 1
    for b in books():
        for lang in ("en", "pt"):
            ui = UI[lang]
            desc_html = pt_text(b["desc"]) if lang == "pt" else b["desc"]
            desc = md.strip_tags(desc_html)
            meta = " · ".join(x for x in [b["publisher"], b["year"]] if x)
            by = md.strip_tags(pt_text(b["by"]) if lang == "pt" else b["by"])
            body = (f'<section class="pagehead"><p class="eyebrow"><a href="{"/pt" if lang == "pt" else ""}/publications">{ui["back_b"]}</a></p><h1 class="doc-title">{html.escape(b["title"], quote=False)}</h1></section>\n'
                    f'<div class="container"><div class="about-grid"><div><p class="docmeta">{html.escape(meta)}</p>'
                    + (f'<p class="docmeta">{html.escape(by)}</p>' if by else "") + f'<p class="body">{desc_html}</p></div>'
                    f'<img src="/{b["img"]}" alt="{ui["cover"]} {html.escape(b["title"])}" width="{b["w"]}" height="{b["h"]}" style="height:auto;max-width:320px"></div></div>\n')
            ld = {"@context": "https://schema.org", "@type": "Book", "name": b["title"], "author": PERSON, "description": desc,
                  "datePublished": b["year"], "inLanguage": b["lang"], "image": BASE + b["img"],
                  "url": f"{BASE}{'pt/' if lang == 'pt' else ''}books/{b['slug']}"}
            if b["publisher"]: ld["publisher"] = {"@type": "Organization", "name": b["publisher"]}
            shell(lang, "books", b["slug"], b["title"], desc, "publications", b["img"], body, ld)
        n_b += 1
    print(f"item pages: {n_e} events, {n_b} books (x2 languages)")


if __name__ == "__main__":
    {"links": add_links, "build": build}[sys.argv[1]]()
