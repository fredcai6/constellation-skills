# evals.euler-1-multiples.checks.spine_completed
evals/euler-1-multiples/checks/spine_completed.py, 350 lines, 2 holes

PROCESS check (gating): a constellation ENGINE spine reached a terminal state

WITH engine-written provenance -- not merely agent-written JSON (issue #127).

The old check trusted plain JSON state: a spine whose tasks were all marked
``complete`` passed, no matter WHO wrote that state. A cheap headless model that
never invoked the engine could HAND-WRITE a spine.json with every step
``complete`` and fabricated evidence notes and sail through -- fabrication was one
forgotten field from passing (epic-101 live-acceptance attempt 6). This check now
demands the fingerprints the engine ALWAYS leaves and a template-copying
fabricator does NOT get for free:

  1. Terminal gated shape: a ``tasks`` map with EVERY task ``complete``. The bare
     ``{"status": "done"}`` form no longer passes on its own -- it carries zero
     provenance and is exactly the cheapest thing a fabricator writes. (The
     runner's ``--dry-run`` now synthesizes a real engine-shaped spine, so its
     self-smoke still bites strictly.)
  2. A plausible ``engine_session`` lease block. The shipped spine TEMPLATE has no
     ``engine_session`` key at all -- only the engine's ``claim`` verb writes one,
     with all of session_id / status / claimed_at / last_heartbeat / claimed_by /
     worktree / previous_session_id / takeover_reason. The claim/heartbeat/release
     timestamps must parse as ISO-8601 and be MONOTONIC (claimed <= heartbeat <=
     released). A fabricator must now forge a whole lease with a monotonic lifecycle,
     not just flip statuses.
  3. Engine evidence grammar. Every evidence id matches the engine's
     ``e-<task>-<n>`` form and is ``produced_by`` engine or human; at least one
     engine-produced ``command-output`` exists (the engine runs command checks);
     and every SATISFIED command / git-change-policy condition is backed by the
     matching engine-produced evidence (or, when waived, a human ``waiver``) its
     ``satisfied_by`` names.

  4. Journal cross-verification (issue #131). When the engine's append-only
     journal sidecar (``<spine>.journal``) is present, it is cross-verified against
     the final spine: the hash-chain is intact, seq is 1..N, timestamps are
     monotonic and fall within the lease window, every ``complete`` task carries an
     ``advance``/``record`` journal entry, and every satisfied engine-checked
     condition's backing evidence id appears in the journal. A fabricator must now
     also forge a self-consistent, hash-chained journal whose every line commits to
     the whole chain before it. GRANDFATHER POLICY: a spine with NO journal (e.g.
     the honest reference workspaces preserved before the journal shipped, or any
     pre-journal engine install) still passes on the lease+grammar checks above --
     the journal STRENGTHENS provenance where present but is never REQUIRED, so the
     check stays backward compatible with journal-absent-but-lease-valid spines.

This is NOT tamper-proof -- the agent owns the filesystem and could forge all of
the above. The bar (issues #127/#131) is deliberately lower: raise fabrication cost
ABOVE just-doing-the-work cost. Forging a monotonic lease plus grammar-correct,
cross-consistent evidence AND a self-consistent hash-chained journal for ten gates
is more work than running the engine, which is the point.

Spine locations searched (run-dir contract, per scripts/run_skill_eval.py::_run_once):

  <run-dir>/spine.json                              contract-level spine
  <run-dir>/workspace/**/.agent-work/**/spine.json  a live engine run's spine

The corpus copy under ``workspace/.claude/`` is excluded so a bundled
``*_SPINE.template.json`` can never satisfy the check.

Usage: ``python spine_completed.py <run-dir>``  ->  exit 0 pass / non-zero fail,
one evidence line on stdout.

imports stdlib: __future__.annotations, datetime.datetime, datetime.timezone, hashlib, json, pathlib.Path, re, sys
imported by: none found

```python
JOURNAL_HASH_FIELDS = ('seq', 'ts', 'session_id', 'verb', 'task', 'evidence_ids', 'prev_hash')
EVIDENCE_ID_RE = re.compile('^e-[a-z0-9][a-z0-9-]*-\\d+$')
SESSION_FIELDS = ('session_id', 'status', 'claimed_at', 'last_heartbeat', 'claimed_by', 'worktree', 'pre...
ENGINE_CHECK_KINDS = ('command', 'git-change-policy')
```

- [_parse_iso](_parse_iso.md) function: Parse an ISO-8601 timestamp (tolerating a trailing 'Z'), or None. Naive
- [all_tasks_complete](all_tasks_complete.md) function: True iff the engine's gated form has a non-empty ``tasks`` map with EVERY
- [engine_session_plausible](engine_session_plausible.md) function: Whether the spine carries an engine-written ``engine_session`` lease with a
- [evidence_grammar_ok](evidence_grammar_ok.md) function: Whether the spine's evidence matches engine grammar and cross-verifies the
- [spine_has_engine_provenance](spine_has_engine_provenance.md) function: Composite gate: terminal gated shape AND engine_session plausibility AND
- [_journal_hash](_journal_hash.md) function: Re-derive an entry's hash exactly as checklist_engine._journal_hash does:
- [journal_consistent](journal_consistent.md) function: Cross-verify the engine journal sidecar against the final spine (issue #131).
- [find_spines](find_spines.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
