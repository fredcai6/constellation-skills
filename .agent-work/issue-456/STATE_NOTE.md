# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch.

- **step**: `execute` (in-progress) · **slug**: **`gs` — the LAST gate, implement in flight**
- **PID**: crew `constellation/issue-456/gs/implementer/attempt-1` running. All others closed.
- **expected artifact**: `.agent-work/issue-456/crew-handoffs/gs-implement-RESULT.md`
- **handoff**: `.agent-work/issue-456/crew-handoffs/gs-implement.md`

## 🟢 RESUME HERE — 10 of 11 gates CLOSED. `gs` is the last one.

`g8` closed clean: implement, review (APPROVE on the 4th pass from the same
reviewer that BLOCKed three times), and integrate all advanced. Suite **1838
passed / 2 skipped / 701 subtests / 0 failed**, selector `bom or docstring`
**11 passed / 4 subtests**, build+check **7/7 exit 0**.

**The landing-zone question is MEASURED and it came back negative for the plan's
assumption.** See `.agent-work/issue-456/landing-zone-measurement.md`. The
116-file landing zone is NOT stable — one reworded docstring rewrites its module
`INDEX.md`. The **2-file** zone (`map/INDEX.md` + `map/ids.jsonl`) IS stable, and
the negative control fires on it. So `gs` ships **two tracked files**, not 3,975,
with the body pages gitignored and locally regenerated. This retires critic F9
outright. **Flagged to Tommy — it narrows what ships, and he can reverse it
before the PR.**

`gs` must also WRITE the `map_tree_freshness` test. It does not exist; the gate's
own closing selector collects **zero** today and would exit 5.

**Owed after the crew returns:** `attach` implementer-result → attest `c1` →
`advance`; then `gs-review`; then `gs-integrate` (`c1` is command-kind, re-run by
`advance`; `c2` needs verdict APPROVE).

**Then, and only then:** `reconcile` → `triage` (drain **tc1–tc19**) → `review` →
`feedback` → `archive`. **Release the lease LAST.**

**Push and open a FULL non-draft PR. Do NOT merge — merge is not approved.**

Rule this run cost five passes to learn: **branch on the SHAPE (fixed, known when
the case is written), never on the MEASURED output (the thing under test).**
