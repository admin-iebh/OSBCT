# -*- coding: utf-8 -*-
"""Prove the redistribution lossless WITHOUT the arithmetic that built it.

`redistribute.py` places a span by computing start(Ni) and subtracting.  Checking
that with the same subtraction proves nothing.  What is checked here is SEMANTIC
and uses only string slicing on the two corpora:

  BOLD       the substring the span selects in the NEW paragraph must be
             BYTE-IDENTICAL to the substring the corresponding span selected in
             the OLD paragraph.  Spans are paired in reading order — old spans
             ascend within the shipped paragraph, new spans ascend by (ordinal,
             offset) across its run, and the refinement is monotonic, so the
             i-th of one is the i-th of the other.  Nothing here recomputes an
             offset.

  APPARATUS  a note selects no substring; it names a MARKER.  So the assertions
             are (1) the note set is preserved exactly, per shipped paragraph —
             same count, same (n, text, variants, xrefs); (2) every note stays
             inside its own shipped paragraph's run, i.e. the refinement is not
             crossed; (3) the marker it names is actually SET in the paragraph
             it now hangs under, which is the invariant the shipped file held at
             the coarse grain and is the only thing the reader can resolve.

Usage:  python3 _xc/reseg/verify_redistribution.py [CORRUPT]
        CORRUPT in {none, shift1, first, appfirst} — the negative control.
"""
import json, os, re, sys, collections
import importlib.util as _ilu

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
VOL, OUT = '20KhuA01', os.path.join(ROOT, '_xc', 'reseg')
sys.path.insert(0, ROOT + '/pipeline')

# !!! READ THE MODE BEFORE LOADING `rebuild_apparatus`, which is a __main__-style
# script and has to be handed a clean `sys.argv`.  Setting it first swallowed the
# CORRUPT argument, so all three negative controls ran the HONEST input and the
# check "passed" on corruption it had never actually been given.  Caught by the
# negative control itself, which is what a negative control is for.
MODE = sys.argv[1] if len(sys.argv) > 1 else 'none'
assert MODE in ('none', 'shift1', 'first', 'appfirst'), 'unknown mode ' + MODE

_s = _ilu.spec_from_file_location('ra', ROOT + '/pipeline/rebuild_apparatus.py')
ra = _ilu.module_from_spec(_s); sys.argv = ['verify']; _s.loader.exec_module(ra)

ship = json.load(open(f'{ROOT}/site/{VOL}.json', encoding='utf-8'))['paragraphs']
new  = json.load(open(f'{OUT}/{VOL}.json', encoding='utf-8'))['paragraphs']
rm   = {int(k): v for k, v in json.load(open(f'{OUT}/ord_remap_{VOL}.json', encoding='utf-8')).items()}
oldb = json.load(open(f'{ROOT}/site/reader/bold/{VOL}.bold.json', encoding='utf-8'))
olda = json.load(open(f'{ROOT}/site/reader/apparatus/{VOL}.appk.json', encoding='utf-8'))
newb = json.load(open(f'{OUT}/bold/{VOL}.bold.json', encoding='utf-8'))
newa = json.load(open(f'{OUT}/apparatus/{VOL}.appk.json', encoding='utf-8'))

RUN = {}
for i in sorted(rm):
    RUN[i] = list(range(rm[i], rm[i + 1] if (i + 1) in rm else len(new)))
OWNER = {j: i for i in RUN for j in RUN[i]}

# ---------- the negative control -----------------------------------------
if MODE == 'shift1':
    newb = {k: [[a + 1, b + 1] for a, b in v] for k, v in newb.items()}
    print('!! CORRUPTED: every bold offset shifted by +1')
elif MODE == 'first':
    z = collections.defaultdict(list)
    for k, v in newb.items(): z[str(RUN[OWNER[int(k)]][0])] += v
    newb = dict(z)
    print('!! CORRUPTED: every bold span moved to the first paragraph of its run')
elif MODE == 'appfirst':
    z = collections.defaultdict(list)
    for k, v in newa.items(): z[str(RUN[OWNER[int(k)]][0])] += v
    newa = dict(z)
    print('!! CORRUPTED: every apparatus note moved to the first paragraph of its run')

fail = 0
# ================= BOLD: substring equality ==============================
checked = passed = 0; misses = []
for k in sorted(oldb, key=int):
    i = int(k); ot = ship[i]['text'] or ''
    want = [ot[a:b] for a, b in oldb[k]]
    got = []
    for j in RUN[i]:
        nt = new[j]['text'] or ''
        for a, b in sorted(newb.get(str(j), [])):
            got.append(nt[a:b] if 0 <= a < b <= len(nt) else '<OUT-OF-BOUNDS>')
    if len(want) != len(got):
        misses.append((k, f'count {len(want)} -> {len(got)}')); fail += 1
        checked += len(want); continue
    for x, (w, g) in enumerate(zip(want, got)):
        checked += 1
        if w == g: passed += 1
        else:
            fail += 1
            if len(misses) < 8: misses.append((k, x, repr(w), repr(g)))
orph = [k for k in newb if int(k) not in OWNER]
print(f'BOLD  substring equality: checked {checked}  passed {passed}  '
      f'FAILED {checked - passed}   orphan keys {len(orph)}')
for m in misses[:8]: print('   MISMATCH', m)

# ================= APPARATUS =============================================
sig = lambda a: (a.get('n'), a.get('text'),
                 json.dumps(a.get('variants'), sort_keys=True, ensure_ascii=False),
                 json.dumps(a.get('xrefs'), sort_keys=True, ensure_ascii=False))
a_par = a_ok = 0; a_bad = []
for k in sorted(olda, key=int):
    i = int(k); a_par += 1
    want = collections.Counter(sig(a) for a in olda[k])
    got = collections.Counter()
    for j in RUN[i]:
        for a in newa.get(str(j), []): got[sig(a)] += 1
    if want == got: a_ok += 1
    else: a_bad.append((k, sum(want.values()), sum(got.values()))); fail += 1
cross = [k for k in newa if int(k) not in OWNER]
print(f'APP   note set preserved per shipped paragraph: {a_ok} of {a_par} '
      f'  FAILED {len(a_bad)}   notes outside any run {len(cross)}')
for m in a_bad[:8]: print('   MISMATCH ord', m)

def marks(t): return {g for m in ra.MARK.finditer(t or '') for g in m.groups() if g}
m_tot = m_ok = 0
for k, arr in newa.items():
    for a in arr:
        m_tot += 1
        if str(a['n']) in marks(new[int(k)]['text']): m_ok += 1
b_tot = b_ok = 0
for k, arr in olda.items():
    for a in arr:
        b_tot += 1
        if str(a['n']) in marks(ship[int(k)]['text']): b_ok += 1
print(f'APP   marker set in the paragraph it hangs under: NEW {m_ok}/{m_tot}'
      f'   (shipped baseline, same test at the coarse grain: {b_ok}/{b_tot})')
if m_ok != m_tot: fail += 1

# a note count is not allowed to change in total either
print(f'APP   totals: shipped {sum(len(v) for v in olda.values())} '
      f'-> new {sum(len(v) for v in newa.values())}')
print('\nRESULT:', 'PASS' if fail == 0 else f'FAIL ({fail} failing assertions)')
sys.exit(0 if fail == 0 else 1)
