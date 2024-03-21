"""
Vicon bridge

ViconBridge is a bridge to forward Vicon positions received from Vicon server to the robots using lsl

@ author    Essam Debie
@ version   1.0
"""


import datetime
import time

import pylsl
from vicon_dssdk import ViconDataStream
import logging
logging.getLogger('pylsl').setLevel(logging.ERROR)

class ViconBridge:
    # lsl params
    srate = 100
    stream_type = 'VICON'

    # Vicon params
    vicon_sr = 100  # vicon sampling rate per second
    vicon_x = None
    vicon_y = None
    vicon_server_ip = '192.168.68.54'
    vicon_server_port = '801'

    def __init__(self, robot_names):
        self.vicon_client = None

        # Initialise a dict of outlets
        self.outlet = {}
        for r in robot_names:
            self.init_lsl(r)

        self.init_vicon_streaming()

        # threading.Thread(target=self.vicon_locator()).start()

    def init_lsl(self, name):
        channel_names = ["x", "y"]
        n_channels = len(channel_names)

        # First create a new stream info.
        #  The first 4 arguments are stream name, stream type, number of channels, and
        #  sampling rate -- all parameterized by the keyword arguments or the channel list above.
        #  For this example, we will always use float32 data so we provide that as the 5th parameter.
        #  The last value would be the serial number of the device or some other more or
        #  less locally unique identifier for the stream as far as available (you
        #  could also omit it but interrupted connections wouldn't auto-recover).
        info = pylsl.StreamInfo(name, self.stream_type, n_channels, self.srate, 'float32', name)

        # append some meta-data
        # https://github.com/sccn/xdf/wiki/EEG-Meta-Data
        # info.desc().append_child_value("manufacturer", "LSLExampleAmp")
        chns = info.desc().append_child("channels")
        for chan_ix, label in enumerate(channel_names):
            ch = chns.append_child("channel")
            ch.append_child_value("label", label)
            ch.append_child_value("unit", "meters")
            ch.append_child_value("type", "Position")

        # next make an outlet; we set the transmission chunk size to 32 samples
        # and the outgoing buffer size to 360 seconds (max.)
        self.outlet[name] = pylsl.StreamOutlet(info, 32, 360)
        print()

    def init_vicon_streaming(self):
        self.vicon_client = ViconDataStream.Client()

    def push_data(self, name, sample):
        # print("now sending data...")
        self.outlet[name].push_sample(sample)

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
                    self.push_data('rvr1', [rand() for _ in range(self.outlet['rvr1'].get_info().channel_count())])
                else:
                    self.vicon_client.GetFrame()
                    for robot, outlet in self.outlet.items():
                        # current position and orientation according to vicon
                        global_position = self.vicon_client.GetSegmentGlobalTranslation(subjectName=robot,
                                                                                        segmentName=robot)

                        print(f"{robot}: {global_position}")
                        self.push_data(robot, [global_position[0][0], global_position[0][1]])
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
    robot_names = ['rvr3', 'rvr2'] #, 'rvr4'
    vb = ViconBridge(robot_names)
    vb.run()
