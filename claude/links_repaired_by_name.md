# Links repaired by name (RECONSTRUCTION — see README.md)

The consequence of `paragraph_numbers_are_not_a_key.md`: a bare paragraph
number is an ADDRESS only within a section, never across a volume.  The
placer therefore matches a canon paragraph's number inside the commentary
section whose NAME matches the canon section's name, and only there.

The vagga REGION boundaries this depends on are those of the section heads
in `sections/<VOL>.json` — which is why misclassified vagga heads
(`fix_vagga_heads.py`; the test is the name, not the typography) were a
links defect and not merely a styling one: an over-wide region lets a bare
number match wherever it likes.

`pipeline/check_links.py` records the baseline (n-match, name-match,
reachable) and refuses regression in any measure.
