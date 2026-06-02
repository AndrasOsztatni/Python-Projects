# initialization.py
import numpy as np
from config import *
import state

def setup_initial_conditions():
    
    state.is_active.fill(1)
    state.sink_active[None] = 0  

    masses_np = np.ones(N) * (M / N)

    r_np = R * np.cbrt(np.random.random(N))
    phi_np = np.random.random(N) * 2 * np.pi
    theta_np = np.arccos(1 - 2 * np.random.random(N))

    pos_np = np.zeros((N, 3))
    pos_np[:, 0] = r_np * np.sin(theta_np) * np.cos(phi_np)
    pos_np[:, 1] = r_np * np.sin(theta_np) * np.sin(phi_np)
    pos_np[:, 2] = r_np * np.cos(theta_np)

    vel_np = np.zeros((N, 3))
    vel_np[:, 2] = 0.0

    # Base rotation
    vel_np[:, 0] = -OMEGA * pos_np[:, 1]
    vel_np[:, 1] =  OMEGA * pos_np[:, 0]

    # Inject Turbulence
    TURBULENCE_STRENGTH = 0.5
    vel_np += np.random.normal(0, TURBULENCE_STRENGTH, (N, 3))

    # Transfer from CPU (NumPy) to GPU (Taichi)
    state.masses.from_numpy(masses_np.astype(np.float32))
    state.pos.from_numpy(pos_np.astype(np.float32))
    state.vel.from_numpy(vel_np.astype(np.float32))