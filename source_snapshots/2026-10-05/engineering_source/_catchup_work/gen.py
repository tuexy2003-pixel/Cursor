import os,re,json
W=os.path.dirname(os.path.abspath(__file__)); R=os.path.dirname(W)
t=open(os.path.join(W,'catchup_template.md')).read()
def sec(n):
    p=os.path.join(W,'sec_%s.md'%n)
    return open(p).read().rstrip() if os.path.exists(p) else '_(section being written — see SYSTEM_PLAYBOOK.md / HANDOFF_LATEST.md meanwhile)_'
subs={k:sec(k.lower()) for k in ['DOORDASH','ORDER','PLATES','RULES','OPEN','EXTRAS','PACKAGE']}
subs['FREEZER']=open(os.path.join(R,'outputs/cand04b_jalen_part2/freezer_prompt.txt')).read().rstrip()
import subprocess
subs['TREE']=subprocess.run('cd %s/stage && find . -type f | sort'%W,shell=True,capture_output=True,text=True).stdout.rstrip()
subs['QUADS']=open(os.path.join(R,'assets/phone_plates/quads.json')).read().rstrip()
for _ in range(2):
    for k,v in subs.items(): t=t.replace('<<%s>>'%k,v)
open(os.path.join(R,'CATCHUP.md'),'w').write(t)
print('CATCHUP.md',len(t),'chars; leftover placeholders:',re.findall(r'<<[A-Z]+>>',t))
