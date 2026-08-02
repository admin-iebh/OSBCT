#!/usr/bin/env python3
"""Zawgyi → Unicode for the Burmese dictionaries in the PCED dataset.

WHY THIS EXISTS.  PCED's Burmese dictionaries — "K" (Tipiṭaka Pāḷi-Myanmar),
"B" (Pali Word Grammar), "O" (Pali Roots), "R" (U Hau Sein) — are encoded in
**Zawgyi**, a legacy font hack that reuses the Myanmar Extended-A block
(U+1060–U+109F) for glyph variants.  Rendered with a Unicode font it is
nonsense.  §3 of the project instructions already anticipates this and names
the verification method: the character census.

THE RULES ARE VENDORED, NOT INVENTED.  They are the Rabbit converter's
Zawgyi→Unicode ruleset, taken verbatim from `pyidaungsu` (BSD, Ye Kyaw Thu et
al.), which is itself the Python port of Rabbit (Ngwe Tun / Solveware).  This
module copies them so the conversion has no runtime dependency on a package
that needs `pycrfsuite` (which will not install here) merely to be imported.

!!! ONE RULE IN THE VENDORED SET IS DEAD, AND IT IS FIXED HERE.  The published
table contains

    {"from": "/(\\u1073|\\u1074)/g", "to": "\\u1039\\u1011"}

— a JavaScript regex literal left as a Python string when the ruleset was
ported.  As written it matches nothing, so Zawgyi's stacked ထ (U+1073, U+1074)
survives conversion untouched.  Corrected below, and the census is what found
it: those two code points were still standing in the output.

VERIFICATION — two independent checks, neither of them my own opinion:

  1. THE CHARACTER CENSUS (§3).  After conversion no character may remain in
     U+1060–U+109F, the range Zawgyi reuses.  Any survivor is an unconverted
     glyph and is reported with its count and an example, not waved through.
  2. GOOGLE'S ZAWGYI DETECTOR (`myanmartools`), a model built independently of
     these rules.  It scores text 0..1 for "this is Zawgyi".  Input should
     score high and output low; if the output still scores high the conversion
     did not happen, whatever the census says.

Run directly for a self-test:  python3 zawgyi.py
"""
import re, sys, collections

# --- the vendored Rabbit ruleset (Zawgyi → Unicode) --------------------------
_RULES_RAW = [
    (u"(\u103d|\u1087)", u"\u103e"), (u"\u103c", u"\u103d"),
    (u"(\u103b|\u107e|\u107f|\u1080|\u1081|\u1082|\u1083|\u1084)", u"\u103c"),
    (u"(\u103a|\u107d)", u"\u103b"), (u"\u1039", u"\u103a"),
    (u"\u106a", u"\u1009"), (u"\u106b", u"\u100a"),
    (u"\u106c", u"\u1039\u100b"), (u"\u106d", u"\u1039\u100c"),
    (u"\u106e", u"\u100d\u1039\u100d"), (u"\u106f", u"\u100d\u1039\u100e"),
    (u"\u1070", u"\u1039\u100f"), (u"(\u1071|\u1072)", u"\u1039\u1010"),
    (u"\u1060", u"\u1039\u1000"), (u"\u1061", u"\u1039\u1001"),
    (u"\u1062", u"\u1039\u1002"), (u"\u1063", u"\u1039\u1003"),
    (u"\u1065", u"\u1039\u1005"),
    # !!! U+1066 AND U+1067 ARE ABSENT FROM THE PUBLISHED RULESET.  Both are
    # Zawgyi's stacked ဆ; 28,511 of them survived conversion across the four
    # dictionaries and the census found every one.  ဆ is U+1006.
    (u"(\u1066|\u1067)", u"\u1039\u1006"),
    (u"\u1068", u"\u1039\u1007"),
    (u"\u1069", u"\u1039\u1008"),
    # !!! was "/(\u1073|\u1074)/g" — a JS literal that matched nothing
    (u"(\u1073|\u1074)", u"\u1039\u1011"),
    (u"\u1075", u"\u1039\u1012"), (u"\u1076", u"\u1039\u1013"),
    (u"\u1077", u"\u1039\u1014"), (u"\u1078", u"\u1039\u1015"),
    (u"\u1079", u"\u1039\u1016"), (u"\u107a", u"\u1039\u1017"),
    (u"\u107c", u"\u1039\u1019"), (u"\u1085", u"\u1039\u101c"),
    (u"\u1033", u"\u102f"), (u"\u1034", u"\u1030"), (u"\u103f", u"\u1030"),
    (u"\u1086", u"\u103f"), (u"\u1036\u1088", u"\u1088\u1036"),
    (u"\u1088", u"\u103e\u102f"), (u"\u1089", u"\u103e\u1030"),
    (u"\u108a", u"\u103d\u103e"),
    (u"([\u1000-\u1021])\u1064", u"\u1004\u103a\u1039\\1"),
    (u"([\u1000-\u1021])\u108b", u"\u1004\u103a\u1039\\1\u102d"),
    (u"([\u1000-\u1021])\u108c", u"\u1004\u103a\u1039\\1\u102e"),
    (u"([\u1000-\u1021])\u108d", u"\u1004\u103a\u1039\\1\u1036"),
    (u"\u108e", u"\u102d\u1036"), (u"\u108f", u"\u1014"), (u"\u1090", u"\u101b"),
    # !!! THE PUBLISHED RULE FOR U+1091 REPRODUCES ITSELF: it maps U+1091 to
    # "\u100f\u1039\u1091", so the character it is meant to remove is still
    # in its own replacement and 17,729 of them came through untouched.  The
    # glyph is ဏ္ဍ = ဏ U+100F + virama + ဍ U+100D; the third code point is a
    # typo for U+100D.
    (u"\u1091", u"\u100f\u1039\u100d"),
    (u"\u1019\u102c(\u107b|\u1093)", u"\u1019\u1039\u1018\u102c"),
    (u"(\u107b|\u1093)", u"\u103a\u1018"), (u"(\u1094|\u1095)", u"\u1037"),
    (u"\u1096", u"\u1039\u1010\u103d"), (u"\u1097", u"\u100b\u1039\u100b"),
    (u"\u103c([\u1000-\u1021])([\u1000-\u1021])?", u"\\1\u103c\\2"),
    (u"([\u1000-\u1021])\u103c\u103a", u"\u103c\\1\u103a"),
    (u"\u1031([\u1000-\u1021])(\u103e)?(\u103b)?", u"\\1\\2\\3\u1031"),
    (u"([\u1000-\u1021])\u1031([\u103b\u103c\u103d\u103e]+)", u"\\1\\2\u1031"),
    (u"\u1032\u103d", u"\u103d\u1032"), (u"\u103d\u103b", u"\u103b\u103d"),
    (u"\u103a\u1037", u"\u1037\u103a"),
    (u"\u102f(\u102d|\u102e|\u1036|\u1037)\u102f", u"\u102f\\1"),
    (u"\u102f\u102f", u"\u102f"),
    (u"(\u102f|\u1030)(\u102d|\u102e)", u"\\2\\1"),
    (u"(\u103e)(\u103b|\u1037)", u"\\2\\1"),
    (u"\u1025(\u103a|\u102c)", u"\u1009\\1"), (u"\u1025\u102e", u"\u1026"),
    (u"\u1005\u103b", u"\u1008"), (u"\u1036(\u102f|\u1030)", u"\\1\u1036"),
    (u"\u1031\u1037\u103e", u"\u103e\u1031\u1037"),
    (u"\u1031\u103e\u102c", u"\u103e\u1031\u102c"), (u"\u105a", u"\u102b\u103a"),
    (u"\u1031\u103b\u103e", u"\u103b\u103e\u1031"),
    (u"(\u102d|\u102e)(\u103d|\u103e)", u"\\2\\1"),
    (u"\u102c\u1039([\u1000-\u1021])", u"\u1039\\1\u102c"),
    (u"\u103c\u1004\u103a\u1039([\u1000-\u1021])", u"\u1004\u103a\u1039\\1\u103c"),
    (u"\u1039\u103c\u103a\u1039([\u1000-\u1021])", u"\u103a\u1039\\1\u103c"),
    (u"\u103c\u1039([\u1000-\u1021])", u"\u1039\\1\u103c"),
    (u"\u1036\u1039([\u1000-\u1021])", u"\u1039\\1\u1036"),
    (u"\u1092", u"\u100b\u1039\u100c"),
    (u"\u104e", u"\u104e\u1004\u103a\u1038"),
    (u"\u1040(\u102b|\u102c|\u1036)", u"\u101d\\1"),
    (u"\u1025\u1039", u"\u1009\u1039"),
    (u"([\u1000-\u1021])\u103c\u1031\u103d", u"\\1\u103c\u103d\u1031"),
    (u"([\u1000-\u1021])\u103d\u1031\u103b", u"\\1\u103b\u103d\u1031"),
]
_RULES = [(re.compile(a), b) for a, b in _RULES_RAW]

# the range Zawgyi reuses for its glyph variants; nothing here may survive
ZAWGYI_RANGE = (0x1060, 0x109F)
# U+104E is legitimate Unicode Burmese (the abbreviation sign) and U+109E/F are
# real symbols, but neither occurs in this material; anything in the range is
# reported and judged, not silently allowed.


# The kinzi rules need the character before them to be a plain consonant, and
# in the source it is often a STACKED one that only becomes plain after the
# expansion rules above have run.  The published order applies kinzi first, so
# those instances are missed.  Rather than reorder a ruleset that is otherwise
# correct, run the four kinzi rules once more at the end; the census is what
# says whether that was enough.
_KINZI = [(re.compile(a), b) for a, b in (
    (u"([\u1000-\u1021])\u1064", u"\u1004\u103a\u1039\\1"),
    (u"([\u1000-\u1021])\u108b", u"\u1004\u103a\u1039\\1\u102d"),
    (u"([\u1000-\u1021])\u108c", u"\u1004\u103a\u1039\\1\u102e"),
    (u"([\u1000-\u1021])\u108d", u"\u1004\u103a\u1039\\1\u1036"),
)]


def convert(text):
    """Zawgyi → Unicode.  Deterministic, reversible in the sense §3 means:
    it is script transcoding, not translation."""
    if not text:
        return text
    for rx, to in _RULES:
        text = rx.sub(to, text)
    for rx, to in _KINZI:
        text = rx.sub(to, text)
    return text


def census(text):
    """§3's check: which characters are left that should not be?"""
    bad = collections.Counter()
    for ch in text:
        if ZAWGYI_RANGE[0] <= ord(ch) <= ZAWGYI_RANGE[1]:
            bad[ch] += 1
    return bad


def report(name, before, after, samples=2):
    """Census + Google's detector, printed so the numbers can be read rather
    than trusted."""
    bad = census(after)
    line = f'{name}: {len(after):,} chars'
    if bad:
        worst = ', '.join(f'U+{ord(c):04X}×{n}' for c, n in bad.most_common(5))
        line += f'  !!! {sum(bad.values()):,} unconverted in U+1060–109F ({worst})'
    else:
        line += '  census clean (nothing left in U+1060–109F)'
    try:
        from myanmartools import ZawgyiDetector
        d = ZawgyiDetector()
        pb, pa = d.get_zawgyi_probability(before[:20000]), \
                 d.get_zawgyi_probability(after[:20000])
        line += f'  |  detector: in {pb:.2f} → out {pa:.2f}'
        if pa > 0.5:
            line += '  !!! output still reads as Zawgyi'
    except Exception as e:
        line += f'  |  detector unavailable ({e})'
    print(line)
    return bad


if __name__ == '__main__':
    # self-test on a known pair: the Zawgyi and Unicode spellings of မြန်မာ
    zg = '\u103b\u1019\u1014\u1039\u1019\u102c'
    uni = convert(zg)
    expect = '\u1019\u103c\u1014\u103a\u1019\u102c'
    print('self-test မြန်မာ:', 'OK' if uni == expect else f'FAIL {uni!r} != {expect!r}')
    # the rule the census caught: stacked ထ
    zg2 = '\u1000\u1073'
    print('stacked ထ (U+1073):', repr(convert(zg2)),
          'OK' if '\u1073' not in convert(zg2) else 'FAIL — still Zawgyi')
