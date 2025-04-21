import numpy as np
from shapely.geometry import LineString, Polygon
import math
import random


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

def segment_traverse_polygone(p1, p2, polygone):
    # Test si le segment p1->p2 coupe le polygone
    ligne = LineString([p1, p2])
    poly = Polygon(polygone)
    return ligne.crosses(poly)

def segment_traverse_polygones(p1, p2, polygones):
    # Test si le segment p1->p2 coupe l'un des polygones dans la liste
    for polygone in polygones:
        if segment_traverse_polygone(p1, p2, polygone):
            return True
    return False

# fonction pour calculer le barycentre de 2 points
def barycentre(points):
    n = len(points)
    if n == 0:
        return None  # erreur
    
    # recuperer les 2 x differents
    unique_x = list(set(p[0] for p in points))

    if len(unique_x) == 2:  # on a 2 points differents
        x = (unique_x[0]+unique_x[1]) / 2
    else:   # on a 1 seul point
        x = sum(p[0] for p in points) / n
    y = sum(p[1] for p in points) / n
    return (x, y)

# test si les 2 segments sont "voisins" sans verification du barycentre
def test2(point1, point2):
    if (point2.sommet_bas[1] <= point1.sommet_bas[1] and point2.sommet_haut[1] >= point1.sommet_haut[1]) or \
             (point2.sommet_bas[1] >= point1.sommet_bas[1] and point2.sommet_haut[1] <= point1.sommet_haut[1]) or \
             (point2.sommet_haut[1] >= point1.sommet_bas[1] and point2.sommet_haut[1] <= point1.sommet_haut[1]) or \
             (point2.sommet_bas[1] >=point1.sommet_bas[1] and point2.sommet_bas[1] <= point1.sommet_haut[1]):
        return True
    else:
        return False

# distance entre 2 points de type PointGraph
def distance_euclidienne(p1, p2):
    x1, y1 = p1.p
    x2, y2 = p2.p
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# distance entre 2 tuples (x, y)
def distance_euclidienne_xy(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def generer_points_et_chercher_plus_proche(graphe, largeur, hauteur):
    # Générer deux points aléatoires (x, y)
    x1 = random.uniform(0, largeur)
    y1 = random.uniform(0, hauteur)

    x2 = random.uniform(0, largeur)
    y2 = random.uniform(0, hauteur)

    pt1 = (x1, y1)
    pt2 = (x2, y2)

    # Trouver le point du graphe le plus proche de pt1
    plus_proche_1 = min(graphe, key=lambda p: distance_euclidienne_xy(p.p, pt1))

    # Pareil pour pt2
    plus_proche_2 = min(graphe, key=lambda p: distance_euclidienne_xy(p.p, pt2))

    return plus_proche_1, plus_proche_2, pt1, pt2