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
import random
from threading import Thread, Lock


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

# for sphero BOLT

from spherov2 import scanner
from spherov2.toy.bolt import BOLT
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color

# For Vicon
from pylsl import resolve_stream, StreamInlet

# For Swarm
from assets import Constants as Cons              # for Constants and Global variables
from assets.Boid import Boid
from assets.Helper_Functions import *             # Import Helper_Functions.py from the parent directory
from Communication_Handler import Communication_Handler


# Define Agent class for controlling the RVR robot.
class Agent:
    logging = True
    
    
    # For VICON
    vicon_enable = True
    vicon_sr = 100      # simpling rate (how time recive in sec)
    locator_handler_x = None
    locator_handler_y = None

    
    # Initializes the Agent instance with the given parameters.
    def __init__(self, start_position, start_heading_angle, robot_size, robot_id, robot_ip, robot_name, all_robtos_ips, bolt_IDs):
        
        self.robot_name = robot_name

        # object from boid to compute next linear_velocity and angular_velocity
        self.boid = Boid(start_position, start_heading_angle, robot_size, robot_id)

        self.command_time_step = 50 # it mean run command each command_time_step ms

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
        
        # --------------- Start new section for bolts ----------------- #
        
        # add sphero BOLTs to the robot
        self.robot_bolts = []
        self.toys = scanner.find_toys(toy_names = self.robot_bolts)
        print('found ' + str(len(self.toys)) + ' toys.')
        

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

        # For VICON
        if self.vicon_enable == True:
            self.vicon_update_lock = threading.Lock()         # lock thrid concruntly
            self.init_lsl()

        # In Python, __init__ methods of classes cannot be declared as asynchronous (async).
        # so we create a separate asynchronous method that performs the necessary setup tasks 
        # then we call this method in the __init__ method.
        self.loop.run_until_complete(self.async_init() )

    # Asynchronously initializes the RVR by waking it up and performing initial setup.
    async def async_init(self):
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

        if self.vicon_enable == False:
            # Add a handler for the locator sensor data
            await self.rvr.sensor_control.add_sensor_data_handler(
                service=RvrStreamingServices.locator,
                handler=self.locator_handler
            )


            ## Start streaming sensor data with a specified interval (10ms), 
            ## The default value is 33 ms , we can change it from file sphero_sdk/common/sensors/sensor_streaming_control.py
            ## then change variable min_streaming_interval to 10
            await self.rvr.sensor_control.start(interval=self.command_time_step)

            # Reset the x and y position of the robot
            await self.rvr.reset_locator_x_and_y()
            

        await asyncio.sleep(1)                  # Give RVR time before start runing

    # Function to Handles the battery percentage information received from the RVR.
    async def battery_percentage_handler(self):
        battery_percentage = await self.rvr.get_battery_percentage()
        print('Battery percentage: ', battery_percentage)

    # Thread For VICON to update each 10 ms
    def init_lsl(self):
        print("looking for Vicon lsl stream...")
        streams = resolve_stream('name', self.robot_name)
        print(f"Stream found for {self.robot_name}")
        # create a new inlet to read from the stream
        self.inlet = StreamInlet(streams[0])
        threading.Thread(target=self.vicon_locator).start()

    # Get all robots positions, ip , name from VICON
    def vicon_locator(self):
        while True:
            try:
                # get a new sample (you can also omit the timestamp part if you're not
                # interested in it)
                sample, timestamp = self.inlet.pull_sample()
            
                with self.vicon_update_lock:
                    if sample[2] == 0:
                        self.locator_handler_x = sample[0] / 1000               # /1000 to covert from mm to meters
                        self.locator_handler_y = sample[1] / 1000               # /1000 to covert from mm to meters
                        # round values to make numbers same in all OS (Windows, Linux)
                        self.locator_handler_x , self.locator_handler_y = [round(v, 5) for v in [self.locator_handler_x, self.locator_handler_y] ]

            except Exception as e:
                print(e)
                pass
            finally:
                time.sleep(1 / self.vicon_sr)

    # Handler for locator sensor data
    async def locator_handler(self, locator_data):

        # print('Locator data response: ', locator_data)
        # Calculate the target position 50cm in front of the robot
        locator = locator_data["Locator"]
        self.locator_handler_x = locator["Y"] 
        self.locator_handler_y = -locator["X"]

        # round values to make numbers same in all OS (Windows, Linux)
        self.locator_handler_x , self.locator_handler_y = [round(v, 5) for v in [self.locator_handler_x, self.locator_handler_y] ]

    # Function to get position values after applying offset
    def get_position_values_after_offset(self, robot_position, GPS_OFFSET_X, GPS_OFFSET_Y):

        # Apply offset to robot_position values to make all x and y positive so (x=0, y=0) in left bottom corner
        robot_position[0] += GPS_OFFSET_X
        robot_position[1] += GPS_OFFSET_Y
        robot_position = [robot_position[0]  , robot_position[1]  , robot_position[2]]
   
        robot_position = robot_position[:2]             # we just need x, y and ignore z
        return robot_position
    
    # Function to Broadcast robot_ID, position, velocity
    def send_information(self):
        data = f"{self.boid.id},{self.boid.x},{self.boid.y},{self.boid.delta_x},{self.boid.delta_y}"
        self.communication_handler.send_message_to_all(data)        # Send information to all connected robots

    # Function to layer on additional BOLT information into boids algorithm - identifiable by BOLT name 
    # Subject to change, BOLT/RVR identifier in message -> different size (velocity should not matter with code)
        
    def receive_BOLT_information(self):
        for count, droid in enumerate(self.toys):
            self.boid.neighbors_IDs.append(self.robot_bolts[count])
            self.boid.neighbors_positions.append()

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
        
        receive_BOLT_information(self)
    


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
        self.communication_handler.handle_termination()
        self.animate_termination()
        

class BOLTLocation:
    def __init__(self, toy, mas,subject_ind):
        self.mas = mas
        self.toy = toy 
        self.subject_ind = subject_ind
        self.WAYPOINT_RANGE = 50
    def getPosition(self):
        self.mas.vicon_client.GetFrame()
        client = self.mas.vicon_client
        subject_names = client.GetSubjectNames()
        segment_names = client.GetSegmentNames(subject_name[subject_ind])
        global_position = client.GetSegmentGlobalTranslation(subject_name[subject_ind], segment_name[subject_ind])
        global_orientation = client.GetSegmentGlobalRotationEulerXYZ(subject_name[subject_ind], segment_name[subject_ind])
        xVicon = global_position[0][0]/10
        yVicon = global_position[0][1]/10
        data = str(segment_names) + " , " + str(xVicon) + ", " + str(yVicon) + ", " + str(xSphero) + ", " + str(ySphero)
        self.mas.log_data(data+"\n")
        xvic, yvic, zvic = global_position[0]
        rollvic, pitchvic, yawvic = global_orientation[0]
        return xVicon , yVicon

class BOLTAgent:

    def __init__(self, toy, mas, xPos, yPos):
        self.mas = mas
        self.toy = toy 
        self.xPos = xPos
        self.yPos = yPos
        self.WAYPOINT_RANGE = 50

    def run_agent(self):
        while(True):    
            for count in range(0, 120):
                speed = self.sphero.get_speed()
                theta = self.sphero.get_heading() 
                xVicon = xPos              
                yVicon = yPos                                  
                target_x = xVicon + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                target_y = yVicon + self.WAYPOINT_RANGE*math.cos(math.radians(theta))
                #### Wall Reflection: Robots move in a 240*120 rectangle area
                if target_x > 120 or target_x < -120:
                    self.sphero.set_heading(-theta)
                    theta = -theta	  
                    target_x = xVicon + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                    target_y = yVicon + self.WAYPOINT_RANGE*math.cos(math.radians(theta))    
                
                if target_y > 120 or target_y < 0:
                    self.sphero.set_heading(180-theta)
                    theta = 180-theta
                    target_x = xVicon + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                    target_y = yVicon + self.WAYPOINT_RANGE*math.cos(math.radians(theta))         
                time.sleep(0.1)  
                            





def main():
    
    # This program moves the robot using linear and angular velocities.

    agent = None
    try:

        # Get starting values from observer
        start_position = [0 , 0]
        start_heading_angle = 0             # put all robots face alighn with x Axis
        robot_size = Cons.ROBOT_SIZE
        robot_id = 1

        # for Comunications
        # Define the IP address for Robot
        # robot_ip = "192.168.0.103"            # for Home Wifi
        # robot_ip = "192.168.43.116"           # for Mobile Wifi
        robot_ip = Cons.rvr_ip              # for RAS Wifi
        
        robot_id_name = Cons.RVR_name
        
        # List of all Robots IP addresses
        # all_robtos_ips = ["192.168.0.103", "192.168.0.104", "192.168.0.105"]
        # all_robtos_ips = ["192.168.43.192", "192.168.43.200", "192.168.43.116"]
        all_robtos_ips = Cons.rvr_ip_list
        
        agentList = []  
        bolt_IDs = ['SB-8427','SB-41F2'] 
        toys = scanner.find_toys(toy_names=bolt_IDs)
        print('found ' + str(len(toys)) + ' toys.')
        agent_threads = []
        
        # setting up RVR thread
        
        selfAgent = Agent(start_position, start_heading_angle, robot_size, robot_id, robot_ip, robot_id_name, all_robtos_ips, bolt_IDs)
        agentList.append(selfAgent)
        
        for toy in toys:
            with SpheroEduAPI(self.toy) as self.sphero:
                time.sleep(5)
                theta = random.randint(-45, 45)
                self.sphero.set_heading(theta)
                self.sphero.set_speed(80) 
                boltAgent = Agent()
        
        for agent in agentList:
            thread = Thread(agent.loop.run_until_complete(agent.run_agent()))
            agent_threads.append(thread)
        
        sunject_ind = 0
        for toy in toys:
            with SpheroEduAPI(self.toy) as self.sphero:
                agentPos = BOLTLocation(toy,mas,subject_ind)
                xPos , yPos = agentPos.getPosition()
                BOLTagent = BOLTAgent(toy, mas, xPos, yPos)
                BOLTthread = Thread(target=BOLTagent.run_agent)
                agent_threads.append(BOLTthread) 
                for i in agent_threads:
                    i.join()
                sunject_ind += 1 

    except KeyboardInterrupt:
        print('\nProgram terminated with keyboard interrupt.')
    except Exception as e:
        print(e)

    finally:
        # Clean up and close the RVR
        agent.loop.run_until_complete( agent.rvr.sensor_control.clear() )

        # Delay to allow RVR issue command before closing
        time.sleep(1)

        agent.loop.run_until_complete(agent.rvr.close())

        print("Program ended.")

if __name__ == '__main__':
    main()
