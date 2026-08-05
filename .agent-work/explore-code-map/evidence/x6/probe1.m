% probe1.m -- discover the mtree API surface and node-kind distribution.
% READ-ONLY over the target. Writes only into the evidence dir.
ev  = 'C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x6';
src = 'C:\Programs\superCoolSpaceSim\matlab_src';

diary(fullfile(ev,'probe1_log.txt'));
fprintf('MATLAB %s\n', version);

L = dir(fullfile(src,'**','*.m'));
fprintf('FILES_FOUND %d\n', numel(L));

% ---- 1. does mtree exist and what methods does it have? ----
fprintf('\n=== which mtree ===\n');
disp(which('mtree'));
fprintf('\n=== methods(mtree) ===\n');
try
    f1 = fullfile(L(1).folder, L(1).name);
    t  = mtree(f1, '-file');
    disp(methods(t));
catch ME
    fprintf('MTREE_CONSTRUCT_FAILED %s\n', ME.message);
end

% ---- 2. FileType across a sample ----
fprintf('\n=== FileType over all files ===\n');
ftypes = containers.Map();
nfail  = 0;
failmsg = {};
tic;
for i = 1:numel(L)
    fp = fullfile(L(i).folder, L(i).name);
    try
        t = mtree(fp, '-file');
        ft = char(t.FileType);
        if isKey(ftypes, ft), ftypes(ft) = ftypes(ft)+1; else, ftypes(ft) = 1; end
    catch ME
        nfail = nfail + 1;
        if nfail <= 5, failmsg{end+1} = sprintf('%s :: %s', fp, ME.message); end %#ok<SAGROW>
    end
end
el = toc;
k = keys(ftypes);
for i = 1:numel(k), fprintf('FILETYPE %-24s %d\n', k{i}, ftypes(k{i})); end
fprintf('MTREE_PARSE_FAILURES %d\n', nfail);
for i=1:numel(failmsg), fprintf('  FAIL %s\n', failmsg{i}); end
fprintf('MTREE_PARSE_ALL_SECONDS %.2f\n', el);

% ---- 3. node kind distribution over the whole corpus ----
fprintf('\n=== node Kind distribution (sample of 60 files) ===\n');
kinds = containers.Map();
total = 0;
tic;
samp = round(linspace(1, numel(L), min(60, numel(L))));
for i = samp
    fp = fullfile(L(i).folder, L(i).name);
    try
        t = mtree(fp, '-file');
    catch
        continue
    end
    ix = indices(t);
    for j = 1:numel(ix)
        n = select(t, ix(j));
        kk = char(n.kind);
        if isKey(kinds, kk), kinds(kk) = kinds(kk)+1; else, kinds(kk) = 1; end
        total = total + 1;
    end
end
el2 = toc;
kk = keys(kinds); vv = cell2mat(values(kinds));
[~,ord] = sort(vv,'descend');
for i = 1:numel(ord)
    fprintf('KIND %-22s %d\n', kk{ord(i)}, vv(ord(i)));
end
fprintf('KIND_TOTAL_NODES %d\n', total);
fprintf('KIND_SCAN_SECONDS %.2f\n', el2);

diary off;
fprintf('PROBE1_DONE\n');
