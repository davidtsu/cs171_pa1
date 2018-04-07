import socket
import sys
import threading
import time
import datetime
import os.path
from time import sleep
from socket import SHUT_RDWR

# setting server name and server port number
serverName = sys.argv[1]   # '169.231.80.116'
serverPort = int(sys.argv[2])               #12000
nickname = raw_input("Enter Username: ")     # username to be used in chat room

# opening socket and sending user name to server
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
clientSocket.send(nickname.encode())
#print ("Client message: %s " %message) 											# message sent

ignoreList = []                 # list of users this client has decided to block
startTime = datetime.datetime.now()
endTime = datetime.datetime.now()
quit = 0


def PrintHelpMenu():
    print("\n************** HELP MENU ******************")
    print("\nCOMMANDS ALLOWED IN THIS KIOSK")
    print("\n\n/play # \n play command is used to buy play tickets.\n Specify the number you want to buy in the command.")
    print("\n \n /movie # \n movie command is used to buy movie tickets. \n Specify the number you want to buy in the command.")
    print("\n\n /help \n help command prints valid commands and intended purpose")
    print("\n\n /quit \n quit command logs user out of kiosk")
    print("\n\n ************** END OF HELP MENU ******************** \n")


def SendMessage():
        while(1):
                inMessage = raw_input()
                #see if a command is being sent
                parsedMessage = inMessage.split(" ")
                if parsedMessage[0] == "/help":
                    PrintHelpMenu()
                elif parsedMessage[0] == "/play" and len(parsedMessage) == 2:
                    clientSocket.send(inMessage.encode())
                elif parsedMessage[0] == "/movie" and len(parsedMessage) == 2:
                    clientSocket.send(inMessage.encode())
                elif  parsedMessage[0] == "/quit":
                    clientSocket.send(inMessage.encode())
                else:
                    clientSocket.send(inMessage.encode())





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
    if len(modifiedMessage) == 0 :
        quit = 1

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
                clientSocket.send(message.encode())
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
