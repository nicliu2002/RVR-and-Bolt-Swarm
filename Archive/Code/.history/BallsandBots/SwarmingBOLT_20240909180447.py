import time
import math
import random
import sys
import os
from threading import Thread
from Swarm2 import Swarm2
from Boid import Boid
from ViconLocator import ViconLocator

def main():
    try:
        vicon_instance = ViconLocator()
        toys = ['SB-CE32','SB-B85A','RV-ACF7']
        swarm = Swarm2(toys, vicon_instance)
        threads = []
        delay = (len(toys)-1)*12

        for toy in toys: 
            subject_ind = 0
            print("finding toy: " + toy)
            boid = Boid(swarm,vicon_instance,toy)
            print('place next boid...')
            thread = Thread(target=boid.run_boid, args=(delay,))
            threads.append(thread)
            thread.start()
            time.sleep(12)
            delay = delay-12
            subject_ind += 1

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