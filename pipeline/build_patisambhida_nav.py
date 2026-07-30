#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Paṭisambhidāmagga (26Khu09) nav tree.

SHAPE, chosen by the user: all three levels the edition's own mātikā prints —

    Paṭisambhidāmaggapāḷi
      1. Mahāvagga        1. Ñāṇakathā        1. Sutamayañāṇaniddesa … (73)
                          2. Diṭṭhikathā      1. Assādadiṭṭhiniddesa  … (16)
                          …                   5. Vimokkhakathā has none
      2. Yuganaddhavagga  …
      3. Paññāvagga       …

MIXED DEPTH IS THE EDITION'S.  The mātikā gives some kathās a list of niddesas
or vāras and prints others with a page number and nothing under them
(Vimokkhakathā, Gatikathā, Kammakathā, Vipallāsakathā, Maggakathā,
Maṇḍapeyyakathā, Lokuttarakathā, Cariyākathā and the rest).  A kathā with no
children is a clickable leaf at its own depth; the reader's generic `tree`
branch renders that without a special case.

TWO INDEPENDENT INPUTS.  The tree is built from `sections/26Khu09.json`, i.e.
from the headings PRINTED OVER EACH SECTION in the body and mapped onto corpus
ordinals.  It is then checked against the MĀTIKĀ printed in the front matter,
which is a different page set by the editors as their own table of contents.
The builder refuses to write unless every mātikā entry appears in the tree, in
the mātikā's own order.

THE CHECK IS A SUBSEQUENCE, NOT AN EQUALITY, AND THAT IS DELIBERATE.  The body
prints headings the mātikā does not list — the Mahāvagga's own "Mātikā", the
Ānāpānassati chakkas and catukkas, the lettered "Ka./Kha./Ga." sub-niddesas of
the Indriyakathā, and the "1. Mātikā" / "2. Niddesa" halves of the Suññakathā.
Those are real printed headings and belong in the tree; requiring the two lists
to be equal would mean either dropping them or falsely reporting a defect.  So
every mātikā entry must be present and in order, and every body-only heading is
REPORTED rather than passed over in silence.

Usage: python3 pipeline/build_patisambhida_nav.py [--write]
Backup: site/reader/nav.json.bakpat
"""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV = os.path.join(ROOT, 'site/reader/nav.json')
VOL = '26Khu09'
WORK, TITLE = 'Khuddaka: Paṭisambhidāmagga', 'Paṭisambhidāmaggapāḷi'
MATIKA_PAGES = (3, 8)          # 0-based pdftotext indices of the front mātikā

# A mātikā name is not always one word: the edition sets "32. Ānantarika
# samādhiñāṇaniddesa" with a space inside the compound, so anchoring the name to
# `\S*` silently dropped that entry from the list being checked against.
MAT = re.compile(r'^\s*(?:([\d-]+)\.\s+)?([A-ZĀĪŪṄÑṆṬḌḶ].*?)\s+\.\.\.\s+\.\.\.\s+\d+\s*$')
# A mātikā line for a kathā that HAS children carries no page number of its own
# ("6. Paṭisambhidākathā" alone on its line), so it needs its own pattern.
MATBARE = re.compile(r'^\s*(\d+)\.\s+([A-ZĀĪŪṄÑṆṬḌḶ]\S*(?:kathā|vagga))\s*$')

# The edition prints "5. Virāgatathā" in the body where its own mātikā sets
# "5. Virāgakathā" — 't' for 'k' (recorded in build_khu_volume.ERRATA).  Both
# readings are kept exactly as each page sets them; this map only tells the
# builder that the body form is a KATHĀ, which its spelling no longer says.
KATHA_ALSO = {'5. Virāgatathā'}


def level(label):
    """0 = vagga, 1 = kathā, 2 = a section inside a kathā."""
    core = re.sub(r'^[\d-]+\.\s*', '', label).strip()
    if re.search(r'vagga$', core, re.I):
        return 0
    if re.search(r'kathā$', core, re.I) or label in KATHA_ALSO:
        return 1
    return 2


# The edition's own misprint, which makes the two pages disagree about one
# heading's spelling.  Both are kept verbatim where they are printed; this pair
# only tells the CHECK that they are the same section, so that a real absence
# is still reported and this one is not mistaken for it.
ERRATUM_SAME = {('virāgatathā', 'virāgakathā')}


def fold(s):
    return re.sub(r'[^a-zāīūṁṃṅñṇṭḍḷ]', '', s.lower())


def same(a, b):
    fa, fb = fold(a), fold(b)
    if fa == fb:
        return True
    return any((fa.endswith(x) and fb.endswith(y)) or (fa.endswith(y) and fb.endswith(x))
               for x, y in ERRATUM_SAME)


def matika():
    pdf = os.path.join(ROOT, 'pali-unicode', VOL + '.pdf')
    pages = subprocess.run(['pdftotext', '-layout', pdf, '-'],
                           capture_output=True, text=True).stdout.split('\f')
    out = []
    for pi in range(MATIKA_PAGES[0], MATIKA_PAGES[1] + 1):
        for l in pages[pi].split('\n'):
            t = l.strip()
            if not t or t.startswith('Mātikā') or 'niṭṭhitā' in t:
                continue
            m = MAT.match(l) or MATBARE.match(l)
            if m:
                out.append(('%s. %s' % (m.group(1), m.group(2))) if m.group(1)
                           else m.group(2))
    return out


def tree_for():
    S = json.load(open(os.path.join(ROOT, 'site/reader/sections', VOL + '.json'),
                       encoding='utf-8'))
    tree, vagga, katha = [], None, None
    for k in sorted(S, key=int):
        for e in S[k]:
            lab, key, lv = e['l'], '%s#%s' % (VOL, k), level(e['l'])
            node = {'label': lab, 'key': key, 'kids': []}
            if lv == 0:
                tree.append(node); vagga, katha = node, None
            elif lv == 1:
                if vagga is None:
                    raise SystemExit('%s: kathā %r before any vagga' % (VOL, lab))
                vagga['kids'].append(node); katha = node
            else:
                # A section with no kathā open belongs directly to the vagga —
                # the Mahāvagga's own "Mātikā" is printed that way.
                (katha or vagga)['kids'].append(node)
    return tree


def main():
    tree = tree_for()
    flat = []
    def walk(ns):
        for n in ns:
            flat.append(n['label']); walk(n['kids'])
    walk(tree)
    mat = matika()
    # every mātikā entry present, in order
    i, missing = 0, []
    for m in mat:
        j = next((x for x in range(i, len(flat)) if same(flat[x], m)), None)
        if j is None:
            missing.append(m)
        else:
            i = j + 1
    extra = [x for x in flat if not any(same(x, m) for m in mat)]

    nv = sum(1 for n in tree)
    nk = sum(len(n['kids']) for n in tree)
    ns = sum(len(k['kids']) for n in tree for k in n['kids'])
    print('%s  %d vaggas / %d kathās / %d sections   mātikā lists %d   [%s]'
          % (VOL, nv, nk, ns, len(mat), 'CHECK' if missing else 'OK'))
    for n in tree:
        print('    %-20s %d kathās' % (n['label'], len(n['kids'])))
    print('    body headings the mātikā does not list (%d, kept — they are '
          'printed):' % len(extra))
    for x in extra:
        print('        %s' % x)
    if missing:
        print('    REFUSED — mātikā entries absent from the body tree:')
        for m in missing:
            print('        %s' % m)
        raise SystemExit('NOT WRITTEN')

    nav = json.load(open(NAV, encoding='utf-8'))
    slot = None
    for lay in nav['layers']:
        for nik in lay.get('nikayas', []):
            for idx, v in enumerate(nik.get('volumes', [])):
                if v.get('vol') == VOL:
                    slot = (nik['volumes'], idx)
    if slot is None:
        raise SystemExit('no nav volume node for ' + VOL)
    npara = len(json.load(open(os.path.join(ROOT, 'site', VOL + '.json'),
                               encoding='utf-8'))['paragraphs'])
    keys = [n['key'] for n in flat_nodes(tree)]
    oor = [k for k in keys if not (0 <= int(k.split('#')[1]) < npara)]
    print('  %d nav keys, %d out of range' % (len(keys), len(oor)))
    if oor:
        raise SystemExit('NOT WRITTEN — keys out of range: %s' % oor[:5])
    lst, idx = slot
    lst[idx] = {'vol': VOL, 'work': WORK, 'title': TITLE,
                'first': '%s#0' % VOL, 'tree': tree}
    if '--write' in sys.argv:
        if not os.path.exists(NAV + '.bakpat'):
            shutil.copy(NAV, NAV + '.bakpat')
        json.dump(nav, open(NAV, 'w', encoding='utf-8'), ensure_ascii=False)
        print('wrote', NAV)
    else:
        print('DRY RUN — pass --write to save')


def flat_nodes(ns):
    for n in ns:
        yield n
        for x in flat_nodes(n['kids']):
            yield x


if __name__ == '__main__':
    main()
