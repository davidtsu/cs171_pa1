# Name: David Tsu, Sang Min Oh
# Class: CS 171
#
# PA 1
# File: movie_server.py
# Description: A server that sells movie tickets.

import socket
import threading
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

# Initialize the number of tickets that the movie server has in store
num_tickets = 50
    
# The task to be run in a single thread. If the client requests the ticket that is available from the movie server, the request is handled locally. If not, the movie server forwards the request to the play server.
def buy_tickets(client, address):
    global num_tickets
    
    while True:
        data = client.recv(1024)
        if not data:
            break

        data_tokens = data.split(" ")
        if len(data_tokens) > 3:
            # The request was forwarded from the Play Server
            print "Received request from kiosk", data_tokens[3], data_tokens[4], "=", data_tokens[0], data_tokens[1], data_tokens[2]
        else:
            # The request is from the kiosk
            print "Received request from kiosk", address, "=", data
                                                  
        if data_tokens[1] == "movie":
            # Local Processing
            requested_num_tickets = int(data_tokens[2])
            if (num_tickets - requested_num_tickets) < 0:
                # Not enough tickets to satisfy request. Send a message to the kiosk saying that the request was unsuccessful.
                time.sleep(3)
                client.send("UNSUCCESSFUL: Not enough movie tickets to honor request.\n")
            else:
                # There are enough tickets. Send a message to the kiosk saying that the request was successful.
                num_tickets = num_tickets - requested_num_tickets
                print "\nNUMBER OF MOVIE TICKETS REMAINING = ", str(num_tickets), "\n"
                message = "SUCCESSFUL: " + str(requested_num_tickets) + " movie tickets purchased.\n"
                time.sleep(3)
                client.send(message)
        else:
            # Check whether the ticket is for a play ticket before forwarding
            if data_tokens[1] != "play":
                time.sleep(3)
                client.send("UNSUCCESSFUL: Invalid type of ticket.\n")
            
            # Forward the request to the Play Server
            print "Forwarding request to the Play Server\n"

            # The Movie Server will act as a client and send the same received request (along with the information of the kiosk that requested the data) to the Play Server
            server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_connect.connect((server_address[1], server_port[1]))
            message = data + " " + str(address)
            time.sleep(3)
            server_connect.send(message)

            # Get the response from the forwarded request and send it to the client
            forward_response = server_connect.recv(1024)
            time.sleep(3)
            client.send(forward_response)

            # Close the connection between the sockets
            server_connect.close()
            
    # After communication with the client is complete, close the client socket
    client.close()

# Create a list of threads
threads = []
    
# Create a TCP socket and bind the server to a port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", server_port[0]))
print "\n*** STARTED MOVIE SERVER ***\n"
print "NUMBER OF MOVIE TICKETS REMAINING = ", str(num_tickets), "\n"

# Loop indefinitely, waiting for a client to connect
while True:
    # Listen for a client that wants to connect
    server.listen(1)
    
    # If a client wants to talk to the server, accept the connection
    client, address = server.accept()

    # Create and start a new thread with the client that connected to the server
    th = threading.Thread(target=buy_tickets, args=(client, address,))
    threads.append(th)
    th.start()

# Wait until all of the threads terminate
for thread in threads:
    thread.join()

# Close the server socket
server.close()
