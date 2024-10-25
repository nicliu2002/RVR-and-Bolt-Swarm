import time
import math
import asyncio
import random
from Swarm2 import Swarm2
from ViconLocator import ViconLocator
from spherov2 import scanner
from spherov2.toy.bolt import BOLT
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color
from RVRController import RVR_Controller


# Shared configuration dictionary
boid_parameters = {
    'WAYPOINT_RANGE': 15,
    'Rc': 100,
    'Ra': 100,
    'Rs': 10,
    'Wc': 1.5,
    'Wa': 1.0,
    'Ws': 0.75,
    'vision_theta': 360,
    'Vmin': 25,
    'Vmax': 75
}

wall_rebound_limit = 150

class Boid_BOLT:

    def __init__(self, swarm, viconInstance, id, boid_parameters=boid_parameters):
        self.swarm = swarm
        self.toy = swarm.get_next_toy()
        # Initialize parameters from the shared configuration dictionary
        self.WAYPOINT_RANGE = boid_parameters['WAYPOINT_RANGE']
        self.Rc = boid_parameters['Rc']
        self.Ra = boid_parameters['Ra']
        self.Rs = boid_parameters['Rs']
        self.Wc = boid_parameters['Wc']
        self.Wa = boid_parameters['Wa']
        self.Ws = boid_parameters['Ws']
        self.vision_theta = boid_parameters['vision_theta']
        self.Vmin = boid_parameters['Vmin']
        self.Vmax = boid_parameters['Vmax']
        self.Locator = viconInstance
        self.id = id
        self.positions = []
        self.initial_coord = self.Locator.get_position(self.id)
        
    def get_position(self,toy):
        # Return the current position and other data for logging and plotting
        x, y = self.Locator.get_position(self.id)
        velocity = self.calculate_vel(toy)
        heading = toy.get_heading()
        return (x, y, velocity, heading)

    def log_position(self,toy):
        # Log the current position to the class variable
        x, y, velocity, heading = self.get_position(toy)
        self.positions.append((x, y))
        # Log data to the swarm's logger
        data = f"{time.time_ns()}, {self.id}, {x}, {y}, {velocity}, {heading}\n"
        self.swarm.log_data(data)
    
    
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
            self.swarm.add_boid(self.id)
            boid.set_speed()
            boid.set_heading(0)
            try:
                for count in range(0, 240):
                    # current position and orientation of robot 480
                    
                    self.log_position(boid)
                    
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
                    waypoint_x, waypoint_y = self.Locator.get_position(self.id)
                    theta = boid.get_heading()                  
                    target_x = waypoint_x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                    target_y = waypoint_y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))
                   
                    # wall reflection if target will be 'out of bounds'
                    if target_x > wall_rebound_limit or target_x < -wall_rebound_limit:
                        print("BOLT out of bounds")
                        boid.set_heading(-theta)
                        theta = -theta
                        target_x = waypoint_x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                        target_y = waypoint_y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))    
 
                    if target_y > wall_rebound_limit or target_y < -wall_rebound_limit:
                        boid.set_heading(180-theta)
                        theta = 180-theta
               
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print('Interrupted')
                


class Boid_RVR:

    def __init__(self, swarm, viconInstance, id, rvr_ip, boid_parameters=boid_parameters):
        self.swarm = swarm
        # self.toy = swarm.get_next_toy()
        self.WAYPOINT_RANGE = boid_parameters['WAYPOINT_RANGE']
        self.Rc = boid_parameters['Rc']
        self.Ra = boid_parameters['Ra']
        self.Rs = boid_parameters['Rs']
        self.Wc = boid_parameters['Wc']
        self.Wa = boid_parameters['Wa']
        self.Ws = boid_parameters['Ws']
        self.vision_theta = boid_parameters['vision_theta']
        self.Vmin = boid_parameters['Vmin']
        self.Vmax = boid_parameters['Vmax']
        self.Locator = viconInstance
        self.id = id
        self.RVR_Controller = RVR_Controller(rvr_ip) 
        self.positions = []
       
    
    def start_loop(self,delay):
        asyncio.run(self.run_boid(delay))
    
    def get_speed_heading(self):
        print("getting heading from vicon")
        lastX, lastY = self.Locator.get_position(self.id)
        time.sleep(0.25)
        nowX, nowY = self.Locator.get_position(self.id)
        return (math.sqrt((nowX-lastX)**2 + (nowY-lastY)**2)),(math.degrees((math.atan2((nowY-lastY), (nowX-lastX)))))
    
    def calculate_heading(self):
        print("getting heading from vicon")
        lastX, lastY = self.Locator.get_position(self.id)
        time.sleep(0.5)
        nowX, nowY = self.Locator.get_position(self.id)
        return(math.degrees((math.atan2((nowY-lastY), (nowX-lastX)))))
    
    def get_position(self):
        # Return the current position and other data for logging and plotting
        x, y = self.Locator.get_position(self.id)
        velocity, heading = self.get_speed_heading()
        return (x, y, velocity, heading)

    def log_position(self):
        # Log the current position to the class variable
        x, y, velocity, heading = self.get_position()
        self.positions.append((x, y))
        # Log data to the swarm's logger
        data = f"{time.time_ns()}, {self.id}, {x}, {y}, {velocity}, {heading}\n"
        self.swarm.log_data(data)    
    
    def run_boid(self, delay):
        time.sleep(5)
        self.swarm.add_boid(self.id)
        self.RVR_Controller.drive_control(0,0)
        
        try:
            for count in range(0, 240):
                
                self.log_position()
                
                # current position and orientation of robot 480
                x, y =  self.Locator.get_position(self.id)
                velocity, theta = self.get_speed_heading()
                
                print("error in heading is: ")
                theta_error = abs(theta - self.calculate_heading())
                print(f"{theta_error}")
                
                data = str(time.time_ns()) + ", " + self.id + ", " + str(x) + ", " + str(y) + ", " + str(velocity) + ", " + str(theta) + ", "
                
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
                self.RVR_Controller.set_heading(int(combined_head))
                theta = combined_head

                if combined_speed > self.Vmin and combined_speed < self.Vmax:
                    self.RVR_Controller.set_speed(int(combined_speed))
                elif combined_speed < self.Vmin:
                    self.RVR_Controller.set_speed(self.Vmin)
                else:
                    self.RVR_Controller.set_speed(self.Vmax)
                                
                # calculate a predicted target 50cm in front of self
                waypoint_x, waypoint_y = self.Locator.get_position(self.id)
                theta = self.RVR_Controller.lastHeading                  
                target_x = waypoint_x + self.WAYPOINT_RANGE*10*math.sin(math.radians(theta))
                target_y = waypoint_y + self.WAYPOINT_RANGE*10*math.cos(math.radians(theta))
                
                # wall reflection if target will be 'out of bounds'
                if target_x > wall_rebound_limit or target_x < -wall_rebound_limit:
                    self.RVR_Controller.set_heading(-theta)
                    theta = -theta
                    target_x = waypoint_x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                    target_y = waypoint_y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))    

                if target_y > wall_rebound_limit or target_y < -wall_rebound_limit:
                    self.RVR_Controller.set_heading(180-theta)
                    theta = 180-theta
            
                time.sleep(0.1)

        except KeyboardInterrupt:
            print('Interrupted')