# Constellation, positioned

*Where constellation sits relative to the two external skill sets it remixes and replaces — the **superpowers** plugin and the **Matt Pocock** skills — why it is different, what seat each constellation skill holds, and the workflow chains that connect them. The machine-checked external → constellation-home coverage record is [`REMOVABILITY_LEDGER.md`](REMOVABILITY_LEDGER.md).*

## What constellation actually is

Not a lightweight technique library. **Constellation is a team-rigor system for solo engineering with agents.** Its premise: rigor is worth the cost, so rigor is the *default*, not a knob. If you don't want rigor you don't reach for constellation. Every skill is a scaffold that keeps a human's standards intact while agents do the work — interrogation that won't quit early, gated checklists an engine enforces, confirmation gates with teeth, an independent reviewer on every change, and an architecture network that keeps *why* hooked to *what*.

The deeper thesis: rigor is a **team property**. One disciplined agent still misses things; a *team* of agents — author plus independent reviewer, commander plus crew, admiral plus waves — catches what any one misses, the way a human team does, while the human provides guiding vision and holds the super-high-level context. The independent fresh-context reviewer is the concrete embodiment of that thesis: it is what makes "trust the agent" safe, and it is cheaper than people think.

## The one-line difference vs. the sources we remix

| | superpowers | Matt Pocock | **Constellation** |
|---|---|---|---|
| Stance | reusable technique skills | "real engineer" skills; grilling-led; leaning toward reference-only economy | **rigor-first, engine-enforced, delegation-native** |
| Spec | — | durable, published (`to-prd` / `to-spec`) | **bounded-durable guidepost → retired into the architecture network** |
| Front door | `brainstorming` etc. | `idea → to-issues → implement` | **three entry paths by problem size (explorer / admiral / commander)** |
| Enforcement | prose | prose + router sync | **checklist engine + `verify_*` scripts + rails (machinery, not exhortation)** |
| Safety net | — | grilling | **an independent fresh-context reviewer on every change** |
| Delegation | subagents | HITL/AFK tags | **first-class: every tier asks up the chain; delegated commanders + admiral waves** |

Constellation **remixes capabilities** from both (vertical-slice language, HITL/AFK typing, dependency edges, refactoring/Fowler discipline, facts-vs-decisions grilling, reproduce-first debugging) but **imports no wording or doctrine** — it stays native. The point of the remix is *removability*: once the native form exists, the external skill can be uninstalled without losing the capability.

## The three entry paths (choose by how the problem feels)

**1 — Vague idea → `explorer`.** Let it breathe. Exploration cycles (shotgun / compare / refine) using interrogator doctrine, excursions (research / `prototyper` / design-it-twice), a cold critic panel, a hard human-only confirmation gate. Out: a confirmed **design spec** + the issues it should become. Explorer stays *pure exploration* — it does not file issues itself; `to-issues` cuts them.

**2 — Big but AFK-easy → `admiral`.** Runs a whole epic in waves of delegated commanders; can enter here directly (interrogator makes sure the idea is fully fledged first). Closeout: episode capture + cartographer reconcile.

**3 — Hard / into-the-weeds → `commander` (human-run).** Deep, focused interrogation that will not quit early (joint understanding is the gate). Two crew in cycles: **`implementer`** (rigorous TDD, vertical-slice chunks) and **`reviewer`** (validates intent *and* implementation, plus a Fowler code-smell pass). Multiple implementer ⇄ reviewer cycles are built-in design-it-twice. Then `cartographer` updates the network and collects feedback.

*Delegated vs. human commander differ only in interrogation depth. A delegated commander (`commander-delegated`) still asks up the chain; so does any crew. Delegation is a feature, not a fallback.*

## The spine that connects them

```
idea → EXPLORER → [confirmed spec] → TO-ISSUES (cut) → ADMIRAL (epic) / COMMANDER (issue)
                                                              → IMPLEMENTER ⇄ REVIEWER
                                                              → DIAGNOSE (when something breaks)
                                                              → CARTOGRAPHER (update network)
                                                              → closeout: retire spec's WHY into the network
```

The `to-issues` box — the cut-work seam between exploration and execution — is what turns a confirmed spec into a dependency-ordered, HITL/AFK-typed issue set (remixing Pocock `to-issues`/`to-tickets`: dependency edges + typing, filing owned here, invoked by the explorer agent but not baked into explorer).

## Each skill's seat

| Constellation skill | Seat in the system | Replaces / remixes |
|---|---|---|
| `explorer` | Ideation → confirmed design spec, human-only convergence | superpowers `brainstorming` |
| `to-issues` | Cut a confirmed spec into dependency-ordered, typed issues | Pocock `to-issues`, superpowers `writing-plans` |
| `admiral` | Run an epic in delegated commander waves | superpowers `dispatching-parallel-agents`, `subagent-driven-development`, `finishing-a-development-branch` |
| `commander` / `commander-delegated` | One issue end to end (live human / frozen launch order) | superpowers `executing-plans`, `subagent-driven-development` |
| `interrogator` | Facts-vs-decisions grilling with a no-quit-early finish gate | Pocock `grill-me`, `grill-with-docs` |
| `implementer` | Bounded change via gated TDD | superpowers `test-driven-development`, Pocock `tdd` |
| `reviewer` | Independent verification + Fowler refactoring pass | superpowers `requesting`/`receiving-code-review`, `verification-before-completion`; Pocock `code-review` |
| `diagnose` | Reproduce-before-you-claim debugging (bug + disconnect) | superpowers `systematic-debugging`, Pocock `diagnose` |
| `write-a-skill` | Author a skill, install-and-corpus-correct rail + shared goodness criteria | superpowers `writing-skills`, Pocock `write-a-skill` |
| `scout` | Map-first architecture-pressure audit | Pocock `improve-codebase-architecture` |
| `triage` | Findings/gaps/drift → issue-ready recommendations | Pocock `github-triage` |
| `cartographer` | Current-only structural map + overlays; retired-spec WHY | (native) |
| `prototyper` | Throwaway prototype answering one named question | (native) |
| `charter` | Compile project doctrine, glossary, engine config | (native) |
| `curator` | Periodic corpus-health maintenance | (native) |
| `docent` | Static HTML explainer from map truth | (native) |
| `workbench` | The checklist-engine substrate every skill drives | (native) |

`skills/_shared/` is shared doctrine (e.g. `skill-goodness.md`), consumed by `write-a-skill` and `curator` alike — it is not itself a skill.

## Deliberate declinations

Not every external skill earns a native home. Constellation *declines* a capability when covering it would add no rigor or would reintroduce a rejected pattern — each declination is recorded, with a reason, in the [removability ledger](REMOVABILITY_LEDGER.md):

- **Skill routers** (`using-superpowers`, `find-skills`): a solo corpus's SKILL_INDEX + each skill's when-to-use description already routes invocation.
- **Durable published spec** (`to-prd` / `to-spec`): constellation's spec is a *bounded-durable* guidepost whose WHY retires into the architecture network — covering the durable-document form would reintroduce the anti-pattern the design rejected.
- **Persona / non-engineering skills** (`caveman`, and Pocock `teach`): out of scope for an engineering rigor system.
- **`zoom-out`**: subsumed by the cartographer current-only map + scout's map-first audit.

## Removability

The whole point of the remix is that the externals become removable. The external → constellation-home mapping — including the declined rows — is the **removability ledger** ([`REMOVABILITY_LEDGER.md`](REMOVABILITY_LEDGER.md), machine-readable source [`removability_ledger.json`](removability_ledger.json)), grounded in the actually-installed inventory ([`installed_externals_manifest.json`](installed_externals_manifest.json)) and enforced by [`scripts/verify_coverage_ledger.py`](../scripts/verify_coverage_ledger.py). That ledger — not this prose — is the ground truth checked before the externals are uninstalled.
