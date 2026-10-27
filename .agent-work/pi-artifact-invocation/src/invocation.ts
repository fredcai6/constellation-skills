import { mkdir, readFile, writeFile, rename, open, unlink, stat } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { Engine } from './engine.js';
import { checklist, type Config } from './workflow.js';
import { PiRuntime, type RuntimeResult } from './pi-runtime.js';

// Changes require a version bump; task text and engine state never enter this prefix.
export const IMPLEMENTER_PROMPT_VERSION = 1;
export const IMPLEMENTER_PROMPT = `You are a Constellation Implementer running a bounded artifact invocation.
Read project AGENTS.md and its referenced guidance when present. The input artifact and its referenced project guidance contain the assignment, scope, authority, verification and return contract. Read them before work. If information is missing or contradictory, report the gap in the named result artifact rather than inventing an assignment. Do not expand scope. Overrides require explicit human or higher-level direction recorded in the artifact.
The controller owns your bound engine gate; do not create a replacement checklist or mutate controller files. The input may reference additional task-specific checklists: follow its requirements and report any conflict.
Write the complete Implementer result to the exact result path supplied in the invocation. Include the assigned gate, evidence and lowercase Return status. Call submit_result after writing it. Your final conversational response is only a delivery acknowledgment; do not restate the result. A complete result is a claim for independent review, not human acceptance. Do not modify the input snapshot or invocation metadata.`;
const digest = (text: string) => createHash('sha256').update(text).digest('hex');
async function save(path: string, value: unknown) {
  const tmp = `${path}.${randomUUID()}.tmp`;
  await writeFile(tmp, JSON.stringify(value, null, 2) + '\n');
  await rename(tmp, path);
}
export function sections(text: string) {
  const result: Record<string, string> = {};
  let name: string | undefined;
  for (const line of text.split(/\r?\n/)) {
    const match = /^##\s+(.+?)\s*$/.exec(line);
    if (match) {
      name = match[1].toLowerCase();
      if (name in result) throw Error(`Duplicate section: ${match[1]}`);
      result[name] = '';
    } else if (name) result[name] += line + '\n';
  }
  return result;
}
function scalar(text: string) { return text.trim().replace(/^`([^`]+)`$/, '$1').trim(); }
export function parseHandoff(text: string) {
  const parts = sections(text);
  for (const name of ['gate', 'task', 'protected intent', 'test mode', 'close criteria', 'allowed scope', 'required evidence', 'verification commands', 'authority', 'stop conditions', 'return format']) {
    if (!parts[name]?.trim() || /^`?<[^>]+>`?$/.test(parts[name].trim())) throw Error(`Incomplete handoff section: ${name}`);
  }
  const gate = scalar(parts.gate);
  // Accept the existing template's filled Delivery sentence without a second format.
  const delivery = /Write the full `IMPLEMENTER_RESULT` to `([^`]+)`/.exec(text)?.[1];
  const result = parts['result artifact'] ? scalar(parts['result artifact']) : delivery;
  if (!result || /[<>\r\n]/.test(result)) throw Error('Handoff must name a concrete Result Artifact path (or filled Delivery path)');
  if (delivery && parts['result artifact'] && result !== delivery) throw Error('Conflicting result artifact paths');
  return { gate, result };
}
type Submission = { path: string; sha256: string; status: string };
type Attempt = { id: string; startedAt: string; endedAt?: string; elapsedMs?: number; outcome: string; error?: string; usage?: RuntimeResult['usage']; metrics?: RuntimeResult['metrics']; submitted?: Submission };
type Manifest = { schemaVersion: 1; id: string; role: 'implementer'; promptVersion: number; input: { path: string; snapshot: string; sha256: string }; result: string; gate: string; config: Config; sessionFile?: string; attempts: Attempt[]; completed?: Submission };

export class ArtifactInvocation {
  constructor(readonly dir: string, private runtime: Pick<PiRuntime, 'prompt'> = new PiRuntime()) { this.dir = resolve(dir); }
  static async create(dir: string, input: string, config: Config) {
    const inputPath = resolve(config.cwd, input);
    const text = await readFile(inputPath, 'utf8');
    const handoff = parseHandoff(text);
    if (![config.maxCalls, config.maxTurns, config.timeoutMs, config.maxOutputTokens ?? 4096].every(n => Number.isSafeInteger(n) && n > 0)) throw Error('Invocation limits must be positive integers');
    const result = resolve(config.cwd, handoff.result);
    if (result === inputPath || result.startsWith(resolve(dir) + '/')) throw Error('Result must not overwrite the input or invocation metadata');
    try { await stat(result); throw Error('Result already exists; use a new result path for a new invocation'); } catch (error: any) { if (error.code !== 'ENOENT') throw error; }
    await mkdir(dir, { recursive: false });
    const id = randomUUID();
    const manifest: Manifest = { schemaVersion: 1, id, role: 'implementer', promptVersion: IMPLEMENTER_PROMPT_VERSION,
      input: { path: inputPath, snapshot: join(resolve(dir), 'input.md'), sha256: digest(text) }, result, gate: handoff.gate,
      config: { ...config, cwd: resolve(config.cwd), source: resolve(config.source) }, attempts: [] };
    await writeFile(manifest.input.snapshot, text);
    await save(join(dir, 'invocation.json'), manifest);
    await save(join(dir, 'spine.json'), checklist(id, true));
    return new ArtifactInvocation(dir);
  }
  private engine(m: Manifest) { return new Engine({ source: m.config.source, python: m.config.python, cwd: m.config.cwd, file: join(this.dir, 'spine.json'), sessionId: m.id }); }
  private async required(m: Manifest, verb: string, args: string[] = []) {
    const result = await this.engine(m).run(verb, args);
    if (!result.ok) throw Error(result.output);
    return result;
  }
  private receipt(m: Manifest) {
    return { run: this.dir, role: m.role, status: m.completed?.status ?? m.attempts.at(-1)?.outcome ?? 'pending',
      input: m.input, result: m.completed ?? m.attempts.at(-1)?.submitted ?? { path: m.result },
      attempts: m.attempts.map(({ id, startedAt, endedAt, elapsedMs, outcome, usage, metrics, error }) =>
        ({ id, startedAt, endedAt, elapsedMs, outcome, estimatedCostUsd: usage?.cost ?? null, costSource: usage ? 'pi-model-catalog' : null, metrics, error })),
      costIncomplete: m.attempts.some(a => !a.usage || (a.metrics?.unknownRequests ?? 0) > 0),
      estimatedCostUsd: m.attempts.reduce((sum, a) => sum + (a.usage?.cost ?? 0), 0),
      engine: join(this.dir, 'spine.json') };
  }
  async status() { return this.receipt(JSON.parse(await readFile(join(this.dir, 'invocation.json'), 'utf8'))); }
  async run(recoverInterrupted = false) {
    const lock = join(this.dir, 'controller.lock');
    let handle;
    try { handle = await open(lock, 'wx'); } catch (error: any) { if (error.code === 'EEXIST') throw Error('Invocation already has a controller; recover it before resuming'); throw error; }
    await handle.writeFile(JSON.stringify({ pid: process.pid, at: new Date().toISOString() }));
    try {
      const m: Manifest = JSON.parse(await readFile(join(this.dir, 'invocation.json'), 'utf8'));
      if (m.completed) {
        if (digest(await readFile(m.result, 'utf8')) !== m.completed.sha256) throw Error('Completed result changed');
        return this.receipt(m);
      }
      if (m.promptVersion !== IMPLEMENTER_PROMPT_VERSION) throw Error('Invocation prompt version changed; resume with its original runtime');
      if (digest(await readFile(m.input.path, 'utf8')) !== m.input.sha256 || digest(await readFile(m.input.snapshot, 'utf8')) !== m.input.sha256) throw Error('Input changed; create a new invocation with the corrected handoff');
      const previous = m.attempts.at(-1);
      if (previous?.outcome === 'running') {
        if (!recoverInterrupted) throw Error('Previous attempt was interrupted; inspect it and explicitly recover before resuming');
        previous.outcome = 'interrupted'; previous.endedAt = new Date().toISOString();
        await save(join(this.dir, 'invocation.json'), m);
      }
      await this.required(m, 'claim', ['--claimed-by', 'implementer', '--worktree', m.config.cwd]);
      const state = await this.engine(m).state();
      if (previous?.outcome === 'verified' && previous.submitted) {
        if (digest(await readFile(m.result, 'utf8')) !== previous.submitted.sha256) throw Error('Verified result changed before recovery');
        if (state.active) {
          await this.required(m, 'attach', ['work', '--type', 'crew-result', '--payload', JSON.stringify({ status: 'complete', artifact: previous.submitted })]);
          await this.required(m, 'advance', ['work', '--why', `Recovered result: ${m.result}`]);
        }
        await this.required(m, 'release'); m.completed = previous.submitted;
        await save(join(this.dir, 'invocation.json'), m); return this.receipt(m);
      }
      if (!state.active) {
        // Only a successful runtime result can enter this crash-recovery path.
        if (previous?.outcome !== 'verified' || !previous.submitted) throw Error('Terminal engine without verified result');
        await this.required(m, 'release'); m.completed = previous.submitted;
        await save(join(this.dir, 'invocation.json'), m); return this.receipt(m);
      }
      if (m.attempts.length >= m.config.maxCalls) throw Error('Invocation attempt limit reached');
      if (state.active.status === 'pending') await this.required(m, 'start', ['work']);
      let before: string | undefined;
      try { const s = await stat(m.result); before = `${s.mtimeMs}:${s.ctimeMs}:${s.size}`; } catch (error: any) { if (error.code !== 'ENOENT') throw error; }
      const attempt: Attempt = { id: randomUUID(), startedAt: new Date().toISOString(), outcome: 'running' };
      m.attempts.push(attempt); await save(join(this.dir, 'invocation.json'), m);
      const started = performance.now();
      try {
        const result = await this.runtime.prompt({ role: 'implementer', cwd: m.config.cwd, sessionDir: join(this.dir, 'session'), sessionFile: m.sessionFile,
          model: m.config.model, systemPrompt: IMPLEMENTER_PROMPT, stage: m.gate,
          prompt: `Execute the handoff snapshot at ${m.input.snapshot}. Original location: ${m.input.path}. SHA256: ${m.input.sha256}. Resolve project-relative references against ${m.config.cwd}. Assigned gate: ${m.gate}. Result artifact: ${m.result}.`,
          maxTurns: m.config.maxTurns, timeoutMs: m.config.timeoutMs, maxOutputTokens: m.config.maxOutputTokens ?? 4096,
          onSessionAllocated: async file => { m.sessionFile = file; await save(join(this.dir, 'invocation.json'), m); },
          tools: [{ name: 'submit_result', description: 'Deliver the named result file. No commentary or duplicated evidence arguments.', parameters: { type: 'object', properties: {}, additionalProperties: false }, execute: async () => {
            if (attempt.submitted) throw Error('Result already submitted');
            const s = await stat(m.result);
            if (!s.isFile() || `${s.mtimeMs}:${s.ctimeMs}:${s.size}` === before) throw Error('Result is stale or not a file');
            const text = await readFile(m.result, 'utf8'); const parts = sections(text);
            const status = scalar(parts['return status'] ?? '');
            if (!['complete', 'partial', 'blocked', 'out-of-scope', 'failed'].includes(status)) throw Error('Result requires a lowercase Return status');
            if (scalar(parts['assigned gate'] ?? '') !== m.gate) throw Error('Result assigned gate does not match handoff');
            for (const name of ['completed slice', 'scope', 'test mode', 'evidence', 'stop conditions hit', 'workflow feedback']) {
              if (!parts[name]?.trim()) throw Error(`Result missing section: ${name}`);
            }
            attempt.submitted = { path: m.result, sha256: digest(text), status };
            await save(join(this.dir, 'invocation.json'), m);
            return { received: true, result: attempt.submitted };
          } }],
        });
        m.sessionFile = result.sessionFile; attempt.usage = result.usage; attempt.metrics = result.metrics;
        if (!attempt.submitted) throw Error('Session stopped without submitting the named result artifact');
        if (digest(await readFile(m.result, 'utf8')) !== attempt.submitted.sha256) throw Error('Result changed after submission');
        attempt.outcome = attempt.submitted.status === 'complete' ? 'verified' : attempt.submitted.status; await save(join(this.dir, 'invocation.json'), m);
        if (attempt.submitted.status === 'complete') {
          await this.required(m, 'attach', ['work', '--type', 'crew-result', '--payload', JSON.stringify({ status: 'complete', artifact: attempt.submitted })]);
          await this.required(m, 'advance', ['work', '--why', `Result delivered: ${m.result}`]);
          await this.required(m, 'release'); m.completed = attempt.submitted;
        } else attempt.outcome = attempt.submitted.status;
      } catch (error: any) {
        if (error.partial) { m.sessionFile = error.partial.sessionFile; attempt.usage = error.partial.usage; attempt.metrics = error.partial.metrics; }
        if (attempt.outcome !== 'verified') attempt.outcome = 'error'; attempt.error = error.message;
      } finally {
        attempt.endedAt = new Date().toISOString(); attempt.elapsedMs = performance.now() - started;
        await save(join(this.dir, 'invocation.json'), m);
      }
      return this.receipt(m);
    } finally { await handle.close(); await unlink(lock); }
  }
}
