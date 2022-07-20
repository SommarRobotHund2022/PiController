import threading
import zmq
import queue
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

dog = config["DOG_TO_USE"]
socket = config['SOCKET']

context = zmq.Context()

sub_sock_server = context.socket(zmq.SUB)
sub_sock_server.connect(socket['socket'] + '2273')
sub_sock_server.setsockopt_string(zmq.SUBSCRIBE, dog['dog'] + ' MD:')

pub_sock_alerts = context.socket(zmq.PUB)
pub_sock_alerts.connect(socket['socket'] + '2274')


Queue_MD = queue.Queue()

def d():
    while True:
        print("hello")
        r = sub_sock_server.recv().decode('utf-8')
        print(r)
        if ("MD:" in r):
            r = r.replace(dog['dog'], '')
            Queue_MD.put(r.replace('MD:', '').strip().upper())
            return

t = threading.Thread(target=d, daemon=True )

