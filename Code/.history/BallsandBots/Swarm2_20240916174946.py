import math
import time
import matplotlib.pyplot as plt
import numpy as np
from spherov2 import scanner
from spherov2.toy.bolt import BOLT
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color


class Swarm2:

    def __init__(self, names, viconInstance):
        
        filtered_names = [name for name in names if "rvr" not in name.lower()]
        
        self.toys = scanner.find_toys(toy_names=filtered_names)
            
        print('found ' + str(len(self.toys)) + ' toys.')
        self.boids = []
        self.nextToy = 0
        self.log = open("swarm_log_Flocking1.txt", 'w')
        self.Locator = viconInstance

    # add to a list of active boids
    def add_boid(self, boid_id):
        self.boids.append(boid_id)
        

    def get_speed_heading(self, id):
        print("getting heading from vicon")
        lastX, lastY = self.Locator.get_position(id)
        time.sleep(0.25)
        nowX, nowY = self.Locator.get_position(id)
        return (math.sqrt((nowX-lastX)**2 + (nowY-lastY)**2)),(math.degrees((math.atan2((nowY-lastY), (nowX-lastX)))))
    
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
            # self.boids contains id strings for each one which are compatible with the locator
            xb,yb = self.Locator.get_position(boid)
            dist = Swarm2.get_distance(x, y, xb, yb)
            dir = 180*math.atan2(x-xb, y-yb)/math.pi
            if dist < radius and dir < vision_theta/2 and dir > -(vision_theta/2):
                speedb, thetab = self.get_speed_heading(boid)
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
            xb,yb = self.Locator.get_position(boid)
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
        self.log.flush()

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
