"""Which of the 67 candidates sit on back-matter pages the checker already excludes?

`check_page_fidelity` separates a volume's front contents and back index/appendix
out of its fault counts (`head_pages` / `tail_pages`).  The census in census.py
collected candidates from `r['rows']`, which is the RAW printed stream and still
holds those pages -- so the review sheet carried lines the instrument had already
set aside.  Recorded here rather than quietly dropped."""
import sys, os, json, time
sys.path.insert(0, os.path.abspath('pipeline'))
import check_page_fidelity as cpf

OUT = '_xc/hy1/edgepg.json'
seen = json.load(open(OUT)) if os.path.exists(OUT) else {}
vols = sorted({json.load(open('_xc/hy1/cen/' + f))['vol']
               for f in os.listdir('_xc/hy1/cen')
               if json.load(open('_xc/hy1/cen/' + f)).get('page_verse_hyphen')})
todo = [v for v in vols if v not in seen]
t0 = time.time()
for v in todo:
    if time.time() - t0 > float(sys.argv[1] if len(sys.argv) > 1 else 150):
        break
    r = cpf.run(v)
    seen[v] = {'head': r.get('head_pages'), 'tail': r.get('tail_pages')}
    json.dump(seen, open(OUT, 'w'))
    print('%-10s head=%s tail=%s' % (v, r.get('head_pages'), r.get('tail_pages')), flush=True)
print('done %d / %d' % (len(seen), len(vols)))
