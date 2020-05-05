# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 15:58:41 2020

@author: Jimmy Lopez jlope690@calstatela.edu
"""

import os
from bitarray import bitarray
import threading
import time
import queue
import socket
#ABCDEFGH
#76543210
#Opposites

#Side 3 +0 | -3 
#Side 1 +4 | -7
#Side 0 +6 | -1
#Side 2 +2 | -5

#Example
#ABCDEFGH
#00110000
# + Side 3 + Side 2

s = socket.socket()
ipLoc = '192.168.1.12'
ipSelf = ''
port = 12345
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((ipLoc, port))
s.listen(5)
c, addr = s.accept()
print('Socket up and running with a connection from',addr)

codeThrust = {'0': bitarray('10000000'), '1': bitarray('01000000'),
        '2': bitarray('00100000'), '3': bitarray('00010000'),
        '4': bitarray('00001000'), '5': bitarray('00000100'),
        '6': bitarray('00000010'), '7': bitarray('00000001'),
        '8': bitarray('00000000'), 'w': bitarray('00011000'),
        'a': bitarray('01100000'), 'd': bitarray('00000110'), 
        's': bitarray('10000001'), 'x': bitarray('00000000')}

def thread_function(num, outQueue):
    #inp = input("Input thruster number: ")
    #outQueue.put(inp)
    rcvdData = c.recv(1024).decode()
    print(f'Command: {rcvdData}')
    sendData = rcvdData
    c.send(sendData.encode())
    outQueue.put(rcvdData)
    

class SERVO:
    def __init__(self, idNum, codeI):
        self.idNum = idNum
        self.sig = 1520
        self.step = 17
        self.codeIn = codeI
    
    def changeSigIndiv(self, signal):
        try:
            if signal.decode(self.codeIn)[0] == '8':
                self.sig = 1520
            else:
                if self.idNum == 0:
                    if (signal[6] == 1):
                        self.sig += self.step
                    if (signal[1] == 1):
                        self.sig -= self.step
                elif self.idNum == 1:
                    if (signal[4] == 1):
                        self.sig += self.step
                    if (signal[7] == 1):
                        self.sig -= self.step
                elif self.idNum == 2:
                    if (signal[2] == 1):
                        self.sig += self.step
                    if (signal[5] == 1):
                        self.sig -= self.step
                elif self.idNum == 3:
                    if (signal[0] == 1):
                        self.sig += self.step
                    if (signal[3] == 1):
                        self.sig -= self.step
        except:
            if signal.any():
                if self.idNum == 0:
                    if (signal[6] == 1):
                        self.sig += self.step
                    if (signal[1] == 1):
                        self.sig -= self.step
                elif self.idNum == 1:
                    if (signal[4] == 1):
                        self.sig += self.step
                    if (signal[7] == 1):
                        self.sig -= self.step
                elif self.idNum == 2:
                    if (signal[2] == 1):
                        self.sig += self.step
                    if (signal[5] == 1):
                        self.sig -= self.step
                elif self.idNum == 3:
                    if (signal[0] == 1):
                        self.sig += self.step
                    if (signal[3] == 1):
                        self.sig -= self.step
            else:
                self.sig = 1520
                
    def echo(self):
        if self.sig != 1520:
            os.system("echo " + str(self.idNum) + "=" + str(self.sig) + "us > /dev/servoblaster")
    
    def printSer(self):
        print(str(self.idNum) + "=" + str(self.sig) + "us > /dev/servoblaster")
                
ser0 = SERVO(0, codeThrust)
ser1 = SERVO(1, codeThrust)
ser2 = SERVO(2, codeThrust)
ser3 = SERVO(3, codeThrust)
a = bitarray()
check = False
myQueue = queue.Queue()
x = threading.Thread(target=thread_function, args=(1,myQueue))
try:    
    while 1:
        if check == False:
            x.start()
            check = True
        if x.isAlive() == False:
            value = myQueue.get()
            if value == 'exit':
                break
            if len(value) > 1:
                a.extend(value)
            else:
                a.encode(codeThrust, value)
            check = False
            x = threading.Thread(target=thread_function, args=(1,myQueue))
        if len(a) == 0:
#            ser0.printSer()
#            ser1.printSer()
#            ser2.printSer()
#            ser3.printSer()
            ser0.echo()
            ser1.echo()
            ser2.echo()
            ser3.echo()
#            time.sleep(1)
        else:
            ser0.changeSigIndiv(a)
            ser1.changeSigIndiv(a)
            ser2.changeSigIndiv(a)
            ser3.changeSigIndiv(a)
 #           ser0.printSer()
 #           ser1.printSer()
 #           ser2.printSer()
 #           ser3.printSer()
            ser0.echo()
            ser1.echo()
            ser2.echo()
            ser3.echo()
            a = bitarray()    
except KeyboardInterrupt:
    s.close()
    pass

s.close()
