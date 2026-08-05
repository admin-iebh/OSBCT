# -*- coding: utf-8 -*-
"""Mark the ordinal-condemned links, at BUILD TIME, on the record they dim.

`claude/decision_dim_the_condemned_links.md` (reader, 2026-08-03): links that
fail an independent check are DIMMED AND GIVEN A REASON, never suppressed.  They
still resolve.  This writes the reason; the reader draws it.

WHY THE FLAG RIDES ON THE LINK ENTRY, and not in a map of its own.  That doc's
third open question warns of the band lesson of `6f46b067`: a check that needs a
SECOND map loaded can return null on a cold cache and silently keep the undimmed
state -- which fails in the one direction that matters, showing a condemned link
as though nothing were wrong.  A separate `linkdim/` artefact has exactly that
failure mode.  Riding on the entry cannot: if the link is drawn, its verdict is
in hand.

WHY IT REUSES check_ordinal RATHER THAN RESTATING IT.  The 320 are whatever that
gate says they are.  A second implementation of "condemned" would drift from the
gate, and then the number the reader is shown and the number the ratchet defends
would be different numbers.  `stem`, `P`, `O`, `name_at`, `sn` are imported.

IDEMPOTENT.  Existing `dim` keys are dropped and recomputed, so a re-run after a
link rebuild is the same operation, and `--verify` asserts that stripping `dim`
returns the file byte-identical to git HEAD -- the reproducibility control this
project learned to want the hard way (`_xc/hy2/FINDINGS.md` 11.3).

    python3 pipeline/mark_condemned.py            # dry run, counts only
    python3 pipeline/mark_condemned.py --write
    python3 pipeline/mark_condemned.py --verify   # strip-dim == HEAD ?
"""
import os, sys, json, collections, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import check_ordinal as C

LINKS = C.LINKS
WRITE = '--write' in sys.argv
VERIFY = '--verify' in sys.argv


def strip_dim(obj):
    """the file as it would be without this script's field"""
    out = {}
    for si, rec in obj.items():
        r = {}
        for layer, ents in rec.items():
            r[layer] = [{k: v for k, v in e.items() if k != 'dim'} for e in ents]
        out[si] = r
    return out


def verify():
    bad = 0
    for f in sorted(os.listdir(LINKS)):
        if not f.endswith('.links.json'):
            continue
        p = os.path.join(LINKS, f)
        rel = os.path.relpath(p, ROOT)
        head = subprocess.run(['git', '-C', ROOT, 'show', 'HEAD:' + rel],
                              capture_output=True)
        if head.returncode:
            continue
        cur = strip_dim(json.load(open(p, encoding='utf-8')))
        was = strip_dim(json.loads(head.stdout.decode('utf-8')))
        if json.dumps(cur, sort_keys=True) != json.dumps(was, sort_keys=True):
            bad += 1
            print('   *** %s differs from HEAD beyond the dim field' % f)
    print('verify: %d files differ beyond `dim`' % bad)
    return bad


def main():
    if VERIFY:
        sys.exit(1 if verify() else 0)
    st = collections.Counter()
    for f in sorted(os.listdir(LINKS)):
        if not f.endswith('.links.json'):
            continue
        cv = f[:-len('.links.json')]
        cps = C.P(cv)
        if not cps:
            continue
        p = os.path.join(LINKS, f)
        links = json.load(open(p, encoding='utf-8'))
        touched = False
        for si, rec in links.items():
            i = int(si)
            if i >= len(cps):
                continue
            a = C.sn(cps[i])
            cn = C.stem(C.name_at(cv, i))
            for layer in ('commentary', 'subcommentary'):
                for ent in rec.get(layer) or []:
                    if ent.pop('dim', None) is not None:
                        touched = True
                    if a is None or ent.get('state') != 'direct':
                        continue
                    tv, _, tis = (ent.get('key') or '').partition('#')
                    if not tis.isdigit():
                        continue
                    ti = int(tis)
                    o = C.O(tv).get(ti)
                    if o is None:
                        continue          # the target states no ordinal: silent
                    st['checked'] += 1
                    if o == a:
                        continue
                    st['condemned'] += 1
                    tps = C.P(tv)
                    tn = C.stem(tps[ti].get('sutta')) if ti < len(tps) else ''
                    # The section name is a THIRD criterion and it does not
                    # always speak.  Report which of the three states it is in,
                    # never collapse `silent` into `concurs`.
                    name = ('concurs' if (cn and tn and cn != tn) else
                            'dissents' if (cn and tn) else 'silent')
                    st['name_' + name] += 1
                    ent['dim'] = {'why': 'ordinal', 'says': o, 'expected': a,
                                  'name': name}
                    touched = True
        if touched and WRITE:
            json.dump(links, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    print('%s  checked %d   CONDEMNED %d   (name concurs %d, dissents %d, silent %d)'
          % ('WROTE' if WRITE else 'DRY RUN', st['checked'], st['condemned'],
             st['name_concurs'], st['name_dissents'], st['name_silent']))


main()
