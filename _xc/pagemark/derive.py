# -*- coding: utf-8 -*-
"""DERIVE EACH PARAGRAPH'S PAGE BREAKS FROM THE PRINTED PAGE.

THE DEFECT.  A corpus paragraph carries ONE `printed` -- the folio it BEGINS on
-- so `block()` in reader2.html can only ever put a page rule at a paragraph
boundary.  Measured over 118 volumes and 30,506 printed pages
(`claude/the_page_marker_is_late_in_two_pages_of_three.md`): 19,727 page breaks
(64.7%) fall INSIDE a paragraph and only 33.9% of markers are drawn on the
letter the page turns at.

THE DATA.  A paragraph must carry its page BREAKS, not one page:

    site/reader/pbreak/<VOL>.json = {"<ord>": [[rawOffset, printed, pdfPage,
                                                 drawnIndex, drawnOffset], ...]}

`rawOffset` is a HALF-OPEN CHARACTER OFFSET INTO THE PARAGRAPH'S RAW `text` --
the same address space `bold/<VOL>.bold.json` uses, deliberately, so that
`_xc/reseg/redistribute.py`'s bold arithmetic carries page breaks through a
re-segmentation with no new proof needed.  Offset 0 means the page opens at the
paragraph's own head, -1 means the page opens ABOVE this ordinal's heading group.

!!! AND THAT ADDRESS IS NOT ENOUGH, because the VERSE BRANCH OF `block()` DOES
NOT DRAW THE CORPUS TEXT.  When `verse/<VOL>.json` carries `groups` for an
ordinal the reader draws `before` + the group padas + `after` from the PRINTED
stream and never renders `pr.text`, so a character offset into `pr.text` is not
an address in what is on screen.  MEASURED: 31,247 of 35,385 mid-paragraph
breaks corpus-wide are on such ordinals -- the majority of the repair, not an
edge case -- and with only `rawOffset` they fell through to an end-of-body flush
that in `40Abhi12` stacked `page 73` immediately above `page 63`, 18 of 18 rules
misplaced.

So a record on such an ordinal carries a SECOND address, in the space the verse
branch actually draws in:

  `drawnIndex`  -- the index into the FLAT sequence of `fmtLine` calls the
                   reader makes (`before` items, then the group padas, then
                   `after` items, in that order), and
  `drawnOffset` -- the character offset INSIDE that drawn string, because an
                   `after` entry is a whole printed paragraph, not one printed
                   line: 71 of 226 located breaks in `40Abhi12` fall inside one.

They are computed by locating the page's own FIRST PRINTED LINE in the entry's
own drawn strings -- printed evidence on both sides, nothing from the corpus.
Both addresses are written; the band views cut `pr.text` at `rawOffset` and the
spine's verse branch flushes by counter at `drawnIndex`.  Where the printed line
cannot be located among the drawn strings the two extra elements are absent and
the reader keeps its bounded end-of-paragraph flush.

THE EVIDENCE IS THE PRINTED PAGE, never the corpus alone.  The printed line
stream is `_xc/reseg/pline.py` (extract.py's own raw_pages + split_page with the
glyph-errata register, so running heads and the apparatus are already gone); the
folio of every pdf page is `_xc/pagemark/folio.py`, read from the running header
by extract.py's own arithmetic and OVERRIDDEN by the corpus's own (pdf_page ->
printed) wherever a paragraph starts on that page, so the numbers the reader
cites do not move.  Each printed line is located in the corpus letter string by
the k-gram index `check_page_fidelity.py` already uses, monotonically.

ONLY WHAT THE PRESENT MECHANISM GETS WRONG IS WRITTEN.  A page that opens at a
paragraph head whose `printed` already equals it needs no record and gets none;
the map is the correction, not a duplicate of the corpus.

  python3 _xc/pagemark/derive.py <VOL> [...] [--out DIR] [--budget N] [--shard i:n]
"""
import sys, os, json, bisect, collections, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
sys.path.insert(0, HERE)
import check_page_fidelity as CPF   # noqa: E402
import pline                        # noqa: E402
import folio as FOL                 # noqa: E402

letters = CPF.letters
Index = CPF.Index
BACK = 40000
ALPHA = CPF.ALPHA if hasattr(CPF, 'ALPHA') else None


def jload(p, d=None):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception:
        return d


def lettermap(s):
    """(letters-only string, [raw index of each letter])."""
    out, pos = [], []
    for i, ch in enumerate(s or ''):
        if not letters(ch):
            continue
        out.append(ch)
        pos.append(i)
    return ''.join(out), pos


# !!! THE FLAT SEQUENCE OF `fmtLine` CALLS, mirroring `block()`'s verse branch in
# `site/reader/reader2.html` exactly: `before` (proseBlocks -> proseOne), then
# every pada of every group, then `after`.  `pre`'s udana fallback is `fmtText`,
# not `fmtLine`, and `tail` is `esc` -- neither is a call and neither is counted.
# If that render order ever changes this function must change with it, which is
# why it is written next to the reason rather than inferred at runtime.
def flat_drawn(vm):
    seq = []

    def one(p):
        if isinstance(p, dict):
            if p.get('gatha') is not None:
                for l in p['gatha']:
                    seq.append('' if l is None else str(l))
                return
            if p.get('t') is not None:
                seq.append(str(p['t']))
                return
        seq.append('' if p is None else str(p))

    def blocks(x):
        if isinstance(x, list):
            for p in x:
                one(p)
        elif x is not None:
            seq.append(str(x))

    if vm.get('before') is not None:
        blocks(vm['before'])
    for g in (vm.get('groups') or []):
        for l in g:
            seq.append('' if l is None else str(l))
    if vm.get('after') is not None:
        blocks(vm['after'])
    return seq


def drawn_index(vm):
    """(letters of every drawn string joined, [(item, raw char offset)] per letter)."""
    D = flat_drawn(vm)
    L, M = [], []
    for i, sv in enumerate(D):
        for j, ch in enumerate(sv):
            if letters(ch):
                L.append(ch)
                M.append((i, j))
    return ''.join(L), M


def _lnds(v):
    """indices of a longest NON-DECREASING subsequence of v (patience, O(n log n))."""
    tails, idx, back = [], [], [-1] * len(v)
    for i, x in enumerate(v):
        j = bisect.bisect_right(tails, x)
        if j == len(tails):
            tails.append(x)
            idx.append(i)
        else:
            tails[j] = x
            idx[j] = i
        back[i] = idx[j - 1] if j else -1
    out, i = [], (idx[-1] if idx else -1)
    while i >= 0:
        out.append(i)
        i = back[i]
    return out[::-1]


def derive(vol):
    S = os.path.join(ROOT, 'site')
    c = jload('%s/%s.json' % (S, vol))
    if not c:
        return None
    paras = c.get('paragraphs', [])
    if not paras:
        return None
    hide = jload('%s/reader/hide/%s.json' % (S, vol), {}) or {}
    verse = jload('%s/reader/verse/%s.json' % (S, vol), {}) or {}

    buf, starts, rawpos = [], [], []
    pos = 0
    for p in paras:
        s, rp = lettermap(p.get('text', '') or '')
        starts.append(pos)
        buf.append(s)
        rawpos.append(rp)
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

    # --- the folio of every pdf page: the header's, overridden by the corpus's own
    F = dict(FOL.folio(vol))
    over = 0
    for p in paras:
        pg, pr = p.get('pdf_page'), p.get('printed')
        if pg and isinstance(pr, int):
            if F.get(pg) != pr:
                over += 1
            F[pg] = pr

    # --- where each printed page truly begins
    # !!! AND IT MUST NOT GO BACKWARDS.  `loc` falls back to `IX.findany` when the
    # monotone find fails, which can put a short repeated line at an occurrence
    # THOUSANDS of characters ahead of the page before it.  Written unguarded that
    # produced `40Abhi12` ord391 carrying [[219, p.73], [236, p.63]] -- the reader
    # drew `page 73` and then `page 63` two words later, which is the "18 of 18
    # misplaced" this file's own fixture reported.  A page whose position is not
    # at or after the previous page's is DROPPED, not written: no record means the
    # old paragraph-boundary behaviour, which is late but never out of order.
    # DROPPING EVERYTHING AFTER A SPIKE WOULD BE WORSE THAN THE SPIKE: one bad
    # jump ahead sets the running maximum and every honest page after it looks
    # backwards (tried, and it cost `40Abhi12` 291 of its 331 ordinals).  So the
    # candidates are collected first, in page order, and the LONGEST NON-DECREASING
    # SUBSEQUENCE of their positions is kept -- the largest set of pages that can
    # all be true at once.  What is dropped is the spike.
    cand = []
    seenf = set()
    for k, l in enumerate(lines):
        pg = F.get(l[0])
        if pg is None or pg in seenf or loc[k] < 0:
            continue
        seenf.add(pg)
        cand.append((pg, l[0], loc[k], l[3]))
    keep = _lnds([c[2] for c in cand])
    _nonmono = len(cand) - len(keep)
    truepos, truepdf, trueline = {}, {}, {}
    for i in keep:
        pg, pdfp, ps, tx = cand[i]
        truepos[pg] = ps
        truepdf[pg] = pdfp
        trueline[pg] = tx

    out = collections.defaultdict(list)
    stt = collections.Counter()
    dcache, dcur = {}, {}
    for pg in sorted(truepos):
        tp = truepos[pg]
        k = max(0, bisect.bisect_right(starts, tp) - 1)
        if not (starts[k] <= tp < ends[k]):
            stt['off_corpus'] += 1
            continue
        li = tp - starts[k]
        ro = rawpos[k][li]
        stt['pages'] += 1
        # !!! A HIDDEN PARAGRAPH IS NOT ON THE PAGE, SO THE RULE CANNOT GO IN IT.
        # This is the SECOND fault of the census -- 430 pages over 64 volumes drawn
        # late although the break IS at a paragraph boundary (`40Abhi12` 96,
        # `39Abhi11` 93).  The paragraph the printed page opens at is suppressed by
        # `hide/<VOL>.json` -- an Abhidhamma peyyala table line such as
        # `1. Kusalattika  2. Vipakattika` -- and its material is re-drawn as the
        # HEADING GROUP of the NEXT VISIBLE ordinal (40Abhi12 ord16/17 -> the
        # `sections/` entry on ord18).  So the page opens ABOVE that heading, and
        # offset -1 says exactly that: draw the rule before the ordinal's heading
        # group, not before its text.
        if hide.get(str(k)):
            v = k
            while v < len(paras) and hide.get(str(v)):
                v += 1
            if v >= len(paras):
                stt['hidden_at_end_of_volume'] += 1
                continue
            stt['above_heading_of_next_visible'] += 1
            out[v].append([-1, pg, truepdf[pg]])
            continue
        if li == 0:
            if paras[k].get('printed') == pg:
                stt['already_right'] += 1
                continue
            stt['boundary_wrong_number'] += 1
        else:
            stt['inside'] += 1
            if ro > 0 and (paras[k].get('text') or '')[ro - 1] not in ' \t\u00a0':
                stt['midword'] += 1
        rec = [ro, pg, truepdf[pg]]
        vm = verse.get(str(k))
        if vm and vm.get('groups') is not None:
            # THE VERSE BRANCH DRAWS THE PRINTED STREAM, NOT `pr.text`, so `ro` is
            # not an address on screen.  Locate this page's own first printed line
            # among the strings that branch actually draws, monotonically within
            # the ordinal, and carry that address as elements 3 and 4.
            stt['in_verse_paragraph'] += 1
            if k not in dcache:
                dcache[k] = drawn_index(vm)
            L, M = dcache[k]
            t = letters(trueline.get(pg, '') or '')
            q = L.find(t, dcur.get(k, 0)) if t else -1
            if q < 0 and t:
                q = L.find(t)
            if q < 0:
                stt['verse_line_not_among_drawn'] += 1
            else:
                dcur[k] = q + len(t)
                rec += [M[q][0], M[q][1]]
                stt['verse_addressed'] += 1
                if M[q][1]:
                    stt['verse_inside_a_drawn_string'] += 1
        out[k].append(rec)
    for k in out:
        out[k].sort()
    stt['written'] = sum(len(v) for v in out.values())
    stt['ords'] = len(out)
    stt['folio_overridden_by_corpus'] = over
    stt['dropped_non_monotone'] = _nonmono
    return {str(k): out[k] for k in sorted(out)}, dict(stt)


def one(vol, outdir=None):
    r = derive(vol)
    if r is None:
        print('SKIP', vol)
        return
    m, s = r
    if outdir:
        json.dump(m, open(os.path.join(outdir, vol + '.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False)
    print('%-11s pages=%5d  already-right=%5d  inside-¶=%5d  boundary-wrong-no=%4d'
          '  written=%5d on %5d ord  [above-head %d, verse %d addressed %d'
          ' (%d inside a drawn string, %d unlocated), midword %d, off-corpus %d,'
          ' non-monotone dropped %d]'
          % (vol, s.get('pages', 0), s.get('already_right', 0), s.get('inside', 0),
             s.get('boundary_wrong_number', 0), s.get('written', 0), s.get('ords', 0),
             s.get('above_heading_of_next_visible', 0), s.get('in_verse_paragraph', 0),
             s.get('verse_addressed', 0), s.get('verse_inside_a_drawn_string', 0),
             s.get('verse_line_not_among_drawn', 0),
             s.get('midword', 0), s.get('off_corpus', 0),
             s.get('dropped_non_monotone', 0)))
    return s


def main(a):
    outdir = None
    budget = 1e9
    if '--out' in a:
        i = a.index('--out'); outdir = a[i + 1]; del a[i:i + 2]
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
    if '--budget' in a:
        i = a.index('--budget'); budget = float(a[i + 1]); del a[i:i + 2]
    shard = None
    if '--shard' in a:
        i = a.index('--shard'); shard = tuple(int(x) for x in a[i + 1].split(':')); del a[i:i + 2]
    vols = ([x for x in a if not x.startswith('--')] or
            sorted(json.load(open(ROOT + '/site/reader/manifest.json',
                                  encoding='utf-8'))['volumes']))
    if shard:
        vols = [v for i, v in enumerate(vols) if i % shard[1] == shard[0]]
    t0 = time.time()
    left = 0
    for v in vols:
        if outdir and os.path.exists(os.path.join(outdir, v + '.json')):
            continue
        if time.time() - t0 > budget:
            left += 1
            continue
        try:
            one(v, outdir)
        except Exception as e:
            print('ERR', v, type(e).__name__, e)
    if left:
        print('...budget reached, %d volumes left' % left)


if __name__ == '__main__':
    main(sys.argv[1:])
