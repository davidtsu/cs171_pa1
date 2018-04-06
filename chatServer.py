# the basic socket code was copied from COMPUTER NETWORKING SIXTH EDITIONA Top-Down Approach
# by James F. KuroseUniversity of Massachusetts, AmherstKeith W. Ross Polytechnic Institute of NYU
import socket
import sys
import time
from time import sleep
import threading
from socket import SHUT_RDWR
from Crypto.Cipher import AES
import hashlib

def myEncr(message):
    newmsg = message + "#@@#" + calculateHashVal(message)
    obj = AES.new('3245456475864749', AES.MODE_CBC, '8685635234145573')
    length = 16 - (len(message) % 16)
    message += chr(32)*length
    ciphertext = obj.encrypt(message)
    return ciphertext

def myDecr(message):
    obj2 = AES.new('3245456475864749', AES.MODE_CBC, '8685635234145573')
    decr = obj2.decrypt(message)
    decr = decr.rstrip()
    return decr

def calculateHashVal(message):
    newmsg = message + 'tacotruck'
    h = hashlib.sha256()
    h.update(newmsg)
    return h.digest()

def deHash(message):
    startPds = message.find("#@@#")
    #print(startPds)
    endPds = startPds + 4
    #print(endPds)
    hashVal = message[endPds:]
    #print(hashVal)
    msgNoHash = message[:startPds]
    #print(msgNoHash)
    return msgNoHash, hashVal

def sendMessage(ReturnMessage, con):
    print("message to send before encyption: %s" %(ReturnMessage))
    ReturnMessage = myEncr(ReturnMessage)
    print("message to send after encyption: %s" %(ReturnMessage))
    for x in range(len(sockList)):
        sockList[x].send(ReturnMessage)



nickName = []
ipList = []
sockList = []
threads = []
i = 0
serverPort = int(sys.argv[1])                                                 # port server is listening on

                                               # port server is listening on

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)     # open a socket
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(('',serverPort))                                  # binding server to this port
serverSocket.listen(1)                                              # begin to listen on port
global closeSock

def ListenForMessage(con, nick):
    while(1):
        #print( "length of connection array %i \n" %len(sockList))
        message = con.recv(1024)                               # recieve message from client
        tempMessage = str(message)
        #print("recieved encryted messsage: %s \n"%(tempMessage))
        tempMessage = myDecr(str(tempMessage))
        tempMessage, randHashVal = deHash(tempMessage)
        #print("decrypted message: %s \n" %(tempMessage))
        if tempMessage[0:2] == "\d" :
            parseMessage = tempMessage.split("&@#")
            if parseMessage[1] in nickName:
                conIndex = nickName.index(parseMessage[1])
                tempMessage = myEncr(tempMessage)
                sockList[conIndex].send(tempMessage)
        
        else :
            parseMessage = tempMessage.split(" ")
            if parseMessage[0] == "/quit" :
                #remove connection
                sockList.remove(con)
                nickName.remove(nick)
                endmes = "bye"
                endmes = myEncr(endmes)
                con.send(endmes)
                sleep(1)
                con.shutdown(SHUT_RDWR)
                con.close()                                            # closing connection
                break
            else:
                tempMessage = nick + " : " + tempMessage
                #print("%s \n" %(tempMessage))
                sendMessage(tempMessage, con)

def newSocket():
    while (1):
        
        connectionSocket, addr = serverSocket.accept()                      # establish connect to client
        message = connectionSocket.recv(1024) # recieve message from client
        message = myDecr(message)
        #message = message.rstrip()
        message, hashVal = deHash(message)
        #print(message)
        nickName.append(message)
        tempMessage = str(message)
        #print("%s connected \n" %tempMessage)
        tempMessage = tempMessage + " connected"
        sockList.append(connectionSocket)
        sendMessage(tempMessage,connectionSocket)
        t = threading.Thread(target=ListenForMessage,args=(connectionSocket,str(message),))
        threads.append(t)
        t.start()

connectionSocket, addr = serverSocket.accept()                      # establish connect to client
message = connectionSocket.recv(1024)                               # recieve message from client
message = myDecr(message)
message, randHashVal = deHash(message)
nickName.append(message)
message = message.rstrip()
tempMessage = str(message)
#print("%s connected \n" %tempMessage)
tempMessage = tempMessage + " connected"
sockList.append(connectionSocket)
sendMessage(tempMessage,connectionSocket)
t = threading.Thread(target=ListenForMessage,args=(connectionSocket,str(message),))
threads.append(t)
t.start()

t = threading.Thread(target=newSocket)
threads.append(t)
t.start()
print "welcome to chat lab"
while (len(sockList) > 0):
    continue

print("closing socket")

serverSocket.close()
connectionSocket.close()

print("socket closed")
exit(1)

#
