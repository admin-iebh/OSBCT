# -*- coding: utf-8 -*-
"""What ELSE moves if the vowel-branch space is deleted from paragraph text?

The repair is a one-character deletion per occurrence.  Bold spans are
[start, end] CHARACTER OFFSETS into paragraphs[].text -- verified: 35Abhi07 ord32
span [3,10] is exactly 'Pavatti'.  So every span lying after a deleted space
must shift by one, or the bold moves onto the wrong letters.

This measures the exposure before anything is written.
"""
import json, os, re, collections

BAD = re.compile(r'(?<=[a-zāīūṁṃṅñṭḍṇḷ])- (?=[aāiīuūeoAĀIĪUŪEO])')
PEY = re.compile(r'-(?:pa|pe|la)- ')
st = collections.Counter()
vols = collections.Counter()

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
    bp = 'site/reader/bold/%s.bold.json' % vol
    bold = json.load(open(bp, encoding='utf-8')) if os.path.exists(bp) else {}
    for i, p in enumerate(d['paragraphs']):
        t = p.get('text') or ''
        # peyyala must not be touched: '-pa- ' keeps its space
        holes = [m.start() + 1 for m in BAD.finditer(PEY.sub('#####', t))]
        if not holes:
            continue
        st['paragraphs'] += 1
        st['deletions'] += len(holes)
        vols[vol] += len(holes)
        sp = bold.get(str(i)) or bold.get(str(p.get('n'))) or []
        if sp:
            st['paragraphs_with_bold'] += 1
            for a, b in sp:
                st['spans_in_those_paragraphs'] += 1
                if any(h < b for h in holes):
                    st['SPANS THAT MUST SHIFT'] += 1

print('vowel-branch deletions            : %d  in %d paragraphs, %d volumes'
      % (st['deletions'], st['paragraphs'], len(vols)))
print('  of those paragraphs, carry bold : %d' % st['paragraphs_with_bold'])
print('  bold spans in them              : %d' % st['spans_in_those_paragraphs'])
print('  SPANS THAT MUST SHIFT           : %d' % st['SPANS THAT MUST SHIFT'])
print()
for v, n in vols.most_common(8):
    print('   %-10s %5d' % (v, n))
