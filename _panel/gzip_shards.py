#!/usr/bin/env python3
"""Store a shard set gzipped, and record that in its manifest.

WHY.  GitHub Pages caps a published site at 1 GB.  DPD's shards are 379.2 MB
across 11,229 files and did not fit, so the tab shipped disabled.  Stored
gzipped they are 43.7 MB (8.68x) and they fit with room to spare.

This is about the SIZE CAP, not about transfer: GitHub Pages already gzips a
.json response over the wire, so the reader was never downloading the expanded
bytes.  What changes is that the inflate now happens in `panel.js` instead of
in the network layer -- see `rawInflate` there, and its Safari-16.4 fallback.

WHAT IT TOUCHES.  For each named set it writes `<shard>.json.gz` beside every
`<shard>.json` and adds the set to the manifest's `gz` list.  It does NOT
delete the `.json` originals: they stay on disk, gitignored, so a rebuild does
not have to start from nothing.  `.gitignore` decides which of the two reaches
the site.

  python3 _panel/gzip_shards.py lookup_eval dpd          # step 1
  python3 _panel/gzip_shards.py lookup gloss freq forms ped   # step 2

`index.json` is NEVER gzipped -- it is what tells the panel which sets are,
so it has to be readable first. The script refuses to gzip it.

mtime=0 in the gzip header, so re-running produces byte-identical output and
does not churn git.
"""
import gzip, json, os, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)


def compact(store, sets):
    base = os.path.join(REPO, 'site', store)
    ipath = os.path.join(base, 'index.json')
    if not os.path.exists(ipath):
        sys.exit(f'no manifest at {ipath}')
    man = json.load(open(ipath))
    known = set(man.get('shards') or {})
    for s in sets:
        if s == 'index':
            sys.exit('refusing to gzip index.json: it names what is gzipped')
        if s not in known:
            sys.exit(f'{store}: no shard group named {s!r} (have {sorted(known)})')

    total_raw = total_gz = total_n = 0
    for s in sets:
        d = os.path.join(base, s)
        files = []
        for dirpath, _, names in os.walk(d):
            files += [os.path.join(dirpath, n) for n in names if n.endswith('.json')]
        files.sort()
        raw = gz = 0
        t0 = time.time()
        for f in files:
            b = open(f, 'rb').read()
            g = gzip.compress(b, 9, mtime=0)
            open(f + '.gz', 'wb').write(g)
            raw += len(b); gz += len(g)
        # Verify EVERY file round-trips, not a sample.  A shard that inflates
        # to something other than what went in is a silently wrong dictionary
        # entry on a reader's screen, and nothing downstream would catch it.
        bad = [f for f in files
               if gzip.decompress(open(f + '.gz', 'rb').read()) != open(f, 'rb').read()]
        if bad:
            sys.exit(f'{s}: {len(bad)} shards do not round-trip, first {bad[0]}')
        print(f'  {s:8s} {len(files):7,} files  {raw/1e6:8.1f} MB -> {gz/1e6:7.1f} MB'
              f'  {raw/max(gz,1):5.2f}x  ({time.time()-t0:.0f}s, all round-trip)')
        total_raw += raw; total_gz += gz; total_n += len(files)

    have = list(man.get('gz') or [])
    for s in sets:
        if s not in have:
            have.append(s)
    man['gz'] = sorted(have)
    json.dump(man, open(ipath, 'w'), ensure_ascii=False)
    print(f'  {"TOTAL":8s} {total_n:7,} files  {total_raw/1e6:8.1f} MB -> '
          f'{total_gz/1e6:7.1f} MB  {total_raw/max(total_gz,1):5.2f}x')
    print(f'  manifest {ipath}: gz = {man["gz"]}')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__.strip().split('\n\n')[-2])
    compact(sys.argv[1], sys.argv[2:])
