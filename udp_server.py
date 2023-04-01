import os
import socket
import sys
import time

# Define NAK timeout period in seconds
NAK_TIMEOUT = 1

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
    received_packets = set()
    with open("test2.jpg", "wb") as f:
        while len(received_packets) < total_packets:
            # Set the NAK timer for the next missing packet
            missing_packets = set(range(1, total_packets+1)) - received_packets
            if missing_packets:
                next_missing_packet = min(missing_packets)
                nak_timer = time.monotonic() + NAK_TIMEOUT
            else:
                nak_timer = None

            # Receive a packet or timeout
            try:
                if nak_timer is None:
                    data, addr = sock.recvfrom(1028)
                else:
                    timeout = max(0, nak_timer - time.monotonic())
                    sock.settimeout(timeout)
                    data, addr = sock.recvfrom(1028)
            except socket.timeout:
                print(f"NAK for packet {next_missing_packet}")
                continue

            sequence_number = int(data[:4].decode())
            data = data[4:]
            f.write(data)
            received_packets.add(sequence_number)
            received_data_size += len(data)

            # Send an acknowledgement back to the client
            sock.sendto("ACK".encode(), addr)
            print(f"Received packet {sequence_number}/{total_packets}")

    # Close the socket and shut down
    sock.close()
    print("File received successfully")

    # Exit on the console
    input("Press enter to exit")
    sys.exit()

if __name__ == "__main__":
    main()