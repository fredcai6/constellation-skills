import { mkdir, readFile, writeFile, rename, open, unlink, stat } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { Engine } from './engine.js';
import type { Config } from './workflow.js';
import { checklist } from './checklist.js';
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
  let fence: { char:string; length:number } | undefined;
  for (const line of text.split(/\r?\n/)) {
    const marker=/^ {0,3}(`{3,}|~{3,})(.*)$/.exec(line);
    if(fence){
      if(marker&&marker[1][0]===fence.char&&marker[1].length>=fence.length&&!marker[2].trim())fence=undefined;
      if(name)result[name]+=line+'\n';
      continue;
    }
    if(marker){fence={char:marker[1][0],length:marker[1].length};if(name)result[name]+=line+'\n';continue;}
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
export type CrewRole = 'implementer' | 'reviewer';
export const RETURN_STATUSES = ['complete', 'partial', 'blocked', 'out-of-scope', 'failed'];
export const resultSections = (role:CrewRole) => role === 'implementer' ? ['completed slice', 'scope', 'test mode', 'evidence', 'stop conditions hit', 'workflow feedback'] : ['handoff compliance', 'scope drift', 'evidence verdict', 'blockers', 'workflow feedback'];
export function outputContract(role:CrewRole,gate:string,source:string) {
  const template=join(source,'skills',role,'templates',role==='implementer'?'IMPLEMENTER_RESULT.template.md':'REVIEW_RESULT.template.md');
  return `\n\n## Output Contract\nUse second-level Markdown headings (\`## Heading\`), not bullet-field substitutes. Result template: ${template}.\nRequired headings: Assigned gate; ${resultSections(role).join('; ')}; Return status${role==='reviewer'?'; Result':''}.\nAssigned gate must be exactly \`${gate}\`. Return status must be exactly one of: ${RETURN_STATUSES.join(' | ')}. Do not use success or failure. ${role==='reviewer'?'Result must be APPROVE, BLOCK or COMMENT.':''}\nWrite the named result file, then call submit_result with no arguments. The file is the delivery; no duplicate explanation.\n`;
}
export const REVIEWER_PROMPT = `You are a Constellation Reviewer running a bounded artifact invocation.
Read project AGENTS.md and referenced guidance when present, then the input artifact and its references. Independently inspect the assigned implementation and run relevant checks. Do not edit project files except the named review result and any review survey explicitly required by the handoff. Do not assume supplied claims are true. Report missing authority or evidence as blockers.
The controller owns your bound delivery gate; do not mutate controller files. Write the full REVIEW_RESULT at the named result path, including Assigned gate, Result (APPROVE, BLOCK or COMMENT), evidence verdict, blockers, workflow feedback and lowercase Return status. Call submit_result after writing it, then only acknowledge delivery. A delivered review does not approve for a human or advance an external Commander gate. Do not modify the input snapshot or invocation metadata.`;
export function parseHandoff(text: string, role: CrewRole = 'implementer') {
  const parts = sections(text);
  for (const name of role === 'implementer' ? ['gate', 'task', 'protected intent', 'test mode', 'close criteria', 'allowed scope', 'required evidence', 'verification commands', 'authority', 'stop conditions', 'return format'] : ['gate', 'task statement', 'how to inspect the diff', 'close criteria', 'allowed scope', 'constraints the implementation must respect', 'evidence produced', 'stop conditions', 'return format']) {
    if (!parts[name]?.trim() || /^`?<[^>]+>`?$/.test(parts[name].trim())) throw Error(`Incomplete handoff section: ${name}`);
  }
  const gate = scalar(parts.gate);
  // Accept the existing template's filled Delivery sentence without a second format.
  const delivery = new RegExp('Write the full `' + (role === 'implementer' ? 'IMPLEMENTER_RESULT' : 'REVIEW_RESULT') + '` to `([^`]+)`').exec(text)?.[1];
  const result = parts['result artifact'] ? scalar(parts['result artifact']) : delivery;
  if (!result || /[<>\r\n]/.test(result)) throw Error('Handoff must name a concrete Result Artifact path (or filled Delivery path)');
  if (delivery && parts['result artifact'] && result !== delivery) throw Error('Conflicting result artifact paths');
  return { gate, result };
}
export type Submission = { path: string; sha256: string; status: string; verdict?: 'APPROVE' | 'BLOCK' | 'COMMENT' };
type Attempt = { id: string; startedAt: string; endedAt?: string; elapsedMs?: number; outcome: string; error?: string; usage?: RuntimeResult['usage']; metrics?: RuntimeResult['metrics']; submitted?: Submission };
type Manifest = { schemaVersion: 1; id: string; role: CrewRole; promptVersion: number; input: { path: string; snapshot: string; sha256: string }; result: string; gate: string; config: Config; sessionFile?: string; attempts: Attempt[]; completed?: Submission; abandoned?: { reason:string; at:string } };

export class ArtifactInvocation {
  constructor(readonly dir: string, private runtime: Pick<PiRuntime, 'prompt'> = new PiRuntime()) { this.dir = resolve(dir); }
  static async create(dir: string, input: string, config: Config, role: CrewRole = 'implementer') {
    const inputPath = resolve(config.cwd, input);
    const text = await readFile(inputPath, 'utf8');
    const handoff = parseHandoff(text, role);
    if (![config.maxCalls, config.maxTurns, config.timeoutMs, config.maxOutputTokens ?? 4096].every(n => Number.isSafeInteger(n) && n > 0)) throw Error('Invocation limits must be positive integers');
    const result = resolve(config.cwd, handoff.result);
    if (result === inputPath || result.startsWith(resolve(dir) + '/')) throw Error('Result must not overwrite the input or invocation metadata');
    try { await stat(result); throw Error('Result already exists; use a new result path for a new invocation'); } catch (error: any) { if (error.code !== 'ENOENT') throw error; }
    await mkdir(dir, { recursive: false });
    const id = randomUUID();
    const manifest: Manifest = { schemaVersion: 1, id, role, promptVersion: IMPLEMENTER_PROMPT_VERSION,
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
    return { run: this.dir, role: m.role, status: m.abandoned ? 'abandoned' : m.completed?.status ?? m.attempts.at(-1)?.outcome ?? 'pending',
      input: m.input, result: m.completed ?? m.attempts.at(-1)?.submitted ?? { path: m.result },
      attempts: m.attempts.map(({ id, startedAt, endedAt, elapsedMs, outcome, usage, metrics, error }) =>
        ({ id, startedAt, endedAt, elapsedMs, outcome, estimatedCostUsd: usage?.cost ?? null, costSource: usage ? 'pi-model-catalog' : null, metrics, error })),
      costIncomplete: m.attempts.some(a => !a.usage || (a.metrics?.unknownRequests ?? 0) > 0),
      estimatedCostUsd: m.attempts.reduce((sum, a) => sum + (a.usage?.cost ?? 0), 0),
      engine: join(this.dir, 'spine.json') };
  }
  async status() { return this.receipt(JSON.parse(await readFile(join(this.dir, 'invocation.json'), 'utf8'))); }
  async abandon(reason:string) {
    if(!reason.trim())throw Error('Abandon reason required');
    const lock=join(this.dir,'controller.lock'),handle=await open(lock,'wx');
    await handle.writeFile(JSON.stringify({pid:process.pid,at:new Date().toISOString()}));
    try {
      const m:Manifest=JSON.parse(await readFile(join(this.dir,'invocation.json'),'utf8'));
      if(m.abandoned||m.completed)return;
      const state=await this.engine(m).state();
      if(state.active){
        await this.required(m,'claim',['--claimed-by',m.role,'--worktree',m.config.cwd]);
        if(state.active.status==='pending')await this.required(m,'start',['work']);
        if(state.active.status!=='blocked')await this.required(m,'block',['work','--blocker',reason]);
        await this.required(m,'release');
      }
      m.abandoned={reason,at:new Date().toISOString()};await save(join(this.dir,'invocation.json'),m);
    } finally {await handle.close();await unlink(lock);}
  }
  async run(recoverInterrupted = false, limits: Partial<Pick<Config,'maxCalls'|'maxTurns'|'timeoutMs'|'maxOutputTokens'>> = {}) {
    const lock = join(this.dir, 'controller.lock');
    let handle;
    try { handle = await open(lock, 'wx'); } catch (error: any) { if (error.code === 'EEXIST') throw Error('Invocation already has a controller; recover it before resuming'); throw error; }
    await handle.writeFile(JSON.stringify({ pid: process.pid, at: new Date().toISOString() }));
    try {
      const m: Manifest = JSON.parse(await readFile(join(this.dir, 'invocation.json'), 'utf8'));
      for(const key of ['maxCalls','maxTurns','timeoutMs','maxOutputTokens'] as const){
        const value=limits[key];if(value===undefined)continue;
        if(!Number.isSafeInteger(value)||value<1)throw Error(key+' must be a positive integer');
        m.config[key]=value;
      }
      if(Object.keys(limits).length)await save(join(this.dir,'invocation.json'),m);
      if (m.abandoned)throw Error('Invocation was explicitly abandoned; start a new crew round');
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
      await this.required(m, 'claim', ['--claimed-by', m.role, '--worktree', m.config.cwd]);
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
        const result = await this.runtime.prompt({ role: m.role, cwd: m.config.cwd, sessionDir: join(this.dir, 'session'), sessionFile: m.sessionFile,
          model: m.config.model, systemPrompt: m.role === 'implementer' ? IMPLEMENTER_PROMPT : REVIEWER_PROMPT, stage: m.gate,
          prompt: `Execute the handoff snapshot at ${m.input.snapshot}. Original location: ${m.input.path}. SHA256: ${m.input.sha256}. Resolve project-relative references against ${m.config.cwd}. Assigned gate: ${m.gate}. Result artifact: ${m.result}.`,
          maxTurns: m.config.maxTurns, timeoutMs: m.config.timeoutMs, maxOutputTokens: m.config.maxOutputTokens ?? 4096,
          onSessionAllocated: async file => { m.sessionFile = file; await save(join(this.dir, 'invocation.json'), m); },
          tools: [{ name: 'submit_result', endInvocation:true, description: 'Deliver the named result file. No commentary or duplicated evidence arguments.', parameters: { type: 'object', properties: {}, additionalProperties: false }, execute: async () => {
            if (attempt.submitted) throw Error('Result already submitted');
            const s = await stat(m.result);
            if (!s.isFile() || `${s.mtimeMs}:${s.ctimeMs}:${s.size}` === before) throw Error('Result is stale or not a file');
            const text = await readFile(m.result, 'utf8'); const parts = sections(text);
            const status = scalar(parts['return status'] ?? '');
            if (!RETURN_STATUSES.includes(status)) throw Error('Result requires ## Return status with one value: '+RETURN_STATUSES.join(' | '));
            if (scalar(parts['assigned gate'] ?? '') !== m.gate) throw Error('Result assigned gate does not match handoff');
            for (const name of resultSections(m.role)) {
              if (!parts[name]?.trim()) throw Error(`Result missing section: ${name}`);
            }
            const verdict = m.role === 'reviewer' ? scalar(parts.result ?? '') : undefined;
            if (m.role === 'reviewer' && !['APPROVE', 'BLOCK', 'COMMENT'].includes(verdict ?? '')) throw Error('Review requires Result APPROVE, BLOCK or COMMENT');
            attempt.submitted = { path: m.result, sha256: digest(text), status, ...(verdict ? { verdict: verdict as Submission['verdict'] } : {}) };
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
