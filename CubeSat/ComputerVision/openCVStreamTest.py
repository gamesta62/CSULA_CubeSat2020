


# Note : flip camera for Raspberry pi  

import numpy as np
import cv2
import cv2.aruco as aruco
import sys, time, math
from flask import Flask, render_template, Response
import io


#--- Define Tag
id_to_find  = 24
marker_size  = 10 #- [cm]



app = Flask(__name__)




#--- Get the camera calibration path
calib_path  = ""
camera_matrix   = np.loadtxt(calib_path+'cameraMatrix_raspi.txt', delimiter=',')
camera_distortion   = np.loadtxt(calib_path+'cameraDistortion_raspi.txt', delimiter=',')

#--- 180 deg rotation matrix around the x axis
R_flip  = np.zeros((3,3), dtype=np.float32)
R_flip[0,0] = 1.0
R_flip[1,1] =-1.0   
R_flip[2,2] =-1.0


#--- Define the aruco dictionary
aruco_dict  = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
parameters  = aruco.DetectorParameters_create()


#--- Capture the videocamera (this may also be a video or a picture)
cap = cv2.VideoCapture(0)

#-- Set the camera size as the one it was calibrated with
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#-- Font for the text in the image
font = cv2.FONT_HERSHEY_PLAIN



@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen():
    """Video streaming generator function."""
    while True:

        # read camera frame
        ret, frame = cap.read()
        
        # convert gray scale
        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #-- remember, OpenCV stores color images in Blue, Green, Red
        #-- Find all the aruco markers in the image
        corners, ids, rejected = aruco.detectMarkers(image=gray, dictionary=aruco_dict, parameters=parameters,
                              cameraMatrix=camera_matrix, distCoeff=camera_distortion)

        #-- Unpack the output, get only the first

        
        if ids is not None and ids[0] == id_to_find:

            ret1 = aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, camera_distortion)

        #-- Unpack the output, get only the first
            rvec, tvec = ret1[0][0,0,:], ret1[1][0,0,:]

        #-- Get the attitude
            aruco.drawDetectedMarkers(frame, corners)
            aruco.drawAxis(frame, camera_matrix, camera_distortion, rvec, tvec, 10)
            str_position = "MARKER Position x=%4.0f  y=%4.0f  z=%4.0f"%(tvec[0], tvec[1], tvec[2])
            cv2.putText(frame, str_position, (0, 100), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        #-- Obtain the rotation matrix tag->camera
            R_ct    = np.matrix(cv2.Rodrigues(rvec)[0])
            R_tc    = R_ct.T

            pos_camera = -R_tc*np.matrix(tvec).T

            str_position = "CAMERA Position x=%4.0f  y=%4.0f  z=%4.0f"%(pos_camera[0], pos_camera[1], pos_camera[2])
            cv2.putText(frame, str_position, (0, 200), font, 1, (0, 255, 0), 2, cv2.LINE_AA)




            cv2.putText(frame, str_position, (0, 200), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

        encode_return_code, image_buffer = cv2.imencode('.jpg', frame)
        io_buf = io.BytesIO(image_buffer)
        yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(
        gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)


      

if __name__=='_main_':
    app.run(host='0.0.0.0',debug=True,threaded=True)




























