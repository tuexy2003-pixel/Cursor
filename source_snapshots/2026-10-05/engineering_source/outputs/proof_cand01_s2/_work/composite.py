import numpy as np, cv2
rng=np.random.default_rng(7)
plate=cv2.imread('plate_toilet_blank_gpt.png').astype(np.float32)   # BGR
scr=cv2.imread('screen_checkout_v1.png').astype(np.float32)
Hh,Ww=plate.shape[:2]
q=np.load('_work/quad.npy').astype(np.float32)
# --- soft key from green excess ---
B,G,R=cv2.split(plate)
exc=G-np.maximum(R,B)
alpha=np.clip((exc-40)/(200-40),0,1)
# keep only main screen component (+ its soft edge)
hard=(exc>120).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(hard)
main=(lab==1+np.argmax(st[1:,4])).astype(np.uint8)
region=cv2.dilate(main,np.ones((7,7),np.uint8))
alpha=alpha*region
alpha=cv2.GaussianBlur(alpha,(0,0),0.7)
alpha=np.where(main>0,np.maximum(alpha,cv2.erode(main,np.ones((3,3),np.uint8)).astype(np.float32)),alpha)
# --- warp screen: pre-downscale with INTER_AREA, then perspective warp ---
s=0.54
small=cv2.resize(scr,(int(1170*s),int(2532*s)),interpolation=cv2.INTER_AREA)
src=np.float32([[0,0],[small.shape[1],0],[small.shape[1],small.shape[0]],[0,small.shape[0]]])
# expand quad a hair so the rounded-corner mask is fully covered
M=cv2.getPerspectiveTransform(src,q)
warp=cv2.warpPerspective(small,M,(Ww,Hh),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
# --- grade the screen to the room ---
w=warp/255.0
w=0.10+0.86*w                     # lift blacks, pull whites down (white ~0.96)
tint=np.array([0.86,0.95,1.00])   # BGR multipliers -> warm (less blue, slightly less green)
w=w*tint
# faint diagonal glare + slight falloff toward bottom-left
yy,xx=np.mgrid[0:Hh,0:Ww].astype(np.float32)
u=((xx-q[:,0].min())/np.ptp(q[:,0]) + (yy-q[:,1].min())/np.ptp(q[:,1]))/2
glare=1.0+0.035*np.exp(-((u-0.28)/0.16)**2)-0.04*u
w=w*glare[...,None]
w=np.clip(w,0,1)*255
w=cv2.GaussianBlur(w,(0,0),0.55)
noise=rng.normal(0,1.6,(Hh,Ww,1)).astype(np.float32)
w=w+noise+rng.normal(0,0.6,(Hh,Ww,3)).astype(np.float32)
# --- despill plate edge pixels (bezel/island rims) ---
p=plate.copy()
lim=np.maximum(p[...,0],p[...,2])*1.0+1
spill=p[...,1]>lim
p[...,1]=np.where(spill,lim,p[...,1])
filled=(cv2.imread('_work/green_filled.png',0)>0).astype(np.uint8)
edge=cv2.dilate(filled,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(31,31)))>0
p=np.where(edge[...,None],p,plate)
a=alpha[...,None]
out=w*a+p*(1-a)
out=np.clip(out,0,255).astype(np.uint8)
cv2.imwrite('composite_code_v1.png',out)
x0,y0=int(q[:,0].min())-25,int(q[:,1].min())-25; x1,y1=int(q[:,0].max())+25,int(q[:,1].max())+25
cv2.imwrite('composite_code_v1_zoom.png',out[max(0,y0):y1,max(0,x0):x1])
# residual green check
o=out.astype(int); ex=o[...,1]-np.maximum(o[...,0],o[...,2])
print('pixels with green excess>25:',int((ex>25).sum()),' >12:',int((ex>12).sum()))
