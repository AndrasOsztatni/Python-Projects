# main.py
import taichi as ti
from config import SINK_ACCRETION_RADIUS
import state
import initialization
import physics
import os

if not os.path.exists("sim_data"):
    os.makedirs("sim_data")

def run_simulation():
    print("Initializing Initial Conditions...")
    initialization.setup_initial_conditions()

    print("Starting Integration on GPU...")
    physics.compute_density_and_pressure()
    physics.compute_total_acceleration()

    window = ti.ui.Window("SPH Star Formation Simulation", (800, 800))
    canvas = window.get_canvas()
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()

    camera.position(3, 3, 3)
    camera.lookat(0, 0, 0)
    camera.up(0, 0, 1) 

    while window.running:
        for _ in range(5):
            physics.step_physics()

        camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)
        scene.set_camera(camera)

        scene.ambient_light((0.4, 0.4, 0.4))
        scene.point_light(pos=(2, 2, 2), color=(1.0, 1.0, 1.0))

        # Render Gas
        scene.particles(state.pos, radius=0.02, color=(0.1, 0.5, 1.0))
        
        # Render the Sink Particle if it exists
        if state.sink_active[None] == 1:
            state.render_sink_pos[0] = state.sink_pos[None]
            scene.particles(state.render_sink_pos, radius=SINK_ACCRETION_RADIUS, color=(1.0, 0.2, 0.1))

        canvas.scene(scene)
        window.show()

if __name__ == "__main__":
    run_simulation()