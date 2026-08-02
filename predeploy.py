#!/usr/bin/env python3
"""A gate for the deploy, on the same argument as every other gate here.

`.gitignore` protects the REPOSITORY.  It does nothing for a deploy: `wrangler
pages deploy site` uploads what is on disk.  So the 441 MB of evaluation
dictionary data now sitting under `site/` — whose redistribution licences are
unconfirmed, and which §9 excludes from the reader's voice — is one careless
command away from the open internet, and `.assetsignore` is a single line
standing in its way.

One line is not enough for that.  This refuses the deploy outright if anything
that must not be published is present and unexcluded, and it refuses if the
upload would breach Cloudflare Pages' limits.  Run it before wrangler:

    python3 predeploy.py && wrangler pages deploy site --project-name=osbct-tipitaka

Exit 0 means the deploy is safe to run.  Anything else means stop.
"""
import os, sys, fnmatch

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, 'site')

# Directories that must NEVER be published, with the reason, so a future reader
# does not have to guess why the deploy is refusing.
FORBIDDEN = {
    'lookup_eval': 'evaluation dictionaries — Abhidhāna/PEU/PPN licences '
                   'unconfirmed, DPD excluded as a voice by §9',
}
# Cloudflare Pages free plan
MAX_FILES = 20000
MAX_FILE_BYTES = 25 * 1024 * 1024


def load_assetsignore():
    p = os.path.join(SITE, '.assetsignore')
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if line and not line.startswith('#'):
            out.append(line)
    return out


def excluded(rel, patterns):
    parts = rel.split(os.sep)
    for pat in patterns:
        if pat in parts:
            return True
        if fnmatch.fnmatch(os.path.basename(rel), pat):
            return True
    return False


def main():
    if not os.path.isdir(SITE):
        print('FAIL: no site/ directory here'); return 2
    patterns = load_assetsignore()
    problems, n_files, biggest = [], 0, (0, '')

    for name, why in FORBIDDEN.items():
        path = os.path.join(SITE, name)
        if os.path.isdir(path) and name not in patterns:
            problems.append(f'{name}/ is present under site/ and NOT in '
                            f'.assetsignore — {why}')

    for dirpath, dirnames, filenames in os.walk(SITE):
        rel_dir = os.path.relpath(dirpath, SITE)
        dirnames[:] = [d for d in dirnames
                       if not excluded(os.path.join(rel_dir, d).lstrip('./'), patterns)]
        for f in filenames:
            rel = os.path.relpath(os.path.join(dirpath, f), SITE)
            if excluded(rel, patterns) or f == '.assetsignore':
                continue
            n_files += 1
            sz = os.path.getsize(os.path.join(dirpath, f))
            if sz > biggest[0]:
                biggest = (sz, rel)

    if n_files > MAX_FILES:
        problems.append(f'{n_files:,} files would upload; Cloudflare Pages '
                        f'allows {MAX_FILES:,}')
    if biggest[0] > MAX_FILE_BYTES:
        problems.append(f'{biggest[1]} is {biggest[0]/1048576:.1f} MB; the '
                        f'per-file limit is {MAX_FILE_BYTES/1048576:.0f} MB')

    print(f'would upload {n_files:,} files, largest {biggest[0]/1024:.0f} kB '
          f'({biggest[1]})')
    for name in FORBIDDEN:
        print(f'  {name}/: '
              + ('excluded' if name in patterns else '!!! NOT EXCLUDED'))
    if problems:
        print('\nDEPLOY REFUSED:')
        for p in problems:
            print('  ✗ ' + p)
        return 1
    print('\ndeploy gate: clear')
    return 0


if __name__ == '__main__':
    sys.exit(main())
