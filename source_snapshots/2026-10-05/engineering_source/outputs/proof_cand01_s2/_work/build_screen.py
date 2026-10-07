import numpy as np
from PIL import Image, ImageDraw, ImageFont
G='/usr/share/fonts/truetype/sand-box/google/'
W,H=1170,2532
EXP=Image.open('dd_checkout_expanded.png').convert('RGB')
COL=Image.open('dd_checkout_full_01.png').convert('RGB')
E=np.asarray(EXP).astype(np.float32)
RED=(235,23,0)      # sampled from real 'Saving $3.49 with Deals' text
INK=(25,25,25)      # sampled real DoorDash text color

def glyph_alpha(arr,x0,x1,y0,y1,bg,ink):
    L=arr[y0:y1,x0:x1].mean(axis=2)
    return np.clip((bg-L)/(bg-ink),0,1)

def paste_alpha(canvas,alpha,x,y,color):
    h,w=alpha.shape
    reg=canvas[y:y+h,x:x+w]
    c=np.array(color,np.float32)
    canvas[y:y+h,x:x+w]=reg*(1-alpha[...,None])+c*alpha[...,None]

# ---------------- PRICE CARD (surgical edit) ----------------
P0,P1=5780,6403           # card incl. borders
CUT=6019                  # whitespace between Subtotal and Delivery Fee rows
PITCH=102                 # real row pitch (5945->6047->6149)
top=E[P0:CUT].copy(); bot=E[CUT:P1].copy()
band=np.repeat(E[CUT:CUT+1],PITCH,axis=0)   # blank card interior line (with real side borders)
price=np.concatenate([top,band,bot],axis=0)
off=lambda y: y-P0                           # source y (above cut) -> price y
offb=lambda y: y-P0+PITCH                    # source y (below cut) -> price y
SUB_BASE=5985
new_base=off(SUB_BASE)+PITCH
# label
pim=Image.fromarray(price.astype(np.uint8)); d=ImageDraw.Draw(pim)
fig=ImageFont.truetype(G+'Figtree/Figtree-VariableFont_wght.ttf',48); fig.set_variation_by_axes([480])
# left margin: match 'S' of Subtotal ink-left at x=101 ; find ink offset of 'm'
bb=fig.getbbox('mydashperks.com',anchor='ls')
d.text((101-bb[0]+1-1,new_base),'mydashperks.com',font=fig,fill=INK,anchor='ls')
price=np.asarray(pim).astype(np.float32).copy()
# amount -$40.00 from real glyph crops, recolored to RED via alpha extraction
# (x0,x1,y0,y1,src_baseline,bg,ink)
G_DOLLAR=(933,957,5945,5991,5985,255,25)
G_DOT=(1017,1024,5978,5985,5985,255,25)
G_FOUR=(979,1005,4364,4398,4398,255,96)      # from item price $4.89 (same size/weight, gray -> alpha)
G_ZERO=(976,1004,3608,3642,3642,255,96)      # from item price $30.55
G_HYPH=(353,369,3625,3630,3642,255,25)       # hyphen from item title 'Chick-fil-A'
seq=[G_HYPH,G_DOLLAR,G_FOUR,G_ZERO,G_DOT,G_ZERO,G_ZERO]
gaps=[4,3,4,5,4,4]   # measured real inter-glyph gaps ($4=3, 0.=5, .5=3, 55=4, 30=4)
PAD=2  # include 2px margin rows/cols for antialias
widths=[g[1]-g[0] for g in seq]
total=sum(widths)+sum(gaps)
xr=1069
x=xr-total
for i,g in enumerate(seq):
    x0,x1,y0,y1,b,bg,ink=g
    a=glyph_alpha(E,x0-1,x1+1,y0-2,y1+2,bg,ink)
    paste_alpha(price,a,x-1,new_base-(b-(y0-2)),RED)
    x+=widths[i]+(gaps[i] if i<len(gaps) else 0)
# Total before tip: $85.34 -> $45.34 (bold 4 from same row)
TB=6331  # baseline of total row digits (ink bottom 6330 +1)
ty=lambda y: offb(y)
# erase $ and 8 region
x_er0,x_er1=914,974
price[ty(6285):ty(6342),x_er0:x_er1]=255
def copy_patch(dst,src,sx0,sx1,sy0,sy1,dx,dy):
    patch=src[sy0:sy1,sx0:sx1]
    reg=dst[dy:dy+(sy1-sy0),dx:dx+(sx1-sx0)]
    dst[dy:dy+(sy1-sy0),dx:dx+(sx1-sx0)]=np.minimum(reg,patch)
# $ : 917-943 -> shift left 1 ; 4: 1043-1070 placed so its right edge = 972
copy_patch(price,E,917,943,6286,6340,916,ty(6286))
copy_patch(price,E,1043,1070,6286,6340,945,ty(6286))
PRICE=price.astype(np.uint8)
Image.fromarray(PRICE).save('_work/price_card_edited.png')

# ---------------- ASSEMBLE ----------------
canvas=np.full((H,W,3),255,np.float32)
y=141
hdr=np.asarray(COL.crop((0,72,W,213))).astype(np.float32); canvas[y:y+hdr.shape[0]]=hdr; y+=hdr.shape[0]
HDR_END=y
cart=np.asarray(EXP.crop((0,3545,W,4722))).astype(np.float32)
cartb=np.asarray(COL.crop((0,3528,W,3598))).astype(np.float32)
canvas[y:y+cart.shape[0]]=cart; y+=cart.shape[0]
canvas[y:y+cartb.shape[0]]=cartb; y+=cartb.shape[0]
CART_END=y
y+=30
PRICE_TOP=y
canvas[y:y+PRICE.shape[0]]=PRICE; y+=PRICE.shape[0]
PRICE_END=y
print('header end',HDR_END,'cart end',CART_END,'price',PRICE_TOP,PRICE_END)

# ---------------- FOOTER: enabled Place Order ----------------
HOME_H=15; HOME_B=24
BTN_H=120; BTN_X0,BTN_X1=24,1146
btn_top=H-HOME_B-HOME_H-30-BTN_H
div_y=btn_top-38     # real: divider 7068-7070, button top 7107
print('divider',div_y,'btn',btn_top, 'space above divider', div_y-PRICE_END)
assert div_y>=PRICE_END
canvas[div_y:H]=255
canvas[div_y:div_y+3]=228
S=4
big=Image.new('L',((BTN_X1-BTN_X0)*S,BTN_H*S),0)
ImageDraw.Draw(big).rounded_rectangle((0,0,(BTN_X1-BTN_X0)*S-1,BTN_H*S-1),radius=BTN_H*S//2,fill=255)
m=np.asarray(big.resize((BTN_X1-BTN_X0,BTN_H),Image.LANCZOS)).astype(np.float32)/255
paste_alpha(canvas,m,BTN_X0,btn_top,RED)
# button text: real glyphs from disabled button (bg 247, ink 178) -> white; '9' replaced by bold '5' from Total row
bdy=btn_top-7107
tx=glyph_alpha(E,340,692,7138,7192,247,178)       # 'Place Order' + '$'
paste_alpha(canvas,tx,340,7138+bdy,(255,255,255))
five=glyph_alpha(E,974,1002,6293,6334,255,25)      # bold 5 (w26) at 975-1001, baseline 6331
paste_alpha(canvas,five,692,7182-(6331-6293)+bdy,(255,255,255))  # button baseline 7182 (ink bottom)
rest=glyph_alpha(E,720,824,7138,7192,247,178)   # '4.02'
paste_alpha(canvas,rest,720,7138+bdy,(255,255,255))
# home indicator
big=Image.new('L',(402*S,HOME_H*S),0); ImageDraw.Draw(big).rounded_rectangle((0,0,402*S-1,HOME_H*S-1),radius=HOME_H*S//2,fill=255)
m=np.asarray(big.resize((402,HOME_H),Image.LANCZOS)).astype(np.float32)/255
paste_alpha(canvas,m,(W-402)//2,H-HOME_B-HOME_H,(0,0,0))

# ---------------- STATUS BAR ----------------
canvas[0:141]=255
SB_CY=int(open('_work/sb_cy.txt').read()) if __import__('os').path.exists('_work/sb_cy.txt') else 88
sb=Image.new('L',(W*S,141*S),0); sd=ImageDraw.Draw(sb)
inter=ImageFont.truetype(G+'Inter/Inter-VariableFont_opsz,wght.ttf',50*S); inter.set_variation_by_axes([32,620])
tb=inter.getbbox('6:15',anchor='ls'); capH=-inter.getbbox('6',anchor='ls')[1]
tcx=183*S
sd.text((tcx-(tb[0]+tb[2])/2, SB_CY*S+capH/2),'6:15',font=inter,fill=255,anchor='ls')
# right cluster: cellular bars, wifi, battery (iOS proportions, pt*3)
u=3*S
bat_w,bat_h=27.3*u,13*u
bx1=1170*S-31*u; bx0=bx1-bat_w
by0=SB_CY*S-bat_h/2
# battery body outline (35% opacity) + fill (80%)
body=Image.new('L',sb.size,0); bd=ImageDraw.Draw(body)
bd.rounded_rectangle((bx0,by0,bx0+24.5*u,by0+bat_h),radius=4.3*u,outline=255,width=int(1.1*u))
bd.rounded_rectangle((bx0+25.6*u,by0+4.3*u,bx0+27.0*u,by0+bat_h-4.3*u),radius=0.9*u,fill=255)
sb=Image.fromarray(np.maximum(np.asarray(sb),(np.asarray(body)*0.4).astype(np.uint8)))
sd=ImageDraw.Draw(sb)
sd.rounded_rectangle((bx0+2.1*u,by0+2.1*u,bx0+2.1*u+(24.5-4.2)*u*0.78,by0+bat_h-2.1*u),radius=2.5*u,fill=255)
# wifi: 3 concentric wedges
wx1=bx0-6.5*u; ww=15.3*u; wcx=wx1-ww/2; wbase=SB_CY*S+5.4*u
for r_out,r_in in [(11.0,8.3),(7.3,4.7),(3.6,0)]:
    R=r_out*u
    sd.pieslice((wcx-R,wbase-R,wcx+R,wbase+R),start=-135,end=-45,fill=255)
    if r_in>0:
        Ri=r_in*u; sd.pieslice((wcx-Ri,wbase-Ri,wcx+Ri,wbase+Ri),start=-135,end=-45,fill=0)
# cellular: 4 bars
cx1=wcx-ww/2-6.0*u; bw=3.0*u; gap=1.6*u
hs=[4.0,6.3,8.7,11.0]
x0=cx1-(4*bw+3*gap); base=SB_CY*S+5.5*u
for i,hh in enumerate(hs):
    xx=x0+i*(bw+gap); sd.rounded_rectangle((xx,base-hh*u,xx+bw,base),radius=0.9*u,fill=255)
sba=np.asarray(sb.resize((W,141),Image.LANCZOS)).astype(np.float32)/255
paste_alpha(canvas,sba,0,0,(0,0,0))
Image.fromarray(canvas.clip(0,255).astype(np.uint8)).save('screen_checkout_v1.png')
print('saved')
