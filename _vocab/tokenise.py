#!/usr/bin/env python3
"""OSBCT roadmap step 1 — vocabulary measurement.

Read-only. Reads a staged copy of site/<VOL>.json + site/reader/hide/<VOL>.json.
Writes nothing into site/.  See dictionary_roadmap.md Appendix A.
"""
import json, re, os, sys, collections, unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
MAN = json.load(open(os.path.join(ROOT, 'manifest.json')))['volumes']

# --- the Pāḷi alphabet, as romanised in THIS edition -------------------------
# Established by the character census, not assumed: the edition writes niggahīta
# as U+1E41 ṁ (there is not one U+1E43 ṃ in 75.4M characters).
PALI = set('aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvsh ḷṁ'.replace(' ', ''))
PALI |= set(c.upper() for c in PALI)
NONPALI_LATIN = set('fqxzwFQXZW')

# apparatus footnote marker: a digit glued to the end of a word.
# Same expression as pipeline/rekey_apparatus.py.
MARK = re.compile(r'([a-zāīūṁṅñṭḍṇḷ])(\d{1,2})\b')
DIGITS = re.compile(r'\d+')
# ’ is an elision mark INSIDE a word (Tāni’ssa) and a closing quote elsewhere.
# !!! THE EDITION ENCODES THAT MARK TWO WAYS: U+2019 ’ (18,817) and U+0027 '
# (208).  Accepting only the first split 199 forms apart; caught by verify.py,
# which tokenises with a regex instead of a character walk.
APOS = {'’', "'"}
WORDCHARS_JOIN = PALI | {'-'} | APOS
WORDCHARS_SPLIT = PALI | APOS


def clean(text):
    """Strip apparatus markers and remaining digits. Returns cleaned text."""
    t = MARK.sub(r'\1', text)
    t = DIGITS.sub(' ', t)
    return t


def tokens(text, hyphen='join'):
    """Yield surface tokens. hyphen='join' keeps hyphenated compounds whole;
    hyphen='split' treats the hyphen as a token boundary."""
    ok = WORDCHARS_JOIN if hyphen == 'join' else WORDCHARS_SPLIT
    buf = []
    prev = ''
    for i, ch in enumerate(text):
        if ch in ok:
            # an apostrophe only joins when flanked by letters on both sides
            if ch in APOS:
                nxt = text[i + 1] if i + 1 < len(text) else ''
                if not (prev in PALI and nxt in PALI):
                    if buf:
                        yield ''.join(buf); buf = []
                    prev = ch
                    continue
            if ch == '-':
                nxt = text[i + 1] if i + 1 < len(text) else ''
                if not (prev in PALI and nxt in PALI):
                    if buf:
                        yield ''.join(buf); buf = []
                    prev = ch
                    continue
            buf.append(ch)
        else:
            if buf:
                yield ''.join(buf); buf = []
        prev = ch
    if buf:
        yield ''.join(buf)


ALPHA_TOK = re.compile(r'[A-Za-zĀāĪīŪūṀṁṄṅÑñṬṭḌḍṆṇḶḷ]+')


def alpha_fraction(text):
    """Share of adjacent token pairs in non-decreasing alphabetical order.
    A printed word index scores ~1.0; running prose ~0.5.  The gate for
    Appendix A.1's 'printed word index inside the body' trap."""
    toks = [x.lower() for x in ALPHA_TOK.findall(text)]
    if len(toks) < 200:
        return None
    inc = sum(1 for a, b in zip(toks, toks[1:]) if a <= b)
    return inc / (len(toks) - 1)


def main():
    out = {}
    freq = {'join': collections.Counter(), 'split': collections.Counter()}
    freq_layer = {}
    per_vol = {}
    hidden_freq = collections.Counter()
    heading_freq = collections.Counter()
    charcensus = collections.Counter()
    defects = []           # non-Pāḷi Latin letters, with context
    alpha_max = []         # word-index gate
    cased = collections.Counter()
    apos_tokens = collections.Counter()

    for vol in sorted(MAN):
        layer = MAN[vol]['layer']
        d = json.load(open(os.path.join(ROOT, 'vol', vol + '.json')))
        hp = os.path.join(ROOT, 'hide', vol + '.json')
        hide = json.load(open(hp)) if os.path.exists(hp) else {}
        hide = {int(k) for k in hide}
        fl = freq_layer.setdefault(layer, {'join': collections.Counter(),
                                           'split': collections.Counter()})
        vstat = {'layer': layer, 'paras': len(d['paragraphs']),
                 'hidden_paras': 0, 'chars': 0,
                 'tok_join': 0, 'tok_split': 0, 'hidden_tok': 0,
                 'heading_tok': 0}
        ghost = sorted(i for i in hide if i >= len(d['paragraphs']))
        if ghost:
            vstat['hide_points_at_nothing'] = ghost

        for i, p in enumerate(d['paragraphs']):
            raw = p['text']
            vstat['chars'] += len(raw)
            charcensus.update(raw)
            af = alpha_fraction(raw)
            if af is not None:
                alpha_max.append((af, len(raw), vol, i, p.get('n')))
            for m in re.finditer('[' + ''.join(NONPALI_LATIN) + ']', raw):
                defects.append({'vol': vol, 'ord': i, 'n': p.get('n'),
                                'char': m.group(0), 'printed': p.get('printed'),
                                'context': raw[max(0, m.start() - 45):m.start() + 45]})
            t = clean(raw)
            tj = list(tokens(t, 'join'))
            ts = list(tokens(t, 'split'))
            if i in hide:
                vstat['hidden_paras'] += 1
                vstat['hidden_tok'] += len(tj)
                hidden_freq.update(x.lower() for x in tj)
                continue
            vstat['tok_join'] += len(tj)
            vstat['tok_split'] += len(ts)
            for x in tj:
                lx = x.lower()
                freq['join'][lx] += 1
                fl['join'][lx] += 1
                if x != lx:
                    cased[lx] += 1
                if '’' in x or "'" in x:
                    apos_tokens[lx] += 1
            for x in ts:
                lx = x.lower()
                freq['split'][lx] += 1
                fl['split'][lx] += 1

        for h in d.get('headings', []):
            ht = h.get('title') or ''
            hts = list(tokens(clean(ht), 'join'))
            vstat['heading_tok'] += len(hts)
            heading_freq.update(x.lower() for x in hts)

        per_vol[vol] = vstat
        print('.', end='', flush=True)
    print()

    out['per_vol'] = per_vol
    out['defects'] = defects
    alpha_max.sort(reverse=True)
    out['alpha_gate_top'] = alpha_max[:10]
    out['charcensus'] = {f'U+{ord(c):04X}': n for c, n in charcensus.most_common()}
    json.dump(out, open(os.path.join(ROOT, 'stats_raw.json'), 'w'), ensure_ascii=False)

    for name, ctr in [('freq_join', freq['join']), ('freq_split', freq['split']),
                      ('freq_hidden', hidden_freq), ('freq_headings', heading_freq),
                      ('freq_cased', cased), ('freq_apos', apos_tokens)]:
        json.dump(dict(ctr), open(os.path.join(ROOT, name + '.json'), 'w'),
                  ensure_ascii=False)
    for layer, fl in freq_layer.items():
        for variant in ('join', 'split'):
            json.dump(dict(fl[variant]),
                      open(os.path.join(ROOT, f'freq_layer_{layer}_{variant}.json'), 'w'),
                      ensure_ascii=False)
    print('written')


if __name__ == '__main__':
    main()
