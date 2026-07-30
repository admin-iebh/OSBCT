#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Give the Yamaka and the Paṭṭhāna the volume level the edition prints.

    python3 pipeline/group_abhidhamma_volumes.py [--write]

THE DEFECT, user-reported from the sidebar.  The Abhidhamma has SEVEN books and
the left pane listed TWENTY-SEVEN rows: five correct ones, then the sixth book
(Yamaka) exploded into its ten yamakas as ten sibling "books", then the seventh
(Paṭṭhāna) into twelve rows across five volumes with FOUR NAMES REPEATED —
Tikapaṭṭhānapāḷi three times, Dukapaṭṭhānapāḷi three times, Dukatikapaṭṭhānapāḷi
and Tikadukapaṭṭhānapāḷi twice each.  `build_nav.py`'s font heuristic took every
`…pāḷi` name in the corpus `book` field as a book of its own.

THE INNER NAMES ARE NOT WRONG — each yamaka and each paṭṭhāna division really
does print its own title page and its own homage inside the volume, which is
why `build_incipit.py` found homages there.  What was missing is the level
ABOVE them, and the edition states it on every volume's own title page:

    Abhidhammapiṭake              Abhidhammapiṭake
    YAMAKAPĀḶI                    PAṬṬHĀNAPĀḶI
    (Paṭhamo bhāgo)               (Paṭhamo bhāgo)

Yamaka in three bhāgas (33-35), Paṭṭhāna in five (36-40) — the same shape the
Jātaka has, and read the same way: off the edition's own front matter rather
than reasoned from another book.  So each of those eight volumes becomes ONE
node labelled as its title page labels it, with its inner books as the first
level of a tree and their existing section lists preserved underneath.  Every
row then lies wholly inside one volume, so each OPENS a reading pane instead of
only expanding — the standing `render()` limitation is never met.

NOT TOUCHED: 29Abhi01, 30Abhi02, 32Abhi04 (one book each) and 31Abhi03, whose
two nodes are genuinely two of the seven books (Dhātukathā, Puggalapaññatti).
Grouping those would invent a book the edition does not print.
"""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV = os.path.join(ROOT, 'site/reader/nav.json')
GROUP = ['33Abhi05', '34Abhi06', '35Abhi07',
         '36Abhi08', '37Abhi09', '38Abhi10', '39Abhi11', '40Abhi12']
WORK = {'Yamakapāḷi': 'Abhidhamma: Yamaka',
        'Paṭṭhānapāḷi': 'Abhidhamma: Paṭṭhāna'}


def cover_title(vol):
    """The volume's own title page: the work name and its bhāga, verbatim.

    Taken from the printed page and not from a table here, so a volume whose
    cover says something else cannot be silently mislabelled.
    """
    txt = subprocess.run(['pdftotext', '-layout', '-f', '1', '-l', '1',
                          os.path.join(ROOT, 'pali-unicode', vol + '.pdf'), '-'],
                         capture_output=True, text=True).stdout
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    work = bhaga = None
    for l in lines:
        if re.fullmatch(r'[A-ZĀĪŪṄÑṆṬḌḶ]+PĀḶI', l):
            work = l[0] + l[1:].lower()            # YAMAKAPĀḶI -> Yamakapāḷi
        m = re.fullmatch(r'\((\w+o bhāgo)\)', l)
        if m:
            bhaga = m.group(1)
    if not work or not bhaga:
        raise SystemExit('%s: could not read the title page (%r)' % (vol, lines[:6]))
    return work, '%s (%s)' % (work, bhaga)


def main():
    nav = json.load(open(NAV, encoding='utf-8'))
    ab = None
    for lay in nav['layers']:
        if lay['layer'] != 'canon':
            continue
        for nik in lay.get('nikayas', []):
            if nik['nikaya'] == 'Abhidhammapiṭaka':
                ab = nik
    if ab is None:
        raise SystemExit('no Abhidhammapiṭaka nikāya in the nav')
    vols = ab['volumes']
    before = len(vols)

    for vol in GROUP:
        hits = [i for i, v in enumerate(vols) if v.get('vol') == vol]
        if not hits:
            raise SystemExit('no nav node for ' + vol)
        if hits != list(range(hits[0], hits[0] + len(hits))):
            raise SystemExit('%s: its nodes are not contiguous' % vol)
        old = [vols[i] for i in hits]
        if any(v.get('tree') for v in old):
            print('  %-9s already a tree — left alone' % vol)
            continue
        work, label = cover_title(vol)
        tree = []
        for v in old:
            kids = []
            for s in v.get('suttas', []):
                kids.append({'label': s['label'], 'key': s['key'],
                             'kids': [{'label': x['label'], 'key': x['key'],
                                       'kids': []}
                                      for x in s.get('subs', [])]})
            tree.append({'label': v['title'], 'key': v['first'], 'kids': kids})
        node = {'vol': vol, 'work': WORK.get(work, 'Abhidhamma'), 'title': label,
                'first': old[0]['first'], 'tree': tree}
        for i in reversed(hits):
            del vols[i]
        vols[hits[0]:hits[0]] = [node]
        print('  %-9s %-2d node(s) -> 1  %-32s inner books: %s'
              % (vol, len(old), label, ', '.join(t['label'] for t in tree)))

    titles = [v['title'] for v in vols]
    dup = sorted({t for t in titles if titles.count(t) > 1})
    print('\nAbhidhamma nav rows: %d -> %d' % (before, len(vols)))
    for v in vols:
        print('   %-9s %s' % (v['vol'], v['title']))
    if dup:
        raise SystemExit('NOT WRITTEN — book titles still repeated: %s' % dup)
    print('no repeated book title')

    if '--write' in sys.argv:
        bak = NAV + '.bakabhigroup'
        if not os.path.exists(bak):
            shutil.copy(NAV, bak)
        json.dump(nav, open(NAV, 'w', encoding='utf-8'), ensure_ascii=False)
        print('wrote', NAV)
    else:
        print('DRY RUN — pass --write to save')


if __name__ == '__main__':
    main()
