import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import os

# Define the folder paths (replace with your actual paths)
input_folder = "Gravity"
output_folder = "Trial Plots"

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# List all CSV files in the input folder
csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

# Function to compute a simple moving average
def moving_average(data, window_size=10):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

# Function to compute the 95% confidence interval
def compute_confidence_interval(data):
    mean = np.mean(data)
    std_err = np.std(data) / np.sqrt(len(data))
    ci_range = 1.96 * std_err  # 1.96 corresponds to 95% confidence level
    return mean, ci_range

# Initialize arrays to store metrics across all runs
all_groupings = []
all_orders = []
all_subgroup_counts = []

# Create a figure with three subplots
plt.style.use('ggplot')
fig, axes = plt.subplots(3, 1, figsize=(10, 15), sharex=True)

# Loop over each CSV file and collect metrics
for file_name in csv_files:
    file_path = os.path.join(input_folder, file_name)
    
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

    # Interpolate missing values to handle NaNs
    df.interpolate(method='linear', limit_direction='both', axis=0, inplace=True)
    df.bfill(inplace=True)
    df.ffill(inplace=True)

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
    groupings = []
    orders = []
    subgroup_counts = []

    # Define parameters
    vision_range = 500  # Adjust based on your specific scenario (in mm)

    for t in range(num_frames):
        # Get positions of all robots at time t
        current_positions = np.array([positions[robot][t] for robot in robot_names])

        # --- Grouping (Cohesion) ---
        separation_distances = []
        for i in range(len(robot_names)):
            bi = current_positions[i]
            bj = np.delete(current_positions, i, axis=0)
            si = np.mean(np.linalg.norm(bi - bj, axis=1))
            separation_distances.append(si)
        grouping = np.mean(separation_distances)
        groupings.append(grouping)

        # --- Order ---
        if t < num_frames - 1:
            current_velocities = np.array([velocities[robot][t] for robot in robot_names])
            norms = np.linalg.norm(current_velocities, axis=1)
            norms[norms == 0] = 1e-6  # Prevent division by zero
            normalized_velocities = current_velocities / norms[:, np.newaxis]
            average_velocity = np.mean(normalized_velocities, axis=0)
            order = np.linalg.norm(average_velocity)
            orders.append(order)
        else:
            orders.append(orders[-1])  # Repeat last value if at the final frame

        # --- Subgroup Count (Clustering) ---
        clustering = DBSCAN(eps=vision_range, min_samples=2).fit(current_positions)
        labels = clustering.labels_
        num_subgroups = len(set(labels)) - (1 if -1 in labels else 0)  # Ignore noise points (-1)
        subgroup_counts.append(num_subgroups)

    # --- Apply Moving Average to Groupings and Orders ---
    smoothed_groupings = moving_average(groupings, window_size=100)
    smoothed_orders = moving_average(orders, window_size=100)

    # --- Find the best 3000-frame window based on smallest grouping ---
    window_size = 3000
    num_windows = len(smoothed_groupings) // window_size

    best_window_start = None
    best_avg_grouping = float('inf')  # Initialize with a high value to find the minimum
    for i in range(num_windows):
        window_start = i * window_size
        window_end = window_start + window_size

        # Calculate the average grouping for this window
        avg_grouping = np.mean(smoothed_groupings[window_start:window_end])

        if avg_grouping < best_avg_grouping:
            best_avg_grouping = avg_grouping
            best_window_start = window_start

    best_window_end = best_window_start + window_size

    # Extract the best window of metrics
    best_smoothed_groupings = smoothed_groupings[best_window_start:best_window_end]
    best_smoothed_orders = smoothed_orders[best_window_start:best_window_end]
    best_subgroup_counts = subgroup_counts[best_window_start:best_window_end]

    # Normalize the x-axis to ensure the plots overlap
    x_axis_normalized = range(3000)  # All runs will now have the same x-axis (0 to 3000)

    # Collect the data for averaging and CI calculation later
    all_groupings.append(np.mean(best_smoothed_groupings))
    all_orders.append(np.mean(best_smoothed_orders))
    all_subgroup_counts.append(np.mean(best_subgroup_counts))

    # Plot the actual traces for each run
    axes[0].plot(x_axis_normalized, best_smoothed_groupings, alpha=0.5, label=f'{file_name} Grouping')
    axes[1].plot(x_axis_normalized, best_smoothed_orders, alpha=0.5, label=f'{file_name} Order')
    axes[2].plot(x_axis_normalized, best_subgroup_counts, alpha=0.5, label=f'{file_name} Subgroup Count')

# Convert lists to numpy arrays for easier calculations
all_groupings = np.array(all_groupings)
all_orders = np.array(all_orders)
all_subgroup_counts = np.array(all_subgroup_counts)

# Compute the total average and 95% confidence intervals
mean_groupings, ci_groupings = compute_confidence_interval(all_groupings)
mean_orders, ci_orders = compute_confidence_interval(all_orders)
mean_subgroup_counts, ci_subgroup_counts = compute_confidence_interval(all_subgroup_counts)

# Plot horizontal lines for the total average and confidence intervals
x_axis_span = range(3000)  # This is used to plot the confidence interval lines across the x-axis

# Plot Grouping (Cohesion) with CI as straight lines
axes[0].axhline(mean_groupings, color='blue', label='Mean Grouping')
axes[0].axhline(mean_groupings - ci_groupings, color='blue', linestyle='--', label='95% CI Lower')
axes[0].axhline(mean_groupings + ci_groupings, color='blue', linestyle='--', label='95% CI Upper')

# Plot Order with CI as straight lines
axes[1].axhline(mean_orders, color='green', label='Mean Order')
axes[1].axhline(mean_orders - ci_orders, color='green', linestyle='--', label='95% CI Lower')
axes[1].axhline(mean_orders + ci_orders, color='green', linestyle='--', label='95% CI Upper')

# Plot Subgroup Count with CI as straight lines
axes[2].axhline(mean_subgroup_counts, color='red', label='Mean Subgroup Count')
axes[2].axhline(mean_subgroup_counts - ci_subgroup_counts, color='red', linestyle='--', label='95% CI Lower')
axes[2].axhline(mean_subgroup_counts + ci_subgroup_counts, color='red', linestyle='--', label='95% CI Upper')

# Configure the subplots with fixed y-limits
axes[0].set_ylim(0, 3500)
axes[0].set_ylabel('Average Separation of Agents (mm)')
axes[0].set_title('Grouping (Cohesion)')
axes[0].legend(loc='upper right')
axes[0].grid(True)

axes[1].set_ylim(0, 1.0)
axes[1].set_ylabel('Deviation in Alignment of Agents')
axes[1].set_title('Order (Alignment)')
axes[1].legend(loc='upper right')
axes[1].grid(True)

axes[2].set_ylim(0, 4)
axes[2].set_ylabel('Subgroup Count')
axes[2].set_xlabel('Frame (shifted to start from 0)')
axes[2].set_title('Subgroup Count with DBSCAN Clustering')
axes[2].legend(loc='upper right')
axes[2].grid(True)

# Adjust layout to avoid overlap
plt.tight_layout()

# Save the combined figure
output_file_path = os.path.join(output_folder, f'{input_folder} CI Comparison.png')
plt.savefig(output_file_path)
plt.close()

print(f"Saved combined plot with actual traces and 95% CI as horizontal lines to {output_file_path}")
