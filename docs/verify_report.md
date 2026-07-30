# Render-vs-PDF verification report

Harness: `pipeline/verify_render_vs_pdf.py` (minw=4), 118 volumes, 0s.

`lines` / `chunks` = printed content missing from the render (drops). `rev` = rendered text that is not contiguous in the print (splices / fabrication). `dup` = rendered more often than printed.

**Clean (0/0/0/0): 52/118 volumes.**

`cover` = pages checked / pages in the PDF, and it has a CEILING WELL BELOW 100%: most volumes carry 60-100 pages of back matter (word, name and verse indices, Sodhanapattaṁ errata) plus front matter, none of which is body text.  19Khu02 is fully covered over its text and still reads 80%, because 96 of its 547 pages are indices.  So compare a volume's cover against ITS OWN text extent before reading it as lost extraction.  THE CHECKED RANGE IS NOW THE EXTENT THE PDF ITSELF DECLARES in its `Subject` metadata ("[327 pages = content 19 + text 298 + index 10]") — available for 116 of the 118 files, and validated against the eleven Khuddaka ranges this project measured by hand: it reproduces ten of them exactly and is one page tighter on the eleventh (18Khu01's tail page is blank).  01Vin01 and 02Vin02 merge text and index into one figure, so those two still fall back to the measured method.  A LOW cover therefore means the volume is mostly back matter, or that its extraction stopped short — read it against that volume's own text extent, not as a defect on its own.

| volume | layer | ¶ | pdf pages | cover | lines | chunks | rev | dup |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 01ViT01 | subcommentary | 23 | 15–474 | 89% | 6241 | 4144 | 1 | 0 |
| 01Vin01 | canon | 662 | 23–403 | 89% | 0 | 0 | 0 | 0 |
| 01VinA01 | commentary | 175 | 14–358 | 86% | 7 | 4 | 15 | 0 |
| 02ViT02 | subcommentary | 314 | 9–456 | 88% | 843 | 592 | 4 | 0 |
| 02Vin02 | canon | 1249 | 14–483 | 92% | 0 | 0 | 0 | 0 |
| 02VinA02 | commentary | 240 | 6–317 | 87% | 0 | 0 | 0 | 0 |
| 03ViT03 | subcommentary | 648 | 21–516 | 88% | 169 | 92 | 5 | 0 |
| 03Vin03 | canon | 490 | 14–524 | 76% | 0 | 0 | 0 | 0 |
| 03VinA03 | commentary | 738 | 11–447 | 89% | 0 | 2 | 0 | 0 |
| 04ViT04 | subcommentary | 280 | 9–370 | 90% | 2376 | 1666 | 5 | 0 |
| 04Vin04 | canon | 458 | 11–518 | 92% | 0 | 0 | 0 | 0 |
| 04VinA04 | commentary | 300 | 11–275 | 87% | 8 | 8 | 16 | 0 |
| 05Kankha | commentary | 932 | 19–375 | 85% | 0 | 0 | 3 | 0 |
| 05ViT05 | subcommentary | 673 | 18–339 | 89% | 181 | 103 | 0 | 0 |
| 05Vin05 | canon | 519 | 14–403 | 89% | 0 | 0 | 0 | 0 |
| 06Di01 | canon | 559 | 18–253 | 89% | 0 | 0 | 0 | 0 |
| 06ViT06 | subcommentary | 814 | 27–611 | 89% | 1969 | 1416 | 11 | 0 |
| 06VinSg06 | commentary | 327 | 5–472 | 99% | 0 | 0 | 0 | 0 |
| 07Di02 | canon | 444 | 9–291 | 91% | 0 | 0 | 0 | 0 |
| 07DiA01 | commentary | 334 | 16–353 | 77% | 3 | 4 | 6 | 0 |
| 07ViT07 | subcommentary | 22 | 21–509 | 93% | 11983 | 9474 | 4 | 0 |
| 08Di03 | canon | 360 | 9–268 | 87% | 0 | 0 | 0 | 0 |
| 08DiA02 | commentary | 345 | 9–411 | 91% | 4 | 2 | 8 | 0 |
| 08DiT01 | subcommentary | 303 | 18–422 | 91% | 1032 | 678 | 3 | 0 |
| 09DiA03 | commentary | 293 | 9–260 | 85% | 4 | 7 | 8 | 0 |
| 09DiT02 | subcommentary | 80 | 5–504 | 95% | 4029 | 2953 | 2 | 0 |
| 09Ma01 | canon | 511 | 15–429 | 92% | 0 | 0 | 0 | 0 |
| 10DiT03 | subcommentary | 245 | 8–444 | 93% | 63 | 9 | 3 | 0 |
| 10Ma02 | canon | 485 | 6–444 | 92% | 0 | 1 | 0 | 1 |
| 10MaA01 | commentary | 197 | 17–414 | 89% | 10 | 9 | 22 | 0 |
| 11DiT04 | subcommentary | 336 | 10–367 | 91% | 18 | 6 | 4 | 0 |
| 11Ma03 | canon | 462 | 6–357 | 92% | 0 | 0 | 0 | 0 |
| 11MaA02 | commentary | 256 | 5–324 | 84% | 4 | 3 | 8 | 0 |
| 12DiT05 | subcommentary | 293 | 9–300 | 93% | 120 | 73 | 6 | 0 |
| 12MaA03 | commentary | 354 | 6–314 | 82% | 0 | 0 | 0 | 0 |
| 12Sam01 | canon | 517 | 39–510 | 85% | 0 | 0 | 0 | 0 |
| 13MaA04 | commentary | 306 | 6–259 | 87% | 2 | 2 | 3 | 0 |
| 13MaT01 | subcommentary | 133 | 17–410 | 92% | 2069 | 1439 | 4 | 0 |
| 13Sam02 | canon | 722 | 18–584 | 93% | 0 | 0 | 0 | 0 |
| 14MaT02 | subcommentary | 309 | 6–329 | 92% | 119 | 91 | 2 | 0 |
| 14Sam03 | canon | 598 | 18–432 | 91% | 1 | 1 | 2 | 0 |
| 14SamA01 | commentary | 254 | 25–349 | 81% | 1 | 1 | 2 | 0 |
| 15An01 | canon | 952 | 32–611 | 88% | 0 | 0 | 0 | 0 |
| 15MaT03 | subcommentary | 639 | 9–450 | 95% | 4 | 2 | 1 | 0 |
| 15SamA02 | commentary | 300 | 19–342 | 83% | 0 | 0 | 0 | 0 |
| 16An02 | canon | 497 | 18–530 | 90% | 0 | 0 | 0 | 0 |
| 16SaT01 | subcommentary | 287 | 25–369 | 87% | 43 | 15 | 1 | 0 |
| 16SamA03 | commentary | 389 | 23–363 | 81% | 0 | 0 | 0 | 0 |
| 17An03 | canon | 426 | 23–580 | 91% | 0 | 0 | 3 | 0 |
| 17AnA01 | commentary | 229 | 17–432 | 87% | 2 | 1 | 4 | 0 |
| 17SaT02 | subcommentary | 655 | 36–586 | 89% | 107 | 48 | 1 | 0 |
| 18AnA02 | commentary | 465 | 19–415 | 77% | 2 | 1 | 4 | 0 |
| 18AnT01 | subcommentary | 218 | 17–304 | 90% | 70 | 19 | 3 | 0 |
| 18Khu01 | canon | 1869 | 25–479 | 82% | 0 | 0 | 0 | 0 |
| 19AnA03 | commentary | 517 | 27–383 | 74% | 0 | 0 | 0 | 0 |
| 19AnT02 | subcommentary | 362 | 17–412 | 91% | 13 | 5 | 3 | 0 |
| 19Khu02 | canon | 3660 | 16–450 | 80% | 0 | 0 | 0 | 0 |
| 20AnT03 | subcommentary | 339 | 19–389 | 91% | 45 | 14 | 1 | 0 |
| 20Khu03 | canon | 4461 | 20–464 | 87% | 0 | 0 | 0 | 0 |
| 20KhuA01 | commentary | 109 | 18–233 | 80% | 0 | 1 | 0 | 0 |
| 21Khu04 | canon | 4858 | 15–434 | 86% | 0 | 0 | 0 | 0 |
| 21KhuA02 | commentary | 138 | 7–453 | 89% | 17 | 17 | 39 | 0 |
| 21KhuT01 | subcommentary | 274 | 7–513 | 95% | 1780 | 1120 | 2 | 0 |
| 22AbhiT01 | subcommentary | 431 | 21–465 | 95% | 2517 | 1392 | 8 | 0 |
| 22Khu05 | canon | 2985 | 26–425 | 77% | 0 | 0 | 0 | 0 |
| 22KhuA03 | commentary | 331 | 12–467 | 86% | 17 | 16 | 32 | 0 |
| 23AbhiT02 | subcommentary | 492 | 15–478 | 92% | 1837 | 1082 | 71 | 0 |
| 23Khu06 | canon | 3675 | 5–382 | 77% | 0 | 0 | 0 | 0 |
| 23KhuA04 | commentary | 98 | 7–399 | 82% | 3 | 2 | 6 | 0 |
| 24AbhiT03 | subcommentary | 963 | 36–606 | 92% | 1450 | 947 | 5 | 0 |
| 24Khu07 | canon | 212 | 4–413 | 84% | 0 | 0 | 0 | 0 |
| 24KhuA05 | commentary | 115 | 8–362 | 81% | 1 | 1 | 2 | 0 |
| 25Khu08 | canon | 335 | 5–311 | 88% | 0 | 0 | 0 | 0 |
| 25KhuA06 | commentary | 264 | 4–317 | 81% | 1 | 4 | 2 | 0 |
| 25VsmT01 | subcommentary | 351 | 8–468 | 88% | 22 | 2 | 3 | 0 |
| 26Khu09 | canon | 405 | 9–427 | 92% | 0 | 0 | 0 | 0 |
| 26KhuA07 | commentary | 736 | 6–329 | 77% | 4 | 6 | 2 | 0 |
| 26VsmT02 | subcommentary | 520 | 8–542 | 94% | 2 | 1 | 4 | 0 |
| 27Khu10 | canon | 271 | 6–346 | 88% | 0 | 0 | 0 | 0 |
| 27KhuA08 | commentary | 1480 | 7–341 | 77% | 0 | 1 | 0 | 0 |
| 28Khu11 | canon | 261 | 14–421 | 89% | 0 | 0 | 0 | 0 |
| 28KhuA09 | commentary | 1121 | 6–275 | 75% | 0 | 0 | 0 | 0 |
| 29Abhi01 | canon | 1780 | 19–316 | 91% | 0 | 0 | 0 | 0 |
| 29KhuA10 | commentary | 453 | 11–495 | 75% | 0 | 1 | 0 | 0 |
| 30Abhi02 | canon | 1044 | 11–463 | 95% | 0 | 0 | 0 | 0 |
| 30KhuA11 | commentary | 1101 | 7–552 | 79% | 0 | 0 | 0 | 0 |
| 31Abhi03 | canon | 890 | 7–191 | 89% | 0 | 0 | 0 | 0 |
| 31KhuA12 | commentary | 590 | 7–311 | 76% | 0 | 0 | 0 | 0 |
| 32Abhi04 | canon | 918 | 14–467 | 92% | 0 | 0 | 0 | 0 |
| 32KhuA13 | commentary | 506 | 4–355 | 79% | 0 | 0 | 0 | 0 |
| 33Abhi05 | canon | 762 | 11–275 | 94% | 0 | 0 | 0 | 0 |
| 33KhuA14 | commentary | 727 | 13–315 | 81% | 1 | 0 | 2 | 0 |
| 34Abhi06 | canon | 627 | 11–326 | 94% | 0 | 0 | 0 | 0 |
| 34KhuA15 | commentary | 945 | 5–358 | 78% | 0 | 0 | 0 | 0 |
| 35Abhi07 | canon | 714 | 9–338 | 95% | 0 | 0 | 0 | 0 |
| 35KhuA16 | commentary | 339 | 5–332 | 85% | 0 | 0 | 1 | 0 |
| 36Abhi08 | canon | 1091 | 29–492 | 93% | 0 | 0 | 0 | 0 |
| 36KhuA17 | commentary | 193 | 10–547 | 85% | 11 | 12 | 19 | 0 |
| 37Abhi09 | canon | 1268 | 27–519 | 93% | 0 | 0 | 0 | 0 |
| 37KhuA18 | commentary | 380 | 10–417 | 84% | 18 | 21 | 36 | 0 |
| 38Abhi10 | canon | 2060 | 6–610 | 98% | 0 | 0 | 0 | 0 |
| 38KhuA19 | commentary | 856 | 10–526 | 83% | 12 | 24 | 32 | 0 |
| 39Abhi11 | canon | 2985 | 9–644 | 98% | 0 | 0 | 0 | 0 |
| 39KhuA20 | commentary | 1158 | 7–510 | 82% | 7 | 19 | 22 | 0 |
| 40Abhi12 | canon | 2413 | 4–445 | 98% | 0 | 0 | 0 | 0 |
| 40KhuA21 | commentary | 1583 | 5–557 | 82% | 28 | 29 | 52 | 0 |
| 41KhuA22 | commentary | 818 | 4–335 | 81% | 6 | 11 | 16 | 0 |
| 42KhuA23 | commentary | 1690 | 4–390 | 77% | 1 | 9 | 11 | 0 |
| 43KhuA24 | commentary | 214 | 4–422 | 78% | 3 | 4 | 6 | 0 |
| 44KhuA25 | commentary | 152 | 5–144 | 78% | 0 | 0 | 0 | 0 |
| 45KhuA26 | commentary | 154 | 5–280 | 94% | 0 | 0 | 0 | 0 |
| 46KhuA27 | commentary | 185 | 6–350 | 85% | 0 | 0 | 0 | 0 |
| 47KhuA28 | commentary | 214 | 7–329 | 81% | 0 | 0 | 0 | 0 |
| 48AbhiA01 | commentary | 344 | 15–468 | 83% | 23 | 19 | 48 | 0 |
| 49AbhiA02 | commentary | 335 | 9–516 | 96% | 20 | 13 | 39 | 2 |
| 50AbhiA03 | commentary | 883 | 13–511 | 93% | 20 | 18 | 46 | 0 |
| 51Vism01 | commentary | 364 | 7–376 | 90% | 2 | 2 | 4 | 0 |
| 52Vism02 | commentary | 532 | 7–362 | 90% | 0 | 3 | 0 | 0 |

## Samples per volume (first 8 of each kind)

### 01ViT01 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Mahākāruṇikaṁ buddhaṁ, dhammañca vimalaṁ varaṁ.`
- `Vande ariyasaṁghañca, dakkhiṇeyyaṁ niraṅgaṇaṁ.`
- `Uḷārapuññatejena, katvā sattuvimaddanaṁ.`
- `Pattarajjābhisekena, sāsanujjotanatthinā.`
- `Nissāya sīhaḷindena, yaṁ parakkamabāhunā.`
- `Katvā nikāyasāmaggiṁ, sāsanaṁ suvisodhitaṁ.`
- `Kassapaṁ taṁ mahātheraṁ, saṁghassa pariṇāyakaṁ.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `pākaṭaṁ gagane candamaṇḍalaṁ viya sāsane`
- `yaṁ nissāya vasanto haṁ`
- `porāṇehi kataṁ yaṁ tu`
- `na taṁ sabbattha bhikkhūnaṁ`
- `vinayasaṁvaṇṇanārambhe ratanattayaṁ namassitukāmo tassa visiṭṭhaguṇayogasandassanatthaṁ yo kappakoṭīhipī tiādimāha`
- `vandanārahe ca katā vandanā yathādhippetamatthaṁ sādheti`
- `ettha ca saṁvaṇṇanārambhe ratanattayapaṇāmakaraṇappayojanaṁ tattha tattha bahudhā papañcenti ācariyā`

*rendered but not contiguous in PDF*

- `ord10 [text] @962/2779: samādhipariyosānāva jhānassa pubbapaṭipadā kathitāti daṭṭhabbaṁ idāni vivicceva kāmehī tiādinayappavattāya pāḷiyā jhānavibhaṅg`

### 01VinA01 (commentary)

*missing from render (line)*

- `kāmarāgasaṁyojanānaṁ, dutiyena avasesa-oghayogāsavaupādānaganthasaṁyojanānaṁ. Paṭhamena ca taṇhāya`
- `upacārena aṭṭha samāpattiyo vuccanti. Kasmā? Kasiṇādiārammaṇūpanijjhāyanato. Lakkhaṇūpanijjhānanti vipassanāmaggaphalāni`
- `pīti sukhaṁ cittekaggatāti etesu. Etāneva hissa “savitakkaṁ savicāran”tiādinā nayena aṅgabhāvena vuttāni. Avuttattā ekaggatā aṅgaṁ na hotīti ce.`
- `sevāmi payirupāsāmi, evaṁ vā jānāmi bujjhāmīti. Yesaṁ hi dhātūnaṁ gatiattho, buddhipi tesaṁ attho. Tasmā “gacchāmī”ti imassa jānāmi bujjhāmīti`
- `Diṭṭhisīlasaṅghātena saṁhatoti saṁgho, so atthato aṭṭhaariyapuggalasamūho. Vuttañhetaṁ tasmiṁyeva Vimāne–`
- `vā4, anujānāmi bhikkhave vihāraggena vā pariveṇaggena vā bhājetun”tiādīsu5 koṭṭhāse. “Yāvatā bhikkhave sattā apadā vā dvipadā vā -paTathāgato tesaṁ ag`
- `dassitāni, tesampi na sabbesaṁ attho pakāsito. Evamimasmiṁ ṭhāne sabbaaṭṭhakathā ākulā luḷitā duviññeyyavinicchayā, tasmā pañca pañcake`

*missing from render (chunk)*

- `etāneva hissa savitakkaṁ savicāran tiādinā nayena aṅgabhāvena vuttāni`
- `yesaṁ hi dhātūnaṁ gatiattho`
- `anujānāmi bhikkhave vihāraggena vā pariveṇaggena vā bhājetun tiādīsu koṭṭhāse`
- `evamimasmiṁ ṭhāne sabbaaṭṭhakathā ākulā luḷitā duviññeyyavinicchayā`

*rendered but not contiguous in PDF*

- `ord14 [text] @7/88: hessati vaṇṇanāpi sakkacca tasmā anusikkhitabbāti tattha taṁ vaṇṇayissaṁ vinayanti vuttattā vinayo tāva`
- `ord30 [before] @2/3: kāmarāgasaṁyojanānaṁ dutiyena avasesaoghayogāsava`
- `ord30 [before] @0/4: upādānaganthasaṁyojanānaṁ paṭhamena ca taṇhāya`
- `ord30 [before] @5/6: upacārena aṭṭha samāpattiyo vuccanti kasmā kasiṇādi`
- `ord30 [before] @0/3: ārammaṇūpanijjhāyanato lakkhaṇūpanijjhānanti vipassanāmaggaphalāni`
- `ord30 [before] @8/9: etesu etāneva hissa savitakkaṁ savicāran ti`
- `ord30 [before] @0/10: ādinā nayena aṅgabhāvena vuttāni avuttattā ekaggatā aṅgaṁ`
- `ord37 [before] @9/10: jānāmi bujjhāmīti yesaṁ hi dhātūnaṁ gati`

### 02ViT02 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Vinayadharassa ca lakkhaṇādikathāvaṇṇanā.`
- `Tasmāti yasmā pana-saddaṁ apanetvā aniyamena puggaladīpakaṁ`
- `yosaddameva āha, tasmā. Etthāti imasmiṁ yo-sadde. Pana-saddassa`
- `nipātamattattā yo-saddasseva atthaṁ pakāsento “yo kocīti vuttaṁ hotī”ti`
- `āha. Yo koci nāmāti yo vā so vā yo kocīti vutto. Vāsadhurayutto vāti`
- `vipassanādhurayutto vā. Sīlesūti pakatīsu.`
- `Bhikkhatīti yācati. Labhanto vā alabhanto vāti yo koci bhikkhati`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `tasmāti yasmā panasaddaṁ apanetvā aniyamena puggaladīpakaṁ yosaddameva āha`
- `panasaddassa nipātamattattā yosaddasseva atthaṁ pakāsento yo kocīti vuttaṁ hotī ti āha`
- `yo koci nāmāti yo vā so vā yo kocīti vutto`
- `vāsadhurayutto vāti vipassanādhurayutto vā`
- `labhanto vā alabhanto vāti yo koci bhikkhati bhikkhaṁ esati gavesati`
- `so taṁ labhatu vā mā vā`
- `tathāpi bhikkhatīti bhikkhūti ayamettha adhippāyo`

*rendered but not contiguous in PDF*

- `ord22 [text] @9/1341: suttanti vadanti upāligāthāsūtiṁ dhīrassa vigatamohassa anīghassa susamacittassa vesamantarassa vimalassa bhagavato tassa sāvako`
- `ord41 [text] @335/1016: tesaṁ byākaraṇagāthā ahosi saroruhaṁ padumapalāsamatrajaṁ aniccatā yaṁ vayataṁ viditvā eko care khaggavisāṇakappo`
- `ord47 [text] @751/1338: dātabbo ti rukkhapabbatādisaññāṇena niyamitappadesassetaṁ adhivacanaṁ ākulāti saṅkulā luḷitāti viloḷitā katthacīti ekissāya aṭ`
- `ord98 [text] @888/1136: vadanti adhiṭṭhāyāti mātikāvasena āṇattikapayogakathāvaṇṇanā niṭṭhitā evaṁ āṇāpentassa ācariyassa tāva dukkaṭanti sace sā`

### 03ViT03 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `537-542-547. Aṭṭhamanavamadasamesu natthi vattabbaṁ, aṅgānipi`
- `sattameva vuttanayeneva veditabbāni.`
- `6. Pāṭidesanīyakaṇḍa.`
- `7. Sekhiyakaṇḍa.`
- `Sekhiyesu sikkhitasikkhenāti catūhi maggehi tisso sikkhā sikkhitvā`
- `ṭhitena, sabbaso pariniṭṭhitakiccenāti vuttaṁ hoti. Tādināti aṭṭhahi`
- `lokadhammehi akampiyaṭṭhena tādinā.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `aṅgānipi sattameva vuttanayeneva veditabbāni`
- `sekhiyesu sikkhitasikkhenāti catūhi maggehi tisso sikkhā sikkhitvā ṭhitena`
- `sabbaso pariniṭṭhitakiccenāti vuttaṁ hoti`
- `tādināti aṭṭhahi lokadhammehi akampiyaṭṭhena tādinā`
- `iti samantapāsādikāya vinayaṭṭhakathāya sāratthadīpaniyaṁ bhikkhu vibhaṅgavaṇṇanā niṭṭhitā`
- `namo tassa bhagavato arahato sammāsambuddhassa`
- `giraggasamajjādīni acittakāni lokavajjānīti vuttattā naccanti vā vaṇṇakanti vā ajānitvāva passantiyā vā nahāyantiyā vā āpattisambhavato vatthuajānanac`

*rendered but not contiguous in PDF*

- `ord241 [text] @314/1382: dukkhāti munīdha jātiṁ dukkhaṁ tiracchesu kasāpatodayaṁ taṁ kathaṁ tattha bhaveyya jātiṁ vinā`
- `ord272 [text] @128/947: tattha na tassa addiṭṭhamidhatthi kiñci sabbaṁ abhiññāsi yadatthi neyyaṁ tathāgato tena samantacakkhū`
- `ord298 [text] @287/977: narasīhagāthāhi nāma aṭṭhahi gāthāhīti siniddhanīlamudukuñcitakeso yuttatuṅgamudukāyatanāso evamādikāhi aṭṭhahi gāthāhi gaṇṭhi`
- `ord382 [text] @1184/2025: nisīdi varamāsane tahiṁ nisinno naradammasārathi buddhāsane majjhagato virocati suvaṇṇanekkhaṁ viya paṇḍukambale nekkhaṁ`
- `ord508 [text] @24/666: kukkuccavinodanatthāya tampi saṁghabhattaṁ anto katvā attano vihāradvāreti vihārassa dvārakoṭṭhakasamīpaṁ sandhāya vuttaṁ bhoja`

### 03VinA03 (commentary)

*missing from render (chunk)*

- `samantapāsādikāya vinayasaṁvaṇṇanāya bhikkhunīvibhaṅgavaṇṇanā niṭṭhitā`
- `dvāsattatiadhikavatthusatapaṭimaṇḍitassa mahākhandhakassa atthavaṇṇanā niṭṭhitā`

### 04ViT04 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Karuṇāpuṇṇahadayaṁ, sugataṁ hitadāyakaṁ.`
- `Natvā dhammañca vimalaṁ, saṁghañca guṇasampadaṁ.`
- `Vaṇṇanā nipuṇāhesuṁ, vinayaṭṭhakathāya yā.`
- `Pubbakehi katā nekā, nānānayasamākulā.`
- `Tattha kāci suvitthiṇṇā, dukkhogāhā ca ganthato.`
- `Viraddhā atthato cāpi, saddato cāpi katthaci.`
- `Kāci katthaci apuṇṇā, kāci sammohakārinī.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `vinayasaṁvaṇṇanārambhe ratanattayaṁ namassitukāmo tassa visiṭṭhaguṇayogasandassanatthaṁ yo kappakoṭīhipītiādimāha`
- `ettha ca saṁvaṇṇanārambhe ratanattayapaṇāmakaraṇappayojanaṁ`
- `tattha tattha bahudhā papañcenti ācariyā`
- `mayaṁ pana idhādhippetameva payojanaṁ dassayissāma`
- `tasmā saṁvaṇṇanārambhe ratanattayapaṇāmakaraṇaṁ yathāpaṭiññātasaṁvaṇṇanāya anantarāyena parisamāpanatthanti veditabbaṁ`
- `tathā hi vuttaṁ tassānubhāvena hatantarāyo ti`
- `ratanattayapaṇāmakaraṇena hi rāgādidosavigamato paññādiguṇapāṭavato āyuādivaḍḍhanato puññātisayabhāvādito ca hoteva yathāpaṭiññātasaṁvaṇṇanāya anantar`

*rendered but not contiguous in PDF*

- `ord7 [text] @246/1309: lobhassa pavattiākārabhedena avatthābhedena ca vutto seyyathidanti taṁ kathanti attho etanti pubbapadeyeva avadhāraṇakaraṇaṁ`
- `ord41 [text] @307/644: saṅkocaṁ anāpajjantena niravasesādhippāyakathane sañjātussāhenāti attho pārājikavatthubhūtāti yesaṁ tīsu maggesu tilabījamattam`
- `ord60 [text] @467/908: dātabbo ti rukkhapabbatādisaññāṇena niyamitabbadesassetaṁ adhivacanaṁ katthacīti ekissā aṭṭhakathāyaṁ ekaṁ pañcakaṁ dassitanti `
- `ord83 [text] @15/116: pana abhiyuñjanādīsu pariyāyenapi mokkho natthi oṇirakkhakathāyaṁ oṇinti oṇītaṁ ānītanti attho oṇirakkhassa santike`
- `ord89 [text] @69/137: parānuddayatāya ca na gahetabban ti bahu ekato dāruādibhāriyassa ekassa bhaṇḍassa ukkhipanakāle gaṇhatha`

### 04VinA04 (commentary)

*missing from render (line)*

- `parivattetvā gahetabbaṁ. Na kevalaṁ mañcena mañcoyeva, ārāmaārāmavatthuvihāravihāravatthupīṭhabhisibimbohanānipi parivattetuṁ`
- `dinnakālato paṭṭhāya garubhaṇḍāni. Tipukoṭṭakasuvaṇṇakāracammakāraupakaraṇesupi eseva nayo. Ayaṁ pana viseso, tipukoṭṭaka-upakaraṇesupi`
- `dutiyavāre āraddhe saṁghatoyeva gahetvā gantabbaṁ. Abhinavaāgantukāva hutvā ñātī vā upaṭṭhāke vā passissāmāti gacchanti, tatra tesaṁ`
- `vīthivasena vā vīthiyaṁ ekagehavasena vā kulavasena vā gāhetabbā. Vīthiādīsu ca yattha bahūni bhattāni, tattha gāme vuttanayeneva bahūnaṁ`
- `uddesabhattasadisaṁ na hoti, vihārameva sandhāya diyyati, tasmā bahiupacāre gāhetuṁ na vaṭṭati. “Sve paṭṭhāyā”ti vutte pana vihāre`
- `vā panthaṁ rundhanti udakaṁ vā, devo vā vassati, sattho vā na gacchati, saussāhena bhuñjitabbaṁ. Ete upaddave olokentena dve tayo divase bhuñjituṁ`
- `Yaṁ pana suttantikattherā “da-kāro ta-kāramāpajjati, ta-kāro dakāramāpajjati, ca-kāro ja-kāramāpajjati, ja-kāro ca-kāramāpajjati, yakāro`
- `ka-kāramāpajjati, ka-kāro yakāramāpajjati, tasmā da-kārādīsu vattabbesu takārādivacanaṁ na virujjhatī”ti vadanti, taṁ kammavācaṁ patvā na vaṭṭati.`

*missing from render (chunk)*

- `pañhā mesā kusalehi cintitā ti āgataṁ`
- `abhinavaāgantukāva hutvā ñātī vā upaṭṭhāke vā passissāmāti gacchanti`
- `vīthiādīsu ca yattha bahūni bhattāni`
- `tasmā bahiupacāre gāhetuṁ na vaṭṭati`
- `adhammakamme dve nava kāni ovādavaggassa paṭhamasikkhāpadaniddese pācittiyavasena vuttāni`
- `ekettha dhammikā katāti ekaṁ dhammena samaggakammamevettha dhammikaṁ katanti attho`
- `vatthuttayassa vaṇṇe bhaññamāne kuddho gārayho hotīti tatthevassā vitthāro vutto`
- `tasmā dakārādīsu vattabbesu takārādivacanaṁ na virujjhatī ti vadanti`

*rendered but not contiguous in PDF*

- `ord119 [before] @6/7: gahetabbaṁ na kevalaṁ mañcena mañcoyeva ārāma`
- `ord119 [before] @0/2: ārāmavatthuvihāravihāravatthupīṭhabhisibimbohanānipi parivattetuṁ`
- `ord119 [before] @3/4: dinnakālato paṭṭhāya garubhaṇḍāni tipukoṭṭakasuvaṇṇakāracammakāra`
- `ord119 [before] @0/7: upakaraṇesupi eseva nayo ayaṁ pana viseso tipukoṭṭakaupakaraṇesupi`
- `ord122 [before] @5/6: dutiyavāre āraddhe saṁghatoyeva gahetvā gantabbaṁ abhinava`
- `ord122 [before] @0/10: āgantukāva hutvā ñātī vā upaṭṭhāke vā passissāmāti`
- `ord122 [before] @8/9: ekagehavasena vā kulavasena vā gāhetabbā vīthi`
- `ord122 [before] @0/9: ādīsu ca yattha bahūni bhattāni tattha gāme`

### 05Kankha (commentary)

*rendered but not contiguous in PDF*

- `ord661 [text] @0/354: bhūtagāmavagga bhūtagāmasikkhāpadavaṇṇanā bhūtagāmavaggassa paṭhame bhūtagāmapātabyatāyāti ettha bhavanti`
- `ord694 [text] @24/184: vuttanayen eva veditabbo rahopaṭicchannarahonisajjasikkhāpadavaṇṇanā niṭṭhitā chaṭṭhe nimantitoti pañcannaṁ bhojanānaṁ aññatare`
- `ord906 [text] @71/143: samuṭṭhānādīni samanubhāsanasadisānīti sikkhamāna navuṭṭhāpanapaṭhamadutiyasikkhāpadavaṇṇanā niṭṭhitā navame sokāvāsanti saṅket`

### 05ViT05 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `“Bhūtagāmavaggo”tipi etasseva nāmaṁ.`
- `6. Pāṭidesanīyakaṇḍa.`
- `7. Sekhiyakaṇḍa.`
- `Bhikkhunīvibhaṅgavaṇṇanā.`
- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `2. Saṁghādisesakaṇḍa.`
- `3. Nissaggiyakaṇḍa.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `bhūtagāmavaggo tipi etasseva nāmaṁ`
- `namo tassa bhagavato arahato sammāsambuddhassa`
- `iti samantapāsādikāya vinayaṭṭhakathāya vimativinodaniyaṁ bhikkhunīvibhaṅgavaṇṇanānayo niṭṭhito`
- `namo tassa bhagavato arahato sammāsambuddhassa`
- `mahāvagge ubhinnaṁ pātimokkhānanti ubhinnaṁ pātimokkhavibhaṅgānaṁ`
- `yaṁ khandhakaṁ saṅgāyiṁsūti sambandho`
- `khandhānaṁ vā pakāsanato khandhako`

### 06ViT06 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Paññāvisuddhāya dayāya sabbe,`
- `Vimocitā yena vineyyasattā.`
- `Taṁ cakkhubhūtaṁ sirasā namitvā,`
- `Lokassa lokantagatassa dhammaṁ.`
- `Saṁghañca sīlādiguṇehi yuttaMādāya sabbesu padesu sāraṁ.`
- `Saṅkhepakāmena mamāsayena,`
- `Sañcodito bhikkhu hitañca disvā.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `taṁ cakkhubhūtaṁ sirasā namitvā`
- `saṁghañca sīlādiguṇehi yuttamādāya sabbesu padesu sāraṁ`
- `sañcodito bhikkhu hitañca disvā`
- `saññā nimittaṁ kattā ca`
- `vattabbaṁ vattumicchatāti vacanato samantapāsādiketi saññā`
- `dīpantare bhikkhujanassa atthaṁ nābhisambhuṇātīti nimittaṁ`
- `buddhaghosoti garūhi gahitanāmadheyyenāti kattā`

*rendered but not contiguous in PDF*

- `ord1 [text] @103/483: saṅkappoti ca avatthantarabhedabhinno rāgova senahātthyaṅgamupeti sammagate rattakāmamupeti kāmapatitaṁ lokassa mātrālamatī ti ā`
- `ord8 [text] @604/758: vipassī sugataggasisso so dhammasenāpati aggasisso sayaṁ munindena yasassa patto anekaso soḷasadhā pasattho`
- `ord10 [text] @71/439: karonto jinapuṅgavassa sassissasaṁghassa adāsi dānaṁ kiṁ bhagavā sassisso tāva mahantaṁ kappiyabhaṇḍaṁ ubbhaṇḍikaṁ`
- `ord34 [text] @332/419: ekacittakoṭṭhāsoti ācariyā vadantī ti vuttaṁ pañcavīsati avahārā nāma vacanabhedeneva bhinnā atthato pana`
- `ord120 [text] @517/541: hoti cettha pārājikāpatti amūlikā ce catutthapārājikavatthubhūtā paṇṇattimattāva siyuṁ tatheva tato dvidhā maggaphalādidhammā`
- `ord503 [text] @25/309: uṇhīsato paṭṭhāyāti muddhato paṭṭhāya siniddhanīlamudukuñcitakeso yuttatuṅgamudukāyatanāso ādigāthāhi atha vā cakkavaraṅkitarat`
- `ord538 [text] @164/241: na katthaci gacchatīti kira adhippāyo chandaṁ datvā khaṇḍasīmaṁ vā sīmantarikaṁ vā bahisīmaṁ`
- `ord557 [text] @4/22: tena ca bhikkhunāti pavāraṇādāyakena tassā ca pavāraṇāya ārocitāya saṁghena ca pavārite`

### 07DiA01 (commentary)

*missing from render (line)*

- `Ñātimittā suhajjā ca, abhinandanti āgatan”tiĀdīsu3 sampaṭicchanepi. “Abhinanditvā anumoditvā”ti-ādīsu4`
- `Sādhu mittānamaddubbho5, pāpassākaraṇaṁ sukhan”tiādīsu6 sundare. “Tena hi brāhmaṇa suṇohi sādhukaṁ manasi karohī”tiādīsu7 sādhukasaddoyeva daḷhīkamme,`
- `“Ajjatagge samma dovārika āvarāmi dvāraṁ nigaṇṭhānaṁ nigaṇṭhīnan”tiādīsu4 hi ādimhi dissati. “Teneva aṅgulaggena taṁ aṅgulaggaṁ`

*missing from render (chunk)*

- `abhinandanti āgatan tiādīsu sampaṭicchanepi`
- `iti sumaṅgalavilāsiniyā dīghanikāyaṭṭhakathāyaṁ brahmajālasuttavaṇṇanā niṭṭhitā`
- `pāpassākaraṇaṁ sukhan tiādīsu sundare`
- `ajjatagge samma dovārika āvarāmi dvāraṁ nigaṇṭhānaṁ nigaṇṭhīnan tiādīsu hi ādimhi dissati`

*rendered but not contiguous in PDF*

- `ord86 [after] @9/10: ñātimittā suhajjā ca abhinandanti āgatan ti`
- `ord86 [after] @1/17: ādīsu sampaṭicchanepi abhinanditvā anumoditvā tiādīsu anumodanepi svāyamidha anumodanasampaṭicchanesu`
- `ord114 [after] @10/11: naro sādhu mittānamaddubbho pāpassākaraṇaṁ sukhan ti`
- `ord114 [after] @1/42: ādīsu sundare tena hi brāhmaṇa suṇohi sādhukaṁ manasi`
- `ord149 [before] @7/8: dovārika āvarāmi dvāraṁ nigaṇṭhānaṁ nigaṇṭhīnan ti`
- `ord149 [before] @2/8: ādīsu hi ādimhi dissati teneva aṅgulaggena taṁ aṅgulaggaṁ`

### 07ViT07 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Buddhaṁ dhammañca saṁghanti-ādinā yā pakāsitā.`
- `Bhadantabuddhaghosena, mātikāṭṭhakathā subhā.`
- `Tassā hi līnapadaṁ vi-kāsanakoyamārambho.`
- `Vippasannenāti vividhappasannena. Kathaṁ? “Itipiso -pa- buddho`
- `bhagavā, svākkhāto -pa- viññūhi, suppaṭipanno -pa- lokassā”ti1 evamādinā.`
- `“Cetasā”ti vuttattā tīsu vandanāsu cetovandanā adhippetā.`
- `Tanninnatādivasena kāyādīhi paṇāmakaraṇaṁ vandanā, guṇavasena`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `buddhaṁ dhammañca saṁghantiādinā yā pakāsitā`
- `tassā hi līnapadaṁ vikāsanakoyamārambho`
- `suppaṭipanno lokassā ti evamādinā`
- `cetasā ti vuttattā tīsu vandanāsu cetovandanā adhippetā`
- `tanninnatādivasena kāyādīhi paṇāmakaraṇaṁ vandanā`
- `guṇavasena manasāpi tathāva karaṇaṁ mānaṁ`
- `paccayādīnaṁ abhisaṅkharaṇaṁ sakkacca karaṇaṁ sakkāro`

*rendered but not contiguous in PDF*

- `ord0 [text] @15/95: catutthaṁ hoti rahopaṭicchanna rahonisajjasikkhāpadavaṇṇanā niṭṭhitā sabhatto samānoti nimantanabhattoti porāṇā santaṁ bhikkhuṁ an`
- `ord1 [text] @20/90: veditabbo ti rahopaṭicchanna rahonisajjasikkhāpadavaṇṇanā niṭṭhitā antoupacārasīmāya dassanūpacāre bhikkhuṁ disvāti yattha ṭhitass`
- `ord3 [text] @5/30: paṭicchannokāsaajjhokāsasallapanasikkhāpadavaṇṇanā dutiyatatiyāni uttānatthāneva paṭicchannokāsaajjhokāsasallapanasikkhāpadavaṇṇanā`
- `ord21 [text] @13/946: sattā pasannā ratanattayasmiṁ dānādipuññābhiratā bhavantūti kaṅkhāvitaraṇīabhinavaṭīkā niṭṭhitā padānukkamo piṭṭhaṅko padānukkam`

### 08DiA02 (commentary)

*missing from render (line)*

- `Vipassī Kakusandhoti ime pana dve bodhisattā payuttaājañña3rathamāruyha mahābhinikkhamanaṁ nikkhamiṁsu. Sikhī`
- `saṅkhārānaṁ abhisaṅkharaṇāyūhanasarāgavirāgaṭṭho, viññāṇassa suññataabyāpāra-asaṅkantipaṭisandhipātubhāvaṭṭho, nāmarūpassa`
- `āyūhanābhisaṅkharaṇayonigatiṭṭhitinivāsesu khipanaṭṭho, jātiyā jātisañjātiokkantinibbattipātubhāvaṭṭho, jarāmaraṇassa khayavayabhedavipariṇāmaṭṭho`
- `upaṭṭhāsi. Tena Bhagavā āyasmantaṁ Ānandaṁ ussādento “mā hevan”tiādimāha. Ayañcettha adhippāyo–Ānanda tvaṁ mahāpañño visadañāṇo,`

*missing from render (chunk)*

- `vipassī kakusandhoti ime pana dve bodhisattā payuttaājaññarathamāruyha mahābhinikkhamanaṁ nikkhamiṁsu`
- `tena bhagavā āyasmantaṁ ānandaṁ ussādento mā hevan tiādimāha`

*rendered but not contiguous in PDF*

- `ord9 [before] @6/7: kakusandhoti ime pana dve bodhisattā payutta`
- `ord9 [before] @0/4: ājaññarathamāruyha mahābhinikkhamanaṁ nikkhamiṁsu sikhī`
- `ord63 [before] @3/4: saṅkhārānaṁ abhisaṅkharaṇāyūhanasarāgavirāgaṭṭho viññāṇassa suññata`
- `ord63 [before] @0/2: abyāpāraasaṅkantipaṭisandhipātubhāvaṭṭho nāmarūpassa`
- `ord63 [before] @3/4: āyūhanābhisaṅkharaṇayonigatiṭṭhitinivāsesu khipanaṭṭho jātiyā jātisañjāti`
- `ord63 [before] @0/3: okkantinibbattipātubhāvaṭṭho jarāmaraṇassa khayavayabhedavipariṇāmaṭṭho`
- `ord63 [before] @8/9: āyasmantaṁ ānandaṁ ussādento mā hevan ti`
- `ord63 [before] @0/7: ādimāha ayañcettha adhippāyo ānanda tvaṁ mahāpañño visadañāṇo`

### 08DiT01 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Saṁvaṇṇanārambhe ratanattayavandanā saṁvaṇṇetabbassa dhammassa`
- `pabhavanissayavisuddhipaṭivedanatthaṁ, taṁ pana dhammasaṁvaṇṇanāsu`
- `viññūnaṁ bahumānuppādanatthaṁ, taṁ sammadeva tesaṁ`
- `uggahadhāraṇādikkamaladdhabbāya sammāpaṭipattiyā`
- `sabbahitasukhanipphādanatthaṁ. Atha vā maṅgalabhāvato, sabbakiriyāsu`
- `pubbakiccabhāvato, paṇḍitehi sammācaritabhāvato1, āyatiṁ paresaṁ`
- `diṭṭhānugati-āpajjanato ca saṁvaṇṇanāyaṁ ratanattayapaṇāmakiriyā. Atha`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `saṁvaṇṇanārambhe ratanattayavandanā saṁvaṇṇetabbassa dhammassa pabhavanissayavisuddhipaṭivedanatthaṁ`
- `taṁ pana dhammasaṁvaṇṇanāsu viññūnaṁ bahumānuppādanatthaṁ`
- `taṁ sammadeva tesaṁ uggahadhāraṇādikkamaladdhabbāya sammāpaṭipattiyā sabbahitasukhanipphādanatthaṁ`
- `āyatiṁ paresaṁ diṭṭhānugatiāpajjanato ca saṁvaṇṇanāyaṁ ratanattayapaṇāmakiriyā`
- `atha vā ratanattayapaṇāmakaraṇaṁ pūjanīyapūjāpuññavisesanibbattanatthaṁ`
- `taṁ attano yathāladdhasampattinimittakassa kammassa balānuppadānatthaṁ`
- `antarā ca tassa asaṅkocanatthaṁ`

*rendered but not contiguous in PDF*

- `ord6 [text] @7790/7968: veditabbo pahāya kāmādimale yathā gatā mahesino sakyamunī jutindharo tathāgato tena tathāgato mato`
- `ord70 [text] @179/2704: veditabbaṁ ayaṁ tāvettha aṭṭhakathāya līnatthavaṇṇanā ayaṁ pana pakaraṇanayena pāḷiyā atthavaṇṇanā sā panāyaṁ`
- `ord129 [text] @722/2050: paṭivedesīti attano hadayagataṁ vācāya pavedesi saraṇagamanassa visayappabhedaphalasaṁkilesabhedānaṁ viya kattu ca vibhāvanā `

### 09DiA03 (commentary)

*missing from render (line)*

- `Tīṇi antaradhānāni nāma pariyatti-antaradhānaṁ, paṭivedhaantaradhānaṁ, paṭipatti-antaradhānanti. Tattha pariyattīti tīṇi piṭakāni.`
- `yakkhasenāpatayo kanditabbā. Viravitabbanti “ayaṁ yakkho gaṇhātī”tiādīni bhaṇantena tehi saddhiṁ kathetabbaṁ. Tattha gaṇhātīti sarīre`
- `nibbānārammaṇo ariyamaggo kilese pajahati, evaṁ jīvitindriyādiārammaṇāpete kammapathā pāṇātipātādīni dussīlyāni pajahantīti veditabbā.`
- `Mūlatoti paṭipāṭiyā satta ñāṇasampayuttacittena viramantassa alobhaadosa-amohavasena timūlāni honti, ñāṇavippayuttacittena viramantassa`

*missing from render (chunk)*

- `viravitabbanti ayaṁ yakkho gaṇhātī tiādīni bhaṇantena tehi saddhiṁ kathetabbaṁ`
- `evaṁ jīvitindriyādiārammaṇāpete kammapathā pāṇātipātādīni dussīlyāni pajahantīti veditabbā`
- `mūlatoti paṭipāṭiyā satta ñāṇasampayuttacittena viramantassa alobhaadosaamohavasena timūlāni honti`
- `ṅa ayoniso manasikāroti anicce niccantiādinā nayena pavatto uppathamanasikāro`
- `maggo vipassanāya vā anantarattā attano vā anantaraṁ phaladayakattā ānantariko cetosamādhīti adhippeto`
- `kha samatho ca vipassanā cāti ime dve saṅgītisutte lokiyalokuttarā kathitā`
- `asaṅkhatā dhātūti paccayehi akataṁ nibbānaṁ`

*rendered but not contiguous in PDF*

- `ord125 [before] @4/5: tīṇi antaradhānāni nāma pariyattiantaradhānaṁ paṭivedha`
- `ord125 [before] @0/6: antaradhānaṁ paṭipattiantaradhānanti tattha pariyattīti tīṇi piṭakāni`
- `ord230 [before] @6/7: kanditabbā viravitabbanti ayaṁ yakkho gaṇhātī ti`
- `ord230 [before] @0/8: ādīni bhaṇantena tehi saddhiṁ kathetabbaṁ tattha gaṇhātīti`
- `ord280 [before] @5/6: nibbānārammaṇo ariyamaggo kilese pajahati evaṁ jīvitindriyādi`
- `ord280 [before] @0/6: ārammaṇāpete kammapathā pāṇātipātādīni dussīlyāni pajahantīti veditabbā`
- `ord280 [before] @5/6: mūlatoti paṭipāṭiyā satta ñāṇasampayuttacittena viramantassa alobha`
- `ord280 [before] @0/5: adosaamohavasena timūlāni honti ñāṇavippayuttacittena viramantassa`

### 09DiT02 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Yo desetvāna saddhammaṁ, gambhīraṁ duddasaṁ varaṁ.`
- `Dīghadassī ciraṁ kālaṁ, patiṭṭhāpesi sāsanaṁ.`
- `Vineyyajjhāsaye chekaṁ, mahāmatiṁ mahādayaṁ.`
- `Natvāna taṁ sasaddhamma-gaṇaṁ gāravabhājanaṁ.`
- `Saṅgītittayamāruḷhā, dīghāgamavarassa yā.`
- `Saṁvaṇṇanā yā ca tassā, vaṇṇanā sādhuvaṇṇitā.`
- `Ācariyadhammapāla-ttherenevābhisaṅkhatā.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `natvāna taṁ sasaddhammagaṇaṁ gāravabhājanaṁ`
- `saṁvaṇṇanā yā ca tassā`
- `nānānayanipuṇagambhīravicitrasikkhattayasaṅgahassa buddhānubuddha saṁvaṇṇitassa saddhāvahaguṇasampannassa dīghāgamavarassa gambhīraduranubodhatthadīpa`
- `ettha ca saṁvaṇṇanārambhe ratanattayapaṇāmakaraṇappayojanaṁ tattha tattha bahudhā papañcenti ācariyā`
- `saṁvaṇṇanārambhe satthari paṇāmakaraṇaṁ dhammassa`
- `satthu ca avitathadesanabhāvappakāsanena dhamme pasādajananatthaṁ`
- `tadubhayappasādā hi mahato atthassa siddhi hotī ti`

*rendered but not contiguous in PDF*

- `ord0 [text] @7785/10612: vutto yassantarato na santi kopā taṁ vigatabhayaṁ sukhiṁ asokaṁ devā nānubhavanti dassanāyā`
- `ord79 [text] @510/3897: attho ayaṁ tāvettha aṭṭhakathāya līnatthavibhāvanā ito paraṁ ācariyadhammapālena yā katā samuṭṭhānādihārādivividhatthavibhāvan`

### 10DiT03 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `3. Ambaṭṭhasutta.`
- `6. Mahālisutta.`
- `7. Jāliyasutta.`
- `8. Mahāsīhanādasutta.`
- `9. Poṭṭhapādasutta.`
- `10. Subhasutta.`
- `11. Kevaṭṭasutta.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `tatridaṁ sādhuvilāsiniyā sādhuvilāsinittasmiṁ hoti byañjanañceva attho ca`
- `natthi cettha yato tato`
- `ettāvatā ca saddhamme pāṭavatthāya`
- `pubbuttare jayabhūmikittāti bhidhānakepi ca`
- `so kāsi vaṇṇanaṁ imaṁ`
- `yaṁ puññaṁ pasutaṁ mayā`
- `ime ca pāṇino sabbe`

*rendered but not contiguous in PDF*

- `ord60 [text] @1949/5129: paṭivedesīti attano hadayagataṁ vācāya pavedesi saraṇagamanassa visayappabhedaphalasaṁkilesabhedānaṁ viya kattu ca vibhāvanā `
- `ord65 [text] @1046/2207: middhī yadā hoti mahagghaso ca mahāvarāhova nivāpavuṭṭho punappunaṁ gabbhamupeti mando ti imāya`
- `ord100 [text] @109/158: assa tathāgamanasaṅkhātaṁ ṭhānaṁ acchinditvāti yojanā kittako pana soti vuttaṁ sammodanīyakathāyapi kālo natthī`

### 10Ma02 (canon)

*missing from render (chunk)*

- `vāseṭṭhāti bhagavā anupubbaṁ yathātathaṁ`

*rendered more often than printed*

- `387x vs afterx: Namo tassa Bhagavato Arahato Sammāsambuddhassa, Namo tassa Bhagavato A`

### 10MaA01 (commentary)

*missing from render (line)*

- `sabbasakkāyadhammajanitaṁ maññanaṁ dassento pathaviṁ pathavitotiādimāha. Tattha lakkhaṇapathavī sasambhārapathavī ārammaṇapathavī`
- `taṇhāmaññanāya maññati. Iti me kesā siyuṁ anāgatamaddhānaṁ. Iti lomātiādinā vā pana nayena tattha nandiṁ samannāneti. “Imināhaṁ sīlena vā -pabrahmacar`
- `Pathavito maññatīti ettha pana pathavitoti nissakkavacanaṁ. Tasmā saupakaraṇassa attano vā parassa vā yathāvuttappabhedato pathavito uppattiṁ`
- `Nāmarūpavavatthānaṁ vā ñātapariññā. Kalāpasammasanādianulomapariyosānā tīraṇapariññā. Ariyamagge ñāṇaṁ pahānapariññāti. Yo`
- `Diṭṭhisīlasaṁghātena saṁhatoti saṁgho, so atthato aṭṭhaariyapuggalasamūho. Vuttañhetaṁ tasmiṁyeva vimāne.`
- `Paṇipāto nāma “ajja ādiṁ katvā ahaṁ abhivādanapaccuṭṭhānaañjalikammasāmīcikammaṁ Buddhādīnaṁyeva tiṇṇaṁ vatthūnaṁ karomi,`
- `“Ajjatagge samma dovārika āvarāmi dvāraṁ nigaṇṭhānaṁ nigaṇṭhīnan”tiādīsu3 hi ādimhi dissati. “Teneva aṅgulaggena taṁ aṅgulaggaṁ`
- `Tasmiṁ pana pāṇe pāṇasaññino jīvitindriyupacchedakaupakkamasamuṭṭhāpikā kāyavacīdvārānaṁ aññataradvārappavattā`

*missing from render (chunk)*

- `evaṁ puthujjanaṁ niddisitvā idāni tassa pathavīādīsu vatthūsu sabbasakkāyadhammajanitaṁ maññanaṁ dassento pathaviṁ pathavitotiādimāha`
- `iti lomātiādinā vā pana nayena tattha nandiṁ samannāneti`
- `imināhaṁ sīlena vā brahmacariyena vā evaṁ siniddhamudusukhumanīlakeso bhavissāmī tiādinā vā pana nayena appaṭiladdhānaṁ paṭilābhāya cittaṁ paṇidahati`
- `tasmā saupakaraṇassa attano vā parassa vā yathāvuttappabhedato pathavito uppattiṁ vā niggamanaṁ vā pathavito vā añño attāti maññamāno pathavito maññat`
- `paṇipāto nāma ajja ādiṁ katvā ahaṁ abhivādanapaccuṭṭhānaañjalikammasāmīcikammaṁ buddhādīnaṁyeva tiṇṇaṁ vatthūnaṁ karomi`
- `ajjatagge samma dovārika āvarāmi dvāraṁ nigaṇṭhānaṁ nigaṇṭhīnan tiādīsu hi ādimhi dissati`
- `tasmiṁ pana pāṇe pāṇasaññino jīvitindriyupacchedakaupakkamasamuṭṭhāpikā kāyavacīdvārānaṁ aññataradvārappavattā vadhakacetanā pāṇātipāto`
- `api ca gahaṭṭhānaṁ attano santakaṁ adātukāmatāya natthītiādinayappavatto appasāvajjo`

*rendered but not contiguous in PDF*

- `ord7 [before] @4/5: sabbasakkāyadhammajanitaṁ maññanaṁ dassento pathaviṁ pathavitoti`
- `ord7 [before] @0/5: ādimāha tattha lakkhaṇapathavī sasambhārapathavī ārammaṇapathavī`
- `ord7 [before] @8/9: me kesā siyuṁ anāgatamaddhānaṁ iti lomāti`
- `ord7 [before] @1/10: ādinā vā pana nayena tattha nandiṁ samannāneti imināhaṁ`
- `ord7 [before] @5/6: brahmacariyena vā evaṁ siniddhamudusukhumanīlakeso bhavissāmī ti`
- `ord7 [before] @1/8: ādinā vā pana nayena appaṭiladdhānaṁ paṭilābhāya cittaṁ paṇidahati`
- `ord7 [before] @7/8: ettha pana pathavitoti nissakkavacanaṁ tasmā sa`
- `ord7 [before] @0/8: upakaraṇassa attano vā parassa vā yathāvuttappabhedato pathavito`

### 11DiT04 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `2. Mahānidānasutta.`
- `3. Mahāparinibbānasutta.`
- `4. Mahāsudassanasutta.`
- `5. Janavasabhasutta.`
- `6. Mahāgovindasutta.`
- `7. Mahāsamayasutta.`
- `8. Sakkapañhasutta.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `imāneva dveti avadhāraṇena appanākammaṭṭhānaṁ tattha niyameti aññapabbesu tadabhāvato`
- `tena pabbadvayassa vipassanākammaṭṭhānatāpi appaṭisiddhā daṭṭhabbā aniccatādidassanato`
- `saṅkhāresu ādīnavavibhāvanāni sivathikapabbānīti āha sivathikānaṁ ādīnavānupassanāvasena vuttattā ti`
- `iriyāpathapabbādīnaṁ appanāvahatā pākaṭā evāti sesāni dvādasapī ti vuttaṁ`
- `niṭṭhitā ca mahāvaggaṭṭhakathāya līnatthappakāsanā`

*rendered but not contiguous in PDF*

- `ord8 [text] @272/646: sambahulānaṁ atthānaṁ vibhāvanavasena pavattavāro sambahulavāro kāmañcāyaṁ pāḷiyaṁ anāgato aṭṭhakathāsu āgatattā pana ānetvā`
- `ord57 [text] @718/2765: attho apasādentoti nibbhacchanto niggaṇhantoti attho tenāti mahāpaññabhāvena tatthāti therassa satipi uttānabhāve paṭiccasamup`
- `ord185 [text] @25/64: āha attānaṁ dameti etenāti damo assāti mahāsudassanarañño eko theroti appaññāto nāmagottato aññataro`
- `ord271 [text] @303/399: adhikamajjhimamudussāhavasena vā jaggatīti jāgarikaṁ anuyuñjati sahassadvisahassasaṅkhyattā mahāgaṇe aṭṭhakathātherāti aṭṭhaka`

### 11MaA02 (commentary)

*missing from render (line)*

- `āgantukapaṭisanthāraṁ katvā etaṁ “ko nu kho bhikkhave”tiādivacanamavoca. Te kira bhikkhū “kacci bhikkhave khamanīyaṁ kacci`
- `bhikkhusaṁghaparivuto cārikaṁ nikkhami. Kosalamahārājaanāthapiṇḍikādayo nivattetuṁ nāsakkhiṁsu. Anāthapiṇḍiko gharaṁ āgantvā`
- `Dhutaṅgasamādānassa attani atthibhāvaṁ najānāpetukāmo dhutaṅgaappiccho nāma. Tassa vibhāvanatthaṁ imāni vatthūni–`
- `paṇītasenāsanāni labhati, so tāni cīvarādīni viya cirapabbajitabahussutaappalābhigilānānaṁ datvā yattha katthaci vasantopi santuṭṭhova hoti,`

*missing from render (chunk)*

- `bhagavā etadavocāti kacci bhikkhave khamanīyan tiādīhi vacanehi āgantukapaṭisanthāraṁ katvā etaṁ ko nu kho bhikkhave tiādivacanamavoca`
- `dhutaṅgasamādānassa attani atthibhāvaṁ najānāpetukāmo dhutaṅgaappiccho nāma`
- `so tāni cīvarādīni viya cirapabbajitabahussutaappalābhigilānānaṁ datvā yattha katthaci vasantopi santuṭṭhova hoti`

*rendered but not contiguous in PDF*

- `ord32 [before] @7/8: etaṁ ko nu kho bhikkhave ti`
- `ord32 [before] @0/8: ādivacanamavoca te kira bhikkhū kacci bhikkhave khamanīyaṁ`
- `ord32 [before] @3/4: bhikkhusaṁghaparivuto cārikaṁ nikkhami kosalamahārāja`
- `ord32 [before] @1/6: anāthapiṇḍikādayo nivattetuṁ nāsakkhiṁsu anāthapiṇḍiko gharaṁ āgantvā`
- `ord32 [before] @4/5: dhutaṅgasamādānassa attani atthibhāvaṁ najānāpetukāmo dhutaṅga`
- `ord32 [before] @2/6: appiccho nāma tassa vibhāvanatthaṁ imāni vatthūni`
- `ord32 [before] @6/7: labhati so tāni cīvarādīni viya cirapabbajitabahussuta`
- `ord32 [before] @0/7: appalābhigilānānaṁ datvā yattha katthaci vasantopi santuṭṭhova hoti`

### 12DiT05 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `2. Udumbarikasutta.`
- `3. Cakkavattisutta.`
- `4. Aggaññasutta.`
- `5. Sampasādanīyasutta.`
- `“Na nivāritā”ti vatvā tattha kāraṇaṁ dassetuṁ “tīṇi hī”ti-ādi vuttaṁ.`
- `Paṭipatti-antaradhānena sāsanassa osakkitattā aparassa uppatti laddhāvasarā`
- `hoti. Paṭipadāti paṭivedhāvahā pubbabhāgapaṭipadā.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `na nivāritā ti vatvā tattha kāraṇaṁ dassetuṁ tīṇi hī tiādi vuttaṁ`
- `paṭipattiantaradhānena sāsanassa osakkitattā aparassa uppatti laddhāvasarā hoti`
- `pariyatti pamāṇan ti vatvā tamatthaṁ bodhisattaṁ nidassanaṁ katvā dassetuṁ yathā tiādi vuttaṁ`
- `tayidaṁ hīnaṁ nidassanaṁ katanti daṭṭhabbaṁ`
- `niyyānikadhammassa hi ṭhitiṁ dassento aniyyānikadhammaṁ nidasseti`
- `mātikāya antarahitāyāti yo pana bhikkhū tiādi nayappavattāya sikkhāpadapāḷimātikāya antarahitāya`
- `pabbajjāupasampadākammesu ca sāsanaṁ tiṭṭhati`

*rendered but not contiguous in PDF*

- `ord129 [text] @33/89: parinibbānato puretarameva hi dhammasenāpati parinibbuto saddhivihārikaṁ adāsīti saddhivihārikaṁ katvā adāsi kathāya mūlanti`
- `ord230 [text] @263/463: jānāpanaṁ hotīti āha jānāpetabbā ti parittassa parikammaṁ kathetabbanti āṭānāṭiyaparittassa parikammaṁ pubbupacāraṭṭhāniyaṁ me`
- `ord264 [text] @62/77: khayante jātattā rāgakkhayo dosakkhayo mohakkhayoti nibbedho vuccati nibbānaṁ maggañāṇena nibbijjhitabbaṭṭhena paṭivijjhitabbaṭṭ`
- `ord266 [text] @271/511: na upalabbhatevāti eseva nayo sesesupi adhikarīyanti etthāti adhikaraṇāni ke adhikarīyanti samathā kathaṁ`
- `ord279 [text] @607/727: samudayāyā tiādi sesesupi eseva nayo pāṇātipātā veditabbāni lokiyalokuttaramissakavasenettha kusalakammapathānaṁ desitattā ver`
- `ord280 [text] @155/243: anuppādadhammataṁ pajānāti tañca pajānanaṁ paccavekkhaṇañāṇanti phalañca te sampayuttadhammā cāti phalasampayuttadhammā ariyap`

### 13MaA04 (commentary)

*missing from render (line)*

- `Evaṁ pātubhūtahatthiratanassa pana cakkavattino parisā pakatimaṅgalaassaṭṭhānaṁ sucisamatalaṁ kāretvā alaṅkaritvā ca purimanayen’eva rañño`
- `veditabbaṁ. Evarūpaṁ assaratanaṁ sandhāya Bhagavā puna caparantiādimāha.`

*missing from render (chunk)*

- `evaṁ pātubhūtahatthiratanassa pana cakkavattino parisā pakatimaṅgalaassaṭṭhānaṁ sucisamatalaṁ kāretvā alaṅkaritvā ca purimanayen eva rañño tassa āgama`
- `evarūpaṁ assaratanaṁ sandhāya bhagavā puna caparantiādimāha`

*rendered but not contiguous in PDF*

- `ord185 [before] @5/6: evaṁ pātubhūtahatthiratanassa pana cakkavattino parisā pakatimaṅgala`
- `ord185 [before] @0/8: assaṭṭhānaṁ sucisamatalaṁ kāretvā alaṅkaritvā ca purimanayen eva`
- `ord185 [before] @6/7: evarūpaṁ assaratanaṁ sandhāya bhagavā puna caparanti`

### 13MaT01 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Evaṁ bāhiranidāne vattabbaṁ atidisitvā idāni abbhantaranidānaṁ ādito`
- `paṭṭhāya saṁvaṇṇetuṁ “yaṁ panetan”ti-ādi vuttaṁ. Tattha yasmā`
- `saṁvaṇṇanaṁ karontena saṁvaṇṇetabbe dhamme padavibhāgaṁ`
- `padatthañca1 dassetvā tato paraṁ piṇḍatthādidassanavasena saṁvaṇṇanā`
- `kātabbā, tasmā padāni tāva dassento “evanti nipātapadan”ti-ādimāha. Tattha`
- `padavibhāgoti padānaṁ viseso, na padaviggaho. Atha vā padāni ca`
- `padavibhāgo ca padavibhāgo, padaviggaho ca padavibhāgo ca`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `evaṁ bāhiranidāne vattabbaṁ atidisitvā idāni abbhantaranidānaṁ ādito paṭṭhāya saṁvaṇṇetuṁ yaṁ panetan tiādi vuttaṁ`
- `tattha yasmā saṁvaṇṇanaṁ karontena saṁvaṇṇetabbe dhamme padavibhāgaṁ padatthañca dassetvā tato paraṁ piṇḍatthādidassanavasena saṁvaṇṇanā kātabbā`
- `tasmā padāni tāva dassento evanti nipātapadan tiādimāha`
- `tattha padavibhāgoti padānaṁ viseso`
- `atha vā padāni ca padavibhāgo ca padavibhāgo`
- `padaviggaho ca padavibhāgo ca padavibhāgoti vā ekasesavasena padapadaviggahā padavibhāgasaddena vuttāti veditabbaṁ`
- `tattha padaviggaho subhagañca taṁ vanañcāti subhagavanaṁ`

*rendered but not contiguous in PDF*

- `ord17 [text] @1445/3301: tenāha evaṁ puthujjanaṁ niddisī ti tassāti puthujjanassa vasati ettha ārammaṇakaraṇavasenāti ārammaṇampi vatthūti`
- `ord24 [text] @1575/2177: veditabbo pahāya kāmādimale yathā gatā mahesino sakyamunī jutindharo tathā gato tena mato`
- `ord69 [text] @96/773: nissāya evāti dassento ayañhī tiādimāha tattha sammutiyā desanā sammutidesanā paramatthassa desanā paramatthadesanā`
- `ord100 [text] @654/1655: kathesi rāsitoti piṇḍato ekajjhanti attho akosallappavattiyāti kosallapaṭipakkhato akosallaṁ vuccati aññāṇaṁ tato pavattanato`

### 14MaT02 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Appa-saddassa parittapariyāyataṁ manasi katvā āha “byañjanaṁ`
- `sāvasesaṁ viyā”ti. Tenāha “na hi tassā”ti-ādi. Appa-saddo panettha`
- `abhāvatthoti sakkā viññātuṁ “appābādhatañca sañjānāmī”ti-ādīsu3 viya.`
- `Atricchatā nāma4 atra atra icchāti katvā. Asantaguṇasambhāvanatāti`
- `attani avijjamānaṁ guṇānaṁ vijjamānānaṁ viya paresaṁ pakāsanā.`
- `Saddhoti maṁ jano jānātūti vattapaṭipattikārakavisesalābhīti jānātu`
- `“vattapaṭipatti-āpāthakajjhāyitā”ti evamādinā. Santaguṇasambhāvanāti`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `appasaddassa parittapariyāyataṁ manasi katvā āha byañjanaṁ sāvasesaṁ viyā ti`
- `tenāha na hi tassā tiādi`
- `appasaddo panettha abhāvatthoti sakkā viññātuṁ appābādhatañca sañjānāmī tiādīsu viya`
- `atricchatā nāma atra atra icchāti katvā`
- `asantaguṇasambhāvanatāti attani avijjamānaṁ guṇānaṁ vijjamānānaṁ viya paresaṁ pakāsanā`
- `saddhoti maṁ jano jānātūti vattapaṭipattikārakavisesalābhīti jānātu vattapaṭipattiāpāthakajjhāyitā ti evamādinā`
- `santaguṇasambhāvanāti icchācāre ṭhatvā attani vijjamānasīladhutadhammādiguṇavibhāvanā`

*rendered but not contiguous in PDF*

- `ord7 [text] @146/346: mamattakārino buddhamāmakā sesapadadvayepi eseva nayo alaṁ ariyāya ariyabhāvāyāti alamariyo rūpāyatanaṁ jānāti cakkhuviññāṇaṁ`
- `ord96 [text] @123/362: kapilavatthusannissayo padesoti āha kapilavatthāhāro ti sākiyamaṇḍalassāti sākiyarājasamūhassa dasannaṁ appicchakathādīnaṁ vatt`

### 14Sam03 (canon)

*missing from render (line)*

- `(Rāgavinayapariyosānadosavinayapariyosānamohavinayapariyosānavaggo vitthāretabbo.) (Yadapi Maggasaṁyuttaṁ vitthāretabbaṁ, tadapi`

*missing from render (chunk)*

- `rāgavinayapariyosānadosavinayapariyosānamohavinayapariyosānavaggo vitthāretabbo yadapi maggasaṁyuttaṁ vitthāretabbaṁ`

*rendered but not contiguous in PDF*

- `ord197 [before] @0/1: rāgavinayapariyosānadosavinayapariyosānamohavinayapariyosāna`
- `ord197 [before] @1/6: vaggo vitthāretabbo yadapi maggasaṁyuttaṁ vitthāretabbaṁ tadapi`

### 14SamA01 (commentary)

*missing from render (line)*

- `Idāni Bhagavato yathābhūtaguṇe kathento Bhagavā hi bhantetiādimāha. Tattha anuppannassāti Kassapasammāsambuddhato paṭṭhāya`

*missing from render (chunk)*

- `idāni bhagavato yathābhūtaguṇe kathento bhagavā hi bhantetiādimāha`

*rendered but not contiguous in PDF*

- `ord198 [after] @67/68: bhagavato yathābhūtaguṇe kathento bhagavā hi bhanteti`
- `ord198 [after] @0/57: ādimāha tattha anuppannassāti kassapasammāsambuddhato paṭṭhāya aññena samaṇena`

### 15MaT03 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Saṅgāravasuttavaṇṇanāya līnatthappakāsanā samattā.`
- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Indriyabhāvanāsuttavaṇṇanāya līnatthappakāsanā samattā.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `namo tassa bhagavato arahato sammāsambuddhassa`

*rendered but not contiguous in PDF*

- `ord516 [text] @40/252: tassa itare hatthino na sahanti sindhavakulatoti sindhavassājānīyakulato sakaṭanābhisamappamāṇanti pariṇāhato mahāsakaṭassa nāb`

### 16SaT01 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `1. Devatāsaṁyutta.`
- `Vibhāgavantānaṁ sabhāvavibhāvanaṁ vibhāgadassanavaseneva hotīti`
- `paṭhamaṁ tāva saṁyuttavaggasuttādivasena saṁyuttāgamassa vibhāgaṁ`
- `dassetuṁ “tattha saṁyuttāgamo nāmā”ti-ādimāha. Tattha tatthāti yaṁ`
- `vuttaṁ “saṁyuttāgamavarassa atthaṁ pakāsayissāmī”ti, tasmiṁ vacane.`
- `Tatthāti vā “etāya aṭṭhakathāya vijānātha saṁyuttanissitaṁ atthan”ti ettha`
- `yaṁ saṁyuttaggahaṇaṁ kataṁ, tattha. Pañca vaggā etassāti pañcavaggo,`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `oghataraṇasuttavaṇṇanā vibhāgavantānaṁ sabhāvavibhāvanaṁ vibhāgadassanavaseneva hotīti paṭhamaṁ tāva saṁyuttavaggasuttādivasena saṁyuttāgamassa vibhāg`
- `tattha tatthāti yaṁ vuttaṁ saṁyuttāgamavarassa atthaṁ pakāsayissāmī ti`
- `tatthāti vā etāya aṭṭhakathāya vijānātha saṁyuttanissitaṁ atthan ti ettha yaṁ saṁyuttaggahaṇaṁ kataṁ`
- `pañca vaggā etassāti pañcavaggo`
- `idāni taṁ ādito paṭṭhāya saṁvaṇṇetukāmo attano saṁvaṇṇanāya tassa paṭhamamahāsaṅgītiyaṁ nikkhittānukkameneva pavattabhāvaṁ dassetuṁ tassa vaggesu sagā`
- `tattha yathāpaccayaṁ tattha tattha desitattā paññattattā ca vippakiṇṇānaṁ dhammavinayānaṁ saṅgahetvā gāyanaṁ kathanaṁ saṅgīti`
- `mahāvisayattā pūjaniyattā ca mahatī saṅgīti mahāsaṅgīti`

*rendered but not contiguous in PDF*

- `ord18 [text] @5389/7106: niddeso ayaṁ tāva aṭṭhakathāya līnatthavaṇṇanā idāni pakaraṇanayena pāḷiyā atthavaṇṇanaṁ karissāma sā pana`

### 17An03 (canon)

*rendered but not contiguous in PDF*

- `ord10 [after] @31/33: ekamantaṁ nisinno kho verañjo brāhmaṇo bhagavantaṁ etadavoca`
- `ord107 [after] @73/75: ekamantaṁ nisinno kho āyasmā sāriputto bhagavantaṁ etadavoca`
- `ord136 [after] @29/31: ekamantaṁ nisinno kho āyasmā ānando bhagavantaṁ etadavoca`

### 17AnA01 (commentary)

*missing from render (line)*

- `abhitthaviyamāno Mahābodhimaṇḍaṁ āruyha acalaṭṭhāne pācīnalokadhātuabhimukho pallaṅkena nisīditvā caturaṅgasamannāgataṁ vīriyaṁ adhiṭṭhāya`
- `patiṭṭhito. Pañcamiyā pana pakkhassa Anattalakkhaṇasuttantadesanāpariyosāne sabbepi arahatte patiṭṭhitā.`

*missing from render (chunk)*

- `pañcamiyā pana pakkhassa anattalakkhaṇasuttantadesanāpariyosāne sabbepi arahatte patiṭṭhitā`

*rendered but not contiguous in PDF*

- `ord84 [before] @4/5: abhitthaviyamāno mahābodhimaṇḍaṁ āruyha acalaṭṭhāne pācīnalokadhātu`
- `ord84 [before] @0/6: abhimukho pallaṅkena nisīditvā caturaṅgasamannāgataṁ vīriyaṁ adhiṭṭhāya`
- `ord84 [before] @4/5: patiṭṭhito pañcamiyā pana pakkhassa anattalakkhaṇasuttantadesanā`
- `ord84 [before] @1/4: pariyosāne sabbepi arahatte patiṭṭhitā`

### 17SaT02 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Dutiyeti dutiye āhāre. Uddālitacammāti uppāṭitacammā, sabbaso`
- `apanītacammāti attho. Na sakkoti dubbalabhāvato. Tathā hi itthī “abalā”ti`
- `vuccati. Silākuṭṭādīnanti ādi-saddena iṭṭhakakuṭṭamattikākuṭṭādīnaṁ`
- `saṅgaho. Uṇṇanābhīti makkaṭakaṁ. Sarabūti`
- `gharagoḷiyā. Uccāliṅgapāṇakā nāma lomasā pāṇakā. Ākāsanissitāti`
- `ākāsacārino. Luñcitvāti uppāṭetvā.`
- `Tisso pariññāti heṭṭhā vuttā ñātapariññādayo tisso pariññā.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `tathā hi itthī abalā ti vuccati`
- `silākuṭṭādīnanti ādisaddena iṭṭhakakuṭṭamattikākuṭṭādīnaṁ saṅgaho`
- `uccāliṅgapāṇakā nāma lomasā pāṇakā`
- `tisso pariññāti heṭṭhā vuttā ñātapariññādayo tisso pariññā`
- `desanā yāva arahattā kathitā sabbaso vedanāsu pariññātāsu kilesānaṁ lesassapi abhāvato`
- `phuṇantīti attano upari sayameva ākirantīti attho`
- `tenāha narā rudantā paridaḍḍhagattā ti`

*rendered but not contiguous in PDF*

- `ord469 [text] @10/15: etesaṁ sabbesaṁ bodhipakkhiyadhammānaṁ ijjhanaṁ vuttaṁ paṁsurajojallanti bhūmireṇusahajātamalaṁ vāṇijakopameti vāṇijakopamapaṭha`

### 18AnA02 (commentary)

*missing from render (line)*

- `“Katamo ca puggalo ugghaṭitaññū, yassa puggalassa sahaudāhaṭavelāya dhammābhisamayo hoti, ayaṁ vuccati puggalo`
- `vasena, chaṭṭhaṁ avasesānaṁ catunnaṁ, sattamaṁ anariyavohāraariyavohārānaṁ. Tathā aṭṭhamanavamadasamāni sappaṭipakkhānaṁ`

*missing from render (chunk)*

- `yassa puggalassa sahaudāhaṭavelāya dhammābhisamayo hoti`

*rendered but not contiguous in PDF*

- `ord389 [after] @6/7: ca puggalo ugghaṭitaññū yassa puggalassa saha`
- `ord389 [after] @0/67: udāhaṭavelāya dhammābhisamayo hoti ayaṁ vuccati puggalo ugghaṭitaññū`
- `ord448 [before] @5/6: vasena chaṭṭhaṁ avasesānaṁ catunnaṁ sattamaṁ anariyavohāra`
- `ord448 [before] @0/4: ariyavohārānaṁ tathā aṭṭhamanavamadasamāni sappaṭipakkhānaṁ`

### 18AnT01 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Anantañāṇaṁ karuṇāniketaṁ,`
- `Namāmi nāthaṁ jitapañcamāraṁ.`
- `Dhammaṁ visuddhaṁ bhavanāsahetuṁ,`
- `Saṁghañca seṭṭhaṁ hatasabbapāpaṁ.`
- `Kassapaṁ taṁ mahātheraṁ, saṁghassa pariṇāyakaṁ.`
- `Dīpasmiṁ tambapaṇṇimhi, sāsanodayakārakaṁ1.`
- `Paṭipattiparādhīnaṁ, sadāraññanivāsinaṁ.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `pākaṭaṁ gagane candamaṇḍalaṁ viya sāsane`
- `yo sīhaḷindo dhitimā yasassī`
- `katvā vihāre vipule ca ramme`
- `vibhāgavantānaṁ sabhāvavibhāvanaṁ vibhāgadassanavaseneva hotīti paṭhamaṁ tāva nipātasuttavasena vibhāgaṁ dassetuṁ tattha aṅguttarāgamo nāmā tiādimāha`
- `tattha tatthāti aṅguttarāgamassa atthaṁ pakāsayissāmī ti yadidaṁ vuttaṁ`
- `yassa atthaṁ pakāsayissāmī ti paṭiññātaṁ`
- `so aṅguttarāgamo nāma nipātasuttavasena evaṁ vibhāgoti attho`

*rendered but not contiguous in PDF*

- `ord18 [text] @5142/7704: maraṇasampāpanavasenapi ayaṁ tāvettha aṭṭhakathāya anuttānatthadīpanā idāni pakaraṇanayena pāḷiyā atthavaṇṇanaṁ karissāma sā `
- `ord82 [text] @2594/2666: veditabbo pahāya kāmādimale yathā gatā mahesino sakyamunī jutindharo tathāgato tena tathāgato mato`
- `ord89 [text] @1164/1404: tenevāha atītepī tiādi sesaṁ uttānatthameva aññāsikoṇḍaññattherādayotiādīsu pana yāthāvasarasaguṇavasenāti yathāsabhāvaguṇava`

### 19AnT02 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Kammakāraṇavaggavaṇṇanāya līnatthappakāsanā niṭṭhitā.`
- `Paṭhamo paṇṇāsako niṭṭhito.`
- `54.55. Tatiye yesaṁ rāgādīnaṁ appahānena purisassa`
- `attabyābādhādīnaṁ sambhavo, pahānena asambhavoti evaṁ rāgādīnaṁ`
- `pahāyako ariyadhammo mahānubhāvatāya mahānisaṁsatāya ca samaṁ`
- `passitabboti sandiṭṭhiko. Iminā nayena sesesu padesupi yathārahaṁ`
- `nīharitvā vattabbo. Saddattho pana visuddhimaggasaṁvaṇṇanāsu1`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `tatiye yesaṁ rāgādīnaṁ appahānena purisassa attabyābādhādīnaṁ sambhavo`
- `pahānena asambhavoti evaṁ rāgādīnaṁ pahāyako ariyadhammo mahānubhāvatāya mahānisaṁsatāya ca samaṁ passitabboti sandiṭṭhiko`
- `iminā nayena sesesu padesupi yathārahaṁ nīharitvā vattabbo`
- `saddattho pana visuddhimaggasaṁvaṇṇanāsu vuttanayena veditabbo`

*rendered but not contiguous in PDF*

- `ord107 [text] @16/36: kammunā nikkhitto niraye ṭhapitoyevāti attho dukkassa vaḍḍhi etesanti dukkhavaḍḍhikā ye hi dukkhaṁ`
- `ord250 [text] @471/1063: gamissanti apāyabhūmiṁ pahāya mānusaṁ dehaṁ buddhoti kittayantassa kāye bhavati yā pīti varameva`
- `ord252 [text] @278/345: sampahāro sabbeva bhonto sahitā samaggā vitthārikā hontu disāsu thūpā bahū janā cakkhumato`

### 20AnT03 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `3. Tatiyapaṇṇāsaka.`
- `4. Catutthapaṇṇāsaka.`
- `5. Pañcamapaṇṇāsaka.`
- `Sattakanipātavaṇṇanāya anuttānatthadīpanā samattā.`
- `Navakanipātavaṇṇanāya anuttānatthadīpanā samattā.`
- `3. Tatiyapaṇṇāsaka.`
- `4. Catutthapaṇṇāsaka.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `niṭṭhitā ca manorathapūraṇiyā aṅguttaranikāyaṭṭhakathāya`
- `mahāaṭṭhakathāya sāranti aṅguttaramahāaṭṭhakathāya sāraṁ`
- `ekūnasaṭṭhimattoti thokaṁ ūnabhāvato mattasaddaggahaṇaṁ`
- `mūlaṭṭhakathāsāranti pubbe vuttaaṅguttaramahāaṭṭhakathāya sārameva anunigamavasena vadati`
- `atha vā mūlaṭṭhakathāsāranti porāṇaṭṭhakathāsu atthasāraṁ`
- `tenedaṁ dasseti aṅguttaramahāaṭṭhakathāya atthasāraṁ ādāya imaṁ manorathapūraṇiṁ karonto sesamahānikāyānampi mūlaṭṭhakathāsu idha viniyogakkhamaṁ atth`
- `mahāvihārādhivāsīnanti ca idaṁ purimapacchimapadehi saddhiṁ sambandhitabbaṁ mahāvihārādhivāsīnaṁ samayaṁ pakāsayantī`

*rendered but not contiguous in PDF*

- `ord301 [text] @239/440: middhī yadā hoti mahagghaso ca mahāvarāhova nivāpapuṭṭho punappunaṁ gabbhamupeti mando ti imāya`

### 20KhuA01 (commentary)

*missing from render (chunk)*

- `taṁ dassento te ca tatthā ti catutthagāthāya pacchimaddhaṁ pahūte annapānamhī ti pañcamagāthāya pubbaddhañca āha`

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

### 21KhuT01 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Saṁvaṇṇanārambhe1 ratanattayavandanā saṁvaṇṇetabbassa dhammassa`
- `pabhavanissayavisuddhipaṭivedanatthaṁ, taṁ pana dhammasaṁvaṇṇanāsu`
- `viññūnaṁ bahumānuppādanatthaṁ, taṁ sammadeva tesaṁ`
- `uggahaṇadhāraṇādikkamaladdhabbāya sammāpaṭipattiyā`
- `sabbahitasukhanipphādanatthaṁ. Atha vā maṅgalabhāvato, sabbakiriyāsu`
- `pubbakiccabhāvato, paṇḍitehi sammācaritabhāvato, āyatiṁ paresaṁ`
- `diṭṭhānugati-āpajjanato ca saṁvaṇṇanāyaṁ ratanattayapaṇāmakiriyā. Atha`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `saṁvaṇṇanārambhe ratanattayavandanā saṁvaṇṇetabbassa dhammassa pabhavanissayavisuddhipaṭivedanatthaṁ`
- `taṁ pana dhammasaṁvaṇṇanāsu viññūnaṁ bahumānuppādanatthaṁ`
- `taṁ sammadeva tesaṁ uggahaṇadhāraṇādikkamaladdhabbāya sammāpaṭipattiyā sabbahitasukhanipphādanatthaṁ`
- `āyatiṁ paresaṁ diṭṭhānugatiāpajjanato ca saṁvaṇṇanāyaṁ ratanattayapaṇāmakiriyā`
- `atha vā ratanattayapaṇāmakaraṇaṁ pūjanīyapūjāpuññavisesanibbattanatthaṁ`
- `taṁ attano yathāladdhasampattinimittassa kammassa balānuppadānatthaṁ`
- `antarā ca tassa asaṅkocanatthaṁ`

*rendered but not contiguous in PDF*

- `ord155 [text] @64/83: iti sattibalānurūpā racitā nayaniddesavibhāvanā niṭṭhitā nettivisayaṁ sāsanavarasaṅkhātaṁ saṁvaṇṇetabbasuttaṁ yesaṁ byañjanapadā`
- `ord273 [text] @798/2104: paṭipannena anāgāminā antarāparinibbāyinā upahaccaparinibbāyinā asaṅkhāraparinibbāyinā sasaṅkhāraparinibbāyinā uddhaṁsotena a`

### 22AbhiT01 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Aṭṭhasāliniṁ tāva vaṇṇentehi ācariyehi tassā sanniveso vibhāvetabbo.`
- `Tasmā idaṁ vuccati–.`
- `“Vacanattho paricchedo, sanniveso ca pāḷiyā.`
- `Sāgarehi tathā cintā, desanāhi gambhīratā.`
- `Desanāya sarīrassa, pavattiggahaṇaṁ tathā.`
- `Therassa vācanāmagga-tappabhāvitatāpi ca.`
- `Paṭivedhā tathā buddha-vacanādīhi ādito.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `aṭṭhasāliniṁ tāva vaṇṇentehi ācariyehi tassā sanniveso vibhāvetabbo`
- `paṭivedhā tathā buddhavacanādīhi ādito`
- `vinayenātha gosiṅgasuttena ca mahesinā`
- `vacanatthavijānanena viditābhidhammasāmaññatthassa abhidhammakathā vuccamānā sobheyyāti abhidhammaparijānanameva ādimhi yuttarūpanti tadatthaṁ pucchat`
- `tattha tatthāti abhidhammassa atthaṁ pakāsayissāmī ti yadidaṁ vuttaṁ`
- `yassa atthaṁ pakāsayissāmī ti paṭiññātaṁ`
- `so abhidhammo kenaṭṭhena abhidhammoti attho`

*rendered but not contiguous in PDF*

- `ord46 [text] @2460/3047: saddārammaṇe uppajjamānaṁ rūpārammaṇan ti vuccati imassa panatthassāti kammadvārānaṁ aññamaññasmiṁ aniyatatāya dvāre caranti`
- `ord69 [text] @7/82: nātisamāhitāya bhāvanāyāti yevāpanakehipi nibbisesataṁ dasseti apaciti eva apacitisahagataṁ puññakiriyāvatthu yathā nandirāgasahag`
- `ord94 [text] @341/795: kaṇṭhe baddhakuṇapaṁ viya paṭinissajjanīyā honti tatrāti lokuttarajjhāne ajjhattañcāti upaḍḍhagāthāya abhinivisitabbaṁ vuṭṭhāta`
- `ord117 [text] @131/1522: taṁkammasahitasantānajanitasukkasoṇitapaccayānaṁ taṁmūlakānaṁ candasūriyavisamaparivattādijanitautāhārādivisamapaccayānañca v`
- `ord216 [text] @185/209: taṁ ce chādeti cīvaraṁ idamatthikaṁ pallaṅkena nisinnassa jaṇṇuke nābhivassati āha bhojanānisaṁsoti yathāvuttehi`
- `ord278 [text] @2391/3024: tiādinā vacīdvāre uppajjamānampi pāṇātipātādīti attho kammadvārānantiādinā pakāsetabbassa sarūpaṁ pakāsanupāyañca dasseti ni`
- `ord317 [text] @228/567: tiādināva vuttappakārādhippāyena visunti saṅkhārehi vinivattetvā pañcadhā uddisati pañcupādānakkhandhe ajjhattadukavasena rūpa`
- `ord334 [text] @82/1312: appāyukasaṁvattaniyakammamūlakānaṁ āhārādīti ādisaddena visamūpakkamādayo pariggaṇhāti yato tihetukādikammato yasmkiñca ṭhānet`

### 22KhuA03 (commentary)

*missing from render (line)*

- `Buddhasāsane vikiritvā Satthari Jetavane viharante devasikaṁ tīṇi mahāupaṭṭhānāni gacchati, gacchanto ca “kiṁ nu kho ādāya āgatoti sāmaṇerā vā`
- `sakkoti, evamevaṁ akusalacetanāya abhāvena pāpaṁ akarontassa dhanuādīni nīharitvā dadatopi pāpaṁ nāma na hotī”ti vatvā anusandhiṁ ghaṭetvā`
- `sahāyikā ahosi. Tattha ca ekadivasaṁ katapariccāgo dhanassa cuddasakoṭiagghanako ahosi. Tathāgatassa setacchattaṁ nisīdanapallaṅko ādhārako`
- `So kira maṅgalaṁ karontānaṁ gehaṁ gantvā “tirokuṭṭesu tiṭṭhantī”tiādinā1 nayena avamaṅgalaṁ katheti, avamaṅgalaṁ karontānaṁ gehaṁ.`
- `sāmīti. Tena hi taṁ āharathāti. Tampi tatheva khepetvā anupubbena khettaārāmuyyānayoggādikampi antamaso bhājanabhaṇḍakampi`
- `bhikkhave Aṅgulimālo bhāyati. Khīṇāsava-usabhānañhi antare jeṭṭhakausabhā mama puttasadisā bhikkhū na bhāyantī”ti vatvā Brāhmaṇavagge`
- `apphoṭessāmīti. Mahājano “kiṁ nāmeso saddo”ti pucchitvā “Cūḷaanāthapiṇḍikassa`
- `dakkhiṇanāsikāsotato. Dakkhiṇa-aṁsakūṭato, vāma-aṁsakūṭato. Vāmaaṁsakūṭato, dakkhiṇa-aṁsakūṭato. Dakkhiṇahatthato, vāmahatthato.`

*missing from render (chunk)*

- `anāthapiṇḍiko hi vihārameva uddissa catupaṇṇāsakoṭidhanaṁ buddhasāsane vikiritvā satthari jetavane viharante devasikaṁ tīṇi mahāupaṭṭhānāni gacchati`
- `evamevaṁ akusalacetanāya abhāvena pāpaṁ akarontassa dhanuādīni nīharitvā dadatopi pāpaṁ nāma na hotī ti vatvā anusandhiṁ ghaṭetvā dhammaṁ desento imaṁ`
- `tattha ca ekadivasaṁ katapariccāgo dhanassa cuddasakoṭiagghanako ahosi`
- `so kira maṅgalaṁ karontānaṁ gehaṁ gantvā tirokuṭṭesu tiṭṭhantī tiādinā nayena avamaṅgalaṁ katheti`
- `tampi tatheva khepetvā anupubbena khettaārāmuyyānayoggādikampi antamaso bhājanabhaṇḍakampi attharaṇapāvuraṇanisīdanampi sabbaṁ attano santakaṁ vikkiṇi`
- `khīṇāsavausabhānañhi antare jeṭṭhakausabhā mama puttasadisā bhikkhū na bhāyantī ti vatvā brāhmaṇavagge imaṁ gāthamāha`
- `aparā nimbamuṭṭhin tiādinā nayena attanā attanā kataṁ parittadānaṁ ārocetvā iminā iminā kāraṇena amhehi ayaṁ sampatti laddhā ti āhaṁsu`
- `atha naṁ satthā upāsaka pubbepi mayā itthiyo nāma nadīādisadisā`

*rendered but not contiguous in PDF*

- `ord6 [before] @7/8: satthari jetavane viharante devasikaṁ tīṇi mahā`
- `ord6 [before] @0/11: upaṭṭhānāni gacchati gacchanto ca kiṁ nu kho`
- `ord11 [before] @6/7: evamevaṁ akusalacetanāya abhāvena pāpaṁ akarontassa dhanu`
- `ord11 [before] @1/11: ādīni nīharitvā dadatopi pāpaṁ nāma na hotī ti`
- `ord40 [before] @7/8: tattha ca ekadivasaṁ katapariccāgo dhanassa cuddasakoṭi`
- `ord40 [before] @1/6: agghanako ahosi tathāgatassa setacchattaṁ nisīdanapallaṅko ādhārako`
- `ord41 [before] @8/9: karontānaṁ gehaṁ gantvā tirokuṭṭesu tiṭṭhantī ti`
- `ord41 [before] @2/7: ādinā nayena avamaṅgalaṁ katheti avamaṅgalaṁ karontānaṁ gehaṁ`

### 23AbhiT02 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Catusaccadasoti cattāri saccāni samāhaṭāni catusaccaṁ, catusaccaṁ`
- `passīti catusaccadaso. Satipi sāvakānaṁ paccekabuddhānañca`
- `catusaccadassanabhāve anaññapubbakattā bhagavato catusaccadassanassa`
- `tattha ca sabbaññutāya dasabalesu ca vasībhāvassa pattito parasantānesu ca`
- `pasāritabhāvena supākaṭattā bhagavāva visesena “catusaccadaso”ti`
- `thomanaṁ arahatīti. Nāthatīti nātho, veneyyānaṁ hitasukhaṁ āsīsati`
- `pattheti, parasantānagataṁ vā kilesabyasanaṁ upatāpeti, “sādhu bhikkhave`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `catusaccadasoti cattāri saccāni samāhaṭāni catusaccaṁ`
- `satipi sāvakānaṁ paccekabuddhānañca catusaccadassanabhāve anaññapubbakattā bhagavato catusaccadassanassa tattha ca sabbaññutāya dasabalesu ca vasībhāv`
- `veneyyānaṁ hitasukhaṁ āsīsati pattheti`
- `parasantānagataṁ vā kilesabyasanaṁ upatāpeti`
- `sādhu bhikkhave bhikkhu kālena kālaṁ attasampattiṁ paccavekkhitā tiādinā vā taṁ taṁ hitapaṭipattiṁ yācatīti attho`
- `sabbasatte vā guṇehi īsati abhibhavatīti paramissaro bhagavā nātho ti vuccati`
- `saddhamme gāravaṁ katvā karissāmī ti sotabbabhāve kāraṇaṁ vatvā puna savane niyojento āha taṁ suṇātha samāhitā ti`

*rendered but not contiguous in PDF*

- `ord59 [text] @58/578: ettha vavatthitā dassitānaṁ catukkānaṁ nayabhāvāti avijjaṁ aṅgaṁ aggahetvā tato paraṁ avijjāpaccayā saṅkhāro`
- `ord73 [text] @591/829: so evarūpo bāhitapāpasamitapāpabhinnakilesatāhi brāhmaṇādisamañño veditabbo asammissatoti vedanādayopi ettha sitā ettha paṭibad`
- `ord321 [text] @75/462: catukkānanti vāracatukkānaṁ vārasoḷasakassa nayabhāvatoti adhippāyo paccayasahitapaccayuppannāni aṅgabhāvena vuttāni na kevalaṁ`
- `ord333 [text] @286/389: sāpi bhikkhubhāve niyatāyeva nāma hoti etthāti kāye avayavā assa atthīti avayavī samudāyo`
- `ord425 [text] @2/75: atthipaṭiccaṁ nāmāti atthitā paṭiccattho nāma asatipi sahajātapurejātādibhāve yasmiṁ sati`
- `ord426 [text] @0/2: vatthunāti jātiādipavattihetunā`
- `ord427 [text] @1/55: patiṭṭhābhāvoti kusalakammesu patiṭṭhānābhāvo so pana yasmā kusalakiriyāya ṭhānaṁ`
- `ord428 [text] @0/4: anivātavuttitāya hetubhūto cittasampaggaho mānaviseso`

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

### 24AbhiT03 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Dhātukathāpakaraṇaṁ desento bhagavā yasmiṁ samaye desesi, taṁ`
- `samayaṁ dassetuṁ, vibhaṅganantaraṁ desitassa pakaraṇassa`
- `dhātukathābhāvaṁ dassetuṁ vā “aṭṭhārasahī”ti-ādimāha. Tattha`
- `balavidhamanavisayātikkamanavasena devaputtamārassa,`
- `appavattikaraṇavasena kilesābhisaṅkhāramārānaṁ,`
- `samudayappahānapariññāvasena khandhamārassa, maccumārassa ca`
- `bodhimūle eva bhañjitattā parūpanissayarahitaṁ niratisayaṁ taṁ bhañjanaṁ`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `dhātukathāpakaraṇaṁ desento bhagavā yasmiṁ samaye desesi`
- `vibhaṅganantaraṁ desitassa pakaraṇassa dhātukathābhāvaṁ dassetuṁ vā aṭṭhārasahī tiādimāha`
- `maccumārassa ca bodhimūle eva bhañjitattā parūpanissayarahitaṁ niratisayaṁ taṁ bhañjanaṁ upādāya bhagavā eva mārabhañjano ti thomito`
- `mārabhañjanaṁ vā etassa na pararājādibhañjananti mārabhañjano`
- `khandhādayo araṇanto dhammā sabhāvaṭṭhena dhātuyo`
- `abhidhammakathādhiṭṭhānaṭṭhena vāti katvā tesaṁ kathanato imassa pakaraṇassa dhātukathāti adhivacanaṁ`
- `yadipi aññesu ca pakaraṇesu te sabhāvā kathitā`

*rendered but not contiguous in PDF*

- `ord867 [text] @401/412: nihantvā timiraṁ loke udito sataraṁsami sirīvilāsarūpena sabbasobhāvibhāvinā obhāsetvādito buddho sarataṁsi yathā paro`
- `ord959 [text] @1/98: vitakkattike sattasu mūlakesūti savitakkasavicāraṁ dhammaṁ paṭiccā tiādinā āgatāni`
- `ord960 [text] @1/35: avisesenāti vipākan ti visesanaṁ akatvā na pana vissajjanaṁ`
- `ord961 [text] @1/60: etanti avitakkavicāramattaṁ avitakka saha gacchantenā ti āgatapāḷipadaṁ tassa`
- `ord962 [text] @1/72: mūlapadameva avasānabhāvenāti savitakkasavicāraṁ dhammaṁ paccayā savitakkasavicāro dhammo uppajjati`

### 24KhuA05 (commentary)

*missing from render (line)*

- `Yañca uparimaheṭṭhimapuratthimapacchimakāyehi dakkhiṇavāmaakkhikaṇṇasotanāsikāsota-aṁsakūṭapassahatthapādehi aṅgulaṅgulantarehi`

*missing from render (chunk)*

- `yañca uparimaheṭṭhimapuratthimapacchimakāyehi dakkhiṇavāmaakkhikaṇṇasotanāsikāsotaaṁsakūṭapassahatthapādehi aṅgulaṅgulantarehi lomalomakūpehi ca aggik`

*rendered but not contiguous in PDF*

- `ord39 [after] @9/10: satte jānātī tiādi yañca uparimaheṭṭhimapuratthimapacchimakāyehi dakkhiṇavāma`
- `ord39 [after] @0/12: akkhikaṇṇasotanāsikāsotaaṁsakūṭapassahatthapādehi aṅgulaṅgulantarehi lomalomakūpehi ca aggikkhandhūdakadhārāpavattanaṁ anaññasādh`

### 25KhuA06 (commentary)

*missing from render (line)*

- `“Yesaṁ kho pana so paṭiggaṇhāti cīvarapiṇḍapātasenāsanagilānappaccayabhesajjaparikkhāraṁ, tesaṁ taṁ mahapphalaṁ hoti`

*missing from render (chunk)*

- `yo rāgamudacchidā asesanti ayaṁ dutiyagāthā`
- `sandiṭṭhikasamparāyikaṁ ādīnavaṁ agaṇetvā muhutteneva paracakkavāḷampi bhavaggampi sampāpuṇituṁ samatthanti vuttaṁ hoti`
- `tehipi mahārājavādena ālapito nāhaṁ bhaṇe rājā ti āha`
- `evaṁ mahagghatāvacane cettha dosābhāvasādhakaṁ idaṁ tāva suttapadaṁ veditabbaṁ yesaṁ kho pana so paṭiggaṇhāti cīvarapiṇḍapātasenāsanagilānappaccayabhe`

*rendered but not contiguous in PDF*

- `ord227 [after] @5/6: yesaṁ kho pana so paṭiggaṇhāti cīvarapiṇḍapātasenāsana`
- `ord227 [after] @0/21: gilānappaccayabhesajjaparikkhāraṁ tesaṁ taṁ mahapphalaṁ hoti mahānisaṁsaṁ idamassa`

### 25VsmT01 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Saddhammaraṁsimālī yo, vineyyakamalākare.`
- `Vibodhesi mahāmoha-tamaṁ hantvāna sabbaso.`
- `Ñāṇātisayabimbaṁ taṁ, visuddhakaruṇāruṇaṁ.`
- `Vanditvā nirupaklesaṁ, buddhādiccaṁ mahodayaṁ.`
- `Lokālokakaraṁ dhammaṁ, guṇarasmisamujjalaṁ.`
- `Ariyasaṁghañca samphullaṁ, visuddhakamalākaraṁ.`
- `Vandanājanitaṁ puññaṁ, iti yaṁ ratanattaye.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`
- `vibodhesi mahāmohatamaṁ hantvāna sabbaso`

*rendered but not contiguous in PDF*

- `ord19 [text] @409/1256: āha arahantādīnan ti sabbadarathappaṭippassaddhiyāti sabbakilesadarathappaṭippassaddhiyā pāṇātipātādīnanti ādisaddena adinnādā`
- `ord38 [text] @293/1090: catukkanayavasena cetaṁ vuttaṁ hānabhāgiyādivasenāti hānakoṭṭhāsikādivasena channaṁanussatiṭṭhānānanti buddhānussatiādīnaṁ cha`
- `ord347 [text] @88/91: sugatiparāyaṇo vā indriyānaṁ aparipakkatāyanti adhippāyo catudhātuvavatthānaniddesassa līnatthavaṇṇanā niṭṭhitā`

### 26KhuA07 (commentary)

*missing from render (line)*

- `Ayaṁ vā aparo nayo–Saṅgahoti dhammikāhi dānapiyavācaatthacariyāhi saṅgaṇhanaṁ. Seyyathidaṁ? Uposathadivasesu`
- `“Mahāsamayo pavanasmiṁ -padakkhitāye aparājitasaṁghan”ti2.`
- `“Tatra bhikkhavo samādahaṁsu -paindriyāni rakkhanti paṇḍitā”ti2.`
- `“Ye keci Buddhaṁ saraṇaṁ gatāse -padevakāyaṁ paripūressantī”ti2.`

*missing from render (chunk)*

- `ayaṁ vā aparo nayo saṅgahoti dhammikāhi dānapiyavācaatthacariyāhi saṅgaṇhanaṁ`
- `evaṁ gantvā ca tattha eko brahmā puratthimacakkavāḷamuddhani okāsaṁ labhitvā tattha ṭhito imaṁ gāthaṁ abhāsi mahāsamayo pavanasmiṁ dakkhitāye aparājit`
- `dutiyo pacchimacakkavāḷamuddhani okāsaṁ labhitvā tattha ṭhito taṁ gāthaṁ sutvā imaṁ gāthaṁ abhāsi tatra bhikkhavo samādahaṁsu indriyāni rakkhanti paṇḍ`
- `catuttho uttaracakkavāḷamuddhani okāsaṁ labhitvā tattha ṭhito taṁ gāthaṁ sutvā imaṁ gāthamabhāsi ye keci buddhaṁ saraṇaṁ gatāse devakāyaṁ paripūressan`
- `imissā pana gāthāya dutiyagāthā bhāvanānubhāvappakāsananayena vuttāti veditabbā`
- `tasmā tamatthaṁ dassento yassindriyānī ti gāthāya tatiyapañhaṁ byākāsi`

*rendered but not contiguous in PDF*

- `ord8 [after] @43/44: vā aparo nayo saṅgahoti dhammikāhi dānapiyavāca`
- `ord8 [after] @0/25: atthacariyāhi saṅgaṇhanaṁ seyyathidaṁ uposathadivasesu paribbayadānaṁ nakkhattadivasesu nakkhattadassāpanaṁ`

### 26VsmT02 (subcommentary)

*missing from render (line)*

- `Namo tassa Bhagavato Arahato Sammāsambuddhassa.`
- `Nigamanakathāvaṇṇanā.`

*missing from render (chunk)*

- `namo tassa bhagavato arahato sammāsambuddhassa`

*rendered but not contiguous in PDF*

- `ord31 [text] @174/466: idaṁ yathādhikatatthadassanavasena vuttaṁ khuddakabhāvāpādanampettha labbhateva olokesi buddhāciṇṇavasena atthi nu kho assa upa`
- `ord123 [text] @67/78: sabbapakārenapīti attho iti saṅkhārakkhandhe vitthārakathāmukhavaṇṇanā abhidhammantogadhampi suttantabhājanīyaṁ suttantanayo eva`
- `ord168 [text] @91/137: dhammāti āha aṭṭha dhammā ti bhaveti ādānanikkhepaparicchinno dhammappabandho bhavo tasmiṁ bhave so`
- `ord519 [text] @41/129: yogīhi etasmiṁ visuddhimagge ādaro karaṇīyoyevāti ettāvatā ca suvisuddhasamācāro visuddhanayamaṇḍitaṁ visuddhimaggaṁ lokassa ya`

### 27KhuA08 (commentary)

*missing from render (chunk)*

- `ettha ca paramaalaṅkatā ti purimasmiṁ pakkhe sandhiṁ akatvā dutiyasmiṁ pakkhe avibhattikaniddeso daṭṭhabbo`

### 29KhuA10 (commentary)

*missing from render (chunk)*

- `evāyaṁ sukhamedhatī ti imāya tatiyagāthāya aññaṁ byākāsi`

### 33KhuA14 (commentary)

*missing from render (line)*

- `nāma tā ayyaputta accharāyo, yāsaṁ tvaṁ hetu brahmacariyaṁ carasī”tiādīni2 vatvā palobhanakammaṁ kātuṁ āraddhe tassādhippāyaṁ`

*rendered but not contiguous in PDF*

- `ord54 [before] @9/10: yāsaṁ tvaṁ hetu brahmacariyaṁ carasī ti`
- `ord54 [before] @0/6: ādīni vatvā palobhanakammaṁ kātuṁ āraddhe tassādhippāyaṁ`

### 35KhuA16 (commentary)

*rendered but not contiguous in PDF*

- `ord336 [text] @764/10682: sammadeva paripūritā dasa pāramiyo dasseti imasmiṁ pana ṭhāne ṭhatvā mahābodhiyānapaṭipattiyaṁ ussāhajātānaṁ kulaputtānaṁ`

### 36KhuA17 (commentary)

*missing from render (line)*

- `ya’dapaṇṇakanti yaṁ apaṇṇakaṁ ekaṁsikaṁ sukkapaṭipadāaparihāniyapaṭipadāsaṅkhātaṁ niyyānikakāraṇaṁ, tadeva gaṇheyya. Kasmā?`
- `parikkhipāpetvā antosāṇiyaṁ daharabhikkhuniyā hatthapādanābhiudarapariyosānādīni oloketvā māsadivase samānetvā gihibhāve gabbhassa`
- `pūjaṁ akāsi. Bodhisatto “dhammaṁ cara mahārāja, mātāpitūsu khattiyā”tiādīhi1 tesakuṇajātake āgatāhi dasahi dhammacariyagāthāhi rañño dhammaṁ`
- `sāmivacanaṁ, ati-asanena atibhuttenāti attho. Pāyāsassapi tappatīti sappiādīhi abhisaṅkhatena madhurapāyāsena tappati titto hoti, dhāto suhito na`
- `Sakko “kahaṁ nu kho nibbattā”ti tattha nibbattabhāvaṁ ñatvā suvaṇṇaeḷālukānaṁ yānakaṁ pūretvā majjhe gāmassa mahallakavesena nisīditvā`
- `sakkāragarukāramānanavandanapūjanāni ceva abhivādanapaccuṭṭhānaañjalikammasāmīcikammāni ca karissāma, ovāde ca te ṭhassāma, tvaṁ pana`
- `kuddālakena bhūmiparikammaṁ katvā ḍākañceva alābukumbhaṇḍaeḷālukādīni ca vapitvā tāni vikkiṇanto kapaṇajīvikaṁ kappesi. Tañhissa`
- `pacchinne sappo tāpasaṁ vanditvā āha “bhante tumhehi mayhaṁ mahāupakāro kato, na kho panāhaṁ daliddo, asukaṭṭhāne me cattālīsa`

*missing from render (chunk)*

- `taṁ gaṇhe ya dapaṇṇakanti yaṁ apaṇṇakaṁ ekaṁsikaṁ sukkapaṭipadāaparihāniyapaṭipadāsaṅkhātaṁ niyyānikakāraṇaṁ`
- `upāsikā sādhū ti sampaṭicchitvā sāṇiṁ parikkhipāpetvā antosāṇiyaṁ daharabhikkhuniyā hatthapādanābhiudarapariyosānādīni oloketvā māsadivase samānetvā g`
- `mātāpitūsu khattiyā tiādīhi tesakuṇajātake āgatāhi dasahi dhammacariyagāthāhi rañño dhammaṁ desetvā mahārāja ito paṭṭhāya appamatto hotī ti rājānaṁ pa`
- `pāyāsassapi tappatīti sappiādīhi abhisaṅkhatena madhurapāyāsena tappati titto hoti`
- `sakko kahaṁ nu kho nibbattā ti tattha nibbattabhāvaṁ ñatvā suvaṇṇaeḷālukānaṁ yānakaṁ pūretvā majjhe gāmassa mahallakavesena nisīditvā eḷālukāni gaṇhat`
- `ito paṭṭhāya mayaṁ tava sakkāragarukāramānanavandanapūjanāni ceva abhivādanapaccuṭṭhānaañjalikammasāmīcikammāni ca karissāma`
- `sāpi tassa upāsakassa itthī sammāsambuddhena kira mayhaṁ durācārabhāvo ñāto ti tato paṭṭhāya pāpakammaṁ nāma na akāsi`
- `so kuddālakena bhūmiparikammaṁ katvā ḍākañceva alābukumbhaṇḍaeḷālukādīni ca vapitvā tāni vikkiṇanto kapaṇajīvikaṁ kappesi`

*rendered but not contiguous in PDF*

- `ord26 [before] @3/4: parikkhipāpetvā antosāṇiyaṁ daharabhikkhuniyā hatthapādanābhi`
- `ord26 [before] @0/6: udarapariyosānādīni oloketvā māsadivase samānetvā gihibhāve gabbhassa`
- `ord55 [before] @2/3: sakkāragarukāramānanavandanapūjanāni ceva abhivādanapaccuṭṭhāna`
- `ord55 [before] @0/9: añjalikammasāmīcikammāni ca karissāma ovāde ca te ṭhassāma`
- `ord88 [verse] @147/159: cari sāpi tassa upāsakassa itthī ghaṭetvā jātakaṁ samodhānesi tadā jayampatikāyeva idāni jayampatikā`
- `ord94 [before] @4/5: kuddālakena bhūmiparikammaṁ katvā ḍākañceva alābukumbhaṇḍa`
- `ord94 [before] @0/8: eḷālukādīni ca vapitvā tāni vikkiṇanto kapaṇajīvikaṁ kappesi`
- `ord99 [before] @8/9: vanditvā āha bhante tumhehi mayhaṁ mahā`

### 37KhuA18 (commentary)

*missing from render (line)*

- `vaḍḍhakīhi saddhiṁ rukkhe nīharati, tacchentānaṁ parivattetvā deti, vāsiādīni upasaṁharati, soṇḍāya veṭhetvā kāḷasuttakoṭiyaṁ gaṇhāti.`
- `karissantīti. Porāṇasaṅghāṭiṁ uttarāsaṅgaṁ karissantīti. Porāṇauttarāsaṅgaṁ kiṁ karissantīti. Antaravāsakaṁ karissantīti. Porāṇaantaravāsakaṁ kiṁ kari`
- `morayoniyaṁ paṭisandhiṁ gahetvā aṇḍakālepi kaṇikāramakuḷavaṇṇaaṇḍakoso hutvā aṇḍaṁ bhinditvā nikkhanto suvaṇṇavaṇṇo ahosi dassanīyo`
- `hatthimaṅgalakārako ahosi. Hatthīnaṁ maṅgalakaraṇaṭṭhāne ābhataupakaraṇabhaṇḍañca hatthālaṅkārañca sabbaṁ soyeva alattha. Evamassa`
- `Natthi itthīsu saccanti etāsu sabhāvo nāmeko natthi. “Imañca jamman”tiādidvinnampi tesaṁ daṇḍāṇāpanavasena vuttaṁ. Tattha jammanti lāmakaṁ.`
- `Bodhisatto gehaṁ pavisitvā tesaṁ kiriyaṁ disvā “imāya pāpāya kataupāyo esa bhavissatī”ti ñatvā gāmabhojakaṁ āmantetvā “bho gāmabhojaka`
- `pūjito apacito lābhī cīvarapiṇḍapātasenāsanagilānapaccayabhesajjaparikkhārānaṁ. Bhikkhusaṁghopi kho sakkato hoti -paparikkhārānaṁ. Aññatitthiyā pana p`
- `kāmaguṇehi nimantento “bhante Ānanda mama gehe pahūtaṁ saviññāṇakaaviññāṇakaratanaṁ, idaṁ majjhe bhinditvā tuyhaṁ dammi, ehi ubho agāraṁ`

*missing from render (chunk)*

- `atīte bārāṇasiyaṁ brahmadatte rajjaṁ kārente bodhisatto morayoniyaṁ paṭisandhiṁ gahetvā aṇḍakālepi kaṇikāramakuḷavaṇṇaaṇḍakoso hutvā aṇḍaṁ bhinditvā n`
- `hatthīnaṁ maṅgalakaraṇaṭṭhāne ābhataupakaraṇabhaṇḍañca hatthālaṅkārañca sabbaṁ soyeva alattha`
- `tasmā dumasākhagocaro ti vuccati`
- `imañca jamman tiādidvinnampi tesaṁ daṇḍāṇāpanavasena vuttaṁ`
- `bodhisatto gehaṁ pavisitvā tesaṁ kiriyaṁ disvā imāya pāpāya kataupāyo esa bhavissatī ti ñatvā gāmabhojakaṁ āmantetvā bho gāmabhojaka amhe tava jaragoṇ`
- `idāni anodissakavasena mettābhāvanaṁ dassento imaṁ gāthamāha sabbe sattā sabbe pāṇā`
- `luddo kāḷakaṇṇinā sakuṇenamhi pahaṭo ti nivattitvā thokaṁ sayitvā puna sattiṁ gahetvā uṭṭhāsi`
- `tena kho pana samayena bhagavā sakkato hoti garukato mānito pūjito apacito lābhī cīvarapiṇḍapātasenāsanagilānapaccayabhesajjaparikkhārānaṁ`

*rendered but not contiguous in PDF*

- `ord12 [before] @7/8: rukkhe nīharati tacchentānaṁ parivattetvā deti vāsi`
- `ord12 [before] @0/6: ādīni upasaṁharati soṇḍāya veṭhetvā kāḷasuttakoṭiyaṁ gaṇhāti`
- `ord14 [before] @4/5: karissantīti porāṇasaṅghāṭiṁ uttarāsaṅgaṁ karissantīti porāṇa`
- `ord14 [before] @1/6: uttarāsaṅgaṁ kiṁ karissantīti antaravāsakaṁ karissantīti porāṇa`
- `ord14 [before] @1/5: antaravāsakaṁ kiṁ karissantīti paccattharaṇaṁ karissantīti`
- `ord14 [verse] @75/160: unnatā dantā assa atthīti unnadantī tassa vacanaṁ sutvā sīho sīhiṁ āha bhadde`
- `ord18 [before] @4/5: morayoniyaṁ paṭisandhiṁ gahetvā aṇḍakālepi kaṇikāramakuḷavaṇṇa`
- `ord18 [before] @0/8: aṇḍakoso hutvā aṇḍaṁ bhinditvā nikkhanto suvaṇṇavaṇṇo ahosi`

### 38KhuA19 (commentary)

*missing from render (line)*

- `kiccena nagaraṁ āgacchasi, dakkhiṇadvāre ṭhatvā dovārikaṁ ‘Mahāassāroho kataragehe vasatī’ti pucchitvā dovārikaṁ gahetvā amhākaṁ gehaṁ`
- `tividhaṁ kāyikavācasikamānasikavasena, catubbidhaṁ pātimokkhasaṁvaraindriyasaṁvara-ājīvapārisuddhipaccayasannissitavasenāti mātikaṁ ṭhapetvā`
- `Rañño ca nāmaṁ upadhārentassa saṁvaccharo atīto. Tadā hatthiassamanusse sīhādayo vāḷā gaṇhanti, dīghajātikaparipantho hoti,`
- `thāmabalasampanno ahosi, so aññesaṁ gijjhānaṁ sīmaṁ atikkamitvā atiuccaṁ uppati. Gijjhā “putto te atidūraṁ uppatatī”ti gijjharañño ācikkhiṁsu.`
- `sattā, te attano maraṇe āgacchante ṭhapetvā sīhamigarājahatthājānīyaassājānīyakhīṇāsave avasesā bodhisattaṁ ādiṁ katvā abhāyantā nāma natthi.`
- `pūretvā adāsi. Brāhmaṇo gāmanigamarājadhānīsu caranto satta kahāpaṇasatāni labhitvā “alaṁ me ettakaṁ dhanaṁ`
- `āgantukasaṅgahaṁ ārabbha kathesi. So kira ekasmiṁ samaye paveṇiāgatānaṁ porāṇakayodhānaṁ saṅgahaṁ akatvā abhinavāgatānaṁ`
- `ativiya āhari. Bahuttasoti bahuso1. Jānaṁ uccaṁ papātinanti “putto te atiuccaṁ ṭhānaṁ laṅghatī”ti sutvā “ucce papātī ayan”ti jānanto. Tejassinti`

*missing from render (chunk)*

- `dakkhiṇadvāre ṭhatvā dovārikaṁ mahāassāroho kataragehe vasatī ti pucchitvā dovārikaṁ gahetvā amhākaṁ gehaṁ āgaccheyyāsī ti vatvā pakkāmi`
- `vuttampi cetaṁ yathāpi bījamaggimhi`
- `tāyapi kiṁ te karomī ti vuttā iminā kākena ekacārikavāraṇassa akkhīsu bhinnesu tumhehi tattha āsāṭikaṁ pātetuṁ icchāmī ti vatvā tāyapi sādhū ti vutte `
- `catubbidhaṁ pātimokkhasaṁvaraindriyasaṁvaraājīvapārisuddhipaccayasannissitavasenāti mātikaṁ ṭhapetvā vitthārento sīlassa vaṇṇaṁ abhāsi`
- `tadā hatthiassamanusse sīhādayo vāḷā gaṇhanti`
- `so aññesaṁ gijjhānaṁ sīmaṁ atikkamitvā atiuccaṁ uppati`
- `nandiyo taṁ sutvā gaccheyyāmahaṁ brāhmaṇa`
- `rājā migaṁ vijjhissāmī ti khurappaṁ sannayhi`

*rendered but not contiguous in PDF*

- `ord6 [before] @6/7: nagaraṁ āgacchasi dakkhiṇadvāre ṭhatvā dovārikaṁ mahā`
- `ord6 [before] @1/9: assāroho kataragehe vasatī ti pucchitvā dovārikaṁ gahetvā amhākaṁ`
- `ord9 [verse] @92/107: khittabījamiva nassatīti attho vuttampi cetaṁ satthā imaṁ dhammadesanaṁ āharitvā jātakaṁ samodhānesi tadā`
- `ord210 [verse] @38/52: sīsañca hatthapādā ca na dissanti ito paṭṭhāya na socissāmi pitusokaharaṇakaputtena nāma tādisena`
- `ord243 [verse] @98/182: vutte ekaṁ maṇḍūkaṁ upaṭṭhahitvā tena athekadivasaṁ kāko vāraṇassa dvepi akkhīni tuṇḍena bhindi`
- `ord245 [verse] @21/40: tumhe disvā anuṭṭhahamānā dosakārikāti attho katvā lohitalittā paridevamānā vicari puna coraghātako kiṁ`
- `ord357 [verse] @71/81: ti vutto catukuṭṭikanirayo ti vuccati evaṁ darīmukhapaccekabuddho gabbhaokkantimūlakañca parihāramūlakañca dukkhaṁ dassetvā idā`
- `ord366 [before] @7/8: nāmaṁ upadhārentassa saṁvaccharo atīto tadā hatthi`

### 39KhuA20 (commentary)

*missing from render (line)*

- `tvaṁ lolabhāvaṁ nissāya Bārāṇasiyaṁ hatthikuṇapādīhi atitto mahāaraññaṁ paviṭṭho”ti vatvā atītaṁ āhari.`
- `rukkhaggatiṇaggasākhaggamakkaṭakasuttajālādīsu muttājālākārena laggitaussavabindūni disvā “samma sārathi kiṁ nāmetan”ti pucchitvā “ete deva`
- `upasaṅkamitvā “tumhākaṁ yaññaṁ yajissāma, dhanaṁ dethā”ti evaṁ bhatiatthāya yadā yaññaṁ yajissanti. Pahū santoti3 bharituṁ posetuṁ samatthā`
- `Kaniṭṭhabhātiko yāva pubbaṇhasamayā javitvā kilami, pakkhasandhīsu aggiuṭṭhānakālo viya ahosi. So bodhisattassa saññaṁ adāsi “bhātika na.`
- `Ukkā cilācā bandhantīti idaṁ Satthā Jetavane viharanto Mittabandhakaupāsakaṁ1 ārabbha kathesi. So kira Sāvatthiyaṁ parijiṇṇassa kulassa putto`
- `uggahetvā mahāvināsaṁ pāpuṇāti, tasmā tava putte atthanissitesu vaḍḍhiāvahesu kiccesu yojetvā sikkhāpehīti. Nise aggīvāti mahārāja hīnajātikopi`
- `saraṁ dūre pātetuṁ samatthā. Akkhaṇavedhinoti aviraddhavedhino, vijjuālokena vijjhanasamatthā vā. Sarānīti anotattādīni mahāsarāni khīyantiyeva.`

*missing from render (chunk)*

- `rājā kenaci pariyāyena tassā manaṁ alabhanto taṁ ekasmiṁ gabbhe kāretvā cintesi ayaṁ paribbājikā evarūpaṁ yasaṁ na icchati`
- `rājā ayaṁ kujjhitvā mayā saddhiṁ na sallapatī ti maññamāno ayaṁ kūṭatāpaso kodhassa uppajjituṁ na dassāmi`
- `vācāya paliguṇṭhitāti idaṁ dassāma`
- `ubhaye ttha vīthiyoti ettha ākāse ayaṁ candassa vīthi`
- `pubbepi tvaṁ lolabhāvaṁ nissāya bārāṇasiyaṁ hatthikuṇapādīhi atitto mahāaraññaṁ paviṭṭho ti vatvā atītaṁ āhari`
- `ahaṁ bhikkhābhājanaṁ me tayā bhinnaṁ`
- `ṭhānaṁ natthīti uppannā saṅkhārā abhijjitvā tiṭṭhantū ti patthanāyapi tesaṁ ṭhānaṁ nāma natthi`
- `evaṁ gacchante kāle bodhisatto ekadivasaṁ pātova rathavaramāruyha mahantena sirivibhavena uyyānakīḷaṁ gacchanto rukkhaggatiṇaggasākhaggamakkaṭakasutta`

*rendered but not contiguous in PDF*

- `ord37 [verse] @138/177: taṁ ekasmiṁ gabbhe kāretvā cintesi olokitamattampi na akāsi pabbajitā kho pana bahumāyā`
- `ord97 [verse] @110/186: dīpeti sukkhañjalipaggahitāti paggahitatucchaañjalino vācāya paliguṇṭhitāti sabbesaṁ upaghātakaraṁ nisitaṁva paṭicchannanti ko`
- `ord108 [verse] @28/34: ubhaye ttha vīthiyoti ettha ākāse evaṁ māṇave kathente brāhmaṇo sallakkhetvā gāthamāha`
- `ord123 [before] @6/7: lolabhāvaṁ nissāya bārāṇasiyaṁ hatthikuṇapādīhi atitto mahā`
- `ord123 [before] @2/6: araññaṁ paviṭṭho ti vatvā atītaṁ āhari`
- `ord185 [verse] @108/236: ṭhāne saritabbayuttakaṁ kathaṁ vītisārayimha ahaṁ bahukampi akataññurūpāti yasmā bālā akataññusabhāvā tasmā tesu`
- `ord217 [verse] @43/54: sīghaṁ atikkamatīti dasseti ṭhānaṁ natthīti evaṁ mahāsatto tassā ovādamadāsi sāpi tassa dhammakathāya`
- `ord233 [before] @2/3: rukkhaggatiṇaggasākhaggamakkaṭakasuttajālādīsu muttājālākārena laggita`

### 40KhuA21 (commentary)

*missing from render (line)*

- `udakapariyante yojanavitthatameva nīlapītalohitaodātasurabhisukhumakusumasamākiṇṇaṁ khuddakagacchavanaṁ, iti imāni`
- `khuddakarājamāsamahārājamāsamuggavanaṁ, tadanantaraṁ tipusaelālukalābukumbhaṇḍavallivanāni, tato pūgarukkhappamāṇaṁ ucchuvanaṁ,`
- `sākhaṁ abhiruyha tena pāpapurisena saddhiṁ sallapanto “mā’yyo man”tiādimāha. Tattha Mā’yyo maṁ kari bhaddanteti mā akari ayyo maṁ`
- `gacchantā vaḍḍhanti. Sa-usabhāmivāti sa-usabhā iva. Appamattassa hi sausabhajeṭṭhako gogaṇo viya bhogā vaḍḍhanti. Upassutinti`
- `vasena nassanti, antojanā bahi gacchanti, tasmā tvaṁ suṭṭhusaṅgahitaantojano hutvā “ettakaṁ nāma me vittan”ti sayaṁ attano dhanaṁ.`
- `purimabhāgena nikkhamāpesi, udake catu-usabhaṁ, thale aṭṭhausabhaṭṭhānaṁ kaṇḍaṁ pesesi. Vātiṅgaṇasaññāya usabhamattake vālaṁ`
- `Anusisso Nāradoti satta jeṭṭhantevāsino ahesuṁ. Aparabhāge Kapiṭṭhakaassamo paripūri. Isigaṇassa vasanokāso nappahoti.`
- `paṭipadaṁ kathetvā idāni tassā paññāya guṇaṁ kathento “sa paññavā”tiādimāha. Tattha kāmaguṇeti kāmakoṭṭhāse hutvā abhāvaṭṭhena aniccato,`

*missing from render (chunk)*

- `tadanantaraṁ udakapariyante yojanavitthatameva nīlapītalohitaodātasurabhisukhumakusumasamākiṇṇaṁ khuddakagacchavanaṁ`
- `so maraṇabhayabhīto olambantaṁ cammabandhaṁ hatthena gahetvā uppatitvā sākhaṁ abhiruyha tena pāpapurisena saddhiṁ sallapanto mā yyo man tiādimāha`
- `appamattassa hi sausabhajeṭṭhako gogaṇo viya bhogā vaḍḍhanti`
- `bodhisatto purohitassa sarīre adhimuccitvā purato gantvā pariggaṇhissāma tāva mahārājā ti āha`
- `tasmā tvaṁ suṭṭhusaṅgahitaantojano hutvā ettakaṁ nāma me vittan ti sayaṁ attano dhanaṁ`
- `thale aṭṭhausabhaṭṭhānaṁ kaṇḍaṁ pesesi`
- `atha naṁ mahāsatto sakka pacchimaṁ mayā ayaṁ hīno ti ñatvā pharusavacanaṁ adhivāsentassa vasena vuttaṁ`
- `evaṁ mahāsatto pācīnalokadhātuto sūriyaṁ uṭṭhāpento viya paññāya paṭipadaṁ kathetvā idāni tassā paññāya guṇaṁ kathento sa paññavā tiādimāha`

*rendered but not contiguous in PDF*

- `ord95 [verse] @155/185: tattha agamāsi tāpaso te disvāva kathesi porisādo tassa saddahitvā tāta tvaṁ gaccha`
- `ord98 [before] @2/3: udakapariyante yojanavitthatameva nīlapītalohita`
- `ord98 [before] @0/4: odātasurabhisukhumakusumasamākiṇṇaṁ khuddakagacchavanaṁ iti imāni`
- `ord98 [before] @2/3: khuddakarājamāsamahārājamāsamuggavanaṁ tadanantaraṁ tipusa`
- `ord98 [before] @0/4: elālukalābukumbhaṇḍavallivanāni tato pūgarukkhappamāṇaṁ ucchuvanaṁ`
- `ord312 [before] @7/8: sausabhāmivāti sausabhā iva appamattassa hi sa`
- `ord312 [before] @0/6: usabhajeṭṭhako gogaṇo viya bhogā vaḍḍhanti upassutinti`
- `ord316 [verse] @120/149: purohitassa sarīre adhimuccitvā purato gantvā rakkhamānā tāsaṁ araññaṁ gantuṁ na deti sayaṁ`

### 41KhuA22 (commentary)

*missing from render (line)*

- `tato aggisantāpanato apanetvā “tāta Temiyakumāra mayaṁ tava apīṭhasappiādibhāvaṁ jānāma. Na hi etesaṁ evarūpāni hatthapādakaṇṇasotāni honti,`
- `pītisomanassaṁ pavattayiṁsu. Antonidhīti rājagehe mahādvārassa antoummārā nidhiṁ nīharāpesi. Bahi nidhīti bahi-ummārā nidhiṁ nīharāpesi.`
- `aṭṭhaṁsu. Ekato amaccamaṇḍalaṁ nisīdi, ekato brāhmaṇagaṇo, ekato seṭṭhiādayo nisīdiṁsu, ekato uttamarūpadharā nāṭakitthiyo nisīdiṁsu, brāhmaṇāpi`
- `amacco sayameva rañño santikaṁ gantvā “mahārāja paṇḍitena evaṁ rathaaḍḍo suvinicchito, Sakkopi tena parājito, kasmā purisavisesaṁ na jānāsi`
- `āṇiyā akkantāya pidhīyati, ekāya āṇiyā akkantāya vivarīyati. Mahāumaṅgassa dvīsu passesu iṭṭhakāhi cinitvā sudhākammaṁ kāresi, matthake`
- `ñatvā mahāsatto attano yodhānaṁ tīṇi satāni pesesi “tumhe jaṅghaumaṅgena gantvā rañño mātarañca aggamahesiñca puttañca dhītarañca`

*missing from render (chunk)*

- `athassa mātāpitaro bhijjamānahadayā viya manusse paṭikkamāpetvā taṁ tato aggisantāpanato apanetvā tāta temiyakumāra mayaṁ tava apīṭhasappiādibhāvaṁ jā`
- `mittānanti buddhādīnaṁ kalyāṇamittānaṁ na dubbhati sabbattha pūjito hotī ti idaṁ sīvalivatthunā vaṇṇetabbaṁ`
- `sunando sārathi ettakāhi gāthāhi dhammaṁ desentampi taṁ asañjānitvā ko nu kho ayan ti āvāṭakhaṇanaṁ pahāya rathasamīpaṁ gantvā tattha tañca pasādhanab`
- `antonidhīti rājagehe mahādvārassa antoummārā nidhiṁ nīharāpesi`
- `puna sīvalidevī ekaṁ upāyaṁ cintetvā gāmaghātaraṭṭhavilumpanākāraṁ viya dassethā ti amacce āṇāpesi`
- `athassa etadahosi ayaṁ mahājano nivattituṁ na icchati`
- `mahājano lekhasāmikehi lekhā bhinnā ti vatvā deviyā gatamaggeneva gato`
- `tattha salomahaṭṭhoti bhikkhave so nimirājā obhāsaṁ disvā ākāsaṁ olokento taṁ dibbābharaṇapaṭimaṇḍitaṁ disvāva bhayena lomahaṭṭho hutvā devatā nu si g`

*rendered but not contiguous in PDF*

- `ord24 [verse] @26/62: mittānanti buddhādīnaṁ kalyāṇamittānaṁ na dubbhati pajjalatīti issariyaparivārena pajjalati siriyā ajahito hotīti ettha`
- `ord252 [verse] @58/88: puna sīvalidevī ekaṁ upāyaṁ cintetvā viya sarīre lākhārasaṁ siñcitvā laddhappahāre viya phalake`
- `ord255 [verse] @34/49: mahājano rājānaṁ anubandhiyeva athassa etadahosi piṭṭhiṁ datvā gacchantaṁ disvā sokaṁ sandhāretuṁ asakkontī`
- `ord433 [verse] @28/42: dibbābharaṇapaṭimaṇḍitaṁ disvāva bhayena lomahaṭṭho hutvā devattaṁ upapajjati aṭṭhasamāpattinibbattanaṁ pana uttamaṁ nāma tena`
- `ord617 [before] @8/9: santikaṁ gantvā mahārāja paṇḍitena evaṁ ratha`
- `ord617 [before] @1/9: aḍḍo suvinicchito sakkopi tena parājito kasmā purisavisesaṁ na`
- `ord617 [before] @8/9: koṭṭāpetvā na aggināti pakatiaggiṁ pahāya araṇi`
- `ord617 [before] @1/8: aggiṁ gāhāpetvā na dārūhīti paṇṇāni gāhāpetvā ambilodanaṁ pacāpetvā`

### 42KhuA23 (commentary)

*missing from render (line)*

- `Ṭhitacittamupādhiyoti lokadhammehi avikampanabhāvena suṭṭhu ṭhitaekaggabhāvappattacittasaṅkhātena upādhinā uttarattharaṇena vā rājāsanena`

*missing from render (chunk)*

- `bhūridattassa bhariyāyo pana taṁ vammikamatthake adisvā mātunivesane vasissatī ti abyāvaṭā ahesuṁ`
- `atha naṁ te brāhmaṇānañca brāhmaṇadevatāya ca sakkāraṁ karohī ti vatvā kā brāhmaṇadevatā ti vutte aggidevoti taṁ navanītasappinā santappehī ti āhaṁsu`
- `so ajānanto itarassa kalyāṇakammassa balena kumbhadāsiyā kucchimhi nibbattosmī ti saññāya evamāha`
- `ṭhitacittamupādhiyoti lokadhammehi avikampanabhāvena suṭṭhu ṭhitaekaggabhāvappattacittasaṅkhātena upādhinā uttarattharaṇena vā rājāsanena samannāgato`
- `tattha yaṁ paṇḍitotye keti so kira hadayaṁ paṇḍitassā ti sutvā cintesi yaṁ eke paṇḍitoti vadanti`
- `evaṁ tumhe raññā puṭṭhā amhākaṁ pitā imañcimañca ovādaṁ adāsī ti katheyyātha`
- `mā rodhayīti mittadubbhikammaṁ karomī ti mā bhāyi`
- `bhikkhave tato vessantaro rājā ñātake āha tumhe āmantetvā mayaṁ gacchāma`

*rendered but not contiguous in PDF*

- `ord77 [verse] @41/49: bhariyāyo pana taṁ vammikamatthake adisvā paridevamānā tassā pādamūle patiṁsu tamatthaṁ pakāsento satthā`
- `ord133 [verse] @57/61: vatvā kā brāhmaṇadevatā ti vutte aparampi kāraṇaṁ dassento gāthamāha`
- `ord422 [verse] @20/113: vikopetuṁ na sakkā jīveti jīvo caranti chindituṁ na sakkonti sira mādāyāti paresaṁ`
- `ord438 [verse] @117/144: attabhāve vipākaṁ adāsi so ajānanto kāraṇenāhaṁ niratthakaṁ sīlanti maññāmi kalimevāti yathā asippo`
- `ord577 [verse] @22/59: kathesi tamatthaṁ pakāsento satthā āha nikkhamma himavantappadese samuddatīre ṭhitaṁ saṭṭhiyojanubbedhaṁ ekagghanaṁ kāḷapabbata`
- `ord590 [verse] @31/33: hadayaṁ paṇḍitassā ti sutvā cintesi nāgarājā āha`
- `ord700 [verse] @93/128: anusāsi evaṁ tumhe raññā puṭṭhā jarasiṅgālo deva kathaṁ samāsano bhaveyya yathā siṅgālo`
- `ord866 [verse] @31/33: vīmaṁsanavasena iti abravi mā rodhayīti nāgarājā āha`

### 43KhuA24 (commentary)

*missing from render (line)*

- `Ye ca kho tvaṁ Gotami dhamme jāneyyāsi “ime dhammā viarāgāya saṁvattanti, no sarāgāya -pa- subharatāya saṁvattanti, no`
- `Idāni nesaṁ dubbalakāraṇaṁ dassento “mūlampi imesaṁ dubbalan”tiādimāha. tattha mūlampīti patiṭṭhaṭṭhena mūlabhūtampi. Assāsapassāsānaṁ.`
- `Cātumahārājikānaṁ devānanti Dhataraṭṭhavirūḷhakavirūpakkhakuverasaṅkhātā catumahārājā issarā etesanti Cātumahārājikā. Rūpādīhi dibbanti`

*missing from render (chunk)*

- `ye ca kho tvaṁ gotami dhamme jāneyyāsi ime dhammā viarāgāya saṁvattanti`
- `idāni nesaṁ dubbalakāraṇaṁ dassento mūlampi imesaṁ dubbalan tiādimāha`
- `cātumahārājikānaṁ devānanti dhataraṭṭhavirūḷhakavirūpakkhakuverasaṅkhātā catumahārājā issarā etesanti cātumahārājikā`
- `tattha paṭhamagāthāya yassūbhayanteti pubbe vutte phassādibhede`

*rendered but not contiguous in PDF*

- `ord13 [before] @9/10: gotami dhamme jāneyyāsi ime dhammā vi`
- `ord13 [before] @0/7: arāgāya saṁvattanti no sarāgāya subharatāya saṁvattanti no`
- `ord13 [before] @7/8: dubbalakāraṇaṁ dassento mūlampi imesaṁ dubbalan ti`
- `ord13 [before] @0/6: ādimāha tattha mūlampīti patiṭṭhaṭṭhena mūlabhūtampi assāsapassāsānaṁ`
- `ord13 [before] @2/3: cātumahārājikānaṁ devānanti dhataraṭṭhavirūḷhakavirūpakkhakuvera`
- `ord13 [before] @1/7: saṅkhātā catumahārājā issarā etesanti cātumahārājikā rūpādīhi dibbanti`

### 48AbhiA01 (commentary)

*missing from render (line)*

- `Abhidhammaṁ patvā pana suttantabhājanīyaabhidhammabhājanīyapañhapucchakanayānaṁ vasena nippadesato vibhattā.`
- `Tattha Khandhavibhaṅgo suttantabhājanīyaabhidhammabhājanīyapañhapucchakānaṁ vasena tidhā vibhatto. So.`
- `Satipaṭṭhānavibhaṅgo atirekabhāṇavāramatto. Tathā sammappadhānaiddhipādabojjhaṅgamaggaṅgavibhaṅgā. Jhānavibhaṅgo dvibhāṇavāramatto.`
- `pavattitadesanā vegena pavattā ākāsagaṅgā viya, adhomukhaṭhapitaudakaghaṭā nikkhanta-udakadhārā viya ca hutvā anantā aparimāṇā ahosi.`
- `sampattaparisāya dhammaṁ desentānaṁ desanā Saṁyuttaaṅguttarikadvemahānikāyappamāṇāva hoti. Kasmā? Buddhānañhi`
- `abhidhammadesanāpariyosānañca tesaṁ bhikkhunaṁ sattappakaraṇauggahaṇañca ekappahāreneva ahosi.`
- `suttasaṅgaho Saṁyuttanikāyo, Cittapariyādānasuttādinavasuttasahassapañcasatasattapaññāsasuttasaṅgaho Aṅguttaranikāyo, Khuddakapāṭhadhammapada-udānaiti`
- `Vividhā hi ettha pañcavidhapātimokkhuddesapārājikādisattaāpattikkhandhamātikāvibhaṅgādippabhedā nayā, visesabhūtā ca`

*missing from render (chunk)*

- `abhidhammaṁ patvā pana suttantabhājanīyaabhidhammabhājanīyapañhapucchakanayānaṁ vasena nippadesato vibhattā`
- `tattha khandhavibhaṅgo suttantabhājanīyaabhidhammabhājanīyapañhapucchakānaṁ vasena tidhā vibhatto`
- `adhomukhaṭhapitaudakaghaṭā nikkhantaudakadhārā viya ca hutvā anantā aparimāṇā ahosi`
- `pacchābhattaṁ pana sampattaparisāya dhammaṁ desentānaṁ desanā saṁyuttaaṅguttarikadvemahānikāyappamāṇāva hoti`
- `khuddakapāṭhadhammapadaudānaitivuttakasuttanipātavimānavatthupetavatthutheragāthātherīgāthājātakaniddesapaṭisambhidāapadānabuddhavaṁsacariyāpiṭakavase`
- `vividhā hi ettha pañcavidhapātimokkhuddesapārājikādisattaāpattikkhandhamātikāvibhaṅgādippabhedā nayā`
- `brāhmaṇagāmaambavananāgavanādīnaṁ brāhmaṇagāmādibhāvo viyāti dvāravavatthānaṁ yujjati`
- `evaṁ sattaaṭṭhādīnaṁ aṅgānaṁ pariṇāmo veditabboti attho`

*rendered but not contiguous in PDF*

- `ord22 [before] @3/4: abhidhammaṁ patvā pana suttantabhājanīya`
- `ord22 [before] @0/4: abhidhammabhājanīyapañhapucchakanayānaṁ vasena nippadesato vibhattā`
- `ord22 [before] @2/3: tattha khandhavibhaṅgo suttantabhājanīya`
- `ord22 [before] @0/5: abhidhammabhājanīyapañhapucchakānaṁ vasena tidhā vibhatto so`
- `ord22 [before] @3/4: satipaṭṭhānavibhaṅgo atirekabhāṇavāramatto tathā sammappadhāna`
- `ord22 [before] @0/3: iddhipādabojjhaṅgamaggaṅgavibhaṅgā jhānavibhaṅgo dvibhāṇavāramatto`
- `ord22 [before] @5/6: pavattitadesanā vegena pavattā ākāsagaṅgā viya adhomukhaṭhapita`
- `ord22 [before] @0/8: udakaghaṭā nikkhantaudakadhārā viya ca hutvā anantā aparimāṇā`

### 49AbhiA02 (commentary)

*missing from render (line)*

- `Paccayasamuṭṭhānānipi “kammajaṁ kammapaccayaṁ kammapaccayautusamuṭṭhānan”ti-ādinā nayena heṭṭhā1 kathitāniyeva. Pañcapi pana`
- `tesaṁ viseso? Khandhā tāva avisesato vuttā, upādānakkhandhā sāsavaupādāniyabhāvena visesetvā. Yath’āha–.`
- `Apuññābhisaṅkhāraniddese akusalā cetanāti dvādasaakusalacittasampayuttā cetanā. Kāmāvacarāti kiñcāpi tattha ṭhapetvā dve`
- `ārammaṇapaccayena, garuṁ katvā assādanakāle ārammaṇādhipatiārammaṇūpanissayehi, avijjāsammūḷhassa anādīnavadassāvino`
- `akusalaṁ karontassa hetusahajāta-aññamaññanissayasampayutta-atthiavigatapaccayehīti anekadhā paccayo hoti.`
- `sampayuttadhammasādhāraṇehi sahajāta-aññamaññanissayasampayuttaatthi-avigatapaccayehi chahi hetupaccayena cāti sattadhā paccayo. Tattha`
- `yasmā parato hetucatukkādīni1 tīṇi catukkāni avigatasampayuttaaññamaññapaccayavasena vuttāni, tasmā idha tāni apanetvā avasesānaṁ`
- `aṅgapaccaṅgavinimutta-ekadhammānupassī, nāpi kesalomādivinimuttaitthipurisānupassī. Yopi cettha kesalomādiko bhūtupādāya-samūhasaṅkhāto`

*missing from render (chunk)*

- `paccayasamuṭṭhānānipi kammajaṁ kammapaccayaṁ kammapaccayautusamuṭṭhānan tiādinā nayena heṭṭhā kathitāniyeva`
- `apuññābhisaṅkhāraniddese akusalā cetanāti dvādasaakusalacittasampayuttā cetanā`
- `garuṁ katvā assādanakāle ārammaṇādhipatiārammaṇūpanissayehi`
- `yaṁkiñci akusalaṁ karontassa hetusahajātaaññamaññanissayasampayuttaatthiavigatapaccayehīti anekadhā paccayo hoti`
- `yaṁ yathā paccayo yassāti ettha pana saṅkhārassa avijjā sampayuttadhammasādhāraṇehi sahajātaaññamaññanissayasampayuttaatthiavigatapaccayehi chahi hetu`
- `tattha yasmā parato hetucatukkādīni tīṇi catukkāni avigatasampayuttaaññamaññapaccayavasena vuttāni`
- `atha vā yvāyaṁ mahāsatipaṭṭhāne idha bhikkhave bhikkhu araññagato vā so satova assasatī tiādinā nayena assāsapassāsādicuṇṇakajātaaṭṭhikapariyosāno kāy`
- `api ca aniccādisattaanupassanāvasenapi anupassitabbā`

*rendered but not contiguous in PDF*

- `ord15 [before] @3/4: paccayasamuṭṭhānānipi kammajaṁ kammapaccayaṁ kammapaccaya`
- `ord15 [before] @0/7: utusamuṭṭhānan tiādinā nayena heṭṭhā kathitāniyeva pañcapi pana`
- `ord15 [before] @7/8: khandhā tāva avisesato vuttā upādānakkhandhā sāsava`
- `ord15 [before] @0/4: upādāniyabhāvena visesetvā yath āha`
- `ord60 [before] @3/4: apuññābhisaṅkhāraniddese akusalā cetanāti dvādasa`
- `ord60 [before] @0/7: akusalacittasampayuttā cetanā kāmāvacarāti kiñcāpi tattha ṭhapetvā dve`
- `ord60 [before] @4/5: ārammaṇapaccayena garuṁ katvā assādanakāle ārammaṇādhipati`
- `ord60 [before] @0/3: ārammaṇūpanissayehi avijjāsammūḷhassa anādīnavadassāvino`

*rendered more often than printed*

- `3x vs 0x: manasikārabahulīkāro ayamāhāro anuppannassa vā`
- `2x vs 1x: sambojjhaṅgassa bhiyyobhāvāya vepullāya bhāvanāya pāripūriyā`

### 50AbhiA03 (commentary)

*missing from render (line)*

- `vīsatidhā paccayo hoti. Chando hetupurejātakamma-āhāraindriyajhānamaggapaccayo na hoti, sesānaṁ sattarasannaṁ paccayānaṁ`
- `adhipatipaccaye vuttanayeneva paccayā honti. Phasso hetupurejātakammaindriyajhānamaggapaccayo na hoti, sesānaṁ aṭṭhārasannaṁ vasena paccayo`
- `pana soḷasannaṁ paccayānaṁ vasena paccayā honti. Vicikicchāissāmacchariyakukkuccāni tato adhipatipaccayaṁ apanetvā pannarasadhā.`
- `natthi. Nissayapaccaye cakkhāyatanādīni ārammaṇaārammaṇādhipatinissaya-upanissayapurejāta-indriyavippayutta-atthiavigatavasena navadhā paccayā honti. `
- `Purejātapaccaye rūpa sadda gandha rasāyatanāni ārammaṇaārammaṇādhipati-upanissayapurejāta-atthi-avigatavasena chadhā paccayā`
- `Āhārapaccaye kabaḷīkārāhāro ārammaṇa-ārammaṇādhipati-upanissayaāhāra-atthi-avigatavasena chadhā paccayo hoti. Indriyādīsu apubbaṁ natthi.`
- `rūpadhammānaṁ ārammaṇapaccayabhāve sati ārammaṇādhipatiārammaṇūpanissayamattaññeva`
- `adhipatipaccayo adhipatipaccayattaṁ avijahantova sahajātaaññamaññanissayavipākasampayuttavippayutta-atthi-avigatānaṁ vasena`

*missing from render (chunk)*

- `chando hetupurejātakammaāhāraindriyajhānamaggapaccayo na hoti`
- `phasso hetupurejātakammaindriyajhānamaggapaccayo na hoti`
- `vicikicchāissāmacchariyakukkuccāni tato adhipatipaccayaṁ apanetvā pannarasadhā`
- `nissayapaccaye cakkhāyatanādīni ārammaṇaārammaṇādhipatinissayaupanissayapurejātaindriyavippayuttaatthiavigatavasena navadhā paccayā honti`
- `purejātapaccaye rūpa sadda gandha rasāyatanāni ārammaṇaārammaṇādhipatiupanissayapurejātaatthiavigatavasena chadhā paccayā honti`
- `āhārapaccaye kabaḷīkārāhāro ārammaṇaārammaṇādhipatiupanissayaāhāraatthiavigatavasena chadhā paccayo hoti`
- `adhipatipaccayo adhipatipaccayattaṁ avijahantova sahajātaaññamaññanissayavipākasampayuttavippayuttaatthiavigatānaṁ vasena aparehipi aṭṭhahākārehi anek`
- `nissayapaccayo nissayapaccayattaṁ avijahantova catuvīsatiyā paccayesu attano nissayapaccayattañceva anantarasamanantarapacchājātaāsevananatthivigatapa`

*rendered but not contiguous in PDF*

- `ord716 [before] @4/5: vīsatidhā paccayo hoti chando hetupurejātakammaāhāra`
- `ord716 [before] @0/6: indriyajhānamaggapaccayo na hoti sesānaṁ sattarasannaṁ paccayānaṁ`
- `ord716 [before] @5/6: adhipatipaccaye vuttanayeneva paccayā honti phasso hetupurejātakamma`
- `ord716 [before] @0/7: indriyajhānamaggapaccayo na hoti sesānaṁ aṭṭhārasannaṁ vasena paccayo`
- `ord716 [before] @6/7: soḷasannaṁ paccayānaṁ vasena paccayā honti vicikicchā`
- `ord716 [before] @1/5: issāmacchariyakukkuccāni tato adhipatipaccayaṁ apanetvā pannarasadhā`
- `ord716 [before] @3/4: natthi nissayapaccaye cakkhāyatanādīni ārammaṇa`
- `ord716 [before] @0/1: ārammaṇādhipatinissayaupanissayapurejātaindriyavippayuttaatthi`

### 51Vism01 (commentary)

*missing from render (line)*

- `Pāpicchasseva pana sato uttarimanussadhammādhigamaparidīpanavācāya tathā tathā vimhāpanaṁ sāmantajappanasaṅkhātaṁ Kuhanavatthūti`
- `Kathaṁ Sammāsambuddhato? Yopi so Bhagavā asītianubyañjanapaṭimaṇḍitadvattiṁsamahāpurisalakkhaṇavicitrarūpakāyo`

*missing from render (chunk)*

- `pāpicchasseva pana sato uttarimanussadhammādhigamaparidīpanavācāya tathā tathā vimhāpanaṁ sāmantajappanasaṅkhātaṁ kuhanavatthūti veditabbaṁ`
- `yopi so bhagavā asītianubyañjanapaṭimaṇḍitadvattiṁsamahāpurisalakkhaṇavicitrarūpakāyo sabbākāraparisuddhasīlakkhandhādiguṇaratanasamiddhadhammakāyo ya`

*rendered but not contiguous in PDF*

- `ord16 [after] @187/188: kuhanavatthū ti pāpicchasseva pana sato uttarimanussadhammādhigamaparidīpana`
- `ord16 [after] @1/8: vācāya tathā tathā vimhāpanaṁ sāmantajappanasaṅkhātaṁ kuhanavatthūti veditabbaṁ yathāha`
- `ord170 [after] @26/27: kathaṁ sammāsambuddhato yopi so bhagavā asīti`
- `ord170 [after] @0/19: anubyañjanapaṭimaṇḍitadvattiṁsamahāpurisalakkhaṇavicitrarūpakāyo sabbākāraparisuddhasīlakkhandhādiguṇaratanasamiddhadhammakāyo y`

### 52Vism02 (commentary)

*missing from render (chunk)*

- `evaṁ bhayato upaṭṭhāne panassa ayaṁ pāḷi aniccato manasikaroto kiṁ bhayato upaṭṭhāti`
- `vuttaṁ hetaṁ aniccato manasikaroto saddhindriyaṁ adhimattaṁ hoti`
- `yaṁ sandhāya vuttaṁ kathaṁ bahiddhā vuṭṭhānavivaṭṭane paññā gotrabhuñāṇaṁ`
