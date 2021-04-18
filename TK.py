from tkinter import *
from tkinter.messagebox import showinfo
import random


# --------------------------------------------------------


class ZoneAffichage(Canvas):
    def __init__(self, parent, w=500, h=400, _bg='white'):  # 500x400 : dessin final !
        self.__w = w
        self.__h = h
        self.__liste_noeuds = []

        # Pour avoir un contour pour le Canevas
        self.__fen_parent=parent
        Canvas.__init__(self, parent, width=w, height=h, bg=_bg, relief=RAISED, bd=1)


    def get_dims(self):
        return (self.__w, self.__h)


    def creer_noeud(self, x_centre, y_centre, rayon , col, fill_color="black"):
        noeud = Balle(self, x_centre, y_centre, rayon , col, fill_color)
        self.pack()
        return noeud


    def placer_un_noeud_sur_canevas(self, x_centre, y_centre, col=None, fill_color="black"):
        w,h = self.get_dims()
        rayon=5
        if col == None :
            col = "red"
            #col= random.choice(['green', 'blue', 'red', 'magenta', 'black', 'maroon', 'purple', 'navy', 'dark cyan'])

        node=self.creer_noeud(x_centre, y_centre, rayon , col, fill_color)
        self.update()

        return node


    #add node ---------------------------
    def action_add_node(self, event):
        print("Trace : (x,y) = ", event.x, event.y)
        self.__fen_parent.placer_un_noeud(event.x, event.y)
    

    #delete node ---------------------------
    def action_delete_node(self, event):
        for elt in self.__fen_parent.list_node :
            x,y,r = elt.get_info_balle()
            i = elt.get_node_ident()
            if abs(x-event.x) <= r and abs(y-event.y) <= r:
                print("Deleted : (x,y) = ", x, y)
                self.__fen_parent.list_node.remove(elt)
                del self.__fen_parent.node_info[i]

                for key in list(self.__fen_parent.route_info.keys()):
                    if str(i) in key.split("-"):
                        self.delete(self.__fen_parent.route_info[key][-1])
                        del self.__fen_parent.route_info[key]

                self.delete(elt.get_node_ident())

        self.update()
    
    #prop node ---------------------------
    def action_def_node(self, event):
        for elt in self.__fen_parent.list_node :
            x,y,r = elt.get_info_balle()
            if abs(x-event.x) <= r and abs(y-event.y) <= r:
                print("Prop node : (x,y) = ", x, y)
                InfoNode(self.__fen_parent, elt.get_node_ident())
        

    #prop line ---------------------------
    def action_def_line(self,event):
        done = False
        last = self.__fen_parent.route_last
        for elt in self.__fen_parent.list_node :
            x,y,r = elt.get_info_balle()
            if abs(x-event.x) <= r and abs(y-event.y) <= r:
                if last == None:
                    print("First node selected : (x,y) = ", x, y)
                    self.__fen_parent.route_last = elt
                    done = True
                elif elt != last:
                    print("Second node selected : (x,y) = ", x, y)

                    id1 = last.get_node_ident()
                    id2 = elt.get_node_ident()

                    if id1 > id2:
                        id2,id1 = id1,id2

                    id_route = str(id1)+'-'+str(id2)

                    if id_route in self.__fen_parent.route_info:
                        InfoRoute(id_route, self.__fen_parent, self.__fen_parent.route_last, elt, True)
                    else:
                        InfoRoute(id_route, self.__fen_parent, self.__fen_parent.route_last, elt, False)
                            
        if not done:
            self.__fen_parent.route_last = None
    




class FenPrincipale(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('BAP Solver')
        self.__zoneAffichage = ZoneAffichage(self)
        self.__zoneAffichage.pack()
        self.__var = IntVar()

        # Création des Buttons
        #self.__boutonEffacer = Button(self, text='Undo', command=self.undo_last_node).pack(side=LEFT, padx=5, pady=5)
        self.__bouton1 = Radiobutton(self, text='Add node', command=self.add_node, variable=self.__var, value=1).pack(side=LEFT, padx=5, pady=5)
        self.__bouton2 = Radiobutton(self, text='Delete node', command=self.delete_node, variable=self.__var, value=2).pack(side=LEFT, padx=5, pady=5)
        self.__bouton3 = Radiobutton(self, text='Node properties', command=self.prop_node, variable=self.__var, value=3).pack(side=LEFT, padx=5, pady=5)
        self.__bouton4 = Radiobutton(self, text='Line properties', command=self.prop_line, variable=self.__var, value=4).pack(side=LEFT, padx=5, pady=5)
        #self.__bouton5 = Radiobutton(self, text='Reset node', command=self.reset_node, variable=self.__var, value=5).pack(side=LEFT, padx=5, pady=5)
        self.__bouton6 = Button(self, text='Restart', command=self.restart).pack(side=LEFT, padx=5, pady=5)
        self.__boutonQuitter = Button(self, text='Quit', command=self.destroy).pack(side=LEFT, padx=5, pady=5)
        

        
        self.__liste_coordonnes_centre_des_nodes=[]
        
        
        self.list_node=[]
        self.node_info = dict()
        self.route_info = dict()
        self.route_last = None

        self.hover_text = self.__zoneAffichage.create_text(0,0,fill="red",text="")

        self.bind('<Motion>', self.motion)

    # detect if we hover a node
    def motion(self, event):
        done = False
        for elt in self.list_node :
            x,y,r = elt.get_info_balle()
            i = elt.get_node_ident()
            m,n = self.node_info[i]
            if abs(x-event.x) <= r and abs(y-event.y) <= r:
                self.__zoneAffichage.delete(self.hover_text)
                self.hover_text = self.__zoneAffichage.create_text(x+50,y,fill="red",text="Nb_up=%s\nNb_down=%s"%(m,n))
                done = True
        if not done:
            self.__zoneAffichage.delete(self.hover_text)
            self.hover_text = self.__zoneAffichage.create_text(0,0,fill="red",text="")

        
    #add node ---------------------------
    def add_node(self):
        self.__zoneAffichage.bind('<Button-1>', self.__zoneAffichage.action_add_node)

    #delete node ---------------------------
    def delete_node(self):
        self.__zoneAffichage.unbind("<Button 1>")
        if len(self.list_node)>=1:
            self.__zoneAffichage.bind('<Button-1>', self.__zoneAffichage.action_delete_node)
        
    
    #prop node ---------------------------
    def prop_node(self):
        self.__zoneAffichage.unbind("<Button 1>")
        if len(self.list_node)>=1:
            self.__zoneAffichage.bind('<Button-1>', self.__zoneAffichage.action_def_node)


            
    #prop line ---------------------------
    def prop_line(self):
        self.__zoneAffichage.unbind("<Button 1>")
        self.route_last = None
        if len(self.list_node)>=2:
            self.__zoneAffichage.bind('<Button-1>', self.__zoneAffichage.action_def_line)
            
    
    # line noeud --------------------------
    def line_noeud(self, x1, y1, x2, y2, col, dashed = False):
        if dashed:
            return self.__zoneAffichage.create_line(x1, y1, x2, y2, fill=col, dash=(5, 1))
        else:
            return self.__zoneAffichage.create_line(x1, y1, x2, y2, fill=col)


    def restart(self):
        self.__zoneAffichage.delete(ALL)
        self.__liste_coordonnes_centre_des_nodes.clear()

        self.list_node = []
        self.node_info = dict()
        self.route_info = dict()
        self.route_last = None
        
    def placer_un_noeud(self, x, y):
        node = self.__zoneAffichage.placer_un_noeud_sur_canevas(x,y)
        self.list_node.append(node)
        self.node_info[node.get_node_ident()] = [0,0]
        self.__liste_coordonnes_centre_des_nodes.append((x,y))


#--------------------------
class InfoNode(Tk):
    def __init__(self, parent, id_):
        Tk.__init__(self)
        self.parent = parent
        self.id = id_
        self.title('Info node')

        frame1 = Frame(self)
        frame1.pack()
        
        Label(frame1, text="Nombre UP\t:",width = 15).pack(side = LEFT)
        
        v1 = StringVar(frame1, value=str(self.parent.node_info[self.id][0]))
        self.E1 = Entry(frame1, bd=1,width = 30, textvariable=v1)
        self.E1.pack(side = RIGHT)
        
        frame2 = Frame(self)
        frame2.pack()
        
        Label(frame2, text="Nombre DOWN  :",width = 15).pack(side = LEFT)

        v2 = StringVar(frame2, value=str(self.parent.node_info[self.id][1]))
        self.E2 = Entry(frame2, bd=1,width = 30, textvariable=v2)
        self.E2.pack(side = RIGHT)
        
        Button(self, text='Enregistrer', command=self.save_quit).pack(side=BOTTOM)

    def save_quit(self):
        try:
            n1 = int(self.E1.get())
            if n1 >= 0:
                self.parent.node_info[self.id][0] = n1

            n2 = int(self.E2.get())
            if n2 >= 0:
                self.parent.node_info[self.id][1] = n2
        except:
            print("Error with inputs!")
        

        self.update()
        self.destroy()
#--------------------------
class InfoRoute(Tk):
    def __init__(self, id_route, parent, elt1, elt2, deja_remp = False):
        Tk.__init__(self)
        self.parent = parent
        self.elt1 = elt1
        self.elt2 = elt2
        self.deja_remp = deja_remp

        self.id_r = id_route

        self.title('Info route')

        #frame 1
        frame1 = Frame(self)
        frame1.pack()
        #frame 2
        frame2 = Frame(self)
        frame2.pack()
        #frame 3
        frame3 = Frame(self)
        frame3.pack()
        #frame 4
        frame4 = Frame(self)
        frame4.pack()

        if self.deja_remp:
            v1 = StringVar(frame1, value=str(self.parent.route_info[self.id_r][2]))
            v2 = StringVar(frame2, value=str(self.parent.route_info[self.id_r][3]))
            v3 = StringVar(frame3, value=str(self.parent.route_info[self.id_r][4]))
            v4 = StringVar(frame4, value=str(self.parent.route_info[self.id_r][5]))
        else:
            v1 = StringVar(frame1, value=str(0))
            v2 = StringVar(frame2, value=str(0))
            v3 = StringVar(frame3, value=str(0))
            v4 = StringVar(frame4, value=str(0))

        Label(frame1, text="Distance :",width = 15).pack(side = LEFT)

        self.E1 = Entry(frame1, bd=1,width = 30, textvariable=v1)
        self.E1.pack(side = RIGHT)
        
        Label(frame2, text="Vitesse :",width = 15).pack(side = LEFT)

        self.E2 = Entry(frame2, bd=1,width = 30, textvariable=v2)
        self.E2.pack(side = RIGHT)

        Label(frame3, text="Frequence :",width = 15).pack(side = LEFT)

        self.E3 = Entry(frame3, bd=1,width = 30, textvariable=v3)
        self.E3.pack(side = RIGHT)
        
        Label(frame4, text="Nb libre  :",width = 15).pack(side = LEFT)

        self.E4 = Entry(frame4, bd=1,width = 30, textvariable=v4)
        self.E4.pack(side = RIGHT)

        Button(self, text='Enregistrer', command=self.save_quit).pack(side=BOTTOM)

    def save_quit(self):
        id1,id2 = self.elt1.get_node_ident(),self.elt2.get_node_ident()
        try:
            n1 = int(self.E1.get())
            n2 = int(self.E2.get())
            n3 = int(self.E3.get())
            n4 = int(self.E4.get())

            if n1 >= 0 and n2 >=0 and n3>=0 and n4 >= 0:
                x1,y1,_ = self.elt1.get_info_balle()
                x2,y2,_ = self.elt2.get_info_balle()  
                line = self.parent.line_noeud(x1, y1, x2, y2, "black", True)
                print(line)
                self.parent.route_info[self.id_r] = [id1,id2,n1,n2,n3,n4, line]
        except:
            print("Error with inputs!")
        
        self.update()
        self.destroy()
#--------------------------
class Balle:
    def __init__(self, canvas, cx, cy, rayon, couleur, fill_color="black"):
        self.__cx, self.__cy = cx, cy
        self.__rayon = rayon
        self.__color = couleur
        self.__can = canvas  # Il le faut pour les déplacements

        self.__canid = self.__can.create_oval(cx - rayon, cy - rayon, cx + rayon, cy + rayon, outline=couleur, fill=fill_color)
        # Pour 3.6 : col: object  # essaie typage !

    def get_node_ident(self):
        return self.__canid

    def get_info_balle(self):
        return self.__cx, self.__cy, self.__rayon


# --------------------------------------------------------
if __name__ == "__main__":
    fen = FenPrincipale()
    fen.mainloop()
