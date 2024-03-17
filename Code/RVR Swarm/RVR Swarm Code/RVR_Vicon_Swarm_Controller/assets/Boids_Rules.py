"""
Behavior Functions

These functions are essential components of the swarm simulation, implementing key behaviors that drive the 
movement of individual agents (boids) within the swarm. The functions follow the rules of alignment, cohesion, 
separation, and wall avoidance to determine the agents' velocities and positions in the swarm.

@ author    Reda Ghanem
@ version   1.0
"""

# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #

# Constants must be first import
from assets import Constants as Cons              # for Constants and Global variables
from Helper_Functions import *

# ⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️⤵️ #

# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #
# ┃----------------------- # behaviours Functions # ---------------------------┃ #
# ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┃ #

# alignment rule: boids attempt to match the velocities of their neighbors
def alignment_rule(self, neighbors_positions, neighbors_velocities):

    alignment_vector = [0, 0]
    neighbor_alig_count = 0

    # calculate the sum of all neighbors velocities
    for neighbor_pos, neighbor_vel in zip(neighbors_positions, neighbors_velocities):  # Use zip() to iterate over lists
        distance = calculate_distance(self.position, neighbor_pos)
        if distance < Cons.ALIGNMENT_RANGE:
            alignment_vector[0] += neighbor_vel[0]
            alignment_vector[1] += neighbor_vel[1]
            neighbor_alig_count += 1

    if neighbor_alig_count > 0:
        # calculate the average of previous sum
        alignment_vector[0] /= neighbor_alig_count
        alignment_vector[1] /= neighbor_alig_count

        # steering match velocity
        alignment_vector = [alignment_vector[0] - self.delta_x, alignment_vector[1] - self.delta_y]
        alignment_vector = normalize_speed_limit(alignment_vector, Cons.MIN_LINEAR_SPEED, Cons.MAX_LINEAR_SPEED)

    return alignment_vector
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# cohesion rule: boids move toward the center of mass of their neighbors
def cohesion_rule(self, neighbors_positions):
    cohesion_vector = [0, 0]
    neighbor_coh_count = 0

    # calculate the sum of all neighbors positions
    for neighbor_pos in neighbors_positions:
        distance = calculate_distance(self.position, neighbor_pos)
        if distance < Cons.COHESION_RANGE:
            cohesion_vector[0] += neighbor_pos[0]
            cohesion_vector[1] += neighbor_pos[1]
            neighbor_coh_count += 1

    if neighbor_coh_count > 0:
        # calculate the average of previous sum
        cohesion_vector[0] /= neighbor_coh_count
        cohesion_vector[1] /= neighbor_coh_count

        # steering toward position
        cohesion_vector = [cohesion_vector[0] - self.x, cohesion_vector[1] - self.y]
        cohesion_vector = normalize_speed_limit(cohesion_vector, Cons.MIN_LINEAR_SPEED, Cons.MAX_LINEAR_SPEED)

    return cohesion_vector

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# separation rule: boids move away from other boids that are too close
def separation_rule(self, neighbors_positions):
    separation_vector = [0, 0]
    neighbor_sep_count = 0

    # calculate the sum of all neighbors positions
    for neighbor_pos in neighbors_positions:
        distance = calculate_distance(self.position, neighbor_pos)
        if distance < Cons.SEPARATION_RANGE:
            separation_vector[0] += neighbor_pos[0]
            separation_vector[1] += neighbor_pos[1]
            neighbor_sep_count += 1

    if neighbor_sep_count > 0:
        # calculate the average of previous sum
        separation_vector[0] /= neighbor_sep_count
        separation_vector[1] /= neighbor_sep_count

        # steering away
        separation_vector = [self.x - separation_vector[0], self.y - separation_vector[1]]
        separation_vector = normalize_speed_limit(separation_vector, Cons.MIN_LINEAR_SPEED, Cons.MAX_LINEAR_SPEED)

    return separation_vector

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
# wall avoidance rule: prevent boids from get out of work space
def wall_avoidance_rule(self):
    wall_avoidance_vector = [0, 0]

    TURN_FACTOR = 1.5 * Cons.WALL_AVOIDANCE_WEIGHT  # We want our boid to turn-around at an organic-looking turn radius

    if self.x < 0 + Cons.WALL_AVOIDANCE_RANGE:         
        wall_avoidance_vector[0] += TURN_FACTOR             

    elif self.x > Cons.ARENA_WIDTH - Cons.WALL_AVOIDANCE_RANGE:      
        wall_avoidance_vector[0] -= TURN_FACTOR             

    if self.y > Cons.ARENA_LENGTH - Cons.WALL_AVOIDANCE_RANGE:     
        wall_avoidance_vector[1] -= TURN_FACTOR             

    elif self.y < 0 + Cons.WALL_AVOIDANCE_RANGE:        
        wall_avoidance_vector[1] += TURN_FACTOR             

    if wall_avoidance_vector != [0,0]:
        wall_avoidance_vector = normalize_speed_limit(wall_avoidance_vector, Cons.MIN_LINEAR_SPEED, Cons.MAX_LINEAR_SPEED)

    return wall_avoidance_vector