# -*- coding: utf-8 -*-
"""RE-KEY bold/<VOL>.sect.json when a `sections` entry SPLITS.

THE PROBLEM.  `site/reader/bold/<VOL>.sect.json` is keyed "<ord>:<entry
index>" -- an index into that ordinal's `sections` entry list -- and its values
are half-open CHARACTER OFFSETS into that entry's own text (reader2.html's
`gathaHTML` does `text.slice(a,b)`, with no stripping).  So splitting entry i
of ordinal O into k entries does two things at once:

  * every key "O:j" with j > i must shift by k-1, and
  * every span inside entry i must move to whichever NEW entry now holds the
    characters it selected, with its offsets rebased on that entry.

Doing only the first silently misplaces the split entry's own lemma spans;
doing neither misplaces every span after it.  This is the problem
`_xc/reseg/redistribute.py` solved for `bold/*.bold.json` in 4d4a1db7, and the
method is that method: locate each new text inside the old one, rebase, and
PROVE IT SEMANTICALLY rather than trust the arithmetic that produced it.

A span that STRADDLES a new boundary is refused loudly, never truncated.
"""
import json, os, sys


class Straddle(Exception):
    pass


NL = None   # set below


def _norm(s):
    """Whitespace normalised CHARACTER FOR CHARACTER -- every whitespace
    character becomes a single space, and the string keeps its length, so a
    position in the normalised frame is the same position in the original."""
    return ''.join(' ' if c.isspace() else c for c in s)


def offsets(old_text, new_texts):
    """Where each new entry's text sits inside the old entry's text.

    THE SEPARATOR CHANGES ACROSS THE SPLIT and this is the whole difficulty.
    The old k:'gatha' entry joins its printed lines with '\n'; the new
    k:'prose' entry joins the same lines with a SPACE (`hyjoin`).  So a new
    piece is NOT a literal substring of the old text and a plain `find` fails
    on six of the seven real splits -- which is how this was caught.

    '\n' and ' ' are both ONE CHARACTER, and reader2.html slices the decoded
    string, so the substitution is LENGTH PRESERVING and a character offset
    survives it unchanged.  Matching is therefore done in a length-preserving
    whitespace-normalised frame, and the offsets it yields are valid in the
    original.

    `hyjoin` can also DELETE a line-end hyphen when it joins, which is NOT
    length preserving.  That case cannot be redistributed by offset at all, so
    it is REFUSED here rather than quietly mismapped -- the tiling check below
    is what refuses it.
    """
    o = _norm(old_text)
    offs, cur = [], 0
    for t in new_texts:
        n = _norm(t)
        i = o.find(n, cur)
        if i < 0:
            raise Straddle('piece not found at/after %d (separator change is '
                           'handled; a hyphen JOIN is not): %r' % (cur, t[:60]))
        if o[cur:i].strip():
            raise Straddle('text dropped before piece: %r' % o[cur:i][:60])
        offs.append(i)
        cur = i + len(n)
    if o[cur:].strip():
        raise Straddle('text dropped after last piece: %r' % o[cur:][:60])
    return offs


def rekey(sect, ord_key, split_idx, old_text, new_texts, _corrupt=None):
    """-> the new sect map.  Entry `split_idx` of ordinal `ord_key` becomes
    len(new_texts) entries starting at that same index.

    `_corrupt` is for the NEGATIVE CONTROL only and is never set in use."""
    k = len(new_texts)
    offs = offsets(old_text, new_texts)
    out = {}
    for key, spans in sect.items():
        o, j = key.rsplit(':', 1)
        j = int(j)
        if o != str(ord_key) or j < split_idx:
            out[key] = [list(s) for s in spans]
            continue
        if j > split_idx:
            nj = j if _corrupt == 'noshift' else j + (k - 1)
            out.setdefault('%s:%d' % (o, nj), []).extend([list(s) for s in spans])
            continue
        for a, b in spans:
            hit = None
            for r, off in enumerate(offs):
                if off <= a and b <= off + len(new_texts[r]):
                    hit = r
                    break
            if hit is None:
                raise Straddle('span [%d,%d) straddles a new boundary in %s'
                               % (a, b, key))
            if _corrupt == 'allfirst':
                hit = 0
            na, nb = a - offs[hit], b - offs[hit]
            if _corrupt == 'shift1':
                na, nb = na + 1, nb + 1
            out.setdefault('%s:%d' % (o, split_idx + hit), []).append([na, nb])
    return out


def _selected(sect, texts):
    """[(absolute position in the ordinal's OLD text, selected substring)] for
    every span in `sect`.  `texts` maps key -> (text the key indexes into,
    that text's absolute offset within the old entry / ordinal frame)."""
    out = []
    for key, spans in sect.items():
        if key not in texts:
            out.append((None, '<<KEY %s HAS NO TEXT>>' % key))
            continue
        text, base = texts[key]
        for a, b in spans:
            if not (0 <= a < b <= len(text)):
                out.append((None, '<<OUT OF RANGE %s [%d,%d) len=%d>>'
                            % (key, a, b, len(text))))
            else:
                out.append((base + a, text[a:b]))
    return sorted(out, key=lambda x: (x[0] is None, x[0], x[1]))


def prove(sect_old, sect_new, ord_key, split_idx, old_entries, new_entries):
    """THE SEMANTIC PROOF.  Independent of `rekey`'s per-span decisions: it
    re-derives, from the two ENTRY LISTS alone, what substring each map's
    spans select and where that substring sits in the ordinal's printed text,
    then requires the two to be equal as sequences.

    Every span must select a byte-identical substring at a byte-identical
    position.  A span that lost its text, moved, or fell out of range shows up
    as an inequality, not as a silently smaller count.

    -> (checked, passed, failures)
    """
    old_text = str(old_entries[str(ord_key)][split_idx].get('l', ''))
    k = len(new_entries[str(ord_key)]) - len(old_entries[str(ord_key)]) + 1
    new_texts = [str(x.get('l', '')) for x in
                 new_entries[str(ord_key)][split_idx:split_idx + k]]
    offs = offsets(old_text, new_texts)

    # base frame: entries OTHER than the split one are their own frame (base 0
    # under a key that names them); the split entry's pieces are based on
    # where they sit inside the OLD entry text, which is what makes an old
    # span and its image comparable at all.
    told, tnew = {}, {}
    for o, arr in old_entries.items():
        for j, x in enumerate(arr):
            told['%s:%d' % (o, j)] = (str(x.get('l', '')),
                                      0 if not (o == str(ord_key) and j == split_idx) else 0)
    for o, arr in new_entries.items():
        for j, x in enumerate(arr):
            if o == str(ord_key) and split_idx <= j < split_idx + k:
                # re-key it back onto the OLD index and OLD frame
                tnew['%s:%d' % (o, j)] = (str(x.get('l', '')), offs[j - split_idx])
            else:
                oj = j - (k - 1) if (o == str(ord_key) and j >= split_idx + k) else j
                tnew['%s:%d' % (o, j)] = (str(x.get('l', '')), 0)
    # spans keyed on an entry AFTER the split must land on the SAME old entry,
    # so name them by their old index when comparing.
    def canon(sect, entries, is_new):
        out = []
        for key, spans in sect.items():
            o, j = key.rsplit(':', 1); j = int(j)
            texts = tnew if is_new else told
            if key not in texts:
                out.append((key, None, '<<NO TEXT FOR %s>>' % key)); continue
            text, base = texts[key]
            if o == str(ord_key) and is_new and j >= split_idx + k:
                oj = j - (k - 1)
            elif o == str(ord_key) and is_new and split_idx <= j < split_idx + k:
                oj = split_idx
            else:
                oj = j
            for a, b in spans:
                if not (0 <= a < b <= len(text)):
                    out.append(('%s:%d' % (o, oj), None,
                                '<<OUT OF RANGE [%d,%d) len=%d>>' % (a, b, len(text))))
                else:
                    # compared in the SAME length-preserving normalised frame
                    # the tiling uses, or the separator change ('\n' -> ' ')
                    # would read as every span having lost its text.
                    out.append(('%s:%d' % (o, oj), base + a, _norm(text)[a:b]))
        return sorted(out, key=lambda x: (x[0], x[1] is None, x[1] or 0, x[2]))

    A = canon(sect_old, old_entries, False)
    B = canon(sect_new, new_entries, True)
    checked = len(A)
    fails = []
    for x, y in zip(A, B):
        if x != y:
            fails.append((x, y))
    if len(A) != len(B):
        fails.append(('COUNT %d' % len(A), 'COUNT %d' % len(B)))
    passed = checked - len([f for f in fails if not str(f[0]).startswith('COUNT')])
    return checked, passed, fails
