import numpy as np
import argparse
import os
import pickle

import rnet


def yes_no_input(M,R,X,Y,F):
    while True:
        choice = input("Do you save results to %d_%2.2fk_results_X%s_Y%s_F%s.pickle ?: "%(M,R,X,Y,F)).lower()
        if choice in ['y', 'ye', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
    
#####################################
# Main
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--M", help="M edges between two input/output nodes (terminals)", default=13, type=int)
    parser.add_argument("--R", help="resistance (kOhm)", default=1.7, type=float)
    parser.add_argument("--X", help="List of touching x-positions (range in 0.0-1.0)", default=[0.25], type=float)
    parser.add_argument("--Y", help="List of touching y-positions (range in 0.0-1.0)", default=[0.25], type=float)
    parser.add_argument("--F", help="List of touching decay rates of R (range in 0.0-1.0)", default=[0.5], type=float)
    args = parser.parse_args()

    M = args.M
    R = args.R
    X = args.X
    Y = args.Y
    F = args.F

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

    if yes_no_input(M,R,X,Y,F):
        with open('%d_%2.2fk_results_X%s_Y%s_F%s.pickle' % (M,R,X,Y,F), mode="wb") as f:
            pickle.dump(d, f)
        print('Results are dumped to %d_%2.2fk_results_X%s_Y%s_F%s.pickle' % (M,R,X,Y,F))
