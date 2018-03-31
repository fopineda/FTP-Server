import sys
import shutil
import os
import string
import socket


# Felipe Osiel Pineda
# 730132665


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


# Replies are loop through and each is checked for <reply-code>, reply-text, or CRLF errors. Those that are valid will
# output a specified message
for reply in sys.stdin:
    sys.stdout.write(reply)
    splitReply = reply.split(" ",1)
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