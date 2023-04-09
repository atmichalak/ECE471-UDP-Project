"""
Author: Alexander Michalak

The `socket` module provides low-level network functionality, while the `struct` module performs conversions between
Python values and C structs. The `os` module provides a way of using operating system dependent functionality, such as
reading or writing to the file system. The `time` module provides various time-related functions, including functions
for sleeping, measuring time intervals, and formatting time values.

`os` - The `os` module provides a way of interacting with the operating system. It provides functions for working with
files, directories, processes, and more. The `os` module is used to get information about the operating system and the
environment in which the Python program is running.

`os`: https://docs.python.org/3/library/os.html

`socket` - The `socket` module provides a low-level interface for network communication. It provides functions for
creating and manipulating sockets, which are the endpoints of a two-way communication link between two programs running
on a network. The `socket` module is used to create network connection,s send a receive data over the network, and more.

`socket`: https://docs.python.org/3/library/socket.html

`struct` - The `struct` module provides functions for working with structured binary data, such as data in a binary file
or data sent over a network. It provides functions for packing and unpacking data into and from byte strings, and for
working with different byte orders and data types. The `struct` module is used to convert data between Python objects
and binary data.

`struct`: https://docs.python.org/3/library/struct.html

`time` - The `time` module provides functions for working with time, such as getting the current time, converting
between time formats, and sleeping for a given amount of time. The `time` module is used to performing timing
operations, measure program performance, and more.

`time`: https://docs.python.org/3/library/time.html

"""

import os
import socket
import struct
import time


BUFFER_SIZE = 1036  # increased packet size to include timeout

def send_image(filename, sock, SERVER_IP, SERVER_PORT):
    # Get the size of the image
    filesize = os.path.getsize(filename)

    # Send the size of the image to the server
    sock.sendto(str(filesize).encode(), (SERVER_IP, SERVER_PORT))

    # Open the image file and read 1024 bytes at a time
    with open(filename, "rb") as f:
        data = f.read(1024)
        seq_num = 1
        total_time = 0
        retry_count = 0
        while data:
            # Construct the packet with sequence number, data, file size, and timeout
            packet = struct.pack('!I1024sI', seq_num, data, filesize) # sequence number is 4-byte integer

            while retry_count < 5:
                # Record the start time for the packet
                start_time = time.perf_counter()

                # Send the packet to the server
                sock.sendto(packet, (SERVER_IP, SERVER_PORT))
                print(f"Sent packet {seq_num} with {len(data)} bytes of data")

                # Wait for the acknowledgement from the server with a 1 second timeout
                sock.settimeout(1)
                try:
                    ack_data, server_address = sock.recvfrom(BUFFER_SIZE)

                    # Record the end time for the packet and calculate the packet time
                    end_time = time.perf_counter()
                    packet_time = end_time - start_time
                    print(f"Client to server packet time: {packet_time*1000000:.0f}us")

                    # Unpack the acknowledgement packet and get the sequence number
                    ack_seq_num = struct.unpack('!I', ack_data)[0]
                    print(f"Received ACK for packet {ack_seq_num}")

                    # Record the start time for the ACK and calculate the ACK time
                    ack_start_time = time.perf_counter()
                    ack_time = ack_start_time - end_time
                    print(f"Server to client ACK time: {ack_time*1000000:.0f}us")

                    # Record round trip time and display
                    round_trip_time = packet_time + ack_time
                    print(f"Round-trip time: {round_trip_time*1000000:.0f}us\n")

                    # Add the packet time and ACK time to the total round trip time
                    total_time += (packet_time + ack_time)

                    # Exit the retry loop and continue to the next packet
                    retry_count = 0
                    break

                except socket.timeout:
                    # Increment the retry count and print the retry message
                    retry_count += 1
                    print(f"Timeout: retrying packet {seq_num} ({retry_count}/5)")

            # If we've reached the maximum number of retries, close the socket and exit the program
            if retry_count >= 5:
                print("Connection failed: max number of retries reached.")
                sock.close()
                return

            seq_num += 1
            data = f.read(1024)

        # Calculate the total time and average round trip time and print the result
        print(f"Total time: {total_time*1000000:.0f}us")
        avg_round_trip_time = total_time / seq_num
        print(f"Average round trip time: {avg_round_trip_time*1000000:.0f}us")

    # Close the socket and print a message
    sock.close()
    print("Client socket closed.")

def main():
    # Set up the client-server connection
    # Prompt the user to enter the IP address
    ip_address = input("Enter the IP address: ")

    # Prompt the user to enter the port number
    server_port = input("Enter the port number: ")

    # Conver the user input for the port number to an integer
    server_port = int(server_port)

    # Set up the SERVER_IP and SERVER_PORT
    SERVER_IP = ip_address
    SERVER_PORT = server_port

    # Display connection output to user
    print(f"Client connected to server at {SERVER_IP}:{SERVER_PORT}")

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set the socket to be non-blocking
    client_socket.setblocking(False)

    # Call the send_image function to send the image file
    send_image("test.jpg", client_socket, SERVER_IP, SERVER_PORT)

    # Close the socket
    client_socket.close()

if __name__ == '__main__':
    main()