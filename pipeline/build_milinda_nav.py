#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Milindapañha (28Khu11 #0) nav tree.

ONE BOOK IN ONE PHYSICAL VOLUME, and the deepest tree in the Khuddaka so far:

    Milindapañhapāḷi                                    28Khu11#0   pdf 1-408
      1. Bāhirakathā            Pubbayogādi
      2. Milindapañha           7 vaggas -> 86 pañhas,
                                Milindapañhapucchāvisajjanā,
                                Meṇḍakapañhārambhakathā -> 6 sections
      4. Meṇḍakapañha           5 vaggas -> 51 pañhas
      5. Anumānapañha           4 vaggas -> 33 pañhas
      6. Opammakathāpañha       Mātikā, 7 vaggas -> 67 pañhas
      Nigamana

DEPTH: the edition's own mātikā lists kaṇḍa -> vagga -> pañha and no deeper, so
that is the depth built here — the same choice the Netti and the Niddesa nav
made.  The generic `tree` branch renders any depth.

WHY THE TOP LEVEL AND THE MIDDLE EXCEPTIONS ARE DECLARED RATHER THAN DERIVED.
A name rule would be wrong for exactly the entries that matter: the kaṇḍa heads
end in `-kathā` and `-pañha`, and so do 237 of the leaves under them; and four
middle-level sections are not vaggas at all (Pubbayogādi,
Milindapañhapucchāvisajjanā, Meṇḍakapañhārambhakathā and the Opamma Mātikā).
They are named here and the MĀTIKĀ CHECK is what tests the result: every entry
of the book's own printed mātikā (pp. i-xi) must appear in the tree, in order.
The mātikā is a different page set by the editors and derived from neither the
body headings nor the corpus, so this is a real two-input check.

!!! THE EDITION'S OWN NUMBERING OF ITS KAṆḌAS IS DEFECTIVE, AND IS PRESERVED.
The body heads them 1, 2, 4, 5, 6 — there is no "3." anywhere, though the text
itself names six divisions ("pubbayogo Milindapañhaṁ lakkhaṇapañhaṁ
meṇḍakapañhaṁ anumānapañhaṁ opammakathāpañhan"ti, p2) and the Nigamana says
"chasu kaṇḍesu".  The front mātikā is worse: it sets the fifth as "5." and then
the sixth as "5." again, where the body has "6.".  Every label here is exactly
what the BODY page prints; the mātikā's own numbers are only used to match.

Usage: python3 pipeline/build_milinda_nav.py [--write]
Backup: site/reader/nav.json.bakmil
"""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV = os.path.join(ROOT, 'site/reader/nav.json')
VOL = '28Khu11'
TITLE = 'Milindapañhapāḷi'
WORK = 'Khuddaka: Milindapañha'
MATIKA_PAGES = (3, 13)          # 0-based pdftotext indices of the front mātikā

# The kaṇḍa heads, exactly as the BODY prints them (see the note above).
TOPS = ['1. Bāhirakathā', '2. Milindapañha', '4. Meṇḍakapañha',
        '5. Anumānapañha', '6. Opammakathāpañha', 'Nigamana']

# Middle-level sections that are not vaggas.  Everything else ending in
# `vagga` is a vagga; everything else again is a leaf.
MIDS = ['Pubbayogādi', 'Milindapañhapucchāvisajjanā',
        'Meṇḍakapañhārambhakathā', 'Mātikā']

# The edition's own misprints, preserved verbatim on both pages and told to the
# check that the two spellings are one section.  Body first, mātikā second.
ERRATUM_SAME = {
    ('6. satapattaṅgapañhā', '6. satapattaṅgapañha'),      # body p389 lengthens
    ('10. dīghaṭṭhipañha', '10. dhīghaṭṭhipañha'),         # mātikā p iv adds h
    ('15. viññāṇanānatthapañha', '15. viññāṇanānātthapañha'),
    ('4. paṭisandahanapuggalavediyanapañha',
     '4. paṭisandahanapuggalavediyapañha'),
    ('6. apuññapañha', '6. apaññapañha'),                  # mātikā p v
    ('7. bhikkhusaṁghapariharaṇapañha',
     '7. bhikkhusaṁghaparihāraṇapañha'),
    ('10. dhammadesanāya appossukkapañha',
     '10. dhammadesanāya appossukapañha'),
    ('5. dvinnaṁ lokuppannānaṁ samakabhāvapañha',
     '5. dvannaṁ lokuppannānaṁ samakabhāvapañha'),
    ('aṭṭha paññāpaṭilābhakāraṇa', 'aṭṭhapaññāpaṭilābhakāraṇa'),
    ('9. vahāhaṅgapañha', '9. varāhaṅgapañha'),
    ('3. bījaṅgapañha', '3. vījaṅgapañha'),
    ('9. bāḷisikaṅgapañha', '9. bhāḷisikaṅgapañha'),
    # The mātikā numbers the sixth kaṇḍa "5." — the same number it has just
    # given the fifth.  The body sets "6.".  Both pages keep what they print.
    ('6. opammakathāpañha', '5. opammakathāpañha'),
}

MAT = re.compile(r'^\s*([\d-]+\.\s+)?([A-ZĀĪŪṄÑṆṬḌḶ][^.]*?)\s+(?:\.\.\.\s+)+\d+\s*$')
# A centred mātikā head, with or without a number: the kaṇḍa and vagga heads
# carry one ("1. Mahāvagga"), the Meṇḍakapañhārambhakathā does not.
CENTRED = re.compile(r'^\s{15,}((?:\d+\.\s+)?[A-ZĀĪŪṄÑṆṬḌḶ]\S*(?:\s+\S+)*?)\s*$')


def fold(s):
    return re.sub(r'[^0-9a-zāīūṁṃṅñṇṭḍḷ.]', '', s.lower())


def same(a, b):
    fa, fb = fold(a), fold(b)
    if fa == fb:
        return True
    return any({fa, fb} == {fold(x), fold(y)} for x, y in ERRATUM_SAME)


def matika(pages):
    """The front mātikā, in printed order: kaṇḍa and vagga heads (centred, no
    page number) and the numbered entries (name ... ... page)."""
    out = []
    for pi in range(MATIKA_PAGES[0], MATIKA_PAGES[1] + 1):
        for l in pages[pi].split('\n'):
            t = l.strip()
            if not t or t.startswith('Mātikā') or t.startswith('Piṭṭhaṅka'):
                continue
            # the running page-header, which on a right-hand page carries the
            # roman folio to the right of the book's name
            if 'niṭṭhitā' in t or fold(TITLE) in fold(t):
                continue
            m = MAT.match(l)
            if m:
                out.append(((m.group(1) or '') + m.group(2)).strip())
                continue
            c = CENTRED.match(l)
            if c and not re.search(r'\d\s*$', c.group(1)):
                out.append(c.group(1).strip())
    return out


def printed_heads():
    """Every printed heading, in PRINTED order, as (label, ordinal).

    Read from BOTH side-maps.  `sections/` holds the headings the page sets
    ABOVE a numbered unit; `uddana/` plain-block `head` fields hold those the
    page sets after one — which is where a section with no numbered unit of its
    own now lives (the Dhutaṅgapañha, the Opamma mātikā, the
    Meṇḍakapañhārambhakathā, the Nigamana).  Reading only `sections/` would
    drop eleven headings from the tree while they render correctly on the page,
    which is exactly the defect build_jataka_nav.py had to be taught about.
    """
    S = json.load(open(os.path.join(ROOT, 'site/reader/sections', VOL + '.json'),
                       encoding='utf-8'))
    U = json.load(open(os.path.join(ROOT, 'site/reader/uddana', VOL + '.json'),
                       encoding='utf-8'))
    out = []
    for k in sorted(set(S) | set(U), key=int):
        for e in S.get(k, []):
            if e.get('k') in ('gatha', 'booktitle'):
                continue
            out.append((e['l'], int(k)))
        for b in U.get(k, []):
            if b.get('head'):
                out.append((b['head'], int(k)))
    return out


def main():
    pdf = os.path.join(ROOT, 'pali-unicode', VOL + '.pdf')
    pages = subprocess.run(['pdftotext', '-layout', pdf, '-'],
                           capture_output=True, text=True).stdout.split('\f')
    npara = len(json.load(open(os.path.join(ROOT, 'site', VOL + '.json'),
                               encoding='utf-8'))['paragraphs'])
    tops = {fold(x) for x in TOPS}
    mids = {fold(x) for x in MIDS}

    tree, kanda, mid = [], None, None
    for lab, ordi in printed_heads():
        node = {'label': lab, 'key': '%s#%d' % (VOL, ordi), 'kids': []}
        f = fold(lab)
        if f in tops:
            tree.append(node); kanda, mid = node, None
        elif f in mids or re.search(r'vagga$', lab, re.I):
            if kanda is None:
                tree.append(node); kanda = node
            else:
                kanda['kids'].append(node)
            mid = node
        else:
            (mid or kanda or {'kids': tree})['kids'].append(node)
    kandas = len(tree)
    vaggas = sum(1 for n in tree for k in n['kids']
                 if re.search(r'vagga$', k['label'], re.I))
    leaves = sum(1 for n in _flat(tree) if not n['kids'])

    flat = []
    def walk(ns):
        for n in ns:
            flat.append(n['label']); walk(n['kids'])
    walk(tree)

    mat = matika(pages)
    i, missing = 0, []
    for m in mat:
        j = next((x for x in range(i, len(flat)) if same(flat[x], m)), None)
        if j is None:
            missing.append(m)
        else:
            i = j + 1
    extra = [x for x in flat if not any(same(x, m) for m in mat)]

    print('%s  %d kaṇḍas / %d vaggas / %d sections   mātikā lists %d   [%s]'
          % (TITLE, kandas, vaggas, len(flat) - kandas, len(mat),
             'CHECK' if missing else 'OK'))
    for n in tree:
        print('    %-24s %2d children, %3d sections'
              % (n['label'], len(n['kids']),
                 sum(1 for _ in _flat(n['kids']))))
        for k in n['kids']:
            if k['kids']:
                print('        %-30s %d' % (k['label'], len(k['kids'])))
    print('    leaves (clickable sections with no children): %d' % leaves)
    if extra:
        print('    body headings the mātikā does not list (%d, KEPT — they are '
              'printed): %s' % (len(extra), ', '.join(extra)))
    fail = False
    for m in missing:
        print('    REFUSED — in the mātikā, absent from the tree: %r' % m)
        fail = True

    keys = [n['key'] for n in _flat(tree)]
    oor = [k for k in keys if not (0 <= int(k.split('#')[1]) < npara)]
    if oor:
        print('    REFUSED — keys out of range:', oor[:5]); fail = True
    print('    %d nav keys, %d out of range' % (len(keys), len(oor)))

    # THE EDITION'S OWN TOTALS, from its Nigamana (p407): "chasu kaṇḍesu
    # bāvīsativaggapatimaṇḍitesu" — six kaṇḍas adorned with twenty-two vaggas.
    # REPORTED, NOT ENFORCED, and this is why: the body prints FIVE kaṇḍa heads
    # (there is no "3.") and TWENTY-THREE vaggas.  Both totals are the
    # edition's own arithmetic disagreeing with the edition's own pages, which
    # is an erratum to record rather than a defect to correct.
    numbered = sum(1 for n in tree if re.match(r'^\d+\.', n['label']))
    print('    the edition\'s Nigamana claims 6 kaṇḍas / 22 vaggas; the body '
          'prints %d NUMBERED kaṇḍa heads (1, 2, 4, 5, 6 — no "3.") plus '
          'Nigamana, and %d vaggas — recorded, not corrected'
          % (numbered, vaggas))

    if fail:
        raise SystemExit('NOT WRITTEN')

    nav = json.load(open(NAV, encoding='utf-8'))
    # REPLACE EVERY NODE FOR THIS VOLUME, not just the first — the invariant is
    # ONE NODE PER BOOK, and a builder that replaces "the" node of a volume
    # leaves the others behind.  That shipped once, on 27Khu10.
    slot = None
    for lay in nav['layers']:
        for nik in lay.get('nikayas', []):
            vols = nik.get('volumes', [])
            hits = [i for i, v in enumerate(vols) if v.get('vol') == VOL]
            if hits:
                slot = (vols, hits)
    if slot is None:
        raise SystemExit('no nav volume node for ' + VOL)
    node = {'vol': VOL, 'work': WORK, 'title': TITLE,
            'first': '%s#0' % VOL, 'tree': tree}
    lst, hits = slot
    print('replacing %d existing nav node(s) for %s with 1' % (len(hits), VOL))
    for i in reversed(hits):
        del lst[i]
    lst[hits[0]:hits[0]] = [node]
    left = [v for v in lst if v.get('vol') == VOL]
    if len(left) != 1:
        raise SystemExit('NOT WRITTEN — %d nodes for %s after the splice, '
                         'expected 1' % (len(left), VOL))
    if '--write' in sys.argv:
        if not os.path.exists(NAV + '.bakmil'):
            shutil.copy(NAV, NAV + '.bakmil')
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
