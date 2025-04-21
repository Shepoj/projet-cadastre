import json
import tkinter as tk
import numpy as np
import chainlist
import winsound
import random

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
    def __init__(self, N, pts, contour="black",couleur='red',tags="tag"):
        self.n=N
        self.pts=pts
        self.contour=contour
        self.couleur=couleur
        self.sommets=None
        self.enveloppe=None
        self.voisins=[]
        self.sb=[]
        self.tags=tags

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
        canevas.create_polygon(tk._flatten(convertie),fill='blue',outline=self.contour, tag=self.tags)
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

    
    def superbande(self,allpolys, window, vp):
        self.sb=(min(self.enveloppe, key=lambda x: x[0]),max(self.enveloppe, key=lambda x: x[0]))
        bande_x=(self.sb[0][0],self.sb[1][0])
        for point in self.sb:
            converted=projection(point, vp, window)
            #canevas.create_line(converted[0],0,converted[0],600)
        for poly in allpolys:
            if poly!=self:
                for point in poly.pts:
                    if bande_x[0]<=point[0]<=bande_x[1]:
                        self.voisins.append(poly)
                        break #peutetre faire avec un while pour eviter break
        return self.voisins
    
    def scanning(self,window,vp):
        for pt in self.enveloppe:
            future_collisions_poly = [] #la liste des polygones qui sont au dessus/en dessous de ce point
            future_collisions_segments = [] #la liste des segments directement au dessus/en dessous de ce point
            up_and_down = {"up":1000.0, "down":0.0} #les coordonnées en y de la droite du trapèze
            y_min_poly, y_max_poly = min(self.enveloppe, key=lambda x: x[1])[1], max(self.enveloppe, key=lambda x: x[1])[1]
            for poly in self.voisins:
                bande_x = (poly.sb[0][0], poly.sb[1][0]) #bande_x c'est les x de superbande du voisin
                if bande_x[0] <= pt[0] <= bande_x[1]:
                    future_collisions_poly.append(poly)
            future_collisions_poly.append(self)
            if future_collisions_poly: #si il y a des polygones au dessus/en dessous
                for poly in future_collisions_poly:
                    for segpoint in range(0, len(poly.pts) - 1): #on va parcourir tous les segments qui composent le polygone voisin
                        segment=(poly.pts[segpoint], poly.pts[segpoint+1])
                        sortedseg=sorted(segment, key=lambda x: x[0]) #sortedseg c'est le segment trié selon x
                        bande_x_seg=(sortedseg[0][0], sortedseg[1][0])#bande_x_seg c'est les x de la superbande du segment courant
                        is_colliding_with_self= poly==self and pt not in segment

                        if bande_x_seg[0] <= pt[0] <= bande_x_seg[1]: #si le point est dans la superbande du segment
                            if segment[0][0] != segment[1][0]:
                                pente=(segment[0][1]-segment[1][1])/(segment[0][0]-segment[1][0])#calcul de la pente
                                delta_x=pt[0]-sortedseg[0][0] #la distance entre le plus petit x du segment et le x du point quon traite
                                collision_y=sortedseg[0][1]+delta_x*pente #on calcule le y ou aura lieu l'intersection
                                delta_y=pt[1]-collision_y #la distance entre le y du point et celui de lintersection, pour savoir si le segment est en haut ou en bas
                                if delta_y>0: #cas ou le segment est en bas
                                    up_and_down["down"]=max(up_and_down["down"],collision_y) #on dit que la collision en bas c'est le point le plus proche du point actuel
                                    if is_colliding_with_self:
                                        up_and_down["down"]=pt[1]
                                elif delta_y<0: #cas ou le segment est en haut
                                    up_and_down["up"]=min(up_and_down["up"],collision_y) #de meme
                                    if is_colliding_with_self:
                                        up_and_down["up"]=pt[1]
                                elif poly!=self: #si la collision se fait sur le point meme, on traite en fonction de la hauteur du 1er point, le seul cas ou ca pose probleme cest une ligne horizontale et on va l'ignorer
                                    if sortedseg[0][1]<pt[1]: #si la pente est positive, le trait est a tracer en haut
                                        up_and_down["down"]=collision_y 
                                    elif sortedseg[0][1]>pt[1]: #si la pente est negative
                                        up_and_down["up"]=collision_y
                                    else:
                                        if pt[1]==y_max_poly: #le polygone est convexe, donc si la pente est nulle on sait quon est soit au dessus soit en dessous du polygone
                                            up_and_down["up"]=pt[1]
                                        else:
                                            up_and_down["down"]=pt[1]
                            else: #le cas ou le segment ou aura lieu la collision est vertical
                                if pt[1]<sortedseg[0][1] and pt[1]<sortedseg[1][1]: #si le point est en dessous du segment
                                    up_and_down["up"]=min(up_and_down["up"],min(sortedseg[0][1],sortedseg[1][1]))
                                    if is_colliding_with_self:
                                        up_and_down["up"]=pt[1]
                                elif pt[1]>sortedseg[0][1] and pt[1]>sortedseg[1][1]:
                                    up_and_down["down"]=max(up_and_down["down"],max(sortedseg[0][1],sortedseg[1][1]))
                                    if is_colliding_with_self:
                                        up_and_down["down"]=pt[1]
                                else: #si le point est sur le segment
                                    up_and_down["up"]=up_and_down["down"]=pt[1]

            point_haut=(pt[0],up_and_down["up"])
            point_bas=(pt[0],up_and_down["down"])
            point_haut_projete=projection(point_haut,vp,window)
            point_bas_projete=projection(point_bas,vp,window)
            ptx=projection(pt,vp,window)
            canevas.create_line(ptx[0],ptx[1],ptx[0],point_haut_projete[1])
            canevas.create_line(ptx[0],ptx[1],ptx[0],point_bas_projete[1])


win= tk.Tk()
canevas=tk.Canvas(win,width=600*ratio,height=600, bg="white")
canevas.pack()

myPolygons=[]




def sleep_show(poly):
    global allpoints,polys
    pol=Polygone(len(polys[poly]),polys[poly],tags="tag"+str(poly))
    allpoints+=pol.affiche_enveloppe([25,25,525*ratio,525],[xmin,ymin, xmax-xmin,ymax-ymin])
    freq=random.randint(4,20)*100
    winsound.Beep(freq, 1000)
    win.after(1000, sleep_show, (poly+1)%len(polys))
    canevas.delete("tag"+str(poly-1))
    myPolygons.append(pol)

win.after(500,sleep_show, 0)

win.mainloop()