"""#613 (atomicity half): `checklist_engine.save()` must install the new document
by ATOMIC RENAME, never by writing over the live target in place.

The load-bearing assertions here are DETERMINISTIC and mechanical, deliberately:

  * `save()` opens no write handle on the target path -- only on a temp sibling;
  * the target's inode is replaced exactly once per save (one `os.replace`);
  * no `*.tmp` sibling survives either a success or a forced failure.

A thread race against the old `write_bytes` implementation would have been
timing-dependent, so it could come out GREEN against the broken code by luck and
thereby fake its own red-proof. A flaky red is not a red. The concurrency test at
the bottom is SUPPORTING evidence -- it exercises the close criterion ("a reader
concurrent with a writer never observes a partial document") but it is not what
discriminates old from new.
"""

import importlib.util
import io
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "checklist_engine.py"


def load_engine():
    spec = importlib.util.spec_from_file_location("checklist_engine", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E = load_engine()

SAMPLE = {"work_id": "w", "type": "gated", "items": [{"id": "i1", "title": "t"}]}


def _real(path) -> str:
    """A comparable absolute path, so the assertion cannot pass or fail on the
    difference between a relative and an absolute spelling of one file."""
    return os.path.realpath(os.fspath(path))


class _WriteOpenRecorder:
    """Record every path opened for WRITING for the duration of one `save()`.

    Both doors are wrapped because the two implementations use different ones:
    `Path.write_bytes` reaches the target through `io.open` (which is what
    `pathlib.Path.open` calls), while `tempfile.mkstemp` reaches its temp through
    `os.open`. Wrapping only one of them would let the other slip past unseen.
    """

    _WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND

    def __init__(self):
        self.write_paths: list[str] = []
        self.replaced_to: list[str] = []

    def __enter__(self):
        real_io_open, real_os_open, real_replace = io.open, os.open, os.replace

        def io_open(file, mode="r", *args, **kwargs):
            if isinstance(file, (str, bytes, os.PathLike)) and any(
                c in mode for c in "wax+"
            ):
                self.write_paths.append(_real(file))
            return real_io_open(file, mode, *args, **kwargs)

        def os_open(path, flags, *args, **kwargs):
            if flags & self._WRITE_FLAGS:
                self.write_paths.append(_real(path))
            return real_os_open(path, flags, *args, **kwargs)

        def replace(src, dst, **kwargs):
            self.replaced_to.append(_real(dst))
            return real_replace(src, dst, **kwargs)

        self._patches = [
            mock.patch("io.open", io_open),
            mock.patch("os.open", os_open),
            mock.patch("os.replace", replace),
        ]
        for p in self._patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in reversed(self._patches):
            p.stop()
        return False


class AtomicSaveTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.path = self.dir / "spine.json"
        self.addCleanup(self._tmp.cleanup)

    def _tmp_siblings(self) -> list[str]:
        return sorted(p.name for p in self.dir.iterdir() if p.name != self.path.name)

    # -- (1) deterministic: the target is never opened for writing ---------- #

    def test_save_never_opens_target_for_writing(self):
        """The discriminating assertion. The old implementation ends in
        `Path(path).write_bytes(...)`, which opens the TARGET with O_TRUNC: the
        window in which a concurrent reader sees a truncated spine. An atomic
        save writes a temp sibling and renames, so the target is never a write
        target at all."""
        self.path.write_text(json.dumps({"work_id": "old"}) + "\n", encoding="utf-8")
        with _WriteOpenRecorder() as rec:
            E.save(self.path, SAMPLE)

        self.assertTrue(rec.write_paths, "no write-open observed at all -- the "
                                        "recorder is not wired to save()")
        self.assertNotIn(
            _real(self.path), rec.write_paths,
            "save() opened the live spine for writing; a concurrent reader can "
            f"observe a truncated document. write-opened: {rec.write_paths}",
        )
        # The payload still landed.
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), SAMPLE)

    def test_save_writes_a_temp_sibling_in_the_same_directory(self):
        """`os.replace` is only atomic within one filesystem, so the temp has to
        be a sibling -- not in the system temp dir."""
        self.path.write_text("{}\n", encoding="utf-8")
        with _WriteOpenRecorder() as rec:
            E.save(self.path, SAMPLE)
        written = [p for p in rec.write_paths if p != _real(self.path)]
        self.assertTrue(written, "save() wrote no temp file")
        for p in written:
            self.assertEqual(
                os.path.dirname(p), _real(self.dir),
                f"temp {p!r} is not a sibling of the target",
            )

    # -- (2) deterministic: the inode is swapped exactly once --------------- #

    def test_target_inode_is_replaced_exactly_once(self):
        """A rename installs a NEW inode at the path; an in-place write keeps the
        old one. Deterministic in both directions, and `os.replace` is counted so
        'exactly once' is measured rather than inferred."""
        self.path.write_text("{}\n", encoding="utf-8")
        before = os.stat(self.path).st_ino
        with _WriteOpenRecorder() as rec:
            E.save(self.path, SAMPLE)
        after = os.stat(self.path).st_ino

        self.assertNotEqual(before, after,
                            "the target's inode did not change: the document was "
                            "written in place, not atomically renamed into place")
        self.assertEqual(
            [p for p in rec.replaced_to if p == _real(self.path)], [_real(self.path)],
            f"expected exactly one os.replace onto the target, got "
            f"{rec.replaced_to!r}",
        )

    # -- (3) deterministic: no temp survives, success or failure ------------ #

    def test_no_temp_sibling_after_success(self):
        E.save(self.path, SAMPLE)
        self.assertEqual(self._tmp_siblings(), [])
        E.save(self.path, SAMPLE)  # again, over an existing file
        self.assertEqual(self._tmp_siblings(), [])

    def test_no_temp_sibling_after_a_failed_replace(self):
        """A forced failure at the install step must leave neither a temp file nor
        a damaged target: the old document is still there, intact and parseable."""
        original = json.dumps({"work_id": "old"}, indent=2) + "\n"
        self.path.write_text(original, encoding="utf-8")

        boom = OSError("forced")
        with mock.patch("os.replace", side_effect=boom):
            with self.assertRaises(OSError):
                E.save(self.path, SAMPLE)

        self.assertEqual(self._tmp_siblings(), [],
                         "a temp file survived a failed save")
        self.assertEqual(self.path.read_text(encoding="utf-8"), original,
                         "a failed save damaged the previous document")

    # -- (4) the target's mode survives the rename -------------------------- #

    def test_existing_file_mode_is_preserved(self):
        """`mkstemp` creates 0600. A bare rename would silently narrow the
        spine's permissions, which is a behaviour change nobody asked for."""
        self.path.write_text("{}\n", encoding="utf-8")
        os.chmod(self.path, 0o640)
        E.save(self.path, SAMPLE)
        self.assertEqual(os.stat(self.path).st_mode & 0o777, 0o640)

    # -- (5) line endings: the behaviour that is easiest to break silently -- #

    def test_crlf_file_stays_crlf(self):
        """`_dominant_newline` reads the EXISTING file, so it must be consulted
        BEFORE the original is replaced. Getting the ordering wrong rewrites
        every ending in the file -- the exact defect save()'s docstring exists to
        prevent."""
        self.path.write_bytes(json.dumps({"work_id": "old"}, indent=2)
                              .replace("\n", "\r\n").encode("utf-8") + b"\r\n")
        E.save(self.path, SAMPLE)
        raw = self.path.read_bytes()
        self.assertIn(b"\r\n", raw)
        self.assertEqual(raw.count(b"\n") - raw.count(b"\r\n"), 0,
                         "a bare LF appeared in a CRLF spine")
        self.assertEqual(json.loads(raw.decode("utf-8")), SAMPLE)

    def test_lf_file_stays_lf(self):
        self.path.write_bytes(b'{\n  "work_id": "old"\n}\n')
        E.save(self.path, SAMPLE)
        raw = self.path.read_bytes()
        self.assertNotIn(b"\r", raw)

    def test_missing_file_gets_lf(self):
        self.assertFalse(self.path.exists())
        E.save(self.path, SAMPLE)
        self.assertNotIn(b"\r", self.path.read_bytes())

    def test_mixed_endings_normalise_to_lf(self):
        self.path.write_bytes(b'{\r\n  "work_id": "old"\n}\n')
        E.save(self.path, SAMPLE)
        self.assertNotIn(b"\r", self.path.read_bytes())

    # -- (6) SUPPORTING (racy by nature): the concurrent reader ------------- #

    def test_concurrent_reader_never_observes_a_partial_document(self):
        """The close criterion, EXERCISED rather than asserted: readers hammer the
        spine while writers replace it, and every read must yield a COMPLETE
        document -- the old one or the new one, never a torn one.

        This test is TIMING-DEPENDENT and is therefore supporting evidence only.
        It is not what proves the fix; tests (1)-(3) are.
        """
        big = {"work_id": "w", "items": [{"id": f"i{n}", "note": "x" * 400}
                                         for n in range(200)]}
        small = {"work_id": "w", "items": []}
        E.save(self.path, small)

        stop = threading.Event()
        errors: list[str] = []
        reads = [0]

        def writer():
            payloads = (big, small)
            n = 0
            while not stop.is_set():
                try:
                    E.save(self.path, payloads[n % 2])
                except OSError as exc:  # pragma: no cover -- would be a finding
                    errors.append(f"writer OSError: {exc!r}")
                n += 1

        def reader():
            while not stop.is_set():
                try:
                    doc = json.loads(self.path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    errors.append(f"TORN READ: {exc}")
                    return
                except OSError as exc:  # pragma: no cover
                    errors.append(f"reader OSError: {exc!r}")
                    return
                if doc.get("work_id") != "w":
                    errors.append(f"partial document: {doc!r}")
                    return
                reads[0] += 1

        threads = [threading.Thread(target=writer) for _ in range(2)]
        threads += [threading.Thread(target=reader) for _ in range(3)]
        for t in threads:
            t.start()
        stop.wait(1.5)
        stop.set()
        for t in threads:
            t.join(timeout=5)

        self.assertEqual(errors, [])
        self.assertGreater(reads[0], 0, "the reader threads never read anything")
        self.assertEqual(self._tmp_siblings(), [],
                         "temp files survived the concurrent run")
        # Whatever landed last is a whole, parseable document.
        json.loads(self.path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
