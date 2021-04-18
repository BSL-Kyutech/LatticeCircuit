import numpy as np
import subprocess
import re


#####################################
# Global variables


# PATH to LTspice application and configuration files
# **NOTE** You MUST change them for your environment!!
file_exe = '/mnt/c/Program Files/LTC/LTspiceXVII/XVIIx64.exe'
path_current =  '/mnt/c/Users/shuhe/Repositories/LatticeCircuit'
filename_net_base = 'base.net'

# Size of circuit
#with open(path_current+str('/')+filename_net_base) as f:
#        data_lines = f.read()
#    for i in range(R.size):
#        data_lines = re.sub('R%d\s([a-zA-Z0-9_]+)\s([a-zA-Z0-9_]+)\s.+(.)\s' % i, 'R%d \\1 \\2 %f\\3\n' % (i,R[i]), data_lines)
#    for i in range(C.size):
#        data_lines = re.sub('C%d\s([a-zA-Z0-9_]+)\s([a-zA-Z0-9_]+)\s.+(.)\s' % i, 'C%d \\1 \\2 %f\\3\n' % (i,C[i]), data_lines)
#    return data_lines

M = 3 # M edges between two input/output nodes (terminals)

# the parameter M should be taken from the netlist file
# NEED TO BE UPDATED!!!

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
# Functions for simulation


# initialize arrays of resistance and capacitance
def initialize_components():
    R = 1 *np.ones((N+(N+1)+1)*N) # kOhm
    C = 1 *np.ones((N+1)*(N+1)) # nF
    return R, C


# compute changes in electrical components (emulation of touch)
def compute_changes_in_components(p, f, p_R=pos_R, p_C=pos_C):
    p_rep_R = np.repeat(p[None,:], (N+(N+1)+1)*N, axis=0)
    p_rep_C = np.repeat(p[None,:], (N+1)*(N+1), axis=0)
    dR = -1.0 * f * np.exp( -1 * np.linalg.norm(p_R-p_rep_R,axis=1) / 2.0)
    dC = 1.0 * f * np.exp( -1 * np.linalg.norm(p_C-p_rep_C,axis=1) / 2.0)
    return dR,dC


# generate net file based on arrays of resistance and capacitance
def generate_netlist(R, C):
    with open(path_current+str('/')+filename_net_base) as f:
        data_lines = f.read()
    for i in range(R.size):
        data_lines = re.sub(r'R%d\s([a-zA-Z0-9_]+)\s([a-zA-Z0-9_]+)\s.+(.)\s' % i, r'R%d \1 \2 %f\3\n' % (i,R[i]), data_lines)
    for i in range(C.size):
        data_lines = re.sub(r'C%d\s([a-zA-Z0-9_]+)\s([a-zA-Z0-9_]+)\s.+(.)\s' % i, r'C%d \1 \2 %f\3\n' % (i,C[i]), data_lines)
    return data_lines


# save a generated netlist data to a temporary net file
def save_netlist(netlist,filename='tmp.net'):
    with open(path_current+str('/')+filename, mode='w') as f:
        f.write(netlist)
    pass


# execute LTspice with the temporary net file
def run_ltspice(filename='tmp.net'):
    ret = []
    subprocess.run([file_exe, '-b', path_current+str('/')+filename])
    with open(path_current+str('/')+re.sub('.net','.log',filename)) as f:
        data_lines = f.read()
    try:
        m = re.search(r'v\(1\)=\(([+-]?[0-9]+[\.]?[0-9]+).+,([+-]?[0-9]+[\.]?[0-9]+).+\)',data_lines)
        ret.append(float(m.group(1)))
        ret.append(float(m.group(2)))
        m = re.search(r'v\(2\)=\(([+-]?[0-9]+[\.]?[0-9]+).+,([+-]?[0-9]+[\.]?[0-9]+).+\)',data_lines)
        ret.append(float(m.group(1)))
        ret.append(float(m.group(2)))
    except AttributeError as e:
        print('catch AttributeError:', e)
        return None
    return np.array(ret)


# repeat LTspice simulation for each position and force that are given
def run_simulation(p_touch, f_touch):
    data_in=[]
    data_out=[]
    R, C = initialize_components()
    for p in p_touch:
        for f in f_touch:
            print("x:%1.1f, y:%1.1f, f:%1.1f" % (p[0], p[1], f))
            print("Making netlist...")
            dR, dC = compute_changes_in_components(p,f)
            netlist = generate_netlist(R+dR, C+dC)
            save_netlist(netlist)
            print("done.")
            while True:
                print("Running LTspice...")
                x=run_ltspice()
                print("done.")
                if x is None:
                    print("No output obtained.")
                    print("Going to re-try")
                else:
                    break
            y=np.insert(p, 2, f)
            data_in.append(x)
            data_out.append(y)
    return np.array(data_in), np.array(data_out)
