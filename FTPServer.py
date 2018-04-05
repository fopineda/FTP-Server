import sys
import shutil
import os
from socket import *
import socket

# Felipe Osiel Pineda
# 730132665

def checkUserOrPass(parameter):
    # Tests both user and pass commands. It creates three boolean values that are initally false and if an error is found
    # then the value is changed to true. Once the the testing is done, it returns to the caller.
    # parameter in this function is the command split by the first occurence of a space.
    parameterError = False
    crlfError = False
    foundLetter = False
    for letter in parameter[1]:
        if ord(letter) != 32 and ord(letter) != 13 and ord(letter) != 10: # checks if username/password contains ascii letter
            foundLetter = True
        if ord(letter) > 127: # checks username to see if it fits ASCII standard
            parameterError = True
            break
    if foundLetter == False:
        parameterError = True
    if "\r\n" not in parameter[1]:
       crlfError = True 
    return parameterError, crlfError   

def checkType(parameter):
    # Tests the type command. It creates two boolean values that are intially false and correspond to an error.
    # Checks if the type-code equals "A" or "I". After that it checks to see if the <CRLF> is present. Returns boolean error values
    # to caller.
    # parameter in this function is initially a the command split by the first occurence of a space but then called on second
    # object of list and stripped of leading whitespaces.
    typeCodeError = False
    crlfError = False
    parameter = parameter[1].lstrip(" ")
    typeChar = parameter[0]
    if parameter[0] != "A" and parameter[0] != "I":
        typeCodeError = True
    if len(parameter[1:]) != 2 or parameter[-2:] != "\r\n":
        crlfError = True
    return typeCodeError, crlfError, typeChar

def checkNoParams(parameter):
    # Test the no parameters command (syst, noop, and quit). These commands can only have two errors (command error and CRLF error).
    # The caller has already checked for the command error, in this function is checks if the <CRLF> is present and if it's at 
    # the correct location. Returns boolean value to caller. 
    # parameter in this function is the orginal command string without split.
    crlfError = False
    if len(parameter[4:]) == 2:
        if len(parameter.split(" ",1)) > 1 or parameter[4] != "\r" or parameter[5] != "\n":
            crlfError = True
    else:
        crlfError = True
    return crlfError

def checkPort(parameter):
    # Passing the orginal command, will be spliting it twice depending on the type of test doing
    parameterError = False
    crlfError = False
    if len(parameter.split(" ",1)) == 2:
        if parameter.split(" ",1)[1] != "\r\n":
            hostAddressPortNumWithoutCRLF = parameter.split()[1].lstrip(" ").split(",")
            hostAddressPortNumWithCRLF = parameter.split(" ",1)[1].lstrip(" ").split(",")
            if len(hostAddressPortNumWithoutCRLF) != 6 or len(parameter.split(" ", 1)) > 2:
                parameterError = True
            for bit in hostAddressPortNumWithoutCRLF:
                if bit.isdigit():
                    if not 0 <= int(bit) <= 255:
                        parameterError = True
                        break
                else:
                    parameterError = True

            if "\r\n" not in hostAddressPortNumWithCRLF[-1]:
                crlfError = True
        else:
            parameterError = True
    else:
        parameterError = True

    return parameterError, crlfError

def checkRetr(parameter):
    parameterError = False
    crlfError = False
    foundCRLF = False
    if len(parameter) == 2:
        if parameter[1] != "\r\n":
            parameter = parameter[1].lstrip(" ")
            if parameter[0] == "/":
                parameter = parameter[1:]
            for letter in parameter[:-2]:
                if ord(letter) == 13 or ord(letter) == 10:
                    foundCRLF = True
                if ord(letter) > 127 or foundCRLF == True: # checks parameter to see if it fits ASCII standard
                    parameterError = True
                    break
        else:
            parameterError = True
    else:
        parameterError = True
    if parameter[-2:] != "\r\n":
        crlfError = True
    return parameterError, crlfError


def code530(paramlist, myCommand):
    # Checks for error 530 Not logged in. 
    is530 = False
    incorrectCommands = ["port", "retr", "type", "syst", "noop"]
    if myCommand in incorrectCommands and "user" not in paramlist and "pass" not in paramlist:
        is530 = True
    return is530

def code503(paramlist, myCommand):
    # Checks for 503 Bad sequence of commands. 
    is503 = False
    if len(paramlist) != 0:   
        correctCommands = ["user", "pass", "quit"]
        if paramlist[-1] == "user" and myCommand not in correctCommands:
            is503 = True
        if myCommand == "pass" and paramlist[-1] != "user":
            is503 = True
        if myCommand == "retr" and "port" not in paramlist:
            is503 = True
    return is503

def assure_path_exists(path):
    # used to check if a certain path (directory/file) exists. If not then create it
    if not os.path.exists(path):
        os.makedirs(path)

def get_absolute_file_path(first_character_stripped_filepath):
    import os
    current_working_directory = os.getcwd()
    absolute_file_path = current_working_directory + os.sep + first_character_stripped_filepath
    return absolute_file_path
    
# Splits the commands given into lines and then each line is split into the first occurence of a whitespace. 
# It then checks to see in which command it will fall under which. If it doesn't fall under any command, then it will be a command error.
# Once it found the it's correct command, it will call the check function to see if has any errors. The functions (functions above)
# will return booelan values that will be examined to see if falls in a specific error.

FTPList= []
retrCount = 0
client_sent_portNumber = 0
client_sent_hostAddress = 0
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # #caled before bind to allow reusing the same port.
server_socket.bind(("", int(sys.argv[1])))
server_socket.listen(1)    # allow only one connection at a time
while True: # to keep the server always running and accept new connections once the inside loop is broken
    connect_socket, address = server_socket.accept() # waiting???
    sys.stdout.write("220 COMP 431 FTP server ready.\r\n")
    connect_socket.send("220 COMP 431 FTP server ready.\r\n".encode())
    while True: # to handle the client input
        client_command = connect_socket.recv(1024) # commands from client
        if not client_command: #check whether the client side has closed the FTP-control connection
            connect_socket.close()
            break
        client_command = client_command.decode()
        sys.stdout.write(client_command)
        splitCommand = client_command.split(" ",1)


        if splitCommand[0].lower()  == "user":
            parameterError, crlfError = checkUserOrPass(splitCommand)
            if parameterError == True or crlfError == True:
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                connect_socket.send("501 Syntax error in parameter.\r\n".encode())
            elif code530(FTPList, "user"):
                sys.stdout.write("530 Not logged in.\r\n")
                connect_socket.send("530 Not logged in.\r\n".encode())
            elif code503(FTPList, "user"):
                sys.stdout.write("503 Bad sequence of commands.\r\n")  
                connect_socket.send("503 Bad sequence of commands.\r\n".encode()) 
            else:
                FTPList.append("user")
                sys.stdout.write("331 Guest access OK, send password.\r\n")  
                connect_socket.send("331 Guest access OK, send password.\r\n".encode())


        elif splitCommand[0].lower()  == "pass":
            parameterError, crlfError = checkUserOrPass(splitCommand)
            if parameterError == True or crlfError == True:
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                connect_socket.send("501 Syntax error in parameter.\r\n".encode())
            elif code530(FTPList, "pass"):
                sys.stdout.write("530 Not logged in.\r\n")
                connect_socket.send("530 Not logged in.\r\n".encode())
            elif code503(FTPList, "pass"):
                sys.stdout.write("503 Bad sequence of commands.\r\n")
                connect_socket.send("503 Bad sequence of commands.\r\n".encode())    
            else:
                FTPList.append("pass")
                sys.stdout.write("230 Guest login OK.\r\n") 
                connect_socket.send("230 Guest login OK.\r\n".encode())   


        elif splitCommand[0].lower()  == "type":
            typeCodeError, crlfError, typeChar = checkType(splitCommand)
            if typeCodeError == True or crlfError == True:
                sys.stdout.write("501 Syntax error in parameter.\r\n") 
                connect_socket.send("501 Syntax error in parameter.\r\n".encode())  
            elif code530(FTPList, "type"):
                sys.stdout.write("530 Not logged in.\r\n")
                connect_socket.send("530 Not logged in.\r\n".encode())
            elif code503(FTPList, "type"):
                sys.stdout.write("503 Bad sequence of commands.\r\n")
                connect_socket.send("503 Bad sequence of commands.\r\n".encode())
            else:
                if typeChar == "A":
                    sys.stdout.write("200 Type set to A.\r\n") 
                    connect_socket.send("200 Type set to A.\r\n".encode())  
                    FTPList.append("type a")
                elif typeChar == "I":
                    sys.stdout.write("200 Type set to I.\r\n") 
                    connect_socket.send("200 Type set to I.\r\n".encode())  
                    FTPList.append("type i")
                else:
                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                    connect_socket.send("01 Syntax error in parameter.\r\n".encode())    


        elif client_command[0:4].lower()  == "syst":
            crlfError = checkNoParams(client_command)
            if crlfError:
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                connect_socket.send("501 Syntax error in parameter.\r\n".encode())   
            elif code530(FTPList, "syst"):
                sys.stdout.write("530 Not logged in.\r\n")
                connect_socket.send("530 Not logged in.\r\n".encode())
            elif code503(FTPList, "syst"):
                sys.stdout.write("503 Bad sequence of commands.\r\n")
                connect_socket.send("503 Bad sequence of commands.\r\n".encode())
            else:
                sys.stdout.write("215 UNIX Type: L8.\r\n") 
                connect_socket.send("215 UNIX Type: L8.\r\n".encode())   
                FTPList.append("syst")


        elif client_command[0:4].lower()  == "noop":
            crlfError = checkNoParams(client_command)
            if crlfError:
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                connect_socket.send("501 Syntax error in parameter.\r\n".encode())   
            elif code530(FTPList, "noop"):
                sys.stdout.write("530 Not logged in.\r\n")
                connect_socket.send("530 Not logged in.\r\n".encode())
            elif code503(FTPList, "noop"):
                sys.stdout.write("503 Bad sequence of commands.\r\n")
                connect_socket.send("503 Bad sequence of commands.\r\n".encode())
            else:
                sys.stdout.write("200 Command OK.\r\n")
                connect_socket.send("200 Command OK.\r\n".encode())
                FTPList.append("noop")


        elif client_command[0:4].lower()  == "quit":
            crlfError = checkNoParams(client_command)
            if crlfError:
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                connect_socket.send("501 Syntax error in parameter.\r\n".encode())   
            else:
                FTPList = []  ## Clearing the list
                sys.stdout.write("221 Goodbye.\r\n")  
                connect_socket.send("221 Goodbye.\r\n".encode())
                # connect_socket.close()  
                break

        elif splitCommand[0].lower()  == "port":
            parameterError, crlfError = checkPort(client_command)
            if parameterError == True or crlfError == True:
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                connect_socket.send("501 Syntax error in parameter.\r\n".encode())   
            elif code530(FTPList, "port"):
                sys.stdout.write("530 Not logged in.\r\n")
                connect_socket.send("530 Not logged in.\r\n".encode())
            elif code503(FTPList, "port"):
                sys.stdout.write("503 Bad sequence of commands.\r\n")
                connect_socket.send("503 Bad sequence of commands.\r\n".encode())
            else:
                ## Assuming the port command is valid all the way (including parameter with six numbers and 5 commas)
                portParameter = client_command.split()[1].lstrip(" ").split(",") 
                hostAddress = ".".join(portParameter[0:-2])
                portNumber = (int(portParameter[-2]) * 256) + int(portParameter[-1])
                client_sent_portNumber = portNumber
                client_sent_hostAddress = hostAddress
                sys.stdout.write("200 Port command successful ("+hostAddress+","+str(portNumber)+").\r\n")
                connect_socket.send(str("200 Port command successful ("+hostAddress+","+str(portNumber)+").\r\n").encode())
                if "port" in FTPList:
                    FTPList.remove("port")  
                FTPList.append("port")


        elif splitCommand[0].lower()  == "retr":
            parameterError, crlfError = checkRetr(splitCommand)
            if parameterError == True or crlfError == True:
                sys.stdout.write("501 Syntax error in parameter.\r\n")
                connect_socket.send("501 Syntax error in parameter.\r\n".encode())    
            elif code530(FTPList, "retr"):
                sys.stdout.write("530 Not logged in.\r\n")
                connect_socket.send("530 Not logged in.\r\n".encode())
            elif code503(FTPList, "retr"):
                sys.stdout.write("503 Bad sequence of commands.\r\n")
                connect_socket.send("503 Bad sequence of commands.\r\n".encode())
            else:
                assure_path_exists("./retr_files")  # Checks if retr_files exits, if not create, otherwise do nothing
                path = splitCommand[1].rstrip("\r\n")
                path = path.lstrip(" ")
                if ord(path[0]) in {92,47} and len(path) > 1:
                    path = path[1:]
                newPath = get_absolute_file_path(path)
                if os.path.exists(newPath): 
                    # connect_socket.send("True") # send a True to the client for not finding a file
                    retrCount = retrCount + 1
                    sys.stdout.write("150 File status okay.\r\n")
                    connect_socket.send("150 File status okay.\r\n".encode())
                    #socket connecting to client data (welcoming) socket for file transfer
                    try:
                        data_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
                        data_server_socket.connect(client_sent_hostAddress, client_sent_portNumber)
                    except:
                        sys.stdout.write("425 Can not open data connection.\r\n")
                        connect_socket.send("425 Can not open data connection.\r\n".encode())
                        continue

                    # reading bytes and sending them
                    merchandise_server = open("./"+newPath, "r") #r for read, b for binary
                    merchandise_server_chunk = merchandise_server.read(1024)
                    while (merchandise_server_chunk):
                        data_server_socket.send(merchandise_server_chunk.encode())
                        merchandise_server_chunk = merchandise_server.read(1024)
                    data_server_socket.close()
                    merchandise_server.close()
                    sys.stdout.write("250 Requested file action completed.\r\n")
                    connect_socket.send("250 Requested file action completed.\r\n".encode())
                    if "port" in FTPList:
                        FTPList.remove("port")
                else:
                    sys.stdout.write("550 File not found or access denied.\r\n")
                    connect_socket.send("550 File not found or access denied.\r\n".encode())
                    # connect_socket.send("False") # send a False to the client for not finding a file
        else:
            sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
            connect_socket.send("500 Syntax error, command unrecognized.\r\n".encode())



