#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE 44.8% IS TWO DIFFERENT THINGS. SEPARATE THEM BEFORE REPAIRING ANY OF IT.

`pipeline/check_links.py` reports that 44.8% of numbered link targets land on a
paragraph whose printed number is not the number the record itself carries.
`claude/links_repaired_by_name.md` says plainly what is not known about that
figure: *"Much of that is layers whose numbering genuinely does not correspond
— a different fault from a mis-aimed link — but it has not been separated."*

Repairing it undifferentiated would invent a fault where the two layers simply
number differently, and quoting it undifferentiated overstates the damage.  So
this script decides nothing and writes nothing.  It splits the residue.

THE EVIDENCE IS THE ONE ALREADY IN THE FILES, and it is not the number.  A
commentary paragraph opens by QUOTING the canon words it is about, and
`bold/<VOL>.bold.json` marks those quotations from the edition's own typography.
So for a residue link, ask the question `_xc/classc_lemma.py` already asks:

    does the TARGET paragraph's bolded lemma occur in the canon paragraph
    that links to it?

  hit          the target really is commenting on this passage.  The number
               disagrees because the layers number differently.  NOT A FAULT.
  no hit, but
  a candidate
  elsewhere
  hits         the target is wrong AND a better one exists.  A real, fixable
               fault -- this is the part worth repairing.
  no hit
  anywhere     undecidable here.  Say so; do not count it as either.

CANDIDATES are drawn from two places, both cheap and both principled: the
paragraphs in the target volume that CARRY the proposed number (the number
proposes -- there are usually several, which is the whole problem), and a
window either side of where the link currently points (the builder's walk
lands near, not far).

THE CONTROL IS NOT OPTIONAL.  Pāḷi is formulaic and a short quotation recurs,
so a bare hit rate says nothing.  Every rate here is printed beside the same
test run against a canon paragraph k places away.  A repair rule is only worth
building if the signal stands clear of that floor.

Usage:  python3 _xc/residue_split.py [--limit N] [--window W]
Writes nothing.  Prints a table.
"""
import json, os, re, sys, collections, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')
BOLD = os.path.join(SITE, 'reader', 'bold')
RANGE = re.compile(r'^\s*(\d+)\s*[-–]\s*(\d+)\s*\.')
WINDOW = 8
MINLEN = 6
MAXLEM = 4

_p, _b, _bynum = {}, {}, {}


def P(v):
    if v not in _p:
        q = os.path.join(SITE, v + '.json')
        try:
            d = json.load(open(q, encoding='utf-8'))
            _p[v] = d.get('paragraphs') or d.get('paras') or []
        except Exception:
            _p[v] = []
    return _p[v]


def B(v):
    if v not in _b:
        q = os.path.join(BOLD, v + '.bold.json')
        try:
            _b[v] = json.load(open(q, encoding='utf-8'))
        except Exception:
            _b[v] = {}
    return _b[v]


def bynum(v):
    """number -> [ordinals bearing it], including the ends of a range."""
    if v not in _bynum:
        m = collections.defaultdict(list)
        for i, q in enumerate(P(v)):
            n = q.get('n')
            if n is not None:
                m[n].append(i)
            r = RANGE.match(q.get('text') or '')
            if r:
                for k in range(int(r.group(1)), int(r.group(2)) + 1):
                    if i not in m[k]:
                        m[k].append(i)
        _bynum[v] = m
    return _bynum[v]


def norm(s):
    return re.sub(r'[^a-zāīūṁṅñṭḍṇḷ ]', ' ',
                  unicodedata.normalize('NFC', s or '').lower())


def squash(s):
    return re.sub(r'\s+', ' ', s).strip()


_lemcache = {}


def lemmas(vol, ord_):
    """The quotations the TARGET paragraph opens with, from the edition's own
    bold typography -- never from a number."""
    k = (vol, ord_)
    if k in _lemcache:
        return _lemcache[k]
    out = []
    b, ps = B(vol), P(vol)
    if b and 0 <= ord_ < len(ps):
        t = ps[ord_].get('text') or ''
        for a, z in (b.get(str(ord_)) or []):
            w = re.sub(r'\s*n?ti$', '', squash(norm(t[a:z]))).strip()
            if len(w) >= MINLEN:
                out.append(w)
        out = sorted(set(out), key=len, reverse=True)[:MAXLEM]
    _lemcache[k] = out
    return out


def hits(vol, ord_, body):
    lem = lemmas(vol, ord_)
    if not lem:
        return None                     # no evidence either way
    return any(l in body for l in lem)


def run(shift=0, limit=0, window=WINDOW):
    cls = collections.Counter()
    bycanon = collections.defaultdict(collections.Counter)
    examples = []
    seen = 0
    for fn in sorted(os.listdir(LINKS)):
        if not fn.endswith('.links.json'):
            continue
        cv = fn[:-len('.links.json')]
        cps = P(cv)
        if not cps:
            continue
        L = json.load(open(os.path.join(LINKS, fn), encoding='utf-8'))
        for ordk, e in L.items():
            i = int(ordk)
            ci = i + shift
            if not (0 <= ci < len(cps)):
                continue
            body = None
            for slot in ('commentary', 'subcommentary'):
                for t in (e.get(slot) or []):
                    key, n = t.get('key') or '', t.get('n')
                    if n is None or '#' not in key:
                        continue
                    tv, to = key.rsplit('#', 1)
                    to = int(to)
                    ps = P(tv)
                    if not ps or to >= len(ps):
                        continue
                    q = ps[to]
                    m = RANGE.match(q.get('text') or '')
                    if q.get('n') == n or (m and int(m.group(1)) <= n <= int(m.group(2))):
                        cls['aligned (not residue)'] += 1
                        continue
                    # ---- this target is the residue
                    seen += 1
                    if limit and seen > limit:
                        return cls, bycanon, examples
                    if body is None:
                        body = squash(norm(cps[ci].get('text') or ''))
                    here = hits(tv, to, body)
                    if here:
                        cls['CONFIRMED where it stands'] += 1
                        bycanon[cv]['confirmed'] += 1
                        continue
                    # candidates: paragraphs carrying the proposed number, and
                    # a window around where the link currently points
                    cand = [o for o in bynum(tv).get(n, []) if o != to]
                    cand += [o for o in range(max(0, to - window),
                                              min(len(ps), to + window + 1))
                             if o != to]
                    good, ev = [], 0
                    for o in dict.fromkeys(cand):
                        h = hits(tv, o, body)
                        if h is None:
                            continue
                        ev += 1
                        if h:
                            good.append(o)
                    if here is None and not ev:
                        cls['undecidable (no quotation anywhere)'] += 1
                        bycanon[cv]['undecidable'] += 1
                    elif len(good) == 1:
                        cls['MIS-AIMED, one better target'] += 1
                        bycanon[cv]['misaimed'] += 1
                        if len(examples) < 25 and not shift:
                            examples.append((cv, i, key, n, good[0],
                                             ps[good[0]].get('n')))
                    elif len(good) > 1:
                        cls['MIS-AIMED, several candidates'] += 1
                        bycanon[cv]['ambiguous'] += 1
                    else:
                        cls['no better target found'] += 1
                        bycanon[cv]['nobetter'] += 1
    return cls, bycanon, examples


def main():
    limit = 0
    window = WINDOW
    if '--limit' in sys.argv:
        limit = int(sys.argv[sys.argv.index('--limit') + 1])
    if '--window' in sys.argv:
        window = int(sys.argv[sys.argv.index('--window') + 1])
    cls, bycanon, examples = run(0, limit, window)
    res = sum(v for k, v in cls.items() if k != 'aligned (not residue)')
    print('THE RESIDUE, SPLIT   (window +-%d, lemma >= %d chars)\n' % (window, MINLEN))
    print('%-40s %8s %8s' % ('', 'targets', 'of residue'))
    for k in ('aligned (not residue)', 'CONFIRMED where it stands',
              'MIS-AIMED, one better target', 'MIS-AIMED, several candidates',
              'no better target found', 'undecidable (no quotation anywhere)'):
        n = cls.get(k, 0)
        pct = ('%7.1f%%' % (100.0 * n / res)) if res and k != 'aligned (not residue)' else ''
        print('%-40s %8d %9s' % (k, n, pct))
    print('%-40s %8d' % ('residue total', res))

    print('\nCONTROL — the same test against a canon paragraph k places away.')
    print('A rate that does not fall here is vocabulary, not alignment.')
    print('%-8s %12s %12s' % ('shift', 'confirmed', 'one better'))
    base_c = cls.get('CONFIRMED where it stands', 0)
    base_m = cls.get('MIS-AIMED, one better target', 0)
    print('%-8s %11.1f%% %11.1f%%' % ('0', 100.0 * base_c / max(res, 1),
                                      100.0 * base_m / max(res, 1)))
    for k in (1, 5, 25):
        c2, _, _ = run(k, limit, window)
        r2 = sum(v for kk, v in c2.items() if kk != 'aligned (not residue)')
        print('%-8d %11.1f%% %11.1f%%'
              % (k, 100.0 * c2.get('CONFIRMED where it stands', 0) / max(r2, 1),
                 100.0 * c2.get('MIS-AIMED, one better target', 0) / max(r2, 1)))

    print('\nBY CANON VOLUME — residue >= 200, most mis-aimed first:')
    rows = []
    for v, c in bycanon.items():
        tot = sum(c.values())
        if tot >= 200:
            rows.append((v, tot, c['confirmed'], c['misaimed'], c['ambiguous'],
                         c['nobetter'], c['undecidable']))
    print('%-10s %8s %10s %9s %10s %9s %11s'
          % ('volume', 'residue', 'confirmed', 'one-fix', 'ambiguous',
             'no-better', 'undecidable'))
    for r in sorted(rows, key=lambda x: -x[3])[:25]:
        print('%-10s %8d %10d %9d %10d %9d %11d' % r)

    print('\nEXAMPLES of "mis-aimed, one better target" (canon -> current, n, better):')
    for cv, i, key, n, better, bn in examples[:15]:
        print('   %-10s #%-6d n=%-6s %-16s -> ord %-6d (n=%s)'
              % (cv, i, n, key, better, bn))


if __name__ == '__main__':
    main()
