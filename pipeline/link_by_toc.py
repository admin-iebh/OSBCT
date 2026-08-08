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
import ordinal_words as _OW                                  # noqa: E402
from ordinal_vagga import read_vaggas                         # noqa: E402

# apadāna position within a vagga: `Dutiyattherāpadāne`, `Tatiyāpadāne`,
# `Sattamaṭṭhamanavamāni`.  Stems, because the edition compounds them.
APOS = {w[:-1] + 'a': v for w, v in _OW.LOC.items() if v <= 12}
# !!! THE STEM'S FINAL VOWEL LENGTHENS AT THE JOIN.  `tatiya` + `apadāne` is
# printed `tatiyāpadāne`, one long vowel, so a literal `tatiya` never matches
# exactly the form that names an apadāna without a thera word in between.  The
# final -a is therefore written `[aā]`, which is the same sandhi that `vaggādi`
# showed in `fix_vagga_heads.py`.  Third time this has cost a fix in one day.
_APOS_RE = re.compile('(' + '|'.join(
    (re.escape(x[:-1]) + '[aā]') if x.endswith('a') else re.escape(x)
    for x in sorted(APOS, key=len, reverse=True)) + ')')
# the marker that says the ordinal is naming an APADĀNA, not something else
APMARK = re.compile(r'(apadān|therāpadān|ttherassa|tthera|āpadān)')


def apadana_positions(text):
    """Which apadāna(s) of the vagga a commentary paragraph says it is about.

    The edition states it in words, with or without a number beside it:

        Vīsatime vagge PAṬHAMAtherāpadānaṁ uttānameva.      -> [1]
        6. DUTIYAttherāpadāne yaṁ dāyavāsiko isīti ...      -> [2]
        TATIYAttherassa apadāne Khaṇḍaphulliyattheroti ...  -> [3]
        ... Chaṭṭhaṁ. SATTAMAAṬṬHAMANAVAMĀNI uttānatthāneva -> [7, 8, 9]

    !!! THE UNNUMBERED ONES ARE COMMENTARY, NOT GAPS.  `33KhuA14` ord 498 has no
    paragraph number at all and is a full gloss of Khaṇḍapulliya; reading only
    numbers would have thrown it away and then reported the canon paragraphs it
    glosses as uncommented.  Reader, 2026-08-07: "unnumbered paragraphs have to
    be included by matching the names of the vaggas in this case."

    Only the OPENING is read, and only when an apadāna marker stands with the
    ordinal -- `Chaṭṭhe nagare Dvāravatiyā` names the sixth apadāna, but a
    `chaṭṭha-` deep inside a gloss is somebody's name.
    """
    head = letters(LEAD.sub('', (text or '')[:90]))
    if not APMARK.search(head):
        return []
    out = []
    for m in _APOS_RE.finditer(head):
        v = APOS.get(m.group(1)) or APOS.get(m.group(1)[:-1] + 'a')
        if not v:
            continue
        # !!! THE ORDINAL MUST SIT AGAINST THE APADĀNA MARKER, NOT MERELY IN A
        # PARAGRAPH THAT MENTIONS ONE.  `33KhuA14` ord 280 (p. 110) opens
        # `Pabbate Himavantamhīti-ādikaṁ āyasmato DUTIYARaṁsisaññakattherassa
        # apadānaṁ` -- `Dutiya-` there is part of the elder's NAME, telling two
        # theras called Raṁsisaññaka apart, and has nothing to do with position.
        # Read loosely it placed canon 15 on the second apadāna's commentary and
        # crossed two links, which assertion 7 caught.
        #
        # In every true case the ordinal runs straight into the marker --
        # `dutiyaTTHERāpadāne`, `tatiyaTTHERassa apadāne`, `tatiyĀPADĀNe` -- with
        # at most the one vowel that sandhi merges at the join.
        tail = head[m.end():m.end() + 6]   # 'tther' is five
        if not re.match(r'^(t*her|[aā]?padān|[aā]?pad)', tail):
            continue
        if v not in out:
            out.append(v)
    return sorted(out)


def place(src, tgt, vagga=None):
    """canon ordinal -> (target ordinal, n, canon section, target section,
    gloss hits, bold count).

    THE ORDER, AND EVERY STEP IS THE EDITION SPEAKING:

      1  VAGGA REGION.  Bounded by the commentary's vagga heads, paired to the
         canon vagga by NAME.  A head may cover SEVERAL canon vaggas -- `21-23.`
         and `34.`+ādi -- and the words in its text say which.
      2  NUMBER, inside that region only.  Unique there, so it is the address.
      3  ORDINAL WORD, for commentary paragraphs carrying no number.
      4  Whatever the region does not account for is NOT COMMENTED.

    Section pairing is no longer a gate on any of this.  It was, and vagga 40
    showed the cost: 519 canon paragraphs, 2 linked and 456 falling out with no
    link AND no verdict, because their sections did not pair.  Sections now only
    label the result and feed the gloss check.
    """
    C, A = paras(src), paras(tgt)
    vs = vaggas(src)
    if vagga is not None:
        lo, hi = vagga if isinstance(vagga, tuple) else (vagga, vagga)
        vs = [x for x in vs if tocnum(x[2]) and lo <= tocnum(x[2])[0] <= hi]
        if not vs:
            raise SystemExit('no vagga %s-%s in %s' % (lo, hi, src))
    avs = vaggas(tgt) or [(0, len(A) - 1, '')]
    # commentary vagga head -> the canon vagga numbers it covers
    cover = {}
    for i, (a0, a1, l) in enumerate(avs):
        m = re.match(r'^\s*(\d+)\s*[-–]\s*(\d+)\s*\.', l or '')
        if m:                                   # `21-23.` says so outright
            nums = list(range(int(m.group(1)), int(m.group(2)) + 1))
        else:
            n0 = tocnum(l)[0] if tocnum(l) else None
            said = read_vaggas((A[a0].get('text') or '')[:400])
            # !!! `ādi` DOES NOT SAY WHERE IT STOPS -- the words do.  `34.
            # Gandhodakavaggādivaṇṇanā` names 34-38 and then treats the 39th
            # separately and only to its eighth apadāna.  Taking the span from
            # the next head's number would have claimed 34-39 entire.
            nums = said if (said and n0 in said) else ([n0] if n0 else [])
        for x in nums:
            cover.setdefault(x, (a0, a1, l))
    out, gaps, notes, unpaired, unsure = {}, [], [], [], []
    for (ca, cb, clbl) in vs:
        cvn, cvs = tocnum(clbl), stem(clbl)
        av = [x for x in avs if stem(x[2]) == cvs and len(cvs) >= 4]
        how = 'name'
        if not av and cvn and cvn[0] in cover:
            av, how = [cover[cvn[0]]], 'declared'
        if not av:
            av = [x for x in avs if tocnum(x[2]) == cvn]
            how = 'number'
        if not av and len(avs) == 1:
            av, how = [avs[0]], 'sole'
        if not av:
            notes.append(('NO VAGGA', clbl, 'not in %s' % tgt))
            continue
        if len(av) > 1:
            notes.append(('VAGGA AMBIGUOUS', clbl, '%d candidates' % len(av)))
            continue
        aa, ab, albl = av[0]
        if how == 'name' and tocnum(albl) != cvn:
            notes.append(('VAGGA NUMBER DIFFERS', clbl,
                          '%s prints %s' % (tgt, albl)))
        # canon apadāna sections of this vagga, in order, with their n-spans
        csec = sections_in(src, ca, cb)
        spans = []
        for a0, a1, l in csec:
            ns = [C[t]['n'] for t in range(a0, a1 + 1) if C[t].get('n') is not None]
            spans.append((set(ns), l))
        # 2. the numbers the region carries, and 3. the ones it names in words
        avail = numbers_in(tgt, aa, ab)
        for j in range(aa, min(ab, len(A) - 1) + 1):
            if A[j].get('n') is not None or expand_range(A[j].get('text') or ''):
                continue
            for pos in apadana_positions(A[j].get('text') or ''):
                if pos <= len(spans):
                    for n in spans[pos - 1][0]:
                        avail.setdefault(n, j)
        secname = {}
        for a0, a1, l in sections_in(tgt, aa, ab):
            for t in range(a0, a1 + 1):
                secname[t] = l
        cname = {}
        for a0, a1, l in csec:
            for t in range(a0, a1 + 1):
                cname[t] = l
        # !!! A NUMBER CAN OCCUR TWICE IN A REGION, AND ONE OF THEM IS A
        # MISPRINT.  `32KhuA13` ord 321 (p. 305) carries `442.` while sitting
        # inside `3-4. Anuruddhatthera-apadānavaṇṇanā`, whose numbers otherwise
        # run 421, 430, 431 -- a `422` printed as `442`.  The real 442 is at ord
        # 330 (p. 309) and glosses `ajjhāyako`, which is canon 442 word for
        # word.  Taking the first occurrence took the misprint and sent canon
        # 442 four printed pages backwards into the wrong thera's apadāna.
        #
        # THE COMMENTARY FOLLOWS ITS CANON IN ORDER, so the resolution is to
        # walk forward: among the paragraphs carrying this number, take the
        # earliest that does not go BACKWARDS from the one already placed.  That
        # is the same fact assertion 7 of `check_toc_links.py` tests, applied
        # while placing instead of afterwards -- and it was assertion 7 that
        # found this, on a volume that had already been applied and passed.
        #
        # The duplicate is REPORTED as a suspected erratum, never corrected:
        # working principle 3.  Which of the two is the misprint is a question
        # about the printed page and is not settled here.
        allpos = collections.defaultdict(list)
        for t in range(aa, min(ab, len(A) - 1) + 1):
            for x in numbers_in(tgt, t, t):
                allpos[x].append(t)
            # !!! AND THE UNNUMBERED PARAGRAPHS, WHICH ARE COMMENTARY TOO.
            # Rebuilding the candidate map from `numbers_in` alone silently
            # dropped every paragraph placed by its ORDINAL WORD -- the count
            # fell from 688 links to 448 and nothing failed, because the lost
            # ones simply became `not_commented`, which is a claim rather than
            # an error.  A refactor that turns links into assertions of silence
            # is the most dangerous shape of change in this file.
            if A[t].get('n') is None and not expand_range(A[t].get('text') or ''):
                for pos in apadana_positions(A[t].get('text') or ''):
                    if pos <= len(spans):
                        for x in spans[pos - 1][0]:
                            allpos[x].append(t)
        for x in allpos:
            allpos[x] = sorted(set(allpos[x]))
        bynum = set()
        for t in range(aa, min(ab, len(A) - 1) + 1):
            bynum |= set(numbers_in(tgt, t, t))
        for x, ts in sorted(allpos.items()):
            if len(ts) > 1:
                notes.append(('DUPLICATE NUMBER', '%s n=%d' % (tgt, x),
                              'ords %s, printed pp. %s -- suspected erratum'
                              % (ts, [A[t].get('printed') for t in ts])))
        floor = aa
        for j in range(ca, cb + 1):
            n = C[j].get('n')
            if n is None:
                continue
            cand = [t for t in allpos.get(n, []) if t >= floor] or \
                allpos.get(n, [])
            o = cand[0] if cand else None
            if o is None:
                gaps.append((j, n, cname.get(j, clbl), albl))
                continue
            floor = o
            lem = lemmas(tgt, o)
            ct = nfold(C[j].get('text') or '')
            hit = sorted(w for w in lem if w in ct)
            # !!! THE RECORD SAYS HOW IT WAS PLACED, because the gate must
            # check the claim that was actually made.  A number placement
            # asserts the target carries that number; an ordinal-word placement
            # asserts the target NAMES that apadāna, and its target is normally
            # unnumbered.  Judging the second by the first failed 180 of vagga
            # 40's 184 links -- a gate red on correct data, which is how gates
            # get switched off.
            how = 'num' if (A[o].get('n') == n or
                            (expand_range(A[o].get('text') or '') or (0, -1))[0]
                            <= n <=
                            (expand_range(A[o].get('text') or '') or (0, -1))[1]
                            ) else 'ord'
            out[j] = (o, n, cname.get(j, clbl), secname.get(o, albl), hit,
                      len(lem), how)
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

    for j, (o, n, cl, al, hit, nl, how) in got.items():
        e = L.setdefault(str(j), {})
        key = '%s#%d' % (tgt, o)
        old, keep = strip_ineligible(e)
        removed += len(old) - len(keep)
        # !!! FIRST, NOT LAST.  `jumpFrom` in reader2.html takes arr[0] of the
        # direct targets, so a stale record in front of this one would send the
        # chip there instead.
        rec = {'key': key, 'state': 'direct', 'n': n, 'by': 'toc-' + how}
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
        spec = argv[k + 1]
        vg = tuple(int(x) for x in spec.split('-')) if '-' in spec else int(spec)
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
          % (src, tgt,
             ('  vagga %s' % ('%d-%d' % vg if isinstance(vg, tuple) else vg))
             if vg else '', dest))
    for x in notes:
        print('  %-12s %-46s %s' % x)
    for a0, b0, l in unpaired:
        print('  %-12s %-46s ord %d-%d' % ('NO PAIR', l, a0, b0))
    print()
    conf = sum(1 for v in got.values() if v[4])
    withb = sum(1 for v in got.values() if v[5])
    bynum = sum(1 for v in got.values() if v[6] == 'num')
    print('  placed              %5d   (%d by number, %d by ordinal word)'
          % (len(got), bynum, len(got) - bynum))
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
