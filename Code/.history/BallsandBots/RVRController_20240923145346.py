import asyncio
import socket

class RVR_Controller:
    
    def __init__(self, RVR_ip, RVR_port=65432):
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
    
    def drive_control(self, speed, heading):
        """Immediately update the speed and heading."""
        self.set_speed(speed)
        self.set_heading(heading)

