import TK
from MACS import MACS
import numpy as np
from tkinter import *
import random

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
        print(dist_matrix)
        vit_matrix = np.zeros((n,n)) + 1
        freq_matrix = np.zeros((n,n)) + 1

        lib_matrix = np.zeros((n,n)) + 1

        for key in list(self.route_info.keys()):
            id1, id2 = list(map(int,key.split("-")))
            id1, id2 = self.list_id_node.index(id1), self.list_id_node.index(id2)

            dist_matrix[id1,id2] = self.route_info[key][0]
            dist_matrix[id2,id1] = self.route_info[key][0]

            vit_matrix[id1,id2] = self.route_info[key][1]
            vit_matrix[id2,id1] = self.route_info[key][1]

            freq_matrix[id1,id2] = self.route_info[key][2]
            freq_matrix[id2,id1] = self.route_info[key][2]

            lib_matrix[id1,id2] = self.route_info[key][3]
            lib_matrix[id2,id1] = self.route_info[key][3]

        temps = dist_matrix/vit_matrix
        
        for i in range(n):
            temps[i,i] = 1e-15
            
        return 1/temps

        # to continue .......
        # merge other classes
        """
        vitesse_matrix = self.route_info[:,:,1]
        vitesse_matrix = np.where(vitesse_matrix!=-1, vitesse_matrix, 1)
        vitesse_matrix = np.where(vitesse_matrix!=0, vitesse_matrix, 1e-15)
        freq_matrix = self.route_info[:,:,2]
        freq_matrix = np.where(freq_matrix!=-1, freq_matrix, 1)
        freq_matrix = np.where(freq_matrix!=0, freq_matrix, 1e-15)
        lib_matrix = self.route_info[:,:,3]
        lib_matrix = np.where(lib_matrix!=-1, lib_matrix, 1)
        n = len(self.list_node)
        lib_matrix += np.repeat(np.array(self.noeud_info)[:,1],n).reshape([n,n])
        lib_matrix = np.where(lib_matrix!=0, lib_matrix, 1e-15)
        besoin_matrix = np.repeat(np.array(self.noeud_info)[:,0],n).reshape([n,n])
        prop_matrix_a = besoin_matrix//lib_matrix
        prop_matrix_b = besoin_matrix%lib_matrix
        prop_matrix = ((prop_matrix_a-1)*prop_matrix_a+prop_matrix_b*prop_matrix_a+0.5)/besoin_matrix
        self.temps_matrix = vit_matrix/dist_matrix
        """
    
    def resolve(self):
        if len(self.list_node)<2:
            return 0
        if self.bus == None:
            vis = self.cal_matrix()
            visibility = np.zeros((len(vis),len(vis),2))
            visibility[:,:,0] = vis
            visibility[:,:,1] = vis
            print(visibility)
            passangers = np.ones((len(vis),len(vis)))-len(vis)
            self.bus = MACS(2,len(vis),2,0.8,visibility,1,0.1,0.8,2,5, visibility, passangers  , 0.3)
            self.bus.loop(10)
            self.sol = self.bus.global_solution
        print(self.sol)

        for line in self.sol:
            col= random.choice(['green', 'blue', 'red', 'magenta', 'black', 'maroon', 'purple', 'navy', 'dark cyan'])
            for i in range(len(line)-1):
                e1 = self.list_node[line[i]]
                x1,y1,_ = e1.get_info_balle()

                e2 = self.list_node[line[i+1]]
                x2,y2,_ = e2.get_info_balle()

                self.line_noeud(x1, y1, x2, y2, col)
        #self.zoneAffichage.placer_noeud(self.x_nodes[self.bus.arrete_m],self.y_nodes[self.bus.arrete_m],3, "red")

if __name__ == "__main__":
    bap = BAP()
    bap.mainloop()
