import time
import math
from Swarm2 import Swarm2
from spherov2.sphero_edu import SpheroEduAPI
from RVRController import RVR_Controller

# bounds the area by out of bounds * 2
out_of_bounds = 100

class Boid_BOLT:
    """Handle boid agent as individual object
    """
    def __init__(self, swarm, viconInstance, id):
        self.swarm = swarm
        self.toy = swarm.get_next_toy()
        # swarm parameters below for adjustment
        self.WAYPOINT_RANGE = 50
        self.Rc = 400
        self.Ra = 400
        self.Rs = 25
        self.Wc = 1.0
        self.Wa = 0
        self.Ws = 0.44
        self.vision_theta = 360
        self.Vmin = 50
        self.Vmax = 75
        self.Locator = viconInstance
        self.id = id
    
    def run_boid(self, delay):
        """Boid update velocity loop"""
        with SpheroEduAPI(self.toy) as boid:
            time.sleep(5)
            self.swarm.add_boid(self.id, boid)
            boid.set_speed(0)
            boid.set_heading(0)
            try:
                for count in range(0, 240):
                    # current position, velocity and orientation of robot 
                    x, y =  self.Locator.get_position(self.id)
                    velocity = boid.get_speed()
                    theta = boid.get_heading()
                    
                    # print("error in heading is: ")
                    # theta_error = abs(theta - self.calculate_heading())
                    # print(f"{theta_error}")
                    
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
                        # print(f"aligned robots for {self.id} is: {align[2]}")
                        data = data + str(align[2]) + ", "
                    else:
                        data = data + "0, "
                    if len(c_com) > 0:
                        # print(f"cohesion robots for {self.id} is: {c_com[2]}")
                        data = data + str(c_com[2]) + ", "
                    else:
                        data = data + "0, "
                    if len(s_com) > 0:
                        # print(f"separation robots for {self.id} is: {s_com[2]}")
                        data = data + str(s_com[2]) + "\n"
                    else:
                        data = data + "0\n"  
                    # self.swarm.log_data(data)
                 
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
                    print(f"location at bounce check for {self.id} is x:{waypoint_x} \t y:{waypoint_y}")
                    theta = boid.get_heading()                  
                    target_x = waypoint_x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                    target_y = waypoint_y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))
                    print(f"location at bounce check for {self.id} is x:{target_x} \t y:{target_y}")

                    # wall reflection if target will be 'out of bounds'
                    if (target_x > out_of_bounds or target_x < -out_of_bounds):
                        boid.set_heading(-theta)
                        theta = -theta
                        target_x = waypoint_x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                        target_y = waypoint_y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))    

                    if target_y > out_of_bounds or target_y < -out_of_bounds:
                        boid.set_heading(180-theta)
                        theta = 180-theta
                        
                    if -out_of_bounds < waypoint_x < out_of_bounds and  -out_of_bounds < waypoint_y < out_of_bounds:
                        self.oob_state = False
                        
                    # print(f"{self.id} looped through")
                    time.sleep(0.15)
            except KeyboardInterrupt:
                print('Interrupted')
                


class Boid_RVR:

    def __init__(self, swarm, viconInstance, id, rvr_ip):
        self.swarm = swarm
        # swarm parameters below for adjustment
        self.WAYPOINT_RANGE = 50
        self.Rc = 400
        self.Ra = 400
        self.Rs = 25
        self.Wc = 1.0
        self.Wa = 0
        self.Ws = 0.44
        self.vision_theta = 360
        self.Vmin = 75
        self.Vmax = 105
        self.Locator = viconInstance
        self.id = id
        self.RVR_Controller = RVR_Controller(rvr_ip)    
    
    def run_boid(self, delay):
        """Boid update velocity loop"""
        time.sleep(5)
        self.swarm.add_boid(self.id, self.RVR_Controller)
        self.RVR_Controller.drive_control(0,0)
        
        try:
            for count in range(0, 240):
                
                # current position and orientation of robot 480
                x, y =  self.Locator.get_position(self.id)
                velocity, theta = self.RVR_Controller.lastSpeed, self.RVR_Controller.lastHeading
                
                # theta_error = abs(theta - self.calculate_heading())
                # print(f"error in heading is: {theta_error}")
                
                data = str(time.time_ns()) + ", " + self.id + ", " + str(x) + ", " + str(y) + ", " + str(velocity) + ", " + str(theta) + ", "
                
                # modify target according to cohesion and alignment rules
                c_com = self.swarm.get_neighbourhood_com(x, y, self.Rc, self.vision_theta)
                s_com = self.swarm.get_neighbourhood_com(x, y, self.Rs, self.vision_theta)
                align = self.swarm.get_neighbourhood_align(x, y, self.Ra, self.vision_theta)
                forces = [[velocity*math.sin(math.radians(theta)), velocity*math.cos(math.radians(theta))]]
                # print('speed ' + str(speed) + ' ' + str(theta))
                
                # calculated updated velocity
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
                
                combined_vel = Swarm2.weighted_sum_forces(forces, weights)
                # print('vx vy ' + str(combined_vel[0]) + ', ' + str(combined_vel[1]))
                
                # calculate parameters for robot and pass to robot
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
                target_x = waypoint_x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                target_y = waypoint_y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))
                
                print(f"location at bounce check for {self.id} is x:{target_x} \t y:{target_y}")

                # print(f"RVR {self.id} moving to target x {target_x} and target y {target_y}")
                
                # wall reflection if target will be 'out of bounds'

                if (target_x > out_of_bounds or target_x < -out_of_bounds):
                    self.RVR_Controller.set_heading(-theta)
                    theta = -theta
                    target_x = waypoint_x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                    target_y = waypoint_y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))    

                if target_y > out_of_bounds or target_y < -out_of_bounds:
                    self.RVR_Controller.set_heading(180-theta)
                    theta = 180-theta
            
                time.sleep(0.15)

        except KeyboardInterrupt:
            print('Interrupted')