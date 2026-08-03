# -*- coding: utf-8 -*-
"""Proof harness for rekey_sect.py, in the style of 4d4a1db7.

FIXTURES
  1. 07DiA01 "3:1" -- the ONE sect.json span set that exists anywhere in the
     corpus (8 real spans over the Sumaṅgalavilāsinī's opening gāthā), split
     at its own printed line boundaries.
  2. The seven real ordinals this change actually splits, with a span on EVERY
     WORD of the old entry text.  The shipped maps for those volumes are all
     `{}`, so without this the arithmetic would never be exercised on the real
     splits at all; with it, it is exercised on the real texts and the real
     boundaries.

NEGATIVE CONTROL: three corruptions of the same input, each of which MUST make
the proof fail.  4d4a1db7 records that on its first run all three controls
PASSED because the corrupt-mode flag was never read -- so the controls are run
here through the same call path as the honest run, with the corruption applied
inside `rekey` itself, and the harness FAILS LOUDLY if a control passes.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rekey_sect import rekey, prove, offsets, Straddle

ROOT = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
FIX = [('02Vin02', '0', 3), ('06VinSg06', '0', 1), ('14SamA01', '0', 5),
       ('17AnA01', '0', 3), ('27Khu10', '151', 1), ('36Abhi08', '0', 1),
       ('38Abhi10', '0', 6)]


def wordspans(text):
    return [[m.start(), m.end()] for m in re.finditer(r'\S+', text)]


def case(name, old_entries, new_entries, ordk, idx, sect):
    old_text = str(old_entries[ordk][idx].get('l', ''))
    k = len(new_entries[ordk]) - len(old_entries[ordk]) + 1
    new_texts = [str(x.get('l', '')) for x in new_entries[ordk][idx:idx+k]]
    try:
        offsets(old_text, new_texts)
    except Straddle as e:
        print('  %-34s TILING REFUSED: %s' % (name, e)); return None
    nsect = rekey(sect, ordk, idx, old_text, new_texts)
    c, p, f = prove(sect, nsect, ordk, idx, old_entries, new_entries)
    print('  %-34s %d -> %d entries   spans checked %d  passed %d  FAILED %d'
          % (name, len(old_entries[ordk]), len(new_entries[ordk]), c, p, len(f)))
    for x in f[:3]:
        print('        %r' % (x,))
    ctrl = {}
    for mode in ('shift1', 'allfirst', 'noshift'):
        try:
            bad = rekey(sect, ordk, idx, old_text, new_texts, _corrupt=mode)
            # A CORRUPTION THAT CHANGES NOTHING IS NOT A CONTROL.  `allfirst`
            # is inert when every span of the split entry already lands in the
            # first piece, and `noshift` is inert when no key follows the split
            # -- and counting those as "the control passed" is exactly the
            # false alarm the first run of this harness produced.  A case is
            # scored only where the corruption actually moved the map, and the
            # harness separately requires that each mode be non-vacuous
            # SOMEWHERE, so a control cannot go unexercised either.
            vacuous = (json.dumps(bad, sort_keys=True)
                       == json.dumps(nsect, sort_keys=True))
            c2, p2, f2 = prove(sect, bad, ordk, idx, old_entries, new_entries)
        except Straddle as e:
            vacuous = False
            c2, p2, f2 = 0, 0, [('refused', str(e))]
        ctrl[mode] = (c2, p2, len(f2), vacuous)
    return {'checked': c, 'passed': p, 'failed': len(f), 'ctrl': ctrl,
            'nsect': nsect, 'k': k}


def main():
    print('=== FIXTURE 1: 07DiA01 "3:1", the corpus\'s only real sect.json spans')
    S = json.load(open(ROOT + '/site/reader/sections/07DiA01.json', encoding='utf-8'))
    sect = json.load(open(ROOT + '/site/reader/bold/07DiA01.sect.json', encoding='utf-8'))
    ordk, idx = '3', 1
    old = str(S[ordk][idx]['l'])
    lines = old.split('\n')
    # THE INDEX-SHIFT PATH NEEDS KEYS AFTER THE SPLIT, and in the seven real
    # splits only ONE has an entry after it -- so on real data alone the
    # `noshift` control is exercised exactly once and proves almost nothing.
    # The entries following this one are given a span on every word, which
    # exercises the shift on all 31 cuts.
    sect = dict(sect)
    for j in range(idx + 1, len(S[ordk])):
        ws = wordspans(str(S[ordk][j].get('l', '')))
        if ws:
            sect['%s:%d' % (ordk, j)] = ws
    print('  entry: %d printed lines, %d chars, %d real spans, %d keys after the split'
          % (len(lines), len(old), len(json.load(open(
              ROOT + '/site/reader/bold/07DiA01.sect.json', encoding='utf-8'))['3:1']),
             len(sect) - 1))
    results = []
    for cut in range(1, len(lines)):
        newS = {o: list(a) for o, a in S.items()}
        newS[ordk] = (S[ordk][:idx]
                      + [{'k': 'gatha', 'l': '\n'.join(lines[:cut])},
                         {'k': 'prose', 'l': '\n'.join(lines[cut:])}]
                      + S[ordk][idx+1:])
        r = case('split after printed line %d' % cut, S, newS, ordk, idx, sect)
        if r: results.append(r)
    print()
    print('=== FIXTURE 2: the seven real splits, a span on every word')
    # The replay dumps are ~13 MB and are NOT committed; they are regenerable,
    # and this harness says so rather than dying on a missing path.
    missing = [v for v, _o, _i in FIX
               if not os.path.exists('%s/_xc/italic9/rebuilt/%s.json' % (ROOT, v))]
    if missing:
        print('  SKIPPED -- no replay dumps for %s.' % ', '.join(missing))
        print('  Regenerate with:  python3 _xc/italic9/replay.py %s'
              % ' '.join(v for v, _o, _i in FIX))
        print('  (fixture 1 above is unaffected and its result stands)')
    for vol, ordk, idx in FIX:
        if vol in missing:
            continue
        S = json.load(open('%s/site/reader/sections/%s.json' % (ROOT, vol), encoding='utf-8'))
        R = json.load(open('%s/_xc/italic9/rebuilt/%s.json' % (ROOT, vol), encoding='utf-8'))['sections']
        R = {str(o): a for o, a in R.items()}
        sect = {}
        # a span on every word of the split entry ...
        sect['%s:%d' % (ordk, idx)] = wordspans(str(S[ordk][idx]['l']))
        # ... and on every word of every LATER entry, so the index shift is
        # exercised too and not only the redistribution.
        for j in range(idx + 1, len(S[ordk])):
            ws = wordspans(str(S[ordk][j].get('l', '')))
            if ws:
                sect['%s:%d' % (ordk, j)] = ws
        r = case('%s ord%s[%d]' % (vol, ordk, idx), S, R, ordk, idx, sect)
        if r: results.append(r)

    print()
    tot_c = sum(r['checked'] for r in results)
    tot_p = sum(r['passed'] for r in results)
    tot_f = sum(r['failed'] for r in results)
    print('SEMANTIC PROOF   %d spans checked, %d passed, %d failed' % (tot_c, tot_p, tot_f))
    print()
    print('NEGATIVE CONTROL (each MUST fail; a control that passes voids the proof)')
    bad_controls = []
    for mode in ('shift1', 'allfirst', 'noshift'):
        live = [r for r in results if not r['ctrl'][mode][3]]
        vac = len(results) - len(live)
        cc = sum(r['ctrl'][mode][0] for r in live)
        pp = sum(r['ctrl'][mode][1] for r in live)
        ff = sum(r['ctrl'][mode][2] for r in live)
        silent = [r for r in live if r['ctrl'][mode][2] == 0]
        if not live:
            note = 'NEVER EXERCISED -- control is worthless here'
            bad_controls.append(mode + '(unexercised)')
        elif silent:
            note = 'PASSED ON %d CORRUPT CASES -- CONTROL BROKEN' % len(silent)
            bad_controls.append(mode)
        else:
            note = 'OK, caught on all %d' % len(live)
        print('  %-9s %d cases live (%d vacuous, not scored): %d spans, %d passed, '
              '%d failed   %s' % (mode, len(live), vac, cc, pp, ff, note))
    print()
    if tot_f == 0 and not bad_controls:
        print('RESULT  PASS  (%d/%d spans, all three controls exercised and caught)'
              % (tot_p, tot_c))
        return 0
    print('RESULT  FAIL  failures=%d broken_controls=%s' % (tot_f, bad_controls))
    return 1


if __name__ == '__main__':
    sys.exit(main())
