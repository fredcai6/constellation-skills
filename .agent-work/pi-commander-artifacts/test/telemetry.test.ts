import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Telemetry } from '../src/telemetry.js';
test('request ledger separates model requests and tools, retains unknown usage on interruption',t=>{
 const dir=mkdtempSync(join(tmpdir(),'pi-events-'));t.after(()=>rmSync(dir,{recursive:true,force:true}));
 const path=join(dir,'events.jsonl'),journal=new Telemetry(path,{role:'implementer',model:'test',stage:'g1'});
 journal.requestStart();journal.firstResponse();journal.firstResponse();journal.requestEnd({stopReason:'toolUse',usage:{totalTokens:4,cost:{total:0.01}}});
 journal.toolEnd('bash',12,false);journal.requestStart();assert.equal(journal.summary().unknownRequests,1);journal.finish('error');
 const events=readFileSync(path,'utf8').trim().split('\n').map(l=>JSON.parse(l));
 assert.equal(events.filter(e=>e.type==='request_start').length,2);
 assert.equal(events.filter(e=>e.type==='request_first_response').length,1);
 const ends=events.filter(e=>e.type==='request_end');assert.equal(ends[0].usage.cost.total,0.01);assert.equal(ends[1].usage,null);assert.equal(ends[1].outcome,'interrupted');
 assert.equal(events.at(-1).requests,2);assert.equal(new Set(events.map(e=>e.invocationId)).size,1);
 assert.ok(ends.every(e=>e.elapsedMs>=0));
});

test('usage report retains incomplete and unknown requests without inventing zero cost',async t=>{
 const {usageReport}=await import('../src/telemetry.js');
 const dir=mkdtempSync(join(tmpdir(),'pi-usage-'));t.after(()=>rmSync(dir,{recursive:true,force:true}));
 const journal=new Telemetry(join(dir,'events.jsonl'),{role:'implementer',model:'test'});
 journal.requestStart();journal.firstResponse();
 const pending=await usageReport(dir);assert.equal(pending.unknownUsageRequests,1);assert.equal(pending.requests[0].estimatedCostUsd,null);
 journal.requestEnd({stopReason:'stop',usage:{input:2,output:1,cacheRead:0,cacheWrite:0,totalTokens:3,cost:{total:0.01}}});journal.finish('complete');
 const done=await usageReport(dir);assert.equal(done.unknownUsageRequests,0);assert.equal(done.knownEstimatedCostUsd,0.01);
 assert.ok(done.requests[0].firstResponseMs>=0);assert.ok(done.requests[0].elapsedMs>=0);
});
