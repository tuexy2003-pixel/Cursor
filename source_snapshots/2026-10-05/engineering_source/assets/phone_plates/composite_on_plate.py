#!/usr/bin/env python3
"""Composite a flat phone-screen render (e.g. an 850x1850 DoorDash Order Complete PNG) onto one of Tyrel's
phone photos ("plates") and export a 1080x1920 slide.

usage:
  /workspace/creative-pipeline/venv/bin/python composite_on_plate.py <plate_name> <flat_screen.png> <out.png> [--debug] [--no-home-indicator] [--seed N]

plate_name = a "name" in quads.json (user_A_iphone11_dark, user_B_bedsheet, user_C_car_thigh, user_D_hand_rings).

What it does:
  * the WHOLE visible display is replaced (rounded-corner mask from the measured quad, pushed ~1px outward), so none of the
    original screen (names, numbers, serials, keyboard...) survives; notch / Dynamic Island are redrawn as solid hardware on top;
  * occluder polygons from quads.json (fingers over the glass) are restored from the photo on top of the new screen;
  * the screen is graded to the plate (white/black level, tint, glare / sun streaks, blur, signal-dependent noise);
  * the background is the cached 2x EDSR upscale of the plate (sr_cache.py; Lanczos fallback), cropped to 9:16 and resized to
    1080x1920; the screen is warped straight into the 1080x1920 frame (never upscaled), then light grain unifies both.
  * --debug also writes <out>_debug.png (quad + rounded mask outline on the plate) and <out>_mask.png.
"""
import cv2,numpy as np,json,os,sys,argparse
D=os.path.dirname(os.path.abspath(__file__))
OW,OH=1080,1920

def load_plate(name):
    doc=json.load(open(os.path.join(D,'quads.json')))
    for p in doc['plates']:
        if p['name']==name: return p
    raise SystemExit('unknown plate %r; choose from %s'%(name,[p['name'] for p in doc['plates']]))

def rounded_rect_mask(w,h,r,ss=4):
    """anti-aliased rounded rectangle mask (float 0..1) of size w x h (flat coords)"""
    W,H,R=w*ss,h*ss,int(round(r*ss)); m=np.zeros((H,W),np.uint8)
    cv2.rectangle(m,(R,0),(W-1-R,H-1),255,-1); cv2.rectangle(m,(0,R),(W-1,H-1-R),255,-1)
    for cx,cy in [(R,R),(W-1-R,R),(R,H-1-R),(W-1-R,H-1-R)]: cv2.circle(m,(cx,cy),R,255,-1,cv2.LINE_AA)
    return cv2.resize(m,(w,h),interpolation=cv2.INTER_AREA).astype(np.float32)/255

def cutout_mask(w,h,cut,ss=4,pad=40):
    """island (pill) or notch mask in flat coords, on a canvas padded by `pad` px on every side (so a notch can run past the top edge)"""
    W,H=w*ss,h*ss; P_=pad*ss; m=np.zeros((H+2*P_,W+2*P_),np.uint8)
    x0,y0,x1,y1=[v*s+P_ for v,s in zip(cut['bbox_norm'],(W,H,W,H))]
    if cut['type']=='dynamic_island':
        r=(y1-y0)/2; cv2.rectangle(m,(int(x0+r),int(y0)),(int(x1-r),int(y1)),255,-1)
        cv2.circle(m,(int(x0+r),int((y0+y1)/2)),int(r),255,-1,cv2.LINE_AA); cv2.circle(m,(int(x1-r),int((y0+y1)/2)),int(r),255,-1,cv2.LINE_AA)
    else:  # notch: rectangle hanging from the top edge, rounded bottom corners, concave fillets where it meets the top edge
        rb=cut.get('bottom_radius_frac',0.045)*W; rf=cut.get('top_fillet_frac',0.014)*W
        y0=0; cv2.rectangle(m,(int(x0),y0),(int(x1),int(y1-rb)),255,-1); cv2.rectangle(m,(int(x0+rb),y0),(int(x1-rb),int(y1)),255,-1)
        cv2.circle(m,(int(x0+rb),int(y1-rb)),int(rb),255,-1,cv2.LINE_AA); cv2.circle(m,(int(x1-rb),int(y1-rb)),int(rb),255,-1,cv2.LINE_AA)
        for sx,cx in [(-1,x0),(1,x1)]:   # fillets: fill the corner square then carve a circle out
            top=P_; sq=np.zeros_like(m); xa,xb=sorted([int(cx),int(cx+sx*rf)]); cv2.rectangle(sq,(xa,top),(xb,int(top+rf)),255,-1)
            cv2.circle(sq,(int(cx+sx*rf),int(top+rf)),int(rf),0,-1,cv2.LINE_AA); m=np.maximum(m,sq)
    return cv2.resize(m,(w+2*pad,h+2*pad),interpolation=cv2.INTER_AREA).astype(np.float32)/255

def add_home_indicator(S):
    """iOS home indicator (same geometry as the cand04/05/06 comp scripts, scaled to the flat size)"""
    h,w=S.shape[:2]; sx,sy=w/850,h/1850; ss=4
    m=np.zeros((h*ss,w*ss),np.uint8); r=int(5.5*sy*ss)
    x0,x1=int((425-146)*sx*ss),int((425+146)*sx*ss); y0,y1=int((1850-31)*sy*ss),int((1850-20)*sy*ss)
    cv2.rectangle(m,(x0+r,y0),(x1-r,y1),255,-1); cv2.circle(m,(x0+r,y0+r),r,255,-1); cv2.circle(m,(x1-r,y0+r),r,255,-1)
    a=cv2.resize(m,(w,h),interpolation=cv2.INTER_AREA).astype(np.float32)[...,None]/255
    return S*(1-a)+15*a

def relayout_statusbar(S,cut):
    """For notch phones: move the left (time) and right (signal/wifi/battery) status-bar groups into the ears beside the notch.
    Only the two glyph groups are touched: they are lifted off the map with a difference alpha, their boxes are inpainted,
    and they are re-pasted centred in the ears (right group shrunk if the ear is narrow)."""
    h,w=S.shape[:2]; sy=h/1850; y0,y1=int(40*sy),int(96*sy)
    band=np.clip(S[y0:y1],0,255).astype(np.uint8); bh=band.shape[0]
    med=cv2.medianBlur(band,21).astype(np.float32); diff=np.abs(band.astype(np.float32)-med).max(2)
    strong=(diff>40).astype(np.uint8)
    out=band.astype(np.float32).copy(); nx0,nx1=cut['bbox_norm'][0]*w,cut['bbox_norm'][2]*w
    for side,(ra,rb) in [('L',(0,int(0.34*w))),('R',(int(0.66*w),w))]:
        colc=strong[:,ra:rb].sum(0); cs=np.where(colc>=2)[0]+ra
        if len(cs)==0: continue
        gx0,gx1=int(cs.min())-4,int(cs.max())+5; rows=np.where(strong[:,gx0:gx1].sum(1)>0)[0]; gy0,gy1=max(0,rows.min()-4),min(bh,rows.max()+5)
        box=np.zeros((bh,w),np.uint8); box[gy0:gy1,gx0:gx1]=255
        bg=cv2.inpaint(np.clip(out,0,255).astype(np.uint8),box,9,cv2.INPAINT_TELEA).astype(np.float32)
        alpha=np.clip((np.abs(band.astype(np.float32)-bg).max(2)-5)/45,0,1)*(box>0)
        gw=gx1-gx0; ear0,ear1=(0,nx0) if side=='L' else (nx1,w)
        scale=min(1.0,0.80*(ear1-ear0)/gw); cx=(ear0+ear1)/2+(3*w/850 if side=='L' else -3*w/850); cy=(gy0+gy1)/2
        M=np.float32([[scale,0,cx-scale*(gx0+gx1)/2],[0,scale,cy-scale*cy]])
        a_w=cv2.warpAffine(alpha,M,(w,bh),flags=cv2.INTER_LINEAR)
        c_w=cv2.warpAffine(band.astype(np.float32)*alpha[...,None],M,(w,bh),flags=cv2.INTER_LINEAR)
        out=bg*(1-a_w[...,None])+c_w+ bg*0   # premultiplied paste
        out=np.where(a_w[...,None]>0,bg*(1-a_w[...,None])+c_w,bg)
        band=np.clip(out,0,255).astype(np.uint8)   # next group works on the updated band
    S=S.copy(); S[y0:y1]=out; return S

def streak_field(plate,q,rng_dbg=None):
    """Sun streaks / white field measured from the photo's own light-mode screen (plate D). Returns a function
    f(Hom_flat_to_img) -> nothing; instead we return rectified white field (850x1850) as BGR float.
    Only low-frequency information is kept: a smooth quadratic base x a 1-D profile across the streak direction, both fitted on
    background pixels only, so no text/bubble shapes can leak."""
    W,H=425,925
    Hm=cv2.getPerspectiveTransform(np.float32(q),np.float32([[0,0],[W,0],[W,H],[0,H]]))
    r=cv2.warpPerspective(plate.astype(np.float32),Hm,(W,H),flags=cv2.INTER_AREA,borderValue=(-1,-1,-1))
    valid=(r.min(2)>=0); g=r.mean(2)
    # exclude cutout/status/keyboard margins: use rows 60..860
    yy,xx=np.mgrid[0:H,0:W].astype(np.float64)
    def basis(x,y): x=x/W; y=y/H; return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],-1)
    m=valid.copy(); m[:70]=False; m[870:]=False; m[:, :12]=False; m[:,-12:]=False
    lap=np.abs(cv2.Laplacian(cv2.GaussianBlur(g,(0,0),1.5),cv2.CV_32F)); m&=lap<1.2
    ys,xs=np.where(m); A=basis(xs,ys); L=g[ys,xs]; keep=np.ones(len(L),bool)
    for _ in range(6):
        cf,*_=np.linalg.lstsq(A[keep],L[keep],rcond=None); keep=L>A@cf-5
    base=(basis(xx,yy)@cf).astype(np.float32)
    # streak direction: scan angles, maximize variance of the binned ratio profile
    ratio=(L/(A@cf))[keep]; kx,ky=xs[keep],ys[keep]; best=None
    for ang in np.arange(-80,81,2.5):
        a=np.radians(ang); u=kx*np.cos(a)+ky*np.sin(a); b=np.round(u/6).astype(int); b-=b.min()
        cnt=np.bincount(b); s=np.bincount(b,ratio); prof=s/np.maximum(cnt,1); ok=cnt>30
        v=np.var(prof[ok]) if ok.sum()>5 else 0
        if best is None or v>best[0]: best=(v,ang)
    a=np.radians(best[1]); u=kx*np.cos(a)+ky*np.sin(a); umin=u.min(); b=np.round((u-umin)/3).astype(int)
    cnt=np.bincount(b); s=np.bincount(b,ratio); prof=np.where(cnt>15,s/np.maximum(cnt,1),np.nan)
    idx=np.arange(len(prof)); okp=~np.isnan(prof); prof=np.interp(idx,idx[okp],prof[okp])
    prof=cv2.GaussianBlur(prof.reshape(1,-1).astype(np.float32),(0,0),2.0).ravel()
    U=(xx*np.cos(a)+yy*np.sin(a)-umin)/3; Ui=np.clip(U,0,len(prof)-1)
    streak=np.interp(Ui.ravel(),idx,prof).reshape(H,W).astype(np.float32)
    # per-channel colour of the white field
    col=np.array([np.median(r[ys[keep],xs[keep],c]/np.maximum(g[ys[keep],xs[keep]],1)) for c in range(3)],np.float32)
    field=(base*streak)[...,None]*col[None,None]
    return cv2.resize(field,(850,1850),interpolation=cv2.INTER_CUBIC),best[1]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('plate'); ap.add_argument('screen'); ap.add_argument('out')
    ap.add_argument('--debug',action='store_true'); ap.add_argument('--no-home-indicator',action='store_true'); ap.add_argument('--seed',type=int,default=11)
    a=ap.parse_args(); P=load_plate(a.plate); L=P['look']; rng=np.random.default_rng(a.seed)
    plate=cv2.imread(os.path.join(D,P['file'])); ph,pw=plate.shape[:2]
    q=np.float32([P['quad'][k] for k in ('TL','TR','BR','BL')])
    # ---------- 9:16 crop box in plate px
    zoom=P['crop'].get('zoom',1.0); ch=ph/zoom; cw=ch*9/16
    cx=P['crop'].get('center_x') or float(q[:,0].mean()); cyc=P['crop'].get('center_y') or ph/2
    x0=float(np.clip(cx-cw/2,0,pw-cw)); y0=float(np.clip(cyc-ch/2,0,ph-ch)); s=OH/ch
    # ---------- background: cached EDSR x2 (fallback Lanczos)
    srp=os.path.join(D,'_cache',P['name']+'_edsr2.png')
    if os.path.exists(srp):
        big=cv2.imread(srp); k=big.shape[1]/pw
        Mb=np.float32([[s/k,0,-x0*s],[0,s/k,-y0*s]])
        bg=cv2.warpAffine(big,Mb,(OW,OH),flags=cv2.INTER_AREA if s/k<1 else cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
        # INTER_AREA is ignored by warpAffine: pre-resize instead for a clean downscale
        tgtw=int(round(big.shape[1]*s/k)); tgth=int(round(big.shape[0]*s/k))
        bigr=cv2.resize(big,(tgtw,tgth),interpolation=cv2.INTER_AREA)
        ox,oy=int(round(x0*s)),int(round(y0*s)); bg=bigr[oy:oy+OH,ox:ox+OW].astype(np.float32)
        if bg.shape[:2]!=(OH,OW): bg=cv2.resize(bg,(OW,OH),interpolation=cv2.INTER_AREA)
        bgsrc='edsr2'
    else:
        Mb=np.float32([[s,0,-x0*s],[0,s,-y0*s]]); bg=cv2.warpAffine(plate,Mb,(OW,OH),flags=cv2.INTER_LANCZOS4).astype(np.float32); bgsrc='lanczos'
    qo=(q-np.float32([x0,y0]))*s
    # ---------- flat screen prep (flat coords are normalised to 850x1850)
    S=cv2.imread(a.screen).astype(np.float32)
    if S.shape[:2]!=(1850,850): S=cv2.resize(S,(850,1850),interpolation=cv2.INTER_AREA)
    if not a.no_home_indicator: S=add_home_indicator(S)
    if L.get('statusbar_relayout') and P['cutout']['type']=='notch': S=relayout_statusbar(S,P['cutout'])
    FW,FH=850,1850
    Hf=cv2.getPerspectiveTransform(np.float32([[0,0],[FW,0],[FW,FH],[0,FH]]),qo)
    # supersampled warp: flat -> 2x output -> area-downsample (anti-aliased, no upscaling of UI)
    Hf2=np.diag([2,2,1]).astype(np.float64)@Hf
    Sw=cv2.resize(cv2.warpPerspective(S,Hf2,(OW*2,OH*2),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE),(OW,OH),interpolation=cv2.INTER_AREA)
    rr=rounded_rect_mask(FW,FH,P['corner_radius_frac']*FW)
    Mw=cv2.warpPerspective(rr,Hf,(OW,OH),flags=cv2.INTER_LINEAR)
    esig=L['edge_sigma']
    soft=cv2.GaussianBlur(Mw,(0,0),esig)
    mask=np.clip(soft/0.6,0,1)                   # 50% point pushed ~1px outward -> no original rim survives
    # ---------- grade
    sc=np.clip(Sw/255.0,0,1)**L.get('gamma',1.0)
    if L['white']=='fit':
        field,ang=streak_field(plate,q); Wf=cv2.warpPerspective(field,Hf,(OW,OH),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
        print('white field from photo: streak angle %.1f deg, white BGR range %s..%s'%(ang,Wf[Mw>0.9].min(0).round(0),Wf[Mw>0.9].max(0).round(0)))
    else:
        Wf=np.ones((OH,OW,3),np.float32)*np.float32(L['white'])
    blk=np.float32(L['black'])
    tint=np.float32(L.get('tint_bgr',[1,1,1]))
    out=blk+(Wf*tint-blk)*sc
    gl=L.get('glare',{})
    if gl.get('kind')=='soft':
        yy,xx=np.mgrid[0:OH,0:OW].astype(np.float32)
        # glare coordinates in flat space
        Hi=np.linalg.inv(Hf); den=Hi[2,0]*xx+Hi[2,1]*yy+Hi[2,2]; fx=(Hi[0,0]*xx+Hi[0,1]*yy+Hi[0,2])/den/FW; fy=(Hi[1,0]*xx+Hi[1,1]*yy+Hi[1,2])/den/FH
        an=np.radians(gl['angle']); u=fx*np.cos(an)+fy*np.sin(an)*2.18
        band=np.exp(-((u-gl['pos'])/0.22)**2)
        mult=1-gl['falloff']*(0.5*(fx-0.5)**2+ (fy-0.3)**2)
        out=out*mult[...,None]+gl['strength']*255*band[...,None]*np.float32([1.0,0.99,0.97])
    out=cv2.GaussianBlur(out,(0,0),L['screen_blur'])
    lum=np.clip(out.mean(2,keepdims=True)/255,0,1)
    n0,n1=L['noise']; nstd=n0+n1*np.sqrt(lum)
    noise=cv2.GaussianBlur(rng.normal(0,1,(OH,OW)).astype(np.float32),(0,0),0.6)[...,None]*1.5
    out=out+noise*nstd+rng.normal(0,L.get('chroma_noise',0.8),(OH,OW,3)).astype(np.float32)
    # ---------- composite screen
    res=bg*(1-mask[...,None])+out*mask[...,None]
    if L.get('bloom',0)>0:
        spill=cv2.GaussianBlur(out*mask[...,None],(0,0),L.get('bloom_sigma',9))
        res=res+L['bloom']*spill*(1-mask[...,None])
    # ---------- notch / island (hardware, on top of the new screen)
    cm=cutout_mask(FW,FH,P['cutout'],pad=40)
    Hc=Hf@np.array([[1,0,-40],[0,1,-40],[0,0,1]],np.float64)
    Cw=cv2.warpPerspective(cm,Hc,(OW,OH),flags=cv2.INTER_LINEAR)
    Cw=np.clip(cv2.GaussianBlur(Cw,(0,0),max(0.7,esig*0.8))/0.85,0,1)
    if P['cutout']['type']=='notch':
        # the notch is part of the bezel: show the photo's own (black) notch pixels, cut out of the new screen
        res=res*(1-Cw[...,None])+bg*Cw[...,None]
    else:
        ccol=np.float32(L.get('cutout_color',[6,6,7]))
        cl=ccol+cv2.GaussianBlur(rng.normal(0,1.4,(OH,OW)).astype(np.float32),(0,0),0.6)[...,None]
        if gl.get('kind')=='soft': cl=cl+gl['strength']*120*band[...,None]
        if L['white']=='fit': cl=cl+0.10*(Wf-Wf[Mw>0.9].mean(0))   # the sun streaks run across the glass over the island too
        Cw=Cw*mask
        res=res*(1-Cw[...,None])+cl*Cw[...,None]
    # ---------- occluders (fingers over the glass) restored from the photo
    occ=np.zeros((OH,OW),np.float32)
    for poly in P.get('occluders',[]):
        pts=((np.float32(poly['points'])-np.float32([x0,y0]))*s).astype(np.int32); cv2.fillPoly(occ,[pts],1.0)
    if occ.any():
        occ=cv2.GaussianBlur(occ,(0,0),1.2); res=res*(1-occ[...,None])+bg*occ[...,None]
    # ---------- global grain to unify the upscaled plate and the new screen
    gr=cv2.GaussianBlur(rng.normal(0,1,(OH,OW)).astype(np.float32),(0,0),0.7)[...,None]*1.4
    res=res+gr*L.get('grain',2.0)
    res=np.clip(res,0,255).round().astype(np.uint8)
    cv2.imwrite(a.out,res)
    print('wrote',a.out,res.shape[1],'x',res.shape[0],'| bg',bgsrc,'| crop plate x %.0f..%.0f y %.0f..%.0f scale %.3f'%(x0,x0+cw,y0,y0+ch,s))
    if a.debug:
        dbg=plate.copy()
        rr8=(rr*255).astype(np.uint8); Hp=cv2.getPerspectiveTransform(np.float32([[0,0],[FW,0],[FW,FH],[0,FH]]),q)
        mm=cv2.warpPerspective(rr8,Hp,(pw,ph)); cc=cv2.warpPerspective((cm*255).astype(np.uint8),Hp,(pw,ph))
        cnts,_=cv2.findContours((mm>127).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cv2.drawContours(dbg,cnts,-1,(0,0,255),1)
        cnts,_=cv2.findContours((cc>127).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cv2.drawContours(dbg,cnts,-1,(0,255,255),1)
        cv2.polylines(dbg,[q.astype(np.int32)],True,(0,255,0),1)
        base=os.path.splitext(a.out)[0]; cv2.imwrite(base+'_debug.png',dbg); cv2.imwrite(base+'_mask.png',(mask*255).astype(np.uint8))
if __name__=='__main__': main()
