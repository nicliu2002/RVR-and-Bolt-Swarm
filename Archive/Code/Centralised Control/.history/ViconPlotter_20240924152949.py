import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Define the column names
column_names = ['Frame', 'Sub_Frame',
                'RX1', 'RY1', 'RZ1', 'TX1', 'TY1', 'TZ1',
                'RX2', 'RY2', 'RZ2', 'TX2', 'TY2', 'TZ2',
                'RX3', 'RY3', 'RZ3', 'TX3', 'TY3', 'TZ3']

# Read the data file, skipping the first three rows
df = pd.read_csv('data.txt', sep='\s+', skiprows=3, names=column_names)

# Convert all data to numeric, coerce errors to NaN
df = df.apply(pd.to_numeric, errors='coerce')

# Extract TX and TY coordinates for each dataset
TX1, TY1 = df['TX1'], df['TY1']
TX2, TY2 = df['TX2'], df['TY2']
TX3, TY3 = df['TX3'], df['TY3']

# Set up the plot
fig, ax = plt.subplots()
line1, = ax.plot([], [], 'bo', label='Dataset 1')
line2, = ax.plot([], [], 'ro', label='Dataset 2')
line3, = ax.plot([], [], 'go', label='Dataset 3')

# Define plot limits
min_x = min(TX1.min(), TX2.min(), TX3.min()) - 10
max_x = max(TX1.max(), TX2.max(), TX3.max()) + 10
min_y = min(TY1.min(), TY2.min(), TY3.min()) - 10
max_y = max(TY1.max(), TY2.max(), TY3.max()) + 10
ax.set_xlim(min_x, max_x)
ax.set_ylim(min_y, max_y)

# Label axes and set title
ax.set_xlabel('TX (mm)')
ax.set_ylabel('TY (mm)')
ax.set_title('Animation Plot')
ax.legend()

# Initialization function
def init():
    line1.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    return line1, line2, line3

# Animation function
def animate(i):
    line1.set_data([TX1.iloc[i]], [TY1.iloc[i]])
    line2.set_data([TX2.iloc[i]], [TY2.iloc[i]])
    line3.set_data([TX3.iloc[i]], [TY3.iloc[i]])
    return line1, line2, line3

# Create animation
ani = animation.FuncAnimation(fig, animate, frames=len(df), init_func=init,
                              interval=200, blit=True)

# Display the plot
plt.show()
