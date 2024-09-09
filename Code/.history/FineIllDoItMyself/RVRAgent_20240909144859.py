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


# if we run code from /home/pi/sphero-sdk-raspberrypi-python/projects/ folder use:
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# if we run code from /home/pi/RVR folder use:
sys.path.append('/home/pi/sphero-sdk-raspberrypi-python/')

# For sphero_sdk
import asyncio
from sphero_sdk import SerialAsyncDal
from sphero_sdk import SpheroRvrAsync
from sphero_sdk import RvrLedGroups             # for LED
from sphero_sdk import RvrStreamingServices     # For locater handler 

# For Vicon
from pylsl import resolve_stream, StreamInlet

# For Swarm
from assets import Constants as Cons              # for Constants and Global variables
from assets.Boid import Boid
from assets.Helper_Functions import *             # Import Helper_Functions.py from the parent directory
from Communication_Handler import Communication_Handler


# Define Agent class for controlling the RVR robot.
class RVRAgent:
    logging = True
    
    locator_handler_x = None
    locator_handler_y = None

    
    # Initializes the Agent instance with the given parameters.
    def __init__(self, start_position, start_heading_angle, robot_size, robot_id, robot_ip, robot_name, all_robtos_ips):
        
        self.robot_name = robot_name

        # object from boid to compute next linear_velocity and angular_velocity
        self.boid = Boid(start_position, start_heading_angle, robot_size, robot_id)

        self.command_time_step = 50 # it mean run command each command_time_step ms
        
        self.localNeighbours = {} # internal dictionary for BOLT to keep track of other BOLTs and RVR
        # local neighbours is a dictionary with keys corresponding to boid IDs and values corresponding to boid pos and vel
        self.localNeighbours[self.boid.id] = [self.boid.x,self.boid.y,self.boid.delta_x,self.boid.delta_y]   

        # ANGULAR_SPEED need to divide by (angle_rat), to make change of ANGULAR_SPEED every 100 step correct as target value you want
        # for ex. if we want 0.9 rad/s this mean that we need to use 0.009 so after 100 step (one sec) we reach 0.9 rad/sec
        angle_rat = 1000/self.command_time_step
        Cons.MAX_ANGULAR_SPEED /= angle_rat
        Cons.MIN_ANGULAR_SPEED /= angle_rat
        
        
        self.loop = asyncio.get_event_loop()
        self.rvr = SpheroRvrAsync(
            dal=SerialAsyncDal(
                self.loop
            )
        )



        # Get the robot's IP address and the IP addresses of all other robots in the swarm
        self.robot_neighbors_ips = []
        for ip in all_robtos_ips:
            if ip != robot_ip:
                self.robot_neighbors_ips.append(ip)

        # ----------------------------------------------------------- #
        # -------------- communication_handler ---------------------- #
        if len(self.robot_neighbors_ips) == 0:
            print("Note that robot_neighbors_ips is empty so robot will try to connect to a virtual default ip 0.0.0.0")
            self.robot_neighbors_ips = ["0.0.0.0"]

        # Create a communication_handler instance for Robot
        self.communication_handler = Communication_Handler(self.robot_name, robot_ip, self.robot_neighbors_ips)
        # Start communication
        self.communication_handler.start_communication()
        # ----------------------------------------------------------- #

        # Handle termination signals (Ctrl+C, etc.)
        signal.signal(signal.SIGINT, self.programe_termination)
        signal.signal(signal.SIGTERM, self.programe_termination)
        
        self.loop.run_until_complete(self.async_init())


    

        # In Python, __init__ methods of classes cannot be declared as asynchronous (async).
        # so we create a separate asynchronous method that performs the necessary setup tasks 
        # then we call this method in the __init__ method.

    def start_signal(self):
        print("start signal received on RVR")
        self.loop.run_until_complete(self.run_agent())

    # Asynchronously initializes the RVR by waking it up and performing initial setup.
    async def async_init(self):
        print("Initialising RVR")
        await self.rvr.wake()
        await asyncio.sleep(1)                  # Give RVR time to wake up

        await self.rvr.reset_yaw()              # set current head angle as zero

        print('Initial heading is ' + str(self.boid.heading_angle))
        
        # Instead of passing the handler to get_battery_percentage, you can call it separately
        await self.battery_percentage_handler()

        # turn off all leds light
        await self.rvr.set_all_leds(
            led_group=RvrLedGroups.all_lights.value,
            led_brightness_values=[color for _ in range(10) for color in [0, 0, 0]]
        )
            
        await asyncio.sleep(1)                  # Give RVR time before start runing
        print("RVR initialisation: success")

    # Function to Handles the battery percentage information received from the RVR.
    async def battery_percentage_handler(self):
        battery_percentage = await self.rvr.get_battery_percentage()
        print('Battery percentage: ', battery_percentage)

    # Handler for locator sensor data
    async def locator_handler(self):
        print("RVR locator handler function")

        # # ----------- commenting out location.json code for now -----------


        # # Opening JSON file
        # with open('location.json', 'r') as openfile:
        #     # Reading from json file
        #     json_object = json.load(openfile)
        #     print("read json as: " + str(json_object))
            
        # position = json_object[self.robot_name]
        
        position = Cons.location[self.boid.id][0]
        
        print("RVR position from json (locator handler) is: " + str(position))

        self.locator_handler_x = position[0]
        self.locator_handler_y = position[1]
        

        # round values to make numbers same in all OS (Windows, Linux)
        
        self.locator_handler_x , self.locator_handler_y = [round(v, 5) for v in [self.locator_handler_x, self.locator_handler_y] ]

    def updateLocalData(self):
        
        print("RVR Update local data function")
    
        Cons.location[self.boid.id] = [[self.boid.x,self.boid.y],[self.boid.delta_x,self.boid.delta_y]] 
        
        print(f"{Cons.location[self.boid.id]=}")

        # with open("localData.json", "r") as openfile:
        #     jsonData = json.load(openfile)
        #     print("read json as: " + str(jsonData))

        # self.localNeighbours = jsonData        
        # self.localNeighbours[self.boid.id] = [self.boid.x,self.boid.y,self.boid.delta_x,self.boid.delta_y]   
        # json_object = json.dumps(self.localNeighbours, indent=4)
        
        # with open("localData.json", "w") as outfile:
        #     outfile.write(json_object)
        #     print("wrote to json: " + str(json_object))

        

    # Function to Broadcast robot_ID, position, velocity
    def send_information(self):
        print("RVR sending information")
        data = str(Cons.location)       
        self.communication_handler.send_message_to_all(data)        # Send information to all connected robots

        

            

    # Function to Collect neighbor IDs, positions, velocities data by Receiving data from other robots
    def receive_information(self):
        # clear all old neighbors data
        self.boid.clear_neighbors_data()
                
        # Access a list of all last received messages from all senders
        last_received_messages = self.communication_handler.get_last_received_messages()
        # print("last_received_message= " ,last_received_messages)
        
        for sender_ip, last_received_message in last_received_messages:
            # print(f"Last received message from {sender_ip}: {last_received_message}")

            neighbors_data = last_received_message.split(',')
            robot_id = int(neighbors_data[0])
            print(robot_id)
            position = [float(neighbors_data[1]), float(neighbors_data[2])]
            velocity = [float(neighbors_data[3]), float(neighbors_data[4])]            
            self.boid.neighbors_IDs.append(robot_id)
            self.boid.neighbors_positions.append(position)
            self.boid.neighbors_velocities.append(velocity)
            
            # update each id for far neighbours to feed to BOLT through file
            
            Cons.farNeighbours[robot_id] = position + velocity

        
        # json_object = json.dumps(farNeighbours, indent=4)
        # with open("localData.json", "w") as outfile:
        #     outfile.write(json_object)
        
        self.localNeighbours = Cons.location
        
        for key, data in self.localNeighbours.items():
            if key != self.boid.id:
                self.boid.neighbors_IDs.append(key)
                self.boid.neighbors_positions.append(data[0])
                self.boid.neighbors_velocities.append(data[1])
        
                


    # Function Runs the main agent loop, controlling the RVR's movements and behaviors.
    async def run_agent(self):

        
        # The control system timeout can be modified to keep a command running longer or shorter
        # than the default 2 seconds.  This remains in effect until changed back,
        # or until a reboot occurs. Note that this is in (milliseconds).
        # we can restore default control system timeout by calling: await restore_default_control_system_timeout()
        await self.rvr.set_custom_control_system_timeout(command_timeout=self.command_time_step+30)
        
        # Start time steps with zero
        time_step = 0

        
        while True:
            try:

                # First step:
                self.locator_handler()
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
                self.send_information()

                # Step [3.5]: For each (Robot) receive_information
                self.receive_information()

                # Step [3.7]: For each (Robot) compute the next step by update_velocity before moving any robot
                self.boid.update_velocity()
                
                # Third Step:
                # Step [3.8]: For each (Robot) moving now
                # Drive the rvr robot based on linear_velocity and the heading_angle
                rvr_linear_velocity = self.boid.linear_velocity
                rvr_heading_angle = int(math.degrees(self.boid.heading_angle))     # convert from radians to degree (# Valid heading values are [-179..+180])                
                
                if time_step % 1 == 0 or time_step < 100 :
                    await self.rvr.drive_with_yaw_si(
                        linear_velocity = rvr_linear_velocity,      # (float): Linear velocity target in m/s. Positive is forward, negative is backward.
                        yaw_angle = rvr_heading_angle,              # (float): Valid yaw values are traditionally [-179..+180], but will continue wrapping outside of that range
                        timeout = None
                    )

                # Step [3.10]:  10 ms delay per step, Delay to allow RVR to drive
                await asyncio.sleep(self.command_time_step/1000)

                # Step [3.11]:  increment steps by one
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
                print("RVR Exception",e)
                self.programe_termination("Exception", "")


    # Function Handle termination signals gracefully.
    def programe_termination(self, signum, frame):
        """
        Handle termination signals gracefully.

        Args:
            signum (int): The signal number.
            frame (frame): The current stack frame.
        """
        print(f"RVR Termination signal received (Signal {signum}). Cleaning up...")
        self.communication_handler.handle_termination()
        self.animate_termination()
        


