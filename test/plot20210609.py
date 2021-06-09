import sys
import numpy as np
import argparse
import subprocess
import re
import os
import yaml
import pickle

import matplotlib.pyplot as plt
import matplotlib.animation as animation

#####################################
# Main
if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--save', help='flag for saving', action='store_true')
    args = parser.parse_args()

    M=13
    N=(7+1)*M+1
    with open('./13_1.70k_results_helix_original.pickle', mode="rb") as f:
        d = pickle.load(f)

    # touching points
    theta = np.linspace(0, 2 * np.pi, 100)
    X = np.linspace(0, 1.0, 100) * (np.sin(theta)/2.0) + 0.5
    Y = np.linspace(0, 1.0, 100) * (np.cos(theta)/2.0) + 0.5
    
    ims = []
    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111)

    def plot(indx):
        plt.cla()
        cntr = ax.contour(d['%d'%indx], colors='blue')
        #ax.clabel(cntr)
        ax.set_aspect('equal')
        int_x = int(X[indx]*(N+1))
        int_y = int(Y[indx]*(N+1))
        ax.scatter(int_y, int_x, color='orange', s=750)
    
    ani = animation.FuncAnimation(fig, plot, frames=range(100), interval=100)

    if args.save:
        ani.save('anim.gif', writer="imagemagic")
    else:
        plt.show()