import taichi as ti
import numpy as np
import time
import tkinter as tk
#Constants
M = 50
m = 1
N = 5000
R = 0.5
R_0 = [5, 0, 0]
G = 1
SOFT_PARAM = 0.1
TIME_STEP = 0.002
TARGET_FPS = 300
FRAME_DURATION = 1 / TARGET_FPS
CENTRAL_RADIUS = 0.2




root = tk.Tk()
root.withdraw() 
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
vel_np[1:] = [0, -2.162, 0]

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


            

@ti.kernel
def acceleration():
    acc[0] = ti.Vector([0.0, 0.0, 0.0])
    for i in range(1, N+1):
        grav_acc = ti.Vector([0.0, 0.0, 0.0])
        
        if (pos[i]-pos[0]).norm() <= radii[0]+0.2 and central_sink_is_active[i]==1:
                central_sink_is_active[i] = 0
                radii[i] = 0.0
                masses[i] = 0.0
                masses[0] += m/N     
                continue

        
        if  central_sink_is_active[i]==1:
            r_vec = pos[i] - pos[0] 
            r2 = r_vec.norm_sqr()
                
            inv_r3 = ti.pow(r2 + SOFT_PARAM**2, -1.5)
            grav_acc += -G * masses[0] * r_vec * inv_r3

                
                
        acc[i] = grav_acc

@ti.kernel
def update_velocity(dt:ti.f32):
    for i in range(1, N+1):
        if central_sink_is_active[i]==1:
            vel[i]+=acc[i]*dt
            
        

@ti.kernel
def update_position(dt:ti.f32):
    for i in range(N+1):
        if central_sink_is_active[i] == 1:
            pos[i]+=vel[i]*dt
        



def physics_step():
    update_velocity(TIME_STEP/2)
    update_position(TIME_STEP)
    acceleration()
    update_velocity(TIME_STEP/2)
    
    


while window.running:
    start_time = time.time()
    physics_step()
    
    camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)

    scene = ti.ui.Scene()
    scene.set_camera(camera)
    scene.ambient_light((0.4, 0.4, 0.4))
    scene.point_light(pos=(2, 2, 2), color=(1.0, 1.0, 1.0))
    scene.particles(pos, radius=0.02, per_vertex_radius=radii, per_vertex_color=colors)
   
    canvas.scene(scene)
    window.show()

    elapsed_time = time.time() - start_time
    if elapsed_time < FRAME_DURATION:
        time.sleep(FRAME_DURATION - elapsed_time)
