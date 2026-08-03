# -*- coding: utf-8 -*-
"""EVERYTHING that carries per-paragraph state for a volume, counted.

The phase-1 doc listed bold/, apparatus/, verse/, uddana/, hide/, sections/ and
the three full rebuilds.  This is the complete list, measured rather than
recalled, with the count of entries touching 20KhuA01 and how each is keyed.
"""
import json, os, re, glob, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
V = '20KhuA01'


def n(p):
    try:
        d = json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
    except Exception:
        return None
    return len(d)


rows = [
    ('site/reader/bold/%s.bold.json' % V, 'ordinal -> [[a,b],..] char offsets', 'SOLVED, commit 4d4a1db7'),
    ('site/reader/bold/%s.sect.json' % V, 'ord:index -> offsets into a sections heading', 'absent here; present in 10 volumes'),
    ('site/reader/apparatus/%s.app.json' % V, 'paragraph id', 'rebuild (doc section 4)'),
    ('site/reader/apparatus/%s.appk.json' % V, 'ordinal', 'rebuild (doc section 4)'),
    ('site/reader/verse/%s.json' % V, 'ordinal of the numbered UNIT', 'BLOCKER 2 -- b2/'),
    ('site/reader/uddana/%s.json' % V, 'ordinal it FOLLOWS', 'BLOCKER 3 -- b3/'),
    ('site/reader/hide/%s.json' % V, 'ordinal, as a SET', 'BLOCKER 3 -- b3/'),
    ('site/reader/sections/%s.json' % V, 'ordinal it HEADS', 'BLOCKER 3 -- b3/'),
    ('site/reader/incipit/%s.json' % V, 'ordinal it precedes', 'b3/ -- WAS NOT ON THE LIST'),
    ('site/reader/booktitle/%s.json' % V, 'ordinal the book opens at', 'b3/ -- WAS NOT ON THE LIST'),
    ('site/reader/ord/%s.json' % V, 'paragraph NUMBER -> ordinal (panel.js)', 'b3/ -- WAS NOT ON THE LIST'),
    ('site/reader/xrefs/%s.json' % V, 'ordinal', 'empty here; non-empty elsewhere -- NOT ON THE LIST'),
    ('site/reader/linksk/%s.rev.json' % V, 'ordinal -> canon key', 'rebuild -- NOT ON THE LIST'),
    ('site/index/%s.idx.json' % V, 'positional postings into paras', 'rebuild (doc section 5)'),
]
print('%-46s %6s  %-42s %s' % ('file', 'keys', 'keyed by', 'status'))
for p, k, st in rows:
    print('%-46s %6s  %-42s %s' % (p.replace('site/reader/', ''), n(p), k, st))

pg = json.load(open(os.path.join(ROOT, 'site/reader/pagespan.json'), encoding='utf-8'))
pi = json.load(open(os.path.join(ROOT, 'site/reader/pageindex.json'), encoding='utf-8'))
print('%-46s %6d  %-42s %s' % ('pagespan.json[VOL]', len(pg.get(V, {})),
                               'ordinal -> last printed page', 'rebuild (doc section 5)'))
print('%-46s %6d  %-42s %s' % ('pageindex.json[VOL]', len(pi.get(V, {})),
                               'printed page -> ordinal', 'rebuild (doc section 5)'))
nav = open(os.path.join(ROOT, 'site/reader/nav.json'), encoding='utf-8').read()
print('%-46s %6d  %-42s %s' % ('nav.json', len(re.findall(r'"%s#(\d+)"' % V, nav)),
                               '<VOL>#<ordinal> node keys', 'rebuild -- WAS NOT ON THE LIST'))
ext = collections.Counter()
for f in glob.glob(os.path.join(ROOT, 'site/reader/linksk/*.links.json')):
    c = len(re.findall(r'"%s#\d+"' % V, open(f, encoding='utf-8').read()))
    if c:
        ext[os.path.basename(f)] = c
print('%-46s %6d  %-42s %s'
      % ('linksk/*.links.json (OTHER volumes)', sum(ext.values()),
         '<VOL>#<ordinal> targets pointing INTO this volume',
         'rebuild -- WAS NOT ON THE LIST'))
print('     from: %s' % dict(ext))
