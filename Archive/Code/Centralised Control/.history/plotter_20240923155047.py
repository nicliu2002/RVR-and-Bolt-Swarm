import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

# Function to load data from a txt file
def load_data(file_path):
    # First, let's read the file while ignoring bad lines (with differing column counts)
    df = pd.read_csv(file_path, header=None, names=['time', 'object', 'x', 'y', 'velocity', 'theta'], 
                     on_bad_lines='skip')  # `on_bad_lines` skips lines with too many columns
    return df

# Load data from the txt file (replace 'data.txt' with your actual file path)
df = load_data('all BOLT test.txt')
print(df)

# Separate the data for each object
df_SB5938 = df[df['object'] == 'SB-5938']
df_SBCE32 = df[df['object'] == 'SB-CE32']

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(-2000, 2000)
ax.set_ylim(-2000, 2000)

# Plot initialization
SB5938_point, = ax.plot([], [], 'bo', label='SB-5938')
SBCE32_point, = ax.plot([], [], 'ro', label='SB-CE32')
SB5938_vector = ax.quiver([], [], [], [], color='blue', scale=50)
SBCE32_vector = ax.quiver([], [], [], [], color='red', scale=50)

# Function to initialize the plot
def init():
    SB5938_point.set_data([], [])
    SBCE32_point.set_data([], [])
    SB5938_vector.set_UVC([], [])
    SBCE32_vector.set_UVC([], [])
    return SB5938_point, SBCE32_point, SB5938_vector, SBCE32_vector

# Function to update the plot
def update(frame):
    # Update positions
    SB5938_point.set_data(df_SB5938['x'].iloc[frame], df_SB5938['y'].iloc[frame])
    SBCE32_point.set_data(df_SBCE32['x'].iloc[frame], df_SBCE32['y'].iloc[frame])
    
    # Update velocity vectors
    SB5938_vector.set_offsets([df_SB5938['x'].iloc[frame], df_SB5938['y'].iloc[frame]])
    SBCE32_vector.set_offsets([df_SBCE32['x'].iloc[frame], df_SBCE32['y'].iloc[frame]])
    
    SB5938_vector.set_UVC(df_SB5938['velocity'].iloc[frame] * np.sin(np.radians(df_SB5938['theta'].iloc[frame])),
                          df_SB5938['velocity'].iloc[frame] * np.cos(np.radians(df_SB5938['theta'].iloc[frame])))
    
    SBCE32_vector.set_UVC(df_SBCE32['velocity'].iloc[frame] * np.sin(np.radians(df_SBCE32['theta'].iloc[frame])),
                          df_SBCE32['velocity'].iloc[frame] * np.cos(np.radians(df_SBCE32['theta'].iloc[frame])))
    
    return SB5938_point, SBCE32_point, SB5938_vector, SBCE32_vector

# Create the animation
ani = FuncAnimation(fig, update, frames=min(len(df_SB5938), len(df_SBCE32)), init_func=init, blit=True, repeat=False)

# Display the animation
plt.legend()
plt.show()
