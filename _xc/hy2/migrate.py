# -*- coding: utf-8 -*-
"""THE VOWEL-BRANCH MIGRATION.  Dry run unless --write is given.

WHAT IT DOES.  In `site/<VOL>.json`, every `X- Y` where the hyphen ends a word
and Y begins with a VOWEL is closed to `X-Y`: one space deleted.  That is
hyjoin's own second branch -- the edition's junction hyphen -- applied to the
paragraph text, which extract.py builds without any hyphen decision at all
(extract.py:204, `cur['text']+=' '+st`).

WHY IT IS SAFE TO DO THIS AND NOT THE CONSONANT BRANCH.  sidecheck.py: the
side-maps, which build_khu_volume.py produces WITH hyjoin, already hold the
closed form -- 207/210 on 09DiT02, 188/211 on 22AbhiT01, 79/140 on 01ViT01, and
in NOT ONE CASE does a side-map hold the broken form.  So the two layers already
disagree and the paragraph text is the side that is wrong.  This makes them
agree.  The consonant branch has no such warrant and is not touched.

WHAT ELSE MOVES.  offsets_audit.py, per artefact, checked by slicing rather than
by field name:
    bold/      OFFSETS  -- [start,end] into paragraphs[].text.  MUST SHIFT.
    verse/ sections/ uddana/ incipit/ booktitle/   verbatim drawn lines, already
               closed (above).  No change.
    apparatus/ links/ linksk/ hide/ xrefs/ ord/ pbreak/   no offsets, no
               verbatim paragraph text.  No change.

CONTROL, and it runs in the dry run.  For every bold span, the substring it
selects must be IDENTICAL before and after.  A span that selects different
letters after the shift is a defect and is counted and shown, not silently
tolerated.  The external control is check_bold_fidelity, which reads the page.

Peyyala (`-pa- `) is masked out and never closed.
"""
import json, os, re, sys, collections

BAD = re.compile(r'(?<=[a-zāīūṁṃṅñṭḍṇḷ])- (?=[aāiīuūeoAĀIĪUŪEO])')
PEY = re.compile(r'-(?:pa|pe|la)- ')
WRITE = '--write' in sys.argv
ONLY = [a for a in sys.argv[1:] if not a.startswith('--')]


def holes(t):
    """indices of the SPACES to delete, ascending"""
    return [m.start() + 1 for m in BAD.finditer(PEY.sub('#####', t))]


def shift(off, hs):
    """an offset after k deleted spaces moves back by k"""
    return off - sum(1 for h in hs if h < off)


def bold_convention(bold, paras):
    """'index' | 'n' | None -- decided ONCE PER VOLUME, by which mapping makes
    the spans slice cleanly, and then used with NO per-paragraph fallback.

    !!! THE FIRST VERSION FELL BACK PER PARAGRAPH: `str(i) if present else
    str(n)`.  On 50AbhiA03 the map is INDEX-keyed; paragraph index 348 carries
    n=366, has no key '348', so it fell through to '366' -- which is a real key
    belonging to paragraph index 366 -- and that paragraph's spans were shifted
    by a DIFFERENT paragraph's deletions.  It was written to the corpus, and
    `check_bold_fidelity` caught it as ord366 moving EXACT -> PART.  The corpus
    was restored from HEAD before anything else was done.
    """
    byidx = {str(i): (p.get('text') or '') for i, p in enumerate(paras)}
    byn = {str(p.get('n')): (p.get('text') or '') for p in paras}

    def score(m):
        ok = tot = 0
        for k, sp in list(bold.items())[:500]:
            t = m.get(k)
            if t is None:
                continue
            for a, b in sp:
                tot += 1
                s = t[a:b]
                if s and s == s.strip():
                    ok += 1
        return ok, tot
    oi, ti = score(byidx)
    on, tn = score(byn)
    if ti and oi / ti >= 0.95 and (not tn or oi / ti > on / max(1, tn)):
        return 'index'
    if tn and on / tn >= 0.95:
        return 'n'
    return None


def main():
    vols = ONLY or sorted(f[:-5] for f in os.listdir('site') if f.endswith('.json'))
    tot = collections.Counter()
    for vol in vols:
        sp = 'site/%s.json' % vol
        try:
            d = json.load(open(sp, encoding='utf-8'))
        except Exception:
            continue
        if not isinstance(d, dict) or 'paragraphs' not in d:
            continue
        paras = d['paragraphs']
        bp = 'site/reader/bold/%s.bold.json' % vol
        bold = json.load(open(bp, encoding='utf-8')) if os.path.exists(bp) else {}
        texts = [(p.get('text') or '') for p in paras]
        conv = bold_convention(bold, paras) if bold else None
        if bold and conv is None:
            print('%-10s *** BOLD KEY CONVENTION UNDECIDED -- SKIPPING VOLUME' % vol)
            continue
        st = collections.Counter()
        newbold = {}
        for i, p in enumerate(paras):
            t = texts[i]
            hs = holes(t)
            if not hs:
                continue
            st['paragraphs'] += 1
            st['deletions'] += len(hs)
            nt = ''.join(c for j, c in enumerate(t) if j not in set(hs))
            k = (str(i) if conv == 'index' else
                 str(p.get('n')) if conv == 'n' else None)
            if k is not None and k in bold:
                out = []
                for a, b in bold[k]:
                    na, nb = shift(a, hs), shift(b, hs)
                    st['spans'] += 1
                    if nb != b or na != a:
                        st['spans_shifted'] += 1
                    # A hole INSIDE the span is expected: the span loses that
                    # one space and keeps its words.  04VinA04 ord160 is the
                    # only one in the corpus -- 'tva puna- upa' -> 'tva puna-upa'.
                    # Anything else is a defect.
                    inside = [h for h in hs if a <= h < b]
                    want = ''.join(c for j, c in enumerate(t[a:b])
                                   if (j + a) not in set(inside))
                    if nt[na:nb] != want:
                        st['SPAN CONTENT CHANGED'] += 1
                        if st['SPAN CONTENT CHANGED'] <= 3:
                            print('   !! %s ord %s  %r -> %r (wanted %r)'
                                  % (vol, k, t[a:b][:40], nt[na:nb][:40], want[:40]))
                    elif inside:
                        st['span_lost_an_inner_space'] += 1
                    out.append([na, nb])
                newbold[k] = out
            if WRITE:
                p['text'] = nt
        if not st['deletions']:
            continue
        tot.update(st)
        print('%-10s paras %4d  deletions %5d  spans %6d  shifted %6d  content-changed %d'
              % (vol, st['paragraphs'], st['deletions'], st['spans'],
                 st['spans_shifted'], st['SPAN CONTENT CHANGED']))
        if WRITE:
            json.dump(d, open(sp, 'w', encoding='utf-8'), ensure_ascii=False)
            if newbold:
                bold.update(newbold)
                json.dump(bold, open(bp, 'w', encoding='utf-8'), ensure_ascii=False)
    print()
    print('%s  paragraphs %d  deletions %d  spans seen %d  shifted %d  CONTENT CHANGED %d'
          % ('WROTE' if WRITE else 'DRY RUN', tot['paragraphs'], tot['deletions'],
             tot['spans'], tot['spans_shifted'], tot['SPAN CONTENT CHANGED']))


main()
