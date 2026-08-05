# -*- coding: utf-8 -*-
"""A printed line-break hyphen that survived into the corpus WITH A SPACE after it.

`hyjoin` decides a line-end hyphen three ways: keep it and space off (peyyala
-pa-), keep it closed up (the edition's own junction hyphen before a vowel:
'agata-' + 'annena' -> 'agata-annena'), or drop it (a soft word break: 'yutta-'
+ 'Madaya' -> 'yuttaMadaya').  NONE of the three leaves 'hyphen + space' inside
a word.  Where the corpus has that, hyjoin was not applied and the plain
prev + ' ' + t path ran instead -- so the word is broken in the corpus text
itself, not merely drawn in two blocks.

Peyyala (-pa- -pe- -la-) and a hyphen before a capital or an opening quote are
excluded: those are the shapes where a following space is correct or ambiguous.
"""
import json, os, re, collections

BAD = re.compile(r'(?<=[a-zāīūṁṃṅñṭḍṇḷ])- (?=[a-zāīūṁṃṅñṭḍṇḷ])')
PEY = re.compile(r'-(?:pa|pe|la)- ')
tot, byvol, ex = 0, collections.Counter(), []
for f in sorted(os.listdir('site')):
    if not f.endswith('.json') or '/' in f:
        continue
    vol = f[:-5]
    try:
        d = json.load(open('site/' + f, encoding='utf-8'))
    except Exception:
        continue
    if not isinstance(d, dict) or 'paragraphs' not in d:
        continue
    for p in d['paragraphs']:
        t = p.get('text') or ''
        t2 = PEY.sub(' ', t)
        for m in BAD.finditer(t2):
            tot += 1
            byvol[vol] += 1
            if len(ex) < 40:
                ex.append((vol, p.get('pdf_page'), p.get('n'),
                           t2[max(0, m.start() - 46):m.end() + 40]))
print('corpus paragraphs carrying a line-break hyphen followed by a space')
print('total occurrences : %d   across %d volumes' % (tot, len(byvol)))
print()
for v, n in byvol.most_common(15):
    print('   %-10s %5d' % (v, n))
print()
for v, pg, n, s in ex[:18]:
    print('   %-10s p%-5s ¶%-6s …%s…' % (v, pg, n, s.replace('\n', ' ')))
