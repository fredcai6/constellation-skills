import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
