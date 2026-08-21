## Wave review - #636 review block

**Exit: repair.** #500 is approved and locally integrated. The #636 lock/transaction change fixes the original two-writer lost update, but independent review found a narrower wrong-target case: if same-session Y exists and seeded X does not, the helper mutates Y instead of appending and mutating X. Wave 1 stays open. Resume the same #636 identity for the exact selection repair and fresh independent review; do not widen into #613. Mechanical #638 continues its already-launched review. Forecast work remains held.
