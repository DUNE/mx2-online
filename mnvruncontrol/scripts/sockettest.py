"""
   sockettest.py:
   a simple program to send commands over a TCP socket and receive any
   response.  designed primarily for testing the dispatchers.
"""

import socket

def sockettest(address, request):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(address)
	s.send(request)
	s.shutdown(socket.SHUT_WR)
	
	datalen = -1
	response = ""
	while datalen != 0:
		data = s.recv(1024)
		datalen = len(data)
		response += data
	
	s.close()
	
	return response
