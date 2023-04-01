import os
import socket
import sys

def main():
    # Get the host machine's IP address
    hostname = socket.gethostname()
    UDP_IP = socket.gethostbyname(hostname)

    # Set up the server's port number
    UDP_PORT = 8080

    # Display the host machine's IP address and port
    print(f"Server IP address: {UDP_IP}:{UDP_PORT}")

    # Ask the user to confirm start the server
    server_start = input("Press 'y' to start the server: ")
    if server_start.lower() != 'y':
        print("Server not started")
        sys.exit()

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the IP address and port number
    sock.bind((UDP_IP, UDP_PORT))

    # Receive the image file size from the client
    data, addr = sock.recvfrom(1024)
    file_size = int(data.decode())
    
    # Receive the total number of packets from the client
    data, addr = sock.recvfrom(1024)
    total_packets = int(data.decode())

    # Receive the image file data from the client and write it to a file
    received_data_size = 0
    with open("test2.jpg", "wb") as f:
        while True:
            data, addr = sock.recvfrom(1028)
            sequence_number = int(data[:4].decode())
            data = data[4:]
            f.write(data)
            received_data_size += len(data)

            # Send an acknowledgement back to the client
            sock.sendto("ACK".encode(), addr)
            print(f"Received packet {sequence_number}/{total_packets}")

            if sequence_number == total_packets:
                break

    # Close the socket and shut down
    sock.close()
    print("File received successfully")

    # Exit on the console
    input("Press enter to exit")
    sys.exit()

if __name__ == "__main__":
    main()
