import numpy as np
import random 
import tqdm

class MACS: 
    
    def __init__(self, nb_ants, nb_buses, nb_buslines, tau_0, visibility, beta,\
                 rho,q_0,mainstop, constant, time,passangers, alpha):
        self.nb_ants = nb_ants
        self.nb_buses = nb_buses
        self.nb_buslines = nb_buslines
        self.tau_0 = tau_0
        self.pheromone_level = tau_0*np.ones((nb_buses+1, nb_buses+1, nb_buslines))
        self.visibility = visibility
        self.non_visited_stops = np.ones((nb_ants, nb_buses))
        self.beta = beta
        self.rho = rho 
        self.q_0 = q_0
        self.solutions = [  [[] for i in range(self.nb_buslines)]  for j in range (self.nb_ants) ]
        self.global_solution = [[] for i in range(self.nb_buslines)]
        self.L_gb = 100000
        self.mainstop = mainstop
        self.mainstop_visited = np.ones((nb_buslines,nb_ants))
        self.mainstop_bis = [mainstop for i in range(nb_ants)]
        self.constant = constant
        self.time = time
        self.passangers = passangers
        self.alpha = alpha
    def probability (self, busline, ant, arret1, arret2, J_ant) :
            somme = np.sum(self.pheromone_level[arret1,1:,busline]*self.visibility[arret1-1,:,busline]**self.beta*J_ant)
            return self.pheromone_level[arret1, arret2, busline]*self.visibility[arret1-1, arret2-1, busline]**self.beta*J_ant[arret2-1]/somme
        
    def probability_0 (self, busline, ant, arret1, arret2, J_ant) :
            somme = np.sum(self.pheromone_level[arret1,1:,busline]*J_ant)
            return self.pheromone_level[arret1, arret2, busline]*J_ant[arret2-1]/somme
        
    def busstop_choice_start(self, busline, ant) : 
        J_ant = self.non_visited_stops[ant,:]
        weights = [self.probability_0( busline, ant, 0, i,J_ant) for i in range(1,self.nb_buses+1)  if self.probability( busline, ant, 0, i,J_ant)!=0]
        print("population : ", list(np.where(J_ant == 1)[0]),  "weigths : ", weights)
        weights[self.mainstop_bis[ant]] = 0
        r = random.choices(list(np.where(J_ant == 1)[0]), weights)[0]
        if r< self.mainstop_bis[ant] :
            self.mainstop_bis[ant]-=1
        self.non_visited_stops[ant,:][r] = 0
        if r==self.mainstop :
            self.mainstop_visited[busline,ant] = 0
            
        return r
       
    def update_pheromone_3(self, busline, stop1, stop2) :
        #print(self.pheromone_level[stop1,stop2,busline])
        self.pheromone_level[stop1,stop2,busline] *= (1-self.rho)
        #print(self.pheromone_level[stop1,stop2,busline])
        self.pheromone_level[stop1,stop2,busline] += self.rho * self.tau_0 
        #print(self.pheromone_level[stop1,stop2,busline])
    
    
    def step2 (self) :
        for i in range(self.nb_buslines) :
            for j in range(self.nb_ants) : 
                r = self.busstop_choice_start(i, j)
                self.solutions[j][i].append(r)
                print(self.pheromone_level[0,r,i])
                self.update_pheromone_3( i, 0, r)
                print(self.pheromone_level[0,r,i])

    def next_stop(self, busstops, ant) : 
        q = random.uniform(0,1)
        J_ant = self.non_visited_stops[ant,:]
        J_init ={}
        if q <= self.q_0 :
            #print("inferior")
            for l in range(self.nb_buslines):
                probas = self.pheromone_level[busstops[l],1:,l]*self.visibility[busstops[l]-1,:,l]**self.beta*J_ant
                #print("proba :", probas)
                
                probas[self.mainstop] *= self.mainstop_visited[l,ant]
                #print("new proba :", probas)
                J_init[np.argmax(probas)] =   [probas[np.argmax(probas)],busstops[l],l]
            J = np.max(list(J_init.keys()))
            #print("J :",J, "J_init :", J_init)
            actual_busstop = J_init[J][1]
            colony  = J_init[J][2]
        else : 
            #print("superior")
            for l in range(self.nb_buslines):
                weights = [self.probability( l, ant, busstops[l]+1, i+1, J_ant) for i in range(len(J_ant)) if J_ant[i]==1 ]
                J_init[l] = random.choices(list(np.where(J_ant == 1)[0]), weights)[0]
            intermediate_list = list(J_init.values())
            #print("intermediate list : ",intermediate_list)
            colony = random.choices(range(len(intermediate_list)))[0]
            #print("colony : ",colony)
            actual_busstop = busstops[colony]
            J = intermediate_list[colony]
            if  J ==self.mainstop : 
                while self.mainstop in self.solutions[ant][colony]:
                    colony = random.choices(range(len(intermediate_list)))[0]
        #print(J,actual_busstop,colony)
        #print("-----------------")
        return J,actual_busstop,colony
      
    def step3 (self):
        for w in range(self.nb_buses-1):
            for k in range(self.nb_ants) :
                #print("non_visited : ", self.non_visited_stops[k,:])
                busstops = self.solutions[k]
                busstops = [elt[len(elt)-1] for elt in busstops]
                #if k==0 : print("busstops : ",busstops)
                #print(np.shape(self.pheromone_level) , np.shape(self.visibility),np.shape(self.non_visited_stops))
                #print("ant : ", k)
                J,actual_busstop,colony = self.next_stop(busstops, k)
                if J == self.mainstop : 
                    self.mainstop_visited[colony,k] = 0
                #print("visied mainstop : ",self.mainstop_visited)

                
                if J != self.mainstop :
                    self.non_visited_stops[k,:][J] = 0
                if J == self.mainstop and ( self.nb_ants-np.sum(self.mainstop_visited[:,k]))==self.nb_ants: 
                 #    print('hey',k)
                     self.non_visited_stops[k,:][J] = 0
                #print("k:",k,"actual_busstop :",actual_busstop)
                self.solutions[k][colony].append(J)
                #print(self.solutions)
                self.update_pheromone_3(colony, actual_busstop, J)
    
    def compute_U_k(self,S_k):
        U_k = np.zeros((self.nb_buses, self.nb_buses))
        for i in range(len(S_k)) :
            for j in range(len(S_k[i])-1):
                u_temp = 0
                for m in range(j+1,len(S_k[i])):
                    U_k[S_k[i][j],S_k[i][m]] = 1/self.visibility[S_k[i][j],S_k[i][m],0] + u_temp
                    u_temp += 1/self.visibility[S_k[i][j],S_k[i][m],0]
        for i in range(self.nb_buses) : 
            for j in range(self.nb_buses): 
                if U_k[i,j]==0 and i!=j :
                     U_k[i,j] =  U_k[i,self.mainstop] + U_k[self.mainstop,j] + self.constant
        return U_k
    def compute_ATT(self,U_k) : 
        sum_y = np.sum(U_k*self.passangers,axis = 1)
        sum_t_y = np.sum(self.passangers, axis = 1)
        return np.sum(sum_y/sum_t_y)/self.nb_buses
    
      
    def update_pheromone_4(self, busline, stop1, stop2) :
        self.pheromone_level[stop1,stop2,busline] *= (1-self.alpha)
        
    def step4(self) :
        self.global_solution = self.solutions[0]
        print(self.global_solution)
        for  k in range(self.nb_ants) : 
            U_k = self.compute_U_k(self.solutions[k])
            L = self.compute_ATT(U_k)
            if L < self.L_gb : 
                self.L_gb = L
                self.global_solution = self.solutions[k]
        for l in range(self.nb_buslines):
            for i in range(self.nb_buses+1) :
                for j in range(self.nb_buses+1) :
                    self.update_pheromone_4 (l, i, j)
    
            for i in range(len(self.global_solution)) :
                for j in range(len(self.global_solution)-1):
                    self.pheromone_level[self.global_solution[i][j]+1,self.global_solution[i][j+1]+1,l] += self.alpha / self.L_gb 

            
    def loop(self,t_max):
        for _ in tqdm.tqdm(range(t_max)):
            self.step2()
            self.step3()
            self.step4()
            
            self.solutions = [ [[] for i in range(self.nb_buslines)]  for j in range (self.nb_ants) ]
            self.non_visited_stops = np.ones((self.nb_ants, self.nb_buses))
            self.mainstop_visited = np.ones((self.nb_buslines,self.nb_ants))
            self.mainstop_bis = [self.mainstop for i in range(self.nb_ants)]
     
        
if __name__ == "__main__": 
    v=np.array([[1e15 ,4.03196307e-03, 5.18023471e-03, 4.47455287e-03, 3.09561919e-03],
                [4.03196307e-03, 1e15, 5.57763435e-03 ,3.48170083e-03 , 4.76190476e-03],
                [5.18023471e-03, 5.57763435e-03, 1e15, 9.24144955e-03, 7.57141343e-03],
                [4.47455287e-03, 3.48170083e-03, 9.24144955e-03, 1e15, 5.34270673e-03],
                [3.09561919e-03, 4.76190476e-03, 7.57141343e-03, 5.34270673e-03, 1e15]])
    
    visibility = np.zeros((5,5,2))
    visibility[:,:,0] = v
    visibility[:,:,1] = v
    passangers = np.ones((5,5))-np.eye(5)
    macs= MACS(2,5,2,0.8,visibility,1,0.1,0.8,2,5, visibility, passangers  , 0.3)
    t_max = 10
    for t in tqdm.tqdm(range(t_max)):
        #print("step2 : ,",macs.pheromone_level)
        macs.step2()
        #print("step3 : ,",macs.pheromone_level)
        macs.step3()
        #print("step4 : ,",macs.pheromone_level)
        macs.step4()
        #print("final : ,",macs.pheromone_level)

        macs.non_visited_stops = np.ones((macs.nb_ants, macs.nb_buses))
        macs.solutions = [ [[] for i in range(macs.nb_buslines)]  for j in range (macs.nb_ants) ]
        macs.non_visited_stops = np.ones((macs.nb_ants, macs.nb_buses))
        macs.mainstop_visited = np.ones((macs.nb_buslines,macs.nb_ants))
        macs.mainstop_bis = [macs.mainstop for i in range(macs.nb_ants)]
        print("--------------------------------------------")

    print(macs.global_solution)

    
    
    
    





        
        


            
            
        
        
        
        