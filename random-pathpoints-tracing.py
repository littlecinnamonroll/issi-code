#I don't use this file any more
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import enum
from enum import Enum
import pandas as pd
#import mapmodule

#relative size of moving dots on the plotted scatter
blob_size = 30
num_inf = 0
def roll(p):
    # Returns true with probability p and false with probability 1-p
    return np.random.random() < p

def roll2(M):
    #M is a dictionary. This returns one of its keys at random
    #with M's values are the probability weights
    return np.random.choice(list(M.keys()), p=list(M.values()))

class Status(Enum):
    #the different statuses that our walker can have
    SUSCEPTIBLE = 0
    ASYMPTOMATIC = 1
    PRESYMPTOMATIC = 2
    INFECTED = 3
    RECOVERED = 4
    DEAD = 5

class Board:
    #colours of the walkers in the different states
    visuals = {Status.SUSCEPTIBLE: "b", Status.ASYMPTOMATIC: "m", Status.PRESYMPTOMATIC: "y", Status.INFECTED: "r", Status.RECOVERED: "g", Status.DEAD: "k"}
    #number of frames per second
    fps = 1000
    def __init__(self, width, height):
        self.width = width
        self.height = height
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
    def add_walker(self,status):
        #this command initialises an instance of the class Walker
        walker = Walker(np.random.randint(self.width),np.random.randint(self.height),status,self)
        #it then adds the generated walker to the list of walkers of the board that called the function
        self.walkers.append(walker)

    def update(self):
        #updates the state of the board based on the individual updates of each walker
        for walker in self.walkers:
            walker.walk()
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
        for walker in self.walkers:
            xdata.append(walker.x)
            ydata.append(walker.y)
            colour_data.append(self.visuals[walker.status])
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
        self.numbers = [self.num_sus, self.num_pre, self.num_asym, self.num_inf, self.num_rec, self.num_dead]
        self.plot_lines.append([i/self.num_walkers for i in self.numbers])
        #print(self.plot_lines)
        #sets the scatter parameters to our parameters
        self.scat.set_offsets(np.c_[xdata, ydata])
        self.scat.set_color(colour_data)
#        print(f"infected={self.num_inf}, asymptomatic={self.num_asym}, presymptomatic={self.num_pre}, recovered={self.num_rec}, dead={self.num_dead}")
        #plt.subplot(212)
        #self.graph_board()
    def graph_board(self):
        #print(self.plot_lines)
        #plt.figure(2)
        for i in range(4):
            #if self.num_inf == 0:
            timeseries = [ x[i] for x in self.plot_lines ]
            self.ax2.plot(range(len(self.plot_lines)),timeseries, list(self.visuals.values())[i])
            #plt.legend(fontsize="xx-large")
class Pathpoint:
    def __init__(self, walker):
        self.walker = walker
        self.board = walker.board
        self.x = np.random.randint(self.board.width)
        self.y = np.random.randint(self.board.height)

class Walker:
    symptom_chance = 0.01 #chance presymptomatic becomes infected
    recover = 0.02 #chance asymptomatic recovers
    infected_probability = 0.5 #chance susceptible catches the virus
    infect_radius = 5
    uses_app_chance = 0.6 #adjust to change fraciton of app users
    #probabilities for transition from infected to each of the following three states
    incubate_prob = {Status.PRESYMPTOMATIC: 0.6, Status.ASYMPTOMATIC: 0.4}
    M = {Status.INFECTED: 0.99, Status.RECOVERED: 0.007, Status.DEAD: 0.003}

    def __init__(self, x, y, status, board):
        self.x = x
        self.y = y

        self.status = status
        self.alert_status = 0
        self.board = board
        tracing_dict = {i: 0 for i in self.board.walkers}
        self.speed = 10 #later, we can vary speeds for different walkers
        self.pathpoint = Pathpoint(self)
        self.app_use = roll(self.uses_app_chance)
        self.traced_list = []
    def __string__(self):
        return "x:{}, y:{}, status:{}".format(self.x,self.y,self.status)
    def position(self):
        return (self.x,self.y)
    def distance(self, other):
        #defines distance between two walkers
        return(np.sqrt(abs(self.x-other.x)**2 + abs(self.y-other.y)**2))
    def new_pathpoint(self):
        self.pathpoint = Pathpoint(self)
    def walk(self):
        #dead people don't walk
        if self.status == Status.DEAD:
            return
        #Pau: Updated dt
        dt = 1e-2
        dist_to_pathpoint = self.distance(self.pathpoint)
        if dist_to_pathpoint > 1:
            #print(f"my coordinates are {self.x} {self.y}, moving towards {self.pathpoint.x} {self.pathpoint.y}")
            vector = np.array([self.pathpoint.x-self.x, self.pathpoint.y-self.y])
            scaling_factor = self.speed*dt/dist_to_pathpoint
            self.x += scaling_factor*vector[0]
            self.y += scaling_factor*vector[1]
        else:
            #print("new pathpoint")
            if roll(0.3):
                self.new_pathpoint()
    def is_susceptible(self):
        return self.status == Status.SUSCEPTIBLE
        #returns true if susceptible and false otherwise
    def is_presymptomatic(self):
        return self.status == Status.PRESYMPTOMATIC
    def is_asymptomatic(self):
        return self.status == Status.ASYMPTOMATIC
    def incubate(self):
        self.status = roll2(Walker.incubate_prob)
    def alert(self):
        if not self.is_alerted():
            self.radius *= 0.9
            self.speed *= 0.6
            self.alert_status = 1
    def is_infected(self):
        return self.status == Status.INFECTED
        #returns true if infected and false otherwise.
    def is_alerted(self):
        return self.alert_status == 1
    def is_recovered(self):
        return self.status == Status.RECOVERED

    def is_dead(self):
        return self.status == Status.DEAD

    def uses_app(self):
        return self.app_use

    def no_of_infected_neighbours(self):
        #finds number of people that are infected and within infect radius of a walker:
        #first, finds all the infected walkers from the board
        infected_walkers = list(self.board.find_infected())
        if self.is_infected():
            infected_walkers.remove(self)
            #don't count the walker as its own neighbour
        infected_neighbours = [x for x in infected_walkers if self.distance(x)<= x.infect_radius]
        return len(infected_neighbours)
    def log_neighbours(self):
        if self.uses_app():
            app_users = list(self.board.find_app_users())
            app_users.remove(self)
            current_app_neighbours = [x for x in app_users if self.distance(x)<= Walker.infect_radius]
        else:
            current_app_neighbours = []
        #using the class radius as the app doesn't know about precautions the other person took
        for x in self.board.walkers:
            if x in current_app_neighbours and not (x in self.traced_list):
                self.tracing_dict[x] += 1
            else:
                self.tracing_dict[x] = 0
            if self.tracing_dict[x] == 10:
                self.traced_list.append(x)
    def update_status(self):
        no_of_infected_neighbours = self.no_of_infected_neighbours()
        if self.is_susceptible() and (no_of_infected_neighbours > 0):
            if roll(1-(1-self.infected_probability)**(no_of_infected_neighbours)):
                self.incubate()
                if self.is_asymptomatic():
                    self.infect_radius *= 0.32 #area of infection reduces approx. 10 times
        elif self.is_asymptomatic():
            if roll(self.recover):
                self.status = Status.RECOVERED
        elif self.is_presymptomatic():
            if roll(self.symptom_chance):
                self.status = Status.INFECTED
                for walker in self.traced_list:
                    walker.alert()
        elif self.is_infected():
            #if infected, transition to the recovered or dead state
            self.status = roll2(Walker.M)

def setup():
    #end_frame =
    myboard = Board(100,100)
    for _ in range(100):
        myboard.add_walker(Status.SUSCEPTIBLE)
    for _ in range(10):
        myboard.add_walker(Status.INFECTED)
    ani = FuncAnimation(myboard.fig, myboard.plot_board, frames=range(100), interval = 1/myboard.fps, repeat=True)
    #graph = myboard.graph_board()
    plt.show()

setup()
#bigness = 100
#percent_healthy = 93
df = pd.DataFrame(columns=["Iterations", "Susceptible", "Infected", "Recovered", "Dead"])
iterations = 0
num_inf = 0
def save_data(bigness, percent_healthy):
    global df
    global iterations
    #data_file = open("saved-data.txt", "w+")
    myboard = Board(bigness, bigness)
    for _ in range(int(bigness*percent_healthy)):
        myboard.add_walker(Status.SUSCEPTIBLE)
    for _ in range(int(bigness*(1-percent_healthy))):
        #print(int(bigness*(1-percent_healthy)))
        myboard.add_walker(Status.INFECTED)
    num_inf = int(bigness*(1-percent_healthy))
    while num_inf > 0:
        num_inf = 0
        for walker in myboard.walkers:
            if (walker.is_infected() or walker.is_presymptomatic() or walker.is_asymptomatic()):
                num_inf +=1
        iterations += 1
        #print(f"new iteration: {iterations}, num_inf: {num_inf}")
        myboard.update()
    num_sus, num_rec, num_dead = 0,0,0
    for walker in myboard.walkers:
        if walker.is_susceptible():
            num_sus += 1
        elif walker.is_recovered():
            num_rec +=1
        elif walker.is_dead():
            num_dead +=1
    data = {"Iterations": iterations, "Susceptible": num_sus, "Infected": "0", "Recovered/Dead": num_rec + num_dead}
    df = df.append(data, ignore_index=True)
#save_data(100,0.93)
#df.to_csv(r"saved-data.csv", index=False, mode="a")
