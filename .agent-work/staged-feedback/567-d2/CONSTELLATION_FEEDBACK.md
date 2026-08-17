# Constellation Feedback Export

## 2026-08-17 — constellation-skills — 567-d2

- **Episode:** 567-d2-001
- **Candidate:** door-schema-vs-cross-reference-doctrine-gap
- **Observed:** An MCP door tool's own description teaches its verb's mechanism well, but it cannot teach meta-doctrine *about* the door itself (e.g. "the door is the default while the CLI stays available," or a dispatched-subagent routing rule) — that class of content has no home except a reference file, and a mission framed as "the door now teaches this, delete the doc" can be wrong specifically for that class.
- **Cost:** A launch order's per-file line-count deliverable (289 lines to delete) was not achievable in full; required a mid-run plan revision after understand-phase investigation, though caught before any file was edited.
- **Proposal:** When authoring a "the tool now teaches this, retire the doc" mission, name the two content classes separately up front (verb/mechanism content vs. meta-doctrine-about-the-tool content) so the retiring agent isn't left to discover the split via test-suite archaeology.
- **Grounding:** tests/test_mcp_adoption.py:894-1030 (TestTier3ChecklistEngineReference); .agent-work/567-d2/MISSION_FRAME.md §"Claims / Evidence Surfaces"
- **Template vintage:** n/a
- **Confidence:** medium

## 2026-08-17 — constellation-skills — 567-d2

- **Episode:** 567-d2-002
- **Candidate:** handoff-byte-exact-constraint-needs-spec-file-discipline
- **Observed:** A Commander-authored "apply this spec verbatim" handoff is only as byte-exact as the spec file itself; writing the spec from memory/paraphrase (rather than copy-pasting from the real source) silently reintroduces the exact defect the "byte-exact" instruction exists to prevent, and a mechanical test suite that only pins substrings (not full text) will not catch it — only an independent reviewer's direct byte-comparison will.
- **Cost:** One extra review round to catch and fix.
- **Proposal:** For any handoff instructing byte-exact retention of existing prose, generate the spec's retained blocks by mechanical extraction (script/grep a byte range) rather than hand-authoring/copy-typing them, removing the paraphrase risk at the source.
- **Grounding:** .agent-work/567-d2/crew-handoffs/g1-review-reviewer-result.md:120-130
- **Template vintage:** n/a
- **Confidence:** high

## 2026-08-17 — constellation-skills — 567-d2

- **Episode:** 567-d2-003
- **Candidate:** full-suite-catches-what-targeted-files-cannot
- **Observed:** A doc-content deletion scoped and verified against the 2-3 test files most obviously about that doc left a real regression undetected (tests/test_retirement_guard.py's approved-mentions census, an entirely unrelated doctrine pinned to an exact line in the same source file) until the full-suite-in-a-clean-worktree gate ran.
- **Cost:** Would have shipped a merge-breaking regression if the full-suite gate had been treated as redundant with the targeted-file verification already done.
- **Proposal:** No change needed to doctrine — this is exactly why the full-suite-in-a-detached-worktree gate is non-negotiable even after targeted tests are green; recording as confirming evidence for that existing rule, not a gap to close.
- **Grounding:** tests/test_retirement_guard.py::test_every_approved_entry_exists_verbatim; tests/data/store_mentions.approved.txt:166
- **Template vintage:** n/a
- **Confidence:** high

## 2026-08-17 — constellation-skills — 567-d2

- **Episode:** 567-d2-004
- **Candidate:** install-constellation-real-run-mutates-caller-mcp-json
- **Observed:** Running `scripts/install_constellation.py` without `--dry-run` mutates the *calling* repo's own `.mcp.json` (interpreter-command probe rewrite) regardless of where `--dest` points — surprising when the invocation's purpose is only to inspect an installed skill copy elsewhere.
- **Cost:** An unintended working-tree change that had to be caught by `git status` and reverted before commit; would have polluted the diff if missed.
- **Proposal:** Scope the `.mcp.json` wiring probe to the `--dest` tree, or require an explicit flag (e.g. `--wire-mcp-here`) to touch the caller's own `.mcp.json`, so a verification-only install invocation is side-effect-free by default.
- **Grounding:** .agent-work/567-d2/triage-candidates/2-install-constellation-mutates-caller-mcp-json.md
- **Template vintage:** n/a
- **Confidence:** medium
