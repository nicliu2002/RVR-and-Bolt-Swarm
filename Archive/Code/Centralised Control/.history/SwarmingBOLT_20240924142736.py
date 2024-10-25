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
        toys = ['SB-CE32','SB-8427','rvr5']
        # toys = ['SB-CE32', 'SB-5938', 'SB-8427']
        # toys = ['rvr1','rvr2','rvr5']

        swarm = Swarm2(toys, vicon_instance)
        
        bolts = ['SB-CE32','SB-8427']
        
        # bolts = ['SB-CE32','SB-5938', 'SB-8427']
        # rvrs = ['rvr1','rvr2','rvr5']
        # rvr_ips = ["192.168.68.51","192.168.68.57","192.168.68.60"]
        
        rvrs = ['rvr5','rvr1']
        rvr_ips = ['192.168.68.60','192.168.68.51']
        
        
        threads = []
        delay_factor = 6
        delay = (len(toys)-1)*delay_factor
        
        for bolt in bolts: 
            print("finding toy: " + bolt)
            boid = Boid_BOLT(swarm,vicon_instance,bolt)
            print('place next boid...')
            thread = Thread(target=boid.run_boid, args=(delay,))
            threads.append(thread)
            thread.start()
            time.sleep(delay_factor)
            delay = delay-delay_factor
        
        for rvr,ip in zip(rvrs, rvr_ips):
            print("finding toy: " + rvr)
            boid = Boid_RVR(swarm,vicon_instance,rvr,ip)
            print('place next boid...')
            thread = Thread(target=boid.run_boid, args=(delay,))
            threads.append(thread)
            thread.start()
            time.sleep(delay_factor)
            delay = delay-delay_factor

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