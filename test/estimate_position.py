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
# Global variables

# Read parameters from config.yml
with open('config.yml') as file:
    config = yaml.safe_load(file.read())
    ltspice_exe = config['ltspice']
    working_dir = config['working_dir']
    filename_net_base = config['base_netlist']
    path_delimiter = config['delimiter']

#####################################
# Main
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    
    M_list = [3, 5, 7, 9]
    R_list = [2.4, 2.1, 1.9, 1.8]
    
    #d={'case1':case1 - baseline,'case2':case2 - baseline,'case3':case3 - baseline,'case4':case4 - baseline}
    d={}
    for i in range(len(M_list)):
        N = (7+1)*M_list[i] # N+1 x N+1 lattice
        with open('%d_%2.1fk_results.pickle' % (M_list[i], R_list[i]), mode="rb") as f:
            d = pickle.load(f)
            print('Loaded pickled data in %d_%2.1fk_results.pickle' % (M_list[i], R_list[i]))
        points = [np.array([0,0]), np.array([0.5,0.5]), np.array([0.25,0.25]), np.array([0.5,0.25])]
        for j in range(4):
            ave_x = 0
            ave_y = 0
            for line in range(len(d['case%d'%(j+1)])):
                for elem in range(len(d['case%d'%(j+1)][line])):
                    ave_x = ave_x + d['case%d'%(j+1)][line][elem] * line
                    ave_y = ave_y + d['case%d'%(j+1)][line][elem] * elem
            ave_x = ave_x / len(d['case%d'%(j+1)])
            ave_y = ave_y / len(d['case%d'%(j+1)])
            print('============')
            print(min(max(ave_x,0),1.0))
            print(min(max(ave_y,0),1.0))
            
            print('------------')
            print(points[j][0]*(N+1))
            print(points[j][1]*(N+1))
            