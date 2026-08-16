# Working notes — cleanup-g-crew-tier (#611)

Sole writer this wave, per LAUNCH_ORDER File Ownership.

## g2-doctrine red/green evidence

RED (unedited `skills/commander/references/crew-dispatch.md`, before this gate's edit):

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q tests/test_crew_dispatch_doctrine.py
FAILED tests/test_crew_dispatch_doctrine.py::ModelTierDoctrineTests::test_doctrine_connects_the_field_to_the_flag_in_one_sentence
FAILED tests/test_crew_dispatch_doctrine.py::ModelTierDoctrineTests::test_doctrine_names_model_flag_and_suggested_tier_field
2 failed in 0.02s
```

First failure: `'--model' not found in` (full file text pasted by pytest) — confirms crew-dispatch.md
said nothing about `--model` at all before this edit, matching the `understand` step's independent
`grep -n "model" crew-dispatch.md` finding (zero hits).

GREEN (after adding the "Name a tier" section to `crew-dispatch.md`, before `## Crew recovery`):

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q tests/test_crew_dispatch_doctrine.py
..                                                                       [100%]
2 passed in 0.01s
```

Self-attestation (no independent reviewer on this reasoning gate — grading myself with the same
rigor a reviewer would apply, per the gate's own imperative): the connecting sentence is "Every
handoff's own **Suggested Model Tier** field (`IMPLEMENTER_HANDOFF.template.md:94`,
`REVIEWER_HANDOFF.template.md:60`) is the thing you resolve `--model` from before calling
`run_crew.py`" — one sentence, both terms, and it states the actual relationship (the field is
what the flag is resolved FROM), not just that both words appear in the document. The section also
states the refusal exists, states this file previously said nothing about model (measured at
`understand`), covers the `--effort`/`--reasoning-effort` connection, and explicitly scopes the
refusal (and this instruction) away from `--resume`/bare `--abandon`.

