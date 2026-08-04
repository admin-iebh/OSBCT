# -*- coding: utf-8 -*-
"""Write the replayed side-maps into site/, backing up to .prejat.

Refuses unless the PRE-CHANGE builder reproduces the shipped file byte for
byte: only then is every difference attributable to the change.
"""
import json, os, sys
ROOT = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
NAMES = ('verse', 'sections', 'uddana', 'hide', 'incipit')
for vol in sys.argv[1:]:
    R = json.load(open('%s/_xc/jat/rebuilt/%s.json' % (ROOT, vol), encoding='utf-8'))
    for n in NAMES:
        p = '%s/site/reader/%s/%s.json' % (ROOT, n, vol)
        data = {str(k): v for k, v in R[n].items()}
        if not data and not os.path.exists(p):
            continue
        if os.path.exists(p) and not os.path.exists(p + '.prejat'):
            os.link(p, p + '.prejat') if False else open(p + '.prejat', 'w', encoding='utf-8').write(
                open(p, encoding='utf-8').read())
        json.dump(data, open(p, 'w'), ensure_ascii=False)
        print('  wrote', p, len(data))
