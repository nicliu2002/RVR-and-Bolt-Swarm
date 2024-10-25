import asyncio
from pylsl import StreamInfo, StreamOutlet

class RVR_Controller:
    
    def __init__(self, RVR_ip, RVR_id, interval=0.1):
        # Create a new stream info (name, data type, number of channels, sample rate, type)
        info = StreamInfo('SpheroRVRControl', 'RVR', 2, 10, 'int32', 'myuid34234')

        # Create an outlet to stream data
        self.outlet = StreamOutlet(info)
        self.lastSpeed = 0
        self.lastHeading = 0
        
        # Start the continuous sending loop as soon as the controller is initialized
        self.interval = interval

    def start_control_loop(self):
        """Method to start the control loop."""
        # Schedule the continually_send coroutine in the event loop
        return asyncio.create_task(self.continually_send())
    
    def drive_control(self, speed, heading):
        """Immediately update the speed and heading."""
        self.outlet.push_sample([speed, heading])
        self.lastSpeed = speed
        self.lastHeading = heading
    
    def set_heading(self, heading):
        """Set the heading and send it with the current speed."""
        self.lastHeading = heading
        print(f"Set Heading to {heading}")
        
    def set_speed(self, speed):
        """Set the speed and send it with the current heading."""
        self.lastSpeed = speed
        print(f"Set Speed to {speed}")

    async def continually_send(self):
        """Continually send speed and heading messages at a given interval."""
        while True:
            # Send the current speed and heading at regular intervals
            self.outlet.push_sample([self.lastSpeed, self.lastHeading])
            print(f"Sent: Speed={self.lastSpeed}, Heading={self.lastHeading}")
            await asyncio.sleep(self.interval)  # Wait for the specified interval before sending the next sample


async def main():
    # Create an RVR controller instance
    controller = RVR_Controller("192.168.68.57", "rvr5", interval=1)

    # Start the control loop
    control_task = controller.start_control_loop()

    # Dynamically set speed and heading
    await asyncio.sleep(5)
    controller.set_speed(100)
    controller.set_heading(180)

    await asyncio.sleep(5)
    controller.set_speed(50)
    controller.set_heading(270)

    # Keep the event loop running for the task
    await control_task

# Start the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
