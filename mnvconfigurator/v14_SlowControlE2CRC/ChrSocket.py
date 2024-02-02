import socket
import sys

class ChrSocket():
    '''
    A socket with custom Send and Receive methods.
    This socket can be (re)used for MULTIPLE tranfers.
    The length of data sent and received is arbitrary.
    The user does not need to care of following:
        1. If the 'send' managed to sent the full message. 
        2. If the 'recv' managed to receive the full message.
        There might be more than one 'send' or 'recv' activity
        underhood, transparent to the user.
    This is handled by implementing a protocol where any sent
    socket is appending a dedicated and unique character at the
    end of the message, which is then checked by the receiver
    socket. The user can change the (default) character value.
    '''
    def __init__(self):
        '''(socket.AF_INET, socket.SOCK_STREAM) -> socket object'''
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        '''the maximum amount of data to be received at once'''
        self.bufsize=4096
        '''the unique character to be used at the end on any message'''
        self.chrend=';'
        '''how many times per message the 'socked.socked.send' was used'''
        self.nsent=0
        '''how many times per message the 'socked.socked.recv' was used'''
        self.nrecv=0
    def connect(self, host, port): self.sock.connect((host, port))
    def close(self): self.sock.close()
    def bind(self, addr): self.sock.bind(addr)
    def listen(self, n): self.sock.listen(n)
    def accept(self):
        newconn = ChrSocket()
        newconn.sock, addr = self.sock.accept()
        return newconn, addr
    def send(self, msg):
        '''send data string'''
        totalsent=0; nsent=0
        msg+=self.chrend
        while totalsent<len(msg):
            sent=self.sock.send(msg[totalsent:])
            if sent == 0: raise RuntimeError('socket connection broken')
            totalsent += sent
            nsent +=1
        self.nsent=nsent
    def recv(self):
        '''returns a string representing the data received'''
        msg = ''; nrecv = 0
        msg = self.sock.recv(self.bufsize)
        if msg == '': raise RuntimeError('socket connection broken')
        nrecv +=1
        while msg[-1]!=self.chrend:
            chunk = self.sock.recv(self.bufsize)
            if chunk == '': raise RuntimeError('socket connection broken')
            msg += chunk
            nrecv +=1
        self.nrecv=nrecv
        return msg[:-1]
    
            
