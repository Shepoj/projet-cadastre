import json
import tkinter as tk
import numpy as np
import chainlist

file = open("cadastre-83062-batiments.json","r")
data = json.load(file)
file.close()

polys=[]

lat=[]
long=[]
allpoints=[]

for feature in data["features"][6060:6194]: #recuperer les points et les ajouter dans la liste de latitude, de longitude et de tous les points
    polys.append(feature["geometry"]["coordinates"][0][0])
    for point in feature["geometry"]["coordinates"][0][0]:
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
    b=[0 , -(1/hauteurwc)*hauteurviewport , hauteurviewport-(1/hauteurwc)*ywc*hauteurviewport+yvp] #ca oui
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

    def polygone(self, vp, window): #affichage du polygone
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
        return self.enveloppe

    def cling(self): #transforme la liste des sommets en liste chainee
        self.sommets=chainlist.DoublyLinkedList()
        for point in self.pts:
            n=chainlist.Node(point)
            self.sommets.insert_back(n)

    def angledet(self,a,b,c): #verifie lobtusite dun angle
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
    
    def convexite(self): #supprime les sommets qui forment les trous concaves dans un polygone : crée l'enveloppe dans self.enveloppe
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

def trapeze(points, window, vp):
    for point in points:
        converted=projection(point, vp, window)
        print(converted)
        canevas.create_line(converted[0],0,converted[0],500)

win= tk.Tk()
canevas=tk.Canvas(win,width=500*ratio,height=500, bg="white")
canevas.pack()
allpoints=[]

for bat in polys:
    poly=Polygone(len(bat),bat)
    allpoints+=poly.affiche_enveloppe([0,0,500*ratio,500],[xmin,ymin, xmax-xmin,ymax-ymin])
   
    #poly.polygone([0,0,500*ratio,500],[xmin,ymin, xmax-xmin,ymax-ymin])


#trapeze(allpoints,[0,0,500*ratio,500],[xmin,ymin, xmax-xmin,ymax-ymin])
win.mainloop()  