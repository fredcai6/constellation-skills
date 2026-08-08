"""g4 REVIEWER's own re-run of all 19 mutations.

Sanctioned route from the handoff: apply the edit DIRECTLY to
scripts/checklist_engine.py, run the NAMED test, revert with
`git checkout -- scripts/checklist_engine.py`, and confirm the tree is clean
BEFORE the next mutation. Anchors were authored here from the source, not copied
from the implementer's driver.

Line endings are preserved (the checkout is CRLF under .gitattributes' text=auto);
matching is done on an LF-normalized copy and the original ending is restored.
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(r"C:/Programs/constellation-skills-wt/epic418-a2-467")
SRC = ROOT / "scripts" / "checklist_engine.py"
TESTFILE = "tests/test_checklist_engine.py"

M = {}


def mut(n, named, old, new):
    M[n] = {"named": named, "old": old, "new": new}


mut("N1", "test_ledger_begin_refused_is_recorded_and_the_healthy_world_records_nothing",
    '    _append_trip_entry(cl, iid, verb, "begin-refused", reading, hard, wid)\n    raise EngineError(',
    '    raise EngineError(')
mut("N2", "test_ledger_begin_released_is_recorded_when_the_same_verb_runs_over_the_line",
    '        _append_trip_entry(cl, iid, verb, "begin-released", reading, hard, wid)\n        return\n',
    '        return\n')
mut("N3", "test_ledger_an_existing_ledger_is_extended_never_replaced",
    '    ledger = cl.setdefault("trip_ledger", [])',
    '    ledger = []\n    cl["trip_ledger"] = ledger')
mut("N4", "test_ledger_is_append_only_across_repeated_begins",
    '    tid = f"tl-{len(ledger) + 1}"', '    tid = "tl-1"')
mut("N5", "test_ledger_is_append_only_across_repeated_begins",
    '        "id": tid, "gate": gate, "verb": verb, "outcome": outcome,',
    '        "id": tid, "gate": gate, "verb": "start", "outcome": outcome,')
mut("N6", "test_ledger_records_the_per_gate_hard_line_not_a_global_constant",
    '    _, hard = _gauge_reader.thresholds_for(\n        reading.model, _gate_headroom_tokens(cl, iid))',
    '    _, hard = _gauge_reader.thresholds_for(\n        reading.model, 0)')
mut("N7", "test_ledger_entry_carries_every_field_including_the_live_why_ref",
    '        "model": reading.model, "why_ref": why_ref, "ts": _now(),',
    '        "model": reading.model, "why_ref": None, "ts": _now(),')
mut("N8", "test_ledger_a_none_reading_writes_no_entry_and_makes_no_compliance_claim",
    '        return _no_reading_advisory(base_dir)',
    '        _mut = _no_reading_advisory(base_dir)\n'
    '        _mr = begin_over_line_records(cl)\n'
    '        if _mr:\n'
    '            _mut += (f"\\nTRIP LEDGER: {len(_mr)} begin(s) at/over the hard line are "\n'
    '                     f"on the record under this understanding.")\n'
    '        return _mut')
mut("N9", "test_compliance_signal_reads_the_live_understanding_not_a_superseded_one",
    '        if e.get("why_ref") != live:\n            continue\n', '')
mut("N10", "test_compliance_signal_counts_both_begin_outcomes_and_nothing_else",
    '        if e.get("outcome") not in ("begin-refused", "begin-released"):\n            continue\n', '')
mut("N11", "test_compliance_signal_is_empty_in_the_healthy_world_and_names_the_begin_in_the_defective_one",
    '    rec = _latest_why_record(cl)\n    live = rec["id"] if rec else None\n    out: list[dict] = []',
    '    return []\n    rec = _latest_why_record(cl)\n    live = rec["id"] if rec else None\n    out: list[dict] = []')
mut("N12", "test_compliance_selector_is_pure_and_reads_stored_state_only",
    '        out.append(e)\n    return out',
    '        e["seen"] = True\n        out.append(e)\n    return out')
mut("N13", "test_compliance_line_also_rides_the_already_requested_hard_advisory",
    '                    f"work at another gate.") + ledger_note',
    '                    f"work at another gate.")')
mut("N14", "test_compliance_line_appears_on_the_hard_advisory_only_in_the_defective_world",
    '                f"{_refresh_attach_hint(gate, wid)}") + ledger_note',
    '                f"{_refresh_attach_hint(gate, wid)}")')
mut("N15", "test_compliance_line_names_the_count_and_the_latest_begin",
    '                f"\\nTRIP LEDGER: {len(records)} begin(s) at/over the hard line are on "',
    '                f"\\nTRIP LEDGER: 1 begin(s) at/over the hard line are on "')
mut("N16", "test_compliance_line_names_the_count_and_the_latest_begin",
    '            last = records[-1]', '            last = records[0]')
# N17 is implemented so the leaked note is genuinely COMPUTED in the soft branch.
# `ledger_note` is scoped inside the hard branch, so a bare `+ ledger_note` there
# would be a NameError -- a crash, not a behaviour change, and therefore weaker
# evidence than the mutation the log describes. This is the stronger form.
mut("N17", "test_compliance_line_never_appears_below_the_hard_band",
    '    if fill >= soft:\n'
    '        return (f"\\nCONTEXT {fill:.0%} (>= soft): you\'ve used most of your context. "',
    '    if fill >= soft:\n'
    '        _sr = begin_over_line_records(cl)\n'
    '        _sn = ("" if not _sr else\n'
    '               f"\\nTRIP LEDGER: {len(_sr)} begin(s) at/over the hard line are on "\n'
    '               f"the record under this understanding (latest: {_sr[-1].get(\'verb\') or \'?\'} "\n'
    '               f"{_sr[-1].get(\'gate\')} -> {_sr[-1].get(\'outcome\')}). Closing this gate does "\n'
    '               f"not clear the record.")\n'
    '        return _sn + (f"\\nCONTEXT {fill:.0%} (>= soft): you\'ve used most of your context. "')
mut("N18", "test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb",
    '    if v == "start":\n        return start(cl, args.id, base_dir=base_dir)',
    '    if v == "start":\n        _trip_hard_gate(cl, args.id, base_dir, verb="start")\n'
    '        return start(cl, args.id, base_dir=base_dir)')
mut("N19", "test_ledger_is_append_only_across_repeated_begins",
    '            _trip_hard_gate(cl, getattr(args, "id", None), base_dir, verb=v)',
    '            _trip_hard_gate(cl, getattr(args, "id", None), base_dir)')


def read():
    raw = SRC.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    return raw.replace("\r\n", "\n"), crlf


def write(text, crlf):
    SRC.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def git(*a):
    return subprocess.run(["git", *a], cwd=str(ROOT), capture_output=True, text=True)


def clean():
    return git("diff", "--quiet", "--", "scripts/checklist_engine.py").returncode == 0


assert clean(), "tree not clean before the battery"
print(f"pre-battery: scripts/checklist_engine.py clean = {clean()}")

results = {}
only = sys.argv[1:] or list(M)
for name in only:
    spec = M[name]
    text, crlf = read()
    hits = text.count(spec["old"])
    assert hits == 1, f"{name}: anchor matched {hits} times, expected exactly 1"
    mutated = text.replace(spec["old"], spec["new"], 1)
    assert mutated != text, f"{name}: replacement did not change the file"
    write(mutated, crlf)
    assert not clean(), f"{name}: file did not actually change on disk"

    p = subprocess.run([sys.executable, "-m", "pytest", "-q", TESTFILE],
                       cwd=str(ROOT), capture_output=True, text=True,
                       env={**__import__("os").environ, "NO_COLOR": "1", "FORCE_COLOR": ""})
    out = p.stdout + p.stderr
    failed_names = set()
    for line in out.splitlines():
        m = re.match(r"^(FAILED|SUBFAILED)\s+\S+::(?:\S+::)?([A-Za-z0-9_]+)", line.strip())
        if m:
            failed_names.add(m.group(2))
        m2 = re.match(r"^(?:FAILED|SUBFAILED)\s+(\S+)", line.strip())
        if m2 and "::" in m2.group(1):
            failed_names.add(m2.group(1).split("::")[-1].split(" ")[0])
    summary = [l for l in out.splitlines() if re.search(r"\d+ (passed|failed)", l)]
    total = 0
    mt = re.search(r"(\d+) failed", out)
    if mt:
        total = int(mt.group(1))
    # a mutation that makes the module unimportable is a crash, not a kill
    crashed = "ERROR" in out and "error" in (summary[-1].lower() if summary else "")

    git("checkout", "--", "scripts/checklist_engine.py")
    reverted = clean()
    killed = spec["named"] in failed_names

    results[name] = {"named": spec["named"], "named_test_red": killed,
                     "total_failed": total, "reverted_clean": reverted,
                     "summary": summary[-1] if summary else "", "crashed": crashed}
    print(f"{name:>4}  named_red={str(killed):<5} total_failed={total:<3} "
          f"reverted_clean={reverted}  | {summary[-1] if summary else ''}")
    assert reverted, f"{name}: TREE NOT CLEAN AFTER REVERT -- aborting"

(ROOT / ".agent-work/issue-467-trip-semantics/g4-review/mutation-rerun.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8")

survived = [k for k, v in results.items() if not v["named_test_red"]]
print(f"\nran {len(results)} mutations; SURVIVORS (named test stayed green): "
      f"{survived or 'none'}")
print(f"final tree clean: {clean()}")
