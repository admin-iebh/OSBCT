# Render-vs-PDF verification report

Harness: `pipeline/verify_render_vs_pdf.py` (minw=4), 1 volumes, 1s.

`lines` / `chunks` = printed content missing from the render (drops). `rev` = rendered text that is not contiguous in the print (splices / fabrication). `dup` = rendered more often than printed.

**Clean (0/0/0/0): 1/1 volumes.**

`cover` = pages checked / pages in the PDF, and it has a CEILING WELL BELOW 100%: most volumes carry 60-100 pages of back matter (word, name and verse indices, Sodhanapattaṁ errata) plus front matter, none of which is body text.  19Khu02 is fully covered over its text and still reads 80%, because 96 of its 547 pages are indices.  So compare a volume's cover against ITS OWN text extent before reading it as lost extraction.  THE CHECKED RANGE IS NOW THE EXTENT THE PDF ITSELF DECLARES in its `Subject` metadata ("[327 pages = content 19 + text 298 + index 10]") — available for 116 of the 118 files, and validated against the eleven Khuddaka ranges this project measured by hand: it reproduces ten of them exactly and is one page tighter on the eleventh (18Khu01's tail page is blank).  01Vin01 and 02Vin02 merge text and index into one figure, so those two still fall back to the measured method.  A LOW cover therefore means the volume is mostly back matter, or that its extraction stopped short — read it against that volume's own text extent, not as a defect on its own.

| volume | layer | ¶ | pdf pages | cover | lines | chunks | rev | dup |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 20KhuA01 | commentary | 673 | 18–233 | 80% | 0 | 0 | 0 | 0 |

## Samples per volume (first 8 of each kind)
