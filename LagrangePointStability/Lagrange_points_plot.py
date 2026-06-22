import numpy as np
import matplotlib.pylab as plt
from scipy.optimize import fsolve
import os

mu = 0.05

FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))

def effective_potential(x, y):
    r1 = np.sqrt((x+mu)**2+y**2)
    r2 = np.sqrt((x - 1 + mu)**2 + y**2)

    r1 = np.where(r1 == 0, 1e-10, r1)
    r2 = np.where(r2 == 0, 1e-10, r2)

    return 0.5 * (x**2 + y**2) + (1 - mu) / r1 + mu / r2

def dU_dx(x):
    r1 = np.abs(x+mu)
    r2 = np.abs(x - 1 + mu)
    return x - ((1 - mu) * (x + mu) / r1**3) - (mu * (x - 1 + mu) / r2**3)

x_L1 = fsolve(dU_dx, 0.5)[0]
x_L2 = fsolve(dU_dx, 1.5)[0]
x_L3 = fsolve(dU_dx, -1.0)[0]

x_L45 = 0.5 - mu
y_L4 = np.sqrt(3) / 2
y_L5 = -np.sqrt(3) / 2

x_val = np.linspace(-1.6, 1.6, 600)
y_val = np.linspace(-1.5, 1.5, 600)
X, Y = np.meshgrid(x_val, y_val)
Z = effective_potential(X, Y)

Z_capped = np.clip(Z, None, 2.5)

plt.figure(figsize=(10, 8), facecolor='#f0f0f0')
ax = plt.gca()

levels = np.linspace(1.4, 2.5, 60)
contours = ax.contour(X, Y, Z_capped, levels=levels, colors='black', linewidths=0.6, alpha=0.7)

C_L1 = effective_potential(x_L1, 0)
C_L2 = effective_potential(x_L2, 0)
C_L3 = effective_potential(x_L3, 0)

ax.contour(X, Y, Z, levels=[C_L1], colors=['red'], linewidths=1.2, alpha=0.5)
ax.contour(X, Y, Z, levels=[C_L2], colors=['blue'], linewidths=1.2, alpha=0.5)
ax.contour(X, Y, Z, levels=[C_L3], colors=['orange'], linewidths=1.2, alpha=0.5)

ax.plot(-mu, 0, 'yo', markersize=25, label='Sun (Primary)')
ax.plot(1-mu, 0, 'ko', markersize=10, markerfacecolor='#4b8bbe',  label='Earth (Secondary)')

l_points_x = [x_L1, x_L2, x_L3, x_L45, x_L45]
l_points_y = [0, 0, 0, y_L4, y_L5]
labels = ['L1', 'L2', 'L3', 'L4', 'L5']

for px, py, label in zip(l_points_x, l_points_y, labels):
    ax.plot(px, py, 'go', markersize=4)
    ax.text(px + 0.05, py + 0.05, label, fontsize=12, fontweight='bold', color='#333333')


ax.set_aspect('equal')
plt.title(f'Effective Potential Contours (Mass Ratio $\mu$ = {mu})', fontsize=14, pad=15)
plt.xlabel('x (Normalized Distance)')
plt.ylabel('y (Normalized Distance)')
plt.xlim([-1.6, 1.6])
plt.ylim([-1.5, 1.5])
plt.grid(False)
plt.legend(loc='lower right')

plt.tight_layout()
plt.savefig(os.path.join(FOLDER_PATH, "Lagrange_points_plot.jpg"), format="jpg")