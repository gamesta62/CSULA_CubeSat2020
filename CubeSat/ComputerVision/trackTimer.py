
from os import sys, path

import numpy as np
import cv2
import cv2.aruco as aruco
import sys, time, math

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from arucotrack import *


freq_send = 1.0



#--------------------------------------------------
#-------------- LANDING MARKER  
#--------------------------------------------------    
#--- Define Tag
id_to_find      = 24
marker_size     = 10 #- [cm]

#--- Get the camera calibration path
# Find full directory path of this script, used for loading config and other files
cwd                 = path.dirname(path.abspath(__file__))
calib_path          = cwd+"/../opencv/"
camera_matrix       = np.loadtxt('cameraMatrix_raspi.txt', delimiter=',')
camera_distortion   = np.loadtxt('cameraDistortion_raspi.txt', delimiter=',')                                      
aruco_tracker       = ArucoTracker(id_to_find=id_to_find, marker_size=marker_size, show_video=False, 
                camera_matrix=camera_matrix, camera_distortion=camera_distortion)
                
time_0 = time.time()

if __name__ == "__main__":

    while True:                
        # marker_found, x, y, z = aruco_tracker.track(loop=False) # Note : XYZ  are all in cm
        marker_found, x, y, z = True,0,0,20# Note : XYZ  are all in cm

        if marker_found:
            if time.time() >= time_0 + 1.0/freq_send:
                time_0 = time.time()
                print("here time ",time_0)
                print("x , y , z ",x,y,z)
                

            if z <= 10.0:
                print (" -->>COMMANDING TO LAND<<")

        else :
           if time.time() >= time_0 + 1.0/freq_send:
                time_0 = time.time()
                print("x = 0, y =0, z = 0")


