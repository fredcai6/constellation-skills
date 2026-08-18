# Candidate A — pure corpus-absence guard

Constraint: reuse the existing `INSTRUCTION_FILES` walk, assert absence of two literals, add no new concept.

**Scope expression** — the existing extractor, unmodified:

```python
scanned = _all_instruction_texts()   # (where, text) over INSTRUCTION_FILES:
                                     # md = whole file; json = every string leaf, by path
RETIRED_CLI_MARKERS = ("CLI fallback:", "<engine>")
```

**Assertions** (one test, `TestTheCLIDoorIsNotTaughtToAgents`):

```python
scanned = _all_instruction_texts()
assert len(INSTRUCTION_FILES) >= 60          # same floor the walk already pins
assert len(scanned) >= len(INSTRUCTION_FILES)  # every file yielded >=1 text
hits = [(where, m) for where, text in scanned
        for m in RETIRED_CLI_MARKERS if m in text]
assert hits == [], MSG
```

**Loop count**: stated by the two floors above and echoed in the message, so an empty or narrowed corpus fails instead of passing vacuously.

**Failure message**: `"<n> instruction texts across <k> files scanned; the retired CLI door is taught again at: <where>: '<marker>'. Agents drive the engine through the door tools (spine_status/spine_start/spine_advance/...). If a door genuinely cannot bind (it already holds a lease), say so in prose without the placeholder and without labelling it a fallback. Do not add an exception list — that is the failure mode this replaces."`

**Location**: `tests/test_mcp_adoption.py`, beside the walk it reuses. It cannot land until `TestTier1ImperativeFields::test_field_still_carries_cli_fallback` is deleted in the same commit — otherwise the suite asserts P and ¬P and is red by construction.

**Three ways it is wrong**

1. **It measures spelling.** `cli fallback —`, `CLI Fallback:`, `${ENGINE}`, or `python3 scripts/checklist_engine.py advance` all pass green. Both prior regrowths were reverts, so byte-identity held by luck; a Charter recompile or template regeneration emits its own phrasing and walks straight through.
2. **It displaces instead of excepting.** With no exception list, the 3 genuine door-refusal sites get reworded ("run the engine script directly") — still a second path, now invisible, and the green guard certifies it. Cheaper still: move the text to `docs/`, or to a `.txt`/`.yaml` under `skills/`. The suffix rule drops it silently — no exception list needed, no failure.
3. **It fires on legitimate history.** A retrospective, ADR, or `write-a-skill` doc quoting the retired clause inside `skills/` goes red, and the only in-constraint fixes are deleting the evidence or adding the forbidden list. `<engine>` also has no ownership check — an unrelated template's placeholder trips it.

**What this cannot catch.** It tests bytes, not doctrine. It cannot distinguish an agent taught the door is the only interface from one taught to shell out, so long as the shelling-out avoids two strings; and it exerts no pull the other way — a corpus that deleted every clause and never taught `spine_advance` passes clean. It cannot see whether the three real door-refusal cases lost their only working path (it reads that deletion as success), nor whether the "one door drives one spine" refusal still behaves as documented. And it is blind one directory over: the same doctrine in `docs/`, in `scripts/`, or in any non-`.md`/`.json` file is out of scope by the walk's own rule.
