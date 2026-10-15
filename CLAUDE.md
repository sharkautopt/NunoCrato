# Nuno Crato — personal website (nunocrato.org)

Static site, no build step. Everything published lives in `docs/`; GitHub Pages serves that folder as-is
(Settings → Pages → branch `main`, folder `/docs`). Pushing to `main` redeploys automatically. Netlify is no longer used.

## Layout

- `docs/*.html` — seven pages: `index`, `research`, `publications`, `education`, `presentations`, `media`, `about`.
  Served at clean URLs (`/research`, `/media`, ...). Styles are in `docs/style.css` (the home page also has an inline `<style>`).
- `docs/presentations/YYYY-MM-DD-short-slug.pdf` — slide decks. Name new ones the same way.
- `docs/wp-content/uploads/...` — files migrated from the old WordPress site. **Never rename or move these:**
  old links from other websites, Google and QR codes in slides depend on the exact paths.
- `docs/images/` — images used by pages (home-page thumbnails are 84px squares, cropped to cover).
- `docs/documents/biographies/` — biography PDFs (EN, PT, ES).
- `docs/old-links.js` — loaded by `index.html`; sends old WordPress addresses (`/?p=…`, `/?page_id=…`, `/?cat=…`) to the
  right section (GitHub Pages has no server redirects). Generated: `python3 tools/make_old_links.py tools/old-wp-inventory.json docs/old-links.js`.
  `tools/old-wordpress-redirects.txt` is the old Netlify rule list, kept for reference only.
- `docs/404.html` — not-found page. `docs/.nojekyll` must stay. `docs/CNAME` holds the custom domain once DNS is switched.
- `tools/check_site.py` — link checker (see below).

## Conventions

- Newest first, inside year sections (`<h2 class="sec">2026</h2>`). English descriptions, original-language titles.
- Links to own files are relative, no leading slash (`presentations/...pdf`, `research`, brand link `./`), never
  `https://www.nunocrato.org/...`. (`404.html` is the exception: it uses absolute paths.)
  The only absolute own-domain URLs are the canonical/`og:`/`twitter:` meta tags (social cards need absolute URLs).
- The EN/PT switch in the header is a non-functional placeholder (`href="#"`). There are no Portuguese page versions.
- No trackers, no build tooling, no frameworks. Keep pages plain HTML.

## Markup to copy

Presentations page (`presentations.html`) and Media page (`media.html`) use the same entry block:

```html
<div class="entry"><div class="when">2026 · Sep</div><div><div class="et">Title</div><div class="ed">One-line description, place, date.</div><a class="dl" href="presentations/2026-09-17-slug.pdf">PDF</a></div></div>
```

External links add `target="_blank" rel="noopener"`. Entries without a file simply omit the `<a class="dl">`.

Home page "Recent activity" (`index.html`) shows the 5 most recent items; add new ones on top and drop the oldest
(make sure the dropped item still exists on the Media page):

```html
    <a class='feed-item' href='media'>
      <img class="feed-thumb" src="images/some-thumb.jpg" alt="">
      <div>
        <div class="feed-when">October 2026 · Book presentation</div>
        <div class="feed-title">Title · place</div>
      </div>
    </a>
```

## Checking a change

1. Serve the folder: `python3 -m http.server 8000 --directory docs` and open the changed pages.
2. Run `python3 tools/check_site.py docs` — it must report `problems: 0`.
3. Commit and push to `main`.

## Open items (as of 2026-10-15)

- (resolved 2026-10-15) Valladolid added to the Media page; Panamá host = SUMUN 2026 (Grupo Santillana); FNAC year = 2026.
- Three old PDFs with accented names were saved with ASCII names
  (`201709-Economistas-na-Educacao-1-1-1.pdf`, `20191210-PISA-2018-Publico-1-1.pdf`,
  `20200624-LUSA-Ensino-a-distancia-PUBLICO-1.pdf`); direct old links to the accented versions are not redirected.
