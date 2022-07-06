from enum import Enum
import threading
from OpenCatSerial import *
import auto
import manual
import zmq
PORT = "/dev/ttyS0"

class Modes(Enum):
    MANUAL = 0
    AUTO = 1
    DAY = 2
    NIGHT = 3

context = zmq.Context()
sub_sock = context.socket(zmq.SUB)
sub_sock.connect("tcp://127.0.0.1:2273")
sub_sock.setsockopt(zmq.SUBSCRIBE, b'MD:')
sub_sock.setsockopt(zmq.SUBSCRIBE, b'ST:')

MODES = [manual, auto, None, None]
MODE = Modes.AUTO

def bg():
    while True:
        cmd = sub_sock.recv().decode('utf-8').replace('MD:', '').strip().capitalize()
        if cmd == Modes.MANUAL.name:
            MODE = Modes.MANUAL
        elif cmd == Modes.AUTO.name:
            MODE = Modes.AUTO

t = threading.Thread(target=bg, daemon=True )

def main():
    t.start()
    while True:
        MODES[MODE.value].run()
    
def open_serial(sc):
        try:
            sc = OpenCatSerialConnection()
        except:
            print('Not OpenCat found on', PORT)
            exit(1)

if __name__=='__main__':
    main()
