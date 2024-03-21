"""
Robot client script

The script runs on Raspberry Pi automatically on boot and is used to manage communication with the robot

@ author    Essam Debie
@ version   1.0
"""

#!/usr/bin/env python3

import atexit
import datetime
import os
import platform
import signal
import socket
import subprocess
import sys
import threading
import time

from pylsl import resolve_stream, StreamInlet

# Disable output buffering
if hasattr(os, "devnull"):
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONHASHSEED"] = "1"
    os.environ["LANG"] = "en_US.UTF-8"
    os.environ["LC_ALL"] = "en_US.UTF-8"
    os.environ["LC_CTYPE"] = "en_US.UTF-8"


class Client:
    def __init__(self, host=None, port=1234):
        self.client_socket = None
        self.host = host
        self.port = port

        self.connected = False

        self.is_running = True  # Flag to indicate if the client is running
        self.received_signal = False
        atexit.register(self.atexit_cleanup)
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), './rvr_config.txt'), 'r') as file:
                contents = file.read()
            self.robot_name = contents.strip().split('=')[1]
        except Exception as e:
            print(e)
            self.robot_name = 'Unknown'

        self.delay = 1  # time to wait before attempting reconnect

        # Dictionary to store running subprocesses
        self.running_scripts = {}
        # self.working_directory = str(os.path.dirname(os.path.abspath(__file__))) + "\\"
        self.working_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rvr_scripts")

        threading.Thread(target=self.observer_discovery2).start()
        # threading.Thread(target=self.connecting_thread).start()
        # discovery_thread.start()

        self.print_time_stamped(f"Client is running and waiting for the observer to come online...")
    #
    def atexit_cleanup(self):
        print("Performing cleanup before exit...")
        # self.received_signal = True

    def handle_exit(self, signum, frame):
        self.is_running = False

        # Stop all running scripts
        for script_name in self.running_scripts:
            process, output_thread = self.running_scripts[script_name]
            if process.poll() is None:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Terminate the process group
                output_thread.join()

        # Close the client socket
        self.connected = False
        if self.client_socket:
            self.client_socket.close()

        print("Client stopped!")
        # Exit the program
        sys.exit()

    def __name__(self):
        return f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

    def print_time_stamped(self, msg):
        print(f"{self.__name__()}: {msg}")

    def capture_output(self, process):
        print("Starting capture_output function...")
        while True:
            response = ' '.join([line for line in process.stdout])
            self.print_time_stamped(response)

            if process.poll() is not None:
                # Process has terminated
                if self.connected:
                    self.send_data(response)
                print(f'process has terminated!')
                break

    def _connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.client_socket.send(f"{self.robot_name}".encode())
        self.connected = True
        self.print_time_stamped(f"Connected to the observer at {self.host}:{self.port}")
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()

    def run(self):
        def wait_msg():
            self.print_time_stamped(f"The observer not active or not responding, trying to connect in {self.delay} seconds...")
            time.sleep(self.delay)

        while True:
            if not self.is_running:
                break
            try:
                if not self.connected:
                    if self.host:
                        self._connect()
                    else:
                        wait_msg()
                else:
                    time.sleep(self.delay)
            except Exception as e:
                wait_msg()

    # def observer_discovery(self):
    #     print('Debug: waiting for broadcast connection!')
    #     discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #     discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #     discovery_socket.bind(('', 12345))  # Bind to the broadcast port
    #
    #     while True:
    #         if not self.is_running:
    #             break
    #
    #         data, address = discovery_socket.recvfrom(1024)  # Receive data from the observer
    #         if data.decode().startswith('rvr observer'):
    #             host = data.decode().split(':')[1].strip()
    #             port = int(data.decode().split(':')[2].strip())
    #             if host is not None and (host != self.host or port != self.port):
    #                 self.host = host
    #                 self.port = port
    #                 self.print_time_stamped(f"The observer found at {self.host}: {self.port}")
    #                 # self._connect()
    #         # else:
    #         #     if not self.connected:
    #         #         self.print_time_stamped(f"The observer not active or not responding, trying again in {self.delay} seconds...")
    #         #         time.sleep(self.delay)

    def observer_discovery2(self):
        print("looking for Observer stream...")
        streams = resolve_stream('type', 'observer_info')

        # create a new inlet to read from the stream
        self.inlet = StreamInlet(streams[0])

        while True:
            if not self.is_running:
                break
            try:
                sample, _ = self.inlet.pull_sample()
                host = sample[0]
                port = int(sample[1])

                if host is not None and (host != self.host or port != self.port):
                    self.host = host
                    self.port = port
                    self.print_time_stamped(f"The observer found at {self.host}: {self.port}")
            except Exception as e:
                print(e)
                pass

    def receive_data(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    self.print_time_stamped("Connection with the observer lost!")
                    self.connected = False
                    self.client_socket.close()
                    break

                # Receive command and script name from the client
                if ',' not in data:
                    continue

                command, script_name = data.split(',')
                if command == 'start':
                    print(f"starting {script_name}")
                    # Check if the script is already running
                    if script_name in self.running_scripts and self.running_scripts[script_name][0].poll() is None:
                        response = f"{script_name} is already running!"
                        print("debug: is already running!")
                    else:
                        if not os.path.exists(os.path.join(self.working_directory, script_name)):
                            response = "Script does not exist."
                            self.print_time_stamped(response)
                            continue

                        try:
                            # Start the script as a subprocess
                            current_os = platform.system()
                            py_cmd = 'python3' if current_os == 'Linux' else 'python'
                            # py_cmd = 'python3'
                            process = subprocess.Popen([py_cmd,
                                                        # self.working_directory+script_name
                                                        os.path.join(self.working_directory, script_name)
                                                        ],
                                                       stdout=subprocess.PIPE,
                                                       stderr=subprocess.STDOUT,
                                                       bufsize=0,
                                                       universal_newlines=True)
                            # Create a separate thread to capture and print the output
                            output_thread = threading.Thread(target=self.capture_output, args=(process,))
                            output_thread.start()
                            self.running_scripts[script_name] = (process, output_thread)
                            response = f"{script_name} started successfully!"
                        except Exception as e:
                            self.print_time_stamped("Error launching subprocess:", str(e))
                elif command == 'stop':
                    # Check if the script is running
                    if script_name in self.running_scripts and self.running_scripts[script_name][0].poll() is None:
                        # Terminate the subprocess
                        self.running_scripts[script_name][0].terminate()
                        del self.running_scripts[script_name]
                        response = f"{script_name} stopped successfully!"
                        print('debug: stopped!')
                    else:
                        response = f"No running {script_name} to stop!"
                else:
                    response = "Invalid command!"

                # print(f"Received data from observer: {data}")
            except ConnectionResetError and OSError:
                self.connected = False
                return
            except Exception as e:
                response = e
                self.print_time_stamped(e)
            finally:
                if self.connected:
                    self.send_data(response)

    def send_data(self, message):
        if self.connected:
            try:
                self.client_socket.send(message.encode())
            except Exception as e:
                self.print_time_stamped(f"Error while sending data to the observer: {str(e)}")
        else:
            self.print_time_stamped("Connection to the observer lost!")


if __name__ == "__main__":
    client = Client(port=1234)
    client.run()
    # client.connect()
