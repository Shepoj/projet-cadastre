import tkinter as tk
import numpy as np
import chainlist

poly = [[5.9889548,43.1210753],[5.9889715,43.1209775],[5.9889815,43.1209784],[5.9889867,43.1209474],[5.9889465,43.1209438],[5.9889485,43.1209321],[5.9889195,43.1209295],[5.9888752,43.1209255],[5.9888653,43.1209033],[5.9888822,43.1208992],[5.9888836,43.1208906],[5.9888709,43.1208706],[5.9888869,43.1208668],[5.9888936,43.1208275],[5.9891953,43.1208555],[5.989178,43.1209569],[5.9891656,43.1209558],[5.9891529,43.1210301],[5.9891476,43.1210296],[5.9891425,43.1210601],[5.9891348,43.1210623],[5.9890993,43.1210591],[5.9890967,43.1210748],[5.9890792,43.1210813],[5.9890376,43.1210775],[5.9890368,43.1210827],[5.9889548,43.1210753]]


lat=[]
long=[]

for point in poly:
    lat.append(point[1])
    long.append(point[0])



ymin,xmin,ymax,xmax = min(lat),min(long),max(lat),max(long)
ratio = (xmax-xmin)/(ymax-ymin)

def projection(point,wc,vp): #point : (x,y) wc : (x, y, dimx, dimy) viewport : (x,y, dimx,dimy)
    (xwc,ywc)=(-wc[0],-wc[1])
    (largeurwc, hauteurwc)=(wc[2],wc[3])
    (largeurviewport, hauteurviewport)=(vp[2],vp[3])
    (xvp,yvp)=vp[0:2]
    a=[(1/largeurwc)*largeurviewport , 0 , (1/largeurwc)*xwc*largeurviewport+xvp]
    b=[0 , -(1/hauteurwc)*hauteurviewport , hauteurviewport-(1/hauteurwc)*ywc*hauteurviewport+yvp]
    c=[0,0,1]
    visu=[a,b,c]
    point3d=[point[0],point[1],1]
    return [int(i) for i in np.matmul(visu,point3d)[:2]]


class Polygone():
    def __init__(self, N, pts, contour="black",couleur='red'):
        self.n=N
        self.pts=pts
        self.contour=contour
        self.couleur=couleur
        self.sommets=None
        self.enveloppe=None

    def polygone(self, vp, window):
        convertie=[projection(self.pts[0],window,vp)]
        for point in range(1,len(self.pts)):
            convertie.append(projection(self.pts[point], window, vp))
        canevas.create_polygon(tk._flatten(convertie),fill=self.couleur,outline=self.contour)

    def affiche_enveloppe(self, vp, window):
        self.cling()
        self.convexite()
        convertie=[projection(self.pts[0],window,vp)]
        for point in range(1,len(self.enveloppe)):
            convertie.append(projection(self.enveloppe[point], window, vp))
        canevas.create_polygon(tk._flatten(convertie),fill='blue',outline=self.contour)

    def cling(self):
        self.sommets=chainlist.DoublyLinkedList()
        for point in self.pts:
            n=chainlist.Node(point)
            self.sommets.insert_back(n)
        print(self.sommets)

    def angledet(self,a,b,c):
        ax,ay=a
        bx,by=b
        cx,cy=c
        ab=(ax-bx,ay-by)
        bc=(bx-cx,by-cy)
        abc=ab[0]*bc[1]-ab[1]*bc[0]
        if abc<0:
            return False
        else:
            return True
    
    def convexite(self):
        nd=self.sommets.head
        while nd.next is not None:
            if nd.prev:
                a=nd.prev.data
            else:
                a=self.sommets.tail.data
            b=nd.data
            if nd.next:
                c=nd.next.data
            else:
                c=self.sommets.head.data
            cond=self.angledet(a,b,c)
            if not cond:
                self.sommets.delete(b)
            nd=nd.next
        self.enveloppe=self.sommets.to_list()



win= tk.Tk()
canevas=tk.Canvas(win,width=500*ratio,height=500, bg="white")
canevas.pack()

pol=Polygone(len(poly),poly)

pol.affiche_enveloppe([0,0,500*ratio,500],[xmin,ymin, xmax-xmin,ymax-ymin])
pol.polygone([0,0,500*ratio,500],[xmin,ymin, xmax-xmin,ymax-ymin])

win.mainloop()

