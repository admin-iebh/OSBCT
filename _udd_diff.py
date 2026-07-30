"""Prove the tidy-filter change moves only the volumes the probe named.

Builds every SPEC volume with build_khu_volume.py.preuddlabel and with the
current file and compares all five maps byte-for-byte.  Resumable: appends one
line per volume to _udd_diff.jsonl.
"""
import importlib.util, json, os, sys
from importlib.machinery import SourceFileLoader

R = os.path.dirname(os.path.abspath(__file__))
MAPS = ('verse', 'sections', 'uddana', 'hide', 'incipit')

def load(path, name):
    sp = importlib.util.spec_from_loader(name, SourceFileLoader(name, path))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

OLD = load(os.path.join(R, 'pipeline/build_khu_volume.py.preuddlabel'), 'bkv_old')
NEW = load(os.path.join(R, 'pipeline/build_khu_volume.py'), 'bkv_new')

def maps(m, vol):
    m.use(vol)
    v, s, u, h, i, rep = m.build()
    return {k: json.dumps(d, ensure_ascii=False, sort_keys=True)
            for k, d in zip(MAPS, (v, s, u, h, i))}

out = os.path.join(R, '_udd_diff.jsonl')
done = {json.loads(l)['vol'] for l in open(out)} if os.path.exists(out) else set()
fh = open(out, 'a')
for vol in (sys.argv[1:] or sorted(NEW.SPEC)):
    if vol in done:
        continue
    a, b = maps(OLD, vol), maps(NEW, vol)
    diff = [k for k in MAPS if a[k] != b[k]]
    fh.write(json.dumps({'vol': vol, 'diff': diff}) + '\n'); fh.flush()
    print(vol, diff or 'identical', flush=True)
