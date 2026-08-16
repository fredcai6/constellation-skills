import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


NOW = datetime(2026, 7, 18, 12, 0, 0, tzinfo=timezone.utc)
MAX_AGE = timedelta(minutes=30)

FRESH_RECORD = {
    "schema_version": 1,
    "fill_fraction": 0.42,
    "model": "claude-opus-4-8",
    "observed_at": (NOW - timedelta(minutes=5)).isoformat(),
}


class UncalibratedModelTests(unittest.TestCase):
    """#252: a model with no profile must yield NO reading, and the reason must
    be retrievable so a caller can explain the silence."""

    def setUp(self):
        self.m = load("gauge_reader")
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "gauge.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _write_flag(self, model):
        (self.path.with_name(self.m.UNCALIBRATED_FILENAME)).write_text(
            json.dumps({"schema_version": 1, "model": model,
                        "observed_at": NOW.isoformat()}), encoding="utf-8")

    def test_record_for_uncalibrated_model_yields_no_reading(self):
        """Otherwise Trip judges the fill against DEFAULT_THRESHOLDS, i.e. the
        wrong scale — the exact failure #252 reports. The record here is
        perfectly fresh and well-formed; only the model is unknown."""
        record = dict(FRESH_RECORD, model="claude-future-9")
        self.path.write_text(json.dumps(record), encoding="utf-8")
        self.assertIsNone(self.m.read(self.path, now=NOW, max_age=MAX_AGE))

    def test_calibrated_model_still_reads(self):
        self.path.write_text(json.dumps(FRESH_RECORD), encoding="utf-8")
        self.assertIsNotNone(self.m.read(self.path, now=NOW, max_age=MAX_AGE))

    def test_uncalibrated_model_reports_the_model(self):
        self._write_flag("claude-future-9")
        self.assertEqual("claude-future-9", self.m.uncalibrated_model(self.path))

    def test_no_flag_reports_none(self):
        self.assertIsNone(self.m.uncalibrated_model(self.path))

    def test_flag_naming_a_now_calibrated_model_is_ignored(self):
        """A row added since the flag was written makes it obsolete — report
        nothing rather than nag about a model that now resolves fine."""
        self._write_flag("claude-opus-5")
        self.assertIsNone(self.m.uncalibrated_model(self.path))

    def test_corrupt_flag_never_raises(self):
        (self.path.with_name(self.m.UNCALIBRATED_FILENAME)).write_text(
            "{not json", encoding="utf-8")
        self.assertIsNone(self.m.uncalibrated_model(self.path))


class ModelTableSyncTests(unittest.TestCase):
    """The writer supplies the window, the reader supplies the thresholds. A
    model in only one table is a half-added model: either no reading is ever
    produced for it, or a reading is produced that the reader then rejects.
    Both are silent, so pin the key sets equal."""

    def test_writer_and_reader_cover_the_same_models(self):
        reader = load("gauge_reader")
        spec = importlib.util.spec_from_file_location(
            "gauge_writer_hook", ROOT / "scripts" / "hooks" / "gauge_writer_hook.py")
        writer = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = writer
        spec.loader.exec_module(writer)

        self.assertEqual(set(writer.MODEL_WINDOWS), set(reader._PROFILES))

    def test_windows_agree_between_the_two_tables(self):
        """The reader stores the window alongside its caps; a disagreement
        would make the same model read at two different scales."""
        reader = load("gauge_reader")
        spec = importlib.util.spec_from_file_location(
            "gauge_writer_hook", ROOT / "scripts" / "hooks" / "gauge_writer_hook.py")
        writer = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = writer
        spec.loader.exec_module(writer)

        for model, window in writer.MODEL_WINDOWS.items():
            self.assertEqual(window, reader._PROFILES[model][0], model)


class ReadTests(unittest.TestCase):
    def setUp(self):
        self.m = load("gauge_reader")
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "gauge.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, record):
        self.path.write_text(json.dumps(record), encoding="utf-8")

    def _read(self, now=NOW, max_age=MAX_AGE):
        return self.m.read(self.path, now=now, max_age=max_age)

    # -- the five failure modes: every one collapses to None -----------------

    def test_absent_file_returns_none(self):
        self.assertIsNone(self._read())

    def test_corrupt_json_returns_none(self):
        self.path.write_text("{not valid json", encoding="utf-8")
        self.assertIsNone(self._read())

    def test_missing_field_returns_none(self):
        record = dict(FRESH_RECORD)
        del record["fill_fraction"]
        self._write(record)
        self.assertIsNone(self._read())

    def test_wrong_typed_field_returns_none(self):
        record = dict(FRESH_RECORD, fill_fraction="0.42")
        self._write(record)
        self.assertIsNone(self._read())

    def test_out_of_range_fill_fraction_returns_none(self):
        record = dict(FRESH_RECORD, fill_fraction=1.5)
        self._write(record)
        self.assertIsNone(self._read())

    def test_bool_schema_version_returns_none(self):
        record = dict(FRESH_RECORD, schema_version=True)
        self._write(record)
        self.assertIsNone(self._read())

    def test_unparseable_observed_at_returns_none(self):
        record = dict(FRESH_RECORD, observed_at="not-a-timestamp")
        self._write(record)
        self.assertIsNone(self._read())

    def test_stale_record_returns_none(self):
        record = dict(FRESH_RECORD, observed_at=(NOW - timedelta(hours=2)).isoformat())
        self._write(record)
        self.assertIsNone(self._read())

    def test_clock_skew_returns_none(self):
        # observed_at far in the future -- writer/reader clocks disagree.
        record = dict(FRESH_RECORD, observed_at=(NOW + timedelta(hours=1)).isoformat())
        self._write(record)
        self.assertIsNone(self._read())

    # -- a stale record NEVER yields a usable reading, across the boundary ---

    def test_stale_never_yields_a_reading_at_the_boundary(self):
        just_stale = dict(FRESH_RECORD, observed_at=(NOW - MAX_AGE - timedelta(seconds=1)).isoformat())
        self._write(just_stale)
        self.assertIsNone(self._read())

    # -- the happy path -------------------------------------------------------

    def test_fresh_record_returns_a_reading(self):
        self._write(FRESH_RECORD)
        reading = self._read()
        self.assertIsNotNone(reading)
        self.assertEqual(reading.schema_version, 1)
        self.assertEqual(reading.fill_fraction, 0.42)
        self.assertEqual(reading.model, "claude-opus-4-8")
        self.assertEqual(reading.observed_at, NOW - timedelta(minutes=5))

    def test_small_clock_skew_within_tolerance_still_reads(self):
        # A few seconds of future skew is ordinary clock drift, not a
        # fabricated reading -- must still resolve.
        record = dict(FRESH_RECORD, observed_at=(NOW + timedelta(seconds=30)).isoformat())
        self._write(record)
        self.assertIsNotNone(self._read())

    def test_naive_now_does_not_raise(self):
        # A caller passing a naive `now` (e.g. `datetime.now()` instead of
        # `datetime.now(timezone.utc)`) must never crash the subtraction
        # against the tz-aware `observed_at` -- that would violate the
        # reader's never-raises contract on every well-formed record.
        self._write(FRESH_RECORD)
        naive_now = NOW.replace(tzinfo=None)
        reading = self.m.read(self.path, now=naive_now, max_age=MAX_AGE)
        self.assertIsNotNone(reading)
        self.assertEqual(reading.fill_fraction, 0.42)


class RawRecordTests(unittest.TestCase):
    """#265: raw_record reports the file's own facts with field-shape
    validation only -- no staleness, no clock-skew, no calibration gate. The
    caller-facing purpose is a frozen `gauge.json` `read()` itself rejected
    (e.g. simply too old) still has SOMETHING honest to say about it."""

    def setUp(self):
        self.m = load("gauge_reader")
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "gauge.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, record):
        self.path.write_text(json.dumps(record), encoding="utf-8")

    def test_absent_file_returns_none(self):
        self.assertIsNone(self.m.raw_record(self.path))

    def test_corrupt_json_returns_none(self):
        self.path.write_text("{not valid json", encoding="utf-8")
        self.assertIsNone(self.m.raw_record(self.path))

    def test_missing_field_returns_none(self):
        record = dict(FRESH_RECORD)
        del record["model"]
        self._write(record)
        self.assertIsNone(self.m.raw_record(self.path))

    def test_wrong_typed_field_returns_none(self):
        record = dict(FRESH_RECORD, fill_fraction="0.42")
        self._write(record)
        self.assertIsNone(self.m.raw_record(self.path))

    def test_stale_record_STILL_reports_raw_facts(self):
        # The whole point: read() rejects this (too old), raw_record does not.
        stale = dict(FRESH_RECORD, observed_at=(NOW - timedelta(hours=2)).isoformat())
        self._write(stale)
        self.assertIsNone(self.m.read(self.path, now=NOW, max_age=MAX_AGE))
        raw = self.m.raw_record(self.path)
        self.assertIsNotNone(raw)
        self.assertEqual(raw["fill_fraction"], 0.42)
        self.assertEqual(raw["model"], "claude-opus-4-8")
        self.assertEqual(raw["observed_at"], NOW - timedelta(hours=2))

    def test_uncalibrated_model_STILL_reports_raw_facts(self):
        # read() rejects an uncalibrated model too -- raw_record has no
        # calibration-table gate, so it still reports the number as-is.
        record = dict(FRESH_RECORD, model="claude-future-9")
        self._write(record)
        self.assertIsNone(self.m.read(self.path, now=NOW, max_age=MAX_AGE))
        raw = self.m.raw_record(self.path)
        self.assertIsNotNone(raw)
        self.assertEqual(raw["model"], "claude-future-9")

    def test_clock_skew_STILL_reports_raw_facts(self):
        record = dict(FRESH_RECORD, observed_at=(NOW + timedelta(hours=1)).isoformat())
        self._write(record)
        self.assertIsNone(self.m.read(self.path, now=NOW, max_age=MAX_AGE))
        raw = self.m.raw_record(self.path)
        self.assertIsNotNone(raw)

    def test_fresh_record_reports_same_facts_as_a_reading(self):
        self._write(FRESH_RECORD)
        raw = self.m.raw_record(self.path)
        reading = self.m.read(self.path, now=NOW, max_age=MAX_AGE)
        self.assertEqual(raw["fill_fraction"], reading.fill_fraction)
        self.assertEqual(raw["model"], reading.model)
        self.assertEqual(raw["observed_at"], reading.observed_at)

    def test_returns_exactly_three_keys(self):
        # No schema_version, no threshold judgment folded in -- raw facts only.
        self._write(FRESH_RECORD)
        self.assertEqual(set(self.m.raw_record(self.path)), {"fill_fraction", "model", "observed_at"})


class SkipReasonTests(unittest.TestCase):
    """#265: skip_reason mirrors uncalibrated_model's fail-safe contract for
    the writer hook's gauge-skip.json sidecar."""

    def setUp(self):
        self.m = load("gauge_reader")
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "gauge.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _write_skip(self, **overrides):
        record = {
            "schema_version": 1,
            "reason": "ambiguous-binding",
            "observed_at": NOW.isoformat(),
            "candidate_count": 2,
        }
        record.update(overrides)
        (self.path.with_name(self.m.SKIP_FILENAME)).write_text(
            json.dumps(record), encoding="utf-8")

    def test_no_sidecar_returns_none(self):
        self.assertIsNone(self.m.skip_reason(self.path))

    def test_corrupt_sidecar_never_raises(self):
        (self.path.with_name(self.m.SKIP_FILENAME)).write_text(
            "{not json", encoding="utf-8")
        self.assertIsNone(self.m.skip_reason(self.path))

    def test_ambiguous_binding_reports_reason_and_candidate_count(self):
        self._write_skip(reason="ambiguous-binding", candidate_count=3)
        info = self.m.skip_reason(self.path)
        self.assertEqual(info["reason"], "ambiguous-binding")
        self.assertEqual(info["candidate_count"], 3)
        self.assertEqual(info["observed_at"], NOW)

    def test_no_usable_record_has_no_candidate_count_key(self):
        record = {
            "schema_version": 1,
            "reason": "no-usable-record",
            "observed_at": NOW.isoformat(),
        }
        (self.path.with_name(self.m.SKIP_FILENAME)).write_text(
            json.dumps(record), encoding="utf-8")
        info = self.m.skip_reason(self.path)
        self.assertEqual(info["reason"], "no-usable-record")
        self.assertNotIn("candidate_count", info)

    def test_missing_reason_returns_none(self):
        self._write_skip(reason=None)
        self.assertIsNone(self.m.skip_reason(self.path))

    def test_missing_observed_at_returns_none(self):
        self._write_skip(observed_at=None)
        self.assertIsNone(self.m.skip_reason(self.path))

    def test_unparseable_observed_at_returns_none(self):
        self._write_skip(observed_at="not-a-timestamp")
        self.assertIsNone(self.m.skip_reason(self.path))

    def test_bool_candidate_count_is_dropped_not_reported(self):
        # bool is a subclass of int -- must not pass as a valid candidate_count.
        self._write_skip(candidate_count=True)
        info = self.m.skip_reason(self.path)
        self.assertIsNotNone(info)
        self.assertNotIn("candidate_count", info)

    def test_non_int_candidate_count_is_dropped_not_reported(self):
        self._write_skip(candidate_count="3")
        info = self.m.skip_reason(self.path)
        self.assertIsNotNone(info)
        self.assertNotIn("candidate_count", info)

    def test_never_staleness_checked(self):
        # Deliberately NOT staleness-checked -- a caller renders the raw age.
        old = NOW - timedelta(days=3)
        self._write_skip(observed_at=old.isoformat())
        info = self.m.skip_reason(self.path)
        self.assertEqual(info["observed_at"], old)


class ThresholdsForTests(unittest.TestCase):
    def setUp(self):
        self.m = load("gauge_reader")

    def test_unknown_model_falls_back_to_default(self):
        self.assertEqual(self.m.thresholds_for("some-unlisted-model"), self.m.DEFAULT_THRESHOLDS)

    def test_known_model_returns_its_keyed_pair(self):
        # Seed a known model in the NEW absolute-cap table for this test,
        # independent of whatever real entries the module ships with. The
        # profile is (window, soft_cap, hard_cap); thresholds_for divides to
        # (soft_cap/window, hard_cap/window) == (0.5, 0.8) here.
        self.m._PROFILES["test-model"] = (100_000, 50_000, 80_000)
        self.assertEqual(self.m.thresholds_for("test-model"), (0.5, 0.8))

    def test_equivalence_to_prior_fraction_literals(self):
        # The refactor from (soft,hard) fractions to absolute-token caps must
        # move NO trip point. Assert thresholds_for reproduces the PRIOR shipped
        # fractions, written here as INDEPENDENT hardcoded literals (NOT read
        # back off the new table -- that would be circular and prove nothing).
        expected = {
            "claude-opus-4-8": (0.08, 0.15),
            "claude-sonnet-5": (0.08, 0.15),
            "claude-fable-5": (0.08, 0.15),
            "claude-haiku-4-5-20251001": (0.45, 0.70),
        }
        for model, pair in expected.items():
            self.assertEqual(self.m.thresholds_for(model), pair)
        # unknown model -> the prior default fraction pair, also a literal.
        self.assertEqual(self.m.thresholds_for("some-unlisted-model"), (0.40, 0.65))

    def test_trip_points_unchanged_at_boundary(self):
        # Prove the SOFT/HARD bands are entered at exactly the same fills as
        # before. For each model, at a fill EQUAL to the literal soft (resp.
        # hard) fraction the band is entered (Trip uses fill >= soft / >= hard),
        # and just below it is not. Boundary values are the independent literals.
        literals = {
            "claude-opus-4-8": (0.08, 0.15),
            "claude-sonnet-5": (0.08, 0.15),
            "claude-fable-5": (0.08, 0.15),
            "claude-haiku-4-5-20251001": (0.45, 0.70),
            "some-unlisted-model": (0.40, 0.65),
        }
        eps = 1e-9
        for model, (soft, hard) in literals.items():
            got_soft, got_hard = self.m.thresholds_for(model)
            # SOFT band: entered at fill == soft, not at fill just below.
            self.assertTrue(soft >= got_soft)
            self.assertFalse((soft - eps) >= got_soft)
            # HARD band: entered at fill == hard, not at fill just below.
            self.assertTrue(hard >= got_hard)
            self.assertFalse((hard - eps) >= got_hard)

    def test_calibrated_shipped_thresholds(self):
        # Lock the human-approved calibration (context-rot research, 2026-07-19).
        # 1M-window models trip at small fractions (absolute cap dominates);
        # the 200K model keeps the classic ~0.5/0.75-ish fractions.
        self.assertEqual(self.m.thresholds_for("claude-opus-4-8"), (0.08, 0.15))
        self.assertEqual(self.m.thresholds_for("claude-sonnet-5"), (0.08, 0.15))
        self.assertEqual(self.m.thresholds_for("claude-fable-5"), (0.08, 0.15))
        self.assertEqual(self.m.thresholds_for("claude-haiku-4-5-20251001"), (0.45, 0.70))
        self.assertEqual(self.m.DEFAULT_THRESHOLDS, (0.40, 0.65))
        # soft strictly below hard for every shipped model (invariant).
        for model in ("claude-opus-4-8", "claude-sonnet-5", "claude-fable-5",
                      "claude-haiku-4-5-20251001"):
            soft, hard = self.m.thresholds_for(model)
            self.assertLess(soft, hard)


class ThresholdsHeadroomOverrideTests(unittest.TestCase):
    """#467 (a): the per-gate context-headroom override. `thresholds_for` takes an
    absolute-token reserve, subtracts it from BOTH caps before dividing by the
    window, and clamps so the override can only ever TIGHTEN.

    TIGHTEN-ONLY IS A SAFETY PROPERTY, not a style choice: an override that could
    RAISE a threshold would let a gate opt out of the governor. So the sweep below
    is hostile (negatives, a huge negative, absurd positives) and asserts the
    returned pair is never above the un-overridden pair for ANY input."""

    # Every value the hostile sweep tries. Negatives and zero must be no-ops;
    # positives must tighten or clamp; none may ever loosen.
    HOSTILE_RESERVES = (-10 ** 12, -150_000, -1, 0, 1, 79_999, 150_000, 10 ** 12)
    SHIPPED_MODELS = ("claude-opus-5", "claude-opus-4-8", "claude-sonnet-5",
                      "claude-fable-5", "claude-haiku-4-5-20251001",
                      "some-unlisted-model")

    def setUp(self):
        self.m = load("gauge_reader")

    def test_headroom_reserve_tightens_both_caps(self):
        # claude-opus-5 is (1_000_000, 80_000, 150_000). A 30K reserve comes off
        # BOTH caps before the division -- literals written independently here,
        # never read back off the table (that would be circular).
        self.assertEqual(self.m.thresholds_for("claude-opus-5"), (0.08, 0.15))
        self.assertEqual(self.m.thresholds_for("claude-opus-5", 30_000), (0.05, 0.12))
        # ... and on the 200K model, the same absolute reserve bites HARDER as a
        # fraction, which is the whole point of an absolute-token reserve:
        # (90_000-30_000)/200_000, (140_000-30_000)/200_000.
        self.assertEqual(
            self.m.thresholds_for("claude-haiku-4-5-20251001", 30_000), (0.30, 0.55))

    def test_headroom_override_of_zero_is_exactly_the_shipped_default(self):
        # The production default is a floor no gate may lower: a zero (or omitted)
        # reserve must reproduce the shipped pair exactly, for every model.
        for model in self.SHIPPED_MODELS:
            self.assertEqual(self.m.thresholds_for(model, 0),
                             self.m.thresholds_for(model))

    def test_headroom_reserve_larger_than_a_cap_clamps_at_zero(self):
        # A reserve bigger than the soft cap floors THAT fraction at 0.0 without
        # going negative, while the hard cap keeps tightening on its own terms.
        self.assertEqual(self.m.thresholds_for("claude-opus-5", 100_000), (0.0, 0.05))
        # A reserve bigger than both caps floors both -- the tightest possible
        # gate (trip immediately), never a negative fraction.
        self.assertEqual(self.m.thresholds_for("claude-opus-5", 10 ** 9), (0.0, 0.0))

    def test_headroom_override_can_only_tighten_never_loosen(self):
        # THE safety property, swept hostilely: across every shipped model and
        # every reserve above, the overridden pair is never ABOVE the default
        # pair. A raised threshold would mean a gate opting OUT of the governor.
        for model in self.SHIPPED_MODELS:
            base_soft, base_hard = self.m.thresholds_for(model)
            for reserve in self.HOSTILE_RESERVES:
                with self.subTest(model=model, reserve=reserve):
                    soft, hard = self.m.thresholds_for(model, reserve)
                    self.assertLessEqual(soft, base_soft)
                    self.assertLessEqual(hard, base_hard)
                    self.assertGreaterEqual(soft, 0.0)
                    self.assertGreaterEqual(hard, 0.0)
                    if reserve <= 0:
                        # A negative reserve is a NO-OP, not a loosening: it
                        # resolves to exactly the shipped default.
                        self.assertEqual((soft, hard), (base_soft, base_hard))

    def test_headroom_override_never_judges_an_uncalibrated_model(self):
        # #252 guard, restated under the override: `thresholds_for` stays TOTAL
        # (an arbitrary model string still yields a usable pair, computed off
        # _DEFAULT_PROFILE's own 200K window -- (80_000-30_000)/200_000 and
        # (130_000-30_000)/200_000), but that pair must never be reached from a
        # real READING. An uncalibrated model yields no reading at all, so no
        # override can ever be judged against a guessed window.
        self.assertEqual(self.m.thresholds_for("some-unlisted-model", 30_000), (0.25, 0.50))
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "gauge.json"
            path.write_text(json.dumps({
                "schema_version": 1, "fill_fraction": 0.42,
                "model": "some-unlisted-model",
                "observed_at": (NOW - timedelta(minutes=5)).isoformat(),
            }), encoding="utf-8")
            self.assertIsNone(self.m.read(path, now=NOW, max_age=MAX_AGE))


class ImpliedTokensTests(unittest.TestCase):
    """#264: the HEADLINE rendering. A fill FRACTION is unfalsifiable on its
    own -- 0.69875 looks like a perfectly ordinary reading. The same fraction
    rendered as an ABSOLUTE token count against a window a human knows is wrong
    on its face (decision:implied-tokens-over-ceiling-predicate).

    It is a derived rendering, never a judgment: nothing in this class asserts
    anything about how full is acceptable."""

    def setUp(self):
        self.m = load("gauge_reader")

    def _reading(self, fill, model="claude-opus-4-8"):
        return self.m.Reading(
            schema_version=1, fill_fraction=fill, model=model, observed_at=NOW)

    def test_implied_count_is_the_fraction_against_the_readers_own_window(self):
        window = self.m._PROFILES["claude-opus-4-8"][0]
        self.assertEqual(
            round(window * 0.42), self.m.implied_tokens(self._reading(0.42)))

    def test_the_252_divergence_is_rendered_absurd_rather_than_plausible(self):
        """THE POINT OF THE WHOLE FUNCTION, on the real incident numbers.

        #252: 139,750 real tokens were divided by a wrongly-assumed 200K window
        and written as fill_fraction 0.69875. As a fraction that reads as an
        unremarkable ~70%. Rendered against claude-opus-5's REAL window it
        comes back as ~698,750 tokens -- five times the session that actually
        happened, and wrong on its face to anyone who knows the model, with no
        recall of session size required.

        The expected value is computed from the table at test time, not typed:
        a re-calibration of the window must move this rendering with it."""
        real_tokens = 139_750
        wrong_window = 200_000
        as_written = real_tokens / wrong_window  # what the writer actually emitted

        implied = self.m.implied_tokens(self._reading(as_written, "claude-opus-5"))
        true_window = self.m._PROFILES["claude-opus-5"][0]

        self.assertEqual(round(true_window * as_written), implied)
        # The rendering is what makes the divergence legible: the implied count
        # is nothing like the session that really happened.
        self.assertNotEqual(real_tokens, implied)
        self.assertGreater(implied, real_tokens * 4)

    def test_a_reading_that_came_through_read_renders_end_to_end(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "gauge.json"
        path.write_text(json.dumps(FRESH_RECORD), encoding="utf-8")

        reading = self.m.read(path, now=NOW, max_age=MAX_AGE)
        window = self.m._PROFILES[reading.model][0]
        self.assertEqual(
            round(window * reading.fill_fraction), self.m.implied_tokens(reading))

    def test_uncalibrated_model_renders_NOTHING_not_a_default_scaled_count(self):
        """Same rule as read()'s own #252 gate: an uncertain model must yield no
        number, never a wrong one. _DEFAULT_PROFILE exists to keep
        thresholds_for total; it must not leak into this rendering."""
        self.assertIsNone(
            self.m.implied_tokens(self._reading(0.42, "claude-future-9")))
        # ...even though thresholds_for still answers for that model.
        self.assertEqual(
            self.m.DEFAULT_THRESHOLDS, self.m.thresholds_for("claude-future-9"))

    def test_zero_fill_renders_zero_not_none(self):
        # 0 is a real reading, not a missing one -- `if implied_tokens(r):`
        # would be a caller bug, but this function must not manufacture the
        # ambiguity by returning None for a legitimate zero.
        self.assertEqual(0, self.m.implied_tokens(self._reading(0.0)))

    def test_every_malformed_input_returns_none_and_never_raises(self):
        window_model = "claude-opus-4-8"
        for label, value in (
            ("no attributes at all", object()),
            ("None", None),
            ("a bare string", "0.42"),
            ("string fill", SimpleNamespace(fill_fraction="0.42", model=window_model)),
            ("bool fill", SimpleNamespace(fill_fraction=True, model=window_model)),
            ("None fill", SimpleNamespace(fill_fraction=None, model=window_model)),
            ("non-str model", SimpleNamespace(fill_fraction=0.42, model=1)),
            ("None model", SimpleNamespace(fill_fraction=0.42, model=None)),
            ("nan fill", SimpleNamespace(fill_fraction=float("nan"), model=window_model)),
            ("inf fill", SimpleNamespace(fill_fraction=float("inf"), model=window_model)),
        ):
            with self.subTest(label):
                self.assertIsNone(self.m.implied_tokens(value))


class PinnedAtCeilingTests(unittest.TestCase):
    """#264 SECONDARY notice. Deliberately not the answer to this issue --
    implied_tokens is. These tests pin both its reach and its limit."""

    def setUp(self):
        self.m = load("gauge_reader")

    def test_a_pinned_reading_is_reported(self):
        self.assertTrue(self.m.pinned_at_ceiling(self.m.FILL_CEILING))

    def test_an_unpinned_reading_is_not(self):
        self.assertFalse(self.m.pinned_at_ceiling(0.0))
        self.assertFalse(self.m.pinned_at_ceiling(self.m.FILL_CEILING / 2))

    def test_it_is_SILENT_across_the_range_where_a_wrong_window_actually_hurt(self):
        """Why it is secondary, asserted rather than asserted-in-prose: both
        real incident readings are below the ceiling, so this predicate says
        nothing about either of them."""
        for label, fill in (("#252", 0.69875), ("#271", 0.126658)):
            with self.subTest(label):
                self.assertFalse(self.m.pinned_at_ceiling(fill))

    def test_the_engine_already_blocks_long_before_the_ceiling_is_reachable(self):
        """The structural reason it fires too late: every shipped profile has
        hard_cap < window, so HARD is entered at hard_cap tokens while the
        clamp only saturates at `window` tokens. No value is typed; the gap is
        read off the table."""
        for model, (window, _soft_cap, hard_cap) in self.m._PROFILES.items():
            with self.subTest(model=model):
                self.assertLess(hard_cap, window)

    def test_a_double_counted_numerator_is_INDISTINGUISHABLE_from_a_small_window(self):
        """THE EXACT LIMIT. A pinned reading proves the RATIO is wrong -- the
        window too small OR the token count too large -- and cannot say which.
        Both causes arrive here as the identical value, so no caller can ever
        recover the cause from the predicate."""
        window = self.m._PROFILES["claude-opus-5"][0]
        tokens = window // 2

        window_too_small = min(self.m.FILL_CEILING, tokens / (window // 5))
        numerator_doubled_twice = min(self.m.FILL_CEILING, (tokens * 4) / window)

        self.assertEqual(window_too_small, numerator_doubled_twice)
        self.assertTrue(self.m.pinned_at_ceiling(window_too_small))
        self.assertTrue(self.m.pinned_at_ceiling(numerator_doubled_twice))

    def test_it_can_never_prove_a_window_RIGHT(self):
        """The other half of the one-directional falsifier: an UNPINNED reading
        is consistent with any window large enough not to saturate, so silence
        here is not evidence of a correct window."""
        tokens = 100_000
        for window in (400_000, 1_000_000, 8_000_000):
            with self.subTest(window=window):
                self.assertFalse(self.m.pinned_at_ceiling(tokens / window))

    def test_the_docstring_indicts_the_RATIO_not_the_denominator(self):
        """A wording pin, not decoration (decision:one-directional-falsifier).
        'Denominator' names one of the two causes and is therefore a false
        claim about what this predicate can establish; it was corrected once
        during planning and a regression would be silent."""
        doc = self.m.pinned_at_ceiling.__doc__
        self.assertIn("RATIO", doc)
        self.assertNotIn("denominator", doc.lower())

    def test_non_numeric_fill_is_false_never_an_exception(self):
        for value in (None, "1.0", object(), True, False):
            with self.subTest(repr(value)):
                self.assertFalse(self.m.pinned_at_ceiling(value))


class ProfileInvariantTests(unittest.TestCase):
    """#264 REGRESSION PIN, asserted nowhere in this repo until now. It passes
    at HEAD on all five shipped profiles by design -- it is not a bug report.

    What it catches is a row whose window is set so low that the gauge is
    STRUCTURALLY INCAPABLE of tripping before it saturates: with
    `hard_cap >= window` the clamp pins the reading at the ceiling at or before
    the moment HARD would have been entered, so the band the whole governor
    exists to reach can never fire cleanly for that model. Nothing else in the
    suite would notice -- every threshold test would still pass, because each
    one only ever looks at a single model's arithmetic in isolation."""

    def setUp(self):
        self.m = load("gauge_reader")

    def _assert_ordered(self, model, profile):
        window, soft_cap, hard_cap = profile
        self.assertLess(
            0, soft_cap, f"{model}: soft_cap must be a positive token count")
        self.assertLess(
            soft_cap, hard_cap,
            f"{model}: soft_cap {soft_cap} is not below hard_cap {hard_cap}, so "
            f"the two bands cannot be entered in order")
        self.assertLess(
            hard_cap, window,
            f"{model}: hard_cap {hard_cap} is not below window {window}, so the "
            f"reading saturates at or before HARD and the band can never fire "
            f"cleanly for this model")

    def test_every_profile_orders_zero_below_soft_below_hard_below_window(self):
        self.assertTrue(self.m._PROFILES, "the profile table must not be empty")
        for model, profile in self.m._PROFILES.items():
            with self.subTest(model=model):
                self._assert_ordered(model, profile)

    def test_the_default_profile_holds_the_same_invariant(self):
        """_DEFAULT_PROFILE is not a row of _PROFILES, but thresholds_for can
        still hand it out, so the same ordering has to hold for it."""
        self._assert_ordered("_DEFAULT_PROFILE", self.m._DEFAULT_PROFILE)


# --- #600: the owner key, normalized and total -------------------------------

# A corpus of REAL `engine_session.session_id` values, harvested by command from
# this checkout on 2026-08-16 (426 distinct values across every checklist JSON;
# 89 of them fail the `[A-Za-z0-9_-]{1,64}` allowlist an earlier draft of this
# change proposed to reject on). The slash-bearing names are not typos and not
# legacy -- they are current fleet practice, which is exactly why R2 ruled
# NORMALIZE, NEVER REJECT: rejecting would have taken the governor away from a
# fifth of the fleet permanently and invisibly, since losing the governor never
# shows up as a test failure.
#
# Pinned as a LITERAL rather than re-harvested at run time on purpose: a test
# that re-scans the live checkout would change its own corpus every time anyone
# claimed a lease, and would pass vacuously in a fresh clone.
_LIVE_SESSION_IDS = (
    # plain, already-allowlist-clean
    "admiral-epic-178",
    "commander-cleanup-b-context-identity",
    "impl-534-01",
    "g1-reviewer-01476478",
    "2fb330a4-dba9-409d-9005-a1342ed2cb19",
    "86708414-f5d3-40d3-8c9a-2f96d1ccdc14-interrogation",
    # slash-bearing -- the 89 (current fleet practice)
    "cartographer/epic-178",
    "constellation/cleanup-b-context-identity/g1/implementer/attempt-1",
    "constellation/archive/2026-08-09-epic-418-followon/commander-424/g3fix4/implementer/attempt-1",
    "constellation/epic-559/a-spine-is-the-job/g1-implement/implementer",
    "constellation/commander-315-native/g1b-review/reviewer",
    # a shell-quoting bug that reached the binding store verbatim, live in the
    # main checkout's store right now
    "$SID",
    "$SESSION",
)

# The two sidecar families the writer already owns. An owner key that
# normalized to either of these words would make `gauge-<owner>.json` collide
# with `gauge-skip.json` / `gauge-uncalibrated.json` -- so they are RESERVED.
_RESERVED = ("skip", "uncalibrated")


class OwnerKeyNormalization(unittest.TestCase):
    """#600 R2: every lease session id must yield a USABLE owner key.

    The key is slug plus hash. The slug is there so a human can read a
    directory listing and see whose file is whose; the hash is there so the
    slug's lossiness (case folding, separator collapsing, truncation) can never
    make two distinct sessions share one file -- which is the whole defect this
    issue exists to remove, and would be a fine way to reintroduce it."""

    def setUp(self):
        self.m = load("gauge_reader")

    def _assert_usable(self, owner, source):
        self.assertIsInstance(owner, str, f"{source!r} yielded no owner key")
        self.assertTrue(owner, f"{source!r} yielded an empty owner key")
        self.assertRegex(
            owner, r"^[a-z0-9_-]{1,64}$",
            f"{source!r} yielded {owner!r}, which is not safe to interpolate "
            f"into a filename")
        self.assertNotIn(
            owner, _RESERVED,
            f"{source!r} yielded the reserved sidecar name {owner!r}")

    def test_every_live_session_id_yields_a_usable_owner(self):
        """The headline: NOT ONE real id is rejected, and no two of them
        collide."""
        seen = {}
        for session_id in _LIVE_SESSION_IDS:
            with self.subTest(session_id=session_id):
                owner = self.m.owner_key(session_id)
                self._assert_usable(owner, session_id)
                # distinctness, which the slug alone cannot carry: these two
                # differ only past the slug's truncation point.
                self.assertNotIn(
                    owner, seen,
                    f"{session_id!r} collided with {seen.get(owner)!r} on "
                    f"owner key {owner!r}")
                seen[owner] = session_id
                # the filename the writer and the engine both compose from it
                name = self.m.gauge_filename(owner)
                self.assertEqual(name, f"gauge-{owner}.json")
                self.assertNotIn(name, (self.m.SKIP_FILENAME,
                                        self.m.UNCALIBRATED_FILENAME))

    def test_ids_differing_only_past_the_slug_truncation_still_differ(self):
        """The slug truncates at 32 characters and the fleet's real names share
        long prefixes, so this is the collision the hash exists to prevent --
        not a hypothetical."""
        a = "constellation/epic-568-510/g2-repair/commander/attempt-1"
        b = "constellation/epic-568-510/g3-engine/commander/attempt-1"
        self.assertNotEqual(self.m.owner_key(a), self.m.owner_key(b))

    def test_an_absent_session_id_yields_no_owner_not_a_crash(self):
        """R3: no owner means the UNOWNED `gauge.json` -- exactly today's
        behaviour -- never an exception and never a repaired name. The live
        binding store in the main checkout carries `engine_session: null`
        entries right now, so this is a real input, not a defensive stub."""
        for absent in (None, "", "   ", 17, [], {}):
            with self.subTest(absent=absent):
                self.assertIsNone(self.m.owner_key(absent))
        self.assertEqual(self.m.gauge_filename(None), self.m.GAUGE_FILENAME)
        self.assertEqual(self.m.GAUGE_FILENAME, "gauge.json")

    def test_the_owner_key_is_stable_across_calls_and_processes(self):
        """Both sides of a process boundary compute this independently (the
        hook from the binding entry, the engine from its own lease), so a key
        that varied per process would silently stop every reading resolving.
        Pinned against a hand-computed value, not against a re-run of the
        implementation."""
        self.assertEqual(self.m.owner_key("eng-1"), "eng-1-cf2640ffe69e")
        self.assertEqual(
            self.m.owner_key("commander-cleanup-b-context-identity"),
            "commander-cleanup-b-context-iden-88c76234484d")

    def test_the_record_owner_is_readable_back_off_the_file(self):
        """The filename removes the collision; the `owner` field makes a
        mismatch DETECTABLE if one ever reappears. Both, not either (R1)."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gauge-eng-1-cf2640ffe69e.json"
            record = dict(FRESH_RECORD)
            record["owner"] = "eng-1-cf2640ffe69e"
            path.write_text(json.dumps(record), encoding="utf-8")
            self.assertEqual(self.m.record_owner(path), "eng-1-cf2640ffe69e")
            # fail-safe, like every other entry point in this module
            self.assertIsNone(self.m.record_owner(Path(tmp) / "absent.json"))
            unowned = Path(tmp) / "gauge.json"
            unowned.write_text(json.dumps(FRESH_RECORD), encoding="utf-8")
            self.assertIsNone(self.m.record_owner(unowned))


if __name__ == "__main__":
    unittest.main()
