#!/usr/bin/env python3
"""Recover the uddāna mnemonic verses (+ their footnotes and the section
colophons) that the original extraction dropped at every vagga / saṁyutta /
nipāta boundary, and emit them as a side-map the reader interleaves — WITHOUT
touching paragraph ordinals (so nav / links / apparatus / bold keep their keys).

Output per volume: site/reader/uddana/<VOL>.json
  { "<afterOrd>": [ {label, lines:[...], app:[{n,text}]} , ... ] }
The reader renders each block right after paragraph <afterOrd>.
"""
import json, os, re, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALI = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ .,–’‘“”()-')
SEP = re.compile(r'^_{5,}$')
PARANUM = re.compile(r'^\d{1,4}(-\d{1,4})?\.\s')          # a numbered paragraph line
SUTTAHEAD = re.compile(r'^\d{1,3}\.\s+\S+(sutta|suttaṁ)\b', re.I)
# start of the volume's back-matter (name/word index, page columns, variant lists)
BACKMATTER = re.compile(r'anukkam|piṭṭhaṅk|nānāpāṭh|(gāthā|pada)sūci|^\[|pāḷiyā\s*$|piṭakassa\s*$', re.I)
FOOT = re.compile(r'^(\d{1,2})\.\s+(.*)$')
UDDLABEL = re.compile(r'uddāna', re.I)

def page_lines(pdf, pg):
    out = subprocess.run(['pdftotext', '-f', str(pg), '-l', str(pg), pdf, '-'],
                         capture_output=True, text=True).stdout
    return [x.rstrip() for x in out.splitlines() if x.strip()]

def extract_block(pdf, pg):
    """From the uddāna label on page pg, collect verse+colophon lines and the
    footnote definitions. Returns (label, lines, footnotes) or None."""
    lines = page_lines(pdf, pg)
    li = next((i for i, l in enumerate(lines) if UDDLABEL.search(l)), None)
    if li is None:
        return None
    label = lines[li].strip()                           # keep any footnote marker on the label
    body, foots, mode = [], [], 'body'
    src = lines[li + 1:]
    # verse may spill onto the next page — append it, we stop at the right marker anyway
    src += ['<<PAGEBREAK>>'] + page_lines(pdf, pg + 1)
    for l in src:
        if l == '<<PAGEBREAK>>':
            if mode == 'foot':
                break                                    # footnotes never cross the page
            continue                                     # verse may spill to the next page
        if SEP.match(l):
            mode = 'foot'; continue
        if mode == 'body':
            if PARANUM.match(l) or SUTTAHEAD.match(l) or BACKMATTER.search(l) or BARE_NUM.match(l):
                break                                    # next paragraph/sutta, back-matter, or a page-number line (top of next page) -> block ends
            body.append(l)
        else:
            foots.append(l)                              # footnote lines start with "N." — keep
    # coalesce footnote lines into numbered entries (a new entry only when the
    # number is the next sequential one — otherwise it's a continuation line that
    # merely happens to begin with a digit, e.g. a long variant gāthā)
    app = []
    for l in foots:
        m = FOOT.match(l)
        if m and int(m.group(1)) == len(app) + 1:
            app.append({'n': int(m.group(1)), 'text': m.group(2).strip()})
        elif app:
            app[-1]['text'] += ' ' + l.strip()
    body = [x.strip() for x in body if x.strip()]
    # keep only footnotes actually referenced by a marker in the label/verse (the
    # page's footnote block is shared with the suttas above it)
    marked = set(int(n) for n in re.findall(r'[A-Za-zāīūṁṃṅñṭḍṇḷ](\d{1,2})(?!\d)', label + ' ' + ' '.join(body)))
    app = [f for f in app if f['n'] in marked]
    return label, body, app

def anchor_ord(paras, pdf, pg):
    """ordinal of the paragraph the uddāna renders after = the last paragraph
    that appears on or before the uddāna's page (the next vagga's first sutta
    begins on a later page)."""
    cand = [i for i, p in enumerate(paras) if (p.get('pdf_page') or 0) <= pg]
    return cand[-1] if cand else len(paras) - 1

def build_volume(vol):
    d = json.load(open(os.path.join(ROOT, 'site', vol + '.json')))
    paras = d['paragraphs']; hs = d.get('headings', [])
    pdf = os.path.join(ROOT, 'pali-unicode', vol + '.pdf')
    if not os.path.exists(pdf):
        return None
    udd_pages = []
    for h in hs:
        if h['kind'] == 'section' and UDDLABEL.search(h.get('title', '')):
            pg = h.get('pdf_page')
            if pg and pg not in udd_pages:
                udd_pages.append(pg)
    out = {}
    for pg in sorted(udd_pages):
        blk = extract_block(pdf, pg)
        if not blk:
            continue
        label, body, app = blk
        if not body:
            continue
        ao = anchor_ord(paras, pdf, pg)
        out.setdefault(str(ao), []).append({'label': label, 'lines': body, 'app': app})
    return out

BARE_NUM = re.compile(r'^\d+$')
def residue(block):
    """flag over-capture: back-matter markers, bare page-number lines, alphabet
    headers, or an implausibly long block (real uddāna blocks are short)."""
    for l in block['lines']:
        if BACKMATTER.search(l) or BARE_NUM.match(l) or re.match(r'^\[', l):
            return l
    if len(block['lines']) > 40:                          # Vinaya khandhaka uddānas are legitimately long
        return f'{len(block["lines"])} lines'
    return None

OUTDIR = os.path.join(ROOT, 'site', 'reader', 'uddana')

def write_all():
    man = json.load(open(os.path.join(ROOT, 'site', 'reader', 'manifest.json')))['volumes']
    canon = sorted(c for c, mm in man.items() if mm['layer'] == 'canon')
    os.makedirs(OUTDIR, exist_ok=True)
    grand = 0; flagged = []
    for vol in canon:
        m = build_volume(vol)
        if m is None:
            continue
        n = sum(len(v) for v in m.values())
        grand += n
        for ao, blks in m.items():
            for b in blks:
                r = residue(b)
                if r:
                    flagged.append((vol, ao, r))
        json.dump(m, open(os.path.join(OUTDIR, vol + '.json'), 'w'), ensure_ascii=False)
        print(f"{vol}: {n} uddāna blocks")
    print(f"\nTOTAL uddāna blocks written: {grand}")
    if flagged:
        print(f"FLAGGED (possible over-capture) {len(flagged)}:")
        for v, a, t in flagged[:30]:
            print(f"   {v} ord{a}: {t!r}")
    else:
        print("no over-capture flagged")

if __name__ == '__main__':
    if sys.argv[1:] == ['--build-all']:
        write_all()
    else:
        for vol in sys.argv[1:]:
            m = build_volume(vol)
            n = sum(len(v) for v in m.values())
            print(f"{vol}: {n} uddāna blocks over {len(m)} anchors")
            for ao, blks in list(m.items()):
                for b in blks:
                    print(f"  after ord {ao} [{b['label']}]  ({len(b['app'])} fn)")
                    for l in b['lines']:
                        print(f"       {l}")
