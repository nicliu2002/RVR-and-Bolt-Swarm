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


class Boid_BOLT:

    def __init__(self, swarm, viconInstance, id):
        self.swarm = swarm
        self.toy = swarm.get_next_toy()
        self.WAYPOINT_RANGE = 50
        self.Rc = 100
        self.Ra = 100
        self.Rs = 25
        self.Wc = 0.02
        self.Wa = 0.02
        self.Ws = 0.01
        self.vision_theta = 360
        self.Vmin = 70
        self.Vmax = 80
        self.Locator = viconInstance
        self.id = id
        
    def calculate_vel(self,boid):
        print("calculating velocity from encoders, units in cm/s, converted to mm/s")
        deltaX = boid.get_velocity()['x']
        deltaY = boid.get_velocity()['y']
        return 10*(math.sqrt(deltaX**2 + deltaY**2))   
    
    def calculate_heading(self):
        print("getting heading from vicon")
        lastX, lastY = self.Locator.get_position(self.id)
        time.sleep(0.5)
        nowX, nowY = self.Locator.get_position(self.id)
        return(math.degrees((math.atan2((nowY-lastY), (nowX-lastX)))))
    
    def run_boid(self, delay):
        with SpheroEduAPI(self.toy) as boid:
            time.sleep(5)
            self.swarm.add_boid(boid)
            boid.set_speed(0)
            boid.set_heading(0)
            try:
                for count in range(0, 240):
                    # current position and orientation of robot 480
                    x, y =  self.Locator.get_position(self.id)
                    velocity = self.calculate_vel(boid)
                    theta = boid.get_heading()
                    
                    print("error in heading is: ")
                    theta_error = abs(theta - self.calculate_heading())
                    print(f"{theta_error}")
                    
                    data = str(time.time_ns()) + ", " + self.toy.name + ", " + str(x) + ", " + str(y) + ", " + str(velocity) + ", " + str(theta) + ", "
                   
                    # modify target according to cohesion and alignment rules
                    c_com = self.swarm.get_neighbourhood_com(x, y, self.Rc, self.vision_theta)
                    s_com = self.swarm.get_neighbourhood_com(x, y, self.Rs, self.vision_theta)
                    align = self.swarm.get_neighbourhood_align(x, y, self.Ra, self.vision_theta)
                    forces = [[velocity*math.sin(math.radians(theta)), velocity*math.cos(math.radians(theta))]]
                    # print('speed ' + str(speed) + ' ' + str(theta))
                    weights = [1]
                    print("Align")
                    print(len(align))
                    if len(align) > 0:
                        forces.append([align[0], align[1]])
                        weights.append(self.Wa)
                        data = data + str(self.Wa*align[0]) + ", " + str(self.Wa*align[1]) + ", "
                    else:
                        data = data + "0, 0, "
                    print("coh")
                    print(len(c_com))
                    if len(c_com) > 0:                      
                        forces.append([c_com[0]-x, c_com[1]-y])
                        weights.append(self.Wc)
                        data = data + str(self.Wc*(c_com[0]-x)) + ", " + str(self.Wc*(c_com[1]-y)) + ", "
                    else:
                        data = data + "0, 0, "
                    print("Sep")
                    print(len(s_com))
                    if len(s_com) > 0:                
                        forces.append([x-s_com[0], y-s_com[1]])
                        weights.append(self.Ws)
                        data = data + str(self.Ws*(x-s_com[0])) + ", " + str(self.Ws*(y-s_com[1])) + ", "
                    else:
                        data = data + "0, 0, "
                    if len(align) > 0:
                        data = data + str(align[2]) + ", "
                    else:
                        data = data + "0, "
                    if len(c_com) > 0:
                        data = data + str(c_com[2]) + ", "
                    else:
                        data = data + "0, "
                    if len(s_com) > 0:
                        data = data + str(s_com[2]) + "\n"
                    else:
                        data = data + "0\n"  
                    self.swarm.log_data(data)
                 
                    combined_vel = Swarm2.weighted_sum_forces(forces, weights)
                    # print('vx vy ' + str(combined_vel[0]) + ', ' + str(combined_vel[1]))
                    combined_speed = math.sqrt(combined_vel[0]*combined_vel[0] + combined_vel[1]*combined_vel[1])
                    combined_head = math.degrees(math.atan2(combined_vel[0], combined_vel[1]))
                    # print('comb speed ' + str(combined_speed) + ' ' + str(combined_head))                
                    boid.set_heading(int(combined_head))
                    theta = combined_head

                    if combined_speed > self.Vmin and combined_speed < self.Vmax:
                        boid.set_speed(int(combined_speed))
                    elif combined_speed < self.Vmin:
                        boid.set_speed(self.Vmin)
                    else:
                        boid.set_speed(self.Vmax)
                                   
                    # calculate a predicted target 50cm in front of self
                    waypoint_x = boid.get_location()['x']
                    waypoint_y = boid.get_location()['y']
                    theta = boid.get_heading()                  
                    target_x = waypoint_x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                    target_y = waypoint_y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))
                   
                    # wall reflection if target will be 'out of bounds'
                    if target_x > 100 or target_x < -100:
                        boid.set_heading(-theta)
                        theta = -theta
                        target_x = waypoint_x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                        target_y = waypoint_y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))    
 
                    if target_y > 100 or target_y < 0:
                        boid.set_heading(180-theta)
                        theta = 180-theta
               
                    time.sleep(0.15)
            except KeyboardInterrupt:
                print('Interrupted')
                


class Boid_RVR:

    def __init__(self, swarm, viconInstance, id):
        self.swarm = swarm
        self.toy = swarm.get_next_toy()
        self.WAYPOINT_RANGE = 50
        self.Rc = 100
        self.Ra = 100
        self.Rs = 25
        self.Wc = 0.02
        self.Wa = 0.02
        self.Ws = 0.01
        self.vision_theta = 360
        self.Vmin = 70
        self.Vmax = 80
        self.Locator = viconInstance
        self.id = id
        self.RVR_Controller = RVR_Controller('192.168.')
        
    def calculate_vel(self,boid):
        print("calculating velocity from encoders, units in cm/s, converted to mm/s")
        deltaX = boid.get_velocity()['x']
        deltaY = boid.get_velocity()['y']
        return 10*(math.sqrt(deltaX**2 + deltaY**2))   
    
    def calculate_heading(self):
        print("getting heading from vicon")
        lastX, lastY = self.Locator.get_position(self.id)
        time.sleep(0.5)
        nowX, nowY = self.Locator.get_position(self.id)
        return(math.degrees((math.atan2((nowY-lastY), (nowX-lastX)))))
    
    def run_boid(self, delay):
        with SpheroEduAPI(self.toy) as boid:
            time.sleep(5)
            self.swarm.add_boid(boid)
            boid.set_speed(0)
            boid.set_heading(0)
            try:
                for count in range(0, 240):
                    # current position and orientation of robot 480
                    x, y =  self.Locator.get_position(self.id)
                    velocity = self.calculate_vel(boid)
                    theta = boid.get_heading()
                    
                    print("error in heading is: ")
                    theta_error = abs(theta - self.calculate_heading())
                    print(f"{theta_error}")
                    
                    data = str(time.time_ns()) + ", " + self.toy.name + ", " + str(x) + ", " + str(y) + ", " + str(velocity) + ", " + str(theta) + ", "
                   
                    # modify target according to cohesion and alignment rules
                    c_com = self.swarm.get_neighbourhood_com(x, y, self.Rc, self.vision_theta)
                    s_com = self.swarm.get_neighbourhood_com(x, y, self.Rs, self.vision_theta)
                    align = self.swarm.get_neighbourhood_align(x, y, self.Ra, self.vision_theta)
                    forces = [[velocity*math.sin(math.radians(theta)), velocity*math.cos(math.radians(theta))]]
                    # print('speed ' + str(speed) + ' ' + str(theta))
                    weights = [1]
                    print("Align")
                    print(len(align))
                    if len(align) > 0:
                        forces.append([align[0], align[1]])
                        weights.append(self.Wa)
                        data = data + str(self.Wa*align[0]) + ", " + str(self.Wa*align[1]) + ", "
                    else:
                        data = data + "0, 0, "
                    print("coh")
                    print(len(c_com))
                    if len(c_com) > 0:                      
                        forces.append([c_com[0]-x, c_com[1]-y])
                        weights.append(self.Wc)
                        data = data + str(self.Wc*(c_com[0]-x)) + ", " + str(self.Wc*(c_com[1]-y)) + ", "
                    else:
                        data = data + "0, 0, "
                    print("Sep")
                    print(len(s_com))
                    if len(s_com) > 0:                
                        forces.append([x-s_com[0], y-s_com[1]])
                        weights.append(self.Ws)
                        data = data + str(self.Ws*(x-s_com[0])) + ", " + str(self.Ws*(y-s_com[1])) + ", "
                    else:
                        data = data + "0, 0, "
                    if len(align) > 0:
                        data = data + str(align[2]) + ", "
                    else:
                        data = data + "0, "
                    if len(c_com) > 0:
                        data = data + str(c_com[2]) + ", "
                    else:
                        data = data + "0, "
                    if len(s_com) > 0:
                        data = data + str(s_com[2]) + "\n"
                    else:
                        data = data + "0\n"  
                    self.swarm.log_data(data)
                 
                    combined_vel = Swarm2.weighted_sum_forces(forces, weights)
                    # print('vx vy ' + str(combined_vel[0]) + ', ' + str(combined_vel[1]))
                    combined_speed = math.sqrt(combined_vel[0]*combined_vel[0] + combined_vel[1]*combined_vel[1])
                    combined_head = math.degrees(math.atan2(combined_vel[0], combined_vel[1]))
                    # print('comb speed ' + str(combined_speed) + ' ' + str(combined_head))                
                    boid.set_heading(int(combined_head))
                    theta = combined_head

                    if combined_speed > self.Vmin and combined_speed < self.Vmax:
                        boid.set_speed(int(combined_speed))
                    elif combined_speed < self.Vmin:
                        boid.set_speed(self.Vmin)
                    else:
                        boid.set_speed(self.Vmax)
                                   
                    # calculate a predicted target 50cm in front of self
                    waypoint_x = boid.get_location()['x']
                    waypoint_y = boid.get_location()['y']
                    theta = boid.get_heading()                  
                    target_x = waypoint_x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                    target_y = waypoint_y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))
                   
                    # wall reflection if target will be 'out of bounds'
                    if target_x > 100 or target_x < -100:
                        boid.set_heading(-theta)
                        theta = -theta
                        target_x = waypoint_x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                        target_y = waypoint_y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))    
 
                    if target_y > 100 or target_y < 0:
                        boid.set_heading(180-theta)
                        theta = 180-theta
               
                    time.sleep(0.15)
            except KeyboardInterrupt:
                print('Interrupted')