"""Build the Portuguese pages (docs/pt/*.html) from the English ones, using tools/pt_strings.py.

usage: python3 tools/make_pt.py          (run from the repo root)
Also (re)writes the EN/PT switch and hreflang links in the English pages.
Titles of works stay in their original language; add new English text to tools/pt_strings.py.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from pt_strings import T, MONTHS

DOCS = "docs"
PAGES = ["index", "research", "publications", "education", "presentations", "media", "about"]
SECTIONS = {"research", "publications", "education", "presentations", "media", "about"}
META = {
 "index": ("Nuno Crato — ISEG, Universidade de Lisboa", "Nuno Crato — Professor Catedrático de Matemática e Estatística no ISEG, Universidade de Lisboa. Antigo Ministro da Educação e Ciência de Portugal (2011–2015). Estatístico, autor e divulgador de ciência."),
 "research": ("Investigação — Nuno Crato", "Investigação de Nuno Crato — modelos estocásticos, econometria, séries temporais e avaliação estatística de políticas de educação. Artigos selecionados e perfis de investigação."),
 "publications": ("Publicações — Nuno Crato", "Livros, artigos académicos e ensaios de Nuno Crato — matemática, estatística, políticas de educação e história da ciência. Duas décadas de escrita para públicos académicos e gerais."),
 "education": ("Educação — Nuno Crato", "O trabalho de Nuno Crato sobre reforma curricular, avaliações internacionais (PISA, TIMSS, PIRLS), formação de professores e equidade educativa — em Portugal e no mundo."),
 "presentations": ("Apresentações — Nuno Crato", "Conferências e apresentações de Nuno Crato — sobre reforma da educação, matemática e política científica. Diapositivos disponíveis para descarregar."),
 "media": ("Media — Nuno Crato", "Aparições nos media, entrevistas, podcasts, artigos de opinião e publicações académicas de Nuno Crato — educação, matemática, política científica e assuntos públicos."),
 "about": ("Sobre — Nuno Crato", "Nuno Crato — Professor Catedrático no ISEG, Universidade de Lisboa, antigo Ministro da Educação e Ciência de Portugal (2011–2015), especialista em políticas de educação e escritor de ciência."),
}
BASE = "https://www.nunocrato.org/"
unknown = set()


def slug(page):
    return "" if page == "index" else page


def switch(page, pt):
    if pt:
        en = "../" if page == "index" else f"../{page}"
        me = "./" if page == "index" else page
        return f'<span class="lang"><a href="{en}">EN</a><a href="{me}" class="on">PT</a></span>'
    other = "pt/" if page == "index" else f"pt/{page}"
    return f'<span class="lang"><a href="#" class="on">EN</a><a href="{other}">PT</a></span>'


def hreflang(page):
    en, pt = BASE + slug(page), BASE + "pt/" + slug(page)
    return (f'<link rel="alternate" hreflang="en" href="{en}">\n<link rel="alternate" hreflang="pt" href="{pt}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{en}">\n')


def translate_text(m):
    raw = m.group(1)
    s = raw.strip()
    if not s:
        return m.group(0)
    lead, trail = raw[: len(raw) - len(raw.lstrip())], raw[len(raw.rstrip()):]
    if s in T:
        return ">" + lead + T[s] + trail + "<"
    d = re.fullmatch(r"(\d{4}) · ([A-Z][a-z]{2})(?:–([A-Z][a-z]{2}))?", s)
    if d:
        out = f"{d.group(1)} · {MONTHS[d.group(2)]}" + (f"–{MONTHS[d.group(3)]}" if d.group(3) else "")
        return ">" + lead + out + trail + "<"
    if re.search(r"\b(the|of|and|with|for|on|from|in)\b", s) and not s.startswith(("http", "(function")):
        unknown.add(s)
    return m.group(0)


def to_pt(page, html):
    head, body = html.split("<body", 1)
    title, desc = META[page]
    head = head.replace('<html lang="en">', '<html lang="pt">')
    head = re.sub(r"<title>[^<]*</title>", f"<title>{title}</title>", head)
    head = re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*"', lambda m: m.group(1) + desc + '"', head)
    head = re.sub(r'(<meta (?:property|name)="(?:og|twitter):title" content=")[^"]*"', lambda m: m.group(1) + title + '"', head)
    url = BASE + "pt/" + slug(page)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*"', lambda m: m.group(1) + url + '"', head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*"', lambda m: m.group(1) + url + '"', head)
    head = head.replace('<meta property="og:type"', '<meta property="og:locale" content="pt_PT">\n<meta property="og:type"', 1)
    head = re.sub(r'<script src="old-links.js"></script>\n?', "", head)
    head = re.sub(r"<link rel=\"alternate\" hreflang[^>]*>\n", "", head)
    head = head.replace('<link rel="canonical"', hreflang(page) + '<link rel="canonical"', 1) if False else head
    head = re.sub(r'(<link rel="canonical" href="[^"]*">\n)', lambda m: m.group(1) + hreflang(page), head, count=1)

    def fix_ref(m):
        attr, q, v = m.group(1), m.group(2), m.group(3)
        if v.startswith(("http", "#", "mailto:", "tel:", "data:", "/", "../")):
            return m.group(0)
        if v in ("./",) or v in SECTIONS:
            return m.group(0)
        return f"{attr}={q}../{v}{q}"
    head = re.sub(r'\b(href|src)=(["\'])([^"\']*)\2', fix_ref, head)
    head = head.replace('rel="stylesheet" href="../style.css"', 'rel="stylesheet" href="../style.css"')
    body = re.sub(r'\b(href|src)=(["\'])([^"\']*)\2', fix_ref, body)
    body = re.sub(r'<span class="lang">.*?</span>', switch(page, True), body, count=1, flags=re.S)
    body = body.replace('aria-label="Toggle menu"', 'aria-label="Abrir menu"')
    body = re.sub(r">([^<>]+)<", translate_text, body)
    # keep brand / nav hrefs working inside pt/
    return head + "<body" + body


os.makedirs(f"{DOCS}/pt", exist_ok=True)
for page in PAGES:
    src = open(f"{DOCS}/{page}.html", encoding="utf-8").read()
    # English page: switch + hreflang
    en = re.sub(r'<span class="lang">.*?</span>', switch(page, False), src, count=1, flags=re.S)
    en = re.sub(r"<link rel=\"alternate\" hreflang[^>]*>\n", "", en)
    en = re.sub(r'(<link rel="canonical" href="[^"]*">\n)', lambda m: m.group(1) + hreflang(page), en, count=1)
    open(f"{DOCS}/{page}.html", "w", encoding="utf-8").write(en)
    open(f"{DOCS}/pt/{page}.html", "w", encoding="utf-8").write(to_pt(page, en))
print("pages written:", len(PAGES))
if unknown:
    print("English-looking text left untranslated:")
    for s in sorted(unknown):
        print(" -", s)
