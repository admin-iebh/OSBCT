#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild a volume's variant apparatus from the printed footnote blocks.

`pipeline/verify_apparatus.py` measures the damage; this repairs it.  For each
printed page it parses the block below the underscore rule into numbered notes
(the block is often two-column) plus `*`/`+` cross-reference lines, then anchors
each note to the paragraph that actually carries its marker.

Anchoring rule: a footnote marker is a digit attached to the end of a Pāḷi word
("nhāru2", "Byūhāni1").  Note k on page P belongs to the paragraph anchored to
page P whose text carries marker k.  Candidate paragraphs are widened by one
page either side, because a paragraph straddling a page break keeps the
`pdf_page` of its first line while its markers may print on the next page.

Nothing is guessed: a note whose marker cannot be located is reported as
UNANCHORED and left out, so the gap stays visible instead of being silently
attached to the wrong paragraph.

Usage: python3 pipeline/rebuild_apparatus.py <VOL> [--write] [--max N]
"""
import json, os, re, shutil, subprocess, sys
import importlib.util as _ilu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fnblock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = _ilu.spec_from_file_location('vr', f'{ROOT}/pipeline/verify_render_vs_pdf.py')
vr = _ilu.module_from_spec(_spec); _spec.loader.exec_module(vr)

# A marker is the digit(s) attached to the END of a Pāḷi word: "nhāru2",
# "osadhehi2.", "samāyutā3ti", "Byūhāni11". The lookbehind (a word char, not a
# digit) is what keeps paragraph numbers like "3. Abrahmacariyā" out — those
# have nothing but space before them. Multi-digit markers are real: pages run
# past note 10.
# A marker attaches with NO space to whatever it annotates — usually the end of
# a Pāḷi word ("nhāru2", "osadhehi2.", "Byūhāni11") but just as often to closing
# punctuation, because it annotates a whole phrase: "(matthaluṅgaṁ).4",
# "muttanti.5". Requiring a letter before the digit missed every one of those.
# The lookbehind still excludes paragraph numbers ("3. Abrahmacariyā"), which
# have whitespace or start-of-string before them.
MARK = re.compile(r'(?<=[^\W\d_.)\]”])(\d+)(?!\d)|(?<=[.)\]”])(\d+)(?!\d)')
SIGLA = ('Sī', 'Syā', 'Kaṁ', 'Kaṃ', 'I', 'Ka', 'Ṭṭha', 'Niddesa',
         'sabbattha', 'bahūsu', 'katthaci', 'sabbatthapi', '?')


def pdf_path(vol):
    for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
        p = f'{ROOT}/{d}/{vol}.pdf'
        if os.path.exists(p): return p
    raise SystemExit(f'no PDF for {vol}')


def page_notes(page_text):
    """({n: text}, [xref lines]) for one printed page."""
    lines = page_text.split('\n')
    k = next((i for i, l in enumerate(lines) if re.match(r'^\s*_{10,}', l)), None)
    if k is None:
        # The rule may be a GRAPHIC.  Until 2026-07-26ak this returned nothing
        # for those pages, so their cells were stored NOWHERE — fourteen pages,
        # ~17 variant readings and cross-references, silently absent from the
        # apparatus of two SHIPPED volumes.  See pipeline/fnblock.py.
        st = fnblock.fn_start(lines)
        if st is None:
            return {}, []
        k = st - 1                     # the rule would have been the line above
    cells = []
    for l in lines[k + 1:]:
        if not l.strip() or re.match(r'^\s*_{10,}', l):
            continue
        # two-column blocks: split on wide gaps, keep left-to-right order
        for c in re.split(r'\s{3,}', l.rstrip()):
            if c.strip():
                cells.append((len(l) - len(l.lstrip()), c.strip()) if not cells else (0, c.strip()))
    # A marker can carry MORE THAN ONE printed note: the edition writes the second
    # as "1-1." against the same marker 1 (20Khu03 p26, p53, p366; also 18Khu01
    # p141/182/209).  Recognising only "^N." dropped every one of them — 11 lost
    # variants in 20Khu03 alone — so notes are a LIST per marker, not one string.
    notes, xrefs, cur = {}, [], None
    for _, c in cells:
        # …and the marker's period is sometimes simply not set (18Khu01 p151
        # prints "3 Anupavādo anupaghāto (Syā, I, Ka)").  Accept a bare number
        # only when a capital or an opening bracket follows, so a continuation
        # line that happens to start with a figure is not mistaken for a marker.
        m = (re.match(r'^(\d+)(?:-\d+)?\.\s*(.*)$', c)
             or re.match(r'^(\d+)\s+(?=[A-ZĀĪŪṄÑṆṬḌḶ(])(.*)$', c))
        if m:
            cur = int(m.group(1))
            notes.setdefault(cur, []).append(m.group(2).strip())
        elif re.match(r'^[*+]', c):
            xrefs.append(c); cur = None
        elif cur is not None and notes.get(cur):
            notes[cur][-1] = (notes[cur][-1] + ' ' + c).strip()   # wrapped continuation
    return notes, xrefs


def _marks(text):
    return {g for m in MARK.finditer(text) for g in m.groups() if g}


def _is_sigla(group):
    """True when a parenthesised group is a WITNESS list, not something else.

    The same brackets carry three different things in this edition: witness
    sigla '(Sī, Syā)', editorial cross-references '(Saṁ 1. 188)', and an
    alternative reading printed in brackets '(Gantvāna Hatthiniṁ puraṁ)'.
    Only the first is a sigla group.
    """
    parts = [x.strip() for x in group.split(',')]
    if not parts or not all(parts):
        return False
    for x in parts:
        if x in SIGLA:
            continue
        if '-' in x and all(y in SIGLA for y in x.split('-')):   # Sī-Ṭṭha, Ka-Ṭṭha
            continue
        return False
    return True


def parse_variants(text):
    """Split a note into {reading, sigla} pairs; unparsed notes keep text only.

    !!! The previous implementation split the note on every comma before a
    capital, which also split INSIDE the sigla group — '(Sī, Syā)' became
    'Padumaṁ (Sī' and 'Syā)', neither of which parsed.  The result was that
    EVERY multi-witness variant in the corpus was silently reduced to text with
    no structure: across all of 19Khu02, 629 notes parsed and every single one
    had exactly one siglum, which is impossible for this edition.  Since the
    structured variant apparatus is the project's stated highest-value output,
    that was the most costly kind of silent failure.

    Scan for sigla groups instead, and take each variant's reading as the text
    running up to its own group.
    """
    out, last = [], 0
    for m in re.finditer(r'\(([^)]*)\)', text):
        if not _is_sigla(m.group(1)):
            continue
        reading = text[last:m.start()]
        last = m.end()
        # a note glued to its neighbour by a failed two-column split keeps the
        # neighbour's printed marker ("Bhāsite (Sī) 3. Khiḍḍaṁ ratiṁ (Syā, I)")
        reading = re.sub(r'^\s*\d+\.\s*', '', reading.strip().lstrip(','))
        # editorial remarks trailing the PREVIOUS variant are not this reading
        reading = re.sub(r'^(evamuparipi\.|evamuparipī\.)\s*', '', reading).strip()
        reading = reading.strip().strip(',').strip()
        if reading:
            out.append({'reading': reading,
                        'sigla': [x.strip() for x in m.group(1).split(',')]})
    return out


def main():
    a = sys.argv[1:]
    vol = a[0]; write = '--write' in a
    cap = int(a[a.index('--max') + 1]) if '--max' in a else 20
    pages = subprocess.run(['pdftotext', '-layout', pdf_path(vol), '-'],
                           capture_output=True, text=True).stdout.split('\f')
    paras = json.load(open(f'{ROOT}/site/{vol}.json', encoding='utf-8'))['paragraphs']
    by_page = {}
    for i, p in enumerate(paras):
        if p.get('pdf_page'): by_page.setdefault(p['pdf_page'], []).append(i)

    # Markers also live in text the reader draws from side-maps rather than from
    # the corpus paragraph (restored verses, colophons, uddāna mnemonics), so the
    # searchable text for an ordinal is the paragraph PLUS anything attached to it.
    def side(o):
        s = ''
        for e in (VERSE.get(str(o)) or {},):
            for g in e.get('groups', []): s += ' ' + ' '.join(g)
            for k in ('before', 'after'):
                v = e.get(k)
                if isinstance(v, str): s += ' ' + v
                elif v: s += ' ' + ' '.join(x if isinstance(x, str) else ' '.join(x.get('gatha', [])) for x in v)
        for b in (UDD.get(str(o)) or []):
            s += ' ' + (b.get('label') or '') + ' ' + ' '.join(b.get('lines', []))
        return s
    def _load(p):
        return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    VERSE = _load(f'{ROOT}/site/reader/verse/{vol}.json')
    UDD = _load(f'{ROOT}/site/reader/uddana/{vol}.json')
    old = json.load(open(f'{ROOT}/site/reader/apparatus/{vol}.appk.json', encoding='utf-8'))
    PAGE_OFF = vr.page_offset(vol, paras, pages)
    new, unanchored, xref_by_ord = {}, [], {}
    for pi, page in enumerate(pages):
        notes, xrefs = page_notes(page)
        if not notes and not xrefs: continue
        # `pdf_page` anchors drift by up to ~3 pages in places (12Sam01 is known
        # to be off by +2 throughout), and a paragraph straddling a page break
        # keeps the page of its FIRST line, so search a window rather than a page.
        # `pi` is a pdftotext INDEX; `by_page` is keyed by the corpus `pdf_page`
        # field, and the two differ by a per-volume offset that is not the same
        # across volumes (see vr.page_offset).  Without converting, every note
        # anchored a page early — masked by the +/-3 window, which then attached
        # it to whatever earlier paragraph happened to carry the same marker
        # number (19Khu02 put page 19's notes 1 and 2 on ords 0 and 3).
        # !!! A NOTE BELONGS TO THE PARAGRAPH THAT *COVERS* ITS PAGE, NOT TO
        # THE FIRST PARAGRAPH *STARTING* ON IT.
        # The old rule took every paragraph STARTING within +/-3 pages and gave
        # the note to the first of them carrying that marker number.  Marker
        # numbers restart on every page, so several candidates in a 7-page
        # window routinely carry the same digit and the note landed on whichever
        # came first — measured: 405 of 435 extra copies across six volumes are
        # unexplained by the printed cell count, e.g. 'Visuddho (Syā)' printed
        # ONCE on p20 and stored at BOTH ord22 and ord28
        # (claude/apparatus_question_settled.md).
        # A paragraph covers from its own first page up to the next paragraph's,
        # so the candidates for page P are the paragraphs that START on P plus
        # the ONE that started earlier and is still running through it — which
        # is what a footnote marker on P can actually refer to.  Ordered
        # covering-first, because a marker on P most often belongs to the text
        # already in progress at the top of the page.
        _pg = pi - PAGE_OFF
        _starts = by_page.get(_pg, [])
        _prev = [o for pg in sorted(by_page) if pg < _pg for o in by_page[pg]]
        # ...BUT `pdf_page` DRIFTS, by up to ~3 pages in places (12Sam01 is off
        # by +2 throughout), and where it does, "covers" is computed from the
        # wrong pages.  So the covering set is tried FIRST and the old window is
        # kept BEHIND it as a rescue: `hit` takes the first candidate carrying
        # the marker, so a real covering paragraph always wins and the window
        # only catches what drift put out of reach.
        # Measured over four volumes: covering-only fixed 08Di03 (5 unanchored
        # -> 0) but LOST two notes in 06Di01 (0 -> 2), which is drift.
        # Covering-first-then-window keeps both.
        _win = [o for d in (0, -1, 1, -2, 2, -3, 3)
                for o in by_page.get(_pg + d, [])]
        cands, _seen = [], set()
        for o in (([_prev[-1]] if _prev else []) + _starts + _win):
            if o not in _seen:
                _seen.add(o); cands.append(o)
        for n, text in sorted((k, t) for k, lst in notes.items() for t in lst):
            hit = next((o for o in cands
                        if str(n) in _marks(paras[o]['text'] + side(o))), None)
            if hit is None:
                unanchored.append((pi, n, text[:60])); continue
            new.setdefault(str(hit), []).append(
                {'n': n, 'text': text, 'variants': parse_variants(text), 'xrefs': []})
        if xrefs and cands:
            xref_by_ord.setdefault(str(cands[0]), []).extend(xrefs)

    # ---- MERGE, not replace -------------------------------------------------
    # The page is the authority, so PDF-derived notes win. But this parser does
    # not place everything, so an existing note is KEPT when its text really is
    # printed somewhere in this volume and the rebuild did not reproduce it.
    # An existing note whose text is NOT printed anywhere is a splice or a
    # fabrication (exactly what verify_apparatus.py flags) and is dropped.
    import importlib.util as _il
    _sp = _il.spec_from_file_location('vr', f'{ROOT}/pipeline/verify_render_vs_pdf.py')
    _vr = _il.module_from_spec(_sp); _sp.loader.exec_module(_vr)
    printed_stream = []
    for pi, page in enumerate(pages):
        n_, x_ = page_notes(page)
        printed_stream += [t for lst in n_.values() for t in lst] + x_
    pidx = _vr.WordIndex(_vr.norm(' '.join(printed_stream)))
    nidx = _vr.WordIndex(' '.join(_vr.norm(a['text']) for v in new.values() for a in v))
    kept, dropped = 0, []
    for o, arr in old.items():
        for a in arr:
            q = _vr.norm(a.get('text', ''))
            if not q or q in nidx:
                continue                      # the rebuild already covers it
            if q in pidx:
                new.setdefault(o, []).append(dict(a)); kept += 1
            else:
                dropped.append((o, a.get('n'), a.get('text', '')[:60]))
    print(f'   merge: kept {kept} existing note(s) the rebuild missed; '
          f'dropped {len(dropped)} not printed anywhere in the volume')
    for o, n, t in dropped[:6]: print(f'     DROPPED ord{o} note {n}: {t}')

    for o in new: new[o].sort(key=lambda a: (a['n'] if a.get('n') is not None else 0))
    o_n = sum(len(v) for v in old.values()); n_n = sum(len(v) for v in new.values())
    print(f'{vol}: printed notes anchored {n_n} (was {o_n} stored)   '
          f'unanchored {len(unanchored)}   xref lines {sum(len(v) for v in xref_by_ord.values())}')
    for pi, n, t in unanchored[:cap]:
        print(f'   UNANCHORED: p{pi} note {n}: {t}')
    if len(unanchored) > cap: print(f'   … {len(unanchored)-cap} more')

    if write:
        path = f'{ROOT}/site/reader/apparatus/{vol}.appk.json'
        if not os.path.exists(path + '.preapp'): shutil.copy(path, path + '.preapp')
        json.dump({k: new[k] for k in sorted(new, key=int)},
                  open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        xp = f'{ROOT}/site/reader/xrefs'
        os.makedirs(xp, exist_ok=True)
        json.dump({k: xref_by_ord[k] for k in sorted(xref_by_ord, key=int)},
                  open(f'{xp}/{vol}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print('wrote', path, 'and', f'{xp}/{vol}.json')
    else:
        print('[dry-run] pass --write to apply')


if __name__ == '__main__':
    main()
