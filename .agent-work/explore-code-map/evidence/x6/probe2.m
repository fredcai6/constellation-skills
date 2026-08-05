% probe2.m -- (a) dump real node structure for methods/anon/dotted-calls,
%             (b) time matlab.codetools.requiredFilesAndProducts on a sample,
%             (c) run checkcode over the corpus.
ev  = 'C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x6';
src = 'C:\Programs\superCoolSpaceSim\matlab_src';
diary(fullfile(ev,'probe2_log.txt'));

% ---------- (a) structure dumps ----------
fprintf('=== DUMPTREE: TestRecordingIntegrator.m (classdef, 1 methods block, 1 method) ===\n');
t = mtree(fullfile(src,'unit_tests','TestRecordingIntegrator.m'),'-file');
dumptree(t);

fprintf('\n=== Parent/Next structure of FUNCTION nodes in a MULTI-method class ===\n');
t2 = mtree(fullfile(src,'core','integrator','Integrator.m'),'-file');
fns = mtfind(t2,'Kind','FUNCTION'); fix = indices(fns);
mts = mtfind(t2,'Kind','METHODS'); mix = indices(mts);
fprintf('Integrator.m: %d FUNCTION nodes, %d METHODS blocks\n', numel(fix), numel(mix));
for j = 1:min(8,numel(fix))
    n = select(t2,fix(j));
    p = Parent(n);
    pk = '<null>'; if ~isnull(p), pk = char(kind(p)); end
    fprintf('  fn#%d name=%-24s line=%-5d parentKind=%s\n', j, stringval(Fname(n)), lineno(n), pk);
end
fprintf('  METHODS block spans (lefttreepos..righttreepos):\n');
for j = 1:numel(mix)
    n = select(t2,mix(j));
    fprintf('    methods#%d line=%d span=[%d..%d]\n', j, lineno(n), lefttreepos(n), righttreepos(n));
end

% ---------- structure of a dotted call and an anon fn ----------
fprintf('\n=== KIND structure: dotted calls + anon fns, sampled from AttitudeController.m ===\n');
t3 = mtree(fullfile(src,'software','AttitudeController.m'),'-file');
d = mtfind(t3,'Kind','DOT'); dix = indices(d);
fprintf('DOT nodes: %d. First 6 with parent kind + rendered text:\n', numel(dix));
for j = 1:min(6,numel(dix))
    n = select(t3,dix(j));
    p = Parent(n); pk='<null>'; if ~isnull(p), pk=char(kind(p)); end
    fprintf('  DOT line=%-5d parent=%-8s text=%s\n', lineno(n), pk, strtrim(tree2str(n)));
end
a = mtfind(t3,'Kind','ANON'); aix = indices(a);
fprintf('ANON nodes: %d. First 4 (Left/Right/Ins kinds):\n', numel(aix));
for j = 1:min(4,numel(aix))
    n = select(t3,aix(j));
    lk='<null>'; rk='<null>'; ik='<null>';
    if ~isnull(Left(n)),  lk=char(kind(Left(n)));  end
    if ~isnull(Right(n)), rk=char(kind(Right(n))); end
    if ~isnull(Ins(n)),   ik=char(kind(Ins(n)));   end
    fprintf('  ANON line=%-5d Left=%-8s Right=%-8s Ins=%-8s text=%s\n', lineno(n), lk, rk, ik, strtrim(tree2str(n)));
end
% how are obj.method(args) call sites shaped?
fprintf('\nCALL nodes whose Left is not a bare ID (first 8):\n');
c = mtfind(t3,'Kind','CALL'); cix = indices(c); shown=0;
for j = 1:numel(cix)
    n = select(t3,cix(j)); lf = Left(n);
    if isnull(lf), continue; end
    if strcmp(char(kind(lf)),'ID'), continue; end
    shown = shown+1;
    fprintf('  CALL line=%-5d LeftKind=%-8s text=%s\n', lineno(n), char(kind(lf)), strtrim(tree2str(n)));
    if shown >= 8, break; end
end
fprintf('  (of %d CALL nodes in this file)\n', numel(cix));

% ---------- (b) requiredFilesAndProducts ----------
fprintf('\n=== requiredFilesAndProducts on a 6-file sample ===\n');
oldp = path();          % restore afterwards; never savepath
cleanupPath = onCleanup(@() path(oldp));
addpath(genpath(src));
L = dir(fullfile(src,'**','*.m'));
samp = round(linspace(1,numel(L),6));
rows = {};
for i = samp
    fp = fullfile(L(i).folder,L(i).name);
    rel = strrep(fp,[src filesep],'');
    tic;
    try
        [fl, pr] = matlab.codetools.requiredFilesAndProducts(fp);
        el = toc;
        inSrc = sum(startsWith(string(fl), src));
        fprintf('RFP %-52s files=%-4d in_matlab_src=%-4d products=%-2d %.1fs\n', rel, numel(fl), inSrc, numel(pr), el);
        rows(end+1,:) = {rel, numel(fl), inSrc, numel(pr), el}; %#ok<SAGROW>
    catch ME
        el = toc;
        fprintf('RFP %-52s FAILED (%.1fs) %s\n', rel, el, ME.message);
        rows(end+1,:) = {rel, -1, -1, -1, el}; %#ok<SAGROW>
    end
end
tot = sum(cell2mat(rows(:,5)));
fprintf('RFP_SAMPLE_TOTAL_SECONDS %.1f  -> extrapolated for 539 files: %.1f min\n', tot, (tot/numel(samp))*539/60);

% ---------- (c) checkcode ----------
fprintf('\n=== checkcode over the whole corpus ===\n');
tic;
allf = arrayfun(@(x) string(fullfile(x.folder,x.name)), L);
info = checkcode(cellstr(allf), '-struct', '-id');
el = toc;
nmsg = sum(cellfun(@numel, info));
fprintf('CHECKCODE_FILES %d  MESSAGES %d  SECONDS %.1f\n', numel(info), nmsg, el);
ids = containers.Map('KeyType','char','ValueType','double');
for i=1:numel(info)
    for j=1:numel(info{i})
        id = info{i}(j).id;
        if isKey(ids,id), ids(id)=ids(id)+1; else, ids(id)=1; end
    end
end
kk = keys(ids); vv = cell2mat(values(ids)); [~,o]=sort(vv,'descend');
fprintf('Top checkcode message ids:\n');
for i=1:min(15,numel(o)), fprintf('  %-14s %d\n', kk{o(i)}, vv(o(i))); end

diary off;
fprintf('PROBE2_DONE\n');
