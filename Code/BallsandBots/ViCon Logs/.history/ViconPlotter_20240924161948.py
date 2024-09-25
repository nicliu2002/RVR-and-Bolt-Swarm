import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

# Load the cleaned CSV data
df = pd.read_csv('3 RVR test 3.csv', skiprows=4)
df.columns = ['Frame', 'Sub Frame', 
              'RX_RVR1', 'RY_RVR1', 'RZ_RVR1', 'TX_RVR1', 'TY_RVR1', 'TZ_RVR1', 
              'RX_RVR2', 'RY_RVR2', 'RZ_RVR2', 'TX_RVR2', 'TY_RVR2', 'TZ_RVR2', 
              'RX_RVR5', 'RY_RVR5', 'RZ_RVR5', 'TX_RVR5', 'TY_RVR5', 'TZ_RVR5']

# Downsample the data (every 5th row)
df = df[::5]

# Extract X and Y coordinates for each RVR
x_coords_rvr1 = df['TX_RVR1']
y_coords_rvr1 = df['TY_RVR1']

x_coords_rvr2 = df['TX_RVR2']
y_coords_rvr2 = df['TY_RVR2']

x_coords_rvr5 = df['TX_RVR5']
y_coords_rvr5 = df['TY_RVR5']

# Define the trail length and fade-out effect
trail_length = 10  # Number of points to show in the trail
fade_factor = 0.1  # How much each segment fades out (smaller value means more fade)

# Create a figure and axis for the animation
fig, ax = plt.subplots()
ax.set_xlim(-2500, 2500)
ax.set_ylim(-2500, 2500)

ax.set_title("Movement Paths of RVR1, RVR2, and RVR5")
ax.set_xlabel("X Coordinate (mm)")
ax.set_ylabel("Y Coordinate (mm)")

# Initialize the lines for each RVR
line1, = ax.plot([], [], 'bo-', lw=2, label='RVR1')
line2, = ax.plot([], [], 'rx-', lw=2, label='RVR2')
line3, = ax.plot([], [], 'gs-', lw=2, label='RVR5')

# Add a legend
ax.legend()

# Initialize the plot with empty data
def init():
    line1.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    return line1, line2, line3

# Update function for animation
def update(frame):
    # For each RVR, plot only the last 'trail_length' points with fading
    start = max(0, frame - trail_length)
    
    # Get segments for each RVR
    x1, y1 = x_coords_rvr1[start:frame+1], y_coords_rvr1[start:frame+1]
    x2, y2 = x_coords_rvr2[start:frame+1], y_coords_rvr2[start:frame+1]
    x3, y3 = x_coords_rvr5[start:frame+1], y_coords_rvr5[start:frame+1]
    
    # Set the trail for each RVR
    line1.set_data(x1, y1)
    line2.set_data(x2, y2)
    line3.set_data(x3, y3)
    
    return line1, line2, line3

# Create the animation
ani = FuncAnimation(fig, update, frames=len(df), init_func=init, blit=True, interval=0.05)

# Save the animation as a GIF using PillowWriter
ani.save("rvr_paths2.gif", writer=PillowWriter(fps=30))

# Display the animation (optional)
plt.show()
