# Nuno Crato — personal website (nunocrato.org)

Static site, no build step. Everything published lives in `site/`; Netlify serves that folder as-is
(`netlify.toml` sets `publish = "site"`). Pushing to `main` redeploys automatically.

## Layout

- `site/*.html` — seven pages: `index`, `research`, `publications`, `education`, `presentations`, `media`, `about`.
  Served at clean URLs (`/research`, `/media`, ...). Styles are in `site/style.css` (the home page also has an inline `<style>`).
- `site/presentations/YYYY-MM-DD-short-slug.pdf` — slide decks. Name new ones the same way.
- `site/wp-content/uploads/...` — files migrated from the old WordPress site. **Never rename or move these:**
  old links from other websites, Google and QR codes in slides depend on the exact paths.
- `site/images/` — images used by pages (home-page thumbnails are 84px squares, cropped to cover).
- `site/documents/biographies/` — biography PDFs (EN, PT, ES).
- `site/_redirects` — redirects from old WordPress addresses (`/?p=…`, `/?page_id=…`, `/?cat=…`) and from `*.html`
  page names. Keep it; extend it when a page is renamed.
- `tools/check_site.py` — link checker (see below).

## Conventions

- Newest first, inside year sections (`<h2 class="sec">2026</h2>`). English descriptions, original-language titles.
- Links to own files are relative to the site root (`/presentations/...pdf`), never `https://www.nunocrato.org/...`.
  The only absolute own-domain URLs are the canonical/`og:`/`twitter:` meta tags (social cards need absolute URLs).
- The EN/PT switch in the header is a non-functional placeholder (`href="#"`). There are no Portuguese page versions.
- No trackers, no build tooling, no frameworks. Keep pages plain HTML.
- Do not add the `.netlify` folder to git (it is in `.gitignore`).

## Markup to copy

Presentations page (`presentations.html`) and Media page (`media.html`) use the same entry block:

```html
<div class="entry"><div class="when">2026 · Sep</div><div><div class="et">Title</div><div class="ed">One-line description, place, date.</div><a class="dl" href="/presentations/2026-09-17-slug.pdf">PDF</a></div></div>
```

External links add `target="_blank" rel="noopener"`. Entries without a file simply omit the `<a class="dl">`.

Home page "Recent activity" (`index.html`) shows the 5 most recent items; add new ones on top and drop the oldest
(make sure the dropped item still exists on the Media page):

```html
    <a class='feed-item' href='/media'>
      <img class="feed-thumb" src="/images/some-thumb.jpg" alt="">
      <div>
        <div class="feed-when">October 2026 · Book presentation</div>
        <div class="feed-title">Title · place</div>
      </div>
    </a>
```

## Checking a change

1. Serve the folder: `python3 -m http.server 8000 --directory site` and open the changed pages.
2. Run `python3 tools/check_site.py site` — it must report `problems: 0`.
3. Commit and push to `main`.

## Open items (as of 2026-10-15)

- Valladolid, XXVI Encuentro Internacional de la Inspección de Educación (30 Sep – 2 Oct): not added; participation
  and year not confirmed.
- Panamá lecture (17 Sep 2026): host event/organisation unknown.
- "Machine Learning com Python" presentation (FNAC Colombo, 14 Oct): flyer shows no year; assumed 2026.
- Three old PDFs with accented names were saved with ASCII names
  (`201709-Economistas-na-Educacao-1-1-1.pdf`, `20191210-PISA-2018-Publico-1-1.pdf`,
  `20200624-LUSA-Ensino-a-distancia-PUBLICO-1.pdf`); direct old links to the accented versions are not redirected.
