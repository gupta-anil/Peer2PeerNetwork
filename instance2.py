from main import *
from thread import *

obj = Peer2PeerNetwork(port = 1234)
obj.main()
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
# sock.connect(('', 1234 ))
# sock.send("'' 1235" )
# sock.send("FGET 1.py")