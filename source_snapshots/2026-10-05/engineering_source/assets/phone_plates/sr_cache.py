"""Build/refresh the cached 2x EDSR super-resolution of each phone plate (background only; the screen is composited later, so no text is ever AI-upscaled).
usage: venv/bin/python sr_cache.py [plate_name ...]"""
import cv2,numpy as np,os,sys,time
D=os.path.dirname(os.path.abspath(__file__))
def sr2(img,tile=360,pad=12):
    m=os.path.join(D,'_models','EDSR_x2.pb')
    if not os.path.exists(m): return None
    sr=cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(m); sr.setModel('edsr',2)
    H,W=img.shape[:2]; out=np.zeros((H*2,W*2,3),np.uint8)
    for y in range(0,H,tile):
        for x in range(0,W,tile):
            y0,x0=max(0,y-pad),max(0,x-pad); y1,x1=min(H,y+tile+pad),min(W,x+tile+pad)
            o=sr.upsample(np.ascontiguousarray(img[y0:y1,x0:x1]))
            ty,tx=min(tile,H-y),min(tile,W-x)
            out[2*y:2*(y+ty),2*x:2*(x+tx)]=o[2*(y-y0):2*(y-y0+ty),2*(x-x0):2*(x-x0+tx)]
    return out
if __name__=='__main__':
    names=sys.argv[1:] or ['user_A_iphone11_dark','user_B_bedsheet','user_C_car_thigh','user_D_hand_rings']
    for n in names:
        t=time.time(); im=cv2.imread(os.path.join(D,n+'.jpg')); o=sr2(im)
        cv2.imwrite(os.path.join(D,'_cache',n+'_edsr2.png'),o); print(n,o.shape,round(time.time()-t),'s',flush=True)
