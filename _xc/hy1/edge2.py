# -*- coding: utf-8 -*-
"""Head/tail AND the interior index gaps, per volume.

edge.py recorded only `head_pages`/`tail_pages`, and align26.py filtered on those
alone -- so on 26 volumes the edition's word index counted as BODY and the join
looked 3-7% worse than it is.  check_page_fidelity does not find those indexes as
a tail at all: it names them as interior gaps matching INDEXRE and subtracts them
as `index_lines`.  18AnA02 reports tail_pages None and edge 3316 together, which
is what gave the game away."""
import sys, os, json, time
sys.path.insert(0, os.path.abspath('pipeline'))
import check_page_fidelity as cpf

OUT = '_xc/hy1/edge2.json'
done = json.load(open(OUT)) if os.path.exists(OUT) else {}
vols = cpf.all_vols()
budget = float(sys.argv[1]) if len(sys.argv) > 1 else 150
t0 = time.time()
for v in vols:
    if v in done:
        continue
    if time.time() - t0 > budget:
        break
    r = cpf.run(v)
    done[v] = {'head': r.get('head_pages'), 'tail': r.get('tail_pages'),
               'index': [[g[0], g[1]] for g in r.get('gaps', []) if g[3] == 'index']}
    json.dump(done, open(OUT, 'w'))
    print('%-10s head=%s tail=%s index_gaps=%s' % (v, done[v]['head'], done[v]['tail'],
                                                   done[v]['index']), flush=True)
print('done %d / %d' % (len(done), len(vols)))
