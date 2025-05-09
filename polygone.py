import chainlist
from utils import projection
import tkinter as tk

class Polygone():
    def __init__(self, N, pts, contour="black",couleur='red'):
        self.n=N
        self.pts=pts
        self.contour=contour
        self.couleur=couleur
        self.sommets=None
        self.enveloppe=None
        self.voisins=[]
        self.sb=[]

    def polygone(self, vp, window, canevas): #affichage du polygone
        convertie=[projection(self.pts[0],window,vp)]
        for point in range(1,len(self.pts)):
            convertie.append(projection(self.pts[point], window, vp))
        canevas.create_polygon(tk._flatten(convertie),fill=self.couleur,outline=self.contour)

    def affiche_enveloppe(self, vp, window, canevas):
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
        self.enveloppe.append(self.enveloppe[0])

    
    def superbande(self,allpolys, window, vp):
        self.sb=(min(self.enveloppe, key=lambda x: x[0]),max(self.enveloppe, key=lambda x: x[0]))
        bande_x=(self.sb[0][0],self.sb[1][0])
        for poly in allpolys:
            if poly!=self:
                for point in poly.pts:
                    if bande_x[0]<=point[0]<=bande_x[1]:
                        self.voisins.append(poly)
                        if self not in poly.voisins:
                            poly.voisins.append(self)
                        break #peutetre faire avec un while pour eviter break
        return self.voisins
    
    def scanning(self,window,vp, canevas, liste_segments):
        for pt in self.enveloppe:
            future_collisions_poly = [] #la liste des polygones qui sont au dessus/en dessous de ce point
            future_collisions_segments = [] #la liste des segments directement au dessus/en dessous de ce point
            up_and_down = {"up":1000.0, "down":0.0} #les coordonnées en y de la droite du trapèze
            y_min_poly, y_max_poly = min(self.enveloppe, key=lambda x: x[1])[1], max(self.enveloppe, key=lambda x: x[1])[1]
            a_traiter=True
            for poly in self.voisins:
                bande_x = (poly.sb[0][0], poly.sb[1][0]) #bande_x c'est les x de superbande du voisin
                if bande_x[0] <= pt[0] <= bande_x[1]:
                    future_collisions_poly.append(poly)
            future_collisions_poly.append(self)
            if future_collisions_poly: #si il y a des polygones au dessus/en dessous
                for poly in future_collisions_poly:
                    segup=[] #segup et segdown permettent de savoir si des segments d'un même polygone sont en haut et en bas du point (pour verifier si il est a linterieur dun autre poly)
                    segdown=[]
                    for segpoint in range(0, len(poly.enveloppe) - 1): #on va parcourir tous les segments qui composent le polygone voisin
                        segment=(poly.enveloppe[segpoint], poly.enveloppe[segpoint+1])
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
                                    else:
                                        segdown.append(segment)
                                elif delta_y<0: #cas ou le segment est en haut
                                    up_and_down["up"]=min(up_and_down["up"],collision_y) #de meme
                                    if is_colliding_with_self:
                                        up_and_down["up"]=pt[1]
                                    else:
                                        segup.append(segment)
                                elif poly!=self: #si la collision se fait sur le point meme, on traite en fonction de la pente
                                    if sortedseg[0][1]<pt[1]: #si la pente est positive, le trait est a tracer en haut
                                        up_and_down["down"]=collision_y 
                                        segdown.append(segment)
                                    elif sortedseg[0][1]>pt[1]: #si la pente est negative
                                        up_and_down["up"]=collision_y
                                        segup.append(segment)
                                    else:
                                        if pt[1]==y_max_poly: #le polygone est convexe, donc si la pente est nulle on sait quon est soit au dessus soit en dessous du polygone
                                            up_and_down["up"]=pt[1]
                                            segup.append(segment)
                                        else:
                                            up_and_down["down"]=pt[1]
                                            segdown.append(segment)
                            else: #le cas ou le segment ou aura lieu la collision est vertical
                                if pt[1]<sortedseg[0][1] and pt[1]<sortedseg[1][1]: #si le point est en dessous du segment
                                    up_and_down["up"]=min(up_and_down["up"],min(sortedseg[0][1],sortedseg[1][1]))
                                    if is_colliding_with_self:
                                        up_and_down["up"]=pt[1]
                                    else:
                                        segup.append(segment)
                                elif pt[1]>sortedseg[0][1] and pt[1]>sortedseg[1][1]:
                                    up_and_down["down"]=max(up_and_down["down"],max(sortedseg[0][1],sortedseg[1][1]))
                                    if is_colliding_with_self:
                                        up_and_down["down"]=pt[1]
                                    else:
                                        segdown.append(segment)
                                else: #si le point est sur le segment
                                    up_and_down["up"]=up_and_down["down"]=pt[1]
                                    segup.append(segment)
                                    segdown.append(segment)
                    if segup and segdown:
                        a_traiter=False

            if a_traiter:
                point_haut=(pt[0],up_and_down["up"])
                point_bas=(pt[0],up_and_down["down"])
                point_haut_projete=projection(point_haut,vp,window)
                point_bas_projete=projection(point_bas,vp,window)
                ptx=projection(pt,vp,window)
                canevas.create_line(ptx[0],ptx[1],ptx[0],point_haut_projete[1], tags="segments")
                canevas.create_line(ptx[0],ptx[1],ptx[0],point_bas_projete[1], tags="segments")
                if ((ptx[0],ptx[1]),(ptx[0],point_haut_projete[1])) not in liste_segments:
                    liste_segments.append(((ptx[0],ptx[1]),(ptx[0],point_haut_projete[1]),[projection(pt, vp, window) for pt in self.enveloppe]))
                if ((ptx[0],ptx[1]),(ptx[0],point_bas_projete[1])) not in liste_segments:   
                    liste_segments.append(((ptx[0],ptx[1]),(ptx[0],point_bas_projete[1]),[projection(pt, vp, window) for pt in self.enveloppe]))