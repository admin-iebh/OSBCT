# -*- coding: utf-8 -*-
"""The reader said the Dukamatika dyads are TWO lines of text.  How many does the
corpus join into one?

Measured with the block map, which is what it is for: on the page each dyad is a
block of 2 printed lines; in the corpus each is one ordinal with a verse `after`
array.  If the page's block has 2 lines and `after` has 1 entry, the printed line
break is lost."""
import json, sys, os, collections
sys.path.insert(0, os.path.abspath('_xc/hy1'))
import adjudicate as A

vol = sys.argv[1] if len(sys.argv) > 1 else '29Abhi01'
d = json.load(open('site/%s.json' % vol, encoding='utf-8'))
ps = d['paragraphs']
V = json.load(open('site/reader/verse/%s.json' % vol, encoding='utf-8'))
BL = json.load(open('_xc/hy1/blocks/%s.json' % vol, encoding='utf-8'))
margin = A.vol_margin(vol, BL)

# printed blocks by their first line's leading text, per page
pageblocks = {}
for pg, p in BL.items():
    pageblocks[int(pg)] = A.judge_page(p, margin)[2]

NRM = lambda s: ''.join(c for c in (s or '') if c.isalnum())
lost = collections.Counter()
examples = []
for i, p in enumerate(ps):
    e = V.get(str(i))
    if not e or not e.get('after'):
        continue
    aft = e['after']
    if len(aft) != 1:
        continue
    key = NRM(aft[0])[:24]
    pg = p.get('pdf_page')
    for k, b in pageblocks.get(pg, []):
        if any(key and key in NRM(l[3]) for l in b):
            if len(b) > 1:
                lost['joined'] += 1
                lost['lines_lost'] += len(b) - 1
                if len(examples) < 5:
                    examples.append((p.get('n'), [l[3][:56] for l in b], aft[0][:80]))
            else:
                lost['ok'] += 1
            break
    else:
        lost['unmatched'] += 1
print('%s : one-entry `after` ordinals' % vol)
print('   printed block was 1 line  (correct)      : %d' % lost['ok'])
print('   printed block was >1 line (BREAK LOST)   : %d   costing %d printed lines'
      % (lost['joined'], lost['lines_lost']))
print('   not matched to a block                   : %d' % lost['unmatched'])
for n, blines, a in examples:
    print()
    print('   para %s -- page sets %d lines:' % (n, len(blines)))
    for l in blines:
        print('        | %s' % l)
    print('     corpus has ONE: %s' % a)
