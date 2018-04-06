# the basic socket code was copied from COMPUTER NETWORKING SIXTH EDITIONA Top-Down Approach
# by James F. KuroseUniversity of Massachusetts, AmherstKeith W. Ross Polytechnic Institute of NYU
import socket
import sys
import time
from time import sleep
import threading
from socket import SHUT_RDWR



def sendMessage(ReturnMessage, con):
    for x in range(len(sockList)):
        sockList[x].send(ReturnMessage.encode())



nickName = []
ipList = []
sockList = []
threads = []
i = 0
serverPort = int(sys.argv[1])                                                 # port server is listening on

                                               # port server is listening on

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)     # open a socket
serverSocket.bind(('',serverPort))                                  # binding server to this port
serverSocket.listen(1)                                              # begin to listen on port
global closeSock

def ListenForMessage(con, nick):
    while(1):
        print( "length of connection array %i \n" %len(sockList))
        message = con.recv(1024)                               # recieve message from client
        tempMessage = str(message)
        if tempMessage[0:2] == "\d" :
            parseMessage = tempMessage.split("&@#")
            if parseMessage[1] in nickName:
                conIndex = nickName.index(parseMessage[1])
                sockList[conIndex].send(tempMessage)
        
        else :
            parseMessage = tempMessage.split(" ")
            if parseMessage[0] == "/quit" :
                #remove connection
                sockList.remove(con)
                nickName.remove(nick)
                endmes = "bye"
                con.send(endmes.encode())
                sleep(1)
                con.shutdown(SHUT_RDWR)
                con.close()                                            # closing connection
                break
            else:
                tempMessage = nick + " : " + tempMessage
                print("%s \n" %(tempMessage))
                sendMessage(tempMessage, con)

def newSocket():
    while (1):
        connectionSocket, addr = serverSocket.accept()                      # establish connect to client
        message = connectionSocket.recv(1024)                               # recieve message from client
        nickName.append(message)
        tempMessage = str(message)
        print("%s connected \n" %tempMessage)
        tempMessage = tempMessage + " connected"
        sockList.append(connectionSocket)
        sendMessage(tempMessage,connectionSocket)
        t = threading.Thread(target=ListenForMessage,args=(connectionSocket,str(message),))
        threads.append(t)
        t.start()

connectionSocket, addr = serverSocket.accept()                      # establish connect to client
message = connectionSocket.recv(1024)                               # recieve message from client
nickName.append(message)
tempMessage = str(message)
print("%s connected \n" %tempMessage)
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
serverSocket.shutdown(SHUT_RDWR)
serverSocket.close()
connectionSocket.shutdown(SHUT_RDWR)
connectionSocket.close()

print("socket closed")
sys.exit(1)


#
