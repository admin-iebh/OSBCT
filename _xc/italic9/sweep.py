# -*- coding: utf-8 -*-
"""THE SWEEP, redone from the PRINTED PAGE over every shipped sections
k:'gatha' entry in every volume.

Independent of build_khu_volume.py.  Evidence: _xc/reseg/pline.py's printed
line stream (extract.py's raw_pages + split_page + glyph errata) and
locate.py's letter->line map.

THE RULE, as build_khu_volume.py states it: verse is a RUN of TWO OR MORE
CONSECUTIVE LINES SHARING AN INDENT ABOVE the body column; prose returns to
the body column.  "Sharing an indent" is load-bearing and the first pass of
this check got it wrong: 14SamA01 p27 sets a two-line couplet at body+14 and
the PROSE PARAGRAPH under it opens at body+5, so a rule that only asks
"above the body column?" swallows the opener into the couplet.

body column = the volume's own modal printed indent.
A lone raised line whose neighbours are at the body column is a PROSE
PARAGRAPH OPENER -- this edition opens a paragraph at body+3..+6.
"""
import json, os, sys, collections
ROOT = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
import pline, locate

SEC = os.path.join(ROOT, 'site', 'reader', 'sections')

def bodycol(st):
    return collections.Counter(it[2] for it in st).most_common(1)[0][0]

def classify(lines, bc, after=None):
    """-> list of 'V' verse / 'p' prose / 'd' display, per printed line.

    verse   a run of >= 2 consecutive lines SHARING an indent above the body
            column.
    prose   a line AT the body column, or a lone raised line at body+3..+7
            whose NEXT PRINTED LINE returns to the body column -- which is
            what a paragraph opener is in this edition (20KhuA01's "Imassa
            dāni ..." at body+4 is the worked precedent).
    display anything else raised and alone: a CENTRED heading, colophon or
            title-page line.  "(Sattamo bhāgo)" at body+26 and "Paccayuddeso."
            at body+28 are these, and calling them prose is the artefact the
            first pass of this check produced.
    """
    n = len(lines); rel = [it[2]-bc for it in lines]; kind = ['p']*n
    i = 0
    while i < n:
        if rel[i] > 2:
            j = i
            while j+1 < n and rel[j+1] == rel[i]:
                j += 1
            if j > i:
                for k in range(i, j+1):
                    kind[k] = 'V'
            else:
                nxt = rel[i+1] if i+1 < n else (after - bc if after is not None else None)
                kind[i] = 'p' if (3 <= rel[i] <= 7 and nxt is not None and nxt <= 2) else 'd'
            i = j+1
        else:
            i += 1
    return rel, kind

def blocks(kind):
    """[(kind, first, last)] runs."""
    out = []
    for k, c in enumerate(kind):
        if out and out[-1][0] == c:
            out[-1][2] = k
        else:
            out.append([c, k, k])
    return [tuple(x) for x in out]

def main(vols):
    rows = []
    for vol in vols:
        p = os.path.join(SEC, vol + '.json')
        if not os.path.exists(p):
            continue
        S = json.load(open(p, encoding='utf-8'))
        ent = [(o, i, x) for o, arr in S.items()
               for i, x in enumerate(arr) if x.get('k') == 'gatha']
        if not ent:
            continue
        try:
            st = pline.stream(vol)
        except SystemExit as e:
            print('%-12s NO PDF (%s)' % (vol, e)); continue
        P = locate.Page(st); bc = bodycol(st)
        nflag = 0
        for o, i, x in ent:
            text = str(x.get('l', ''))
            sp = P.span(text)
            if sp is None:
                print('%-12s sec%s[%d]  NOT LOCATED in printed stream' % (vol, o, i))
                continue
            l0, l1, _a, _b = sp
            lines = st[l0:l1+1]
            after = st[l1+1][2] if l1+1 < len(st) else None
            rel, kind = classify(lines, bc, after)
            bl = blocks(kind)
            npro = kind.count('p')
            if npro:
                nflag += 1
                print('%-12s sec%-4s[%d]  %3d lines  prose=%-3d verse=%-3d  blocks=%s'
                      % (vol, o, i, len(lines), npro, kind.count('V'),
                         ''.join('%s%d' % (k, e-s+1) for k, s, e in bl)))
                rows.append({'vol': vol, 'ord': o, 'idx': i, 'nlines': len(lines),
                             'prose': npro, 'verse': kind.count('V'),
                             'blocks': [[k, s, e] for k, s, e in bl],
                             'l0': l0, 'l1': l1, 'bc': bc,
                             'rel': rel, 'kind': ''.join(kind)})
        print('%-12s %d gatha entries, %d flagged' % (vol, len(ent), nflag))
    json.dump(rows, open(os.path.join(ROOT, '_xc', 'italic9', 'sweep.json'), 'w'),
              ensure_ascii=False, indent=1)
    print('\nTOTAL FLAGGED %d in %d volumes' % (len(rows), len({r['vol'] for r in rows})))

if __name__ == '__main__':
    vols = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(SEC) if f.endswith('.json'))
    main(vols)
