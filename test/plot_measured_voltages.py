import sys
import numpy as np
import argparse
import subprocess
import re
import os
import yaml
import pickle

import matplotlib.pyplot as plt

#####################################
# Main
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", help="pickle files storing rnet voltages", type=str, nargs='*')
    args = parser.parse_args()

    for filename in args.filenames:
        #N = (7+1)*M_list[i] # N+1 x N+1 lattice
        with open(filename, mode="rb") as f:
            d = pickle.load(f)

        print(len(d))
        for i in range(len(d)):
            fig = plt.figure(figsize=(5,5))
            ax = fig.add_subplot(111)
            cntr = ax.contour(d['%d'%i], colors='blue')
            ax.clabel(cntr)
            ax.set_aspect('equal')

            plt.show()

    # #d={'case1':case1 - baseline,'case2':case2 - baseline,'case3':case3 - baseline,'case4':case4 - baseline}
    # d={}
    # for i in range(len(M_list)):
    #     N = (7+1)*M_list[i] # N+1 x N+1 lattice
    #     with open('%d_%2.1fk_results.pickle' % (M_list[i], R_list[i]), mode="rb") as f:
    #         d = pickle.load(f)
    #         print('Loaded pickled data in %d_%2.1fk_results.pickle' % (M_list[i], R_list[i]))
    #     points = [np.array([0,0]), np.array([0.5,0.5]), np.array([0.25,0.25]), np.array([0.5,0.25])]
    #     for j in range(4):
    #         fig = plt.figure(figsize=(5,5))
    #         ax = fig.add_subplot(111)
    #         cntr = ax.contour(d['case%d'%(j+1)], colors='blue')
    #         ax.clabel(cntr)
    #         ax.set_aspect('equal')

    #         points[j]
    #         int_x = int(points[j][0]*(N+1))
    #         int_y = int(points[j][1]*(N+1))
    #         ax.scatter(int_y, int_x, color='orange', s=750)


    #         plt.show()