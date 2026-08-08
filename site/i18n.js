// OSBCT interface translations (EN / ES). The Pāḷi corpus itself is never translated.
window.I18N = {
  // nav / chrome
  nav_home:{en:'Home',es:'Inicio'},
  nav_reader:{en:'Reader',es:'Lector'},
  nav_search:{en:'Search',es:'Búsqueda'},
  nav_downloads:{en:'Downloads',es:'Descargas'},
  nav_about:{en:'About',es:'Acerca'},
  nav_errata:{en:'Errata',es:'Erratas'},
  btn_errata:{en:'Errata',es:'Erratas'},
  theme_toggle:{en:'Toggle light / dark',es:'Cambiar claro / oscuro'},

  // TOOLTIPS.  These were the last English strings left in the Spanish
  // interface (2026-07-30f): `applyI18n` has always supported
  // `data-i18n-title`, and NOT ONE element in the site used it, so every
  // tooltip stayed English whatever the language.  The reader also builds
  // tooltips in JS, and those go through `t()` at the call site.
  // The Pāḷi is never translated — only the gloss beside it.
  tip_nav:{en:'Hide / show navigation',es:'Ocultar / mostrar la navegación'},
  tip_toc:{en:'Table of contents',es:'Índice'},
  tip_layer_canon:{en:'Pāḷi — Tipiṭaka (canon)',es:'Pāḷi — Tipiṭaka (canon)'},
  tip_layer_comm:{en:'Aṭṭhakathā — commentary',es:'Aṭṭhakathā — comentario'},
  tip_layer_tika:{en:'Ṭīkā — subcommentary',es:'Ṭīkā — subcomentario'},
  tip_outline:{en:'Collapse long commentaries into a lemma outline',
               es:'Contraer los comentarios largos en un esquema de lemas'},
  tip_smaller:{en:'Smaller text',es:'Reducir el texto'},
  tip_larger:{en:'Larger text',es:'Agrandar el texto'},
  tip_copy_text:{en:'Copy text',es:'Copiar el texto'},
  tip_copy_cit:{en:'Copy citation',es:'Copiar la cita'},
  tip_view_page:{en:'View printed page',es:'Ver la página impresa'},
  tip_goto:{en:'Go to',es:'Ir a'},

  // AN EMPTY BAND SAYS WHY IT IS EMPTY (2026-08-01).  Added with the prune of
  // the 22,719 commentary targets the edition does not assign: where the reader
  // used to be shown the wrong Aṭṭhakathā it is now shown nothing, and nothing
  // has to be explained.  The placeholder is the band name, Pāḷi in both languages.
  band_none:{en:'The edition assigns no %s to this work.',
             es:'La edición no asigna ningún %s a esta obra.'},
  band_here:{en:'No %s is linked to the passages on screen.',
             es:'Ningún %s está enlazado con los pasajes en pantalla.'},
  // said on the layer button itself, and when it is pressed: the WORK has this
  // band but this VOLUME links nothing to it (2026-08-03)
  band_vol:{en:'No %s is linked in this volume.',
            es:'Ningún %s está enlazado en este volumen.'},
  // On the paragraph's own dimmed jump chip (2026-08-03).
  // !!! IT USED TO SAY "No %s is linked to this paragraph." and a reader read
  // that, reasonably, as "this passage has no Ṭīkā" — which is the one thing
  // that is NOT known.  The Aratisutta HAS a subcommentary record
  // (`20AnT03#57`); it is a `covered` fallback the builder invented, so it is
  // not shown.  Whether the Ṭīkā glosses the sutta is undetermined.  The gap is
  // ours, and the wording now says so.
  // `band_vol` and `band_layer` keep "is linked": they are scoped to a volume
  // and to what is on screen, where the misreading does not arise.
  band_para:{en:'No %s passage could be identified for this paragraph.',
             es:'No se ha podido identificar ningún pasaje de %s para este párrafo.'},
  // A CANON PARAGRAPH'S COMMENTARY IS A RANGE (2026-08-04, reader-reported).
  // The band now draws the whole printed section, not the first paragraph of
  // it, and the reader asked for a control because some runs are long — the
  // longest in `18Khu01` is 98 paragraphs.  The count is substituted for %s.
  run_more:{en:'Read more — %s more paragraphs of this section',
            es:'Leer más — %s párrafos más de esta sección'},
  run_less:{en:'Show less',es:'Mostrar menos'},
  // !!! A TAB OPENED BEFORE A DEPLOY NEVER LEARNED THERE HAD BEEN ONE
  // (2026-08-04).  The reader photographed a fault that had already been fixed
  // and shipped, because his tab was still running the previous document; see
  // `checkBuildLive` in reader2.html.  This is that tab saying so.
  newbuild:{en:'This page is not the version now published — what you are reading may be out of date.',
            es:'Esta página no es la versión publicada ahora — lo que estás leyendo puede estar desactualizado.'},
  newbuild_btn:{en:'Load the current version',es:'Cargar la versión actual'},
  lang_toggle:{en:'Cambiar a español',es:'Switch to English'},

  // landing
  land_sub:{en:'Chaṭṭha Saṅgāyana edition — Pāḷi Canon, Commentaries &amp; Subcommentaries',
            es:'Edición Chaṭṭha Saṅgāyana — Canon Pāḷi, Comentarios y Subcomentarios'},
  land_prov:{en:'Romanised from the edition published by the Ministry of Religious Affairs, Yangon (Pāḷi Series, 2008). A searchable, cross-referenced Unicode corpus of all 118 volumes.',
             es:'Romanizado de la edición publicada por el Ministerio de Asuntos Religiosos, Yangon (Serie Pāḷi, 2008). Un corpus Unicode de los 118 volúmenes, con búsqueda y referencias cruzadas.'},
  stat_volumes:{en:'volumes',es:'volúmenes'},
  stat_paragraphs:{en:'paragraphs',es:'párrafos'},
  stat_variants:{en:'variant readings',es:'lecturas variantes'},
  stat_layers:{en:'linked',es:'enlazadas'},
  land_layers3:{en:'3 layers',es:'3 capas'},
  btn_read:{en:'Read &amp; browse',es:'Leer y explorar'},
  btn_search:{en:'Search',es:'Buscar'},
  btn_download:{en:'Download PDFs',es:'Descargar PDF'},
  btn_about:{en:'About',es:'Acerca'},
  land_foot:{en:'Tipiṭaka · Aṭṭhakathā · Ṭīkā — navigate from any canon paragraph to its commentary and subcommentary. Diacritic-insensitive search across the whole corpus.',
             es:'Tipiṭaka · Aṭṭhakathā · Ṭīkā — navegue desde cualquier párrafo del canon a su comentario y subcomentario. Búsqueda insensible a diacríticos en todo el corpus.'},
  credits:{en:'<b>Editorial Board and Staff.</b> This Tipiṭaka material has been sponsored by the Venerable Aggasāmi, Mr. Tran Minh Loi, Mr. Tu Son, the Tathāgata Meditation Center, the Paññārāma Meditation Center, and devotees from Myanmar and Vietnam. This material is published by the Ministry of Religious Affairs of Myanmar for free distribution as a Gift of the Dhamma. Permission is granted to duplicate this material for free, non-commercial distribution. Comments and suggestions are welcome; please send them to <a href="mailto:buddhasasanasociety@gmail.com">buddhasasanasociety@gmail.com</a>. Version 01 — 10 November 2008. This site is a project of the Instituto de Estudios Buddhistas Hispano (IEBH) and Buddhismo Theravāda México-Hispano AR (BTHAR). For more information about this site and our projects, contact <a href="mailto:admin@iebh.org">admin@iebh.org</a> or <a href="mailto:admin@bthar.org">admin@bthar.org</a>.',
           es:'<b>Consejo Editorial y Staff.</b> Este material del Tipiṭaka ha sido patrocinado por el Venerable Aggasāmi, el Sr. Tran Minh Loi, el Sr. Tu Son, el Centro de Meditación Tathāgata, el Centro de Meditación Paññārāma y devotos de Myanmar y Vietnam. Este material está publicado por el Ministerio de Asuntos Religiosos de Myanmar para distribución gratuita como un Regalo del Dhamma. Se otorga permiso para duplicar este material para distribución gratuita, no comercial. Comentarios y sugerencias son bienvenidos; por favor envíelos a <a href="mailto:buddhasasanasociety@gmail.com">buddhasasanasociety@gmail.com</a>. Versión 01 — 10 de noviembre de 2008. Este sitio es un proyecto del Instituto de Estudios Buddhistas Hispano (IEBH) y de Buddhismo Theravāda México-Hispano AR (BTHAR). Para más información sobre este sitio y nuestros proyectos contactar <a href="mailto:admin@iebh.org">admin@iebh.org</a> o <a href="mailto:admin@bthar.org">admin@bthar.org</a>.'},

  // search page
  search_sub:{en:'Full-text search across 118 volumes — Tipiṭaka, Aṭṭhakathā, Ṭīkā · 83,751 paragraphs',
              es:'Búsqueda de texto completo en 118 volúmenes — Tipiṭaka, Aṭṭhakathā, Ṭīkā · 83.751 párrafos'},
  search_ph:{en:'Search Pāḷi — words, a phrase, * wildcard; diacritics optional',
             es:'Buscar en Pāḷi — palabras, una frase, comodín *; diacríticos opcionales'},
  opt_all:{en:'All layers',es:'Todas las capas'},
  lay_all:{en:'All',es:'Todas'},
  opt_pali:{en:'Pāḷi only',es:'Solo Pāḷi'},
  opt_atth:{en:'Aṭṭhakathā only',es:'Solo Aṭṭhakathā'},
  opt_tika:{en:'Ṭīkā only',es:'Solo Ṭīkā'},
  search_btn:{en:'Search',es:'Buscar'},
  search_foot:{en:'Type one word, several words, or a phrase — a phrase matches the words adjacent and in order; paragraphs carrying the words apart are listed separately. Diacritics are optional: nibbana finds nibbāna. * completes a word: dhamm*, *vaggo, dham*ti (at least 3 letters beside the *). A bare word also matches inside longer words. Results show the book, the printed page and the paragraph; click a result to open it in the reader at the marked word.',
               es:'Escriba una palabra, varias palabras o una frase — una frase encuentra las palabras adyacentes y en orden; los párrafos que llevan las palabras separadas se listan aparte. Los diacríticos son opcionales: nibbana encuentra nibbāna. * completa una palabra: dhamm*, *vaggo, dham*ti (mínimo 3 letras junto al *). Una palabra sola también coincide dentro de palabras más largas. Los resultados muestran el libro, la página impresa y el párrafo; haga clic en un resultado para abrirlo en el lector sobre la palabra marcada.'},
  s_loading:{en:'Loading term index…',es:'Cargando índice de términos…'},
  s_ready:{en:'Ready.',es:'Listo.'},
  s_open:{en:'open in reader →',es:'abrir en el lector →'},
  s_nomatch:{en:'No matches',es:'Sin resultados'},
  s_occ:{en:'occurrence(s)',es:'aparición(es)'},
  s_sections:{en:'Sections',es:'Secciones'},

  // reader
  r_selectvol:{en:'Select a volume at left.',es:'Seleccione un volumen a la izquierda.'},
  r_hint:{en:'Canon paragraphs carry jumps to their Aṭṭhakathā and Ṭīkā; commentary and subcommentary carry a link back to the canon.',
          es:'Los párrafos del canon incluyen saltos a su Aṭṭhakathā y Ṭīkā; el comentario y el subcomentario incluyen un enlace de vuelta al canon.'},
  r_loading:{en:'Loading',es:'Cargando'},
  grp_canon:{en:'Tipiṭaka (Canon)',es:'Tipiṭaka (Canon)'},
  grp_comm:{en:'Aṭṭhakathā (Commentary)',es:'Aṭṭhakathā (Comentario)'},
  grp_sub:{en:'Ṭīkā (Subcommentary)',es:'Ṭīkā (Subcomentario)'},
  r_paras:{en:'paragraphs',es:'párrafos'},
  r_page:{en:'page',es:'página'},
  r_cite:{en:'cite',es:'citar'},
  r_copied:{en:'copied ✓',es:'copiado ✓'},
  r_backcanon:{en:'↩ Canon',es:'↩ Canon'},
  r_viewpage:{en:'View printed page',es:'Ver la página impresa'},
  r_smaller:{en:'Smaller text',es:'Texto más pequeño'},
  r_larger:{en:'Larger text',es:'Texto más grande'},
  r_width:{en:'Reading width',es:'Ancho de lectura'},
  r_volumes:{en:'Volumes',es:'Volúmenes'},
  r_covered:{en:'covered by',es:'cubierto por'},

  // downloads
  dl_h1:{en:'Unicode PDF downloads',es:'Descargas de PDF Unicode'},
  dl_intro:{en:'The Sixth Council edition with a corrected Unicode text layer injected — pages render identically to the print, but text is searchable and copyable. Public domain.',
            es:'La edición del Sexto Concilio con una capa de texto Unicode corregida — las páginas se ven idénticas a la impresión, pero el texto se puede buscar y copiar. Dominio público.'},
  dl_note:{en:'<b>Provenance:</b> romanised edition, Ministry of Religious Affairs, Yangon (Pāḷi Series, 2008). Original page layout and printed page numbers preserved. Copy text with <b>Paste and Match Style</b> to avoid the legacy display font.',
           es:'<b>Procedencia:</b> edición romanizada, Ministerio de Asuntos Religiosos, Yangon (Serie Pāḷi, 2008). Se conservan el diseño de página original y los números de página impresos. Copie el texto con <b>Pegar y hacer coincidir el estilo</b> para evitar la fuente heredada.'},
  dl_canon:{en:'Tipiṭaka (Canon)',es:'Tipiṭaka (Canon)'},
  dl_comm:{en:'Aṭṭhakathā (Commentary)',es:'Aṭṭhakathā (Comentario)'},
  dl_sub:{en:'Ṭīkā (Subcommentary)',es:'Ṭīkā (Subcomentario)'}
};
// The variant sigla of the printed apparatus.  The siglum itself is the
// edition's and never changes; only the gloss beside it is interface text.
window.SIGLA={
  'Sī':{en:'Sīhaḷa (Sinhalese)',es:'Sīhaḷa (cingalés)'},
  'Syā':{en:'Syāma (Thai)',es:'Syāma (tailandés)'},
  'Kaṁ':{en:'Kamboja (Cambodian)',es:'Kamboja (camboyano)'},
  'I':{en:'PTS / English',es:'PTS / inglés'},
  'Ka':{en:'some Burmese mss',es:'algunos mss. birmanos'},
  'Ka-Sī':{en:'Ka + Sīhaḷa',es:'Ka + Sīhaḷa'},
  'katthaci':{en:'in some copies',es:'en algunas copias'},
  'sabbattha':{en:'in all copies',es:'en todas las copias'},
  'bahūsu':{en:'in many copies',es:'en muchas copias'}
};
window.sigla=function(s){ const e=window.SIGLA[s]; return e? (e[window.osbctLang()]||e.en) : s; };

window.osbctLang=function(){ let l=localStorage.getItem('osbct-lang'); if(!l){ l=(navigator.language||'en').toLowerCase().indexOf('es')===0?'es':'en'; } return l; };
window.t=function(k){ const e=window.I18N[k]; if(!e) return k; return e[osbctLang()]||e.en; };
window.osbctSetLang=function(l){ localStorage.setItem('osbct-lang',l); location.reload(); };
// THE SITE'S OWN VERSION, SAID ON EVERY PAGE (2026-08-09, reader request).
// One source, many displays: every element carrying class="sitever" is
// filled from here.  This project's citation metadata has been a release
// behind THREE times — a version painted on the site is one more place
// where that drift becomes visible instead of silent.  BUMPING THIS LINE
// IS PART OF TAGGING, beside CITATION.cff and .zenodo.json (the checklist
// there names this file now).
window.OSBCT_VERSION='v2.5.0';
document.addEventListener('DOMContentLoaded',function(){
  var els=document.querySelectorAll('.sitever');
  for(var i=0;i<els.length;i++) els[i].textContent=window.OSBCT_VERSION;
});
window.applyI18n=function(){
  const lang=osbctLang(); document.documentElement.lang=lang;
  document.querySelectorAll('[data-i18n]').forEach(el=>{ el.innerHTML=t(el.getAttribute('data-i18n')); });
  document.querySelectorAll('[data-i18n-ph]').forEach(el=>{ el.setAttribute('placeholder',t(el.getAttribute('data-i18n-ph'))); });
  // !!! WRITE TO `data-tip` ONCE THE ELEMENT HAS ONE.  `tipify` moves `title`
  // into `data-tip` so the custom tooltip can render it; if this kept writing
  // `title`, a language switch would hand the element BOTH and the browser
  // would draw its own tooltip over ours.
  document.querySelectorAll('[data-i18n-title]').forEach(el=>{
    el.setAttribute(el.hasAttribute('data-tip')?'data-tip':'title',
                    t(el.getAttribute('data-i18n-title'))); });
  document.querySelectorAll('.langbtn').forEach(b=>{ b.textContent = lang==='es'?'EN':'ES';
    // same rule as `data-i18n-title` above: never hand a tipified element a
    // `title` as well, or the browser draws its own tooltip over ours
    b.setAttribute(b.hasAttribute('data-tip')?'data-tip':'title', t('lang_toggle'));
    b.onclick=()=>osbctSetLang(lang==='es'?'en':'es'); });
};
document.addEventListener('DOMContentLoaded',window.applyI18n);
