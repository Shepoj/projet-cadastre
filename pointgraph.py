# classe pour tous les points (milieux de segments + barycentre)
class PointGraph:
    def __init__(self, p):
        self.p = p                  # tuple (x, y)
        self.sommet_haut = None     # tuple (x, y)
        self.sommet_bas = None      # tuple (x, y)
        self.voisins = []           # liste de PointGraph
        self.meme_x = []            # liste de PointGraph avec le même x
        self.polygone_source = None # liste des points du polygone source

    # ajoute un voisin au point
    def ajouter_voisin(self, autre_point):
        if autre_point not in self.voisins:
            self.voisins.append(autre_point)
