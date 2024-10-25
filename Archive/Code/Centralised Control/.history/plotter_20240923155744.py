import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

# Function to load data from a txt file
def load_data(file_path):
    # Read the file while ignoring bad lines (with differing column counts)
    df = pd.read_csv(file_path, header=None, names=['time', 'object', 'x', 'y', 'velocity', 'theta'], 
                     on_bad_lines='skip')  # `on_bad_lines` skips lines with too many columns
    # Strip leading/trailing spaces from 'object' column
    df['object'] = df['object'].str.strip()
    return df

# Load data from the txt file (replace 'data.txt' with your actual file path)
df = load_data('all BOLT test.txt')

# Separate the data for each object
df_SB5938 = df[df['object'] == ' SB-5938'].reset_index(drop=True)
df_SBCE32 = df[df['object'] == ' SB-CE32'].reset_index(drop=True)

# Find the maximum number of frames
max_frames = max(len(df_SB5938), len(df_SBCE32))

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(-200, 200)
ax.set_ylim(-200, 200)
ax.set_xlabel('X Position')
ax.set_ylabel('Y Position')
ax.set_title('Positions and Velocity Vectors of SB-5938 and SB-CE32')

# Plot initialization
SB5938_point, = ax.plot([], [], 'bo', label='SB-5938')
SBCE32_point, = ax.plot([], [], 'ro', label='SB-CE32')

# Initialize quiver objects with empty data
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
    # Clear previous quiver plots
    global SB5938_vector, SBCE32_vector
    SB5938_vector.remove()
    SBCE32_vector.remove()
    
    # Update positions for SB-5938 if frame is within its data length
    if frame < len(df_SB5938):
        x_SB5938 = df_SB5938['x'].iloc[frame]
        y_SB5938 = df_SB5938['y'].iloc[frame]
        SB5938_point.set_data([x_SB5938], [y_SB5938])
        # Compute velocity components
        v_SB5938 = df_SB5938['velocity'].iloc[frame]
        theta_SB5938 = df_SB5938['theta'].iloc[frame]
        u_SB5938 = v_SB5938 * np.sin(np.radians(theta_SB5938))
        v_SB5938 = v_SB5938 * np.cos(np.radians(theta_SB5938))
        # Update quiver
        SB5938_vector = ax.quiver(x_SB5938, y_SB5938, u_SB5938, v_SB5938, color='blue', scale=50)
    else:
        SB5938_point.set_data([], [])
        SB5938_vector = ax.quiver([], [], [], [], color='blue', scale=50)
    
    # Update positions for SB-CE32 if frame is within its data length
    if frame < len(df_SBCE32):
        x_SBCE32 = df_SBCE32['x'].iloc[frame]
        y_SBCE32 = df_SBCE32['y'].iloc[frame]
        SBCE32_point.set_data([x_SBCE32], [y_SBCE32])
        # Compute velocity components
        v_SBCE32 = df_SBCE32['velocity'].iloc[frame]
        theta_SBCE32 = df_SBCE32['theta'].iloc[frame]
        u_SBCE32 = v_SBCE32 * np.sin(np.radians(theta_SBCE32))
        v_SBCE32 = v_SBCE32 * np.cos(np.radians(theta_SBCE32))
        # Update quiver
        SBCE32_vector = ax.quiver(x_SBCE32, y_SBCE32, u_SBCE32, v_SBCE32, color='red', scale=50)
    else:
        SBCE32_point.set_data([], [])
        SBCE32_vector = ax.quiver([], [], [], [], color='red', scale=50)
    
    return SB5938_point, SBCE32_point, SB5938_vector, SBCE32_vector

# Create the animation
ani = FuncAnimation(fig, update, frames=max_frames, init_func=init, blit=False, repeat=False)

# Display the animation
plt.legend()
plt.show()
