from flask import Response
from flask import Flask
from flask import render_template
import threading
import socket
from os import sys, path

# Adding socket stuff---------------------

#Change ip to server host ip
sock = socket.socket()
ip = '127.0.0.1' #connects to self
#ip = '192.168.43.209'  # SimPlat ip
port = 12345
sock.connect((ip, port))

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# from opencv.lib_aruco_pose import *
from opencv.arucotracklib import *

# --------------------------------------------------
# -------------- FUNCTIONS
# --------------------------------------------------

# Goal of this navigation is to have CubeSat Rotate a degree/ angle; with the goal of
# having the target aligned in its center before thrusting toward target.

#dictionary to convert commands to the appropriate thruster commands that simplat will receive from CubeSat
thrustDic = {'Stop': '00000000',
             'Left': '01100000',
             'Right': '00000110',
             'Forward': '00011000',
             'Backward': '10000001',
             'UpperRightDiagonal': '00011110',
             'UpperLeftDiagonal': '01111000',
             'BottomRightDiagonal': '10000111',
             'CounterClockWise': '01010101',
             'ClockWise': '10101010'}

#dictionary of the appropriate counter thrust commands for each thrust
reverseDic = {'Stop': 'Stop',
              'Left': 'Right',
              'Right': 'Left',
              'Forward': 'Backward',
              'Backward': 'Forward',
              'CounterClockWise': 'ClockWise',
              'ClockWise': 'CounterClockWise'}

#This is the distance CubeSat will maintain between itself and the target. Measured in cm
distanceGoal = 30.0

#Function used to return the x and y angle the target is relative in the camera frame
def marker_position_to_angle(x, y, z):
    angle_x = math.degrees(math.atan2(x, z))
    angle_y = math.degrees(math.atan2(y, z))

    return (angle_x, angle_y)


def initialSearch():
    #loops until target is found for first time, then sends counterthrust to simplat and ends the loop, returning back to nav()
    while True:
        marker_found, x, y, z = aruco_tracker.track(loop=False)
        if marker_found is True:
            sock.send(sendCommand('CounterClockWise').encode())
            break
    return


def checkCenterTreshhold(currentX):
    # function takes in the current x value from the camera and checks to see if the target is near the the center threshhold of the camera
    # if the target is outside the thresh hold, return false. if the target is within center thresh hold, return true
    # change min and max value as neccessary to change threshold
    minX = -20.0
    maxX = 20.0
    return False if currentX < minX or currentX > maxX else True


def checkDistanceThreshhold(currentZ):
    # function takes in current z value from camera and checks to see if the distance between cubesat and the target is within the goal
    # if the distance is too great or they are too close, return false. if the distance is within the goal, return true
    return False if currentZ > distanceGoal or currentZ < distanceGoal - 5 else True

def headerControl(degree):
    # if the degree is negative, that means the target is to the left of CubeSat so a clockwise rotation is neccessary,
    # else if the degree is positive, the target is to the right of CubeSat so a counter-clockwise rotation is needed
    if degree < 0:
        thrustCommand = 'ClockWise'
    elif degree > 0:
        thrustCommand = 'CounterClockWise'
    else:
        thrustCommand = 'Stop'

    # while loop to keep receiving data from OpenCV to get target location. loop ends when cubesat is within threshold
    # or it ends when the target is no longer within camera view
    marker_found, x, y, z = aruco_tracker.track(loop=False)
    while marker_found:
        marker_found, x, y, z = aruco_tracker.track(loop=False)
        checker = checkCenterTreshhold(x)
        if checker is True:
            sock.send(sendCommand(reverseCommand(thrustCommand)).encode())
            break
    return



def velocityControl(dist):
    #depending on the distance received, cubesat will issue either a forward or backward thrust
    if dist > distanceGoal:
        command = 'Forward'
    if dist <= distanceGoal - 5: #5 can be any number but the idea is that this means the distance between target and cubesat is closer than distancegoal
        command = 'Backward'

    # while loop that keeps forward command going until either target is off center or cubesat is within distance
    # loop may also end if the target is no longer within frame
    marker_found, x, y, z = aruco_tracker.track(loop=False)
    while marker_found:
        marker_found, x, y, z = aruco_tracker.track(loop=False)
        checker = checkDistanceThreshhold(z)
        if checker is True:
            sock.send(sendCommand(reverseCommand(command)).encode())
            break
    return

#simple functions to get the approrpiate thruster command from the dictionary to send to simplat
def sendCommand(command):
    return thrustDic[command]

def reverseCommand(command):
    return reverseDic[command]


# --------------------------------------------------
# -------------- CONNECTION
# --------------------------------------------------
# -- Connect to the vehicle
print('Connecting...')

# --------------------------------------------------
# -------------- LANDING MARKER
# --------------------------------------------------
# --- Define Tag
id_to_find = 24
marker_size = 10  # - [cm]

# --- Get the camera calibration path
# Find full directory path of this script, used for loading config and other files
cwd = path.dirname(path.abspath(__file__))
calib_path = cwd + "/../opencv/"
camera_matrix = np.loadtxt('cameraMatrix_raspi.txt', delimiter=',')
camera_distortion = np.loadtxt('cameraDistortion_raspi.txt', delimiter=',')
aruco_tracker = ArucoSingleTracker(id_to_find=id_to_find, marker_size=marker_size, show_video=False,
                                   camera_matrix=camera_matrix, camera_distortion=camera_distortion)

# lines 157 - 179 are lines of code to help display cubesat's camera feed to an html page using flask
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

def generate():
    while True:
        frame = aruco_tracker.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

def nav():
    #firstSearch is set to true on startup to let the software know it needs to perform the initial search
    firstSearch = True
    #prevX, prevZ, and prevAngleX are values received from OpenCV from previous iteration of the main loop
    prevX = 0
    prevZ = 0
    prevAngleX = 0

    #there are sleep commands for 0.5 secs to allow the camera to refocus if it needs to
    while True:

        # (x,y, z) add test values
        marker_found, x, y, z = aruco_tracker.track(loop=False)  # Note : XYZ  are all in cm
        x = -x

        if marker_found:
            angle_x, angle_y = marker_position_to_angle(x, y, z)

            angle_x, angle_y = marker_position_to_angle(x, y, z)
            withinCenter = checkCenterTreshhold(x)
            withinDistance = checkDistanceThreshhold(z)

            #sets the x, angle x, and z values into variables in case the target was lost
            prevX = x
            prevZ = z
            prevAngleX = angle_x

            if not withinCenter and not withinDistance:
                # if both checks fail meaning the distance is larger than the goal and the target is not within center threshold
                print('outside of center threshold and distance threshold')
                headerControl(angle_x)
                time.sleep(0.5)
            elif withinCenter and not withinDistance:
                # the target is within center threshold but is outside distance goal
                print('target within center threshold but outside distance goal')
                velocityControl(z)
                time.sleep(0.5)
            elif not withinCenter and withinDistance:
                # target is within distance goal but not within center threshold
                print('target within distance goal but outside center threshold')
                headerControl(angle_x)
                time.sleep(0.5)

            # --- COmmand to land
            if z <= distanceGoal:
                print(" -->>Target Distination Reached <<")

        #if the marker is not within the camera frame
        if marker_found is False:
            #if cubesat still needs to perform initialsearch
            if firstSearch is True:
                #CubeSat performs initial search to find the target for the first time
                sock.send(sendCommand('ClockWise').encode())
                print('Searching for target...')
                initialSearch()
                firstSearch = False
                time.sleep(0.5)
            #if Cubesat already has found the target before and needs to relocate it
            elif firstSearch is False:
                #CubeSat has to find the target again after losing it. uses previous info to figure out where target was moving
                withinCenter = checkCenterTreshhold(prevX)
                withinDistance = checkDistanceThreshhold(prevZ)
                if not withinDistance:
                    #the target wasn't within distance goal before cubesat lost it
                    if prevZ > distanceGoal:
                        #if the target was last seen moving away i.e. too far for the camera, cubesat will be at rest initially,
                        #so try doubling cubesat's normal speed by sending two forward thrust commands to keep up with target
                        sock.send(sendCommand('Forward').encode())
                        sock.send(sendCommand('Forward').encode())
                        while not marker_found:
                            # while loop to keep checking the camera frame to see if target is found again
                            marker_found, x, y, z = aruco_tracker.track(loop=False)
                            if marker_found:
                                sock.send(sendCommand('Backward').encode())
                                sock.send(sendCommand('Backward').encode())
                                break
                    elif prevZ < distanceGoal:
                        #if the target was seen getting closer to cubesat before being lost, assume that the target is too close
                        sock.send(sendCommand('Backward').encode())
                        while not marker_found:
                            # while loop to keep checking the camera frame to see if target is found again
                            marker_found, x, y, z = aruco_tracker.track(loop=False)
                            if marker_found:
                                sock.send(sendCommand('Forward').encode())
                                break
                elif not withinCenter:
                    #target wasnt near center of camera view when cubesat lost it
                    #look at previous data to see whether target was last seen on left or right side of camera view
                    #try doubling rotation speed from rest to keep up with target
                    if prevAngleX < 0:
                        command = 'ClockWise'
                    elif prevAngleX > 0:
                        command = 'CounterClockWise'
                    sock.send(sendCommand(command).encode())
                    sock.send(sendCommand(command).encode())
                    while not marker_found:
                        #while loop to keep checking the camera frame to see if target is found again
                        marker_found, x, y, z = aruco_tracker.track(loop=False)
                        if marker_found:
                            #stop the rotation with counterthrust
                            sock.send(sendCommand(reverseCommand(command)).encode())
                            sock.send(sendCommand(reverseCommand(command)).encode())
                            break


def startFlask():
    # start the flask app
    app.run(host='127.0.0.1', port='8000', debug=True,
            threaded=True, use_reloader=False)

if __name__ == '__main__':
    t = threading.Thread(name='background', target=startFlask)
    t1 = threading.Thread(name='foreground', target=nav)
    t.start()
    t1.start()