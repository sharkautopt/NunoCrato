#!/bin/sh
# Full rebuild after any content change. Run from the repo root.
set -e
python3 tools/make_docs.py rewrite
python3 tools/make_pt.py > /dev/null
python3 tools/make_docs.py build
python3 tools/make_events.py
python3 tools/make_sitemap.py
python3 tools/check_site.py docs
