# -*- coding: utf-8 -*-
"""Replay the builder over a volume and compare every side-map with the shipped
one.  Resumable: one <VOL>.json per volume under _xc/jat/rebuilt/."""
import importlib.util, json, os, sys, time
from importlib.machinery import SourceFileLoader
ROOT = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
OUT = os.path.join(ROOT, '_xc', 'jat', 'rebuilt')
os.makedirs(OUT, exist_ok=True)

def load():
    p = os.path.join(ROOT, 'pipeline', 'build_khu_volume.py')
    spec = importlib.util.spec_from_loader('bkv', SourceFileLoader('bkv', p))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def main(vols):
    budget = 40.0
    t0 = time.time()
    for vol in vols:
        dst = os.path.join(OUT, vol + '.json')
        if os.path.exists(dst):
            continue
        if time.time() - t0 > budget:
            print('BUDGET'); return
        m = load()
        try:
            m.use(vol)
            v, s, u, h, i, rep = m.build()
        except Exception as e:
            print('%-9s BUILD FAILED %r' % (vol, e)); sys.stdout.flush(); continue
        json.dump({'verse': v, 'sections': s, 'uddana': u, 'hide': h, 'incipit': i,
                   'report': rep}, open(dst, 'w'), ensure_ascii=False)
        out = [vol]
        for name, cur in (('verse', v), ('sections', s), ('uddana', u),
                          ('hide', h), ('incipit', i)):
            sp = os.path.join(ROOT, 'site', 'reader', name, vol + '.json')
            S = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}
            R = {str(k): x for k, x in cur.items()}
            same = (S == R)
            moved = [k for k in set(S) & set(R) if S[k] != R[k]]
            out.append('%s %s(ship %d cur %d, -%d +%d moved %d)'
                       % (name, 'SAME' if same else 'DIFF', len(S), len(R),
                          len(set(S) - set(R)), len(set(R) - set(S)), len(moved)))
        print('  '.join(out)); sys.stdout.flush()

if __name__ == '__main__':
    main(sys.argv[1:])
