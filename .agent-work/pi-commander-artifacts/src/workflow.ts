import { mkdir, readFile, writeFile, rename, open, unlink } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { Engine } from './engine.js';
import { PiRuntime, type RuntimeTool, type Role, type RuntimePrompt } from './pi-runtime.js';
import { ArtifactInvocation, parseHandoff, sections, outputContract, type CrewRole, type Submission } from './invocation.js';
import { COMMANDER_PROMPT, COMMANDER_PROMPT_VERSION, type ArtifactRef, hash, writeArtifact, verifyArtifact, uniqueName } from './artifacts.js';

export type CrewResult = { verdict: 'COMPLETE' | 'APPROVE' | 'BLOCK'; summary: string; evidence: string[]; artifact?: Submission };
export type Config = { source: string; python: string; cwd: string; model: string; maxTurns: number; timeoutMs: number; maxCalls: number; maxOutputTokens?: number };
type CrewBinding = { role: CrewRole; dir: string; input: ArtifactRef };
type ArtifactFlow = { promptVersion: number; task: ArtifactRef; original: ArtifactRef; plan?: ArtifactRef; bindings: Partial<Record<CrewRole, CrewBinding>>; history: CrewBinding[]; lastDispatch?:ArtifactRef };
type Run = { artifacts?: ArtifactFlow; id: string; task: string; config: Config; plan?: string; repairFindings?: CrewResult; sessions: Partial<Record<Role, string>>; results: Partial<Record<Role, CrewResult>>; calls: number; cost: number; overrides: {authority:string;reason:string;verb:string;args:string[];at:string}[] };
const schema = (properties: Record<string, unknown>, required: string[] = Object.keys(properties)) => ({type:'object',properties,required,additionalProperties:false});
const str = {type:'string',minLength:1};
const phases = ['plan', 'implement', 'review', 'accept'];
export { checklist } from './checklist.js';
import { checklist } from './checklist.js';

async function json(path:string) { return JSON.parse(await readFile(path,'utf8')); }
async function save(path:string,data:unknown) { const tmp = `${path}.${randomUUID()}.tmp`; await writeFile(tmp,JSON.stringify(data,null,2)+'\n'); await rename(tmp,path); }
export class Workflow {
  constructor(readonly dir:string, private runtime: Pick<PiRuntime,'prompt'> = new PiRuntime()) { this.dir=resolve(dir); }
  static async create(dir:string, task:string, config:Config) {
    if (!task.trim()) throw Error('A task is required');
    if (![config.maxCalls,config.maxTurns,config.timeoutMs].every(n=>Number.isInteger(n)&&n>0)) throw Error('Call, turn and timeout limits must be positive integers');
    if(config.maxOutputTokens!==undefined&&(!Number.isSafeInteger(config.maxOutputTokens)||config.maxOutputTokens<1))throw Error('maxOutputTokens must be a positive integer');
    await mkdir(dir,{recursive:false});
    const id = randomUUID();
    await save(join(dir,'run.json'),{id,task,config:{...config,cwd:resolve(config.cwd),source:resolve(config.source)},sessions:{},results:{},calls:0,cost:0,overrides:[]});
    await save(join(dir,'spine.json'),checklist(id));
    const w = new Workflow(dir);
    await w.required(w.engine(await w.run()).run('claim',['--claimed-by','commander','--worktree',config.cwd]));
    return w;
  }
  static async createFromArtifact(dir:string, input:string, config:Config) {
    const originalPath=resolve(config.cwd,input),text=await readFile(originalPath,'utf8');
    const w=await Workflow.create(dir,text,config),r=await w.run();
    const task=await writeArtifact(join(w.dir,'artifacts','task.md'),text);
    r.artifacts={promptVersion:COMMANDER_PROMPT_VERSION,task,original:{path:originalPath,sha256:hash(text)},bindings:{},history:[]};
    await save(join(w.dir,'run.json'),r);return w;
  }
  private run():Promise<Run> { return json(join(this.dir,'run.json')); }
  private engine(r:Run,role?:Role) { return new Engine({source:r.config.source,python:r.config.python,cwd:r.config.cwd,file:join(this.dir,role?`${role}.json`:'spine.json'),sessionId:role?`${r.id}/${role}`:r.id}); }
  private async required(p:ReturnType<Engine['run']>) { const r=await p; if(!r.ok) throw Error(r.output); return r; }
  private async locked<T>(f:()=>Promise<T>):Promise<T> {
    const lock=join(this.dir,'controller.lock');
    let handle;
    try {handle=await open(lock,'wx');} catch(e:any) {if(e.code==='EEXIST') throw Error(`Another controller holds ${lock}. If it crashed, verify it stopped before removing the lock.`);throw e;}
    await handle.writeFile(JSON.stringify({pid:process.pid,at:new Date().toISOString()}));
    try{return await f();}finally{await handle.close();await unlink(lock);}
  }
  async status() {const r=await this.run(); return {...(r.artifacts?{task:r.artifacts.task,plan:r.artifacts.plan,crewInvocations:r.artifacts.bindings,lastDispatch:r.artifacts.lastDispatch}:{task:r.task,plan:r.plan}),calls:r.calls,maxCalls:r.config.maxCalls,cost:r.cost,maxOutputTokens:r.config.maxOutputTokens??1024,sessions:r.sessions,results:r.results,engine:await this.engine(r).state()};}
  private async evidence(r:Run, type:string,payload:unknown,role?:Role) {
    const e=this.engine(r,role);const s=await e.state();if(!s.active)throw Error('Workflow is already complete');
    if(s.active.status==='pending')await this.required(e.run('start',[s.active.id]));
    await this.required(e.run('attach',[s.active.id,'--type',type,'--payload',JSON.stringify(payload)]));
  }
  async approve(reason:string) {return this.locked(async()=>{
    if(!reason.trim())throw Error('Approval needs a human decision');
    const r=await this.run(),e=this.engine(r),s=await e.state(),id=s.active?.id;
    if(id!=='plan'&&id!=='accept')throw Error('Human approval is only available at plan or accept');
    if(r.artifacts)await this.verifyFlow(r);
    if(id==='plan'&&!r.plan)throw Error('Ask Commander to propose a plan first');
    await this.evidence(r,'user-decision',{authority:'human',decision:reason,plan:r.artifacts?.plan??r.plan});
    await this.required(e.run('advance',[id,'--why',reason]));
    if(!(await e.state()).active)await this.required(e.run('release',[]));
    return this.status();
  });}
  async restartCrew(role:CrewRole,authority:string,reason:string) {return this.locked(async()=>{
    if(!['implementer','reviewer'].includes(role)||!authority.trim()||!reason.trim())throw Error('Role, explicit directing authority and reason required');
    const r=await this.run();if(!r.artifacts)throw Error('Crew restart applies only to artifact workflows');
    await this.verifyFlow(r);
    const phase=role==='implementer'?'implement':'review',state=await this.engine(r).state();
    if(state.active?.id!==phase)throw Error(`Restart ${role} is unavailable at ${state.active?.id}`);
    const binding=r.artifacts.bindings[role];if(!binding)throw Error('No existing crew invocation to restart');
    r.overrides.push({authority,reason,verb:'restart-crew',args:[role],at:new Date().toISOString()});await save(join(this.dir,'run.json'),r);
    await new ArtifactInvocation(binding.dir).abandon(`${authority}: ${reason}`);
    delete r.artifacts.bindings[role];delete r.results[role];await save(join(this.dir,'run.json'),r);
    return this.status();
  });}
  async repair(reason:string) {return this.locked(async()=>this.repairRun(await this.run(),reason));}
  private async repairRun(r:Run,reason:string) {
    const state=await this.engine(r).state();
    if(!r.results.reviewer&&state.active?.id==='review'){
      try{const saved:CrewResult=await json(join(this.dir,'reviewer-result.json'));if(saved.verdict==='BLOCK')r.results.reviewer=saved;}
      catch(error:any){if(error.code!=='ENOENT')throw error;}
    }
    if(!['review','implement'].includes(state.active?.id??'')||r.results.reviewer?.verdict!=='BLOCK')throw Error('Repair is available after a reviewer BLOCK');
    if(!reason.trim())throw Error('Repair reason is required');
    if(r.artifacts){await this.verifyFlow(r);for(const binding of Object.values(r.artifacts.bindings))await new ArtifactInvocation(binding.dir).abandon(reason);}
    r.overrides.push({authority:'commander',reason,verb:'repair',args:[],at:new Date().toISOString()});
    await save(join(this.dir,'run.json'),r);
    for(const role of r.artifacts?[]:['implementer','reviewer'] as const){
      const child=this.engine(r,role);
      await this.required(child.run('claim',['--claimed-by',role,'--worktree',r.config.cwd]));
      const cs=await child.state();
      if(!cs.active)await this.required(child.run('reopen',['work','--reason',reason]));
      else if(cs.active.status==='blocked')await this.required(child.run('resume',['work','--reason',reason]));
    }
    if((await this.engine(r).state()).active?.id==='review')await this.required(this.engine(r).run('reopen',['implement','--reason',reason]));
    r.repairFindings=r.results.reviewer;
    if(r.artifacts)r.artifacts.bindings={};
    delete r.results.implementer;delete r.results.reviewer;
    await save(join(this.dir,'run.json'),r);
    return this.status();
  }
  async override(authority:string,reason:string,verb:string,args:string[]) {return this.locked(async()=>{
    if(!authority.trim()||!reason.trim())throw Error('Explicit directing authority and reason are required');
    if(!['waive','reopen','resume','skip','amend','start','advance','attest'].includes(verb))throw Error('Override supports waive, reopen, resume, skip, amend, start, advance, attest');
    const r=await this.run();r.overrides.push({authority,reason,verb,args,at:new Date().toISOString()});await save(join(this.dir,'run.json'),r);
    if(verb==='reopen'&&['implement','review'].includes(args[0])){
      const state=await this.engine(r).state();
      if(state.active&&phases.indexOf(args[0])>=phases.indexOf(state.active.id))throw Error('Only a completed parent gate can be reopened; use repair after a reviewer BLOCK');
      const roles:('implementer'|'reviewer')[]=args[0]==='implement'?['implementer','reviewer']:['reviewer'];
      for(const role of roles){
        if(r.artifacts){const binding=r.artifacts.bindings[role];if(binding)await new ArtifactInvocation(binding.dir).abandon(reason);delete r.artifacts.bindings[role];delete r.results[role];continue;}
        try{await readFile(join(this.dir,`${role}.json`));}catch(error:any){if(error.code==='ENOENT')continue;throw error;}
        const child=this.engine(r,role);await this.required(child.run('claim',['--claimed-by',role,'--worktree',r.config.cwd]));
        if(!(await child.state()).active)await this.required(child.run('reopen',['work','--reason',reason]));
        delete r.results[role];
      }
      await save(join(this.dir,'run.json'),r);
    }
    const extra=verb==='start'?[]:verb==='advance'?['--why',reason]:verb==='attest'?['--note',reason]:verb==='waive'||verb==='amend'?['--authority',authority,'--reason',reason]:['--reason',reason];
    const result=await this.required(this.engine(r).run(verb,[...args,...extra]));
    if(verb==='advance'&&!result.state?.active){
      await this.required(this.engine(r).run('release',[]));
      result.state=await this.engine(r).state();
    }
    return result;
  });}
  async chat(message:string, limits:Partial<Pick<Config,'maxOutputTokens'|'maxTurns'|'timeoutMs'|'maxCalls'>>={}) {return this.locked(async()=>{
    const r=await this.run();
    for(const key of ['maxOutputTokens','maxTurns','timeoutMs','maxCalls'] as const){
      const value=limits[key];if(value===undefined)continue;
      if(!Number.isSafeInteger(value)||value<1)throw Error(key+' must be a positive integer');
      r.config[key]=value;
    }
    if(Object.keys(limits).length)await save(join(this.dir,'run.json'),r); const s=await this.engine(r).state();
    if(!s.active)return {text:'Workflow complete',status:await this.status()};
    const phase=s.active.id;
    if(r.artifacts)return this.artifactChat(r,message,s);
    const tools:RuntimeTool[]=[];
    if(phase==='plan')tools.push({name:'propose_plan',description:'Save a bounded implementation and verification plan for human approval. Then stop.',parameters:schema({plan:str}),execute:async({plan}:{plan:string})=>{if(!plan.trim())throw Error('Plan is empty');r.plan=plan;await save(join(this.dir,'run.json'),r);return {saved:true,next:'Wait for human approval through the approve command'};}});
    if(phase==='implement'||phase==='review')tools.push({name:'dispatch_crew',description:`Run the ${phase==='implement'?'implementer':'reviewer'} in its own Pi session and return verified engine result.`,parameters:schema({instructions:str},[]),execute:async(args:{instructions?:string}={})=>this.dispatch(r,phase==='implement'?'implementer':'reviewer',args.instructions)});
    if(phase==='review'&&r.results.reviewer?.verdict==='BLOCK')tools.push({name:'request_repair',description:'Return reviewer findings to implementation within the approved plan. Preserves separate crew sessions and engine history.',parameters:schema({reason:str}),execute:async({reason}:{reason:string})=>this.repairRun(r,reason)});
    const result=await this.call(r,'commander',`You are Constellation Commander. Own the task and delegate implementation and independent review through the supplied tools. Read project guidance as needed. You cannot modify project files directly. Follow the active engine step. Human approval is an external explicit operation; never claim to approve for the human. Overrides exist when the human or a higher-level agent explicitly directs them; ask for that direction when needed. Keep plans and reports short.\nTask: ${r.task}\nApproved/proposed plan: ${r.plan??'none'}\nEngine state: ${JSON.stringify(s)}\nCrew results: ${JSON.stringify(r.results)}`,message,tools,phase);
    return {...result,status:await this.status()};
  });}
  private async call(r:Run,role:Role,systemPrompt:string,prompt:string,tools:RuntimeTool[],stage?:string) {
    return this.accountedCall(r,{role,cwd:r.config.cwd,sessionDir:join(this.dir,'sessions',role),sessionFile:r.sessions[role],stage,model:r.config.model,systemPrompt,prompt,tools,maxOutputTokens:r.config.maxOutputTokens??1024,maxTurns:r.config.maxTurns,timeoutMs:r.config.timeoutMs});
  }
  private async accountedCall(r:Run,input:RuntimePrompt) {
    if(r.calls>=r.config.maxCalls)throw Error(`Run call limit reached (${r.config.maxCalls}); no new model session started`);
    r.calls++;await save(join(this.dir,'run.json'),r);
    try {
      const result=await this.runtime.prompt({...input,onSessionAllocated:async file=>{
        r.sessions[input.role]=file;await save(join(this.dir,'run.json'),r);await input.onSessionAllocated?.(file);
      }});
      r.sessions[input.role]=result.sessionFile;r.cost+=result.usage.cost;await save(join(this.dir,'run.json'),r);return result;
    }catch(error:any){if(error.partial){r.sessions[input.role]=error.partial.sessionFile;r.cost+=error.partial.usage.cost;await save(join(this.dir,'run.json'),r);}throw error;}
  }
  private async verifyFlow(r:Run) {
    const a=r.artifacts!;
    if(a.promptVersion!==COMMANDER_PROMPT_VERSION)throw Error('Commander prompt version changed; use original runtime');
    for(const ref of [a.task,a.original,a.plan,r.results.implementer?.artifact,r.results.reviewer?.artifact,r.repairFindings?.artifact])if(ref)await verifyArtifact(ref);
  }
  private async artifactChat(r:Run,message:string,state:Awaited<ReturnType<Engine['state']>>) {
    await this.verifyFlow(r);
    const a=r.artifacts!,phase=state.active!.id,role:CrewRole=phase==='review'?'reviewer':'implementer';
    const tools:RuntimeTool[]=[];
    if(phase==='plan')tools.push({name:'propose_plan',endInvocation:true,description:'Save the full plan as an artifact, then wait for human approval.',parameters:schema({plan:str}),execute:async({plan}:{plan:string})=>{
      if(!plan.trim())throw Error('Plan is empty');
      a.plan=await writeArtifact(join(this.dir,'artifacts',uniqueName('plan')),plan);r.plan=plan;await save(join(this.dir,'run.json'),r);return {plan:a.plan,next:'Wait for human approval'};
    }});
    if(phase==='implement'||phase==='review'){
      tools.push({name:'write_handoff',description:`Write the complete ${role} Markdown handoff artifact. Include the named result path and all task-specific instructions.`,parameters:schema({content:str}),execute:async({content}:{content:string})=>{
        const parsed=parseHandoff(content,role);
        if(sections(content)['output contract'])throw Error('Output Contract is filled by the controller; omit that section');
        const input=await writeArtifact(join(this.dir,'artifacts',uniqueName(`${role}-handoff`)),content+outputContract(role,parsed.gate,r.config.source));return {input};
      }});
      tools.push({name:'dispatch_crew',endInvocation:true,description:`Dispatch ${role} from its complete handoff file; return only a delivery receipt.`,parameters:schema({input:str}),execute:async(args:{input:string})=>this.dispatchArtifact(r,role,args.input)});
    }
    if(phase==='review'&&r.results.reviewer?.verdict==='BLOCK')tools.push({name:'request_repair',endInvocation:true,description:'Return recorded review findings for repair within the approved plan.',parameters:schema({reason:str}),execute:async({reason}:{reason:string})=>this.repairRun(r,reason)});
    const context=await writeArtifact(join(this.dir,'artifacts',uniqueName('commander-context','json')),JSON.stringify({request:message,task:a.task,original:a.original,plan:a.plan,engine:state,results:r.results,repairFindings:r.repairFindings,crewInvocations:a.bindings,lastDispatch:a.lastDispatch,directions:r.overrides,workingDirectory:r.config.cwd},null,2));
    const result=await this.call(r,'commander',COMMANDER_PROMPT,`Read invocation context at ${context.path}. SHA256: ${context.sha256}.`,tools,phase);
    return {sessionFile:result.sessionFile,usage:result.usage,metrics:result.metrics,context,status:await this.status()};
  }
  private async dispatchArtifact(r:Run,role:CrewRole,input:string) {
    await this.verifyFlow(r);
    const parent=this.engine(r),state=await parent.state(),phase=role==='implementer'?'implement':'review';
    if(state.active?.id!==phase)throw Error(`Dispatch ${role} unavailable at ${state.active?.id}`);
    if(!r.artifacts!.plan)throw Error('No approved plan');
    const a=r.artifacts!,inputPath=resolve(r.config.cwd,input);
    let binding=a.bindings[role];
    if(binding&&binding.input.path!==inputPath)throw Error('Existing crew invocation must resume its recorded handoff');
    if(!binding){
      const text=await readFile(inputPath,'utf8');parseHandoff(text,role);
      const dir=join(this.dir,'crew',`${role}-${a.history.filter(b=>b.role===role).length+1}`);
      await mkdir(join(this.dir,'crew'),{recursive:true});
      await ArtifactInvocation.create(dir,inputPath,r.config,role);
      binding={role,dir,input:{path:inputPath,sha256:hash(text)}};a.bindings[role]=binding;a.history.push(binding);await save(join(this.dir,'run.json'),r);
    }
    const invocation=new ArtifactInvocation(binding.dir,{prompt:input=>this.accountedCall(r,{...input,stage:phase,sessionFile:input.sessionFile??r.sessions[role]})});
    const receipt=await invocation.run(false,{maxCalls:r.config.maxCalls,maxTurns:r.config.maxTurns,timeoutMs:r.config.timeoutMs,maxOutputTokens:r.config.maxOutputTokens});
    a.lastDispatch=await writeArtifact(join(this.dir,'artifacts',uniqueName('crew-receipt','json')),JSON.stringify(receipt,null,2));await save(join(this.dir,'run.json'),r);
    const submitted=receipt.result as Submission;
    if(!submitted.sha256)return {ok:false,status:receipt.status,receipt:a.lastDispatch,invocation:binding.dir,next:'Report the incomplete result and stop; resume the recorded handoff or obtain explicit restart direction'};
    await verifyArtifact(submitted);
    const success=receipt.status==='complete'&&submitted.status==='complete'&&(role==='implementer'||submitted.verdict==='APPROVE');
    // A persisted BLOCK remains evidence even if the provider failed afterward.
    if(receipt.status!=='complete'&&submitted.verdict!=='BLOCK')return {ok:false,status:receipt.status,receipt:a.lastDispatch,result:submitted,invocation:binding.dir,next:'Report incomplete delivery and stop; do not advance or start the next role'};
    const result:CrewResult={verdict:success?(role==='implementer'?'COMPLETE':'APPROVE'):'BLOCK',summary:`${role} ${success?'completed':'requires attention'}; see ${submitted.path}`,evidence:[submitted.path],artifact:submitted};
    r.results[role]=result;await save(join(this.dir,'run.json'),r);
    if(success){await this.evidence(r,role==='reviewer'?'review-result':'crew-result',result);await this.required(parent.run('advance',[phase,'--why',result.summary]));}
    return {ok:success,verdict:result.verdict,result:submitted,receipt:a.lastDispatch,invocation:binding.dir,estimatedCostUsd:receipt.estimatedCostUsd,next:(await parent.state()).active?.id??'complete'};
  }
  private async dispatch(r:Run,role:'implementer'|'reviewer',instructions?:string) {
    const parent=this.engine(r),before=await parent.state();
    const phase=role==='implementer'?'implement':'review';
    if(before.active?.id!==phase)throw Error(`Dispatch ${role} is unavailable at ${before.active?.id}`);
    if(!r.plan)throw Error('No approved plan');
    const path=join(this.dir,`${role}.json`);
    try{await readFile(path);}catch(error:any){if(error.code!=='ENOENT')throw error;await save(path,checklist(`${r.id}/${role}`,true));}
    const child=this.engine(r,role);await this.required(child.run('claim',['--claimed-by',role,'--worktree',r.config.cwd]));
    let result:CrewResult|undefined;
    const tools:RuntimeTool[]=[{name:'finish_crew',description:'Submit your final result with concrete commands, observations and file references as evidence. BLOCK if incomplete.',parameters:schema({verdict:{type:'string',enum:role==='reviewer'?['APPROVE','BLOCK']:['COMPLETE','BLOCK']},summary:str,evidence:{type:'array',items:str,minItems:1}}),execute:async(value:CrewResult)=>{
      if(result)throw Error('Result already submitted');
      if(!value.summary?.trim()||!Array.isArray(value.evidence)||!value.evidence.length||value.evidence.some(e=>typeof e!=='string'||!e.trim()))throw Error('Summary and concrete evidence required');
      if(![role==='reviewer'?'APPROVE':'COMPLETE','BLOCK'].includes(value.verdict))throw Error('Invalid verdict for role');
      result=value;await save(join(this.dir,`${role}-result.json`),value);return {received:true};
    }}];
    const childState=await child.state();
    if(!childState.active){
      const prior:CrewResult=r.results[role]??await json(join(this.dir,`${role}-result.json`));
      if(prior.verdict!==(role==='reviewer'?'APPROVE':'COMPLETE')||!prior.summary?.trim()||!prior.evidence?.length)throw Error('Completed crew has no valid successful result');
      r.results[role]=prior;await save(join(this.dir,'run.json'),r);
      await this.evidence(r,role==='reviewer'?'review-result':'crew-result',prior);
      await this.required(parent.run('advance',[phase,'--why',prior.summary]));
      await this.required(child.run('release',[]));
      return {ok:true,...prior,recovered:true,next:await parent.state()};
    }
    if(childState.active.status==='pending')await this.required(child.run('start',['work']));
    try{
      await this.call(r,role,`You are Constellation ${role}. Work only on this bounded task. Working directory: ${r.config.cwd}. Read the project instructions at ${join(r.config.cwd,'AGENTS.md')} and referenced guidance before work. ${role==='reviewer'?'Independently inspect the implementation and run relevant checks. Do not edit project files. Approve only if the task and approved plan are satisfied.':'Implement the approved plan and run relevant checks.'} Call finish_crew with concrete evidence. Use BLOCK for incomplete work.\nTask: ${r.task}\nPlan: ${r.plan}\nReviewer findings to address: ${JSON.stringify(r.repairFindings??null)}\nImplementation result: ${JSON.stringify(r.results.implementer??null)}\nCommander handoff: ${instructions??'Follow the approved plan.'}\nYour checklist: ${JSON.stringify(childState)}`,'Perform your handoff now.',tools,phase);
    }catch(error:any){
      if(result?.verdict==='BLOCK'){
        r.results[role]=result;await save(join(this.dir,'run.json'),r);
        return {ok:false,...result,interrupted:error.message,next:'Resolve the recorded blocker before retrying'};
      }
      throw error;
    }
    if(!result)throw Error(`${role} stopped without submitting finish_crew; saved session can be resumed`);
    r.results[role]=result;await save(join(this.dir,'run.json'),r);
    if(result.verdict==='BLOCK')return {ok:false,...result,next:'Report the blocker; obtain explicit recovery direction'};
    await this.evidence(r,'crew-result',result,role);await this.required(child.run('advance',['work','--why',result.summary]));await this.required(child.run('release',[]));
    await this.evidence(r,role==='reviewer'?'review-result':'crew-result',result);
    await this.required(parent.run('advance',[phase,'--why',result.summary]));
    return {ok:true,...result,next:await parent.state()};
  }
}
