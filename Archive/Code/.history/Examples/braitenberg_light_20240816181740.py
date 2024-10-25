import time
import math
from spherov2 import scanner
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color

# in case of a collision, flash red, turn 45 degrees and attempt to move again
def on_collision(api):
    api.stop_roll()
    api.set_main_led(Color(255, 0, 0))
    print('Collision')
    api.set_heading(api.get_heading() + 45)
    api.set_speed(100)
    time.sleep(0.25)
    api.set_main_led(Color(255, 22, 255))

# adjust velocity based on luminosity
def adjust_vel(api):
    #lum = api.get_luminosity()['ambient_light']
    #weight = 200/lum # the bigger the lum, the smaller the weight
    #print(lum)
    weight = random.randint(50,100)
    api.set_speed(100)
    api.spin(360//weight, 0.5) # the the smaller the weight the bigger the turn in the same period

def main():
    toys = scanner.find_toys(toy_names=['RV-92F1'])
    with SpheroEduAPI(toys[0]) as droid:
        droid.register_event(EventType.on_collision, on_collision)
        droid.set_main_led(Color(255, 255, 255))
        adjust_vel(droid)
 
        try:
            while(True):
                # adjust velocity based on light level
                adjust_vel(droid)

                time.sleep(0.05)

        except KeyboardInterrupt:
            print('Interrupted')
            

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
