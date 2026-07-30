#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the four 19Khu02 book nodes and patch them into nav.json IN PLACE.

19Khu02 carries FOUR books (Vimānavatthu, Petavatthu, Theragāthā, Therīgāthā).
Every book needs its own nav node with a correct `first` ordinal, because the
reader builds BOOKSPAN from those ordinals and slices `cv.paras` to
[start, next_start) — without all four, one book bleeds into the next.

Why this is a per-volume script rather than a re-run of build_khuddaka_nav.py:
that builder rewrites the WHOLE Khuddaka nikāya node, which would blow away
18Khu01's hand-built Itivuttaka/Suttanipāta `nipatas` (nested) structure.  This
script touches only the four 19Khu02 nodes.

BOOK BOUNDARIES — CORRECTED.  docs/19Khu02_structure.json originally recorded
Theragāthā at ord 1849 and Therīgāthā at ord 3140.  Both were LATE, because the
`book` field is a running header and on a new book's first page(s) it prints the
NIPĀTA name ('Ekakanipāta'), not the book title; a carry-forward over those
paragraphs puts the first '…pāḷi' occurrence after the real start.  The reliable
signal is the verse number resetting to 1.  Verified four ways, see verify().
"""
import json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV  = os.path.join(ROOT, 'site/reader/nav.json')
VOL  = '19Khu02'

# (title, expected verse count) — the edition's own numbering, used as a check.
BOOKS = [('Vimānavatthupāḷi', 1289), ('Petavatthupāḷi', 814),
         ('Theragāthāpāḷi', 1288), ('Therīgāthāpāḷi', 524)]


def load_paras():
    return json.load(open(os.path.join(ROOT, 'site', VOL + '.json')))['paragraphs']


def book_starts(paras):
    """Book starts = every paragraph whose n resets to 1 after a larger n."""
    starts = [0]
    for i in range(1, len(paras)):
        a, b = paras[i - 1].get('n'), paras[i].get('n')
        if b == 1 and isinstance(a, int) and a > 1:
            starts.append(i)
    return starts


# Three PDF section headings were captured as corpus paragraphs, carrying the
# heading's own ordinal as `n` — so they break the verse-number sequence.  They
# are a BODY defect (hide + re-place as headings), not a boundary problem, so
# the boundary check identifies and excludes them rather than failing on them.
LEAKED_HEAD = re.compile(r'^\s*\d+\.\s*[A-ZĀĪŪṄÑṆṬḌḶ][^,;]{0,70}vatthu(?:\s*\(\d+\))?\s*$')


def leaked_headings(paras, lo, hi):
    out = []
    for i in range(lo, hi):
        t = (paras[i].get('text') or '').strip()
        if LEAKED_HEAD.match(t):
            out.append(i)
    return out


def verify(paras, starts):
    """Self-verifying: refuse to write unless every check passes."""
    errs = []
    if len(starts) != len(BOOKS):
        errs.append(f'expected {len(BOOKS)} book starts, found {len(starts)}: {starts}')
        return errs
    bounds = list(zip(starts, starts[1:] + [len(paras)]))
    for (title, nverses), (lo, hi) in zip(BOOKS, bounds):
        ns = [p.get('n') for p in paras[lo:hi] if isinstance(p.get('n'), int)]
        if not ns:
            errs.append(f'{title}: no numbered paragraphs'); continue
        if ns[0] != 1:
            errs.append(f'{title}: first n is {ns[0]}, expected 1')
        if max(ns) != nverses:
            errs.append(f'{title}: last verse {max(ns)}, edition prints {nverses}')
        leaked = leaked_headings(paras, lo, hi)
        if leaked:
            print(f'  NOTE {title}: {len(leaked)} leaked section headings captured as '
                  f'paragraphs (body defect, fix separately): {leaked}')
        ns = [p.get('n') for i, p in enumerate(paras[lo:hi], lo)
              if isinstance(p.get('n'), int) and i not in set(leaked)]
        if ns != sorted(ns):
            bad = [(i, a, b) for i, (a, b) in enumerate(zip(ns, ns[1:])) if b < a][:5]
            errs.append(f'{title}: verse numbers not monotonic (first descents {bad})')
        # the '…pāḷi' book-field form must appear inside the span and nowhere before it
        stem = title.replace('pāḷi', '').lower()
        first_named = next((i for i in range(len(paras))
                            if (paras[i].get('book') or '').lower().startswith(stem)), None)
        if first_named is None or not (lo <= first_named < hi):
            errs.append(f'{title}: book-field form first seen at {first_named}, outside [{lo},{hi})')
    return errs


SEC = os.path.join(ROOT, 'site/reader/sections', VOL + '.json')


def sections_items():
    """Every PDF-derived heading as (ord, label, kind), in printed order."""
    sec = json.load(open(SEC))
    out = []
    for k, arr in sec.items():
        for h in arr:
            if h.get('k') in ('book', 'vagga', 'sutta'):
                out.append((int(k), h['l'], h['k']))
    out.sort(key=lambda x: (x[0], ['book', 'vagga', 'sutta'].index(x[2])))
    return out


def build_tree(lo, hi):
    """book -> division/nipāta -> vagga -> leaf, from the printed headings.

    Two shapes are folded into one:
      * Vimānavatthu   division (Itthivimāna / Purisavimāna) -> vagga -> vimāna,
        with the vagga numbers running CONTINUOUSLY 1-7 across the divisions
        (the edition's own numbering — do not renumber per division);
      * Theragāthā     nipāta -> vagga -> theragāthā (only Ekakanipāta has vaggas).
    A level with no children renders as a clickable leaf at its own depth.

    SUB-SERIES.  Inside Pāricchattakavagga the fifth vimāna, Guttilavimāna, is
    itself followed by a numbered series of 36 minor vimānas whose numbering
    restarts at 1; the vagga then resumes at 6.  Counting those as vagga leaves
    gave 46 where the edition has 10 (and 121 vimānas where the standard count
    is 85).  A leaf whose number is not the next one expected therefore belongs
    to the PRECEDING leaf, not to the vagga.
    """
    items = [x for x in sections_items() if lo <= x[0] < hi
             and not re.match(r'(Nidānagāthā|Tass?uddānaṁ|Tatruddānaṁ)', x[1])]
    tree, cur_div, cur_vag, cur_leaf, expect = [], None, None, None, 1
    seen_div, sub_n = {}, None
    for o, label, kind in items:
        key = f'{VOL}#{o}'
        if kind == 'book':
            # The division head is REPRINTED as a running header at the top of a
            # later page ('1. Itthivimāna' again at ord483, sharing its line with
            # 4. Mañjiṭṭhakavagga).  Reuse the division already open rather than
            # opening a second one, or vaggas 4-7 hang off a duplicate.
            fold = re.sub(r'^\d+\.\s*', '', label).strip().lower()
            if fold in seen_div:
                cur_div = seen_div[fold]
            else:
                cur_div = {'label': label, 'key': key, 'kids': []}
                seen_div[fold] = cur_div
                tree.append(cur_div)
            cur_vag, cur_leaf, expect, sub_n = None, None, 1, None
        elif kind == 'vagga':
            cur_vag = {'label': label, 'key': key, 'kids': []}
            (cur_div['kids'] if cur_div else tree).append(cur_vag)
            cur_leaf, expect, sub_n = None, 1, None
        else:
            host = cur_vag or cur_div
            m = re.match(r'(\d+)\.', label)
            n = int(m.group(1)) if m else None
            if host is None:
                tree.append({'label': label, 'key': key, 'kids': []}); continue
            # SUB-SERIES.  A leaf numbered 1 when the vagga is already past its
            # second member opens a series belonging to the PRECEDING leaf
            # (Guttilavimāna's 36 minor vimānas).  It cannot be closed by
            # comparing against the vagga's own counter, because the sub-numbers
            # run 1..36 straight THROUGH it — 6,7,8… match the vagga's expected
            # 6,7,8 exactly, which is how the whole series was mistaken for vagga
            # members.  What does close it is the numbering DROPPING: the series
            # ends at 36 and the vagga resumes at 6.
            if n is not None and cur_leaf is not None:
                if sub_n is None and n == 1 and expect > 2:
                    sub_n = 1
                    cur_leaf.setdefault('kids', []).append(
                        {'label': label, 'key': key, 'kids': []})
                    continue
                if sub_n is not None:
                    if n == sub_n + 1:
                        sub_n = n
                        cur_leaf['kids'].append({'label': label, 'key': key, 'kids': []})
                        continue
                    sub_n = None            # numbering dropped: back to the vagga
            cur_leaf = {'label': label, 'key': key, 'kids': []}
            host['kids'].append(cur_leaf)
            expect = (n + 1) if n is not None else expect + 1
    return tree


# The edition's own totals, used to refuse a tree that does not reproduce them.
# Sources: the counts printed in each book's closing uddāna where it gives one
# (Petavatthu's vagguddāna prints "Vatthūni ekapaññāsaṁ" = 51), otherwise the
# standard divisions of the book.
LEAF_SPEC = {'Vimānavatthupāḷi': 85, 'Petavatthupāḷi': 51,
             'Theragāthāpāḷi': 264, 'Therīgāthāpāḷi': 73}


def leaves(tree, depth=0):
    """Leaf nodes at the vagga level — a sub-series hanging off a leaf is not one."""
    out = []
    for nd in tree:
        if nd.get('kids') and depth < 2:
            out += leaves(nd['kids'], depth + 1)
        else:
            out.append(nd)
    return out


def tree_stats(tree, depth=0, acc=None):
    acc = acc if acc is not None else {}
    for nd in tree:
        acc[depth] = acc.get(depth, 0) + 1
        if nd.get('kids'):
            tree_stats(nd['kids'], depth + 1, acc)
    return acc


def main():
    paras = load_paras()
    starts = book_starts(paras)
    errs = verify(paras, starts)
    for e in errs:
        print('FAIL:', e)
    if errs:
        sys.exit(1)
    bounds = list(zip(starts, starts[1:] + [len(paras)]))
    for (title, nv), (lo, hi) in zip(BOOKS, bounds):
        print(f'  {title:20} ord {lo:5d}-{hi-1:<5d}  {hi-lo:5d} ¶  verses 1-{nv}')

    # chapter nodes come from build_khuddaka_nav's own logic, re-run with the
    # corrected spans (it now applies the same n-reset snap).
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'bkn', os.path.join(ROOT, 'pipeline/build_khuddaka_nav.py'))
    bkn = importlib.util.module_from_spec(spec); spec.loader.exec_module(bkn)
    nodes = bkn.build_volume(VOL)
    got = {int(n['first'].split('#')[1]) for n in nodes}
    if got != set(starts):
        print('FAIL: chapter builder disagrees on book starts:', sorted(got), 'vs', starts)
        sys.exit(1)

    # Replace each book's flat vagga list with the PDF-derived nested tree.
    bounds = list(zip(starts, starts[1:] + [len(paras)]))
    bad = []
    for nd, (lo, hi) in zip(nodes, bounds):
        t = build_tree(lo, hi)
        if not t:
            print(f'  NOTE {nd["title"]}: no PDF headings, keeping flat vaggas')
            continue
        nd.pop('vaggas', None); nd.pop('nipata', None)
        nd['tree'] = t
        st = tree_stats(t)
        got, want = len(leaves(t)), LEAF_SPEC.get(nd['title'])
        ok = 'OK' if got == want else 'MISMATCH (edition has %s)' % want
        print('  %-20s tree %-22s leaves %d  %s' % (nd['title'],
              ' -> '.join('%d' % st[d] for d in sorted(st)), got, ok))
        if got != want:
            bad.append('%s: %d leaves, edition has %d' % (nd['title'], got, want))

    # A sub-series title is SUBORDINATE to the vimāna it hangs off, but the
    # section builder cannot know that (it only sees a numbered heading), so all
    # 36 of Guttilavimāna's minor vimānas were emitted at the same heading weight
    # as the vagga's own members — the tree had the hierarchy, the reading pane
    # did not.  The tree is where the sub-series is identified, so demote them
    # here, to the reader's existing `vatthu` class (the subordinate-title class
    # used for the Dhammapada's vatthu headings).
    sub_keys = set()
    for nd in nodes:
        for lvl1 in nd.get('tree', []):
            for lvl2 in lvl1.get('kids', []):
                for leaf in lvl2.get('kids', []):
                    for sub in leaf.get('kids', []):
                        sub_keys.add(sub['key'])
    if sub_keys:
        sec = json.load(open(SEC))
        demoted = 0
        # a sub-series ordinal may also carry its PARENT's heading (Guttilavimāna
        # and its first sub-item share ord 311), so demote by label, not by ordinal
        sublabels = {}
        for nd in nodes:
            for lvl1 in nd.get('tree', []):
                for lvl2 in lvl1.get('kids', []):
                    for leaf in lvl2.get('kids', []):
                        for sub in leaf.get('kids', []):
                            sublabels.setdefault(sub['key'].split('#')[1], set()).add(sub['label'])
        for o, arr in sec.items():
            for h in arr:
                if h.get('k') == 'sutta' and h['l'] in sublabels.get(o, ()):
                    h['k'] = 'vatthu'; demoted += 1
        json.dump(sec, open(SEC, 'w'), ensure_ascii=False)
        print('  demoted %d sub-series heading(s) to the subordinate `vatthu` class' % demoted)

    if bad:
        for b in bad:
            print('FAIL:', b)
        sys.exit(1)

    nav = json.load(open(NAV))
    canon = next(L for L in nav['layers'] if L['layer'] == 'canon')
    nk = next(n for n in canon['nikayas'] if n['nikaya'] == 'Khuddakanikāya')
    old = [v for v in nk['volumes'] if v['vol'] == VOL]
    if len(old) != len(nodes):
        print(f'NOTE: nav had {len(old)} {VOL} nodes, writing {len(nodes)}')
    at = nk['volumes'].index(old[0])
    nk['volumes'] = nk['volumes'][:at] + nodes + \
                    [v for v in nk['volumes'][at:] if v['vol'] != VOL]
    shutil.copy(NAV, NAV + '.bak19')
    json.dump(nav, open(NAV, 'w'), ensure_ascii=False)
    print(f'nav.json patched: {len(nodes)} {VOL} book nodes (backup nav.json.bak19)')


if __name__ == '__main__':
    main()
