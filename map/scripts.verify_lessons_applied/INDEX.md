# scripts.verify_lessons_applied
scripts/verify_lessons_applied.py, 49 lines, 1 holes

Feedback-step gate: refuse advance while any threshold-ripe lesson is unpaid.

A lesson is unpaid when its scope threshold is crossed and it has no terminal
disposition this cycle (neither applied/exported nor deferred at/above its current
count). Reuses the ripeness model from apply_lessons_delta. Exit 0 = clear, 1 = blocked.

imports stdlib: __future__.annotations, argparse, pathlib.Path, sys
imports third-party: agent_work_root.durable_root, apply_lessons_delta.LessonsDeltaError, apply_lessons_delta.load_playbook, apply_lessons_delta.ripe_lessons
imported by: none found

- [main](main.md) function: HOLE: no docstring
