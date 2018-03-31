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

# Takes in the requests and loops throught them. It takes them one by one to see if it falls under connect, get, or quit
# once there it will do the appropriate checks.
requestDict = {}
for request in sys.stdin:
    sys.stdout.write(request)
    splitRequest = request.split(" ",1)

    if splitRequest[0].lower().rstrip("\n")  == "connect":  # needs work
        serverHost, serverPort, serverHostError ,serverPortError = checkConnect(splitRequest[1:])
        if serverHostError:
            print("ERROR -- server-host") 
        elif serverPortError:
            print("ERROR -- server-port")       
        else:   
            if "connect" in requestDict:
                del requestDict["connect"]
            requestDict["connect"] = 8000
            print("CONNECT accepted for FTP server at host "+serverHost+" and port "+serverPort)
            sys.stdout.write("USER anonymous\r\n")
            sys.stdout.write("PASS guest@\r\n")
            sys.stdout.write("SYST\r\n")
            sys.stdout.write("TYPE I\r\n")


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
            hortPort = my_ip+","+portNumber
            print("GET accepted for "+pathname)
            sys.stdout.write("PORT "+hortPort+"\r\n") 
            sys.stdout.write("RETR "+pathname+"\r\n")
            requestDict["connect"] = int(requestDict.get("connect")) + 1


    elif splitRequest[0].lower().rstrip("\n")  == "quit":
        errorConnect = isErrorConnect(requestDict, "quit")
        if len(splitRequest) > 1:
            print("ERROR -- request")      # not sure
        elif errorConnect:
            print("ERROR -- expecting CONNECT")
        else:
            requestDict = {}
            print("QUIT accepted, terminating FTP client")
            sys.stdout.write("QUIT\r\n")


    else:
        print("ERROR -- request")
