import numpy as np
import matplotlib.pyplot as plt
import time 

import sys

from request_server.request_server import send_request_py

####
MY_IP = sys.argv[1]  
MY_PORT = sys.argv[2]
#MY_IP = '127.0.0.1'
#MY_PORT = '8888'
MY_IP_PORT = f"{MY_IP}:{MY_PORT}"

### 
IP_POOL = ["127.0.0.1"]
PORT_POOL = [f"{8888+i}" for i in range(10)]
PORT_POOL.remove(MY_PORT)

IP_PORT_POOL = [f"{ip}:{port}" for ip in IP_POOL for port in PORT_POOL]

# 1 - Define the upper and lower bounds of the search space
n_dim = 2               # Number of dimensions of the problem

lb = np.array([-5, -5])  # lower bound for the search space
ub = np.array([5, 5])  # upper bound for the search space

# 2 - Define the parameters for the optimization
max_iters = 100  # maximum number of iterations

# 3 - Parameters for the algorithm
pc = 0.9 # crossover probability
pop_size = 1   # number of individuals in the population

# 4.- Cost Function (Función Himmelblau)
def himmelblau(X):
    x,y = X
    return (x**2 + y -11)**2 + (x + y**2 -7)**2

step_size = 0.4

# problem dimension
n_dim = np.shape(lb)[0]

# randomly initialize xi
xi = (ub - lb) * np.random.random_sample(size = n_dim) + lb

# send xi to the server
send_request_py(MY_IP_PORT, 1, xi)

# obtain the cost of the solution
xi_cost = himmelblau(xi)

time.sleep(5)

file = open(f"ind_{MY_IP}_{MY_PORT}.txt", "w")

# optimization
for id_iter in range(max_iters):
    print("-----------------------------")
    print("-%%%%%%%%%%%%%%%%%%%%%%%%%%%-")
    print("        Iteración {}\nIP PORT {}\nBest Value {}".format(id_iter, MY_IP_PORT, xi_cost))
    print("-%%%%%%%%%%%%%%%%%%%%%%%%%%%-")
    print("-----------------------------")

    # randomly pick 3 candidate solution 
    xa_ip_port , xb_ip_port , xc_ip_port = np.random.choice(IP_PORT_POOL, 3) 
    
    V1 = np.array(send_request_py(xa_ip_port, 0, []))
    V2 = np.array(send_request_py(xb_ip_port, 0, []))
    Vb = np.array(send_request_py(xc_ip_port, 0, []))

    # create the difference vector
    Vd = V1 - V2
    # create the mutant vector
    Vm = Vb + step_size*Vd
    # make sure the mutant vector is in [lb,ub]
    Vm = np.clip(Vm,lb,ub)
    # create a trial vector by recombination
    Vt = np.zeros(n_dim)
    jr = np.random.rand()   # index of the dimension
                            # that will under crossover
                            # regardless of pc
    for id_dim in range(n_dim):
        rc = np.random.rand()
        if rc < pc or id_dim == jr:
            # perform recombination
            Vt[id_dim] = Vm[id_dim]
        else:
            # copy from Vb
            Vt[id_dim] = xi[id_dim]
    # obtain the cost of the trial vector
    vt_cost = himmelblau(Vt)
    # select the individual for the next generation
    if vt_cost < xi_cost:
        xi = np.copy(Vt)
        xi_cost = vt_cost

        # send xi to the server
        send_request_py(MY_IP_PORT, 1, xi)

    file.write(f"{id_iter},{xi_cost}\n")

file.close()
