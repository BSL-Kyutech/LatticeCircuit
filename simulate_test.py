import sim7x7 as sim
import numpy as np


if __name__=='__main__':
    # Prepare test touching parameters (positions and strength)
    tmp_x, tmp_y = np.meshgrid(np.linspace(0.1,0.9,1), np.linspace(0.1,0.9,1))
    p_touch = np.stack([tmp_x.reshape(-1), tmp_y.reshape(-1)])
    p_touch = p_touch.T
    f_touch = np.linspace(0.1, 1.0, 10)
    
    # Run simulation
    data_in, data_out = sim.run_simulation(p_touch, f_touch)

    # Show data
    print('==== Contents in data_in ====')
    print(data_in)
    print('==== Contents in data_out ====')
    print(data_out)
