# -*- coding: utf-8 -*-
"""A gate on BLOCKBREAK: does any restored break fall MID-SENTENCE?

A structural line break falls at a boundary; a WRAP does not.  So every drawn
line the patch newly creates should end at a terminator, and one that does not is
a break the patch invented inside a running sentence -- the exact damage the
ragged/justified test was added to stop (34KhuA15 ord14, 'Idha Tathagato' /
'Yamakapatihiram karoti').

This is deliberately INDEPENDENT of the ragged test itself: it reads the produced
side-map, not the block map, so it can fail when that test is wrong.
"""
import sys, os, re, importlib, json, collections

sys.path.insert(0, os.path.abspath('pipeline'))
TERM = ('.', ',', ';', ':', '?', '!', '–', '—', '”', '’', ')', '-')
# A FOOTNOTE MARKER IS NOT THE END OF THE LINE.  The marker is a superscript
# digit that follows the punctuation, so `…kammaṁ vinassatī”ti.6` ends in `6`
# and the raw last-character test called a properly terminated line
# mid-sentence.  It reported 32KhuA13 as 2 when the real number is 1.
# check_page_fidelity already separates these as `digit_only`; this gate did not.
_MARK = re.compile(r'\d+$')


def ends_at_boundary(x):
    return _MARK.sub('', (x or '').rstrip()).rstrip()[-1:] in TERM


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
    new = [x for k in da for x in db.get(k, []) if x not in set(da[k])]
    bad = [x for x in new if not ends_at_boundary(x)]
    la = sum(len(x) for x in da.values()); lb = sum(len(x) for x in db.values())
    tot['new'] += len(new); tot['bad'] += len(bad); tot['delta'] += lb - la
    print('%-10s drawn %5d -> %5d (%+5d)   new lines %4d   MID-SENTENCE %3d %s'
          % (vol, la, lb, lb - la, len(new), len(bad), '<<< FAIL' if bad else ''), flush=True)
    for x in bad[:3]:
        print('        ?? %s' % x[:96])
print()
print('TOTAL  +%d drawn lines, %d new, %d mid-sentence' % (tot['delta'], tot['new'], tot['bad']))
