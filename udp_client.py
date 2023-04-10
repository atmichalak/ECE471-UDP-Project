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

`select` - The `select` module in Python provides a way to monitor and handle I/O operations on multiple file
descriptors. This includes sockets, files, pipes, and any other file-like objects that can be monitors for I/O events.
It provides a mechanism for waiting until one or more of these file descriptors are ready for reading, writing, or
exceptional conditions. This can be useful for implementing network servers or other applications that need to handle
multiple connections at once.

`select`: https://docs.python.org/3/library/select.html

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

--- Behavior ---

1.  The code imports necessary libraries `os`, `socket`, `struct`, and `time`.
2.  It sets the buffer size to 1036 bytes.
3.  The `send_image` function is defined that takes a filename, a socket, server IP and server port as parameters.
4.  Inside the function, the size of the image is obtained using os.path.getsize function and sent to the server using
    `sock.sendto`.
5.  The image file is opened and read 1024 bytes at a time in a loop.
6.  A packet is constructed with sequence number, image data, file size, and timeout using `struct.pack`.
7.  A while loop is started to send the packet to the server, and wait for the acknowledgement. The loop runs up to 5
    times if the server doesn't send the acknowledgement within the timeout of 1 second.
8.  The start time for the packet is recorded, and the packet is sent to the server using `sock.sendto`.
9.  A message is printed indicating the packet has been sent.
10. The client waits for an acknowledgement from the server using sock.recvfrom with a 1-second timeout.
11. If the client receives an acknowledgement, the end time is recorded, and the round trip time for the packet is
    calculated.
12. The sequence number of the acknowledgement is extracted using `struct.unpack`, and a message is printed indicating
    the packet has been received by the server.
13. The start time of the acknowledgement is recorded, and the acknowledgement time is calculated.
14. The round trip time for the packet is calculated and printed.
15. The total round trip time is added to the total time for all packets, and the retry loop is exited.
16. If the maximum number of retries is reached, a message is printed and the function returns.
17. The sequence number is incremented, and the next 1024 bytes of data are read from the image file.
18. Once all data has been sent, the total time and average round trip time are calculated and printed.
19. The socket is closed, and a message is printed indicating the socket has been closed.
20. The `main` function is defined.
21. The user is prompted to enter the server IP address and port number.
22. The server IP and port number are set, and a message is printed indicating the connection has been established.
23. A UDP socket is created and set to non-blocking mode.
24. The `send_image` function is called with the appropriate parameters.
25. The socket is closed.
26. The main function is called if the code is executed directly.

"""

import os
import select
import socket
import struct
import time


# Set up the buffer (aka the packet) 1024 bytes of image data and 12 bytes of sequence numbers and timers
BUFFER_SIZE = 1036
TIMEOUT = 1


# The send_image() method is the driver of the script/program, as this does all of the work on the image file
def send_image(filename, sock, SERVER_IP, SERVER_PORT):
    # Get the size of the image
    filesize = os.path.getsize(filename)

    # Send the size of the image to the server
    sock.sendto(str(filesize).encode(), (SERVER_IP, SERVER_PORT))
    print("\nSending data...")

    # Open the image file and read 1024 bytes at a time
    with open(filename, "rb") as f:
        data = f.read(1024)
        seq_num = 1
        total_time = 0
        retry_count = 0

        # Wait for the acknowledgement from the server with a 1 second timeout
        sock.settimeout(TIMEOUT)
        while data:
            # Construct the packet with sequence number, data, file size, and timeout
            if len(data) < 1024:
                packet = struct.pack(
                    f'!I{len(data)}sI', seq_num, data, filesize)
            else:
                packet = struct.pack('!I1024sI', seq_num, data, filesize)

            while retry_count < 5:
                # Wait until the socket is ready for writing or the timeout expires
                try:
                    # Use select to wait for the socket to be ready for writing
                    # and set it to be non-blocking for allow for immediate return
                    ready = select.select([], [sock], [sock], TIMEOUT)
                    if not ready[1]:
                        # Timeout expires
                        retry_count += 1
                        print(
                            f"Timeout: retrying packet {seq_num} ({retry_count}/5)")
                        continue
                except socket.error as e:
                    # Handle socket error
                    print(f"Socket error: {e}")
                    retry_count += 1
                    continue

                # Record the start time for the packet
                start_time = time.perf_counter_ns()

                # Send the packet to the server
                sock.sendto(packet, (SERVER_IP, SERVER_PORT))
                print(f"Sent packet {seq_num} with {len(data)} bytes of data")

                try:
                    ack_data, server_address = sock.recvfrom(BUFFER_SIZE)

                    # Record the end time for the packet and calculate the packet time
                    end_time = time.perf_counter_ns()
                    packet_time = end_time - start_time
                    print(f"Client to server packet time: {packet_time}ns")

                    # Unpack the acknowledgement packet and get the sequence number
                    ack_seq_num = struct.unpack('!I', ack_data)[0]
                    print(f"Received ACK for packet {ack_seq_num}")

                    # Record the start time for the ACK and calculate the ACK time
                    ack_start_time = time.perf_counter_ns()
                    ack_time = ack_start_time - end_time
                    print(f"Server to client ACK time: {ack_time}ns")

                    # Trash conversion from ack_time (ns) time TIMEOUT in seconds
                    if ack_time > TIMEOUT*1000000000:
                        # Timeout if ACK time exceeds a certain value
                        raise socket.timeout("ACK time exceeded maximum value")

                    # Record round trip time and display
                    round_trip_time = packet_time + ack_time
                    print(f"Round-trip time: {round_trip_time}ns\n")

                    # Add the packet time and ACK time to the total round trip time
                    total_time += (packet_time + ack_time)

                    # Exit the retry loop and continue to the next packet
                    retry_count = 0
                    break

                except socket.timeout:
                    # Increment the retry count and print the retry message
                    retry_count += 1
                    print(
                        f"Timeout: retrying packet {seq_num} ({retry_count}/5)")

            # If we've reached the maximum number of retries, close the socket and exit the program
            if retry_count >= 5:
                print("Connection failed: max number of retries reached.")
                sock.close()
                return

            seq_num += 1
            data = f.read(1024)

        # Calculate the total time and average round trip time and print the result
        print(f"Total time: {total_time}ns")
        avg_round_trip_time = total_time / seq_num
        print(f"Average round trip time: {avg_round_trip_time}ns")

    # Close the socket and print a message
    sock.close()
    print("Client socket closed.")


# Define the main function to run the client
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


# Call the main function if this file is being run directly
# This is here to have it run similarly to an imperative manner, similar to C, C++ and Java
# This could be written as a script, considering how short it is and doesn't really need a modular
# design
if __name__ == '__main__':
    main()
