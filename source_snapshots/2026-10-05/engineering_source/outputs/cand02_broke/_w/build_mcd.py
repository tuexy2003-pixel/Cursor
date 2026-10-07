import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from rend import *
V=np.asarray(Image.open('../../proof_cand01_s2/order_complete_v3.png').convert('RGB')).astype(float)
out=np.full((1850,850,3),255.)
out[0:637]=V[0:637]
BLK=(17,17,17); GRY=(76,76,76); GRN=(0x00,0x83,0x2D)
SFT=SF+'SF-Pro-Text-Semibold.otf'
# ---- status bar: inpaint time digits + battery
u8=np.clip(out[:120],0,255).astype(np.uint8)[:,:,::-1].copy()
m=np.zeros(u8.shape[:2],np.uint8); m[48:88,94:212]=255; m[48:88,710:776]=255
u8=cv2.inpaint(u8,m,6,cv2.INPAINT_TELEA); out[:120]=u8[:,:,::-1]
x0,x1=put_ink(out,'8:36',35.5,101,80,(0,0,0),w=None,blur=0.35,path=SFT)
print('time ink',x0,x1)
P=V[50:86,180:212]; L=P.mean(2,keepdims=True); A=np.clip((215-L)/170,0,1)
dx=x1+9-183; reg=out[50:86,180+dx:212+dx]; reg[:]=reg*(1-A)+np.minimum(P,reg)*A
print('arrow shift',dx)
# battery (4x supersampled RGBA)
S=4; bw,bh=64,34
bat=Image.new('RGBA',(bw*S,bh*S),(0,0,0,0)); d=ImageDraw.Draw(bat)
bx0,by0,bx1,by1=2,4,48,28  # body
d.rounded_rectangle([bx0*S,by0*S,bx1*S,by1*S],radius=7.5*S,outline=(0,0,0,105),width=int(2.3*S))
fill_w=(bx1-bx0-9)*0.30
d.rounded_rectangle([(bx0+4.5)*S,(by0+4.5)*S,(bx0+4.5+fill_w)*S,(by1-4.5)*S],radius=3*S,fill=(0,0,0,255))
d.rounded_rectangle([(bx1+2)*S,12*S,(bx1+5)*S,20*S],radius=2*S,fill=(0,0,0,105))
bat=bat.resize((bw,bh),Image.LANCZOS)
ba=np.asarray(bat).astype(float); al=ba[...,3:4]/255
reg=out[51:51+bh,715:715+bw]; reg[:]=reg*(1-al)+ba[...,:3]*al
# ---- McDonald's logo circles
arch=Image.open('mcd_arches.png').convert('RGBA')
def logo(cx,cy,D=83):
    S=4; L=Image.new('RGBA',(D*S,D*S),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.ellipse([0,0,D*S-1,D*S-1],fill=(218,41,28,255))
    aw=int(D*S*0.60); ah=int(aw*arch.height/arch.width)
    a2=arch.resize((aw,ah),Image.LANCZOS)
    L.alpha_composite(a2,((D*S-aw)//2,(D*S-ah)//2+int(0.02*D*S)))
    L=L.resize((D,D),Image.LANCZOS); la=np.asarray(L).astype(float); al=la[...,3:4]/255
    X0=int(round(cx-D/2)); Y0=int(round(cy-D/2))
    reg=out[Y0:Y0+D,X0:X0+D]; reg[:]=reg*(1-al)+la[...,:3]*al
out[266:362,722:822]=255; logo(771.5,313.5)
out[524:618,28:126]=255; logo(76.5,570.5)
# ---- date line
out[322:368,28:600]=255
put_ink(out,'Thursday, Sep 24, 2026 at 8:31 PM',33.4,36,352,GRY,w=360)
# ---- store row
out[535:615,140:760]=255
put_ink(out,"McDonald's",31,151,564,BLK,w=450)
put_ink(out,'1 item',25.5,151,598,GRY,w=360)
# ---- item row
out[637:773]=255; out[773:776]=V[773:776]
T=Image.open('../in_A.png').convert('RGB').crop((70,70,277,265))
t=np.asarray(T).astype(float)
bg=np.median(np.concatenate([t[:8].reshape(-1,3),t[-8:].reshape(-1,3),t[:,:8].reshape(-1,3),t[:,-8:].reshape(-1,3)]),0)
t=np.clip(t*255/bg,0,255)
lum=t.mean(2,keepdims=True); k=np.clip((lum-238)/12,0,1)   # push near-white to pure white
t=t*(1-k)+255*k
T=Image.fromarray(t.astype(np.uint8)).resize((124,117),Image.LANCZOS)
out[705-58:705-58+117,38:38+124]=np.asarray(T).astype(float)
put_ink(out,'1 × Deluxe Spicy McCrispy™ Meal',26,202,676,BLK,w=450)
put_ink(out,'Large, Sprite® Berry Blast, French Fries',26,202,708,GRY,w=360)
put_ink(out,'$13.99',26,202,742,BLK,w=450)
# ---- price block (drop Dasher Tip), shifted
out[776:973]=V[1455:1652]
out[973:1133]=V[1690:1850]
out[1133:]=255
for base,txt,col,w in [(812,'$13.99',GRY,360),(889,'-$10.00',GRN,360),(927,'$2.99',GRY,360),(965,'$1.10',GRY,360),(1004,'$8.08',BLK,410)]:
    y=base; out[y-24:y+8,560:830]=255 if txt!='x' else 0
    put_ink(out,txt,26.6,808,base,col,w=w,align='r')
# payment row
out[1100:1133,140:720]=255; out[1070:1125,560:830]=255
put_ink(out,'$8.08',27,808,1105,BLK,w=410,align='r')
put_ink(out,'Visa •••• 5821 · 9/24/26, 7:58 PM',27,152,1125,GRY,w=360)
out[1072:1122,36:118]=255
S=4; bw,bh=46,30
B=Image.new('RGBA',(bw*S,bh*S),(0,0,0,0)); d=ImageDraw.Draw(B)
d.rounded_rectangle([0,0,bw*S-1,bh*S-1],radius=5*S,fill=(255,255,255,255),outline=(214,214,214,255),width=int(1.2*S))
vm=Image.open('visa_mark.png').crop((0,324,960,635)); vw=int(34*S); vh=int(vw*vm.height/vm.width)
B.alpha_composite(vm.resize((vw,vh),Image.LANCZOS),((bw*S-vw)//2,(bh*S-vh)//2))
B=B.resize((bw,bh),Image.LANCZOS); ba=np.asarray(B).astype(float); al=ba[...,3:4]/255
reg=out[1096-15:1096-15+bh,75-23:75-23+bw]; reg[:]=reg*(1-al)+ba[...,:3]*al
Image.fromarray(np.clip(out,0,255).round().astype(np.uint8)).save('../order_complete_mcd.png')
print('ok')
