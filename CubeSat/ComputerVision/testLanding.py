
from os import sys, path

import time
import math
import argparse
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


# from opencv.lib_aruco_pose import *
from opencv.arucotracklib import *



#--------------------------------------------------
#-------------- FUNCTIONS  
#--------------------------------------------------    


#Goal of this navigation is to have CubeSat Rotate a degree/ angle; with the goal of 
# having the target aligned in its center before thrusting toward target.

# ---HEADING CONTROLS
# By knowing how long SimPlat takes to rotate a full 360 we can computer the amount of
# time it takes to move N degrees. 
# Now that we have time it takes to rotate a certain degree/angle, we can use this to send a 
# rotate command for X amount of seconds before sending counter thrusting to stop rotation .
# This will line us up with the target in the center of our screen. 

# XYZ -> Angle-> Rotate(angle) ->computeRotateTime(angel) ->startRotate(seconds )


def marker_position_to_angle(x, y, z):
    
    angle_x = math.atan2(x,z)
    angle_y = math.atan2(y,z)
    
    return (angle_x, angle_y)
    

   
       
#--------------------------------------------------
#-------------- CONNECTION  
#--------------------------------------------------    
#-- Connect to the vehicle
print('Connecting...')



#--------------------------------------------------
#-------------- LANDING MARKER  
#--------------------------------------------------    
#--- Define Tag
id_to_find      = 24
marker_size     = 10 #- [cm]

distanceGoal        = 50.0



#--- Get the camera calibration path
# Find full directory path of this script, used for loading config and other files
cwd                 = path.dirname(path.abspath(__file__))
calib_path          = cwd+"/../opencv/"
camera_matrix       = np.loadtxt('cameraMatrix_raspi.txt', delimiter=',')
camera_distortion   = np.loadtxt('cameraDistortion_raspi.txt', delimiter=',')                                      
aruco_tracker       = ArucoSingleTracker(id_to_find=id_to_find, marker_size=marker_size, show_video=False, 
                camera_matrix=camera_matrix, camera_distortion=camera_distortion)
                
                
time_0 = time.time()

while True:                



    # (x,y, z) add test values
    marker_found, x, y, z = aruco_tracker.track(loop=False) # Note : XYZ  are all in cm

    if marker_found:
        #rotateCCW()
        #degree = marker_position_to_angle(x,y,z)
        #rate = headerControl(degree)
        #delay_command = rotate_thruster(rate))
        #sendDelayedCommand(rate)    # inner loop that takes delay(sends 2 commands, 1 before delay and 1 after)
        # = ^loop delay()
        #   ^if checkthreshold(x,y,z) == false
        #       ^sendStop()
        #=  ^else continue
        # = send last command
        

        angle_x, angle_y    = marker_position_to_angle(x, y, z)

        print("X ; ",x)
        print("Y ; ",y)
        print("Z ; ",z)
        print("angleX : ",angle_x)
        print("angleY : ",angle_y)


        #--- COmmand to land
        if z <= distanceGoal:
             print (" -->>Target Distination Reached <<")
    if marker_found is False:
        # rotateCW()
        print("X: 0")
        print("Y: 0")
        print("Z: 0")
        print("rotate until find !")
            
