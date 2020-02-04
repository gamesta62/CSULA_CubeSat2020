
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



def marker_position_to_angle(x, y, z):
    
    angle_x = math.atan2(x,z)
    angle_y = math.atan2(y,z)
    
    return (angle_x, angle_y)
    
def camera_to_uav(x_cam, y_cam):
    x_uav =-y_cam
    y_uav = x_cam
    return(x_uav, y_uav)
    
def uav_to_ne(x_uav, y_uav, yaw_rad):
    c       = math.cos(yaw_rad)
    s       = math.sin(yaw_rad)
    
    north   = x_uav*c - y_uav*s
    east    = x_uav*s + y_uav*c 
    return(north, east)
    
def check_angle_descend(angle_x, angle_y, angle_desc):
    return(math.sqrt(angle_x**2 + angle_y**2) <= angle_desc)
        
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
freq_send       = 1 #- Hz

land_alt_cm         = 50.0
land_speed_cms      = 30.0



#--- Get the camera calibration path
# Find full directory path of this script, used for loading config and other files
cwd                 = path.dirname(path.abspath(__file__))
calib_path          = cwd+"/../opencv/"
camera_matrix       = np.loadtxt(calib_path+'cameraMatrix_raspi.txt', delimiter=',')
camera_distortion   = np.loadtxt(calib_path+'cameraDistortion_raspi.txt', delimiter=',')                                      
aruco_tracker       = ArucoSingleTracker(id_to_find=id_to_find, marker_size=marker_size, show_video=False, 
                camera_matrix=camera_matrix, camera_distortion=camera_distortion)
                
                
time_0 = time.time()

while True:                

    marker_found, x_cm, y_cm, z_cm = aruco_tracker.track(loop=False)
    if marker_found:
        x_cm, y_cm          = camera_to_uav(x_cm, y_cm)
        
        angle_x, angle_y    = marker_position_to_angle(x_cm, y_cm, z_cm)

        print("X ; ",x_cm)
        print("Y ; ",y_cm)
        print("Z ; ",z_cm)
        print("angleX : ",angle_x)
        print("angleY : ",angle_y)


        #--- COmmand to land
        if z_cm <= land_alt_cm:
             print (" -->>COMMANDING TO LAND<<")
            
