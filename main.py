from __future__ import print_function
import socket
from thread import *
import sys
import signal
import struct
import time
import os

seperator1 = "#"
seperator2 = "$"

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
        self.handlers = {"NAME":self.handleName, "LIST":self.handleList, "JOIN":self.handleJoin, "QUER":self.handleQuer, "RESP":self.handleResp, "FGET":self.handleFget, "QUIT":self.handleQuit, "REPL":self.handleRepl, "ERRO":self.handleErro, "RLPL":self.handleRlpl}
        self.myId = (self.host, self.port)

    def handlePeerConnection(self, clientSocket, peerAddress):
        # data = clientSocket.recv(1024)
        # print("data is ", data)
        # (host, port) = data.split()
        # print("host and port are ",host, int(port))
        # clientSocket.send("RCVD")
        # peerconn = PeerConnection(clientSocket)
        try:
            print("recieving data")
            peerconn = PeerConnection(peerAddress = peerAddress, sock = clientSocket)
            (msgType, msgData) = peerconn.recvData()
            print("messageType and message data are", msgType, msgData)
            if msgType != "REPL" and msgType != "RLPL":
                print ("Connection closed as msgType is %s..."%msgType)
                peerconn.close()
        except:
            print("Unable to receive data from the peer...")

        if msgType not in self.handlers:
            print("Invalid message type")
            return

        if msgType == "NAME":
            try:
                (host, port) = msgData.split(seperator2)
            except:
                print("error in splitting data")
            peerconn = PeerConnection(peerAddress = (host, int(port)))
            self.handleName(peerconn)

        if msgType == "LIST":
            try:
                (host, port) = msgData.split(seperator2)
            except:
                print("error in splitting data")
            peerconn = PeerConnection(peerAddress = (host, int(port)))
            self.handleList(peerconn)
        
        if msgType == "JOIN":
            """ Assuming the msgData is of the form host pair """
            try:
                host, port = msgData.split(seperator2)
                port = int(port)
                peerconn = PeerConnection(peerAddress = (host, int(port)))
            except:
                print("Invalid message type for join...")
            self.handleJoin(peerconn, host, port)
        
        if msgType == "QUER":
            """ Assuming the message is of the form queryFile ttl host port """
            try:
                queryFile, ttl, host, port = msgData.split(seperator2)
                port = int(port)
                ttl = int(ttl)
                peerconn = PeerConnection(peerAddress = (host, int(port)))
            except:
                print("Invalid message type for Query...")
            self.handleQuer(peerconn, queryFile, ttl, host, port)

        if msgType == "RESP":
            self.handleResp(msgData)

        if msgType == "FGET":
            """ Assuming the msgData is host, port, filename """
            try:
                (host, port, filename) = msgData.split(seperator2)
            except:
                print("error in splitting data")
            peerconn = PeerConnection(peerAddress = (host, int(port)))
            self.handleFget(peerconn, filename)

        if msgType == "QUIT":
            """ Assuming the msgData is of the form host port """
            try:
                host, port = msgData.split(seperator2)
                port = int(port)
            except:
                print("Invalid data format for Quit...")
            self.handleQuit(host, port)

        if msgType == "REPL":
            fdata, filename = msgData.split(seperator2)
            self.handleRepl(fdata, filename, peerconn)

        if msgType == "ERRO":
            self.handleErro(msgData)

        if msgType == "RLPL":
            self.handleRlpl(peerconn, int(msgData))         

    def main(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        try:
            print(self.host, self.port)
            sock.bind((self.host, self.port))
            print("binding succesfull")
        except socket.error,e:
            printDebugMessages(e)
            sys.exit()
        sock.listen(5)
        # time.sleep(2)
        # if self.port == 1234:
        #     peerconn1 = PeerConnection(('', 1235))
        #     self.addPeer(self.peerIdGenerator.getID(), ('', 1235))
        #     print("[peerConnection]  sending data")
        #     peerconn1.sendData("test", "Hi, did you recieve the message")
        #     print("[peerConnection]  sent data")
        # elif self.port == 1235:
        #     connection,peer = sock.accept()
        #     self.addPeer(self.peerIdGenerator.getID(), peer)
        #     peerconn2 = PeerConnection(('', 1234), sock = connection)
        #     print("[peerConnection]  recieving data")
        #     print(peerconn2.recvData())
        #     print("[peerConnection]  recieved data")

        # self.scheduler()
        self.initializeLocalFileTable()
        # start_new_thread(self.scheduler,())
        print("passed scheduler")
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
        
    # def sendData(self,peerAddress,data):
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     sock.connect(peerAddress)
    #     sock.sendall(data)
    #     sock.close()



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

    def initializeLocalFileTable(self):
        for i in os.listdir("./localFiles"):
            self.localFileTable[i] = "./localFiles/" + str(i)

    def addToLocalFileTable(self,fileName,filePath):
        if not fileName in self.localFileTable:
            self.localFileTable[fileName] = filePath
        

    def delFromLocalFileTable(self,fileName):
        if fileName in self.localFileTable:
            self.localFileTable.pop(fileName)
        
    def initializePeerFileTable(self):
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

    # Useless message type. Why do we need this type?
    # def handleName(self, peerconn):  # [TODO]
    #     """ Returns the official peerID """
    #     try:
    #         peerconn.sendData("REPL", "%s%s%d"%(self.myId[0], seperator2, self.myId[1]))
    #     except:
    #         print("Error in sending myId in handleName...")
    #     peerconn.close()

    def handleList(self, peerconn):
        """ Returns the list of known peers """
        try:
            peerconn.sendData("RLPL", "%d"%(self.getNumPeers()))
        except:
            print("Error in sending number of known peers...")
        peerList = self.getDictofPeers() # peerId -> (host, port) mapping dictionary
        for pid in peerList:
            (host, port) = peerList[pid]
            try:
                peerconn.sendData("RLPL", "%s%s%s%s%d"%(pid, seperator2, host, seperator2, port))
            except:
                print("Error in sending the peer List data in handleList...")
        peerconn.close()
    
    def handleRlpl(self, peerconn, npeersToRecv):
        """ Handles the reply of the List query send to the peer """
        for i in range(npeersToRecv):
            try:
                msgType, msgData = peerconn.recvData()
                assert(msgType == "RLPL")
                pid, host, port = msgData.split(seperator2)
                self.addPeer(pid, (host, port))
            except:
                print("Error in receiving the peer's file table...")
        peerconn.close()

    def handleJoin(self, peerconn, host, port):
        """ Adds the given peer to it's list of known peers """
        peerList = self.getDictofPeers()
        if self.getMaxPeers() >= self.getNumPeers():
            try:
                peerconn.sendData("ERRO", "Maximum limit reached. So can't add%s%s%s%d"%(seperator2, host, seperator2, port))
            except:
                print("Cannot send the error message that maximum number of peers reached...")
            return
        self.addPeer(self.peerIdGenerator.getID() ,(host, port)) # [TODO]
        peerconn.close()        
    
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
            peerconn.sendData("RESP", "%s%s%s%s%d"%(filename, seperator2,foundHost, seperator2,foundPort))
            peerconn.close()
            return

        for filename in fileDict:
            if filename == queryFile:
                (foundHost, foundPort) = fileDict[filename]
                break
        
        if foundHost != None:
            peerconn.sendData("RESP", "%s%s%s%s%d"%(filename, seperator2,foundHost, seperator2,foundPort))
            peerconn.close()
            return
        peerconn.close()
        # Coming here means no idea about the file. So broadcasting to neighbouring peers for the file
        if ttl > 0:
            msdData = "%s%s%d%s%s%s%d"%(queryFile, seperator2, ttl-1, seperator2, host, seperator2, port)
            peerDict = self.getDictofPeers()
            for pid in peerDict:
                (host, port) = peerDict[pid]
                conn1 = PeerConnection(peerAddress = (host, port))
                conn1.sendData("QUER", msdData)
                conn1.close()
                # self.sendToPeer("Quer", host, port, msdData)

    def handleResp(self, data):
        """ Add the queried response file to to my dict of known files """
        filename, host, port = data.split(seperator2)
        port = int(port)
        # fileDict = self.getDictOfFiles()
        self.peerFileTable[filename] = (host, port)
        print("updated peer file table is ", self.peerFileTable)
        
    def handleFget(self, peerconn, filename):
        """ Sends the file to the peer """
        try:
            f = open(self.localFileTable[filename], "r")
        except:
            print("File not found...")
        fdata = f.read(3)
        while fdata != "":
            fdata += seperator2
            fdata += filename
            try:
                peerconn.sendData("REPL", fdata)
            except:
                print("Error in sending the file data to peer...")
            fdata = f.read(1024)
        peerconn.sendData("REPL", "EndOfFile")
        peerconn.close()
        f.close()
        
    def handleRepl(self, fdata, filename, peerconn):
        """ Saves the filedata to the file """
        print("Downloading the file %s" %filename)
        f = open("./writeLocation/" + filename, "a")
        f.write(fdata)
        msgType, msgData = peerconn.recvData()
        while msgData != "EndOfFile":
            msgData,t = msgData.split(seperator2)
            f.write(msgData)
            msgType, msgData = peerconn.recvData()
        peerconn.close()
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
            conn1 = PeerConnection(peerAddress = (host, port))
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
            recvHoost, recvPort = msgData.split(seperator2)
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
                    pid, recvHoost, recvPort = msgData.split(seperator2)
                    recvPort = int(recvPort)
                    self.addPeer(pid, (recvHoost, recvPort)) 
            except:
                print("Error in receiving the peer List...")
            conn1.close()
            
            myPeerDict = self.getDictofPeers()
            for pid in myPeerDict:
                self.buildPeerList(myPeerDict[0], myPeerDict[1], hops-1)

        except:
            print("Error in building peer list")
        
    def refreshPeerList(self):
        removePeerList = []
        print(self.peers)
        print("in refreshPeerList")
        for i in self.peers:
            try:
                conn = PeerConnection(peerAddress = self.peers[i])
                print("connection still active", self.peers[i])
                conn.close()
            except:
                removePeerList.append(i)
                print("Adding lazy connection", self.peers[i])
        for i in removePeerList:
            self.delFromPeerFileTable(self.peers[i])
            print("removing inactive peer", self.peers[i])
            self.peers.pop(i)

    def scheduler(self):
        while(1):
            self.refreshPeerList()
            time.sleep(5)


class GeneratePeerID():
    def __init__(self):
        self.id = 0

    def getID(self):
        self.id +=1
        return self.id

class PeerConnection():
    def __init__(self, peerAddress = None, sock = None):
        if sock:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Opening socket to peerAddress:",peerAddress)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            self.sock.connect(peerAddress)

    def sendData(self,msgType, data):
        print("Sending data...")
        self.sock.send(str(msgType) + seperator1 + str(data))
        print("Data sent. Waiting for ack...")
        self.sock.recv(1)
        print("Ack received....")

    def recvData(self):
        print("Receiving Data...")
        data = self.sock.recv(65535)
        print("Data received. Sending Ack...")
        self.sock.send("A")
        print("Ack sent...")
        tmp = (data[0:4], data[5:])
        print("Data returned is: ",tmp)
        return tmp

    def close(self):
        self.sock.close()

