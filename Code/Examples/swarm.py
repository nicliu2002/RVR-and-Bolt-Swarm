import time 
import math
import random
from spherov2 import scanner
from spherov2.toy.bolt import BOLT
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color
from threading import Thread

class Swarm:

    def __init__(self):
        self.boids = []
        self.log = open("swarm_log_red_comms.txt", 'w')

    # add to a list of active boids
    def add_boid(self, boid):
        self.boids.append(boid)

    # return average boid stats (coms and avg vel) of boids within the three radii of interest wrt given position
    def get_neighbourhood_stats(self, name, x, y, rad_c, rad_s, rad_a, vision_theta):
        x_com_c = 0
        y_com_c = 0
        x_com_s = 0
        y_com_s = 0
        x_vec_a = 0
        y_vec_a = 0
        num_boids_c = 0
        num_boids_a = 0
        num_boids_s = 0
        for boid in self.boids:
            if boid.toy.name != name:
                xb = boid.api.get_location()['x']
                yb = boid.api.get_location()['y']
                dist = Swarm.get_distance(x, y, xb, yb)
                dir = 180*math.atan2(x-xb, y-yb)/math.pi
                if dist < rad_c and dir < vision_theta/2 and dir > -(vision_theta/2):
                    x_com_c = x_com_c + xb
                    y_com_c = y_com_c + yb
                    num_boids_c = num_boids_c + 1
                if dist < rad_s and dir < vision_theta/2 and dir > -(vision_theta/2):
                    x_com_s = x_com_s + xb
                    y_com_s = y_com_s + yb
                    num_boids_s = num_boids_s + 1
                if dist < rad_a and dir < vision_theta/2 and dir > -(vision_theta/2):
                    thetab = boid.api.get_heading()
                    speedb = boid.api.get_speed()
                    x_vec_a = x_vec_a + speedb*math.sin(math.radians(thetab))
                    y_vec_a = y_vec_a + speedb*math.cos(math.radians(thetab))
                    num_boids_a = num_boids_a + 1
        result = [0, 0, 0, 0, 0, 0, 0, 0, 0] # format is c_com_x, c_com_y, s_com_x, s_com_y, a_vel_x, a_vel_y, n_c, n_s, n_a
        if num_boids_c > 0: # only return a value if there are boids nearby other than me
            result[0] = x_com_c/num_boids_c
            result[1] = y_com_c/num_boids_c
            result[6] = num_boids_c
        if num_boids_s > 0:
            result[2] = x_com_s/num_boids_s
            result[3] = y_com_s/num_boids_s
            result[7] = num_boids_s
        if num_boids_a > 0: # only return a value if there are boids nearby other than me
            result[4] = x_vec_a/num_boids_a
            result[5] = y_vec_a/num_boids_a
            result[8] = num_boids_a
        return result

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

    def __init__(self, swarm, toy):
        self.swarm = swarm
        self.toy = toy
        self.WAYPOINT_RANGE = 50
        self.Rc = 100
        self.Ra = 50
        self.Rs = 25
        self.Wc = 1.0
        self.Wa = 1.0
        self.Ws = 0.5
        self.vision_theta = 360
        self.Vmin = 70
        self.Vmax = 80
        
    def run_boid(self, delay):
        with SpheroEduAPI(self.toy) as self.api:
            time.sleep(5)
            self.swarm.add_boid(self)
            theta = random.randint(-45, 45)
            speed = random.randint(self.Vmin, self.Vmax)
            self.api.set_heading(theta)
            self.api.set_speed(speed)
            time.sleep(1)
            self.api.set_speed(0)
            time.sleep(delay)
            self.api.set_speed(speed)
            try:
                for count in range(0, 480):
                    try:
                        # current position and orientation of robot
                        x = self.api.get_location()['x']
                        y = self.api.get_location()['y']
                        speed = self.api.get_speed()
                        theta = self.api.get_heading()
                        data = str(time.time_ns()) + ", " + self.toy.name + ", " + str(x) + ", " + str(y) + ", " + str(speed) + ", " + str(theta) + ", "
                    
                        # modify target according to cohesion, separation and alignment rules
                        stats = self.swarm.get_neighbourhood_stats(self.toy.name, x, y, self.Rc, self.Rs, self.Ra, self.vision_theta)
                        forces = [[speed*math.sin(math.radians(theta)), speed*math.cos(math.radians(theta))], [stats[0]-x, stats[1]-y], [x-stats[2], y-stats[3]], [stats[4], stats[5]]]
                        weights = [1, self.Wc, self.Ws, self.Wa]
                        data = data + str(self.Wa*stats[4]) + ", " + str(self.Wa*stats[5]) + ", " + str(self.Wc*(stats[0]-x)) + ", " + str(self.Wc*(stats[1]-y)) + ", "
                        data = data + str(self.Ws*(x-stats[2])) + ", " + str(self.Ws*(y-stats[3])) + ", " + str(stats[8]) + ", " + str(stats[6]) + ", " + str(stats[7]) + "\n"
                        self.swarm.log_data(data)
                  
                        combined_vel = Swarm.weighted_sum_forces(forces, weights) 
                        # print('vx vy ' + str(combined_vel[0]) + ', ' + str(combined_vel[1]))
                        combined_speed = math.sqrt(combined_vel[0]*combined_vel[0] + combined_vel[1]*combined_vel[1])
                        combined_head = math.degrees(math.atan2(combined_vel[0], combined_vel[1]))
                        # print('comb speed ' + str(combined_speed) + ' ' + str(combined_head))                 
                        self.api.set_heading(int(combined_head))
                        theta = combined_head

                        if combined_speed > self.Vmin and combined_speed < self.Vmax:
                            self.api.set_speed(int(combined_speed))
                        elif combined_speed < self.Vmin:
                            self.api.set_speed(self.Vmin)
                        else:
                            self.api.set_speed(self.Vmax)
                                     
                        # calculate a predicted target 50cm in front of self
                        x = self.api.get_location()['x']
                        y = self.api.get_location()['y']
                        theta = self.api.get_heading()    
                                    
                        target_x = x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                        target_y = y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))
                    
                        # wall reflection if target will be 'out of bounds'
                        if target_x > 120 or target_x < -120:
                            self.api.set_heading(-theta)
                            theta = -theta        
                            target_x = x + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                            target_y = y + self.WAYPOINT_RANGE*math.cos(math.radians(theta))    
  
                        if target_y > 120 or target_y < 0:
                            self.api.set_heading(180-theta)
                            theta = 180-theta
                    except:
                        print('exception, moving on')
                    time.sleep(0.25)
            except KeyboardInterrupt:
                print('Interrupted')
            

def main():
    try:
        names = ['SB-B85A', 'SB-8427', 'SB-B11E'] 
        toys = scanner.find_toys(toy_names=names)
        print('found ' + str(len(toys)) + ' toys.')
        
        swarm = Swarm()
        threads = []
        delay = (len(toys)-1)*12

        for toy in toys:          
            boid = Boid(swarm, toy)
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
