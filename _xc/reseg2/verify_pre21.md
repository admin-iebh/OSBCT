# Render-vs-PDF verification report

Harness: `pipeline/verify_render_vs_pdf.py` (minw=4), 1 volumes, 2s.

`lines` / `chunks` = printed content missing from the render (drops). `rev` = rendered text that is not contiguous in the print (splices / fabrication). `dup` = rendered more often than printed.

**Clean (0/0/0/0): 0/1 volumes.**

`cover` = pages checked / pages in the PDF, and it has a CEILING WELL BELOW 100%: most volumes carry 60-100 pages of back matter (word, name and verse indices, Sodhanapattaṁ errata) plus front matter, none of which is body text.  19Khu02 is fully covered over its text and still reads 80%, because 96 of its 547 pages are indices.  So compare a volume's cover against ITS OWN text extent before reading it as lost extraction.  THE CHECKED RANGE IS NOW THE EXTENT THE PDF ITSELF DECLARES in its `Subject` metadata ("[327 pages = content 19 + text 298 + index 10]") — available for 116 of the 118 files, and validated against the eleven Khuddaka ranges this project measured by hand: it reproduces ten of them exactly and is one page tighter on the eleventh (18Khu01's tail page is blank).  01Vin01 and 02Vin02 merge text and index into one figure, so those two still fall back to the measured method.  A LOW cover therefore means the volume is mostly back matter, or that its extraction stopped short — read it against that volume's own text extent, not as a defect on its own.

| volume | layer | ¶ | pdf pages | cover | lines | chunks | rev | dup |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 21KhuA02 | commentary | 138 | 7–453 | 89% | 17 | 17 | 39 | 0 |

## Samples per volume (first 8 of each kind)

### 21KhuA02 (commentary)

*missing from render (line)*

- `ukkhitto”ti laddhiṁ ca, ukkhittānuvattakānaṁ dhammakathikaantevāsikānaṁ pana “adhimmikeneva kammena ukkhitto”ti laddhiṁ ca,`
- `nimantetvā punadivase mahādānaṁ datvā “bhante ito tesaṁ petānaṁ dibbaannapānaṁ sampajjatū”ti pattiṁ adāsi, tesaṁ tatheva nibbatti. Punadivase`
- `anāgate uppajjanakassa Gotamabuddhassa sāsane paṭhamaaggasāvakaṭṭhānaṁ patthitaṁ, tvaṁ dutiya-aggasāvakaṭṭhānaṁ pattehī’ti”.`
- `anāgate uppajjanakassa Gotamabuddhassa nāma sāsane paṭhamaaggasāvakaṭṭhānaṁ patthesiṁ, tvampi tassa sāsane dutiyaaggasāvakaṭṭhānaṁ patthehīti. Mayhaṁ `
- `ṭhito āha “bhante mama sahāyo Saradatāpaso yassa Satthussa paṭhamaaggasāvako bhaveyyan”ti patthesi, ahampi “tasseva dutiya-aggasāvako`
- `paññāya nisammakārino kāyādīhi saññatassa dhammajīvikaṁ jīvantassa satiavippavāse ṭhitassa issariyaṁ vaḍḍhatiyevā”ti vatvā imaṁ gāthamāha–`
- `attabhāvameva maṇḍayamānā kālaṁ vītināmesi. Maghopi mātāpituupaṭṭhānaṁ kule jeṭṭhāpacāyanakammaṁ1 saccavācaṁ apharusavācaṁ`
- `ahosi suvaṇṇavaṇṇā asādhāraṇāya rūpasiriyā samannāgatā. Vepacittiasurindo āgatāgatānaṁ asurānaṁ “tumhe mama dhītu anucchavikā na`

*missing from render (chunk)*

- `ukkhittānuvattakānaṁ dhammakathikaantevāsikānaṁ pana adhimmikeneva kammena ukkhitto ti laddhiṁ ca`
- `rājā buddhappamukhaṁ bhikkhusaṁghaṁ nimantetvā punadivase mahādānaṁ datvā bhante ito tesaṁ petānaṁ dibbaannapānaṁ sampajjatū ti pattiṁ adāsi`
- `saradatāpasopi antevāsikattherānaṁ santikaṁ gantvā sahāyakassa sirivaḍḍhanakuṭumbikassa sāsanaṁ pesesi bhante mama sahāyakassa vadetha sahāyakena te s`
- `ahaṁ satthu paṭhamaaggasāvakaṁ nisabhattheraṁ disvā anāgate uppajjanakassa gotamabuddhassa nāma sāsane paṭhamaaggasāvakaṭṭhānaṁ patthesiṁ`
- `tvampi tassa sāsane dutiyaaggasāvakaṭṭhānaṁ patthehīti`
- `so teneva niyāmena sattāhaṁ mahādānaṁ pavattetvā bhagavantaṁ vanditvā añjaliṁ paggayha ṭhito āha bhante mama sahāyo saradatāpaso yassa satthussa paṭha`
- `evarūpassa hi vīriyasampannassa satisampannassa kāyavācāhi parisuddhakammassa paññāya nisammakārino kāyādīhi saññatassa dhammajīvikaṁ jīvantassa satia`
- `maghopi mātāpituupaṭṭhānaṁ kule jeṭṭhāpacāyanakammaṁ saccavācaṁ apharusavācaṁ apisuṇavācaṁ maccheravinayaṁ akkodhananti imāni satta vatapadāni pūretvā`

*rendered but not contiguous in PDF*

- `ord19 [before] @5/6: ukkhitto ti laddhiṁ ca ukkhittānuvattakānaṁ dhammakathika`
- `ord19 [before] @1/8: antevāsikānaṁ pana adhimmikeneva kammena ukkhitto ti laddhiṁ ca`
- `ord24 [before] @8/9: datvā bhante ito tesaṁ petānaṁ dibba`
- `ord24 [before] @0/9: annapānaṁ sampajjatū ti pattiṁ adāsi tesaṁ tatheva`
- `ord24 [before] @4/5: anāgate uppajjanakassa gotamabuddhassa sāsane paṭhama`
- `ord24 [before] @1/6: aggasāvakaṭṭhānaṁ patthitaṁ tvaṁ dutiyaaggasāvakaṭṭhānaṁ pattehī ti`
- `ord24 [before] @5/6: anāgate uppajjanakassa gotamabuddhassa nāma sāsane paṭhama`
- `ord24 [before] @1/6: aggasāvakaṭṭhānaṁ patthesiṁ tvampi tassa sāsane dutiya`
