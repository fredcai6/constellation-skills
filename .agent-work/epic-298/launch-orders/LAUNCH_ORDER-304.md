# Launch Order: `commander-304 — issue #304, Commander map-input contract`

You start cold. Everything below is pasted, not pointed at.

## Mission

Issue #304 (spec B3): express Commander map-first intake as **one canonical concern-owned contract** projected into Commander context and plan — a resolved canonical entrypoint, a **REPORTED** degraded mode when it cannot be resolved (never a silent fallback to code crawling), and **deletion** of the scattered prose the contract supersedes, each deletion filed with a predictive tripwire. Then **run** the affected workflows and record the outcome against each tripwire — the pathway is deletion **plus run**, not deletion alone. Plus the first corpus-size / per-role-surface trend snapshot from git as the standing aggregate baseline.

Full cold-panel agentic review per spec B0.4. This is not downgradable to a light pass.

## The single most important thing in this order

**The deficiency is primacy and contract — not path.** Do not build "resolve an entrypoint." That capability already exists in the corpus that matters and is demonstrably insufficient.

Measured, at f1Brainz commit `3541d292`, in `CLAUDE.md` — the file Claude Code auto-loads into every session:

```
Also read before touching an area:
- `README.md`                  — repo map and entry points
- `TESTING.md`                 — test commands and failure triage
- `docs/architecture/index.md` — structural map: module boundaries, relationships, dead paths
- `docs/DOCUMENTATION.md`      — doc library map and maintenance rules
```

Verbatim again at `AGENTS.md:27` and `README.md:203`. **A canonical entrypoint, at an exact path, in the always-loaded bootstrap.** But it is one of four supplementary reads, a peer of a test-commands doc, and "Also" marks the whole list secondary. No primacy. No "first." No orientation protocol. No statement of what to do when it is missing or stale.

Tommy's framing, which is the bar: **"there is a gulf between saying 'there is a map' and 'use the map first to orient yourself'."**

What you are building is the second thing.

## Prior-Wave Verdicts (pasted)

### From #299's baseline capture — merged `8de2faa`, record at `.agent-work/epic-298/baselines/BASELINE_RECORD.md`

Five plan-stage Commander-brief runs against f1Brainz pinned at `3541d292`, rubric frozen before any run.

**Finding 1 — the map is a confirmation step, not an orientation step.**

| task | tool calls | first `docs/architecture/*` | first `src/*` | map before src? |
|---|---|---|---|---|
| #690 | 43 | 5 | 2 | **no** |
| #688 | 35 | 23 | 0 | **no** |
| #698 | 35 | 28 | 0 | **no** |
| #716 | 61 | 51 | `NO-SRC-READ` | n/a |
| #704 | 10 | 4 | 0 | **no** |

Every run read source before the map. **Every run did read the map** — no run reached `NO-MAP-READ`; three reached it only after 20+ tool calls. Uniform shape: grep/ls into `src/`, form a hypothesis, then open the packet to check it.

**So a canonical entrypoint named in the auto-loaded bootstrap did not produce map-first orientation.** That is your problem statement, measured rather than assumed.

**Finding 2 — ZERO skill invocations across all five runs.** Not one `Skill` call, with the `Skill` tool present and all 19 constellation skills enumerated in every `system/init` event. Four of five never read a corpus file at all. The corpus was **offered and declined**.

**Read that finding carefully, because it bears directly on your design** — see Pre-Rulings.

**Finding 3** — the negative control (#704, single file named in its own title) is indistinguishable from the real tests on the ordering measure, and was the cheapest, cleanest run in the set. Non-discrimination in a single arm is uninformative rather than disqualifying, but it means "induced map consultation" is **not** by itself evidence your contract worked.

**Declared limitation** — the baseline's seam-lift power is ≈1 partially-discriminating task at n=1. It supports a direction-of-travel note only. Do not treat any seam number from it as a target.

### From #302 — Tommy's ruling on the two-bin rule

**No third bin. Assumption 6 stands, B0.3 unchanged.** Verbatim: *"machinize the mechanizable. we don't need stochastic reasoning for predictable logic... these are aspirations."* Note the precise shape: the third-bin candidates were not ruled *mechanizable*, they were ruled **not catastrophic**. They stay as prose and do not earn a bin.

### From #300's cold panel — the methodology finding that applies to you

45 deliberate mutations, 34 killed, 11 survivors. It found the issue's single acceptance test **could not falsify the property it existed to falsify** — it re-encoded both children's artifacts through the parent's encoder, so an environment-dependent encoder passed green. **That had already survived two independent reviewer rounds**, one of which returned a correct BLOCK on a different real defect. The commander's diagnosis: *"a reviewer given a handoff checks conformance to that handoff, and no handoff asked 'can this test fail?'"*

This order asks it: **can your degraded-mode check fail?** Prove it by mutation, not assertion.

## Pre-Rulings

Each overridable if evidence contradicts it — say so when overriding.

- decision:primacy-not-path — the contract must establish that map orientation happens **before** source exploration and **informs** it. A contract that only resolves a path ships a capability f1Brainz already had.
  `@grade: settled/human · leans #304,#307`
- decision:contract-at-context-and-plan — wire it at the **context** and **plan** steps, not reconcile. The two existing `docs/architecture` mentions in Commander doctrine (`commander-core.md:142`, `COMMANDER_SPINE.template.json:75`) are **both the absent-map fallback at reconcile** — neither fires at orientation time. What *does* fire at orientation time are two **pathless** imperatives: context's *"Read the current map (packets, overlays, decision anchors) for the area the ask touches"* and plan's *"Map-first: BEFORE authoring execute.json, produce a mission frame from the current map."* Both say *the current map*; neither says where it is. **Your contract is the join between pathless-but-primary (corpus) and pathed-but-secondary (target repo).**
  `@grade: settled/human · leans #304`
- decision:317-folds-in — #317 is **yours**. Every shipped checklist template carries `"config_ref": "docs/agents/engine-config.json"` plus several hundred words of imperative prose explaining the path is dead, that its absence is sanctioned degradation, and that the reader must **not** create the file. **That prose is now wrong in both directions**: `docs/agents/` exists in this repo as of #325, and f1Brainz genuinely ships `docs/agents/engine-config.json`. It is plausibly the concrete instance behind Tommy's *"it pointed to some random template at at least one point."* This is corpus-wide-or-nothing, and you are the corpus-wide issue.
  `@grade: settled/human · leans #304,#317`
- decision:tripwires-are-episodes — file each deletion's predictive tripwire as an episode in the store shipped by #301 (`episodes/active/`), **not** in `.agent-work/LESSONS.md`. Tommy ruled the playbook a dead end; episodes accumulate, consolidation lands in `docs/agents/`, live agents read local+global doctrine only. This is better for you, not merely different: the episode record already carries a prediction and an outcome slot, which is exactly the deletion-plus-run pathway's shape. LESSONS.md has no outcome field and is at its 20/20 cap.
  `@grade: settled/human · leans #304,#308`
- decision:degraded-mode-is-the-common-case — "unresolvable entrypoint" is not hypothetical. It is the current state of every repo without `docs/architecture/`, **including this one**. Treat the reported-degraded path as the common case, not the edge case, and give it at least as much design attention as the resolved path.
  `@grade: guess · leans #304 · settle: count repos in the dogfood roots with and without docs/architecture/`
- decision:baselines-satisfied — `decision:baselines-before-f-merge` is **discharged**. #299's arm is captured and merged. You may merge when green and reviewed.
  `@grade: settled/human · leans #304,#299`

## The design question I am NOT pre-ruling — weigh it in your design-it-twice

Finding 2 says the corpus was offered and declined: zero skill invocations in five runs on ordinary planning briefs. If that holds, **a contract that lives only inside Commander doctrine reaches only agents who chose to invoke the Commander.**

The one surface that was reliably delivered in every measured run is the target repo's **auto-loaded `CLAUDE.md`**. Everything else — skills, `docs/agents/*`, references — requires the agent to choose to read it.

So there is a real design fork, and it is yours to explore rather than mine to settle:

- **(A)** The contract lives in Commander doctrine, as the issue was cut. Clean, concern-owned, and reaches Commanders only.
- **(B)** The contract additionally projects a thin, generated stanza into the **consuming repo's** always-loaded bootstrap surface, so the primacy instruction is delivered whether or not a role is invoked.
- **(C)** Something else you find.

(B) is not obviously right — it puts Constellation content into a file the target repo owns, which is a real boundary cost and a maintenance surface. But (A) may be building a delivery mechanism the measurement says does not deliver. **Run this through design-it-twice under distinct named constraints and surface the convergence to the Admiral** — convergence is human-only per the latitude contract.

The probe on #331 is running in parallel and may reduce the uncertainty here. **Do not block on it**; if its result lands before your plan freezes, I will forward it.

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable, reported with the same rigor as a win. The spec is explicit: *"if deletion alone suffices, the break is not taken — that outcome is success, not failure."*

Applied here: if the deletion-plus-run pathway shows the superseded prose was doing nothing and the contract adds nothing measurable, **say so**. If a tripwire fires against you, record it against the tripwire rather than explaining it away — that is the entire point of filing predictions before deleting.

Scoped nulls: a negative kills that specific test, never the idea class. "This contract shape did not change orientation" — never "map-first cannot be mechanized."

## Inherited Latitude

**Delegated** — adjudicate and log: architecture/structural choices inside your deliverable; issue filing/closing on `fredcai6/constellation-skills` (`gh issue create/comment/close` pre-cleared — **file findings to the tracker directly, never bank them worktree-locally**); fix-now triage; full test suite; `git push` to `epic-298/*`; merge when green **and** reviewed, gated on the CI check exit code read at source; model tier for sub-dispatches within Budget.

**Must float to me** — do not decide: any scope change; **design-it-twice convergence on the load-bearing contract shape (human-only, always)**; production defaults or user-visible behavior; **two-bin routing rulings and pathway verdicts — Tommy's, always**; anything out-of-taxonomy, with one line on why it fit no class.

**Not pre-cleared:** any `gh` write against `fredcai6/f1Brainz`.

## File Ownership

Working notes: **`notes-304.md`**. Sole writer.

> Never `findings-304.md`. The harness `Write` tool refuses any path whose basename contains "findings" — a guard against unprompted report-dumping that cannot tell this file was deliberately assigned. Three agents hit it in one epic. The guard is not ours to change; the word is.

## Workspace

```
C:/Programs/constellation-skills-wt/e298-304
branch: epic-298/304
base:   8de2faaa04d8db66847e3ac92d7f84cd89efa084  (origin/main, "measure(#299): capture the PRE-change baseline arm ... (#334)")
```

**First step, before any git operation**, from inside that worktree:
```
py scripts/verify_worktree_isolation.py --here "C:/Programs/constellation-skills-wt/e298-304"
```
Must exit 0. Paste the output into your return. Run from anywhere else and it correctly refuses — that is the check working.

**Do not touch `C:/Programs/constellation-skills`.** It carries Tommy's uncommitted work (`install_constellation.py`, `tests/test_write_a_skill.py`, `SKILL_INDEX.md`, untracked `skills/clean-codebase/`) that a branch checkout there would disturb. This already cost a recovery once this epic.

A second commander (`epic-298/331-probe`) is live in `constellation-skills-wt/e298-331`. **Never enter its worktree.**

When editing global doctrine, edit the canonical `skills/_shared/global-*.md` — **never** `skills/<role>/references/global-*.md`, which `install_constellation.py` regenerates at install time. An edit there is silently overwritten.

PR integration defaults to **server-side merge**.

## Inherited Context

**Python and CI — measured today, and both interpreters are wrong in different directions:**
```
py     -> 3.12.13 (matches CI's pin) but pytest NOT INSTALLED -- `py -m pytest` fails outright
python -> 3.14.3  (two minors AHEAD of CI) with pytest 9.0.2
```
Run the suite with **`python -m pytest`** (full suite is ~1160 passed, 36s). **A local green is never the merge gate** — gate on the CI check exit code read at source, re-run at merge time. `Path.read_text(newline=...)` is 3.13+ and passed locally while failing CI on PR #320, costing 39 failures.

**Windows:** write files with explicit `encoding='utf-8', newline='\n'` (default is the ANSI codepage; this epic lost a JSON delta to `UnicodeDecodeError: byte 0x97`). MAX_PATH is real — paths over ~180 chars break `git worktree add` on windows-latest. PR bodies: write to a temp file and `gh pr create -F <file>`; a heredoc or PowerShell here-string **fails for PR bodies** (here-strings work for `git commit -m` only, and not at all in the Bash tool). `core.autocrlf` means working-tree bytes differ across worktrees for identical committed content (#319) — compare normalized content or blob OIDs. Use **absolute paths** for `git worktree add`.

**Engine:** never hand-edit spine/survey JSON. `--finding` text containing backticks is **shell-mangled and silently drops words** from the journal — avoid backticks in findings. On a **survey**, `record` is the re-record verb; `advance`/`reopen` refuse as gated-only. Command postconditions inherit the launcher's cwd (#315) — relative paths resolve against the wrong root.

**Method:** *a check that cannot fail is indistinguishable from one that passed* — and it appears in **rubrics** as well as tests: #299's cold critic killed a losing condition mathematically bounded at 0, which could only fire when another had already fired. *Verify launch-order claims against the code* — this order states facts about f1Brainz and about doctrine line numbers; **if something here does not match what you find, the code wins, and say so in your return.** *Derive distribution claims from a command*, never from a test-output tail. *A round-trip test proves the parser, not the artifact.* *A non-reading must be visibly distinct from an uncollected one.*

## Pre-empted Steps

- **Problem framing** — the primacy-not-path framing above is ratified; do not re-derive it.
- **Baseline arm** — captured, merged, and pasted above. Do not re-run it.
- **#317 disposition** — folded in, not a separate corpus cleanup.
- **Worktree provisioning** — done.

## Data Locations

- Baseline record and transcripts: `.agent-work/epic-298/baselines/` (in your worktree, on main as of `8de2faa`). `runs/run-<N>/stream.ndjson` holds full tool-call transcripts; `extract_ordering.py --self-test` runs 33 checks including a real-transcript fixture.
- f1Brainz: `C:/Programs/f1Brainz`, pinned `3541d292`. **Read-only. No pushes, no PRs, no issue comments.**
- Prep recon: `.agent-work/epic-298/prep-299-report.md`.

## Budget

- **Model tier (required): Opus.** Cold panel mandatory (B0.4). Design-it-twice mandatory on the contract shape. Sub-dispatches at the least-powerful tier that works. **No Fable subagents at any tier — name the model explicitly on every dispatch.**
- At most 3 concurrent sub-dispatches. If a usage-limit reset is near, defer rather than launching into it. Rewrite your crash-resume state note before **each** detach.

## Stop Conditions

Stop and return when: scope would change; the design-it-twice convergence is ready (that one is human-only and must be surfaced); a two-bin routing question or pathway verdict arises; budget crossed; evidence impossible; **or you need context this order does not cover and cannot safely proceed without — return-and-query me, I answer and continue you.**

Asking up is always sanctioned and always legitimate. This epic has one logged Admiral error where a commander's float went unanswered and it merged on its own reading; that failure was mine. #299 floated twice, proceeded on its own recommendation while telling me what it was doing, and was right both times. That is the shape I want.

## Return Shape

Deliver your artifact and verdict **before** going idle — an idle notification with no artifact reads as stalled, not done.

1. **Verdict**: contract landed, or an honest null with what the evidence showed.
2. **Degraded mode demonstrated on a genuinely broken entrypoint** — and evidence the check **can fail**, by mutation.
3. **Deletions**, each with its filed tripwire episode id, **plus the outcome of actually running the affected workflows against it.** Deletion without the run is half the pathway.
4. **Trend snapshot** filed (corpus size / per-role surface, from git).
5. **The design-it-twice candidates and your convergence recommendation** — surfaced, not decided.
6. **Map impact** and **triage candidates** (filed to the tracker, numbers listed here).
7. **Workflow feedback** — what this order got wrong, what tooling made harder than necessary. Blunt is useful.
8. Your `verify_worktree_isolation.py --here` output.
9. **PR number and its CI check exit code, read at source.**
