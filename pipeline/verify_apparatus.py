#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the VARIANT APPARATUS (footnotes) against the printed page.

`pipeline/verify_render_vs_pdf.py` diffs the reading body only.  It never reads
`apparatus/<VOL>.appk.json` or the `app` arrays inside uddāna blocks, so 68,412
stored footnotes across 118 volumes had never been compared to the pages they
come from.  That is not a small gap: the apparatus records what the Sinhalese,
Thai, Cambodian and PTS editions read differently, and is arguably the most
valuable single output of the project.

Each printed page carries its notes below a long underscore rule, frequently set
in TWO COLUMNS.  This script collects that block for every page in range, and
compares it against the stored notes in both directions:

  REVERSE  every stored note must appear CONTIGUOUSLY in the printed footnote
           text of the volume.  A miss means the note was spliced together from
           material that is not adjacent on the page — e.g. 18Khu01 ord512,
           where one stored note merges a footnote from page 100 with a
           different footnote from page 99 (and drops a verse out of it).

  FORWARD  every printed note must appear among the stored notes.  A miss is a
           variant reading the reader simply does not show.

Matching is on normalised word sequences, reusing the body harness's `norm` and
`WordIndex`, so the two tools agree about spelling, peyyala and hyphenation.

Usage:
  python3 pipeline/verify_apparatus.py <VOL> [p0 p1] [--max N] [--quiet]
  python3 pipeline/verify_apparatus.py --all [--budget SECONDS] [--out FILE]
                                            [--cache DIR]
"""
import json, os, re, sys, time, subprocess, importlib.util
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import fnblock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_s = importlib.util.spec_from_file_location('vr', f'{ROOT}/pipeline/verify_render_vs_pdf.py')
vr = importlib.util.module_from_spec(_s); _s.loader.exec_module(vr)
norm, WordIndex = vr.norm, vr.WordIndex


def page_range(vol):
    """pdftotext INDEX range of the volume's pages, via the measured offset.

    Using `pdf_page` directly as an index skipped 19Khu02's first page of
    footnotes entirely, so its two notes there were reported as splices —
    the harness was looking at the wrong page, not the apparatus at the wrong
    text."""
    d = json.load(open(f'{ROOT}/site/{vol}.json', encoding='utf-8'))
    pp = [p['pdf_page'] for p in d['paragraphs'] if p.get('pdf_page')]
    if not pp:
        return (0, 0)
    # One page of MARGIN at the low end.  The offset is measured from body text,
    # and a volume whose first paragraph was hand-inserted (18Khu01's Saraṇattaya)
    # can carry a page anchor that does not match the rest, so a hard low bound
    # can still clip the first footnote page.  The window only GATHERS printed
    # cells, so erring wide is safe; erring narrow reports real notes as splices.
    off = vr.page_offset(vol, d['paragraphs'])
    return (max(0, min(pp) + off - 1), max(pp) + off + 4)


def printed_notes(vol, p0, p1):
    """(joined footnote text, [cells]) for the volume's page range.

    A footnote block is everything below the first long underscore rule on a
    page.  `-layout` is required because the block is often two-column; cells
    are split on runs of three or more spaces.
    """
    pages = subprocess.run(['pdftotext', '-layout', vr.pdf_path(vol), '-'],
                           capture_output=True, text=True).stdout.split('\f')
    stream, cells = [], []
    for pi in range(p0, min(p1, len(pages) - 1) + 1):
        lines = pages[pi].split('\n')
        k = next((i for i, l in enumerate(lines) if re.match(r'^\s*_{10,}', l)), None)
        if k is None:
            # ...unless the rule is a GRAPHIC, in which case there is no line to
            # find and this returned nothing for the page.  That made the gate
            # DOUBLY wrong once the notes were recovered: the fourteen affected
            # pages' cells were absent from the printed side, so every note
            # rebuilt from them was reported SPLICED — 13 in 05Vin05 and 3 in
            # 03Vin03 — while the `printed cells` total stayed at the old
            # figure.  See pipeline/fnblock.py.
            st = fnblock.fn_start(lines)
            if st is None:
                continue
            k = st - 1
        for l in lines[k + 1:]:
            if not l.strip() or re.match(r'^\s*_{10,}', l):
                continue
            for cell in re.split(r'\s{3,}', l.strip()):
                cell = cell.strip()
                if cell:
                    cells.append((pi, cell))
                    stream.append(cell)
    return ' '.join(stream), cells


def stored_notes(vol):
    """[(ord, n, text)] from the apparatus file and from uddāna blocks."""
    out = []
    p = f'{ROOT}/site/reader/apparatus/{vol}.appk.json'
    if os.path.exists(p):
        for o, arr in json.load(open(p, encoding='utf-8')).items():
            for a in arr:
                if a.get('text'):
                    out.append((o, a.get('n'), a['text']))
    x = f'{ROOT}/site/reader/xrefs/{vol}.json'
    if os.path.exists(x):
        for o, lines in json.load(open(x, encoding='utf-8')).items():
            for l in lines:
                out.append((o, None, l))
    u = f'{ROOT}/site/reader/uddana/{vol}.json'
    if os.path.exists(u):
        for o, blocks in json.load(open(u, encoding='utf-8')).items():
            for b in blocks:
                for a in b.get('app', []):
                    if a.get('text'):
                        out.append((o, a.get('n'), a['text']))
    return out


def verify(vol, p0=None, p1=None, quiet=False, cap=25):
    if p0 is None:
        p0, p1 = page_range(vol)
    joined, cells = printed_notes(vol, p0, p1)
    stored = stored_notes(vol)
    pidx = WordIndex(norm(joined))
    sidx = WordIndex(' '.join(norm(t) for _, _, t in stored))

    spliced = []
    for o, n, t in stored:
        q = norm(t)
        if len(q.split()) < 2 or q in pidx:
            continue
        w = q.split(); a, b = 0, len(w)
        while a < b:
            mid = (a + b + 1) // 2
            if ' '.join(w[:mid]) in pidx: a = mid
            else: b = mid - 1
        spliced.append((o, n, a, len(w), ' '.join(w[max(0, a - 4):a + 6])))

    # A printed cell is either a numbered VARIANT note ("3. Aṭṭhī (Syā, Kaṁ)") or a
    # starred CROSS-REFERENCE ("* Khu 2. 129 piṭṭhe Petavatthumhipi.").  They are
    # different kinds of loss and want different fixes, so count them apart.
    missing, missing_xref = [], []
    for pi, c in cells:
        q = norm(c)
        if len(q.split()) < 3 or q in sidx:
            continue
        (missing_xref if re.match(r'^[*+]', c.strip()) else missing).append((pi, c))

    print(f'{vol} apparatus: stored {len(stored):5d} | printed cells {len(cells):5d} '
          f'| spliced {len(spliced):4d} | variants-not-stored {len(missing):4d} '
          f'| xrefs-not-stored {len(missing_xref):4d}')
    if not quiet:
        for o, n, a, ln, ctx in spliced[:cap]:
            print(f'   SPLICED   : ord{o} note {n} diverges at word {a}/{ln}: …{ctx}…')
        for pi, c in missing[:cap]:
            print(f'   VARIANT-LOST : p{pi}: {c[:95]}')
        for pi, c in missing_xref[:cap]:
            print(f'   XREF-LOST    : p{pi}: {c[:95]}')
        for name, lst in (('spliced', spliced), ('variants', missing), ('xrefs', missing_xref)):
            if len(lst) > cap:
                print(f'   … {len(lst) - cap} more {name} suppressed')
    return spliced, missing, missing_xref


def main():
    a = sys.argv[1:]
    cap = int(a[a.index('--max') + 1]) if '--max' in a else 25
    quiet = '--quiet' in a
    if '--all' in a:
        out = a[a.index('--out') + 1] if '--out' in a else f'{ROOT}/docs/apparatus_report.md'
        budget = float(a[a.index('--budget') + 1]) if '--budget' in a else 1e9
        # !!! THE CACHE WAS KEYED ON EXISTENCE ALONE, AND ITS PATH WAS FIXED.
        # `verify_all_volumes.py` at least re-checks a volume whose data is
        # newer than its cache entry; this one did not, so a stale
        # /tmp/osbct/appcache — 118 entries from an earlier session, which is
        # exactly what was found there on 2026-07-26x — would be reused whole
        # and the report rewritten from old measurements in under a second.
        # That is the same trap this file's own handoff records twice for the
        # body sweep.  Now: `--cache DIR` for parity, and an entry is STALE if
        # any of that volume's own inputs is newer than it.
        cache = a[a.index('--cache') + 1] if '--cache' in a else \
            f'{ROOT}/_appcache'
        os.makedirs(cache, exist_ok=True)

        def fresh(cf, vol):
            if not os.path.exists(cf):
                return False
            t = os.path.getmtime(cf)
            for p in (f'{ROOT}/site/{vol}.json',
                      f'{ROOT}/site/reader/apparatus/{vol}.appk.json',
                      f'{ROOT}/site/reader/xrefs/{vol}.json',
                      f'{ROOT}/site/reader/uddana/{vol}.json',
                      f'{ROOT}/pali-unicode/{vol}.pdf',
                      f'{ROOT}/pipeline/verify_apparatus.py',
                      f'{ROOT}/pipeline/verify_render_vs_pdf.py'):
                if os.path.exists(p) and os.path.getmtime(p) > t:
                    return False
            return True

        man = json.load(open(f'{ROOT}/site/reader/manifest.json', encoding='utf-8'))['volumes']
        rows, t0 = [], time.time()
        for i, v in enumerate(sorted(man), 1):
            cf = f'{cache}/{v}.json'
            if fresh(cf, v):
                rows.append(json.load(open(cf, encoding='utf-8'))); continue
            if time.time() - t0 > budget:
                print(f'-- budget reached, {len(man) - i + 1} left; re-run to continue'); break
            sp, ms, mx = verify(v, quiet=True)
            r = [v, man[v]['layer'], len(stored_notes(v)), len(sp), len(ms), len(mx),
                 [list(x) for x in sp[:4]], [list(x) for x in ms[:4]], [list(x) for x in mx[:3]]]
            json.dump(r, open(cf, 'w', encoding='utf-8'), ensure_ascii=False)
            rows.append(r)
        rows = [tuple(r) for r in rows]
        clean = [r for r in rows if r[3] == 0 and r[4] == 0 and r[5] == 0]
        with open(out, 'w', encoding='utf-8') as f:
            f.write('# Apparatus (variant-reading) verification report\n\n')
            f.write(f'`pipeline/verify_apparatus.py`, {len(rows)} volumes, '
                    f'{sum(r[2] for r in rows):,} stored footnotes.\n\n')
            f.write('`spliced` = a stored note that is NOT contiguous on the printed page '
                    '(merged from two notes, or fabricated). `not-stored` = a printed variant '
                    'the reader does not show.\n\n')
            f.write(f'**Clean: {len(clean)}/{len(rows)} volumes.**\n\n')
            f.write('| volume | layer | notes | spliced | variants lost | xrefs lost |\n'
                    '|---|---|---:|---:|---:|---:|\n')
            for v, lay, n, sp, ms, mx, _, _, _ in rows:
                f.write(f'| {v} | {lay} | {n} | {sp} | {ms} | {mx} |\n')
            f.write('\n## Samples\n')
            for v, lay, n, sp, ms, mx, xs, xm, xx in rows:
                if not (sp or ms or mx): continue
                f.write(f'\n### {v}\n')
                for o, nn, aa, ln, ctx in xs:
                    f.write(f'- spliced: ord{o} note {nn} diverges at word {aa}/{ln}: `{ctx}`\n')
                for pi, c in xm:
                    f.write(f'- variant lost: p{pi} `{str(c)[:120]}`\n')
                for pi, c in xx:
                    f.write(f'- xref lost: p{pi} `{str(c)[:120]}`\n')
        print(f'\nclean {len(clean)}/{len(rows)}  ->  {out}')
        return
    pos = [x for x in a if not x.startswith('--')]
    verify(pos[0], int(pos[1]) if len(pos) > 2 else None,
           int(pos[2]) if len(pos) > 2 else None, quiet=quiet, cap=cap)


if __name__ == '__main__':
    main()
