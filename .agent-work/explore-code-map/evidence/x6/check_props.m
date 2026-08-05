function check_props()
% check_props.m -- list every extracted property name per file, so the 414 total
% can be checked line-by-line against the source.
ev  = 'C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x6';
src = 'C:\Programs\superCoolSpaceSim\matlab_src';
diary(fullfile(ev,'check_props_log.txt'));
L = dir(fullfile(src,'**','*.m'));
tot = 0;
fid = fopen(fullfile(ev,'properties_extracted.tsv'),'w');
fprintf(fid,'file\tblock_line\tproperty\n');
for i=1:numel(L)
    fp = fullfile(L(i).folder,L(i).name);
    rel = strrep(fp,[src filesep],'');
    t = mtree(fp,'-file');
    pbs = mtfind(t,'Kind','PROPERTIES'); pix = indices(pbs);
    if isempty(pix), continue; end
    idAt = containers.Map('KeyType','double','ValueType','any');
    idn = mtfind(t,'Kind','ID'); idix = indices(idn);
    for j=1:numel(idix), n=select(t,idix(j)); idAt(position(n))=stringval(n); end
    idPos = sort(cell2mat(keys(idAt)));
    for j=1:numel(pix)
        pb = select(t,pix(j)); bl = lineno(pb);
        st = Body(pb);
        while ~isnull(st)
            nm = bn(st);
            if isempty(nm), nm = firstIdAt(lefttreepos(st), idPos, idAt); end
            if ~isempty(nm)
                tot = tot+1;
                fprintf(fid,'%s\t%d\t%s\n', rel, bl, nm);
                if strcmp(rel,['subsystems' filesep 'SolarArray.m'])
                    fprintf('SolarArray block@%d : %s\n', bl, nm);
                end
            end
            st = Next(st);
        end
    end
end
fclose(fid);
fprintf('TOTAL_PROPERTIES_EXTRACTED %d\n', tot);
diary off;
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

function nm = firstIdAt(pos, idPos, idAt)
    nm='';
    k = find(idPos >= pos, 1, 'first');
    if isempty(k), return; end
    nm = idAt(idPos(k));
end
