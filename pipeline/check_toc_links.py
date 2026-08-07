#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ratchet for `link_by_toc.py`: eight assertions over one canon vagga.

WHY THIS FILE EXISTS SEPARATELY.  The placement in `link_by_toc.py` was written
and looked right, and running these checks against it found two defects it could
not see in itself:

  1. a not_commented paragraph kept its FOREIGN records, so canon n=248 -- the
     paragraph the reader had just established is not commented at all -- went on
     drawing a live chip into `41KhuA22`, the Jātaka commentary.  The verdict said
     one thing and the link data did the other.
  2. 8 of the 133 uncommented paragraphs had no link entry to write a verdict
     onto, so they vanished from the accounting: 543 + 125 + 1 = 669 against 663
     canon numbers.  An identity that must hold is the cheapest instrument there
     is, and it was the one that noticed.

A third came out of assertion 2 once the first two were fixed: 56 superseded
records were being kept behind the new ones, each carrying the old builder's `n`,
every one of which failed "the target really carries this number" while the new
records passed.

THE ASSERTIONS.  Each is written so that it can only pass for a real reason.

  1  nothing outside the vagga is touched          -- scope
  2  every link's target really carries its number -- the placement is true
  3  only the eligible commentary is linked        -- the vagga rule held
  4  linked + not_commented + cannot_establish = the canon's numbered paragraphs
  5  no paragraph is both linked and verdicted     -- the states are exclusive
  6  at most one commentary record per paragraph   -- no superseded guesses
  7  targets advance monotonically through the vagga
  8  no verdict of silence over a number the commentary actually carries

!!! ASSERTION 7 CATCHES A PLAUSIBLE WRONG ANSWER.  1-6 are satisfied by any
self-consistent map, including one that pairs the right sections and then
scatters inside them.  A commentary follows its canon in order, so an inversion
means two links crossed -- the signature of a number matched in the wrong
section.  It tests the SHAPE of the result rather than its bookkeeping.

!!! ASSERTION 8 WAS ADDED AFTER ASSERTIONS 1-7 WERE ALL GREEN OVER A FILE THAT
WAS WRONG.  The reader opened Apadāna 5, saw the A chip dimmed, and asked how it
had been missed.  `32KhuA13` p. 111 quotes canon 5 in full and glosses it word by
word; the builder had written canon 5 out as `cannot_establish` because the
commentary section holding it paired with nothing, and every assertion stayed
green because all seven audit the links that WERE made.  Nothing looked at what
was not linked -- which is precisely where a claim about the edition's silence
lives.  A verdict is an assertion about the printed page and needs an instrument
pointed at the printed page, not at the builder's own bookkeeping.

Usage:
  python3 pipeline/check_toc_links.py 20Khu03 32KhuA13 --vagga 1
  python3 pipeline/check_toc_links.py 20Khu03 32KhuA13 --vagga 1 --live
  python3 pipeline/check_toc_links.py --selftest
"""
import json, os, sys, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import link_by_toc as T                                     # noqa: E402

LIVE = os.path.join(ROOT, 'site', 'reader', 'linksk')
DRY = os.path.join(ROOT, '_xc', 'linksk_toc')


def vagga_bounds(src, vg):
    for a, b, l in T.vaggas(src):
        n = T.tocnum(l)
        if n and n[0] == vg:
            return a, b, l
    raise SystemExit('no vagga %d in %s' % (vg, src))


def check(src, tgt, vg, new, old):
    C, A = T.paras(src), T.paras(tgt)
    a, b, lbl = vagga_bounds(src, vg)
    out = []

    def add(name, ok, detail):
        out.append((name, bool(ok), detail))

    keys = set(new) | set(old)
    outside = [k for k in keys
               if not (a <= int(k) <= b)
               and json.dumps(old.get(k), sort_keys=True)
               != json.dumps(new.get(k), sort_keys=True)]
    add('nothing outside the vagga touched', not outside,
        '%d paragraphs changed' % len(outside))

    ok = bad = 0
    vols = set()
    for k, e in new.items():
        if not (a <= int(k) <= b):
            continue
        for t in (e.get('commentary') or []):
            v, o = t['key'].split('#')
            vols.add(v)
            # !!! THE VOLUME IS NOT THIS ASSERTION'S BUSINESS.  Counting a
            # foreign record as a number failure made assertion 2 fire whenever
            # assertion 3 did, so the selftest could not show either one catching
            # its defect ALONE -- and an assertion that only ever fires alongside
            # another is not evidence of anything on its own.
            if v != tgt:
                continue
            o, n = int(o), t.get('n')
            r = T.expand_range(A[o].get('text') or '')
            if n is not None and (A[o].get('n') == n or (r and r[0] <= n <= r[1])):
                ok += 1
            else:
                bad += 1
    add('every link target carries its number', not bad,
        '%d ok, %d bad' % (ok, bad))
    add('only the eligible commentary is linked',
        not (vols - {tgt}), 'volumes linked: %s' % (sorted(vols) or ['-']))

    linked = nc = ce = 0
    for k, e in new.items():
        if not (a <= int(k) <= b):
            continue
        w = (e.get('verdict') or {}).get('why')
        # !!! A PARTITION, NOT THREE TALLIES.  Counting a paragraph as linked AND
        # verdicted made the total move whenever the states overlapped, so the
        # exclusivity defect showed up here too and neither assertion could be
        # seen catching it alone.  Exclusivity is assertion 5's job; this one
        # asks only whether every canon number was accounted for exactly once.
        if w == 'not_commented':
            nc += 1
        elif w == 'cannot_establish':
            ce += 1
        elif e.get('commentary'):
            linked += 1
    num = sum(1 for i in range(a, b + 1) if C[i].get('n') is not None)
    add('the accounting closes', linked + nc + ce == num,
        '%d linked + %d not_commented + %d cannot_establish = %d, canon has %d'
        % (linked, nc, ce, linked + nc + ce, num))

    dup = [k for k, e in new.items() if a <= int(k) <= b
           and e.get('commentary') and e.get('verdict')]
    add('the three states are exclusive', not dup,
        '%d paragraphs both linked and verdicted' % len(dup))

    mult = [k for k, e in new.items() if a <= int(k) <= b
            and len(e.get('commentary') or []) > 1]
    add('no superseded records kept', not mult,
        '%d paragraphs with more than one record' % len(mult))

    seq = [int(e['commentary'][0]['key'].split('#')[1])
           for k, e in sorted(new.items(), key=lambda x: int(x[0]))
           if a <= int(k) <= b and e.get('commentary')]
    inv = sum(1 for i in range(1, len(seq)) if seq[i] < seq[i - 1])
    add('targets advance monotonically', not inv, '%d inversions' % inv)

    # !!! THE ASSERTION THAT THE OTHER SEVEN COULD NOT MAKE, AND THE ONLY ONE
    # THAT TESTS THE VERDICT ITSELF.
    #
    # Reader, 2026-08-07: "paragraph 5 of the Apadānapāḷi is commented and the A
    # is dimmed.  You missed that?"  He was right.  `32KhuA13` ord 11 quotes
    # canon 5 in full and glosses it word by word, and canon 5 was nonetheless
    # written out as `cannot_establish` because the commentary section holding
    # it paired with nothing.  ALL SEVEN ASSERTIONS ABOVE WERE GREEN while that
    # was in the file, because every one of them checks the bookkeeping of the
    # links that WERE made.  None of them looks at what was NOT linked, which is
    # exactly where a claim about the edition's silence lives.
    #
    # So: a paragraph declared not_commented or cannot_establish must not have
    # its number carried ANYWHERE in the commentary's region for this vagga --
    # not merely absent from the section it was paired with.  The search is
    # deliberately wider than the placer's, so the placer cannot satisfy it by
    # construction.  A gate that only re-asks the question the builder already
    # asked is not an independent check.
    av = T.vaggas(tgt) or [(0, len(A) - 1, '')]
    cvn = T.tocnum(lbl)
    reg = [x for x in av if T.tocnum(x[2]) == cvn] or (av if len(av) == 1 else [])
    wrong = []
    if reg:
        r0, r1 = reg[0][0], reg[0][1]
        held = {}
        for j in range(r0, min(r1, len(A) - 1) + 1):
            if A[j].get('n') is not None:
                held.setdefault(A[j]['n'], j)
            rg = T.expand_range(A[j].get('text') or '')
            if rg:
                for x in range(rg[0], rg[1] + 1):
                    held.setdefault(x, j)
        for k, e in new.items():
            if not (a <= int(k) <= b):
                continue
            w = (e.get('verdict') or {}).get('why')
            if w not in ('not_commented', 'cannot_establish'):
                continue
            n = (e.get('verdict') or {}).get('n')
            if n is not None and n in held:
                wrong.append((k, n, held[n], A[held[n]].get('printed')))
    add('no verdict of silence over a number the commentary carries',
        not wrong,
        '%d paragraphs declared uncommented whose number IS in %s%s'
        % (len(wrong), tgt,
           '' if not wrong else '  e.g. n=%s at ord %s, printed p.%s'
           % (wrong[0][1], wrong[0][2], wrong[0][3])))
    return out


# ---------------------------------------------------------------- selftest
def selftest():
    """!!! EACH DEFECT IS INJECTED ALONE.  A gate that only fires on a heap of
    faults is untested against the one fault that will actually happen.  Every
    case below breaks exactly one assertion and must leave the other six green;
    a case that trips two means an assertion is not measuring what it claims."""
    src, tgt, vg = '20Khu03', '32KhuA13', 1
    base = json.load(open(os.path.join(DRY, src + '.links.json'), encoding='utf-8'))
    old = json.load(open(os.path.join(LIVE, src + '.links.json'), encoding='utf-8'))
    a, b, _ = vagga_bounds(src, vg)
    linked = [k for k, e in base.items()
              if a <= int(k) <= b and e.get('commentary')]
    verdicted = [k for k, e in base.items()
                 if a <= int(k) <= b
                 and (e.get('verdict') or {}).get('why') == 'not_commented']

    def mut(fn):
        d = copy.deepcopy(base)
        fn(d)
        return d

    def out_of_scope(d):
        k = max(base, key=int)
        d[k] = {'commentary': [{'key': tgt + '#1', 'state': 'direct'}]}

    def wrong_number(d):
        d[linked[5]]['commentary'][0]['n'] = 99999

    def foreign(d):
        # the exact defect of 2026-08-07: a link into the Jātaka commentary.
        # Only the VOLUME is changed -- same ordinal, same number -- so nothing
        # but the eligibility assertion has anything to object to.
        r = d[linked[5]]['commentary'][0]
        r['key'] = '41KhuA22#' + r['key'].split('#')[1]

    def lost_verdict(d):
        del d[verdicted[0]]['verdict']
        d[verdicted[0]].pop('commentary', None)

    def both_states(d):
        d[linked[5]]['verdict'] = {'why': 'not_commented'}

    def superseded(d):
        # a duplicate of the VALID record, so the extra one is unimpeachable on
        # every count except that it should not be there at all
        d[linked[5]]['commentary'].append(
            dict(d[linked[5]]['commentary'][0], state='covered'))

    def crossed(d):
        x, y = linked[10], linked[40]
        d[x]['commentary'][0], d[y]['commentary'][0] = \
            d[y]['commentary'][0], d[x]['commentary'][0]

    def false_silence(d):
        # the reader's canon-5 defect, reproduced: a paragraph the commentary
        # demonstrably glosses, written out as silence.  Moving it from linked
        # to not_commented leaves the accounting and the ordering untouched, so
        # only the assertion that reads the commentary itself can object.
        k = linked[5]
        n = d[k]['commentary'][0]['n']
        d[k]['commentary'] = []
        d[k]['verdict'] = {'why': 'not_commented', 'n': n}

    cases = [('out of scope', out_of_scope, 0),
             ('number not carried', wrong_number, 1),
             ('ineligible volume', foreign, 2),
             ('verdict lost', lost_verdict, 3),
             ('states overlap', both_states, 4),
             ('superseded record', superseded, 5),
             ('links crossed', crossed, 6),
             ('silence over a gloss', false_silence, 7)]
    print('SELFTEST')
    clean = check(src, tgt, vg, base, old)
    fails = [n for n, ok, d in clean if not ok]
    print('  %-22s %s' % ('unmutated input', 'all 8 green' if not fails
                          else 'NOT GREEN: %s' % fails))
    bad = bool(fails)
    for name, fn, idx in cases:
        r = check(src, tgt, vg, mut(fn), old)
        tripped = [i for i, (n, ok, d) in enumerate(r) if not ok]
        good = tripped == [idx]
        bad |= not good
        print('  %-22s -> %-38s %s'
              % (name, r[idx][0], 'caught, alone' if good
                 else 'WRONG: tripped %s' % [r[i][0] for i in tripped]))
    return 1 if bad else 0


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    argv = sys.argv[1:]
    vg = 1
    if '--vagga' in argv:
        k = argv.index('--vagga')
        vg = int(argv[k + 1])
        del argv[k:k + 2]
    a = [x for x in argv if not x.startswith('-')]
    if len(a) != 2:
        print(__doc__)
        sys.exit(2)
    src, tgt = a
    d = LIVE if '--live' in argv else DRY
    new = json.load(open(os.path.join(d, src + '.links.json'), encoding='utf-8'))
    old = json.load(open(os.path.join(LIVE, src + '.links.json'), encoding='utf-8'))
    print('%s -> %s  vagga %d   checking %s' % (src, tgt, vg, d))
    rows = check(src, tgt, vg, new, old)
    for n, ok, det in rows:
        print('  %-38s %-4s %s' % (n, 'PASS' if ok else 'FAIL', det))
    n_bad = sum(1 for _, ok, _ in rows if not ok)
    print('  %d passed, %d failed' % (len(rows) - n_bad, n_bad))
    sys.exit(1 if n_bad else 0)
