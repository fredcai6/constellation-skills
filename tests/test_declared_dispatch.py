"""Tests for scripts/verify_declared_dispatch.py -- the oracle the generator's
injected `[[gate.dispatch]]` postcondition (LIFECYCLE_CONTRACT.md section 5)
shells out to. Reuses scripts/run_crew.py's own registry loading and
`is_abandoned` -- these tests never hand-roll a second JSON parse either.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_declared_dispatch as vdd  # noqa: E402
from run_crew import registry_path, save_registry  # noqa: E402


def _entry(*, gate="g4", role="implementer", parent="constellation/epic-1/execute/commander/attempt-1",
           model="sonnet", abandoned=False, crew_id="constellation/epic-1/g4/implementer/attempt-1"):
    return {
        "crew_id": crew_id,
        "session_name": crew_id,
        "work_id": "epic-1",
        "gate": gate,
        "role": role,
        "parent": parent,
        "model": model,
        "status": "abandoned" if abandoned else "completed",
        "abandoned": abandoned,
    }


# --------------------------------------------------------------------------- #
# check_declared_dispatch -- PURE (no filesystem, no subprocess)
# --------------------------------------------------------------------------- #

class TestCheckDeclaredDispatch:
    #: Close criterion 4: a registry entry naming the WRONG parent -- made
    #: realistic (a real-looking Admiral session id), not obviously garbage,
    #: exactly the defect LIFECYCLE_CONTRACT.md section 5 / the launch order
    #: names.
    def test_wrong_parent_is_refused(self):
        entries = [_entry(parent="admiral-epic-418-followon")]
        ok, message = vdd.check_declared_dispatch(
            entries, gate="g4", role="implementer",
            parent="constellation/epic-1/execute/commander/attempt-1", model="sonnet",
        )
        assert ok is False
        assert "admiral-epic-418-followon" in message
        assert "g4" in message and "implementer" in message

    def test_wrong_model_is_refused(self):
        entries = [_entry(model="haiku")]
        ok, message = vdd.check_declared_dispatch(
            entries, gate="g4", role="implementer",
            parent="constellation/epic-1/execute/commander/attempt-1", model="sonnet",
        )
        assert ok is False
        assert "haiku" in message

    def test_no_matching_entry_at_all_is_refused(self):
        ok, message = vdd.check_declared_dispatch(
            [], gate="g4", role="implementer",
            parent="constellation/epic-1/execute/commander/attempt-1", model="sonnet",
        )
        assert ok is False
        assert "no non-abandoned" in message

    def test_entry_for_a_different_gate_or_role_does_not_count(self):
        entries = [_entry(gate="g3"), _entry(role="reviewer")]
        ok, message = vdd.check_declared_dispatch(
            entries, gate="g4", role="implementer",
            parent="constellation/epic-1/execute/commander/attempt-1", model="sonnet",
        )
        assert ok is False

    def test_matching_entry_is_accepted(self):
        entries = [_entry()]
        ok, message = vdd.check_declared_dispatch(
            entries, gate="g4", role="implementer",
            parent="constellation/epic-1/execute/commander/attempt-1", model="sonnet",
        )
        assert ok is True
        assert "constellation/epic-1/g4/implementer/attempt-1" in message

    #: Close criterion 8, ACCEPTED_FALSE_ALARM -- populated, not merely named
    #: (DESIGN_NOTE.md section 9). A naive checker that ignored `abandoned`
    #: would flag this; the shipped one must not.
    def test_abandoned_wrong_parent_entry_does_not_block(self):
        entries = [
            _entry(parent="admiral-epic-418-followon", abandoned=True,
                   crew_id="constellation/epic-1/g4/implementer/attempt-1"),
            _entry(crew_id="constellation/epic-1/g4/implementer/attempt-2"),
        ]
        ok, message = vdd.check_declared_dispatch(
            entries, gate="g4", role="implementer",
            parent="constellation/epic-1/execute/commander/attempt-1", model="sonnet",
        )
        assert ok is True
        assert "attempt-2" in message

    def test_abandoned_status_field_also_counts_as_abandoned(self):
        # is_abandoned() honors EITHER `abandoned: true` OR `status:
        # "abandoned"` -- both shapes appear in real registries.
        entries = [{**_entry(parent="admiral-epic-418-followon"), "abandoned": False, "status": "abandoned"}]
        ok, message = vdd.check_declared_dispatch(
            entries, gate="g4", role="implementer",
            parent="constellation/epic-1/execute/commander/attempt-1", model="sonnet",
        )
        assert ok is False
        assert "no non-abandoned" in message


# --------------------------------------------------------------------------- #
# main() -- the CLI layer, against a real crew-runs.json fixture on disk
# --------------------------------------------------------------------------- #

class TestMainCLI:
    def test_exit_0_on_matching_entry(self, tmp_path, capsys):
        entries = [_entry()]
        save_registry(registry_path("epic-1", tmp_path), entries)
        rc = vdd.main([
            "--root", str(tmp_path), "--work-id", "epic-1", "--gate", "g4",
            "--role", "implementer", "--parent", "constellation/epic-1/execute/commander/attempt-1",
            "--model", "sonnet",
        ])
        assert rc == 0
        assert "matches" in capsys.readouterr().out

    def test_exit_1_on_wrong_parent(self, tmp_path, capsys):
        entries = [_entry(parent="admiral-epic-418-followon")]
        save_registry(registry_path("epic-1", tmp_path), entries)
        rc = vdd.main([
            "--root", str(tmp_path), "--work-id", "epic-1", "--gate", "g4",
            "--role", "implementer", "--parent", "constellation/epic-1/execute/commander/attempt-1",
            "--model", "sonnet",
        ])
        assert rc == 1
        assert "admiral-epic-418-followon" in capsys.readouterr().out

    def test_missing_registry_file_is_exit_1_not_a_crash(self, tmp_path, capsys):
        rc = vdd.main([
            "--root", str(tmp_path), "--work-id", "epic-1", "--gate", "g4",
            "--role", "implementer", "--parent", "constellation/epic-1/execute/commander/attempt-1",
            "--model", "sonnet",
        ])
        assert rc == 1
        assert "no non-abandoned" in capsys.readouterr().out

    def test_reuses_run_crew_registry_loading_not_a_second_parser(self):
        import inspect
        src = inspect.getsource(vdd)
        assert "from run_crew import" in src
        assert "is_abandoned" in src
        # Only main()'s own read of a --root/--work-id-derived path via
        # run_crew.load_registry -- no second json.loads of crew-runs.json.
        assert src.count("json.loads") == 0
