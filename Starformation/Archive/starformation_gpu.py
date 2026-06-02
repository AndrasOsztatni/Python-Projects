import taichi as ti
import numpy as np
import math

G = 1.0                     #Gravitational Constant
M = 2.0                     #Total Mass
N = 4000                    # Particle count 
R = 1.0                     #Radius of Sphere inwhich Particles are generated at the beginning
OMEGA = 1.0                 #Initial angular velocity 


TIME_STEP = 0.005   
SOFT_PARAM = 0.1            #Softhening Parameter to avoid ininities by inverse square laws
SMOOTHING_LENGTH = 0.5      #SPH Smoothening Length
SOUND_SPEED = 0.5           #Speed of Sound

# Viscosity Parameters
ALPHA = 0.25                
BETA = 0.5                  
EPSILON = 0.01              
MIN_DENSITY = 0.05          

# Energy Conservation Parameters
GAMMA = 5.0 / 3.0            
RHO_CRIT = 3.0     

# Sink Particle Parameters
SINK_CREATION_DENSITY = 8.0  
SINK_ACCRETION_RADIUS = 0.15  

SPH_CUTOFF = 3.0 * SMOOTHING_LENGTH
SPH_CUTOFF_SQR = SPH_CUTOFF**2

#Turbulance for randomness at the beginning
TURBULENCE_STRENGTH = 0.5

# INITIALIZE TAICHI

ti.init(arch=ti.cuda)

# TAICHI DATA STRUCTURES

ti.init(arch=ti.cuda)
pos = ti.Vector.field(3, dtype=ti.f32, shape=N)
vel = ti.Vector.field(3, dtype=ti.f32, shape=N)
acc = ti.Vector.field(3, dtype=ti.f32, shape=N)

masses = ti.field(dtype=ti.f32, shape=N)
rho = ti.field(dtype=ti.f32, shape=N)
pressure = ti.field(dtype=ti.f32, shape=N)

is_active = ti.field(dtype=ti.i32, shape=N)

sink_active = ti.field(dtype=ti.i32, shape=())
sink_mass = ti.field(dtype=ti.f32, shape=())
sink_pos = ti.Vector.field(3, dtype=ti.f32, shape=())
sink_vel = ti.Vector.field(3, dtype=ti.f32, shape=())

# A tiny array just for rendering the sink particle in the UI
render_sink_pos = ti.Vector.field(3, dtype=ti.f32, shape=1)

# INITIALIZATION

is_active.fill(1)
sink_active[None] = 0  

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

# 1. Base rotation (so the cloud still generally spins)
vel_np[:, 0] = -OMEGA * pos_np[:, 1]
vel_np[:, 1] =  OMEGA * pos_np[:, 0]

# 2. Add random 3D turbulence to every particle
vel_np += np.random.normal(0, TURBULENCE_STRENGTH, (N, 3))

masses.from_numpy(masses_np.astype(np.float32))
pos.from_numpy(pos_np.astype(np.float32))
vel.from_numpy(vel_np.astype(np.float32))

# ==========================================
# 5. PHYSICS ENGINES (GPU Kernels)
# ==========================================
@ti.func
def gaussian_kernel_and_gradient_3D(r_vec, h):
    r2 = r_vec.norm_sqr()
    normalization = 1.0 / ((h * math.sqrt(math.pi))**3)
    W = normalization * ti.exp(-r2 / (h**2))
    
    grad_factor = (-2.0 / (h**2)) * W
    grad_W = grad_factor * r_vec
    return W, grad_W

@ti.kernel
def compute_density_and_pressure():
    for i in range(N):
        if is_active[i] == 1:    
            rho_i = 0.0
            for j in range(N):
                # FIX: Only interact with ALIVE gas!
                if is_active[j] == 1: 
                    r_vec = pos[j] - pos[i]
                    r2 = r_vec.norm_sqr()
                    
                    if r2 < SPH_CUTOFF_SQR:
                        W, _ = gaussian_kernel_and_gradient_3D(r_vec, SMOOTHING_LENGTH)
                        rho_i += masses[j] * W
            
            rho_i = ti.max(rho_i, MIN_DENSITY)
            rho[i] = rho_i
            
            if rho_i <= RHO_CRIT:
                pressure[i] = (SOUND_SPEED**2) * rho_i
            else:
                P_crit = (SOUND_SPEED**2) * RHO_CRIT
                pressure[i] = P_crit * ti.pow(rho_i / RHO_CRIT, GAMMA)

@ti.kernel
def manage_sink_particle():
    if sink_active[None] == 0:
        for i in range(N):
            if is_active[i] == 1 and rho[i] > SINK_CREATION_DENSITY:
                sink_active[None] = 1
                sink_mass[None] = masses[i]
                sink_pos[None] = pos[i]
                sink_vel[None] = vel[i]
                is_active[i] = 0 
                break 

    if sink_active[None] == 1:
        for i in range(N):
            if is_active[i] == 1:
                dist_to_sink = (pos[i] - sink_pos[None]).norm()
                
                if dist_to_sink < SINK_ACCRETION_RADIUS:
                    new_mass = sink_mass[None] + masses[i]
                    new_vel = (sink_mass[None] * sink_vel[None] + masses[i] * vel[i]) / new_mass
                    
                    sink_mass[None] = new_mass
                    sink_vel[None] = new_vel
                    is_active[i] = 0

@ti.kernel
def compute_total_acceleration():
    for i in range(N):
        if is_active[i] == 1:
            acc_i = ti.Vector([0.0, 0.0, 0.0])
            for j in range(N):
                # FIX: Only interact with ALIVE gas, and don't calculate self-force!
                if i != j and is_active[j] == 1:
                    r_vec = pos[i] - pos[j] 
                    r2 = r_vec.norm_sqr()
                    
                    inv_r3 = ti.pow(r2 + SOFT_PARAM**2, -1.5)
                    acc_i += -G * masses[j] * r_vec * inv_r3 
                    
                    if r2 < SPH_CUTOFF_SQR:
                        _, grad_W = gaussian_kernel_and_gradient_3D(r_vec, SMOOTHING_LENGTH)
                        pressure_term = (pressure[i] / (rho[i]**2)) + (pressure[j] / (rho[j]**2))
                        
                        v_vec = vel[i] - vel[j]
                        v_dot_r = v_vec.dot(r_vec)
                        visc_term = 0.0
                        
                        if v_dot_r < 0.0:
                            mu = (SMOOTHING_LENGTH * v_dot_r) / (r2 + EPSILON * SMOOTHING_LENGTH**2)
                            rho_ij = ti.max(0.5 * (rho[i] + rho[j]), MIN_DENSITY)
                            visc_term = (-ALPHA * SOUND_SPEED * mu + BETA * mu**2) / rho_ij
                        
                        acc_i += -masses[j] * (pressure_term + visc_term) * grad_W
            
            # SINK GRAVITY
            if sink_active[None] == 1:
                sink_r_vec = sink_pos[None] - pos[i]
                sink_r2 = sink_r_vec.norm_sqr()
                sink_inv_r3 = ti.pow(sink_r2 + SOFT_PARAM**2, -1.5)
                acc_i += G * sink_mass[None] * sink_r_vec * sink_inv_r3        
            
            acc[i] = acc_i

@ti.kernel
def update_velocity(dt: ti.f32):
    for i in range(N):
        if is_active[i] == 1:
            vel[i] += acc[i] * dt

@ti.kernel
def update_position(dt: ti.f32):
    for i in range(N):
        if is_active[i] == 1:
            pos[i] += vel[i] * dt


def step_physics():
    update_velocity(TIME_STEP / 2.0)
    update_position(TIME_STEP)
    compute_density_and_pressure()
    
    # FIX: Run sink logic before forces
    manage_sink_particle() 
    
    compute_total_acceleration()
    update_velocity(TIME_STEP / 2.0)

# ==========================================
# 6. MAIN GGUI ANIMATION LOOP
# ==========================================
print("Starting Integration on GPU...")

compute_density_and_pressure()
compute_total_acceleration()

window = ti.ui.Window("SPH Star Formation Simulation", (800, 800))
canvas = window.get_canvas()
scene = ti.ui.Scene()
camera = ti.ui.Camera()

camera.position(3, 3, 3)
camera.lookat(0, 0, 0)
camera.up(0, 0, 1) # Note: Up vector changed to Z to match our physics!

while window.running:
    # 5 steps per frame is visually pleasing with the new dt=0.005
    for _ in range(5):
        step_physics()

    camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)
    scene.set_camera(camera)

    scene.ambient_light((0.4, 0.4, 0.4))
    scene.point_light(pos=(2, 2, 2), color=(1.0, 1.0, 1.0))

    # Render Gas
    scene.particles(pos, radius=0.02, color=(0.1, 0.5, 1.0))
    
    # Render the Sink Particle if it exists!
    if sink_active[None] == 1:
        render_sink_pos[0] = sink_pos[None]
        # Draw a big, glowing red star
        scene.particles(render_sink_pos, radius=SINK_ACCRETION_RADIUS, color=(1.0, 0.2, 0.1))

    canvas.scene(scene)
    window.show()