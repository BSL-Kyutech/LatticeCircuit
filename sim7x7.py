import numpy as np
import subprocess
import re
import os
import yaml


#####################################
# Global variables

# Read parameters from config.yml
with open('config.yml') as file:
    config = yaml.safe_load(file.read())
    ltspice_exe = config['ltspice']
    working_dir = config['working_dir']
    filename_net_base = config['base_netlist']
    path_delimiter = config['delimiter']

# Read the parameter M from the base netlist file
with open(working_dir+path_delimiter+filename_net_base) as f:
    data_lines = f.read()
    m = re.search(r'M:([0-9]+),', data_lines)
    r = re.search(r'R:([0-9]+),', data_lines)
    c = re.search(r'C:([0-9]+),', data_lines)
    M=int(m.group(1))
    R_init=int(r.group(1))
    C_init=int(c.group(1))
    
N = (7+1)*M # Total length of a side

# Positions of resistors
pos_R = []
for i in range(N):
    pos_R.append([(1.0/N/2.0)+(1.0/N)*i, 0])
for i in range(N):
    for j in range(N+1):
        pos_R.append([(1.0/N)*j, (1.0/N/2.0)+(1.0/N)*i])
    for j in range(N):
        pos_R.append([(1.0/N/2.0)+(1.0/N)*j, (1.0/N)+(1.0/N)*i])
pos_R = np.array(pos_R)

# Positions of capacitors
pos_C = []
for i in range(N+1):
    for j in range(N+1):
        pos_C.append([(1.0/N)*j, (1.0/N)*i])
pos_C = np.array(pos_C)


#####################################
# Functions

# initialize arrays of resistance and capacitance
def initialize_components():
    R = R_init *np.ones((N+(N+1)+1)*N) # kOhm
    C = C_init *np.ones((N+1)*(N+1)) # nF
    return R, C


# compute changes in electrical components (emulation of touch)
def compute_changes_in_components(p, f, alpha, beta, sigma, p_R=pos_R, p_C=pos_C):
    p_rep_R = np.repeat(p[None,:], (N+(N+1)+1)*N, axis=0)
    p_rep_C = np.repeat(p[None,:], (N+1)*(N+1), axis=0)
    #dR = -1.0 * f * np.exp( -1 * np.linalg.norm(p_R-p_rep_R,axis=1) / 2.0)
    #dC = 1.0 * f * np.exp( -1 * np.linalg.norm(p_C-p_rep_C,axis=1) / 2.0)
    dR = -1.0 * alpha * f * np.exp( -1 * np.power(np.linalg.norm(p_R-p_rep_R,axis=1),2) / sigma)
    dC =  1.0 * beta  * f * np.exp( -1 * np.power(np.linalg.norm(p_C-p_rep_C,axis=1),2) / sigma)
    
    return dR,dC


# generate net file based on arrays of resistance and capacitance
def generate_netlist(R, C):
    file_path = working_dir+path_delimiter+filename_net_base
    with open(file_path) as f:
        data_lines = f.read()
    for i in range(R.size):
        data_lines = re.sub(r'R%d\s([a-zA-Z0-9_]+)\s([a-zA-Z0-9_]+)\s.+(.)\s' % i, r'R%d \1 \2 %f\3\n' % (i,R[i]), data_lines)
    for i in range(C.size):
        data_lines = re.sub(r'C%d\s([a-zA-Z0-9_]+)\s([a-zA-Z0-9_]+)\s.+(.)\s' % i, r'C%d \1 \2 %f\3\n' % (i,C[i]), data_lines)
    return data_lines


# save a generated netlist data to a temporary net file
def save_netlist(netlist,filename='tmp.net'):
    file_path = working_dir+path_delimiter+filename
    with open(file_path, mode='w') as f:
        f.write(netlist)
    pass


# execute LTspice with the temporary net file
def run_ltspice(filename='tmp.net'):
    ret = []
    file_path = working_dir+path_delimiter
    print("Launching a subprocess with %s..." % (file_path+filename) )
    subprocess.run([ltspice_exe, '-b', file_path+filename])
    print("Subprocess is closed.")
    print("Reading data from %s..." % (file_path+re.sub('.net','.log',filename)) )
    with open(file_path+re.sub('.net','.log',filename)) as f:
        data_lines = f.read()
    try:
        for i in range(48):
            m = re.search(r'v\(%d\): MAX\(v\(%d\)\)=([+-]?[0-9]+[\.]?[0-9]+) FROM ([+-]?[0-9]+[\.]?[0-9]+) TO ([+-]?[0-9]+[\.]?[0-9]+)' % (i+1, i+1), data_lines)
            if not m:
                m = re.search(r'v\(%d\): v\(%d\)=([+-]?[0-9]+[\.]?[0-9]+) at ([+-]?[0-9]+[\.]?[0-9]+)' % (i+1, i+1), data_lines)
            ret.append(float(m.group(1)))
    except AttributeError as e:
        print('AttributeError: ', e)
        return None
    return np.array(ret)


# repeat LTspice simulation for each position and force that are given
def run_simulation(p_touch, f_touch, alpha=1.0, beta=1.0, sigma=10.0):
    data_in=[]
    data_out=[]
    R, C = initialize_components()
    if len(p_touch)==0:
        netlist = generate_netlist(R, C)
        save_netlist(netlist)
        while True:
            print("Running LTspice...")
            x=run_ltspice()
            if x is None:
                print("No output obtained.")
                print("Going to re-try")
            else:
                break
        data_in.append(x)
        data_out.append([])
    for p in p_touch:
        for f in f_touch:
            print("x:%1.1f, y:%1.1f, f:%1.1f" % (p[0], p[1], f))
            print("Making netlist...")
            dR, dC = compute_changes_in_components(p, f, alpha, beta, sigma)
            netlist = generate_netlist(R+dR, C+dC)
            save_netlist(netlist)
            while True:
                print("Running LTspice...")
                x=run_ltspice()
                if x is None:
                    print("No output obtained.")
                    print("Going to re-try")
                else:
                    break
            y=np.insert(p, 2, f)
            data_in.append(x)
            data_out.append(y)
    return np.array(data_in), np.array(data_out)
