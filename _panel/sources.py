#!/usr/bin/env python3
"""Dictionary source readers, factored out of `build_panel_data.py` VERBATIM.

Not a second implementation: this is the same code the prototype build has been
running behind a gate since 2026-08-01, moved into a module so `build_eval.py`
can use it without either copying it or re-deriving it.  `build_panel_data.py`
is left untouched -- it is committed and working, and its pilot build is still
the comparison surface.

StarDict layout, for anyone reading this cold:
  <name>.idx      headword \0 offset(4) size(4)   -- the entries, in order
  <name>.syn.dz   variant  \0 index(4)            -- inflected/alternate forms
  <name>.dict.dz  gzip of the concatenated entry bodies
"""
import json, re, os, sys, gzip, struct, csv, collections

FOLD = {'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'}
def fold(s):
    return ''.join(FOLD.get(c, c) for c in s.lower())

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

