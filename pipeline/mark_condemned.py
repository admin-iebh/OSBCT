# -*- coding: utf-8 -*-
"""Mark the ordinal-condemned links, at BUILD TIME, on the record they dim.

`claude/decision_dim_the_condemned_links.md` (reader, 2026-08-03): links that
fail an independent check are DIMMED AND GIVEN A REASON, never suppressed.  They
still resolve.  This writes the reason; the reader draws it.

WHY THE FLAG RIDES ON THE LINK ENTRY, and not in a map of its own.  That doc's
third open question warns of the band lesson of `6f46b067`: a check that needs a
SECOND map loaded can return null on a cold cache and silently keep the undimmed
state -- which fails in the one direction that matters, showing a condemned link
as though nothing were wrong.  A separate `linkdim/` artefact has exactly that
failure mode.  Riding on the entry cannot: if the link is drawn, its verdict is
in hand.

WHY IT REUSES check_ordinal RATHER THAN RESTATING IT.  The 320 are whatever that
gate says they are.  A second implementation of "condemned" would drift from the
gate, and then the number the reader is shown and the number the ratchet defends
would be different numbers.  `stem`, `P`, `O`, `name_at`, `sn` are imported.

IDEMPOTENT.  Existing `dim` keys are dropped and recomputed, so a re-run after a
link rebuild is the same operation, and `--verify` asserts that stripping `dim`
returns the file byte-identical to git HEAD -- the reproducibility control this
project learned to want the hard way (`_xc/hy2/FINDINGS.md` 11.3).

============================================================================
THE SECOND FAMILY: CONCORDANCE.  Added 2026-08-07.
============================================================================

`pipeline/check_concordance.py` asserts that a cross-layer link stays inside the
volumes `site/concordance.json` pairs with its canon volume, and counts 3,163
targets that do not.  It moves nothing and it is a ratchet, not a repair; this
carries its verdict onto the link the same way the ordinal one is carried, so
the reader sees it.  Same reasoning as above for why the flag rides on the entry.

FOUR THINGS WERE MEASURED FIRST, AND EACH ONE CHANGED THE DESIGN.  Numbers as of
2026-08-07; `--stats` re-derives all four rather than trusting this paragraph.

1.  **3,163 IS NOT THE NUMBER OF BUTTONS.**  It counts link TARGETS in the data.
    The reader draws only `state == 'direct'` entries (`directTargets`, and
    reader2.html:2109 -- "that is not a link"), and only 1,164 of the 3,163 are
    direct.  The other 1,999 are `covered` and are never rendered at all.  Worse,
    `dimOf` reads `r[0].dim` -- the FIRST direct target -- so the count that
    actually reaches a reader's eye is **1,162 buttons**.  Marking is done on all
    1,164 anyway, because the entry is where the verdict belongs and which entry
    is drawn is the reader's business.  But a handoff that says "3,163 links are
    now dimmed" would be wrong by a factor of 2.7, so this file says both numbers.

2.  **THREE LINKS ARE CONDEMNED BY BOTH CHECKS**, and a single `dim` object
    cannot hold two verdicts.  Whichever pass ran second would have overwritten
    the first silently -- losing a real finding and leaving the reader a partial
    reason.  Three is small enough to have gone unnoticed for a long time, which
    is the argument for handling it rather than the argument against.  So: `why`
    carries the PRIMARY verdict and `also` carries the rest, and both are shown.

3.  **CONCORDANCE OUTRANKS ORDINAL WHEN BOTH FIRE**, and the order is not
    arbitrary.  Ordinal says "the right volume, the wrong sutta in it";
    concordance says "the wrong volume".  The second subsumes the first -- if the
    volume is wrong then the sutta inside it was never the question -- so leading
    with ordinal would tell the reader the smaller truth and bury the larger.

4.  **`no_such_layer` IS 0 TODAY** -- there is no link into a layer the
    concordance says does not exist.  The branch is written and counted anyway,
    because it is a different fault (a manufactured target, not a mis-aimed one)
    and it must not silently become an `outside` if it ever appears.  Reported as
    0 rather than omitted, so that a future non-zero is visibly new.

    **And 2 canon volumes are absent from the concordance altogether.**  Those are
    skipped, not condemned: the concordance saying nothing about a volume is not
    the concordance ruling against it, and collapsing the two would manufacture a
    verdict out of a gap.  `check_concordance.py` counts them separately for the
    same reason.

    python3 pipeline/mark_condemned.py            # dry run, counts only
    python3 pipeline/mark_condemned.py --write
    python3 pipeline/mark_condemned.py --verify   # strip-dim == HEAD ?
    python3 pipeline/mark_condemned.py --stats    # re-derive the four numbers above
"""
import os, sys, json, collections, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import check_ordinal as C

LINKS = C.LINKS
WRITE = '--write' in sys.argv
VERIFY = '--verify' in sys.argv
STATS = '--stats' in sys.argv
LAYERS = ('commentary', 'subcommentary')


def concordance_allows():
    """canon volume -> {layer: set(allowed target volumes)}.

    Imported in spirit from check_concordance.py and deliberately NOT
    re-implemented from concordance.json by hand: the volumes condemned here
    must be exactly the volumes that gate counts, or the number the reader is
    shown and the number the ratchet defends become different numbers.  That is
    the same rule that made this file import check_ordinal instead of restating
    it, and it is the mistake that rule exists to prevent.
    """
    import check_concordance as CC
    allowed, _seen = CC.allowed()
    return allowed


def strip_dim(obj):
    """the file as it would be without this script's field"""
    out = {}
    for si, rec in obj.items():
        r = {}
        for layer, ents in rec.items():
            r[layer] = [{k: v for k, v in e.items() if k != 'dim'} for e in ents]
        out[si] = r
    return out


def verify():
    bad = 0
    for f in sorted(os.listdir(LINKS)):
        if not f.endswith('.links.json'):
            continue
        p = os.path.join(LINKS, f)
        rel = os.path.relpath(p, ROOT)
        head = subprocess.run(['git', '-C', ROOT, 'show', 'HEAD:' + rel],
                              capture_output=True)
        if head.returncode:
            continue
        cur = strip_dim(json.load(open(p, encoding='utf-8')))
        was = strip_dim(json.loads(head.stdout.decode('utf-8')))
        if json.dumps(cur, sort_keys=True) != json.dumps(was, sort_keys=True):
            bad += 1
            print('   *** %s differs from HEAD beyond the dim field' % f)
    print('verify: %d files differ beyond `dim`' % bad)
    return bad


def ordinal_verdict(cv, i, a, cn, ent, st):
    """The 320.  Unchanged in substance; lifted out of main() so that the two
    checks read as two checks and neither can quietly acquire the other's
    scope."""
    if a is None:
        return None
    tv, _, tis = (ent.get('key') or '').partition('#')
    if not tis.isdigit():
        return None
    ti = int(tis)
    o = C.O(tv).get(ti)
    if o is None:
        return None               # the target states no ordinal: silent
    st['checked'] += 1
    if o == a:
        return None
    st['ordinal'] += 1
    tps = C.P(tv)
    tn = C.stem(tps[ti].get('sutta')) if ti < len(tps) else ''
    # The section name is a THIRD criterion and it does not always speak.
    # Report which of the three states it is in, never collapse `silent`
    # into `concurs`.
    name = ('concurs' if (cn and tn and cn != tn) else
            'dissents' if (cn and tn) else 'silent')
    st['name_' + name] += 1
    return {'why': 'ordinal', 'says': o, 'expected': a, 'name': name}


def concordance_verdict(cv, layer, ent, allow, st):
    """The 3,163 -- of which 1,164 are `direct` and can reach a reader.

    `kind` is the distinction check_concordance.py draws and it is kept whole
    here.  `outside` is a wrong volume among volumes that exist; `no such
    layer` is a target in a layer the edition says this volume does not have,
    which is a manufactured link rather than a mis-aimed one.  They are not the
    same fault and they must not be shown in the same words.
    """
    tv, _, tis = (ent.get('key') or '').partition('#')
    if not tis.isdigit():
        return None
    perlayer = allow.get(cv)
    if perlayer is None:
        # The concordance says nothing about this canon volume.  Silence is
        # not a verdict.  Counted, never condemned.
        st['skipped: canon volume absent from concordance'] += 1
        return None
    ok = perlayer[layer]
    st['conc_checked'] += 1
    if tv in ok:
        return None
    if not ok:
        st['conc_no_such_layer'] += 1
        return {'why': 'concordance', 'kind': 'no such layer',
                'target': tv, 'layer': layer, 'allowed': []}
    st['conc_outside'] += 1
    return {'why': 'concordance', 'kind': 'outside', 'target': tv,
            'layer': layer, 'allowed': sorted(ok)}


# Concordance first.  A wrong VOLUME subsumes a wrong sutta inside a volume, so
# it is the larger statement and it leads.  See point 3 of the header.
RANK = {'concordance': 0, 'ordinal': 1}


def main():
    if VERIFY:
        sys.exit(1 if verify() else 0)
    allow = concordance_allows()
    st = collections.Counter()
    # Point 1 of the header: what the DATA says versus what a reader can see.
    # `dimOf` in reader2.html reads r[0].dim -- the first direct entry -- so
    # only that one becomes a visible chip.  Counting both, every run, is the
    # only thing that stops "3,163 links are now dimmed" being written down.
    for f in sorted(os.listdir(LINKS)):
        if not f.endswith('.links.json'):
            continue
        cv = f[:-len('.links.json')]
        cps = C.P(cv)
        if not cps:
            continue
        p = os.path.join(LINKS, f)
        links = json.load(open(p, encoding='utf-8'))
        touched = False
        for si, rec in links.items():
            i = int(si)
            if i >= len(cps):
                continue
            a = C.sn(cps[i])
            cn = C.stem(C.name_at(cv, i))
            for layer in LAYERS:
                first_direct = True
                for ent in rec.get(layer) or []:
                    if ent.pop('dim', None) is not None:
                        touched = True
                    if ent.get('state') != 'direct':
                        # Counted, never marked.  This is the 1,999 half of the
                        # 3,163 -- entries the reader never draws (reader2.html
                        # filters to `direct`, and 2109 says why: "that is not
                        # a link").  Tallying them here is what lets --stats
                        # re-derive point 1 of the header instead of quoting it.
                        st['not drawn (state != direct)'] += 1
                        if concordance_verdict(cv, layer, ent, allow,
                                               collections.Counter()):
                            st['violations among entries never drawn'] += 1
                        continue
                    vs = [v for v in (
                        concordance_verdict(cv, layer, ent, allow, st),
                        ordinal_verdict(cv, i, a, cn, ent, st),
                    ) if v]
                    if first_direct:
                        st['buttons'] += 1
                        first_direct = False
                        if vs:
                            st['BUTTONS dimmed'] += 1
                            st['buttons dimmed: ' + vs[0]['why']] += 1
                    if not vs:
                        continue
                    st['links dimmed'] += 1
                    if len(vs) > 1:
                        st['BOTH checks fired'] += 1
                    vs.sort(key=lambda v: RANK[v['why']])
                    d = dict(vs[0])
                    # Nothing is dropped.  A second verdict rides in `also`
                    # rather than overwriting the first -- three links have one
                    # today, and a silent overwrite of three findings is
                    # exactly the size of defect that survives for months.
                    if len(vs) > 1:
                        d['also'] = vs[1:]
                    ent['dim'] = d
                    touched = True
        if touched and WRITE:
            json.dump(links, open(p, 'w', encoding='utf-8'), ensure_ascii=False)

    print('%s' % ('WROTE' if WRITE else 'DRY RUN'))
    print('  ordinal      checked %6d   condemned %5d   (name concurs %d, dissents %d, silent %d)'
          % (st['checked'], st['ordinal'], st['name_concurs'],
             st['name_dissents'], st['name_silent']))
    print('  concordance  checked %6d   condemned %5d   (outside %d, no such layer %d)'
          % (st['conc_checked'], st['conc_outside'] + st['conc_no_such_layer'],
             st['conc_outside'], st['conc_no_such_layer']))
    print('  both fired on %d link(s)' % st['BOTH checks fired'])
    print('')
    print('  LINKS marked dim          %6d  of %d direct entries'
          % (st['links dimmed'], st['conc_checked']))
    print('  BUTTONS a reader can see  %6d  of %d   (concordance %d, ordinal %d)'
          % (st['BUTTONS dimmed'], st['buttons'],
             st['buttons dimmed: concordance'], st['buttons dimmed: ordinal']))
    print('  entries never drawn       %6d  (state != direct)' % st['not drawn (state != direct)'])
    print('  skipped, no concordance   %6d  (silence is not a verdict)'
          % st['skipped: canon volume absent from concordance'])
    if STATS:
        direct_v = st['conc_outside'] + st['conc_no_such_layer']
        allv = direct_v + st['violations among entries never drawn']
        cb = st['buttons dimmed: concordance']
        print('')
        print('  ---- the header re-derived, so it is never merely quoted ----')
        print('  1. concordance violations, ALL entries      %6d   <- "the 3,163"' % allv)
        print('       of which never drawn (not `direct`)    %6d'
              % st['violations among entries never drawn'])
        print('       of which direct, and so marked         %6d' % direct_v)
        print('       of which a reader can SEE as a chip    %6d   <- overstated %.1fx by the headline'
              % (cb, allv / max(1, cb)))
        print('  2. links carrying `also` (both checks)      %6d' % st['BOTH checks fired'])
        print('  3. precedence when both fire: %s' % ', '.join(
            k for k, _ in sorted(RANK.items(), key=lambda kv: kv[1])))
        print('  4. no_such_layer                            %6d' % st['conc_no_such_layer'])
        print('     canon volumes absent from concordance, entries skipped %d'
              % st['skipped: canon volume absent from concordance'])


main()
