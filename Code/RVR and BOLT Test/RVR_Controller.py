import os
import sys
sys.path.append('/home/pi/sphero-sdk-raspberrypi-python/')

import asyncio
import time
# BOLT SDK
from spherov2 import scanner
from spherov2.sphero_edu import EventType, SpheroEduAPI
from spherov2.types import Color

# RVR SDK
from sphero_sdk import SpheroRvrAsync
from sphero_sdk import SerialAsyncDal




loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)

async def findBolts():
    toys = scanner.find_toys(toy_names=['SB-5938']) # substitute your own sphero ID here
    droid = SpheroEduAPI(toys[0])
    return droid
# Handler for the active controller stopped notification.
# After sending a stop command, your program can wait for
# this async to confirm that the robot has come to a stop
async def stopped_handler():
    print('RVR has stopped')


async def main():
    """ This program has RVR drive around using the normalized RC drive command.
    """
    print("wake up BOLT")
    # connect to robot
    asyncio.sleep(5) # delay to ensure connection established
    print("wake up RVR")
    droid = await findBolts()
    await rvr.wake()
    # Give RVR time to wake up
    await asyncio.sleep(2)
    # Register the handler for the stopped notification
    await rvr.on_robot_has_stopped_notify(handler=stopped_handler)
    await rvr.reset_yaw()
    print("sending RVR drive command")
    await rvr.drive_rc_si_units(
        linear_velocity=.3,     # Valid velocity values are in the range of [-2..2] m/s
        yaw_angular_velocity=0, # RVR will spin at up to 624 degrees/s.  Values outside of [-624..624] will saturate internally.
        flags=0
    )
    await droid.set_main_led(Color(3, 255, 0))
    print("moving BOLT")
    await droid.set_speed(60)
    await droid.set_speed(0)
    
    print("sending RVR drive command")
    await rvr.set_custom_control_system_timeout(command_timeout=20000)
    await rvr.drive_rc_si_units(
    linear_velocity=.3,     # Valid velocity values are in the range of [-2..2] m/s
    yaw_angular_velocity=0, # RVR will spin at up to 624 degrees/s.  Values outside of [-624..624] will saturate internally.
    flags=0
    )
    await asyncio.sleep(3) # allow both RVR and bolt to move forward
    await rvr.drive_stop(2.0)
    await rvr.on_robot_has_stopped_notify(handler=stopped_handler)
    await rvr.restore_default_control_system_timeout()
    await asyncio.sleep(1)
    await rvr.close()


if __name__ == '__main__':
    try:
        loop.run_until_complete(
            main()
        )

    except KeyboardInterrupt:
        print('\nProgram terminated with keyboard interrupt.')

        loop.run_until_complete(
            rvr.close()
        )

    finally:
        if loop.is_running():
            loop.close()
