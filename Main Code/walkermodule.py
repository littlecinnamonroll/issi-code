import random
import numpy as np
import enum
from enum import Enum

def roll(p):
    # Returns true with probability p and false with probability 1-p
    return np.random.random() < p

def roll2(M):
    #M is a dictionary. This returns one of its keys at random
    #with M's values are the probability weights
    return np.random.choice(list(M.keys()), p=list(M.values()))

class Pathpoint:
    def __init__(self, walker):
        self.walker = walker
        self.board = walker.board
        self.x = np.random.randint(self.board.width)
        self.y = np.random.randint(self.board.height)

class Status(Enum):
    #the different statuses that our walker can have
    SUSCEPTIBLE = 0
    ASYMPTOMATIC = 1
    PRESYMPTOMATIC = 2
    INFECTED = 3
    RECOVERED = 4
    DEAD = 5

class Walker:

    def __init__(self, x, y, status, board,model):
        self.x = x
        self.y = y

        self.status = status
        self.alert_status = 0
        self.test_status = 0
        self.board = board
        self.model = model
        self.infect_radius = self.model.infect_radius
        self.tracing_dict = {}
        self.speed = 0.5 #later, we can vary speeds for different walkers
        self.pathpoint = Pathpoint(self)
        self.app_use = roll(self.model.uses_app_chance)
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
        dist_to_pathpoint = self.distance(self.pathpoint)
        if dist_to_pathpoint > 1:
            #print(f"my coordinates are {self.x} {self.y}, moving towards {self.pathpoint.x} {self.pathpoint.y}")
            vector = np.array([self.pathpoint.x-self.x, self.pathpoint.y-self.y])
            scaling_factor = self.speed/dist_to_pathpoint
            self.x += scaling_factor*vector[0]
            self.y += scaling_factor*vector[1]
        else:
            #print("new pathpoint")
            if roll(0.3):
                self.new_pathpoint()
    def test(self):
            if not (self.is_infected() or self.is_recovered() or self.is_dead()):
                if roll(self.model.test_chance):
                    if ((self.is_susceptible() and roll(self.model.false_positive)) or (self.is_presymptomatic() or self.is_asymptomatic()) and roll(1-self.model.false_negative)):
                        self.test_status = 1
                        for i in self.traced_list:
                            if not i.is_alerted():
                                i.alert()
                    else:
                        pass

    def is_susceptible(self):
        return self.status == Status.SUSCEPTIBLE
        #returns true if susceptible and false otherwise
    def is_presymptomatic(self):
        return self.status == Status.PRESYMPTOMATIC
    def is_asymptomatic(self):
        return self.status == Status.ASYMPTOMATIC
    def incubate(self):
        self.status = roll2(self.model.incubate_prob)
    def alert(self):
        if not self.is_alerted():
            self.infect_radius *= self.model.alerted_radius_reduction
            self.speed *= self.model.alerted_speed_reduction
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
            #app_users.remove(self)
            current_app_neighbours = [x for x in app_users if self.distance(x)<= self.model.app_radius]
        else:
            current_app_neighbours = []
        #using the class radius as the app doesn't know about precautions the other person took
        for x in self.board.walkers:
            if x in current_app_neighbours and not (x in self.traced_list):
                if x in self.tracing_dict.keys():
                    self.tracing_dict[x] += 1
                else:
                    self.tracing_dict[x] = 1
            else:
                self.tracing_dict[x] = 0
            if self.tracing_dict[x] == 3:
                self.traced_list.append(x)
    def update_status(self):
        self.log_neighbours()
        no_of_infected_neighbours = self.no_of_infected_neighbours()
        if self.is_susceptible() and (no_of_infected_neighbours > 0):
            if roll(1-(1-self.model.infected_probability)**(no_of_infected_neighbours)):
                self.incubate()
                if self.is_asymptomatic():
                    self.infect_radius *= 0.32 #area of infection reduces approx. 10 times
        elif self.is_asymptomatic():
            if roll(self.model.recover_chance):
                self.status = Status.RECOVERED
        elif self.is_presymptomatic():
            if roll(self.model.symptom_chance):
                self.status = Status.INFECTED
                if self.uses_app():
                    self.alert()
            #    if self.alert_status == 0:
                for walker in self.traced_list:
                    if not walker.is_alerted():
                        walker.alert()
        elif self.is_infected():
            #if infected, transition to the recovered or dead state
            self.status = roll2(self.model.M)
