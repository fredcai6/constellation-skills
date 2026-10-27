# GPU status issue 1 validation — 2026-10-22

The first implementation provides `./gpu status`, `./gpu status --json`, and
`--budget SECONDS`, using the Python standard library and read-only Linux files.
No workload, container, driver, scheduler, or GPU configuration changes were made.

## Evidence

- All 60 fixture tests pass with the known-working Python 3.12 executable recorded
  in the agent guide. All 60 also pass under Python 3.14 from a temporary copy of
  the package and tests outside this checkout. No dependency install was needed.
- The configured build backend, `setuptools.build_meta`, imports successfully.
  A wheel installation was not exercised.
- A mocked fdinfo-directory PermissionError regression failed before the final
  correction and passes afterward. Permission-denied directories now contribute
  an aggregated partial-process-visibility note.
- A supplemental mocked disappearance between fdinfo enumeration and open produces
  a visible disappearance note. CLI budgets nan, inf, -inf, zero and negative all
  return status 2 without collection.
- A final live JSON observation found two AMD PCI devices (0000:03:00.0 and
  0000:7c:00.0). Both reported permission gaps. The observation only read existing
  sysfs and proc files. Process counts depend on the caller's permissions and the
  observation time; they are not a complete workload inventory.
- Approved scope, agent guidance, and provider authorization were unchanged.

## Process limits and lessons

Pi owns separate persisted Commander, Implementer, and Reviewer sessions. The
first independent review blocked silent fdinfo permission gaps and invalid budget
handling. The implementer's repair summary then claimed several changes absent
from disk. The coordinator checked the files, reproduced the missing permission
note with a failing regression, and corrected the remaining permission, packaging,
and test-path issues directly before requesting a fresh independent review.

The pilot also exposed runtime rough edges: response truncation, overly small
turn budgets, missing crew steering, and losing submitted BLOCK results when an
invocation subsequently failed. Constellation Pi now exposes persistent response
and resume budgets, bounded crew handoffs, truncation stop behavior, and retention
of submitted BLOCK findings. The existing Constellation engine was not modified.

Collection remains cooperative; an individual kernel read can block. VRAM reads
are not atomic. Unknown/invalid values remain null with notes, and process
visibility gaps never establish that a GPU is idle or available for new work.

## Independent review

The separate Pi Reviewer returned APPROVE after independently running all 60 tests,
reading the final files, checking the prior BLOCK findings, rejecting invalid CLI
budgets including nan, and performing read-only live text/JSON observations. The
coordinator's direct fixes were therefore reviewed by a different session. The
persisted session/result evidence remains local in `.constellation-pi/`, excluded
from Git. Human final acceptance remains pending; no human approval was fabricated.
