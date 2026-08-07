# scripts.context_manifest:rev
function, scripts/context_manifest.py:132, 37 lines

```python
def rev(data: bytes) -> str
```

Git blob OID of `data` after LF normalisation.

Equal to `git hash-object <path>` and `git rev-parse HEAD:<path>` for a tracked
clean file under this repo's `.gitattributes` (`* text=auto`) with
`core.autocrlf=true` — but only for content git actually normalises, and that
takes **two** conditions, not one:

1. **No attribute exemption.** A `-text` or `binary` attribute in
   `.gitattributes` makes git stop normalising that path.
2. **No content-triggered refusal.** Under `text=auto` git also declines on the
   bytes alone, with no `.gitattributes` entry involved anywhere: a NUL byte
   (git auto-detects binary) or a lone CR (a carriage return not followed by a
   line feed, where normalising would not round-trip). For such content git
   stores the raw bytes, while this function normalises unconditionally — so it
   deliberately diverges there.

Both halves are watched mechanically, by two different kinds of check, because
they are two different kinds of fact.

Condition 1 is repository **configuration**: this repository's `.gitattributes`
is `* text=auto` and assigns `-text`/`binary` to nothing, so no path is exempt.
`RevIsGitBlobOid.test_gitattributes_exempts_no_path_from_lf_normalisation`
asserts that, and it fails the moment any exemption is added — including one
scoped to a subtree a `context_refs` declares, which is the shape that would
otherwise slip past a reader's eye.

Condition 2 is **content**, so no configuration check can see it at all. It is
pinned instead by
`RevIsGitBlobOid.test_rev_diverges_from_git_for_content_git_refuses_to_normalise`,
which asserts the divergence rather than assuming it away. No file in any root a
`context_refs` can name is in that class today — this corpus is markdown and
JSON written under `* text=auto` — but the boundary is watched rather than
stated more narrowly than it is.

calls stdlib: builtins.len, hashlib.sha1
reads stdlib: hashlib (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
