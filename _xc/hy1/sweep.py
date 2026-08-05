# -*- coding: utf-8 -*-
"""Driver for the BLOCKBREAK sweep over every `katha`-mode volume.

RESUMABLE: skips any volume already in _xc/hy1/sweep/, and stops when the
budget runs out.  `nohup ... &` does not survive between bridge calls, so this
is written to be re-invoked, never left running.

    python3 _xc/hy1/sweep.py [budget_seconds] [per_volume_timeout]
"""
import sys, os, json, time, subprocess

ROOT = os.path.abspath('.')
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
OUT = '_xc/hy1/sweep'


def katha_volumes():
    import build_khu_volume as L
    out = []
    for k, v in sorted(L.SPEC.items()):
        bs = v.get('books') if isinstance(v, dict) else None
        if bs and any(len(b) > 6 and b[6] == 'katha' for b in bs):
            out.append(k)
    return out


def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 480
    pertim = float(sys.argv[2]) if len(sys.argv) > 2 else 240
    os.makedirs(OUT, exist_ok=True)
    vols = katha_volumes()
    todo = [v for v in vols if not os.path.exists('%s/%s.json' % (OUT, v))]
    print('katha volumes %d ; done %d ; todo %d'
          % (len(vols), len(vols) - len(todo), len(todo)), flush=True)
    t0 = time.time()
    for v in todo:
        if time.time() - t0 > budget:
            print('BUDGET -- %d left' % (len(todo) - todo.index(v)), flush=True)
            break
        try:
            subprocess.run([sys.executable, '_xc/hy1/sweep_one.py', v],
                           timeout=pertim)
        except subprocess.TimeoutExpired:
            # Record it, so the sweep does not retry it forever and so a slow
            # volume is visible as a slow volume rather than as a gap.
            json.dump({'vol': v, 'ok': False, 'error': 'TIMEOUT %.0fs' % pertim},
                      open('%s/%s.json' % (OUT, v), 'w'))
            print('%-10s TIMEOUT %.0fs' % (v, pertim), flush=True)
    done = len(os.listdir(OUT))
    print('sweep: %d / %d volumes recorded' % (done, len(vols)), flush=True)


main()
