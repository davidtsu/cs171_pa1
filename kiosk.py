# Name: David Tsu, Sang Min Oh
# Class: CS 171
#
# PA 1
# File: kiosk.py
# Description: A kiosk (client) that connects to the ticket-selling servers.

import random
import socket
import sys
import time

# Read from the configuration file and determine the IP address and listening port of each server.
# Movie Server - index 0
# Play Server - index 1
server_address = []
server_port = []
cfg_read = open("config.txt", "r")
for line in cfg_read:
    tokens = line.split("\t")
    server_address.append(tokens[1])
    server_port.append(int(tokens[2][:-1]))

print "\n*** WELCOME TO THE KIOSK ***\n\nCOMMANDS:\n\nBUY TICKET = \"buy <movie, play> <amount to purchase>\"\nQUIT = \"quit\"\n"

# Infinite loop that lets users buy tickets
while True:
    # Get the request from the user
    request = raw_input()
    if request == "quit":
        print "Exiting kiosk..."
        sys.exit(0)

    # If the request isn't to quit the kiosk, continue
    
    # Create a TCP for connecting to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect the client to a random ticket-selling server
    rand_num = random.randint(0,1)
    client.connect((server_address[rand_num], server_port[rand_num]))

    # Send the request to the server
    time.sleep(3)
    client.send(request)

    # Receive the response from the server
    response = client.recv(1024)
    print response

    # Close the socket
    client.close()



