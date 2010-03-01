import sys
import ChrSocket

client = ChrSocket.ChrSocket()
hostname = ChrSocket.socket.gethostname()
hostaddr = ChrSocket.socket.gethostbyname(hostname)
port = 1098
client.connect(hostaddr, port)

try:
    while True:
        sdata = raw_input("Enter string data ['' to quit]: ")
        ndata = raw_input("Enter int repeat ['' to quit]: ")
        if sdata=='' or ndata=='': break
        sentmsg = int(ndata) * str(sdata)

        client.send(sentmsg)
        print 'sending report: ', sentmsg[0], len(sentmsg), client.nsent

        recvmsg=client.recv()
        print 'receive report: ', recvmsg[0], len(recvmsg), client.nrecv

        if recvmsg!=sentmsg: print 'received != sent' 

        print

except: print sys.exc_info()[0], sys.exc_info()[1]

client.close()
























