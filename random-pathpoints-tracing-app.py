import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import enum
from enum import Enum
import pandas as pd
from modelclass import Model
from boardmodule import Board
from walkermodule import Status
import sys
#import mapmodule

def roll(p):
    # Returns true with probability p and false with probability 1-p
    return np.random.random() < p

def roll2(M):
    #M is a dictionary. This returns one of its keys at random
    #with M's values are the probability weights
    return np.random.choice(list(M.keys()), p=list(M.values()))

def animation():
    #end_frame =
    myboard = Board(200,200, 34/10000)
    mymodel = Model(myboard, 0, 0, 0)
    for _ in range(100):
        mymodel.add_walker(Status.SUSCEPTIBLE)
    for _ in range(10):
        mymodel.add_walker(Status.INFECTED)
    ani = FuncAnimation(mymodel.board.fig, mymodel.board.plot_board, frames=range(1000), interval = 1/mymodel.fps, repeat=False)
    ani.save("simulation.mp4",dpi=96,fps=50)
    #graph = myboard.graph_board()
    #plt.show()

animation()

def save_data(bigness, density, percent_healthy, useappc, radiusc, speedc):
    df = pd.DataFrame(columns=["Iterations", "Susceptible", "Infected", "Recovered", "Dead"])
    iterations = 0
    num_sus,num_inf,num_end = 0,0,0
    #data_file = open("saved-data.txt", "w+")
    myboard = Board(bigness, bigness, density)
    mymodel = Model(myboard, useappc, radiusc, speedc)
    num_walkers = bigness**2*density
    for _ in range(int(num_walkers*percent_healthy)):
        mymodel.add_walker(Status.SUSCEPTIBLE)
        num_sus +=1
    for _ in range(int(num_walkers*(1-percent_healthy)*mymodel.incubate_prob[Status.PRESYMPTOMATIC])):
        mymodel.add_walker(Status.PRESYMPTOMATIC)
        num_inf +=1
    for _ in range(int(num_walkers*(1-percent_healthy)*mymodel.incubate_prob[Status.ASYMPTOMATIC])):
        mymodel.add_walker(Status.ASYMPTOMATIC)
        num_inf +=1
    list_sus = [num_sus]
    list_inf = [num_inf]
    list_end = [num_end]
    while num_inf > num_walkers*mymodel.detectability_threshold:
        num_inf, num_sus, num_end = 0,0,0
        for walker in myboard.walkers:
            if walker.is_susceptible():
                num_sus +=1
            elif (walker.is_infected() or walker.is_presymptomatic() or walker.is_asymptomatic()):
                num_inf +=1
            else:
                num_end +=1
        list_sus.append(num_sus)
        list_inf.append(num_inf)
        list_end.append(num_end)
        iterations += 1

        #print(f"new iteration: {iterations}, num_inf: {num_inf}")
        myboard.update()
    num_rec = 0
    for walker in myboard.walkers:
        if walker.is_recovered():
            num_rec +=1
        num_dead = num_end - num_rec
    data = {"Iterations": iterations, "Susceptible": num_sus, "Infected": num_inf, "Recovered": num_rec, "Dead": num_dead, "Radius factor": radiusc, "Speed factor": speedc}
    df = df.append(data, ignore_index=True)
    df.to_csv(f"saved-data-app{useappc}.csv", index=False, mode="a")

    fig,ax = plt.subplots()

    ax.plot(range(iterations+1),list_sus, "b", label="Susceptible")
    ax.plot(range(iterations+1),list_inf, "r", label="Infected")
    ax.plot(range(iterations+1),list_end, "g", label="Recovered")
    plt.xlabel("Number of frames")
    plt.ylabel("Number of walkers")
    plt.title("SIR curve with all traced\nNo radius of contagion")
    plt.legend(fontsize="xx-large")

#given = int(sys.argv[1])
#for bigness in range(50,201,5):
#useapp_proportion = int(sys.argv[1])


save_data(50,0.01,0.93, 0, 0,0)
plt.savefig(f"title.png")
#save_data(400,34/10000,0.93, 1, 0,0)
#plt.savefig(f"data-alltracing.png")
plt.close("all")
#plt.show()
