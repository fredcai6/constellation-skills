# Issue-set manifest schema and adapter contract

The manifest is the tracker-agnostic issue set — one JSON file, the single
source of truth for a cut. It is evidence, never a review gate.

## Manifest fields

Top level:

- `epic` (object, required)
  - `title` (string, required) — non-empty.
  - `spec_path` (string) — the confirmed `DESIGN_SPEC.md` this set was cut from.
    Also feeds the epic's deterministic idempotency key.
  - `body` (string) — one-paragraph intent; the filer appends the wave-ordered
    task list beneath it.
- `issues` (array, required, non-empty) — each an object:
  - `id` (string, required) — unique within the set; the edge and receipt key.
  - `title` (string, required) — non-empty.
  - `body` (string) — what to build, acceptance, out-of-scope.
  - `type` (string, required) — `AFK` (an agent can run it unattended) or
    `HITL` (a human decision is required). No other value.
  - `hitl_reason` (string) — required and non-empty whenever `type` is `HITL`;
    it names why a human decision is needed.
  - `blocks` (array of ids) — this issue must land before each named issue.
    Every target must name a known issue id.
  - `labels` (array of strings) — optional tracker labels.

## The rail (`verify_issue_set.py`)

Refuses (exits non-zero) on: an unconfirmed spec (re-runs
`verify_spec_confirmed.py`); zero `blocks` edges across the whole set, or a
`blocks` target naming no known id; an untyped or wrongly-typed issue; a HITL
issue with no `hitl_reason`; and the structural basics (an epic with a title, a
non-empty issue list, unique ids, titles present). Coverage-vs-spec and
scope judgment are the independent reviewer's call, not the rail's.

## The adapter seam (`file_issue_set.py`)

Every tracker plugs into one port — `find_epic` / `create_epic` /
`find_issue` / `create_issue`. `find_*` returns a tracker ref or `None` by
searching for an idempotency-key marker embedded in the filed body.

- `github` — the shipped default; shells out to `gh`.
- `markdown` — the offline fixture; the "tracker" is one markdown file.
- `gitlab` — reserved seam, not built this epic.

### Idempotency

Each epic/issue carries a deterministic key (`epic:<hash>` /
`issue:<hash>:<id>`) embedded as a hidden marker in its body, plus a receipt
JSON keyed by those keys. On re-run the filer skips anything the receipt
records; when the receipt is missing an entry — the crash landed between the
tracker write and the receipt write — the adapter re-finds the item by key and
adopts it. This holds a duplicate-free result at all three crash points:
before-file, after-file-before-receipt, after-receipt.
