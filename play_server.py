# Name: David Tsu, Sang Min Oh
# Class: CS 171
#
# PA1
# File: play_server.py
# Description: A server that sells play tickets.

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

# Initialize the number of tickets that the play server has in store
num_tickets = 50

# The task to be run in a single thread. If the client requests the ticket that is available from the play server, the request is handled locally. If not, the play server forwards the request to the movie server.
def buy_tickets(client, address):
    global num_tickets
    
    while True:
        data = client.recv(1024)
        if not data:
            break

        data_tokens = data.split(" ")
        if len(data_tokens) > 3:
            # The request was forwarded from the Movie Server
            print "Received request from kiosk", data_tokens[3], data_tokens[4], "=", data_tokens[0], data_tokens[1], data_tokens[2]
        else:
            print "Received request from kiosk", address, "=", data

        if data_tokens[1] == "play":
            # Local Processing
            requested_num_tickets = int(data_tokens[2])
            if (num_tickets - requested_num_tickets) < 0:
                # Not enough tickets to satisfy request. Send a message to the kiosk saying that the request was unsuccessful.
                time.sleep(3)
                client.send("UNSUCCESSFUL: Not enough play tickets to honor request.\n")
            else:
                # There are enough tickets. Send a message to the kiosk saying that the request was successful.
                num_tickets = num_tickets - requested_num_tickets
                print "\nNUMBER OF PLAY TICKETS REMAINING = ", str(num_tickets), "\n"
                message = "SUCCESSFUL: " + str(requested_num_tickets) + " play tickets purchased.\n"
                time.sleep(3)
                client.send(message)
        else:
            # Check whether the ticket is for a movie ticket before forwarding
            if data_tokens[1] != "movie":
                time.sleep(3)
                client.send("UNSUCCESSFUL: Invalid type of ticket.\n")
            
            # Forward the request to the Movie Server
            print "Forwarding request to the Movie Server\n"

            # The Play Server will act as a client and send the same received request to the Movie Server
            server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_connect.connect((server_address[0], server_port[0]))
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
server.bind(("0.0.0.0", server_port[1]))
print "\n*** STARTED PLAY SERVER ***\n"
print "NUMBER OF PLAY TICKETS REMAINING = ", num_tickets, "\n"

# Loop indefinitely, waiting for a client to connect
while True:
    # Listen for a client that wants to connect
    server.listen(1)

    # If a client wants to talk to the server, accept the connection
    client, address = server.accept()

    # Create and start a new thread with the client that connected to the server
    th = threading.Thread(target=buy_tickets, args=(client, address))
    threads.append(th)
    th.start()

# Wait until all of the threads terminate
for thread in threads:
    thread.join()

# Close the server socket
server.close()
