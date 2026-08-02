# Viewpoint reports — issue #309, g2-dispatch (verbatim)

Both dispatched Sonnet, general-purpose agent, whole-slice (Candidate B design), doctrine
pasted inline (all 4 seeded corpus-slice files pasted in full into each prompt), no skill
invocation relied upon. Reports below are the verbatim agent output, unedited.

## Viewpoint A — Contradiction Auditor

> ## Contradiction Audit Findings
>
> **1. triage-copy.md — internal contradiction over whether Triage uses the checklist engine**
>
> - Statement A (top of doc, under the header): *"**No checklist. Work through the candidates directly.**"*
> - Statement B (Gate Discipline section): *"Every candidate must first clear `checklist_engine.py`'s gated sequence — claim, current, attest, advance — before it may be routed to `fixed-now`, `filed`, or `recommend-and-defer`; a routing decision made outside the engine's own gate sequence is not recorded and does not count as triaged."*
>
> These govern the same fact — does triaging a candidate require passing through `checklist_engine.py`'s gated sequence? Statement A flatly says there is no checklist and candidates are worked directly; Statement B says every candidate must clear a specific gated engine sequence before it can even be routed, and that skipping the engine means the work "does not count as triaged." A reader following the top-level instruction would never invoke the engine at all, violating Gate Discipline.
>
> **2. episode-store-excerpt-copy.md — internal contradiction over whether retired-episode content is ever removed**
>
> - Statement A (Policy, bullet 1): *"Retirement means **excluded from ordinary rhyme-search, RETAINED in history.** Never deletion, never truncation."* Reinforced later: *"The episode's **content** is never deleted or truncated by retirement."*
> - Statement B (Policy, last bullet): *"As a storage-hygiene measure, once an episode has been retired for more than 90 days its agent-supplied assertion bodies are cleared to keep the archive lean, leaving only the mechanical fields and the retirement block intact."*
>
> Both are in the same "Policy (settled — stated here)" list governing the same entity (a retired episode's stored content). Statement A asserts an absolute guarantee that content is never deleted or truncated. Statement B describes exactly that: agent-supplied assertion bodies — content — being cleared/removed after 90 days, leaving only a subset of fields. "Cleared... leaving only the mechanical fields" is a truncation/deletion of the assertion bodies, directly at odds with "never deletion, never truncation."
>
> **3. triage-copy.md vs curator-copy.md — contradiction over whether Triage implements Route candidates**
>
> - triage-copy.md: *"Triage does not implement, keep backlog, or pull work into current scope unless asked."* Its own Fix-Now Eligibility Ladder further restricts self-implementation to bounded, adjacent, verifiable, non-structural work: *"No architecture/production-default impact — structural changes still route through reconcile; fix-now never carries one."*
> - curator-copy.md (Route section): *"Route hands the flagged candidate to Triage, which implements the recommended fix directly before the candidate is closed out."*
>
> Curator's Route step exists specifically for design decisions ("move doctrine to `_shared`, re-scope or kill a section, change a budget") — i.e., structural/architectural changes. By triage's own ladder, structural changes can never be `fixed-now` and thus Triage would never implement them itself; it would only produce a `filed` or `recommend-and-defer` recommendation. Curator's claim that Triage "implements the recommended fix directly" for these routed candidates conflicts both with Triage's general "does not implement... unless asked" posture and with the specific ladder rung that excludes structural changes from self-implementation.
>
> No contradictions were found involving debt-cadence-copy.md — its policies (dry-run-by-default, human-gated `--confirm`, session-scoped cron caveats) are self-consistent and don't overlap in subject matter with the other three documents.

## Viewpoint B — Drift Auditor

> ## Drift Audit Findings
>
> **1. Triage's role: "implements" vs "does not implement"**
> - File: `triage-copy.md` — "Write issue-ready recommendations for follow-up work. **Triage does not implement**, keep backlog, or pull work into current scope unless asked."
> - File: `curator-copy.md` — "Route hands the flagged candidate to Triage, **which implements the recommended fix directly** before the candidate is closed out."
> - Disagreement: Triage's own document states it does not implement work (absent an explicit ask); Curator's document asserts, as a stated fact about Triage's behavior, that Triage implements the fix directly.
>
> **2. Triage gate discipline: engine-gated vs "no engine checklist" precedent**
> - File: `curator-copy.md`, Mend section — "**No engine checklist — a fixed linear pass** (the triage precedent): work the flagged rows directly."
> - File: `triage-copy.md`, Gate Discipline section — "Every candidate must first clear `checklist_engine.py`'s gated sequence — claim, current, attest, advance — before it may be routed to `fixed-now`, `filed`, or `recommend-and-defer`."
> - Disagreement: Curator cites Triage as the *precedent* for skipping the engine checklist in favor of a fixed linear pass, but Triage's own document states every candidate must clear `checklist_engine.py`'s gated sequence before being routed.
>
> **3. Dogfood roots: three declared, two used in every invocation example**
> - File: `debt-cadence-copy.md`, "Dogfood project roots" — lists three repos: f1Brainz, network_elo, story_time — "This list is durable and expected to grow."
> - File: `debt-cadence-copy.md`, "Sweep invocation" — all three example commands use only f1Brainz and story_time.
> - Disagreement: `network_elo` is declared part of "the current set of consuming repos swept for feedback" but is omitted from every single worked invocation in the same document.
>
> **4. "Never deletion, never truncation" vs. clearing assertion bodies after 90 days**
> - File: `episode-store-excerpt-copy.md`, Policy bullet — "Retirement means excluded from ordinary rhyme-search, RETAINED in history. **Never deletion, never truncation.**" (restated: "content... never deleted or truncated by retirement.")
> - File: `episode-store-excerpt-copy.md`, same section — "once an episode has been retired for more than 90 days its **agent-supplied assertion bodies are cleared**... leaving only the mechanical fields."
> - Disagreement: absolute retention claim vs. described clearing of assertion bodies after 90 days.
>
> **Lower-confidence, out-of-slice reference (not claimed as confirmed):**
> - `episode-store-excerpt-copy.md` references "continuing `governor-268-003` from §3" and "(§6)" — these sections aren't included in the slice, so I can't verify the worked example is actually consistent with whatever §3/§6 say elsewhere in the source document.
>
> No other enumerated lists, counts, or identifiers... showed disagreement between their declaration and their usage.

## Supplementary instrument-validation probe (noise/false-positive demonstration)

Neither viewpoint above took the DECOY1 bait (the real, unmodified "No checklist" vs.
"Drive every step through the checklist engine" pairing) — both correctly distinguished
it from a genuine defect. That is informative but leaves `decision:prove-the-miss`'s
NOISE half undemonstrated (no actual false positive was produced to then reject). A
third, explicitly-labeled, low-bar "fast pattern-matcher" probe was dispatched against
DECOY1's two quotes ALONE (not the full slice, not a scope expansion — an instrument
validation exercise, not a third sweep viewpoint) to test whether the sweep pathway CAN
produce a false positive when a lens is deliberately made less careful:

> YES — these contradict on their surface wording. Statement A explicitly says "No
> checklist," directing Triage to work candidates directly without one. Statement B
> mandates the opposite: every step must be "driven through the checklist engine"...
> Even though they come from different documents (Triage vs. Curator) and may govern
> different workflows, the direct clash in phrasing... is a clear surface-level
> inconsistency that should be flagged.

This IS a false positive: the probe's own text acknowledges "may govern different
workflows" yet still flags it as a contradiction, ignoring GROUND_TRUTH.json's stated
criterion (no doctrine requires uniform tooling across skills). Scored and rejected at
g3-score as noise, demonstrating the reject half of decision:prove-the-miss.
