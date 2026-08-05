# -*- coding: utf-8 -*-
"""repro.py over every volume.  Resumable, budgeted; writes _xc/hy2/repro/.

The question is not 'does extract.py work' but 'for WHICH volumes is the
shipped corpus still what extract.py produces'.  35Abhi07 reproduces 714/714
exactly; 20KhuA01 produces 63 paragraphs against a shipped 673.  A repair at
extract.py:204 reaches only the first kind.
"""
import sys, os, json, time

sys.path.insert(0, os.path.abspath('pipeline'))
OUT = '_xc/hy2/repro'


def pdf_of(vol):
    for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
        p = '%s/%s.pdf' % (d, vol)
        if os.path.exists(p):
            return p
    return None


def one(vol):
    import extract as E
    pdf = pdf_of(vol)
    if not pdf:
        return {'vol': vol, 'error': 'no pdf'}
    pgs, paras, heads = E.extract(pdf)
    ship = json.load(open('site/%s.json' % vol, encoding='utf-8'))['paragraphs']
    a = [(p.get('text') or '').strip() for p in paras]
    b = [(p.get('text') or '').strip() for p in ship]
    n = min(len(a), len(b))
    sa = set(a)
    return {'vol': vol, 'n_extract': len(a), 'n_shipped': len(b),
            'same_index': sum(1 for x, y in zip(a, b) if x == y),
            'present_anywhere': sum(1 for y in b if y in sa),
            'pct_index': round(100.0 * sum(1 for x, y in zip(a, b) if x == y)
                               / max(1, n), 2)}


def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 480
    os.makedirs(OUT, exist_ok=True)
    vols = sorted(f[:-5] for f in os.listdir('site') if f.endswith('.json'))
    t0 = time.time()
    for v in vols:
        dst = '%s/%s.json' % (OUT, v)
        if os.path.exists(dst) or not pdf_of(v):
            continue
        if time.time() - t0 > budget:
            print('BUDGET'); break
        try:
            r = one(v)
        except Exception as e:
            r = {'vol': v, 'error': '%s: %s' % (type(e).__name__, e)}
        json.dump(r, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
        print('%-10s extract %5s shipped %5s  same-index %5s (%s%%) %s'
              % (v, r.get('n_extract', '-'), r.get('n_shipped', '-'),
                 r.get('same_index', '-'), r.get('pct_index', '-'),
                 r.get('error', '')), flush=True)
    print('recorded %d' % len(os.listdir(OUT)))


main()
