import spherov2
    


global currentPosX, currentPosY

updateCurrentPos(api) # updates global position variables

timeCount = 0 # sets the time count to 0
x = api.get_location()['x'] # gets initial robot x coordinates from local positioning system
y = api.get_location()['y'] # gets initial robot y coordinates from local positioning system
theta = api.get_heading() # gets robot initial heading

# print("current location data: X: " + str(x) + "     Y: " + str(y) + "     Theta: " + str(theta))

target_x = scaleParam*nodeX # converts x grid coordinates to local positioning system coordinates
target_y = scaleParam*nodeY # converts y grid coordinates to local positioning system coordinates

# print("target data is:      target x: " + str(target_x) + "     target y: " + str(target_y))

dist_error = get_distance(x, y, target_x, target_y) # gets initial euclidean distance to target

while dist_error >= 2:
    
    # loop continually gets distance and heading to target until robot is within 3 cm of target 
    
    timeCount += 1
    progressiveX = api.get_location()['x']
    progressiveY = api.get_location()['y']            
    dist_error = get_distance(progressiveX, progressiveY, target_x, target_y)
    theta_error = 180*math.atan2(target_x-progressiveX, target_y-progressiveY)/math.pi
    api.set_heading(int(theta_error))
    time.sleep(0.01) # small sleep prevents over correction
    api.set_speed(35) # robot moves at minimal speed to overcome carpet friction to prevent over correction
    # print("moving location data: X: " + str(progressiveX) + "     Y: " + str(progressiveY) + "   Theta: " + str(theta_error) + "    dist_error: " + str(dist_error))
    # moves until distance error is less than 5
    
    if dist_error < 3: # if statement triggers on reaching target location and returns successful "moved" string
        
        # print("New Current Positions: " + "     X: " + str(progressiveX) + "      Y: " + str(progressiveY))
        api.set_speed(0)
        updateCurrentPos(api)
        return "moved"
        
    if timeCount > 25: # if statement occurs if robot times out and is unable to reach target location, returns "blocked" string
        
        print("Could not move")
        updateCurrentPos(api)
        api.set_speed(-65) # robot uses a small "jiggle" to unstuck itself from block
        time.sleep(1.5)
        api.set_speed(0)
        return "blocked" 
    
    time.sleep(0.05)