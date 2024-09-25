import pandas as pd
import matplotlib.pyplot as plt

# Load the cleaned CSV data
df = pd.read_csv('3 bolt test.csv', skiprows=4)
df.columns = ['Frame', 'Sub Frame', 'RX_SB_5938', 'RY_SB_5938', 'RZ_SB_5938', 'TX_SB_5938', 'TY_SB_5938', 'TZ_SB_5938',
              'RX_SB_8427', 'RY_SB_8427', 'RZ_SB_8427', 'TX_SB_8427', 'TY_SB_8427', 'TZ_SB_8427',
              'RX_SB_CE32', 'RY_SB_CE32', 'RZ_SB_CE32', 'TX_SB_CE32', 'TY_SB_CE32', 'TZ_SB_CE32']

# Extract X and Y coordinates for each robot
x_coords_sb_5938 = df['TX_SB_5938']
y_coords_sb_5938 = df['TY_SB_5938']

x_coords_sb_8427 = df['TX_SB_8427']
y_coords_sb_8427 = df['TY_SB_8427']

x_coords_sb_ce32 = df['TX_SB_CE32']
y_coords_sb_ce32 = df['TY_SB_CE32']

# Create the plot
plt.figure(figsize=(10, 6))

# Plot the paths of each robot
plt.plot(x_coords_sb_5938, y_coords_sb_5938, label='SB-5938 Path', marker='o', linestyle='-')
plt.plot(x_coords_sb_8427, y_coords_sb_8427, label='SB-8427 Path', marker='x', linestyle='--')
plt.plot(x_coords_sb_ce32, y_coords_sb_ce32, label='SB-CE32 Path', marker='s', linestyle='-.')

# Add titles and labels
plt.title('Paths of SB-5938, SB-8427, and SB-CE32')
plt.xlabel('X Coordinate (mm)')
plt.ylabel('Y Coordinate (mm)')

# Add a legend to identify each robot
plt.legend()

# Display the plot
plt.grid(True)
plt.show()
