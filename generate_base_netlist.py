import numpy as np
import re
import argparse
import sys


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("M", help="M edges between two input/output nodes (terminals)", type=int)
    parser.add_argument("--R", help="resistance (kOhm)", default=10, type=int)
    parser.add_argument("--pulldown", help="resistance (kOhm)", default=10000, type=int)
    parser.add_argument("--C", help="capacitance (nF)", default=1, type=int)
    parser.add_argument("--V", help="input voltage (V)", default=1, type=int)
    parser.add_argument("--F", help="input frequency (Hz)", default=False, type=int)
    parser.add_argument("--D", help="simulation duration (msec)", default=100, type=int)
    parser.add_argument('-s', '--sine', help='select SINE for the input', action='store_true')
    parser.add_argument('-p', '--pulse', help='select PULSE for the input', action='store_true')
    parser.add_argument('-g', '--ground', help='set nodes on outer edges as GND', action='store_true')
    args = parser.parse_args()

    M = args.M
    R = args.R
    C = args.C
    V = args.V
    F = args.F
    D = args.D
    pulldown = args.pulldown
    Ds = int(D*0.8)
    sine_flag = args.sine
    pulse_flag = args.pulse
    gnd_flag = args.ground

    N = (7+1)*M # N+1 x N+1 lattice

    center = (N+2)*(N/2)+1
    node_in = int(center)
    node_out = []
    node_edge = []
    for i in range(7):
        for j in range(7):
            m = (N+1)*M*(i+1)+M*(j+1)+1
            node_out.append(m)
    node_out.remove(node_in)
    for i in range(N+1):
        if (i+1) == 1:
            for j in range(N+1):
                node_edge.append(j+1)
        elif (i+1) == N+1:
            for j in range(N+1):
                node_edge.append((i*(N+1))+j+1)
        else:
            node_edge.append((i*(N+1))+1)
            node_edge.append((i*(N+1))+N+1)
    
    # make a map of all nodes
    map_node = np.arange((N+1)*(N+1))
    map_node = map_node + 1

    # translate to node labels
    map_node = ["N%03d" % node for node in map_node]
    # place output terminals. if -g was given, place edge GND terminals as well.
    for i in range(len(node_out)):
        map_node = ["%d"%(i+1) if node==("N%03d" % node_out[i]) else node for node in map_node]
    if gnd_flag:
        for i in range(len(node_edge)):
            map_node = ["0" if node==("N%03d" % node_edge[i]) else node for node in map_node]
    # make a list of replaced nodes
    node_replaced = node_out
    if gnd_flag:
        node_replaced.extend(node_edge)
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
    
    ##################################################
    # Contents generation from here

    # comments for simulation setup
    print( "* M:%d, R:%d, C:%d, V:%d, F:%d, D:%d" % (M,R,C,V,F,D) )

    # rows of resisters
    count_r = 1
    for i in range(N+1):
        for j in range(N):
            if map_node[i,j] == "0" and map_node[i,j+1] == "0":
                pass
            else:
                print( "R%d %s %s %dk" % (count_r, map_node[i,j], map_node[i,j+1], R) )
                count_r = count_r + 1
    # columns of resisters
    for i in range(N):
        for j in range(N+1): 
            if map_node[i,j] == "0" and map_node[i+1,j] == "0":
                pass
            else:
                print( "R%d %s %s %dk" % (count_r, map_node[i,j], map_node[i+1,j], R) )
                count_r = count_r + 1
    # pulldown resisters for output terminals
    if pulldown < 10000:
        for i in range(7*7-1):
            print( "R%d %s %s %dk" % (count_r, i+1, 0, pulldown) )
            count_r = count_r + 1
    # capacitors
    if C > 0:
        count_c = 1
        for i in range(N+1):
            for j in range(N+1):
                if map_node[i,j] == "0":
                    pass
                else:
                    print( "C%d %s 0 %dn" % (count_c, map_node[i,j], C) )
                    count_c = count_c + 1
    # input
    if F:
        if sine_flag:
            print( "V1 N%03d 0 SINE(0 %d %d)" % (node_in, V, F) )
        elif pulse_flag:
            period = 1.0/F*1000.0
            print( "V1 N%03d 0 PULSE(0 %d 0 0.0001m 0.0001m %fm %fm)" % (node_in, V, period/2.0, period) )
        else:
            print( "netlist generation is aborted!!", file=sys.stderr )
            print( "Select -s or -p to specify a type of power profiles!!", file=sys.stderr )
            exit(1)
    else:
        print( "V1 N%03d 0 PULSE(0 %d 0 0.0001m 0.0001m %dm %dm)" % (node_in, V, D, D*2) )

    # simulation setups
    #print( ".ac oct 1 10k 10k" )
    print( ".tran %dm" % D )
    for i in range(len(node_out)):
        #print( ".meas AC V(%d) FIND V(%d) AT 10k" % (i+1, i+1) )
        if F and pulse_flag:
            print( ".meas TRAN V(%d) FIND V(%d) WHEN V(N%03d)=%d cross=%d" % (i+1, i+1, node_in, int(V/2.0), 2*int(D/period)) )
        else:
            print( ".meas TRAN V(%d) MAX V(%d) FROM %dm TO %dm" % (i+1, i+1, Ds, D) )
    print( ".backanno" )
    print( ".end" )
