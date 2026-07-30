#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Give every book the NAME its title page prints, in its own side-map.

The edition opens each book with a title page set:

        Khuddakanikāya
        <Book name>                <- this, large and centred
        _____
        Namo tassa Bhagavato Arahato Sammāsambuddhassa.

Output: `site/reader/booktitle/<VOL>.json` = {ordinal: [lines]} — the whole stack
the page sets above the homage, in printed order.  That is normally two lines,
the piṭaka or nikāya and then the book:

        Dīghanikāya                <- series line, smaller
        Sīlakkhandhavaggapāḷi      <- the book, largest

and occasionally three (38Abhi10: Abhidhammapiṭaka / Dhammānuloma /
Dukapaṭṭhānapāḷi).  The reader draws the last line as the title and the ones
above it smaller, so the page's own hierarchy survives.  A bare string is still
accepted for compatibility.

WHY ITS OWN MAP AND NOT `sections/`: a volume that gains a sections file switches
the reader's `canonHead` to the secmap path and silently drops every inline
heading it draws from its `headings` array.  Only 4 of 36 canon volumes have a
sections file, so putting titles there would have broken 32 volumes' headings in
order to add a title.  Same reasoning that moved the incipit out of sections.

ANCHORS.  A book's first ordinal comes from `nav.json` — every canon book node
carries `first`, and those ordinals are already verified for the volumes whose
structure has been built.  `incipit/<VOL>.json` is used as well where it exists,
since it marks book heads directly.

VERIFICATION.  The name is never taken from the nav label; it is read off the
printed page, and a book whose title page cannot be located is FLAGGED, not
guessed.  Run without --write first and read the flags.

    python3 pipeline/build_booktitles.py <VOL|--canon> [--write]
"""
import json, os, re, shutil, subprocess, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sp = importlib.util.spec_from_file_location('vr', f'{ROOT}/pipeline/verify_render_vs_pdf.py')
vr = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(vr)

# Suttanipāta prints "Bhagavatā" where the other books print "Bhagavato" — this
# is data, never a constant (HANDOFF, incipit fix 2026-07-25ac).
# …and 38Abhi10 sets "Namo Tassa" with a capital T, so the match is case-folded
# on that word too. The edition is not uniform; the regex must not assume it is.
HOMAGE = re.compile(r'Namo [Tt]assa Bhagavat[oāa] Arahato Sammāsambuddhassa')
SERIES = ('Khuddakanikāya', 'Dīghanikāya', 'Majjhimanikāya', 'Saṁyuttanikāya',
          'Aṅguttaranikāya', 'Vinayapiṭaka', 'Abhidhammapiṭaka', 'Suttantapiṭaka',
          'Suttapiṭaka', 'Vinayapiṭake', 'Abhidhammapiṭake')


def anchors(vol):
    """Book-head ordinals for a volume: nav `first` values plus incipit keys."""
    out = set()
    nav = json.load(open(f'{ROOT}/site/reader/nav.json', encoding='utf-8'))
    for L in nav['layers']:
        for nk in L.get('nikayas', []):
            for v in nk.get('volumes', []):
                if v.get('vol') == vol and v.get('first'):
                    out.add(int(v['first'].split('#')[1]))
                # A work spread over volumes puts other volumes' keys in its tree
                # (Apadāna). Take only WORK-level tree nodes — those are unnumbered
                # ("Therāpadāna"); anything with a leading number is a division,
                # nipāta or vagga INSIDE a book, and anchoring a title there put a
                # spurious "Therīgāthāpāḷi" on Therīgāthā's second nipāta.
                for node in v.get('tree', []) or []:
                    k = node.get('key', '')
                    if k.startswith(vol + '#') and not re.match(r'^\d', node.get('label', '')):
                        out.add(int(k.split('#')[1]))
    p = f'{ROOT}/site/reader/incipit/{vol}.json'
    if os.path.exists(p):
        out |= {int(k) for k in json.load(open(p, encoding='utf-8'))}
    # !!! A BOOK TITLE ANCHORED TO A HIDDEN ORDINAL NEVER RENDERS.  `block()`
    # and `render_parts` skip a hidden paragraph and take its `booktitle`,
    # `incipit` and `uddana` entries with it — the rule START HERE states as a
    # census ("no key of any side-map may appear in that volume's `hide/`") and
    # which this builder was the last consumer not to obey.  It bit 29KhuA10:
    # the volume's title-page paragraph (ord0, `Theragāthā-aṭṭhakathā`) is a
    # leaked heading the body builder hides, and `anchors` took it from the
    # STALE nav's `first` and preferred it as the earliest of the two ordinals
    # sharing that title page.  Dropping hidden ordinals moves the anchor to
    # ord2, where every companion volume already carries it.
    # MEASURED over all 118 volumes: this volume alone moves; 79 booktitle maps
    # are byte-identical.
    p = f'{ROOT}/site/reader/hide/{vol}.json'
    if os.path.exists(p):
        out -= {int(k) for k in json.load(open(p, encoding='utf-8'))}
    return sorted(out)


def title_on_page(pages, idx):
    """Every line the page sets above the homage, in printed order.

    The series line ('Dīghanikāya', 'Vinayapiṭaka', 'Khuddakanikāya' …) is part
    of what the title page says and is kept, not filtered out: the edition names
    the collection above the book on every one of these pages.
    """
    lines = [l.strip() for l in pages[idx].split('\n') if l.strip()]
    h = next((i for i, l in enumerate(lines) if HOMAGE.search(l)), None)
    if h is None:
        return None
    stack = [l for l in lines[:h]
             if not re.fullmatch(r'[_\s]+', l) and not re.fullmatch(r'\d+', l)]
    if not stack:
        return None
    # the last line is the book's own name; anything that is running text means
    # this is not a title page
    if len(stack[-1].split()) > 6 or stack[-1].endswith('.'):
        return None
    return stack


def build(vol, verbose=True):
    paras = json.load(open(f'{ROOT}/site/{vol}.json', encoding='utf-8'))['paragraphs']
    pages = subprocess.run(['pdftotext', '-layout', vr.pdf_path(vol), '-'],
                           capture_output=True, text=True).stdout.split('\f')
    off = vr.page_offset(vol, paras, pages)
    out, flagged, bypage = {}, [], {}
    for o in anchors(vol):
        if o >= len(paras):
            flagged.append((o, 'ordinal out of range')); continue
        pg = paras[o].get('pdf_page')
        if pg is None:
            flagged.append((o, 'no page anchor')); continue
        title, at = None, None
        for d in (0, -1, 1, -2, 2, -3, 3, -4, 4):
            i = pg + off + d
            if 0 <= i < len(pages):
                title = title_on_page(pages, i)
                if title:
                    at = i
                    break
        if title:
            # ONE TITLE PAGE, ONE BOOK HEAD.  Several ordinals can sit near the
            # same title page; the book begins at the earliest of them.  Without
            # this a book got two titles (39Abhi11 ord2265 and 2266, 40Abhi12
            # ord187 and 189).
            prev = bypage.get(at)
            if prev is None or o < prev:
                if prev is not None:
                    out.pop(str(prev), None)
                bypage[at] = o
                out[str(o)] = title
                if verbose:
                    print(f'  ord {o:5d}  {title}')
            elif verbose:
                print(f'  ord {o:5d}  (same title page as ord {prev}, skipped)')
        else:
            flagged.append((o, f'no title page found near pdf page {pg}'))
    for o, why in flagged:
        print(f'  ord {o:5d}  FLAGGED — {why}')
    return out, flagged


def write(vol, data):
    p = f'{ROOT}/site/reader/booktitle/{vol}.json'
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if os.path.exists(p) and not os.path.exists(p + '.bak'):
        shutil.copy(p, p + '.bak')
    json.dump(data, open(p, 'w'), ensure_ascii=False)


def main():
    a = sys.argv[1:]
    wr = '--write' in a
    if '--canon' in a:
        man = json.load(open(f'{ROOT}/site/reader/manifest.json', encoding='utf-8'))['volumes']
        vols = sorted(v for v, d in man.items() if d.get('layer') == 'canon')
    else:
        vols = [x for x in a if not x.startswith('--')]
    tot = fl = 0
    for vol in vols:
        print(f'== {vol} ==')
        out, flagged = build(vol)
        tot += len(out); fl += len(flagged)
        if wr:
            write(vol, out)
    print(f'\n{len(vols)} volume(s): {tot} book title(s), {fl} flagged'
          + ('' if wr else '  — DRY RUN, pass --write'))


if __name__ == '__main__':
    main()
