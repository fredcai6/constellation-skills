# Triage candidate: the test proving a platform fallback could not run on that platform

- **Disposition:** the instance is **fixed in lane A**; the pattern is
  `recommend-and-defer`. Not filed (`decision:no-issue-filing`).
- **Raised by:** the Admiral, from lane A's own CI failure. Recorded by `cmdr-567-a`
  because it is an unusually clean specimen of a defect class this epic cares about.
- **Severity:** low individually, high as a pattern — it is the "check that cannot fail"
  family, in the form where the check cannot **run**.

## The specimen

Lane A fixed a real defect: `save()` called `os.fchmod`, which is **Unix-only**, unguarded —
so on `windows-latest` every save of an existing file raised `AttributeError`, and every
mutating engine verb ends in `save()`. A dead engine, not a red test.

The test written to prove the fallback works simulated the Windows shape by patching the
attribute away:

```python
with mock.patch.object(E.os, "fchmod", side_effect=AttributeError("no fchmod")):
    E.save(self.path, SAMPLE)
```

On Windows CI it errored:

```
AttributeError: <module 'os' (frozen)> does not have the attribute 'fchmod'
```

`mock.patch.object` **requires the attribute to exist** in order to replace it. On Windows
`os.fchmod` genuinely does not exist — which is the entire condition the test exists to
cover. So **the one test proving the fallback works was the one test that could not run on
the one platform that needs the fallback.**

Fix: `create=True` (or `raising=False` in the pytest idiom), so the patch installs the
attribute when it is missing and the fallback is exercised on both platforms.

## Why the pattern is worth recording, not just the instance

The usual "check that cannot fail" passes vacuously. This one **errors**, which sounds
safer — an error is visible. But it is visible only where the code path is *not* needed:

- On POSIX, the test runs and passes, and proves the fallback works where it is never used.
- On Windows, the test errors, and proves nothing where it is always used.

So the platform on which the guard matters is the platform on which its proof is absent, and
the CI signal for that absence looks like an unrelated test error rather than a coverage gap.
An author reading "1 error on Windows, passes on Linux" reasonably files it as a test-harness
problem — which is what it looks like, and which is why it hides.

**The general shape:** *a test that simulates a platform's absence of a feature by removing
that feature cannot run on the platform that already lacks it.* Same for a test that
simulates a missing binary by unsetting `PATH`, or a missing env var by deleting it, where the
target platform never had it.

## Recommendation

Two things, both cheap:

1. **A convention for platform-fallback tests:** simulate absence with `create=True` /
   `raising=False`, never with a plain patch. Then the same test exercises the fallback where
   the feature exists and where it does not, and the coverage is symmetric.
2. **When a platform-specific guard ships, ask which platform its test runs on.** For a
   guard whose whole purpose is "platform X lacks this", the proof must run on X. If CI only
   runs X, a test that errors on X is a *coverage* failure wearing a test-error costume.

Not proposed: making this a lint. The condition is a judgement about intent (is this patch
simulating an absence?) and a linter cannot see that. It belongs in the handoff template's
evidence section, if anywhere.

## Related

- `subtest-hides-a-raising-test-body.md` — the reporting-layer version: `PASSED` on the
  summary line with the failure on a separate `SUBFAILED` line.
- `map-ids-jsonl-empty-repo-wide.md` — a suite green against an empty map because it only
  ever compared the artifact to a regeneration of itself.

All three are the same question asked three ways: **does this green mean what its reader
thinks it means?**
