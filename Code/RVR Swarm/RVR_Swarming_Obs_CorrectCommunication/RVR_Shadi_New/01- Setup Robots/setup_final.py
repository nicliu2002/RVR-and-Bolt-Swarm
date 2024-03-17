"""
Robot Setup Script

@ author    Essam Debie
@ version   1.0
"""


import time
import paramiko
import os
from paramiko.ssh_exception import SSHException

import CONFIG


N = 10
n = 1


def print_step(msg):
    global n
    print(f"{n}/{N}: {msg}")
    n = n+1


def exec_command(ssh, comm):
    stdin, stdout, stderr = ssh.exec_command(comm)
    output = stdout.read().decode()
    errors = stderr.read().decode()
    status = stdout.channel.recv_exit_status()  # 0 is success
    return status ==0, output, errors


def make_remote_dir(sftp, remote_dir):
    # Create every directory in the remote_dir path if it does not exist
    dirs_to_create = remote_dir.split('/')
    current_dir = ''
    for directory in dirs_to_create:
        current_dir += directory + '/'
        try:
            sftp.listdir(current_dir)
        except FileNotFoundError:
            sftp.mkdir(current_dir)


# Recursive function to send files and directories
def send_dir(ssh, local_path, remote_path):
    sftp = ssh.open_sftp()
    # Check if local_path is a file
    if os.path.isfile(local_path):
        sftp.put(local_path, remote_path)
    # Check if local_path is a directory
    elif os.path.isdir(local_path):
        make_remote_dir(sftp, remote_path)
        # Iterate over the files and subdirectories in the local directory
        for item in os.listdir(local_path):
            # Recursively send each file or subdirectory
            send_dir(ssh, f"{local_path}/{item}", f"{remote_path}/{item}")


def send_file(ssh, local_path, remote_path):
    sftp = ssh.open_sftp()

    # Create remote directory if it does not exist
    remote_dir = os.path.dirname(remote_path)
    try:
        sftp.stat(remote_dir)
    except IOError as e:
        # Create every directory in the remote_dir path if it does not exist
        make_remote_dir(sftp, remote_dir)
        pass

    sftp.put(local_path, remote_path)
    sftp.close()


def reboot_client(ssh, ip_address, new_ip_address = None):
    try:
        # Reboot Raspberry Pi
        ssh.exec_command('sudo reboot')
        # Wait for Raspberry Pi to come back online
        time.sleep(5)
        timeout = 120
        start_time = time.time()
        while True:
            try:
                if new_ip_address is None:
                    new_ip_address = ip_address
                ssh.connect(new_ip_address, username=CONFIG.user, password=CONFIG.password)
                ssh.close()
                break
            except (TimeoutError, SSHException) as e:
                if time.time() - start_time >= timeout:
                    raise TimeoutError('Raspberry Pi did not come back online')
                print('    - Waiting for raspberry Pi to reboot...')
                time.sleep(2)
        print('     - Raspberry Pi rebooted and is back online.')
    except Exception as e:
        print(f"Error restarting Raspberry Pi: {e}")


def run_on_startup(ssh):
    script_path = f'{CONFIG.remote_path}{CONFIG.local_path}'
    # Remove existing symlink if it exists
    existing_symlink_path = '/etc/systemd/system/rvr_client.service'
    try:
        ssh.exec_command(f'sudo test -L {existing_symlink_path}')
        # ssh.exec_command(f'sudo rm {existing_symlink_path}')
        # print(f"     └──> Removed existing symlink at {existing_symlink_path}")
    except Exception as e:
        print(f"     └──> Exception: {e}")
        pass

    service_unit_content = f'''\
    [Unit]
    Description=RVR client
    After=network.target

    [Service]
    ExecStart=/usr/bin/python3 {script_path} > {os.path.join(CONFIG.remote_path, "rvr_client.log")} 2> {os.path.join(CONFIG.remote_path, "rvr_client_error.log")}

    WorkingDirectory={CONFIG.remote_path}
    StandardOutput=file:{os.path.join(CONFIG.remote_path, "rvr_client.log")}
    StandardError=file:{os.path.join(CONFIG.remote_path, "rvr_client_error.log")}
    Restart=always
    ExecStop=/bin/kill -SIGTERM %p
    User=pi

    [Install]
    WantedBy=multi-user.target
    '''

    unit_file_path = f'{CONFIG.remote_path}rvr_client.service'

    with ssh.open_sftp() as sftp:
        with sftp.file(unit_file_path, 'w') as f:
            f.write(service_unit_content)

    # Reload systemd to apply the changes
    success, stdout, stderr = exec_command(ssh, 'sudo systemctl daemon-reload')
    if not success:
        print(f" - Error starting {script_path} on startup!")

    # Enable and start the service
    success, stdout, stderr = exec_command(ssh,
                                           f'sudo systemctl enable {CONFIG.remote_path}rvr_client.service && sudo systemctl start rvr_client')
    if not success:
        print(f" - Error starting {script_path} on startup!")

########################################################################################


def install_pylsl(ssh):
    print_step("Installing lsl package...")
    send_file(ssh, './lsl/pylsl-1.16.1-py2.py3-none-any.whl', '/home/pi/temp/lsl/pylsl-1.16.1-py2.py3-none-any.whl')
    status, output, errors = exec_command(ssh, comm="cd /home/pi/temp/lsl/ ; python3 -m pip install pylsl-1.16.1-py2.py3-none-any.whl")
    print(f"    - liblsl installed successfully")
    send_file(ssh, './lsl/liblsl.so', '/home/pi/.local/lib/python3.7/site-packages/pylsl/lib/liblsl.so')
    print(f"    - liblsl.so file transferred successfully")


def send_client_and_config(ssh):
    print_step(f"Transferring {CONFIG.local_path} to {CONFIG.remote_path}...")
    with open('rvr_config.txt', 'w') as file:
        # Write the variable value to the file
        file.write(f'name={CONFIG.name}')
    send_file(ssh, './rvr_config.txt', CONFIG.remote_path + 'rvr_config.txt')
    send_file(ssh, CONFIG.local_path, f'{CONFIG.remote_path}/{CONFIG.local_path}')
    print(f"    - {CONFIG.local_path}  file transferred successfully")


def run_client_onstartup(ssh):
    print_step(f"Adding {CONFIG.remote_path}{CONFIG.local_path} to startup script...")
    run_on_startup(ssh=ssh)
    print(f'    - {CONFIG.remote_path + CONFIG.local_path} script has been added to startup successfully!')


def send_user_scripts(ssh):
    print_step("Transferring rvr_scripts directory...")
    send_dir(ssh, './rvr_scripts', f'{CONFIG.remote_path}rvr_scripts')


def reboot_client(ssh):
    print_step(f"Rebooting client at {CONFIG.ipaddress}!")
    reboot_client(ssh, CONFIG.ipaddress)
########################################################################################


def setup(curr_ip_address):
    try:
        # Set up the SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(curr_ip_address, username=CONFIG.user, password=CONFIG.password)

        setup_funcs = [
            install_pylsl,
            send_client_and_config,
            run_client_onstartup,
            send_user_scripts,
            # reboot_client
        ]
        global N
        N = len(setup_funcs)

        for f in setup_funcs:
            f(ssh)
        print('-------------------------------')
        print(f"Raspberry Pi setup completed!")

    except Exception as e:
        print(e)
    finally:
        # Close the SSH connection
        ssh.close()


if __name__ == '__main__':
    setup(curr_ip_address=CONFIG.current_ip)
