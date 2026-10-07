import numpy as np, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
G='/usr/share/fonts/truetype/sand-box/google/DM Sans/'
DM=G+[f for f in os.listdir(G) if 'Italic' not in f][0]
SF='/workspace/creative-pipeline/outputs/proof_cand01_s1/_w/fonts/'
def font(size,w=370,ss=4,path=DM):
    f=ImageFont.truetype(path,int(round(size*ss)))
    try:
        if w is None: raise Exception
        ax=f.get_variation_axes()
        f.set_variation_by_axes([(w if b'eight' in x['name'] else min(max(size,x['minimum']),x['maximum'])) for x in ax])
    except Exception: pass
    return f
def mask(text,size,w=370,blur=0.45,ss=4,path=DM):
    """returns (alpha float array HxW at 1x, x_off, baseline_row) text laid at origin baseline"""
    f=font(size,w,ss,path)
    l,t,r,b=f.getbbox(text,anchor='ls')
    W=r-l+8*ss; H=b-t+8*ss
    W+=(-W)%ss; H+=(-H)%ss
    im=Image.new('L',(W,H),0); d=ImageDraw.Draw(im)
    ox=4*ss-l; oy=4*ss-t
    d.text((ox,oy),text,font=f,fill=255,anchor='ls')
    im=im.resize((W//ss,H//ss),Image.LANCZOS)
    if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im).astype(float)/255, ox/ss, oy/ss, (r-l)/ss
def put(dst,text,size,x,base,color,w=370,blur=0.45,align='l',path=DM):
    """dst: float HxWx3 array. x = left edge (align l) or right edge (align r) of ink advance"""
    a,ox,oy,adv=mask(text,size,w,blur,path=path)
    if align=='r': x=x-adv
    x0=int(round(x-ox)); y0=int(round(base-oy))
    h,wd=a.shape
    reg=dst[y0:y0+h,x0:x0+wd]
    a3=a[...,None]
    reg[:]=reg*(1-a3)+np.array(color,float)*a3
    return adv
def put_ink(dst,text,size,x,base,color,w=370,blur=0.45,align='l',path=DM,thr=0.3):
    a,ox,oy,adv=mask(text,size,w,blur,path=path)
    cols=np.where((a>thr).any(0))[0]
    x0=int(round(x-cols[0])) if align=='l' else int(round(x-cols[-1]-1))
    y0=int(round(base-oy)); h,wd=a.shape
    reg=dst[y0:y0+h,x0:x0+wd]; a3=a[...,None]
    reg[:]=reg*(1-a3)+np.array(color,float)*a3
    return x0+cols[0], x0+cols[-1]+1
