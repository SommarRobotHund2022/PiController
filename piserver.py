import threading
import zmq
import queue

context = zmq.Context()

sub_sock_server = context.socket(zmq.SUB)
sub_sock_server.connect('tcp://192.168.137.1:2273')
sub_sock_server.setsockopt(zmq.SUBSCRIBE, b'MD:')
sub_sock_server.setsockopt(zmq.SUBSCRIBE, b'ST:')

pub_sock_alerts = context.socket(zmq.PUB)
pub_sock_alerts.connect('tcp://192.168.137.1:2274')


Queue_MD = queue.Queue()
Queue_ST = queue.Queue()
lock = threading.Lock()
def d():
    while True:
        r = sub_sock_server.recv().decode('utf-8')
        print("Incoming message: " + r)
        if ("MD:" in r):
            print("adding message to mode queue")
            lock.acquire()
            Queue_MD.put(r.replace('MD:', '').strip().upper())
            lock.release()
        elif ("ST:" in r):
            lock.acquire()
            Queue_ST.put(r.replace('ST:', '').strip().upper())
            lock.release()
        else:
            return

t = threading.Thread(target=d, daemon=True )

