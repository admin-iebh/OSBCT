# -*- coding: utf-8 -*-
"""BLOCKER 3 -- uddana/, hide/, sections/ (and incipit/, booktitle/, ord/).

WHAT EACH IS KEYED TO, read off reader2.html rather than assumed:

  sections/   drawn by `secmap(i)`, emitted BEFORE `block(i)`  (reader2:1735,
              1845)  -> the ordinal the printed heading HEADS
              => FIRST of the run
  incipit/    `incHTML(i)` inside `canonFront(i)`, also before the block
              => FIRST of the run
  booktitle/  `titleHTML(i)` inside `canonFront(i)`, also before the block
              => FIRST of the run
  uddana/     `udd(i)` emitted AFTER `block(i)`  (reader2:1833, 1845)
              -> "the paragraph it FOLLOWS"
              => LAST of the run
  hide/       `if(HIDE[String(i)]) return ''` -- a SET of suppressed ordinals,
              not a pointer  => the WHOLE run
  ord/        {paragraph number -> ordinal}, panel.js:1620  => FIRST of the run
              (the numbered opener keeps `n` under re-segmentation)

THE PROOF IS PRINTED ORDER, NOT ARITHMETIC.  Every anchored item is located in
the PRINTED LINE STREAM (pline.py) and required to sit, on the page, between
the paragraph before it and the paragraph after it.  That evidence is the PDF;
it does not know the remap exists.

Run:  python3 _xc/reseg/b3/b3_sidemaps.py
      python3 _xc/reseg/b3/b3_sidemaps.py --control
"""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import pline, locate

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
VOL = '20KhuA01'
CTL = '--control' in sys.argv


def J(p):
    return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))


ship = J('site/%s.json' % VOL)['paragraphs']
reseg = J('_xc/reseg/%s.json' % VOL)['paragraphs']
remap = J('_xc/reseg/ord_remap_%s.json' % VOL)
anch = json.load(open(os.path.join(HERE, 'anchors_%s.json' % VOL), encoding='utf-8'))
PG = locate.Page(pline.stream(VOL))
NA = anch['reseg']


def run(o):
    a = remap[str(o)]
    b = remap[str(o + 1)] if str(o + 1) in remap else len(reseg)
    return list(range(a, b))


RUNS = {o: run(o) for o in range(len(ship))}
SPLIT = {o: len(r) > 1 for o, r in RUNS.items()}


# ------------------------------------------------------------------ remap ---
def remap_first(m):
    return {str(RUNS[int(k)][0]): v for k, v in m.items()}


def remap_last(m):
    return {str(RUNS[int(k)][-1]): v for k, v in m.items()}


def remap_set(m):
    out = {}
    for k, v in m.items():
        for i in RUNS[int(k)]:
            out[str(i)] = v
    return out


# ------------------------------------------------------- printed-order check -
def block_text(b):
    """every printed line an uddana block claims, in order"""
    ls = list(b.get('lines') or [])
    if b.get('label'):
        ls = [b['label']] + ls
    if b.get('head'):
        ls = [b['head']] + ls
    return ls


def locate_lines(lines, frm=0):
    """(letter_start, letter_end) of these printed lines, searched IN ORDER
    from letter offset `frm`.  Everything here is in LETTER space -- mixing it
    with line indices is exactly the bug that made the first run of this file
    report 102 of 109 section headings misplaced."""
    lo = hi = None
    cur = frm
    for t in lines:
        sp = PG.span(t, cur)
        if sp is None:
            return None
        if lo is None:
            lo = sp[2]
        hi = sp[3]
        cur = sp[3]
    return None if lo is None else (lo, hi)


def prev_end(i):
    """letter offset at which the nearest located paragraph before i ends"""
    for j in range(i - 1, -1, -1):
        if NA[j]:
            return NA[j][3]
    return 0


def next_start(i):
    for j in range(i + 1, len(NA)):
        if NA[j]:
            return NA[j][2]
    return len(PG.text)


def check_after(newkey, lines, label):
    """material the page prints AFTER this paragraph and BEFORE the next one --
    which is what `keyed by the paragraph it follows` means on the page."""
    if not lines:
        return 'nolines'
    a = NA[newkey][3] if NA[newkey] else 0
    b = next_start(newkey)
    loc = locate_lines(lines, a)
    if loc is None:
        # 9 of 33 blocks are not recovered from print at all -- their line is
        # INSIDE the anchor paragraph, because the corpus holds it too.  That
        # is a different fact from 'not on the page', so it is named.
        inside = locate_lines(lines, NA[newkey][2] if NA[newkey] else 0)
        if inside and NA[newkey] and inside[1] <= NA[newkey][3]:
            return 'inside-anchor-para(corpus holds it too)'
        return 'unlocatable-after-anchor'
    return 'ok' if loc[1] <= b else 'past-next-para(%d..%d vs %d..%d)' % (
        loc[0], loc[1], a, b)


def check_before(newkey, lines, label):
    """material the page prints BEFORE this paragraph and AFTER the previous."""
    if not lines:
        return 'nolines'
    a = prev_end(newkey)
    b = NA[newkey][2] if NA[newkey] else len(PG.text)
    loc = locate_lines(lines, a)
    if loc is None:
        return 'unlocatable-after-prev'
    return 'ok' if loc[1] <= b else 'past-anchor(%d..%d vs %d..%d)' % (
        loc[0], loc[1], a, b)


def verify(mapping, kind, itemlines, label, shift=0):
    """kind 'after' | 'before'; `shift` is the negative control."""
    tally = collections.Counter()
    bad = []
    for k, v in mapping.items():
        nk = int(k) + shift
        if not (0 <= nk < len(reseg)):
            tally['out-of-range'] += 1
            continue
        for lines in itemlines(v):
            r = (check_after if kind == 'after' else check_before)(nk, lines, label)
            tally[r.split('(')[0]] += 1
            if not r.startswith('ok') and len(bad) < 8:
                bad.append((k, r, (lines or [''])[0][:52]))
    print('   %-34s %s' % (label, dict(tally)))
    for b in bad:
        print('        %s' % (b,))
    return tally


def udd_lines(v):
    return [block_text(b) for b in v]


def sec_lines(v):
    return [[ln for ln in str(h['l']).split('\n') if ln.strip()] for h in v]


def one_line(v):
    return [[v] if isinstance(v, str) else list(v)]


# =============================================================== uddana =====
print('=== uddana/  (22 keys, all 22 split, max run 31) ===')
udd = J('site/reader/uddana/%s.json' % VOL)
print('   split runs among its keys: %d of %d   longest run %d'
      % (sum(1 for k in udd if SPLIT[int(k)]), len(udd),
         max(len(RUNS[int(k)]) for k in udd)))
udd_last = remap_last(udd)
udd_first = remap_first(udd)
assert len(udd_last) == len(udd) and len(udd_first) == len(udd)
print('  SEMANTIC CHECK (printed order) -- LAST of run, the design:')
t_ok = verify(udd_last, 'after', udd_lines, 'uddana @ last-of-run')
if CTL:
    print('  NEGATIVE CONTROLS (each MUST fire):')
    t_first = verify(udd_first, 'after', udd_lines, 'CONTROL first-of-run')
    t_sh = verify(udd_last, 'after', udd_lines, 'CONTROL anchor shifted +1', shift=1)
    t_sh2 = verify(udd_last, 'after', udd_lines, 'CONTROL anchor shifted -1', shift=-1)
    corrupt = {k: [{'label': None, 'lines': ['Zzzz not printed anywhere'], 'app': []}]
               for k in list(udd_last)[:5]}
    t_c = verify(corrupt, 'after', udd_lines, 'CONTROL corrupted line text')

# =============================================================== hide =======
print()
print('=== hide/  (a SET, not a pointer) ===')
hide = J('site/reader/hide/%s.json' % VOL)
hide_new = remap_set(hide)
hide_first = remap_first(hide)
lets = locate.letters
old_hidden = lets(' '.join(ship[int(k)].get('text') or '' for k in sorted(hide, key=int)))
new_hidden = lets(' '.join(reseg[int(k)].get('text') or ''
                           for k in sorted(hide_new, key=int)))
print('   old keys %d -> new keys %d (runs %s)'
      % (len(hide), len(hide_new), [len(RUNS[int(k)]) for k in sorted(hide, key=int)]))
print('   SEMANTIC CHECK: hidden LETTERS identical  %s  (%d vs %d)'
      % (old_hidden == new_hidden, len(old_hidden), len(new_hidden)))
assert old_hidden == new_hidden
if CTL:
    nf = lets(' '.join(reseg[int(k)].get('text') or '' for k in sorted(hide_first, key=int)))
    print('   CONTROL first-of-run only : identical %s (%d letters, %d lost) -> fired %s'
          % (nf == old_hidden, len(nf), len(old_hidden) - len(nf), nf != old_hidden))
    if nf == old_hidden:
        print('        (INERT HERE, and said so: all 3 shipped hide/ keys sit on '
              'UNSPLIT paragraphs, so pointer and set agree.  The set semantics '
              'are demonstrated on a split ordinal instead:)')
        _o = next(o for o in range(len(ship)) if len(RUNS[o]) > 3)
        _p = lets(ship[_o].get('text'))
        _set = lets(' '.join(reseg[i].get('text') or '' for i in RUNS[_o]))
        _ptr = lets(reseg[RUNS[_o][0]].get('text'))
        print('        old ord %d, run of %d: shipped paragraph %d letters | set %d '
              '(match %s) | pointer %d (match %s, %d letters would stay on the page)'
              % (_o, len(RUNS[_o]), len(_p), len(_set), _set == _p, len(_ptr),
                 _ptr == _p, len(_p) - len(_ptr)))
    drop = dict(hide_new)
    drop.pop(sorted(drop, key=int)[1], None)
    nd = lets(' '.join(reseg[int(k)].get('text') or '' for k in sorted(drop, key=int)))
    print('   CONTROL one run member dropped: identical %s -> fired %s'
          % (nd == old_hidden, nd != old_hidden))
    extra = dict(hide_new)
    extra[str(next(i for i in range(len(reseg)) if str(i) not in hide_new))] = 1
    ne = lets(' '.join(reseg[int(k)].get('text') or '' for k in sorted(extra, key=int)))
    print('   CONTROL one extra ordinal hidden: identical %s -> fired %s'
          % (ne == old_hidden, ne != old_hidden))

# =============================================================== sections ===
print()
print('=== sections/  (98 keys, 88 split -- first-of-run was never verified) ===')
sec = J('site/reader/sections/%s.json' % VOL)
print('   split runs among its keys: %d of %d' % (sum(1 for k in sec if SPLIT[int(k)]), len(sec)))
sec_first = remap_first(sec)
sec_last = remap_last(sec)

# ANCHOR BY PRINTED POSITION, NOT BY THE OLD ORDINAL.  first-of-run is right
# in 97 of 109 headings and WRONG in 12, and the 12 are not noise: the printed
# heading sits above prose that the OLD corpus had swallowed into the PREVIOUS
# lump, so the run it belongs to starts one paragraph earlier than the old key
# says.  The shipped page gets this right only because `verse/`'s `before`
# blocks lift that prose out of the previous paragraph; dissolve the
# substitution and first-of-run puts the heading below the text it heads.
# Measured by the equivalence check in b2 step 5: exactly this, at ord548.
import bisect as _bisect
STARTS = [a[2] for a in NA]


def _following(off):
    j = _bisect.bisect_left(STARTS, off)
    return j if j < len(NA) else len(NA) - 1


def sections_by_print(secmap):
    out = {}
    cur = 0
    moved = 0
    for k in sorted(secmap, key=int):
        for h in secmap[k]:
            lines = [x for x in str(h['l']).split('\n') if x.strip()]
            loc = locate_lines(lines, cur)
            if loc is None:
                loc = locate_lines(lines, 0)
            if loc is None:
                tgt = RUNS[int(k)][0]
            else:
                cur = loc[1]
                tgt = _following(loc[1])
            if tgt != RUNS[int(k)][0]:
                moved += 1
            out.setdefault(str(tgt), []).append(h)
    print('   headings whose printed position puts them on a DIFFERENT new '
          'ordinal from first-of-run: %d' % moved)
    return out


sec_print = sections_by_print(sec)
print('  SEMANTIC CHECK (printed order) -- FIRST of run, the design:')
s_ok = verify(sec_first, 'before', sec_lines, 'sections @ first-of-run')
verify(sec_print, 'before', sec_lines, 'sections @ printed position')
if CTL:
    print('  NEGATIVE CONTROLS (each MUST fire):')
    verify(sec_last, 'before', sec_lines, 'CONTROL last-of-run')
    verify(sec_first, 'before', sec_lines, 'CONTROL anchor shifted +1', shift=1)
    verify(sec_first, 'before', sec_lines, 'CONTROL anchor shifted -1', shift=-1)

# ================================================ incipit / booktitle / ord =
print()
print('=== incipit/ , booktitle/ , ord/ -- also per-paragraph, also unlisted ===')
inc = J('site/reader/incipit/%s.json' % VOL)
btl = J('site/reader/booktitle/%s.json' % VOL)
ordm = J('site/reader/ord/%s.json' % VOL)
inc_new, btl_new = remap_first(inc), remap_first(btl)
print('   incipit %d -> %d   booktitle %d -> %d' % (len(inc), len(inc_new), len(btl), len(btl_new)))
verify(inc_new, 'before', one_line, 'incipit @ first-of-run')
verify(btl_new, 'before', one_line, 'booktitle @ first-of-run')
ord_new = {k: RUNS[v][0] for k, v in ordm.items()}
bad_n = [(k, v) for k, v in ord_new.items() if reseg[v].get('n') != int(k)]
print('   ord/ {n->ordinal} %d keys; new ordinal whose paragraph does NOT carry '
      'that n: %d %s' % (len(ord_new), len(bad_n), bad_n[:5]))
if CTL:
    bad_shift = [(k, v + 1) for k, v in ord_new.items()]
    n_bad = sum(1 for k, v in bad_shift if v >= len(reseg) or reseg[v].get('n') != int(k))
    print('   CONTROL ord/ shifted +1: mismatches %d of %d -> fired %s'
          % (n_bad, len(ord_new), n_bad > 0))

# =============================================================== write ======
if not CTL:
    out = {'uddana': udd_last, 'hide': hide_new, 'sections': sec_print,
           'incipit': inc_new, 'booktitle': btl_new,
           'ord': {k: v for k, v in ord_new.items()}}
    for n, d in out.items():
        json.dump(d, open(os.path.join(HERE, '%s_%s.json' % (n, VOL)), 'w',
                          encoding='utf-8'), ensure_ascii=False)
    print()
    print('wrote', ', '.join('%s_%s.json' % (n, VOL) for n in out))
    # losslessness: every block survives, byte for byte, including nested `app`
    a = json.dumps([udd[k] for k in sorted(udd, key=int)], ensure_ascii=False, sort_keys=True)
    b = json.dumps([udd_last[k] for k in sorted(udd_last, key=int)], ensure_ascii=False, sort_keys=True)
    print('LOSSLESS: uddana blocks (incl. nested app arrays) byte-identical after remap:', a == b)
    a = json.dumps([h for k in sorted(sec, key=int) for h in sec[k]], ensure_ascii=False, sort_keys=True)
    b = json.dumps([h for k in sorted(sec_print, key=int) for h in sec_print[k]], ensure_ascii=False, sort_keys=True)
    print('LOSSLESS: sections entries byte-identical after remap:', a == b)
