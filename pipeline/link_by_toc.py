#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Place canon->commentary links from the two TABLES OF CONTENTS, vagga by vagga.

WHY.  Reader, 2026-08-07: "The concordance is for general understanding of the
relations between the three ... We should go book by book to determine the exact
links."  The concordance says `20Khu03 -> 32KhuA13` and that is true at the level
it works at.  It does NOT mean `32KhuA13` covers the canon volume: `32KhuA13`
carries `Therāpadāna / 1. Buddhavagga` and nothing else, while canon `20Khu03`
runs to `42. Bhaddālivagga`.  Reading the concordance as a link map is what put
canon Apadāna paragraphs into the Jātaka and Cariyāpiṭaka commentaries.

THE ORDER, AND IT IS THE READER'S:  vagga -> section -> number -> gloss.

  VAGGA   `20Khu03` is 42 vaggas and THE PARAGRAPH NUMBER RESTARTS AT EACH ONE.
          Buddhavagga runs n 1..663; `2. Sīhāsaniyavagga` then restarts at n 1.
          Measured over the volume: 4,461 numbered paragraphs carry only 663
          distinct numbers, 519 of them non-unique, median 3 candidates, max 42.
          So the number cannot choose the vagga -- the vagga is chosen first.
  SECTION the two TOCs pair one for one by name.  `3-9. Khadiravaniyarevatatthera-
          apadāna` (canon) / `3-9. Khadiravaniyatthera-apadānavaṇṇanā`
          (commentary) -- the printed numbering `3-N.` agrees and the stems match
          after -vaṇṇanā is stripped.  Both criteria must hold.
  NUMBER  INSIDE a paired section the numbers are the edition's own and are
          unique, so the number places the link.  This is the reader's stated
          preference and it is correct once the section is fixed.
  GLOSS   the commentary's bold marks the canon words it glosses, so a shared
          lemma CONFIRMS the placement.  It is reported, never used to place --
          `link_by_gloss.py` is the tool for the case where the number is absent
          or has run out of step, and this file does not duplicate it.

!!! AN ABSENT NUMBER IS A RESULT, NOT A MISS.  Inside a paired section the
commentary's numbers are enumerable, so a canon number that is not among them is
NOT COMMENTED -- a fact about the printed page, established without searching for
anything.  That matters because the string search that would otherwise be needed
fails in the dangerous direction: sandhi hides `indriyāni` inside `yassindriyāni`
and a plain match reports "no gloss found", which becomes a confident denial.
Here nothing is searched for, so nothing can be missed.  Reader's decision of
2026-08-07: those paragraphs get NO CHIP and the verdict `not_commented`.
Outside a paired section the verdict is `cannot_establish` and is never collapsed
into `not_commented`.

!!! THE ABBREVIATED RANGE.  The edition prints `234-5.` meaning 234-235 and
`275-7.` meaning 275-277, alongside the full `278-281.`.  A naive
`(\\d+)-(\\d+)` reads `234-5` as the empty range and silently reports 235 as
uncommented.  `expand_range` restores the elided leading digits.  This was found
by counting gaps twice with and without it -- see `--stats`.

SCOPE.  One canon volume, one commentary volume, one vagga (or all), per run.
`build_links_bynum.py` records with numbers that a corpus-wide rebuild lost on
both axes at once.

Writes to `_xc/linksk_toc/`, NEVER into `site/` without `--apply`: `site/` is
published and hashed into BUILD, so a dry run there would move the cache-buster
for every visitor.

Usage:
  python3 pipeline/link_by_toc.py 20Khu03 32KhuA13 --vagga 1           # dry
  python3 pipeline/link_by_toc.py 20Khu03 32KhuA13 --vagga 1 --stats
  python3 pipeline/link_by_toc.py 20Khu03 32KhuA13 --vagga 1 --apply
"""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')
OUT = os.path.join(ROOT, '_xc', 'linksk_toc')

# ---------------------------------------------------------------- loading
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
FOLD = str.maketrans({'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm',
                      'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ḷ': 'l'})
NAS = str.maketrans({'m': 'N', 'n': 'N'})
LEAD = re.compile(r'^[\d\s.,\-–()*]+')
TAIL = re.compile(r'(vaṇṇanā|vaṇṇanaṁ|vaṇṇana|vaṇṇānā)$')
KIND = re.compile(r'(suttanta|sutta|apadāna|apadāna|pāḷi|kathā|desanā|ṁ)+$')


def letters(s):
    return LET.sub('', (s or '').lower())


def nfold(s):
    """fold, then collapse m/n -- the edition writes -ṁ in the text and -n before
    a quotation-closing `ti` (upaṭṭhānaṁ / upaṭṭhānanti); same word."""
    return letters(s).translate(FOLD).translate(NAS)


def stem(s):
    """A comparable core for `3-9. Khadiravaniyarevatatthera-apadāna` and
    `3-9. Khadiravaniyatthera-apadānavaṇṇanā`.  Blunt on purpose: it decides
    WHICH SECTION and never asserts that two things are the same text."""
    s = letters(LEAD.sub('', (s or '').strip().lower()))
    p = None
    while p != s:
        p = s
        s = TAIL.sub('', s)
        s = KIND.sub('', s)
    # the edition spells the same thera both `-atthera` and `-attera`, and the
    # canon may carry a fuller name (`Khadiravaniyarevata`) than the commentary
    s = s.translate(FOLD)
    s = re.sub(r'a(t+)hera$', '', s)
    s = re.sub(r'(.)\1', r'\1', s)
    return s


# ---------------------------------------------------------------- TOC numbering
# `3-1.`, `3. 1.`, `1.` -- the printed unit number, as a tuple so `3-1` and `1`
# stay distinguishable.  The canon prints `3. 3. Mahākassapatthera-apadāna` where
# the commentary prints `3-3.`; both mean the same unit.
TOCNUM = re.compile(r'^\s*(\d+)\s*(?:[-.]\s*(\d+))?\s*\.\s*(?=\S)')


def tocnum(l):
    """The printed unit number as a tuple: `1.` -> (1,), `3-1.` -> (3, 1).

    !!! THE TWO SIDES PUNCTUATE IT DIFFERENTLY.  The canon prints
    `3. 3. Mahākassapatthera-apadāna` and the commentary `3-3. Mahākassapatthera-
    apadānavaṇṇanā`; both mean unit 3 of group 3.  A hyphen and a full stop are
    therefore the same separator here, and the tuple keeps `3-1` distinct from
    `1`, which is what stops `1. Buddha-apadāna` pairing with `3-1. Sāriputta`.
    """
    m = TOCNUM.match(l or '')
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2))) if m.group(2) else (int(m.group(1)),)


# ---------------------------------------------------------------- ranges
# !!! ONE IMPLEMENTATION, FOR ALL BOOKS.  `expand_range` was written here first
# and now lives in `printed_range.py` with its own selftest, because three other
# files in this directory carried the naive form -- including `check_links.py`,
# the ratchet.  Reader, 2026-08-07: "You should remember this for all books."
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from printed_range import expand_range, RANGE     # noqa: E402,F401


def numbers_in(v, a, b):
    """{number -> ordinal} for [a,b] of volume v, ranges expanded."""
    P, out = paras(v), {}
    for j in range(a, min(b, len(P) - 1) + 1):
        n = P[j].get('n')
        if n is not None:
            out.setdefault(n, j)
        r = expand_range(P[j].get('text') or '')
        if r:
            for x in range(r[0], r[1] + 1):
                out.setdefault(x, j)
    return out


# ---------------------------------------------------------------- structure
def heads(v, kind):
    out = []
    S = secs(v)
    for k in sorted(S, key=int):
        for x in S[k]:
            if x.get('k') == kind:
                out.append((int(k), x['l']))
    return out


def spans(hs, end):
    return [(a, (hs[i + 1][0] - 1 if i + 1 < len(hs) else end), l)
            for i, (a, l) in enumerate(hs)]


def vaggas(v):
    return spans(heads(v, 'vagga'), len(paras(v)) - 1)


def sections_in(v, a, b):
    hs = [(i, l) for i, l in heads(v, 'sutta') if a <= i <= b]
    return spans(hs, b)


# ---------------------------------------------------------------- pairing
def pair_sections(csec, asec):
    """Pair canon sections to commentary sections by TOC number AND stem.

    !!! BOTH CRITERIA, AND THEN THE LONGEST MONOTONIC RUN.  A name alone repeats
    across the corpus (`Buddhasaññakatthera-apadāna` occurs in two canon volumes)
    and a printed unit number alone repeats in every vagga.  Requiring both, and
    then keeping only the longest run of pairs whose order agrees on both sides,
    is `link_by_gloss.py`'s discriminator; an isolated pair far from the run is a
    coincidence of name and number, not a work this commentary covers.
    """
    A = [(tocnum(l), stem(l)) for a, b, l in asec]
    pairs, notes = [], []
    for i, (a, b, l) in enumerate(csec):
        cn, cs = tocnum(l), stem(l)
        # !!! THE STEMS ARE COMPATIBLE, NOT EQUAL.  The canon prints
        # `3-9. Khadiravaniyarevatatthera-apadāna` and the commentary
        # `3-9. Khadiravaniyatthera-apadānavaṇṇanā` -- the same elder, the canon
        # carrying the fuller name.  Demanding equality drops that pair, and
        # dropping it broke the run so that `3-10. Ānanda` was then discarded as
        # isolated: one over-strict comparison cost two sections.  Prefix
        # containment either way, with the printed unit number as the control.
        def ok(k):
            an, as_ = A[k]
            if an != cn or min(len(as_), len(cs)) < 4:
                return False
            return as_.startswith(cs) or cs.startswith(as_)
        cand = [k for k in range(len(asec)) if ok(k)]
        if len(cand) != 1:
            loose = [k for k in range(len(asec)) if A[k][1] == cs and len(cs) >= 4]
            if len(loose) == 1:
                cand = loose
                notes.append(('NUM DIFFERS', l, asec[loose[0]][2]))
            else:
                notes.append(('UNPAIRED', l,
                              '%d commentary sections match' % len(cand or loose)))
                continue
        if stem(asec[cand[0]][2]) != cs:
            notes.append(('NAME DIFFERS', l, asec[cand[0]][2]))
        pairs.append((i, cand[0]))
    runs, cur = [], []
    for x in pairs:
        if cur and (x[0] != cur[-1][0] + 1 or x[1] < cur[-1][1]):
            runs.append(cur)
            cur = []
        cur.append(x)
    if cur:
        runs.append(cur)
    keep = max(runs, key=len) if runs else []
    for x in pairs:
        if x not in keep:
            notes.append(('DROPPED', csec[x[0]][2], 'isolated from the paired run'))
    return keep, notes


# ---------------------------------------------------------------- gloss check
def lemmas(v, o, minlen=6):
    t = paras(v)[o].get('text') or ''
    out = set()
    for a, z in (bold(v).get(str(o)) or []):
        w = re.sub(r'(nti|ti)$', '', letters(t[a:z]))
        if len(w) >= minlen:
            out.add(nfold(w))
    return out


# ---------------------------------------------------------------- place
def place(src, tgt, vagga=None):
    C, A = paras(src), paras(tgt)
    vs = vaggas(src)
    # `unclaimed` collects the numbers carried by commentary sections that no
    # canon section paired with -- see the note beside its use below.
    unclaimed = {}
    if vagga is not None:
        vs = [x for x in vs if tocnum(x[2]) and tocnum(x[2])[0] == vagga]
        if not vs:
            raise SystemExit('no vagga %s in %s' % (vagga, src))
    # the commentary's own vagga head bounds the region it covers; front matter
    # (Ganthārambhakathā .. Santikenidānakathā) lies before it and is not a target
    avs = vaggas(tgt) or [(0, len(A) - 1, '')]
    out, gaps, notes, unpaired, unsure = {}, [], [], [], []
    for (ca, cb, clbl) in vs:
        cvn = tocnum(clbl)
        av = [x for x in avs if tocnum(x[2]) == cvn] or \
             ([avs[0]] if len(avs) == 1 else [])
        if not av:
            notes.append(('NO VAGGA', clbl, 'not in %s' % tgt))
            continue
        aa, ab, albl = av[0]
        csec = sections_in(src, ca, cb)
        asec = sections_in(tgt, aa, ab)
        pairs, n2 = pair_sections(csec, asec)
        notes += [(a, b, c) for a, b, c in n2]
        paired_c = {i for i, _ in pairs}
        for i, (a, b, l) in enumerate(csec):
            if i not in paired_c:
                unpaired.append((a, b, l))
        # !!! A COMMENTARY SECTION NO CANON SECTION PAIRED WITH STILL CARRIES
        # NUMBERS, AND THEY ARE NOT SILENCE.  `32KhuA13` opens Buddhavagga with
        # `Abbhantaranidānavaṇṇanā` (p. 111), the commentary's own introduction
        # to the Therāpadāna; the canon has no section facing it, so it pairs
        # with nothing -- yet it carries n=5 and quotes canon 5 outright
        # ("5. Atha Buddhāpadānāni, suṇātha suddhamānasā").  Counting 5 as
        # not_commented because it fell outside every pair would be exactly the
        # untested absence stated as a claim that this file exists to prevent.
        # So numbers held by unpaired commentary sections downgrade the verdict
        # to `cannot_establish` and are reported for the reader to settle.
        paired_a = {k for _, k in pairs}
        for k, (a0, a1, al) in enumerate(asec):
            if k not in paired_a:
                for n in numbers_in(tgt, a0, a1):
                    unclaimed.setdefault(n, al)
        for ci, ai in pairs:
            c0, c1, cl = csec[ci]
            a0, a1, al = asec[ai]
            avail = numbers_in(tgt, a0, a1)
            for j in range(c0, c1 + 1):
                n = C[j].get('n')
                if n is None:
                    continue
                o = avail.get(n)
                if o is None:
                    if n in unclaimed:
                        unsure.append((j, n, cl, unclaimed[n]))
                    else:
                        gaps.append((j, n, cl, al))
                    continue
                lem = lemmas(tgt, o)
                ct = nfold(C[j].get('text') or '')
                hit = sorted(w for w in lem if w in ct)
                out[j] = (o, n, cl, al, hit, len(lem))
    return out, gaps, notes, unpaired, unsure


# ---------------------------------------------------------------- write
def build(src, tgt, vagga=None, apply=False):
    got, gaps, notes, unpaired, unsure = place(src, tgt, vagga)
    f = os.path.join(LINKS, src + '.links.json')
    L = json.load(open(f, encoding='utf-8'))
    touched = {j for j in got} | {g[0] for g in gaps}
    before = collections.Counter()
    for j in sorted(touched):
        for t in (L.get(str(j), {}).get('commentary') or []):
            before[t['key'].split('#')[0] + ' ' + str(t.get('state'))] += 1
    changed = removed = 0
    foreign = collections.Counter()

    def strip_ineligible(e):
        """!!! WITHIN THIS VAGGA, `tgt` IS THE ONLY ELIGIBLE COMMENTARY, so a
        record pointing anywhere else is ineligible whatever its number says.
        The first version of this function dropped only `tgt` records on a
        not_commented paragraph and kept the foreign ones -- so canon n=248,
        which the check had just established is NOT commented, went on drawing a
        live chip into `41KhuA22`, the Jātaka commentary.  The verdict said one
        thing and the link data did another.  Caught by running the check, not
        by reading this.  Every drop is counted into `foreign` and printed."""
        old = e.get('commentary') or []
        keep = [x for x in old if x['key'].split('#')[0] == tgt]
        for x in old:
            v = x['key'].split('#')[0]
            if v != tgt:
                foreign[v] += 1
        return old, keep

    for j, (o, n, cl, al, hit, nl) in got.items():
        e = L.setdefault(str(j), {})
        key = '%s#%d' % (tgt, o)
        old, keep = strip_ineligible(e)
        removed += len(old) - len(keep)
        # !!! FIRST, NOT LAST.  `jumpFrom` in reader2.html takes arr[0] of the
        # direct targets, so a stale record in front of this one would send the
        # chip there instead.
        rec = {'key': key, 'state': 'direct', 'n': n, 'by': 'toc'}
        if not old or old[0].get('key') != key or old[0].get('state') != 'direct':
            changed += 1
        # !!! THE NEW RECORD REPLACES, IT DOES NOT JOIN A QUEUE.  `link_by_gloss.py`
        # keeps the old `covered` records on purpose, because there the placement
        # is a proposal and `check_links.py`'s `reachable` ratchet exists so a map
        # cannot raise its rates by dropping what it could not place.  Here the
        # placement is not a proposal: the two TOCs pair the sections and the
        # edition's own number places the paragraph inside the pair, so any other
        # record for this volume is a superseded guess.  Keeping them was measured:
        # 56 stale records survived, each carrying the OLD builder's `n`, and the
        # check that every record's target really carries its number failed on all
        # 56 while the new records passed.  A second wrong answer sitting behind
        # the right one is still wrong data in the file.
        removed += len([x for x in keep if x['key'] != key])
        e['commentary'] = [rec]
        e.pop('verdict', None)
    for j, n, cl, al in gaps:
        # !!! THE ENTRY IS CREATED IF IT IS MISSING.  8 of the 133 canon
        # paragraphs found uncommented had no link record at all, so writing the
        # verdict only onto existing entries lost them and the accounting did
        # not close -- 543 + 125 + 1 = 669 against 663 canon numbers. An
        # arithmetic identity that must hold is the cheapest check there is.
        e = L.setdefault(str(j), {})
        old, keep = strip_ineligible(e)
        removed += len(old)
        # !!! NO CHIP.  Reader's decision of 2026-08-07.  Inside a paired section
        # the commentary's numbers are enumerable, so an absent number is the
        # printed page's own silence and not a failed search -- nothing was
        # searched for, so sandhi cannot have hidden it.  The paragraph keeps an
        # entry carrying the verdict rather than being deleted, so that
        # `check_links.py`'s `reachable` ratchet sees the change instead of the
        # map quietly getting smaller.
        e['commentary'] = []
        e['verdict'] = {'why': 'not_commented', 'layer': 'commentary',
                        'vol': tgt, 'n': n, 'section': cl, 'by': 'toc'}
    for j, n, cl, al in unsure:
        e = L.setdefault(str(j), {})
        old, keep = strip_ineligible(e)
        removed += len(old)
        # !!! NO CHIP HERE EITHER, AND FOR THE OPPOSITE REASON.  `not_commented`
        # draws nothing because the edition is silent; this draws nothing because
        # WE cannot tell, and a link is an assertion.  The two must stay distinct
        # in the data even though they look the same on the page -- collapsing
        # the third state into the second is the failure the header names, and it
        # would happen here first, on the one paragraph where it is visible.
        e['commentary'] = []
        e['verdict'] = {'why': 'cannot_establish', 'layer': 'commentary',
                        'vol': tgt, 'n': n, 'section': cl, 'held_by': al,
                        'by': 'toc'}
    dest = LINKS if apply else OUT
    os.makedirs(dest, exist_ok=True)
    json.dump(L, open(os.path.join(dest, src + '.links.json'), 'w',
                      encoding='utf-8'), ensure_ascii=False)
    return (got, gaps, notes, unpaired, unsure, before, changed, removed,
            foreign, dest)


# ---------------------------------------------------------------- main
if __name__ == '__main__':
    argv = sys.argv[1:]
    vg = None
    if '--vagga' in argv:
        k = argv.index('--vagga')
        vg = int(argv[k + 1])
        del argv[k:k + 2]          # !!! the VALUE too, or it reads as a volume
    a = [x for x in argv if not x.startswith('-')]
    if len(a) != 2:
        print(__doc__)
        sys.exit(2)
    src, tgt = a
    (got, gaps, notes, unpaired, unsure, before, changed, removed,
     foreign, dest) = build(src, tgt, vg, '--apply' in sys.argv)
    C, A = paras(src), paras(tgt)
    print('%s -> %s%s   wrote %s'
          % (src, tgt, '  vagga %d' % vg if vg else '', dest))
    for x in notes:
        print('  %-12s %-46s %s' % x)
    for a0, b0, l in unpaired:
        print('  %-12s %-46s ord %d-%d' % ('NO PAIR', l, a0, b0))
    print()
    conf = sum(1 for v in got.values() if v[4])
    withb = sum(1 for v in got.values() if v[5])
    print('  placed              %5d' % len(got))
    print('    gloss confirms    %5d  of %d with bold in the target (%.1f%%)'
          % (conf, withb, 100.0 * conf / withb if withb else 0))
    print('  not commented       %5d' % len(gaps))
    print('  CANNOT ESTABLISH    %5d  (number held by an unpaired commentary'
          ' section)' % len(unsure))
    for j, n, cl, al in unsure:
        print('      canon n=%-5s %-38s -> %s' % (n, cl[:38], al))
    print('  records changed     %5d' % changed)
    print('  records removed     %5d' % removed)
    for v, c in foreign.most_common():
        print('    ineligible in this vagga: %-10s %5d' % (v, c))
    print()
    print('  was, over the same paragraphs:')
    for k, v in before.most_common():
        print('    %-24s %5d' % (k, v))

    if '--stats' in sys.argv:
        print()
        print('  ABBREVIATED RANGES in %s (`234-5.` = 234-235):' % tgt)
        bad = 0
        for j, p in enumerate(A):
            m = RANGE.match(p.get('text') or '')
            if m and len(m.group(2)) < len(m.group(1)):
                bad += 1
                if bad <= 6:
                    print('    ord %-4d p.%-4s %s'
                          % (j, p.get('printed'), (p.get('text') or '')[:60]))
        print('    %d in the volume; without expand_range each would have'
              ' produced a false not_commented' % bad)
        print()
        print('  NOT COMMENTED, as printed-number runs:')
        cur = []
        run = []
        for j, n, cl, al in gaps + [(None, None, None, None)]:
            if run and cl == run[-1][2] and n == run[-1][1] + 1:
                run.append((j, n, cl, al))
                continue
            if run:
                cur.append((run[0][2], run[0][1], run[-1][1]))
            run = [(j, n, cl, al)] if j is not None else []
        last = None
        for cl, lo, hi in cur:
            if cl != last:
                print('    %s' % cl)
                last = cl
            print('       n %s' % (lo if lo == hi else '%d-%d' % (lo, hi)))
