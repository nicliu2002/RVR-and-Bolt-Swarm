import time
import math
import random
from spherov2 import scanner
from spherov2.toy.bolt import BOLT
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color
from threading import Thread

class Swarm2:

    def __init__(self, names):
        self.toys = scanner.find_toys(toy_names=names)
        print('found ' + str(len(self.toys)) + ' toys.')
        self.boids = []
        self.nextToy = 0
        self.log = open("swarm_log_RandNew4.txt", 'w')

    # add to a list of active boids
    def add_boid(self, boid):
        self.boids.append(boid)


    # dole out toys for assingment to new boids
    def get_next_toy(self):
        toy = self.toys[self.nextToy]
        self.nextToy = self.nextToy+1
        return toy

    # return average velocity of boids with the given radius of given position
    def get_neighbourhood_align(self, x, y, radius, vision_theta):
        vec_x = 0
        vec_y = 0
        num_boids = 0
        for boid in self.boids:
            xb = boid.get_location()['x']
            yb = boid.get_location()['y']
            dist = Swarm2.get_distance(x, y, xb, yb)
            dir = 180*math.atan2(x-xb, y-yb)/math.pi
            if dist < radius and dir < vision_theta/2 and dir > -(vision_theta/2):
                thetab = boid.get_heading()
                speedb = boid.get_speed()
                vec_x = vec_x + speedb*math.sin(math.radians(thetab))
                vec_y = vec_y + speedb*math.cos(math.radians(thetab))
                num_boids = num_boids + 1
        if num_boids > 1: # only return a value if there are boids nearby other than me
            vec_x = vec_x/num_boids
            vec_y = vec_y/num_boids
            return [vec_x, vec_y, num_boids-1]
        else:
            return []

    # return centre of mass of boids within the given radius of given position
    # return an empty list if no such boids exist
    def get_neighbourhood_com(self, x, y, radius, vision_theta):
        x_com = 0
        y_com = 0
        num_boids = 0
        for boid in self.boids:
            xb = boid.get_location()['x']
            yb = boid.get_location()['y']
            dist = Swarm2.get_distance(x, y, xb, yb)
            dir = 180*math.atan2(x-xb, y-yb)/math.pi
            if dist < radius and dir < vision_theta/2 and dir > -(vision_theta/2):
                x_com = x_com + xb
                y_com = y_com + yb
                num_boids = num_boids + 1
        if num_boids > 1: # only return a value if there are boids nearby other than me
            x_com = x_com/num_boids
            y_com = y_com/num_boids
            return [x_com, y_com, num_boids-1]
        else:
            return []

    def log_data(self, data):
        self.log.write(data)

    def finalise(self):
        self.log.close()

    @staticmethod
    def get_distance(x1, y1, x2, y2):
        return math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

    @staticmethod
    def weighted_sum_forces(forces, weights):
        vec_x = 0
        vec_y = 0
        for (force, weight) in zip(forces, weights):
            vec_x = vec_x + weight*force[0]
            vec_y = vec_y + weight*force[1]
        return [vec_x, vec_y]            



class Boid:

    def __init__(self, swarm):
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
       
    def run_boid(self, delay):
        with SpheroEduAPI(self.toy) as boid:
            time.sleep(5)
            self.swarm.add_boid(boid)
            theta = random.randint(-45, 45)
            speed = random.randint(self.Vmin, self.Vmax)
            boid.set_heading(theta)
            boid.set_speed(speed)
            time.sleep(1)
            boid.set_speed(0)
            time.sleep(delay)
            boid.set_speed(speed)
            try:
                for count in range(0, 240):
                    # current position and orientation of robot 480
                    x = boid.get_location()['x']
                    y = boid.get_location()['y']
                    speed = boid.get_speed()
                    theta = boid.get_heading()
                    data = str(time.time_ns()) + ", " + self.toy.name + ", " + str(x) + ", " + str(y) + ", " + str(speed) + ", " + str(theta) + ", "
                   
                    # modify target according to cohesion and alignment rules
                    c_com = self.swarm.get_neighbourhood_com(x, y, self.Rc, self.vision_theta)
                    s_com = self.swarm.get_neighbourhood_com(x, y, self.Rs, self.vision_theta)
                    align = self.swarm.get_neighbourhood_align(x, y, self.Ra, self.vision_theta)
                    forces = [[speed*math.sin(math.radians(theta)), speed*math.cos(math.radians(theta))]]
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
                    x = boid.get_location()['x']
                    y = boid.get_location()['y']
                    theta = boid.get_heading()                  
                    target_x = x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                    target_y = y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))
                   
                    # wall reflection if target will be 'out of bounds'
                    if target_x > 100 or target_x < -100:
                        boid.set_heading(-theta)
                        theta = -theta
                        target_x = x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                        target_y = y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))    
 
                    if target_y > 100 or target_y < 0:
                        boid.set_heading(180-theta)
                        theta = 180-theta
               
                    time.sleep(0.15)
            except KeyboardInterrupt:
                print('Interrupted')
           

def main():
    try:
        toys = ['SB-CE32','SB-8050','SB-41F2']
        swarm = Swarm2(toys)
        threads = []
        delay = (len(toys)-1)*12

        for toy in toys:          
            boid = Boid(swarm)
            print('place next boid...')
            thread = Thread(target=boid.run_boid, args=(delay,))
            threads.append(thread)
            thread.start()
            time.sleep(12)
            delay = delay-12

        for thread in threads:
            thread.join()

        swarm.finalise()

    except KeyboardInterrupt:
        print('Interrupted')
   
           
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Main Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)