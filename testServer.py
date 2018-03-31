# test server

import socket

s = socket.socket()
print ("Server socket successfully created!")

port = 12345
s.bind(('',port))
print("Server socket binded to "+ str(port))
s.listen(5)
print("Server socket is listening...")

# At this point the server is just listening waiting for a client to connect.

while True:
    c, addr = s.accept()
    print("received connection from "+str(addr)) ## addr is tuple: (address, port)
    c.send('Thank you for connecting!\n'.encode())
    c.close()


#First of all we import socket which is necessary.

#Then we made a socket object and reserved a port on our pc.

#After that we binded our server to the specified port. 
# Passing an empty string means that the server can listen to incoming connections from other computers as well. 
# If we would have passed 127.0.0.1 then it would have listened to only those calls made within the local computer.

#After that we put the server into listen mode.5 here means that 5 connections are kept waiting 
# if the server is busy and if a 6th socket trys to connect then the connection is refused.

#At last we make a while loop and start to accept all incoming connections and close those connections 
# after a thank you message to all connected sockets.


# To test:
#       Bring up two terminals
#       First terminal run this file
#       Second terminal type telnet localhost 12345 and click enter