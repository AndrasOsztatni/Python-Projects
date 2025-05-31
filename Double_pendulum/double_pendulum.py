import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Define the parameters for the double pendulum
g = 9.81  # Acceleration due to gravity (m/s^2)
L1 = 1.0  # Length of the first pendulum (m)
L2 = 1.0  # Length of the second pendulum (m)
m1 = 1.0  # Mass of the first pendulum (kg)
m2 = 1.0  # Mass of the second pendulum (kg)

# Define the equations of motion for the double pendulum
def equations(t, y):
    theta1, z1, theta2, z2 = y
    delta = theta2 - theta1

    denominator1 = (m1 + m2) * L1 - m2 * L1 * np.cos(delta) * np.cos(delta)
    denominator2 = (L2 / L1) * denominator1

    theta1_dot = z1
    z1_dot = ((m2 * L1 * z1 * z1 * np.sin(delta) * np.cos(delta) +
               m2 * g * np.sin(theta2) * np.cos(delta) +
               m2 * L2 * z2 * z2 * np.sin(delta) -
               (m1 + m2) * g * np.sin(theta1)) / denominator1)

    theta2_dot = z2
    z2_dot = ((-m2 * L2 * z2 * z2 * np.sin(delta) * np.cos(delta) +
               (m1 + m2) * g * np.sin(theta1) * np.cos(delta) -
               (m1 + m2) * L1 * z1 * z1 * np.sin(delta) -
               (m1 + m2) * g * np.sin(theta2)) / denominator2)

    return [theta1_dot, z1_dot, theta2_dot, z2_dot]

# Define initial conditions (in radians and radians per second)
initial_conditions = [np.pi / 2, 0, np.pi / 1, 0]

# Define the time span for the simulation
t_span = (0, 10)
t_eval = np.linspace(0, 10, 2000)

# Solve the equations
solution = solve_ivp(equations, t_span, initial_conditions, t_eval=t_eval, rtol=1e-9)

# Extract the angles from the solution
theta1 = solution.y[0]
theta2 = solution.y[2]

# Calculate the (x, y) positions of the pendulums
x1 = L1 * np.sin(theta1)
y1 = -L1 * np.cos(theta1)
x2 = x1 + L2 * np.sin(theta2)
y2 = y1 - L2 * np.cos(theta2)

# Plot the trajectories of the pendulums
plt.plot(x1, y1, label='Pendulum 1')
plt.plot(x2, y2, label='Pendulum 2')
plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.legend()
plt.title('Double Pendulum Trajectories')
plt.show()
