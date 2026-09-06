# The dictionary manifests carried 1.1 MB the panel never read

**2026-09-06.** The item `perf_search.js` named when its ceiling dropped to 520 KB: the
lookup rows' largest file was `lookup_eval/index.json`, 653 KB raw, 129 KB gz, fetched
before the first dictionary lookup of a visit.

## Measured

`shards: {set: {name: {keys: N, bytes: N}}}` was 563 KB of the 653. `panel.js` resolves a
shard by walking `m[name]` for deepening prefixes — `shardName`, `eShardName`, `hwlook` —
and reads nothing else from an entry. The counts are the builder's self-report. The same
shape in `lookup/index.json` (375 KB) and `lookup_eval/hw/index.json` (272 KB).

## Gate red first

`perf_search.js` had given the lookup rows their own 700 KB ceiling for a few hours, with
the reason written beside it. That exception is gone: one ceiling, 520 KB, every row. Red on
`bf930a3f6108`: two lookup rows, max 0.65 MB (`perf_search_red_run_2026-09-06_manifests.txt`).

## Then

`pipeline/slim_store_manifests.py`: for each of the three manifests, the per-shard entries
move to `index.diag.json` beside it (tracked, uploaded, fetched by nothing) and `shards`
becomes `{set: {name: 1}}`; every other key byte-equal; verified that the shard names per set
are identical, and that the diag file merged back reproduces the original. Idempotent, and
refuses to run on a slim manifest whose diag is missing.

| manifest | before | after | gz before → after |
|---|---:|---:|---:|
| `lookup/index.json` | 375 KB | 65 KB | |
| `lookup_eval/index.json` | 653 KB | 177 KB | 129 → 44 KB |
| `lookup_eval/hw/index.json` | 272 KB | 73 KB | |

`check_lookup_reach` 12/12, `check_hw_reach` green, `check_apd_gear` green — every word
still reaches its shard. `perf_search`: cold lookup 1.46 → 0.67 MB raw, 0.31 → 0.18 gz,
waves 6 → 5; baseline re-recorded. `WLV` → `20260906a`, `panel.js?v=20260906a`.

## Owed to the host

The store is on R2: `pipeline/r2_upload.sh` first (rclone copies only what changed: three
manifests and three diag files), then `git push`. Shard names being identical, an old
manifest against the new bucket or the reverse resolves every key the same — the order is
safe, the bump only stops a returning reader keeping the fat manifest for a year.
