#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The edition's leading paragraph RANGE, read the way the edition writes it.

READER, 2026-08-07: "You are right when you say `234-5.` means 234-235,
`415-20.` means 415-420.  You should remember this for all books.  This is
important."  Hence this module: one implementation, imported everywhere, so that
"for all books" is enforced by the code and not by anybody's memory.

THE RULE.  A paragraph may open with a printed range covering several units:

    278-281.  Disvā me -pa- pucchituṁ amataṁ padanti uttānatthameva.
    234-5.    Tassa Anomadassissa Bhagavato Munino ...
    415-20.   Tadaḍḍhakaṁ tato aḍḍhakaṁ ...

THE UPPER BOUND IS ABBREVIATED WHENEVER ITS LEADING DIGITS REPEAT THE LOWER
BOUND'S.  `234-5.` is 234-235, not "234 to 5"; `415-20.` is 415-420.  When the
second number has FEWER digits than the first, restore the elided leading digits
from the first.  Written out in full -- `278-281.` -- it is left alone.

!!! IT FAILS IN THE DANGEROUS DIRECTION.  Read naively, `234-5.` yields the empty
range, so every unit it covers is reported as having no commentary paragraph --
a false "NOT COMMENTED", which is a confident denial that looks exactly like a
real result.  Measured over the corpus: **576 of the 2,572 leading ranges in the
118 volumes are abbreviated (22.4%), and reading them naively loses 926 numbers.**
Concentrated in `26KhuA07` (112), `06ViT06` (98), `28KhuA09` (46), `03VinA03`
(43), `27KhuA08` (36).  `32KhuA13` has 22, which is where it was found.

!!! AND IT WAS SILENTLY WRONG IN THE RATCHET.  `check_links.py` measured
`n_match` -- whether a link's target really carries its number -- with the naive
regex, so a link correctly pointing at a `234-5.` paragraph for n=235 was counted
as a MISS.  The published rate was therefore too low, and the ratchet that exists
to stop the map getting worse was itself misreading the edition.  Fixing it moves
the baseline UP; that is a corrected measurement, not an improvement in the data.

Usage:
    from printed_range import expand_range
    r = expand_range(p.get('text'))          # (lo, hi) or None
    if r and r[0] <= n <= r[1]: ...

    python3 pipeline/printed_range.py --selftest
    python3 pipeline/printed_range.py --census      # over site/
"""
import re

# `-` and the en dash `–` both occur; the terminator may be `.` or `,`
RANGE = re.compile(r'^\s*(\d+)\s*[-–]\s*(\d+)\s*[.,]')


def expand_range(text):
    """The leading printed range of a paragraph as (lo, hi), or None.

    Returns None when there is no leading range, and also when the pair cannot
    be read as ascending even after expansion -- a malformed range is not
    guessed at.  Flag rather than guess: the caller sees None and falls back to
    the exact number, which is the conservative direction here.
    """
    m = RANGE.match(text or '')
    if not m:
        return None
    lo_s, hi_s = m.group(1), m.group(2)
    if len(hi_s) < len(lo_s):
        # `415-20.` -> lo_s[:1] + '20' -> '420';  `234-5.` -> '23' + '5' -> '235'
        hi_s = lo_s[:len(lo_s) - len(hi_s)] + hi_s
    lo, hi = int(lo_s), int(hi_s)
    return (lo, hi) if hi >= lo else None


def covers(text, n):
    """True if the paragraph's printed range covers unit `n`."""
    r = expand_range(text)
    return bool(r) and r[0] <= n <= r[1]


def numbers_of(p):
    """Every unit number a paragraph record accounts for: its own `n` plus any
    covered by a printed range.  The two sources are unioned rather than one
    preferred -- a range paragraph usually carries the range's first number as
    `n` as well, and dropping either has cost a real reading before."""
    out = set()
    if p.get('n') is not None:
        out.add(p['n'])
    r = expand_range(p.get('text') or '')
    if r:
        out.update(range(r[0], r[1] + 1))
    return out


# ---------------------------------------------------------------- selftest
CASES = [
    # (text, expected)  -- the first four are transcribed from the printed page
    ('278-281. Disvā me -pa- pucchituṁ amataṁ padanti uttānatthameva.',
     (278, 281)),                       # written out in full, left alone
    ('234-5. Tassa Anomadassissa Bhagavato Munino monasaṅkhātena', (234, 235)),
    ('415-20. Tadaḍḍhakaṁ tato aḍḍhakaṁ aḍḍhatiyasatayojananti', (415, 420)),
    ('275-7. Ajjhāyako -pa- muniṁ mone samāhitanti monaṁ vuccati', (275, 277)),
    ('58-66. Pathabyā pathaviyā pabbate ca ākāse ca', (58, 66)),
    ('22-3. Evaṁ pāsādassa sobhaṁ vaṇṇetvā', (22, 23)),
    ('101-2. Sace labhethāti kā uppatti?', (101, 102)),
    ('1234-5. hypothetical four digit', (1234, 1235)),
    ('1234-45. hypothetical, two elided', (1234, 1245)),
    ('9-10. the upper bound is LONGER, so nothing is elided', (9, 10)),
    # !!! WIDE IS NOT WRONG, AND NO WIDTH GUARD IS IMPOSED.  Abbreviated ranges
    # run 2-6 units almost always, but `28KhuA09` p. 227 prints `604-57.` -- 54
    # units -- because the commentary declines the whole Serīsakapetavatthu as
    # identical with the Serīsakavimānavatthu, and p. 240 prints `714-36.` for
    # the Revatīpetavatthu the same way.  Both were read on the page before this
    # case was written.  A plausibility threshold would have rejected exactly the
    # two places where the edition says the most in one line.
    ('604-57. Suṇotha yakkhassa vāṇijānañcāti idaṁ Serīsakapetavatthu',
     (604, 657)),
    ('714-36. Uṭṭhehi revate supāpadhammeti idaṁ Revatīpetavatthu', (714, 736)),
    # !!! THE ONE MALFORMED RANGE IN THE CORPUS, AND IT IS NOT CORRECTED HERE.
    # `14Sam03` ord 592 prints `1187-1179.`  Both bounds are four digits, so
    # nothing is elided and the range simply descends.  Working principle 3 --
    # never silently correct the edition -- so this returns None and the caller
    # falls back to the exact number.  Recorded as an erratum, not repaired.
    ('1187-1179. Evameva kho bhikkhave appakā te sattā,', None),
    ('247. Aḷārapamhā hasulā, susaññā tanumajjhimā.', None),
    ('', None),
    (None, None),
    ('12–14. en dash', (12, 14)),
    ('12-4, comma terminator', (12, 14)),
]


def selftest():
    bad = 0
    print('SELFTEST  expand_range')
    for text, want in CASES:
        got = expand_range(text)
        ok = got == want
        bad += not ok
        print('  %-4s %-58s -> %-12s %s'
              % ('ok' if ok else 'FAIL',
                 (text or '(none)')[:58], got,
                 '' if ok else '(expected %s)' % (want,)))
    # !!! THE NAIVE READING MUST DISAGREE, OR THE FIX IS NOT DOING ANYTHING.
    # A selftest that only shows the new code agreeing with itself would pass
    # just as happily if expand_range were reverted to the naive form.
    naive = 0
    for text, want in CASES:
        m = RANGE.match(text or '')
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            n = (lo, hi) if hi >= lo else None
            if n != want:
                naive += 1
    print('  naive reading disagrees on %d of the %d cases%s'
          % (naive, len(CASES), '' if naive else '   <-- NOTHING IS BEING TESTED'))
    return 1 if (bad or not naive) else 0


def census():
    import json, os, collections
    site = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'site')
    vols = sorted(f[:-5] for f in os.listdir(site)
                  if f.endswith('.json') and re.match(r'^\d\d[A-Za-z]', f))
    tot = ab = lost = 0
    per = collections.Counter()
    for v in vols:
        try:
            P = json.load(open(os.path.join(site, v + '.json'),
                               encoding='utf-8'))['paragraphs']
        except Exception:
            continue
        for p in P:
            m = RANGE.match(p.get('text') or '')
            if not m:
                continue
            tot += 1
            if len(m.group(2)) < len(m.group(1)):
                ab += 1
                per[v] += 1
                r = expand_range(p.get('text'))
                lost += (r[1] - r[0]) if r else 0
    print('volumes                         %5d' % len(vols))
    print('paragraphs with a leading range %5d' % tot)
    print('  abbreviated upper bound       %5d   (%.1f%%)'
          % (ab, 100.0 * ab / max(tot, 1)))
    print('  unit numbers a naive reader loses %d' % lost)
    for v, c in per.most_common(12):
        print('    %-10s %4d' % (v, c))


if __name__ == '__main__':
    import sys
    if '--census' in sys.argv:
        census()
    else:
        sys.exit(selftest())
