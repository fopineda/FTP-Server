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
    int_digitList = list(range(0,10))
    str_digitList = [str(r) for r in int_digitList]
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
            if serverHost[0] == "." or serverHost[0] in str_digitList:   # to check if the server hosts starts with a period
                serverHostError = True
            for char in serverHost.lower():
                if char not in str_digitList and char not in alphabetList:
                    print(char)
                    serverHostError = True
                    break
            if not 0 <= int(serverPort) <= 65535:
                serverPortNotInRange = True
            try: 
                for num in serverPort:
                    if int(num) not in int_digitList:
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
    errorConnect = False
    requestList = ["get", "quit"]
    if request in requestList and "connect" not in rDict:
        errorConnect = True
    return errorConnect

### FTPclient2.py functions
def checkCode(code):
    # Function is given the code part of reply and parses it to see if it is indeed a value between 100 and 599 and
    # also if all the characters in the code are digits
    int_digitList = list(range(0,10))
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
            if int(num) not in int_digitList:
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
            print("FTP reply "+code+" accepted. Text is: "+text.rstrip("\r\n"))
    else:
        print("ERROR -- reply-code")


def assure_path_exists(path):
    # used to check if a certain path (directory/file) exists. If not then create it
    if not os.path.exists(path):
        os.makedirs(path)

retrCount = 1
# Takes in the requests and loops throught them. It takes them one by one to see if it falls under connect, get, or quit
# once there it will do the appropriate checks.
requestDict = {}
# for request in sys.stdin:
#     sys.stdout.write(request)
while True:
    request = input()
    request = request+"\n"
    sys.stdout.write(request)
    splitRequest = request.split(" ",1)
    if splitRequest[0].lower().rstrip("\n")  == "connect":  
        serverHost, serverPort, serverHostError ,serverPortError = checkConnect(splitRequest[1:])
        if serverHostError:
            print("ERROR -- server-host") 
        elif serverPortError:
            print("ERROR -- server-port")       
        else:
            control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
            try:
                # create control socket (FTP-control connection)
                # Ex: CONNECT classroom.cs.unc.edu 9000
                print("CONNECT accepted for FTP server at host "+serverHost+" and port "+serverPort)
                control_socket.connect((serverHost, int(serverPort)))
            except:
                print("CONNECT failed")
                continue
            if "connect" in requestDict:
                del requestDict["connect"]
            requestDict["connect"] = sys.argv[1] # records port number provided in command line assoc with connect command
            
            received_data = control_socket.recv(1024).decode()
            receiveReplies(received_data)

            # USER-PASS-SYST-TYPE being sent after CONNECT command
            sys.stdout.write("USER anonymous\r\n")
            control_socket.send("USER anonymous\r\n".encode())
            received_data = control_socket.recv(1024).decode()
            receiveReplies(received_data)

            sys.stdout.write("PASS guest@\r\n")
            control_socket.send("PASS guest@\r\n".encode())
            received_data = control_socket.recv(1024).decode()
            receiveReplies(received_data)

            sys.stdout.write("SYST\r\n")
            control_socket.send("SYST\r\n".encode())
            received_data = control_socket.recv(1024).decode()
            receiveReplies(received_data)

            sys.stdout.write("TYPE I\r\n")
            control_socket.send("TYPE I\r\n".encode())
            received_data = control_socket.recv(1024).decode()
            receiveReplies(received_data)

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
                data_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # #caled before bind to allow reusing the same port.
                data_client_socket.bind((socket.gethostbyname(socket.gethostname()), int(requestDict.get("connect")))) #client hostname, command line arguement port number
                data_client_socket.listen(1)

            except:
                print("GET failed, FTP-data port not allocated")
                continue
            
            sys.stdout.write("PORT "+hostPort+"\r\n")
            control_socket.send(str("PORT "+hostPort+"\r\n").encode())
            received_data = control_socket.recv(1024).decode()
            receiveReplies(received_data)
            requestDict["connect"] = int(requestDict.get("connect")) + 1

            sys.stdout.write("RETR "+pathname+"\r\n")
            control_socket.send(str("RETR "+pathname+"\r\n").encode())
            received_data = control_socket.recv(1024).decode()
            receiveReplies(received_data)


            if received_data[0:3] == "150":
                received_data = control_socket.recv(1024).decode()
                receiveReplies(received_data)
                assure_path_exists("./retr_files")  # Checks if retr_files exits, if not create, otherwise do nothing
                connection_socket, addr = data_client_socket.accept()
                str_retrCount = str(retrCount)
                if 10 <= retrCount < 100:
                    str_retrCount = "0"+ str_retrCount
                else:
                    str_retrCount = str(retrCount)
                merchandise_client = open("retr_files/file"+str_retrCount, "wb+") ## HelloWorld.java not being copied correctly (client)
                merchandise_client_chunk = connection_socket.recv(1024)
                while merchandise_client_chunk:
                    merchandise_client.write(merchandise_client_chunk)
                    merchandise_client_chunk = connection_socket.recv(1024)
                merchandise_client.close() 
                connection_socket.close()
                retrCount += 1
            else:
                continue

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
            control_socket.send("QUIT\r\n".encode())
            received_data = control_socket.recv(1024).decode()
            receiveReplies(received_data)
            control_socket.close()

    else:
        print("ERROR -- request")
