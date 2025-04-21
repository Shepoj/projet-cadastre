from pointgraph import PointGraph
from utils import barycentre, segment_traverse_polygones, projection, test2, distance_euclidienne

# creer le graphe planaire a partir de la liste de segments
def graphe_planaire(liste_seg, ratio):
    graphe_planaire = []

    # on cree une premier version du graphe_planaire avec tous les mileux des segments(qu'on instancie en PointGraph)
    for seg in liste_seg:
        (x1, y1), (x2, y2), enveloppe = seg
        # on trie pour déterminer haut/bas
        if y1 < 0:
            y1 = 0
        if y2 < 0:
            y2 = 0
        if y1 > 600:
            y1 = 600
        if y2 > 600:
            y2 = 600
        if y1 > y2:
            haut, bas = (x1, y1), (x2, y2)
        else:
            haut, bas = (x2, y2), (x1, y1)
        my = (haut[1] + bas[1]) / 2     # definition du milieu
        p = (x1, round(my, 2))      # on arrondit le y pour eviter les erreurs d'affichage
        ptg = PointGraph(p)         # instanciation du PointGraph
        ptg.sommet_haut = haut
        ptg.sommet_bas = bas
        ptg.polygone_source = enveloppe

        # si il y a deja un point avec le meme p, on ne l'ajoute pas
        existe_deja = False
        for i in range(len(graphe_planaire)):
            if graphe_planaire[i].p == ptg.p:
                existe_deja = True
                break
        # on ajoute tous ceux du meme x, au dernier de ce x
        if not existe_deja:
            if graphe_planaire and graphe_planaire[-1].p[0] == ptg.p[0]:
                ptg.meme_x = graphe_planaire[-1].meme_x     # on lui donne la liste des points du meme x
                ptg.meme_x.append(graphe_planaire[-1])      # on ajoute le dernier point du meme x
            graphe_planaire.append(ptg)
            
    # premier barycentre (le point tout a gauche)
    p = graphe_planaire[0].p
    x = (0 + p[0]) / 2
    y = 300
    ptg = PointGraph((x, y))

    # ajouter le barycentre au debut de la liste
    graphe_planaire.insert(0, ptg)
    ptg.ajouter_voisin(graphe_planaire[1])
    graphe_planaire[1].ajouter_voisin(ptg)
    
    i=2
    polygones_actuels = []  # represente les polygones que le ptg actuel peut couper suivant leur x
    # on relie les points voisins et on ajoute les barycentres
    while i < len(graphe_planaire):
        ptg = graphe_planaire[i]
        # on met a jour la liste des polygones actuels
        if ptg.polygone_source not in polygones_actuels:
            polygones_actuels.append(ptg.polygone_source)
        # les x minimum du polygone source de ptg
        ptg_x_min = min(ptg.polygone_source, key=lambda x: x[0])[0]
        ptg_x_max = max(ptg.polygone_source, key=lambda x: x[0])[0]
        temp_polygone = None
        # supprimer les polygones qui ne sont pas dans la bande de ptg sauf le x juste avant
        for polygone in polygones_actuels:
            poly_min_x = min(polygone, key=lambda x: x[0])[0]
            poly_max_x = max(polygone, key=lambda x: x[0])[0]
            if not(poly_min_x <= ptg_x_min <= poly_max_x) and not(poly_min_x <= ptg_x_max <= poly_max_x):
                if temp_polygone is None:
                    temp_polygone = polygone
                elif poly_max_x > max(temp_polygone, key=lambda x: x[0])[0]:
                    polygones_actuels = [p for p in polygones_actuels if p != temp_polygone]
                    temp_polygone = polygone
                else:
                    polygones_actuels.remove(polygone)
        
        # si ptg et le point precendent de graphe_planaire partagent le meme sommet de polygone
        if ptg.p[0] == graphe_planaire[i - 1].p[0] and graphe_planaire[i - 1].sommet_haut is not None and ptg.sommet_bas[1] == graphe_planaire[i - 1].sommet_haut[1]:
            # recuperer le barycentre de graphe_planaire[i-1]
            bary1=0
            bary2=0
            # chercher le ou les barycentre de graphe_planaire[i-1]
            for voisin in graphe_planaire[i - 1].voisins:
                if voisin.sommet_bas is None:
                    if bary1 != 0:
                        bary2 = voisin
                    else:
                        bary1 = voisin

            # si le barycentre n'est pas voisin du point courant
            if (bary1 != 0 and bary2 != 0) or (bary1 !=0 and segment_traverse_polygones(ptg.p, bary1.p, polygones_actuels)):
                j = i - 2
                
                # chercher le premier point du graphe_planaire qui est voisin du point courant
                while segment_traverse_polygones(ptg.p, graphe_planaire[j].p, polygones_actuels+[graphe_planaire[j].polygone_source]) or \
                        graphe_planaire[j].sommet_haut is None:
                    j -= 1
                if j >= 0:
                    p = PointGraph(barycentre([ptg.p, graphe_planaire[j].p]))
                    p.ajouter_voisin(ptg)
                    p.ajouter_voisin(graphe_planaire[j])
                    # relie le barycentre aux points du meme x que graphe_planaire[j](point avant barycentre)
                    for meme_x in graphe_planaire[j].meme_x:
                        count = 0
                        for voisin in meme_x.voisins:
                            if voisin.sommet_haut is None:
                                count += 1
                        if not segment_traverse_polygones(ptg.p, meme_x.p, polygones_actuels + [meme_x.polygone_source]) and \
                            count < 2: # on verifie si le barycentre est voisin du point courant, si le point a deja plus de 2 barycentres on passe, parce qu'un point peut avoir que 2 bary max
                            p.ajouter_voisin(meme_x)
                            meme_x.ajouter_voisin(p)
                            p.p = barycentre([temp.p for temp in p.voisins])
                    graphe_planaire[j].ajouter_voisin(p)
                    ptg.ajouter_voisin(p)
                    graphe_planaire.insert(i, p)
                    i += 2
                else: # il n'a pas de voisin
                    graphe_planaire.remove(ptg)
                    for voisin in ptg.voisins:
                        voisin.voisins.remove(ptg)

            else:
                # si le barycentre est voisin du point courant
                if bary1 != 0:
                    bary1.ajouter_voisin(ptg)
                    bary1.p = barycentre([p.p for p in bary1.voisins])
                    ptg.ajouter_voisin(bary1)
                i+=1
        
        else:
            #si il faut aller chercher le voisin
            j = i - 1
            # on cherche le premier point du graphe_planaire qui est voisin du point courant
            while segment_traverse_polygones(ptg.p, graphe_planaire[j].p, polygones_actuels + [graphe_planaire[j].polygone_source]) or \
                    graphe_planaire[j].sommet_haut is None:
                j -= 1
            if j >= 0:
                p = PointGraph(barycentre([ptg.p, graphe_planaire[j].p]))
                p.ajouter_voisin(ptg)
                ptg.ajouter_voisin(p)
                p.ajouter_voisin(graphe_planaire[j])
                graphe_planaire[j].ajouter_voisin(p)
                
                # on relie le barycentre aux points du meme x que graphe_planaire[j](point avant barycentre)
                for meme_x in graphe_planaire[j].meme_x:
                    count = 0
                    for voisin in meme_x.voisins:
                        if voisin.sommet_haut is None:
                            count += 1
                    if (not segment_traverse_polygones(ptg.p, meme_x.p, polygones_actuels + [meme_x.polygone_source])) and count < 2:
                        p.ajouter_voisin(meme_x)
                        meme_x.ajouter_voisin(p)
                p.p = barycentre([temp.p for temp in p.voisins])
                graphe_planaire.insert(i, p)
                i += 2
            else: # il n'a pas de voisin
                graphe_planaire.remove(ptg)
                for voisin in ptg.voisins:
                    voisin.voisins.remove(ptg)

    # mettre premier point au mileux de sa bande
    graphe_planaire[0].p = (graphe_planaire[0].p[0]/2,graphe_planaire[0].p[1])
    
    # ajouter le dernier point
    p = graphe_planaire[-1].p
    x = (p[0] + (600*ratio)) / 2
    y = 300
    ptg = PointGraph((x, y))
    graphe_planaire.append(ptg)
    ptg.ajouter_voisin(graphe_planaire[-2])
    graphe_planaire[-2].ajouter_voisin(ptg)

    # ajouter le barycentre aux points du meme x que le dernier point
    for j in graphe_planaire[-2].meme_x:
        count = 0
        for voisin in j.voisins:
            if voisin.sommet_haut is None:
                count+=1
        if test2(graphe_planaire[-2], j) and count < 2:
            ptg.ajouter_voisin(j)
            j.ajouter_voisin(ptg)
    # mettre dernier point au milieux de sa bande
    graphe_planaire[-1].p = ((graphe_planaire[-2].p[0]+(600*ratio))/2,graphe_planaire[-1].p[1])

    return graphe_planaire


def dijkstra(graphe, depart, arrivee):
    # Initialiser les distances à l'infini pour tous les points
    distances = {}
    for point in graphe:
        distances[point] = float("inf")
    distances[depart] = 0

    # Dictionnaire pour se souvenir du chemin
    precedent = {}

    # Liste des points à visiter
    a_visiter = graphe.copy()

    while a_visiter:
        # Trouver le point avec la distance la plus courte
        point_courant = min(a_visiter, key=lambda p: distances[p])

        if point_courant == arrivee:
            break  # On a trouvé le chemin

        a_visiter.remove(point_courant)

        for voisin in point_courant.voisins:
            d = distance_euclidienne(point_courant, voisin)
            nouvelle_distance = distances[point_courant] + d
            if voisin not in distances:
                continue
            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                precedent[voisin] = point_courant

    # Reconstruire le chemin
    chemin = []
    point = arrivee
    while point != depart:
        chemin.append(point)
        point = precedent.get(point)
        if point is None:
            print("Aucun chemin trouvé.")
            return []
    chemin.append(depart)
    chemin.reverse()

    return chemin


def afficher_graphe(graphe, canevas):
    # Afficher p de chaque PointGraph
    for ptg in graphe:
        canevas.create_oval(ptg.p[0] - 2, ptg.p[1] - 2, ptg.p[0] + 2, ptg.p[1] + 2, fill="green", tags="graphe")
        #canevas.create_text(ptg.p[0], ptg.p[1] - 10, text=str(ptg.p), font=("Arial", 8))
        if ptg.voisins is not None:
            for voisin in ptg.voisins:
                canevas.create_line(ptg.p[0], ptg.p[1], voisin.p[0], voisin.p[1], fill="red", tags="graphe")
                #canevas.create_text((ptg.p[0] + voisin.p[0]) / 2, (ptg.p[1] + voisin.p[1]) / 2, text=str(voisin.p), font=("Arial", 8))