#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scout a volume BEFORE writing anything for it.

Every volume built so far needed the same four measurements first, and they
have been hand-rolled as session scratch three times (33Abhi05, 34Abhi06,
35Abhi07).  They belong in the repo, so a later session does not start by
rewriting them — the same reason `regress.py` was moved here on 2026-07-26w.

    python3 pipeline/scout_volume.py <VOL> extent    # where the TEXT really is
    python3 pipeline/scout_volume.py <VOL> corpus    # n-runs, resets, book field
    python3 pipeline/scout_volume.py <VOL> geometry  # the printed page's shape
    python3 pipeline/scout_volume.py <VOL> pair      # WHERE printed and corpus differ
    python3 pipeline/scout_volume.py <VOL> page N…   # print pages, as read

NOTHING here decides anything; it reports what the page and the corpus say so
the SPEC can be written from measurements instead of from a hypothesis.
"""
import json, os, re, subprocess, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOM  = re.compile(r'Namo [Tt]assa Bhagavato Arahato Sammāsambuddhassa')
# the printed back matter always opens with the word index's own title
# !!! THE INDEX'S OWN TITLE IS NOT SPELT THE SAME IN EVERY VOLUME — 05Vin05
# heads it "Lakkhitabbānaṁ anukkamanikā", with a dental `n` where every other
# volume sets the retroflex `ṇ`, and 02Vin02 heads its own "Saṁvaṇṇitapadānaṁ
# anukkamaṇika" with a SHORT final `a`.  Spelt only one way, the scan walked
# past the index and put the text extent two pages long — on both volumes.
BACK = re.compile(r'anukkama[ṇn]ik[āa]\b|anukkamo\s', re.I)
_EXTENT = [
    re.compile(r'content\s+(\d+)\s*(?:pages\s*)?\+\s*text\s+(\d+)'),
    re.compile(r'(\d+)\s+pages of content,\s*(\d+)\s+pages of text(?!\s+and\s+index)'),
]



def _pdf(vol):
    """The volume's PDF, wherever it lives — canon, commentary or subcommentary.

    The same three-folder search `verify_render_vs_pdf.py` and
    `build_khu_volume.py` do.  `pali-unicode` is tried first, so every canon
    volume resolves exactly as before.
    """
    for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
        p = os.path.join(ROOT, d, vol + '.pdf')
        if os.path.exists(p):
            return p
    return os.path.join(ROOT, 'pali-unicode', vol + '.pdf')

def pages_of(vol):
    return subprocess.run(
        ['pdftotext', '-layout', _pdf(vol), '-'],
        capture_output=True, text=True).stdout.split('\f')


def lines_of(pg):
    return [l.rstrip() for l in pg.split('\n') if l.strip()]


def declared(vol):
    """(first, last) 1-based printed-PDF page from the metadata, or None.

    Deliberately refuses the two forms that MERGE text and index into one
    figure — 01Vin01 and 02Vin02 say "405 pages of text and index" — because a
    tail taken from those is wrong by the whole index.
    """
    out = subprocess.run(['pdfinfo', _pdf(vol)],
                         capture_output=True, text=True).stdout
    m = re.search(r'^Subject: *(.*)$', out, re.M)
    subj = m.group(1) if m else ''
    for f in _EXTENT:
        mm = f.search(subj)
        if mm:
            c, t = int(mm.group(1)), int(mm.group(2))
            return (c + 1, c + t), subj
    return None, subj


def cmd_extent(vol, pages):
    dec, subj = declared(vol)
    print('metadata: %s' % (subj or '(none)'))
    print('declared text extent (1-based): %s%s'
          % (dec, '' if dec else '   <<< NOT USABLE, text and index are one figure'))
    # the FIRST body page: the first page carrying a homage, else the first
    # page after the front matter that is not a mātikā page
    homs = [i for i in range(1, len(pages)) if HOM.search(pages[i - 1])]
    print('homage pages (1-based): %s' % homs)
    # the LAST body page: the page before the first back-matter page after it
    back = [i for i in range(1, len(pages))
            if BACK.search('\n'.join(lines_of(pages[i - 1])[:3]))]
    back = [i for i in back if not homs or i > homs[0]]
    # ...AND A BLANK LEAF BEFORE THE INDEX IS NOT TEXT.  03Vin03 closes
    # "Mahāvaggapāḷi niṭṭhitā." on p525 and leaves p526 blank; counted in, the
    # extent came out one page long.
    while back and not lines_of(pages[back[0] - 2]):
        back[0] -= 1
    print('back-matter candidates (1-based, by their own heading): %s' % back[:6])
    if homs and back:
        print('=> MEASURED text extent (1-based): %d-%d   body gate 0-based: %d %d'
              % (homs[0], back[0] - 1, homs[0] - 1, back[0] - 2))
    print()
    print('--- the folio on each candidate edge page ---')
    for i in [x for x in (homs[:1] + [homs[0] - 1] if homs else [])] + \
             ([back[0] - 1, back[0]] if back else []):
        if 1 <= i < len(pages):
            print('  p%-4d %r' % (i, (lines_of(pages[i - 1]) or [''])[0][:96]))


def cmd_corpus(vol, pages):
    paras = json.load(open(os.path.join(ROOT, 'site', vol + '.json'),
                           encoding='utf-8'))['paragraphs']
    print('corpus paragraphs: %d' % len(paras))
    ns = [(o, p.get('n')) for o, p in enumerate(paras) if isinstance(p.get('n'), int)]
    print('numbered paragraphs: %d of %d' % (len(ns), len(paras)))
    prev, resets = None, []
    for o, n in ns:
        if prev is not None and n <= prev:
            resets.append((o, prev, n, (paras[o].get('text') or '')[:58]))
        prev = n
    print('n ends at %s | resets: %d' % (prev, len(resets)))
    for r in resets[:40]:
        print('   ord%-6d %s -> %s   %r' % r)
    if len(resets) > 40:
        print('   ... %d more' % (len(resets) - 40))
    print('book field runs:')
    seen = []
    for o, p in enumerate(paras):
        b = p.get('book')
        if b and (not seen or seen[-1][1] != b):
            seen.append((o, b))
    for o, b in seen[:40]:
        print('   ord%-6d %s' % (o, b))
    if len(seen) > 40:
        print('   ... %d more' % (len(seen) - 40))


def cmd_geometry(vol, pages, p0=None, p1=None):
    """What the printed page looks like — indents, numbered lines, display."""
    dec, _ = declared(vol)
    homs = [i for i in range(1, len(pages)) if HOM.search(pages[i - 1])]
    p0 = int(p0) if p0 else (homs[0] if homs else (dec[0] if dec else 1))
    p1 = int(p1) if p1 else (dec[1] if dec else len(pages) - 1)
    ind = collections.Counter()
    numbered = collections.Counter()
    disp_com = 0
    disp = 0
    for pg in range(p0, p1 + 1):
        for l in lines_of(pages[pg - 1])[1:]:      # drop the running header
            i = len(l) - len(l.lstrip())
            t = l.strip()
            ind[i] += 1
            if re.match(r'^\d+(?:-\d+)?\.\s', t):
                numbered[i] += 1
            if i >= 8:
                disp += 1
                if ',' in t:
                    disp_com += 1
    print('pages %d-%d' % (p0, p1))
    print('line indents (count):')
    for i in sorted(ind):
        if ind[i] >= 20 or numbered[i]:
            print('   %2d : %6d lines %s' % (i, ind[i],
                  ('  (%d numbered)' % numbered[i]) if numbered[i] else ''))
    print('lines at indent >= 8: %d, of which %d carry a comma' % (disp, disp_com))
    print('   -> `no_verse` is arguable only if that second figure is 0')


def cmd_page(vol, pages, *nums):
    for s in nums:
        for pg in ([int(s)] if '-' not in s
                   else range(int(s.split('-')[0]), int(s.split('-')[1]) + 1)):
            print('=== 1-based page %d ===' % pg)
            for l in lines_of(pages[pg - 1]):
                print('   %2d %r' % (len(l) - len(l.lstrip()), l.strip()[:104]))


def cmd_pair(vol, pages, *_):
    """Align the PRINTED numbered-unit stream against the corpus, book by book,
    and NAME every divergence with its page.  A count alone says a book does
    not pair; this says WHERE, which is the only thing that can be acted on."""
    import difflib, importlib.util as ilu
    sp = ilu.spec_from_file_location('bkv', os.path.join(ROOT, 'pipeline',
                                                         'build_khu_volume.py'))
    B = ilu.module_from_spec(sp); sp.loader.exec_module(B)
    B.use(vol)
    pg = B.pdf_pages()
    paras = json.load(open(os.path.join(ROOT, 'site', vol + '.json'),
                           encoding='utf-8'))['paragraphs']
    for bk in B.BOOKS:
        title, q0, q1, o0, o1 = bk[:5]
        items = B.kat_items(pg, q0, q1)
        printed = [it for it in items if it[0] in ('unit', 'uverse')]
        hs = [B.split_centre(it[1].strip()) for it in items if it[0] == 'head']
        hs = [x for parts in hs for x in parts]
        runs = set()
        for a in range(len(hs)):
            acc = ''
            for b in range(a, min(a + 3, len(hs))):
                acc = (acc + ' ' + hs[b]).strip()
                runs.add(re.sub(r'\s+', ' ', acc))
        hide = set()
        for o in range(o0, o1):
            raw = (paras[o].get('text') or '').strip()
            t = B.head_body(re.sub(r'^\d+(?:-\d+)?\.\s*', '', raw))
            if (B.kat_is_head(t, printed=False) or B._is_double_head(raw)
                    or B._starts_double_head(raw)
                    or re.sub(r'\s+', ' ', raw) in runs
                    or raw in B.SPEC[vol].get('headfix', ())):
                hide.add(o)
        ords = [o for o in range(o0, o1) if o not in hide]
        print('=' * 76)
        print('%-24s pp %d-%d  ord %d-%d   printed %d / corpus %d'
              % (title, q0, q1, o0, o1, len(printed), len(ords)))
        a = [it[1] for it in printed]
        b = [paras[o].get('n') for o in ords]
        if len(a) == len(b):
            bad = [(k, a[k], b[k]) for k in range(len(a)) if a[k] != b[k]]
            print('   pairs 1:1; n-mismatches: %d' % len(bad))
            for k, x, y in bad[:12]:
                print('     pos %d printed %s corpus %s  (p%s)'
                      % (k, x, y, printed[k][3]))
            continue
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
                a=a, b=b, autojunk=False).get_opcodes():
            if tag == 'equal':
                continue
            print('  %-7s printed[%d:%d]=%s  corpus[%d:%d]=%s'
                  % (tag, i1, i2, a[i1:i2], j1, j2, b[j1:j2]))
            for k in range(i1, i2):
                print('     PRINTED n=%s p%s  %r'
                      % (printed[k][1], printed[k][3], printed[k][2][:88]))
            for k in range(j1, j2):
                print('     CORPUS  ord%d n=%s  %r'
                      % (ords[k], paras[ords[k]].get('n'),
                         (paras[ords[k]].get('text') or '')[:88]))


if __name__ == '__main__':
    vol, what = sys.argv[1], sys.argv[2]
    pgs = pages_of(vol)
    {'extent': cmd_extent, 'corpus': cmd_corpus, 'pair': cmd_pair,
     'geometry': cmd_geometry, 'page': cmd_page}[what](vol, pgs, *sys.argv[3:])
