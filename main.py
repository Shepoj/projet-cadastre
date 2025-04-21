import json
import tkinter as tk
from polygone import Polygone
from utils import generer_points_et_chercher_plus_proche
from pointgraph import PointGraph
from graphe import graphe_planaire, afficher_graphe, dijkstra

file = open("cadastre-83062-batiments.json","r")
data = json.load(file)
file.close()

polys = []    # liste de tous les polygones du fichier

lat = []      # liste de toutes les latitudes
long = []     # liste de toutes les longitudes
allpoints = []        # liste des envoloppes

# recuperer les points et les ajouter dans la liste de latitude, de longitude et de tous les points
for feature in data["features"][6060:6194]: 
    polys.append(feature["geometry"]["coordinates"][0][0])
    for point in feature["geometry"]["coordinates"][0][0]:
        lat.append(point[1])
        long.append(point[0])

ymin,xmin,ymax,xmax = min(lat),min(long),max(lat),max(long)
ratio = (xmax-xmin)/(ymax-ymin)

liste_segments = []   # liste de tous les segments


win= tk.Tk()
canevas=tk.Canvas(win,width=600*ratio,height=600, bg="white")
canevas=tk.Canvas(win, width=600*ratio, height=600, bg="white")
canevas.pack()

myPolygons=[]

for poly in polys:
    pol=Polygone(len(poly),poly)

    allpoints+=pol.affiche_enveloppe([25,25,525*ratio,525],[xmin,ymin, xmax-xmin,ymax-ymin])
    #pol.polygone([25,25,525*ratio,525],[xmin,ymin, xmax-xmin,ymax-ymin])
    myPolygons.append(pol)

for pol in myPolygons:
    pol.superbande(myPolygons,[25,25,525*ratio,525],[xmin,ymin, xmax-xmin,ymax-ymin])

for pol in myPolygons:
    pol.scanning([25,25,525*ratio,525],[xmin,ymin, xmax-xmin,ymax-ymin])
    pass



myPolygons=[]   # liste de tous les polygones (classe Polygone)

# creation des envoloppes et des polygones
for poly in polys:
    pol=Polygone(len(poly), poly)
    allpoints+=pol.affiche_enveloppe([25, 25, 525*ratio, 525],[xmin, ymin, xmax-xmin, ymax-ymin], canevas)
    myPolygons.append(pol)

# creation de la superbande
for pol in myPolygons:
    pol.superbande(myPolygons, [25, 25, 525*ratio, 525], [xmin, ymin, xmax-xmin, ymax-ymin])

# creation des segments
for pol in myPolygons:
    pol.scanning([25,25,525*ratio,525],[xmin,ymin, xmax-xmin,ymax-ymin], canevas, liste_segments)
    
# trier la liste des segments
liste_segments.sort(key=lambda x: (x[0][0], x[1][1])) # on trie par x du point haut puis par y du point bas

# suppprime les segments qui ont le meme x du point haut et bas
for i in range(len(liste_segments) - 2, -1, -1):  # Parcours inversé
    if liste_segments[i][0][0] == liste_segments[i][1][0] and liste_segments[i][0][1] == liste_segments[i][1][1]:
        liste_segments.pop(i)


# creer et afficher le graphe planaire
graphe = graphe_planaire(liste_segments, ratio)
afficher_graphe(graphe, canevas)

def relancer_dijkstra():
    # Effacer uniquement les anciens éléments
    canevas.delete("chemin")

    # Générer deux points et trouver leurs correspondants dans le graphe
    point_depart, point_arrivee, alea1, alea2 = generer_points_et_chercher_plus_proche(graphe, 600 * ratio, 600)

    # Afficher les points aléatoires
    canevas.create_oval(alea1[0]-4, alea1[1]-4, alea1[0]+4, alea1[1]+4, fill="orange", tags="chemin")
    canevas.create_oval(alea2[0]-4, alea2[1]-4, alea2[0]+4, alea2[1]+4, fill="orange", tags="chemin")

    # Relier aux sommets du graphe
    canevas.create_line(alea1[0], alea1[1], point_depart.p[0], point_depart.p[1], fill="orange", dash=(4, 2), tags="chemin")
    canevas.create_line(alea2[0], alea2[1], point_arrivee.p[0], point_arrivee.p[1], fill="orange", dash=(4, 2), tags="chemin")

    # Calculer et afficher le nouveau chemin
    chemin = dijkstra(graphe, point_depart, point_arrivee)
    for i in range(len(chemin)-1):
        a = chemin[i].p
        b = chemin[i+1].p
        canevas.create_line(a[0], a[1], b[0], b[1], fill="green", width=2, tags="chemin")

segments_visibles = True
graphe_visible = True
chemin_visible = True

# Fonction pour changer la visibilité des segments
def changer_segments():
    global segments_visibles
    if segments_visibles:
        canevas.itemconfigure("segments", state="hidden")
        segments_visibles = False
    else:
        canevas.itemconfigure("segments", state="normal")
        segments_visibles = True

# Fonction pour changer la visibilité du graphe
def changer_graphe():
    global graphe_visible
    if graphe_visible:
        canevas.itemconfigure("graphe", state="hidden")
        graphe_visible = False
    else:
        canevas.itemconfigure("graphe", state="normal")
        graphe_visible = True

def changer_chemin():
    global chemin_visible
    if chemin_visible:
        canevas.itemconfigure("chemin", state="hidden")
    else:
        canevas.itemconfigure("chemin", state="normal")
    chemin_visible = not chemin_visible


# Bouton en bas à droite pour relancer Dijkstra avec de nouveaux points
bouton = tk.Button(win, text="Nouveau chemin", command=relancer_dijkstra)
bouton.place(x=600*ratio - 250, y=600 - 40)

btn_chemin = tk.Button(win, text="Chemin", command=changer_chemin)
btn_chemin.place(x=600*ratio - 122, y=600 - 40)

# Bouton pour cacher/afficher les segments
btn_segments = tk.Button(win, text="Segments", command=changer_segments)
btn_segments.place(x=600*ratio - 130, y=600 - 80)

# Bouton pour cacher/afficher le graphe
btn_graphe = tk.Button(win, text="Graphe", command=changer_graphe)
btn_graphe.place(x=600*ratio - 122, y=600 - 120)

win.mainloop()  