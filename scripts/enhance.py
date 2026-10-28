import cv2, numpy as np, sys, os
from PIL import Image, ImageFilter
C={'torresmo':(470,440,412),'portuguesa':(436,446,400),'calabresa':(458,432,420)}
def enhance(im):
    im=cv2.fastNlMeansDenoisingColored(im,None,4,4,7,21)
    # white balance (gray world, 60%)
    f=im.astype(np.float32); m=f.reshape(-1,3).mean(0); gain=m.mean()/m; gain=1+(gain-1)*0.6
    f=np.clip(f*gain,0,255)
    # warmth
    f[...,2]*=1.04; f[...,0]*=0.96
    im=np.clip(f,0,255).astype(np.uint8)
    lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB); L,a,b=cv2.split(lab)
    L=cv2.createCLAHE(clipLimit=1.8,tileGridSize=(8,8)).apply(L)
    im=cv2.cvtColor(cv2.merge([L,a,b]),cv2.COLOR_LAB2BGR)
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(np.float32)
    s=hsv[...,1]/255; hsv[...,1]=np.clip((s+ (1-s)*s*0.55)*255,0,255)   # vibrance
    hsv[...,2]=np.clip(255*((hsv[...,2]/255)**0.93),0,255)              # leve brilho
    im=cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2BGR)
    return im
def cut(im,cx,cy,r,out=900):
    h,w=im.shape[:2]; pad=r+10
    big=cv2.copyMakeBorder(im,pad,pad,pad,pad,cv2.BORDER_REPLICATE)
    crop=big[cy+pad-r:cy+pad+r, cx+pad-r:cx+pad+r]
    crop=cv2.resize(crop,(out,out),interpolation=cv2.INTER_LANCZOS4)
    blur=cv2.GaussianBlur(crop,(0,0),2.2); crop=cv2.addWeighted(crop,1.55,blur,-0.55,0)  # unsharp
    yy,xx=np.mgrid[:out,:out]; d=np.hypot(xx-out/2,yy-out/2)/(out/2)
    alpha=np.clip((1.0-d)/0.012,0,1)
    shade=np.clip(1-(np.clip(d-0.82,0,1)/0.18)*0.25,0,1)[...,None]          # borda levemente escurecida
    crop=np.clip(crop*shade,0,255).astype(np.uint8)
    rgba=np.dstack([cv2.cvtColor(crop,cv2.COLOR_BGR2RGB),(alpha*255).astype(np.uint8)])
    return rgba
os.makedirs('final',exist_ok=True)
sheet=[]
for n,(cx,cy,r) in C.items():
    o=cv2.imread(f'orig/{n}.png')
    e=enhance(o)
    rgba=cut(e,cx,cy,r)
    Image.fromarray(rgba).save(f'final/{n}.webp',quality=84,method=6)
    # before/after panel
    ob=cv2.cvtColor(o,cv2.COLOR_BGR2RGB); ob=cv2.circle(ob.copy(),(cx,cy),r,(255,0,0),3)
    a=Image.fromarray(ob).resize((450,int(450*o.shape[0]/o.shape[1])))
    bg=Image.new('RGB',(450,450),(23,16,13)); fi=Image.fromarray(rgba).resize((430,430)); bg.paste(fi,(10,10),fi)
    p=Image.new('RGB',(920,max(a.height,450)),(40,30,25)); p.paste(a,(0,0)); p.paste(bg,(470,0)); sheet.append(p)
H=sum(s.height for s in sheet)+20*len(sheet); out=Image.new('RGB',(920,H),(40,30,25)); y=0
for s in sheet: out.paste(s,(0,y)); y+=s.height+20
out.save('antes-depois.jpg',quality=88)
print([ (f, os.path.getsize('final/'+f)) for f in os.listdir('final')])
