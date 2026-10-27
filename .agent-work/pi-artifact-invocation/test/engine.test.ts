import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { Engine } from "../src/engine.js";
const source = process.env.CONSTELLATION_SOURCE ?? fileURLToPath(new URL("../../../../", import.meta.url));
const python = process.env.CONSTELLATION_PYTHON ?? "/home/tommy/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/bin/python";
async function fixture(command = `"${python}" -c "pass"`) {
  const cwd = await mkdtemp(join(tmpdir(), "constellation-pi-engine-"));
  const file = join(cwd, "plan.json");
  await writeFile(file, JSON.stringify({ work_id: "bridge-test", type: "gated", config: {}, items: ["g1"], tasks: {
    g1: { id: "g1", title: "Bridge gate", imperative: "Run the check", status: "pending", status_detail: {},
      preconditions: [], postconditions: command ? [{ id: "c1", statement: "Check passes", check: { kind: "command", command }, satisfied: false }] : [],
      constraints: [], evidence: [], rework_count: 0, why_exempt: true },
  }, consolidation: null, triage_candidates: [], blockers: [] }));
  return { cwd, file, engine: new Engine({ source, python, cwd, file, sessionId: "commander-test" }) };
}
const cli = (file: string, cwd: string, ...args: string[]) => execFileSync(python, [join(source, "scripts/checklist_engine.py"), "--file", file, ...args], { cwd, encoding: "utf8" });
test("state equals original projection and human CLI stays unchanged", async () => {
  const f = await fixture();
  try {
    const before = await readFile(f.file, "utf8");
    const human = cli(f.file, f.cwd, "current");
    const state = await f.engine.state();
    const original = execFileSync(python, ["-c", "import sys,json; from pathlib import Path; sys.path.insert(0, sys.argv[1]); import checklist_engine as e; print(json.dumps(e.state(e.load(Path(sys.argv[2])))))", join(source, "scripts"), f.file], { encoding: "utf8" });
    assert.deepEqual(state, JSON.parse(original));
    assert.equal((await f.engine.run("current")).output, human.trim());
    assert.equal(await readFile(f.file, "utf8"), before);
    assert.equal(state.active?.id, "g1");
    assert.ok(state.active?.next_verbs.length);
  } finally { await rm(f.cwd, { recursive: true, force: true }); }
});
test("failed command blocks advance through the real engine", async () => {
  const f = await fixture(`"${python}" -c "import sys; sys.exit(1)"`);
  try {
    assert.equal((await f.engine.run("claim")).ok, true);
    assert.equal((await f.engine.run("start", ["g1"])).ok, true);
    const result = await f.engine.run("advance", ["g1"]);
    assert.equal(result.ok, false);
    assert.match(result.output, /REFUSED/);
    assert.equal(result.state?.active?.id, "g1");
    assert.notEqual(result.state?.active?.status, "done");
    assert.deepEqual(result.state, await f.engine.state());
  } finally { await rm(f.cwd, { recursive: true, force: true }); }
});
test("lease ownership enforced; owner completes and releases", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.engine.run("claim")).ok, true);
    const refused = await new Engine({ ...f.engine.options, sessionId: "other-session" }).run("start", ["g1"]);
    assert.equal(refused.ok, false);
    assert.match(refused.output, /session|lease/i);
    assert.equal(refused.state?.active?.status, "pending");
    assert.equal((await f.engine.run("start", ["g1"])).ok, true);
    const done = await f.engine.run("advance", ["g1"]);
    assert.equal(done.ok, true, done.output);
    assert.equal(done.state?.active, null);
    assert.equal((await f.engine.run("release")).ok, true);
  } finally { await rm(f.cwd, { recursive: true, force: true }); }
});
test("adapter prevents argv changing bound identity or file; errors are clear", async () => {
  const f = await fixture();
  try {
    await assert.rejects(f.engine.run("claim", ["--session-id=someone-else"]), /identity.*bound/);
    await assert.rejects(f.engine.run("start", ["g1", "--file", "different.json"]), /identity.*bound/);
    const result = await f.engine.run("unknown-command");
    assert.equal(result.ok, false);
    assert.match(result.output, /invalid choice/);
    await assert.rejects(new Engine({ ...f.engine.options, source: resolve(f.cwd, "missing") }).state(), /engine not found/);
  } finally { await rm(f.cwd, { recursive: true, force: true }); }
});
