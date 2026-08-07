"""Tests for `scripts/context_manifest.py` — the deterministic projection substrate.

The manifest answers *what was made available to an agent, at which revision* —
delivery, not use. These tests are deliberately adversarial: a suite that only
parses the real shipped corpus proves the corpus is clean, not that the tool is
correct, so most fixtures below are authored to make the producer return a
*wrong* answer.
"""

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cm = load("context_manifest")


def _is_gated_checklist(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return False
    return (
        isinstance(data, dict)
        and data.get("type") == "gated"
        and isinstance(data.get("items"), list)
        and isinstance(data.get("tasks"), dict)
        and bool(data["items"])
    )


class RevIsGitBlobOid(unittest.TestCase):
    """`rev` is the git blob OID of the LF-normalised bytes, computed in-process.

    No `git` subprocess in production code; the subprocess here is the *oracle*
    the implementation is measured against.
    """

    TARGETS = [
        "scripts/checklist_engine.py",
        "scripts/agent_work_root.py",
        "skills/commander/templates/COMMANDER_SPINE.template.json",
        ".gitattributes",
    ]

    def _git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
        )

    def test_rev_equals_git_hash_object_for_real_tracked_files(self):
        # Real tracked files in this repo — not fixtures. `git hash-object` applies
        # the repo's `.gitattributes` (`* text=auto`) clean filter to the working-tree
        # bytes, which is exactly the normalisation `rev` reproduces in-process. This
        # holds whether or not the file is dirty, which is the point: the identity
        # function needs no case analysis.
        for rel in self.TARGETS:
            with self.subTest(path=rel):
                oracle = self._git("hash-object", "--", rel)
                self.assertEqual(oracle.returncode, 0, oracle.stderr)
                self.assertEqual(
                    cm.rev((ROOT / rel).read_bytes()), oracle.stdout.strip()
                )

    def test_rev_equals_git_rev_parse_head_for_tracked_clean_files(self):
        # The committed-object half of the same equality — meaningful only where the
        # working tree matches HEAD, so cleanliness is measured, never assumed.
        clean = [
            rel for rel in self.TARGETS
            if not self._git("status", "--porcelain", "--", rel).stdout.strip()
        ]
        self.assertTrue(clean, "expected at least one clean tracked target")
        for rel in clean:
            with self.subTest(path=rel):
                oracle = self._git("rev-parse", f"HEAD:{rel}")
                self.assertEqual(oracle.returncode, 0, oracle.stderr)
                self.assertEqual(
                    cm.rev((ROOT / rel).read_bytes()), oracle.stdout.strip()
                )

    def test_rev_of_crlf_and_lf_twins_is_identical(self):
        # The false-FAIL hunt: CRLF is this corpus's single largest named
        # irreproducibility source. Twins of identical content MUST agree.
        lf = b"# doctrine\n\nline one\nline two\n"
        crlf = b"# doctrine\r\n\r\nline one\r\nline two\r\n"
        self.assertNotEqual(lf, crlf)
        self.assertEqual(cm.rev(lf), cm.rev(crlf))

    def test_rev_crlf_twin_written_to_disk_matches_git_hash_object(self):
        # Same property, proven end-to-end against the oracle rather than against
        # `rev` alone: a CRLF file on disk hashes to its LF twin's OID.
        with tempfile.TemporaryDirectory() as tmp:
            lf_path = Path(tmp) / "lf.md"
            crlf_path = Path(tmp) / "crlf.md"
            lf_path.write_bytes(b"alpha\nbeta\n")
            crlf_path.write_bytes(b"alpha\r\nbeta\r\n")
            oracle = subprocess.run(
                ["git", "hash-object", "--", str(lf_path)],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(oracle.returncode, 0, oracle.stderr)
            expected = oracle.stdout.strip()
            self.assertEqual(cm.rev(lf_path.read_bytes()), expected)
            self.assertEqual(cm.rev(crlf_path.read_bytes()), expected)

    def _raw_blob_oid(self, data):
        """Git's blob OID of exactly these bytes, with no normalisation. The second
        oracle: it lets the divergence test say *why* the two disagree, not merely
        that they do."""
        return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()

    def test_rev_diverges_from_git_for_content_git_refuses_to_normalise(self):
        # The equality envelope, pinned at its edge. Under `* text=auto` git
        # declines to normalise on CONTENT grounds as well as on attribute grounds
        # — a NUL byte (auto-detected binary) or a lone CR (normalising would not
        # round-trip) — and stores the raw bytes instead. `rev` normalises
        # unconditionally, so for exactly this content it deliberately differs from
        # the oracle.
        #
        # This is a characterization test. It does not ask for the divergence to be
        # fixed: `rev` is settled, and no file in any declarable root is in this
        # class. It exists because a `.gitattributes` check can only ever see the
        # attribute half of the condition (that half is
        # `test_gitattributes_exempts_no_path_from_lf_normalisation` below), so
        # without this the content half would be a claim nothing checks. If git's
        # normalisation rules ever move, the two explanatory assertions below say
        # which half moved.
        diverging = {
            "lone_CR": b"alpha\rbeta\r\n",
            "CR_CR_LF": b"alpha\r\r\nbeta\r\n",
            "NUL_byte": b"\x00\x01\x02BINARY\r\nrow\r\n",
        }
        with tempfile.TemporaryDirectory() as tmp:
            for name, data in diverging.items():
                with self.subTest(case=name):
                    path = Path(tmp) / f"{name}.bin"
                    path.write_bytes(data)
                    oracle = self._git("hash-object", "--", str(path))
                    self.assertEqual(oracle.returncode, 0, oracle.stderr)
                    oid = oracle.stdout.strip()
                    # The divergence itself — known, documented in `rev`'s docstring.
                    self.assertNotEqual(cm.rev(data), oid)
                    # Why: git stored the bytes verbatim...
                    self.assertEqual(oid, self._raw_blob_oid(data))
                    # ...while `rev` normalised them.
                    self.assertEqual(
                        cm.rev(data), self._raw_blob_oid(data.replace(b"\r\n", b"\n"))
                    )
            # Control, through the same machinery: content git DOES normalise still
            # agrees. Without this the assertNotEqual above would also pass if the
            # oracle were simply broken.
            control = b"alpha\r\nbeta\r\n"
            control_path = Path(tmp) / "control.md"
            control_path.write_bytes(control)
            oracle = self._git("hash-object", "--", str(control_path))
            self.assertEqual(oracle.returncode, 0, oracle.stderr)
            self.assertEqual(cm.rev(control), oracle.stdout.strip())
            self.assertNotEqual(self._raw_blob_oid(control), oracle.stdout.strip())

    def test_gitattributes_exempts_no_path_from_lf_normalisation(self):
        # The configuration half of `rev`'s equality envelope, asserted in a
        # committed test rather than in a run-local gate check that no reader of
        # `main` can open. `rev` equals `git hash-object` only while git actually
        # normalises the bytes; a `-text` or `binary` attribute makes git stop, and
        # the two then diverge silently for every path the pattern covers.
        #
        # Deliberately pattern-blind: it rejects the attribute on ANY pattern, not
        # only on `*`. An exemption scoped to a subtree — `skills/**/references/*.md
        # -text`, `docs/agents/*.md -text` — is the dangerous shape precisely
        # because it looks narrow while covering exactly the corpus `context_refs`
        # declares, and a check written against `*` alone would wave it through.
        attributes = ROOT / ".gitattributes"
        self.assertTrue(attributes.exists(), ".gitattributes is part of the invariant")
        offenders = []
        for number, line in enumerate(
            attributes.read_text(encoding="utf-8").splitlines(), start=1
        ):
            body = line.split("#", 1)[0].strip()
            if not body:
                continue
            pattern, *attrs = body.split()
            for attr in attrs:
                # `-text`, `binary` (a macro for `-text -diff`), and `text=false`
                # all take a path out of LF normalisation.
                if attr in ("-text", "binary", "text=false"):
                    offenders.append((number, pattern, attr))
        self.assertEqual(
            offenders, [],
            "a path exempted from LF normalisation makes rev() diverge from "
            "git hash-object for that path, silently and permanently",
        )

    def test_rev_of_empty_bytes_is_the_git_empty_blob(self):
        self.assertEqual(cm.rev(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")

    def test_rev_is_sensitive_to_content_change(self):
        # A stale record must not silently pass: change the bytes, the rev moves.
        self.assertNotEqual(cm.rev(b"alpha\n"), cm.rev(b"alpha!\n"))


def checklist(declaration=None, items=("context",), work_id="w-1"):
    """A minimal real-shaped checklist. `declaration=None` means the task carries
    no `context_refs` at all — the pre-existing-spine case."""
    tasks = {}
    for item in items:
        task = {"id": item, "title": item, "imperative": "…", "status": "pending"}
        if declaration is not None and item == items[0]:
            task["context_refs"] = list(declaration)
        tasks[item] = task
    return {"work_id": work_id, "type": "gated", "items": list(items), "tasks": tasks}


def _dirty_key_paths(obj, prefix="") -> list:
    """Every JSON-pointer-ish path at which a key named `dirty` occurs, at any
    depth. Empty list means the field is genuinely gone rather than merely moved
    somewhere the caller forgot to look (#327, #305 g4)."""
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            here = f"{prefix}/{key}"
            if key == "dirty":
                found.append(here)
            found.extend(_dirty_key_paths(value, here))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            found.extend(_dirty_key_paths(value, f"{prefix}/{index}"))
    return found


class ManifestEnvelope(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.skill = Path(self.tmp.name) / "skill"
        self.repo = Path(self.tmp.name) / "repo"
        (self.skill / "references").mkdir(parents=True)
        (self.repo / "docs").mkdir(parents=True)
        (self.skill / "references" / "doctrine.md").write_bytes(b"doctrine\n")
        (self.repo / "docs" / "glossary.md").write_bytes(b"glossary\n")
        self.roots = {"skill": self.skill, "repo": self.repo, "durable": self.repo}

    def build(self, declaration, **kw):
        return cm.build_manifest(checklist(declaration), self.roots, **kw)

    def test_envelope_has_exactly_five_keys(self):
        m = self.build([{"root": "skill", "path": "references/doctrine.md", "required": True}])
        self.assertEqual(list(m), ["contract", "step", "files", "repo_rev", "run"])
        self.assertEqual(m["contract"], cm._MANIFEST_CONTRACT_VERSION)
        self.assertEqual(m["step"], "context")

    def test_row_is_exactly_root_path_rev(self):
        # Not `bytes` (redundant against rev), not `state` (it IS rev == None), and
        # emphatically not `tracked`/`canon` — trackedness is environment-varying,
        # which is a determinism hazard rather than a feature.
        m = self.build([{"root": "skill", "path": "references/doctrine.md", "required": True}])
        self.assertEqual(list(m["files"][0]), ["root", "path", "rev"])
        self.assertEqual(m["files"][0]["rev"], cm.rev(b"doctrine\n"))

    def test_required_lives_in_the_declaration_not_the_manifest(self):
        m = self.build([{"root": "skill", "path": "references/doctrine.md", "required": True}])
        self.assertNotIn("required", m["files"][0])

    def test_absent_file_yields_null_rev_and_keeps_the_row(self):
        # Absence-by-design is normal: a doctrine overlay legitimately missing in a
        # skill-source repo must not drop the row and must not raise.
        m = self.build([{"root": "repo", "path": "docs/agents/ORCHESTRATOR_CONTEXT.md",
                         "required": False}])
        self.assertEqual(m["files"], [{"root": "repo",
                                       "path": "docs/agents/ORCHESTRATOR_CONTEXT.md",
                                       "rev": None}])

    def test_present_but_unreadable_raises_so_null_means_one_thing(self):
        with self.assertRaises(OSError):
            self.build([{"root": "skill", "path": "references", "required": True}])

    def test_path_escaping_its_root_raises(self):
        for bad in ("../outside.md", "references/../../outside.md", "..\\outside.md",
                    "/etc/passwd"):
            with self.subTest(path=bad):
                with self.assertRaises(cm.DeclarationError):
                    self.build([{"root": "skill", "path": bad, "required": True}])

    def test_a_drive_letter_path_is_rejected_not_silently_folded(self):
        # `PurePosixPath("C:/Windows/win.ini").is_absolute()` is False and its parts
        # are ('C:', 'Windows', 'win.ini'), so the posix-shaped guards see nothing
        # wrong; `ntpath.join` then applies same-drive semantics and folds the whole
        # thing to `<root>\Windows\win.ini`, which IS inside the root, so the escape
        # guard passes too. The result would be a manifest row whose recorded `path`
        # is not the path that was read — which defeats the record's entire purpose
        # — and the same declaration would name a literal directory called `C:` on
        # POSIX, i.e. it is content-divergent across operating systems. A colon in a
        # declared path has the same effect in its non-leading form (`file.md:name`
        # is an NTFS alternate data stream on Windows and an ordinary filename on
        # POSIX), so the guard rejects the character, not just the drive shape.
        for bad in ("C:/Windows/win.ini", "c:/windows/win.ini", "C:Windows/win.ini",
                    "docs/glossary.md:stream", "docs/a:b/c.md"):
            with self.subTest(path=bad):
                with self.assertRaises(cm.DeclarationError):
                    self.build([{"root": "repo", "path": bad, "required": True}])

    def test_unknown_root_token_or_unmapped_root_raises(self):
        with self.assertRaises(cm.DeclarationError):
            self.build([{"root": "elsewhere", "path": "x.md", "required": True}])
        with self.assertRaises(cm.DeclarationError):
            cm.build_manifest(
                checklist([{"root": "durable", "path": "x.md", "required": True}]),
                {"skill": self.skill, "repo": self.repo},
            )

    def test_malformed_entries_fail_visibly(self):
        for bad in ([{"path": "x.md"}], [{"root": "skill"}], ["x.md"],
                    [{"root": "skill", "path": "x.md", "bytes": 3}]):
            with self.subTest(entry=bad):
                with self.assertRaises(cm.DeclarationError):
                    self.build(bad)

    def test_a_declaration_that_is_not_a_list_raises_rather_than_projecting_nothing(self):
        # `context_refs: "docs/agents/GLOSSARY.md"` is an entirely plausible
        # authoring mistake, and the silent reading of it is the worst one: a string
        # is a Sequence, a dict is iterable, and either would project an empty (or
        # nonsense) manifest that looks perfectly valid. Absent means "nothing
        # declared"; malformed must mean "stop", not "nothing declared".
        for bad in ("docs/agents/GLOSSARY.md",
                    {"root": "repo", "path": "docs/agents/GLOSSARY.md"},
                    b"docs/agents/GLOSSARY.md",
                    7,
                    True):
            with self.subTest(declaration=bad):
                with self.assertRaises(cm.DeclarationError):
                    cm.declaration_of({"context_refs": bad})
                with self.assertRaises(cm.DeclarationError):
                    cm.build_manifest(
                        {"work_id": "w", "type": "gated", "items": ["context"],
                         "tasks": {"context": {"id": "context", "title": "c",
                                               "imperative": "…", "status": "pending",
                                               "context_refs": bad}}},
                        self.roots,
                    )
        # …while the absent case stays exactly as forgiving as it was.
        self.assertEqual(cm.declaration_of({}), ())
        self.assertEqual(cm.declaration_of({"context_refs": None}), ())
        self.assertEqual(cm.declaration_of({"context_refs": []}), ())

    def test_declaration_order_is_content_and_a_permutation_is_a_difference(self):
        a = {"root": "skill", "path": "references/doctrine.md", "required": True}
        b = {"root": "repo", "path": "docs/glossary.md", "required": True}
        forward = self.build([a, b])
        reversed_ = self.build([b, a])
        self.assertEqual([r["path"] for r in forward["files"]],
                         ["references/doctrine.md", "docs/glossary.md"])
        # Order is content: the two must NOT compare equal, or a doctrine reordering
        # would be invisible in the record.
        self.assertNotEqual(cm.content(forward), cm.content(reversed_))

    def test_duplicate_declared_paths_are_both_retained(self):
        e = {"root": "skill", "path": "references/doctrine.md", "required": True}
        m = self.build([e, e])
        self.assertEqual(len(m["files"]), 2)

    def test_no_absolute_root_path_appears_in_content(self):
        m = self.build([{"root": "skill", "path": "references/doctrine.md", "required": True}])
        rendered = cm.encode(cm.content(m))
        for root in self.roots.values():
            self.assertNotIn(Path(root).as_posix(), rendered)
            self.assertNotIn(str(root), rendered)
        # …and the varying facts ARE present, in /run and only there.
        self.assertIn(self.skill.as_posix(), cm.encode(m["run"]))

    def test_content_excludes_exactly_the_run_subtree(self):
        m = self.build([{"root": "skill", "path": "references/doctrine.md", "required": True}])
        # BIDIRECTIONAL. `set(m) - set(content(m)) == {"run"}` on its own is blind to
        # any key `content()` *adds* — the direction a leak actually travels.
        self.assertEqual(set(m), set(cm.content(m)) | {"run"})
        self.assertNotIn("run", cm.content(m))

    def test_the_envelope_is_exactly_the_content_allowlist_plus_run(self):
        # The weld that makes "/run is the entire exclusion set" true rather than
        # merely stated: the produced envelope and the admitted key list must agree.
        # Adding a key to either alone fails here, so neither can drift.
        m = self.build([{"root": "skill", "path": "references/doctrine.md", "required": True}])
        self.assertEqual(set(m), set(cm.CONTENT_KEYS) | {"run"})
        self.assertEqual(list(cm.content(m)), list(cm.CONTENT_KEYS))

    def test_a_varying_field_placed_outside_run_cannot_become_content(self):
        # The cold panel's surviving mutation, in its two forms. `cwd` is the
        # environment fact `run_facts()` already reads, so this is the exact leak.
        m = self.build([{"root": "skill", "path": "references/doctrine.md", "required": True}])

        # Form 1 — the producer grows a top-level key. `content()` admits rather than
        # denies, so the key is excluded by default…
        leaked = dict(m)
        leaked["host_cwd"] = Path.cwd().as_posix()
        self.assertNotIn("host_cwd", cm.content(leaked))
        # …and its mere presence in the envelope is a failure, not a silent pass.
        with self.assertRaises(AssertionError):
            self.assertEqual(set(leaked), set(cm.content(leaked)) | {"run"})

        # Form 2 — `content()` itself is rewritten to promote a `/run` fact. The
        # bidirectional assertion is what catches this one.
        def leaky_content(manifest):
            out = {k: v for k, v in manifest.items() if k != "run"}
            out["host_cwd"] = manifest.get("run", {}).get("host", {}).get("cwd")
            return out

        with self.assertRaises(AssertionError):
            self.assertEqual(set(m), set(leaky_content(m)) | {"run"})

    def test_manifest_never_carries_file_contents(self):
        # Delivery, not use — and metadata only. The bytes of a declared file must
        # not appear anywhere in the record.
        m = self.build([{"root": "skill", "path": "references/doctrine.md", "required": True}])
        self.assertNotIn("doctrine\n", cm.encode(m))

    def test_reader_is_the_single_injected_impure_edge(self):
        seen = []

        def fake_reader(path):
            seen.append(path)
            return b"injected\n"

        m = self.build([{"root": "repo", "path": "docs/nonexistent.md", "required": True}],
                       reader=fake_reader)
        self.assertEqual(len(seen), 1)
        self.assertEqual(m["files"][0]["rev"], cm.rev(b"injected\n"))

    def test_stale_record_does_not_silently_pass(self):
        # A file whose bytes changed but whose recorded rev did not: rebuilding must
        # disagree with the stale record rather than quietly re-validating it.
        entry = {"root": "skill", "path": "references/doctrine.md", "required": True}
        before = self.build([entry])
        (self.skill / "references" / "doctrine.md").write_bytes(b"doctrine, amended\n")
        after = self.build([entry])
        self.assertNotEqual(cm.content(before), cm.content(after))

    def test_untracked_vs_absent_disagreement_is_confined_to_rev(self):
        # The amendment defect: the same declared path is present in one environment
        # and absent in another. Both environments must still agree on the SHAPE of
        # the content — same step, same rows, same order — so the difference is one
        # honest `rev`, never a structural disagreement.
        entry = {"root": "repo", "path": "docs/agents/ORCHESTRATOR_CONTEXT.md",
                 "required": False}
        absent = self.build([entry])
        (self.repo / "docs" / "agents").mkdir()
        (self.repo / "docs" / "agents" / "ORCHESTRATOR_CONTEXT.md").write_bytes(b"x\n")
        present = self.build([entry])
        self.assertIsNone(absent["files"][0]["rev"])
        self.assertEqual(present["files"][0]["rev"], cm.rev(b"x\n"))
        self.assertEqual([(r["root"], r["path"]) for r in absent["files"]],
                         [(r["root"], r["path"]) for r in present["files"]])


#: Every real, committed, gated spine/plan template this repo ships. Used instead of
#: authored fixtures wherever the property under test is "existing spines keep
#: working" — a fixture would prove only that the fixture works.
REAL_SPINE_TEMPLATES = sorted(
    p for p in (ROOT / "skills").glob("*/templates/*.json")
    if _is_gated_checklist(p)
)


class SelectionUsesTheEnginesOwnSelector(unittest.TestCase):
    """`active_id()` is THE selector. A second one would drift silently."""

    def test_producer_imports_the_engines_selector_and_defines_no_second_one(self):
        # The function object the producer calls is compiled from the engine's own
        # source file — not a copy, not a reimplementation.
        self.assertEqual(
            Path(cm.active_id.__code__.co_filename).resolve(),
            (ROOT / "scripts" / "checklist_engine.py").resolve(),
        )
        source = (ROOT / "scripts" / "context_manifest.py").read_text(encoding="utf-8")
        self.assertIn("from checklist_engine import active_id", source)
        self.assertNotIn("def active_id", source)

    def test_step_tracks_active_id_as_items_complete(self):
        cl = checklist(
            [{"root": "skill", "path": "references/doctrine.md", "required": True}],
            items=("context", "understand", "plan"),
        )
        engine = load("checklist_engine")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "references").mkdir()
            (Path(tmp) / "references" / "doctrine.md").write_bytes(b"doctrine\n")
            roots = {"skill": Path(tmp), "repo": Path(tmp), "durable": Path(tmp)}
            for expected in ("context", "understand", "plan"):
                self.assertEqual(engine.active_id(cl), expected)
                m = cm.build_manifest(cl, roots)
                self.assertEqual(m["step"], expected)
                self.assertEqual(m["step"], engine.active_id(cl))
                cl["tasks"][expected]["status"] = "complete"
            # Everything terminal: no active step, and the producer says so loudly
            # rather than inventing one.
            self.assertIsNone(engine.active_id(cl))
            with self.assertRaises(ValueError):
                cm.build_manifest(cl, roots)

    def test_real_spine_templates_produce_a_manifest_without_crashing(self):
        # The pre-existing-spine guarantee, checked against every real shipped
        # template rather than an authored fixture. `context_refs` is optional, so
        # a template without it must project nothing and must not raise.
        self.assertGreaterEqual(len(REAL_SPINE_TEMPLATES), 5)
        with tempfile.TemporaryDirectory() as tmp:
            roots = {"skill": Path(tmp), "repo": ROOT, "durable": Path(tmp)}
            for path in REAL_SPINE_TEMPLATES:
                with self.subTest(template=path.relative_to(ROOT).as_posix()):
                    cl = json.loads(path.read_text(encoding="utf-8"))
                    m = cm.build_manifest(cl, roots)
                    self.assertEqual(m["step"], cl["items"][0])
                    task = cl["tasks"][m["step"]]
                    if cm.DECLARATION_KEY not in task:
                        self.assertEqual(m["files"], [], "no declaration -> empty manifest")


class CommanderSpineDeclaration(unittest.TestCase):
    """The first real declaration in the corpus. (Pinning the declaration against
    the step's imperative prose is a separate lint and is deliberately not here.)"""

    TEMPLATE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"

    #: The declaration, pinned as a literal. Everything else in this class compares
    #: the declaration against itself or against a manifest derived from it — a
    #: self-referential oracle that cannot see an entry being **dropped**, or its
    #: `root` token being **retargeted** to a tree the file is not in (which
    #: resolves to `rev: null` forever, indistinguishable from a legitimately-absent
    #: overlay). The prose lint is one-directional by design and cannot see it
    #: either. This literal is the only place either defect is visible: a deliberate
    #: change here is a two-line diff, an accidental one is a failure.
    #:
    #: The `durable`-rooted `.agent-work/LESSONS.md` row was dropped deliberately by
    #: #308, which cut the lessons READ path: a live agent no longer loads the bank,
    #: so nothing declares it. That leaves the corpus with **no** `durable`
    #: declaration at all — a re-added one shows up here as a failure, which is the
    #: point of pinning the list rather than deriving it.
    EXPECTED = [
        ("skill", "references/global-orchestrator.md", True),
        ("skill", "references/global-everyone.md", True),
        ("repo", "docs/agents/ORCHESTRATOR_CONTEXT.md", False),
        ("repo", "docs/agents/GLOSSARY.md", False),
        ("repo", "docs/agents/engine-config.json", False),
    ]

    def setUp(self):
        self.spine = json.loads(self.TEMPLATE.read_text(encoding="utf-8"))
        self.declaration = self.spine["tasks"]["context"][cm.DECLARATION_KEY]

    def test_the_declaration_is_exactly_the_pinned_root_path_required_list(self):
        self.assertEqual(
            [(e["root"], e["path"], e["required"]) for e in self.declaration],
            self.EXPECTED,
        )

    def test_declaration_is_ordered_wellformed_and_non_empty(self):
        self.assertGreater(len(self.declaration), 0)
        self.assertIsInstance(self.declaration, list)
        for entry in self.declaration:
            with self.subTest(path=entry.get("path")):
                self.assertEqual(sorted(entry), ["path", "required", "root"])
                self.assertIn(entry["root"], cm.ROOT_TOKENS)
                self.assertIsInstance(entry["required"], bool)
                self.assertNotIn("\\", entry["path"])

    def test_declaration_projects_one_row_per_entry_in_declared_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            roots = {"skill": Path(tmp), "repo": Path(tmp), "durable": Path(tmp)}
            # Reached the way a real run reaches it — `init` terminal, then the
            # engine's own selector arrives at `context`. There is no `step=`
            # override to pin it with, deliberately.
            self.spine["tasks"]["init"]["status"] = "complete"
            self.assertEqual(cm.active_id(self.spine), "context")
            m = cm.build_manifest(self.spine, roots)
            self.assertEqual(m["step"], "context")
            self.assertEqual(
                [(r["root"], r["path"]) for r in m["files"]],
                [(e["root"], e["path"]) for e in self.declaration],
            )

    def test_only_the_context_step_carries_a_declaration(self):
        carriers = [i for i, t in self.spine["tasks"].items() if cm.DECLARATION_KEY in t]
        self.assertEqual(carriers, ["context"])

    def test_the_context_imperative_prose_is_not_replaced_by_the_declaration(self):
        # The prose carries rules a path list cannot express. The declaration
        # sits alongside it.
        #
        # Two of this test's original three sentinels -- "sanctioned degradation"
        # and "do NOT create the overlay file" -- were phrases of the
        # config_ref-is-absent-by-design block that issue #304 deleted as
        # falsified (docs/agents/ EXISTS in this repo, and Charter ships a task
        # that WRITES docs/agents/engine-config.json). The test's intent is
        # unchanged and it still pins three phrases; the two replacements quote
        # prose that survives, and they are the other degraded-mode rules --
        # paths-are-not-guaranteed, and declare-before-you-read -- which are
        # precisely the kind a path list still cannot express.
        prose = self.spine["tasks"]["context"]["imperative"]
        self.assertIn("record the substitution", prose)
        self.assertIn("do not treat those paths as guaranteed to exist", prose)
        self.assertIn("degraded is a declared reading, never a licence to start from code", prose)


class Written(unittest.TestCase):
    def test_produce_writes_under_agent_work_workid_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / ".agent-work"
            roots = {"skill": Path(tmp), "repo": Path(tmp), "durable": Path(tmp)}
            cl = checklist([{"root": "repo", "path": "absent.md", "required": False}],
                           work_id="300")
            path, manifest = cm.produce(cl, roots, work)
            self.assertEqual(path, work / "300" / "context" / "context.json")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), manifest)
            self.assertNotIn(b"\r\n", path.read_bytes())


FIXTURES = json.loads(
    (ROOT / "tests" / "fixtures" / "context_declarations.json").read_text(encoding="utf-8")
)


class AdversarialDeclarations(unittest.TestCase):
    """Fixtures authored to make the producer return a *wrong* answer."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        for rel, text in FIXTURES["tree"].items():
            target = base / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(text.encode("utf-8"))
        # A decoy sibling the producer must never notice: if anything in the chain
        # enumerated a directory, this would show up in the manifest.
        (base / "skill" / "references" / "DECOY-NEVER-DECLARED.md").write_bytes(b"decoy\n")
        self.roots = {"skill": base / "skill", "repo": base / "repo",
                      "durable": base / "repo"}

    def build(self, entries, **kw):
        return cm.build_manifest(checklist(entries), self.roots, **kw)

    def test_every_rejected_fixture_raises_rather_than_degrading(self):
        for name, entries in FIXTURES["rejected"].items():
            with self.subTest(fixture=name):
                with self.assertRaises(cm.DeclarationError):
                    self.build(entries)

    def test_declaration_order_permutation_registers_as_a_difference(self):
        forward = self.build(FIXTURES["accepted"]["ordered_two"]["entries"])
        permuted = self.build(FIXTURES["accepted"]["ordered_two_permuted"]["entries"])
        self.assertEqual({r["rev"] for r in forward["files"]},
                         {r["rev"] for r in permuted["files"]})
        self.assertNotEqual(cm.encode(cm.content(forward)),
                            cm.encode(cm.content(permuted)))

    def test_absent_fixture_is_retained_with_a_null_rev(self):
        m = self.build(FIXTURES["accepted"]["absent_is_retained"]["entries"])
        self.assertEqual([r["rev"] for r in m["files"]], [None])

    def test_duplicate_declared_paths_are_two_rows(self):
        m = self.build(FIXTURES["accepted"]["duplicate_paths"]["entries"])
        self.assertEqual(len(m["files"]), 2)
        self.assertEqual(m["files"][0], m["files"][1])

    def test_crlf_and_lf_twins_materialised_on_disk_agree(self):
        # Materialised at test time on purpose — see the `_readme` in
        # tests/fixtures/context_declarations.json: a committed CRLF twin cannot
        # survive this repo's `* text=auto` normalisation, and forcing it would need
        # the `-text` exemption that breaks rev()'s equality with git in the first
        # place. So the twin is written byte-for-byte here.
        refs = Path(self.tmp.name) / "skill" / "references"
        (refs / "twin-lf.md").write_bytes(b"a\nb\nc\n")
        (refs / "twin-crlf.md").write_bytes(b"a\r\nb\r\nc\r\n")
        self.assertNotEqual((refs / "twin-lf.md").read_bytes(),
                            (refs / "twin-crlf.md").read_bytes())
        lf = self.build([{"root": "skill", "path": "references/twin-lf.md", "required": True}])
        crlf = self.build([{"root": "skill", "path": "references/twin-crlf.md", "required": True}])
        self.assertEqual(lf["files"][0]["rev"], crlf["files"][0]["rev"])

    def test_changed_bytes_never_silently_revalidate_a_recorded_rev(self):
        entries = FIXTURES["accepted"]["ordered_two"]["entries"]
        recorded = cm.content(self.build(entries))
        target = Path(self.tmp.name) / "skill" / "references" / "doctrine.md"
        target.write_bytes(target.read_bytes() + b"appended\n")
        self.assertNotEqual(recorded, cm.content(self.build(entries)))

    def test_untracked_vs_absent_does_not_change_the_content_shape(self):
        entry = FIXTURES["accepted"]["absent_is_retained"]["entries"][0]
        absent = self.build([entry])
        target = Path(self.tmp.name) / "repo" / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"present but untracked\n")
        present = self.build([entry])
        # The only permitted difference is the one honest `rev`; step, ordering and
        # row identity must be byte-identical, so two environments never disagree
        # structurally over a file one of them happens to have.
        self.assertEqual(
            [(r["root"], r["path"]) for r in absent["files"]],
            [(r["root"], r["path"]) for r in present["files"]],
        )
        self.assertEqual(absent["step"], present["step"])
        self.assertIsNone(absent["files"][0]["rev"])
        self.assertIsNotNone(present["files"][0]["rev"])


class ProducerGuards(unittest.TestCase):
    """Standing invariants of the producer's source and its writes."""

    SOURCE = ROOT / "scripts" / "context_manifest.py"

    @property
    def own_files(self):
        """The producer plus every test module written against it — discovered, so a
        new sibling test file inherits these guards instead of escaping them."""
        return [self.SOURCE] + sorted((ROOT / "tests").glob("test_context_*.py"))

    @staticmethod
    def _names_used(path):
        """Every identifier and attribute actually *used as code* in a module.

        Parsed rather than grepped: a substring scan would trip over the module's
        own prose ("no globs", "not sorted()") and report a comment as a violation.
        """
        tree = ast.parse(path.read_text(encoding="utf-8"))
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                used.add(node.attr)
            elif isinstance(node, ast.Import):
                used |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                used.add((node.module or "").split(".")[0])
        return used

    def test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer(self):
        # Source half: a glob would import filesystem ordering — a named
        # irreproducibility source — into the record. Sorting is banned for the same
        # reason: declaration order is content and must never be re-derived.
        used = self._names_used(self.SOURCE)
        banned = {"glob", "iglob", "rglob", "listdir", "scandir", "walk", "iterdir",
                  "fnmatch", "sorted", "sort"}
        self.assertEqual(sorted(banned & used), [])

        # Behavioural half: with every enumeration primitive booby-trapped, the
        # producer must still work, and must read exactly the declared paths.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "references").mkdir()
            for name in ("declared.md", "decoy-a.md", "decoy-b.md", "decoy-c.md"):
                (base / "references" / name).write_bytes(name.encode())
            seen = []

            def counting_reader(path):
                seen.append(Path(path).name)
                return cm.read_bytes(path)

            def explode(*a, **k):  # pragma: no cover - must never be called
                raise AssertionError("the producer enumerated the filesystem")

            import os as _os
            patched = {"listdir": _os.listdir, "scandir": _os.scandir, "walk": _os.walk}
            for name in patched:
                setattr(_os, name, explode)
            self.addCleanup(lambda: [setattr(_os, n, f) for n, f in patched.items()])
            try:
                m = cm.build_manifest(
                    checklist([{"root": "skill", "path": "references/declared.md",
                                "required": True}]),
                    {"skill": base, "repo": base, "durable": base},
                    reader=counting_reader,
                )
            finally:
                for name, original in patched.items():
                    setattr(_os, name, original)
            self.assertEqual(seen, ["declared.md"])
            self.assertEqual([r["path"] for r in m["files"]], ["references/declared.md"])

    def test_every_manifest_write_is_newline_pinned(self):
        # Source half: no unpinned text write may exist in the module. On Windows an
        # unpinned `open(..., "w")` translates every \n to \r\n, and the record would
        # not survive its own identity function.
        tree = ast.parse(self.SOURCE.read_text(encoding="utf-8"))
        text_writes = 0
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name in ("write_text", "writelines"):
                self.fail(f"{name}() cannot pin newline; use open(..., newline='\\n')")
            if name != "open":
                continue
            mode = node.args[1].value if len(node.args) > 1 else None
            if mode is None or "b" in mode:
                continue
            text_writes += 1
            keywords = {kw.arg: kw.value for kw in node.keywords}
            self.assertIn("newline", keywords, "text open() must pin newline")
            self.assertEqual(keywords["newline"].value, "\n")
        self.assertGreaterEqual(text_writes, 1, "expected a text write in the producer")

        # Behavioural half: the bytes on disk really are LF, whatever the platform.
        with tempfile.TemporaryDirectory() as tmp:
            path = cm.write_manifest(
                {"contract": 1, "step": "context",
                 "files": [{"root": "repo", "path": "a.md", "rev": None}]},
                Path(tmp) / "300" / "context" / "context.json",
            )
            self.assertNotIn(b"\r\n", path.read_bytes())

    #: 3.13+-only APIs that a 3.14 dev host accepts silently and CI's pinned 3.12
    #: rejects. `Path.read_text/write_text(newline=)` is the one this epic has
    #: already shipped red once.
    PY313_ONLY_KWARGS = {"read_text": "newline", "write_text": "newline"}
    PY313_ONLY_ATTRS = {"batched", "TypeIs", "ReadOnly", "CommandLineParser"}

    def test_producer_and_its_tests_are_py312_compatible(self):
        # CI pins Python 3.12 (.github/workflows/ci.yml) while dev hosts run newer,
        # so a 3.13+-only API goes red only in CI. This epic has already shipped
        # exactly that once.
        files = self.own_files
        self.assertGreaterEqual(len(files), 2)
        for path in files:
            with self.subTest(file=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    name = getattr(node.func, "attr", None)
                    banned_kwarg = self.PY313_ONLY_KWARGS.get(name)
                    if banned_kwarg and any(kw.arg == banned_kwarg for kw in node.keywords):
                        self.fail(f"{path.name}: {name}({banned_kwarg}=) is 3.13+ only")
                    if name in self.PY313_ONLY_ATTRS:
                        self.fail(f"{path.name}: {name}() is 3.13+ only")

    def test_producer_shells_out_to_nothing(self):
        # AST-level, narrower than it once read: this file's OWN SOURCE contains
        # none of these identifiers. It does NOT mean build_manifest() never
        # shells out -- the default `repo_state` edge (`default_repo_state`)
        # delegates to `checklist_engine.repo_revision`, which does shell out to
        # git, by design (#300 g5): that indirection is what keeps this guard
        # literally true after `repo_rev` exists, not a claim that assembly is
        # subprocess-free. The invariant that actually matters -- real
        # injectability, not merely an absent identifier -- is pinned directly by
        # `test_build_manifest_with_both_edges_injected_shells_out_to_nothing`
        # below.
        used = self._names_used(self.SOURCE)
        banned = {"subprocess", "urllib", "requests", "socket", "http", "system", "popen"}
        self.assertEqual(sorted(banned & used), [])

    def test_build_manifest_with_both_edges_injected_shells_out_to_nothing(self):
        # The guarantee readers actually care about: with BOTH impure edges
        # faked, build_manifest performs zero subprocess calls, so no test needs
        # a real git repository. Patched at the `subprocess` module level (not
        # merely "the fakes were never called") so a future unconditional git
        # call added anywhere in build_manifest's own path -- not mediated by
        # `repo_state` -- would be caught here too.
        import subprocess as _subprocess

        def explode(*a, **k):  # pragma: no cover - must never be called
            raise AssertionError("build_manifest shelled out despite both edges being injected")

        original_run, original_popen = _subprocess.run, _subprocess.Popen
        _subprocess.run = explode
        _subprocess.Popen = explode
        self.addCleanup(lambda: (
            setattr(_subprocess, "run", original_run),
            setattr(_subprocess, "Popen", original_popen),
        ))

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "references").mkdir()
            (base / "references" / "declared.md").write_bytes(b"doctrine\n")
            m = cm.build_manifest(
                checklist([{"root": "skill", "path": "references/declared.md",
                            "required": True}]),
                {"skill": base, "repo": base, "durable": base},
                reader=cm.read_bytes,
                repo_state=lambda roots: {"commit": "deadbeef", "dirty": False},
            )
        self.assertEqual(m["repo_rev"], {"commit": "deadbeef"})


class Serialisation(unittest.TestCase):
    def test_encode_is_the_one_canonical_encoder(self):
        obj = {"contract": 1, "step": "context", "files": [], "note": "em—dash"}
        text = cm.encode(obj)
        self.assertTrue(text.endswith("\n"))
        self.assertIn("em—dash", text)  # ensure_ascii=False
        self.assertIn('\n  "step"', text)  # indent=2
        self.assertEqual(json.loads(text), obj)

    def test_written_manifest_has_lf_endings_on_every_platform(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = cm.write_manifest({"contract": 1, "step": "context", "files": []},
                                     Path(tmp) / "w" / "context" / "context.json")
            raw = path.read_bytes()
            self.assertNotIn(b"\r\n", raw)
            # The written file must survive its own identity function: rev of the
            # bytes on disk equals rev of the encoded string.
            self.assertEqual(
                cm.rev(raw), cm.rev(cm.encode(json.loads(raw)).encode("utf-8"))
            )

    def test_manifest_path_is_agent_work_workid_context_step_json(self):
        p = cm.manifest_path(".agent-work", "300", "context")
        self.assertEqual(Path(p).as_posix(), ".agent-work/300/context/context.json")


class RepoRevContent(unittest.TestCase):
    """`repo_rev` -- Tommy's doctrine-version stamp (#300 g5): the repo revision,
    admitted into `CONTENT_KEYS` (a fact about canon, not about the run
    environment). The per-file blob OID (`rev`, tested above in `RevIsGitBlobOid`)
    is untouched -- this is a second, coarser fact, not a replacement.

    Split in rework 1 (BLOCKER-1): `repo_rev` in content carries `commit` only,
    which is canon-determined (identical for any checkout of that commit). A
    review proved the original placement (both `commit` and `dirty` inside
    content) wrong: two checkouts at the same commit, delivering byte-identical
    declared canon, disagreed on `repo_rev` solely because `git status
    --porcelain` is repo-wide and picked up dirt on a file no declaration named.

    `dirty` moved to the excluded `run` subtree then, and was removed outright in
    #327 (#305 g4) once a real producing caller made its behaviour observable: it
    is repo-wide, so what it reports is dominated by the run's own bookkeeping,
    and it is computed before the manifest is written, so it reads its
    predecessor's tree rather than its own. `test_dirty_appears_nowhere_in_the_manifest`
    below is the guard on that removal; the `repo_state` fakes throughout this
    class still SUPPLY the field, unchanged, because a consumer that ignores what
    it is handed is exactly what is being asserted."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.skill = Path(self.tmp.name) / "skill"
        self.repo = Path(self.tmp.name) / "repo"
        (self.skill / "references").mkdir(parents=True)
        (self.repo / "docs").mkdir(parents=True)
        (self.skill / "references" / "doctrine.md").write_bytes(b"doctrine\n")
        self.roots = {"skill": self.skill, "repo": self.repo, "durable": self.repo}

    def build(self, repo_state=None, **kw):
        decl = [{"root": "skill", "path": "references/doctrine.md", "required": True}]
        kwargs = dict(kw)
        if repo_state is not None:
            kwargs["repo_state"] = repo_state
        return cm.build_manifest(checklist(decl), self.roots, **kwargs)

    def test_repo_rev_is_admitted_into_content_keys(self):
        self.assertIn("repo_rev", cm.CONTENT_KEYS)

    def test_repo_rev_is_a_content_field_not_a_run_field(self):
        # The whole point of #300 g5: commit is a fact about canon, so it must
        # not hide in the excluded /run subtree.
        m = self.build(repo_state=lambda roots: {"commit": "deadbeef", "dirty": False})
        self.assertNotIn("repo_rev", m["run"])
        self.assertIn("repo_rev", cm.content(m))
        self.assertEqual(cm.content(m)["repo_rev"], {"commit": "deadbeef"})

    def test_repo_rev_shape_is_exactly_commit(self):
        m = self.build(repo_state=lambda roots: {"commit": "abc123", "dirty": True})
        self.assertEqual(sorted(m["repo_rev"]), ["commit"])

    def test_dirty_appears_nowhere_in_the_manifest(self):
        # #327 (#305 g4), the removal's regression guard. The `repo_state` edge
        # still SUPPLIES `dirty` -- that contract is unchanged, and it is what
        # makes this test mean something: the consumer is handed the field and
        # must drop it on the floor. Asserted at every depth, not just in `run`,
        # so a future re-introduction anywhere in the envelope fails here.
        m = self.build(repo_state=lambda roots: {"commit": "deadbeef", "dirty": True})
        self.assertNotIn("dirty", m["run"])
        self.assertNotIn("dirty", m["repo_rev"])
        self.assertNotIn("dirty", cm.content(m))
        self.assertEqual(_dirty_key_paths(m), [])
        # And not smuggled in under another spelling of the same bytes: the
        # encoded manifest must not contain the token at all.
        self.assertNotIn("dirty", cm.encode(m))

    def test_content_is_unaffected_by_dirty_when_commit_is_equal(self):
        # The regression #300 g5 rework 1 closed, in-process and fast: two
        # repo_state fakes that agree on `commit` but disagree on `dirty` must
        # still produce byte-identical content. `tests/test_context_determinism.py`'s
        # `RealCheckoutSkew` covers the same property end-to-end, over real git
        # worktrees; this is the unit-level complement.
        m_clean = self.build(repo_state=lambda roots: {"commit": "deadbeef", "dirty": False})
        m_dirty = self.build(repo_state=lambda roots: {"commit": "deadbeef", "dirty": True})
        self.assertEqual(cm.content(m_clean), cm.content(m_dirty))
        # Strengthened for #327: the property used to stop at `content()` because
        # the two manifests genuinely differed inside the `run` subtree. With the
        # field dropped on the floor, the WHOLE envelope is now insensitive to
        # `dirty`, not just the compared part -- only `generated_at` may move.
        self.assertEqual(
            {k: v for k, v in m_clean["run"].items() if k != "generated_at"},
            {k: v for k, v in m_dirty["run"].items() if k != "generated_at"},
        )
        self.assertEqual(
            {k: v for k, v in m_clean.items() if k != "run"},
            {k: v for k, v in m_dirty.items() if k != "run"},
        )

    def test_repo_rev_does_not_replace_the_per_file_blob_oid(self):
        # The per-file row's `rev` -- tested exhaustively in RevIsGitBlobOid and
        # ManifestEnvelope above -- must be completely unaffected by repo_rev's
        # presence: still exactly {root, path, rev}, still the blob OID.
        m = self.build(repo_state=lambda roots: {"commit": "deadbeef", "dirty": True})
        self.assertEqual(list(m["files"][0]), ["root", "path", "rev"])
        self.assertEqual(m["files"][0]["rev"], cm.rev(b"doctrine\n"))

    def test_repo_state_is_injectable_as_the_second_impure_edge(self):
        seen = []

        def fake_repo_state(roots):
            seen.append(roots)
            return {"commit": "injected-sha", "dirty": True}

        m = self.build(repo_state=fake_repo_state)
        self.assertEqual(len(seen), 1)
        self.assertIs(seen[0], self.roots)
        self.assertEqual(m["repo_rev"], {"commit": "injected-sha"})

    def test_default_repo_state_on_a_non_git_directory_yields_no_commit(self):
        # self.repo is a plain tempdir, never `git init`-ed.
        m = self.build()
        self.assertEqual(m["repo_rev"], {"commit": None})

    def test_default_repo_state_with_no_repo_root_mapped_yields_no_commit(self):
        roots = {"skill": self.skill, "durable": self.repo}
        m = cm.build_manifest(
            checklist([{"root": "skill", "path": "references/doctrine.md", "required": True}]),
            roots,
        )
        self.assertEqual(m["repo_rev"], {"commit": None})

    def test_default_repo_state_against_the_real_repo_matches_the_commit_oracle(self):
        # Singular: the porcelain-status oracle went with `dirty` (#327). The
        # commit half is the only one the manifest still carries.
        import subprocess
        commit_oracle = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT),
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(commit_oracle.returncode, 0, commit_oracle.stderr)

        roots = {"skill": self.skill, "repo": ROOT, "durable": self.repo}
        m = cm.build_manifest(
            checklist([{"root": "skill", "path": "references/doctrine.md", "required": True}]),
            roots,
        )
        self.assertEqual(m["repo_rev"]["commit"], commit_oracle.stdout.strip())

    def test_repo_rev_survives_json_round_trip_untransformed(self):
        m = self.build(repo_state=lambda roots: {"commit": "deadbeef", "dirty": False})
        self.assertEqual(json.loads(json.dumps(m))["repo_rev"], m["repo_rev"])

    def test_doctrine_version_is_the_repo_rev_field(self):
        # Named for gate g5's own -k selector ('repo_rev or doctrine_version'):
        # "doctrine version" IS the repo_rev content field, not a separate one.
        m = self.build(repo_state=lambda roots: {"commit": "cafefeed", "dirty": False})
        self.assertEqual(cm.content(m)["repo_rev"]["commit"], "cafefeed")


class EpisodeContextFieldShape(unittest.TestCase):
    """The manifest must be assignable to an episode `context` field with **no
    transformation** — a plain JSON value the caller can store as-is. This is a
    test-after/inspection check: it exercises the real producer end to end and
    makes the property explicit, rather than trusting it as an implied side
    effect of the other tests."""

    def test_produced_manifest_is_assignable_to_episode_context_field_untransformed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            work = base / ".agent-work"
            (base / "doc.md").write_bytes(b"doctrine\n")
            roots = {"skill": base, "repo": base, "durable": base}
            cl = checklist(
                [{"root": "repo", "path": "doc.md", "required": True},
                 {"root": "repo", "path": "absent.md", "required": False}],
                work_id="300",
            )
            path, manifest = cm.produce(cl, roots, work)

            # No transformation required: assigning `manifest` to a JSON field is
            # exactly json.loads(json.dumps(manifest)), and it must round-trip
            # byte-for-byte -- not merely "close enough".
            round_tripped = json.loads(json.dumps(manifest))
            self.assertEqual(round_tripped, manifest)
            # ...and the file actually on disk agrees with the in-memory value too.
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), manifest)

            # Every value anywhere in the structure is a JSON-native type: no Path,
            # no datetime, no set, nothing that would need a custom encoder to
            # survive assignment into an episode record.
            def assert_json_native(value):
                if isinstance(value, dict):
                    for key, sub in value.items():
                        self.assertIsInstance(key, str)
                        assert_json_native(sub)
                elif isinstance(value, list):
                    for item in value:
                        assert_json_native(item)
                else:
                    self.assertIsInstance(value, (str, int, float, bool, type(None)))

            assert_json_native(manifest)

            # No absolute path in the manifest's informational content -- the part
            # an episode record would actually key or compare on. (`run.roots` and
            # `run.host.cwd` legitimately carry this environment's absolute paths;
            # that is the declared, single exclusion set `cm.content()` strips —
            # see test_no_absolute_root_path_appears_in_content above.)
            rendered_content = cm.encode(cm.content(manifest))
            self.assertNotIn(base.as_posix(), rendered_content)
            self.assertNotIn(str(base), rendered_content)


if __name__ == "__main__":
    unittest.main()
