#!/usr/bin/python3
from enum import Enum
import threading
import zmq
import time
from queue import Queue, LifoQueue


context = zmq.Context()
req_sock = context.socket(zmq.REQ)
sub_sock = context.socket(zmq.SUB)
sub_sock.connect('tcp://127.0.0.1:2271')
req_sock.connect("tcp://127.0.0.1:2272")
sub_sock.setsockopt_string(zmq.SUBSCRIBE, 'distance is')

sensorQueue = LifoQueue()
# Default value
distanceForward = 21
distanceLeft = 21
distanceRight = 21

class Cmd(Enum):
    FORWARD = 0
    LEFT = 1
    RIGHT = 2
    BACKWARD = 3
    NOTHING = 4

lastCmd = Cmd.NOTHING 

def append_log():
    while True:
        time.sleep(1)
        r = sub_sock.recv().decode('utf-8')
        sensorQueue.put(r)

t = threading.Thread(target=append_log, daemon=True )
t.start()

def run():
    global lastCmd
    if not sensorQueue.empty():
        req_sock.send_string("kbalance")
        req_sock.recv()
        lastCmd = Cmd.NOTHING

        # Vrid huvudet at hoger och kolla ultraljudsensor.
        req_sock.send_string("m0 -75")
        req_sock.recv() 
        time.sleep(2)
        distanceRight = int(sensorQueue.get().split(":")[1])
        print("Right distance: ", distanceRight)
        
        #Vrid huvudet åt vänster och kolla ultraljudsensor.
        req_sock.send_string("m0 75")
        req_sock.recv()
        time.sleep(2)
        distanceLeft = int(sensorQueue.get().split(":")[1])
        print("Left distance: ", distanceLeft)

        #Vrid huvudet fram och kolla ultraljudsensor
        req_sock.send_string("m0 0")
        req_sock.recv()
        time.sleep(2)
        distanceForward = int(sensorQueue.get().split(":")[1])
        print("Forward distance: ", distanceForward)
        
        if (distanceLeft > 20 and distanceRight > 20 and distanceForward >= 20 and lastCmd != Cmd.FORWARD):
            req_sock.send_string("kwkF")
            req_sock.recv()
            print("Should Walk Foward")
            lastCmd = Cmd.FORWARD
            time.sleep(2)

        elif(distanceLeft < 20 or distanceForward < 20 and lastCmd != Cmd.LEFT): # (distanceLeft < 20 or distanceForward < 15) and distanceRight > 20
            req_sock.send_string("kbkR")
            req_sock.recv()
            print("Should back Right")
            lastCmd = Cmd.LEFT
            time.sleep(2)

        elif(distanceRight < 20 or distanceForward < 20 and lastCmd != Cmd.RIGHT):
            req_sock.send_string("kbkL")
            req_sock.recv()
            print("Should back left")
            lastCmd = Cmd.RIGHT
            time.sleep(2)

        elif(distanceRight < 20 and distanceLeft < 20 and distanceForward < 20 and lastCmd != Cmd.BACKWARD):
            req_sock.send_string("kbk")
            req_sock.recv()
            print("Should back Backwards")
            lastCmd = Cmd.BACKWARD
            time.sleep(2)
            
        
        for i in range(4):
            distanceForward = int(sensorQueue.get().split(":")[1])
            if(distanceForward > 20 and not lastCmd == Cmd.FORWARD):
                req_sock.send_string("kwkF")
                req_sock.recv()
                print("Should walk Forward in loop ", i)
                lastCmd = Cmd.FORWARD
            elif distanceForward <= 20 and lastCmd != Cmd.BACKWARD:
                req_sock.send_string("kbkL")
                req_sock.recv()
                print("Should back Backwards in loop ", i)
                lastCmd = Cmd.BACKWARD
            time.sleep(2)

            
        
if __name__== "__main__":
    while True:
        try:
            run()
        except KeyboardInterrupt as e:
            print("Stopping")
            req_sock.send_string("kbalance")
            req_sock.recv()
            break