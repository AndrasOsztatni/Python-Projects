import pygame
import sys
import math

# 1. Initialize Pygame
pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("3D Solar System Simulation")
clock = pygame.time.Clock()
FPS = 60

# --- Camera Variables ---
radius = 5000.0
theta = math.radians(90)
phi = math.pi / 3

is_dragging = False
last_mouse_pos = (0, 0)
sensitivity = 0.01

# --- NEW: Grid Setup (Subdivided) ---
grid_lines = []
grid_size = 2000     # How far the grid stretches out
grid_step = 100     # The size of each square on the grid

# Instead of drawing one long line, we draw them step-by-step
for i in range(-grid_size, grid_size + 1, grid_step):
    for j in range(-grid_size, grid_size, grid_step):
        
        # 1. Tiny line segments parallel to Z (Front/Back)
        z_start = (i, 0, j)
        z_end = (i, 0, j + grid_step)
        grid_lines.append((z_start, z_end))
        
        # 2. Tiny line segments parallel to X (Left/Right)
        x_start = (j, 0, i)
        x_end = (j + grid_step, 0, i)
        grid_lines.append((x_start, x_end))

# --- NEW: The 3D Engine "Lens" ---
def project_3d_to_2d(x, y, z, cam_theta, cam_phi, cam_radius, screen_w, screen_h):
    """ Converts a 3D coordinate into a 2D screen pixel """
    
    # STEP 1: Yaw (Rotate the universe left/right around the Y-axis)
    x_rot1 = x * math.cos(cam_theta) - z * math.sin(cam_theta)
    y_rot1 = y
    z_rot1 = x * math.sin(cam_theta) + z * math.cos(cam_theta)
    
    # STEP 2: Pitch (Rotate the universe up/down around the X-axis)
    pitch = math.pi / 2 - cam_phi
    x_rot2 = x_rot1
    y_rot2 = y_rot1 * math.cos(pitch) - z_rot1 * math.sin(pitch)
    z_rot2 = y_rot1 * math.sin(pitch) + z_rot1 * math.cos(pitch)
    
    # STEP 3: Translate (Push the universe away by the camera's radius)
    x_final = x_rot2
    y_final = y_rot2
    z_final = z_rot2 + cam_radius
    
    # STEP 4: Perspective Projection (Flatten to 2D)
    FOV = 400 # Focal length (Field of View zoom)
    
    # We only draw points that end up IN FRONT of the camera (z_final > 0)
    if z_final > 1:
        # Calculate 2D position and shift to the center of the screen
        screen_x = screen_w // 2 + int((x_final * FOV) / z_final)
        # We SUBTRACT the Y value because Pygame's Y-axis is inverted (0 is at the top)
        screen_y = screen_h // 2 - int((y_final * FOV) / z_final)
        return (screen_x, screen_y)
    
    # If the point is behind the camera, return None so we don't draw it
    return None

# --- NEW: Custom UI Slider Class ---
class TimeSlider:
    def __init__(self, min_val, max_val, start_val):
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.is_dragging = False
        self.width = 200
        self.height = 10
        self.font = pygame.font.SysFont(None, 24)
        
    def update_and_draw(self, screen, events, screen_width):
        # 1. Anchor the slider to the top right of the screen
        x = screen_width - self.width - 30
        y = 30
        
        # Calculate exactly where the knob should sit based on current speed
        percent = (self.val - self.min_val) / (self.max_val - self.min_val)
        knob_x = x + (percent * self.width)
        knob_y = y + (self.height // 2)

        # 2. Handle Mouse Interaction
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Calculate distance from mouse click to the knob center
                dist = math.dist(event.pos, (knob_x, knob_y))
                if dist < 15: # If they clicked within 15 pixels of the knob, start dragging
                    self.is_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_dragging = False
            elif event.type == pygame.MOUSEMOTION and self.is_dragging:
                # Clamp the mouse X position so it can't drag off the edges of the track
                mouse_x = max(x, min(event.pos[0], x + self.width))
                # Calculate the new time value based on the new mouse position
                new_percent = (mouse_x - x) / self.width
                self.val = self.min_val + new_percent * (self.max_val - self.min_val)

        # 3. Draw the UI
        pygame.draw.rect(screen, (100, 100, 100), (x, y, self.width, self.height), border_radius=5) # Track
        pygame.draw.circle(screen, (255, 255, 255), (int(knob_x), int(knob_y)), 10) # Knob
        
        # Draw the text label underneath
        text = self.font.render(f"Simulation Speed: {self.val:.2f}x", True, (255, 255, 255))
        screen.blit(text, (x, y + 20))
        
        return self.val

# Initialize the slider (Min speed 0.0, Max speed 10.0, Starting speed 1.0)
time_slider = TimeSlider(0.0, 10.0, 1.0)

class Body:
    G = 0.001

    def __init__(self, x, y, z, mass, color, radius, vx=0.0, vy=0.0, vz=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.mass = mass
        self.color = color
        self.radius = radius
        
        # Velocity (Speed)
        self.vx = vx
        self.vy = vy
        self.vz = vz
        

    def calculate_gravity(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        
        # Distance formula: r = sqrt(dx^2 + dy^2 + dz^2)
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        # Safety check: If they are in the exact same spot, prevent division by zero
        if distance == 0:
            return 0, 0, 0

        # Newton's Law of Universal Gravitation
        force = self.G * (self.mass * other.mass) / (distance**2)
        
        # Break the force down into X, Y, Z components
        force_x = force * (dx / distance)
        force_y = force * (dy / distance)
        force_z = force * (dz / distance)
        
        return force_x, force_y, force_z

    def update_position(self, force_x, force_y, force_z, time_step=1.0):
        #Accerelation of the Body
        ax = force_x / self.mass
        ay = force_y / self.mass
        az = force_z / self.mass

        # Update velocity based on acceleration
        self.vx += ax * time_step
        self.vy += ay * time_step
        self.vz += az * time_step

        # Update position based on the new velocity
        self.x += self.vx * time_step
        self.y += self.vy * time_step
        self.z += self.vz * time_step

# --- NEW: Create the Solar System ---
# Create a list to hold all our celestial bodies
# --- NEW: Create the Solar System ---
bodies = []

# Create the Sun
# Mass is 333,000x Earth. It sits dead center at (0,0,0).
sun = Body(0, 0, 0, mass=333000, color=(255, 255, 0), radius=25)
bodies.append(sun)

# 1 AU (Astronomical Unit) = 150 pixels in our 3D engine
AU = 150

# Planet Data: (Name, Distance in AU, Mass relative to Earth, Color, Radius for drawing)
planet_data = [
    ("Neptune", 30.07, 17.00, (100, 150, 220), 12),
    ("Uranus", 19.19, 14.00, (150, 200, 255), 12),
    ("Saturn", 9.537, 95.00, (230, 210, 180), 16),
    ("Jupiter", 5.203, 318.0, (200, 180, 150), 18),
    ("Mars", 1.524, 0.107, (255, 100, 100), 5),
    ("Earth", 1.000, 1.000, (100, 150, 255), 9),
    ("Venus", 0.723, 0.815, (255, 200, 150), 8),
    ("Mercury", 0.387, 0.055, (150, 150, 150), 4) 
]

# Generate all planets automatically
for name, au_dist, relative_mass, color, radius in planet_data:
    # Convert AU to actual 3D pixel coordinates
    distance_from_sun = au_dist * AU
    
    # Calculate the perfect starting velocity for a circular orbit
    # v = sqrt(G * M_sun / r)
    orbital_velocity = math.sqrt(Body.G * sun.mass / distance_from_sun)
    
    # Create the planet and push it perfectly along the Z-axis
    planet = Body(
        x=distance_from_sun, 
        y=0, 
        z=0, 
        mass=relative_mass, 
        color=color, 
        radius=radius, 
        vx=0, 
        vy=0, 
        vz=orbital_velocity
    )
    bodies.append(planet)

# 4. The Main Application Loop
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH = event.w
            HEIGHT = event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            
        # --- Camera Mouse Controls ---
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # NEW RULE: Only drag the camera if the slider is NOT being dragged
            if event.button == 1 and not time_slider.is_dragging: 
                is_dragging = True
                last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            # We also check not time_slider.is_dragging here to ensure the camera 
            # freezes while we are adjusting the speed
            if is_dragging and not time_slider.is_dragging:
                mouse_x, mouse_y = event.pos
                dx = mouse_x - last_mouse_pos[0]
                dy = mouse_y - last_mouse_pos[1]
                theta += dx * sensitivity
                phi += dy * sensitivity
                phi = max(0.01, min(math.pi - 0.01, phi))
                last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEWHEEL:
            radius -= event.y * 50 
            radius = max(50.0, radius)

    # --- B. Game Logic / Physics ---
    
    # Step 1: Calculate forces for all bodies BEFORE moving them.
    # (If we move them while calculating, the math breaks!)
    current_time_step = time_slider.update_and_draw(screen, events, WIDTH)

    # Calculate forces
    forces = []
    for body in bodies:
        total_fx = total_fy = total_fz = 0
        for other in bodies:
            if body != other:
                fx, fy, fz = body.calculate_gravity(other)
                total_fx += fx
                total_fy += fy
                total_fz += fz
        forces.append((total_fx, total_fy, total_fz))

    # Apply forces using the SLIDER's time step!
    for i, body in enumerate(bodies):
        # We only need to do math if the time step is greater than 0
        if current_time_step > 0:
            body.update_position(forces[i][0], forces[i][1], forces[i][2], time_step=current_time_step)


    # --- C. Rendering (Drawing) ---
    screen.fill((0, 0, 0))

    # 1. Draw the Grid (Keep your existing grid drawing code here)
    for start_point, end_point in grid_lines:
        p1_2d = project_3d_to_2d(*start_point, theta, phi, radius, WIDTH, HEIGHT)
        p2_2d = project_3d_to_2d(*end_point, theta, phi, radius, WIDTH, HEIGHT)
        if p1_2d and p2_2d:
            pygame.draw.line(screen, (50, 50, 50), p1_2d, p2_2d, 1)

    # 2. Draw the Planets
    FOV = 400 # This should match the FOV inside your project_3d_to_2d function!
    
    for body in bodies:
        pos_2d = project_3d_to_2d(body.x, body.y, body.z, theta, phi, radius, WIDTH, HEIGHT)
        
        if pos_2d: 
            # Calculate the true distance from the camera to the planet
            # (We approximate using the camera's radius for the scale illusion)
            scale_factor = FOV / radius
            
            # Scale the planet's drawn radius perfectly
            drawn_radius = max(2, int(body.radius * scale_factor))
            pygame.draw.circle(screen, body.color, pos_2d, drawn_radius)

    # Update the actual display
    pygame.display.flip()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()