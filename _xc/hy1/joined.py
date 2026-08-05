# -*- coding: utf-8 -*-
"""How many printed line breaks does the corpus lose INSIDE a side-map entry?

A verse `after`/`before`/`groups` entry is one DRAWN line.  Where the printed page
sets that same text over several lines, the break is lost.

Matched by FULL normalised equality of the entry against a printed block's joined
text -- never by prefix.  `_xc/hy1/dyad.py` matched a 24-character prefix and, on
a text as formulaic as the Dhammasangani, matched `cittapassaddhi` to
`cittapaguññata`; every number it produced was wrong and is discarded.

The corpus `pdf_page` anchor and the block map's page index do not always agree
(29Abhi01 anchors para 121 on 33 while the block map has 121 on 34), so a window
of +/-2 pages is searched and the page that matches is reported.
"""
import json, os, sys, re, collections

NRM = re.compile(r'[^0-9A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]')
n = lambda s: NRM.sub('', s or '')
B = '_xc/hy1/blocks2'
sys.path.insert(0, os.path.abspath('_xc/hy1'))
import adjudicate as A
A.B = B


def scan(vol):
    try:
        BL = json.load(open('%s/%s.json' % (B, vol), encoding='utf-8'))
        V = json.load(open('site/reader/verse/%s.json' % vol, encoding='utf-8'))
        D = json.load(open('site/%s.json' % vol, encoding='utf-8'))
    except Exception:
        return None
    margin = A.vol_margin(vol, BL)
    blocks = {}
    for pg, p in BL.items():
        bs = []
        for k, b in A.judge_page(p, margin)[2]:
            bs.append((n(' '.join(l[3] for l in b)), len(b), b))
        blocks[int(pg)] = bs
    ps = D['paragraphs']
    st = collections.Counter()
    ex = []
    for i, p in enumerate(ps):
        e = V.get(str(i))
        if not e:
            continue
        pg0 = p.get('pdf_page')
        if not isinstance(pg0, int):
            continue
        entries = []
        for key in ('before', 'after'):
            entries += [(key, x) for x in (e.get(key) or []) if isinstance(x, str)]
        for g in (e.get('groups') or []):
            if isinstance(g, dict):
                for ln in (g.get('gatha') or []):
                    entries.append(('groups', ln))
        for key, txt in entries:
            t = n(txt)
            if len(t) < 12:
                continue
            st['entries'] += 1
            hit = None
            for pg in (pg0, pg0 + 1, pg0 - 1, pg0 + 2, pg0 - 2):
                for bt, nl, b in blocks.get(pg, []):
                    if bt == t:
                        hit = (pg, nl, b); break
                if hit:
                    break
            if not hit:
                st['unmatched'] += 1
                continue
            st['matched'] += 1
            if hit[1] > 1:
                st['JOINED'] += 1
                st['lines_lost'] += hit[1] - 1
                if len(ex) < 3:
                    ex.append((p.get('n'), key, [l[3][:58] for l in hit[2]], txt[:70]))
    return st, ex


if __name__ == '__main__':
    vols = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(B))
    tot = collections.Counter()
    rows = []
    for v in vols:
        r = scan(v)
        if not r:
            continue
        st, ex = r
        tot.update(st)
        if st['JOINED']:
            rows.append((v, st['JOINED'], st['lines_lost'], st['matched'], st['entries']))
        if len(vols) <= 3:
            for nn, k, blines, t in ex:
                print('  para %s [%s] page sets %d lines:' % (nn, k, len(blines)))
                for l in blines:
                    print('       | %s' % l)
                print('    corpus ONE: %s' % t)
    print()
    print('entries %d  matched %d  unmatched %d' % (tot['entries'], tot['matched'], tot['unmatched']))
    print('ENTRIES THAT JOIN >1 PRINTED LINE: %d, costing %d printed lines, in %d volumes'
          % (tot['JOINED'], tot['lines_lost'], len(rows)))
    for v, j, l, m, e in sorted(rows, key=lambda z: -z[2])[:15]:
        print('   %-10s joined %5d  lines lost %5d  (matched %d of %d)' % (v, j, l, m, e))
