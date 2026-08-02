#!/usr/bin/env python3
"""Draw a stratified hand-judging sheet from promotion_population.json.

THE UNIT OF JUDGEMENT IS THE ROW, not the click.  The panel's claim is made
per row — "this row is here because the phrase it glosses stands in front of
you" — so that is what gets judged, as the 60 proximity verdicts did.

Stratified over the three BOXED groups, and inside `here`/`word` over the
gloss-row band, because the band is where the earlier measurement found the
behaviour changed.  `prox` is too rare (58 firing clicks in 2,000) to stratify
further; it is sampled whole.

Writes promotion_sheet.html — self-contained, judgements export as JSON.
"""
import json, os, random, collections, html, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SEED = 20260803
N_PER_GROUP = 20
PROX = 'In the commentary on this paragraph'
HERE = 'On a phrase that stands in this paragraph'
WORD = 'On the word itself'
WHY = {
    PROX: 'shown first because the phrase the edition glosses stands in this '
          'paragraph — checked, not guessed',
    HERE: 'shown first because the phrase the edition glosses stands in this '
          'paragraph — checked, not guessed',
    WORD: 'the edition glosses this form on its own, wherever it stands',
}
CLAIM = {
    PROX: ('This row sits in the commentary paragraph the edition’s link map ties to '
           'the paragraph on screen, AND the phrase it glosses stands in that paragraph.'),
    HERE: ('The phrase this row glosses — more than one word — stands in the '
           'paragraph on screen. Nothing is claimed about where the row sits.'),
    WORD: ('The edition glosses this single form on its own. True wherever the form '
           'stands, and said that way.'),
}
SCHEME = [
    ('A', 'the claim holds and the row helps here',
     'the promotion is right: this really is the edition explaining what is in front of the reader'),
    ('B', 'the claim holds but the row is beside the point here',
     'technically true — the phrase does stand here, or the edition does gloss this form — '
     'but it explains a different phrase, a different sense, or says almost nothing'),
    ('C', 'the claim does not hold',
     'the promotion is wrong: the phrase is not really here (a spurious stem match), '
     'or the row is not the commentary on this paragraph at all'),
]


def band(n):
    return ('1' if n == 1 else '2-3' if n <= 3 else '4-10' if n <= 10
            else '11-50' if n <= 50 else '>50')


def mark(para, word):
    """The paragraph with the clicked word marked, as the reader saw it."""
    rx = re.compile('(^|[^a-zāīūṁṅñṭḍṇḷ’])(' + re.escape(word) +
                    ')($|[^a-zāīūṁṅñṭḍṇḷ’0-9])', re.I)
    m = rx.search(para)
    if not m:
        return html.escape(para)
    a, b = m.start(2), m.end(2)
    return (html.escape(para[:a]) + '<mark>' + html.escape(para[a:b]) + '</mark>'
            + html.escape(para[b:]))


def main():
    rng = random.Random(SEED)
    recs = json.load(open(os.path.join(ROOT, 'promotion_population.json')))

    # ---- build the pool of judgeable (click, group, row) triples -------------
    pool = collections.defaultdict(list)
    for ri, r in enumerate(recs):
        for g in r['groups']:
            if g['label'] not in (PROX, HERE, WORD):
                continue
            for rowi, row in enumerate(g['rows']):
                pool[g['label']].append((ri, g['label'], rowi))

    picked = []
    for label in (PROX, HERE, WORD):
        cand = pool[label]
        if label == PROX:
            rng.shuffle(cand)
            take = cand[:N_PER_GROUP]
        else:
            # stratify over the band, evenly, then top up from the whole pool
            by = collections.defaultdict(list)
            for t in cand:
                by[band(recs[t[0]]['_n'])].append(t)
            take, bands = [], ['1', '2-3', '4-10', '11-50', '>50']
            per = N_PER_GROUP // len(bands)
            for b in bands:
                p = by[b][:]
                rng.shuffle(p)
                take += p[:per]
            leftover = [t for t in cand if t not in set(take)]
            rng.shuffle(leftover)
            take += leftover[:N_PER_GROUP - len(take)]
        picked += take
        print(f'{label[:34]:36s} pool {len(cand):6,} rows  → sampled {len(take)}')

    rng.shuffle(picked)          # judge them blind to the group ordering

    # ---- render -------------------------------------------------------------
    items = []
    for k, (ri, label, rowi) in enumerate(picked):
        r = recs[ri]
        g = [x for x in r['groups'] if x['label'] == label][0]
        row = g['rows'][rowi]
        others = [x for i, x in enumerate(g['rows']) if i != rowi]
        items.append({
            'i': k, 'label': label, 'vol': r['vol'], 'word': r['word'],
            'n': r['_n'], 'band': band(r['_n']), 'pid': r['pid'],
            'para_html': mark(r['para'], r['word']),
            'row': row, 'n_group': len(g['rows']),
            'others': others[:6], 'n_others': len(others),
        })

    js = json.dumps(items, ensure_ascii=False)
    scheme_html = ''.join(
        f'<div class="sc"><b>{c}</b> — {html.escape(t)}<span>{html.escape(d)}</span></div>'
        for c, t, d in SCHEME)
    claim_js = json.dumps(CLAIM, ensure_ascii=False)
    why_js = json.dumps(WHY, ensure_ascii=False)

    out = TEMPLATE.replace('/*ITEMS*/', js).replace('/*CLAIMS*/', claim_js) \
                  .replace('/*WHYS*/', why_js).replace('<!--SCHEME-->', scheme_html)
    assert '/*ITEMS*/' not in out and '<!--SCHEME-->' not in out, 'template substitution failed'
    p = os.path.join(ROOT, 'promotion_sheet.html')
    open(p, 'w').write(out)
    print(f'\nwrote {p}  ({len(items)} items, {len(out)/1024:.0f} kB)')


TEMPLATE = r"""<!doctype html>
<html lang="en"><meta charset="utf-8">
<title>OSBCT — judging the Gloss tab's boxed top group</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#faf8f4;--fg:#1c1a17;--mut:#6b6459;--line:#ded7cb;--app:#fff;
      --canon:#8a6d3b;--comm:#3b6b8a;--acc:#7a3b8a;--ok:#2f6b3f;--bad:#8a3b3b}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:15px/1.55 Inter,system-ui,-apple-system,sans-serif}
header{position:sticky;top:0;z-index:9;background:var(--bg);
  border-bottom:1px solid var(--line);padding:14px 22px}
h1{font-size:17px;margin:0 0 4px}
.sub{font-size:12.5px;color:var(--mut);margin:0}
.bar{display:flex;gap:14px;align-items:center;margin-top:9px;flex-wrap:wrap}
button{font:600 13px Inter,system-ui,sans-serif;background:var(--app);
  border:1px solid var(--line);border-radius:7px;padding:7px 13px;cursor:pointer;color:var(--fg)}
button:hover{border-color:var(--mut)}
button.pri{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.prog{font-size:12.5px;color:var(--mut)}
main{max-width:900px;margin:0 auto;padding:20px 22px 120px}
details.help{background:var(--app);border:1px solid var(--line);border-radius:10px;
  padding:12px 15px;margin:0 0 20px}
details.help summary{cursor:pointer;font-weight:600;font-size:13.5px}
.sc{margin:9px 0;font-size:13.5px}
.sc b{display:inline-block;min-width:17px}
.sc span{display:block;color:var(--mut);font-size:12.5px;margin-left:17px}
.item{background:var(--app);border:1px solid var(--line);border-radius:12px;
  padding:16px 18px;margin:0 0 16px}
.item.done{border-color:var(--ok)}
.hd{display:flex;justify-content:space-between;gap:12px;align-items:baseline;
  font-size:12px;color:var(--mut);margin-bottom:9px;flex-wrap:wrap}
.hd .n{font-weight:700;color:var(--fg);font-size:14px}
.tag{font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;
  border:1px solid var(--line);border-radius:20px;padding:2px 9px}
.tag.prox{color:var(--comm);border-color:var(--comm)}
.tag.here{color:var(--acc);border-color:var(--acc)}
.tag.word{color:var(--canon);border-color:var(--canon)}
.para{font-family:"Gentium Plus",Georgia,serif;font-size:16px;line-height:1.7;
  background:var(--bg);border-radius:8px;padding:11px 13px;margin:0 0 12px}
.para mark{background:#ffe9a8;padding:0 2px;border-radius:3px;font-weight:700}
.claim{font-size:12.5px;color:var(--mut);border-left:2px solid var(--line);
  padding:2px 0 2px 10px;margin:0 0 12px}
.claim b{color:var(--fg)}
.row{border:1px solid var(--line);border-left:3px solid var(--comm);
  border-radius:8px;padding:10px 12px;background:var(--bg)}
.row.wordgrp{border-left-color:var(--canon)}
.lem{font-family:"Gentium Plus",Georgia,serif;font-weight:700;font-size:15.5px}
.gl{font-family:"Gentium Plus",Georgia,serif;font-size:15px;margin-top:3px}
.cite{font-size:11.5px;color:var(--mut);margin-top:5px}
.why{font-size:11.5px;color:var(--mut);font-style:italic;margin:5px 0 0}
details.more{margin-top:9px;font-size:12.5px}
details.more summary{cursor:pointer;color:var(--mut)}
details.more .row{margin-top:7px;border-left-color:var(--line)}
.judge{display:flex;gap:7px;margin-top:13px;flex-wrap:wrap}
.judge label{flex:1;min-width:150px;border:1px solid var(--line);border-radius:8px;
  padding:8px 11px;cursor:pointer;font-size:13px;background:var(--bg)}
.judge input{margin-right:6px}
.judge label:has(input:checked){border-color:var(--fg);background:var(--app);font-weight:600}
.judge label.A:has(input:checked){border-color:var(--ok);color:var(--ok)}
.judge label.C:has(input:checked){border-color:var(--bad);color:var(--bad)}
textarea{width:100%;margin-top:9px;font:13px Inter,system-ui,sans-serif;
  border:1px solid var(--line);border-radius:8px;padding:8px 10px;resize:vertical;
  background:var(--bg);color:var(--fg)}
footer{position:fixed;bottom:0;left:0;right:0;background:var(--app);
  border-top:1px solid var(--line);padding:11px 22px;display:flex;gap:12px;
  align-items:center;justify-content:center}
#out{position:fixed;inset:5% 8%;background:var(--app);border:1px solid var(--line);
  border-radius:12px;padding:18px;display:none;z-index:20;flex-direction:column}
#out textarea{flex:1;font:11.5px ui-monospace,SFMono-Regular,Menlo,monospace}
</style>
<header>
  <h1>Judging the Gloss tab's boxed top group</h1>
  <p class="sub">60 rows the <b>shipped</b> promotion rule actually promotes, sampled from
     2,000 clicks driven through the live panel in Chromium. One row per item.</p>
  <div class="bar">
    <span class="prog" id="prog">0 / 60 judged</span>
    <button onclick="jump()">Next unjudged</button>
    <button class="pri" onclick="exportJ()">Export verdicts</button>
  </div>
</header>
<main>
<details class="help" open>
  <summary>How to judge</summary>
  <p style="font-size:13.5px;margin:10px 0 4px">Each item shows a canon paragraph as the
  reader saw it, with the word they clicked marked. Below it is <b>one row the panel put in
  a box at the top</b>, and the claim the panel made in putting it there. Judge whether that
  claim earns the row its place.</p>
  <!--SCHEME-->
  <p style="font-size:12.5px;color:var(--mut);margin:10px 0 0">Notes are worth more than the
  letter — especially where you hesitate. Judgements save in this page as you go; press
  <b>Export verdicts</b> at the end.</p>
</details>
<div id="list"></div>
</main>
<footer>
  <span class="prog" id="prog2">0 / 60</span>
  <button onclick="jump()">Next unjudged</button>
  <button class="pri" onclick="exportJ()">Export verdicts</button>
</footer>
<div id="out">
  <b style="margin-bottom:8px">Verdicts — copy this back to Claude</b>
  <textarea id="outt" readonly></textarea>
  <div style="margin-top:10px;display:flex;gap:9px">
    <button class="pri" onclick="navigator.clipboard.writeText(document.getElementById('outt').value)">Copy</button>
    <button onclick="document.getElementById('out').style.display='none'">Close</button>
  </div>
</div>
<script>
const ITEMS = /*ITEMS*/;
const CLAIM = /*CLAIMS*/;
const WHY   = /*WHYS*/;
const V = {};
const KEY = {'In the commentary on this paragraph':'prox',
             'On a phrase that stands in this paragraph':'here',
             'On the word itself':'word'};
const esc = s => String(s).replace(/[&<>"]/g, c =>
  ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function rowHtml(r, cls){
  return '<div class="row '+cls+'"><div class="lem">'+esc(r.l)+'</div>'
    + '<div class="gl">'+esc(r.g)+'</div>'
    + '<div class="cite">'+esc(r.cite)+'</div></div>';
}
function render(){
  document.getElementById('list').innerHTML = ITEMS.map(it => {
    const k = KEY[it.label];
    let h = '<div class="item" id="it'+it.i+'">';
    h += '<div class="hd"><span class="n">#'+(it.i+1)+'</span>'
       + '<span class="tag '+k+'">'+esc(it.label)+'</span>'
       + '<span>'+esc(it.vol)+' · clicked <b>'+esc(it.word)+'</b> · '
       + it.n.toLocaleString()+' gloss rows in the edition (band '+esc(it.band)+')'
       + ' · this group holds '+it.n_group+'</span></div>';
    h += '<div class="para">'+it.para_html+'</div>';
    h += '<div class="claim"><b>The panel’s claim:</b> '+esc(CLAIM[it.label])+'</div>';
    h += rowHtml(it.row, k==='word'?'wordgrp':'');
    h += '<div class="why">on screen this box carries: “'+esc(WHY[it.label])+'”</div>';
    if (it.n_others)
      h += '<details class="more"><summary>the other '+it.n_others
         + ' row'+(it.n_others>1?'s':'')+' in this same box</summary>'
         + it.others.map(r => rowHtml(r, k==='word'?'wordgrp':'')).join('')
         + (it.n_others > it.others.length
            ? '<div class="cite">… and '+(it.n_others-it.others.length)+' more</div>' : '')
         + '</details>';
    h += '<div class="judge">' + [['A','A — right, and helps here'],
                                  ['B','B — true but beside the point'],
                                  ['C','C — claim does not hold']]
      .map(([c,lbl]) => '<label class="'+c+'"><input type="radio" name="v'+it.i+'" value="'+c+'"'
        + ' onchange="setV('+it.i+',this.value)">'+esc(lbl)+'</label>').join('') + '</div>';
    h += '<textarea rows="2" placeholder="note — what made it right or wrong" '
       + 'oninput="setN('+it.i+',this.value)"></textarea>';
    return h + '</div>';
  }).join('');
  restore();
}
function setV(i,v){ (V[i]=V[i]||{}).v=v; save(); prog();
  document.getElementById('it'+i).classList.add('done'); }
function setN(i,n){ (V[i]=V[i]||{}).n=n; save(); }
function save(){ try{ sessionStorage.setItem('osbct-promo-verdicts', JSON.stringify(V)); }catch(e){} }
function restore(){
  let s=null; try{ s=sessionStorage.getItem('osbct-promo-verdicts'); }catch(e){}
  if(!s) return prog();
  Object.assign(V, JSON.parse(s));
  for(const i in V){
    if(V[i].v){ const el=document.querySelector('input[name=v'+i+'][value="'+V[i].v+'"]');
      if(el){ el.checked=true; document.getElementById('it'+i).classList.add('done'); } }
    if(V[i].n){ const t=document.querySelector('#it'+i+' textarea'); if(t) t.value=V[i].n; }
  }
  prog();
}
function prog(){
  const n = Object.values(V).filter(x=>x.v).length;
  document.getElementById('prog').textContent  = n+' / '+ITEMS.length+' judged';
  document.getElementById('prog2').textContent = n+' / '+ITEMS.length;
}
function jump(){
  const it = ITEMS.find(x => !(V[x.i]||{}).v);
  if(it) document.getElementById('it'+it.i).scrollIntoView({block:'center',behavior:'smooth'});
}
function exportJ(){
  const out = {note:'Hand verdicts on the SHIPPED promotion rule, _panel/promotion_sheet.html',
               scheme:{A:'the claim holds and the row helps here',
                       B:'the claim holds but the row is beside the point here',
                       C:'the claim does not hold'},
               verdicts:{}};
  ITEMS.forEach(it => { const v=V[it.i];
    if(v&&v.v) out.verdicts[it.i]=[v.v, v.n||'', KEY[it.label], it.vol, it.word]; });
  document.getElementById('outt').value = JSON.stringify(out, null, 1);
  document.getElementById('out').style.display = 'flex';
}
render();
</script>
</html>
"""


if __name__ == '__main__':
    main()
