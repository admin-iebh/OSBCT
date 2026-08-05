# -*- coding: utf-8 -*-
"""Line LEADING from the PDF's own coordinates, which is where the stanza break
actually lives.

`pdftotext -layout` does NOT emit a blank line between stanzas (proved on
20KhuA01 pdftotext p233: eight verse lines contiguous, while the page plainly
sets a gap after the fourth).  The gap is typographic leading, below the
threshold at which -layout breaks a line.  `pdftotext -bbox` gives every word's
y, and the leading is bimodal: within a block one value, at a block break a
larger one.  Nothing in this project reads it.
"""
import subprocess, re, collections, sys, os

WORD = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', re.S)


def page_lines(pdf, page):
    x = subprocess.run(['pdftotext', '-bbox', '-f', str(page), '-l', str(page), pdf, '-'],
                       capture_output=True).stdout.decode('utf-8', 'replace')
    ws = [(round(float(m.group(2)), 1), float(m.group(1)), re.sub(r'<[^>]+>', '', m.group(5)))
          for m in WORD.finditer(x)]
    g = collections.defaultdict(list)
    for y, x0, t in ws:
        g[y].append((x0, t))
    rows = []
    for y in sorted(g):
        w = sorted(g[y])
        if rows and y - rows[-1][0] < 3.0:
            rows[-1] = (rows[-1][0], min(rows[-1][1], w[0][0]),
                        rows[-1][2] + ' ' + ' '.join(t for _, t in w))
        else:
            rows.append((y, w[0][0], ' '.join(t for _, t in w)))
    return rows


def leads(rows):
    return [round(rows[i][0] - rows[i - 1][0], 1) for i in range(1, len(rows))]


if __name__ == '__main__':
    pdf, pages = sys.argv[1], [int(a) for a in sys.argv[2:]]
    for p in pages:
        rows = page_lines(pdf, p)
        L = leads(rows)
        body = [g for g in L if 5 < g < 60]
        c = collections.Counter(body)
        print('== %s p%d : %d lines' % (os.path.basename(pdf), p, len(rows)))
        print('   leading histogram: %s' % c.most_common(6))
        if c:
            base = c.most_common(1)[0][0]
            brk = sorted({g for g in body if g > base + 2})
            print('   body leading %.1f   break leadings %s' % (base, brk))
