import time
import math
import random
from spherov2 import scanner
from spherov2.toy.bolt import BOLT
from spherov2.sphero_edu import EventType, SpheroEduAPI
from threading import Thread, Lock
from vicon_dssdk import ViconDataStream
from twisted.web._element import Expose

class MAS:

    # vicon_server_ip = 'l-hvhnpt3'
    vicon_server_ip = '192.168.68.54'
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

class Agent:

    def __init__(self, toy, mas, xPos, yPos):
        self.mas = mas
        self.toy = toy 
        self.xPos = xPos
        self.yPos = yPos
        self.WAYPOINT_RANGE = 50

    def run_agent(self):
     
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
    try:
        names = ['SB-8427','RV-92F1'] 
        toys = scanner.find_toys(toy_names=names)
        print('found ' + str(len(toys)) + ' toys.')
        mas = MAS()
        agent_threads = []
        while(True):
            sunject_ind = 0
            for toy in toys:
                with SpheroEduAPI(toy) as sphero:
                    time.sleep(5)
                    theta = random.randint(-45, 45)
                    sphero.set_heading(theta)
                    sphero.set_speed(80) 
                    agentPos = Location(toy,mas,sunject_ind)
                    xPos , yPos = agentPos.getPosition()
                    agent = Agent(toy, mas, xPos, yPos)
                    thread = Thread(target=agent.run_agent)
                    agent_threads.append(thread)
                    thread.start() 
                    for thread in agent_threads:
                        thread.join()
                    sunject_ind += 1        


    


    except KeyboardInterrupt:
        print('Interrupted')
            
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Main Interrupted')
     

