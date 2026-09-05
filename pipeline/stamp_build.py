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

!!! IT ALSO HASHED A STALE FILE QUITE HAPPILY (2026-07-30j).  On 2026-07-30i
`pageindex.json` was found eight days behind the volumes it indexes, and this
script had been dutifully hashing it and handing every visitor a fresh URL for
the wrong data.  3,774 cross-references — 13.4% of everything that resolved —
were landing on a paragraph that is not on the cited page, and none on the right
one.  Being newly distributed is not the same as being right.

So it now REFUSES TO STAMP when `pipeline/check_derived.py` reports a derived
artefact older than its sources.  Staleness has to block the publishing step,
because no other gate can see it: `check_layout` grades roles, `verify_apparatus`
counts notes, `regress check` compares side-maps to their own baseline.
`--force` overrides, and says so loudly.

!!! WHAT BUILD DOES NOT COVER, AND WHY HASHING THE HTML WOULD NOT FIX IT
(2026-08-01).  The 2026-07-31c note reads "`stamp_build.py` hashes JSON and
`i18n.js` but NOT the reader HTML, so an HTML-only fix moves no BUILD and
nothing forces a refetch."  The first half is true; the conclusion does not
follow, and adding the HTML to the hash would be a fix for the wrong thing.

BUILD only ever appears INSIDE a query string that this page builds:

    jget(url) -> fetch(url + '?v=' + BUILD)        and  i18n.js?v=BUILD

The HTML itself is fetched at its BARE URL — `/reader/reader2.html`, with no
buster anywhere (checked: `index.html` and `reader.html` both link to the bare
path, and the `?q=` on search results is a search term, not a version).  So
moving BUILD cannot make any browser re-fetch the HTML.  It would only hand
every returning visitor 1,691 fresh JSON URLs for data that had not changed —
the exact cost that made `stamp_build` idempotency worth fixing on 07-31b.

How long a visitor keeps stale HTML is set by GitHub Pages' own
`Cache-Control` and by the CDN, neither of which this repository controls.
The two things that DO work are already in place:
  * `verify_live.py` byte-compares the published HTML against this working
    copy, so a stale ORIGIN is detected rather than assumed;
  * when testing an HTML-only change, open it with a fresh query string or in
    a private window — the change is real, the copy on screen is not.
If stale HTML ever needs solving for real visitors rather than for testing, the
honest fix is in the page: fetch a small version marker and offer a reload when
it disagrees with the built-in BUILD.  Do not reach for the hash.

Run it LAST, after every builder and before deploying.
Usage: python3 pipeline/stamp_build.py [--write] [--force] [--fast]
"""
import hashlib, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
# every page that fetches data, not just the readers — `search.html` had no
# cache-buster either, and its index is rebuilt whenever a corpus is.
READERS = [os.path.join(SITE, 'reader', 'reader2.html'),
           os.path.join(SITE, 'reader', 'reader.html'),
           os.path.join(SITE, 'search.html'),
           os.path.join(SITE, 'errata.html'),
           os.path.join(SITE, 'downloads.html')]

sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import check_derived

# DEEP BY DEFAULT.  The mtime screen alone raised a false alarm the first time
# it ran — `pdfblanks.json` was older than two volumes that had been rewritten
# without changing anything it reads — and a gate that cries wolf teaches the
# operator to reach for --force, which is worse than no gate.  This step runs
# once per deploy; twenty seconds buys a proof instead of a guess.  `--fast`
# skips the rebuilds when you are only checking the wiring.
print('checking derived artefacts before stamping:')
_stale = check_derived.run(deep='--fast' not in sys.argv)
if _stale:
    if '--force' not in sys.argv:
        print('\nREFUSING TO STAMP. A derived artefact is older than its sources, so the\n'
              'stamp would publish stale data under a fresh cache-buster — exactly the\n'
              'failure of 2026-07-30i. Rebuild as shown above, or pass --force.')
        sys.exit(2)
    print('\n--force: STAMPING OVER %d STALE ARTEFACT(S). The site will serve them.' % _stale)
print()

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
        # searchcore.js joined it on 2026-09-05: one search implementation for
        # both pages, loaded by <script src>, versioned the same way.
        if not (f.endswith('.json') or f in ('i18n.js', 'searchcore.js')):
            continue
        p = os.path.join(base, f)
        st = os.stat(p)
        h.update(('%s|%d|%d\n' % (os.path.relpath(p, SITE), st.st_size,
                                  int(st.st_mtime))).encode())
        n += 1
stamp = h.hexdigest()[:12]
print('%d JSON + i18n/searchcore file(s) under site/  ->  BUILD %s' % (n, stamp))

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
# !!! AND THE READER ITSELF CARRIES NO CACHE-BUSTER (fixed here 2026-08-03).
# `reader2.html` versions everything it FETCHES and nothing versions the page,
# so an HTML-only change reaches a returning visitor only when their cache
# expires.  It has cost a round-trip on nearly every check for two days -- and
# worse than a delay: on 2026-08-03 the reader photographed a fault that was
# already fixed, because his browser was running the previous reader over the
# rebuilt data, and the two disagreed on screen exactly where the old code and
# the new data met.
#
# So the stamp is also published as a tiny file the page can fetch with a
# cache-defeating query, and the page compares it with its own constant.  This
# file is the only thing in the site that must never be served stale, and it is
# 30 bytes.
if '--write' in sys.argv:
    # `date` rides beside the hash (2026-08-09, reader request): the version
    # chip's tooltip shows when the site was last updated, and because this
    # line runs on EVERY stamp, nobody has to remember to bump it — which is
    # how the citation files fell behind.
    #
    # !!! "TRUE BY CONSTRUCTION" IS WHAT THIS COMMENT USED TO CLAIM, AND IT IS
    # FALSE.  It is true by construction only if the stamping machine's clock is
    # right.  On 2026-09-05 an agent sandbox read `Aug 26` and this line wrote
    # `"date": "2026-08-26"` into build.json, which then SHIPPED and was served
    # in the version chip.  That is the SECOND time this project has been bitten
    # by that clock — the first is the 08-23/08-26 correction in NEXT_SESSION.md.
    # So: if you are stamping from a sandbox, check `date` against the date the
    # environment states before pushing, because nothing downstream will.
    import datetime
    with open(os.path.join(SITE, 'build.json'), 'w', encoding='utf-8') as fh:
        json.dump({'build': stamp,
                   'date': datetime.date.today().isoformat()}, fh)
    print('   site/build.json      %s' % stamp)

# Version every <script src="…i18n.js"> so a new stamp forces a re-fetch.
I18N_SRC = re.compile(r'(<script src="[^"]*(?:i18n|searchcore)\.js)(\?v=[^"]*)?(")')
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
