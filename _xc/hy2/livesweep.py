# -*- coding: utf-8 -*-
"""livecheck.py over every volume.  Resumable, budgeted; writes _xc/hy2/live/."""
import json, os, re, sys, time, collections, importlib, subprocess

sys.path.insert(0, os.path.abspath('pipeline'))
WORD = re.compile(r'[A-Za-zĀĪŪāīūṁṃṅñÑṬṭḌḍṆṇḶḷ-]+')
OUT = '_xc/hy2/live'


def one(vol):
    os.environ['BLOCKBREAK'] = '0'
    for m in list(sys.modules):
        if m.startswith('build_khu_volume'):
            del sys.modules[m]
    mod = importlib.import_module('build_khu_volume')
    mod.use(vol)
    mid = set()
    for pg in mod.pdf_pages():
        for l in pg.split('\n'):
            s = l.rstrip()
            for m in WORD.finditer(s):
                w = m.group(0).strip('-')
                if '-' not in w or m.end() >= len(s):
                    continue
                a, _, b = w.partition('-')
                if not a or not b or b[0] in 'aāiīuūeoAĀIĪUŪEO':
                    continue
                mid.add(w)
    d = json.load(open('site/%s.json' % vol, encoding='utf-8'))
    low = '\n'.join((p.get('text') or '') for p in d['paragraphs']).casefold()
    hits = {}
    for w in mid:
        c = w.replace('-', '')
        if len(c) < 8:
            continue
        if c.casefold() in low and w.casefold() not in low:
            hits[w] = low.count(c.casefold())
    return {'vol': vol, 'midline': len(mid), 'corrupt_types': len(hits),
            'corrupt_tokens': sum(hits.values()), 'hits': hits}


def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 480
    os.makedirs(OUT, exist_ok=True)
    vols = sorted(f[:-5] for f in os.listdir('site') if f.endswith('.json'))
    t0 = time.time()
    for v in vols:
        dst = '%s/%s.json' % (OUT, v)
        if os.path.exists(dst):
            continue
        if time.time() - t0 > budget:
            print('BUDGET'); break
        try:
            r = one(v)
        except Exception as e:
            r = {'vol': v, 'error': '%s: %s' % (type(e).__name__, e)}
        json.dump(r, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
        print('%-10s midline %4s  corrupt types %3s  tokens %4s %s'
              % (v, r.get('midline', '-'), r.get('corrupt_types', '-'),
                 r.get('corrupt_tokens', '-'), r.get('error', '')), flush=True)
    print('recorded %d / %d' % (len(os.listdir(OUT)), len(vols)))


main()
