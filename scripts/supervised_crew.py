"""Durable registry seam for hosts supervising their own bound role sessions.

No model/provider/CLI launching lives here. The host owns allocation and resume;
this module reuses shared identity, duplicate, registry and completion contracts.
"""
from pathlib import Path
import run_crew


def begin(*, root, work_id, gate, role, job_id, parent, worktree, handoff, result, spine, model, pid, resume=None):
    root=Path(root)
    entries=run_crew.load_registry(run_crew.registry_path(work_id,root))
    if resume:
        entry=run_crew.find_entry(entries,resume)
        if entry is None or entry.get('supervised_job')!=job_id:
            raise run_crew.CrewLaunchError('No matching supervised assignment to resume')
        def update(e):
            e.update(status='running',pid=pid,last_heartbeat=run_crew._now())
            return True
        _,entry,_=run_crew.mutate_registry_entry(run_crew.registry_path(work_id,root),resume,update)
        return entry
    duplicate=run_crew.active_duplicate(entries,work_id,gate,role,worktree)
    if duplicate:
        raise run_crew.CrewLaunchError('Unresolved crew assignment; resume or explicitly abandon it')
    attempt=run_crew.next_attempt(entries,work_id,gate,role,worktree)
    entry=run_crew.build_entry(work_id=work_id,gate=gate,role=role,attempt=attempt,worktree=worktree,handoff=handoff,result=result,root=root,started=run_crew._now(),backend='supervised',pid=pid,dispatch='supervised',model=model,spine=spine,parent=parent)
    entry.update(door_bound=bool(spine),supervised_job=job_id,resumable=True)
    run_crew.append_registry_entry(run_crew.registry_path(work_id,root),entry)
    return entry


def finish(*,root,work_id,session,delivered):
    root=Path(root)
    def update(entry):
        if delivered:
            if entry.get('spine') and not run_crew.spine_terminal(entry['spine'],root):
                raise run_crew.CrewLaunchError('Supervised role checklist is not terminal')
            if not run_crew.result_fresh(entry['result'],root,since=entry['started_at']):
                raise run_crew.CrewLaunchError('Supervised result is absent/stale')
        entry.update(status='completed' if delivered else 'resumable',pid=None,last_heartbeat=run_crew._now())
        if delivered:entry['completed_at']=run_crew._now()
        return delivered
    _,entry,_=run_crew.mutate_registry_entry(run_crew.registry_path(work_id,root),session,update)
    return entry
