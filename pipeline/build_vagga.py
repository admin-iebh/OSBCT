#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE `vagga` FIELD DOES NOT HOLD A VAGGA. BUILD ONE THAT DOES.

WHY.  Measured 2026-08-03 (`claude/the_commentary_states_its_own_position.md`):
296 of 320 ordinal-condemned links could not be repaired because the region
selector had nothing to select on.  `12Sam01` paragraphs carry 32 distinct
`vagga` values against the volume's 95 vagga headings, and the values include
`Nidānavaggasaṁyuttapāḷi` -- a piṭaka-level title -- and bare `Paṭhamavagga`,
which names no vagga at all.  It is whatever heading the structure parse last
saw, forward-filled.

THE EDITION ALREADY SAYS IT, TWICE, AND BOTH STATEMENTS ARE ALREADY EXTRACTED.
`headings` carries `kind: "vagga"` entries of two shapes:

    {"kind":"vagga","n":1,   "title":"Naḷavagga",        "pdf_page":38}   OPENER
    {"kind":"vagga","n":null,"title":"Naḷavaggo paṭhamo.","pdf_page":42}  CLOSER

The opener carries the edition's own vagga number; the closer names the same
vagga in the nominative and states its ordinal in words.  So `n is not None`
separates them -- no regex required -- and the two can be checked against each
other, which is what `--check` does.

WHERE ONLY CLOSERS SURVIVE (`05Kankha`, `20Khu03`) the vagga still has a name and
an end: it runs from the previous closer to this one.  That is used, and marked
`from: "closer"` so a reader of the output can tell the two apart.

BOUNDARIES ARE PAGE-ANCHORED, WHICH IS AN ESTIMATE.  A heading carries
`pdf_page` and nothing finer, and several suttas share a page, so a boundary
taken from the page alone can put the last sutta of one vagga into the next.
Where `sutta_n` is parsed it resets to 1 at exactly the boundary, so a reset on
or beside the heading's page SNAPS the boundary to it.  604 of 732 resets
already coincide with an opener page, which is the cross-check for this.

WRITES TO `_xc/vagga/`, NEVER INTO `site/`.  Defect 3 of `build_links_bynum.py`:
`site/` is published and hashed into BUILD, so writing there would move the
cache-buster for every visitor before anyone has judged the output.

WHAT IT MEASURED, 2026-08-03.  1,620 vaggas over 33,287 paragraphs -- 39% of the
corpus, and the 61% is an acknowledged gap rather than a guess: 38 volumes print
no vagga heading at all, and 19 more print one near the front and none after, so
they are refused by the guard below.  The edition's two statements agree with
each other **97.9%** of the time (512 of 523): where both an opener and its
closer survive, the closer's ordinal word matches the opener's number.  409 of
1,620 boundaries snapped to a `sutta_n` reset.

Against the field it replaces, on `direct` cross-layer links: the old
paragraph `vagga` field names both sides of 15,066 links and the two names agree
49.6% of the time; this one names both sides of 8,403 and agrees **65.6%**.
Fewer answers, better answers, and it does not answer where it does not know.

IT DID NOT RESCUE THE CORRECTOR, and that is recorded rather than buried --
`_xc/ordinal_corrector2.py`.  It halved the dead zone (296 -> 180 `no_region`)
and still proposes nothing better: 30 proposals of 320, 3.7% name agreement
against the current link's 3.4%.  The limit was never the region.  Of the 320,
only 92 have the canon's vagga missing from the target volume; **195 have the
vagga present and no paragraph in it stating the wanted ordinal**, because the
ordinal is printed on 3,617 paragraphs out of 86,365.  A placement rule cannot
place onto a paragraph that says nothing.

Usage:
  python3 pipeline/build_vagga.py            # build into _xc/vagga/
  python3 pipeline/build_vagga.py --check    # build, then report and cross-check
"""
import json, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, 'site')
OUT = os.path.join(ROOT, '_xc', 'vagga')
VOLFILE = re.compile(r'^\d\d[A-Za-z][A-Za-z0-9]*\.json$')

# nominative masculine of the same ordinals the commentary uses in the locative
NOM = {'paṭhamo':1,'dutiyo':2,'tatiyo':3,'catuttho':4,'pañcamo':5,'chaṭṭho':6,
       'sattamo':7,'aṭṭhamo':8,'navamo':9,'dasamo':10,'ekādasamo':11,
       'dvādasamo':12,'bārasamo':12,'terasamo':13,'telasamo':13,'teḷasamo':13,
       'cuddasamo':14,'catuddasamo':14,'coddasamo':14,'pannarasamo':15,
       'paṇṇarasamo':15,'pañcadasamo':15,'soḷasamo':16,'sattarasamo':17,
       'sattadasamo':17,'aṭṭhārasamo':18,'aṭṭhadasamo':18,'ekūnavīsatimo':19,
       'vīsatimo':20,'ekavīsatimo':21,'bāvīsatimo':22,'dvāvīsatimo':22,
       'tevīsatimo':23,'catuvīsatimo':24,'pañcavīsatimo':25,'chabbīsatimo':26,
       'sattavīsatimo':27,'aṭṭhavīsatimo':28,'ekūnatiṁsatimo':29,'tiṁsatimo':30}
CLOSER = re.compile(r'^(?P<name>.+?vagg)o\d*\s+(?P<ord>[a-zāīūṁṅñṭḍṇḷ]+)\s*\.?\s*$', re.I)
LEAD = re.compile(r'^[\d\s.,\-–()]+')


def stem(s):
    """A comparable core.  Strips the printed numbering, then the -vagga /
    -vaggo tail, so `Naḷavagga` and `Naḷavaggo paṭhamo.` reduce alike."""
    s = (s or '').strip().lower()
    s = LEAD.sub('', s)
    s = re.sub(r'[^a-zāīūṁṃṅñṭḍṇḷ]', '', s)
    s = re.sub(r'vagg[ao]?(vaṇṇanā)?$', '', s)
    return s


def sn(p):
    try:
        return int(p.get('sutta_n'))
    except (TypeError, ValueError):
        return None


def build(v):
    d = json.load(open(os.path.join(SITE, v + '.json'), encoding='utf-8'))
    ps = d.get('paragraphs') or []
    hs = [h for h in (d.get('headings') or []) if h.get('kind') == 'vagga']
    openers = [h for h in hs if h.get('n') is not None]
    closers = []
    for h in hs:
        if h.get('n') is not None:
            continue
        m = CLOSER.match((h.get('title') or '').strip())
        if m:
            closers.append((h, m.group('name'), NOM.get(m.group('ord').lower())))

    # --- where each paragraph sits, by page
    pages = [p.get('pdf_page') or 0 for p in ps]
    resets = set()
    prev = None
    for i, p in enumerate(ps):
        s = sn(p)
        if s is None:
            continue
        if s == 1 and (prev is None or prev > 1):
            resets.add(i)
        prev = s

    def first_on_or_after(page):
        for i, pg in enumerate(pages):
            if pg >= page:
                return i
        return len(ps)

    def snap(i, page):
        """A page-anchored boundary is an estimate; a `sutta_n` reset on the
        same page or the one before it is not.  Prefer the reset."""
        best = None
        for r in resets:
            if abs((pages[r] or 0) - page) <= 1 and abs(r - i) <= 12:
                if best is None or abs(r - i) < abs(best - i):
                    best = r
        return best if best is not None else i

    bounds = []          # (start_index, name, n, source)
    if openers:
        for h in openers:
            i = first_on_or_after(h.get('pdf_page') or 0)
            bounds.append([snap(i, h.get('pdf_page') or 0),
                           (h.get('title') or '').strip(), h.get('n'), 'opener'])
    elif closers:
        # the vagga ENDS at the closer; it starts after the previous one
        start = 0
        for h, name, ordn in closers:
            end = first_on_or_after(h.get('pdf_page') or 0)
            bounds.append([start, name + 'a', ordn, 'closer'])
            start = min(end + 1, len(ps))
    bounds.sort(key=lambda b: b[0])
    # a boundary may not go backwards
    for k in range(1, len(bounds)):
        if bounds[k][0] <= bounds[k - 1][0]:
            bounds[k][0] = bounds[k - 1][0] + 1

    # A REGION THAT COVERS THE WHOLE VOLUME IS NOT A VAGGA.  19 volumes carry a
    # single vagga heading near the front and none after -- `20Khu03` would put
    # all 4,461 paragraphs in `Buddhavagga`, `09Ma01` all 511 in
    # `Mūlapariyāyavagga`.  Assigning those inflates coverage and makes the
    # stated ordinal ambiguous inside a region that is really a whole nikāya.
    # Where fewer than three boundaries were found and they would swallow the
    # volume, emit nothing and say so: an acknowledged gap, not a wrong answer.
    if len(bounds) < 3 and len(ps) > 120:
        return d, ps, hs, openers, closers, resets, [], {}

    out = {}
    for k, b in enumerate(bounds):
        a = b[0]
        z = bounds[k + 1][0] - 1 if k + 1 < len(bounds) else len(ps) - 1
        for i in range(max(0, a), min(z, len(ps) - 1) + 1):
            out[i] = {'vagga': b[1], 'stem': stem(b[1]), 'n': b[2], 'from': b[3]}
    return d, ps, hs, openers, closers, resets, bounds, out


def main():
    os.makedirs(OUT, exist_ok=True)
    vols = sorted(f[:-5] for f in os.listdir(SITE) if VOLFILE.match(f))
    T = collections.Counter()
    rows = []
    for v in vols:
        d, ps, hs, openers, closers, resets, bounds, out = build(v)
        json.dump({'vol': v, 'source': 'headings kind=vagga',
                   'vaggas': len(bounds), 'byOrd': {str(k): x for k, x in out.items()}},
                  open(os.path.join(OUT, v + '.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False)
        # cross-check: does the closer's word agree with the opener's number?
        ok = bad = 0
        if openers and closers:
            byname = {}
            for h in openers:
                byname.setdefault(stem(h.get('title')), []).append(h.get('n'))
            for h, name, ordn in closers:
                got = byname.get(stem(name))
                if got and ordn is not None:
                    if ordn in got:
                        ok += 1
                    else:
                        bad += 1
        snapped = sum(1 for b in bounds if b[0] in resets)
        T['paras'] += len(ps)
        T['assigned'] += len(out)
        T['vaggas'] += len(bounds)
        T['xok'] += ok
        T['xbad'] += bad
        T['snapped'] += snapped
        if bounds:
            rows.append((v, len(ps), len(out), len(bounds), snapped, ok, bad,
                         bounds[0][3]))
    if '--check' not in sys.argv:
        print('wrote %d volumes to %s' % (len(vols), OUT))
        return
    print('%-11s %6s %6s %5s %6s %6s %5s %5s  %s'
          % ('vol', 'paras', 'assign', '%', 'vaggas', 'snapped', 'x-ok', 'x-bad', 'from'))
    for r in rows:
        print('%-11s %6d %6d %4.0f%% %6d %6d %5d %5d  %s'
              % (r[0], r[1], r[2], 100.0 * r[2] / max(1, r[1]), r[3], r[4], r[5], r[6], r[7]))
    print('-' * 66)
    print('%-11s %6d %6d %4.0f%% %6d %6d %5d %5d'
          % ('TOTAL', T['paras'], T['assigned'], 100.0 * T['assigned'] / max(1, T['paras']),
             T['vaggas'], T['snapped'], T['xok'], T['xbad']))
    if T['xok'] + T['xbad']:
        print('\ncloser word vs opener number: %.1f%% agree (%d of %d)'
              % (100.0 * T['xok'] / (T['xok'] + T['xbad']), T['xok'], T['xok'] + T['xbad']))
    print('boundaries snapped to a sutta_n reset: %d of %d' % (T['snapped'], T['vaggas']))


if __name__ == '__main__':
    main()
