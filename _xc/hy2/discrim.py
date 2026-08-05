# -*- coding: utf-8 -*-
"""The consonant branch: is the hyphen the EDITION'S or a soft line break?

hyjoin drops a line-end hyphen whenever the next letter is a consonant.  For
1,521 of the 8,812 that is wrong, because the edition sets a real hyphen before
a consonant in the grammatical citation form -- `ca-saddo` "the word `ca`",
`da-karassa` "of the letter `da`", `adi-saddena`.

The discriminator must not be a word list and must not come from the corpus.
It comes from the PAGE:

    a SOFT line-break hyphen exists only at a line end.  The EDITION'S hyphen
    also occurs MID-LINE.

So take the two halves, close them up with the hyphen kept, and ask whether that
string occurs anywhere in this volume's printed line stream away from a line
end.  Found -> the hyphen is the edition's, KEEP it.  Not found -> no evidence
either way from this test, and the occurrence is left for the page.

Deliberately three-valued.  `unknown` is a reported outcome, not a default that
silently takes one branch.
"""
import json, os, re, sys, collections

sys.path.insert(0, os.path.abspath('pipeline'))

BAD = re.compile(r'(?<=[a-zāīūṁṃṅñṭḍṇḷ])- (?=[A-Za-zĀĪŪāīūṁṃṅñṭḍṇḷ])')
PEY = re.compile(r'-(?:pa|pe|la)- ')
VOWELS = set('aāiīuūeoAĀIĪUŪEO')
WORD = re.compile(r'[A-Za-zĀĪŪāīūṁṃṅñÑṬṭḌḍṆṇḶḷ’‘-]+')


def line_stream(vol):
    """every printed line of the volume, from pdftotext -layout"""
    import importlib
    os.environ['BLOCKBREAK'] = '0'
    for m in list(sys.modules):
        if m.startswith('build_khu_volume'):
            del sys.modules[m]
    mod = importlib.import_module('build_khu_volume')
    mod.use(vol)
    out = []
    for pg in mod.pdf_pages():
        out += [l.rstrip() for l in pg.split('\n') if l.strip()]
    return out


def main(vol):
    lines = line_stream(vol)
    # every hyphenated token that appears NOT at the end of its printed line
    midline = set()
    for l in lines:
        for m in WORD.finditer(l):
            w = m.group(0)
            if '-' not in w or w.endswith('-'):
                continue
            if m.end() >= len(l.rstrip()):
                continue          # token sits at the line end; no evidence
            # CASEFOLDED.  The continuation half is often line-initial and
            # therefore capitalised ('Va- saddo' against a mid-line 'va-saddo'),
            # and a case-sensitive test missed every one of them.
            midline.add(w.strip('-').casefold())

    d = json.load(open('site/%s.json' % vol, encoding='utf-8'))
    st = collections.Counter()
    keep, drop, unk = [], [], []
    for p in d['paragraphs']:
        t = PEY.sub(' ', p.get('text') or '')
        for m in BAD.finditer(t):
            if t[m.end():m.end() + 1] in VOWELS:
                continue
            st['consonant'] += 1
            a = WORD.search(t[:m.start() + 1][::-1])
            b = WORD.search(t[m.end():])
            if not a or not b:
                st['unparsed'] += 1
                continue
            left = a.group(0)[::-1].rstrip('-')
            right = b.group(0)
            cand = left + '-' + right
            ctx = t[max(0, m.start() - 34):m.end() + 30].replace('\n', ' ')
            if cand.strip('-').casefold() in midline:
                st['KEEP (edition hyphen)'] += 1
                keep.append((cand, ctx))
            else:
                st['no midline evidence'] += 1
                unk.append((cand, ctx))
    print('== %s ==   printed lines %d, hyphenated mid-line tokens %d'
          % (vol, len(lines), len(midline)))
    for k, v in st.most_common():
        print('   %-24s %5d' % (k, v))
    print('   -- KEEP samples --')
    for c, x in keep[:8]:
        print('      %-28s …%s…' % (c, x))
    print('   -- no evidence samples --')
    for c, x in unk[:8]:
        print('      %-28s …%s…' % (c, x))


for v in sys.argv[1:]:
    main(v)
