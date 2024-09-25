import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Function to process each CSV file
def process_csv(csv_path):
    print(f'Processing file: {csv_path}')
    
    # Read the data file
    try:
        # Attempt to read the data, skipping the first line (metadata)
        df = pd.read_csv(csv_path, sep='\s+', skiprows=1)
        
        # If the second line contains units, skip it
        if 'rad' in df.columns.tolist() or 'mm' in df.columns.tolist():
            df = pd.read_csv(csv_path, sep='\s+', skiprows=2)
            header_line = 2
        else:
            header_line = 1
        
        # Assign column names
        column_names = ['Frame', 'Sub_Frame',
                        'RX1', 'RY1', 'RZ1', 'TX1', 'TY1', 'TZ1',
                        'RX2', 'RY2', 'RZ2', 'TX2', 'TY2', 'TZ2',
                        'RX3', 'RY3', 'RZ3', 'TX3', 'TY3', 'TZ3']
        
        # Check if the number of columns matches
        if len(df.columns) != len(column_names):
            print(f"Error: Expected {len(column_names)} columns, but found {len(df.columns)}.")
            print("Please check the data format.")
            return
        
        df.columns = column_names
        
        # Convert all data to numeric, coerce errors to NaN
        df = df.apply(pd.to_numeric, errors='coerce')
        
    except Exception as e:
        print(f"Failed to read the data file: {e}")
        return
    
    # Check for NaN values in 'Frame' column
    if df['Frame'].isnull().any():
        print("Warning: 'Frame' column contains NaN values.")
        print(df['Frame'])
        return
    
    # Extract data
    frames = df['Frame']
    TX1 = df['TX1']
    TX2 = df['TX2']
    TX3 = df['TX3']
    
    # Check for NaN in TX columns
    if TX1.isnull().all() and TX2.isnull().all() and TX3.isnull().all():
        print("Error: All TX columns contain NaN values.")
        return
    
    # Plot TX vs Frame for each robot
    plt.figure(figsize=(10, 6))
    plt.plot(frames, TX1, 'b-', label='Robot 1 TX')
    plt.plot(frames, TX2, 'r-', label='Robot 2 TX')
    plt.plot(frames, TX3, 'g-', label='Robot 3 TX')
    plt.xlabel('Frame')
    plt.ylabel('TX (mm)')
    plt.title('TX over Frames')
    plt.legend()
    plt.grid(True)
    # Save the static plot
    plot_path = os.path.join(os.path.dirname(csv_path), 'TX_plot.png')
    plt.savefig(plot_path)
    plt.close()
    
    # Create an animation for TX over frames
    fig, ax = plt.subplots()
    ax.set_xlim(frames.min(), frames.max())
    min_tx = min(TX1.min(), TX2.min(), TX3.min())
    max_tx = max(TX1.max(), TX2.max(), TX3.max())
    ax.set_ylim(min_tx - 10, max_tx + 10)
    ax.set_xlabel('Frame')
    ax.set_ylabel('TX (mm)')
    ax.set_title('TX Animation')
    line1, = ax.plot([], [], 'b-', label='Robot 1 TX')
    line2, = ax.plot([], [], 'r-', label='Robot 2 TX')
    line3, = ax.plot([], [], 'g-', label='Robot 3 TX')
    ax.legend()
    
    # Initialization function
    def init():
        line1.set_data([], [])
        line2.set_data([], [])
        line3.set_data([], [])
        return line1, line2, line3
    
    # Animation function
    def animate(i):
        x = frames.iloc[:i+1]
        y1 = TX1.iloc[:i+1]
        y2 = TX2.iloc[:i+1]
        y3 = TX3.iloc[:i+1]
        line1.set_data(x, y1)
        line2.set_data(x, y2)
        line3.set_data(x, y3)
        return line1, line2, line3
    
    # Create animation
    ani = animation.FuncAnimation(fig, animate, frames=len(frames),
                                  init_func=init, interval=200, blit=True)
    
    # Save the animation
    anim_path = os.path.join(os.path.dirname(csv_path), 'TX_animation.mp4')
    ani.save(anim_path, writer='ffmpeg')
    plt.close()
    print(f"Processing of {csv_path} completed successfully.")

# Main function to process all CSV files in subfolders
def main():
    root_dir = '.'  # Set the root directory
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.csv') or file.endswith('.txt'):
                csv_path = os.path.join(subdir, file)
                process_csv(csv_path)
    print('Processing complete.')

if __name__ == '__main__':
    main()
