#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the render-vs-PDF harness over every volume in the manifest and emit a
per-volume mismatch report.

Page range per volume is taken from the corpus paragraphs' own `pdf_page`
anchors: [min(pdf_page), max(pdf_page)].  That deliberately excludes the
volume's front matter (mātikā / TOC, set in an ornamental font that does not
extract) and its back matter (word and verse indices), neither of which the
reader renders.  Where `pdf_page` is known to carry a fixed offset (12Sam01),
the range is still self-consistent because both ends shift together.

Canon volumes with side-maps (verse / sections / uddana) are checked as
rendered.  Commentary and sub-commentary volumes have no side-maps, so their
render is the corpus text alone and the diff is a corpus-integrity check.

Results are cached per volume, so the sweep is resumable: re-running picks up
where it stopped and only re-checks volumes whose cache entry is missing or
older than the volume's own data.  `--budget S` stops after S seconds so the
run fits inside a constrained shell timeout; just call it again to continue.

Usage:
  python3 pipeline/verify_all_volumes.py [--layer canon] [--vol 18Khu01 ...]
                                         [--minw 4] [--out docs/verify_report.md]
                                         [--cache DIR] [--budget SECONDS] [--force]
"""
import json, os, sys, io, re, time, subprocess, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('vr', f'{ROOT}/pipeline/verify_render_vs_pdf.py')
vr = importlib.util.module_from_spec(spec); spec.loader.exec_module(vr)


BACKMATTER = re.compile(r'anukkam|piṭṭhaṅk|nānāpāṭh|(gāthā|pada)sūci|sūciparicchedo', re.I)


def _bm(page):
    """Back matter is announced in a page's HEADING, not anywhere on it.

    Searching the whole page matched the word 'anukkamaṇika' inside an ordinary
    FOOTNOTE on 19Khu02's last text page (p451), so the tail extension stopped
    one page short and the volume's closing colophon 'Therīgāthāpāḷi niṭṭhitā.'
    was never compared.  Only the first few lines can announce back matter.
    """
    head = '\n'.join([l.strip() for l in page.split('\n') if l.strip()][:3])
    return bool(BACKMATTER.search(head))


# THE EDITION'S OWN PDFs DECLARE THEIR TEXT EXTENT, and nothing in this project
# had ever read it.  Every one of the 118 files carries it in the PDF `Subject`
# field — "[327 pages = content 19 + text 298 + index 10]" — in one of two
# wordings.  That is the publisher stating where the front matter ends and where
# the back-matter index begins, which is exactly what `page_range` below has
# been GUESSING from the corpus `pdf_page` anchors plus a back-matter marker.
#
# VALIDATED BEFORE BEING TRUSTED, against the eleven Khuddaka ranges this
# project measured by hand over ten sessions: the declared extent reproduces
# TEN of them exactly, and the eleventh differs only because the hand range ran
# one page past the end of 18Khu01's text onto a BLANK page (idx 480; the text
# ends at 479 and the index starts at 481).  So where it is available it is
# better than the guess, and it removes two standing caveats at once — the
# sweep's overshoot into 22Khu05's and 23Khu06's printed word index, and the
# inflated baselines that overshoot produced.
#
# SEVEN VOLUMES STATE IT DIFFERENTLY and two of those seven merge text and
# index into one figure ("[23 pages of content, 405 pages of text and index]",
# 01Vin01 and 02Vin02), so their tail cannot be taken from the metadata.  Those
# fall back to the measured method below, which is why it is kept.
_EXTENT_FORMS = [
    re.compile(r'content\s+(\d+)\s*(?:pages\s*)?\+\s*text\s+(\d+)'),
    re.compile(r'(\d+)\s+pages of content,\s*(\d+)\s+pages of text(?!\s+and\s+index)'),
]
_DECL = {}

# !!! AND THE METADATA IS NOT INFALLIBLE — 33Abhi05 IS THE FIRST VOLUME WHERE
# IT IS WRONG.  It declares "content 10 + text 265", i.e. 0-based 10-274, but
# 1-based page 11 carries the ROMAN folio "viii" and is the last page of the
# front mātikā: the front matter is ELEVEN pages, not ten.  The declared text
# LENGTH is right (265 pages) and the whole range is shifted by one, so the
# sweep was reading a mātikā page in as body text at the head and leaving the
# Saccayamaka's last printed unit, its "Pariññāvāro." and its
# "Saccayamakapāḷi niṭṭhitā." out at the tail — 4 lines and 3 reversed on a
# volume that reads 0/0/0/0 over its real extent.
#
# `build_khu_volume.SPEC` holds a HAND-MEASURED extent for every volume built
# from the printed page, and it is a second reading of the same question, so it
# is preferred where it exists rather than a table being typed here.  MEASURED
# BEFORE IT WAS TRUSTED: over the twenty volumes that SPEC covers it agrees
# with the metadata on nineteen and differs only on 33Abhi05.
_SPECR = {}
try:
    import importlib.util as _ilu2
    _s2 = _ilu2.spec_from_file_location('bkv', f'{ROOT}/pipeline/build_khu_volume.py')
    _bkv = _ilu2.module_from_spec(_s2); _s2.loader.exec_module(_bkv)
    for _v, _d in _bkv.SPEC.items():
        _bs = _d.get('books') or []
        if _bs:
            _SPECR[_v] = (min(b[1] for b in _bs) - 1, max(b[2] for b in _bs) - 1)
except Exception:
    _SPECR = {}


def declared_range(vol):
    """[first, last] 0-based pdftotext page from the PDF's own metadata, or None."""
    if vol not in _DECL:
        out = subprocess.run(['pdfinfo', vr.pdf_path(vol)],
                             capture_output=True, text=True).stdout
        m = re.search(r'^Subject: *(.*)$', out, re.M)
        subj = m.group(1) if m else ''
        _DECL[vol] = None
        for f in _EXTENT_FORMS:
            mm = f.search(subj)
            if mm:
                c, t = int(mm.group(1)), int(mm.group(2))
                _DECL[vol] = (c, c + t - 1)
                break
    return _DECL[vol]


def page_range(vol, tail=8):
    """[first, last] pdftotext page of the volume's main text.

    Lower bound = the first paragraph's own `pdf_page` anchor, which already
    excludes the front matter (mātikā / TOC, set in an ornamental font that
    does not extract as text and would otherwise flood the report).
    Upper bound = the last paragraph's page, extended by up to `tail` pages so
    the closing colophons and uddāna verses that sit past the final paragraph
    are covered, stopping before the back-matter indices.
    """
    d = json.load(open(f'{ROOT}/site/{vol}.json', encoding='utf-8'))
    npara = len(d['paragraphs'])
    dec = _SPECR.get(vol) or declared_range(vol)
    if dec:
        return dec[0], dec[1], npara
    pp = [p['pdf_page'] for p in d['paragraphs'] if p.get('pdf_page')]
    if not pp:
        return None, None, npara
    pages = subprocess.run(['pdftotext', vr.pdf_path(vol), '-'],
                           capture_output=True, text=True).stdout.split('\f')
    last = max(pp)
    for k in range(1, tail + 1):
        if last + 1 >= len(pages) - 1: break
        if _bm(pages[last + 1]): break
        last += 1
    # LOW BOUND — corpus `pdf_page` is the 1-based printed PDF page, but `pages`
    # is 0-indexed, so using it directly skipped each volume's FIRST TEXT PAGE:
    # the one carrying the book title, the "Namo tassa…" homage, the opening
    # headings and the first verses.  That page was therefore never compared in
    # any volume — the exact material the incipit/heading work is about.  Step
    # back one page when the preceding page is real body text (not front matter,
    # which is paginated in roman numerals, and not a back-matter index).
    first = min(pp)
    if first > 0:
        prev = pages[first - 1]
        head = '\n'.join([l.strip() for l in prev.split('\n') if l.strip()][:2])
        if head and not _bm(prev) \
           and not re.match(r'^[ivxlcdm]+\b', head, re.I):
            first -= 1
    return first, last, len(d['paragraphs'])


_NP = {}


def npages(vol):
    if vol not in _NP:
        try:
            o = subprocess.run(['pdfinfo', vr.pdf_path(vol)], capture_output=True, text=True).stdout
            _NP[vol] = int(re.search(r'Pages:\s+(\d+)', o).group(1))
        except Exception:
            _NP[vol] = 0
    return _NP[vol]


def main():
    a = sys.argv[1:]
    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default
    minw = int(opt('--minw', 4))
    out  = opt('--out', f'{ROOT}/docs/verify_report.md')
    layer = opt('--layer')
    man = json.load(open(f'{ROOT}/site/reader/manifest.json', encoding='utf-8'))['volumes']
    vols = a[a.index('--vol') + 1:] if '--vol' in a else sorted(man)
    if layer:
        vols = [v for v in vols if man[v]['layer'] == layer]

    cache = opt('--cache', '/tmp/osbct/verify_cache')
    budget = float(opt('--budget', 1e9))
    force = '--force' in a
    os.makedirs(cache, exist_ok=True)

    # !!! THE CACHE CHECK WAS EXISTENCE-ONLY, AND THIS FILE'S OWN DOCSTRING
    # CLAIMED OTHERWISE ("only re-checks volumes whose cache entry is missing or
    # older than the volume's own data").  It did no mtime comparison at all, so
    # re-running the sweep after REBUILDING a volume silently kept the old row:
    # 30Abhi02 was rebuilt on 2026-07-26y, re-swept, and still reported its
    # pre-rebuild 1/2/4 — the corpus file had not changed, only the SIDE-MAPS,
    # which is how every rebuild in this project works.  Now the entry is stale
    # if ANY input the render depends on is newer than it.
    def fresh(cf, vol):
        if not os.path.exists(cf):
            return False
        t = os.path.getmtime(cf)
        ps = [f'{ROOT}/site/{vol}.json', f'{ROOT}/pali-unicode/{vol}.pdf',
              f'{ROOT}/pipeline/verify_render_vs_pdf.py',
              f'{ROOT}/pipeline/verify_all_volumes.py']
        for d in ('verse', 'sections', 'uddana', 'hide', 'incipit', 'booktitle'):
            ps.append(f'{ROOT}/site/reader/{d}/{vol}.json')
        for p in ps:
            if os.path.exists(p) and os.path.getmtime(p) > t:
                return False
        return True

    rows, t0 = [], time.time()
    for i, vol in enumerate(vols, 1):
        cf = f'{cache}/{vol}.json'
        if not force and fresh(cf, vol):
            try:
                rows.append(tuple(json.load(open(cf, encoding='utf-8')))); continue
            except Exception:
                pass
        if time.time() - t0 > budget:
            print(f'-- budget reached, {len(vols) - i + 1} volumes left; re-run to continue',
                  flush=True)
            break
        try:
            p0, p1, n = page_range(vol)
            if p0 is None:
                rows.append((vol, man[vol]['layer'], n, None, None, 'no pdf_page anchors', None)); continue
            buf = io.StringIO(); old = sys.stdout; sys.stdout = buf
            try:
                fl, fc, rv, dp = vr.verify(vol, p0, p1, 0, n, minw, quiet=True)
            finally:
                sys.stdout = old
            rows.append((vol, man[vol]['layer'], n, (p0, p1),
                         (len(fl), len(fc), len(rv), len(dp)), None,
                         {'lines': fl[:8], 'chunks': fc[:8],
                          'rev': [f'ord{o} [{k}] @{x}/{y}: {c}' for o, k, x, y, c in rv[:8]],
                          'dup': [f'{c}x vs {p}x: {t[:70]}' for c, p, t in dp[:8]]}))
        except Exception as e:
            rows.append((vol, man.get(vol, {}).get('layer', '?'), None, None, None,
                         f'{type(e).__name__}: {e}', None))
        json.dump(rows[-1], open(cf, 'w', encoding='utf-8'), ensure_ascii=False)
        tot = rows[-1][4]
        print(f'[{i}/{len(vols)}] {vol:10s} '
              + (f'{tot[0]:6d} lines {tot[1]:5d} chunks {tot[2]:5d} rev {tot[3]:4d} dup'
                 if tot else f'-- {rows[-1][5]}'), flush=True)

    rows = [tuple(r) for r in rows]
    clean = [r for r in rows if r[4] and sum(r[4]) == 0]
    with open(out, 'w', encoding='utf-8') as f:
        f.write('# Render-vs-PDF verification report\n\n')
        f.write(f'Harness: `pipeline/verify_render_vs_pdf.py` (minw={minw}), '
                f'{len(rows)} volumes, {time.time()-t0:.0f}s.\n\n')
        f.write('`lines` / `chunks` = printed content missing from the render (drops). '
                '`rev` = rendered text that is not contiguous in the print '
                '(splices / fabrication). `dup` = rendered more often than printed.\n\n')
        f.write(f'**Clean (0/0/0/0): {len(clean)}/{len(rows)} volumes.**\n\n')
        f.write('`cover` = pages checked / pages in the PDF, and it has a CEILING WELL '
                'BELOW 100%: most volumes carry 60-100 pages of back matter (word, name '
                'and verse indices, Sodhanapattaṁ errata) plus front matter, none of which '
                'is body text.  19Khu02 is fully covered over its text and still reads 80%, '
                'because 96 of its 547 pages are indices.  So compare a volume\'s cover '
                'against ITS OWN text extent before reading it as lost extraction.  '
                'THE CHECKED RANGE IS NOW THE EXTENT THE PDF ITSELF DECLARES '
                'in its `Subject` metadata ("[327 pages = content 19 + text 298 + '
                'index 10]") — available for 116 of the 118 files, and validated '
                'against the eleven Khuddaka ranges this project measured by hand: '
                'it reproduces ten of them exactly and is one page tighter on the '
                'eleventh (18Khu01\'s tail page is blank).  01Vin01 and 02Vin02 '
                'merge text and index into one figure, so those two still fall back '
                'to the measured method.  A LOW cover therefore means the volume is '
                'mostly back matter, or that its extraction stopped short — read it '
                'against that volume\'s own text extent, not as a defect on its own.'
                '\n\n')
        f.write('| volume | layer | ¶ | pdf pages | cover | lines | chunks | rev | dup |\n')
        f.write('|---|---|---:|---|---:|---:|---:|---:|---:|\n')
        for vol, lay, n, pr, tot, err, _ in rows:
            if err:
                f.write(f'| {vol} | {lay} | {n or "-"} | - | - | ⚠ {err} | | | |\n')
            else:
                tp = npages(vol)
                cov = f'{100.0*(pr[1]-pr[0]+1)/tp:.0f}%' if tp else '?'
                f.write(f'| {vol} | {lay} | {n} | {pr[0]}–{pr[1]} | {cov} | '
                        f'{tot[0]} | {tot[1]} | {tot[2]} | {tot[3]} |\n')
        f.write('\n## Samples per volume (first 8 of each kind)\n')
        for vol, lay, n, pr, tot, err, ex in rows:
            if not ex or not tot or sum(tot) == 0:
                continue
            f.write(f'\n### {vol} ({lay})\n')
            for k, label in (('lines', 'missing from render (line)'),
                             ('chunks', 'missing from render (chunk)'),
                             ('rev', 'rendered but not contiguous in PDF'),
                             ('dup', 'rendered more often than printed')):
                if ex[k]:
                    f.write(f'\n*{label}*\n\n')
                    for s in ex[k]:
                        f.write(f'- `{str(s)[:150]}`\n')
    print(f'\nclean {len(clean)}/{len(rows)}  ->  {out}')


if __name__ == '__main__':
    main()
