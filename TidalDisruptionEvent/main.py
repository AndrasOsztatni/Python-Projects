import taichi as ti
import numpy as np
import time
from config import FRAME_DURATION
from state import pos, radii, colors
import kernels
import initialization


def run_simulation():
    initialization.setup_initial_condition()

    window = ti.ui.Window("Tidal Disruption Event", res=(initialization.screen_width, initialization.screen_height-30), pos=(0, 30))
    canvas = window.get_canvas()
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()

    camera.position(-10, 0, 30)
    camera.lookat(0, 0, 0)
    camera.up(0, 0, 1)


                
    while window.running:
        start_time = time.time()
        kernels.physics_step()
        
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

if __name__ == "__main__":
    run_simulation()
