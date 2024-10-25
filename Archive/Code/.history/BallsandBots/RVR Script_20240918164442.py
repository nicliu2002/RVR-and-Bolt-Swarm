import sys
import os

sys.path.append('/home/pi/sphero-sdk-raspberrypi-python/')


import socket
import asyncio
from sphero_sdk import SpheroRvrAsync
from sphero_sdk import SerialAsyncDal
from sphero_sdk import DriveFlagsBitmask

# Event loop for asyncio
loop = asyncio.get_event_loop()

# Initialize the Sphero RVR
rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)

# Initialize location and velocity variables
current_location = [0, 0]  # Placeholder for actual location
current_velocity = [0, 0]  # Placeholder for actual velocity

async def initialize_rvr():
    """Initialize the RVR."""
    await rvr.wake()
    await asyncio.sleep(2)
    print("RVR initialized.")
    await rvr.reset_yaw()

async def update_rvr_movement(speed, heading):
    """Update the RVR movement with speed and heading."""
    speed = max(0, min(speed, 255))
    speed = int(speed * 0.8)  # Scale down the speed
    heading = int(heading % 360)  # Ensure heading is within valid range
    await rvr.drive_with_heading(
        speed=speed,  # Valid speed values are 0-255
        heading=heading,  # Valid heading values are 0-359
        flags=DriveFlagsBitmask.none.value
    )  
      
    await asyncio.sleep(1)
    print(f"RVR moving at speed {speed} and heading {heading}")

async def listen_for_commands(host='0.0.0.0', port=65432):
    """Listen for incoming commands via a socket."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}...")

        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # Data format: 'speed,heading\n'
                message = data.decode('utf-8').strip()
                try:
                    speed, heading = map(int, message.split(','))
                    await update_rvr_movement(speed, heading)
                except ValueError as e:
                    print(f"Invalid {speed=}\t{heading=}")
                    print(e.message)
                    print(e.args)

async def main():
    """Main function to initialize RVR and listen for commands."""
    await initialize_rvr()

    # Start the socket server to listen for speed and heading commands
    await listen_for_commands()

if __name__ == '__main__':
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Shutting down RVR...")
        loop.run_until_complete(rvr.close())
        print("RVR shutdown successfully.")
