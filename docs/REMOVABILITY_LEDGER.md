# Removability coverage ledger

*The ground truth for epic-164's done-condition (#11): every **installed** external skill (superpowers + Matt Pocock + any other source) maps to a **constellation home** or a **recorded declination**. This is what is checked — mechanically — before the human uninstalls the externals. It is not a self-produced wish-list: it is checked against the actually-installed inventory.*

- **Machine-readable source:** [`removability_ledger.json`](removability_ledger.json)
- **Installed-inventory manifest (ground truth):** [`installed_externals_manifest.json`](installed_externals_manifest.json)
- **The rail:** [`scripts/verify_coverage_ledger.py`](../scripts/verify_coverage_ledger.py)

## How to check it (the done-condition rail)

```bash
py scripts/verify_coverage_ledger.py
```

Exit `0` means: every installed external is mapped, every `★`/covered home skill really exists in the corpus, and every declined row carries a reason. It **refuses** (exit `1`) when:

- **(a)** a `★` (new-this-epic) or covered row names a `home_skill` that does not exist under `skills/` — a false coverage claim;
- **(b)** an external in the installed-inventory manifest is absent from the ledger — a silently-missed capability;
- **(c)** a `declined` row has no reason — an unrecorded decision.

Legend: **★** = new or changed work in this epic (its home must exist); *unmarked* = already-covered by an existing skill (verify, don't build); *declined* = deliberate non-coverage tied to the capability it declines.

## Ground truth vs. the design spec (honest reconciliation)

The DESIGN_SPEC Section F expected sets did **not** all match the real install. Reconciled honestly:

| Source | Spec expected | Actually installed | Delta |
|---|---|---|---|
| superpowers | 14 | 14 (plugin v6.1.1) | **match** |
| Matt Pocock | 21 "v1.1.0" capabilities | **11** `mattpocock/skills` folders | **delta** — the spec named capabilities (`to-tickets`, `diagnosing-bugs`, `writing-great-skills`, `code-review`, `triage`, `research`, `handoff`, `setup`, `wayfinder`, `ask-matt`, `teach`, …) whose names do not match the installed folders. Where a spec capability maps cleanly to an installed folder it is preserved; spec capabilities with no installed folder are **not installed externals** and are not ledger rows. |
| vercel-labs | (not mentioned) | 1 (`find-skills`) | **spec omission** — installed but never enumerated by the spec; added honestly. |

The Pocock mirror symlinks under `~/.claude/skills/` are currently **dangling** (their `~/.agents/skills/` targets were pruned); `~/.agents/.skill-lock.json` is the authoritative installed manifest and is what the manifest was captured from.

**Result: 26 installed externals, all mapped — no uncovered coverage gap.**

## superpowers (14 installed, plugin v6.1.1)

| External | Status | Constellation home |
|---|---|---|
| brainstorming | covered | explorer |
| dispatching-parallel-agents | covered | admiral / workbench `run_crew` |
| executing-plans | covered | commander + checklist engine |
| finishing-a-development-branch | covered | admiral merge / commander cleanup |
| requesting-code-review | covered | reviewer |
| receiving-code-review | covered | reviewer + implementer rework |
| subagent-driven-development | covered | commander / admiral |
| systematic-debugging | ★ | diagnose (#4) |
| test-driven-development | covered | implementer |
| using-git-worktrees | covered | workbench / admiral (baked in) |
| using-superpowers | *declined* | skill-router; SKILL_INDEX + when-to-use descriptions suffice solo |
| verification-before-completion | covered | engine command-rails + reviewer |
| writing-plans | covered | commander plan step |
| writing-skills | ★ | write-a-skill (#6) + shared goodness criteria |

## Matt Pocock (11 installed, `mattpocock/skills`)

| External | Status | Constellation home |
|---|---|---|
| caveman | *declined* | persona/communication-style skill, not an engineering rigor workflow (out of scope, like Pocock `teach`) |
| diagnose | ★ | diagnose (#4) — one loop, two altitudes |
| github-triage | covered | triage |
| grill-me | ★ | interrogator sharpening (D1) — facts-vs-decisions + no-quit-early finish gate |
| grill-with-docs | ★ | interrogator sharpening (D1) — resolve facts by exploring code/docs |
| improve-codebase-architecture | covered | scout |
| tdd | covered | implementer |
| to-issues | ★ | to-initial-issues (#1) — one runnable current wave plus nonbinding forecast, dependency edges, and HITL/AFK typing |
| to-prd | *declined* | durable published spec declined by design; explorer's spec is bounded-durable, WHY retired into the network |
| write-a-skill | ★ | write-a-skill (#6) — remixes Pocock's authoring rubric into shared goodness criteria |
| zoom-out | *declined* | subsumed by cartographer current-only map + scout map-first audit; low value solo |

## Other installed source (1, `vercel-labs/skills`)

| External | Status | Constellation home |
|---|---|---|
| find-skills | *declined* | skill-router/discovery; SKILL_INDEX + when-to-use descriptions suffice solo (same class as `using-superpowers`) |

## What the human accepts at uninstall

Uninstall (#11) is gated on: every **★** row shipped (its home skill exists — the rail proves this), every unmarked row spot-verified, and the human accepting each **declined** row. A full replay of real invocations against a constellation-only box is a stronger future check (noted in DESIGN_SPEC TF9), not claimed here.
