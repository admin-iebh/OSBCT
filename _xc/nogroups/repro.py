# -*- coding: utf-8 -*-
"""Does `build_khu_volume.py` still reproduce the SHIPPED verse map, entry for
entry?  Nothing may be changed in the builder until it does -- a rebuild that
already differs cannot show what a change to it did."""
import json, os, sys, runpy, io, contextlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

def built(vol):
    argv = sys.argv[:]
    sys.argv = [ROOT + '/pipeline/build_khu_volume.py', vol]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            g = runpy.run_path(ROOT + '/pipeline/build_khu_volume.py',
                               run_name='__main__')
    finally:
        sys.argv = argv
    return g['v'], buf.getvalue()

def main():
    for vol in sys.argv[1:]:
        try:
            v, log = built(vol)
        except SystemExit as e:
            print('%-10s BUILD REFUSED: %s' % (vol, e)); continue
        except Exception as e:
            print('%-10s BUILD ERROR: %r' % (vol, e)); continue
        shipped = json.load(open('%s/site/reader/verse/%s.json' % (ROOT, vol),
                                 encoding='utf-8'))
        a = json.dumps(v, ensure_ascii=False, sort_keys=True)
        b = json.dumps(shipped, ensure_ascii=False, sort_keys=True)
        if a == b:
            print('%-10s IDENTICAL (%d entries)' % (vol, len(v)))
        else:
            ka, kb = set(v), set(shipped)
            diff = [k for k in ka & kb if v[k] != shipped[k]]
            print('%-10s DIFFERS  built %d shipped %d | only-built %d only-shipped %d '
                  '| changed %d  %s'
                  % (vol, len(v), len(shipped), len(ka - kb), len(kb - ka),
                     len(diff), sorted(diff, key=int)[:8]))

if __name__ == '__main__':
    main()
