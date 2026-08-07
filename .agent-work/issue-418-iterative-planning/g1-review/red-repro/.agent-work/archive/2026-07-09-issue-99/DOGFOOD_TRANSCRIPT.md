# Dogfood transcript + judgment — issue-99

Cold subagent (no authoring context; inputs: doctrine section, commander plan-step paragraph, design-it-twice-brief.md, toy issue). Rubric pre-registered in DOGFOOD_RUBRIC.md before dispatch. Full returned brief appended below.

## Judgment against the pre-registered rubric

| # | Rubric item | Result | Evidence in transcript |
|---|---|---|---|
| 1 | N≥2 dispatch set, distinct named constraints | **PASS** | 3 agents: A/smallest-diff, B/most-testable, C/best-seam-placement (all from the plan menu, mutually distinct) |
| 2 | Framing block with sketch explicitly labeled "not a proposal" | **PASS** | Constraints-in-play + held-fixed dependencies + code sketch headed "Illustrative sketch — NOT a proposal, zero weight at convergence" |
| 3 | Trap: typo handled as named untaken road, not silent | **PASS (full credit, branch a)** | "Untaken-road record — loud skips": typo named with reason (genuinely trivial, no interface/seam), folded as rider, "surfaced here at approval rather than silently bundled" |
| 4 | Panel-vs-single record with rationale, surfaced/overturnable | **PASS** | Panel of 3 with load-bearing-contract rationale AND a concrete human downscale option (drop C → 2 candidates) |
| 5 | Convergence stays human | **PASS** | Output section left "Pending convergence — convergence is human-only"; explicitly "not pre-empting the pick" |

**No FAIL conditions triggered. Verdict: PASS — the doctrine is followable by a cold reader.**

Beyond-rubric observations (positive signal, not scored): the subagent (a) correctly applied "one brief designs one thing twice" to split the bundled issue rather than briefing both decisions; (b) recorded a second untaken road (a 4th max-flexibility candidate, skipped as YAGNI, named so the human can reinstate); (c) unprompted, flagged the companion cold-plan-critic mechanism from the commander paragraph — the two-mechanism structure survived the cold read.

## Returned brief (verbatim)

# Design-it-twice Brief: `report.py --json output`

**Framing note before the brief:** the issue bundles two decisions — the `--json` flag (a new machine-consumed output contract) and the `sumary`→`summary` typo fix. Doctrine says one brief designs one thing twice; two decisions means two briefs. But the typo fix is genuinely trivial (a one-token string edit in the `--help` text, no interface, no seam), so it is **not** a second brief — it is recorded as a named untaken road below and rides along in the winning plan's gate. This brief designs the `--json` decision.

---

## The one thing being designed twice

The **gate plan** for adding `--json` to `report.py` — specifically **where the seam sits between report-data assembly and output rendering**, so the plain-text summary and the JSON emit the *same* data from one source of truth instead of two paths that can drift.

## Count and panel — a surfaced choice

**Panel of 3.** Rationale: `--json` introduces a **load-bearing, machine-consumed output contract** (other tools will parse it), and the issue's "same data as JSON" requirement makes the assembly-vs-render **seam placement** genuinely load-bearing, not cosmetic. Doctrine biases a load-bearing interface to a panel, and "when in doubt, panel." This is surfaced, not silent: **the human may downscale to 2** (drop the `best-seam-placement` candidate) if they judge future output-format extensibility a non-goal for this tool.

## The constraints (one per agent, each distinct and named)

Three plan candidates, same target, one constraint each:

- **Agent A — `smallest-diff`**: minimal change. Assemble the JSON at the existing print site reusing whatever is already in scope; fewest lines touched; no refactor of the text path.
- **Agent B — `most-testable`**: extract a pure `build_report_data()` returning a structured dict as the single source of truth; a text renderer and a JSON renderer each consume it; tests assert on the dict and on each renderer independently.
- **Agent C — `best-seam-placement`**: introduce an explicit output-format seam (a formatter dispatch keyed off `--json`) placed where a future `--csv`/`--yaml` would slot in without touching data assembly.

## Compared on

- **Depth** — does the candidate hide serialization/format complexity behind the seam, or leak `json.dumps` and field-shaping up into the CLI/arg-handling code?
- **Locality** — is the change contained to the format/print path, or does it fan out across `report.py` (and touch the text path's behavior)?
- **Seam placement** — is the assembly↔render boundary drawn where "same data, two formats" is enforced structurally rather than by convention?
- **Testability** — can the JSON payload and the unchanged text output each be exercised and falsified on their own?

## Framing block — presented to the human WHILE the agents run

**Constraints in play:** `smallest-diff` (least churn/risk), `most-testable` (shared-dict source of truth, isolatable pathways), `best-seam-placement` (extensible format boundary) — chosen to span the real tension: minimal churn vs. a durable seam for a contract other tools will consume.

**Dependencies — held fixed for all three candidates:**
- Existing plain-text output stays **byte-for-byte unchanged** (regression guard).
- JSON carries the **same data** — no fields added, none dropped relative to the text summary.
- **stdlib `json` only** — no new dependency.
- Flag is spelled `--json` (per the issue); the two output modes are mutually exclusive.
- The `sumary`→`summary` `--help` typo fix is folded into the same change but is **not** part of this decision.

**What each candidate will touch:** the argparse setup (add the flag), the format/print path in `report.py`, and the tests. Held out of scope: the data the report already computes.

**Illustrative sketch — NOT a proposal, zero weight at convergence:**
```
data = build_report_data(...)
print(json.dumps(data, indent=2) if args.json else render_text(data))
```
Offered only to prime parallel thinking. It leans toward one candidate's shape; it must not anchor the pick.

## Output — a recommendation, never a menu

**Pending convergence — convergence is human-only.** The three agents generate and compare; the human picks the winner or a named hybrid. This slot is filled *after* the fanout returns, with the opinionated pick plus the axis-by-axis reason it won (e.g. "B's `build_report_data()` source-of-truth seam, because it is the only candidate that makes 'same data' structural rather than conventional and lets the JSON payload be tested without the CLI — adopting C's dispatch only if the human keeps format-extensibility as a goal"). Handing back the raw three-candidate pile would be a failed run; the defended recommendation is the deliverable. I am **not** pre-empting the pick here.

## Untaken-road record — loud skips

- **Typo fix `sumary`→`summary`** — genuinely trivial, one-token edit in the `--help` string, no interface or seam decision. No parallel candidate warranted; folded as a rider into the winning plan's gate. Surfaced here at approval rather than silently bundled.
- **A 4th `max-flexibility` / pluggable-format-registry candidate** — skipped as YAGNI: a registry for one new format is speculative generality; `best-seam-placement` (C) already covers "leave room for a second format" without the machinery. Named so the human can reinstate it if more formats are actually coming.

## Panel-vs-single record

**Panel (3), because `--json` is a load-bearing machine-consumed output contract and the "same data" invariant makes the assembly↔render seam genuinely load-bearing.** Surfaced at the plan-approved checkpoint so the human can overturn it — the standing downscale option is **2 candidates** (`smallest-diff` + `most-testable`, dropping `best-seam-placement`) if output-format extensibility is judged a non-goal for this tool.

---

**Parallel-agent dispatch set I would launch** (not launched here): 3 agents, one constraint each — A/`smallest-diff`, B/`most-testable`, C/`best-seam-placement` — each producing ONE gate-plan candidate for `--json` scored on the four axes above, against the fixed dependencies. I present the framing block to the human at dispatch time so they reason in parallel; I converge only on their pick.

**Companion mechanism (noted, not executed here):** per the Mission-frame doctrine the plan step also runs a **cold plan critic** on the converged candidate plan + mission frame before the plan-approved checkpoint — sibling to this brief, bias-to-yes, findings human-triaged. Flagging it so the plan-approved gate isn't mistaken for design-it-twice alone.
