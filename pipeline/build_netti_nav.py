#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Netti (27Khu10 #0) and Peṭakopadesa (27Khu10 #151) nav trees.

TWO BOOKS IN ONE PHYSICAL VOLUME, each with its own title page, its own mātikā
and its own closing colophon.  The standing rule applies: both need their own
nav node with a correct `first` ordinal, or BOOKSPAN cannot bound them and one
renders into the other.

    Nettipāḷi                                  27Khu10#0    pdf 1-166
      1. Saṅgahavāra
      2. Uddesavāra
      3. Niddesavāra        Hārasaṅkhepa, Nayasaṅkhepa, Dvādasapada
      4. Paṭiniddesavāra    16 hāravibhaṅgas, 16 hārasampātas,
                            Nayasamuṭṭhāna, Sāsanapaṭṭhāna
    Peṭakopadesapāḷi                           27Khu10#151  pdf 167-341
      1. Ariyasaccappakāsanapaṭhamabhūmi … 8. Suttavebhaṅgiya   (flat)

WHY THE TOP LEVEL IS DECLARED RATHER THAN DERIVED.  The Netti's mātikā sets its
four vāras and the thirty-four sections under the fourth at the SAME indent and
restarts the numbering twice (1-4, then 1-16, then 1-16), so the printed table
gives no typographic signal for the nesting; and the Peṭakopadesa's eighth
entry, "8. Suttavebhaṅgiya", is the one bhūmi whose name does not say so.  A
name rule would therefore be wrong for exactly the cases that matter.  The top
level is named here and the MĀTIKĀ CHECK is what tests it: every entry of each
book's own printed mātikā must appear in that book's tree, in order.

Usage: python3 pipeline/build_netti_nav.py [--write]
Backup: site/reader/nav.json.baknet
"""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV = os.path.join(ROOT, 'site/reader/nav.json')
VOL = '27Khu10'

BOOKS = [
 {'title': 'Nettipāḷi', 'work': 'Khuddaka: Netti', 'first': 0,
  'matika': (3, 4),
  'tops': ['1. Saṅgahavāra', '2. Uddesavāra', '3. Niddesavāra',
           '4. Paṭiniddesavāra']},
 {'title': 'Peṭakopadesapāḷi', 'work': 'Khuddaka: Peṭakopadesa', 'first': 151,
  'matika': (5, 5),
  'tops': ['1. Ariyasaccappakāsanapaṭhamabhūmi', '2. Sāsanapaṭṭhānadutiyabhūmi',
           '3. Suttādhiṭṭhānatatiyabhūmi', '4. Suttavicayacatutthabhūmi',
           '5. Pañcamabhūmi', '6. Suttatthasamuccayabhūmi',
           '7. Hārasampātabhūmi', '8. Suttavebhaṅgiya']},
]

MAT = re.compile(r'^\s*(?:([\d-]+)\.\s+)?([A-ZĀĪŪṄÑṆṬḌḶ].*?)\s+\.\.\.\s+\.\.\.\s+\d+\s*$')


# The edition's own misprint: the Netti mātikā sets "13. Sodanahāravibhaṅga"
# where the body heads "13. Sodhanahāravibhaṅga", and the same mātikā spells the
# matching sampāta "Sodhanahārasampāta" WITH the h — so the two printed pages
# disagree, and one disagrees with itself.  Both are kept as printed; this pair
# only tells the check they are one section (see build_khu_volume.ERRATA).
ERRATUM_SAME = {('sodanahāravibhaṅga', 'sodhanahāravibhaṅga')}


def fold(s):
    return re.sub(r'[^a-zāīūṁṃṅñṇṭḍḷ]', '', s.lower())


def same(a, b):
    fa, fb = fold(a), fold(b)
    return fa == fb or any({fa, fb} == {x, y} for x, y in ERRATUM_SAME)


def matika(pages, p0, p1):
    out = []
    for pi in range(p0, p1 + 1):
        for l in pages[pi].split('\n'):
            t = l.strip()
            if not t or t.startswith('Mātikā') or 'niṭṭhitā' in t:
                continue
            m = MAT.match(l)
            if m:
                out.append(('%s. %s' % (m.group(1), m.group(2))) if m.group(1)
                           else m.group(2))
    return out


def main():
    S = json.load(open(os.path.join(ROOT, 'site/reader/sections', VOL + '.json'),
                       encoding='utf-8'))
    pdf = os.path.join(ROOT, 'pali-unicode', VOL + '.pdf')
    pages = subprocess.run(['pdftotext', '-layout', pdf, '-'],
                           capture_output=True, text=True).stdout.split('\f')
    npara = len(json.load(open(os.path.join(ROOT, 'site', VOL + '.json'),
                               encoding='utf-8'))['paragraphs'])
    bounds = [b['first'] for b in BOOKS] + [npara]

    nav = json.load(open(NAV, encoding='utf-8'))
    # REPLACE EVERY NODE FOR THIS VOLUME, not just the first.  A physical volume
    # holding two books ALREADY has two nav nodes — build_khuddaka_nav.py splits
    # the 21 Khuddaka books across the 11 volumes — so replacing "the" node left
    # the second one behind and the sidebar showed Peṭakopadesapāḷi TWICE, once
    # from this builder and once in its old `nipata`/`vaggas` shape.  Splice out
    # all of them and put the new list where the first one stood.
    slot = None
    for lay in nav['layers']:
        for nik in lay.get('nikayas', []):
            vols = nik.get('volumes', [])
            hits = [i for i, v in enumerate(vols) if v.get('vol') == VOL]
            if hits:
                slot = (vols, hits)
    if slot is None:
        raise SystemExit('no nav volume node for ' + VOL)

    fail, nodes = False, []
    for bi, b in enumerate(BOOKS):
        lo, hi = bounds[bi], bounds[bi + 1]
        tops = {fold(x): x for x in b['tops']}
        tree, cur = [], None
        for k in sorted(S, key=int):
            if not (lo <= int(k) < hi):
                continue
            for e in S[k]:
                if e['k'] == 'gatha':
                    continue                       # display verse, not a heading
                lab, key = e['l'], '%s#%s' % (VOL, k)
                node = {'label': lab, 'key': key, 'kids': []}
                if fold(lab) in tops:
                    tree.append(node); cur = node
                elif cur is None:
                    tree.append(node); cur = node  # a heading before any top
                else:
                    cur['kids'].append(node)
        flat = []
        def walk(ns):
            for n in ns:
                flat.append(n['label']); walk(n['kids'])
        walk(tree)
        mat = matika(pages, *b['matika'])
        i, missing = 0, []
        for m in mat:
            j = next((x for x in range(i, len(flat)) if same(flat[x], m)), None)
            if j is None:
                missing.append(m)
            else:
                i = j + 1
        extra = [x for x in flat if not any(same(x, m) for m in mat)]
        print('%-18s %d top / %d sections   mātikā lists %d   [%s]'
              % (b['title'], len(tree), len(flat) - len(tree), len(mat),
                 'CHECK' if missing else 'OK'))
        for n in tree:
            print('    %-34s %d' % (n['label'], len(n['kids'])))
        if extra:
            print('    body headings the mātikā does not list (%d, kept — they '
                  'are printed): %s' % (len(extra), ', '.join(extra)))
        for m in missing:
            print('    REFUSED — in the mātikā, absent from the tree: %s' % m)
            fail = True
        keys = [n['key'] for n in _flat(tree)]
        oor = [k for k in keys if not (0 <= int(k.split('#')[1]) < npara)]
        if oor:
            print('    REFUSED — keys out of range:', oor[:5]); fail = True
        print('    %d nav keys, %d out of range' % (len(keys), len(oor)))
        nodes.append({'vol': VOL, 'work': b['work'], 'title': b['title'],
                      'first': '%s#%d' % (VOL, b['first']), 'tree': tree})
    if fail:
        raise SystemExit('NOT WRITTEN')
    lst, hits = slot
    print('replacing %d existing nav node(s) for %s with %d'
          % (len(hits), VOL, len(nodes)))
    for i in reversed(hits):
        del lst[i]
    lst[hits[0]:hits[0]] = nodes
    left = [v for v in lst if v.get('vol') == VOL]
    if len(left) != len(nodes):
        raise SystemExit('NOT WRITTEN — %d nodes for %s after the splice, expected %d'
                         % (len(left), VOL, len(nodes)))
    if '--write' in sys.argv:
        if not os.path.exists(NAV + '.baknet'):
            shutil.copy(NAV, NAV + '.baknet')
        json.dump(nav, open(NAV, 'w', encoding='utf-8'), ensure_ascii=False)
        print('wrote', NAV)
    else:
        print('DRY RUN — pass --write to save')


def _flat(ns):
    for n in ns:
        yield n
        for x in _flat(n['kids']):
            yield x


if __name__ == '__main__':
    main()
