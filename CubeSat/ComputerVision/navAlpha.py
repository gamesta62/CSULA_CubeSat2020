
from os import sys, path
import time
import math
import argparse

# Adding socket stuff---------------------

import socket
sock = socket.socket()
ip = '127.0.0.1'
port = 12345
#sock.connect((ip, port))

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# from opencv.lib_aruco_pose import *
from arucotracklib import *

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

thrustDic = {'Stop': '00000000',
             'Left': '01100000',
             'Right': '00000110',
             'Forward': '00011000',
             'Backward': '10000001',
             'UpperRightDiagonal': '00011110',
             'UpperLeftDiagonal' : '01111000',
             'BottomRightDiagonal' : '10000111',
             'CounterClockWise' : '01010101',
             'ClockWise' : '10101010'}

# Testing only 
full360inSeconds = 4.0
# dist_in_seconds = 3.0 # Travel 10 cms in 3 seconds
rate = 10/3.0
distanceGoal    = 20.0

def marker_position_to_angle(x, y, z):
    
    angle_x = math.degrees(math.atan2(x,z))
    angle_y = math.degrees(math.atan2(y,z))
    
    return (angle_x, angle_y)


def calcDegreeRate(degree, full360inSeconds):
    # if we know rate it takes for SimPlat to complete a complete 360 degree rotation,
    # we can calcute what  rate it takes to complete a desired angle
    # example here is if SimPlat were to take 4 seconds to rotate a complete 360
    seconds = full360inSeconds / 360
    secondsToRotateAngle = seconds * degree
    # print("it will take ", secondsToRotateAngle, " seconds to rotate ", degree, " degrees")
    return secondsToRotateAngle


def checkCenterTreshhold(currentX):
    # function takes in the current x value from the camera and checks to see if the target is near the the center threshhold of the camera
    # if the target is outside the thresh hold, return false. if the target is within center thresh hold, return true
    #change min and max value as neccessary to change threshold
    minX = -5
    maxX = 5
    if currentX < minX or currentX > maxX:
        return False
    return True


def checkDistanceThreshhold(currentZ):
    # function takes in current z value from camera and checks to see if the distance between cubesat and the target is within the goal
    # if the distance is too great, return false. if the distance is within the goal, return true
    if currentZ > distanceGoal:
        return False
    return True


def headerControl(degree):
    # if the degree is negative, that means the target is to the left of CubeSat so a clockwise rotation is neccessary,
    # else if the degree is positive, the target is to the right of CubeSat so a counter-clockwise rotation is needed
    if degree > 0:
        thrustCommand = 'ClockWise'
    elif degree < 0:
        thrustCommand = 'CounterClockWise'
    else:
        # print("Stop")'
        thrustCommand = 'Stop'
    # print(thrustCommand)
    seconds = calcDegreeRate(degree, full360inSeconds)
    print(f'Rotation: {thrustCommand}')
    print(f'seconds: {seconds}')
    return thrustCommand, abs(seconds)

def calcDistTime(currentZ):
    z_difference = currentZ - distanceGoal
    return z_difference/rate

def velocityControl(dist):
    if dist > distanceGoal:
        delayCommand = 'Forward'
    if dist <= distanceGoal:
        delayCommand = 'Stop'

    return delayCommand, calcDistTime(dist)

def sendCommand(command):
    # Socket not set up, but this is the command to send 
    # sock.send(ThrustDic[command].encode())
    
    print(f'Command: {command}')
    return thrustDic[command]


def sendDelayedCommand(command, timer=0):    # Sends command, waits, sends reverse command
    com = sendCommand(command)
    #sock.send(com.encode())
    start = time.time()
    while True:
        if time.time() - start < timer:
            break
        elif timer == 0:
            break
    com = sendCommand(reverseCommand(command))
    #sock.send(com.encode())

def reverseCommand(command):
    reverse = ''
    
    if command == 'Left':
        reverse = 'Right'
    elif command == 'Right':
        reverse = 'Left'
    elif command == 'Forward':
        reverse = 'Backward'
    elif command == 'Backward':
        reverse = 'Forward'
    elif command == 'CounterClockWise':
        reverse = 'ClockWise'
    elif command == 'ClockWise':
        reverse = 'CounterClockWise'
    elif command == 'Stop':
        reverse = 'Stop'
    return reverse
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
        angle_x, angle_y    = marker_position_to_angle(x, y, z)

        # print(f'X:{x} Y:{y}, Z:{z}, angleX:{angle_x}')
        angle_x, angle_y    = marker_position_to_angle(x, y, z)
        secondsToRotate = calcDegreeRate(angle_x, full360inSeconds)
        withinCenter = checkCenterTreshhold(x)
        withinDistance = checkDistanceThreshhold(z)

        if withinCenter is False and withinDistance is False:
            # if both checks fail meaning the distance is larger than the goal and the target is not within center threshold
            print('outside of center threshold and distance threshold')
            delayed, seconds = headerControl(angle_x)
        elif withinCenter is True and withinDistance is False:
            # the target is within center threshold but is outside distance goal
            print('target within center threshold but outside distance goal')
            delayed, seconds = velocityControl(z)
        elif withinCenter is False and withinDistance is True:
            # target is within distance goal but not within center threshold
            print('target within distance goal but outside center threshold')
            delayed, seconds = headerControl(angle_x)
        elif withinDistance is True and withinCenter is True:
            # do nothing
            print('do nothing')
            delayed = 'Stop'
            seconds = 0

        command = sendDelayedCommand(delayed, seconds)
        print(f'command: {command}')
        #time.sleep(1)

        #--- COmmand to land
        if z <= distanceGoal:
             print (" -->>Target Distination Reached <<")

    if marker_found is False:
        # rotateCW()
        print("X: 0")
        print("Y: 0")
        print("Z: 0")
        print("rotate until find !")
        #time.sleep(1)
            
