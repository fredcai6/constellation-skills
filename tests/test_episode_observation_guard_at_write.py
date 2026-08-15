"""Tests for the write-time instruction-shaped-statement guard in
scripts/apply_episode_delta.py (episode-guard-at-write).

The defect: tests/test_episode_observations.py::RealStoreTests scans episodes/ as a
postcondition of an INTEGRATE gate, but episode records are authored at CLOSEOUT --
strictly later. A lane's own green suite can never have covered the episodes it had not
yet written, so a record that reads as an instruction rather than an observation could
write cleanly and only red the suite once an Admiral re-measured, after the lane had
already archived and pushed. This module proves the fix: apply_episode_delta.py now
calls the read-time guard's own triggers_for()/EXCEPTIONS (scripts/
verify_episode_observations.py) BEFORE a create or restate-assertion op is allowed to
land, so the same statement can no longer pass the writer and then fail the reader.

SCOPE, and why every fixture here "targets the real store" without ever pointing
--store-root at the tracked episodes/ directory: the guard is deliberately scoped to
the ONE store tests/test_episode_observations.py::RealStoreTests actually scans (see
apply_episode_delta._is_real_store's own docstring). A throwaway --store-root is how
every other test in this suite isolates itself -- including this store's own
tests/test_episode_store.py and the read-time guard's own
tests/test_episode_observations.py, both of which build adversarial, instruction-shaped
fixtures THROUGH this exact writer and would lose the ability to build them at all if
an ordinary temp store were guarded too. So "the real store" is simulated here by
patching apply_episode_delta.store_root() to a throwaway directory and never overriding
it with an explicit --store-root -- the writer then treats that throwaway directory
exactly as it would treat the genuine tracked one, without ever touching the genuine
tracked one.
"""

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRITER_SCRIPT = ROOT / "scripts" / "apply_episode_delta.py"

# main at the branch point named in LAUNCH_ORDER.md — scripts/apply_episode_delta.py at
# this revision has no write-time guard at all, which is what makes it the RED half of
# the RED-before/GREEN-after pair below.
PRE_CHANGE_REV = "2c46cab8"


def _git_show(rev: str, path: str) -> str:
    return subprocess.run(
        ["git", "show", f"{rev}:{path}"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout


def load_current():
    spec = importlib.util.spec_from_file_location("apply_episode_delta_egaw_current", WRITER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_pre_change():
    """The writer's source AS OF the pre-change revision, executed under the CURRENT
    file's own path (so any relative-to-__file__ resolution inside it, e.g.
    store_root()'s default, still means what it meant at that revision)."""
    source = _git_show(PRE_CHANGE_REV, "scripts/apply_episode_delta.py")
    spec = importlib.util.spec_from_file_location("apply_episode_delta_egaw_pre_change", WRITER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    exec(compile(source, str(WRITER_SCRIPT), "exec"), module.__dict__)
    return module


def create_op(run="egaw-guard", **statements):
    """One well-formed create op. Every agent-supplied statement is overridable by
    keyword, using the field name with '-' spelled '_' (mirrors
    tests/test_episode_observations.py's own create_op helper, which this module
    deliberately does not import — that file is not this lane's to depend on)."""
    defaults = {
        "task_intent": "Investigated why the closeout suite reds after episodes are written.",
        "expected_behavior": "A record written at closeout is covered by the suite that guards it.",
        "observed_behavior": "The full-suite check ran before the episode it should have covered existed.",
        "impact_cost": "One dispatch was spent rewording records after the fact.",
        "workaround": "none.",
    }
    defaults.update(statements)
    return {
        "op": "create",
        "mechanical": {
            "run": run,
            "project": "constellation-skills",
            "role": "commander",
            "spine-step": "g1-implement",
            "context-manifest-ref": "ctx-egaw-g1@0000000",
            "refusals": 0,
            "reopens": 0,
            "rework-count": 0,
            "failed-commands": 0,
            "artifact-ref": [],
        },
        "agent_supplied": {
            "task-intent": {"strength": "strong", "statement": defaults["task_intent"]},
            "expected-behavior": {"strength": "medium", "statement": defaults["expected_behavior"]},
            "observed-behavior": {"strength": "strong", "statement": defaults["observed_behavior"]},
            "impact-cost": {"strength": "medium", "statement": defaults["impact_cost"]},
            "workaround": {"strength": "strong", "statement": defaults["workaround"]},
        },
    }


# The pre-rewrite shape this whole lane exists to catch: a workaround statement whose
# first clause opens with a bare, subjectless imperative verb ("Read").
BARE_VERB_WORKAROUND = "Read the launch order before writing the closeout episode."


class _RealStoreCase(unittest.TestCase):
    def _run(self, module, *ops, work_id="t"):
        """Drive module.main() exactly as the real CLI would, against a throwaway
        directory that module.store_root() has been patched to treat as THE store —
        see the module docstring for why this, and not --store-root, is what
        simulates "the real store" here."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "episodes"
        module.store_root = lambda: root
        delta_path = Path(tmp.name) / "delta.json"
        delta_path.write_text(json.dumps({"work_id": work_id, "ops": list(ops)}), encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = module.main(["--delta", str(delta_path)])
        return rc, out.getvalue() + err.getvalue(), root


class RedBeforeGreenAfterTests(_RealStoreCase):
    """The load-bearing pair: the exact same delta, against the exact same writer
    entry point, before and after this lane's change."""

    def test_bare_verb_workaround_was_accepted_before_this_change(self):
        """RED (before): the pre-change writer had no opinion about statement content
        at all — the delta this suite now refuses used to write cleanly."""
        pre = load_pre_change()
        rc, out, root = self._run(pre, create_op(workaround=BARE_VERB_WORKAROUND))
        self.assertEqual(0, rc, out)
        self.assertTrue((root / "active" / "egaw-guard-001.md").is_file())

    def test_bare_verb_workaround_is_rejected_now(self):
        """GREEN (after): the same delta, against the current writer, is refused and
        nothing is written."""
        cur = load_current()
        rc, out, root = self._run(cur, create_op(workaround=BARE_VERB_WORKAROUND))
        self.assertNotEqual(0, rc, out)
        active = root / "active"
        self.assertEqual([], list(active.glob("*.md")) if active.is_dir() else [])

    def test_the_rejection_names_the_offending_word_and_kind(self):
        cur = load_current()
        rc, out, _ = self._run(cur, create_op(workaround=BARE_VERB_WORKAROUND))
        self.assertNotEqual(0, rc, out)
        self.assertIn("'Read'", out)
        self.assertIn("workaround", out)
        self.assertIn("imperative", out)


class ControlTests(_RealStoreCase):
    """The check must not become a blanket refusal."""

    def test_a_well_formed_observation_still_writes(self):
        cur = load_current()
        rc, out, root = self._run(cur, create_op())
        self.assertEqual(0, rc, out)
        self.assertTrue((root / "active" / "egaw-guard-001.md").is_file())

    def test_second_person_is_also_caught_for_any_kind_not_just_workaround(self):
        cur = load_current()
        rc, out, root = self._run(
            cur, create_op(task_intent="Investigate why your closeout suite reds.")
        )
        self.assertNotEqual(0, rc, out)
        self.assertIn("second-person", out)
        active = root / "active"
        self.assertEqual([], list(active.glob("*.md")) if active.is_dir() else [])


class ScopeTests(_RealStoreCase):
    """The guard is scoped to the real store only (see _is_real_store) — an ordinary
    --store-root temp directory, the pattern every other episode-store test uses,
    still accepts an instruction-shaped statement unchanged. This is not a gap in the
    fix: nothing scans a throwaway root, so guarding it would protect nothing while
    breaking the many fixtures (in this store's own tests and the read-time guard's)
    that build adversarial statements through this writer on purpose."""

    def test_an_explicit_store_root_bypasses_the_guard_by_design(self):
        cur = load_current()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "episodes"
        delta_path = Path(tmp.name) / "delta.json"
        delta_path.write_text(
            json.dumps({"work_id": "t", "ops": [create_op(workaround=BARE_VERB_WORKAROUND)]}),
            encoding="utf-8",
        )
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cur.main(["--delta", str(delta_path), "--store-root", str(root)])
        self.assertEqual(0, rc, out.getvalue() + err.getvalue())
        self.assertTrue((root / "active" / "egaw-guard-001.md").is_file())


class GrandfatheredExceptionTests(_RealStoreCase):
    """A write-time check must not make a grandfathered (exception-listed) assertion
    permanently uneditable — see LAUNCH_ORDER.md's exception-list hazard."""

    EXCEPTION_KEY = ("issue-308-014", "a5")  # workaround; picked from the guard's own list

    def _seed_episode(self, module, root):
        module.ensure_store_layout(root)
        episode_id, _ = self.EXCEPTION_KEY
        ep = module.Episode(
            episode_id=episode_id,
            run="issue-308",
            project="constellation-skills",
            role="implementer",
            spine_step="g1-implement",
            context_manifest_ref="ctx@0000000",
            refusals=0, reopens=0, rework_count=0, failed_commands=0,
            artifact_refs=[],
            agent_supplied={
                kind: module.Assertion(
                    aid=f"a{i}", kind=kind, strength="medium",
                    lifecycle_standing="active", statement=f"{kind} was recorded.",
                )
                for i, kind in enumerate(module.AGENT_SUPPLIED_KINDS, start=1)
            },
        )
        (root / "active" / f"{episode_id}.md").write_text(
            module.render_episode(ep), encoding="utf-8"
        )

    def test_the_key_is_really_on_the_guards_own_exception_list(self):
        """Guards the fixture itself against the exception list moving out from under
        it — that list is not this lane's to change (LAUNCH_ORDER.md)."""
        cur = load_current()
        self.assertIn(self.EXCEPTION_KEY, cur._guard().EXCEPTIONS)

    def test_restating_a_grandfathered_assertion_with_a_tripping_statement_still_writes(self):
        cur = load_current()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "episodes"
        cur.store_root = lambda: root
        self._seed_episode(cur, root)

        episode_id, assertion_id = self.EXCEPTION_KEY
        delta_path = Path(tmp.name) / "delta.json"
        delta_path.write_text(json.dumps({
            "work_id": "t",
            "ops": [{
                "op": "restate-assertion",
                "id": episode_id,
                "assertion": assertion_id,
                "statement": BARE_VERB_WORKAROUND,
                "history": "exercised by the write-time guard's own grandfather-exception test.",
            }],
        }), encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cur.main(["--delta", str(delta_path)])
        self.assertEqual(0, rc, out.getvalue() + err.getvalue())

    def test_the_same_statement_is_refused_on_a_non_excepted_assertion(self):
        """Proves the exception is doing the work above — without it, the identical
        restatement is rejected exactly like create's."""
        cur = load_current()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "episodes"
        cur.store_root = lambda: root
        # A fresh, well-formed episode not on the exception list.
        rc, out, _ = self._run(cur, create_op())
        self.assertEqual(0, rc, out)
        cur.store_root = lambda: root  # _run() re-patches per call; keep it pinned

        delta_path = Path(tmp.name) / "delta.json"
        delta_path.write_text(json.dumps({
            "work_id": "t",
            "ops": [{
                "op": "restate-assertion",
                "id": "egaw-guard-001",
                "assertion": "a5",
                "statement": BARE_VERB_WORKAROUND,
                "history": "control for the grandfather-exception test.",
            }],
        }), encoding="utf-8")
        out2, err2 = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out2), contextlib.redirect_stderr(err2):
            rc2 = cur.main(["--delta", str(delta_path)])
        self.assertNotEqual(0, rc2, out2.getvalue() + err2.getvalue())


if __name__ == "__main__":
    unittest.main()
