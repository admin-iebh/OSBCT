#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""How many links land on the commentary's REPRINT of the canon text, per pair.

REPLACES the 2026-08-09 measurement behind
`claude/link_targets_land_on_the_requotation.md`, which undercounts every row.
That one compared whole strings and kept the canon's inline footnote-marker
digits, so on `19Khu02 -> 27KhuA08` alone it called **168 verbatim reprints
different** and reported 500 links on a repeat where there are 907, and 267
same-numbered gloss pairs where there are 435.

THREE CORRECTIONS, each one earned on that pair:

  1. THE CANON CARRIES FOOTNOTE MARKERS INSIDE THE WORD -- `malyadhare1`,
     `Imāsāhaṁ1` -- and the commentary's reprint does not.  They are apparatus,
     not text, and they come out before anything is compared.
  2. COMPARE AGAINST THE COMMENTARY PARAGRAPH'S OPENING, not against the whole
     of it.  The commentary often reprints the verse AND appends prose
     ("... -- Ayaṁ gāthā ..."), which drags a whole-string ratio to 0.53.
  3. DECIDE BY A RELATIVE TEST WHERE ONE IS AVAILABLE.  For a canon paragraph
     numbered n, the commentary paragraphs also numbered n are the candidates,
     and the only question asked is which is LESS like the canon paragraph.
     No threshold, so no threshold to tune.

WHERE A THRESHOLD IS STILL UNAVOIDABLE, AND THIS IS SAID OUT LOUD.  When a
canon paragraph has exactly ONE candidate, there is nothing to compare it
against and the call has to be absolute: is this lone paragraph the reprint
(the edition quoted the verse and never commented on it) or is it the comment?
`SOLO` is that threshold.  Every run prints how many paragraphs sit within
+-0.15 of it, so the reader can see how much of the answer rests on it.  On
19Khu02 -> 27KhuA08 the answer was: almost none.

WHAT THIS DOES NOT DO.  It does not move anything -- `relink_requotation.py`
does that, one named pair at a time.  A high count here is not permission to
write a corpus-wide rule; the four pairs that report no gloss at all are built
differently, not defective, and need a reader's description before any number
about them means anything.

Usage:
  python3 pipeline/measure_requotation.py            # every pair with reprints
  python3 pipeline/measure_requotation.py 19Khu02 27KhuA08    # one pair, verbose
"""
import json, os, re, sys, glob, difflib, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')

SOLO = 0.60      # the absolute call, used ONLY when there is one candidate
MIN_SEP = 0.15   # below this a two-candidate set is not called here
TAIL_OK = 0.50   # a paragraph this much longer than the canon text it opens
                 # with has gone on to comment; the link is already right
MIN_LINKS = 40   # pairs smaller than this are not worth a row

_p = {}


def paras(vol):
    if vol not in _p:
        try:
            d = json.load(open(os.path.join(SITE, vol + '.json'), encoding='utf-8'))
            _p[vol] = d.get('paragraphs') or d.get('paras') or []
        except Exception:
            _p[vol] = []
    return _p[vol]


def words(s):
    s = (s or '')
    s = re.sub(r'^[\d\s.,\-–()]+', '', s)
    s = re.sub(r'\d+', '', s)
    s = re.sub(r'[^\w\s]', ' ', s, flags=re.UNICODE).lower()
    return s.split()


def opening(cw, aw):
    if not cw or not aw:
        return 0.0
    return difflib.SequenceMatcher(None, cw, aw[:len(cw)]).ratio()


def tail(cw, aw):
    """How much of the commentary paragraph is left AFTER the reprinted canon
    text, as a multiple of the canon paragraph's own length.

    !!! WITHOUT THIS THE MEASURE LIES, and it lied for a whole afternoon on
    2026-08-26.  `31KhuA12` (Therīgāthā-aṭṭhakathā) does NOT print the verse
    and the comment as two paragraphs.  It prints them as ONE:

        #8  n=4  “Tisse sikkhassu sikkhāya, ... anāsavā”ti– gāthaṁ abhāsi.
                 Tattha tisseti tassā ālapanaṁ.  Sikkhassu sikkhāyāti
                 adhisīlasikkhādikāya tividhāya sikkhāya sikkha, ...

    The paragraph OPENS with the canon verse, so `opening` scores 1.0 and the
    pair reported 514 links "landing on a reprint" — when every one of them
    already lands on the commentary, three words further into the same
    paragraph.  Nothing was there to move.  A measure that reads only the
    opening cannot tell "this is the reprint" from "this reprints and then
    comments", and those are opposite facts about a link.
    """
    if not cw or not aw:
        return 0.0
    return max(0.0, (len(aw) - len(cw)) / float(len(cw)))


def pairs():
    """(canon vol, target vol) -> [canon ordinals with a direct link]"""
    out = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(LINKS, '*.links.json'))):
        cv = os.path.basename(f).split('.')[0]
        L = json.load(open(f, encoding='utf-8'))
        for ordk, e in L.items():
            for slot in ('commentary', 'subcommentary'):
                for t in (e.get(slot) or []):
                    if t.get('state') != 'direct':
                        continue
                    k = t.get('key') or ''
                    if '#' in k:
                        out[(cv, k.split('#')[0])].append((int(ordk), int(k.split('#')[1])))
    return out


def measure(cv, tv, links, verbose=False):
    C, A = paras(cv), paras(tv)
    if not C or not A:
        return None
    by_n = collections.defaultdict(list)
    for i, p in enumerate(A):
        if p.get('n') is not None:
            by_n[p['n']].append(i)

    r = collections.Counter()
    offsets = collections.Counter()
    near = 0
    books = collections.Counter()
    for o, cur in links:
        if o >= len(C):
            continue
        p = C[o]
        books[p.get('book')] += 1
        cand = by_n.get(p.get('n')) or []
        if not cand:
            r['no candidate'] += 1
            continue
        cw = words(p.get('text'))
        # Does the paragraph the link ALREADY points at reprint the canon text
        # and then go on to comment on it, in the one paragraph?  If so there is
        # nothing wrong with the link and nothing to move.  This is the whole of
        # Therīgāthā- and Theragāthā-aṭṭhakathā's shape and most of the Jātaka's.
        if 0 <= cur < len(A):
            aw = words(A[cur].get('text'))
            if opening(cw, aw) >= SOLO and tail(cw, aw) > TAIL_OK:
                r['reprints AND comments, same paragraph'] += 1
                continue
        qs = sorted(((i, opening(cw, words(A[i].get('text')))) for i in cand),
                    key=lambda x: -x[1])
        if len(qs) == 1:
            q = qs[0][1]
            if abs(q - SOLO) <= 0.15:
                near += 1
            r['solo: reprint, no comment printed' if q >= SOLO
              else 'solo: already the comment'] += 1
            continue
        (qi, qq), (gi, gq) = qs[0], qs[1]
        if qq - gq < MIN_SEP:
            r['two candidates too close to call'] += 1
            continue
        if cur == qi:
            r['on the reprint, a comment exists'] += 1
            offsets[gi - qi] += 1
        elif cur == gi:
            r['already on the comment'] += 1
        else:
            r['on neither candidate'] += 1
    on_reprint = (r['on the reprint, a comment exists']
                  + r['solo: reprint, no comment printed'])
    return {'links': len(links), 'on_reprint': on_reprint,
            'movable': r['on the reprint, a comment exists'],
            'r': r, 'offsets': offsets, 'near_threshold': near,
            'book': books.most_common(1)[0][0] if books else None}


def main():
    want = sys.argv[1:3] if len(sys.argv) >= 3 else None
    P = pairs()
    rows = []
    for (cv, tv), links in sorted(P.items()):
        if want and (cv, tv) != tuple(want):
            continue
        if not want and len(links) < MIN_LINKS:
            continue
        m = measure(cv, tv, links)
        if not m or (not want and not m['on_reprint']):
            continue
        rows.append((cv, tv, m))

    rows.sort(key=lambda x: -x[2]['on_reprint'])
    print('%-9s %-10s %7s %11s %9s %8s  %s' %
          ('canon', 'layer', 'direct', 'on reprint', 'movable', '%', 'canon book'))
    tot_l = tot_r = tot_m = tot_near = 0
    for cv, tv, m in rows:
        print('%-9s %-10s %7d %11d %9d %7.0f%%  %s' %
              (cv, tv, m['links'], m['on_reprint'], m['movable'],
               100.0 * m['on_reprint'] / max(m['links'], 1), m['book']))
        tot_l += m['links']; tot_r += m['on_reprint']
        tot_m += m['movable']; tot_near += m['near_threshold']
    print('%-9s %-10s %7d %11d %9d' % ('TOTAL', '', tot_l, tot_r, tot_m))
    print('\nparagraphs within +-0.15 of the SOLO threshold (%.2f): %d '
          '— the part of the count that rests on it' % (SOLO, tot_near))

    if want:
        cv, tv, m = rows[0]
        print('\n%s -> %s, in full:' % (cv, tv))
        for k, v in m['r'].most_common():
            print('   %-42s %5d' % (k, v))
        if m['offsets']:
            off = m['offsets']
            print('   quote->comment offsets: %d distinct, %d..%d'
                  % (len(off), min(off), max(off)))
            print('      ' + '  '.join('%d:%d' % kv for kv in
                                       sorted(off.items())[:14]))


if __name__ == '__main__':
    main()
