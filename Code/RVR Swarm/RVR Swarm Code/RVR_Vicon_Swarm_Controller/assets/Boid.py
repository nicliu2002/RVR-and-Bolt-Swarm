"""
Boid Class

The Boid class is a fundamental component for simulating the behavior of individual agents in a swarm.
The Boid class represents an individual agent in a swarm robotics scenario. 
Boids follow specific rules, such as alignment, cohesion, and separation, to calculate their linear and angular velocities. 
This class also handles the computation of forces and velocities for each boid, including interactions with neighbors and wall avoidance. 
Additionally, it manages the boid's position, heading angle, and other essential properties.

@author    Reda Ghanem
@version   1.0
"""

# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #

import math                         # for mathematical operations
import numpy as np                  # for array operations

# Constants must be first import
from assets import Constants as Cons            # for Constants and Global variables
from Helper_Functions import *                  # for helper functions ex. normalize_speed_limit ...
from Boids_Rules import *                       # for swarm rules ex. alignment_rule, cohesion_rule ...


# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #

# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #
# ┃---------------------------- # Boid Class # --------------------------------┃ #
# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #

class Boid:
    def __init__(self, start_position = [0,0], start_heading_angle = 0, boid_size = [10,10], boid_id = 0):

        self.x, self.y              = start_position            # start_position contains [x, y] of the boid
        self.position               = [self.x, self.y]          # boid position as list [x, y]
        self.heading_angle          = start_heading_angle       # start Orientation angle of the boid

        # Calculate the forward velocity
        self.delta_x                = Cons.MAX_LINEAR_SPEED * math.cos(self.heading_angle)
        self.delta_y                = Cons.MAX_LINEAR_SPEED * math.sin(self.heading_angle)
        self.delta_x, self.delta_y  = normalize_speed_limit([self.delta_x, self.delta_y], Cons.MIN_LINEAR_SPEED, Cons.MAX_LINEAR_SPEED)
        self.velocity               = [self.delta_x, self.delta_y]  # boid velocity as list [delt_x, delt_y]

        self.acceleration           = 1                          # acceleration
        self.linear_velocity        = Cons.MAX_LINEAR_SPEED      # linear velocity in pixel/sec, where 1 pixel = 1 cm
        self.angular_velocity       = 0                          # angular velocity in rad/sec

        self.width                  = boid_size[0]               # width of boid
        self.height                 = boid_size[1]               # height of boid
        self.radius                 = 0.5 * math.sqrt(self.width **2 + self.height **2)

        self.id                     = boid_id                    # boid id


        # variables to collect data from neighbors 
        self.neighbors_IDs = []
        self.neighbors_positions = []
        self.neighbors_velocities = []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to compute next step math
    def update_velocity(self):

        # Calculate boid forces
        alignment_force          = alignment_rule(self, self.neighbors_positions , self.neighbors_velocities)
        cohesion_force           = cohesion_rule(self, self.neighbors_positions)
        separation_force         = separation_rule(self, self.neighbors_positions)

        wall_avoidance_force     = wall_avoidance_rule(self)


        force_x = (
                    Cons.ALIGNMENT_WEIGHT            * alignment_force[0]            +
                    Cons.COHESION_WEIGHT             * cohesion_force[0]             +
                    Cons.SEPARATION_WEIGHT           * separation_force[0]           +
                    Cons.WALL_AVOIDANCE_WEIGHT       * wall_avoidance_force[0]       

                )

        force_y = (
                    Cons.ALIGNMENT_WEIGHT            * alignment_force[1]            +
                    Cons.COHESION_WEIGHT             * cohesion_force[1]             +
                    Cons.SEPARATION_WEIGHT           * separation_force[1]           +
                    Cons.WALL_AVOIDANCE_WEIGHT       * wall_avoidance_force[1]       
                )
        

        # round values to make numbers same in all OS (Windows, Linux)
        force_x , force_y = [round(v, 5) for v in [force_x, force_y] ]
        

        #  Update boid's velocity
        self.delta_x += force_x
        self.delta_y += force_y

        # Normalize boid's velocity to limit it in range [MIN_LINEAR_SPEED, MAX_LINEAR_SPEED]
        self.delta_x, self.delta_y = normalize_speed_limit([self.delta_x, self.delta_y], Cons.MIN_LINEAR_SPEED, Cons.MAX_LINEAR_SPEED)

        # update boid velocity
        self.velocity   = [self.delta_x, self.delta_y]  # boid velocity as list [delt_x, delt_y]

        current_angle = self.heading_angle
        desired_angle = math.atan2(self.delta_y, self.delta_x)
        angle_diff = desired_angle - current_angle
        angle_diff = normalize_angle_diff(angle_diff)

        # Calculate angular_velocity
        Kp = 5                                      
        angular_velocity = Kp * angle_diff          
        angular_velocity = normalize_angular_velocity(angular_velocity, Cons.MIN_ANGULAR_SPEED, Cons.MAX_ANGULAR_SPEED)        

        # Control moving forward while turning
        ANGLE_THRESHOLD = 0.05     # Threshold angle value to control when moving forward while turning
        if abs(angle_diff) > ANGLE_THRESHOLD:
            slow_temp = ( math.degrees(abs(angle_diff)) )/20 + 1         
            linear_velocity = Cons.MAX_LINEAR_SPEED/slow_temp           
            # round values to make numbers same in all OS (Windows, Linux)
            linear_velocity = round(linear_velocity, 5)
        else:
            # Move forward once the boid is facing the correct direction,
            linear_velocity = Cons.MAX_LINEAR_SPEED         

        # update boid linear and angular velocities
        self.linear_velocity  = linear_velocity   # Set a desired linear velocity
        self.angular_velocity = angular_velocity  # Set a desired angular velocity


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to clear all old neighbors data
    def clear_neighbors_data(self):

        self.neighbors_IDs.clear()
        self.neighbors_positions.clear()
        self.neighbors_velocities.clear()
        
