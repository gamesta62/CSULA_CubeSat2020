from flask import Flask, render_template, request
import argparse

import socket

app = Flask(__name__)
# add socket connection to simPat

# 


# s = socket.socket()
# s.connect(('127.0.0.1',12345))
s = socket.socket()
s.connect(('127.0.0.1',12345))

@app.route("/", methods=['GET', 'POST'])


def index():
    print(request.method)
    # s = socket.socket()
    # s.connect(('127.0.0.1',12345))
    # # str = input("S: ")
    # s.send(str.encode());

  
    if request.method == 'POST':
        if request.form.get('Forward') == 'Forward':
            message = "forward "
            s.send(message.encode());

                # pass
            # add bittarray to send
            print("Forward")
        if  request.form.get('Reverse') == 'Reverse':
            # pass # do something else
            message = "reverse "
            s.send(message.encode());
            print("Reverse")
        if  request.form.get('Left') == 'Left':
            # pass # do something else
            message = "left"
            s.send(message.encode())
            print("Left")

        if  request.form.get('Right') == 'Right':
            # pass # do something else
            message = "right"
            s.send(message.encode());

            print("Right")
        if  request.form.get('Stop') == 'Stop':
            # pass # do something else
            message = 'stop'
            s.send(message.encode())

            print("Stop")
        if  request.form.get('counterclock') == 'counterclock':
            # pass # do something else
            message = 'counterclock'
            s.send(message.encode());

        if  request.form.get('ClockWise') == 'ClockWise':
            # pass # do something else
            message = 'clockwise'
            s.send(message.encode());

            print("ClockWise")
        if  request.form.get('StartDetectionTrack') == 'StartDetectionTrack':
            # pass # do something else
            message = 'startDetection'
            s.send(message.encode());

            print("StartDetectionTrack")
        else:
                # pass # unknown
                print('nothing')
            # return render_template("index.html")
    elif request.method == 'GET':
            # return render_template("index.html")
        print("No Post Back Call")
    return render_template("index.html")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")

    args = vars(ap.parse_args())

    app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)
    # s.send(str.encode());
    # str = input("S: ")