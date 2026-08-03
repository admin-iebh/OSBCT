#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Place a canon->commentary link from what the EDITION says, not from a number.

WHY.  User-reported 2026-08-03: reading Khuddakapāṭhapāḷi (`18Khu01`) the
per-paragraph **A** chips are dimmed, although the work plainly has a commentary
(`20KhuA01`).  `hasBand` in reader2.html draws a live chip only for a `direct`
target, and `18Khu01.links.json` held 49 direct and 56 covered into `20KhuA01`.

Those links were built when `20KhuA01` was 109 LUMPED paragraphs.  It was
re-segmented to 673 (commit `75ee5904`) and the re-key mapped every old link
onto the FIRST paragraph of the lump it used to point at, which is right only
where the lump began at the passage the link was about.

WHAT THIS READS.  Five signals, none of them the bare paragraph number, all of
them printed in the edition:

  BLOCK   both volumes head their works with the SAME printed number and
          essentially the same name -- `5. Maṅgalasutta` / `5. Maṅgalasutta-
          vaṇṇanā`.  Two independent criteria; both must agree or the block is
          skipped.  This is `relink_by_name.py`'s discriminator, taken from the
          reader's `sections/` side-map instead of the `sutta` field, because
          the `sutta` field is measurably wrong here: it labels the ten
          Kumārapañhā `Maṅgalasutta` and puts the Tirokuṭṭa/Nidhikaṇḍa boundary
          four paragraphs early, while `sections/` is anchored to the printed
          position.
  H-inc   a sub-head QUOTING the canon incipit: `Asevanā cātigāthāvaṇṇanā`.
  H-ord   a sub-head naming the gāthā by ORDINAL WORD: `Paṭhamagāthāvaṇṇanā`,
          `Catutthapañcamagāthāvaṇṇanā`.  Table reused from
          `pipeline/ordinal_words.py`.
  H-part  a sub-head naming a RUN of the block's units:
          `Purimapañcasikkhāpadavaṇṇanā` -- the edition's own statement that
          this passage comments on sikkhāpada 1-5.
  GLOSS   the edition's BOLD marks the canon words a commentary paragraph is
          glossing; `bold/<VOL>.bold.json` carries the spans.  This is the
          evidence `_xc/classc_lemma.py` uses as a confirmer; here it proposes.

!!! THE GLOSS ROUTE IS WORTHLESS WITHOUT THE CONTROL `classc_lemma.py`'s
docstring names.  Pāḷi is formulaic and a short lemma recurs: `mānasaṁ bhāvaye
aparimāṇaṁ` closes Mettasutta gāthā 7 AND gāthā 8, so gāthā 8's commentary
scores on gāthā 7 and wins.  Counting ONLY lemmas that occur in exactly one
canon paragraph of the block removes that class entirely -- it turned 8 of the
11 route disagreements from unresolved into unanimous, and turned canon 85 from
wrong to right.  Do not drop it.

!!! AND THE ORDINAL HEAD IS NOT THE CANON'S NUMBERING.  In Tirokuṭṭa the canon
prints `Idaṁ vo ñātīnaṁ hotu` inside paragraph 3 and the commentary counts it as
the first half of gāthā 4, so from there on the commentary's gāthā number runs
one ahead of the canon's.  H-ord and the printed number agree with each other
and are both wrong for six of the eleven paragraphs; the gloss is right for
five of those six and silent on the last.  Where they split, the gloss wins.
That is the whole reason this file exists rather than another number walk.

SCOPE.  One source volume and one target volume per run, and it says so on the
command line.  `build_links_bynum.py` records, with numbers, that a corpus-wide
rebuild lost on both axes at once.

Usage:
  python3 pipeline/link_by_gloss.py 18Khu01 20KhuA01            # dry, to _xc/
  python3 pipeline/link_by_gloss.py 18Khu01 20KhuA01 --apply    # into site/
"""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import ordinal_words

SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')
OUT = os.path.join(ROOT, '_xc', 'linksk_gloss')

_p, _s, _b = {}, {}, {}
def paras(v):
    if v not in _p:
        _p[v] = json.load(open(os.path.join(SITE, v + '.json'),
                               encoding='utf-8'))['paragraphs']
    return _p[v]
def secs(v):
    if v not in _s:
        _s[v] = json.load(open(os.path.join(SITE, 'reader/sections', v + '.json'),
                               encoding='utf-8'))
    return _s[v]
def bold(v):
    if v not in _b:
        q = os.path.join(SITE, 'reader/bold', v + '.bold.json')
        _b[v] = json.load(open(q, encoding='utf-8')) if os.path.exists(q) else {}
    return _b[v]

# ---------------------------------------------------------------- normalising
LET = re.compile(r'[^a-zāīūṁṃṅñṭḍṇḷ]')
FOLD = str.maketrans({'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n',
                      'ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'})
NAS = str.maketrans({'m':'N','n':'N'})
def letters(s):
    return LET.sub('', (s or '').lower())
def fold(s):
    return letters(s).translate(FOLD)
def nfold(s):
    """fold, then collapse m/n.  The edition writes -ṁ in the text and -n
    before the quotation-closing 'ti' (upaṭṭhānaṁ / upaṭṭhānanti); the two are
    the same word and must compare equal."""
    return fold(s).translate(NAS)

LEAD = re.compile(r'^[\d\s.,\-–()*]+')
TAIL = re.compile(r'(vaṇṇanā|vaṇṇanaṁ|vaṇṇana|vaṇṇānā)$')
KIND = re.compile(r'(suttanta|sutta|pāḷi|kathā|desanā|ṁ)+$')
def stem(s):
    s = letters(LEAD.sub('', (s or '').strip().lower()))
    p = None
    while p != s:
        p = s; s = TAIL.sub('', s); s = KIND.sub('', s)
    return s

# ------------------------------------------------------------- head readers
ORD = {w[:-1] + 'a': v for w, v in ordinal_words.LOC.items()}   # paṭhame->paṭhama
ORDS = sorted(ORD, key=len, reverse=True)
CARD = {'eka':1,'dvi':2,'du':2,'ti':3,'catu':4,'pañca':5,'cha':6,'satta':7,
        'aṭṭha':8,'nava':9,'dasa':10}
FILL = ('gāthā','dvaya','ttaya','pubbaddha','paraddha','pada','pāṭha')
MARK = ('gāthā', 'pāṭha', 'pañha')
QCLOSE = re.compile(r'(iccādi|icceva|ādi|ti)$')

def head_ordinals(name):
    """Ordinals a gāthā head names, in order.  Fires only when the WHOLE head
    is ordinal words plus filler, so an incipit head is never mined for one."""
    s = TAIL.sub('', letters(LEAD.sub('', name or '')))
    if 'gāthā' not in s:
        return []
    got, i = [], 0
    while i < len(s):
        for o in ORDS:
            if s.startswith(o, i):
                got.append(ORD[o]); i += len(o); break
        else:
            for f in FILL:
                if s.startswith(f, i):
                    i += len(f); break
            else:
                return []
    return got

def head_incipit(name):
    """The canon words a head quotes, nasal-folded, or None.  Only heads
    carrying one of the edition's quotation markers -- gāthā, pāṭha, pañha --
    are read this way; `Nikkhepappayojana` names a topic, not a lemma."""
    s = TAIL.sub('', letters(LEAD.sub('', name or '')))
    if head_ordinals(name):
        return None
    hit = [s.find(m) for m in MARK if m in s]
    if not hit:
        return None
    s = QCLOSE.sub('', s[:min(hit)])
    return nfold(s) if len(s) >= 4 else None

def head_part(name):
    """('purima'|'pacchima', k) for `Purimapañcasikkhāpadavaṇṇanā`."""
    s = TAIL.sub('', letters(LEAD.sub('', name or '')))
    for side in ('purima', 'pacchima'):
        if s.startswith(side):
            r = s[len(side):]
            for c in sorted(CARD, key=len, reverse=True):
                if r.startswith(c):
                    return side, CARD[c]
    return None

# ------------------------------------------------------------------- blocks
NUMHEAD = re.compile(r'^\s*(\d+)\.\s*\S')
def blocks(v):
    """The work-level heads of a volume: a `book` head carrying a printed
    number.  `18Khu01` also numbers every Dhammapada vatthu, so the `k` field
    is what keeps 'Yamakavagga' out of the works."""
    S, n = secs(v), len(paras(v))
    heads = [(int(k), S[k][0]['l']) for k in sorted(S, key=int)
             if S[k][0].get('k') in ('book', 'sutta')
             and NUMHEAD.match(S[k][0]['l'])]
    return [(a, (heads[i+1][0]-1 if i+1 < len(heads) else n-1), lbl,
             int(NUMHEAD.match(lbl).group(1)))
            for i, (a, lbl) in enumerate(heads)]

def subsections(v, a, b):
    S = secs(v)
    hs = sorted(i for i in (int(k) for k in S) if a <= i <= b)
    if not hs or hs[0] != a:
        hs = [a] + hs
    return [(s, (hs[k+1]-1 if k+1 < len(hs) else b)) for k, s in enumerate(hs)]

def labels(v, i):
    return [x['l'] for x in secs(v).get(str(i), [])]

# ------------------------------------------------------------------- lemmas
def lemmas(v, o, minlen=6):
    t = paras(v)[o].get('text') or ''
    out = set()
    for a, z in (bold(v).get(str(o)) or []):
        w = re.sub(r'(nti|ti)$', '', letters(t[a:z]))
        if len(w) >= minlen:
            out.add(nfold(w))
    return out

QUOTED = re.compile(r'[“"]([^”"]{6,300})[”"]')

# -------------------------------------------------------------------- place
def place(src, tgt):
    C, A = paras(src), paras(tgt)
    # !!! THE NAME SELECTS, THE NUMBER CONFIRMS -- not the other way round.
    # `18Khu01` numbers 282 Dhammapada vatthu as well as its nine works, so a
    # number-first lookup pairs `1. Yamakavagga` with `1. Saraṇattayavaṇṇanā`.
    tb = {}
    for b in blocks(tgt):
        tb.setdefault(fold(stem(b[2])), []).append(b)
    out, notes = {}, []
    sb = blocks(src)
    pairs = []
    for bi, (ca, cb, clbl, num) in enumerate(sb):
        cs = fold(stem(clbl))
        if len(cs) < 4:          # `2. Desanāsutta` stems to nothing, and an
            continue             # empty stem is a suffix of every name
        cand = [t for k, v in tb.items()
                if min(len(k), len(cs)) >= 4
                and (k == cs or k.endswith(cs) or cs.endswith(k))
                for t in v if t[3] == num]
        if len(cand) != 1:
            if cand:
                notes.append(('SKIP', clbl, '%d target heads of that name' % len(cand)))
            continue
        pairs.append((bi, ca, cb, clbl, cand[0]))
    # !!! KEEP ONLY THE LONGEST RUN OF ADJACENT SOURCE BLOCKS.  `18Khu01` holds
    # the whole Khuddaka: its nine Khuddakapāṭha works are source blocks 0-8,
    # and an isolated pair 500 blocks later is a coincidence of name and number,
    # not a work this commentary covers.
    runs, cur = [], []
    for x in pairs:
        if cur and x[0] != cur[-1][0] + 1:
            runs.append(cur); cur = []
        cur.append(x)
    if cur:
        runs.append(cur)
    keep = max(runs, key=len) if runs else []
    for x in pairs:
        if x not in keep:
            notes.append(('SKIP', x[3], 'isolated from the run of paired works'))
    for bi, ca, cb, clbl, t in keep:
        aa, ab = t[0], t[1]
        subs = subsections(tgt, aa, ab)
        lem = {j: lemmas(tgt, j) for j in range(aa, ab + 1)}
        cf = {i: nfold(C[i].get('text') or '') for i in range(ca, cb + 1)}

        def disc(w):
            """A lemma that occurs in more than one canon paragraph of this
            block discriminates nothing.  THE CONTROL -- see the header."""
            return sum(1 for k in cf if w in cf[k]) == 1

        hord, hinc, hpart, named = collections.defaultdict(list), [], [], set()
        for s, e in subs:
            for l in labels(tgt, s):
                # the work's own head names the WORK, not a unit inside it --
                # `4. Kumārapañhavaṇṇanā` carries the marker `pañha` and would
                # otherwise register as an incipit head and make a block with
                # no unit divisions look sectioned.
                if NUMHEAD.match(l):
                    continue
                o = head_ordinals(l)
                for x in o:
                    hord[x].append(s)
                if o:
                    named.add(s)
                inc = head_incipit(l)
                if inc:
                    hinc.append((s, inc)); named.add(s)
                pt = head_part(l)
                if pt:
                    hpart.append((s, pt)); named.add(s)

        cnum = [i for i in range(ca, cb + 1) if C[i].get('n') is not None]

        # ONE canon paragraph in the block: the block IS its commentary.
        if cb == ca:
            out[ca] = (aa, 'block', {})
            continue

        for i in range(ca, cb + 1):
            n, ct, r = C[i].get('n'), cf[i], {}
            if n is not None and len(set(hord.get(n, []))) == 1:
                r['H-ord'] = hord[n][0]
            hit = [s for s, inc in hinc if ct.startswith(inc)]
            if len(hit) > 1:            # several heads quote the same opening:
                keep = [s for s in hit  # prefer one that carries the number
                        if any(A[j].get('n') == n for j in range(s, min(s + 3, ab + 1)))]
                hit = keep
            if len(hit) == 1:
                r['H-inc'] = hit[0]
            if n is not None:
                cand = [j for j in range(aa, ab + 1) if A[j].get('n') == n]
                if cand:
                    r['NUM'] = max([s for s, e in subs if s <= cand[0]] or [aa])
            for s, (side, k) in hpart:
                if i in cnum:
                    pos = cnum.index(i) + 1
                    if (side == 'purima' and pos <= k) or \
                       (side == 'pacchima' and pos > len(cnum) - k):
                        r['H-part'] = s
            if named:
                # SECTIONED block: score whole sub-sections.
                sc = []
                for s, e in subs:
                    ch = sum(len(w) for w in
                             set().union(*[lem[j] for j in range(s, e + 1)])
                             if w in ct and disc(w))
                    sc.append((ch, -s, s))
                sc.sort(reverse=True)
                if sc and sc[0][0] > 0:
                    r['GLOSS'] = sc[0][2]; r['_g'] = sc[0][0]
            else:
                # UNSECTIONED block (no head names a unit): score paragraphs.
                # A prefix quote -- the commentary announcing the canon lemma
                # it is about -- counts double; the gloss breaks the tie.
                sc = []
                for j in range(aa, ab + 1):
                    q = max([len(nfold(x)) for x in QUOTED.findall(A[j].get('text') or '')
                             if len(nfold(x)) >= 8 and ct.startswith(nfold(x))] or [0])
                    ch = sum(len(w) for w in lem[j] if w in ct and disc(w))
                    if q or ch:
                        sc.append((2 * q + ch, -j, j))
                sc.sort(reverse=True)
                if sc:
                    r['GLOSS'] = sc[0][2]; r['_g'] = sc[0][0]
            # DECIDE.  The gloss is the edition's own statement of what is being
            # glossed and outranks a head's gāthā count where the two differ.
            # H-part first: `Purimapañcasikkhāpadavaṇṇanā` is the edition
            # stating WHICH CANON UNITS this passage comments on, and the block
            # holds no finer division, so a lemma hit inside it can only pick a
            # sub-topic of the same passage -- a worse landing, not a better one.
            pick = r.get('H-part') or r.get('GLOSS') or r.get('H-inc') \
                or r.get('H-ord') or r.get('NUM')
            by = ('part' if 'H-part' in r else 'gloss' if 'GLOSS' in r
                  else 'name' if 'H-inc' in r else 'ord' if 'H-ord' in r
                  else 'num' if 'NUM' in r else None)
            if pick is not None:
                out[i] = (pick, by, r)

        # !!! ONE GAP FILL, AND IT FIRES ONCE.  Where the gloss is silent and an
        # ordinal head collapses this paragraph onto the previous one's target
        # while exactly one unclaimed sub-head lies between the neighbours, the
        # head's gāthā count has run ahead of the canon's -- the Tirokuṭṭa fault
        # in the header.  Ordinal-placed only: a `H-part` head covers a run of
        # canon units ON PURPOSE and must not be split.
        taken = {v[0] for v in out.values()}
        for i in range(ca + 1, cb):
            if i not in out or out[i][1] != 'ord':
                continue
            prev, nxt = out.get(i - 1), out.get(i + 1)
            if not prev or not nxt or out[i][0] != prev[0]:
                continue
            free = [s for s, e in subs if prev[0] < s < nxt[0] and s not in taken]
            if len(free) == 1:
                out[i] = (free[0], 'ord-gap', out[i][2])
                taken.add(free[0])
    return out, notes


def build(src, tgt, apply=False):
    C, A = paras(src), paras(tgt)
    got, notes = place(src, tgt)
    f = os.path.join(LINKS, src + '.links.json')
    L = json.load(open(f, encoding='utf-8'))
    before = collections.Counter()
    for k, e in L.items():
        st = [x['state'] for x in e.get('commentary', []) if x['key'].startswith(tgt + '#')]
        before['direct' if 'direct' in st else 'covered' if st else 'none'] += 1
    changed = 0
    for i, (o, by, r) in sorted(got.items()):
        e = L.setdefault(str(i), {})
        key = '%s#%d' % (tgt, o)
        # !!! THE EXISTING RECORDS ARE KEPT.  They are `covered` pointers that
        # draw no chip and that the reader never follows, and `check_links`'
        # `reachable` is a ratchet built so that a map cannot raise its rates by
        # dropping what it cannot place.  Removing them is a separate, separately
        # measurable decision -- the shape of `6f7e5629`'s prune -- and not part
        # of this repair.  Only an existing record for the SAME key is dropped,
        # so the map does not gain a duplicate.
        arr = [x for x in e.get('commentary', []) if x['key'] != key]
        # !!! `n` ONLY WHERE THE TARGET REALLY CARRIES IT.  A record reading
        # `"n": 1` while pointing at a paragraph with no number is the exact
        # self-contradiction `check_links.py` was written to catch, and this
        # placement was not made by the number in the first place.
        cn, tp = C[i].get('n'), A[o]
        m = re.match(r'^\s*(\d+)\s*[-–]\s*(\d+)\s*\.', tp.get('text') or '')
        carries = cn is not None and (tp.get('n') == cn or
                                      (m and int(m.group(1)) <= cn <= int(m.group(2))))
        rec = {'key': key, 'state': 'direct', 'n': cn if carries else None,
               'by': by}
        old = [x for x in e.get('commentary', []) if x['key'].startswith(tgt + '#')]
        if not old or old[0].get('key') != rec['key'] or old[0].get('state') != 'direct':
            changed += 1
        # !!! FIRST, NOT LAST.  `jumpFrom` in reader2.html takes `arr[0]` of the
        # DIRECT targets, so a stale direct record from another volume in front
        # of this one would send the chip there instead.  Canon 15 carries
        # `46KhuA27#76 direct` from an older build; the reader must land in this
        # work's own commentary.
        e['commentary'] = [rec] + arr
    dest = LINKS if apply else OUT
    os.makedirs(dest, exist_ok=True)
    json.dump(L, open(os.path.join(dest, src + '.links.json'), 'w',
                      encoding='utf-8'), ensure_ascii=False)
    return got, notes, before, changed, dest


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('-')]
    if len(a) != 2:
        print(__doc__); sys.exit(2)
    src, tgt = a
    got, notes, before, changed, dest = build(src, tgt, '--apply' in sys.argv)
    C = paras(src)
    print('%s -> %s   wrote %s' % (src, tgt, dest))
    for x in notes:
        print('  %s %s: %s' % x)
    by = collections.Counter(v[1] for v in got.values())
    print('  placed %d canon paragraphs: %s' % (len(got), dict(by)))
    print('  records that changed: %d' % changed)
    for i in sorted(got):
        o, b, r = got[i]
        keys = {k: v for k, v in r.items() if not k.startswith('_')}
        split = len(set(keys.values())) > 1
        print('   %4d n=%-5s -> %s#%-4d by=%-8s %s%s'
              % (i, C[i].get('n'), tgt, o, b, keys, '   <-- SPLIT' if split else ''))
