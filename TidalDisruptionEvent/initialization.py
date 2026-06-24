import tkinter as tk
import taichi as ti
from config import *
import numpy as np
from state import *

root = tk.Tk()
root.withdraw() 
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

#Initialize Taichi
def setup_initial_condition():
    radii_np = np.ones(N+1) * 0.02
    radii_np[0] = CENTRAL_RADIUS

    colors_np = np.ones((N+1, 3))
    colors_np[0] = [1, 1, 0]
    colors_np[1:] = [125/255, 186/255, 1] 

    #Set up Initial Conditions
    masses_np = np.ones(N+1)*(m/N)
    masses_np[0] = M

    r_np = R * np.cbrt(np.random.random(N+1))
    phi_np = np.random.random(N+1) * 2 * np.pi
    theta_np = np.arccos(1 - 2 * np.random.random(N+1))

    pos_np = np.zeros((N+1, 3))
    pos_np[:, 0] = r_np * np.sin(theta_np) * np.cos(phi_np) + R_0[0]
    pos_np[:, 1] = r_np * np.sin(theta_np) * np.sin(phi_np) + R_0[1]
    pos_np[:, 2] = r_np * np.cos(theta_np) + R_0[2]
    pos_np[0] = [0, 0, 0]

    vel_np = np.zeros((N+1, 3))
    vel_np[1:] = [0, -2.162, 0]

    masses.from_numpy(masses_np.astype(np.float32))
    pos.from_numpy(pos_np.astype(np.float32))
    vel.from_numpy(vel_np.astype(np.float32))
    colors.from_numpy(colors_np.astype(np.float32))
    radii.from_numpy(radii_np.astype(np.float32))
    central_sink_is_active.from_numpy(central_sink_is_active_np.astype(np.float32))
