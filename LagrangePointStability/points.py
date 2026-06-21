import numpy as np
import matplotlib.pyplot as plt

# Constants
M_SUN = 10000.0
M_EARTH = 300.0 # Increased slightly relative to Sun so its gravity well is visible
D = 1000.0
IPS = np.array([0.0, 0.0])
IPE = np.array([D, 0.0])
G = 1.0

def effective_potential(x, y):
    # True 2D scalar distances
    rs = np.sqrt((x - IPS[0])**2 + (y - IPS[1])**2)
    re = np.sqrt((x - IPE[0])**2 + (y - IPE[1])**2)
    
    # Prevent strict division by zero at the exact center of the masses
    rs = np.where(rs == 0, 1e-10, rs)
    re = np.where(re == 0, 1e-10, re)
    
    # Calculate Center of Mass (Barycenter) for the rotating frame
    x_cm = (M_SUN * IPS[0] + M_EARTH * IPE[0]) / (M_SUN + M_EARTH)
    y_cm = 0.0
    r_cm = np.sqrt((x - x_cm)**2 + (y - y_cm)**2)
    
    # Kepler's Third Law dictates the correct angular velocity
    omega = np.sqrt(G * (M_SUN + M_EARTH) / D**3)
    
    # Scalar potentials: V = -GM/r
    v_sun = -G * M_SUN / rs
    v_earth = -G * M_EARTH / re
    
    # Centrifugal potential: Vc = -0.5 * w^2 * r^2
    v_centrifugal = -0.5 * omega**2 * r_cm**2
    
    # Effective potential is the simple scalar sum
    return v_sun + v_earth + v_centrifugal

# Adjusted grid bounds to focus on the area around and between the two bodies
y, x = np.meshgrid(np.linspace(-500, 1500, 1000), np.linspace(-500, 1500, 1000))

z = effective_potential(x, y)

# Determine color limits using percentiles to ignore the infinite negative spikes 
# at the center of the stars, ensuring the Lagrange saddle points are visible.
z_min, z_max = np.percentile(z, 5), np.percentile(z, 95)
z_clipped = np.clip(z, a_min=z_min, a_max=z_max)

fig, ax = plt.subplots(figsize=(10, 8))

# Contourf is the standard for potential fields as it maps equipotential lines natively
levels = np.linspace(z_min, z_max, 60)
c = ax.contourf(x, y, z_clipped, levels=levels, cmap="viridis")
ax.set_title("Effective Gravitational Potential (Rotating Frame)")

# Mark the bodies
ax.plot(IPS[0], IPS[1], 'ro', label="Sun")
ax.plot(IPE[0], IPE[1], 'bo', label="Earth")
ax.legend()

ax.axis([x.min(), x.max(), y.min(), y.max()])
ax.set_aspect('equal')

fig.colorbar(c, ax=ax, label="Potential Energy")
plt.show()