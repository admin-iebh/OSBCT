# -*- coding: utf-8 -*-
"""BLOCKER 2 -- `verse/` substitutes for the body, so it needs a mapping and a
proof of its own, not a remap.  See b2_findings.md for the prose.

WHAT IT IS KEYED TO (measured):
  71 entries.  The 67 that carry a `groups` key are EXACTLY the 67 numbered
  corpus paragraphs -- `pair_ords` in build_khu_volume.py's kathā path, which
  pair 1:1 with the printed NUMBERED UNITS.  So the key is the printed UNIT,
  and under re-segmentation a unit is a RUN.
  reader2.html:1474 substitutes only when `vmap.groups` exists, so the other 4
  entries never render at all -- and all four hold printed gāthā the corpus
  does not contain.  Four restored verses are in the map and off the page.

WHAT THE ENTRIES HOLD, against the RE-SEGMENTED corpus letters:
  before prose 25 (all in corpus) | after prose 378 (all in corpus)
  after gāthā 65 (all in corpus)  | after gāthā 6 (ABSENT -- restored verse)

THE MAPPING: every block is located in the PRINTED LINE STREAM with a monotone
cursor and assigned to the new paragraph whose printed extent contains it.  The
old->new ordinal remap is never consulted.
"""
import json, os, re, sys, bisect, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import pline, locate

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
VOL = '20KhuA01'
CTL = '--control' in sys.argv
L = locate.letters
LEADNUM = re.compile(r'^\s*\d{1,4}(?:-\d+)?\.\s*')


def J(p):
    return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))


ship = J('site/%s.json' % VOL)['paragraphs']
reseg = J('_xc/reseg/%s.json' % VOL)['paragraphs']
verse = J('site/reader/verse/%s.json' % VOL)
PG = locate.Page(pline.stream(VOL))
NA = json.load(open(os.path.join(os.path.dirname(HERE), 'b3',
                                 'anchors_%s.json' % VOL), encoding='utf-8'))['reseg']
STARTS = [a[2] for a in NA]


def nletters(s):
    return L(LEADNUM.sub('', s or ''))


def btxt(b, role):
    if role == 'groups':
        return ' '.join(b), 'group'
    if isinstance(b, str):
        return b, 'prose'
    if isinstance(b, dict) and 'gatha' in b:
        return ' '.join(b['gatha']), 'gatha'
    if isinstance(b, dict) and 't' in b:
        return b['t'], 'unit'
    return json.dumps(b, ensure_ascii=False), 'other'


def owner(off):
    j = bisect.bisect_right(STARTS, off) - 1
    if 0 <= j < len(NA) and NA[j][2] <= off < NA[j][3]:
        return j
    return None


def following(off):
    j = bisect.bisect_left(STARTS, off)
    return j if j < len(NA) else None


def preceding(off):
    j = bisect.bisect_right(STARTS, off) - 1
    return j if j >= 0 else None


# ---- 1. locate every block on the printed page, in printed order -----------
def locate_blocks(shift=0, scramble=False, corrupt=0):
    items = []
    cur = NA[0][2]
    n = 0
    for k in sorted(verse, key=int):
        v = verse[k]
        seq = [(r, i, b) for r in ('before', 'groups', 'after')
               for i, b in enumerate(v.get(r) or [])]
        if scramble:
            seq = seq[::-1]
        for role, bi, b in seq:
            n += 1
            t, kind = btxt(b, role)
            s = L(t)
            it = {'old': int(k), 'role': role, 'bi': bi, 'b': b, 'kind': kind}
            if corrupt and n == corrupt:
                # corrupt what will be RENDERED, not what is searched for: the
                # block still locates correctly, so only the semantic check can
                # catch it.  (The first version of this control corrupted the
                # search key instead; the block then simply failed to locate,
                # was dropped, and the paragraph rendered its own corpus text --
                # so the control passed on corrupted input.  It is the second
                # control this investigation has caught being a no-op.)
                it['b'] = (b[:-4] + 'ZZQQ') if isinstance(b, str) else dict(
                    b, gatha=[(b['gatha'][0][:-4] + 'ZZQQ')] + list(b['gatha'][1:]))
            i = PG.text.find(s, cur) if s else -1
            if i < 0:
                it['span'] = None
                it['at'] = cur
            else:
                cur = i + len(s)
                it['span'] = [i + shift, i + len(s) + shift]
            items.append(it)
    return items


def assign(items):
    straddle = []
    unowned = []
    for it in items:
        sp = it['span']
        if sp is None:
            it['own'] = None
            it['unlocated'] = True
            unowned.append(it)
            continue
        a, b = owner(sp[0]), owner(sp[1] - 1)
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
            straddle.append(it)
    return straddle, unowned




REMAP = J('_xc/reseg/ord_remap_%s.json' % VOL)
RUNS = {}
for _o in range(len(ship)):
    _a = REMAP[str(_o)]
    _b = REMAP[str(_o + 1)] if str(_o + 1) in REMAP else len(reseg)
    RUNS[_o] = list(range(_a, _b))


def build(_opt=None, anchor='design', udd_anchor='last', merge=True,
          leak_hide=True, write=False, quiet=False):
    """anchor='monotonic' is THE control the doc asked for: the naive
    old-ordinal -> first-of-run remap of the shipped verse map."""
    _opt = dict(_opt or {})
    P = (lambda *a, **k: None) if quiet else print
    items = locate_blocks(**_opt)
    straddle, unowned = assign(items)
    P('=== 1. LOCATE (evidence = the printed line stream, not the remap) ===')
    P('   blocks %d   located %d   restored-verse (no corpus paragraph) %d   '
          'unlocatable %d   straddling a new-paragraph boundary %d'
          % (len(items), sum(1 for i in items if i['span']),
             sum(1 for i in items if i.get('restored')),
             sum(1 for i in items if i.get('unlocated')), len(straddle)))
    for s in straddle:
        P('      STRADDLE old%-4s %-6s ords %s..%s  %r'
              % (s['old'], s['kind'], s['own'], s['own_end'],
                 btxt(s['b'], s['role'])[0][:52]))
    for u in unowned:
        P('      RESTORED old%-4s -> before ord %s  %r'
              % (u['old'], u.get('own'), btxt(u['b'], u['role'])[0][:52]))

    # ---- 2. merge only where a block straddles --------------------------------
    parent = list(range(len(reseg)))


    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x


    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)


    if merge:
        for s in straddle:
            for j in range(s['own'], s['own_end'] + 1):
                union(s['own'], j)
    groups = collections.defaultdict(list)
    for i in range(len(reseg)):
        groups[find(i)].append(i)
    merged = {g: v for g, v in groups.items() if len(v) > 1}
    if sum(1 for i in items if i.get('unlocated')):
        P('   REFUSING: %d block(s) could not be located on the printed page'
          % sum(1 for i in items if i.get('unlocated')))
        return False, None
    P('=== 2. MERGE (a boundary a printed block crosses is not a boundary) ===')
    P('   merged groups %d   paragraphs absorbed %d   %s'
          % (len(merged), sum(len(v) - 1 for v in merged.values()),
             {g: v for g, v in list(merged.items())[:12]}))

    # ---- 3. build the new map --------------------------------------------------
    # RESTORE=0 reproduces the SHIPPED page exactly: the 4 restored gāthā that
    # reader2.html:1474 silently drops (their entries carry no `groups` key) are
    # dropped here too, so the equivalence check in step 5 is an equality and not
    # an equality-plus-an-excuse.  RESTORE=1 puts them back, through `sections/`
    # with k:'gatha' -- the path reader2.html:1735 already has for "display verse
    # the page prints above a paragraph and the corpus does not hold at all".
    RESTORE = os.environ.get('RESTORE', '0') == '1'

    byg = collections.defaultdict(list)
    sec_add = collections.defaultdict(list)
    orphan_restored = []
    for it in items:
        if it['own'] is None:
            continue
        byg[find(it['own'])].append(it)

    new_verse = {}
    absorb = sorted(j for v in merged.values() for j in v[1:])
    kept = dropped = 0
    for g, bs in sorted(byg.items()):
        grp = groups[g]
        a0 = NA[grp[0]][2]
        bs = sorted(bs, key=lambda x: (x['span'][0] if x['span'] else a0))
        corpus_bs = [b for b in bs if not b.get('restored')]
        if not corpus_bs:
            # nothing here but restored verse: substituting would BLANK the body
            orphan_restored.extend(bs)
            if RESTORE:
                for b in bs:
                    t = btxt(b['b'], b['role'])[0]
                    lines = b['b']['gatha'] if isinstance(b['b'], dict) and 'gatha' in b['b'] else [t]
                    sec_add[str(grp[0])].append({'l': '\n'.join(lines), 'k': 'gatha'})
            continue
        if not RESTORE:
            bs = corpus_bs
        # DROP AN ENTRY ONLY WHEN IT IS PROVABLY REDUNDANT.  An entry may be
        # dropped exactly when its blocks say, letter for letter, what the corpus
        # paragraphs already say -- then the paragraph can render itself.  Any
        # other case (a gāthā whose line breaks the corpus lost, an uddāna line the
        # corpus holds but `uddana/` draws, a line the corpus dropped) means the
        # print and the corpus differ over this extent and the print must be kept.
        got = ''.join(nletters(btxt(b['b'], b['role'])[0]) for b in bs)
        want = ''.join(nletters(reseg[j]['text']) for j in grp)
        if got == want and not any(b['kind'] in ('gatha', 'group') for b in bs):
            dropped += 1
            continue
        kept += 1
        before = [b for b in bs if b['span'] and b['span'][1] <= a0]
        after = [b for b in bs if b not in before]
        e = {'groups': []}
        if before:
            e['before'] = [b['b'] for b in before]
        e['after'] = [b['b'] for b in after]
        new_verse[str(g)] = e
    P('=== 3. NEW MAP  (RESTORE=%d) ===' % RESTORE)
    P('   groups holding blocks %d -> entries kept (they carry gāthā) %d   '
          'entries dropped (prose only, the corpus carries it) %d'
          % (len(byg), kept, dropped))
    P('   restored gāthā with NO corpus block beside them: %d  -> %s'
          % (len(orphan_restored),
             'emitted as sections k:gatha' if RESTORE else 'dropped, as the shipped reader drops them'))
    P('   paragraphs to be ADDED to hide/ because a merge absorbed them: %d %s'
          % (len(absorb), absorb))

    # ---- 3b. uddana/ claims printed lines the corpus ALSO holds ---------------
    # 9 of 33 uddāna blocks are not "recovered from print" at all: their line is in
    # the corpus.  Today that is invisible, because the containing paragraph is a
    # numbered unit whose body comes from the printed stream and the kathā reader
    # routed the line into `uddana/` instead of into an `after` block.  After
    # re-segmentation the containing paragraph renders itself, so the line would be
    # drawn TWICE.  Where the block IS the whole new paragraph the paragraph is
    # hidden (uddana/ draws it, in its own printed presentation); where it is only
    # the tail of a longer paragraph the verse entry is kept and its blocks, which
    # do not contain the line, substitute for the body -- which is exactly what the
    # rule in step 3 already decides.
    UDD = J('site/reader/uddana/%s.json' % VOL)
    udd_hide = []
    udd_tail = []
    _cur = NA[0][2]
    for _k in sorted(UDD, key=int):
        for _b in UDD[_k]:
            _lines = (([_b['label']] if _b.get('label') else [])
                      + ([_b['head']] if _b.get('head') else [])
                      + list(_b.get('lines') or []))
            _t = L(''.join(_lines))
            _i = PG.text.find(_t, _cur)
            if _i < 0:
                _i = PG.text.find(_t)
            else:
                _cur = _i + len(_t)
            if _i < 0:
                continue
            _j = owner(_i)
            if _j is None:
                continue
            if L(reseg[_j]['text']) == _t:
                udd_hide.append(_j)
            else:
                udd_tail.append((_j, _t))
    if anchor == 'monotonic':
        new_verse = {str(RUNS[int(k)][0]): v for k, v in verse.items()}
    P('=== 3b. uddana/ blocks whose text the CORPUS also holds ===')
    P('   blocks recovered from print (a gap between paragraphs): %d'
          % (sum(len(v) for v in UDD.values()) - len(udd_hide) - len(udd_tail)))
    P('   blocks that ARE a whole new paragraph -> that paragraph joins hide/: %d %s'
          % (len(udd_hide), udd_hide))
    P('   blocks that are the TAIL of a longer new paragraph -> the verse entry '
          'is kept and substitutes without them: %d %s'
          % (len(udd_tail), [x[0] for x in udd_tail]))

    # ---- 3c. LEAKED HEADINGS ---------------------------------------------------
    # `extract.py` does not always recognise a printed heading, so the heading line
    # survives as body text -- `build_khu_volume.py` calls these "leaked corpus
    # headings" and hides them (`hide[str(o)] = 1`; ord19 of the shipped hide/ is
    # one).  In the 109-paragraph corpus a leaked heading was buried inside a lump
    # whose body came from the printed stream, so it never showed.  Re-segmentation
    # gives it a paragraph of its own and it would be drawn as body text under the
    # very heading `sections/` draws from the same line.  Found by the equivalence
    # check at +22 letters: `Khantī cāti gāthāvaṇṇanā`, new ord376.
    SEC0 = J('site/reader/sections/%s.json' % VOL)
    # Read from the PARAGRAPH side, not with a forward cursor over the heading
    # list: a heading may be printed inside a paragraph's extent, and a cursor
    # walking the headings in ordinal order steps over exactly those.  For each
    # new paragraph, does its text END with a printed heading?
    _HL = {}
    for _k in SEC0:
        for _h in SEC0[_k]:
            if _h.get('k') != 'gatha':
                _HL[L(_h['l'])] = _h['l']
    sec_hide = []
    sec_tail = []
    for _j, _p in enumerate(reseg):
        _pt = L(_p.get('text'))
        if _pt in _HL:
            sec_hide.append(_j)
            continue
        for _t in _HL:
            if len(_t) > 8 and _pt.endswith(_t):
                sec_tail.append((_j, _t))
                break
    P('=== 3c. printed headings that re-segmentation turned into paragraphs ===')
    P('   leaked headings that ARE a whole new paragraph -> join hide/: %d %s'
      % (len(sec_hide), sec_hide))
    P('   leaked headings absorbed INSIDE a longer new paragraph -> the verse '
      'entry keeps substituting without them: %d %s'
      % (len(sec_tail), [x[0] for x in sec_tail]))

    # ---- 4. SEMANTIC PROOF ----------------------------------------------------
    # An entry substitutes for the body, so over its own printed extent its blocks
    # must say what the PAGE says -- not what the corpus says, because a block may
    # legitimately carry a line the corpus dropped.  The page is the authority and
    # is also the evidence source that the assignment did not use for this test.
    P('=== 4. SEMANTIC CHECK -- the entry must reproduce the PAGE over its own '
          'extent ===')
    exact = bad = 0
    badl = []
    for g in sorted(new_verse, key=int):
        gi = int(g)
        grp = groups[gi]
        bs = (new_verse[g].get('before') or []) + (new_verse[g].get('after') or [])
        got = ''.join(nletters(btxt(b, 'after')[0]) for b in bs)
        lo = min(NA[j][2] for j in grp)
        hi = max(NA[j][3] for j in grp)
        want = nletters(PG.text[lo:hi]) if False else L(PG.text[lo:hi])
        got2 = ''.join(L(btxt(b, 'after')[0]) for b in bs)
        # the printed extent starts at the paragraph's first letter, which for a
        # numbered unit is the unit NUMBER; the block has it stripped, so compare
        # with the leading number removed from the printed side too
        want = LEADNUM.sub('', reseg[grp[0]]['text'])[:0] and want or want
        wnum = L(reseg[grp[0]]['text']) [:len(L(reseg[grp[0]]['text'])) - len(nletters(reseg[grp[0]]['text']))]
        if want.startswith(wnum) and wnum:
            want = want[len(wnum):]
        for _o, _t in udd_tail + sec_tail:
            if _o in grp and _t in want:
                want = want.replace(_t, '', 1)
        if got2 == want:
            exact += 1
        else:
            bad += 1
            if len(badl) < 10:
                badl.append((gi, len(got2), len(want)))
    P('   entries whose blocks reproduce the printed page over their extent '
          'EXACTLY: %d   not exactly: %d' % (exact, bad))
    for b in badl:
        P('      ord %-4d block-letters %5d vs printed-extent letters %5d' % b)

    # ---- 5. RENDERED-LETTER EQUIVALENCE ---------------------------------------
    def render(paras, vmap, udd, sec, hide, inc, btl):
        """The letters reader2.html would put on the page, in order.
        Mirrors reader2.html:1735-1845 (front matter, sections, block, uddana),
        1472-1550 (the verse branch, incl. `vmap.groups` gating) and 1220-1245."""
        out = []
        for i, p in enumerate(paras):
            if hide.get(str(i)):
                continue
            for s in (btl.get(str(i)) or []):
                out.append(nletters(s))
            if inc.get(str(i)):
                out.append(nletters(inc[str(i)]))
            for h in (sec.get(str(i)) or []):
                out.append(nletters(h['l']))
            v = vmap.get(str(i))
            if v is not None and 'groups' in v:
                for b in (v.get('before') or []):
                    out.append(nletters(btxt(b, 'before')[0]))
                for gp in (v.get('groups') or []):
                    out.append(nletters(' '.join(gp)))
                for b in (v.get('after') or []):
                    out.append(nletters(btxt(b, 'after')[0]))
            else:
                out.append(nletters(p.get('text')))
            for blk in (udd.get(str(i)) or []):
                if blk.get('head'):
                    out.append(nletters(blk['head']))
                if blk.get('label'):
                    out.append(nletters(blk['label']))
                out.append(nletters(' '.join(blk.get('lines') or [])))
        return ''.join(out)


    B3 = os.path.join(os.path.dirname(HERE), 'b3')
    old_render = render(ship, verse,
                        J('site/reader/uddana/%s.json' % VOL),
                        J('site/reader/sections/%s.json' % VOL),
                        J('site/reader/hide/%s.json' % VOL),
                        J('site/reader/incipit/%s.json' % VOL),
                        J('site/reader/booktitle/%s.json' % VOL))
    new_hide = json.load(open(os.path.join(B3, 'hide_%s.json' % VOL), encoding='utf-8'))
    for j in absorb:
        new_hide[str(j)] = 1
    if leak_hide:
        for j in udd_hide:
            new_hide[str(j)] = 1
        for j in sec_hide:
            new_hide[str(j)] = 1
    new_sec_raw = json.load(open(os.path.join(B3, 'sections_%s.json' % VOL), encoding='utf-8'))
    new_sec = {}
    for _k in sorted(new_sec_raw, key=int):
        _t = int(_k)
        while _t < len(reseg) - 1 and new_hide.get(str(_t)):
            _t += 1
        new_sec[str(_t)] = list(new_sec.get(str(_t), [])) + new_sec_raw[_k]
    # AN UDDĀNA ANCHORED ON A HIDDEN PARAGRAPH IS NEVER DRAWN.  reader2.html:1845
    # skips the whole paragraph, `udd(i)` included, so the anchor has to step back
    # to the last VISIBLE ordinal of the run.  Found by the equivalence check, at
    # -31 letters -- the one uddāna whose own paragraph had just been hidden.
    UDD0 = J('site/reader/uddana/%s.json' % VOL)
    new_udd_raw = (json.load(open(os.path.join(B3, 'uddana_%s.json' % VOL), encoding='utf-8'))
                   if udd_anchor == 'last'
                   else {str(RUNS[int(k)][0]): v for k, v in UDD0.items()})
    new_udd = {}
    for _k in sorted(new_udd_raw, key=int):
        _t = int(_k)
        while _t > 0 and new_hide.get(str(_t)):
            _t -= 1
        new_udd[str(_t)] = list(new_udd.get(str(_t), [])) + new_udd_raw[_k]
    P('   uddana anchors stepped back off a hidden paragraph: %d'
          % sum(1 for k in new_udd_raw if k not in new_udd))
    for k, v in sec_add.items():
        new_sec[k] = list(new_sec.get(k, [])) + v
    new_render = render(reseg, new_verse,
                        new_udd, new_sec, new_hide,
                        json.load(open(os.path.join(B3, 'incipit_%s.json' % VOL), encoding='utf-8')),
                        json.load(open(os.path.join(B3, 'booktitle_%s.json' % VOL), encoding='utf-8')))
    P('=== 5. RENDERED-LETTER EQUIVALENCE (blanking, doubling and misordering '
          'in one number) ===')
    same = old_render == new_render
    P('   shipped render %d letters / new render %d letters / delta %+d / identical=%s'
          % (len(old_render), len(new_render), len(new_render) - len(old_render), same))
    if not same:
        i = next((i for i in range(min(len(old_render), len(new_render)))
                  if old_render[i] != new_render[i]), min(len(old_render), len(new_render)))
        P('   first divergence at %d:\n      old %r\n      new %r'
              % (i, old_render[i:i + 90], new_render[i:i + 90]))

    if write:
        for _n, _d in (('hide', new_hide), ('uddana', new_udd), ('sections', new_sec)):
            json.dump(_d, open(os.path.join(HERE, 'final_%s_%s.json' % (_n, VOL)), 'w',
                               encoding='utf-8'), ensure_ascii=False)
        json.dump(new_verse, open(os.path.join(HERE, 'verse_%s.json' % VOL), 'w',
                                  encoding='utf-8'), ensure_ascii=False)
        json.dump({'absorbed_by_merge': absorb}, open(
            os.path.join(HERE, 'hide_additions_%s.json' % VOL), 'w',
            encoding='utf-8'), ensure_ascii=False)
        P('wrote verse_%s.json and hide_additions_%s.json' % (VOL, VOL))

    return same, len(new_render) - len(old_render)


if __name__ == '__main__':
    if not CTL:
        build(write=True)
    else:
        base, _ = build(quiet=True)
        print('design run: rendered-letter equivalence =', base)
        print()
        print('=== NEGATIVE CONTROLS -- each MUST break the equivalence ===')
        ctl = [
            ('every located span pushed 1 letter',      dict(_opt={'shift': 1})),
            ('block order reversed inside each entry',  dict(_opt={'scramble': True})),
            ('one block\'s RENDERED text corrupted (#200)', dict(_opt={'corrupt': 200})),
            ('one block\'s RENDERED text corrupted (#40)',  dict(_opt={'corrupt': 40})),
            ('MONOTONIC remap (old ord -> first of run)', dict(anchor='monotonic')),
            ('uddana anchored FIRST of run',            dict(udd_anchor='first')),
            ('straddle merge disabled',                 dict(merge=False)),
            ('leaked-heading / uddana hide disabled',   dict(leak_hide=True and False)),
        ]
        fired = 0
        for label, kw in ctl:
            try:
                same, delta = build(quiet=True, **kw)
            except Exception as e:
                same, delta = False, 'exception: %s' % e
            print('   %-44s equivalence=%-5s delta=%s  -> fired=%s'
                  % (label, same, delta, not same))
            fired += (not same)
        print('CONTROLS THAT FIRED: %d of %d' % (fired, len(ctl)))
