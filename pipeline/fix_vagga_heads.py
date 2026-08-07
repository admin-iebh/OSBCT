#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reclassify section heads that NAME a vagga but are marked `sutta`.

REPORTED BY THE READER, 2026-08-07, about `33KhuA14`:

    "Page viii `19. Kuṭajapupphiyavaggavaṇṇanā` should be centered in the PDF
    since it is the title of the vagga like `18. Kumudavagga`.  The case is the
    same with `20. Tamālapupphiyavaggavaṇṇanā` and the rest until
    `34. Gandhodakavaggādivaṇṇanā`.  All these should be treated like
    `18. Kumudavagga`, that is as a Commentary of a vagga."

WHAT IT COST.  The extraction takes a head's KIND from its typography, and the
PDF does not centre these, so fourteen vagga titles in `33KhuA14` were recorded
as `sutta`.  A vagga region is bounded by the next VAGGA head, so vagga 18's
region ran from ord 472 to ord 560 -- swallowing every declaration for vaggas
19-39.  Inside that over-wide region a bare paragraph number then matched
wherever it liked: canon n=2 of `1. Kumudamāliyatthera-apadāna` was reported as
held by `27. Padumukkhipavaggavaṇṇanā`, which is the number-as-address fault the
whole `link_by_toc.py` design exists to prevent, let back in through the
boundaries rather than the matching.

THE TEST IS THE NAME, NOT THE TYPOGRAPHY.  A head whose stem ends in `vagga`
after `-vaṇṇanā` and a trailing `ādi` are stripped is a vagga head.  That is a
statement about the words the edition printed, which is evidence; centring is a
statement about how a typesetter laid them out, which is not.

!!! `book` IS LEFT ALONE.  `18Khu01` marks the Dhammapada's `1. Yamakavagga`
and its fellows as `book`, and that is deliberate -- they head works in the nav
tree.  Only `sutta` is reclassified, and only where the name decides.

Corpus-wide this finds 258 heads in 18 volumes.  This script changes ONE volume
per run, on purpose: `build_links_bynum.py` records what a corpus-wide sweep
cost the last time one was attempted.

Usage:
  python3 pipeline/fix_vagga_heads.py 33KhuA14            # report only
  python3 pipeline/fix_vagga_heads.py 33KhuA14 --apply    # rewrite sections/
  python3 pipeline/fix_vagga_heads.py --census            # all volumes, no write
"""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = os.path.join(ROOT, 'site', 'reader', 'sections')

TAIL = re.compile(r'(vaṇṇanā|vaṇṇanaṁ|vaṇṇana)$')


def names_vagga(l):
    """True if the head names a vagga.

    !!! `vaggādi` IS `vagga` + `ādi`, AND THE VOWELS HAVE ALREADY COALESCED.
    Stripping a literal `ādi` off `kaṇikārapupphiyavaggādivaṇṇanā` leaves
    `...vagg`, not `...vagga`, because the final -a of *vagga* and the initial
    ā- of *ādi* are one vowel in the printed word.  The first version of this
    function did exactly that and so missed every `ādi` head -- `21-23.
    Kaṇikārapupphiyavaggādivaṇṇanā`, `34. Gandhodakavaggādivaṇṇanā`,
    `43. Sakiṁsammajjakavaggādivaṇṇanā`, `50. Kiṅkaṇipupphavaggādivaṇṇanā` --
    which are precisely the heads that cover SEVERAL vaggas at once and so
    matter most for the boundaries.  Both endings are therefore tested
    directly, and no vowel is un-sandhied by hand.
    """
    s = re.sub(r'[^a-zāīūṁṃṅñṭḍṇḷ]', '', (l or '').lower())
    p = None
    while p != s:
        p = s
        s = TAIL.sub('', s)
    return s.endswith('vagga') or s.endswith('vaggādi')


def scan(v):
    S = json.load(open(os.path.join(SEC, v + '.json'), encoding='utf-8'))
    hits = []
    for k in sorted(S, key=int):
        for j, x in enumerate(S[k]):
            if x.get('k') == 'sutta' and names_vagga(x['l']):
                hits.append((int(k), j, x['l']))
    return S, hits


def apply(v, S, hits):
    for k, j, l in hits:
        S[str(k)][j]['k'] = 'vagga'
        # !!! THE ORIGINAL CLASSIFICATION IS KEPT, NOT OVERWRITTEN.  Working
        # principle 3: this is a correction to OUR extraction, made on the
        # reader's authority about the printed page, and the next person must be
        # able to see that it was made and what it was before.
        S[str(k)][j]['k_was'] = 'sutta'
        S[str(k)][j]['k_why'] = 'names a vagga; reader 2026-08-07'
    json.dump(S, open(os.path.join(SEC, v + '.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)


if __name__ == '__main__':
    if '--census' in sys.argv:
        tot = collections.Counter()
        for f in sorted(os.listdir(SEC)):
            if not f.endswith('.json'):
                continue
            v = f[:-5]
            _, h = scan(v)
            if h:
                tot[v] = len(h)
        for v, c in tot.most_common():
            print('  %-10s %4d' % (v, c))
        print('  %d volumes, %d heads' % (len(tot), sum(tot.values())))
        sys.exit(0)
    a = [x for x in sys.argv[1:] if not x.startswith('-')]
    if len(a) != 1:
        print(__doc__)
        sys.exit(2)
    v = a[0]
    S, hits = scan(v)
    print('%s: %d heads name a vagga but are classified `sutta`' % (v, len(hits)))
    for k, j, l in hits:
        print('   ord %-5d %s' % (k, l))
    if '--apply' in sys.argv:
        apply(v, S, hits)
        print('rewritten: %s' % os.path.join(SEC, v + '.json'))
    else:
        print('(report only; pass --apply to rewrite)')
