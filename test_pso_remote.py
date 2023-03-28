import numpy as np
import time
import sys

IP_SERVER_ADD = sys.argv[1]

# Para hacer el muestreo por Latin Hypecube
from scipy.stats.qmc import LatinHypercube,scale

from request_server.request_server import send_request_py

# Tamaño de la población
n = 1

# Número de variables
n_var = 2

engine = LatinHypercube(d=2)
sample = engine.random(n=n)

l_bounds = np.array([-5,-5])
u_bounds = np.array([5,5])

sample_scaled = scale(sample,l_bounds, u_bounds)

# Definimos la clase Particle
class Particle:
    def __init__(self,x,v):
        self.x = x
        self.v = v
        self.x_best = x

particula = Particle(sample_scaled[0], np.array([0]*n_var))


# Cognitive scaling parameter
α = 0.8
# Social scaling parameter
β = 0.8

# velocity inertia
w = 0.5
# minimum value for the velocity inertia
w_min = 0.4
# maximum value for the velocity inertia
w_max = 0.9

# Velocidad máxima
vMax = np.multiply(u_bounds-l_bounds,0.2)
# Velocidad mínima
vMin = -vMax

# Función Himmelblau
def himmelblau(X):
    x,y = X
    return (x**2 + y -11)**2 + (x + y**2 -7)**2

value_f = himmelblau(particula.x)

best_global_vector = send_request_py(IP_SERVER_ADD, value_f, particula.x)

maxiter = 60


for k in range(maxiter):
    #print(k)
    time.sleep(1)
    # Actualiza velocidad de la partícula
    ϵ1,ϵ2 = np.random.uniform(), np.random.uniform()
    particula.v = w*particula.v + α*ϵ1*(particula.x_best - particula.x) + β*ϵ2*(best_global_vector - particula.x)

    # Ajusta velocidad de la partícula
    index_vMax = np.where(particula.v > vMax)
    index_vMin = np.where(particula.v < vMin)

    if np.array(index_vMax).size > 0:
        particula.v[index_vMax] = vMax[index_vMax]
    if np.array(index_vMin).size > 0:
        particula.v[index_vMin] = vMin[index_vMin]

    # Actualiza posición de la partícula
    particula.x += particula.v

    # Ajusta posición de la particula
    index_pMax = np.where(particula.x > u_bounds)
    index_pMin = np.where(particula.x < l_bounds)

    if np.array(index_pMax).size > 0:
        particula.x[index_pMax] = u_bounds[index_pMax]
    if np.array(index_pMin).size > 0:
        particula.x[index_pMin] = l_bounds[index_pMin]

    # Evaluamos la función
    y = himmelblau(particula.x)

    best_global_vector = send_request_py(IP_SERVER_ADD, y, particula.x)

    if not all(np.array(best_global_vector)==particula.x):
        if y < himmelblau(particula.x_best):
            P.x_best = np.copy(particula.x)

    # Actualizamos w

    w = w_max - k * ((w_max-w_min)/maxiter)
