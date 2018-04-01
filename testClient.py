#testClient

import socket


# Server is listening, now you as the client have to connect to it.
s = socket.socket()
port = 12345
s.connect(('127.0.0.1', port))
received_message = s.recv(1024)
# print(type(received_message)) # bytes
# print(type(received_message.decode()))
print(received_message.decode())
s.close()

#First of all we make a socket object.

#Then we connect to localhost on port 12345 (the port on which our server runs) and lastly we receive data 
# from the server (have to decode it) and close the connection.

#Now save this file as client.py and run it from the terminal after starting the server script.