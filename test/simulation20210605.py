import numpy as np
import argparse
import os
import pickle

import rnet



#####################################
# Main
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--M", help="M edges between two input/output nodes (terminals)", default=13, type=int)
    parser.add_argument("-r", "--R", help="resistance (kOhm)", default=1.7, type=float)
    parser.add_argument("-x", "--X", help="List of touching x-positions (range in 0.0-1.0)", default=[0.25], type=float, nargs='+')
    parser.add_argument("-y", "--Y", help="List of touching y-positions (range in 0.0-1.0)", default=[0.25], type=float, nargs='+')
    parser.add_argument("-f", "--F", help="List of touching decay rates of R (range in 0.0-1.0)", default=[0.5], type=float, nargs='+')
    args = parser.parse_args()

    M = 13
    R = 1.7
    theta = np.linspace(0, 2 * np.pi, 100)
    #X = np.linspace(0, 1.0, 100) * (np.sin(theta)+1.0)/2.0
    X = np.linspace(0, 1.0, 100) * (np.sin(theta)/2.0) + 0.5
    #Y = np.linspace(0, 1.0, 100) * (np.cos(theta)+1.0)/2.0
    Y = np.linspace(0, 1.0, 100) * (np.cos(theta)/2.0) + 0.5
    F = 0.5 * np.ones(100)

    # prepare the base netlist
    if not os.path.exists('./%d_%2.2fk_base.net' % (M,R)):
        netlist = rnet.generate_base_netlist(M,R)
    else:
        netlist = './%d_%2.2fk_base.net' % (M,R)

    # prepare the base netlist voltages without touching
    if not os.path.exists('%d_%2.2fk_baseline.pickle' % (M,R)):
        # compute baseline voltages
        baseline=rnet.analyze_operating_points(netlist)
        # dump to pickle file
        with open('%d_%2.2fk_baseline.pickle' % (M,R), mode="wb") as f:
            pickle.dump(baseline, f)
    else:
        with open('%d_%2.2fk_baseline.pickle' % (M,R), mode="rb") as f:
            baseline = pickle.load(f)
    
    d = {}
    for i in range(min(min(len(X),len(Y)), len(F))):
        netlist_touched = rnet.generate_touched_netlist(netlist, X[i], Y[i], F[i])
        rmat=rnet.analyze_operating_points(netlist_touched)
        d['%d'%i] = rmat-baseline
        print(d['%d'%i])

    with open('%d_%2.2fk_results_helix.pickle' % (M,R), mode="wb") as f:
        pickle.dump(d, f)
    print('Results are dumped to %d_%2.2fk_results_helix.pickle' % (M,R))
