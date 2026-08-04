# Render-vs-PDF verification report

Harness: `pipeline/verify_render_vs_pdf.py` (minw=4), 2 volumes, 4s.

`lines` / `chunks` = printed content missing from the render (drops). `rev` = rendered text that is not contiguous in the print (splices / fabrication). `dup` = rendered more often than printed.

**Clean (0/0/0/0): 0/2 volumes.**

`cover` = pages checked / pages in the PDF, and it has a CEILING WELL BELOW 100%: most volumes carry 60-100 pages of back matter (word, name and verse indices, Sodhanapattaṁ errata) plus front matter, none of which is body text.  19Khu02 is fully covered over its text and still reads 80%, because 96 of its 547 pages are indices.  So compare a volume's cover against ITS OWN text extent before reading it as lost extraction.  THE CHECKED RANGE IS NOW THE EXTENT THE PDF ITSELF DECLARES in its `Subject` metadata ("[327 pages = content 19 + text 298 + index 10]") — available for 116 of the 118 files, and validated against the eleven Khuddaka ranges this project measured by hand: it reproduces ten of them exactly and is one page tighter on the eleventh (18Khu01's tail page is blank).  01Vin01 and 02Vin02 merge text and index into one figure, so those two still fall back to the measured method.  A LOW cover therefore means the volume is mostly back matter, or that its extraction stopped short — read it against that volume's own text extent, not as a defect on its own.

| volume | layer | ¶ | pdf pages | cover | lines | chunks | rev | dup |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 23KhuA04 | commentary | 98 | 7–399 | 82% | 3 | 2 | 6 | 0 |
| 24KhuA05 | commentary | 115 | 8–362 | 81% | 1 | 1 | 2 | 0 |

## Samples per volume (first 8 of each kind)

### 23KhuA04 (commentary)

*missing from render (line)*

- `Yañca uparimaheṭṭhimapurimapacchimakāyehi dakkhiṇavāmaakkhikaṇṇasota-nāsikasota-aṁsakūṭahatthapādehi2 aṅguli-aṅgulantarehi`
- `avūpasanto, sasallo lokasannivāso viddho puthusallehi, avijjandhakārāvaraṇo kilesapañjarapakkhitto, avijjāgato lokasannivāso aṇḍabhūto.`
- `Yathā cetesaṁ ñāṇānaṁ vasena, evaṁ yathāvuttānaṁ satipaṭṭhānasammappadhānavibhāvanañāṇādīnaṁ anantāparimeyyabhedānaṁ`

*missing from render (chunk)*

- `yañca uparimaheṭṭhimapurimapacchimakāyehi dakkhiṇavāmaakkhikaṇṇasotanāsikasotaaṁsakūṭahatthapādehi aṅguliaṅgulantarehi lomakūpehi ca aggikkhandhūdakad`
- `evaṁ yathāvuttānaṁ satipaṭṭhānasammappadhānavibhāvanañāṇādīnaṁ anantāparimeyyabhedānaṁ anaññasādhāraṇānaṁ paññāvisesānaṁ vasena bhagavā tathāni ñāṇāni`

*rendered but not contiguous in PDF*

- `ord21 [after] @9/10: satte jānātī tiādi yañca uparimaheṭṭhimapurimapacchimakāyehi dakkhiṇavāma`
- `ord21 [after] @0/12: akkhikaṇṇasotanāsikasotaaṁsakūṭahatthapādehi aṅguliaṅgulantarehi lomakūpehi ca aggikkhandhūdakadhārāpavattanaṁ anaññasādhāraṇaṁ v`
- `ord21 [after] @5/6: avūpasanto sasallo lokasannivāso viddho puthusallehi avijjandha`
- `ord21 [after] @0/255: kārāvaraṇo kilesapañjarapakkhitto avijjāgato lokasannivāso aṇḍabhūto pariyonaddho tantākulakajāto`
- `ord21 [after] @15/16: cetesaṁ ñāṇānaṁ vasena evaṁ yathāvuttānaṁ satipaṭṭhāna`
- `ord21 [after] @0/15: sammappadhānavibhāvanañāṇādīnaṁ anantāparimeyyabhedānaṁ anaññasādhāraṇānaṁ paññāvisesānaṁ vasena bhagavā tathāni`

### 24KhuA05 (commentary)

*missing from render (line)*

- `Yañca uparimaheṭṭhimapuratthimapacchimakāyehi dakkhiṇavāmaakkhikaṇṇasotanāsikāsota-aṁsakūṭapassahatthapādehi aṅgulaṅgulantarehi`

*missing from render (chunk)*

- `yañca uparimaheṭṭhimapuratthimapacchimakāyehi dakkhiṇavāmaakkhikaṇṇasotanāsikāsotaaṁsakūṭapassahatthapādehi aṅgulaṅgulantarehi lomalomakūpehi ca aggik`

*rendered but not contiguous in PDF*

- `ord39 [after] @9/10: satte jānātī tiādi yañca uparimaheṭṭhimapuratthimapacchimakāyehi dakkhiṇavāma`
- `ord39 [after] @0/12: akkhikaṇṇasotanāsikāsotaaṁsakūṭapassahatthapādehi aṅgulaṅgulantarehi lomalomakūpehi ca aggikkhandhūdakadhārāpavattanaṁ anaññasādh`
