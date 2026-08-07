# scripts.verify_agent_feedback
scripts/verify_agent_feedback.py, 251 lines, 3 holes

Verify the durable Constellation agent feedback log for a work id.

imports stdlib: __future__.annotations, argparse, json, pathlib.Path, re, sys
imports third-party: agent_work_root.durable_root
imported by: none found

```python
_BARE_NONE_RE = re.compile('^[-*]?\\s*`?none\\.?`?\\s*$', re.IGNORECASE)
_SIGNAL_SECTIONS = ('Friction / unclear', 'Crew-reported friction', 'Improvement signals')
```

- [FeedbackVerificationError](FeedbackVerificationError.md) class: Raised when the durable feedback-log invariant is broken.
- [_entry_block](_entry_block.md) function: Return the feedback entry block for work_id (its ## heading to the next ##).
- [_boilerplate_errors](_boilerplate_errors.md) function: Reject content-free entries: every signal bullet is a bare 'none'.
- [_current_run_archive_dirs](_current_run_archive_dirs.md) function: HOLE: no docstring
- [_durable_feedback_errors](_durable_feedback_errors.md) function: The durable-log positive check: the shared main-checkout AGENT_FEEDBACK.md.
- [_negative_errors](_negative_errors.md) function: The mode-independent negative checks: nothing durable leaked into the work
- [_staged_feedback_errors](_staged_feedback_errors.md) function: The fencing-aware positive check: a worktree-local staged trio + citation.
- [verify_agent_feedback](verify_agent_feedback.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
