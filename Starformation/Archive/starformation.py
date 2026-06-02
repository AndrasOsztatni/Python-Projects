import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#Constants (G = gravittational constant, M = mass of cloud, N = number of particles in cloud, R = radius of cloud)
G = 1
M = 3
N = 100
R = 1

#Simulation Parameters
TIME_STEP = 0.005
SOFT_PARAM = 0.1
MAX_TIME = 2
OMEGA = 2
h = 0.5
SPEED_OF_SOUND = 0.5
#Generating Uniform Distribution of Particles

masses = np.ones(N)*(M/N)

r = R * np.cbrt(np.random.random(N))
phi = np.random.random(N)*2*np.pi
theta = np.arccos(1 - 2*np.random.random(N))

#Convert Spherical Coordinates to Cartesion

pos=np.zeros((3, N))
pos[0] = r * np.sin(theta) * np.cos(phi)
pos[1] = r * np.sin(theta) * np.sin(phi)
pos[2] = r * np.cos(theta)

#Initial Rotation of the Cloud

vel = np.zeros((3, N))
vel[0] = - OMEGA * pos[1] # vx=-omega * y
vel[1] = OMEGA * pos[0] # vy = omega * x
vel[2] = 0 #vz = 0

def acceleration(positions, masses, G, soft_param):
    N = positions.shape[1]
    acc = np.zeros((3, N))

    for i in range(N):
        dx = positions[0, :] - positions[0, i]
        dy = positions[1, :] - positions[1, i]
        dz = positions[2, :] - positions[2, i]

        inv_r3 = (dx**2 + dy**2 + dz**2 + soft_param**2)**(-1.5)

        acc[0, i] = G * np.sum(masses * dx * inv_r3)
        acc[1, i] = G * np.sum(masses * dy * inv_r3)
        acc[2, i] = G * np.sum(masses * dz * inv_r3)
    return acc


#Density at one point with Smoothed Gaussian Kernel

def gaussian_kernel_3D(dx, dy, dz, h):
    
    normalization = 1 / (h * np.sqrt(np.pi) )**3
    r2 = dx**2 + dy**2 + dz**2
    W = normalization * np.exp(-r2/(h**2))

    grad_factor = -2*r / (h**2) * W
    dW_dx = grad_factor * dx
    dW_dy = grad_factor * dy
    dW_dz = grad_factor * dz

    return W, dW_dx, dW_dy, dW_dz

def get_density_and_pressure(positions, masses, h, soundspeed):
    N = positions.shape[1]
    rho = np.zeros(N)
    
    for i in range(N):
        dx = positions[0, :] - positions[0, i]
        dy = positions[1, :] - positions[1, i]
        dz = positions[2, :] - positions[2, i]

        W, _, _, _ = gaussian_kernel_3D(dx, dy, dz, h)

        rho[i] = np.sum(masses * W)
    
    pressure = soundspeed ** 2 * rho
    return rho, pressure

def get_pressure_acceleration(positions, masses, rho, pressure, h):

    N = positions.shape[1]
    acc_press = np.zeros((3, N))
    
    for i in range(N):
        
        dx = positions[0, :] - positions[0, i]
        dy = positions[1, :] - positions[1, i]
        dz = positions[2, :] - positions[2, i]
        
        _, dW_dx, dW_dy, dW_dz = gaussian_kernel_3D(dx, dy, dz, h)
        
    
        pressure_term = (pressure[i] / rho[i]**2) + (pressure / rho**2)

        acc_press[0, i] = -np.sum(masses * pressure_term * dW_dx)
        acc_press[1, i] = -np.sum(masses * pressure_term * dW_dy)
        acc_press[2, i] = -np.sum(masses * pressure_term * dW_dz)
        
    return acc_press

def get_total_acceleration(positions, masses, h, G, soft_param, sound_speed):
    #Gravity
    acc_gravity = acceleration(positions, masses, G, soft_param)

    #Density and Pressure
    rho, pressure = get_density_and_pressure(positions, masses, h, sound_speed)

    #Pressure acceleration
    acc_pressure = get_pressure_acceleration(positions, masses, rho, pressure, h)
    return acc_gravity + acc_pressure

# Initial acceleration before starting
acc = acceleration(pos, masses, G, SOFT_PARAM)
t = 0.0

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

def update(frame):
    global pos, vel, acc, t # We need to update these global variables
    
    # We run 10 physics steps per visual frame. 
    # If we animated every single step, the animation would be painfully slow!
    for _ in range(10):
        # Kick 1
        vel += acc * (TIME_STEP/2)
        # Drift
        pos += vel * TIME_STEP
        # Update Acceleration
        acc = get_total_acceleration(pos, masses, h, G, SOFT_PARAM, SPEED_OF_SOUND)
        # Kick 2
        vel += acc * (TIME_STEP/2)
        
        # Advance time
        t += TIME_STEP

    # --- Draw the Frame ---
    ax.clear() 
    ax.set_xlim(-2*R, 2*R)
    ax.set_ylim(-2*R, 2*R)
    ax.set_zlim(-2*R, 2*R)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'Time: {t:.2f}')
    
    # Scatter the new positions
    ax.scatter(pos[0], pos[1], pos[2], s=10, c='blue', alpha=0.5)

print("Rendering Animation...")

# Create the animation object
# frames=200 means it will run update() 200 times. 
# interval=50 means 50 milliseconds between frames (20 fps).
ani = animation.FuncAnimation(fig, update, frames=200, interval=50, blit=False)

plt.show()

