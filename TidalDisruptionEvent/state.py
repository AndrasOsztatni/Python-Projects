import taichi as ti
import numpy as np
from config import N

ti.init(arch=ti.gpu)

pos = ti.Vector.field(3, dtype=ti.f32, shape=N+1)
vel = ti.Vector.field(3, dtype=ti.f32, shape=N+1)
acc = ti.Vector.field(3, dtype=ti.f32, shape=N+1)
colors = ti.Vector.field(3, dtype=ti.f32, shape=N+1)
radii = ti.field(dtype=ti.f32, shape=N+1)
central_sink_is_active = ti.field(dtype=ti.f32, shape=N+1)


central_sink_is_active_np = np.ones(N+1)



masses = ti.field(dtype=ti.f32, shape=N+1)