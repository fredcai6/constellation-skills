"""Relaunch acceptance test for #507 / #370 / #413 (crew delivery addressing).

Pre-Ruling 2 (NOT OVERRIDABLE, `LO-w5-c3-addressing.md`): the acceptance test must
exercise a simulated relaunch and prove the delivery ANNOUNCEMENT mechanism, not
merely that a result file exists — a file-existence-only check cannot fail, and
today's handoffs would already "pass" one.

Two tests:

- `test_a_...` characterizes TODAY'S bug: instance-name addressing, modeled
  directly from #507's own evidence table (there is no in-repo function to call —
  `SendMessage` name resolution is a property of the Agent-tool harness itself,
  outside this repo's code — so the model is the honest way to characterize it).
  A handoff naming the Commander instance that was live when it was WRITTEN
  misroutes once the Commander relaunches again before the crew DELIVERS: lookup
  resolves toward the retired origin of the lineage, never the live head.

- `test_b_...` proves the FIX: the job/gate-addressed result path is the real
  delivery, discovered by the REAL `run_crew.py` / `recover_crews.py` production
  functions (no mocks) from the durable registry + result artifact alone. A
  simulated relaunch — a fresh reload of the registry from disk, sharing no
  Python-level identity with the dispatching instance — discovers the completed
  crew regardless of which Commander instance is asking, because no agent name
  appears anywhere in the discovery path.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_CREW = ROOT / "scripts" / "run_crew.py"
RECOVER = ROOT / "scripts" / "recover_crews.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RC = load_module("run_crew", RUN_CREW)
REC = load_module("recover_crews", RECOVER)


def write_handoff(root: Path, work_id: str, gate: str, role: str) -> str:
    rel = f".agent-work/{work_id}/crew-handoffs/{gate}-{role}.md"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("handoff body\n", encoding="utf-8")
    return rel


def result_rel(work_id: str, gate: str, role: str) -> str:
    return f".agent-work/{work_id}/crew-handoffs/{gate}-{role}-result.md"


class InstanceAddressingMisroutesAfterRelaunch(unittest.TestCase):
    """#507: characterizes today's bug — addressing a crew's delivery to the
    Commander instance name that was live when the HANDOFF was written."""

    @staticmethod
    def _resolve(lineage_at_delivery: list[str], requested: str) -> str:
        """Direct transcription of #507's reported resolution behavior:
        'SendMessage to commander-w4-467-h fails ... the lookup resolves a
        lineage toward its origin, not its head. A handoff naming -h lands on
        -a, the retired first instance.' `lineage_at_delivery[0]` is the origin,
        `lineage_at_delivery[-1]` is the live head at delivery time. Addressing
        the live head resolves to itself (SendMessage still works for whoever
        is actually current); addressing any other lineage member — exactly
        what a handoff written earlier does once the Commander relaunches
        again — resolves to the origin, never to the live head."""
        if requested == lineage_at_delivery[-1]:
            return lineage_at_delivery[-1]
        if requested in lineage_at_delivery:
            return lineage_at_delivery[0]
        raise KeyError(requested)

    def test_a_handoff_written_before_the_next_relaunch_misroutes(self):
        # #507's actual sequence: the crew's handoff names the Commander
        # instance that is LIVE when the handoff is written.
        lineage_at_write = [
            "commander-w4-467", "commander-w4-467-b",
            "commander-w4-467-c", "commander-w4-467-h",
        ]
        addressed = lineage_at_write[-1]  # "-h" — live at write time

        # The Commander relaunches again before the crew's result is delivered
        # (#507: three relaunches inside one wave).
        lineage_at_delivery = lineage_at_write + [
            "commander-w4-467-i", "commander-w4-467-j",
        ]
        live_successor = lineage_at_delivery[-1]  # "-j" — live at delivery time

        resolved = self._resolve(lineage_at_delivery, addressed)

        # The reported failure: resolution lands on the retired ORIGIN, not the
        # live successor — a completed verdict reaches nobody who owns the gate.
        self.assertEqual(
            lineage_at_delivery[0], resolved,
            "characterization diverged from #507: expected the misroute to "
            "land on the retired origin instance",
        )
        self.assertNotEqual(
            live_successor, resolved,
            "characterization failed to reproduce #507: the resolved target "
            "must not be the live successor — that is the misroute",
        )


class JobAddressedDeliverySurvivesRelaunch(unittest.TestCase):
    """The fix: the WRITE to the job/gate-addressed result path is the
    delivery, discovered by the real `run_crew.py` / `recover_crews.py`
    functions from the durable registry alone — no agent name involved."""

    def test_b_relaunched_commander_discovers_a_completed_crew_with_no_shared_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_id, gate, role = "issue-507-sim", "g4", "implementer"

            # --- the dispatching Commander instance (e.g. "commander-w4-467-h")
            # records the durable entry before the crew starts, per
            # `run_crew.py`'s external-backend contract (the Agent-tool
            # harness has no headless CLI to spawn). ---
            handoff = write_handoff(root, work_id, gate, role)
            result = result_rel(work_id, gate, role)
            entries: list[dict] = []
            entry = RC.record_external_attempt(
                work_id=work_id, gate=gate, role=role, handoff=handoff,
                result=result, worktree=".", model="sonnet", attempt=1,
                root=root, entries=entries,
            )
            session = entry["session_name"]
            self.assertIsNone(
                entry["pid"], "external entries must be PID-less — recover_crews "
                "cannot use liveness to identify them",
            )

            # --- the crew delivers: per the fixed handoff templates, the WRITE
            # to the job/gate-addressed path IS the delivery. Its SendMessage
            # courtesy ping (now explicitly best-effort, non-load-bearing) is
            # not modeled — the point is that discovery does not need it. ---
            (root / result).parent.mkdir(parents=True, exist_ok=True)
            (root / result).write_text("IMPLEMENTER_RESULT\ncompleted\n", encoding="utf-8")

            # --- simulated relaunch: two DIFFERENT, later Commander instances
            # ask "is this crew done?" Neither shares any Python-level state
            # with the dispatcher above — each reloads the registry FRESH from
            # disk, exactly as a relaunched process would on cold start, and
            # `asking_instance` itself is never passed into either production
            # function below. That absence is the property being proved: the
            # discovery path takes no agent identity at all. ---
            for asking_instance in ("commander-w4-467-i", "commander-w4-467-j"):
                reloaded_entries = RC.load_registry(RC.registry_path(work_id, root))

                fresh, verified_entry = RC.verify_external_result(
                    reloaded_entries, session, root,
                )
                self.assertTrue(
                    fresh, f"{asking_instance}: run_crew.verify_external_result "
                    f"did not find the result fresh",
                )
                self.assertEqual("completed", verified_entry["status"])

                # Independently, `recover_crews.classify_entry` — the function a
                # relaunched Commander actually runs on cold start before
                # assuming a crew must be (re)dispatched — reaches the same
                # verdict from the same durable facts.
                reloaded_again = RC.load_registry(RC.registry_path(work_id, root))
                classified = REC.classify_registry(
                    reloaded_again,
                    alive=RC.process_alive,
                    result_present=REC._default_result_present(root),
                )
                states = {e["session_name"]: s for e, s in classified}
                self.assertEqual(
                    REC.STATE_COMPLETE, states[session],
                    f"{asking_instance} failed to discover the completed crew "
                    f"via the durable registry alone",
                )


if __name__ == "__main__":
    unittest.main()
