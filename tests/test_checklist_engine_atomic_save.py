"""#613 (atomicity half): `checklist_engine.save()` must install the new document
by ATOMIC RENAME, never by writing over the live target in place.

The load-bearing assertions here are DETERMINISTIC and mechanical, deliberately:

  * `save()` opens no write handle on the target path -- only on a temp sibling;
  * the target's inode is replaced exactly once per save (one `os.replace`);
  * no `*.tmp` sibling survives either a success or a forced failure.

A thread race against the old `write_bytes` implementation would have been
timing-dependent, so it could come out GREEN against the broken code by luck and
thereby fake its own red-proof. A flaky red is not a red.

**A real thread-race test lived here through issue #647 and was deleted.** It
ran readers concurrent with a writer and asserted every read was complete. Two
rulings on #647 found it did not discriminate anything the deterministic tests
below don't already discriminate: on POSIX it could not fail for tearing at all
(`rename(2)` never invalidates an open reader, and (1)-(3) below already prove
`save()` never touches the target's bytes in place and installs by exactly one
atomic rename); on Windows it failed for CONTENTION -- a busy retry budget
exhausted under synthetic thread-loop load -- not for tearing, which is a
different invariant than the one it claimed to test and one the (4b)/(4c)
sections below already pin deterministically and without a race:
`test_save_never_opens_target_for_writing`, `test_target_inode_is_replaced_exactly_once`,
`test_a_windows_sharing_violation_is_retried_and_then_succeeds`,
`test_a_persistent_sharing_violation_RAISES_rather_than_losing_the_write`, and
`test_a_non_busy_OSError_is_NOT_retried` -- plus their (4c) reader-side mirrors
added when the racy test was removed. A racy test that cannot prove anything
beyond what these already prove is the "check that cannot mean what it claims"
pattern issue #518 tracks generally; do not re-add it. If a NEW invariant needs
covering, add a deterministic test for that invariant specifically, the way
(4b)/(4c) do.
"""

import importlib.util
import io
import errno
import json
import os
import tempfile
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

    @unittest.skipUnless(hasattr(os, "fchmod"), "POSIX mode bits are not a Windows concept")
    def test_existing_file_mode_is_preserved(self):
        """`mkstemp` creates 0600. A bare rename would silently narrow the
        spine's permissions, which is a behaviour change nobody asked for.

        Skipped off POSIX rather than asserted loosely: Windows honours only the
        read-only bit, so `os.chmod(path, 0o640)` there does not produce a `0o640`
        stat and an assertion on the bits would fail for a reason that has nothing
        to do with `save()`. The platform-independent half — that saving does not
        CRASH where `fchmod` is absent — is
        `test_save_survives_where_fchmod_is_unavailable` below, which runs
        everywhere."""
        self.path.write_text("{}\n", encoding="utf-8")
        os.chmod(self.path, 0o640)
        E.save(self.path, SAMPLE)
        self.assertEqual(os.stat(self.path).st_mode & 0o777, 0o640)

    def test_save_survives_where_fchmod_is_unavailable(self):
        """`os.fchmod` is Unix-only and this repo's CI is `windows-latest`, so an
        unguarded call raised `AttributeError` for every save of an existing file —
        a dead engine on that platform, since every mutating verb ends in `save()`.

        Simulates the Windows shape on any host by making the call raise, which is
        what a Windows interpreter effectively presents. Runs everywhere on purpose: a
        `skipUnless` here would make the guard untested precisely where it matters.

        **`create=True` is load-bearing and was added after CI proved it.** Without
        it, `mock.patch.object` requires the attribute to already exist — so on
        Windows, where `os.fchmod` is genuinely absent, the PATCH ITSELF raised
        `AttributeError: <module 'os'> does not have the attribute 'fchmod'` and the
        test errored before exercising anything. The one test proving the fallback
        works could not run on the one platform that needs the fallback: a check that
        cannot fail exactly where it matters. Recorded as its own triage candidate
        (issue #567 lane A)."""
        self.path.write_text("{}\n", encoding="utf-8")
        with mock.patch.object(E.os, "fchmod", create=True,
                               side_effect=AttributeError("no fchmod")):
            E.save(self.path, SAMPLE)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), SAMPLE,
                         "save() must still write the document when fchmod is absent")
        self.assertEqual(self._tmp_siblings(), [],
                         "the fchmod fallback path leaked a temp file")

    # -- (4b) the Windows replace-busy retry ------------------------------- #

    def test_a_windows_sharing_violation_is_retried_and_then_succeeds(self):
        """POSIX `rename(2)` replaces a destination whoever holds it open; Windows
        `MoveFileEx` FAILS when a reader has it open without `FILE_SHARE_DELETE`,
        which CPython's `open()` does not pass. Measured in CI: two writers and three
        readers on one spine produced `PermissionError(13, 'Access denied')` on
        Windows while Linux passed clean.

        Simulates that on any host: the first two `os.replace` calls raise with
        `winerror` set to a Windows busy code, the third succeeds. The document must
        land and no temp may survive."""
        self.path.write_text("{}\n", encoding="utf-8")
        real_replace = os.replace
        calls = [0]

        def flaky(src, dst):
            calls[0] += 1
            if calls[0] <= 2:
                exc = PermissionError(13, "Access is denied")
                exc.winerror = 5  # ERROR_ACCESS_DENIED
                raise exc
            return real_replace(src, dst)

        with mock.patch.object(E.os, "replace", side_effect=flaky):
            E.save(self.path, SAMPLE)
        self.assertEqual(calls[0], 3, "the retry did not re-attempt the install")
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), SAMPLE)
        self.assertEqual(self._tmp_siblings(), [], "the retry path leaked a temp file")

    def test_a_persistent_sharing_violation_RAISES_rather_than_losing_the_write(self):
        """Fail-loud is the whole point. If every attempt loses the race, the error
        propagates so the caller learns the write did not land — it must never return
        as though it had."""
        self.path.write_text('{"work_id": "old"}\n', encoding="utf-8")

        def always_busy(src, dst):
            exc = PermissionError(13, "Access is denied")
            exc.winerror = 32  # ERROR_SHARING_VIOLATION
            raise exc

        with mock.patch.object(E.os, "replace", side_effect=always_busy):
            with self.assertRaises(PermissionError):
                E.save(self.path, SAMPLE)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")),
                         {"work_id": "old"},
                         "a failed install must leave the previous document intact")
        self.assertEqual(self._tmp_siblings(), [],
                         "a persistently failed install leaked a temp file")

    def test_a_non_busy_OSError_is_NOT_retried(self):
        """The retry is deliberately narrow: only the two Windows busy codes. A real
        permission problem or a vanished directory must fail on the FIRST attempt,
        because retrying those turns a clear failure into a slow one."""
        self.path.write_text("{}\n", encoding="utf-8")
        calls = [0]

        def other_error(src, dst):
            calls[0] += 1
            raise OSError(errno.ENOSPC, "No space left on device")

        with mock.patch.object(E.os, "replace", side_effect=other_error):
            with self.assertRaises(OSError):
                E.save(self.path, SAMPLE)
        self.assertEqual(calls[0], 1, "a non-busy OSError was retried; it must not be")

    # -- (4c) the Windows read-busy retry: the reader-side mirror of (4b) --- #
    #
    # Added by issue #647's second ruling to close a gap the deleted racy
    # concurrent-reader test's failure exposed: (4b) above has full
    # deterministic coverage of `_replace_with_retry` (the WRITER's busy
    # retry), by mocking `os.replace`; NOTHING anywhere mocked `read_text` to
    # prove `_read_text_with_retry` (the READER's busy retry) actually
    # retries, actually gives up correctly, and actually respects the narrow
    # `os.name == "nt"` scoping `_read_busy_on_windows` documents for its bare
    # `PermissionError` fallback. These five tests give the reader side the
    # same shape of proof the writer side already had -- no thread, no race.

    def test_a_windows_read_sharing_violation_is_retried_and_then_succeeds(self):
        """The reader-side mirror of
        `test_a_windows_sharing_violation_is_retried_and_then_succeeds`: a
        concurrent `save()`'s `os.replace` briefly holds the destination name
        exclusively, so an ordinary `read_text()` can raise the same Windows
        busy `PermissionError` while the install is mid-flight
        (`_read_text_with_retry`'s own docstring).

        Simulates that on any host: the first two `read_text` calls raise
        with `winerror` set to a Windows busy code, the third succeeds and
        returns the real document."""
        self.path.write_text(json.dumps(SAMPLE, indent=2) + "\n", encoding="utf-8")
        real_read_text = Path.read_text
        calls = [0]

        def flaky(**kwargs):
            calls[0] += 1
            if calls[0] <= 2:
                exc = PermissionError(13, "Access is denied")
                exc.winerror = 5  # ERROR_ACCESS_DENIED
                raise exc
            return real_read_text(self.path, **kwargs)

        with mock.patch.object(Path, "read_text", side_effect=flaky):
            doc = E.load(self.path)
        self.assertEqual(calls[0], 3, "the retry did not re-attempt the read")
        self.assertEqual(doc, SAMPLE)

    def test_a_persistent_read_sharing_violation_RAISES_rather_than_returning_a_partial_document(self):
        """Fail-loud is the reader's contract too: if every attempt loses the
        race, `load()` must propagate the error -- never return a partial or
        wrong document, and never silently retry forever. Also pins that the
        retry actually runs its full budget (`E._REPLACE_ATTEMPTS` calls)
        before giving up, rather than bailing early."""
        self.path.write_text(json.dumps(SAMPLE, indent=2) + "\n", encoding="utf-8")
        calls = [0]

        def always_busy(**kwargs):
            calls[0] += 1
            exc = PermissionError(13, "Access is denied")
            exc.winerror = 32  # ERROR_SHARING_VIOLATION
            raise exc

        with mock.patch.object(Path, "read_text", side_effect=always_busy):
            with self.assertRaises(PermissionError):
                E.load(self.path)
        self.assertEqual(calls[0], E._REPLACE_ATTEMPTS,
                         "the read retry gave up before exhausting its budget")

    def test_a_non_busy_read_OSError_is_NOT_retried(self):
        """Symmetric with `test_a_non_busy_OSError_is_NOT_retried`: a real read
        failure -- not the transient busy shape -- must fail on the FIRST
        attempt, or a genuine problem (a vanished directory, a real
        permission error) turns into a slow failure instead of a fast,
        honest one."""
        self.path.write_text(json.dumps(SAMPLE, indent=2) + "\n", encoding="utf-8")
        calls = [0]

        def other_error(**kwargs):
            calls[0] += 1
            raise OSError(errno.ENOENT, "No such file or directory")

        with mock.patch.object(Path, "read_text", side_effect=other_error):
            with self.assertRaises(OSError):
                E.load(self.path)
        self.assertEqual(calls[0], 1, "a non-busy OSError was retried; it must not be")

    def test_a_bare_permission_error_is_retried_as_busy_on_windows(self):
        """`_read_busy_on_windows` treats a bare `PermissionError` (`errno.EACCES`,
        NO `winerror` at all) as busy too -- but its own docstring says this is
        scoped to `os.name == "nt"` ONLY. This pins the Windows leg of that
        split: on `nt`, the bare shape IS retried."""
        self.path.write_text(json.dumps(SAMPLE, indent=2) + "\n", encoding="utf-8")
        real_read_text = Path.read_text
        calls = [0]

        def bare_then_ok(**kwargs):
            calls[0] += 1
            if calls[0] <= 2:
                raise PermissionError(errno.EACCES, "Access is denied")  # no winerror
            return real_read_text(self.path, **kwargs)

        with mock.patch.object(E.os, "name", "nt"), \
             mock.patch.object(Path, "read_text", side_effect=bare_then_ok):
            doc = E.load(self.path)
        self.assertEqual(calls[0], 3, "a bare PermissionError was not retried on Windows")
        self.assertEqual(doc, SAMPLE)

    def test_a_bare_permission_error_is_NOT_retried_off_windows(self):
        """The other half of the same split: off Windows, a bare
        `PermissionError(EACCES)` is a REAL permission problem -- `rename(2)`
        never invalidates an open reader on POSIX, so nothing transient
        produces this shape there -- and must fail on the FIRST attempt, not
        be retried into a slow success-that-should-have-failed (see
        `test_an_unreadable_spine_file_is_refused` for the same posture
        enforced elsewhere)."""
        self.path.write_text(json.dumps(SAMPLE, indent=2) + "\n", encoding="utf-8")
        calls = [0]

        def bare(**kwargs):
            calls[0] += 1
            raise PermissionError(errno.EACCES, "Permission denied")

        with mock.patch.object(E.os, "name", "posix"), \
             mock.patch.object(Path, "read_text", side_effect=bare):
            with self.assertRaises(PermissionError):
                E.load(self.path)
        self.assertEqual(calls[0], 1,
                         "a bare PermissionError was retried off Windows; it must not be")

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


if __name__ == "__main__":
    unittest.main()
