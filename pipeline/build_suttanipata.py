#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the Suttanipāta reader side-maps DIRECTLY FROM THE PRINTED PDF.

Why this exists
---------------
The Suttanipāta side-maps (`verse/18Khu01.json`, `uddana/18Khu01.json`) were
originally derived by *splitting the corpus paragraph text*.  The corpus itself
is defective for this book — it drops short pāda lines, drops sutta-end
colophons, and its prose extraction spliced non-contiguous passages together
and duplicated others.  Splitting a defective text faithfully reproduces the
defect, so the render inherited every one of them.

This builder instead parses the `pdftotext -layout` text of the printed Sixth
Council edition (the project's authority) into an ordered item stream —
headings, numbered verses with their pādas and per-sutta `(N)` counts, prose
paragraphs, and colophons — and maps it onto the corpus paragraph ordinals by
verse number.  Nothing in the corpus (`site/18Khu01.json`) is modified: the
reader renders `before + groups + after` from the side-map whenever a verse
entry exists, so the side-map alone controls the rendered content.

Verification is by `pipeline/verify_render_vs_pdf.py` in BOTH directions:
every PDF line must appear in the render, and every rendered prose block must
appear contiguously in the PDF.

Usage: python3 pipeline/build_suttanipata.py [--write]
"""
import re, json, os, sys, subprocess, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOL  = '18Khu01'
P0, P1 = 303, 479        # pdftotext page indices (0-based, \f split) of Suttanipāta
LO, HI = 705, 1869       # corpus paragraph range [LO, HI)

# ---------------------------------------------------------------- PDF parsing

HEADRE = re.compile(r'^(?:\d+\.\s+)?[A-ZĀĪŪṄÑṆṬḌḶ][^,]*?(?:sutta|pucchā|vagga|gāthā)\d*(?:\s*\([^)]*\))?$')
COLORE = re.compile(r'^[A-ZĀĪŪṄÑṆṬḌḶ]\S*(?:suttaṁ|vaggo|gāthā|pucchā|pāḷi|gāthāyo|niṭṭhitā)\d*\s+\S+\.?$'
                    r'|^\S+pāḷi\s+(?:niṭṭhitā|samattā)\.$')
PAGEHDR = re.compile(r'^\s*(?:\d+\s+)?(?:\d+\.\s+)?'
                     r'(?:\S+vagga|\S+nipāta|Suttanipātapāḷi|Khuddakanikāya|Suttuddānagāthā)'
                     r'(?:\s+\d+)?\s*$')
RUNHDR  = re.compile(r'^(?:\d+\.\s+)?\S+(?:vagga|nipāta|gāthā|pāḷi)\s+\d{3}$')
VNUM    = re.compile(r'^(\s{0,10})(\d+)\.(?:\s*([*+]))?(\s.*|)$')
CNT_END = re.compile(r'\s+\((\d+(?:-\d+)?)\)\s*$')

def _ind(l): return len(l) - len(l.lstrip(' '))

def _pagelines(page, pi):
    out = []
    for idx, l in enumerate(page.split('\n')):
        if re.match(r'^\s*_{10,}', l): break          # footnote rule: rest is apparatus
        if not l.strip(): continue
        if re.fullmatch(r'\s*_+\s*', l): continue     # decorative rule between suttas
        if re.fullmatch(r'\s*\d+\s*', l): continue    # bare page number
        if idx <= 2 and PAGEHDR.match(l): continue    # running page header
        out.append((pi, l))
    return out

def parse_pdf(layout_text):
    pages = layout_text.split('\f')
    lines = []
    for pi in range(P0, P1 + 1):
        lines += _pagelines(pages[pi], pi)

    def is_head(t, d): return d >= 15 and HEADRE.match(t) and not COLORE.match(t)
    def is_colo(t, d): return d >= 12 and COLORE.match(t)

    items, i = [], 0
    while i < len(lines):
        pi, l = lines[i]; d = _ind(l); t = l.strip()
        if RUNHDR.match(t):                       # mid-page running header w/ page no.
            i += 1; continue
        if is_colo(t, d):
            items.append({'k': 'colo', 't': t, 'p': pi}); i += 1; continue
        if is_head(t, d):
            items.append({'k': 'head', 't': t, 'p': pi}); i += 1; continue
        m = VNUM.match(l)
        if m:
            V = len(m.group(1)); num = int(m.group(2)); rest = m.group(4).strip()
            padas, count = [], None
            def take(s):
                nonlocal count
                s = s.rstrip()
                mc = CNT_END.search(s)
                if mc: count = mc.group(1); s = s[:mc.start()].rstrip()
                if s: padas.append(s)
            if rest: take(rest)
            j = i + 1
            while j < len(lines):
                pj, l2 = lines[j]; d2 = _ind(l2); t2 = l2.strip()
                if is_colo(t2, d2) or is_head(t2, d2): break
                if re.fullmatch(r'\(\d+(?:-\d+)?\)', t2): count = t2[1:-1]; j += 1; continue
                # a new verse number always ends this verse: indents shift page to page,
                # so relative indent alone cannot be trusted across a page break
                if d2 <= 10 and VNUM.match(l2): break
                if pj != pi:
                    if count is not None: break
                    if not (len(t2) <= 64 and re.search(r'[,.;]$', t2)): break
                if d2 > V: take(t2); j += 1; continue
                break
            items.append({'k': 'verse', 'n': num, 'padas': padas, 'count': count, 'p': pi})
            i = j; continue
        # prose: a paragraph starts indented; wrapped/page-break lines sit at column <3
        if d <= 2 and items and items[-1]['k'] == 'prose':
            items[-1]['t'] += ' ' + t
        else:
            items.append({'k': 'prose', 't': t, 'p': pi})
        j = i + 1
        while j < len(lines):
            pj, l2 = lines[j]; d2 = _ind(l2); t2 = l2.strip()
            if d2 > 2 or VNUM.match(l2) or is_colo(t2, d2) or is_head(t2, d2): break
            items[-1]['t'] += ' ' + t2; j += 1
        i = j
    return items

# ------------------------------------------------------------------- mapping

def build(items, paras):
    """Map the PDF item stream onto corpus ordinals LO..HI-1 by verse number."""
    ords = list(range(LO, HI))
    ns   = [int(paras[o]['n']) for o in ords]
    vpos = [k for k, x in enumerate(items) if x['k'] == 'verse']

    # For each corpus paragraph, the position of the PDF verse that opens it.
    starts, cur = [], 0
    for n in ns:
        while cur < len(vpos) and items[vpos[cur]]['n'] != n: cur += 1
        if cur >= len(vpos):
            raise SystemExit(f'verse {n} not found in PDF stream')
        starts.append(vpos[cur]); cur += 1
    starts.append(len(items))

    verse, uddana = {}, {}
    # Anything before the book's first verse belongs to ord LO — EXCEPT the
    # "Namo tassa…" homage, which the edition sets as a display line at the head
    # of every book. It belongs in sections/<vol>.json as k:'incipit' so the
    # reader styles it, not in the first paragraph's intro prose.
    head_lead = [x['t'] for x in items[:starts[0]]
                 if x['k'] == 'prose' and 'amo tassa' not in x['t']]

    for idx, o in enumerate(ords):
        s, e = starts[idx], starts[idx + 1]
        seg = items[s:e]
        groups, counts, nums = [], [], []
        for x in seg:
            if x['k'] == 'verse':
                groups.append(x['padas']); counts.append(x['count']); nums.append(x['n'])
        # prose that trails this paragraph's last verse, up to the next paragraph;
        # once a colophon appears we are into the uddāna/colophon block.
        last_v = max(k for k, x in enumerate(seg) if x['k'] == 'verse')
        after, blocks, seen_colo = [], [], False
        for x in seg[last_v + 1:]:
            if x['k'] == 'head':
                break          # past the next sutta's heading: that prose is ITS intro
            if x['k'] == 'colo':
                seen_colo = True; blocks.append({'label': '', 'lines': [x['t']], 'app': []})
            elif x['k'] == 'prose':
                if not seen_colo: after.append(x['t'])
                elif x['t'].startswith('Tassuddāna'):
                    blocks.append({'label': x['t'], 'lines': [], 'app': []})
                elif blocks and blocks[-1]['label']: blocks[-1]['lines'].append(x['t'])
                else: blocks.append({'label': '', 'lines': [x['t']], 'app': []})
        # prose sitting between the previous paragraph's colophon and this one's
        # first verse (sutta intro narrative) becomes this paragraph's `before`
        before = []
        if idx > 0:
            prev_last = max(k for k, x in enumerate(items[starts[idx-1]:s]) if x['k'] == 'verse')
            tail = items[starts[idx-1]:s][prev_last + 1:]
            # Only prose that follows this sutta's HEADING is its intro.  Prose
            # sitting between the previous sutta's colophon and that heading is
            # the previous VAGGA's closing "Tassuddānaṁ" mnemonic — it belongs to
            # the previous paragraph's uddāna block, which already collects it.
            # (Treating a colophon as the boundary put every vagga's uddāna at the
            # top of the NEXT vagga as well, so it rendered twice.)
            seen_head = False
            for x in tail:
                if x['k'] == 'head': seen_head = True
                elif x['k'] == 'colo': seen_head = False
                elif x['k'] == 'prose' and seen_head: before.append(x['t'])
        else:
            before = head_lead

        ent = {'groups': groups}
        if any(c is not None for c in counts): ent['counts'] = counts
        if len(groups) > 1: ent['nums'] = nums
        if before: ent['before'] = before
        if after:  ent['after'] = after
        verse[str(o)] = ent
        if blocks: uddana[str(o)] = blocks
    return verse, uddana

# -------------------------------------------------------------------- driver

def main():
    write = '--write' in sys.argv
    lay = subprocess.run(['pdftotext', '-layout', f'{ROOT}/pali-unicode/{VOL}.pdf', '-'],
                         capture_output=True, text=True).stdout
    items = parse_pdf(lay)
    kinds = {}
    for x in items: kinds[x['k']] = kinds.get(x['k'], 0) + 1
    print('parsed items:', kinds)

    paras = json.load(open(f'{ROOT}/site/{VOL}.json', encoding='utf-8'))['paragraphs']
    verse, uddana = build(items, paras)

    nv = sum(len(e['groups']) for e in verse.values())
    print(f'mapped {len(verse)} paragraphs, {nv} verses, '
          f'{sum(len(e.get("before",[])) for e in verse.values())} before-prose, '
          f'{sum(len(e.get("after",[])) for e in verse.values())} after-prose, '
          f'{sum(len(v) for v in uddana.values())} colophon/uddāna blocks')

    for name, new in (('verse', verse), ('uddana', uddana)):
        path = f'{ROOT}/site/reader/{name}/{VOL}.json'
        old = json.load(open(path, encoding='utf-8'))
        merged = {k: v for k, v in old.items() if not (LO <= int(k) < HI)}
        merged.update(new)
        merged = {k: merged[k] for k in sorted(merged, key=int)}
        if write:
            if not os.path.exists(path + '.presn'): shutil.copy(path, path + '.presn')
            json.dump(merged, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
            print('wrote', path)
        else:
            print(f'[dry-run] {name}: {len(old)} -> {len(merged)} keys')

if __name__ == '__main__':
    main()
