# Paragraph numbers are not a key (RECONSTRUCTION — see README.md)

Tested 2026-08-02.  The paragraph numbers printed in the edition were
reported to be shared across Tipiṭaka, Aṭṭhakathā and Ṭīkā, which would have
made them the join key for cross-referencing.  THEY ARE NOT.

Only 28 of 118 volumes carry a non-decreasing paragraph-number series; 90
RESTART, because a commentary volume covers several nipātas and the
numbering begins again with each.  `19AnA03` holds two paragraphs numbered
113; `21Khu04` holds 4,347 duplicate numbers among 4,858 numbered
paragraphs.

Building the cross-layer links on the number put 40.3% of canon→commentary
links on the wrong sutta.  The repair anchors the number match INSIDE the
section whose NAME matches — see `links_repaired_by_name.md` and
`pipeline/check_links.py`, the ratchet that keeps it from regressing.
