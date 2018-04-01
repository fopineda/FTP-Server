import sys
import shutil
import os
import string
import socket


# Felipe Osiel Pineda
# 730132665

def checkConnect(request):
    # Function split the serverhost and serverport and checks the individually.
    alphabetList = list(string.ascii_lowercase)
    alphabetList.append(".")
    digitList = list(range(0,10))
    serverHost = ""
    serverPort = ""
    serverHostError = False
    serverPortError = False
    serverPortNotInRange = False
    serverPortNotDigits = False
    if len(request) == 1:
        request = request[0].lstrip(" ").split(" ",1)  #['classroom.cs.unc.edu', '9000\n']
        if len(request) == 2:
            serverHost = request[0].lstrip(" ")
            serverPort = request[1].lstrip(" ").rstrip("\n")
            if serverHost[0] == "." or serverHost[0] in digitList:   # to check if the server hosts starts with a period
                serverHostError = True
            for char in serverHost.lower():
                if char not in digitList and char not in alphabetList:
                    serverHostError = True
                    break
            if not 0 <= int(serverPort) <= 65535:
                serverPortNotInRange = True
            try: 
                for num in serverPort:
                    if int(num) not in digitList:
                            serverPortNotDigits = True
            except Exception as err:
                serverPortNotDigits = True
            if serverPortNotInRange == True or serverPortNotDigits == True:
                serverPortError = True
        else:
            serverHostError = True
    else:
        serverHostError = True
    return serverHost, serverPort, serverHostError, serverPortError

def checkGet(request):
    # Function checks the request to see if the the pathname is all ASCII characters.
    pathnameError = False
    pathname = ""
    foundLetter = False
    if len(request) == 1:
        request[0] = request[0].lstrip(" ")
        if len(request) == 1:
            for letter in request[0]:
                if ord(letter) != 32 and ord(letter) != 10: # checks if there is a letter present, pathnames can't be all spaces
                    foundLetter = True
                if ord(letter) > 127:
                    pathnameError = True
                    break
        else:
            pathnameError = True
    else:
        pathnameError = True
    if foundLetter == False:
        pathnameError = True
    if pathnameError == False:
        pathname = request[0].rstrip("\n") # strips newlines because the prints in the tests adds them automatically
    return pathnameError, pathname

def isErrorConnect(rDict, request):  
    # For any valid user request that appears before the first CONNECT request, print out the
    # error message “ERROR -- expecting CONNECT”.
    errorConnect = False
    requestList = ["get", "quit"]
    if request in requestList and "connect" not in rDict:
        errorConnect = True
    return errorConnect

### FTPclient2.py functions
def checkCode(code):
    # Function is given the code part of reply and parses it to see if it is indeed a value between 100 and 599 and
    # also if all the characters in the code are digits
    digitList = list(range(0,10))
    codeNotDigits = False
    codeNotInRange = False
    codeError = False
    try:
        if not 100 <= int(code) <= 599:
            codeNotInRange = True
    except Exception as err:
        codeNotInRange = True
    try: 
        for num in code:
            if int(num) not in digitList:
                codeNotDigits = True
    except Exception as err:
        codeNotDigits = True
    if codeNotInRange == True or codeNotDigits == True:
        codeError = True
    return code, codeError

def checkreplytext(text):
    # Function is given the text part of the reply to see if the characters inside are indeed any of the 128 ASCII
    # characters except for <CR> and <LF>
    replyTextError = False
    crlfError = False
    foundLetter = False
    for letter in text:
        if ord(letter) != 32 and ord(letter) != 13 and ord(letter) != 10: # checks if username/password contains ascii letter
            foundLetter = True
        if ord(letter) > 127: # checks username to see if it fits ASCII standard
            replyTextError = True
            break
    if foundLetter ==  False:
        replyTextError = True
    if "\r\n" not in text:
       crlfError = True 
    return text, replyTextError, crlfError

def receiveReplies(str):
    splitReply = str.split(" ",1)
    if len(splitReply) > 1:
        code, codeError = checkCode(splitReply[0])
        text, replyTextError, crlfError = checkreplytext(splitReply[1])
        if codeError:
            print("ERROR -- reply-code")
        elif replyTextError:
            print("ERROR -- reply-text")
        elif crlfError:
            print("ERROR -- <CRLF>")
        else:
            print("FTP reply "+code+" accepted.  Text is : "+text.rstrip("\r\n"))
    else:
        print("ERROR -- reply-code")

# Takes in the requests and loops throught them. It takes them one by one to see if it falls under connect, get, or quit
# once there it will do the appropriate checks.
requestDict = {}
for request in sys.stdin:
    sys.stdout.write(request)
    splitRequest = request.split(" ",1)

    if splitRequest[0].lower().rstrip("\n")  == "connect":  
        serverHost, serverPort, serverHostError ,serverPortError = checkConnect(splitRequest[1:])
        if serverHostError:
            print("ERROR -- server-host") 
        elif serverPortError:
            print("ERROR -- server-port")       
        else:   
            if "connect" in requestDict:
                del requestDict["connect"]
            requestDict["connect"] = sys.argv[1] # records port number provided in command line
            try:
                # create control socket (FTP-control connection)
                # Ex: CONNECT classroom.cs.unc.edu 9000
                control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                control_socket.connect((serverHost, serverPort))
            except:
                sys.stdout.write("CONNECT failed\r\n")
                break
            print("CONNECT accepted for FTP server at host "+serverHost+" and port "+serverPort)
            received_data = control_socket.recv(1024)
            receiveReplies(received_data.decode())
            sys.stdout.write("USER anonymous\r\n")
            control_socket.send("USER anonymous\r\n".encode())
            received_data = control_socket.recv(1024)
            receiveReplies(received_data.decode())
            sys.stdout.write("PASS guest@\r\n")
            control_socket.send("PASS guest@\r\n".encode())
            received_data = control_socket.recv(1024)
            receiveReplies(received_data.decode())
            sys.stdout.write("SYST\r\n")
            control_socket.send("SYST\r\n".encode())
            received_data = control_socket.recv(1024)
            receiveReplies(received_data.decode())
            sys.stdout.write("TYPE I\r\n")
            control_socket.send("TYPE I\r\n".encode())
            received_data = control_socket.recv(1024)
            receiveReplies(received_data.decode())

    elif splitRequest[0].lower().rstrip("\n")  == "get":
        errorConnect = isErrorConnect(requestDict, "get")
        pathnameError, pathname  = checkGet(splitRequest[1:])
        if pathnameError:
            print("ERROR -- pathname")
        elif errorConnect:
            print("ERROR -- expecting CONNECT")
        else:
            requestDict["get"] = pathname
            my_ip = socket.gethostbyname(socket.gethostname()).replace(".",",")
            portNumber = str(int(requestDict.get("connect"))//256)+","+str(int(requestDict.get("connect"))%256)
            hostPort = my_ip+","+portNumber
            print("GET accepted for "+pathname)
            try:
                # create welcome socket (FTP-data connection)
                data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_socket.bind((socket.gethostbyname(socket.gethostname()), requestDict.get("connect"))) #client hostname, command line arguement port number
                data_socket.listen(1)
            except:
                sys.stdout.write("GET failed, FTP-data port not allocated\r\n")
                break                  #?
            
            sys.stdout.write("PORT "+hostPort+"\r\n")
            control_socket.send("PORT "+hostPort+"\r\n".encode())
            received_data = control_socket.recv(1024)
            receiveReplies(received_data.decode())

            sys.stdout.write("RETR "+pathname+"\r\n")
            control_socket.send("RETR "+pathname+"\r\n".encode())
            received_data = control_socket.recv(1024)
            receiveReplies(received_data.decode())

            while True:
                connection_socket, addr = data_socket.accept()
                data = connection_socket.recv(1024)
                connection_socket.close()

            # start here
            requestDict["connect"] = int(requestDict.get("connect")) + 1


    elif splitRequest[0].lower().rstrip("\n")  == "quit":
        errorConnect = isErrorConnect(requestDict, "quit")
        if len(splitRequest) > 1:
            print("ERROR -- request")      
        elif errorConnect:
            print("ERROR -- expecting CONNECT")
        else:
            requestDict = {}
            print("QUIT accepted, terminating FTP client")
            sys.stdout.write("QUIT\r\n")


    else:
        print("ERROR -- request")
