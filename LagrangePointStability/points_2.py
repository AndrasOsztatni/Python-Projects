import numpy as np
from scipy.optimize import root

# Constants
M_SUN = 10000.0
M_EARTH = 300.0 
D = 1000.0
G = 1.0

# Define Barycenter and Positions
x_cm = (M_EARTH * D) / (M_SUN + M_EARTH) # Sun is at x=0, Earth at x=D
IPS = np.array([0.0, 0.0])
IPE = np.array([D, 0.0])

# Kepler's Third Law
omega = np.sqrt(G * (M_SUN + M_EARTH) / D**3)

def net_acceleration(vars):
    x, y = vars
    
    # Distances cubed
    r1_3 = ((x - IPS[0])**2 + (y - IPS[1])**2)**1.5
    r2_3 = ((x - IPE[0])**2 + (y - IPE[1])**2)**1.5
    
    # Prevent division by zero mathematically
    if r1_3 == 0 or r2_3 == 0:
        return [np.inf, np.inf]

    # Gravity components
    gx = -G * M_SUN * (x - IPS[0]) / r1_3 - G * M_EARTH * (x - IPE[0]) / r2_3
    gy = -G * M_SUN * (y - IPS[1]) / r1_3 - G * M_EARTH * (y - IPE[1]) / r2_3
    
    # Centrifugal components (relative to barycenter)
    cx = omega**2 * (x - x_cm)
    cy = omega**2 * y
    
    return [gx + cx, gy + cy]

# Initial guesses for L1, L2, L3 (Collinear) and L4, L5 (Equilateral)
guesses = {
    "L1": [D * 0.9, 0],   # Between Sun and Earth
    "L2": [D * 1.1, 0],   # Behind Earth
    "L3": [-D * 1.0, 0],  # Behind Sun
    "L4": [D / 2, D * 0.866],  # 60 degrees ahead
    "L5": [D / 2, -D * 0.866]  # 60 degrees behind
}

# Solve for exact coordinates
print("Exact Lagrange Point Coordinates:")
print("-" * 35)
for name, guess in guesses.items():
    sol = root(net_acceleration, guess)
    if sol.success:
        print(f"{name}: x = {sol.x[0]:.4f}, y = {sol.x[1]:.4f}")
    else:
        print(f"Failed to converge for {name}")