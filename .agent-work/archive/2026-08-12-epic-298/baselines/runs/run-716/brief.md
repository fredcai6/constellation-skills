You are picking up issue #716 in this repository (fredcai6/f1Brainz).

--- ISSUE #716: constellation: work_id-with-slash parsing breaks run_crew.py + verify_agent_feedback.py (nested Commander-under-Admiral) ---
From #659 lessons audit (constellation shared-machinery bug, hit TWICE independently in one run — epic-659/665). Two constellation-commander scripts assume a work_id has no internal '/', which breaks this repo's nested Commander-under-Admiral convention (`epic-<N>/<issue>`):
- `run_crew.py --verify-result`'s `load_registry_for_resume` parses `session.split('/')[1]` — drops everything after the first slash.
- `verify_agent_feedback.py`'s `_current_run_archive_dirs` matches `path.name == work_id` — unsatisfiable when work_id contains '/'.
Both forced a waive/workaround in epic-659. Fix: a single shared work_id-safe parsing/matching helper both scripts import. NOTE: these scripts live in the constellation-skills install, not this repo — route to wherever constellation-commander's scripts are maintained. Also exported to the constellation upstream queue in the audit delta.
--- END ISSUE ---

This is a PLANNING engagement only. Implementation is a separate, later engagement and
is out of scope for you: do not modify, commit, push, or open a pull request, and do not
comment on the issue.

Understand the problem, then produce a plan. Your plan must name the specific files you
would change and explain why each one. Finish by stating your file list plainly under a
final heading `FILES I WOULD CHANGE`, one path per line.
