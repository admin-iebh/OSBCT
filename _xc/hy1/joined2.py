# -*- coding: utf-8 -*-
"""Printed line breaks lost inside a DISPLAY block.

joined.py asked the wrong question two ways and is superseded.

 (1) It matched a corpus entry against a whole printed block by exact equality.
     The block carries the paragraph number ('107.') the entry omits, so 1,812 of
     1,884 entries failed to match and the 4% that did were not a sample of
     anything.
 (2) More fundamentally, a PROSE paragraph's line breaks are not structural --
     the page wraps it and the reader reflows it, and joining them is correct.
     A break is only lost where the page sets the lines APART, which is exactly
     what the block map's `display` verdict identifies.

So this iterates DISPLAY BLOCKS, not corpus entries, and asks of each: does the
corpus draw this block's N printed lines as N drawn lines, or fewer?
"""
import json, os, sys, re, collections

NRM = re.compile(r'[^A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]')
LEADNUM = re.compile(r'^\s*\d+\s*\.?\s*')
n = lambda s: NRM.sub('', s or '')
strip = lambda s: n(LEADNUM.sub('', s or ''))
B = '_xc/hy1/blocks2'
# A DECORATIVE RULE IS NOT A PRINTED LINE OF TEXT.  39Abhi11 sets a parenthetical
# and an ornamental rule ('____') under it; the block map groups the two, and
# counting the rule made 120 lines look lost on a volume where nothing is.  The
# repair correctly does not move them; the MEASURE was wrong.
RULE = re.compile(r'^[\s_\-–—=.]*$')
sys.path.insert(0, os.path.abspath('_xc/hy1'))
import adjudicate as A
A.B = B


def drawn_lines(vol):
    out = set()
    try:
        V = json.load(open('site/reader/verse/%s.json' % vol, encoding='utf-8'))
    except Exception:
        return out
    # An entry in before/after/tail/groups is EITHER a string (one prose run)
    # OR a dict {"gatha": [line, line, ...]} holding the drawn verse lines.  The
    # first version of this walker handled the dict only under `groups` and took
    # `after` elements to be strings, so every verse line the builder puts inside
    # `after` was invisible: 20KhuA01 came out 184 blocks "not in the verse map"
    # when its stanzas are plainly there.  Walk the shape, do not assume it.
    def walk(x):
        if isinstance(x, str):
            out.add(strip(x))
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    for e in V.values():
        if isinstance(e, dict):
            for k in ('before', 'after', 'tail', 'groups'):
                walk(e.get(k))
    return out


def scan(vol):
    try:
        BL = json.load(open('%s/%s.json' % (B, vol), encoding='utf-8'))
    except Exception:
        return None
    D = drawn_lines(vol)
    if not D:
        return None
    margin = A.vol_margin(vol, BL)
    st = collections.Counter()
    ex = []
    for pg, p in BL.items():
        for k, b in A.judge_page(p, margin)[2]:
            if k != 'display' or len(b) < 2:
                continue
            st['blocks'] += 1
            b = [l for l in b if not RULE.match(l[3] or '')]
            if len(b) < 2:
                st['rule_only'] += 1
                continue
            per = [strip(l[3]) for l in b]
            have = sum(1 for t in per if t and t in D)
            joined = strip(' '.join(l[3] for l in b))
            if have == len(per):
                st['kept'] += 1
            elif joined in D:
                st['JOINED'] += 1
                st['lines_lost'] += len(b) - 1
                if len(ex) < 3:
                    ex.append((pg, [l[3][:56] for l in b]))
            elif have == 0:
                st['absent'] += 1
            else:
                st['partial'] += 1
    return st, ex


if __name__ == '__main__':
    vols = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(B))
    tot, rows = collections.Counter(), []
    for v in vols:
        r = scan(v)
        if not r:
            continue
        st, ex = r
        tot.update(st)
        if st['JOINED']:
            rows.append((v, st['JOINED'], st['lines_lost'], st['blocks']))
        if len(vols) <= 3:
            for pg, blines in ex:
                print('  p%s sets %d lines, corpus draws them as one:' % (pg, len(blines)))
                for l in blines:
                    print('       | %s' % l)
    print()
    print('display blocks of >1 printed line : %d' % tot['blocks'])
    print('   drawn as separate lines (kept) : %d' % tot['kept'])
    print('   JOINED into one drawn line     : %d   costing %d printed lines'
          % (tot['JOINED'], tot['lines_lost']))
    print('   partly present                 : %d' % tot['partial'])
    print('   not in the verse map at all    : %d' % tot['absent'])
    print('   block was text + a rule only   : %d  (not a fault; see RULE)' % tot['rule_only'])
    print()
    for v, j, l, nb in sorted(rows, key=lambda z: -z[2])[:14]:
        print('   %-10s joined %5d  lines lost %5d  of %5d display blocks' % (v, j, l, nb))
