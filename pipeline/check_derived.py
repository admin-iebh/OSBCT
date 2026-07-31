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
    ('links (legacy)', 'site/reader/links', ['site/*.json'],
     'loaded by nothing in reader2.html; retire or rebuild'),
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
            good, why = content()
            kind = 'content'
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
