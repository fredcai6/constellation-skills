% extract2.m -- corrected extraction. Fixes vs extract.m:
%   1. FUNCTION classification by METHODS/FUNCTION *span containment*, not Parent-walking
%      (mtree's Parent on a list element returns the PREVIOUS SIBLING, so only the first
%       method in each block was ever classified as a method).
%   2. Qualified calls: obj.m(...) / pkg.f(...) / Class.s(...) parse as SUBSCR over DOT,
%      never as CALL. Extract and resolve those separately.
%   3. Anonymous-function parameters read from Left, not Ins.
%   4. Resolve callees to defining files -> directory-level dependency edges.
% READ-ONLY over the target. All output -> evidence dir.
function extract2()

ev  = 'C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x6';
src = 'C:\Programs\superCoolSpaceSim\matlab_src';
diary(fullfile(ev,'extract3_log.txt'));
tStart = tic;

L = dir(fullfile(src,'**','*.m'));
nF = numel(L);
fprintf('FILES %d\n', nF);

% ---------- pass 0: build the name -> defining-file resolution tables ----------
pkgDirs = containers.Map('KeyType','char','ValueType','double');
dd = dir(fullfile(src,'**'));
for i=1:numel(dd)
    if dd(i).isdir && startsWith(dd(i).name,'+')
        p = dd(i).name(2:end);
        pkgDirs(p) = 1;
    end
end

classFile = containers.Map('KeyType','char','ValueType','any');   % ClassName -> relfile
funcFile  = containers.Map('KeyType','char','ValueType','any');   % file-scope function name -> relfile
stemFile  = containers.Map('KeyType','char','ValueType','any');
relOf = cell(nF,1); dirOf = cell(nF,1); ftOf = cell(nF,1);

for i = 1:nF
    fp  = fullfile(L(i).folder, L(i).name);
    rel = strrep(fp, [src filesep], '');
    relOf{i} = rel;
    d = fileparts(rel); if isempty(d), d = '<root>'; end
    dirOf{i} = d;
    [~,stem,~] = fileparts(L(i).name);
    stemFile(stem) = rel;
    try
        t = mtree(fp,'-file');
        ftOf{i} = char(t.FileType);
        if strcmp(ftOf{i},'ClassDefinitionFile')
            cn = mtfind(t,'Kind','CLASSDEF'); cix = indices(cn);
            if ~isempty(cix)
                ce = Cexpr(select(t,cix(1)));
                nm = '';
                if strcmp(char(kind(ce)),'ID'), nm = stringval(ce);
                else
                    lf = Left(ce);
                    if ~isnull(lf) && strcmp(char(kind(lf)),'ID'), nm = stringval(lf); end
                end
                if ~isempty(nm), classFile(nm) = rel; end
            end
        else
            funcFile(stem) = rel;   % MATLAB resolves a function file by its FILENAME
        end
    catch
        ftOf{i} = 'ParseError';
    end
end
fprintf('PKG_DIRS %d  CLASSES %d  FUNCTION_FILES %d\n', double(pkgDirs.Count), double(classFile.Count), double(funcFile.Count));

% ---------- accumulators ----------
S = struct();
S.files = nF;
S.filetype = struct('ScriptFile',0,'FunctionFile',0,'ClassDefinitionFile',0);
S.parse_failures = 0;
S.tx = struct('script',0,'main_function',0,'subfunction',0,'nested_function',0, ...
              'method',0,'property_accessor',0,'anon_function',0);
S.co = struct('input_param',0,'output_param',0,'property',0,'property_typed',0, ...
              'persistent',0,'global',0, ...
              'local_assigned_distinct',0,'loop_var',0,'anon_param',0);
S.classdefs = 0; S.methods_blocks = 0; S.properties_blocks = 0;
S.ed = struct('bare_call_sites',0,'qualified_call_sites',0,'subscr_total',0, ...
              'dot_total',0,'id_occurrences',0,'write_occurrences',0,'read_occurrences',0);
S.qual = struct('to_class_static',0,'to_package_function',0,'on_local_variable_UNRESOLVED',0, ...
                'on_unknown_base',0);

defNames  = containers.Map('KeyType','char','ValueType','double');
calleeCnt = containers.Map('KeyType','char','ValueType','double');
pairSet   = containers.Map('KeyType','char','ValueType','double');
dirEdges  = containers.Map('KeyType','char','ValueType','double');
propNames = containers.Map('KeyType','char','ValueType','double');
edgeRows  = {};
perFile   = cell(nF,1);
failures  = {};

for i = 1:nF
    fp = fullfile(L(i).folder, L(i).name);
    rel = relOf{i}; myDir = dirOf{i};
    try
        t = mtree(fp,'-file');
    catch ME
        S.parse_failures = S.parse_failures+1;
        failures{end+1} = sprintf('%s :: %s', rel, ME.message); %#ok<SAGROW>
        continue
    end
    ft = char(t.FileType);
    if isfield(S.filetype, ft), S.filetype.(ft) = S.filetype.(ft)+1; end
    if strcmp(ft,'ScriptFile'), S.tx.script = S.tx.script+1; end

    S.classdefs        = S.classdefs        + numel(indices(mtfind(t,'Kind','CLASSDEF')));
    S.ed.dot_total     = S.ed.dot_total     + numel(indices(mtfind(t,'Kind','DOT')));
    S.ed.subscr_total  = S.ed.subscr_total  + numel(indices(mtfind(t,'Kind','SUBSCR')));
    S.ed.id_occurrences= S.ed.id_occurrences+ numel(indices(mtfind(t,'Kind','ID')));

    % ---- METHODS block spans ----
    mts = mtfind(t,'Kind','METHODS'); mix = indices(mts);
    S.methods_blocks = S.methods_blocks + numel(mix);
    mL = zeros(numel(mix),1); mR = zeros(numel(mix),1);
    for j=1:numel(mix)
        n = select(t,mix(j)); mL(j)=lefttreepos(n); mR(j)=righttreepos(n);
    end

    % ---- position -> ID name table (needed because PROPTYPEDECL hides its name:
    %      `joint_id double = 0` is EQUALS(Left=PROPTYPEDECL, Right=INT) and no
    %      accessor on PROPTYPEDECL returns the identifier. MATLAB's own tree2str
    %      also throws "unknown expr node PROPTYPEDECL" on it.) ----
    idAt = containers.Map('KeyType','double','ValueType','any');
    idn = mtfind(t,'Kind','ID'); idix = indices(idn);
    for j=1:numel(idix)
        n = select(t,idix(j));
        idAt(position(n)) = stringval(n);
    end
    idPos = sort(cell2mat(keys(idAt)));

    % ---- properties ----
    pbs = mtfind(t,'Kind','PROPERTIES'); pix = indices(pbs);
    S.properties_blocks = S.properties_blocks + numel(pix);
    for j=1:numel(pix)
        st = Body(select(t,pix(j)));
        while ~isnull(st)
            nm = baseName(st);
            if isempty(nm)
                % typed declaration: take the leftmost identifier of the statement
                nm = firstIdAt(lefttreepos(st), idPos, idAt);
                if ~isempty(nm), S.co.property_typed = S.co.property_typed+1; end
            end
            if ~isempty(nm)
                S.co.property = S.co.property+1;
                if isKey(propNames,nm), propNames(nm)=propNames(nm)+1; else, propNames(nm)=1; end
            end
            st = Next(st);
        end
    end

    % ---- persistent / global ----
    for kx = {'PERSISTENT','GLOBAL'}
        gs = mtfind(t,'Kind',kx{1}); gix = indices(gs);
        for j=1:numel(gix)
            gn = select(t,gix(j)); v = Arg(gn);
            if isnull(v), v = Body(gn); end
            c = 0;
            while ~isnull(v)
                if strcmp(char(kind(v)),'ID'), c=c+1; end
                v = Next(v);
            end
            if c==0, c=1; end
            if strcmp(kx{1},'PERSISTENT'), S.co.persistent=S.co.persistent+c;
            else, S.co.global=S.co.global+c; end
        end
    end

    % ---- anonymous functions (params via Left) ----
    % anon params are ANONID nodes, not ID nodes
    an = mtfind(t,'Kind','ANON'); aix = indices(an);
    S.tx.anon_function = S.tx.anon_function + numel(aix);
    S.co.anon_param = S.co.anon_param + numel(indices(mtfind(t,'Kind','ANONID')));

    % ---- FUNCTION nodes: spans, names, params, classification ----
    fns = mtfind(t,'Kind','FUNCTION'); fix = indices(fns); nfn = numel(fix);
    fL = zeros(nfn,1); fR = zeros(nfn,1); fname = cell(nfn,1); fcls = cell(nfn,1);
    for j=1:nfn
        n = select(t,fix(j));
        fL(j)=lefttreepos(n); fR(j)=righttreepos(n);
        nm=''; fh = Fname(n);
        if ~isnull(fh), nm = stringval(fh); end
        fname{j}=nm;
        if ~isempty(nm)
            if isKey(defNames,nm), defNames(nm)=defNames(nm)+1; else, defNames(nm)=1; end
        end
        p = Ins(n);
        while ~isnull(p), S.co.input_param=S.co.input_param+1; p=Next(p); end
        o = Outs(n);
        while ~isnull(o), S.co.output_param=S.co.output_param+1; o=Next(o); end
    end
    % classify by span containment
    for j=1:nfn
        inMethods = any(fL(j)>=mL & fR(j)<=mR);
        nested = false;
        for q=1:nfn
            if q~=j && fL(j)>fL(q) && fR(j)<=fR(q), nested=true; break; end
        end
        if inMethods && ~nested
            if contains(fname{j},'.')   % get.X / set.X property accessors
                fcls{j}='property_accessor'; S.tx.property_accessor=S.tx.property_accessor+1;
            else
                fcls{j}='method'; S.tx.method=S.tx.method+1;
            end
        elseif nested
            fcls{j}='nested_function'; S.tx.nested_function=S.tx.nested_function+1;
        elseif j==1 && strcmp(ft,'FunctionFile')
            fcls{j}='main_function'; S.tx.main_function=S.tx.main_function+1;
        else
            fcls{j}='subfunction'; S.tx.subfunction=S.tx.subfunction+1;
        end
    end

    % ---- locals + writes (also builds the per-function name scope) ----
    scope = containers.Map('KeyType','char','ValueType','double');  % "fnIdx|name"
    eqs = mtfind(t,'Kind','EQUALS'); eix = indices(eqs);
    for j=1:numel(eix)
        en = select(t,eix(j)); lhsn = Left(en); names={};
        if ~isnull(lhsn) && strcmp(char(kind(lhsn)),'LB')
            v = Arg(lhsn); if isnull(v), v=Body(lhsn); end
            while ~isnull(v)
                nm=baseName(v); if ~isempty(nm), names{end+1}=nm; end %#ok<SAGROW>
                v=Next(v);
            end
        else
            nm=baseName(lhsn); if ~isempty(nm), names{end+1}=nm; end
        end
        S.ed.write_occurrences = S.ed.write_occurrences + max(1,numel(names));
        fi = encl(position(en), fL, fR);
        for q=1:numel(names)
            k = sprintf('%d|%s', fi, names{q});
            if ~isKey(scope,k), scope(k)=1; end
        end
    end
    frs = mtfind(t,'Kind','FOR'); frix = indices(frs);
    for j=1:numel(frix)
        n = select(t,frix(j)); iv = Index(n);
        if isnull(iv), continue; end
        nm = baseName(iv);
        if ~isempty(nm)
            S.co.loop_var = S.co.loop_var+1;
            S.ed.write_occurrences = S.ed.write_occurrences+1;
            k = sprintf('%d|%s', encl(position(n), fL, fR), nm);
            if ~isKey(scope,k), scope(k)=1; end
        end
    end
    % parameters belong to the scope too
    for j=1:nfn
        n = select(t,fix(j));
        for acc = {'Ins','Outs'}
            if strcmp(acc{1},'Ins'), p=Ins(n); else, p=Outs(n); end
            while ~isnull(p)
                if strcmp(char(kind(p)),'ID')
                    k = sprintf('%d|%s', j, stringval(p));
                    if ~isKey(scope,k), scope(k)=1; end
                end
                p = Next(p);
            end
        end
    end
    S.co.local_assigned_distinct = S.co.local_assigned_distinct + double(scope.Count);

    % ---- bare calls: CALL with Left = ID ----
    cs = mtfind(t,'Kind','CALL'); cix = indices(cs);
    for j=1:numel(cix)
        n = select(t,cix(j)); lf = Left(n);
        if isnull(lf) || ~strcmp(char(kind(lf)),'ID'), continue; end
        nm = stringval(lf);
        S.ed.bare_call_sites = S.ed.bare_call_sites+1;
        recordCallee(nm);
        fi = encl(position(n), fL, fR);
        emit(rel, myDir, fi, fname, nm, 'bare');
    end

    % ---- qualified calls: SUBSCR whose Left is a DOT ----
    ss = mtfind(t,'Kind','SUBSCR'); six = indices(ss);
    for j=1:numel(six)
        n = select(t,six(j)); lf = Left(n);
        if isnull(lf) || ~strcmp(char(kind(lf)),'DOT'), continue; end
        base = baseName(Left(lf));
        memb = '';
        rt = Right(lf);
        if ~isnull(rt), memb = stringval(rt); end
        if isempty(base) || isempty(memb), continue; end
        S.ed.qualified_call_sites = S.ed.qualified_call_sites+1;
        fi = encl(position(n), fL, fR);
        inScope = isKey(scope, sprintf('%d|%s', fi, base));
        full = [base '.' memb];
        if inScope
            S.qual.on_local_variable_UNRESOLVED = S.qual.on_local_variable_UNRESOLVED+1;
        elseif isKey(classFile, base)
            S.qual.to_class_static = S.qual.to_class_static+1;
            recordCallee(full); emit(rel, myDir, fi, fname, base, 'static');
        elseif isKey(pkgDirs, base)
            S.qual.to_package_function = S.qual.to_package_function+1;
            recordCallee(full); emit(rel, myDir, fi, fname, [base '.' memb], 'package');
        else
            S.qual.on_unknown_base = S.qual.on_unknown_base+1;
        end
    end

    perFile{i} = struct('file',rel,'filetype',ft,'functions',nfn, ...
                        'methods',sum(strcmp(fcls,'method')),'locals',double(scope.Count));
end

S.ed.read_occurrences = S.ed.id_occurrences - S.ed.write_occurrences;
S.tx.total_named = S.tx.script + S.tx.main_function + S.tx.subfunction + ...
                   S.tx.nested_function + S.tx.method + S.tx.property_accessor;
S.co.total_named = S.co.input_param + S.co.output_param + S.co.property + ...
                   S.co.persistent + S.co.global;

% resolve internal vs external for bare calls
nInt=0; nExt=0; dI=containers.Map(); dE=containers.Map();
ck = keys(calleeCnt);
for i=1:numel(ck)
    nm=ck{i}; c=calleeCnt(nm);
    root = nm; k = strfind(nm,'.'); if ~isempty(k), root = nm(1:k(1)-1); end
    if isKey(classFile,root)||isKey(funcFile,root)||isKey(stemFile,root)||isKey(pkgDirs,root)
        nInt=nInt+c; dI(nm)=1;
    else
        nExt=nExt+c; dE(nm)=1;
    end
end
S.calls = struct('internal_occurrences',nInt,'external_occurrences',nExt, ...
                 'distinct_internal_targets',double(dI.Count), ...
                 'distinct_external_targets',double(dE.Count), ...
                 'distinct_caller_callee_pairs',double(pairSet.Count), ...
                 'distinct_directory_edges',double(dirEdges.Count));
S.distinct_defined_names = double(defNames.Count);
S.distinct_property_names = double(propNames.Count);
S.packages = double(pkgDirs.Count);
S.classes  = double(classFile.Count);
S.elapsed_seconds = toc(tStart);
S.failures = failures;

fid=fopen(fullfile(ev,'summary3.json'),'w'); fprintf(fid,'%s',jsonencode(S,'PrettyPrint',true)); fclose(fid);
pf = perFile(~cellfun(@isempty,perFile));
fid=fopen(fullfile(ev,'per_file3.json'),'w'); fprintf(fid,'%s',jsonencode([pf{:}],'PrettyPrint',true)); fclose(fid);
fid=fopen(fullfile(ev,'call_edges3.tsv'),'w'); fprintf(fid,'file\tenclosing\tcallee\tkind\n');
for i=1:size(edgeRows,1), fprintf(fid,'%s\t%s\t%s\t%s\n', edgeRows{i,:}); end
fclose(fid);
dk = keys(dirEdges); dv = cell2mat(values(dirEdges)); [~,o]=sort(dv,'descend');
fid=fopen(fullfile(ev,'dir_edges3.txt'),'w');
for i=1:numel(o), fprintf(fid,'%-6d %s\n', dv(o(i)), dk{o(i)}); end
fclose(fid);
ck2=keys(calleeCnt); cv2=cell2mat(values(calleeCnt)); [~,o2]=sort(cv2,'descend');
fid=fopen(fullfile(ev,'top_callees3.txt'),'w');
for i=1:min(70,numel(o2))
    nm=ck2{o2(i)}; root=nm; k=strfind(nm,'.'); if ~isempty(k), root=nm(1:k(1)-1); end
    if isKey(classFile,root)||isKey(funcFile,root)||isKey(stemFile,root)||isKey(pkgDirs,root), tg='INTERNAL'; else, tg='EXTERNAL'; end
    fprintf(fid,'%-9s %-40s %d\n', tg, nm, cv2(o2(i)));
end
fclose(fid);

disp(jsonencode(S,'PrettyPrint',true));
fprintf('\n--- top 25 directory edges ---\n');
for i=1:min(25,numel(o)), fprintf('%-6d %s\n', dv(o(i)), dk{o(i)}); end
diary off;
fprintf('EXTRACT2_DONE %.2fs\n', S.elapsed_seconds);

% ================= helpers =================
    function recordCallee(nm)
        if isKey(calleeCnt,nm), calleeCnt(nm)=calleeCnt(nm)+1; else, calleeCnt(nm)=1; end
    end
    function emit(relf, dsrc, fi, fnames, callee, kindTag)
        e = '<file-level>';
        if fi>0 && ~isempty(fnames{fi}), e = fnames{fi}; end
        pk = sprintf('%s::%s->%s', relf, e, callee);
        if ~isKey(pairSet,pk)
            pairSet(pk)=1;
            edgeRows(end+1,:) = {relf, e, callee, kindTag}; %#ok<AGROW>
        end
        % directory-level edge, resolved through the defining file
        root = callee; kk2 = strfind(callee,'.'); if ~isempty(kk2), root = callee(1:kk2(1)-1); end
        tgt = '';
        if isKey(classFile,root), tgt = classFile(root);
        elseif isKey(funcFile,root), tgt = funcFile(root);
        elseif isKey(stemFile,root), tgt = stemFile(root);
        end
        if isempty(tgt), return; end
        dt = fileparts(tgt); if isempty(dt), dt = '<root>'; end
        if strcmp(dt,dsrc), return; end
        de = sprintf('%s -> %s', dsrc, dt);
        if isKey(dirEdges,de), dirEdges(de)=dirEdges(de)+1; else, dirEdges(de)=1; end
    end
end

function nm = baseName(n)
    nm=''; d=0;
    while ~isnull(n) && d<8
        switch char(kind(n))
            case 'ID', nm=stringval(n); return
            case {'DOT','SUBSCR','CELLINDEX','LP','PROPTYPEDECL','EQUALS','ATTR','ATBASE'}
                n = Left(n);
            otherwise, return
        end
        d=d+1;
    end
end

function nm = firstIdAt(pos, idPos, idAt)
% leftmost identifier at or after character position `pos`
    nm = '';
    k = find(idPos >= pos, 1, 'first');
    if isempty(k), return; end
    nm = idAt(idPos(k));
end

function idx = encl(pos, fL, fR)
    idx=0; best=inf;
    for q=1:numel(fL)
        if pos>=fL(q) && pos<=fR(q)
            w=fR(q)-fL(q);
            if w<best, best=w; idx=q; end
        end
    end
end
