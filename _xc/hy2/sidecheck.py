# -*- coding: utf-8 -*-
"""Do the side-maps ALREADY carry the closed-up form?

`verse/`, `sections/`, `uddana/`, `incipit/` are produced by
build_khu_volume.py, which HAS hyjoin.  `paragraphs[].text` is produced by
extract.py, which has not.  So the two layers may already disagree at exactly
these places -- and if they do, repairing the paragraph text does not 'change'
the corpus so much as make it consistent with what the reader is already drawn.

For each vowel-branch occurrence in a paragraph, look at the same ordinal's
drawn lines and ask which form they hold.
"""
import json, os, re, sys, collections

BAD = re.compile(r'(?<=[a-zāīūṁṃṅñṭḍṇḷ])- (?=[aāiīuūeoAĀIĪUŪEO])')
PEY = re.compile(r'-(?:pa|pe|la)- ')


def drawn_of(vol):
    out = collections.defaultdict(list)
    for d in ('verse', 'sections', 'uddana', 'incipit'):
        p = 'site/reader/%s/%s.json' % (d, vol)
        if not os.path.exists(p):
            continue
        data = json.load(open(p, encoding='utf-8'))
        if not isinstance(data, dict):
            continue
        for k, v in data.items():
            acc = []

            def w(x):
                if isinstance(x, str):
                    acc.append(x)
                elif isinstance(x, dict):
                    for y in x.values():
                        w(y)
                elif isinstance(x, list):
                    for y in x:
                        w(y)
            w(v)
            out[str(k)] += acc
    return out


def main(vol):
    paras = json.load(open('site/%s.json' % vol, encoding='utf-8'))['paragraphs']
    dr = drawn_of(vol)
    st = collections.Counter()
    ex = []
    for i, p in enumerate(paras):
        t = p.get('text') or ''
        masked = PEY.sub('#####', t)
        for m in BAD.finditer(masked):
            st['occurrences'] += 1
            # the two halves either side of the hyphen
            a = re.search(r'[A-Za-zĀĪŪāīūṁṃṅñÑṬṭḌḍṆṇḶḷ]+-$', t[:m.start() + 1])
            b = re.match(r'[A-Za-zĀĪŪāīūṁṃṅñÑṬṭḌḍṆṇḶḷ]+', t[m.end():])
            if not a or not b:
                st['unparsed'] += 1
                continue
            left, right = a.group(0), b.group(0)
            broken = left + ' ' + right          # what the paragraph text has
            closed = left + right                # what hyjoin would produce
            lines = dr.get(str(i)) or dr.get(str(p.get('n'))) or []
            blob = '\n'.join(lines)
            if not lines:
                st['no side-map for this ordinal'] += 1
            elif closed in blob and broken not in blob:
                st['SIDE-MAP ALREADY CLOSED'] += 1
                if len(ex) < 6:
                    ex.append(('closed', closed))
            elif broken in blob:
                st['side-map has the SAME break'] += 1
            else:
                st['not found in side-map'] += 1
    print('== %s ==' % vol)
    for k, v in st.most_common():
        print('   %-32s %5d' % (k, v))
    for k, s in ex:
        print('      %s | %s' % (k, s))


for v in sys.argv[1:]:
    main(v)
