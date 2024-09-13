import time
import math
import random
from Swarm2 import Swarm2
from ViconLocator import ViconLocator
from spherov2 import scanner
from spherov2.toy.bolt import BOLT
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color
from RVRController import RVR_Controller

controller = RVR_Controller("192.168.68.57","rvr5")

print("setting speed to 255")

controller.set_speed(255)