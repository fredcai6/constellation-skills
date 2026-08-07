# scripts.run_crew:CrewBackend.verify
method, scripts/run_crew.py:465, 29 lines

```python
def verify(self, entries: list[dict], session: str, *, root: Path) -> tuple[bool, dict]
```

Uniform across backends: exists-AND-fresh against the entry's

`started_at`; finalize to `completed` on fresh, else leave `running`.

Returns (fresh, entry). Reuses the canonical `result_fresh` — no
duplicated freshness logic. Freshness is judged against the entry's
`started_at` (its dispatch time), so a stale leftover result from a prior
attempt at the same path does NOT clear the hold. Both `result_present`
(existence) and `result_fresh` are recorded so the CLI can tell the two
failure modes apart (MISSING vs STALE). Only a fresh result finalizes to
`completed`; otherwise the entry is left `running` so the duplicate-guard
keeps holding. Refuses if the named crew is unknown or abandoned.

calls internal: CrewLaunchError x2, _now, find_entry, is_abandoned, registry_path, result_exists, result_fresh, save_registry

referenced by: none found
