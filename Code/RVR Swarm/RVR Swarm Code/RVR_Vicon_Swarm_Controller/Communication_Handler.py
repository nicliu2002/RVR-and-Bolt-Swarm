"""
Communication Handler

The Communication_Handler class is responsible for managing communication between devices over a network. 
It allows for sending and receiving messages between devices, monitoring the availability of robots, 
and gracefully handling termination signals. This class serves as a foundation for creating networked 
applications that involve message exchange and robot monitoring.

@ author    Reda Ghanem
@ version   1.0
"""
 
# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #

import socket
import threading
import time

# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #

# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #
# ┃-------------------- # Communication_Handler Class # -----------------------┃ #
# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #


class Communication_Handler:
    def __init__(self, my_ip, port=12345):
        """
        Initialize the Communication_Handler.

        Args:
            my_ip (str): The IP address of the laptop.
            port (int): The port to use for communication (default is 12345).
        """
        self.my_ip = my_ip
        self.port = port
        self.available_robots = []
        self.receive_thread = None
        self.check_robots_thread = None
        self.is_running = True  # Flag to indicate if the program is running

        # Initialize a dictionary to store the last received message from each sender
        self.last_received_messages = {}

        

    def send_message_to_ip(self, ip, message):
        """
        Send a message to a specified IP address.

        Args:
            ip (str): The IP address of the recipient.
            message (str): The message to send.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, self.port))
                s.send(message.encode())
        except Exception as e:
            print(f"Error sending message to {ip}: {e}")


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    def receive_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.my_ip, self.port))
            s.listen()
            print(f"Listening for messages on {self.my_ip}:{self.port}")
            s.settimeout(1)  # Set a timeout of 1 second on the socket
            while self.is_running:
                try:
                    conn, addr = s.accept()
                    with conn:
                        data = conn.recv(1024)
                        if data:
                            message = data.decode()
                            # print(f"Received message: {message} from {addr[0]}")
                            # Store the last received message from this sender
                            self.last_received_messages[addr[0]] = message
                except socket.timeout:
                    pass  # Handle the timeout and check the is_running flag
    

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function: Get a list of all the last received messages from all senders.
    def get_last_received_messages(self):
        """
        Returns:
            list: A list of tuples where each tuple contains (sender_ip, message).
        """
        return [(sender_ip, self.last_received_messages[sender_ip]) for sender_ip in self.last_received_messages]

                
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    def check_robots(self):
        """
        Periodically check for available robots and update the list of available robots.
        """
        previous_available_robots = []

        while self.is_running:
            for ip in self.all_ips:
                if ip != self.my_ip:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(1)  # Adjust the timeout as needed
                            s.connect((ip, self.port))
                        if ip not in self.available_robots:
                            self.available_robots.append(ip)
                    except Exception as e:
                        # print(f"Robot with IP ({ip}) is currently disconnected.")

                        # Remove the disconnected robot from the available_robots list
                        if ip in self.available_robots:
                            self.available_robots.remove(ip)

                        # Remove the disconnected robot from the last_received_messages dictionary
                        if ip in self.last_received_messages:
                            del self.last_received_messages[ip]

            if self.available_robots != previous_available_robots:
                # print("Available robots:", self.available_robots)
                previous_available_robots = self.available_robots.copy()

            time.sleep(1)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    def handle_termination(self):
        """ Handle termination signals gracefully. """

        self.is_running = False

        # Join threads to ensure they have completed
        if self.receive_thread:
            self.receive_thread.join()
        if self.check_robots_thread:
            self.check_robots_thread.join()

        print("Threads stopped.")
        print("Sockets closed.")
        
        # No need to close sockets here, as they are automatically closed when exiting the 'with' block

        # sys.exit(0)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    def start_communication(self, all_ips):
        """
        Start communication and threads.

        Args:
            all_ips (list): List of all IP addresses to communicate with.
        """
        self.all_ips = all_ips
        # Create threads here
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.check_robots_thread = threading.Thread(target=self.check_robots)
        self.receive_thread.start()
        self.check_robots_thread.start()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    def send_message_to_all(self, message):
        """
        Send messages to all available robots.

        Args:
            message (str): The message to send to all available robots.
        """
        for ip in self.available_robots:
            if ip != self.my_ip:
                self.send_message_to_ip(ip, message)




