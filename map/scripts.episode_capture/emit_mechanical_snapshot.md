# scripts.episode_capture:emit_mechanical_snapshot
function, scripts/episode_capture.py:458, 55 lines

```python
def emit_mechanical_snapshot(checklist: Mapping[str, Any], base_dir: Any = None) -> Path | None
```

Write the active step's mechanical group beside its manifest. Never raises.

**Overwrites, where the manifest is write-if-absent — and the asymmetry is the
point, not an inconsistency.** The manifest records what was DELIVERED to an
agent at one instant, and pinning it by revision is only honest if its bytes
cannot move. This record is a tally: `reopens`, `rework-count`, `failed-commands`
and `refusals` all change as the step is worked, so a frozen copy would not be a
preserved record, it would be a wrong number. Refreshing it costs nothing the
manifest's guarantee depends on, because the pin is over the MANIFEST's bytes,
not over this file's.

**Known scope, stated rather than papered over:** the seam fires on `start` and
`reopen`, so what lands is a STEP-ACTIVATION reading. At `start(x)` the step has
not run yet and its tallies are legitimately near zero; `reopen(x)` refreshes them
with the previous attempt's totals. A caller wanting live values calls
`mechanical_fields()` directly, which always reads current state. Covering the end
of a step would mean a seam on `advance` as well, which is a change to g1's
ratified placement and is not made here.

Records what it could NOT source, by name, in `refused` — the same rule as g1's
failure stub. An absent field and a field nobody tried to read are different
facts, and a reader has no other way to tell them apart.

Swallows every error, including its own write failure, and deliberately does NOT
let one escape into `emit_step_manifest`'s stub path: a broken snapshot would
otherwise be reported as a failed MANIFEST, which is a different component's
health and would send a reader hunting the wrong defect.

calls internal: _engine, mechanical_fields, snapshot_path
calls stdlib: builtins.open, datetime.datetime.now, json.dumps
reads internal: MECHANICAL_CONTRACT_VERSION, REQUIRED_MECHANICAL_FIELDS
reads stdlib: builtins.Exception, datetime.datetime, datetime.timezone, datetime.timezone.utc, json (module)
unresolved: 6 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
