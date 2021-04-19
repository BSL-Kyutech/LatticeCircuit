import argparse
import numpy as np
import re


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("M", help="M edges between two input/output nodes (terminals)", type=int)
    parser.add_argument("--R", help="resistance (kOhm)", default=1, type=int)
    parser.add_argument("--C", help="capacitance (nF)", default=1, type=int)
    parser.add_argument("--V", help="input voltage (V)", default=1, type=int)
    parser.add_argument("--F", help="input frequency (Hz)", default=1000, type=int)
    args = parser.parse_args()

    M = args.M
    R = args.R
    C = args.C
    V = args.V
    F = args.F

    N = (7+1)*M # N x N lattice

    center = (N+2)*(N/2)+1
    node_in = int(center)
    node_out = []
    for i in range(7):
        for j in range(7):
            m = (N+1)*M*(i+1)+M*(j+1)+1
            node_out.append(m)
    node_out.remove(node_in)

    map_node = np.arange((N+1)*(N+1))
    map_node = map_node + 1
    # translate to node labels and place output terminals
    map_node = ["N%03d" % node for node in map_node]
    for i in range(len(node_out)):
        map_node = ["%d"%(i+1) if node==("N%03d" % node_out[i]) else node for node in map_node]
        map_node = ["N%03d" % (int(re.sub(r'\D', '', node))-1) if int(re.sub(r'\D', '', node)) > node_out[i] else node for node in map_node]
    # reshape the list to a square matrix
    map_node = np.array(map_node)
    map_node = map_node.reshape([(N+1),(N+1)])
    
    ##################################################
    # Contents generation from here

    # rows of resisters
    count_r = 1
    for i in range(N+1):
        for j in range(N):
            print( "R%d %s %s %dk" % (count_r, map_node[i,j], map_node[i,j+1], R) )
            count_r = count_r + 1
    # columns of resisters
    for i in range(N):
        for j in range(N+1):
            print( "R%d %s %s %dk" % (count_r, map_node[i,j], map_node[i+1,j], R) )
            count_r = count_r + 1
    # capacitors
    count_c = 1
    for i in range(N+1):
        for j in range(N+1):
            print( "C%d %s 0 %dn" % (count_c, map_node[i,j], C) )
            count_c = count_c + 1
    
    # input
    #print( "V1 N%03d 0 AC %dV" % (node_in, V) )
    print( "V1 N%03d 0 SINE(0 %d %d)" % (node_in, V, F) )

    # simulation setups
    #print( ".ac oct 1 10k 10k" )
    print( ".tran 10m" )
    for i in range(len(node_out)):
        #print( ".meas AC V(%d) FIND V(%d) AT 10k" % (i+1, i+1) )
        print( ".meas TRAN V(%d) MAX V(%d) FROM 5m TO 10m" % (i+1, i+1) )
    print( ".backanno" )
    print( ".end" )
