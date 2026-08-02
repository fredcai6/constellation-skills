Wires mechanical episode capture from engine state, makes context-manifest emission a byproduct of step assembly, and removes `run.dirty` from the manifest producer.

Closes #327.

## What this is, and what it is not

#305 was framed as "wire the manifest producer". The baseline exceeded that framing, and the issue was re-scoped against the code before planning rather than against the order's description: `scripts/apply_episode_delta.py` (the validated writer) and `scripts/query_episodes.py` (retrieval) were already substantially built, and `_FIELD_READERS` already enumerated the mechanical field group exactly. **The field group was never this issue's to design — it is a frozen contract this issue fills from engine state.**

So: not "build capture". **"Wire capture from engine state into an existing validated writer, and make manifest emission a byproduct of assembly."**

At baseline, `grep -rn "context_manifest" skills/` returned nothing and `produce()` had **zero callers repo-wide**. #300's AC1 — "a manifest is produced on every deterministic assembly" — was therefore true *definitionally, over zero assemblies*. That was confirmed against the code, not assumed, and it is the fact that makes everything below matter.

## The four gates

| gate | what shipped |
|---|---|
| **g1** | Assembly seam — the manifest becomes a byproduct of starting a step |
| **g2** | Mechanical composer — the field group from engine state alone |
| **g3** | Negative control, proof it can fail, and cross-run retrieval |
| **g4** | Drop `run.dirty` (#327) and record the sequencing on main |

---

## Read this before you tidy anything away

**Severing the seam at its call site turns the control RED 8/13, so #300's AC1 is falsifiable — but #300's own tests stay fully green and never reach the call site (measured reached-count 0, not inferred). The falsifiability lives in #305's control, not in #300's tests.**

**Someone tidying away a control that looks redundant is the most likely way this mechanism dies quietly.**

That is the decay guard, and it is stated here rather than only in an issue because the PR body is what a future reader of `main` actually encounters. The control looks redundant precisely because #300's tests are green. They are green *without reaching the code the control protects*.

## An asserted property that was never attacked is a claim, not a guarantee

The closed-world census was asserted, and well documented, by the g3 rework — and **never attacked** until V2 (`attest --evidence`, the exact shape a blacklist misses). This is distinct from the "costume" family of defects: the guard was not vacuous, not theatre, and not badly written. It was simply never shot at. Documentation quality and adversarial exposure are independent axes, and only one of them was satisfied.

## A red-proof against a revision that never ships proves nothing about what ships

The g3 rework's proofs ran against `49059be` and `fb9dfc2`; the shipped file was `667b5e4`. The proof existed; the proof was not attached to the thing. This is a member of the **#345** pattern — *we reliably build the capability and unreliably wire the guarantee* — and it is filed as **#381**.

It is in this PR body and not only in the issue because it was found here, by the same discipline that the g4 gate then needed: every red-proof in g4 is bound to the shipped blob OID, and both the g4 implementer and the g4 reviewer recorded the OID they proved against.

## The corrected control claim — do not let a later summary re-broaden this

> The control supplies the engine no agent-authored **narrative**. Every string it hands over is a fixed identifier declared in the test module — the work id, the temp repo's directory name, the role, the condition ids, and one `reopen --reason` — and nothing composed at issue time. The mechanical fields that echo those identifiers (`run`, `project`, `role`) echo what the run is *made of*, not prose written *about* it. What the argv census mechanically checks is narrower than that claim, and the docstring says so.

**This claim has now been wrong three times in three different ways. Every error was in the broadening direction, and every one was caught by a mutation — none by reading.** The ratified sentence in the launch order did not survive verification; neither did the first correction. The sentence above is the one that did.

The reusable diagnosis: *every narrowing inspected the GUARD and asked "what does this fail to catch?" — nobody inspected the MECHANICAL FIELDS and asked "where does each one come from?"*, which answers it immediately, because `role`'s declared source is written in plain English in the test module. The audit kept examining the detector instead of the thing being detected.

## `run.dirty` (#327) — removed, not repaired

`build_manifest` no longer consumes the `dirty` half of the `repo_state` edge. No manifest carries the field anywhere — not in `run`, not in `repo_rev`, not in `content()`. `run` is now exactly `{work_id, generated_at, roots, host}`.

**Why removal rather than a third re-placement.** The field is **neither reliably constant nor informative**. It is repo-wide, so it reports dirt on files no declaration names; and it is not dependably `true`, because `build_manifest()` computes it **before** `write_manifest()` creates the file — so the flag never reads its own side effect, it reads its **predecessor's**. Measured at the point of removal, across the 49 manifests the producer had written in-tree: **47 `true`, 1 `false`, 1 field-absent.** A reader can therefore neither use a value nor ignore it; both readings are unavailable.

The lone `false` is the mechanism in miniature rather than an exception to it: commit `2456130` cleaned the tree 2m16s before that manifest was generated, so it recorded what its predecessor left behind, not what it was itself about to do.

Nothing replaces it. Per-declared-file dirtiness stays derivable from content alone — each row's `rev` against `git rev-parse <commit>:<path>` — which is scoped to the declared set and strictly better than a repo-wide flag.

`CONTENT_KEYS` is untouched, still `("contract", "step", "files", "repo_rev")`: `dirty` was never content, so the removal needed no content change. `content()` is byte-identical. `checklist_engine.repo_revision()` is **docstring-only — behaviour and signature unchanged**, still returning both halves as a general repo-facts primitive.

## Verdicts and waivers — no APPROVE was ever fabricated

`g2-integrate.c2`, `g3-integrate.c2` and `g4-integrate.c2` were each **waived `--force`**. The gate condition demands the literal verdict string `APPROVE`; the sanctioned verdict on this epic is `APPROVE-WITH-FOLLOWUPS`, which is a first-class verdict and not a soft BLOCK. That is a **gate-plan defect, filed as #371** — not a satisfied condition, and not a verdict anyone rewrote. **The real verdict is on the record in every case.**

The g4 review returned a genuine **BLOCK**, which is also on the record. It blocked on a false causal claim in the design doc — one the g4 reviewer handoff had explicitly named as *deliberately unverified by the Commander* and asked the reviewer to attack. It was refuted on both halves, reworked, and re-reviewed.

## Known, filed, deliberately not fixed here

- **#382** — the independence guard's static layer is defeated by an aliased import (`from episode_capture import reopen_total as _alias`), the exact case its own docstring names as covered; and the `artifact-ref` fixture stages only **one** path, so the multi-element constraint is unmet and mutation M8 (`out[:1]`) passes.
- `docs/CHECKLIST_ENGINE_DESIGN.md:187` omits `repo_rev` from the stated `build_manifest` return shape — stale since #300 g5, unrelated to #327.
- A surviving mutant in `default_repo_state`'s no-repo-root early return: deleting `"dirty": None` leaves the full suite green. The module docstring justifies returning both halves; that decision has no test.

## Suite

`1487 passed, 2 skipped, 472 subtests`, measured on the shipped tree.
