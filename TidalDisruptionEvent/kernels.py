import taichi as ti
from config import *
from state import *

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