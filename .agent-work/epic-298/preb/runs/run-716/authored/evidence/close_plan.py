import subprocess, sys

ENGINE = r"C:\Users\fredc\.claude\skills\constellation-commander\scripts\checklist_engine.py"
FILE = ".agent-work/issue-716/spine.json"
SESSION = "commander-issue-716"


def eng(*args):
    r = subprocess.run([sys.executable, ENGINE, "--file", FILE, *args, "--session-id", SESSION],
                       capture_output=True, text=True, encoding="utf-8")
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    lines = [ln for ln in out.splitlines() if ln.strip() and not ln.startswith("RAIL:")]
    print(f"[{r.returncode}] " + " | ".join(lines[-2:]))


eng("attest", "plan", "--which", "postconditions", "--cond", "c1", "--note",
    "Mission frame authored at .agent-work/issue-716/MISSION_FRAME.md. NOT skipped as trivial: the "
    "change is small in lines but crosses a distribution boundary with a documented silent-drift "
    "precedent. The target repo (constellation-skills) has no Cartographer packet map, so the frame is "
    "written against source structure (line-numbered, re-verifiable) plus docs/RECURSIVE_IMPROVEMENT_"
    "DESIGN.md, per the commander doctrine's no-packet-map path. Map-confidence section records that "
    "LESSONS.md:373 was treated as a lead and re-verified, and found to UNDER-report the blast radius.")

eng("attest", "plan", "--which", "postconditions", "--cond", "c2", "--note",
    "execute.json authored: e0-context + 3 crew gates (G1 shared helper / G2 distribution / G3 "
    "adoption), each with implement/review/integrate, each carrying an anchors block cut from the "
    "frame. Ownership scope enumerated against the gates before freezing: work_id.py + test_work_id.py "
    "-> G1; install_constellation.py + test_install_constellation.py -> G2; run_crew.py, "
    "verify_agent_feedback.py, test_crew_launcher.py, test_verify_agent_feedback.py, "
    "RECURSIVE_IMPROVEMENT_DESIGN.md -> G3. All four decision classes have a gate; the one unresolved "
    "choice is carried as a user-decision postcondition (g2-integrate c3), not buried in a handoff. "
    "Gate ORDER is load-bearing: test_bundled_scripts_carry_their_sibling_imports compares against the "
    "bundle, so distribution must precede the first import or the G2/G3 boundary is knowingly red. "
    "Check commands verified by running them: full suite 1160 passed / 1 skipped / 45s on 2026-08-01.")

eng("attest", "plan", "--which", "postconditions", "--cond", "c4", "--note",
    "Plan-alternatives RUN, recorded at .agent-work/issue-716/PLAN_ALTERNATIVES.md: three candidates "
    "under distinct constraints (A distribution-before-use one-concern-per-gate; B defect-per-gate "
    "partial-land; C single gate minimum ceremony), compared on seam placement / locality / "
    "testability / red-window risk / review depth on the historically-drifting concern, converging on "
    "A with two named grafts (from B: all three call sites adopt in ONE gate so the seam has two "
    "adapters before it is blessed; from C: no separate gate for the doc line). UNTAKEN ROAD, named: "
    "independent parallel-subagent authorship — this engagement carries a standing instruction not to "
    "dispatch subagents, so the candidates were authored serially in one context and may share a blind "
    "spot.")

eng("attest", "plan", "--which", "postconditions", "--cond", "c5", "--note",
    "Cold plan critic RUN in the same artifact: six findings, five accepted, one rejected with reason. "
    "Three changed the spec materially — F2 narrowed the parser's back-compat fallback so a malformed "
    "session name cannot silently resolve to a plausible-but-wrong work-id; F4 CORRECTED the "
    "_entry_block tie-break, which as first drafted ('prefer the longest match') returned the CHILD "
    "entry for a parent id, inverting the very bug being fixed; F5 added a real-corpus measurement over "
    "both AGENT_FEEDBACK.md files so 'strictly widening' is measured rather than argued. F1 replaced "
    "G2's 'tests pass' with a positive install proof plus a deferred falsification, because the guard "
    "passes vacuously at that gate. UNTAKEN ROAD, named: a context-free critic and a 3-lens panel — "
    "the same no-subagent instruction applies, so this pass is adversarial-by-discipline, not "
    "adversarial-by-construction. Panel-vs-single choice surfaced in the artifact: single, because the "
    "one load-bearing interface choice is settled by the issue text itself. A fresh cold read remains "
    "the cheapest available hardening before implementation.")

eng("attach", "plan", "--type", "user-decision",
    "--field", "cite=ENGAGEMENT_BRIEF:standing-delegation",
    "--field", "frame=.agent-work/issue-716/MISSION_FRAME.md",
    "--field", "plan=.agent-work/issue-716/execute.json",
    "--field", "alternatives=.agent-work/issue-716/PLAN_ALTERNATIVES.md",
    "--field", "statement=Plan approved by the Commander under the engagement's standing delegation "
               "(no human reachable). What would have been asked at this checkpoint, and how it was "
               "decided: (1) three gates or two? -- three, because distribution is the one concern with "
               "a documented silent-drift precedent in this repo and it needs its own review lens; "
               "(2) is the unnamed _entry_block instance in scope? -- yes, bounded to a strictly-"
               "widening exact-match-preferred rule, because deferring the same root cause in the same "
               "file guarantees a third waive; (3) companion-wiring vs hand-added bundle literals? -- "
               "NOT self-decided: it edits an existing guard test, so it is carried FORWARD as an open "
               "user-decision postcondition at g2-integrate c3; (4) accept a non-independent critic? -- "
               "yes, with the limitation named as an untaken road rather than hidden. The engagement "
               "stops here: execute is out of scope.")
