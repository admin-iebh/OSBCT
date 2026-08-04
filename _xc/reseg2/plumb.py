# -*- coding: utf-8 -*-
"""GENERIC plumb census: read the PDF char stream, find the body column,
count LITERAL LEADING SPACES at that column.

The signal (phase 1): a paragraph opener is ONE leading space at the body
column; display gathā sit at THREE.  pdfplumber's x0 alone shows nothing --
the indent is spaces in the text stream.  Block quotations are a separate
text block at x0 > body and are removed by the x0 filter.

Nothing here is hardcoded per volume: the body column is MEASURED as the
modal first-char x0 over all body lines of the volume.

Writes _xc/reseg2/plumb_<VOL>.json = {raw_pdf_page: [[lead, text], ...]}
and prints the census.
"""
import sys, os, json, collections, re
sys.path.insert(0, os.path.abspath('_xc/reseg'))
import pline
import pdfplumber

VOL = sys.argv[1]
OUT = '_xc/reseg2/plumb_%s.json' % VOL


def rows_of(page):
    r = collections.defaultdict(list)
    for ch in page.chars:
        r[round(ch['top'], 0)].append(ch)
    out = []
    for t in sorted(r):
        cs = sorted(r[t], key=lambda c: c['x0'])
        tx = ''.join(c['text'] for c in cs)
        if not tx.strip():
            continue
        out.append((round(cs[0]['x0'], 1), tx))
    return out


pdf = pline.pdf_of(VOL)
pl = pdfplumber.open(pdf)
allrows = []
for i in range(len(pl.pages)):
    ls = rows_of(pl.pages[i])
    # drop the running header (first row) and everything from the footnote rule down
    cut = next((k for k, (x, t) in enumerate(ls) if t.strip().startswith('_________')), len(ls))
    allrows.append(ls[1:cut])
pl.close()

# --- measure the body column: the modal first-char x0 over all body rows ---
xc = collections.Counter()
for ls in allrows:
    for x, t in ls:
        xc[x] += 1
BODY_X, bodyn = xc.most_common(1)[0]
print('%s  body column x0 = %.1f  (%d of %d rows, %.1f%%)'
      % (VOL, BODY_X, bodyn, sum(xc.values()), 100.0 * bodyn / sum(xc.values())))
print('   next columns:', [(x, n) for x, n in xc.most_common(6)[1:]])

out = {}
lead = collections.Counter()
for i, ls in enumerate(allrows, 1):
    keep = [[len(t) - len(t.lstrip()), t.strip()] for x, t in ls if abs(x - BODY_X) <= 0.5]
    out[str(i)] = keep
    for l, t in keep:
        lead[l] += 1
json.dump({'body_x': BODY_X, 'pages': out}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)

tot = sum(lead.values())
print('   leading-space census at the body column (%d rows):' % tot)
for l in sorted(lead):
    if lead[l] >= 5:
        print('      %2d space  %6d  %5.1f%%' % (l, lead[l], 100.0 * lead[l] / tot))
op = lead[1]
cont = lead[0]
print('   OPENERS (1 space) = %d   BODY (0 space) = %d   gathā (3 space) = %d' % (op, cont, lead[3]))
print('   MEAN LINES PER OPENER = %.2f   <-- prose mode if >= 4, verse if ~1-2' % ((cont + op) / max(1, op)))
