from enum import Enum
import threading
import auto
import manual
import zmq
PORT = "/dev/ttyS0"
from pisockets import Queue_MD, Queue_ST, t, pub_sock_alerts, dog

class Modes(Enum):
    MANUAL = 0
    AUTO = 1
    DAY = 2
    NIGHT = 3

MODES = [manual, auto, None, None]
MODE = None

def bg():
    global MODE
    while True:
        if (not Queue_MD.empty()):
            print("entered queue") 
            mode = Queue_MD.get()
            if mode == Modes.MANUAL.name:
                print("enter manual mode")
                MODE = Modes.MANUAL
            elif mode == Modes.AUTO.name:
                print("enter auto mode")
                MODE = Modes.AUTO
        elif (not Queue_ST.empty()):
            # We dont really care about the value in the queue, its just to see if a new swap has been made by the webapp, and if it has it returns what mode this dog currently is in
            Queue_ST.get()
            pub_sock_alerts.send_string(dog['dog'] + MODE.name)

t1 = threading.Thread(target=bg, daemon=True)
def main():
    t.start()
    t1.start()
    while True:
        if (MODE != None):
            MODES[MODE.value].run()

if __name__=='__main__':
    main()



