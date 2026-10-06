#!/usr/bin/env python3
"""iOS 26 (Liquid Glass) dark-mode Messages screenshot builder.
Geometry/colours sampled from a real iPhone 1206x2622 (402pt @3x) dark-mode screenshot.
Usage:  python build_imessage_ios26.py spec.json
spec keys (all optional except thread/out):
  out            : path of 1080x1920 (9:16, fitted on black) output
  out_full       : path of the native 1206x2622 screenshot (optional)
  status         : {"time":"5:42","battery":0.2,"battery_color":"yellow"|"white","signal":3}
  contact        : {"name":"Dre 🤍","initial":"D","photo":"/path.png","subtitle":"Text Message · SMS"}
                   photo = circular avatar image (square crop OK); else gradient+initial
                   subtitle = grey label under name pill (defaults to "Text Message · SMS" when service=sms)
  unread         : "4"  (null -> no count badge)
  service        : "imessage" (blue, 'iMessage' field, Delivered allowed) | "sms" (green bubbles + SMS chrome)
  top_space      : min px (native) of empty black kept between header (y 445) and first item (default 240)
  max_bubble_frac: max bubble width as fraction of screen width (default 0.77)
  side_fill     : if true, scale to fill 1080 width and vertically crop to 1920 (closer phone crop; thin side margins)
  thread         : list of {"ts":"Wed, Sep 23 at 9:14 PM"} | {"in":"text"} | {"out":"text","delivered":true}
                   | {"from":"me"|"them","image":"/path.png","width_frac":0.60}  (photo attachment, no tail)
"""
import json, os, sys, urllib.request, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE=os.path.dirname(os.path.abspath(__file__)); AS=os.path.join(HERE,'ios26_assets')
FD='/workspace/creative-pipeline/outputs/proof_cand01_s1/_w/fonts/'
W,H=1206,2622; SS=2
BG=(0,0,0); GRAY_B=(38,38,40); BLUE=(66,143,247); GREEN=(52,199,89)
TS_COL=(141,141,146); WHITE=(255,255,255); PH_COL=(95,95,97); GLASS=(24,24,24)
BUB_PX=51; TRACK=-1.29; LINE=66; EMO_PX=58
# vertical rhythm (native px @3x). Reference: body-bottom->timestamp cap 47-49, cap->next body 53-55,
# sender switch 30. Consecutive same-sender run: no tail except on the last bubble, tight 2pt gap.
TS_ABOVE=49; TS_BELOW=54; GROUP_GAP=6
IMG_R=54   # photo attachment corner radius (18pt @3x)
def side_of(it):
    if it is None or 'ts' in it: return None
    if 'in' in it: return 'in'
    if 'out' in it: return 'out'
    if 'image' in it: return 'out' if it.get('from','me') in ('me','out') else 'in'
    return None
_fc={}
def F(n,px):
    k=(n,px)
    if k not in _fc: _fc[k]=ImageFont.truetype(FD+n,round(px*SS))
    return _fc[k]
def is_emoji(ch): return ord(ch)>=0x2600
def emoji_img(ch,size):
    cp='%x'%ord(ch); p=os.path.join(AS,'emoji','apple160_%s.png'%cp)
    if not os.path.exists(p):
        urllib.request.urlretrieve('https://raw.githubusercontent.com/iamcal/emoji-data/master/img-apple-160/%s.png'%cp,p)
    return Image.open(p).convert('RGBA').resize((round(size*SS),)*2,Image.LANCZOS)
def runs(t):
    out=[];buf=''
    for ch in t:
        if ch=='\ufe0f': continue
        if is_emoji(ch):
            if buf: out.append(('t',buf)); buf=''
            out.append(('e',ch))
        else: buf+=ch
    if buf: out.append(('t',buf))
    return out
def tlen(s,f,track): return f.getlength(s)/SS+track*len(s)
def measure(t,f,track=TRACK): return sum(tlen(v,f,track) if k=='t' else EMO_PX+4 for k,v in runs(t))
def draw_text(img,x,base,t,f,fill,track=TRACK):
    d=ImageDraw.Draw(img)
    for k,v in runs(t):
        if k=='t':
            for i,ch in enumerate(v):
                d.text(((x+f.getlength(v[:i])/SS+track*i)*SS,base*SS),ch,font=f,fill=fill,anchor='ls')
            x+=tlen(v,f,track)
        else:
            e=emoji_img(v,EMO_PX); img.paste(e,(round((x+2)*SS),round((base-EMO_PX*0.80)*SS)),e); x+=EMO_PX+4
    return x
def wrap(t,f,maxw):
    words=t.split(' '); lines=[]; cur=''
    for w_ in words:
        c=(cur+' '+w_).strip()
        if measure(c,f)<=maxw or not cur: cur=c
        else: lines.append(cur); cur=w_
    lines.append(cur); return lines
# ---------- bubble shapes: 9-slice of real iOS 26 bubble masks ----------
T_IN=np.asarray(Image.open(os.path.join(AS,'tmpl_in.png'))).astype(np.float32)/255   # tail bottom-left
T_OUT=np.asarray(Image.open(os.path.join(AS,'tmpl_out.png'))).astype(np.float32)[1:]/255 # tail bottom-right (row0 empty)
BODY_H=121; MID=60
def slice_mask(T,bw,bh,tail):
    """T: template (body starts at row0,col0; body width = T.shape[1] for in / measured), returns alpha (h,w) native px"""
    tw=T.shape[1]; cx=tw//2
    # horizontal
    if bw>=tw: A=np.concatenate([T[:,:cx],np.repeat(T[:,cx:cx+1],bw-tw,1),T[:,cx:]],1)
    else:
        cut=tw-bw; A=np.concatenate([T[:,:cx-cut//2],T[:,cx+(cut-cut//2):]],1)
    # vertical
    extra=bh-BODY_H
    top=A[:MID]; bot=A[MID:]
    if extra>0: A=np.concatenate([top,np.repeat(A[MID:MID+1],extra,0),bot],0)
    elif extra<0: A=np.concatenate([top[:MID+extra//2],bot[-extra+extra//2:]],0) if False else A
    if not tail:
        top=A[:MID]; A=np.concatenate([A[:bh-MID],top[::-1]],0)
        A=A[:bh]
    return A
def paste_alpha(canvas,A,x0,y0,color):
    """canvas: RGB PIL at SS scale; A: native alpha"""
    m=Image.fromarray((np.clip(A,0,1)*255).astype(np.uint8)).resize((A.shape[1]*SS,A.shape[0]*SS),Image.LANCZOS)
    canvas.paste(color,(round(x0*SS),round(y0*SS)),m)
# ---------- glass ----------
def glass(canvas,shape_fn,bbox):
    x0,y0,x1,y1=bbox; w=round((x1-x0)*SS); h=round((y1-y0)*SS)
    m=Image.new('L',(w,h),0); shape_fn(ImageDraw.Draw(m),w,h)
    ma=np.asarray(m)
    import cv2
    dist=cv2.distanceTransform((ma>127).astype(np.uint8),cv2.DIST_L2,3)/SS
    rim=np.clip(30*(1-(dist-0.5)/3.0),0,30)
    col=np.clip(np.array(GLASS,np.float32)[None,None,:]+rim[...,None],0,255).astype(np.uint8)
    canvas.paste(Image.fromarray(col),(round(x0*SS),round(y0*SS)),m)
def build(spec):
    st=spec.get('status',{}); ct=spec.get('contact',{}); sms=spec.get('service','imessage')=='sms'
    OUTC=GREEN if sms else BLUE
    # header bottom: avatar+pill end ~445; SMS subtitle adds ~55 native px
    _sub=ct.get('subtitle')
    if _sub is None and sms: _sub='Text Message · SMS'
    HEADER_BOTTOM=485 if _sub else 445
    fb=F('SF-Pro-Text-Regular.otf',BUB_PX)
    fts_b=F('SF-Pro-Text-Semibold.otf',33); fts_r=F('SF-Pro-Text-Regular.otf',33)
    FIELD=(240,2417,1122,2538); PLUS=(84,2418,204,2538)
    MAXW=round(spec.get('max_bubble_frac',0.77)*W)-91
    # ---- layout items (native px) ----
    items=[]; th=spec['thread']
    for i,it in enumerate(th):
        if 'ts' in it: items.append({'k':'ts','t':it['ts']}); continue
        side=side_of(it)
        nxt=th[i+1] if i+1<len(th) else None
        tail=not (nxt and side_of(nxt)==side)
        if 'image' in it:   # photo attachment: rounded corners, no bubble colour, no tail
            pim=Image.open(it['image']).convert('RGB'); iw=round(it.get('width_frac',0.60)*W); ih=round(iw*pim.height/pim.width)
            items.append({'k':'b','side':side,'img':pim,'w':iw,'h':ih,'tail':False,'deliv':bool(it.get('delivered')) and not sms})
            continue
        txt=it[side]
        lines=wrap(txt,fb,MAXW); inkw=max(measure(l,fb) for l in lines)
        items.append({'k':'b','side':side,'lines':lines,'w':round(inkw+91),'h':BODY_H+LINE*(len(lines)-1),'tail':tail,'deliv':bool(it.get('delivered')) and not sms})
    # bottom-anchored stack
    y=FIELD[1]-51
    for i in range(len(items)-1,-1,-1):
        it=items[i]; nxt=items[i+1] if i+1<len(items) else None
        if it['k']=='b':
            if nxt is None: gap=37 if it.get('deliv') else 0   # room for 'Delivered' above the field
            elif nxt['k']=='ts': gap=TS_ABOVE
            elif it.get('deliv'): gap=25+26+26
            elif nxt['side']==it['side']: gap=GROUP_GAP
            else: gap=30
            y-=gap; it['y1']=y; it['y0']=y-it['h']; y=it['y0']
        else:
            gap=TS_BELOW if nxt else 0   # timestamp cap-top -> next bubble top
            y-=gap; it['cap']=y; y=it['cap']
    top=y
    # screen taller than a real phone if the thread + reserved top space doesn't fit
    # (keeps every iOS proportion exact; 9:16 output then shows the phone column on black)
    need=HEADER_BOTTOM+spec.get('top_space',240)-top; dy=max(0,round(need)); Hc=H+dy
    for it in items:
        for k in ('y0','y1','cap'):
            if k in it: it[k]+=dy
    top+=dy
    FIELD=(FIELD[0],FIELD[1]+dy,FIELD[2],FIELD[3]+dy); PLUS=(PLUS[0],PLUS[1]+dy,PLUS[2],PLUS[3]+dy)
    # Optional top anchor: a short thread sits under the header like a captured
    # screen, with the unused area left above the composer. Does not grow the canvas.
    if spec.get('anchor')=='top' and items:
        def item_top(it):
            return it['cap'] if it['k']=='ts' else it['y0']
        def item_bot(it):
            return it['cap']+33 if it['k']=='ts' else it['y1']
        target=HEADER_BOTTOM+spec.get('top_space',36)
        shift=target-item_top(items[0])
        last=max(item_bot(it) for it in items)
        room=(FIELD[1]-70)-last
        if shift>room: shift=room
        if shift:
            for it in items:
                for k in ('y0','y1','cap'):
                    if k in it: it[k]+=shift
            top+=shift
    img=Image.new('RGB',(W*SS,Hc*SS),BG); d=ImageDraw.Draw(img)
    # ---- draw thread ----
    for it in items:
        if it['k']=='ts':
            t=it['t']; a,b=(t.split(' at ',1)+[''])[:2]; b=(' at '+b) if b else ''
            wa=tlen(a,fts_b,0); wb=tlen(b,fts_r,0); x=W/2-(wa+wb)/2; base=it['cap']+23
            draw_text(img,x,base,a,fts_b,TS_COL,0); draw_text(img,x+wa,base,b,fts_r,TS_COL,0); continue
        bw,bh=it['w'],it['h']
        if 'img' in it:
            x0=48 if it['side']=='in' else W-48-bw
            ph=it['img'].resize((bw*SS,bh*SS),Image.LANCZOS)
            mk=Image.new('L',ph.size,0); ImageDraw.Draw(mk).rounded_rectangle((0,0,ph.size[0]-1,ph.size[1]-1),radius=IMG_R*SS,fill=255)
            img.paste(ph,(round(x0*SS),round(it['y0']*SS)),mk)
        elif it['side']=='in':
            A=slice_mask(T_IN,bw,bh,it['tail']); x0=48; paste_alpha(img,A,x0,it['y0'],GRAY_B)
        else:
            A=slice_mask(T_OUT,bw,bh,it['tail']); x0=W-48-bw; paste_alpha(img,A,x0,it['y0'],OUTC)
        for j,l in enumerate(it.get('lines',[])):
            draw_text(img,x0+45,it['y0']+79+LINE*j,l,fb,WHITE)
        if it.get('deliv'):
            fdl=F('SF-Pro-Text-Semibold.otf',33); wd=tlen('Delivered',fdl,0)
            draw_text(img,W-48-45-wd,it['y1']+25+23,'Delivered',fdl,TS_COL,0)
    # ---- status bar ----
    ft=F('SF-Pro-Text-Semibold.otf',50); T=st.get('time','9:41')
    tb=ft.getbbox(T,anchor='ls'); tw=(tb[2]-tb[0])/SS
    cx=148+97/2; draw_text(img,cx-tw/2-tb[0]/SS,117,T,ft,WHITE,-0.3)
    nsig=st.get('signal',3)
    for i,hh in enumerate([14,21,29,37]):
        x=865+16*i; d.rounded_rectangle(((x)*SS,(116-hh)*SS,(x+10)*SS,116*SS),radius=2.5*SS,fill=WHITE if i<nsig else (70,70,72))
    wx,wy=970.5,116.5
    for ro,ri in [(37.5,27.5),(24.5,15.0),(11.5,0)]:
        R=ro*SS; d.pieslice(((wx*SS-R),(wy*SS-R),(wx*SS+R),(wy*SS+R)),start=-135,end=-45,fill=WHITE)
        if ri: Ri=ri*SS; d.pieslice(((wx*SS-Ri),(wy*SS-Ri),(wx*SS+Ri),(wy*SS+Ri)),start=-135,end=-45,fill=BG)
    bx0,by0,bx1,by1=1018,78,1093,117
    d.rounded_rectangle((bx0*SS,by0*SS,bx1*SS,by1*SS),radius=12*SS,outline=(102,102,102),width=round(2.6*SS))
    d.rounded_rectangle((1096*SS,92*SS,1100.5*SS,102*SS),radius=2*SS,fill=(102,102,102))
    lvl=st.get('battery',0.2); bc=(248,215,72) if st.get('battery_color','yellow')=='yellow' else WHITE
    ix0,iy0,ix1,iy1=bx0+6,by0+6,bx1-6,by1-6
    d.rounded_rectangle((ix0*SS,iy0*SS,(ix0+max(8,(ix1-ix0)*lvl))*SS,iy1*SS),radius=6*SS,fill=bc)
    # ---- header glass ----
    unread=spec.get('unread')
    fcount=F('SF-Pro-Text-Medium.otf',42) if os.path.exists(FD+'SF-Pro-Text-Medium.otf') else F('SF-Pro-Text-Semibold.otf',42)
    if unread:
        cw=max(57,tlen(str(unread),fcount,0)+30); cap_x1=151+cw+52
    else: cap_x1=88+33+39
    glass(img,lambda dr,w,h: dr.rounded_rectangle((0,0,w-1,h-1),radius=h/2,fill=255),(49,186,cap_x1,316))
    chev=[(121,225+3),(91,253),(121,281-3)]
    d.line([(x*SS,y*SS) for x,y in chev],fill=WHITE,width=round(6.5*SS),joint='curve')
    for x,y in (chev[0],chev[2]):
        r=3.25*SS; d.ellipse((x*SS-r,y*SS-r,x*SS+r,y*SS+r),fill=WHITE)
    if unread:
        d.rounded_rectangle((151*SS,224*SS,(151+cw)*SS,281*SS),radius=28.5*SS,fill=(238,238,240))
        d.text(((151+cw/2)*SS,(252.5)*SS),str(unread),font=fcount,fill=(28,28,30),anchor='mm')
    # video circle
    glass(img,lambda dr,w,h: dr.ellipse((0,0,w-1,h-1),fill=255),(1026,186,1158,318))
    d.rounded_rectangle((1056*SS,230*SS,1112*SS,276*SS),radius=10*SS,outline=WHITE,width=round(5*SS))
    d.polygon([(1117*SS,246*SS),(1133*SS,233*SS),(1133*SS,273*SS),(1117*SS,260*SS)],fill=WHITE)
    d.line([(1117*SS,246*SS),(1133*SS,233*SS),(1133*SS,273*SS),(1117*SS,260*SS),(1117*SS,246*SS)],fill=WHITE,width=round(3*SS),joint='curve')
    # avatar (photo or gradient+initial)
    D_=180; ax0,ay0=603-D_/2,186
    photo=ct.get('photo') or ct.get('avatar')
    m=Image.new('L',(D_*SS,D_*SS),0); ImageDraw.Draw(m).ellipse((0,0,D_*SS-1,D_*SS-1),fill=255)
    if photo and os.path.exists(photo):
        pim=Image.open(photo).convert('RGB')
        side=min(pim.size); L=(pim.width-side)//2; T=(pim.height-side)//2
        pim=pim.crop((L,T,L+side,T+side)).resize((D_*SS,D_*SS),Image.LANCZOS)
        img.paste(pim,(round(ax0*SS),round(ay0*SS)),m)
    else:
        gr=np.linspace(0,1,D_*SS)[:,None,None]
        arr=(np.array([112,113,120])*(1-gr)+np.array([72,73,80])*gr).repeat(D_*SS,1).astype(np.uint8)
        av=Image.fromarray(arr)
        img.paste(av,(round(ax0*SS),round(ay0*SS)),m)
        d.text((603*SS,(276+1)*SS),ct.get('initial','?'),font=F('SF-Pro-Display-Bold.otf',92),fill=WHITE,anchor='mm')
    # name pill — omitted when no contact name is locked, so we don't invent one
    fn=F('SF-Pro-Text-Semibold.otf',50); name=ct.get('name','')
    if name:
        nw=tlen(name,fn,-0.5); pw=41+nw+10+9+30; px0=603-pw/2
        glass(img,lambda dr,w,h: dr.rounded_rectangle((0,0,w-1,h-1),radius=h/2,fill=255),(px0,352,px0+pw,442))
        draw_text(img,px0+41,415,name,fn,WHITE,-0.5)
        cx0=px0+41+nw+10; d.line([(cx0*SS,389*SS),((cx0+8)*SS,401*SS),(cx0*SS,413*SS)],fill=(135,135,140),width=round(3.2*SS),joint='curve')
    # optional subtitle under name pill (SMS chrome)
    subtitle=ct.get('subtitle')
    if subtitle is None and sms:
        subtitle='Text Message \u00b7 SMS'
    if subtitle:
        fsub=F('SF-Pro-Text-Regular.otf',33)
        sw=tlen(subtitle,fsub,0)
        # pill bottom 442; ~18px gap then cap; matches real iOS SMS header
        draw_text(img,603-sw/2,442+14+23,subtitle,fsub,TS_COL,0)
    # ---- input bar ----
    glass(img,lambda dr,w,h: dr.ellipse((0,0,w-1,h-1),fill=255),PLUS)
    pcx,pcy=144,2478+dy
    for a_,b_ in [((pcx-23,pcy),(pcx+23,pcy)),((pcx,pcy-23),(pcx,pcy+23))]:
        d.line([(a_[0]*SS,a_[1]*SS),(b_[0]*SS,b_[1]*SS)],fill=WHITE,width=round(5*SS))
    glass(img,lambda dr,w,h: dr.rounded_rectangle((0,0,w-1,h-1),radius=h/2,fill=255),FIELD)
    draw_text(img,289,2494+dy,'Text Message \u00b7 SMS' if sms else 'iMessage',fb,PH_COL)
    mx,my=1059,2470+dy; lw=round(4.2*SS)
    d.rounded_rectangle(((mx-9)*SS,(my-18)*SS,(mx+9)*SS,(my+9)*SS),radius=9*SS,outline=PH_COL,width=lw)
    d.arc(((mx-16)*SS,(my-14)*SS,(mx+16)*SS,(my+18)*SS),start=0,end=180,fill=PH_COL,width=lw)
    d.line([(mx*SS,(my+18)*SS),(mx*SS,(my+33)*SS)],fill=PH_COL,width=lw)
    full=img.resize((W,Hc),Image.LANCZOS)
    if spec.get('out_full'): full.save(spec['out_full'])
    if spec.get('side_fill'):
        # Closer phone crop: fill 1080 width (no letterbox gutters), vertically crop to 1920.
        # Anchor near header avatar (y=186) so chrome stays; may clip status bar / input /
        # a few px of the last bubble tail. Bubbles hug left/right edges (~48*s margin).
        s=1080/W; scaled_h=round(Hc*s); scaled=full.resize((1080,scaled_h),Image.LANCZOS)
        last_b=[it for it in items if it.get('k')=='b' and 'y1' in it]
        last_y1=max(it['y1'] for it in last_b) if last_b else Hc
        win_native=1920/s
        avatar_top=186
        # Keep the whole last bubble, tail included, inside the 1920 window.
        bubble_end=last_y1+40
        crop_start=bubble_end-win_native
        if crop_start<0: crop_start=0
        # If the thread is short enough, also keep the avatar.
        if crop_start<avatar_top and avatar_top+win_native>=bubble_end:
            crop_start=avatar_top
        y0=max(0,min(scaled_h-1920, round(crop_start*s)))
        out=scaled.crop((0,y0,1080,y0+1920))
        fw=1080
        print('canvas',W,Hc,'(+%d)'%dy,'side_fill s=%.3f'%s,'crop_native %.0f..%.0f'% (y0/s,(y0+1920)/s),'| thread top',round(top),'free below header',round(top-HEADER_BOTTOM),'native =',round((top-HEADER_BOTTOM)*s),'out px')
    else:
        s=1920/Hc; fw=round(W*s); out=Image.new('RGB',(1080,1920),BG); out.paste(full.resize((fw,1920),Image.LANCZOS),((1080-fw)//2,0))
        print('canvas',W,Hc,'(+%d)'%dy,'scale->1920 %.3f'%s,'column width',fw,'| thread top',round(top),'free below header',round(top-HEADER_BOTTOM),'native =',round((top-HEADER_BOTTOM)*s),'out px')
    out.save(spec['out'])
    first=[i for i in items if i['k']=='ts' or i['k']=='b'][0]
    for it in items:
        if it['k']=='b': print(it['side'],round(it['y0']),it['w'],it['tail'],it.get('lines','[image %dx%d]'%(it['w'],it['h'])))
        else: print('TS',round(it['cap']),it['t'])
    return items
if __name__=='__main__':
    build(json.load(open(sys.argv[1])))
