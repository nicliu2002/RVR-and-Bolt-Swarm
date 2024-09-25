import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

# Load the cleaned CSV data
df = pd.read_csv('hetero test 3.csv', skiprows=4)
df.columns = ['Frame', 'Sub Frame', 
              'RX_SB_8427', 'RY_SB_8427', 'RZ_SB_8427', 'TX_SB_8427', 'TY_SB_8427', 'TZ_SB_8427', 
              'RX_SB_CE32', 'RY_SB_CE32', 'RZ_SB_CE32', 'TX_SB_CE32', 'TY_SB_CE32', 'TZ_SB_CE32', 
              'RX_RVR5', 'RY_RVR5', 'RZ_RVR5', 'TX_RVR5', 'TY_RVR5', 'TZ_RVR5']

# Downsample the data (every 5th row)
df = df[::5]

# Extract X and Y coordinates for each entity
x_coords_sb_8427 = df['TX_SB_8427']
y_coords_sb_8427 = df['TY_SB_8427']

x_coords_sb_ce32 = df['TX_SB_CE32']
y_coords_sb_ce32 = df['TY_SB_CE32']

x_coords_rvr5 = df['TX_RVR5']
y_coords_rvr5 = df['TY_RVR5']

# Define the trail length and fade-out effect
trail_length = 10  # Number of points to show in the trail
fade_factor = 0.1  # How much each segment fades out (smaller value means more fade)

# Create a figure and axis for the animation
fig, ax = plt.subplots()
ax.set_xlim(-2500, 2500)
ax.set_ylim(-2500, 2500)

ax.set_title("Movement Paths of SB-8427, SB-CE32, and RVR5")
ax.set_xlabel("X Coordinate (mm)")
ax.set_ylabel("Y Coordinate (mm)")

# Initialize the lines for each entity
line1, = ax.plot([], [], 'bo-', lw=2, label='SB-8427')
line2, = ax.plot([], [], 'rx-', lw=2, label='SB-CE32')
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
    # For each entity, plot only the last 'trail_length' points with fading
    start = max(0, frame - trail_length)
    
    # Get segments for each entity
    x1, y1 = x_coords_sb_8427[start:frame+1], y_coords_sb_8427[start:frame+1]
    x2, y2 = x_coords_sb_ce32[start:frame+1], y_coords_sb_ce32[start:frame+1]
    x3, y3 = x_coords_rvr5[start:frame+1], y_coords_rvr5[start:frame+1]
    
    # Set the trail for each entity
    line1.set_data(x1, y1)
    line2.set_data(x2, y2)
    line3.set_data(x3, y3)
    
    return line1, line2, line3

# Create the animation
ani = FuncAnimation(fig, update, frames=len(df), init_func=init, blit=True, interval=0.05)

# Save the animation as a GIF using PillowWriter
ani.save("hetero.gif", writer=PillowWriter(fps=30))

# Display the animation (optional)
plt.show()
