from main import *
from thread import *

obj = Peer2PeerNetwork(port = 1235)
# print("passed through main")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
sock.connect(('', 1234 ))
sock.send("'' 1235" )
sock.recv(1024)
sock.send("FGET 1.py")
start_new_thread(obj.main(),())