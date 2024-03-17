"""
Experiment observer object

Observer can act like a server in a centralised environment to host main swarming logic and communicating low level
commands with robots. It can also act as an observer in centralised and decentralised environment to collect statistics
and any other performance measures as needed.



@ author    Essam Debie
@ version   1.0
"""


import atexit
import datetime
import signal
import socket
import sys
import threading
from time import sleep

import pylsl
import select
from tabulate import tabulate


def get_lan_ip():
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Connect to a public IP address
        sock.connect(("8.8.8.8", 80))

        # Get the local IP address
        local_ip = sock.getsockname()[0]

        return local_ip
    except socket.error:
        return None


class Observer:
    def __init__(self, host, port=1234):
        self.host = host
        self.port = port
        self.broadcast_port = 12345
        self.buffer_size = 1024
        self.clients = {}
        self.clients_update_lock = threading.Lock()

        self.verbose = True

        self.received_signal = False
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)
        atexit.register(self.atexit_cleanup)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.active = True
        self.is_running = True

    def atexit_cleanup(self):
        print("Performing cleanup before exit...")
        self.received_signal = True

    def handle_exit(self, signum, frame):
        print("Stopping the observer...")

        self.is_running = False

        # Close all client sockets and join client threads
        with self.clients_update_lock:
            for client_ip in list(self.clients.keys()):
                self.remove_client(self.clients[client_ip]['socket'], client_ip)

        # Close the server socket
        self.server_socket.close()
        # Exit the program
        sys.exit(0)

    def __name__(self):
        # return f"{str(datetime.datetime.now().replace(second=0).replace(microsecond=0))} {self.__class__.__name__}"
        return f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}" # {self.__class__.__name__}

    def print_time_stamped(self, msg):
        print(f"{self.__name__()}: {msg}")

    def run(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        if self.verbose:
            self.print_time_stamped(f"Observer listening on {self.host}:{self.port}")

        reporting_thread = threading.Thread(target=self.report_thread)
        reporting_thread.start()

        broadcast_thread = threading.Thread(target=self.broadcast_thread)
        broadcast_thread.start()

        accept_thread = threading.Thread(target=self.accept_clients)
        accept_thread.start()

    def accept_clients(self):
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_ip = client_address[0]
                if client_ip not in self.clients:
                    # Receive the client's initial message
                    client_name = client_socket.recv(1024).decode().strip()

                    self.print_time_stamped(f"New connection from {client_name} at {client_ip}")

                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_ip))
                    with self.clients_update_lock:
                        self.clients[client_ip] = {'name': client_name, 'socket': client_socket, 'thread': client_thread}
                    client_thread.start()
            except OSError as e:
                if not self.is_running:
                    break
                self.print_time_stamped(f"Error while accepting client connection: {str(e)}")

    def handle_client(self, client_socket, client_address):
            while True:
                try:
                    data = client_socket.recv(self.buffer_size)
                    if not data:
                        continue
                    self.handle_data(client_socket, data)
                except Exception as e:
                    self.print_time_stamped(f"Error while receiving data from {client_address}: {str(e)}")
                    self.remove_client(client_socket, client_address)
                    break

    def handle_data(self, sock, data):
        # Handle incoming data from clients
        decoded_data = data.decode().strip()
        if decoded_data == "list_clients":
            self.list_clients(sock)
        elif decoded_data.startswith("send_all"):
            self.send_all(sock, decoded_data[9:])
        elif decoded_data.startswith("send_to"):
            self.send_to(sock, decoded_data[7:])
        else:
            self.print_time_stamped(f"{sock.getpeername()[0]} --> {decoded_data}")
            # sock.send("Invalid command".encode())

    def list_clients(self, sock):
        # Send a list of connected clients to a specific client
        client_list = "Connected clients:\n"
        for i, client in enumerate(self.clients):
            client_list += f"{i + 1}. {client[1]}\n"
        sock.send(client_list.encode())

    def send_all(self, sock, message):
        # Send a message to all connected clients
        for client in self.clients:
            if client[0] != sock:
                client[0].send(message.encode())

    def send_to(self, client, message):
        # Send a message to a specific client
        # client_index = int(message.split(" ")[0])
        try:
            self.clients[client]['socket'].send(message.encode())
        except Exception as e:
            self.print_time_stamped(f"Invalid client or client not connected: {client}")

    def remove_client(self, sock, client_address):
        # Remove a disconnected client from the list of clients
        for client in self.clients:
            if client == client_address:
                self.print_time_stamped(f"Connection with {client} lost")
                self.clients.pop(client)
                break
        sock.close()
        # self.inputs.remove(sock)

    def shutdown(self):
        self.active = False
        self.server_socket.close()
        for client in self.clients:
            client.active = False

    def report_thread(self):
        while True:
            client_list = [{'Name': c['name'], 'Connected on': ip} for ip, c in self.clients.items()]
            # print("Len", len(client_list))
# =============================================================================
#             for ip, c in self.clients.items():
#                 print("Test",ip)
# =============================================================================
            if len(client_list) == 0:
                self.print_time_stamped('0 clients connected!')
            else:
                headers = client_list[0].keys()
                rows = [list(item.values()) for item in client_list]
                table = tabulate(rows, headers=headers, tablefmt="grid")
                print(table)

            threading.Event().wait(10)  # Wait for 30 seconds

    def broadcast_thread(self):
        data_format = 'string'
        channel_names = ["host", "port"]
        n_channels = len(channel_names)
        name = "ObserverInfoStream"
        info = pylsl.StreamInfo(name=name, type='observer_info', channel_count=n_channels,
                                 channel_format=data_format, source_id='server_info_id')

        chns = info.desc().append_child("channels")
        for chan_ix, label in enumerate(channel_names):
            ch = chns.append_child("channel")
            ch.append_child_value("label", label)

        outlet = pylsl.StreamOutlet(info)

        observerInfo = [self.host, str(self.port)]
        while True:
            outlet.push_sample(observerInfo)
            threading.Event().wait(5)  # Wait for 5 seconds

    def start_all(self, script_name):
        clients = self.clients.copy()
        self.print_time_stamped(f"Starting {script_name}")
        for k, v in clients.items():
            self.send_to(k, f'start,{script_name}')

    def stop_all(self, script_name):
        clients = self.clients.copy()
        for k, v in clients.items():
            self.print_time_stamped(f"Stopping {script_name} on {k}")
            self.send_to(k, f'stop,{script_name}')


if __name__ =="__main__":
    ip = get_lan_ip()

    # total number of robots in the current experiment
    num_of_robots = 1

    server = Observer(host=ip, port=12346)
    server.run()
    print("Num of Clients:", server.clients.items())
    script = 'RVR_Vicon_Swarm_Controller/rvr_vicon_swarm_controller.py'
    # script = 'rvr_scripts/rvr_vicon_swarm_controller.py'
    #script = 'rvr_vicon_swarm_controller.py'
    sleep(10)

    print("Wait until all robots connected to the observer...")
 
    print("Wait until all robots connected to the observer...")
    while len(server.clients.items()) != num_of_robots:
        sleep(2)


    if len(server.clients.items()) == num_of_robots:
       
        server.start_all(script)
        sleep(120)
        server.stop_all(script)
