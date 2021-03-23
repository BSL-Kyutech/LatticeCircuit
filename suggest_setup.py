import sys


if __name__=='__main__':
    args = sys.argv
    M = int(args[1]) # N nodes between two nearest neighbor terminals
    
    N = (7+1)*M
    center = (N+2)*(N/2)+1
    node_in = int(center)
    node_out = []
    for i in range(7):
        print( "%d-th row" % (i+1) )
        for j in range(7):
            m = (N+1)*M*(i+1)+M*(j+1)+1
            node_out.append(m)
            print(m)
    print("< Result >")
    print("Lattice size:")
    print("%d x %d lattice" % (N,N))
    print("Input node:")
    print(node_in)
    print("Output nodes:")
    print(node_out)
    print("")
    print("< Example >")
    print("python3 generate_net.py %d 1 1 > example.net" % N)
    print("python3 insert_command.py")
    
    # sato