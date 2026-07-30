"""Dry-run one volume's side-map build and diff it against what is on disk.

Writes NOTHING.  `build_khu_volume` only writes under `--write`, and this
driver never passes it: it imports the module (module-level body is spec and
function defs only, guarded by `if __name__ == '__main__'`), calls `use(VOL)`
then `build()`, and serialises each map exactly as the builder's own `write()`
would — `json.dump(..., ensure_ascii=False)`, default separators — so the
comparison is byte-for-byte against the shipped file.

Result line per volume, one of:
  SAME   <VOL>                       all five maps rebuild identical
  DIFF   <VOL>  <map>:+a-b~c ...     a added, b removed, c changed keys
  ERR    <VOL>  <exception>
"""
import io, json, os, sys, traceback, contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
R = os.path.join(ROOT, 'site', 'reader')
MAPS = ('verse', 'sections', 'uddana', 'hide', 'incipit')

def diff(old, new):
    if old is None:
        return 'MISSING-ON-DISK'
    if isinstance(new, dict) and isinstance(old, dict):
        ok, nk = set(old), set(new)
        add, rem = nk - ok, ok - nk
        chg = [k for k in ok & nk if old[k] != new[k]]
        if not (add or rem or chg):
            return None
        return '+%d-%d~%d' % (len(add), len(rem), len(chg))
    return None if old == new else 'NOT-A-DICT-CHANGED'

def run(vol):
    import build_khu_volume as B
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):          # the builder prints a lot
        B.use(vol)
        v, s, u, h, inc = B.build()[:5]
    out = {}
    for name, data in zip(MAPS, (v, s, u, h, inc)):
        p = os.path.join(R, name, vol + '.json')
        if not os.path.exists(p):
            out[name] = 'MISSING-ON-DISK' if data else None
            continue
        disk_txt = open(p, encoding='utf-8').read()
        new_txt = json.dumps(data, ensure_ascii=False)
        if disk_txt == new_txt:
            out[name] = None
            continue
        try:
            d = diff(json.loads(disk_txt), json.loads(new_txt))
        except Exception:
            d = 'UNPARSEABLE'
        out[name] = d or 'BYTES-ONLY'      # same content, different serialisation
    return out

if __name__ == '__main__':
    vol = sys.argv[1]
    try:
        out = run(vol)
    except Exception as e:
        print('ERR    %-10s %s: %s' % (vol, type(e).__name__, e))
        if '--tb' in sys.argv:
            traceback.print_exc()
        sys.exit(0)
    bad = {k: v for k, v in out.items() if v}
    if not bad:
        print('SAME   %-10s all five maps identical' % vol)
    else:
        print('DIFF   %-10s %s' % (vol, '  '.join('%s:%s' % kv for kv in bad.items())))
