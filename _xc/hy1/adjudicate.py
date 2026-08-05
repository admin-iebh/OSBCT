# -*- coding: utf-8 -*-
"""Adjudicate verse-vs-prose from the BLOCK MAP, not from a display column.

The evidence every failing instrument has used is indent + shortness, and three
one-line glosses at a paragraph indent look exactly like three padas (12DiT05
p300).  The block map adds the boundary, and with the boundary a much simpler
discriminator becomes available -- the SHAPE OF A BLOCK:

    PROSE   : first line indented, continuations return to the left margin.
              The block's x values are {margin+k, margin, margin, ...}.
    DISPLAY : every line of the block sits at ONE x, right of the margin.

That is a statement about a block, not about a line, and it needs no
display_column.  A one-line block is decided by whether its x equals the x at
which THIS PAGE opens its prose paragraphs.
"""
import json, os, sys, collections

B = '_xc/hy1/blocks2'


def page_blocks(pg):
    out, cur = [], []
    for ln in pg['lines']:
        if ln[2] and cur:
            out.append(cur); cur = []
        cur.append(ln)
    if cur:
        out.append(cur)
    return out


_MARGIN = {}


def vol_margin(vol, d):
    """The left text margin is a constant of the VOLUME, not of a page.

    Computed per page it fails on any page the display dominates: 06ViT06 p28 is
    14 verse lines at x=105.8 against 4 prose lines at 62.6, so the modal x was
    the VERSE indent and every stanza was judged prose.  46KhuA27 p7 is a title
    page with no prose on it at all.  Over a whole volume, prose dominates and
    the modal x is the margin."""
    if vol not in _MARGIN:
        c = collections.Counter()
        for pg in d.values():
            for l in pg['lines']:
                c[round(l[1], 1)] += 1
        _MARGIN[vol] = c.most_common(1)[0][0]
    return _MARGIN[vol]


def judge_page(pg, margin):
    blocks = page_blocks(pg)
    # the x at which this page opens a prose paragraph: the commonest first-line
    # x among blocks that DO return to the margin
    opens = collections.Counter(round(b[0][1], 1) for b in blocks
                                if len(b) > 1 and any(round(l[1], 1) == margin for l in b[1:]))
    popen = opens.most_common(1)[0][0] if opens else None
    res = []
    for b in blocks:
        bxs = [round(l[1], 1) for l in b]
        rest = set(bxs[1:])
        if len(b) > 1 and any(x == margin for x in bxs[1:]):
            k = 'prose'                       # continuations return to the margin
        elif len(set(bxs)) == 1 and bxs[0] > margin + 2:
            k = 'display' if len(b) > 1 else ('prose' if bxs[0] == popen else 'display?')
        elif len(rest) == 1 and min(rest) > margin + 2:
            # The block sits wholly right of the margin and its first line differs.
            # WHICH WAY it differs is the whole answer, and no line-length test is
            # needed: a HANGING first line is a numbered display item (07ViT07 p488
            # sets '4.' at 84.2 and its three padas at 97.2); a first line indented
            # FURTHER RIGHT is an ordinary paragraph opening, so the block is a
            # prose block-quote (40KhuA21 p450 opens at 105.8 over 11 lines at 84.2).
            k = 'display' if bxs[0] < min(rest) else 'prose'
        else:
            k = 'other'
        res.append((k, b))
    return margin, popen, res


_VD = {}


def judge(vol, page, needle):
    if vol not in _VD:
        _VD[vol] = json.load(open('%s/%s.json' % (B, vol), encoding='utf-8'))
    d = _VD[vol]
    pg = d.get(str(page))
    if not pg:
        return None
    margin, popen, res = judge_page(pg, vol_margin(vol, d))
    for k, b in res:
        for l in b:
            if needle and needle[:26] in l[3].replace('  ', ' '):
                return k, len(b), round(b[0][1], 1), margin, popen
    return None


if __name__ == '__main__':
    KNOWN = [('06ViT06', 28, 'Saṁghañca sīlādiguṇehi', 'display'),
             ('20KhuA01', 233, 'Viññū jano vimalasīla', 'display'),
             ('12DiT05', 300, 'Mūlakaṭṭhakathāsāranti pubbe', 'prose'),
             ('46KhuA27', 7, 'Yo sabbalokātigasabbasobhā', 'display'),
             ('20KhuA01', 233, 'Evaṁ Bhagavā desanaṁ', 'prose')]
    print('CONTROL -- five cases already settled by reading the page:')
    ok = 0
    for vol, pg, needle, want in KNOWN:
        r = judge(vol, pg, needle)
        got = r[0] if r else None
        ok += (got == want)
        print('   %-9s p%-4d  want %-8s got %-9s %s   %s'
              % (vol, pg, want, got, 'OK ' if got == want else '!! ', needle[:34]))
    print('   %d / %d' % (ok, len(KNOWN)))


def run_candidates():
    items = json.load(open('_xc/hy1/review.json', encoding='utf-8'))
    pm = json.load(open('_xc/hy1/pagemap.json'))
    out, tally = [], collections.Counter()
    for c in items:
        k = '%s|%d' % (c['vol'], c['pg'])
        pdfp = pm.get(k, {}).get('pdftotext')
        printed = pm.get(k, {}).get('printed')
        r = judge(c['vol'], pdfp, c['text']) if pdfp else None
        v = r[0] if r else 'UNRESOLVED'
        tally[v] += 1
        out.append(dict(vol=c['vol'], pline=c['pg'], pdftotext=pdfp, printed=printed,
                        verdict=v, block_len=(r[1] if r else None),
                        x=(r[2] if r else None), text=c['text']))
    json.dump(out, open('_xc/hy1/verdicts.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print()
    print('42 candidates, adjudicated from the block map:')
    for k, n in tally.most_common():
        print('   %-12s %3d' % (k, n))
    print()
    for o in sorted(out, key=lambda z: (z['verdict'], z['vol'])):
        print('   %-9s p%-5s pr%-5s %-9s block=%-3s x=%-6s %s'
              % (o['vol'], o['pdftotext'], o['printed'], o['verdict'],
                 o['block_len'], o['x'], o['text'][:44]))


if __name__ == '__main__':
    run_candidates()
