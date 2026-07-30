#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Give every book the NAME the edition prints on its title page.

The edition opens each book with a title page set:

        Khuddakanikāya
        <Book name>                <- this, large and centred
        _____
        Namo tassa Bhagavato Arahato Sammāsambuddhassa.

The reader had no way to show that name, so a volume holding several books ran
one book into the next with nothing announcing the change — and where the name
WAS captured it had been swept into the opening verse block, so it showed small,
italic and left-aligned instead of as a title.

This adds a `k:'booktitle'` sections entry at each book's first ordinal, taking
the wording from the page itself.  Book heads are located by the incipit map
(`incipit/<VOL>.json`), which already marks exactly one ordinal per book.

Idempotent: re-running replaces the entry rather than adding a second.

    python3 pipeline/add_booktitles.py <VOL> [--write]
"""
import json, os, re, shutil, subprocess, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sp = importlib.util.spec_from_file_location('vr', f'{ROOT}/pipeline/verify_render_vs_pdf.py')
vr = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(vr)

# Suttanipāta prints 'Bhagavatā' where the other books print 'Bhagavato' — this
# is data, never a constant (HANDOFF, incipit fix 2026-07-25ac).
HOMAGE = re.compile(r'Namo tassa Bhagavat[oāa] Arahato Sammāsambuddhassa')
SERIES = ('Khuddakanikāya', 'Dīghanikāya', 'Majjhimanikāya', 'Saṁyuttanikāya',
          'Aṅguttaranikāya', 'Vinayapiṭaka', 'Abhidhammapiṭaka', 'Suttantapiṭaka')


def title_on_page(pages, idx):
    """The book name printed above the homage on this title page."""
    lines = [l.strip() for l in pages[idx].split('\n') if l.strip()]
    h = next((i for i, l in enumerate(lines) if HOMAGE.search(l)), None)
    if h is None:
        return None
    for l in reversed(lines[:h]):
        if re.fullmatch(r'[_\s]+', l) or l in SERIES or re.fullmatch(r'\d+', l):
            continue
        return l
    return None


def main():
    vol = sys.argv[1]
    write = '--write' in sys.argv
    paras = json.load(open(f'{ROOT}/site/{vol}.json', encoding='utf-8'))['paragraphs']
    pages = subprocess.run(['pdftotext', '-layout', vr.pdf_path(vol), '-'],
                           capture_output=True, text=True).stdout.split('\f')
    off = vr.page_offset(vol, paras, pages)
    inc = json.load(open(f'{ROOT}/site/reader/incipit/{vol}.json', encoding='utf-8'))
    secp = f'{ROOT}/site/reader/sections/{vol}.json'
    sec = json.load(open(secp, encoding='utf-8')) if os.path.exists(secp) else {}

    added = 0
    for k in sorted(inc, key=int):
        o = int(k)
        pg = paras[o].get('pdf_page')
        if pg is None:
            print(f'  ord {o}: no page anchor, skipped'); continue
        # the homage may sit a page either side of the paragraph's own anchor
        title = None
        for d in (0, -1, 1, -2, 2):
            i = pg + off + d
            if 0 <= i < len(pages):
                title = title_on_page(pages, i)
                if title:
                    break
        if not title:
            print(f'  ord {o}: no title found near page {pg}, FLAGGED'); continue
        arr = [h for h in sec.get(k, []) if h.get('k') != 'booktitle']
        # the same name may already sit in the list as ordinary heading/verse text
        arr = [h for h in arr if h.get('l', '').strip() != title]
        sec[k] = [{'l': title, 'k': 'booktitle'}] + arr
        added += 1
        print(f'  ord {o:5d}  {title}')

    if write:
        if os.path.exists(secp) and not os.path.exists(secp + '.prebooktitle'):
            shutil.copy(secp, secp + '.prebooktitle')
        os.makedirs(os.path.dirname(secp), exist_ok=True)
        json.dump(sec, open(secp, 'w'), ensure_ascii=False)
        print(f'{vol}: {added} book title(s) written to sections/{vol}.json')
    else:
        print(f'{vol}: {added} book title(s) — DRY RUN, pass --write')


if __name__ == '__main__':
    main()
