# Incidents

- 2026-08-14 — the sandbox helper behind the normal `tools.apply_patch` call
  failed with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`.
  The Commander paused mutation, reported it to the Admiral, then resumed with
  the approved direct `apply_patch` TTY workaround. No shell or Python rewrite
  path was used.
