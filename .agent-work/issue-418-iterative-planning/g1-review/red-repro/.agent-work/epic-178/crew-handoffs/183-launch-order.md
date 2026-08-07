# Launch Order: implementer — issue #183 (Refresh: reach-up flow + job-file principle) — Wave 1 — HITL

You are an implementer dispatched by the Admiral running epic-178 (Context Governor v1). You start cold; everything you need is pasted here. Do NOT open other issues. #179 is MERGED to main — build on its primitives as they actually shipped (below). HITL: the acceptance is a qualitative human judge (symmetric-recovery drill) — build to that seam; the human signs off.

## Mission
Implement issue #183 — the reach-up Refresh flow (Module 4), built on #179's engine primitives. Wire the uniform reach-up mechanism into the tier skills' doctrine and encode the **job-file-not-agent-file** principle. Deliverable: the doctrine wiring (skill `.md` edits), a reproducible symmetric-recovery **drill** (so the qualitative judge can be exercised), and a result artifact framing the human sign-off.

## Prior-Wave Verdicts (pasted — real merged interfaces)

**From #179 (MERGED, in `scripts/checklist_engine.py`):**
- `refresh-request` — an evidence type written via the existing `attach` verb, payload = pointers only (`seam`, `why_ref`). Example shape the agent writes: `attach <gate> --type refresh-request --field seam=<active-gate-id> --field why_ref=<latest-why-record-id>`.
- `has_pending_refresh_request(cl, gate)` — pure predicate (bool). "Pending" = a refresh-request present and NOT superseded. It does NOT yet mark a request *fulfilled* — #179's author explicitly flagged that YOU (#183) own the consume/fulfil semantics: you can extend the predicate or supersede the evidence to clear a request once the fresh agent has picked it up. Decide and document how a fulfilled request is cleared so a relaunched agent doesn't re-trip.
- `why_trail` is top-level append-only; the live DIGEST is the latest non-mechanical `why`, surfaced as a `DIGEST:` line on `current`. A `REFRESH REQUESTED:` line appears on `current` when a pending refresh-request exists for the active gate. Cold-start reads `current` alone: `DIGEST:` + `ACTIVE <gate> — <imperative>`.
- Why-record ids are `w-N` (sequential); `why_ref` points at one.

**Note on #182 (Trip):** Trip is being built in a sibling worktree this same wave. Its HARD band will call `has_pending_refresh_request` and refuse advance until a refresh-request exists. You do NOT need Trip to land first — you wire the DOCTRINE/FLOW around the same #179 primitives. If the spec is silent on an interaction between your fulfil-semantics and Trip's HARD gate, float it to the Admiral.

## Frozen build spec (authoritative)
- **Uniform reach-up mechanism, one at every tier:** on a soft-accepted or hard-forced trip, the agent writes a `refresh-request` (via #179's `attach`; payload = pointers `seam`+`why_ref`, never copies) into its OWN engine work file, then goes idle. The **invoker sees it via `current`** when inspecting the invokee's engine state, and relaunches a **fresh** agent that cold-starts from **`current` alone** (`DIGEST:` + `ACTIVE <gate> — <imperative>`) — NO heavyweight handoff document, NO `REFRESH_HANDOFF.md`.
- **Reach-up chain:** Commander→implementer/reviewer; Admiral→Commander; human at the top. The same `current` read at every tier.
- **Job-file-not-agent-file principle (encode in doctrine):** engine work files (`spine.json`, plan, `why_trail`) are **job-scoped, not agent-scoped** — a relaunched agent **reuses the same file**. Agents are ephemeral; the job file persists; refresh = swap the agent, keep the file. This also grounds #179's append-only `why_trail` across agent changes.
- **Symmetric recovery:** intentional refresh and crash-resume read from the **identical `current`** (crash = the refresh-request line simply absent → fall back to today's cold-start). The handoff never re-serializes engine state (pointers only).
- **CUT / OUT OF SCOPE (do NOT build):** crew-edge extra robustness (SF4 cut); pi self-refresh adapter (dropped until pi work is real); the deferred pre-emptive-handoff-at-specific-gates idea.

## Acceptance — QUALITATIVE HUMAN JUDGE (not a unit test; named as such per spec TF4)
The **symmetric-recovery drill**: an intentional refresh AND a simulated crash both resume from the identical `current` read, and the fresh agent completes **without re-deriving the why** the trail already holds. A human adjudicates "did the fresh agent resume from `current` and complete without re-deriving the why?" — this is why the issue is HITL.
- **Your job:** make this drill **reproducible and cheap for the human to judge** — a scripted or clearly-documented scenario (a spine with a `why_trail`, a refresh-request attached, a fresh cold-start from `current`) plus a crash-variant (same, refresh-request absent), so the human can run/read it and render the judgment. Do NOT self-certify the qualitative judge; frame it for the human.

## Pre-Rulings (overridable only if evidence contradicts — say so if you override)
- **File fence:** edit the tier-skill doctrine `.md` files (the reach-up + job-file principle belongs where the tiers read it — global doctrine references and/or per-tier skill docs) and add the drill artifact. Do NOT edit `checklist_engine.py` (that's #182) or the gauge modules. Identify the exact doctrine homes and list them in your result for Admiral review before finalizing.
- Depends on #179 merged. Reuse its primitives exactly as merged.
- Doctrine edits are load-bearing text a human ratifies — draft them faithfully to the spec; the Admiral/human signs off (HITL). Flag any place the spec is silent on WHERE a rule should live rather than guessing.

## Honest-Null Clause
A measured negative (e.g. "the cold-start from `current` alone is insufficient because X") is a complete, successful deliverable — report it with full rigor; it may be the most valuable finding.

## Inherited Latitude
Frozen spec. Float to the Admiral: any doctrine-home ambiguity, any interface mismatch with #179 as merged, any spec silence affecting where a rule lives.

## Workspace
Your worktree: **C:/Programs/constellation-wt-183** (branch `epic178-183-refresh`, base `e2b8005` = post-Wave-0 main with #179+#181+#180 merged, provisioned via `git worktree add C:/Programs/constellation-wt-183 -b epic178-183-refresh e2b8005`).
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-183` — must exit 0; paste output.
PR integration is server-side merge; you just open the PR.
NOTE ON DOCTRINE HOMES: the tier-skill doctrine lives under `skills/<role>/` (e.g. `skills/commander/`, `skills/admiral/`, `skills/implementer/`, `skills/reviewer/`) and shared/global doctrine under `skills/<role>/references/global-*.md`. The reach-up + job-file principle is cross-tier — identify the exact home(s), LIST them in your result for Admiral review, and float if unsure where a rule belongs. Do NOT touch `scripts/checklist_engine.py` (that's #182) or the gauge modules.

## Inherited Context (platform invariants)
- Windows box. If you add a drill script, make it runnable with `py`. PR body via temp file + `gh pr create -F <file>`.
- Set `PYTHONIOENCODING=utf-8` in captured-subprocess child envs.

## Budget
- **Model tier:** Sonnet (doctrine drafting + drill; the hard part is the human judgment, not volume).

## Stop Conditions
Stop and return on doctrine-home ambiguity, interface mismatch, spec contradiction, or the qualitative seam (which the human owns). Return-and-query the Admiral.

## Return Shape
Write result to **C:/Programs/constellation-skills/.agent-work/epic-178/crew-handoffs/183-result.md** (MAIN checkout path) BEFORE going idle: verdict + summary; `--here` output; the list of doctrine files edited (for Admiral/human review); the reproducible symmetric-recovery drill (how to run/read it) framed for the human's qualitative sign-off; diffstat; PR URL; any floats/map-impact/triage.
