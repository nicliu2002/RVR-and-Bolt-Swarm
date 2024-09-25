import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Load the cleaned CSV data
df = pd.read_csv('3 bolt test.csv', skiprows=4)
df.columns = ['Frame', 'Sub Frame', 'RX_SB_5938', 'RY_SB_5938', 'RZ_SB_5938', 'TX_SB_5938', 'TY_SB_5938', 'TZ_SB_5938',
              'RX_SB_8427', 'RY_SB_8427', 'RZ_SB_8427', 'TX_SB_8427', 'TY_SB_8427', 'TZ_SB_8427',
              'RX_SB_CE32', 'RY_SB_CE32', 'RZ_SB_CE32', 'TX_SB_CE32', 'TY_SB_CE32', 'TZ_SB_CE32']

# Extract X and Y coordinates for each robot
x_coords_sb_5938 = df['TX_SB_5938']
y_coords_sb_5938 = df['TY_SB_5938']

x_coords_sb_8427 = df['TX_SB_8427']
y_coords_sb_8427 = df['TY_SB_8427']

x_coords_sb_ce32 = df['TX_SB_CE32']
y_coords_sb_ce32 = df['TY_SB_CE32']

# Define the trail length and fade-out effect
trail_length = 10  # Number of points to show in the trail
fade_factor = 0.1  # How much each segment fades out (smaller value means more fade)

# Create a figure and axis for the animation
fig, ax = plt.subplots()
ax.set_xlim(min(x_coords_sb_5938.min(), x_coords_sb_8427.min(), x_coords_sb_ce32.min()) - 10, 
            max(x_coords_sb_5938.max(), x_coords_sb_8427.max(), x_coords_sb_ce32.max()) + 10)
ax.set_ylim(min(y_coords_sb_5938.min(), y_coords_sb_8427.min(), y_coords_sb_ce32.min()) - 10, 
            max(y_coords_sb_5938.max(), y_coords_sb_8427.max(), y_coords_sb_ce32.max()) + 10)

ax.set_title("Movement Paths of SB-5938, SB-8427, and SB-CE32")
ax.set_xlabel("X Coordinate (mm)")
ax.set_ylabel("Y Coordinate (mm)")

# Initialize the lines for each robot
line1, = ax.plot([], [], 'bo-', lw=2, label='SB-5938')
line2, = ax.plot([], [], 'rx-', lw=2, label='SB-8427')
line3, = ax.plot([], [], 'gs-', lw=2, label='SB-CE32')

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
    # For each robot, plot only the last 'trail_length' points with fading
    start = max(0, frame - trail_length)
    
    # Get segments for each robot
    x1, y1 = x_coords_sb_5938[start:frame+1], y_coords_sb_5938[start:frame+1]
    x2, y2 = x_coords_sb_8427[start:frame+1], y_coords_sb_8427[start:frame+1]
    x3, y3 = x_coords_sb_ce32[start:frame+1], y_coords_sb_ce32[start:frame+1]
    
    # Set the trail for each robot
    line1.set_data(x1, y1)
    line2.set_data(x2, y2)
    line3.set_data(x3, y3)
    
    # Apply fade effect by setting the alpha (transparency) of each trail
    for i, (line, x, y) in enumerate(zip([line1, line2, line3], [x1, x2, x3], [y1, y2, y3])):
        # Create fading effect by reducing the alpha for each point
        for j in range(len(x)):
            alpha = 1 - fade_factor * (len(x) - j - 1)
            if i == 0:
                line.set_markerfacecolor((0, 0, 1, alpha))  # Blue with fading for SB-5938
            elif i == 1:
                line.set_markerfacecolor((1, 0, 0, alpha))  # Red with fading for SB-8427
            elif i == 2:
                line.set_markerfacecolor((0, 1, 0, alpha))  # Green with fading for SB-CE32
    
    return line1, line2, line3

# Create the animation
ani = FuncAnimation(fig, update, frames=len(df), init_func=init, blit=True, interval=5)

# Display the animation
plt.show()
