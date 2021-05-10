import TK
from MACS import MACS
import numpy as np
from tkinter import *
import random
random.seed(3)
class BAP(TK.FenPrincipale):
    def __init__(self):
        TK.FenPrincipale.__init__(self, True)
        self.bus = None

    def distance_matrix(self):
        n = len(self.list_node)
        X = np.zeros((n,n))
        Y = np.zeros((n,n))

        for i in range(n):
            e = self.list_node[i]
            x,y,_ = e.get_info_balle()

            X[:,i] += x
            X[i,:] -= x
            
            Y[:,i] += y
            Y[i,:] -= y

        return (X**2+Y**2)**0.5

    def cal_matrix(self):
        n = len(self.list_node)
        dist_matrix = self.distance_matrix()
        vit_matrix = np.zeros((n,n)) + 1

        for key in list(self.route_info.keys()):
            id1, id2 = list(map(int,key.split("-")))
            id1, id2 = self.list_id_node.index(id1), self.list_id_node.index(id2)

            dist_matrix[id1,id2] = self.route_info[key][0]
            dist_matrix[id2,id1] = self.route_info[key][0]

            vit_matrix[id1,id2] = self.route_info[key][1]
            vit_matrix[id2,id1] = self.route_info[key][1]

        temps = dist_matrix/vit_matrix
        
        for i in range(n):
            temps[i,i] = 1e-15
            
        return 1/temps
    
    def resolve(self):
        if len(self.list_node)<2:
            return 0
        if self.bus == None or self.restart:
            vis = self.cal_matrix()

            # cette valeur doit etre changer pour tester avec plusieurs lignes de bus
            num_buslines = 2
            visibility = np.ones((len(vis)+1,len(vis)+1,num_buslines))
            
            for i in range(num_buslines):
                visibility[1:,1:,i] = vis

            nb_ants = len(vis)
            nb_buses = len(vis)
            tau_0 = 0.8
            beta = 1
            rho = 0.4
            q_0 = 0
            mainstop = 1
            constant = 5

            # passangers[i,j] correspond au nombre de passagers qui sont à la station i 
            # et qui ont pour destination la station j
            passangers = np.ones((nb_buses,nb_buses))-np.eye(nb_buses)
            alpha = 0.3 
            t_max = 100
            self.bus = MACS(nb_ants, nb_buses, num_buslines, tau_0, visibility, beta, rho,q_0,mainstop, constant,passangers, alpha)
            
            self.bus.loop(t_max)
            self.sol = self.bus.global_solution
            self.restart = False
        print("solution : ",self.sol)

        for line in self.sol:
            col= np.random.choice(['green', 'blue', 'red', 'magenta', 'black', 'maroon', 'purple', 'navy', 'dark cyan'])
            for i in range(len(line)-1):
                e1 = self.list_node[line[i]-1]
                x1,y1,_ = e1.get_info_balle()

                e2 = self.list_node[line[i+1]-1]
                x2,y2,_ = e2.get_info_balle()

                self.line_noeud(x1, y1, x2, y2, col)

if __name__ == "__main__":
    bap = BAP()
    bap.mainloop()

