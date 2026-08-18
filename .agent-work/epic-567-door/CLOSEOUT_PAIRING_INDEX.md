# Closeout pairing index — epic #567

**60 triage candidates** staged across nine lanes and the Admiral. Every one is a
committed markdown file on `main` with a full write-up, so **none is at risk** — this index
decides where each is *surfaced*, not whether it survives.

The standing ruling, in the human's words: *"keep track of the issues, but we've been ballooning
out tracking. let's hold on to them until the end then see if we can pair them with open issues,
anything else we can file under episodes."* **No candidate becomes a new issue.**

## Grouping decision
Posting one comment per candidate would mean **60 comments across ~12 issues** — which is the
ballooning the ruling exists to prevent, in a different shape. So candidates are grouped: **one
comment per target issue**, carrying every candidate paired to it with its path. ~12 comments.

## Pairings

### → #559
*6 candidate(s)*

- **[W1-A]** the spine template's `init` imperative asserts a binding that does not exist
  `.agent-work/567-a/triage-candidates/engine-init-imperative-asserts-a-false-binding.md`
- **[W1-A]** a hardlink defeats any path-based containment check
  `.agent-work/567-a/triage-candidates/hardlinks-defeat-path-based-containment.md`
- **[W2-D1]** Triage candidate — after the sweep, the corpus never names the door's binding call
  `.agent-work/567-d1/triage-candidates/corpus-never-names-the-doors-binding-call.md`
- **[W2-D1]** Triage candidate — `scripts/mcp_spine_server.py` carries a CLI-fallback sentence no walk reads
  `.agent-work/567-d1/triage-candidates/mcp-spine-server-cli-fallback-sentence.md`
- **[ADM]** a `fork` grandchild inherits its dispatcher's spine identity and drives its dispatcher's spine
  `.agent-work/epic-567-door/triage-candidates/tc1-fork-inherits-dispatcher-spine-identity.md`
- **[ADM]** the door cannot drive a Commander's child `execute.json` plan
  `.agent-work/epic-567-door/triage-candidates/tc5-the-door-cannot-drive-a-child-execute-plan.md`

### → #535
*4 candidate(s)*

- **[W1-A]** three bootstrap defects in the launch-order template
  `.agent-work/567-a/triage-candidates/launch-order-bootstrap-defects.md`
- **[ADM]** every launch order's first instruction requires a sticky `cd`, and an agent that cannot make one stick never reaches step one
  `.agent-work/epic-567-door/triage-candidates/tc3-launch-order-first-line-blocks-an-agent-that-cannot-cd.md`
- **[W2-F]** no Commander-level spec compilation into a spine
  `.agent-work/archive/2026-08-17-567-f/triage-candidates/commander-level-spec-compilation.md`
- **[W2-F]** ExternalBackend cannot go spine-only
  `.agent-work/archive/2026-08-17-567-f/triage-candidates/external-backend-spine-only.md`

### → #544
*4 candidate(s)*

- **[W1-A]** `map/ids.jsonl` is empty, so every run in this repo orients DEGRADED
  `.agent-work/567-a/triage-candidates/map-ids-jsonl-empty-repo-wide.md`
- **[W1-A]** `verify-frame` refuses the template it is paired with
  `.agent-work/567-a/triage-candidates/verify-frame-refuses-every-anchor-when-degraded.md`
- **[W2-D1]** map/ids.jsonl is empty, so map_orient can never RESOLVE in this repo
  `.agent-work/567-d1/triage-candidates/map-ids-jsonl-empty.md`
- **[W2-D1]** verify-frame and decision-grading cannot both be satisfied in a repo with no map
  `.agent-work/567-d1/triage-candidates/verify-frame-refuses-graded-decisions.md`

### → #369
*3 candidate(s)*

- **[W1-A]** record WHO wrote each spine journal entry
  `.agent-work/567-a/triage-candidates/write-provenance-on-spine-journal.md`
- **[W1-G]** a Commander cannot tell its own dispatched fork's writes from unauthorized tampering
  `.agent-work/567-g/triage-candidates/no-instrument-distinguishes-own-fork-writes-from-tampering.md`
- **[ADM]** nothing records who wrote what, so an agent cannot tell its own crew's writes from tampering
  `.agent-work/epic-567-door/triage-candidates/tc2-no-write-attribution-produces-false-tamper-reports.md`

### → #432
*2 candidate(s)*

- **[W1-B]** crew-backend-design spec Decision 2 is now stale
  `.agent-work/567-b/triage-candidates/tc1-crew-backend-design-doc-drift.md`
- **[W1-B]** consider mandatory `--spine` at dispatch time for ExternalBackend
  `.agent-work/567-b/triage-candidates/tc2-mandatory-spine-at-dispatch.md`

### → #561
*2 candidate(s)*

- **[W2-D1]** Triage candidate — `docs/agents/CREW_CONTEXT.md` "Python Invocation" is stale
  `.agent-work/567-d1/triage-candidates/crew-context-python-invocation-stale.md`
- **[ADM]** the mandated debt sweep reports "clean" on this host having read nothing
  `.agent-work/epic-567-door/triage-candidates/tc4-debt-sweep-roots-are-windows-paths-so-the-sweep-reports-clean-having-read-nothing.md`

### → #595
*2 candidate(s)*

- **[W1-C]** duplicated precedence prose
  `.agent-work/567-c/triage-candidates/tc1-duplicated-precedence-prose.md`
- **[W1-C]** #595's context-trip advisory wording is still unedited
  `.agent-work/567-c/triage-candidates/tc3-issue-595-advisory-wording-followup.md`

### → #613
*2 candidate(s)*

- **[W1-A]** #613's lost-update half remains after lane A's atomicity fix
  `.agent-work/567-a/triage-candidates/613-lost-update-half-remains.md`
- **[W1-A]** `_atomic_write_json`'s fixed temp name corrupts under two writers
  `.agent-work/567-a/triage-candidates/gauge-writer-hook-fixed-temp-name.md`

### → #495
*1 candidate(s)*

- **[W1-G]** subprocess-output comparisons decode with the wrong encoding on Windows CI (issue #495 family)
  `.agent-work/567-g/triage-candidates/newline-sensitive-byte-identity-assertions-windows-ci.md`

### → #522
*1 candidate(s)*

- **[W1-C]** #522's pin-test pattern reproduced live
  `.agent-work/567-c/triage-candidates/tc4-issue-522-pin-test-pattern.md`

### → #541
*1 candidate(s)*

- **[W2-E]** `checklist_engine.py`'s own `refusals` counter never sees a door-own rejection
  `.agent-work/archive/2026-08-17-567-e/triage-candidates/engine-refusals-counter-blind-to-door-own-rejections.md`

### → #565
*1 candidate(s)*

- **[W2-D2]** verify corpus-wide pointers into workbench's shrunk docs once every wave-2 lane merges
  `.agent-work/archive/2026-08-17-567-d2/triage-candidates/3-corpus-wide-pointers-into-shrunk-workbench-docs.md`

### → #575
*1 candidate(s)*

- **[W1-A]** the test proving a platform fallback could not run on that platform
  `.agent-work/567-a/triage-candidates/a-guard-test-that-cannot-run-where-the-guard-is-needed.md`

### → #615
*1 candidate(s)*

- **[ADM]** an Admiral spine can lose its lease mid-run, and nothing surfaces it
  `.agent-work/epic-567-door/triage-candidates/tc7-an-admiral-spine-can-lose-its-lease-mid-run-and-nothing-says-so.md`

### → EPISODE
*26 candidate(s)*

- **[W1-A]** the door's `main()` catches only `KeyError`, so any other raise kills it
  `.agent-work/567-a/triage-candidates/door-main-catches-only-keyerror.md`
- **[W1-A]** "mutate then restore" is an unsafe instruction to give a crew
  `.agent-work/567-a/triage-candidates/mutate-a-copy-never-the-tracked-file.md`
- **[W1-A]** `subTest` can report PASSED while the test body raises
  `.agent-work/567-a/triage-candidates/subtest-hides-a-raising-test-body.md`
- **[W1-B]** episode imperative-detector cannot tell a homograph from an instruction
  `.agent-work/567-b/triage-candidates/tc3-imperative-detector-homograph-allowlist-growth.md`
- **[W1-G]** minor duplication in two closeout primitives (Fowler, non-blocking)
  `.agent-work/567-g/triage-candidates/duplicated-code-in-advance-release-and-release-child-plans.md`
- **[W1-G]** reviewer's r6-fowler survey template breaks on nested work-ids
  `.agent-work/567-g/triage-candidates/reviewer-fowler-template-work-id-substitution-bug.md`
- **[W2-D1]** Triage candidate — a test that fails only when the suite is run from inside a dispatched crew
  `.agent-work/567-d1/triage-candidates/crew-launcher-scratch-dir-test-fails-inside-a-crew.md`
- **[W2-D1]** Triage candidate — the crew skills state a norm that is the exception for this dispatch shape
  `.agent-work/567-d1/triage-candidates/dispatched-crew-spine-is-not-bound.md`
- **[W2-D1]** Doctrine prose asserts facts owned by the commander spine, with nothing tying the two together
  `.agent-work/567-d1/triage-candidates/doctrine-asserts-spine-postconditions-with-no-tie.md`
- **[W2-D1]** docs/agents/engine-config.json is referenced by three files and does not exist
  `.agent-work/567-d1/triage-candidates/engine-config-json-absent.md`
- **[W2-D1]** execute.json duplicates each gate's anchors block byte-identically across its triad
  `.agent-work/567-d1/triage-candidates/execute-json-anchors-duplicated-per-task.md`
- **[W2-D1]** `CONSTELLATION_FEEDBACK.template.md` still claims a writer that no gate contains
  `.agent-work/567-d1/triage-candidates/feedback-export-template-claims-a-writer-that-is-gone.md`
- **[W2-D1]** Triage candidate — the Fowler record path is per-work-id, so a second reviewer overwrites the first gate's audit evidence
  `.agent-work/567-d1/triage-candidates/fowler-record-path-collides-across-gates.md`
- **[W2-D1]** GLOSSARY.md has no entry for "door", the term this epic makes load-bearing
  `.agent-work/567-d1/triage-candidates/glossary-has-no-door-entry.md`
- **[W2-D1]** A headless `claude -p` launched inside a lane worktree inherits that lane's spine and Stop hook
  `.agent-work/567-d1/triage-candidates/headless-dispatch-inherits-parent-spine.md`
- **[W2-D1]** Triage candidate — the `.agent-work/templates/.baseline/` mirror doubles every doctrine target, with no named reconciler
  `.agent-work/567-d1/triage-candidates/overlay-baseline-mirror-doubles-every-target.md`
- **[W2-D1]** Triage candidate — `set -o pipefail` in an engine `command` check cannot pass on POSIX
  `.agent-work/567-d1/triage-candidates/pipefail-in-command-checks-cannot-pass.md`
- **[W2-D1]** Skill prose names bundled scripts by a repo-relative path, 91 sites across 27 files
  `.agent-work/567-d1/triage-candidates/prose-names-vendored-script-paths-corpus-wide.md`
- **[W2-D1]** Triage candidate — `TEMPLATES_MANIFEST.json` is a fourth copy of template truth
  `.agent-work/567-d1/triage-candidates/templates-manifest-is-a-fourth-copy.md`
- **[W2-D1]** Triage candidate — the standard whole-suite evidence command is unsafe to run while driving the engine
  `.agent-work/567-d1/triage-candidates/whole-suite-evidence-is-unsafe-during-engine-drive.md`
- **[ADM]** a dispatched crew's own environment reds a test it never touched
  `.agent-work/epic-567-door/triage-candidates/tc6-crew-env-leaks-into-the-suite-and-reds-a-test-the-crew-did-not-touch.md`
- **[W2-D2]** test_crew_launcher.py scratch-dir test leaks CREW_SCRATCH_DIR from caller env
  `.agent-work/archive/2026-08-17-567-d2/triage-candidates/1-crew-launcher-scratch-dir-env-leak.md`
- **[W2-D2]** a real (non-dry-run) install_constellation.py invocation mutates the CALLING repo's own .mcp.json regardless of --dest
  `.agent-work/archive/2026-08-17-567-d2/triage-candidates/2-install-constellation-mutates-caller-mcp-json.md`
- **[W2-D2]** install_constellation.py has no supported "templates-only, no taught procedure" skill state
  `.agent-work/archive/2026-08-17-567-d2/triage-candidates/4-first-class-retired-skill-installer-state.md`
- **[W2-E]** second-person `TOOLS` descriptions silently skip episode capture
  `.agent-work/archive/2026-08-17-567-e/triage-candidates/second-person-tool-descriptions-skip-capture.md`
- **[W2-H]** a zero-framed Agent-tool subagent will discover and drive its dispatcher's own live engine state, under the dispatcher's own identity, indistinguishably from the dispatcher itself
  `.agent-work/archive/2026-08-17-archive-2026-08-17-567-h/triage-candidates/tc-rogue-cold-subject.md`

### → HUMAN
*2 candidate(s)*

- **[W1-G]** wire finish_work as an actual spine_done MCP tool
  `.agent-work/567-g/triage-candidates/wire-finish-work-as-mcp-tool.md`
- **[ADM]** model tier should be a per-role default with an allowed set, not an inherited value
  `.agent-work/epic-567-door/triage-candidates/tc8-model-tier-should-be-a-per-role-default-with-an-allowed-set-not-an-inherited-value.md`

### → RESOLVED
*1 candidate(s)*

- **[W1-C]** #442's target text is fenced to a concurrent lane
  `.agent-work/567-c/triage-candidates/tc2-issue-442-fenced-out.md`

