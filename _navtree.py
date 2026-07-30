#!/usr/bin/env python3
"""Print a volume's nav tree as it stands in site/reader/nav.json.

    python3 _navtree.py <VOL> [label-substring]
"""
import json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
vol = sys.argv[1]
sub = sys.argv[2] if len(sys.argv) > 2 else None
nav = json.load(open(os.path.join(ROOT, 'site/reader/nav.json'), encoding='utf-8'))
hit = [v for L in nav['layers'] for nk in L.get('nikayas', [])
       for v in nk.get('volumes', []) if v.get('vol') == vol]
def walk(ns, d=0, on=False):
    for n in ns:
        show = on or sub is None or sub in n['label']
        if show:
            print('%s%-46s [%s]' % ('  ' * d, n['label'], n['key'].split('#')[1]))
        walk(n.get('kids', []), d + 1, show)
for nd in hit:
    print('NODE %r first=%s  %d rows'
          % (nd['title'], nd['first'],
             sum(1 for _ in json.dumps(nd.get('tree', [])).split('"label"')) - 1))
    walk(nd.get('tree', []))
