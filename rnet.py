import sys
import numpy as np
import argparse
import subprocess
import re
import os
import yaml
import pickle

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
# Functions
def generate_map_node(M):
    N = (7+1)*M # N+1 x N+1 lattice

    node_sink = [1, N+1, (N+1)*(N+1)-N, (N+1)*(N+1)]
    
    # make a map of all nodes
    map_node = np.arange((N+1)*(N+1))
    map_node = map_node + 1

    # translate to node labels
    map_node = ["N%03d" % node for node in map_node]
    # place GND
    for i in range(len(node_sink)):
        map_node = ["0" if node==("N%03d" % node_sink[i]) else node for node in map_node]
    # make a list of replaced nodes
    node_replaced = node_sink
    node_replaced.sort(reverse=True)
    # fill gaps of node numbers by replaced nodes (make node numbers serial)
    for i in range(len(node_replaced)):
        map_node = ["N%03d" % (int(re.sub(r'N([0-9]+)', r'\1', node))-1) 
        if int(re.sub(r'N([0-9]+)', r'\1', node)) > node_replaced[i] and len(re.sub(r'N([0-9]+)', r'\1', node)) > 2 
        else node 
        for node in map_node]
    # reshape the list to a square matrix
    map_node = np.array(map_node)
    map_node = map_node.reshape([(N+1),(N+1)])
    
    return map_node

def generate_base_netlist(M, R, I=True):
    N = (7+1)*M # N+1 x N+1 lattice
    map_node = generate_map_node(M)

    ##################################################
    # Contents generation from here
    print("Generating netlist with M=%d, R=%2.2fk..." % (M,R) )
    filename = '%d_%2.2fk_base.net' % (M,R)
    with open(filename,'w') as f:
        # comments for simulation setup
        print( "* M:%d, R:%2.2fk" % (M, R) , file=f )
        # rows of resisters
        count_r = 1
        for i in range(N+1):
            for j in range(N):
                print( "R%d %s %s %2.2fk" % (count_r, map_node[i,j], map_node[i,j+1], R) , file=f )
                count_r = count_r + 1
        # columns of resisters
        for i in range(N):
            for j in range(N+1): 
                print( "R%d %s %s %2.2fk" % (count_r, map_node[i,j], map_node[i+1,j], R) , file=f )
                count_r = count_r + 1
        # input
        if I:
            print( "I1 0 %s 1mA" % (map_node[int(N/2),int(N/2)]) , file=f )
        else:
            print( "V1 %s 0 5V" % (map_node[int(N/2),int(N/2)]) , file=f )
        # simulation setups
        print( ".op" , file=f)
        for i in range((N+1)*(N+1)-4):
            print( ".meas OP V_%d PARAM V(N%03d)" % ((i+1),(i+1)) , file=f )
        # finalize
        print( ".backanno" , file=f )
        print( ".end" , file=f )
        
    return filename


def generate_touched_netlist(filename, x, y, gamma):
    # Read the parameter M from the base netlist file
    with open(filename) as f:
        data_lines = f.read()
    m = re.search(r'M:([0-9]+),', data_lines)
    r = re.search(r'R:([+-]?[0-9]+[\.]?[0-9]+)k', data_lines)
    M=int(m.group(1))
    R=float(r.group(1))
    N = (7+1)*M # N+1 x N+1 lattice
    map_node = generate_map_node(M)

    int_x = int(x*(N+1))
    int_y = int(y*(N+1))

    origin_x = int_x - int((M-1)/2)
    origin_y = int_y - int((M-1)/2)
    filename_out = '%d_%2.2fk_(%1.2f,%1.2f,%1.2f).net' % (M,R,x,y,gamma)
    
    with open(filename) as f:
        data_lines = f.read()
        # rows of resisters
        for i in range(M):
            for j in range(M):
                if (origin_x + i) >= 0 and (origin_y + j) >= 0 and (origin_x + i + 1) < N+1 and (origin_y + j + 1) < N+1 :
                    data_lines = re.sub(r'R([0-9]+)\s%s\s%s\s([+-]?[0-9]+[\.]?[0-9]+)k' % (map_node[origin_x+i,origin_y+j], map_node[origin_x+i,origin_y+j+1]), 
                                        r'R\1 %s %s %2.2fk' % (map_node[origin_x+i,origin_y+j], map_node[origin_x+i,origin_y+j+1], R*gamma), 
                                        data_lines)
        # columns of resisters
        for i in range(M):
            for j in range(M):
                if (origin_x + i) >= 0 and (origin_y + j) >= 0 and (origin_x + i + 1) < N+1 and (origin_y + j + 1) < N+1:
                    data_lines = re.sub(r'R([0-9]+)\s%s\s%s\s([+-]?[0-9]+[\.]?[0-9]+)k' % (map_node[origin_x+i,origin_y+j], map_node[origin_x+i+1,origin_y+j]), 
                                        r'R\1 %s %s %2.2fk' % (map_node[origin_x+i,origin_y+j], map_node[origin_x+i+1,origin_y+j], R*gamma), 
                                        data_lines)
        with open(filename_out, 'w') as fout:
            fout.write(data_lines)

    return filename_out

def analyze_operating_points(filename):
    # Read the parameter M from the base netlist file
    with open(filename) as f:
        data_lines = f.read()
    m = re.search(r'M:([0-9]+),', data_lines)
    r = re.search(r'R:([+-]?[0-9]+[\.]?[0-9]+)k', data_lines)
    M=int(m.group(1))
    R=float(r.group(1))
    N = (7+1)*M # N+1 x N+1 lattice
    node_sink = [1, N+1, (N+1)*(N+1)-N, (N+1)*(N+1)]
    
    file_path = working_dir+path_delimiter
    print("Launching a subprocess with %s..." % (file_path+filename) )
    # Run LTspice
    subprocess.run([ltspice_exe, '-b', file_path+filename])
    print("Subprocess is closed.")
    # Read log file
    print("Reading data from %s..." % (file_path+re.sub('.net','.log',filename)) )
    results = np.zeros((N+1)*(N+1))
    with open(file_path+re.sub('.net','.log',filename)) as f:
        data_lines = f.read()
    try:
        #i=1
        j=0
        for i in range((N+1)*(N+1)):
            if (i+1) in node_sink:
                j = j + 1
                pass
            else:
                m = re.search(r'v_%d: v\(n%03d\)=([+-]?[0-9]+[\.]?[0-9]*)' % ((i+1-j), (i+1-j)), data_lines)
                # **NOTE**
                # ([+-]?[0-9]+[\.]?[0-9]+): doesnt match to "1" because it requires a number after the decimal point
                # ([+-]?[0-9]+[\.]?[0-9]*): match to "1" but does not match to .3
                results[i] = float(m.group(1))
            #print(i)
            #i = i + 1
        results = results.reshape([(N+1),(N+1)])
    except AttributeError as e:
        print('AttributeError: ', e)
    
    return results
    

#####################################
# Main
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--M", help="M edges between two input/output nodes (terminals)", default=13, type=int)
    parser.add_argument("--R", help="resistance (kOhm)", default=1.7, type=float)
    args = parser.parse_args()

    M = args.M
    R = args.R

    # generate base netlist
    netlist = generate_base_netlist(M,R)
    # compute baseline voltages
    baseline=analyze_operating_points(netlist)
    print(baseline)
    # dump to pickle file
    with open('%d_%2.2fk_baseline.pickle' % (M,R), mode="wb") as f:
        pickle.dump(baseline, f)
    