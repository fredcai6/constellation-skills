import { spawn } from "node:child_process";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

export interface EngineState {
  kind: string;
  active: null | {
    id: string;
    status: string;
    imperative: string;
    next_verbs: string[];
    [key: string]: unknown;
  };
  [key: string]: unknown;
}
export interface EngineResult {
  ok: boolean;
  output: string;
  state: EngineState | null;
}
export interface EngineOptions {
  source: string;
  python: string;
  cwd: string;
  file: string;
  sessionId: string;
}

/** Calls the unchanged engine in a separate Python process without a shell. */
export class Engine {
  readonly options: EngineOptions;
  constructor(options: EngineOptions) {
    for (const [key, value] of Object.entries(options)) {
      if (typeof value !== "string" || !value.trim()) throw new Error(`${key} must be a non-empty string`);
    }
    for (const key of ["source", "python", "cwd", "file", "sessionId"] as const) {
      if (!options[key]) throw new Error(`Missing engine option: ${key}`);
    }
    this.options = { ...options, source: resolve(options.source), cwd: resolve(options.cwd), file: resolve(options.cwd, options.file) };
  }
  async state(): Promise<EngineState> {
    const result = await this.request("state", []);
    if (!result.ok || !result.state) throw new Error(result.output || "Engine state unavailable");
    return result.state;
  }
  async run(verb: string, args: string[] = []): Promise<EngineResult> {
    if (!verb || verb.startsWith("-") || /\s/.test(verb)) throw new Error("Engine verb must be a single command name");
    if (!Array.isArray(args) || args.some(arg => typeof arg !== "string")) throw new Error("Engine args must be strings");
    return this.request(verb, args);
  }
  private request(verb: string, args: string[]): Promise<EngineResult> {
    const bridge = fileURLToPath(new URL("../python/engine_bridge.py", import.meta.url));
    return new Promise((accept, reject) => {
      const child = spawn(this.options.python, [bridge], { cwd: this.options.cwd, stdio: ["pipe", "pipe", "pipe"] });
      let stdout = "", stderr = "";
      child.stdout.setEncoding("utf8").on("data", chunk => { stdout += chunk; });
      child.stderr.setEncoding("utf8").on("data", chunk => { stderr += chunk; });
      child.on("error", error => reject(new Error(`Cannot launch engine bridge: ${error.message}`)));
      child.stdin.on("error", error => reject(new Error(`Cannot send engine request: ${error.message}`)));
      child.on("close", code => {
        if (code !== 0) { reject(new Error(`Engine bridge exited ${code}: ${stderr.trim()}`)); return; }
        try {
          const result = JSON.parse(stdout);
          if (typeof result.ok !== "boolean" || typeof result.output !== "string" || !("state" in result)) throw new Error("invalid response shape");
          if (result.error) throw new Error(result.output);
          accept(result);
        } catch (error) { reject(new Error(`Engine bridge failed: ${error instanceof Error ? error.message : String(error)}`)); }
      });
      child.stdin.end(JSON.stringify({ ...this.options, verb, args }));
    });
  }
}
