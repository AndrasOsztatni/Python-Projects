import taichi as ti
import numpy as np
import time
import tkinter as tk
#Constants
M = 50
m = 20
N = 5000
R = 0.5
R_0 = [10, 0, 0]
G = 1
SOFT_PARAM = 0.01
TIME_STEP = 0.0025
TARGET_FPS = 300
FRAME_DURATION = 1 / TARGET_FPS
CENTRAL_RADIUS = 0.6
MIN_DISTANCE = 0.01
SMOOTHING_LENGTH = 0.5
SPH_CUTOFF = 3.0 * SMOOTHING_LENGTH
SPH_CUTOFF_SQR = SPH_CUTOFF**2
MIN_DENSITY = 0.05
CIRCLE_RES = 1000

root = tk.Tk()
root.withdraw() # Hide the main tkinter window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

#Initialize Taichi
ti.init(arch=ti.gpu)

pos = ti.Vector.field(3, dtype=ti.f32, shape=N+1)
vel = ti.Vector.field(3, dtype=ti.f32, shape=N+1)
acc = ti.Vector.field(3, dtype=ti.f32, shape=N+1)
colors = ti.Vector.field(3, dtype=ti.f32, shape=N+1)
radii = ti.field(dtype=ti.f32, shape=N+1)
central_sink_is_active = ti.field(dtype=ti.f32, shape=N+1)
rho = ti.field(dtype=ti.f32, shape=N+1)

circle_pos = ti.Vector.field(3, dtype=ti.f32, shape=CIRCLE_RES)
circle_indices = ti.field(dtype=ti.i32, shape=CIRCLE_RES * 2)

circle_pos_np = np.zeros((CIRCLE_RES, 3), dtype=np.float32)
circle_indices_np = np.zeros(CIRCLE_RES * 2, dtype=np.int32)

central_sink_is_active_np = np.ones(N+1)

radii_np = np.ones(N+1) * 0.02
radii_np[0] = CENTRAL_RADIUS

colors_np = np.ones((N+1, 3))
colors_np[0] = [1, 1, 0]
colors_np[1:] = [125/255, 186/255, 1] 

masses = ti.field(dtype=ti.f32, shape=N+1)

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
vel_np[1:] = [-2, -1, 0]

masses.from_numpy(masses_np.astype(np.float32))
pos.from_numpy(pos_np.astype(np.float32))
vel.from_numpy(vel_np.astype(np.float32))
colors.from_numpy(colors_np.astype(np.float32))
radii.from_numpy(radii_np.astype(np.float32))
central_sink_is_active.from_numpy(central_sink_is_active_np.astype(np.float32))
window = ti.ui.Window("Tidal Disruption Event", res=(screen_width, screen_height-30), pos=(0, 30))
canvas = window.get_canvas()
scene = ti.ui.Scene()
camera = ti.ui.Camera()

camera.position(-10, 0, 30)
camera.lookat(0, 0, 0)
camera.up(0, 0, 1)

@ti.func
def gaussian_kernel_and_gradient_3D(r_vec, h):
    r2 = r_vec.norm_sqr()
    normalization = 1.0 / ((h * np.sqrt(np.pi))**3)
    W = normalization * ti.exp(-r2 / (h**2))
    
    grad_factor = (-2.0 / (h**2)) * W
    grad_W = grad_factor * r_vec
    return W, grad_W

@ti.kernel
def compute_density_and_pressure():
    for i in range(N):
        if central_sink_is_active[i] == 1:    
            rho_i = 0.0
            for j in range(N):
                if central_sink_is_active[j] == 1: 
                    r_vec = pos[j] - pos[i]
                    r2 = r_vec.norm_sqr()
                    
                    if r2 < SPH_CUTOFF_SQR:
                        W, _ = gaussian_kernel_and_gradient_3D(r_vec, SMOOTHING_LENGTH)
                        rho_i += masses[j] * W
            
            rho_i = ti.max(rho_i, MIN_DENSITY)
            rho[i] = rho_i
            

@ti.kernel
def acceleration():
    acc[0] = ti.Vector([0.0, 0.0, 0.0])
    for i in range(1, N+1):
        acc_i = ti.Vector([0.0, 0.0, 0.0])
        if (pos[i]-pos[0]).norm() <= CENTRAL_RADIUS+0.5:
                central_sink_is_active[i] = 0
                radii[i] = 0.0
                masses[i] = 0.0
                masses[0] += m/N
                
                continue
        for j in range(N+1):
            if (pos[i]-pos[j]).norm() <= MIN_DISTANCE:
                acc[i] = [0, 0, 0]
                break
            if i != j:
                r_vec = pos[i] - pos[j] 
                r2 = r_vec.norm_sqr()
                
                inv_r3 = ti.pow(r2 + SOFT_PARAM**2, -1.5)
                acc_i += -G * masses[j] * r_vec * inv_r3
        acc[i] = acc_i

@ti.kernel
def update_velocity(dt:ti.f32):
    for i in range(N+1):
        if central_sink_is_active[i]==1:
            vel[i]+=acc[i]*dt

@ti.kernel
def update_position(dt:ti.f32):
    for i in range(N+1):
        if central_sink_is_active[i] == 1:
            pos[i]+=vel[i]*dt
        

def get_Roche_Limit():
    R = np.pow(16, 1/3) * (CENTRAL_RADIUS+0.5) * np.pow((M*N / m), 1/3) 
    return R

def physics_step():
    update_velocity(TIME_STEP/2)
    update_position(TIME_STEP)
    acceleration()
    update_velocity(TIME_STEP/2)
    
    



def Circle():
    Circle_Radius = get_Roche_Limit()
    for i in range(CIRCLE_RES):
        angle = (i / CIRCLE_RES) * 2 * np.pi
        
        circle_pos_np[i] = [Circle_Radius * np.cos(angle), Circle_Radius * np.sin(angle), 0.0]
        
        circle_indices_np[2*i] = i
        circle_indices_np[2*i + 1] = (i + 1) % CIRCLE_RES

    circle_pos.from_numpy(circle_pos_np)
    circle_indices.from_numpy(circle_indices_np)
Circle()
print(get_Roche_Limit())
while window.running:
    start_time = time.time()
    physics_step()
    
    camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)

    scene = ti.ui.Scene()
    scene.set_camera(camera)
    scene.ambient_light((0.4, 0.4, 0.4))
    scene.point_light(pos=(2, 2, 2), color=(1.0, 1.0, 1.0))
    scene.particles(pos, radius=0.02, per_vertex_radius=radii, per_vertex_color=colors)
    Circle()
    scene.lines(circle_pos, width=2, indices=circle_indices, color=(1.0, 0.0, 0.0)) 
    canvas.scene(scene)
    window.show()

    elapsed_time = time.time() - start_time
    if elapsed_time < FRAME_DURATION:
        time.sleep(FRAME_DURATION - elapsed_time)
