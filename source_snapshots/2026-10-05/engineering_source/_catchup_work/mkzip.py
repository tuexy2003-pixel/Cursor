import os,zipfile
S=os.path.join(os.path.dirname(os.path.abspath(__file__)),'stage'); Z='/workspace/creative-pipeline/CATCHUP.zip'
tmp=Z+'.tmp'
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for d,_,fs in sorted(os.walk(S)):
        for f in sorted(fs):
            p=os.path.join(d,f); a=os.path.relpath(p,S)
            zi=zipfile.ZipInfo.from_file(p,a); zi.compress_type=zipfile.ZIP_DEFLATED
            if os.access(p,os.X_OK): zi.external_attr=(0o755<<16)
            with open(p,'rb') as fh: z.writestr(zi,fh.read())
os.replace(tmp,Z); print(Z,os.path.getsize(Z))
