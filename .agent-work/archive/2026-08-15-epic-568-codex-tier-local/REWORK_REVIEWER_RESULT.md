# Rework reviewer result

Verdict: APPROVE

## Evidence

- CLI parser to `ExternalBackend` registry persistence is covered through the
  checked-in entrypoint, not a reconstructed `CrewSpec`:
  `tests/test_crew_launcher.py:1864-1883` calls `RC.main(...)` with
  `--backend external`, `--model gpt-5.6`, and `--reasoning-effort xhigh`, proves
  no launcher call occurred, reloads `crew-runs.json`, and asserts all backend,
  model, and reasoning-effort values. The production chain is direct:
  `scripts/run_crew.py:1500` parses the option, `1702-1707` puts it on
  `CrewSpec`, `1297-1303` passes it into the shared entry builder, and
  `949-950` conditionally persists it.

- Abandon/relaunch inheritance is covered through `RC.main(...)` and durable
  registry reload at `tests/test_crew_launcher.py:824-848`. The test seeds a
  prior record with `reasoning_effort: high`, omits the option from the
  relaunch CLI, and proves attempt 2 retains `high`. The implementation uses a
  CLI override when supplied and otherwise reads the abandoned entry at
  `scripts/run_crew.py:1678-1685`.

- Legacy omission compatibility is covered at
  `tests/test_crew_launcher.py:850-873`: a legacy record with no
  `reasoning_effort` relaunches successfully and the new entry still omits the
  field. Ordinary resume compatibility for an omitted field is also exercised
  at `2422-2435`.

- No Claude `--reasoning-effort` flag is emitted. `CliBackend.dispatch` records
  `spec.reasoning_effort` at `scripts/run_crew.py:1167-1174`, but its argv call
  at `1182-1187` has no reasoning-effort argument. Checked-in assertions cover
  initial CLI dispatch (`tests/test_crew_launcher.py:2387-2402`), resume
  (`2404-2420`), legacy resume (`2422-2435`), and abandon/relaunch (`824-848`).

- Optional metadata scope and backward compatibility are preserved:
  `CrewSpec.reasoning_effort` defaults to `None` (`scripts/run_crew.py:1074`),
  both public wrapper additions are optional keyword-only parameters
  (`1367`, `1426`), and `build_entry` omits the key when no value is supplied
  (`949-950`). Existing registry records therefore do not require migration.
  The field influences registry inspection/relaunch metadata only and does not
  enter process argv or environment construction.

## Verification

```text
python -m pytest -q tests/test_crew_launcher.py
166 passed in 0.54s
```

`git diff --check -- scripts/run_crew.py tests/test_crew_launcher.py` also
completed cleanly.

## Remaining risk

- `--reasoning-effort` accepts an arbitrary string rather than a constrained
  enum. That is consistent with metadata-only transport and does not affect
  Claude argv, but downstream external dispatch consumers remain responsible
  for validating whether a recorded value is supported by their selected
  Codex model.
- The tests use the launch seam rather than a real Claude executable. They
  conclusively inspect constructed argv, which is the relevant contract here,
  but do not constitute an end-to-end launcher binary integration test.
