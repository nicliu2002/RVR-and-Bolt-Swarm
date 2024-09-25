import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

# Function to load data from a txt file
def load_data(file_path):
    # Using on_bad_lines='skip' to skip problematic lines with incorrect column counts
    df = pd.read_csv(file_path, header=None, names=['time', 'object', 'x', 'y', 'velocity', 'theta'], 
                     on_bad_lines='skip')  # Skip lines with too many or too few columns
    return df

# Load data from the txt file (replace 'all BOLT test.txt' with your actual file path)
df = load_data('all BOLT test.txt')

# Strip leading/trailing spaces and convert object names to uppercase
df['object'] = df['object'].str.strip().str.upper()

# Print the unique object names
unique_objects = df['object'].unique()
print("Unique object names:", unique_objects)

# Dynamically create DataFrames for each unique object
object_dfs = {obj: df[df['object'] == obj] for obj in unique_objects}

# Ensure there is data to plot
if all(df.empty for df in object_dfs.values()):
    print("No data available for any objects.")
else:
    # Dynamically set axis limits based on data
    x_min = min(df['x'].min(), df['y'].min()) - 10
    x_max = max(df['x'].max(), df['y'].max()) + 10

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(x_min, x_max)

    # Create dictionaries to store plots for each object
    points = {}
    vectors = {}

    # Initialize plots for each object
    colors = ['blue', 'red', 'green', 'orange']  # Add more colors if needed
    for i, (obj, obj_df) in enumerate(object_dfs.items()):
        color = colors[i % len(colors)]
        points[obj], = ax.plot([], [], 'o', label=obj, color=color)
        vectors[obj] = ax.quiver([], [], [], [], color=color, scale=50)

    # Function to initialize the plot
    def init():
        # Return a flattened list of all point and vector elements for blitting
        elements = []
        for obj in unique_objects:
            points[obj].set_data([], [])
            vectors[obj].set_UVC([], [])
            elements.append(points[obj])
            elements.append(vectors[obj])
        return elements

    # Function to update the plot for each frame
    def update(frame):
        elements = []
        for obj in unique_objects:
            obj_df = object_dfs[obj]
            points[obj].set_data(obj_df['x'].iloc[frame], obj_df['y'].iloc[frame])

            # Update velocity vectors
            vectors[obj].set_offsets([obj_df['x'].iloc[frame], obj_df['y'].iloc[frame]])
            vectors[obj].set_UVC(obj_df['velocity'].iloc[frame] * np.sin(np.radians(obj_df['theta'].iloc[frame])),
                                 obj_df['velocity'].iloc[frame] * np.cos(np.radians(obj_df['theta'].iloc[frame])))
            
            elements.append(points[obj])
            elements.append(vectors[obj])

        return elements

    # Create the animation
    ani = FuncAnimation(fig, update, frames=min(len(df) for df in object_dfs.values()), init_func=init, blit=True, repeat=False)

    # Display the animation
    plt.legend()
    plt.show()
