import { appendFileSync } from 'node:fs';
import { randomUUID } from 'node:crypto';

/** Metadata only: never prompts, tool arguments, credentials, or tool output. */
export class Telemetry {
  readonly id = randomUUID();
  private started = performance.now();
  private request?: { id: string; started: number; first: boolean };
  private requests = 0;
  private unknownRequests = 0;
  constructor(readonly path: string, private context: { role: string; model: string; stage?: string }) {
    this.record('invocation_start');
  }
  private record(type: string, fields: Record<string, unknown> = {}) {
    appendFileSync(this.path, JSON.stringify({ type, at: new Date().toISOString(), invocationId: this.id, ...this.context, ...fields }) + '\n');
  }
  requestStart() {
    this.request = { id: randomUUID(), started: performance.now(), first: false };
    this.requests++;
    this.record('request_start', { requestId: this.request.id });
  }
  firstResponse() {
    if (!this.request || this.request.first) return;
    this.request.first = true;
    this.record('request_first_response', { requestId: this.request.id, elapsedMs: performance.now() - this.request.started });
  }
  requestEnd(message?: { stopReason: string; usage: any }) {
    if (!this.request) return;
    const known = message && (message.usage.totalTokens > 0 || !['error', 'aborted'].includes(message.stopReason));
    if (!known) this.unknownRequests++;
    this.record('request_end', {
      requestId: this.request.id, elapsedMs: performance.now() - this.request.started,
      outcome: message?.stopReason ?? 'interrupted', usage: known ? message!.usage : null,
      costSource: known ? 'pi-model-catalog' : null,
    });
    this.request = undefined;
  }
  toolEnd(name: string, elapsedMs: number | undefined, isError: boolean) {
    this.record('tool_end', { tool: name, elapsedMs: elapsedMs ?? null, isError });
  }
  finish(outcome: string) {
    this.requestEnd();
    this.record('invocation_end', { outcome, ...this.summary() });
  }
  summary() { return { invocationId: this.id, elapsedMs: performance.now() - this.started, requests: this.requests, unknownRequests: this.unknownRequests + (this.request ? 1 : 0), events: this.path }; }
}

/** Reconstruct receipts from the ledger; incomplete requests remain visible. */
export async function usageReport(dir: string) {
  const { readdir, readFile } = await import('node:fs/promises');
  const { join } = await import('node:path');
  const requests = new Map<string, Record<string, any>>();
  async function scan(path: string) {
    for (const entry of await readdir(path, { withFileTypes: true })) {
      if (entry.isDirectory() && entry.name !== 'runtime-config') await scan(join(path, entry.name));
      if (entry.isFile() && entry.name === 'events.jsonl') {
        for (const line of (await readFile(join(path, entry.name), 'utf8')).split('\n')) {
          if (!line.trim()) continue;
          const event = JSON.parse(line);
          if (event.type === 'request_start') requests.set(event.requestId, { requestId: event.requestId, invocationId: event.invocationId, role: event.role, stage: event.stage, model: event.model, startedAt: event.at, outcome: 'incomplete', elapsedMs: null, firstResponseMs: null, estimatedCostUsd: null });
          const request = requests.get(event.requestId);
          if (!request) continue;
          if (event.type === 'request_first_response') request.firstResponseMs = event.elapsedMs;
          if (event.type === 'request_end') Object.assign(request, { outcome: event.outcome, elapsedMs: event.elapsedMs, estimatedCostUsd: event.usage?.cost?.total ?? null, costSource: event.costSource, tokens: event.usage ? { input: event.usage.input, output: event.usage.output, cacheRead: event.usage.cacheRead, cacheWrite: event.usage.cacheWrite } : null });
        }
      }
    }
  }
  await scan(dir);
  const rows = [...requests.values()];
  return { requests: rows, knownEstimatedCostUsd: rows.reduce((sum, row) => sum + (row.estimatedCostUsd ?? 0), 0), unknownUsageRequests: rows.filter(row => row.estimatedCostUsd === null).length };
}
