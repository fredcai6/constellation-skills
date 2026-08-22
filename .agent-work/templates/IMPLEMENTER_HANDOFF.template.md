# Implementer Handoff

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Concise fragments. Omit filler.

## Gate
`<gate id from execute.json, e.g. g1>`

## Task
`<one bounded task — what to build>`

## Protected Intent
`<the user/system outcome this gate must not violate>`

## Test Mode
`<TDD required | test-after allowed | inspection-only — brief reason>`

## Close Criteria
`<what must be true when done; each item the implementer proves>`
- `<criterion>`

Never pin a literal artifact count (packets, decisions, modules, pages) recalled from memory into a close criterion — a hard number the evidence must "match" is a trap when it disagrees with map truth. Write "one page per packet file — count from the map at authoring time" or re-derive the number from the live map before freezing the handoff.

For a **meaning-preserving doc / register-diet** gate, carry three explicit lists so the edit is deterministic for the implementer and independently verifiable for the reviewer: the exact BEFORE/AFTER for each edit, a MUST-SURVIVE operative-fact list, and a forbidden-signature list. When any of that edit's prose is lifted **verbatim from a SKILL.md**, dry-run it against the residual-guard signature list — the retired/relocated signatures a no-residual guard asserts must not reappear inline (e.g. the `retired` tuple in `tests/test_install_constellation.py`) — **before dispatch**, so the handoff never asks the implementer to re-introduce a signature the guard will later reject.

## Allowed Scope
`<files, modules, regions, or decisions the implementer may touch>`
When the gate adds or changes a validation, **pre-authorize the test files that already exercise the gated behavior** (their test data/harness, not excluded production code) so a legitimate minimal reconciliation of those tests does not read as an out-of-scope breach. When the behavior change **invalidates an existing test's scenario**, name that test and say so explicitly ("expect to reseed/rewrite test X — its old scenario is what this change now forbids"); otherwise "full suite green (N tests pre-change)" reads as don't-touch-existing-tests and momentarily conflicts with the close criteria.

When the gate asks the implementer to **dogfood a method-in-skill generator** to produce a demo artifact, explicitly sanction a non-shipped generation aid (a throwaway script that mechanizes the method, output-only committed) — otherwise the implementer must reason about whether hand-authoring is required to honor "no large generator shipped."

## Specific Exclusions
`<things that look in-scope but are off-limits; omit section if none>`
In a multi-issue wave, **annotate every fenced / do-not-touch line with the OWNING issue number**, and where two gates' or issues' scopes intersect, name the exclusion explicitly at the intersection.

## Constraints
`<rules the implementation must respect — from project rules or gate-specific needs>`
- `<rule>`

When the task passes an object/dataclass-typed parameter, **name its fields explicitly** rather than leaving the crew to infer the shape from surrounding call sites.

## Map Anchors (inbound)
Map context this gate inherits from the mission frame, so the implementation lands on the right structure and honors recorded rules. Omit a line when the gate carries nothing for it.
Carry each decision anchor's `@grade` tag across from the mission frame on its own child line — an anchor without its tier reads as equally settled as every other, leaving this gate no way to tell "revise this freely" from "stop, this is not yours to unsettle" when the implementation meets reality contradicting it (see `references/global-everyone.md`, "Decision fixedness").
- **Map entry point:** `<the specific map file(s) where this crew starts — "start with this page/packet". You already did the map work at frame time; hand it down so the crew never re-derives it. Omit only when no map artifact touches this gate.>`
- **Structural:** `<struct:id — path/symbol, level — where the work lands or depends>`
- **Capability:** `<capability:id — behavior this gate changes or relies on>`
- **Constraints/assumptions:** `<constraint:id | assumption:id — must not be silently violated>`
- **Decision anchors:** `<decision:id — governs this structure; do not contradict without surfacing a candidate>`
  `@grade: <tier>[/provenance][ · leans <ids>][ · settle: <experiment>]`
- **Evidence expectations:** `<claim:id or check this gate must re-confirm>`
- **Map confidence flags:** `<node id — low-confidence/stale/disputed area; verify rather than trust; omit if none>`

## Deliverable Path Check
`<required — filled by the commander at gate-planning time, before dispatch. For each of this gate's deliverable artifact path(s), classify it:>`
- **Committed** — `<path>`; verified via `git check-ignore <path>` exiting 1 (not ignored) before dispatch — record the exact command run and its exit code.
- **Local-only** — `<path>`; intentionally gitignored (e.g. under `.agent-work/`) — state this explicitly so the reviewer does not expect it in the diff.

When a gate creates a **new** tracked-to-be file, state that it is untracked until staged: "`git diff` shows N-1 files; the new file appears in `git status`." Otherwise a scope claim like "diff touches exactly N files" reads as false against a correct working tree and the reviewer momentarily mistrusts correct evidence.

## Required Evidence
`<what to produce: test output, command result, inspection note, generated artifact>`
When the crew must assert a specific return/message string, **quote the EXACT expected string** so the crew asserts equality, not a substring guess; mark any illustrative example string as illustrative.
A claimed test-failure distribution must be **derived mechanically** (`pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`), never summarized from a glance at the output tail — the reviewer reproduces every figure, and a correct root cause does not excuse a wrong supporting number.
When the gate expects the suite to be transiently red, state the expectation **by root cause** (the failing mechanism, wherever it surfaces) with the per-file distribution shown — never by file name alone — and make any failure outside that root-cause class a stop condition.
A handoff spends the implementer's finite **self-check budget**: every additional fact the Required Evidence asks it to *prove* divides that attention further, so an over-stuffed evidence list buys **content coverage** on paper and shallow checking in practice. Name which evidence items are load-bearing (prove rigorously) versus confirmatory (a spot-check suffices), rather than letting every item compete equally for the same self-check budget.

## Wiring Grep

**Required. Write `none — <reason>` only for a slice that adds no callable symbol.**

One command naming every symbol this slice adds, showing for each a call site **outside its own
definition and outside any `--self-test` path**:

```bash
<grep naming each new symbol, e.g. grep -rn "new_symbol" --include=*.py . | grep -v "def new_symbol" | grep -v self_test>
```

**We reliably build the capability and unreliably wire the guarantee.** A symbol that only its own
definition and its own self-test reference is shipped-inert: it passes review, passes tests, and no
caller ever reaches it. **State the count of call sites found.** Zero external call sites is a stop
condition, not a note — `grep` for the *caller*, because `grep` for the *name* is satisfied by any
module that ships its own self-test.

## Verification Commands

Exact commands to run. Write `none — <reason>` if not applicable.

```bash
<command>
```

## Suggested Model Tier
`<simple bounded | stronger — reason: scope/ambiguity/risk>`

## Authority
`<decisions already made and by whom; what the implementer must not decide alone>`

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required evidence cannot be produced, a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the work harder than it needed to be).

The result's `Return status` field (`complete | partial | blocked | out-of-scope | failed`, `references/status-model.md`) is what the Commander copies verbatim, lowercase, into this gate's `implementer-result` evidence as the `status` field — the gate's postcondition matches on that exact field name and exact-case value, so write it lowercase here.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to `.agent-work/<work-id>/crew-handoffs/<gate>-implementer-result.md` before ending your turn — that write is the delivery, and it is what a resumed or relaunched Commander finds regardless of which instance dispatched you. `SendMessage` an announcement to the dispatching Commander too, but treat it as a best-effort courtesy ping, not the delivery itself: the instance you address may have relaunched or handed off in the meantime and no longer resolve, or (dispatched as a subagent) may not be addressable from your thread at all — a missing ping is not a missing result.
