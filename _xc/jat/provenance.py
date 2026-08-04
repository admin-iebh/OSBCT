# -*- coding: utf-8 -*-
"""Where do the class-1 and class-3 lines come from?  Per flagged printed line,
which side-map holds its letters, so classes 1 and 3 can be told apart by SOURCE
and not merely by the class the reader gives them."""
import sys, os, re, json, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
ALPHA = re.compile(r'[^0-9A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]')
def L(s): return ALPHA.sub('', s or '')

def maps(vol):
    S = os.path.join(ROOT, 'site')
    def j(p):
        try: return json.load(open(p, encoding='utf-8'))
        except Exception: return {}
    return (j('%s/reader/verse/%s.json' % (S, vol)),
            j('%s/reader/sections/%s.json' % (S, vol)),
            j('%s/reader/uddana/%s.json' % (S, vol)))

def sources(vol):
    vm, sec, udd = maps(vol)
    out = {}                       # name -> letter string
    def cat(name, lines):
        out[name] = out.get(name, '') + ''.join(L(x) for x in lines)
    g, bef, aft = [], [], []
    for o, e in vm.items():
        for l in (e.get('groups') or []):
            g.extend(l)
        for key, sink in (('before', bef), ('after', aft)):
            x = e.get(key)
            if x is None: continue
            for b in (x if isinstance(x, list) else [x]):
                if isinstance(b, dict) and 'gatha' in b: sink.extend(b['gatha'])
    cat('verse.groups', g); cat('verse.before.gatha', bef); cat('verse.after.gatha', aft)
    sg, sp, sh = [], [], []
    for o, es in sec.items():
        for e in es:
            (sg if e.get('k') == 'gatha' else sp if e.get('k') == 'prose' else sh).append(e.get('l') or '')
    cat('sections.gatha', sg); cat('sections.prose', sp); cat('sections.head', sh)
    ul = []
    for o, bs in udd.items():
        for b in bs:
            if b.get('label'): ul.append(b['label'])
            ul.extend(b.get('lines', []))
    cat('uddana', ul)
    return out

def main(vols):
    for vol in vols:
        rows = json.load(open('%s/_xc/jat/%s.rows.json' % (ROOT, vol), encoding='utf-8'))['rows']
        src = sources(vol)
        for cls in ('PROSE_AS_VERSE', 'PROSE_AS_UDDANA'):
            c = collections.Counter()
            for r in rows:
                if r[5] != cls: continue
                t = L(r[6])
                hit = [n for n, s in src.items() if t and t in s]
                c['+'.join(hit) or 'NONE'] += 1
            print('%-10s %-16s %s' % (vol, cls, dict(c)))

if __name__ == '__main__':
    main(sys.argv[1:])
