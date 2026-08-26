#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Move a link off the commentary's REPRINT of the canon verse and onto the
comment — one book pair at a time, never a corpus-wide rule.

WHY.  `27KhuA08` (Vimānavatthu-aṭṭhakathā) prints, for each vimāna: the
unnumbered nidāna prose, then THE CANON'S VERSES REPRINTED IN FULL UNDER THE
CANON'S OWN NUMBERS, then the comments RESTARTING AT THE SAME NUMBERS.  Verified
on the printed page, 2026-08-26:

    p.130   333. “Vatthuttamadāyikā nārī, / Pavarā hoti naresu nārīsu. ...
                 — set as verse, inside the run 330-336, 341, 349, 357, 365
    p.133   333. Tattha **vatthuttamadāyikā**ti vatthānaṁ uttamaṁ seṭṭhaṁ, ...
                 — set as prose, bold lemmas, inside the run 333, 334, 341,
                   373, 381, 389, 397, 405

Both bear the number 333.  A placer working from the number alone takes the
first, so a reader who opens the Aṭṭhakathā band at 19Khu02 ¶333 is shown the
verse he has just finished reading, and the comment on it sits 44 paragraphs
further on with nothing pointing at it.
Full account: `claude/vimanavatthu_atthakatha_quotes_then_glosses.md`.

WHY THERE IS NO TEXT THRESHOLD, AND WHAT IS USED INSTEAD.  Every absolute text
test was tried on this book and every one of them fails, because the two classes
overlap in both directions:

  * a QUOTE may be abridged by peyyala — `258. Abhikkantena vaṇṇena -pa- ...` —
    and score 0.35 against the canon paragraph;
  * a GLOSS OPENS BY QUOTING ITS OWN LEMMA — `245. Mā tvaṁ uposathe bhāyīti
    bhadde uposathe tvaṁ mā bhāyi. Kasmā? ...` — and scores 0.36.

Position fails too: "everything after the first number-decrease is gloss" is
only 78% right, because a vimāna alternates quote-run and gloss-run more than
once (18 blocks hold two decreases, one holds seven).

So this uses NO absolute threshold.  For a canon paragraph numbered n it takes
the commentary paragraphs ALSO numbered n and asks only a RELATIVE question:
which of these is less like the canon paragraph?  That is decisive here — of the
435 canon paragraphs with two candidates, the separation between the two is at
least 0.25, and 416 of them separate by 0.5 or more.  The two closest pairs were
read by eye and both resolve the same way: the near one is a peyyala-abridged
quote, the far one the gloss.

WHAT IT WILL NOT DO.

  * It will not touch a canon paragraph with only ONE candidate.  470 of them
    have a quote and no comment — the edition does not gloss every verse, and
    that silence is the edition's, not a defect to repair.  Turning those into
    links to somewhere else would invent a commentary that was never printed.
  * It will not touch `covered` records, which are evidence and are filtered by
    the reader, not here.
  * It will not run on any pair not named in PAIRS.  How a commentary relates to
    its canon is a per-book question (the reader, 2026-08-09), and sixteen other
    pairs show the same symptom with four different shapes.

Usage:
  python3 pipeline/relink_requotation.py             # dry run, changes nothing
  python3 pipeline/relink_requotation.py --apply     # writes, then rebuild rev:
                                                     #   python3 pipeline/build_rev.py
"""
import json, os, re, sys, difflib, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')

# canon volume, the canon BOOK inside it this commentary covers, commentary vol
PAIRS = [
    ('19Khu02', 'Vimānavatthupāḷi', '27KhuA08'),
    # 2026-08-26. Petavatthu-aṭṭhakathā, the same shape, confirmed on printed
    # p.7 (`... imā gāthā abhāsi.` then `1. Tattha khettūpamāti ...`) and p.161.
    # It MIXES shapes, which 27KhuA08 did not: 101 of its links already land on
    # a paragraph that reprints the verse and then comments in the same
    # paragraph. Those are correct as they stand and are skipped, not moved —
    # see the TAIL_OK guard below and `pipeline/measure_requotation.py:tail`.
    ('19Khu02', 'Petavatthupāḷi', '28KhuA09'),
]

# A pair closer than this is not decided here.  Nothing in this book reaches it
# — the closest is 0.30 — so it exists to stop a future book being decided by a
# coin toss without anyone noticing.
TAIL_OK = 0.50   # a paragraph this much longer than the canon text it opens
                 # with has gone on to comment; the link is already right

MIN_SEP = 0.15


def paras(vol):
    d = json.load(open(os.path.join(SITE, vol + '.json'), encoding='utf-8'))
    return d.get('paragraphs') or d.get('paras') or []


def words(s):
    """The canon carries footnote-marker digits INSIDE the word — `malyadhare1`,
    `Imāsāhaṁ1` — and the commentary's reprint does not.  A comparison that
    keeps them calls 168 verbatim reprints different.  They are apparatus, not
    text, so they come out."""
    s = (s or '')
    s = re.sub(r'^[\d\s.,\-–()]+', '', s)      # the leading paragraph number
    s = re.sub(r'\d+', '', s)                   # inline footnote markers
    s = re.sub(r'[^\w\s]', ' ', s, flags=re.UNICODE).lower()
    return s.split()


def opening(cw, aw):
    """How much of the commentary paragraph's OPENING is the canon paragraph.
    Compared against the opening and not the whole, because the commentary
    often reprints the verse AND appends prose to it ("... — Ayaṁ gāthā ...")."""
    if not cw or not aw:
        return 0.0
    return difflib.SequenceMatcher(None, cw, aw[:len(cw)]).ratio()


def tail(cw, aw):
    """How much of the paragraph is left after the canon text it opens with,
    as a multiple of the canon paragraph's own length.

    !!! THIS GUARD IS WHY 28KhuA09 DID NOT LOSE 101 CORRECT LINKS.  Some
    commentaries print the verse and the comment as ONE paragraph:

        “Tisse sikkhassu sikkhāya, ... anāsavā”ti– gāthaṁ abhāsi.
        Tattha tisseti tassā ālapanaṁ.  Sikkhassu sikkhāyāti ...

    Such a paragraph OPENS with the canon text, so `opening` scores 1.0 and it
    looks exactly like a bare reprint — but the link already lands on the
    commentary and moving it would be a defect, not a repair.  27KhuA08 is pure
    shape A so this never arose there; 28KhuA09 mixes the two and 101 of its
    links are of this kind.  Whole volumes are built this way — see
    `claude/link_targets_land_on_the_requotation.md` §1.
    """
    if not cw or not aw:
        return 0.0
    return max(0.0, (len(aw) - len(cw)) / float(len(cw)))


def plan(cvol, book, avol):
    C, A = paras(cvol), paras(avol)
    L = json.load(open(os.path.join(LINKS, cvol + '.links.json'), encoding='utf-8'))
    by_n = collections.defaultdict(list)
    for i, p in enumerate(A):
        if p.get('n') is not None:
            by_n[p['n']].append(i)

    moves, tally, close = {}, collections.Counter(), []
    for o, p in enumerate(C):
        # !!! `book` IS UNSET ON THE VOLUME'S OPENING PARAGRAPHS.  In 19Khu02 it
        # is None for ords 0-3 — Pīṭhavagga, the first vagga of Vimānavatthu,
        # and the only four None in the volume.  Filtering on the name alone
        # silently dropped ¶1, which is one of the two cases check_links.py
        # asserts, so the gate would have stayed red with no move recorded and
        # nothing saying why.  A NAMED book still excludes: 19Khu02 ¶199 of
        # Petavatthupāḷi carries a link into 27KhuA08#313, which is a stray
        # across books and a separate question — it is not touched here.
        if p.get('book') not in (book, None):
            continue
        e = L.get(str(o)) or {}
        direct = [t for t in (e.get('commentary') or [])
                  if t.get('state') == 'direct'
                  and (t.get('key') or '').startswith(avol + '#')]
        cand = by_n.get(p.get('n')) or []
        if not cand:
            tally['number absent from the commentary'] += 1
            continue
        if not direct:
            tally['no direct link to move'] += 1
            continue
        cw = words(p.get('text'))
        cur0 = int((direct[0].get('key') or '').split('#')[1])
        if 0 <= cur0 < len(A):
            aw = words(A[cur0].get('text'))
            if opening(cw, aw) >= 0.60 and tail(cw, aw) > TAIL_OK:
                tally['reprints AND comments in one paragraph — correct as is'] += 1
                continue
        qs = sorted(((i, opening(cw, words(A[i].get('text')))) for i in cand),
                    key=lambda x: -x[1])
        if len(qs) == 1:
            tally['one candidate: %s' %
                  ('the quote, no comment printed' if qs[0][1] >= 0.60
                   else 'already the comment')] += 1
            continue
        if len(qs) > 2:
            tally['more than two candidates — NOT DECIDED HERE'] += 1
            continue
        (qi, qq), (gi, gq) = qs[0], qs[1]
        if qq - gq < MIN_SEP:
            # !!! BOTH CANDIDATES OPEN WITH THE VERSE.  That happens when the
            # comment RE-QUOTES before commenting — 28KhuA09 #735 is
            # `486. “Tassa kammassa kusalassa ... khāditun”ti. Tattha paṭihatāti
            # paṭihatacittā ...` against the bare #729.  `opening` cannot
            # separate them because both openings ARE the verse; `tail` can,
            # and it is the same distinction the TAIL_OK guard above makes:
            # 13 words against 41.  Break the tie on it, and only when exactly
            # one of the two continues past the verse.
            long0 = tail(cw, words(A[qs[0][0]].get('text'))) > TAIL_OK
            long1 = tail(cw, words(A[qs[1][0]].get('text'))) > TAIL_OK
            if long0 == long1:
                # both bare, or both continue: nothing here can tell them apart
                close.append((o, p.get('n'), qs))
                tally['two candidates too close to call — NOT MOVED'] += 1
                continue
            # the one that continues past the verse is the comment
            gi = qs[1][0] if long1 else qs[0][0]
            qi = qs[0][0] if long1 else qs[1][0]
            tally['tie on opening, broken by the tail'] += 1
        cur = int((direct[0].get('key') or '').split('#')[1])
        if cur == qi:
            moves[o] = (qi, gi, round(qq, 3), round(gq, 3))
            tally['MOVE quote -> comment'] += 1
        elif cur == gi:
            tally['already on the comment'] += 1
        else:
            tally['direct link on neither candidate — left alone'] += 1
    return C, A, L, moves, tally, close


def main():
    apply_ = '--apply' in sys.argv
    total = 0
    for cvol, book, avol in PAIRS:
        C, A, L, moves, tally, close = plan(cvol, book, avol)
        print('%s (%s) -> %s' % (cvol, book, avol))
        for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
            print('   %-46s %5d' % (k, v))
        for o, n, qs in close:
            print('   TOO CLOSE, read it: canon ord %d (n=%s) %s' % (o, n, qs))
        if moves:
            some = sorted(moves.items())[:3]
            print('   e.g. ' + '; '.join(
                '%s#%d -> %s#%d (was %s#%d)' % (cvol, o, avol, g, avol, q)
                for o, (q, g, _, _) in some))
        if apply_:
            for o, (qi, gi, qq, gq) in moves.items():
                for t in (L[str(o)].get('commentary') or []):
                    if (t.get('state') == 'direct'
                            and t.get('key') == '%s#%d' % (avol, qi)):
                        t['key'] = '%s#%d' % (avol, gi)
                        # provenance: the record must say how it got here
                        t['by'] = 'requotation'
                        t['was'] = '%s#%d' % (avol, qi)
            f = os.path.join(LINKS, cvol + '.links.json')
            # !!! DEFAULT SEPARATORS ON PURPOSE.  The link maps are written one
            # volume to a line with `", "` between items, and a compact dump
            # rewrites every byte of a one-line file — `git diff` then reports
            # "1 insertion, 1 deletion" for 437 moves and nobody can read it.
            # The formatting is what makes the change reviewable.
            json.dump(L, open(f, 'w', encoding='utf-8'), ensure_ascii=False)
            print('   written: %s' % f)
        total += len(moves)
    if apply_:
        print('\n%d links moved.  NOW REBUILD THE REVERSE MAPS, or the band '
              'side still answers with the old target:\n'
              '    python3 pipeline/build_rev.py' % total)
    else:
        print('\ndry run — nothing written.  %d links would move.' % total)


if __name__ == '__main__':
    main()
