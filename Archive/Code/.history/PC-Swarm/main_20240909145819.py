import time
import math
import random
from spherov2 import scanner
from spherov2.toy.bolt import BOLT
from spherov2.sphero_edu import EventType, SpheroEduAPI
from threading import Thread, Lock
from vicon_dssdk import ViconDataStream
from twisted.web._element import Expose

max_time_step = 500000

class MAS:

    #vicon_server_ip = 'l-hvhnpt3'
    vicon_server_ip = '192.168.68.52'
    vicon_server_port = '801'

    def __init__(self):
        self.log = open("mas_logViconSpheroSwarm1.txt", 'w')
        self.vicon_client = ViconDataStream.Client()

        try:
            print("Connecting to Vicon server ...")
            self.vicon_client.Connect(f"{self.vicon_server_ip}:{self.vicon_server_port}")
            self.vicon_client.SetBufferSize(3)
            self.vicon_client.EnableSegmentData()

            has_frame = False

            while not has_frame:
                self.vicon_client.GetFrame()
                has_frame = True

        except ViconDataStream.DataStreamException as e:
            print('Vicon Datastream Error: ', e)


    def log_data(self, data):
        self.log.write(data)

    def get_client(self):
        return self.vicon_client

class Location:
    """Return Vicon X and Y
    """
    def __init__(self, toy, mas,subject_ind):
        self.mas = mas
        self.toy = toy 
        self.subject_ind = subject_ind
        self.WAYPOINT_RANGE = 50
        
    def getPosition(self):
        self.mas.vicon_client.GetFrame()
        client = self.mas.vicon_client
        subject_names = client.GetSubjectNames()
        global_position = client.GetSegmentGlobalTranslation(subject_names[self.subject_ind], subject_names[self.subject_ind])
        xVicon = global_position[0][0]/10
        yVicon = global_position[0][1]/10
        data = str(subject_names[self.subject_ind]) + " , " + str(xVicon) + ", " + str(yVicon)
        self.mas.log_data(data+"\n")
        return xVicon , yVicon

class Agent:

    def __init__(self, toy, mas, subject_ind):
        self.toy = toy 
        self.subject_ind = subject_ind
        self.Locator = Location(self.toy,mas,subject_ind)
        self.xPos, self.yPos = self.Locator.getPosition()
        self.velocity = 0
        self.heading = 0
        self.WAYPOINT_RANGE = 50
        
    
    # each agent needs to have a vicon velocity and position attribute to calculate the three boid forces, this will be achieved by:
    #  - Calculating the vicon velocity
    #  - Receiving velocity and position of nearby neighbours
    #  - Calculating Boid forces and returning velocity w/ heading (heading will be referenced to heading of 0 on BOLT/RVR)
    
    def calculate_vel(self):
        print("calculating velocity from encoders, units in cm/s, converted to mm/s")
        deltaX = self.toy.get_velocity()['x']
        deltaY = self.toy.get_velocity()['y']
        return 10*(math.sqrt(deltaX**2 + deltaY**2))        

    def calculate_heading(self):
        print("getting heading from vicon")
        lastX, lastY = self.Locator.getPosition()
        time.sleep(0.5)
        nowX, nowY = self.Locator.getPosition()
        return(math.degrees((math.atan2((nowY-lastY),(nowX-lastX)))))
    
    def get_pos_vel(self):
        return self.xPos, self.yPos, self.velocity, self.heading
        
    def get_neighbours_pos_vel(self):
        

    def run_agent(self):
        for count in range(0, max_time_step):
                                  
            self.xPos, self.yPos = self.Locator.getPosition()
            self.vel=self.calculate_vel()
            self.heading = self.calculate_heading()
            #### Wall Reflection: Robots move in a 240*120 rectangle area
            if target_x > 120 or target_x < -120:
                self.toy.set_heading(-theta)
                theta = -theta	  
                target_x = xVicon + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                target_y = yVicon + self.WAYPOINT_RANGE*math.cos(math.radians(theta))    
            
            if target_y > 120 or target_y < 0:
                self.toy.set_heading(180-theta)
                theta = 180-theta
                target_x = xVicon + self.WAYPOINT_RANGE*math.sin(math.radians(theta))
                target_y = yVicon + self.WAYPOINT_RANGE*math.cos(math.radians(theta))         
            time.sleep(0.1)  
            



def main():
    try:
        names = ['SB-8427','SB-41F2'] 
        toys = scanner.find_toys(toy_names=names)
        print('found ' + str(len(toys)) + ' toys.')
        mas = MAS()
        agent_threads = []
        while(True):
            subject_ind = 0
            for toy in toys:
                with SpheroEduAPI(toy) as boid:
                    time.sleep(5)
                    theta = random.randint(-45, 45)
                    boid.set_heading(theta)
                    boid.set_speed(80) 
                    agentPos = Location(toy,mas,subject_ind)
                    xPos , yPos = agentPos.getPosition()
                    agent = Agent(toy, mas, xPos, yPos)
                    thread = Thread(target=agent.run_agent)
                    agent_threads.append(thread)
                    thread.start() 
                    for thread in agent_threads:
                        thread.join()
                    subject_ind += 1        


    


    except KeyboardInterrupt:
        print('Interrupted')
            
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Main Interrupted')
     

