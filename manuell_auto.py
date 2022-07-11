from enum import Enum
import threading
import auto
import manual
import zmq
PORT = "/dev/ttyS0"
from piserver import Queue_MD, Queue_ST, t

class Modes(Enum):
    MANUAL = 0
    AUTO = 1
    DAY = 2
    NIGHT = 3

MODES = [manual, auto, None, None]
MODE = Modes.AUTO

def bg():
    global MODE
    while True:
        if (not Queue_MD.empty()):
            if Queue_MD.get == Modes.MANUAL.name:
                MODE = Modes.MANUAL
            elif Queue_MD.get == Modes.AUTO.name:
                MODE = Modes.AUTO

def main():
    t.start()
    while True:
        MODES[MODE.value].run()

if __name__=='__main__':
    main()
