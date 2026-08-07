# scripts.check_corpus_freshness
scripts/check_corpus_freshness.py, 189 lines, 7 holes

Report whether an installed constellation corpus is current with upstream main.

Reads the CORPUS.json provenance marker the installer stamps into a skills root
(source_commit) and compares it to the HEAD of constellation's main branch on
GitHub. Needs NO local constellation clone: it fetches the remote head with
`gh api` and falls back to a plain HTTPS call to the GitHub REST API, so it runs
inside a cloud session on any consuming repo that carries a project-scope install.

Where check_skill_freshness.py answers "did my customized templates drift from
their baseline?", this answers the coarser, clone-free question "is this whole
corpus behind upstream, and by how much?".

Exit codes:
  0  current      — installed source_commit == upstream main HEAD
  1  behind        — upstream has commits the install does not (count + subjects)
  2  cannot-determine — no/invalid marker, unknown commit, or the remote is
                        unreachable; never a false "current".

imports stdlib: __future__.annotations, argparse, json, pathlib.Path, subprocess, sys, urllib.error, urllib.request
imported by: none found

```python
DEFAULT_REPO = 'fredcai6/constellation-skills'
DEFAULT_BRANCH = 'main'
CORPUS_MARKER = 'CORPUS.json'
```

- [_utf8_stdio](_utf8_stdio.md) function: Mirror check_skill_freshness: don't make every call site set PYTHONIOENCODING.
- [FreshnessError](FreshnessError.md) class: HOLE: no docstring
- [GitHubRemote](GitHubRemote.md) class: Fetches upstream facts from the GitHub REST API. Tries `gh api` first
  - [GitHubRemote.__init__](GitHubRemote.__init__.md) method: HOLE: no docstring
  - [GitHubRemote._get](GitHubRemote._get.md) method: HOLE: no docstring
  - [GitHubRemote.head_commit](GitHubRemote.head_commit.md) method: HOLE: no docstring
  - [GitHubRemote.compare](GitHubRemote.compare.md) method: GitHub compare of base...head. `ahead_by` is how many commits `head`
- [read_marker](read_marker.md) function: HOLE: no docstring
- [_subject](_subject.md) function: HOLE: no docstring
- [evaluate](evaluate.md) function: Return (exit_code, human report). Raises FreshnessError only for the
- [main](main.md) function: HOLE: no docstring
