import { mkdir, stat } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import {
  createAgentSession, DefaultResourceLoader, ModelRuntime, SessionManager, SettingsManager,
  type AgentSession, type CreateAgentSessionOptions, type ToolDefinition,
} from '@earendil-works/pi-coding-agent';

export type Role = 'commander' | 'implementer' | 'reviewer';

export interface RuntimeTool {
  name: string;
  description: string;
  parameters: any;
  execute(args: any): Promise<unknown>;
}

export interface RuntimePrompt {
  role: Role;
  cwd: string;
  sessionDir: string;
  sessionFile?: string;
  /** Persist this pointer before the prompt can make a provider request. New
   * JSONL files appear when Pi persists its first conversation message. */
  onSessionAllocated?(sessionFile: string): Promise<void> | void;
  /** provider/model-id, or an Anthropic model ID. */
  model: string;
  systemPrompt: string;
  prompt: string;
  tools: RuntimeTool[];
  maxTurns?: number;
  timeoutMs?: number;
  maxOutputTokens?: number;
}

export interface RuntimeResult {
  text: string;
  sessionFile: string;
  usage: { input: number; output: number; cost: number };
}

/** Failed runs still expose their persisted session and incremental, known usage. */
export class PiRuntimeError extends Error {
  constructor(message: string, public readonly partial: RuntimeResult, options?: ErrorOptions) {
    super(message, options);
    this.name = 'PiRuntimeError';
  }
}

type RuntimeSession = Pick<AgentSession, 'prompt' | 'subscribe' | 'messages' | 'getSessionStats' | 'dispose'> & {
  agent: Pick<AgentSession['agent'], 'abort' | 'streamFunction'>;
};

interface RuntimeDependencies {
  createSession(options: CreateAgentSessionOptions): Promise<{ session: RuntimeSession }>;
  createModelRuntime: typeof ModelRuntime.create;
}

const readTools = ['read', 'ls', 'grep', 'find'];
const roleTools: Record<Role, string[]> = {
  commander: readTools,
  implementer: [...readTools, 'bash', 'edit', 'write'],
  // Bash enables test execution. This is a role convention, not a filesystem sandbox.
  reviewer: [...readTools, 'bash'],
};

export class PiRuntime {
  constructor(private readonly dependencies: RuntimeDependencies = {
    createSession: createAgentSession,
    createModelRuntime: ModelRuntime.create,
  }) {}

  async prompt(input: RuntimePrompt): Promise<RuntimeResult> {
    const maxTurns = input.maxTurns ?? 12;
    const timeoutMs = input.timeoutMs ?? 120_000;
    const maxOutputTokens = input.maxOutputTokens ?? 1024;
    if (!Number.isSafeInteger(maxTurns) || maxTurns < 1) throw new Error('maxTurns must be a positive integer');
    if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1) throw new Error('timeoutMs must be a positive integer');
    if (!Number.isSafeInteger(maxOutputTokens) || maxOutputTokens < 1) throw new Error('maxOutputTokens must be a positive integer');
    if (!(input.role in roleTools)) throw new Error(`Unknown role: ${input.role}`);
    const cwd = resolve(input.cwd);
    const sessionDir = resolve(input.sessionDir);
    const agentDir = join(sessionDir, 'runtime-config');
    await mkdir(sessionDir, { recursive: true });
    if (input.sessionFile && !(await stat(resolve(input.sessionFile))).isFile()) {
      throw new Error('Resume requires an existing Pi session file');
    }
    const manager = input.sessionFile
      ? SessionManager.open(resolve(input.sessionFile), sessionDir, cwd)
      : SessionManager.create(cwd, sessionDir);
    const sessionFile = manager.getSessionFile();
    if (!sessionFile) throw new Error('Pi did not allocate a persistent session file');

    // In-memory settings and an explicit loader prevent ~/.pi, project AGENTS,
    // skills, packages, MCP, or extensions from changing this role's instructions.
    const settingsManager = SettingsManager.inMemory({
      compaction: { enabled: false },
      retry: { enabled: false, provider: { maxRetries: 0, timeoutMs } },
      cacheWarming: 'off',
    });
    const resourceLoader = new DefaultResourceLoader({
      cwd, agentDir, settingsManager,
      noExtensions: true, disabledBuiltinExtensions: ['mcp'],
      noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true,
      systemPrompt: input.systemPrompt,
      appendSystemPromptOverride: () => [],
      agentsFilesOverride: () => ({ agentsFiles: [] }),
    });
    await resourceLoader.reload();
    // Use env credentials through Pi; no catalog refresh or shared auth/config files.
    const modelRuntime = await this.dependencies.createModelRuntime({
      authPath: join(agentDir, 'auth.json'), modelsPath: null,
      allowModelNetwork: false, refreshOnCreate: false,
    });
    const separator = input.model.indexOf('/');
    const provider = separator < 0 ? 'anthropic' : input.model.slice(0, separator);
    const id = separator < 0 ? input.model : input.model.slice(separator + 1);
    const model = modelRuntime.getModel(provider, id);
    if (!model) throw new Error(`Unknown Pi model: ${provider}/${id}`);

    const builtinNames = new Set(Object.values(roleTools).flat());
    const names = new Set<string>();
    const customTools: ToolDefinition[] = input.tools.map((tool) => {
      if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(tool.name) || builtinNames.has(tool.name) || names.has(tool.name)) {
        throw new Error(`Invalid or duplicate workflow tool name: ${tool.name}`);
      }
      names.add(tool.name);
      return {
        name: tool.name, label: tool.name, description: tool.description,
        parameters: tool.parameters,
        async execute(_id, args, signal) {
          signal?.throwIfAborted();
          const result = await tool.execute(args);
          return {
            content: [{ type: 'text', text: typeof result === 'string' ? result : JSON.stringify(result) ?? 'null' }],
            details: result,
          };
        },
      };
    });
    const { session } = await this.dependencies.createSession({
      cwd, agentDir, sessionManager: manager, settingsManager, resourceLoader,
      modelRuntime, model, thinkingLevel: 'off',
      tools: [...roleTools[input.role], ...names], customTools,
    });
    // Preserve Pi's model runtime/auth/events while bounding every provider response.
    const stream = session.agent.streamFunction;
    session.agent.streamFunction = (model, context, options) =>
      stream(model, context, { ...options, maxTokens: maxOutputTokens });
    const initial = session.getSessionStats();
    const startMessage = session.messages.length;
    const result = (): RuntimeResult => {
      const stats = session.getSessionStats();
      return {
        sessionFile,
        text: session.messages.slice(startMessage).flatMap((message) =>
          message.role === 'assistant'
            ? message.content.flatMap((part) => part.type === 'text' ? [part.text] : []) : [],
        ).join('\n'),
        usage: {
          input: stats.tokens.input + stats.tokens.cacheRead + stats.tokens.cacheWrite
            - initial.tokens.input - initial.tokens.cacheRead - initial.tokens.cacheWrite,
          output: stats.tokens.output - initial.tokens.output,
          cost: stats.cost - initial.cost,
        },
      };
    };
    let turns = 0;
    let limit: string | undefined;
    const stop = (reason: string) => {
      limit ??= reason;
      // Synchronous abort avoids awaiting session settlement inside its own event.
      session.agent.abort();
    };
    const unsubscribe = session.subscribe((event) => {
      if(event.type==='turn_end'&&event.message.role==='assistant'&&event.message.stopReason==='length')stop('Pi response reached its output-token limit; increase maxOutputTokens before resuming');
      if (event.type === 'turn_start' && ++turns > maxTurns) stop(`Pi exceeded ${maxTurns} turns`);
      if (event.type === 'turn_end' && turns >= maxTurns
          && event.message.role === 'assistant'
          && event.message.content.some((part) => part.type === 'toolCall')) {
        stop(`Pi reached its ${maxTurns}-turn limit`);
      }
    });
    const timer = setTimeout(() => stop(`Pi exceeded ${timeoutMs}ms`), timeoutMs);
    try {
      await input.onSessionAllocated?.(sessionFile);
      if (limit) throw new Error(limit);
      await session.prompt(input.prompt);
      if (limit) throw new Error(limit);
      const last = session.messages.slice(startMessage).filter((m) => m.role === 'assistant').at(-1);
      if (last && (last.stopReason === 'error' || last.stopReason === 'aborted' || last.stopReason === 'length')) {
        throw new Error(`Pi stopped with ${last.stopReason}: ${last.errorMessage ?? 'incomplete response'}`);
      }
      return result();
    } catch (error) {
      throw new PiRuntimeError(limit ?? (error instanceof Error ? error.message : String(error)), result(), { cause: error });
    } finally {
      clearTimeout(timer);
      unsubscribe();
      session.dispose();
    }
  }
}
