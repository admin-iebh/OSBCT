# -*- coding: utf-8 -*-
"""The 8,790 hyphen-space breaks, split by what hyjoin WOULD do to them.

FINDINGS 10.4 says the repair is to route these through `hyjoin`, whose three
decisions are: peyyala -> keep and space off; next letter a VOWEL -> keep the
hyphen and close up; otherwise -> DROP the hyphen and close up.

Reading the actual occurrences, that third branch is not safe.  01ViT01 p40
carries `Upannasattho va ca- saddo` and `Va- saddo hi upamana...`, and the SAME
volume writes `ettha va-saddo padapuranena` mid-line with the hyphen kept.  The
`-saddo` construction ("the word `ca`", "the word `va`") is the EDITION'S OWN
hyphen and it stands before a consonant.  hyjoin would produce `casaddo` and
`vasaddo`.

So the population must be split before anything is joined, and the consonant
branch needs its own evidence.  This counts the split; discrim.py tests the
evidence.
"""
import json, os, re, collections

BAD = re.compile(r'(?<=[a-zāīūṁṃṅñṭḍṇḷ])- (?=[A-Za-zĀĪŪāīūṁṃṅñṭḍṇḷ])')
PEY = re.compile(r'-(?:pa|pe|la)- ')
VOWELS = set('aāiīuūeoAĀIĪUŪEO')

tot = collections.Counter()
byvol_cons = collections.Counter()
ex_cons = []

for f in sorted(os.listdir('site')):
    if not f.endswith('.json'):
        continue
    vol = f[:-5]
    try:
        d = json.load(open('site/' + f, encoding='utf-8'))
    except Exception:
        continue
    if not isinstance(d, dict) or 'paragraphs' not in d:
        continue
    for p in d['paragraphs']:
        t = PEY.sub(' ', p.get('text') or '')
        for m in BAD.finditer(t):
            nxt = t[m.end():m.end() + 1]
            tot['all'] += 1
            if nxt in VOWELS:
                tot['vowel_keep'] += 1
            else:
                tot['consonant'] += 1
                byvol_cons[vol] += 1
                if len(ex_cons) < 30:
                    ex_cons.append((vol, p.get('pdf_page'),
                                    t[max(0, m.start() - 40):m.end() + 34]))

print('hyphen-space occurrences        : %d' % tot['all'])
print('  next letter a VOWEL  (hyjoin keeps the hyphen, closes up) : %d  (%.1f%%)'
      % (tot['vowel_keep'], 100.0 * tot['vowel_keep'] / max(1, tot['all'])))
print('  next letter a CONSONANT (hyjoin DROPS the hyphen)         : %d  (%.1f%%)'
      % (tot['consonant'], 100.0 * tot['consonant'] / max(1, tot['all'])))
print()
print('consonant branch, worst volumes:')
for v, n in byvol_cons.most_common(10):
    print('   %-10s %5d' % (v, n))
print()
for v, pg, s in ex_cons[:16]:
    print('   %-10s p%-5s …%s…' % (v, pg, s.replace('\n', ' ')))
