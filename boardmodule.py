import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import enum
from enum import Enum
from walkermodule import Walker, Status

def roll(p):
    # Returns true with probability p and false with probability 1-p
    return np.random.random() < p

def roll2(M):
    #M is a dictionary. This returns one of its keys at random
    #with M's values are the probability weights
    return np.random.choice(list(M.keys()), p=list(M.values()))

t = 0
#relative size of moving dots on the plotted scatter
blob_size = 30

class Board:
    #colours of the walkers in the different states
    visuals = {Status.SUSCEPTIBLE: "b", Status.ASYMPTOMATIC: "m", Status.PRESYMPTOMATIC: "y", Status.INFECTED: "r", Status.RECOVERED: "g", Status.DEAD: "k"}
    SIR_visuals = ["b", "r", "g"]
    def __init__(self, width, height, density):
        self.width = width
        self.height = height
        self.density = density
        #we initialise the walkers as en empty list that we later add to
        self.walkers = []
        #each instance of the class Board has its own instance variables for the scatter plot
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(2,1,1)
        self.ax2 = self.fig.add_subplot(2,1,2)
        self.scat = self.ax1.scatter([],[], s=[blob_size], c=["b"])
        self.ax1.set_xlim(0, self.width)
        self.ax1.set_ylim(0, self.height)
        #self.ax2.set_xlim(0,1000)
        self.ax2.set_ylim(0,1.0)
        self.plot_lines = []


    def update(self):
        #updates the state of the board based on the individual updates of each walker
        for walker in self.walkers:
            walker.walk()
            walker.test()
            walker.update_status()

    def find_infected(self):
        #returns a list of all the infected walkers on the board
        for walker in self.walkers:
            if (walker.is_infected() or walker.is_presymptomatic() or walker.is_asymptomatic()):
                yield walker
    def find_app_users(self):
        for walker in self.walkers:
            if not (walker.is_recovered() or walker.is_dead()):
                if walker.uses_app():
                    yield walker

    def plot_board(self,frame):
        #this function plots the board
        #plt.subplot(211)
        xdata = []
        ydata = []
        colour_data = []
        #initialising numbers of walkers in each state
        self.num_sus, self.num_pre, self.num_asym, self.num_inf, self.num_rec, self.num_dead = 0,0,0,0,0,0
        #updates the board and the plotting arguments
        self.update()
        #print(Board.visuals)
        for walker in self.walkers:
            xdata.append(walker.x)
            ydata.append(walker.y)
            #print(walker.status)
            colour_data.append(Board.visuals[walker.status])
            if walker.is_susceptible():
                self.num_sus += 1
            elif walker.is_presymptomatic():
                self.num_pre +=1
            elif walker.is_asymptomatic():
                self.num_asym +=1
            elif walker.is_infected():
                self.num_inf +=1
            elif walker.is_recovered():
                self.num_rec +=1
            elif walker.is_dead():
                self.num_dead +=1
        self.num_walkers = len(self.walkers)
        self.numbers = [self.num_sus+self.num_pre+self.num_asym, self.num_inf, self.num_rec+self.num_dead]
        self.plot_lines.append([i/self.num_walkers for i in self.numbers])
        #print(self.plot_lines)
        #sets the scatter parameters to our parameters
        self.scat.set_offsets(np.c_[xdata, ydata])
        self.scat.set_color(colour_data)
#        print(f"infected={self.num_inf}, asymptomatic={self.num_asym}, presymptomatic={self.num_pre}, recovered={self.num_rec}, dead={self.num_dead}")
        #plt.subplot(212)
        self.graph_board()
    def graph_board(self):
        global t
        t += 1
        if t == 10:
            for i in range(3):
            #    if self.num_inf + self.num_pre + self.num_asym == 0:
                timeseries = [ x[i] for x in self.plot_lines ]
                self.ax2.plot(range(len(self.plot_lines)),timeseries, self.SIR_visuals[i])
                #plt.legend(fontsize="xx-large")
                t = 0
