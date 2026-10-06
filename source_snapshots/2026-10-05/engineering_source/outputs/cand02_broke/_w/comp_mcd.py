import numpy as np, cv2
C=cv2.imread('../in_C.png').astype(np.float32)
S=cv2.imread('../order_complete_mcd.png')
_h=np.zeros((1850*4,850*4),np.uint8); _r=22; cv2.rectangle(_h,((425-146)*4+_r,(1850-31)*4),((425+146)*4-_r,(1850-20)*4),255,-1); [cv2.circle(_h,(cx,(1850-31)*4+_r),_r,255,-1) for cx in ((425-146)*4+_r,(425+146)*4-_r)]
_h=cv2.resize(_h,(850,1850),interpolation=cv2.INTER_AREA).astype(np.float32)[...,None]/255
S=(S*(1-_h)+15*_h).astype(np.uint8)  # iOS home indicator (visible on a photographed phone)
q=np.load('quad_c.npy').astype(np.float32)
filled=cv2.imread('filled_c.png',0)
H,W=C.shape[:2]
g=cv2.cvtColor(C.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)
er=cv2.erode(filled,np.ones((31,31),np.uint8))>0
# --- white field: robust quadratic fit per channel to bright background
ys,xs=np.where(er&(g>195)); sel=np.arange(len(xs))[::7]; xs,ys=xs[sel],ys[sel]
def basis(x,y):
    x=x/W; y=y/H; return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],1)
A=basis(xs.astype(np.float64),ys.astype(np.float64)); keep=np.ones(len(xs),bool)
for it in range(4):
    Lv=g[ys,xs]; cf,*_=np.linalg.lstsq(A[keep],Lv[keep],rcond=None); keep=Lv>A@cf-6
coef=[np.linalg.lstsq(A[keep],C[ys[keep],xs[keep],c],rcond=None)[0] for c in range(3)]
gy,gx=np.mgrid[0:H,0:W].astype(np.float64)
B=basis(gx.ravel(),gy.ravel())
Wf=np.stack([(B@coef[c]).reshape(H,W) for c in range(3)],2).astype(np.float32)
print('white field BGR at TL/center/BR:',Wf[200,350].round(1),Wf[800,600].round(1),Wf[1400,850].round(1))
# black level from darkest text in photo
dark=C[er&(g<120)]; lum=dark.mean(1); blk=dark[lum<=np.percentile(lum,0.5)].mean(0)
print('photo text black BGR',blk.round(1))
blk=np.minimum(blk,np.array([26,26,26]))*0.85+3
# noise measurement in flat bright area
hp=g-cv2.GaussianBlur(g,(0,0),2.0); flat=er&(g>200)&(np.abs(cv2.Laplacian(cv2.GaussianBlur(g,(0,0),3),cv2.CV_32F))<0.3)
print('photo noise std',hp[flat].std().round(2), 'n',flat.sum())
# --- warp screen
tw,th=int(np.linalg.norm(q[1]-q[0])),int(np.linalg.norm(q[3]-q[0]))
Sd=cv2.resize(S,(tw,th),interpolation=cv2.INTER_AREA).astype(np.float32)
src=np.float32([[0,0],[tw,0],[tw,th],[0,th]])
M=cv2.getPerspectiveTransform(src,q)
Sw=cv2.warpPerspective(Sd,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
rr=np.zeros((th*4,tw*4),np.uint8); r=int(72*4)
cv2.rectangle(rr,(r,0),(tw*4-r,th*4),255,-1); cv2.rectangle(rr,(0,r),(tw*4,th*4-r),255,-1)
for cx,cy in [(r,r),(tw*4-r,r),(r,th*4-r),(tw*4-r,th*4-r)]: cv2.circle(rr,(cx,cy),r,255,-1)
rr=cv2.resize(rr,(tw,th),interpolation=cv2.INTER_AREA)
Mw=cv2.warpPerspective(rr,M,(W,H),flags=cv2.INTER_LINEAR).astype(np.float32)/255
fd=cv2.GaussianBlur(cv2.dilate(filled,np.ones((5,5),np.uint8)).astype(np.float32)/255,(0,0),0.8)
mask=np.maximum(Mw,fd)
# --- grade: map screen 0..255 onto photographed range [black .. white field]
s=np.clip(Sw/255.0,0,1)
s=s**1.06
out=blk+(Wf-blk)*s
out=cv2.GaussianBlur(out,(0,0),0.62)
rng=np.random.default_rng(7)
n=rng.normal(0,1,(H,W,1)).astype(np.float32)*float(hp[flat].std())*1.25+rng.normal(0,0.7,(H,W,3)).astype(np.float32)
out=out+cv2.GaussianBlur(n,(0,0),0.5)*1.25
# --- island from photo on top
hole=cv2.subtract(filled,(g>150).astype(np.uint8)*255)
n2,l2,s2,_=cv2.connectedComponentsWithStats(hole)
isl=[j for j in range(1,n2) if s2[j,1]<160 and s2[j,4]>5000][0]
im=((l2==isl)*255).astype(np.uint8); im=cv2.dilate(im,np.ones((7,7),np.uint8))
imf=cv2.GaussianBlur(im.astype(np.float32)/255,(0,0),1.2)[...,None]
m3=mask[...,None]
res=C*(1-m3)+out*m3
res=res*(1-imf)+C*imf
res=np.clip(res,0,255).round().astype(np.uint8)
cv2.imwrite('../composite_mcd.png',res)
# 9:16
xs_=np.where(filled.any(0))[0]; cx=int((xs_[0]+xs_[-1])/2); x0=int(np.clip(cx-450,0,W-900))
crop=res[:,x0:x0+900]; print('916 crop x',x0,x0+900)
cv2.imwrite('../composite_mcd_916.png',cv2.resize(crop,(1080,1920),interpolation=cv2.INTER_LANCZOS4))
g2=cv2.cvtColor(res,cv2.COLOR_BGR2GRAY).astype(np.float32); hp2=g2-cv2.GaussianBlur(g2,(0,0),2.0)
fl2=er&(g2>200)&(np.abs(cv2.Laplacian(cv2.GaussianBlur(g2,(0,0),3),cv2.CV_32F))<0.3)
print('composite noise std',hp2[fl2].std().round(2),'n',fl2.sum())
