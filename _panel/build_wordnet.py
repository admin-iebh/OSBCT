#!/usr/bin/env python3
"""WordNet 3.1 -> site/lookup/wn/, sharded exactly as build_lookup.py shards.

WHY THIS EXISTS
    The panel's reference tabs are written in the technical English of
    1921-2020 philology -- "almsman", "denominative", "periphrastic",
    "aorist".  This project's stated audience meets that English before it
    meets the Pāḷi.  So an English word inside someone else's gloss is
    clickable, and this is what answers it.  Reader's decision, 2026-08-02
    (`claude/panel_backlog_and_decisions_2026-08-02.md`, item 4; section H of
    the design brief).

    It does not touch §9.  §9 governs which dictionaries may speak about
    PĀḶI.  An English dictionary explaining an English word in another
    dictionary's gloss is not a Pāḷi authority and never presents itself as
    one.  It is attributed in the panel like every other source, because §9's
    attribution obligation is not limited to the Abhidhāna.

SOURCE AND LICENCE -- CHECKED, NOT REPEATED
    WordNet 3.1, Princeton University, taken from the `wordnet31` corpus in
    `nltk_data` (raw.githubusercontent.com/nltk/nltk_data), which carries the
    database files unmodified.  `wordnet31/README` names 3.1; `log.grind.3.1`
    is the build log of that release.

    The licence shipped in that corpus (`wordnet31/LICENSE`) grants use, copy,
    modification and distribution "for any purpose and without fee or royalty"
    on ONE condition that matters here: the copyright notice and disclaimer
    must "appear on ALL copies".  So the notice travels with the data --
    `site/lookup/wn/LICENSE` -- and the panel shows the attribution line.  The
    file is headed "WordNet Release 3.0" because Princeton carried the same
    licence text forward unchanged; the data is 3.1.

WHAT IS DROPPED, AND WHY IT IS SAID HERE
    * MULTI-WORD LEMMAS (`abdominal_cavity`).  The panel reaches this store by
      recovering ONE word under the caret, so a two-word headword can never be
      asked for.  Measured below at build time and printed -- a silent drop
      reads as coverage that is not there.
    * Nothing else.  Every single-word lemma in all four parts of speech is
      shipped with all of its senses in WordNet's own sense order.

MORPHOLOGY
    A reader clicks `mendicants`, and WordNet is keyed on `mendicant`.  The
    irregular forms are WordNet's own exception lists (noun.exc, verb.exc,
    adj.exc, adv.exc) and they are folded into this store as ALIAS keys --
    `"men": "man"` -- so the browser needs no exception file.  The regular
    suffix rules (Morphy's detachment table) are four lines of JavaScript and
    live in panel.js, tried only after the exact key misses.

OUTPUT
    site/lookup/wn/<shard>.json   value is EITHER a list of senses
                                  [[pos, def, [examples], [synonyms]], ...]
                                  OR a string, the lemma this form is an
                                  inflection of.
    site/lookup/wn/LICENSE        Princeton's notice, verbatim
    site/lookup/index.json        `sets.wn` and `shards.wn` merged in, leaving
                                  every other set untouched -- this file is
                                  built by build_lookup.py from sources that
                                  are not all present in every session, so it
                                  is EDITED, never regenerated, from here.
"""
import collections, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
OUT = os.path.join(REPO, 'site', 'lookup', 'wn')
MANIFEST = os.path.join(REPO, 'site', 'lookup', 'index.json')
CAP = 150_000                      # the same ceiling build_lookup.py keeps

FOLD = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm', 'ṅ': 'n', 'ñ': 'n',
        'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ḷ': 'l'}
fold = lambda s: ''.join(FOLD.get(c, c) for c in s.lower())

POS = {'n': 'noun', 'v': 'verb', 'a': 'adj', 'r': 'adv'}


def shard_table(keys_bytes):
    """Verbatim in behaviour from build_lookup.py: adaptive prefix sharding,
    start at depth 2, split any bucket over the cap one character deeper."""
    def bucket(k, d):
        return (fold(k)[:d] + '_' * d)[:d]

    assign, work, manifest = {}, [(2, list(keys_bytes.items()))], {}
    while work:
        depth, items = work.pop()
        groups = collections.defaultdict(list)
        for k, b in items:
            groups[bucket(k, depth)].append((k, b))
        if len(groups) == 1 and depth > 40:
            g, gi = next(iter(groups.items()))
            for k, _ in gi:
                assign[k] = g
            manifest[g] = {'keys': len(gi), 'bytes': sum(b for _, b in gi)}
            continue
        for g, gi in groups.items():
            total = sum(b for _, b in gi) + 2 * len(gi)
            if total > CAP and len(gi) > 1:
                work.append((depth + 1, gi))
            else:
                for k, _ in gi:
                    assign[k] = g
                manifest[g] = {'keys': len(gi), 'bytes': total}
    return assign, manifest


def parse_gloss(g):
    """`definition; "an example"; "another"` -> (definition, [examples]).

    Split on ';' and call a part an example when it is QUOTED; everything
    before the first quoted part is the definition, rejoined, because
    definitions contain semicolons of their own."""
    parts = [p.strip() for p in g.split(';')]
    d, ex, in_ex = [], [], False
    for p in parts:
        if p.startswith('"'):
            in_ex = True
            ex.append(p.strip('"').strip())
        elif in_ex and ex:
            ex[-1] = ex[-1] + '; ' + p.strip('"').strip()     # a quoted example that itself had a ';'
        else:
            d.append(p)
    return '; '.join(x for x in d if x), [e for e in ex if e]


def read_data(src):
    """offset -> (pos, definition, examples, [words])"""
    syn = {}
    for p in POS:
        path = os.path.join(src, 'data.' + POS[p])
        with open(path, encoding='utf-8', errors='replace') as fh:
            for line in fh:
                if line.startswith('  '):
                    continue
                head, _, gloss = line.partition('|')
                f = head.split()
                if len(f) < 4:
                    continue
                off, ss_type, w_cnt = f[0], f[2], int(f[3], 16)
                words = []
                for i in range(w_cnt):
                    w = f[4 + 2 * i]
                    words.append(re.sub(r'\(.*?\)$', '', w).replace('_', ' '))
                d, ex = parse_gloss(gloss.strip())
                # `a` and `s` are both adjectives (`s` = satellite); the reader
                # does not care which, and "adj" is what a gloss reader needs
                syn[(POS[p], off)] = ('a' if ss_type in 'as' else ss_type, d, ex, words)
    return syn


def read_index(src):
    """lemma -> [(pos, offset), ...] in WordNet's own sense order"""
    out = collections.defaultdict(list)
    for p in POS:
        path = os.path.join(src, 'index.' + POS[p])
        with open(path, encoding='utf-8', errors='replace') as fh:
            for line in fh:
                if line.startswith('  '):
                    continue
                f = line.split()
                if len(f) < 6:
                    continue
                lemma, n_synsets = f[0], int(f[2])
                offs = f[-n_synsets:]
                for o in offs:
                    out[lemma].append((POS[p], o))
    return out


def read_exceptions(src):
    """inflected -> base, from WordNet's own exception lists"""
    exc = {}
    for p in POS:
        path = os.path.join(src, POS[p] + '.exc')
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8', errors='replace') as fh:
            for line in fh:
                f = line.split()
                if len(f) >= 2 and '_' not in f[0]:
                    exc.setdefault(f[0], f[1])
    return exc


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else '/tmp/wn31/wordnet31'
    syn = read_data(src)
    idx = read_index(src)
    exc = read_exceptions(src)

    data, multi, unreach = {}, 0, 0
    for lemma, senses in idx.items():
        if '_' in lemma:
            multi += 1
            continue
        # !!! THE SHARD NAME IS A FILE NAME AND A URL, and English lemmas are
        # not Pāḷi ones: `9/11` shards to `9/` and the write fails on the
        # slash.  Pure letters (with internal hyphen or apostrophe) is also
        # exactly what a click can ever recover, so nothing reachable is lost.
        if not re.fullmatch(r"[a-z][a-z'\-]*", lemma.lower()):
            unreach += 1
            continue
        rows = []
        for pos, off in senses:
            s = syn.get((pos, off))
            if not s:
                continue
            t, d, ex, words = s
            others = [w for w in words if w.lower() != lemma.lower() and ' ' not in w]
            row = [t, d]
            if ex or others:
                row.append(ex)
            if others:
                row.append(others[:8])
            rows.append(row)
        if rows:
            data[lemma.lower()] = rows

    aliases = 0
    for form, base in exc.items():
        f = form.lower()
        if f in data or base.lower() not in data:
            continue
        data[f] = base.lower()
        aliases += 1

    entry = lambda k, v: (len(k.encode()) + 3
                          + len(json.dumps(v, ensure_ascii=False).encode()) + 1)
    sizes = {k: entry(k, v) for k, v in data.items()}
    assign, man = shard_table(sizes)

    os.makedirs(OUT, exist_ok=True)
    # !!! `glob('*.json')` DOES NOT SEE A DOTFILE, AND THE FIRST RUN LEFT ONE.
    # Before the alphabetic filter below existed, this build crashed on the
    # lemma `9/11` (whose shard name carries a slash) — but not before writing
    # `.2.json`, from `.22-caliber`.  The next run's cleanup globbed past it,
    # and it was staged for commit as part of the shipped store: a shard no
    # manifest names, which the panel can never fetch and no reader would ever
    # see fail.  Use listdir, and verify the directory against the manifest at
    # the end of this function rather than trusting the cleanup.
    for f in os.listdir(OUT):
        if f.endswith('.json'):
            os.remove(os.path.join(OUT, f))
    buckets = collections.defaultdict(dict)
    for k, v in data.items():
        buckets[assign[k]][k] = v
    biggest = 0
    for name, obj in buckets.items():
        p = os.path.join(OUT, name + '.json')
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump(obj, fh, ensure_ascii=False, separators=(',', ':'))
        biggest = max(biggest, os.path.getsize(p))

    lic = os.path.join(src, 'LICENSE')
    if os.path.exists(lic):
        with open(lic, encoding='utf-8', errors='replace') as fh:
            txt = fh.read()
        with open(os.path.join(OUT, 'LICENSE'), 'w', encoding='utf-8') as fh:
            fh.write(txt)

    # ---- merge into the existing manifest; never regenerate it
    m = json.load(open(MANIFEST, encoding='utf-8'))
    m.setdefault('sets', {})['wn'] = {
        'keys': len(data),
        'largest_bytes': biggest,
        'aliases': aliases,
        'source': 'WordNet 3.1, Princeton University — Princeton WordNet '
                  'licence (permissive; the copyright notice must travel with '
                  'the data, and does: site/lookup/wn/LICENSE). English→English '
                  'only: it explains the English of the reference tabs and is '
                  'not a Pāḷi authority (§9 untouched).',
        'note': 'single-word alphabetic lemmas only (%d multi-word headwords '
                'and %d containing digits or punctuation dropped — a click '
                'recovers one word of letters and can never ask for them); '
                'values are [[pos, definition, [examples], [synonyms]], …], or '
                'a string naming the lemma this inflection belongs to'
                % (multi, unreach),
    }
    m.setdefault('shards', {})['wn'] = man
    with open(MANIFEST, 'w', encoding='utf-8') as fh:
        json.dump(m, fh, ensure_ascii=False, indent=1)

    # the directory and the manifest must name exactly the same shards: a file
    # the manifest does not name is unreachable, and a name with no file is a
    # 404 in the panel
    on_disk = {f[:-5] for f in os.listdir(OUT) if f.endswith('.json')}
    extra, absent = on_disk - set(man), set(man) - on_disk
    if extra or absent:
        print('    !! shard directory and manifest disagree: %d unnamed files '
              '%s, %d named files missing %s'
              % (len(extra), sorted(extra)[:5], len(absent), sorted(absent)[:5]))
        return 1

    print('wn: %d keys (%d alias forms), %d shards, largest %d bytes'
          % (len(data), aliases, len(buckets), biggest))
    print('    %d multi-word headwords dropped, %d not pure-alphabetic' % (multi, unreach))
    print('    total %.1f MB'
          % (sum(os.path.getsize(p) for p in glob.glob(os.path.join(OUT, '*.json'))) / 1e6))
    if biggest > CAP:
        print('    !! a shard is over the %d-byte cap' % CAP)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
