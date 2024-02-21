import sys
import ChrSocket

server = ChrSocket.ChrSocket()
hostname = ChrSocket.socket.gethostname()
hostaddr = ChrSocket.socket.gethostbyname(hostname)
port = 1099
address = (hostaddr, port)
server.bind(address)
server.listen(1)
print('Listening server at address = %s' % str(address))
client, addr = server.accept()
print('Get Connection from ', addr)

try:
    while True:

        recvmsg=client.recv()
        print('receive report: ', recvmsg[0], len(recvmsg), client.nrecv)

        sentmsg=recvmsg
        client.send(sentmsg)
        print('sending report: ', sentmsg[0], len(sentmsg), client.nsent)
        
        print()
    
except: print(sys.exc_info()[0], sys.exc_info()[1])

client.close()
server.close()
    
