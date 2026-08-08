#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ordinal words for VAGGA numbers, 1-60, generated and then proved.

WHY A SECOND TABLE.  `ordinal_words.py` covers 1-30 and names a sutta's position
WITHIN a vagga -- `113. Sattame adhammacariyāti`.  The Apadāna commentary also
names whole VAGGAS, and goes past 30:

    p. 199  Catutiṁsatimavagga-pañcatiṁsatimavagga-chattiṁsatimavagga-
            sattatiṁsatimavagga-aṭṭhatiṁsatimavaggā uttānatthāyeva.
            Ekūnacattālīsamavaggepi paṭhamāpadānādīni aṭṭhamāpadānantāni
            uttānānevāti.
    p. 212  Paññāsamavagge ca ekapaññāsamavagge ca dvepaññāsamavagge ca
            tepaññāsamavagge ca sabbāni apadānāni uttānānevāti.

That is the edition stating its own coverage in words, and it is the only
statement of it there is: `34. Gandhodakavaggādivaṇṇanā` gives `34` and `ādi`,
and `ādi` alone does not say where it stops.  The words do -- and they stop at
38, then treat the 39th separately and only as far as its eighth apadāna.
Inferring the span from the next head's number would have got 34-39 entire and
been wrong about the 39th.

GENERATED, THEN PROVED.  The forms are regular -- decade stem plus unit prefix,
with `ekūna-` ("one less than") for 9-before-the-decade -- so the table is
generated rather than typed, which is how a typo gets in.  `verify()` then reads
every occurrence in the corpus and checks it against the number printed on the
head it sits under.  A form nobody uses proves nothing and is harmless; a form
that occurs and disagrees with its head is a failure and is printed.

!!! THE DECADE WORD ALONE IS THE ROUND NUMBER.  `cattālīsama` is 40th, not
"fortieth-something", and `paññāsama` is 50th.  Unit-prefixed forms are 41+ and
51+.  Getting this backwards would shift a whole decade by one and still look
plausible, which is why 40 and 50 are asserted explicitly in the selftest.

!!! SANDHI AT THE JOIN, AND IT IS NOT UNDONE BY HAND.  `vagga` + `ādi` is
`vaggādi`, one vowel; `-vaggā` closes a list.  Matching therefore looks for the
ordinal stem immediately followed by `vagg`, and never tries to split a compound
back into its parts.

Usage:
    from ordinal_vagga import VAGGA_ORD, read_vaggas
    read_vaggas(text)      # -> sorted list of vagga numbers the text names

    python3 pipeline/ordinal_vagga.py --selftest
    python3 pipeline/ordinal_vagga.py --verify       # against site/
"""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')

# 1-10, and the decade words.  Spelling variants are the edition's.
UNITS = {
    1: ['paṭhama'], 2: ['dutiya'], 3: ['tatiya'], 4: ['catuttha'],
    5: ['pañcama'], 6: ['chaṭṭha'], 7: ['sattama'], 8: ['aṭṭhama'],
    9: ['navama'], 10: ['dasama'],
}
# prefixes used when a unit is compounded onto a decade
PRE = {
    1: ['eka'], 2: ['bā', 'dvā', 'dve', 'du'], 3: ['te', 'ti'],
    4: ['catu'], 5: ['pañca'], 6: ['cha', 'chat', 'cham'],
    7: ['satta'], 8: ['aṭṭha'],
}
DECADE = {
    10: ['dasama'], 20: ['vīsatima', 'vīsama'], 30: ['tiṁsatima', 'tiṁsama'],
    40: ['cattālīsama', 'cattārīsama'], 50: ['paññāsama', 'paṇṇāsama'],
    60: ['saṭṭhima'],
}


def _build():
    t = collections.defaultdict(set)
    for n, ws in UNITS.items():
        for w in ws:
            t[w].add(n)
    for d, dws in DECADE.items():
        for dw in dws:
            t[dw].add(d)                       # the decade word alone == d
            for u, pws in PRE.items():
                for pw in pws:
                    t[pw + dw].add(d + u)      # ekacattālīsama = 41
            # `ekūna-` is "one less than": ekūnavīsatima = 19
            for pw in ('ekūna', 'ūna'):
                t[pw + dw].add(d - 1)
    # 11-19 are irregular and are taken from ordinal_words.py, which already
    # carries the edition's own spellings for them
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import ordinal_words as O
    for w, v in O.LOC.items():
        t[w[:-1] + 'a'].add(v)
    # a form that resolves to more than one number is not usable as evidence
    return {w: sorted(v)[0] for w, v in t.items() if len(v) == 1}


VAGGA_ORD = _build()
_STEMS = sorted(VAGGA_ORD, key=len, reverse=True)
_ALT = '|'.join(re.escape(s) for s in _STEMS)
# the ordinal stem immediately followed by `vagg` -- see the sandhi note above
VAGGA_RE = re.compile('(' + _ALT + ')vagg', re.IGNORECASE)


def read_vaggas(text):
    """Every vagga number the text names, in order, deduplicated."""
    out = []
    for m in VAGGA_RE.finditer((text or '').lower()):
        n = VAGGA_ORD.get(m.group(1))
        if n is not None and n not in out:
            out.append(n)
    return sorted(out)


# ---------------------------------------------------------------- verify
HEADNUM = re.compile(r'^\s*(\d+)')


def verify(quiet=False):
    """Every occurrence in the corpus, against the ENCLOSING VAGGA's number.

    !!! THE FIRST VERSION OF THIS COMPARED THE WRONG TWO THINGS and reported 75
    failures that were not failures.  `05ViT05` ord 52 sits under the head
    `1. Ovādasikkhāpadavaṇṇanā` and its text opens `Tatiyavaggassa paṭhame` --
    the FIRST sikkhāpada OF THE THIRD vagga.  Head number 1, vagga named 3, and
    both are right: the head numbers the sikkhāpada, the words name the vagga
    containing it.  Checking the words against the head asked whether a sutta
    number equals a vagga number, which is not a question about anything.

    The enclosing vagga is the real control, and it is a much stronger test:
    it puts the generated table against the corpus's own structural numbering
    on every occurrence, in volumes that have nothing to do with the Apadāna.
    """
    secdir = os.path.join(SITE, 'reader', 'sections')
    ok = bad = 0
    fails = []
    for f in sorted(os.listdir(secdir)):
        if not f.endswith('.json'):
            continue
        v = f[:-5]
        try:
            P = json.load(open(os.path.join(SITE, v + '.json'),
                               encoding='utf-8'))['paragraphs']
            S = json.load(open(os.path.join(secdir, f), encoding='utf-8'))
        except Exception:
            continue
        # ordinal -> number of the vagga head at or before it
        vg = []
        for k in sorted(S, key=int):
            for x in S[k]:
                if x.get('k') == 'vagga':
                    m = HEADNUM.match(x['l'] or '')
                    if m:
                        vg.append((int(k), int(m.group(1))))
        if not vg:
            continue
        starts = [a for a, _ in vg]
        import bisect
        for k in sorted(S, key=int):
            o = int(k)
            # !!! THE OPENING ONLY.  The formula that names the vagga stands
            # at the head of the paragraph; a mention 300 characters in is a
            # cross-reference to some other vagga and is not this paragraph's
            # subject.  Scanning 400 characters produced false disagreements --
            # `16SamA03` ord 201 opens `Tatiye ...` and was scored against a
            # `paṭhamavagge` far later in the same paragraph.
            got = read_vaggas((P[o].get('text') or '')[:120])
            if not got:
                continue
            j = bisect.bisect_right(starts, o) - 1
            if j < 0:
                continue
            enc = vg[j][1]
            # the enclosing vagga must be among the vaggas the words name --
            # a declaration legitimately names several, starting with its own
            if enc in got:
                ok += 1
            else:
                bad += 1
                fails.append((v, o, enc, got,
                              (P[o].get('text') or '')[:70]))
    if not quiet:
        print('occurrences agreeing with the enclosing vagga: %d' % ok)
        print('occurrences disagreeing:                       %d' % bad)
        for v, o, h, g, t in fails[:12]:
            print('   %-10s ord %-5d enclosing vagga %-4d names %s\n        %s'
                  % (v, o, h, g, t))
    return ok, bad, fails


def selftest():
    bad = 0
    # !!! TRANSCRIBED FROM THE PRINTED PAGE, not from the generator.
    CASES = [
        ('Catutiṁsatimavaggapañcatiṁsatimavaggachattiṁsatimavagga-'
         'sattatiṁsatimavagga-aṭṭhatiṁsatimavaggā uttānatthāyeva.',
         [34, 35, 36, 37, 38]),
        ('Ekūnacattālīsamavaggepi paṭhamāpadānādīni aṭṭhamāpadānantāni'
         ' uttānānevāti.', [39]),
        ('Ekavīsatime bāvīsatime tevīsatime ca vagge', []),   # no `-vagg` join
        ('Paññāsamavagge ca ekapaññāsamavagge ca dvepaññāsamavagge ca'
         ' tepaññāsamavagge ca sabbāni apadānāni uttānānevāti.',
         [50, 51, 52, 53]),
        ('Tecattālīsamavagge sabbatherāpadānāni uttānāneva.', [43]),
        ('Ito parampi ekūnavīsatimavagge āgatānaṁ', [19]),
        ('Vīsatime vagge paṭhamattherāpadānaṁ uttānameva.', []),
    ]
    print('SELFTEST  read_vaggas')
    for t, want in CASES:
        got = read_vaggas(t)
        okk = got == want
        bad += not okk
        print('  %-4s %-62s -> %-18s %s'
              % ('ok' if okk else 'FAIL', t[:62], got,
                 '' if okk else '(expected %s)' % want))
    # the two that would shift a whole decade
    for w, n in (('cattālīsama', 40), ('paññāsama', 50), ('dasama', 10),
                 ('ekacattālīsama', 41), ('ekūnacattālīsama', 39)):
        got = VAGGA_ORD.get(w)
        okk = got == n
        bad += not okk
        print('  %-4s %-24s = %-4s %s'
              % ('ok' if okk else 'FAIL', w, got, '' if okk else '(want %d)' % n))
    # !!! THE TRANSCRIBED CASES ARE THE GROUND TRUTH AND THEY MUST ALL PASS.
    # The corpus sweep is reported but does NOT fail the selftest, and the
    # reason is recorded rather than assumed: the residue is volumes whose own
    # vagga heads are not extracted -- `03ViT03` places six paragraphs that name
    # vaggas 2-7 under an enclosing vagga 9 -- which is the SAME defect
    # `fix_vagga_heads.py` addresses, in volumes not yet done.  Failing here on
    # someone else's missing heads would make this file's gate meaningless and
    # invite it being switched off.
    ok, nbad, _ = verify(quiet=True)
    print('  corpus: %d occurrences agree with the enclosing vagga, %d disagree'
          % (ok, nbad))
    print('  (the residue is volumes whose vagga heads are not extracted;'
          ' see fix_vagga_heads.py)')
    if not ok:
        print('  *** NOTHING WAS TESTED against the corpus ***')
    return 1 if (bad or not ok) else 0


if __name__ == '__main__':
    if '--verify' in sys.argv:
        verify()
    else:
        sys.exit(selftest())
