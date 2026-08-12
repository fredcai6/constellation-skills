# f3 probe handoff

This is a throwaway empirical probe, not a real implementer task. Do exactly this and nothing else:

1. Call the `SendMessage` tool with `to` set to the value of the `SPINE_PARENT` environment
   variable (read it from your environment) and `message` set to exactly:
   `f3-probe token=e1fu-f3-9c2a1d reached the parent`
2. Whatever happens — the tool succeeds, errors, or does not exist — write the outcome to
   `.agent-work/epic-559/e1-fail-up/f3-probe/RESULT.md` with this exact shape:

```
# f3 probe result

SPINE_PARENT seen: <the env var value you read>
SendMessage attempted: yes
Outcome: <one of: delivered / tool-error / tool-not-found / other>
Raw detail: <the exact tool result, error message, or exception text you observed, verbatim>
```

Do not attempt anything else — no code changes, no other tool calls beyond what is needed to
read the env var, call SendMessage once, and write the result file. The run is only complete
when the result artifact this handoff names exists.
