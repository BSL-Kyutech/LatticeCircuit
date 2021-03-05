import sys
import numpy as np

if __name__=='__main__':
    args = sys.argv
    M = int(args[1]) # M nodes between two nearest neighbor terminals
    R = int(args[2]) # resistance (kOhm)
    C = int(args[3]) # capacitance (nF)

    N = (7+1)*M # N x N lattice

    center = (N+2)*(N/2)+1
    node_in = int(center)
    node_out = []
    for i in range(7):
        for j in range(7):
            m = (N+1)*M*(i+1)+M*(j+1)+1
            node_out.append(m)

    map_node = np.arange((N+1)*(N+1))
    map_node = map_node + 1
    map_node = map_node.reshape([(N+1),(N+1)])

    # rows of resisters
#    count_r = 1
#    count_terminal = 0
#    for i in range(N+1):
#        for j in range(N):
#            print( "R%d N%d N%d %dk" % (count_r, i*N+(j+i+1), i*N+(j+i+1)+1, R) )
#            count_r = count_r + 1
    # columns of resisters
#    for i in range(N+1):
#        for j in range(N):
#            print( "R%d N%d N%d %dk" % (count_r, j*N+(j+i+1), j*N+(j+i+1)+1+N, R) )
#            count_r = count_r + 1
#    # capacitors
#    count_r = 1
#    for i in range((N+1)*(N+1)):
#        print( "C%d N%d 0 %dn" % (count_r, i+1, C) )
#        count_r = count_r + 1
    