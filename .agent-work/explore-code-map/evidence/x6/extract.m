% extract.m -- full container/transformer/edge extraction from matlab_src via mtree.
% READ-ONLY over the target: mtree(...,'-file') only reads. All output -> evidence dir.
ev  = 'C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x6';
src = 'C:\Programs\superCoolSpaceSim\matlab_src';

diary(fullfile(ev,'extract_log.txt'));
tStart = tic;
L = dir(fullfile(src,'**','*.m'));
nF = numel(L);
fprintf('FILES %d\n', nF);

% ---------- accumulators ----------
S = struct();
S.files = nF;
S.filetype = struct('ScriptFile',0,'FunctionFile',0,'ClassDefinitionFile',0,'Other',0);
S.parse_failures = 0;

% transformers
S.tx = struct('main_function',0,'subfunction',0,'nested_function',0, ...
              'method',0,'script',0,'anon_function',0);
S.classdefs = 0;
S.methods_blocks = 0;
S.properties_blocks = 0;

% containers
S.co = struct('input_param',0,'output_param',0,'property',0, ...
              'persistent',0,'global',0,'local_assigned_distinct',0, ...
              'loop_var',0,'anon_capture_param',0);
S.varargin = 0; S.varargout = 0;

% edges / occurrences
S.ed = struct('call_sites',0,'dot_method_or_field',0,'subscr',0, ...
              'write_occurrences',0,'id_occurrences',0);

% name tables
defFuncNames  = containers.Map('KeyType','char','ValueType','double'); % all defined transformer names
classNames    = containers.Map('KeyType','char','ValueType','double');
fileStems     = containers.Map('KeyType','char','ValueType','double');
calleeCount   = containers.Map('KeyType','char','ValueType','double');
fieldCount    = containers.Map('KeyType','char','ValueType','double');
propNames     = containers.Map('KeyType','char','ValueType','double');

callerCalleePairs = containers.Map('KeyType','char','ValueType','double'); % "file::fn -> callee"
fileCalleeRaw     = {};   % rows: {relfile, enclosing_fn, callee}
perFile = cell(nF,1);
failures = {};

% ---------- helpers ----------
listNames = @(n) n; %#ok<NASGU>

for i = 1:nF
    fp  = fullfile(L(i).folder, L(i).name);
    rel = strrep(fp, [src filesep], '');
    [~,stem,~] = fileparts(L(i).name);
    if isKey(fileStems,stem), fileStems(stem)=fileStems(stem)+1; else, fileStems(stem)=1; end
    try
        t = mtree(fp, '-file');
    catch ME
        S.parse_failures = S.parse_failures + 1;
        failures{end+1} = sprintf('%s :: %s', rel, ME.message); %#ok<SAGROW>
        continue
    end

    ft = char(t.FileType);
    switch ft
        case 'ScriptFile',           S.filetype.ScriptFile = S.filetype.ScriptFile+1; S.tx.script = S.tx.script+1;
        case 'FunctionFile',         S.filetype.FunctionFile = S.filetype.FunctionFile+1;
        case 'ClassDefinitionFile',  S.filetype.ClassDefinitionFile = S.filetype.ClassDefinitionFile+1;
        otherwise,                   S.filetype.Other = S.filetype.Other+1;
    end

    fRec = struct('file',rel,'filetype',ft,'functions',0,'methods',0,'properties',0, ...
                  'locals',0,'calls',0);

    % ===== classdef =====
    cds = mtfind(t,'Kind','CLASSDEF');
    cix = indices(cds);
    for j = 1:numel(cix)
        S.classdefs = S.classdefs + 1;
        cn = select(t,cix(j));
        try
            ce = Cexpr(cn);
            % Cexpr may be the class name ID or a "<" inheritance expression
            nm = '';
            if strcmp(char(kind(ce)),'ID')
                nm = stringval(ce);
            else
                lf = Left(ce);
                if ~isnull(lf) && strcmp(char(kind(lf)),'ID'), nm = stringval(lf); end
            end
            if ~isempty(nm)
                if isKey(classNames,nm), classNames(nm)=classNames(nm)+1; else, classNames(nm)=1; end
            end
        catch
        end
    end

    % ===== properties blocks =====
    pbs = mtfind(t,'Kind','PROPERTIES');
    pix = indices(pbs);
    for j = 1:numel(pix)
        S.properties_blocks = S.properties_blocks + 1;
        pb = select(t,pix(j));
        st = Body(pb);
        while ~isnull(st)
            nm = baseName(st);
            if ~isempty(nm)
                S.co.property = S.co.property + 1;
                fRec.properties = fRec.properties + 1;
                if isKey(propNames,nm), propNames(nm)=propNames(nm)+1; else, propNames(nm)=1; end
            end
            st = Next(st);
        end
    end

    % ===== methods blocks =====
    mbs = mtfind(t,'Kind','METHODS');
    S.methods_blocks = S.methods_blocks + numel(indices(mbs));

    % ===== persistent / global =====
    for kk = {'PERSISTENT','GLOBAL'}
        gs = mtfind(t,'Kind',kk{1});
        gix = indices(gs);
        for j = 1:numel(gix)
            gn = select(t,gix(j));
            v = Arg(gn);
            if isnull(v), v = Body(gn); end
            cnt = 0;
            while ~isnull(v)
                if strcmp(char(kind(v)),'ID'), cnt = cnt+1; end
                v = Next(v);
            end
            if cnt==0, cnt = 1; end
            if strcmp(kk{1},'PERSISTENT'), S.co.persistent = S.co.persistent + cnt;
            else,                          S.co.global     = S.co.global     + cnt; end
        end
    end

    % ===== anonymous functions =====
    ans_ = mtfind(t,'Kind','ANON');
    aix = indices(ans_);
    S.tx.anon_function = S.tx.anon_function + numel(aix);
    for j = 1:numel(aix)
        an = select(t,aix(j));
        p = Ins(an);
        while ~isnull(p)
            S.co.anon_capture_param = S.co.anon_capture_param + 1;
            p = Next(p);
        end
    end

    % ===== functions (transformers) : spans + params + classification =====
    fns = mtfind(t,'Kind','FUNCTION');
    fix = indices(fns);
    nfn = numel(fix);
    spanL = zeros(nfn,1); spanR = zeros(nfn,1); fname = cell(nfn,1); fclass = cell(nfn,1);
    for j = 1:nfn
        fn = select(t,fix(j));
        try
            spanL(j) = lefttreepos(fn);
            spanR(j) = righttreepos(fn);
        catch
            spanL(j) = position(fn); spanR(j) = position(fn);
        end
        nm = '';
        try
            fh = Fname(fn);
            if ~isnull(fh), nm = stringval(fh); end
        catch
        end
        fname{j} = nm;
        if ~isempty(nm)
            if isKey(defFuncNames,nm), defFuncNames(nm)=defFuncNames(nm)+1; else, defFuncNames(nm)=1; end
        end

        % classify: method (ancestor METHODS) / nested (ancestor FUNCTION) / main / subfunction
        cls = 'subfunction';
        anc = Parent(fn); depth = 0; isMethod = false; isNested = false;
        while ~isnull(anc) && depth < 12
            kk2 = char(kind(anc));
            if strcmp(kk2,'METHODS'), isMethod = true; break; end
            if strcmp(kk2,'FUNCTION'), isNested = true; break; end
            anc = Parent(anc); depth = depth+1;
        end
        if isMethod
            cls = 'method'; S.tx.method = S.tx.method+1; fRec.methods = fRec.methods+1;
        elseif isNested
            cls = 'nested_function'; S.tx.nested_function = S.tx.nested_function+1;
        elseif j==1 && strcmp(ft,'FunctionFile')
            cls = 'main_function'; S.tx.main_function = S.tx.main_function+1;
        else
            S.tx.subfunction = S.tx.subfunction+1;
        end
        fclass{j} = cls;
        fRec.functions = fRec.functions+1;

        % params
        p = Ins(fn);
        while ~isnull(p)
            S.co.input_param = S.co.input_param + 1;
            if strcmp(char(kind(p)),'ID') && strcmp(stringval(p),'varargin'), S.varargin = S.varargin+1; end
            p = Next(p);
        end
        o = Outs(fn);
        while ~isnull(o)
            S.co.output_param = S.co.output_param + 1;
            if strcmp(char(kind(o)),'ID') && strcmp(stringval(o),'varargout'), S.varargout = S.varargout+1; end
            o = Next(o);
        end
    end

    % ===== assignments -> local containers + write occurrences =====
    localsByFn = containers.Map('KeyType','char','ValueType','double');
    eqs = mtfind(t,'Kind','EQUALS');
    eix = indices(eqs);
    for j = 1:numel(eix)
        en = select(t,eix(j));
        lhsn = Left(en);
        names = {};
        if ~isnull(lhsn) && strcmp(char(kind(lhsn)),'LB')
            % [a,b] = f(...)
            v = Arg(lhsn); if isnull(v), v = Body(lhsn); end
            if isnull(v), v = List(lhsn); end
            while ~isnull(v)
                nm = baseName(v); if ~isempty(nm), names{end+1} = nm; end %#ok<SAGROW>
                v = Next(v);
            end
        else
            nm = baseName(lhsn); if ~isempty(nm), names{end+1} = nm; end
        end
        S.ed.write_occurrences = S.ed.write_occurrences + max(1,numel(names));
        fi = enclosingIdx(position(en), spanL, spanR);
        for q = 1:numel(names)
            key = sprintf('%d|%s', fi, names{q});
            if ~isKey(localsByFn,key), localsByFn(key)=1; end
        end
    end
    % for-loop induction variables
    frs = mtfind(t,'Kind','FOR');
    frix = indices(frs);
    for j = 1:numel(frix)
        fn2 = select(t,frix(j));
        iv = Index(fn2);
        if isnull(iv), continue; end
        nm = baseName(iv);
        if ~isempty(nm)
            S.co.loop_var = S.co.loop_var + 1;
            S.ed.write_occurrences = S.ed.write_occurrences + 1;
            key = sprintf('%d|%s', enclosingIdx(position(fn2), spanL, spanR), nm);
            if ~isKey(localsByFn,key), localsByFn(key)=1; end
        end
    end
    nLocals = double(localsByFn.Count);
    S.co.local_assigned_distinct = S.co.local_assigned_distinct + nLocals;
    fRec.locals = nLocals;

    % ===== call sites -> edges =====
    cls_ = mtfind(t,'Kind','CALL');
    clix = indices(cls_);
    S.ed.call_sites = S.ed.call_sites + numel(clix);
    for j = 1:numel(clix)
        cn = select(t,clix(j));
        tgt = Left(cn);
        nm = '';
        if ~isnull(tgt)
            kt = char(kind(tgt));
            if strcmp(kt,'ID')
                nm = stringval(tgt);
            elseif strcmp(kt,'DOT')
                rt = Right(tgt);
                if ~isnull(rt), nm = ['.' stringval(rt)]; end
            end
        end
        if isempty(nm), continue; end
        if isKey(calleeCount,nm), calleeCount(nm)=calleeCount(nm)+1; else, calleeCount(nm)=1; end
        fi = enclosingIdx(position(cn), spanL, spanR);
        encl = '<file-level>';
        if fi>0 && ~isempty(fname{fi}), encl = fname{fi}; end
        pk = sprintf('%s::%s -> %s', rel, encl, nm);
        if isKey(callerCalleePairs,pk), callerCalleePairs(pk)=callerCalleePairs(pk)+1;
        else, callerCalleePairs(pk)=1; fileCalleeRaw(end+1,:) = {rel, encl, nm}; end %#ok<SAGROW>
        fRec.calls = fRec.calls + 1;
    end

    % DOT / FIELD / SUBSCR occurrence counts
    S.ed.dot_method_or_field = S.ed.dot_method_or_field + numel(indices(mtfind(t,'Kind','DOT')));
    S.ed.subscr             = S.ed.subscr             + numel(indices(mtfind(t,'Kind','SUBSCR')));
    S.ed.id_occurrences     = S.ed.id_occurrences     + numel(indices(mtfind(t,'Kind','ID')));

    % field names touched (obj.foo)
    fds = mtfind(t,'Kind','FIELD');
    fdix = indices(fds);
    for j = 1:numel(fdix)
        fn3 = select(t,fdix(j));
        try
            nm = stringval(fn3);
            if ~isempty(nm)
                if isKey(fieldCount,nm), fieldCount(nm)=fieldCount(nm)+1; else, fieldCount(nm)=1; end
            end
        catch
        end
    end

    perFile{i} = fRec;
end

S.tx.total_named = S.tx.main_function + S.tx.subfunction + S.tx.nested_function + S.tx.method + S.tx.script;
S.co.total_named = S.co.input_param + S.co.output_param + S.co.property + S.co.persistent + S.co.global;

% ---------- internal vs external call resolution ----------
internalTargets = containers.Map('KeyType','char','ValueType','double');
kk = keys(defFuncNames); for i=1:numel(kk), internalTargets(kk{i})=1; end
kk = keys(classNames);   for i=1:numel(kk), internalTargets(kk{i})=1; end
kk = keys(fileStems);    for i=1:numel(kk), internalTargets(kk{i})=1; end

nInt=0; nExt=0; nDot=0; distInt=containers.Map(); distExt=containers.Map();
ck = keys(calleeCount);
for i=1:numel(ck)
    nm = ck{i}; c = calleeCount(nm);
    if startsWith(nm,'.')
        nDot = nDot + c;
    elseif isKey(internalTargets, nm)
        nInt = nInt + c; distInt(nm)=1;
    else
        nExt = nExt + c; distExt(nm)=1;
    end
end
S.calls = struct('internal_occurrences',nInt,'external_occurrences',nExt, ...
                 'dotted_method_call_occurrences',nDot, ...
                 'distinct_internal_targets',double(distInt.Count), ...
                 'distinct_external_targets',double(distExt.Count), ...
                 'distinct_caller_callee_pairs',double(callerCalleePairs.Count));

S.distinct_defined_function_names = double(defFuncNames.Count);
S.distinct_class_names = double(classNames.Count);
S.distinct_property_names = double(propNames.Count);
S.distinct_field_names = double(fieldCount.Count);
S.elapsed_seconds = toc(tStart);
S.failures = failures;

% ---------- write outputs ----------
fid = fopen(fullfile(ev,'summary.json'),'w'); fprintf(fid,'%s',jsonencode(S,'PrettyPrint',true)); fclose(fid);

pf = perFile(~cellfun(@isempty,perFile));
fid = fopen(fullfile(ev,'per_file.json'),'w'); fprintf(fid,'%s',jsonencode([pf{:}],'PrettyPrint',true)); fclose(fid);

fid = fopen(fullfile(ev,'call_edges.tsv'),'w');
fprintf(fid,'file\tenclosing_function\tcallee\n');
for i=1:size(fileCalleeRaw,1)
    fprintf(fid,'%s\t%s\t%s\n', fileCalleeRaw{i,1}, fileCalleeRaw{i,2}, fileCalleeRaw{i,3});
end
fclose(fid);

% top external callees (what a mapper would have to treat as "library")
ck = keys(calleeCount); cv = cell2mat(values(calleeCount));
[~,ord] = sort(cv,'descend');
fid = fopen(fullfile(ev,'top_callees.txt'),'w');
for i=1:min(60,numel(ord))
    nm = ck{ord(i)};
    if startsWith(nm,'.'), tag='DOTTED'; elseif isKey(internalTargets,nm), tag='INTERNAL'; else, tag='EXTERNAL'; end
    fprintf(fid,'%-9s %-34s %d\n', tag, nm, cv(ord(i)));
end
fclose(fid);

disp(jsonencode(S,'PrettyPrint',true));
diary off;
fprintf('EXTRACT_DONE %.2fs\n', S.elapsed_seconds);

% ---------- local helper ----------
function nm = baseName(n)
    nm = '';
    d = 0;
    while ~isnull(n) && d < 8
        k = char(kind(n));
        switch k
            case 'ID',   nm = stringval(n); return
            case {'DOT','SUBSCR','CELLINDEX','LP','PROPTYPEDECL','EQUALS','ATTR'}
                n = Left(n);
            otherwise
                return
        end
        d = d + 1;
    end
end

function idx = enclosingIdx(pos, spanL, spanR)
    idx = 0; best = inf;
    for q = 1:numel(spanL)
        if pos >= spanL(q) && pos <= spanR(q)
            w = spanR(q) - spanL(q);
            if w < best, best = w; idx = q; end
        end
    end
end
