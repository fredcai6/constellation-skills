# Implementer rework result

## Scope completed

- Removed the unused `CliBackend.resume` read of `reasoning_effort`.
- Added checked-in CLI-to-`ExternalBackend` coverage proving `--model` and
  `--reasoning-effort` persist in `crew-runs.json` without spawning a CLI.
- Added abandon/relaunch coverage proving stored `reasoning_effort` is inherited
  and remains metadata-only (no Claude `--reasoning-effort` argument).
- Added a legacy registry relaunch case whose older entry omits the optional
  field; it relaunches successfully and leaves the field absent.

## Verification

Pre-edit focused baseline:

```text
python -m unittest tests.test_crew_launcher.BackendEquivalenceTests.test_reasoning_effort_is_metadata_only_and_recorded tests.test_crew_launcher.BackendEquivalenceTests.test_cli_resume_reads_reasoning_effort_from_registry tests.test_crew_launcher.BackendEquivalenceTests.test_legacy_resume_without_reasoning_effort_does_not_crash
...
Ran 3 tests in 0.003s
OK
```

The baseline was already green because the production paths already carried the
metadata; this rework adds direct coverage for the previously unproven paths.

Focused post-edit suite:

```text
python -m pytest -q tests/test_crew_launcher.py -k 'reasoning_effort or cli_parser_persists_model'
6 passed, 160 deselected in 0.07s
```

No Claude argv reasoning-effort flag was added.
