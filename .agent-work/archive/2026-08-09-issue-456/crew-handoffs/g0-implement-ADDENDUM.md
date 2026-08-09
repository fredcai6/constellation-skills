# g0 handoff — ADDENDUM 1 (Commander rulings)

Written 2026-08-07, after the first implementer returned `partial` at a context
trip. **Read this together with `g0-implement.md`.** Nothing in the original
task, scope, or close criteria is withdrawn; this only settles the three
decisions the first implementer correctly flagged instead of deciding alone, and
adds the field it found missing.

## Ruling 1 — do NOT port `render.py` or `render_fn.py`. Ratified.

The original handoff's module table listed six prototype modules. That table was
wrong to imply all six get ported, and it collided with this same handoff's own
wiring rule (zero external call sites is a stop condition). The implementer took
the wiring rule as governing and flagged the conflict. **That was the right
call and I am ratifying it, having verified the reason independently rather than
taking it on trust:**

`render_map.py`'s own header states it is a *"self-contained adaptation of
evidence/x11/render_fn.py"* which derives the module list instead of hardcoding
it. `render_fn.py` carries the human's page-format rulings (one page per
class/function/method, agent-lean, ASCII-only template text) — and those
rulings are carried **forward** into `render_map.py`, not lost by skipping it.
So `render_map.py` genuinely supersedes both, and porting the other two would
create symbols nothing calls.

**Port four modules:** `astx.py`, `supplement.py`, `render_map.py`, and the
`checks.py`/`checks2.py` pair (wired only — `g1` rewrites them).

The read-only prototype keeps all six, so nothing is lost if a later gate wants
them.

## Ruling 2 — artifact paths. Ratified as proposed, and now fixed here.

The original handoff never said where rebuilt artifacts land, which is a real
gap: the `.gitignore` entries it demanded presuppose paths no field supplied.
Fixed:

- **Statement store and supplement → `<root>/.code-map/`**
  (`statements.jsonl`, `supplement.json`).
- **Page tree → `<root>/map/`.**

The reasoning is sound and worth keeping: the render stage does `rmtree(map/)`,
so intermediates must not live under `map/` or the render deletes the stores it
was just built from.

## Ruling 3 — TWO `.gitignore` entries, not three. Changed.

The original handoff demanded three narrow entries: statement store, supplement,
**position cache**. The implementer found that **no gate in the plan produces a
position cache** — `g3` only removes positions from `ids.jsonl`, and pages still
carry `path:line, N lines`. It is right.

**Ruling: write two entries, for `.code-map/statements.jsonl` and
`.code-map/supplement.json`. Drop the position-cache entry.** An ignore rule for
a file nothing produces is precisely the stale line that `g3`'s own close
criterion complains about for the supplement — I am not going to ship the defect
this plan exists to remove. If a later gate introduces a position cache, it adds
its own entry as part of that gate.

## New field the handoff should have carried — Discovery mechanism

The discovery layer enumerates from **`git ls-files`** (with `-z`, so unusual
paths cannot be silently mangled by git's default quoting). This was stated in
`gate-spec.json` but not in the handoff, and the first implementer had to go
find it. It is already implemented and green — recorded here so it is not
re-litigated.

## Two triage candidates filed from this crew's observations

Both are recorded on the spine; **neither is yours to fix.** Do not act on them.

- **`tc6`** — `corpus` is overloaded. The glossary defines it as the *installed
  skills* corpus; this issue uses it for source files, and `discover_corpus` is
  now a shipped symbol name. Keep the symbol name as-is and say **"mappable
  corpus"** in prose where the distinction matters, exactly as the first
  implementer did.
- **`tc5`** — the context gauge is work-area-scoped, not agent-scoped (see
  below).

## Why the first implementer stopped, and what it means for you

It hit a HARD context trip at `advance m2-cli` and filed a `refresh-request`
exactly as doctrine requires. **Its work is done and green — only the gate was
left unclosed.**

**Important, and it affects how you should read your own trips:** the gauge is
shared across the whole work area, so the reading you see may be the
*Commander's* context rather than yours (`tc5`). A trip is therefore not
reliable evidence about **your** headroom. Do not push through one — the rule
still stands — but do not treat it as proof you are nearly full either. Just
file the request and hand off cleanly, and say in your result how much real work
you had left.

**This gate is deliberately being run as more than one implementer pass.** That
is a design change I am making on the first implementer's own feedback: a gate
this wide (six modules, ~90 KB, plus the doctrine set) does not fit one context,
and discovering that seam by tripping into it wastes a run. You are not behind,
and you are not expected to finish everything.

## Where to pick up

Drive the existing plan at `.agent-work/issue-456/g0-implementer-plan.json`.
**Claim it with the same session id, `g0-impl-9febe0be`** — a same-id re-claim is
idempotent, not a takeover, so no `--force`.

Cold-start from `current`. The first item is `advance m2-cli` (its work is
already green — 7 CLI tests plus the discovery suite; only the gate is open),
then `m3` onward: the four stage ports, the two `.gitignore` entries, the
bundling resolution, the end-to-end run, and the closeout evidence.

**Commit as each item closes.** Do not save it all for the end — if you trip,
committed work survives and uncommitted work does not.
