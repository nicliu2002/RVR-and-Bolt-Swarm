import os
import sys
import time
sys.path.append('/home/pi/sphero-sdk-raspberrypi-python/')

# BOLT SDK
from spherov2 import scanner
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color

from sphero_sdk import SpheroRvrObserver

rvr = SpheroRvrObserver()


def main():
    """ This program has RVR drive around in different directions using the function drive_with_yaw_si.
        This is a newer command, and uses some different conventions from what you may be accustomed to if you
        have used the initial release of this SDK.

        In Sphero conventions, "heading" is CCW positive, matching a compass, while "yaw" is CW positive, as a
        rotation around the (vertical) Z axis of the robot following the right hand rule.  This yaw convention
        was selected to match the ISO 8855 standard:
        "Road Vehicles - Vehicle dynamics and road-holding ability -- Vocabulary"

        Because of this difference between heading and yaw, headings will need to be converted into yaw angles
        IF you want to switch commands in existing projects.  In the _si version of this command, yaw_angle
        is a float, allowing for the specification of non-integer yaw targets.

        To eliminate the flags field, unsigned scalar speed values have been replaced in newer commands with
        signed linear velocity values.  In the _si versions of drive commands, linear_velocity is a float argument
        in meters per second.
    """
    try:
        rvr.wake()
        time.sleep(2)
        print("RVR awake")
        toys = scanner.find_toys(toy_names=['SB-5938']) # substitute your own sphero ID here
        time.sleep(2)
        print(str(toys)) 
        with SpheroEduAPI(toys[0]) as droid:
        # Give RVR time to wake up

            rvr.reset_yaw()
            rvr.drive_with_yaw_si(
                linear_velocity=0.5,
                yaw_angle=0  # Valid yaw values are traditionally [-179..+180], but will continue wrapping outside of that range
            )
            droid.set_speed(60)
            # Delay to allow RVR to drive
            time.sleep(1)

            rvr.drive_with_yaw_si(
                linear_velocity=0.5,
                yaw_angle=10  # Valid yaw values are traditionally [-179..+180], but will continue wrapping outside of that range
            )
            droid.spin(10)
            # Delay to allow RVR to drive
            time.sleep(1)

            rvr.drive_with_yaw_si(
                linear_velocity=0.5,
                yaw_angle=90  # Valid yaw values are traditionally [-179..+180], but will continue wrapping outside of that range
            )
            droid.spin(90)
            # Delay to allow RVR to drive
            time.sleep(1)

            rvr.drive_with_yaw_si(
                linear_velocity=0.5,
                yaw_angle=270,  # Valid yaw values are traditionally [-179..+180], but will continue wrapping outside of that range
            )
            droid.spin(270)
            # Delay to allow RVR to drive
            time.sleep(1)

            # This will bring RVR to a stop facing a yaw angle of zero.
            rvr.drive_with_yaw_si(
                linear_velocity=0,
                yaw_angle=0,  # Valid yaw values are traditionally [-179..+180], but will continue wrapping outside of that range
            )
            droid.set_heading(0)
            # Delay to allow RVR to drive
            time.sleep(2)

    except KeyboardInterrupt:
        print('\nProgram terminated with keyboard interrupt.')

    finally:
        rvr.close()


if __name__ == '__main__':
    main()
