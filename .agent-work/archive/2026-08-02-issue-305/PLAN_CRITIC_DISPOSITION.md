# Cold panel disposition — issue #305

Three cold critics (intent-fit, testability, simplicity/YAGNI), each reading only the
planning artifacts with no authoring context. Panel, not single, per the review-class floor.

**Every load-bearing finding below was re-verified by me at source before disposal.** The
panel was right on essentially everything material, and the plan it attacked is not the plan
that will be built. One finding I override, with reason.

## The three findings that changed the design

### D1 — ACCEPTED, and it reverses my convergence. The widened seam is unnecessary: `start` is already unskippable.

Simplicity critic, finding 1. **Verified at source:**

- `advance()` — `checklist_engine.py:1644`: `if t["status"] != "in-progress": raise EngineError(...)`
- Only two sites set `in-progress`: `start()` at `:1635` and `reopen` at `:1852`.

So on a gated spine **every gate that ever advances must first be `start`ed**, enforced by
the engine's own status machine rather than by agent goodwill. My convergence widened the
seam to the whole `dispatch()` chokepoint to buy unskippability that `start` already
provides for free.

This is strictly better than either candidate, on every axis at once:

- **Blast radius** collapses from "every verb of every concurrent commander" to one verb.
- **Semantics improve.** `context_manifest.py`'s own docstring says the manifest records
  *"these files were made available to the agent running this step."* Emitting at step
  activation **is** that. Re-emitting on every subsequent verb smears it into "whatever was
  available at the last verb call" and destroys the delivery record it exists to be.
- **It removes two git subprocesses per verb.** `produce()` → `default_repo_state` →
  `repo_revision` shells `git rev-parse HEAD` **and** a repo-wide `git status --porcelain`.
  Under the widened seam that ran on every `attest`/`attach`/`advance`/`claim`, on shared
  machinery, with `.agent-work/` now tracked. Neither candidate priced this. I did not
  either.
- **Write-if-absent becomes possible**, which is what makes D2 solvable.

Adopted: **emit at `start()` and `reopen()`, write-if-absent.** My earlier recommendation
(`dispatch()` chokepoint) is withdrawn. The float to the Admiral is amended accordingly.

### D2 — ACCEPTED. `context-manifest-ref` was being filled in a form the frozen contract forbids.

Intent-fit finding 2, testability F3. **Verified at source:** `docs/EPISODE_STORE.md:679-689`
specifies the field as `<manifest-ref>@<revision>` — the worked example is
`ctx-governor-268-g1@a1b2c3d` — and states that *"any content-addressable artifact under git
satisfies this trivially by pinning to its own blob hash at capture time."* It then names
the failure case explicitly: *"If #300 lands as something that is not revision-pinnable (a
live-mutating index with no historical snapshot), that is a real conflict and a float to the
Admiral."*

Both candidates filled it with `str(manifest_path(...))` — a raw absolute worktree path, no
revision, dead the moment the worktree is swept, and **under my widened seam it was rewritten
on every verb**, which is precisely the live-mutating index the doc says to float.

Resolved without a float, because D1 makes it resolvable: with write-if-absent the manifest
is a stable per-step snapshot, and the pin is
`ctx-<work-id>-<step>@<rev>` where `rev` is `context_manifest.rev(manifest_bytes)` — the
existing blob-OID function, which is exactly the "pin to its own blob hash" the doc asks for.
The contract is satisfied as written rather than reinterpreted.

### D3 — ACCEPTED. The negative control I called "the strongest idea in either candidate" was the weaker of the two and was vacuous.

All three critics, independently. Testability F1/F2 is the sharpest statement.

**Verified at source:** `_validate_create` (`apply_episode_delta.py:888-899`) is a
**type-and-presence** checker. For the five string fields the whole test is
`isinstance(str) and value.strip()`; for the four int fields, `isinstance(int) and >= 0`.
The only value constraint anywhere is `RUN_RE` on `run`.

So the control I adopted is passed by:

```python
def mechanical_fields(...): return {"run":"x","project":"x","role":"x","spine-step":"x",
    "context-manifest-ref":"x","refusals":0,"reopens":0,"rework-count":0,"failed-commands":0}
```

Nine constants. Touches no `cl`, no journal, no evidence, no manifest. And the "red-proof"
(delete one field, assert the validator raises) passes byte-for-byte on that same constant
composer, because deleting a key from a dict is independent of how the dict was populated.
It proves *the validator rejects incomplete input* — not *the capture works*. Those are
different claims and I conflated them.

This is the fifth instance of the epic's own named failure shape, and I re-committed it in
the document that quoted the rule. Recorded plainly rather than smoothed over.

Adopted: **B's independently-tallied ground truth is the primary control** — the harness
records each induced event at the moment it issues the triggering call, then asserts equality
field by field against the composer's output. The validator stays in the pipeline as a shape
check on the way to the writer, which is what it is. It is not an oracle.

## Findings accepted that fix specific values

- **D4 — `durable` root formula double-nests.** Verified: the one shipped declaration is
  `{"root": "durable", "path": ".agent-work/LESSONS.md"}`
  (`COMMANDER_SPINE.template.json:31`), so `roots["durable"]` must be the **checkout root**.
  Candidate A's `durable_agent_work(repo_root)` = `<root>/.agent-work` would resolve to
  `<root>/.agent-work/.agent-work/LESSONS.md`, and `read_bytes` returns `None` for a missing
  file — so it ships a plausible-looking manifest with `rev: null` and every gate green. Use
  `durable_root()`.
- **D5 — `project` would be the worktree name.** Verified: `git rev-parse --show-toplevel`
  here returns `.../constellation-skills-wt/e298-305`, so `Path(root).name` = `"e298-305"`.
  The same repo yields a different `project` every epic, killing the one join meant to
  survive worktree deletion. Source it from the **main checkout** via `durable_root()`.
- **D6 — `artifact-ref`: both formulas are wrong.** Verified: the `artifact-ref` evidence
  type has **zero occurrences** across ~900 evidence items in `.agent-work/` (top types:
  `command-output` 439, `gated` 107, `user-decision` 101). So candidate B's formula requires
  a new agent habit — a second secretly-agent-dependent field, which is the exact class the
  issue forbids. Candidate A's synthetic `<task-id>.<type>#<id>` token is not a path and can
  never join across runs. The shipped episodes use **repo-relative paths**
  (`docs/EPISODE_STORE.md`, `.gitignore`, `.agent-work/issue-309/...`). Source from
  `_collect_changed_files()` (`checklist_engine.py:607`), which already returns repo-relative
  paths mechanically and is already shipped.
- **D7 — an all-null manifest is a valid manifest.** `rows()` emits `rev: None` for any
  unfound file and `required` is deliberately not copied into the row. So "manifest produced"
  and "manifest correct" are indistinguishable by presence checks. The control asserts
  `content()` against a hand-computed expectation for the step's declared refs, not merely
  that a file exists.
- **D8 — fail-soft must not be silent.** Accepted with a modification neither candidate had:
  the emit still never changes a verb's exit code, but an emission failure writes a **stub
  manifest recording the failure** rather than vanishing. A missing manifest and a failed one
  must be visibly different — this is inherited doctrine (*a non-reading must be visibly
  distinct from an uncollected one*) and my launch order names it.

## Findings accepted as scope reductions

- **D9 — gate count.** A proposed 9, B proposed 12, my convergence kept roughly the union.
  The simplicity critic is right that this reads as a rebuild, not wiring. Cut to **four
  gates**. Dropped: A's G7 (materializing the pre-#305 engine to prove a new feature is
  absent before it exists — a tautology), A's G8 red-proof (tests shipped code), A's G2
  (an absence check for a flag nobody wrote), B's G11 (re-tests `select_episodes`, already
  covered).
- **D10 — the 0/3/4 exit-code vocabulary has no call sites** once the bespoke verifier
  scripts are cut; the surviving checks are pytest, whose vocabulary is 0/1. Kept **only**
  where a non-pytest check genuinely survives, not as a blanket rule.

## The finding I OVERRIDE

**`run.dirty` removal is not a rider — it is ratified scope.** The simplicity critic
recommended cutting #327 to its own issue and noted honestly that it could not find
`LAUNCH_ORDER-305.md` to check. It could not: the order lives in the main checkout, which
critics are fenced out of. The order scopes #327 into this issue explicitly and carries
`decision:drop-run-dirty @grade: settled/human`. A `settled/human` tier means only the ruling
tier unsettles it — not me, and not a critic. **Kept, as ordered.**

Its adjacent observation is accepted and separable: after `dirty` is removed,
`default_repo_state` still calls `repo_revision()`, which still runs a repo-wide
`git status --porcelain` whose result nobody consumes. That waste is real. It is filed, not
fixed here.

## The finding that goes UP, not into the plan

**D11 — nothing triggers episode creation.** Intent-fit finding 1. Verified:
`docs/EPISODE_STORE.md:781` says *"**#305** wires automated capture — nothing writes to this
store on its own yet"*, and `_validate_create` requires all five agent-supplied assertion
kinds with non-empty statements, so a complete episode **cannot** be created without agent
judgment. Both candidates declined to wire creation; my convergence never mentioned it.

I will not resolve this silently in either direction. My reading, which the plan is built on:
the acceptance criterion is *"a run where the agent records nothing must still yield the full
mechanical field group"* — **the field group, not a complete episode**. So the engine emits a
**mechanical snapshot** at the same seam, mechanically, every run. The judgment half stays
agent-initiated because it is irreducibly judgment. That makes the negative control literally
true and the store's mechanical half genuinely zero-effort.

But whether that satisfies "#305 wires automated capture" as the store doc means it is not
mine to decide. **Floated.**
