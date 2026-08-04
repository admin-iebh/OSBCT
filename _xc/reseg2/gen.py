# -*- coding: utf-8 -*-
"""Generate volume-parameterised copies of the phase-1/2 side-map scripts.

The originals in _xc/reseg/{b1,b2,b3}/ are hardcoded to 20KhuA01.  Rather than
rewrite them (which would lose the proofs they carry), this makes copies under
_xc/reseg2/{b1,b2,b3}/ with EXACTLY the hardcoded constants replaced, each
substitution asserted to fire exactly once.  The layout is mirrored so the
HERE/ROOT path arithmetic inside them still resolves.

    python3 _xc/reseg2/gen.py          # regenerate
"""
import os, shutil, re
ROOT = os.path.abspath('.')
SRC = ROOT + '/_xc/reseg'
DST = ROOT + '/_xc/reseg2'

for d in ('b1', 'b2', 'b3'):
    os.makedirs(DST + '/' + d, exist_ok=True)
for f in ('pline.py', 'locate.py'):
    shutil.copy2(SRC + '/' + f, DST + '/' + f)
for f in os.listdir(SRC):
    if f.startswith('_pline_') and not os.path.exists(DST + '/' + f):
        shutil.copy2(SRC + '/' + f, DST + '/' + f)

SUBS = [
    ("VOL = '20KhuA01'\n",                     "VOL = os.environ['VOL']\n"),
    ("VOL = sys.argv[1] if len(sys.argv) > 1 else '20KhuA01'\n",
                                               "VOL = os.environ['VOL']\n"),
    ("'_xc/reseg/%s.json' % VOL",              "'_xc/reseg2/%s.json' % VOL"),
    ("'_xc/reseg/ord_remap_%s.json' % VOL",    "'_xc/reseg2/ord_remap_%s.json' % VOL"),
    ("os.path.join(ROOT, '_xc', 'reseg', 'b1')", "os.path.join(ROOT, '_xc', 'reseg2', 'b1')"),
]

# --- ONE BEHAVIOURAL PATCH, NOT A CONSTANT ---------------------------------
# `sections_by_print` retried the search FROM ZERO when a heading could not be
# located after the cursor.  On 20KhuA01 that rescued four leaked headings; on
# 23KhuA04 it silently mis-anchored ALL EIGHT vagga headings to ordinal 0,
# because those headings are NOT PRINTED IN THE BODY AT ALL -- their only
# occurrence in the line stream is the front-matter contents page, and the
# retry found that.  The check could not see it: the contents page really is
# printed before paragraph 0, so `check_before` returned ok on all 89.
# A heading that cannot be located after the cursor is now REFUSED and left at
# first-of-run, and the refusals are counted and printed.
PATCH_SECBYPRINT = ("""            loc = locate_lines(lines, cur)
            if loc is None:
                loc = locate_lines(lines, 0)
            if loc is None:
                tgt = RUNS[int(k)][0]
            else:
                cur = loc[1]
                tgt = _following(loc[1])""",
"""            loc = locate_lines(lines, cur)
            if loc is None:
                tgt = RUNS[int(k)][0]
                _refused.append((k, lines[0][:48] if lines else ''))
            else:
                cur = loc[1]
                tgt = _following(loc[1])""")
# --- SECOND BEHAVIOURAL PATCH: the cursor must start at the BODY -----------
# `sections_by_print` started its cursor at letter 0, i.e. inside the FRONT
# MATTER.  20KhuA01's front matter does not repeat its headings, so this was
# invisible.  23KhuA04 prints a full contents listing (Ganthārambhakathā, every
# vagga, every sutta) before the body, and the cursor locked onto it: 68 of 89
# headings were anchored to the contents page, and `check_before` returned ok
# on every one of them, because the contents page really is printed before
# paragraph 0.  A check that passes on wrong input is not a check.
# b2's `locate_blocks` already starts at NA[0][2]; this makes them agree.
PATCH_SECCOUNT = ("""def sections_by_print(secmap):
    out = {}
    cur = 0
    moved = 0""",
"""def sections_by_print(secmap):
    out = {}
    cur = NA[0][2] if (NA and NA[0]) else 0   # the BODY, not the front matter
    moved = 0
    _refused = []""")
PATCH_SECPRINT = ("""    print('   headings whose printed position puts them on a DIFFERENT new '
          'ordinal from first-of-run: %d' % moved)""",
"""    print('   headings whose printed position puts them on a DIFFERENT new '
          'ordinal from first-of-run: %d' % moved)
    print('   headings NOT LOCATABLE on the page after the cursor -> REFUSED, '
          'left at first-of-run: %d' % len(_refused))
    for _r in _refused[:12]:
        print('        refused old ord %-5s %r' % _r)""")

# --- THIRD BEHAVIOURAL PATCH: a "restored" block the SHIPPED READER DREW ----
# b2 calls a block "restored" when its printed position falls in no new
# paragraph -- printed matter the corpus does not hold.  Under RESTORE=0 it
# dropped all of them, "as the shipped reader drops them".  That is true only
# of blocks belonging to an entry with NO `groups` key, which reader2.html:1474
# never draws.  20KhuA01's four were all of that kind, so the equivalence held.
# 24KhuA05 has one in an entry that DOES carry `groups`: the shipped reader
# draws it, and dropping it lost the printed sutta heading
# `1-2-3. Mohapariññādisuttavaṇṇanā` -- 28 letters off the page.
# So the test is not "restored" but "did the shipped reader draw it".
PATCH_RENDEROLD = ("""    _opt = dict(_opt or {})""",
"""    _opt = dict(_opt or {})
    RENDERED_OLD = {int(_k) for _k, _v in verse.items() if 'groups' in _v}""")
PATCH_RESTORED = ("""        corpus_bs = [b for b in bs if not b.get('restored')]""",
"""        corpus_bs = [b for b in bs if not b.get('restored')]
        drawn_bs = [b for b in bs if (not b.get('restored'))
                    or (b['old'] in RENDERED_OLD)]""")
PATCH_NOTRESTORE = ("""        if not RESTORE:
            bs = corpus_bs""",
"""        if not RESTORE:
            bs = drawn_bs""")

# --- FOURTH BEHAVIOURAL PATCH: a straddle is an OVERLAP, not two endpoints --
# `assign` decided straddling from `owner(start)` and `owner(end-1)` only.  A
# printed block that begins inside paragraph P, swallows the WHOLE of P+1, and
# ends in the gap after it (a gap is real: printed headings belong to no
# paragraph) has owner(end-1) = None, so `own_end` fell back to `own` and no
# straddle was reported -- while P+1, un-merged and un-hidden, went on
# rendering its own text.  24KhuA05 ord528/529: the gāthā pāda
# `Madhuram imaṁ paguṇaṁ suvibhattaṁ` was drawn TWICE, +30 letters.
# 20KhuA01 has no block that swallows a whole paragraph, so it never showed.
# The set of paragraphs a block straddles is now every paragraph whose printed
# extent INTERSECTS the block's span.
PATCH_COVERED = ("""def assign(items):
    straddle = []""",
"""def covered(a, b):
    '''every paragraph whose printed extent intersects [a, b)'''
    j = bisect.bisect_right(STARTS, a) - 1
    if j < 0:
        j = 0
    out = []
    while j < len(NA) and NA[j][2] < b:
        if NA[j][3] > a:
            out.append(j)
        j += 1
    return out


def assign(items):
    straddle = []""")
PATCH_ASSIGN = ("""        a, b = owner(sp[0]), owner(sp[1] - 1)
        if a is None and b is None:
            it['own'] = following(sp[1])       # restored verse: goes ABOVE the
            it['as'] = 'before'                # paragraph that follows it
            it['restored'] = True
            unowned.append(it)
            continue
        it['own'] = a if a is not None else b
        it['own_end'] = b if b is not None else a
        it['as'] = 'after'
        if it['own'] != it['own_end']:
            straddle.append(it)""",
"""        cov = covered(sp[0], sp[1])
        if not cov:
            it['own'] = following(sp[1])       # restored verse: goes ABOVE the
            it['as'] = 'before'                # paragraph that follows it
            it['restored'] = True
            unowned.append(it)
            continue
        it['own'] = cov[0]
        it['own_end'] = cov[-1]
        it['as'] = 'after'
        if len(cov) > 1:
            straddle.append(it)""")

# --- FIFTH BEHAVIOURAL PATCH: uddana/ by PRINTED POSITION, not last-of-run --
# `uddana/` is keyed by the paragraph it FOLLOWS.  Under the shipped lumps,
# last-of-run was that paragraph 23 times out of 33 in 20KhuA01 and the rest
# were the corpus-holds-it class, so last-of-run shipped.  It does NOT hold in
# 21KhuA02: `uddana @ last-of-run` locates only 27 of 113 blocks after their
# anchor and misses 85.  The Dhammapada-aṭṭhakathā closes every vatthu with a
# colophon, and a shipped lump swallows text printed AFTER the colophon, so the
# last paragraph of the run is far past it.  The visible cost was an ORDERING
# error the whole-volume equivalence caught at delta 0:
# `Maṭṭhakuṇḍalīvatthu dutiyaṁ.` was drawn after the heading `3. Tissatthera
# vatthu` instead of before it.
# The block is now anchored to the paragraph it follows ON THE PAGE, exactly as
# sections/ is anchored to the paragraph it heads; unlocatable blocks are
# REFUSED and left at last-of-run rather than guessed.
PATCH_UDDPRINT = ("""# =============================================================== write ======""",
"""# ============================================== uddana by printed position ==
ENDS = [a[3] if a else 0 for a in NA]


def _preceding(off):
    o = owner_of(off)
    if o is not None:
        return o
    j = bisect.bisect_right(ENDS, off) - 1
    return max(0, j)


def owner_of(off):
    j = _bisect.bisect_right(STARTS, off) - 1
    if 0 <= j < len(NA) and NA[j] and NA[j][2] <= off < NA[j][3]:
        return j
    return None


import bisect
def uddana_by_print(uddmap):
    out = {}
    cur = NA[0][2] if (NA and NA[0]) else 0
    moved = 0
    refused = []
    for k in sorted(uddmap, key=int):
        for b in uddmap[k]:
            lines = block_text(b)
            loc = locate_lines(lines, cur) if lines else None
            if loc is None:
                tgt = RUNS[int(k)][-1]
                refused.append((k, (lines or [''])[0][:48]))
            else:
                cur = loc[1]
                tgt = _preceding(loc[0])
            if tgt != RUNS[int(k)][-1]:
                moved += 1
            out.setdefault(str(tgt), []).append(b)
    print('   uddana blocks whose printed position puts them on a DIFFERENT new '
          'ordinal from last-of-run: %d' % moved)
    print('   uddana blocks NOT LOCATABLE on the page -> REFUSED, left at '
          'last-of-run: %d' % len(refused))
    for r in refused[:8]:
        print('        refused old ord %-5s %r' % r)
    return out


print()
print('=== uddana/ re-anchored by PRINTED POSITION ===')
udd_print = uddana_by_print(udd)
verify(udd_print, 'after', udd_lines, 'uddana @ printed position')

# =============================================================== write ======""")
PATCH_UDDWRITE = ("""    out = {'uddana': udd_last, 'hide': hide_new, 'sections': sec_print,""",
"""    out = {'uddana': udd_print, 'hide': hide_new, 'sections': sec_print,""")
PATCH_UDDLOSS = ("""    b = json.dumps([udd_last[k] for k in sorted(udd_last, key=int)], ensure_ascii=False, sort_keys=True)""",
"""    b = json.dumps([_b for k in sorted(udd_print, key=int) for _b in udd_print[k]], ensure_ascii=False, sort_keys=True)""")
PATCH_UDDLOSSA = ("""    a = json.dumps([udd[k] for k in sorted(udd, key=int)], ensure_ascii=False, sort_keys=True)""",
"""    a = json.dumps([_b for k in sorted(udd, key=int) for _b in udd[k]], ensure_ascii=False, sort_keys=True)""")

# --- a hook, not a behaviour change: expose the two render strings so the
# divergences can be enumerated and adjudicated against the page.
PATCH_HOOK = ("""        return ''.join(out)""",
"""        globals().setdefault('_CHUNKS', []).append(list(out))
        return ''.join(out)""")

# --- SIXTH PATCH: carry the no-`groups` verse entries through --------------
# phase 3 §2.  An entry with no `groups` key is never drawn by
# reader2.html:1474, but it IS in the shipped MAP, and `verify_render_vs_pdf`
# measures the map.  Dropping it reads as printed lines missing from the
# render.  Carried at the printed position b2 already found, in its shipped
# shape and still WITHOUT `groups`, so the browser ignores it exactly as today.
PATCH_CARRY = ("""    P('=== 3. NEW MAP  (RESTORE=%d) ===' % RESTORE)""",
"""    _carried = 0
    for _k, _v in verse.items():
        if 'groups' in _v:
            continue
        _tg = [it['own'] for it in items
               if it['old'] == int(_k) and it['own'] is not None]
        if not _tg:
            continue
        _key = str(find(min(_tg)))
        if _key in new_verse:          # never clobber a rebuilt entry
            _key = None
        if _key is not None:
            # THE SLOT COMES FROM THE PRINTED POSITION, not from the shipped
            # entry.  Under the lumps `before` and `after` were the same place;
            # after re-segmentation they are not.  23KhuA04's carried gāthā
            # `Sītibhūtosmi nibbuto”ti3–` is printed ABOVE the paragraph that
            # opens `ādinā Theragāthāsu–`, and keeping the shipped `after`
            # cost one chunk in verify_render_vs_pdf that the pre-state did not
            # have.  b2 already computed `as` for every one of these blocks.
            _its = [it for it in items if it['old'] == int(_k)
                    and it['own'] is not None]
            _slot = ('before' if _its and all(it.get('as') == 'before'
                                              for it in _its) else 'after')
            _blocks = [b for _s in ('before', 'after') for b in (_v.get(_s) or [])]
            new_verse[_key] = {_slot: _blocks}
            _carried += 1
    P('   no-`groups` entries carried through unchanged (never drawn, but the '
      'map holds them): %d' % _carried)
    P('=== 3. NEW MAP  (RESTORE=%d) ===' % RESTORE)""")

# --- SEVENTH PATCH: a `groups` block moved into before/after needs a SHAPE --
# A block from the `groups` role is a bare LIST of pādas.  Emitting it verbatim
# into `before`/`after` produced a shape no consumer accepts: reader2.html's
# `proseOne` handles `{gatha:[...]}` or a string, and `rebuild_apparatus.py:189`
# does `x.get('gatha')` and CRASHED on 21KhuA02 with AttributeError.
# The letter-equivalence check did not see it -- `btxt` fell through to
# `json.dumps(b)` and the JSON punctuation is stripped by the letters filter, so
# the letters matched while the shape was wrong.  A check on letters is blind to
# shape; this is the second thing in this work that passed on bad input.
# 118 blocks in 21KhuA02, and that volume alone in the corpus.
PATCH_SHAPE = ("""        if before:
            e['before'] = [b['b'] for b in before]
        e['after'] = [b['b'] for b in after]""",
"""        def _emit(x):
            # a bare list is a `groups` block; give it the gāthā shape every
            # consumer already understands
            return {'gatha': list(x['b'])} if isinstance(x['b'], list) else x['b']
        if before:
            e['before'] = [_emit(b) for b in before]
        e['after'] = [_emit(b) for b in after]""")

FILES = ['b1/b1_ids.py', 'b2/b2_verse.py', 'b3/b3_sidemaps.py', 'b3/locate_paras.py']
EXTRA = {'b3/b3_sidemaps.py': [PATCH_SECCOUNT, PATCH_SECBYPRINT, PATCH_SECPRINT,
                               PATCH_UDDPRINT, PATCH_UDDWRITE,
                               PATCH_UDDLOSSA, PATCH_UDDLOSS],
         'b2/b2_verse.py': [PATCH_RENDEROLD, PATCH_RESTORED, PATCH_NOTRESTORE,
                            PATCH_COVERED, PATCH_ASSIGN, PATCH_HOOK,
                            PATCH_CARRY, PATCH_SHAPE]}
# --- EIGHTH PATCH: read the PRE-state ---------------------------------------
# The preparation scripts read `site/...` directly.  Once apply2.py has run,
# `site/` holds the RE-SEGMENTED files, so re-running preparation feeds the
# output back in as input (it fails loudly -- KeyError on the remap -- rather
# than silently, but it fails).  Every `site/...` literal is now routed through
# `_PRE`, which prefers `<path>.prereseg2` when it exists.  That makes the whole
# chain re-runnable after an apply, which is what a repeatable procedure needs.
HELPER = """

def _PRE(p):
    '''prefer the pre-re-segmentation backup, so preparation can be re-run
    after apply2.py has written into site/'''
    q = p + '.prereseg2'
    return q if os.path.exists(os.path.join(ROOT, q)) else p

"""
import re as _re

for rel in FILES:
    s = open(SRC + '/' + rel, encoding='utf-8').read()
    hits = []
    for a, b in SUBS + EXTRA.get(rel, []):
        n = s.count(a)
        if n:
            s = s.replace(a, b)
            hits.append('%s x%d' % (a.strip()[:44], n))
    assert 'VOL = os.environ' in s, 'VOL not parameterised in ' + rel
    # route every site/ literal through _PRE
    n_pre = 0
    def _wrap(m):
        global n_pre
        n_pre += 1
        return "_PRE(%s)" % m.group(0)
    s2 = _re.sub(r"'site/[^']*' % VOL", _wrap, s)
    m = _re.search(r"^ROOT = .*$", s2, _re.M)
    assert m, 'no ROOT line in ' + rel
    s2 = s2[:m.end()] + HELPER + s2[m.end():]
    print('%-24s _PRE wraps: %d' % ('', n_pre))
    open(DST + '/' + rel, 'w', encoding='utf-8').write(s2)
    print('%-24s %s' % (rel, '; '.join(hits)))
print('generated into _xc/reseg2/{b1,b2,b3}/')
