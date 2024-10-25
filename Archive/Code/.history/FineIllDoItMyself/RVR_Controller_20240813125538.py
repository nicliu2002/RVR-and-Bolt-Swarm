import sys
import os
import math
import time
import signal
import random
from threading import Thread, Lock

# if we run code from /home/pi/sphero-sdk-raspberrypi-python/projects/ folder use:
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# if we run code from /home/pi/RVR folder use:
sys.path.append('/home/pi/sphero-sdk-raspberrypi-python/')

# running code from laptop to test compile
# sys.path.append(r"C:\Users\nicli\Documents\Thesis\Code\sphero-sdk-raspberrypi-python\sphero-sdk-raspberrypi-python")

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

from RVRAgent import RVRAgent
from BOLTAgent import BOLTAgent
from ViconLocator import ViconLocator

def main():
    # This program moves the robot using linear and angular velocities.

    try:
        agentList = []
        agent_threads = []
        
        
        ViconInstance = ViconLocator(Cons.RVR_name, Cons.BOLT_ID_list)
        
        # Get starting values from observer
        start_position = [0 , 0]
        start_heading_angle = 0             # put all robots face alighn with x Axis
        robot_size = Cons.ROBOT_SIZE
        bolt_size = Cons.BOLT_SIZE
        robot_id = Cons.RVR_name

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
        
        bolt_list = Cons.BOLT_ID_list
        RVR = RVRAgent(start_position, start_heading_angle, robot_size, robot_id, robot_ip, robot_id_name, all_robtos_ips)
        agentList.append(RVR)
        
        for bolt in bolt_list:
            boltAgent = BOLTAgent(start_position, start_heading_angle, bolt_size, bolt, bolt)
            print(type(boltAgent))
            agentList.append(boltAgent)
        
        print(str(agentList))
        
        print("------------------ creating threads ------------------")
        
        for agent in agentList:
            if type(agent) == 'BOLTAgent.BOLTAgent':
                thread = Thread(target=agent.start_signal)
                print("created: " + str(type(agent)) + " thread: success")
            else: 
                thread = Thread(target=agent.start_signal)
                print("created: " + str(type(agent)) + " thread: success")
            agent_threads.append(thread)    
            print(" --- " )
            
        print("\n initalising threads")
        for thread in agent_threads:
            thread.start()
            print(" --- ")
        for thread in agent_threads:
            thread.join()
            print(" --- ")
                

    except KeyboardInterrupt:
        print('\nProgram terminated with keyboard interrupt.')
    except Exception as e:
        print(e)

    finally:
        # Clean up and close the RVR
        print("Program ended.") 

if __name__ == '__main__':
    main()