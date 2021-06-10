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
    with open('./13_1.70k_baseline.pickle', mode="rb") as f:
        baseline = pickle.load(f)

    # touching points
    theta = np.linspace(0, 2 * np.pi, 100)
    X = np.linspace(0, 1.0, 100) * (np.sin(theta)/2.0) + 0.5
    Y = np.linspace(0, 1.0, 100) * (np.cos(theta)/2.0) + 0.5
    
    ims = []
    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111)

    def plot(indx):
        plt.cla()
        ret_v = np.abs(np.diff(d['%d'%indx],axis=0)-np.diff(baseline,axis=0))
        ret_v = (ret_v[:,1:]+ret_v[:,:-1])/2.0
        ret_h = np.abs(np.diff(d['%d'%indx])-np.diff(baseline))
        ret_h = (ret_h[1:,:]+ret_h[:-1,:])/2.0
        ret = ret_v + ret_h
        #ret = np.where(ret > np.mean(ret)*10.0, ret, 0)

        cntr = ax.contour(ret, colors='blue')
        ax.set_aspect('equal')
        int_x = int(X[indx]*(N+1))
        int_y = int(Y[indx]*(N+1))
        ax.scatter(int_y, int_x, color='orange', s=750)
        ax.set_xlim(0, 103)
        ax.set_ylim(0, 103)
    
    ani = animation.FuncAnimation(fig, plot, frames=range(100), interval=100)

    if args.save:
        ani.save('anim_feature.gif', writer="imagemagic")
    else:
        plt.show()