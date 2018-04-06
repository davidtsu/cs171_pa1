import socket
import sys
import threading
import time
import datetime
import os.path
from time import sleep
from socket import SHUT_RDWR
from Crypto.Cipher import AES
import hashlib

def myEncr(message):
    #print(message)
    newmsg = message + "#@@#" + calculateHashVal(message) #for hashing
    print(newmsg)
    obj = AES.new('3245456475864749', AES.MODE_CBC, '8685635234145573')
    length = 16 - (len(newmsg) % 16)
    newmsg += chr(32)*length
    ciphertext = obj.encrypt(newmsg)
    return ciphertext

def myDecr(message):
    obj2 = AES.new('3245456475864749', AES.MODE_CBC, '8685635234145573')
    decr = obj2.decrypt(message)
    decr = decr.rstrip()
    return decr

def calculateHashVal(message):
    newmsg = message + 'tacotruck'
    #print(newmsg)
    h = hashlib.sha256()
    h.update(newmsg)
    return h.digest()

def deHash(message):
    startPounds = message.find("#@@#")
    endPounds = startPounds + 4
    hashVal = message[endPounds:]
    msgNoHash = message[:startPounds]
    #print(msgNoHash)
    #print(hashVal)
    return msgNoHash, hashVal

# setting server name and server port number
serverName = sys.argv[1]   # '169.231.80.116'
serverPort = int(sys.argv[2])               #12000
nickname = raw_input("Enter Username: ")     # username to be used in chat room

# opening socket and sending user name to server
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
nickname1 = myEncr(nickname)
clientSocket.send(nickname1)
#print ("Client message: %s " %message) 											# message sent

ignoreList = []                 # list of users this client has decided to block
startTime = datetime.datetime.now()
endTime = datetime.datetime.now()
quit = 0


def PrintHelpMenu():
    print("\n************** HELP MENU ******************")
    print("\nCOMMANDS ALLOWED IN THIS CHAT ROOM")
    print("\n\n/msg nickname message \n msg command is used for private messaging.\n nickname parameter is the user who you are private messaging \n message is the private message you wish to send user. ")
    print("\n \n /ignore username \n ignore command is used to block private and public messages sent by a user")
    print("\n\n /ping username \n ping command is prints the RTT for messages sent to the specified user. \n Only ping one user at a time")
    print("\n\n /help \n help command prints valid commands and intended purpuse")
    print("\n\n /quit \n quit command removes user from chat room")
    print("\n\n /sendFile \n command sends files to another person in chat room \n syntax:    /sendFile reciever filename.filetype")
    print("\n\n ************** END OF HELP MENU ******************** \n")


def SendFile(username, filename):
    sourceFile  = open(str(filename), 'rb');
    header = str("\dataFile&@#" + username + "&@#"+ filename +"&@#")
    headLen = len(header)
    readSize = 800 - headLen
    buff = sourceFile.read(readSize);
    #print(len(buff))
    while True:
        if not buff: break;
        #header = str("\dataFile&@#" + username + "&@#"+ filename +"&@#") #+ buff)
        #print(len(buff))
        message = str(header) + str(buff)
        message = myEncr(message)
        clientSocket.send(message)
        sleep(1)
        buff = sourceFile.read(readSize)
    sourceFile.close()
    message = ("finished\n")
    message = myEncr(message)
    clientSocket.send(message)

def RecieveFile(message):
    #parse
    parseMessage = message.split("&@#")
    #open file
    print "writing to file"
    destinationFile = open(str(parseMessage[2]), 'ab+');
    #write
    dataList = parseMessage[3:len(parseMessage)]
    data = " ".join(dataList)
    destinationFile.write(str(data));
    #close
    destinationFile.close()



def SendMessage():
        while(1):
                inMessage = raw_input()
                #see if a command is being sent
                parsedMessage = inMessage.split(" ")
                if parsedMessage[0] == "/help":
                    PrintHelpMenu()
                elif parsedMessage[0] == "/ignore" and len(parsedMessage) == 2:
                    ignoreList.append(parsedMessage[1])
                elif parsedMessage[0] == "/unignore" and len(parsedMessage) == 2:
                    ignoreList.remove(parsedMessage[1])
                elif parsedMessage[0] == "/ping"   and len(parsedMessage) == 2 :
                    startTime = datetime.datetime.now()
                    inMessage = myEncr(inMessage)
                    clientSocket.send(inMessage)
                elif parsedMessage[0] == "/sendFile"   and len(parsedMessage) == 3 :
                    if os.path.isfile(str(parsedMessage[2])) :
                        inMessage = myEncr(inMessage)
                        clientSocket.send(inMessage)
                        SendFile(parsedMessage[1], parsedMessage[2])
                    else:
                        print "\n file does not exist in program directory. \n Place file in program directory before sending"
                elif  parsedMessage[0] == "/quit":
                    inMessage = myEncr(inMessage)
                    clientSocket.send(inMessage)
                else:
                    inMessage = myEncr(inMessage)
                    #print(inMessage)
                    clientSocket.send(inMessage)
                    


threads = []
t = threading.Thread(target=SendMessage)
threads.append(t)
t.start()
''' t1 = threading.Thread(target=recieveMessage)
threads.append(t)
t.start()
'''
while  quit == 0:
    # handling recieved messages
    modifiedMessage = clientSocket.recv(1024)                                        # recieving message from server
    modifiedMessage = str(modifiedMessage)
    modifiedMessage = myDecr(modifiedMessage)
    modifiedMessage, newHash = deHash(modifiedMessage)
    originalHash = calculateHashVal(modifiedMessage)
    if newHash != originalHash:
        print("This message was modified between sender and receiver!")
    if len(modifiedMessage) == 0 :
        quit = 1
    
    if modifiedMessage[0:2] == "\d":
        print "recieving file"
        RecieveFile(modifiedMessage)
    else:
        parsedMessage = modifiedMessage.split(" ")
        if parsedMessage[0] in ignoreList:
            continue
        elif len(parsedMessage) > 4 and parsedMessage[2] == "/msg":
            if parsedMessage[3] == nickname:
                printList = parsedMessage[0:2] + parsedMessage[4: len(parsedMessage)]
                printMes = " ".join(printList)
                print("private message from %s\n" %printMes)
        elif len(parsedMessage) > 3 and parsedMessage[2] == "/ping":
            if parsedMessage[3] == nickname:
                print("%s pinged you \n" %(parsedMessage[0]))
                message = "/pAnswer " + parsedMessage[0] + " " + nickname
                message = myEncr(message)
                clientSocket.send(message)
        elif len(parsedMessage) > 4 and parsedMessage[2] == "/sendFile":
            if parsedMessage[3] == nickname:
                print("recieving file")
                #destinationFile = open(str(parsedMessage[2]), 'w');
                #destinationFile.truncate()
                #destinationFile.close()
        elif len(parsedMessage) > 4 and parsedMessage[2] == "/pAnswer":
            if parsedMessage[3] == nickname:
                endTime = datetime.datetime.now()
                RTT = endTime - startTime
                RTT = float(RTT.microseconds)/1000
                print("RTT for %s is %i ms" %(parsedMessage[4], RTT))
        else:
            print("%s\n" %modifiedMessage)

print("quit chat \n")
clientSocket.shutdown(SHUT_RDWR)
clientSocket.close()
sys.exit(0)


