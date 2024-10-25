import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import os

# Define the folder paths (replace with your actual paths)
input_folder = "./"
output_folder = "appendix"

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# List all CSV files in the input folder
csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

# Function to compute a simple moving average
def moving_average(data, window_size=10):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

# Check if there is at least one CSV file
if len(csv_files) > 0:
    # Choose the first CSV file for plotting
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
            from sklearn.cluster import DBSCAN
            clustering = DBSCAN(eps=vision_range, min_samples=2).fit(current_positions)
            labels = clustering.labels_
            num_subgroups = len(set(labels)) - (1 if -1 in labels else 0)  # Ignore noise points (-1)
            subgroup_counts.append(num_subgroups)

        # --- Apply Moving Average to Groupings, Orders, and Subgroup Counts ---
        smoothed_groupings = moving_average(groupings, window_size=100)
        smoothed_orders = moving_average(orders, window_size=100)
        smoothed_subgroup_counts = moving_average(subgroup_counts, window_size=100)

        # Calculate averages
        avg_grouping = np.mean(smoothed_groupings)
        avg_order = np.mean(smoothed_orders)
        avg_subgroup_count = np.mean(smoothed_subgroup_counts)

        # Plot the metrics
        plt.style.use('ggplot')
        fig, axes = plt.subplots(3, 1, figsize=(10, 15), sharex=True)
        
        fig.suptitle(file_name,fontsize=16)

        # Normalize the x-axis to ensure the plots overlap
        x_axis_normalized = range(len(smoothed_groupings))  # Adjusted for one data log

        # Plot the smoothed metrics
        axes[0].plot(x_axis_normalized, smoothed_groupings, label=f'{file_name} - Grouping',color = 'b')
        axes[1].plot(x_axis_normalized, smoothed_orders, label=f'{file_name} - Order', color='g')
        axes[2].plot(x_axis_normalized, smoothed_subgroup_counts, label=f'{file_name} - Subgroup Count',color='r')

        # Add horizontal lines for averages
        axes[0].axhline(avg_grouping, color='b', linestyle='--', label=f'Avg Grouping = {avg_grouping:.2f}')
        axes[1].axhline(avg_order, color='g', linestyle='--', label=f'Avg Order = {avg_order:.2f}')
        axes[2].axhline(avg_subgroup_count, color='r', linestyle='--', label=f'Avg Subgroup Count = {avg_subgroup_count:.2f}')

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
        axes[2].set_title('Subgroup Count with DBSCAN Clustering')
        axes[2].legend(loc='upper right')
        axes[2].grid(True)

        # Adjust layout to avoid overlap
        plt.tight_layout()

        # Save the combined figure
        output_file_path = os.path.join(output_folder, f'{file_name} metric plot.png')
        plt.savefig(output_file_path)
        plt.close()

        print(f"Saved plot for {file_name} with averages to {output_file_path}")
else:
    print("No CSV files found in the input folder.")