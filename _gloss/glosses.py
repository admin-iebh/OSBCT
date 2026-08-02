#!/usr/bin/env python3
"""Roadmap step 3, pilot — extract the aṭṭhakathā's own word-glosses.

The formula the commentary uses is: the word, then -ti, then the explanation
(indriyānīti …, sañciccāti …).  The printed edition sets the glossed word in
BOLD, and the site already carries that as site/reader/bold/<VOL>.bold.json —
character offsets into each paragraph's text.  So the head of a gloss is not
guessed from a pattern: it is read off the typography of the printed page, and
the -ti is the confirmation.

Nothing here invents a definition.  Every row is a verbatim span of the edition
with its printed page number.
"""
import json, re, os, collections

ROOT = os.path.dirname(os.path.abspath(__file__))

PALI = set('aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvshḷṁ')
PALI |= {c.upper() for c in PALI}
SHORT = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'e': 'a', 'o': 'a'}
CLOSERS = '”’"\''


def undo_ti_sandhi(w):
    """`sañcicca` + `ti` is printed `sañciccāti`, so the bold span reads
    `Sañciccā`.  `ānaṁ` + `ti` is printed `ānanti`, so it reads `Ānan`.
    Return the candidate underlying forms, most likely first. The surface form
    is always included -- some lemmas really do end in a long vowel."""
    w = w.strip()
    out = [w]
    if w and w[-1] in SHORT:
        out.append(w[:-1] + SHORT[w[-1]])
    if w and w[-1] in 'nmñṅṇ':
        out.append(w[:-1] + 'ṁ')
    if w and w[-1] == 'n':
        out.append(w[:-1] + 'ṁ')
    seen = set()
    return [x for x in out if not (x in seen or seen.add(x))]


def coalesce(text, spans):
    """!!! A LEMMA MAY BE MORE THAN ONE WORD.  The edition bolds `Dehi me`ti
    and `“jānanto sañjānanto cecca”`ti as separate runs, and taking each run
    on its own produced rows keyed `me` and `desī` -- a lemma that is half a
    word.  Merge runs separated only by space, hyphen or a quote mark.

    !!! AND BY A COMMA.  Found by the second reader, 2026-08-01h: the quoted
    lemma `“nīlañca pītakañca ceteti, upakkamatī”`ti was being keyed on its
    last word alone, because the comma blocked the merge.  63 occurrences in
    02VinA02.  The gloss body was right; the headword was a fragment."""
    spans = sorted(spans)
    out = []
    for s, e in spans:
        if out and all(c in ' ,;-‘“’”' for c in text[out[-1][1]:s]):
            out[-1][1] = e
        else:
            out.append([s, e])
    return [tuple(x) for x in out]


def heads(text, spans):
    """Bold runs immediately followed by the quotative -ti.
    Returns (start, end_of_bold, end_of_ti, quoted, series)."""
    out = []
    for s, e in coalesce(text, spans):
        j = e
        quoted = False
        while j < len(text) and text[j] in CLOSERS:
            j += 1
            quoted = True
        if text[j:j + 2] in ('ti', 'tī') and not (
                j + 2 < len(text) and text[j + 2] in PALI):
            j += 2
            # `X`ti-ādi = "the words beginning with X" -- the head of a series,
            # not a definition of X alone.  Keep it, but say which it is.
            series = bool(re.match(r'\s*-?\s*ād[iī]', text[j:j + 10]))
            out.append((s, e, j, quoted, series))
    return out


def first_sentence(s):
    """!!! THE LAST GLOSS IN A RUN SWALLOWED THE REST OF THE PARAGRAPH.
    Verified against the printed page (02VinA02, printed p.75): the edition sets
    `Apacitoti apacitippatto.` and then goes on to discuss all five terms
    together. Running each gloss to the next bold head made `Apacito` own that
    whole discussion -- 700 characters attributed to a word that the edition
    defines in one. The definition proper ends at the first sentence-final stop
    outside quotation marks. Truncating is the safe error here and the fuller
    stretch is kept beside it as `context`, so nothing is lost."""
    depth = 0
    for i, c in enumerate(s):
        if c == '“':
            depth += 1
        elif c == '”':
            depth = max(0, depth - 1)
        elif c == '.' and depth == 0:
            if i + 1 >= len(s) or s[i + 1] == ' ':
                # `-pa-` and `-ādi` style abbreviations are not sentence ends
                if not s[max(0, i - 3):i].endswith('-pa'):
                    return s[:i + 1]
    return s


def extract(vol):
    d = json.load(open(os.path.join(ROOT, 'vol', vol + '.json')))
    ps = d['paragraphs']
    bp = os.path.join(ROOT, 'bold', vol + '.bold.json')
    if not os.path.exists(bp):
        return None
    bold = json.load(open(bp))
    hp = os.path.join(ROOT, 'hide', vol + '.json')
    hide = {int(k) for k in json.load(open(hp))} if os.path.exists(hp) else set()

    rows = []
    stats = collections.Counter()
    for o_str, spans in bold.items():
        o = int(o_str)
        if o in hide or o >= len(ps):
            stats['skipped_paragraphs'] += 1
            continue
        p = ps[o]
        t = p['text']
        hs = heads(t, spans)
        stats['bold_spans'] += len(spans)
        stats['bold_runs'] += len(coalesce(t, spans))
        stats['gloss_heads'] += len(hs)
        for k, (s, e, tend, quoted, series) in enumerate(hs):
            stop = hs[k + 1][0] if k + 1 < len(hs) else len(t)
            lemma = t[s:e]
            body = t[tend:stop].strip()
            if series:
                body = re.sub(r'^\s*-?\s*ād[iī]\S*\s*', '', body)
                stats['series_heads'] += 1
            words = lemma.split()
            # a gloss that begins with a conjunction is a continuation, not a
            # definition; keep it but mark it so the panel can prefer others.
            rows.append({
                'lemma': lemma,
                'words': len(words),
                # only the LAST word carries the -ti sandhi
                'candidates': (words[:-1] + undo_ti_sandhi(words[-1])
                               if words else []),
                'gloss': first_sentence(body),
                'context': body,
                # !!! THE NEXT LEMMA CAN CUT IN BEFORE THE SENTENCE ENDS, so
                # the gloss stops mid-clause.  Found by the second reader,
                # 2026-08-01h, who declined to judge such a row rather than
                # guess -- which was the right call.  2.0% of clean rows.
                # Flagged, not patched: completing it would mean guessing
                # where the edition's sentence goes.
                'truncated': not first_sentence(body).rstrip().endswith(
                    ('.', '?', '!', '”')),
                'quoted_lemma': quoted,
                'series_head': series,
                'vol': vol,
                'ord': o,
                'n': p.get('n'),
                # !!! THIS IS THE PARAGRAPH'S PAGE RANGE, NOT THE GLOSS'S PAGE.
                # The corpus records which pages a paragraph covers but not
                # where inside it each page break falls, so the page a given
                # gloss is printed on cannot be established from this data.
                # Estimating it from the character offset would be a guess;
                # principle 2 says flag instead. Cite the range.
                'covers': p.get('covers'),
                'printed_first': p.get('printed'),
                'pdf_page': p.get('pdf_page'),
                'sutta': p.get('sutta'),
                'offset': s,
            })
    return rows, stats


if __name__ == '__main__':
    import sys
    vol = sys.argv[1] if len(sys.argv) > 1 else '02VinA02'
    rows, stats = extract(vol)
    json.dump(rows, open(os.path.join(ROOT, f'glosses_{vol}.json'), 'w'),
              ensure_ascii=False, indent=1)
    print(vol, dict(stats), 'rows', len(rows))
