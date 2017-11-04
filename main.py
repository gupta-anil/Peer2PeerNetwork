import socket
from thread import *
import sys
import signal

maxLengthExceededError = "123"
peerNotFound = "124"
def printDebugMessages(error):
    print("[%s] %s" %(e[0], e[1]))


class Peer2PeerNetwork():
    """docstring for Peer2PeerNetwork"""
    def __init__(self, port = 1234, maxConnections = 5, maxPeers = 10):
        # super(Peer2PeerNetwork, self).__init__()
        self.peers = {}
        self.host = "localhost"
        self.port = port
        self.maxConnections = maxConnections
        self.maxPeers = maxPeers
        self.peerIdGenerator = GeneratePeerID()

        
    def main(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        try:
            sock.bind((self.host, self.port))
            print("binding succeful")
        except socket.error,e:
            printDebugMessages(e)
            sys.exit()
        sock.listen(5)
        while(1):
            try:
                connection, peerAddress = sock.accept()
                print("(peerAddress is "+ str(peerAddress))
                self.addPeer(self.peerIdGenerator.getID(), peerAddress)
                start_new_thread(self.handlePeerConnection, (connection, peerAddress))
            except KeyboardInterrupt:
                for i in self.getPeerIds():
                    self.removePeer(i)
                print("exiting\n")
                sock.close()
                sys.exit()
        
 
    def addPeer(self, pid, peerAddress):
        if not peerAddress in self.peers.values():
            if len(self.peers) < self.maxPeers:
                self.peers[pid] = peerAddress
                print("connection added", peerAddress)
            else:
                printDebugMessages([maxLengthExceededError, "Maximum number of peers exceeded"])

    def removePeer(self, pid):
        if pid in self.peers:
            removedConnection = self.peers.pop(pid)
            print("connection removed", removedConnection)
        else:
            printDebugMessages([peerNotFound, "Cannot remove a non existing peer"])

    def getNumPeers(self):
        return len(self.peers)

    def getPeerIds(self):
        return self.peers.keys()

    def handlePeerConnection(self,connection, peerAddress):
        pass

class GeneratePeerID():
    def __init__(self):
        self.id = 0

    def getID(self):
        self.id +=1
        return self.id

obj = Peer2PeerNetwork()
obj.main()