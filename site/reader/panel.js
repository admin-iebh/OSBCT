/* OSBCT word-lookup panel — reader2 integration, BEHIND A FLAG.
   ---------------------------------------------------------------------------
   Enable with `?wl=1` in the URL, or once with localStorage['osbct-wl']='1'.
   `?wl=0` turns it off again.  Nothing runs, nothing is fetched and no event
   is bound while the flag is off, so a reader who has not asked for it meets
   exactly the reader that shipped before.

   WHAT IT SHOWS, AND WHOSE VOICE IT SPEAKS IN (§9)
     Edition   — DEFAULT.  The edition's own glosses: the aṭṭhakathā and ṭīkā
                 explaining the word, from roadmap step 3.
     PED       — the PTS Pali-English Dictionary 1921–25, public domain.  A
                 reference, marked as one; not the panel's voice.
     header    — corpus occurrence counts from roadmap step 1.
   Abhidhāna, PEU and PPN are NOT here.  The prototype has them and they are
   the better lexical authority; they wait on the permissions recorded in
   claude/panel_prototype_built.md.  DPD is not here either and will not be:
   it is a build-time filter, never a voice (§9).

   HOW THE EDITION TAB ORDERS ITSELF — measured, not assumed (2026-08-02)
   The obvious ranking was proximity: put first the gloss sitting in the
   commentary paragraph the link map ties to the canon paragraph on screen.
   Measured over all 40 canon volumes and all 187,248 gloss rows:

       a proximity row exists for   6.5% of clicks that get any gloss
       and when it exists it is really about this passage 57% of the time
       (Dīgha 84 · Khuddaka 80 · Majjhima 79 · Vinaya 63 · Aṅguttara 61 ·
        Saṁyutta 39 · Abhidhamma 36 — the Abhidhamma volumes share one
        Pañcapakaraṇa commentary and their paragraph numbers collide)

   So proximity is NOT the ranking.  The tab LEADS WITH THE OCCURRENCES and
   says how many there are.  What earns a place at the top is a checkable
   claim, not a positional guess: a row is promoted only when the phrase it
   glosses — the words the edition printed in bold — actually stands in the
   paragraph on screen.  `row.k` carries that phrase's stems; the check runs
   here, at click time, against the text already rendered.  Measured, that rule
   reaches 80.9% of glossed clicks and 99.3% of the >50-row band — which was
   the band the whole exercise was about (13.3% of canon clicks).

   FOUR GROUPS, each with a criterion a reader could check for themselves:
       "in the commentary on this paragraph"   phrase present AND the row sits
                                               in the linked paragraph   3.6%
       "on a phrase that stands in this ¶"     phrase present, >1 word
       "on the word itself"                    the edition glosses this form
                                               alone — true wherever it stands,
                                               and said that way
       "all occurrences"                       the rest, in the edition's order

   Click recovery is caret-based: no per-word spans (roadmap §5).
   Chrome goes through i18n.js.  The Pāḷi never does.                        */
(function () {
'use strict';

// ---------------------------------------------------------------- the flag --
var q = new URLSearchParams(location.search);
if (q.has('wl')) {
  try { localStorage.setItem('osbct-wl', q.get('wl') === '0' ? '0' : '1'); } catch (e) {}
}
var ON = false;
try { ON = localStorage.getItem('osbct-wl') === '1'; } catch (e) {}
if (q.get('wl') === '1') ON = true;
if (q.get('wl') === '0') ON = false;
if (!ON) return;

// A SECOND FLAG FOR THE EVALUATION DICTIONARIES (?wle=1).  Every source it
// adds either has an unresolved redistribution licence (Abhidhāna, PEU, PPN)
// or is excluded by §9 as a voice however it is licensed (DPD).  They are
// worth reading and they are not the project's to publish, so they sit behind
// their own switch, off unless asked for, each banner'd where it is shown, and
// their data lives in site/lookup_eval/ which is gitignored.  ?wl=1 alone is
// still Edition + PED and nothing else.
if (q.has('wle')) {
  try { localStorage.setItem('osbct-wle', q.get('wle') === '0' ? '0' : '1'); } catch (e) {}
}
var EVAL = false;
try { EVAL = localStorage.getItem('osbct-wle') === '1'; } catch (e) {}
if (q.get('wle') === '1') EVAL = true;
if (q.get('wle') === '0') EVAL = false;

// ------------------------------------------------------------ i18n strings --
// Same shape and the same fallback discipline reader2 uses: if i18n.js has not
// loaded, a bare t() in a render path throws and takes the panel with it.
var S = {
  wl_edition:   {en: 'Edition', es: 'Edición'},
  wl_ped:       {en: 'PED', es: 'PED'},
  wl_tip_ed:    {en: 'The edition’s own glosses — aṭṭhakathā and ṭīkā',
                 es: 'Las glosas de la edición misma — aṭṭhakathā y ṭīkā'},
  wl_tip_ped:   {en: 'PTS Pali-English Dictionary (Rhys Davids & Stede, 1921–25) — public domain',
                 es: 'PTS Pali-English Dictionary (Rhys Davids y Stede, 1921–25) — dominio público'},
  wl_corpus:    {en: 'corpus', es: 'corpus'},
  wl_canon:     {en: 'canon', es: 'canon'},
  wl_comm:      {en: 'aṭṭh.', es: 'aṭṭh.'},
  wl_sub:       {en: 'ṭīkā', es: 'ṭīkā'},
  wl_loading:   {en: 'Loading…', es: 'Cargando…'},
  wl_close:     {en: 'Close', es: 'Cerrar'},
  wl_ed_src:    {en: 'The edition’s own glosses (bold lemma + -ti formula, step 3). '
                   + 'Ordered as the books stand: volume, then paragraph.',
                 es: 'Las glosas de la edición misma (lema en negrita + fórmula -ti, paso 3). '
                   + 'En el orden de los libros: volumen y luego párrafo.'},
  wl_prox:      {en: 'In the commentary on this paragraph',
                 es: 'En el comentario a este párrafo'},
  wl_here:      {en: 'On a phrase that stands in this paragraph',
                 es: 'Sobre una frase que está en este párrafo'},
  wl_word:      {en: 'On the word itself',
                 es: 'Sobre la palabra misma'},
  wl_rest:      {en: 'Other occurrences', es: 'Otras apariciones'},
  wl_checked:   {en: 'shown first because the phrase the edition glosses stands '
                   + 'in this paragraph — checked, not guessed',
                 es: 'se muestra primero porque la frase que glosa la edición está '
                   + 'en este párrafo — comprobado, no supuesto'},
  wl_why_word:  {en: 'the edition glosses this form on its own, wherever it stands',
                 es: 'la edición glosa esta forma por sí sola, dondequiera que esté'},
  wl_nogloss:   {en: 'The edition gives no gloss for this form.',
                 es: 'La edición no da ninguna glosa para esta forma.'},
  wl_noped:     {en: 'No PED entry reachable from this form.',
                 es: 'Ninguna entrada del PED es alcanzable desde esta forma.'},
  wl_ped_src:   {en: 'The Pali Text Society’s Pali-English Dictionary, T. W. Rhys Davids '
                   + '& William Stede, 1921–25 (public domain). A reference, not this '
                   + 'edition’s voice.',
                 es: 'The Pali Text Society’s Pali-English Dictionary, T. W. Rhys Davids '
                   + 'y William Stede, 1921–25 (dominio público). Una referencia, no la '
                   + 'voz de esta edición.'},
  wl_trunc:     {en: '…continues in the text (cut short by the next lemma — flagged, not patched)',
                 es: '…continúa en el texto (cortada por el lema siguiente — señalado, no corregido)'},
  wl_quoted:    {en: 'quoted', es: 'citada'},
  wl_series:    {en: '-ādi: heads a series', es: '-ādi: encabeza una serie'},
  wl_more:      {en: 'Show more', es: 'Mostrar más'},
  wl_of:        {en: 'of', es: 'de'},
  wl_pilot:     {en: 'Word lookup — in testing', es: 'Consulta de palabras — en pruebas'},
  wl_dpd:       {en: 'DPD', es: 'DPD'},
  wl_abhi:      {en: 'Abhidhāna', es: 'Abhidhāna'},
  wl_peu:       {en: 'PEU', es: 'PEU'},
  wl_cped:      {en: 'CPED', es: 'CPED'},
  wl_ppn:       {en: 'PPN', es: 'PPN'},
  wl_ny:        {en: 'Nyanatiloka', es: 'Nyanatiloka'},
  wl_vri:       {en: 'VRI', es: 'VRI'},
  wl_pwg:       {en: 'PWG', es: 'PWG'},
  wl_tpm:       {en: 'TPM', es: 'TPM'},
  wl_rt:        {en: 'Roots', es: 'Raíces'},
  wl_uhs:       {en: 'U Hau Sein', es: 'U Hau Sein'},
  wl_dict:      {en: 'Pāḷi Dictionary', es: 'Diccionario Pāḷi'},
  wl_tip_dict:  {en: 'The dictionaries aggregated at dictionary.sutta.org, plus CPED and PPN — '
                   + 'one section each, in order of authority. Reference, never the panel’s voice (§9).',
                 es: 'Los diccionarios reunidos en dictionary.sutta.org, más CPED y PPN — '
                   + 'una sección cada uno, por orden de autoridad. Referencia, nunca la voz del panel (§9).'},
  wl_jump:      {en: 'In this word:', es: 'En esta palabra:'},
  wl_nodict:    {en: 'No dictionary reached from this form.',
                 es: 'Ningún diccionario alcanzado desde esta forma.'},
  wl_tip_dpd:   {en: 'Digital Pāḷi Dictionary (Bodhirasa) — evaluation only; §9 keeps it a build-time filter, never the panel’s voice',
                 es: 'Digital Pāḷi Dictionary (Bodhirasa) — sólo evaluación; el §9 lo mantiene como filtro, nunca como voz del panel'},
  wl_tip_abhi:  {en: 'Tipiṭaka-Pāḷi-Myanmā-Abhidhāna (Ministry of Religious Affairs, Yangon) — the lexical authority (§9)',
                 es: 'Tipiṭaka-Pāḷi-Myanmā-Abhidhāna (Ministerio de Asuntos Religiosos, Yangón) — la autoridad léxica (§9)'},
  wl_tip_peu:   {en: 'PEU — the Abhidhāna’s English rendering (encoded by Bodhirasa)',
                 es: 'PEU — la versión inglesa del Abhidhāna (codificada por Bodhirasa)'},
  wl_tip_cped:  {en: 'Concise Pali-English Dictionary (A.P. Buddhadatta)',
                 es: 'Concise Pali-English Dictionary (A.P. Buddhadatta)'},
  wl_tip_ppn:   {en: 'Dictionary of Pāli Proper Names (G.P. Malalasekera)',
                 es: 'Dictionary of Pāli Proper Names (G.P. Malalasekera)'},
  wl_tip_ny:    {en: 'Buddhist Dictionary (Nyanatiloka Mahāthera) — a doctrinal glossary, not a lexicon',
                 es: 'Buddhist Dictionary (Nyanatiloka Mahāthera) — un glosario doctrinal, no un léxico'},
  wl_tip_vri:   {en: 'Pali-Dictionary, Vipassana Research Institute',
                 es: 'Pali-Dictionary, Vipassana Research Institute'},
  wl_tip_pwg:   {en: 'Pali Word Grammar from the Pali Myanmar Dictionary — Burmese, converted from Zawgyi',
                 es: 'Pali Word Grammar del Pali Myanmar Dictionary — birmano, convertido desde Zawgyi'},
  wl_tip_tpm:   {en: 'Tipiṭaka Pāḷi-Myanmar Dictionary — Burmese, converted from Zawgyi; a second copy of the Abhidhāna’s digitisation',
                 es: 'Tipiṭaka Pāḷi-Myanmar Dictionary — birmano, convertido desde Zawgyi; segunda copia de la digitalización del Abhidhāna'},
  wl_tip_rt:    {en: 'Pali Roots Dictionary (ဓာတ်အဘိဓာန်) — Burmese, converted from Zawgyi',
                 es: 'Pali Roots Dictionary (ဓာတ်အဘိဓာန်) — birmano, convertido desde Zawgyi'},
  wl_tip_uhs:   {en: 'U Hau Sein’s Pāḷi-Myanmar Dictionary — Burmese, converted from Zawgyi',
                 es: 'Diccionario Pāḷi-birmano de U Hau Sein — birmano, convertido desde Zawgyi'},
  wl_eval:      {en: 'Evaluation only — this source is not published with the edition. '
                   + 'Its redistribution licence is unconfirmed, or §9 excludes it as a voice.',
                 es: 'Sólo evaluación — esta fuente no se publica con la edición. '
                   + 'Su licencia de redistribución no está confirmada, o el §9 la excluye como voz.'},
  wl_zg:        {en: 'Burmese, transcoded from Zawgyi to Unicode and verified by character census (§3).',
                 es: 'Birmano, transcodificado de Zawgyi a Unicode y verificado por censo de caracteres (§3).'},
  wl_mt:        {en: 'machine-translated (Google) — withheld by default',
                 es: 'traducción automática (Google) — retenida por omisión'},
  wl_mt_show:   {en: 'Show the machine translation anyway',
                 es: 'Mostrar la traducción automática de todos modos'},
  wl_cites:     {en: 'Citations:', es: 'Citas:'},
  wl_cites_note:{en: '(transcoded from the Burmese; an abbreviation without a settled reading is left as printed)',
                 es: '(transcritas del birmano; una abreviatura sin lectura establecida se deja como está impresa)'},
  wl_en_btn:    {en: 'English (PEU) ⇣', es: 'Inglés (PEU) ⇣'},
  wl_en_attr:   {en: 'PEU’s English rendering of this entry. A translation, not the authority: where they differ, the Abhidhāna governs.',
                 es: 'La versión inglesa del PEU de esta entrada. Una traducción, no la autoridad: donde difieran, gobierna el Abhidhāna.'},
  wl_back:      {en: 'Back', es: 'Atrás'},
  wl_noentry:   {en: 'No entry for the resolved lemma(s).',
                 es: 'Ninguna entrada para el lema resuelto.'},
  wl_thisvol:   {en: 'this volume', es: 'este volumen'}
};
if (window.I18N) for (var k in S) if (!window.I18N[k]) window.I18N[k] = S[k];
function T(key) {
  if (window.t && window.I18N && window.I18N[key]) return window.t(key);
  var lang = 'en';
  try { lang = localStorage.getItem('osbct-lang') || 'en'; } catch (e) {}
  return (S[key] && (S[key][lang] || S[key].en)) || key;
}

// ------------------------------------------------------------------- utils --
var FOLD = {'ā':'a','ī':'i','ū':'u','ṁ':'m','ṃ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l'};
function fold(s) { return s.toLowerCase().replace(/[āīūṁṃṅñṭḍṇḷ]/g, function (c) { return FOLD[c] || c; }); }
var VOW = 'aiueo';
// the same normalisation build_lookup.py used to write row.k — they must agree
function stem(w) {
  var f = fold(w).replace(/(.)\1+/g, '$1');
  while (f && (f.slice(-1) === 'm' || f.slice(-1) === 'n' || VOW.indexOf(f.slice(-1)) >= 0))
    f = f.slice(0, -1);
  return f;
}
var PALI = 'aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvshḷṁ';
var PALISET = {}; (PALI + PALI.toUpperCase()).split('').forEach(function (c) { PALISET[c] = 1; });
var APOS = {'’': 1, "'": 1};
function esc(s) { return String(s).replace(/[&<>"]/g, function (c) {
  return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

// the shard manifest decides the shard name (adaptive prefix, see index.json)
var MAN = null;
function shardName(set, key) {
  var f = fold(key), m = MAN && MAN.shards && MAN.shards[set];
  if (!m) return (f.slice(0, 2) + '__').slice(0, 2);
  for (var d = 2; d <= 40; d++) {
    var name = (f.slice(0, d) + new Array(d + 1).join('_')).slice(0, d);
    if (m[name]) return name;
  }
  return (f.slice(0, 2) + '__').slice(0, 2);
}
function safeName(k) {
  return fold(k).split('').map(function (c) {
    return /[a-z0-9]/.test(c) ? c : '-' + c.charCodeAt(0) + '-'; }).join('');
}

var CACHE = {};
function jfetch(url) {
  if (CACHE[url]) return CACHE[url];
  return CACHE[url] = fetch(url).then(function (r) { return r.ok ? r.json() : null; })
                                .catch(function () { return null; });
}
// !!! The shard data lives at site/lookup/, and this file runs from
// site/reader/ — a bare 'lookup/…' resolves to /reader/lookup/ and every fetch
// 404s in silence, which is exactly what the first run of gate_reader.py found:
// the panel opened, the header was right, and every count was empty.  Same '../'
// convention reader2 already uses for '../<VOL>.json'.
var BASE = '../lookup/';
var EBASE = '../lookup_eval/';
// The manifest names the shards; without it shardName() guesses a 2-character
// prefix that mostly does not exist.  Nothing may look anything up until it has
// landed, so every lookup waits on the same promise.
var MANP = null, EMAN = null, EMANP = null;
function manifest() {
  if (!MANP) MANP = jfetch(BASE + 'index.json').then(function (m) { MAN = m; return m; });
  return MANP;
}
function emanifest() {
  if (!EMANP) EMANP = jfetch(EBASE + 'index.json').then(function (m) { EMAN = m; return m; });
  return EMANP;
}
function eShardName(set, key) {
  var f = fold(key), m = EMAN && EMAN.shards && EMAN.shards[set];
  if (!m) return null;
  for (var d = 2; d <= 40; d++) {
    var name = (f.slice(0, d) + new Array(d + 1).join('_')).slice(0, d);
    if (m[name]) return name;
  }
  return null;
}
function look(set, key) {
  return manifest().then(function () {
    return jfetch(BASE + set + '/' + shardName(set, key) + '.json');
  }).then(function (o) {
    return o ? (o[key] !== undefined ? o[key] : o[key.toLowerCase()]) : null;
  });
}
// the evaluation store, same shard scheme, different manifest and directory
function elook(set, key) {
  if (!EVAL) return Promise.resolve(null);
  return emanifest().then(function () {
    var n = eShardName(set, key);
    return n ? jfetch(EBASE + set + '/' + n + '.json') : null;
  }).then(function (o) {
    if (!o) return null;
    var v = o[key] !== undefined ? o[key] : o[key.toLowerCase()];
    // an oversize value lives in its own file; the shard holds only a marker
    if (v && v.big && v.pages)
      return jfetch(EBASE + set + '/big/' + safeName(key) + '.0.json')
        .then(function (pg) { return pg ? pg.rows : null; });
    return v;
  });
}

// -------------------------------------------------------------- the markup --
var CSS = ''
+ '#wl{position:fixed;z-index:60;background:var(--panel);color:var(--fg);'
+ 'border-left:1px solid var(--line);box-shadow:-2px 0 18px rgba(0,0,0,.10);'
+ 'display:none;flex-direction:column;font-family:Inter,system-ui,sans-serif}'
+ '#wl.open{display:flex}'
+ 'body.wl-side #wl{top:52px;right:0;bottom:0;width:380px}'
+ 'body.wl-sheet #wl{left:0;right:0;bottom:0;top:auto;width:auto;max-height:62vh;'
+ 'border-left:none;border-top:2px solid var(--accent);box-shadow:0 -6px 20px rgba(0,0,0,.22)}'
+ '#wl .wl-h{padding:9px 12px 0;border-bottom:1px solid var(--line);background:var(--app)}'
+ '#wl .wl-w{font-family:"Gentium Plus",Georgia,serif;font-size:22px;font-weight:700;'
+ 'padding-right:26px;word-break:break-word}'
+ '#wl .wl-c{font-size:11px;color:var(--mut);margin:2px 0 7px}'
+ '#wl .wl-c b{color:var(--fg)}'
+ '#wl .wl-x{position:absolute;top:6px;right:9px;border:none;background:none;'
+ 'font-size:17px;color:var(--mut);cursor:pointer;line-height:1}'
+ '#wl .wl-tabs{display:flex;gap:3px;flex-wrap:wrap}'
+ '#wl .wl-tabs button{font:600 12px/1 Inter,system-ui,sans-serif;border:1px solid var(--line);'
+ 'border-bottom:none;background:var(--chip);color:var(--chipfg);padding:7px 10px 8px;'
+ 'border-radius:8px 8px 0 0;cursor:pointer;position:relative}'
+ '#wl .wl-tabs button[aria-selected=true]{background:var(--panel);color:var(--accent)}'
+ '#wl .wl-tabs button.dis{opacity:.42;cursor:default}'
+ '#wl .wl-tabs button .wl-n{font-weight:400;opacity:.7}'
+ '#wl .wl-tabs button[data-tip]:hover::after{content:attr(data-tip);position:absolute;'
+ 'top:calc(100% + 5px);left:0;z-index:70;width:max-content;max-width:min(260px,70vw);'
+ 'white-space:normal;text-align:left;font:400 12px/1.4 Inter,system-ui,sans-serif;'
+ 'color:#fff;background:#3a3126;padding:6px 8px;border-radius:5px;'
+ 'box-shadow:0 2px 8px rgba(0,0,0,.3);pointer-events:none}'
+ '#wl .wl-b{overflow-y:auto;overflow-wrap:break-word;padding:10px 12px 18px;flex:1 1 auto;font-size:13.5px;line-height:1.55}'
+ '#wl .wl-src{font-size:11px;color:var(--mut);margin:0 0 8px}'
+ '#wl .wl-sub{font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;'
+ 'color:var(--mut);margin:12px 0 4px}'
+ '#wl .wl-promo{border:1px solid var(--line);border-left:3px solid var(--comm);'
+ 'border-radius:8px;padding:2px 9px;background:var(--app)}'
+ '#wl .wl-wordgrp{border:1px solid var(--line);border-left:3px solid var(--canon);'
+ 'border-radius:8px;padding:2px 9px}'
+ '#wl .wl-why{font-size:10.5px;color:var(--mut);margin:3px 0 0;font-style:italic}'
+ '#wl .wl-row{border-top:1px solid var(--line);padding:7px 0 5px}'
+ '#wl .wl-promo .row:first-child,#wl .wl-wordgrp .row:first-child,'
+ '#wl .wl-row:first-of-type{border-top:none}'
+ '#wl .wl-lem{font-family:"Gentium Plus",Georgia,serif;font-weight:700}'
+ '#wl .wl-g{font-family:"Gentium Plus",Georgia,serif}'
+ '#wl .wl-cite{font-size:11px;color:var(--mut);margin-top:2px}'
+ '#wl .wl-flag{font-size:11px;color:var(--mut)}'
+ '#wl .wl-more{font:600 12px Inter,system-ui,sans-serif;color:var(--accent);'
+ 'background:none;border:1px dashed var(--line);border-radius:6px;padding:6px 10px;'
+ 'cursor:pointer;margin:10px 0}'
+ '#wl .wl-none{color:var(--mut);font-size:12.5px}'
+ '#wl .wl-banner{background:var(--app);color:var(--mut);border:1px solid var(--line);'
+ 'border-radius:6px;font-size:11px;padding:5px 8px;margin:0 0 8px}'
+ '#wl .wl-my{font-family:"Padauk","Myanmar Text","Myanmar MN","Myanmar Sangam MN","Noto Sans Myanmar",serif;'
+ 'font-size:15px;line-height:1.9;margin:.25em 0}'
+ '#wl .wl-etym{color:var(--comm);font-family:"Padauk","Myanmar Text","Myanmar MN","Myanmar Sangam MN",serif;'
+ 'font-size:14px;line-height:1.9}'
+ '#wl .wl-cites{font-size:11px;color:var(--fg);background:var(--app);'
+ 'border-radius:5px;padding:4px 7px;margin:.3em 0}'
+ '#wl .wl-reveal{font:600 11px Inter,system-ui,sans-serif;color:var(--accent);'
+ 'background:none;border:1px dashed var(--line);border-radius:5px;'
+ 'padding:4px 8px;cursor:pointer;margin:.3em 0}'
+ '#wl .wl-inline{border-left:3px solid var(--line);padding-left:8px;margin:.3em 0}'
+ '#wl .wl-hidden{display:none}'
+ '#wl .wl-sec{border-top:1px solid var(--line);padding-top:10px;margin-top:14px}'
+ '#wl .wl-sec:first-of-type{border-top:none;margin-top:0;padding-top:0}'
+ '#wl .wl-sec .wl-sub{margin-top:0;color:var(--accent);font-size:11.5px}'
+ '#wl .wl-jump{font-size:11.5px;line-height:1.9;padding:0 0 10px;'
+ 'border-bottom:1px solid var(--line);margin-bottom:12px}'
+ '#wl .wl-jump a{color:var(--accent);text-decoration:underline;'
+ 'text-decoration-style:dotted;text-underline-offset:2px;margin-right:2px}'
+ '#wl .wl-ext{overflow-wrap:break-word}'
+ '#wl .wl-ext table,#wl .wl-ext img{max-width:100%}'
/* DPD's declension grid is wider than any panel; it spilled 34px past the
   edge and the gate's geometry check caught it.  Scroll it, do not squash it:
   a declension table with collapsed columns is worse than one you drag. */
+ '#wl .wl-ext .inflection{display:block;overflow-x:auto;max-width:100%}'
+ '#wl .wl-ext .inflection table{max-width:none}'
/* !!! and not every DPD table is inside .inflection -- the gate reported a
   bare TBODY 34px past the edge.  Give every table in an entry its own
   horizontal scroller instead of trusting DPD's markup to be consistent. */
+ '#wl .wl-ext{max-width:100%}'
+ '#wl .wl-ext table{display:block;overflow-x:auto;max-width:100%;width:max-content}'
+ '#wl .wl-ext table tbody,#wl .wl-ext table thead{width:max-content}'
+ '#wl .wl-ext pre{white-space:pre-wrap;word-break:break-word}'
+ '#wl .wl-ext table{border-collapse:collapse;font-size:11.5px}'
/* DPD'S OWN CHIPS -- grammar, examples, declension, root family, compound
   family, idioms -- each open a block DPD keeps hidden inside the entry. They
   are how a DPD entry is read and the reader asked for them, so they are kept
   as chips, set smaller and warmer than the real tabs above so the two rows
   are told apart by weight.
   !!! This block went in once before and silently did not apply: the string it
   was replacing had drifted, the replace matched nothing, and there was no
   assertion to say so -- the chips rendered as four run-together blue links.
   Anchored and asserted now. */
+ '#wl .wl-ext a.dpd-button{display:inline-block;font:600 10.5px/1 Inter,system-ui,sans-serif;'
+ 'color:var(--chipfg);background:var(--chip);border:1px solid var(--line);'
+ 'border-radius:9px;padding:5px 9px;margin:3px 4px 0 0;text-decoration:none;'
+ 'cursor:pointer;white-space:nowrap}'
+ '#wl .wl-ext a.dpd-button:hover{background:var(--hover);color:var(--fg)}'
+ '#wl .wl-ext .button-box{margin:6px 0 3px}'
/* ...and the blocks they open must START closed.  DPD marks them
   `class="dpd content hidden"` and relies on its own stylesheet, which is not
   here -- so every one of them was open, and the entry arrived as a wall with
   the chips doing nothing visible. */
+ '#wl .wl-ext .content.hidden,#wl .wl-ext .dpd.hidden{display:none}'
/* DPD's feedback prompts point at DPD's own site and are addressed to its
   editors, not to a reader of this edition. */
+ '#wl .wl-ext a.dpd-link{display:none}'
+ '#wl .wl-ext p.dpd-footer{display:none}'
+ '#wl .wl-ext td,#wl .wl-ext th{border:1px solid var(--line);padding:1px 4px}'
+ '#wl .wl-back{border:1px solid var(--line);background:var(--panel);'
+ 'color:var(--accent);border-radius:5px;font:700 13px/1 Inter,system-ui,sans-serif;'
+ 'padding:3px 7px;cursor:pointer;margin-right:6px;display:none}'
+ '#wl .wl-back.on{display:inline-block}'
+ '#wl .wl-ped p{margin:.35em 0}'
+ /* !!! THE PANEL IS position:fixed AND THE PAGE IS A GRID, SO NOTHING
     REFLOWED FOR IT.  Measured in Chromium by sweeping the viewport
     (gate_reader.py --breakpoints): at every width from 1500 down to 1180 the
     canon paragraph's right edge sat 190-350px INSIDE the panel — the side
     panel was simply printed on top of the text it was explaining, and the
     text column never moved.  reader2's main region is `.main` (grid-area:
     main), so that is what has to give up the width. */
  'body.wl-side.wl-open .main{padding-right:380px}'
+ 'body.wl-sheet.wl-open .main{padding-bottom:64vh}'
+ '.wl-mark{background:var(--hl);border-radius:2px}';

var el = null;
function build() {
  var s = document.createElement('style'); s.textContent = CSS;
  document.head.appendChild(s);
  el = document.createElement('aside');
  el.id = 'wl'; el.setAttribute('aria-label', 'Word lookup');
  el.innerHTML =
    '<div class="wl-h"><button class="wl-x" id="wlx" title="' + esc(T('wl_close')) + '">✕</button>'
    + '<div class="wl-w"><button class="wl-back" id="wlback" title="'
    + esc(T('wl_back')) + '">‹</button><span id="wlw">&nbsp;</span></div>'
    + '<div class="wl-c" id="wlc"></div>'
    + '<div class="wl-tabs" id="wlt" role="tablist"></div></div>'
    + '<div class="wl-b" id="wlb"></div>';
  document.body.appendChild(el);
  document.getElementById('wlx').addEventListener('click', close);
  document.getElementById('wlback').addEventListener('click', function () {
    var prev = HIST.pop();
    updateBack();
    if (prev) lookup(prev.word, prev.para, true);
  });
  // RECURSIVE LOOKUP.  A word inside the panel is a word like any other: the
  // same caret recovery runs on the panel body, and the paragraph context is
  // carried over so the Edition tab still knows where the reader is standing.
  // It fires only when the corpus actually has the word — an English or
  // Burmese word in a dictionary entry is a silent no-op rather than an empty
  // panel.
  document.getElementById('wlb').addEventListener('click', function (ev) {
    if (ev.target.closest('a,button')) return;
    var hit = wordAt(ev.clientX, ev.clientY);
    if (!hit || !current || hit.word === current.word) return;
    look('freq', hit.word).then(function (fr) {
      if (!fr || !current) return;
      HIST.push({word: current.word, para: current.para});
      updateBack();
      lookup(hit.word, current.para, true);
    });
  });
  layout();
  addEventListener('resize', layout);
  try {
    var m = document.querySelector('.main');
    if (m && window.ResizeObserver) new ResizeObserver(layout).observe(m);
  } catch (e) {}
}

// LAYOUT — decided by the width the TEXT would be left with, measured, not by
// a viewport breakpoint guessed from the prototype.
//
// The prototype's rule was "side panel at >= ~1140px".  Swept inside reader2
// (gate_reader.py --breakpoints) that is wrong twice over.  First, reader2
// keeps a 300px left pane above 861px, so the same viewport leaves far less
// text; at 1180px the canon column came out at 456px — 59 characters, below a
// comfortable measure.  Second, the reader lets the user HIDE that pane, and
// then 300px comes back: a rule keyed on the viewport cannot see the
// difference and would give a reader with the pane hidden a bottom sheet on a
// screen with room to spare.
//
// So the rule reads the region the text actually lives in.  `.main` is
// reader2's grid area; its clientWidth does not change when the panel adds
// padding, so it is a stable measure of what there is to divide.
var PANEL_W = 380;      // must match the width in CSS above
var TEXT_MIN = 550;     // ≈ 65 characters at the reader's default size,
                        // measured: 1240px viewport with the pane shown
function mainW() {
  var m = document.querySelector('.main');
  return m ? m.clientWidth : innerWidth;
}
function layout() {
  var side = mainW() >= PANEL_W + TEXT_MIN;
  document.body.classList.toggle('wl-side', side);
  document.body.classList.toggle('wl-sheet', !side);
}
function close() {
  el.classList.remove('open');
  document.body.classList.remove('wl-open');
  unmark();
}

// !!! IN SHEET MODE THE PANEL COVERS THE WORD IT IS EXPLAINING.  Measured on a
// real 390x844 phone viewport in Chromium: the sheet's top edge lands at y=321
// and the clicked word sat at y=460, behind it — the reader taps a word and the
// answer arrives on top of the question.  reader2 scrolls in `.scroll`, so that
// is what has to move; the word is put a little above the sheet, not merely
// "into view", or it ends up flush against the edge.
function keepWordVisible() {
  if (!markEl || !document.body.classList.contains('wl-sheet')) return;
  var sc = document.getElementById('scroll');
  if (!sc) return;
  var limit = el.getBoundingClientRect().top - 12;
  var r = markEl.getBoundingClientRect();
  if (r.bottom <= limit && r.top >= 56) return;
  var target = 56 + (limit - 56) * 0.45;       // a little above the middle
  sc.scrollTop += (r.top - target);
}

// ------------------------------------------- caret-based click recovery ----
function wordAt(x, y) {
  var node, off, c, r;
  if (document.caretPositionFromPoint) {
    c = document.caretPositionFromPoint(x, y); if (!c) return null;
    node = c.offsetNode; off = c.offset;
  } else if (document.caretRangeFromPoint) {
    r = document.caretRangeFromPoint(x, y); if (!r) return null;
    node = r.startContainer; off = r.startOffset;
  } else return null;
  if (!node || node.nodeType !== 3) return null;
  var t = node.textContent;
  function isW(i) {
    var ch = t[i]; if (ch === undefined) return false;
    if (PALISET[ch]) return true;
    if (APOS[ch]) return !!(PALISET[t[i - 1] || ''] && PALISET[t[i + 1] || '']);
    return false;
  }
  if (!isW(off) && !isW(off - 1)) return null;
  var a = isW(off) ? off : off - 1, b = a;
  while (a > 0 && isW(a - 1)) a--;
  while (b < t.length - 1 && isW(b + 1)) b++;
  var w = t.slice(a, b + 1).replace(/(\d{1,2})$/, '');
  return w ? {word: w, node: node, a: a, b: b} : null;
}

var markEl = null;
function unmark() {
  if (!markEl) return;
  var p = markEl.parentNode;
  while (markEl.firstChild) p.insertBefore(markEl.firstChild, markEl);
  p.removeChild(markEl); p.normalize(); markEl = null;
}
function mark(node, a, b) {
  unmark();
  var r = document.createRange(); r.setStart(node, a); r.setEnd(node, b + 1);
  markEl = document.createElement('mark'); markEl.className = 'wl-mark';
  try { r.surroundContents(markEl); } catch (e) { markEl = null; }
}

// ------------------------------------------------------------- the lookup --
var current = null;
var HIST = [];
function updateBack() {
  var b = document.getElementById('wlback');
  if (b) b.classList.toggle('on', HIST.length > 0);
}
function paraTextOf(node) {
  var p = node && node.parentNode;
  while (p && !(p.classList && p.classList.contains('para'))) p = p.parentNode;
  return p;
}

// The paragraph's stems WITH THEIR COUNTS.  A two-word lemma has to find two
// words, or `Tassa tassā` would count as satisfied by a single `tassa`.
function poolOf(text) {
  var pool = {};
  function add(w) { var s = stem(w); if (s) pool[s] = (pool[s] || 0) + 1; }
  (text.match(/[aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvshḷṁAĀIĪUŪEOKGṄCJÑṬḌṆTDNPBMYRLVSHḶṀ’'-]+/g) || [])
    .forEach(function (w) {
      add(w);
      if (w.indexOf('-') >= 0)
        w.split('-').forEach(function (part) { if (part) add(part); });
    });
  return pool;
}
function inPara(row, pool) {
  if (!row.k || !row.k.length) return false;
  var need = {}, i;
  for (i = 0; i < row.k.length; i++) need[row.k[i]] = (need[row.k[i]] || 0) + 1;
  for (var s in need) if (!(pool[s] >= need[s])) return false;
  return true;
}

function lookup(word, paraEl, inPanel) {
  if (!inPanel) { HIST.length = 0; updateBack(); }   // a click in the text starts fresh
  current = {word: word, para: paraEl};
  el.classList.add('open');
  el.dataset.state = 'loading';
  document.body.classList.add('wl-open');
  document.getElementById('wlw').textContent = word;
  document.getElementById('wlc').textContent = T('wl_loading');
  document.getElementById('wlb').innerHTML = '';

  var vo = volOrdOf(paraEl);
  Promise.all([look('freq', word), look('gloss', word), look('forms', word),
               vo ? loadLinks(vo.vol) : Promise.resolve(null)])
    .then(function (res) {
      if (!current || current.word !== word) return;   // superseded by a later click
      var freq = res[0], gl = res[1], forms = res[2];
      var linked = vo ? linkedKeys(res[3], vo.ord) : {};
      // A high-frequency form's rows do not fit in a shard (`tattha` alone has
      // 718): the shard carries only the count and the rows live in paged
      // files.  Fetch the first page now — the panel must never claim a total
      // it has not got, nor show a count with nothing behind it.
      var big = gl && !Array.isArray(gl) && gl.big ? gl : null;
      var pGloss = big
        ? jfetch(BASE + 'gloss/big/' + safeName(word) + '.0.json')
        : Promise.resolve(null);
      var pPed = (forms && forms.length)
        ? Promise.all(forms.map(function (h) {
            return look('ped', h).then(function (e) { return {h: h, e: e}; }); }))
        : Promise.resolve([]);
      // the evaluation store: form -> {h: DPD headwords, b: base lemmas},
      // then one fetch per headword and per lemma
      var pEval = elook('form', word).then(function (fr) {
        if (!fr) return null;
        return Promise.all([
          Promise.all((fr.h || []).map(function (h) {
            return elook('dpd', h).then(function (e) { return {h: h, e: e}; }); })),
          Promise.all((fr.b || []).map(function (b) {
            return elook('lem', b).then(function (e) { return {b: b, e: e}; }); }))
        ]).then(function (z) {
          return {dpd: z[0].filter(function (x) { return x.e; }),
                  lem: z[1].filter(function (x) { return x.e; })};
        });
      });
      return Promise.all([pGloss, pPed, pEval]).then(function (r2) {
        if (!current || current.word !== word) return;
        var page0 = r2[0], ped = r2[1], ev = r2[2];
        var rows = Array.isArray(gl) ? gl : (page0 ? page0.rows : []);
        var nGloss = big ? big.big : rows.length;
        render({word: word, para: paraEl, freq: freq, rows: rows,
                linked: linked, ev: ev,
                big: !!big, page: page0 ? page0.page : null,
                pages: page0 ? page0.pages : null, nGloss: nGloss,
                ped: ped.filter(function (p) { return p.e; })});
      });
    });
}

// !!! ELEVEN TABS WAS TOO MANY, AND THE READER SAID SO (2026-08-02).  A tab
// row that wraps to three lines is a menu, not a choice, and it also put the
// modern lexica on the same visual footing as the edition's own glosses --
// which is the one thing §9 is about.  So there are now THREE tabs:
//
//     Edition           the edition's own glosses.  Always first, always default.
//     Abhidhāna         the §9 lexical authority, with PEU's English inside each
//                       entry behind its attributed reveal, as before.
//     Pāḷi Dictionary   everything else, stacked as SECTIONS inside one tab, in
//                       order of authority, each with its own attribution and
//                       banner.  This is the shape dictionary.sutta.org itself
//                       uses, and what the reader asked for.
//
// Nothing is lost: every source still has its own heading, count and
// attribution, and DPD is still last and still banner'd.
var DICT_SECTIONS = [
  ['ped',  'wl_ped',  'wl_tip_ped'],
  ['cped', 'wl_cped', 'wl_tip_cped'],
  ['ny',   'wl_ny',   'wl_tip_ny'],
  ['vri',  'wl_vri',  'wl_tip_vri'],
  ['ppn',  'wl_ppn',  'wl_tip_ppn'],
  ['uhs',  'wl_uhs',  'wl_tip_uhs'],
  ['rt',   'wl_rt',   'wl_tip_rt'],
  ['tpm',  'wl_tpm',  'wl_tip_tpm'],
  ['pwg',  'wl_pwg',  'wl_tip_pwg']
  // DPD is NOT a section here: with the evaluation flag on it has its own tab,
  // first, and with the flag off it is not in the build at all.
];

function tabBtn(id, label, n, dis, tip) {
  // no `disabled` attribute: it swallows hover events, and the tooltip with
  // them, in Safari.  A class + aria-disabled + a click guard instead.
  return '<button role="tab" data-tab="' + id + '" aria-selected="false"'
    + (dis ? ' class="dis" aria-disabled="true"' : '')
    + (tip ? ' data-tip="' + esc(tip) + '"' : '') + '>'
    + esc(label) + (n != null ? ' <span class="wl-n">' + n + '</span>' : '') + '</button>';
}

function render(d) {
  var tabs = document.getElementById('wlt'), body = document.getElementById('wlb');
  var c = d.freq;
  document.getElementById('wlc').innerHTML = c
    ? '<b>' + c[0] + '</b> ' + esc(T('wl_corpus')) + ' · ' + c[1] + ' ' + esc(T('wl_canon'))
      + ' · ' + c[2] + ' ' + esc(T('wl_comm')) + ' · ' + c[3] + ' ' + esc(T('wl_sub'))
    : '';
  var nPed = d.ped.reduce(function (s, p) { return s + p.e.length; }, 0);
  // how many entries each evaluation source has for this word
  d.n = {};
  var lems = (d.ev && d.ev.lem) || [];
  function count(field, listy) {
    var n = 0;
    lems.forEach(function (L) {
      var v = L.e[field];
      if (v) n += listy ? v.length : 1;
    });
    return n;
  }
  d.n.dpd = (d.ev && d.ev.dpd) ? d.ev.dpd.length : 0;
  d.n.abhi = count('a', true);
  d.n.peu = count('p', false);
  d.n.cped = count('cp', false);
  d.n.ppn = count('pn', true);
  d.n.ny = count('ny', true);
  d.n.vri = count('vri', true);
  d.n.pwg = count('pwg', true);
  d.n.tpm = count('tpm', true);
  d.n.rt = count('rt', true);
  d.n.uhs = count('uhs', true);

  d.n.ped = nPed;
  // the aggregate count on the one dictionary tab
  var nDict = 0;
  DICT_SECTIONS.forEach(function (t) {
    if (EVAL || t[0] === 'ped') nDict += (d.n[t[0]] || 0);
  });
  d.nDict = nDict;
  // TAB ORDER DEPENDS ON WHICH PANEL THIS IS, AND THAT IS THE WHOLE POINT.
  //
  // With the evaluation flag ON this is the reader's own comparison surface,
  // and they want it in the prototype's order: DPD first, the edition last.
  // That is a working preference about a local tool, and §9 does not reach it.
  //
  // With the flag OFF this is the publishable panel, there IS no DPD, and the
  // edition is first because it is the only voice there is. So §9's guarantee
  // is kept exactly where it applies, and the gate asserts it there.
  var html = EVAL
    ? tabBtn('dpd',  T('wl_dpd'),  d.n.dpd || null, !d.n.dpd, T('wl_tip_dpd'))
      + tabBtn('abhi', T('wl_abhi'), d.n.abhi || null, !d.n.abhi, T('wl_tip_abhi'))
      + tabBtn('dict', T('wl_dict'), nDict || null, !nDict, T('wl_tip_dict'))
      + tabBtn('ed',   T('wl_edition'), d.nGloss || null, !d.nGloss, T('wl_tip_ed'))
    : tabBtn('ed',   T('wl_edition'), d.nGloss || null, !d.nGloss, T('wl_tip_ed'))
      + tabBtn('dict', T('wl_dict'), nDict || null, !nDict, T('wl_tip_dict'));
  tabs.innerHTML = html;
  Array.prototype.forEach.call(tabs.querySelectorAll('button'), function (b) {
    b.addEventListener('click', function () {
      if (!b.classList.contains('dis')) show(b.dataset.tab, d); });
  });
  // Edition is the default tab, always — never a dictionary (§9)
  var first = EVAL
    ? (d.n.dpd ? 'dpd' : d.n.abhi ? 'abhi' : nDict ? 'dict' : 'ed')
    : (d.nGloss ? 'ed' : nDict ? 'dict' : 'ed');
  show(first, d);
  keepWordVisible();
  el.dataset.state = 'ready';
}

function show(tab, d) {
  var tabs = document.getElementById('wlt'), body = document.getElementById('wlb');
  Array.prototype.forEach.call(tabs.querySelectorAll('button'), function (b) {
    b.setAttribute('aria-selected', b.dataset.tab === tab ? 'true' : 'false'); });
  body.innerHTML = tab === 'ed'   ? viewEd(d)
                 : tab === 'abhi' ? viewAbhi(d)
                 : tab === 'dpd'  ? viewDpd(d)
                 : viewDict(d);
  body.scrollTop = 0;
  var more = body.querySelector('button.more');
  if (more) more.addEventListener('click', function () { loadMore(d, more); });
}

function rowHtml(r) {
  return '<div class="wl-row"><span class="lem g">' + esc(r.l) + '</span>'
    + (r.q ? ' <span class="wl-flag">(' + esc(T('wl_quoted')) + ')</span>' : '')
    + (r.h ? ' <span class="wl-flag">(' + esc(T('wl_series')) + ')</span>' : '')
    + ' — <span class="wl-g">' + esc(r.g) + '</span>'
    + (r.t ? '<div class="wl-flag">' + esc(T('wl_trunc')) + '</div>' : '')
    + '<div class="wl-cite">' + esc(r.v) + ' §' + (r.n != null ? r.n : '—')
    + (r.p ? ' · p.' + r.p : '') + (r.s ? ' · ' + esc(r.s) : '') + '</div></div>';
}

// Which target paragraphs does the edition's link map tie this one to?
//
// !!! reader2 declares its own `state` with `const` at script top level, which
// does NOT put it on `window` — reading `window.state.links` from here gets
// undefined, silently, and every gloss would fall out of the promoted group
// with no error to show for it.  So the panel loads the same map itself.  That
// also keeps the coupling to one thing that is already a published file
// (`linksk/<VOL>.links.json`, keyed by ordinal) rather than to reader2's
// internals, which another session may be changing.
function volOrdOf(paraEl) {
  var m = paraEl && paraEl.id && /^p-(.+)-(\d+)$/.exec(paraEl.id);
  return m ? {vol: m[1], ord: m[2]} : null;
}
function loadLinks(vol) {
  return jfetch('linksk/' + vol + '.links.json');
}
function linkedKeys(links, ord) {
  var out = {}, e = (links && links[String(ord)]) || {};
  ['commentary', 'subcommentary'].forEach(function (layer) {
    (e[layer] || []).forEach(function (t) {
      if (t && t.n != null) out[t.key.split('#')[0] + '|' + t.n] = 1; });
  });
  return out;
}

function viewEd(d) {
  var h = '<div class="wl-src">' + esc(T('wl_ed_src')) + '</div>';
  if (!d.nGloss) return h + '<p class="wl-none">' + esc(T('wl_nogloss')) + '</p>';
  var rows = d.rows;
  var pool = d.para ? poolOf(d.para.textContent) : {};
  var linked = d.linked || {};
  // FOUR GROUPS, EACH WITH A CRITERION THAT CAN BE STATED AND CHECKED.
  //
  // !!! The first version had two, and the second of them was a lie by
  // omission.  "The lemma stands in this paragraph" is a real coincidence for a
  // multi-word lemma and NO information at all for a one-word one: if the
  // reader clicked `tattha`, then a row whose whole lemma is `tattha` is
  // trivially "in this paragraph".  Measured over the corpus: the rule fires on
  // 80.9% of glossed clicks, but 30% of what it promotes is that empty
  // one-word case.  A one-word gloss is worth having — it is the edition
  // defining the word plainly — so it keeps a group; it just must not be
  // dressed up as being about this passage.
  var prox = [], here = [], word = [], rest = [];
  rows.forEach(function (r) {
    var multi = (r.w || (r.k || []).length) > 1;   // words printed in bold
    if (inPara(r, pool)) {
      if (linked[r.v + '|' + r.n]) prox.push(r);
      else if (multi) here.push(r);
      else word.push(r);
    } else rest.push(r);
  });
  if (prox.length)
    h += '<div class="wl-sub">' + esc(T('wl_prox')) + '</div><div class="wl-promo">'
       + prox.map(rowHtml).join('') + '</div>'
       + '<div class="wl-why">' + esc(T('wl_checked')) + '</div>';
  if (here.length)
    h += '<div class="wl-sub">' + esc(T('wl_here')) + '</div><div class="wl-promo">'
       + here.map(rowHtml).join('') + '</div>'
       + (prox.length ? '' : '<div class="wl-why">' + esc(T('wl_checked')) + '</div>');
  if (word.length)
    h += '<div class="wl-sub">' + esc(T('wl_word')) + '</div><div class="wl-wordgrp">'
       + word.map(rowHtml).join('') + '</div>'
       + '<div class="wl-why">' + esc(T('wl_why_word')) + '</div>';
  if (rest.length)
    // !!! "All occurrences (1 of 5)" read as though it were showing one of
    // five, when it was showing the one that had NOT been promoted.  The count
    // that belongs here is the size of this group; the total is on the tab.
    h += '<div class="wl-sub">' + esc(T('wl_rest')) + ' <span class="wl-flag">('
       + rest.length + ')</span></div>'
       + rest.map(rowHtml).join('');
  if (d.big && d.pages && d.page + 1 < d.pages)
    h += '<button class="wl-more">' + esc(T('wl_more')) + ' — '
       + ((d.page + 1) * 120) + ' ' + esc(T('wl_of')) + ' ' + d.nGloss + '</button>';
  return h;
}

function loadMore(d, btn) {
  var next = (d.page == null ? 0 : d.page + 1);
  if (next >= d.pages) return;
  btn.disabled = true;
  jfetch(BASE + 'gloss/big/' + safeName(d.word) + '.' + next + '.json')
    .then(function (o) {
      if (!o) return;
      d.rows = d.rows.concat(o.rows); d.page = o.page; d.pages = o.pages;
      show('ed', d);
    });
}

function viewPed(d) {
  var h = '<div class="wl-src">' + esc(T('wl_ped_src')) + '</div>';
  if (!d.ped.length) return h + '<p class="wl-none">' + esc(T('wl_noped')) + '</p>';
  d.ped.forEach(function (p) {
    p.e.forEach(function (body) {
      h += '<div class="wl-row wl-ped"><div class="lem g">' + esc(p.h) + '</div>'
         + '<div>' + body + '</div></div>';
    });
  });
  return h;
}



// ---------------------------------------------------- evaluation views ----
// Every one of these opens with an attribution line and the evaluation banner.
// Sources are never merged: one tab, one source, and PEU's English appears
// inside an Abhidhāna entry only in an attributed, collapsed reveal.
function evHead(srcLine, extra) {
  return '<div class="wl-banner">' + esc(T('wl_eval')) + '</div>'
       + '<div class="wl-src">' + esc(srcLine) + (extra ? ' ' + esc(extra) : '')
       + '</div>';
}

function viewDpd(d) {
  var h = evHead(T('wl_tip_dpd'));
  var e = (d.ev && d.ev.dpd) || [];
  if (!e.length) return h + '<p class="wl-none">' + esc(T('wl_noentry')) + '</p>';
  // DPD's entry carries its own chips -- grammar, examples, declension, root
  // family, compound family, idioms -- each opening a block it keeps hidden.
  // They are how the entry is read, so they are passed through as DPD draws
  // them and wired up in show().
  e.forEach(function (x, i) {
    h += '<div class="wl-row"><span class="wl-cite">' + (i + 1) + '. </span>'
       + '<span class="wl-lem wl-g">' + esc(x.h) + '</span>'
       + '<div class="wl-ext wl-dpd">' + x.e + '</div></div>';
  });
  return h;
}

function viewAbhi(d) {
  var h = evHead(T('wl_tip_abhi'));
  var i = 0;
  ((d.ev && d.ev.lem) || []).forEach(function (L) {
    (L.e.a || []).forEach(function (row) {
      i++;
      // row = [Burmese headword+POS, Burmese etymology, roman etymology,
      //        Burmese definition, [transcoded citations]]
      var myhead = row[0], myetym = row[1], rometym = row[2],
          mydef = row[3], cites = row[4] || [];
      h += '<div class="wl-row"><span class="wl-cite">' + i + '. </span>'
         + '<span class="wl-lem wl-g">' + esc(L.b) + '</span> '
         + '<span class="wl-my">' + esc(myhead) + '</span>'
         + ((myetym || rometym)
            ? '<div class="wl-etym">' + esc(myetym)
              + (rometym ? ' <span class="wl-cite">' + esc(rometym) + '</span>' : '')
              + '</div>' : '')
         + '<div class="wl-my">' + esc(mydef) + '</div>'
         + (cites.length
            ? '<div class="wl-cites">' + esc(T('wl_cites')) + ' '
              + cites.map(esc).join(' · ')
              + ' <span class="wl-cite">' + esc(T('wl_cites_note')) + '</span></div>'
            : '');
      if (L.e.p) {
        h += '<button class="wl-reveal">' + esc(T('wl_en_btn')) + '</button>'
           + '<div class="wl-inline wl-hidden"><div class="wl-src">'
           + esc(L.e.pm ? T('wl_mt') : T('wl_en_attr')) + '</div>' + L.e.p + '</div>';
      }
      h += '</div>';
    });
  });
  if (!i) h += '<p class="wl-none">' + esc(T('wl_noentry')) + '</p>';
  return h;
}

function viewPeu(d) {
  var h = evHead(T('wl_tip_peu'));
  var human = '', mt = '', i = 0;
  ((d.ev && d.ev.lem) || []).forEach(function (L) {
    if (!L.e.p) return;
    i++;
    var ent = '<div class="wl-row"><span class="wl-cite">' + i + '. </span>'
            + '<span class="wl-lem wl-g">' + esc(L.e.pk || L.b) + '</span>'
            + '<div class="wl-ext">' + L.e.p + '</div></div>';
    if (L.e.pm) mt += ent; else human += ent;
  });
  h += human;
  // machine translation is never mixed in: it is withheld behind its own press
  if (mt)
    h += '<div class="wl-banner">' + esc(T('wl_mt')) + '</div>'
       + '<button class="wl-reveal">' + esc(T('wl_mt_show')) + '</button>'
       + '<div class="wl-mt wl-hidden">' + mt + '</div>';
  if (!i) h += '<p class="wl-none">' + esc(T('wl_noentry')) + '</p>';
  return h;
}


// ONE TAB, MANY SOURCES.  Each keeps its own heading, count, attribution and
// banner -- a section, not a merge.  A jump strip at the top says what is in
// here for this word, so the reader can see at a glance without scrolling.
function viewDict(d) {
  var have = DICT_SECTIONS.filter(function (t) {
    return (EVAL || t[0] === 'ped') && (d.n[t[0]] || 0) > 0;
  });
  if (!have.length)
    return '<p class="wl-none">' + esc(T('wl_nodict')) + '</p>';

  var h = '';
  if (have.length > 1) {
    h += '<div class="wl-jump"><span class="wl-cite">' + esc(T('wl_jump')) + '</span> '
       + have.map(function (t) {
           return '<a href="#wl-s-' + t[0] + '">' + esc(T(t[1]))
                + ' <span class="wl-cite">' + d.n[t[0]] + '</span></a>';
         }).join(' · ') + '</div>';
  }
  have.forEach(function (t) {
    var key = t[0];
    h += '<div class="wl-sec" id="wl-s-' + key + '">'
       + '<div class="wl-sub">' + esc(T(t[1]))
       + ' <span class="wl-flag">(' + d.n[key] + ')</span></div>'
       + '<div class="wl-src">' + esc(T(t[2]))
       + (LEXBURMESE[key] ? ' ' + esc(T('wl_zg')) : '') + '</div>'
       + (key === 'ped' ? '' : '<div class="wl-banner">' + esc(T('wl_eval')) + '</div>')
       + sectionBody(d, key)
       + '</div>';
  });
  return h;
}

function sectionBody(d, key) {
  if (key === 'ped') {
    var h = '';
    d.ped.forEach(function (p) {
      p.e.forEach(function (body) {
        h += '<div class="wl-row"><div class="wl-lem wl-g">' + esc(p.h) + '</div>'
           + '<div class="wl-ext">' + body + '</div></div>';
      });
    });
    return h;
  }
  if (key === 'dpd') return dpdBody(d);
  return lexBody(d, key);
}

function dpdBody(d) {
  var h = '', e = (d.ev && d.ev.dpd) || [];
  e.forEach(function (x, i) {
    h += '<div class="wl-row"><span class="wl-cite">' + (i + 1) + '. </span>'
       + '<span class="wl-lem wl-g">' + esc(x.h) + '</span>'
       + '<div class="wl-ext">' + x.e + '</div></div>';
  });
  return h;
}

function lexBody(d, key) {
  var field = LEXFIELD[key], h = '', i = 0;
  if (!field) return '';
  ((d.ev && d.ev.lem) || []).forEach(function (L) {
    var v = L.e[field];
    if (!v) return;
    (Array.isArray(v) ? v : [v]).forEach(function (ent) {
      i++;
      h += '<div class="wl-row"><span class="wl-cite">' + i + '. </span>'
         + '<span class="wl-lem wl-g">' + esc(L.b) + '</span>'
         + '<div class="' + (LEXBURMESE[key] ? 'wl-my' : 'wl-ext') + '">'
         + (LEXBURMESE[key] ? esc(ent) : ent) + '</div></div>';
    });
  });
  return h;
}

var LEXFIELD = {cped: 'cp', ppn: 'pn', ny: 'ny', vri: 'vri',
                pwg: 'pwg', tpm: 'tpm', rt: 'rt', uhs: 'uhs'};
var LEXTIP = {cped: 'wl_tip_cped', ppn: 'wl_tip_ppn', ny: 'wl_tip_ny',
              vri: 'wl_tip_vri', pwg: 'wl_tip_pwg', tpm: 'wl_tip_tpm',
              rt: 'wl_tip_rt', uhs: 'wl_tip_uhs'};
var LEXBURMESE = {pwg: 1, tpm: 1, rt: 1, uhs: 1};

function viewLex(d, tab) {
  var field = LEXFIELD[tab];
  if (!field) return '<p class="wl-none">' + esc(T('wl_noentry')) + '</p>';
  var h = evHead(T(LEXTIP[tab]), LEXBURMESE[tab] ? T('wl_zg') : '');
  var i = 0;
  ((d.ev && d.ev.lem) || []).forEach(function (L) {
    var v = L.e[field];
    if (!v) return;
    (Array.isArray(v) ? v : [v]).forEach(function (ent) {
      i++;
      h += '<div class="wl-row"><span class="wl-cite">' + i + '. </span>'
         + '<span class="wl-lem wl-g">' + esc(L.b) + '</span>'
         + '<div class="' + (LEXBURMESE[tab] ? 'wl-my' : 'wl-ext') + '">'
         + (LEXBURMESE[tab] ? esc(ent) : ent) + '</div></div>';
    });
  });
  if (!i) h += '<p class="wl-none">' + esc(T('wl_noentry')) + '</p>';
  return h;
}

// ------------------------------------------------------------------- wire --
function start() {
  build();
  manifest();
  document.addEventListener('click', function (ev) {
    if (el && el.contains(ev.target)) return;
    var p = ev.target.closest && ev.target.closest('.para');
    if (!p) return;
    if (ev.target.closest('a,button,.tools,.app')) return;
    var hit = wordAt(ev.clientX, ev.clientY);
    if (!hit) return;
    mark(hit.node, hit.a, hit.b);
    lookup(hit.word, p);
  }, true);
}

if (document.readyState === 'loading')
  document.addEventListener('DOMContentLoaded', start);
else start();

// exposed for the gate
window.WL = {lookup: function (w, p) { return lookup(w, p); },
             panelW: PANEL_W, textMin: TEXT_MIN, layout: layout, on: true};
})();
