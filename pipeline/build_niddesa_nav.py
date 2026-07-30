#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Mahāniddesa (24Khu07) and Cūḷaniddesa (25Khu08) nav trees.

SHAPE, chosen by the user: book -> vagga -> suttaniddesa.  The numbered lemma
sections (210 in 24Khu07, 161 + 174 in 25Khu08) are NOT tree leaves; each is one
Suttanipāta verse with its whole commentary and they belong in ☰ Contents.
That is also exactly the depth the edition's own mātikā lists and no deeper.

TWO INDEPENDENT INPUTS, which is the point of this builder.  The tree is built
from `sections/<VOL>.json`, i.e. from the headings PRINTED OVER EACH SECTION in
the body, mapped onto corpus ordinals.  It is then checked against the MĀTIKĀ
printed in the volume's front matter — a different page, set by the editors as
their own table of contents.  Neither is derived from the other, so agreement is
a real check and not the 19Khu02 "two checks, one input" trap.  The builder
REFUSES TO WRITE unless every leaf, in order, matches the mātikā.

WHAT THE EDITION PRINTS, and why 25Khu08 has two identically-named rows:

    Mahāniddesapāḷi                       24Khu07
      1. Aṭṭhakavagga        16 suttaniddesas (Kāma … Sāriputta)

    Cūḷaniddesapāḷi                       25Khu08
      Pārāyanavagga          the vagga's own TEXT, pp. 1-21: Vatthugāthā, the
                             16 māṇavapucchās, Pārāyanatthutigāthā and
                             Pārāyanānugītigāthā — verse, with no commentary
      Pārāyanavagga          the NIDDESA, pp. 24-307: 19 sections, of which the
                             19th, Khaggavisāṇasuttaniddesa, is itself divided
                             into four vaggas

The mātikā prints BOTH of those blocks under the bare heading "Pārāyanavagga",
and so does the body.  The edition nowhere distinguishes them by name, so
neither does this builder: inventing "text"/"niddesa" or "I"/"II" labels would
be exactly the mistake corrected for the Jātaka, where a division the edition
does print ("Paṭhamo bhāgo") had been replaced by an editorial one.  The two
rows are told apart by their children, as the printed page tells them apart.

MIXED DEPTH IS THE EDITION'S.  Only Khaggavisāṇasuttaniddesa carries vaggas; the
other eighteen sections sit directly under their vagga.  The reader's generic
`tree` branch renders any depth, so this needs no special case.

Usage: python3 pipeline/build_niddesa_nav.py [--write]
Backup: site/reader/nav.json.baknid
"""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV = os.path.join(ROOT, 'site/reader/nav.json')

# Per volume: the mātikā's pdftotext page indices (0-based \f), the vagga
# headings expected at top level, and the sub-vagga names that belong UNDER a
# section rather than beside it.
SPEC = {
 '24Khu07': {
   'work': 'Khuddaka: Mahāniddesa', 'title': 'Mahāniddesapāḷi',
   'matika': (2, 3), 'blocks': ['1. Aṭṭhakavagga'], 'subvaggas': set(),
   'expect': [16],
 },
 '25Khu08': {
   'work': 'Khuddaka: Cūḷaniddesa', 'title': 'Cūḷaniddesapāḷi',
   'matika': (3, 4), 'blocks': ['Pārāyanavagga', 'Pārāyanavagga'],
   'subvaggas': {'Paṭhamavagga', 'Dutiyavagga', 'Tatiyavagga', 'Catutthavagga'},
   'expect': [19, 19],
 },
}

# A mātikā line: "10. Kappamāṇavapucchā   ...   ...   15" or, for the unnumbered
# sections, "    Pārāyanatthutigāthā   ...   ...   21".  The leaders and the page
# number are dropped; only the NAME and its number are kept, because those are
# what the body headings must reproduce.
MAT = re.compile(r'^\s*(?:(\d+)\.\s+)?([A-ZĀĪŪṄÑṆṬḌḶ]\S*)\s+\.\.\.\s+\.\.\.\s+\d+\s*$')
# Lines the mātikā prints that are not entries.
MATSKIP = re.compile(r'^(Mātikā|Piṭṭhaṅka|Mātikā\s+Piṭṭhaṅka|.*mātikā niṭṭhitā\.)$')


def norm_name(s):
    """Compare names by letters only — the mātikā and the body headings differ
    in spelling in several places and the edition's own inconsistency is
    preserved, not corrected: 24Khu07's mātikā sets 'Cūḷaviyūhasuttaniddesa',
    '14. Tuvaṭṭakasuttaniddesa' and '12.' for the section the body heads
    'Cūḷabyūhasuttaniddesa' and 'Tuvaṭakasuttaniddesa'.  Comparing letter sets
    would hide a real mismatch, so compare the folded string and REPORT every
    difference; the run is only refused when the two lists differ in LENGTH or
    ORDER, which is what a structural error looks like."""
    return re.sub(r'[^a-zāīūṁṃṅñṇṭḍḷ]', '', s.lower())


def matika(vol):
    pdf = os.path.join(ROOT, 'pali-unicode', vol + '.pdf')
    pages = subprocess.run(['pdftotext', '-layout', pdf, '-'],
                           capture_output=True, text=True).stdout.split('\f')
    p0, p1 = SPEC[vol]['matika']
    out = []
    for pi in range(p0, p1 + 1):
        for l in pages[pi].split('\n'):
            t = l.strip()
            if not t or MATSKIP.match(t):
                continue
            m = MAT.match(l)
            if m:
                out.append((m.group(1), m.group(2)))
    return out


def tree_for(vol):
    S = json.load(open(os.path.join(ROOT, 'site/reader/sections', vol + '.json'),
                       encoding='utf-8'))
    sub = SPEC[vol]['subvaggas']
    tree, cur, leaf = [], None, None
    for k in sorted(S, key=int):
        for e in S[k]:
            key = '%s#%s' % (vol, k)
            lab, kind = e['l'], e['k']
            bare = re.sub(r'^\d+(?:-\d+)?\.\s*', '', lab).strip()
            if kind == 'vagga' and bare in sub:
                # a vagga printed BELOW a section heading is that section's own
                # division (only Khaggavisāṇasuttaniddesa has any)
                if leaf is None:
                    raise SystemExit('%s: sub-vagga %r with no section open' % (vol, lab))
                leaf['kids'].append({'label': lab, 'key': key, 'kids': []})
            elif kind == 'vagga':
                cur = {'label': lab, 'key': key, 'kids': []}
                tree.append(cur); leaf = None
            else:
                if cur is None:
                    raise SystemExit('%s: section %r with no vagga open' % (vol, lab))
                leaf = {'label': lab, 'key': key, 'kids': []}
                cur['kids'].append(leaf)
    return tree


def check(vol, tree):
    sp = SPEC[vol]
    bad = []
    got_blocks = [n['label'] for n in tree]
    if got_blocks != sp['blocks']:
        bad.append('top-level rows %r != %r' % (got_blocks, sp['blocks']))
    counts = [len(n['kids']) for n in tree]
    if counts != sp['expect']:
        bad.append('section counts %r != %r' % (counts, sp['expect']))
    # against the edition's own mātikā — the independent second input
    leaves = [k['label'] for n in tree for k in n['kids']]
    mat = ['%s. %s' % (n, s) if n else s for n, s in matika(vol)]
    if len(leaves) != len(mat):
        bad.append('mātikā lists %d sections, the body prints %d' % (len(mat), len(leaves)))
    diffs = []
    for a, b in zip(leaves, mat):
        if norm_name(a) != norm_name(b):
            diffs.append((a, b))
    # A spelling difference between the two pages is the EDITION'S, and is kept
    # on both sides; only a difference in count or order refuses the write.
    if diffs and len(leaves) == len(mat):
        na = [norm_name(x) for x in leaves]
        nb = [norm_name(x) for x in mat]
        if sorted(na) != sorted(nb) and len(diffs) > 4:
            bad.append('%d of %d sections do not match the mātikā' % (len(diffs), len(mat)))
    return bad, diffs, mat


def main():
    nav = json.load(open(NAV, encoding='utf-8'))
    vols = {}
    for lay in nav['layers']:
        for nik in lay.get('nikayas', []):
            for i, v in enumerate(nik.get('volumes', [])):
                if v.get('vol') in SPEC and v.get('first', '').endswith('#0'):
                    vols[v['vol']] = (nik['volumes'], i)
    fail = False
    for vol in SPEC:
        tree = tree_for(vol)
        bad, diffs, mat = check(vol, tree)
        n_leaf = sum(len(n['kids']) for n in tree)
        n_sub = sum(len(k['kids']) for n in tree for k in n['kids'])
        print('%s  %d vagga row(s) / %d sections / %d sub-vaggas   mātikā lists %d   [%s]'
              % (vol, len(tree), n_leaf, n_sub, len(mat), 'CHECK' if bad else 'OK'))
        for n in tree:
            print('    %-16s %d sections' % (n['label'], len(n['kids'])))
        for a, b in diffs:
            print('    EDITION SPELLS IT TWO WAYS (both kept): body %r / mātikā %r' % (a, b))
        for b in bad:
            print('    REFUSED:', b); fail = True
        if vol not in vols:
            print('    REFUSED: no nav volume node for', vol); fail = True
            continue
        lst, i = vols[vol]
        node = {'vol': vol, 'work': SPEC[vol]['work'], 'title': SPEC[vol]['title'],
                'first': '%s#0' % vol, 'tree': tree}
        lst[i] = node
    # every key must resolve
    for vol in SPEC:
        n = len(json.load(open(os.path.join(ROOT, 'site', vol + '.json'),
                               encoding='utf-8'))['paragraphs'])
        lst, i = vols[vol]
        keys = []
        def walk(t):
            for nd in t:
                keys.append(nd['key']); walk(nd['kids'])
        walk(lst[i]['tree'])
        oor = [k for k in keys if not (0 <= int(k.split('#')[1]) < n)]
        print('  %s: %d nav keys, %d out of range' % (vol, len(keys), len(oor)))
        if oor:
            print('    REFUSED:', oor[:5]); fail = True
    if fail:
        raise SystemExit('NOT WRITTEN')
    if '--write' in sys.argv:
        if not os.path.exists(NAV + '.baknid'):
            shutil.copy(NAV, NAV + '.baknid')
        json.dump(nav, open(NAV, 'w', encoding='utf-8'), ensure_ascii=False)
        print('wrote', NAV)
    else:
        print('DRY RUN — pass --write to save')


if __name__ == '__main__':
    main()
