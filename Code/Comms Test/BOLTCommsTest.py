import time
import math
import random
from spherov2 import scanner
from spherov2.toy.bolt import BOLT
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color


message_channels = (4, )


def on_ir_message_4(api, channel):
    if channel != 4:
        return
    print("Message received on channel 4")
    api.stop_roll()
    for i in range(3):
        api.set_main_led(Color(255, 0, 0))
        time.sleep(0.05)
        api.set_main_led(Color(0,255,0))
        time.sleep(0.05)
        api.set_main_led(Color(0,0,255))
        time.sleep(0.05)
    api.listen_for_ir_message(message_channels)
    
def lightFlash(api):
    api.set_main_led(Color(255,255,255))
    time.sleep
        

def main():
    toys = scanner.find_toys(toy_names=['SB-09D3'])
    with SpheroEduAPI(toys[0]) as droid:
        droid.register_event(EventType.on_ir_message, on_ir_message_4(droid,))
        droid.listen_for_ir_message(message_channels)
        try:
            while(True):
                droid.listen_for_ir_message(message_channels)
                time.sleep(0.05)
        except KeyboardInterrupt:
            print('Interrupted')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
