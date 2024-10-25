import time
import sys
import os
from threading import Thread
from Swarm2 import Swarm2
from Boid import Boid_BOLT, Boid_RVR
from ViconLocator import ViconLocator

def main():
    try:
        vicon_instance = ViconLocator()
        
        # all toys to add to swarm and connect to bolts
        
        toys = ['SB-CE32','SB-41E0','rvr4','rvr1']
        # toys = ['SB-CE32', 'SB-5938', 'SB-8427']
        # toys = ['rvr1','rvr2','rvr5']
        
        swarm = Swarm2(toys, vicon_instance)
        
        # used for bolt vicon positioning and connecting to bolt
        
        bolts = ['SB-CE32','SB-41E0']
        
        # bolts = ['SB-CE32','SB-5938', 'SB-8427']
        # rvrs = ['rvr1','rvr2','rvr5']
        # rvr_ips = ["192.168.68.51","192.168.68.57","192.168.68.60"]
        
        # rvr name is principally used for vicon positioning, ip is used for passing commands, name and ip must correspond
        
        rvrs = ['rvr4','rvr1'] 
        rvr_ips = ['192.168.68.55','192.168.68.50']
        
        threads = []
        
        # adjust delay factor between starting of each agent
        delay_factor = 6
        delay = (len(toys)-1)*delay_factor
        
        # initiate boid bolts objects in threads
        
        for bolt in bolts: 
            print("initialising: " + bolt)
            boid = Boid_BOLT(swarm,vicon_instance,bolt)
            print('place next boid...')
            thread = Thread(target=boid.run_boid, args=(delay,))
            threads.append(thread)
            thread.start()
            time.sleep(delay_factor)
            delay = delay-delay_factor
        
        # initiate boid rvr objects in threads
        
        for rvr,ip in zip(rvrs, rvr_ips):
            print("initialising: " + rvr)
            boid = Boid_RVR(swarm,vicon_instance,rvr,ip)
            print('place next boid...')
            thread = Thread(target=boid.run_boid, args=(delay,))
            threads.append(thread)
            thread.start()
            time.sleep(delay_factor)
            delay = delay-delay_factor

        # close all threads once the threads are done
        for thread in threads:
            thread.join()
        
        # close swarm
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