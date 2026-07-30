#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Close the last render-vs-PDF residuals in 18Khu01 (Khuddaka volume 1).

Every item here was surfaced by `pipeline/verify_render_vs_pdf.py` and checked
against the printed page.  Nothing in `site/18Khu01.json` is modified — all
changes go into the reader side-maps.

  ord111  Dhammapada v23.  The corpus paragraph runs v23 straight into v24
          (with a stray "24." mid-verse), and v24 is ALSO rendered from the
          uddāna side-map as a restored verse with its vatthu title — so v24's
          text appeared twice.  Give ord111 a verse entry holding only v23 as
          the page prints it; the side-map keeps v24.

  ord522  Udāna, Bāhiyasutta.  The verse entry held 3 of the 5 printed lines,
          and because a verse entry replaces the paragraph text, the last two
          pādas and the closing formula were dropped from the render.

  ord542  Udāna, Lokasutta.  The corpus dropped two pādas ("Bhavapareto
          bhavamevābhinandati.", "Asesavirāganirodho nibbānaṁ.").  The page
          sets this sutta as verse -> prose -> verse, which block() could not
          express, so `after` entries may now also be {"gatha": [...]} objects
          (see the matching reader change).

  uddāna  Three printed recitation-section markers were absent from the render
          (Dhammapada "Paṭhamabhāṇavāraṁ.", Itivuttaka "Paṭhamabhāṇavāro." and
          "Tatiyabhāṇavāraṁ."), as was the Dhammapada closing section heading
          "Uddānagāthāyo".

Usage: python3 pipeline/fix_18khu01_residuals.py [--write]
"""
import json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOL = '18Khu01'


def layout_pages():
    return subprocess.run(['pdftotext', '-layout', f'{ROOT}/pali-unicode/{VOL}.pdf', '-'],
                          capture_output=True, text=True).stdout.split('\f')


def body(page):
    out = []
    for l in page.split('\n'):
        if re.match(r'^\s*_{10,}', l): break
        if l.strip(): out.append(l.rstrip())
    return out


def between(lines, start_pat, end_pat):
    """Printed lines strictly after start_pat up to and including end_pat."""
    i = next(k for k, l in enumerate(lines) if re.search(start_pat, l))
    j = next(k for k, l in enumerate(lines) if k > i and re.search(end_pat, l))
    return [re.sub(r'^\s*[*+]\s*', '', l).strip() for l in lines[i + 1:j + 1]]


def flat(pages, lo, hi):
    """Body lines of pages [lo,hi) as one stream — several of these passages
    straddle a page break (which is exactly why the Bāhiyasutta verse was
    truncated to 3 of its 5 pādas in the first place)."""
    out = []
    HDR = re.compile(r'^\s*(?:\d+\s+\S+|(?:\d+\.\s+)?\S+\s+\d+)\s*$')
    for pi in range(lo, hi):
        b = body(pages[pi])
        if b and HDR.match(b[0]): b = b[1:]     # running page header
        out += b
    return out


def strip_mark(l):
    return re.sub(r'^\s*[*+]\s*', '', l).strip()


def main():
    write = '--write' in sys.argv
    pages = layout_pages()
    V = json.load(open(f'{ROOT}/site/reader/verse/{VOL}.json', encoding='utf-8'))
    U = json.load(open(f'{ROOT}/site/reader/uddana/{VOL}.json', encoding='utf-8'))

    # ---- ord111: Dhammapada verse 23, exactly as printed -------------------
    L = flat(pages, 38, 44)
    i = next(k for k, l in enumerate(L) if 'Te jhāyino' in l)
    v23 = [strip_mark(L[i]).split('. ', 1)[1], strip_mark(L[i + 1])]
    assert v23[0].startswith('Te jhāyino') and v23[1].startswith('Phusanti'), v23
    V['111'] = {'groups': [v23]}

    # ---- ord522: Udāna Bāhiyasutta, all five pādas (spans a page break) ----
    L = flat(pages, 108, 113)
    k = next(x for x, l in enumerate(L) if 'Yattha āpo ca pathavī' in l)
    g = [strip_mark(l) for l in L[k:k + 5]]
    g[-1] = re.sub(r'\.\s*\.\s*Dasamaṁ\.$', '.', g[-1])
    assert g[3].startswith('Yadā ca attanā') and 'pamuccatī' in g[4], g
    # The page prints ". Dasamaṁ." on the verse's last line and the bracketed
    # formula on the NEXT line, so the formula must follow the tail — block()
    # renders `after` before `tail`, so it goes in the uddāna side-map instead.
    V['522'] = {'groups': [g], 'tail': 'Dasamaṁ.'}
    AYAM = '(Ayampi udāno vutto Bhagavatā iti me sutanti.)2.'
    b522 = U.setdefault('522', [])
    if not any(AYAM in l for b in b522 for l in b.get('lines', [])):
        b522.insert(0, {'label': '', 'lines': [AYAM], 'app': []})

    # ---- ord542: Udāna Lokasutta, verse -> prose -> verse ------------------
    L = flat(pages, 139, 141)
    a = next(x for x, l in enumerate(L) if re.match(r'^\s*udānesi–', l))
    b = next(x for x, l in enumerate(L) if x > a and 'brahmacariyaṁ vussati' in l)
    g1 = [strip_mark(l) for l in L[a + 1:b + 1]]
    c = next(x for x, l in enumerate(L) if x > b and l.strip().startswith('Ye hi keci'))
    d = next(x for x, l in enumerate(L) if x > c and l.strip().startswith('Evametaṁ'))
    prose = []
    for l in L[c:d]:
        if re.match(r'^\s{3,}\S', l) or not prose: prose.append(l.strip())
        else: prose[-1] += ' ' + l.strip()
    e = next(x for x, l in enumerate(L) if x > d and 'Upaccagā sabbabhavāni' in l)
    g2 = [strip_mark(l) for l in L[d:e + 1]]
    g2[-1] = re.sub(r'\.\s*\.\s*Dasamaṁ\.$', '.', g2[-1])
    assert any('Bhavapareto' in l for l in g1), g1
    assert any('Asesavirāganirodho' in l for l in g2), g2
    V['542'] = {'groups': [g1], 'after': prose + [{'gatha': g2}], 'tail': 'Dasamaṁ.'}

    # ---- printed markers absent from the render ---------------------------
    def append_block(ord_, line):
        U.setdefault(str(ord_), []).append({'label': '', 'lines': [line], 'app': []})
    append_block(283, 'Paṭhamabhāṇavāraṁ.')      # Dhammapada, after Buddhavaggo cuddasamo
    append_block(632, 'Paṭhamabhāṇavāro.')       # Itivuttaka, Dukanipāta
    append_block(688, 'Tatiyabhāṇavāraṁ.')       # Itivuttaka, Tikanipāta
    blocks = U['512']                            # Dhammapada closing section heading
    at = next(x for x, b in enumerate(blocks) if b.get('label') == 'Dhammapade vaggānamuddānaṁ')
    if not any(b.get('label') == 'Uddānagāthāyo' for b in blocks):
        blocks.insert(at, {'label': 'Uddānagāthāyo', 'lines': [], 'app': []})

    print(f'verse entries touched: 111, 522, 542   '
          f'(ord542: {len(V["542"]["groups"][0])} + {len(g2)} pāda lines, {len(prose)} prose)')
    print(f'uddāna blocks added:  283, 632, 688, 512(label)')

    if write:
        for name, data in (('verse', V), ('uddana', U)):
            path = f'{ROOT}/site/reader/{name}/{VOL}.json'
            if not os.path.exists(path + '.preresid'):
                shutil.copy(path, path + '.preresid')
            data = {k: data[k] for k in sorted(data, key=int)}
            json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
            print('wrote', path)
    else:
        print('[dry-run] pass --write to apply')


if __name__ == '__main__':
    main()
