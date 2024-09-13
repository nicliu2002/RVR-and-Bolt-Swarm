import sys
import os

sys.path.append('/home/pi/sphero-sdk-raspberrypi-python/')

from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream

import asyncio
from sphero_sdk import SpheroRvrAsync
from sphero_sdk import SerialAsyncDal
from sphero_sdk import DriveFlagsBitmask


loop = asyncio.get_event_loop()

rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)

# Initialize location and velocity variables
current_location = [0, 0]  # Placeholder for actual location
current_velocity = [0, 0]  # Placeholder for actual velocity

async def initialize_rvr():
    await rvr.wake()
    await asyncio.sleep(2)
    print("RVR initialized.")
    await rvr.reset_yaw()


async def update_rvr_movement(speed, heading):
    speed = max(0, min(speed, 255))
    heading = heading % 360
    await rvr.drive_with_heading(
        speed=128,  # Valid speed values are 0-255
        heading=0,  # Valid heading values are 0-359
        flags=DriveFlagsBitmask.none.value
    )  
    await asyncio.sleep(1)


async def main():
    await initialize_rvr()

    try:
        await update_rvr_movement(100,100)

    except KeyboardInterrupt:
        await rvr.close()
        print("RVR shutdown successfully.")


if __name__ == '__main__':
    try:
        loop.run_until_complete(
            main()
        )
        
    except KeyboardInterrupt:
        print("RVR shutdown successfully.")
