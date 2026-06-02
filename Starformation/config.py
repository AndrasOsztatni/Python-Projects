import math

G = 1.0                     #Gravitational Constant
M = 2.0                     #Total Mass
N = 4000                    # Particle count 
R = 1.0                     #Radius of Sphere inwhich Particles are generated at the beginning
OMEGA = 1.0                 #Initial angular velocity 


TIME_STEP = 0.005   
SOFT_PARAM = 0.1            #Softhening Parameter to avoid ininities by inverse square laws
SMOOTHING_LENGTH = 0.5      #SPH Smoothening Length
SOUND_SPEED = 0.5           #Speed of Sound

# Viscosity Parameters
ALPHA = 0.25                
BETA = 0.5                  
EPSILON = 0.01              
MIN_DENSITY = 0.05          

# Energy Conservation Parameters
GAMMA = 5.0 / 3.0            
RHO_CRIT = 3.0     

# Sink Particle Parameters
SINK_CREATION_DENSITY = 8.0  
SINK_ACCRETION_RADIUS = 0.15  

SPH_CUTOFF = 3.0 * SMOOTHING_LENGTH
SPH_CUTOFF_SQR = SPH_CUTOFF**2

#Turbulance for randomness at the beginning
TURBULENCE_STRENGTH = 0.5