"""
Helper Functions

This code snippet defines various utility functions that can be used for different purposes. 
These functions cover a range of tasks such as normalizing angles and velocities, and calculate_distance.

@ author    Reda Ghanem
@ version   1.0
"""

# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #

import math                         # for mathematical operations
import os                           # for operating system related functionalities
import platform                     # Module for obtaining the operating system information
import sys                          # Module for interacting with the Python interpreter
import tkinter as tk                # Import the tkinter module and alias it as "tk"
import time
from tkinter import messagebox


# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# Function to normalize the difference between two angles
def normalize_angle_diff(angle_diff):
    angle_diff = math.atan2(math.sin(angle_diff) , math.cos(angle_diff))

    # round values to make numbers same in all OS (Windows, Linux)
    angle_diff = round(angle_diff, 5)

    return angle_diff
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# Function to normalize the angular velocity vector
def normalize_angular_velocity(raw_angular_velocity, min_angular_speed, max_angular_speed):
    clamped_angular_velocity = max(min(raw_angular_velocity, max_angular_speed), min_angular_speed)

    # round values to make numbers same in all OS (Windows, Linux)
    clamped_angular_velocity = round(clamped_angular_velocity, 5)

    return clamped_angular_velocity
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# Function to normalize the linear speed vector
def normalize_speed_limit(speed , min_speed , max_speed ):
    speed_magnitude = math.sqrt(speed[0]**2 + speed[1]**2)
    if speed_magnitude != 0:
        if speed_magnitude > max_speed:
            speed[0] = (speed[0] / speed_magnitude) * max_speed
            speed[1] = (speed[1] / speed_magnitude) * max_speed
        elif speed_magnitude < min_speed:
            speed[0] = (speed[0] / speed_magnitude) * min_speed
            speed[1] = (speed[1] / speed_magnitude) * min_speed
    
    # round values to make numbers same in all OS (Windows, Linux)
    speed = [round(v, 5) for v in [speed[0], speed[1]] ]
    
    return speed
# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #
def calculate_distance(point_a, point_b):
        distance_diff = [point_a[0] - point_b[0], point_a[1] - point_b[1]]
        distance = math.sqrt(distance_diff[0] ** 2 + distance_diff[1] ** 2)
    
        return distance
    



