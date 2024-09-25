import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load the cleaned CSV data
df = pd.read_csv('3 bolt test.csv', skiprows=4)
df.columns = ['Frame', 'Sub Frame', 'RX_SB_5938', 'RY_SB_5938', 'RZ_SB_5938', 'TX_SB_5938', 'TY_SB_5938', 'TZ_SB_5938',
              'RX_SB_8427', 'RY_SB_8427', 'RZ_SB_8427', 'TX_SB_8427', 'TY_SB_8427', 'TZ_SB_8427',
              'RX_SB_CE32', 'RY_SB_CE32', 'RZ_SB_CE32', 'TX_SB_CE32', 'TY_SB_CE32', 'TZ_SB_CE32']

# Extract the X and Y coordinates from SB-5938
x_coords = df['TX_SB_5938']
y_coords = df['TY_SB_5938']

# Create a figure and axis for the animation
fig, ax = plt.subplots()
line, = ax.plot([], [], 'bo-', lw=2)

# Set up plot limits based on the data range
ax.set_xlim(min(x_coords) - 10, max(x_coords) + 10)
ax.set_ylim(min(y_coords) - 10, max(y_coords) + 10)
ax.set_title("Movement Animation for SB-5938")
ax.set_xlabel("X Coordinate (mm)")
ax.set_ylabel("Y Coordinate (mm)")

# Initialize the plot
def init():
    line.set_data([], [])
    return line,

# Update function for animation
def update(frame):
    line.set_data(x_coords[:frame+1], y_coords[:frame+1])
    return line,

# Create animation
ani = FuncAnimation(fig, update, frames=len(x_coords), init_func=init, blit=True, interval=500)

# Display the animation
plt.show()
