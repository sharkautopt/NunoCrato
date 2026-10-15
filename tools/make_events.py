"""Build the Events pages (docs/events.html, docs/pt/events.html) and the calendar file docs/events.ics
from tools/events.json.

usage (repo root):  python3 tools/make_pt.py && python3 tools/make_events.py
Run it after make_pt.py (it uses presentations.html / pt/presentations.html as the page template).
The page also re-sorts itself in the visitor's browser by today's date, so upcoming/past stay right between rebuilds.
"""
import datetime, html, json, os, re, urllib.parse

DOCS = "docs"
BASE = "https://www.nunocrato.org/"
events = json.load(open("tools/events.json", encoding="utf-8"))
today = datetime.date.today().isoformat()
MON = {"en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
       "pt": ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]}
UI = {
 "en": dict(title="Events — Nuno Crato", eyebrow="Calendar", h1="Events",
            desc="Upcoming and past lectures, conferences and book presentations by Nuno Crato.",
            intro="Upcoming and past public appearances. Add an event to your calendar, or download the full calendar.",
            up="Upcoming", past="Past", none_up="No upcoming events are announced at the moment.",
            add="Add to calendar", ics="Download the full calendar (.ics)",
            note="Earlier lectures are on the Presentations and Media pages."),
 "pt": dict(title="Eventos — Nuno Crato", eyebrow="Calendário", h1="Eventos",
            desc="Próximas conferências, palestras e apresentações de livros de Nuno Crato, e eventos passados.",
            intro="Próximas e passadas intervenções públicas. Adicione um evento ao seu calendário ou descarregue o calendário completo.",
            up="Próximos", past="Passados", none_up="Não há eventos anunciados de momento.",
            add="Adicionar ao calendário", ics="Descarregar o calendário completo (.ics)",
            note="As conferências anteriores estão nas páginas Apresentações e Media."),
}


def d(s):
    return datetime.date.fromisoformat(s)


def fmt_date(e, lang):
    a, b, m = d(e["start"]), d(e["end"]), MON[lang]
    if a == b:
        return f"{a.day} {m[a.month-1]} {a.year}"
    if a.month == b.month:
        return f"{a.day}–{b.day} {m[a.month-1]} {a.year}"
    return f"{a.day} {m[a.month-1]} – {b.day} {m[b.month-1]} {a.year}"


def lisbon_offset_hours(day):
    """Europe/Lisbon: UTC+1 from the last Sunday of March to the last Sunday of October (inclusive of that Sunday's early hours)."""
    def last_sunday(y, mth):
        x = datetime.date(y, mth, 31)
        return x - datetime.timedelta(days=(x.weekday() + 1) % 7)
    y = day.year
    return 1 if last_sunday(y, 3) <= day < last_sunday(y, 10) else 0


def end_of(e):
    """End time; when the source gives none, assume 1.5 hours after the start."""
    if e.get("end_time"):
        return e["end_time"]
    h, m = map(int, e["time"].split(":"))
    mins = h * 60 + m + 90
    return f"{mins // 60:02d}:{mins % 60:02d}"


def utc_stamp(day, hhmm):
    h, m = map(int, hhmm.split(":"))
    dt = datetime.datetime(day.year, day.month, day.day, h, m) - datetime.timedelta(hours=lisbon_offset_hours(day))
    return dt.strftime("%Y%m%dT%H%M%SZ")


def gcal(e, lang):
    day = d(e["start"])
    if e.get("time"):
        dates = utc_stamp(day, e["time"]) + "/" + utc_stamp(day, end_of(e))
    else:
        dates = day.strftime("%Y%m%d") + "/" + (d(e["end"]) + datetime.timedelta(days=1)).strftime("%Y%m%d")
    q = {"action": "TEMPLATE", "text": e.get("title_pt", e["title"]) if lang == "pt" else e["title"],
         "dates": dates, "location": e["place_" + lang], "details": e["desc_" + lang]}
    return "https://calendar.google.com/calendar/render?" + urllib.parse.urlencode(q)


def entry(e, lang, upcoming):
    ui = UI[lang]
    when = fmt_date(e, lang) + (f"<br>{e['time']}" if e.get("time") else "")
    title = e.get("title_pt", e["title"]) if lang == "pt" else e["title"]
    links = ""
    if upcoming:
        links += f'<a class="dl" href="{html.escape(gcal(e, lang))}" target="_blank" rel="noopener">{ui["add"]}</a>'
    for l in e["links"]:
        url = l["url"] if re.match(r"https?:", l["url"]) else ("../" if lang == "pt" else "") + l["url"]
        ext = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
        links += f'<a class="dl" href="{html.escape(url)}"{ext}>{l[lang]}</a>'
    img = f'<img class="still" src="{"../" if lang == "pt" else ""}{e["image"]}" alt="">' if e.get("image") and upcoming else ""
    return (f'<div class="entry" data-start="{e["start"]}" data-end="{e["end"]}"><div class="when">{when}</div><div>'
            f'<div class="et">{html.escape(title, quote=False)}</div>'
            f'<div class="ed">{html.escape(e["desc_" + lang], quote=False)} <em>{html.escape(e["place_" + lang], quote=False)}.</em></div>'
            f'{links}</div></div>\n')


SCRIPT = """<script>
(function(){
var up=document.getElementById('upcoming'),past=document.getElementById('past');if(!up||!past)return;
var now=new Date(),t=now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0');
var all=[].slice.call(document.querySelectorAll('.entry[data-end]'));
var u=all.filter(function(e){return e.dataset.end>=t}).sort(function(a,b){return a.dataset.start<b.dataset.start?-1:1});
var p=all.filter(function(e){return e.dataset.end<t}).sort(function(a,b){return a.dataset.start<b.dataset.start?1:-1});
u.forEach(function(e){up.appendChild(e)});p.forEach(function(e){past.appendChild(e)});
var none=document.getElementById('none-upcoming');if(none)none.style.display=u.length?'none':'';
all.forEach(function(e){var g=e.querySelector('a[href^="https://calendar.google.com"]');if(g)g.style.display=e.dataset.end>=t?'':'none'});
})();
</script>
"""


def build(lang):
    src = open(f"{DOCS}/{'pt/' if lang == 'pt' else ''}presentations.html", encoding="utf-8").read()
    ui = UI[lang]
    head, rest = src.split("<section class=\"pagehead\">", 1)
    tail = rest[rest.index("<footer"):]
    slug = "pt/events" if lang == "pt" else "events"
    head = re.sub(r"<title>[^<]*</title>", f"<title>{ui['title']}</title>", head)
    head = re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*"', lambda m: m.group(1) + ui["desc"] + '"', head)
    head = re.sub(r'(<meta (?:property|name)="(?:og|twitter):title" content=")[^"]*"', lambda m: m.group(1) + ui["title"] + '"', head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*"', lambda m: m.group(1) + BASE + slug + '"', head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*"', lambda m: m.group(1) + BASE + slug + '"', head)
    head = re.sub(r'(<link rel="alternate" hreflang="en" href=")[^"]*"', lambda m: m.group(1) + BASE + 'events"', head)
    head = re.sub(r'(<link rel="alternate" hreflang="pt" href=")[^"]*"', lambda m: m.group(1) + BASE + 'pt/events"', head)
    head = re.sub(r'(<link rel="alternate" hreflang="x-default" href=")[^"]*"', lambda m: m.group(1) + BASE + 'events"', head)
    # nav: active link
    head = head.replace(" class='active'", "")
    head = re.sub(r"<a href='events'>", "<a class='active' href='events'>", head)
    head = re.sub(r'<span class="lang">.*?</span>',
                  '<span class="lang"><a href="../events">EN</a><a href="events" class="on">PT</a></span>' if lang == "pt"
                  else '<span class="lang"><a href="#" class="on">EN</a><a href="pt/events">PT</a></span>', head, flags=re.S)
    ups = sorted([e for e in events if e["end"] >= today], key=lambda e: e["start"])
    pasts = sorted([e for e in events if e["end"] < today], key=lambda e: e["start"], reverse=True)
    ics_href = ("../" if lang == "pt" else "") + "events.ics"
    body = (f'<section class="pagehead"><p class="eyebrow">{ui["eyebrow"]}</p><h1>{ui["h1"]}</h1><p class="intro">{ui["intro"]}</p></section>\n'
            f'<div class="container">\n<p><a class="dl" style="margin:0" href="{ics_href}" download>{ui["ics"]}</a></p>\n'
            f'<h2 class="sec">{ui["up"]}</h2>\n<div id="upcoming">\n' + "".join(entry(e, lang, True) for e in ups) + "</div>\n"
            f'<p id="none-upcoming" class="intro"{" style=\"display:none\"" if ups else ""}>{ui["none_up"]}</p>\n'
            f'<h2 class="sec">{ui["past"]}</h2>\n<div id="past">\n' + "".join(entry(e, lang, False) for e in pasts) + "</div>\n"
            f'<p class="intro" style="margin-top:32px">{ui["note"]}</p>\n</div>\n')
    out = head + body + tail.replace("</body>", SCRIPT + "</body>")
    path = f"{DOCS}/{'pt/' if lang == 'pt' else ''}events.html"
    open(path, "w", encoding="utf-8").write(out)


def ics_escape(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def build_ics():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//nunocrato.org//Events//EN", "CALSCALE:GREGORIAN",
             "X-WR-CALNAME:Nuno Crato — events", "X-WR-TIMEZONE:Europe/Lisbon"]
    for e in sorted(events, key=lambda e: e["start"]):
        lines += ["BEGIN:VEVENT", f"UID:{e['start']}-{abs(hash(e['title'])) % 10**8 if False else re.sub(r'[^a-z0-9]+', '-', e['title'].lower())[:40]}@nunocrato.org", f"DTSTAMP:{now}"]
        if e.get("time"):
            lines += [f"DTSTART:{utc_stamp(d(e['start']), e['time'])}", f"DTEND:{utc_stamp(d(e['start']), end_of(e))}"]
        else:
            lines += [f"DTSTART;VALUE=DATE:{d(e['start']).strftime('%Y%m%d')}",
                      f"DTEND;VALUE=DATE:{(d(e['end']) + datetime.timedelta(days=1)).strftime('%Y%m%d')}"]
        lines += [f"SUMMARY:{ics_escape(e['title'])}", f"LOCATION:{ics_escape(e['place_en'])}", f"DESCRIPTION:{ics_escape(e['desc_en'])}"]
        ext = [l["url"] for l in e["links"] if l["url"].startswith("http")]
        if ext:
            lines.append(f"URL:{ext[0]}")
        lines.append("END:VEVENT")
    # fold long lines (75 octets)
    out = []
    for l in lines:
        b = l.encode("utf-8")
        while len(b) > 74:
            cut = 74
            while cut > 0 and (b[cut] & 0xC0) == 0x80:
                cut -= 1
            out.append(b[:cut].decode("utf-8")); b = b" " + b[cut:]
        out.append(b.decode("utf-8"))
    open(f"{DOCS}/events.ics", "w", encoding="utf-8", newline="").write("\r\n".join(out) + "\r\n")


for lang in ("en", "pt"):
    build(lang)
build_ics()
print(f"events: {len(events)} ({sum(1 for e in events if e['end'] >= today)} upcoming as of {today})")
