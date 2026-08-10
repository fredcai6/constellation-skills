"""DC4 acceptance test for the MCP front door (issue #424, workstream F, gate
g2): the CLI projection and the MCP tool result carry the SAME imperative
text for EVERY gate that has one, proven as a property over the whole shipped
template population -- not a sample.

Why a population, not a sample (critic finding F42, cited verbatim in the
g2-implementer-handoff.md): "one gate matching once establishes nothing."
`tests/test_mcp_identity.py` already exists at gate g3 (DC2/DC3); this file
never touches it. `tests/test_mcp_spine_server.py` already ships a
byte-identity check for ONE gate (g1) -- that is the SAMPLE. This file is the
POPULATION: every gate carrying a non-empty `imperative` field, discovered by
walking the shipped/committed template tree (`skills/**/templates/*.template.json`)
rather than by hand-listing paths, so a template added tomorrow is covered
automatically instead of silently missed.

Mechanism. `scripts/mcp_spine_server.py`'s `spine_status` tool wraps the exact
same `checklist_engine.main(["--file", SPINE, "current"])` call the CLI makes
-- it never re-derives or re-renders anything (see that module's own
docstring). Both arms here are nonetheless driven as REAL, SEPARATE OS
processes: the CLI arm as a `python checklist_engine.py --file <spine>
current` subprocess, and the MCP arm as a real `mcp_spine_server.py`
subprocess spoken to over newline-delimited JSON-RPC via
`test_mcp_identity.ServerInstance` -- that file's own house pattern for
driving a real server subprocess (read, not edited, here). This is a genuine
equivalence check across two independently-launched processes, not a
tautology against shared in-process state.

For each discovered gate this file builds a synthetic ONE-item checklist
whose single task is a byte-for-byte deep copy of the real task dict pulled
out of the shipped template (id, title, imperative, pre/postconditions,
constraints, directives, anchors) with only its runtime bookkeeping fields
(status, evidence, satisfied flags, ...) reset to "never started" -- so the
gate becomes the ACTIVE gate the instant the checklist loads, and
`render_human()`'s first line (`ACTIVE <id> [<status>] — <imperative>`) is
exercised through the REAL rendering path with the REAL imperative text, for
every gate in the corpus, not a hand-picked one.

Three verification rules this file is graded on (`docs/agents/CREW_CONTEXT.md`,
echoed in the handoff):
  1. A check that cannot fail is indistinguishable from one that passed --
     `PositiveControlTests` below manufactures a genuine divergence and
     proves the comparison detects it, asserting the divergence itself
     landed before trusting the red result.
  2. Any guard that loops must assert what it looped over --
     `test_population_is_nonzero_and_reported` asserts the discovered gate
     count is non-zero and prints/report it; if it looks suspiciously small
     against the ~61-gate/12-template baseline measured when this file was
     written, the assertion message says so explicitly.
  3. Assert against behaviour, never against text that describes it -- every
     assertion in this file is against RENDERED subprocess output, never
     against the raw `imperative` field or a docstring/description.
"""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# test_mcp_identity.py is this repo's house pattern for driving a real
# mcp_spine_server.py subprocess over JSON-RPC (bounded reads, no unconditional
# blocking read inside an eager assertion message -- see its own module
# docstring). Reused here, never re-implemented; not edited by this file (it
# is gate g3's deliverable). pytest has no tests/__init__.py, so both files
# import as top-level modules -- make that import path explicit rather than
# relying on incidental sys.path ordering.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_mcp_identity import ServerInstance  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "scripts" / "checklist_engine.py"
SERVER = ROOT / "scripts" / "mcp_spine_server.py"
TEMPLATE_GLOB = "skills/*/templates/*.template.json"

# Baseline measured 2026-08-09 against this exact tree: 61 gates carrying a
# non-empty imperative, across 12 templates (of 19 *.template.json files
# found; the other 7 are result/record templates with no "tasks"/"items"
# checklist shape -- ENGINE_CONFIG, FINDING, INTERROGATION_RECORD,
# REPLAN_INPUT, REPLAN_RESULT, FOWLER_PASS, INITIAL_ISSUE_SET, SHAPED_BRIEF).
# A pin to the revision measured, per doctrine -- not a permanent fact, a
# floor for "suspiciously small" (rule 2).
MEASURED_GATE_COUNT = 61
MEASURED_TEMPLATE_COUNT = 12
SUSPICIOUSLY_SMALL_FLOOR = 30  # well under the measured 61; a real mass-drop trips this

ACTIVE_LINE_RE = re.compile(r"^ACTIVE (?P<id>\S+) \[(?P<status>[^\]]*)\] — (?P<imp>.*)$")


class GateSpec:
    """One gate discovered by walking the shipped template tree: which
    template file it came from, its id, the checklist `type` that template
    declares, and a deep copy of its REAL task dict (never mutated once
    stored -- callers deep-copy again before touching it)."""

    __slots__ = ("template", "checklist_type", "gate_id", "task")

    def __init__(self, template: Path, checklist_type: str, gate_id: str, task: dict):
        self.template = template
        self.checklist_type = checklist_type
        self.gate_id = gate_id
        self.task = task

    def __repr__(self) -> str:  # pragma: no cover - debug aid only
        return f"GateSpec({self.template}::{self.gate_id})"


def discover_checklist_templates(root: Path = ROOT) -> list[Path]:
    """Walk the shipped/committed template tree -- never a hand-maintained
    path list, so a template added later is covered automatically (rule: the
    population, not the sample)."""
    return sorted(root.glob(TEMPLATE_GLOB))


def discover_gates_with_imperative(root: Path = ROOT) -> tuple[list[GateSpec], list[Path]]:
    """Every gate, across every shipped gated/survey checklist template,
    carrying a non-empty `imperative` field. Returns (gates, skipped) where
    `skipped` is every *.template.json found that is not a gated/survey
    checklist (a result/record template with no tasks/items shape) -- kept
    so the population report can show what was excluded and why, not just a
    silent filter."""
    gates: list[GateSpec] = []
    skipped: list[Path] = []
    for path in discover_checklist_templates(root):
        data = json.loads(path.read_text(encoding="utf-8"))
        checklist_type = data.get("type")
        tasks = data.get("tasks")
        if checklist_type not in ("gated", "survey") or not isinstance(tasks, dict) or "items" not in data:
            skipped.append(path)
            continue
        for gate_id in sorted(tasks):
            task = tasks[gate_id]
            imperative = (task.get("imperative") or "").strip()
            if imperative:
                gates.append(GateSpec(path, checklist_type, gate_id, copy.deepcopy(task)))
    return gates, skipped


def build_single_gate_spine(gate: GateSpec) -> dict:
    """A one-item checklist whose sole task is `gate.task` verbatim (deep
    copy), with only runtime bookkeeping reset so the gate is ACTIVE the
    instant the file loads -- the real imperative text rendered through the
    real engine, for the real gate, not a synthetic marker gate."""
    task = copy.deepcopy(gate.task)
    task["status"] = "pending"
    task["status_detail"] = {}
    task["result"] = None
    task["finding"] = None
    task["evidence"] = []
    task["rework_count"] = 0
    for key in ("preconditions", "postconditions"):
        for cond in task.get(key) or []:
            cond["satisfied"] = False
            cond.pop("waived", None)
            cond.pop("attested", None)
    return {
        "work_id": f"dc4-equiv-{gate.gate_id}",
        "type": gate.checklist_type,
        "config": {"rework_cap": 99},
        "items": [gate.gate_id],
        "tasks": {gate.gate_id: task},
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
    }


def write_spine(path: Path, spine: dict) -> None:
    path.write_text(json.dumps(spine, indent=2), encoding="utf-8")


def cli_current_text(spine_path: Path) -> str:
    """The CLI arm: a REAL, separate `checklist_engine.py current` subprocess
    (never an in-process call) -- proof this is comparing two independently
    launched processes, not shared in-process state."""
    # Explicit UTF-8: the CLI's own stdout is already pinned to UTF-8 by
    # checklist_engine.py's own _utf8_stdio(); decode it explicitly here too
    # rather than falling back to the platform default (cp1252 on an
    # unconfigured Windows box) when reading it back into this test process
    # -- same pin as tests/test_mcp_spine_server.py's own _cli_current().
    proc = subprocess.run(
        [sys.executable, str(ENGINE), "--file", str(spine_path), "current"],
        capture_output=True, text=True, encoding="utf-8", timeout=30,
    )
    assert proc.returncode == 0, (
        f"CLI `current` failed unexpectedly (rc={proc.returncode}): "
        f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
    )
    return proc.stdout.strip()


def extract_imperative(rendered_text: str, expected_gate_id: str) -> str:
    """Pull the imperative substring out of a REAL rendered `current`/
    `spine_status` projection's `ACTIVE <id> [<status>] — <imperative>` line.
    `current` is a railed verb (`RAIL_VERBS` in checklist_engine.py), so a
    doctrine banner can precede the ACTIVE line (e.g. a single-item synthetic
    checklist reads as "near-terminal" -- its one gate is inherently the last
    one -- and gets the near-terminal rail); scan every line for the ACTIVE
    line rather than assuming it is line one. Both CLI and MCP run the exact
    same `dispatch()` against identical spine content, so the rail text itself
    is not part of what this file compares -- only the ACTIVE line's
    imperative substring is. Fails loudly (not silently) if no line matches
    the expected shape or the wrong gate is named -- a shape change here would
    otherwise let a mismatch slip through as a confusing empty-string
    comparison instead of a clear diagnostic."""
    active_lines = [ln for ln in rendered_text.splitlines() if ln.startswith("ACTIVE ")]
    assert active_lines, (
        f"projection for {expected_gate_id!r} carried no 'ACTIVE <id> [<status>] — <imperative>' "
        f"line at all (full text: {rendered_text!r})"
    )
    assert len(active_lines) == 1, (
        f"projection for {expected_gate_id!r} carried {len(active_lines)} ACTIVE lines, expected "
        f"exactly one: {active_lines!r}"
    )
    match = ACTIVE_LINE_RE.match(active_lines[0])
    assert match is not None, (
        f"projection for {expected_gate_id!r} has an ACTIVE line that does not match the expected "
        f"'ACTIVE <id> [<status>] — <imperative>' shape: {active_lines[0]!r}"
    )
    assert match.group("id") == expected_gate_id, (
        f"projection reports the wrong active gate: expected {expected_gate_id!r}, "
        f"got {match.group('id')!r}"
    )
    return match.group("imp")


# --------------------------------------------------------------------------- #
# m1 — thin slice: prove the wiring end to end against exactly ONE real gate
# --------------------------------------------------------------------------- #
class SingleGateWiringTests(unittest.TestCase):
    """Baseline: pick one real, well-known gate (EXECUTE_PLAN.template.json's
    `g1-implement`) and prove CLI vs MCP byte-identity through the full real
    pipeline before generalizing to the whole population in m2."""

    @classmethod
    def setUpClass(cls):
        execute_plan = ROOT / "skills" / "commander" / "templates" / "EXECUTE_PLAN.template.json"
        data = json.loads(execute_plan.read_text(encoding="utf-8"))
        cls.gate = GateSpec(execute_plan, data["type"], "g1-implement",
                             copy.deepcopy(data["tasks"]["g1-implement"]))
        assert (cls.gate.task.get("imperative") or "").strip(), \
            "fixture gate g1-implement unexpectedly carries no imperative -- pick a different known gate"

        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.spine_path = cls.root / "spine.json"
        write_spine(cls.spine_path, build_single_gate_spine(cls.gate))
        cls.server = ServerInstance(cls.spine_path, "dc4-single-gate-session", cls.root,
                                     engine=ENGINE, server=SERVER)

    @classmethod
    def tearDownClass(cls):
        cls.server.close()
        cls.tmp.cleanup()

    def test_single_gate_cli_and_mcp_imperative_are_byte_identical(self):
        cli_text = cli_current_text(self.spine_path)
        mcp_text = self.server.status_text(timeout=15)
        self.assertIsNotNone(mcp_text, "MCP door produced no reply for the single-gate wiring test")

        cli_imp = extract_imperative(cli_text, self.gate.gate_id)
        mcp_imp = extract_imperative(mcp_text, self.gate.gate_id)

        # Ground truth: both arms must also match the source field verbatim,
        # not merely match each other (two independently-wrong renderers
        # that happen to agree would otherwise slip through undetected).
        self.assertEqual(self.gate.task["imperative"], cli_imp,
                          "CLI projection diverged from the source template's imperative field")
        self.assertEqual(self.gate.task["imperative"], mcp_imp,
                          "MCP projection diverged from the source template's imperative field")
        self.assertEqual(cli_imp, mcp_imp,
                          "DC4 violated on a single real gate: CLI and MCP imperative text differ")


# --------------------------------------------------------------------------- #
# m2 — the population, not the sample
# --------------------------------------------------------------------------- #
class PopulationPropertyTests(unittest.TestCase):
    """The property itself: every gate carrying an imperative, across every
    shipped gated/survey checklist template, discovered by walking the tree.
    One persistent MCP server subprocess is reused across the whole walk
    (its bound SPINE_FILE is rewritten before each gate's comparison, since
    the engine reloads the checklist from disk on every verb call) rather
    than launching 61 server processes -- both arms remain REAL, separate
    processes; only the number of MCP server *launches* is reduced from one
    per gate to one for the whole class."""

    @classmethod
    def setUpClass(cls):
        cls.gates, cls.skipped_templates = discover_gates_with_imperative()
        # Rule 2: a guard that loops must assert what it looped over.
        assert len(cls.gates) > 0, (
            "the template walk discovered ZERO gates with an imperative -- the property "
            "would pass vacuously without examining a single interesting item; this is a "
            "defect in the walk itself (glob pattern, root, or template shape assumption), "
            "not a passing result"
        )

        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.spine_path = cls.root / "spine.json"
        write_spine(cls.spine_path, build_single_gate_spine(cls.gates[0]))
        cls.server = ServerInstance(cls.spine_path, "dc4-population-session", cls.root,
                                     engine=ENGINE, server=SERVER)
        # Positive control before trusting any comparison below: the door
        # must be demonstrably up and answering real engine output.
        boot_text = cls.server.status_text(timeout=15)
        assert boot_text is not None, "MCP door produced no reply at population-test startup -- cannot run the property"
        assert "ACTIVE" in boot_text, f"MCP door is up but not serving a real gate projection: {boot_text!r}"

    @classmethod
    def tearDownClass(cls):
        cls.server.close()
        cls.tmp.cleanup()

    def test_population_is_nonzero_and_reported(self):
        n = len(self.gates)
        templates = sorted({str(g.template.relative_to(ROOT)) for g in self.gates})
        skipped_names = sorted(str(p.relative_to(ROOT)) for p in self.skipped_templates)
        print(
            f"\nDC4 population: {n} gates carrying an imperative, across "
            f"{len(templates)} checklist templates: {templates}\n"
            f"Skipped (not a gated/survey checklist shape): {skipped_names}"
        )
        self.assertGreater(n, 0, "gate count must be non-zero -- see setUpClass assertion")
        self.assertGreaterEqual(
            n, SUSPICIOUSLY_SMALL_FLOOR,
            f"only {n} gates found across {len(templates)} templates -- suspiciously small "
            f"against the {MEASURED_GATE_COUNT}-gate/{MEASURED_TEMPLATE_COUNT}-template "
            f"population measured 2026-08-09 on this same tree; investigate the walk before "
            f"trusting this property (a template directory rename or an over-narrow glob "
            f"would silently produce exactly this shape of false-clean result)"
        )

    def test_every_gate_imperative_is_byte_identical_between_cli_and_mcp(self):
        mismatches: list[tuple[str, str, str, str]] = []
        checked = 0
        for gate in self.gates:
            write_spine(self.spine_path, build_single_gate_spine(gate))
            cli_text = cli_current_text(self.spine_path)
            mcp_text = self.server.status_text(timeout=15)
            self.assertIsNotNone(
                mcp_text, f"{gate.template.name}::{gate.gate_id}: MCP door produced no reply"
            )
            cli_imp = extract_imperative(cli_text, gate.gate_id)
            mcp_imp = extract_imperative(mcp_text, gate.gate_id)
            checked += 1
            if cli_imp != mcp_imp:
                mismatches.append((str(gate.template.relative_to(ROOT)), gate.gate_id, cli_imp, mcp_imp))

        # Rule 2, restated for the comparison loop itself: prove every
        # discovered gate was actually examined, not just iterated past.
        self.assertEqual(
            checked, len(self.gates),
            f"only checked {checked}/{len(self.gates)} discovered gates -- the loop exited early"
        )
        self.assertEqual(
            [], mismatches,
            f"DC4 violated on {len(mismatches)}/{checked} gates -- CLI and MCP imperative text "
            f"diverged: {mismatches}"
        )


# --------------------------------------------------------------------------- #
# m3 — positive control: proof the comparison itself can fail, every run
# --------------------------------------------------------------------------- #
class PositiveControlTests(unittest.TestCase):
    """Same bar `tests/test_mcp_identity.py`'s own `DC3PositiveControlTests`
    names for this gate by name ('Same bar gate g2 sets for its own property
    check: demonstrate the red state, not just claim it.'). A check that
    cannot fail is indistinguishable from one that passed -- this class
    manufactures a genuine divergence through the REAL pipeline (two spines,
    identical except one gate's imperative text, read by the CLI arm and the
    MCP arm respectively) and proves: (a) the manufactured mutation actually
    landed -- never trust an edit that silently matched nothing -- and (b)
    the comparison built above genuinely detects the resulting mismatch. Runs
    on every future suite invocation, so drift in the comparator itself is
    caught automatically rather than only once, by hand, at authoring time.
    """

    @classmethod
    def setUpClass(cls):
        cls.gates, _ = discover_gates_with_imperative()
        assert cls.gates, "positive control needs at least one real gate to manufacture a divergence from"
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_control_is_green_when_the_two_arms_read_the_same_spine(self):
        """The unmutated baseline for the next test's contrast: one spine
        file, both arms, imperative matches -- must NOT raise."""
        gate = self.gates[0]
        spine_path = self.root / "green" / "spine.json"
        spine_path.parent.mkdir(parents=True, exist_ok=True)
        write_spine(spine_path, build_single_gate_spine(gate))
        server = ServerInstance(spine_path, "dc4-pc-green-session", spine_path.parent,
                                 engine=ENGINE, server=SERVER)
        try:
            cli_imp = extract_imperative(cli_current_text(spine_path), gate.gate_id)
            mcp_text = server.status_text(timeout=15)
            self.assertIsNotNone(mcp_text)
            mcp_imp = extract_imperative(mcp_text, gate.gate_id)
            self.assertEqual(cli_imp, mcp_imp)  # must not raise
        finally:
            server.close()

    def test_control_is_red_when_the_two_arms_read_genuinely_different_imperatives(self):
        """RED: mutate ONE gate's imperative text for the copy the MCP arm
        reads, leaving the CLI arm's copy untouched. Proof the mutation
        actually applied (rule 1: a sed that silently matched nothing leaves
        a green suite indistinguishable from a passing guard) is the direct
        string-inequality assertion against the two spine files' own JSON
        content, BEFORE the comparison is trusted to have caught anything."""
        gate = self.gates[0]
        original_imperative = gate.task["imperative"]
        mutated_imperative = original_imperative + " [[DC4-POSITIVE-CONTROL-MUTATION]]"

        original_dir = self.root / "unmutated"
        mutated_dir = self.root / "mutated"
        original_dir.mkdir(parents=True, exist_ok=True)
        mutated_dir.mkdir(parents=True, exist_ok=True)

        cli_spine_path = original_dir / "spine.json"
        write_spine(cli_spine_path, build_single_gate_spine(gate))

        mutated_gate = GateSpec(gate.template, gate.checklist_type, gate.gate_id, copy.deepcopy(gate.task))
        mutated_gate.task["imperative"] = mutated_imperative
        mcp_spine_path = mutated_dir / "spine.json"
        write_spine(mcp_spine_path, build_single_gate_spine(mutated_gate))

        # Proof the mutation actually applied: read the file BACK off disk
        # (not the in-memory dict) and assert it genuinely differs.
        on_disk_mcp_spine = json.loads(mcp_spine_path.read_text(encoding="utf-8"))
        on_disk_imperative = on_disk_mcp_spine["tasks"][gate.gate_id]["imperative"]
        self.assertEqual(mutated_imperative, on_disk_imperative,
                          "the manufactured mutation did not land in the file the MCP arm will read")
        self.assertNotEqual(original_imperative, on_disk_imperative,
                             "the manufactured mutation is a no-op -- indistinguishable from a "
                             "sed that silently matched nothing; this control would prove nothing")

        server = ServerInstance(mcp_spine_path, "dc4-pc-red-session", mutated_dir,
                                 engine=ENGINE, server=SERVER)
        try:
            cli_imp = extract_imperative(cli_current_text(cli_spine_path), gate.gate_id)
            mcp_text = server.status_text(timeout=15)
            self.assertIsNotNone(mcp_text)
            mcp_imp = extract_imperative(mcp_text, gate.gate_id)

            self.assertEqual(cli_imp, original_imperative)
            self.assertEqual(mcp_imp, mutated_imperative)
            with self.assertRaises(AssertionError):
                self.assertEqual(
                    cli_imp, mcp_imp,
                    "positive control: the comparison must detect this manufactured divergence"
                )
        finally:
            server.close()


if __name__ == "__main__":
    unittest.main()
