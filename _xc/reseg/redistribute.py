# -*- coding: utf-8 -*-
"""PROTOTYPE ONLY.  Redistribute the two intra-paragraph side-maps of 20KhuA01
across the re-segmented paragraphs.  Writes ONLY inside _xc/reseg/.

THE GROUND FACT, re-asserted here rather than trusted: the re-segmentation is a
STRICT REFINEMENT, and the join is a SINGLE SPACE.  `reseg.py` reproduces
`extract.py`'s own loop, whose continuation line is `cur['text'] += ' ' + st`;
the extra flush turns the space that WOULD have been inserted into the boundary.
So for old paragraph P covering new paragraphs N1..Nk

    P.text == N1.text + ' ' + N2.text + ' ' + ... + ' ' + Nk.text

and the offset of Ni inside P is  start(N1)=0,  start(Ni)=start(Ni-1)+len(Ni-1)+1.
That is asserted for all 109 before anything is redistributed.

THE TWO MAPS ARE NOT THE SAME KIND OF THING.

  bold/<VOL>.bold.json   {ord: [[a,b], ...]}   HALF-OPEN CHARACTER OFFSETS into
      the paragraph's RAW `text` (the reader subtracts the leading "NN. " itself
      in `fmtBold`, so the stored numbers include it).  Pure arithmetic applies.

  apparatus/<VOL>.appk.json  {ord: [{n,text,variants,xrefs}, ...]}   NO OFFSETS.
      `n` is the printed footnote MARKER — a digit set against a word in the
      paragraph ("nhāru2") — and the reader draws the notes as a block under the
      paragraph, labelled with `n`.  The anchor is therefore a REFERENCE, not a
      position, and `rebuild_apparatus.py` resolves it as (printed page, marker)
      before SORTING the survivors by `n`, which throws the page away.
      63% of the notes (329/520) are ambiguous on the marker number alone,
      because marker numbers restart on every printed page and one shipped
      paragraph spans several.  So the page is RECOVERED here, by matching each
      stored note's (n, text) back against the printed footnote cells.
"""
import json, os, re, sys, subprocess, collections
import importlib.util as _ilu

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
VOL  = '20KhuA01'
OUT  = os.path.join(ROOT, '_xc', 'reseg')
sys.path.insert(0, ROOT + '/pipeline')

# the marker regex is `rebuild_apparatus.py`'s own, imported rather than copied
_s = _ilu.spec_from_file_location('ra', ROOT + '/pipeline/rebuild_apparatus.py')
ra = _ilu.module_from_spec(_s); sys.argv = ['redistribute']; _s.loader.exec_module(ra)

ship = json.load(open(f'{ROOT}/site/{VOL}.json', encoding='utf-8'))['paragraphs']
new  = json.load(open(f'{OUT}/{VOL}.json', encoding='utf-8'))['paragraphs']
rm   = {int(k): v for k, v in
        json.load(open(f'{OUT}/ord_remap_{VOL}.json', encoding='utf-8')).items()}
bold = json.load(open(f'{ROOT}/site/reader/bold/{VOL}.bold.json', encoding='utf-8'))
app  = json.load(open(f'{ROOT}/site/reader/apparatus/{VOL}.appk.json', encoding='utf-8'))

# ---------- the refinement, asserted -------------------------------------
RUN, START = {}, {}
for i in sorted(rm):
    s = rm[i]; e = rm[i + 1] if (i + 1) in rm else len(new)
    RUN[i] = list(range(s, e))
    off, st = 0, {}
    for j in RUN[i]:
        st[j] = off; off += len(new[j]['text'] or '') + 1
    START[i] = st
    joined = ' '.join(new[j]['text'] or '' for j in RUN[i])
    assert joined == (ship[i]['text'] or ''), f'NOT A REFINEMENT at old ord {i}'
print(f'refinement asserted: {len(rm)} shipped paragraphs == space-join of '
      f'{len(new)} new paragraphs, exact')

# ---------- 1. bold: exact arithmetic ------------------------------------
nb = collections.defaultdict(list)
b_tot = b_strad = 0
for k, spans in bold.items():
    i = int(k); st = START[i]
    for a, b in spans:
        b_tot += 1
        j = None
        for cand in RUN[i]:
            L = len(new[cand]['text'] or '')
            if st[cand] <= a < st[cand] + L: j = cand; break
        if j is None:                     # offset fell on a joining space
            b_strad += 1; continue
        if b > st[j] + len(new[j]['text'] or ''):
            b_strad += 1; continue        # span crosses a boundary
        nb[str(j)].append([a - st[j], b - st[j]])
print(f'bold: {b_tot} spans in, {sum(len(v) for v in nb.values())} out, '
      f'{b_strad} unplaceable (straddling or on a separator)')

# ---------- 2. apparatus: recover the page, then anchor ------------------
pages = subprocess.run(['pdftotext', '-layout',
                        f'{ROOT}/atthakatha-unicode/{VOL}.pdf', '-'],
                       capture_output=True, text=True).stdout.split('\f')
PAGE_OFF = ra.vr.page_offset(VOL, ship, pages)
occ = collections.defaultdict(list)      # (n, printed text) -> [corpus pdf_page]
for pi, page in enumerate(pages):
    notes, _x = ra.page_notes(page)
    for n, lst in notes.items():
        for t in lst: occ[(n, t)].append(pi - PAGE_OFF)

def marks(t): return {g for m in ra.MARK.finditer(t or '') for g in m.groups() if g}

na = collections.defaultdict(list)
why = collections.Counter(); audit = []
for k, arr in app.items():
    i = int(k); run = RUN[i]
    # the page each new paragraph COVERS: from its own pdf_page to the next one's
    cov = {}
    for x, j in enumerate(run):
        lo = new[j].get('pdf_page') or 0
        hi = (new[run[x + 1]].get('pdf_page') or lo) if x + 1 < len(run) else lo
        cov[j] = (lo, hi)
    for a in arr:
        n = a['n']
        cands = [j for j in run if str(n) in marks(new[j]['text'])]
        pg = sorted(set(occ.get((n, a['text']), [])))
        pick, tag = None, None
        if not cands:
            pick, tag = run[0], 'no-marker-in-any-new-paragraph'
        elif len(cands) == 1:
            pick, tag = cands[0], 'unique-marker'
        else:
            exact = [j for j in cands if len(pg) == 1 and (new[j].get('pdf_page') or 0) == pg[0]]
            covers = [j for j in cands if any(cov[j][0] <= p <= cov[j][1] for p in pg)]
            if len(exact) == 1: pick, tag = exact[0], 'page-exact'
            elif exact:         pick, tag = exact[0], 'page-exact-first-of-several'
            elif len(covers) == 1: pick, tag = covers[0], 'page-covering'
            elif covers:        pick, tag = covers[0], 'page-covering-first-of-several'
            else:               pick, tag = cands[0], 'AMBIGUOUS-first-candidate'
        why[tag] += 1
        na[str(pick)].append(dict(a))
        audit.append({'old': i, 'new': pick, 'n': n, 'text': a['text'],
                      'pages': pg, 'cands': cands, 'why': tag})
for o in na: na[o].sort(key=lambda x: (x['n'] if x.get('n') is not None else 0))
print(f'apparatus: {sum(len(v) for v in app.values())} notes in, '
      f'{sum(len(v) for v in na.values())} out')
for t, c in why.most_common(): print(f'   {c:5d}  {t}')

json.dump({k: nb[k] for k in sorted(nb, key=int)},
          open(f'{OUT}/bold/{VOL}.bold.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump({k: na[k] for k in sorted(na, key=int)},
          open(f'{OUT}/apparatus/{VOL}.appk.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=0)
json.dump(audit, open(f'{OUT}/audit_apparatus_{VOL}.json', 'w', encoding='utf-8'),
          ensure_ascii=False)
print('WROTE _xc/reseg/bold/, _xc/reseg/apparatus/, audit_apparatus_%s.json' % VOL)
