# -*- coding: utf-8 -*-
"""Build a volume with BLOCKBREAK off and on IN THE SAME PROCESS and diff the
side-maps.  The builder's own summary line is not the measure -- it reports
`prose_paras` from a counter, and a counter is not the artefact."""
import json, os, sys, importlib, collections

ROOT = os.path.abspath('.')
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))


def build(vol, flag):
    os.environ['BLOCKBREAK'] = flag
    for m in list(sys.modules):
        if m.startswith('build_khu_volume_bb'):
            del sys.modules[m]
    mod = importlib.import_module('build_khu_volume_bb')
    mod.use(vol)
    v, s, u, h, i, r = mod.build()
    return {'verse': v, 'sections': s, 'uddana': u, 'hide': h, 'incipit': i}


def drawn(v):
    """every drawn line in the verse map, as a flat list per ordinal"""
    out = {}
    for k, e in v.items():
        acc = []

        def walk(x):
            if isinstance(x, str):
                acc.append(x)
            elif isinstance(x, dict):
                for y in x.values():
                    walk(y)
            elif isinstance(x, list):
                for y in x:
                    walk(y)
        for kk in ('before', 'after', 'tail', 'groups'):
            walk(e.get(kk))
        out[k] = acc
    return out


vol = sys.argv[1]
A = build(vol, '0')
B = build(vol, '1')
da, db = drawn(A['verse']), drawn(B['verse'])
print('== %s ==' % vol)
for name in ('sections', 'uddana', 'hide', 'incipit'):
    same = json.dumps(A[name], sort_keys=True, ensure_ascii=False) == \
           json.dumps(B[name], sort_keys=True, ensure_ascii=False)
    print('   %-9s %s' % (name, 'identical' if same else '*** CHANGED ***'))
la = sum(len(x) for x in da.values())
lb = sum(len(x) for x in db.values())
moved = [k for k in da if da.get(k) != db.get(k)]
print('   verse ordinals %d -> %d' % (len(da), len(db)))
print('   DRAWN LINES    %d -> %d   (%+d)' % (la, lb, lb - la))
print('   ordinals whose drawn lines change: %d' % len(moved))
# text must be preserved exactly: the concatenation may not change
ja = ''.join(''.join(da[k]) for k in sorted(da, key=lambda z: int(z)))
jb = ''.join(''.join(db[k]) for k in sorted(db, key=lambda z: int(z)))
import re
n = lambda s: re.sub(r'[^0-9A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]', '', s)
print('   letters identical: %s' % (n(ja) == n(jb)))
for k in moved[:3]:
    print('   -- ord %s' % k)
    for x in da[k][:2]:
        print('      OFF | %s' % x[:78])
    for x in db[k][:3]:
        print('      ON  | %s' % x[:78])
