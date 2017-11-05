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
        self.localFileTable = {} # contains tuple fileName, file path, 
        self.peerFileTable = {} # stores the tuple fileName, list of peers having the file
        self.handlers = {"NAME":self.handleName, "LIST":self.handleList, "JOIN":self.handleJoin, "Quer":self.handleQuer, "RESP":self.handleResp, "FGET":self.handleFget, "QUIT":self.handleQuit, "REPL":self.handleRepl, "ERRO":self.handleErro}
        self.myId = (host, port)


    def handlePeerConnection(self, clientSocket, peerAddress):
        (host, port) = peerAddress
        peerconn = PeerConnection(None, host, port, clientSocket)
        try:
            msgType, msgData = peerconn.recvData()
        except:
            print("Unable to receive data from the peer...")
        if msgType not in self.handlers:
            print("Invalid message type")
            return
        
        if msgType == "NAME":
            self.handleName(peerconn)
        if msgType == "LIST":
            self.handleList(peerconn)
        if msgType == "JOIN":
            """ Assuming the msgData is of the form host pair """
            try:
                host, port = msgData.split()
                port = int(port)
            except:
                print("Invalid message type for join...")
            self.handleJoin(peerconn, host, port)
        if msgType == "Quer":
            """ Assuming the message is of the form queryFile ttl host port """
            try:
                queryFile, ttl, host, port = msgData.split()
                port = int(port)
                ttl = int(ttl)
            except:
                print("Invalid message type for Query...")
            self.handleQuer(peerconn, queryFile, ttl, host, port)
        if msgType == "RESP":
            self.handleResp(msgData)
        if msgType == "FGET":
            """ Assuming the msgData is same as the filename """
            self.handleFget(peerconn, msgData)
        if msgType == "QUIT":
            """ Assuming the msgData is of the form host port """
            try:
                host, port = msgData.split()
                port = int(port)
            except:
                print("Invalid data format for Quit...")
            self.handleQuit(host, port)
        if msgType == "REPL":
            fdata, filename = msgData.split("[saket,anil,abhishek]")
            self.handleRepl(peerconn, fdata, filename)
        if msgType == "ERRO":
            self.handleErro(msgData)
            

    def main(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        try:
            sock.bind((self.host, self.port))
            print("binding succesfull")
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
        
    def sendData(self,peerAddress,data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(peerAddress)
        sock.sendall(data)
        sock.close()



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

    def initializeLocalFileTable():
        pass

    def addToLocalFileTable(self,fileName,filePath):
        if not fileName in self.localFileTable:
            self.localFileTable[fileName] = filePath
        

    def delFromLocalFileTable(self,fileName):
        if fileName in self.localFileTable:
            self.localFileTable.pop(fileName)
        

    def initializePeerFileTable():
        pass

    def addToPeerFileTable(self, fileName, peerAddress):
        if fileName in self.peerFileTable:
            self.peerFileTable[fileName].append(peerAddress)
        else:
            self.peerFileTable[fileName] = [peerAddress]

    def delFromPeerFileTable(self, peerAddress, fileName = None):
        if fileName is None:
            for i in self.peerFileTable:
                if peerAddress in self.peerFileTable[i]:
                    self.peerFileTable[i].remove(peerAddress)
        else:
            if peerAddress in self.peerFileTable[fileName]:
                self.peerFileTable[fileName].remove(peerAddress)

    def getDictofPeers(self):
        return self.peers

    def getDictOfFiles(self):
        return self.peerFileTable

    def getMaxPeers(self):
        return self.maxPeers

    def getOwnFileList(self):
        return self.localFileTable.keys()

    def getMyHost(self):
        return self.host

    def getMyPort(self):
        return self.port






    def handleName(self, peerconn):
        """ Returns the official peerID """
        try:
            peerconn.sendData("REPL", "%s %d"%(self.myId[0], self.myId[1]))
        except:
            print("Error in sending myId in handleName...")

    def handleList(self, peerconn):
        """ Returns the list of known peers """
        try:
            peerconn.sendData("REPL", "%d"%(self.getNumPeers()))
        except:
            print("Error in sending number of known peers...")
        peerList = self.getDictofPeers() # peerId -> (host, port) mapping dictionary
        for pid in peerList:
            (host, port) = peerList[pid]
            try:
                peerconn.sendData("REPL", "%s %s %d"%(pid, host, port))
            except:
                print("Error in sending the peer List data in handleList...")
    
    def handleJoin(self, peerconn, host, port):
        """ Adds the given peer to it's list of known peers """
        peerList = self.getDictofPeers()
        if self.getMaxPeers() >= self.getNumPeers():
            try:
                peerconn.sendData("ERRO", "Maximum limit reached. So can't add %s %d"%(host, port))
            except:
                print("Cannot send the error message that maximum number of peers reached...")
            return
        self.addPeer(self.peerIdGenerator.getID() ,(host, port)) # [TODO]
    
    def handleQuer(self, peerconn, queryFile, ttl, host, port):
        """ Returns whether it has the required files."""
        fileDict = self.getDictOfFiles()
        ownFileList = self.getOwnFileList()
        foundHost, foundPort = None, None
        for filename in ownFileList:
            if filename == queryFile:
                foundHost = self.getMyHost()
                foundPort = self.getMyPort()
                break
        if foundHost != None:
            peerconn.sendData("RESP", "%s %s %d"%(filename, foundHost, foundPort))
            return

        for filename in fileDict:
            if filename == queryFile:
                (foundHost, foundPort) = fileDict[filename]
                break
        
        if foundHost != None:
            peerconn.sendData("RESP", "%s %s %d"%(filename, foundHost, foundPort))
            return

        # Coming here means no idea about the file. So broadcasting to neighbouring peers for the file
        if ttl > 0:
            msdData = "%s %d %s %d"%(queryFile, ttl-1, host, port)
            peerDict = self.getDictofPeers()
            for pid in peerDict:
                (host, port) = peerDict[pid]
                conn1 = PeerConnection(host, port)
                conn1.sendData("QUER", msdData)
                conn1.close()
                # self.sendToPeer("Quer", host, port, msdData)

    def handleResp(self, data):
        """ Add the queried response file to to my dict of known files """
        filename, host, port = data.split()
        port = int(port)
        fileDict = self.getDictOfFiles()
        fileDict[filename] = (host, port)
        
    def handleFget(self, peerconn, filename):
        """ Sends the file to the peer """
        try:
            f = open(filename, "r")
        except:
            print("File not found...")
        fdata = f.read()
        fdata += "[saket,anil,abhishek]"
        fdata += filename
        try:
            peerconn.sendData("REPL", fdata)
        except:
            print("Error in sending the file data to peer...")
        f.close()

    def handleQuit(self, host, port):
        """ Removes the host, port peer from list of known peers """
        peerDict = self.getDictofPeers()
        pid = None
        for p in peerDict:
            if peerDict[p][0] == host and peerDict[p][1] == port:
                pid = p
                break
        if pid != None:
            del peerDict[pid]
        return

    def handleRepl(self, peerconn, fdata, filename):
        """ Saves the filedata to the file """
        print("Downloading the file %s", filename)
        f = open(filename, "w")
        f.write(fdata)
        f.close()
        print("Downloaded the file...")
        ownFileList = self.getOwnFileList()
        found = False
        for file in ownFileList:
            if file == filename:
                found = True
                break
        if found == False:
            ownFileList.append(filename)
            print("Added the file %s to my local list of files..."%filename)

    def handleErro(self, error):
        """ Prints the error """
        print("Error received: %s", error)


    def buildPeerList(self, host, port, hops = 1):
        """ Build the list of known peers upto the maximum number allowed """
        if hops <= 0:
            return
        if self.getMaxPeers() >= self.getNumPeers():
            return
        try:
            conn1 = PeerConnection(host, port)
            try:
                conn1.sendData("NAME", "")
            except:
                print("Error sending the NAME query...")
            try:
                msgType, msgData = conn1.recvData()
                if msgType != "NAME":
                    raise
            except:
                print("Error receiving the response of the NAME query")
            recvHoost, recvPort = msgData.split()
            recvPort = int(recvPort)
            self.addPeer(self.GeneratePeerID(), (recvHoost, recvPort))

            # Do recursive depth first search to add more peers
            try:
                conn1.sendData("LIST", "")
            except:
                print("Error in seding the LIST query...")
            try:
                msgType, msgData = conn1.recvData()
                if msgType != "REPL":
                    raise
                npeers = int(msgData) # number of peers it knows
                for i in range(npeers):
                    msgType, msgData = conn1.recvData()
                    if msgType != "REPL":
                        raise
                    pid, recvHoost, recvPort = msgData.split()
                    recvPort = int(recvPort)
                    self.addPeer(pid, (recvHoost, recvPort)) 
            conn1.close()
            except:
                print("Error in receiving the peer List...")
            
            myPeerDict = self.getDictofPeers()
            for pid in myPeerDict:
                self.buildPeerList(myPeerDict[0], myPeerDict[1], hops-1)

        except:
            print("Error in building peer list")
        


class GeneratePeerID():
    def __init__(self):
        self.id = 0

    def getID(self):
        self.id +=1
        return self.id
