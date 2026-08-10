#!/usr/bin/env python3
"""The Abhidhāna's citation transcoding, shared by the two builds that read
`pm12e.csv`.

THIS IS A COPY OF `build_eval.py`'s BLOCK, AND THE COPY IS DELIBERATE.
`build_eval.py` computes these tables at module scope, below a DPD index read
that needs the 889 MB GoldenDict build present; importing it to reach one
regex would make `build_own.py` depend on DPD, which is the exact inversion
`claude/dpd_gates_the_abhidhana.md` is about.  Copying is the lesser evil, but
a copy that drifts is worse than either — so the two are held together by a
gate, not by good intentions: `pipeline/check_hw_agrees_with_lem.py` compares
every Abhidhāna row this module produces against the rows already sitting in
`stores/lookup_eval/lem/`, which `build_eval.py` wrote.  If the transcodings
ever diverge, that gate says so on the next run.

Citation transcoding is build_panel_data.py's, unchanged: the abbreviations are
a closed set, the Burmese digits deterministic (incl. ၎ for 4 and letter-ဝ for 0
inside digit runs), and an abbreviation without a settled reading is LEFT IN
BURMESE rather than guessed (principle 2).
"""
import re

BUR_ABBR = {
    'တိပိ': 'Tipi', 'ဓာန်': 'Dhān', 'ဋီ': 'ṭī', 'ရူ': 'Rū', 'ဋ္ဌ': 'ṭṭha',
    'ကစ္စည်း': 'Kacc', 'နီတိ': 'Nīti', 'သုတ္တ': 'Sutta', 'ဓာတု': 'Dhātu',
    'ဓာတွတ္ထ': 'Dhātvattha', 'မောဂ်': 'Mog', 'ဏွာဒိ': 'Ṇvādi',
    'နိရုတ္တိ': 'Nirutti', 'သဒ္ဒါ': 'Sadd', 'ပဒ': 'Pada', 'နှာ': 'p.',
    'သာရတ္ထ': 'Sāratth', 'မဏိမဉ္ဇူ': 'Maṇimañjū', 'ဝိဘာဝိနီ': 'Vibhāvinī',
    'အဘိ': 'Abhi', '၎': '〃', 'ဓာ': 'Dhā', 'ဝိ': 'Vi', 'ဒီ': 'Dī', 'မ': 'Ma',
    'သံ': 'Saṁ', 'အံ': 'Aṁ', 'ခု': 'Khu', 'ပဋိသံ': 'Paṭisaṁ', 'ဓမ္မ': 'Dhamma',
    'နေတ္တိ': 'Netti', 'ဝိသုဒ္ဓိ': 'Visuddhi', 'သီ': 'Sī', 'ဇာ': 'Jā',
}
BDIG = str.maketrans('၀၁၂၃၄၅၆၇၈၉၎ဝ', '012345678940')
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
                parts.append(BUR_ABBR.get(comp, comp))
        n = re.sub(r'\s*[။၊]\s*', '.', num).translate(BDIG)
        out.append(' '.join(parts) + ' ' + n)
    seen, ded = set(), []
    for c in out:
        if c not in seen:
            seen.add(c); ded.append(c)
    return ded


def row_value(row):
    """One `pm12e.csv` row → the value shape the panel already renders, exactly
    as `build_eval.py:265` builds it: columns 1–4 stripped, plus the deduped
    transcoded citations drawn from columns 2 and 4."""
    r = [x.strip() for x in row[1:5]]
    cites = transcode_cites(r[1]) + transcode_cites(r[3])
    seen, ded = set(), []
    for c in cites:
        if c not in seen:
            seen.add(c); ded.append(c)
    return r + [ded]
