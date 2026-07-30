#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Jātaka nav as the Sixth Council prints it: TWO BHĀGAS.

THE EDITION MAKES THIS DIVISION ITSELF, and says so on its own title pages:

    Chaṭṭhasaṅgītipiṭakaṁ                 Chaṭṭhasaṅgītipiṭakaṁ
    Suttantapiṭake Khuddakanikāye         Suttantapiṭake Khuddakanikāye
    JĀTAKAPĀḶI                            JĀTAKAPĀḶI
    (Paṭhamo bhāgo)      [Pāḷi Series 22] (Dutiyo bhāgo)      [Pāḷi Series 23]

Each volume also carries its OWN mātikā, whose every page is headed
"Jātakapāḷi paṭhamabhāga" / "Jātakapāḷi dutiyabhāga" — a work the edition
treated as undivided would not print two separate tables of contents under two
different names.  An earlier version of this file grouped both volumes under one
Jātakapāḷi row on the ground that "the edition does not make this division".
That was simply wrong: it does, explicitly, and this builder now follows it.

    Jātakapāḷi (Paṭhamo bhāgo)            22Khu05
      1. Ekakanipāta   15 vaggas -> 150 jātakas
      …
      7. Sattakanipāta  2 vaggas ->  21 jātakas
      8. Aṭṭhakanipāta  NO vaggas ->  10 jātakas
      …
      16. Tiṁsanipāta   NO vaggas ->  10 jātakas      (ends at jātaka 520)
    Jātakapāḷi (Dutiyo bhāgo)             23Khu06
      17. Cattālīsanipāta … 22. Mahānipāta            (jātakas 521-547)

WHY THIS IS NOT THE APADĀNA CASE, and why both choices are coherent.  The
Apadāna is printed in two bhāgas too, but ITS break falls in the MIDDLE of
Therāpadāna, between vaggas 42 and 43 of a series the edition numbers 1-56
straight through — so grouping those two volumes under one row keeps a vagga
series from being cut in half.  The Jātaka's break falls exactly on a NIPĀTA
boundary and cuts no structural unit at all.

**THE DIVISION DOES NOT RENUMBER, AND THAT IS ASSERTED BELOW.** The second bhāga
opens at "17. Cattālīsanipāta" and "521. Tesakuṇajātaka" — the nipātas run 1-22
and the jātakas 1-547 continuously across the two books.  Renumbering either
series from 1 in the second volume would be this builder's most likely silent
failure, so it refuses to write unless the two trees join up.

A real gain over the single-row shape: each bhāga row is a book node in its own
volume, so it OPENS A READING PANE.  The one-row form could only expand, because
render() slices a single volume's paragraph array.
"""
import json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV  = os.path.join(ROOT, 'site/reader/nav.json')

# (vol, ord_lo, ord_hi, nav title, work label).  The titles are the edition's
# own, taken from each volume's printed title page — not "I"/"II", which the
# edition never sets.
BHAGA = [
    ('22Khu05', 0, 2985, 'Jātakapāḷi (Paṭhamo bhāgo)', 'Khuddaka: Jātaka I'),
    ('23Khu06', 0, 3675, 'Jātakapāḷi (Dutiyo bhāgo)',  'Khuddaka: Jātaka II'),
]

# The edition's own totals, per bhāga and combined.  NOT taken from tradition:
# the handoff records that a check against the traditional 559 Therāpadānas
# PASSED on data missing four printed headings.  Every number here is
# recomputable from the printed headings.
EXPECT = {
    '22Khu05': {'nipatas': (1, 16), 'jatakas': (1, 520),   'vaggas': 42},
    '23Khu06': {'nipatas': (17, 22), 'jatakas': (521, 547), 'vaggas': 0},
}
# Vaggas exist ONLY in nipātas 1-7.  Stated so the shape is asserted rather than
# merely produced: reading structure off the corpus `vagga` field instead would
# invent 15 vaggas in the upper nipātas, because that field sticks on a COLOPHON
# ("Gandhāravaggo dutiyo.") and carries forward to the end of the volume.
VAGGA_NIPATAS = {1: 15, 2: 10, 3: 5, 4: 5, 5: 3, 6: 2, 7: 2}


def head_kind(label):
    core = re.sub(r'^\d+(?:-\d+)?\.\s*', '', label).strip()
    core = re.sub(r'\s*\([\d\s.–-]+\)$', '', core)
    if re.search(r'nipāta\d*$', core, re.I):
        return 'book'
    if re.search(r'vagga\d*$', core, re.I):
        return 'vagga'
    return 'sutta'


def sections(vol):
    """[(ord, label, kind)] in printed order for one volume.

    Read from `sections/` AND from the `head` of any plain block in `uddana/`.
    THE SECOND SOURCE IS NOT OPTIONAL.  Where the corpus spliced two printed
    verses into one paragraph and the edition prints a jātaka heading between
    them, that heading cannot go in `sections` — a sections entry renders above
    the whole paragraph, i.e. above the PREVIOUS jātaka's last verse — so the
    builder emits it as the head of the block carrying the spliced verse, which
    puts it in the right place on the page.  Reading only `sections` therefore
    loses those jātakas from the tree and from ☰ Contents while they render
    perfectly: content present, in the right place, missing from the structure.
    22Khu05 has exactly two (205. Gaṅgeyyajātaka, 223. Puṭabhattajātaka), and
    the 1-547 check below is what caught them.
    """
    out = []
    p = os.path.join(ROOT, 'site/reader/sections', vol + '.json')
    for k, arr in json.load(open(p)).items():
        for i, h in enumerate(arr):
            out.append((int(k), i, h['l'], h.get('k')))
    up = os.path.join(ROOT, 'site/reader/uddana', vol + '.json')
    if os.path.exists(up):
        for k, arr in json.load(open(up)).items():
            for i, b in enumerate(arr):
                if b.get('head'):
                    # sorts after any sections entry on the same ordinal, since
                    # the block renders after the paragraph body
                    out.append((int(k), 1000 + i, b['head'], head_kind(b['head'])))
    # Several headings share one ordinal (a nipāta head, its first vagga head
    # and the first jātaka head all land on the volume's opening paragraph), so
    # the order WITHIN an ordinal is the order the builder emitted them, which
    # is the printed order.  Sorting by kind instead would put the jātaka before
    # its own nipāta on every such page.
    out.sort(key=lambda x: (x[0], x[1]))
    return [(o, l, k) for o, _, l, k in out]


def num_of(label):
    m = re.match(r'(\d+)(?:-\d+)?\.', label.strip())
    return int(m.group(1)) if m else None


def build_tree(vol, lo, hi):
    tree, cur_nip, cur_vag = [], None, None
    for o, label, k in sections(vol):
        if not (lo <= o < hi):
            continue
        key = '%s#%d' % (vol, o)
        if k == 'book':                       # nipāta
            cur_nip = {'label': label, 'key': key, 'kids': []}
            cur_vag = None
            tree.append(cur_nip)
        elif k == 'vagga':
            cur_vag = {'label': label, 'key': key, 'kids': []}
            (cur_nip['kids'] if cur_nip else tree).append(cur_vag)
        elif k in ('sutta', 'vatthu'):        # jātaka leaf
            leaf = {'label': label, 'key': key, 'kids': []}
            if cur_vag is not None:
                cur_vag['kids'].append(leaf)
            elif cur_nip is not None:
                cur_nip['kids'].append(leaf)
            else:
                tree.append(leaf)
    return tree


def leaves(tree):
    for nip in tree:
        for kid in nip['kids']:
            if kid['kids']:
                yield from kid['kids']
            else:
                yield kid


def main():
    bad, nodes, all_nips, all_jats = [], [], [], []

    for vol, lo, hi, title, work in BHAGA:
        tree = build_tree(vol, lo, hi)
        exp = EXPECT[vol]
        n0, n1 = exp['nipatas']
        j0, j1 = exp['jatakas']

        nips = [num_of(n['label']) for n in tree]
        if nips != list(range(n0, n1 + 1)):
            bad.append('%s: nipātas %s, expected %d-%d exactly as the edition '
                       'numbers them (the second bhāga does NOT restart at 1)'
                       % (vol, nips, n0, n1))

        nvag = sum(1 for n in tree for k in n['kids'] if k['kids'])
        if nvag != exp['vaggas']:
            bad.append('%s: %d vaggas, the edition prints %d' % (vol, nvag, exp['vaggas']))
        for n in tree:
            ni = num_of(n['label'])
            vs = [k for k in n['kids'] if k['kids']]
            want = VAGGA_NIPATAS.get(ni, 0)
            if len(vs) != want:
                bad.append('nipāta %d (%s) has %d vaggas, the edition prints %d'
                           % (ni, n['label'], len(vs), want))
            vnums = [num_of(v['label']) for v in vs]
            if vnums != list(range(1, len(vs) + 1)):
                bad.append('nipāta %d vagga numbering is %s, expected 1-%d'
                           % (ni, vnums, len(vs)))
        # the upper nipātas hold jātaka LEAVES directly — no invented vagga tier
        for n in tree:
            ni = num_of(n['label'])
            if ni not in VAGGA_NIPATAS and any(k['kids'] for k in n['kids']):
                bad.append('nipāta %d has a vagga level the edition does not print' % ni)

        jn = [num_of(l['label']) for l in leaves(tree)]
        if jn != list(range(j0, j1 + 1)):
            miss = [i for i in range(j0, j1 + 1) if i not in set(jn)]
            bad.append('%s: %d jātakas %s…%s, expected %d-%d continuous. missing %s'
                       % (vol, len(jn), jn[:3], jn[-3:], j0, j1, miss[:12]))

        # every leaf must live in this volume — a bhāga row opens a reading pane,
        # so a key pointing at the other volume would render nothing
        stray = [x['key'] for x in list(tree) + list(leaves(tree))
                 if not x['key'].startswith(vol + '#')]
        if stray:
            bad.append('%s: %d keys point outside the volume, e.g. %s'
                       % (vol, len(stray), stray[:3]))
        npara = len(json.load(open(os.path.join(ROOT, 'site', vol + '.json')))['paragraphs'])
        oor = [x['key'] for x in list(tree) + list(leaves(tree))
               if int(x['key'].split('#')[1]) >= npara]
        if oor:
            bad.append('%s: nav keys out of range: %s' % (vol, oor[:3]))

        all_nips += nips
        all_jats += jn
        nodes.append({'vol': vol, 'work': work, 'title': title,
                      'first': '%s#%d' % (vol, lo), 'tree': tree})
        print('%-28s %s   %2d nipātas (%d-%d), %2d vaggas, %3d jātakas (%d-%d)'
              % (title, vol, len(tree), n0, n1, nvag, len(jn), j0, j1))
        for n in tree:
            vs = [k for k in n['kids'] if k['kids']]
            nl = sum(len(k['kids']) for k in vs) if vs else len(n['kids'])
            print('     %-22s %s%3d jātakas'
                  % (n['label'], ('%2d vaggas -> ' % len(vs)) if vs else '  no vaggas -> ', nl))

    # --- THE JOIN: dividing the book must not renumber it -------------------
    if all_nips != list(range(1, 23)):
        bad.append('nipātas across the two bhāgas are %s…%s — the division must not '
                   'renumber; the edition runs 1-22 straight through'
                   % (all_nips[:3], all_nips[-3:]))
    if all_jats != list(range(1, 548)):
        bad.append('jātakas across the two bhāgas do not join up 1-547')

    if bad:
        print('\nREFUSING TO WRITE — the tree does not reproduce the edition:')
        for b in bad:
            print('  *', b)
        sys.exit(1)

    print('\njoin across the two bhāgas: nipātas 1-22 continuous, jātakas 1-547 '
          'continuous — the edition divides the book but does not renumber it')

    nav = json.load(open(NAV))
    canon = next(L for L in nav['layers'] if L['layer'] == 'canon')
    nk = next(n for n in canon['nikayas'] if n['nikaya'] == 'Khuddakanikāya')
    vols = nk['volumes']
    at = next(i for i, v in enumerate(vols) if v['vol'] in ('22Khu05', '23Khu06'))
    keep = [v for v in vols if v['vol'] not in ('22Khu05', '23Khu06')]
    nk['volumes'] = keep[:at] + nodes + keep[at:]
    shutil.copy(NAV, NAV + '.bakjat')
    json.dump(nav, open(NAV, 'w'), ensure_ascii=False)
    print('nav.json patched: Jātakapāḷi in TWO bhāgas (backup nav.json.bakjat)')


if __name__ == '__main__':
    main()

# Unlike the one-row form this replaces, each bhāga row OPENS a reading pane:
# every node, vagga and leaf lies in the row's own volume, so render()'s
# single-volume slice is sufficient.  The outstanding `render()` multi-volume
# work therefore no longer applies to the Jātaka — only to the Apadāna, whose
# break really does cut a vagga series in half.
