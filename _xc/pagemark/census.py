# -*- coding: utf-8 -*-
"""Where the reader DRAWS a printed-page marker, against where the page actually
turns.  MEASURE ONLY -- nothing is written to site/, no baseline is recorded.

Reader-reported with a screenshot (`21KhuA02`, Dhammapada-aṭṭhakathā I): printed
page 5 opens MID-PARAGRAPH at `pūretuṁ pabbajissāmi tātāti`, and the reader
draws its `page 5` rule at the head of the NEXT paragraph -- roughly half a page
late.  This measures that over all 118 volumes.

WHY IT CAN DRIFT AT ALL.  `block()` in `reader2.html` emits the rule per
PARAGRAPH:

    if(pr.printed!=null && LASTPG[vol]!==pr.printed){ rule=pageRule(vol,kind,pr); ... }

and a paragraph carries ONE `printed` -- the page it STARTS on.  So a marker can
only ever be placed at a paragraph boundary, and wherever a paragraph spans a
page break the marker waits for the next boundary.  That is the mechanism to be
VERIFIED, not assumed, and it is verified here by locating the page's first
printed line in the corpus and comparing that position with the position the
reader puts the rule at.

This matters beyond display: the printed page number is the CITABLE reference
for this edition, and the footnote apparatus is anchored by (printed page, marker).

THE EVIDENCE is `_xc/reseg/pline.py` -- extract.py's own raw_pages + split_page
over the PDF with the glyph-errata register applied, so running heads and the
footnote apparatus are already gone.  The corpus side is the paragraph array in
ordinal order, which is what the spine draws and what carries `printed`.

  python3 _xc/pagemark/census.py <VOL> [...]
  python3 _xc/pagemark/census.py --all --out DIR --budget 32     # resumable
  python3 _xc/pagemark/census.py <VOL> --controls
"""
import sys, os, json, bisect, collections, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
import check_page_fidelity as CPF                      # noqa: E402
import pline                                           # noqa: E402

letters = CPF.letters
Index = CPF.Index
BACK = 40000

RESEG = ('20KhuA01', '21KhuA02', '23KhuA04', '24KhuA05')


def jload(p, d=None):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception:
        return d


def run(vol, control=None):
    S = os.path.join(ROOT, 'site')
    c = jload('%s/%s.json' % (S, vol))
    if not c:
        return None
    paras = c.get('paragraphs', [])
    if not paras:
        return None
    hide = jload('%s/reader/hide/%s.json' % (S, vol), {}) or {}

    # --- CONTROLS act on the CORPUS side only; the printed page is never touched.
    if control == 'shiftprinted':          # every paragraph claims the next one's page
        pr = [p.get('printed') for p in paras]
        pr = pr[1:] + pr[:1]
        paras = [dict(p, printed=x) for p, x in zip(paras, pr)]
    elif control == 'roundprinted':        # every paragraph claims the page 2 later
        paras = [dict(p, printed=(None if p.get('printed') is None
                                  else p['printed'] + 2)) for p in paras]
    elif control == 'nohide':              # ignore the hide map
        hide = {}
    elif control == 'lumped':              # every 4 paragraphs claim the first's page
        out, last = [], None
        for i, p in enumerate(paras):
            if i % 4 == 0:
                last = p.get('printed')
            out.append(dict(p, printed=last))
        paras = out

    buf, starts = [], []
    pos = 0
    for p in paras:
        s = letters(p.get('text', '') or '')
        starts.append(pos)
        buf.append(s)
        pos += len(s)
    C = ''.join(buf)
    ends = [starts[i] + len(buf[i]) for i in range(len(paras))]
    if not C:
        return None
    IX = Index(C)

    st = pline.stream(vol)
    pgs = [p['pdf_page'] for p in paras if p.get('pdf_page')]
    LO, HI = min(pgs), max(pgs)
    lines = [x for x in st if LO <= x[0] <= HI and letters(x[3])]
    if not lines:
        return None

    # --- locate every printed line, monotonically, exactly as check_page_fidelity does
    loc = []
    cur = 0
    for l in lines:
        t = letters(l[3])
        j = IX.find(t, cur)
        if j < 0:
            j = IX.find(t, max(0, cur - BACK))
        if j < 0:
            j = IX.findany(t)
        if j >= 0:
            cur = j + len(t)
        loc.append(j)

    # --- printed-page number of each pdf page, from the corpus's own paragraphs
    pr_of = {}
    for p in paras:
        if p.get('pdf_page') and p.get('printed') is not None:
            pr_of.setdefault(p['pdf_page'], p['printed'])
    # --- where the reader draws the rule: first NON-HIDDEN paragraph whose
    #     `printed` differs from the one before it, in ordinal order
    marker = {}
    last = object()
    for i, p in enumerate(paras):
        if hide.get(str(i)):
            continue
        v = p.get('printed')
        if v is None:
            continue
        if v != last:
            marker.setdefault(v, starts[i])
            last = v
    # --- where each printed page actually begins: the located position of the
    #     first line of the first pdf page carrying that printed number
    truepos, trueline = {}, {}
    for k, l in enumerate(lines):
        pg = pr_of.get(l[0])
        if pg is None or pg in truepos:
            continue
        if loc[k] < 0:
            continue
        truepos[pg] = loc[k]
        trueline[pg] = k

    st2 = collections.Counter()
    rows = []
    locpos = sorted(x for x in loc if x >= 0)
    for pg in sorted(set(pr_of.values())):
        if pg not in truepos:
            st2['page_unlocated'] += 1
            continue
        tp = truepos[pg]
        if pg not in marker:
            st2['marker_missing'] += 1
            rows.append([pg, None, tp, None, None, 'MISSING'])
            continue
        mp = marker[pg]
        d = mp - tp
        # is the true page break INSIDE a paragraph, or between two?
        k = max(0, bisect.bisect_right(starts, tp) - 1)
        inside = (starts[k] < tp < ends[k])
        st2['pages'] += 1
        st2['break_inside_paragraph' if inside else 'break_at_boundary'] += 1
        # drift in printed LINES: how many located printed lines lie between
        # where the page turns and where the rule is drawn
        if d > 0:
            nl = sum(1 for x in locpos if tp <= x < mp)
            st2['LATE'] += 1
            st2['late_chars'] += d
            st2['late_lines'] += nl
            rows.append([pg, mp, tp, d, nl, 'LATE'])
        elif d < 0:
            nl = sum(1 for x in locpos if mp <= x < tp)
            st2['EARLY'] += 1
            st2['early_chars'] += -d
            rows.append([pg, mp, tp, d, nl, 'EARLY'])
        else:
            st2['EXACT'] += 1
            rows.append([pg, mp, tp, 0, 0, 'EXACT'])
    st2['lines_total'] = len(lines)
    st2['lines_unlocated'] = sum(1 for x in loc if x < 0)
    st2['paras'] = len(paras)
    st2['reseg'] = 1 if vol in RESEG else 0
    return dict(st2), rows


def one(vol, out=None, control=None):
    r = run(vol, control)
    if r is None:
        print('SKIP', vol)
        return None
    s, rows = r
    if out:
        json.dump({'vol': vol, 'stat': s, 'rows': rows},
                  open(os.path.join(out, vol + '.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False)
    n = s.get('pages', 0) or 1
    print('%-11s pages=%5d EXACT=%5d (%5.1f%%) LATE=%5d EARLY=%4d MISSING=%4d '
          'inside=%5d boundary=%5d  medianlate=%s'
          % (vol, s.get('pages', 0), s.get('EXACT', 0), 100.0 * s.get('EXACT', 0) / n,
             s.get('LATE', 0), s.get('EARLY', 0), s.get('marker_missing', 0),
             s.get('break_inside_paragraph', 0), s.get('break_at_boundary', 0),
             (sorted(r[4] for r in rows if r[5] == 'LATE')[s.get('LATE', 0) // 2]
              if s.get('LATE', 0) else 0)))
    return s


CONTROLS = ['shiftprinted', 'roundprinted', 'lumped', 'nohide']


def main(a):
    out = None
    budget = 1e9
    if '--out' in a:
        i = a.index('--out'); out = a[i + 1]; del a[i:i + 2]
        if not os.path.isdir(out):
            os.makedirs(out)
    if '--budget' in a:
        i = a.index('--budget'); budget = float(a[i + 1]); del a[i:i + 2]
    shard = None
    if '--shard' in a:
        i = a.index('--shard'); shard = tuple(int(x) for x in a[i + 1].split(':')); del a[i:i + 2]
    if '--controls' in a:
        a.remove('--controls')
        for v in [x for x in a if not x.startswith('--')]:
            base = run(v)
            if base is None:
                continue
            bs, brows = base
            bmap = dict((r[0], (r[3], r[5])) for r in brows)
            print('%s  honest: %d pages, EXACT %d, LATE %d, MISSING %d'
                  % (v, bs.get('pages', 0), bs.get('EXACT', 0), bs.get('LATE', 0),
                     bs.get('marker_missing', 0)))
            for cn in CONTROLS:
                r = run(v, cn)
                if r is None:
                    continue
                cs, crows = r
                moved = sum(1 for x in crows
                            if bmap.get(x[0], (None, None)) != (x[3], x[5]))
                print('   %-14s pages whose verdict moved: %5d   (EXACT %d -> %d)'
                      % (cn, moved, bs.get('EXACT', 0), cs.get('EXACT', 0)))
        return
    vols = CPF.all_vols() if '--all' in a else [x for x in a if not x.startswith('--')]
    if shard:
        vols = [v for i, v in enumerate(vols) if i % shard[1] == shard[0]]
    t0 = time.time()
    left = 0
    for v in vols:
        if out and os.path.exists(os.path.join(out, v + '.json')):
            continue
        if time.time() - t0 > budget:
            left += 1
            continue
        try:
            one(v, out)
        except Exception as e:
            print('ERR', v, type(e).__name__, e)
    if left:
        print('...budget reached, %d volumes left' % left)


if __name__ == '__main__':
    main(sys.argv[1:])
