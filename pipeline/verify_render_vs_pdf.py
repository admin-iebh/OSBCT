#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render-vs-PDF content verification harness (per volume), BOTH directions.

Assembles exactly what the reader renders for a book/volume — mirroring
`block()` in site/reader/reader2.html:

    sections heading -> verse.before -> (verse.groups | corpus paragraph text)
                     -> verse.after  -> verse.tail -> uddana side-map block

and compares it against the printed PDF page text.

  FORWARD  (--forward, default on): every PDF line, and every PDF sentence
           chunk of >= minw words, must appear in the render.  A miss is a
           DROP: content the printed edition has and the reader does not.

  REVERSE  (--reverse, default on): every rendered prose block and every
           rendered verse must appear CONTIGUOUSLY in the PDF.  A miss means
           the render splices non-adjacent passages together or fabricates
           text.  The report gives the word offset at which the block stops
           matching.

  DUPLICATE: a block may match the PDF and still be rendered MORE times than
           the edition prints it (e.g. a sutta's intro prose attached both to
           the previous paragraph's colophon block and to its own `before`).
           Neither direction above can see that, so render occurrences are
           counted against PDF occurrences separately.

The printed Sixth Council edition is the authority in both directions.

Usage:
  python3 pipeline/verify_render_vs_pdf.py <VOL> <pdf_first> <pdf_last> <ord_lo> <ord_hi> [minw]
      [--lines] [--no-forward] [--no-reverse] [--quiet] [--max N]

(page numbers are pdftotext \\f indices; ords are the book's paragraph range.)
Exit status is 0 only when both directions report zero mismatches.
"""
import json, subprocess, re, unicodedata, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fnblock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(s):
    s = unicodedata.normalize('NFC', s)
    s = re.sub(r'([A-Za-zāīūṁṃṅñṭḍṇḷ])\d+', r'\1', s)   # footnote markers
    s = re.sub(r'\(\d+(-\d+)?\)', ' ', s)               # per-verse counts (N)
    s = re.sub(r'\b\d+\.?\b', ' ', s)                   # verse/paragraph numbers
    # peyyala: the PDF text layer sometimes loses the closing hyphen of "-pa-"
    # ("-paathāparaṁ", "-pathinamiddhaṁ", "-paBuddho"), so collapse "-pa"/"-pe"
    # plus an optional closing hyphen wherever it opens a token.
    s = re.sub(r'(^|\s)-p([ae])-?', r'\1 ', s)
    # intra-word hyphen: the edition sets e.g. "ekacca-asassatikā", "sa-uttaraṁ",
    # "vayo-anuppatto", and the PDF text layer frequently loses the hyphen —
    # so join rather than split, making both sides agree either way.
    s = re.sub(r'(?<=\w)[-‑]\s*(?=\w)', '', s)
    s = re.sub(r'[“”‘’"\'.,;:?!*+–—\-()\[\]]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip().lower()


def chunks(text, minw=4):
    out = []
    for c in re.split(r'(?<=[,.;?])\s+', text):
        n = norm(c)
        if len(n.split()) >= minw:
            out.append(n)
    return out



class WordIndex:
    """Phrase lookup over a normalised token stream.

    A plain `phrase in bigstring` test is O(len(text)) per query, which is fine
    for one book and quadratic for a 3,000-paragraph volume.  This indexes token
    positions instead and probes the rarest token of the query, so both
    "does the print contain this?" and "how many times?" stay near-linear.
    """
    __slots__ = ('w', 'pos')

    def __init__(self, text):
        self.w = text.split()
        self.pos = {}
        for i, t in enumerate(self.w):
            self.pos.setdefault(t, []).append(i)

    def count(self, phrase):
        q = phrase.split()
        if not q: return 0
        rare, ri = None, 0
        for i, t in enumerate(q):
            p = self.pos.get(t)
            if p is None: return 0
            if rare is None or len(p) < len(rare): rare, ri = p, i
        n, k = 0, len(q)
        for p in rare:
            st = p - ri
            if st < 0 or st + k > len(self.w): continue
            if self.w[st:st + k] == q: n += 1
        return n

    def __contains__(self, phrase):
        return self.count(phrase) > 0


def _load(path):
    return json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}


def render_parts(vol, lo, hi):
    """The ordered stream of render elements, mirroring reader2.html block()."""
    d = json.load(open(f'{ROOT}/site/{vol}.json', encoding='utf-8'))['paragraphs']
    U = _load(f'{ROOT}/site/reader/uddana/{vol}.json')
    V = _load(f'{ROOT}/site/reader/verse/{vol}.json')
    S = _load(f'{ROOT}/site/reader/sections/{vol}.json')
    H = _load(f'{ROOT}/site/reader/hide/{vol}.json')
    I = _load(f'{ROOT}/site/reader/incipit/{vol}.json')
    B = _load(f'{ROOT}/site/reader/booktitle/{vol}.json')   # the book's own name
    parts = []      # (ord, kind, text)
    if not S:
        # No precise sections file: the reader draws its inline headings from the
        # corpus `headings` array (buildOutline / HEADMAP), so count those labels
        # as rendered.  Matching is position-independent, so anchoring is moot.
        for h in json.load(open(f'{ROOT}/site/{vol}.json', encoding='utf-8')).get('headings', []):
            if h.get('title'): parts.append((-1, 'head', h['title']))
    for i in range(lo, hi):
        if str(i) in H:
            continue
        # printed order on a book's title page: name, then homage, then headings
        if str(i) in B:
            _b = B[str(i)]
            for _l in ([_b] if isinstance(_b, str) else _b):
                parts.append((i, 'head', _l))
        if str(i) in I:
            parts.append((i, 'incipit', I[str(i)]))
        for h in S.get(str(i), []):
            parts.append((i, 'head', h['l']))
        e = V.get(str(i), {})
        # `before` / `after` may be a bare string or a list of paragraphs —
        # reader2.html's proseBlocks() accepts both, so mirror that here.
        def _plist(x):
            # mirrors proseOne(): an entry may be a {"gatha": [...]} object
            if x is None: return []
            xs = [x] if isinstance(x, str) else list(x)
            out = []
            for p in xs:
                if isinstance(p, dict) and p.get('gatha'):
                    out.append(' '.join(p['gatha']))
                elif isinstance(p, dict) and p.get('t') is not None:
                    # a numbered prose paragraph inside another unit's block —
                    # proseOne draws the number as a .pn and then the text
                    out.append('%s. %s' % (p['n'], p['t']))
                else:
                    out.append(p)
            return out
        # `[]` IS TRUTHY IN JS AND FALSY IN PYTHON, and that difference was a
        # latent divergence between this model and block().  The reader takes
        # the verse branch — rendering `before + after` and NOT the corpus text
        # — for any entry that has a `groups` key at all, including an empty
        # one; this modelled the corpus text as rendered in that case.  No
        # volume had an empty groups list until 26Khu09, whose prose units have
        # no verse lemma to carry them and are written exactly that way, so the
        # divergence had never fired.  Mirror the reader.
        if e.get('groups') is not None:
            # block(): when a verse entry has no `before`, the reader still renders
            # the corpus text up to the "…udānaṁ udānesi–" marker as the lead-in.
            # Missing this made every Udāna narrative look dropped (~2,180 lines).
            if e.get('before') is not None:
                for p in _plist(e.get('before')):
                    parts.append((i, 'before', p))
            elif e['groups']:
                # ...AND ONLY WHEN THERE IS A VERSE TO INTRODUCE.  The fallback
                # lifts the narrative lead-in out of the CORPUS paragraph so it
                # stands above the gāthā the side-map supplies.  A PROSE unit
                # has no gāthā and its whole body already comes from `after`,
                # drawn from the printed stream, so the lead-in was counted a
                # SECOND time — 03Vin03's Mahākhandhaka has seven such units
                # and this gate reported two of them as `rendered-too-often`.
                # The reader had the same bug and was fixed with it
                # (reader2.html, backup `.bakvinaya`).
                # ...AND ONLY WHEN THE GROUPS DO NOT ALREADY CARRY IT.  A
                # Jātaka unit whose whole printed paragraph — gāthā, gloss and
                # lead-in together — is one group needs no lead-in lifted: the
                # fallback would draw it a SECOND time.  41KhuA22 ord143/ord804
                # were reported `rendered-too-often` for exactly this.
                # Measured over every volume's verse map: the fallback fires on
                # 76 entries corpus-wide and the group already contains the
                # lead-in in 2, both of them in 41KhuA22.  Nothing else moves.
                m = re.match(r'(?s)^(.*?udāna\S*\s+udānes[iī][–-])', d[i]['text'])
                if m and norm(m.group(1)) not in norm(
                        ' '.join(' '.join(g) for g in e['groups'])):
                    parts.append((i, 'before', m.group(1)))
            for g in e['groups']:
                parts.append((i, 'verse', ' '.join(g)))
        else:
            for p in _plist(e.get('before')):
                parts.append((i, 'before', p))
            txt = d[i]['text']
            if str(i) in I:   # block(): the embedded copy is stripped from the body
                txt = re.sub(r'Namo\s+\S+\s+\S+\s+[Aa]rahato\s+Sammāsambuddhassa\.?\s*', '', txt, count=1)
            parts.append((i, 'text', txt))
        for p in _plist(e.get('after')):
            parts.append((i, 'after', p))
        if e.get('tail'):
            parts.append((i, 'tail', e['tail']))
        for b in U.get(str(i), []):
            # uddanaHTML(): a `plain` block is a restored canon verse (optionally
            # carrying its own vatthu `head`); otherwise it is a colophon/uddāna
            # block with an optional label.
            if b.get('head'):
                parts.append((i, 'head', b['head']))
            if b.get('label'):
                parts.append((i, 'udd', b['label']))
            kind = 'verse' if b.get('plain') else 'udd'
            for l in b.get('lines', []):
                parts.append((i, kind, l))
    return parts


# per-volume running page-headers (vagga / book / nipāta names)
RUNHDR = re.compile(
    r'^(\d+\.\s+)?(\S*vagga|\S*nipāta|\S*pāḷi|\S*gāthā|Khuddakanikāya|Vinayapiṭaka|'
    r'Abhidhammapiṭaka|Suttantapiṭaka)$')


def pdf_path(vol):
    for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
        p = f'{ROOT}/{d}/{vol}.pdf'
        if os.path.exists(p): return p
    raise SystemExit(f'no PDF found for {vol}')



# !!! THE GATE MUST APPLY THE GLYPH ERRATUM REGISTER, OR IT REPORTS ARTEFACTS.
# `build_khu_volume.py` substitutes the register's `apply_from`/`apply_to` on
# the printed text before parsing, so the side-maps carry the corrected reading;
# the corpus was corrected to match (2026-07-29m).  This gate reads the PDF
# directly, so without the same substitution it compares a corrected render
# against an uncorrected page and reports ONE line per corrected place.
# MEASURED before this was added: +1 line/chunk/not-in-PDF per declared literal
# on exactly the seven volumes that have one — 06VinSg06 +1, 07DiA01 +1,
# 08DiA02 +3, 18AnA02 +1, 27Khu10 +1, 32Abhi04 +3, 49AbhiA02 +3.
# The same class as the line-end-hyphen disagreement of 2026-07-28a: "the gate
# models the reader — a render defect lives in both", and so must a correction.
def _glyph_errata_for(vol, _cache={}):
    if not _cache:
        try:
            reg = json.load(open(os.path.join(ROOT, 'data', 'glyph_errata.json'),
                                 encoding='utf-8'))
        except Exception:
            reg = {'entries': []}
        for e in reg.get('entries', ()):
            if e.get('apply_from') and e.get('apply_to'):
                _cache.setdefault(e['vol'], {})[e['apply_from']] = e['apply_to']
        _cache.setdefault('', {})
    return _cache.get(vol, {})


def pdftext(vol, layout=True):
    """`pdftotext` for this gate, with the glyph errata applied."""
    cmd = ['pdftotext'] + (['-layout'] if layout else []) + [pdf_path(vol), '-']
    txt = subprocess.run(cmd, capture_output=True, text=True).stdout
    for a, b in _glyph_errata_for(vol).items():
        txt = txt.replace(a, b)
    return txt

def running_headers(pages, p0, p1, top=4, minpages=3):
    """Line-forms that recur at the top of pages across the volume.

    Every volume prints its own running header (a sutta, vagga, book or
    commentary name), so a fixed regex misses most of them — and an unfiltered
    header is doubly damaging: it is reported as missing content AND it splits
    the paragraph it interrupts, so the paragraph then looks non-contiguous.
    Deriving the set from the pages themselves is volume-agnostic.
    """
    from collections import Counter
    attop, total = Counter(), Counter()
    for pi in range(p0, min(p1, len(pages) - 1) + 1):
        n = 0
        _raw = pages[pi].split('\n')
        _hcut = fnblock.fn_start(_raw)      # graphic rule: nothing to break on
        for _li, l in enumerate(_raw):
            if _hcut is not None and _li >= _hcut: break
            t = l.strip()
            if not t or re.fullmatch(r'[_\s]+', t) or re.fullmatch(r'\d+', t): continue
            if re.search(r'_{10,}', t): break
            total[t] += 1
            n += 1
            if n <= top: attop[t] += 1
    # A true running header appears at the top of a page and essentially nowhere
    # else.  Requiring that ratio keeps recurring CONTENT out of the set — e.g.
    # Udāna's 80 "udānesi–" lines, a few of which happen to land at a page top.
    # Position alone is still not enough.  In the Apadāna the refrain
    # "N. Paṭisambhidā catasso -pa- kataṁ Buddhassa sāsanaṁ." closes almost every
    # apadāna, so it lands at a page top often, and the rarer numberings of it
    # ("10. …", "11. …") clear both the count and the ratio — the set absorbed
    # them and DELETED 7 printed occurrences of real content, which then showed
    # up as the render producing that line more often than the edition prints it.
    # A running header in this edition is a TITLE: a vagga, nipāta, book or
    # commentary name, with no terminal sentence punctuation.  A sentence-ending
    # line of any length is content, however reliably it falls at a page top.
    #
    # !!! THAT RULE WAS STATED CORRECTLY AND THEN NOT APPLIED, IN TWO WAYS, AND
    # 25Khu08 was bitten by both.
    #  (a) The test carried an escape hatch — `and len(t.split()) > 3` — which
    #      exempted SHORT sentence-ending lines, and a short sentence is still a
    #      sentence.  The Niddesa's formula "…uddhaṁ adho / tiriyañcāpi majjhe."
    #      and the Pārāyana refrain "Nā'penti'me Gotamasāsanamhā." break at a
    #      page top again and again, so both entered the set.
    #  (b) It tested only SENTENCE punctuation, so a verse PĀDA ending in a
    #      comma — "Yaṁ yaṁ disaṁ vajati Bhūripañño," — passed it and was
    #      absorbed too.  A title does not end in a comma either.
    # Every page-top occurrence of an absorbed line is DELETED FROM THE PRINTED
    # SIDE, so the render then holds content the print appears not to have: on
    # 25Khu08 that showed as 4 rendered blocks not-in-PDF and 2 rendered more
    # often than printed, every one of them correct.  This is the THIRD time
    # recurring content has been absorbed into this set (Udāna's "udānesi–"
    # lines, then the Apadāna refrain), and each earlier fix tightened one axis
    # and left the next open.  So: terminal punctuation of ANY kind means
    # content, with no length exemption.
    def title_like(t):
        return not re.search(r'[.,;:?!”"]\d*$', t)
    return {t for t, c in attop.items()
            if c >= minpages and len(t) < 60 and c >= 0.6 * total[t] and title_like(t)}


def layout_headers(vol, pages_plain):
    """The running header of each page, taken from the PRINTED GEOMETRY.

    `running_headers` above derives the set by FREQUENCY, and frequency has a
    floor: a form must head at least three pages.  A section shorter than that
    therefore never enters the set and its header LEAKS INTO THE BODY, where it
    splits the paragraph it interrupts — which is the other half of the damage
    that function's own docstring describes.  26Khu09 shows it: "6. Gatikathā"
    heads only two pages and "7. Kammakathā" and "9. Maggakathā" only one each,
    so all three were being read as body text in the middle of a sentence.
    Raising the floor would let content back in, and the floor is there for good
    reason.

    So use the page's own geometry instead, which needs no threshold at all: in
    this edition the running header is the line that CARRIES THE PRINTED PAGE
    NUMBER, set hard against the opposite margin ("6      Paṭisambhidāmaggapāḷi"
    on a verso, "1. Ñāṇakathā      5" on a recto).  `-layout` preserves that
    spacing; the plain text this function reads does not, which is why the
    frequency heuristic existed.  Read the geometry from `-layout` and match it
    back onto the plain stream.  A page whose first line is not header-shaped —
    the first page of a section, where the edition suppresses the header — is
    correctly left alone.
    """
    lay = pdftext(vol).split('\f')
    out = {}
    for pi in range(min(len(lay), len(pages_plain))):
        for l in lay[pi].split('\n'):
            if not l.strip():
                continue
            if re.match(r'^\s*\d+\s{2,}\D', l) or re.search(r'\s{3,}\d+\s*$', l):
                t = re.sub(r'^\s*\d+\s+', '', re.sub(r'\s+\d+\s*$', '', l.strip()))
                n = norm(t)
                if n:
                    out[pi] = n
            break                      # only the page's FIRST line can be one
    return out


def display_lines(vol):
    """Per page, the normalised text of every CENTRED SHORT UNPUNCTUATED line.

    That is the heading class, and it is the class that GLUES: a chunk is built
    by running lines together until one ends in sentence punctuation, so a
    heading with no terminal stop fuses with the line below it and fabricates a
    chunk that exists nowhere in the render — where the two are correctly a
    heading and a paragraph, drawn as separate elements.
    `pdf_lines` already terminates the page's FIRST body line for exactly this
    reason; that was enough while the only offender was a page-top running
    header, but 29Abhi01 sets 99 such headings MID-PAGE ("Tika" above
    "Tividhena rūpasaṅgaho–"), and the whole Abhidhamma is built this way.
    Read from `-layout`, so this is the printed geometry and not a guess.
    A short line that is really body text loses nothing by being terminated:
    the sentinel is dropped by norm(), the LINE-level comparison is untouched,
    and the only effect is that the chunk comparison breaks there too.
    """
    lay = pdftext(vol).split('\f')
    out = {}
    for pi, page in enumerate(lay):
        acc = set()
        lraw = page.split('\n')
        lcut = fnblock.fn_start(lraw, where=f'{vol} p{pi} layout')
        for li, l in enumerate(lraw):
            if lcut is not None and li >= lcut:
                break
            t = l.strip()
            if not t or FNRULE_L.search(l):
                continue
            ind = len(l) - len(l.lstrip())
            if (ind >= 8 and len(t.split()) <= 6
                    and not re.search(r'[.,;:?!”"–-]$', t)):
                n = norm(t)
                if n:
                    acc.add(n)
        if acc:
            out[pi] = acc
    return out


FNRULE_L = re.compile(r'_{10,}')


def display_openers(vol):
    """Per page, the normalised text of every line that OPENS a display block.

    The chunker runs lines together until one ends in sentence punctuation, so
    a PROSE line with no terminal stop glues to whatever follows it.  Where what
    follows is a display block, that fabricates a chunk the render never has —
    the reader draws a paragraph and a gāthā block as two elements.
    `display_lines` already prevents this shape for HEADINGS, but it cannot
    catch this one: it collects only CENTRED SHORT UNPUNCTUATED lines, and a
    verse pāda ends in ',' or '.', so it is never in that set.  The line that
    glues is the PROSE one ABOVE, which is why this needs a LOOK-AHEAD.

    A display opener is a line at indent >= 8 whose previous non-blank line sits
    AT THE BODY COLUMN ITSELF (indent 0) — i.e. the first line of a display run
    opening out of PROSE, not every pāda of it and not a numbered verse unit's
    own continuation.  Read from `-layout`, so it is the printed geometry.
    """
    lay = pdftext(vol).split('\f')
    out = {}
    for pi, page in enumerate(lay):
        acc, prev = set(), None
        for l in page.split('\n'):
            if not l.strip():
                continue
            ind = len(l) - len(l.lstrip())
            # PREDECESSOR AT THE BODY COLUMN ITSELF, not merely below the
            # display gate.  MEASURED over the seven junctions this rule was
            # built for: all six genuine prose->display cases have a
            # predecessor at indent 0, and the ONE case that is not prose has
            # its predecessor at indent 6 — 10Ma02 p413 `456. Tesaṁ vo ahaṁ
            # byakkhissaṁ, (Vāseṭṭhāti Bhagavā)`, a numbered VERSE unit whose
            # opening pāda hangs left because the number pushes it there, meeting
            # its OWN continuation.  Terminating that would silence a report
            # about a verse the render may be splitting in two — a real
            # question, not an artefact — so the rule stops at the body column.
            if ind >= 8 and prev == 0:
                n = norm(l.strip())
                if n:
                    acc.add(n)
            prev = ind
        if acc:
            out[pi] = acc
    return out


def pdf_lines(vol, p0, p1):
    pages = pdftext(vol, layout=False).split('\f')
    heads = running_headers(pages, p0, p1)
    geo = layout_headers(vol, pages)
    disp = display_lines(vol)
    dopen = display_openers(vol)
    out = []
    TOP = 4
    for pi in range(p0, min(p1, len(pages) - 1) + 1):
        foot = False
        seen = 0
        raw = pages[pi].split('\n')
        # Where the rule is a GRAPHIC there is no `_{10,}` for the test below to
        # find, and the whole apparatus block was arriving in the BODY
        # comparison.  This gate MODELS THE READER, so it has to cut where the
        # builder cuts — but the fact being shared is a fact about the PRINTED
        # PAGE, not about the reader, which is why it lives in its own module
        # and not in an import of the builder.  See pipeline/fnblock.py.
        gcut = fnblock.fn_start(raw, where=f'{vol} p{pi}')
        for li, l in enumerate(raw):
            if gcut is not None and li >= gcut:
                foot = True
            if foot:
                continue
            mfr = re.search(r'_{10,}', l)
            if mfr:
                # The rule that opens the apparatus is NOT always alone on its
                # line.  This function reads plain (non -layout) pdftotext, and
                # there a body line that abuts the rule arrives glued to it —
                # 23Khu06 p301 sets the peyyala "-pa" immediately before it.
                # Anchoring this test at the start of the line therefore missed
                # the rule completely and let that page's ENTIRE apparatus into
                # the BODY comparison, where its variant notes were reported as
                # missing body content.  Keep whatever precedes the rule and
                # drop the rest of the page.
                foot = True
                l = l[:mfr.start()]
                if not l.strip():
                    continue
                # AND WHEN IT IS GLUED, ONE CHARACTER IS LOST WITH IT.  25Khu08
                # p63 sets the page's last body line as "pararūpavedanāsaññā-
                # saṅkhāra-", hyphenated across the break; `-layout` shows that
                # hyphen and plain pdftotext swallows it into the rule's glyph
                # run, so the line arrives as "…saṅkhāra" and norm() can no
                # longer rejoin it with "viññāṇaṁ." on the next page.  The
                # printed side then loses a word the render correctly has,
                # reported once as a missing line and once as a rendered block
                # not in the PDF.  Text ending in a WORD CHARACTER immediately
                # against the rule is exactly that case — a line that genuinely
                # ends before the rule is separated from it by whitespace — so
                # restore the hyphen and let norm()'s intra-word join do the
                # rest.  (23Khu06 p301's peyyala "-pa" becomes "-pa-", which
                # norm() collapses identically either way.)
                if re.search(r'\w$', l):
                    l += '-'
            t = re.sub(r'^[*+]\s*', '', l.strip())   # leading cross-ref marker
            if not t or re.fullmatch(r'_+', t):      # blank / decorative rule
                continue
            if re.match(r'^\d+$', t) or RUNHDR.match(t):
                continue
            seen += 1
            # A derived running header only counts as one at the TOP of a page.
            # Applying the set globally would delete recurring short CONTENT lines
            # too — e.g. Udāna's 80 "udānesi–" lines, which also happen to land at
            # a page top often enough to look like a header.
            if seen <= TOP and t in heads:
                continue
            # …and the same page's header as the printed geometry gives it,
            # which needs no frequency threshold and so catches the headers of
            # sections too short to clear one.
            if seen == 1 and geo.get(pi) and norm(t) == geo[pi]:
                continue
            # A page-top heading/running-header with no terminal punctuation would
            # otherwise glue to the first content line and fabricate a chunk that
            # exists nowhere (heading + refrain). Terminate it so the chunker
            # breaks there; norm() drops the sentinel, so nothing else changes.
            # !!! NOT WHEN THE LINE ENDS IN A HYPHEN.  The sentinel then lands
            # AFTER the hyphen ("…Gaṅgāyamunā-."), which defeats the line-end
            # rejoin twenty lines below, so both halves of the hyphenated
            # compound are reported missing AND the render block that correctly
            # holds it whole is reported not-in-PDF.  A hyphenated line cannot
            # glue a heading to content anyway — it is a word continuing onto
            # the next line, which is exactly what must NOT be broken.
            # Found on 28Khu11 p369 ("…Gaṅgāyamunā-") and p417
            # ("…daṭṭhaphuṭṭhadiṭṭha-"), both of which happen to be the first
            # body line of their page.  Affects every volume.
            if (not t.endswith('-')
                    and not re.search(r'[.,;:?!”"]$', t)
                    and (seen == 1 or norm(t) in disp.get(pi, ()))):
                t += '.'
            # LINE-END HYPHENATION, rejoined for the LINE-level comparison too.
            # The chunk and reverse directions read this list as one joined
            # stream, where norm()'s intra-word rule already puts a hyphenated
            # compound back together; the per-line direction does not, so it
            # tested the two halves as if they were whole words and reported
            # BOTH as missing (25Khu08 "pararūpavedanāsaññāsaṅkhāra-" and its
            # continuation "viññāṇaṁ. Oraṁ vuccati…").  Join on the hyphen and
            # nothing else — the same rule the builders use, and for the same
            # reason: every wider rule fabricates words out of ordinary wraps.
            # LOOK-AHEAD: this line OPENS a display block, so the line above
            # it ends a paragraph in the render whatever its punctuation says.
            # Terminate the PREVIOUS line so the chunker cannot glue prose to a
            # gāthā and fabricate a chunk the render never has.
            if (norm(t) in dopen.get(pi, ()) and out
                    and not out[-1].endswith('-')
                    and not re.search(r'[.,;:?!”"]$', out[-1])):
                out[-1] += '.'
            if out and out[-1].endswith('-'):
                out[-1] = out[-1][:-1] + t
            else:
                out.append(t)
    return out


def verify(vol, p0, p1, lo, hi, minw=4, do_fwd=True, do_rev=True,
           lines_mode=True, quiet=False, cap=40):
    parts = render_parts(vol, lo, hi)
    render = WordIndex(' '.join(norm(p) for _, _, p in parts))
    pdfl = pdf_lines(vol, p0, p1)
    pdfs = WordIndex(norm(' '.join(pdfl)))

    fwd_line, fwd_chunk, rev, dup, struct = [], [], [], [], []
    # A SECOND RENDERING OF THE SAME PAGES, consulted only to EXPLAIN a
    # failure — never to excuse one it cannot explain.
    #
    # This gate reads the PDF in content-stream order (`pdftotext` with no
    # -layout), which is the right model of reading order almost everywhere.
    # On 38Abhi10 it is not: the file's own stream puts a short continuation
    # line BEFORE the line it continues — printed p319 reads "…vipāke ekaṁ -pa-
    # avigate / dve." and the stream emits "dve." first — so seven rendered
    # paragraphs came back as not-contiguous although the page reads exactly as
    # rendered.  `-layout` reconstructs by POSITION and has them right; it is
    # also what every builder reads, so agreeing with it is not circular only
    # because the disagreement is BETWEEN TWO READINGS OF THE PDF, and the one
    # that reflects the printed page wins.
    #
    # This can only RECLASSIFY an existing failure, never create one, so no
    # volume that is clean today can move.
    _lay = [None]
    def _layout_index():
        if _lay[0] is None:
            pgs = pdftext(vol).split('\f')
            ls = []
            for pi in range(p0, min(p1, len(pgs) - 1) + 1):
                for l in pgs[pi].split('\n'):
                    t = l.strip()
                    if not t:
                        continue
                    if ls and ls[-1].endswith('-'):
                        ls[-1] = ls[-1][:-1] + t
                    else:
                        ls.append(t)
            _lay[0] = WordIndex(' '.join(norm(x) for x in ls))
        return _lay[0]

    if do_fwd:
        if lines_mode:
            for t in pdfl:
                n = norm(t)
                if n and n not in render:
                    fwd_line.append(t)
        for c in chunks(' '.join(pdfl), minw):
            if c not in render:
                fwd_chunk.append(c)
    # ...and the same artifact seen from the forward side.  A chunk is cut from
    # the content-stream reading, so where that stream mis-orders two lines it
    # MANUFACTURES a chunk that spans the join — text the page never sets in
    # that order, and which the render is therefore right not to contain.  The
    # test is the same: a chunk absent from the render AND absent from the
    # -layout reading of the same pages is the FILE's, not a drop.
    # DEFECT FOUND 2026-07-26 (recorded, then fixed): `order, order_chunks =
    # [], []` used to sit BELOW this block and silently discarded every chunk
    # the reclassification had just named, so a chunk absent from the render
    # AND from the -layout reading was removed from the failure count and
    # reported NOWHERE.  It never hid a real failure — those go to `_keep` —
    # but it undercounted the PDF-reading-order column.  Initialise first.
    order, order_chunks = [], []
    if fwd_chunk:
        _li = _layout_index()
        _keep = [c for c in fwd_chunk if c in _li]
        order_chunks = [c for c in fwd_chunk if c not in _li]
        fwd_chunk = _keep
    if do_rev:
        for ordi, kind, p in parts:
            if kind in ('head', 'udd', 'tail', 'incipit'):
                continue          # headings/colophons are editorial labels, not body text
            n = norm(p)
            if not n or n in pdfs:
                continue
            if n in _layout_index():
                order.append((ordi, kind, n))
                continue
            w = n.split(); a, b = 0, len(w)
            while a < b:
                mid = (a + b + 1) // 2
                if ' '.join(w[:mid]) in pdfs: a = mid
                else: b = mid - 1
            rev.append((ordi, kind, a, len(w), ' '.join(w[max(0, a - 5):a + 7])))

    if do_rev:
        from collections import Counter
        cnt = Counter()
        for ordi, kind, p in parts:
            # 'udd' MUST be counted here: excluding it hid a real duplication in
            # which a vagga's closing uddāna verses were rendered both as that
            # vagga's uddāna block AND as the next vagga's opening prose.
            if kind in ('head', 'tail', 'incipit'):
                continue
            n = norm(p)
            if len(n.split()) >= 4:
                cnt[n] += 1
        for n, c in cnt.items():
            inpdf = pdfs.count(n)
            if c > max(inpdf, 1):
                dup.append((c, inpdf, n))
        dup.sort(reverse=True)

    # STRUCTURAL guard.  The diff above compares CONTENT: it cannot tell that a
    # line is rendered in the wrong ROLE (the "Namo tassa…" homage folded into a
    # paragraph's prose instead of set as the book's incipit reads identically to
    # it).  Presentation belongs to the jsdom checks, but this one shape recurs
    # once per book across the canon, so it is worth guarding here.
    for ordi, kind, p in parts:
        # !!! THE EXCEPTION WINDOW WAS THE COMPLEMENT OF THE ONE IT MEANT.
        # `p[:i - 60]` is everything up to SIXTY CHARACTERS BEFORE the homage —
        # i.e. it EXCLUDED exactly the sixty characters this test exists to
        # look at.  A narrative homage is introduced immediately before it
        # ("tikkhattuṁ udānaṁ udānesi “namo tassa…"), so the marker always fell
        # in the excluded window and the guard flagged the quotation as a
        # mis-rendered incipit.  MEASURED over every corpus volume: 22
        # paragraphs carry the homage, the old window flags 20 and this one
        # flags 16, and ALL FOUR changed verdicts are OLD-ONLY — nothing is
        # newly hidden, so this cannot mask a defect the old test caught.
        # The four are 09Ma01 ord287, 10Ma02 ord387 and ord472, 12Sam01 ord186,
        # every one of them a character in the story uttering the homage.
        _i = p.find('amo tassa')
        if kind in ('before', 'after', 'text') and re.search(r'[Nn]amo tassa \S+ [Aa]rahato Sammāsambuddhassa', p) \
                and not re.search(r'udān|[“”"‘–-]', p[max(0, _i - 60):_i] + ' '):
            struct.append((ordi, kind, p[:70]))

    print(f'{vol} [{lo}-{hi}) pdf {p0}-{p1}: '
          f'PDF-lines-missing {len(fwd_line)} | PDF-chunks-missing(minw={minw}) {len(fwd_chunk)} '
          f'| render-not-in-PDF {len(rev)} | rendered-too-often {len(dup)}'
          + (f' | PDF-reading-order {len(order) + len(order_chunks)}'
             if (order or order_chunks) else '')
          + (f' | mis-rendered {len(struct)}' if struct else ''))
    if not quiet:
        for t in fwd_line[:cap]:  print('   MISSING-LINE :', t[:100])
        for c in fwd_chunk[:cap]: print('   MISSING-CHUNK:', c[:100])
        for c in order_chunks[:cap]:
            print(f'   PDF-ORDER    : the content-stream reading joins two lines '
                  f'the page does not — chunk absent from the -layout reading '
                  f'too: {c[:70]}')
        for o, k, n in order[:cap]:
            print(f'   PDF-ORDER    : ord{o} [{k}] is contiguous in the -layout '
                  f'reading of these pages but not in the content-stream '
                  f'reading — the FILE\'s order, not the render\'s: {n[:70]}')
        for o, k, a, n, ctx in rev[:cap]:
            print(f'   NOT-IN-PDF   : ord{o} [{k}] diverges at word {a}/{n}: ...{ctx}...')
        for o, k, p in struct[:cap]:
            print(f'   MIS-RENDERED : ord{o} [{k}] homage set as body text: {p}')
        for c, ip, n in dup[:cap]:
            print(f'   DUPLICATED   : rendered {c}x, printed {ip}x: {n[:80]}')
        for name, lst in (('lines', fwd_line), ('chunks', fwd_chunk), ('reverse', rev), ('duplicates', dup)):
            if len(lst) > cap:
                print(f'   ... {len(lst) - cap} more {name} suppressed (--max to raise)')
    return fwd_line, fwd_chunk, rev, dup + struct


if __name__ == '__main__':
    argv = sys.argv[1:]
    cap, pos, i = 40, [], 0
    while i < len(argv):
        a = argv[i]
        if a == '--max':
            cap = int(argv[i + 1]); i += 2; continue
        if a.startswith('--'):
            i += 1; continue
        pos.append(a); i += 1
    flags = set(x for x in argv if x.startswith('--'))
    fl, fc, rv, dp = verify(pos[0], int(pos[1]), int(pos[2]), int(pos[3]), int(pos[4]),
                            int(pos[5]) if len(pos) > 5 else 4,
                            do_fwd='--no-forward' not in flags,
                            do_rev='--no-reverse' not in flags,
                            lines_mode='--no-lines' not in flags,
                            quiet='--quiet' in flags, cap=cap)
    sys.exit(1 if (fl or fc or rv or dp) else 0)

_PAGE_OFF = {}


def page_offset(vol, paras=None, pages=None):
    """MEASURED offset from a paragraph's `pdf_page` to its pdftotext index.

    The corpus `pdf_page` field does NOT use one convention across volumes: for
    19Khu02, 06Di01 and 09Ma01 it is the 1-based printed PDF page (index =
    pdf_page - 1), while for 18Khu01 and 12Sam01 the anchors sit two pages low
    (index = pdf_page + 1; 12Sam01's +2 drift is noted in HANDOFF.md).  Assuming
    either convention silently mis-pages one group or the other — which is how
    the apparatus tools were anchoring notes a page early, and why 19Khu02's
    first page of footnotes was never compared at all.

    So measure it: try each offset and keep the one that puts the most
    paragraphs' opening words on the page they claim.  The winner is decisive
    (400/400 against <100 for the runner-up on every volume tested), so a weak
    winner is itself worth reporting.
    """
    if vol in _PAGE_OFF:
        return _PAGE_OFF[vol]
    if paras is None:
        paras = json.load(open(f'{ROOT}/site/{vol}.json', encoding='utf-8'))['paragraphs']
    if pages is None:
        pages = pdftext(vol).split('\f')
    npg = [norm(x) for x in pages]
    samp = [p for p in paras if p.get('pdf_page') and len(norm(p.get('text') or '')) > 60][:400]
    best, score = 0, -1
    for off in (-2, -1, 0, 1, 2):
        hit = 0
        for p in samp:
            i = p['pdf_page'] + off
            if 0 <= i < len(npg):
                probe = ' '.join(norm(p['text']).split()[:6])
                if probe and probe in npg[i]:
                    hit += 1
        if hit > score:
            best, score = off, hit
    _PAGE_OFF[vol] = best
    return best
