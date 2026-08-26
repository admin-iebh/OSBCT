#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The section names the edition prints, which the corpus does not carry.

WHY.  Found 2026-08-26 from a link repair: `19Khu02` holds **3,660 paragraphs
and 3 distinct `sutta` values**.  The Petavatthu's first 340 paragraphs answered
to a *Vimānavatthu* section name, because `name_at` carried the last one forward
across the book boundary and there was nothing of its own to stop it.  That is
5,616 paragraphs in 44 volumes reading under the wrong heading.

The first question was "what should a paragraph with no section fall back to?"
**It was the wrong question.**  The edition prints a section name there:

    Petavatthupāḷi
    1. Uragavagga
    1. Khettūpamapetavatthu          <- printed, and absent from the corpus
    1. Khettūpamā arahanto, dāyakā kassakūpamā.
       Khettūpamapetavatthu paṭhamaṁ.
    2. Sūkaramukhapetavatthu
    4. Kāyo te sabbasovaṇṇo, ...

So this is not a display fallback.  It is **missing extracted data**, and the
repair is to read what the edition prints.

WHERE THE TEXT COMES FROM.  `pali-unicode/*.pdf` — the volumes this project
already repaired — hand back clean Unicode through `pdftotext`.  No legacy
decoding is needed and none is done here.

HOW A HEADING IS TOLD FROM A VERSE.  Both are numbered lines.  A heading is
short, carries no comma, does not end in a full stop, and ends on a section
word (`-vatthu`, `-vagga`, `-sutta`, `-gāthā`, `-nipāta`, …).  A verse runs
long and is punctuated.

**AND EVERY HEADING MUST ANCHOR, WHICH IS WHAT KEEPS THE MĀTIKĀ OUT.**  The
front matter lists every section name in order — and reading those as headings
would place hundreds of sections on page 16.  A Mātikā entry is followed by
another Mātikā entry; a body heading is followed by its first verse.  So a
heading is accepted only when a verse line follows it within a few lines, and
the number on that verse is the anchor.  Requiring the anchor is not a tidiness
check, it is the thing that separates the two sources.

SELF-VERIFYING, and this is the measure to trust rather than the count:
`--check` resolves every anchor against the corpus IN ORDER and reports any
that cannot be found, or that go backwards.  On `19Khu02`: **501 of 501
resolved in order, 0 backwards, 0 unresolvable.**

WHAT THIS INSTRUMENT DOES NOT SEE, STATED SO THE COUNT IS NOT MISREAD.  It
finds 4,279 headings over the 40 canon volumes and the corpus is missing 1,301
of them — but that is **a lower bound on the gap, not a measurement of it**,
because the extractor under-detects badly wherever headings are not numbered
lines ending in a section word:

    20Khu03  4,461 paragraphs, 1 heading found   -- Apadāna, certainly hundreds
    29Abhi01 1,780 paragraphs, 0 found
    36-40Abhi 0 found in any of them
    06Di01   1 found where the corpus already has 14

Those volumes are not evidence that the edition prints no sections there.  They
are evidence that this reads one shape of heading.  **Do not write from this
script into a volume whose `--check` does not resolve cleanly**, and do not
quote 1,301 as the size of the defect.

Usage:
  python3 pipeline/extract_sections.py                 # the corpus-wide table
  python3 pipeline/extract_sections.py 19Khu02         # one volume, listed
  python3 pipeline/extract_sections.py 19Khu02 --check # resolve every anchor
"""
import subprocess, re, json, os, sys, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
# !!! THE COMMENTARY VOLUMES NEED THIS TOO, AND HALF-DOING IT MAKES THE
# name-match GATE WORSE, NOT BETTER.  Writing the canon's real section names
# while the commentary still carries a stale carried-forward one leaves the
# comparison honest on one side and wrong on the other: 19Khu02 ¶1381 became
# `Kaṇṇamuṇḍapetivatthu` while its target still answered `Suttapetavatthuvaṇṇanā`,
# and name-match FELL. Both sides get the same treatment or neither does.
PDF_DIRS = [os.path.join(ROOT, d) for d in
            ('pali-unicode', 'atthakatha-unicode', 'tika-unicode')]


def pdf_for(vol):
    for d in PDF_DIRS:
        f = os.path.join(d, vol + '.pdf')
        if os.path.exists(f):
            return f
    return None


PDFS = os.path.join(ROOT, 'pali-unicode')

NUM = re.compile(r'^(\d+)\.\s*(.*)$')
TYPE = re.compile(r'(vatthu|vagga|sutta|gāthā|nipāta|kaṇḍa|pañha|niddesa'
                  r'|bhāṇavāra|vaṇṇanā|vaṇṇanaṁ)\s*$', re.I)


def is_head(t):
    return (len(t.split()) <= 4 and ',' not in t and not t.endswith('.')
            and bool(TYPE.search(t)))


def is_verse(t):
    return bool(t) and (',' in t or t.endswith('.') or len(t.split()) > 4)


def headings(pdf):
    """(printed section number, name, the paragraph number it opens on)"""
    txt = subprocess.run(['pdftotext', pdf, '-'],
                         capture_output=True, text=True).stdout
    out = []
    for page in txt.split('\f'):
        lines = [l.strip() for l in page.split('\n')]
        # !!! DROP THE RUNNING HEAD.  Every page opens with the nikāya or book
        # name, and `1. Uragavagga` recurring at the top of forty pages reads
        # as forty headings if it is not dropped.
        body, seen = [], 0
        for l in lines:
            if not l:
                body.append(l)
                continue
            seen += 1
            if seen == 1:
                continue
            body.append(l)
        for k, l in enumerate(body):
            m = NUM.match(l)
            if not m:
                continue
            t = m.group(2).strip()
            if not t or not is_head(t):
                continue
            nxt = None
            for j in range(k + 1, min(k + 8, len(body))):
                m2 = NUM.match(body[j])
                if not m2:
                    continue
                b = m2.group(2).strip()
                if not b or is_head(b):
                    continue
                if is_verse(b):
                    nxt = int(m2.group(1))
                    break
            if nxt is not None:
                out.append((int(m.group(1)), t, nxt))
    return out


def paras(vol):
    f = os.path.join(SITE, vol + '.json')
    if not os.path.exists(f):
        return []
    d = json.load(open(f, encoding='utf-8'))
    return d.get('paragraphs') or d.get('paras') or []


def resolve(vol, H):
    """Walk the headings in order and place each on the first paragraph, at or
    after the previous one, carrying its anchor number.  Returns
    (placements, restarts, unresolvable, backwards)."""
    C = paras(vol)
    out, restarts, missing, back = [], 0, 0, 0
    cur, prev = 0, -1
    for num, t, nx in H:
        j = None
        for o in range(cur, len(C)):
            if C[o].get('n') == nx:
                j = o
                break
        if j is None:
            for o in range(len(C)):
                if C[o].get('n') == nx:
                    j = o
                    break
            if j is None:
                missing += 1
                continue
            restarts += 1
        if j < prev:
            back += 1
        out.append((j, t, nx))
        prev, cur = j, j
    return out, restarts, missing, back


VAGGA = re.compile(r'vagga\s*$', re.I)

# --------------------------------------------------------------------------
# THE COMMENTARIES, which the canon reader could not touch.  Added 2026-08-26
# after that reader was found to yield 14 headings for a 1,480-paragraph volume.
#
# THE DIFFERENCE IS NOT THE NAME, IT IS WHAT FOLLOWS THE HEADING.  A canon
# heading is followed by its first numbered verse, so the verse number anchors
# it.  A commentary heading is followed by the *nidāna prose* — the story — and
# there is no number in sight for many lines.  Printed p.9 of 28KhuA09:
#
#     Khettūpamapetavatthuvaṇṇanā niṭṭhitā.
#     ─────
#          2. Sūkaramukhapetavatthuvaṇṇanā
#     Kāyo te sabbasovaṇṇoti idaṁ Satthari Rājagahaṁ upanissāya Veḷuvane ...
#
# So the anchor here is TEXT, not number: take the prose line that follows and
# find the corpus paragraph that opens with it.
COMM_HEAD = re.compile(r'vaṇṇanā\s*$')


def commentary_headings(pdf):
    """(printed number, name, the prose line the section opens with)"""
    txt = subprocess.run(['pdftotext', pdf, '-'],
                         capture_output=True, text=True).stdout
    out = []
    for page in txt.split('\f'):
        lines = [l.strip() for l in page.split('\n')]
        body, seen = [], 0
        for l in lines:
            if not l:
                body.append(l)
                continue
            seen += 1
            if seen == 1:
                continue
            body.append(l)
        for k, l in enumerate(body):
            m = NUM.match(l)
            if not m:
                continue
            t = m.group(2).strip()
            if not COMM_HEAD.search(t) or len(t.split()) > 3:
                continue
            op = None
            for j in range(k + 1, min(k + 5, len(body))):
                b = body[j].strip()
                if not b:
                    continue
                # !!! THIS 45 IS WHAT KEEPS THE MĀTIKĀ OUT, and it is the same
                # discriminator as the canon reader's anchor requirement wearing
                # different clothes: a Mātikā entry is followed by another
                # Mātikā entry — short — and a body heading by real prose.
                if COMM_HEAD.search(b) or len(b) < 45:
                    break
                op = b
                break
            if op:
                out.append((int(m.group(1)), t, op))
    return out


def matika(pdf):
    """The front matter lists every section of the volume, in order.  It is the
    COMPLETENESS CHECK, and this is the reason it matters more than the count:

    a heading the body scan MISSES does not leave a gap — it leaves the previous
    section's name spread over the missing one's paragraphs.  That is precisely
    the defect being repaired, re-created by a partial repair.  So the body scan
    must find as many headings as the Mātikā lists, or it must not write.
    """
    txt = subprocess.run(['pdftotext', pdf, '-'],
                         capture_output=True, text=True).stdout
    names, run = [], []
    for line in txt.split('\n'):
        l = line.strip()
        m = NUM.match(l)
        if m and COMM_HEAD.search(m.group(2).strip()) \
                and len(m.group(2).split()) <= 3:
            run.append(m.group(2).strip())
        else:
            if len(run) >= 4:
                names.extend(run)
            run = []
    if len(run) >= 4:
        names.extend(run)
    return names


def key_of(s):
    s = re.sub(r'^[\d\s.,\-–()]+', '', s or '')
    s = re.sub(r'\d+', '', s)
    return re.sub(r'[^\w]', '', s, flags=re.UNICODE).lower()


def write_commentary(vol):
    pdf = pdf_for(vol)
    if not pdf or 'unicode' not in pdf:
        print('REFUSING %s: no Unicode PDF' % vol)
        return 1
    F = commentary_headings(pdf)
    M = matika(pdf)
    if len(F) != len(M):
        print('REFUSING %s: the body scan found %d headings, the Mātikā lists '
              '%d. A missed heading does not leave a gap — it spreads the '
              'previous section over the missing one, which is the defect '
              'being repaired.' % (vol, len(F), len(M)))
        return 1
    C = paras(vol)
    NA = [key_of(p.get('text')) for p in C]
    placed, cur = [], 0
    for num, t, op in F:
        k = key_of(op)[:40]
        j = None
        for o in range(cur, len(C)):
            if k and (NA[o].startswith(k) or k in NA[o][:150]):
                j = o
                break
        if j is None:
            print('REFUSING %s: %r could not be anchored' % (vol, t))
            return 1
        placed.append((j, t))
        cur = j
    f = os.path.join(SITE, vol + '.json')
    d = json.load(open(f, encoding='utf-8'))
    P = d.get('paragraphs') or d.get('paras')
    bounds = [j for j, _ in placed] + [len(P)]
    before = len(set(p.get('sutta') for p in P if p.get('sutta')))
    for i, (j, t) in enumerate(placed):
        for o in range(j, bounds[i + 1]):
            P[o]['sutta'] = t
    json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False)
    now = len(set(p.get('sutta') for p in P if p.get('sutta')))
    print('%s: %d section names written (Mātikā agrees: %d); distinct %d -> %d'
          % (vol, len(placed), len(M), before, now))
    return 0


def write(vol):
    """Write the sutta-level names onto site/<vol>.json.

    THE FIELD REPEATS ON EVERY PARAGRAPH OF ITS SECTION, not just the first.
    That is the convention already in the data — `Rasuttamadāyikāvimānavatthu
    (4)` sits on sixty consecutive paragraphs — and `name_at` is written to
    tolerate either.  Following the data rather than the docstring, so the field
    means the same thing everywhere.

    VAGGA HEADINGS ARE NOT WRITTEN.  The extractor picks them up
    (`1. Uragavagga`) because they are real printed headings, but the corpus has
    a `vagga` field of its own and it already agrees on 24 of 25 — so these rows
    are a CROSS-CHECK on that field, not something to write into `sutta`.  The
    one disagreement is reported rather than silently repaired: ord 483 carries
    `'Itthivimāna      4. Mañjiṭṭhakavagga'`, two headings glued together with
    the index left in, where the edition prints `Mañjiṭṭhakavagga`.
    """
    pdf = pdf_for(vol)
    if not pdf or 'pali-unicode' not in pdf:
        # !!! MEASURED 2026-08-26, DO NOT REMOVE THIS WITHOUT REPEATING IT.
        # This reader is CANON-SHAPED.  On the commentaries it finds almost
        # nothing and misplaces what it finds:
        #   27KhuA08  14 headings for a 1,480-paragraph volume, 1 backwards
        #   28KhuA09   6 headings, and `Pañcaputtakhādakapetivatthuvaṇṇanā`
        #              anchored to ¶1, which is Khettūpamā — plainly wrong
        # The commentaries name their sections `...vaṇṇanā` and do not number
        # the heading line the way the canon does, so the number-anchored method
        # has nothing to hold on to.  A commentary reader is a separate piece of
        # work; until it exists, refusing is the only safe answer.
        print('REFUSING %s: this extractor is validated on the CANON volumes '
              'only (pali-unicode/). See the guard in write().' % vol)
        return 1
    H = headings(pdf)
    pl, rs, ms, bk = resolve(vol, H)
    if ms or bk:
        print('REFUSING: %d unresolvable, %d backwards — a volume whose anchors '
              'do not resolve cleanly is not one to write into' % (ms, bk))
        return 1
    C0 = paras(vol)
    if len(H) * 100 < len(C0):
        print('REFUSING: %d headings for %d paragraphs — too few to be the '
              'volume\'s real structure; the reader is missing this shape'
              % (len(H), len(C0)))
        return 1
    suttas = [(j, t) for j, t, _ in pl if not VAGGA.search(t)]
    vaggas = [(j, t) for j, t, _ in pl if VAGGA.search(t)]

    f = os.path.join(SITE, vol + '.json')
    d = json.load(open(f, encoding='utf-8'))
    C = d.get('paragraphs') or d.get('paras')
    bounds = [j for j, _ in suttas] + [len(C)]
    before = len(set(p.get('sutta') for p in C if p.get('sutta')))
    for k, (j, t) in enumerate(suttas):
        for o in range(j, bounds[k + 1]):
            C[o]['sutta'] = t
    json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False)
    now = len(set(p.get('sutta') for p in C if p.get('sutta')))
    print('%s: %d section names written over %d paragraphs; distinct %d -> %d'
          % (vol, len(suttas), len(C), before, now))

    dis = [(j, t, C[j].get('vagga')) for j, t in vaggas if C[j].get('vagga') != t]
    print('vagga cross-check: %d of %d agree with the corpus `vagga` field'
          % (len(vaggas) - len(dis), len(vaggas)))
    for j, t, have in dis:
        print('   ord %-5d edition prints %r, corpus has %r  — NOT repaired here'
              % (j, t, have))
    return 0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if args and '--write' in sys.argv:
        v = args[0]
        pdf = pdf_for(v)
        if pdf and 'pali-unicode' not in pdf:
            sys.exit(write_commentary(v))
        sys.exit(write(v))
    if args:
        vol = args[0]
        H = headings(pdf_for(vol))
        C = paras(vol)
        have = set(p.get('sutta') for p in C if p.get('sutta'))
        print('%s: %d headings printed, %d distinct; corpus carries %d'
              % (vol, len(H), len(set(t for _, t, _ in H)), len(have)))
        if '--check' in sys.argv:
            pl, rs, ms, bk = resolve(vol, H)
            print('  resolved %d/%d in order, %d restarts, %d unresolvable, '
                  '%d backwards' % (len(pl), len(H), rs, ms, bk))
            for j, t, nx in pl[:12]:
                print('   %-40s ¶%-5d -> ord %-5d %s'
                      % (t, nx, j, (C[j].get('text') or '')[:44]))
        else:
            for num, t, nx in H[:40]:
                print('   %3d. %-40s -> ¶%d' % (num, t, nx))
        return

    print('%-10s %7s %9s %10s %9s' %
          ('volume', 'paras', 'printed', 'in corpus', 'MISSING'))
    tp = tm = 0
    for pdf in sorted(glob.glob(os.path.join(PDFS, '*.pdf'))):
        v = os.path.basename(pdf)[:-4]
        C = paras(v)
        if not C:
            continue
        have = set(p.get('sutta') for p in C if p.get('sutta'))
        d = set(t for _, t, _ in headings(pdf))
        miss = len(d - have)
        print('%-10s %7d %9d %10d %9d%s'
              % (v, len(C), len(d), len(have), miss, '  <<<' if miss > 50 else ''))
        tp += len(d)
        tm += miss
    print('%-10s %7s %9d %10s %9d' % ('TOTAL', '', tp, '', tm))
    print('\nA LOWER BOUND, not the size of the defect — see the header: this '
          'reads one shape of heading and is blind in several volumes.')


if __name__ == '__main__':
    main()
