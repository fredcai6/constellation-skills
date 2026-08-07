#!/usr/bin/env python
"""Verify the #440 two-arm acceptance EVIDENCE. It does NOT re-run the arms.

Exit 0 only if the captured evidence is complete and self-consistent. Exit 1 on
anything missing or contradictory, naming every failure.

Written so it CAN fail: every check below is a real comparison against a file on
disk, and truncating or contradicting any evidence file makes it exit non-zero.
See `--selftest`, which proves that on a deliberately damaged copy.

    python verify_evidence.py            # check evidence/
    python verify_evidence.py --dir X    # check a copy
    python verify_evidence.py --selftest # prove it fails on truncated evidence
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DIR = HERE / "evidence"

# The single differing file the two arms are allowed to have. Anything else in
# the recursive diff means the arms were not a controlled comparison.
ONLY_DIFF = "spine_rail.py"

# Read from scripts/gauge_reader.py `_PROFILES` at the time of the run. Kept as
# a literal so this checker never imports the code under test -- an evidence
# checker that asks the implementation what to expect cannot contradict it.
HARD_FRACTION = {
    "claude-opus-5": 150_000 / 1_000_000,
    "claude-opus-4-8": 150_000 / 1_000_000,
    "claude-sonnet-5": 150_000 / 1_000_000,
    "claude-fable-5": 150_000 / 1_000_000,
    "claude-haiku-4-5-20251001": 140_000 / 200_000,
}


class Checker:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.notes: list[str] = []

    def ok(self, cond, msg: str) -> bool:
        if cond:
            self.notes.append("PASS  " + msg)
            return True
        self.failures.append(msg)
        self.notes.append("FAIL  " + msg)
        return False


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def check_arm_diff(c: Checker, d: Path) -> None:
    p = d / "arm-diff.txt"
    if not c.ok(p.is_file(), "arm-diff.txt present"):
        return
    lines = [x for x in p.read_text(encoding="utf-8").splitlines()
             if x.strip() and not x.lstrip().startswith("#")]
    differ = [x for x in lines if " differ" in x or x.startswith("Only in")]
    c.ok(len(differ) == 1,
         "recursive scripts/ diff names exactly one differing file (found {0}: {1})".format(
             len(differ), differ))
    if differ:
        c.ok(ONLY_DIFF in differ[0],
             "the one differing file is {0} ({1})".format(ONLY_DIFF, differ[0].strip()))


def check_settings_differ_only_in_hook_path(c: Checker, d: Path) -> None:
    t = load(d / "settings-treatment.json")
    k = load(d / "settings-control.json")
    if not c.ok(t is not None and k is not None,
                "both arms' settings files present and parseable"):
        return

    def strip_hooks(s):
        s = json.loads(json.dumps(s))
        s.pop("hooks", None)
        return s

    c.ok(strip_hooks(t) == strip_hooks(k),
         "the two settings files are identical apart from their hooks block")

    def cmds(s):
        out = []
        for entry in ((s.get("hooks") or {}).get("PostToolUse") or []):
            for h in entry.get("hooks") or []:
                out.append((entry.get("matcher"), h.get("command")))
        return out

    tc, kc = cmds(t), cmds(k)
    c.ok(len(tc) == len(kc) == 2, "each arm wires exactly two PostToolUse hooks")
    c.ok([m for m, _ in tc] == [m for m, _ in kc],
         "hook matchers are identical across arms")
    if len(tc) == 2:
        c.ok("spine_rail.py" in (tc[0][1] or "") and "gauge_writer_hook.py" in (tc[1][1] or ""),
             "spine_rail.py is wired AHEAD of gauge_writer_hook.py")
        c.ok("/treatment/" in (tc[0][1] or "") and "/control/" in (kc[0][1] or ""),
             "each arm's hook command points at its OWN arm tree")
    # Every difference between the two settings files must be a hook path.
    diffs = [(a, b) for a, b in zip(tc, kc) if a != b]
    c.ok(all("treatment" in (a[1] or "") and "control" in (b[1] or "")
             for a, b in diffs) and len(diffs) == 2,
         "the ONLY difference between the arms is the absolute hook path")


def _fill_over_hard(record) -> tuple[bool, str]:
    if not isinstance(record, dict):
        return False, "no record"
    model = record.get("model")
    fill = record.get("fill_fraction")
    hard = HARD_FRACTION.get(model)
    if hard is None:
        return False, "model {0!r} is not in the calibration table".format(model)
    if not isinstance(fill, (int, float)):
        return False, "fill_fraction is not a number"
    return float(fill) >= hard, "fill {0:.4f} vs hard {1:.4f} for {2}".format(
        float(fill), hard, model)


def _under(path: str | None, root: str | None) -> bool:
    """Is `path` inside `root`? Both are Windows absolute paths as recorded."""
    if not path or not root:
        return False
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except (ValueError, OSError):
        return False


def check_binding(c: Checker, arm_name: str, a: dict, expect: str) -> None:
    """Where did the BINDING land? -- the fact the whole claim rests on.

    g2-review finding F1: this was the worst of eight silent-pass holes. Without
    it a treatment arm whose binding pointed at the sandbox MAIN -- i.e. the #440
    defect NOT fixed -- still exited 0, because the arm checks only ever read the
    gauge paths and never the binding that produced them. `path_source` was
    asserted for the preflight alone, though it is the single most load-bearing
    fact in the result: it is what says the hook DERIVED the worktree root from
    `git worktree list` rather than being handed it.

    `expect` is "wt" (the fix works) or "main" (the defect reproduces).
    """
    sb = a.get("sandbox") or {}
    entries = a.get("binding_entries") or []
    if not c.ok(bool(entries),
                "{0}: the binding store recorded at least one entry".format(arm_name)):
        return

    root = sb.get(expect)
    label = "WORKTREE" if expect == "wt" else "sandbox MAIN"
    bound = [e for e in entries if _under(e.get("spine"), root)]
    c.ok(bool(bound),
         "{0}: the binding resolved the relative --file to the {1} ({2})".format(
             arm_name, label,
             ", ".join(repr(e.get("spine")) for e in entries) or "no entries"))

    other = "main" if expect == "wt" else "wt"
    c.ok(not any(_under(e.get("spine"), sb.get(other)) for e in entries),
         "{0}: NO binding entry points at the {1} -- the arms are not both-ways "
         "ambiguous".format(arm_name, "sandbox MAIN" if expect == "wt" else "WORKTREE"))

    sources = [e.get("path_source") for e in bound]
    if expect == "wt":
        c.ok("git_worktree" in sources,
             "treatment: path_source is 'git_worktree', so the hook DERIVED the root "
             "from `git worktree list` -- it was NOT handed the value being proved "
             "(got {0!r})".format(sources))
    else:
        c.ok(all(s is None for s in sources),
             "control: path_source is null, the pre-fix cwd-relative resolution "
             "(got {0!r})".format(sources))


def check_treatment(c: Checker, d: Path) -> dict | None:
    a = load(d / "arm-treatment.json")
    if not c.ok(a is not None, "arm-treatment.json present and parseable"):
        return None
    c.ok(a.get("headless", {}).get("timed_out") is False,
         "treatment headless run did not time out")
    # F1: a headless run killed part-way (attempt 1 died on a weekly usage limit
    # at exit 1) must not be read as a clean arm.
    c.ok(a.get("headless", {}).get("exit") == 0,
         "treatment headless run exited 0 (got {0!r}) -- a part-way kill is not a "
         "clean arm".format(a.get("headless", {}).get("exit")))

    check_binding(c, "treatment", a, expect="wt")

    g = a.get("gauge_in_worktree") or {}
    c.ok(g.get("exists") is True,
         "treatment: gauge.json exists BESIDE THE WORKTREE SPINE (the engine's own read path)")
    over, why = _fill_over_hard(g.get("record"))
    c.ok(over, "treatment: the worktree reading is at/over HARD -- " + why)
    # F1: a gauge at BOTH candidate paths would make "which one did the engine
    # read?" unanswerable, so the phantom must be empty on this arm.
    c.ok((a.get("gauge_in_main_phantom") or {}).get("exists") is not True,
         "treatment: NOTHING was written to the phantom path in the sandbox MAIN, "
         "so the reading is unambiguous")

    c.ok(a.get("advance_exit") not in (None, 0),
         "treatment: `advance` exit code is non-zero (got {0!r})".format(a.get("advance_exit")))
    out = (a.get("advance_output") or "")
    c.ok("REFUSED" in out, "treatment: engine output carries the REFUSED refusal")
    c.ok("hard limit" in out,
         "treatment: the refusal is the HARD-band message, not some other refusal")
    c.ok(a.get("m1_status_after") == "in-progress",
         "treatment: the refused gate stayed in-progress (got {0!r})".format(
             a.get("m1_status_after")))
    return a


def check_control_is_positive(c: Checker, d: Path) -> dict | None:
    """The sharpest requirement: a QUIET control proves nothing. It must be shown
    to have WORKED AND MISSED -- a real reading, over HARD, at the WRONG path."""
    a = load(d / "arm-control.json")
    if not c.ok(a is not None, "arm-control.json present and parseable"):
        return None
    c.ok(a.get("headless", {}).get("timed_out") is False,
         "control headless run did not time out")
    c.ok(a.get("headless", {}).get("exit") == 0,
         "control headless run exited 0 (got {0!r}) -- a part-way kill is not a "
         "clean arm".format(a.get("headless", {}).get("exit")))

    # The defect reproducing is the POINT of this arm, so assert its shape too:
    # the binding must land in the sandbox MAIN, which is what makes the miss a
    # miss rather than an absence.
    check_binding(c, "control", a, expect="main")

    phantom = a.get("gauge_in_main_phantom") or {}
    c.ok(phantom.get("exists") is True,
         "POSITIVE CONTROL: a real gauge.json was written into the phantom "
         ".agent-work/<work_id>/ inside the sandbox MAIN")
    over, why = _fill_over_hard(phantom.get("record"))
    c.ok(over, "POSITIVE CONTROL: the misfiled reading is itself at/over HARD -- " + why)

    c.ok((a.get("gauge_in_worktree") or {}).get("exists") is not True,
         "control: NOTHING was written beside the worktree spine, so the engine saw nothing")
    c.ok(a.get("advance_exit") == 0,
         "control: `advance` SUCCEEDED (exit 0, got {0!r}) -- the governor was blind".format(
             a.get("advance_exit")))
    c.ok(a.get("m1_status_after") == "complete",
         "control: the gate advanced to complete (got {0!r})".format(a.get("m1_status_after")))
    return a


def check_attribution(c: Checker, arm_name: str, a: dict) -> None:
    """Whose reading is this? gauge.json carries no agent id, so the answer has
    to come from three independent signals, not one."""
    att = a.get("attribution") or {}
    c.ok(att.get("composite_key_present") is True,
         "{0} attribution 1/3: the binding key has the composite session_id#agent_id "
         "shape, which only a DISPATCHED agent produces".format(arm_name))
    irm = att.get("identity_resolution_ms")
    c.ok(isinstance(irm, (int, float)),
         "{0} attribution 2/3: identity_resolution_ms is present on the record -- the "
         "writer emits that fifth field ONLY for a dispatched agent (got {1!r})".format(
             arm_name, irm))
    # F1: signal 3 is only evidence if the two models actually DIFFER. With an
    # identical pair the equality below still passes while proving nothing about
    # whose reading it is, so assert the premise before the conclusion.
    c.ok(a.get("parent_model") != a.get("subagent_model_requested"),
         "{0} attribution 3/3 premise: parent ({1!r}) and subagent ({2!r}) ran "
         "DIFFERENT models, so the model field can discriminate between them".format(
             arm_name, a.get("parent_model"), a.get("subagent_model_requested")))
    c.ok(att.get("gauge_model") == att.get("subagent_model_id_expected"),
         "{0} attribution 3/3: gauge.json's model is the SUBAGENT's ({1!r}), not the "
         "parent's -- parent and subagent ran different models (got {2!r})".format(
             arm_name, att.get("subagent_model_id_expected"), att.get("gauge_model")))

    # KNOWN LIMIT, not chased (g2-review F2; scope-discipline ruling). Both
    # timestamps below are written by the same collect() call, so this proves the
    # reading was fresh WHEN THE ENGINE READ IT -- which is the relation the trip
    # depends on -- but it cannot detect stale evidence being re-presented later.
    # Settling that needs an out-of-band clock (the reviewer used file mtimes).
    # Filed at triage rather than fixed here.
    obs = att.get("observed_at")
    wall = att.get("wall_clock_at_collect")
    try:
        o = datetime.fromisoformat(obs)
        w = datetime.fromisoformat(wall)
        if o.tzinfo is None:
            o = o.replace(tzinfo=timezone.utc)
        if w.tzinfo is None:
            w = w.replace(tzinfo=timezone.utc)
        age = (w - o).total_seconds()
        c.ok(0 <= age < 1800,
             "{0}: observed_at is within the reader's 30-minute freshness window "
             "against wall clock ({1:.0f}s old)".format(arm_name, age))
    except Exception:
        c.ok(False, "{0}: observed_at could not be compared to wall clock "
                    "(observed_at={1!r})".format(arm_name, obs))


def check_cross_arm(c: Checker, t: dict | None, k: dict | None) -> None:
    if not (t and k):
        return
    c.ok(t.get("parent_model") == k.get("parent_model")
         and t.get("subagent_model_requested") == k.get("subagent_model_requested"),
         "both arms ran the same parent/subagent model pair")
    c.ok("/treatment/" in (t.get("hook_path") or "")
         and "/control/" in (k.get("hook_path") or ""),
         "the recorded hook_path differs between arms and names each arm's own tree")


def check_live_checkout_untouched(c: Checker, d: Path,
                                  t: dict | None, k: dict | None) -> None:
    """Did the HARNESS write the live checkout's binding store?

    The decisive test is whether a SANDBOX path leaked into that store -- not
    whether its bytes changed. The store is shared, live state: every engine
    `claim`/`advance` by any concurrently-running agent rewrites it through the
    LIVE checkout's own PostToolUse hook. During this run that included this
    implementer's own plan lease and a sibling commander's crew plan. So
    byte-stability is not achievable while other agents are working, and its
    absence says nothing about the harness either way.

    Leakage, by contrast, is exactly the exclusion and it can genuinely fail:
    had the harness pointed CLAUDE_PROJECT_DIR at the live checkout, the
    sandbox's own spine paths would appear in this store.
    """
    a = load(d / "live-checkout-untouched.json")
    if not c.ok(a is not None, "live-checkout-untouched.json present"):
        return

    live = Path((a.get("before") or {}).get("path") or "")
    sandbox_roots = set()
    for arm in (t, k):
        m = ((arm or {}).get("sandbox") or {}).get("main")
        if m:
            # .../<temp>/<sandbox-root>/run-<arm>/main -> <sandbox-root>
            sandbox_roots.add(Path(m).parent.parent.name)
    sandbox_roots = {r for r in sandbox_roots if r}

    store = load(live) if live.is_file() else None
    if not c.ok(store is not None,
                "the LIVE binding store is present and parseable at {0}".format(live)):
        return
    if not c.ok(bool(sandbox_roots),
                "the arms recorded their sandbox root, so leakage is testable"):
        return

    blob = json.dumps(store)
    leaked = sorted(r for r in sandbox_roots if r in blob)
    c.ok(not leaked,
         "the harness NEVER wrote the LIVE checkout's binding store: no sandbox "
         "path leaked into it (roots checked: {0}{1})".format(
             sorted(sandbox_roots), "; LEAKED: " + str(leaked) if leaked else ""))

    if a.get("unchanged") is True:
        c.notes.append("PASS  the live store was additionally byte-identical "
                       "across the run window")
    else:
        c.notes.append(
            "NOTE  the live store's bytes changed during the run ({0} -> {1} bytes). "
            "That is concurrent live-agent activity writing through the LIVE "
            "checkout's own hook, not the harness; the leakage check above is what "
            "tests the exclusion.".format((a.get("before") or {}).get("size"),
                                          (a.get("after") or {}).get("size")))


def check_preflight(c: Checker, d: Path) -> None:
    a = load(d / "preflight-arms.json")
    if not c.ok(a is not None, "preflight-arms.json present"):
        return
    t = (a.get("treatment") or {}).get("resolved") or {}
    k = (a.get("control") or {}).get("resolved") or {}
    c.ok((a.get("treatment") or {}).get("hook_exit") == 0
         and (a.get("control") or {}).get("hook_exit") == 0,
         "preflight: both arm trees are COMPLETE (each hook ran and wrote the store)")
    c.ok(t.get("path_source") == "git_worktree",
         "preflight: the treatment arm DERIVED the worktree via `git worktree list` "
         "(path_source=git_worktree), it was not handed the root (got {0!r})".format(
             t.get("path_source")))
    c.ok("\\wt\\" in (t.get("spine") or "") or "/wt/" in (t.get("spine") or ""),
         "preflight: treatment resolved to the WORKTREE spine")
    c.ok("\\main\\" in (k.get("spine") or "") or "/main/" in (k.get("spine") or ""),
         "preflight: control resolved to the MAIN CHECKOUT path (the defect)")


def verify(d: Path) -> Checker:
    c = Checker()
    c.ok(d.is_dir(), "evidence directory {0} exists".format(d))
    if not d.is_dir():
        return c
    check_arm_diff(c, d)
    check_settings_differ_only_in_hook_path(c, d)
    check_preflight(c, d)
    t = check_treatment(c, d)
    k = check_control_is_positive(c, d)
    if t:
        check_attribution(c, "treatment", t)
    if k:
        check_attribution(c, "control", k)
    check_cross_arm(c, t, k)
    check_live_checkout_untouched(c, d, t, k)
    return c


def selftest() -> int:
    """Prove this checker can fail. Copy the real evidence, damage it three
    different ways, and require a non-zero exit each time."""
    if not DEFAULT_DIR.is_dir():
        print("selftest: no evidence to copy", file=sys.stderr)
        return 1
    base = verify(DEFAULT_DIR)
    print("selftest: real evidence -> {0}".format("PASS" if not base.failures else "FAIL"))
    if base.failures:
        print("selftest: real evidence does not pass; nothing to mutate against",
              file=sys.stderr)
        return 1

    cases = {
        "missing-control-arm": lambda d: (d / "arm-control.json").unlink(),
        "truncated-arm-diff": lambda d: (d / "arm-diff.txt").write_text(
            "# truncated\n", encoding="utf-8"),
        "control-made-quiet": lambda d: _rewrite(
            d / "arm-control.json", "gauge_in_main_phantom",
            {"path": "x", "exists": False, "record": None}),
        "treatment-advance-succeeded": lambda d: _rewrite(
            d / "arm-treatment.json", "advance_exit", 0),
        # Proves the live-checkout leakage check can fail: relabel the sandbox
        # root as one that IS present in the live binding store, which is what a
        # harness that had written the live checkout would look like.
        "live-store-leaked": lambda d: _rewrite(
            d / "arm-treatment.json", "sandbox",
            {"main": "C:/Programs/constellation-skills/run-treatment/main",
             "wt": "C:/Programs/constellation-skills/run-treatment/wt",
             "spine": "C:/Programs/constellation-skills/run-treatment/wt/s.json"}),
        # --- g2-review F1: the four holes closed above, each proved fallible ---
        # THE IMPORTANT ONE. A treatment arm whose binding points at the sandbox
        # MAIN is the #440 defect NOT fixed. Before check_binding existed this
        # mutation exited 0 -- the acceptance artifact for this very issue passed
        # while the bug was present.
        "treatment-binds-main": lambda d: _rebind(
            d / "arm-treatment.json", "main", None),
        # The derivation claim on its own: the right path reached the wrong way.
        # `path_source` null means the hook was handed the root rather than
        # deriving it from `git worktree list`.
        "treatment-path-source-not-derived": lambda d: _rebind(
            d / "arm-treatment.json", "wt", None),
        # A control that binds the worktree is not reproducing the defect.
        "control-binds-worktree": lambda d: _rebind(
            d / "arm-control.json", "wt", "git_worktree"),
        # A part-way kill (attempt 1 died here on a weekly usage limit) is not a
        # clean arm and must not read as one.
        "treatment-headless-killed": lambda d: _rewrite(
            d / "arm-treatment.json", "headless",
            {"exit": 1, "timed_out": False, "elapsed_s": 143.0,
             "stdout_tail": "You've hit your weekly limit"}),
        # Attribution signal 3 is vacuous when both tiers run the same model.
        "same-model-both-tiers": lambda d: _rewrite(
            d / "arm-treatment.json", "parent_model", "sonnet"),
    }
    failed = []
    for name, damage in cases.items():
        tmp = Path(tempfile.mkdtemp(prefix="acc440-selftest-"))
        copy = tmp / "evidence"
        shutil.copytree(DEFAULT_DIR, copy)
        damage(copy)
        c = verify(copy)
        good = bool(c.failures)
        print("selftest: {0:<28} -> {1}".format(
            name, "correctly FAILED" if good else "WRONGLY PASSED"))
        if not good:
            failed.append(name)
        shutil.rmtree(tmp, ignore_errors=True)
    if failed:
        print("selftest: these mutations were not caught: {0}".format(failed),
              file=sys.stderr)
        return 1
    print("selftest: OK -- passes real evidence, fails every damaged copy")
    return 0


def _rewrite(path: Path, key: str, value) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data[key] = value
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _rebind(path: Path, where: str, path_source: str | None) -> None:
    """Repoint an arm's binding entries at the other tree, for --selftest.

    Damages ONLY `binding_entries`, leaving the gauge paths untouched, so the
    mutation is caught by `check_binding` specifically rather than by some other
    check noticing collateral damage.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    root = (data.get("sandbox") or {}).get(where)
    for e in data.get("binding_entries") or []:
        e["spine"] = str(Path(root) / ".agent-work" / "sbwork" / "spine.json")
        e["path_source"] = path_source
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(DEFAULT_DIR))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    c = verify(Path(args.dir))
    for line in c.notes:
        print(line)
    print("")
    if c.failures:
        print("EVIDENCE INCOMPLETE OR CONTRADICTORY -- {0} failure(s):".format(len(c.failures)))
        for f in c.failures:
            print("  - " + f)
        return 1
    print("EVIDENCE COMPLETE AND SELF-CONSISTENT ({0} checks)".format(len(c.notes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
