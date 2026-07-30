#!/usr/bin/env python3
"""Build the Khuddakanikāya left pane: the 21 books (official OSBCT list),
split out of the 11 physical volumes, each book showing its chapters as tree
leaves with suttas/verses in the ☰ Contents (same reader mechanism as
Aṅguttara's nipāta nodes). The corpus `book` field flip-flops between the book
name and its chapter names (Itivuttaka↔nipātas, Thera/Therīgāthā↔nipātas,
Jātaka↔nipātas), so the canonical book is carried forward.
"""
import json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_majjhima_nav import fold, nkey, clean_label, edist, SITE

NAV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'site', 'reader', 'nav.json')
NIKAYA = 'Khuddakanikāya'

# ordered (display title, [book-field stems that identify it]) per physical volume
VOL_BOOKS = {
 '18Khu01': [('Khuddakapāṭhapāḷi', ['khuddakapatha']), ('Dhammapadapāḷi', ['dhammapada']),
             ('Udānapāḷi', ['udana']),
             ('Itivuttakapāḷi', ['itivuttaka', 'ekakanipata', 'dukanipata', 'tikanipata', 'catukkanipata']),
             ('Suttanipātapāḷi', ['suttanipata'])],
 '19Khu02': [('Vimānavatthupāḷi', ['vimanavatthu']), ('Petavatthupāḷi', ['petavatthu']),
             ('Theragāthāpāḷi', ['theragatha']), ('Therīgāthāpāḷi', ['therigatha'])],
 '20Khu03': [('Apadānapāḷi I', ['therapadana', 'apadana'])],
 '21Khu04': [('Apadānapāḷi II', ['therapadana', 'theriapadana', 'apadana']),
             ('Buddhavaṁsapāḷi', ['buddhavamsa']), ('Cariyāpiṭakapāḷi', ['cariyapitaka'])],
 '22Khu05': [('Jātakapāḷi I', ['jataka'])],
 '23Khu06': [('Jātakapāḷi II', ['jataka'])],
 '24Khu07': [('Mahāniddesapāḷi', ['mahaniddesa'])],
 '25Khu08': [('Cūḷaniddesapāḷi', ['culaniddesa'])],
 '26Khu09': [('Paṭisambhidāmaggapāḷi', ['patisambhidamagga', 'ditthiniddesa'])],
 '27Khu10': [('Nettippakaraṇapāḷi', ['netti']), ('Peṭakopadesapāḷi', ['petakopadesa'])],
 '28Khu11': [('Milindapañhapāḷi', ['milindapanha', 'attanipatana'])],
}
# 21 books in official order
BOOK_ORDER = [t for v in ['18Khu01','19Khu02','20Khu03','21Khu04','22Khu05','23Khu06',
                          '24Khu07','25Khu08','26Khu09','27Khu10','28Khu11'] for t, _ in VOL_BOOKS[v]]

def is_chapter(v):
    """a vagga/nipāta chapter marker (not a book title)."""
    f = fold(v)
    return f.endswith('vagga') or f.endswith('nipata') or f.endswith('nipatapali')

def book_of(vol, bookfield, cur):
    """map a paragraph's book field to a canonical book title (carry-forward)."""
    f = nkey(bookfield)
    for title, stems in VOL_BOOKS[vol]:
        if any(f.startswith(s) for s in stems):
            return title
    return cur   # chapter/nipāta name -> stays in current book

def chapter_label(v):
    return clean_label(re.sub(r'\d+$', '', v or ''))

def chapters_from_headings(hs, paras, lo, hi):
    """chapters from the corpus headings array (kind sutta/section with a number),
    for books whose sections aren't in the vagga/sutta paragraph fields
    (Khuddakapāṭha, Buddhavaṁsa …). Anchored to paragraphs by pdf_page."""
    plo, phi = paras[lo].get('pdf_page') or 0, paras[hi - 1].get('pdf_page') or 10 ** 9
    out = []; ptr = lo; seen = set()
    for h in hs:
        if h.get('kind') not in ('sutta', 'section'): continue
        if h.get('n') is None: continue                       # start headings only (end-markers have n=None)
        pg = h.get('pdf_page') or 0
        if not (plo <= pg <= phi): continue
        t = clean_label((h.get('title') or '').strip())
        if not t or re.match(r'^[_\s.]+$', t) or 'niṭṭhit' in fold(t): continue
        k = nkey(t)
        if not k or k in seen: continue                       # dedup by name, not ordinal
        while ptr < hi and (paras[ptr].get('pdf_page') or 0) < pg: ptr += 1
        seen.add(k)
        out.append({'raw': t, 'ord': min(ptr, hi - 1)})
    out.sort(key=lambda x: x['ord'])
    return out

def build_volume(vol):
    d0 = json.load(open(SITE(vol)))
    paras = d0['paragraphs']; HEADS = d0.get('headings', [])
    single = len(VOL_BOOKS[vol]) == 1
    # 1. assign each paragraph to a canonical book (carry-forward)
    cur = VOL_BOOKS[vol][0][0]
    spans = []; sn = False
    for i, p in enumerate(paras):
        b = p.get('book')
        if single:
            bk = cur
        else:
            bk = book_of(vol, b, cur) if (b and b != 'X') else cur
            # 18Khu01: the running header stays 'Catukkanipāta' through all of
            # Suttanipāta, so the book field never names it — detect by its first
            # vagga (Uragavagga); everything from there on is Suttanipāta.
            if vol == '18Khu01' and nkey(p.get('vagga')) == 'uragavagga':
                sn = True
            if sn:
                bk = 'Suttanipātapāḷi'
        cur = bk
        if not spans or spans[-1]['book'] != bk:
            spans.append({'book': bk, 'start': i})
    for j, s in enumerate(spans):
        s['end'] = spans[j + 1]['start'] if j + 1 < len(spans) else len(paras)
    # merge any non-consecutive fragments of the same book (flip-flop can reopen)
    merged = {}
    for s in spans:
        merged.setdefault(s['book'], []).append((s['start'], s['end']))
    # 1b. SNAP each book's start back to its verse-number reset.
    # The `book` field is a running header, and on a new book's FIRST page the
    # header often prints the NIPĀTA name ('Ekakanipāta'), not the book title.
    # book_of() carries the previous book forward through those paragraphs, so
    # the first '…pāḷi' occurrence lands 1..n paragraphs LATE.  (19Khu02:
    # Theragāthā was found at 1849 but really starts at 1848; Therīgāthā at
    # 3140 but really starts at 3136.)  The reliable signal is the paragraph
    # number resetting to 1: walk back over a strictly-increasing run of `n`
    # to the paragraph with n == 1, and require the paragraph before it to
    # carry a LARGER n (i.e. it really is a reset, not just the volume start).
    for title, ranges in merged.items():
        lo = ranges[0][0]
        if lo == 0:
            continue
        j = lo
        while j > 0:
            a, b = paras[j - 1].get('n'), paras[j].get('n')
            if not isinstance(a, int) or not isinstance(b, int) or a != b - 1:
                break
            j -= 1
        if j < lo and paras[j].get('n') == 1 and isinstance(paras[j - 1].get('n'), int) \
           and paras[j - 1]['n'] > 1:
            ranges[0] = (j, ranges[0][1])
            for other, orng in merged.items():          # close the previous book at j
                if other == title:
                    continue
                for k, (s0, s1) in enumerate(orng):
                    if s0 < j <= s1:
                        orng[k] = (s0, j)
    # 2. per book: collect chapters (vagga field, else nipāta from book field) + suttas
    nodes = []
    for title, _ in VOL_BOOKS[vol]:
        ranges = merged.get(title)
        if not ranges:
            continue
        lo = ranges[0][0]; hi = ranges[-1][1]
        vaggas = []
        for i in range(lo, hi):
            p = paras[i]
            ch = None
            v = p.get('vagga')
            if v and v != 'X' and fold(v).endswith('vagga'):
                ch = v
            elif title != 'Suttanipātapāḷi':   # Suttanipāta's book field is the stuck 'Catukkanipāta' header — vaggas only
                b = p.get('book')
                if b and b != 'X' and is_chapter(b):
                    ch = b
            if ch is None:
                continue
            if vaggas and nkey(vaggas[-1]['raw']) == nkey(ch):
                continue
            vaggas.append({'raw': ch, 'ord': i})
        # books with no vagga/nipāta chapters (Khuddakapāṭha, Buddhavaṁsa, Netti,
        # Peṭakopadesa …): take sections from the corpus headings (has all of
        # them incl. those whose paragraph `sutta` field is empty), else the
        # `sutta` field as a last resort
        if not vaggas:
            vaggas = chapters_from_headings(HEADS, paras, lo, hi)
        if not vaggas:
            seen = None
            for i in range(lo, hi):
                su = paras[i].get('sutta')
                if not su or su == 'X': continue
                if nkey(su) == seen: continue
                seen = nkey(su)
                vaggas.append({'raw': su, 'ord': i})
        # suttas per chapter span (named sutta field)
        chnodes = []
        for ci, vg in enumerate(vaggas):
            cend = vaggas[ci + 1]['ord'] if ci + 1 < len(vaggas) else hi
            subs = []; seen = None
            for i in range(vg['ord'], cend):
                su = paras[i].get('sutta')
                if not su or su == 'X': continue
                k = nkey(su)
                if k == seen: continue
                seen = k
                subs.append({'label': clean_label(su), 'key': f'{vol}#{i}'})
            chnodes.append({'label': f'{ci+1}. {chapter_label(vg["raw"])}', 'key': f'{vol}#{vg["ord"]}',
                            'subs': [{'label': f'{j+1}. {x["label"]}', 'key': x['key']} for j, x in enumerate(subs)]})
        man = json.load(open(os.path.join(os.path.dirname(NAV), 'manifest.json')))['volumes']
        nodes.append({'vol': vol, 'work': man.get(vol, {}).get('work', vol), 'title': title,
                      'first': f'{vol}#{lo}', 'nipata': True, 'vaggas': chnodes})
    return nodes

def main():
    nodes = []
    for vol in VOL_BOOKS:
        nodes += build_volume(vol)
    got = [n['title'] for n in nodes]
    missing = [b for b in BOOK_ORDER if b not in got]
    if missing:
        print('WARNING missing books:', missing)
    nav = json.load(open(NAV))
    canon = next(L for L in nav['layers'] if L['layer'] == 'canon')
    nk = next((n for n in canon['nikayas'] if n['nikaya'] == NIKAYA), None)
    if nk is None:
        nk = {'nikaya': NIKAYA, 'volumes': []}; canon['nikayas'].append(nk)
    # order nodes by official book order
    nodes.sort(key=lambda n: BOOK_ORDER.index(n['title']))
    nk['volumes'] = nodes
    shutil.copy(NAV, NAV + '.bak')
    json.dump(nav, open(NAV, 'w'), ensure_ascii=False)
    nc = sum(len(n['vaggas']) for n in nodes)
    print(f"Khuddaka nav: {len(nodes)} books, {nc} chapters")
    for n in nodes:
        print(f"   {n['title']:22} {len(n['vaggas'])} chapters ({n['vol']})")

if __name__ == '__main__':
    main()
