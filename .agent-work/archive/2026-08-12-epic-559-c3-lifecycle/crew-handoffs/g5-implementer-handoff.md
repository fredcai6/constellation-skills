# Implementer Handoff — g5: the two carried findings

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g5` · **Role:** `implementer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` (you are already in it)
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g5-implementer-result.md`

## Read first

`.agent-work/epic-559/c3-lifecycle/LIFECYCLE_CONTRACT.md` **§7 and §7b**.
`.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` — **the whole document**; you are reconciling
it, so you need all of it, especially §4, §6's `### CORRECTION` block, §7 and §10.
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g4-implementer-result.md` — g4 ran just before you and
added new fault codes. **Its result lists them; §7 of the note must gain them.**

## Finding 1 — `not_yet_written` is read with bare truthiness

`scripts/generate_spine.py:424` (`compile_condition`) and `:673` (`_probe_pytest`) both do
`cond.get("not_yet_written")`.

**It is worse than "a string is misread as a declaration", and the Commander measured this directly.**
Driving `generate_spine.compile_spec` on a fixture spec with `not_yet_written = "false"` (a TOML *string*)
returns `check: None` for that condition — **the gate silently loses its check entirely.** A field that
exists to make a check *not run* deletes the check when its author writes the word "false".

### The fix — refuse, do not coerce

Add a **new spec-shape fault** for a `not_yet_written` key present with a non-`bool` value: name the
field, the gate, the condition, and the offending type. Refused before any probe, alongside the other
`spec-*` faults in `spec_shape_faults`/`_cond_faults`.

This is **stricter than the launch order's literal wording** ("add the `isinstance` guard"), deliberately,
and the deviation is already recorded in `LIFECYCLE_CONTRACT.md` §7. A guard that silently reinterprets a
value reproduces the exact silence this generator exists to end — its own §1 says a wrong check "does not
announce itself: it exits 0 and the gate opens on nothing." Both plan candidates reached this
independently.

Note `True`/`False` are `bool`; `isinstance(x, bool)` is the right predicate. Be careful that `1`/`0` are
`int`, not `bool`, and must be refused.

## Finding 2 — `DESIGN_NOTE.md` §4, §7 and §10 are stale

The note is the generator's **frozen contract**, and a wrong contract is worse than none. Reconcile those
three sections against what the code actually does now, and against §6's own `### CORRECTION` block.

- **§4** — the closed kind vocabulary and what each kind compiles to. Verify every claim against
  `scripts/generate_spine.py` as it stands **after g4**. In particular §4's `qualitative` and `pytest`
  paragraphs must account for what `not_yet_written` does (it compiles to `check: null`), which the note
  never says anywhere.
- **§7** — the spec-shape fault vocabulary. It must list **every** fault code the generator can now
  raise: the originals, g4's new dispatch faults, and yours. **Enumerate them by command from the source,
  never from memory or from the note's existing list** — an under-inclusive list presented as complete is
  the exact failure this wave is watching for. State the count.
- **§10** — the four-defect table and its residual column. Check each row still holds. Where the code has
  moved, correct it; where a claim is simply no longer true, **delete it** rather than softening it.

**Correct or delete. Do not hedge.** If a claim is right, leave it exactly as it is — an unnecessary
rewrite of a correct paragraph is churn a reviewer has to re-verify for nothing.

## Close criteria

1. **VIOLATING** — `not_yet_written = "false"` (TOML string) is **refused by fault name**.
2. **VIOLATING** — `not_yet_written = "true"` (TOML string) is refused too. The guard is about **type**,
   not about value; a fix that only catches the falsy-looking spelling has missed the point.
3. **VIOLATING** — `not_yet_written = 1` (int) is refused.
4. **INNOCENT ×3** — `not_yet_written = true`, `= false`, and the field **omitted entirely** each behave
   exactly as they do today. The `= true` path must still compile to `check: null` and still emit the
   non-blocking `undecidable-pytest-not-yet-written` note; the `= false` and omitted paths must still take
   the strict probe path.
5. §7 of `DESIGN_NOTE.md` lists every fault code the generator can raise, **with the count stated**, and
   your result shows the command you enumerated them with.
6. §4 and §10 carry no claim the shipped code contradicts.
7. Suite green; `python scripts/validate_spine.py --sweep --root .` still exactly **23**. Neither shipped
   spec uses `not_yet_written`, so nothing shipped should move — if the number changes, **stop**: that
   means a shipped template moved, which is a no-go this wave.

## Allowed scope

`scripts/generate_spine.py` · `tests/test_generate_spine.py` ·
`.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` · `map/` (regenerated, never hand-edited).

## Specific exclusions

- **Do not touch `scripts/spine_lifecycle.py`, `scripts/mcp_spine_server.py`, or anything g4 shipped**
  beyond adding your own fault. g1–g4 are reviewed and integrated.
- `scripts/validate_spine.py` is **not** changed. You will notice it has **no `not_yet_written` concept**,
  so a legitimately-TDD-red check and a permanently-vacuous one are indistinguishable to the oracle
  (`LIFECYCLE_CONTRACT.md` §7b records this). **That is a finding for the return, not a change to make.**
- `generate_spine.py:910`'s missing `newline="\n"` — **this one IS yours** if you are editing that file
  anyway: fix it, since `docs/agents/CREW_CONTEXT.md:43` requires it on every write and CI runs
  `windows-latest`. Say so explicitly in your result.

## Constraints — a violation voids the gate

- `checklist_engine.py`'s on-disk format unchanged; `validate_spine.py` unchanged.
- `settings.json`, `.mcp.json`, `docs/agents/*` untouched. **If the harness refuses an `Edit`/`Write` on
  `.mcp.json`, that guard is deliberate — do not route around it with a `Bash` write. Block and ask.**
- `skills/**` untouched — a different crew owns it. If something there must change, **block and say so.**
- **`encoding="utf-8", newline="\n"` on EVERY write** (`docs/agents/CREW_CONTEXT.md:43`).
- Never run `scripts/install_constellation.py`. No merge, no push to `main`. Never `git add -A`.
  Never two crews in one worktree.

## Deliverable path check

- **Committed** — `scripts/generate_spine.py`, `tests/test_generate_spine.py` (both tracked).
- **Committed** — `.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` is **tracked**
  (`git check-ignore` exits 1), so it appears in `git diff` like any source file.
- **Local-only** — your result artifact; the Commander commits it.

## Required evidence

Load-bearing:

1. All three VIOLATING fixtures and all three INNOCENT cases, run, with output pasted.
2. **The mechanical enumeration of fault codes** for §7 — the command and its full output, plus the count.
3. The `DESIGN_NOTE.md` diff, with a one-line reason per changed claim ("§10 row 3 said X; the code does
   Y since g4").

Confirmatory: the suite total, the sweep count.

```
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

The Commander will tell you the exact pre-change suite total when dispatching; g4 raised it. Use `python`,
never `python3`.

## Stop conditions

- A constraint above would have to be violated → **block**, name it, return.
- The sweep count changes → **stop and block**; a shipped template moved.
- A `DESIGN_NOTE.md` claim you cannot verify either way → say so plainly in the note and in your result
  rather than guessing. An honest "unverified" beats a confident wrong contract.
- Two failed attempts at the same check → block rather than a third.
- **Never waive.** `spine_halt` with `action=block`, name what you cannot satisfy, and return.

## Return format

Write the result artifact at the path above **before ending your turn**. Carry a **`Return status`** field
whose value is exactly `complete` (lowercase) when done, the evidence above pasted verbatim, the fault
enumeration and its count, anything you could not verify, and a short **Workflow Feedback** section.
