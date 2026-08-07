# Setting up the R2 bucket — the checklist

**Written 2026-08-07.** This is steps 1–3 of `docs/DEPLOY_SCALE.md` §6a, written out as
things to do rather than as a decision. **Nothing in this checklist moves, deletes or
rewrites a file in the repository.** At the end of it the stores are still at
`site/lookup/` and `site/lookup_eval/` and GitHub Pages is still publishing them exactly as
it does today. The relocation is step 4 and it is gated on step 8 below being green.

Cloudflare's own pages, checked on 2026-08-07, are linked at the foot.

---

## Step 0 — the prerequisite that decides whether any of this works

**The domain must already be a zone in the same Cloudflare account as the bucket.** That is
Cloudflare's rule, not ours, and it is the one thing that can stop this at the first move.

Log in at `dash.cloudflare.com` and look at the **Websites** list.

- **`buddha-dhamma.net` is there** → carry on to step 1.
- **It is not there** → the domain is managed elsewhere and must be added first, either by
  moving its nameservers to Cloudflare or by a **partial (CNAME) setup**. That is a change
  to the DNS of the live site, so it is a decision, not a step. **Stop and say so** rather
  than working around it.

*Not verified here: the sandbox has no DNS resolution, so which of the two is true was not
established. `site/DEPLOY.md` documents a Cloudflare Pages route and `site/CNAME` binds the
domain to GitHub Pages, so the account may well already exist — but "may well" is not
"does", and this is the check that costs one minute and saves an afternoon.*

---

## Step 1 — create the bucket

R2 → **Create bucket**. Name it **`osbct-dict`**. Location: automatic is fine.

*(If you choose a different name, set `OSBCT_R2_BUCKET` when running the upload script.)*

---

## Step 2 — create the API token, for rclone

R2 → **Manage R2 API Tokens** → **Create API token**.

- Permission: **Object Read & Write**
- Scope it to the `osbct-dict` bucket only.

Copy the **Access Key ID**, the **Secret Access Key**, and your **Account ID** (shown on the
R2 overview page). **The secret is shown once.** Put it in your password manager, not in a
file in this repository — nothing in this project should ever contain it.

---

## Step 3 — configure rclone

Install rclone (`brew install rclone`). **v1.59 or later** — earlier versions return
`HTTP 401` against R2 because they do not follow the S3 spec closely enough.

```
rclone config
```

- `n` for a new remote
- name: **`osbct-r2`**  ← the script expects this name
- storage type: **Amazon S3 Compliant Storage Providers**
- provider: **Cloudflare R2**
- credentials: enter them manually; paste the Access Key ID and Secret Access Key
- region: leave blank
- endpoint: **`https://<ACCOUNT_ID>.r2.cloudflarestorage.com`**

**If the token is scoped to one bucket** (step 2), add `no_check_bucket = true` to that
remote in `rclone config file`, or rclone errors when it tries to check the bucket exists.

Writing the file directly is less error-prone than the wizard, because the wizard never
asks about `no_check_bucket` and the menu numbers move between rclone versions.
`rclone config file` prints the path; the remote is:

```
[osbct-r2]
type = s3
provider = Cloudflare
access_key_id = <ACCESS KEY ID>
secret_access_key = <SECRET ACCESS KEY>
endpoint = https://<ACCOUNT_ID>.r2.cloudflarestorage.com
acl = private
no_check_bucket = true
```

### Verify with a round trip, not with a bucket listing

**CORRECTED 2026-08-07, having first been written wrong here.** This step said to check the
remote with `rclone tree osbct-r2:`. **That fails on a correctly-scoped token**, because
listing *buckets* is an account-level operation and the token in step 2 grants object
access to one bucket. The failure looks like a credentials problem and is not one — which
is exactly the sort of wrong diagnosis this project has lost afternoons to.

`rclone ls osbct-r2:osbct-dict` is no better on its own: the bucket is empty at this point,
so success and silent failure both print nothing. **Prove it with a round trip**, which
exercises write, list, read and delete and leaves the bucket clean:

```
echo "osbct r2 test $(date)" > /tmp/r2test.txt
rclone copy /tmp/r2test.txt osbct-r2:osbct-dict/
rclone ls   osbct-r2:osbct-dict          # expect: one line, r2test.txt
rclone cat  osbct-r2:osbct-dict/r2test.txt   # expect: the line you wrote
rclone delete osbct-r2:osbct-dict/r2test.txt
rclone ls   osbct-r2:osbct-dict          # expect: nothing
```

---

## Step 4 — upload the stores

From the repository root:

```
bash pipeline/r2_upload.sh
```

It uploads `site/lookup/` and `site/lookup_eval/` — 24,599 files, about 360 MB — in three
passes, because the content type differs per kind and rclone applies `--header-upload` to
everything it touches in one run. It ends by comparing the object count in the bucket
against `git ls-files` and **says so loudly if they disagree**.

Expect it to take a while: it is 24,599 small objects, not 360 MB of one file.

**Cost, so it is not a surprise:** R2's free tier is 10 GB stored, 1 million Class A
(write) operations and 10 million Class B (read) operations per month. This upload is
~0.36 GB and ~24,600 writes. Egress from R2 is free. Re-running to update a dictionary
only sends what changed, because the script uses `--checksum`.

---

## Step 5 — connect the custom domain

Bucket → **Settings** → **Custom Domains** → **Add** → `dict.buddha-dhamma.net` →
**Continue** → review the DNS record → **Connect Domain**.

Status goes **Initializing** → **Active** in a few minutes. If it stays put, use the `...`
menu → **Retry connection**.

**Do not use the `r2.dev` development URL instead.** It is rate-limited, Cloudflare
documents it as non-production, and caching, WAF and access controls do not work through
it. Do not point a CNAME at it either — Cloudflare calls that an unsupported access path.

---

## Step 6 — apply the CORS policy

`dict.buddha-dhamma.net` is a **different origin** from `buddha-dhamma.net`. Without this,
every dictionary fetch fails in the browser and the panel is silently empty — while `curl`
and any command-line test look perfectly healthy. That asymmetry is why the gate in step 8
sends an `Origin` header.

Bucket → **Settings** → **CORS Policy** → **Add CORS policy** → **JSON** tab → paste the
contents of **`pipeline/r2_cors.json`** → **Save**.

Use the dashboard, not `wrangler r2 bucket cors set`. **The two take different schemas** —
the dashboard takes the S3-style array (`AllowedOrigins`, `AllowedMethods`, …) which is
what `pipeline/r2_cors.json` contains; Wrangler takes a `{"rules":[{"allowed":{…}}]}` shape
and would reject that file.

Rule propagation can take up to 30 seconds. And **if you ever change this policy later,
purge the cache for the hostname** — Cloudflare will keep serving already-cached objects
without the new CORS headers otherwise.

---

## Step 7 — point the panel at the bucket

`site/reader/panel.js:541-542`. Two lines:

```js
var BASE  = '../lookup/';
var EBASE = '../lookup_eval/';
```

become

```js
var BASE  = 'https://dict.buddha-dhamma.net/lookup/';
var EBASE = 'https://dict.buddha-dhamma.net/lookup_eval/';
```

**This is the whole switch, and reverting is editing it back.** Every file is still exactly
where it was.

---

## Step 8 — run the gate. This is the step that decides.

```
node pipeline/check_r2_origin.js https://dict.buddha-dhamma.net
```

Every line must be green. It compares each probe **byte for byte** against the file in the
repository — an HTTP 200 carrying the wrong bytes is precisely what it exists to catch —
and it runs three negative controls each time so that a pass means something.

What it is looking for, and why each one is a real risk rather than a formality:

| probe | the risk |
|---|---|
| `gzip branch` | `jfetch` sniffs magic bytes because a `.gz` arrives either opaque or already inflated, and **which one is the host's choice**. `python3 -m http.server` never sets `Content-Encoding`, so every other gate we have is blind to one branch |
| `NON-ASCII` | **164 shard filenames** carry `’ ‘ “ ” ° √` |
| `SPACE` | **458 contain a space** — the larger group, and the one that hides, because a space is printable ASCII |
| `CORS` | step 6, from the browser's point of view rather than curl's |
| negative controls | a missing shard must 404; both comparators must detect a mutation |

**Green** → tell me, and step 4 of §6a follows: the relocation out of `site/`, which is
what actually drops the Pages deploy from 26,576 files to about 2,000.

**Red** → nothing has been risked. Revert step 7's two lines and send me the output.

---

## Sources

- [Public buckets and custom domains](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [Configure CORS](https://developers.cloudflare.com/r2/buckets/cors/)
- [rclone with R2](https://developers.cloudflare.com/r2/examples/rclone/)
