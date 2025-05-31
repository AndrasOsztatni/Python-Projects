import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define the gravitational constant
G = 1.0  # Using a normalized gravitational constant for simplicity

# Define masses of the three bodies
m1 = 1.0
m2 = 1.0
m3 = 1.0

# Define the equations of motion
def equations(t, y):
    x1, y1, x2, y2, x3, y3, vx1, vy1, vx2, vy2, vx3, vy3 = y
    r12 = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    r13 = np.sqrt((x3 - x1)**2 + (y3 - y1)**2)
    r23 = np.sqrt((x3 - x2)**2 + (y3 - y2)**2)
    
    ax1 = G * m2 * (x2 - x1) / r12**3 + G * m3 * (x3 - x1) / r13**3
    ay1 = G * m2 * (y2 - y1) / r12**3 + G * m3 * (y3 - y1) / r13**3
    ax2 = G * m1 * (x1 - x2) / r12**3 + G * m3 * (x3 - x2) / r23**3
    ay2 = G * m1 * (y1 - y2) / r12**3 + G * m3 * (y3 - y2) / r23**3
    ax3 = G * m1 * (x1 - x3) / r13**3 + G * m2 * (x2 - x3) / r23**3
    ay3 = G * m1 * (y1 - y3) / r13**3 + G * m2 * (y2 - y3) / r23**3
    
    return [vx1, vy1, vx2, vy2, vx3, vy3, ax1, ay1, ax2, ay2, ax3, ay3]

# Define initial positions and velocities
initial_positions = [-1.0, 0.0, 1.0, 1.0, 0.2, -1.0]
initial_velocities = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
initial_conditions = initial_positions + initial_velocities

# Define time span for the simulation
t_span = (0, 100)
t_eval = np.linspace(0, 100, 3000)

# Solve the equations
solution = solve_ivp(equations, t_span, initial_conditions, t_eval=t_eval, rtol=1e-9)

# Extract the positions from the solution
x1, y1 = solution.y[0], solution.y[1]
x2, y2 = solution.y[2], solution.y[3]
x3, y3 = solution.y[4], solution.y[5]

# Ensure x1, y1, x2, y2, x3, and y3 are sequences
x1, y1 = np.asarray(x1), np.asarray(y1)
x2, y2 = np.asarray(x2), np.asarray(y2)
x3, y3 = np.asarray(x3), np.asarray(y3)

# Create the figure and axes
fig, ax = plt.subplots()
line1, = ax.plot([], [], label='Body 1', color='blue')
line2, = ax.plot([], [], label='Body 2', color='green')
line3, = ax.plot([], [], label='Body 3', color='red')
marker1 = ax.plot([], [], 'o', color='blue')[0]
marker2 = ax.plot([], [], 'o', color='green')[0]
marker3 = ax.plot([], [], 'o', color='red')[0]
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.set_title('Three-Body Problem Trajectories')

# Initialization function to set up the background of each frame
def init():
    line1.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    marker1.set_data([], [])
    marker2.set_data([], [])
    marker3.set_data([], [])
    return line1, line2, line3, marker1, marker2, marker3

# Animation function to update the data for each frame
def update(frame):
    if frame<100:
        line1.set_data(x1[:frame], y1[:frame])
        line2.set_data(x2[:frame], y2[:frame])
        line3.set_data(x3[:frame], y3[:frame])
        marker1.set_data([x1[frame]], [y1[frame]])
        marker2.set_data([x2[frame]], [y2[frame]])
        marker3.set_data([x3[frame]], [y3[frame]])
        return line1, line2, line3, marker1, marker2, marker3
    else:
        line1.set_data(x1[(frame-100):frame], y1[(frame-100):frame])
        line2.set_data(x2[(frame-100):frame], y2[(frame-100):frame])
        line3.set_data(x3[(frame-100):frame], y3[(frame-100):frame])
        marker1.set_data([x1[frame]], [y1[frame]])
        marker2.set_data([x2[frame]], [y2[frame]])
        marker3.set_data([x3[frame]], [y3[frame]])
        return line1, line2, line3, marker1, marker2, marker3

# Create the animation
ani = FuncAnimation(fig, update, frames=len(t_eval), init_func=init, interval=25)

# Display the animation
plt.show()
