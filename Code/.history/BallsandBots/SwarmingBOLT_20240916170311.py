import time
import math
import asyncio
import random
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread, Event
from Swarm2 import Swarm2
from Boid import Boid_BOLT, Boid_RVR
from ViconLocator import ViconLocator


def live_plotting_thread(boids, boid_rvrs, stop_event):
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()
    while not stop_event.is_set():
        ax.clear()
        # Plot positions for Boid_BOLT instances
        for boid in boids:
            positions = boid.positions
            if positions:
                pos_array = np.array(positions)
                ax.plot(pos_array[:, 0], pos_array[:, 1], 'bo-', label=boid.id)  # 'bo-' blue circle markers

        # Plot positions for Boid_RVR instances
        for rvr in boid_rvrs:
            positions = rvr.positions
            if positions:
                pos_array = np.array(positions)
                ax.plot(pos_array[:, 0], pos_array[:, 1], 'ro-', label=rvr.id)  # 'ro-' red circle markers

        ax.set_xlim(-2000, 2000)  # Adjust as needed
        ax.set_ylim(-2000, 2000)  # Adjust as needed
        ax.set_title('Boid Positions')
        ax.set_xlabel('X Position (mm)')
        ax.set_ylabel('Y Position (mm)')
        ax.legend()
        plt.draw()
        plt.pause(0.1)

    plt.ioff()
    plt.show()


def main():
    
    try:
        
        vicon_instance = ViconLocator()
        toys = ['SB-CE32','SB-B85A','rvr5']
        swarm = Swarm2(toys, vicon_instance)        
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