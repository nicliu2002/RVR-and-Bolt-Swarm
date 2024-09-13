import asyncio
import socket

class RVR_Controller:
    
    def __init__(self, RVR_ip, RVR_port):
        # Initialize socket connection
        self.RVR_ip = RVR_ip
        self.RVR_port = RVR_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((RVR_ip, RVR_port))
        
        # Initialize last speed and heading
        self.lastSpeed = 0
        self.lastHeading = 0

    def send_data(self, speed, heading):
        """Send the current speed and heading via socket."""
        message = f"{speed},{heading}\n"  # Send as a comma-separated string
        self.sock.sendall(message.encode('utf-8'))  # Send encoded message over the socket
        print(f"Sent: Speed={speed}, Heading={heading}")
    
    def set_heading(self, heading):
        """Set the heading and send it with the current speed."""
        self.lastHeading = heading
        self.send_data(self.lastSpeed, self.lastHeading)
        print(f"Set Heading to {heading}")
        
    def set_speed(self, speed):
        """Set the speed and send it with the current heading."""
        self.lastSpeed = speed
        self.send_data(self.lastSpeed, self.lastHeading)
        print(f"Set Speed to {speed}")

    def close(self):
        """Close the socket connection."""
        self.sock.close()

# Example usage:
async def main():
    # Create an RVR controller instance and connect to the server
    controller = RVR_Controller("192.168.68.57", 65432)

    # Set an initial speed and heading
    controller.set_speed(255)
    controller.set_heading(90)

    await asyncio.sleep(5)
    controller.set_speed(100)
    controller.set_heading(180)

    await asyncio.sleep(5)
    controller.set_speed(50)
    controller.set_heading(270)

    # Close the socket connection when done
    controller.close()

# Start the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
s