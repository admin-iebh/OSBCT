"""Measurement only: which uddana blocks does the tidy filter drop, corpus-wide?

Loads a copy of build_khu_volume.py whose tidy filter records what it removes
instead of silently removing it.  Writes one JSON line per volume so the run
can be resumed a few volumes at a time (device_bash has a 45 s ceiling).
"""
import importlib.util, json, os, re, sys
from importlib.machinery import SourceFileLoader

R = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(R, 'pipeline', 'build_khu_volume.py')
TMP = os.path.join(R, 'pipeline', '_udd_probe_mod.py')

s = open(SRC).read()
old = "        uddana[k] = [b for b in uddana[k] if b.get('lines') or b.get('head')]"
assert s.count(old) == 1, s.count(old)
new = ("        for _b in uddana[k]:\n"
       "            if not (_b.get('lines') or _b.get('head')):\n"
       "                DROPPED.append((k, dict(_b)))\n" + old)
open(TMP, 'w').write("DROPPED = []\n" + s.replace(old, new))

spec = importlib.util.spec_from_loader('bkv_probe', SourceFileLoader('bkv_probe', TMP))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

out = os.path.join(R, '_udd_probe.jsonl')
done = set()
if os.path.exists(out):
    for l in open(out):
        done.add(json.loads(l)['vol'])

vols = sys.argv[1:] or sorted(m.SPEC)
fh = open(out, 'a')
for vol in vols:
    if vol in done:
        continue
    m.DROPPED[:] = []
    m.use(vol)
    v, sec, u, h, inc, rep = m.build()
    fh.write(json.dumps({'vol': vol, 'n': len(m.DROPPED),
                         'dropped': m.DROPPED}, ensure_ascii=False) + '\n')
    fh.flush()
    print(vol, len(m.DROPPED), flush=True)
