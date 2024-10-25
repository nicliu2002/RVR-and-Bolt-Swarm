"""
Communication Handler

The Communication_Handler class is the central component of a networked communication system, facilitating seamless
interaction between devices. It plays a pivotal role in message exchange, robot monitoring, and graceful termination
signal handling. This class serves as the backbone for developing sophisticated networked applications, providing
a robust foundation for building collaborative systems that rely on effective communication and real-time monitoring.

@ author            Reda Ghanem
@ version           1.0
@ last update       11/12/2023
"""

# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #

import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import atexit
import platform
import os

# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #

# Flag to enable or disable print Exception Errors
print_exception_errors_flag = False

# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #
# ┃-------------------- # Communication_Handler Class # -----------------------┃ #
# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #


class Communication_Handler:
    # Initialize the Communication_Handler.
    # Parameters:
    #       - robot_name (str): The name or identifier of the robot.
    #       - host (str): The IP address of the Agent.
    #       - neighbors_ips (list): List of IP addresses of neighboring robots.
    #       - port (int): The port to use for communication (default is 12345).
    def __init__(self, robot_name='', host='', neighbors_ips='', port=12345):

        self.robot_name = robot_name
        self.host = host
        self.neighbors_ips = neighbors_ips
        self.port = port

        # Set the buffer size for data transmission
        self.buffer_size = 1024

        # Initialize variables to store server-side and client-side instances
        self.server_side = None
        self.client_side = None

        # Initialize threads for server-side and client-side operations
        self.server_side_thread = None
        self.client_side_thread = None

        # Flag to indicate if the Communication_Handler is currently running or not.
        # When set to True, the Communication_Handler is active; when set to False, it is intended to be stopped or terminated.
        self.is_running = None

        # Register cleanup function to be called on program exit
        atexit.register(self.atexit_cleanup)


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to Start communication and threads.
    def start_communication(self):

        self.is_running = True

        # Initialize server and client sides
        self.server_side = ServerSide(self.robot_name, self.host, self.port)
        self.client_side = ClientSide(self.robot_name, self.neighbors_ips, self.port)

        # Create and start threads for server and client sides
        self.server_side_thread = threading.Thread(target=self.server_side.start, daemon=True)
        self.client_side_thread = threading.Thread(target=self.client_side.start, daemon=True)

        self.server_side_thread.start()

        # Sleep for a short duration to ensure the server side thread has started before client side
        time.sleep(1)

        self.client_side_thread.start()

        # Sleep for a short duration to ensure the client side thread has started before client side
        time.sleep(1)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to send a message to all connected clients via the client side.
    # Parameters:
    #       - data (str): The message to be sent to all connected neighbors.
    def send_message_to_all(self, data):
        # Delegates the task to the corresponding method in the client side
        self.client_side.send_message_to_all_hosts(data)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to retrieve a list of all the last received messages from the server side
    # Returns 'list': A list of tuples where each tuple contains (sender_ip, message).
    def get_last_received_messages(self):
        # Delegates the task to the corresponding method in the server side
        return self.server_side.get_last_received_messages_from_clients()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to Perform cleanup before exit
    def atexit_cleanup(self):


        # check if the program exit before calling handle_termination, then call it now
        if self.is_running == True:
            print_in_green_box("Performing cleanup for Communications before exit...")
            self.handle_termination()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to Handle termination signals gracefully
    def handle_termination(self):

        self.is_running = False             # set Communication_Handler as inactive

        try:
            # Call handle_termination for server and client sides if they exist
            if hasattr(self, 'server_side_thread'):
                self.server_side.terminating_serverside()
                self.server_side_thread.join()

            if hasattr(self, 'client_side_thread'):
                self.client_side.terminating_clientside()
                self.client_side_thread.join()

            print("\nAll Threads stopped.")
            print("All Sockets closed.")
            animate_termination()

            # No need to close sockets here, as they are automatically closed when exiting the 'with' block

            # sys.exit(0)
        except Exception as e:
            # Handle errors while calling handle_termination
            print_exception_errors(f"Error while calling handle_termination: {str(e)}")


# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #
# ┃------------------------- # ServerSide Class # -----------------------------┃ #
# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #

class ServerSide:
    # Initialize the ServerSide class.
    # Parameters:
    #       - robot_name (str): Name of the robot associated with this server.
    #       - host (str): The IP address of the server.
    #       - port (int): The port to use for server communication.
    #       - buffer_size (int): Size of the buffer for receiving messages (default is 1024).
    def __init__(self, robot_name, host, port=12345, buffer_size=1024):
        """

        """
        self.robot_name = robot_name
        self.host = host
        self.port = port
        self.buffer_size = buffer_size

        # Create a TCP socket for server communication
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set socket option to allow reusing the address immediately after the server is terminated
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Set the timeout for the server socket, so each 1 sec out from server_socket.accept()
        self.server_socket.settimeout(1)  # 1 second timeout (adjust as needed)

        # Initialize thread for accept_clients function
        self.accept_clients_thread = None

        # Dictionary to store information about connected clients (IP as key)
        self.clients = {}

        # Lock to synchronize access to the clients dictionary
        self.clients_update_lock = threading.Lock()

        # Dictionary to store the last received message from each client (IP as key)
        self.last_received_messages = {}

        # Flag to indicate if the server is currently running or not.
        # When set to True, the server side is active; when set to False, it is intended to be stopped or terminated.
        self.is_running = True

        # Lock for synchronizing access to is_running
        self.is_running_lock = threading.Lock()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to accept incoming client connections
    def accept_clients(self):
        while True:
            with self.is_running_lock:
                if not self.is_running:
                    break

            try:
                # Accept incoming client connections
                client_socket, client_address = self.server_socket.accept()

                # Extract client IP address from the client address tuple
                client_ip = client_address[0]

                # Check if the client is not already in the clients dictionary
                if client_ip not in self.clients:
                    # Receive the client's name sent by the client
                    client_name = client_socket.recv(self.buffer_size).decode().strip()

                    # Print information about the new connection
                    print(f"New connection from {client_name} at {client_ip}")

                    # Create a new thread to handle the client and pass it to the handle_client method
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_ip),
                                                     daemon=True)

                    # Update the clients dictionary with client information (name, socket, thread)
                    with self.clients_update_lock:
                        self.clients[client_ip] = {'name': client_name, 'socket': client_socket,
                                                   'thread': client_thread}

                    # Start the thread to handle the client
                    client_thread.start()

            except socket.timeout:
                # Handle timeout (no incoming connection during the specified timeout)
                pass

            except OSError as e:
                # Handle errors while accepting client connections
                with self.is_running_lock:
                    if not self.is_running:
                        break
                print_exception_errors(f"Error while accepting client connection: {str(e)}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to handle communication with a client.
    
    def handle_client(self, client_socket, client_address):
        while True:
            with self.is_running_lock:
                if not self.is_running:
                    break

            try:
                # Receive message_length_bytes from the client
                message_length_bytes = client_socket.recv(4)
                message_length = int.from_bytes(message_length_bytes, byteorder='big')

                # Check if message_length_bytes is received
                if message_length_bytes:
                    # Decode the received message
                    message = client_socket.recv(message_length).decode()

                    # Update the last received messages with the client's address and message
                    self.last_received_messages[client_address] = message
            except Exception as e:
                # Handle errors while receiving data from the client
                print_exception_errors(f"Error while receiving data from {client_address}: {str(e)}")

                # Remove the client from the clients dictionary and close its socket
                self.remove_client(client_socket, client_address)

                # Exit the loop
                break

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to retrieve a list of all the last received messages from all senders
    # Returns 'list': A list of tuples where each tuple contains (sender_ip, message).
    def get_last_received_messages_from_clients(self):
        # Use a list comprehension to create a list of tuples containing sender IP and corresponding message
        return [(sender_ip, self.last_received_messages[sender_ip]) for sender_ip in self.last_received_messages]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to remove a disconnected client from the server.
    # Parameters:
    #       - client_socket: The socket object associated with the disconnected client.
    #       - client_address: The IP address of the disconnected client.
    def remove_client(self, client_socket, client_address):
        # Iterate through the clients to find the one with the specified address
        for client in self.clients:
            if client == client_address:
                # Print a message indicating the lost connection
                print(f"Connection with {client} lost")
                # Remove the client from the dictionary
                self.clients.pop(client)
                break
        # Close the socket associated with the disconnected client
        client_socket.close()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to check if another program is using the specified port and terminate it
    def terminate_program_using_port(self, port):
        try:
            # checks the operating system and uses the appropriate command to kill the process.
            if platform.system() == "Linux":
                # Use the `fuser` command to find the process ID (PID) of the program using the port
                pid = os.popen(f"fuser -n tcp {port}").read().strip()
                print(f"     └──> successfully found process ID (PID) of the program which using the port")
                if pid:
                    # Use the `kill` command to terminate the process
                    os.system(f"kill -9 {pid}")
                    print("     └──> successfully killed the process")
            elif platform.system() == "Windows":
                # Use the `netstat` command to find the process ID (PID) of the program using the port
                pid = os.popen(f"netstat -ano | findstr {port}").read().split()[4]
                print(f"     └──> successfully found process ID (PID) of the program which using the port")
                if pid:
                    # Use the `taskkill` command to terminate the process
                    os.system(f"taskkill /pid {pid} /f")
                    print("     └──> successfully killed the process")
            else:
                print(f"Unsupported operating system: {platform.system()}")
        except Exception as e:
            print(f"     └──>* Error while terminating program: {e}")

        # Sleep for a short duration to give chance for terminating the program
        time.sleep(1)


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to start the server side of communication
    def start(self):
        try:
            # Bind the server socket to the specified host and port, then start listening
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            # Print a message indicating that the server is listening for messages
            print(f"{self.robot_name} Listening for messages on {self.host}:{self.port}")
            # Create a thread to accept incoming clients
            self.accept_clients_thread = threading.Thread(target=self.accept_clients, daemon=True)
            self.accept_clients_thread.start()

        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"Address {self.host} with Port {self.port} is already in use.")
                print(f"     └──> Trying terminate the program using the specified Address.")
                self.terminate_program_using_port(self.port)
                self.start()  # Retry starting the server with the new port
            else:
                raise  # Re-raise the exception if it's not related to address in use

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to handle termination of the server side
    def terminating_serverside(self):
        # Print a message indicating the termination of the server side for a specific robot
        print_in_green_box(f"Terminating ServerSide of {self.robot_name}")

        # Set the is_running flag to False to signal termination
        with self.is_running_lock:
            self.is_running = False

        # Wait for the accept thread to finish if it exists
        if hasattr(self, 'accept_clients_thread'):
            self.accept_clients_thread.join()

        # Print a message indicating that the server side has been terminated
        print("ServerSide terminated.")


# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #
# ┃------------------------- # ClientSide Class # -----------------------------┃ #
# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #

class ClientSide:
    # Initialize the ClientSide class.
    #  Parameters:
    #       - robot_name (str): The name of the robot.
    #       - neighbors_ips (list): List of IP addresses of neighboring robots.
    #       - port (int): The port to use for communication.
    def __init__(self, robot_name, neighbors_ips, port=12345):
        self.robot_name = robot_name
        self.port = port
        self.neighbors_ips = neighbors_ips

        # Create dictionary to store sockets for communication with each neighbor.
        self.sockets_to_hosts = {neighbor: socket.socket(socket.AF_INET, socket.SOCK_STREAM) for neighbor in
                                 neighbors_ips}

        # Create dictionary to work as a flag to indicate if the client side is running.
        self.connected_to_host = {neighbor: False for neighbor in neighbors_ips}

        # Initialize thread for connect_to_neighbors_as_client function
        self.connect_to_neighbors_as_client_thread = None

        # Flag to indicate whether the client side is currently running or not.
        # When set to True, the client side is active; when set to False, it is intended to be stopped or terminated.
        self.is_running = True

        # Lock for synchronizing access to is_running
        self.is_running_lock = threading.Lock()

        # Executor for managing parallel tasks related to neighbors.
        self.executor = ThreadPoolExecutor(max_workers=len(neighbors_ips))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to establish connections to neighboring hosts as a client
    def connect_to_neighbors_as_client(self):
        while True:

            with self.is_running_lock:
                if not self.is_running:
                    break

            # Iterate over the list of neighbors' IPs
            for neighbor_ip in self.neighbors_ips:
                # Check if not already connected to the neighbor
                if not self.connected_to_host[neighbor_ip] and self.is_running == True:
                    try:
                        # Create a new socket for each connection attempt
                        self.sockets_to_hosts[neighbor_ip] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        # Set the timeout for the sockets_to_hosts[neighbor_ip], so each 1 sec out from sockets_to_hosts[neighbor_ip].connect
                        self.sockets_to_hosts[neighbor_ip].settimeout(2)  # 2 second timeout (adjust as needed)
                        # Connect to the neighbor's IP and port
                        self.sockets_to_hosts[neighbor_ip].connect((neighbor_ip, self.port))
                        # Send the robot's name to the neighbor
                        self.sockets_to_hosts[neighbor_ip].send(f"{self.robot_name}".encode())
                        self.connected_to_host[neighbor_ip] = True
                        print(f"Connected to the host at {neighbor_ip}:{self.port}")


                    except socket.timeout:
                        # Handle timeout (no connection established during the specified timeout)
                        pass

                    except Exception as e:
                        # Handle errors during connection attempts
                        print_exception_errors(f"Error connecting to {neighbor_ip}:{self.port}: {str(e)}")
                        pass

            # Sleep for a short duration to avoid excessive connection attempts
            time.sleep(1)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to send a message to all connected hosts
    
    def send_message_to_all_hosts(self, message):
        def send_message(ip):
            try:
                # Check if still connected to the neighbor
                if self.connected_to_host[ip]:
                    # Send the message to the connected neighbor
                    message_length = len(message)
                    self.sockets_to_hosts[ip].send(message_length.to_bytes(4, byteorder='big'))
                    self.sockets_to_hosts[ip].send(message.encode())
            except Exception as e:
                # Handle errors during message sending
                print_exception_errors(f"Error sending message to {ip}: {str(e)}")
                self.connected_to_host[ip] = False
                self.sockets_to_hosts[ip].close()

        # Get a list of all connected neighbors' IPs
        all_hosts_ips = list(self.sockets_to_hosts.keys())
        # Use ThreadPoolExecutor to concurrently send messages to all connected neighbors
        self.executor.map(send_message, all_hosts_ips)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to start the client side
    def start(self):
        # Create a thread to continuously attempt to connect to neighbors as a client
        self.connect_to_neighbors_as_client_thread = threading.Thread(target=self.connect_to_neighbors_as_client,
                                                                      daemon=True)
        self.connect_to_neighbors_as_client_thread.start()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # Function to handle termination of the client side
    def terminating_clientside(self):
        print_in_green_box("Terminating ClientSide")

        with self.is_running_lock:
            self.is_running = False

        if hasattr(self, 'connect_to_neighbors_as_client_thread'):
            self.connect_to_neighbors_as_client_thread.join()

        print("ClientSide terminated.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━ Helper Functions ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# Function to print the message in a green box:
def print_in_green_box(message):
    # Calculate the width of the box based on the message length
    box_width = len(message) + 2  # 1 dashes on each side

    # ANSI escape codes for terminal text color
    green_color = "\033[92m"
    reset_color = "\033[0m"

    print("")   # print new line

    # Print the top border in green
    print(green_color + "+" + "-" * box_width + "+" + reset_color)

    # Print the message in green with vertical bars on each side
    print(green_color + f"| {message} |" + reset_color)

    # Print the bottom border in green
    print(green_color + "+" + "-" * box_width + "+" + reset_color)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# Function to print the first word in red and the rest in the default color:
def print_exception_errors(error_message):

    if print_exception_errors_flag:
        # Split the error message into words
        words = error_message.split()

        # ANSI escape codes for terminal text color
        red_color = "\033[91m"
        reset_color = "\033[0m"

        # Print the first word in red and the rest in the default color
        print(red_color + words[0] + reset_color, end=" ")
        print(" ".join(words[1:]))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

# Function to animate the termination process with a progress indicator.
# Parameters:
#       - iterations: Number of animation steps (default is 20).
#       - delay: Time delay between steps in seconds (default is 0.02).
def animate_termination(iterations=20, delay=0.02):
    # List of characters for animation
    animation_chars = ["⠻", "⠽", "⠾", "⠷", "⠯", "⠟"]

    # ANSI escape codes for terminal text color
    green_color = "\033[92m"
    reset_color = "\033[0m"

    # Loop through iterations to display animated progress
    for i in range(iterations):
        for char in animation_chars:
            # Display animated progress with green color
            print(f"{green_color}{str('▇' * i)}{char}{reset_color}", end="\r")
            time.sleep(delay)

    # Clear the line and print the final message
    print(end="\r")
    print(f"{green_color}{str('▇' * iterations)}{reset_color}")
    print_in_green_box("All Communications Terminated Successfully!")

