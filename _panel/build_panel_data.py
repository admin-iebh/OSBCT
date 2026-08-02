#!/usr/bin/env python3
"""OSBCT word-lookup panel PILOT — data builder.

Builds the per-volume lookup data for the panel prototype, for ONE canon
volume (default 09Ma01).  Standalone pilot: writes only under _panel/data/,
never into site/.

Sources (all filters or attributed sources, per project instructions §9):
  - DPD StarDict (dpd/, dpd-grammar/, dpd-deconstructor/)  — CC BY-NC-SA,
    EVALUATION ONLY in this prototype; the shipped panel must not carry DPD
    glosses (decided 2026-08-01, claude/start_here_dictionary_phase.md).
    Used here additionally as form→lemma resolver (the permitted filter use).
  - PEU StarDict (peu/) — English rendering of the Tipiṭaka-Pāḷi-Myanmā-
    Abhidhāna.  Machine-translated entries carry the literal string
    "Google Translate" and are flagged, never mixed.
  - pm12e.csv (Tipitaka-Pali-Projector legacy/pm12e.zip, 2020-12-09) — the
    Burmese Abhidhāna itself, citations intact.  THE lexical authority (§9).
  - _gloss/by_volume/ — step-3 aṭṭhakathā/ṭīkā glosses (the edition's own).
  - _vocab/freq/ — step-1 corpus frequency shards.
  - site/reader/links/<VOL>.fwd.json — proximity (linked commentary para).

Tokenisation and fold() replicate _vocab/tokenise.py and site/search.html
exactly; the character walk below is verified against a regex recount at the
end of the run (same discipline as _vocab/verify.py — a build that cannot
fail is not evidence).
"""
import json, re, os, sys, gzip, struct, csv, collections, html as htmllib

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get('PANEL_SRC', os.path.dirname(ROOT))  # dir holding site/, _gloss/, _vocab/, dicts
VOL = os.environ.get('PANEL_VOL', '09Ma01')
GLOSS_VOLS = ['10MaA01', '11MaA02', '12MaA03', '13MaA04',
              '13MaT01', '14MaT02', '15MaT03']
OUT = os.path.join(ROOT, 'data')

# ---------------------------------------------------------------- alphabet --
# From _vocab/tokenise.py — established by the character census, not assumed.
PALI = set('aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvsh ḷṁ'.replace(' ', ''))
PALI |= set(c.upper() for c in PALI)
MARK = re.compile(r'([a-zāīūṁṅñṭḍṇḷ])(\d{1,2})\b')
DIGITS = re.compile(r'\d+')
APOS = {'’', "'"}
WORDCHARS = PALI | APOS          # hyphen=split, matching _vocab/freq

FOLD = {'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'}
def fold(s):
    return ''.join(FOLD.get(c, c) for c in s.lower())

def clean(text):
    t = MARK.sub(r'\1', text)
    return DIGITS.sub(' ', t)

def tokens(text):
    buf = []; prev = ''
    for i, ch in enumerate(text):
        if ch in WORDCHARS:
            if ch in APOS:
                nxt = text[i+1] if i+1 < len(text) else ''
                if not (prev in PALI and nxt in PALI):
                    if buf: yield ''.join(buf); buf = []
                    prev = ch; continue
            buf.append(ch); prev = ch
        else:
            if buf: yield ''.join(buf); buf = []
            prev = ch
    if buf: yield ''.join(buf)

# ---------------------------------------------------------------- stardict --
def read_idx(path):
    data = open(path, 'rb').read(); out = []; i = 0
    while i < len(data):
        j = data.index(b'\0', i)
        w = data[i:j].decode('utf-8')
        off, sz = struct.unpack('>II', data[j+1:j+9])
        out.append((w, off, sz)); i = j + 9
    return out

def iter_syn(path):
    data = gzip.open(path).read() if path.endswith('.dz') else open(path,'rb').read()
    i = 0
    while i < len(data):
        j = data.index(b'\0', i)
        w = data[i:j].decode('utf-8')
        n = struct.unpack('>I', data[j+1:j+5])[0]
        yield w, n; i = j + 5

def ensure_dict(base):
    """Decompress <base>.dict.dz to <base>.dict once; return open file."""
    dz, plain = base + '.dict.dz', base + '.dict'
    if not os.path.exists(plain):
        with gzip.open(dz) as f, open(plain, 'wb') as g:
            while True:
                chunk = f.read(1 << 22)
                if not chunk: break
                g.write(chunk)
    return open(plain, 'rb')

def entry(f, off, sz):
    f.seek(off); return f.read(sz).decode('utf-8')

# ------------------------------------------------------------- dpd trimming --
BODY = re.compile(r'</head>\s*<body[^>]*>', re.S)
def dpd_trim(html):
    """Keep the visible entry: summary line + grammar/declension/root-family
    content divs.  Drop head, scripts, audio buttons, frequency (CST-based,
    not this edition), feedback forms."""
    m = BODY.search(html)
    body = html[m.end():] if m else html
    body = re.sub(r'</body>\s*</html>\s*$', '', body)
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    # drop audio play buttons
    body = re.sub(r'<a class="dpd-button play[^"]*"[^>]*>.*?</a>', '', body, flags=re.S)
    # drop frequency + feedback content divs and their buttons
    body = re.sub(r'<div class="dpd content hidden" id=(?:frequency|feedback)_[^>]*>.*?</div>', '', body, flags=re.S)
    body = re.sub(r'<a class=dpd-button data-target=(?:frequency|feedback)_[^>]*>.*?</a>', '', body, flags=re.S)
    body = re.sub(r'<p class=dpd-footer>.*?</p>', '', body, flags=re.S)
    return body

def gram_trim(html):
    m = BODY.search(html)
    body = html[m.end():] if m else html
    body = re.sub(r'</body>\s*</html>\s*$', '', body)
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    return body

DECON_LI = re.compile(r'<li>(.*?)</li>', re.S)
def decon_list(html):
    """Deconstructor entries are small HTML docs with an <ul> of analyses.
    Return the list of analyses as plain strings (alternatives, unranked)."""
    m = BODY.search(html)
    body = html[m.end():] if m else html
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    items = [re.sub(r'<[^>]+>', '', x).strip() for x in DECON_LI.findall(body)]
    if not items:
        body2 = ' '.join(re.sub(r'<[^>]+>', ' ', body).split())
        if body2: items = [body2]
    # strip the DPD boilerplate footer that rides inside the entry
    out = []
    for x in items:
        x = re.split(r'These word breakups are code-generated', x)[0].strip(' . ')
        if x: out.append(x)
    return out

# ------------------------------------------------------------------- build --
def main():
    os.makedirs(OUT, exist_ok=True)
    for d in ('forms', 'hw', 'gloss'):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)

    vol = json.load(open(os.path.join(SRC, 'site', f'{VOL}.json')))
    paras = vol['paragraphs']

    # 1. vocabulary of the volume ------------------------------------------
    forms = collections.Counter()
    for p in paras:
        for t in tokens(clean(p['text'])):
            forms[t] += 1
    # verification recount by regex (independent path)
    rx = re.compile('[' + ''.join(sorted(PALI)) + ']+(?:[’\'][' + ''.join(sorted(PALI)) + ']+)*')
    forms2 = collections.Counter()
    for p in paras:
        for t in rx.findall(clean(p['text'])):
            forms2[t] += 1
    assert forms == forms2, 'tokeniser disagreement: %d vs %d' % (len(forms), len(forms2))
    print(f'{VOL}: {sum(forms.values())} tokens, {len(forms)} types (verified by second path)')

    # normalised key sets for dict lookups
    def norm(w): return w.lower().replace('ṁ', 'ṃ')   # ṁ → ṃ
    need = {}
    for w in forms:
        need.setdefault(norm(w), set()).add(w)

    # 2. DPD syn: form → headword index ------------------------------------
    dpd_idx = read_idx(os.path.join(SRC, 'dpd', 'dpd.idx'))
    dpd_pos = {w: i for i, (w, _, _) in enumerate(dpd_idx)}
    form2hw = collections.defaultdict(set)
    for w in need:                       # headwords that ARE the form
        if w in dpd_pos: form2hw[w].add(w)
    hits = 0
    for w, n in iter_syn(os.path.join(SRC, 'dpd', 'dpd.syn.dz')):
        lw = w.lower()
        if lw in need:
            form2hw[lw].add(dpd_idx[n][0]); hits += 1
    print(f'DPD syn scan: {hits} synonym hits, {len(form2hw)} of {len(need)} normalised forms resolve')

    hws = sorted({h for s in form2hw.values() for h in s})
    print(f'{len(hws)} DPD headwords needed')

    # 3. DPD entries for those headwords ------------------------------------
    dpdf = ensure_dict(os.path.join(SRC, 'dpd', 'dpd'))
    dpd_html = {}
    for h in hws:
        w, off, sz = dpd_idx[dpd_pos[h]]
        dpd_html[h] = dpd_trim(entry(dpdf, off, sz))

    # 4. grammar + deconstructor, keyed by the FORM -------------------------
    gr_idx = read_idx(os.path.join(SRC, 'dpd-grammar', 'dpd-grammar.idx'))
    gr_pos = {w: (o, s) for w, o, s in gr_idx}
    grf = ensure_dict(os.path.join(SRC, 'dpd-grammar', 'dpd-grammar'))
    gram = {}
    for w in need:
        if w in gr_pos:
            o, s = gr_pos[w]; gram[w] = gram_trim(entry(grf, o, s))
    # syn for grammar (variant spellings)
    for w, n in iter_syn(os.path.join(SRC, 'dpd-grammar', 'dpd-grammar.syn.dz')):
        lw = w.lower()
        if lw in need and lw not in gram:
            hw2, o, s = gr_idx[n]; gram[lw] = gram_trim(entry(grf, o, s))
    print(f'grammar entries: {len(gram)}')

    de_idx = read_idx(os.path.join(SRC, 'dpd-deconstructor', 'dpd-deconstructor.idx'))
    de_pos = {w: (o, s) for w, o, s in de_idx}
    def_ = ensure_dict(os.path.join(SRC, 'dpd-deconstructor', 'dpd-deconstructor'))
    decon = {}
    for w in need:
        if w in de_pos:
            o, s = de_pos[w]; decon[w] = decon_list(entry(def_, o, s))
    for w, n in iter_syn(os.path.join(SRC, 'dpd-deconstructor', 'dpd-deconstructor.syn.dz')):
        lw = w.lower()
        if lw in need and lw not in decon:
            hw2, o, s = de_idx[n]; decon[lw] = decon_list(entry(def_, o, s))
    print(f'deconstructor entries: {len(decon)}')

    # 5. lemma set (strip DPD homonym numbering) + PEU + Abhidhāna ----------
    def base(h): return re.sub(r'\s+[\d.]+$', '', h)
    lemmas = sorted({base(h) for h in hws})
    peu_idx = read_idx(os.path.join(SRC, 'peu', 'peu.idx'))
    peu_pos = {w: (o, s) for w, o, s in peu_idx}
    peu_syn = {}
    for w, n in iter_syn(os.path.join(SRC, 'peu', 'peu.syn.dz')):
        peu_syn.setdefault(w, peu_idx[n][0])
    peuf = ensure_dict(os.path.join(SRC, 'peu', 'peu'))
    def peu_get(k):
        kk = k if k in peu_pos else peu_syn.get(k)
        if kk is None:
            k2 = k.replace('ṁ', 'ṃ')
            kk = k2 if k2 in peu_pos else peu_syn.get(k2)
        if kk is None: return None
        o, s = peu_pos[kk]
        h = entry(peuf, o, s)
        return kk, h

    # CPED / DOP / DPPN — modern lexica, reference tabs (filter side of §9) --
    def body_trim(h):
        m = BODY.search(h)
        b = h[m.end():] if m else h
        b = re.sub(r'</body>\s*</html>\s*$', '', b)
        b = re.sub(r'<script.*?</script>', '', b, flags=re.S)
        b = re.sub(r'<!DOCTYPE[^>]*>|<html[^>]*>|<head>.*?</head>|<link[^>]*>', '', b, flags=re.S)
        return b.strip()

    cped_idx = read_idx(os.path.join(SRC, '00-CPED', 'cped.idx'))
    cped_pos = {w.lstrip('﻿'): (o, s) for w, o, s in cped_idx}
    cpedf = ensure_dict(os.path.join(SRC, '00-CPED', 'cped'))
    def cped_get(k):
        for kk in (k, k.replace('ṃ', 'ṁ')):
            if kk in cped_pos:
                o, s = cped_pos[kk]; return entry(cpedf, o, s)
        return None

    dop_idx = read_idx(os.path.join(SRC, '02-DOP', 'cone.idx'))
    dop_syn = collections.defaultdict(list)          # plain form → all homonyms
    syn_raw = open(os.path.join(SRC, '02-DOP', 'cone.syn'), 'rb').read()
    i = 0
    while i < len(syn_raw):
        j = syn_raw.index(b'\0', i)
        w = syn_raw[i:j].decode('utf-8')
        n = struct.unpack('>I', syn_raw[j+1:j+5])[0]
        dop_syn[w].append(n); i = j + 5
    dop_pos = {w: (o, s) for w, o, s in dop_idx}
    dopf = ensure_dict(os.path.join(SRC, '02-DOP', 'cone'))
    def dop_get(k):
        ns = dop_syn.get(k) or dop_syn.get(k.replace('ṃ', 'ṁ'))
        if ns is None:
            for kk in (k, k.replace('ṃ', 'ṁ')):
                if kk in dop_pos:
                    o, s = dop_pos[kk]; return [body_trim(entry(dopf, o, s))]
            return None
        out = []
        for n in ns:
            w, o, s = dop_idx[n]; out.append(body_trim(entry(dopf, o, s)))
        return out

    # DPPN from digitalpalidictionary/other-dictionaries v1.0.8 (13,642 entries;
    # the local StarDict PPN carries only 1,367 — superseded)
    ppn = collections.defaultdict(list)
    ppn_path = os.path.join(SRC, 'dppn', 'DPPN.json')
    if os.path.exists(ppn_path):
        NAME_B = re.compile(r'<b>(.*?)</b>')
        for row in json.load(open(ppn_path)):
            m = NAME_B.search(row.get('name', ''))
            if not m: continue
            key = re.sub(r'<[^>]+>', '', m.group(1)).strip().strip('.').lower()
            if key: ppn[key].append(row['name'] + row['entry'])
    print(f'CPED {len(cped_pos)} · DOP {len(dop_idx)} idx / {len(dop_syn)} syn · DPPN {len(ppn)} names')

    # Burmese Abhidhāna (pm12e.csv): roman headword → rows -----------------
    # Citation transcoding: the abbreviations are a CLOSED SET and the digits
    # are deterministic (incl. ၎ standing for 4 in digit runs, as in ၎၇၅=475).
    # Only confidently-identified abbreviations are romanised; an unknown head
    # keeps its Burmese form with digits converted — transcoding, not
    # translation, and never a guess (principle 2).
    BUR_ABBR = {
        'တိပိ': 'Tipi',        'ဓာန်': 'Dhān',       'ဋီ': 'ṭī',
        'ရူ': 'Rū',            'ဋ္ဌ': 'ṭṭha',        'ကစ္စည်း': 'Kacc',
        'နီတိ': 'Nīti',        'သုတ္တ': 'Sutta',     'ဓာတု': 'Dhātu',
        'ဓာတွတ္ထ': 'Dhātvattha', 'မောဂ်': 'Mog',     'ဏွာဒိ': 'Ṇvādi',
        'နိရုတ္တိ': 'Nirutti',  'သဒ္ဒါ': 'Sadd',      'ပဒ': 'Pada',
        'နှာ': 'p.',           'သာရတ္ထ': 'Sāratth',  'မဏိမဉ္ဇူ': 'Maṇimañjū',
        'ဝိဘာဝိနီ': 'Vibhāvinī', 'အဘိ': 'Abhi',      '၎': '〃',
        'ဓာ': 'Dhā',
        # Burmese-script Pāḷi titles transliterate deterministically (§3):
        'ဝိ': 'Vi',   'ဒီ': 'Dī',   'မ': 'Ma',    'သံ': 'Saṁ',  'အံ': 'Aṁ',
        'ခု': 'Khu',  'ပဋိသံ': 'Paṭisaṁ', 'ဓမ္မ': 'Dhamma', 'နေတ္တိ': 'Netti',
        'ဝိသုဒ္ဓိ': 'Visuddhi', 'သီ': 'Sī', 'ဇာ': 'Jā',
    }
    # ၎ stands for 4 and the LETTER ဝ (wa) for 0 inside digit runs — both
    # observed in the source (ရူ၊နှာ။၎ဝ၇ = Rū p. 407); deterministic once known.
    BDIG = str.maketrans('၀၁၂၃၄၅၆၇၈၉၎ဝ', '0123456789 40'.replace(' ', ''))
    # A digit run: real digits, ၎ (=4), and letter-ဝ as zero — but ဝ only when
    # NOT carrying a vowel/medial sign (ဝိ… is a word, ၎ဝ၇ is 407), and every
    # run must contain at least one true digit.
    NUMRUN = r'(?=[၀-၉၎ဝ]*[၀-၉၎])(?:[၀-၉၎]|ဝ(?![ါ-ှ]))+'
    CITE_RE = re.compile(
        r'([က-ဿၚ-႟၎][က-ဿၚ-႟]*(?:၊(?:[က-ဿၚ-႟][က-ဿၚ-႟]*|[၀-၉၎]+))*)'
        r'[။၊]\s*(' + NUMRUN + r'(?:\s*[။၊\-]\s*' + NUMRUN + r')*)')
    def transcode_cites(text):
        out = []
        for m in CITE_RE.finditer(text or ''):
            head, num = m.group(1), m.group(2)
            parts = []
            for comp in head.split('၊'):
                if re.fullmatch(r'[၀-၉၎]+', comp):
                    parts.append(comp.translate(BDIG))
                else:
                    parts.append(BUR_ABBR.get(comp, comp))   # unknown: keep Burmese
            n = re.sub(r'\s*[။၊]\s*', '.', num).translate(BDIG)
            out.append(' '.join(parts) + ' ' + n)
        seen, ded = set(), []
        for c in out:
            if c not in seen: seen.add(c); ded.append(c)
        return ded

    abhi = collections.defaultdict(list)
    csv_path = os.path.join(SRC, 'tpp', 'legacy', 'pm12e_x', 'pm12e.csv')
    n_cited = 0
    if os.path.exists(csv_path):
        with open(csv_path, newline='', encoding='utf-8') as f:
            for row in csv.reader(f):
                if not row or not row[0]: continue
                r = [x.strip() for x in row[1:5]]
                cites = transcode_cites(r[1]) + transcode_cites(r[3])
                seen, ded = set(), []
                for c in cites:
                    if c not in seen: seen.add(c); ded.append(c)
                if ded: n_cited += 1
                abhi[row[0].strip().lower()].append(r + [ded])
    print(f'Abhidhāna (pm12e.csv): {len(abhi)} roman headwords; {n_cited} rows carry transcoded citations')

    peu_out, abhi_hits = {}, 0
    n_cped = n_dop = n_ppn = 0
    for lm in lemmas:
        rec = {}
        got = peu_get(lm)
        if got:
            kk, h = got
            rec['p'] = h
            rec['pk'] = kk
            rec['pm'] = 1 if 'Google Translate' in h else 0
        rows = abhi.get(lm.lower()) or abhi.get(lm.lower().replace('ṁ', 'ṃ'))
        if rows:
            rec['a'] = rows; abhi_hits += 1
        c = cped_get(lm)
        if c: rec['cp'] = c; n_cped += 1
        dp = dop_get(lm)
        if dp: rec['dp'] = dp; n_dop += 1
        pn = ppn.get(lm.lower()) or ppn.get(lm.lower().replace('ṃ', 'ṁ')) \
             or ppn.get(lm.lower().replace('ṁ', 'ṃ'))
        if pn: rec['pn'] = pn; n_ppn += 1
        if rec: peu_out[lm] = rec
    print(f'PEU/Abhidhāna: {len(peu_out)} lemmas with an entry ({abhi_hits} with Burmese Abhidhāna); '
          f'CPED {n_cped} · DOP {n_dop} · PPN {n_ppn}')

    # 6. glosses (step 3) keyed by candidate --------------------------------
    gl_by_cand = collections.defaultdict(list)
    gl_counts = {}
    for gv in GLOSS_VOLS:
        p = os.path.join(SRC, '_gloss', 'by_volume', f'{gv}.json')
        if not os.path.exists(p): continue
        rows = json.load(open(p)); gl_counts[gv] = len(rows)
        for r in rows:
            if r.get('citation_frame') or r.get('degenerate'): continue
            compact = {
                'l': r['lemma'], 'g': r['gloss'], 'v': r['vol'], 'o': r['ord'],
                'n': r.get('n'), 'pf': r.get('printed_first'),
                'pp': r.get('pdf_page'), 's': r.get('sutta'),
                't': 1 if r.get('truncated') else 0,
                'q': 1 if r.get('quoted_lemma') else 0,
                'sh': 1 if r.get('series_head') else 0,
                'w': r.get('words', 1),
            }
            for c in set(r.get('candidates') or [r['lemma']]):
                gl_by_cand[c].append(compact)
    print(f'glosses: {sum(gl_counts.values())} rows in {len(gl_counts)} vols; {len(gl_by_cand)} candidate keys')

    # 7. freq rows for the volume's forms -----------------------------------
    fidx = json.load(open(os.path.join(SRC, '_vocab', 'freq', 'index.json')))
    shard_names = set(fidx['shards'])
    def shard_of(form):
        f = fold(form)
        for d in range(2, max(3, len(f)) + 2):
            key = (f[:d] + '_' * d)[:d]
            if key in shard_names: return key
        return None
    by_shard = collections.defaultdict(list)
    for w in forms: by_shard[shard_of(w)].append(w)
    freq = {}
    missing_shard = by_shard.pop(None, [])
    for sh, ws in by_shard.items():
        tbl = json.load(open(os.path.join(SRC, '_vocab', 'freq', f'{sh}.json')))
        for w in ws:
            r = tbl.get(w) or tbl.get(w.lower())   # freq shards store lowercased forms
            if r: freq[w] = r
    print(f'freq rows found: {len(freq)} of {len(forms)} forms'
          + (f' ({len(missing_shard)} no shard)' if missing_shard else ''))

    # 8. emit ---------------------------------------------------------------
    # forms shards: folded 2-char prefix
    def pfx(s):
        f = fold(s); return ((f[:2]) + '__')[:2]
    forms_sh = collections.defaultdict(dict)
    for w in sorted(forms):
        nw = norm(w)
        rec = {'c': freq.get(w), 'n': forms[w]}
        hh = sorted(form2hw.get(nw, []))
        if hh: rec['hw'] = hh
        if nw in decon: rec['de'] = decon[nw]
        if nw in gram: rec['gr'] = 1          # grammar html stored per-form shard below
        forms_sh[pfx(w)][w] = rec
    # grammar html in its own shards (big)
    gram_sh = collections.defaultdict(dict)
    for w, h in gram.items(): gram_sh[pfx(w)][w] = h
    # headword shards: dpd html + peu/abhi at base-lemma level
    hw_sh = collections.defaultdict(dict)
    for h in hws:
        b = base(h)
        hw_sh[pfx(h)][h] = {'d': dpd_html[h], 'b': b}
    lem_sh = collections.defaultdict(dict)
    for lm, rec in peu_out.items(): lem_sh[pfx(lm)][lm] = rec
    gloss_sh = collections.defaultdict(dict)
    for c, rows in gl_by_cand.items(): gloss_sh[pfx(c)][c] = rows

    def dump(dirname, table):
        d = os.path.join(OUT, dirname); os.makedirs(d, exist_ok=True)
        total = 0
        for k, v in table.items():
            s = json.dumps(v, ensure_ascii=False, separators=(',', ':'))
            open(os.path.join(d, f'{k}.json'), 'w').write(s); total += len(s.encode())
        return total

    t1 = dump('forms', forms_sh)
    t2 = dump('hw', hw_sh)
    t3 = dump('lem', lem_sh)
    t4 = dump('gram', gram_sh)
    t5 = dump('gloss', gloss_sh)
    # volume + links, copied for the standalone page
    json.dump(vol, open(os.path.join(OUT, 'volume.json'), 'w'), ensure_ascii=False)
    fwd = json.load(open(os.path.join(SRC, 'site', 'reader', 'links', f'{VOL}.fwd.json')))
    json.dump(fwd, open(os.path.join(OUT, 'links.json'), 'w'), ensure_ascii=False)

    meta = {
        'vol': VOL, 'tokens': sum(forms.values()), 'types': len(forms),
        'resolved_forms': len(form2hw), 'dpd_headwords': len(hws),
        'peu_lemmas': sum(1 for r in peu_out.values() if 'p' in r),
        'abhi_lemmas': abhi_hits,
        'cped_lemmas': n_cped, 'dop_lemmas': n_dop, 'ppn_lemmas': n_ppn,
        'gloss_rows': sum(gl_counts.values()), 'gloss_vols': gl_counts,
        'bytes': {'forms': t1, 'hw': t2, 'lem': t3, 'gram': t4, 'gloss': t5},
        'sources': {
            'dpd': 'DPD GoldenDict 2026-05-01 (CC BY-NC-SA 4.0) — EVALUATION ONLY, not for release (§9)',
            'peu': 'PEU StarDict 2024-02-24, encoded by Bodhirasa — English rendering of the Abhidhāna; Google-Translate entries flagged',
            'abhidhana': 'pm12e.csv 2020-12-09, Tipitaka-Pali-Projector legacy/pm12e.zip — Burmese Abhidhāna, citations intact',
            'cped': 'Concise Pali English Dictionary (A.P. Buddhadatta) — StarDict, local GoldenDict copy',
            'dop': 'Dictionary of Pāli by Margaret Cone — StarDict, local GoldenDict copy (matches other-dictionaries dump, 37,39x entries)',
            'ppn': 'Dictionary of Pāli Proper Names (G.P. Malalasekera) — DPPN.json, digitalpalidictionary/other-dictionaries v1.0.8 (13,642 entries; local StarDict PPN had 1,367 and was superseded)',
            'glosses': 'OSBCT _gloss step 3 (the edition itself)',
            'freq': 'OSBCT _vocab step 1',
        },
    }
    json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'), indent=1)
    print(json.dumps(meta, indent=1)[:1200])

if __name__ == '__main__':
    main()
