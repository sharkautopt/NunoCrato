"""Document viewer pages: every local PDF link on the site opens a page with a preview instead of a download.

usage (repo root):
  python3 tools/make_docs.py rewrite   # step 1: find direct PDF links in the English pages, register them, point them at view/<slug>
  python3 tools/make_docs.py build     # step 2 (after make_pt.py): write docs/view/*.html and docs/pt/view/*.html + thumbnails

Registry: tools/documents.json  (path -> slug, title, description, date, section). Safe to run repeatedly.
"""
import html, os, re, subprocess, sys, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
import viewlib

DOCS = "docs"
BASE = "https://www.nunocrato.org/"
SECTION_PAGES = ["research", "publications", "education", "presentations", "media", "about"]
SECTION_LABEL = {"en": {"research": "Research", "publications": "Publications", "education": "Education", "presentations": "Presentations", "media": "Media", "about": "About"},
                 "pt": {"research": "Investigação", "publications": "Publicações", "education": "Educação", "presentations": "Apresentações", "media": "Media", "about": "Sobre"}}
UI = {"en": dict(back="←", download="Download PDF", open="Open in new tab", pages="pages", page="page", doc="Document", tap="Tap the preview to open the PDF.",
                 eyebrow_suffix=""),
      "pt": dict(back="←", download="Descarregar PDF", open="Abrir num novo separador", pages="páginas", page="página", doc="Documento", tap="Toque na pré-visualização para abrir o PDF.",
                 eyebrow_suffix="")}
LINK = re.compile(r'<a\b([^>]*?)href="([^"]+\.pdf)"([^>]*)>(.*?)</a>', re.S | re.I)


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def chunks(text):
    """Yield (kind, block_text) for each entry block and each linklist in a page."""
    pos = [m.start() for m in re.finditer(r'<div class="entry"', text)]
    for i, p in enumerate(pos):
        end = pos[i + 1] if i + 1 < len(pos) else len(text)
        stop = re.search(r'<h2 class="sec"|<footer', text[p:end])
        yield "entry", text[p:p + stop.start()] if stop else text[p:end]
    for m in re.finditer(r'<div class="linklist">(.*?)</div>', text, re.S):
        yield "linklist", m.group(1)


def field(block, cls):
    m = re.search(rf'class="{cls}">(.*?)</div>', block, re.S)
    return m.group(1).strip() if m else ""


def clean_label(label):
    label = strip_tags(label)
    label = re.sub(r"\s*[—-]\s*PDF$", "", label)
    label = re.sub(r"\s*\(PDF\)$", "", label).strip()
    m = re.fullmatch(r"PDF \((v\d+)\)", label)
    if m:
        return m.group(1)
    return "" if label.upper().startswith("PDF") else label


def local(href):
    return not re.match(r"(https?:|//|mailto:|#)", href)


def rewrite():
    reg = viewlib.load()
    taken = {v["slug"] for v in reg.values()}
    changed = 0
    for section in SECTION_PAGES:
        path = f"{DOCS}/{section}.html"
        text = open(path, encoding="utf-8").read()
        for kind, block in chunks(text):
            for m in LINK.finditer(block):
                href = urllib.parse.unquote(m.group(2))
                if not local(href) or href in reg:
                    continue
                label = clean_label(m.group(4))
                if kind == "entry":
                    title, desc, when = field(block, "et"), field(block, "ed"), strip_tags(field(block, "when"))
                    if label and label.lower() not in ("read", "details"):
                        title = f"{title} — {label}"
                else:
                    title, desc, when = label or os.path.basename(href), "", ""
                if not os.path.exists(f"{DOCS}/{href}"):
                    print("  missing file, skipped:", href); continue
                slug = viewlib.make_slug(href, taken); taken.add(slug)
                reg[href] = dict(slug=slug, title=title, desc_en=desc, when_en=when, section=section)
        def repl(m):
            href = urllib.parse.unquote(m.group(2))
            if href in reg and local(href):
                attrs = re.sub(r"\s*\bdownload\b(=\"[^\"]*\")?", "", m.group(1) + m.group(3))
                return f'<a{(" " + attrs.strip()) if attrs.strip() else ""} href="view/{reg[href]["slug"]}">{m.group(4)}</a>'.replace("<a href", "<a href", 1)
            return m.group(0)
        new = LINK.sub(repl, text)
        # keep attribute order tidy: class first, then href
        new = re.sub(r'<a (class="[^"]*") (target="[^"]*"|rel="[^"]*")* ?href="(view/[^"]+)"', lambda m: f'<a {m.group(1)} href="{m.group(3)}"', new)
        if new != text:
            open(path, "w", encoding="utf-8").write(new); changed += 1
    viewlib.save(reg)
    print(f"registry: {len(reg)} documents; pages rewritten: {changed}")


def pt_context(slug, section):
    """Title / description / date of the Portuguese entry that links to view/<slug>."""
    path = f"{DOCS}/pt/{section}.html"
    if not os.path.exists(path):
        return None
    text = open(path, encoding="utf-8").read()
    for kind, block in chunks(text):
        if f'href="view/{slug}"' in block:
            if kind == "entry":
                m = re.search(rf'<a\b[^>]*href="view/{slug}"[^>]*>(.*?)</a>', block, re.S)
                label = clean_label(m.group(1)) if m else ""
                title = field(block, "et")
                if label and label.lower() not in ("read", "detalhes", "ler"):
                    title = f"{title} — {label}"
                return dict(title=title, desc=field(block, "ed"), when=strip_tags(field(block, "when")))
            m = re.search(rf'<a\b[^>]*href="view/{slug}"[^>]*>(.*?)</a>', block, re.S)
            return dict(title=clean_label(m.group(1)) if m else "", desc="", when="")
    return None


def head_for(lang, title, desc_plain, url_path, slug, thumb):
    src = open(f"{DOCS}/{'pt/' if lang == 'pt' else ''}presentations.html", encoding="utf-8").read()
    head = src.split('<section class="pagehead">', 1)[0]
    tail = src[src.index("<footer"):]
    head = re.sub(r"<title>[^<]*</title>", f"<title>{html.escape(title, quote=False)} — Nuno Crato</title>", head)
    d = html.escape(desc_plain[:300], quote=True)
    head = re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*"', lambda m: m.group(1) + d + '"', head)
    head = re.sub(r'(<meta (?:property|name)="(?:og|twitter):title" content=")[^"]*"', lambda m: m.group(1) + html.escape(title, quote=True) + '"', head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*"', lambda m: m.group(1) + BASE + url_path + '"', head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*"', lambda m: m.group(1) + BASE + url_path + '"', head)
    head = re.sub(r'(<meta (?:property|name)="(?:og|twitter):image" content=")[^"]*"', lambda m: m.group(1) + BASE + thumb + '"', head)
    head = re.sub(r'<link rel="alternate" hreflang="en" href="[^"]*"', f'<link rel="alternate" hreflang="en" href="{BASE}view/{slug}"', head)
    head = re.sub(r'<link rel="alternate" hreflang="pt" href="[^"]*"', f'<link rel="alternate" hreflang="pt" href="{BASE}pt/view/{slug}"', head)
    head = re.sub(r'<link rel="alternate" hreflang="x-default" href="[^"]*"', f'<link rel="alternate" hreflang="x-default" href="{BASE}view/{slug}"', head)
    return head, tail


def absolutize(chunk, lang):
    pre = "/pt/" if lang == "pt" else "/"

    def f(m):
        attr, q, v = m.group(1), m.group(2), m.group(3)
        if re.match(r"(https?:|//|mailto:|#|/)", v) or v == "":
            return m.group(0)
        if v == "./":
            return f"{attr}={q}{pre}{q}"
        if v in SECTION_PAGES:
            return f"{attr}={q}{pre}{v}{q}"
        if v.startswith("../"):
            return f"{attr}={q}/{v[3:]}{q}"
        return f"{attr}={q}/{v}{q}"
    return re.sub(r'\b(href|src)=(["\'])([^"\']*)\2', f, chunk)


def make_thumb(path, slug):
    out = f"{DOCS}/view/thumbs/{slug}"
    os.makedirs(f"{DOCS}/view/thumbs", exist_ok=True)
    if os.path.exists(out + ".jpg") and os.path.getmtime(out + ".jpg") >= os.path.getmtime(path):
        return
    subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=72", "-f", "1", "-l", "1", "-scale-to-x", "640", "-scale-to-y", "-1", "-singlefile", path, out],
                   check=True, stderr=subprocess.DEVNULL)


def pdf_info(path):
    out = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", out)
    return int(m.group(1)) if m else None


def build():
    reg = viewlib.load()
    os.makedirs(f"{DOCS}/view", exist_ok=True)
    os.makedirs(f"{DOCS}/pt/view", exist_ok=True)
    n = 0
    for href, d in sorted(reg.items()):
        path = f"{DOCS}/{href}"
        if not os.path.exists(path):
            continue
        slug, section = d["slug"], d["section"]
        make_thumb(path, slug)
        pages, mb = pdf_info(path), os.path.getsize(path) / 1e6
        for lang in ("en", "pt"):
            ui = UI[lang]
            if lang == "pt":
                ctx = pt_context(slug, section) or dict(title=d["title"], desc=d["desc_en"], when=d["when_en"])
                title, desc, when = ctx["title"], ctx["desc"], ctx["when"]
            else:
                title, desc, when = d["title"], d["desc_en"], d["when_en"]
            url_path = ("pt/" if lang == "pt" else "") + f"view/{slug}"
            head, tail = head_for(lang, strip_tags(title), strip_tags(desc) or strip_tags(title), url_path, slug, f"view/thumbs/{slug}.jpg")
            head = absolutize(head, lang)
            head = head.replace(" class='active'", "")
            head = re.sub(rf"<a href='(/(?:pt/)?{section})'>", r"<a class='active' href='\1'>", head)
            head = re.sub(r'<span class="lang">.*?</span>',
                          (f'<span class="lang"><a href="/view/{slug}">EN</a><a href="/pt/view/{slug}" class="on">PT</a></span>' if lang == "pt"
                           else f'<span class="lang"><a href="#" class="on">EN</a><a href="/pt/view/{slug}">PT</a></span>'), head, flags=re.S)
            file_url = "/" + urllib.parse.quote(href)
            meta = " · ".join(x for x in [when, "PDF", (f"{pages} {ui['pages'] if pages != 1 else ui['page']}" if pages else ""),
                                          f"{mb:.1f} MB"] if x)
            sect_url = ("/pt/" if lang == "pt" else "/") + section
            body = (f'<section class="pagehead"><p class="eyebrow"><a href="{sect_url}">{ui["back"]} {SECTION_LABEL[lang][section]}</a></p>'
                    f'<h1 class="doc-title">{title}</h1>' + (f'<p class="intro">{desc}</p>' if desc else "") + '</section>\n'
                    f'<div class="container">\n<p class="docmeta">{html.escape(meta)}</p>\n'
                    f'<p><a class="dl" href="{file_url}" download>{ui["download"]}</a><a class="dl" href="{file_url}" target="_blank" rel="noopener">{ui["open"]}</a></p>\n'
                    f'<div class="viewer" id="viewer" data-src="{file_url}#view=FitH" data-title="{html.escape(strip_tags(title), quote=True)}">'
                    f'<a href="{file_url}" target="_blank" rel="noopener"><img class="poster" src="/view/thumbs/{slug}.jpg" alt="" width="640" loading="lazy"></a>'
                    f'<p class="docmeta">{ui["tap"]}</p></div>\n</div>\n')
            script = ("<script>(function(){var v=document.getElementById('viewer');if(!v||!window.matchMedia||!matchMedia('(min-width:900px)').matches)return;"
                      "var f=document.createElement('iframe');f.src=v.dataset.src;f.title=v.dataset.title;f.className='pdf-frame';v.innerHTML='';v.appendChild(f);})();</script>\n")
            out = head + body + tail.replace("</body>", script + "</body>")
            out_path = f"{DOCS}/{'pt/' if lang == 'pt' else ''}view/{slug}.html"
            open(out_path, "w", encoding="utf-8").write(out)
        n += 1
    print(f"viewer pages: {n} documents x 2 languages")


if __name__ == "__main__":
    {"rewrite": rewrite, "build": build}[sys.argv[1]]()
