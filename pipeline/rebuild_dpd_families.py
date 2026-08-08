#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Give DPD's root family, compound family and idioms their content back.

WHY.  Reader, 2026-08-09: clicking those chips showed `root family
loading...` forever, and after the scrub the chips were gone entirely — he
wants them back WITH their content.  Diagnosed against the GoldenDict source
(reconnected by the reader): each raw entry carries an inline script

    var data_<lemma> = {..., "family_root": "√su 1 √su",
                        "family_compounds": ['sāvaka'], "family_idioms": [...]}

whose fields are KEYS into three shared files in the build's res/ folder —
family_root_json.js (4.1 MB, 3,358 families), family_compound_json.js
(6.5 MB, 5,502), family_idiom_json.js (0.57 MB, 1,170).  `dpd_trim` stripped
every <script>, losing the keys, and the shared files were never ingested:
the stubs could not have loaded from anywhere.

WHAT THIS BUILDS:
  * stores/lookup_eval/family/{root,comp,idm}/<p2>.json (+.json.gz) —
    key -> PRE-RENDERED HTML in the wording of DPD's own templates (heading +
    table), minus its feedback footer, which the original trim already
    dropped deliberately;
  * stores/lookup_eval/dpd/* rewritten: same entries, byte-identical except
    the three stub divs, which are EMPTIED of their `loading...` lie and
    stamped with `data-fk` carrying their JSON-encoded key list.

THIS IS A REFRESH, NOT A ROUND-TRIP.  The store was built from the
2026-05-01 GoldenDict release; the reader's folder is 2026-07-28.  Measured
before deciding: entry `a 1.1` differs from the store in exactly four date
strings and nothing else, so the July source is the same pipeline later in
time, and every entry REBUILDS from it — DPD's own updates ride along.  The
158 headwords the newer release no longer carries keep their stored entries
(reported), because the form index still points at them.

SELF-CHECKS:
  1. REPORT the scale honestly: entries identical after date normalisation
     vs really changed by the DPD update vs kept-stale;
  2. every extracted key resolves in its family file (fatal);
  3. after writing: zero `loading...` strings anywhere, every `data-fk` key
     resolves in the emitted family store (fatal).

The PANEL side (fetch on chip click, inject) is a separate change in
panel.js; WLV must be bumped — the STORES change this time — and the new
family/ tree must be uploaded to the R2 bucket beside the rest of
lookup_eval/ or production serves 404s and only the archive fallback works.

Usage:  GD_DIR=/path/to/GoldenDict python3 pipeline/rebuild_dpd_families.py
        (GD_DIR must contain dpd/dpd.idx etc.; report first, --apply writes)
"""
import sys, os, re, json, gzip, glob, collections, html as htmllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, '_panel'))
import sources

GD = os.environ.get('GD_DIR')
if not GD or not os.path.exists(os.path.join(GD, 'dpd', 'dpd.idx')):
    print('set GD_DIR to the GoldenDict folder (containing dpd/dpd.idx)'); sys.exit(2)
DPDDIR = os.path.join(ROOT, 'stores', 'lookup_eval', 'dpd')
FAMDIR = os.path.join(ROOT, 'stores', 'lookup_eval', 'family')
APPLY = '--apply' in sys.argv

FOLD = {'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'}
def fold(s): return ''.join(FOLD.get(c, c) for c in s.lower())
def p2(key):
    letters = re.sub(r'[^a-z]', '', fold(key))
    return (letters[:2] if len(letters) >= 2 else (letters + '_')[:2]) or '__'

def res_json(name):
    s = open(os.path.join(GD, 'dpd', 'res', name), encoding='utf-8').read()
    m = re.match(r'\s*(?:const|var|let)\s+\w+\s*=\s*', s)
    return json.loads(s[m.end():].rstrip().rstrip(';'))

E = htmllib.escape
def render_rows(rows):
    h = '<table class=family><tbody>'
    for r in rows:
        h += ('<tr><th>' + E(r[0]) + '</th><td><b>' + E(r[1]) + '</b></td><td>'
              + E(r[2]) + '</td><td><span class=gray>' + E(r[3]) + '</span></td></tr>')
    return h + '</tbody></table>'
def render_root(fr):
    return ('<p class="heading underlined"><b>%d</b> words belong to the root family <b>%s</b> (%s)</p>'
            % (fr['count'], E(fr['root_family']), E(fr['root_meaning']))) + render_rows(fr['data'])
def render_comp(key, fc):
    return ('<p class="heading underlined"><b>%d</b> compounds contain <b>%s</b></p>'
            % (fc['count'], E(key))) + render_rows(fc['data'])
def render_idm(key, fi):
    return ('<p class="heading underlined"><b>%d</b> idioms contain <b>%s</b></p>'
            % (fi['count'], E(re.sub(r'\d+$', '', key)))) + render_rows(fi['data'])

# tolerant field extraction from the inline `var data_<lemma> = {...}` —
# NOT json.loads: the lists are single-quoted.  Apostrophes inside a lemma
# would break the inner regex, so anything unparseable is REPORTED.
RE_ROOT = re.compile(r'"family_root":\s*"([^"]*)"')
RE_COMP = re.compile(r'"family_compounds":\s*\[(.*?)\]', re.S)
RE_IDM  = re.compile(r'"family_idioms":\s*\[(.*?)\]', re.S)
RE_ITEM = re.compile(r"'([^']*)'")
def extract_keys(raw):
    m = re.search(r'<script>\s*var data_', raw)
    seg = raw[m.start():raw.find('</script>', m.start())] if m else ''
    root = (RE_ROOT.search(seg) or [None]) and (RE_ROOT.search(seg).group(1) if RE_ROOT.search(seg) else '')
    comp = RE_ITEM.findall(RE_COMP.search(seg).group(1)) if RE_COMP.search(seg) else []
    idm  = RE_ITEM.findall(RE_IDM.search(seg).group(1)) if RE_IDM.search(seg) else []
    return root.strip(), comp, idm

def main():
    idx = sources.read_idx(os.path.join(GD, 'dpd', 'dpd.idx'))
    pos = {w: i for i, (w, _, _) in enumerate(idx)}
    dictf = sources.ensure_dict(os.path.join(GD, 'dpd', 'dpd'))
    fam_src = {'root': res_json('family_root_json.js'),
               'comp': res_json('family_compound_json.js'),
               'idm':  res_json('family_idiom_json.js')}

    shards = sorted(glob.glob(os.path.join(DPDDIR, '*.json.gz')))
    NDATE = re.compile(r'20\d\d-\d\d-\d\d')
    changed, missing_hw, badkeys = [], [], []
    used = {'root': set(), 'comp': set(), 'idm': set()}
    new_shards = {}
    n_entries = n_stamped = n_same = 0
    for sf in shards:
        d = json.load(gzip.open(sf))
        out = {}
        for hw, old in d.items():
            n_entries += 1
            if hw not in pos:
                # kept-stale: the July release dropped this headword, so its
                # May entry stays — with its stubs scrubbed the same way,
                # since no family content can ever arrive for it
                missing_hw.append(hw)
                dead0 = set()
                oldh = re.sub(r'<div class="dpd content hidden" id="?([^ >"]+)"?>[^<]*loading\.\.\.</div>',
                              lambda m: (dead0.add(m.group(1)), '')[1], old)
                if dead0:
                    oldh = re.sub(r'<a (?=[^>]*class="?dpd-button)[^>]*data-target="?([^ >"]+)"?[^>]*>[^<]*</a>',
                                  lambda m: '' if m.group(1) in dead0 else m.group(0), oldh)
                out[hw] = oldh; continue
            w, off, sz = idx[pos[hw]]
            raw = sources.entry(dictf, off, sz)
            trimmed = sources.dpd_trim(raw)
            if NDATE.sub('', trimmed) == NDATE.sub('', old): n_same += 1
            else: changed.append(hw)
            root, comp, idm = extract_keys(raw)
            fks = {'root': [root] if root else [], 'comp': comp, 'idm': idm}
            # a key the res/ files do not carry is DPD's own inconsistency
            # (121 of ~78,000 at last count): DROP it — the div stays a stub
            # and the panel's scrub removes its chip, which is the honest
            # rendering of "DPD promises this and cannot deliver it either"
            for t in fks:
                keep = []
                for k in fks[t]:
                    if k in fam_src[t]: used[t].add(k); keep.append(k)
                    else: badkeys.append((t, hw, k))
                fks[t] = keep
            nh = trimmed
            def stamp(nh, div_id_prefix, keys):
                if not keys: return nh, 0
                pat = re.compile(r'(<div class="dpd content hidden" id=' + div_id_prefix
                                 + r'[^ >]*)>([^<]*loading\.\.\.)?')
                return pat.sub(lambda m: m.group(1) + " data-fk='"
                               + json.dumps(keys, ensure_ascii=False).replace("'", '&#39;') + "'>", nh, 1), 1
            s1 = s2 = s3 = 0
            nh, s1 = stamp(nh, 'family_root_',     fks['root'])
            nh, s2 = stamp(nh, 'family_compound_', fks['comp'])
            nh, s3 = stamp(nh, 'family_idiom_',    fks['idm'])
            n_stamped += (s1 + s2 + s3)
            # every stub that remains — family_set_/family_word_ (not asked
            # for; add the same way if ever wanted), and divs whose entry has
            # no key for them — is removed HERE with its chip, so the store
            # never ships a promise it cannot keep.  panel.js's dpdScrub
            # stays as belt-and-braces for old cached shards.
            dead = set()
            def _kill(m):
                dead.add(m.group(1)); return ''
            nh = re.sub(r'<div class="dpd content hidden" id="?([^ >"]+)"?>[^<]*loading\.\.\.</div>',
                        _kill, nh)
            if dead:
                nh = re.sub(r'<a (?=[^>]*class="?dpd-button)[^>]*data-target="?([^ >"]+)"?[^>]*>[^<]*</a>',
                            lambda m: '' if m.group(1) in dead else m.group(0), nh)
            out[hw] = nh
        new_shards[sf] = out

    print('entries: %d | stamped divs: %d | identical after date-norm: %d | changed by the DPD update: %d | kept stale (gone from July idx): %d | unresolvable keys: %d'
          % (n_entries, n_stamped, n_same, len(changed), len(missing_hw), len(badkeys)))
    print('families used: root %d/%d, comp %d/%d, idm %d/%d'
          % (len(used['root']), len(fam_src['root']), len(used['comp']),
             len(fam_src['comp']), len(used['idm']), len(fam_src['idm'])))
    if changed: print('  CHANGED sample:', changed[:8])
    if missing_hw: print('  KEPT-STALE sample:', missing_hw[:8])
    if badkeys: print('  DROPPED-KEY sample (DPD\'s own res/ lacks them; their chips scrub away):', badkeys[:6])
    if not APPLY:
        print('report only; nothing written (use --apply)'); return

    # family stores, pre-rendered, only the families our headwords reach
    for t, render in (('root', lambda k, v: render_root(v)),
                      ('comp', render_comp), ('idm', render_idm)):
        buckets = collections.defaultdict(dict)
        for k in used[t]:
            buckets[p2(k)][k] = render(k, fam_src[t][k]) if t != 'root' else render_root(fam_src[t][k])
        tdir = os.path.join(FAMDIR, t); os.makedirs(tdir, exist_ok=True)
        for p, m in buckets.items():
            body = json.dumps(m, ensure_ascii=False)
            open(os.path.join(tdir, p + '.json'), 'w', encoding='utf-8').write(body)
            gzip.open(os.path.join(tdir, p + '.json.gz'), 'wt', encoding='utf-8').write(body)
        print('family/%s: %d families in %d buckets' % (t, len(used[t]), len(buckets)))

    for sf, out in new_shards.items():
        body = json.dumps(out, ensure_ascii=False)
        open(sf[:-3], 'w', encoding='utf-8').write(body)      # .json
        gzip.open(sf, 'wt', encoding='utf-8').write(body)     # .json.gz
    print('dpd shards rewritten: %d' % len(new_shards))

    # ---- post-verification over what was actually written ----
    fam_have = {t: set() for t in used}
    for t in used:
        for f in glob.glob(os.path.join(FAMDIR, t, '*.json')):
            fam_have[t].update(json.load(open(f, encoding='utf-8')))
    bad = 0
    for sf in shards:
        d = json.load(gzip.open(sf))
        for hw, h in d.items():
            if 'loading...' in h: print('FAIL: loading... survives in', hw); bad += 1
            for m in re.finditer(r"data-fk='([^']*)'", h):
                for k in json.loads(m.group(1).replace('&#39;', "'")):
                    t = ('root' if '√' in k or k in fam_have['root'] else None)
                    if not any(k in fam_have[tt] for tt in fam_have):
                        print('FAIL: data-fk key unresolvable:', hw, k); bad += 1
    if bad: sys.exit(1)
    print('post-verification: zero loading..., every data-fk key resolves')

    # !!! A WRITTEN FILE THE BUCKET WILL NEVER SEE (2026-08-09, production:
    # "The family data could not be loaded").  `stores/lookup_eval/*` in
    # .gitignore ate the new family/ tree; `git add -A` skipped it; the
    # commit shipped without it; and r2_upload.sh — git-driven BY DESIGN —
    # correctly uploaded nothing.  Four correct mechanisms, one invisible
    # absence.  So this build now checks its own output is trackable.
    import subprocess
    probe = glob.glob(os.path.join(FAMDIR, '*', '*.json.gz'))[:1]
    if probe:
        r = subprocess.run(['git', '-C', ROOT, 'check-ignore', probe[0]],
                           capture_output=True)
        if r.returncode == 0:
            print('FAIL: %s is GIT-IGNORED — the bucket uploader takes its '
                  'file list from git and will never see it.  Fix .gitignore '
                  'first.' % probe[0])
            sys.exit(1)
    print('git-trackability: the family store is visible to git')

if __name__ == '__main__':
    main()
