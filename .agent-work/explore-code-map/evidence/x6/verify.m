function verify()
% verify.m -- print per-entity detail for 3 files so the counts can be checked by hand
% against the source, and settle the ANON parameter question.
ev  = 'C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x6';
src = 'C:\Programs\superCoolSpaceSim\matlab_src';
diary(fullfile(ev,'verify_log.txt'));

targets = { fullfile(src,'unit_tests','TestRecordingIntegrator.m'), ...
            fullfile(src,'core','+contractspec','software.m'), ...
            fullfile(src,'subsystems','SolarArray.m') };

for ti = 1:numel(targets)
    fp = targets{ti};
    fprintf('\n================ %s ================\n', strrep(fp,[src filesep],''));
    t = mtree(fp,'-file');
    fprintf('FileType: %s\n', char(t.FileType));

    mts = mtfind(t,'Kind','METHODS'); mix = indices(mts);
    mL=zeros(numel(mix),1); mR=zeros(numel(mix),1);
    for j=1:numel(mix), n=select(t,mix(j)); mL(j)=lefttreepos(n); mR(j)=righttreepos(n); end
    fprintf('METHODS blocks: %d   PROPERTIES blocks: %d\n', numel(mix), numel(indices(mtfind(t,'Kind','PROPERTIES'))));

    % properties, listed
    pbs = mtfind(t,'Kind','PROPERTIES'); pix=indices(pbs);
    for j=1:numel(pix)
        st = Body(select(t,pix(j))); k=0;
        fprintf('  properties block #%d (line %d):', j, lineno(select(t,pix(j))));
        while ~isnull(st)
            nm = bn(st);
            if ~isempty(nm), k=k+1; fprintf(' %s', nm); end
            st = Next(st);
        end
        fprintf('   [%d names]\n', k);
    end

    % functions, classified
    fns = mtfind(t,'Kind','FUNCTION'); fix=indices(fns); nfn=numel(fix);
    fL=zeros(nfn,1); fR=zeros(nfn,1); nm=cell(nfn,1);
    for j=1:nfn
        n=select(t,fix(j)); fL(j)=lefttreepos(n); fR(j)=righttreepos(n);
        fh=Fname(n); nm{j}=''; if ~isnull(fh), nm{j}=stringval(fh); end
    end
    fprintf('FUNCTION nodes: %d\n', nfn);
    for j=1:min(nfn,40)
        inM = any(fL(j)>=mL & fR(j)<=mR);
        nest=false; for q=1:nfn, if q~=j && fL(j)>fL(q) && fR(j)<=fR(q), nest=true; break; end, end
        if inM && ~nest, c='method'; elseif nest, c='nested'; elseif j==1 && strcmp(char(t.FileType),'FunctionFile'), c='main'; else, c='subfunction'; end
        n=select(t,fix(j));
        ni=0; p=Ins(n);  while ~isnull(p), ni=ni+1; p=Next(p); end
        no=0; o=Outs(n);  while ~isnull(o), no=no+1; o=Next(o); end
        fprintf('  line %-5d %-12s %-34s in=%d out=%d\n', lineno(n), c, nm{j}, ni, no);
    end
    if nfn>40, fprintf('  ... (%d more)\n', nfn-40); end
end

% ---- settle the ANON parameter question on a file that has one ----
fprintf('\n================ ANON structure hunt ================\n');
L = dir(fullfile(src,'**','*.m'));
found = 0;
for i=1:numel(L)
    t = mtree(fullfile(L(i).folder,L(i).name),'-file');
    a = mtfind(t,'Kind','ANON'); aix=indices(a);
    if isempty(aix), continue; end
    fprintf('file: %s\n', strrep(fullfile(L(i).folder,L(i).name),[src filesep],''));
    for j=1:min(3,numel(aix))
        n = select(t,aix(j));
        fprintf('  ANON line %d text=%s\n', lineno(n), strtrim(tree2str(n)));
        for acc = {'Left','Right','Ins','Outs','Arg','Body'}
            v = feval(acc{1}, n);
            if isnull(v), fprintf('    %-6s = <null>\n', acc{1});
            else
                s=''; try, s=strtrim(tree2str(v)); catch, end
                fprintf('    %-6s = %-10s %s\n', acc{1}, char(kind(v)), s);
            end
        end
        % walk the Left chain as a list
        p = Left(n); c=0; nms={};
        while ~isnull(p), c=c+1; if strcmp(char(kind(p)),'ID'), nms{end+1}=stringval(p); end, p=Next(p); end %#ok<AGROW>
        fprintf('    Left-as-list: %d node(s), IDs: %s\n', c, strjoin(nms,','));
    end
    found = found+1;
    if found>=2, break; end
end
diary off;
fprintf('VERIFY_DONE\n');
end

function nm = bn(n)
    nm=''; d=0;
    while ~isnull(n) && d<8
        switch char(kind(n))
            case 'ID', nm=stringval(n); return
            case {'DOT','SUBSCR','CELLINDEX','LP','PROPTYPEDECL','EQUALS','ATTR','ATBASE'}
                n=Left(n);
            otherwise, return
        end
        d=d+1;
    end
end
