# Commands to run on the host — 2026-08-23

Run from the repository root, in order. **This is not a release** — no version
bump, no tag, no Zenodo deposit. It is a content change under `site/`, so it
needs a stamp (already done), a push and a Pages run, and nothing else.

**The R2 sync is NOT needed.** Nothing under `stores/` changed. The `hw/` store
owed since 08-10 was verified this session as already on the bucket.

---

## 1. Delete what the sandbox could not

```bash
cd ~/Documents/OSBCT

# the zero-byte git lock the sandbox leaves behind (push.sh also does this)
rm -f .git/index.lock

# the forward link map as it was before the 437 moves — keep it until you have
# read the diff, then remove
rm -f site/reader/linksk/19Khu02.links.json.prerequote

# printed pages I rendered to verify against; the sandbox cannot unlink them
rm -rf "$(ls -d ~/Library/Application\ Support/Claude/local-agent-mode-sessions/*/*/*/outputs/pg 2>/dev/null)"
```

## 2. Look at the diff before committing

The link maps are one line per volume, so `git diff` will report "1 insertion,
1 deletion" for 437 moves and show you nothing readable. **Read it by parsing,
not by diffing:**

```bash
python3 - <<'EOF'
import json, subprocess
old = json.loads(subprocess.run(
    ['git','show','HEAD:site/reader/linksk/19Khu02.links.json'],
    capture_output=True, text=True).stdout)
new = json.load(open('site/reader/linksk/19Khu02.links.json', encoding='utf-8'))
d = [k for k in set(old) | set(new) if old.get(k) != new.get(k)]
print('records differing:', len(d))          # expect 437
for k in sorted(d, key=int)[:5]:
    print(k, new[k]['commentary'][-1])        # each carries by/was provenance
EOF
```

Every moved record says how it got there:

    {"key": "27KhuA08#511", "state": "direct", "n": 333,
     "by": "requotation", "was": "27KhuA08#467"}

And the gate that was red before the move must now be green:

```bash
python3 pipeline/check_links.py                    # both named cases ok
python3 pipeline/check_links.py --negative-control # must fire
python3 pipeline/check_concordance.py
```

## 3. Commit and push

`COMMIT_MSG.bak` carries the message. `push.sh` re-checks the stale lock, the
stale message and the forgotten stamp, then prompts before committing.

```bash
./push.sh
```

The stamp is already written — build **`8a89a13c6b74`** (was `c97a3f99fdb2`).

## 4. Fresh Pages run

GitHub → Actions → **Run workflow**. Never "Re-run failed jobs".
Then hard-reload the reader (Cmd-Shift-R).

```bash
# and check what is LIVE with a cache-buster, or you are measuring the past —
# this has now given a false "the deploy failed" three times
curl -s "https://buddha-dhamma.net/build.json?cb=$RANDOM" ; echo
```

Expect `8a89a13c6b74`.

## 5. Then look at it as a reader

Open `19Khu02` ¶333 with the Aṭṭhakathā band on. It should show
`333. Tattha vatthuttamadāyikāti vatthānaṁ uttamaṁ seṭṭhaṁ …` — the comment,
printed page 133 — and not the verse you have just finished reading.

Worth a look too: ¶349, ¶357, ¶365. Those are among the 470 the edition quotes
and never comments on, so they still reach the reprint. That is the edition's
silence and it was left alone deliberately — but seeing it in the reader is the
way to decide whether it should be *said* rather than merely left.

---

## The ordering rule, for the next actual release

**CUT THE TAG LAST.** Every metadata file must be committed and pushed before
the tag exists, or Zenodo mints a deposit describing the previous release. This
project has broken that rule three times. The v2.7.1 sequence — checklist files,
commit, push, Pages, R2, *then* tag, then the GitHub Release, then read the DOI
from the record — is in git history at `RUN_ON_HOST.md` before this revision.

`v2.7.0` is a lightweight tag where v2.4.0–v2.6.0 are annotated. It has a DOI.
**Leave it**; recorded so nobody rediscovers it as a defect.
