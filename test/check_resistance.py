import sys
import numpy as np
import argparse
import subprocess
import re
import os
import yaml

#####################################
# Global variables

# Read parameters from config.yml
with open('config.yml') as file:
    config = yaml.safe_load(file.read())
    ltspice_exe = config['ltspice']
    working_dir = config['working_dir']
    filename_net_base = config['base_netlist']
    path_delimiter = config['delimiter']

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("M", help="M edges between two input/output nodes (terminals)", type=int)
    parser.add_argument("R", help="resistance (kOhm)", type=float)
    args = parser.parse_args()

    M = args.M
    R = args.R

    N = (7+1)*M # N+1 x N+1 lattice

    # make a map of all nodes
    map_node = np.arange((N+1)*(N+1))
    map_node = map_node + 1

    # translate to node labels
    map_node = ["N%03d" % node for node in map_node]
    # place GND
    map_node[-1] = "0"
    
    # reshape the list to a square matrix
    map_node = np.array(map_node)
    map_node = map_node.reshape([(N+1),(N+1)])
    
    ##################################################
    # Contents generation from here
    print("Generating netlist with M=%d, R=%2.1fk..." % (M,R) )
    filename = '%d_%2.1fk_test.net' % (M,R) 
    with open(filename,'w') as f:
        # comments for simulation setup
        print( "* M:%d, R:%2.1fk, In:N%03d, GND:N%03d" % (M, R, 1, (N+1)*(N+1)) , file=f)
        # rows of resisters
        count_r = 1
        for i in range(N+1):
            for j in range(N):
                print( "R%d %s %s %2.1fk" % (count_r, map_node[i,j], map_node[i,j+1], R) , file=f)
                count_r = count_r + 1
        # columns of resisters
        for i in range(N):
            for j in range(N+1): 
                print( "R%d %s %s %2.1fk" % (count_r, map_node[i,j], map_node[i+1,j], R) , file=f)
                count_r = count_r + 1
        # input
        print( "I1 0 N%03d 1mA" % 1, file=f)
        # simulation setups
        print( ".op", file=f)
        # measure setups
        print( ".meas OP V_entire PARAM V(N%03d)" % 1, file=f)
        # finalize
        print( ".backanno" , file=f)
        print( ".end" , file=f)

    ##################################################
    # Simulation from here
    file_path = working_dir+path_delimiter
    print("Launching a subprocess with %s..." % (file_path+filename) )
    # Run LTspice
    subprocess.run([ltspice_exe, '-b', file_path+filename])
    print("Subprocess is closed.")
    # Read log file
    print("Reading data from %s..." % (file_path+re.sub('.net','.log',filename)) )
    with open(file_path+re.sub('.net','.log',filename)) as f:
        data_lines = f.read()
    try:
        m = re.search(r'v_entire: v\(n001\)=([+-]?[0-9]+[\.]?[0-9]+)', data_lines)
    except AttributeError as e:
        print('AttributeError: ', e)
    
    # Show results
    print('---')
    print(m.group(1)+" kOhm")
    
