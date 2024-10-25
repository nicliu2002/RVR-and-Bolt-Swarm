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
        self.outlet.push_sample([speed, heading])
        self.lastSpeed = speed
        self.lastHeading = heading
    
    def set_heading(self, heading):
        speed = self.lastSpeed
        self.outlet.push_sample([speed, heading])
        self.lastHeading = heading
        
    def set_speed(self, speed):
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


# Example usage:
async def main():
    # Create an RVR controller instance
    controller = RVR_Controller("192.168.68.57", "rvr5")

    # Set an initial speed and heading
    controller.set_speed(255)
    controller.set_heading(90)

    # Start sending the speed and heading continuously
    await controller.continually_send(interval=0.01)  # Send data every 0.5 seconds


# Start the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
