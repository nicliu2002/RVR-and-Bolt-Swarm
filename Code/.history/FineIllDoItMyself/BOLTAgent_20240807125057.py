"""
Agent Class

The Agent class is responsible for controlling the RVR robot's movements and behaviors in a swarm robotics scenario. 
It utilizes the Boid algorithm to calculate linear and angular velocities, communicates with other robots using the 
Communication_Handler class, and receives position updates from VICON. This class serves as the core component for 
coordinating the actions of the RVR robot in a multi-robot system.

@Project    RVR Vicon Swarming Project
@author     Reda Ghanem
@version    1.0
"""


import sys
import math
import time
import threading
import signal
import json

# for BOLT

from spherov2 import scanner
from spherov2.sphero_edu import EventType, SpheroEduAPI


# if we run code from /home/pi/sphero-sdk-raspberrypi-python/projects/ folder use:
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# if we run code from /home/pi/RVR folder use:
sys.path.append('/home/pi/sphero-sdk-raspberrypi-python/')

# For Swarm
from assets import Constants as Cons              # for Constants and Global variables
from assets.Boid import Boid
from assets.Helper_Functions import *             # Import Helper_Functions.py from the parent directory


# Define Agent class for controlling the RVR robot.
class BOLTAgent:
    logging = True
    
    locator_handler_x = 0
    locator_handler_y = 0
    
    # Initializes the Agent instance with the given parameters.
    def __init__(self, start_position, start_heading_angle, robot_size, robot_id, robot_name):
        
        self.robot_name = robot_name
        
        # object from boid to compute next linear_velocity and angular_velocity
        self.boid = Boid(start_position, start_heading_angle, robot_size, robot_id)

        self.command_time_step = 50 # it mean run command each command_time_step ms
        
        self.localNeighbours = {} # internal dictionary for BOLT to keep track of other BOLTs and RVR
        # local neighbours is a dictionary with keys corresponding to boid IDs and values corresponding to boid pos and vel
        self.localNeighbours[self.boid.id] = [self.boid.x,self.boid.y,self.boid.delta_x,self.boid.delta_y] 
        
        # initalise the json objects 
        
        json_object = json.dumps(self.localNeighbours, indent=4)
        
        with open("localData.json", "w") as outfile:
            outfile.write(json_object)
            print("Wrote to json: " + str(json_object))  

        
        print("Looking for bolt: " + self.robot_name)
        
        self.toy = scanner.find_toy(toy_name=self.robot_name)
        print("scanning....")
        time.sleep(5)
        
        print("Found bolt: " + str(self.toy))


        # ANGULAR_SPEED need to divide by (angle_rat), to make change of ANGULAR_SPEED every 100 step correct as target value you want
        # for ex. if we want 0.9 rad/s this mean that we need to use 0.009 so after 100 step (one sec) we reach 0.9 rad/sec
        angle_rat = 1000/self.command_time_step
        Cons.MAX_ANGULAR_SPEED /= angle_rat
        Cons.MIN_ANGULAR_SPEED /= angle_rat


        # Handle termination signals (Ctrl+C, etc.)
        signal.signal(signal.SIGINT, self.programe_termination)
        signal.signal(signal.SIGTERM, self.programe_termination)
        
        print("bolt agent intialisation: success")

    # Start signal to deal with type identification
    def start_signal(self):
        self.run_agent()
        
        
    # Handler for locator sensor data
    def locator_handler(self):
        
        print("BOLT locator handler function")
        
        # Opening JSON file
        with open('location.json', 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            print("Read from json: " + str(json_object))

            
        position = json_object[self.robot_name]
        self.locator_handler_x = position[0]
        self.locator_handler_y = position[1]

        # round values to make numbers same in all OS (Windows, Linux)
        
        self.locator_handler_x , self.locator_handler_y = [round(v, 5) for v in [self.locator_handler_x, self.locator_handler_y] ]

    # updates local .json files with robot locations
    
    def updateLocalData(self):
        
        print("BOLT update local data function")
        
        with open("localData.json", "r") as openfile:
            jsonData = json.load(openfile)
            print("Read from json: " + str(jsonData))
            
        self.localNeighbours = jsonData        
        self.localNeighbours[self.boid.id] = [self.boid.x,self.boid.y,self.boid.delta_x,self.boid.delta_y]   
        json_object = json.dumps(self.localNeighbours, indent=4)
        
        with open("localData.json", "w") as outfile:
            outfile.write(json_object)
            print("Wrote to json: " + str(jsonData))

    # Function to Collect neighbor IDs, positions, velocities data by Receiving data from other robots
    def receive_information(self):
        print("BOLT receive information function")
        
        
        
        with open('location.json', 'r') as openfile:
            # Reading from json file
            print("reading from json file")
            json_object = json.load(openfile)
            print("read: " + str(json_object))
        
        for key, data in json_object.items():
            if key != self.boid.id:
                position = [float(data[0]), float(data[1])]
                velocity = [float(data[2]), float(data[3])]
    
                self.boid.neighbors_IDs.append(key)
                self.boid.neighbors_positions.append(position)
                self.boid.neighbors_velocities.append(velocity)
        
        for key, data in self.localNeighbours.items():
            if key != self.boid.id:
                position = [float(data[0]), float(data[1])]
                velocity = [float(data[2]), float(data[3])]
    
                self.boid.neighbors_IDs.append(key)
                self.boid.neighbors_positions.append(position)
                self.boid.neighbors_velocities.append(velocity)
                
    # Function Runs the main agent loop, controlling the RVR's movements and behaviors.
    
    def run_agent(self):
        
        time_step = 0

        
        while True:
            try:

                # First step:
                # Step [01]: get current position from vicon
                if self.locator_handler_x != None and self.locator_handler_y != None:
                    # self.locator_handler_x, self.locator_handler_y = self.get_position_values_after_offset([self.locator_handler_x, self.locator_handler_y, 0], Cons.GPS_OFFSET_X, Cons.GPS_OFFSET_Y)
                    self.boid.x = self.locator_handler_x
                    self.boid.y = self.locator_handler_y
                
                self.boid.position = [self.boid.x, self.boid.y]          # boid position as list [x, y]
                # update heading_angle by adding current angular_velocity value
                self.boid.heading_angle += self.boid.angular_velocity
                self.boid.heading_angle = round(self.boid.heading_angle, 5)         # round values to make numbers same in all OS (Windows, Linux)

                # Second Step: 
                # Update linear and angular velocities here based on boid rules
                self.updateLocalData()
                # Step [3.4]: For each (Robot) send_information to server_data
                # we skip this step and we will use robots list in function receive_information
                # Step [3.5]: For each (Robot) receive_information
                self.receive_information()

                # Step [3.7]: For each (Robot) compute the next step by update_velocity before moving any robot from the boid code
                self.boid.update_velocity()

                # Third Step:
                # Step [3.8]: For each (Robot) moving now
                # Drive the BOLT robot based on linear_velocity and the heading_angle
                
                newSpeed =  int((self.boid.linear_velocity)*50)
                newHeading = int(math.degrees(self.boid.heading_angle))
                
                print("Updating BOLT with new SPeed: " + str(newSpeed) +"new Heading:  " + str(newHeading))
                
                with SpheroEduAPI(self.toy) as droid:            
                    droid.set_heading(newHeading)
                    time.sleep(0.5)
                    droid.set_speed(newSpeed)
                    time.sleep(0.5) 
                time_step += 1


                # # print some information
                # if time_step % 50 == 0:
                #     clear_console()
                #     print("------------------------------------------------")
                #     print("time_step             = " , time_step)
                #     print("RVR position          = " , self.boid.position)
                #     print("RVR heading_angle     = " , self.boid.heading_angle)
                #     print("RVR linear_velocity   = " , rvr_linear_velocity)
                #     print("RVR heading_angle     = " , rvr_heading_angle)

                if time_step == 100*Cons.MAX_STOP_TIME:
                    print("MAX_STOP_TIME reached: Stop")
                    break

            
            except Exception as e:
                print(e)
                self.programe_termination("Exception", "")


    # Function Handle termination signals gracefully.
    def programe_termination(self, signum, frame):
        """
        Handle termination signals gracefully.

        Args:
            signum (int): The signal number.
            frame (frame): The current stack frame.
        """
        print(f"Termination signal received (Signal {signum}). Cleaning up...")



