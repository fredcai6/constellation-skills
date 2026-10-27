# Pi runtime implementation

`src/pi-runtime.ts` owns persistent Pi SDK sessions for Commander, Implementer, and Reviewer. It uses the pinned `@earendil-works/pi-coding-agent` 1.4.0 API directly, including `ModelRuntime`, `DefaultResourceLoader`, `SessionManager`, and `createAgentSession`.

Each request supplies the role prompt and workflow tools. Resource discovery is disabled for project context files, skills, prompts, themes, extensions, and MCP. Settings are in memory; model configuration and auth paths are isolated beneath the session directory. Pi resolves provider credentials from the environment. No credentials were examined or model requests made during implementation.

Commander gets read, ls, grep, find, and supplied workflow tools. Implementer also gets bash, edit, and write. Reviewer also gets bash to execute verification. These are normal role tool sets, not a security sandbox: bash can mutate files. Parent/controller callbacks own workflow-state checks and explicit override authorization.

Limits default to 12 turns, 120 seconds, and 1024 output tokens per provider response. The controller can choose smaller turn limits. Automatic retries, compaction, catalog network refresh, and cache warming are disabled. Timeout and turn exhaustion signal Pi's synchronous abort; cleanup waits for Pi's prompt to settle, preserving message persistence and known usage. Custom workflow callbacks must finish or implement their own cancellation: the minimal callback contract does not carry an AbortSignal. An uncooperative callback can delay timeout settlement. This limitation is explicit rather than hiding live work behind a Promise timeout.

`PiRuntimeError.partial` includes text, session file, and incremental known usage for failed runs. Usage input counts uncached input plus cache reads/writes; cost comes from Pi. An interrupted provider may report incomplete usage. The optional `onSessionAllocated` callback is awaited before prompting so the controller can persist the session pointer before any model request. Pi creates new JSONL files on its first persisted conversation message; an allocation pointer may precede the file. Session resume requires an existing file and rebinds the supplied role/tools/context; the controller owns session identity and role consistency.

Eight deterministic tests cover pre-request session pointer persistence, isolated resources, real JSONL persistence/resume, incremental usage, custom tools, role tool sets, turn/time ceilings, provider errors, invalid inputs, and real SDK initialization with no provider request. The SDK initialization test also verifies output-token capping and available Haiku model resolution offline.

Validation:

```sh
node --import tsx test/pi-runtime.test.ts
./node_modules/.bin/tsc --noEmit --target ES2022 --module NodeNext --moduleResolution NodeNext --skipLibCheck src/pi-runtime.ts test/pi-runtime.test.ts
```

The `tsx` CLI's IPC socket is blocked in this workspace sandbox; `node --import tsx` avoids that socket. All eight tests and typecheck pass. No live API smoke test was performed.
