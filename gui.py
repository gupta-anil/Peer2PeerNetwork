import sys
import threading
import socket
from Tkinter import *
from random import *
from main import *
from thread import *

class GUI(Frame):
    def __init__( self,firstpeer,serverport,master=None):
        Frame.__init__(self,master)
        self.grid()
        self.createWidgets()
        self.master.title( "GUI ")
        self.p2pnetwork = Peer2PeerNetwork(port=serverport)
        host,port = firstpeer.split(':')
        self.p2pnetwork.initializeLocalFileTable()
        self.p2pnetwork.initializePeerFileTable()
        self.updateFileList()
        self.updatePeerFileList()
        self.p2pnetwork.addPeer(1,(host,port))
        self.updatePeerList()
        print "Thread to Be started"

        # t = threading.Thread( target = self.p2pnetwork.main, args = [] )
        # t.start()
        
        start_new_thread(self.p2pnetwork.main,())

    def updatePeerList( self ):
        if self.peerList.size() > 0:
            self.peerList.delete(0, self.peerList.size() - 1)
        for p in self.p2pnetwork.getPeerIds():
            self.peerList.insert( END, p )


    def updateFileList( self ):
        if self.fileList.size() > 0:
            self.fileList.delete(0, self.fileList.size() - 1)
        for f in self.p2pnetwork.localFileTable:
            # print f 
            p = self.p2pnetwork.localFileTable[f]
            if not p:
                p = '(local)'
            self.fileList.insert( END, "%s:%s" % (f,p))
    def updatePeerFileList( self ):
        if self.peerfileList.size() > 0:
            self.peerfileList.delete(0, self.peerfileList.size() - 1)
        for f in self.p2pnetwork.peerFileTable:
            # print f 
            p = self.p2pnetwork.peerFileTable[f]
            if not p:
                p = '(peer)'
            self.fileList.insert( END, "%s:%s" % (f,p) )

    def onAdd(self):
      file = self.addfileEntry.get()
      if file.lstrip().rstrip():
         filename = file.lstrip().rstrip()
         self.p2pnetwork.addToLocalFileTable( filename,"./localFiles"+filename )
      self.addfileEntry.delete( 0, len(file) )
      self.updateFileList()


    def onSearch(self):
      key = self.searchEntry.get()
      self.searchEntry.delete( 0, len(key) )
      print key

      for p in self.p2pnetwork.getPeerIds():
        print self.p2pnetwork.myId
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.connect(('',1234))
        # sock.send("ERRO sendingerrormsg")
        peerconn = PeerConnection(peerAddress = self.p2pnetwork.myId)
        # time.sleep(2)
        # peerconn = self.p2pnetwork.PeerConnection(peerAddress = self.myId)
        peerconn.sendData("QUER",key+":2:"+self.p2pnetwork.host+":"+str(self.p2pnetwork.port))
        # self.p2pnetwork.sendtopeer( p, QUERY, "%s %s 4" % ( self.btpeer.myid, key ) )


    def onFetch(self):
      sels = self.fileList.curselection()
      if len(sels)==1:
         sel = self.fileList.get(sels[0]).split(':')
         if len(sel) > 2:  # fname:host:port
            fname,host,port = sel
            # resp = self.btpeer.connectandsend( host, port, FILEGET, fname )
            if len(resp) and resp[0][0] == REPLY:
               fd = file( fname, 'w' )
               fd.write( resp[0][1] )
               fd.close()
               self.p2pnetwork.localFileTable[fname] = "./localFiles"+fname  # because it's local now


    def onRemove(self):
      sels = self.peerList.curselection()
      if len(sels)==1:
         peerid = self.peerList.get(sels[0])
         # self.btpeer.sendtopeer( peerid, PEERQUIT, self.btpeer.myid )
         self.p2pnetwork.removePeer(peerid)


    def onRefresh(self):
        self.updatePeerList()
        self.updateFileList()
        # Update Peer File List HERE 
        # self.peerfileList.insert( END, 'a', 'b', 'c', 'd', 'e', 'f', 'g' )


    def createWidgets(self):
        fileFrame = Frame(self)
        peerfileFrame = Frame(self)
        peerFrame = Frame(self)

        rebuildFrame = Frame(self)
        searchFrame = Frame(self)
        addfileFrame = Frame(self)
        pbFrame = Frame(self)

        fileFrame.grid(row=0, column=0, sticky=N+S)
        peerFrame.grid(row=0, column=1, sticky=N+S)
        peerfileFrame.grid(row = 0, column = 2, sticky= N+S)
        pbFrame.grid(row=2, column=1)
        addfileFrame.grid(row=3)
        searchFrame.grid(row=4)
        rebuildFrame.grid(row=3, column=1)

        Label( fileFrame, text='Available Files' ).grid()
        Label( peerFrame, text='Peer List' ).grid()
        Label( peerfileFrame, text='PeerFile  List' ).grid()

        fileListFrame = Frame(fileFrame)
        fileListFrame.grid(row=1, column=0)
        fileScroll = Scrollbar( fileListFrame, orient=VERTICAL )
        fileScroll.grid(row=0, column=1, sticky=N+S)

        self.fileList = Listbox(fileListFrame, height=5, 
                            yscrollcommand=fileScroll.set)
        # self.fileList.insert( END, 'a', 'b', 'c', 'd', 'e', 'f', 'g' )
        self.fileList.grid(row=0, column=0, sticky=N+S)
        fileScroll["command"] = self.fileList.yview

        peerfileListFrame = Frame(peerfileFrame)
        peerfileListFrame.grid(row=1, column=0)
        peerfileScroll = Scrollbar( peerfileListFrame, orient=VERTICAL )
        peerfileScroll.grid(row=0, column=1, sticky=N+S)

        self.peerfileList = Listbox(peerfileListFrame, height=5, 
                            yscrollcommand=peerfileScroll.set)
        # self.peerfileList.insert( END, 'a', 'b', 'c', 'd', 'e', 'f', 'g' )
        self.peerfileList.grid(row=0, column=0, sticky=N+S)
        peerfileScroll["command"] = self.peerfileList.yview

        self.fetchButton = Button( peerfileFrame, text='Fetch',
                          command=self.onRefresh)
        self.fetchButton.grid()

        self.addfileEntry = Entry(addfileFrame, width=25)
        self.addfileButton = Button(addfileFrame, text='Add',
                          command=self.onAdd)
        self.addfileEntry.grid(row=0, column=0)
        self.addfileButton.grid(row=0, column=1)

        self.searchEntry = Entry(searchFrame, width=25)
        self.searchButton = Button(searchFrame, text='Search', 
                          command=self.onSearch)
        self.searchEntry.grid(row=0, column=0)
        self.searchButton.grid(row=0, column=1)

        peerListFrame = Frame(peerFrame)
        peerListFrame.grid(row=1, column=0)
        peerScroll = Scrollbar( peerListFrame, orient=VERTICAL )
        peerScroll.grid(row=0, column=1, sticky=N+S)

        self.peerList = Listbox(peerListFrame, height=5,
                      yscrollcommand=peerScroll.set)
        #self.peerList.insert( END, '1', '2', '3', '4', '5', '6' )
        self.peerList.grid(row=0, column=0, sticky=N+S)
        peerScroll["command"] = self.peerList.yview

        self.removeButton = Button( pbFrame, text='Remove',
                                  command=self.onRemove )
        self.refreshButton = Button( pbFrame, text = 'Refresh', 
                          command=self.onRefresh )

        # self.rebuildEntry = Entry(rebuildFrame, width=25)
        # self.rebuildButton = Button( rebuildFrame, text = 'Rebuild', 
        #                   command=self.onRebuild )
        self.removeButton.grid(row=0, column=0)
        self.refreshButton.grid(row=0, column=1)
        # self.rebuildEntry.grid(row=0, column=0)
        # self.rebuildButton.grid(row=0, column=1)




# def startapp():
#   app = GUI()
#   app.mainloop()

# if __name__=='__main__':
#   startapp()
app = GUI("localhost:1235",1234)
app.mainloop()