"""
Structure de liste doublement chaÃ®nÃ©e

Implantation initiale :
  https://python.19633.com/fr/Python/1001000998.html

Corrections (!), modifications et ajouts C. Nguyen, universitÃ© de Toulon
"""

class Node(object):
    """
    noeud d'une double liste chaÃ®nÃ©e
    """
    def __init__(self, value):
        self.__data = value
        self.prev = None
        self.next = None

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        # le type (dynamique) du noeud ne doit pas changer
        if self.__data is not None and type(value) != type(self.__data):
            raise ValueError
        self.__data = value


class DoublyLinkedList(object):
    """
    structure de donnÃ©es de la double liste chaÃ®nÃ©e
    - gestion de la rÃ©fÃ©rence courante : current_init(), current_forward(), current_backward() avec bouclage tÃªte <-> queue implicite,
    - insertions (courante, tÃªte, queue) :  insert(), insert_front(), insert_back(),
    - suppressions (occurence, index) : delete() sans retour, pop() avec retour de l'occurence,
    - affichages : build_string(), display(), __str__().
    """
    def __init__(self):
        """
        deux rÃ©fÃ©rences head et tail
        aspect circulaire implicite
        """
        self.head = None
        self.tail = None
        # une 3eme pour le parcours de la DLL
        self.curr = None
        # taille a conserver pour eviter son calcul
        self.__size = 0

    @property
    def size(self):
        """ uniquement accesseur, gestion purement interne """
        return self.__size

    def current_init(self, start):
        """
        initialisation de la position courante
        """
        # verif
        temp_node = self.head
        while temp_node is not None:
            if temp_node == start:
                self.curr = start
                return
            temp_node = temp_node.next
        raise ValueError
        
    def current_forward(self):
        """
        progression vers l'avant avec bouclage implicite
        """
        # gestion de self.curr : s'il y a un "apres", on y va
        if self.curr.next is not None:
            self.curr = self.curr.next
        # sinon on boucle
        else:
            self.curr = self.head

    def current_backward(self):
        """
        progression vers l'arriÃ¨re avec bouclage implicite
        """
        # gestion de self.curr : s'il y a un "avant", on y va
        if self.curr.prev is not None:
            self.curr = self.curr.prev
        # sinon on boucle
        else:
            self.curr = self.tail
 
    def insert_front(self, node):
        """ insertion en tÃªte """
        # il y a deja des elements
        if self.head is not None:
            node.next = self.head
            self.head.prev = node
            self.head = node
        # la DLL est vide
        else:
            self.head = self.tail = node
        # augmentation de la taille
        self.__size += 1
 
    def insert_back(self, node):
        """ insertion en queue """
        # heresie, trop couteux
        # if self.head is not None:
            # current_node = self.head
            # while(current_node.next is not None):
            #     current_node = current_node.next
        # il y a deja des elements
        if self.tail is not None:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        # la DLL est vide
        else:
            self.head = self.tail = node
        # augmentation de la taille
        self.__size += 1

    def insert(self, node, index):
        """
        insertion de node *Ã  l'emplacement* index
        (donc 0 est correct)
        """
        # il y a deja des elements
        if self.head is not None:
            i = 0
            current_node = self.head
            while current_node is not None:
                # enregistrement trouve
                if i == index:
                    node.next = current_node.next
                    node.prev = current_node
                    current_node.next = node
                    # si l'on n'est pas en fin de DLL, dernier raccord
                    if node.next is not None:
                        node.next.prev = node
                    break  # inutile de poursuivre
                current_node = current_node.next
                i += 1
        # DLL vide et index nul => ok
        elif index == 0:
            self.insert_front(node)
        else:
            raise IndexError
        # augmentation de la taille
        self.__size += 1
  
    def delete(self, value):
        """
        supprime la 1Ã¨re occurence de value
        l'interruption ValueError est levÃ©e si la valeur n'existe pas
        """
        # DLL vide
        if self.head is None:
            # print('Doubly Linked List is empty')
            # return
            raise ValueError
        # DLL a un seul enregistrement
        if self.head.next is None:
            if self.head.data ==  value:
                temp_node = self.head
                self.head = None
                del temp_node
                # diminution de la taille
                self.__size -= 1
                return
            else:
                # print("Element is not found in our list")
                # return
                raise ValueError
        # dans les autres cas
        else:
            temp_node = self.head
            while temp_node is not None:
                if temp_node.data == value:
                    # cas particulier de la tete
                    if temp_node.prev is not None:
                        temp_node.prev.next = temp_node.next
                    else:
                        self.head = temp_node.next
                    # cas particulier de la queue
                    if temp_node.next is not None:
                        temp_node.next.prev = temp_node.prev
                    else:
                        self.tail = temp_node.prev
                    # print('temp_node.data', temp_node.data)
                    del temp_node
                    # diminution de la taille
                    self.__size -= 1
                    return
                temp_node = temp_node.next
            # dernier enregistrement
            # if temp_node.data == value:
            #     temp_node.prev.next = None
            #     del temp_node
            #     return
            # print("Element is not found in the list")
            # enregistrement non trouve
            raise ValueError

    def pop(self, index):
        """
        suppression d'un enregistrement Ã  la position index
        et retour de cet enregistrement (s'il existe)
        """
        current_node = self.head
        i = 0
        while current_node != self.tail and i < index:
            current_node = current_node.next
            i += 1
        if i == index:
            # si on n'est pas en queue
            if current_node.next is not None:
                current_node.next.prev = current_node.prev
            else:
                current_node.prev.next = None
                self.tail = current_node.prev  # maj tail
            # si on n'est pas en tete
            if current_node.prev is not None:
                current_node.prev.next = current_node.next
            else:
                current_node.next.prev = None
                self.head = current_node.next  # maj head
            data = current_node.data
            del current_node
            # diminution de la taille
            self.__size -= 1
            return data
        else:
            return None

    def to_list(self):
        L=[]
        nd = self.head
        while nd.next is not None:
            L.append(nd.data)
            nd=nd.next
        return L

    def build_string(self, reverse=False):
        """
        contenu de la double liste sous forme de string
        soit de la tÃªte vers la queue, soit inversement
        """
        ch = ''  # chaine a afficher
        if not reverse:
            current_node = self.head
            # tant qu'on n'est pas en bout de liste
            while current_node is not None:
                ch += str(current_node.data)
                # il y a encore (au moins) un enregistrement
                if current_node.next is not None:
                    ch += '-->'
                current_node = current_node.next
        else:
            previous_node = self.tail
            while previous_node is not None:
                ch += str(previous_node.data)
                # il y a encore (au moins) un enregistrement
                if previous_node.prev is not None:
                    ch += '-->'
                previous_node = previous_node.prev
        return ch

    def display(self, reverse=False):
        """
        affichage sur la console du contenu de la double liste
        soit de la tÃªte vers la queue, soit inversement
        """
        print(self.build_string(reverse))

    def __str__(self):
        """ affichage par dÃ©faut """
        return self.build_string()


if __name__ == "__main__":
    # tests unitaires originaux
    # node1 = Node(12)
    # node2 = Node(13)
 
    # dll = DoublyLinkedList()
    # dll.insert_front(node1)
    # dll.insert_front(node2)
    # dll.display()
 
    # dll.insert_back(Node(14))
    # dll.insert_back(Node(26))
    # dll.insert_front(Node(1))
    # dll.display()

    # dll.delete(dll.head.data)
    # dll.display()
    # dll.delete(12)
    # dll.display()

    # tests avec des couples de coordonnees
    poly = ((59,52), (41,45), (40,70), (29,64), (22,70), (10,62), (17,53), (15,41), (6,48), (2,28), (13,14), (24,21), (40,1), (33,32), (50,27))

    dll = DoublyLinkedList()
    for som in poly:
        dll.insert_back(Node(som))
        # dll.display()
    print('initialisation :', dll, '/ taille', dll.size)

    print('\nsuppressions')
    enreg = dll.pop(4)
    print('pop(4) :', enreg, '/', dll)
    enreg = dll.pop(0)  # suppression en tete
    print('pop(0) :', enreg, '/', dll)
    enreg = dll.pop(12)  # suppression en queue
    print('pop(12) :', enreg, '/', dll)
    enreg = dll.pop(666)  # suppression out of range
    print('pop(666) :', enreg, '/', dll)

    print('\naffichage de la queue vers la tÃªte')
    dll.display(True)  # affichage renverse

    print('\nparcours de la DLL')
    print('1er enreg', dll.head.data)
    dll.current_init(dll.head)
    dll.current_forward()
    print('2Ã¨me enreg', dll.curr.data)

    print('\nremplacement du noeud courant')
    try:
        dll.curr.data = 3
    except ValueError:
        print('erreur dans le type de donnÃ©e')
        dll.curr.data = (0, 0)
        print(dll, '/ taille', dll.size)
