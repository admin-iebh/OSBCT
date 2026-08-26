#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Does a cross-layer link point at the paragraph it says it points at?

WHY THIS EXISTS.  User-reported 2026-08-02: clicking **A** on the Aratisutta
landed on Pacchāsamaṇasuttavaṇṇanā and the title went blank.  The link record
read

    {"key": "19AnA03#86", "state": "covered", "n": 113}

and `19AnA03#86` is paragraph **112**.  THE RECORD CONTRADICTED ITS OWN TARGET,
and nothing in this repository looked.  That invariant is free -- both halves are
already in the files -- and it would have caught the fault on the day it was
introduced.  The lesson is the project's own: an assertion nobody wrote is
indistinguishable from one that passes.

WHY IT IS A RATCHET AND NOT A THRESHOLD.  The paragraph number is NOT a key:
only 28 of 118 volumes carry a non-decreasing series, 90 restart, and `21Khu04`
holds 4,347 duplicate numbers among 4,858 numbered paragraphs.  Some layers
genuinely do not correspond paragraph-for-paragraph, so a perfect score is not
available and demanding one would mean either a permanently red gate or a
threshold picked to be green, which measures nothing.  So this records the
CURRENT numbers and fails when they get WORSE.  A repair must move them up; a
regression cannot hide in an aggregate.

THREE MEASURES, because one can be gamed by dropping links:

  n-match      of the targets carrying a paragraph number, the share landing on
               a paragraph with that number (or on a range paragraph covering
               it -- the edition prints `111-114.` and means it)
  name-match   of the canon->layer links where BOTH sides name a sutta, the
               share whose names share a stem.  This is the one a reader feels:
               it is exactly "did the sutta keep its name"
  reachable    distinct layer paragraphs any link reaches.  Without this, a
               map could raise both rates by deleting every hard case

Usage:
  python3 pipeline/check_links.py                 # measure and compare
  python3 pipeline/check_links.py --record        # accept current as baseline
  python3 pipeline/check_links.py --negative-control
Exit 0 = no measure regressed.
"""
import json, os, re, sys, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'links_baseline.json')
TOL = 0.001          # a tenth of a percentage point of float noise

# !!! THE RANGE READER LIVES IN ONE PLACE NOW.  This file used the naive
# `(\d+)-(\d+)` form, so `234-5.` read as the empty range and a link correctly
# pointing at it for n=235 was counted a MISS.  576 of the corpus's 2,572 leading
# ranges are abbreviated (22.4%), so `n_match` -- the rate this ratchet exists to
# defend -- was understated.  Reader, 2026-08-07: the rule holds "for all books".
from printed_range import expand_range
LEAD = re.compile(r'^[\d\s.,\-–()]+')
TAIL = re.compile(r'(vaṇṇanā|vaṇṇanaṁ|vaṇṇana)$')
KIND = re.compile(r'(suttanta|sutta|vagga|nipāta|pāḷi|kathā|desanā|dvaya|ṁ)+$')

_pc, _sn = {}, {}


def P(v):
    if v not in _pc:
        try:
            d = json.load(open(os.path.join(SITE, v + '.json'), encoding='utf-8'))
            _pc[v] = d.get('paragraphs') or d.get('paras') or []
        except Exception:
            _pc[v] = []
    return _pc[v]


def stem(s):
    s = (s or '').strip().lower()
    s = LEAD.sub('', s)
    s = re.sub(r'[^a-zāīūṁṃṅñṭḍṇḷ]', '', s)
    prev = None
    while prev != s:
        prev = s
        s = TAIL.sub('', s)
        s = KIND.sub('', s)
    return s


def name_at(v, i):
    """The section name covering ordinal i: the `sutta` field marks where a
    section opens, so it is carried forward -- BUT NEVER ACROSS A BOOK.

    !!! IT USED TO CARRY ACROSS, AND THAT IS A REAL DEFECT IN THE CORPUS THAT
    THIS MEASURE WAS SPREADING.  A book's opening paragraphs often carry no
    `sutta` field at all: in `19Khu02` the Petavatthu starts at ord 1034 and the
    first `sutta` in it is at ord 1374, so **340 paragraphs of Petavatthu were
    being called by a Vimānavatthu section name** -- ord 1371 answered
    `Rasuttamadāyikāvimānavatthu (4)`.  Corpus-wide that is **5,616 paragraphs
    in 44 volumes** (worst: 19Khu02 678, 01Vin01 399, 28KhuA09 397).

    Found 2026-08-26 because the 28KhuA09 link repair moved one such link onto a
    target that DOES have a name, which made the pair checkable for the first
    time and dropped name-match by 0.004.  The link was right; the name was
    wrong.  Answering None here is honest -- the pair is simply not counted --
    where answering the previous book's name is a false agreement or a false
    disagreement depending on which way it falls.

    THE UNDERLYING DEFECT IS NOT FIXED, only stopped from being measured: the
    corpus still has 5,616 paragraphs with no section of their own, and the
    reader still shows them that way.  That belongs to the nav/section builders.
    """
    if v not in _sn:
        out, cur, st, book = [], None, 0, object()
        ps = P(v)
        for j, p in enumerate(ps):
            if p.get('book') != book:
                if cur is not None:
                    out.append((st, j - 1, cur))
                cur, book = None, p.get('book')
            if p.get('sutta'):
                if cur is not None:
                    out.append((st, j - 1, cur))
                cur, st = p['sutta'], j
        if cur is not None:
            out.append((st, len(ps) - 1, cur))
        _sn[v] = out
    for a, b, nm in _sn[v]:
        if a <= i <= b:
            return nm
    return None


def measure(load=None):
    """`load` lets the negative control feed a perturbed map in memory."""
    nok = nbad = agree = dis = 0
    reach = set()
    worst = collections.Counter()
    for f in sorted(glob.glob(os.path.join(LINKS, '*.links.json'))):
        src = os.path.basename(f).split('.')[0]
        cps = P(src)
        if not cps:
            continue
        L = (load(f) if load else
             json.load(open(f, encoding='utf-8')))
        for ordk, e in L.items():
            i = int(ordk)
            if i >= len(cps):
                continue
            cn = name_at(src, i)
            for kind in ('commentary', 'subcommentary'):
                for t in (e.get(kind) or []):
                    key = t.get('key') or ''
                    if '#' not in key:
                        continue
                    v, o = key.rsplit('#', 1)
                    ps = P(v)
                    if not ps or int(o) >= len(ps):
                        continue
                    q = ps[int(o)]
                    reach.add(key)
                    n = t.get('n')
                    if n is not None:
                        r = expand_range(q.get('text') or '')
                        if q.get('n') == n or (r and r[0] <= n <= r[1]):
                            nok += 1
                        else:
                            nbad += 1
                            worst[src] += 1
                    tn = name_at(v, int(o))
                    if cn and tn:
                        a, b = stem(cn), stem(tn)
                        if a and b and (a == b or a in b or b in a):
                            agree += 1
                        else:
                            dis += 1
    return {'n_match': round(100.0 * nok / max(nok + nbad, 1), 3),
            'name_match': round(100.0 * agree / max(agree + dis, 1), 3),
            'reachable': len(reach),
            'n_checked': nok + nbad, 'name_checked': agree + dis}, worst


# ---------------------------------------------------------------------------
# THE RE-QUOTATION CASES.  Added 2026-08-26.
#
# WHY.  `27KhuA08` (Vimānavatthu-aṭṭhakathā) prints, for each vimāna: unnumbered
# nidāna prose, then the canon's verses REPRINTED IN FULL UNDER THE CANON'S OWN
# NUMBERS, then the comments RESTARTING AT THE SAME NUMBERS.  Both bear the same
# number, so a placer working from the number alone takes the first one -- the
# quote -- every time.  A reader who opens the Aṭṭhakathā band at 19Khu02 ¶333
# is shown the verse he has just finished reading, set as prose, while the
# comment on it sits 44 paragraphs further on with nothing pointing at it.
# Full account: claude/vimanavatthu_atthakatha_quotes_then_glosses.md.
#
# WHY NAMED CASES AND NOT A MEASURE.  There is no text test that separates quote
# from gloss in this book, and it is worth saying exactly why, because the
# obvious ones were tried and all of them fail:
#
#   * whole-string similarity          -- fails: the commentary often reprints
#                                         the verse AND appends prose to it
#                                         ("... -- Ayaṁ gāthā ..."), so a real
#                                         quote scores 0.53
#   * prefix containment               -- fails: canon and commentary disagree
#                                         on single words (padmaṁ/paddhaṁ,
#                                         Upapajjati/Uppajjati), so a real quote
#                                         breaks off at 50% coverage
#   * opening similarity               -- fails BOTH WAYS: a quote may be
#                                         abridged by peyyala (`-pa-`) and score
#                                         0.35, and A GLOSS OPENS BY QUOTING ITS
#                                         OWN LEMMA -- "Mā tvaṁ uposathe bhāyīti
#                                         bhadde ..." -- and scores 0.36 too.
#
# The distributions overlap; there is no threshold. So these are cases READ off
# the printed page and named, one at a time, exactly as the reader said this
# work has to go: one book at a time, and within the book, by eye. Each entry
# records the canon paragraph, the target it must NOT keep (the reprint), and
# the paragraph the comment actually is.
REQUOTE_CASES = [
    # canon vol, canon ord, printed n, forbidden target, the gloss
    #
    # 27KhuA08 Vimānavatthu-aṭṭhakathā — repaired 2026-08-26.
    # p.130 has ¶333 as verse in the run 330-336; p.133 restarts at
    # `333. Tattha vatthuttamadāyikāti ...`.
    ('19Khu02', 317, 333, '27KhuA08#467', '27KhuA08#511'),
    ('19Khu02',   0,   1, '27KhuA08#4',   '27KhuA08#11'),
    #
    # 28KhuA09 Petavatthu-aṭṭhakathā — same shape, repaired 2026-08-26.
    # p.7 ends the verse run at ¶3 with `imā gāthā abhāsi.` and restarts
    # `1. Tattha khettūpamāti ...`; p.161 has `397. Akammakāmāti sādhūhi ...`.
    ('19Khu02', 1034,   1, '28KhuA09#4',   '28KhuA09#7'),
    ('19Khu02', 1430, 397, '28KhuA09#579', '28KhuA09#595'),
]


def requote(load=None):
    """Named cases where a link is known to land on the commentary's reprint of
    the canon verse instead of on the comment.  Hard assertions, not a ratchet:
    each one was read, and a repair either moves it or it did not happen."""
    out = []
    for vol, ordn, n, forbidden, gloss in REQUOTE_CASES:
        f = os.path.join(LINKS, vol + '.links.json')
        if not os.path.exists(f):
            out.append((vol, ordn, n, forbidden, gloss, None, 'no link file'))
            continue
        L = (load(f) if load else json.load(open(f, encoding='utf-8')))
        e = L.get(str(ordn)) or {}
        tvol = forbidden.split('#')[0]
        got = [t.get('key') for t in (e.get('commentary') or [])
               if t.get('state') == 'direct'
               and (t.get('key') or '').startswith(tvol + '#')]
        cur = got[0] if got else None
        if cur == forbidden:
            out.append((vol, ordn, n, forbidden, gloss, cur, 'lands on the reprint'))
        elif cur is None:
            out.append((vol, ordn, n, forbidden, gloss, cur, 'no direct link at all'))
        else:
            out.append((vol, ordn, n, forbidden, gloss, cur, 'ok'))
    return out


def report_requote(cases):
    print('\n  re-quotation cases (the commentary reprints before it comments):')
    fails = []
    for vol, ordn, n, forbidden, gloss, cur, why in cases:
        if why == 'ok':
            print('  ok    %s#%d (¶%d) -> %s' % (vol, ordn, n, cur))
        else:
            print('  FAIL  %s#%d (¶%d) -> %s : %s'
                  % (vol, ordn, n, cur, why))
            print('        that paragraph is the canon verse reprinted; '
                  'the comment is %s' % gloss)
            fails.append('%s#%d (¶%d) still lands on the reprint %s, not on %s'
                         % (vol, ordn, n, forbidden, gloss))
    return fails


def report(m, worst, base):
    print('  n-match     %7.2f%%  of %d numbered targets' % (m['n_match'], m['n_checked']))
    print('  name-match  %7.2f%%  of %d links naming a sutta on both sides'
          % (m['name_match'], m['name_checked']))
    print('  reachable   %7d    distinct layer paragraphs' % m['reachable'])
    fails = []
    if base:
        for k, label in (('n_match', 'n-match'), ('name_match', 'name-match'),
                         ('reachable', 'reachable paragraphs')):
            if m[k] < base[k] - (TOL if k != 'reachable' else 0):
                fails.append('%s fell from %s to %s' % (label, base[k], m[k]))
        print('  baseline    n-match %s%%  name-match %s%%  reachable %d'
              % (base['n_match'], base['name_match'], base['reachable']))
    else:
        print('  (no baseline recorded — run with --record)')
    if worst:
        print('  worst sources by wrong-number targets: %s'
              % ', '.join('%s %d' % kv for kv in worst.most_common(6)))
    return fails


if __name__ == '__main__':
    base = (json.load(open(BASE, encoding='utf-8'))
            if os.path.exists(BASE) else None)

    if '--negative-control' in sys.argv:
        # !!! A CHECK THAT CANNOT FAIL IS A COMMENT.  Shift every ordinal by one
        # in memory -- the shape of the reported fault, an off-by-one into the
        # neighbouring paragraph -- and require every measure to notice.
        def shifted(f):
            L = json.load(open(f, encoding='utf-8'))
            for e in L.values():
                for kind in ('commentary', 'subcommentary'):
                    for t in (e.get(kind) or []):
                        k = t.get('key') or ''
                        if '#' in k:
                            v, o = k.rsplit('#', 1)
                            t['key'] = '%s#%d' % (v, int(o) + 1)
            return L
        m, w = measure(load=shifted)
        print('--- negative control: every ordinal shifted by one ---')
        f = report(m, w, base)
        if not f:
            print('\nCONTROL IS BROKEN: shifting every link by one paragraph '
                  'did not move a single measure')
            sys.exit(1)
        print('\ncontrol fired: %s' % '; '.join(f))
        sys.exit(0)

    m, w = measure()
    print('cross-layer links, %s' % LINKS)
    fails = report(m, w, base)
    # !!! THE NAMED CASES ARE NOT PART OF THE BASELINE and must not be, or
    # `--record` would accept the defect as the standard.  They are assertions.
    rq = requote()
    fails = fails + report_requote(rq)
    if '--record' in sys.argv:
        json.dump(m, open(BASE, 'w', encoding='utf-8'), indent=1)
        print('\nbaseline recorded (the three measures only — '
              'the re-quotation cases are assertions and are never recorded)')
        sys.exit(0)
    if fails:
        print('\nLINKS REGRESSED:')
        for x in fails:
            print('  - %s' % x)
        sys.exit(1)
    print('\nno measure regressed')
