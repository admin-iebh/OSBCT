# -*- coding: utf-8 -*-
"""Does hyjoin's CONSONANT branch already destroy edition hyphens where it RUNS?

discrim.py shows that on the paths where hyjoin does NOT run, 1,521 of the 8,812
hyphen-space breaks stand before a consonant, and some are the edition's own
grammatical citation hyphen (`ca-saddo`, `va-saddo`, `adi-saddena`).  hyjoin's
third branch drops the hyphen before a consonant.  If that branch is reached on
the paths where hyjoin DOES run, the corpus should contain the closed-up form.

So: for every hyphenated token the PAGE sets mid-line (where the hyphen cannot
be a line-break artefact), ask whether the CORPUS carries that token with the
hyphen removed.  A hit is text the builder has already corrupted.
"""
import json, os, re, sys, collections, importlib

sys.path.insert(0, os.path.abspath('pipeline'))
WORD = re.compile(r'[A-Za-zĀĪŪāīūṁṃṅñÑṬṭḌḍṆṇḶḷ-]+')


def main(vol):
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
                    continue      # vowel: hyjoin KEEPS the hyphen, not at risk
                mid.add(w)
    d = json.load(open('site/%s.json' % vol, encoding='utf-8'))
    body = '\n'.join((p.get('text') or '') for p in d['paragraphs'])
    low = body.casefold()
    hits = collections.Counter()
    for w in mid:
        closed = w.replace('-', '')
        if len(closed) < 8:
            continue              # too short to be safe against chance matches
        if closed.casefold() in low and w.casefold() not in low:
            hits[w] += low.count(closed.casefold())
    print('%-10s mid-line consonant-hyphen tokens %4d | CORRUPTED IN CORPUS %3d'
          % (vol, len(mid), len(hits)))
    for w, n in hits.most_common(6):
        print('        %-34s -> %-30s x%d' % (w, w.replace('-', ''), n))


for v in sys.argv[1:]:
    main(v)
