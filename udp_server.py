"""
Author: Alexander Michalak
        Paul Celmer
        Omar Hawari

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

--- Behavior --- Top to bottom explaination

1.  The code imports two modules: `socket` and `struct`.
2.  The code defines a constant variable `BUFFER_SIZE` with a value of 1032. This value will be used as the size of the
    buffer for receiving data over the network.
3.  The code defines a function `receive_image()` that takes one argument, `sock`, which is a socket object. The function
    receives an image data from a client, unpacks it and writes it to a file.
4.  The `receive_image()` function first receives the size of the image data from the client using the `recvfrom()`
    method on the socket object `sock`. It then converts the data to an integer using the `decode()` method.
5.  The function then opens a new file in binary write mode with the name "test2.jpg" using the `open()` method.
6.  The function uses a while loop to receive packets of data from the client. It receives a packet using the
    `recvfrom()` method on the sock object and unpacks it using the `struct.unpack()` method, which returns a tuple
    containing the sequence number, data, and file size.
7.  The function checks if the sequence number of the packet matches the expected sequence number, and if it does not
    match, it ignores the packet and continues waiting for the next packet.
8.  If the sequence number matches the expected sequence number, the function writes the data from the packet to the
    file using the `write()` method.
9.  The function sends an acknowledgement packet to the client with the sequence number of the packet using the
    `sendto()` method on the `sock` object.
10. The function increments the sequence number by 1 and checks if it has received all the data by comparing the
    current position of the file pointer with the total size of the image data. If it has received all the data, the
    function breaks out of the while loop.
11. The function prints a message indicating that the file has been received successfully.
12. The code defines a main function that sets up the server parameters, accepts user input to set up the server IP and
    port, creates a UDP socket, binds the socket to the server address and port, and calls the `receive_image()` function
    to receive the image data.
13. Finally, the main function closes the socket and prints a message indicating that the server socket has been closed.
14. The code checks if the file is being run directly using the `__name__` variable, and if it is, it calls the
    main function. This is to have the program/script resemble C or C++ code.

"""

import socket
import struct


# Define the buffer size (increased packet size to include packet header)
BUFFER_SIZE = 1032


# The receive_image() method is the main driver of the server, as this handles the information from the socket
# connection and rebuilding the image file from the client
def receive_image(sock):
    # Receive the size of the image from the client
    data, client_address = sock.recvfrom(BUFFER_SIZE)
    filesize = int(data.decode())
    print("\nReceiving data...")
    print(f"Received image size: {filesize}")

    # Open a new file to write the image data to -- in this case 'test2.jpg' as per the requirements for the project
    with open("test2.jpg", "wb") as f:
        # Since receiving, seq_num starts at 1 as it is expecting 1 from the client
        seq_num = 1
        while True:
            # Receive the packet from the client
            packet, client_address = sock.recvfrom(BUFFER_SIZE)
            
            # This is for output to console and it peels off the 1024 bytes in the f-string
            # since the actual packet is 1032 bytes in length, not 1024
            print(f"Received packet {seq_num} with {len(packet)-8} bytes of data")

            # Unpack the packet and get the sequence number, data, and file size
            # struct.unpack() does the opposite (obviously) as struct.pack() and breaks the struct into chunks
            # determined by the user parameters -- this also catches the last packet that is smaller than 1024 bytes
            # packet_date[0] is the sequence number of type !I -- big-endian integer of 4 bytes
            # packet_data[1] is the image data of type s1024 -- char[] of 1024 bytes
            # packet_data[2] is the filesize, for looping until the size of 'test.jpg' is the same as 'test2.jpg'
            # No error checking or data validity but that is out of scope -- could be done with a checksum sent with the
            # packet header
            packet_data = struct.unpack(f'!I{min(filesize-f.tell(),1024)}sI', packet)
            packet_seq_num = packet_data[0]
            packet_data = packet_data[1]
            packet_filesize = packet_data[2]

            # If the sequence number is not what we expect, ignore the packet and continue waiting
            # This is for TIMEOUTs and out-of-order packets -- probably out of scope for this project
            if packet_seq_num != seq_num:
                print(f"Ignoring packet {packet_seq_num}, expected packet {seq_num}")
                continue

            # Write the data from the packet to the file -- the opposite of what is done in the client, rb or read-binary vs.
            # write-binary
            f.write(packet_data)

            # Send an acknowledgement to the client with the sequence number of the packet
            # This could be sent as a small packet with a separate loop or function in in the client receiving this
            # and handling it for better space and time performance
            ack_packet = struct.pack('!I', seq_num)
            sock.sendto(ack_packet, client_address)
            print(f"Sent ACK for packet {seq_num}\n")

            seq_num += 1

            # If we have received all the data, break out of the loop
            # No checksum or data validity check, but essentially a size parity check
            # test.jpg == test2.jpg? -- if yes, break out of the loop and return to 'main'
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

    # Bind the socket to the server address and port (in this case, will be host IP and any
    # port of choice)
    server_socket.bind((SERVER_IP, SERVER_PORT))

    # Print a message indicating that the server is listening
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    # Call the receive_image function to receive the image data
    receive_image(server_socket)

    # Close the socket and print a message
    server_socket.close()
    print("Server socket closed.")


# Call the main function if this file is being run directly
# This is here to have it run similarly to an imperative manner, similar to C, C++ and Java
# This could be written as a script, considering how short it is and doesn't really need a modular
# design
if __name__ == "__main__":
    main()
