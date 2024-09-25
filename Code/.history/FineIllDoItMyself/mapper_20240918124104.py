"""
Vicon bridge

ViconBridge is a bridge to forward Vicon positions received from Vicon server to the robots using Matplotlib

@ author    Essam Debie
@ version   1.0
"""

import datetime
import time
import matplotlib.pyplot as plt
from vicon_dssdk import ViconDataStream
import logging

from assets import Constants as Cons

logging.getLogger('pylsl').setLevel(logging.ERROR)

class ViconBridge:
    # Vicon params
    vicon_sr = 100  # vicon sampling rate per second
    vicon_x = None
    vicon_y = None
    vicon_server_ip = '192.168.68.54'
    vicon_server_port = '801'

    def __init__(self, robot_names):
        self.vicon_client = None
        self.robot_names = robot_names
        self.positions = {robot: (0, 0) for robot in robot_names}  # Initialize positions for each robot

        self.init_vicon_streaming()
        self.setup_plot()

    def setup_plot(self):
        # Setup the plot
        self.fig, self.ax = plt.subplots()
        self.scatters = {
            robot: self.ax.scatter([], [], label=robot) for robot in self.robot_names
        }
        self.ax.set_xlim(-5, 5)  # Set x-axis limits, adjust as needed
        self.ax.set_ylim(-5, 5)  # Set y-axis limits, adjust as needed
        self.ax.legend()
        plt.ion()  # Enable interactive mode
        plt.show()

    def init_vicon_streaming(self):
        self.vicon_client = ViconDataStream.Client()

    def update_plot(self):
        for robot, scatter in self.scatters.items():
            x, y = self.positions[robot]
            scatter.set_offsets([x, y])
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def vicon_locator(self):
        debug = False
        while True and not debug:
            try:
                self.log("Connecting to Vicon server...")
                self.vicon_client.Connect(f"{self.vicon_server_ip}:{self.vicon_server_port}")
                self.vicon_client.SetBufferSize(3)
                self.vicon_client.EnableSegmentData()

                has_frame = False

                while not has_frame:
                    self.vicon_client.GetFrame()
                    has_frame = True
                self.log("Connected to Vicon server.")
                break
            except ViconDataStream.DataStreamException as e:
                sleep_secs = 10
                self.log('  - Vicon Datastream Error: ' + e.message + f'. Trying again in {sleep_secs} seconds.')
                time.sleep(sleep_secs)
                continue

        while True:
            try:
                if debug:
                    from random import random as rand

                    for robot in self.robot_names:
                        self.positions[robot] = (rand() * 10 - 5, rand() * 10 - 5)  # Random positions
                else:
                    self.vicon_client.GetFrame()
                    for robot in self.robot_names:
                        # Current position according to vicon
                        global_position = self.vicon_client.GetSegmentGlobalTranslation(subjectName=robot,
                                                                                        segmentName=robot)
                        x, y = global_position[0][0], global_position[0][1]
                        self.positions[robot] = (x, y)
                        print(f"{robot}: {x}, {y}")

                self.update_plot()

            except Exception as e:
                print(e)
                pass
            finally:
                time.sleep(1 / self.vicon_sr)

    def run(self):
        self.vicon_locator()

    def log(self, msg):
        print(f"{datetime.datetime.now().replace(second=0, microsecond=0)}: {msg}")

if __name__ == '__main__':
    robot_names = ['bolt1']  # Add more robot names if needed
    vb = ViconBridge(robot_names)
    vb.run()
