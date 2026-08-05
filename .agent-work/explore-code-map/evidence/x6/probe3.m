function probe3()
% probe3.m -- dump the exact node structure of a typed properties block and an ANON,
% so the name extraction can be fixed correctly rather than guessed.
ev  = 'C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x6';
src = 'C:\Programs\superCoolSpaceSim\matlab_src';
diary(fullfile(ev,'probe3_log.txt'));

t = mtree(fullfile(src,'subsystems','SolarArray.m'),'-file');
pbs = mtfind(t,'Kind','PROPERTIES'); pix = indices(pbs);
for j = 1:numel(pix)
    pb = select(t,pix(j));
    fprintf('\n=== PROPERTIES block #%d (line %d) ===\n', j, lineno(pb));
    st = Body(pb); c = 0;
    while ~isnull(st) && c < 6
        c = c+1;
        txt='<tree2str FAILED>'; try, txt=strtrim(tree2str(st)); catch, end
        fprintf('  stmt#%d kind=%-14s line=%-4d text=%s\n', c, char(kind(st)), lineno(st), txt);
        for acc = {'Left','Right','Arg','Index','Ins','Outs','Body','Attr','Cattr','Fname','List','Vector'}
            v = [];
            try, v = feval(acc{1}, st); catch, continue; end
            if isempty(v) || isnull(v), continue; end
            s='<n/a>'; try, s=strtrim(tree2str(v)); catch, end
            sv='';
            if strcmp(char(kind(v)),'ID'), try, sv=[' stringval=' stringval(v)]; catch, end, end
            fprintf('      %-6s -> %-14s %s%s\n', acc{1}, char(kind(v)), s, sv);
        end
        st = Next(st);
    end
end

fprintf('\n=== ANONID count check ===\n');
L = dir(fullfile(src,'**','*.m'));
nAnon=0; nAnonId=0;
for i=1:numel(L)
    tt = mtree(fullfile(L(i).folder,L(i).name),'-file');
    nAnon   = nAnon   + numel(indices(mtfind(tt,'Kind','ANON')));
    nAnonId = nAnonId + numel(indices(mtfind(tt,'Kind','ANONID')));
end
fprintf('ANON %d  ANONID %d\n', nAnon, nAnonId);

fprintf('\n=== corpus-wide PROPTYPEDECL / property-statement census ===\n');
nPTD=0; nStmt=0; nEq=0; nId=0; nOther=0; otherKinds=containers.Map();
for i=1:numel(L)
    tt = mtree(fullfile(L(i).folder,L(i).name),'-file');
    nPTD = nPTD + numel(indices(mtfind(tt,'Kind','PROPTYPEDECL')));
    pb2 = mtfind(tt,'Kind','PROPERTIES'); p2 = indices(pb2);
    for j=1:numel(p2)
        st = Body(select(tt,p2(j)));
        while ~isnull(st)
            nStmt = nStmt+1;
            k = char(kind(st));
            switch k
                case 'PROPTYPEDECL', nPTDstmt=1; %#ok<NASGU>
                case 'EQUALS', nEq=nEq+1;
                case 'ID', nId=nId+1;
                otherwise
                    if ~strcmp(k,'PROPTYPEDECL')
                        nOther=nOther+1;
                        if isKey(otherKinds,k), otherKinds(k)=otherKinds(k)+1; else, otherKinds(k)=1; end
                    end
            end
            st = Next(st);
        end
    end
end
fprintf('PROPERTY_STATEMENTS %d   of which EQUALS %d, bare ID %d, other %d\n', nStmt, nEq, nId, nOther);
fprintf('PROPTYPEDECL_NODES_TOTAL %d\n', nPTD);
kk=keys(otherKinds);
for i=1:numel(kk), fprintf('  otherstmt %-16s %d\n', kk{i}, otherKinds(kk{i})); end

diary off;
fprintf('PROBE3_DONE\n');
end
