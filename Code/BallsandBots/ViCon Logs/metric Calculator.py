import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull, distance
from sklearn.cluster import DBSCAN

# File paths (replace with your actual file paths)
file_path = "Swarming Behaviour 1 test 5.csv"

# Load the robot names from the third line of the CSV
with open(file_path, 'r') as file:
    lines = file.readlines()
robot_line = lines[2]
robot_names = [name.split(':')[0].split()[-1] for name in robot_line.split(',') if 'Global Angle' in name]

# Load the CSV data, skipping the first 4 rows of metadata
df = pd.read_csv(file_path, skiprows=4)

# Assign column names dynamically based on the robot names
columns = ['Frame', 'Sub Frame']
for robot in robot_names:
    columns += [
        f'RX_{robot}', f'RY_{robot}', f'RZ_{robot}',
        f'TX_{robot}', f'TY_{robot}', f'TZ_{robot}'
    ]
df.columns = columns

# Downsample the data for computational efficiency
df = df[::20].reset_index(drop=True)

# Interpolate missing values to handle NaNs
df.interpolate(method='linear', limit_direction='both', axis=0, inplace=True)
# Fill any remaining NaNs at the start or end using ffill and bfill
df.bfill(inplace=True)
df.ffill(inplace=True)

# Check if any NaNs remain
if df.isnull().values.any():
    print("Warning: DataFrame still contains NaN values after interpolation.")

# Extract positions and calculate velocities for each robot
positions = {}
velocities = {}
dt = 1  # Assuming a uniform time step; adjust if necessary

for robot in robot_names:
    # Positions
    pos = df[[f'TX_{robot}', f'TY_{robot}']].values
    positions[robot] = pos

    # Velocities (differences between consecutive positions)
    vel = np.diff(pos, axis=0) / dt
    velocities[robot] = vel

num_frames = len(df)

# Initialize lists to store metrics over time
collision_counts = []
flock_densities = []
groupings = []
straggler_counts = []
orders = []
subgroup_counts = []
diffusions = []

# Define parameters
vision_range = 1000  # Adjust based on your specific scenario (in mm)
half_vision_range = vision_range / 2

for t in range(num_frames):
    # Get positions of all robots at time t
    current_positions = np.array([positions[robot][t] for robot in robot_names])
    n = len(robot_names)

    # Check for NaN values and remove them
    valid_indices = ~np.isnan(current_positions).any(axis=1)
    valid_positions = current_positions[valid_indices]
    valid_n = valid_positions.shape[0]

    # If there are less than 2 valid positions, we cannot compute some metrics
    if valid_n < 2:
        # Append NaN or a default value to the metrics lists
        collision_counts.append(np.nan)
        flock_densities.append(np.nan)
        groupings.append(np.nan)
        straggler_counts.append(np.nan)
        orders.append(np.nan)
        subgroup_counts.append(np.nan)
        diffusions.append(np.nan)
        continue  # Skip to the next time step

    # Update n to the number of valid positions
    n = valid_n

    # --- Collision Count ---
    # Calculate pairwise distances
    distances = distance.pdist(valid_positions)
    # Count pairs where distance < half_vision_range
    collisions = np.sum(distances < half_vision_range)
    collision_counts.append(collisions)

    # --- Flock Density ---
    # Calculate the area of the convex hull formed by the robots
    try:
        hull = ConvexHull(valid_positions)
        area = hull.volume  # For 2D data, 'volume' gives the area
    except:
        area = 1e-6  # Avoid division by zero if hull cannot be formed
    flock_density = n / area
    flock_densities.append(flock_density)

    # --- Grouping (Cohesion) ---
    separation_distances = []
    for i in range(n):
        bi = valid_positions[i]
        bj = np.delete(valid_positions, i, axis=0)
        si = np.mean(np.linalg.norm(bi - bj, axis=1))
        separation_distances.append(si)
    grouping = np.mean(separation_distances)
    groupings.append(grouping)

    # --- Straggler Count ---
    straggler_count = 0
    for i in range(n):
        bi = valid_positions[i]
        bj = np.delete(valid_positions, i, axis=0)
        distances = np.linalg.norm(bi - bj, axis=1)
        # Check if the boid is farther than half_vision_range from all others
        if np.all(distances > half_vision_range):
            straggler_count += 1
    straggler_counts.append(straggler_count)

    # --- Order ---
    if t < num_frames - 1:
        current_velocities = np.array([velocities[robot][t] for idx, robot in enumerate(robot_names) if valid_indices[idx]])
        norms = np.linalg.norm(current_velocities, axis=1)
        norms[norms == 0] = 1e-6  # Prevent division by zero
        normalized_velocities = current_velocities / norms[:, np.newaxis]
        average_velocity = np.mean(normalized_velocities, axis=0)
        order = np.linalg.norm(average_velocity)
        orders.append(order)
    else:
        orders.append(orders[-1])  # Repeat last value if at the final frame

    # --- Subgroup Count ---
    # Only proceed if there are at least 2 valid positions
    if valid_n >= 2:
        clustering = DBSCAN(eps=vision_range, min_samples=2).fit(valid_positions)
        labels = clustering.labels_
        num_subgroups = len(set(labels)) - (1 if -1 in labels else 0)
        subgroup_counts.append(num_subgroups)
    else:
        subgroup_counts.append(0)  # Not enough data to form subgroups

    # --- Diffusion ---
    centroid = np.mean(valid_positions, axis=0)
    distances_from_centroid = np.linalg.norm(valid_positions - centroid, axis=1)
    diffusion = np.std(distances_from_centroid)
    diffusions.append(diffusion)

# Combine metrics into a DataFrame for analysis or plotting
metrics_df = pd.DataFrame({
    'Frame': df['Frame'],
    'Collision_Count': collision_counts,
    'Flock_Density': flock_densities,
    'Grouping': groupings,
    'Straggler_Count': straggler_counts,
    'Order': orders,
    'Subgroup_Count': subgroup_counts,
    'Diffusion': diffusions
})

# --- Data Visualization ---

# Option 1: Use a built-in Matplotlib style
plt.style.use('ggplot')

# Option 2: If you prefer to use seaborn styles, ensure seaborn is installed and imported
# import seaborn as sns
# sns.set_style('darkgrid')

# Set up the plotting environment
plt.rcParams.update({'font.size': 12})

# Plot each metric over time
fig, axes = plt.subplots(4, 2, figsize=(15, 20))
axes = axes.flatten()

# Metric names and corresponding data
metrics = [
    ('Collision Count', 'Collision_Count'),
    ('Flock Density', 'Flock_Density'),
    ('Grouping (Cohesion)', 'Grouping'),
    ('Straggler Count', 'Straggler_Count'),
    ('Order', 'Order'),
    ('Subgroup Count', 'Subgroup_Count'),
    ('Diffusion', 'Diffusion')
]

for ax, (title, column) in zip(axes, metrics):
    ax.plot(metrics_df['Frame'], metrics_df[column], marker='o', linestyle='-')
    ax.set_title(title)
    ax.set_xlabel('Frame')
    ax.set_ylabel(title)
    ax.grid(True)

# Hide any unused subplots
for i in range(len(metrics), len(axes)):
    fig.delaxes(axes[i])

plt.tight_layout()
plt.show()

# --- Optional: Visualize Swarm Movement at Key Time Steps ---

# Identify key frames: Start, Middle, and End
start_frame = 0
middle_frame = num_frames // 2
end_frame = num_frames - 1

key_frames = [start_frame, middle_frame, end_frame]
key_frame_titles = ['Start', 'Middle', 'End']

fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))

for ax, frame_idx, title in zip(axes2, key_frames, key_frame_titles):
    ax.set_title(f'Swarm Positions at {title} (Frame {frame_idx})')
    ax.set_xlabel('X Position (mm)')
    ax.set_ylabel('Y Position (mm)')
    ax.set_xlim(-2500, 2500)
    ax.set_ylim(-2500, 2500)
    ax.grid(True)

    current_positions = np.array([positions[robot][frame_idx] for robot in robot_names])
    valid_indices = ~np.isnan(current_positions).any(axis=1)
    valid_positions = current_positions[valid_indices]
    valid_robot_names = [robot for idx, robot in enumerate(robot_names) if valid_indices[idx]]

    # Plot positions
    for i, robot in enumerate(valid_robot_names):
        x, y = valid_positions[i]
        ax.plot(x, y, 'o', label=f'Robot {robot}')
    
    # Optionally, plot the convex hull
    if valid_positions.shape[0] >= 3:
        hull = ConvexHull(valid_positions)
        for simplex in hull.simplices:
            ax.plot(valid_positions[simplex, 0], valid_positions[simplex, 1], 'k-')

    ax.legend()

plt.tight_layout()
plt.show()
