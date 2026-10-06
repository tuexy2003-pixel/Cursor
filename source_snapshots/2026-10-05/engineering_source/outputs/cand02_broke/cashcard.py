import sys
from PIL import Image, ImageDraw, ImageFont
src='/home/box/agent-data/agents/adee5ede-5650-49b5-aee0-fdce25deef5d/attachments/6ad56b9ed906513c82b35ef9304bd14f731a6a306e54ae3b30ed7cac7f9055af.png'
amt=sys.argv[1] if len(sys.argv)>1 else None
im=Image.open(src).convert('RGB')
card=im.crop((14,168,541,488))
card.save('cash_card_crop_orig.png')
if amt:
    S=4
    big=card.resize((card.width*S,card.height*S),Image.LANCZOS)
    d=ImageDraw.Draw(big)
    # find balance text bbox (bright pixels) in region
    px=card.load()
    xs=[];ys=[]
    for y in range(75,160):
        for x in range(20,400):
            r,g,b=px[x,y]
            if r>200 and g>200 and b>200: xs.append(x);ys.append(y)
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
    print('bbox',x0,y0,x1,y1)
    bg=px[x1+30,y0-8]
    d.rectangle(((x0-4)*S,(y0-6)*S,(x1+6)*S,(y1+6)*S),fill=bg)
    f=ImageFont.truetype('/workspace/creative-pipeline/outputs/proof_cand01_s1/_w/fonts/SF-Pro-Display-Bold.otf',10)
    # size font so cap height matches
    target=(y1-y0+1)*S
    size=10
    while True:
        f=ImageFont.truetype(f.path,size); bb=f.getbbox('$')
        if bb[3]-bb[1]>=target: break
        size+=1
    bb=f.getbbox(amt)
    d.text((x0*S-bb[0],y0*S-bb[1]),amt,font=f,fill=(255,255,255))
    out=big.resize((1080,round(1080*card.height/card.width)),Image.LANCZOS)
    out.save(f'cash_card_{amt.replace("$","").replace(",","")}.png')
