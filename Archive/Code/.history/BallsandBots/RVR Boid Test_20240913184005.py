import time
import math
import asyncio
import random
import sys
import os
from threading import Thread
from Swarm2 import Swarm2
from Boid import Boid_BOLT, Boid_RVR
from ViconLocator import ViconLocator

def main():
    try:
        vicon_instance = ViconLocator()
        toys = ['rvr5']
        swarm = Swarm2(toys, vicon_instance)
        rvrs = ['rvr5']
        threads = []
        delay = (len(toys)-1)*12

        for rvr in rvrs:
            print("finding toy: " + rvr)
            boid = Boid_RVR(swarm,vicon_instance,rvr)
            print('place next boid...')
            thread = Thread(target=boid.start_loop, args=(delay,))
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