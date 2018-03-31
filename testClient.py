#testClient

import socket


# Server is listening, now you as the client have to connect.
s = socket.socket()
port = 12345
s.connect(('127.0.0.1', port))
print(s.recv(1024))
s.close()

#First of all we make a socket object.

#Then we connect to localhost on port 12345 (the port on which our server runs) and lastly we receive data 
# from the server and close the connection.

#Now save this file as client.py and run it from the terminal after starting the server script.