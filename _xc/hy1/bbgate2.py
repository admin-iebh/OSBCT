# -*- coding: utf-8 -*-
"""bbgate.py, on MULTISETS.

bbgate.py computes the newly drawn lines as

    new = [x for k in da for x in db.get(k, []) if x not in set(da[k])]

which is a SET test, and on a text as formulaic as the Yamaka that is a large
undercount in two independent ways:

  1. the same damaged string is drawn dozens of times and collapses to one;
  2. a string that ALSO occurs somewhere in the flag-off build for the same
     ordinal is not counted new at all, however many extra copies ON draws.

This counts occurrences instead: per ordinal, Counter(ON) - Counter(OFF).
Same mid-sentence test, so the two are directly comparable.
"""
import sys, os, importlib, collections

sys.path.insert(0, os.path.abspath('pipeline'))
TERM = ('.', ',', ';', ':', '?', '!', '–', '—', '”', '’', ')', '-')


def build(vol, flag):
    os.environ['BLOCKBREAK'] = flag
    for m in list(sys.modules):
        if m.startswith('build_khu_volume_bb'):
            del sys.modules[m]
    mod = importlib.import_module('build_khu_volume_bb')
    mod.use(vol)
    return mod.build()[0]


def drawn(v):
    out = {}
    for k, e in v.items():
        acc = []

        def w(x):
            if isinstance(x, str):
                acc.append(x)
            elif isinstance(x, dict):
                for y in x.values():
                    w(y)
            elif isinstance(x, list):
                for y in x:
                    w(y)
        for kk in ('before', 'after', 'tail', 'groups'):
            w(e.get(kk))
        out[k] = acc
    return out


tot = collections.Counter()
for vol in sys.argv[1:]:
    try:
        da, db = drawn(build(vol, '0')), drawn(build(vol, '1'))
    except Exception as e:
        print('%-10s ERROR %s' % (vol, e)); continue
    new_set, new_ms, bad_set, bad_ms = 0, 0, 0, 0
    worst = collections.Counter()
    for k in da:
        A, B = da[k], db.get(k, [])
        sa = set(A)
        ns = [x for x in B if x not in sa]
        new_set += len(ns)
        bad_set += sum(1 for x in ns if (x or '').rstrip()[-1:] not in TERM)
        d = collections.Counter(B) - collections.Counter(A)
        for x, c in d.items():
            new_ms += c
            if (x or '').rstrip()[-1:] not in TERM:
                bad_ms += c
                worst[x] += c
    la = sum(len(x) for x in da.values()); lb = sum(len(x) for x in db.values())
    tot['new_set'] += new_set; tot['bad_set'] += bad_set
    tot['new_ms'] += new_ms; tot['bad_ms'] += bad_ms; tot['delta'] += lb - la
    print('%-10s drawn %5d -> %5d (%+5d) | SET new %4d bad %3d | MULTISET new %4d bad %3d %s'
          % (vol, la, lb, lb - la, new_set, bad_set, new_ms, bad_ms,
             '<<< FAIL' if bad_ms else ''), flush=True)
    for x, c in worst.most_common(4):
        print('        %3dx  %s' % (c, x[:88]))
print()
print('TOTAL  %+d drawn | SET new %d bad %d | MULTISET new %d bad %d'
      % (tot['delta'], tot['new_set'], tot['bad_set'], tot['new_ms'], tot['bad_ms']))
