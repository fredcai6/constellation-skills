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


class ThresholdsForTests(unittest.TestCase):
    def setUp(self):
        self.m = load("gauge_reader")

    def test_unknown_model_falls_back_to_default(self):
        self.assertEqual(self.m.thresholds_for("some-unlisted-model"), self.m.DEFAULT_THRESHOLDS)

    def test_known_model_returns_its_keyed_pair(self):
        # Seed a known model in the table for this test, independent of
        # whatever real entries the module ships with.
        self.m._THRESHOLDS["test-model"] = (0.5, 0.8)
        self.assertEqual(self.m.thresholds_for("test-model"), (0.5, 0.8))


if __name__ == "__main__":
    unittest.main()
