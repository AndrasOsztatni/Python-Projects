import taichi as ti
import math
from config import *
from state import *

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