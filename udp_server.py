"""
Author: Alexander Michalak

The `socket` module provides low-level network functionality, while the `struct` module performs conversions between
Python values and C structs.

`socket` - The `socket` module provides a low-level interface for network communication. It provides functions for
creating and manipulating sockets, which are the endpoints of a two-way communication link between two programs running
on a network. The `socket` module is used to create network connection,s send a receive data over the network, and more.

`socket`: https://docs.python.org/3/library/socket.html

`struct` - The `struct` module provides functions for working with structured binary data, such as data in a binary file
or data sent over a network. It provides functions for packing and unpacking data into and from byte strings, and for
working with different byte orders and data types. The `struct` module is used to convert data between Python objects
and binary data.

`struct`: https://docs.python.org/3/library/struct.html

"""

import socket
import struct

# Define the buffer size (increased packet size to include packet header)
BUFFER_SIZE = 1036

# Define a function to receive the image data from the client
def receive_image(sock):
    # Receive the size of the image from the client
    data, client_address = sock.recvfrom(BUFFER_SIZE)
    filesize = int(data.decode())
    print(f"Received image size: {filesize}")

    # Open a new file to write the image data to
    with open("test2.jpg", "wb") as f:
        seq_num = 1
        while True:
            # Receive the packet from the client
            packet, client_address = sock.recvfrom(BUFFER_SIZE)
            print(f"Received packet {seq_num} with {len(packet)-8} bytes of data")

            # Unpack the packet and get the sequence number, data, and file size
            packet_data = struct.unpack('!I1024sI', packet)
            packet_seq_num = packet_data[0]
            packet_data = packet_data[1]
            packet_filesize = packet_data[2]

            # If the sequence number is not what we expect, ignore the packet and continue waiting
            if packet_seq_num != seq_num:
                print(f"Ignoring packet {packet_seq_num}, expected packet {seq_num}")
                continue

            # Write the data from the packet to the file
            f.write(packet_data)

            # Send an acknowledgement to the client with the sequence number of the packet
            ack_packet = struct.pack('!I', seq_num)
            sock.sendto(ack_packet, client_address)
            print(f"Sent ACK for packet {seq_num}\n")

            seq_num += 1

            # If we have received all the data, break out of the loop
            if f.tell() >= filesize:
                break

    # Print a message indicating the file has been received
    print("File received successfully.")

# Define the main function to run the server
def main():
    # Set up server parameters and accept user input to set up the server IP and port
    # Get the current machine's hostname
    hostname = socket.gethostname()

    # GEt the IP address for the hostname
    ip_address = socket.gethostbyname(hostname)

    # Print the IP address
    print(f"IP address for {hostname} is {ip_address}")

    # Prompt the user to enter a port number
    server_port = input("Enter a port number: ")

    # Conver the user input to an integer
    server_port = int(server_port)

    # Set up the SERVER_IP and SERVER_PORT variables
    SERVER_IP = ip_address
    SERVER_PORT = server_port

    # Print the SERVER_IP and SERVER_PORT variables
    print(f"Server address: {SERVER_IP}:{SERVER_PORT}")

    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the server address and port
    server_socket.bind((SERVER_IP, SERVER_PORT))

    # Print a message indicating that the server is listening
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    # Call the receive_image function to receive the image data
    receive_image(server_socket)

    # Close the socket and print a message
    server_socket.close()
    print("Server socket closed.")

# Call the main function if this file is being run directly
# This is here to have it run similarly to an imperaritive manner, similar to C, C++ and Java
# This could be written as a script, considering how short it is and doesn't really need a modular
# design
if __name__ == "__main__":
    main()
