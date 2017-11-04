class Peer:
    def __init__(self, host, port):
        """ Assumed getters:
            self.getDictofPeers() expecting dictionary with pid->(host,port)
            self.getNumOfPeers()
            self.getDictOfFiles() Dict of known files
            self.getMaxPeers()
            self.getOwnFileList() List of files in local machine
            self.getMyHost()
            self.getMyPort()
        """
        self.handlers = {"NAME":self.handleName, "LIST":self.handleList, "JOIN":self.handleJoin, "Quer":self.handleQuer, "RESP":self.handleResp, "FGET":self.handleFget, "QUIT":self.handleQuit, "REPL":self.handleRepl, "ERRO":self.handleErro}
        self.myId = (host, port)

    def handle(self, clientSocket):
        host, port = clientSocket.getpeername()
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
            

    def handleName(self, peerconn):
        """ Returns the official peerID """
        try:
            peerconn.sendData("REPL", self.myId)
        except:
            print("Error in sending myId in handleName...")

    def handleList(self, peerconn):
        """ Returns the list of known peers """
        try:
            peerconn.sendData("REPL", "%d"%(self.getNumOfPeers()))
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
        if self.getMaxPeers() >= self.getNumOfPeers():
            try:
                peerconn.sendData("ERRO", "Maximum limit reached. So can't add %s %d"%(host, port))
            except:
                print("Cannot send the error message that maximum number of peers reached...")
            return
        self.addPeer(host, port)
    
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
                self.sendToPeer("Quer", host, port, msdData)

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

    def buildPeerList(self, host, port, hops=1):
        """ Makes the list of peer list by querying from the immediate neighbours """
        if self.getNumOfPeers() >= self.getMaxPeers() or not hops:
            return
        
        