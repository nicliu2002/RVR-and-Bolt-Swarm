import sys

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
    print(f"RVR moving at speed {speed} and heading {heading}")
    await rvr.drive_with_heading(speed=speed, heading=heading, flags=DriveFlagsBitmask.none.value)
    print(f"RVR moving at speed {speed} and heading {heading}")
    await asyncio.sleep(1)

async def listen_for_commands():
    streams = resolve_stream('name', 'SpheroRVRControl')
    inlet = StreamInlet(streams[0])
    
    print("Listening for LSL commands...")

    try:
        while True:
            sample, _ = inlet.pull_sample()
            speed, heading = sample[0], sample[1]
            await update_rvr_movement(speed, heading)
    except asyncio.CancelledError:
        print("Listener task cancelled.")


async def main():
    await initialize_rvr()
    listener_task = asyncio.create_task(listen_for_commands())

    try:
        await asyncio.gather(listener_task)

    except KeyboardInterrupt:
        listener_task.cancel()
        await rvr.close()
        print("RVR shutdown successfully.")

if __name__ == '__main__':
    asyncio.run(main())
