import threading
import zmq
import queue

context = zmq.Context()

sub_sock_server = context.socket(zmq.SUB)
sub_sock_server.connect('tcp://192.168.137.1:2273')
sub_sock_server.setsockopt(zmq.SUBSCRIBE, b'MD:')
sub_sock_server.setsockopt(zmq.SUBSCRIBE, b'ST:')


Queue_MD = queue.Queue()
Queue_ST = queue.Queue()

def d():
    while True:
        r = sub_sock_server.recv().decode('utf-8')
        if ("MD:" in r):
            Queue_MD.put(r.replace('MD:', '').strip().upper())
        elif ("ST:" in r):
            Queue_ST.put(r.replace('ST:', '').strip().upper())
        else:
            return

t = threading.Thread(target=d, daemon=True )

