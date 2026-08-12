# Workflow Closeout: `<work-id>`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

## Summary

`<short summary of completed workflow>`

## Local todo status

**Status:** `complete | partial | blocked`  
**Remaining items:** `<none or list>`

## Evidence captured

- `<evidence item>`

## Durable artifacts promoted

- `<artifact path and summary>`

## Triage candidates / recommendations

- `<path/title or none>`

## Episode capture

What this run observed is recorded as episodes at the Commander `feedback` step, written
through `scripts/apply_episode_delta.py` and proved by `scripts/verify_episode_captured.py`.
Confirm here only that the capture gate passed. An episode is a record of what happened; a
rule for a future agent to follow belongs in `docs/agents/*` and is a human's call.

## Reconciliation status

**Required:** `yes | no`  
**Status:** `complete | skipped | blocked`  
**Reason:** `<reason>`

## Archive action

**Status:** `complete | pending because <reason> | skipped because <reason>`  
**Archived to:** `.agent-work/archive/<date>-<work-id>/ or none`  
**Archive is authoritative:** `no`
