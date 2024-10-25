import asyncio
from pylsl import StreamInfo, StreamOutlet

class RVR_Controller:
    
    def __init__(self, RVR_ip, RVR_id):
        # Create a new stream info (name, data type, number of channels, sample rate, type)
        info = StreamInfo('SpheroRVRControl', 'RVR', 2, 10, 'int32', 'myuid34234')

        # Create an outlet to stream data
        self.outlet = StreamOutlet(info)
        self.lastSpeed = 0
        self.lastHeading = 0
        
    def drive_control(self, speed, heading):
        """Immediately update the speed and heading."""
        self.outlet.push_sample([speed, heading])
        self.lastSpeed = speed
        self.lastHeading = heading
    
    def set_heading(self, heading):
        """Set the heading and send it with the current speed."""
        speed = self.lastSpeed
        self.outlet.push_sample([speed, heading])
        self.lastHeading = heading
        
    def set_speed(self, speed):
        """Set the speed and send it with the current heading."""
        heading = self.lastHeading
        self.outlet.push_sample([speed, heading])
        self.lastSpeed = speed

    async def continually_send(self, interval=0.1):
        """Continually send speed and heading messages at a given interval."""
        while True:
            # Send the current speed and heading at regular intervals
            self.outlet.push_sample([self.lastSpeed, self.lastHeading])
            print(f"Sent: Speed={self.lastSpeed}, Heading={self.lastHeading}")
            await asyncio.sleep(interval)  # Wait for the specified interval before sending the next sample


async def dynamic_changes(controller):
    """Dynamically change the speed and heading over time."""
    await asyncio.sleep(5)  # Wait 5 seconds before the first change
    print("Changing speed to 100 and heading to 180")
    controller.set_speed(100)
    controller.set_heading(180)

    await asyncio.sleep(5)  # Wait another 5 seconds before the next change
    print("Changing speed to 50 and heading to 270")
    controller.set_speed(50)
    controller.set_heading(270)

    await asyncio.sleep(5)  # Wait another 5 seconds
    print("Changing speed to 255 and heading to 0")
    controller.set_speed(255)
    controller.set_heading(0)


# Example usage:
async def main():
    # Create an RVR controller instance
    controller = RVR_Controller("192.168.68.57", "rvr5")

    # Set an initial speed and heading
    controller.set_speed(255)
    controller.set_heading(90)

    # Start sending the speed and heading continuously in the background
    send_task = asyncio.create_task(controller.continually_send(interval=1))  # Send data every 1 second
    
    # Dynamically change the speed and heading over time
    await dynamic_changes(controller)

    # Keep the loop running to continue sending data
    await send_task


# Start the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
