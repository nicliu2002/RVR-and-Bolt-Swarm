import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

file_path = "Swarming Behaviour 1 test 5.csv"  # Replace with your actual file path

# Load and preprocess the data
with open(file_path, 'r') as file:
    lines = file.readlines()

robot_line = lines[2]
robot_names = [name.split(':')[0].split()[-1] for name in robot_line.split(',') if 'Global Angle' in name]

df = pd.read_csv(file_path, skiprows=4)
columns = ['Frame', 'Sub Frame']
for robot in robot_names:
    columns += [f'RX_{robot}', f'RY_{robot}', f'RZ_{robot}', f'TX_{robot}', f'TY_{robot}', f'TZ_{robot}']
df.columns = columns

# Downsample the data for clarity
df = df[::20]

# Handle NaN values by interpolation
df.interpolate(method='linear', limit_direction='forward', axis=0, inplace=True)

# Extract positions
positions = {}
for robot in robot_names:
    positions[robot] = df[[f'TX_{robot}', f'TY_{robot}']].values

# Identify the frame with the best swarming
# Calculate the centroid at each frame
centroids = df[[f'TX_{robot}' for robot in robot_names]].mean(axis=1), df[[f'TY_{robot}' for robot in robot_names]].mean(axis=1)
centroids = np.column_stack(centroids)

# Calculate average distance to centroid at each frame
avg_distances = []
for i in range(len(df)):
    distances = []
    for robot in robot_names:
        pos = positions[robot][i]
        centroid = centroids[i]
        distance = np.linalg.norm(pos - centroid)
        distances.append(distance)
    avg_distance = np.mean(distances)
    avg_distances.append(avg_distance)

# Find the frame with minimum average distance (best swarming)
best_swarm_frame = np.argmin(avg_distances)

# Define frames for starting, best swarming, and dispersing
frames = {
    'Starting': 0,
    'Best Swarming': best_swarm_frame,
    'Dispersing': len(df) - 1
}

# Create the plot
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
colors = plt.cm.get_cmap('tab10', len(robot_names))

for idx, (title, frame_idx) in enumerate(frames.items()):
    ax = axes[idx]
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('X Position (mm)', fontsize=14)
    ax.set_ylabel('Y Position (mm)', fontsize=14)
    ax.set_xlim(-2500, 2500)
    ax.set_ylim(-2500, 2500)
    ax.grid(True)

    for i, robot in enumerate(robot_names):
        # Plot the current position
        x, y = positions[robot][frame_idx]
        ax.plot(x, y, 'o', color=colors(i), label=f'Robot {robot}' if frame_idx == 0 else "")
        
        # Plot the trail
        if idx > 0:
            trail_indices = range(frames['Starting'], frame_idx + 1)
            trail_x = positions[robot][trail_indices, 0]
            trail_y = positions[robot][trail_indices, 1]
            ax.plot(trail_x, trail_y, '-', color=colors(i), alpha=0.7)
            # Add arrow to indicate direction
            if len(trail_x) > 1:
                ax.arrow(trail_x[-2], trail_y[-2],
                         trail_x[-1] - trail_x[-2],
                         trail_y[-1] - trail_y[-2],
                         shape='full', lw=0, length_includes_head=True,
                         head_width=50, color=colors(i))
    if frame_idx == 0:
        ax.legend(fontsize=12)

plt.tight_layout()
plt.show()
