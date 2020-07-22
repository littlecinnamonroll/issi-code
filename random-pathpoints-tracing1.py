import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import enum
from enum import Enum
import pandas as pd
from modelclass import Model
from boardmodule import Board
from walkermodule import Status
#import mapmodule

def roll(p):
    # Returns true with probability p and false with probability 1-p
    return np.random.random() < p

def roll2(M):
    #M is a dictionary. This returns one of its keys at random
    #with M's values are the probability weights
    return np.random.choice(list(M.keys()), p=list(M.values()))

def setup():
    #end_frame =
    myboard = Board(100,100)
    mymodel = Model(myboard)
    for _ in range(100):
        mymodel.add_walker(Status.SUSCEPTIBLE)
    for _ in range(10):
        mymodel.add_walker(Status.INFECTED)
    ani = FuncAnimation(mymodel.board.fig, mymodel.board.plot_board, frames=range(100), interval = 1/mymodel.fps, repeat=True)
    #graph = myboard.graph_board()
    plt.show()

#setup()
#bigness = 100
#percent_healthy = 93


def save_data(bigness, density, percent_healthy):
    df = pd.DataFrame(columns=["Iterations", "Susceptible", "Infected", "Recovered/Dead"])
    iterations = 0
    num_inf = 0
    #data_file = open("saved-data.txt", "w+")
    myboard = Board(bigness, bigness, density)
    mymodel = Model(myboard)
    for _ in range(int(bigness**2*density*percent_healthy)):
        mymodel.add_walker(Status.SUSCEPTIBLE)
    for _ in range(int(bigness**2*density*(1-percent_healthy)*mymodel.incubate_prob[Status.PRESYMPTOMATIC])):
        mymodel.add_walker(Status.PRESYMPTOMATIC)
        num_inf +=1
    for _ in range(int(bigness**2*density*(1-percent_healthy)*mymodel.incubate_prob[Status.ASYMPTOMATIC])):
        mymodel.add_walker(Status.ASYMPTOMATIC)
        num_inf +=1
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
    df.to_csv(r"saved-data-1.csv", index=False, mode="a")
save_data(100,0.02,0.93)
