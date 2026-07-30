#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild 19Khu02's reader side-maps DIRECTLY FROM THE PRINTED PDF.

19Khu02 = Vimānavatthu + Petavatthu + Theragāthā + Therīgāthā.

THE GOVERNING LESSON (HANDOFF.md): side-maps built by SPLITTING THE CORPUS TEXT
inherit every corpus defect.  This parses `pdftotext -layout` of the printed
edition into an item stream (heading / numbered verse + its printed pāda lines /
prose / colophon / uddāna) and maps it onto corpus ordinals BY VERSE NUMBER.
The corpus (site/19Khu02.json) is never touched — the reader renders
`before + groups + after` from the side-map whenever a verse entry exists, so the
side-map alone controls what is shown.

Corpus defects this repairs, all found by verify_render_vs_pdf.py:
  * dropped printed pāda lines inside a verse (e.g. v1094 loses "Sukuṇḍalī
    kappitakesamassu.", v1098 loses "Bahussute taṇhakkhayūpapanne.");
  * vagga uddāna verses SPLICED onto the tail of the vagga's last paragraph
    (ord155/269/482/631/692) while the same text also renders from uddana/ —
    so it showed twice, once in the wrong role;
  * every Tassuddānaṁ / Tatruddānaṁ and every sutta- and vagga-end colophon of
    Petavatthu, Theragāthā and Therīgāthā missing outright;
  * Theragāthā's opening Nidānagāthā missing outright;
  * three printed section headings captured as corpus paragraphs (ord 388, 390,
    857) — hidden here and re-placed as headings;
  * no verse structure at all: every verse rendered as run-on prose.

Writes: site/reader/{verse,uddana,sections,hide,incipit}/19Khu02.json
Backups: *.pre19build
"""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R    = os.path.join(ROOT, 'site/reader')
VOL  = '19Khu02'
PDF  = os.path.join(ROOT, 'pali-unicode', VOL + '.pdf')

# (title, pdf_first, pdf_last, ord_lo, ord_hi, last_verse) — see docs/19Khu02_structure.json
BOOKS = [('Vimānavatthupāḷi', 17, 141,    0, 1034, 1289),
         ('Petavatthupāḷi',  143, 234, 1034, 1848,  814),
         ('Theragāthāpāḷi',  235, 391, 1848, 3136, 1288),
         ('Therīgāthāpāḷi',  393, 451, 3136, 3660,  524)]

FNRULE = re.compile(r'^\s*_{20,}\s*$')
DECOR  = re.compile(r'^\s*_{3,19}\s*$')
VERSE  = re.compile(r'^(\d+)\.\s*(.*)$')
HOMAGE = re.compile(r'Namo tassa Bhagavato Arahato Sammāsambuddhassa')
UDDLBL = re.compile(r'^(Tassuddānaṁ|Tatruddānaṁ|Atha vagguddānaṁ|Vagguddānaṁ|'
                    r'[A-ZĀĪŪṄÑṆṬḌḶ]\S*uddānaṁ|Nidānagāthā)\d*$')
# A NUMBERED line that is really a centred heading pushed into the body column.
# ("6. Gandhapañcaṅgulikadāyikāvimānavatthu" on p58 read as verse 6, colliding
#  with the real verse 6; the same shape leaked into the corpus at ord 388/390/857.)
HEADTXT = re.compile(r'^[A-ZĀĪŪṄÑṆṬḌḶ][^,]*'
                     r'(vimānavatthu|petavatthu|theragāthā|therīgāthā|vatthu|vimāna|vagga|nipāta)'
                     r'\d*\s*(\(\d+\))?$')
# A body-column line that OPENS a prose run.  Indent cannot decide this: the
# edition sets the closing formula "Itthaṁ sudaṁ … abhāsitthāti." flush with the
# verse number on one page and flush with the pādas on the next (p235 vs p236),
# so alignment is not authority.  Classify by form and render it consistently as
# prose; the run then continues until the next verse number or centred line.
PROSEOPEN = re.compile(r'^(Itthaṁ sudaṁ|\(|“|Idha bhante|Evaṁ me sutaṁ)')
DIVISION = re.compile(r'(itthivimāna|purisavimāna)$', re.I)
NIPATA   = re.compile(r'nipāta\d*$', re.I)
VAGGA    = re.compile(r'vagga\d*$', re.I)


def pdf_pages():
    txt = subprocess.run(['pdftotext', '-layout', PDF, '-'],
                         capture_output=True, text=True).stdout
    return txt.split('\f')


def page_lines(pages, i):
    out = []
    for l in (l.rstrip() for l in pages[i - 1].split('\n')):
        if FNRULE.match(l):
            break                                    # footnote block -> end of page
        if l.strip() and not DECOR.match(l):
            out.append(l)
    if out and (re.match(r'^\s*\d+\s{2,}\D', out[0]) or re.search(r'\s{3,}\d+\s*$', out[0])):
        out = out[1:]                                # running page-header
    return [(len(l) - len(l.lstrip()), l.strip()) for l in out]


def items_for(pages, p0, p1):
    """('centre',txt,pg) | ('verse',n,txt,pg) | ('pada',txt,pg) | ('prose',txt,pg)"""
    items = []
    for pg in range(p0, p1 + 1):
        lines = page_lines(pages, pg)
        if not lines:
            continue
        vind = [i for i, t in lines if VERSE.match(t) and i < 20]
        if not vind:
            # A page with no verse number on it is a colophon / uddāna page
            # (p234, p391).  There is no body column to measure against, so the
            # indent rule would call its uddāna lines body text — they are not.
            for ind, t in lines:
                items.append(('homage', t, pg) if HOMAGE.search(t) else ('centre', t, pg))
            continue
        body = min(vind)
        centred = body + 12
        prose_run = False
        for ind, t in lines:
            m = VERSE.match(t)
            if HOMAGE.search(t):
                items.append(('homage', t, pg)); prose_run = False
            elif ind >= centred:
                items.append(('centre', t, pg)); prose_run = False
            elif m and HEADTXT.match(m.group(2)):
                items.append(('centre', t, pg)); prose_run = False
            elif m:
                items.append(('verse', int(m.group(1)), m.group(2), pg)); prose_run = False
            elif PROSEOPEN.match(t) or prose_run:
                items.append(('prose', t, pg)); prose_run = True
            else:
                items.append(('pada', t, pg))
    return items


def split_centre(t):
    """Two centred headings typeset on ONE line.

    The Mañjiṭṭhakavagga head shares its line with the division head, so it
    extracted as '1. Itthivimāna      4. Mañjiṭṭhakavagga'.  A run of 3+ spaces
    between two heading-shaped halves is the separator.
    """
    m = re.match(r'^(\d+\.\s+\S[^\s].*?)\s{3,}(\d+\.\s+\S.*)$', t)
    return [m.group(1).strip(), m.group(2).strip()] if m else [t]


def head_kind(txt):
    """sections `k`: 'book' (division / nipāta) > 'vagga' > 'sutta' (leaf)."""
    core = re.sub(r'^\d+\.\s*', '', txt).strip()
    if DIVISION.search(core) or NIPATA.search(core):
        return 'book'
    if VAGGA.search(core):
        return 'vagga'
    return 'sutta'


def build():
    pages = pdf_pages()
    paras = json.load(open(os.path.join(ROOT, 'site', VOL + '.json')))['paragraphs']
    verse, sections, uddana, hide, incipit = {}, {}, {}, {}, {}
    report = {'books': [], 'unmapped': [], 'leaked': []}

    for title, p0, p1, o0, o1, lastv in BOOKS:
        items = items_for(pages, p0, p1)
        # corpus verse-number -> ordinal (this book's slice only)
        n2ord = {}
        for o in range(o0, o1):
            n = paras[o].get('n')
            if isinstance(n, int) and n not in n2ord:
                n2ord[n] = o
        # corpus paragraphs whose TEXT is a printed heading (leaked into the corpus)
        for o in range(o0, o1):
            t = re.sub(r'^\d+\.\s*', '', (paras[o].get('text') or '').strip())
            if HEADTXT.match(t):
                hide[str(o)] = 1
                report['leaked'].append({'ord': o, 'text': (paras[o].get('text') or '').strip()})

        pend_heads, pend_centre = [], []      # headings / colophons awaiting placement
        pend_open = []                        # printed-order material before verse 1
        cur_ord, cur_groups, cur_after = None, [], []
        vseen = set()
        opened = False
        # A vagga's closing material — "<Name>vimānaṁ ekādasamaṁ." then
        # "Tassuddānaṁ" then the mnemonic verse — is set at the PĀDA indent, not
        # the centred indent, once it shares a page with verses.  Without this
        # flag those lines were appended to the last verse's groups, which is
        # exactly the splice the corpus itself makes (ord155/269/482/...).  So:
        # a centred COLOPHON or uddāna label opens a tail; everything in the body
        # column after it belongs to that tail until the next verse number.
        in_tail = False
        items_extra = []

        def flush():
            """close the current verse: write its groups + trailing prose."""
            if cur_ord is None:
                return
            e = {'groups': [g for g in cur_groups if g]}
            if cur_after:
                e['after'] = list(cur_after)
            verse[str(cur_ord)] = e

        def place_centre(blocks, after_ord):
            """colophons + uddāna verses render AFTER the previous paragraph."""
            if after_ord is None or not blocks:
                return
            uddana.setdefault(str(after_ord), []).extend(blocks)

        for it in items:
            kind = it[0]
            if kind == 'verse':
                n, txt = it[1], it[2]
                o = n2ord.get(n)
                if o is None or n in vseen:
                    report['unmapped'].append({'book': title, 'n': n, 'pg': it[3],
                                               'text': txt[:70]})
                    continue
                vseen.add(n)
                flush()
                if not opened:
                    # Everything printed between the book's title page and its
                    # first verse — title headings AND display verse such as
                    # Theragāthā's Nidānagāthā — goes into `sections` in printed
                    # order, so the page's own sequence survives.
                    opened = True
                    if pend_open:
                        sections[str(o)] = pend_open
                        pend_open = []
                    pend_heads, pend_centre = [], []
                else:
                    if pend_centre:
                        place_centre(pend_centre, cur_ord)
                        pend_centre = []
                    if pend_heads:
                        sections[str(o)] = pend_heads
                        pend_heads = []
                cur_ord, cur_groups, cur_after = o, [[txt]], []
                in_tail = False
            elif kind in ('pada', 'prose'):
                if not opened:
                    if kind == 'pada' and pend_open and pend_open[-1]['k'] == 'gatha':
                        pend_open[-1]['l'] += '\n' + it[1]
                    else:
                        pend_open.append({'l': it[1], 'k': 'gatha'})
                elif in_tail and pend_centre:
                    pend_centre[-1]['lines'].append(it[1])
                elif kind == 'pada':
                    if cur_groups:
                        cur_groups[-1].append(it[1])
                elif cur_ord is not None:
                    cur_after.append(it[1])
            elif kind == 'homage':
                incipit[str(o0)] = it[1].strip()
            elif kind == 'centre' and len(split_centre(it[1])) > 1:
                for part in split_centre(it[1]):
                    items_extra.append(part)
                for part in items_extra:
                    pend_heads.append({'l': part, 'k': head_kind(part)})
                items_extra = []
            else:                                     # centre
                t = it[1]
                if t.strip() in ('Khuddakanikāya', title):
                    continue                          # title page
                if not opened:
                    if UDDLBL.match(t):
                        pend_open.append({'l': t, 'k': 'vagga'})
                    elif VERSE.match(t):
                        pend_open.append({'l': t, 'k': head_kind(t)})
                    elif pend_open and pend_open[-1]['k'] == 'gatha':
                        pend_open[-1]['l'] += '\n' + t
                    else:
                        pend_open.append({'l': t, 'k': 'gatha'})
                    continue
                if UDDLBL.match(t):
                    pend_centre.append({'label': t, 'lines': [], 'app': []})
                    in_tail = True
                elif VERSE.match(t):
                    pend_heads.append({'l': t, 'k': head_kind(t)})   # heading: no tail
                elif pend_centre and pend_centre[-1].get('label') and not pend_heads:
                    pend_centre[-1]['lines'].append(t)   # a line of the open uddāna
                    in_tail = True
                else:
                    pend_centre.append({'label': None, 'lines': [t], 'app': []})
                    in_tail = True
        flush()
        if pend_centre:
            place_centre(pend_centre, cur_ord)
        if pend_heads:
            report['unmapped'].append({'book': title, 'trailing_heads': pend_heads})
        report['books'].append({'book': title, 'verses_mapped': len(vseen),
                                'expected': lastv})

    # tidy: an uddāna block with a label but no lines is a stray label
    for k in list(uddana):
        uddana[k] = [b for b in uddana[k] if b.get('lines')]
        if not uddana[k]:
            del uddana[k]
    return verse, sections, uddana, hide, incipit, report


def write(name, data):
    p = os.path.join(R, name, VOL + '.json')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if os.path.exists(p) and not os.path.exists(p + '.pre19build'):
        shutil.copy(p, p + '.pre19build')
    json.dump(data, open(p, 'w'), ensure_ascii=False)
    return p


if __name__ == '__main__':
    v, s, u, h, inc, rep = build()
    print('verse entries %d | sections %d | uddana anchors %d | hidden %d | incipits %d'
          % (len(v), len(s), len(u), len(h), len(inc)))
    for b in rep['books']:
        print('   %-20s verses mapped %d / %d' % (b['book'], b['verses_mapped'], b['expected']))
    print('   leaked corpus headings hidden: %s' % [x['ord'] for x in rep['leaked']])
    if rep['unmapped']:
        print('   UNMAPPED (%d):' % len(rep['unmapped']))
        for x in rep['unmapped'][:15]:
            print('     ', x)
    if '--write' in sys.argv:
        for n, d in (('verse', v), ('sections', s), ('uddana', u), ('hide', h), ('incipit', inc)):
            print('  wrote', write(n, d))
    else:
        print('DRY RUN — pass --write to save')
