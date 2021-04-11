import argparse


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("M", help="M edges between two input/output nodes (terminals)", type=int)
    args = parser.parse_args()
    M = args.M
    
    N = (7+1)*M
    center = (N+2)*(N/2)+1
    node_in = int(center)
    node_out = []
    for i in range(7):
        print( "%d-th row of terminals" % (i+1) )
        for j in range(7):
            m = (N+1)*M*(i+1)+M*(j+1)+1
            node_out.append(m)
            print(m)
    node_out.remove(node_in)
    print("< Result >")
    print("Lattice size:")
    print("%d x %d lattice" % (N,N))
    print("%d nodes in total" % ((N+1)*(N+1)))
    print("Input node:")
    print(node_in)
    print("Output nodes:")
    print(node_out)
    print("")
    print("< Example >")
    print("You can generate the suggested grid RC circuit using 1kOhm resistance, 1nF capacitance, and 1V input as follows:")
    print("")
    print("python3 generate_net.py %d > example.net" % M)
    print("")
    print("For the detail, check the help \"python3 generate_net.py -h\"")
    