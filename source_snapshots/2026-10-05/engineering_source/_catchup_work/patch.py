import os,re,json,glob
from PIL import Image, ImageDraw, ImageFilter
S=os.path.join(os.path.dirname(os.path.abspath(__file__)),'stage')
OLD='/workspace/creative-pipeline'
# 1) redact personal info in Wingstop checkout refs
def redact(p,boxes):
    im=Image.open(p).convert('RGB')
    for b in boxes:
        reg=im.crop(b).filter(ImageFilter.GaussianBlur(18)); im.paste(reg,b[:2])
        d=ImageDraw.Draw(im); d.rectangle(b,outline=(200,0,0),width=2)
    im.save(p)
redact(os.path.join(S,'outputs/cand04_groceries_wingstop/_w/ref/dd_prices.png'),[(0,40,600,621)])
redact(os.path.join(S,'outputs/cand04_groceries_wingstop/_w/ref/dd_header.png'),[(690,4,912,56)])
# 2) make scripts ROOT-relative
n=0
for p in glob.glob(S+'/**/*.py',recursive=True)+glob.glob(S+'/**/*.bak',recursive=True):
    src=open(p).read()
    if OLD not in src and '/usr/share/fonts/truetype/sand-box/google/DM Sans/' not in src: continue
    rel=os.path.relpath(os.path.dirname(p),S); depth=0 if rel=='.' else len(rel.split(os.sep))
    up="'"+"/".join(['..']*depth)+"'" if depth else "'.'"
    rootline=("import os as _os; ROOT=_os.environ.get('ROOT') or _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),%s))  # package root (portable)\n"%up)
    s=src.replace("'/usr/share/fonts/truetype/sand-box/google/DM Sans/'","ROOT+'/fonts/DM Sans/'")
    s=s.replace("'"+OLD+"/","ROOT+'/").replace('"'+OLD+'/','ROOT+"/')
    s=s.replace("'"+OLD+"'","ROOT").replace(OLD,'$ROOT')   # remaining mentions in docstrings/comments
    lines=s.split('\n',1)
    if lines[0].startswith('#!'): s=lines[0]+'\n'+rootline+lines[1]
    else: s=rootline+s
    open(p,'w').write(s); n+=1
print('patched py files:',n)
# 3) chat builder: expand $ROOT in spec strings
b=os.path.join(S,'outputs/_tools/build_imessage_ios26.py'); s=open(b).read()
print('json.load uses:',[m.start() for m in re.finditer(r'json\.load',s)])
old="    build(json.load(open(sys.argv[1])))"
assert old in s, 'loader line not found'
s=s.replace(old,"    _t=open(sys.argv[1]).read().replace('$ROOT',ROOT)  # portable spec paths\n    build(json.loads(_t))")
open(b,'w').write(s)
# 4) spec JSONs: absolute box paths -> $ROOT
k=0
for p in glob.glob(S+'/**/*.json',recursive=True):
    t=open(p).read()
    if OLD in t: open(p,'w').write(t.replace(OLD,'$ROOT')); k+=1
print('patched json specs:',k)
