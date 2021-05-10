# -*- coding: utf-8 -*-
"""
@authors: Aymane and Anas
"""
""" Ce code se base sur le document "Multiple Ant Colony System  for the bus allocation problem"
déposé sur Moodle sous le nom de 'Sujet-Bus-Allocation-GA-multiple-colonies.pdf'.
"""

import numpy as np
import random 
import tqdm
from copy import deepcopy
random.seed(3)
class MACS: 
    def __init__(self, nb_ants, nb_buses, nb_buslines, tau_0, visibility, beta,\
                 rho,q_0,mainstop, constant,passangers, alpha):
        self.nb_ants = nb_ants
        self.nb_buses = nb_buses
        self.nb_buslines = nb_buslines
        self.tau_0 = tau_0
        self.pheromone_level = tau_0*np.ones((nb_buses+1, nb_buses+1, nb_buslines))# On ajoute un noeaud source comme suggéré par la thèse.
                                                                                   # Ceci permet d'avoir une meilleur initialisation à chaque itération
        self.pheromone_level [0,:,:] = 0.21 *np.ones((nb_buses+1, nb_buslines))  # On initialise le niveau de phéromone entre le noeud source et le reste des arrets.
        self.pheromone_level [:,0,:] = 0.21 *np.ones((nb_buses+1, nb_buslines))  # pheromone_level doit rester symétrique
        
        self.visibility = visibility
        
        self.non_visited_stops = np.ones((nb_ants, nb_buses+1))
        self.non_visited_stops[:,0] = np.zeros(nb_ants)                         # Le noeud source ne sert qu'à l'initialisation, on la met  
                                                                                # à 0 car on veut pas la revisiter après.
        self.beta = beta
        self.alpha = alpha                                                              
        self.rho = rho 
        self.q_0 = q_0      # paramètre qui détermine l'importance relative de l'exploration versus l'exploitation 
        
        self.solutions = [ [[] for i in range(self.nb_buslines)]  for j in range (self.nb_ants) ]# Chaque liste dans self.solutions est une solution
                                                                                                 #Une solution est une liste de liste, ou chaque sous-liste est une bussline.   
        self.global_solution = [[] for i in range(self.nb_buslines)]
        self.L_gb = 100000          
        self.mainstop = mainstop
        self.mainstop_visited = np.ones((nb_buslines,nb_ants))  #Cette variable aide à savoir si l'arrêt centarl était visité par toutes d'une ACS donnée.
        self.mainstop_bis = [mainstop for i in range(nb_ants)]  # Cette variable aide à s'assurer qu'on choisisse par l'arrêt central comme extrémité 
                                                                # du baseline (cf la conftion busline_choice_start)
        self.constant = constant # Le temps nécessaire pour changer de bus : Utilisé dansle calcu de la matrice U permettant de trouver ATT
        self.passangers = passangers # passagerns[i,j] :  nombre personnes en attente à l’arrêt i ayant l’arrêt j pour destination 
        
    def probability (self, busline, ant, arret1, arret2, J_ant) : 
        """
        Fonction qui calcule la probabilité que la fourmi ant de la colonie busline se trouvant à l'arrêt 1
        choisisse l'arrêt 2 comme destination ( équation (2) du document "Multiple Ant Colony System  for the bus allocation problem" )        
        
        Paramètres
        ----------
        busline : int
        ant: int
        arret1: int 
        arret2 : int
        J_ant : list
             liste des arrêts non visités par la fourmi ant
        Returns
        -------
        probability : float
        """
        somme = np.sum(self.pheromone_level[arret1,:,busline]*self.visibility[arret1,:,busline]**self.beta*J_ant)
        return self.pheromone_level[arret1, arret2, busline]*self.visibility[arret1, arret2, busline]**self.beta*J_ant[arret2]/somme

    def busstop_choice_start(self, busline, ant) : 
        """
        Fonction qui permet de déterminer les arrêts par où commence la ligne de bus (busline) 
        décrite dans le document "Multiple Ant Colony System  for the bus allocation problem" 
        dans le paragraphe 3 de la partie 4.
        
        Paramètres
        ----------
        busline : int
        ant: int
        
        Returns
        -------
        r : int
            le prochain arrêt pour la fourmi ant de la colonie busline
        """
        J_ant = self.non_visited_stops[ant,:]
        weights = [self.probability( busline, ant, 0, i,J_ant) for i in range(1,self.nb_buses+1) if J_ant[i]!=0 ]
        weights[self.mainstop_bis[ant]-1] = 0  # Eviter de commencer par l'arrêt central.
        r = random.choices(list(np.where(J_ant == 1)[0]), weights)[0]
        if r< self.mainstop_bis[ant] :         # mettre le bon weight(ligne avant la précédente) à 0 dans les prochaines itérations.
             self.mainstop_bis[ant]-=1 
        if r!= self.mainstop : self.non_visited_stops[ant,:][r] = 0
        if r==self.mainstop : # On ne met pas self.non_visited_stops[ant,:][r] à 0 car on attend à ce que toutes les 
                              # fourmis d'une ACS l'ont visité car c'est l'arrêt central.
            self.mainstop_visited[busline,ant] = 0
        return r
       
    def update_pheromone_3(self, busline, stop1, stop2) :
        """
        Fonction qui permet de faire le mis à jour local du niveau de phéromone (equation 3)
        
        Paramètres
        ----------
        busline : int
        stop1: int
        stop2: int
        """
        self.pheromone_level[stop1,stop2,busline] *= (1-self.rho)
        self.pheromone_level[stop2,stop1,busline] *= (1-self.rho)
        self.pheromone_level[stop1,stop2,busline] += self.rho * self.tau_0 
        self.pheromone_level[stop2,stop1,busline] += self.rho * self.tau_0     
    
    def step2 (self) :
        """
        Fonction qui réalise l'étape 2 du pseudo-code page 6 du document 'Sujet-Bus-Allocation-GA-multiple-colonies.pdf'
        qui consiste en l'initialisation des différentes lignes de bus et en la mise à jour des niveaux de phéronmones suite à cette initialisation'
        """
        for i in range(self.nb_buslines) :
            for j in range(self.nb_ants) : 
                r = self.busstop_choice_start(i, j)
                self.solutions[j][i].append(r)
                self.update_pheromone_3( i, 0, r)

    def next_stop(self, busstops, ant) : 
        """
        Fonction qui permet de déterminer le prochain arrêt qui sera ajouté à la solution par l'ACS de ant 
         
        Paramètres
        ----------
        busstops : Si la solution est de la forme  [[5, 3], [4, 3], [1, 3, 2]], busstops est : [3, 3, 2], c'est-à-dire
                   c'est les derniers arrêts visité pas l'ACS de ant.
        ant: int
        
        Returns
        -------
        J : int 
            prochain arrêt 
        actual_busstop :int 
            arrêt de la ligne de bus qui va s'étendre suite à cette étape.
        colony : int
            la ligne de bus qui à laquelle J sera ajoutée.
        """
        q = random.uniform(0,1)
        J_ant = self.non_visited_stops[ant,:]
        J_init ={}
        if q <= self.q_0 : # Si q est inférieur à q_0 : Exploitation
            for l in range(self.nb_buslines):
                # On stocke dans J_init les arrêts de bus selon l'equation 1 
                probas = self.pheromone_level[busstops[l],:,l]*self.visibility[busstops[l],:,l]**self.beta*J_ant
                probas[self.mainstop] *= self.mainstop_visited[l,ant]
                J_init[np.argmax(probas)] =   [probas[np.argmax(probas)],busstops[l],l]
            J = np.max(list(J_init.keys())) # On choisit J ayant la plus grande arg max.
            actual_busstop = J_init[J][1]
            colony  = J_init[J][2]
            
        else : # Si q est supérieur à q_0 : Exploration
            for l in range(self.nb_buslines):
                # On stocke dans J_init les arrêts de bus selon l'equation 2
                J_ant_mainstop_visited = deepcopy(J_ant)
                J_ant_mainstop_visited[self.mainstop]*= self.mainstop_visited[l,ant]
                weights = [self.probability( l, ant, busstops[l], i, J_ant) for i in range(1,self.nb_buses+1) if J_ant_mainstop_visited[i]!=0 ]
                if list(np.where(J_ant_mainstop_visited == 1)[0])!=[]:
                    J_init[l] = random.choices(list(np.where(J_ant_mainstop_visited==1))[0], weights)[0]
            # On choisit J aléatoirement par J_inti
            colony = random.choices(list(J_init.keys()))[0] 
            actual_busstop = busstops[colony]
            J = J_init[colony]
        return J,actual_busstop,colony
      
    def step3 (self):
        """
        Fonction qui réalise l'étape 3 du pseudo-code page 6 du document 'Sujet-Bus-Allocation-GA-multiple-colonies.pdf'
        qui consiste à trouver le prochain arrêt de chaque ACS et en la mise à jour des niveaux de phéronmones suite à cette initialisation
        et ceci (nb_buses - 1) fois pour avoir une solution complète à la fin.
        """
        for w in range(self.nb_buses-1):
            for k in range(self.nb_ants) :
                solution_k = self.solutions[k]
                busstops = [elt[len(elt)-1] for elt in solution_k] # Si la solution est de la forme  [[5, 3], [4, 3], [1, 3, 2]], busstops est : [3, 3, 2], c'est-à-dire
                                                                   # c'est les derniers arrêts visité pas l'ACS de ant.
                J,actual_busstop,colony = self.next_stop(busstops, k)
                if J!= self.mainstop :
                    self.non_visited_stops[k,:][J] = 0
                if J == self.mainstop : 
                    self.mainstop_visited[colony,k] = 0
                if J == self.mainstop and ( self.nb_ants-np.sum(self.mainstop_visited[:,k]))==self.nb_ants: 
                     self.non_visited_stops[k,:][J] = 0
                self.solutions[k][colony].append(J) # Ajouter l'arrêt trouvé à la solution.
                self.update_pheromone_3(colony, actual_busstop, J) # Mise à jour local des niveaux de phéromones.
    
    def compute_U_k(self,S_k):
        """
        Fonction qui Calcule la matrice U qui permet de calculer ATT
        U_k est calculé comme expliqué dans le document 'Sujet-Bus-Allocation-GA-multiple-colonies.pdf'.
        
        Paramètres 
        ----------
        S_k: liste de liste, chaque élément de S_k correspond à une ligne de bus.
        
        Returns
        -------
        U_k :np.array
        """
        U_k = np.zeros((self.nb_buses, self.nb_buses))
        for i in range(len(S_k)) :
            for j in range(len(S_k[i])-1):
                u_temp = 0
                for m in range(j+1,len(S_k[i])):
                    U_k[S_k[i][j]-1,S_k[i][m]-1] = 1/self.visibility[S_k[i][j],S_k[i][m],0] + u_temp
                    u_temp += 1/self.visibility[S_k[i][j],S_k[i][m],0]
        for i in range(self.nb_buses) : 
            for j in range(self.nb_buses): 
                if U_k[i,j]==0 and i!=j :
                     U_k[i,j] =  U_k[i,self.mainstop-1] + U_k[self.mainstop-1,j] + self.constant
        return U_k
    
    def compute_ATT(self,U_k) : 
        """
        Fonction qui Calcule ATT.
        
        Paramètres 
        ----------
        U_k: np.array
        
        Returns
        -------
        _ATT : float
        """
        sum_y = np.sum(U_k*self.passangers,axis = 1)
        sum_t_y = np.sum(self.passangers, axis = 1)
        return np.sum(sum_y/sum_t_y)/self.nb_buses
    
      
    def update_pheromone_4(self, busline, stop1, stop2) :
        """
        Faire partiellement (complété dans step4) la mise à jour globale des niveaux de phéromènes.
        """
        self.pheromone_level[stop1,stop2,busline] *= (1-self.alpha)
        self.pheromone_level[stop2,stop1,busline] *= (1-self.alpha)
        
    def step4(self) :
        """
        Fonction qui réalise l'étape 4 du pseudo-code page 6 du document 'Sujet-Bus-Allocation-GA-multiple-colonies.pdf'
        qui consiste à calculer L_k pour chaque ant k pour trouver le meilleur L noté L_g et la meilleure solution notée 
        global_solution et qui fait la mise à jour global des niveaux de phéromones.
        """
        self.global_solution = self.solutions[0]
        for  k in range(self.nb_ants) : 
            U_k = self.compute_U_k(self.solutions[k])
            L = self.compute_ATT(U_k)
            if L < self.L_gb : 
                self.L_gb = L
                self.global_solution = self.solutions[k]
        for l in range(self.nb_buslines):
            #Diminution du niveau de phéromone global
            for i in range(1,self.nb_buses+1) :                  
                for j in range(1,self.nb_buses+1) :
                    self.update_pheromone_4 (l, i, j)
            #Augmentation du niveau de phéromones des arrêts appartenant à la solution globale. 
            for i in range(len(self.global_solution)) :
                for j in range(len(self.global_solution[i])-1):
                    self.pheromone_level[self.global_solution[i][j],self.global_solution[i][j+1],l] += self.alpha / self.L_gb 
                    self.pheromone_level[self.global_solution[i][j+1],self.global_solution[i][j],l] += self.alpha / self.L_gb 
    
    def loop(self,t_max):
        for _ in range(t_max):
            #print(self.global_solution)
            self.step2()
            self.step3()
            self.step4()
            self.non_visited_stops = np.ones((self.nb_ants, self.nb_buses+1))
            self.non_visited_stops[:,0] = np.zeros(self.nb_ants)
            self.solutions = [ [[] for i in range(self.nb_buslines)]  for j in range (self.nb_ants) ]
            self.mainstop_visited = np.ones((self.nb_buslines,self.nb_ants))
            self.mainstop_bis = [self.mainstop for i in range(self.nb_ants)]
            
    
if __name__ == "__main__": 
    """
    Cette partie permet de tester le code sans utiliser la partie graphique
    """
    v=np.array([[1e15 ,4.03196307e-03, 5.18023471e-03, 4.47455287e-03, 3.09561919e-03],
                [4.03196307e-03, 1e15, 5.57763435e-03 ,3.48170083e-03 , 4.76190476e-03],
                [5.18023471e-03, 5.57763435e-03, 1e15, 9.24144955e-03, 7.57141343e-03],
                [4.47455287e-03, 3.48170083e-03, 9.24144955e-03, 1e15, 5.34270673e-03],
                [3.09561919e-03, 4.76190476e-03, 7.57141343e-03, 5.34270673e-03, 1e15]])
    
    visibility = np.ones((6,6,3))*1000
    visibility[1:,1:,0] = v
    visibility[1:,1:,1] = v
    visibility[1:,1:,2] = v
    passangers = 3*np.ones((5,5))-np.eye(5)
    
    nb_ants = 5
    nb_buses = 5
    nb_buslines = 2
    tau_0 = 0.8
    beta = 1
    rho = 0.1
    q_0 = 0.7
    mainstop = 1
    constant = 5
    passangers =  np.ones((5,5))-np.eye(5)
    alpha = 0.01
    macs= MACS(nb_ants, nb_buses, nb_buslines, tau_0, visibility, beta,\
                rho,q_0,mainstop, constant,passangers, alpha)
    t_max = 100
    macs.loop(t_max)

    print("--------------------------------------------")
    print(macs.global_solution)

    
    
    
    





        
        


            
            
        
        
        