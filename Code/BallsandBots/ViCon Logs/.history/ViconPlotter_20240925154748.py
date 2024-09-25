import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import numpy as np

file_path = "Initial 2 Bolt 2 RVR.csv"  # Replace with your actual file path
save_path = "Initial 2 Bolt 2 RVR.mp4"

# Manually load the first few lines of the CSV to extract robot names
with open(file_path, 'r') as file:
    lines = file.readlines()

# Extract the robot names from the third line
# The robot names are formatted as 'Global Angle <robot>:<robot>' in the third line
robot_line = lines[2]  # This is the third line in the file
robot_names = [name.split(':')[0].split()[-1] for name in robot_line.split(',') if 'Global Angle' in name]

# Load the actual CSV data, skipping the first 4 rows of metadata
df = pd.read_csv(file_path, skiprows=4)

# Dynamically assign column names based on the extracted robot names
columns = ['Frame', 'Sub Frame']
for robot in robot_names:
    columns += [f'RX_{robot}', f'RY_{robot}', f'RZ_{robot}', f'TX_{robot}', f'TY_{robot}', f'TZ_{robot}']

# Assign these dynamic columns to the dataframe
df.columns = columns

# Downsample the data (every 5th row)
df = df[::10]

# Dictionary to store x and y coordinates for each robot
robot_coords = {}

# Extract X and Y coordinates dynamically for each robot
for robot in robot_names:
    robot_coords[robot] = {
        'x': df[f'TX_{robot}'],
        'y': df[f'TY_{robot}']
    }

# Define the trail length and fade-out effect
trail_length = 10  # Number of points to show in the trail
fade_factor = 0.1  # How much each segment fades out (smaller value means more fade)

# Create a figure and axis for the animation
fig, ax = plt.subplots()
ax.set_xlim(-2500, 2500)
ax.set_ylim(-2500, 2500)

ax.set_title("Movement Paths of Robots")
ax.set_xlabel("X Coordinate (mm)")
ax.set_ylabel("Y Coordinate (mm)")

# Initialize lines for each robot and assign distinct colors and markers dynamically
colors = ['bo-', 'rx-', 'gs-', 'm^-']  # List of color/marker combinations
lines = {}
for i, robot in enumerate(robot_names):
    lines[robot], = ax.plot([], [], colors[i % len(colors)], lw=2, label=robot)

# Add a legend
ax.legend()

# Initialize the plot with empty data
def init():
    for robot in robot_names:
        lines[robot].set_data([], [])
    return lines.values()

# Update function for animation
def update(frame):
    start = max(0, frame - trail_length)
    
    # Update each robot's trail dynamically
    for robot in robot_names:
        x_data = robot_coords[robot]['x'][start:frame+1]
        y_data = robot_coords[robot]['y'][start:frame+1]
        lines[robot].set_data(x_data, y_data)
    
    return lines.values()

# Create the animation
ani = FuncAnimation(fig, update, frames=len(df), init_func=init, blit=True, interval=0.05)

# Save the animation as an MP4 video using FFMpegWriter
# Ensure you have ffmpeg installed (can be downloaded from https://ffmpeg.org/download.html)
writer = FFMpegWriter(fps=30, metadata=dict(artist='Me'), bitrate=1800)
ani.save(save_path, writer=writer)

# Display the animation (optional)
plt.show()
