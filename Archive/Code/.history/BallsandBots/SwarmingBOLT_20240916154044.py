import time
import math
import asyncio
import random
import sys
import os
from threading import Thread, Event
from Swarm2 import Swarm2
from Boid import Boid_BOLT, Boid_RVR
from ViconLocator import ViconLocator

def main():
    try:
        vicon_instance = ViconLocator()
        toys = ['SB-CE32','SB-B85A','rvr5']
        swarm = Swarm2(toys, vicon_instance)
        # Create a stop event for the plotting thread
        stop_event = Event()

        # Start the plotting thread
        plot_thread = Thread(
            target=swarm.plot_live_positions_and_forces,
            args=(5, 180, 1.0, 1.0, stop_event)
        )
        plot_thread.start()
        bolts = ['SB-CE32','SB-B85A']
        rvrs = ['rvr5']
        rvr_ips = ["192.168.68.57"]
        threads = []
        delay = (len(toys)-1)*12

        for bolt in bolts: 
            print("finding toy: " + bolt)
            boid = Boid_BOLT(swarm,vicon_instance,bolt)
            print('place next boid...')
            thread = Thread(target=boid.run_boid, args=(delay,))
            threads.append(thread)
            thread.start()
            time.sleep(12)
            delay = delay-12
        
        for rvr,ip in zip(rvrs, rvr_ips):
            print("finding toy: " + rvr)
            boid = Boid_RVR(swarm,vicon_instance,rvr,ip)
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