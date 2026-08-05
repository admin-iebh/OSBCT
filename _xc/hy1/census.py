"""Corpus-wide: printed lines ending in a line-break hyphen, by the PAGE's class
and the CORPUS's class.  Resumable, one JSON per volume, budgeted."""
import sys, os, json, time, collections
sys.path.insert(0, os.path.abspath('pipeline'))
import check_page_fidelity as cpf

OUT = '_xc/hy1/cen'
os.makedirs(OUT, exist_ok=True)
budget = float(sys.argv[1]) if len(sys.argv) > 1 else 500
vols = cpf.all_vols()
t0 = time.time()
todo = [v for v in vols if not os.path.exists('%s/%s.json' % (OUT, v))]
sys.stderr.write('done %d todo %d\n' % (len(vols) - len(todo), len(todo)))
for v in todo:
    if time.time() - t0 > budget:
        sys.stderr.write('BUDGET, %d left\n' % len(todo)); break
    try:
        r = cpf.run(v, verbose=True)
        if r is None: 
            json.dump({'vol': v, 'skip': 1}, open('%s/%s.json' % (OUT, v), 'w')); continue
        c = collections.Counter()
        ex = []
        for x in r['rows']:
            if not (x[6] or '').rstrip().endswith('-'):
                continue
            c['hy'] += 1
            c['hy_%s' % x[3]] += 1                    # page class
            c['v_%s' % x[5]] += 1                     # verdict
            if x[3] == 'verse':
                ex.append([x[0], x[1], x[5], x[6][:100]])
        json.dump({'vol': v, 'counts': dict(c), 'page_verse_hyphen': ex},
                  open('%s/%s.json' % (OUT, v), 'w'), ensure_ascii=False)
        print('%-10s hy %5d  page-verse %4d  page-prose %5d' %
              (v, c['hy'], c['hy_verse'], c['hy_prose']), flush=True)
    except Exception as e:
        json.dump({'vol': v, 'err': '%s: %s' % (type(e).__name__, e)},
                  open('%s/%s.json' % (OUT, v), 'w'))
        print('%-10s ERR %s' % (v, e), flush=True)
