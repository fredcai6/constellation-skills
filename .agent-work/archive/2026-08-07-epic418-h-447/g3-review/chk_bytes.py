import subprocess
for p in ['skills/commander/templates/COMMANDER_SPINE.template.json',
          'skills/admiral/templates/ADMIRAL_SPINE.template.json',
          'tests/data/store_mentions.approved.txt']:
    b=open(p,'rb').read()
    crlf=b.count(b'\r\n'); total_lf=b.count(b'\n'); bare=total_lf-crlf
    old=subprocess.run(['git','show','HEAD:'+p],capture_output=True).stdout
    ocrlf=old.count(b'\r\n'); olf=old.count(b'\n'); obare=olf-ocrlf
    print(f'{p}\n  WORKING: bytes={len(b)} lines(LF)={total_lf} CRLF={crlf} bareLF={bare}')
    print(f'  HEAD blob: lines(LF)={olf} CRLF={ocrlf} bareLF={obare}')
