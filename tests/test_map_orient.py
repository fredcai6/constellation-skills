"""The falsification floor for scripts/map_orient.py.

The protected intent is the REPORTED degraded mode: degrading is fine,
degrading silently is refused. Degraded is the COMMON case -- this repo has no
`docs/architecture/` at all -- so the degraded arms carry at least as much of
this file as the resolved arm.

This file is run TWICE: once normally, and once per mutation by
tests/test_mutation_floor.py, which points `MAP_ORIENT_MODULE` at a mutated
copy of the module and asserts this floor goes RED. That is why the module
under test is a variable rather than a fixed import.
"""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The module under test. tests/test_mutation_floor.py overrides this to run the
# whole floor against a mutant.
MODULE_PATH = Path(os.environ.get("MAP_ORIENT_MODULE", ROOT / "scripts" / "map_orient.py"))

SHIPPED_INDEX_TEMPLATE = ROOT / "skills/cartographer/templates/ARCHITECTURE_INDEX.template.md"


def load():
    spec = importlib.util.spec_from_file_location("map_orient_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    # A frozen dataclass resolves its own module through sys.modules at class
    # creation; without this line the import raises on 3.14.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mo = load()


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return path


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MODULE_PATH), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd is not None else None,
    )


def orient(root: Path, work_id: str = "w", *extra: str, cwd: Path | None = None):
    return run_cli("orient", "--root", str(root), "--work-id", work_id, *extra, cwd=cwd)


def verdict(proc: subprocess.CompletedProcess) -> str:
    return proc.stdout.splitlines()[0] if proc.stdout.splitlines() else ""


def receipt_of(root: Path, work_id: str = "w") -> dict:
    path = root / ".agent-work" / work_id / "map-orientation.json"
    return json.loads(path.read_text(encoding="utf-8"))


class RepoFixture:
    """A tmp directory that is a PROVEN repo root unless asked otherwise."""

    def __init__(self, stack: unittest.TestCase, git: bool = True):
        self.tmp = tempfile.TemporaryDirectory()
        stack.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        if git:
            (self.root / ".git").mkdir()

    def file(self, rel: str, text: str) -> Path:
        return write(self.root / rel, text)

    def dir(self, rel: str) -> Path:
        target = self.root / rel
        target.mkdir(parents=True, exist_ok=True)
        return target


REAL_PACKET = """# Packet: src/physics

```yaml
id: struct:physics
level: container
```

Owns `capability:lap_fit` under `constraint:physics_region_no_evo_import`.
"""

REAL_INDEX = """# Architecture Index

| Node | Level |
|---|---|
| `struct:app` | container |
| `struct:app.api` | component |

Overlay: `capability:serve_requests`, `decision:one_canonical_path`.
"""

REAL_MAP_JSON = json.dumps(
    {"nodes": [{"id": "struct:app", "level": "container"}, {"id": "struct:app.api"}]},
    indent=2,
)


# =============================================================================
# Resolution matrix -- ordered, first hit wins, every candidate still recorded
# =============================================================================


class ResolutionMatrix(unittest.TestCase):
    def test_generated_map_resolves_first(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/generated/map.json", REAL_MAP_JSON)
        repo.file("docs/architecture/index.md", REAL_INDEX)
        proc = orient(repo.root)
        self.assertEqual(verdict(proc), "RESOLVED")
        self.assertEqual(receipt_of(repo.root)["entrypoint"], "docs/architecture/generated/map.json")

    def test_index_resolves_when_no_generated_map(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/index.md", REAL_INDEX)
        proc = orient(repo.root)
        self.assertEqual(verdict(proc), "RESOLVED")
        self.assertEqual(receipt_of(repo.root)["entrypoint"], "docs/architecture/index.md")

    def test_packets_resolve_when_no_index(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/packets/physics.md", REAL_PACKET)
        proc = orient(repo.root)
        self.assertEqual(verdict(proc), "RESOLVED")
        self.assertEqual(receipt_of(repo.root)["entrypoint"], "docs/architecture")

    def test_explicit_entrypoint_is_tried_first(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/index.md", REAL_INDEX)
        repo.file("notes/my-map.md", REAL_PACKET)
        proc = orient(repo.root, "w", "--entrypoint", "notes/my-map.md")
        self.assertEqual(verdict(proc), "RESOLVED")
        self.assertEqual(receipt_of(repo.root)["entrypoint"], "notes/my-map.md")

    def test_every_candidate_is_recorded_even_after_a_hit(self):
        """The receipt is a delivery record, not a first-hit lookup log."""
        repo = RepoFixture(self)
        repo.file("docs/architecture/index.md", REAL_INDEX)
        repo.file("notes/my-map.md", REAL_PACKET)
        orient(repo.root, "w", "--entrypoint", "notes/my-map.md")
        tried = receipt_of(repo.root)["candidates_tried"]
        self.assertEqual([c["kind"] for c in tried], ["entrypoint", "generated-map", "index", "packets-dir"])
        # The entrypoint hit first, yet the later index.md hit is still on the record.
        self.assertEqual(tried[0]["outcome"], "hit")
        self.assertEqual(tried[2]["outcome"], "hit")
        self.assertEqual(tried[1]["outcome"], "absent")

    def test_resolved_reports_the_anchor_count_it_actually_found(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/index.md", REAL_INDEX)
        orient(repo.root)
        self.assertEqual(receipt_of(repo.root)["anchor_count"], 4)


# =============================================================================
# Every DEGRADED reason produced distinctly
# =============================================================================


class DegradedReasons(unittest.TestCase):
    def test_no_map_directory_at_all(self):
        repo = RepoFixture(self)
        proc = orient(repo.root)
        self.assertEqual(verdict(proc), "DEGRADED-NO-MAP")

    def test_empty_index_is_empty_map_not_no_map(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/index.md", "")
        proc = orient(repo.root)
        self.assertEqual(verdict(proc), "DEGRADED-EMPTY-MAP")

    def test_scaffolded_map_dir_with_no_content_is_empty_map(self):
        repo = RepoFixture(self)
        repo.dir("docs/architecture/packets")
        proc = orient(repo.root)
        self.assertEqual(verdict(proc), "DEGRADED-EMPTY-MAP")

    def test_content_without_a_citable_anchor_is_unparseable(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/index.md", "# Architecture Index\n\nComing soon.\n")
        proc = orient(repo.root)
        self.assertEqual(verdict(proc), "DEGRADED-UNPARSEABLE")

    def test_broken_generated_map_is_unparseable_not_resolved(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/generated/map.json", "{not json at all")
        proc = orient(repo.root)
        self.assertEqual(verdict(proc), "DEGRADED-UNPARSEABLE")

    def test_generated_map_without_nodes_does_not_resolve(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/generated/map.json", json.dumps({"nodes": []}))
        proc = orient(repo.root)
        self.assertNotEqual(verdict(proc), "RESOLVED")

    def test_packets_that_are_all_blank_do_not_resolve(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/packets/a.md", "   \n\n")
        proc = orient(repo.root)
        self.assertEqual(verdict(proc), "DEGRADED-EMPTY-MAP")

    def test_a_degraded_repo_never_exits_zero_undischarged(self):
        repo = RepoFixture(self)
        proc = orient(repo.root)
        self.assertEqual(proc.returncode, 10)


# =============================================================================
# RESOLVED requires citable CONTENT, not file existence
# =============================================================================


class CitableContent(unittest.TestCase):
    def test_the_shipped_index_template_itself_does_not_resolve(self):
        """The scaffold this repo ships must read DEGRADED, verbatim.

        Uses the real committed template rather than a copied fixture so it
        cannot rot into something nobody maintains.
        """
        self.assertTrue(SHIPPED_INDEX_TEMPLATE.is_file(), SHIPPED_INDEX_TEMPLATE)
        repo = RepoFixture(self)
        repo.file(
            "docs/architecture/index.md",
            SHIPPED_INDEX_TEMPLATE.read_text(encoding="utf-8"),
        )
        proc = orient(repo.root)
        self.assertTrue(verdict(proc).startswith("DEGRADED-"), proc.stdout)
        self.assertEqual(verdict(proc), "DEGRADED-UNPARSEABLE")
        self.assertEqual(receipt_of(repo.root)["anchor_count"], 0)

    def test_an_existing_but_empty_index_is_never_resolved(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/index.md", "")
        self.assertNotEqual(verdict(orient(repo.root)), "RESOLVED")

    def test_placeholder_ids_are_not_citable(self):
        repo = RepoFixture(self)
        repo.file(
            "docs/architecture/index.md",
            "| `struct:<id>` | `capability:<id>` | `decision:<id>` |\n",
        )
        self.assertEqual(verdict(orient(repo.root)), "DEGRADED-UNPARSEABLE")

    def test_this_repo_resolves_degraded(self):
        """This repo has no docs/architecture/ -- the honest verdict is DEGRADED.

        This will legitimately flip the day this repo grows a real map. That is
        the point: the floor tracks reality rather than asserting a wish.
        """
        proof = mo.probe_root(ROOT)
        candidates = mo.collect_candidates(ROOT, None)
        orientation = mo.build_orientation(ROOT.as_posix(), proof, candidates)
        self.assertTrue(proof.proven, proof.evidence)
        self.assertEqual(orientation.mode, "DEGRADED-NO-MAP")
        self.assertEqual(orientation.anchor_count, 0)


# =============================================================================
# "Could not look" vs "looked and found nothing" -- one bit apart
# =============================================================================


class CouldNotLookDiscriminator(unittest.TestCase):
    def test_bare_directory_and_the_same_directory_with_git_differ_in_one_bit(self):
        repo = RepoFixture(self, git=False)

        before = orient(repo.root, "before")
        self.assertEqual(verdict(before), "UNRESOLVABLE-ROOT")
        self.assertEqual(before.returncode, 11)

        # The ONLY thing that changes between the two calls.
        (repo.root / ".git").mkdir()

        after = orient(repo.root, "after")
        self.assertEqual(verdict(after), "DEGRADED-NO-MAP")
        self.assertEqual(after.returncode, 10)

    def test_unresolvable_root_is_not_a_degraded_verdict(self):
        repo = RepoFixture(self, git=False)
        proc = orient(repo.root)
        self.assertFalse(verdict(proc).startswith("DEGRADED"), proc.stdout)

    def test_repo_root_proof_is_positive_not_an_absence_test(self):
        self.assertTrue(mo.prove_repo_root("/r", True, None).proven)
        self.assertTrue(mo.prove_repo_root("/r", False, "/r").proven)
        # A subdirectory of a repo is not itself a repo root.
        self.assertFalse(mo.prove_repo_root("/r/sub", False, "/r").proven)
        self.assertFalse(mo.prove_repo_root("/r", False, None).proven)


# =============================================================================
# The partial-fill matrix -- substitutes AND unmapped AND escalation
# =============================================================================


COMPLETE_RECORD = {
    "substitutes": [{"path": "README.md", "content_hash": "a" * 64}],
    "unmapped": ["src/engine/ internals were never read"],
    "escalation": "asking commander whether a map is in scope for this issue",
}


def degraded_receipt(root: Path, work_id: str, **overrides) -> Path:
    body = {
        "schema_version": 1,
        "work_id": work_id,
        "root": root.as_posix(),
        "mode": "DEGRADED-NO-MAP",
        "entrypoint": None,
        "anchor_count": 0,
        "candidates_tried": [
            {"order": 1, "kind": "index", "path": "docs/architecture/index.md",
             "exists": False, "outcome": "absent", "anchor_count": 0, "note": "absent"}
        ],
        "emitted_at": "2026-08-01T00:00:00+00:00",
    }
    body.update(COMPLETE_RECORD)
    body.update(overrides)
    return write(
        root / ".agent-work" / work_id / "map-orientation.json",
        json.dumps(body, indent=2) + "\n",
    )


def verify(root: Path, work_id: str) -> subprocess.CompletedProcess:
    return run_cli("verify-orientation", "--root", str(root), "--work-id", work_id)


class PartialFillMatrix(unittest.TestCase):
    """Each arm omits exactly ONE required field; the other two are present.

    Three arms is what kills an `all` -> `any` mutation: `any` would let every
    one of them through. The positive control is what stops a bare
    `return False` from faking the kill.
    """

    def test_positive_control_a_complete_record_passes(self):
        repo = RepoFixture(self)
        degraded_receipt(repo.root, "w")
        proc = verify(repo.root, "w")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_missing_substitutes_is_refused(self):
        repo = RepoFixture(self)
        degraded_receipt(repo.root, "w", substitutes=[])
        self.assertEqual(verify(repo.root, "w").returncode, 10)

    def test_missing_unmapped_is_refused(self):
        repo = RepoFixture(self)
        degraded_receipt(repo.root, "w", unmapped=[])
        self.assertEqual(verify(repo.root, "w").returncode, 10)

    def test_missing_escalation_is_refused(self):
        repo = RepoFixture(self)
        degraded_receipt(repo.root, "w", escalation=None)
        self.assertEqual(verify(repo.root, "w").returncode, 10)

    def test_filler_escalation_is_refused(self):
        repo = RepoFixture(self)
        for filler in ("", "  ", "none", "N/A", "n/a", "tbd"):
            with self.subTest(filler=filler):
                degraded_receipt(repo.root, "w", escalation=filler)
                self.assertEqual(verify(repo.root, "w").returncode, 10)

    def test_filler_unmapped_is_refused(self):
        repo = RepoFixture(self)
        for filler in ("none", "n/a", ""):
            with self.subTest(filler=filler):
                degraded_receipt(repo.root, "w", unmapped=[filler])
                self.assertEqual(verify(repo.root, "w").returncode, 10)

    def test_one_filler_poisons_a_multi_element_unmapped_list(self):
        """MULTI-element on purpose.

        A single-element list cannot tell `not any(is_filler)` from
        `not all(is_filler)` -- they agree on lists of length 1. A floor built
        only from single-element cases therefore lets a mutation between them
        SURVIVE, which is exactly what happened before this test existed.
        """
        repo = RepoFixture(self)
        real = "src/engine internals were never read"
        for entries in (["none", real], [real, "n/a"], ["none", "n/a"], [real, "", real]):
            with self.subTest(unmapped=entries):
                degraded_receipt(repo.root, "w", unmapped=entries)
                self.assertEqual(verify(repo.root, "w").returncode, 10)

    def test_a_multi_element_unmapped_list_of_real_entries_passes(self):
        """Positive control for the case above: an all-real list must pass."""
        repo = RepoFixture(self)
        degraded_receipt(
            repo.root,
            "w",
            unmapped=["src/engine was never read", "the data layer was never read"],
        )
        self.assertEqual(verify(repo.root, "w").returncode, 0)

    def test_one_unpinned_substitute_poisons_a_multi_element_list(self):
        repo = RepoFixture(self)
        degraded_receipt(
            repo.root,
            "w",
            substitutes=[
                {"path": "README.md", "content_hash": "b" * 64},
                {"path": "gone.md", "content_hash": None},
            ],
        )
        self.assertEqual(verify(repo.root, "w").returncode, 10)

    def test_filler_substitute_path_is_refused(self):
        repo = RepoFixture(self)
        degraded_receipt(repo.root, "w", substitutes=[{"path": "none", "content_hash": "a" * 64}])
        self.assertEqual(verify(repo.root, "w").returncode, 10)

    def test_unhashed_substitute_is_refused(self):
        repo = RepoFixture(self)
        degraded_receipt(repo.root, "w", substitutes=[{"path": "README.md", "content_hash": ""}])
        self.assertEqual(verify(repo.root, "w").returncode, 10)

    def test_the_completeness_predicate_requires_all_three(self):
        """Direct assertion on the predicate the mutation targets."""
        self.assertTrue(mo.degraded_record_is_complete(dict(COMPLETE_RECORD)))
        for dropped, empty in (("substitutes", []), ("unmapped", []), ("escalation", None)):
            with self.subTest(dropped=dropped):
                record = dict(COMPLETE_RECORD)
                record[dropped] = empty
                self.assertFalse(mo.degraded_record_is_complete(record))


# =============================================================================
# verify-orientation -- the gate check
# =============================================================================


class UnreadableSubstitute(unittest.TestCase):
    """A substitute that cannot be read must REFUSE, never discharge.

    This is the hole the whole contract exists to close: the tool used to emit
    `content_hash: "unreadable"` for a path it could not read, and a non-empty
    sentinel satisfied the "is it hash-pinned" test -- so a single typo in a
    substitute path discharged the entire degraded record at exit 0.
    """

    def test_a_nonexistent_substitute_path_refuses(self):
        """The reviewer's exact reproduction, pinned."""
        repo = RepoFixture(self)
        proc = orient(
            repo.root, "w",
            "--substitute", "docs/THIS_FILE_DOES_NOT_EXIST.md",
            "--unmapped", "structural relationships",
            "--escalation", "surfaced-to-principal",
        )
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(proc.returncode, 10)
        self.assertNotEqual(verify(repo.root, "w").returncode, 0)

    def test_an_unreadable_substitute_is_not_pinned_with_a_sentinel(self):
        repo = RepoFixture(self)
        orient(
            repo.root, "w",
            "--substitute", "docs/THIS_FILE_DOES_NOT_EXIST.md",
            "--unmapped", "structural relationships",
            "--escalation", "surfaced-to-principal",
        )
        pinned = receipt_of(repo.root, "w")["substitutes"]
        self.assertIsNone(pinned[0]["content_hash"])

    def test_the_refusal_names_the_offending_substitute(self):
        repo = RepoFixture(self)
        proc = orient(
            repo.root, "w",
            "--substitute", "docs/THIS_FILE_DOES_NOT_EXIST.md",
            "--unmapped", "structural relationships",
            "--escalation", "surfaced-to-principal",
        )
        self.assertIn("THIS_FILE_DOES_NOT_EXIST", proc.stderr)

    def test_one_real_substitute_still_discharges(self):
        """Positive control: the fix must not refuse a genuine declaration."""
        repo = RepoFixture(self)
        repo.file("README.md", "the substitute I actually read\n")
        proc = orient(
            repo.root, "w",
            "--substitute", "README.md",
            "--unmapped", "structural relationships",
            "--escalation", "surfaced-to-principal",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(verify(repo.root, "w").returncode, 0)

    def test_a_sentinel_content_hash_in_a_handwritten_receipt_refuses(self):
        repo = RepoFixture(self)
        for bad in ("unreadable", "n/a", "", None, "a" * 63, "Z" * 64):
            with self.subTest(content_hash=bad):
                degraded_receipt(
                    repo.root, "w",
                    substitutes=[{"path": "README.md", "content_hash": bad}],
                )
                self.assertEqual(verify(repo.root, "w").returncode, 10)

    def test_a_hash_pin_must_be_a_real_sha256(self):
        self.assertTrue(mo.is_content_hash(hashlib.sha256(b"x").hexdigest()))
        self.assertFalse(mo.is_content_hash("unreadable"))
        self.assertFalse(mo.is_content_hash("a" * 63))
        self.assertFalse(mo.is_content_hash(None))


class VerifyOrientation(unittest.TestCase):
    def test_resolved_with_a_wellformed_receipt_passes(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/index.md", REAL_INDEX)
        self.assertEqual(orient(repo.root).returncode, 0)
        proc = verify(repo.root, "w")
        self.assertEqual(verdict(proc), "RESOLVED")
        self.assertEqual(proc.returncode, 0)

    def test_a_missing_receipt_is_reported_not_assumed(self):
        repo = RepoFixture(self)
        proc = verify(repo.root, "never-oriented")
        self.assertEqual(verdict(proc), "RECEIPT-MISSING")
        self.assertEqual(proc.returncode, 12)

    def test_a_malformed_receipt_is_reported(self):
        repo = RepoFixture(self)
        write(repo.root / ".agent-work" / "w" / "map-orientation.json", "{broken")
        self.assertEqual(verify(repo.root, "w").returncode, 12)

    def test_an_unresolvable_root_receipt_never_passes(self):
        repo = RepoFixture(self)
        degraded_receipt(repo.root, "w", mode="UNRESOLVABLE-ROOT")
        proc = verify(repo.root, "w")
        self.assertEqual(verdict(proc), "UNRESOLVABLE-ROOT")
        self.assertEqual(proc.returncode, 11)

    def test_orient_with_a_full_declaration_discharges_the_degraded_record(self):
        repo = RepoFixture(self)
        repo.file("README.md", "the substitute I actually read\n")
        proc = orient(
            repo.root, "w",
            "--substitute", "README.md",
            "--unmapped", "src/ internals were never read",
            "--escalation", "asking commander whether a map is in scope",
        )
        self.assertEqual(verdict(proc), "DEGRADED-NO-MAP")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(verify(repo.root, "w").returncode, 0)

    def test_substitutes_are_hash_pinned(self):
        repo = RepoFixture(self)
        body = "the substitute I actually read\n"
        repo.file("README.md", body)
        orient(repo.root, "w", "--substitute", "README.md",
               "--unmapped", "everything else", "--escalation", "ask commander")
        pinned = receipt_of(repo.root, "w")["substitutes"]
        self.assertEqual(pinned[0]["path"], "README.md")
        self.assertEqual(
            pinned[0]["content_hash"],
            hashlib.sha256(body.encode("utf-8")).hexdigest(),
        )


# =============================================================================
# Contract shape: reserved literals, exit vocabulary, cwd independence
# =============================================================================


class ContractShape(unittest.TestCase):
    def test_first_stdout_line_is_always_a_reserved_literal(self):
        repo = RepoFixture(self)
        cases = [orient(repo.root, "a")]
        repo.file("docs/architecture/index.md", "")
        cases.append(orient(repo.root, "b"))
        repo.file("docs/architecture/index.md", "# nothing citable\n")
        cases.append(orient(repo.root, "c"))
        repo.file("docs/architecture/index.md", REAL_INDEX)
        cases.append(orient(repo.root, "d"))
        cases.append(verify(repo.root, "never-oriented"))
        bare = RepoFixture(self, git=False)
        cases.append(orient(bare.root, "e"))
        for proc in cases:
            with self.subTest(first=verdict(proc)):
                self.assertIn(verdict(proc), mo.RESERVED_FIRST_LINES)
                self.assertTrue(verdict(proc).strip())

    def test_semantic_exit_codes_avoid_the_argparse_traceback_shell_collision(self):
        for code in mo.SEMANTIC_EXIT_CODES:
            with self.subTest(code=code):
                self.assertNotIn(code, (0, 1, 2, 126, 127))
                self.assertGreater(code, 2)
                self.assertLess(code, 126)

    def test_a_usage_error_exits_two_and_is_not_a_verdict(self):
        proc = run_cli("orient", "--no-such-flag")
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn(proc.returncode, mo.SEMANTIC_EXIT_CODES)

    def test_no_subcommand_is_a_usage_error_not_a_verdict(self):
        proc = run_cli()
        self.assertEqual(proc.returncode, 2)

    def test_self_test_floor_passes(self):
        proc = run_cli("--self-test")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_verdict_is_independent_of_the_launcher_cwd(self):
        repo = RepoFixture(self)
        repo.file("docs/architecture/index.md", REAL_INDEX)
        elsewhere = RepoFixture(self)
        elsewhere.file("docs/architecture/index.md", "# decoy, nothing citable\n")

        from_repo = orient(repo.root, "here", cwd=repo.root)
        from_elsewhere = orient(repo.root, "there", cwd=elsewhere.root)

        self.assertEqual(verdict(from_repo), verdict(from_elsewhere))
        self.assertEqual(from_repo.returncode, from_elsewhere.returncode)
        self.assertEqual(
            receipt_of(repo.root, "here")["entrypoint"],
            receipt_of(repo.root, "there")["entrypoint"],
        )


# =============================================================================
# verify-frame -- the citation check
# =============================================================================
#
# The seam: **anchor ids exist only in the map**, so citing one is set-membership
# proof the map was read. That turns "did the map inform the plan" into a
# question a machine can answer with no stochastic judgement.
#
# What it does NOT achieve, stated here so no reader has to infer it: measured
# against this epic's baseline five runs, this check has sensitivity 0/4 and
# specificity 0/1 -- four runs cited map artifacts while exhibiting the defect
# (they would pass) and the one run that would fail it was correct to disengage.
# It ships as a regression FLOOR so map-ignoring cannot silently return. It is
# not the fix for the measured defect, which is map-LATENESS.


GOOD_FRAME = """# Mission Frame

## Intent
Serve the API without breaking the canonical path.

## Structural Anchors
- `struct:app` — the container
- `struct:app.api` — component

## Affected Capabilities
- `capability:serve_requests` — what changes

## Decision Anchors
- `decision:one_canonical_path` — what it fixed
"""

UNKNOWN_ANCHOR_FRAME = """# Mission Frame

## Structural Anchors
- `struct:app` — real
- `struct:ghost_module` — invented; nothing in the map carries this id
"""

CODE_CUT_FRAME = """# Mission Frame

## Intent
Fix the solver.

## Structural Anchors
- `src/engine/solver.py` — where the maths lives
- `scripts/run_solver.py` — the entrypoint I found by grepping
- `src/engine/util.py` — helpers
"""

DEGRADED_FRAME = """# Mission Frame

## Intent
No map exists; this frame is cut from the doctrine I declared at orient time.

## Substituted Reading
- `README.md` — the repo's own doctrine, hash-pinned in the orientation receipt
"""

UUNDECLARED_FALLBACK_FRAME = """# Mission Frame

## Substituted Reading
- `README.md` — declared and pinned
- `CLAUDE.md` — I also read this
"""


def frame(root: Path, text: str, work_id: str = "w") -> Path:
    return write(root / ".agent-work" / work_id / "MISSION_FRAME.md", text)


def verify_frame(root: Path, work_id: str = "w", *extra: str) -> subprocess.CompletedProcess:
    return run_cli("verify-frame", "--root", str(root), "--work-id", work_id, *extra)


def resolved_repo(case: unittest.TestCase) -> RepoFixture:
    """A repo with a real map, already oriented -- the RESOLVED baseline."""
    repo = RepoFixture(case)
    repo.file("docs/architecture/index.md", REAL_INDEX)
    proc = orient(repo.root)
    case.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
    return repo


class AbsentFrameRefuses(unittest.TestCase):
    """THE load-bearing negative case of this gate.

    A check that passes when the artifact it checks does not exist is not a
    check -- it is a decoration that reports success for every run that skips
    the work entirely. Everything else in `verify-frame` is downstream of this
    one refusal, which is why it was written first.
    """

    def test_an_absent_frame_refuses_on_a_resolved_repo(self):
        repo = resolved_repo(self)
        proc = verify_frame(repo.root)
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(verdict(proc), "FRAME-MISSING")

    def test_an_absent_frame_refuses_on_a_degraded_repo_too(self):
        """The degraded arm must not become the vacuous-pass back door."""
        repo = RepoFixture(self)
        repo.file("README.md", "doctrine\n")
        orient(repo.root, "w", "--substitute", "README.md",
               "--unmapped", "everything structural", "--escalation", "ask commander")
        proc = verify_frame(repo.root)
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(verdict(proc), "FRAME-MISSING")

    def test_an_empty_frame_file_is_the_same_as_no_frame(self):
        repo = resolved_repo(self)
        frame(repo.root, "   \n\n")
        self.assertEqual(verdict(verify_frame(repo.root)), "FRAME-MISSING")

    def test_the_refusal_names_the_path_it_looked_for(self):
        repo = resolved_repo(self)
        proc = verify_frame(repo.root)
        self.assertIn("MISSION_FRAME.md", proc.stdout + proc.stderr)

    def test_a_frame_without_a_receipt_refuses_rather_than_passing(self):
        """No orientation happened at all -- the frame cannot be checked
        against anything, and 'cannot check' is never 'passes'."""
        repo = RepoFixture(self)
        frame(repo.root, GOOD_FRAME)
        proc = verify_frame(repo.root)
        self.assertEqual(verdict(proc), "RECEIPT-MISSING")
        self.assertEqual(proc.returncode, 12)


class VerifyFrameResolved(unittest.TestCase):
    def test_a_frame_citing_real_map_anchors_passes(self):
        repo = resolved_repo(self)
        frame(repo.root, GOOD_FRAME)
        proc = verify_frame(repo.root)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(verdict(proc), "FRAME-OK")

    def test_an_anchor_that_does_not_resolve_refuses_and_names_it(self):
        repo = resolved_repo(self)
        frame(repo.root, UNKNOWN_ANCHOR_FRAME)
        proc = verify_frame(repo.root)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(verdict(proc), "FRAME-REFUSED")
        self.assertIn("struct:ghost_module", proc.stdout + proc.stderr)
        # ...and does NOT indict the anchor that does resolve.
        self.assertNotIn("struct:app does not", proc.stdout + proc.stderr)

    def test_a_frame_cut_from_source_paths_refuses(self):
        repo = resolved_repo(self)
        frame(repo.root, CODE_CUT_FRAME)
        proc = verify_frame(repo.root)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(verdict(proc), "FRAME-REFUSED")
        self.assertIn("src/engine/solver.py", proc.stdout + proc.stderr)

    def test_a_frame_with_no_citation_at_all_refuses(self):
        repo = resolved_repo(self)
        frame(repo.root, "# Mission Frame\n\nI thought about it a lot.\n")
        self.assertNotEqual(verify_frame(repo.root).returncode, 0)

    def test_placeholder_anchors_do_not_count_as_citations(self):
        """An unfilled MISSION_FRAME scaffold must not satisfy the check."""
        repo = resolved_repo(self)
        frame(repo.root, "## Structural Anchors\n- `struct:<id>` — path/symbol, level\n")
        self.assertNotEqual(verify_frame(repo.root).returncode, 0)

    def test_the_shipped_mission_frame_template_itself_does_not_pass(self):
        """The scaffold this repo ships, verbatim. Uses the real committed file
        so it cannot rot into a fixture nobody maintains."""
        template = ROOT / "skills/commander/templates/MISSION_FRAME.template.md"
        self.assertTrue(template.is_file(), template)
        repo = resolved_repo(self)
        frame(repo.root, template.read_text(encoding="utf-8"))
        self.assertNotEqual(verify_frame(repo.root).returncode, 0)


class VerifyFrameContractShape(unittest.TestCase):
    def test_orient_never_prints_an_anchor_id(self):
        """LOAD-BEARING -- do not drop this test.

        If `orient` echoed the ids it found, the citation check would be
        self-satisfying: an agent could paste back what the tool told it and
        never open the map. The proof that the map was read has to come from
        somewhere the tool did not hand over.
        """
        repo = RepoFixture(self)
        repo.file("docs/architecture/index.md", REAL_INDEX)
        repo.file("docs/architecture/packets/physics.md", REAL_PACKET)
        proc = orient(repo.root)
        self.assertEqual(verdict(proc), "RESOLVED")
        found = mo.ANCHOR_RE.findall(proc.stdout) if hasattr(mo.ANCHOR_RE, "findall") else []
        self.assertEqual(found, [], f"orient leaked anchor ids on stdout: {proc.stdout!r}")
        # Belt and braces: the raw token must not appear either.
        for token in ("struct:app", "capability:serve_requests", "struct:physics"):
            with self.subTest(token=token):
                self.assertNotIn(token, proc.stdout)

    def test_verify_frame_only_echoes_ids_the_frame_itself_cited(self):
        """The same rule for the checker: naming the offending citation is
        required, listing the valid inventory would hand over the answer."""
        repo = resolved_repo(self)
        frame(repo.root, UNKNOWN_ANCHOR_FRAME)
        out = verify_frame(repo.root).stdout + verify_frame(repo.root).stderr
        self.assertIn("struct:ghost_module", out)
        # `capability:serve_requests` is in the map but NOT in the frame.
        self.assertNotIn("capability:serve_requests", out)
        self.assertNotIn("decision:one_canonical_path", out)

    def test_every_verify_frame_first_line_is_a_reserved_literal(self):
        repo = resolved_repo(self)
        cases = [verify_frame(repo.root)]
        frame(repo.root, GOOD_FRAME)
        cases.append(verify_frame(repo.root))
        frame(repo.root, CODE_CUT_FRAME)
        cases.append(verify_frame(repo.root))
        cases.append(verify_frame(repo.root, "never-oriented"))
        for proc in cases:
            with self.subTest(first=verdict(proc)):
                self.assertIn(verdict(proc), mo.RESERVED_FIRST_LINES)
                self.assertTrue(verdict(proc).strip())

    def test_verify_frame_invents_no_new_exit_codes(self):
        repo = resolved_repo(self)
        seen = {verify_frame(repo.root).returncode}
        frame(repo.root, GOOD_FRAME)
        seen.add(verify_frame(repo.root).returncode)
        frame(repo.root, CODE_CUT_FRAME)
        seen.add(verify_frame(repo.root).returncode)
        frame(repo.root, UNKNOWN_ANCHOR_FRAME)
        seen.add(verify_frame(repo.root).returncode)
        self.assertTrue(seen <= {mo.EXIT_OK, *mo.SEMANTIC_EXIT_CODES}, seen)

    def test_an_unresolvable_root_receipt_never_lets_a_frame_pass(self):
        repo = RepoFixture(self)
        degraded_receipt(repo.root, "w", mode="UNRESOLVABLE-ROOT")
        frame(repo.root, GOOD_FRAME)
        proc = verify_frame(repo.root)
        self.assertEqual(proc.returncode, 11)

    def test_report_only_is_the_flag_flip_between_gating_and_reporting(self):
        """The gate-vs-report ruling must be a flag flip, not a rebuild -- and
        the reported verdict must be unchanged, only its blocking-ness."""
        repo = resolved_repo(self)
        frame(repo.root, CODE_CUT_FRAME)
        gating = verify_frame(repo.root)
        reporting = verify_frame(repo.root, "w", "--report-only")
        self.assertNotEqual(gating.returncode, 0)
        self.assertEqual(reporting.returncode, 0)
        self.assertEqual(verdict(gating), verdict(reporting))
        self.assertIn("would exit", reporting.stdout)


# =============================================================================
# The degraded case's PARTIAL independent oracle
# =============================================================================
#
# The degraded check's declared weakness is that substitutes are SELF-SELECTED:
# it verifies the author cited what the author declared. A fixed, corpus-declared
# fallback search order that `orient` PROBES on the filesystem converts HALF of
# that into an oracle the agent does not author -- whether one of those paths
# resolved is answered by the filesystem. It does NOT close the gap: the agent
# still chooses what to declare, and anything outside the set stays labelled
# unverified. Both labels are asserted below precisely so the receipt's
# distinction between them cannot rot into a decoration.


class KnownFallbackProbe(unittest.TestCase):
    def test_orient_records_which_known_fallbacks_actually_exist(self):
        """Existence is settled by the filesystem, not by the agent's account."""
        repo = RepoFixture(self)
        repo.file("README.md", "doctrine\n")
        repo.file("CLAUDE.md", "more doctrine\n")
        orient(repo.root, "w", "--substitute", "README.md",
               "--unmapped", "everything structural", "--escalation", "ask commander")
        probed = {e["path"]: e for e in receipt_of(repo.root)["fallbacks_probed"]}
        self.assertEqual(tuple(probed), mo.KNOWN_FALLBACKS)
        self.assertTrue(probed["README.md"]["exists"])
        self.assertTrue(probed["CLAUDE.md"]["exists"])
        self.assertFalse(probed["AGENTS.md"]["exists"])

    def test_a_probed_fallback_that_exists_is_hash_pinned_too(self):
        repo = RepoFixture(self)
        repo.file("AGENTS.md", "agent doctrine\n")
        orient(repo.root, "w", "--substitute", "AGENTS.md",
               "--unmapped", "structure", "--escalation", "commander")
        probed = {e["path"]: e for e in receipt_of(repo.root)["fallbacks_probed"]}
        self.assertTrue(mo.is_content_hash(probed["AGENTS.md"]["content_hash"]))
        self.assertIsNone(probed["README.md"]["content_hash"])

    def test_the_probe_reports_a_fallback_the_agent_never_declared(self):
        """The oracle's whole point: it answers independently of the agent."""
        repo = RepoFixture(self)
        repo.file("README.md", "doctrine\n")
        repo.file("AGENTS.md", "undeclared but present\n")
        orient(repo.root, "w", "--substitute", "README.md",
               "--unmapped", "structure", "--escalation", "commander")
        receipt = receipt_of(repo.root)
        declared = [s["path"] for s in receipt["substitutes"]]
        probed = {e["path"]: e["exists"] for e in receipt["fallbacks_probed"]}
        self.assertNotIn("AGENTS.md", declared)
        self.assertTrue(probed["AGENTS.md"])


class SubstituteLabels(unittest.TestCase):
    """BOTH labels, asserted on real receipts written by the real CLI."""

    def _label(self, repo_files: dict, substitute: str) -> str:
        repo = RepoFixture(self)
        for rel, text in repo_files.items():
            repo.file(rel, text)
        orient(repo.root, "w", "--substitute", substitute,
               "--unmapped", "structure", "--escalation", "commander")
        entries = receipt_of(repo.root)["substitutes"]
        self.assertEqual(len(entries), 1, entries)
        return entries[0]["source"]

    def test_a_present_known_fallback_is_labelled_known_fallback(self):
        self.assertEqual(
            self._label({"README.md": "doctrine\n"}, "README.md"),
            mo.LABEL_KNOWN_FALLBACK,
        )

    def test_a_path_outside_the_known_set_is_labelled_agent_declared(self):
        self.assertEqual(
            self._label({"docs/notes/whatever.md": "my notes\n"}, "docs/notes/whatever.md"),
            mo.LABEL_AGENT_DECLARED,
        )

    def test_a_declared_but_ABSENT_known_fallback_is_not_labelled_verified(self):
        """Set membership alone must not earn the verified label -- that would
        be the self-attestation this labelling exists to separate out."""
        self.assertEqual(self._label({}, "README.md"), mo.LABEL_AGENT_DECLARED)

    def test_a_docs_index_fallback_is_labelled_known_fallback(self):
        self.assertEqual(
            self._label({"docs/index.md": "the docs index\n"}, "docs/index.md"),
            mo.LABEL_KNOWN_FALLBACK,
        )

    def test_the_label_never_upgrades_the_pin(self):
        """A label is a provenance note, not a discharge: an absent substitute
        still refuses, whatever it is called."""
        repo = RepoFixture(self)
        orient(repo.root, "w", "--substitute", "README.md",
               "--unmapped", "structure", "--escalation", "commander")
        entry = receipt_of(repo.root)["substitutes"][0]
        self.assertEqual(entry["source"], mo.LABEL_AGENT_DECLARED)
        self.assertIsNone(entry["content_hash"])
        proc = run_cli("verify-orientation", "--root", str(repo.root), "--work-id", "w")
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class VerifyFrameDegraded(unittest.TestCase):
    """The degraded arm of verify-frame, against the hash-pinned prior."""

    def degraded_repo(self, *extra_files: str) -> RepoFixture:
        repo = RepoFixture(self)
        repo.file("README.md", "the repo's own doctrine\n")
        for rel in extra_files:
            repo.file(rel, "more doctrine\n")
        proc = orient(repo.root, "w", "--substitute", "README.md",
                      "--unmapped", "everything structural",
                      "--escalation", "ask commander for a map")
        self.assertTrue(verdict(proc).startswith("DEGRADED-"), proc.stdout)
        return repo

    def test_a_degraded_frame_citing_a_declared_substitute_passes(self):
        repo = self.degraded_repo()
        frame(repo.root, DEGRADED_FRAME)
        proc = verify_frame(repo.root)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(verdict(proc), "FRAME-OK")

    def test_a_degraded_frame_citing_an_UNDECLARED_fallback_refuses(self):
        """The point of pinning: the frame is compared against a COMMITTED
        prior declaration, not a same-breath assertion by the same agent."""
        repo = self.degraded_repo("CLAUDE.md")
        frame(repo.root, UUNDECLARED_FALLBACK_FRAME)
        proc = verify_frame(repo.root)
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(verdict(proc), "FRAME-REFUSED")
        self.assertIn("CLAUDE.md", proc.stdout + proc.stderr)

    def test_a_degraded_frame_citing_map_anchors_refuses(self):
        """No map was read, so a map anchor cannot be a member of anything."""
        repo = self.degraded_repo()
        frame(repo.root, GOOD_FRAME)
        self.assertNotEqual(verify_frame(repo.root).returncode, 0)

    def test_a_degraded_frame_citing_nothing_declared_refuses(self):
        repo = self.degraded_repo()
        frame(repo.root, "# Mission Frame\n\nI read some things.\n")
        self.assertNotEqual(verify_frame(repo.root).returncode, 0)


# =============================================================================
# The provenance label must be REPORTED, not merely stored
# =============================================================================
#
# g2 review BLOCK: `substitute_label()` was reachable ONLY from `self_test()`.
# The `source` key was written to every receipt and read back by nothing -- no
# output surface, no test outside the module's own harness. A module that ships
# its own test harness as a subcommand launders dead code as live: a caller-grep
# rooted at `main` finds `self_test` via `--self-test`, so every self-tested
# helper comes back reachable.
#
# These tests live OUTSIDE `self_test` on purpose. That is the whole point: the
# label is only real if a reader who never runs `--self-test` can see it.


class SubstituteProvenanceIsReported(unittest.TestCase):
    def degraded_with(self, files: dict, *substitutes: str) -> subprocess.CompletedProcess:
        """Orient a mapless repo declaring `substitutes`, then report on it."""
        repo = RepoFixture(self)
        for rel, text in files.items():
            repo.file(rel, text)
        args = []
        for sub in substitutes:
            args += ["--substitute", sub]
        orient(repo.root, "w", *args, "--unmapped", "everything structural",
               "--escalation", "ask commander for a map")
        return verify(repo.root, "w")

    def test_a_present_known_fallback_is_REPORTED_as_known_fallback(self):
        proc = self.degraded_with({"README.md": "doctrine\n"}, "README.md")
        self.assertIn("README.md", proc.stdout)
        self.assertIn(mo.LABEL_KNOWN_FALLBACK, proc.stdout)

    def test_an_agent_declared_substitute_is_REPORTED_as_unverified(self):
        proc = self.degraded_with(
            {"docs/notes/whatever.md": "my notes\n"}, "docs/notes/whatever.md"
        )
        self.assertIn(mo.LABEL_AGENT_DECLARED, proc.stdout)
        self.assertIn("UNVERIFIED", proc.stdout)

    def test_BOTH_labels_appear_in_one_real_report(self):
        """The distinction is only useful if a reader can see both at once."""
        proc = self.degraded_with(
            {"README.md": "doctrine\n", "docs/notes/mine.md": "notes\n"},
            "README.md",
            "docs/notes/mine.md",
        )
        self.assertIn(mo.LABEL_KNOWN_FALLBACK, proc.stdout)
        self.assertIn(mo.LABEL_AGENT_DECLARED, proc.stdout)

    def test_a_receipt_with_no_source_key_reports_as_agent_declared(self):
        """Forward compatibility in the CONSERVATIVE direction: a receipt from
        before the label existed must never be UPGRADED by omission."""
        repo = RepoFixture(self)
        repo.file("README.md", "doctrine\n")
        degraded_receipt(repo.root, "w")  # COMPLETE_RECORD carries no `source`
        proc = verify(repo.root, "w")
        self.assertIn(mo.LABEL_AGENT_DECLARED, proc.stdout)
        self.assertNotIn(mo.LABEL_KNOWN_FALLBACK, proc.stdout)

    def test_an_unrecognised_source_value_reports_as_agent_declared(self):
        repo = RepoFixture(self)
        degraded_receipt(
            repo.root, "w",
            substitutes=[{"path": "README.md", "content_hash": "a" * 64, "source": "trust-me"}],
        )
        proc = verify(repo.root, "w")
        self.assertIn(mo.LABEL_AGENT_DECLARED, proc.stdout)
        self.assertNotIn("trust-me", proc.stdout)

    def test_the_report_still_prints_no_anchor_id(self):
        """The anti-leak rule survives the new output. A substitute path is not
        an anchor id -- and it was declared BY the agent, so echoing it back
        hands over nothing the agent did not already write."""
        repo = RepoFixture(self)
        repo.file("README.md", "doctrine mentioning `struct:app` in prose\n")
        orient(repo.root, "w", "--substitute", "README.md",
               "--unmapped", "structure", "--escalation", "commander")
        proc = verify(repo.root, "w")
        self.assertEqual(mo.ANCHOR_RE.findall(proc.stdout), [], proc.stdout)

    def test_the_provenance_line_is_never_line_zero(self):
        """The reserved-first-line contract outranks the new output."""
        proc = self.degraded_with({"README.md": "doctrine\n"}, "README.md")
        self.assertIn(verdict(proc), mo.RESERVED_FIRST_LINES)


if __name__ == "__main__":
    unittest.main()
