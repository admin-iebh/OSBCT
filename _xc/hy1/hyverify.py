# -*- coding: utf-8 -*-
"""Control on hyspace.py: is each flagged 'hyphen + space' really a PRINTED LINE
BREAK, or does the edition set it that way?

For every occurrence, look for a printed line that ENDS with the flagged hyphen
and a NEXT printed line that BEGINS with the continuation.  Found => the edition
broke a line there and the corpus inserted a space that is not on the page.
Not found => the flag is wrong and hyspace.py is over-counting."""
import json, os, re, sys, random
sys.path.insert(0, os.path.abspath('_xc/reseg'))
import pline

BAD = re.compile(r'(?<=[a-zāīūṁṃṅñṭḍṇḷ])- (?=[a-zāīūṁṃṅñṭḍṇḷ])')
PEY = re.compile(r'-(?:pa|pe|la)- ')
NRM = re.compile(r'[^0-9A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]')
n = lambda s: NRM.sub('', s or '')

vols = sys.argv[1:] or ['01ViT01', '05ViT05', '06ViT06', '09DiT02', '46KhuA27']
random.seed(11)
gtot = gok = gno = 0
for vol in vols:
    st = pline.stream(vol)
    ends, starts = {}, {}
    for i, l in enumerate(st):
        t = l[3].rstrip()
        if t.endswith('-'):
            ends.setdefault(n(t[:-1])[-14:], []).append(i)
    d = json.load(open('site/%s.json' % vol, encoding='utf-8'))
    hits = []
    for p in d['paragraphs']:
        t = PEY.sub(' ', p.get('text') or '')
        for m in BAD.finditer(t):
            hits.append((n(t[max(0, m.start() - 30):m.start() + 1])[-14:],
                         n(t[m.end():m.end() + 24])[:12]))
    smp = random.sample(hits, min(60, len(hits)))
    ok = no = 0
    for pre, post in smp:
        found = False
        for i in ends.get(pre, []):
            if i + 1 < len(st) and n(st[i + 1][3])[:12].startswith(post[:8]):
                found = True
                break
        ok, no = (ok + 1, no) if found else (ok, no + 1)
    gtot += len(smp); gok += ok; gno += no
    print('%-10s occurrences %5d   sampled %3d   confirmed a printed line break %3d   NOT %3d'
          % (vol, len(hits), len(smp), ok, no))
print()
print('sample total %d   confirmed %d (%.1f%%)   unconfirmed %d'
      % (gtot, gok, 100.0 * gok / max(1, gtot), gno))
