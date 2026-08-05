# -*- coding: utf-8 -*-
"""BLOCK-BOUNDARY MAP: where the printed page starts a new block.

The separator is not one constant.  Measured over all 118 volumes, it is EITHER
a ~6.0pt space-before (112 volumes' commonest gap) OR a whole skipped line
(gap == 2x the body leading), and which is used varies by volume and by context:
20Khu03 sets 15.5 within a couplet and 31.0 between stanzas, 29Abhi01 sets 16.1
within a paragraph and 32.3 between.  So this does NOT look for 6.0.

The rule needs no constant at all:

    a new block begins wherever the leading exceeds THAT PAGE's own body
    leading by more than 3.0pt

which catches the 6.0pt space, the skipped line, and the heading gap alike, and
is measured per page exactly as `display_column_pages` measures its column.

Line y is the MODAL word y (a superscript footnote marker has a smaller yMin and
pulled whole lines up by ~0.9pt before this was fixed).

Output per volume: {page: {"body": leading, "lines": [[y, x, is_start, text],...]}}
"""
import sys, os, json, re, collections, subprocess, time

WORD = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', re.S)
PAGE = re.compile(r'<page width="[\d.]+" height="[\d.]+">(.*?)</page>', re.S)
TAG = re.compile(r'<[^>]+>')
THRESH = 3.0
OUT = '_xc/hy1/blocks'


def vol_pages(pdf):
    x = subprocess.run(['pdftotext', '-bbox', pdf, '-'], capture_output=True)
    return PAGE.findall(x.stdout.decode('utf-8', 'replace'))


def lines_of(body):
    g = collections.defaultdict(list)
    for m in WORD.finditer(body):
        g[round(float(m.group(2)), 1)].append((float(m.group(1)), TAG.sub('', m.group(5))))
    rows = []
    for y in sorted(g):
        w = sorted(g[y])
        if rows and y - rows[-1][0] < 3.0:
            rows[-1][3].extend([y] * len(w))
            rows[-1][1] = min(rows[-1][1], w[0][0])
            rows[-1][2] += ' ' + ' '.join(t for _, t in w)
        else:
            rows.append([y, w[0][0], ' '.join(t for _, t in w), [y] * len(w)])
    return [(collections.Counter(ys).most_common(1)[0][0], x0, t) for y, x0, t, ys in rows]


def main():
    os.makedirs(OUT, exist_ok=True)
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 400
    vols = []
    for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith('.pdf'):
                    vols.append((f[:-4], d + '/' + f))
    t0 = time.time()
    n = 0
    for vol, src in vols:
        dst = '%s/%s.json' % (OUT, vol)
        if os.path.exists(dst):
            continue
        if time.time() - t0 > budget:
            print('BUDGET'); break
        out, stats = {}, collections.Counter()
        for pi, body in enumerate(vol_pages(src), 1):
            rows = lines_of(body)
            if len(rows) < 4:
                continue
            L = [round(rows[i][0] - rows[i - 1][0], 1) for i in range(1, len(rows))]
            Lb = [g for g in L if 5 < g < 80]
            if len(Lb) < 4:
                continue
            base = collections.Counter(Lb).most_common(1)[0][0]
            marks, starts = [], 0
            for i, (y, x0, t) in enumerate(rows):
                st = 1 if i == 0 or (rows[i][0] - rows[i - 1][0]) > base + THRESH else 0
                starts += st
                marks.append([y, round(x0, 1), st, t])
            out[pi] = {'body': base, 'lines': marks}
            stats['pages'] += 1; stats['starts'] += starts; stats['lines'] += len(rows)
        json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
        n += 1
        print('%-10s pages %4d  lines %6d  block starts %5d (%.1f%%)'
              % (vol, stats['pages'], stats['lines'], stats['starts'],
                 100.0 * stats['starts'] / max(1, stats['lines'])), flush=True)
    print('volumes written this run: %d ; total %d' % (n, len(os.listdir(OUT))))


main()
