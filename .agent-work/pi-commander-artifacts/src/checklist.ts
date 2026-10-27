const phases = ['plan', 'implement', 'review', 'accept'];
export function checklist(id: string, crew = false) {
  const items = crew ? ['work'] : phases;
  return {work_id:id,type:'gated',config:{},items,tasks:Object.fromEntries(items.map(name=>[name,{
    id:name,title:name,imperative: crew ? 'Perform the bounded handoff. Call finish_crew with an honest verdict and concrete evidence.' : ({plan:'Propose a bounded plan, then wait for human approval.',implement:'Dispatch a Pi implementer with the approved plan.',review:'Dispatch a separate Pi reviewer. A BLOCK requires repair or an explicit override.',accept:'Present the result and wait for human acceptance.'}[name]),
    status:'pending',preconditions:[],postconditions:[{id:'evidence',statement:'Required result or explicit human decision is recorded',check:{kind:'artifact',evidence_type:crew?'crew-result':name==='plan'||name==='accept'?'user-decision':name==='review'?'review-result':'crew-result',...(name==='review'?{match:{verdict:'APPROVE'}}:{})},satisfied:false,override_policy:{allowed:true,reason_required:true}}],constraints:[],directives:null,child_checklist:null,result:null,finding:null,evidence:[],rework_count:0,status_detail:{}
  }]))};
}
