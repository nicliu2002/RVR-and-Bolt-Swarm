import sys
import os
import math
import time
import signal
import random
from threading import Thread, Lock

# if we run code from /home/pi/sphero-sdk-raspberrypi-python/projects/ folder use:
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# if we run code from /home/pi/RVR folder use:
sys.path.append('/home/pi/sphero-sdk-raspberrypi-python/')

# running code from laptop to test compile
# sys.path.append(r"C:\Users\nicli\Documents\Thesis\Code\sphero-sdk-raspberrypi-python\sphero-sdk-raspberrypi-python")

# For sphero_sdk
import asyncio
from sphero_sdk import SerialAsyncDal
from sphero_sdk import SpheroRvrAsync
from sphero_sdk import RvrLedGroups             # for LED
from sphero_sdk import RvrStreamingServices     # For locater handler 

# for sphero BOLT

from spherov2 import scanner
from spherov2.toy.bolt import BOLT
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color

# For Vicon
from pylsl import resolve_stream, StreamInlet

# For Swarm
from assets import Constants as Cons              # for Constants and Global variables
from assets.Boid import Boid
from assets.Helper_Functions import *             # Import Helper_Functions.py from the parent directory

from RVRAgent import RVRAgent
from BOLTAgent import BOLTAgent
from ViconLocator import ViconLocator
