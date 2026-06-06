import taichi as ti
from config import N

# INITIALIZE TAICHI

ti.init(arch=ti.gpu)

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