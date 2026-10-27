import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test, { type TestContext } from 'node:test';
import { createAgentSession, ModelRuntime, type AgentSession, type CreateAgentSessionOptions } from '@earendil-works/pi-coding-agent';
import { PiRuntime, PiRuntimeError, type RuntimePrompt } from '../src/pi-runtime.js';

type Message = AgentSession['messages'][number];
type Listener = Parameters<AgentSession['subscribe']>[0];
type Event = Parameters<Listener>[0];
const assistant = (text: string, stopReason = 'stop', toolCall = false): Message => ({
  role: 'assistant', content: toolCall ? [{ type: 'toolCall', id: 'call-1', name: 'test', arguments: {} }] : [{ type: 'text', text }],
  api: 'anthropic-messages', provider: 'anthropic', model: 'test', timestamp: Date.now(),
  stopReason, errorMessage: stopReason === 'error' ? 'mock provider failed' : undefined,
  usage: { input: 2, output: 1, cacheRead: 1, cacheWrite: 0, totalTokens: 4,
    cost: { input: 0.001, output: 0.001, cacheRead: 0, cacheWrite: 0, total: 0.002 } },
} as Message);

async function fixture(t: TestContext, behavior = 'success') {
  const dir = await mkdtemp(join(tmpdir(), 'constellation-pi-runtime-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const captures: CreateAgentSessionOptions[] = [];
  let aborted = 0;
  let disposed = 0;
  let modelCreations = 0;
  let promptsStarted = 0;
  const runtime = new PiRuntime({
    createModelRuntime: (async (options) => {
      modelCreations++;
      assert.equal(options?.allowModelNetwork, false);
      assert.equal(options?.refreshOnCreate, false);
      assert.equal(options?.modelsPath, null);
      return { getModel: (provider: string, id: string) => ({ provider, id }) } as unknown as ModelRuntime;
    }),
    async createSession(options) {
      captures.push(options);
      const manager = options.sessionManager!;
      const messages: Message[] = [...manager.buildSessionContext().messages];
      let listener: Listener = () => {};
      let releaseAbort: (() => void) | undefined;
      const emit = (event: unknown) => listener(event as Event);
      const add = (message: Message) => {
        messages.push(message);
        manager.appendMessage(message as Parameters<typeof manager.appendMessage>[0]);
      };
      return { session: {
        messages,
        agent: {
          abort() { aborted++; releaseAbort?.(); },
          streamFunction() { throw new Error('Mock never contacts a model'); },
        },
        subscribe(callback) { listener = callback; return () => { listener = () => {}; }; },
        dispose() { disposed++; },
        getSessionStats() {
          const n = messages.filter((m) => m.role === 'assistant').length;
          return { sessionFile: manager.getSessionFile(), sessionId: manager.getSessionId(),
            tokens: { input: n * 2, output: n, cacheRead: n, cacheWrite: 0, total: n * 4 }, cost: n * 0.002,
            userMessages: 0, assistantMessages: n, toolCalls: 0, toolResults: 0, totalMessages: messages.length };
        },
        async prompt(text) {
          promptsStarted++;
          add({ role: 'user', content: text, timestamp: Date.now() });
          await emit({ type: 'turn_start' });
          if (behavior === 'timeout') {
            await new Promise<void>((done) => { releaseAbort = done; });
            add(assistant('partial', 'aborted'));
            return;
          }
          const message = assistant('done', behavior === 'error' ? 'error' : behavior === 'length' ? 'length' : 'stop', behavior === 'turn-limit' || behavior === 'length');
          add(message);
          await emit({ type: 'turn_end', message, toolResults: [] });
        },
      } };
    },
  });
  const input: RuntimePrompt = { role: 'commander', cwd: dir, sessionDir: join(dir, 'sessions'),
    model: 'anthropic/test', systemPrompt: 'Only the Commander instructions.', prompt: 'Do the task.', tools: [] };
  return { runtime, input, captures, dir, started: () => promptsStarted,
    counts: () => ({ aborted, disposed, modelCreations }) };
}

test('awaits session pointer persistence before prompting and stops on persistence failure', async (t) => {
  const f = await fixture(t);
  let allocated: string | undefined;
  const result = await f.runtime.prompt({ ...f.input, async onSessionAllocated(file) {
    assert.equal(f.started(), 0);
    await Promise.resolve();
    allocated = file;
  } });
  assert.equal(result.sessionFile, allocated);
  assert.equal(f.started(), 1);
  await assert.rejects(f.runtime.prompt({ ...f.input, async onSessionAllocated() {
    await Promise.resolve();
    throw new Error('State save failed');
  } }), (error) => {
    assert.ok(error instanceof PiRuntimeError);
    assert.match(error.message, /State save failed/);
    assert.equal(error.partial.usage.cost, 0);
    return true;
  });
  assert.equal(f.started(), 1);
  assert.equal(f.counts().disposed, 2);
});

test('owns isolated Pi context, persists JSONL, and resumes with incremental usage', async (t) => {
  const f = await fixture(t);
  await writeFile(join(f.dir, 'AGENTS.md'), 'Foreign harness instructions must not load.');
  let received: unknown;
  f.input.tools = [{ name: 'workflow_next', description: 'Proceed', parameters: { type: 'object', properties: {} },
    async execute(args) { received = args; return { state: 'ready' }; } }];
  const result = await f.runtime.prompt(f.input);
  assert.equal(result.text, 'done');
  assert.deepEqual(result.usage, { input: 3, output: 1, cost: 0.002 });
  assert.match(await readFile(result.sessionFile, 'utf8'), /"type":"session"/);
  const options = f.captures[0];
  assert.deepEqual(options.tools, ['read', 'ls', 'grep', 'find', 'workflow_next']);
  assert.equal(options.thinkingLevel, 'off');
  const loader = options.resourceLoader!;
  assert.equal(loader.getSystemPrompt(), f.input.systemPrompt);
  assert.deepEqual(loader.getAgentsFiles().agentsFiles, []);
  assert.deepEqual(loader.getAppendSystemPrompt(), []);
  assert.deepEqual(loader.getSkills().skills, []);
  assert.deepEqual(loader.getExtensions().extensions, []);
  const response = await options.customTools![0].execute('call', {}, undefined, undefined, {} as never);
  assert.deepEqual(received, {});
  assert.deepEqual(response.content, [{ type: 'text', text: '{"state":"ready"}' }]);
  const resumed = await f.runtime.prompt({ ...f.input, sessionFile: result.sessionFile });
  assert.equal(resumed.sessionFile, result.sessionFile);
  assert.equal(resumed.text, 'done');
  assert.deepEqual(resumed.usage, result.usage);
  assert.deepEqual(f.counts(), { aborted: 0, disposed: 2, modelCreations: 2 });
});

test('implementer gets coding tools and reviewer gets test tools without edit/write', async (t) => {
  const f = await fixture(t);
  await f.runtime.prompt({ ...f.input, role: 'implementer' });
  await f.runtime.prompt({ ...f.input, role: 'reviewer' });
  assert.deepEqual(f.captures[0].tools, ['read', 'ls', 'grep', 'find', 'bash', 'edit', 'write']);
  assert.deepEqual(f.captures[1].tools, ['read', 'ls', 'grep', 'find', 'bash']);
});

for (const behavior of ['turn-limit', 'timeout', 'error']) {
  test(`${behavior} failure reports persisted partial usage and disposes session`, async (t) => {
    const f = await fixture(t, behavior);
    await assert.rejects(f.runtime.prompt({ ...f.input, maxTurns: 1, timeoutMs: 20 }), (error) => {
      assert.ok(error instanceof PiRuntimeError);
      assert.equal(error.partial.usage.cost, 0.002);
      assert.ok(error.partial.sessionFile.endsWith('.jsonl'));
      assert.match(error.message, behavior === 'error' ? /provider failed/ : /limit|exceeded/);
      return true;
    });
    assert.equal(f.counts().disposed, 1);
    assert.equal(f.counts().aborted, behavior === 'error' ? 0 : 1);
  });
}

test('rejects bad budgets, missing resume files, and builtin tool shadowing', async (t) => {
  const f = await fixture(t);
  await assert.rejects(f.runtime.prompt({ ...f.input, maxTurns: 0 }), /maxTurns/);
  await assert.rejects(f.runtime.prompt({ ...f.input, timeoutMs: -1 }), /timeoutMs/);
  await assert.rejects(f.runtime.prompt({ ...f.input, sessionFile: join(f.dir, 'missing.jsonl') }), /ENOENT/);
  await assert.rejects(f.runtime.prompt({ ...f.input, tools: [{ name: 'bash', description: 'shadow', parameters: {}, async execute() {} }] }), /tool name/);
  assert.equal(f.captures.length, 0);
});

test('real Pi SDK initializes isolated role and custom tools without any model request', async (t) => {
  const dir = await mkdtemp(join(tmpdir(), 'constellation-pi-sdk-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  await writeFile(join(dir, 'AGENTS.md'), 'Foreign instructions that must not appear.');
  const runtime = new PiRuntime({
    createModelRuntime: ModelRuntime.create,
    async createSession(options) {
      const actual = await createAgentSession(options);
      assert.deepEqual(actual.session.getActiveToolNames().sort(), ['find', 'grep', 'ls', 'read', 'workflow_next']);
      assert.match(actual.session.systemPrompt, /Own Commander context/);
      assert.doesNotMatch(actual.session.systemPrompt, /Foreign instructions/);
      // Assert provider options through the real Agent wrapper without requesting a model.
      actual.session.agent.streamFunction = (_model, _context, request) => {
        assert.equal(request?.maxTokens, 1024);
        throw new Error('offline stream probe');
      };
      actual.session.prompt = async () => {
        const context = { messages: [] } as unknown as Parameters<AgentSession['agent']['streamFunction']>[1];
        assert.throws(() => actual.session.agent.streamFunction(options.model!, context), /offline stream probe/);
      };
      return actual;
    },
  });
  await runtime.prompt({ role: 'commander', cwd: dir, sessionDir: join(dir, 'sessions'),
    model: 'anthropic/claude-haiku-4-5', systemPrompt: 'Own Commander context', prompt: 'No API request',
    tools: [{ name: 'workflow_next', description: 'Next step', parameters: { type: 'object', properties: {} }, async execute() { return {}; } }],
  });
});

test('truncated tool responses abort instead of continuing with the same insufficient cap',async t=>{
 const f=await fixture(t,'length');
 await assert.rejects(f.runtime.prompt({...f.input,maxOutputTokens:32}),error=>error instanceof PiRuntimeError&&/output-token limit/.test(error.message)&&error.partial.usage.cost>0);
 assert.equal(f.counts().aborted,1);assert.equal(f.counts().disposed,1);
});
