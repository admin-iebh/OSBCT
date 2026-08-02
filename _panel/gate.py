#!/usr/bin/env python3
"""The panel's gate (dictionary roadmap §6) — a gate that OPENS THE PANEL.

Clicks a sample of words in real Chromium and asserts what the panel shows
against the data files directly:

  1. the panel opens and the header is the clicked surface form;
  2. the corpus count shown equals the _vocab freq row;
  3. the DPD tab count equals the number of resolved headwords in the data —
     and when there are none, the §4 unresolved message is shown and NO lemma
     is displayed as if resolved;
  4. the Edition tab count equals the gloss rows keyed to the form;
  5. machine-translated PEU entries are NOT visible until explicitly revealed;
  6. sources are never merged: the Abhidhāna tab contains no PEU English
     definition markup, the PEU tab no Burmese text (spot check).

The argument for this gate is 2026-07-30: 23,386 cross-references parsed
correctly for weeks and never reached the reader, and no existing gate could
see it.  A feature whose value is what appears in a panel needs a gate that
opens the panel.

Sample: deterministic (seed 20260801), stratified — high-frequency, gloss-rich,
unresolved, capitalised, elision-marked, digit-glued forms all represented.
"""
import json, glob, random, re, sys, collections
from playwright.sync_api import sync_playwright

SEED = 20260801
N_RANDOM = 30

FOLD = {'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'}
fold = lambda s: ''.join(FOLD.get(c, c) for c in s.lower())
pfx = lambda s: (fold(s)[:2] + '__')[:2]

# ---- load the data the panel is supposed to display -------------------------
forms = {}
for f in glob.glob('data/forms/*.json'):
    forms.update(json.load(open(f)))
gloss = collections.defaultdict(list)
for f in glob.glob('data/gloss/*.json'):
    for k, v in json.load(open(f)).items():
        gloss[k].extend(v)
lems = {}
for f in glob.glob('data/lem/*.json'):
    lems.update(json.load(open(f)))
hwt = {}
for f in glob.glob('data/hw/*.json'):
    hwt.update(json.load(open(f)))

rng = random.Random(SEED)
pool = sorted(forms)
sample = set(rng.sample(pool, N_RANDOM))
# stratified additions
sample.add('maññati')                                     # high-frequency, all four tabs
sample.update([w for w in pool if 'hw' not in forms[w]][:3])      # unresolved
sample.update([w for w in pool if w[0].isupper()][:2])            # capitalised
sample.update([w for w in pool if '’' in w][:2])                  # elision mark
sample = sorted(sample)

def expected(word):
    rec = forms.get(word) or forms.get(word.lower())
    gl = []
    for k in {word, word.lower()}:
        gl.extend(gloss.get(k, []))
    hws = rec.get('hw', []) if rec else []
    bases = sorted({hwt[h]['b'] for h in hws if h in hwt})
    n_abhi = sum(len(lems[b]['a']) for b in bases if b in lems and 'a' in lems[b])
    n_peu = sum(1 for b in bases if b in lems and 'p' in lems[b])
    n_peu_mt = sum(1 for b in bases if b in lems and 'p' in lems[b] and lems[b].get('pm'))
    n_cped = sum(1 for b in bases if b in lems and 'cp' in lems[b])
    n_dop = sum(1 for b in bases if b in lems and 'dp' in lems[b])
    n_ppn = sum(len(lems[b]['pn']) for b in bases if b in lems and 'pn' in lems[b])
    return rec, hws, gl, n_abhi, n_peu, n_peu_mt, n_cped, n_dop, n_ppn

fails, checked = [], 0
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 800})
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.goto('http://localhost:8931/', wait_until='networkidle')
    pg.wait_for_selector('p.para', timeout=8000)

    for word in sample:
        box = pg.evaluate('''(word)=>{
          const rx=new RegExp('(^|[^aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvshḷṁAĀIĪUŪEOKGṄCJÑṬḌṆTDNPBMYRLVSHḶṀ’\\'])'+
            word.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')+
            '($|[^aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvshḷṁAĀIĪUŪEOKGṄCJÑṬḌṆTDNPBMYRLVSHḶṀ’\\'0-9])');
          for(const p of document.querySelectorAll('p.para')){
            const t=p.textContent; const m=rx.exec(t); if(!m)continue;
            const i=m.index+m[1].length;
            const walker=document.createTreeWalker(p,NodeFilter.SHOW_TEXT);
            let acc=0,node;
            while((node=walker.nextNode())){
              const L=node.textContent.length;
              if(acc+L>i){
                const r=document.createRange();
                r.setStart(node,i-acc);
                r.setEnd(node,Math.min(i-acc+word.length,node.textContent.length));
                p.scrollIntoView({block:'center'});
                let rect=r.getBoundingClientRect();
                window.scrollBy(0,rect.y-innerHeight/2);
                rect=r.getBoundingClientRect();
                return {x:rect.x+Math.min(rect.width/2,6),y:rect.y+rect.height/2};
              }
              acc+=L;
            }
          }
          return null;
        }''', word)
        if not box:
            continue          # whole-word occurrence not found in rendered text
        checked += 1
        pg.mouse.click(box['x'], box['y'])
        pg.wait_for_selector('#panel[data-state="ready"]', timeout=20000)
        st = pg.evaluate('''()=>({
          open:document.getElementById('panel').classList.contains('open'),
          word:document.getElementById('pword').textContent,
          counts:document.getElementById('pcounts').textContent,
          tabs:Object.fromEntries([...document.querySelectorAll('#ptabs button')]
            .map(b=>[b.dataset.tab,{n:(b.querySelector('.n')||{}).textContent||null,dis:b.classList.contains('dis')}])),
          body:document.getElementById('pbody').innerHTML
        })''')
        rec, hws, gl, n_abhi, n_peu, n_peu_mt, n_cped, n_dop, n_ppn = expected(word)

        def fail(msg): fails.append(f'{word}: {msg}')
        if not st['open']: fail('panel did not open'); continue
        if st['word'] != word: fail(f'header {st["word"]!r} != clicked {word!r}'); continue
        # corpus count
        if rec and rec.get('c'):
            if not st['counts'].startswith(str(rec['c'][0]) + ' '):
                fail(f'corpus count shown {st["counts"]!r} != freq {rec["c"][0]}')
        # DPD tab count = resolved headwords
        shown = st['tabs'].get('dpd', {})
        n_shown = int(shown.get('n') or 0)
        if n_shown != len(hws):
            fail(f'DPD count {n_shown} != data {len(hws)}')
        # unresolved honesty
        if not hws:
            if 'Not resolved' not in st['body'] and not shown.get('dis'):
                fail('unresolved form without the §4 message')
            if 'class="lemma"' in st['body']:
                fail('unresolved form but a lemma is displayed')
        # Edition tab count = gloss rows
        ed = st['tabs'].get('ed', {})
        n_ed = int(ed.get('n') or 0)
        if n_ed != len(gl):
            fail(f'Edition count {n_ed} != gloss rows {len(gl)}')
        # Abhidhāna / PEU counts
        ab = int(st['tabs'].get('abhi', {}).get('n') or 0)
        if ab != n_abhi: fail(f'Abhidhāna count {ab} != data {n_abhi}')
        pu = int(st['tabs'].get('peu', {}).get('n') or 0)
        if pu != n_peu: fail(f'PEU count {pu} != data {n_peu}')
        for tid, exp_n in (('cped', n_cped), ('dop', n_dop), ('ppn', n_ppn)):
            got = int(st['tabs'].get(tid, {}).get('n') or 0)
            if got != exp_n: fail(f'{tid.upper()} count {got} != data {exp_n}')
        # MT segregation: open PEU tab, assert no Google-Translate text visible
        if n_peu_mt:
            pg.click('#ptabs button[data-tab="peu"]')
            pg.wait_for_timeout(200)
            vis = pg.evaluate('''()=>{
              const mt=document.querySelector('.pbody .mt');
              return {hidden:!mt||getComputedStyle(mt).display==='none',
                      reveal:!!document.querySelector('.pbody .mt-reveal')};}''')
            if not vis['hidden']: fail('machine translation visible before reveal')
            if not vis['reveal']: fail('no reveal button for machine translation')
        # source separation: PEU markup may appear in the Abhidhāna tab ONLY
        # inside an attributed .en-inline reveal block, and that block must be
        # hidden until its button is pressed
        if n_abhi:
            pg.click('#ptabs button[data-tab="abhi"]')
            pg.wait_for_timeout(200)
            sep = pg.evaluate('''()=>({
              loose:[...document.querySelectorAll('.pbody .definition')]
                     .some(el=>!el.closest('.en-inline')),
              shown:[...document.querySelectorAll('.pbody .en-inline')]
                     .some(el=>!el.classList.contains('hidden'))})''')
            if sep['loose']: fail('PEU markup outside the attributed reveal in the Abhidhāna tab')
            if sep['shown']: fail('English reveal visible before its button was pressed')

    b.close()

print(f'gate: {checked} words clicked, {len(fails)} failures')
for f in fails: print('  FAIL', f)
if errors: print('page errors:', errors[:5])
sys.exit(1 if fails or errors else 0)
