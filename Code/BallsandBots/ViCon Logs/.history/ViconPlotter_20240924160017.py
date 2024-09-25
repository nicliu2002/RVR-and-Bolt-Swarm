import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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

# Create a figure and axis for the animation
fig, ax = plt.subplots()
line1, = ax.plot([], [], 'bo-', lw=2, label='SB-5938')
line2, = ax.plot([], [], 'rx-', lw=2, label='SB-8427')
line3, = ax.plot([], [], 'gs-', lw=2, label='SB-CE32')

# Set up plot limits based on the data range
ax.set_xlim(min(x_coords_sb_5938.min(), x_coords_sb_8427.min(), x_coords_sb_ce32.min()) - 10, 
            max(x_coords_sb_5938.max(), x_coords_sb_8427.max(), x_coords_sb_ce32.max()) + 10)
ax.set_ylim(min(y_coords_sb_5938.min(), y_coords_sb_8427.min(), y_coords_sb_ce32.min()) - 10, 
            max(y_coords_sb_5938.max(), y_coords_sb_8427.max(), y_coords_sb_ce32.max()) + 10)

ax.set_title("Movement Paths of SB-5938, SB-8427, and SB-CE32")
ax.set_xlabel("X Coordinate (mm)")
ax.set_ylabel("Y Coordinate (mm)")

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
    # Update the data for each robot
    line1.set_data(x_coords_sb_5938[:frame+1], y_coords_sb_5938[:frame+1])
    line2.set_data(x_coords_sb_8427[:frame+1], y_coords_sb_8427[:frame+1])
    line3.set_data(x_coords_sb_ce32[:frame+1], y_coords_sb_ce32[:frame+1])
    return line1, line2, line3

# Create the animation
ani = FuncAnimation(fig, update, frames=len(df), init_func=init, blit=True, interval=20)

# Display the animation
plt.show()
