#!/usr/bin/python3
from ast import NodeTransformer
from enum import Enum
import threading
import zmq
import time
from queue import Queue, LifoQueue
from pisockets import pub_sock_alerts, dog, socket

SLEEPTIMER = 1

context = zmq.Context()
req_sock = context.socket(zmq.REQ)
sub_sock = context.socket(zmq.SUB)
sub_sock.connect(socket['socket'] + '2276')
req_sock.connect("tcp://127.0.0.1:2272")
sub_sock.setsockopt_string(zmq.SUBSCRIBE, dog['dog'] + ' distance is :')

sensorQueue = LifoQueue()
# Default value
distanceForward = 21
distanceLeft = 21
distanceRight = 21

total_stuck = 0

class Cmd(Enum):
    FORWARD = 0
    LEFT = 1
    RIGHT = 2
    BACKWARD = 3
    NOTHING = 4

lastCmd = Cmd.NOTHING 

def append_log():
    while True:
        time.sleep(0.5)
        r = sub_sock.recv().decode('utf-8')
        print(r)
        sensorQueue.put(r)

t = threading.Thread(target=append_log, daemon=True )
t.start()

def run():
    print("hello")
    global lastCmd
    global total_stuck

    if not sensorQueue.empty():
        firstValue = None
        counter_alert = 0
        req_sock.send_string("kbalance")
        req_sock.recv()
        lastCmd = Cmd.NOTHING


        req_sock.send_string("ksit")
        req_sock.recv()
        # Vrid huvudet at hoger och kolla ultraljudsensor.
        req_sock.send_string("m0 -75")
        req_sock.recv() 
        time.sleep(2)
        distanceRight = int(sensorQueue.get().split(":")[2])
        print("Right distance: ", distanceRight)
        
        #Vrid huvudet åt vänster och kolla ultraljudsensor.
        req_sock.send_string("m0 75")
        req_sock.recv()
        time.sleep(2)
        distanceLeft = int(sensorQueue.get().split(":")[2])
        print("Left distance: ", distanceLeft)

        #Vrid huvudet fram och kolla ultraljudsensor
        req_sock.send_string("m0 0")
        req_sock.recv()
        time.sleep(2)
        distanceForward = int(sensorQueue.get().split(":")[2])
        print("Forward distance: ", distanceForward)
        
        req_sock.send_string("kbalance")
        req_sock.recv()
        time.sleep(2)


        if(distanceForward > 25 and not lastCmd == Cmd.FORWARD):
            req_sock.send_string("kwkF")
            req_sock.recv()
            time.sleep(1.25)

        elif(distanceLeft < 25 and distanceForward <= 25 and lastCmd != Cmd.LEFT):
            req_sock.send_string("kbkR")
            req_sock.recv()
            print("Should back Right")
            lastCmd = Cmd.LEFT
            time.sleep(1.25)

        elif(distanceRight < 25 and distanceForward < 25 and lastCmd != Cmd.RIGHT):
            req_sock.send_string("kbkL")
            req_sock.recv()
            print("Should back left")
            lastCmd = Cmd.RIGHT
            time.sleep(1.25)

        elif(distanceRight < 25 and distanceLeft < 25 and distanceForward < 25 and lastCmd != Cmd.BACKWARD):
            req_sock.send_string("kbk")
            req_sock.recv()
            lastCmd = Cmd.BACKWARD
            time.sleep(1.25)

        elif(distanceForward <= 25 and not lastCmd == Cmd.BACKWARD):
            req_sock.send_string("kbkL")
            req_sock.recv()
            lastCmd = Cmd.BACKWARD
            time.sleep(1.25)

        for i in range(12):
            distanceForward = int(sensorQueue.get().split(":")[2])

            if (firstValue == None):
                firstValue = distanceForward

            if (firstValue != None and (distanceForward >= firstValue-3 and distanceForward <= firstValue+3)):
                counter_alert += 1

            if(distanceForward > 25 and not lastCmd == Cmd.FORWARD):
                req_sock.send_string("kwkF")
                req_sock.recv()
                lastCmd = Cmd.FORWARD
            elif distanceForward <= 25 and lastCmd != Cmd.BACKWARD:
                req_sock.send_string("kbkL")
                req_sock.recv()
                lastCmd = Cmd.BACKWARD
            time.sleep(1.25)

        if counter_alert >= 4:
            if total_stuck < 3:
                total_stuck += 1
        else:
            if total_stuck > 0:
                total_stuck -= 2
        print(total_stuck)
        if total_stuck >= 2:    
            pub_sock_alerts.send_string(dog['dog'] + " Stuck")
        else:
            pub_sock_alerts.send_string(dog['dog'] + " Operational")
        # while not sensorQueue.empty():
        #         sensorQueue.get()

            
        
if __name__== "__main__":
    req_socket.send_string("kwkF")
    while True:
        try:
            run()
        except KeyboardInterrupt as e:
            print("Stopping")
            req_sock.send_string("kbalance")
            req_sock.recv()
            break
