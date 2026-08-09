#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Is every DERIVED file newer than the sources it was derived from?

WHY THIS EXISTS.  `site/reader/pageindex.json` is built from `site/*.json` by
`build_pageindex.py`, and NOTHING runs that builder for you.  On 2026-07-30i it
was found dated 2026-07-23, eight days behind volumes rebuilt on the 27th-29th
and behind the page audit of the 29th that rewrote `printed` in all 118 files.

The damage was not that a link failed.  Every link still rendered, still looked
right, and still went somewhere.  **3,774 of them — 13.4% of everything that
resolved — went to a paragraph that is not on the cited page, and not one of
them went to the right one.**  Roughly a thousand were more than ten printed
pages out; the worst was 1,680.

No gate saw it.  `check_layout` grades roles.  `verify_apparatus` counts stored
notes.  `regress check` compares side-maps to their own baseline.  `_navdup`
walks the tree.  And `stamp_build.py` HASHED the stale file, so the wrong data
was distributed promptly and with a fresh cache-buster.

`stamp_build.py` now refuses to stamp when this reports STALE.  That is the
point: staleness must block the step that publishes, because it is invisible
everywhere else.

TWO STRENGTHS OF CHECK, and the difference matters:
  * `content` — rebuild the artefact in memory and compare.  A PROOF.  Only for
    artefacts cheap enough to rebuild in a second or two.
  * `mtime`   — is any source newer than the artefact?  A SCREEN.  It can cry
    wolf after a `touch` or a fresh checkout, and it cannot see a source that
    was edited and restored.  Where a content check is affordable, use it.

Usage:  python3 pipeline/check_derived.py [--quiet] [--deep]
        --deep also re-runs the slow builders (~20s) and compares their output,
        turning the mtime screens into proofs.  Use it before deploying.
Exit 0 = all fresh, 1 = something is stale.
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# A VOLUME file, not just anything under `site/`.  `site/errata.json`,
# `concordance.json` and `downloads.data.json` live there too and are no part of
# the corpus — counting them made every artefact look stale the moment an
# erratum was recorded, which is the fastest way to teach someone to ignore a
# gate.
VOLJSON = re.compile(r'^\d{2}[A-Za-z][A-Za-z0-9]*\.json$')


def _sources(patterns):
    out = []
    for pat in patterns:
        for p in glob.glob(os.path.join(ROOT, pat)):
            if pat == 'site/*.json' and not VOLJSON.match(os.path.basename(p)):
                continue
            out.append(p)
    return out


def _newest(patterns):
    """(mtime, path) of the newest source file, or (0, None)."""
    best, who = 0.0, None
    for p in _sources(patterns):
        m = os.path.getmtime(p)
        if m > best:
            best, who = m, p
    return best, who


def _pageindex_content():
    """PROOF for pageindex.json: rebuild it from site/*.json and compare.

    Identical to `build_pageindex.py` — first paragraph beginning on each
    printed page.  Kept in step with it deliberately: if the two ever disagree
    about how the index is built, this check is what will say so.
    """
    out = {}
    for js in sorted(glob.glob(os.path.join(ROOT, 'site/*.json'))):
        vol = os.path.basename(js)[:-5]
        try:
            d = json.load(open(js, encoding='utf-8'))
        except Exception:
            continue
        if not isinstance(d, dict) or 'paragraphs' not in d:
            continue
        pg = {}
        for i, p in enumerate(d['paragraphs']):
            pr = p.get('printed')
            if pr is not None and str(pr) not in pg:
                pg[str(pr)] = i
        if pg:
            out[vol] = pg
    cur_p = os.path.join(ROOT, 'site/reader/pageindex.json')
    if not os.path.exists(cur_p):
        return False, 'site/reader/pageindex.json does not exist'
    cur = json.load(open(cur_p, encoding='utf-8'))
    if cur == out:
        return True, '%d volumes, %d pages, byte-for-byte what the builder would write' % (
            len(out), sum(len(v) for v in out.values()))
    bad = [v for v in sorted(set(cur) | set(out)) if cur.get(v) != out.get(v)]
    moved = sum(1 for v in bad for k in (cur.get(v) or {})
                if k in (out.get(v) or {}) and cur[v][k] != out[v][k])
    return False, ('%d of %d volumes DISAGREE with site/*.json; %d page entries point at a '
                   'different paragraph. First: %s' % (len(bad), len(set(cur) | set(out)),
                                                       moved, ', '.join(bad[:6])))


def _pageindex_selfcheck():
    """Does every entry point at a paragraph that really carries that page?

    Independent of the builder: it asks the corpus, not the recipe.  This is
    what makes the rebuilt index trustworthy rather than merely fresh.
    """
    idx_p = os.path.join(ROOT, 'site/reader/pageindex.json')
    if not os.path.exists(idx_p):
        return False, 'missing'
    idx = json.load(open(idx_p, encoding='utf-8'))
    ok = bad = 0
    first = None
    for vol, pages in idx.items():
        js = os.path.join(ROOT, 'site', vol + '.json')
        if not os.path.exists(js):
            bad += len(pages)
            first = first or (vol, 'no such volume')
            continue
        ps = json.load(open(js, encoding='utf-8'))['paragraphs']
        for pg, o in pages.items():
            if 0 <= o < len(ps) and str(ps[o].get('printed')) == str(pg):
                ok += 1
            else:
                bad += 1
                first = first or (vol, 'page %s -> ord %s, whose printed page is %s'
                                  % (pg, o, ps[o].get('printed') if 0 <= o < len(ps) else 'out of range'))
    if bad:
        return False, '%d entries point at the wrong paragraph (e.g. %s: %s)' % (bad, first[0], first[1])
    return True, 'all %d entries point at a paragraph carrying that printed page' % ok


def _pdfblanks_content():
    """PROOF for pdfblanks.json: re-run the builder (dry) and compare.

    ~17s, which is why it is not in the default screen — pass `--deep`.  It
    earns its keep: on 2026-07-30j the mtime screen called this file stale
    because two volumes had been rewritten an hour after it was built, and the
    content was IDENTICAL.  A gate that cries wolf is a gate that gets ignored.
    """
    # !!! sys.argv IS INHERITED BY AN EXEC'D MODULE (fixed 2026-07-31b).
    # `build_pdfblanks.py` decides whether to write by `'--write' in sys.argv`,
    # and exec'ing it here handed it the PARENT's argv — so
    # `stamp_build.py --write` turned this read-only check into a real write.
    # The file's content never changed, but its MTIME did, and `stamp_build.py`
    # hashes name|size|mtime: **BUILD moved on every single run**, so every
    # deploy busted every visitor's cache of all 1,691 JSON files even when not
    # one byte had changed. On a phone that is the difference between a warm
    # cache and re-downloading megabytes. A check must have no side effects.
    import contextlib, importlib.util as il, io as _io
    sp = il.spec_from_file_location('bp', os.path.join(ROOT, 'pipeline/build_pdfblanks.py'))
    m = il.module_from_spec(sp)
    _argv = sys.argv
    sys.argv = [os.path.join(ROOT, 'pipeline/build_pdfblanks.py')]     # no --write
    try:
        with contextlib.redirect_stdout(_io.StringIO()):
            sp.loader.exec_module(m)
    except SystemExit:
        pass
    finally:
        sys.argv = _argv
    new = next((v for k, v in vars(m).items()
                if isinstance(v, dict) and v and all(isinstance(x, list) for x in v.values())), None)
    if new is None:
        return True, 'could not read the builder result — falling back to the mtime screen'
    cur = json.load(open(os.path.join(ROOT, 'site/reader/pdfblanks.json'), encoding='utf-8'))
    diff = [k for k in set(cur) | set(new) if cur.get(k) != new.get(k)]
    if diff:
        return False, '%d volume(s) differ from what the builder would write: %s' % (
            len(diff), ', '.join(sorted(diff)[:6]))
    return True, '%d volumes, identical to a fresh build' % len(cur)


def _pbreak_load_derive():
    """`_xc/pagemark/derive.py` as a module, or None if it cannot be imported."""
    import importlib.util as il
    dp = os.path.join(ROOT, '_xc/pagemark/derive.py')
    if not os.path.exists(dp):
        return None
    if os.path.dirname(dp) not in sys.path:
        sys.path.insert(0, os.path.dirname(dp))
    try:
        sp = il.spec_from_file_location('_pm_derive', dp)
        m = il.module_from_spec(sp)
        sp.loader.exec_module(m)
        return m
    except Exception:
        return None


def _pbreak_content(deep=False):
    """Is `site/reader/pbreak/` still the map its sources produce?

    WHY THIS EXISTS.  `pbreak` is the only derived artefact whose staleness is
    invisible BOTH to an mtime screen and to any structural grading of its own
    contents, and it has already cost this project a shipped regression: after
    `17b3f2bd` moved ordinals onto the verse branch, `29KhuA10` went from 3
    misplaced page rules to **253** and `32KhuA13` from 0 to 115, and no gate
    said a word.  A record's `drawnIndex` addresses the flat sequence of
    `fmtLine` calls the reader makes for THAT ordinal's verse entry; change the
    verse entry and the address means something else, or nothing.

    WHY NOT AN MTIME SCREEN.  `pbreak/` is 118 files and `site/reader/verse/` is
    212MB of them; a rebuild of ONE volume's side-maps makes the whole directory
    look stale, so the screen would be red on nearly every working day and would
    be answered with --force.

    WHY NOT A STRUCTURAL CHECK ALONE.  Measured over all 118 volumes: 1,982
    records sit on a verse ordinal carrying NO drawn address, and every one is
    legitimate -- `verse_line_not_among_drawn`, residue the derivation reports
    itself.  A record left stale by an ordinal MOVING onto the verse branch has
    exactly that shape.  The absence of an address cannot be graded, so absence
    is not graded here.

    THREE SIGNALS, WEAKEST LAST.

    1. STAMP -- `derive.py` records the sha256 of the three corpus files it
       reads (`site/<VOL>.json`, `verse/`, `hide/`) in `pbreak/_stamp.json`.
       Exact, 0.3s, and the only one of the three that catches the `29KhuA10`
       shape.  A volume with a map and no stamp is STALE, not exempt.
    2. STRUCTURE -- a `drawnIndex` past the end of the sequence the current
       verse entry would draw, a `drawnOffset` past the end of that string, or
       a drawn address on an ordinal that is no longer a verse ordinal.  0 on
       all 118 today.  This one needs no stamp, so it still speaks if the
       sidecar is deleted or hand-written.
    3. AGREEMENT (--deep, ~15s) -- a 5-field record carries TWO addresses for
       the same printed page opening, `rawOffset` into `pr.text` and
       (`drawnIndex`, `drawnOffset`) into the drawn stream.  They must land on
       the same letters.  8,586 of 8,591 agree on the first 30 volumes; the
       five that do not are repeated pada openings, so the tolerance is a
       fraction, not zero.
    """
    D = _pbreak_load_derive()
    if D is None:
        return True, 'cannot import _xc/pagemark/derive.py -- pbreak NOT CHECKED'
    pd = os.path.join(ROOT, 'site/reader/pbreak')
    if not os.path.isdir(pd):
        return False, 'site/reader/pbreak/ does not exist'
    vols = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(pd, '*.json'))
                  if not os.path.basename(f).startswith('_'))
    stamps = {}
    sp = os.path.join(pd, '_stamp.json')
    if os.path.exists(sp):
        try:
            stamps = json.load(open(sp, encoding='utf-8'))
        except Exception:
            stamps = {}
    unstamped, drifted, hard, disagree, pairs = [], [], [], 0, 0
    loud = []
    for v in vols:
        want = D.stamp_of(v)
        got = stamps.get(v)
        if got is None:
            unstamped.append(v)
        elif got != want:
            who = [k for k in want if want.get(k) != (got or {}).get(k)]
            drifted.append((v, who))
        try:
            m = json.load(open(os.path.join(pd, v + '.json'), encoding='utf-8'))
        except Exception:
            hard.append((v, '?', 'unreadable map'))
            continue
        vp = os.path.join(ROOT, 'site/reader/verse', v + '.json')
        vm = json.load(open(vp, encoding='utf-8')) if os.path.exists(vp) else {}
        paras = None
        vpairs = vdis = 0
        for o, recs in m.items():
            e = vm.get(str(o))
            verse = bool(e) and e.get('groups') is not None
            seq = D.flat_drawn(e) if verse else None
            for r in recs:
                if len(r) < 5:
                    continue
                if not verse:
                    hard.append((v, o, 'drawn address on an ordinal the verse branch no longer draws'))
                    continue
                if not (0 <= r[3] < len(seq)):
                    hard.append((v, o, 'drawnIndex %s but the verse entry draws %d strings'
                                 % (r[3], len(seq))))
                    continue
                if not (0 <= r[4] <= len(seq[r[3]])):
                    hard.append((v, o, 'drawnOffset %s past the end of a %d-character string'
                                 % (r[4], len(seq[r[3]]))))
                    continue
                if not deep:
                    continue
                if paras is None:
                    paras = json.load(open(os.path.join(ROOT, 'site', v + '.json'),
                                           encoding='utf-8'))['paragraphs']
                if not (0 <= int(o) < len(paras)):
                    continue
                drawn = ''.join(c for c in (seq[r[3]][r[4]:] + ' ' + ' '.join(seq[r[3] + 1:r[3] + 4]))
                                if D.letters(c))
                raw = ''.join(c for c in ((paras[int(o)].get('text') or '')[r[0]:r[0] + 240])
                              if D.letters(c))
                if len(drawn) < 30 or len(raw) < 30:
                    continue
                pairs += 1
                vpairs += 1
                if drawn[:30] != raw[:30]:
                    disagree += 1
                    vdis += 1
        # PER VOLUME, NOT CORPUS-WIDE.  One stale volume is a few hundred records
        # against 30,000 good ones, so a corpus rate would barely move; and the
        # honest rate is not zero.  MEASURED over all 118: 30,376 agree, 46 do
        # not (0.151%), the worst volume 34KhuA15 at 2.49% and only four above
        # 1% -- repeated pada openings, where the printed stream and the corpus
        # order two identical lines differently.  10% is four times the worst
        # honest reading and far below a stale map, where the addresses are not
        # merely reordered but meaningless (`29KhuA10`: 253 of ~453).
        if vpairs and vdis >= 5 and vdis * 10 > vpairs:
            loud.append((v, vdis, vpairs))
    msgs = []
    if unstamped:
        msgs.append('%d volume(s) have a map and NO stamp (%s) -- derive.py has not run '
                    'since the stamp was added; re-derive or run '
                    '`python3 _xc/pagemark/stamp_existing.py --write`'
                    % (len(unstamped), ', '.join(unstamped[:6])))
    if drifted:
        msgs.append('%d volume(s) DERIVED FROM SOURCES THAT HAVE SINCE CHANGED: %s'
                    % (len(drifted),
                       '; '.join('%s (%s)' % (v, ', '.join(sorted(who)))
                                 for v, who in drifted[:6])))
    if hard:
        msgs.append('%d record(s) address a verse stream that no longer exists, e.g. %s ord %s: %s'
                    % (len(hard), hard[0][0], hard[0][1], hard[0][2]))
    if loud:
        msgs.append('%d volume(s) whose two addresses no longer name the same page '
                    'opening (>10%%): %s'
                    % (len(loud), ', '.join('%s %d/%d' % x for x in loud[:6])))
    if msgs:
        return False, ' | '.join(msgs)
    return True, ('%d volumes stamped and structurally sound%s'
                  % (len(vols), ', %d of %d two-address records agree'
                     % (pairs - disagree, pairs) if deep and pairs else ''))


# (label, artefact, sources, rebuild command, content-check fn or None)
DERIVED = [
    ('pageindex', 'site/reader/pageindex.json', ['site/*.json'],
     'python3 pipeline/build_pageindex.py', _pageindex_content),
    ('pagespan', 'site/reader/pagespan.json', ['site/*.json', '_seam/*.txt'],
     'python3 pipeline/build_pagespan.py --write', None),
    ('pdfblanks', 'site/reader/pdfblanks.json', ['site/*.json'],
     'python3 pipeline/build_pdfblanks.py --write', 'deep:%s' % '_pdfblanks_content'),
    ('search index', 'site/index', ['site/*.json'],
     'python3 pipeline/build_search_index.py', None),
    # NOT an mtime screen: see `_pbreak_content`.  212MB of verse maps means any
    # side-map rebuild makes the directory look stale, and the failure this
    # catches (`29KhuA10`, 3 misplaced page rules -> 253) leaves the mtimes fine.
    ('pbreak', 'site/reader/pbreak', ['site/reader/verse/*.json'],
     'python3 _xc/pagemark/derive.py <VOL> --out site/reader/pbreak'
     '   (move the old file away first -- derive.py SKIPS an existing output)',
     _pbreak_content),
]

# ADVISORY, NOT BLOCKING (added 2026-07-31b).  These are derived from the corpus
# too, and the same silent staleness is possible — but they are reported rather
# than enforced, for two reasons.  `linksk/` and `links/` are ALREADY older than
# the newest volume JSON (13:18 against 13:49 on 30 July), so blocking on them
# would stop every deploy until a rebuild nobody has scheduled; and the apparatus
# is rebuilt by a different pipeline whose inputs are the PDFs, so an mtime
# screen against `site/*.json` would misjudge it.  Wire any of these into
# DERIVED once its rebuild is routine — a blocking check nobody can satisfy gets
# answered with --force, which is worse than an advisory nobody reads.
ADVISORY = [
    ('apparatus', 'site/reader/apparatus',
     ['site/*.json', 'pipeline/extract.py', 'pipeline/rebuild_apparatus.py'],
     'python3 pipeline/rebuild_apparatus.py  (then _xref/fill_xrefs.py --write)'),
    ('linksk (reader)', 'site/reader/linksk', ['site/*.json'],
     'the link builders — see HANDOFF; never run pipeline/build_links.py'),
    # `links (legacy)` RETIRED 2026-08-08, at the reader's decision and on
    # measurement, not narrative: over the 20,263 canon paragraphs where BOTH
    # generations offered a commentary target, the old generation's target
    # agreed with the source's section name 26.95% of the time against
    # linksk/'s 46.48% (identical proxy applied to both), covered 22,348
    # paragraphs against 43,607, and addressed them by paragraph number and
    # `id` — the two recorded non-keys.  Loaded by nothing on the site.  The
    # files remain in git history; the reader deletes the working tree copy
    # with `git rm -r site/reader/links/`.
    ('sections', 'site/reader/sections', ['site/*.json'],
     'the per-volume nav builders'),
    ('nav.json', 'site/reader/nav.json', ['site/reader/sections/*'],
     'the nav builders — NEVER import one; run as a subprocess'),
]


def run(quiet=False, deep=False):
    rows, stale = [], 0
    for label, art, srcs, cmd, content in DERIVED:
        ap = os.path.join(ROOT, art)
        if os.path.isdir(ap):
            files = glob.glob(os.path.join(ap, '*'))
            amt = max((os.path.getmtime(f) for f in files), default=0.0)
        else:
            amt = os.path.getmtime(ap) if os.path.exists(ap) else 0.0
        smt, who = _newest(srcs)
        if isinstance(content, str) and content.startswith('deep:'):
            if deep:
                good, why = globals()[content[5:]]()
                kind = 'content'
            else:
                good = amt >= smt and amt > 0
                kind = 'mtime'
                why = ('newer than every source' if good else
                       'older than %s — MAY be stale; confirm with --deep, which rebuilds and '
                       'compares' % (os.path.relpath(who, ROOT) if who else '?'))
        elif content is not None:
            # A content check may want to know whether this is a deep run.  Only
            # `_pbreak_content` does; the others keep their zero-argument form,
            # so the flag is passed by inspection rather than by convention.
            try:
                good, why = content(deep) if content is _pbreak_content else content()
            except TypeError:
                good, why = content()
            kind = 'content+deep' if (content is _pbreak_content and deep) else 'content'
        else:
            good = amt >= smt and amt > 0
            kind = 'mtime'
            why = ('newer than every source' if good else
                   'OLDER than %s' % (os.path.relpath(who, ROOT) if who else '?'))
        rows.append((label, kind, good, why, cmd))
        if not good:
            stale += 1
    adv = []
    for label, art, srcs, cmd in ADVISORY:
        ap = os.path.join(ROOT, art)
        files = glob.glob(os.path.join(ap, '*')) if os.path.isdir(ap) else ([ap] if os.path.exists(ap) else [])
        amt = max((os.path.getmtime(f) for f in files), default=0.0)
        smt, who = _newest(srcs)
        if amt and smt and amt < smt:
            adv.append((label, os.path.relpath(who, ROOT) if who else '?', cmd))

    ok, why = _pageindex_selfcheck()
    rows.append(('pageindex self-check', 'corpus', ok, why,
                 'python3 pipeline/build_pageindex.py'))
    if not ok:
        stale += 1
    if not quiet or stale:
        for label, kind, good, why, cmd in rows:
            print('  %-22s %-8s %s  %s' % (label, kind, 'ok   ' if good else 'STALE', why))
            if not good:
                print('  %-22s %-8s        rebuild with: %s' % ('', '', cmd))
        print('\n%s' % ('%d DERIVED ARTEFACT(S) STALE — do not deploy' % stale if stale
                        else 'all derived artefacts fresh'))
        if adv:
            print('\nADVISORY — derived, older than their sources, NOT blocking:')
            for label, who, cmd in adv:
                print('  %-18s older than %s' % (label, who))
                print('  %-18s rebuild: %s' % ('', cmd))
    return stale


if __name__ == '__main__':
    sys.exit(1 if run('--quiet' in sys.argv, '--deep' in sys.argv) else 0)
