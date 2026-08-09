#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE GLYPH VISUAL REVIEW SHEET — every unresolved census glyph beside its
printed page.

WHY.  E021 (2026-08-09) was a register candidate whose guessed correction was
wrong twice — the register said delete, the session said `( )` — and the
printed page said neither: the x is the EDITION'S OWN position siglum.  The
guess was only settled by rendering the page at the exact site.  59 register
entries still stand on the same kind of guess.  This sheet prepares that
evidence once, for all of them, so the reader can judge each site the way
E021 was judged.

WHAT.  For every register entry still status=candidate, plus every census
sidecar / _vocab candidate not already in the register, locate the site in
the volume's PDF and render a clip of the printed line.  One static HTML
sheet, three-way verdict per row (misprint / edition's mark / unclear), an
Export button that serialises the verdicts to JSON for the reader to hand
back.  Nothing here writes to the register — the sheet GATHERS judgments,
it does not apply them (working principles 2 and 3).

THE E021 LESSON IS BUILT IN: the first page-match is not trusted.  Every
page whose text carries the context is rendered (capped at 3), and the
sheet shows them all with their header line, so a repeated formula cannot
silently substitute its twin.

Usage:  python3 pipeline/build_glyph_review.py
Output: _review/glyph_review.html, _review/clips/*.png, _review/report.json
"""
import json, os, re, sys, glob, html, unicodedata

try:
    import pymupdf as fitz
except ImportError:
    import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = '_review'
FOLDERS = ('pali-unicode', 'atthakatha-unicode', 'tika-unicode')


def pdf_path(vol):
    for f in FOLDERS:
        p = os.path.join(f, vol + '.pdf')
        if os.path.exists(p):
            return p
    return None


def collect():
    """Register candidates + sidecar/_vocab extras, deduped by (vol, glyph,
    context core)."""
    sites, seen = [], set()
    reg = json.load(open('data/errata.json', encoding='utf-8'))
    for e in reg['entries']:
        # EVERY register entry claims its (vol, glyph) — a confirmed or
        # resolved entry must not resurface from a sidecar as an X-row
        # (X002/X008 did exactly that on the first run).
        seen.add((e['volume'], e.get('glyph')))
        if e.get('status') != 'candidate':
            continue
        if not (isinstance(e.get('glyph'), str) and len(e['glyph']) == 1):
            # page-number entries (E063/E064/E066) and the homage variants
            # (E068–E077) carry no glyph: different classes, already
            # adjudicated at their printed pages — not this sheet's work.
            continue
        sites.append({'key': e['id'], 'vol': e['volume'], 'glyph': e.get('glyph'),
                      'printed': e.get('printed_page'), 'ctx': e.get('context') or '',
                      'sug': e.get('suggested_reading') or '', 'src': 'register',
                      'conf': e.get('confidence')})
    extra = []
    for f in sorted(glob.glob('corpus/*.errata.json')):
        vol = os.path.basename(f).split('.')[0]
        for i, r in enumerate(json.load(open(f, encoding='utf-8'))):
            extra.append((vol, r.get('ch'), r.get('ctx') or '',
                          'sidecar:%s' % r.get('type')))
    v = json.load(open('_vocab/glyph_erratum_candidates.json', encoding='utf-8'))
    for r in v['candidates']:
        extra.append((r['vol'], r['char'], r.get('context') or '', 'vocab'))
    n = 0
    for vol, ch, ctx, src in extra:
        if ch is None:
            # control-char sidecar rows carry no 'ch'; the character is in
            # the context.  One row per site, keyed by the context itself.
            m = re.search(r'[\x00-\x1f\x7f-\x9f]', ctx)
            ch = m.group(0) if m else None
        if (vol, ch) in seen and (vol, ch, ctx[:20]) in seen:
            continue
        if (vol, ch) in seen and not (ch and unicodedata.category(ch)[0] == 'C'):
            continue                     # register already holds this glyph
        seen.add((vol, ch)); seen.add((vol, ch, ctx[:20]))
        n += 1
        sites.append({'key': 'X%03d' % n, 'vol': vol, 'glyph': ch,
                      'printed': None, 'ctx': ctx, 'sug': '', 'src': src,
                      'conf': None})
    return sites


def flat(s):
    return re.sub(r'\s+', ' ', s)


def needles(site):
    """Successively shorter search strings centred on the glyph.  The glyph
    itself is kept in the needle when it is printable — the PDF text layer
    carries the same corrupt byte the corpus does — and dropped when it is a
    control character."""
    ctx, g = flat(site['ctx']), site['glyph'] or ''
    printable = g and unicodedata.category(g)[0] != 'C'
    i = ctx.find(g) if g else -1
    out = []
    if i >= 0 and printable:
        for pre, post in ((18, 18), (12, 12), (8, 8), (4, 10), (10, 4)):
            out.append(ctx[max(0, i - pre):i + len(g) + post])
    if i >= 0:
        # GLYPH-FREE needles.  Two reasons: control characters never reach a
        # text layer, and pymupdf can decode a byte differently from the
        # pdftotext run the corpus came from (the 12DiT05/27Khu10 'q' sites
        # failed exactly there on the first run).
        out.append(ctx[max(0, i - 30):i])
        out.append(ctx[i + len(g):i + len(g) + 30])
    out.append(ctx[:28]); out.append(ctx[-28:])
    ctrl = re.compile(r'[\x00-\x1f\x7f-\x9f]')
    return [n.strip() for n in (ctrl.sub('', x) for x in out)
            if len(n.strip()) >= 10]


def header_line(page):
    for l in page.get_text().split('\n'):
        if l.strip():
            return l.strip()[:60]
    return ''


def main():
    os.makedirs(os.path.join(OUT, 'clips_b'), exist_ok=True)
    sites = collect()
    report, docs, pagecache = [], {}, {}
    for s in sites:
        p = pdf_path(s['vol'])
        row = dict(s, pdf=p, hits=[])
        if not p:
            row['fail'] = 'NO PDF'
            report.append(row); continue
        if p not in docs:
            docs[p] = fitz.open(p)
            pagecache[p] = [flat(pg.get_text()) for pg in docs[p]]
        doc, texts = docs[p], pagecache[p]
        pages, used = [], None
        for nd in needles(s):
            pages = [i for i, t in enumerate(texts) if nd in t]
            if pages:
                used = nd; break
        if not pages:
            row['fail'] = 'CONTEXT NOT FOUND IN PDF TEXT LAYER'
            report.append(row); continue
        for i in pages[:3]:
            pg = doc[i]
            rects = pg.search_for(used) or []
            for shorter in needles(s):
                if rects: break
                rects = pg.search_for(shorter) or []
            fn = '%s_%s_p%d.png' % (s['key'], s['vol'], i + 1)
            if rects:
                r = rects[0]
                clip = fitz.Rect(pg.rect.x0, max(pg.rect.y0, r.y0 - 34),
                                 pg.rect.x1, min(pg.rect.y1, r.y1 + 26))
            else:                        # page found, line not; show whole page
                clip = pg.rect
            pg.get_pixmap(matrix=fitz.Matrix(3, 3), clip=clip).save(
                os.path.join(OUT, 'clips_b', fn))
            row['hits'].append({'pdf_page': i + 1, 'header': header_line(pg),
                               'img': 'clips_b/' + fn, 'line_found': bool(rects)})
        row['needle'] = used
        report.append(row)
        print('%-6s %-10s %-3s pages %s' % (s['key'], s['vol'],
              'ok' if row['hits'] else '--', [h['pdf_page'] for h in row['hits']]))

    json.dump(report, open(os.path.join(OUT, 'report.json'), 'w',
              encoding='utf-8'), ensure_ascii=False, indent=1)

    R = []
    for row in report:
        g = row['glyph'] or ''
        cp = 'U+%04X' % ord(g) if len(g) == 1 else repr(g)
        ctx = html.escape(row['ctx'])
        if g and g in row['ctx']:
            ctx = ctx.replace(html.escape(g), '<mark>%s</mark>' % html.escape(g), 1)
        imgs = ''.join(
            '<figure><img src="%s"><figcaption>pdf p.%d — %s%s</figcaption></figure>'
            % (h['img'], h['pdf_page'], html.escape(h['header']),
               '' if h['line_found'] else ' — LINE NOT LOCATED, whole page shown')
            for h in row['hits'])
        if not row['hits']:
            imgs = '<p class="fail">%s</p>' % html.escape(row.get('fail', '?'))
        k = row['key']
        R.append("""<section id="%s"><h2>%s — %s · printed p.%s · glyph <code>%s</code> %s · %s</h2>
<p class="ctx">…%s…</p><p class="sug">register suggests: <b>%s</b>%s</p>%s
<p class="verdict">
<label><input type="radio" name="%s" value="misprint"> misprint — confirm correction</label>
<label><input type="radio" name="%s" value="edition-mark"> edition's own mark — preserve</label>
<label><input type="radio" name="%s" value="unclear"> unclear</label>
<input type="text" name="%s_note" placeholder="note / corrected reading"></p></section>"""
            % (k, k, row['vol'], row.get('printed') or '?', html.escape(g), cp,
               row['src'], ctx, html.escape(row['sug']) or '(delete?)',
               ' · confidence %s' % row['conf'] if row['conf'] else '',
               imgs, k, k, k, k))
    page = """<!doctype html><meta charset="utf-8"><title>Glyph review — %d sites</title>
<style>body{font:15px/1.5 Georgia,serif;max-width:920px;margin:2em auto;padding:0 1em}
section{border-top:1px solid #ccc;padding:1em 0}h2{font-size:15px}
img{max-width:100%%;border:1px solid #ddd}figcaption{font:12px system-ui;color:#666}
mark{background:#ffb3b3;font-weight:bold}.fail{color:#b00;font-weight:bold}
.ctx{background:#f6f6f6;padding:.5em}.verdict label{margin-right:1.2em}
input[type=text]{width:60%%}textarea{width:100%%;height:10em}</style>
<h1>Glyph visual review — %d sites, generated by pipeline/build_glyph_review.py</h1>
<p>Every unresolved census glyph beside the printed page.  Where several pages
carry the same context, ALL are shown (the E021 lesson: the first page-match is
not the right page-match).  Verdicts export below; nothing is applied from here.</p>
%s
<h2>Export</h2><button onclick="ex()">Export verdicts to JSON</button>
<textarea id="out"></textarea>
<script>function ex(){const o={};document.querySelectorAll('section').forEach(s=>{
const k=s.id;const v=s.querySelector('input[type=radio]:checked');
const n=s.querySelector('input[type=text]').value;
if(v||n)o[k]={verdict:v?v.value:null,note:n||null}});
document.getElementById('out').value=JSON.stringify(o,null,1)}</script>
""" % (len(report), len(report), '\n'.join(R))
    open(os.path.join(OUT, 'glyph_review.html'), 'w', encoding='utf-8').write(page)
    ok = sum(1 for r in report if r['hits'])
    print('\n%d sites, %d located, %d not; sheet at _review/glyph_review.html'
          % (len(report), ok, len(report) - ok))


if __name__ == '__main__':
    main()
