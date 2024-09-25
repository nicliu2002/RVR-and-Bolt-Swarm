import sys
import os
import time
import math
import random
from Swarm2 import Swarm2
from ViconLocator import ViconLocator
from spherov2 import scanner
from spherov2.toy.bolt import BOLT
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color
from RVRController import RVR_Controller

controller = RVR_Controller("192.168.68.57","rvr5")

locator = ViconLocator(log_file="vicon bolt test.txt")


print("setting speed to 255")

def get_distance(x1, y1, x2, y2):
    return math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

def get_speed_heading(self):
    print("getting heading from vicon")
    lastX, lastY = self.Locator.get_position(id)
    time.sleep(0.25)
    nowX, nowY = self.Locator.get_position(id)
    return (math.sqrt((nowX-lastX)**2 + (nowY-lastY)**2)),(math.degrees((math.atan2((nowY-lastY), (nowX-lastX)))))

try:

    timeCount = 0 # sets the time count to 0
    x,y = locator.get_position(id)
    theta = controller.get_heading() # gets robot initial heading

    # print("current location data: X: " + str(x) + "     Y: " + str(y) + "     Theta: " + str(theta))

    target_x = -50 # converts x grid coordinates to local positioning system coordinates
    target_y = 50 # converts y grid coordinates to local positioning system coordinates

    # print("target data is:      target x: " + str(target_x) + "     target y: " + str(target_y))

    dist_error = get_distance(x, y, target_x, target_y) # gets initial euclidean distance to target

    while dist_error >= 1:
        
        
        
        # loop continually gets distance and heading to target until robot is within 3 cm of target 
        
        timeCount += 1
        progressiveX, progressiveY = locator.get_position(id)  
        dist_error = get_distance(progressiveX, progressiveY, target_x, target_y)
        theta_error = 180*math.atan2(target_x-progressiveX,target_y-progressiveY )/math.pi
        print(f"{progressiveX=}\t{progressiveY=}\t{theta_error=}\t{dist_error=}")  
        controller.set_heading(int(theta_error))
        time.sleep(0.01) # small sleep prevents over correction
        controller.set_speed(50) # robot moves at minimal speed to overcome carpet friction to prevent over correction
        # print("moving location data: X: " + str(progressiveX) + "     Y: " + str(progressiveY) + "   Theta: " + str(theta_error) + "    dist_error: " + str(dist_error))
        # moves until distance error is less than 5
        
        if dist_error < 3: # if statement triggers on reaching target location and returns successful "moved" string
            
            # print("New Current Positions: " + "     X: " + str(progressiveX) + "      Y: " + str(progressiveY))
            controller.set_speed(0)
            controller.set_heading(0)  
            print("at location")            
        
        time.sleep(0.05)
        
except KeyboardInterrupt:
        print('Main Interrupted')
        controller.set_speed(0)
        controller.set_heading(0)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


def get_distance(x1, y1, x2, y2):
    return math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

def get_speed_heading(self):
    print("getting heading from vicon")
    lastX, lastY = self.Locator.get_position(id)
    time.sleep(0.25)
    nowX, nowY = self.Locator.get_position(id)
    return (math.sqrt((nowX-lastX)**2 + (nowY-lastY)**2)),(math.degrees((math.atan2((nowY-lastY), (nowX-lastX)))))

locator = ViconLocator(log_file="vicon bolt test.txt")

id = "SB-CE32"

toy = scanner.find_toy(toy_name=id)
try:
    with SpheroEduAPI(toy) as controller:

        timeCount = 0 # sets the time count to 0
        x,y = locator.get_position(id)
        theta = controller.get_heading() # gets robot initial heading

        # print("current location data: X: " + str(x) + "     Y: " + str(y) + "     Theta: " + str(theta))

        target_x = -50 # converts x grid coordinates to local positioning system coordinates
        target_y = 50 # converts y grid coordinates to local positioning system coordinates

        # print("target data is:      target x: " + str(target_x) + "     target y: " + str(target_y))

        dist_error = get_distance(x, y, target_x, target_y) # gets initial euclidean distance to target

        while dist_error >= 1:
            
            
            
            # loop continually gets distance and heading to target until robot is within 3 cm of target 
            
            timeCount += 1
            progressiveX, progressiveY = locator.get_position(id)  
            dist_error = get_distance(progressiveX, progressiveY, target_x, target_y)
            theta_error = 180*math.atan2(target_x-progressiveX,target_y-progressiveY )/math.pi
            print(f"{progressiveX=}\t{progressiveY=}\t{theta_error=}\t{dist_error=}")  
            controller.set_heading(int(theta_error))
            time.sleep(0.01) # small sleep prevents over correction
            controller.set_speed(50) # robot moves at minimal speed to overcome carpet friction to prevent over correction
            # print("moving location data: X: " + str(progressiveX) + "     Y: " + str(progressiveY) + "   Theta: " + str(theta_error) + "    dist_error: " + str(dist_error))
            # moves until distance error is less than 5
            
            if dist_error < 3: # if statement triggers on reaching target location and returns successful "moved" string
                
                # print("New Current Positions: " + "     X: " + str(progressiveX) + "      Y: " + str(progressiveY))
                controller.set_speed(0)
                controller.set_heading(0)  
                print("at location")            
            
            time.sleep(0.05)
            
except KeyboardInterrupt:
        print('Main Interrupted')
        with SpheroEduAPI(toy) as controller:
            controller.set_speed(0)
            controller.set_heading(0)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)