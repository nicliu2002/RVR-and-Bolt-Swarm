import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

# Load the cleaned CSV data
df = pd.read_csv('RVR Updated 2.csv', skiprows=4)
df.columns = ['Frame', 'Sub Frame', 
              'RX_SB_8427', 'RY_SB_8427', 'RZ_SB_8427', 'TX_SB_8427', 'TY_SB_8427', 'TZ_SB_8427', 
              'RX_SB_CE32', 'RY_SB_CE32', 'RZ_SB_CE32', 'TX_SB_CE32', 'TY_SB_CE32', 'TZ_SB_CE32', 
              'RX_RVR1', 'RY_RVR1', 'RZ_RVR1', 'TX_RVR1', 'TY_RVR1', 'TZ_RVR1',
              'RX_RVR4', 'RY_RVR4', 'RZ_RVR4', 'TX_RVR4', 'TY_RVR4', 'TZ_RVR4']

# Downsample the data (every 5th row)
df = df[::5]

# Extract X and Y coordinates for each entity
x_coords_sb_8427 = df['TX_SB_8427']
y_coords_sb_8427 = df['TY_SB_8427']

x_coords_sb_ce32 = df['TX_SB_CE32']
y_coords_sb_ce32 = df['TY_SB_CE32']

x_coords_rvr1 = df['TX_RVR1']
y_coords_rvr1 = df['TY_RVR1']

x_coords_rvr4 = df['TX_RVR4']
y_coords_rvr4 = df['TY_RVR4']

# Define the trail length and fade-out effect
trail_length = 10  # Number of points to show in the trail
fade_factor = 0.1  # How much each segment fades out (smaller value means more fade)

# Create a figure and axis for the animation
fig, ax = plt.subplots()
ax.set_xlim(-2500, 2500)
ax.set_ylim(-2500, 2500)

ax.set_title("Movement Paths of SB-8427, SB-CE32, RVR1, and RVR4")
ax.set_xlabel("X Coordinate (mm)")
ax.set_ylabel("Y Coordinate (mm)")

# Initialize the lines for each entity
line1, = ax.plot([], [], 'bo-', lw=2, label='SB-8427')
line2, = ax.plot([], [], 'rx-', lw=2, label='SB-CE32')
line3, = ax.plot([], [], 'gs-', lw=2, label='RVR1')
line4, = ax.plot([], [], 'm^-', lw=2, label='RVR4')  # Added for RVR4

# Add a legend
ax.legend()

# Initialize the plot with empty data
def init():
    line1.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    line4.set_data([], [])  # Added for RVR4
    return line1, line2, line3, line4

# Update function for animation
def update(frame):
    # For each entity, plot only the last 'trail_length' points with fading
    start = max(0, frame - trail_length)
    
    # Get segments for each entity
    x1, y1 = x_coords_sb_8427[start:frame+1], y_coords_sb_8427[start:frame+1]
    x2, y2 = x_coords_sb_ce32[start:frame+1], y_coords_sb_ce32[start:frame+1]
    x3, y3 = x_coords_rvr1[start:frame+1], y_coords_rvr1[start:frame+1]
    x4, y4 = x_coords_rvr4[start:frame+1], y_coords_rvr4[start:frame+1]
    
    # Set the trail for each entity
    line1.set_data(x1, y1)
    line2.set_data(x2, y2)
    line3.set_data(x3, y3)
    line4.set_data(x4, y4)  # Added for RVR4
    
    return line1, line2, line3, line4

# Create the animation
ani = FuncAnimation(fig, update, frames=len(df), init_func=init, blit=True, interval=0.05)

# Save the animation as a GIF using PillowWriter
ani.save("hetero.gif", writer=PillowWriter(fps=30))

# Display the animation (optional)
plt.show()
