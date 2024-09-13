import asyncio
import sys

sys.path.append('/home/pi/sphero-sdk-raspberrypi-python/')

from sphero_sdk import SpheroRvrAsync
from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream
import time



# Initialize RVR asynchronously
rvr = SpheroRvrAsync()

# Initialize location and velocity variables
current_location = [0, 0]  # Placeholder for actual location
current_velocity = [0, 0]  # Placeholder for actual velocity

async def initialize_rvr():
    await rvr.wake()
    await asyncio.sleep(2)
    print("RVR initialized.")

async def update_rvr_movement(speed, heading):
    speed = max(0, min(speed, 255))
    heading = heading % 360
    await rvr.drive_with_heading(speed=speed, heading=heading, flags=0)
    print(f"RVR moving at speed {speed} and heading {heading}")

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

async def send_telemetry():
    info = StreamInfo('RVRTelemetry', 'Telemetry', 4, 10, 'float32', 'rvr_telemetry_id')
    outlet = StreamOutlet(info)
    
    while True:
        # Update current location and velocity from RVR sensors (these would be read from sensors)
        # Simulating location and velocity data
        current_location[0] += 0.01  # X coordinate
        current_location[1] += 0.01  # Y coordinate
        current_velocity[0] = 0.5  # Simulate some velocity data (e.g., 0.5 m/s)
        current_velocity[1] = 0.5
        
        outlet.push_sample(current_location + current_velocity)
        await asyncio.sleep(0.1)

async def main():
    await initialize_rvr()

    listener_task = asyncio.create_task(listen_for_commands())
    telemetry_task = asyncio.create_task(send_telemetry())

    try:
        await asyncio.gather(listener_task, telemetry_task)
    except KeyboardInterrupt:
        listener_task.cancel()
        telemetry_task.cancel()
        await rvr.close()
        print("RVR shutdown successfully.")

if __name__ == '__main__':
    asyncio.run(main())
