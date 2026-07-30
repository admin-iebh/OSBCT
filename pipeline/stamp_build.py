#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stamp the reader's cache-buster from the DATA, so a rebuild can never be
invisible to a returning visitor.

WHY THIS EXISTS.  `reader2.html` fetches every JSON through

    jget(url) -> fetch(url + '?v=' + BUILD)

and `BUILD` was a hand-typed constant.  It was last touched on 2026-07-28u, so
every data change after that date — the seven Vinaya Ṭīkā, the five Dīgha, the
three Majjhima, every relink and apparatus rebuild, `pdfblanks.json`,
`pagespan.json` — kept the SAME URL and every returning browser went on serving
the old file from cache.  Reported 2026-07-29t as "Ganthārambhakathāvaṇṇanā
still starts on page 52": the reader was new, the corpus it loaded was not, and
the header gave it away — `08DiT01 · 303 ¶` where the rebuilt volume has 315.

THE STAMP IS DERIVED, NOT TYPED.  It hashes the name, size and mtime of every
file the reader can fetch, so any rebuild moves it and no rebuild can fail to.
A fresh git checkout moves the mtimes and so moves the stamp once, which costs
one cache miss and is the safe direction to err in.

Run it LAST, after every builder and before deploying.
Usage: python3 pipeline/stamp_build.py [--write]
"""
import hashlib, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
# every page that fetches data, not just the readers — `search.html` had no
# cache-buster either, and its index is rebuilt whenever a corpus is.
READERS = [os.path.join(SITE, 'reader', 'reader2.html'),
           os.path.join(SITE, 'reader', 'reader.html'),
           os.path.join(SITE, 'search.html'),
           os.path.join(SITE, 'errata.html'),
           os.path.join(SITE, 'downloads.html')]

h = hashlib.sha1()
n = 0
for base, dirs, files in os.walk(SITE):
    dirs[:] = sorted(d for d in dirs if d not in ('.git',))
    for f in sorted(files):
        # !!! i18n.js MUST BE IN THE HASH AND MUST CARRY A BUSTER (2026-07-30f).
        # The stamp used to cover JSON only.  When the tooltip keys were added,
        # BUILD did not move, so a returning visitor would have kept a CACHED
        # i18n.js while loading the NEW html — and `t()` returns the KEY when a
        # key is missing, so every wired tooltip would have read `tip_toc`,
        # `tip_nav`, `tip_larger` on screen.  Hashing it and versioning the
        # <script src> is what stops that.
        if not (f.endswith('.json') or f == 'i18n.js'):
            continue
        p = os.path.join(base, f)
        st = os.stat(p)
        h.update(('%s|%d|%d\n' % (os.path.relpath(p, SITE), st.st_size,
                                  int(st.st_mtime))).encode())
        n += 1
stamp = h.hexdigest()[:12]
print('%d JSON + i18n file(s) under site/  ->  BUILD %s' % (n, stamp))

for rp in READERS:
    if not os.path.exists(rp):
        continue
    s = open(rp, encoding='utf-8').read()
    m = re.search(r"const BUILD='([^']*)'", s)
    if not m:
        print('   %s carries no BUILD constant — skipped' % os.path.basename(rp))
        continue
    print('   %-13s %s -> %s' % (os.path.basename(rp), m.group(1), stamp))
    if '--write' in sys.argv:
        open(rp, 'w', encoding='utf-8').write(
            s[:m.start(1)] + stamp + s[m.end(1):])
# Version every <script src="…i18n.js"> so a new stamp forces a re-fetch.
I18N_SRC = re.compile(r'(<script src="[^"]*i18n\.js)(\?v=[^"]*)?(")')
pages = [os.path.join(b, f) for b, d, fs in os.walk(SITE) for f in fs
         if f.endswith('.html')]
touched = 0
for pp in sorted(pages):
    s = open(pp, encoding='utf-8').read()
    if not I18N_SRC.search(s):
        continue
    out = I18N_SRC.sub(lambda m: m.group(1) + '?v=' + stamp + m.group(3), s)
    if out != s:
        touched += 1
        if '--write' in sys.argv:
            open(pp, 'w', encoding='utf-8').write(out)
print('   i18n.js cache-buster: %d page(s) %s'
      % (touched, 'updated' if '--write' in sys.argv else 'would be updated'))

if '--write' not in sys.argv:
    print('DRY RUN — pass --write')
