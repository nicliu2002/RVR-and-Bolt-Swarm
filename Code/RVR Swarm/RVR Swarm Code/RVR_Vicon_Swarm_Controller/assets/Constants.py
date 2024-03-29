"""
Initialization and Configuration

This section of the code handles the initialization and configuration of various parameters and settings for a simulation environment. 
It encompasses the loading of configuration data from a JSON file, setting up constants and variables, and preparing the simulation environment.

@ author    Reda Ghanem
@ version   1.0
"""

# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #

import json                         # for JSON handling
import os                           # for operating system related functionalities
import math                         # for mathematical operations
import sys                          # for system-specific parameters and functions


# very important if you will run on (Local PC), you can acces all files from current_directory
current_directory, filename = os.path.split(os.path.abspath(__file__))  # Get the current directory and the filename of the current file
sys.path.append(current_directory)      # Append the current directory to the system path
os.chdir(current_directory)             # Change the current working directory to the current directory

from Helper_Functions import *

# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

# Load data from the JSON file, .. becaise its in prevoius folder of CURRENT_DIRECTORY
with open('inputs_data.json', 'r') as json_file:
    loaded_data = json.load(json_file)           

# Extract the values from the JSON data and store them in variables
# Behaviors Weights, numbers in range [0,1]
ALIGNMENT_WEIGHT            = loaded_data['ALIGNMENT_WEIGHT']
COHESION_WEIGHT             = loaded_data['COHESION_WEIGHT']
SEPARATION_WEIGHT           = loaded_data['SEPARATION_WEIGHT']
WALL_AVOIDANCE_WEIGHT       = loaded_data['WALL_AVOIDANCE_WEIGHT']
# Behaviors Range, All Next Distance in meter, numbers in range [0, Max range for the Emitter and Receiver]
ALIGNMENT_RANGE             = loaded_data['ALIGNMENT_RANGE']
COHESION_RANGE              = loaded_data['COHESION_RANGE']
SEPARATION_RANGE            = loaded_data['SEPARATION_RANGE']
WALL_AVOIDANCE_RANGE        = loaded_data['WALL_AVOIDANCE_RANGE']
# Robot Speed
MAX_LINEAR_SPEED            = loaded_data['MAX_LINEAR_SPEED']               # Maximium robot linear speed m/s
MIN_LINEAR_SPEED            = loaded_data['MIN_LINEAR_SPEED']               # Minimum robot linear speed m/s
MAX_ANGULAR_SPEED           = loaded_data['MAX_ANGULAR_SPEED']              # Maximium robot angular speed rad/s
MIN_ANGULAR_SPEED           = loaded_data['MIN_ANGULAR_SPEED']              # Minimum robot angular speed rad/s
# Environmental Setup
ARENA_WIDTH                 = loaded_data['ARENA_WIDTH']                    # RectangleArena Width, (in meters)
ARENA_LENGTH                = loaded_data['ARENA_LENGTH']                   # RectangleArena Length, (in meters)
CELL_SIZE                   = loaded_data['CELL_SIZE']                      # Cell Size, (in meters)
NUM_OF_ROBOTS               = loaded_data['NUM_OF_ROBOTS']                  # Number of robots
ITERATIONS_PER_SECOND       = loaded_data['ITERATIONS_PER_SECOND']          # Number of iterations per second
MAX_STOP_TIME               = loaded_data['MAX_STOP_TIME']                  # Stop simulation after ... sec
PRINT_CONSOLE_RESULT        = loaded_data["PRINT_CONSOLE_RESULT"]           # print results in console if true 

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# Robot body dimensions

robot_width =  0.216         # Width of RVR (in meters)
robot_length = 0.185         # Length of RVR (in meters)
robot_height = 0.114         # Height of RVR (in meters)
ROBOT_SIZE = [robot_width, robot_length]         # make ROBOT_SIZE in cm and int

ROBOT_RADIUS = 0.5 * math.sqrt(ROBOT_SIZE[0]**2 + ROBOT_SIZE[1]**2)

