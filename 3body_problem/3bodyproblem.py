import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

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
initial_positions = [-1.0, 0.0, 0.1, 1.0, 0.0, 0.0]
initial_velocities = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
initial_conditions = initial_positions + initial_velocities

# Define time span for the simulation
t_span = (0, 6)
t_eval = np.linspace(0, 6, 1000)

# Solve the equations
solution = solve_ivp(equations, t_span, initial_conditions, t_eval=t_eval, rtol=1e-9)

# Extract the positions from the solution
x1, y1 = solution.y[0], solution.y[1]
x2, y2 = solution.y[2], solution.y[3]
x3, y3 = solution.y[4], solution.y[5]

# Plot the trajectories
plt.plot(x1, y1, label='Body 1')
plt.plot(x2, y2, label='Body 2')
plt.plot(x3, y3, label='Body 3')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.title('Three-Body Problem Trajectories')
plt.show()
