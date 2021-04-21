import numpy as np
import argparse
import sim7x7 as sim


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--grid', help='flag for grid search', action='store_true')
    parser.add_argument("--Dp", help="divide of position", default=3, type=int)
    parser.add_argument("--Df", help="divide of force", default=3, type=int)
    parser.add_argument('-s', '--specify', help='flag for specifying a contact point and force.', action='store_true')
    parser.add_argument("--X", help="x position", default=0.5, type=float)
    parser.add_argument("--Y", help="y position", default=0.5, type=float)
    parser.add_argument("--F", help="force", default=0.5, type=float)
    
    args = parser.parse_args()
    specify_flag = args.specify
    grid_flag = args.grid
    if specify_flag:
        position = [args.X, args.Y]
        force = args.F
        # Prepare a test touching parameter (position and strength)
        p_touch = np.array([position])
        f_touch = np.array([force])
    elif grid_flag:
        divide_position = args.Dp
        divide_force = args.Df
        # Prepare test touching parameters (positions and strength)
        tmp_x, tmp_y = np.meshgrid(np.linspace(0.1,0.9,divide_position), np.linspace(0.1,0.9,divide_force))
        p_touch = np.stack([tmp_x.reshape(-1), tmp_y.reshape(-1)])
        p_touch = p_touch.T
        f_touch = np.linspace(0.1, 1.0, 2)
    else:
        print( "No valid option is specified" )
        print( "See -h for finding valid options" )
        exit(1)
    
    # Run simulation
    vols, params = sim.run_simulation(p_touch, f_touch)    

    # Show results
    print('==== Measured voltages ====')
    print(vols)
    print('==== Emulated touching ====')
    print(params)
    