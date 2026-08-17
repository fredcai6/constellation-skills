# Triage candidate: the door's `main()` catches only `KeyError`, so any other raise kills it

- **Disposition:** `recommend-and-defer`. Not filed (`decision:no-issue-filing`). The one
  **instance** lane A hit is fixed in-lane; the general shape is not, deliberately.
- **Raised by:** the `g2` reviewer, generalising from a blocking finding it made against this
  lane's own new code. Relayed by `cmdr-567-a`.
- **Severity:** medium-high. It is a denial-of-service on the whole tool surface, and it turns
  any ordinary programming error into a dead server rather than a refusal.

## The instance that exposed it

`spine_bind` was given a `spine_file` containing a **NUL byte**. Path resolution raised
`ValueError`. `main()`'s dispatch catches only `KeyError`:

```python
elif nm in LIFECYCLE_TOOL_NAMES:
    try:
        result = call_lifecycle_tool(nm, call_args)
    except KeyError as exc:
        result = _tool_error(f"tool error: missing or unknown {exc}")
```

So the `ValueError` unwound the whole process and **the server died with exit 1** — on the
one tool reachable while nothing is bound. Lane A fixes that call site by catching
`ValueError` and refusing through `_tool_error`.

## Why the general shape deserves its own change

The instance is one argument on one tool. The shape is: **every unhandled exception anywhere
under a lifecycle dispatch kills the door.** That is a poor trade for this component, for
three reasons specific to it:

1. **The blast radius is the whole session, not the call.** A dead MCP server does not return
   an error the model can read and recover from — the client sees the transport close. This
   repo already learned that lesson once: `_spine_from_env`'s docstring records that an
   unset `SPINE_FILE` used to raise `KeyError` *at import*, so "the server died before it
   could refuse anything and the client saw only `Connection closed`." Issue #603 fixed
   exactly this failure at startup and left it live at dispatch.
2. **It converts every future programming error into an outage.** A `TypeError` from a bad
   argument shape, an `OSError` from a vanished directory, a `RecursionError` — each becomes
   a dead door instead of a refusal a caller can act on. The module's whole design posture is
   "fail visibly rather than emit plausible wrong output"; dying is not failing visibly, it
   is failing *silently at the transport*.
3. **Refusal machinery already exists and is well built.** `_tool_error` takes a `tool` and a
   `rejection_class` and lands every refusal in the rejection log. There is a ready-made
   fail-closed path; the dispatch simply does not route unexpected exceptions into it.

## Recommendation

Wrap both dispatch arms in a broad handler that returns through `_tool_error` rather than
propagating:

```python
try:
    result = call_lifecycle_tool(nm, call_args)   # and call_tool(nm, call_args)
except KeyError as exc:
    result = _tool_error(f"tool error: missing or unknown {exc}", tool=nm,
                         rejection_class="unknown-argument")
except Exception as exc:  # noqa: BLE001 -- a dead door cannot refuse anything
    result = _tool_error(f"tool error: {type(exc).__name__}: {exc}", tool=nm,
                         rejection_class="unhandled-exception")
```

**The `noqa` comment is the point of the change, not an apology for it.** A blanket
`except Exception` is normally a smell; here the alternative is a process that cannot answer
at all, which is strictly worse for a long-lived server whose client has no other channel.
Worth stating in the docstring so a future reader does not "tidy" it away.

Two things to pin alongside it, or the fix rots:

- **A test per dispatch arm** that plants a raising tool implementation and asserts the door
  returns a refusal **and stays alive**. Without the liveness half the test passes on a dead
  process that happened to write something first.
- **A `rejection_class` distinct from the deliberate refusals**, so an unhandled exception is
  visibly a *bug* in the rejection log rather than blending into ordinary policy refusals.
  An unhandled-exception refusal is a defect to fix, not a boundary working.

## Scope note

Lane A deliberately did **not** take this on. Its fence is
`scripts/mcp_spine_server.py`, so the change is technically in-scope by file — but it
alters the failure semantics of **all twelve tools**, which is a structural change beyond the
converged design and therefore a float, not a fix-now. The lane fixed its own instance and
reported the shape, which is the boundary the launch order draws.
