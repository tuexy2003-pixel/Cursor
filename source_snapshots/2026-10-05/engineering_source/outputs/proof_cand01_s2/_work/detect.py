import numpy as np, cv2
im=cv2.imread('plate_toilet_blank_gpt.png')
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
mask=cv2.inRange(hsv,(40,120,120),(85,255,255))
n,lab,stats,_=cv2.connectedComponentsWithStats(mask)
i=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]); m=(lab==i).astype(np.uint8)*255
print('green area',stats[i])
# fill holes (island) for outer shape
cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cnts,key=cv2.contourArea)
filled=np.zeros_like(m); cv2.drawContours(filled,[c],-1,255,-1)
cv2.imwrite('_work/green_mask.png',m); cv2.imwrite('_work/green_filled.png',filled)
# edges: fit lines to contour points on each side, excluding corner regions
pts=c[:,0,:].astype(np.float64)
x0,y0,w,h=cv2.boundingRect(c)
print('bbox',x0,y0,w,h)
def fit(sel):
    p=pts[sel]; vx,vy,cx,cy=cv2.fitLine(p.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel(); return (vx,vy,cx,cy), len(p)
rc=90 # exclude rounded corners
# classify points by which side of bbox they're near
left =(pts[:,0]<x0+w*0.25)&(pts[:,1]>y0+rc+40)&(pts[:,1]<y0+h-rc-40)
right=(pts[:,0]>x0+w*0.75)&(pts[:,1]>y0+rc+40)&(pts[:,1]<y0+h-rc-40)
top  =(pts[:,1]<y0+h*0.25)&(pts[:,0]>x0+rc+40)&(pts[:,0]<x0+w-rc-40)
bot  =(pts[:,1]>y0+h*0.75)&(pts[:,0]>x0+rc+40)&(pts[:,0]<x0+w-rc-40)
L=[fit(s) for s in (top,right,bot,left)]
for l in L: print(l)
def inter(a,b):
    (vx1,vy1,x1,y1),(vx2,vy2,x2,y2)=a[0],b[0]
    A=np.array([[vx1,-vx2],[vy1,-vy2]]); t=np.linalg.solve(A,[x2-x1,y2-y1]); return (x1+t[0]*vx1,y1+t[0]*vy1)
T,R,B,Lf=L
quad=[inter(T,Lf),inter(T,R),inter(B,R),inter(B,Lf)]
print('quad TL TR BR BL',[tuple(round(v,1) for v in q) for q in quad])
np.save('_work/quad.npy',np.array(quad))
# island: holes inside filled region
hole=cv2.subtract(filled,m)
n2,lab2,st2,cen2=cv2.connectedComponentsWithStats(hole)
for j in range(1,n2):
    if st2[j,4]>200: print('hole',st2[j],cen2[j])
