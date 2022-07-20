from enum import Enum
import threading
import auto
import manual
import zmq
PORT = "/dev/ttyS0"
from piserver import Queue_MD, t

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
            
            mode = Queue_MD.get()
            if mode == Modes.MANUAL.name:
                MODE = Modes.MANUAL
            elif mode == Modes.AUTO.name:
                MODE = Modes.AUTO

t1 = threading.Thread(target=bg, daemon=True)
def main():
    t.start()
    t1.start()
    while True:
        if (MODE != None):
            MODES[MODE.value].run()

if __name__=='__main__':
    main()



