# -*- coding: utf-8 -*-
"""REPLAY THE PATCHED EMITTER over each volume's real printed item stream.

This is the method 43ecbd60 used for 20KhuA01, done by the builder itself
rather than by hand: `build_khu_volume.use(VOL); build()` runs `kat_items` /
`items_for` over the PDF and hands the patched emitter the same item stream it
would get in production.  Nothing is written to site/ here.

For every volume the rebuilt `sections` map is compared against the SHIPPED one
ordinal by ordinal, so a rebuild that moves anything OTHER than the flagged
gāthā entry is visible and refused rather than adopted wholesale.
"""
import importlib.util, json, os, sys
from importlib.machinery import SourceFileLoader
ROOT = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
OUT = os.path.join(ROOT, '_xc', 'italic9', 'rebuilt')
os.makedirs(OUT, exist_ok=True)

def load():
    p = os.path.join(ROOT, 'pipeline', 'build_khu_volume.py')
    spec = importlib.util.spec_from_loader('bkv', SourceFileLoader('bkv', p))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def main(vols):
    for vol in vols:
        m = load()                      # fresh module: `use` sets globals
        try:
            m.use(vol)
            v, s, u, h, i, rep = m.build()
        except Exception as e:
            print('%-12s BUILD FAILED %r' % (vol, e)); sys.stdout.flush(); continue
        json.dump({'sections': s, 'verse': v, 'uddana': u, 'hide': h, 'incipit': i},
                  open(os.path.join(OUT, vol + '.json'), 'w'), ensure_ascii=False)
        sp = os.path.join(ROOT, 'site', 'reader', 'sections', vol + '.json')
        S = json.load(open(sp, encoding='utf-8'))
        R = {str(k): x for k, x in s.items()}
        ka, kb = set(S), set(R)
        moved = [k for k in ka & kb if S[k] != R[k]]
        print('%-12s rebuilt: %d ords (shipped %d)  onlyShipped=%d onlyRebuilt=%d  moved=%d %s'
              % (vol, len(R), len(S), len(ka-kb), len(kb-ka), len(moved), sorted(moved)[:12]))
        sys.stdout.flush()

if __name__ == '__main__':
    main(sys.argv[1:])
