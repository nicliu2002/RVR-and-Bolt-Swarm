import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

file_path = r"final_trials\Random trial 3.csv"  # Replace with your actual file path

# Manually load the first few lines of the CSV to extract robot names
with open(file_path, 'r') as file:
    lines = file.readlines()

# Extract the robot names from the third line
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

# Downsample the data (every 20th row)
df = df[::40].reset_index(drop=True)

# Dictionary to store x and y coordinates for each robot
robot_coords = {}

# Extract X and Y coordinates dynamically for each robot
for robot in robot_names:
    robot_coords[robot] = {
        'x': df[f'TX_{robot}'].values,
        'y': df[f'TY_{robot}'].values
    }

# Define the trail length
trail_length = 30  # Number of points to show in the trail

# Create a figure and axis for the plot
fig, ax = plt.subplots()
ax.set_xlim(-2500, 2500)
ax.set_ylim(-2500, 2500)

ax.set_title("Movement Paths of Robots")
ax.set_xlabel("X Coordinate (mm)")
ax.set_ylabel("Y Coordinate (mm)")

# Initialize lines and arrows for each robot
colors = ['b', 'r', 'g', 'm', 'c', 'y', 'k']  # Expand the list if needed
lines = {}
arrows = {}  # Dictionary to store arrow patches for each robot

for i, robot in enumerate(robot_names):
    lines[robot], = ax.plot([], [], colors[i % len(colors)] + '-', lw=2, label=robot)
    arrows[robot] = None  # Initialize arrows to None

# Add a legend
ax.legend()

# Update function for the animation
def update(frame):
    start = max(0, frame - trail_length)

    artists = []  # Collect all artist objects to return

    # Update each robot's trail dynamically
    for i, robot in enumerate(robot_names):
        x_data = robot_coords[robot]['x'][start:frame+1]
        y_data = robot_coords[robot]['y'][start:frame+1]
        lines[robot].set_data(x_data, y_data)
        artists.append(lines[robot])  # Add line to artists list

        # Remove old arrow if it exists
        if arrows[robot] is not None:
            arrows[robot].remove()
            arrows[robot] = None

        # Add arrow to indicate direction
        if len(x_data) > 1:
            dx = x_data[-1] - x_data[-2]
            dy = y_data[-1] - y_data[-2]
            arrows[robot] = ax.arrow(x_data[-2], y_data[-2], dx, dy,
                                     head_width=100, head_length=100,
                                     fc=colors[i % len(colors)],
                                     ec=colors[i % len(colors)],
                                     length_includes_head=True)
            artists.append(arrows[robot])  # Add arrow to artists list

    return artists  # Return the list of artist objects

# Create the animation
ani = FuncAnimation(fig, update, frames=len(df), interval=50, blit=True)

# Save the animation as a video file (e.g., MP4)
ani.save(r'location_plot_videos\Random trial 3.mp4', writer='ffmpeg', dpi=200)

# Display the plot
plt.show()
